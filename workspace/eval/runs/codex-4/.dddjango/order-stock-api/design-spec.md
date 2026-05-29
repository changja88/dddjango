# Design Spec: order-stock-api

## 1. Context and Scope

- Bounded context placement: create a new independent `orders` BC/app under `application/orders/`.
  - Why: G0 scope fixes a separate `orders` bounded context; `discipline-houserules` §1 applies the dddjango standard tree because the current project only has a flat `catalog` startapp layout, not an established layered convention.
- Existing upstream inventory source: `catalog.Product` remains the stock source for this smoke scope.
  - Why: scope explicitly reuses `catalog.Product`; `orders` must not absorb the `catalog` model into its domain language (`architecture-ddd` §2.3).
- API framework: plain Django view returning `JsonResponse`.
  - Why: scope fixes plain Django; no Django Ninja/DRF contract or schema layer is introduced.
- Test runner: Django built-in `manage.py test`.
  - Why: scope fixes Django default test runner.
- Included behavior: create one order for one product and one requested quantity; if stock is sufficient, decrement stock and persist the order in one transactional flow; if stock is insufficient, return HTTP 409 and leave order/stock unchanged.
- Excluded behavior: multi-line orders, payment, customer accounts, reservation, async messaging, idempotency storage, external integrations.

## 2. Ubiquitous Language

- `Order`: the `orders` BC aggregate representing a successfully accepted purchase request for one product and quantity.
- `ProductInventory`: an upstream inventory collaborator exposed to `orders` as a port, backed by `catalog.Product`.
- `ProductInventorySnapshot`: the stock view used by the domain decision: `product_id`, `available_stock`, and `version`.
- `Quantity`: value object for the positive integer requested by the caller.
- `InsufficientStock`: domain rejection when requested quantity exceeds available stock.
- `InvalidQuantity`: domain rejection when a quantity is not a positive integer.

Application/infra outcome, not ubiquitous domain language:

- `InventoryConflict`: persistence-time concurrent modification or database lock conflict; the application service reloads/retries and may surface a retryable HTTP 409 outcome.

Why: language is scoped to the `orders` BC (`architecture-ddd` §2.3); the upstream `catalog.Product` ORM model is translated at the ACL boundary.

## 3. Domain Design

### Aggregate Boundary

- Aggregate root: `Order`.
- Aggregate fields: `id` after persistence, `product_id`, `quantity`, `status`, `created_at`.
- Initial status: `created`.
- Invariant: an `Order` can be created only after the domain has accepted the requested `Quantity` against a `ProductInventorySnapshot`.
- Quantity invariant: `Quantity` must be a positive integer and is validated in the domain creation path.

Why: the scope has one order for one product; a small aggregate protects the real invariant without pulling `catalog.Product` into the `orders` aggregate (`architecture-ddd` §3.3).

### Domain Policy

- `Quantity` is a value object under `domain_layer/order/value_object/quantity.py`; it rejects non-integer or non-positive input with `InvalidQuantity`.
- `Order.create(product_id, quantity, inventory_snapshot)` accepts a validated `Quantity` and performs the stock sufficiency decision.
- If `quantity.value > inventory_snapshot.available_stock`, raise `InsufficientStock`.
- If quantity is valid and stock is sufficient, return a new `Order` instance.
- SQL/ORM update code must not be the only owner of the stock sufficiency decision.

Why: domain objects own business invariants, while application services orchestrate flow and transactions (`architecture-ddd` §3.2, §3.6). The DB layer may enforce backstops but not replace the domain decision.

### Domain Events

- No domain event is introduced for this slice.

Why: no result-eventual side effect is in scope; stock decrement and order creation require immediate consistency, so synchronous ACL + transaction is the correct integration style (`architecture-ddd` 규칙4, §6.8; `discipline-houserules` `references/final.md` §2).

### Repositories and Ports

- `OrderRepository`: domain repository interface for persisting `Order`.
- `ProductInventoryPort`: domain collaborator port for loading and decrementing upstream inventory.
- `DjangoOrderRepository`: Django ORM implementation of `OrderRepository`.
- `DjangoProductInventoryPort`: ACL adapter backed by `catalog.Product`.

Why: repository and port abstractions follow DIP (`architecture-ddd` §5.1, §5.2); naming follows `discipline-houserules` §4: abstraction = concept + role suffix, implementation = technology/source qualifier + full base name, no `Interface`/`Impl`.

## 4. Application Flow

