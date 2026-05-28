# Stock-aware order API design spec

## Context and placement

- Bounded context placement: extend the existing `catalog` area selected in G0.
  - Why: the request couples product stock and order creation, and the user fixed placement to the existing catalog area; the design must not silently split a new order/sales context.
- Existing repository signal: the current project is a minimal Django 4.2 project with a single `catalog` app, `catalog.models.Product(name, price, stock)`, one initial migration, no API layer, and only placeholder tests.
- Layout decision: the current flat `startapp` layout is not a mature project convention, so new feature code should follow the dddjango standard structure for the `catalog` context. Preserve the Django app label `catalog` and the existing product table during migration.
  - Why: `discipline-houserules` §1 treats unorganized `startapp` layout as not enough convention to copy; standard layout keeps domain/application/infra/presentation responsibilities separated.

## Package and test structure

Apply the dddjango standard filetree to the `catalog` context:

```text
application/catalog/
├── catalog_api_router.py
├── domain_layer/
│   ├── order/
│   │   ├── order.py
│   │   ├── entity/
│   │   ├── value_object/
│   │   ├── repository/order_repository.py
│   │   ├── domain_service/
│   │   ├── event/
│   │   ├── specification/
│   │   └── exception.py
│   └── product/
│       ├── product.py
│       ├── entity/
│       ├── value_object/accepted_stock.py
│       ├── repository/product_repository.py
│       ├── domain_service/
│       ├── event/
│       ├── specification/
│       └── exception.py
├── application_layer/
│   ├── create_order/
│   │   ├── command/create_order_app.py
│   │   └── dto/create_order_command.py
│   └── unit_of_work.py
├── infra_layer/
│   ├── django_catalog/
│   │   ├── apps.py
│   │   ├── models/product_model.py
│   │   ├── models/order_model.py
│   │   ├── migrations/
│   │   └── admin/
│   └── repository/
│       ├── product_repository.py
│       ├── order_repository.py
│       └── catalog_unit_of_work.py
├── presentation_layer/
│   ├── api/create_order/api_orders.py
│   └── schema/
│       ├── schema_in.py
│       ├── schema_out.py
│       └── error_out.py
└── test/
    ├── unit/
    ├── integration/
    └── e2e/
```

Standard invariants that apply to this slice:

- Keep an `application/` container even for this single feature app.
- Keep four physical layers: `domain_layer`, `application_layer`, `infra_layer`, `presentation_layer`.
- Organize domain by concept first (`order`, `product`) and by kind second (`entity`, `value_object`, `repository`, etc.).
- Keep kind folders as folders, even when initially empty; do not flatten to files like `repository.py`.
- The Django app lives at `application.catalog.infra_layer.django_catalog`; `CatalogConfig.label = "catalog"` so existing app label semantics are retained.
- Do not place new ORM models in an app-root `models.py`.
- ORM model class names use `<Name>Model`; domain objects use bare names. Existing `Product` should be migrated to `ProductModel` without renaming the existing `catalog_product` table.
- Repository abstractions use concept + role suffix: `OrderRepository`, `ProductRepository`.
- Implementations use technology/source qualifier + full abstraction base name: `DjangoOrderRepository`, `DjangoProductRepository`, `DjangoCatalogUnitOfWork`.
- No `Interface` or `Impl` suffixes. File names are unabbreviated, such as `order_repository.py`.

Migration safety note:

- Preserve the existing `catalog` app label and `catalog_product` table name. If the physical app path and ORM class name are changed, the migration must be state-safe and must not drop/recreate the product table.
  - Why: DB rollout safety in `architecture-db` §11 and houserules ORM naming both matter; preserving the table avoids destructive schema churn while moving toward the standard layout.
- Before adding or preserving `stock >= 0` and `price >= 0` check constraints, verify existing `catalog_product` rows do not violate them.
- If negative `stock` or `price` values exist, add a data migration or manual cleanup step before the constraint migration.
- PostgreSQL rollout should prefer adding check constraints with low-lock risk, such as `NOT VALID` followed by `VALIDATE CONSTRAINT`, when operating on non-trivial data volume.
- SQLite may rebuild tables for constraint changes; this is acceptable for the current small project only if the migration preserves all existing product rows and avoids destructive drop/recreate behavior from the application's perspective.

