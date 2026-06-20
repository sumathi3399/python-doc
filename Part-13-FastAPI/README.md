# Part 13: FastAPI

> Build modern, high-performance REST APIs with FastAPI - the fastest Python web framework.

## 📚 Table of Contents

1. [FastAPI Introduction](#1-fastapi-introduction)
2. [Request Handling](#2-request-handling)
3. [Response Handling](#3-response-handling)
4. [Dependency Injection](#4-dependency-injection)
5. [Validation with Pydantic](#5-validation-with-pydantic)
6. [Routing](#6-routing)
7. [Middleware](#7-middleware)
8. [Authentication & Authorization](#8-authentication--authorization)
9. [Error Handling](#9-error-handling)
10. [Background Tasks](#10-background-tasks)
11. [WebSockets](#11-websockets)
12. [Exercises](#exercises)

---

## 1. FastAPI Introduction

### What is FastAPI?

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

**Key Features:**
- **Fast**: Very high performance, on par with NodeJS and Go
- **Fast to code**: Increase development speed by 200-300%
- **Fewer bugs**: Reduce human-induced errors by 40%
- **Intuitive**: Great editor support with autocomplete
- **Easy**: Designed to be easy to use and learn
- **Short**: Minimize code duplication
- **Robust**: Production-ready code with automatic interactive docs

### Why FastAPI?

```python
# Comparison with Flask

# Flask
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Manual validation
    if not isinstance(user_id, int):
        return jsonify({"error": "Invalid ID"}), 400
    
    # Manual response
    user = {"id": user_id, "name": "Alice"}
    return jsonify(user)

# FastAPI
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=User)
async def get_user(user_id: int):
    # Automatic validation
    # Automatic serialization
    # Automatic documentation
    return User(id=user_id, name="Alice")
```

### FastAPI Architecture

```python
"""
FastAPI Architecture:

┌─────────────────────────────────────┐
│         Client Request              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         ASGI Server (Uvicorn)       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Middleware Stack            │
│  (CORS, Auth, Logging, etc.)       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Route Handler               │
│  (Your endpoint function)           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Request Validation             │
│      (Pydantic Models)              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Dependency Injection           │
│      (DB, Auth, etc.)               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Business Logic                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Response Serialization         │
│      (Pydantic Models)              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Client Response             │
└─────────────────────────────────────┘
"""
```

### ASGI Servers (Uvicorn)

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Run with Uvicorn
# Terminal:
# uvicorn main:app --reload

# With custom settings
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload --workers 4

# In code
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        workers=4     # Number of worker processes
    )

# Access:
# - API: http://localhost:8000
# - Interactive docs (Swagger): http://localhost:8000/docs
# - Alternative docs (ReDoc): http://localhost:8000/redoc
```

---

## 2. Request Handling

### Path Parameters

```python
from fastapi import FastAPI, Path

app = FastAPI()

# Basic path parameter
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

# Multiple path parameters
@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}

# Path with validation
@app.get("/items/{item_id}")
async def get_item(
    item_id: int = Path(
        ...,
        title="Item ID",
        description="The ID of the item to get",
        ge=1,  # Greater than or equal to 1
        le=1000  # Less than or equal to 1000
    )
):
    return {"item_id": item_id}

# String path parameter
@app.get("/users/{username}")
async def get_user_by_name(
    username: str = Path(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$"
    )
):
    return {"username": username}

# Enum path parameter
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    return {"model_name": model_name, "message": "Have some residuals"}
```

### Query Parameters

```python
from fastapi import FastAPI, Query
from typing import Optional, List

app = FastAPI()

# Basic query parameters
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
# Usage: /items/?skip=20&limit=10

# Optional query parameters
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

# Query with validation
@app.get("/items/")
async def read_items(
    q: str = Query(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9\s]+$",
        title="Query string",
        description="Search query"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return {"q": q, "skip": skip, "limit": limit}

# Required query parameter
@app.get("/items/")
async def read_items(q: str = Query(..., min_length=3)):  # Required
    return {"q": q}

# List query parameters
@app.get("/items/")
async def read_items(tags: List[str] = Query([])):
    return {"tags": tags}
# Usage: /items/?tags=python&tags=fastapi&tags=web

# Boolean query parameter
@app.get("/items/")
async def read_items(active: bool = True):
    return {"active": active}
# Usage: /items/?active=false
```

### Request Body

```python
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# Simple request body
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax:
        item_dict["price_with_tax"] = item.price + item.tax
    return item_dict

# Multiple body parameters
class User(BaseModel):
    username: str
    full_name: Optional[str] = None

@app.post("/items/")
async def create_item(item: Item, user: User):
    return {"item": item, "user": user}

# Body with validation
class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0, description="Price must be positive")
    tax: float = Field(0, ge=0, le=100)
    tags: List[str] = Field(default_factory=list)

@app.post("/items/")
async def create_item(item: Item):
    return item

# Nested models
class Image(BaseModel):
    url: str
    name: str

class Item(BaseModel):
    name: str
    price: float
    images: Optional[List[Image]] = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Headers

```python
from fastapi import FastAPI, Header
from typing import Optional

app = FastAPI()

# Read headers
@app.get("/items/")
async def read_items(user_agent: Optional[str] = Header(None)):
    return {"User-Agent": user_agent}

# Custom headers
@app.get("/items/")
async def read_items(
    x_token: str = Header(...),
    x_request_id: Optional[str] = Header(None)
):
    return {"X-Token": x_token, "X-Request-ID": x_request_id}

# Duplicate headers
from typing import List

@app.get("/items/")
async def read_items(x_tag: List[str] = Header([])):
    return {"X-Tag": x_tag}
```

### Cookies

```python
from fastapi import FastAPI, Cookie
from typing import Optional

app = FastAPI()

@app.get("/items/")
async def read_items(
    session_id: Optional[str] = Cookie(None),
    ads_id: Optional[str] = Cookie(None)
):
    return {"session_id": session_id, "ads_id": ads_id}
```

### Form Data

```python
from fastapi import FastAPI, Form

app = FastAPI()

# pip install python-multipart

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}

# Form with validation
@app.post("/signup/")
async def signup(
    username: str = Form(..., min_length=3, max_length=20),
    email: str = Form(...),
    password: str = Form(..., min_length=8),
    agree_to_terms: bool = Form(...)
):
    return {"username": username, "email": email}
```

### File Uploads

```python
from fastapi import FastAPI, File, UploadFile
from typing import List

app = FastAPI()

# Small file upload (loaded into memory)
@app.post("/upload/")
async def upload_file(file: bytes = File(...)):
    return {"file_size": len(file)}

# Large file upload (streamed)
@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

# Multiple file uploads
@app.post("/uploadfiles/")
async def upload_files(files: List[UploadFile]):
    return {
        "filenames": [file.filename for file in files]
    }

# File upload with form data
@app.post("/upload/")
async def upload_file(
    file: UploadFile,
    title: str = Form(...),
    description: str = Form(None)
):
    return {
        "filename": file.filename,
        "title": title,
        "description": description
    }

# Save uploaded file
import aiofiles

@app.post("/upload/")
async def upload_file(file: UploadFile):
    async with aiofiles.open(f"uploads/{file.filename}", 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return {"filename": file.filename, "saved": True}
```

---

## 3. Response Handling

### Response Models

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import Optional, List

app = FastAPI()

class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    username: str
    email: EmailStr
    # No password field!

# Automatic response filtering
@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn):
    # Even if we return the whole user with password
    # FastAPI will only include fields from UserOut
    return user

# Response model with list
class Item(BaseModel):
    name: str
    price: float

@app.get("/items/", response_model=List[Item])
async def get_items():
    return [
        {"name": "Item 1", "price": 10.5},
        {"name": "Item 2", "price": 20.0}
    ]

# Response model with optional fields
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    return {
        "username": "john",
        "email": "john@example.com",
        # full_name and disabled are optional
    }
```

### Status Codes

```python
from fastapi import FastAPI, status

app = FastAPI()

# Explicit status code
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}

# Common status codes
@app.get("/items/", status_code=200)  # OK
@app.post("/items/", status_code=201)  # Created
@app.delete("/items/{item_id}", status_code=204)  # No Content
@app.patch("/items/{item_id}", status_code=200)  # OK

# Dynamic status code
from fastapi import Response

@app.post("/items/")
async def create_item(name: str, response: Response):
    if name == "exists":
        response.status_code = status.HTTP_200_OK
        return {"message": "Item already exists"}
    
    response.status_code = status.HTTP_201_CREATED
    return {"name": name}
```

### Response Headers

```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/items/")
async def get_items(response: Response):
    response.headers["X-Custom-Header"] = "Custom Value"
    response.headers["X-Total-Count"] = "100"
    return {"items": []}

# Set-Cookie header
@app.post("/login/")
async def login(response: Response):
    response.set_cookie(key="session_id", value="abc123", httponly=True)
    return {"message": "Logged in"}
```

### Custom Responses

```python
from fastapi import FastAPI
from fastapi.responses import (
    JSONResponse,
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    FileResponse,
    StreamingResponse
)

app = FastAPI()

# JSON response (default)
@app.get("/json/")
async def get_json():
    return {"message": "Hello"}

# HTML response
@app.get("/html/", response_class=HTMLResponse)
async def get_html():
    return "<html><body><h1>Hello World</h1></body></html>"

# Plain text response
@app.get("/text/", response_class=PlainTextResponse)
async def get_text():
    return "Hello World"

# Redirect response
@app.get("/redirect/")
async def redirect():
    return RedirectResponse(url="/new-url")

# File response
@app.get("/download/")
async def download_file():
    return FileResponse(
        path="file.pdf",
        media_type="application/pdf",
        filename="download.pdf"
    )

# Custom JSON response
@app.get("/custom/")
async def custom_response():
    return JSONResponse(
        content={"message": "Hello"},
        status_code=200,
        headers={"X-Custom": "Value"}
    )
```

### Streaming Responses

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

# Stream generator
async def generate_data():
    for i in range(10):
        await asyncio.sleep(0.5)
        yield f"data: {i}\n\n"

@app.get("/stream/")
async def stream():
    return StreamingResponse(
        generate_data(),
        media_type="text/event-stream"
    )

# Stream file
@app.get("/stream-file/")
async def stream_file():
    async def file_generator():
        with open("large_file.txt", "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    return StreamingResponse(
        file_generator(),
        media_type="application/octet-stream"
    )
```

---

## 4. Dependency Injection

### Depends() Function

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Simple dependency
def get_query_param(q: str = None):
    return q

@app.get("/items/")
async def read_items(query: str = Depends(get_query_param)):
    return {"query": query}

# Class-based dependency
class Pagination:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(pagination: Pagination = Depends()):
    return {
        "skip": pagination.skip,
        "limit": pagination.limit
    }

# Database dependency
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
async def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

### Dependency Scopes

```python
from fastapi import FastAPI, Depends, Request

app = FastAPI()

# Request-scoped dependency (default)
async def get_request_id(request: Request):
    return request.headers.get("X-Request-ID", "unknown")

@app.get("/items/")
async def read_items(request_id: str = Depends(get_request_id)):
    return {"request_id": request_id}

# Application-scoped (singleton)
class DatabaseConnection:
    def __init__(self):
        self.connection = "db://connection"
    
    def get_connection(self):
        return self.connection

db_connection = DatabaseConnection()

def get_db_connection():
    return db_connection.get_connection()

@app.get("/items/")
async def read_items(conn: str = Depends(get_db_connection)):
    return {"connection": conn}
```

### Dependency Inheritance

```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()

# Base dependencies
def verify_token(x_token: str = Header(...)):
    if x_token != "secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return x_token

def verify_key(x_key: str = Header(...)):
    if x_key != "secret-key":
        raise HTTPException(status_code=401, detail="Invalid key")
    return x_key

# Nested dependencies
def get_current_user(token: str = Depends(verify_token)):
    # Decode token and get user
    return {"username": "john", "token": token}

def get_admin_user(user: dict = Depends(get_current_user)):
    if user["username"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user

# Apply dependencies to endpoints
@app.get("/users/me/")
async def read_current_user(user: dict = Depends(get_current_user)):
    return user

@app.get("/admin/")
async def admin_panel(admin: dict = Depends(get_admin_user)):
    return {"message": "Admin panel", "admin": admin}

# Router-level dependencies
from fastapi import APIRouter

admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(get_admin_user)]  # Apply to all routes
)

@admin_router.get("/dashboard/")
async def dashboard():
    return {"message": "Admin dashboard"}

@admin_router.get("/users/")
async def users():
    return {"message": "Admin users"}

app.include_router(admin_router)
```

### Dependency Overrides

```python
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()

# Real dependency
def get_db():
    return "real_database"

@app.get("/items/")
async def read_items(db: str = Depends(get_db)):
    return {"db": db}

# Override for testing
def get_test_db():
    return "test_database"

app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)
response = client.get("/items/")
print(response.json())  # {"db": "test_database"}
```

---

## 5. Validation with Pydantic

### Request Validation

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional

app = FastAPI()

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    tax: float = Field(0, ge=0, le=100)
    
    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        if not v.replace(' ', '').isalnum():
            raise ValueError('name must be alphanumeric')
        return v.title()
    
    @validator('price')
    def price_must_be_reasonable(cls, v):
        if v > 1000000:
            raise ValueError('price seems unrealistic')
        return v

@app.post("/items/")
async def create_item(item: Item):
    return item

# FastAPI automatically validates the request
# If validation fails, returns 422 Unprocessable Entity
```

### Response Validation

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/", response_model=List[Item])
async def get_items():
    # FastAPI validates the response matches the model
    return [
        {"name": "Item 1", "price": 10.5},
        {"name": "Item 2", "price": 20.0}
    ]
    # If we return invalid data, FastAPI raises an error
```

### Custom Validators

```python
from fastapi import FastAPI
from pydantic import BaseModel, validator, root_validator

app = FastAPI()

class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('username too short')
        if not v.isalnum():
            raise ValueError('username must be alphanumeric')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('password too short')
        if not any(c.isupper() for c in v):
            raise ValueError('password must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('password must contain digit')
        return v
    
    @root_validator
    def verify_password_match(cls, values):
        password = values.get('password')
        confirm = values.get('confirm_password')
        if password != confirm:
            raise ValueError('passwords do not match')
        return values

@app.post("/register/")
async def register(user: UserRegistration):
    return {"username": user.username, "email": user.email}
```

### Error Responses

```python
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

app = FastAPI()

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
    )

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item

# Request with invalid data returns:
# {
#     "detail": [
#         {
#             "field": "price",
#             "message": "value is not a valid float",
#             "type": "type_error.float"
#         }
#     ]
# }
```

---

I'll continue with the remaining sections. Let me create the rest of Part 13:

<function_calls>
<invoke name="StrReplace">
<parameter name="path">/Users/sumathi.nadakuditi/Desktop/Python stack/Part-13-FastAPI/README.md