# Typing

Use this reference for type hints, Python-version gates, `X | None`, generics, external data shapes, decorators, type narrowing, and Ruff/typecheck compatibility.

## Type Contracts

- Add types to public functions and methods so callers can see inputs, outputs, and `None` possibility.
- Prefer `T | None` and `A | B` over `Optional[T]` and `Union[A, B]` when the project targets Python 3.10+.
- Use built-in collection generics such as `list[Order]`, `dict[str, int]`, and `tuple[str, ...]`.
- Type collection contents; unparameterized `list`, `dict`, and `tuple` hide contracts.
- Use `TypedDict` for external JSON/API dictionaries when a lightweight typed shape is enough.

## Advanced Typing

- Use `Literal` for a small local set of values; use `Enum`/`StrEnum` when the concept has domain meaning or behavior.
- Use `Final` for constants and `NewType` when two values share a runtime type but must not be mixed by callers.
- Use PEP 695 type parameter syntax only when the project targets Python 3.12+.
- Use `@override` only when the project targets Python 3.12+ or has the right `typing_extensions` dependency.
- Use `ParamSpec` and `Concatenate` for decorators that preserve or adapt callable signatures.
- Use `TypeIs` when available for two-branch narrowing; use `TypeGuard` for older targets or incompatible narrowing cases.

## Tooling

- Follow the project’s configured Python target before using 3.12+ or 3.13+ features.
- Prefer Ruff-compatible modern syntax when Ruff `UP`, `B`, `SIM`, `C4`, `RET`, `PTH`, or `RUF` rules are enabled.
- Use strict mypy or pyright settings incrementally when the project already has them; do not impose strict mode across legacy code without a rollout plan.
- When changing type contracts, run the project’s available Ruff/typecheck/test commands or report that they were not run.
