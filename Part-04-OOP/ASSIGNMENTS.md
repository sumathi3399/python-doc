# Part 4: Object-Oriented Programming - Assignments

## Assignment Guidelines

- **Estimated time:** 12-16 hours total
- **Prerequisites:** Parts 1-3 complete
- **Submission:** Python package or modules with demo script and sample output
- **Rules:** Demonstrate OOP principles; use dataclasses where appropriate

---

## Assignment 1: Public Library Management System

### Scenario

Design a complete library system using OOP. The system manages books, members, loans, and fines — modeling real-world entities as classes with proper relationships.

### Requirements

**Classes to implement:**

1. **`Book`**
   - Attributes: ISBN, title, author, genre, copies_total, copies_available
   - Methods: `is_available()`, `__str__`, `__repr__`
   - Magic: `__eq__` by ISBN, `__hash__` for set usage

2. **`Member`** (base class)
   - Attributes: member_id, name, email, join_date, borrowed_books (list)
   - Methods: `borrow(book)`, `return_book(book)`, `get_borrowed_count()`
   - `__str__` for display

3. **`PremiumMember(Member)`** — inheritance
   - Extended loan period (14 vs 7 days)
   - Override `borrow()` to allow up to 5 books (base: 3)
   - Additional method: `reserve_book(book)` — queue when unavailable

4. **`StudentMember(Member)`**
   - Discount on fines (50%)
   - Override fine calculation method

5. **`Loan`**
   - Attributes: book, member, loan_date, due_date, returned_date (optional)
   - Methods: `is_overdue()`, `calculate_fine(rate_per_day)`, `mark_returned()`
   - Use `@property` for `days_overdue`

6. **`Library`** — composition (not inheritance)
   - Holds collections of books and members
   - Methods: `add_book`, `register_member`, `search_by_title`, `search_by_author`, `checkout`, `checkin`, `get_overdue_loans`
   - Use `__len__` for total books, `__contains__` for ISBN lookup

7. **`Catalog`** — class with class variables
   - `total_books_registered` — class variable incremented on each `Book` creation
   - `@classmethod` `get_statistics()` — returns registry stats
   - `@staticmethod` `validate_isbn(isbn)` — format check

8. **`BookNotAvailableError`** — custom exception class (inherit `Exception`)

**Dataclass:**
- `BookSummary` frozen dataclass: title, author, available_copies — for read-only API responses

### Technical Specifications

- Classes and objects, `self`, constructors (`__init__`)
- Instance vs class variables
- Instance methods, `@classmethod`, `@staticmethod`
- Inheritance and method overriding
- Encapsulation: use `_protected` convention for internal state
- Polymorphism: `checkout(member: Member)` works for any member type
- Magic methods: `__str__`, `__repr__`, `__eq__`, `__len__`, `__contains__`, `@property`
- Dataclasses (`@dataclass`, `frozen=True`)
- Composition: Library has Books and Members

### Acceptance Criteria

- [ ] Full workflow: register member → add books → borrow → return → calculate fine
- [ ] Premium and Student members behave differently on borrow limits/fines
- [ ] `BookNotAvailableError` raised when checking out unavailable book
- [ ] Search returns correct results (case-insensitive title search)
- [ ] `Catalog.get_statistics()` reflects book count
- [ ] `BookSummary` is immutable (frozen)
- [ ] Demo script exercises all classes with printed output

### Bonus Challenges

- Abstract base class `Media` with `Book` and `DVD` subclasses (use `abc.ABC`)
- `__iter__` on Library to iterate available books
- Context manager on `Loan`: `with loan.track():` auto-returns on exit

### Hints

- `due_date = loan_date + timedelta(days=period)` — `from datetime import datetime, timedelta`
- Override `borrow` with `super().borrow(book)` for shared logic
- `__eq__` and `__hash__` must be consistent if using books in sets

---

## Assignment 2: E-Commerce Domain Model

### Scenario

Build the domain layer (no database, no API) for an online store. Focus on OOP design: Product hierarchy, shopping cart, orders, and payment processing.

### Requirements

**Product hierarchy (inheritance + ABC):**

```python
# Product (ABC) → PhysicalProduct, DigitalProduct, SubscriptionProduct
```

