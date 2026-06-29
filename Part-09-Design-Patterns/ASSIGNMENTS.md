# Part 9: Design Patterns - Assignments

## Assignment Guidelines

- **Estimated time:** 14-18 hours total
- **Prerequisites:** Parts 1-8 complete
- **Submission:** Python package demonstrating patterns with README mapping each pattern to files
- **Rules:** Use at least 8 distinct patterns across assignments; justify when Pythonic alternatives are better

---

## Assignment 1: Extensible Notification Platform

### Scenario

Build a notification system where new channels (Email, SMS, Slack, Push) and delivery strategies can be added without modifying core code. Multiple design patterns must work together.

### Requirements

**Patterns to implement (minimum):**

| Pattern | Usage |
|---------|-------|
| **Factory** | `NotificationFactory.create(channel_type)` → Email/SMS/Slack notifier |
| **Strategy** | `DeliveryStrategy`: immediate, batched, scheduled |
| **Observer** | `EventBus` notifies subscribers on `notification.sent`, `notification.failed` |
| **Singleton** | `ConfigurationManager` — one global config instance |
| **Template Method** | `BaseNotifier.send()` defines steps: validate → format → deliver → log; subclasses implement `deliver()` |
| **Decorator** | `LoggingNotifierDecorator`, `RetryNotifierDecorator` wrapping any `Notifier` |
| **Facade** | `NotificationService` — simple `send(user, message, channel)` hiding subsystem complexity |
| **Command** | `SendNotificationCommand` with `execute()` and `undo()` (undo removes from outbox queue) |

**Functional requirements:**

1. Register users with channel preferences (`dict` or small model)
2. Send notification through factory-created notifier with selected strategy
3. Observers: `MetricsObserver` (counts), `AuditLogObserver` (writes log file)
4. Batch strategy queues messages; flush when batch size or timeout reached
5. Decorators stack: `Retry(Logging(EmailNotifier()))`
6. Facade exposes one-liner API used by demo CLI
7. Command pattern supports undo for last 10 notifications in outbox

**Pythonic alternatives section in README:**
- When module-level functions replace Strategy
- When `@register` dict replaces Factory
- When generators replace Iterator pattern

### Technical Specifications

- Creational: Factory, Singleton, Builder (optional for complex messages)
- Structural: Decorator, Facade, Adapter (adapt legacy `LegacySmsGateway` to `Notifier` interface)
- Behavioral: Strategy, Observer, Command, Template Method
- ABC or Protocol for `Notifier` interface

### Acceptance Criteria

- [ ] New channel type addable by creating class + factory registration only
- [ ] Strategy swap changes behavior without changing client code
- [ ] 2+ observers receive events on send
- [ ] Decorator stack logs and retries (prove retry with mock failure)
- [ ] Facade `send()` works end-to-end from CLI
- [ ] Command `undo()` removes last notification from outbox
- [ ] README maps each pattern to specific class/file

### Bonus Challenges

- **Builder** for `NotificationBuilder().to(user).subject().body().priority().build()`
- **Chain of Responsibility** for validation pipeline before send
- **Prototype** for cloning notification templates

### Hints

- Observer: `EventBus.subscribe(event_name, callback)` list
- Command history: `deque` of commands max 10
- Adapter: wrap `LegacySmsGateway.send_sms(phone, msg)` as `Notifier.deliver()`

---

## Assignment 2: Document Export Framework

### Scenario

A reporting service exports data to PDF, CSV, JSON, and HTML. The framework must support multiple export formats, filtering pipelines, and a simplified API for clients.

### Requirements

**Patterns:**

