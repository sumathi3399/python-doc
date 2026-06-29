# Part 15: Redis Integration - Assignments

## Assignment Guidelines

- **Estimated time:** 14-18 hours total
- **Prerequisites:** Parts 1-14 complete; Redis server or Docker required
- **Submission:** FastAPI app integrating Redis for caching, sessions, rate limiting, pub/sub
- **Rules:** Use `redis-py` and `redis.asyncio`; handle Redis connection failures gracefully

---

## Assignment 1: API Caching & Performance Layer

### Scenario

Build a FastAPI service for product catalog APIs where Redis provides a caching layer, cache warming, invalidation, and statistics — reducing database load by 80%+ on read-heavy endpoints.

### Requirements

1. **Redis connection:**
   - Sync client for scripts; `redis.asyncio` for FastAPI
   - Connection pool configuration
   - Health check: `GET /health/redis` pings Redis

2. **Cache-aside pattern:**

```python
async def get_product(product_id: int) -> Product:
    # 1. Check cache
    # 2. On miss: load DB, set cache with TTL
    # 3. Return product
```

3. **TTL strategy:**
   - Products: 300s
   - Product lists: 60s
   - Categories: 3600s

4. **Cache key design:** `product:{id}`, `products:list:{hash_of_query_params}`, `category:{id}`

5. **Serialization:** JSON via `model_dump_json()` / `json.loads`

6. **Cache invalidation:**
   - On product update/delete: delete `product:{id}` and related list keys (use set `product:{id}:list_keys` to track)
   - On category change: pattern invalidation with `SCAN` (document performance note)

7. **Cache warming:** startup event preloads top 20 products by ID list

8. **Cache statistics:**
   - Hits, misses, hit rate — stored in Redis `HINCRBY stats:hits 1`
   - `GET /admin/cache/stats` returns metrics

9. **Stampede protection:** simple lock with `SET lock:product:{id} NX EX 10` while recomputing

10. **Graceful degradation:** if Redis down, fall through to DB only; log warning

11. **Write-through variant** for `update_product` — write DB then update cache

12. **Tests:** mock Redis with `fakeredis` or pytest fixture

### Technical Specifications

- Redis strings, hashes, sets
- TTL (`SETEX`, `expire`)
- Cache-aside and write-through patterns
- Cache invalidation strategies
- Connection pooling
- Async Redis with FastAPI
- Atomic operations (`SET NX`)

### Acceptance Criteria

- [ ] Second identical request served from cache (prove with DB query counter)
- [ ] TTL expiry causes refresh after sleep/test mock time
- [ ] Update invalidates product and list caches
- [ ] Stats endpoint shows hits > 0 after repeated reads
- [ ] App runs when Redis unavailable (degraded mode)
- [ ] Stampede lock prevents duplicate DB queries (test with concurrent requests)
- [ ] 12+ tests with fakeredis

### Bonus Challenges

- Redis JSON module if available
- Bloom filter for "product probably not in cache" quick negative
- Two-tier cache: in-memory LRU + Redis

### Hints

- `await redis.get(key)` / `await redis.set(key, value, ex=300)`
- Track list keys: on cache list, `SADD product:1:list_keys products:list:abc`
- fakeredis: `import fakeredis.aioredis`

---

## Assignment 2: Session Management & Rate Limiting Platform

### Scenario

Implement session storage and distributed rate limiting for an API gateway — two core Redis use cases in production systems.

### Requirements

**Session management:**

1. **`SessionStore` class:**
   - `create_session(user_id, data: dict) -> session_id` — `SET session:{id} JSON EX 3600`
   - `get_session(session_id) -> dict | None`
   - `update_session(session_id, data)` — merge JSON
   - `delete_session(session_id)` — logout
   - `extend_session(session_id)` — sliding window: refresh TTL on each access

2. **Multi-device sessions:** `SADD user:{user_id}:sessions {session_id}`; list all sessions for user

3. **Revoke all sessions** for user on password change

4. **FastAPI middleware:** read `session_id` cookie; attach `request.state.user`

5. **Session data:** user_id, roles, created_at, last_accessed, device_info

**Rate limiting:**

1. **Sliding window** per IP: `rate:ip:{ip}` using sorted set with timestamps

2. **Token bucket** per user for API tier: basic 100/min, premium 1000/min

3. **Endpoint-specific limits:** `POST /auth/login` — 5/min per IP

