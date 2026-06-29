# Part 3: Functions - Assignments

## Assignment Guidelines

- **Estimated time:** 10-14 hours total
- **Prerequisites:** Parts 1-2 complete
- **Submission:** Python module(s) with `if __name__ == "__main__"` demo block
- **Rules:** Focus on functions, scope, closures, and higher-order functions; decorators introduced lightly only as preview (full decorators in Part 8)

---

## Assignment 1: Data Transformation Pipeline Library

### Scenario

Build `transformkit` — a small library of composable functions for cleaning and transforming data records (like ETL preprocessing). Backend teams use it before sending data to APIs or databases.

### Requirements

Implement the following **as pure functions** where possible:

1. **Core transforms (each a function):**
   - `normalize_string(s)` — strip, lowercase, collapse multiple spaces
   - `parse_number(value, default=0)` — safely convert str/int/float to float
   - `clean_record(record: dict) -> dict` — apply normalizers to all string fields
   - `filter_records(records, predicate)` — higher-order filter using a predicate function
   - `map_records(records, mapper)` — apply mapper function to each record

2. **`*args` and `**kwargs`:**
   - `merge_records(*records, **defaults)` — merge multiple dicts; later keys override; defaults fill missing keys
   - `build_query(**filters)` — build a query string from keyword filters (skip `None` values)

3. **Lambda and HOF:**
   - `compose(*functions)` — return a function such that `compose(f, g)(x) == f(g(x))`
   - `pipe(value, *functions)` — left-to-right application: `pipe(x, f, g) == g(f(x))`
   - Provide 3 lambdas: `is_positive`, `double`, `to_string`

4. **Closures:**
   - `make_multiplier(factor)` — returns function that multiplies input by factor
   - `make_validator(min_val, max_val)` — returns function checking if value is in range
   - `make_counter(start=0)` — returns function that returns incremented count each call

5. **Default arguments pitfall demo:**
   - Include `append_to(element, target=[])` showing the mutable default bug
   - Fix with `target=None` pattern in `append_to_safe`

6. **Recursion:**
   - `flatten(nested_list)` — recursively flatten arbitrarily nested lists
   - `deep_get(data, *keys, default=None)` — safely traverse nested dicts

7. **Demo script** applying a pipeline to 10 sample user records:
   - Clean → filter active users → map to summary dict → merge with defaults

### Technical Specifications