1. **Abstract Factory** — `ExportFactory` creates matching `Writer` + `Formatter` pairs
2. **Builder** — `ReportBuilder` with fluent API: `.add_section().add_table().set_theme().build()`
3. **Strategy** — `SortStrategy`, `FilterStrategy` applied before export
4. **Iterator** — custom `ReportSectionIterator` over nested sections
5. **Composite** — `ReportComponent` tree: sections contain tables, paragraphs, charts (charts as stub)
6. **Proxy** — `LazyDataProxy` loads heavy dataset only on first access to `.rows`
7. **Memento** — save/restore `ReportBuilder` state for undo in interactive mode
8. **State** — `ExportJob` transitions: draft → validating → exporting → completed/failed

**Data:** Sample sales data (100+ rows) with region, product, amount, date

**Deliverables:**
- Export same report to 4 formats with consistent content
- Filter strategy: date range + minimum amount
- Sort strategy: by amount descending
- Composite tree printed as indented structure
- State pattern rejects invalid transitions (e.g., export from draft without validate)

### Technical Specifications

- Minimum 8 patterns from creational, structural, behavioral categories
- Clear separation: data loading, transformation, formatting, writing
- Pythonic notes: dataclasses for Report nodes, `@singledispatch` for format dispatch

### Acceptance Criteria

- [ ] All 4 export formats produce files from same builder pipeline
- [ ] Builder fluent API constructs multi-section report
- [ ] Composite `render()` traverses tree recursively
- [ ] Lazy proxy loads data exactly once (counter proves)
- [ ] Memento restores previous builder state after undo
- [ ] Invalid state transition raises error with clear message

### Bonus Challenges

- **Visitor** pattern for traversing composite and exporting per-node
- **Flyweight** for shared style objects across table cells
- **Bridge** separating abstraction (Report) from implementation (Renderer)

### Hints

- Builder methods return `self` for chaining
- Memento: store `deepcopy` of builder internal list
- State: each state is class with `validate(job)`, `export(job)` methods

---

## Assignment 3: E-Commerce Checkout Orchestrator

### Scenario

Implement checkout flow coordinating cart, inventory, payment, and shipping subsystems. This is the capstone pattern assignment — 10+ patterns in one coherent system.

### Requirements

**Subsystems (use Facade per subsystem):**
- `InventoryFacade` — reserve/release stock
- `PaymentFacade` — charge/refund (mock)
- `ShippingFacade` — calculate rates, create shipment

**Patterns in checkout flow:**

1. **Factory Method** — `PaymentProcessorFactory` creates Card/PayPal/Crypto processors
2. **Strategy** — shipping cost: standard, express, overnight
3. **Observer** — order status changes notify email/inventory/analytics listeners
4. **Command** — checkout steps as commands; saga-style compensation on failure
5. **Chain of Responsibility** — fraud check → stock check → payment → confirmation
6. **Singleton** — order ID generator
7. **Decorator** — add gift wrap, insurance to line items (price decorators)
8. **Adapter** — third-party `StripeLegacyAPI` adapted to `PaymentProcessor`
9. **Template Method** — `CheckoutProcess.run()` fixed steps, subclasses override hooks
10. **Repository** (preview) — `OrderRepository` in-memory storage

**Compensation (saga):** if payment fails after stock reserved, release stock via compensating command

**Demo:** CLI checkout with 3 products; simulate payment failure and successful retry

### Technical Specifications

- Integrate creational, structural, behavioral patterns cohesively
- Not pattern soup — each pattern solves a stated problem in README
- Diagram in README (ASCII or mermaid) showing flow

### Acceptance Criteria

- [ ] Successful checkout runs full chain and notifies all observers
- [ ] Payment failure triggers stock release (compensation)
- [ ] 3 shipping strategies produce different costs for same cart
- [ ] Fraud handler in chain can block checkout
- [ ] 10+ patterns documented with one-sentence justification each
- [ ] Demo runs without external services

### Bonus Challenges

- **Mediator** between cart, inventory, and payment instead of direct calls
- **Specification** pattern for complex discount rules
- Serialize order to dict using **Memento** for cart snapshots

### Hints

- Command compensation: each command implements `undo()`
- Chain: each handler has `set_next(handler)` or list iteration
- Keep payment/inventory as separate modules with facades
