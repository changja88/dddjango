# Pydantic V2

Use this reference for pydantic v2 external DTOs, config, runtime validation, strict mode, and migrations from v1 APIs.

## Boundary Rule

- Use pydantic v2 for external request/response DTOs, API payloads, config, settings-like data, and runtime validation at system boundaries.
- Do not force pydantic models as the default domain model. Domain invariants should live in value objects, entities, aggregates, domain services, or application services as appropriate.
- If Django Ninja schemas already own API serialization, coordinate with `implementation-django-ninja` before adding separate pydantic DTOs.

## V2 APIs

- Use `model_validate()` for parsing and validation.
- Use `model_dump()` for serialization to dictionaries.
- Use `ConfigDict` instead of v1 `Config` classes.
- Use `@field_validator` instead of v1 `@validator`.
- Use `@model_validator` for cross-field or model-level validation.

## Strictness

- Use strict mode when coercion would hide bad external input.
- Apply field-level laxness only when the boundary intentionally accepts coercion.
- Keep validation errors mapped to the correct adapter layer; do not leak raw boundary exceptions into domain behavior.

## Migration Notes

- Treat v1 APIs such as `dict()`, `parse_obj()`, and `@validator` as legacy migration concerns.
- When replacing v1 code, update tests or contract checks that depend on serialization names, error shapes, or coercion behavior.
