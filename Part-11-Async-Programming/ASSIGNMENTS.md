# Part 11: Async Programming - Assignments

## Assignment Guidelines

- **Estimated time:** 14-18 hours total
- **Prerequisites:** Parts 1-10 complete; `aiohttp`, `httpx` recommended
- **Submission:** Async Python project runnable with `asyncio.run(main())`
- **Rules:** No blocking calls in async code (`time.sleep`, sync `requests`); use `asyncio.sleep`, `aiohttp`/`httpx`

---

## Assignment 1: Async Task Queue System

### Scenario

Build a production-style async task queue with producers enqueueing jobs and multiple worker coroutines processing them concurrently — similar to Celery/ARQ but simplified.

### Requirements

1. **`asyncio.Queue`** — bounded queue (maxsize=100) for tasks

2. **Task model:** `Task(id, type, payload, retries=0)` with types: `email`, `report`, `webhook`

3. **Producers (2 coroutines):** generate tasks at different rates; stop when total enqueued reaches N

4. **Consumers (5 workers):** `async def worker(name, queue)` — process until sentinel received

5. **Graceful shutdown:**
   - `asyncio.Event` `shutdown_event`
   - Send `None` sentinel per worker
   - `await asyncio.gather(*workers, return_exceptions=True)`

6. **Retry with exponential backoff:** failed task re-queued with `await asyncio.sleep(2 ** retries)`

7. **Timeout per task:** `asyncio.wait_for(process(task), timeout=5.0)`

8. **Metrics coroutine:** every 2s print queue size, completed, failed counts

9. **Task handlers** simulate async I/O with `asyncio.sleep(random)`

10. **Structured concurrency:** use `asyncio.TaskGroup` (3.11+) or `gather` for worker supervision

11. **Exception handling:** log task failures; don't crash workers

12. **Priority option (bonus path):** separate queues for high/normal priority

### Technical Specifications

- `async`/`await`, coroutines
- Event loop via `asyncio.run()`
- `create_task`, `gather`, `wait_for`, `Queue`, `Event`
- Async patterns: producer-consumer, graceful shutdown
- Retry and timeout patterns
- No blocking I/O in async path

### Acceptance Criteria

- [ ] 100+ tasks processed by 5 workers concurrently
- [ ] Graceful shutdown completes all in-flight tasks or cancels cleanly
- [ ] Retries occur on simulated random failures (30% failure rate)
- [ ] Timeouts logged for slow tasks (inject 10s sleep on some)
- [ ] Metrics coroutine prints live stats
- [ ] Final report: total completed, failed, retried, avg processing time

### Bonus Challenges

- `asyncio.Semaphore` limiting concurrent webhook calls to 3
- Dead letter queue for tasks exceeding max retries
- Persist queue state to JSON on shutdown and resume on start

### Hints

- Worker loop: `while True: task = await queue.get(); if task is None: break`
- Use `try/finally: queue.task_done()` if using `join` pattern
- `asyncio.create_task(metrics_loop())` at startup

---

## Assignment 2: Real-Time API Aggregator

### Scenario

Build a dashboard backend that fetches data from 5+ mock/real APIs concurrently, handles failures gracefully, and returns aggregated JSON — typical BFF (Backend for Frontend) pattern.

### Requirements

1. **Data sources (async HTTP):**
   - Weather API (mock or open API)
   - Exchange rates
   - News headlines
   - GitHub user stats
   - Crypto prices
   - At least 5 distinct endpoints

2. **Concurrent fetch:** `asyncio.gather(*coros, return_exceptions=True)`

3. **Per-request timeout:** 5 seconds via `wait_for`

4. **Retry:** 3 attempts with exponential backoff for transient errors

5. **Rate limiting:** `asyncio.Semaphore(5)` max concurrent requests

6. **Circuit breaker (simple):** after 3 failures, skip API for 30 seconds

7. **Partial results:** if 2/5 APIs fail, return available data + `errors` section

8. **`async context manager` HTTP client:** single `aiohttp.ClientSession` or `httpx.AsyncClient` for connection pooling

