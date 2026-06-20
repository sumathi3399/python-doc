# Part 6: Exception Handling

> Learn to write robust code that gracefully handles errors and unexpected situations.

## 📚 Table of Contents

1. [Introduction to Exceptions](#1-introduction-to-exceptions)
2. [Try-Except Basics](#2-try-except-basics)
3. [Exception Hierarchy](#3-exception-hierarchy)
4. [Custom Exceptions](#4-custom-exceptions)
5. [Best Practices](#5-best-practices)
6. [Context Managers](#6-context-managers)
7. [Exercises](#exercises)

---

## 1. Introduction to Exceptions

### What is an Exception?

An exception is an event that disrupts normal program flow. Instead of crashing, Python allows you to **catch and handle** these errors.

```python
# Without exception handling - Program crashes
number = int("hello")  # ValueError: invalid literal
print("This never runs")

# With exception handling - Program continues
try:
    number = int("hello")
except ValueError:
    print("Invalid number!")
print("Program continues")  # This runs!
```

### Common Exceptions

```python
# ValueError - Invalid value
int("hello")  # Can't convert to int

# TypeError - Wrong type
"hello" + 5  # Can't add string and int

# KeyError - Key not in dictionary
person = {"name": "Alice"}
person["age"]  # Key doesn't exist

# IndexError - Index out of range
numbers = [1, 2, 3]
numbers[10]  # Index too large

# FileNotFoundError - File doesn't exist
open("nonexistent.txt")

# ZeroDivisionError - Division by zero
10 / 0

# AttributeError - Attribute doesn't exist
"hello".nonexistent_method()
```

---

## 2. Try-Except Basics

### Basic Try-Except

```python
try:
    # Code that might raise an exception
    result = 10 / 0
except ZeroDivisionError:
    # Handle the error
    print("Cannot divide by zero!")
```

### Catching Multiple Exceptions

```python
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("Cannot divide by zero!")
        return None
    except TypeError:
        print("Both arguments must be numbers!")
        return None

print(safe_divide(10, 2))    # 5.0
print(safe_divide(10, 0))    # Cannot divide by zero! None
print(safe_divide(10, "a"))  # Both arguments must be numbers! None
```

### Catching Multiple Exceptions (Same Handler)

```python
try:
    # Some operation
    value = int(input("Enter number: "))
    result = 100 / value
except (ValueError, ZeroDivisionError) as e:
    print(f"Error: {e}")
```

### Getting Exception Details

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error occurred: {e}")
    print(f"Error type: {type(e)}")
```

### The Else Clause

```python
try:
    value = int(input("Enter number: "))
except ValueError:
    print("Invalid input!")
else:
    # Runs ONLY if no exception occurred
    print(f"You entered: {value}")
```

### The Finally Clause

```python
file = None
try:
    file = open("data.txt", "r")
    content = file.read()
    print(content)
except FileNotFoundError:
    print("File not found!")
finally:
    # ALWAYS runs (cleanup code)
    if file:
        file.close()
        print("File closed")
```

### Complete Try-Except Structure

```python
try:
    # Try to do something
    result = risky_operation()
except SpecificError as e:
    # Handle specific error
    handle_error(e)
except AnotherError:
    # Handle another error
    handle_another_error()
else:
    # Runs if NO exception
    print("Success!")
finally:
    # ALWAYS runs (cleanup)
    cleanup()
```

---

## 3. Exception Hierarchy

### Python Exception Tree

```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── StopIteration
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   ├── FloatingPointError
    │   └── OverflowError
    ├── AssertionError
    ├── AttributeError
    ├── EOFError
    ├── ImportError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── NameError
    ├── OSError
    │   ├── FileNotFoundError
    │   └── PermissionError
    ├── RuntimeError
    ├── TypeError
    └── ValueError
```

### Catching Hierarchy

```python
# ❌ Bad: Catch broad exception first
try:
    result = 10 / 0
except Exception:  # Catches everything!
    print("Some error")
except ZeroDivisionError:  # Never reached
    print("Division by zero")

# ✅ Good: Catch specific first
try:
    result = 10 / 0
except ZeroDivisionError:  # Specific
    print("Division by zero")
except Exception:  # General (fallback)
    print("Some other error")
```

### Catching Base vs Specific

```python
try:
    numbers = [1, 2, 3]
    print(numbers[10])
except LookupError:  # Catches IndexError, KeyError
    print("Item not found")

try:
    result = 10 / 0
except ArithmeticError:  # Catches ZeroDivisionError, etc.
    print("Math error")
```

---

## 4. Custom Exceptions

### Creating Custom Exceptions

```python
class ValidationError(Exception):
    """Raised when validation fails"""
    pass

def validate_age(age):
    if age < 0:
        raise ValidationError("Age cannot be negative")
    if age > 150:
        raise ValidationError("Age too high")
    return age

try:
    validate_age(-5)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Custom Exceptions with Data

```python
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(f"Insufficient funds: ${balance} < ${amount}")

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    return balance - amount

try:
    new_balance = withdraw(100, 150)
except InsufficientFundsError as e:
    print(e)  # Insufficient funds: $100 < $150
    print(f"Your balance: ${e.balance}")
    print(f"Requested: ${e.amount}")
```

### Exception Hierarchy Example

```python
class DatabaseError(Exception):
    """Base class for database errors"""
    pass

class ConnectionError(DatabaseError):
    """Database connection failed"""
    pass

class QueryError(DatabaseError):
    """Query execution failed"""
    pass

def execute_query(query):
    if not connected:
        raise ConnectionError("Not connected to database")
    if not valid_query(query):
        raise QueryError(f"Invalid query: {query}")
    # Execute query...

try:
    execute_query("SELECT * FROM users")
except ConnectionError:
    print("Connection issue - retry later")
except QueryError:
    print("Fix your query")
except DatabaseError:
    print("Some database error")
```

---

## 5. Best Practices

### 1. Be Specific

```python
# ❌ Bad: Catching everything
try:
    data = json.loads(text)
except:  # Too broad!
    print("Error")

# ✅ Good: Catch specific exceptions
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
```

### 2. Don't Swallow Exceptions

```python
# ❌ Bad: Silent failure
try:
    critical_operation()
except Exception:
    pass  # Error hidden!

# ✅ Good: At least log it
try:
    critical_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise if needed
```

### 3. Use EAFP (Easier to Ask Forgiveness than Permission)

```python
# ❌ LBYL (Look Before You Leap) - Pythonic way less preferred
if key in dictionary:
    value = dictionary[key]
else:
    value = default

# ✅ EAFP (Pythonic way)
try:
    value = dictionary[key]
except KeyError:
    value = default

# Or even better: use get()
value = dictionary.get(key, default)
```

### 4. Clean Up Resources

```python
# ❌ Bad: Resource might not be closed
file = open("data.txt")
data = file.read()
file.close()  # Might not run if error above

# ✅ Good: Use try-finally
file = open("data.txt")
try:
    data = file.read()
finally:
    file.close()

# ✅ Best: Use context manager
with open("data.txt") as file:
    data = file.read()
# File automatically closed
```

### 5. Fail Fast

```python
# ✅ Good: Validate early
def process_user(user_id, age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    if not user_id:
        raise ValueError("User ID required")
    
    # Continue with valid data
    expensive_operation(user_id, age)
```

### 6. Add Context to Exceptions

```python
# ❌ Bad: Generic error
if age < 0:
    raise ValueError("Invalid value")

# ✅ Good: Specific context
if age < 0:
    raise ValueError(f"Age cannot be negative: {age}")
```

### 7. Use Logging

```python
import logging

try:
    result = risky_operation()
except Exception as e:
    logging.error(f"Operation failed: {e}", exc_info=True)
    # exc_info=True includes full traceback
    raise
```

---

## 6. Context Managers

### The `with` Statement

```python
# Without context manager
file = open("data.txt")
try:
    content = file.read()
finally:
    file.close()

# With context manager
with open("data.txt") as file:
    content = file.read()
# File automatically closed, even if exception occurs
```

### Multiple Context Managers

```python
with open("input.txt") as infile, open("output.txt", "w") as outfile:
    content = infile.read()
    outfile.write(content.upper())
```

### Creating Custom Context Manager

```python
class DatabaseConnection:
    def __enter__(self):
        print("Opening connection")
        self.conn = self.connect()
        return self.conn
    
    def __exit__(self, exc_type, exc_value, traceback):
        print("Closing connection")
        self.conn.close()
        # Return False to propagate exception
        # Return True to suppress exception
        return False

with DatabaseConnection() as conn:
    conn.execute("SELECT * FROM users")
# Connection automatically closed
```

### Context Manager with contextlib

```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"Elapsed: {end - start:.2f}s")

with timer():
    # Some operation
    time.sleep(2)
# Prints: Elapsed: 2.00s
```

---

## Exercises

### Level 1: Basics

1. **Safe Input**
   - Get number from user
   - Handle ValueError
   - Keep asking until valid

2. **Safe File Read**
   - Read file
   - Handle FileNotFoundError
   - Return empty string if not found

3. **Safe Division**
   - Function divide(a, b)
   - Handle ZeroDivisionError
   - Handle TypeError

4. **List Access**
   - Get item from list by index
   - Handle IndexError
   - Return None if out of range

5. **Dictionary Access**
   - Get value from dict
   - Handle KeyError
   - Return default value

### Level 2: Intermediate

6. **Multiple Exceptions**
   - Function that might raise 3 different exceptions
   - Handle each specifically
   - Use else and finally

7. **Custom Exception**
   - Create InvalidEmailError
   - Validate email format
   - Raise custom exception if invalid

8. **Retry Logic**
   - Try operation 3 times
   - Catch exception
   - Retry with delay

9. **File Context Manager**
   - Create context manager for file operations
   - Log open/close
   - Handle exceptions

10. **Validation Chain**
    - Validate user input (age, email, phone)
    - Raise specific custom exceptions
    - Handle all validation errors

### Level 3: Challenging

11. **Exception Chaining**
    - Catch exception, add context, re-raise
    - Use `raise ... from ...`

12. **Transaction System**
    - Implement rollback on exception
    - Multiple operations
    - All-or-nothing

13. **Logging System**
    - Custom exception handler
    - Log to file
    - Different log levels

14. **API Error Handling**
    - Handle network errors
    - Timeout errors
    - Rate limit errors
    - Retry with exponential backoff

15. **Resource Pool**
    - Context manager for resource pool
    - Acquire/release resources
    - Handle cleanup on exception

---

## Projects

### Project 1: Robust Calculator
- Handle all possible exceptions
- Validate input
- Provide helpful error messages
- Logging

### Project 2: File Processor
- Read files safely
- Handle missing files
- Handle corrupt data
- Transaction-like behavior

### Project 3: User Registration System
- Validate all inputs
- Custom exceptions
- Comprehensive error handling
- Error logging

---

## Key Takeaways

✅ **Exception Handling**:
- Use try-except to handle errors
- Catch specific exceptions
- Use else for success code
- Use finally for cleanup

✅ **Best Practices**:
- Be specific with exceptions
- Don't swallow errors
- Use EAFP (try-except) over LBYL (if checks)
- Add context to errors
- Use logging

✅ **Custom Exceptions**:
- Inherit from Exception
- Add meaningful data
- Create exception hierarchies

✅ **Context Managers**:
- Use `with` for resources
- Automatic cleanup
- Create custom ones when needed

---

Continue to [Part-07-Type-Hints](../Part-07-Type-Hints/README.md)!
