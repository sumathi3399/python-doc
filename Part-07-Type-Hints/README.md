# Part 7: Type Hints & Annotations

> Add type safety to your Python code for better IDE support and fewer bugs.

## 📚 Table of Contents

1. [Introduction to Type Hints](#1-introduction-to-type-hints)
2. [Basic Type Annotations](#2-basic-type-annotations)
3. [Advanced Types](#3-advanced-types)
4. [Function Annotations](#4-function-annotations)
5. [Type Checking with mypy](#5-type-checking-with-mypy)
6. [Best Practices](#6-best-practices)
7. [Exercises](#exercises)

---

## 1. Introduction to Type Hints

### What are Type Hints?

Type hints are **annotations** that specify the expected types of variables, function parameters, and return values. They're optional but provide benefits:

- **Better IDE support** (autocomplete, refactoring)
- **Catch bugs early** (static type checking)
- **Self-documenting code** (clear expectations)
- **Refactoring safety** (find affected code)

```python
# Without type hints
def greet(name):
    return f"Hello, {name}!"

# With type hints
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

### Runtime Behavior

**Important**: Type hints don't affect runtime!

```python
def add(a: int, b: int) -> int:
    return a + b

# This still works (no runtime error)
result = add("hello", "world")  # "helloworld"
print(result)

# Type checker (mypy) would catch this error!
```

---

## 2. Basic Type Annotations

### Variable Annotations

```python
# Basic types
name: str = "Alice"
age: int = 25
height: float = 5.8
is_student: bool = True

# Without initial value
user_id: int
user_id = 123

# None type
result: None = None
```

### Built-in Collection Types

```python
from typing import List, Dict, Set, Tuple

# List
numbers: List[int] = [1, 2, 3, 4, 5]
names: List[str] = ["Alice", "Bob"]

# Dictionary
scores: Dict[str, int] = {"Alice": 95, "Bob": 87}
config: Dict[str, str] = {"host": "localhost"}

# Set
unique_ids: Set[int] = {1, 2, 3, 4}

# Tuple (fixed size)
point: Tuple[int, int] = (10, 20)
person: Tuple[str, int, str] = ("Alice", 25, "NYC")

# Tuple (variable size)
numbers: Tuple[int, ...] = (1, 2, 3, 4, 5)
```

### Python 3.9+ Simplified Syntax

```python
# Python 3.9+ allows using built-in types directly
numbers: list[int] = [1, 2, 3]
scores: dict[str, int] = {"Alice": 95}
unique: set[str] = {"a", "b"}
point: tuple[int, int] = (10, 20)
```

---

## 3. Advanced Types

### Optional

```python
from typing import Optional

# Optional[T] means T or None
def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None  # OK

# Equivalent to Union[str, None]
name: Optional[str] = None
name = "Alice"  # OK
```

### Union

```python
from typing import Union

# Can be one of multiple types
def process_id(id: Union[int, str]) -> str:
    return str(id)

process_id(123)      # OK
process_id("abc")    # OK
# process_id(3.14)   # Error (not int or str)

# Multiple types
value: Union[int, float, str] = 42
```

### Any

```python
from typing import Any

# Any type allowed (escape hatch)
def process(data: Any) -> Any:
    return data

process(123)        # OK
process("hello")    # OK
process([1, 2, 3])  # OK
```

### Literal

```python
from typing import Literal

# Only specific values allowed
def set_status(status: Literal["active", "inactive"]) -> None:
    print(f"Status: {status}")

set_status("active")     # OK
# set_status("pending")  # Error!

# Use with Union
Mode = Literal["r", "w", "a"]
def open_file(mode: Mode) -> None:
    pass
```

### TypeVar (Generics)

```python
from typing import TypeVar, List

T = TypeVar('T')

def first(items: List[T]) -> T:
    return items[0]

# Type is preserved
numbers = [1, 2, 3]
result: int = first(numbers)  # OK, result is int

names = ["Alice", "Bob"]
name: str = first(names)  # OK, name is str
```

### Callable

```python
from typing import Callable

# Function type
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

def add(x: int, y: int) -> int:
    return x + y

result = apply(add, 5, 3)  # OK

# Callable with no args
def run(callback: Callable[[], None]) -> None:
    callback()
```

---

## 4. Function Annotations

### Basic Function Annotations

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

def print_message(message: str) -> None:
    print(message)
```

### Default Arguments

```python
def create_user(
    name: str,
    age: int = 18,
    email: Optional[str] = None
) -> dict[str, Any]:
    return {"name": name, "age": age, "email": email}
```

### *args and **kwargs

```python
from typing import Any

def log(*messages: str) -> None:
    for msg in messages:
        print(msg)

def configure(**options: Any) -> None:
    for key, value in options.items():
        print(f"{key}: {value}")
```

### Multiple Return Values

```python
def get_min_max(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)

minimum, maximum = get_min_max([1, 5, 3, 9, 2])
```

---

## 5. Type Checking with mypy

### Installing mypy

```bash
pip install mypy
```

### Running mypy

```bash
# Check single file
mypy script.py

# Check directory
mypy src/

# Strict mode
mypy --strict script.py
```

### Example with Errors

```python
# example.py
def add(a: int, b: int) -> int:
    return a + b

result: int = add(5, "3")  # Type error!
```

```bash
$ mypy example.py
example.py:4: error: Argument 2 to "add" has incompatible type "str"; expected "int"
Found 1 error in 1 file (checked 1 source file)
```

### Configuring mypy

Create `mypy.ini`:

```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Type Ignoring

```python
result = some_library_function()  # type: ignore

# With comment
result = legacy_code()  # type: ignore[attr-defined]
```

---

## 6. Best Practices

### 1. Start Gradually

```python
# Begin with function signatures
def process_data(data: dict) -> list:
    # Implementation...
    pass

# Add more detail over time
def process_data(data: dict[str, Any]) -> list[str]:
    # Implementation...
    pass
```

### 2. Use Type Aliases

```python
from typing import Union

# Define alias
UserId = Union[int, str]
Coordinates = tuple[float, float]

def get_user(user_id: UserId) -> dict:
    pass

def calculate_distance(start: Coordinates, end: Coordinates) -> float:
    pass
```

### 3. Document Complex Types

```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str

def create_user(data: UserDict) -> None:
    print(data["name"])
```

### 4. Use Protocol for Duck Typing

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...

def render(obj: Drawable) -> None:
    obj.draw()

# Any class with draw() method works
class Circle:
    def draw(self) -> None:
        print("Drawing circle")

render(Circle())  # OK
```

---

## Exercises

### Level 1: Basics

1. **Annotate Variables**
   - Create 10 variables of different types
   - Add type hints

2. **Function Signatures**
   - Write 5 functions
   - Add parameter and return type hints

3. **Collection Types**
   - Create list, dict, set with type hints
   - Nested collections

### Level 2: Intermediate

4. **Optional Types**
   - Function that may return None
   - Use Optional properly

5. **Union Types**
   - Function accepting multiple types
   - Proper handling of each type

6. **Type Aliases**
   - Create aliases for complex types
   - Use in function signatures

### Level 3: Challenging

7. **Generic Function**
   - Use TypeVar
   - Works with any type

8. **Protocol**
   - Define protocol
   - Multiple implementations

9. **Complete Module**
   - Fully typed module
   - Pass mypy --strict

---

## Key Takeaways

✅ **Type Hints Benefits**:
- Better IDE support
- Catch bugs early
- Self-documenting
- Safe refactoring

✅ **Basic Types**:
- int, str, float, bool
- list, dict, set, tuple
- Optional, Union, Any

✅ **Advanced**:
- TypeVar for generics
- Protocol for duck typing
- Literal for specific values
- Callable for functions

✅ **Tools**:
- mypy for type checking
- Type hints are optional
- Don't affect runtime

---

Continue to [Part-08-Decorators](../Part-08-Decorators/README.md)!
