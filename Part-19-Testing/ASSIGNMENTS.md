# Part 19: Testing - Practice Problems

> Test unit tests, integration tests, mocking

---

## Problem 1: Basic Unit Test

**Task**: Test a function
```python
import pytest

def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
```

**Time**: 5 minutes

---

## Problem 2: Parametrized Test

**Task**: Test multiple inputs
```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

**Time**: 10 minutes

---

## Problem 3: Test with Fixture

**Task**: Setup test data
```python
import pytest

@pytest.fixture
def sample_user():
    return {"name": "Alice", "age": 25}

def test_user_name(sample_user):
    assert sample_user["name"] == "Alice"
```

**Time**: 10 minutes

---

## Problem 4: Mock External Call

**Task**: Mock HTTP request
```python
from unittest.mock import Mock, patch

def fetch_data(url):
    import requests
    return requests.get(url).json()

def test_fetch_data():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"data": "test"}
        result = fetch_data("http://test.com")
        assert result == {"data": "test"}
```

**Time**: 20 minutes

---

## Problem 5: FastAPI TestClient

**Task**: Test API endpoint
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello"}

def test_read_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}
```

**Time**: 15 minutes

---

## Problem 6: Database Test with Fixture

**Task**: Test with test DB
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_user(db_session):
    user = User(name="Alice")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

**Time**: 20 minutes

---

## Problem 7: Test Exception Raised

**Task**: Verify error is raised
```python
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

**Time**: 10 minutes

---

## Problem 8: Test Coverage

**Task**: Run with coverage
```bash
# Install pytest-cov
pip install pytest-cov

# Run tests with coverage
pytest --cov=myapp --cov-report=html

# View coverage in htmlcov/index.html
```

**Time**: 10 minutes

---

## Problem 9: Integration Test

**Task**: Test multiple components
```python
def test_create_and_retrieve_user(client, db_session):
    # Create user via API
    response = client.post("/users/", json={"name": "Alice"})
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Retrieve user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"
```

**Time**: 20 minutes

---

## Problem 10: Async Test

**Task**: Test async function
```python
import pytest
import asyncio

async def async_add(a, b):
    await asyncio.sleep(0.1)
    return a + b

@pytest.mark.asyncio
async def test_async_add():
    result = await async_add(2, 3)
    assert result == 5
```

**Time**: 15 minutes

---

## Summary Check

**8+ solved** → Testing mastered  
**5-7 solved** → Practice mocking  
**< 5 solved** → Review pytest basics
