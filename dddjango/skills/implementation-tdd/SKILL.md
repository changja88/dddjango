---
name: implementation-tdd
description: >
  Use for TDD methodology: test list, failing tests before implementation, Red-Green-Refactor, Inside-Out vs Outside-In, acceptance/unit loops, boundary cases, refactoring checkpoints, state vs behavior verification choice, mock-role guidance, BDD/ATDD relationship, and AI-assisted TDD. Use for TDD/테스트 주도 개발/테스트주도 개발, 테스트 목록, 실패 테스트/실패하는 테스트, 테스트 먼저, Red-Green-Refactor/레드-그린-리팩터, 경계값 테스트, 쿠폰 정책 TDD. Prefer workflow-dddjango-subagents for composite/risky/subagent Django work, implementation-test for pytest fixture/mock/factory mechanics, property-based tests, coverage, mutation testing, testcontainers, and pytest-bdd/Gherkin mechanics, architecture-api or architecture-db when API/DB contracts are unclear, and Django implementation skills when ORM/services/API code is the main work. Do not use for simple answer-only explanations or detailed test-tool implementation without a TDD workflow request.
---

# TDD Implementation

Use this skill to turn behavior into tests before implementation. TDD here means using tests as executable specification, feedback, and refactoring protection.

## Routing

- If API contract, DB constraint, transaction, locking, migration rollout, or consistency decisions are unclear, use `architecture-api` or `architecture-db` before locking test expectations.
- If domain policy, invariant, use case, or behavior ownership is unclear, use `architecture-ddd` before fixing expected outcomes in tests.
- If security or performance risk is the main concern, use the relevant architecture, implementation, or workflow skill for that analysis; this skill only keeps the TDD loop honest around agreed behavior.
- If legacy refactoring strategy, characterization scope, or code smell cleanup is the main work, use `implementation-cleancode` with this skill only for the TDD/characterization sequence.
- If the main work is pytest fixtures, mocks, factories, property-based tests, coverage, mutation testing, testcontainers, or pytest-bdd/Gherkin mechanics, use `implementation-test`.
- If the main work is Django ORM/migrations/services or Django Ninja API implementation, use the relevant implementation skill after the test target is clear.
- If the work is composite or risky across domain, DB, API, Django implementation, and tests, or the user explicitly asks for subagents, role decomposition, parallel review, or agent responsibility distribution in a Django task, use `workflow-dddjango-subagents` first.
- For a tiny explanation of TDD terminology, answer directly without role maps or full workflow ceremony.

## Reference Loading

- Load only the reference file(s) relevant to the current TDD task.
- Read [red-green-refactor.md](references/red-green-refactor.md) for the core cycle, red/green/refactor rules, green strategies, and honest execution reporting.
- Read [inside-out-outside-in.md](references/inside-out-outside-in.md) for classic vs London school, state vs behavior verification, double-loop TDD, and approach selection.
- Read [test-list.md](references/test-list.md) for test lists, starting tests, boundary cases, AAA, test quality, and test smell prevention.
- Read [bdd-atdd.md](references/bdd-atdd.md) for the TDD, ATDD, and BDD relationship and pytest-bdd/Gherkin handoff boundary.
- Read [ai-assisted-tdd.md](references/ai-assisted-tdd.md) for AI-assisted TDD workflow, prompt-as-test thinking, validation, and false claim prevention.

## Runtime Rules

- Start with a test list for behavior, boundary cases, and known risks before implementation.
- Treat boundary examples as prompts to expand the test list; for validity windows include the accepted boundary and the day after expiration rejected. A rejection on another axis does not cover the boundary. Use `references/test-list.md` for detailed independent-axis and nearest outside/complement cases.
- For ambiguous policy tests, separate confirmed behavior tests and unresolved domain decisions before locking expectations; route unresolved policy or invariant ownership to `architecture-ddd`.
- Write or propose the next failing test before production code unless the user asks for explanation only or the workspace is read-only.
- When working inside a composite workflow, state the test files or test cases the Test Agent should own.
- Confirm Red before Green when actually running tests; if tests were not run, say they were written/planned but not executed.
- Call a cycle Red-Green only when a failing test run was captured before the passing run. If existing production behavior already passes newly added tests, report it as regression or characterization coverage rather than a completed Red step.
- Green means the smallest implementation that passes the current test, not the final architecture.
- Refactor only while tests are green; preserve externally visible behavior unless the user requests a behavior change.
- Prefer output/state verification for domain logic; use behavior verification/mocks mainly for external roles and boundaries.
- Keep pytest fixture/mock/factory mechanics in `implementation-test`; this skill owns the TDD sequence, test selection, and state-vs-behavior verification choice.
- Report only verification actually run. Never claim failing tests, passing tests, or subagent review happened without evidence.
