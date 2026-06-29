# Part 19: Testing FastAPI Microservices - Assignments

## Assignment Guidelines

- **Estimated time:** 16-22 hours total
- **Prerequisites:** Parts 1-18 complete; existing microservices codebase (from Parts 17-18) or provided starter
- **Submission:** Comprehensive test suite with coverage reports, CI config, and testing documentation
- **Rules:** Follow testing pyramid — many unit, fewer integration, few E2E

---

## Assignment 1: Complete Test Pyramid for Single Service

### Scenario

For the User Service (or Bookstore monolith from Part 16), implement the full testing pyramid with pytest — unit, integration, and API tests achieving 80%+ coverage on critical paths.

### Requirements

**Test structure:**

```
tests/
├── unit/
│   ├── test_services.py
│   ├── test_schemas.py
│   └── test_security.py
├── integration/
│   ├── test_repositories.py
│   └── test_database.py
├── api/
│   ├── test_auth_endpoints.py
│   └── test_user_endpoints.py
├── conftest.py
└── factories.py
```

**Unit tests (60% of tests, fastest):**

- `UserService.create_user` — mock repository; test duplicate email raises
- `UserService.authenticate` — wrong password, inactive user, success
- Pydantic schema validation — invalid email, weak password
- `hash_password` / `verify_password` / `create_access_token` utilities
- No database, no HTTP

**Integration tests (25%):**

- Repository CRUD against real test SQLite/PostgreSQL
- Transaction rollback on error
- Unique constraint on email enforced by DB

**API tests (15%):**

- `TestClient` full request/response cycle
- Register → login → access protected route
- 422 validation errors structure
- 401/403 status codes

**Fixtures (`conftest.py`):**

- `db_session` — function-scoped clean DB
- `client` — app with overridden dependencies
- `authenticated_client` — client with auth headers pre-set
- `user_factory` — creates users with random emails

**Mocking:**

- `@patch('app.utils.email.send_email')` — verify called on register
- `pytest-mock` `mocker` fixture for httpx external calls

**Coverage:**

- `pytest --cov=app --cov-report=html --cov-fail-under=80`
- Exclude `main.py` if needed in `.coveragerc`

**Parametrize:**

- `@pytest.mark.parametrize` for password validation rules (5 invalid, 2 valid)

### Technical Specifications

- Testing pyramid concept
- pytest fixtures and conftest
- Unit tests with mocks
- Integration tests with test database
- FastAPI TestClient API tests
- pytest-cov coverage
- unittest.mock / pytest-mock

### Acceptance Criteria

- [ ] ≥ 50 tests total; unit tests run in < 5 seconds
- [ ] Coverage ≥ 80% on `app/services` and `app/api`
- [ ] No unit test touches real database
- [ ] Integration tests use separate test DB (not dev DB)
- [ ] API tests cover all auth edge cases
- [ ] `htmlcov/index.html` generated
- [ ] README explains how to run each test tier: `pytest tests/unit`, etc.

### Bonus Challenges

- Hypothesis property-based tests for email validation
- Mutation testing with `mutmut` on one service module
- Benchmark tests with `pytest-benchmark` for password hashing

### Hints

- Override deps: `app.dependency_overrides[get_db] = lambda: test_session`
- Factory: `def user_factory(**kwargs): defaults = {email: fake.email(), ...}; return User(**{**defaults, **kwargs})`
- Markers: `@pytest.mark.integration` for slower tests

---

## Assignment 2: Multi-Service Integration & Contract Tests

### Scenario

Test interactions between Order, Product, and Payment services — including contract tests ensuring API compatibility and integration tests with test containers.

### Requirements

**1. API contract tests (Product Service):**

- Define expected response schema for `GET /products/{id}`
- Test that response matches JSON schema (use `jsonschema` library)
- Breaking change detection: if field removed, test fails

**2. Integration tests with Docker:**

- `docker-compose.test.yml` — spins up services + databases for CI
- `pytest` session fixture starts compose (or use `testcontainers-python`)
- Test: Order Service creates order → calls real Product Service HTTP → stock decreases

**3. Mock external services:**

- `respx` or `pytest-httpx` mock Payment Service:
```python
@pytest.mark.respx(base_url="http://payment:8002")
async def test_order_payment(respx_mock):
    respx_mock.post("/charge").respond(200, json={"status": "ok"})
```

**4. Database integration:**

- Order test DB seeded with product IDs matching Product Service seed
- Verify saga: payment fail → order cancelled in DB

