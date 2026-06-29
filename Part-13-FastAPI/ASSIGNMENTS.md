# Part 13: FastAPI - Assignments

## Assignment Guidelines

- **Estimated time:** 14-18 hours total
- **Prerequisites:** Parts 1-12 complete
- **Submission:** Runnable FastAPI app with OpenAPI docs, tests using `TestClient`
- **Rules:** Use dependency injection, Pydantic models, proper HTTP status codes

---

## Assignment 1: Task & Project Management API

### Scenario

Build a complete REST API for a task management system (like a lightweight Jira/Trello). Teams, projects, tasks, comments, and labels — with full CRUD, filtering, pagination, and validation.

### Requirements

**Endpoints (minimum):**

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/teams` | Create team |
| GET | `/api/v1/teams` | List teams (paginated) |
| POST | `/api/v1/projects` | Create project under team |
| GET | `/api/v1/projects/{id}` | Get project with tasks |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks` | List with filters: status, assignee, label, due_before |
| PATCH | `/api/v1/tasks/{id}` | Partial update |
| DELETE | `/api/v1/tasks/{id}` | Soft delete |
| POST | `/api/v1/tasks/{id}/comments` | Add comment |
| GET | `/api/v1/health` | Health check |

**FastAPI features to use:**

1. **Path parameters** with validation (`Path(ge=1)`)
2. **Query parameters** — pagination: `skip`, `limit`; filters as optional query params
3. **Request body** — Pydantic `TaskCreate`, `TaskUpdate` with optional fields
4. **Response models** — `TaskResponse`, `TaskListResponse` with metadata
5. **Status codes** — `201` create, `204` delete, `404` not found
6. **Dependency injection:**
   - `get_db()` — yields in-memory or SQLite store
   - `get_current_user()` — mock user from header `X-User-Id`
   - `get_pagination` — returns `PaginationParams` model
7. **Router organization** — `api/v1/endpoints/tasks.py`, `router.py` includes sub-routers
8. **Middleware** — custom logging middleware printing method, path, duration
9. **CORS** — configure for `http://localhost:3000`
10. **Background tasks** — on task creation, `background_tasks.add_task(send_notification, ...)`
11. **Exception handlers** — custom handler for `NotFoundError` → 404 JSON
12. **OpenAPI tags** and descriptions on all endpoints
13. **File upload** — `POST /api/v1/tasks/{id}/attachments` with `UploadFile`
14. **Headers** — `X-Request-ID` returned via middleware

**In-memory or SQLite storage acceptable** — focus on API layer.

### Technical Specifications

- FastAPI routing, request/response handling
- Path, query, body, header, file parameters
- Dependency injection (nested deps)
- Pydantic validation integration
- Middleware, background tasks
- Exception handlers
- APIRouter and versioning
- TestClient tests (10+)

### Acceptance Criteria

- [ ] Swagger UI at `/docs` shows all endpoints with schemas
- [ ] Pagination returns `{items, total, page, per_page, has_next}`
- [ ] Filter `?status=done&assignee=1` works correctly
- [ ] PATCH updates only provided fields
- [ ] 422 returned for invalid body with field errors
- [ ] Background task logged on create (prove with mock/test)
- [ ] Middleware adds `X-Request-ID` header
- [ ] 10+ TestClient tests passing

### Bonus Challenges

- WebSocket `/ws/projects/{id}` for live task updates
- API versioning header `Accept-Version: v1`
- HATEOAS links in responses (`self`, `comments`)

### Hints

- `APIRouter(prefix="/tasks", tags=["tasks"])`
- Pagination dependency: `def pagination(skip: int = 0, limit: int = Query(20, le=100))`
- Soft delete: `is_deleted` flag; filter out in list queries

---

## Assignment 2: Authentication & Authorization API

### Scenario

Extend or build a standalone FastAPI service with JWT authentication, role-based access control, and protected endpoints — patterns used in every production API.

### Requirements

1. **Auth endpoints:**
   - `POST /auth/register` — UserCreate with password validation
   - `POST /auth/login` — returns JWT access + refresh tokens
   - `POST /auth/refresh` — new access token from refresh token
   - `POST /auth/logout` — token blocklist (in-memory set)
   - `GET /auth/me` — current user profile

2. **Security dependencies:**
   - `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")`
   - `get_current_user(token: str = Depends(oauth2_scheme))`
   - `require_role("admin")` — dependency factory returning checker
   - `require_permission("users:write")` — fine-grained RBAC

