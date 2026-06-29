# Part 18: Service-to-Service Communication - Assignments

## Assignment Guidelines

- **Estimated time:** 18-24 hours total
- **Prerequisites:** Parts 1-17 complete
- **Submission:** Multi-protocol communication project (REST + messaging + gRPC)
- **Rules:** Implement timeouts, retries, idempotency, and correlation IDs on every cross-service call

---

## Assignment 1: Order-Payment Saga with REST & Message Queue

### Scenario

Implement an order checkout flow where Order Service and Payment Service communicate via synchronous REST for queries and asynchronous messaging for the payment workflow — including failure compensation.

### Requirements

**Order Service:**

- `POST /orders` — creates order in `pending` state
- Publishes `PaymentRequested` event to RabbitMQ (or Redis Streams)
- Listens for `PaymentCompleted`, `PaymentFailed`
- On `PaymentCompleted` → status `paid`; on `PaymentFailed` → `cancelled` + `StockReleaseRequested` event

**Payment Service:**

- Consumes `PaymentRequested`
- Simulates payment processing (80% success, 20% failure with random)
- Publishes `PaymentCompleted` or `PaymentFailed` with same `correlation_id` and `order_id`
- `GET /payments/{order_id}` — sync status query via REST

**REST integration (Order → Payment):**

- Before creating order, `GET /payments/methods/{user_id}` validates payment method exists
- Use `httpx.AsyncClient` with:
  - Timeout: 3s connect, 5s read
  - Retry: 3 attempts, exponential backoff on 5xx
  - Correlation header: `X-Correlation-ID`

**Messaging (RabbitMQ recommended):**

- Exchange: `orders` (topic)
- Queues: `payment.requests`, `payment.results`, `inventory.release`
- Dead letter exchange for failed messages after 3 retries
- Manual ack after successful processing

**Idempotency:**

- Payment Service: `Idempotency-Key` header on REST; `payment_idempotency:{key}` in Redis
- Event handler skips duplicate `PaymentRequested` with same `event_id`

**Error handling:**

- Order Service REST client: circuit breaker after 5 failures
- Malformed message → DLQ + alert log

**Docker Compose:** order-service, payment-service, rabbitmq, redis, postgres × 2

### Technical Specifications

- Synchronous REST (httpx) with timeouts and retries
- Asynchronous messaging (RabbitMQ or Kafka)
- Event-driven architecture
- Saga pattern with compensation
- Idempotency keys
- Correlation IDs
- Dead letter queues

### Acceptance Criteria

- [ ] Successful payment flow: order pending → paid (events + state correct)
- [ ] Failed payment cancels order and publishes stock release event
- [ ] Duplicate `PaymentRequested` does not double-charge (idempotency proved)
- [ ] REST retry logs 3 attempts on simulated 503 from Payment Service
- [ ] DLQ receives message after handler raises 3 times
- [ ] Correlation ID consistent in Order and Payment logs for one checkout
- [ ] `docker-compose up` runs full flow via test script

### Bonus Challenges

- Outbox table in Order Service for reliable event publish
- Payment webhook simulation (async callback path)
- OpenAPI client generated from Payment Service spec

### Hints

- RabbitMQ: `aio_pika` connect_robust, declare durable queues
- Saga compensation: separate handler for `PaymentFailed`
- httpx retry: `transport = httpx.AsyncHTTPTransport(retries=3)` or manual loop

---

## Assignment 2: Event Streaming with Kafka

### Scenario

Build an event streaming pipeline for an analytics platform using Kafka — multiple producers, multiple consumer groups, and event schema evolution.

### Requirements

**Topics:**

- `user.events` — registration, login, profile_update
- `order.events` — created, paid, shipped
- `analytics.aggregates` — computed metrics (producer: analytics service)

**Producers (User Service & Order Service):**

- Publish JSON events with schema:
```json
{
  "event_id": "uuid",
  "event_type": "order.created",
  "timestamp": "ISO8601",
  "correlation_id": "uuid",
  "version": 1,
  "payload": {}
}
```
- Partition key: `user_id` for user events, `order_id` for order events
- Producer acks=all, retries=3

**Consumers:**

1. **Analytics Consumer** (consumer group `analytics`)
   - Aggregates: orders per hour, revenue per hour
   - Writes to PostgreSQL `hourly_stats` table
   - At-least-once semantics with manual offset commit after DB write

2. **Notification Consumer** (consumer group `notifications`)
   - Sends email stub on `order.paid`
   - Independent offset from analytics group — same events, different processing

3. **Audit Consumer** (consumer group `audit`)
   - Append-only audit log table

**Kafka features:**

