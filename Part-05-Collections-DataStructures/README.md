# Part 5: Collections & Data Structures

> Master Python's built-in data structures and learn to choose the right tool for every task.

## 📚 Table of Contents

1. [Introduction to Data Structures](#1-introduction-to-data-structures)
2. [Lists - Deep Dive](#2-lists---deep-dive)
3. [Tuples](#3-tuples)
4. [Sets](#4-sets)
5. [Dictionaries](#5-dictionaries)
6. [Advanced Collections](#6-advanced-collections)
7. [Time Complexity](#7-time-complexity)
8. [Choosing the Right Data Structure](#8-choosing-the-right-data-structure)
9. [Exercises](#exercises)

---

## 1. Introduction to Data Structures

### What is a Data Structure?

A **data structure** is a way of organizing and storing data so you can perform operations efficiently.

### Why Different Data Structures?

```python
# Problem: Check if item exists

# Bad: Using wrong data structure
items_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 1000
if 5000 in items_list:  # Slow! O(n)
    print("Found")

# Good: Using right data structure
items_set = set(range(10000))
if 5000 in items_set:  # Fast! O(1)
    print("Found")
```

### Python's Built-in Data Structures

| Structure | Ordered | Mutable | Duplicates | Use Case |
|-----------|---------|---------|------------|----------|
| **List** | ✅ | ✅ | ✅ | General purpose collection |
| **Tuple** | ✅ | ❌ | ✅ | Immutable sequences |
| **Set** | ❌ | ✅ | ❌ | Unique items, fast lookup |
| **Dict** | ✅* | ✅ | ❌ (keys) | Key-value pairs |

*Ordered since Python 3.7+

---

## 2. Lists - Deep Dive

### List Methods - Complete Reference

#### Adding Elements

```python
fruits = ["apple", "banana"]

# append() - Add single item to end - O(1)
fruits.append("orange")
print(fruits)  # ['apple', 'banana', 'orange']

# extend() - Add multiple items - O(k)
fruits.extend(["grape", "mango"])

# insert() - Add at specific position - O(n)
fruits.insert(0, "strawberry")
```

#### List Comprehensions

```python
# Basic comprehension
squares = [x**2 for x in range(10)]

# With condition
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# Nested comprehension
matrix = [[i*j for j in range(5)] for i in range(5)]

# Flatten 2D list
matrix = [[1, 2], [3, 4]]
flat = [item for row in matrix for item in row]
```

### List Copying - Shallow vs Deep

```python
# Shallow copy
original = [[1, 2], [3, 4]]
shallow = original.copy()
shallow[0].append(99)
print(original)  # [[1, 2, 99], [3, 4]] - Nested affected!

# Deep copy
import copy
original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)
deep[0].append(99)
print(original)  # [[1, 2], [3, 4]] - Safe!
```

---

## 3. Tuples

### Why Use Tuples?

**1. Immutability = Safety**
```python
config = ("localhost", 5432, "mydb")
# config[1] = 9999  # TypeError! Safe from changes
```

**2. Dictionary Keys**
```python
locations = {(10, 20): "Point A", (30, 40): "Point B"}
```

### Named Tuples

```python
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
print(p.x, p.y)  # 10 20
```

---

## 4. Sets

### Set Operations

```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

union = a | b          # {1, 2, 3, 4, 5, 6, 7, 8}
intersection = a & b   # {4, 5}
difference = a - b     # {1, 2, 3}
sym_diff = a ^ b       # {1, 2, 3, 6, 7, 8}
```

### Use Cases

**Remove Duplicates:**
```python
numbers = [1, 2, 2, 3, 3, 4]
unique = list(set(numbers))
```

**Fast Membership:**
```python
valid_users = {"alice", "bob", "charlie"}
if "alice" in valid_users:  # O(1)
    print("Valid")
```

---

## 5. Dictionaries

### Dictionary Methods

```python
person = {"name": "Alice", "age": 25}

# Safe access
email = person.get("email", "N/A")

# Iterate
for key, value in person.items():
    print(f"{key}: {value}")

# Merge
person.update({"city": "NYC"})

# Set default
person.setdefault("phone", "123-456")
```

### Advanced Techniques

**Dictionary Comprehension:**
```python
squares = {x: x**2 for x in range(5)}
```

**Invert Dictionary:**
```python
original = {"a": 1, "b": 2}
inverted = {v: k for k, v in original.items()}
```

---

## 6. Advanced Collections

### defaultdict

```python
from collections import defaultdict

# Auto-initialize missing keys
word_count = defaultdict(int)
for word in ["apple", "banana", "apple"]:
    word_count[word] += 1
print(dict(word_count))  # {'apple': 2, 'banana': 1}

# Group items
groups = defaultdict(list)
for item, category in [("apple", "fruit"), ("carrot", "veg")]:
    groups[category].append(item)
```

### Counter

```python
from collections import Counter

# Count elements
words = ["apple", "banana", "apple", "orange", "banana", "apple"]
counts = Counter(words)
print(counts)  # Counter({'apple': 3, 'banana': 2, 'orange': 1})

# Most common
print(counts.most_common(2))  # [('apple', 3), ('banana', 2)]

# Add counts
c1 = Counter(['a', 'b'])
c2 = Counter(['b', 'c'])
print(c1 + c2)  # Counter({'b': 2, 'a': 1, 'c': 1})
```

### deque (Double-Ended Queue)

```python
from collections import deque

# Fast append/pop from both ends - O(1)
dq = deque([1, 2, 3])
dq.append(4)        # Add to right
dq.appendleft(0)    # Add to left
dq.pop()            # Remove from right
dq.popleft()        # Remove from left

# Rotate
dq.rotate(1)   # Rotate right
dq.rotate(-1)  # Rotate left

# Use case: Recent items
recent = deque(maxlen=3)
for i in range(10):
    recent.append(i)
print(recent)  # deque([7, 8, 9], maxlen=3)
```

### heapq (Priority Queue)

```python
import heapq

# Min heap
heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 3)
heapq.heappush(heap, 7)

smallest = heapq.heappop(heap)  # 3

# Get N largest/smallest
numbers = [5, 2, 8, 1, 9, 3, 7]
largest_3 = heapq.nlargest(3, numbers)
print(largest_3)  # [9, 8, 7]

smallest_3 = heapq.nsmallest(3, numbers)
print(smallest_3)  # [1, 2, 3]
```

### OrderedDict

```python
from collections import OrderedDict

# Maintains insertion order (less needed in Python 3.7+)
ordered = OrderedDict()
ordered['a'] = 1
ordered['b'] = 2
ordered['c'] = 3

# Move to end
ordered.move_to_end('a')
print(ordered)  # OrderedDict([('b', 2), ('c', 3), ('a', 1)])

# Move to beginning
ordered.move_to_end('a', last=False)
```

### ChainMap

```python
from collections import ChainMap

# Combine multiple dicts
defaults = {'color': 'blue', 'size': 'medium'}
user = {'color': 'red'}

config = ChainMap(user, defaults)
print(config['color'])  # 'red' (from user)
print(config['size'])   # 'medium' (from defaults)
```

---

## 7. Time Complexity

### Big O Notation Basics

**O(1) - Constant**: Always same time
**O(n) - Linear**: Time grows with input size
**O(n²) - Quadratic**: Nested loops
**O(log n) - Logarithmic**: Binary search
**O(n log n) - Linearithmic**: Efficient sorting

### List Operations

| Operation | Time Complexity |
|-----------|----------------|
| append() | O(1) |
| pop() from end | O(1) |
| pop(0) from start | O(n) |
| insert(i, x) | O(n) |
| x in list | O(n) |
| list[i] | O(1) |
| list.sort() | O(n log n) |

### Dictionary Operations

| Operation | Average | Worst |
|-----------|---------|-------|
| d[key] | O(1) | O(n) |
| key in d | O(1) | O(n) |
| del d[key] | O(1) | O(n) |
| d.items() | O(n) | O(n) |

### Set Operations

| Operation | Average | Worst |
|-----------|---------|-------|
| x in s | O(1) | O(n) |
| s.add(x) | O(1) | O(n) |
| s \\| t (union) | O(len(s)+len(t)) | - |
| s & t (intersection) | O(min(len(s), len(t))) | - |

---

## 8. Choosing the Right Data Structure

### Decision Tree

```
Need key-value pairs?
  → Yes: Use Dict
  → No: Continue

Need unique items only?
  → Yes: Use Set
  → No: Continue

Need order + immutability?
  → Yes: Use Tuple
  → No: Use List
```

### Use Case Examples

**1. Shopping Cart**
```python
# Dict: item_id → quantity
cart = {"item_123": 2, "item_456": 1}
```

**2. Recent History**
```python
# deque with maxlen
from collections import deque
history = deque(maxlen=10)
```

**3. Word Frequency**
```python
# Counter
from collections import Counter
freq = Counter(words)
```

**4. Priority Queue**
```python
# heapq
import heapq
tasks = []
heapq.heappush(tasks, (priority, task))
```

**5. Coordinates**
```python
# Tuple (immutable)
point = (10, 20)
```

---

## Exercises

### Level 1: Basics

1. **List Manipulation**
   - Create list of 10 numbers
   - Add 5 more using different methods
   - Remove duplicates
   - Sort in descending order

2. **Tuple Practice**
   - Create named tuple for Student (name, age, grade)
   - Create 5 students
   - Sort by grade

3. **Set Operations**
   - Two sets of numbers
   - Find union, intersection, difference
   - Check if one is subset of another

4. **Dictionary CRUD**
   - Create user dictionary
   - Add/update/delete keys
   - Iterate and print

5. **Counter Usage**
   - Count letters in a string
   - Find 3 most common

### Level 2: Intermediate

6. **Nested Lists**
   - Create 2D matrix
   - Sum each row
   - Sum each column
   - Find maximum element

7. **Dictionary Grouping**
   - Group students by grade
   - Use defaultdict

8. **Set Analysis**
   - Find common elements in 3 sets
   - Find elements unique to each

9. **Priority Queue**
   - Implement task scheduler with heapq
   - Add tasks with priorities
   - Process highest priority first

10. **Deque Operations**
    - Implement browser history (back/forward)
    - Max 10 items

### Level 3: Challenging

11. **Flatten Nested List**
    - Recursive function to flatten any depth

12. **Dictionary Inversion**
    - Handle multiple keys with same value

13. **LRU Cache**
    - Implement Least Recently Used cache
    - Use OrderedDict

14. **Word Index**
    - Build inverted index (word → line numbers)
    - Use defaultdict

15. **Performance Comparison**
    - Benchmark list vs set lookup
    - 1000, 10000, 100000 items

---

## Projects

### Project 1: Contact Manager
- Store contacts (name, phone, email)
- Search, add, delete, update
- Group by first letter

### Project 2: Inventory System
- Track products (ID, name, quantity, price)
- Add/remove stock
- Low stock alerts
- Sales reporting

### Project 3: Text Analyzer
- Read text file
- Word frequency
- Most common words
- Unique words
- Average word length

---

## Key Takeaways

✅ **Lists**: Ordered, mutable, general purpose
✅ **Tuples**: Ordered, immutable, safe
✅ **Sets**: Unordered, unique, fast lookup
✅ **Dicts**: Key-value, fast access

✅ **Advanced**:
- defaultdict: Auto-initialize
- Counter: Count elements
- deque: Fast both-end operations
- heapq: Priority queue
- OrderedDict: Ordered dict operations

✅ **Performance**: Choose based on operations needed

---

Continue to [Part-06-Exception-Handling](../Part-06-Exception-Handling/README.md)!