Use case: `CreateOrderApp`.

Flow:

1. Parse and validate a `CreateOrderCommand` containing `product_id` and `quantity`; the command creates a domain `Quantity`.
2. Start a DB transaction owned by the application service.
3. Load a `ProductInventorySnapshot` through `ProductInventoryPort`.
4. Call `Order.create(...)` so the domain accepts or rejects the request.
5. Ask `ProductInventoryPort` to decrement stock using the loaded snapshot version.
6. If the decrement detects a version conflict, reload inventory and rerun steps 4-5 for a bounded retry.
7. Persist the accepted `Order` through `OrderRepository`.
8. Commit the transaction and return an output DTO.

Transaction and retry policy:

- Transaction owner: `CreateOrderApp`.
- Maximum retry: one immediate retry after an optimistic version conflict.
- SQLite lock retry: if SQLite raises a write-lock `OperationalError` during the inventory decrement transaction, roll back that transaction and retry the whole use case once with a fresh snapshot.
- If the retry observes insufficient stock, return the domain `InsufficientStock` outcome.
- If the retry still conflicts or remains locked, surface the application/infra `InventoryConflict` outcome as HTTP 409 with a retryable conflict problem type.
- The order is persisted only after stock decrement succeeds.

Why: application services coordinate transactions and dependencies without owning business rules (`architecture-ddd` §3.6); Risky Writes require explicit transaction owner, locking/retry, side-effect timing, and test criteria (`architecture-db` §9.6).

## 5. API Contract

Endpoint:

- Method: `POST`
- Path: `/api/orders/`
- Content-Type: `application/json`
- Content negotiation: `Accept` is not strictly enforced in this smoke scope; successful responses are `application/json`, and error responses are `application/problem+json`.
- Auth: none for this smoke scope.
- Idempotency-Key: not supported for this scope; repeated successful POSTs create separate orders while stock remains sufficient.

Why: POST is non-idempotent creation (`architecture-api` §2); idempotency storage is excluded by G0 scope even though duplicate-sensitive production APIs would normally define an idempotency key policy (`architecture-api` §13).

Request body:

```json
{
  "product_id": 1,
  "quantity": 2
}
```

Validation:

- `product_id` is required and must be a positive integer.
- `quantity` is required and must be a positive integer.
- Unknown JSON fields are ignored only if plain parsing already tolerates them; the response contract does not expose them.
- All request validation failures use `400 invalid-order-request`, including malformed JSON, missing `product_id`, missing `quantity`, non-integer values, and non-positive values.
- Missing or non-`application/json` `Content-Type` is rejected before body validation with `415 unsupported-media-type`.

Success response:

- Status: `201 Created`
- Body:

```json
{
  "id": 123,
  "product_id": 1,
  "quantity": 2,
  "status": "created"
}
```

Error responses use RFC 9457 Problem Details shape and `application/problem+json` content type.

Unsupported media type:

- Status: `415 Unsupported Media Type`
- Type: `/problems/unsupported-media-type`
- Title: `Unsupported Media Type`
- Body fields: `type`, `title`, `status`, `detail`

Invalid order request:

- Status: `400 Bad Request`
- Type: `/problems/invalid-order-request`
- Title: `Invalid order request`
- Applies to:
  - malformed JSON body.
  - missing `product_id` or `quantity`.
  - non-integer `product_id` or `quantity`.
  - non-positive `product_id` or `quantity`.
- Body fields: `type`, `title`, `status`, `detail`, and `errors` when field-level validation details are available.
- Field error codes: `required`, `invalid_integer`, `must_be_positive`.

Product not found:

- Status: `404 Not Found`
- Type: `/problems/product-not-found`
- Title: `Product not found`
- Body fields: `type`, `title`, `status`, `detail`

Insufficient stock:

- Status: `409 Conflict`
- Type: `/problems/insufficient-stock`
- Title: `Insufficient stock`
- Body fields: `type`, `title`, `status`, `detail`, `available_stock`, `requested_quantity`

Concurrent inventory conflict after retry:

- Status: `409 Conflict`
- Type: `/problems/inventory-conflict`
- Title: `Inventory conflict`
- Body fields: `type`, `title`, `status`, `detail`

Why: URLs are noun resources and POST creates a subordinate resource (`architecture-api` §3); status-specific bodies and Problem Details follow `architecture-api` §5-§6.

## 6. Data Design

### Schema Changes

New `orders` Django app schema:

- `OrderModel`
  - `id`: `BigAutoField` primary key.
  - `product`: `ForeignKey('catalog.Product', on_delete=PROTECT)`; ORM column is `product_id`, and the domain still sees only the integer id.
  - `quantity`: positive integer.
  - `status`: short string, initially `created`.
  - `created_at`: timezone-aware creation timestamp.

Existing `catalog.Product` schema additions:

- Add `version`: non-negative integer with default `0`.
- Add DB check constraint: `stock >= 0`.

Why: `OrderModel` is persistence for the new aggregate; the FK protects same-database referential integrity while the repository maps it to a plain `product_id` so the domain keeps only an id reference across BCs (`architecture-ddd` §3.3; `architecture-db` §8). `version` enables optimistic concurrency across SQLite and Postgres; check constraint is a DB backstop for the inventory invariant (`architecture-db` §8, §9.6).

### Indexes and Constraints

- `OrderModel.product`: use the FK-created index if Django creates one; do not add a second explicit product lookup index for this write-only slice.
- `OrderModel.created_at`: add an index only if ordering/listing is introduced later; not required for this slice.
- `OrderModel.quantity`: DB check `quantity > 0`.
- `OrderModel.status`: DB check `status IN ('created')`; no separate status table for this scope.
- `catalog.Product.stock`: DB check `stock >= 0`.

Why: the current API does not query orders by product, so an extra explicit index would be speculative; FK support is enough for referential integrity and deletion protection (`architecture-db` §5, §7-§8). DB checks protect simple invariants at the storage boundary (`architecture-db` §8).

### Transaction, Locking, and Engine Differences

- Primary consistency mechanism: optimistic compare-and-swap using `catalog.Product.version`.
- Decrement persistence condition: match the previously loaded `product_id` and `version`; update `stock = stock - quantity` and `version = version + 1`.
- The SQL/ORM `WHERE` clause must contain identity and version conflict guards, not a duplicate `stock >= quantity` business decision.
- The domain decision still runs before each decrement attempt using a fresh snapshot.
- DB check `stock >= 0` remains the final backstop.
- Stock writer contract: every application path that mutates `catalog.Product.stock` must also advance `catalog.Product.version`. This slice implements only the orders ACL writer; direct DB edits or admin/manual stock changes are outside the concurrency guarantee unless they preserve that contract.

Postgres behavior:

- The ACL may use `select_for_update()` when loading the product snapshot inside the transaction.
- The version guard still stays in place to make concurrency behavior explicit and testable.

SQLite behavior:

- `select_for_update()` is effectively a no-op.
- SQLite deferred transactions can expose lock timing differences.
- The version guard detects lost updates when SQLite reaches the conditional update path, and the `stock >= 0` constraint prevents negative stock.
- SQLite may instead raise `OperationalError` such as `database is locked` during concurrent writes. Treat that as an infra conflict: roll back, retry the whole use case once with a fresh snapshot, then map another lock/conflict to the same HTTP 409 `/problems/inventory-conflict` outcome.

Why: inventory decrement is a Risky Write, so the design must name locking, retry, and engine behavior (`architecture-db` §9.5-§9.6). The domain owns the business decision while the DB enforces durable conflict/backstop constraints (`architecture-ddd` §3.2; `architecture-db` §8).

### Migration Safety

- `orders` app migration creates a new table only.
- `OrderModel.product` uses `on_delete=PROTECT`, so product deletion is refused once orders reference the product.
- `catalog.Product.version` is additive with a default and does not require backfill for this small smoke project.
- `catalog.Product.stock >= 0` is safe for seeded/current data because `stock` is already a `PositiveIntegerField`; for a large production table this would use an expand/validate/contract rollout.

Why: schema rollout should be additive and lock-aware; the smoke repository is small, but the decision remains explicit (`architecture-db` §11).

## 7. Package and Test Structure

Existing project finding:

- Current source tree has `config/` and a flat `catalog/` Django startapp with `models.py`, `views.py`, and `tests.py`.
- There is no established layered app convention, repository layer, package-level `application/` container, or semantic test directory layout.

Decision:

- Apply the dddjango standard tree to the new `orders` BC.
- Do not restructure existing `catalog`; integrate with it through an ACL adapter.

Why: `discipline-houserules` §1 says existing established conventions win, but flat startapp state is not an established convention to copy. Scope fixes `orders` as a new independent area.

Standard-tree invariants to apply for `orders`:

