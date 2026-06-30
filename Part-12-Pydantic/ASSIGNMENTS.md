# Part 12: Pydantic - Practice Problems

> Test Pydantic models, validation, serialization

---

## Problem 1: Basic Model

**Task**: Create user model
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

user = User(name="Alice", age=25, email="alice@example.com")
assert user.name == "Alice"
```

**Time**: 10 minutes

---

## Problem 2: Field Validation

**Task**: Email and age constraints
```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: EmailStr

# This should raise ValidationError
try:
    user = User(name="Bob", age=200, email="invalid")
except Exception as e:
    print("Validation failed")
```

**Time**: 15 minutes

---

## Problem 3: Optional Fields

**Task**: Optional and default values
```python
from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    stock: int = 0

p = Product(name="Widget", price=9.99)
assert p.stock == 0
```

**Time**: 10 minutes

---

## Problem 4: Nested Models

**Task**: Address in user
```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    zipcode: str

class User(BaseModel):
    name: str
    address: Address

user = User(
    name="Alice",
    address={"street": "123 Main", "city": "NYC", "zipcode": "10001"}
)
```

**Time**: 15 minutes

---

## Problem 5: Field Validator

**Task**: Custom validation
```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

user = User(name="Alice", password="secure123")
```

**Time**: 20 minutes

---

## Problem 6: Model Validator

**Task**: Cross-field validation
```python
from pydantic import BaseModel, model_validator

class User(BaseModel):
    password: str
    confirm_password: str
    
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
```

**Time**: 20 minutes

---

## Problem 7: Model Serialization

**Task**: Convert to dict and JSON
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

user = User(name="Alice", age=25)
data = user.model_dump()  # to dict
json_str = user.model_dump_json()  # to JSON string
```

**Time**: 10 minutes

---

## Problem 8: Parsing from Dict

**Task**: Load from data
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

data = {"name": "Alice", "age": 25}
user = User.model_validate(data)
assert user.name == "Alice"
```

**Time**: 10 minutes

---

## Problem 9: Config Settings

**Task**: From environment variables
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
print(settings.app_name)
```

**Time**: 15 minutes

---

## Problem 10: Exclude Fields in Serialization

**Task**: Hide sensitive data
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    email: str
    password: str = Field(exclude=True)

user = User(name="Alice", email="a@example.com", password="secret")
data = user.model_dump()
assert 'password' not in data
```

**Time**: 15 minutes

---

## Summary Check

**8+ solved** → Pydantic mastered  
**5-7 solved** → Practice validators  
**< 5 solved** → Review model basics
