# Pytest And Fixtures

Load this when writing pytest tests, fixtures, shared `conftest.py`, parametrized cases, markers, async tests, or pytest command guidance.

## Test Shape

- Use plain test functions or small `Test*` classes when grouping related behavior improves scanning.
- Name tests by behavior and expected result, not by implementation method.
- Use `assert` statements that automatically decide pass/fail; avoid print-based manual checks.
- Use `pytest.raises(ExpectedError, match=...)` for expected exceptions.
- Use `pytest.approx` for floating point comparisons.
- Use `pytest.mark.parametrize` when the same behavior must be checked across meaningful examples or boundary values.

## Fixtures

- Use fixtures for shared setup, teardown, and expensive resources.
- Use `yield` fixtures when teardown must always run after the test.
- Keep fixture scope as narrow as practical. Use `module` or `session` scope only for expensive resources with explicit isolation around each test.
- Put broadly shared fixtures in `tests/conftest.py`; put unit/integration-specific fixtures in nested `conftest.py` files near the tests that use them.
- Avoid fixture chains that hide the behavior under test. A fixture should make the test clearer than inline setup.

## Isolation Helpers

- Use `monkeypatch` for environment variables and small module-level seams.
- Use `tmp_path` for filesystem work so tests do not depend on the developer machine.
- Do not use real network calls in unit tests. Guard or mock them at the boundary.
- For time-dependent logic, prefer dedicated time tools from `test-doubles.md` instead of hand-patching `datetime` in many modules.

## Configuration And Markers

- Register custom markers in pytest config and enable strict marker checking when possible.
- Use markers such as `slow`, `integration`, `database`, and `e2e` to make test cost explicit.
- Use `skip` and `skipif` for unavailable environments.
- Use `xfail(strict=True)` only for a known, tracked bug or unsupported behavior; do not hide unexpected failures.
- Use marker selection commands such as `pytest -m "not slow"` or `pytest -m "database and not slow"` when reporting how to run subsets.
- For rare marker-driven setup, read marker arguments through `request.node.get_closest_marker(...)` inside a fixture. Prefer explicit fixture parameters when that is clearer.

## Plugins And Commands

- Use `pytest-asyncio` for `async def` tests and async fixtures; choose `auto` mode for asyncio-only projects and `strict` when multiple async frameworks coexist.
- Use `pytest-xdist` only when tests are isolated enough for parallel execution.
- Use `pytest-cov` when the project prefers direct pytest integration, such as `pytest --cov=src --cov-report=html tests/`, `pytest --cov=src --cov-fail-under=80 tests/`, or `pytest --cov=src --cov-branch tests/`.
- Use `pytest-randomly` to expose order dependence and record the seed when investigating failures.
- Use `pytest-timeout` for hanging tests, especially integration tests.
- Common commands:
  - `pytest tests/`
  - `pytest -k "name_fragment"`
  - `pytest -m "not slow"`
  - `pytest --lf`
  - `pytest -x --pdb`

Only report a command as passing if it was actually executed.
