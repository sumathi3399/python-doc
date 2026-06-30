# Part 7: Type Hints & Annotations - Practice Problems

> Test typing, generics, protocols

---

## Problem 1: Basic Annotations

**Task**: Annotate function
```python
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> str:
    return f"Hello, {name}"
```

**Time**: 5 minutes

---

## Problem 2: Optional Types

**Task**: Function returning optional value
```python
from typing import Optional

def find_user(user_id: int) -> Optional[dict]:
    # Return user dict or None
    if user_id == 1:
        return {"name": "Alice"}
    return None
```

**Time**: 10 minutes

---

## Problem 3: List and Dict Types

**Task**: Type collections
```python
from typing import List, Dict

def process_scores(scores: List[int]) -> Dict[str, float]:
    return {
        "average": sum(scores) / len(scores),
        "max": float(max(scores))
    }
```

**Time**: 10 minutes

---

## Problem 4: Union Types

**Task**: Multiple return types
```python
from typing import Union

def parse_value(value: str) -> Union[int, float, str]:
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value
```

**Time**: 15 minutes

---

## Problem 5: Type Aliases

**Task**: Create type alias
```python
from typing import List, Tuple

# Define type aliases
Vector = List[float]
Point = Tuple[float, float]

def distance(p1: Point, p2: Point) -> float:
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
```

**Time**: 10 minutes

---

## Problem 6: Generic Function

**Task**: First element of any list
```python
from typing import TypeVar, List

T = TypeVar('T')

def first(items: List[T]) -> T:
    return items[0]

# Works with List[int], List[str], etc.
```

**Time**: 15 minutes

---

## Problem 7: Callable Type

**Task**: Function that takes function
```python
from typing import Callable

def apply_twice(func: Callable[[int], int], value: int) -> int:
    return func(func(value))

def double(x: int) -> int:
    return x * 2

assert apply_twice(double, 3) == 12
```

**Time**: 15 minutes

---

## Problem 8: Literal Types

**Task**: Direction type
```python
from typing import Literal

Direction = Literal["north", "south", "east", "west"]

def move(direction: Direction) -> str:
    return f"Moving {direction}"

# move("north") is valid
# move("up") would be type error in mypy
```

**Time**: 10 minutes

---

## Problem 9: Protocol

**Task**: Duck typing with protocol
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str:
        ...

class Circle:
    def draw(self) -> str:
        return "Drawing circle"

def render(shape: Drawable) -> None:
    print(shape.draw())

render(Circle())  # Works without inheritance
```

**Time**: 20 minutes

---

## Problem 10: TypedDict

**Task**: Typed dictionary
```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str

def create_user(name: str, age: int, email: str) -> UserDict:
    return {"name": name, "age": age, "email": email}
```

**Time**: 15 minutes

---

## Summary Check

**8+ solved** → Type hints mastered  
**5-7 solved** → Practice generics and protocols  
**< 5 solved** → Review typing module
