"""
Solutions to Part 1 Exercises - Python Fundamentals

Study these solutions after attempting the exercises yourself.
Understanding WHY these solutions work is more important than the code itself.
"""

# ============================================================================
# LEVEL 1: BASICS
# ============================================================================

print("="*60)
print("LEVEL 1: BASICS")
print("="*60)

# Exercise 1: Hello, Python!
print("\n--- Exercise 1: Hello, Python! ---")
print("Hello, Python!")

# Explanation:
# print() is a built-in function that displays text to the console
# Strings are enclosed in quotes (single or double)


# Exercise 2: Personal Introduction
print("\n--- Exercise 2: Personal Introduction ---")
name = "Alice"
age = 25
favorite_color = "blue"

print(f"My name is {name}, I am {age} years old, and my favorite color is {favorite_color}")

# Explanation:
# f"..." creates an f-string (formatted string literal)
# {variable} inside f-string inserts the variable's value
# This is the most Pythonic way to format strings in modern Python


# Exercise 3: Simple Calculator
print("\n--- Exercise 3: Simple Calculator ---")
num1 = 10
num2 = 3

print(f"Sum: {num1} + {num2} = {num1 + num2}")
print(f"Difference: {num1} - {num2} = {num1 - num2}")
print(f"Product: {num1} × {num2} = {num1 * num2}")
print(f"Quotient: {num1} ÷ {num2} = {num1 / num2}")
print(f"Integer Division: {num1} // {num2} = {num1 // num2}")
print(f"Remainder: {num1} % {num2} = {num1 % num2}")

# Explanation:
# / returns a float (3.333...)
# // returns an integer (3)
# % returns the remainder (1)


# Exercise 4: Type Detective
print("\n--- Exercise 4: Type Detective ---")
my_int = 42
my_float = 3.14
my_string = "Hello"
my_bool = True
my_list = [1, 2, 3]

print(f"{my_int} is of type {type(my_int)}")
print(f"{my_float} is of type {type(my_float)}")
print(f"{my_string} is of type {type(my_string)}")
print(f"{my_bool} is of type {type(my_bool)}")
print(f"{my_list} is of type {type(my_list)}")

# Explanation:
# type() returns the type of any object
# Python has dynamic typing - variables don't have fixed types


# Exercise 5: String Play
print("\n--- Exercise 5: String Play ---")
full_name = "Alice Johnson"

print(f"Original: {full_name}")
print(f"UPPERCASE: {full_name.upper()}")
print(f"lowercase: {full_name.lower()}")
print(f"Title Case: {full_name.title()}")

# Explanation:
# Strings are immutable - methods return NEW strings
# .upper() converts all characters to uppercase
# .lower() converts all characters to lowercase
# .title() capitalizes first letter of each word


# ============================================================================
# LEVEL 2: INTERMEDIATE
# ============================================================================

print("\n" + "="*60)
print("LEVEL 2: INTERMEDIATE")
print("="*60)

# Exercise 6: Temperature Converter
print("\n--- Exercise 6: Temperature Converter ---")
celsius = 25
fahrenheit = (celsius * 9/5) + 32

print(f"{celsius}°C = {fahrenheit}°F")

# Explanation:
# Formula: F = (C × 9/5) + 32
# Order of operations: multiplication and division before addition
# Use parentheses for clarity even when not strictly needed


# Exercise 7: Even or Odd Checker
print("\n--- Exercise 7: Even or Odd Checker ---")
number = 17

if number % 2 == 0:
    print(f"{number} is even")
else:
    print(f"{number} is odd")

# Explanation:
# % (modulo) returns the remainder after division
# Even numbers have remainder 0 when divided by 2
# Odd numbers have remainder 1 when divided by 2


# Exercise 8: BMI Calculator
print("\n--- Exercise 8: BMI Calculator ---")
height = 1.75  # meters
weight = 70    # kilograms

bmi = weight / (height ** 2)
print(f"Height: {height}m")
print(f"Weight: {weight}kg")
print(f"BMI: {bmi:.2f}")