3. **Protected resources:**
   - `GET /admin/users` — admin only
   - `PUT /users/{id}` — owner or admin
   - `DELETE /users/{id}` — admin only

4. **Password hashing** — `passlib` bcrypt or `hashlib` pbkdf2

5. **JWT payload** — `sub`, `exp`, `roles`, `permissions`

6. **Custom exceptions** — `InvalidCredentials`, `InsufficientPermissions`, `TokenExpired`

7. **Exception handlers** — 401, 403 with consistent `ErrorResponse` schema

8. **Request validation** — email format, password strength via Pydantic

9. **Response models** — never expose `hashed_password`

10. **Rate limiting middleware (simple)** — in-memory dict per IP for `/auth/login`

11. **Cookie variant (optional path)** — `set_cookie` for access token HttpOnly

12. **Tests:**
    - Login success/failure
    - Access without token → 401
    - User accessing admin route → 403
    - Token refresh flow

### Technical Specifications

- OAuth2 password flow
- JWT create/decode
- Dependency injection for auth
- Security scopes concept (optional)
- HTTPException vs custom handlers
- Pydantic User models (Create, Response, InDB)

### Acceptance Criteria

- [ ] Login returns valid JWT decodable with secret
- [ ] Protected endpoint rejects missing/invalid token
- [ ] Admin-only route blocks regular user with 403
- [ ] Owner can update own profile; not others'
- [ ] Refresh token flow works end-to-end
- [ ] Password never in any response body
- [ ] 15+ auth tests passing

### Bonus Challenges

- API key authentication as alternative `Depends(get_api_key)` from header
- OAuth2 scopes with `Security(get_current_user, scopes=["items:read"])`
- Multi-factor stub: TOTP code on login step 2

### Hints

- `from jose import jwt` or `import jwt` (PyJWT)
- Role checker: `def require_role(role): def checker(user=Depends(get_current_user)): ...`
- Token blocklist checked in `get_current_user`

---

## Assignment 3: Content Publishing Platform API

### Scenario

Build a FastAPI application combining advanced routing, WebSockets, streaming, and content negotiation — a blog/CMS backend with real-time features.

### Requirements

1. **Resource routing:**
   - `/articles` CRUD with slug-based lookup `/articles/{slug}`
   - `/authors/{author_id}/articles` nested route
   - `/tags/{tag_name}/articles` filter route

2. **Advanced parameters:**
   - `Header` — `Accept-Language` for content locale
   - `Cookie` — `session_id` for anonymous draft saving
   - `Form` — `POST /articles/{id}/publish` multipart form
   - `File` + `Form` together for article with cover image

3. **Response variety:**
   - `JSONResponse` default
   - `HTMLResponse` for `/articles/{slug}/preview`
   - `StreamingResponse` for `/articles/{id}/export/markdown` — stream chunks
   - `RedirectResponse` for old slug → new slug

4. **Status codes:** `201`, `204`, `301`, `409` (duplicate slug)

5. **WebSocket `/ws/articles/live`** — broadcast new article notifications to subscribers

6. **Lifespan events** (modern FastAPI):
   - Startup: initialize DB connection pool mock
   - Shutdown: close connections, log goodbye

7. **Sub-applications:** mount static files at `/static` via `app.mount`

8. **Custom middleware stack:**
   - Request ID
   - Process time header
   - GZip for responses > 1KB (optional)

9. **Dependency with yield** — DB session with cleanup

10. **OpenAPI customization** — custom description, contact info, servers list

11. **Validation errors** — custom 422 handler with structured `ErrorResponse`

12. **Integration tests** — full article publish flow including file upload

### Technical Specifications

- All Part 13 topics: routing, DI, middleware, websockets, background tasks, lifespan
- Multiple response types
- Form and file handling
- API documentation

### Acceptance Criteria

- [ ] Slug conflict returns 409 with clear message
- [ ] File upload stores metadata linked to article
- [ ] Streaming export returns markdown incrementally (test chunk count)
- [ ] WebSocket clients receive publish event
- [ ] Lifespan startup/shutdown logged
- [ ] `/docs` reflects custom OpenAPI metadata
- [ ] 12+ tests including WebSocket test

### Bonus Challenges

- Content negotiation: same URL returns JSON or XML based on Accept header
- Server-Sent Events endpoint for article feed
- GraphQL mount optional (strawberry) — document as bonus only

### Hints

- StreamingResponse: `async def gen(): yield chunk`
- WebSocket: `await websocket.accept()` then `await manager.broadcast(...)`
- Lifespan: `@asynccontextmanager async def lifespan(app): ... yield ...`
