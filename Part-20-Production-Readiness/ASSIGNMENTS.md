# Part 20: Production Readiness - Assignments

## Assignment Guidelines

- **Estimated time:** 18-24 hours total
- **Prerequisites:** Parts 1-19 complete; microservices project from Parts 17-18 recommended
- **Submission:** Production-ready deployment package with Docker, Kubernetes manifests, monitoring, and security hardening
- **Rules:** No secrets in code; all config via environment; health checks required on every service

---

## Assignment 1: Containerization & Kubernetes Deployment

### Scenario

Take the microservices platform (or Bookstore API) from development to a Kubernetes-ready deployment — optimized Docker images, orchestration manifests, and environment-specific configuration.

### Requirements

**Docker (each service):**

1. **Multi-stage Dockerfile:**
   - Stage 1: build dependencies with `pip wheel`
   - Stage 2: `python:3.11-slim` runtime, copy wheels, non-root user `appuser`
   - Image size documented before/after optimization

2. **`.dockerignore`** — exclude tests, `.git`, `__pycache__`

3. **Health check in Dockerfile:**
   ```dockerfile
   HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
   ```

4. **docker-compose.prod.yml** — production overrides:
   - No volume mounts for source code
   - Restart policies `unless-stopped`
   - Resource limits (memory, CPU)
   - Secrets via env files (not committed)

**Kubernetes manifests (`k8s/`):**

1. **Deployment** per service — replicas: 2 for stateless services
2. **Service** — ClusterIP for internal; LoadBalancer or Ingress for gateway
3. **ConfigMap** — non-secret config (LOG_LEVEL, ENVIRONMENT)
4. **Secret** — template `secret.yaml.example` (base64 placeholders); document `kubectl create secret`
5. **Ingress** — route `api.example.local` to gateway
6. **HorizontalPodAutoscaler** — CPU target 70%, min 2 max 5 replicas for gateway
7. **Liveness probe** — `GET /health` initialDelaySeconds: 10
8. **Readiness probe** — `GET /ready` checks DB connection
9. **Resource requests/limits** — memory 256Mi/512Mi per service

**Configuration management:**

- `DevelopmentSettings` / `StagingSettings` / `ProductionSettings`
- ConfigMap values injected as env vars
- `get_settings()` cached; document config reload limitations

**Graceful shutdown:**

- Uvicorn `--timeout-graceful-shutdown 30`
- Lifespan hook: close DB pool, flush logs, drain in-flight requests
- `preStop` hook in K8s: `sleep 5` before SIGTERM (document why)

**Deployment scripts:**

- `scripts/deploy.sh` — apply manifests in order
- `scripts/rollback.sh` — `kubectl rollout undo`

### Technical Specifications

- Docker multi-stage builds
- docker-compose production patterns
- Kubernetes Deployments, Services, Ingress
- ConfigMaps and Secrets
- Liveness and readiness probes
- HPA autoscaling
- Graceful shutdown
- Environment-based configuration

### Acceptance Criteria

- [ ] Docker images build without dev dependencies in final stage
- [ ] Containers run as non-root user
- [ ] `kubectl apply -f k8s/` deploys to local cluster (minikube/kind) successfully
- [ ] Readiness probe fails when DB unreachable (test by stopping DB pod)
- [ ] HPA manifest valid (`kubectl apply --dry-run=client`)
- [ ] Graceful shutdown logs "shutting down" and completes in-flight request (test script)
- [ ] `secret.yaml` NOT committed; `.example` file IS committed
- [ ] Image size reduction documented (target: 30%+ smaller than single-stage)

### Bonus Challenges

- Helm chart instead of raw manifests
- NetworkPolicy restricting service-to-service traffic
- PodDisruptionBudget for gateway

### Hints

- Slim image: `RUN pip install --no-cache-dir` in builder only
- Readiness: endpoint calls `SELECT 1` on database
- preStop: allows load balancer to drain connections before pod terminates

---

## Assignment 2: Observability, Security & Performance Hardening

### Scenario

Add production-grade observability (logs, metrics, traces), security controls, and performance optimizations to the deployed platform.

### Requirements

**Logging:**

1. **Structured JSON logs** in production (structlog or python-json-logger)
2. **Correlation ID** in every log line — middleware sets and propagates
3. **Log levels** per module configurable via env
4. **Request logging middleware** — method, path, status, duration_ms, user_id (if auth)
5. **Centralized logging** — Fluentd/Vector sidecar or document ELK/Loki stack integration
6. **No PII in logs** — mask email, never log passwords/tokens

**Metrics (Prometheus):**

1. `prometheus-fastapi-instrumentator` or custom `/metrics` endpoint
2. Metrics exposed:
   - `http_requests_total` by method, path, status
   - `http_request_duration_seconds` histogram
   - `db_connection_pool_size` gauge
   - Custom: `orders_created_total` counter
3. `ServiceMonitor` YAML for Prometheus Operator (or scrape config)
4. **Grafana dashboard JSON** — 4 panels: RPS, error rate, p95 latency, CPU

**APM / Error tracking:**

- Sentry SDK integration — `SENTRY_DSN` from secret
- Sample rate 10% in production
- Test: `GET /debug/sentry-test` raises exception → appears in Sentry (or mock)

**Distributed tracing:**

- OpenTelemetry → Jaeger or OTLP collector
- Trace gateway → order → inventory call chain

**Security:**

1. **Security headers middleware:**
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `Strict-Transport-Security` (document HTTPS requirement)
   - `Content-Security-Policy` baseline

2. **Rate limiting** — Redis-backed, 100/min per IP on gateway

