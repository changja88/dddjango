# Scope: order-stock-api

## User request

재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.

## Current project context

- Django 4.2 project with one existing app: `catalog`.
- `catalog.Product` currently has `name`, `price`, and `stock`.
- There is no existing order app, order model, API endpoint, or API framework.
- `PROMPT.md` fixes this smoke-test run's choices:
  - Place the feature in a new independent `orders` bounded-context app.
  - Use active lenses `ddd + db + api`.
  - Keep scope to a single order for one product and quantity.
  - Use plain Django `JsonResponse`.
  - Use Django's built-in test runner.

## Proposed behavior boundary

- Add an HTTP API that creates one order for one product and one requested quantity.
- If requested quantity is available, create the order and decrement product stock in the same transactional flow.
- If requested quantity exceeds current stock, reject the request with HTTP 409 and do not create an order or change stock.
- Keep this feature intentionally small: no multi-line orders, payment, customer account, reservation, idempotency key, or external integration.

## Proposed placement

Use a new independent `orders` app/bounded context, reusing `catalog.Product` as the inventory source for this smoke test.

## Proposed active design lenses

- ddd: order creation policy and inventory invariant.
- api: new HTTP endpoint, request/response shape, and 409 conflict behavior.
- db: order persistence, stock update transaction, migrations, and consistency constraints.
