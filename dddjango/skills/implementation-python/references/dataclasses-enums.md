# Dataclasses And Enums

Use this reference for value objects, finite states, dataclass options, `Enum`/`StrEnum`, `NamedTuple`, and `match/case`.

## Finite States

- Use `Enum` or `StrEnum` for meaningful finite states such as order status, payment state, or permission level.
- Prefer `StrEnum` or `str, Enum` when values must serialize as strings and the project target supports it.
- Keep state-transition rules in domain/application code, not in arbitrary string comparisons.
- Use `match/case` for explicit state machines when it makes the allowed cases easier to audit.

## Dataclass Value Objects

- Use dataclasses for data-centered objects with clear fields and small behavior.
- Use `frozen=True` when the object represents a value and mutation would break reasoning.
- Use `slots=True` when many instances are created or attribute shape should stay fixed.
- Use `kw_only=True` for constructors where positional arguments would be ambiguous.
- Use `field(default_factory=...)` for mutable defaults.
- Use `__post_init__` and `InitVar` for normalization that belongs to construction, but keep durable domain invariants in the domain boundary.
- For precision-sensitive value objects such as money, ratios, or measurements, consider `Decimal` or `Fraction` instead of `float`.
- For value objects with behavior, test value semantics and immutability when relevant, plus one representative valid operation and one invariant rejection path.

## Alternatives

- Use `NamedTuple` for small immutable records that need tuple compatibility.
- Use a normal class when behavior, invariants, lifecycle, or dependencies dominate over stored fields.
- Do not convert every DTO or service into a dataclass just for uniformity.
- Coordinate persistence-shaped Django models with `implementation-django`; dataclasses do not replace ORM models by default.