Tests:

- Domain and application unit tests: `application/catalog/test/unit/`.
- DB repository and HTTP API tests: `application/catalog/test/integration/`.
- End-to-end tests are optional for this slice; create `e2e/` only if a full server-level flow is added.
  - Why: `discipline-houserules` §1.3 requires semantic grouping instead of a flat `test_*.py` list.

## Domain design

### Ubiquitous language

- Product: an item in the catalog with a current stock count and price.
- Stock: available units that may be decremented when an order is accepted.
- Accepted order record: a created catalog purchase record for one product and a requested quantity.
- Order: in this slice, shorthand for the accepted order record created together with catalog stock decrement.
- Sufficient stock: product stock is greater than or equal to requested quantity at the moment of acceptance.
- Insufficient stock: product exists but current stock is lower than requested quantity.
- Stock acceptance: the domain operation that validates sufficient stock, decrements accepted stock, and returns `AcceptedStock`, the product data needed to create the accepted order record.

If payment, shipping, cancellation, customer account ownership, or a long-lived order lifecycle is added later, revisit whether this `Order` still belongs inside `catalog` or should move to a separate sales/order bounded context.

### Aggregates and invariants

- `Product` aggregate owns the stock invariant.
  - Invariant: stock must never become negative.
  - Behavior: decrement stock only by a positive quantity and only when stock is sufficient.
  - Why: `architecture-ddd` §3.3 says true invariants belong inside the aggregate boundary.
- `Order` aggregate records an accepted order.
  - Invariant: quantity must be a positive integer.
  - Invariant: an order references exactly one product id.
  - Invariant: `unit_price` is captured from the product at acceptance time.
  - No status workflow is introduced.
  - Why: scope excludes payment, shipping, cancellation, reservation, and order status; a created order is only the accepted purchase record.
- Cross-aggregate consistency:
  - Creating an order and decrementing product stock must happen in one database transaction.
  - The application service may coordinate `Product` and `Order` in one transaction for this simple same-database case.
  - Why: `architecture-ddd` §3.3 keeps aggregates small, and rule 4 permits consistency outside an aggregate through process coordination; this does not change the bounded-context placement.

### Application flow

`CreateOrderApp` accepts `CreateOrderCommand(product_id, quantity)`:

1. Validate command-level shape: integer `product_id`, integer `quantity`, `quantity > 0`.
2. Start a catalog unit of work.
3. Ask `ProductRepository.accept_stock(product_id, quantity)` to perform stock acceptance in domain terms.
4. If no product exists, raise `ProductNotFound`.
5. If product exists but stock is insufficient, raise `InsufficientStock`.
6. On success, receive an `AcceptedStock` result containing `product_id`, `accepted_quantity`, and `unit_price`.
7. Build an `Order` from the accepted-stock result, not from a separate price lookup or caller-provided price.
8. Persist the order through `OrderRepository`.
9. Commit the unit of work and return the created order result.

`ProductRepository.accept_stock` is a domain repository port, not a raw persistence command. Its implementation may use a conditional database update for concurrency, but the port semantics preserve the `Product` aggregate behavior: accept a positive stock decrement only when the aggregate has sufficient stock, and return the product snapshot needed for order creation. `AcceptedStock` is immutable domain/application data with:

- `product_id`
- `accepted_quantity`
- `unit_price`

Domain events:

- No domain event is introduced in this slice.
  - Why: no downstream notification, external side effect, or eventual-consistency workflow is in scope; `architecture-ddd` §3.7 requires event timing only when events are adopted.

## API contract

### Endpoint

