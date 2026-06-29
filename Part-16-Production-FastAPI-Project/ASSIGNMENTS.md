# Part 16: Production-Grade FastAPI Project - Assignments

## Assignment Guidelines

- **Estimated time:** 20-30 hours total
- **Prerequisites:** Parts 1-15 complete
- **Submission:** Full production-style FastAPI project with layered architecture, tests, Docker, and documentation
- **Rules:** Follow structure from [README.md](README.md); no business logic in endpoints

---

## Assignment 1: Production Bookstore API

### Scenario

Build a complete production-grade REST API for an online bookstore — the capstone for the FastAPI stack. Every concept from Part 16 must appear in a cohesive, deployable application.

### Requirements

**Project structure (mandatory):**

```
app/
├── main.py
├── api/
│   ├── deps.py
│   └── v1/
│       ├── router.py
│       └── endpoints/
│           ├── books.py
│           ├── authors.py
│           ├── orders.py
│           └── auth.py
├── core/
│   ├── config.py
│   ├── security.py
│   ├── logging.py
│   └── exceptions.py
├── db/
│   ├── base.py
│   ├── session.py
│   └── repositories/
│       ├── base.py
│       ├── book.py
│       └── order.py
├── models/
├── schemas/
├── services/
│   ├── book.py
│   └── order.py
├── utils/
└── tests/
```

**Layer responsibilities:**

| Layer | Responsibility |
|-------|----------------|
| Endpoints | HTTP only — parse request, call service, return response |
| Services | Business logic, orchestration, raise domain exceptions |
| Repositories | CRUD, queries, no business rules |
| Schemas | Pydantic request/response validation |
| Models | SQLAlchemy ORM |

**Features:**

1. **Configuration** — `pydantic-settings` with dev/test/prod configs via `ENVIRONMENT`
2. **Database** — PostgreSQL or SQLite; SQLAlchemy 2.x; Alembic migrations
3. **Auth** — JWT register/login; protected order endpoints
4. **Books** — CRUD, search by title/author, pagination, filter by genre
5. **Orders** — place order (transactional stock check), list user orders, cancel pending
6. **Custom exceptions** — `NotFoundException`, `ConflictException`, `UnauthorizedException`
7. **Global exception handlers** — consistent `ErrorResponse` JSON for AppException and ValidationError
8. **Logging** — structlog JSON logs; request middleware with request_id, path, method, duration
9. **Validation** — nested schemas: `OrderCreate` with `list[OrderItemCreate]`; custom password validator
10. **Dependency injection** — `get_db`, `get_book_service`, `get_current_user`
11. **Use case (optional module):** `RegisterUserUseCase` with welcome email background task
12. **Docker** — `Dockerfile` + `docker-compose.yml` with app + db (+ redis optional)
13. **`.env.example`** — all required variables documented

**Non-functional:**

- Type hints throughout
- No raw SQL in endpoints
- Secrets from environment only
- `GET /health` and `GET /ready` (checks DB connection)

### Technical Specifications

All Part 16 topics:
- Layered architecture and separation of concerns
- Configuration management (multi-environment)
- Database integration + repository pattern
- Service layer + use cases
- Error handling (custom exceptions + handlers)
- structlog logging + request middleware
- Pydantic schemas (Create/Update/Response separation)
- Testing setup with pytest fixtures

### Acceptance Criteria

- [ ] Endpoints contain no business logic (verified by code review checklist in README)
- [ ] Duplicate book ISBN returns 409 via service exception
- [ ] Order placement rolls back on insufficient stock
- [ ] Logs are valid JSON with `request_id` field
- [ ] `ENVIRONMENT=testing` uses test database config
- [ ] `docker-compose up` starts working API
- [ ] OpenAPI docs complete at `/docs`
- [ ] Architecture diagram in README

### Bonus Challenges

- Redis caching for book catalog (Part 15 integration)
- OpenTelemetry tracing span per request
- GitHub Actions CI running tests + mypy

### Hints

- Service raises `NotFoundException("Book not found")` — handler converts to 404
- Repository: `class BookRepository(BaseRepository[Book])`
- structlog: bind `request_id` in middleware, use in services

---

## Assignment 2: Comprehensive Test Suite for Layered API

### Scenario

For the Bookstore API (Assignment 1) or a provided starter project, implement a complete test suite demonstrating production testing practices from Part 16.

### Requirements

**pytest configuration (`pytest.ini`):**

```ini
[pytest]
testpaths = tests
addopts = -v --cov=app --cov-report=term-missing --cov-fail-under=75
```

**`tests/conftest.py` fixtures:**

- `db` — fresh database per test function (create/drop tables)
- `client` — TestClient with `get_db` override
- `test_user` — seeded user in DB
- `auth_headers` — JWT for test_user
- `sample_books` — 10 books seeded
- `mock_email` — patch `send_welcome_email`

**Test modules:**

