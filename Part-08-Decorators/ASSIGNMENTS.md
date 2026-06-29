# Part 8: Decorators - Assignments

## Assignment Guidelines

- **Estimated time:** 12-16 hours total
- **Prerequisites:** Parts 1-7 complete
- **Submission:** Python package `decorator_toolkit` with demo app and composition examples
- **Rules:** Use `@functools.wraps` on all decorators; demonstrate stacking and decorator factories

---

## Assignment 1: Composable Decorator Toolkit

### Scenario

Build a production-style decorator library used to cross-cut concerns (logging, caching, auth, rate limiting) across business functions — similar to what frameworks provide under the hood.

### Requirements

Implement each decorator in `decorator_toolkit/`:

1. **`@log_calls`** — log function name, args, kwargs, return value, execution time (use `logging`)

2. **`@log_calls(level=logging.DEBUG)`** — parameterized decorator factory

3. **`@timer`** — print or log elapsed time; store time in `func.last_duration` attribute

4. **`@memoize`** — cache based on `*args, **kwargs` (hashable only); expose `cache_info()` and `cache_clear()` on wrapped function

5. **`@retry(max_attempts=3, delay=1.0, exceptions=(Exception,))`** — exponential backoff optional via `backoff=2.0`

6. **`@rate_limit(calls=10, period=60)`** — sliding window using timestamps list in closure

7. **`@validate_types`** — check argument types against annotations at runtime (use `inspect.signature` + `typing.get_type_hints`)

8. **`@require_auth(roles: list[str] | None = None)`** — checks `kwargs.get("current_user")` or thread-local; raises `PermissionError`

9. **`@deprecated(reason: str)`** — emit `warnings.warn` on each call

10. **`@singleton`** — class decorator ensuring one instance

11. **`@register_route(path)`** — class decorator storing routes on class `_routes` dict (mini framework)

12. **Class-based decorator `@CountCalls`** — implements `__init__` and `__call__`

13. **Async versions:** `@async_timer`, `@async_retry` using `asyncio.sleep`

14. **Composition demo:**

```python
@log_calls()
@timer
@memoize
@retry(max_attempts=2)
def expensive_fetch(user_id: int) -> dict: ...
```

15. **Conditional decorator factory `@debug_only(decorator)`** — applies decorator only if `DEBUG=True`

### Technical Specifications

- Function decorators with `@wraps`
- Decorators with arguments (three-level nesting)
- Stacking decorators (order matters — document in README)
- Class decorators
- Class-based decorators
- Built-in decorators: demonstrate `@property`, `@staticmethod`, `@classmethod` in example model class
- `functools.lru_cache` comparison section in README vs custom `@memoize`
- Preserve function metadata (`__name__`, `__doc__`)

### Acceptance Criteria

- [ ] All 12+ decorators implemented and tested in demo
- [ ] `@wraps` used everywhere; wrapped function shows original `__name__`
- [ ] `@memoize` returns cached result on second identical call (prove with counter)
- [ ] `@rate_limit` blocks after N calls within period
- [ ] `@retry` succeeds after transient failures in test
- [ ] Stacked decorators work together on `expensive_fetch`
- [ ] Class decorator `@singleton` returns same instance
- [ ] Async decorators work on `async def` functions

### Bonus Challenges

- `@circuit_breaker(failure_threshold=5, recovery_timeout=30)`
- Decorator that accepts both `@tracked` and `@tracked()` syntax
- `parametrize(**kwargs)` decorator injecting fixed kwargs

### Hints

- Decorator factory pattern:

```python
def retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ...
        return wrapper
    return decorator
```

- Rate limit: store `calls = []` timestamps; prune older than `period`
- `singleton`: override `__new__` or store instance in closure dict

---

## Assignment 2: Mini Web Framework Using Decorators

### Scenario

Create `microapi` — a tiny WSGI/ASGI-style router where routes, middleware, and error handlers are registered exclusively via decorators.

### Requirements

1. **`@app.route(path, methods=["GET"])`** — register handler in global/app registry

2. **`@app.before_request`** — runs before each handler; can abort with response

