# Part 11: Async Programming

> Master asynchronous programming in Python for building high-performance, concurrent applications.

## 📚 Table of Contents

1. [Async Fundamentals](#1-async-fundamentals)
2. [Event Loop](#2-event-loop)
3. [Coroutines](#3-coroutines)
4. [asyncio Module](#4-asyncio-module)
5. [Async Context Managers](#5-async-context-managers)
6. [Async Iterators](#6-async-iterators)
7. [Async Patterns](#7-async-patterns)
8. [Performance Optimization](#8-performance-optimization)
9. [Exercises](#exercises)

---

## 1. Async Fundamentals

### Synchronous vs Asynchronous Execution

**Synchronous (Sequential):**
```python
import time

def download_file(file_id):
    print(f"Downloading file {file_id}...")
    time.sleep(2)  # Simulates network delay
    print(f"File {file_id} downloaded!")
    return f"data_{file_id}"

# Sequential execution - takes 6 seconds
start = time.time()
result1 = download_file(1)
result2 = download_file(2)
result3 = download_file(3)
print(f"Total time: {time.time() - start:.2f}s")  # ~6 seconds
```

**Asynchronous (Concurrent):**
```python
import asyncio

async def download_file(file_id):
    print(f"Downloading file {file_id}...")
    await asyncio.sleep(2)  # Non-blocking delay
    print(f"File {file_id} downloaded!")
    return f"data_{file_id}"

# Concurrent execution - takes 2 seconds
async def main():
    start = time.time()
    results = await asyncio.gather(
        download_file(1),
        download_file(2),
        download_file(3)
    )
    print(f"Total time: {time.time() - start:.2f}s")  # ~2 seconds
    print(f"Results: {results}")

asyncio.run(main())
```

### Blocking vs Non-Blocking I/O

**Blocking I/O:**
```python
# Thread waits (blocks) until operation completes
import requests

def fetch_data(url):
    response = requests.get(url)  # Blocks until response received
    return response.json()

# While waiting for response, CPU is idle
data = fetch_data("https://api.example.com/data")
```

**Non-Blocking I/O:**
```python
# Thread can do other work while waiting
import aiohttp

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# While waiting, event loop can run other coroutines
data = await fetch_data("https://api.example.com/data")
```

### Event-Driven Architecture

```python
"""
Event Loop Model:

┌─────────────────────────────┐
│       Event Loop            │
│                             │
│  ┌─────────────────────┐   │
│  │   Ready Queue       │   │
│  │  [task1, task2...]  │   │
│  └─────────────────────┘   │
│                             │
│  ┌─────────────────────┐   │
│  │   Waiting Queue     │   │
│  │  [task waiting I/O] │   │
│  └─────────────────────┘   │
└─────────────────────────────┘

When I/O completes → Move to ready queue
When task awaits → Move to waiting queue
"""

import asyncio

async def task_a():
    print("Task A: Starting")
    await asyncio.sleep(1)  # Yields control to event loop
    print("Task A: Done")

async def task_b():
    print("Task B: Starting")
    await asyncio.sleep(0.5)  # Yields control to event loop
    print("Task B: Done")

async def main():
    await asyncio.gather(task_a(), task_b())

asyncio.run(main())
# Output:
# Task A: Starting
# Task B: Starting
# Task B: Done
# Task A: Done
```

### When to Use Async

**✅ Use Async For:**
- **I/O-bound operations**: Network requests, file I/O, database queries
- **High concurrency**: Handling many connections (web servers, chat apps)
- **Real-time applications**: WebSockets, streaming data
- **API calls**: Multiple concurrent API requests

**❌ Don't Use Async For:**
- **CPU-bound operations**: Heavy computations, image processing
- **Simple scripts**: Single request, linear flow
- **Existing sync code**: Unless significant I/O bottleneck

```python
# Good use case: Concurrent API calls
async def fetch_user_data(user_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_user(session, uid) for uid in user_ids]
        return await asyncio.gather(*tasks)

# Bad use case: CPU-intensive work
async def fibonacci(n):  # DON'T DO THIS
    if n <= 1:
        return n
    await asyncio.sleep(0)  # Pointless await
    return fibonacci(n-1) + fibonacci(n-2)
```

---

## 2. Event Loop

### How Event Loop Works

```python
"""
Event Loop Workflow:

1. Check ready queue for tasks
2. Execute task until it awaits
3. Register I/O operation with OS
4. Move task to waiting queue
5. Check if any I/O completed
6. Move completed tasks to ready queue
7. Repeat until all tasks done
"""

import asyncio

# Get the event loop
loop = asyncio.get_event_loop()

# Or use asyncio.run() which handles loop creation/closing
asyncio.run(main())
```

### Event Loop Lifecycle

```python
import asyncio

async def task():
    print("Task running")
    await asyncio.sleep(1)
    return "Done"

# Method 1: asyncio.run() - Preferred (Python 3.7+)
result = asyncio.run(task())
print(result)

# Method 2: Manual loop management - Lower level
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    result = loop.run_until_complete(task())
    print(result)
finally:
    loop.close()
```

### Running the Event Loop

```python
import asyncio

async def say_after(delay, message):
    await asyncio.sleep(delay)
    print(message)

async def main():
    print(f"Started at {time.strftime('%X')}")
    
    # Run sequentially
    await say_after(1, "First")
    await say_after(1, "Second")
    
    print(f"Finished at {time.strftime('%X')}")

asyncio.run(main())  # Takes 2 seconds
```

### Multiple Loop Strategies

```python
import asyncio

# Strategy 1: gather() - Run all, wait for all
async def strategy_gather():
    results = await asyncio.gather(
        fetch_data(1),
        fetch_data(2),
        fetch_data(3)
    )
    return results

# Strategy 2: create_task() - Fine-grained control
async def strategy_tasks():
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    task3 = asyncio.create_task(fetch_data(3))
    
    # Can do other work here
    print("Tasks started, doing other work...")
    
    # Wait for completion
    result1 = await task1
    result2 = await task2
    result3 = await task3
    
    return [result1, result2, result3]

# Strategy 3: as_completed() - Process as they complete
async def strategy_as_completed():
    tasks = [fetch_data(i) for i in range(1, 4)]
    
    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(f"Got result: {result}")
```

---

## 3. Coroutines

### async/await Syntax

```python
# Regular function
def regular_function():
    return "I'm synchronous"

# Coroutine function (notice 'async')
async def coroutine_function():
    return "I'm asynchronous"

# Calling them
result1 = regular_function()  # Executes immediately
result2 = coroutine_function()  # Returns coroutine object, doesn't execute

print(type(result2))  # <class 'coroutine'>

# To execute coroutine, you must await it
async def main():
    result = await coroutine_function()  # Now it executes
    print(result)

asyncio.run(main())
```

### Creating Coroutines

```python
import asyncio

# Basic coroutine
async def greet(name):
    await asyncio.sleep(1)
    return f"Hello, {name}!"

# Coroutine that calls other coroutines
async def greet_many(names):
    for name in names:
        greeting = await greet(name)
        print(greeting)

# Coroutine with error handling
async def safe_fetch(url):
    try:
        await asyncio.sleep(1)  # Simulate network request
        if url == "bad_url":
            raise ValueError("Invalid URL")
        return f"Data from {url}"
    except ValueError as e:
        print(f"Error: {e}")
        return None

async def main():
    await greet_many(["Alice", "Bob"])
    result = await safe_fetch("bad_url")

asyncio.run(main())
```

### Awaiting Coroutines

```python
import asyncio

async def step1():
    print("Step 1 starting")
    await asyncio.sleep(1)
    print("Step 1 done")
    return 1

async def step2():
    print("Step 2 starting")
    await asyncio.sleep(1)
    print("Step 2 done")
    return 2

# Sequential execution
async def sequential():
    result1 = await step1()  # Wait for step1
    result2 = await step2()  # Then wait for step2
    return result1 + result2  # Takes 2 seconds

# Concurrent execution
async def concurrent():
    result1, result2 = await asyncio.gather(
        step1(),  # Both start immediately
        step2()
    )
    return result1 + result2  # Takes 1 second
```

### Coroutine Execution Flow

```python
import asyncio

async def coroutine_flow():
    print("1. Coroutine started")
    
    # Execution continues until await
    print("2. About to await")
    
    # Control returns to event loop here
    await asyncio.sleep(1)
    
    # Resumes after sleep completes
    print("3. After await")
    
    # Another await
    await asyncio.sleep(1)
    
    print("4. Coroutine ending")
    return "Done"

async def main():
    print("Main: Starting")
    result = await coroutine_flow()
    print(f"Main: Got result: {result}")

asyncio.run(main())
```

### Common Coroutine Patterns

```python
import asyncio
from typing import List

# Pattern 1: Concurrent API calls
async def fetch_all_users(user_ids: List[int]):
    async def fetch_user(user_id):
        await asyncio.sleep(0.5)  # Simulate API call
        return {"id": user_id, "name": f"User{user_id}"}
    
    tasks = [fetch_user(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)

# Pattern 2: Producer-Consumer
async def producer(queue):
    for i in range(5):
        await asyncio.sleep(0.5)
        await queue.put(i)
        print(f"Produced: {i}")
    await queue.put(None)  # Sentinel value

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumed: {item}")
        await asyncio.sleep(1)

async def producer_consumer():
    queue = asyncio.Queue()
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )

# Pattern 3: Retry logic
async def retry_operation(max_attempts=3):
    for attempt in range(max_attempts):
        try:
            await asyncio.sleep(0.5)
            if attempt < max_attempts - 1:
                raise ValueError("Failed")
            return "Success"
        except ValueError as e:
            print(f"Attempt {attempt + 1} failed")
            if attempt == max_attempts - 1:
                raise

asyncio.run(retry_operation())
```

---

## 4. asyncio Module

### asyncio.create_task()

```python
import asyncio
import time

async def say_hello(name, delay):
    await asyncio.sleep(delay)
    return f"Hello, {name}!"

async def main():
    # Create tasks - they start running immediately
    task1 = asyncio.create_task(say_hello("Alice", 2))
    task2 = asyncio.create_task(say_hello("Bob", 1))
    
    print("Tasks created, both running now")
    
    # Do other work while tasks run
    await asyncio.sleep(0.5)
    print("Did some other work")
    
    # Wait for results
    result1 = await task1
    result2 = await task2
    
    print(result1, result2)

asyncio.run(main())
```

### asyncio.gather()

```python
import asyncio

async def fetch_data(source_id):
    await asyncio.sleep(1)
    return f"Data from {source_id}"

async def main():
    # Gather waits for all coroutines to complete
    results = await asyncio.gather(
        fetch_data("API-1"),
        fetch_data("API-2"),
        fetch_data("API-3")
    )
    print(results)
    # ['Data from API-1', 'Data from API-2', 'Data from API-3']

# Error handling with gather
async def main_with_errors():
    results = await asyncio.gather(
        fetch_data("API-1"),
        failing_fetch(),  # This will fail
        fetch_data("API-3"),
        return_exceptions=True  # Don't stop on error
    )
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {i} failed: {result}")
        else:
            print(f"Task {i} result: {result}")

async def failing_fetch():
    await asyncio.sleep(0.5)
    raise ValueError("API error")

asyncio.run(main_with_errors())
```

### asyncio.wait()

```python
import asyncio

async def task(name, duration):
    await asyncio.sleep(duration)
    return f"{name} completed"

async def main():
    tasks = {
        asyncio.create_task(task("Task1", 2)),
        asyncio.create_task(task("Task2", 1)),
        asyncio.create_task(task("Task3", 3))
    }
    
    # Wait for first completion
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )
    
    print(f"First completed: {done.pop().result()}")
    print(f"Still pending: {len(pending)}")
    
    # Wait for all remaining
    done, pending = await asyncio.wait(pending)
    for task in done:
        print(task.result())

# Wait with timeout
async def main_with_timeout():
    tasks = {
        asyncio.create_task(task("Task1", 5)),
        asyncio.create_task(task("Task2", 1))
    }
    
    done, pending = await asyncio.wait(
        tasks,
        timeout=2  # Wait max 2 seconds
    )
    
    print(f"Completed in time: {len(done)}")
    print(f"Timed out: {len(pending)}")
    
    # Cancel pending tasks
    for t in pending:
        t.cancel()

asyncio.run(main())
```

### asyncio.sleep()

```python
import asyncio
import time

# Non-blocking sleep
async def async_sleep_demo():
    print("Start")
    await asyncio.sleep(2)  # Event loop can run other tasks
    print("After 2 seconds")

# Compare with blocking sleep
async def blocking_sleep_demo():
    print("Start")
    time.sleep(2)  # BLOCKS entire event loop - DON'T DO THIS
    print("After 2 seconds")

# Practical use: Rate limiting
async def rate_limited_requests(urls, requests_per_second=5):
    delay = 1.0 / requests_per_second
    
    results = []
    for url in urls:
        result = await fetch_url(url)
        results.append(result)
        await asyncio.sleep(delay)  # Rate limit
    
    return results
```

### Timeouts and Cancellation

```python
import asyncio

# Timeout with wait_for
async def long_operation():
    await asyncio.sleep(10)
    return "Completed"

async def main_timeout():
    try:
        result = await asyncio.wait_for(long_operation(), timeout=2.0)
        print(result)
    except asyncio.TimeoutError:
        print("Operation timed out!")

# Manual cancellation
async def main_cancel():
    task = asyncio.create_task(long_operation())
    
    await asyncio.sleep(1)
    task.cancel()  # Cancel the task
    
    try:
        await task
    except asyncio.CancelledError:
        print("Task was cancelled")

# Graceful cancellation
async def cancellable_task():
    try:
        while True:
            await asyncio.sleep(1)
            print("Working...")
    except asyncio.CancelledError:
        print("Cleaning up...")
        await cleanup()
        raise  # Re-raise to properly cancel

async def cleanup():
    print("Cleanup complete")

# Shield from cancellation
async def critical_operation():
    await asyncio.sleep(2)
    return "Important data"

async def main_shield():
    task = asyncio.create_task(critical_operation())
    shielded = asyncio.shield(task)
    
    try:
        await asyncio.wait_for(shielded, timeout=1.0)
    except asyncio.TimeoutError:
        print("Timed out, but task continues")
        result = await task  # Wait for it to finish
        print(f"Got result: {result}")

asyncio.run(main_timeout())
```

---

## 5. Async Context Managers

### async with

```python
import asyncio

# Async context manager for resource management
class AsyncDatabase:
    async def __aenter__(self):
        print("Connecting to database...")
        await asyncio.sleep(1)  # Simulate connection
        self.connection = "Connected"
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Closing database connection...")
        await asyncio.sleep(0.5)  # Simulate cleanup
        self.connection = None
        return False  # Don't suppress exceptions

    async def query(self, sql):
        await asyncio.sleep(0.5)
        return f"Results for: {sql}"

# Usage
async def main():
    async with AsyncDatabase() as db:
        result = await db.query("SELECT * FROM users")
        print(result)
    # Connection automatically closed

asyncio.run(main())
```

### Creating Async Context Managers

```python
import asyncio
from contextlib import asynccontextmanager

# Method 1: Class-based
class AsyncFile:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
    
    async def __aenter__(self):
        print(f"Opening {self.filename}")
        await asyncio.sleep(0.1)  # Simulate async open
        self.file = open(self.filename, 'w')
        return self.file
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(f"Closing {self.filename}")
        await asyncio.sleep(0.1)  # Simulate async close
        if self.file:
            self.file.close()

# Method 2: Decorator-based
@asynccontextmanager
async def async_file(filename):
    print(f"Opening {filename}")
    await asyncio.sleep(0.1)
    f = open(filename, 'w')
    try:
        yield f
    finally:
        print(f"Closing {filename}")
        await asyncio.sleep(0.1)
        f.close()

# Real-world example: HTTP session
import aiohttp

@asynccontextmanager
async def http_session():
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()

async def fetch_data():
    async with http_session() as session:
        async with session.get('https://api.example.com/data') as response:
            return await response.json()
```

### Practical Examples

```python
import asyncio
from contextlib import asynccontextmanager

# Connection pool manager
@asynccontextmanager
async def get_db_connection(pool):
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)

# Timeout context
@asynccontextmanager
async def timeout_context(seconds):
    task = asyncio.current_task()
    
    def timeout_callback():
        task.cancel()
    
    handle = asyncio.get_event_loop().call_later(seconds, timeout_callback)
    try:
        yield
    finally:
        handle.cancel()

# Usage
async def main():
    try:
        async with timeout_context(2.0):
            await long_running_operation()
    except asyncio.CancelledError:
        print("Operation timed out")

# Async lock context
async def safe_operation(lock, resource):
    async with lock:  # Automatically acquire and release
        print(f"Working on {resource}")
        await asyncio.sleep(1)
        print(f"Done with {resource}")

async def main_locks():
    lock = asyncio.Lock()
    await asyncio.gather(
        safe_operation(lock, "Resource A"),
        safe_operation(lock, "Resource B")
    )
```

---

## 6. Async Iterators

### async for

```python
import asyncio

# Async iterator class
class AsyncRange:
    def __init__(self, start, stop):
        self.current = start
        self.stop = stop
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        
        await asyncio.sleep(0.5)  # Simulate async operation
        value = self.current
        self.current += 1
        return value

# Usage
async def main():
    async for num in AsyncRange(0, 5):
        print(num)

asyncio.run(main())
```

### Creating Async Iterators

```python
import asyncio

# Method 1: Async generator (simplest)
async def async_countdown(n):
    while n > 0:
        await asyncio.sleep(1)
        yield n
        n -= 1

async def main():
    async for num in async_countdown(5):
        print(num)

# Method 2: Class-based
class AsyncDataFetcher:
    def __init__(self, urls):
        self.urls = urls
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.urls):
            raise StopAsyncIteration
        
        url = self.urls[self.index]
        self.index += 1
        
        # Simulate fetching data
        await asyncio.sleep(0.5)
        return f"Data from {url}"

async def fetch_all():
    urls = ['url1', 'url2', 'url3']
    async for data in AsyncDataFetcher(urls):
        print(data)

# Real-world: Paginated API
class PaginatedAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.page = 1
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        url = f"{self.base_url}?page={self.page}"
        
        # Simulate API call
        await asyncio.sleep(0.5)
        data = {"page": self.page, "items": [f"item{i}" for i in range(3)]}
        
        if self.page > 3:  # Stop after 3 pages
            raise StopAsyncIteration
        
        self.page += 1
        return data

async def fetch_all_pages():
    async for page_data in PaginatedAPI("https://api.example.com/items"):
        print(f"Page {page_data['page']}: {page_data['items']}")

asyncio.run(fetch_all_pages())
```

### Async Comprehensions

```python
import asyncio

async def fetch_number(n):
    await asyncio.sleep(0.5)
    return n * 2

# Async list comprehension
async def main():
    # Create list of results
    results = [await fetch_number(i) for i in range(5)]
    print(results)  # [0, 2, 4, 6, 8]
    
    # With condition
    even_results = [
        await fetch_number(i) 
        for i in range(10) 
        if i % 2 == 0
    ]
    print(even_results)

# Async generator expression
async def async_gen():
    return (await fetch_number(i) for i in range(5))

async def use_async_gen():
    gen = async_gen()
    async for value in gen:
        print(value)

asyncio.run(main())
```

---

## 7. Async Patterns

### Concurrent API Calls

```python
import asyncio
import aiohttp
from typing import List, Dict

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()

async def fetch_multiple_urls(urls: List[str]) -> List[Dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# With error handling
async def fetch_url_safe(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            response.raise_for_status()
            return {"url": url, "data": await response.json(), "error": None}
    except Exception as e:
        return {"url": url, "data": None, "error": str(e)}

async def fetch_all_safe(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url_safe(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### Rate Limiting

```python
import asyncio
from asyncio import Semaphore
import time

# Pattern 1: Semaphore (limit concurrent requests)
async def rate_limited_fetch(url, semaphore):
    async with semaphore:
        print(f"Fetching {url}")
        await asyncio.sleep(1)  # Simulate request
        return f"Data from {url}"

async def fetch_with_limit(urls, max_concurrent=5):
    semaphore = Semaphore(max_concurrent)
    tasks = [rate_limited_fetch(url, semaphore) for url in urls]
    return await asyncio.gather(*tasks)

# Pattern 2: Token bucket
class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

async def rate_limited_request(url, bucket):
    await bucket.acquire()
    print(f"Requesting {url} at {time.strftime('%H:%M:%S')}")
    await asyncio.sleep(0.5)
    return f"Data from {url}"

async def main():
    bucket = TokenBucket(rate=2.0, capacity=5)  # 2 requests per second
    urls = [f"url{i}" for i in range(10)]
    
    tasks = [rate_limited_request(url, bucket) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

asyncio.run(main())
```

### Retries

```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_async(
    coro_func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Retry async function with exponential backoff."""
    
    for attempt in range(max_attempts):
        try:
            return await coro_func()
        except exceptions as e:
            if attempt == max_attempts - 1:
                raise
            
            wait_time = delay * (backoff ** attempt)
            print(f"Attempt {attempt + 1} failed: {e}")
            print(f"Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

# Usage
async def unreliable_api_call():
    import random
    await asyncio.sleep(0.5)
    if random.random() < 0.7:  # 70% failure rate
        raise ValueError("API Error")
    return "Success"

async def main():
    result = await retry_async(
        unreliable_api_call,
        max_attempts=5,
        delay=1.0,
        backoff=2.0,
        exceptions=(ValueError,)
    )
    print(f"Result: {result}")

# With decorator
def async_retry(max_attempts=3, delay=1.0, backoff=2.0):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await retry_async(
                lambda: func(*args, **kwargs),
                max_attempts=max_attempts,
                delay=delay,
                backoff=backoff
            )
        return wrapper
    return decorator

@async_retry(max_attempts=3, delay=1.0)
async def fetch_data(url):
    print(f"Fetching {url}")
    await asyncio.sleep(0.5)
    # Might fail...
    return "Data"
```

### Circuit Breaker

```python
import asyncio
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
    
    async def call(self, coro_func):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                print("Circuit: Trying half-open state")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await coro_func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                print("Circuit: Closing (recovered)")
                self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            print("Circuit: Opening (too many failures)")
            self.state = CircuitState.OPEN

# Usage
circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=5.0)

async def unreliable_service():
    import random
    await asyncio.sleep(0.5)
    if random.random() < 0.7:
        raise ValueError("Service error")
    return "Success"

async def main():
    for i in range(10):
        try:
            result = await circuit_breaker.call(unreliable_service)
            print(f"Call {i}: {result}")
        except Exception as e:
            print(f"Call {i}: Failed - {e}")
        
        await asyncio.sleep(1)

asyncio.run(main())
```

---

## 8. Performance Optimization

### When Async is Faster

```python
import asyncio
import time
import requests
import aiohttp

# Example 1: I/O-bound operations

# Synchronous - SLOW
def fetch_sync(urls):
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response.json())
    return results

# Asynchronous - FAST
async def fetch_async(urls):
    async with aiohttp.ClientSession() as session:
        async def fetch_one(url):
            async with session.get(url) as response:
                return await response.json()
        
        tasks = [fetch_one(url) for url in urls]
        return await asyncio.gather(*tasks)

# Benchmark
urls = ['https://api.example.com/data'] * 10

start = time.time()
sync_results = fetch_sync(urls)
print(f"Sync took: {time.time() - start:.2f}s")  # ~10 seconds

start = time.time()
async_results = asyncio.run(fetch_async(urls))
print(f"Async took: {time.time() - start:.2f}s")  # ~1 second
```

### When Async is NOT Needed

```python
import asyncio

# ❌ BAD: CPU-bound work doesn't benefit from async
async def calculate_fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

# Using async here is SLOWER due to overhead
async def bad_async():
    results = await asyncio.gather(
        calculate_fibonacci(1000),
        calculate_fibonacci(1000),
        calculate_fibonacci(1000)
    )
    return results

# ✅ GOOD: Use multiprocessing for CPU-bound
from concurrent.futures import ProcessPoolExecutor

def good_cpu_bound():
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(
            calculate_fibonacci,
            [1000, 1000, 1000]
        ))
    return results

# ❌ BAD: Single I/O operation
async def single_request():
    await asyncio.sleep(1)
    return "Done"

# No benefit, just use regular function
def regular_request():
    time.sleep(1)
    return "Done"

# ✅ GOOD: Multiple I/O operations
async def multiple_requests():
    results = await asyncio.gather(
        fetch_data(1),
        fetch_data(2),
        fetch_data(3)
    )
    return results
```

### Profiling Async Code

```python
import asyncio
import time
from functools import wraps

# Timing decorator
def async_timed(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            return await func(*args, **kwargs)
        finally:
            elapsed = time.time() - start
            print(f"{func.__name__} took {elapsed:.2f}s")
    return wrapper

# Usage
@async_timed
async def slow_operation():
    await asyncio.sleep(2)
    return "Done"

# Profiling with context manager
class AsyncTimer:
    def __init__(self, name="Operation"):
        self.name = name
    
    async def __aenter__(self):
        self.start = time.time()
        return self
    
    async def __aexit__(self, *args):
        elapsed = time.time() - self.start
        print(f"{self.name} took {elapsed:.2f}s")

# Usage
async def main():
    async with AsyncTimer("Fetching data"):
        await fetch_data()
    
    async with AsyncTimer("Processing"):
        await process_data()

# Task monitoring
async def monitor_tasks():
    all_tasks = asyncio.all_tasks()
    
    for task in all_tasks:
        print(f"Task: {task.get_name()}")
        print(f"Done: {task.done()}")
        print(f"Cancelled: {task.cancelled()}")

# Memory usage
import tracemalloc

async def profile_memory():
    tracemalloc.start()
    
    # Your async code here
    await heavy_async_operation()
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory: {current / 10**6:.2f} MB")
    print(f"Peak memory: {peak / 10**6:.2f} MB")
    tracemalloc.stop()
```

### Optimization Tips

```python
import asyncio

# 1. Batch operations
async def fetch_users_batch(user_ids):
    # ✅ GOOD: Single request with all IDs
    return await api_call(f"users?ids={','.join(map(str, user_ids))}")

async def fetch_users_individual(user_ids):
    # ❌ BAD: Separate request for each
    tasks = [api_call(f"users/{uid}") for uid in user_ids]
    return await asyncio.gather(*tasks)

# 2. Use connection pooling
import aiohttp

# ✅ GOOD: Reuse session
async def fetch_many_good(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_session(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# ❌ BAD: New session each time
async def fetch_many_bad(urls):
    tasks = [fetch_new_session(url) for url in urls]
    return await asyncio.gather(*tasks)

# 3. Avoid blocking calls in async
async def good_async():
    # ✅ Use async version
    await asyncio.sleep(1)
    
    # ✅ Run blocking call in executor
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, blocking_function)
    
    return result

async def bad_async():
    # ❌ NEVER do this - blocks event loop
    time.sleep(1)
    result = blocking_function()
    return result

# 4. Cancel unnecessary tasks
async def fetch_first_success(urls):
    tasks = [asyncio.create_task(fetch(url)) for url in urls]
    
    try:
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                # Got first success, cancel others
                for task in tasks:
                    if not task.done():
                        task.cancel()
                return result
            except Exception:
                continue
    finally:
        # Ensure all tasks are cancelled
        for task in tasks:
            if not task.done():
                task.cancel()

# 5. Use asyncio.create_task() over await
async def sequential_slow():
    # ❌ Runs sequentially
    result1 = await operation1()
    result2 = await operation2()
    return result1, result2

async def concurrent_fast():
    # ✅ Runs concurrently
    task1 = asyncio.create_task(operation1())
    task2 = asyncio.create_task(operation2())
    return await task1, await task2
```

---

## Exercises

### Exercise 1: Async Web Scraper
Create an async web scraper that fetches multiple pages concurrently.

**Requirements:**
- Fetch multiple URLs concurrently
- Implement rate limiting (max 5 concurrent requests)
- Add retry logic with exponential backoff
- Extract and return page titles

```python
# Your solution here
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def scrape_pages(urls):
    # Implement this
    pass
```

### Exercise 2: Async File Processor
Build an async file processor that reads, processes, and writes files concurrently.

**Requirements:**
- Read multiple files asynchronously
- Process data (e.g., count words)
- Write results to output files
- Use async context managers

```python
# Your solution here
async def process_files(file_paths):
    # Implement this
    pass
```

### Exercise 3: Real-time Data Aggregator
Create a system that fetches data from multiple APIs and aggregates results.

**Requirements:**
- Fetch from 3+ different APIs concurrently
- Implement timeout (5 seconds per request)
- Handle failures gracefully
- Return aggregated results

```python
# Your solution here
async def aggregate_data(api_urls):
    # Implement this
    pass
```

### Exercise 4: Async Task Queue
Implement a producer-consumer pattern with async queues.

**Requirements:**
- Producer adds tasks to queue
- Multiple consumers process tasks concurrently
- Implement graceful shutdown
- Track completed tasks

```python
# Your solution here
async def task_queue_system(num_producers, num_consumers):
    # Implement this
    pass
```

---

## Summary

### Key Concepts

1. **Async Fundamentals**
   - Non-blocking I/O
   - Event loop architecture
   - Coroutines and await

2. **Core asyncio Functions**
   - `asyncio.run()`, `create_task()`, `gather()`, `wait()`
   - Timeouts and cancellation
   - Error handling

3. **Advanced Patterns**
   - Async context managers and iterators
   - Rate limiting and circuit breakers
   - Retry logic
   - Connection pooling

4. **Performance**
   - Use for I/O-bound operations
   - Avoid for CPU-bound tasks
   - Profile and optimize
   - Batch operations when possible

### Best Practices

✅ **DO:**
- Use `asyncio.run()` as entry point
- Create tasks with `create_task()` for concurrency
- Handle exceptions properly
- Use async context managers for resources
- Implement timeouts
- Profile your async code

❌ **DON'T:**
- Use `time.sleep()` (use `asyncio.sleep()`)
- Forget to await coroutines
- Mix sync and async code carelessly
- Use async for CPU-bound operations
- Create too many concurrent tasks without limiting

### Next Steps

Now that you understand async programming, you're ready to:
- Learn **Pydantic** for data validation (Part 12)
- Build APIs with **FastAPI** (Part 13)
- Integrate async database operations with **SQLAlchemy** (Part 14)

---

**Continue to [Part 12: Pydantic](../Part-12-Pydantic/README.md)** →
