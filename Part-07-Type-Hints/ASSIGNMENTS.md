# Part 7: Type Hints & Annotations - Assignments

## Assignment Guidelines

- **Estimated time:** 10-14 hours total
- **Prerequisites:** Parts 1-6 complete
- **Submission:** Fully typed Python package that passes `mypy --strict` (document any intentional `# type: ignore` with justification)
- **Rules:** Type hints on all public functions, methods, and module-level variables

---

## Assignment 1: Type-Safe HTTP API Client Library

### Scenario

Build `typed_client` — a small HTTP API client for a fictional "Weather & Geo" REST API. Every request and response is typed. The library must catch type errors at development time via mypy, not at runtime in production.

### Requirements

**Type definitions:**

```python
from typing import TypeVar, Generic, Optional, Union, Callable, Protocol, Literal, TypedDict, Any
from dataclasses import dataclass
```

1. **Response models (TypedDict or dataclass):**
   - `Coordinates`, `WeatherData`, `ForecastDay`, `ApiErrorResponse`

2. **Generic paginated response:**

```python
T = TypeVar("T")

@dataclass
class PaginatedResponse(Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
```

3. **Protocol for cache backend:**

```python
class CacheBackend(Protocol):
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str, ttl: int) -> None: ...
```

Implement `MemoryCache` and `NoOpCache` satisfying the protocol without inheritance.

4. **Client methods (all fully annotated):**

```python
def get_weather(city: str, *, units: Literal["metric", "imperial"] = "metric") -> WeatherData: ...
def get_forecast(city: str, days: int = 5) -> list[ForecastDay]: ...
def search_cities(query: str, limit: int = 10) -> PaginatedResponse[str]: ...
```

5. **Callback types:**

```python
ErrorHandler = Callable[[ApiErrorResponse], None]
RetryPredicate = Callable[[Exception], bool]
```

6. **`request` method with Union return:**

```python
def request(
    method: Literal["GET", "POST", "PUT", "DELETE"],
    path: str,
    *,
    params: Optional[dict[str, str]] = None,
    json_body: Optional[dict[str, Any]] = None,
) -> Union[WeatherData, list[ForecastDay], PaginatedResponse[str]]: ...
```

7. **Type aliases:**

```python
Headers = dict[str, str]
QueryParams = dict[str, Union[str, int, float]]
JsonDict = dict[str, Any]
```

8. **Generic repository:**

```python
class Repository(Generic[T]):
    def __init__(self, store: dict[str, T]) -> None: ...
    def get(self, key: str) -> Optional[T]: ...
    def save(self, key: str, value: T) -> None: ...
```

9. **mypy configuration:** Include `mypy.ini` with `strict = True`

10. **Mock implementation:** Return hardcoded data (no real HTTP) but types must be complete

### Technical Specifications

- Basic annotations: `int`, `str`, `float`, `bool`, `None`
- `Optional`, `Union`, `list`, `dict` (Python 3.9+ style `list[T]`)
- `Callable`, `TypeVar`, `Generic`
- `Protocol` for structural typing
- `Literal` for constrained strings
- `TypedDict` for JSON-like dicts
- Type aliases with `TypeAlias` or simple assignment
- Function parameter kinds: positional, keyword-only (`*`), defaults
- Return type annotations on generators if used

### Acceptance Criteria

- [ ] `mypy --strict` passes with 0 errors
- [ ] `Protocol` implementations type-check without inheriting Protocol
- [ ] `PaginatedResponse[WeatherData]` and `PaginatedResponse[str]` both work
- [ ] `Literal["metric", "imperial"]` enforced by type checker (invalid value flagged)
- [ ] All public functions have parameter and return annotations
- [ ] README documents how to run mypy
- [ ] At least 3 `TypeVar` or `Generic` usages

### Bonus Challenges

- `overload` for `request()` returning precise type per method+path combination
- `Final` for module-level constants
- `ParamSpec` and `TypeVarTuple` for advanced decorator typing (if on 3.10+)
- Runtime validation with `typing.get_type_hints()` demo script

### Hints

- Use `from __future__ import annotations` for forward references
- Protocol: class only needs matching methods — no `(Protocol)` inheritance required in usage
- Mock `request` with `match method` / `if path ==` returning typed dataclasses

---

## Assignment 2: Typed Domain Model for Event Ticketing

### Scenario

Model a concert ticketing domain with complete type coverage. Nested types, optional fields, and validators (runtime) complement static types.

### Requirements

1. **Enums and Literals:**
   - `SeatSection = Literal["orchestra", "balcony", "general"]`
   - `OrderStatus = Literal["pending", "confirmed", "cancelled", "refunded"]`