# Explanation:
# ** is the exponentiation operator (power)
# height ** 2 is the same as height * height
# :.2f formats a float to 2 decimal places


# Exercise 9: String Reverser
print("\n--- Exercise 9: String Reverser ---")
text = "Python"
reversed_text = text[::-1]

print(f"Original: {text}")
print(f"Reversed: {reversed_text}")

# Explanation:
# [::-1] is slicing with step -1 (goes backwards)
# [start:end:step] - when omitted, start=0, end=len, step=1
# Negative step reverses the string


# Exercise 10: Circle Calculator
print("\n--- Exercise 10: Circle Calculator ---")
import math

radius = 5
area = math.pi * (radius ** 2)
circumference = 2 * math.pi * radius

print(f"Radius: {radius}")
print(f"Area: {area:.2f}")
print(f"Circumference: {circumference:.2f}")

# Explanation:
# math.pi provides accurate value of π
# Area formula: π × r²
# Circumference formula: 2 × π × r


# ============================================================================
# LEVEL 3: CHALLENGING
# ============================================================================

print("\n" + "="*60)
print("LEVEL 3: CHALLENGING")
print("="*60)

# Exercise 11: Swap Without Temp
print("\n--- Exercise 11: Swap Without Temp ---")
a = 10
b = 20

print(f"Before swap: a = {a}, b = {b}")

# Method 1: Tuple unpacking (Pythonic way)
a, b = b, a

print(f"After swap: a = {a}, b = {b}")

# Explanation:
# Python evaluates right side first: (b, a) creates a tuple (20, 10)
# Then unpacks to: a = 20, b = 10
# This is the most Pythonic way to swap values

# Alternative methods:
# Method 2: Arithmetic (works only for numbers)
# a = a + b  # a becomes 30
# b = a - b  # b becomes 10
# a = a - b  # a becomes 20

# Method 3: XOR (bitwise, works for integers)
# a = a ^ b
# b = a ^ b
# a = a ^ b


# Exercise 12: Type Conversion Chain
print("\n--- Exercise 12: Type Conversion Chain ---")
value = "42"
print(f"Start: '{value}' (type: {type(value).__name__})")

# Convert to int and multiply
value = int(value)
print(f"After int(): {value} (type: {type(value).__name__})")

value = value * 2
print(f"After *2: {value} (type: {type(value).__name__})")

# Convert to float and divide
value = float(value)
print(f"After float(): {value} (type: {type(value).__name__})")

value = value / 3
print(f"After /3: {value} (type: {type(value).__name__})")

# Convert to string and concatenate
value = str(value)
result = value + " is the answer"
print(f"Final: '{result}' (type: {type(result).__name__})")

# Explanation:
# Type conversions are explicit in Python (strong typing)
# Each conversion creates a new object
# Division always returns float, even for integers


# Exercise 13: Identity vs Equality
print("\n--- Exercise 13: Identity vs Equality ---")
list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1

print(f"list1: {list1} (id: {id(list1)})")
print(f"list2: {list2} (id: {id(list2)})")
print(f"list3: {list3} (id: {id(list3)})")

print(f"\nlist1 == list2: {list1 == list2} (same content)")
print(f"list1 is list2: {list1 is list2} (same object)")
print(f"\nlist1 == list3: {list1 == list3} (same content)")
print(f"list1 is list3: {list1 is list3} (same object)")

# Explanation:
# == checks if values are equal (content comparison)
# is checks if variables refer to the same object (identity comparison)
# list1 and list3 point to the SAME object in memory
# list2 is a DIFFERENT object with the same content


# Exercise 14: Mutable Modification
print("\n--- Exercise 14: Mutable Modification ---")
original = [1, 2, 3]
reference = original

print(f"Before modification:")
print(f"original: {original} (id: {id(original)})")
print(f"reference: {reference} (id: {id(reference)})")

original.append(4)

print(f"\nAfter original.append(4):")
print(f"original: {original} (id: {id(original)})")
print(f"reference: {reference} (id: {id(reference)})")

