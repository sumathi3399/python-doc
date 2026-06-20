# Part 15: Redis Integration

> Master Redis for caching, session management, rate limiting, and real-time features in Python applications.

## 📚 Table of Contents

1. [Redis Fundamentals](#1-redis-fundamentals)
2. [Python Redis Client](#2-python-redis-client)
3. [Async Redis](#3-async-redis)
4. [Caching Patterns](#4-caching-patterns)
5. [Session Management](#5-session-management)
6. [Rate Limiting](#6-rate-limiting)
7. [Distributed Locks](#7-distributed-locks)
8. [Pub/Sub](#8-pubsub)
9. [Exercises](#exercises)

---

## 1. Redis Fundamentals

### What is Redis?

**Redis** (Remote Dictionary Server) is an in-memory data structure store used as:
- **Database**: Persistent key-value store
- **Cache**: Fast temporary storage
- **Message broker**: Pub/Sub messaging
- **Session store**: User session management

**Key Features:**
- In-memory storage (extremely fast)
- Persistence options (RDB, AOF)
- Rich data structures
- Atomic operations
- TTL (Time To Live) support
- Pub/Sub messaging
- Lua scripting

### Data Structures

```python
"""
Redis Data Structures:

1. String     - Simple key-value
2. List       - Linked list
3. Set        - Unique unordered collection
4. Sorted Set - Ordered set with scores
5. Hash       - Field-value pairs
6. Bitmap     - Bit-level operations
7. HyperLogLog - Cardinality estimation
8. Stream     - Append-only log
"""

# String: "key" -> "value"
SET user:1:name "Alice"
GET user:1:name

# List: Ordered collection
LPUSH messages "Hello"
LPUSH messages "World"
LRANGE messages 0 -1  # ["World", "Hello"]

# Set: Unique values
SADD tags "python"
SADD tags "redis"
SMEMBERS tags  # ["python", "redis"]

# Sorted Set: Values with scores
ZADD leaderboard 100 "Alice"
ZADD leaderboard 200 "Bob"
ZRANGE leaderboard 0 -1 WITHSCORES

# Hash: Field-value pairs
HSET user:1 name "Alice"
HSET user:1 email "alice@example.com"
HGETALL user:1
```

### Use Cases

```python
"""
Common Redis Use Cases:

1. Caching
   - API responses
   - Database queries
   - Computed results
   - Session data

2. Rate Limiting
   - API rate limits
   - Login attempts
   - Request throttling

3. Session Management
   - User sessions
   - Shopping carts
   - Temporary data

4. Real-time Analytics
   - Page views
   - Live dashboards
   - Event tracking

5. Message Queues
   - Background jobs
   - Task queues
   - Event streaming

6. Distributed Locks
   - Resource coordination
   - Distributed systems
   - Preventing race conditions

7. Leaderboards
   - Gaming scores
   - Rankings
   - Top lists
"""
```

---

## 2. Python Redis Client

### redis-py Basics

```python
# Install: pip install redis

import redis

# Connect to Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,  # Database number (0-15)
    decode_responses=True  # Return strings instead of bytes
)

# Test connection
r.ping()  # True

# String operations
r.set('name', 'Alice')
r.get('name')  # 'Alice'

# With expiration (TTL)
r.setex('session:123', 3600, 'user_data')  # Expires in 1 hour
r.ttl('session:123')  # Returns remaining seconds

# Delete
r.delete('name')

# Check existence
r.exists('name')  # 0 (False) or 1 (True)

# Multiple operations
r.mset({'key1': 'value1', 'key2': 'value2'})
r.mget(['key1', 'key2'])  # ['value1', 'value2']
```

### Connection Management

```python
import redis
from redis.connection import ConnectionPool

# Method 1: Direct connection
r = redis.Redis(host='localhost', port=6379, db=0)

# Method 2: Connection pool (recommended for production)
pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50,
    decode_responses=True
)
r = redis.Redis(connection_pool=pool)

# Method 3: From URL
r = redis.from_url('redis://localhost:6379/0')
r = redis.from_url('redis://:password@localhost:6379/0')

# Context manager
with redis.Redis(host='localhost', port=6379) as r:
    r.set('key', 'value')
    value = r.get('key')

# Sentinel (high availability)
from redis.sentinel import Sentinel

sentinel = Sentinel([
    ('localhost', 26379),
    ('localhost', 26380),
    ('localhost', 26381)
], socket_timeout=0.1)

# Get master
master = sentinel.master_for('mymaster', socket_timeout=0.1)
master.set('key', 'value')

# Get slave (for reads)
slave = sentinel.slave_for('mymaster', socket_timeout=0.1)
value = slave.get('key')
```

### Connection Pools

```python
import redis
from redis.connection import ConnectionPool

# Create pool
pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=100,  # Max connections in pool
    socket_timeout=5,     # Socket timeout
    socket_connect_timeout=5,
    retry_on_timeout=True,
    decode_responses=True
)

# Use pool
r1 = redis.Redis(connection_pool=pool)
r2 = redis.Redis(connection_pool=pool)
# Both share the same pool

# Pool management
pool.max_connections  # 100
pool.connection_kwargs  # Connection settings

# Release connections
r1.connection_pool.release(r1.connection)

# Close pool
pool.disconnect()

# FastAPI integration
from fastapi import FastAPI

app = FastAPI()

# Create pool at startup
@app.on_event("startup")
async def startup():
    app.state.redis_pool = ConnectionPool(
        host='localhost',
        port=6379,
        max_connections=50
    )
    app.state.redis = redis.Redis(connection_pool=app.state.redis_pool)

@app.on_event("shutdown")
async def shutdown():
    app.state.redis_pool.disconnect()

# Use in endpoints
@app.get("/data/{key}")
async def get_data(key: str):
    value = app.state.redis.get(key)
    return {"value": value}
```

---

## 3. Async Redis

### aioredis / redis with async support

```python
# Install: pip install redis[asyncio]

import asyncio
from redis import asyncio as aioredis

# Create async connection
async def main():
    redis = await aioredis.from_url(
        "redis://localhost",
        encoding="utf-8",
        decode_responses=True
    )
    
    # String operations
    await redis.set('key', 'value')
    value = await redis.get('key')
    print(value)
    
    # Close connection
    await redis.close()

asyncio.run(main())

# With connection pool
async def main():
    pool = aioredis.ConnectionPool.from_url(
        "redis://localhost",
        max_connections=10
    )
    redis = aioredis.Redis(connection_pool=pool)
    
    await redis.set('key', 'value')
    value = await redis.get('key')
    
    await redis.close()
    await pool.disconnect()
```

### Async Operations

```python
import asyncio
from redis import asyncio as aioredis

async def cache_operations():
    redis = await aioredis.from_url("redis://localhost")
    
    # Set with expiration
    await redis.setex('session:123', 3600, 'user_data')
    
    # Get
    value = await redis.get('session:123')
    
    # Pipeline (batch operations)
    pipe = redis.pipeline()
    pipe.set('key1', 'value1')
    pipe.set('key2', 'value2')
    pipe.get('key1')
    results = await pipe.execute()
    
    # Transaction (atomic operations)
    async with redis.pipeline(transaction=True) as pipe:
        pipe.set('counter', 0)
        pipe.incr('counter')
        pipe.incr('counter')
        results = await pipe.execute()
    
    await redis.close()

# FastAPI integration
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.state.redis = await aioredis.from_url(
        "redis://localhost",
        encoding="utf-8",
        decode_responses=True
    )

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()

@app.get("/cache/{key}")
async def get_cached(key: str):
    value = await app.state.redis.get(key)
    return {"value": value}

@app.post("/cache/{key}")
async def set_cached(key: str, value: str, ttl: int = 3600):
    await app.state.redis.setex(key, ttl, value)
    return {"message": "Cached successfully"}
```

---

## 4. Caching Patterns

### Simple Caching

```python
import redis
import json

r = redis.Redis(decode_responses=True)

# Cache function result
def get_user(user_id: int):
    # Try cache first
    cache_key = f"user:{user_id}"
    cached = r.get(cache_key)
    
    if cached:
        print("Cache hit!")
        return json.loads(cached)
    
    # Cache miss - fetch from database
    print("Cache miss - fetching from DB")
    user = fetch_from_database(user_id)
    
    # Store in cache (1 hour TTL)
    r.setex(cache_key, 3600, json.dumps(user))
    
    return user

# Decorator for caching
import functools

def redis_cache(ttl=3600):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try cache
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            r.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@redis_cache(ttl=600)
def expensive_computation(x, y):
    import time
    time.sleep(2)  # Simulate slow operation
    return x + y

result = expensive_computation(5, 3)  # Takes 2 seconds (cache miss)
result = expensive_computation(5, 3)  # Instant (cache hit)
```

### Cache Aside

```python
"""
Cache-Aside Pattern (Lazy Loading):

1. Application checks cache
2. If miss, fetch from database
3. Store in cache for next time
4. Return data

Pros: Only caches what's actually used
Cons: Cache miss penalty
"""

import redis
import json

r = redis.Redis(decode_responses=True)

class UserRepository:
    def get_user(self, user_id: int):
        cache_key = f"user:{user_id}"
        
        # 1. Check cache
        cached = r.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 2. Cache miss - fetch from DB
        user = self._fetch_from_db(user_id)
        
        # 3. Store in cache
        if user:
            r.setex(cache_key, 3600, json.dumps(user))
        
        # 4. Return
        return user
    
    def update_user(self, user_id: int, data: dict):
        # Update database
        self._update_db(user_id, data)
        
        # Invalidate cache
        cache_key = f"user:{user_id}"
        r.delete(cache_key)
    
    def _fetch_from_db(self, user_id: int):
        # Database query
        return {"id": user_id, "name": "Alice"}
    
    def _update_db(self, user_id: int, data: dict):
        # Database update
        pass
```

### Write Through

```python
"""
Write-Through Pattern:

1. Write to cache first
2. Then write to database
3. Cache always in sync with DB

Pros: Cache always up-to-date
Cons: Write latency, cache overhead
"""

import redis
import json

r = redis.Redis(decode_responses=True)

class UserRepository:
    def create_user(self, user_data: dict):
        # 1. Write to database
        user_id = self._insert_to_db(user_data)
        user_data['id'] = user_id
        
        # 2. Write to cache (write-through)
        cache_key = f"user:{user_id}"
        r.setex(cache_key, 3600, json.dumps(user_data))
        
        return user_data
    
    def update_user(self, user_id: int, data: dict):
        # 1. Update database
        self._update_db(user_id, data)
        
        # 2. Update cache (write-through)
        cache_key = f"user:{user_id}"
        user_data = self._fetch_from_db(user_id)
        r.setex(cache_key, 3600, json.dumps(user_data))
        
        return user_data
    
    def get_user(self, user_id: int):
        cache_key = f"user:{user_id}"
        
        # Try cache
        cached = r.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Fetch from DB
        user = self._fetch_from_db(user_id)
        
        # Cache it
        if user:
            r.setex(cache_key, 3600, json.dumps(user))
        
        return user
```

### TTL Management

```python
import redis

r = redis.Redis(decode_responses=True)

# Set TTL on creation
r.setex('key', 3600, 'value')  # Expires in 1 hour

# Set TTL on existing key
r.expire('key', 3600)

# Set expiration timestamp
import time
timestamp = int(time.time()) + 3600
r.expireat('key', timestamp)

# Check TTL
ttl = r.ttl('key')  # Returns seconds remaining
if ttl == -1:
    print("Key exists but has no expiration")
elif ttl == -2:
    print("Key does not exist")
else:
    print(f"Key expires in {ttl} seconds")

# Remove expiration
r.persist('key')

# Variable TTL based on data type
def cache_with_smart_ttl(key: str, value: any):
    if isinstance(value, list):
        ttl = 300  # 5 minutes for lists
    elif isinstance(value, dict):
        ttl = 600  # 10 minutes for dicts
    else:
        ttl = 3600  # 1 hour for others
    
    r.setex(key, ttl, json.dumps(value))

# Sliding window TTL
def get_with_refresh(key: str):
    value = r.get(key)
    if value:
        r.expire(key, 3600)  # Reset TTL on access
    return value
```

---

## 5. Session Management

### Storing Sessions

```python
import redis
import json
import uuid

r = redis.Redis(decode_responses=True)

class SessionManager:
    def create_session(self, user_id: int) -> str:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Session data
        session_data = {
            'user_id': user_id,
            'created_at': time.time(),
            'last_accessed': time.time()
        }
        
        # Store in Redis (24 hour expiration)
        session_key = f"session:{session_id}"
        r.setex(session_key, 86400, json.dumps(session_data))
        
        return session_id
    
    def get_session(self, session_id: str) -> dict:
        session_key = f"session:{session_id}"
        session_data = r.get(session_key)
        
        if not session_data:
            return None
        
        # Update last accessed time
        data = json.loads(session_data)
        data['last_accessed'] = time.time()
        r.setex(session_key, 86400, json.dumps(data))
        
        return data
    
    def update_session(self, session_id: str, data: dict):
        session_key = f"session:{session_id}"
        existing_data = self.get_session(session_id)
        
        if existing_data:
            existing_data.update(data)
            r.setex(session_key, 86400, json.dumps(existing_data))
    
    def delete_session(self, session_id: str):
        session_key = f"session:{session_id}"
        r.delete(session_key)

# FastAPI integration
from fastapi import FastAPI, Cookie, Response

app = FastAPI()
session_manager = SessionManager()

@app.post("/login/")
async def login(username: str, password: str, response: Response):
    # Authenticate user
    user_id = authenticate(username, password)
    
    if user_id:
        # Create session
        session_id = session_manager.create_session(user_id)
        
        # Set cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=86400,
            secure=True  # HTTPS only
        )
        
        return {"message": "Logged in successfully"}
    
    return {"error": "Invalid credentials"}

@app.get("/profile/")
async def profile(session_id: str = Cookie(None)):
    session = session_manager.get_session(session_id)
    
    if not session:
        return {"error": "Unauthorized"}
    
    user_id = session['user_id']
    # Fetch user data
    return {"user_id": user_id}

@app.post("/logout/")
async def logout(session_id: str = Cookie(None)):
    session_manager.delete_session(session_id)
    return {"message": "Logged out successfully"}
```

### Session Expiration

```python
import redis
import json
import time

r = redis.Redis(decode_responses=True)

class SessionManager:
    def __init__(self, ttl=3600):
        self.ttl = ttl
    
    def create_session(self, user_id: int, remember_me: bool = False):
        session_id = str(uuid.uuid4())
        
        # Different TTL based on "remember me"
        ttl = 2592000 if remember_me else self.ttl  # 30 days vs 1 hour
        
        session_data = {
            'user_id': user_id,
            'created_at': time.time(),
            'remember_me': remember_me
        }
        
        session_key = f"session:{session_id}"
        r.setex(session_key, ttl, json.dumps(session_data))
        
        return session_id
    
    def extend_session(self, session_id: str):
        """Extend session TTL (sliding window)"""
        session_key = f"session:{session_id}"
        
        # Check if exists
        if r.exists(session_key):
            # Reset TTL
            r.expire(session_key, self.ttl)
            return True
        return False
    
    def get_session_ttl(self, session_id: str) -> int:
        session_key = f"session:{session_id}"
        return r.ttl(session_key)
    
    def cleanup_expired_sessions(self):
        """Manual cleanup (Redis does this automatically)"""
        pattern = "session:*"
        for key in r.scan_iter(pattern):
            if r.ttl(key) == -2:  # Key expired
                r.delete(key)
```

---

## 6. Rate Limiting

### Token Bucket

```python
import redis
import time

r = redis.Redis(decode_responses=True)

class TokenBucketRateLimiter:
    def __init__(self, rate: int, capacity: int):
        """
        rate: tokens per second
        capacity: max tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
    
    def allow_request(self, user_id: str) -> bool:
        key = f"rate_limit:token_bucket:{user_id}"
        now = time.time()
        
        # Get current state
        pipe = r.pipeline()
        pipe.hget(key, 'tokens')
        pipe.hget(key, 'last_update')
        tokens, last_update = pipe.execute()
        
        # Initialize if first request
        if tokens is None:
            tokens = self.capacity
            last_update = now
        else:
            tokens = float(tokens)
            last_update = float(last_update)
        
        # Add new tokens based on time elapsed
        elapsed = now - last_update
        tokens = min(self.capacity, tokens + elapsed * self.rate)
        
        # Check if request allowed
        if tokens >= 1:
            tokens -= 1
            
            # Update state
            pipe = r.pipeline()
            pipe.hset(key, 'tokens', tokens)
            pipe.hset(key, 'last_update', now)
            pipe.expire(key, int(self.capacity / self.rate) + 1)
            pipe.execute()
            
            return True
        
        return False

# Usage
limiter = TokenBucketRateLimiter(rate=10, capacity=100)  # 10 requests/sec

if limiter.allow_request("user:123"):
    print("Request allowed")
else:
    print("Rate limit exceeded")

# FastAPI integration
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()
limiter = TokenBucketRateLimiter(rate=10, capacity=100)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Get user ID from request (e.g., from token)
    user_id = request.headers.get("X-User-ID", request.client.host)
    
    if not limiter.allow_request(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    response = await call_next(request)
    return response
```

### Sliding Window

```python
import redis
import time

r = redis.Redis(decode_responses=True)

class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def allow_request(self, user_id: str) -> tuple[bool, int]:
        """
        Returns: (allowed, remaining_requests)
        """
        key = f"rate_limit:sliding_window:{user_id}"
        now = time.time()
        window_start = now - self.window_seconds
        
        pipe = r.pipeline()
        
        # Remove old requests outside window
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiration
        pipe.expire(key, self.window_seconds)
        
        results = pipe.execute()
        request_count = results[1]
        
        if request_count < self.max_requests:
            remaining = self.max_requests - request_count - 1
            return True, remaining
        else:
            # Remove the request we just added (over limit)
            r.zrem(key, str(now))
            return False, 0

# Usage
limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=60)

allowed, remaining = limiter.allow_request("user:123")
if allowed:
    print(f"Request allowed. {remaining} remaining")
else:
    print("Rate limit exceeded")

# FastAPI integration with headers
from fastapi import FastAPI, HTTPException, Response

app = FastAPI()
limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_id = request.client.host
    
    allowed, remaining = limiter.allow_request(user_id)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(limiter.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + limiter.window_seconds))
            }
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response
```

### Implementation Patterns

```python
import redis
from functools import wraps

r = redis.Redis(decode_responses=True)

# Decorator for rate limiting
def rate_limit(max_calls: int, period: int):
    """
    Rate limit decorator
    max_calls: Maximum calls allowed
    period: Time period in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create key from function name
            key = f"rate_limit:{func.__name__}"
            
            # Increment counter
            current = r.incr(key)
            
            if current == 1:
                # First call, set expiration
                r.expire(key, period)
            
            if current > max_calls:
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {period}s")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=10, period=60)
def api_call():
    return "Success"

# Per-user rate limiting
class UserRateLimiter:
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period
    
    def check_limit(self, user_id: str) -> bool:
        key = f"user_rate_limit:{user_id}"
        
        current = r.incr(key)
        
        if current == 1:
            r.expire(key, self.period)
        
        return current <= self.max_calls
    
    def get_remaining(self, user_id: str) -> int:
        key = f"user_rate_limit:{user_id}"
        current = int(r.get(key) or 0)
        return max(0, self.max_calls - current)

# Usage
limiter = UserRateLimiter(max_calls=100, period=3600)

if limiter.check_limit("user:123"):
    # Process request
    remaining = limiter.get_remaining("user:123")
    print(f"Request allowed. {remaining} remaining")
else:
    print("Rate limit exceeded")
```

---

## 7. Distributed Locks

### Acquiring Locks

```python
import redis
import time
import uuid

r = redis.Redis(decode_responses=True)

class RedisLock:
    def __init__(self, key: str, timeout: int = 10):
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())
    
    def acquire(self) -> bool:
        """Acquire lock"""
        # SET if not exists (NX) with expiration (EX)
        return r.set(
            self.key,
            self.identifier,
            nx=True,
            ex=self.timeout
        )
    
    def release(self) -> bool:
        """Release lock (only if we own it)"""
        # Lua script for atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        script = r.register_script(lua_script)
        return script(keys=[self.key], args=[self.identifier])
    
    def __enter__(self):
        while not self.acquire():
            time.sleep(0.1)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

# Usage
lock = RedisLock("resource:1", timeout=10)

if lock.acquire():
    try:
        # Critical section
        print("Lock acquired, doing work...")
        time.sleep(2)
    finally:
        lock.release()
else:
    print("Could not acquire lock")

# Context manager
with RedisLock("resource:1"):
    # Critical section
    print("Doing work with lock...")
```

### Lock Patterns

```python
import redis
import time

r = redis.Redis(decode_responses=True)

# Pattern 1: Simple lock with retry
def acquire_lock_with_retry(key: str, timeout: int = 10, max_retries: int = 3):
    identifier = str(uuid.uuid4())
    lock_key = f"lock:{key}"
    
    for attempt in range(max_retries):
        if r.set(lock_key, identifier, nx=True, ex=timeout):
            return identifier
        time.sleep(0.1 * (attempt + 1))  # Exponential backoff
    
    return None

# Pattern 2: Lock with auto-renewal
class RenewableLock:
    def __init__(self, key: str, timeout: int = 10):
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())
        self.acquired = False
    
    def acquire(self) -> bool:
        self.acquired = r.set(
            self.key,
            self.identifier,
            nx=True,
            ex=self.timeout
        )
        return self.acquired
    
    def renew(self) -> bool:
        """Extend lock expiration"""
        if self.acquired:
            return r.expire(self.key, self.timeout)
        return False
    
    def release(self):
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        script = r.register_script(lua_script)
        script(keys=[self.key], args=[self.identifier])
        self.acquired = False

# Pattern 3: Distributed counter with lock
class DistributedCounter:
    def __init__(self, key: str):
        self.key = key
        self.lock_key = f"lock:{key}"
    
    def increment(self) -> int:
        with RedisLock(self.lock_key):
            current = int(r.get(self.key) or 0)
            new_value = current + 1
            r.set(self.key, new_value)
            return new_value
    
    def get(self) -> int:
        return int(r.get(self.key) or 0)
```

### Redlock Algorithm

```python
"""
Redlock Algorithm (for multiple Redis instances)

1. Get current time in milliseconds
2. Try to acquire lock on all N instances
3. If acquired on majority (N/2 + 1), success
4. If failed, release all locks
5. Add randomized delay before retry
"""

import redis
import time
import random

class Redlock:
    def __init__(self, redis_instances: list, key: str, ttl: int = 10):
        self.instances = redis_instances
        self.key = f"lock:{key}"
        self.ttl = ttl
        self.identifier = str(uuid.uuid4())
        self.quorum = len(redis_instances) // 2 + 1
    
    def acquire(self) -> bool:
        start_time = time.time()
        acquired_count = 0
        
        # Try to acquire lock on all instances
        for instance in self.instances:
            try:
                if instance.set(
                    self.key,
                    self.identifier,
                    nx=True,
                    px=self.ttl * 1000  # milliseconds
                ):
                    acquired_count += 1
            except:
                pass
        
        # Calculate elapsed time
        elapsed = (time.time() - start_time) * 1000
        validity_time = self.ttl * 1000 - elapsed
        
        # Check if we got the quorum
        if acquired_count >= self.quorum and validity_time > 0:
            return True
        
        # Failed to get quorum, release all locks
        self.release()
        return False
    
    def release(self):
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        for instance in self.instances:
            try:
                script = instance.register_script(lua_script)
                script(keys=[self.key], args=[self.identifier])
            except:
                pass

# Usage with multiple Redis instances
instances = [
    redis.Redis(host='redis1', port=6379),
    redis.Redis(host='redis2', port=6379),
    redis.Redis(host='redis3', port=6379),
    redis.Redis(host='redis4', port=6379),
    redis.Redis(host='redis5', port=6379),
]

lock = Redlock(instances, "resource:1", ttl=10)

if lock.acquire():
    try:
        print("Lock acquired on majority")
        # Critical section
    finally:
        lock.release()
else:
    print("Failed to acquire lock")
```

---

## 8. Pub/Sub

### Publishing Messages

```python
import redis

r = redis.Redis(decode_responses=True)

# Publish message
r.publish('news', 'Breaking news!')
r.publish('alerts', 'System alert!')

# Publish with pattern
r.publish('channel:room1', 'Message to room 1')
r.publish('channel:room2', 'Message to room 2')

# Publisher class
class Publisher:
    def __init__(self):
        self.r = redis.Redis(decode_responses=True)
    
    def send_message(self, channel: str, message: str):
        subscribers_count = self.r.publish(channel, message)
        return subscribers_count
    
    def broadcast(self, message: str):
        """Send to all channels"""
        channels = ['news', 'alerts', 'updates']
        for channel in channels:
            self.r.publish(channel, message)

# Usage
pub = Publisher()
count = pub.send_message('news', 'Hello subscribers!')
print(f"Message delivered to {count} subscribers")
```

### Subscribing to Channels

```python
import redis
import json

r = redis.Redis(decode_responses=True)

# Subscribe to single channel
pubsub = r.pubsub()
pubsub.subscribe('news')

for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"Received: {message['data']}")

# Subscribe to multiple channels
pubsub = r.pubsub()
pubsub.subscribe('news', 'alerts', 'updates')

for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"Channel {message['channel']}: {message['data']}")

# Pattern subscription
pubsub = r.pubsub()
pubsub.psubscribe('channel:*')  # Subscribe to all channels starting with "channel:"

for message in pubsub.listen():
    if message['type'] == 'pmessage':
        print(f"Pattern {message['pattern']}: {message['data']}")

# Subscriber class
class Subscriber:
    def __init__(self, channels: list):
        self.r = redis.Redis(decode_responses=True)
        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(channels)
    
    def listen(self):
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                self.handle_message(message['channel'], message['data'])
    
    def handle_message(self, channel: str, data: str):
        print(f"[{channel}] {data}")
    
    def stop(self):
        self.pubsub.unsubscribe()
        self.pubsub.close()

# Usage
sub = Subscriber(['news', 'alerts'])
sub.listen()  # Blocks and listens for messages
```

### Use Cases

```python
import redis
import json
import threading

r = redis.Redis(decode_responses=True)

# Use Case 1: Real-time Notifications
class NotificationSystem:
    def __init__(self):
        self.r = redis.Redis(decode_responses=True)
    
    def send_notification(self, user_id: str, notification: dict):
        channel = f"user:{user_id}:notifications"
        self.r.publish(channel, json.dumps(notification))
    
    def subscribe_user(self, user_id: str, callback):
        pubsub = self.r.pubsub()
        channel = f"user:{user_id}:notifications"
        pubsub.subscribe(channel)
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                notification = json.loads(message['data'])
                callback(notification)

# Use Case 2: Chat Application
class ChatRoom:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.channel = f"chat:room:{room_id}"
        self.r = redis.Redis(decode_responses=True)
        self.pubsub = self.r.pubsub()
    
    def send_message(self, user: str, message: str):
        msg_data = {
            'user': user,
            'message': message,
            'timestamp': time.time()
        }
        self.r.publish(self.channel, json.dumps(msg_data))
    
    def join(self, callback):
        self.pubsub.subscribe(self.channel)
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                msg_data = json.loads(message['data'])
                callback(msg_data)
    
    def leave(self):
        self.pubsub.unsubscribe()

# Use Case 3: Event Broadcasting
class EventBroadcaster:
    def __init__(self):
        self.r = redis.Redis(decode_responses=True)
    
    def broadcast_event(self, event_type: str, data: dict):
        channel = f"events:{event_type}"
        event = {
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }
        self.r.publish(channel, json.dumps(event))
    
    def subscribe_events(self, event_types: list, callback):
        pubsub = self.r.pubsub()
        channels = [f"events:{event_type}" for event_type in event_types]
        pubsub.subscribe(channels)
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                event = json.loads(message['data'])
                callback(event)

# FastAPI WebSocket integration
from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

class WebSocketNotifier:
    def __init__(self):
        self.r = redis.Redis(decode_responses=True)
        self.connections = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.connections[user_id] = websocket
        
        # Start listening for notifications
        asyncio.create_task(self.listen_notifications(user_id))
    
    async def listen_notifications(self, user_id: str):
        pubsub = self.r.pubsub()
        pubsub.subscribe(f"user:{user_id}:notifications")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                ws = self.connections.get(user_id)
                if ws:
                    await ws.send_text(message['data'])

notifier = WebSocketNotifier()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await notifier.connect(websocket, user_id)
    
    try:
        while True:
            await websocket.receive_text()
    except:
        del notifier.connections[user_id]
```

---

## Exercises

### Exercise 1: Caching Layer for API
Build a complete caching layer for a REST API.

**Requirements:**
- Cache-aside pattern
- TTL management
- Cache invalidation
- Cache warming
- Cache statistics

```python
# Your solution here
import redis
from fastapi import FastAPI

app = FastAPI()
r = redis.Redis(decode_responses=True)

# Implement caching layer
```

### Exercise 2: Rate Limiter Middleware
Create a comprehensive rate limiting middleware.

**Requirements:**
- Sliding window algorithm
- Per-user limits
- Different limits for different endpoints
- Rate limit headers
- Admin bypass

```python
# Your solution here
from fastapi import FastAPI, Request

app = FastAPI()

# Implement rate limiter
```

### Exercise 3: Session Storage System
Build a complete session management system.

**Requirements:**
- Create/read/update/delete sessions
- Session expiration
- Sliding window sessions
- Multi-device sessions
- Session revocation

```python
# Your solution here

# Implement session system
```

### Exercise 4: Real-time Notification System
Create a real-time notification system using Pub/Sub.

**Requirements:**
- User-specific notifications
- Broadcast notifications
- Notification types
- WebSocket integration
- Notification history

```python
# Your solution here
from fastapi import FastAPI, WebSocket

app = FastAPI()

# Implement notification system
```

---

## Summary

### Key Concepts

1. **Redis Basics**
   - In-memory data store
   - Multiple data structures
   - TTL support
   - Atomic operations

2. **Caching**
   - Cache-aside pattern
   - Write-through pattern
   - TTL management
   - Cache invalidation

3. **Session Management**
   - Session storage
   - Expiration strategies
   - Sliding windows
   - Multi-device support

4. **Rate Limiting**
   - Token bucket
   - Sliding window
   - Per-user limits
   - Distributed rate limiting

5. **Advanced Features**
   - Distributed locks
   - Pub/Sub messaging
   - Real-time features
   - Async operations

### Best Practices

✅ **DO:**
- Use connection pooling
- Set appropriate TTLs
- Handle Redis failures gracefully
- Use async Redis for async apps
- Implement proper rate limiting
- Use Lua scripts for atomic operations
- Monitor Redis memory usage

❌ **DON'T:**
- Store large objects in Redis
- Use Redis as primary database
- Forget to set expiration
- Block the main thread
- Store sensitive data unencrypted
- Use single Redis instance in production
- Ignore memory limits

### Next Steps

Now that you understand Redis, you're ready to:
- Build **production-grade FastAPI projects** (Part 16)
- Implement complete caching strategies
- Add real-time features
- Scale applications horizontally

---

**Continue to [Part 16: Production-Grade FastAPI Project](../Part-16-Production-FastAPI-Project/README.md)** →
