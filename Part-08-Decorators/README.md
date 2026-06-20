# Part 8: Decorators

> Master Python decorators - a powerful pattern for modifying function and class behavior.

## 📚 Table of Contents

1. [Introduction to Decorators](#1-introduction-to-decorators)
2. [Function Decorators](#2-function-decorators)
3. [Decorators with Arguments](#3-decorators-with-arguments)
4. [Class Decorators](#4-class-decorators)
5. [Built-in Decorators](#5-built-in-decorators)
6. [Practical Decorators](#6-practical-decorators)
7. [Advanced Patterns](#7-advanced-patterns)
8. [Exercises](#exercises)

---

## 1. Introduction to Decorators

### What is a Decorator?

A decorator is a function that **modifies the behavior** of another function or class without changing its source code.

**Think of it as a wrapper:**
```
Original Function → Decorator → Modified Function
```

### Why Use Decorators?

- **Code reuse**: Apply same behavior to multiple functions
- **Separation of concerns**: Keep core logic separate from cross-cutting concerns
- **Clean syntax**: Elegant `@decorator` syntax
- **Non-invasive**: Don't modify original function

### First-Class Functions Review

```python
# Functions are objects
def greet(name):
    return f"Hello, {name}!"

# Assign to variable
say_hello = greet
print(say_hello("Alice"))  # Hello, Alice!

# Pass as argument
def apply(func, value):
    return func(value)

result = apply(greet, "Bob")  # Hello, Bob!

# Return from function
def get_greeter():
    def greet(name):
        return f"Hi, {name}!"
    return greet

greeter = get_greeter()
print(greeter("Charlie"))  # Hi, Charlie!
```

### Simple Decorator Example

```python
def simple_decorator(func):
    def wrapper():
        print("Before function call")
        func()
        print("After function call")
    return wrapper

@simple_decorator
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Before function call
# Hello!
# After function call
```

**What `@simple_decorator` does:**
```python
# This:
@simple_decorator
def say_hello():
    print("Hello!")

# Is equivalent to:
def say_hello():
    print("Hello!")
say_hello = simple_decorator(say_hello)
```

---

## 2. Function Decorators

### Basic Decorator Pattern

```python
def my_decorator(func):
    def wrapper():
        # Do something before
        result = func()
        # Do something after
        return result
    return wrapper

@my_decorator
def my_function():
    print("Function executed")
```

### Decorator with Function Arguments

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

result = add(5, 3)
# Output:
# Calling add
# Finished add
print(result)  # 8
```

### Preserving Function Metadata

```python
from functools import wraps

# ❌ Without @wraps
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def greet(name):
    """Greet someone"""
    return f"Hello, {name}!"

print(greet.__name__)  # wrapper (wrong!)
print(greet.__doc__)   # None (lost!)

# ✅ With @wraps
def good_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@good_decorator
def greet(name):
    """Greet someone"""
    return f"Hello, {name}!"

print(greet.__name__)  # greet (correct!)
print(greet.__doc__)   # Greet someone (preserved!)
```

### Timing Decorator

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

result = slow_function()
# slow_function took 1.0012 seconds
```

### Logging Decorator

```python
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_str = ', '.join(repr(a) for a in args)
        kwargs_str = ', '.join(f"{k}={v!r}" for k, v in kwargs.items())
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))
        
        print(f"Calling {func.__name__}({all_args})")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

result = add(5, 3)
# Output:
# Calling add(5, 3)
# add returned 8
```

### Retry Decorator

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    print(f"Attempt {attempts} failed: {e}. Retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def unstable_function():
    import random
    if random.random() < 0.7:
        raise ValueError("Random failure")
    return "Success!"
```

---

## 3. Decorators with Arguments

### Understanding Decorator Arguments

```python
# Decorator without arguments
@decorator
def func():
    pass

# Decorator with arguments
@decorator(arg1, arg2)
def func():
    pass
```

**How it works:**
```python
# This:
@decorator(arg1, arg2)
def func():
    pass

# Becomes:
decorator_with_args = decorator(arg1, arg2)
func = decorator_with_args(func)
```

### Simple Parameterized Decorator

```python
from functools import wraps

def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Output:
# Hello, Alice!
# Hello, Alice!
# Hello, Alice!
```

### Validation Decorator

```python
from functools import wraps

def validate_types(**type_checks):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check argument types
            for arg_name, expected_type in type_checks.items():
                if arg_name in kwargs:
                    value = kwargs[arg_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{arg_name} must be {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(name=str, age=int)
def create_user(name, age):
    return {"name": name, "age": age}

user = create_user(name="Alice", age=25)  # OK
# user = create_user(name="Bob", age="30")  # TypeError!
```

### Rate Limiting Decorator

```python
import time
from functools import wraps

def rate_limit(max_calls, time_window):
    """Limit function calls to max_calls per time_window seconds"""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside time window
            calls[:] = [call_time for call_time in calls 
                       if now - call_time < time_window]
            
            if len(calls) >= max_calls:
                sleep_time = time_window - (now - calls[0])
                print(f"Rate limit exceeded. Waiting {sleep_time:.2f}s...")
                time.sleep(sleep_time)
                calls.pop(0)
            
            calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=3, time_window=10)
def api_call():
    print("API call made")
    return "Response"
```

---

## 4. Class Decorators

### Decorating Classes

```python
def add_str_method(cls):
    """Add __str__ method to class"""
    def __str__(self):
        attrs = ', '.join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{cls.__name__}({attrs})"
    cls.__str__ = __str__
    return cls

@add_str_method
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("Alice", 25)
print(person)  # Person(name=Alice, age=25)
```

### Singleton Pattern Decorator

```python
from functools import wraps

def singleton(cls):
    """Ensure only one instance of class exists"""
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class Database:
    def __init__(self):
        print("Initializing database...")

db1 = Database()  # Initializing database...
db2 = Database()  # (no output - returns same instance)
print(db1 is db2)  # True
```

### Class Method Decorator

```python
def method_decorator(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        print(f"Calling {method.__name__}")
        return method(self, *args, **kwargs)
    return wrapper

class MyClass:
    @method_decorator
    def greet(self, name):
        return f"Hello, {name}!"

obj = MyClass()
obj.greet("Alice")
# Calling greet
# Returns: Hello, Alice!
```

---

## 5. Built-in Decorators

### @property

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        """Get radius"""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """Set radius with validation"""
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value
    
    @property
    def area(self):
        """Computed property"""
        import math
        return math.pi * self._radius ** 2

circle = Circle(5)
print(circle.radius)  # 5 (uses getter)
circle.radius = 10    # Uses setter
print(circle.area)    # 314.159... (computed)
# circle.radius = -5  # ValueError!
```

### @staticmethod

```python
class MathUtils:
    @staticmethod
    def add(a, b):
        """Doesn't need instance or class"""
        return a + b
    
    @staticmethod
    def is_even(n):
        return n % 2 == 0

# Call without instance
print(MathUtils.add(5, 3))       # 8
print(MathUtils.is_even(10))     # True
```

### @classmethod

```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_string(cls, date_string):
        """Alternative constructor"""
        year, month, day = map(int, date_string.split('-'))
        return cls(year, month, day)
    
    @classmethod
    def today(cls):
        """Factory method"""
        import datetime
        today = datetime.date.today()
        return cls(today.year, today.month, today.day)

date1 = Date(2024, 1, 15)
date2 = Date.from_string("2024-01-15")
date3 = Date.today()
```

### @functools.lru_cache

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    """Cached fibonacci - much faster!"""
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(100))  # Fast! Results are cached
print(fibonacci.cache_info())  # CacheInfo(hits=98, misses=101, ...)
```

---

## 6. Practical Decorators

### Authentication Decorator

```python
from functools import wraps

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if user is authenticated
        if not is_authenticated():
            raise PermissionError("Authentication required")
        return func(*args, **kwargs)
    return wrapper

def is_authenticated():
    # Check authentication logic
    return True  # Simplified

@require_auth
def view_profile(user_id):
    return f"Profile for user {user_id}"
```

### Cache Decorator

```python
from functools import wraps

def memoize(func):
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    return wrapper

@memoize
def expensive_calculation(n):
    print(f"Computing for {n}...")
    import time
    time.sleep(1)
    return n * n

print(expensive_calculation(5))  # Computing for 5... 25
print(expensive_calculation(5))  # 25 (cached, instant)
```

### Deprecation Warning

```python
import warnings
from functools import wraps

def deprecated(reason):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated: {reason}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@deprecated("Use new_function() instead")
def old_function():
    return "This is old"

old_function()  # Shows deprecation warning
```

---

## 7. Advanced Patterns

### Stacking Decorators

```python
from functools import wraps
import time

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Time: {time.time() - start:.4f}s")
        return result
    return wrapper

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# Applied bottom to top: log_calls(timer(func))
@log_calls
@timer
def slow_function():
    time.sleep(1)
    return "Done"

slow_function()
# Calling slow_function
# Time: 1.0012s
```

### Class-Based Decorators

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count} of {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def greet(name):
    return f"Hello, {name}!"

greet("Alice")  # Call 1 of greet
greet("Bob")    # Call 2 of greet
```

### Context Manager Decorator

```python
from contextlib import contextmanager

@contextmanager
def timer_context():
    import time
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"Elapsed: {end - start:.4f}s")

with timer_context():
    time.sleep(1)
    print("Working...")
# Working...
# Elapsed: 1.0012s
```

---

## Exercises

### Level 1: Basics

1. **Simple Decorator**
   - Create decorator that prints function name before calling

2. **Repeat Decorator**
   - Decorator that calls function N times

3. **Uppercase Decorator**
   - Decorator that converts string return value to uppercase

4. **Count Calls**
   - Track how many times function is called

5. **Add Metadata**
   - Decorator that adds custom attributes to function

### Level 2: Intermediate

6. **Timing Decorator**
   - Measure and print execution time

7. **Memoization**
   - Implement caching decorator

8. **Type Validation**
   - Validate function argument types

9. **Retry Logic**
   - Retry on exception with max attempts

10. **Rate Limiter**
    - Limit function calls per time window

### Level 3: Challenging

11. **Async Decorator**
    - Decorator for async functions

12. **Conditional Decorator**
    - Apply decorator only if condition is true

13. **Decorator Factory**
    - Create decorator that generates other decorators

14. **Chained Decorators**
    - Multiple decorators that work together

15. **Property Decorator**
    - Implement your own property-like decorator

---

## Projects

### Project 1: Web Framework Decorators
- Route decorator (@app.route('/'))
- Before/after request decorators
- Error handler decorator

### Project 2: Performance Monitoring
- Timing decorator
- Memory usage decorator
- Profiling decorator
- Aggregate statistics

### Project 3: API Client Library
- Retry with exponential backoff
- Rate limiting
- Authentication
- Response caching
- Error handling

---

## Key Takeaways

✅ **Decorators**:
- Modify function behavior without changing code
- Use @decorator syntax
- Can be stacked
- Preserve metadata with @wraps

✅ **Common Patterns**:
- Timing and logging
- Validation and authentication
- Caching and memoization
- Retry logic
- Rate limiting

✅ **Built-in**:
- @property for getters/setters
- @staticmethod for utility functions
- @classmethod for alternative constructors
- @lru_cache for automatic caching

✅ **Advanced**:
- Decorators with arguments
- Class decorators
- Class-based decorators
- Decorator factories

---

Continue to [Part-09-Design-Patterns](../Part-09-Design-Patterns/README.md)!
