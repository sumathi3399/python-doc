# Part 11: Async Programming - Practice Problems

> Test async/await, asyncio, coroutines

---

## Problem 1: Basic Async Function

**Task**: Simple async function
```python
import asyncio

async def greet(name):
    return f"Hello, {name}"

# Run it
result = asyncio.run(greet("Alice"))
assert result == "Hello, Alice"
```

**Time**: 10 minutes

---

## Problem 2: Async Sleep

**Task**: Delayed async function
```python
import asyncio

async def delayed_message(delay, message):
    await asyncio.sleep(delay)
    return message

result = asyncio.run(delayed_message(1, "Done"))
```

**Time**: 10 minutes

---

## Problem 3: Running Multiple Coroutines

**Task**: Run 3 tasks concurrently
```python
import asyncio

async def task(n):
    await asyncio.sleep(1)
    return n * 2

async def main():
    results = await asyncio.gather(
        task(1),
        task(2),
        task(3)
    )
    return results  # [2, 4, 6]

asyncio.run(main())
```

**Time**: 15 minutes

---

## Problem 4: Create Task

**Task**: Use asyncio.create_task
```python
import asyncio

async def count():
    for i in range(3):
        print(i)
        await asyncio.sleep(0.5)

async def main():
    task1 = asyncio.create_task(count())
    task2 = asyncio.create_task(count())
    await task1
    await task2

asyncio.run(main())
```

**Time**: 15 minutes

---

## Problem 5: Async with Timeout

**Task**: Cancel after timeout
```python
import asyncio

async def long_operation():
    await asyncio.sleep(5)
    return "Done"

async def main():
    try:
        result = await asyncio.wait_for(long_operation(), timeout=2)
    except asyncio.TimeoutError:
        return "Timeout!"

result = asyncio.run(main())
```

**Time**: 15 minutes

---

## Problem 6: Async Queue

**Task**: Producer-consumer pattern
```python
import asyncio

async def producer(queue):
    for i in range(5):
        await queue.put(i)
        await asyncio.sleep(0.1)

async def consumer(queue):
    while True:
        item = await queue.get()
        print(f"Got {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    producer_task = asyncio.create_task(producer(queue))
    consumer_task = asyncio.create_task(consumer(queue))
    
    await producer_task
    await queue.join()
    consumer_task.cancel()

asyncio.run(main())
```

**Time**: 20 minutes

---

## Problem 7: Async Context Manager

**Task**: Async with statement
```python
import asyncio

class AsyncResource:
    async def __aenter__(self):
        print("Acquiring resource")
        await asyncio.sleep(1)
        return self
    
    async def __aexit__(self, *args):
        print("Releasing resource")
        await asyncio.sleep(1)

async def main():
    async with AsyncResource() as resource:
        print("Using resource")

asyncio.run(main())
```

**Time**: 20 minutes

---

## Problem 8: Async Iterator

**Task**: Async for loop
```python
import asyncio

class AsyncRange:
    def __init__(self, n):
        self.n = n
        self.i = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.i >= self.n:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        self.i += 1
        return self.i

async def main():
    async for i in AsyncRange(3):
        print(i)

asyncio.run(main())
```

**Time**: 25 minutes

---

## Problem 9: aiohttp Request (if available)

**Task**: Async HTTP GET
```python
import asyncio
# import aiohttp  # pip install aiohttp

async def fetch(url):
    # Simulate with sleep if aiohttp not available
    await asyncio.sleep(0.5)
    return f"Content from {url}"

async def main():
    result = await fetch("https://example.com")
    print(result)

asyncio.run(main())
```

**Time**: 15 minutes

---

## Problem 10: Gather vs Wait

**Task**: Understand difference
```python
import asyncio

async def task(n):
    await asyncio.sleep(n)
    return n

async def main():
    # gather - waits for all, returns results in order
    results = await asyncio.gather(task(1), task(2))
    print(results)  # [1, 2]
    
    # wait - more control with FIRST_COMPLETED etc
    done, pending = await asyncio.wait(
        [task(1), task(2)],
        return_when=asyncio.ALL_COMPLETED
    )

asyncio.run(main())
```

**Time**: 20 minutes

---

## Summary Check

**8+ solved** → Async mastered  
**5-7 solved** → Practice gather and create_task  
**< 5 solved** → Review async/await basics
