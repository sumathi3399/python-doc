# Part 2: Control Flow - Practice Problems

> Quick checks for conditionals, loops, and control flow keywords

---

## Problem 1: If-Elif-Else Chain

**Task**: Grade calculator
```python
def get_grade(score):
    # Return: A (>=90), B (>=80), C (>=70), D (>=60), F (<60)
    pass

# Test
assert get_grade(95) == "A"
assert get_grade(72) == "C"
assert get_grade(55) == "F"
```

**Time**: 5-10 minutes

---

## Problem 2: Compound Conditions

**Task**: Age and membership check
```python
def can_enter_club(age, is_member):
    # Allow if: (age >= 21) OR (age >= 18 AND is_member)
    pass

assert can_enter_club(22, False) == True
assert can_enter_club(19, True) == True
assert can_enter_club(17, True) == False
```

**Time**: 10 minutes

---

## Problem 3: For Loop with Range

**Task**: Print multiplication table
```python
def multiplication_table(n):
    # Print: 1 x n = n, 2 x n = 2n, ... 10 x n = 10n
    pass
```

**Expected output** for `multiplication_table(5)`:
```
1 x 5 = 5
2 x 5 = 10
...
10 x 5 = 50
```

**Time**: 10 minutes

---

## Problem 4: While Loop with Counter

**Task**: Count down
```python
def countdown(n):
    # Print from n to 1, then "Blast off!"
    # Use while loop
    pass
```

**Time**: 5 minutes

---

## Problem 5: Break Statement

**Task**: Find first number divisible by 7
```python
def find_first_multiple_of_7(numbers):
    # Return first number divisible by 7, or None
    # Use break
    pass

assert find_first_multiple_of_7([3, 5, 14, 21, 28]) == 14
assert find_first_multiple_of_7([1, 2, 3]) == None
```

**Time**: 10 minutes

---

## Problem 6: Continue Statement

**Task**: Print only odd numbers
```python
def print_odds(numbers):
    for num in numbers:
        # Skip even numbers using continue
        pass
```

**Time**: 5 minutes

---

## Problem 7: Loop Else Clause

**Task**: Search with else
```python
def find_item(items, target):
    for item in items:
        if item == target:
            return f"Found {target}"
            break
    else:
        return f"{target} not found"

# Test it
```

**Time**: 10 minutes

---

## Problem 8: Enumerate

**Task**: Index with value
```python
students = ["Alice", "Bob", "Charlie"]
# Print: "1. Alice", "2. Bob", "3. Charlie"
# Use enumerate starting from 1
```

**Time**: 5 minutes

---

## Problem 9: Nested Loops

**Task**: Pattern printing
```python
# Print this pattern:
# *
# **
# ***
# ****
# Use nested loops or repeat
```

**Time**: 10 minutes

---

## Problem 10: Zip Function

**Task**: Combine parallel lists
```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]
# Print: "Alice: 85", "Bob: 92", "Charlie: 78"
# Use zip
```

**Time**: 5 minutes

---

## Summary Check

**8+ solved** → Ready for Part 3  
**5-7 solved** → Review loops and break/continue  
**< 5 solved** → Revisit control flow concepts
