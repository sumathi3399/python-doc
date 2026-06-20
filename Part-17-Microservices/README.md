# Part 17: Microservices Architecture with FastAPI

> Design, build, and deploy production-ready microservices using FastAPI and modern architectural patterns.

## 📚 Table of Contents

1. [Introduction to Microservices](#1-introduction-to-microservices)
2. [Service Design & Boundaries](#2-service-design--boundaries)
3. [API Gateway Pattern](#3-api-gateway-pattern)
4. [Service Discovery](#4-service-discovery)
5. [Distributed Tracing](#5-distributed-tracing)
6. [Centralized Logging](#6-centralized-logging)
7. [Circuit Breaker Pattern](#7-circuit-breaker-pattern)
8. [Complete Microservices Example](#8-complete-microservices-example)
9. [Exercises](#exercises)

---

## 1. Introduction to Microservices

### What are Microservices?

**Microservices** are an architectural style where an application is composed of small, independent services that communicate over well-defined APIs.

### Monolith vs Microservices

```
MONOLITH:
┌─────────────────────────┐
│   Single Application    │
│  ┌──────────────────┐  │
│  │  User Service    │  │
│  │  Order Service   │  │
│  │  Product Service │  │
│  │  Payment Service │  │
│  └──────────────────┘  │
│    Single Database      │
└─────────────────────────┘

MICROSERVICES:
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  User    │  │  Order   │  │ Product  │  │ Payment  │
│ Service  │  │ Service  │  │ Service  │  │ Service  │
├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤
│   DB     │  │   DB     │  │   DB     │  │   DB     │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### When to Use Microservices

**✅ Good Fit:**
- Large, complex applications
- Multiple teams working independently
- Different scaling requirements per service
- Need for technology diversity
- Frequent deployments

**❌ Not Recommended:**
- Small applications
- Single team
- Simple requirements
- Tight coupling between features
- Limited infrastructure

### Microservices Characteristics

```python
# 1. Single Responsibility
# Each service does ONE thing well

# User Service - Only handles users
@app.post("/users")
async def create_user(user: UserCreate):
    return user_service.create(user)

# 2. Independent Deployment
# Can deploy without affecting other services

# 3. Decentralized Data
# Each service owns its database

# 4. API-First Design
# Services communicate via well-defined APIs
```

---

## 2. Service Design & Boundaries

### Domain-Driven Design (DDD)

**Identify Bounded Contexts:**

```python
# E-commerce Domain Model

# 1. User Context
class User:
    id: int
    email: str
    profile: UserProfile

# 2. Product Context
class Product:
    id: int
    name: str
    price: Decimal
    inventory: int

# 3. Order Context
class Order:
    id: int
    user_id: int  # Reference to User
    items: List[OrderItem]
    status: OrderStatus

# 4. Payment Context
class Payment:
    id: int
    order_id: int  # Reference to Order
    amount: Decimal
    status: PaymentStatus
```

### Service Boundaries

```python
# BAD: Too Fine-Grained
# Too many services, too much overhead
- UserEmailService
- UserPasswordService
- UserProfileService
- UserAuthenticationService

# GOOD: Cohesive Services
# Right level of granularity
- UserService (handles all user operations)
- AuthService (authentication & authorization)

# BAD: Too Coarse-Grained
# Essentially a monolith
- EverythingService

# GOOD: Well-Defined Boundaries
- UserService
- ProductService
- OrderService
- PaymentService
```

### Service Communication Patterns

```python
# 1. Synchronous (REST/HTTP)
# User Service → Order Service
async with httpx.AsyncClient() as client:
    response = await client.get(f"{ORDER_SERVICE_URL}/orders/{order_id}")
    order = response.json()

# 2. Asynchronous (Message Queue)
# Order Service → Payment Service (via Kafka)
await kafka_producer.send("order.created", {
    "order_id": order_id,
    "amount": total_amount
})

# 3. Event-Driven
# Payment successful → Update order status
@kafka_consumer.subscribe("payment.completed")
async def on_payment_completed(event):
    await order_service.mark_as_paid(event["order_id"])
```

### Data Management Strategies

```python
# 1. Database per Service
"""
User Service → PostgreSQL (user_db)
Product Service → PostgreSQL (product_db)
Order Service → PostgreSQL (order_db)
Inventory Service → MongoDB (inventory_db)
"""

# 2. Shared Nothing
# Services don't share databases

# 3. API Composition
# Aggregate data from multiple services
async def get_order_details(order_id: int):
    # Get order from Order Service
    order = await order_service.get(order_id)
    
    # Get user from User Service
    user = await user_service.get(order.user_id)
    
    # Get products from Product Service
    products = await product_service.get_many(order.product_ids)
    
    # Compose response
    return {
        "order": order,
        "user": user,
        "products": products
    }

# 4. Event Sourcing (for complex scenarios)
# Store all changes as events
```

---

## 3. API Gateway Pattern

### What is an API Gateway?

A single entry point for all clients that routes requests to appropriate microservices.

```
Client → API Gateway → [User Service, Order Service, Product Service]
```

### Simple API Gateway with FastAPI

```python
# gateway.py
from fastapi import FastAPI, Request
import httpx
from typing import Any

app = FastAPI(title="API Gateway")

# Service URLs
SERVICES = {
    "users": "http://user-service:8001",
    "products": "http://product-service:8002",
    "orders": "http://order-service:8003"
}

async def proxy_request(service: str, path: str, request: Request) -> Any:
    """Forward request to appropriate service"""
    service_url = SERVICES.get(service)
    if not service_url:
        raise HTTPException(404, f"Service {service} not found")
    
    url = f"{service_url}{path}"
    
    async with httpx.AsyncClient() as client:
        # Forward request with same method, headers, body
        response = await client.request(
            method=request.method,
            url=url,
            headers=request.headers,
            content=await request.body()
        )
        return response.json()

# Route to services
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(service: str, path: str, request: Request):
    return await proxy_request(service, f"/{path}", request)

# Example usage:
# GET http://gateway/users/123 → http://user-service:8001/users/123
# POST http://gateway/orders → http://order-service:8003/orders
```

### API Gateway with Authentication

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional
import httpx

app = FastAPI(title="API Gateway with Auth")

async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token"""
    if not authorization:
        raise HTTPException(401, "Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    # Verify with auth service
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://auth-service:8000/verify",
            json={"token": token}
        )
        if response.status_code != 200:
            raise HTTPException(401, "Invalid token")
        return response.json()

@app.get("/users/me")
async def get_current_user(user = Depends(verify_token)):
    """Get current user from User Service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://user-service:8001/users/{user['user_id']}"
        )
        return response.json()

@app.get("/orders")
async def get_user_orders(user = Depends(verify_token)):
    """Get orders for current user"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://order-service:8003/orders?user_id={user['user_id']}"
        )
        return response.json()
```

### API Gateway Features

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import time
from collections import defaultdict

app = FastAPI()

# 1. Rate Limiting
rate_limit_store = defaultdict(list)

async def rate_limit(request: Request):
    client_ip = request.client.host
    now = time.time()
    
    # Clean old entries
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] 
        if now - t < 60
    ]
    
    if len(rate_limit_store[client_ip]) >= 100:  # 100 requests per minute
        raise HTTPException(429, "Rate limit exceeded")
    
    rate_limit_store[client_ip].append(now)

# 2. Request Logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s"
    )
    
    return response

# 3. Error Handling
@app.exception_handler(httpx.RequestError)
async def handle_service_error(request: Request, exc: httpx.RequestError):
    return JSONResponse(
        status_code=503,
        content={"error": "Service temporarily unavailable"}
    )

# 4. Response Aggregation
@app.get("/dashboard")
async def get_dashboard(user_id: int):
    """Aggregate data from multiple services"""
    async with httpx.AsyncClient() as client:
        # Parallel requests
        user_task = client.get(f"http://user-service:8001/users/{user_id}")
        orders_task = client.get(f"http://order-service:8003/orders?user_id={user_id}")
        stats_task = client.get(f"http://analytics-service:8004/stats/{user_id}")
        
        user_resp, orders_resp, stats_resp = await asyncio.gather(
            user_task, orders_task, stats_task
        )
        
        return {
            "user": user_resp.json(),
            "recent_orders": orders_resp.json(),
            "statistics": stats_resp.json()
        }
```

---

## 4. Service Discovery

### What is Service Discovery?

Mechanism for services to find and communicate with each other dynamically.

### Simple Service Registry

```python
# registry.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List
import time

app = FastAPI(title="Service Registry")

class ServiceInfo(BaseModel):
    name: str
    host: str
    port: int
    health_check_url: str

# In-memory registry
services: Dict[str, List[ServiceInfo]] = {}

@app.post("/register")
async def register_service(service: ServiceInfo):
    """Register a service"""
    if service.name not in services:
        services[service.name] = []
    
    # Add or update service
    services[service.name] = [
        s for s in services[service.name] 
        if s.host != service.host or s.port != service.port
    ]
    services[service.name].append(service)
    
    return {"status": "registered"}

@app.get("/discover/{service_name}")
async def discover_service(service_name: str):
    """Discover service instances"""
    if service_name not in services:
        raise HTTPException(404, f"Service {service_name} not found")
    
    return {"instances": services[service_name]}

@app.delete("/deregister/{service_name}")
async def deregister_service(service_name: str, host: str, port: int):
    """Deregister a service instance"""
    if service_name in services:
        services[service_name] = [
            s for s in services[service_name]
            if s.host != host or s.port != port
        ]
    return {"status": "deregistered"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": list(services.keys())}
```

### Service Registration (Client Side)

```python
# service.py
from fastapi import FastAPI
import httpx
import asyncio

app = FastAPI()

REGISTRY_URL = "http://registry:8000"
SERVICE_NAME = "user-service"
SERVICE_HOST = "user-service"
SERVICE_PORT = 8001

async def register_with_registry():
    """Register this service with the registry"""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{REGISTRY_URL}/register",
            json={
                "name": SERVICE_NAME,
                "host": SERVICE_HOST,
                "port": SERVICE_PORT,
                "health_check_url": f"http://{SERVICE_HOST}:{SERVICE_PORT}/health"
            }
        )

@app.on_event("startup")
async def startup_event():
    """Register on startup"""
    await register_with_registry()
    # Start heartbeat
    asyncio.create_task(send_heartbeat())

async def send_heartbeat():
    """Send periodic heartbeat"""
    while True:
        await asyncio.sleep(30)  # Every 30 seconds
        try:
            await register_with_registry()
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Deregister on shutdown"""
    async with httpx.AsyncClient() as client:
        await client.delete(
            f"{REGISTRY_URL}/deregister/{SERVICE_NAME}",
            params={"host": SERVICE_HOST, "port": SERVICE_PORT}
        )
```

### Service Discovery (Client Side)

```python
# client.py
import httpx
import random
from typing import Optional

class ServiceClient:
    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self.cache = {}
    
    async def get_service_url(self, service_name: str) -> str:
        """Get URL for a service (with load balancing)"""
        # Discover service instances
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.registry_url}/discover/{service_name}"
            )
            instances = response.json()["instances"]
        
        if not instances:
            raise Exception(f"No instances found for {service_name}")
        
        # Simple random load balancing
        instance = random.choice(instances)
        return f"http://{instance['host']}:{instance['port']}"
    
    async def call_service(
        self, 
        service_name: str, 
        path: str, 
        method: str = "GET",
        **kwargs
    ):
        """Make request to a service"""
        service_url = await self.get_service_url(service_name)
        url = f"{service_url}{path}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

# Usage
client = ServiceClient("http://registry:8000")

# Call user service
user = await client.call_service("user-service", "/users/123")

# Call order service
orders = await client.call_service("order-service", "/orders", method="GET")
```

---

## 5. Distributed Tracing

### What is Distributed Tracing?

Track requests as they flow through multiple services to understand latency and dependencies.

### OpenTelemetry with FastAPI

```python
# tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

def setup_tracing(service_name: str):
    """Configure OpenTelemetry tracing"""
    # Create tracer provider
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })
    
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    
    # Add span processor
    tracer_provider.add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    return tracer_provider

# user_service.py
from fastapi import FastAPI
from tracing import setup_tracing

app = FastAPI()

# Setup tracing
setup_tracing("user-service")
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user - automatically traced"""
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("database_query"):
        # Database query
        user = await db.get_user(user_id)
    
    with tracer.start_as_current_span("cache_check"):
        # Cache operation
        await cache.set(f"user:{user_id}", user)
    
    return user
```

### Manual Span Creation

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.post("/orders")
async def create_order(order: OrderCreate):
    with tracer.start_as_current_span("create_order") as span:
        # Add attributes to span
        span.set_attribute("order.user_id", order.user_id)
        span.set_attribute("order.item_count", len(order.items))
        
        # Validate order
        with tracer.start_as_current_span("validate_order"):
            await validate_order(order)
        
        # Save to database
        with tracer.start_as_current_span("save_to_db"):
            order_id = await db.save_order(order)
        
        # Publish event
        with tracer.start_as_current_span("publish_event"):
            await event_bus.publish("order.created", {"order_id": order_id})
        
        span.set_attribute("order.id", order_id)
        return {"order_id": order_id}
```

### Cross-Service Tracing

```python
# Service A calls Service B with trace context
import httpx
from opentelemetry.propagate import inject

async def call_service_b():
    headers = {}
    # Inject trace context into headers
    inject(headers)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://service-b/api/endpoint",
            headers=headers
        )
        return response.json()

# Service B extracts trace context
from opentelemetry.propagate import extract

@app.get("/api/endpoint")
async def endpoint(request: Request):
    # Extract trace context from headers
    context = extract(dict(request.headers))
    
    # Continue trace
    with tracer.start_as_current_span("service_b_work", context=context):
        result = await do_work()
        return result
```

---

## 6. Centralized Logging

### Structured Logging with structlog

```python
# logging_config.py
import structlog
import logging

def setup_logging(service_name: str):
    """Configure structured logging"""
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Add service name to all logs
    structlog.contextvars.bind_contextvars(service=service_name)

# Usage in service
from logging_config import setup_logging
import structlog

setup_logging("user-service")
logger = structlog.get_logger()

@app.post("/users")
async def create_user(user: UserCreate):
    logger.info(
        "creating_user",
        email=user.email,
        user_type=user.user_type
    )
    
    try:
        user_id = await db.create_user(user)
        logger.info("user_created", user_id=user_id)
        return {"user_id": user_id}
    except Exception as e:
        logger.error(
            "user_creation_failed",
            email=user.email,
            error=str(e),
            exc_info=True
        )
        raise
```

### Request Correlation IDs

```python
from fastapi import FastAPI, Request
import uuid
import structlog

app = FastAPI()

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to each request"""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    
    # Bind to context
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    # Add to response
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response

# All logs will include correlation_id
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info("fetching_user", user_id=user_id)
    # Log includes correlation_id automatically
    return await db.get_user(user_id)
```

### Forwarding Correlation IDs

```python
async def call_another_service(correlation_id: str):
    """Forward correlation ID to downstream services"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://order-service/orders",
            headers={"X-Correlation-ID": correlation_id}
        )
        return response.json()
```

---

## 7. Circuit Breaker Pattern

### What is Circuit Breaker?

Prevent cascading failures by stopping requests to failing services temporarily.

```
States:
CLOSED → Normal operation (all requests go through)
   ↓ (too many failures)
OPEN → Block all requests (fail fast)
   ↓ (after timeout)
HALF-OPEN → Try a few requests
   ↓ (if successful)
CLOSED → Resume normal operation
```

### Circuit Breaker Implementation

```python
# circuit_breaker.py
import time
from enum import Enum
from typing import Callable, Any
import asyncio

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Exception = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Async version"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )

# Usage
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

async def call_external_service():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://external-service/api")
        return response.json()

# Protected call
try:
    result = await breaker.call_async(call_external_service)
except Exception as e:
    logger.error("Service call failed", error=str(e))
    # Return fallback response
    result = {"status": "unavailable"}
```

### Circuit Breaker Decorator

```python
def circuit_breaker(failure_threshold=5, recovery_timeout=60):
    """Decorator for circuit breaker"""
    breaker = CircuitBreaker(failure_threshold, recovery_timeout)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call_async(func, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@circuit_breaker(failure_threshold=3, recovery_timeout=30)
async def get_user_from_service(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://user-service/users/{user_id}")
        response.raise_for_status()
        return response.json()

# With fallback
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        return await get_user_from_service(user_id)
    except Exception:
        # Fallback to cache or default
        cached = await cache.get(f"user:{user_id}")
        if cached:
            return cached
        return {"id": user_id, "status": "unavailable"}
```

---

## 8. Complete Microservices Example

### System Architecture

```
┌──────────────┐
│  API Gateway │ :8000
└──────┬───────┘
       │
       ├───→ User Service :8001 → PostgreSQL
       │
       ├───→ Product Service :8002 → PostgreSQL
       │
       ├───→ Order Service :8003 → PostgreSQL
       │         │
       │         └───→ Kafka → Payment Service :8004
       │
       └───→ Notification Service :8005
                    ↑
                    └──── Kafka
```

### Project Structure

```
microservices/
├── gateway/
│   ├── main.py
│   ├── routes.py
│   └── middleware.py
├── user-service/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── service.py
│   └── database.py
├── product-service/
│   ├── main.py
│   ├── models.py
│   └── ...
├── order-service/
│   ├── main.py
│   ├── models.py
│   └── ...
├── payment-service/
│   ├── main.py
│   └── ...
├── notification-service/
│   ├── main.py
│   └── ...
├── shared/
│   ├── auth.py
│   ├── logging.py
│   ├── tracing.py
│   └── events.py
└── docker-compose.yml
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  # API Gateway
  gateway:
    build: ./gateway
    ports:
      - "8000:8000"
    depends_on:
      - user-service
      - product-service
      - order-service
    environment:
      - USER_SERVICE_URL=http://user-service:8001
      - PRODUCT_SERVICE_URL=http://product-service:8002
      - ORDER_SERVICE_URL=http://order-service:8003
  
  # User Service
  user-service:
    build: ./user-service
    ports:
      - "8001:8001"
    depends_on:
      - postgres-user
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres-user:5432/users
      - REDIS_URL=redis://redis:6379
  
  # Product Service
  product-service:
    build: ./product-service
    ports:
      - "8002:8002"
    depends_on:
      - postgres-product
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres-product:5432/products
  
  # Order Service
  order-service:
    build: ./order-service
    ports:
      - "8003:8003"
    depends_on:
      - postgres-order
      - kafka
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres-order:5432/orders
      - KAFKA_URL=kafka:9092
  
  # Payment Service
  payment-service:
    build: ./payment-service
    ports:
      - "8004:8004"
    depends_on:
      - kafka
    environment:
      - KAFKA_URL=kafka:9092
  
  # Notification Service
  notification-service:
    build: ./notification-service
    depends_on:
      - kafka
    environment:
      - KAFKA_URL=kafka:9092
  
  # Databases
  postgres-user:
    image: postgres:15
    environment:
      - POSTGRES_DB=users
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
  
  postgres-product:
    image: postgres:15
    environment:
      - POSTGRES_DB=products
  
  postgres-order:
    image: postgres:15
    environment:
      - POSTGRES_DB=orders
  
  # Redis
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  # Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      - ZOOKEEPER_CLIENT_PORT=2181
  
  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    environment:
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
  
  # Monitoring
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "6831:6831/udp"  # Agent
```

*Continued in next response...*

---

## Exercises

### Level 1: Basic

1. **Simple Microservices**
   - Create User and Product services
   - Implement basic CRUD
   - Test independently

2. **API Gateway**
   - Create gateway to route requests
   - Forward to services
   - Add logging

3. **Service Discovery**
   - Implement basic registry
   - Register services on startup
   - Discover services

### Level 2: Intermediate

4. **Distributed Tracing**
   - Add OpenTelemetry
   - Trace requests across services
   - View in Jaeger

5. **Circuit Breaker**
   - Implement circuit breaker
   - Test with failing service
   - Add fallbacks

6. **Event-Driven**
   - Order service publishes events
   - Payment service consumes
   - Handle failures

### Level 3: Challenging

7. **Complete System**
   - Build e-commerce microservices
   - All patterns implemented
   - Full observability

---

## Key Takeaways

✅ **Microservices**:
- Independent services
- Own database per service
- Communicate via APIs
- Independent deployment

✅ **Patterns**:
- API Gateway for routing
- Service Discovery
- Circuit Breaker for resilience
- Event-driven for async

✅ **Observability**:
- Distributed tracing
- Centralized logging
- Correlation IDs
- Monitoring

---

Continue to [Part-18-Service-Communication](../Part-18-Service-Communication/README.md)!
