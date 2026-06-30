# Part 8: Decorators - Practice Problems

> Test function decorators, decorators with arguments, built-in decorators

---

## Problem 1: Simple Decorator

**Task**: Print function name before calling
```python
def print_name(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@print_name
def greet(name):
    return f"Hello, {name}"

greet("Alice")  # Should print "Calling greet" then return
```

**Time**: 15 minutes

---

## Problem 2: Decorator with functools.wraps

**Task**: Preserve function metadata
```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def example():
    \"\"\"This is an example\"\"\"
    pass

print(example.__name__)  # Should be 'example'
print(example.__doc__)   # Should show docstring
```

**Time**: 10 minutes

---

## Problem 3: Timer Decorator

**Task**: Measure execution time
```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end-start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```

**Time**: 15 minutes

---

## Problem 4: Decorator with Arguments

**Task**: Repeat decorator
```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def say_hello():
    print("Hello")

say_hello()  # Prints "Hello" 3 times
```

**Time**: 20 minutes

---

## Problem 5: Memoization Decorator

**Task**: Cache function results
```python
def memoize(func):
    cache = {}
    def wrapper(n):
        if n not in cache:
            cache[n] = func(n)
        return cache[n]
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**Time**: 20 minutes

---

## Problem 6: Class Method Decorator

**Task**: Use @classmethod
```python
class MyClass:
    count = 0
    
    @classmethod
    def increment(cls):
        cls.count += 1
    
    @classmethod
    def get_count(cls):
        return cls.count

MyClass.increment()
assert MyClass.get_count() == 1
```

**Time**: 10 minutes

---

## Problem 7: Static Method Decorator

**Task**: Use @staticmethod
```python
class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b

result = MathUtils.add(3, 5)
assert result == 8
```

**Time**: 5 minutes

---

## Problem 8: Property Decorator

**Task**: Getter and setter
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

c = Circle(5)
assert c.radius == 5
c.radius = 10
```

**Time**: 15 minutes

---

## Problem 9: LRU Cache

**Task**: Use built-in cache decorator
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(n):
    print(f"Computing {n}")
    return n ** 2

expensive_function(5)  # Computes
expensive_function(5)  # Returns cached result
```

**Time**: 10 minutes

---

## Problem 10: Stacking Decorators

**Task**: Multiple decorators
```python
def bold(func):
    def wrapper():
        return f"<b>{func()}</b>"
    return wrapper

def italic(func):
    def wrapper():
        return f"<i>{func()}</i>"
    return wrapper

@bold
@italic
def greet():
    return "Hello"

print(greet())  # <b><i>Hello</i></b>
```

**Time**: 15 minutes

---

## Summary Check

**8+ solved** → Decorators mastered  
**5-7 solved** → Practice decorator arguments  
**< 5 solved** → Review decorator patterns
