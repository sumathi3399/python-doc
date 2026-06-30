# Part 16: Production FastAPI Project - Practice Problems

> Test layered architecture, testing, config

---

## Problem 1: Project Structure

**Task**: Create layered folders
```
app/
├── api/
│   └── endpoints/
├── core/
│   └── config.py
├── models/
├── schemas/
├── services/
└── tests/
```

**Time**: 10 minutes

---

## Problem 2: Configuration with Settings

**Task**: Environment-based config
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    database_url: str
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Time**: 15 minutes

---

## Problem 3: Custom Exception

**Task**: Domain exception
```python
class NotFoundException(Exception):
    pass

class ValidationException(Exception):
    pass

def get_user(user_id):
    if user_id not in db:
        raise NotFoundException(f"User {user_id} not found")
```

**Time**: 10 minutes

---

## Problem 4: Exception Handler

**Task**: Global error handler
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class AppException(Exception):
    pass

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )
```

**Time**: 15 minutes

---

## Problem 5: Service Layer

**Task**: Business logic separation
```python
# services/user.py
class UserService:
    def __init__(self, db):
        self.db = db
    
    def create_user(self, user_data):
        # Business logic here
        return self.db.add(user_data)

# api/endpoints/users.py
@app.post("/users/")
def create_user(user: UserCreate, service: UserService = Depends()):
    return service.create_user(user)
```

**Time**: 20 minutes

---

## Problem 6: Repository Pattern

**Task**: Data access layer
```python
class UserRepository:
    def __init__(self, db):
        self.db = db
    
    def get_by_id(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create(self, user_data):
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        return user
```

**Time**: 20 minutes

---

## Problem 7: Dependency Injection

**Task**: Get DB session
```python
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

**Time**: 15 minutes

---

## Problem 8: Structured Logging

**Task**: Request logging middleware
```python
import time
import logging

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logging.info(f"{request.method} {request.url} - {duration:.2f}s")
    return response
```

**Time**: 15 minutes

---

## Problem 9: Test with TestClient

**Task**: API endpoint test
```python
from fastapi.testclient import TestClient

def test_read_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}
```

**Time**: 15 minutes

---

## Problem 10: Health Check Endpoint

**Task**: Readiness probe
```python
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Check DB connection
        db.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

**Time**: 15 minutes

---

## Summary Check

**8+ solved** → Production patterns understood  
**5-7 solved** → Practice layered architecture  
**< 5 solved** → Review separation of concerns
