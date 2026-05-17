---
name: implementation-cleancode
description: >
  Use for clean code review/refactoring: responsibility separation, naming, function shape, encapsulation, abstraction, SOLID, duplication, error handling, legacy code, code smells, fat models/views/routers, long functions, scattered logic, and maintainability findings. Use for 클린 코드, 코드 리뷰, 리팩터링, 책임 분리, 네이밍, 함수 분리, 비대한 모델, Fat View, 뷰/라우터 비즈니스 로직, 긴 함수, 흩어진 로직, 캡슐화, 추상화, 중복 제거, 레거시, 유지보수성 리뷰. Prefer architecture-implementation-patterns for pattern selection, layered/hexagonal, repository/UoW, outbox, or dependency direction; use clean-code for maintainability review of an already chosen structure. Prefer architecture-ddd/api/db for unresolved contracts, implementation-python for typing, Django skills for concrete code, and workflow-dddjango-subagents for composite work. Do not use for typo-only edits, formatter-only changes, or simple one-line explanations.
---

# Clean Code

Use this skill when the task is to review, refactor, or improve maintainability. The goal is code that is easier to understand and change while preserving behavior and domain intent.

## Routing

- If domain rules, invariants, aggregate ownership, or bounded context are unclear, use `architecture-ddd` before judging structure.
- If the main question is architecture/design pattern selection, use `architecture-implementation-patterns`; use this skill to judge whether an already proposed pattern reduces maintainability risk.
- If REST contract, DB schema, transaction, locking, migration rollout, or consistency decisions are unresolved, use `architecture-api` or `architecture-db` before treating the issue as only code quality.
- If Python typing, dataclasses, enums, Protocol, pydantic, Ruff, or typecheck compatibility are the main work, use `implementation-python` with this skill.
- If concrete Django ORM, migration, QuerySet, transaction, settings, or service/selector implementation details are primary, use `implementation-django`; keep this skill central for Fat Model, View/Router business-logic, responsibility, duplication, naming, or maintainability reviews.
- If API Router/Schema/status/error implementation is the main work, use `implementation-django-ninja`.
- If test fixtures, mocks, factories, coverage, or TDD method are the main work, use `implementation-test` or `implementation-tdd`.
- If the user explicitly asks for subagents, role decomposition, parallel review, or agent responsibility distribution in a Django task, use `workflow-dddjango-subagents` first.
- For a tiny naming question, typo, or formatter-only issue, answer or edit directly without DDD/workflow ceremony.

## Reference Loading

- Load only the reference file(s) relevant to the current clean-code task.
- Read [responsibility.md](references/responsibility.md) for change reasons, SRP, cohesion/coupling, responsibility-driven design, comments, and review output.
- Read [naming-functions.md](references/naming-functions.md) for naming, function design, arguments, command/query separation, side effects, formatting, and docstrings.
- Read [encapsulation-abstraction.md](references/encapsulation-abstraction.md) for information hiding, deep modules, object design, SOLID, DRY, errors, and dependency management.
- Read [legacy-review.md](references/legacy-review.md) for code smells, behavior-preserving refactoring, characterization tests, seams, sprout/wrap methods, and legacy risk handling.

## Runtime Rules

- For code review requests, lead with findings ordered by severity and cite concrete files/lines.
- For review-only requests or workflow Review Agent handoffs, produce findings/proposals only. For direct user/coordinator refactor requests that explicitly assign edits, make scoped behavior-preserving changes.
- Separate code by reason to change, not by file size or arbitrary layer count.
- Keep domain rules readable and protected; do not let style preferences outrank domain invariants.
- Prefer behavior-preserving small refactors. Add or use characterization tests before risky legacy changes when practical.
- Avoid speculative generality: add abstractions only when they remove real complexity, meaningful duplication, or a proven change axis.
- For major interface or architecture changes, compare at least two materially different options before choosing.
- Prefer clear names and simple functions, but keep public modules/classes deep enough that callers are not forced through implementation steps.
- Treat DRY as single-source business knowledge, not mechanical removal of every similar-looking line.
- Fix obvious nearby quality problems in the touched scope when doing so preserves behavior; if time or risk prevents cleanup, note the residual risk rather than silently leaving it.
- Report only verification actually run. If tests, linters, typechecks, or review subagents were not run, say so.
