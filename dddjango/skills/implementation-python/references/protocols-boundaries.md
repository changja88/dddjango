# Protocols And Boundaries

Source basis: `workspace/reference/implementation-python/reference/final.md`의 Protocol, class API, exception, context manager, async/concurrency 섹션.

`Protocol`, structural subtyping, replaceable boundary, exception, context manager, async/concurrency choice, unnecessary abstraction 회피를 판단할 때 사용한다.

## Protocols

- caller가 replaceable implementation 사이의 structural contract를 필요로 할 때 `Protocol`을 사용한다.
- 좋은 후보는 repository-like port, clock/ID generator, external gateway adapter, file-like stream, strategy object다.
- implementation이 하나뿐이고 meaningful boundary가 없으면 class마다 protocol을 만들지 않는다.
- caller가 capability 일부만 필요하면 작은 protocol을 합성한다.
- type relationship이 caller에게 중요할 때만 generic protocol을 사용한다.
- `@runtime_checkable`은 presence check일 뿐이다. runtime에서 method signature를 검증하지 않는다.

## Boundaries

- external SDK, filesystem, HTTP, framework detail이 core code를 테스트하거나 교체하기 어렵게 만들면 narrow role 뒤에 둔다.
- simple stable helper, local value object, real boundary가 아닌 implementation detail은 direct dependency를 선호한다.
- Repository와 Unit of Work architecture는 주로 `architecture-implementation-patterns`의 책임이다. 이 skill은 Python contract 표현만 돕는다.

## Attributes And Properties

- behavior가 필요 없으면 boilerplate getter/setter보다 plain attribute를 선호한다.
- attribute처럼 보이는 access에 computed, lazy, compatibility, validation behavior가 필요할 때 `@property`를 사용한다.
- dynamic attribute access가 object의 핵심 책임이 아니면 broad `__getattr__` 또는 `__getattribute__` hook을 피한다.

## Class API Shape

- closure보다 named object가 명확한 stateful callable object에는 `__call__`을 사용할 수 있다.
- subclass를 존중해야 하는 alternative constructor에는 `@classmethod`를 사용한다.
- class 근처에 둘 이유는 있지만 instance/class state가 필요 없는 stateless helper에만 `@staticmethod`를 사용한다.
- domain/value object와 debugging-oriented class에는 유용한 `__repr__`을 구현한다. 별도의 user-facing representation이 도움이 될 때만 `__str__`을 추가한다.
- protected implementation detail은 single leading underscore를 선호한다. subclass field collision을 피해야 할 때만 double-underscore name mangling을 사용한다.
- subclass registration이나 validation이 실제로 필요하면 metaclass보다 `__init_subclass__`를 우선한다.
- mixin은 narrow, stateless, one reusable behavior에 집중한다. control flow를 숨기는 inheritance chain을 피한다.
- custom container에서 built-in behavior를 override할 때는 `collections.abc` base class나 `UserDict` 계열 wrapper를 선호한다.

## Exceptions And Resource Flow

- module이 여러 related error를 노출하면 top-level module exception을 정의한다.
- `None`이 valid business result가 아니면 exceptional failure에 `None`을 반환하지 말고 explicit exception을 raise한다.
- `try`/`except`/`else`/`finally`로 expected recovery, success-only work, cleanup을 분리한다.
- `warnings.deprecated`는 프로젝트가 Python 3.13+를 target할 때만 사용한다. 그렇지 않으면 explicit `DeprecationWarning`을 쓰고 type-checker integration이 약하다는 점을 문서화한다.
- resource acquisition/release에는 context manager를 사용하고 cleanup behavior를 보이게 유지한다.

## Async And Concurrency

- 프로젝트가 Python 3.11+를 target하고 작업이 실제 async이면 structured concurrency에 `asyncio.TaskGroup`을 사용한다.
- `TaskGroup` 내부 task failure는 `ExceptionGroup`으로 묶여 전파된다. 서로 다른 error group을 분리해 처리해야 하면 `except*`를 사용한다.
- async refactor 전 Django ORM call, external SDK, file I/O, side effect가 프로젝트 runtime에서 실제로 async-safe인지 확인한다.
- async로 만들 수 없는 blocking I/O에는 thread를 사용한다. GIL 아래에서 thread가 CPU-bound code를 개선한다고 가정하지 않는다.
- free-threaded Python과 subinterpreter는 version/runtime-specific choice이며 default로 취급하지 않는다.
