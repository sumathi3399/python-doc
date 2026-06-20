# Part 9: Design Patterns in Python

> Learn proven solutions to common programming problems using Pythonic design patterns.

## 📚 Table of Contents

1. [Introduction to Design Patterns](#1-introduction-to-design-patterns)
2. [Creational Patterns](#2-creational-patterns)
3. [Structural Patterns](#3-structural-patterns)
4. [Behavioral Patterns](#4-behavioral-patterns)
5. [Pythonic Alternatives](#5-pythonic-alternatives)
6. [Exercises](#exercises)

---

## 1. Introduction to Design Patterns

### What are Design Patterns?

**Design patterns** are reusable solutions to commonly occurring problems in software design. They represent best practices evolved over time.

### Why Learn Design Patterns?

- **Communication**: Common vocabulary with other developers
- **Proven Solutions**: Battle-tested approaches
- **Best Practices**: Learn from experienced developers
- **Code Quality**: More maintainable and flexible code

### Pattern Categories

1. **Creational**: Object creation mechanisms
2. **Structural**: Object composition
3. **Behavioral**: Communication between objects

---

## 2. Creational Patterns

### Singleton Pattern

**Purpose**: Ensure class has only one instance

```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Usage
db1 = Singleton()
db2 = Singleton()
print(db1 is db2)  # True - same instance
```

**With Decorator:**
```python
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    def __init__(self):
        print("Database initialized")

db1 = Database()  # Database initialized
db2 = Database()  # (reuses same instance)
```

**Real-World Example:**
```python
class ConfigurationManager:
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set(self, key, value):
        self._config[key] = value
    
    def get(self, key):
        return self._config.get(key)

# Global configuration access
config = ConfigurationManager()
config.set("db_host", "localhost")

# Elsewhere in code
config2 = ConfigurationManager()
print(config2.get("db_host"))  # localhost
```

### Factory Pattern

**Purpose**: Create objects without specifying exact class

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")

# Usage
animal = AnimalFactory.create_animal("dog")
print(animal.speak())  # Woof!
```

**Real-World Example - Document Creator:**
```python
class Document(ABC):
    @abstractmethod
    def render(self):
        pass

class PDFDocument(Document):
    def render(self):
        return "Rendering PDF..."

class WordDocument(Document):
    def render(self):
        return "Rendering Word document..."

class DocumentFactory:
    @staticmethod
    def create(file_extension):
        if file_extension == ".pdf":
            return PDFDocument()
        elif file_extension in [".doc", ".docx"]:
            return WordDocument()
        else:
            raise ValueError(f"Unsupported format: {file_extension}")

doc = DocumentFactory.create(".pdf")
print(doc.render())
```

### Builder Pattern

**Purpose**: Construct complex objects step by step

```python
class Pizza:
    def __init__(self):
        self.size = None
        self.cheese = False
        self.pepperoni = False
        self.mushrooms = False
    
    def __str__(self):
        toppings = []
        if self.cheese: toppings.append("cheese")
        if self.pepperoni: toppings.append("pepperoni")
        if self.mushrooms: toppings.append("mushrooms")
        return f"{self.size} pizza with {', '.join(toppings)}"

class PizzaBuilder:
    def __init__(self):
        self.pizza = Pizza()
    
    def set_size(self, size):
        self.pizza.size = size
        return self  # Return self for chaining
    
    def add_cheese(self):
        self.pizza.cheese = True
        return self
    
    def add_pepperoni(self):
        self.pizza.pepperoni = True
        return self
    
    def add_mushrooms(self):
        self.pizza.mushrooms = True
        return self
    
    def build(self):
        return self.pizza

# Usage with method chaining
pizza = (PizzaBuilder()
         .set_size("large")
         .add_cheese()
         .add_pepperoni()
         .build())

print(pizza)  # large pizza with cheese, pepperoni
```

**Real-World Example - Query Builder:**
```python
class Query:
    def __init__(self):
        self.table = None
        self.conditions = []
        self.fields = []
        self.limit_value = None
    
    def to_sql(self):
        fields_str = ", ".join(self.fields) or "*"
        sql = f"SELECT {fields_str} FROM {self.table}"
        if self.conditions:
            sql += " WHERE " + " AND ".join(self.conditions)
        if self.limit_value:
            sql += f" LIMIT {self.limit_value}"
        return sql

class QueryBuilder:
    def __init__(self):
        self.query = Query()
    
    def select(self, *fields):
        self.query.fields = fields
        return self
    
    def from_table(self, table):
        self.query.table = table
        return self
    
    def where(self, condition):
        self.query.conditions.append(condition)
        return self
    
    def limit(self, limit):
        self.query.limit_value = limit
        return self
    
    def build(self):
        return self.query.to_sql()

# Usage
sql = (QueryBuilder()
       .select("name", "email")
       .from_table("users")
       .where("age > 18")
       .where("active = true")
       .limit(10)
       .build())

print(sql)
# SELECT name, email FROM users WHERE age > 18 AND active = true LIMIT 10
```

### Prototype Pattern

**Purpose**: Clone existing objects

```python
import copy

class Prototype:
    def clone(self):
        return copy.deepcopy(self)

class Car(Prototype):
    def __init__(self, model, color, features):
        self.model = model
        self.color = color
        self.features = features

# Create base car
base_car = Car("Model S", "Blue", ["Autopilot", "Sunroof"])

# Clone and modify
car2 = base_car.clone()
car2.color = "Red"

print(f"Car 1: {base_car.color}")  # Blue
print(f"Car 2: {car2.color}")       # Red
```

---

## 3. Structural Patterns

### Adapter Pattern

**Purpose**: Make incompatible interfaces compatible

```python
# Old interface
class OldPrinter:
    def print_text(self, text):
        return f"[OLD] {text}"

# New interface expected
class ModernPrinter:
    def print(self, document):
        return f"[MODERN] {document}"

# Adapter
class PrinterAdapter:
    def __init__(self, old_printer):
        self.old_printer = old_printer
    
    def print(self, document):
        # Adapt old interface to new
        return self.old_printer.print_text(document)

# Usage
old = OldPrinter()
adapter = PrinterAdapter(old)
print(adapter.print("Hello"))  # [OLD] Hello
```

**Real-World Example - API Adapter:**
```python
class OldAPIClient:
    def fetch_user_data(self, user_id):
        return {"id": user_id, "full_name": "John Doe"}

class NewAPIClient:
    def get_user(self, user_id):
        # Expected format different
        return {"user_id": user_id, "name": "Jane Doe"}

class APIAdapter:
    def __init__(self, old_client):
        self.old_client = old_client
    
    def get_user(self, user_id):
        old_data = self.old_client.fetch_user_data(user_id)
        # Transform to new format
        return {
            "user_id": old_data["id"],
            "name": old_data["full_name"]
        }

# Works with new interface
adapter = APIAdapter(OldAPIClient())
user = adapter.get_user(123)
```

### Decorator Pattern (Not the same as Python decorators!)

**Purpose**: Add behavior dynamically

```python
class Coffee:
    def cost(self):
        return 5

class MilkDecorator:
    def __init__(self, coffee):
        self._coffee = coffee
    
    def cost(self):
        return self._coffee.cost() + 1

class SugarDecorator:
    def __init__(self, coffee):
        self._coffee = coffee
    
    def cost(self):
        return self._coffee.cost() + 0.5

# Usage - wrap with decorators
coffee = Coffee()
print(coffee.cost())  # 5

coffee_with_milk = MilkDecorator(coffee)
print(coffee_with_milk.cost())  # 6

coffee_with_milk_and_sugar = SugarDecorator(coffee_with_milk)
print(coffee_with_milk_and_sugar.cost())  # 6.5
```

### Facade Pattern

**Purpose**: Provide simplified interface to complex system

```python
# Complex subsystems
class CPU:
    def freeze(self): print("CPU frozen")
    def jump(self, addr): print(f"Jump to {addr}")
    def execute(self): print("Executing")

class Memory:
    def load(self, addr, data): print(f"Load {data} at {addr}")

class HardDrive:
    def read(self, sector, size): return f"Data from sector {sector}"

# Facade - simple interface
class ComputerFacade:
    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hd = HardDrive()
    
    def start(self):
        """Simple start method hides complexity"""
        self.cpu.freeze()
        data = self.hd.read(0, 1024)
        self.memory.load(0, data)
        self.cpu.jump(0)
        self.cpu.execute()

# Usage - simple!
computer = ComputerFacade()
computer.start()
```

### Proxy Pattern

**Purpose**: Control access to object

```python
class RealDatabase:
    def query(self, sql):
        print(f"Executing: {sql}")
        return "Result"

class DatabaseProxy:
    def __init__(self):
        self._db = None
        self._cache = {}
    
    def query(self, sql):
        # Lazy initialization
        if self._db is None:
            print("Initializing database...")
            self._db = RealDatabase()
        
        # Caching
        if sql in self._cache:
            print("Returning cached result")
            return self._cache[sql]
        
        result = self._db.query(sql)
        self._cache[sql] = result
        return result

# Usage
db = DatabaseProxy()
db.query("SELECT * FROM users")  # Initializing + Executing
db.query("SELECT * FROM users")  # Returning cached result
```

---

## 4. Behavioral Patterns

### Strategy Pattern

**Purpose**: Select algorithm at runtime

```python
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid ${amount} with credit card"

class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid ${amount} with PayPal"

class CryptoPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid ${amount} with cryptocurrency"

class ShoppingCart:
    def __init__(self):
        self.payment_strategy = None
    
    def set_payment_strategy(self, strategy):
        self.payment_strategy = strategy
    
    def checkout(self, amount):
        if not self.payment_strategy:
            raise ValueError("No payment method selected")
        return self.payment_strategy.pay(amount)

# Usage
cart = ShoppingCart()
cart.set_payment_strategy(CreditCardPayment())
print(cart.checkout(100))  # Paid $100 with credit card

cart.set_payment_strategy(PayPalPayment())
print(cart.checkout(50))   # Paid $50 with PayPal
```

### Observer Pattern

**Purpose**: Notify multiple objects about events

```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class Observer:
    def __init__(self, name):
        self.name = name
    
    def update(self, message):
        print(f"{self.name} received: {message}")

# Usage
subject = Subject()

obs1 = Observer("Observer 1")
obs2 = Observer("Observer 2")

subject.attach(obs1)
subject.attach(obs2)

subject.notify("Hello observers!")
# Observer 1 received: Hello observers!
# Observer 2 received: Hello observers!
```

**Real-World Example - Stock Price Monitor:**
```python
class StockExchange:
    def __init__(self):
        self._observers = {}
    
    def subscribe(self, stock, observer):
        if stock not in self._observers:
            self._observers[stock] = []
        self._observers[stock].append(observer)
    
    def update_price(self, stock, price):
        if stock in self._observers:
            for observer in self._observers[stock]:
                observer.price_changed(stock, price)

class Investor:
    def __init__(self, name):
        self.name = name
    
    def price_changed(self, stock, price):
        print(f"{self.name} notified: {stock} is now ${price}")

# Usage
exchange = StockExchange()

investor1 = Investor("Alice")
investor2 = Investor("Bob")

exchange.subscribe("AAPL", investor1)
exchange.subscribe("AAPL", investor2)

exchange.update_price("AAPL", 150.50)
# Alice notified: AAPL is now $150.5
# Bob notified: AAPL is now $150.5
```

### Command Pattern

**Purpose**: Encapsulate requests as objects

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class Light:
    def on(self):
        print("Light is ON")
    
    def off(self):
        print("Light is OFF")

class LightOnCommand(Command):
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        self.light.on()
    
    def undo(self):
        self.light.off()

class LightOffCommand(Command):
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        self.light.off()
    
    def undo(self):
        self.light.on()

class RemoteControl:
    def __init__(self):
        self.history = []
    
    def execute(self, command):
        command.execute()
        self.history.append(command)
    
    def undo(self):
        if self.history:
            command = self.history.pop()
            command.undo()

# Usage
light = Light()
remote = RemoteControl()

remote.execute(LightOnCommand(light))   # Light is ON
remote.execute(LightOffCommand(light))  # Light is OFF
remote.undo()                           # Light is ON (undo last)
```

### Iterator Pattern

**Purpose**: Access elements sequentially

```python
class BookCollection:
    def __init__(self):
        self.books = []
    
    def add_book(self, book):
        self.books.append(book)
    
    def __iter__(self):
        return iter(self.books)

# Usage
collection = BookCollection()
collection.add_book("1984")
collection.add_book("Brave New World")

for book in collection:
    print(book)
```

**Custom Iterator:**
```python
class RangeIterator:
    def __init__(self, start, end):
        self.current = start
        self.end = end
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        current = self.current
        self.current += 1
        return current

# Usage
for i in RangeIterator(0, 5):
    print(i)  # 0, 1, 2, 3, 4
```

---

## 5. Pythonic Alternatives

### When NOT to Use Patterns

Python has built-in features that replace some patterns:

**Instead of Singleton:**
```python
# Just use a module!
# config.py
settings = {
    "db_host": "localhost",
    "db_port": 5432
}

# Import anywhere - same object
from config import settings
```

**Instead of Factory:**
```python
# Use dict mapping
creators = {
    "dog": lambda: Dog(),
    "cat": lambda: Cat()
}

animal = creators["dog"]()
```

**Instead of Iterator:**
```python
# Use generator
def range_generator(start, end):
    while start < end:
        yield start
        start += 1

for i in range_generator(0, 5):
    print(i)
```

**Instead of Strategy:**
```python
# Use first-class functions
def credit_card_payment(amount):
    return f"Paid ${amount} with credit card"

def paypal_payment(amount):
    return f"Paid ${amount} with PayPal"

# Select at runtime
payment_method = credit_card_payment
print(payment_method(100))
```

---

## Exercises

### Level 1: Basic

1. **Singleton**
   - Implement singleton pattern
   - Test with multiple instances

2. **Simple Factory**
   - Create factory for shapes
   - Circle, Square, Triangle

3. **Observer**
   - Newsletter subscription system
   - Notify subscribers

### Level 2: Intermediate

4. **Builder**
   - HTTP request builder
   - Method chaining

5. **Strategy**
   - Sorting strategies
   - Different algorithms

6. **Adapter**
   - Adapt old API to new interface

### Level 3: Challenging

7. **Complete System**
   - Use 3+ patterns together
   - E-commerce checkout system

8. **Command with Undo**
   - Text editor commands
   - Full undo/redo

9. **Observer + Strategy**
   - Stock trading system
   - Different trading strategies

---

## Key Takeaways

✅ **Creational**:
- Singleton: One instance
- Factory: Create without specifying class
- Builder: Construct step by step
- Prototype: Clone objects

✅ **Structural**:
- Adapter: Make interfaces compatible
- Decorator: Add behavior
- Facade: Simplify complex system
- Proxy: Control access

✅ **Behavioral**:
- Strategy: Select algorithm
- Observer: Event notification
- Command: Encapsulate requests
- Iterator: Sequential access

✅ **Pythonic**:
- Use built-in features when possible
- Modules for singletons
- Functions for strategies
- Generators for iterators

---

Continue to [Part-10-Concurrency-Parallelism](../Part-10-Concurrency-Parallelism/README.md)!
