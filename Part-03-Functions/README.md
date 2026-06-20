# Part 3: Functions

> Master functions - the cornerstone of reusable, maintainable code.

## 📚 Table of Contents

1. [Function Basics](#1-function-basics)
2. [Parameters and Arguments](#2-parameters-and-arguments)
3. [Return Values](#3-return-values)
4. [*args and **kwargs](#4-args-and-kwargs)
5. [Lambda Functions](#5-lambda-functions)
6. [Scope and Closures](#6-scope-and-closures)
7. [Higher-Order Functions](#7-higher-order-functions)
8. [Exercises](#exercises)

---

## 1. Function Basics

### What is a Function?

A function is a reusable block of code that performs a specific task.

**Why Use Functions?**
- **Reusability**: Write once, use many times
- **Organization**: Break complex problems into smaller pieces
- **Maintainability**: Fix bugs in one place
- **Testing**: Test individual components

### Defining Functions

```python
# Basic function definition
def greet():
    print("Hello, World!")

# Call the function
greet()  # Output: Hello, World!
```

**Syntax:**
```python
def function_name():
    # function body
    # indented code block
```

### Function with Parameters

```python
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")  # Hello, Alice!
greet("Bob")    # Hello, Bob!
```

### Function with Multiple Parameters

```python
def introduce(name, age, city):
    print(f"My name is {name}, I am {age} years old, and I live in {city}")

introduce("Alice", 25, "NYC")
```

---

## 2. Parameters and Arguments

### Positional Arguments

```python
def divide(a, b):
    return a / b

result = divide(10, 2)  # a=10, b=2
print(result)  # 5.0

# Order matters!
result = divide(2, 10)  # a=2, b=10
print(result)  # 0.2
```

### Keyword Arguments

```python
def introduce(name, age, city):
    print(f"{name} is {age} years old from {city}")

# Using keyword arguments (order doesn't matter)
introduce(age=25, city="NYC", name="Alice")
introduce(name="Bob", age=30, city="LA")

# Mix positional and keyword
introduce("Charlie", age=35, city="Chicago")
```

**Rule:** Positional arguments must come before keyword arguments!

```python
# ✅ Correct
introduce("Alice", age=25, city="NYC")

# ❌ Error: positional argument follows keyword argument
introduce(name="Alice", 25, "NYC")
```

### Default Arguments

```python
def greet(name, message="Hello"):
    print(f"{message}, {name}!")

greet("Alice")              # Hello, Alice!
greet("Bob", "Hi")          # Hi, Bob!
greet("Charlie", message="Hey")  # Hey, Charlie!
```

**Important:** Default parameters must come after non-default parameters

```python
# ✅ Correct
def func(a, b, c=10, d=20):
    pass

# ❌ Error: non-default argument follows default argument
def func(a, b=10, c, d=20):
    pass
```

**⚠️ Warning: Mutable Default Arguments**

```python
# WRONG - Common mistake!
def add_item(item, list=[]):
    list.append(item)
    return list

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] - Wait, what?!
print(add_item(3))  # [1, 2, 3] - Same list is reused!

# CORRECT - Use None as default
def add_item(item, list=None):
    if list is None:
        list = []
    list.append(item)
    return list

print(add_item(1))  # [1]
print(add_item(2))  # [2] - New list each time
```

---

## 3. Return Values

### Basic Return

```python
def add(a, b):
    return a + b

result = add(5, 3)
print(result)  # 8
```

### Multiple Return Values

```python
def get_min_max(numbers):
    return min(numbers), max(numbers)

# Python returns a tuple
result = get_min_max([1, 5, 3, 9, 2])
print(result)  # (1, 9)

# Unpack into variables
minimum, maximum = get_min_max([1, 5, 3, 9, 2])
print(f"Min: {minimum}, Max: {maximum}")  # Min: 1, Max: 9
```

### Return with Conditions

```python
def check_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

grade = check_grade(85)
print(grade)  # B
```

### Early Return

```python
def divide(a, b):
    if b == 0:
        return "Cannot divide by zero"
    return a / b

print(divide(10, 2))   # 5.0
print(divide(10, 0))   # Cannot divide by zero
```

### Functions Without Return (return None)

```python
def print_message(message):
    print(message)
    # No return statement

result = print_message("Hello")
print(result)  # None
```

---

## 4. *args and **kwargs

### *args - Variable Positional Arguments

**What is *args?**
- Allows function to accept any number of positional arguments
- Packs arguments into a tuple
- The name "args" is convention (can be any name with *)

```python
def sum_all(*args):
    print(f"args type: {type(args)}")  # <class 'tuple'>
    print(f"args value: {args}")
    
    total = 0
    for num in args:
        total += num
    return total

print(sum_all(1, 2, 3))           # 6
print(sum_all(1, 2, 3, 4, 5))     # 15
print(sum_all(10, 20))            # 30
```

**Real-world Example:**

```python
def create_user(username, *roles):
    print(f"Creating user: {username}")
    print(f"Roles: {roles}")
    
create_user("alice", "admin", "developer", "reviewer")
# Creating user: alice
# Roles: ('admin', 'developer', 'reviewer')
```

### **kwargs - Variable Keyword Arguments

**What is **kwargs?**
- Allows function to accept any number of keyword arguments
- Packs arguments into a dictionary
- The name "kwargs" is convention (can be any name with **)

```python
def print_info(**kwargs):
    print(f"kwargs type: {type(kwargs)}")  # <class 'dict'>
    print(f"kwargs value: {kwargs}")
    
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="NYC")
# kwargs type: <class 'dict'>
# kwargs value: {'name': 'Alice', 'age': 25, 'city': 'NYC'}
# name: Alice
# age: 25
# city: NYC
```

**Real-world Example:**

```python
def create_user(username, **attributes):
    user = {"username": username}
    user.update(attributes)
    return user

user1 = create_user("alice", email="alice@example.com", age=25)
user2 = create_user("bob", email="bob@example.com", role="admin", active=True)

print(user1)  # {'username': 'alice', 'email': 'alice@example.com', 'age': 25}
print(user2)  # {'username': 'bob', 'email': 'bob@example.com', 'role': 'admin', 'active': True}
```

### Combining *args and **kwargs

```python
def func(a, b, *args, **kwargs):
    print(f"a: {a}")
    print(f"b: {b}")
    print(f"args: {args}")
    print(f"kwargs: {kwargs}")

func(1, 2, 3, 4, 5, x=10, y=20)
# a: 1
# b: 2
# args: (3, 4, 5)
# kwargs: {'x': 10, 'y': 20}
```

**Parameter Order Rules:**

```python
# Correct order: positional, *args, default, **kwargs
def function(a, b, *args, c=10, **kwargs):
    pass

# ✅ Valid calls
function(1, 2, 3, 4, c=5, x=10)
function(1, 2, c=5, x=10, y=20)
```

### Unpacking Arguments

```python
# Unpacking lists/tuples with *
def add(a, b, c):
    return a + b + c

numbers = [1, 2, 3]
result = add(*numbers)  # Same as add(1, 2, 3)
print(result)  # 6

# Unpacking dictionaries with **
def introduce(name, age, city):
    print(f"{name} is {age} from {city}")

person = {"name": "Alice", "age": 25, "city": "NYC"}
introduce(**person)  # Same as introduce(name="Alice", age=25, city="NYC")
```

---

## 5. Lambda Functions

### What are Lambda Functions?

Lambda functions are **anonymous functions** defined in one line.

**Syntax:**
```python
lambda arguments: expression
```

### Basic Lambda Examples

```python
# Regular function
def square(x):
    return x ** 2

# Equivalent lambda
square = lambda x: x ** 2

print(square(5))  # 25
```

### Lambda with Multiple Arguments

```python
# Addition
add = lambda a, b: a + b
print(add(3, 5))  # 8

# Maximum of two numbers
max_of_two = lambda a, b: a if a > b else b
print(max_of_two(10, 20))  # 20
```

### Lambda as Function Arguments

```python
# Sorting with custom key
students = [
    {"name": "Alice", "grade": 85},
    {"name": "Bob", "grade": 92},
    {"name": "Charlie", "grade": 78}
]

# Sort by grade
sorted_students = sorted(students, key=lambda s: s["grade"])
print(sorted_students)

# Sort by name
sorted_by_name = sorted(students, key=lambda s: s["name"])
print(sorted_by_name)
```

### Lambda with map(), filter(), reduce()

```python
# map() - Apply function to each element
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x ** 2, numbers))
print(squares)  # [1, 4, 9, 16, 25]

# filter() - Filter elements
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(even_numbers)  # [2, 4]

# reduce() - Reduce to single value
from functools import reduce
sum_all = reduce(lambda a, b: a + b, numbers)
print(sum_all)  # 15
```

**When to Use Lambda:**
- ✅ Simple, one-line operations
- ✅ As arguments to higher-order functions
- ✅ Throwaway functions (used once)

**When NOT to Use Lambda:**
- ❌ Complex logic (use regular functions)
- ❌ Multiple statements needed
- ❌ Need for documentation/naming

---

## 6. Scope and Closures

### Variable Scope

```python
# Global scope
x = "global"

def outer():
    # Enclosing scope
    x = "enclosing"
    
    def inner():
        # Local scope
        x = "local"
        print(f"Inner: {x}")
    
    inner()
    print(f"Outer: {x}")

outer()
print(f"Global: {x}")

# Output:
# Inner: local
# Outer: enclosing
# Global: global
```

### LEGB Rule

Python looks for variables in this order:
1. **L**ocal - inside current function
2. **E**nclosing - in enclosing functions
3. **G**lobal - at module level
4. **B**uilt-in - Python's built-in names

```python
x = "global"

def test():
    x = "local"
    print(x)  # Prints "local" (L)

test()
print(x)  # Prints "global" (G)
```

### Modifying Global Variables

```python
counter = 0

def increment():
    global counter  # Declare as global
    counter += 1

increment()
increment()
print(counter)  # 2
```

**⚠️ Warning:** Avoid using `global` when possible. Pass parameters instead.

```python
# Better approach - Pure function
def increment(counter):
    return counter + 1

counter = 0
counter = increment(counter)
counter = increment(counter)
print(counter)  # 2
```

### Nonlocal Keyword

```python
def outer():
    count = 0
    
    def inner():
        nonlocal count  # Refer to enclosing scope
        count += 1
        return count
    
    print(inner())  # 1
    print(inner())  # 2
    print(inner())  # 3

outer()
```

### Closures

**What is a Closure?**
A function that remembers values from its enclosing scope.

```python
def multiplier(n):
    def multiply(x):
        return x * n  # 'n' is captured from enclosing scope
    return multiply

# Create specialized functions
times_2 = multiplier(2)
times_3 = multiplier(3)

print(times_2(5))  # 10
print(times_3(5))  # 15
```

**Practical Example - Counter Factory:**

```python
def make_counter():
    count = 0
    
    def increment():
        nonlocal count
        count += 1
        return count
    
    return increment

counter1 = make_counter()
counter2 = make_counter()

print(counter1())  # 1
print(counter1())  # 2
print(counter2())  # 1 (separate counter)
print(counter1())  # 3
```

---

## 7. Higher-Order Functions

**Higher-order functions** either:
1. Take functions as arguments, OR
2. Return functions as results

### Functions as Arguments

```python
def apply_operation(a, b, operation):
    return operation(a, b)

def add(x, y):
    return x + y

def multiply(x, y):
    return x * y

print(apply_operation(5, 3, add))       # 8
print(apply_operation(5, 3, multiply))  # 15

# With lambda
print(apply_operation(5, 3, lambda x, y: x - y))  # 2
```

### Built-in Higher-Order Functions

#### map()

```python
# Transform each element
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# With regular function
def celsius_to_fahrenheit(c):
    return (c * 9/5) + 32

celsius = [0, 10, 20, 30, 40]
fahrenheit = list(map(celsius_to_fahrenheit, celsius))
print(fahrenheit)  # [32.0, 50.0, 68.0, 86.0, 104.0]
```

#### filter()

```python
# Filter elements
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)  # [2, 4, 6, 8, 10]

# Filter complex objects
users = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 17},
    {"name": "Charlie", "age": 30}
]

adults = list(filter(lambda u: u["age"] >= 18, users))
print(adults)
```

#### reduce()

```python
from functools import reduce

# Sum all numbers
numbers = [1, 2, 3, 4, 5]
total = reduce(lambda a, b: a + b, numbers)
print(total)  # 15

# Find maximum
maximum = reduce(lambda a, b: a if a > b else b, numbers)
print(maximum)  # 5
```

### Decorator Preview

```python
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@logger
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Output:
# Calling greet
# Hello, Alice!
# Finished greet
```

---

## Exercises

### Level 1: Basics

1. **Simple Calculator**
   - Create functions: add, subtract, multiply, divide
   - Each takes two numbers and returns result

2. **Temperature Converter**
   - Function to convert Celsius to Fahrenheit
   - Function to convert Fahrenheit to Celsius

3. **String Length**
   - Function that takes a string and returns its length
   - Don't use built-in len()

4. **Is Even**
   - Function that checks if a number is even
   - Returns True or False

5. **Max of Three**
   - Function that returns maximum of three numbers

### Level 2: Intermediate

6. **Factorial**
   - Function to calculate factorial (n!)
   - Use loop, not recursion

7. **Prime Checker**
   - Function that checks if number is prime
   - Return True or False

8. **List Statistics**
   - Function that takes a list of numbers
   - Returns dictionary with: min, max, sum, average

9. **Reverse String**
   - Function that reverses a string
   - Don't use [::-1]

10. **Count Vowels**
    - Function that counts vowels in a string
    - Return count of each vowel

### Level 3: Challenging

11. **Fibonacci Generator**
    - Function that returns nth Fibonacci number
    - Use recursion

12. **Function Composition**
    - Create function that composes two functions
    - compose(f, g)(x) should equal f(g(x))

13. **Decorator Practice**
    - Create a timing decorator
    - Measures function execution time

14. **Currying**
    - Create curried version of add(a, b, c)
    - add(1)(2)(3) should return 6

15. **Memoization**
    - Implement memoization for factorial function
    - Cache previously calculated values

---

## Key Takeaways

✅ **Function Fundamentals:**
- Functions enable code reuse and organization
- Use descriptive names (verb + noun)
- Keep functions small and focused
- One function = One responsibility

✅ **Parameters:**
- Positional arguments: order matters
- Keyword arguments: order doesn't matter
- Default arguments: provide fallback values
- *args: variable positional arguments (tuple)
- **kwargs: variable keyword arguments (dict)

✅ **Best Practices:**
- Avoid mutable default arguments
- Use pure functions when possible (no side effects)
- Return values instead of modifying globals
- Document complex functions
- Keep functions short (< 20 lines ideal)

✅ **Advanced Concepts:**
- Lambda: one-line anonymous functions
- Closures: functions that remember enclosing scope
- Higher-order functions: functions that work with functions
- Decorators: modify function behavior

---

## What's Next?

Continue to [Part-04-OOP](../Part-04-OOP/README.md) to learn Object-Oriented Programming!
