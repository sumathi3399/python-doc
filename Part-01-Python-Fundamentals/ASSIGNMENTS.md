# Part 1: Python Fundamentals - Practice Problems

> **Purpose**: Quick skill checks to verify you understand the concepts. If you can solve these, you can move forward. If not, review the section.

---

## Problem 1: Python Execution Model

**Concept**: Understand bytecode compilation

**Task**: Create a Python script that:
1. Writes a simple function to a `.py` file
2. Uses `py_compile` to compile it to `.pyc`
3. Prints the location of the bytecode file

**Expected output**:
```
Created: example.py
Compiled to: __pycache__/example.cpython-311.pyc
```

**Time**: 10-15 minutes

---

## Problem 2: Memory References and id()

**Concept**: Variables as references, integer interning

**Task**: Write code that demonstrates:
```python
a = 257
b = 257
c = 256
d = 256

# Print whether a is b
# Print whether c is d
# Explain why in comments
```

**Verify**: `c is d` should be `True`, `a is b` should be `False`

**Time**: 5-10 minutes

---

## Problem 3: Type Conversion Chain

**Concept**: Type coercion and conversion

**Task**: Complete this conversion chain without errors:
- Start with string `"42"`
- Convert to int, multiply by 2
- Convert to float, divide by 3
- Convert back to string, concatenate with " is the answer"
- Print final result

**Expected output**: `"28.0 is the answer"`

**Time**: 5 minutes

---

## Problem 4: Mutable vs Immutable

**Concept**: Understanding mutability

**Task**: Predict and verify the output:
```python
# Case 1: List (mutable)
list1 = [1, 2, 3]
list2 = list1
list1.append(4)
print(list2)  # What prints?

# Case 2: String (immutable)
str1 = "hello"
str2 = str1
str1 = str1 + " world"
print(str2)  # What prints?
```

Write the predictions as comments, then run to verify.

**Time**: 10 minutes

---

## Problem 5: Operators & Precedence

**Concept**: Operator precedence and types

**Task**: Calculate these without running first, then verify:
```python
result1 = 10 + 3 * 2
result2 = (10 + 3) * 2
result3 = 10 / 3
result4 = 10 // 3
result5 = 10 % 3
result6 = 2 ** 3 ** 2  # Right associative!
```

Write expected values as comments, then print to check.

**Time**: 10 minutes

---

## Problem 6: is vs ==

**Concept**: Identity vs equality

**Task**: Fix this code to use correct comparison:
```python
def check_none(value):
    # Bug: using == instead of is
    if value == None:
        return "Empty"
    return "Has value"

# Also demonstrate when == and is differ
x = [1, 2, 3]
y = [1, 2, 3]
# x == y: ?
# x is y: ?
```

**Time**: 10 minutes

---

## Problem 7: Truthiness Table

**Concept**: Truthy and falsy values

**Task**: Complete this truth table program:
```python
values = [0, 1, "", "hello", [], [1], None, False, True]

for val in values:
    print(f"{repr(val):15} -> {bool(val)}")
```

Add comments explaining why each is truthy/falsy.

**Time**: 10-15 minutes

---

## Problem 8: Variable Scope

**Concept**: Global vs local scope

**Task**: Fix the scope issues in this code:
```python
count = 0

def increment():
    count = count + 1  # UnboundLocalError!
    return count

def increment_correct():
    # Fix it here using global
    pass

# Test both versions
```

**Time**: 10 minutes

---

## Problem 9: Data Type Quiz

**Concept**: All basic types

**Task**: Write a function `analyze_value(val)` that returns a dict:
```python
{
    "type": "int" | "float" | "str" | "bool" | "NoneType",
    "value": val,
    "is_numeric": True/False,
    "is_truthy": True/False
}
```

Test with: `42`, `3.14`, `"hello"`, `True`, `None`, `0`, `""`

**Time**: 15-20 minutes

---

## Problem 10: String Operations

**Concept**: String immutability and methods

**Task**: Clean user input:
```python
def clean_username(username):
    # 1. Strip whitespace
    # 2. Convert to lowercase
    # 3. Replace spaces with underscores
    # 4. Return cleaned username
    pass

# Test cases
assert clean_username("  John Doe  ") == "john_doe"
assert clean_username("ALICE") == "alice"
```

**Time**: 10 minutes

---

## Summary Check

If you solved **8+ problems** without looking at solutions → **You're ready for Part 2!**

If you solved **5-7 problems** → Review tough sections, try again

If you solved **< 5 problems** → Study Part 1 material again carefully
