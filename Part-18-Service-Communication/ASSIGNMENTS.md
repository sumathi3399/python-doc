# Part 18: Service Communication - Practice Problems

> Test REST, messaging, gRPC

---

## Problem 1: REST Call with Retry

**Task**: HTTP with retry logic
```python
import httpx
import time

async def call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5)
                return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

**Time**: 20 minutes

---

## Problem 2: Message Queue Producer

**Task**: Publish message to RabbitMQ
```python
# Using pika library
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='tasks')
channel.basic_publish(exchange='', routing_key='tasks', body='Task data')

connection.close()
```

**Time**: 15 minutes

---

## Problem 3: Message Queue Consumer

**Task**: Consume messages
```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='tasks')

def callback(ch, method, properties, body):
    print(f"Received: {body}")

channel.basic_consume(queue='tasks', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
```

**Time**: 15 minutes

---

## Problem 4: Event-Driven Pattern

**Task**: Publish domain event
```python
import json

class EventPublisher:
    def __init__(self, channel):
        self.channel = channel
    
    def publish(self, event_type, data):
        event = {
            "type": event_type,
            "data": data,
            "timestamp": "2024-01-01T00:00:00"
        }
        self.channel.basic_publish(
            exchange='events',
            routing_key=event_type,
            body=json.dumps(event)
        )

# Usage
publisher.publish("user.created", {"user_id": 1, "name": "Alice"})
```

**Time**: 20 minutes

---

## Problem 5: Idempotent Message Handler

**Task**: Process message once
```python
import redis

r = redis.Redis()

def process_message(message_id, data):
    # Check if already processed
    if r.exists(f"processed:{message_id}"):
        print("Already processed")
        return
    
    # Process message
    print(f"Processing {data}")
    
    # Mark as processed
    r.setex(f"processed:{message_id}", 86400, "1")
```

**Time**: 20 minutes

---

## Problem 6: Correlation ID in Events

**Task**: Track request across events
```python
import uuid

def create_event(event_type, data, correlation_id=None):
    return {
        "event_id": str(uuid.uuid4()),
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "type": event_type,
        "data": data
    }

event = create_event("order.created", {"order_id": 123}, "corr-123")
```

**Time**: 15 minutes

---

## Problem 7: gRPC Service Definition

**Task**: Create proto file
```protobuf
syntax = "proto3";

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
}

message UserRequest {
  int32 user_id = 1;
}

message UserResponse {
  int32 user_id = 1;
  string name = 2;
}
```

**Time**: 15 minutes

---

## Problem 8: REST vs Messaging Decision

**Task**: Choose correct pattern
```
Choose REST or Messaging:

1. Get user details immediately: ________
2. Send email notification: ________
3. Order payment processing: ________
4. Real-time chat message: ________
5. Product catalog query: ________

Answers: 1=REST, 2=Messaging, 3=Messaging, 4=Messaging, 5=REST
```

**Time**: 10 minutes

---

## Problem 9: Saga Pattern (Order)

**Task**: Compensating transactions
```python
class OrderSaga:
    def __init__(self):
        self.steps = []
    
    async def execute(self, order):
        try:
            # Step 1: Reserve inventory
            await self.reserve_inventory(order)
            self.steps.append(('inventory', order.id))
            
            # Step 2: Process payment
            await self.process_payment(order)
            self.steps.append(('payment', order.id))
            
            return "SUCCESS"
        except Exception as e:
            # Compensate in reverse order
            await self.compensate()
            return "FAILED"
    
    async def compensate(self):
        for step, order_id in reversed(self.steps):
            if step == 'inventory':
                await self.release_inventory(order_id)
            elif step == 'payment':
                await self.refund_payment(order_id)
```

**Time**: 30 minutes

---

## Problem 10: Dead Letter Queue

**Task**: Handle failed messages
```python
def process_with_dlq(message, max_retries=3):
    retry_count = message.get('retry_count', 0)
    
    try:
        # Process message
        process(message['data'])
    except Exception as e:
        if retry_count < max_retries:
            # Retry
            message['retry_count'] = retry_count + 1
            republish(message)
        else:
            # Send to DLQ
            send_to_dlq(message)
```

**Time**: 20 minutes

---

## Summary Check

**7+ solved** → Communication patterns mastered  
**4-6 solved** → Practice async messaging  
**< 4 solved** → Review REST vs messaging
