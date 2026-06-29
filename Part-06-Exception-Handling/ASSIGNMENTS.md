# Part 6: Exception Handling - Assignments

## Assignment Guidelines

- **Estimated time:** 10-14 hours total
- **Prerequisites:** Parts 1-5 complete
- **Submission:** Python package with logging output samples and test data (valid + corrupt files)
- **Rules:** Use specific exceptions; custom exception hierarchy; context managers throughout

---

## Assignment 1: Robust Data Ingestion Pipeline

### Scenario

Build a batch processor that ingests mixed-format data files (CSV, JSON, line-delimited logs), validates records, and writes clean output. Production pipelines must never crash silently — every failure mode is handled deliberately.

### Requirements

**Custom exception hierarchy:**

```python
class PipelineError(Exception): ...
class ValidationError(PipelineError): ...
class ParseError(PipelineError): ...
class FileAccessError(PipelineError): ...
class ConfigurationError(PipelineError): ...
```

Each custom exception stores: `message`, `source_file`, `line_number` (optional), `original_exception` (for chaining).

**Core components:**

1. **`Config` context manager** — loads config dict from JSON file; raises `ConfigurationError` if missing keys; logs load/close

2. **`read_file(path)`** — handles `FileNotFoundError`, `PermissionError`; returns content or raises `FileAccessError` with `raise ... from e`

3. **`parse_csv_line(line, line_no)`** — raises `ParseError` with line number on malformed data

4. **`validate_record(record)`** — raises `ValidationError` subclasses:
   - `InvalidEmailError`
   - `InvalidAgeError`
   - `MissingFieldError`

5. **`process_file(path)`** structure:

```python
try:
    content = read_file(path)
except FileAccessError as e:
    log error; return ProcessingResult(failed=True, ...)
else:
    # parsing succeeded
finally:
    # update statistics, close resources
```

6. **`BatchProcessor` context manager:**
   - On enter: initialize stats (`processed`, `failed`, `skipped`)
   - On exit: write summary report even if exception occurred
   - On exception inside: rollback in-memory buffer (transaction-style all-or-nothing per file)

7. **Retry logic:** `retry_operation(func, max_attempts=3, delay=1)` for simulated flaky network read (mock with random failure)