3. **`@app.after_request`** — modify response; must use `@wraps` and call handler

4. **`@app.error_handler(ExceptionType)`** — register error handlers

5. **`@require_json`** — validates Content-Type; parses body or raises 400

6. **`@require_methods("POST", "PUT")`** — method check decorator

7. **`@with_db_session`** — injects `db` kwarg; closes session in finally (mock DB)

8. **`RouteRegistry` class** with decorator methods:

```python
app = RouteRegistry()

@app.get("/users")
def list_users(): ...

@app.post("/users")
@require_json
def create_user(data): ...
```

9. **Dispatch function `app.handle(method, path, **kwargs)`** — finds route, runs before hooks, handler, after hooks

10. **Decorator order documentation:** demonstrate wrong vs right order for `@route` + `@auth`

11. **Class-based view:**

```python
@register_controller("/products")
class ProductController:
    @get("/")
    def list(self): ...
    
    @post("/")
    @require_json
    def create(self, data): ...
```

12. **Test suite** (manual asserts ok): 10 routes, middleware runs, error handler catches

### Technical Specifications

- All decorator patterns from Part 8
- Registry pattern with decorators
- Middleware as decorator chain
- Class decorators for controller registration
- `@wraps` throughout

### Acceptance Criteria

- [ ] Routes registered via decorators dispatch correctly
- [ ] `before_request` can short-circuit request
- [ ] `error_handler` catches typed exception and returns error response dict
- [ ] `require_json` rejects non-JSON requests
- [ ] Class-based controller routes work
- [ ] README includes decorator stacking order explanation

### Bonus Challenges

- URL parameters: `@app.route("/users/<int:user_id>")` parsing
- CORS middleware decorator
- Generate OpenAPI-like route manifest from registry

### Hints

- Registry: `routes[(method, path)] = func`
- Before hooks: list of functions called in registration order
- Class routes: register bound methods on instantiation or via metaclass

---

## Assignment 3: Performance Monitoring Suite

### Scenario

Build decorators and context managers that profile application performance — timing, memory, call counts — aggregating statistics for a report.

### Requirements

1. **`@profile`** — records per-function: call count, total time, min, max, avg (store in global `ProfilerStats` dict)

2. **`@profile` + `@profile.group("database")`** — optional group tag for categorized stats

3. **`MemoryTracker` class decorator** — tracks approximate memory delta per call (use `sys.getsizeof` on result or `tracemalloc` if available)

4. **`@trace`** — print indented call tree (track depth in thread-local or context var)

5. **`@limit_recursion(max_depth=100)`** — prevent runaway recursion

6. **`ProfilerReport` context manager:**
   - On exit: print formatted table of all `@profile` stats
   - Sort by total time descending

7. **`@deprecated` + `@profile` combo** on legacy functions in demo

8. **Property decorator exercise:**

```python
class Stats:
    @property
    def average_time(self) -> float: ...
    
    @average_time.setter
    def average_time(self, value): ...  # read-only with custom error
```

9. **`@lru_cache` vs `@memoize` benchmark** — document in report output

10. **Export:** `export_stats_json()` from profiler registry

### Technical Specifications

- Practical decorators: timing, logging, profiling
- Class-based and parameterized decorators
- Context managers combined with decorators
- Built-in `@property`, `@lru_cache`
- `@wraps` and metadata

### Acceptance Criteria

- [ ] Profiler captures 5+ functions in demo run
- [ ] Report shows call count and avg time correctly (verify with `time.sleep`)
- [ ] Grouped stats filterable by group name
- [ ] `ProfilerReport` prints on context exit even if exception raised
- [ ] `trace` shows nested call indentation
- [ ] JSON export contains all recorded functions

### Bonus Challenges

- Thread-safe profiler using `threading.Lock`
- `@sample(rate=0.1)` — profile only 10% of calls randomly
- Dashboard: simple ASCII bar chart of top 5 slowest functions

### Hints

- Stats key: `f"{func.__module__}.{func.__name__}"`
- Thread-local depth: `import threading; depth = threading.local()`
- `tracemalloc.start()` before/after for better memory stats