- Method and path: `POST /api/orders/`
- Resource: `orders`
- Authentication/authorization: none in this slice.
- Request `Content-Type`: `application/json`
- Requests with any other content type return `415 Unsupported Media Type` Problem Details.
- Response media type: JSON for success, RFC 9457 Problem Details for errors.
- `Accept` negotiation is not strict in this slice: the API always returns JSON-compatible responses and does not define a separate `406 Not Acceptable` contract.
- Versioning: no URL version for this initial project API; future breaking changes must introduce a new path prefix such as `/api/v2/`.
  - Why: `architecture-api` §3 prefers noun resources and §10 requires an explicit version strategy; this minimal project has no existing API version scheme.

### Request body

```json
{
  "product_id": 1,
  "quantity": 2
}
```

Validation rules:

- `product_id` is required and must be a positive integer.
- `quantity` is required and must be a positive integer.
- Unknown fields are rejected as validation errors with `400 Bad Request`.

### Success response

Status: `201 Created`

```json
{
  "id": 10,
  "product_id": 1,
  "quantity": 2,
  "unit_price": 1500,
  "created_at": "2026-05-28T10:30:00Z"
}
```

- Do not include a `Location` header unless a read endpoint for the created order is implemented in the same slice.
- `unit_price` is a non-negative integer copied from `Product.price` at acceptance time.

### Error responses

All errors use `application/problem+json` and the same base Problem Details shape:

```json
{
  "type": "urn:problem:catalog:invalid-order-request",
  "title": "Invalid order request",
  "status": 400,
  "detail": "Request body is invalid."
}
```

- Required fields for every problem response: `type`, `title`, `status`, `detail`.
- `instance` is not used in this slice and should be omitted.
- Validation errors may include an `errors` extension with the shape `{ "field_name": ["message", "..."] }`.
- Non-field validation errors use the key `non_field_errors`.

Validation failure:

- Status: `400 Bad Request`
- Type: `urn:problem:catalog:invalid-order-request`
- Title: `Invalid order request`
- Detail: request body is invalid.
- Include `errors` for missing fields, type errors, non-positive values, and unknown fields.

Unsupported media type:

- Status: `415 Unsupported Media Type`
- Type: `urn:problem:catalog:unsupported-media-type`
- Title: `Unsupported media type`
- Detail: request content type must be `application/json`.

Product not found:

- Status: `404 Not Found`
- Type: `urn:problem:catalog:product-not-found`
- Title: `Product not found`
- Detail: product does not exist.

Insufficient stock:

- Status: `409 Conflict`
- Type: `urn:problem:catalog:insufficient-stock`
- Title: `Insufficient stock`
- Detail: request cannot be accepted because available stock is lower than requested quantity.

Idempotency policy:

- No `Idempotency-Key` storage is introduced in this slice.
- Repeating the same `POST /api/orders/` request is a new order attempt and may decrement stock again.
- Clients must treat retries after ambiguous network failure as unsafe unless a later idempotency feature is added.
  - Why: `architecture-api` §13 requires the policy to be explicit; durable replay storage would add a separate persistence concern outside the approved scope.

OpenAPI:

- The endpoint contract above must be represented in OpenAPI if the implementation introduces an OpenAPI-capable API layer.
- Acceptance tests are the minimum executable contract for this slice.

## Data design

### Tables and constraints

Existing product table:

- Preserve table: `catalog_product`
- Fields:
  - `id`
  - `name`
  - `price`
  - `stock`
- Add or preserve constraints:
  - `stock >= 0`
  - `price >= 0`
- `price` is a non-negative integer; zero-price products are allowed because the existing product contract uses `price >= 0`.

New order table:

- Table: `catalog_order`
- ORM class: `OrderModel`
- Fields:
  - `id` big auto primary key
  - `product_id` foreign key to `catalog_product(id)`, `on_delete=PROTECT`
  - `quantity` positive integer
  - `unit_price` non-negative integer captured from `Product.price` during stock acceptance
  - `created_at` timezone-aware timestamp set on creation
- Constraints:
  - `quantity > 0`
  - `unit_price >= 0`
- Indexes:
  - use the Django foreign-key index on `product_id`; do not create a duplicate explicit index for the same column.
  - index on `created_at` only if list/query endpoints are later added; not required for this write-only slice.

No order status column is added.

### Transaction and risky write strategy

