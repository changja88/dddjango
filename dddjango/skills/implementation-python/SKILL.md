---
name: implementation-python
description: >
  Use for Python implementation quality: type hints, X | None, built-in generics, TypedDict, type narrowing, decorators, dataclass, NamedTuple, Enum/StrEnum, match/case, Protocol, context managers, pydantic v2 boundaries, async/concurrency choices, exceptions, Ruff, mypy, and pyright. Use for Python typing/타입 힌트/타이핑, dataclass/데이터클래스, Enum/StrEnum/열거형, Protocol/프로토콜 boundary, pydantic v2 런타임 검증, 비동기, 예외 처리, modern Python and Python-version gates. Prefer architecture-ddd for unclear domain modeling, architecture-api or architecture-db for unresolved API/DB contracts, implementation-django-ninja for Router/Schema/API implementation, implementation-cleancode for general refactoring, implementation-django for ORM/migrations, implementation-test for pytest, and workflow-dddjango-subagents for explicit subagent, role decomposition, parallel review, or responsibility splitting requests. Do not use for simple syntax explanations, typo-only edits, or API/DB/domain contract decisions that are still undecided.
---

# Python Implementation

dddjango 작업에서 Python 언어 계층의 계약과 구현 선택을 다룰 때 사용한다. 타입으로 입출력 계약을 드러내고, 현대 Python 구문을 프로젝트 target에 맞게 선택하며, runtime validation은 올바른 boundary에 둔다.

## Routing

- 도메인 용어, invariant, aggregate boundary, state transition rule이 불명확하면 Python construct를 고르기 전에 `architecture-ddd`를 사용한다.
- REST resource, status code, Problem Details, OpenAPI, DB schema, transaction, locking, migration rollout 결정이 unresolved이면 Python type으로 인코딩하기 전에 `architecture-api` 또는 `architecture-db`를 사용한다.
- 주된 작업이 Django ORM, migration, transaction, QuerySet, settings이면 `implementation-django`를 사용한다.
- 주된 작업이 Django Ninja Router/Schema/API test이면 `implementation-django-ninja`를 사용한다.
- 주된 작업이 pytest fixture, mock, factory, coverage이면 `implementation-test`를 사용한다. Red-Green-Refactor 방법 자체가 핵심이면 `implementation-tdd`를 사용한다.
- 일반 refactor/review에 Python-specific typing 또는 language choice가 함께 있으면 `implementation-cleancode`와 이 skill을 함께 사용한다.
- 사용자가 dddjango subagent, role decomposition, parallel review, responsibility splitting을 명시적으로 요구하면 먼저 `workflow-dddjango-subagents`를 사용한다.
- 아주 작은 syntax 질문이나 한 줄 type hint 설명은 DDD/workflow 절차 없이 직접 답한다.

## Reference Loading

- 현재 Python implementation task에 필요한 reference file만 읽는다.
- type hints, `X | None`, built-in generics, `TypedDict`, narrowing, decorator, Ruff/typecheck, Python-version gate는 [typing.md](references/typing.md)를 읽는다.
- finite state, value object, dataclass option, `Enum`/`StrEnum`, `NamedTuple`, `match/case`는 [dataclasses-enums.md](references/dataclasses-enums.md)를 읽는다.
- `Protocol`, replaceable boundary, structural subtyping, exception, context manager, async/concurrency, 불필요한 abstraction 회피는 [protocols-boundaries.md](references/protocols-boundaries.md)를 읽는다.
- external DTO/config/runtime validation, pydantic v2 API, strict mode, validation과 domain invariant의 boundary는 [pydantic-v2.md](references/pydantic-v2.md)를 읽는다.

## Runtime Rules

- public function/method contract는 input과 return type으로 명시한다. 단, 프로젝트 style이나 Python version과 싸우는 noisy annotation은 추가하지 않는다.
- 프로젝트 target이 지원하면 `T | None`, `A | B`, `list[Order]` 같은 built-in generics를 우선한다.
- finite state에는 `Enum` 또는 `StrEnum`을 사용한다. 값이 지역적이고 behavior가 붙지 않을 때만 `Literal`을 사용한다.
- immutability와 attribute shape가 도움이 되는 value object에는 `@dataclass(frozen=True, slots=True)`를 고려한다. behavior-heavy service를 dataclass로 만들지 않는다.
- `Protocol`은 replaceable boundary나 caller가 실제로 이득을 보는 structural contract에만 사용한다.
- pydantic v2는 external input/output DTO, config, runtime validation에 사용한다. pydantic을 default domain model로 만들지 않는다.
- 3.12+, 3.13+, 3.14+ syntax를 쓰기 전에 프로젝트의 Python version, Ruff, mypy, pyright 설정과 맞춘다.
- 실제로 실행한 verification만 보고한다. Ruff, typecheck, test, runtime check를 실행하지 않았으면 실행하지 않았다고 말한다.