- Function basics: definition, parameters, return values
- Positional, keyword, default, `*args`, `**kwargs`
- Lambda functions
- Scope: local, enclosing, global (demonstrate one careful `global` use with comment why it's avoided elsewhere)
- Closures and factory functions
- Higher-order functions: `map`, `filter` (built-in) and custom
- Function composition
- Recursion
- Docstrings on all public functions

### Acceptance Criteria

- [ ] At least 15 user-defined functions
- [ ] `compose` and `pipe` work with 3+ functions chained
- [ ] Closures maintain independent state (two counters don't share state)
- [ ] Mutable default bug demonstrated and fixed
- [ ] `flatten` handles 3+ levels of nesting
- [ ] Demo processes 10 records end-to-end with printed output
- [ ] No function exceeds ~25 lines (split if needed)

### Bonus Challenges

- Implement `curry_add(a, b=None, c=None)` supporting `curry_add(1)(2)(3) == 6`
- `memoize(func)` without using `functools.lru_cache` — dict-based cache
- `partial_apply(func, *fixed_args)` — bind arguments early

### Hints

- `compose` can use `reduce` or a simple loop: `result = f; for g in reversed(functions[1:]): ...`
- Closure counter: `def make_counter(): count = 0; def inc(): nonlocal count; count += 1; return count`
- Keep predicates as `Callable` conceptually even without type hints (Part 7)

---

## Assignment 2: Statistical Analysis Toolkit

### Scenario

Create a reusable statistics module for analyzing numeric datasets. Every calculation is a function; a orchestrator function ties them together.

### Requirements

1. **Single-responsibility functions:**
   - `mean`, `median`, `mode`, `variance`, `std_dev`, `min_max`, `percentile(data, p)`

2. **Functions returning functions:**
   - `get_aggregator(method_name: str)` — returns `mean`, `median`, or `sum` function by name; raises `ValueError` for unknown

3. **Variable arguments:**
   - `combine_stats(*datasets)` — return dict of stats for each dataset keyed by index
   - `summary_report(**named_datasets)` — stats for named datasets

4. **Nested functions:**
   - `analyze(data)` contains inner `validate()` and `compute()` functions
   - `validate` checks empty list, non-numeric values
   - `compute` calls other module functions

5. **Callback pattern:**
   - `apply_to_outliers(data, callback, threshold=2.0)` — find values beyond 2 std devs; call `callback(value)` for each

6. **Generator-style function (preview):**
   - `rolling_window(data, size)` — use `yield` to produce sliding windows (if not covered, use function returning list of windows)

7. **CLI driver** using functions only (no classes):
   - Read numbers from user until `done`
   - Print full summary report

### Technical Specifications

- Return values vs side effects (prefer returns)
- Keyword-only parameters for optional config: `def percentile(data, p, *, interpolate=True)`
- Unpacking in function calls
- Functions as first-class objects (store in dict registry)

### Acceptance Criteria

- [ ] `mean` and `median` match manual calculation on test data
- [ ] `get_aggregator("mean")(data)` works
- [ ] `summary_report` handles 3+ named datasets via `**kwargs`
- [ ] `analyze` rejects empty data with clear error
- [ ] `rolling_window([1,2,3,4,5], 3)` → `[1,2,3], [2,3,4], [3,4,5]`
- [ ] All functions have docstrings with parameter descriptions

### Bonus Challenges

- Implement `timing` decorator manually (preview Part 8) using nested function pattern
- `zip_stats(list_a, list_b)` — element-wise stats using `zip` inside functions
- Benchmark: function comparing loop-based vs built-in `sum` on large list

### Hints

- Median: sort copy of data; handle even/odd length
- Mode: `collections.Counter` allowed if introduced in Part 5 — otherwise manual dict counting
- Registry: `AGGREGATORS = {"mean": mean, "median": median}`

---

## Assignment 3: Mini Shell Command Parser

### Scenario

Build a simplified shell that parses command strings and dispatches to handler functions — mirroring how web frameworks route requests to handlers.

### Requirements

1. **Registry pattern:**
   - `register_command(name, handler)` — store in dict
   - `execute(line)` — parse line, lookup handler, call with args

2. **Parsing function:**
   - `parse_command(line) -> (command, args, kwargs)`
   - Support: `echo hello world`, `calc add 3 5`, `repeat 3 say hi`
   - Parse `--flag value` style kwargs optionally

3. **Built-in commands (each a function):**
   - `cmd_echo(*args)` — print args
   - `cmd_calc(operation, a, b)` — add/sub/mul/div
   - `cmd_repeat(n, *words)` — repeat print n times
   - `cmd_history()` — show last 10 commands (closure over history list)
   - `cmd_exit()` — return sentinel to stop REPL

4. **REPL:**
   - `run_shell()` — `while True` loop calling `execute`

5. **Error handling functions:**
   - `safe_execute(line)` — catch errors, return error message string (use try/except from Part 6 if available, else validate inputs)

6. **Higher-order registration:**
   - `require_args(n)` — returns decorator that validates arg count before calling handler (manual decorator pattern with nested functions)

### Technical Specifications

- All Part 3 function concepts integrated
- Functions stored in data structures
- Closures for command history
- Nested functions for parsing
- `*args`/`**kwargs` in handlers

### Acceptance Criteria

- [ ] Shell runs interactively with 5+ commands
- [ ] Unknown command prints helpful message
- [ ] `calc add 10 5` outputs `15`
- [ ] History tracks and displays commands
- [ ] `require_args` prevents wrong arg count
- [ ] Parsing handles multiple spaces between tokens

### Bonus Challenges

- Pipe syntax: `echo hello | repeat 2` (split and chain functions)
- Aliases: `register_alias("?", "help")`
- Completion: `list_commands(prefix)` filtering registry keys

### Hints

- `parts = line.split()` then `cmd, *args = parts[0], parts[1:]`
- History closure: list defined in outer scope of `run_shell`, mutated by `execute`
- Decorator without `@`: `handler = require_args(2)(handler)`
