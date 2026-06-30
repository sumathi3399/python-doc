# Part 15: Redis Integration - Practice Problems

> Test Redis caching, sessions, pub/sub

---

## Problem 1: Connect to Redis

**Task**: Basic connection
```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.ping()  # Should return True
```

**Time**: 5 minutes

---

## Problem 2: SET and GET

**Task**: Store and retrieve string
```python
import redis

r = redis.Redis(decode_responses=True)

r.set('key', 'value')
value = r.get('key')
assert value == 'value'
```

**Time**: 5 minutes

---

## Problem 3: SET with Expiry

**Task**: TTL for caching
```python
import redis
import time

r = redis.Redis(decode_responses=True)

r.setex('temp_key', 5, 'temp_value')  # Expires in 5 seconds
print(r.get('temp_key'))  # 'temp_value'
time.sleep(6)
print(r.get('temp_key'))  # None
```

**Time**: 10 minutes

---

## Problem 4: Lists - Queue

**Task**: LPUSH and RPOP
```python
import redis

r = redis.Redis(decode_responses=True)

r.lpush('queue', 'task1', 'task2', 'task3')
task = r.rpop('queue')  # Get task1 (FIFO)
```

**Time**: 10 minutes

---

## Problem 5: Hash - Store Object

**Task**: HSET and HGET
```python
import redis

r = redis.Redis(decode_responses=True)

r.hset('user:1', mapping={'name': 'Alice', 'age': '25'})
name = r.hget('user:1', 'name')
all_data = r.hgetall('user:1')
```

**Time**: 15 minutes

---

## Problem 6: Set Operations

**Task**: Add and check membership
```python
import redis

r = redis.Redis(decode_responses=True)

r.sadd('tags', 'python', 'redis', 'fastapi')
is_member = r.sismember('tags', 'python')  # True
all_tags = r.smembers('tags')
```

**Time**: 10 minutes

---

## Problem 7: Sorted Set - Leaderboard

**Task**: ZADD and ZRANGE
```python
import redis

r = redis.Redis(decode_responses=True)

r.zadd('leaderboard', {'Alice': 100, 'Bob': 85, 'Charlie': 120})
top_3 = r.zrevrange('leaderboard', 0, 2, withscores=True)
```

**Time**: 15 minutes

---

## Problem 8: Increment Counter

**Task**: Atomic increment
```python
import redis

r = redis.Redis(decode_responses=True)

r.set('counter', 0)
r.incr('counter')
r.incr('counter', 5)  # Increment by 5
count = int(r.get('counter'))  # 6
```

**Time**: 10 minutes

---

## Problem 9: Cache Pattern

**Task**: Check cache before DB
```python
import redis

r = redis.Redis(decode_responses=True)

def get_user(user_id):
    # Check cache
    cached = r.get(f'user:{user_id}')
    if cached:
        return cached
    
    # Simulate DB query
    user_data = f'User {user_id} data'
    
    # Cache for 5 minutes
    r.setex(f'user:{user_id}', 300, user_data)
    return user_data
```

**Time**: 20 minutes

---

## Problem 10: Pub/Sub

**Task**: Publish and subscribe
```python
import redis
import threading
import time

r = redis.Redis(decode_responses=True)

def subscriber():
    pubsub = r.pubsub()
    pubsub.subscribe('channel')
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Received: {message['data']}")

# Start subscriber in thread
t = threading.Thread(target=subscriber, daemon=True)
t.start()

time.sleep(1)
r.publish('channel', 'Hello Redis!')
time.sleep(1)
```

**Time**: 20 minutes

---

## Summary Check

**8+ solved** → Redis mastered  
**5-7 solved** → Practice caching patterns  
**< 5 solved** → Review Redis data types
