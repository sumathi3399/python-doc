# Part 3: Functions - Practice Problems

> Test your understanding of functions, parameters, scope, and closures

---

## Problem 1: Basic Function

**Task**: Temperature converter
```python
def celsius_to_fahrenheit(celsius):
    # F = C * 9/5 + 32
    pass

assert celsius_to_fahrenheit(0) == 32
assert celsius_to_fahrenheit(100) == 212
```

**Time**: 5 minutes

---

## Problem 2: Default Arguments

**Task**: Greeting function
```python
def greet(name, greeting="Hello"):
    # Return: "Hello, Alice!" or custom greeting
    pass

assert greet("Alice") == "Hello, Alice!"
assert greet("Bob", "Hi") == "Hi, Bob!"
```

**Time**: 5 minutes

---

## Problem 3: *args

**Task**: Sum any number of arguments
```python
def add_all(*numbers):
    # Return sum of all arguments
    pass

assert add_all(1, 2, 3) == 6
assert add_all(10) == 10
assert add_all() == 0
```

**Time**: 10 minutes

---

## Problem 4: **kwargs

**Task**: Build query string
```python
def build_query(**params):
    # Return: "key1=val1&key2=val2"
    # Skip None values
    pass

assert build_query(name="Alice", age=25) == "name=Alice&age=25"
```

**Time**: 15 minutes

---

## Problem 5: Lambda Function

**Task**: Sort by second element
```python
pairs = [(1, 'one'), (3, 'three'), (2, 'two')]
# Sort by second element using lambda
# Result: [(1, 'one'), (2, 'two'), (3, 'three')]
```

**Time**: 10 minutes

---

## Problem 6: Closure

**Task**: Counter function
```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = make_counter()
assert counter() == 1
assert counter() == 2
```

**Time**: 15 minutes

---

## Problem 7: Map Function

**Task**: Square all numbers
```python
numbers = [1, 2, 3, 4, 5]
# Use map and lambda to get [1, 4, 9, 16, 25]
```

**Time**: 5 minutes

---

## Problem 8: Filter Function

**Task**: Get even numbers
```python
numbers = [1, 2, 3, 4, 5, 6]
# Use filter to get [2, 4, 6]
```

**Time**: 5 minutes

---

## Problem 9: Recursion

**Task**: Factorial
```python
def factorial(n):
    # Base case: factorial(0) = 1
    # Recursive: factorial(n) = n * factorial(n-1)
    pass

assert factorial(5) == 120
assert factorial(0) == 1
```

**Time**: 15 minutes

---

## Problem 10: Decorator (Simple)

**Task**: Add logging
```python
def log_calls(func):
    def wrapper(*args):
        print(f"Calling {func.__name__}")
        return func(*args)
    return wrapper

@log_calls
def add(a, b):
    return a + b

# Should print "Calling add" then return 8
add(3, 5)
```

**Time**: 20 minutes

---

## Summary Check

**8+ solved** → Part 4 ready  
**5-7 solved** → Review closures and higher-order functions  
**< 5 solved** → Practice more with function basics
