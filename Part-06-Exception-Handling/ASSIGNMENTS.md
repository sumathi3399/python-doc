# Part 6: Exception Handling - Practice Problems

> Test try/except, custom exceptions, context managers

---

## Problem 1: Basic Try-Except

**Task**: Safe division
```python
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Cannot divide by zero"

assert safe_divide(10, 2) == 5
assert safe_divide(10, 0) == "Cannot divide by zero"
```

**Time**: 10 minutes

---

## Problem 2: Multiple Exceptions

**Task**: Safe conversion
```python
def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return "Invalid number"
    except TypeError:
        return "Wrong type"

assert safe_int("42") == 42
assert safe_int("abc") == "Invalid number"
assert safe_int(None) == "Wrong type"
```

**Time**: 10 minutes

---

## Problem 3: Finally Block

**Task**: File reading with cleanup
```python
def read_file(filename):
    try:
        f = open(filename, 'r')
        content = f.read()
        return content
    except FileNotFoundError:
        return None
    finally:
        # Always close if opened
        if 'f' in locals():
            f.close()
```

**Time**: 15 minutes

---

## Problem 4: Else Clause

**Task**: Search with result message
```python
def find_item(items, target):
    try:
        index = items.index(target)
    except ValueError:
        return f"{target} not found"
    else:
        return f"Found {target} at index {index}"
```

**Time**: 10 minutes

---

## Problem 5: Custom Exception

**Task**: Create validation error
```python
class ValidationError(Exception):
    pass

def validate_age(age):
    if age < 0 or age > 150:
        raise ValidationError("Invalid age")
    return True

# Test it
```

**Time**: 10 minutes

---

## Problem 6: Exception Chaining

**Task**: Add context to errors
```python
def process_data(data):
    try:
        result = int(data) / 10
    except (ValueError, ZeroDivisionError) as e:
        raise RuntimeError("Processing failed") from e
```

**Time**: 15 minutes

---

## Problem 7: Context Manager

**Task**: Use with statement
```python
# Read file using context manager
with open('test.txt', 'r') as f:
    content = f.read()
# File automatically closed
```

**Time**: 5 minutes

---

## Problem 8: Custom Context Manager

**Task**: Timer context
```python
import time

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        self.end = time.time()
        print(f"Elapsed: {self.end - self.start:.2f}s")

with Timer():
    time.sleep(1)
```

**Time**: 20 minutes

---

## Problem 9: Suppress Exceptions

**Task**: Ignore file not found
```python
from contextlib import suppress

# Don't crash if file doesn't exist
with suppress(FileNotFoundError):
    with open('missing.txt') as f:
        content = f.read()
```

**Time**: 10 minutes

---

## Problem 10: Assertion

**Task**: Input validation
```python
def set_age(age):
    assert 0 <= age <= 150, "Age must be 0-150"
    return age

# Test valid and invalid
```

**Time**: 5 minutes

---

## Summary Check

**8+ solved** → Exception handling mastered  
**5-7 solved** → Practice custom exceptions and context managers  
**< 5 solved** → Review try/except patterns
