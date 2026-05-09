---
name: implementation-tdd
description: Use for TDD methodology: test list, failing tests before implementation, Red-Green-Refactor, Inside-Out vs Outside-In, acceptance/unit loops, boundary cases, refactoring checkpoints, and AI-assisted TDD. Use for TDD, 실패 테스트, 테스트 먼저, Red-Green-Refactor, 쿠폰 정책 TDD. Prefer workflow-dddjango-subagents for composite/subagent Django work, implementation-test for pytest fixtures/mocks/factories, and architecture-ddd when domain rules or invariants are unclear.
---

# TDD Implementation

Use this skill to turn behavior into tests before implementation. TDD here means using tests as executable specification, feedback, and refactoring protection.

## Routing

- If domain rules, invariants, aggregate ownership, or ubiquitous language are unclear, use `architecture-ddd` before writing domain tests.
- If the main work is pytest fixtures, mocks, factories, property-based tests, coverage, mutation testing, or testcontainers, use `implementation-test`.
- If the main work is Django ORM/migrations/services or Django Ninja API implementation, use the relevant implementation skill after the test target is clear.
- If the user explicitly asks for subagents, role decomposition, parallel review, or responsibility splitting in a Django task, use `workflow-dddjango-subagents` first.
- For a tiny explanation of TDD terminology, answer directly without role maps or full workflow ceremony.

## Reference Loading

- Read [red-green-refactor.md](references/red-green-refactor.md) for the core cycle, red/green/refactor rules, green strategies, and honest execution reporting.
- Read [inside-out-outside-in.md](references/inside-out-outside-in.md) for classic vs London school, state vs behavior verification, double-loop TDD, and approach selection.
- Read [test-list.md](references/test-list.md) for test lists, starting tests, boundary cases, AAA, test quality, and test smell prevention.
- Read [ai-assisted-tdd.md](references/ai-assisted-tdd.md) for AI-assisted TDD workflow, prompt-as-test thinking, validation, and false claim prevention.

## Runtime Rules

- Start with a test list for behavior, boundary cases, and known risks before implementation.
- Write or propose the next failing test before production code unless the user asks for explanation only or the workspace is read-only.
- When working inside a composite workflow, state the test files or test cases the Test Agent should own.
- Confirm Red before Green when actually running tests; if tests were not run, say they were written/planned but not executed.
- Green means the smallest implementation that passes the current test, not the final architecture.
- Refactor only while tests are green; preserve externally visible behavior unless the user requests a behavior change.
- Prefer output/state verification for domain logic; use behavior verification/mocks mainly for external roles and boundaries.
- Keep pytest fixture/mock/factory mechanics in `implementation-test`; this skill owns the TDD sequence and test selection.
- Report only verification actually run. Never claim failing tests, passing tests, or subagent review happened without evidence.
