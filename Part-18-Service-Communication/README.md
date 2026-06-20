# Part 18: Service-to-Service Communication

> Master patterns for inter-service communication in distributed systems using REST, messaging, and events.

## 📚 Table of Contents

1. [Communication Patterns Overview](#1-communication-patterns-overview)
2. [Synchronous Communication (REST)](#2-synchronous-communication-rest)
3. [Asynchronous Communication (Messaging)](#3-asynchronous-communication-messaging)
4. [Event-Driven Architecture](#4-event-driven-architecture)
5. [Kafka Integration](#5-kafka-integration)
6. [RabbitMQ Integration](#6-rabbitmq-integration)
7. [gRPC Communication](#7-grpc-communication)
8. [Best Practices](#8-best-practices)
9. [Exercises](#exercises)

---

## 1. Communication Patterns Overview

### Synchronous vs Asynchronous

```
SYNCHRONOUS (Request-Response):
Service A → [HTTP Request] → Service B
Service A ← [HTTP Response] ← Service B
(Service A waits for response)

ASYNCHRONOUS (Message-Based):
Service A → [Message] → Queue → Service B
Service A continues immediately
Service B processes when ready
```

### When to Use Each

| Pattern | Use When | Example |
|---------|----------|---------|
| **Synchronous REST** | Immediate response needed | Get user profile |
| **Asynchronous Messages** | Fire-and-forget | Send email notification |
| **Events** | Multiple consumers | Order created event |
| **RPC (gRPC)** | High performance needed | Internal microservices |

---

## 2. Synchronous Communication (REST)

### Basic HTTP Client with httpx

```python
# service_client.py
import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException

class ServiceClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
    
    async def get(self, path: str, **kwargs) -> Dict[Any, Any]:
        """GET request"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}", **kwargs)
            response.raise_for_status()
            return response.json()
    
    async def post(self, path: str, json: Dict = None, **kwargs) -> Dict[Any, Any]:
        """POST request"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{path}", 
                json=json, 
                **kwargs
            )
            response.raise_for_status()
            return response.json()

# Usage in Order Service
user_client = ServiceClient("http://user-service:8001")
product_client = ServiceClient("http://product-service:8002")

@app.post("/orders")
async def create_order(order: OrderCreate):
    # Validate user exists
    try:
        user = await user_client.get(f"/users/{order.user_id}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(404, "User not found")
    
    # Validate products exist
    for item in order.items:
        try:
            product = await product_client.get(f"/products/{item.product_id}")
            if product["stock"] < item.quantity:
                raise HTTPException(400, f"Insufficient stock for {product['name']}")
        except httpx.HTTPStatusError:
            raise HTTPException(404, f"Product {item.product_id} not found")
    
    # Create order
    order_id = await db.create_order(order)
    return {"order_id": order_id}
```

### Retry Logic with Exponential Backoff

```python
import httpx
import asyncio
from typing import Callable, Any
import random

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    *args,
    **kwargs
) -> Any:
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            if attempt == max_retries - 1:
                raise
            
            # Calculate delay with jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            total_delay = delay + jitter
            
            logger.warning(
                f"Request failed (attempt {attempt + 1}/{max_retries}): {e}. "
                f"Retrying in {total_delay:.2f}s..."
            )
            await asyncio.sleep(total_delay)

# Usage
async def fetch_user(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://user-service/users/{user_id}")
        response.raise_for_status()
        return response.json()

# With retry
user = await retry_with_backoff(fetch_user, user_id=123, max_retries=3)
```

### Timeout and Error Handling

```python
from fastapi import FastAPI, HTTPException
import httpx
import asyncio

app = FastAPI()

class ServiceTimeoutError(Exception):
    pass

async def call_service_with_timeout(
    url: str,
    timeout: float = 5.0,
    fallback = None
):
    """Call service with timeout and fallback"""
    try:
        async with httpx.AsyncClient() as client:
            response = await asyncio.wait_for(
                client.get(url),
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
    
    except asyncio.TimeoutError:
        logger.error(f"Service timeout: {url}")
        if fallback is not None:
            return fallback
        raise ServiceTimeoutError(f"Service timeout after {timeout}s")
    
    except httpx.HTTPStatusError as e:
        logger.error(f"Service error: {url}, status: {e.response.status_code}")
        if fallback is not None:
            return fallback
        raise
    
    except httpx.RequestError as e:
        logger.error(f"Service unavailable: {url}, error: {e}")
        if fallback is not None:
            return fallback
        raise

@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: int):
    """Get dashboard with fallbacks"""
    
    # Critical data - no fallback
    user = await call_service_with_timeout(
        f"http://user-service/users/{user_id}",
        timeout=5.0
    )
    
    # Non-critical data - with fallback
    recommendations = await call_service_with_timeout(
        f"http://recommendation-service/recommendations/{user_id}",
        timeout=2.0,
        fallback=[]  # Empty list if service fails
    )
    
    return {
        "user": user,
        "recommendations": recommendations
    }
```

### Parallel Service Calls

```python
import asyncio
import httpx

async def get_order_details(order_id: int):
    """Fetch order details from multiple services in parallel"""
    
    async with httpx.AsyncClient() as client:
        # Parallel requests
        order_task = client.get(f"http://order-service/orders/{order_id}")
        user_task = client.get(f"http://user-service/users/{order.user_id}")
        products_task = client.get(f"http://product-service/products")
        
        # Wait for all to complete
        order_resp, user_resp, products_resp = await asyncio.gather(
            order_task,
            user_task,
            products_task,
            return_exceptions=True  # Don't fail if one fails
        )
        
        # Handle responses
        order = order_resp.json() if not isinstance(order_resp, Exception) else None
        user = user_resp.json() if not isinstance(user_resp, Exception) else None
        products = products_resp.json() if not isinstance(products_resp, Exception) else []
        
        return {
            "order": order,
            "user": user,
            "products": products
        }
```

---

## 3. Asynchronous Communication (Messaging)

### Message Queue Benefits

- **Decoupling**: Services don't need to know about each other
- **Reliability**: Messages persisted until processed
- **Load Leveling**: Consumers process at their own pace
- **Scalability**: Multiple consumers can process in parallel

### Message Patterns

```python
# 1. Point-to-Point (Queue)
"""
Producer → Queue → Single Consumer
"""

# 2. Publish-Subscribe (Topic)
"""
Producer → Topic → Consumer 1
                → Consumer 2
                → Consumer 3
"""

# 3. Request-Reply
"""
Service A → Request Queue → Service B
Service A ← Reply Queue ← Service B
"""
```

---

## 4. Event-Driven Architecture

### Event Types

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Dict

class Event(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    service: str
    data: Dict[str, Any]

# Domain Events
class OrderCreatedEvent(BaseModel):
    order_id: int
    user_id: int
    total_amount: float
    items: list

class PaymentCompletedEvent(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    status: str

class InventoryUpdatedEvent(BaseModel):
    product_id: int
    quantity_change: int
    new_stock: int
```

### Event Publisher

```python
# event_publisher.py
import json
from typing import Any, Dict
from datetime import datetime
import uuid

class EventPublisher:
    def __init__(self, kafka_producer):
        self.producer = kafka_producer
    
    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        topic: str = "events"
    ):
        """Publish an event"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "order-service",
            "data": data
        }
        
        # Serialize and send
        message = json.dumps(event)
        await self.producer.send(topic, message.encode())
        
        logger.info(f"Published event: {event_type}", event_id=event["event_id"])

# Usage in Order Service
@app.post("/orders")
async def create_order(order: OrderCreate):
    # Save order
    order_id = await db.create_order(order)
    
    # Publish event
    await event_publisher.publish(
        event_type="order.created",
        data={
            "order_id": order_id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "items": [item.dict() for item in order.items]
        }
    )
    
    return {"order_id": order_id}
```

### Event Consumer

```python
# event_consumer.py
import json
from typing import Callable, Dict

class EventConsumer:
    def __init__(self, kafka_consumer):
        self.consumer = kafka_consumer
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register handler for event type"""
        self.handlers[event_type] = handler
    
    async def start(self):
        """Start consuming events"""
        async for message in self.consumer:
            try:
                # Parse event
                event = json.loads(message.value.decode())
                event_type = event["event_type"]
                
                # Find and call handler
                if event_type in self.handlers:
                    await self.handlers[event_type](event)
                else:
                    logger.warning(f"No handler for event type: {event_type}")
            
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)

# Usage in Payment Service
consumer = EventConsumer(kafka_consumer)

@consumer.register_handler("order.created")
async def handle_order_created(event):
    """Process payment when order is created"""
    order_id = event["data"]["order_id"]
    amount = event["data"]["total_amount"]
    
    logger.info(f"Processing payment for order {order_id}")
    
    # Process payment
    payment_id = await payment_service.process(order_id, amount)
    
    # Publish payment completed event
    await event_publisher.publish(
        event_type="payment.completed",
        data={
            "payment_id": payment_id,
            "order_id": order_id,
            "amount": amount,
            "status": "completed"
        }
    )

# Start consumer
asyncio.create_task(consumer.start())
```

### Saga Pattern (Distributed Transactions)

```python
# Choreography-based Saga
"""
1. Order Service → order.created
2. Payment Service → payment.completed OR payment.failed
3. Inventory Service → inventory.reserved OR inventory.reservation.failed
4. Shipping Service → shipping.scheduled

If any fails → Compensating actions
"""

# Order Service
@app.post("/orders")
async def create_order(order: OrderCreate):
    order_id = await db.create_order(order, status="pending")
    
    # Start saga
    await event_publisher.publish("order.created", {
        "order_id": order_id,
        "user_id": order.user_id,
        "items": [item.dict() for item in order.items]
    })
    
    return {"order_id": order_id, "status": "pending"}

# Payment Service - Success
@consumer.register_handler("order.created")
async def process_payment(event):
    order_id = event["data"]["order_id"]
    
    try:
        payment_id = await payment_service.charge(order_id)
        await event_publisher.publish("payment.completed", {
            "order_id": order_id,
            "payment_id": payment_id
        })
    except PaymentError:
        await event_publisher.publish("payment.failed", {
            "order_id": order_id,
            "reason": "insufficient_funds"
        })

# Order Service - Handle payment failure (Compensation)
@consumer.register_handler("payment.failed")
async def handle_payment_failure(event):
    order_id = event["data"]["order_id"]
    
    # Cancel order
    await db.update_order(order_id, status="cancelled")
    
    # Notify user
    await event_publisher.publish("order.cancelled", {
        "order_id": order_id,
        "reason": "payment_failed"
    })
```

---

## 5. Kafka Integration

### Kafka Producer

```python
# kafka_producer.py
from aiokafka import AIOKafkaProducer
import json

class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
    
    async def start(self):
        """Start producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()
    
    async def stop(self):
        """Stop producer"""
        if self.producer:
            await self.producer.stop()
    
    async def send(self, topic: str, value: dict, key: str = None):
        """Send message to topic"""
        if key:
            key = key.encode()
        
        await self.producer.send(topic, value=value, key=key)
        logger.info(f"Sent message to {topic}")

# FastAPI integration
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await kafka_producer.start()
    yield
    # Shutdown
    await kafka_producer.stop()

app = FastAPI(lifespan=lifespan)

kafka_producer = KafkaProducer("kafka:9092")

@app.post("/orders")
async def create_order(order: OrderCreate):
    order_id = await db.create_order(order)
    
    # Send to Kafka
    await kafka_producer.send(
        topic="orders",
        value={
            "order_id": order_id,
            "user_id": order.user_id,
            "amount": order.total_amount
        },
        key=str(order_id)  # Partition by order_id
    )
    
    return {"order_id": order_id}
```

### Kafka Consumer

```python
# kafka_consumer.py
from aiokafka import AIOKafkaConsumer
import json
import asyncio

class KafkaConsumer:
    def __init__(
        self,
        topic: str,
        bootstrap_servers: str,
        group_id: str
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = None
    
    async def start(self):
        """Start consumer"""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode())
        )
        await self.consumer.start()
    
    async def stop(self):
        """Stop consumer"""
        if self.consumer:
            await self.consumer.stop()
    
    async def consume(self, handler):
        """Consume messages and process with handler"""
        try:
            async for message in self.consumer:
                try:
                    logger.info(
                        f"Received message from {message.topic}",
                        partition=message.partition,
                        offset=message.offset
                    )
                    
                    await handler(message.value)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    # Could send to dead letter queue here
        
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)

# Payment Service consumer
async def handle_order_message(message):
    """Process order for payment"""
    order_id = message["order_id"]
    amount = message["amount"]
    
    # Process payment
    payment_result = await process_payment(order_id, amount)
    
    # Send result
    await kafka_producer.send(
        topic="payments",
        value={
            "order_id": order_id,
            "payment_id": payment_result.id,
            "status": payment_result.status
        }
    )

# Start consumer in background
@app.on_event("startup")
async def startup():
    consumer = KafkaConsumer(
        topic="orders",
        bootstrap_servers="kafka:9092",
        group_id="payment-service"
    )
    await consumer.start()
    asyncio.create_task(consumer.consume(handle_order_message))
```

### Consumer Groups and Partitioning

```python
"""
Topic: orders (3 partitions)

Consumer Group: payment-processors
├── Consumer 1 → Partition 0
├── Consumer 2 → Partition 1
└── Consumer 3 → Partition 2

Each partition processed by only one consumer in group
Messages with same key go to same partition
"""

# Producer - Partition by user_id
await kafka_producer.send(
    topic="orders",
    value=order_data,
    key=str(order.user_id)  # All orders from same user go to same partition
)

# Multiple consumers in same group
# Scale by adding more consumers (up to number of partitions)
consumer1 = KafkaConsumer("orders", "kafka:9092", "payment-group")
consumer2 = KafkaConsumer("orders", "kafka:9092", "payment-group")
consumer3 = KafkaConsumer("orders", "kafka:9092", "payment-group")
```

---

## 6. RabbitMQ Integration

### RabbitMQ Producer

```python
# rabbitmq_producer.py
import aio_pika
import json

class RabbitMQProducer:
    def __init__(self, url: str):
        self.url = url
        self.connection = None
        self.channel = None
    
    async def start(self):
        """Connect to RabbitMQ"""
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
    
    async def stop(self):
        """Close connection"""
        if self.connection:
            await self.connection.close()
    
    async def publish(
        self,
        exchange: str,
        routing_key: str,
        message: dict
    ):
        """Publish message to exchange"""
        # Declare exchange
        exchange_obj = await self.channel.declare_exchange(
            exchange,
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        # Publish message
        await exchange_obj.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=routing_key
        )
        
        logger.info(f"Published to {exchange}/{routing_key}")

# Usage
producer = RabbitMQProducer("amqp://guest:guest@rabbitmq:5672/")

@app.post("/orders")
async def create_order(order: OrderCreate):
    order_id = await db.create_order(order)
    
    # Publish to RabbitMQ
    await producer.publish(
        exchange="orders",
        routing_key="order.created",
        message={
            "order_id": order_id,
            "user_id": order.user_id,
            "amount": order.total_amount
        }
    )
    
    return {"order_id": order_id}
```

### RabbitMQ Consumer

```python
# rabbitmq_consumer.py
import aio_pika
import json

class RabbitMQConsumer:
    def __init__(self, url: str, exchange: str, queue_name: str):
        self.url = url
        self.exchange_name = exchange
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
    
    async def start(self, routing_keys: list, handler):
        """Start consuming messages"""
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        
        # Declare exchange
        exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        # Declare queue
        queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True
        )
        
        # Bind queue to exchange with routing keys
        for routing_key in routing_keys:
            await queue.bind(exchange, routing_key=routing_key)
        
        # Start consuming
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body.decode())
                        await handler(data, message.routing_key)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")

# Usage in Payment Service
consumer = RabbitMQConsumer(
    url="amqp://guest:guest@rabbitmq:5672/",
    exchange="orders",
    queue_name="payment-queue"
)

async def handle_message(data, routing_key):
    if routing_key == "order.created":
        await process_payment(data["order_id"], data["amount"])
    elif routing_key == "order.cancelled":
        await refund_payment(data["order_id"])

@app.on_event("startup")
async def startup():
    asyncio.create_task(
        consumer.start(
            routing_keys=["order.created", "order.cancelled"],
            handler=handle_message
        )
    )
```

---

## 7. gRPC Communication

### gRPC Benefits

- **Performance**: Binary protocol, smaller payloads
- **Type Safety**: Strongly typed contracts
- **Streaming**: Bi-directional streaming
- **Language Agnostic**: Works across languages

### Protocol Buffer Definition

```protobuf
// user.proto
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc CreateUser (CreateUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User);
}

message User {
  int32 id = 1;
  string email = 2;
  string name = 3;
  int32 age = 4;
}

message GetUserRequest {
  int32 id = 1;
}

message CreateUserRequest {
  string email = 1;
  string name = 2;
  int32 age = 3;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
}
```

### gRPC Server (Python)

```python
# user_service_grpc.py
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserServicer(user_pb2_grpc.UserServiceServicer):
    async def GetUser(self, request, context):
        """Get user by ID"""
        user = await db.get_user(request.id)
        
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return user_pb2.User()
        
        return user_pb2.User(
            id=user.id,
            email=user.email,
            name=user.name,
            age=user.age
        )
    
    async def CreateUser(self, request, context):
        """Create new user"""
        user_id = await db.create_user(
            email=request.email,
            name=request.name,
            age=request.age
        )
        
        return user_pb2.User(
            id=user_id,
            email=request.email,
            name=request.name,
            age=request.age
        )
    
    async def ListUsers(self, request, context):
        """Stream users"""
        users = await db.list_users(
            page=request.page,
            page_size=request.page_size
        )
        
        for user in users:
            yield user_pb2.User(
                id=user.id,
                email=user.email,
                name=user.name,
                age=user.age
            )

# Start gRPC server
async def serve():
    server = grpc.aio.server()
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()
```

### gRPC Client

```python
# user_client.py
import grpc
import user_pb2
import user_pb2_grpc

class UserClient:
    def __init__(self, host: str = 'localhost:50051'):
        self.channel = grpc.aio.insecure_channel(host)
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)
    
    async def get_user(self, user_id: int):
        """Get user"""
        request = user_pb2.GetUserRequest(id=user_id)
        response = await self.stub.GetUser(request)
        return response
    
    async def create_user(self, email: str, name: str, age: int):
        """Create user"""
        request = user_pb2.CreateUserRequest(
            email=email,
            name=name,
            age=age
        )
        response = await self.stub.CreateUser(request)
        return response
    
    async def list_users(self, page: int = 1, page_size: int = 10):
        """List users (streaming)"""
        request = user_pb2.ListUsersRequest(
            page=page,
            page_size=page_size
        )
        
        users = []
        async for user in self.stub.ListUsers(request):
            users.append(user)
        
        return users

# Usage in Order Service
user_client = UserClient('user-service:50051')

@app.post("/orders")
async def create_order(order: OrderCreate):
    # Validate user via gRPC
    try:
        user = await user_client.get_user(order.user_id)
    except grpc.RpcError as e:
        raise HTTPException(404, "User not found")
    
    # Create order
    order_id = await db.create_order(order)
    return {"order_id": order_id}
```

---

## 8. Best Practices

### 1. Idempotency

```python
# Ensure operations can be retried safely
@app.post("/orders")
async def create_order(order: OrderCreate, idempotency_key: str):
    # Check if already processed
    existing = await db.get_order_by_idempotency_key(idempotency_key)
    if existing:
        return {"order_id": existing.id, "status": "already_processed"}
    
    # Process order
    order_id = await db.create_order(order, idempotency_key=idempotency_key)
    return {"order_id": order_id}
```

### 2. Correlation IDs

```python
# Track requests across services
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    
    # Add to context
    request.state.correlation_id = correlation_id
    
    # Forward to downstream services
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response

# When calling other services
async def call_service(url: str, correlation_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"X-Correlation-ID": correlation_id}
        )
        return response.json()
```

### 3. Timeouts

```python
# Always set timeouts
async with httpx.AsyncClient(timeout=5.0) as client:
    response = await client.get(url)

# Different timeouts for different operations
timeouts = httpx.Timeout(
    connect=2.0,  # Connection timeout
    read=5.0,     # Read timeout
    write=5.0,    # Write timeout
    pool=10.0     # Pool timeout
)
```

### 4. Circuit Breaker

```python
# Use circuit breaker for external calls
@circuit_breaker(failure_threshold=5, recovery_timeout=60)
async def call_external_service():
    # ...
```

### 5. Dead Letter Queue

```python
# Handle failed messages
async def process_message(message):
    try:
        await handle_message(message)
    except Exception as e:
        # Send to DLQ after max retries
        if message.retry_count >= MAX_RETRIES:
            await dlq.send(message)
        else:
            # Retry
            message.retry_count += 1
            await queue.send(message)
```

---

## Exercises

### Level 1: Basic

1. **REST Communication**
   - Call one service from another
   - Handle errors
   - Add retry logic

2. **Kafka Producer**
   - Publish messages
   - Use partitioning
   - Test delivery

3. **Kafka Consumer**
   - Consume messages
   - Process events
   - Handle errors

### Level 2: Intermediate

4. **Event-Driven Flow**
   - Order creates payment request
   - Payment publishes result
   - Update order status

5. **gRPC Service**
   - Define proto
   - Implement server
   - Create client

6. **Saga Pattern**
   - Implement distributed transaction
   - Handle compensation
   - Test failure scenarios

### Level 3: Challenging

7. **Complete Communication**
   - Mix of REST and messaging
   - Circuit breakers
   - Distributed tracing
   - Full error handling

---

## Key Takeaways

✅ **Patterns**:
- Synchronous for immediate response
- Asynchronous for fire-and-forget
- Events for multiple consumers

✅ **Tools**:
- httpx for REST calls
- Kafka for event streaming
- RabbitMQ for message queuing
- gRPC for performance

✅ **Best Practices**:
- Idempotency for retries
- Correlation IDs for tracing
- Timeouts always
- Circuit breakers for resilience
- Dead letter queues for failures

---

Continue to [Part-19-Testing](../Part-19-Testing/README.md)!
