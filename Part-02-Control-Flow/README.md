# Part 2: Control Flow

> Master conditional statements and loops - the building blocks of program logic.

## 📚 Table of Contents

1. [If-Elif-Else Statements](#1-if-elif-else-statements)
2. [Loops - For and While](#2-loops---for-and-while)
3. [Loop Control - Break, Continue, Pass](#3-loop-control---break-continue-pass)
4. [Advanced Loop Techniques](#4-advanced-loop-techniques)
5. [Nested Control Structures](#5-nested-control-structures)
6. [Exercises](#exercises)
7. [Projects](#projects)

---

## 1. If-Elif-Else Statements

### Basic If Statement

```python
age = 18

if age >= 18:
    print("You are an adult")
```

**Key Points:**
- Condition must evaluate to True or False
- Code block is indented (4 spaces is standard)
- No parentheses needed around condition
- Colon `:` is required

### If-Else Statement

```python
age = 15

if age >= 18:
    print("You are an adult")
else:
    print("You are a minor")
```

### If-Elif-Else Statement

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Your grade: {grade}")
```

**Important:**
- `elif` is short for "else if"
- Conditions are checked top to bottom
- First true condition is executed, rest are skipped
- `else` is optional

### Nested If Statements

```python
age = 25
has_license = True

if age >= 18:
    if has_license:
        print("You can drive")
    else:
        print("You need a license")
else:
    print("Too young to drive")
```

### Conditional Expressions (Ternary Operator)

```python
# Basic syntax: value_if_true if condition else value_if_false
age = 20
status = "Adult" if age >= 18 else "Minor"
print(status)  # "Adult"

# Multiple conditions
score = 85
result = "Excellent" if score >= 90 else "Good" if score >= 70 else "Poor"
```

**⚠️ Warning:** Don't overuse ternary operators - they can reduce readability!

### Truthy and Falsy Values

```python
# Falsy values (evaluate to False)
if 0:
    print("Won't print")

if "":
    print("Won't print")

if []:
    print("Won't print")

if None:
    print("Won't print")

# Truthy values (evaluate to True)
if 1:
    print("Will print")

if "text":
    print("Will print")

if [1]:
    print("Will print")

# Practical usage
name = input("Enter name: ")
if name:  # Check if name is not empty
    print(f"Hello, {name}")
else:
    print("You didn't enter a name")
```

### Multiple Conditions

```python
age = 25
salary = 50000

# AND - Both must be true
if age >= 21 and salary >= 40000:
    print("Eligible for premium credit card")

# OR - At least one must be true
if age < 18 or age > 65:
    print("Eligible for discount")

# NOT - Inverts condition
is_weekend = False
if not is_weekend:
    print("It's a weekday")

# Complex conditions
temperature = 25
is_raining = False
has_umbrella = True

if temperature > 20 and (not is_raining or has_umbrella):
    print("Good day for a walk")
```

### Using `in` with If Statements

```python
# Check membership
fruits = ["apple", "banana", "orange"]
fruit = "apple"

if fruit in fruits:
    print(f"{fruit} is in the list")

# Check substring
text = "Python Programming"
if "Python" in text:
    print("Found Python")

# Check dictionary keys
user = {"name": "Alice", "age": 25}
if "email" in user:
    print(user["email"])
else:
    print("Email not found")
```

---

## 2. Loops - For and While

### For Loop Basics

**For loop is used when you know how many times to iterate**

```python
# Iterate over a list
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)

# Output:
# apple
# banana
# orange
```

### Using range()

```python
# range(stop) - from 0 to stop-1
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# range(start, stop) - from start to stop-1
for i in range(1, 6):
    print(i)  # 1, 2, 3, 4, 5

# range(start, stop, step) - with custom step
for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8

# Counting backwards
for i in range(10, 0, -1):
    print(i)  # 10, 9, 8, ..., 1
```

### Iterating Over Strings

```python
text = "Python"
for char in text:
    print(char)

# Output:
# P
# y
# t
# h
# o
# n
```

### Iterating Over Dictionaries

```python
user = {"name": "Alice", "age": 25, "city": "NYC"}

# Iterate over keys (default)
for key in user:
    print(key)

# Iterate over values
for value in user.values():
    print(value)

# Iterate over key-value pairs
for key, value in user.items():
    print(f"{key}: {value}")
```

### While Loop Basics

**While loop is used when you don't know how many iterations needed**

```python
# Basic while loop
count = 0
while count < 5:
    print(count)
    count += 1

# Output: 0, 1, 2, 3, 4
```

### While Loop with User Input

```python
# Keep asking until valid input
while True:
    age = input("Enter your age: ")
    if age.isdigit():
        age = int(age)
        break
    print("Invalid input. Please enter a number.")

print(f"Your age is {age}")
```

### While vs For Loop

```python
# Using for loop (when count is known)
for i in range(5):
    print(i)

# Using while loop (equivalent)
i = 0
while i < 5:
    print(i)
    i += 1

# For loop is preferred when possible (more Pythonic)
```

---

## 3. Loop Control - Break, Continue, Pass

### Break Statement

**Exits the loop completely**

```python
# Find first even number
numbers = [1, 3, 5, 8, 9, 10]
for num in numbers:
    if num % 2 == 0:
        print(f"Found first even number: {num}")
        break

# Search in a loop
names = ["Alice", "Bob", "Charlie", "David"]
search = "Charlie"

for name in names:
    if name == search:
        print(f"Found {search}!")
        break
else:
    # This else runs only if loop completes WITHOUT break
    print(f"{search} not found")
```

### Continue Statement

**Skips current iteration, continues with next**

```python
# Print only odd numbers
for i in range(10):
    if i % 2 == 0:
        continue  # Skip even numbers
    print(i)

# Output: 1, 3, 5, 7, 9

# Skip specific values
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for num in numbers:
    if num == 5:
        continue  # Skip 5
    print(num)
```

### Pass Statement

**Does nothing - placeholder for empty code blocks**

```python
# Placeholder for future implementation
for i in range(5):
    pass  # TODO: Implement later

# Empty function
def future_function():
    pass

# Empty class
class FutureClass:
    pass

# Useful when you need syntactically correct code but no action
if condition:
    pass  # Nothing to do here
else:
    print("Do something")
```

### Loop Else Clause

**Executes if loop completes normally (no break)**

```python
# Search with else
numbers = [1, 3, 5, 7, 9]
search = 6

for num in numbers:
    if num == search:
        print(f"Found {search}")
        break
else:
    print(f"{search} not found")  # This runs

# Check if all numbers are positive
numbers = [1, 2, 3, 4, 5]
for num in numbers:
    if num < 0:
        print("Found negative number")
        break
else:
    print("All numbers are positive")  # This runs
```

---

## 4. Advanced Loop Techniques

### enumerate() - Get Index and Value

```python
fruits = ["apple", "banana", "orange"]

# Without enumerate (manual index)
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# With enumerate (Pythonic way)
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# Start index from 1
for index, fruit in enumerate(fruits, start=1):
    print(f"{index}: {fruit}")

# Output:
# 1: apple
# 2: banana
# 3: orange
```

### zip() - Iterate Over Multiple Lists

```python
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
cities = ["NYC", "LA", "Chicago"]

# Zip multiple lists together
for name, age, city in zip(names, ages, cities):
    print(f"{name} is {age} years old and lives in {city}")

# zip() stops at shortest list
list1 = [1, 2, 3, 4, 5]
list2 = ["a", "b", "c"]

for num, letter in zip(list1, list2):
    print(f"{num}: {letter}")

# Output:
# 1: a
# 2: b
# 3: c
```

### reversed() - Iterate in Reverse

```python
numbers = [1, 2, 3, 4, 5]

for num in reversed(numbers):
    print(num)

# Output: 5, 4, 3, 2, 1

# With strings
text = "Python"
for char in reversed(text):
    print(char)

# Output: n, o, h, t, y, P
```

### sorted() - Iterate in Sorted Order

```python
numbers = [3, 1, 4, 1, 5, 9, 2]

# Sort ascending
for num in sorted(numbers):
    print(num)

# Sort descending
for num in sorted(numbers, reverse=True):
    print(num)

# Sort strings
names = ["Charlie", "Alice", "Bob"]
for name in sorted(names):
    print(name)

# Output: Alice, Bob, Charlie
```

### List Comprehension (Preview)

```python
# Create list of squares
squares = []
for i in range(10):
    squares.append(i ** 2)

# Same with list comprehension (more Pythonic)
squares = [i ** 2 for i in range(10)]

# With condition
even_squares = [i ** 2 for i in range(10) if i % 2 == 0]

print(even_squares)  # [0, 4, 16, 36, 64]
```

---

## 5. Nested Control Structures

### Nested Loops

```python
# Multiplication table
for i in range(1, 6):
    for j in range(1, 6):
        print(f"{i} × {j} = {i * j}")
    print()  # Empty line after each number

# Pattern printing
for i in range(5):
    for j in range(i + 1):
        print("*", end="")
    print()

# Output:
# *
# **
# ***
# ****
# *****

# Nested list iteration
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

for row in matrix:
    for element in row:
        print(element, end=" ")
    print()
```

### Nested If Statements

```python
age = 25
income = 50000
credit_score = 720

# Loan eligibility checker
if age >= 21:
    if income >= 40000:
        if credit_score >= 700:
            print("Approved for premium loan")
        else:
            print("Approved for standard loan")
    else:
        print("Income too low")
else:
    print("Age requirement not met")

# Better: Flatten with and
if age >= 21 and income >= 40000 and credit_score >= 700:
    print("Approved for premium loan")
elif age >= 21 and income >= 40000:
    print("Approved for standard loan")
elif age >= 21:
    print("Income too low")
else:
    print("Age requirement not met")
```

### Loop with Nested Conditions

```python
# Process numbers with multiple conditions
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

for num in numbers:
    if num % 2 == 0:
        if num % 4 == 0:
            print(f"{num} is divisible by 4")
        else:
            print(f"{num} is divisible by 2 but not 4")
    else:
        if num > 5:
            print(f"{num} is odd and greater than 5")
        else:
            print(f"{num} is odd and 5 or less")
```

---

## Exercises

### Level 1: Basics

1. **Age Classifier**
   - Get age from user
   - Print: "Child" (0-12), "Teen" (13-19), "Adult" (20-59), "Senior" (60+)

2. **Number Sign**
   - Get a number from user
   - Print whether it's "Positive", "Negative", or "Zero"

3. **Count to Ten**
   - Use a for loop to print numbers 1 to 10

4. **Sum Calculator**
   - Calculate sum of numbers 1 to 100 using a loop

5. **Multiplication Table**
   - Get a number from user
   - Print its multiplication table (1 to 10)

### Level 2: Intermediate

6. **Factorial Calculator**
   - Get a number from user
   - Calculate and print its factorial using a loop

7. **Prime Checker**
   - Get a number from user
   - Check if it's prime using a loop

8. **Vowel Counter**
   - Get a string from user
   - Count and print number of vowels

9. **Fibonacci Sequence**
   - Print first N Fibonacci numbers (N from user)

10. **Password Validator**
    - Keep asking for password until it meets requirements:
      - At least 8 characters
      - Contains at least one digit
      - Contains at least one uppercase letter

### Level 3: Challenging

11. **Pattern Printer**
    - Print pyramid pattern:
      ```
          *
         ***
        *****
       *******
      *********
      ```

12. **Number Guessing Game**
    - Generate random number 1-100
    - Let user guess (give "higher" or "lower" hints)
    - Count attempts

13. **Palindrome Checker**
    - Get a string from user
    - Check if it's a palindrome (reads same forwards/backwards)

14. **Prime Numbers in Range**
    - Print all prime numbers between 1 and 100

15. **Matrix Sum**
    - Create a 3x3 matrix (nested lists)
    - Calculate sum of each row and column

---

## Projects

### Project 1: Interactive Menu System

Create a calculator with menu:
```
=== Calculator ===
1. Add
2. Subtract
3. Multiply
4. Divide
5. Exit

Enter choice:
```

Keep showing menu until user chooses Exit.

### Project 2: Student Grade Manager

Create a program that:
- Accepts multiple student names and scores
- Calculates average for each student
- Assigns letter grades
- Shows class statistics (highest, lowest, average)
- Continues until user types "done"

### Project 3: Simple ATM System

Create an ATM simulation:
- Start with balance of $1000
- Menu: Check Balance, Deposit, Withdraw, Exit
- Validate withdrawal amount
- Show transaction history
- Loop until user exits

---

## Key Takeaways

✅ **Control Flow Basics:**
- `if/elif/else` for decisions
- `for` loop for known iterations
- `while` loop for unknown iterations
- `break` to exit loop
- `continue` to skip iteration
- `pass` as placeholder

✅ **Best Practices:**
- Use `for` loop with `range()` instead of `while` when possible
- Use `enumerate()` when you need both index and value
- Use `zip()` to iterate over multiple lists
- Avoid deeply nested loops (max 2-3 levels)
- Use loop `else` clause for search patterns
- Keep conditions simple and readable

✅ **Common Mistakes:**
- Forgetting colon `:` after conditions/loops
- Incorrect indentation
- Infinite loops (forgetting to update condition)
- Using `=` instead of `==` in conditions
- Modifying list while iterating

---

## What's Next?

Continue to [Part-03-Functions](../Part-03-Functions/README.md) to learn about creating reusable code blocks!
