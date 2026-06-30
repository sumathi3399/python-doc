# Part 21: Complete E-Commerce Project - Practice Problems

> Final integration checks for the capstone

---

## Problem 1: Service Setup

**Task**: Create basic service structure
```
ecommerce/
├── user-service/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── product-service/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
└── docker-compose.yml
```

**Time**: 20 minutes

---

## Problem 2: User Service API

**Task**: User registration endpoint
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/users/")
def create_user(user: UserCreate):
    # Hash password, save to DB
    return {"id": 1, "username": user.username}
```

**Time**: 20 minutes

---

## Problem 3: Product Service API

**Task**: Product CRUD
```python
from fastapi import FastAPI

app = FastAPI()

products = []

@app.post("/products/")
def create_product(name: str, price: float):
    product = {"id": len(products) + 1, "name": name, "price": price}
    products.append(product)
    return product

@app.get("/products/")
def list_products():
    return products
```

**Time**: 20 minutes

---

## Problem 4: Order Service with Event

**Task**: Create order and publish event
```python
import pika

def create_order(user_id, product_ids):
    order = {"user_id": user_id, "products": product_ids}
    
    # Publish event
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key='orders', body=str(order))
    connection.close()
    
    return order
```

**Time**: 25 minutes

---

## Problem 5: API Gateway

**Task**: Route to services
```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://user-service:8001/users/{user_id}")
        return response.json()

@app.get("/api/products/")
async def get_products():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://product-service:8002/products/")
        return response.json()
```

**Time**: 25 minutes

---

## Problem 6: Database Per Service

**Task**: User service with SQLAlchemy
```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)

engine = create_engine('postgresql://user:pass@localhost/userdb')
Base.metadata.create_all(engine)
```

**Time**: 20 minutes

---

## Problem 7: Redis Caching

**Task**: Cache product list
```python
import redis
import json

r = redis.Redis()

def get_products_cached():
    cached = r.get('products')
    if cached:
        return json.loads(cached)
    
    products = fetch_products_from_db()
    r.setex('products', 300, json.dumps(products))
    return products
```

**Time**: 20 minutes

---

## Problem 8: Docker Compose Full Stack

**Task**: All services together
```yaml
version: '3.8'
services:
  gateway:
    build: ./gateway
    ports:
      - "8000:8000"
  
  user-service:
    build: ./user-service
    ports:
      - "8001:8000"
  
  product-service:
    build: ./product-service
    ports:
      - "8002:8000"
  
  redis:
    image: redis:7
  
  postgres:
    image: postgres:15
```

**Time**: 25 minutes

---

## Problem 9: Integration Test

**Task**: Test full purchase flow
```python
import pytest
from fastapi.testclient import TestClient

def test_purchase_flow():
    # Create user
    response = client.post("/api/users/", json={"username": "alice"})
    user_id = response.json()["id"]
    
    # Get products
    response = client.get("/api/products/")
    products = response.json()
    
    # Create order
    response = client.post("/api/orders/", json={
        "user_id": user_id,
        "product_ids": [products[0]["id"]]
    })
    assert response.status_code == 201
```

**Time**: 30 minutes

---

## Problem 10: Monitoring Dashboard

**Task**: Health check all services
```python
import httpx
import asyncio

async def check_services():
    services = {
        "gateway": "http://localhost:8000/health",
        "user": "http://localhost:8001/health",
        "product": "http://localhost:8002/health"
    }
    
    results = {}
    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            try:
                response = await client.get(url)
                results[name] = "healthy"
            except:
                results[name] = "unhealthy"
    
    return results
```

**Time**: 20 minutes

---

## Summary Check

**8+ solved** → Project complete!  
**5-7 solved** → Finish remaining integrations  
**< 5 solved** → Review Parts 16-20 first

---

**Congratulations! You have completed the Python Backend Stack course!**
