# Part 13: FastAPI - Practice Problems

> Test routing, request/response, dependencies

---

## Problem 1: Basic GET Endpoint

**Task**: Hello World API
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Test with: uvicorn main:app --reload
```

**Time**: 10 minutes

---

## Problem 2: Path Parameters

**Task**: Get item by ID
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

# Test: GET /items/42
```

**Time**: 10 minutes

---

## Problem 3: Query Parameters

**Task**: Optional query params
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Test: GET /items/?skip=0&limit=20
```

**Time**: 10 minutes

---

## Problem 4: Request Body with Pydantic

**Task**: POST endpoint with validation
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

@app.post("/items/")
def create_item(item: Item):
    return item

# Test with JSON body
```

**Time**: 15 minutes

---

## Problem 5: Response Model

**Task**: Control response shape
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str

@app.post("/users/", response_model=UserOut)
def create_user(user: UserIn):
    return user  # password excluded in response
```

**Time**: 15 minutes

---

## Problem 6: Status Codes

**Task**: Return 201 on creation
```python
from fastapi import FastAPI, status

app = FastAPI()

@app.post("/items/", status_code=status.HTTP_201_CREATED)
def create_item(name: str):
    return {"name": name}
```

**Time**: 10 minutes

---

## Problem 7: HTTPException

**Task**: Raise 404 error
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

items = {"foo": "The Foo"}

@app.get("/items/{item_id}")
def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}
```

**Time**: 15 minutes

---

## Problem 8: Dependency Injection

**Task**: Common query parameters
```python
from fastapi import FastAPI, Depends

app = FastAPI()

def common_parameters(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@app.get("/items/")
def read_items(commons: dict = Depends(common_parameters)):
    return commons
```

**Time**: 20 minutes

---

## Problem 9: Router

**Task**: Organize endpoints
```python
from fastapi import APIRouter, FastAPI

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
def read_items():
    return [{"name": "Item 1"}]

@router.get("/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

app = FastAPI()
app.include_router(router)
```

**Time**: 15 minutes

---

## Problem 10: Background Tasks

**Task**: Send email after response
```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def send_email(email: str):
    print(f"Sending email to {email}")

@app.post("/send-notification/")
def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email)
    return {"message": "Email will be sent"}
```

**Time**: 15 minutes

---

## Summary Check

**8+ solved** → FastAPI basics mastered  
**5-7 solved** → Practice dependencies and routing  
**< 5 solved** → Review FastAPI documentation