This feature is a Risky Write because it changes inventory and creates an order.

- Transaction owner: `CreateOrderApp` through `CatalogUnitOfWork`.
- Transaction boundary: stock decrement and order insert are committed or rolled back together.
- Isolation target: database default read committed behavior where available; do not require serializable isolation.
- Locking/write strategy: conditional `UPDATE`, not `select_for_update`.

Required stock decrement semantics:

```sql
UPDATE catalog_product
SET stock = stock - :quantity
WHERE id = :product_id
  AND stock >= :quantity;
```

- If affected rows = 1: stock was sufficient and is now decremented.
- If affected rows = 0 and product exists: insufficient stock.
- If affected rows = 0 and product does not exist: product not found.
- The successful stock acceptance path must capture `Product.price` after the conditional update succeeds and before the unit of work commits.
- Do not read the price before the stock decrement as the source for `unit_price`; the accepted-stock result is produced only after the write has proven stock sufficiency.

Engine-specific behavior:

- SQLite: `select_for_update` is effectively unavailable for row locking; a single conditional `UPDATE` is the portable guard, and the transaction must avoid read-then-write stock decisions.
- SQLite-compatible price capture: after the conditional `UPDATE` affects one row, perform a `SELECT price FROM catalog_product WHERE id = :product_id` inside the same unit of work before inserting the order.
- PostgreSQL: the conditional `UPDATE` obtains the row lock for the write and rechecks the predicate at update time under normal OLTP isolation; it prevents concurrent oversell without serializable isolation.
- PostgreSQL-preferred price capture: use `UPDATE ... RETURNING price` when the implementation path supports it; otherwise use the same post-update in-transaction select fallback.

Why: `architecture-db` §9.6 requires transaction owner, locking strategy, isolation/retry, and tests for Risky Writes. Conditional update plus DB checks protects the invariant across SQLite development and PostgreSQL production, while `select_for_update` would leave a lock gap in SQLite.

### Repository responsibilities

- `ProductRepository` exposes `accept_stock(product_id, quantity)` in domain terms.
  - It must not expose raw ORM query details to the application layer.
  - It maps conditional-update outcomes to `ProductNotFound` or `InsufficientStock`.
  - It returns accepted-stock data with `product_id`, `accepted_quantity`, and `unit_price` after a successful decrement.
- `OrderRepository` persists accepted `Order` records.
- `CatalogUnitOfWork` owns transaction commit/rollback and supplies repositories.

No ACL is needed.

- Why: `Product` and `Order` are inside the same selected `catalog` bounded context; ACL/OHS is for crossing bounded-context boundaries, not for coordinating two aggregates in the same context.

## External observable behavior

Acceptance tests should verify:

1. `POST /api/orders/` with existing product and sufficient stock returns `201`, creates one order, and decrements stock by requested quantity.
2. `POST /api/orders/` with existing product and insufficient stock returns `409`, creates no order, and leaves stock unchanged.
3. `POST /api/orders/` with unknown product returns `404`, creates no order, and changes no stock.
4. Invalid request shape, non-positive quantity, or unknown request fields return `400` Problem Details.
5. Non-JSON request content returns `415` Problem Details.
6. Two competing order attempts cannot reduce product stock below zero; only attempts covered by available stock may create orders.
7. Successful order creation stores `unit_price` from the accepted-stock result captured in the same transaction as the stock decrement.

## Self-consistency check

- Domain ownership is consistent: `Product` owns the stock invariant; `Order` records accepted orders.
- API and domain errors align: insufficient stock maps to `409`, missing product maps to `404`, invalid input maps to `400`, and unsupported media type maps to `415`.
- DB strategy supports the domain invariant and accepted order record: conditional update and `stock >= 0` check prevent negative stock across supported engines, and price is captured only after successful stock acceptance inside the unit of work.
- Package names align with houserules: abstractions are `OrderRepository`, `ProductRepository`, and implementations are `DjangoOrderRepository`, `DjangoProductRepository`, `DjangoCatalogUnitOfWork`.
- The selected placement remains `catalog`; no new bounded context is introduced.