9. **Cache layer:** in-memory dict with TTL; `async def cached_fetch(url)` checks cache first

10. **`aggregate_dashboard()`** — returns unified schema:

```json
{
  "generated_at": "...",
  "weather": {...},
  "rates": {...},
  "partial": true,
  "errors": [{"source": "news", "error": "timeout"}]
}
```

11. **CLI:** `python aggregator.py --refresh 10` refreshes every 10 seconds until Ctrl+C

12. **Async file log:** append each aggregation result to `dashboard.log` using `aiofiles` or executor for write

### Technical Specifications

- asyncio module: gather, wait_for, create_task, Semaphore
- aiohttp or httpx async client
- Async context managers (`async with`)
- Error handling in async code
- Connection pooling
- Rate limiting and circuit breaker patterns

### Acceptance Criteria

- [ ] All 5 APIs fetched concurrently (timing proves parallelism)
- [ ] Total time ≈ slowest API not sum of all (within reason)
- [ ] Timeout prevents hung requests
- [ ] Partial success response when some APIs fail
- [ ] Circuit breaker opens after repeated failures (test with bad URL)
- [ ] Cache prevents duplicate fetch within TTL
- [ ] Single shared ClientSession for all requests

### Bonus Challenges

- `asyncio.as_completed` streaming results to UI as they arrive
- Async generator `stream_prices()` yielding updates every second
- Health check coroutine per API source

### Hints

- `return_exceptions=True` then check `isinstance(r, Exception)`
- Circuit breaker state: `{api: {"failures": 0, "open_until": 0}}`
- Cache entry: `(data, expiry_time)`

---

## Assignment 3: Async Chat Server with WebSocket & Pub/Sub

### Scenario

Implement a multi-room chat server using WebSockets where messages broadcast asynchronously to room members, with optional Redis pub/sub for cross-instance fan-out (Redis optional — in-memory fallback required).

### Requirements

1. **`asyncio.start_server` or FastAPI WebSockets** — accept client connections

2. **Connection manager:**
   - `async def connect(websocket, room, user)`
   - `async def disconnect(websocket, room, user)`
   - `async def broadcast(room, message)` — send to all in room

3. **Rooms:** join/leave commands via JSON messages

4. **Async iterator:** `async for message in websocket` receive loop

5. **Background tasks:**
   - Heartbeat ping every 30s (`create_task`)
   - Cleanup stale connections

6. **In-memory pub/sub:** `asyncio.Queue` per room for message distribution

7. **Optional Redis pub/sub:** `redis.asyncio` subscribe to `room:{id}` channel

8. **Async context manager for connection:**

```python
@asynccontextmanager
async def managed_connection(websocket):
    try:
        yield websocket
    finally:
        await cleanup(websocket)
```

9. **Concurrent room handling:** 10+ simultaneous connections in demo script

10. **Load test script:** `async def simulate_client(name, room)` × 20 clients with `gather`

11. **Typing indicators:** broadcast ephemeral events without persistence

12. **Error handling:** disconnect on protocol error; don't crash server

### Technical Specifications

- Coroutines, tasks, gather, create_task
- Async context managers
- Async iterators (`async for`)
- WebSocket async I/O (websockets library or FastAPI)
- Optional: redis.asyncio pub/sub
- Graceful shutdown with task cancellation

### Acceptance Criteria

- [ ] 10+ clients chat concurrently in 2+ rooms
- [ ] Messages isolated to correct room
- [ ] Disconnect removes client from room registry
- [ ] Heartbeat detects dead connections
- [ ] Server runs 60s+ under load test without error
- [ ] `async with managed_connection` ensures cleanup
- [ ] README documents message protocol JSON schema

### Bonus Challenges

- Message history last 50 per room with `deque`
- Private messages between users
- Admin `kick` command with authorization check
- Integrate with Part 15 Redis pub/sub if completed

### Hints

- Room registry: `dict[str, set[WebSocket]]` — use async lock when modifying
- Broadcast: `await gather(*[ws.send(msg) for ws in room], return_exceptions=True)`
- Shutdown: cancel heartbeat tasks, close all websockets
