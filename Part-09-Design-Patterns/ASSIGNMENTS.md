# Part 9: Design Patterns - Practice Problems

> Test Singleton, Factory, Observer, Strategy, and more

---

## Problem 1: Singleton Pattern

**Task**: Ensure one instance
```python
class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

db1 = Database()
db2 = Database()
assert db1 is db2  # Same instance
```

**Time**: 15 minutes

---

## Problem 2: Factory Pattern

**Task**: Create objects by type
```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof"

class Cat(Animal):
    def speak(self):
        return "Meow"

class AnimalFactory:
    @staticmethod
    def create(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()

animal = AnimalFactory.create("dog")
assert animal.speak() == "Woof"
```

**Time**: 20 minutes

---

## Problem 3: Observer Pattern

**Task**: Event notification
```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class Observer:
    def __init__(self, name):
        self.name = name
    
    def update(self, message):
        print(f"{self.name} received: {message}")

subject = Subject()
obs1 = Observer("A")
subject.attach(obs1)
subject.notify("Hello")
```

**Time**: 20 minutes

---

## Problem 4: Strategy Pattern

**Task**: Different algorithms
```python
class SortStrategy:
    def sort(self, data):
        pass

class BubbleSort(SortStrategy):
    def sort(self, data):
        # Implementation
        return sorted(data)

class QuickSort(SortStrategy):
    def sort(self, data):
        return sorted(data, reverse=False)

class Sorter:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def sort(self, data):
        return self.strategy.sort(data)

sorter = Sorter(BubbleSort())
assert sorter.sort([3,1,2]) == [1,2,3]
```

**Time**: 25 minutes

---

## Problem 5: Decorator Pattern

**Task**: Add behavior dynamically
```python
class Coffee:
    def cost(self):
        return 5

class MilkDecorator:
    def __init__(self, coffee):
        self._coffee = coffee
    
    def cost(self):
        return self._coffee.cost() + 2

coffee = Coffee()
milk_coffee = MilkDecorator(coffee)
assert milk_coffee.cost() == 7
```

**Time**: 20 minutes

---

## Problem 6: Builder Pattern

**Task**: Step-by-step construction
```python
class Pizza:
    def __init__(self):
        self.size = None
        self.toppings = []

class PizzaBuilder:
    def __init__(self):
        self.pizza = Pizza()
    
    def set_size(self, size):
        self.pizza.size = size
        return self
    
    def add_topping(self, topping):
        self.pizza.toppings.append(topping)
        return self
    
    def build(self):
        return self.pizza

pizza = PizzaBuilder().set_size("large").add_topping("cheese").build()
```

**Time**: 20 minutes

---

## Problem 7: Adapter Pattern

**Task**: Make incompatible interfaces work
```python
class OldPrinter:
    def print_old(self, text):
        return f"OLD: {text}"

class NewPrinter:
    def print(self, text):
        pass

class PrinterAdapter(NewPrinter):
    def __init__(self, old_printer):
        self.old_printer = old_printer
    
    def print(self, text):
        return self.old_printer.print_old(text)

old = OldPrinter()
adapter = PrinterAdapter(old)
print(adapter.print("Hello"))
```

**Time**: 20 minutes

---

## Problem 8: Command Pattern

**Task**: Encapsulate actions
```python
class Command:
    def execute(self):
        pass

class LightOnCommand(Command):
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        self.light.turn_on()

class Light:
    def turn_on(self):
        print("Light on")

light = Light()
command = LightOnCommand(light)
command.execute()
```

**Time**: 20 minutes

---

## Problem 9: Template Method

**Task**: Define algorithm skeleton
```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    def process(self):
        self.read_data()
        self.process_data()
        self.save_data()
    
    @abstractmethod
    def read_data(self):
        pass
    
    @abstractmethod
    def process_data(self):
        pass
    
    def save_data(self):
        print("Saving")

class CSVProcessor(DataProcessor):
    def read_data(self):
        print("Reading CSV")
    
    def process_data(self):
        print("Processing CSV")
```

**Time**: 25 minutes

---

## Problem 10: Facade Pattern

**Task**: Simplified interface
```python
class SubsystemA:
    def operation_a(self):
        return "A"

class SubsystemB:
    def operation_b(self):
        return "B"

class Facade:
    def __init__(self):
        self.subsystem_a = SubsystemA()
        self.subsystem_b = SubsystemB()
    
    def simple_operation(self):
        return self.subsystem_a.operation_a() + self.subsystem_b.operation_b()

facade = Facade()
assert facade.simple_operation() == "AB"
```

**Time**: 15 minutes

---

## Summary Check

**7+ solved** → Design patterns understood  
**4-6 solved** → Review pattern purposes  
**< 4 solved** → Study patterns with examples
