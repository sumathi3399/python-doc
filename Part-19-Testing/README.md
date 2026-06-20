# Part 19: Testing FastAPI Microservices

> Build confidence in your code with comprehensive testing strategies from unit tests to end-to-end scenarios.

## 📚 Table of Contents

1. [Testing Pyramid](#1-testing-pyramid)
2. [Unit Testing](#2-unit-testing)
3. [Integration Testing](#3-integration-testing)
4. [API Testing](#4-api-testing)
5. [Database Testing](#5-database-testing)
6. [Mocking & Fixtures](#6-mocking--fixtures)
7. [Test Coverage](#7-test-coverage)
8. [End-to-End Testing](#8-end-to-end-testing)
9. [Performance Testing](#9-performance-testing)
10. [Exercises](#exercises)

---

## 1. Testing Pyramid

### Test Types

```
        /\
       /E2E\          Few, slow, expensive
      /------\
     /Integration\    Moderate number
    /-----------\
   /   Unit Tests  \  Many, fast, cheap
  /-----------------\
```

### Testing Strategy

| Type | Purpose | Speed | Count | Cost |
|------|---------|-------|-------|------|
| **Unit** | Test individual functions | Fast | Many (70%) | Low |
| **Integration** | Test component interaction | Medium | Some (20%) | Medium |
| **E2E** | Test full user workflows | Slow | Few (10%) | High |

---

## 2. Unit Testing

### Basic pytest Setup

```python
# tests/test_services.py
import pytest
from app.services import user_service
from app.models import User

def test_calculate_age():
    """Test age calculation"""
    from datetime import date
    
    birth_date = date(1990, 1, 1)
    age = user_service.calculate_age(birth_date)
    
    assert age >= 33  # Will be 33+ depending on current year

def test_validate_email():
    """Test email validation"""
    assert user_service.validate_email("test@example.com") == True
    assert user_service.validate_email("invalid-email") == False
    assert user_service.validate_email("") == False

def test_format_user_name():
    """Test name formatting"""
    assert user_service.format_name("john doe") == "John Doe"
    assert user_service.format_name("JANE SMITH") == "Jane Smith"
    assert user_service.format_name("") == ""
```

### Testing with Pydantic Models

```python
# tests/test_schemas.py
import pytest
from pydantic import ValidationError
from app.schemas import UserCreate, OrderCreate

def test_user_create_valid():
    """Test valid user creation"""
    user = UserCreate(
        email="test@example.com",
        name="Test User",
        age=25
    )
    
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.age == 25

def test_user_create_invalid_email():
    """Test invalid email"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="invalid-email",
            name="Test User",
            age=25
        )
    
    errors = exc_info.value.errors()
    assert any(error["type"] == "value_error.email" for error in errors)

def test_user_create_negative_age():
    """Test negative age"""
    with pytest.raises(ValidationError):
        UserCreate(
            email="test@example.com",
            name="Test User",
            age=-5
        )

@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("invalid", False),
    ("", False),
    ("test@", False),
])
def test_email_validation_parametrized(email, expected):
    """Test email validation with multiple inputs"""
    try:
        user = UserCreate(email=email, name="Test", age=25)
        assert expected == True
    except ValidationError:
        assert expected == False
```

### Testing Business Logic

```python
# tests/test_order_service.py
from app.services.order_service import OrderService
from app.models import Order, OrderItem

class TestOrderService:
    def test_calculate_order_total(self):
        """Test order total calculation"""
        service = OrderService()
        
        items = [
            OrderItem(product_id=1, quantity=2, price=10.00),
            OrderItem(product_id=2, quantity=1, price=15.00),
        ]
        
        total = service.calculate_total(items)
        assert total == 35.00
    
    def test_calculate_order_total_with_discount(self):
        """Test order total with discount"""
        service = OrderService()
        
        items = [
            OrderItem(product_id=1, quantity=2, price=10.00),
        ]
        
        total = service.calculate_total(items, discount_percent=10)
        assert total == 18.00  # 20 - 10% = 18
    
    def test_validate_order_items_empty(self):
        """Test validation with empty items"""
        service = OrderService()
        
        with pytest.raises(ValueError, match="Order must have at least one item"):
            service.validate_order([])
    
    def test_validate_order_items_invalid_quantity(self):
        """Test validation with invalid quantity"""
        service = OrderService()
        
        items = [OrderItem(product_id=1, quantity=0, price=10.00)]
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            service.validate_order(items)
```

---

## 3. Integration Testing

### Testing with TestClient

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API"}

def test_create_user():
    """Test user creation"""
    response = client.post(
        "/users",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "age": 25
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_create_user_duplicate_email():
    """Test duplicate email error"""
    user_data = {
        "email": "duplicate@example.com",
        "name": "Test User",
        "age": 25
    }
    
    # First creation
    response1 = client.post("/users", json=user_data)
    assert response1.status_code == 201
    
    # Second creation (duplicate)
    response2 = client.post("/users", json=user_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]

def test_get_user():
    """Test getting user"""
    # Create user first
    create_response = client.post(
        "/users",
        json={"email": "get@example.com", "name": "Get User", "age": 30}
    )
    user_id = create_response.json()["id"]
    
    # Get user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

def test_get_user_not_found():
    """Test getting non-existent user"""
    response = client.get("/users/99999")
    assert response.status_code == 404
```

### Testing with Authentication

```python
# tests/test_auth.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Get authentication token"""
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_protected_endpoint_without_auth():
    """Test accessing protected endpoint without auth"""
    response = client.get("/users/me")
    assert response.status_code == 401

def test_protected_endpoint_with_auth(auth_headers):
    """Test accessing protected endpoint with auth"""
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert "email" in response.json()

def test_invalid_token():
    """Test with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401
```

---

## 4. API Testing

### Async Testing

```python
# tests/test_async_endpoints.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_async_create_user():
    """Test async user creation"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/users",
            json={"email": "async@example.com", "name": "Async User", "age": 25}
        )
    
    assert response.status_code == 201
    assert response.json()["email"] == "async@example.com"

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test handling concurrent requests"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create multiple users concurrently
        tasks = [
            ac.post("/users", json={"email": f"user{i}@example.com", "name": f"User {i}", "age": 25})
            for i in range(10)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.status_code == 201 for r in responses)
        
        # All should have unique IDs
        ids = [r.json()["id"] for r in responses]
        assert len(ids) == len(set(ids))
```

### Testing Error Handling

```python
def test_validation_error():
    """Test validation error response"""
    response = client.post(
        "/users",
        json={"email": "invalid", "name": "", "age": -5}
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    
    # Check specific validation errors
    assert any(e["loc"] == ["body", "email"] for e in errors)
    assert any(e["loc"] == ["body", "name"] for e in errors)
    assert any(e["loc"] == ["body", "age"] for e in errors)

def test_server_error_handling():
    """Test internal server error handling"""
    # Simulate error condition
    with patch("app.services.user_service.create_user", side_effect=Exception("Database error")):
        response = client.post(
            "/users",
            json={"email": "test@example.com", "name": "Test", "age": 25}
        )
        
        assert response.status_code == 500
        assert "error" in response.json()
```

---

## 5. Database Testing

### Test Database Setup

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

# Test database URL
TEST_DATABASE_URL = "postgresql://test:test@localhost:5432/test_db"

@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test"""
    # Create engine
    engine = create_engine(TEST_DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()
```

### Testing Database Operations

```python
# tests/test_database.py
def test_create_user_in_db(test_db):
    """Test creating user in database"""
    from app.models import User
    
    user = User(
        email="db@example.com",
        name="DB User",
        age=25
    )
    
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    assert user.id is not None
    assert user.email == "db@example.com"

def test_query_user(test_db):
    """Test querying user"""
    from app.models import User
    
    # Create user
    user = User(email="query@example.com", name="Query User", age=25)
    test_db.add(user)
    test_db.commit()
    
    # Query user
    queried_user = test_db.query(User).filter(User.email == "query@example.com").first()
    
    assert queried_user is not None
    assert queried_user.email == "query@example.com"

def test_update_user(test_db):
    """Test updating user"""
    from app.models import User
    
    # Create user
    user = User(email="update@example.com", name="Old Name", age=25)
    test_db.add(user)
    test_db.commit()
    
    # Update user
    user.name = "New Name"
    test_db.commit()
    
    # Verify update
    updated_user = test_db.query(User).filter(User.id == user.id).first()
    assert updated_user.name == "New Name"

def test_delete_user(test_db):
    """Test deleting user"""
    from app.models import User
    
    # Create user
    user = User(email="delete@example.com", name="Delete User", age=25)
    test_db.add(user)
    test_db.commit()
    user_id = user.id
    
    # Delete user
    test_db.delete(user)
    test_db.commit()
    
    # Verify deletion
    deleted_user = test_db.query(User).filter(User.id == user_id).first()
    assert deleted_user is None
```

---

## 6. Mocking & Fixtures

### pytest Fixtures

```python
# tests/conftest.py
import pytest
from datetime import datetime

@pytest.fixture
def sample_user():
    """Sample user data"""
    return {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "age": 25,
        "created_at": datetime.utcnow()
    }

@pytest.fixture
def sample_users():
    """Multiple sample users"""
    return [
        {"id": 1, "email": "user1@example.com", "name": "User 1", "age": 25},
        {"id": 2, "email": "user2@example.com", "name": "User 2", "age": 30},
        {"id": 3, "email": "user3@example.com", "name": "User 3", "age": 35},
    ]

@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email service"""
    emails_sent = []
    
    async def mock_send_email(to: str, subject: str, body: str):
        emails_sent.append({"to": to, "subject": subject, "body": body})
    
    monkeypatch.setattr("app.services.email_service.send_email", mock_send_email)
    
    return emails_sent
```

### Mocking External Services

```python
# tests/test_external_services.py
from unittest.mock import patch, Mock
import pytest

@pytest.mark.asyncio
async def test_fetch_user_from_external_api():
    """Test fetching user from external API"""
    mock_response = Mock()
    mock_response.json.return_value = {"id": 1, "name": "External User"}
    mock_response.status_code = 200
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        from app.services import external_service
        user = await external_service.fetch_user(1)
        
        assert user["id"] == 1
        assert user["name"] == "External User"

@pytest.mark.asyncio
async def test_external_api_timeout():
    """Test handling external API timeout"""
    with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Timeout")):
        from app.services import external_service
        
        with pytest.raises(httpx.TimeoutException):
            await external_service.fetch_user(1)

@pytest.mark.asyncio
async def test_payment_service_mock(mock_payment_service):
    """Test with mocked payment service"""
    from app.services import order_service
    
    order_id = await order_service.create_order({
        "user_id": 1,
        "amount": 100.00
    })
    
    # Verify payment was called
    assert len(mock_payment_service.calls) == 1
    assert mock_payment_service.calls[0]["amount"] == 100.00
```

### Mocking Database

```python
@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = {
        "id": 1,
        "email": "test@example.com"
    }
    return db

def test_get_user_with_mock_db(mock_db):
    """Test getting user with mocked database"""
    from app.services import user_service
    
    user = user_service.get_user(mock_db, user_id=1)
    
    assert user["id"] == 1
    assert user["email"] == "test@example.com"
    
    # Verify database was called correctly
    mock_db.query.assert_called_once()
```

---

## 7. Test Coverage

### Running Coverage

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=app tests/

# Generate HTML report
pytest --cov=app --cov-report=html tests/

# Coverage with branch analysis
pytest --cov=app --cov-branch tests/

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80 tests/
```

### Coverage Configuration

```ini
# setup.cfg or .coveragerc
[coverage:run]
source = app
omit = 
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False

[coverage:html]
directory = htmlcov
```

### Testing Critical Paths

```python
# tests/test_critical_paths.py
def test_user_registration_flow(client):
    """Test complete user registration"""
    # 1. Register user
    response = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "secure123", "name": "New User"}
    )
    assert response.status_code == 201
    
    # 2. Verify email sent
    # (would check mock email service)
    
    # 3. Login
    login_response = client.post(
        "/auth/login",
        json={"email": "new@example.com", "password": "secure123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 4. Access protected resource
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client.get("/users/me", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "new@example.com"

def test_order_creation_flow(client, auth_headers):
    """Test complete order creation flow"""
    # 1. Create order
    order_response = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1}
            ]
        },
        headers=auth_headers
    )
    assert order_response.status_code == 201
    order_id = order_response.json()["order_id"]
    
    # 2. Verify order status
    status_response = client.get(f"/orders/{order_id}", headers=auth_headers)
    assert status_response.json()["status"] == "pending"
    
    # 3. Process payment
    payment_response = client.post(
        f"/orders/{order_id}/payment",
        json={"payment_method": "credit_card"},
        headers=auth_headers
    )
    assert payment_response.status_code == 200
    
    # 4. Verify order completed
    final_status = client.get(f"/orders/{order_id}", headers=auth_headers)
    assert final_status.json()["status"] == "completed"
```

---

## 8. End-to-End Testing

### E2E Test Setup

```python
# tests/test_e2e.py
import pytest
from httpx import AsyncClient
import asyncio

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_user_journey():
    """Test complete user journey from registration to purchase"""
    
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Register
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "e2e@example.com",
                "password": "password123",
                "name": "E2E User"
            }
        )
        assert register_response.status_code == 201
        
        # 2. Login
        login_response = await client.post(
            "/auth/login",
            json={"email": "e2e@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Browse products
        products_response = await client.get("/products")
        products = products_response.json()
        assert len(products) > 0
        
        # 4. Add to cart
        cart_response = await client.post(
            "/cart/items",
            json={"product_id": products[0]["id"], "quantity": 2},
            headers=headers
        )
        assert cart_response.status_code == 200
        
        # 5. Create order
        order_response = await client.post(
            "/orders",
            headers=headers
        )
        order_id = order_response.json()["order_id"]
        
        # 6. Process payment
        payment_response = await client.post(
            f"/orders/{order_id}/payment",
            json={"payment_method": "credit_card", "card_number": "4111111111111111"},
            headers=headers
        )
        assert payment_response.status_code == 200
        
        # 7. Verify order status
        order_status = await client.get(f"/orders/{order_id}", headers=headers)
        assert order_status.json()["status"] == "completed"
```

---

## 9. Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tasks"""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_products(self):
        """Get products (most common)"""
        self.client.get("/products")
    
    @task(2)
    def get_user_profile(self):
        """Get user profile"""
        self.client.get("/users/me", headers=self.headers)
    
    @task(1)
    def create_order(self):
        """Create order (less common)"""
        self.client.post(
            "/orders",
            json={"items": [{"product_id": 1, "quantity": 1}]},
            headers=self.headers
        )

# Run: locust -f locustfile.py --host=http://localhost:8000
```

### Benchmarking

```python
# tests/test_performance.py
import time
import pytest

def test_endpoint_response_time(client):
    """Test endpoint responds within acceptable time"""
    iterations = 100
    total_time = 0
    
    for _ in range(iterations):
        start = time.time()
        response = client.get("/products")
        total_time += time.time() - start
        
        assert response.status_code == 200
    
    average_time = total_time / iterations
    assert average_time < 0.1  # Should respond in < 100ms

@pytest.mark.asyncio
async def test_concurrent_requests_performance():
    """Test handling concurrent requests"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        start = time.time()
        
        # 100 concurrent requests
        tasks = [client.get("/products") for _ in range(100)]
        responses = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        
        assert all(r.status_code == 200 for r in responses)
        assert elapsed < 5  # Should handle 100 requests in < 5s
```

---

## Exercises

### Level 1: Basic

1. **Unit Tests**
   - Test utility functions
   - Test Pydantic models
   - Test business logic

2. **API Tests**
   - Test CRUD endpoints
   - Test validation errors
   - Test authentication

3. **Database Tests**
   - Test model creation
   - Test queries
   - Test relationships

### Level 2: Intermediate

4. **Integration Tests**
   - Test multiple services together
   - Test with test database
   - Test error scenarios

5. **Mocking**
   - Mock external APIs
   - Mock database
   - Mock email service

6. **Fixtures**
   - Create reusable fixtures
   - Test data factories
   - Setup/teardown

### Level 3: Challenging

7. **E2E Tests**
   - Complete user journeys
   - Multiple microservices
   - Real database

8. **Performance Tests**
   - Load testing
   - Benchmarking
   - Stress testing

9. **Complete Coverage**
   - 80%+ coverage
   - All critical paths
   - Edge cases

---

## Key Takeaways

✅ **Testing Strategy**:
- Unit tests: Most, fast, cheap
- Integration: Some, medium
- E2E: Few, slow, expensive

✅ **Tools**:
- pytest for test framework
- TestClient for API testing
- pytest-cov for coverage
- Locust for load testing

✅ **Best Practices**:
- Test critical paths first
- Use fixtures for reusable setup
- Mock external dependencies
- Aim for 80%+ coverage
- Write fast, reliable tests

---

Continue to [Part-20-Production-Readiness](../Part-20-Production-Readiness/README.md)!