- `Product`: name, sku, price, `calculate_price()` abstract
- `PhysicalProduct`: weight, shipping_cost added to price
- `DigitalProduct`: file_size_mb, license_type; no shipping
- `SubscriptionProduct`: billing_cycle (monthly/yearly); `calculate_price()` applies discount for yearly

**`ShoppingCart`:**
- Add/remove/update quantity
- `__getitem__`, `__iter__` for iteration
- `total`, `item_count` as properties
- Apply `Discount` objects (strategy-like: percentage vs fixed)

**`Order`:**
- Composed of cart snapshot (list of line items)
- Status workflow: pending → paid → shipped → delivered (validate transitions)
- `__str__` produces order summary

**`Customer`:**
- Regular vs `VIPCustomer` (10% automatic discount on `calculate_total`)

**Magic methods showcase:**
- `Product.__lt__` for price comparison sorting
- `Cart.__add__` to merge two carts
- `LineItem.__mul__` for quantity scaling

**`Inventory`:**
- Class-level `_registry` dict of all products by SKU
- `@classmethod register_product(cls, product)`
- Prevent duplicate SKU registration

### Technical Specifications

- All four OOP pillars: encapsulation, inheritance, polymorphism, abstraction
- Abstract base class with `@abstractmethod`
- Properties for computed values
- Rich magic method usage (6+ dunder methods)
- Dataclass for `Address` and `LineItem`

### Acceptance Criteria

- [ ] Three product types price differently via polymorphic `calculate_price()`
- [ ] Cart correctly computes totals with multiple discounts
- [ ] Order status cannot skip invalid transitions (raise error or return False)
- [ ] VIP discount applies automatically
- [ ] Products sortable by price using `<`
- [ ] Inventory registry prevents duplicate SKUs
- [ ] 20+ unit-test-style assertions in demo block (or separate test file)

### Bonus Challenges

- `OrderBuilder` (builder pattern preview): fluent API `OrderBuilder().add_item(...).with_address(...).build()`
- `Money` value object with `__add__` and `__radd__` preventing float precision issues (store cents as int)
- Serialization: `to_dict()` / `from_dict()` on Order

### Hints

- Line item: `dataclass` with product, quantity, unit_price snapshot
- Status transitions: dict mapping `valid_next = {"pending": ["paid", "cancelled"], ...}`
- ABC: `from abc import ABC, abstractmethod`

---

## Assignment 3: Employee Management & Payroll Engine

### Scenario

Model a company's org structure and payroll system. Combines inheritance, composition, and operator overloading in one cohesive system.

### Requirements

1. **`Employee` hierarchy:** `SalariedEmployee`, `HourlyEmployee`, `Contractor` — each implements `calculate_pay(period)` differently

2. **`Department`:** contains employees; methods `add_employee`, `remove_employee`, `total_payroll`, `highest_paid`

3. **`Company`:** contains departments; `company_wide_payroll()`, `find_employee_by_id(id)` searching all departments

4. **`PaySlip`:** dataclass generated per employee per period with deductions

5. **Operator overloading:**
   - `Employee.__eq__` by employee_id
   - `PaySlip.__lt__` by net_pay for sorting
   - `Department.__iadd__(employee)` for `dept += emp`

6. **`@property` examples:**
   - `Employee.full_name` from first + last
   - `Employee.is_active` based on termination_date

7. **`__repr__` vs `__str__`:** developer-friendly repr, user-friendly str throughout

### Technical Specifications

- Complete OOP feature set from Part 4
- Composition over inheritance where appropriate (Company has Departments)
- Inheritance for employee pay types
- Dataclasses for PaySlip and simple value objects

### Acceptance Criteria

- [ ] Payroll calculations correct for all 3 employee types
- [ ] Company finds employee across departments
- [ ] `+=` adds employee to department
- [ ] Properties compute derived values correctly
- [ ] Meaningful `__repr__` on all core classes

### Bonus Challenges

- `Employee.__format__` for custom pay display: `f"{emp:pay}"`
- Observer-style: `Department.notify_payroll_complete()` calling callbacks (preview Part 9)
- Export org chart as indented string using recursion

### Hints

- Hourly: `hours * rate`; Salaried: `annual / 12`; Contractor: `project_fee`
- `find_employee`: nested loop over departments and employees
- Use `dataclasses.field(default_factory=list)` for mutable defaults
