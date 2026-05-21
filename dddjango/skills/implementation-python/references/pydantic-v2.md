# Pydantic V2

Source basis: `workspace/reference/implementation-python/reference/final.md`의 pydantic v2 API, strict mode, boundary 결정 섹션.

pydantic v2 external DTO, config, runtime validation, strict mode, v1 API migration을 판단할 때 사용한다.

## Boundary Rule

- pydantic v2는 external request/response DTO, API payload, config, settings-like data, system boundary runtime validation에 사용한다.
- pydantic model을 default domain model로 강제하지 않는다. domain invariant는 value object, entity, aggregate, domain service, application service 중 적절한 owner에 둔다.
- Django Ninja schema가 API serialization을 이미 소유하면 별도 pydantic DTO를 추가하기 전에 `implementation-django-ninja`와 조율한다.
- raw pydantic validation error shape를 domain behavior로 누수하지 않는다. adapter/API/config loading layer에서 적절한 application/domain error로 변환한다.

## V2 APIs

- parsing과 validation에는 `model_validate()`를 사용한다.
- dictionary serialization에는 `model_dump()`을 사용한다.
- v1 `Config` class 대신 `ConfigDict`를 사용한다.
- v1 `@validator` 대신 `@field_validator`를 사용한다.
- cross-field 또는 model-level validation에는 `@model_validator`를 사용한다.

## Strictness

- coercion이 나쁜 external input을 숨기면 strict mode를 사용한다.
- boundary가 의도적으로 coercion을 허용하는 field에만 field-level laxness를 적용한다.
- validation error는 올바른 adapter layer에 mapping한다. raw boundary exception을 domain behavior로 누수하지 않는다.

## Migration Notes

- `dict()`, `parse_obj()`, `@validator` 같은 v1 API는 legacy migration concern으로 취급한다.
- v1 code를 교체할 때 serialization name, error shape, coercion behavior에 의존하는 test나 contract check를 함께 갱신한다.
