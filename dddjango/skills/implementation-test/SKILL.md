---
name: implementation-test
description: >
  Use for Python/Django test implementation and review: pytest, fixtures/conftest.py, parametrization, assertions, test doubles, fake/mock/stub/spy/dummy, factory_boy/Faker, Hypothesis property tests, time/HTTP mocking, testcontainers, coverage, mutation testing, BDD, flaky tests, Django Ninja TestClient/API contract tests, idempotency/concurrency tests. Use for 테스트 코드 작성/리뷰, pytest 픽스처, mock/모킹, 테스트 더블, 팩토리, 커버리지, 뮤테이션 테스트, 속성 기반 테스트, 중복 요청/동시성 테스트, flaky/불안정 테스트. Prefer workflow-dddjango-subagents for composite/risky/subagent Django work, implementation-tdd for Red-Green-Refactor flow, and architecture-ddd/architecture-db/architecture-api when invariants, data constraints, or REST contracts are unclear. Do not use for simple explanations, answer-only requests, or pure TDD method planning without test implementation details.
---

# Test Implementation

Use this skill to write or review concrete pytest tests, fixtures, factories, doubles, property tests, and test quality checks. The test should verify behavior, invariants, and contracts rather than implementation details.

## Routing

- If the user asks for Red-Green-Refactor, failing-test-first sequencing, or TDD coaching, use `implementation-tdd`; use this skill for the pytest mechanics behind that flow.
- If domain invariants, policy ownership, aggregates, or bounded context language are unclear, use `architecture-ddd` before locking in assertions.
- If DB schema, constraints, transactions, locking, query performance, or rollout behavior is unresolved, use `architecture-db` before encoding those assumptions in tests.
- If REST resources, status codes, Problem Details, pagination, idempotency, or OpenAPI contract behavior is unresolved, use `architecture-api` before writing API contract assertions.
- If the work is Django ORM, migration, service, selector, or Django Ninja implementation, use the relevant implementation skill for production code and this skill for `tests/**`, `conftest.py`, factories, and doubles.
- If the work is composite or risky across domain, DB, API, Django implementation, and tests, or the user explicitly asks for subagents, role decomposition, parallel review, or agent responsibility distribution in a Django task, use `workflow-dddjango-subagents` first.
- For a small assertion, fixture, import ordering, typo, or pytest command explanation, answer directly without DDD or workflow ceremony.

## Reference Loading

- Load only the reference file(s) relevant to the current test implementation task.
- Read [pytest-fixtures.md](references/pytest-fixtures.md) for pytest structure, assertions, fixtures, `conftest.py`, parametrization, markers, plugins, async tests, and execution commands.
- Read [test-doubles.md](references/test-doubles.md) for dummy/stub/spy/mock/fake selection, output/state/communication verification, `Mock`, `AsyncMock`, `seal`, monkeypatch, time mocking, and HTTP mocking.
- Read [factories-property-tests.md](references/factories-property-tests.md) for factory_boy, Faker, traits, Django factories, Hypothesis, stateful property tests, and pytest-bdd.
- Read [coverage-mutation.md](references/coverage-mutation.md) for test pyramid strategy, testcontainers, coverage.py, tox/nox, FIRST, AAA, anti-patterns, mutation testing, and debugging.

## Runtime Rules

- Choose the smallest test level that protects the behavior: fast domain unit tests first, integration tests for ORM/transactions/constraints/query performance, and Django Ninja `TestClient` tests for request/response contracts.
- Prefer output and state verification for domain logic. Use communication verification and mocks mainly for external systems, adapters, or collaboration that must be observed.
- Do not mock every collaborator by default. Use fakes for useful in-memory behavior and mocks for external roles such as payment, email, HTTP, or SDK boundaries.
- Keep tests independent, repeatable, self-validating, and readable. Isolate time, randomness, filesystem, environment, network, and database state.
- Put shared setup in fixtures or factories only when it makes the test clearer; avoid hidden fixture chains that obscure the behavior under test.
- Use property-based tests for invariants over broad input spaces and example tests for named boundary cases.
- Treat coverage and mutation scores as signals to inspect, not proof that behavior is fully tested.
- In composite workflows, own `tests/**`, `conftest.py`, and factory files; coordinate with implementation skills without changing production code unless assigned.
- Report only tests, coverage, mutation checks, or subagent reviews that were actually run. If a command was not run, state that directly.
