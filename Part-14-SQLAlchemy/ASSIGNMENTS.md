# Part 14: SQLAlchemy - Assignments

## Assignment Guidelines

- **Estimated time:** 16-20 hours total
- **Prerequisites:** Parts 1-13 complete
- **Submission:** SQLAlchemy project with Alembic migrations, repository layer, and tests
- **Rules:** Use SQLAlchemy 2.x style (`select()`, `session.execute()`); include Alembic migrations

---

## Assignment 1: Blog Platform Database Layer

### Scenario

Design and implement the complete database layer for a multi-author blog with posts, comments, tags, and categories. Focus on relationships, efficient queries, and avoiding the N+1 problem.

### Requirements

**Models:**

1. **`User`** — id, email, username, hashed_password, is_active, created_at
2. **`Post`** — id, title, slug, content, status (draft/published), author_id FK, published_at
3. **`Comment`** — id, post_id, author_id, body, created_at, parent_id (self-referential for threads)
4. **`Tag`** — id, name (unique)
5. **`post_tags`** — association table (many-to-many)
6. **`Category`** — id, name; one-to-many with Post

**Relationships:**

- User → Posts (one-to-many)
- Post → Comments (one-to-many, cascade delete)
- Post ↔ Tags (many-to-many)
- Comment → Comment (self-referential tree)
- Category → Posts

**Repository layer:**

```python
class PostRepository:
    def get_with_comments(self, post_id: int) -> Post | None  # eager load
    def get_published_by_author(self, author_id: int, skip: int, limit: int) -> list[Post]
    def search_by_tag(self, tag_name: str) -> list[Post]
    def get_feed(self, skip: int, limit: int) -> list[Post]  # published, with author+tags
```

**Query requirements:**

- Use `select()` with `join`, `options(selectinload(...))` or `joinedload`
- Aggregate: count posts per author (`func.count`, `group_by`)
- Filter: posts published in last 30 days
- Subquery: authors with more than 5 published posts
- Avoid N+1: prove with SQL echo that feed query uses ≤ 3 queries

**Session management:**

- `get_db()` dependency with yield pattern
- Context manager `with Session(engine) as session:`

**Alembic:**

- Initial migration creating all tables
- Second migration adding `view_count` column to Post

**CRUD scripts:**

- Seed database with 5 users, 20 posts, 50 comments, 10 tags
- CLI: `python -m blog.cli create-post`, `list-posts`, `add-comment`

### Technical Specifications

- SQLAlchemy 2.x ORM declarative models
- Relationships: one-to-many, many-to-many, self-referential
- Sessions, transactions, commit/rollback
- select(), where(), join(), eager loading
- Repository pattern
- Alembic migrations
- Indexes on slug, email, published_at

### Acceptance Criteria

- [ ] All relationships navigable in Python (`post.author`, `post.tags`, `comment.replies`)
- [ ] Cascade delete removes comments when post deleted
- [ ] `get_feed` loads author and tags without N+1 (SQL log evidence in README)
- [ ] Search by tag returns correct posts
- [ ] Self-referential comments support 3-level threading
- [ ] Both Alembic migrations apply cleanly on empty DB
- [ ] 15+ tests with in-memory SQLite

### Bonus Challenges

- Soft delete mixin (`deleted_at` column) with filtered queries
- Full-text search on title/content (SQLite FTS or ILIKE)
- Async SQLAlchemy version with `AsyncSession`

### Hints

- Association table: `Table('post_tags', Base.metadata, Column('post_id', FK), Column('tag_id', FK))`
- Eager load: `options(selectinload(Post.comments), joinedload(Post.author))`
- Self-ref: `parent_id = mapped_column(ForeignKey('comments.id'))`, `replies = relationship(back_populates='parent')`

---

## Assignment 2: E-Commerce Database Schema

### Scenario

Build a production-grade e-commerce schema: products, inventory, orders, payments, and addresses — with complex relationships and transactional order placement.

### Requirements

**Models:**

- `Customer`, `Address` (one-to-many from customer)
- `Product`, `ProductCategory` (self-referential tree), `ProductImage`
- `Inventory` (product_id, warehouse_id, quantity) — composite uniqueness
- `Warehouse`
- `Order`, `OrderItem` (snapshot price at purchase time)
- `Payment` (one-to-one with Order)
- `ProductTag`, `product_tag_link` (many-to-many)
- `Cart`, `CartItem` (optional)

**Business operations (service functions using session):**

