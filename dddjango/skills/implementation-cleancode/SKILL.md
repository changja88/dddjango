---
name: implementation-cleancode
description: Use for clean code review/refactoring: responsibility separation, naming, functions, comments/docstrings, encapsulation, abstraction, SOLID, duplication, error handling, legacy code, code smells, and maintainability findings. Use for 코드 리뷰, 리팩터링, 책임 분리, 품질 개선. Prefer architecture-ddd for domain modeling, implementation-python for Python typing, implementation-django for Django ORM/migrations, and workflow-dddjango-subagents for composite/subagent work.
---

# Clean Code

Use this skill when the task is to review, refactor, or improve maintainability. The goal is code that is easier to understand and change while preserving behavior and domain intent.

## Routing

- If domain rules, invariants, aggregate ownership, or bounded context are unclear, use `architecture-ddd` before judging structure.
- If Python typing, dataclasses, enums, Protocol, pydantic, Ruff, or typecheck compatibility are the main work, use `implementation-python` with this skill.
- If Django ORM, migrations, QuerySets, transactions, settings, or service/selector implementation are the main work, use `implementation-django`.
- If API Router/Schema/status/error implementation is the main work, use `implementation-django-ninja`.
- If test fixtures, mocks, factories, coverage, or TDD method are the main work, use `implementation-test` or `implementation-tdd`.
- If the user explicitly asks for subagents, role decomposition, parallel review, or responsibility splitting in a Django task, use `workflow-dddjango-subagents` first.
- For a tiny naming question, typo, or formatter-only issue, answer or edit directly without DDD/workflow ceremony.

## Reference Loading

- Read [responsibility.md](references/responsibility.md) for change reasons, SRP, cohesion/coupling, responsibility-driven design, comments, and review output.
- Read [naming-functions.md](references/naming-functions.md) for naming, function design, arguments, command/query separation, side effects, formatting, and docstrings.
- Read [encapsulation-abstraction.md](references/encapsulation-abstraction.md) for information hiding, deep modules, object design, SOLID, DRY, errors, and dependency management.
- Read [legacy-review.md](references/legacy-review.md) for code smells, behavior-preserving refactoring, characterization tests, seams, sprout/wrap methods, and legacy risk handling.

## Runtime Rules

- For code review requests, lead with findings ordered by severity and cite concrete files/lines.
- For review-only requests or workflow Review Agent handoffs, do not edit code unless the coordinator/user explicitly assigns edits; for direct refactor requests, make scoped behavior-preserving changes.
- Separate code by reason to change, not by file size or arbitrary layer count.
- Keep domain rules readable and protected; do not let style preferences outrank domain invariants.
- Prefer behavior-preserving small refactors. Add or use characterization tests before risky legacy changes when practical.
- Avoid speculative generality: add abstractions only when they remove real complexity, meaningful duplication, or a proven change axis.
- Prefer clear names and simple functions, but keep public modules/classes deep enough that callers are not forced through implementation steps.
- Treat DRY as single-source business knowledge, not mechanical removal of every similar-looking line.
- Report only verification actually run. If tests, linters, typechecks, or review subagents were not run, say so.
