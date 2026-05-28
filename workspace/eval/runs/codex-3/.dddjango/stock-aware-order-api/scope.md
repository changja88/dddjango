# Stock-aware order API scope

## User request

Build an API that creates an order when product stock is sufficient, decrementing stock atomically. If stock is insufficient, reject the request with HTTP 409 Conflict.

## Functional scope

- Add an externally callable order creation API.
- Accept a product identifier and requested quantity.
- When the product exists and current stock is greater than or equal to the requested quantity:
  - create an order record;
  - decrement the product stock by the requested quantity;
  - return a successful creation response.
- When stock is insufficient:
  - do not create an order;
  - do not decrement stock;
  - return HTTP 409 Conflict.

## Boundary assumptions

- Product already exists in the `catalog` app via `Product`.
- Quantity validation, product-not-found behavior, response body shape, and endpoint path will be finalized in design.
- No payment, customer account, shipping, cancellation, reservation, or order status workflow is included.
- Concurrency safety for stock decrement is in scope because stock and order creation must stay consistent.

## Existing project signal

- Current project has a single Django app, `catalog`.
- `catalog.models.Product` already contains `name`, `price`, and `stock`.
- No API router/view or order model exists yet.
- This change introduces both an external HTTP contract and database schema changes.

## Proposed placement

Selected: add order creation inside the existing `catalog` area.

## Active design lenses

- ddd: required for order creation and stock invariant.
- api: required because a new HTTP API contract is introduced.
- db: required because order persistence and transactional stock decrement are needed.
