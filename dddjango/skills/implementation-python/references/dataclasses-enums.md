# Dataclasses And Enums

Source basis: `workspace/reference/implementation-python/reference/final.md`의 dataclass, Enum/StrEnum, NamedTuple, match/case 섹션.

value object, finite state, dataclass option, `Enum`/`StrEnum`, `NamedTuple`, `match/case`를 판단할 때 사용한다.

## Finite States

- order status, payment state, permission level처럼 의미 있는 finite state에는 `Enum` 또는 `StrEnum`을 사용한다.
- 값이 문자열로 serialize되어야 하고 Python target이 허용하면 `StrEnum`을 우선한다. 낮은 target에서는 `str, Enum` 조합을 사용한다.
- state-transition rule은 임의 문자열 비교가 아니라 domain/application code에 둔다.
- allowed case를 감사하기 쉬워질 때 explicit state machine에 `match/case`를 사용한다.

## Dataclass Value Objects

- field가 명확하고 behavior가 작은 data-centered object에 dataclass를 사용한다.
- 객체가 value를 표현하고 mutation이 reasoning을 깨면 `frozen=True`를 사용한다.
- 인스턴스가 많거나 attribute shape를 고정해야 하면 `slots=True`를 사용한다.
- positional argument가 모호한 constructor에는 `kw_only=True`를 사용한다.
- mutable default에는 `field(default_factory=...)`를 사용한다.
- construction normalization에는 `__post_init__`와 `InitVar`를 사용할 수 있다. durable domain invariant는 domain boundary에 둔다.
- money, ratio, measurement처럼 precision-sensitive value object에는 `float` 대신 `Decimal` 또는 `Fraction`을 고려한다.
- behavior가 있는 value object는 value semantics, immutability, 대표 valid operation, invariant rejection path를 테스트한다.

## Alternatives

- tuple compatibility가 필요한 작은 immutable record에는 `NamedTuple`을 사용한다.
- behavior, invariant, lifecycle, dependency가 stored field보다 중요하면 일반 class를 사용한다.
- uniformity만을 위해 모든 DTO나 service를 dataclass로 바꾸지 않는다.
- persistence-shaped Django model은 `implementation-django`와 조율한다. dataclass는 기본적으로 ORM model을 대체하지 않는다.
