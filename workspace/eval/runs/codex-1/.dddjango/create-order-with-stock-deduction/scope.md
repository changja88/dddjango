# Scope: create order with stock deduction

## User request

재고가 있을 때만 주문을 생성하고 재고를 차감하는 기능.

## Current project context

- Django 4.2 project rooted at `/Users/hyun/Desktop/dddjango-smoke`.
- Existing app: `catalog`.
- Existing model: `catalog.models.Product(name, price, stock)`.
- No existing order model, service layer, API route, or non-empty tests.
- The directory is not a Git repository.

## Proposed scope

- Add an order creation capability for a single product and quantity.
- Create an order only when the selected product has enough stock.
- Deduct the ordered quantity from product stock in the same transactional operation.
- Preserve stock and create no order when stock is insufficient.
- Keep this as domain/application behavior first; do not add a new HTTP API unless requested.

## Out of scope

- Payment, shipment, customer accounts, carts, multiple products per order, discounts, refunds, reservations, and backorders.
- Public API endpoint design.

## Placement decision for G0

This touches the existing `catalog` area because `Product.stock` is already there, but it introduces an order concept.

Options for approval:

1. Add it inside existing `catalog` for the smallest project-local change.
2. Create a separate order-oriented app/boundary for clearer future growth.
3. Let the design architect decide.

Default proposal: option 1, because the project is currently minimal and the feature has one product/stock invariant.

## Active design lenses

- ddd: active, because the order/stock invariant is a domain rule.
- db: active, because an `Order` persistence model and transaction boundary are expected.
- api: inactive, because no external HTTP contract is requested.
