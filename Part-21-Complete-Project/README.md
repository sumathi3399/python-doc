# Part 21: Complete E-Commerce Microservices Project

> Build a production-ready e-commerce platform using all the skills you've learned throughout this course.

## 📚 Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Service Specifications](#3-service-specifications)
4. [Implementation Guide](#4-implementation-guide)
5. [Testing Strategy](#5-testing-strategy)
6. [Deployment](#6-deployment)
7. [Monitoring & Observability](#7-monitoring--observability)
8. [Final Checklist](#8-final-checklist)

---

## 1. Project Overview

### Project Goal

Build a complete, production-ready e-commerce microservices platform that demonstrates mastery of:
- Python fundamentals through advanced concepts
- FastAPI for building REST APIs
- Microservices architecture
- Async programming
- Database design
- Message queuing
- Testing
- Production deployment

### Features

#### User Features
- ✅ User registration and authentication
- ✅ Browse products by category
- ✅ Search products
- ✅ Shopping cart management
- ✅ Place orders
- ✅ Payment processing
- ✅ Order tracking
- ✅ Email notifications

#### Admin Features
- ✅ Product management (CRUD)
- ✅ Inventory management
- ✅ Order management
- ✅ User management
- ✅ Analytics dashboard

### Technology Stack

```
Backend Services:
- FastAPI (Python 3.11+)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Redis (Caching & Sessions)
- Kafka (Event Streaming)

Infrastructure:
- Docker & Docker Compose
- Kubernetes (optional)
- Nginx (API Gateway)

Monitoring:
- Prometheus (Metrics)
- Grafana (Dashboards)
- Jaeger (Distributed Tracing)
- Structlog (Logging)

Testing:
- pytest
- pytest-asyncio
- TestClient
```

---

## 2. System Architecture

### High-Level Architecture

```
┌──────────────┐
│   Client     │
│  (Browser)   │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ API Gateway  │ (Nginx/FastAPI)
│   Port 8000  │
└──────┬───────┘
       │
       ├────────────────────────────────────────┐
       │                                        │
       ↓                                        ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ User Service │  │   Product    │  │    Order     │
│   :8001      │  │   Service    │  │   Service    │
│              │  │   :8002      │  │   :8003      │
│  PostgreSQL  │  │  PostgreSQL  │  │  PostgreSQL  │
└──────────────┘  └──────────────┘  └──────┬───────┘
                                            │
                                            │ Kafka
                                            ↓
                  ┌──────────────┐  ┌──────────────┐
                  │   Payment    │  │Notification  │
                  │   Service    │  │   Service    │
                  │   :8004      │  │   :8005      │
                  │  PostgreSQL  │  │              │
                  └──────────────┘  └──────────────┘

                  ┌──────────────┐
                  │    Redis     │ (Caching)
                  │    :6379     │
                  └──────────────┘
```

### Data Flow

```
1. User Registration/Login:
   Client → API Gateway → User Service → Database

2. Browse Products:
   Client → API Gateway → Product Service → Cache/Database

3. Place Order:
   Client → API Gateway → Order Service → Database
                       → Kafka ("order.created")
                       → Payment Service (processes payment)
                       → Kafka ("payment.completed")
                       → Order Service (updates order)
                       → Kafka ("order.confirmed")
                       → Notification Service (sends email)

4. Admin Operations:
   Client → API Gateway → Service → Database
```

---

## 3. Service Specifications

### Service 1: User Service (Port 8001)

**Responsibilities:**
- User registration
- Authentication (JWT)
- User profile management
- Password reset

**Database Schema:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20)
);
```

**API Endpoints:**
```
POST   /auth/register          - Register new user
POST   /auth/login             - Login (get JWT)
POST   /auth/refresh           - Refresh token
POST   /auth/logout            - Logout
GET    /users/me               - Get current user
PUT    /users/me               - Update profile
POST   /users/me/change-password
GET    /health                 - Health check
```

### Service 2: Product Service (Port 8002)

**Responsibilities:**
- Product catalog management
- Category management
- Product search
- Inventory tracking

**Database Schema:**
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    stock_quantity INTEGER DEFAULT 0,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**API Endpoints:**
```
GET    /products               - List products (paginated, filterable)
GET    /products/:id           - Get product details
POST   /products               - Create product (admin)
PUT    /products/:id           - Update product (admin)
DELETE /products/:id           - Delete product (admin)
GET    /products/search        - Search products
GET    /categories             - List categories
POST   /categories             - Create category (admin)
GET    /health                 - Health check
```

### Service 3: Order Service (Port 8003)

**Responsibilities:**
- Shopping cart management
- Order creation
- Order status management
- Order history

**Database Schema:**
```sql
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id),
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL, -- pending, paid, confirmed, shipped, delivered, cancelled
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
```

**API Endpoints:**
```
# Cart
POST   /cart/items             - Add item to cart
GET    /cart                   - Get cart
PUT    /cart/items/:id         - Update cart item
DELETE /cart/items/:id         - Remove from cart

# Orders
POST   /orders                 - Create order from cart
GET    /orders                 - List user orders
GET    /orders/:id             - Get order details
PUT    /orders/:id/cancel      - Cancel order
GET    /admin/orders           - List all orders (admin)
PUT    /admin/orders/:id/status - Update order status (admin)
GET    /health                 - Health check
```

### Service 4: Payment Service (Port 8004)

**Responsibilities:**
- Process payments (simulated)
- Payment status tracking
- Refunds

**Database Schema:**
```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    payment_method VARCHAR(50) NOT NULL, -- credit_card, paypal, etc.
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL, -- pending, completed, failed, refunded
    transaction_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Kafka Consumers:**
```
- Consumes: order.created
- Publishes: payment.completed, payment.failed
```

**API Endpoints:**
```
GET    /payments/:id           - Get payment details
POST   /payments/:id/refund    - Refund payment (admin)
GET    /health                 - Health check
```

### Service 5: Notification Service (Port 8005)

**Responsibilities:**
- Email notifications
- Event logging

**Kafka Consumers:**
```
- Consumes: order.created, order.confirmed, payment.completed
```

**Email Templates:**
- Welcome email (user registration)
- Order confirmation
- Order shipped
- Order delivered
- Payment receipt

---

## 4. Implementation Guide

### Phase 1: Foundation (Week 1)

#### Day 1-2: Project Setup

```bash
# Create project structure
mkdir ecommerce-platform
cd ecommerce-platform

# Create service directories
mkdir -p gateway user-service product-service order-service payment-service notification-service shared

# Create shared utilities
mkdir -p shared/{auth,database,kafka,logging,config}

# Initialize git
git init
```

**Project Structure:**
```
ecommerce-platform/
├── gateway/
│   ├── main.py
│   ├── routes.py
│   └── middleware.py
├── user-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   ├── api/
│   │   └── database.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── product-service/
│   └── ... (similar structure)
├── order-service/
│   └── ... (similar structure)
├── payment-service/
│   └── ... (similar structure)
├── notification-service/
│   └── ... (similar structure)
├── shared/
│   ├── auth.py
│   ├── database.py
│   ├── kafka_client.py
│   └── logging_config.py
├── docker-compose.yml
├── docker-compose.dev.yml
└── README.md
```

#### Day 3-4: User Service

**Implement:**
1. Database models
2. Pydantic schemas
3. Authentication (JWT)
4. CRUD operations
5. API endpoints
6. Unit tests

#### Day 5-7: Product Service

**Implement:**
1. Database models
2. Schemas
3. CRUD operations
4. Search functionality
5. Caching with Redis
6. Tests

### Phase 2: Core Features (Week 2)

#### Day 1-3: Order Service

**Implement:**
1. Cart management
2. Order creation
3. Order status workflow
4. Kafka producer for events
5. Tests

#### Day 4-5: Payment Service

**Implement:**
1. Kafka consumer setup
2. Payment processing (simulated)
3. Event publishing
4. Tests

#### Day 6-7: Notification Service

**Implement:**
1. Kafka consumer for multiple topics
2. Email service integration
3. Email templates
4. Tests

### Phase 3: Integration (Week 3)

#### Day 1-2: API Gateway

**Implement:**
1. Request routing
2. Authentication middleware
3. Rate limiting
4. CORS configuration
5. Load balancing

#### Day 3-4: Service Integration

**Test:**
1. End-to-end workflows
2. Error scenarios
3. Event-driven flows
4. Integration tests

#### Day 5-7: Monitoring & Observability

**Implement:**
1. Prometheus metrics
2. Distributed tracing (Jaeger)
3. Structured logging
4. Health checks
5. Grafana dashboards

### Phase 4: Production Ready (Week 4)

#### Day 1-2: Docker & Kubernetes

**Create:**
1. Dockerfiles for all services
2. Docker Compose
3. Kubernetes manifests
4. Helm charts (optional)

#### Day 3-4: CI/CD

**Setup:**
1. GitHub Actions / GitLab CI
2. Automated testing
3. Docker image building
4. Deployment pipeline

#### Day 5-7: Documentation & Polish

**Complete:**
1. API documentation (OpenAPI)
2. README with setup instructions
3. Architecture diagrams
4. Deployment guide
5. Final testing

---

## 5. Testing Strategy

### Unit Tests (70% coverage)

```python
# tests/test_user_service.py
def test_create_user():
    user_data = {"email": "test@example.com", "password": "secure123"}
    user = create_user(user_data)
    assert user.email == "test@example.com"

def test_hash_password():
    password = "secure123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
```

### Integration Tests (20% coverage)

```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_order_creation_flow():
    # Create user
    user = await create_test_user()
    
    # Add products to cart
    cart = await add_to_cart(user.id, product_id=1, quantity=2)
    
    # Create order
    order = await create_order(user.id)
    
    assert order.status == "pending"
    assert order.total_amount == 100.00
```

### E2E Tests (10% coverage)

```python
# tests/test_e2e.py
@pytest.mark.e2e
async def test_complete_purchase_flow():
    """Test complete user journey"""
    # 1. Register
    # 2. Login
    # 3. Browse products
    # 4. Add to cart
    # 5. Checkout
    # 6. Payment
    # 7. Receive confirmation
```

---

## 6. Deployment

### Docker Compose (Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f user-service

# Stop all services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Kubernetes (Production)

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployments
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/user-service

# Scale service
kubectl scale deployment user-service --replicas=5
```

---

## 7. Monitoring & Observability

### Metrics to Track

```
Business Metrics:
- User registrations per day
- Orders created per hour
- Revenue per day
- Average order value
- Cart abandonment rate

Technical Metrics:
- Request rate (req/sec)
- Response time (p50, p95, p99)
- Error rate (%)
- Service availability (%)
- Database connection pool usage

Infrastructure Metrics:
- CPU usage
- Memory usage
- Disk I/O
- Network traffic
```

### Alerts to Configure

```
Critical:
- Service down (>1 min)
- Error rate > 5%
- Response time p99 > 1s
- Database connections exhausted

Warning:
- Error rate > 1%
- Response time p99 > 500ms
- High memory usage (>80%)
- Low disk space (<20%)
```

---

## 8. Final Checklist

### Functionality ✅
- [ ] User registration and authentication
- [ ] Product browsing and search
- [ ] Shopping cart
- [ ] Order creation
- [ ] Payment processing
- [ ] Email notifications
- [ ] Admin dashboard

### Code Quality ✅
- [ ] Clean, readable code
- [ ] Proper error handling
- [ ] Input validation
- [ ] Type hints throughout
- [ ] Documentation strings
- [ ] Consistent code style

### Testing ✅
- [ ] Unit tests (>70% coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Load tests
- [ ] All tests passing

### Security ✅
- [ ] Password hashing
- [ ] JWT authentication
- [ ] Input sanitization
- [ ] SQL injection prevention
- [ ] CORS configured
- [ ] Security headers
- [ ] Rate limiting
- [ ] Secrets management

### Performance ✅
- [ ] Database indexing
- [ ] Query optimization
- [ ] Caching strategy
- [ ] Connection pooling
- [ ] Response compression

### Observability ✅
- [ ] Structured logging
- [ ] Metrics collection
- [ ] Distributed tracing
- [ ] Health checks
- [ ] Dashboards

### Deployment ✅
- [ ] Dockerfiles optimized
- [ ] Docker Compose working
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline
- [ ] Deployment documentation

### Documentation ✅
- [ ] README with setup instructions
- [ ] API documentation
- [ ] Architecture diagrams
- [ ] Deployment guide
- [ ] Contribution guidelines

---

## Bonus Features (Optional)

If you finish early, consider adding:

1. **Advanced Features**
   - Product reviews and ratings
   - Wishlist functionality
   - Product recommendations
   - Multi-currency support
   - Promotional codes/discounts

2. **Enhanced Monitoring**
   - Real-time analytics dashboard
   - Customer behavior tracking
   - A/B testing framework

3. **Scalability**
   - Read replicas
   - Caching layers
   - CDN integration
   - Message queue for heavy tasks

4. **Admin Features**
   - Advanced reporting
   - Inventory forecasting
   - Customer analytics
   - Fraud detection

---

## Congratulations! 🎉

By completing this capstone project, you've demonstrated:

✅ **Python Mastery**: From fundamentals to advanced concepts
✅ **FastAPI Expertise**: Building production APIs
✅ **Microservices Architecture**: Designing distributed systems
✅ **Async Programming**: Efficient concurrent operations
✅ **Database Design**: Relational database modeling
✅ **Event-Driven Systems**: Message queues and events
✅ **Testing**: Comprehensive test coverage
✅ **DevOps**: Docker, Kubernetes, CI/CD
✅ **Production Skills**: Monitoring, logging, deployment

### You're Now Ready For:

- 🚀 Backend Engineering roles
- 🤖 Gen AI/ML Engineering (with Python foundation)
- 🏗️ System Architecture positions
- 📊 Data Engineering paths
- 💼 Senior/Lead developer roles

### Next Steps:

1. **Portfolio**: Add this project to your GitHub and resume
2. **Blog**: Write about what you built and learned
3. **Gen AI Path**: Continue to ML/AI development
4. **Job Search**: Apply to backend engineering positions
5. **Keep Learning**: Technology never stops evolving!

---

**You've come from Python noob to production-ready backend pro. Amazing work! 💪🎓**

Continue to the [Gen AI Learning Path](../GEN-AI-PATH.md) if you're ready for AI/ML development!
