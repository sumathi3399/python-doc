# Part 14: SQLAlchemy

> Master SQLAlchemy - the most popular Python SQL toolkit and Object-Relational Mapping (ORM) library.

## 📚 Table of Contents

1. [SQLAlchemy Core vs ORM](#1-sqlalchemy-core-vs-orm)
2. [Database Setup](#2-database-setup)
3. [ORM Basics](#3-orm-basics)
4. [Sessions](#4-sessions)
5. [CRUD Operations](#5-crud-operations)
6. [Relationships](#6-relationships)
7. [Querying](#7-querying)
8. [Advanced Features](#8-advanced-features)
9. [SQLAlchemy 2.x](#9-sqlalchemy-2x)
10. [Exercises](#exercises)

---

## 1. SQLAlchemy Core vs ORM

### Understanding the Layers

```python
"""
SQLAlchemy Architecture:

┌─────────────────────────────────────┐
│         ORM Layer (High-level)      │
│  - Work with Python objects         │
│  - Automatic relationship handling  │
│  - Session management               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Core Layer (Mid-level)      │
│  - SQL Expression Language          │
│  - Table & Column objects           │
│  - Direct SQL construction          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Engine (Low-level)          │
│  - Connection pooling               │
│  - Dialect management               │
│  - Transaction handling             │
└─────────────────────────────────────┘
"""
```

### When to Use Which

```python
# Core - For complex queries, performance-critical operations
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

engine = create_engine('sqlite:///example.db')
metadata = MetaData()

users_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('email', String)
)

# Execute raw SQL
with engine.connect() as conn:
    result = conn.execute(users_table.select())
    for row in result:
        print(row)

# ORM - For most application development
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

# Work with objects
with Session(engine) as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()

"""
Use Core when:
- Building query builders
- Performance is critical
- Need fine-grained SQL control
- Working with dynamic queries

Use ORM when:
- Building applications
- Need relationships
- Want Python-like interface
- Standard CRUD operations
"""
```

---

## 2. Database Setup

### Engine Creation

```python
from sqlalchemy import create_engine

# SQLite (file-based)
engine = create_engine('sqlite:///mydb.db', echo=True)

# SQLite (in-memory)
engine = create_engine('sqlite:///:memory:')

# PostgreSQL
engine = create_engine('postgresql://user:password@localhost:5432/mydb')

# MySQL
engine = create_engine('mysql+pymysql://user:password@localhost:3306/mydb')

# With connection pool settings
engine = create_engine(
    'postgresql://user:password@localhost/mydb',
    pool_size=10,          # Number of connections to maintain
    max_overflow=20,       # Max connections above pool_size
    pool_timeout=30,       # Seconds to wait before timeout
    pool_recycle=3600,     # Recycle connections after 1 hour
    echo=True              # Log SQL statements
)
```

### Connection Management

```python
from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///mydb.db')

# Method 1: Context manager (recommended)
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
    for row in result:
        print(row)

# Method 2: Explicit connection
conn = engine.connect()
try:
    result = conn.execute(text("SELECT * FROM users"))
finally:
    conn.close()

# Method 3: With transaction
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users (name) VALUES ('Alice')"))
    # Auto-commits at end, rollback on exception
```

### Database URLs

```python
"""
Database URL Format:
dialect+driver://username:password@host:port/database

Common patterns:
"""

# SQLite
'sqlite:///relative/path/to/database.db'
'sqlite:////absolute/path/to/database.db'
'sqlite:///:memory:'

# PostgreSQL
'postgresql://scott:tiger@localhost/mydatabase'
'postgresql+psycopg2://scott:tiger@localhost/mydatabase'
'postgresql+pg8000://scott:tiger@localhost/mydatabase'

# MySQL
'mysql://scott:tiger@localhost/mydatabase'
'mysql+pymysql://scott:tiger@localhost/mydatabase'
'mysql+mysqlconnector://scott:tiger@localhost/mydatabase'

# Microsoft SQL Server
'mssql+pyodbc://scott:tiger@localhost/mydatabase'
'mssql+pymssql://scott:tiger@localhost/mydatabase'

# With special characters in password
from urllib.parse import quote_plus
password = 'p@ssw0rd!#'
encoded_password = quote_plus(password)
url = f'postgresql://user:{encoded_password}@localhost/mydb'
```

---

## 3. ORM Basics

### Declarative Base

```python
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

# Create base class
Base = declarative_base()

# Define model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

# Create all tables
from sqlalchemy import create_engine

engine = create_engine('sqlite:///mydb.db')
Base.metadata.create_all(engine)
```

### Model Definition

```python
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # String columns
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sku = Column(String(50), unique=True, index=True)
    
    # Numeric columns
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    
    # Boolean
    active = Column(Boolean, default=True)
    
    # DateTime
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
```

### Column Types

```python
from sqlalchemy import (
    Integer, SmallInteger, BigInteger,
    String, Text, Unicode,
    Float, Numeric,
    Boolean,
    Date, DateTime, Time, Interval,
    LargeBinary,
    Enum,
    JSON
)
from enum import Enum as PyEnum

class Status(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class User(Base):
    __tablename__ = 'users'
    
    # Integer types
    id = Column(BigInteger, primary_key=True)
    age = Column(SmallInteger)
    
    # String types
    username = Column(String(50))  # VARCHAR(50)
    bio = Column(Text)             # TEXT (unlimited)
    unicode_name = Column(Unicode(100))
    
    # Numeric types
    height = Column(Float)
    salary = Column(Numeric(10, 2))  # DECIMAL(10,2)
    
    # Boolean
    is_active = Column(Boolean, default=True)
    
    # Date/Time
    birth_date = Column(Date)
    created_at = Column(DateTime)
    login_time = Column(Time)
    
    # Binary
    profile_picture = Column(LargeBinary)
    
    # Enum
    status = Column(Enum(Status))
    
    # JSON
    preferences = Column(JSON)
```

### Constraints

```python
from sqlalchemy import (
    Column, Integer, String, Float,
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    # Table-level constraints
    __table_args__ = (
        # Check constraint
        CheckConstraint('price > 0', name='positive_price'),
        CheckConstraint('quantity >= 0', name='non_negative_quantity'),
        
        # Unique constraint on multiple columns
        UniqueConstraint('name', 'category_id', name='unique_product_per_category'),
        
        # Index
        Index('idx_product_name', 'name'),
        Index('idx_product_price', 'price'),
        Index('idx_composite', 'name', 'category_id'),
    )
```

---

## 4. Sessions

### Session Management

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine('sqlite:///mydb.db')

# Create session factory
SessionLocal = sessionmaker(bind=engine)

# Method 1: Context manager (recommended)
with SessionLocal() as session:
    user = User(name="Alice")
    session.add(user)
    session.commit()
# Session automatically closed

# Method 2: Try-finally pattern
session = SessionLocal()
try:
    user = User(name="Bob")
    session.add(user)
    session.commit()
finally:
    session.close()

# Method 3: Dependency injection (FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Depends

@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Session Lifecycle

```python
from sqlalchemy.orm import Session

session = Session(engine)

# 1. Clean state (empty)
print(session.new)  # Set()
print(session.dirty)  # Set()

# 2. Add object
user = User(name="Alice")
session.add(user)
print(session.new)  # {User instance}

# 3. Commit
session.commit()
print(session.new)  # Set() (empty now)

# 4. Modify object
user.name = "Alice Smith"
print(session.dirty)  # {User instance}

# 5. Commit changes
session.commit()
print(session.dirty)  # Set() (empty now)

# 6. Close session
session.close()
```

### Transactions

```python
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

session = Session(engine)

# Basic transaction
try:
    user1 = User(name="Alice")
    user2 = User(name="Bob")
    
    session.add(user1)
    session.add(user2)
    session.commit()  # Commits both or neither
except Exception:
    session.rollback()  # Rollback on error
    raise
finally:
    session.close()

# Nested transactions (savepoints)
session.begin()
try:
    user = User(name="Alice")
    session.add(user)
    
    # Nested transaction
    session.begin_nested()
    try:
        # This might fail
        duplicate_user = User(name="Alice")  # Assuming unique constraint
        session.add(duplicate_user)
        session.commit()  # Commit savepoint
    except IntegrityError:
        session.rollback()  # Rollback to savepoint
        print("Duplicate user, continuing...")
    
    session.commit()  # Commit outer transaction
except Exception:
    session.rollback()
    raise
```

### Commit and Rollback

```python
from sqlalchemy.orm import Session

session = Session(engine)

# Commit - persist changes
user = User(name="Alice")
session.add(user)
print(user.id)  # None (not yet in DB)

session.commit()
print(user.id)  # 1 (assigned after commit)

# Rollback - discard changes
user.name = "Bob"
print(user.name)  # "Bob"

session.rollback()
print(user.name)  # "Alice" (reverted)

# Auto-rollback on exception
try:
    user = User(name="Charlie")
    session.add(user)
    raise ValueError("Something went wrong")
    session.commit()  # Never reached
except ValueError:
    session.rollback()  # Changes discarded

# Flush - write to DB without committing
user = User(name="Dave")
session.add(user)
session.flush()  # Writes to DB, assigns ID
print(user.id)  # 2 (has ID now)

# But not committed yet, can still rollback
session.rollback()
```

---

## 5. CRUD Operations

### Creating Records

```python
from sqlalchemy.orm import Session

session = Session(engine)

# Create single record
user = User(name="Alice", email="alice@example.com")
session.add(user)
session.commit()

print(user.id)  # Auto-generated ID

# Create multiple records
users = [
    User(name="Bob", email="bob@example.com"),
    User(name="Charlie", email="charlie@example.com"),
    User(name="Dave", email="dave@example.com")
]
session.add_all(users)
session.commit()

# Create with relationships
post = Post(
    title="My Post",
    content="Post content",
    author=user  # Set relationship
)
session.add(post)
session.commit()

# Bulk insert (faster, no ORM features)
session.bulk_insert_mappings(
    User,
    [
        {"name": "User1", "email": "user1@example.com"},
        {"name": "User2", "email": "user2@example.com"},
    ]
)
session.commit()
```

### Reading/Querying

```python
from sqlalchemy.orm import Session

session = Session(engine)

# Get all records
users = session.query(User).all()

# Get first record
user = session.query(User).first()

# Get by primary key
user = session.query(User).get(1)  # v1.x
user = session.get(User, 1)  # v2.x

# Filter
users = session.query(User).filter(User.name == "Alice").all()
users = session.query(User).filter_by(name="Alice").all()

# Multiple filters
users = session.query(User).filter(
    User.name == "Alice",
    User.age > 18
).all()

# OR condition
from sqlalchemy import or_

users = session.query(User).filter(
    or_(User.name == "Alice", User.name == "Bob")
).all()

# IN clause
users = session.query(User).filter(
    User.name.in_(["Alice", "Bob", "Charlie"])
).all()

# LIKE
users = session.query(User).filter(User.name.like("%alice%")).all()

# Count
count = session.query(User).count()

# Exists
exists = session.query(User).filter(User.name == "Alice").exists()
result = session.query(exists).scalar()

# One result (raises if not found or multiple found)
user = session.query(User).filter_by(email="alice@example.com").one()

# One or None
user = session.query(User).filter_by(email="alice@example.com").one_or_none()
```

### Updating Records

```python
from sqlalchemy.orm import Session

session = Session(engine)

# Update single record
user = session.query(User).filter_by(name="Alice").first()
user.email = "newemail@example.com"
session.commit()

# Update multiple records
session.query(User).filter(User.age < 18).update({"active": False})
session.commit()

# Update with expression
session.query(Product).filter(Product.id == 1).update({
    "price": Product.price * 1.1  # 10% increase
})
session.commit()

# Bulk update (faster, no ORM features)
session.bulk_update_mappings(
    User,
    [
        {"id": 1, "email": "user1@example.com"},
        {"id": 2, "email": "user2@example.com"},
    ]
)
session.commit()
```

### Deleting Records

```python
from sqlalchemy.orm import Session

session = Session(engine)

# Delete single record
user = session.query(User).filter_by(name="Alice").first()
session.delete(user)
session.commit()

# Delete multiple records
session.query(User).filter(User.active == False).delete()
session.commit()

# Delete all records
session.query(User).delete()
session.commit()

# Soft delete (recommended)
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    deleted_at = Column(DateTime, nullable=True)
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None

# Soft delete
user.deleted_at = datetime.utcnow()
session.commit()

# Query only non-deleted
active_users = session.query(User).filter(User.deleted_at == None).all()
```

---

## 6. Relationships

### One-to-One

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # One-to-One relationship
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True)
    bio = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    
    # Back reference
    user = relationship("User", back_populates="profile")

# Usage
user = User(name="Alice")
profile = Profile(bio="Software developer")
user.profile = profile

session.add(user)
session.commit()

# Access
print(user.profile.bio)  # "Software developer"
print(profile.user.name)  # "Alice"
```

### One-to-Many

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # One-to-Many relationship
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey('users.id'))
    
    # Many-to-One relationship
    author = relationship("User", back_populates="posts")

# Usage
user = User(name="Alice")
post1 = Post(title="First Post", content="Content 1")
post2 = Post(title="Second Post", content="Content 2")

user.posts.append(post1)
user.posts.append(post2)

session.add(user)
session.commit()

# Access
print(user.posts)  # [<Post>, <Post>]
print(post1.author.name)  # "Alice"
```

### Many-to-Many

```python
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

# Association table
student_course = Table(
    'student_course',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # Many-to-Many relationship
    courses = relationship(
        "Course",
        secondary=student_course,
        back_populates="students"
    )

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # Many-to-Many relationship
    students = relationship(
        "Student",
        secondary=student_course,
        back_populates="courses"
    )

# Usage
student = Student(name="Alice")
course1 = Course(name="Python 101")
course2 = Course(name="Web Development")

student.courses.append(course1)
student.courses.append(course2)

session.add(student)
session.commit()

# Access
print(student.courses)  # [<Course>, <Course>]
print(course1.students)  # [<Student>]
```

### Relationship Loading

```python
from sqlalchemy.orm import relationship, joinedload, selectinload, subqueryload

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # Lazy loading (default) - Load when accessed
    posts = relationship("Post", lazy='select')
    
    # Joined loading - Load with JOIN
    comments = relationship("Comment", lazy='joined')
    
    # Subquery loading - Load with subquery
    likes = relationship("Like", lazy='subquery')
    
    # Select-in loading - Load with IN clause
    followers = relationship("Follow", lazy='selectin')
    
    # No loading - Never load automatically
    notifications = relationship("Notification", lazy='noload')
    
    # Dynamic loading - Return query object
    messages = relationship("Message", lazy='dynamic')

# Usage

# Lazy (N+1 problem)
users = session.query(User).all()
for user in users:
    print(user.posts)  # Separate query for each user

# Joined load (single query with JOIN)
users = session.query(User).options(joinedload(User.posts)).all()
# SELECT users.*, posts.* FROM users LEFT JOIN posts ...

# Selectin load (two queries)
users = session.query(User).options(selectinload(User.posts)).all()
# SELECT * FROM users
# SELECT * FROM posts WHERE author_id IN (...)

# Subquery load (two queries with subquery)
users = session.query(User).options(subqueryload(User.posts)).all()

# Dynamic relationship returns query
user = session.query(User).first()
recent_messages = user.messages.filter(
    Message.created_at > datetime.now() - timedelta(days=7)
).all()
```

---

## 7. Querying

### Filter, filter_by

```python
from sqlalchemy.orm import Session

session = Session(engine)

# filter() - Use column expressions
users = session.query(User).filter(User.name == "Alice").all()
users = session.query(User).filter(User.age > 18).all()
users = session.query(User).filter(User.email.like("%@gmail.com")).all()

# filter_by() - Use keyword arguments
users = session.query(User).filter_by(name="Alice").all()
users = session.query(User).filter_by(name="Alice", age=30).all()

# Multiple filters (AND)
users = session.query(User).filter(
    User.name == "Alice",
    User.age > 18
).all()

# OR condition
from sqlalchemy import or_

users = session.query(User).filter(
    or_(
        User.name == "Alice",
        User.name == "Bob"
    )
).all()

# NOT condition
from sqlalchemy import not_

users = session.query(User).filter(
    not_(User.name == "Alice")
).all()

# IN clause
users = session.query(User).filter(
    User.name.in_(["Alice", "Bob", "Charlie"])
).all()

# BETWEEN
users = session.query(User).filter(
    User.age.between(18, 30)
).all()

# NULL check
users = session.query(User).filter(User.email == None).all()
users = session.query(User).filter(User.email != None).all()
users = session.query(User).filter(User.email.is_(None)).all()
users = session.query(User).filter(User.email.isnot(None)).all()
```

### Order by, Group by

```python
from sqlalchemy import func, desc

session = Session(engine)

# Order by
users = session.query(User).order_by(User.name).all()
users = session.query(User).order_by(desc(User.created_at)).all()
users = session.query(User).order_by(User.name, desc(User.age)).all()

# Group by
counts = session.query(
    User.city,
    func.count(User.id)
).group_by(User.city).all()

# Having
counts = session.query(
    User.city,
    func.count(User.id).label('user_count')
).group_by(User.city).having(func.count(User.id) > 10).all()

# Limit and offset
users = session.query(User).limit(10).all()
users = session.query(User).offset(20).limit(10).all()

# Distinct
cities = session.query(User.city).distinct().all()
```

### Joins

```python
from sqlalchemy.orm import Session

session = Session(engine)

# Inner join
results = session.query(User, Post).join(Post).all()

# Explicit join condition
results = session.query(User, Post).join(
    Post, User.id == Post.author_id
).all()

# Left outer join
results = session.query(User).outerjoin(Post).all()

# Multiple joins
results = session.query(User).join(Post).join(Comment).all()

# Join with filter
results = session.query(User).join(Post).filter(
    Post.title.like("%Python%")
).all()

# Access joined data
for user, post in session.query(User, Post).join(Post).all():
    print(f"{user.name}: {post.title}")
```

### Subqueries

```python
from sqlalchemy import func
from sqlalchemy.orm import aliased

session = Session(engine)

# Scalar subquery
subq = session.query(
    func.count(Post.id)
).filter(Post.author_id == User.id).correlate(User).scalar_subquery()

users_with_post_count = session.query(
    User.name,
    subq.label('post_count')
).all()

# Subquery as table
subq = session.query(
    Post.author_id,
    func.count(Post.id).label('post_count')
).group_by(Post.author_id).subquery()

results = session.query(
    User.name,
    subq.c.post_count
).outerjoin(subq, User.id == subq.c.author_id).all()

# EXISTS
from sqlalchemy import exists

has_posts = session.query(
    exists().where(Post.author_id == User.id)
).correlate(User)

users_with_posts = session.query(User).filter(has_posts).all()
```

### Aggregations

```python
from sqlalchemy import func

session = Session(engine)

# Count
user_count = session.query(func.count(User.id)).scalar()
user_count = session.query(User).count()

# Sum
total_price = session.query(func.sum(Order.total)).scalar()

# Average
avg_age = session.query(func.avg(User.age)).scalar()

# Min/Max
min_price = session.query(func.min(Product.price)).scalar()
max_price = session.query(func.max(Product.price)).scalar()

# Multiple aggregations
stats = session.query(
    func.count(User.id).label('total_users'),
    func.avg(User.age).label('avg_age'),
    func.min(User.age).label('min_age'),
    func.max(User.age).label('max_age')
).first()

# Group by with aggregation
city_stats = session.query(
    User.city,
    func.count(User.id).label('user_count'),
    func.avg(User.age).label('avg_age')
).group_by(User.city).all()
```

---

## 8. Advanced Features

### Migrations with Alembic

```python
# Install: pip install alembic

# Initialize Alembic
# alembic init alembic

# alembic/env.py
from myapp.models import Base
target_metadata = Base.metadata

# alembic.ini
sqlalchemy.url = postgresql://user:pass@localhost/mydb

# Create migration
# alembic revision --autogenerate -m "Create users table"

# Generated migration file:
"""
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('users')
"""

# Apply migrations
# alembic upgrade head

# Rollback
# alembic downgrade -1

# Show current version
# alembic current

# Show history
# alembic history
```

### Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, NullPool, StaticPool

# Default connection pool
engine = create_engine(
    'postgresql://user:pass@localhost/mydb',
    poolclass=QueuePool,
    pool_size=5,          # Normal pool size
    max_overflow=10,      # Max extra connections
    pool_timeout=30,      # Wait 30s for connection
    pool_recycle=3600,    # Recycle after 1 hour
    pool_pre_ping=True    # Test connections before using
)

# No connection pool (new connection each time)
engine = create_engine(
    'sqlite:///mydb.db',
    poolclass=NullPool
)

# Static pool (for single-threaded, like SQLite)
engine = create_engine(
    'sqlite:///:memory:',
    poolclass=StaticPool
)

# Monitor pool status
engine.pool.status()
```

### Query Optimization

```python
from sqlalchemy.orm import Session, joinedload, selectinload

session = Session(engine)

# ❌ BAD: N+1 query problem
users = session.query(User).all()
for user in users:
    print(user.posts)  # Separate query for each user!

# ✅ GOOD: Eager loading
users = session.query(User).options(
    joinedload(User.posts)
).all()

# ✅ GOOD: Select-in loading (better for collections)
users = session.query(User).options(
    selectinload(User.posts)
).all()

# ✅ GOOD: Load only needed columns
results = session.query(User.id, User.name).all()

# ✅ GOOD: Use exists() instead of count()
# Bad
if session.query(User).filter_by(email=email).count() > 0:
    pass

# Good
from sqlalchemy import exists
if session.query(exists().where(User.email == email)).scalar():
    pass

# ✅ GOOD: Bulk operations
session.bulk_insert_mappings(User, [{"name": "User1"}, {"name": "User2"}])

# ✅ GOOD: Use indexes
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, index=True)  # Indexed
    name = Column(String)
    
    __table_args__ = (
        Index('idx_name_email', 'name', 'email'),  # Composite index
    )
```

### N+1 Problem

```python
from sqlalchemy.orm import Session, joinedload, selectinload

# ❌ N+1 Problem Example
users = session.query(User).all()  # 1 query
for user in users:
    print(user.posts)  # N queries (one per user)
# Total: N+1 queries

# ✅ Solution 1: joinedload (one query with JOIN)
users = session.query(User).options(
    joinedload(User.posts)
).all()
# Total: 1 query

# ✅ Solution 2: selectinload (two queries, better for large collections)
users = session.query(User).options(
    selectinload(User.posts)
).all()
# Total: 2 queries (users, then all posts)

# ✅ Solution 3: subqueryload
users = session.query(User).options(
    subqueryload(User.posts)
).all()

# Nested relationships
users = session.query(User).options(
    selectinload(User.posts).selectinload(Post.comments)
).all()
```

---

## 9. SQLAlchemy 2.x

### New Query Syntax

```python
# SQLAlchemy 1.x (deprecated)
from sqlalchemy.orm import Session

session = Session(engine)
users = session.query(User).filter(User.name == "Alice").all()

# SQLAlchemy 2.x (recommended)
from sqlalchemy import select

stmt = select(User).where(User.name == "Alice")
users = session.execute(stmt).scalars().all()

# Or with session.scalars()
users = session.scalars(select(User).where(User.name == "Alice")).all()

# Multiple columns
stmt = select(User.id, User.name).where(User.age > 18)
results = session.execute(stmt).all()

# Join
stmt = select(User, Post).join(Post).where(Post.title.like("%Python%"))
results = session.execute(stmt).all()

# Count
from sqlalchemy import func

stmt = select(func.count(User.id))
count = session.execute(stmt).scalar()
```

### Async Support

```python
# Install: pip install sqlalchemy[asyncio] aiosqlite

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

# Create async engine
engine = create_async_engine(
    "sqlite+aiosqlite:///./test.db",
    echo=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Use async session
async def get_users():
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.age > 18)
        result = await session.execute(stmt)
        users = result.scalars().all()
        return users

# Create tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CRUD operations
async def create_user(name: str, email: str):
    async with AsyncSessionLocal() as session:
        user = User(name=name, email=email)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

# FastAPI integration
from fastapi import FastAPI, Depends

app = FastAPI()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users/")
async def read_users(db: AsyncSession = Depends(get_db)):
    stmt = select(User)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Migration Guide

```python
"""
SQLAlchemy 1.x → 2.x Migration

1. Update query syntax
"""
# Old
users = session.query(User).filter(User.name == "Alice").all()

# New
from sqlalchemy import select
stmt = select(User).where(User.name == "Alice")
users = session.scalars(stmt).all()

"""
2. Update session creation
"""
# Old
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# New (same, but async option available)
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

"""
3. Update relationship loading
"""
# Old & New (no change)
from sqlalchemy.orm import joinedload
users = session.query(User).options(joinedload(User.posts)).all()

"""
4. Use select() for queries
"""
# Old
session.query(User).filter_by(name="Alice").first()

# New
from sqlalchemy import select
stmt = select(User).where(User.name == "Alice")
session.scalars(stmt).first()

"""
5. Async support (new feature)
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("sqlite+aiosqlite:///./test.db")

async def get_users():
    async with AsyncSession(engine) as session:
        stmt = select(User)
        result = await session.execute(stmt)
        return result.scalars().all()
```

---

## Exercises

### Exercise 1: Blog System
Create a blog system with posts and comments.

**Requirements:**
- User model with posts relationship
- Post model with comments
- Comment model
- CRUD operations
- Query posts by author
- Get post with comments (avoid N+1)

```python
# Your solution here
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()

# Implement models and operations
```

### Exercise 2: E-commerce Database
Build an e-commerce database schema.

**Requirements:**
- Products with categories
- Orders with order items
- Users with addresses
- Many-to-many: products and tags
- Calculate order total
- Query products by category

```python
# Your solution here

# Implement e-commerce schema
```

### Exercise 3: User Management System
Create a user management system with roles.

**Requirements:**
- User model with roles (many-to-many)
- Role model with permissions
- Query users by role
- Check user permissions
- Soft delete users
- Audit trail (created_at, updated_at)

```python
# Your solution here

# Implement user management system
```

---

## Summary

### Key Concepts

1. **SQLAlchemy Basics**
   - ORM vs Core
   - Engine and sessions
   - Models and columns

2. **CRUD Operations**
   - Create, read, update, delete
   - Querying with filters
   - Joins and aggregations

3. **Relationships**
   - One-to-One, One-to-Many, Many-to-Many
   - Lazy vs eager loading
   - Avoiding N+1 problem

4. **Advanced Features**
   - Migrations with Alembic
   - Connection pooling
   - Query optimization
   - SQLAlchemy 2.x features

### Best Practices

✅ **DO:**
- Use context managers for sessions
- Define relationships properly
- Use eager loading to avoid N+1
- Add indexes for frequently queried columns
- Use Alembic for migrations
- Handle transactions properly
- Use SQLAlchemy 2.x syntax

❌ **DON'T:**
- Leave sessions open
- Use lazy loading in loops
- Forget to commit changes
- Skip migrations
- Ignore N+1 problems
- Hardcode connection strings
- Use deprecated 1.x query API

### Next Steps

Now that you understand SQLAlchemy, you're ready to:
- Add caching with **Redis** (Part 15)
- Build production-grade **FastAPI projects** (Part 16)
- Integrate everything into microservices

---

**Continue to [Part 15: Redis Integration](../Part-15-Redis-Integration/README.md)** →
