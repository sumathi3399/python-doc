# Part 12: Pydantic

> Master Pydantic for data validation, serialization, and settings management in Python.

## 📚 Table of Contents

1. [Pydantic Basics](#1-pydantic-basics)
2. [Validation](#2-validation)
3. [Serialization](#3-serialization)
4. [Parsing](#4-parsing)
5. [Advanced Features](#5-advanced-features)
6. [Pydantic v2](#6-pydantic-v2)
7. [Exercises](#exercises)

---

## 1. Pydantic Basics

### Why Pydantic Exists

**Problem: Unreliable Data**
```python
# Without Pydantic - No validation
def create_user(data: dict):
    user = {
        "name": data["name"],  # What if it's not a string?
        "age": data["age"],     # What if it's negative?
        "email": data["email"]  # What if it's invalid?
    }
    return user

# Runtime errors are common
create_user({"name": 123, "age": -5, "email": "not-an-email"})
```

**Solution: Pydantic**
```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    name: str
    age: int = Field(gt=0, le=120)
    email: EmailStr

# Automatic validation
user = User(name="Alice", age=30, email="alice@example.com")  # ✅ Valid
user = User(name=123, age=-5, email="bad-email")  # ❌ ValidationError
```

**Key Benefits:**
- **Runtime validation**: Catch errors before they cause problems
- **Type hints**: Clear data structures
- **Serialization**: Easy conversion to/from JSON
- **IDE support**: Autocomplete and type checking
- **Performance**: Written in Rust (v2), extremely fast

### BaseModel Fundamentals

```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    # Required fields
    username: str
    email: str
    
    # Optional field
    age: Optional[int] = None
    
    # Field with default value
    is_active: bool = True
    
    # Field with default factory
    tags: list[str] = []

# Creating instances
user1 = User(username="alice", email="alice@example.com")
print(user1)
# username='alice' email='alice@example.com' age=None is_active=True tags=[]

user2 = User(
    username="bob",
    email="bob@example.com",
    age=30,
    tags=["developer", "python"]
)

# Accessing fields
print(user2.username)  # bob
print(user2.age)       # 30

# Validation happens automatically
try:
    User(username=123, email="invalid")  # ❌ ValidationError
except Exception as e:
    print(e)
```

### Field Types

```python
from pydantic import BaseModel, HttpUrl, EmailStr, UUID4, constr, conint
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Set, Tuple
from uuid import UUID

class CompleteExample(BaseModel):
    # Basic types
    name: str
    age: int
    height: float
    is_active: bool
    
    # Date and time
    created_at: datetime
    birth_date: date
    
    # Collections
    tags: List[str]
    scores: Dict[str, int]
    unique_ids: Set[int]
    coordinates: Tuple[float, float]
    
    # Special types
    email: EmailStr
    website: HttpUrl
    user_id: UUID4
    price: Decimal
    
    # Constrained types
    username: constr(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    rating: conint(ge=1, le=5)

# Example usage
data = {
    "name": "Alice",
    "age": 30,
    "height": 5.6,
    "is_active": True,
    "created_at": "2024-01-01T10:00:00",
    "birth_date": "1994-01-01",
    "tags": ["python", "developer"],
    "scores": {"math": 95, "science": 88},
    "unique_ids": {1, 2, 3},
    "coordinates": (40.7128, -74.0060),
    "email": "alice@example.com",
    "website": "https://example.com",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "price": "99.99",
    "username": "alice_123",
    "rating": 5
}

example = CompleteExample(**data)
print(example.created_at)  # datetime object
print(example.price)       # Decimal('99.99')
```

### Field() for Advanced Configuration

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(
        ...,  # Required (same as no default)
        description="Product name",
        min_length=1,
        max_length=100
    )
    
    price: float = Field(
        gt=0,  # Greater than 0
        le=1000000,  # Less than or equal to 1 million
        description="Product price in USD"
    )
    
    quantity: int = Field(
        default=0,
        ge=0,  # Greater than or equal to 0
        description="Available quantity"
    )
    
    sku: str = Field(
        pattern=r'^[A-Z]{3}-\d{4}$',
        examples=["ABC-1234"]
    )
    
    # Computed field with alias
    discount_price: float = Field(
        alias="discountPrice",
        description="Price after discount"
    )

# Usage
product = Product(
    name="Laptop",
    price=999.99,
    sku="LAP-1234",
    discountPrice=899.99
)

print(product.name)           # Laptop
print(product.discount_price) # 899.99
```

---

## 2. Validation

### Automatic Validation

```python
from pydantic import BaseModel, ValidationError
from typing import List

class User(BaseModel):
    name: str
    age: int
    email: str
    hobbies: List[str]

# ✅ Valid data
user = User(
    name="Alice",
    age=30,
    email="alice@example.com",
    hobbies=["reading", "coding"]
)

# ❌ Type coercion
user2 = User(
    name="Bob",
    age="25",  # String -> int (coerced)
    email="bob@example.com",
    hobbies=["gaming"]
)
print(user2.age)  # 25 (int)

# ❌ Validation errors
try:
    User(
        name=123,  # Not a string
        age="not-a-number",  # Can't convert to int
        email="alice@example.com",
        hobbies="not-a-list"  # Not a list
    )
except ValidationError as e:
    print(e)
    """
    3 validation errors for User
    name
      Input should be a valid string
    age
      Input should be a valid integer
    hobbies
      Input should be a valid list
    """
```

### Custom Validators

```python
from pydantic import BaseModel, field_validator, ValidationError

class User(BaseModel):
    username: str
    email: str
    age: int
    
    @field_validator('username')
    @classmethod
    def username_must_be_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('username must be alphanumeric')
        return v
    
    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('invalid email format')
        return v.lower()  # Normalize to lowercase
    
    @field_validator('age')
    @classmethod
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('age must be positive')
        if v > 150:
            raise ValueError('age seems unrealistic')
        return v

# Usage
user = User(username="alice123", email="ALICE@EXAMPLE.COM", age=30)
print(user.email)  # alice@example.com (normalized)

try:
    User(username="alice@123", email="alice@example.com", age=30)
except ValidationError as e:
    print(e)  # username must be alphanumeric
```

### Field Validators

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    name: str
    price: float
    discount_percent: float
    
    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('price must be positive')
        return v
    
    @field_validator('discount_percent')
    @classmethod
    def discount_must_be_valid(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('discount must be between 0 and 100')
        return v

# Multiple fields validation
class Rectangle(BaseModel):
    width: float
    height: float
    
    @field_validator('width', 'height')
    @classmethod
    def dimensions_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('dimensions must be positive')
        return v

# Transform data
class User(BaseModel):
    name: str
    email: str
    
    @field_validator('name')
    @classmethod
    def capitalize_name(cls, v):
        return v.title()
    
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v):
        return v.lower().strip()

user = User(name="alice smith", email="  ALICE@EXAMPLE.COM  ")
print(user.name)   # Alice Smith
print(user.email)  # alice@example.com
```

### Model Validators

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str
    
    @model_validator(mode='after')
    def check_dates(self):
        if self.start_date > self.end_date:
            raise ValueError('start_date must be before end_date')
        return self

# Usage
date_range = DateRange(start_date="2024-01-01", end_date="2024-12-31")  # ✅

try:
    DateRange(start_date="2024-12-31", end_date="2024-01-01")  # ❌
except ValidationError as e:
    print(e)

# Cross-field validation
class PasswordReset(BaseModel):
    password: str
    confirm_password: str
    
    @model_validator(mode='after')
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('passwords do not match')
        return self

# Business logic validation
class Order(BaseModel):
    total_amount: float
    discount: float
    final_amount: float
    
    @model_validator(mode='after')
    def verify_calculation(self):
        expected = self.total_amount - self.discount
        if abs(self.final_amount - expected) > 0.01:
            raise ValueError('final_amount calculation is incorrect')
        return self
```

### Validator Order

```python
from pydantic import BaseModel, field_validator, model_validator

class User(BaseModel):
    username: str
    email: str
    age: int
    
    # 1. Field validators run first (in order of fields)
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        print(f"1. Validating username: {v}")
        return v.lower()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        print(f"2. Validating email: {v}")
        return v.lower()
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        print(f"3. Validating age: {v}")
        if v < 0:
            raise ValueError('age must be positive')
        return v
    
    # 2. Model validators run after all field validators
    @model_validator(mode='after')
    def validate_model(self):
        print(f"4. Model validation: {self.username}, {self.email}, {self.age}")
        return self

user = User(username="ALICE", email="ALICE@EXAMPLE.COM", age=30)
# Output:
# 1. Validating username: ALICE
# 2. Validating email: ALICE@EXAMPLE.COM
# 3. Validating age: 30
# 4. Model validation: alice, alice@example.com, 30
```

---

## 3. Serialization

### model_dump() - to dict

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str
    age: int
    email: str
    address: Address
    tags: List[str]

user = User(
    name="Alice",
    age=30,
    email="alice@example.com",
    address=Address(street="123 Main St", city="NYC", country="USA"),
    tags=["developer", "python"]
)

# Basic dump
data = user.model_dump()
print(data)
# {
#     'name': 'Alice',
#     'age': 30,
#     'email': 'alice@example.com',
#     'address': {'street': '123 Main St', 'city': 'NYC', 'country': 'USA'},
#     'tags': ['developer', 'python']
# }

# Exclude fields
data = user.model_dump(exclude={'email'})
print(data)  # email not included

# Include only specific fields
data = user.model_dump(include={'name', 'age'})
print(data)  # Only name and age

# Exclude nested fields
data = user.model_dump(exclude={'address': {'street'}})
print(data)  # address without street

# Exclude unset fields
class OptionalUser(BaseModel):
    name: str
    age: int
    bio: str = None

user2 = OptionalUser(name="Bob", age=25)
print(user2.model_dump())  # includes bio: None
print(user2.model_dump(exclude_unset=True))  # excludes bio

# Exclude defaults
print(user2.model_dump(exclude_defaults=True))

# Exclude None values
print(user2.model_dump(exclude_none=True))
```

### model_dump_json() - to JSON

```python
from pydantic import BaseModel
from datetime import datetime

class Event(BaseModel):
    name: str
    timestamp: datetime
    attendees: List[str]

event = Event(
    name="Python Meetup",
    timestamp=datetime(2024, 1, 15, 18, 0),
    attendees=["Alice", "Bob", "Charlie"]
)

# Dump to JSON string
json_str = event.model_dump_json()
print(json_str)
# '{"name":"Python Meetup","timestamp":"2024-01-15T18:00:00","attendees":["Alice","Bob","Charlie"]}'

# Pretty print
json_str = event.model_dump_json(indent=2)
print(json_str)
# {
#   "name": "Python Meetup",
#   "timestamp": "2024-01-15T18:00:00",
#   "attendees": ["Alice", "Bob", "Charlie"]
# }

# Exclude fields
json_str = event.model_dump_json(exclude={'attendees'})

# Save to file
with open('event.json', 'w') as f:
    f.write(event.model_dump_json(indent=2))
```

### Custom Serializers

```python
from pydantic import BaseModel, field_serializer
from datetime import datetime

class User(BaseModel):
    name: str
    email: str
    created_at: datetime
    balance: float
    
    @field_serializer('email')
    def serialize_email(self, value):
        # Mask email for privacy
        username, domain = value.split('@')
        masked = username[0] + '*' * (len(username) - 2) + username[-1]
        return f"{masked}@{domain}"
    
    @field_serializer('created_at')
    def serialize_datetime(self, value):
        return value.strftime('%Y-%m-%d')
    
    @field_serializer('balance')
    def serialize_balance(self, value):
        return f"${value:.2f}"

user = User(
    name="Alice",
    email="alice@example.com",
    created_at=datetime(2024, 1, 15),
    balance=1234.5
)

print(user.model_dump())
# {
#     'name': 'Alice',
#     'email': 'a***e@example.com',
#     'created_at': '2024-01-15',
#     'balance': '$1234.50'
# }

# Custom serializer for specific mode
class Product(BaseModel):
    name: str
    price: float
    internal_cost: float
    
    @field_serializer('internal_cost')
    def serialize_cost(self, value, _info):
        # Only include in 'python' mode, not 'json'
        if _info.mode == 'json':
            return None
        return value
```

---

## 4. Parsing

### model_validate() - from dict

```python
from pydantic import BaseModel, ValidationError
from typing import List

class User(BaseModel):
    name: str
    age: int
    tags: List[str]

# From dict
data = {
    "name": "Alice",
    "age": 30,
    "tags": ["python", "developer"]
}

user = User.model_validate(data)
print(user)
# name='Alice' age=30 tags=['python', 'developer']

# Type coercion
data = {
    "name": "Bob",
    "age": "25",  # String -> int
    "tags": "single-tag"  # Not a list, but single value
}

try:
    user = User.model_validate(data)
except ValidationError as e:
    print(e)

# Strict mode - no coercion
try:
    user = User.model_validate(data, strict=True)
except ValidationError as e:
    print("Strict mode failed:", e)
```

### model_validate_json() - from JSON

```python
from pydantic import BaseModel, ValidationError
import json

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

# From JSON string
json_str = '{"name": "Laptop", "price": 999.99, "in_stock": true}'
product = Product.model_validate_json(json_str)
print(product)
# name='Laptop' price=999.99 in_stock=True

# From JSON file
with open('product.json', 'w') as f:
    f.write(json_str)

with open('product.json', 'r') as f:
    product = Product.model_validate_json(f.read())

# Invalid JSON
try:
    Product.model_validate_json('{"name": "Laptop", "price": "not-a-number"}')
except ValidationError as e:
    print(e)
```

### Parsing Errors

```python
from pydantic import BaseModel, ValidationError, Field
from typing import List

class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    age: int = Field(ge=0, le=150)
    tags: List[str]

# Multiple validation errors
try:
    User(
        username="ab",  # Too short
        email="not-an-email",  # Invalid
        age=200,  # Too high
        tags="not-a-list"  # Wrong type
    )
except ValidationError as e:
    print(e)
    """
    4 validation errors for User
    username
      String should have at least 3 characters
    email
      value is not a valid email address
    age
      Input should be less than or equal to 150
    tags
      Input should be a valid list
    """
    
    # Error details
    for error in e.errors():
        print(f"Field: {error['loc']}")
        print(f"Message: {error['msg']}")
        print(f"Type: {error['type']}")
        print()

# Programmatic error handling
def safe_parse_user(data: dict):
    try:
        return User.model_validate(data), None
    except ValidationError as e:
        errors = {}
        for error in e.errors():
            field = error['loc'][0]
            errors[field] = error['msg']
        return None, errors

user, errors = safe_parse_user({
    "username": "ab",
    "email": "alice@example.com",
    "age": 30,
    "tags": ["python"]
})

if errors:
    print("Validation failed:", errors)
    # {'username': 'String should have at least 3 characters'}
```

---

## 5. Advanced Features

### Nested Models

```python
from pydantic import BaseModel
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: Optional[str] = None

class Company(BaseModel):
    name: str
    address: Address

class User(BaseModel):
    name: str
    email: str
    home_address: Address
    work_address: Optional[Address] = None
    companies: List[Company] = []

# Create nested structure
user = User(
    name="Alice",
    email="alice@example.com",
    home_address=Address(
        street="123 Main St",
        city="NYC",
        country="USA",
        zip_code="10001"
    ),
    work_address=Address(
        street="456 Office Blvd",
        city="NYC",
        country="USA"
    ),
    companies=[
        Company(
            name="Tech Corp",
            address=Address(street="789 Tech Ave", city="SF", country="USA")
        )
    ]
)

# Access nested fields
print(user.home_address.city)  # NYC
print(user.companies[0].name)  # Tech Corp

# Nested validation
data = {
    "name": "Bob",
    "email": "bob@example.com",
    "home_address": {
        "street": "123 Main St",
        "city": "NYC",
        "country": "USA"
    }
}

user = User.model_validate(data)
```

### Generic Models

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    data: T
    message: str
    success: bool

class User(BaseModel):
    name: str
    email: str

class Product(BaseModel):
    name: str
    price: float

# Use with different types
user_response = Response[User](
    data=User(name="Alice", email="alice@example.com"),
    message="User fetched successfully",
    success=True
)

product_response = Response[Product](
    data=Product(name="Laptop", price=999.99),
    message="Product fetched successfully",
    success=True
)

# List response
class ListResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int

users_response = ListResponse[User](
    data=[
        User(name="Alice", email="alice@example.com"),
        User(name="Bob", email="bob@example.com")
    ],
    total=2,
    page=1
)

print(users_response.model_dump())
```

### Computed Fields

```python
from pydantic import BaseModel, computed_field

class User(BaseModel):
    first_name: str
    last_name: str
    birth_year: int
    
    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @computed_field
    @property
    def age(self) -> int:
        from datetime import datetime
        return datetime.now().year - self.birth_year

user = User(first_name="Alice", last_name="Smith", birth_year=1990)

print(user.full_name)  # Alice Smith
print(user.age)        # 34 (in 2024)

# Computed fields are included in serialization
data = user.model_dump()
print(data)
# {
#     'first_name': 'Alice',
#     'last_name': 'Smith',
#     'birth_year': 1990,
#     'full_name': 'Alice Smith',
#     'age': 34
# }

# Another example
class Rectangle(BaseModel):
    width: float
    height: float
    
    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @computed_field
    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

rect = Rectangle(width=10, height=5)
print(rect.area)       # 50.0
print(rect.perimeter)  # 30.0
```

### Model Configuration

```python
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    model_config = ConfigDict(
        # Validation
        validate_assignment=True,  # Validate on attribute assignment
        validate_default=True,      # Validate default values
        
        # Serialization
        str_strip_whitespace=True,  # Strip whitespace from strings
        str_to_lower=False,         # Don't lowercase strings
        
        # Extra fields
        extra='forbid',  # Options: 'allow', 'ignore', 'forbid'
        
        # JSON schema
        json_schema_extra={
            "examples": [
                {
                    "name": "Alice",
                    "email": "alice@example.com"
                }
            ]
        },
        
        # Aliases
        populate_by_name=True,  # Allow using field name or alias
        
        # Performance
        use_enum_values=True,  # Use enum values instead of enum objects
    )
    
    name: str
    email: str

# validate_assignment example
user = User(name="Alice", email="alice@example.com")
user.name = "Bob"  # Validated
try:
    user.name = 123  # ValidationError
except Exception as e:
    print(e)

# extra='forbid' example
try:
    User(name="Alice", email="alice@example.com", age=30)  # Extra field
except Exception as e:
    print("Extra field not allowed")

# Aliases
class Product(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name: str
    price: float = Field(alias='productPrice')

# Can use either name
p1 = Product(name="Laptop", price=999.99)
p2 = Product(name="Laptop", productPrice=999.99)
```

### Field Constraints

```python
from pydantic import BaseModel, Field
from typing import List

class Product(BaseModel):
    # String constraints
    name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r'^[a-zA-Z0-9\s]+$'
    )
    
    # Numeric constraints
    price: float = Field(
        gt=0,        # Greater than
        le=1000000   # Less than or equal
    )
    
    quantity: int = Field(
        ge=0,        # Greater than or equal
        lt=10000     # Less than
    )
    
    discount: float = Field(
        ge=0,
        le=100,
        description="Discount percentage"
    )
    
    # Collection constraints
    tags: List[str] = Field(
        min_length=1,
        max_length=10
    )
    
    # Multiple of constraint
    pack_size: int = Field(multiple_of=6)

# Usage
product = Product(
    name="Laptop Pro",
    price=999.99,
    quantity=50,
    discount=15.5,
    tags=["electronics", "computer"],
    pack_size=12
)

# Validation errors
try:
    Product(
        name="",  # Too short
        price=0,  # Must be > 0
        quantity=-1,  # Must be >= 0
        discount=150,  # Must be <= 100
        tags=[],  # Must have at least 1 item
        pack_size=7  # Must be multiple of 6
    )
except Exception as e:
    print(e)
```

---

## 6. Pydantic v2

### Performance Improvements

```python
"""
Pydantic v2 is 5-50x faster than v1!

Why?
- Core validation written in Rust
- Optimized type checking
- Better memory usage
- Lazy validation when possible
"""

from pydantic import BaseModel
import time

class User(BaseModel):
    name: str
    email: str
    age: int

# Benchmark
data = {"name": "Alice", "email": "alice@example.com", "age": 30}

start = time.time()
for _ in range(100000):
    user = User.model_validate(data)
elapsed = time.time() - start

print(f"Created 100k instances in {elapsed:.2f}s")
# v1: ~2-3 seconds
# v2: ~0.1-0.3 seconds
```

### Core Changes

```python
from pydantic import BaseModel, Field, field_validator

# ❌ Pydantic v1 (deprecated)
"""
class OldUser(BaseModel):
    name: str
    
    class Config:
        validate_assignment = True
    
    @validator('name')
    def name_valid(cls, v):
        return v.title()
    
    def dict(self):
        return ...
    
    def json(self):
        return ...
"""

# ✅ Pydantic v2 (current)
class NewUser(BaseModel):
    name: str
    
    model_config = {
        'validate_assignment': True
    }
    
    @field_validator('name')
    @classmethod
    def name_valid(cls, v):
        return v.title()
    
    def model_dump(self):  # Replaces dict()
        return super().model_dump()
    
    def model_dump_json(self):  # Replaces json()
        return super().model_dump_json()

# Key changes:
# 1. Config -> model_config
# 2. @validator -> @field_validator
# 3. .dict() -> .model_dump()
# 4. .json() -> .model_dump_json()
# 5. .parse_obj() -> .model_validate()
# 6. .parse_raw() -> .model_validate_json()
```

### Migration from v1

```python
"""
Migration Guide: v1 -> v2

1. Update imports
"""
# Old
from pydantic import validator

# New
from pydantic import field_validator, model_validator

"""
2. Update Config
"""
# Old
class User(BaseModel):
    class Config:
        validate_assignment = True

# New
from pydantic import ConfigDict

class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

"""
3. Update validators
"""
# Old
@validator('name')
def validate_name(cls, v):
    return v

# New
@field_validator('name')
@classmethod
def validate_name(cls, v):
    return v

"""
4. Update root validators
"""
# Old
@root_validator
def validate_model(cls, values):
    return values

# New
@model_validator(mode='after')
def validate_model(self):
    return self

"""
5. Update serialization
"""
# Old
user.dict()
user.json()
User.parse_obj(data)
User.parse_raw(json_str)

# New
user.model_dump()
user.model_dump_json()
User.model_validate(data)
User.model_validate_json(json_str)

"""
6. Update field configuration
"""
# Old
name: str = Field(..., regex=r'^[a-z]+$')

# New
name: str = Field(..., pattern=r'^[a-z]+$')

# Run migration tool
# pip install pydantic-v1-migration
# pydantic-v1-migration path/to/code
```

---

## Exercises

### Exercise 1: User Management System
Create a complete user management system with validation.

**Requirements:**
- User model with email, password, age validation
- Address model (nested)
- Custom validator for strong passwords
- Serialize users excluding sensitive data

```python
# Your solution here
from pydantic import BaseModel, EmailStr, Field, field_validator

class Address(BaseModel):
    # Implement this
    pass

class User(BaseModel):
    # Implement this
    pass
```

### Exercise 2: API Request/Response Models
Build Pydantic models for a REST API.

**Requirements:**
- Product model with constraints
- CreateProductRequest model
- ProductResponse model with computed fields
- ListResponse generic model

```python
# Your solution here
from pydantic import BaseModel
from typing import List, Generic, TypeVar

# Implement models
```

### Exercise 3: Configuration Management
Create a configuration system using Pydantic.

**Requirements:**
- DatabaseConfig with connection settings
- APIConfig with rate limits
- AppConfig combining all configs
- Load from environment variables
- Validation for all settings

```python
# Your solution here
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseSettings):
    # Implement this
    pass
```

### Exercise 4: Data Validation Pipeline
Build a data validation and transformation pipeline.

**Requirements:**
- Accept CSV data
- Validate each row using Pydantic
- Transform data (normalize, clean)
- Report validation errors
- Export cleaned data

```python
# Your solution here
import csv
from pydantic import BaseModel, ValidationError

def validate_csv(file_path):
    # Implement this
    pass
```

---

## Summary

### Key Concepts

1. **Pydantic Basics**
   - BaseModel for data classes
   - Automatic type validation
   - Field types and constraints

2. **Validation**
   - Field validators
   - Model validators
   - Custom validation logic
   - Error handling

3. **Serialization & Parsing**
   - model_dump() / model_dump_json()
   - model_validate() / model_validate_json()
   - Custom serializers
   - Exclude/include fields

4. **Advanced Features**
   - Nested models
   - Generic models
   - Computed fields
   - Model configuration

5. **Pydantic v2**
   - 5-50x faster
   - Rust core
   - Updated API
   - Migration path

### Best Practices

✅ **DO:**
- Use Pydantic for all data validation
- Define clear field constraints
- Use type hints properly
- Handle ValidationError explicitly
- Leverage computed fields
- Use model_config for behavior

❌ **DON'T:**
- Skip validation
- Use dict over model_dump()
- Ignore validation errors
- Over-complicate validators
- Forget to update to v2

### Next Steps

Now that you understand Pydantic, you're ready to:
- Build APIs with **FastAPI** (Part 13)
- Integrate with **SQLAlchemy** for database models (Part 14)
- Create production-grade applications (Part 16)

---

**Continue to [Part 13: FastAPI](../Part-13-FastAPI/README.md)** →
