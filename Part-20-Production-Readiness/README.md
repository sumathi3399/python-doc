# Part 20: Production Readiness

> Deploy your FastAPI applications to production with confidence using Docker, Kubernetes, monitoring, and observability.

## 📚 Table of Contents

1. [Docker & Containerization](#1-docker--containerization)
2. [Kubernetes Deployment](#2-kubernetes-deployment)
3. [Configuration Management](#3-configuration-management)
4. [Secrets Management](#4-secrets-management)
5. [Logging & Monitoring](#5-logging--monitoring)
6. [Health Checks](#6-health-checks)
7. [Graceful Shutdown](#7-graceful-shutdown)
8. [Performance Optimization](#8-performance-optimization)
9. [Security Best Practices](#9-security-best-practices)
10. [Exercises](#exercises)

---

## 1. Docker & Containerization

### Dockerfile for FastAPI

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Stage Build (Optimized)

```dockerfile
# Multi-stage Dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/appdb
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./app:/app/app  # Mount for development
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=appdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

### .dockerignore

```
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.pytest_cache
.hypothesis
.vscode
.idea
*.swp
*.swo
*~
.DS_Store
```

---

## 2. Kubernetes Deployment

### Deployment Manifest

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  labels:
    app: fastapi
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: your-registry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service Manifest

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  redis-url: "redis://redis-service:6379"
  log-level: "INFO"
  workers: "4"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-url: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0BwZz01NDMyL2RiCg==  # base64 encoded
  api-key: c2VjcmV0LWtleQ==  # base64 encoded
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 3. Configuration Management

### Pydantic Settings

```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    app_name: str = "FastAPI App"
    debug: bool = False
    environment: str = "production"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database
    database_url: str
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Redis
    redis_url: str
    redis_ttl: int = 3600
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list[str] = ["*"]
    
    # Monitoring
    log_level: str = "INFO"
    sentry_dsn: Optional[str] = None
    
    # External Services
    external_api_url: Optional[str] = None
    external_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()
```

### Environment Files

```bash
# .env.development
DEBUG=true
ENVIRONMENT=development
DATABASE_URL=postgresql://user:pass@localhost:5432/dev_db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:3000"]

# .env.production
DEBUG=false
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/prod_db
REDIS_URL=redis://prod-redis:6379
LOG_LEVEL=INFO
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Using Configuration

```python
# app/main.py
from app.config import settings
from fastapi import FastAPI

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

@app.on_event("startup")
async def startup():
    print(f"Starting {settings.app_name}")
    print(f"Environment: {settings.environment}")
    print(f"Workers: {settings.workers}")

# Use settings throughout the app
@app.get("/config")
async def get_config():
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug
    }
```

---

## 4. Secrets Management

### AWS Secrets Manager

```python
# app/secrets.py
import boto3
import json
from functools import lru_cache

class SecretsManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager', region_name='us-east-1')
    
    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> dict:
        """Get secret from AWS Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            raise

secrets_manager = SecretsManager()

# Usage
db_credentials = secrets_manager.get_secret("prod/database")
DATABASE_URL = f"postgresql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['database']}"
```

### HashiCorp Vault

```python
# app/vault.py
import hvac

class VaultClient:
    def __init__(self, url: str, token: str):
        self.client = hvac.Client(url=url, token=token)
    
    def get_secret(self, path: str) -> dict:
        """Get secret from Vault"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path
            )
            return response['data']['data']
        except Exception as e:
            logger.error(f"Failed to get secret from Vault: {e}")
            raise

vault = VaultClient(
    url="https://vault.example.com",
    token=os.getenv("VAULT_TOKEN")
)

# Usage
secrets = vault.get_secret("app/database")
DATABASE_URL = secrets["database_url"]
```

### Kubernetes Secrets

```python
# Mount secrets as environment variables or files

# As environment variables (already shown in k8s manifests)

# As files
# k8s/deployment.yaml
spec:
  containers:
  - name: fastapi
    volumeMounts:
    - name: secrets
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: app-secrets

# Read in application
with open("/etc/secrets/database-url") as f:
    DATABASE_URL = f.read().strip()
```

---

## 5. Logging & Monitoring

### Structured Logging

```python
# app/logging_config.py
import logging
import structlog
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    handler = logging.StreamHandler()
    handler.setFormatter(jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    ))
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

# Usage
logger = structlog.get_logger()

@app.post("/users")
async def create_user(user: UserCreate):
    logger.info(
        "creating_user",
        email=user.email,
        user_type=user.user_type,
        correlation_id=request.state.correlation_id
    )
    
    try:
        user_id = await user_service.create(user)
        logger.info("user_created", user_id=user_id)
        return {"user_id": user_id}
    except Exception as e:
        logger.error(
            "user_creation_failed",
            error=str(e),
            exc_info=True
        )
        raise
```

### Prometheus Metrics

```python
# app/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import time

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect metrics for each request"""
    active_requests.inc()
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Record metrics
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    active_requests.dec()
    
    return response

@app.get("/metrics")
async def metrics():
    """Expose metrics for Prometheus"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Application Performance Monitoring (APM)

```python
# app/apm.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def setup_sentry(dsn: str, environment: str):
    """Configure Sentry APM"""
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=1.0,  # 100% of transactions
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
    )

# Usage in main.py
if settings.sentry_dsn:
    setup_sentry(settings.sentry_dsn, settings.environment)
```

---

## 6. Health Checks

### Comprehensive Health Checks

```python
# app/health.py
from fastapi import APIRouter, status
from typing import Dict, Any
import asyncio

router = APIRouter()

async def check_database() -> Dict[str, Any]:
    """Check database connection"""
    try:
        await db.execute("SELECT 1")
        return {"status": "healthy", "latency_ms": 5}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis() -> Dict[str, Any]:
    """Check Redis connection"""
    try:
        await redis.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_external_service() -> Dict[str, Any]:
    """Check external service"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.external_api_url}/health")
            if response.status_code == 200:
                return {"status": "healthy"}
            return {"status": "degraded", "status_code": response.status_code}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@router.get("/ready")
async def readiness_check():
    """Readiness check - can it handle requests?"""
    # Check all dependencies
    checks = await asyncio.gather(
        check_database(),
        check_redis(),
        check_external_service(),
        return_exceptions=True
    )
    
    database, redis_check, external = checks
    
    # Determine overall status
    is_ready = (
        database["status"] == "healthy" and
        redis_check["status"] == "healthy"
    )
    
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(
        content=json.dumps({
            "status": "ready" if is_ready else "not_ready",
            "checks": {
                "database": database,
                "redis": redis_check,
                "external_service": external
            }
        }),
        status_code=status_code,
        media_type="application/json"
    )

@router.get("/live")
async def liveness_check():
    """Liveness check - is it running?"""
    return {"status": "alive"}
```

---

## 7. Graceful Shutdown

### Handling Shutdown Signals

```python
# app/shutdown.py
import signal
import asyncio
from contextlib import asynccontextmanager

class GracefulShutdown:
    def __init__(self):
        self.is_shutting_down = False
        self.active_requests = 0
    
    async def shutdown(self):
        """Handle graceful shutdown"""
        self.is_shutting_down = True
        logger.info("Shutting down gracefully...")
        
        # Wait for active requests to complete (with timeout)
        timeout = 30  # 30 seconds
        start = time.time()
        
        while self.active_requests > 0 and (time.time() - start) < timeout:
            logger.info(f"Waiting for {self.active_requests} active requests...")
            await asyncio.sleep(1)
        
        # Close connections
        await db.close()
        await redis.close()
        
        logger.info("Shutdown complete")

shutdown_handler = GracefulShutdown()

@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track active requests"""
    if shutdown_handler.is_shutting_down:
        return Response(
            content="Service is shutting down",
            status_code=503
        )
    
    shutdown_handler.active_requests += 1
    try:
        response = await call_next(request)
        return response
    finally:
        shutdown_handler.active_requests -= 1

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting...")
    
    # Register signal handlers
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(shutdown_handler.shutdown())
        )
    
    yield
    
    # Shutdown
    await shutdown_handler.shutdown()

app = FastAPI(lifespan=lifespan)
```

---

## 8. Performance Optimization

### Connection Pooling

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

# Configure connection pool
engine = create_async_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,  # 5
    max_overflow=settings.database_max_overflow,  # 10
    pool_pre_ping=True,  # Test connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=settings.debug,
)
```

### Caching Strategy

```python
# app/cache.py
from functools import wraps
import json
import hashlib

def cache_result(ttl: int = 3600):
    """Cache function result in Redis"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached = await redis.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {func.__name__}")
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await redis.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=3600)
async def get_popular_products():
    """Get popular products (cached for 1 hour)"""
    products = await db.query(Product).order_by(Product.sales.desc()).limit(10).all()
    return [product.dict() for product in products]
```

### Response Compression

```python
# app/middleware.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB
```

### Database Query Optimization

```python
# Use select load strategies
from sqlalchemy.orm import selectinload, joinedload

# Bad: N+1 queries
users = await db.query(User).all()
for user in users:
    orders = await user.orders  # Separate query for each user!

# Good: Eager loading
users = await db.query(User).options(selectinload(User.orders)).all()
for user in users:
    orders = user.orders  # Already loaded!

# Good: Joined load for one-to-one
user = await db.query(User).options(joinedload(User.profile)).first()
```

---

## 9. Security Best Practices

### Security Headers

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers"""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/resource")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
    return {"message": "This endpoint is rate limited"}
```

### Input Validation & Sanitization

```python
from pydantic import validator, Field

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)
    
    @validator('name')
    def sanitize_name(cls, v):
        # Remove any HTML tags
        import re
        v = re.sub(r'<[^>]*>', '', v)
        return v.strip()
```

### SQL Injection Prevention

```python
# ✅ Good: Using ORM (parameterized queries)
user = await db.query(User).filter(User.email == email).first()

# ✅ Good: Using parameters with raw SQL
result = await db.execute(
    "SELECT * FROM users WHERE email = :email",
    {"email": email}
)

# ❌ Bad: String formatting (vulnerable to SQL injection!)
# NEVER DO THIS:
result = await db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

---

## Exercises

### Level 1: Basic

1. **Docker Setup**
   - Create Dockerfile
   - Build and run container
   - Use Docker Compose

2. **Configuration**
   - Environment variables
   - Multiple environments
   - Configuration validation

3. **Health Checks**
   - Implement basic health check
   - Add readiness probe
   - Test liveness probe

### Level 2: Intermediate

4. **Kubernetes Deployment**
   - Create manifests
   - Deploy to cluster
   - Configure autoscaling

5. **Monitoring**
   - Add Prometheus metrics
   - Structured logging
   - APM integration

6. **Performance**
   - Connection pooling
   - Caching strategy
   - Query optimization

### Level 3: Challenging

7. **Complete Production Setup**
   - Multi-environment deployment
   - Full observability
   - Security hardening
   - Load testing

---

## Key Takeaways

✅ **Deployment**:
- Docker for containerization
- Kubernetes for orchestration
- Multi-stage builds for optimization

✅ **Configuration**:
- Environment-based config
- Secrets management
- Validation

✅ **Observability**:
- Structured logging
- Metrics (Prometheus)
- Distributed tracing
- APM (Sentry)

✅ **Reliability**:
- Health checks (liveness, readiness)
- Graceful shutdown
- Connection pooling
- Caching

✅ **Security**:
- Security headers
- Rate limiting
- Input validation
- Secrets management

---

Continue to [Part-21-Complete-Project](../Part-21-Complete-Project/README.md)!
