# Test List

Use this reference for test lists, starting tests, boundary cases, AAA, test quality, and test smell prevention.

## Test List

- Start by listing behavior, examples, boundaries, and risk cases.
- Choose the next test that teaches something new and feels implementable.
- Start with a simple case where the operation does little or nothing when that gives fast feedback.
- Include regression tests for reported bugs before fixing them.
- Keep tests independent: they must not depend on execution order, shared mutable state, or data leaked from earlier tests.

## Test Shape

- Think Assert First: decide the observable outcome, then derive setup.
- Keep final test code in Arrange-Act-Assert order.
- Use meaningful test data where differences communicate intent.
- Name tests by unit, condition, and expected behavior.
- Prefer one clear reason to fail per test.

## Quality And Smells

- Good tests balance regression protection, refactoring resistance, fast feedback, and maintainability.
- Avoid assertion roulette, erratic tests, fragile tests, slow tests, manual intervention, obscure tests, conditional test logic, magic data, and eager tests.
- Boundary cases belong in the test list when they affect domain policy or API contract.
