# Part 10: Concurrency & Parallelism

> Master Python's concurrency tools to write efficient programs that do multiple things at once.

## 📚 Table of Contents

1. [Concurrency vs Parallelism](#1-concurrency-vs-parallelism)
2. [The Global Interpreter Lock (GIL)](#2-the-global-interpreter-lock-gil)
3. [Threading](#3-threading)
4. [Multiprocessing](#4-multiprocessing)
5. [Choosing the Right Tool](#5-choosing-the-right-tool)
6. [Exercises](#exercises)

---

## 1. Concurrency vs Parallelism

### Definitions

**Concurrency**: Dealing with multiple things at once (task switching)
**Parallelism**: Doing multiple things at once (truly simultaneous)

```
Concurrency (Single Core):
Time →
Core: [Task A][Task B][Task A][Task B][Task A]
      (switching between tasks)

Parallelism (Multiple Cores):
Time →
Core 1: [Task A][Task A][Task A][Task A][Task A]
Core 2: [Task B][Task B][Task B][Task B][Task B]
        (truly simultaneous)
```

### When to Use What

**I/O-Bound Tasks** (waiting for external resources):
- Reading/writing files
- Network requests
- Database queries
- **Solution**: Threading or Async

**CPU-Bound Tasks** (heavy computation):
- Data processing
- Image manipulation
- Mathematical calculations
- **Solution**: Multiprocessing

---

## 2. The Global Interpreter Lock (GIL)

### What is the GIL?

The GIL is a **mutex** (lock) that allows only **one thread** to execute Python bytecode at a time, even on multi-core systems.

### Why Does it Exist?

1. **Memory Management**: Python's memory management isn't thread-safe
2. **Simplicity**: Makes C extensions easier to write
3. **Historical**: Design decision from early Python days

### Impact

```python
import threading
import time

counter = 0

def increment():
    global counter
    for _ in range(1000000):
        counter += 1

# Two threads
thread1 = threading.Thread(target=increment)
thread2 = threading.Thread(target=increment)

start = time.time()
thread1.start()
thread2.start()
thread1.join()
thread2.join()
print(f"Time: {time.time() - start:.2f}s")
print(f"Counter: {counter}")

# Despite 2 threads, not 2x faster due to GIL
# May even be slower due to context switching!
```

### Working Around the GIL

1. **For I/O**: Use threading (GIL released during I/O)
2. **For CPU**: Use multiprocessing (separate processes = separate GILs)
3. **For Both**: Use async I/O (event loop)

---

## 3. Threading

### Basic Threading

```python
import threading
import time

def worker(name, delay):
    print(f"{name} starting")
    time.sleep(delay)
    print(f"{name} finished")

# Create threads
thread1 = threading.Thread(target=worker, args=("Thread-1", 2))
thread2 = threading.Thread(target=worker, args=("Thread-2", 1))

# Start threads
thread1.start()
thread2.start()

# Wait for completion
thread1.join()
thread2.join()

print("All threads completed")
```

### Thread with Return Value

```python
import threading

def calculate_square(number, results, index):
    """Store result in shared list"""
    results[index] = number * number

results = [None, None, None]
threads = []

numbers = [5, 10, 15]
for i, num in enumerate(numbers):
    thread = threading.Thread(target=calculate_square, args=(num, results, i))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(results)  # [25, 100, 225]
```

### Thread Safety - The Problem

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1  # NOT thread-safe!

threads = [threading.Thread(target=increment) for _ in range(10)]

for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(counter)  # Probably not 1,000,000! (race condition)
```

### Locks for Thread Safety

```python
import threading

counter = 0
lock = threading.Lock()

def increment_safe():
    global counter
    for _ in range(100000):
        with lock:  # Acquire lock
            counter += 1
        # Lock automatically released

threads = [threading.Thread(target=increment_safe) for _ in range(10)]

for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(counter)  # Exactly 1,000,000!
```

### RLock (Reentrant Lock)

```python
import threading

class Counter:
    def __init__(self):
        self.count = 0
        self.lock = threading.RLock()  # Can be acquired multiple times by same thread
    
    def increment(self):
        with self.lock:
            self.count += 1
            self.check_limit()  # Can acquire lock again
    
    def check_limit(self):
        with self.lock:  # Same thread can acquire again
            if self.count > 100:
                print("Limit exceeded!")
```

### Semaphore (Limit Concurrent Access)

```python
import threading
import time

# Allow max 3 threads to access resource simultaneously
semaphore = threading.Semaphore(3)

def access_resource(thread_id):
    print(f"Thread {thread_id} waiting...")
    with semaphore:
        print(f"Thread {thread_id} accessing resource")
        time.sleep(2)
        print(f"Thread {thread_id} releasing resource")

threads = [threading.Thread(target=access_resource, args=(i,)) 
           for i in range(10)]

for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

### Thread-Safe Queue

```python
import threading
import queue
import time

def producer(q):
    for i in range(5):
        item = f"item-{i}"
        q.put(item)
        print(f"Produced {item}")
        time.sleep(0.5)
    q.put(None)  # Sentinel to signal completion

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consumed {item}")
        time.sleep(1)
        q.task_done()

# Thread-safe queue
q = queue.Queue()

prod_thread = threading.Thread(target=producer, args=(q,))
cons_thread = threading.Thread(target=consumer, args=(q,))

prod_thread.start()
cons_thread.start()

prod_thread.join()
cons_thread.join()
```

### ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def download_file(url):
    """Simulate downloading"""
    print(f"Downloading {url}")
    time.sleep(2)
    return f"Content from {url}"

urls = [f"http://example.com/file{i}" for i in range(5)]

# Create thread pool
with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit tasks
    future_to_url = {executor.submit(download_file, url): url 
                     for url in urls}
    
    # Process as they complete
    for future in as_completed(future_to_url):
        url = future_to_url[future]
        try:
            result = future.result()
            print(f"Downloaded {url}: {len(result)} bytes")
        except Exception as e:
            print(f"Error downloading {url}: {e}")
```

---

## 4. Multiprocessing

### Basic Multiprocessing

```python
import multiprocessing
import time

def worker(name, delay):
    print(f"{name} starting in process {multiprocessing.current_process().name}")
    time.sleep(delay)
    print(f"{name} finished")

if __name__ == "__main__":  # Required on Windows!
    process1 = multiprocessing.Process(target=worker, args=("Process-1", 2))
    process2 = multiprocessing.Process(target=worker, args=("Process-2", 1))
    
    process1.start()
    process2.start()
    
    process1.join()
    process2.join()
    
    print("All processes completed")
```

### Process with Return Value

```python
import multiprocessing

def calculate_square(number):
    return number * number

if __name__ == "__main__":
    numbers = [5, 10, 15, 20]
    
    # Create process pool
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(calculate_square, numbers)
    
    print(results)  # [25, 100, 225, 400]
```

### Process Pool for CPU-Intensive Tasks

```python
import multiprocessing
import time

def cpu_intensive_task(n):
    """Simulate heavy computation"""
    count = 0
    for i in range(n):
        count += i ** 2
    return count

if __name__ == "__main__":
    numbers = [5000000] * 8
    
    # Sequential
    start = time.time()
    results = [cpu_intensive_task(n) for n in numbers]
    sequential_time = time.time() - start
    
    # Parallel
    start = time.time()
    with multiprocessing.Pool() as pool:
        results = pool.map(cpu_intensive_task, numbers)
    parallel_time = time.time() - start
    
    print(f"Sequential: {sequential_time:.2f}s")
    print(f"Parallel: {parallel_time:.2f}s")
    print(f"Speedup: {sequential_time / parallel_time:.2f}x")
```

### Inter-Process Communication - Queue

```python
import multiprocessing

def producer(q):
    for i in range(5):
        q.put(f"item-{i}")
        print(f"Produced item-{i}")

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consumed {item}")

if __name__ == "__main__":
    q = multiprocessing.Queue()
    
    prod = multiprocessing.Process(target=producer, args=(q,))
    cons = multiprocessing.Process(target=consumer, args=(q,))
    
    prod.start()
    cons.start()
    
    prod.join()
    q.put(None)  # Signal consumer to stop
    cons.join()
```

### Shared Memory

```python
import multiprocessing

def increment_shared(shared_value, lock):
    for _ in range(100000):
        with lock:
            shared_value.value += 1

if __name__ == "__main__":
    # Shared memory
    shared_value = multiprocessing.Value('i', 0)  # 'i' = integer
    lock = multiprocessing.Lock()
    
    processes = [
        multiprocessing.Process(target=increment_shared, 
                              args=(shared_value, lock))
        for _ in range(4)
    ]
    
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    
    print(f"Final value: {shared_value.value}")  # 400,000
```

### ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_data(data):
    """CPU-intensive processing"""
    result = sum(i ** 2 for i in range(data))
    return result

if __name__ == "__main__":
    data = [1000000, 2000000, 3000000, 4000000]
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        future_to_data = {executor.submit(process_data, d): d 
                         for d in data}
        
        for future in as_completed(future_to_data):
            data_value = future_to_data[future]
            try:
                result = future.result()
                print(f"Processed {data_value}: {result}")
            except Exception as e:
                print(f"Error: {e}")
```

---

## 5. Choosing the Right Tool

### Decision Tree

```
Is your task I/O-bound (waiting for network, disk, etc.)?
  YES → Use Threading or Async
    Many concurrent I/O operations? → Async
    Mix of I/O and CPU? → Threading
  
  NO → Is it CPU-bound (heavy computation)?
    YES → Use Multiprocessing
      Independent tasks? → Process Pool
      Shared state needed? → Processes with shared memory
```

### Comparison Table

| Feature | Threading | Multiprocessing | Async |
|---------|-----------|----------------|-------|
| **GIL Impact** | Yes | No | Yes |
| **Memory** | Shared | Separate | Shared |
| **Overhead** | Low | High | Very Low |
| **Best For** | I/O-bound | CPU-bound | I/O-bound |
| **Debugging** | Hard | Harder | Medium |
| **Scaling** | Limited | Good | Excellent |

### Example Comparison

```python
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_task(n):
    return sum(i ** 2 for i in range(n))

def io_task(n):
    time.sleep(n)
    return n

if __name__ == "__main__":
    # CPU-bound task
    print("CPU-bound task:")
    
    # Threading (slow - GIL)
    start = time.time()
    with ThreadPoolExecutor(4) as executor:
        list(executor.map(cpu_task, [5000000] * 4))
    print(f"Threading: {time.time() - start:.2f}s")
    
    # Multiprocessing (fast - no GIL)
    start = time.time()
    with ProcessPoolExecutor(4) as executor:
        list(executor.map(cpu_task, [5000000] * 4))
    print(f"Multiprocessing: {time.time() - start:.2f}s")
    
    # I/O-bound task
    print("\nI/O-bound task:")
    
    # Threading (fast - GIL released during I/O)
    start = time.time()
    with ThreadPoolExecutor(4) as executor:
        list(executor.map(io_task, [1] * 4))
    print(f"Threading: {time.time() - start:.2f}s")
```

---

## Exercises

### Level 1: Basic

1. **Simple Threading**
   - Create 3 threads
   - Each prints its name
   - Wait for all to complete

2. **Download Simulator**
   - Simulate downloading 5 files
   - Use threading
   - Print progress

3. **Counter with Lock**
   - Multiple threads increment counter
   - Use lock for safety
   - Verify final count

### Level 2: Intermediate

4. **Producer-Consumer**
   - Producer generates items
   - Consumer processes items
   - Use Queue

5. **Thread Pool**
   - Process 10 URLs
   - Max 3 concurrent
   - Use ThreadPoolExecutor

6. **Process Pool**
   - Calculate primes in range
   - Use multiprocessing
   - Compare with sequential

### Level 3: Challenging

7. **Web Scraper**
   - Scrape multiple pages
   - Threading for I/O
   - Rate limiting

8. **Image Processor**
   - Process images in parallel
   - Use multiprocessing
   - Progress tracking

9. **Complete System**
   - Mix of I/O and CPU tasks
   - Threading + Multiprocessing
   - Proper synchronization

---

## Key Takeaways

✅ **Concurrency vs Parallelism**:
- Concurrency: Task switching
- Parallelism: Simultaneous execution

✅ **GIL**:
- Limits Python threads to one at a time
- Released during I/O operations
- Doesn't affect multiprocessing

✅ **Threading**:
- Good for I/O-bound tasks
- Shared memory
- Lower overhead
- Use locks for thread safety

✅ **Multiprocessing**:
- Good for CPU-bound tasks
- Separate memory
- Higher overhead
- No GIL limitations

✅ **Best Practices**:
- Choose right tool for task type
- Use thread/process pools
- Avoid shared state when possible
- Handle exceptions properly

---

Continue to [Part-11-Async-Programming](../Part-11-Async-Programming/README.md)!