print("\nExplanation:")
print("Both variables point to the SAME list object.")
print("Modifying the list through either variable affects both.")
print("This is because lists are MUTABLE objects.")

# Key Insight:
# When you do reference = original, you're NOT copying the list
# You're creating another reference to the SAME list
# To create a copy, use: reference = original.copy()


# Exercise 15: Memory Explorer
print("\n--- Exercise 15: Memory Explorer ---")

# Small integers (typically -5 to 256 are cached)
a = 10
b = 10
c = 10

print("Small integers (10):")
print(f"a: id = {id(a)}")
print(f"b: id = {id(b)}")
print(f"c: id = {id(c)}")
print(f"All same? {id(a) == id(b) == id(c)}")

# Large integers (not cached)
x = 1000
y = 1000
z = 1000

print("\nLarge integers (1000):")
print(f"x: id = {id(x)}")
print(f"y: id = {id(y)}")
print(f"z: id = {id(z)}")
print(f"All same? {id(x) == id(y) == id(z)}")

print("\nExplanation:")
print("Python caches small integers (-5 to 256) for efficiency.")
print("Small integers with same value share the same object.")
print("Larger integers create separate objects each time.")
print("This is called 'integer interning' - an optimization.")

# Explanation:
# Python optimizes memory by reusing small integer objects
# This is safe because integers are IMMUTABLE
# For larger numbers, Python creates separate objects


# ============================================================================
# BONUS CHALLENGES
# ============================================================================

print("\n" + "="*60)
print("BONUS CHALLENGES")
print("="*60)

# Exercise 16: String Manipulation Master
print("\n--- Exercise 16: String Manipulation Master ---")
text = "  Python Programming  "

print(f"Original: '{text}'")

# Step 1: Remove whitespace
step1 = text.strip()
print(f"After strip(): '{step1}'")

# Step 2: Replace Programming with Development
step2 = step1.replace("Programming", "Development")
print(f"After replace(): '{step2}'")

# Step 3: Convert to uppercase
step3 = step2.upper()
print(f"After upper(): '{step3}'")

# Step 4: Split into list
step4 = step3.split()
print(f"After split(): {step4}")

# All in one line (method chaining)
result = text.strip().replace("Programming", "Development").upper().split()
print(f"One-liner result: {result}")


# Exercise 17: Number Games
print("\n--- Exercise 17: Number Games ---")
number = 987654

# Last digit
last_digit = number % 10
print(f"Number: {number}")
print(f"Last digit: {last_digit}")

# First digit
first_digit = int(str(number)[0])
print(f"First digit: {first_digit}")

# Sum of all digits
digit_sum = sum(int(digit) for digit in str(number))
print(f"Sum of digits: {digit_sum}")

# Detailed explanation of sum:
print("\nStep-by-step sum calculation:")
for digit in str(number):
    print(f"  Digit: {digit} (int: {int(digit)})")


# Exercise 18: Boolean Logic
print("\n--- Exercise 18: Boolean Logic ---")
age = 25
has_license = True
has_car = False

# Check conditions
can_drive = age >= 18 and has_license
needs_car = has_license and not has_car
ready_to_drive = can_drive and has_car

print(f"Age: {age}")
print(f"Has license: {has_license}")
print(f"Has car: {has_car}")
print()
print(f"Can drive? {can_drive}")
print(f"Needs car? {needs_car}")
print(f"Ready to drive? {ready_to_drive}")

# Detailed breakdown
print("\nDetailed breakdown:")
print(f"Can drive = (age >= 18) AND (has_license)")
print(f"          = ({age >= 18}) AND ({has_license})")
print(f"          = {age >= 18} AND {has_license}")
print(f"          = {can_drive}")


print("\n" + "="*60)
print("All Solutions Completed!")
print("="*60)
print("\nKey Learnings:")
print("1. Python syntax is clean and readable")
print("2. Type conversions must be explicit")
print("3. Strings are immutable, lists are mutable")
print("4. == checks equality, is checks identity")
print("5. Python optimizes memory for small integers")
print("6. Understanding these fundamentals is crucial!")