3. **Input validation** — all endpoints use Pydantic; no raw SQL

4. **Secrets management:**
   - Document AWS Secrets Manager / Vault integration (implement mock loader)
   - Rotate `SECRET_KEY` procedure in RUNBOOK

5. **CORS** — explicit allowed origins, no `*` in production config

6. **Dependency scanning** — `pip-audit` or `safety check` in CI

**Performance:**

1. **Connection pooling** — SQLAlchemy pool_size=10, max_overflow=20, pool_pre_ping=True
2. **Redis caching** — cache product catalog; document hit rate target
3. **GZip middleware** for responses > 1KB
4. **Query optimization** — add index; include EXPLAIN output in PERF.md showing improvement
5. **Uvicorn workers** — `(2 * CPU) + 1` documented in deployment guide

### Technical Specifications

- Structured logging and correlation IDs
- Prometheus metrics and Grafana dashboards
- Sentry/error tracking
- OpenTelemetry tracing
- Security headers and rate limiting
- Secrets management patterns
- Connection pooling and caching
- Query optimization

### Acceptance Criteria

- [ ] Logs parseable as JSON; grep by correlation_id returns full request chain
- [ ] `/metrics` returns Prometheus format; `orders_created_total` increments on order
- [ ] Sentry captures test exception (or mock verifier passes)
- [ ] Jaeger shows trace for checkout flow
- [ ] Security headers present on all gateway responses (test script)
- [ ] Rate limit returns 429 after threshold
- [ ] `pip-audit` runs in CI with zero critical CVEs (or documented exceptions)
- [ ] PERF.md documents query before/after index with timings

### Bonus Challenges

- Alertmanager rules YAML for error rate > 5%
- OWASP ZAP scan baseline in CI
- Redis cluster for HA caching

### Hints

- structlog: `structlog.processors.JSONRenderer()`
- Prometheus: `Counter('orders_created_total', 'Orders created')`
- Security middleware: pure ASGI or Starlette `BaseHTTPMiddleware`

---

## Assignment 3: Production Readiness Review & Runbook

### Scenario

Produce the operational documentation and automated checks proving the system is production-ready — the final gate before go-live.

### Requirements

**`PRODUCTION_CHECKLIST.md`** — complete every item with evidence (link to file or test):

| Category | Items |
|----------|-------|
| Deployment | Docker optimized, K8s manifests, HPA, rollback tested |
| Configuration | Env-based config, secrets not in repo, prod validation on startup |
| Reliability | Health/readiness probes, graceful shutdown, circuit breakers |
| Observability | JSON logs, metrics, tracing, dashboards |
| Security | Headers, rate limit, CORS, hashed passwords, pip-audit |
| Performance | Pooling, caching, indexes, load test results |
| Testing | 80%+ coverage, E2E passing, CI green |
| Documentation | README, RUNBOOK, ARCHITECTURE, API docs |

**`RUNBOOK.md` operational procedures:**

1. **Deploy new version** — step-by-step with kubectl/docker-compose
2. **Rollback** — command and verification
3. **Scale service** — manual and HPA behavior
4. **Debug high latency** — check metrics → traces → logs flow
5. **Debug failed order** — trace order_id through services
6. **Rotate secrets** — zero-downtime procedure
7. **Database migration** — alembic upgrade in K8s job
8. **Incident response** — severity levels, who to notify (template)
9. **On-call common alerts** — ErrorRateHigh, PodCrashLooping responses

**Automated readiness check `scripts/production_readiness.py`:**

Script exits 0 only if ALL pass:

- [ ] `GET /health` returns 200 on all services
- [ ] `GET /ready` returns 200 (DB connected)
- [ ] Required env vars set (SECRET_KEY, DATABASE_URL)
- [ ] `/metrics` accessible
- [ ] Security headers present
- [ ] Rate limit header present
- [ ] Log output is valid JSON (one sample line)
- [ ] Database migrations at head (`alembic current` check)
- [ ] SSL/TLS documented for production ingress

**Load test evidence:**

- Attach Locust/k6 results meeting SLAs:
  - p95 latency < 500ms at 50 RPS
  - Error rate < 0.1%
  - No memory leak over 10 minute run (memory stable ±10%)

**Disaster recovery (documented):**

- DB backup schedule and restore test procedure
- RTO/RPO targets stated
- Multi-AZ deployment notes

**CI/CD pipeline (`.github/workflows/deploy.yml`):**

- On tag `v*`: run tests → build images → push registry → deploy staging
- Manual approval gate before production (document)

### Technical Specifications

- Production readiness checklist
- Operational runbooks
- Automated health/readiness verification
- Load testing SLAs
- Disaster recovery documentation
- CI/CD deployment pipeline

### Acceptance Criteria

- [ ] PRODUCTION_CHECKLIST.md 100% items checked with evidence
- [ ] RUNBOOK.md covers all 9 procedures with commands
- [ ] `production_readiness.py` passes on healthy stack
- [ ] Load test meets documented SLAs in PERFORMANCE.md
- [ ] DR restore procedure tested once (document timestamp and result)
- [ ] CI/CD YAML valid; documented secrets needed for pipeline
- [ ] Third-party review: peer can deploy from README alone without asking questions

### Bonus Challenges

- SLO document: 99.9% availability, error budget policy
- Feature flags for dark launches (LaunchDarkly mock or env-based)
- Cost estimate spreadsheet for AWS/GCP monthly run

### Hints

- Readiness script: use `httpx` async gather for parallel health checks
- RUNBOOK: copy-pasteable commands, not prose only
- SLAs: define before load test, then verify