1. **`test_auth.py`** (8+ tests)
   - Register success, duplicate email, weak password
   - Login success, wrong password
   - Protected route without token → 401

2. **`test_books.py`** (10+ tests)
   - CRUD happy paths
   - Search and pagination
   - 404 on missing book
   - 422 on invalid price

3. **`test_orders.py`** (8+ tests)
   - Place order success
   - Insufficient stock → 400/409
   - Cancel order
   - User can only see own orders

4. **`test_services.py`** (unit tests, 6+)
   - Mock repository; test `BookService.create_book` duplicate ISBN
   - Test `OrderService.place_order` without DB

5. **`test_repositories.py`** (6+)
   - Direct repository tests against test DB
   - `get_by_isbn`, pagination

6. **`test_exceptions.py`** (4+)
   - Custom exceptions return correct status codes via TestClient

7. **`test_logging.py`** (2+)
   - Request middleware adds X-Request-ID (optional header check)

**Mocking:**

- `@patch` email utility — verify called once on register
- Mock external payment gateway if present

**Coverage:**

- Overall ≥ 75%
- Services layer ≥ 85%

### Technical Specifications

- pytest fixtures and conftest
- FastAPI TestClient
- Dependency overrides for test DB
- Unit vs integration test separation
- Mocking with unittest.mock
- Coverage reporting

### Acceptance Criteria

- [ ] `pytest` passes all tests
- [ ] Coverage ≥ 75% on `app/` package
- [ ] Tests are isolated — order doesn't matter
- [ ] No test calls real external services
- [ ] Fixtures documented in conftest docstrings
- [ ] At least 40 total tests
- [ ] CI-ready: tests run with single command

### Bonus Challenges

- Factory Boy or manual factories for test data
- Parametrized tests for pagination edge cases
- `pytest-asyncio` for async endpoints if any

### Hints

- Override: `app.dependency_overrides[get_db] = override_get_db`
- Clear overrides in fixture teardown: `app.dependency_overrides.clear()`
- Unit test service: `mock_repo = Mock(); service = BookService(mock_repo)`

---

## Assignment 3: Configuration, Observability & Deployment Package

### Scenario

Take the Bookstore API to deployment readiness — focus on configuration hardening, observability, and container orchestration without adding new business features.

### Requirements

1. **Multi-environment config:**
   - `DevelopmentSettings`, `ProductionSettings`, `TestingSettings`
   - `@lru_cache get_settings()` factory
   - Production requires: `SECRET_KEY`, `DATABASE_URL`; fails on startup if missing

2. **Logging production setup:**
   - JSON logs in production; console pretty print in development
   - Log levels configurable via `LOG_LEVEL`
   - Request/response logging middleware (exclude `/health`)
   - Error logging with stack traces in `AppException` handler

3. **Error response schema** — all errors match:

```json
{
  "error": "NotFoundException",
  "message": "Book not found",
  "path": "/api/v1/books/999",
  "details": null
}
```

4. **Validation error handler** — field-level `details` array

5. **Docker:**
   - Multi-stage Dockerfile (builder + runtime slim image)
   - Non-root user in container
   - `docker-compose.yml`: app, postgres, redis
   - Healthchecks on all services

6. **Alembic** — migrations run on container startup via entrypoint script

7. **Documentation package:**
   - `README.md` — setup, env vars, run tests, run docker
   - `ARCHITECTURE.md` — layer diagram, request flow
   - `API.md` — key endpoints summary (or link to /docs)

8. **Makefile or scripts:**
   - `make test`, `make run`, `make migrate`, `make docker-up`

9. **Security checklist** in README (completed checkboxes):
   - Secrets not in code
   - CORS configured
   - Passwords hashed
   - SQL injection prevented (ORM only)
   - Rate limiting noted (even if stub)

10. **Graceful shutdown** — log shutdown event on SIGTERM (uvicorn handles; add lifespan hook)

### Technical Specifications

- pydantic-settings multi-environment
- structlog production configuration
- Exception handlers and error schemas
- Docker multi-stage builds
- docker-compose orchestration
- Alembic in deployment
- Health/readiness endpoints

### Acceptance Criteria

- [ ] `ENVIRONMENT=production` without SECRET_KEY fails at import/startup
- [ ] Production logs are single-line JSON parseable by `jq`
- [ ] `docker-compose up --build` brings full stack healthy within 60s
- [ ] Migrations apply automatically on first start
- [ ] All three documentation files complete
- [ ] Makefile targets work on clean clone
- [ ] Security checklist 8/8 items addressed in README

### Bonus Challenges

- `prometheus-fastapi-instrumentator` metrics endpoint
- Sentry SDK integration (DSN from env)
- Kubernetes manifests: Deployment, Service, Ingress stub

### Hints

- Multi-stage: stage 1 `pip install`, stage 2 copy site-packages + app only
- Entrypoint: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0`
- structlog: `JSONRenderer()` when `not settings.DEBUG`
