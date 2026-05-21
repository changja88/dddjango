# Django API And Concurrency Tests

Load this when writing Django Ninja API contract tests, pytest-django database tests, idempotency tests, transaction/locking tests, or concurrency race tests.

## Django Ninja TestClient

- Use `ninja.testing.TestClient` for router/API-level request and response contracts when middleware and URL resolver behavior are not the subject.
- Assert public contract fields: status code, response body shape, Problem Details fields, headers, auth/permission outcome, pagination, filtering, and sorting.
- Do not assert private helper calls, exact ORM query strings, or service internals unless those are the public contract.
- Use the full Django test client or browser/e2e tooling only when middleware, URL routing, templates, sessions, CSRF, or browser behavior is the contract.

Minimal shape:

```python
from ninja.testing import TestClient

from orders.api import router


client = TestClient(router)


def test_order_detail_contract(order_factory):
    order = order_factory(status="paid")

    response = client.get(f"/orders/{order.id}")

    assert response.status_code == 200
    assert response.json()["status"] == "paid"
```

## pytest-django Database Selection

- Use `pytest.mark.django_db` or the `db` fixture for ORM tests that need ordinary database access and rollback isolation.
- Use `pytest.mark.django_db(transaction=True)` or `transactional_db` when commit/rollback effects, `transaction.on_commit`, row locks, separate connections, or lock timeouts are part of the behavior.
- Keep database tests marked explicitly so test cost and resource use are visible.
- Use testcontainers with the production-like database when backend-specific locking, isolation, indexes, constraints, or SQL behavior matters.

## API Contract Tests

- For successful writes, assert status code, response schema, persisted state, and important headers such as `Location` or idempotency metadata when the API defines them.
- For validation failures, assert the agreed error contract. If Problem Details is required, check `type`, `title`, `status`, `detail`, `instance`, and field-error extensions that matter.
- For auth and authorization, include unauthenticated, authenticated-but-forbidden, and allowed cases when the policy differs.
- For pagination and filtering, assert both response shape and selected items; do not only assert `200`.

## Idempotency Tests

- Same key and same payload should replay or return the same logical result without duplicating side effects.
- Same key and different payload should fail with the API's chosen conflict or validation response.
- Missing key should follow the API contract: allowed non-idempotent behavior, rejected request, or alternate deduplication.
- Assert durable state as well as response body, such as one order, one payment attempt, one outbox event, or one idempotency record.
- If idempotency storage has uniqueness constraints, cover them with database tests instead of relying only on mocked repositories.

## Transaction And Lock Tests

- Use transaction-capable tests for `select_for_update`, explicit commit/rollback behavior, and separate connection observations.
- Keep the domain rule covered by fast unit tests, then add integration tests for DB constraints, transaction boundaries, and lock behavior.
- For lock behavior, prefer deterministic coordination such as barriers, lock timeouts, `nowait=True`, or `skip_locked=True` over arbitrary sleeps.
- State backend assumptions in the test name or marker when the behavior depends on PostgreSQL, MySQL, or another specific database.

## Concurrency Tests

- Use concurrency tests only for invariants that can actually fail under racing writes, such as stock reservation, balance updates, duplicate create, or idempotency replay.
- Run concurrent attempts through the same public service/API path when possible; otherwise use the narrow repository/transaction boundary that owns the invariant.
- Assert exactly what must remain true after the race: one success, no negative stock, unchanged balance, unique row count, or a single emitted side effect.
- Investigate flaky results before adding `skip` or `xfail`; common causes are missing barriers, shared state, SQLite lock semantics, random order, and cleanup leakage.

## Escalation Boundaries

- Use `architecture-api` first when status codes, Problem Details, idempotency semantics, or response shape are undecided.
- Use `architecture-db` first when uniqueness, transaction isolation, locking, indexes, or idempotency persistence are undecided.
- Use Django implementation skills for production code changes; this skill owns tests, fixtures, factories, and test doubles unless assigned otherwise.
