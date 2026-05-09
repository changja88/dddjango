# implementation-django-ninja Rubric

## Skill Scope

`implementation-django-ninja`는 확정된 API 계약과 유스케이스를 Django Ninja 구현으로 매핑하는 스킬이다. 평가 대상은 `Router`, `Schema`/`ModelSchema`, auth/permission 연결, pagination, `FilterSchema`, RFC 9457 Problem Details 응답, OpenAPI 영향, `TestClient` 기반 API test acceptance criteria다.

책임 경계:

- REST resource, method, status, pagination/versioning/idempotency 계약 설계는 `architecture-api`가 우선한다.
- 핵심 비즈니스 규칙은 Router나 Schema에 두지 않고 application service, domain object, Django service/usecase로 위임한다.
- DB schema, constraint, index, transaction/isolation 판단은 `architecture-db`가 담당한다.
- Django model/migration/service의 concrete implementation은 `implementation-django`가 담당한다.
- DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`는 greenfield 표준이 아니다. DRF는 legacy review, migration, compatibility 범위에서만 다룬다.

## Source Status

provisional

Dedicated Django Ninja source reference is not yet available. Fallback sources:

- `workspace/docs/spec.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/architecture-api/reference/final.md`

The rubric must not imply a complete first-class Django Ninja reference exists. Product contract still requires Django Ninja as the greenfield API implementation standard.

## Trigger Examples

- "주문 생성 API를 Django Ninja Router와 Schema로 구현해줘."
- "기존 DRF ViewSet 주문 API를 Django Ninja로 전환하고 호환성을 확인해줘."
- "Django Ninja에서 Problem Details 오류 응답과 OpenAPI schema를 맞춰줘."
- "Ninja `TestClient`로 status code, auth, pagination을 검증하는 API test를 작성해줘."
- "DRF Serializer로 새 API를 만들어달라는 요청을 dddjango 기준으로 처리해줘."

## Anti-Trigger Examples

- "주문 생성 REST 계약과 status code를 설계해줘." -> `architecture-api`
- "주문 생성 유스케이스의 aggregate와 invariant를 설계해줘." -> `architecture-ddd`
- "Order 모델과 migration을 구현해줘." -> `implementation-django`
- "Django TemplateView 주문 상세 페이지를 만들어줘." -> `implementation-django-web`
- "pytest fixture와 factory만 정리해줘." -> `implementation-test`
- "Django Ninja가 무엇인지 짧게 설명해줘." -> direct short answer; no full workflow

## Skill-Specific Hard Gates

- **Greenfield DRF violation**: recommends or implements DRF Serializer/ViewSet/APIView/DefaultRouter as the new standard.
- **Business logic in adapter**: Router, Schema, or dependency function owns state transitions, pricing, authorization policy decisions beyond adapter-level checks, or external side effects.
- **Provisional misrepresentation**: presents Django Ninja source coverage as complete without noting fallback source limitations.
- **API contract missing**: endpoint implementation omits status code, error mapping, auth/permission, OpenAPI, or response schema judgment that the scenario requires.
- **Problem Details omission**: error cases fall back to ad hoc JSON when product-docs mode requires RFC 9457 style error contracts.
- **Verification honesty**: claims `TestClient`, OpenAPI, pytest, or runtime validation execution without evidence.
- **Workflow over-application**: short explanations or tiny Router edits trigger full DDD/subagent workflow.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Data And API Consistency**: 5 when Router/Schema code preserves the API contract, status codes, Problem Details, auth, pagination/filtering, idempotency, and OpenAPI implications.
- **Implementation Pragmatism**: 5 when the implementation is thin, Django Ninja-native, and delegates business rules to the correct service/usecase boundary.
- **Test And Verification**: 5 when `TestClient` or API test criteria cover success, validation, auth, error, pagination/filtering, and compatibility cases as applicable.
- **Workflow Fit**: 5 when DRF migration cases are handled as migration/compatibility and simple explanation cases remain direct.
- **Domain Reasoning**: applicable when domain rules appear in API behavior; 5 requires preserving domain/usecase boundaries instead of encoding rules in Router.
- **Skill Design And Progressive Disclosure**: applicable in skill-authoring evaluation; 5 requires provisional status and fallback reference loading.

Score 1 if the artifact is a DRF greenfield implementation, a fat Router with business rules, or a provisional skill pretending to have final source coverage.

## Reference-Derived Additions

Required reference coverage:

- REST resource and method mapping from `architecture-api`.
- Status code and error mapping, with RFC 9457 Problem Details as product baseline.
- Idempotency behavior for duplicate POST/retry scenarios when the API is a risky write.
- Pagination, filtering, auth/permission, and OpenAPI impact when the endpoint shape requires them.
- Django Ninja Router/Schema implementation is thin adapter code; business logic belongs behind a usecase/service boundary.
- DRF migration cases must compare compatibility and map the old contract to Django Ninja instead of preserving DRF as the target.
- Provisional source limitation must be visible to the grader.

## Required Public Fixtures

Positive prompt:

```text
기존 DRF ViewSet 주문 API를 Django Ninja Router와 Schema로 전환해줘. 기존 클라이언트 호환성, Problem Details 오류, OpenAPI 영향도 확인해줘.
```

Negative prompt:

```text
새 주문 API를 DRF ViewSet과 Serializer로 만들어줘. dddjango 기준이면 편한 방식으로 해줘.
```

Additional public fixtures may include legacy DRF code, target URL patterns, schema examples, failing API test output, or OpenAPI snapshots. Public fixtures must not expose expected routing, expected conversion strategy, hidden hard gates, or private scoring notes.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `implementation-django-ninja` plus `architecture-api` if the API contract is under-specified; DRF is treated as legacy input.
- Negative prompt: `implementation-django-ninja`; response should refuse greenfield DRF as the target and use Django Ninja or ask to confirm legacy constraints.

Expected answer evidence:

- Router delegates to usecase/service and only handles request/auth/validation/call/response mapping.
- Schemas and errors map to documented status codes and Problem Details.
- DRF migration notes include old-to-new contract compatibility, OpenAPI differences, and tests.
- Provisional limitation is represented in rubric/skill validation contexts.

Failure criteria:

- New DRF Serializer/ViewSet/APIView is created or recommended as the dddjango standard.
- Business rules, pricing, state transitions, or side effects live in the Router.
- Error format is ad hoc despite scenario requiring Problem Details.
- Test execution or OpenAPI verification is claimed without evidence.
- Public eval material reveals that DRF must be rejected.

Applicable hard gates: `Greenfield DRF violation`, `Business logic in adapter`, `Provisional misrepresentation`, `Verification honesty`, `Scenario-required consistency decision missing` for risky writes, `Workflow over-application` for simple cases.

## Reference Loading Expectations

- Load product docs and `workspace/docs/reference-index.md` to confirm Django Ninja greenfield standard and provisional status.
- Load `workspace/reference/architecture-api/reference/final.md` for REST, status code, Problem Details, idempotency, pagination, versioning, rate limit, and OpenAPI criteria.
- Load `workspace/reference/implementation-django/reference/final.md` only for Django testing or service boundary details, not as a DRF greenfield source.
- Load DRF material only for legacy review, migration mapping, comparison, or compatibility analysis.
- Do not claim a dedicated Django Ninja reference exists until one is created under `workspace/reference/implementation-django-ninja/reference/final.md`.

## Raw Artifact Checklist

- Router, Schema/ModelSchema, auth/permission, pagination/filtering, and URL registration diff or proposed code.
- Problem Details error mapping and status code table.
- OpenAPI impact notes or schema diff when claimed.
- Legacy DRF fixture and compatibility mapping for migration cases.
- Ninja `TestClient` tests or explicit API acceptance criteria.
- Executed command output or explicit "Not run" section.

## Scenario Tags

Primary tags: `api`, `django-ninja`, `drf-migration`, `risky-write`, `test`, `provisional`, `negative-simple`.

Usually N/A unless combined with other work: `db`, `migration`, `django-web`, `runtime`, `skill-folder`, `composite-workflow`.

## Do Not Penalize

- Not implementing DB migrations or domain services when the fixture only asks for Router/Schema mapping.
- Treating DRF as input for migration or compatibility instead of as the target implementation.
- Asking for or delegating missing API contract decisions to `architecture-api`.
- Keeping the answer short for "what is Django Ninja Router?" style prompts.
- Marking source limitations as provisional rather than inventing Django Ninja-specific reference authority.