1. **`place_order(customer_id, cart_items) -> Order`**
   - Transaction: check inventory → decrement stock → create order + items → create payment pending
   - Rollback entire transaction if insufficient stock

2. **`calculate_order_total(order_id) -> Decimal`** — sum of line items; never recalculate from current product price

3. **`get_products_by_category(category_id, include_subcategories=True)`** — recursive CTE or tree walk

4. **`get_low_stock_products(threshold=10)`** — join Inventory, filter, order by quantity

5. **`apply_discount(order_id, percent)`** — update order within transaction

**Advanced queries:**

- Top 10 products by revenue (join OrderItem, aggregate)
- Customers with no orders (outer join, filter null)
- Products never ordered (subquery / NOT IN / NOT EXISTS)

**Alembic:** 3 migrations — initial, add index on order status, add audit columns

**SQLAlchemy 2.x:**

- Use `mapped_column`, `Mapped[]` type annotations
- `session.scalars(select(Product).where(...)).all()`

### Technical Specifications

- Complex relationships and constraints
- Transactions and isolation (demonstrate rollback)
- Aggregations and subqueries
- Repository + service layer separation
- Indexes and unique constraints
- SQLAlchemy 2.x typed models

### Acceptance Criteria

- [ ] `place_order` atomically fails when stock insufficient (no partial order)
- [ ] OrderItem stores price snapshot different from current Product.price after price change
- [ ] Category tree query returns products in child categories
- [ ] Top revenue query matches manual calculation on seed data
- [ ] 3 migrations apply in order
- [ ] 20+ tests including transaction failure case

### Bonus Challenges

- Optimistic locking with `version_id` column on Product/Inventory
- Read-only `session.execute(text("SELECT ..."))` for reporting
- Partitioning strategy documented for Orders by date

### Hints

- Snapshot price: `OrderItem.unit_price = product.price` at order time
- Stock check in same transaction before commit
- Recursive category: `cte = select(Category).where(...).cte(recursive=True)`

---

## Assignment 3: User Management with RBAC & Audit Trail

### Scenario

Implement an enterprise user management database with roles, permissions, soft deletes, and full audit logging — patterns common in admin systems.

### Requirements

**Models:**

- `User` — soft delete (`deleted_at`), `created_at`, `updated_at`
- `Role`, `Permission`
- `user_roles` (many-to-many), `role_permissions` (many-to-many)
- `AuditLog` — user_id, action, table_name, record_id, old_values JSON, new_values JSON, timestamp

**Features:**

1. **Soft delete users** — `session.execute(update(User).where(...).values(deleted_at=func.now()))`; default queries exclude deleted

2. **`user_has_permission(user_id, permission_name) -> bool`** — join through roles

3. **Audit listener** — SQLAlchemy event `after_insert`, `after_update`, `after_delete` on User model writes AuditLog

4. **Bulk operations** — `session.execute(insert(Role), list_of_dicts)` for seeding

5. **Pagination** — keyset pagination on User.id for large datasets

6. **Hybrid property** — `User.is_deleted` based on `deleted_at`

7. **Query users by role** with eager load roles and permissions in one query

8. **Restore soft-deleted user** — clear `deleted_at`

9. **Unique constraint** — email active only among non-deleted (partial unique index if SQLite 3.37+ or document limitation)

10. **Migration** — Alembic autogenerate from models; manual edit for indexes

**CLI admin tool:**

- `assign-role user@email.com admin`
- `audit-log --user-id 5`
- `list-users --role editor --include-deleted`

### Technical Specifications

- Many-to-many twice (users-roles, roles-permissions)
- Soft delete pattern
- SQLAlchemy events for audit
- Timestamps (server_default=func.now())
- JSON column for audit old/new values
- Session flush/commit patterns

### Acceptance Criteria

- [ ] Permission check returns True/False correctly for role setup
- [ ] Soft deleted user excluded from `list_users()` but present with `include_deleted=True`
- [ ] Audit log entry created on user update with old and new email
- [ ] Bulk role seed inserts 5 roles in one statement
- [ ] Restore user makes them visible again
- [ ] Eager load fetches user+roles+permissions in ≤ 2 queries
- [ ] 15+ tests

### Bonus Challenges

- Row-level security simulation in service layer
- `history` table using SQLAlchemy-Continuum or manual version table
- Read replica routing documented (conceptual)

### Hints

- Soft delete filter: `.where(User.deleted_at.is_(None))`
- Events: `@event.listens_for(User, 'after_update')`
- JSON: `mapped_column(JSON)` for audit values as dict