8. **Validation chain:** validate email → age → phone; collect ALL errors (don't stop at first) using a list, raise `ValidationError` with `errors: list` if any fail

9. **Logging:** configure `logging` module — INFO for success, WARNING for skipped, ERROR for failures, DEBUG for parse details

10. **CLI:** process directory of files; continue on single file failure (don't abort batch)

### Technical Specifications

- try/except/else/finally
- Specific exception catching (not bare `except:`)
- Exception hierarchy and custom exceptions
- Exception chaining (`raise X from Y`)
- EAFP vs LBYL — prefer try/except for file/parse operations
- Context managers (`with`, custom `__enter__`/`__exit__`)
- `contextlib.contextmanager` for at least one manager
- Logging integration

### Acceptance Criteria

- [ ] Corrupt file doesn't crash batch; logged and skipped
- [ ] Missing file raises `FileAccessError` with chained cause
- [ ] Validation reports multiple errors per record when applicable
- [ ] `BatchProcessor` summary written in `finally`/`__exit__`
- [ ] Transaction rollback: partial records not committed on mid-file failure
- [ ] Retry succeeds on 3rd attempt in test scenario
- [ ] Log file contains timestamped entries at 3+ levels

### Bonus Challenges

- `suppress` context manager from `contextlib` for optional fields
- Dead letter queue: write failed records to `failed/` directory with error metadata
- Exponential backoff in retry: 1s, 2s, 4s

### Hints

- `__exit__` receives exc_type, exc_val, exc_tb; return False to re-raise
- Validation collector: `errors = []; errors.append(...)` then `if errors: raise ValidationError(errors)`
- Use `logging.exception()` inside except blocks for stack traces

---

## Assignment 2: User Registration & Authentication Service

### Scenario

Implement a terminal-based registration/login system with exhaustive validation and error handling — simulating what happens before data hits a database.

### Requirements

1. **Exception types:**
   - `AuthError` (base)
   - `UserAlreadyExistsError`, `InvalidCredentialsError`, `AccountLockedError`, `WeakPasswordError`

2. **Validation functions** (each raises specific exception):
   - Email format (basic regex or rules)
   - Password strength (8+ chars, upper, lower, digit, special)
   - Username (3-20 alphanumeric)
   - Age 13-120

3. **Registration flow:**
   - try/except each validation; display user-friendly messages
   - `else` block: create user on full success
   - `finally` block: log attempt (success/failure) to `auth.log`

4. **Login flow:**
   - Track failed attempts in dict; lock after 5 failures (`AccountLockedError`)
   - Reset counter on success

5. **Context manager `auth_session(user)`:**
   - Yields user object while "logged in"
   - Ensures logout in `__exit__`
   - Raises if session already active

6. **File persistence context manager `user_store(path)`:**
   - Loads users JSON on enter
   - Saves on clean exit
   - Does NOT save if exception occurred during session (rollback)

7. **Simulated API client `ExternalEmailService.send()`:**
   - Randomly raises `ConnectionError`, `TimeoutError`
   - Caller implements retry with exponential backoff and logs each attempt

### Technical Specifications

- Full exception handling patterns from Part 6
- Multiple except blocks and exception tuples: `except (ValueError, TypeError) as e`
- Custom exception attributes accessed in handlers
- Context managers for resources and transactions

### Acceptance Criteria

- [ ] Weak password rejected with specific reasons listed
- [ ] Account locks after 5 failed logins
- [ ] User store rollback on mid-session crash (test by raising after register)
- [ ] External email retry logs 3 attempts before giving up
- [ ] All exceptions inherit from `AuthError` where appropriate
- [ ] No bare `except:` clauses

### Bonus Challenges

- Exception group handling (Python 3.11+) for batch validation
- `warnings.warn()` for deprecated username formats
- Audit trail context manager nesting: `with user_store(), audit_log():`

### Hints

- Password rules: collect failures in list, raise `WeakPasswordError` with details
- `failed_attempts.setdefault(username, 0)`
- `user_store.__exit__`: only save if `exc_type is None`

---

## Assignment 3: Safe Calculator & Expression Evaluator

### Scenario

Build a calculator that parses and evaluates math expressions from user input. Invalid input, division by zero, and overflow must all be handled gracefully with custom errors.

### Requirements

1. **Custom exceptions:** `CalculatorError`, `SyntaxError` (custom, not builtin shadow — name it `ExpressionSyntaxError`), `DivisionByZeroError`, `OverflowError` (custom)

2. **Tokenizer and parser** (simple: split tokens or recursive descent for `+,-,*,/`)

3. **Evaluation with try/except at each level:**
   - Tokenize errors → `ExpressionSyntaxError`
   - Unknown operator → `CalculatorError`
   - Division by zero → `DivisionByZeroError`
   - Result too large → custom `OverflowError`

4. **Context manager `calculation_context`:** sets precision mode (normal/scientific); restores on exit

5. **History file context manager:** append each successful calculation; handle `IOError`

6. **REPL:** continues after errors; displays error type and message; never crashes

7. **Use `else`:** only add to history if evaluation succeeded
8. **Use `finally`:** reset "last result" display flag

### Technical Specifications

- Exception hierarchy
- try/except/else/finally in one cohesive app
- Context managers for precision and file history
- User-friendly error messages mapping exception → message

### Acceptance Criteria

- [ ] `10 / 0` → `DivisionByZeroError` with clear message
- [ ] `10 + + 5` → syntax error
- [ ] REPL runs 10+ operations including errors without exiting
- [ ] History file contains only successful calculations
- [ ] Context manager restores precision mode after exception

### Bonus Challenges

- Variables: `x = 5` then `x + 3` with `NameError` handling
- Parentheses support with nested parse error messages including position
- `atexit` or `finally` to flush history on Ctrl+C

### Hints

- Tokenize: `import re; re.findall(r'\d+\.?\d*|[+\-*/()]', expr)`
- Map custom exceptions to messages in dict at REPL level
- Don't name your class `SyntaxError` — use `ExpressionSyntaxError`