**5. Message queue integration tests:**

- Publish `PaymentCompleted` to test RabbitMQ
- Assert Order Service updates status within 5 seconds (poll DB)

**6. Test isolation:**

- Each integration test cleans up data or uses unique IDs (uuid)

**7. CI configuration (GitHub Actions YAML):**

```yaml
# .github/workflows/test.yml
# services: postgres, redis, rabbitmq
# steps: lint, unit tests, integration tests
```

**8. Test documentation `TESTING.md`:**

- Pyramid diagram for this project
- How to run locally vs CI
- Flaky test policy

### Technical Specifications

- Integration testing across services
- Contract/schema testing
- Mocking HTTP with respx/httpx mock
- Testcontainers or docker-compose for CI
- Message queue integration tests
- CI pipeline for tests

### Acceptance Criteria

- [ ] Contract test fails when Product response schema changes (demonstrate with commented breaking change)
- [ ] Integration test creates real order across 2+ running services
- [ ] Payment mock allows testing success and failure paths
- [ ] Event-driven test passes with test broker
- [ ] GitHub Actions workflow file present and valid YAML
- [ ] TESTING.md complete with run instructions
- [ ] Integration tests marked `@pytest.mark.integration` skippable via `-m "not integration"`

### Bonus Challenges

- Pact consumer-driven contract testing
- WireMock container for third-party APIs
- Database snapshot testing for complex query results

### Hints

- testcontainers: `PostgresContainer("postgres:15")` context manager
- respx: activate mock only in tests that need it
- Unique IDs: `order_id = f"test-{uuid4()}"` prevent collisions

---

## Assignment 3: E2E, Performance & Load Testing

### Scenario

Implement end-to-end user journey tests and performance benchmarks for the microservices platform — validating the system works as a whole under load.

### Requirements

**E2E tests (few, slow, high value):**

Script `tests/e2e/test_purchase_journey.py`:

1. Register user via Gateway
2. Login → obtain JWT
3. Browse products
4. Create order with 2 items
5. Simulate payment completion (webhook or event inject)
6. Verify order status `paid`
7. Verify analytics endpoint reflects new order
8. Verify notification/email mock called

- Run against `docker-compose.e2e.yml` full stack
- `@pytest.mark.e2e` marker; single worker (`pytest -n0`)

**API performance tests:**

- `tests/performance/test_api_latency.py`
- Assert `GET /products` p95 < 200ms with 100 sequential requests (local)
- Assert 50 concurrent requests complete without 5xx (use `asyncio.gather` + httpx)

**Load tests (Locust):**

- `locustfile.py` with scenarios:
  - Browse products (weight 70%)
  - Login (weight 20%)
  - Create order (weight 10%)
- Target: 50 users, spawn rate 5/s, run 2 minutes
- Document results: RPS, failure rate, p95 latency in `PERFORMANCE.md`

**Stress test:**

- Ramp until error rate > 1% — find breaking point (document, don't fix)

**Database performance tests:**

- Query plan for slow query (EXPLAIN) — document index added to fix
- N+1 detection test: assert query count ≤ 5 for product list with authors

**Chaos E2E:**

- Kill Payment Service mid-checkout
- Assert Order ends in `pending` or `failed` — not corrupted state
- Restart Payment; recovery flow works

**Coverage gap analysis:**

- `coverage report --skip-covered` — document uncovered critical paths and justify or add tests

### Technical Specifications

- E2E testing full user journeys
- Performance/latency testing
- Locust load testing
- Stress testing methodology
- Chaos testing basics
- Query performance and N+1 tests

### Acceptance Criteria

- [ ] E2E purchase journey passes on clean docker-compose stack
- [ ] Performance test documents p95 latency with pass/fail thresholds
- [ ] Locust run produces report in PERFORMANCE.md with screenshots or tables
- [ ] Chaos test documented with expected vs actual behavior
- [ ] N+1 test fails before fix, passes after `selectinload` added (show in README)
- [ ] E2E tests separated from unit tests in CI (optional nightly job)
- [ ] No E2E test depends on execution order of other E2E tests

### Bonus Challenges

- k6 load test script as alternative to Locust
- Synthetic monitoring script runnable every 5 min in staging
- Playwright test for admin UI if exists

### Hints

- E2E: use longest timeouts `httpx.Timeout(30.0)`
- Locust: `class WebsiteUser(HttpUser): @task(7) def browse(self): self.client.get("/products")`
- N+1: use SQLAlchemy `echo=True` or event listener counting queries
