# Part 17: Microservices Architecture - Assignments

## Assignment Guidelines

- **Estimated time:** 20-28 hours total
- **Prerequisites:** Parts 1-16 complete
- **Submission:** Multi-service project with Docker Compose, API Gateway, and observability basics
- **Rules:** Each service owns its database; communicate via APIs/events only — no shared DB tables

---

## Assignment 1: User & Product Microservices with API Gateway

### Scenario

Decompose a monolithic e-commerce app into independent User and Product microservices behind an API Gateway. Each service deploys, scales, and fails independently.

### Requirements

**Services:**

1. **User Service** (port 8001)
   - Own PostgreSQL/SQLite database `users_db`
   - CRUD users, JWT auth (register/login)
   - `GET /health`, `GET /ready`
   - Publishes `user.created` event to message broker stub (in-memory or Redis/RabbitMQ)

2. **Product Service** (port 8002)
   - Own database `products_db`
   - CRUD products, categories, search
   - No direct access to users table — only stores `owner_id` as int
   - `GET /health`, `GET /ready`

3. **API Gateway** (port 8000)
   - Routes `/api/v1/users/*` → User Service
   - Routes `/api/v1/products/*` → Product Service
   - JWT validation at gateway for protected routes
   - Request logging with correlation ID (`X-Correlation-ID` generated or forwarded)
   - Rate limiting (in-memory or Redis): 100 req/min per IP
   - Aggregated `GET /health` — reports status of all downstream services

**Service discovery (basic):**

- `ServiceRegistry` class — services register on startup with name, host, port, health URL
- Gateway looks up service URL from registry (in-memory dict or Redis)
- Heartbeat: services re-register every 30s; stale entries removed after 90s

**Resilience:**

- **Circuit breaker** on gateway → downstream calls (3 failures → open 30s → half-open)
- Timeout on proxy requests: 5 seconds
- Fallback response when circuit open: `503` with JSON message

**Docker Compose:**

```yaml
services:
  gateway, user-service, product-service, user-db, product-db, redis (optional)
```

**Each service structure:** layered FastAPI app from Part 16 (slim version)

### Technical Specifications

- Microservice boundaries and database-per-service
- API Gateway pattern (routing, auth, rate limit)
- Service discovery (basic registry)
- Circuit breaker pattern
- Correlation IDs for tracing
- Health and readiness checks
- Docker Compose orchestration

### Acceptance Criteria

- [ ] User and Product services run independently; stopping one doesn't crash the other
- [ ] Gateway routes correctly; client never calls 8001/8002 directly in docs
- [ ] JWT issued by User Service validated at Gateway
- [ ] Correlation ID appears in both gateway and service logs for same request
- [ ] Circuit breaker opens after 3 simulated failures; returns 503
- [ ] `docker-compose up` starts all services healthy
- [ ] Each service has own migration/schema — no cross-DB joins
- [ ] Architecture diagram in README

### Bonus Challenges

- OpenTelemetry trace propagation gateway → services
- Gateway response caching for GET products (30s TTL)
- Kubernetes manifests for one service

### Hints

- Gateway proxy: `httpx.AsyncClient` forward request with headers
- Circuit states: closed → open (after failures) → half-open (one trial)
- Registry key: `services:user-service` → `{host, port, last_heartbeat}`

---

## Assignment 2: Order Service with Event-Driven Integration

### Scenario

Add an Order Service that coordinates with User and Product services asynchronously. When an order is placed, events notify inventory and analytics services without tight coupling.

### Requirements

**Order Service** (port 8003, own `orders_db`):

- `POST /orders` — create order with items (product_id, quantity)
- Validates user exists via **sync REST call** to User Service (with circuit breaker)
- Validates stock via **sync REST call** to Product Service
- Stores order with status: `pending` → `confirmed` → `shipped` → `delivered`
- Publishes events:
  - `order.created`
  - `order.confirmed`
  - `order.cancelled`

**Inventory Worker** (or Product Service consumer):

- Subscribes to `order.created`
- Reserves/reduces stock
- Publishes `inventory.reserved` or `inventory.failed`

**Analytics Service** (port 8004, lightweight):

- Subscribes to all order events
- Stores event counts in own DB or in-memory metrics
- `GET /analytics/orders/summary` — totals by status

**Message broker:** Redis Pub/Sub, RabbitMQ, or Kafka (pick one; document choice)

**Patterns:**

- Event-driven architecture
- Saga-style compensation: on `inventory.failed`, Order Service cancels order and publishes `order.cancelled`
- Idempotent event handlers: `event_id` deduplication in Redis `SET NX`
- Dead letter queue for failed event processing (3 retries)