4. **Middleware `RateLimitMiddleware`:**
   - Returns `429` with headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
   - Admin API key bypasses limits

5. **Redis Lua script** for atomic increment + expire (rate limit check in one round trip)

6. **Distributed rate limit** — works across multiple app instances (prove with 2 processes)

7. **Rate limit stats** in Redis hash per endpoint

**Error handling:**

- Redis timeout → fail open or closed (document choice; implement configurable)

### Technical Specifications

- Session storage patterns
- Sliding window and token bucket rate limiting
- Sorted sets, Lua scripts
- Middleware integration
- TTL and sliding expiration
- Multi-key operations

### Acceptance Criteria

- [ ] Session persists across requests; sliding TTL extends on access
- [ ] Logout deletes session; subsequent request unauthenticated
- [ ] Revoke all clears all user sessions
- [ ] 6th login attempt in 1 minute returns 429
- [ ] Rate limit headers present and accurate
- [ ] Lua script used for atomic rate check
- [ ] Admin bypass works with `X-Admin-Key` header
- [ ] 15+ tests

### Bonus Challenges

- Geographic rate limits by country header
- Session fixation protection on login (rotate session ID)
- Redis Cluster compatibility notes

### Hints

- Sliding window ZSET: `ZADD key now now`, `ZREMRANGEBYSCORE key 0 now-window`, `ZCARD key`
- Lua: `EVAL` script returns 1 if allowed, 0 if denied
- Session cookie: `httponly=True, secure=True` in production notes

---

## Assignment 3: Real-Time Notifications with Pub/Sub & Distributed Locks

### Scenario

Build a notification service using Redis Pub/Sub for real-time delivery, distributed locks for scheduled job coordination, and WebSocket fan-out via FastAPI.

### Requirements

1. **Pub/Sub channels:**
   - `notifications:user:{user_id}` — user-specific
   - `notifications:broadcast` — all users
   - `notifications:room:{room_id}` — chat room style

2. **`NotificationPublisher`:**
   - `publish_user(user_id, payload)`
   - `publish_broadcast(payload)`
   - JSON serialization with type field: `order_shipped`, `message`, `alert`

3. **`NotificationSubscriber`** (background asyncio task):
   - Subscribes to pattern `notifications:*` or per-user channels
   - Forwards to WebSocket `ConnectionManager`

4. **WebSocket endpoint `/ws/notifications`:**
   - Authenticated user subscribes to their channel on connect
   - Receives pub/sub messages in real time

5. **Notification history:**
   - `LPUSH notifications:history:{user_id} payload` + `LTRIM` keep last 100
   - `GET /notifications/history` reads list

6. **Distributed lock (scheduled job):**
   - `send_daily_digest()` job must run on exactly one worker
   - `SET digest:lock:2024-01-15 NX EX 300` — only winner runs
   - Lock release with Lua compare-and-del (prevent deleting other's lock)

7. **Idempotent job processing:**
   - `SET job:processed:{job_id} 1 NX EX 86400` — skip duplicate

8. **Presence system:**
   - `SET presence:user:{id} online EX 60` refreshed by heartbeat
   - `GET /users/online` returns count via `SCAN` or maintained set

9. **Integration test:** publish message → subscriber → WebSocket client receives within 1s

10. **Failure handling:** subscriber reconnect loop on Redis disconnect

### Technical Specifications

- Pub/Sub publish/subscribe
- Lists for history
- Distributed locks with NX and Lua unlock
- Async pub/sub with `redis.asyncio`
- WebSocket integration
- Idempotency keys

### Acceptance Criteria

- [ ] User A does not receive User B's notifications
- [ ] Broadcast reaches all connected WebSocket clients
- [ ] History returns last 100 notifications in order
- [ ] Daily digest lock allows only one worker execution (test with 3 concurrent asyncio tasks)
- [ ] Duplicate job ID skipped on second attempt
- [ ] Presence expires after 60s without heartbeat
- [ ] Subscriber recovers after Redis restart simulation

### Bonus Challenges

- Redis Streams instead of Pub/Sub for persistence
- Consumer groups with `XREADGROUP`
- Leaderboard using sorted set for notification engagement scores

### Hints

- `pubsub = redis.pubsub(); await pubsub.subscribe(channel)`
- Lock release Lua: `if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) end`
- WebSocket manager: dict mapping user_id → set of websockets