2. **Nested dataclasses (fully typed):**
   - `Venue`, `Event`, `Seat`, `Ticket`, `Order`, `Customer`, `PaymentInfo`

3. **Optional fields:** `Customer.phone: Optional[str]`, `Event.supporting_act: Optional[str]`

4. **Union types:**
   - `PaymentMethod = Union[CreditCardPayment, PayPalPayment, CashPayment]` (dataclasses with discriminator field)

5. **Functions:**
   - `calculate_order_total(order: Order, *, discount_code: Optional[str] = None) -> Decimal`
   - `find_available_seats(event: Event, section: SeatSection, count: int) -> list[Seat]`
   - `apply_discount(total: Decimal, code: str) -> Decimal` — raises `ValueError`

6. **Type narrowing:** function `process_payment(method: PaymentMethod) -> str` using `isinstance` checks; mypy must narrow types in branches

7. **Callable:** `PricingStrategy = Callable[[Event, Seat], Decimal]` — implement `standard_pricing` and `dynamic_pricing`

8. **Class with typed attributes:**

```python
class TicketInventory:
    _seats: dict[str, Seat]
    def reserve(self, seat_ids: list[str]) -> list[Ticket]: ...
```

9. **Module `__all__`** exporting public typed API

10. **Test file `test_types.py`:** uses `assert isinstance` and runs mypy on test fixtures

### Technical Specifications

- Function annotations with complex nested types
- `Optional`, `Union`, `Literal`
- `Callable` for strategy functions
- Type narrowing with isinstance
- Dataclasses with typed fields
- mypy strict compliance

### Acceptance Criteria

- [ ] 10+ dataclasses/TypedDicts all fully annotated
- [ ] `process_payment` branches type-check without casts
- [ ] `PricingStrategy` callable accepted by `quote_ticket(event, seat, strategy)`
- [ ] Optional fields handled without `None` attribute errors (mypy catches misuse)
- [ ] `__all__` lists all public symbols

### Bonus Challenges

- `TypedDict` with `total=False` for partial updates: `EventUpdate`
- `NewType` for `OrderId = NewType("OrderId", str)` and `SeatId`
- Generic `Result[T, E]` type for success/failure returns

### Hints

- Use `decimal.Decimal` for money types
- Narrow Union: `if isinstance(method, CreditCardPayment): method.last_four` — mypy knows type
- Dataclass: `from dataclasses import dataclass, field`

---

## Assignment 3: Configuration & Plugin System with Protocols

### Scenario

Build a typed configuration loader and plugin registry. Plugins are discovered by protocol conformance, not inheritance.

### Requirements

1. **`AppConfig` using TypedDict or pydantic-style dataclass** (stdlib dataclass only):
   - `database: DatabaseConfig`, `redis: RedisConfig`, `logging: LoggingConfig`

2. **Each config nested and fully typed** with `Optional` defaults documented

3. **`load_config(path: Optional[Path] = None) -> AppConfig`** — reads JSON/YAML mock

4. **Plugin Protocol:**

```python
class ProcessorPlugin(Protocol):
    name: str
    def process(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]: ...
    def configure(self, options: dict[str, Any]) -> None: ...
```

5. **`PluginRegistry`:**

```python
class PluginRegistry:
    def register(self, plugin: ProcessorPlugin) -> None: ...
    def get(self, name: str) -> Optional[ProcessorPlugin]: ...
    def run_all(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]: ...
```

6. **Implement 3 plugins** (FilterPlugin, TransformPlugin, ValidatePlugin) — no common base class

7. **`TypeGuard` function (3.10+):**

```python
def is_valid_config(obj: dict[str, Any]) -> TypeGuard[AppConfig]: ...
```

8. **mypy plugin test:** intentionally broken file `broken_types.py` showing 5 errors mypy catches — document in README

9. **CI-style script `check_types.sh`:** runs mypy on entire package

### Technical Specifications

- Protocols, TypeGuard, Generics, Optional, TypedDict
- mypy strict mode
- Type-safe configuration loading
- Structural subtyping

### Acceptance Criteria

- [ ] Plugins register without inheriting from Protocol
- [ ] `run_all` chains plugins with correct types throughout
- [ ] `is_valid_config` narrows type in if-branch (mypy verified)
- [ ] `check_types.sh` exits 0 on clean code, non-zero on broken file
- [ ] README lists 5 example mypy errors from intentional mistakes

### Bonus Challenges

- `functools.singledispatch` with typed overloads
- Config validation errors typed as `list[ConfigError]` dataclass
- Generic `Plugin[T]` where T is input/output record type

### Hints

- `TypeGuard` returns bool but tells mypy the narrowed type in True branch
- Plugins can be simple classes with `name` as class attribute
- `Path` from `pathlib` for file paths
