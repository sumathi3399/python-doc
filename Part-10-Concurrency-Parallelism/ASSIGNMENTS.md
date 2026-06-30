# Part 10: Concurrency & Parallelism - Practice Problems

> Test threading, multiprocessing, GIL understanding

---

## Problem 1: Basic Thread

**Task**: Run function in thread
```python
import threading
import time

def worker(name):
    print(f"{name} starting")
    time.sleep(1)
    print(f"{name} done")

thread = threading.Thread(target=worker, args=("Worker-1",))
thread.start()
thread.join()
```

**Time**: 10 minutes

---

## Problem 2: Multiple Threads

**Task**: Run 3 workers concurrently
```python
import threading

def worker(num):
    print(f"Worker {num}")

threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

**Time**: 15 minutes

---

## Problem 3: Thread with Lock

**Task**: Safe counter increment
```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(1000):
        with lock:
            counter += 1

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # Should be 5000
```

**Time**: 20 minutes

---

## Problem 4: Queue for Thread Communication

**Task**: Producer-consumer
```python
import threading
import queue
import time

q = queue.Queue()

def producer():
    for i in range(5):
        q.put(i)
        time.sleep(0.1)

def consumer():
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consumed {item}")
        q.task_done()

threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
```

**Time**: 20 minutes

---

## Problem 5: ThreadPoolExecutor

**Task**: Process URLs concurrently
```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch(url):
    time.sleep(0.5)  # Simulate I/O
    return f"Fetched {url}"

urls = ["url1", "url2", "url3"]
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(fetch, urls)
    for result in results:
        print(result)
```

**Time**: 15 minutes

---

## Problem 6: Basic Process

**Task**: CPU-bound in separate process
```python
import multiprocessing

def compute(n):
    return sum(i*i for i in range(n))

if __name__ == "__main__":
    process = multiprocessing.Process(target=compute, args=(1000000,))
    process.start()
    process.join()
```

**Time**: 10 minutes

---

## Problem 7: ProcessPoolExecutor

**Task**: Parallel computation
```python
from concurrent.futures import ProcessPoolExecutor

def square(n):
    return n * n

if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5]
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(square, numbers))
    print(results)  # [1, 4, 9, 16, 25]
```

**Time**: 15 minutes

---

## Problem 8: GIL Understanding

**Task**: Compare threading vs multiprocessing for CPU
```python
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_task():
    return sum(i*i for i in range(1000000))

if __name__ == "__main__":
    # Threading (GIL limits)
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda _: cpu_task(), range(4)))
    print(f"Threading: {time.time() - start:.2f}s")
    
    # Multiprocessing (no GIL)
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda _: cpu_task(), range(4)))
    print(f"Multiprocessing: {time.time() - start:.2f}s")
```

**Time**: 20 minutes

---

## Problem 9: Semaphore

**Task**: Limit concurrent access
```python
import threading
import time

semaphore = threading.Semaphore(2)  # Max 2 at a time

def access_resource(num):
    with semaphore:
        print(f"Worker {num} accessing")
        time.sleep(1)
        print(f"Worker {num} done")

threads = [threading.Thread(target=access_resource, args=(i,)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

**Time**: 15 minutes

---

## Problem 10: When to Use What

**Task**: Choose correct tool
```
Choose threading or multiprocessing:

1. Web scraping 100 URLs: ________
2. Computing prime numbers: ________
3. Reading 50 files: ________
4. Image processing: ________
5. API requests: ________

Answers: 1=threading, 2=multiprocessing, 3=threading, 4=multiprocessing, 5=threading
```

**Time**: 5 minutes

---

## Summary Check

**8+ solved** → Concurrency mastered  
**5-7 solved** → Practice GIL and pools  
**< 5 solved** → Review threading vs multiprocessing
