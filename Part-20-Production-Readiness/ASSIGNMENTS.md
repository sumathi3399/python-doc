# Part 20: Production Readiness - Practice Problems

> Test Docker, K8s, monitoring, security

---

## Problem 1: Basic Dockerfile

**Task**: Create Dockerfile for FastAPI
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Time**: 15 minutes

---

## Problem 2: Docker Compose

**Task**: Define app + database
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

**Time**: 15 minutes

---

## Problem 3: Health Check Endpoint

**Task**: Kubernetes liveness probe
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ready")
def ready():
    # Check dependencies
    return {"status": "ready"}
```

**Time**: 10 minutes

---

## Problem 4: Kubernetes Deployment

**Task**: Create deployment YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
```

**Time**: 20 minutes

---

## Problem 5: Environment Variables

**Task**: Load config from env
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

settings = Settings()
```

**Time**: 10 minutes

---

## Problem 6: Structured Logging

**Task**: JSON logging format
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
```

**Time**: 20 minutes

---

## Problem 7: Prometheus Metrics

**Task**: Expose metrics endpoint
```python
from prometheus_client import Counter, make_asgi_app
from fastapi import FastAPI

app = FastAPI()

request_count = Counter('http_requests_total', 'Total requests')

@app.middleware("http")
async def count_requests(request, call_next):
    request_count.inc()
    return await call_next(request)

# Mount metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Time**: 20 minutes

---

## Problem 8: Rate Limiting with Redis

**Task**: Limit requests per user
```python
import redis
from fastapi import HTTPException

r = redis.Redis()

def check_rate_limit(user_id, limit=100, window=60):
    key = f"rate:{user_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, window)
    if count > limit:
        raise HTTPException(429, "Rate limit exceeded")
```

**Time**: 20 minutes

---

## Problem 9: Graceful Shutdown

**Task**: Handle SIGTERM
```python
import signal
import sys

def graceful_shutdown(signum, frame):
    print("Shutting down gracefully...")
    # Close connections
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
```

**Time**: 15 minutes

---

## Problem 10: Security Headers

**Task**: Add security middleware
```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)
```

**Time**: 15 minutes

---

## Summary Check

**7+ solved** → Production ready  
**4-6 solved** → Practice Docker and K8s  
**< 4 solved** → Review deployment basics
