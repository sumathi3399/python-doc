# Part 12: Pydantic - Assignments

## Assignment Guidelines

- **Estimated time:** 12-16 hours total
- **Prerequisites:** Parts 1-11 complete; Pydantic v2 syntax required
- **Submission:** Python package with models, validation pipeline, and pytest tests
- **Rules:** Use Pydantic v2 (`field_validator`, `model_validator`, `model_dump`, `ConfigDict`)

---

## Assignment 1: Healthcare Patient Records System

### Scenario

Build a strict validation layer for a healthcare application's patient records. Incorrect data must never enter the system — Pydantic is the gatekeeper before any database or API persistence.

### Requirements

**Models (nested):**

1. **`Address`** — street, city, state, postal_code, country; postal code validated per country rules (simplified regex)

2. **`EmergencyContact`** — name, relationship, phone; phone E.164 format via regex validator

3. **`Medication`** — name, dosage, frequency (`Literal`), start_date, end_date optional; `model_validator` ensures end_date > start_date

4. **`Allergy`** — allergen, severity (`Literal["mild", "moderate", "severe"]`)

5. **`Patient`** — id, name, dob, email (`EmailStr`), phone, address, emergency_contacts (list, min 1), medications, allergies, blood_type (`Literal`), is_active

6. **`PatientCreate`** — excludes id; password field for portal access with strength validator

7. **`PatientUpdate`** — all fields optional (`model_config` or optional fields)

8. **`PatientResponse`** — excludes internal notes and password; `model_config = ConfigDict(from_attributes=True)`

9. **`PatientSummary`** — computed fields: `age` (from dob), `medication_count`, `has_severe_allergy`

**Validators:**

- `@field_validator` for string normalizations (strip, title case names)
- `@model_validator(mode='after')` for cross-field rules (e.g., pediatric patient < 18 requires guardian contact)
- Custom `ValidationError` handler formatting errors for API response

**Serialization:**

- `model_dump(exclude_none=True, by_alias=True)` with field aliases (`patient_id` alias for `id`)
- `model_dump_json()` for API output
- `model_validate()` from dict and JSON
- Custom serializer for `datetime` fields to ISO format

**Parsing pipeline:**

- `parse_patient_batch(json_lines: list[str]) -> tuple[list[Patient], list[dict]]` — returns valid patients + error report per line

### Technical Specifications

- Pydantic v2 BaseModel, Field constraints
- field_validator, model_validator
- EmailStr, Field(ge, le, min_length, pattern)
- Computed fields (`@computed_field`)
- model_dump, model_validate, model_validate_json
- ConfigDict: from_attributes, populate_by_name, str_strip_whitespace
- Nested models
- ValidationError handling

### Acceptance Criteria

- [ ] Invalid email rejected with field-level error message
- [ ] Pediatric rule enforced when dob < 18 years ago
- [ ] `PatientResponse` never includes password or internal notes
- [ ] Computed `age` matches manual calculation
- [ ] Batch parser returns 8/10 valid on provided test file with error details for 2 failures
- [ ] JSON round-trip: `Patient.model_validate(p.model_dump())` succeeds
- [ ] 15+ pytest tests covering validators

### Bonus Challenges

- Generic `PaginatedResponse[T]` using Pydantic v2 generics
- `SecretStr` for password field — never appears in repr/dump
- Discriminated union for `InsuranceInfo | SelfPay` via `Field(discriminator='type')`

### Hints

- Age: `(date.today() - dob).days // 365`
- model_validator after: `def check_guardian(self) -> Self:`
- Error report: `except ValidationError as e: e.errors()`

---

## Assignment 2: E-Commerce Catalog & Order Validation

### Scenario

Model a complete e-commerce domain with products, variants, pricing rules, carts, and orders. Validation must enforce business rules at the schema level.

### Requirements

1. **`Money`** — amount (`Decimal`), currency (`Literal["USD", "EUR", "INR"]`); no float for money

2. **`ProductVariant`** — sku, attributes dict, price, stock (`Field(ge=0)`)

3. **`Product`** — name, description, category, tags, variants (min 1), `model_validator` unique SKUs across variants

4. **`DiscountCode`** — code, percent OR fixed amount (mutually exclusive — model validator)

5. **`CartItem`** — variant_sku, quantity (`Field(ge=1, le=99)`)

