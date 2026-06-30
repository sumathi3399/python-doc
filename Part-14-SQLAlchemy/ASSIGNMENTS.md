# Part 14: SQLAlchemy - Practice Problems

> Test ORM, relationships, queries

---

## Problem 1: Define Model

**Task**: Create User model
```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)

# Create tables
engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
```

**Time**: 15 minutes

---

## Problem 2: Create Session

**Task**: Add and commit user
```python
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

user = User(name="Alice", email="alice@example.com")
session.add(user)
session.commit()
```

**Time**: 10 minutes

---

## Problem 3: Query Records

**Task**: SELECT queries
```python
# Get all users
users = session.query(User).all()

# Get one user
user = session.query(User).filter(User.name == "Alice").first()

# Count
count = session.query(User).count()
```

**Time**: 15 minutes

---

## Problem 4: Update Record

**Task**: Modify existing user
```python
user = session.query(User).filter(User.name == "Alice").first()
user.email = "newemail@example.com"
session.commit()
```

**Time**: 10 minutes

---

## Problem 5: Delete Record

**Task**: Remove user
```python
user = session.query(User).filter(User.name == "Alice").first()
session.delete(user)
session.commit()
```

**Time**: 10 minutes

---

## Problem 6: One-to-Many Relationship

**Task**: User has many posts
```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="posts")
```

**Time**: 20 minutes

---

## Problem 7: Filtering and Ordering

**Task**: Complex queries
```python
# Filter and order
users = session.query(User).filter(User.name.like("%Ali%")).order_by(User.id.desc()).all()

# Multiple filters
users = session.query(User).filter(User.id > 5).filter(User.name != "Admin").all()
```

**Time**: 15 minutes

---

## Problem 8: Join Query

**Task**: Get users with posts
```python
from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.posts)).all()
```

**Time**: 15 minutes

---

## Problem 9: Aggregation

**Task**: Count posts per user
```python
from sqlalchemy import func

results = session.query(
    User.name,
    func.count(Post.id).label('post_count')
).join(Post).group_by(User.name).all()
```

**Time**: 20 minutes

---

## Problem 10: Transaction Rollback

**Task**: Rollback on error
```python
try:
    user = User(name="Bob", email="bob@example.com")
    session.add(user)
    # Something goes wrong
    raise Exception("Error!")
    session.commit()
except:
    session.rollback()
```

**Time**: 10 minutes

---

## Summary Check

**8+ solved** → SQLAlchemy ready  
**5-7 solved** → Practice relationships  
**< 5 solved** → Review ORM basics
