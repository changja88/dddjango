---
name: implementation-python
description: >
  Use for Python implementation quality: type hints, X | None, built-in generics, dataclass, Enum/StrEnum, Protocol, pydantic v2 boundaries, async/concurrency choices, exceptions, Ruff, mypy, and pyright. Use for Python typing/타입 힌트/타이핑, dataclass/데이터클래스, Enum/StrEnum/열거형, Protocol/프로토콜 boundary, pydantic v2 런타임 검증, 비동기, 예외 처리, modern Python. Prefer architecture-ddd for unclear domain modeling, architecture-api or architecture-db for unresolved API/DB contracts, implementation-django-ninja for Router/Schema/API implementation, implementation-cleancode for general refactoring, implementation-django for ORM/migrations, and implementation-test for pytest. Do not use for simple syntax explanations, typo-only edits, or API/DB/domain contract decisions that are still undecided.
---

# Python Implementation

Use this skill for the Python-language layer of a dddjango task: expressing contracts with types, choosing modern Python constructs, and keeping runtime validation at the right boundary.

## Routing

- If domain terms, invariants, aggregate boundaries, or state-transition rules are unclear, use `architecture-ddd` before choosing Python constructs.
- If REST resources, status codes, Problem Details, OpenAPI, DB schema, transaction, locking, or migration rollout decisions are unresolved, use `architecture-api` or `architecture-db` before encoding them in Python types.
- If the main work is Django ORM, migrations, transactions, QuerySets, or settings, use `implementation-django`.
- If the main work is Django Ninja Router/Schema/API tests, use `implementation-django-ninja`.
- If the main work is pytest fixtures, mocks, factories, or coverage, use `implementation-test`; if the method is Red-Green-Refactor, use `implementation-tdd`.
- Use `implementation-cleancode` with this skill when the request is a general refactor/review plus Python-specific typing or language choices.
- If the user explicitly asks for dddjango subagents, role decomposition, parallel review, or responsibility splitting in a Django task, use `workflow-dddjango-subagents` first.
- For a tiny syntax question or one-line type hint explanation, answer directly without DDD/workflow ceremony.

## Reference Loading

- Load only the reference file(s) relevant to the current Python implementation task.
- Read [typing.md](references/typing.md) for type hints, `X | None`, generics, `TypedDict`, narrowing, decorators, Ruff/typecheck, and Python-version gates.
- Read [dataclasses-enums.md](references/dataclasses-enums.md) for finite states, value objects, dataclass options, `Enum`/`StrEnum`, `NamedTuple`, and `match/case`.
- Read [protocols-boundaries.md](references/protocols-boundaries.md) for `Protocol`, replaceable boundaries, structural subtyping, exceptions, context managers, async/concurrency, and when not to abstract.
- Read [pydantic-v2.md](references/pydantic-v2.md) for external DTO/config/runtime validation, v2 APIs, strict mode, and the boundary between validation and domain invariants.

## Runtime Rules

- Make public function and method contracts explicit with input and return types, but do not add noisy annotations that fight project style or Python version.
- Prefer `T | None`, `A | B`, and built-in generics such as `list[Order]` when the project target supports them.
- Use `Enum` or `StrEnum` for finite states; use `Literal` only when the values are local and unlikely to need behavior.
- Use `@dataclass(frozen=True, slots=True)` for value objects when immutability and memory shape help; avoid dataclasses for behavior-heavy services.
- Use `Protocol` only for replaceable boundaries or structural contracts that callers really benefit from.
- Use pydantic v2 for external input/output DTOs, config, and runtime validation. Do not make pydantic the default domain model.
- Align code with the project’s configured Python version, Ruff, mypy, and pyright settings before using 3.12+, 3.13+, or 3.14+ syntax.
- Report only verification actually run. If Ruff, typecheck, tests, or runtime checks were not run, say so.
