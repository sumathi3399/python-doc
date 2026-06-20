# Part 16: Production-Grade FastAPI Project

> Build production-ready FastAPI applications with proper architecture, testing, and deployment strategies.

## 📚 Table of Contents

1. [Project Structure](#1-project-structure)
2. [Configuration Management](#2-configuration-management)
3. [Database Integration](#3-database-integration)
4. [Service Layer](#4-service-layer)
5. [Error Handling](#5-error-handling)
6. [Logging](#6-logging)
7. [Validation & Schemas](#7-validation--schemas)
8. [Testing Setup](#8-testing-setup)
9. [Complete Project Example](#complete-project-example)

---

## 1. Project Structure

### Folder Organization

```
app/
├── __init__.py
├── main.py                 # Application entry point
├── api/                    # API layer
│   ├── __init__.py
│   ├── deps.py            # Shared dependencies
│   └── v1/                # API version 1
│       ├── __init__.py
│       ├── router.py      # Main router
│       └── endpoints/     # Endpoint modules
│           ├── __init__.py
│           ├── users.py
│           ├── auth.py
│           └── items.py
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── security.py        # Security utilities
│   ├── logging.py         # Logging setup
│   └── exceptions.py      # Custom exceptions
├── db/                     # Database layer
│   ├── __init__.py
│   ├── base.py            # Base model
│   ├── session.py         # Database session
│   └── repositories/      # Data access layer
│       ├── __init__.py
│       ├── base.py
│       ├── user.py
│       └── item.py
├── models/                 # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   └── item.py
├── schemas/                # Pydantic schemas
│   ├── __init__.py
│   ├── user.py
│   └── item.py
├── services/               # Business logic
│   ├── __init__.py
│   ├── user.py
│   └── item.py
├── utils/                  # Utilities
│   ├── __init__.py
│   ├── email.py
│   └── validators.py
└── tests/                  # Tests
    ├── __init__.py
    ├── conftest.py
    ├── test_users.py
    └── test_items.py

# Additional files
.env                        # Environment variables
.env.example               # Example environment file
.gitignore
requirements.txt           # Dependencies
README.md
docker-compose.yml
Dockerfile
alembic.ini               # Database migrations
pytest.ini                # Pytest configuration
```

### Separation of Concerns

```python
"""
Layered Architecture:

1. API Layer (api/)
   - HTTP request/response handling
   - Request validation
   - Route definitions
   - Dependency injection

2. Service Layer (services/)
   - Business logic
   - Orchestration
   - Transaction management
   - Complex operations

3. Repository Layer (db/repositories/)
   - Data access
   - Database queries
   - CRUD operations
   - Data persistence

4. Model Layer (models/)
   - SQLAlchemy models
   - Database schema
   - Relationships

5. Schema Layer (schemas/)
   - Pydantic models
   - Request/response validation
   - Data serialization
"""
```

### Layered Architecture

```python
# models/user.py (Database Model)
from sqlalchemy import Column, Integer, String, Boolean
from db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

# schemas/user.py (Pydantic Schemas)
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

# db/repositories/user.py (Data Access)
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, user: UserCreate, hashed_password: str) -> User:
        db_user = User(
            email=user.email,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

# services/user.py (Business Logic)
from core.security import get_password_hash, verify_password
from db.repositories.user import UserRepository
from schemas.user import UserCreate

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, user: UserCreate):
        # Check if user exists
        existing = self.user_repo.get_by_email(user.email)
        if existing:
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create user
        return self.user_repo.create(user, hashed_password)
    
    def authenticate(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

# api/v1/endpoints/users.py (API Endpoints)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db
from services.user import UserService
from db.repositories.user import UserRepository
from schemas.user import UserCreate, UserResponse

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        db_user = service.create_user(user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 2. Configuration Management

### Environment Variables

```python
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
SECRET_KEY=your-secret-key-here
DEBUG=True
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# .env.example (commit this)
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
SECRET_KEY=change-me
DEBUG=False
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:3000
```

### pydantic-settings

```python
# core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "My API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Usage in other modules
from core.config import settings

print(settings.DATABASE_URL)
print(settings.SECRET_KEY)
```

### Multiple Environments

```python
# core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal

class BaseConfig(BaseSettings):
    APP_NAME: str = "My API"
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"

class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./dev.db"
    LOG_LEVEL: str = "DEBUG"

class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"
    
    # Additional production settings
    SENTRY_DSN: str = ""
    
class TestingConfig(BaseConfig):
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    LOG_LEVEL: str = "DEBUG"

# Config factory
@lru_cache()
def get_settings() -> BaseConfig:
    import os
    env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    return config_class()

settings = get_settings()
```

---

## 3. Database Integration

### SQLAlchemy with FastAPI

```python
# db/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here for Alembic
from models.user import User
from models.item import Item

# db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# main.py
from fastapi import FastAPI
from db.base import Base
from db.session import engine

app = FastAPI()

# Create tables
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

# Usage in endpoints
from fastapi import Depends
from sqlalchemy.orm import Session
from db.session import get_db

@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Dependency Injection for DB

```python
# api/deps.py
from typing import Generator
from sqlalchemy.orm import Session
from db.session import SessionLocal

def get_db() -> Generator:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage
from fastapi import Depends
from sqlalchemy.orm import Session
from api.deps import get_db

@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Repository Pattern

```python
# db/repositories/base.py
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        db_obj = self.get(id)
        if db_obj:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

# db/repositories/user.py
from db.repositories.base import BaseRepository
from models.user import User
from sqlalchemy.orm import Session

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> User:
        return self.db.query(self.model).filter(
            self.model.email == email
        ).first()
    
    def get_active_users(self) -> List[User]:
        return self.db.query(self.model).filter(
            self.model.is_active == True
        ).all()

# Usage
def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repo)
):
    user = repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## 4. Service Layer

### Business Logic Separation

```python
# services/base.py
from typing import Generic, TypeVar
from db.repositories.base import BaseRepository

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[RepositoryType]):
    def __init__(self, repository: RepositoryType):
        self.repository = repository

# services/user.py
from services.base import BaseService
from db.repositories.user import UserRepository
from schemas.user import UserCreate, UserUpdate
from core.security import get_password_hash, verify_password
from fastapi import HTTPException, status

class UserService(BaseService[UserRepository]):
    def create_user(self, user: UserCreate):
        # Business logic
        existing = self.repository.get_by_email(user.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create user
        user_data = user.dict()
        user_data['hashed_password'] = hashed_password
        del user_data['password']
        
        return self.repository.create(user_data)
    
    def authenticate(self, email: str, password: str):
        user = self.repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    def update_user(self, user_id: int, user_update: UserUpdate):
        existing = self.repository.get(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = user_update.dict(exclude_unset=True)
        
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data['password'])
            del update_data['password']
        
        return self.repository.update(user_id, update_data)

# api/deps.py
from sqlalchemy.orm import Session
from db.repositories.user import UserRepository
from services.user import UserService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

# api/v1/endpoints/users.py
@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return service.create_user(user)
```

### Service Classes

```python
# services/item.py
from services.base import BaseService
from db.repositories.item import ItemRepository
from schemas.item import ItemCreate, ItemUpdate
from fastapi import HTTPException, status

class ItemService(BaseService[ItemRepository]):
    def create_item(self, owner_id: int, item: ItemCreate):
        item_data = item.dict()
        item_data['owner_id'] = owner_id
        return self.repository.create(item_data)
    
    def get_user_items(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.repository.get_by_owner(user_id, skip, limit)
    
    def update_item(self, item_id: int, item_update: ItemUpdate, user_id: int):
        # Check ownership
        item = self.repository.get(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        if item.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this item"
            )
        
        update_data = item_update.dict(exclude_unset=True)
        return self.repository.update(item_id, update_data)
    
    def delete_item(self, item_id: int, user_id: int) -> bool:
        item = self.repository.get(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        if item.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this item"
            )
        
        return self.repository.delete(item_id)
```

### Use Case Patterns

```python
# services/use_cases/register_user.py
from dataclasses import dataclass
from schemas.user import UserCreate
from services.user import UserService
from utils.email import send_welcome_email

@dataclass
class RegisterUserUseCase:
    """Use case for user registration"""
    user_service: UserService
    
    def execute(self, user_data: UserCreate):
        # 1. Create user
        user = self.user_service.create_user(user_data)
        
        # 2. Send welcome email (async task)
        send_welcome_email(user.email)
        
        # 3. Log registration
        logger.info(f"New user registered: {user.email}")
        
        return user

# Usage
from fastapi import BackgroundTasks

@router.post("/register/")
def register(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    service: UserService = Depends(get_user_service)
):
    use_case = RegisterUserUseCase(service)
    new_user = use_case.execute(user)
    
    # Add background task
    background_tasks.add_task(send_welcome_email, new_user.email)
    
    return new_user
```

---

## 5. Error Handling

### Custom Exceptions

```python
# core/exceptions.py
class AppException(Exception):
    """Base exception for application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)

class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)

class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=400)

class ConflictException(AppException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status_code=409)
```

### Error Handlers

```python
# main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from core.exceptions import AppException
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# Custom exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": str(request.url)
        }
    )

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": errors
        }
    )

# Generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred"
        }
    )
```

### Error Responses

```python
# schemas/errors.py
from pydantic import BaseModel
from typing import Optional, List

class ErrorDetail(BaseModel):
    field: str
    message: str
    type: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    path: Optional[str] = None
    details: Optional[List[ErrorDetail]] = None

# Usage in endpoints
from fastapi import HTTPException
from schemas.errors import ErrorResponse

@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def get_user(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user
```

---

## 6. Logging

### structlog Setup

```python
# core/logging.py
import logging
import structlog
from core.config import settings

def setup_logging():
    """Configure structured logging"""
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=settings.LOG_LEVEL,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# main.py
from core.logging import setup_logging

setup_logging()

logger = structlog.get_logger()

@app.on_event("startup")
async def startup():
    logger.info("application_startup", version=settings.APP_VERSION)
```

### Request Logging

```python
# core/logging.py
import time
import structlog
from fastapi import Request

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    
    # Bind request ID to logger context
    logger_with_context = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method
    )
    
    # Log request
    logger_with_context.info(
        "request_started",
        client_host=request.client.host
    )
    
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger_with_context.info(
        "request_completed",
        status_code=response.status_code,
        duration=f"{duration:.3f}s"
    )
    
    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.3f}"
    
    return response
```

### Error Logging

```python
# core/logging.py
import structlog
from fastapi import Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger()

@app.exception_handler(Exception)
async def log_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc)
    )
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# In services
class UserService:
    def create_user(self, user: UserCreate):
        try:
            logger.info("creating_user", email=user.email)
            db_user = self.repository.create(user)
            logger.info("user_created", user_id=db_user.id)
            return db_user
        except Exception as e:
            logger.error(
                "user_creation_failed",
                email=user.email,
                error=str(e)
            )
            raise
```

---

## 7. Validation & Schemas

### Pydantic Schemas

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Request/Response Models

```python
# schemas/item.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)

class ItemResponse(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ItemListResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    page: int
    per_page: int
```

### Schema Organization

```python
# schemas/__init__.py
from .user import UserCreate, UserUpdate, UserResponse
from .item import ItemCreate, ItemUpdate, ItemResponse
from .auth import Token, TokenPayload
from .common import PaginationParams, ResponseMetadata

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    "Token",
    "TokenPayload",
    "PaginationParams",
    "ResponseMetadata"
]

# schemas/common.py
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

class ResponseMetadata(BaseModel):
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
```

---

## 8. Testing Setup

### pytest Configuration

```python
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=app --cov-report=html --cov-report=term-missing

# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base
from db.session import get_db
from main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

### Test Fixtures

```python
# tests/conftest.py (continued)
import pytest
from models.user import User
from core.security import get_password_hash

@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    from core.security import create_access_token
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_items(db, test_user):
    items = [
        Item(title=f"Item {i}", owner_id=test_user.id, price=10.0 * i)
        for i in range(1, 6)
    ]
    db.add_all(items)
    db.commit()
    return items
```

### Mocking

```python
# tests/test_users.py
import pytest
from unittest.mock import Mock, patch
from services.user import UserService

def test_create_user(client, db):
    user_data = {
        "email": "newuser@example.com",
        "password": "Password123",
        "full_name": "New User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "password" not in data

def test_create_user_duplicate_email(client, test_user):
    user_data = {
        "email": test_user.email,  # Duplicate
        "password": "Password123",
        "full_name": "New User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

@patch('utils.email.send_email')
def test_create_user_sends_email(mock_send_email, client):
    user_data = {
        "email": "test@example.com",
        "password": "Password123",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 200
    mock_send_email.assert_called_once_with(
        to_email=user_data["email"],
        subject="Welcome!"
    )

# tests/test_items.py
def test_get_items(client, test_items, auth_headers):
    response = client.get("/api/v1/items/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5

def test_get_items_unauthorized(client):
    response = client.get("/api/v1/items/")
    
    assert response.status_code == 401

def test_create_item(client, auth_headers):
    item_data = {
        "title": "New Item",
        "description": "Item description",
        "price": 29.99
    }
    
    response = client.post(
        "/api/v1/items/",
        json=item_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == item_data["title"]
    assert data["price"] == item_data["price"]
```

---

## Complete Project Example

Let me create a complete, working example that ties everything together:

```python
# Complete Production-Grade FastAPI Project Example
# This demonstrates all concepts covered in Part 16

"""
Project Structure:
app/
├── main.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── exceptions.py
├── db/
│   ├── base.py
│   ├── session.py
│   └── repositories/
│       └── user.py
├── models/
│   └── user.py
├── schemas/
│   └── user.py
├── services/
│   └── user.py
├── api/
│   ├── deps.py
│   └── v1/
│       ├── router.py
│       └── endpoints/
│           └── users.py
└── tests/
    ├── conftest.py
    └── test_users.py
"""

# See individual files in the example project repository
# This completes the comprehensive FastAPI production template
```

---

## Summary

### Key Concepts

1. **Project Structure**
   - Layered architecture
   - Separation of concerns
   - Clean code organization

2. **Configuration**
   - Environment variables
   - Settings management
   - Multiple environments

3. **Database**
   - SQLAlchemy integration
   - Repository pattern
   - Dependency injection

4. **Business Logic**
   - Service layer
   - Use case patterns
   - Transaction management

5. **Error Handling**
   - Custom exceptions
   - Global handlers
   - Structured responses

6. **Logging**
   - Structured logging
   - Request logging
   - Error tracking

7. **Validation**
   - Pydantic schemas
   - Request/response models
   - Custom validators

8. **Testing**
   - pytest setup
   - Fixtures
   - Mocking

### Best Practices

✅ **DO:**
- Follow layered architecture
- Use dependency injection
- Implement proper error handling
- Add comprehensive logging
- Write tests
- Use type hints
- Document APIs
- Handle secrets securely

❌ **DON'T:**
- Mix business logic in endpoints
- Hardcode configuration
- Skip error handling
- Forget logging
- Skip tests
- Expose sensitive data
- Ignore security

### Next Steps

You now have a complete production-grade FastAPI template! Next:
- Deploy to production
- Add monitoring (Prometheus, Grafana)
- Implement CI/CD
- Scale horizontally
- Add caching layers
- Implement rate limiting
- Add authentication/authorization

---

**🎉 Congratulations! You've completed the comprehensive Python Backend Stack course!** →
