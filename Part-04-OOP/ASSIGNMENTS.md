# Part 4: Object-Oriented Programming - Practice Problems

> Test OOP concepts: classes, inheritance, magic methods

---

## Problem 1: Basic Class

**Task**: Create Person class
```python
class Person:
    def __init__(self, name, age):
        pass
    
    def introduce(self):
        return f"Hi, I'm {self.name} and I'm {self.age}"

p = Person("Alice", 25)
assert p.introduce() == "Hi, I'm Alice and I'm 25"
```

**Time**: 10 minutes

---

## Problem 2: Class vs Instance Variables

**Task**: Count instances
```python
class Counter:
    count = 0  # Class variable
    
    def __init__(self):
        # Increment count
        pass

c1 = Counter()
c2 = Counter()
assert Counter.count == 2
```

**Time**: 10 minutes

---

## Problem 3: Inheritance

**Task**: Animal hierarchy
```python
class Animal:
    def speak(self):
        return "Some sound"

class Dog(Animal):
    def speak(self):
        return "Woof!"

dog = Dog()
assert dog.speak() == "Woof!"
```

**Time**: 10 minutes

---

## Problem 4: `__str__` and `__repr__`

**Task**: String representations
```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author
    
    def __str__(self):
        # User-friendly: "Title by Author"
        pass
    
    def __repr__(self):
        # Dev-friendly: "Book('Title', 'Author')"
        pass

book = Book("1984", "Orwell")
print(book)  # Should use __str__
```

**Time**: 15 minutes

---

## Problem 5: `__eq__` Method

**Task**: Compare objects
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        # Equal if same x and y
        pass

assert Point(1, 2) == Point(1, 2)
assert Point(1, 2) != Point(2, 1)
```

**Time**: 10 minutes

---

## Problem 6: Property Decorator

**Task**: Temperature with validation
```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Below absolute zero")
        self._celsius = value

temp = Temperature(0)
assert temp.fahrenheit == 32
```

**Time**: 20 minutes

---

## Problem 7: Static Method

**Task**: Utility method
```python
class MathUtils:
    @staticmethod
    def is_even(n):
        # No access to self/cls needed
        pass

assert MathUtils.is_even(4) == True
assert MathUtils.is_even(5) == False
```

**Time**: 5 minutes

---

## Problem 8: Class Method

**Task**: Alternative constructor
```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_string(cls, date_string):
        # Parse "2024-01-15" and create Date
        pass

date = Date.from_string("2024-01-15")
assert date.year == 2024
```

**Time**: 15 minutes

---

## Problem 9: Dataclass

**Task**: Product with dataclass
```python
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0
    
    def total_value(self):
        return self.price * self.quantity

p = Product("Widget", 9.99, 5)
assert p.total_value() == 49.95
```

**Time**: 10 minutes

---

## Problem 10: Composition

**Task**: Car has Engine
```python
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower

class Car:
    def __init__(self, model, engine):
        self.model = model
        self.engine = engine  # Composition

engine = Engine(200)
car = Car("Toyota", engine)
assert car.engine.horsepower == 200
```

**Time**: 10 minutes

---

## Summary Check

**8+ solved** → OOP mastered  
**5-7 solved** → Review inheritance and magic methods  
**< 5 solved** → Study OOP fundamentals again