- Use an `application/` container even with a single new app.
- Create all four `_layer` directories: `domain_layer/`, `application_layer/`, `infra_layer/`, `presentation_layer/`.
- Organize first by concept/feature, then by kind: `domain_layer/order/{entity,value_object,repository,...}` and `application_layer/create_order/{command,dto,...}`.
- Keep kind-level folders as folders, not flattened files; preserve `__init__.py` regular packages.
- Put the Django app under `application/orders/infra_layer/django_orders/`.
- `OrdersConfig.name = 'application.orders.infra_layer.django_orders'` and `label = 'orders'`.
- Do not put root `models.py` in `application/orders/`.
- Name ORM models with `<Name>Model`, e.g. `OrderModel`; domain aggregate remains `Order`.
- Name ports/repositories as `OrderRepository`, `ProductInventoryPort`, `DjangoOrderRepository`, and `DjangoProductInventoryPort`; file names are unabbreviated, e.g. `order_repository.py`, `product_inventory_port.py`.

Planned source layout:

```text
application/
  orders/
    orders_api_router.py
    published_service/
    domain_layer/
      order/
        order.py
        entity/
        value_object/
          quantity.py
        repository/
          order_repository.py
        port/
          product_inventory_port.py
        domain_service/
        event/
        specification/
        exception.py
    application_layer/
      create_order/
        command/
          create_order_app.py
        dto/
          create_order_command.py
        query/
        handler/
        service/
    infra_layer/
      django_orders/
        apps.py
        models/
          order_model.py
        migrations/
        admin/
      repository/
        order_repository.py
      acl/
        catalog_acl.py
      service/
    presentation_layer/
      api/
        create_order/
          api_orders.py
      schema/
        schema_in.py
        schema_out.py
        error_out.py
    test/
      unit/
      integration/
      e2e/
```

Routing/config changes for implementation:

- Add `application.orders.infra_layer.django_orders` to `INSTALLED_APPS`.
- Include the `orders` URL patterns from `config.urls` under `/api/orders/`.

Test layout:

- Domain unit tests: `application/orders/test/unit/test_order_creation_policy.py`.
- Application unit tests with fakes: `application/orders/test/unit/test_create_order_app.py`.
- API/DB integration tests: `application/orders/test/integration/test_create_order_api.py`.
- No e2e test is required for this slice, but the `e2e/` package is present under the standard tree.

Why: tests are split by meaning rather than flat `test_*.py` lists (`discipline-houserules` §1.3; `references/final.md` §2).

## 8. External Observable Behaviors

Acceptance tests should verify:

- `POST /api/orders/` with existing product and sufficient stock returns `201`, creates one order, and decrements stock by requested quantity.
- The success body contains `id`, `product_id`, `quantity`, and `status = "created"`.
- `POST /api/orders/` with requested quantity greater than available stock returns `409` Problem Details with type `insufficient-stock`.
- Insufficient stock creates no order and leaves stock unchanged.
- Missing/non-JSON `Content-Type` returns `415` Problem Details and creates no order.
- Malformed JSON, missing `product_id`, missing `quantity`, non-integer values, or non-positive values return `400` Problem Details with type `invalid-order-request` and create no order.
- Unknown product returns `404` Problem Details and creates no order.
- A simulated optimistic version conflict reruns the domain decision; if stock is no longer sufficient, response is `409` with type `insufficient-stock` and no order is created.
- A simulated unresolved version conflict or SQLite write lock after retry returns `409` with type `inventory-conflict` and no order is created.

Why: these are the externally visible contract and consistency guarantees; implementation details such as repository classes are not acceptance-test targets.

## 9. Self-Consistency Check

- Domain ownership: stock sufficiency is decided in the `orders` domain using a translated inventory snapshot; persistence only guards concurrency and storage constraints.
- BC boundary: `orders` does not import `catalog` from domain/application code; only `DjangoProductInventoryPort`, `DjangoOrderRepository`, and `OrderModel` in infra touch `catalog.Product` or its FK.
- Reference integrity: `OrderModel.product` is an infra-level FK with `PROTECT`; the domain still carries only `product_id`.
- Transaction order: stock decrement succeeds before order persistence, so retry cannot duplicate orders.
- Naming: domain `Order` and ORM `OrderModel` remain distinct; repository/port names follow houserules §4.
- API status codes and DB behavior agree: invalid request data is 400, unsupported media type is 415, insufficient domain stock and unresolved inventory conflicts are both 409 with different Problem Details `type` values.
