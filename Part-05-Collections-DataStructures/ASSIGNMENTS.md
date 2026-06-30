# Part 5: Collections & Data Structures - Practice Problems

> Test list, tuple, set, dict, and advanced collections

---

## Problem 1: List Operations

**Task**: Remove duplicates preserving order
```python
def remove_duplicates(items):
    # [1, 2, 2, 3, 1] → [1, 2, 3]
    pass

assert remove_duplicates([1, 2, 2, 3, 1]) == [1, 2, 3]
```

**Time**: 10 minutes

---

## Problem 2: List Comprehension

**Task**: Squares of even numbers
```python
numbers = [1, 2, 3, 4, 5, 6]
# Get [4, 16, 36] using list comprehension
```

**Time**: 5 minutes

---

## Problem 3: Tuple Unpacking

**Task**: Swap without temp variable
```python
a, b = 5, 10
# Swap using tuple unpacking
# Result: a=10, b=5
```

**Time**: 5 minutes

---

## Problem 4: Set Operations

**Task**: Common and unique elements
```python
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

# Find: intersection, union, difference
common = ?
all_items = ?
only_in_set1 = ?
```

**Time**: 10 minutes

---

## Problem 5: Dictionary Methods

**Task**: Count word frequency
```python
def word_count(text):
    # Return dict: {"hello": 2, "world": 1}
    pass

assert word_count("hello world hello") == {"hello": 2, "world": 1}
```

**Time**: 15 minutes

---

## Problem 6: DefaultDict

**Task**: Group by first letter
```python
from collections import defaultdict

words = ["apple", "banana", "apricot", "blueberry"]
# Group: {"a": ["apple", "apricot"], "b": ["banana", "blueberry"]}
```

**Time**: 15 minutes

---

## Problem 7: Counter

**Task**: Most common elements
```python
from collections import Counter

numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
# Find top 2 most common with counts
```

**Time**: 10 minutes

---

## Problem 8: Deque

**Task**: Sliding window max size 3
```python
from collections import deque

def add_to_window(window, item):
    # Keep max 3 items (FIFO)
    pass

window = deque(maxlen=3)
```

**Time**: 10 minutes

---

## Problem 9: Named Tuple

**Task**: Point with x, y
```python
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
assert p.x == 10
assert p[1] == 20
```

**Time**: 10 minutes

---

## Problem 10: Heapq

**Task**: Find 3 smallest numbers
```python
import heapq

numbers = [5, 2, 9, 1, 7, 3]
# Use heapq.nsmallest to get [1, 2, 3]
```

**Time**: 10 minutes

---

## Summary Check

**8+ solved** → Collections mastered  
**5-7 solved** → Practice set operations and advanced collections  
**< 5 solved** → Review data structures chapter
