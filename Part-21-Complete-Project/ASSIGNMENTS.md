# Part 21: Complete E-Commerce Microservices Project - Assignments

## Assignment Guidelines

- **Estimated time:** 40-60 hours total (capstone)
- **Prerequisites:** All Parts 1-20 complete
- **Submission:** Full production-ready e-commerce microservices platform — portfolio-quality
- **Rules:** This integrates everything; all services must run via `docker-compose up`; documentation must enable a new developer to run the system in < 30 minutes

---

## Assignment 1: E-Commerce Platform — Core Implementation

### Scenario

Build the complete e-commerce microservices platform described in [README.md](README.md) — User, Product, Order, Payment, and Notification services behind an API Gateway. This is the primary capstone deliverable integrating the entire Python Backend Stack course.

### Requirements

**Services to implement:**

| Service | Port | Database | Responsibility |
|---------|------|----------|----------------|
| API Gateway | 8000 | — | Routing, auth, rate limit, CORS |
| User Service | 8001 | users_db | Auth, profiles, JWT |
| Product Service | 8002 | products_db | Catalog, search, inventory, Redis cache |
| Order Service | 8003 | orders_db | Cart, orders, saga orchestration |
| Payment Service | 8004 | payments_db | Payment processing (simulated) |
| Notification Service | 8005 | — | Email notifications via events |

**User Service:**

- Register, login, refresh token, profile CRUD
- Password hashing, JWT access + refresh tokens
- Role: `customer`, `admin`
- Publishes `user.registered` event

**Product Service:**

- Product CRUD (admin), public browse/search
- Categories, pagination, filter by price range
- Inventory count per product
- Redis cache for product list and detail (TTL 5 min)
- Publishes `inventory.updated` on stock change

**Order Service:**

- Shopping cart (add, update, remove, clear) — Redis or DB
- `POST /orders/checkout` — saga:
  1. Validate cart
  2. REST: check stock (Product Service)
  3. REST: reserve stock
  4. Publish `order.created`
  5. Publish `payment.requested`
- Listen: `payment.completed` → order `paid`; `payment.failed` → cancel + release stock
- Order history for authenticated user

**Payment Service:**

- Consume `payment.requested`
- Simulate 90% success rate; 2 second processing delay
- Publish `payment.completed` or `payment.failed`
- `GET /payments/{order_id}` status query
- Idempotent processing

**Notification Service:**

- Consume: `user.registered`, `order.created`, `payment.completed`, `order.shipped`
- Send email stubs (log to file or Mailhog in docker-compose)
- Email templates (Jinja2): welcome, order confirmation, payment receipt

**API Gateway:**

- Route all public traffic
- JWT validation on protected routes
- Rate limiting: 100/min anonymous, 500/min authenticated
- `X-Correlation-ID` generation
- `GET /health` aggregated

**Shared library (`shared/`):**

- `auth.py` — JWT decode utilities
- `events.py` — event envelope schema, publish/subscribe helpers
- `logging.py` — structlog configuration
- `config.py` — base settings class

**Infrastructure (`docker-compose.yml`):**

- All services + PostgreSQL per service (or schema isolation documented)
- Redis, RabbitMQ (or Kafka)
- Mailhog for email testing
- Jaeger for tracing
- Volumes for persistence

**Each service:**

- Layered architecture (api / services / repositories / models / schemas)
- Alembic migrations
- Dockerfile multi-stage
- `GET /health`, `GET /ready`
- pytest tests ≥ 70% coverage per service

### Technical Specifications

Integrates ALL course topics:

- Python fundamentals through async programming
- FastAPI, Pydantic, SQLAlchemy, Redis
- Production patterns: config, logging, error handling, testing
- Microservices: gateway, service discovery, circuit breaker
- Communication: REST, message queue events, correlation IDs
- Observability: structured logs, health checks

### Acceptance Criteria

