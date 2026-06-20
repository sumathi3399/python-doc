# Part 4: Object-Oriented Programming

> Master OOP concepts - the foundation of modern software design.

## 📚 Table of Contents

1. [Introduction to OOP](#1-introduction-to-oop)
2. [Classes and Objects](#2-classes-and-objects)
3. [The `self` Keyword](#3-the-self-keyword)
4. [Constructors and Initialization](#4-constructors-and-initialization)
5. [Instance vs Class Variables](#5-instance-vs-class-variables)
6. [Methods](#6-methods)
7. [OOP Principles](#7-oop-principles)
8. [Magic Methods (Dunder Methods)](#8-magic-methods-dunder-methods)
9. [Dataclasses](#9-dataclasses)
10. [Exercises](#exercises)

---

## 1. Introduction to OOP

### What is Object-Oriented Programming?

**OOP is a programming paradigm based on "objects" that contain:**
- **Data** (attributes/properties)
- **Behavior** (methods/functions)

### Why OOP?

**Real-World Modeling:**
```python
# Procedural approach
user_name = "Alice"
user_age = 25
user_email = "alice@example.com"

# Object-Oriented approach
class User:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

user = User("Alice", 25, "alice@example.com")
```

**Benefits:**
1. **Organization**: Group related data and behavior
2. **Reusability**: Create templates (classes) and make copies (objects)
3. **Maintainability**: Changes in one place affect all instances
4. **Abstraction**: Hide complex implementation details
5. **Inheritance**: Reuse code from parent classes

---

## 2. Classes and Objects

### Defining a Class

```python
class Dog:
    """A simple Dog class"""
    pass

# Create an object (instance)
my_dog = Dog()
print(type(my_dog))  # <class '__main__.Dog'>
```

### Class with Attributes

```python
class Dog:
    # Class attribute (shared by all instances)
    species = "Canis familiaris"
    
    def __init__(self, name, age):
        # Instance attributes (unique to each instance)
        self.name = name
        self.age = age

# Create instances
buddy = Dog("Buddy", 5)
miles = Dog("Miles", 3)

print(buddy.name)      # Buddy
print(miles.name)      # Miles
print(buddy.species)   # Canis familiaris
print(miles.species)   # Canis familiaris
```

### Class with Methods

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def bark(self):
        return f"{self.name} says Woof!"
    
    def get_info(self):
        return f"{self.name} is {self.age} years old"

buddy = Dog("Buddy", 5)
print(buddy.bark())      # Buddy says Woof!
print(buddy.get_info())  # Buddy is 5 years old
```

---

## 3. The `self` Keyword

### What is `self`?

**`self` refers to the current instance of the class.**

```python
class Counter:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1  # self refers to this specific instance
    
    def get_count(self):
        return self.count

# Create two separate counters
counter1 = Counter()
counter2 = Counter()

counter1.increment()
counter1.increment()
counter2.increment()

print(counter1.get_count())  # 2
print(counter2.get_count())  # 1
```

### Why `self` is Needed

```python
class Person:
    def __init__(self, name):
        # self.name refers to THIS instance's name attribute
        self.name = name
    
    def greet(self):
        # self.name accesses THIS instance's name
        print(f"Hello, I'm {self.name}")

alice = Person("Alice")
bob = Person("Bob")

alice.greet()  # Hello, I'm Alice
bob.greet()    # Hello, I'm Bob
```

**Behind the Scenes:**
```python
# When you call:
alice.greet()

# Python actually does:
Person.greet(alice)  # Passes alice as self!
```

### `self` is Convention

```python
# This works but don't do it!
class BadExample:
    def __init__(this, name):  # 'this' instead of 'self'
        this.name = name

# Always use 'self' - it's a strong Python convention
class GoodExample:
    def __init__(self, name):
        self.name = name
```

---

## 4. Constructors and Initialization

### `__init__` Constructor

```python
class User:
    def __init__(self, name, email):
        """Initialize a new user"""
        self.name = name
        self.email = email
        self.created_at = datetime.now()  # Automatic timestamp

user = User("Alice", "alice@example.com")
# __init__ is called automatically when creating instance
```

### Constructor with Default Values

```python
class User:
    def __init__(self, name, email, role="user", active=True):
        self.name = name
        self.email = email
        self.role = role
        self.active = active

# Different ways to create users
user1 = User("Alice", "alice@example.com")
user2 = User("Bob", "bob@example.com", role="admin")
user3 = User("Charlie", "charlie@example.com", active=False)
```

### Validation in Constructor

```python
class User:
    def __init__(self, name, age):
        if not name:
            raise ValueError("Name cannot be empty")
        if age < 0:
            raise ValueError("Age cannot be negative")
        
        self.name = name
        self.age = age

# Valid
user1 = User("Alice", 25)

# Invalid - raises ValueError
try:
    user2 = User("", 25)
except ValueError as e:
    print(e)  # Name cannot be empty
```

### `__new__` vs `__init__`

```python
class MyClass:
    def __new__(cls, *args, **kwargs):
        """Creates the instance (called first)"""
        print("__new__ called")
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, value):
        """Initializes the instance (called second)"""
        print("__init__ called")
        self.value = value

obj = MyClass(10)
# Output:
# __new__ called
# __init__ called
```

**When to use `__new__`:**
- Implementing singletons
- Subclassing immutable types (tuple, str)
- Metaclass programming

**Most of the time, just use `__init__`!**

---

## 5. Instance vs Class Variables

### Instance Variables

```python
class Dog:
    def __init__(self, name):
        self.name = name  # Instance variable

dog1 = Dog("Buddy")
dog2 = Dog("Max")

print(dog1.name)  # Buddy
print(dog2.name)  # Max

dog1.name = "Charlie"
print(dog1.name)  # Charlie
print(dog2.name)  # Max (unchanged)
```

### Class Variables

```python
class Dog:
    # Class variable (shared by ALL instances)
    species = "Canis familiaris"
    count = 0
    
    def __init__(self, name):
        self.name = name
        Dog.count += 1  # Access class variable via class name

dog1 = Dog("Buddy")
dog2 = Dog("Max")

print(Dog.count)        # 2
print(dog1.count)       # 2
print(dog2.count)       # 2

print(Dog.species)      # Canis familiaris
print(dog1.species)     # Canis familiaris
```

### Instance vs Class Variables Pitfall

```python
class Counter:
    count = 0  # Class variable
    
    def increment_wrong(self):
        self.count += 1  # Creates instance variable!
    
    def increment_correct(self):
        Counter.count += 1  # Modifies class variable

c1 = Counter()
c2 = Counter()

c1.increment_wrong()
print(Counter.count)  # 0 (class variable unchanged)
print(c1.count)       # 1 (new instance variable created)
print(c2.count)       # 0 (class variable)

c1.increment_correct()
c2.increment_correct()
print(Counter.count)  # 2 (class variable modified)
```

---

## 6. Methods

### Instance Methods

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
    
    def deposit(self, amount):
        """Instance method - operates on instance data"""
        if amount > 0:
            self.balance += amount
            return True
        return False
    
    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False
    
    def get_balance(self):
        return self.balance

account = BankAccount("Alice", 1000)
account.deposit(500)
account.withdraw(200)
print(account.get_balance())  # 1300
```

### Class Methods

```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_string(cls, date_string):
        """Alternative constructor"""
        year, month, day = map(int, date_string.split('-'))
        return cls(year, month, day)
    
    @classmethod
    def today(cls):
        """Factory method"""
        import datetime
        today = datetime.date.today()
        return cls(today.year, today.month, today.day)

# Regular constructor
date1 = Date(2024, 1, 15)

# Using class method
date2 = Date.from_string("2024-01-15")
date3 = Date.today()
```

### Static Methods

```python
class MathUtils:
    @staticmethod
    def add(a, b):
        """Doesn't need instance or class - just utility function"""
        return a + b
    
    @staticmethod
    def is_even(n):
        return n % 2 == 0

# Call without creating instance
print(MathUtils.add(5, 3))      # 8
print(MathUtils.is_even(10))    # True

# Can also call from instance (but not common)
utils = MathUtils()
print(utils.add(2, 3))          # 5
```

### When to Use Each?

| Method Type | Access to | Use When |
|-------------|-----------|----------|
| **Instance** | `self` (instance data) | Need to access/modify instance state |
| **Class** | `cls` (class data) | Factory methods, alternative constructors |
| **Static** | Neither | Utility functions, don't need instance/class |

---

## 7. OOP Principles

### 1. Encapsulation

**Hide internal details, expose only what's necessary**

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self._balance = balance  # "Private" by convention
    
    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
    
    def withdraw(self, amount):
        if 0 < amount <= self._balance:
            self._balance -= amount
    
    def get_balance(self):
        return self._balance

account = BankAccount("Alice", 1000)
# Good: Using methods
account.deposit(500)

# Bad: Direct access (not prevented, just discouraged)
account._balance += 1000  # Works but shouldn't do this
```

**Name Mangling (Strong Privacy):**

```python
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # Name mangled to _BankAccount__balance
    
    def get_balance(self):
        return self.__balance

account = BankAccount(1000)
print(account.get_balance())  # 1000
# print(account.__balance)    # AttributeError
print(account._BankAccount__balance)  # 1000 (can still access, but awkward)
```

### 2. Inheritance

**Create new classes based on existing ones**

```python
# Parent class
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass

# Child classes
class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

dog = Dog("Buddy")
cat = Cat("Whiskers")

print(dog.speak())  # Buddy says Woof!
print(cat.speak())  # Whiskers says Meow!
```

**Using `super()`:**

```python
class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
    
    def info(self):
        return f"{self.brand} {self.model}"

class Car(Vehicle):
    def __init__(self, brand, model, num_doors):
        super().__init__(brand, model)  # Call parent constructor
        self.num_doors = num_doors
    
    def info(self):
        parent_info = super().info()  # Call parent method
        return f"{parent_info} with {self.num_doors} doors"

car = Car("Toyota", "Camry", 4)
print(car.info())  # Toyota Camry with 4 doors
```

**Multiple Inheritance:**

```python
class Flyable:
    def fly(self):
        return "Flying!"

class Swimmable:
    def swim(self):
        return "Swimming!"

class Duck(Flyable, Swimmable):
    def quack(self):
        return "Quack!"

duck = Duck()
print(duck.fly())    # Flying!
print(duck.swim())   # Swimming!
print(duck.quack())  # Quack!
```

### 3. Polymorphism

**Different classes with same interface**

```python
class Shape:
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        import math
        return math.pi * self.radius ** 2

# Polymorphism in action
shapes = [
    Rectangle(5, 10),
    Circle(7),
    Rectangle(3, 4)
]

for shape in shapes:
    print(f"Area: {shape.area():.2f}")
```

### 4. Abstraction

**Hide complex implementation, show only essential features**

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount):
        """Must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def refund(self, transaction_id):
        pass

class StripeProcessor(PaymentProcessor):
    def process_payment(self, amount):
        return f"Processing ${amount} via Stripe"
    
    def refund(self, transaction_id):
        return f"Refunding transaction {transaction_id} via Stripe"

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount):
        return f"Processing ${amount} via PayPal"
    
    def refund(self, transaction_id):
        return f"Refunding transaction {transaction_id} via PayPal"

# Cannot instantiate abstract class
# processor = PaymentProcessor()  # TypeError

# Can instantiate concrete classes
stripe = StripeProcessor()
paypal = PayPalProcessor()

print(stripe.process_payment(100))
print(paypal.process_payment(50))
```

---

## 8. Magic Methods (Dunder Methods)

### `__str__` and `__repr__`

```python
class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year
    
    def __str__(self):
        """User-friendly string representation"""
        return f"'{self.title}' by {self.author}"
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"Book('{self.title}', '{self.author}', {self.year})"

book = Book("1984", "George Orwell", 1949)

print(str(book))   # '1984' by George Orwell
print(repr(book))  # Book('1984', 'George Orwell', 1949)
print(book)        # Uses __str__ if available
```

### Comparison Methods

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __eq__(self, other):
        """Equal to =="""
        return self.age == other.age
    
    def __lt__(self, other):
        """Less than <"""
        return self.age < other.age
    
    def __le__(self, other):
        """Less than or equal <="""
        return self.age <= other.age

alice = Person("Alice", 25)
bob = Person("Bob", 30)
charlie = Person("Charlie", 25)

print(alice == charlie)  # True
print(alice < bob)       # True
print(alice <= charlie)  # True

# Can now sort!
people = [bob, alice, charlie]
sorted_people = sorted(people)
for person in sorted_people:
    print(f"{person.name}: {person.age}")
```

### Container Methods

```python
class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def __len__(self):
        """len(cart)"""
        return len(self.items)
    
    def __getitem__(self, index):
        """cart[index]"""
        return self.items[index]
    
    def __setitem__(self, index, value):
        """cart[index] = value"""
        self.items[index] = value
    
    def __contains__(self, item):
        """item in cart"""
        return item in self.items
    
    def add(self, item):
        self.items.append(item)

cart = ShoppingCart()
cart.add("Apple")
cart.add("Banana")
cart.add("Orange")

print(len(cart))            # 3
print(cart[0])              # Apple
print("Apple" in cart)      # True

# Can iterate!
for item in cart:
    print(item)
```

### Callable Objects

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    
    def __call__(self, x):
        """Makes instance callable like a function"""
        return x * self.factor

times_2 = Multiplier(2)
times_3 = Multiplier(3)

print(times_2(5))  # 10
print(times_3(5))  # 15
```

---

## 9. Dataclasses

### Why Dataclasses?

**Without dataclass:**
```python
class Person:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email
    
    def __repr__(self):
        return f"Person(name={self.name}, age={self.age}, email={self.email})"
    
    def __eq__(self, other):
        return (self.name, self.age, self.email) == (other.name, other.age, other.email)
```

**With dataclass:**
```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    email: str

# Automatically gets __init__, __repr__, __eq__, and more!
person = Person("Alice", 25, "alice@example.com")
print(person)  # Person(name='Alice', age=25, email='alice@example.com')
```

### Dataclass Features

```python
from dataclasses import dataclass, field

@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0  # Default value
    tags: list = field(default_factory=list)  # Mutable default
    
    def total_value(self):
        return self.price * self.quantity

product = Product("Laptop", 999.99, 5)
print(product)
print(f"Total value: ${product.total_value()}")
```

### Frozen Dataclass (Immutable)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

point = Point(10, 20)
# point.x = 15  # FrozenInstanceError
```

---

## Exercises

### Level 1: Basics

1. **Simple Class**
   - Create a `Person` class with name and age
   - Add method to introduce themselves

2. **Bank Account**
   - Class with deposit, withdraw methods
   - Track balance

3. **Rectangle Class**
   - Store width and height
   - Methods for area and perimeter

### Level 2: Intermediate

4. **Student Class**
   - Store name and grades list
   - Methods: add_grade, get_average, get_letter_grade

5. **Library System**
   - Book class (title, author, ISBN)
   - Library class to manage books
   - Methods: add_book, find_book, remove_book

6. **Inheritance**
   - Vehicle parent class
   - Car and Motorcycle child classes
   - Override methods appropriately

### Level 3: Challenging

7. **Complete OOP System**
   - Implement a mini e-commerce system
   - Classes: Product, Customer, Order, ShoppingCart
   - Use all OOP principles

---

Continue to [Part-05-Collections-DataStructures](../Part-05-Collections-DataStructures/README.md)!
