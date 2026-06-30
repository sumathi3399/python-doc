# Part 17: Microservices - Practice Problems

> Test service boundaries, gateway, discovery

---

## Problem 1: Service Health Check

**Task**: Add health endpoint to service
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "user-service"}
```

**Time**: 5 minutes

---

## Problem 2: API Gateway Routing

**Task**: Forward requests to services
```python
import httpx
from fastapi import FastAPI

app = FastAPI()

USER_SERVICE = "http://localhost:8001"

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE}/users/{user_id}")
        return response.json()
```

**Time**: 20 minutes

---

## Problem 3: Service Discovery Registry

**Task**: Simple in-memory registry
```python
services = {}

def register_service(name, url):
    services[name] = url

def get_service(name):
    return services.get(name)

register_service("user-service", "http://localhost:8001")
url = get_service("user-service")
```

**Time**: 15 minutes

---

## Problem 4: Circuit Breaker (Basic)

**Task**: Track failures and open circuit
```python
import time

class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=30):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func()
            self.failure_count = 0
            self.state = "CLOSED"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise e
```

**Time**: 30 minutes

---

## Problem 5: Correlation ID Middleware

**Task**: Track requests across services
```python
from fastapi import FastAPI, Request
import uuid

app = FastAPI()

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

**Time**: 15 minutes

---

## Problem 6: Rate Limiting

**Task**: Simple rate limiter
```python
import time
from collections import defaultdict

rate_limits = defaultdict(list)

def rate_limit(ip, max_requests=10, window=60):
    now = time.time()
    # Clean old requests
    rate_limits[ip] = [t for t in rate_limits[ip] if now - t < window]
    
    if len(rate_limits[ip]) >= max_requests:
        return False
    
    rate_limits[ip].append(now)
    return True

# Use in endpoint
if not rate_limit(request.client.host):
    raise HTTPException(429, "Too many requests")
```

**Time**: 20 minutes

---

## Problem 7: Config Per Service

**Task**: Environment-specific settings
```python
from pydantic_settings import BaseSettings

class ServiceSettings(BaseSettings):
    service_name: str
    port: int = 8000
    database_url: str
    
    class Config:
        env_prefix = "SERVICE_"

settings = ServiceSettings()
```

**Time**: 10 minutes

---

## Problem 8: Docker Compose Services

**Task**: Define two services
```yaml
version: '3.8'
services:
  user-service:
    build: ./user-service
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgres://...
  
  product-service:
    build: ./product-service
    ports:
      - "8002:8000"
```

**Time**: 15 minutes

---

## Problem 9: Service-to-Service Call with Timeout

**Task**: Call with timeout
```python
import httpx

async def call_other_service(url, timeout=5):
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url)
            return response.json()
        except httpx.TimeoutException:
            return {"error": "Service timeout"}
```

**Time**: 15 minutes

---

## Problem 10: Aggregate Health Check

**Task**: Check all services
```python
import httpx

async def check_all_services():
    services = {
        "user": "http://localhost:8001/health",
        "product": "http://localhost:8002/health"
    }
    
    results = {}
    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            try:
                response = await client.get(url, timeout=2)
                results[name] = response.json()
            except:
                results[name] = {"status": "unhealthy"}
    
    return results
```

**Time**: 20 minutes

---

## Summary Check

**7+ solved** → Microservices basics ready  
**4-6 solved** → Practice service communication  
**< 4 solved** → Review service patterns