- [ ] `docker-compose up --build` starts entire platform healthy within 3 minutes
- [ ] Complete purchase flow works: register → login → browse → cart → checkout → payment → email logged
- [ ] Payment failure cancels order and restores inventory
- [ ] Admin can create product; visible in catalog within cache TTL
- [ ] JWT required for cart and checkout; public product browse works without auth
- [ ] Correlation ID traceable across all service logs for one checkout
- [ ] 6 services each with ≥ 70% test coverage
- [ ] No shared databases between services
- [ ] README quickstart works on clean machine

### Bonus Challenges

- Admin dashboard API (aggregate stats from services)
- Product image upload to S3/MinIO
- Wishlist and product reviews services

### Hints

- Start with User + Product; then Order + Payment event flow; then Gateway
- Event envelope: `{event_id, type, correlation_id, timestamp, payload}`
- Mailhog UI: `http://localhost:8025` to verify emails
- Follow phased implementation in README Section 4

---

## Assignment 2: Testing, CI/CD & Quality Gates

### Scenario

Implement the complete quality pipeline for the e-commerce platform — automated testing, CI/CD, security scanning, and deployment automation.

### Requirements

**Testing (full pyramid per service + system level):**

1. **Unit tests** — 200+ total across services; services and schemas mocked appropriately
2. **Integration tests** — DB + message broker per service
3. **Contract tests** — Product Service API schema validated by Order Service tests
4. **E2E test** — `tests/e2e/test_full_purchase.py` against docker-compose stack:
   - Register → login → add to cart → checkout → verify paid → verify email in Mailhog
5. **Load test** — Locust: 100 users, 5 min, < 1% errors, p95 < 1s for product browse

**CI pipeline (`.github/workflows/ci.yml`):**

```yaml
jobs:
  lint:       # ruff/black/mypy
  unit:       # pytest tests/unit --cov
  integration: # docker-compose test stack
  e2e:        # nightly or on main only
  security:   # pip-audit, bandit
  build:      # docker build all services
```

**Quality gates (merge blocked if):**

- Coverage < 75% overall
- Any unit test failing
- `mypy` errors on `shared/` and service layers
- Critical CVE in `pip-audit`
- E2E failing on main branch

**CD pipeline (`.github/workflows/cd.yml`):**

- On release tag: build → push to registry → deploy to staging
- Smoke test after deploy: `production_readiness.py`
- Manual workflow dispatch for production

**Test data management:**

- `scripts/seed.py` — seed products, admin user, test customer
- Idempotent seed (safe to run multiple times)

**Documentation `TESTING.md`:**

- How to run each test tier locally
- How CI differs from local
- Flaky test debugging guide
- Coverage report location

### Technical Specifications

- Complete testing pyramid
- Contract and E2E testing
- Locust load testing
- GitHub Actions CI/CD
- Security scanning (pip-audit, bandit)
- Quality gates and coverage thresholds
- Test seeding scripts

### Acceptance Criteria

- [ ] CI pipeline YAML present and logically structured
- [ ] 200+ unit tests pass in < 2 minutes total
- [ ] E2E purchase test passes against docker-compose
- [ ] Locust results documented with pass/fail against SLAs
- [ ] `pip-audit` and `bandit` run without critical findings
- [ ] CD deploys to staging (local kind/minikube or documented cloud)
- [ ] `seed.py` populates demo data for manual testing
- [ ] TESTING.md enables new developer to run all test tiers

### Bonus Challenges

- Mutation testing on Order Service saga logic
- DAST scan with OWASP ZAP in CI
- Performance regression: fail CI if p95 increases > 20% from baseline

### Hints

- CI integration tests: `docker compose -f docker-compose.test.yml up -d --wait`
- E2E Mailhog: HTTP API `http://localhost:8025/api/v2/messages` to assert email
- Cache coverage across services: `coverage combine` for monorepo report

---

## Assignment 3: Production Launch Package

### Scenario

Finalize the e-commerce platform for production launch — Kubernetes deployment, observability stack, operational runbooks, and portfolio presentation. This assignment proves job-readiness.

### Requirements

**Kubernetes (`k8s/`):**

