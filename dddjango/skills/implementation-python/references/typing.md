# Typing

근거 요약: Python 언어 특화 source reference의 타입 시스템, 함수 계약, Ruff, mypy/pyright 섹션.

type hints, Python-version gate, `X | None`, built-in generics, external data shape, decorator, type narrowing, Ruff/typecheck compatibility를 판단할 때 사용한다.

## Type Contracts

- public function과 method에는 caller가 input, output, `None` 가능성을 볼 수 있게 type을 붙인다.
- 프로젝트가 Python 3.10+를 target하면 `Optional[T]`, `Union[A, B]`보다 `T | None`, `A | B`를 우선한다.
- `list[Order]`, `dict[str, int]`, `tuple[str, ...]` 같은 built-in collection generics를 사용한다.
- collection 내부 타입을 적는다. parameter 없는 `list`, `dict`, `tuple`은 contract를 숨긴다.
- 외부 JSON/API dictionary가 가벼운 typed shape만 필요하면 `TypedDict`를 사용한다.

## Collection Choice

- 습관이 아니라 역할로 collection을 고른다. ordered sequence는 `list`, membership/uniqueness는 `set`, key lookup은 `dict`, fixed record는 `tuple` 또는 `NamedTuple`을 사용한다.
- `deque`, `heapq`, `bisect`, `array`는 behavior나 performance가 실제로 중요할 때만 사용한다.
- missing key가 예상되고 default behavior가 use case의 일부이면 `dict.get()` 또는 `defaultdict`를 사용한다.
- custom missing-key behavior가 mapping type의 핵심 책임일 때만 `__missing__`을 사용한다.
- ordering intent는 `sorted(..., key=...)`나 tuple key로 명시한다.

## Function Contracts

- `[]`, `{}`, `datetime.now()`처럼 mutable 또는 time-sensitive default argument를 피한다. `None` 후 local initialization을 하거나 dataclass field에는 `default_factory`를 쓴다.
- boolean flag, optional behavior, ambiguous control은 keyword-only argument로 만들어 call site의 의도를 드러낸다.
- positional-only argument는 API compatibility 보존이나 parameter name 의존을 막아야 할 때만 제한적으로 사용한다.
- `None`이 유효한 business result가 아니면 `None` 반환보다 explicit exception을 우선한다.

## Advanced Typing

- 작은 지역 값 집합에는 `Literal`을 사용한다. concept에 domain meaning이나 behavior가 붙으면 `Enum`/`StrEnum`을 사용한다.
- constant에는 `Final`을, runtime type은 같지만 caller가 섞으면 안 되는 값에는 `NewType`을 사용한다.
- PEP 695 type parameter syntax는 프로젝트가 Python 3.12+를 target할 때만 사용한다.
- variable-length generic shape가 caller에게 본질적일 때만 `TypeVarTuple`/`Unpack`을 사용한다.
- type parameter default는 Python 3.13+ target이고 default type이 중요한 변화를 숨기지 않으면서 caller noise를 줄일 때만 사용한다.
- `@override`는 Python 3.12+ target이거나 적절한 `typing_extensions` dependency가 있을 때만 사용한다.
- callable metadata와 signature를 보존하거나 조정하는 decorator에는 `functools.wraps`와 `ParamSpec`, `Concatenate`를 함께 사용한다.
- 양쪽 branch narrowing이 필요하고 사용할 수 있으면 `TypeIs`를 사용한다. older target이나 incompatible narrowing case에는 `TypeGuard`를 사용한다.

## Tooling

- 3.12+, 3.13+, 3.14+ feature를 쓰기 전에 `pyproject.toml`, `ruff.toml`, `pyrightconfig.json`, CI 설정의 Python target을 확인한다.
- Ruff `UP`, `B`, `SIM`, `C4`, `RET`, `PTH`, `RUF` rule이 켜져 있으면 Ruff-compatible modern syntax를 우선한다.
- Ruff 설정을 바꿀 때는 `target-version`, selected rule, per-file-ignore, formatter 충돌 rule을 함께 확인한다.
- mypy/pyright strict mode는 프로젝트가 이미 쓰고 있거나 rollout plan이 있을 때 점진적으로 적용한다. legacy code 전체에 갑자기 강제하지 않는다.
- type contract를 바꾸면 프로젝트의 Ruff/typecheck/test command를 실행하거나, 실행하지 않은 command를 명시적으로 보고한다.
