# Part 10: Concurrency & Parallelism - Assignments

## Assignment Guidelines

- **Estimated time:** 12-16 hours total
- **Prerequisites:** Parts 1-9 complete
- **Submission:** Python project with benchmark scripts and thread-safety demonstrations
- **Rules:** Justify threading vs multiprocessing choices; use proper synchronization

---

## Assignment 1: Concurrent Web Scraper & Data Pipeline

### Scenario

Build a web scraper that fetches 50+ URLs (use mock HTTP server or `httpbin.org`), parses titles/metadata, and writes results to CSV. I/O-bound work should use threading; demonstrate GIL behavior vs multiprocessing on a CPU-bound comparison task.

### Requirements

**Part A — Threaded scraper (I/O-bound):**

1. **`fetch_url(url) -> dict`** — simulate or real HTTP with `requests`/`urllib`; include status, title, response time
2. **`ThreadPoolExecutor`** — scrape URLs with `max_workers` configurable (4, 8, 16)
3. **Rate limiter** — max 5 concurrent requests using `threading.Semaphore`
4. **Shared results list** — protect with `threading.Lock` when appending
5. **Progress tracker** — thread-safe counter with `Lock` or `atomic` operations
6. **Producer-consumer** — one thread reads URLs from `queue.Queue`, workers consume
7. **Error handling** — failed URLs logged; don't stop batch
8. **Compare sequential vs threaded** — print timing table

**Part B — CPU-bound comparison:**

1. **`is_prime(n)`** or hash computation on large data
2. Run on 4 large numbers sequentially vs `ProcessPoolExecutor`
3. Run same with `ThreadPoolExecutor` — document GIL effect in README (threads slower or similar)
4. **`multiprocessing.Queue`** — workers return results via queue

**Part C — Mixed workload:**

1. Scrape URLs (threads) → extract IDs → compute expensive hash per ID (processes)
2. Orchestrate with `concurrent.futures.as_completed`

**Thread safety proof:**

- Demonstrate **broken** counter without lock (optional race demo with high iteration)
- Fix with `Lock` — show correct final count

### Technical Specifications

- `threading.Thread`, `Lock`, `Semaphore`, `Queue`
- `multiprocessing.Process`, `Pool`, `ProcessPoolExecutor`, `Queue`
- `concurrent.futures.ThreadPoolExecutor`, `ProcessPoolExecutor`, `as_completed`
- GIL understanding documented
- Choosing threading vs multiprocessing

### Acceptance Criteria

- [ ] 50 URLs processed with threaded path
- [ ] Rate limiting prevents more than 5 concurrent fetches
- [ ] Threaded scrape faster than sequential (on network or mock delay)
- [ ] Process pool faster than threads on CPU-bound task
- [ ] No lost results due to race conditions (lock used)
- [ ] Producer-consumer processes all URLs
- [ ] README explains GIL with measured timings

### Bonus Challenges

- `threading.Barrier` — all workers sync before writing final report
- `multiprocessing.Manager` for shared dict
- Graceful shutdown on `KeyboardInterrupt` with thread join timeout

### Hints

- Mock delay: `time.sleep(0.1)` in fetch simulates I/O
- `with lock: results.append(...)`
- CPU task: sum of primes up to large N per worker

---

## Assignment 2: Parallel Image & File Processor

### Scenario

Process a directory of files: resize images (CPU-heavy if using PIL), compute SHA-256 hashes, and generate manifest. Use multiprocessing for CPU work and threading for I/O-bound manifest writing.

### Requirements

1. **Input:** 20+ image files (or generate with PIL) + 20 text files

2. **CPU stage (process pool):**
   - Resize images to thumbnail (multiprocessing)
   - Compute SHA-256 of each file (multiprocessing)
   - `chunksize` tuning experiment — document optimal chunk size

3. **I/O stage (thread pool):**
   - Write manifest JSON lines concurrently
   - Thread-safe write to single manifest with lock OR one file per worker merged at end

4. **`multiprocessing.Pool` with `imap_unordered`** — process files with progress bar (print counts)

5. **Shared state:** use `multiprocessing.Value` for processed counter

6. **Error isolation:** corrupt file doesn't crash pool; errors collected in `Manager().list()`

7. **Benchmark script:** compare 1, 2, 4, 8 workers; plot or table in README

8. **`if __name__ == "__main__"` guard** — required for multiprocessing on Windows/macOS

### Technical Specifications

- Process pools for CPU-bound
- Thread pools for I/O-bound
- Synchronization primitives
- Shared memory basics (`Value`, `Manager`)
- Exception handling in workers

### Acceptance Criteria

- [ ] All images resized to `thumbnails/` directory
- [ ] SHA-256 manifest matches independent verification
- [ ] Parallel faster than serial on 20+ files
- [ ] Worker errors reported in error log file
- [ ] `if __name__ == "__main__"` present
- [ ] chunksize experiment documented with numbers

### Bonus Challenges

- Pipeline: process pool → thread pool via `Queue` between stages
- Memory limit: don't load all files at once — stream processing
- `concurrent.futures.wait` with `FIRST_EXCEPTION` policy

### Hints

- PIL resize in worker function at module level (picklable)
- `hashlib.sha256()` read file in chunks
- Manager list for errors: `errors.append()` in except block in worker

---

## Assignment 3: Real-Time Log Stream Processor

### Scenario

Simulate a high-volume log stream (generator producing 10,000 lines/sec) with multiple consumer threads aggregating metrics in real time, while a separate process computes heavy anomaly detection on windows of data.

### Requirements

1. **Producer thread** — generates log lines with timestamp, level, message, user_id; puts on `queue.Queue(maxsize=1000)`

2. **Consumer threads (3):** parse logs, update shared metrics:
   - Count per level (ERROR, WARN, INFO)
   - Count per user_id
   - Use `defaultdict` + `Lock` OR `multiprocessing.Manager().dict()` if crossing processes

3. **Backpressure:** producer blocks when queue full; log backpressure events

4. **Anomaly process (separate process):**
   - Receives batches via `multiprocessing.Queue`
   - Runs statistical anomaly detection (e.g., ERROR rate > 3x rolling average)
   - Sends alerts back via another queue

5. **Coordinator thread:**
   - Every 5 seconds, snapshot metrics and print dashboard
   - On shutdown (`threading.Event`), signal all threads to stop

6. **`join` with timeout** — ensure clean shutdown within 10 seconds

7. **Deadlock avoidance:** document lock ordering if multiple locks used

8. **Performance report:** throughput (lines/sec), queue depth over time

### Technical Specifications

- Threading for stream processing (I/O/simulation bound)
- Multiprocessing for CPU-heavy anomaly detection
- `Queue`, `Event`, `Lock`, `Thread`, `Process`
- Graceful shutdown patterns
- GIL vs separate process for CPU work

### Acceptance Criteria

- [ ] 60+ seconds of simulated streaming without crash
- [ ] Metrics match manual count on small sample
- [ ] Anomaly process detects injected error spike
- [ ] Clean shutdown on Ctrl+C or stop signal
- [ ] Backpressure occurs when consumers slower than producer (demonstrate)
- [ ] README includes architecture diagram

### Bonus Challenges

- `ThreadPoolExecutor` for burst processing of ERROR lines only
- Priority queue for ERROR lines processed first
- Compare same anomaly detection in thread vs process with timings

### Hints

- `stop_event = threading.Event()` checked in loops
- Batch logs every N lines or every T seconds for anomaly process
- Inject spike: producer emits 50% ERROR for 2 seconds mid-run