**Distributed tracing:**

- Correlation ID passed in events and REST calls
- Log structured: `order_id`, `correlation_id`, `event_type`

**Centralized logging format (all services):**

```json
{"timestamp", "service", "level", "correlation_id", "message", "extra"}
```

### Technical Specifications

- Event-driven communication
- REST for sync validation; messaging for async workflows
- Saga/compensation pattern
- Idempotent consumers
- Correlation ID propagation
- Centralized logging format
- Service autonomy

### Acceptance Criteria

- [ ] Order creation triggers inventory update without direct DB access to product DB
- [ ] Inventory failure cancels order (compensation demonstrated)
- [ ] Duplicate `order.created` event processed only once (idempotency key)
- [ ] Analytics reflects order counts after 5 test orders
- [ ] Correlation ID traceable across REST + event logs in README example
- [ ] Dead letter queue receives event after 3 handler failures (simulated)
- [ ] All services start via docker-compose

### Bonus Challenges

- Outbox pattern: write event to outbox table in same transaction as order
- Kafka partitioning by `order_id`
- Jaeger UI showing trace across 4 services

### Hints

- Event envelope: `{event_id, type, timestamp, correlation_id, payload}`
- Saga: Order listens for `inventory.failed` → update status cancelled
- Idempotency: `if redis.setnx(f"processed:{event_id}", 1): handle()`

---

## Assignment 3: Resilient Microservices Platform (Capstone)

### Scenario

Harden the microservices platform with full observability, configuration management, and production patterns — integrating everything from Part 17 into one deployable system.

### Requirements

**Extend previous assignments with:**

1. **Config server pattern (lightweight):**
   - Shared `config/` repo or env files per environment
   - Each service loads `COMMON_CONFIG` + service-specific overrides
   - Hot-reload config on `SIGHUP` or polling (optional)

2. **Circuit breaker library** — shared module `shared/resilience.py`:
   - Reusable `@circuit_breaker` decorator or wrapper for httpx calls
   - Metrics: failure count, state exported at `GET /metrics` (Prometheus text format stub)

3. **Distributed tracing:**
   - OpenTelemetry SDK in each service
   - Export to Jaeger (docker-compose sidecar)
   - Propagate `traceparent` header gateway → services

4. **API Gateway enhancements:**
   - Request/response logging to stdout (JSON)
   - CORS, security headers (`X-Content-Type-Options`, etc.)
   - Load balancing: round-robin across 2 Product Service instances

5. **Service mesh concepts (documented):**
   - mTLS between services (conceptual or Linkerd/Istio notes)
   - Retry policy: 3 retries, exponential backoff on 502/503

6. **Chaos testing script:**
   - `chaos.py` randomly stops a container; gateway returns degraded health
   - Document expected behavior

7. **Complete docker-compose** with:
   - gateway, 3 business services, 3 databases, redis, rabbitmq/kafka, jaeger

8. **Documentation:**
   - `ARCHITECTURE.md` — boundaries, data ownership, communication matrix
   - `RUNBOOK.md` — how to debug failed order, read traces, reset circuit breaker

**Communication matrix table (required in README):**

| From | To | Method | Sync/Async | Purpose |
|------|-----|--------|------------|---------|
| Gateway | User | HTTP | Sync | Proxy auth |
| Order | Product | HTTP | Sync | Stock check |
| Order | Inventory | Event | Async | Reserve stock |

### Technical Specifications

- All Part 17 patterns integrated
- API Gateway, service discovery, circuit breaker
- Distributed tracing (OpenTelemetry/Jaeger)
- Centralized structured logging
- Event-driven architecture
- Docker Compose full stack
- Operational documentation

### Acceptance Criteria

- [ ] 2 Product Service instances; gateway load balances between them
- [ ] Jaeger shows trace for `POST /orders` spanning ≥ 3 services
- [ ] Circuit breaker metrics visible at `/metrics`
- [ ] Chaos script documented with before/after health check output
- [ ] No service accesses another service's database
- [ ] RUNBOOK explains debugging steps with examples
- [ ] Full stack starts with one command

### Bonus Challenges

- Consul or etcd for real service discovery
- Canary deployment notes with two gateway routes
- Policy: Product Service v2 behind header `X-API-Version: 2`

### Hints

- OTel: `opentelemetry-instrumentation-fastapi`
- Round-robin: gateway maintains index counter per service name
- Shared module: publish as local pip package `shared/` in monorepo
