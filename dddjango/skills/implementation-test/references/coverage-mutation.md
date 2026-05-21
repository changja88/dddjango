# Coverage, Mutation, And Test Quality

Load this when choosing test levels, integration tools, coverage, mutation testing, multi-environment testing, quality review, anti-pattern cleanup, or debugging commands.

## Test Strategy

- Favor many fast unit tests, fewer integration tests, and very few end-to-end tests.
- Use small tests for pure domain rules and value objects.
- Use integration tests for ORM mapping, transactions, constraints, query performance, external adapters, and persistence behavior.
- Use Django Ninja `TestClient` tests for request/response shape, status codes, Problem Details, auth, pagination, and filtering.
- For risky write behavior, include replay/idempotency, uniqueness, transaction/locking, or concurrency tests when those risks affect the invariant.
- Use the SMURF trade-offs to explain cost: speed, maintainability, utilization, reliability, and fidelity.
- Classify tests by resource use as well as purpose: small tests avoid I/O and sleeps; medium tests may use local processes; large tests may use network or multiple services.

## Integration With Real Services

- Use testcontainers when fidelity matters more than speed, especially for PostgreSQL, Redis, or multiple services.
- Scope containers at `session` or `module` level when startup is expensive, then isolate each test with transactions, cleanup fixtures, or fresh namespaces.
- Do not use real external SaaS services in repeatable automated tests unless the test is explicitly large/e2e and isolated from normal CI.

## Coverage And Multi-Environment Runs

- Use branch coverage when branch behavior matters.
- Exclude migrations, tests, `conftest.py`, abstract methods, and type-check-only branches only with a clear reason.
- Put coverage config in `pyproject.toml` when the project already centralizes tool config: `source`, `branch`, `omit`, `fail_under`, `show_missing`, and justified `exclude_lines`.
- Use `coverage run -m pytest`, `coverage report`, `coverage html`, `coverage xml`, and `coverage combine` as appropriate.
- Use `pytest --cov=src`, `--cov-report`, `--cov-fail-under`, and `--cov-branch` when the project uses `pytest-cov` rather than direct coverage.py commands.
- Treat `fail_under` as a floor, not as proof that critical behavior is tested.
- Use tox for straightforward multi-version or dependency matrices. Use nox when Python code is useful for dynamic session setup, Django-version parametrization, or reusable local workflows.
- Include lint/typecheck sessions in tox/nox only when the project actually runs those gates; do not imply they passed unless executed.

## Mutation Testing

- Use mutation testing to find assertions that miss boundary conditions or equivalent behavior.
- Start with high-value modules; full-suite mutation can be expensive.
- For mutmut, use targeted runs such as `mutmut run --paths-to-mutate "src/" --tests-dir "tests/"`, then inspect with `mutmut results` and `mutmut show <id>`.
- Interpret result states before editing tests: killed is useful signal, survived means the tests missed a meaningful behavior or the mutant is equivalent, timeout/suspicious needs manual inspection.
- Inspect survived mutants and add meaningful tests only when they represent a real missed behavior.
- Boundary cases such as `>`, `>=`, `==`, and off-by-one transitions are common mutation targets.
- Add tests for the missing behavior, not assertions that merely pin the current implementation.
- Do not chase 100% mutation score blindly; analyze whether the surviving mutant is meaningful.

## Test Quality Review

- FIRST: tests should be fast, independent, repeatable, self-validating, and timely.
- AAA: keep Arrange, Act, and Assert clear. Prefer one Act per test; multiple related asserts are fine for the same Act.
- Avoid tests coupled to private methods, internal algorithms, exact SQL strings, or incidental HTML unless those are the public contract.
- Watch for empty tests, weak assertions, excessive setup, unrelated asserts, hidden shared state, over-mocking, local-only assumptions, and flaky timing.
- For flaky tests, identify the cause first: timing, ordering, shared state, external dependency, filesystem/environment leak, random seed, or database cleanup.
- Do not silence a flaky test with skip or xfail unless the cause, scope, and follow-up are explicit.
- Debug with `pytest --pdb`, `pytest --lf --pdb`, `pytest -x --pdb`, targeted `-k`, and recorded random seeds.
- When a higher-level test finds a bug, add the smallest lower-level regression test that reproduces the defect before fixing it.