- Create topics with 3 partitions, replication factor 1 (dev)
- Consumer rebalance handling — log on partition assign/revoke
- `GET /kafka/health` — check broker connectivity

**Failure scenarios (test scripts):**

- Consumer crash mid-processing → message redelivered → idempotent write
- Slow consumer → lag monitoring endpoint `GET /analytics/lag`

**Schema evolution:**

- `version: 2` adds optional field `metadata` — consumers handle both v1 and v2

### Technical Specifications

- Kafka producer/consumer (aiokafka or confluent-kafka)
- Topic partitioning and consumer groups
- Event-driven architecture
- At-least-once delivery and idempotent consumers
- Event schema versioning
- Offset management

### Acceptance Criteria

- [ ] Events with same user_id land in same partition (prove with partition metadata in logs)
- [ ] Analytics and Notification groups both process same `order.paid` independently
- [ ] Hourly stats match manual count after 100 test events
- [ ] Consumer idempotency: replay does not duplicate stats (unique constraint on hour+metric)
- [ ] v1 and v2 events both consumed without crash
- [ ] Lag endpoint returns increasing then decreasing lag under load test

### Bonus Challenges

- Kafka Connect sink to PostgreSQL (config only)
- Exactly-once semantics discussion + transactional producer attempt
- Schema Registry with Avro (optional advanced)

### Hints

- aiokafka: `AIOKafkaProducer`, `AIOKafkaConsumer(group_id='analytics')`
- Idempotent DB write: `INSERT ... ON CONFLICT DO NOTHING`
- Partition key: `key=order_id.encode()` on send

---

## Assignment 3: gRPC Inter-Service Communication

### Scenario

Replace REST calls between high-throughput internal services with gRPC for inventory checks and stock reservation — while keeping REST at the API Gateway for external clients.

### Requirements

**Protocol Buffers (`protos/inventory.proto`):**

```protobuf
service InventoryService {
  rpc CheckStock(StockRequest) returns (StockResponse);
  rpc ReserveStock(ReserveRequest) returns (ReserveResponse);
  rpc ReleaseStock(ReleaseRequest) returns (ReleaseResponse);
  rpc StreamStockUpdates(StockFilter) returns (stream StockUpdate);
}
```

**Inventory gRPC Server** (port 50051):

- Implement all 4 RPCs
- `CheckStock` — read current quantity
- `ReserveStock` — decrement if available; return success/failure
- `ReleaseStock` — compensation for cancelled orders
- `StreamStockUpdates` — server streaming: push updates every 5s for filtered SKUs

**Order Service gRPC Client:**

- Call `CheckStock` before order creation
- Call `ReserveStock` in transaction flow
- On payment failure, call `ReleaseStock`
- Connection channel with keepalive options

**API Gateway:**

- Still REST externally
- Order Service uses gRPC internally — document "REST at edge, gRPC inside"

**gRPC features:**

- Metadata: pass `correlation-id` in gRPC metadata headers
- Deadline: 2 second deadline on `CheckStock`
- Error handling: map `grpc.RpcError` codes to application errors
- Reflection enabled for `grpcurl` testing

**Mixed communication assignment deliverable:**

| Integration | Protocol | Use Case |
|-------------|----------|----------|
| Client → Gateway | REST | Public API |
| Gateway → Order | REST | Proxy |
| Order → Inventory | gRPC | Stock check/reserve |
| Order → Payment | RabbitMQ | Async payment |
| Analytics | Kafka | Event stream |

**Tests:**

- Unit test gRPC servicer with in-memory server
- Integration test full order with mock payment

### Technical Specifications

- gRPC server and client in Python (`grpcio`, `grpcio-tools`)
- Protocol Buffers definition and code generation
- Streaming RPC (server streaming)
- Metadata and deadlines
- Error status codes
- Mixed REST + gRPC + messaging architecture

### Acceptance Criteria

- [ ] `grpcurl` can call CheckStock and ReserveStock
- [ ] Order flow uses gRPC for inventory (not REST) — verified in code/README
- [ ] Deadline exceeded on slow CheckStock returns error to Order Service
- [ ] StreamStockUpdates delivers 5 updates in 25s test
- [ ] correlation-id visible in gRPC metadata on server logs
- [ ] Full mixed-protocol diagram in README
- [ ] proto generated Python files in repo or generation script documented

### Bonus Challenges

- Bidirectional streaming for real-time inventory sync
- gRPC health checking protocol (`grpc.health.v1`)
- TLS/mTLS between Order and Inventory (self-signed certs)

### Hints

- Generate: `python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/inventory.proto`
- Deadline: `stub.CheckStock(request, timeout=2)`
- Metadata: `metadata=(('correlation-id', cid),)`