- Deployment + Service for each of 6 services
- StatefulSet or managed DB documented (or CNPG operator notes)
- Ingress with TLS (cert-manager or self-signed for local)
- HPA on gateway and product service
- ConfigMaps and Secrets (templated)
- NetworkPolicy: only gateway exposed externally

**Observability stack (`docker-compose.observability.yml` or k8s addons):**

- Prometheus + Grafana
- Jaeger
- Loki or ELK for logs (optional)
- Pre-built Grafana dashboard: business metrics (orders/hour, revenue) + technical (latency, errors)

**Business metrics instrumentation:**

- `orders_created_total`, `revenue_total`, `user_registrations_total`
- Grafana panels for each

**Operational docs:**

1. **`README.md`** — project overview, architecture diagram, quickstart ≤ 30 min
2. **`ARCHITECTURE.md`** — C4 diagram (context + container level), data ownership, event catalog
3. **`RUNBOOK.md`** — deploy, rollback, scale, debug order, rotate secrets, incident response
4. **`API.md`** — link to gateway OpenAPI; authentication guide
5. **`PRODUCTION_CHECKLIST.md`** — 100% complete from Part 20 Assignment 3
6. **`EVENT_CATALOG.md`** — all events: type, producer, consumers, payload schema

**Security final review:**

- Penetration self-test checklist (OWASP Top 10 mapping)
- All endpoints authorization matrix (public/authenticated/admin)
- Secrets in vault; `.env` never committed

**Performance final review:**

- `PERFORMANCE.md` — load test results, optimizations applied, SLAs met
- Caching hit rate metrics from Redis

**Portfolio presentation:**

- `DEMO.md` — 5-minute demo script with curl commands or Postman collection
- Architecture diagram (PNG or mermaid in README)
- 3-minute elevator pitch paragraph for resume/LinkedIn
- List of technologies used (skills matrix)

**Final integration verification script `scripts/verify_platform.sh`:**

Checks (exit 0 only if all pass):
1. All services healthy
2. E2E test passes
3. Grafana dashboard loads
4. Sample order completes
5. Email received in Mailhog
6. Trace visible in Jaeger
7. Coverage ≥ 75%
8. `production_readiness.py` passes

### Technical Specifications

- Full Kubernetes deployment
- Prometheus + Grafana monitoring
- Distributed tracing
- Complete operational documentation
- Event catalog for event-driven architecture
- Security and performance final review
- Portfolio-quality presentation

### Acceptance Criteria

- [ ] Platform deployable to local Kubernetes (kind/minikube) with documented steps
- [ ] Grafana dashboard shows live order metrics during demo
- [ ] All 6 documentation files complete and consistent
- [ ] EVENT_CATALOG.md documents ≥ 8 event types
- [ ] Authorization matrix covers all endpoints
- [ ] `verify_platform.sh` passes on clean deploy
- [ ] DEMO.md enables 5-minute live demo without improvisation
- [ ] Project suitable for GitHub portfolio and resume link

### Bonus Challenges

- Helm umbrella chart for entire platform
- Multi-region deployment design document
- Cost optimization report (right-sizing pods, reserved instances)
- Video demo recording script

### Hints

- Event catalog table: Event | Producer | Consumers | Topic/Queue | Payload fields
- C4 diagram: use mermaid `C4Context` or draw.io export
- Demo script: exact curl commands with expected JSON responses
- Verify script: orchestrate existing scripts; don't duplicate logic

---

## Final Submission Checklist

Before considering the course complete, verify:

- [ ] All 21 parts' concepts appear somewhere in the platform
- [ ] `docker-compose up` → `verify_platform.sh` → exit 0
- [ ] README enables setup in < 30 minutes
- [ ] GitHub repo has clear structure, no secrets committed
- [ ] You can explain every architectural decision in a technical interview
- [ ] Resume lists: Python, FastAPI, SQLAlchemy, Redis, PostgreSQL, Docker, Kubernetes, RabbitMQ/Kafka, pytest, microservices

**Congratulations — completing this capstone demonstrates production-ready Python backend engineering skills.**