6. **`Cart`** — items, discount_code optional; computed `subtotal`, `discount_amount`, `total`

7. **`ShippingAddress`**, **`OrderCreate`**, **`Order`** — status enum, timestamps

8. **`OrderResponse`** with nested items and computed `item_count`

9. **Import from ORM mock:** class with attributes matching model; validate via `from_attributes`

10. **CSV import pipeline:**
    - `ProductImportRow` model per CSV row
    - `validate_csv(path) -> ValidationReport` with row numbers and errors
    - `ValidationReport` model: total, valid, invalid, errors: list[`RowError`]

11. **JSON Schema export:** `Product.model_json_schema()` documented in README

12. **Settings:** `CatalogSettings(BaseSettings)` — max_cart_items, allowed_currencies, tax_rate

### Technical Specifications

- Field constraints, Literal, Decimal
- model_validator cross-field
- computed_field
- Generic models if applicable
- BaseSettings from pydantic-settings
- Serialization exclude/include
- Custom validators for business rules

### Acceptance Criteria

- [ ] Duplicate variant SKUs rejected on Product
- [ ] Discount code applies correctly in computed totals
- [ ] Float price in input coerced or rejected per your documented policy
- [ ] CSV validator reports row 7 error with field name
- [ ] `from_attributes` works with mock ORM object
- [ ] Settings load from `.env` file
- [ ] 20+ unit tests

### Bonus Challenges

- `TypeAdapter(list[Product])` for validating JSON array
- Field `serialization_alias` for camelCase API output
- `model_copy(update={...})` for immutable order status updates

### Hints

- Use `Decimal` via validator converting str/int inputs
- Cart total: sum item.price * qty in computed field
- RowError: `row: int`, `field: str`, `message: str`

---

## Assignment 3: Multi-Environment Configuration & Secrets Platform

### Scenario

Build a type-safe configuration system for a microservices-style app with nested settings, secret handling, and environment-specific overrides.

### Requirements

1. **`DatabaseSettings`** — url (`PostgresDsn` or str), pool_size, echo, connect_timeout

2. **`RedisSettings`** — url, max_connections

3. **`SecuritySettings`** — secret_key (`SecretStr`), algorithm, token_expire_minutes

4. **`APISettings`** — host, port, debug, cors_origins (`list[str]` parsed from comma-separated env)

5. **`AppSettings(BaseSettings)`** — nests above via `model_config SettingsConfigDict(env_nested_delimiter='__')`

6. **Environment variants:**
   - `DevelopmentSettings` — debug True, sqlite default
   - `ProductionSettings` — debug False, required secrets
   - `TestingSettings` — in-memory DB

7. **Factory `get_settings() -> AppSettings`** using `@lru_cache` and `ENVIRONMENT` env var

8. **`validate_settings_on_startup()`** — raises if production missing `SECRET_KEY`

9. **`SettingsExport`** — model with secrets redacted in `model_dump()` custom serializer

10. **Parse complex env values:**
    - JSON string to `list[str]` for ALLOWED_HOSTS
    - `field_validator(mode='before')` for cors_origins string split

11. **Documentation model `SettingsSchema`** — describes each field for ops team (name, type, required, default, description)

12. **CLI `python -m config check`** — loads settings and prints validation result

### Technical Specifications

- pydantic-settings BaseSettings
- Nested settings, env prefixes
- SecretStr, field validators (before/after)
- model_dump with exclude
- Settings validation at startup
- Pydantic v2 ConfigDict

### Acceptance Criteria

- [ ] `DATABASE__URL` nested env var loads correctly
- [ ] Production fails fast without SECRET_KEY
- [ ] SecretStr not printed in logs/dumps
- [ ] `get_settings()` returns cached singleton
- [ ] `.env.example` file generated from field descriptions
- [ ] CLI check exits 0 in dev, non-zero when required prod vars missing
- [ ] README documents all env variables in table

### Bonus Challenges

- `Json[T]` type for complex env parsing
- AWS Secrets Manager loader (mock) merging into settings
- `model_validate` migration from legacy flat dict format

### Hints

- `model_config = SettingsConfigDict(env_file='.env', env_nested_delimiter='__')`
- `SecretStr.get_secret_value()` only when needed
- lru_cache on get_settings prevents re-parsing
