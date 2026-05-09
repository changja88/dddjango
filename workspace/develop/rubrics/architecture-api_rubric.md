# architecture-api Rubric

## Skill Scope

`architecture-api`는 도메인 유스케이스를 REST API 계약으로 설계하는 스킬이다. 평가 대상은 resources, URLs, HTTP methods, status codes, RFC 9457 Problem Details, auth/authz contract, pagination, filtering, sorting, versioning, backward compatibility, deprecation, rate limiting, idempotency key behavior, and OpenAPI impact.

책임 경계:

- Django Ninja Router/Schema/TestClient implementation은 `implementation-django-ninja`가 담당한다.
- DB schema, idempotency storage, constraint, transaction/isolation은 `architecture-db`가 담당한다.
- Domain aggregate/invariant and usecase ownership are owned by `architecture-ddd`.
- API adapter must not own core business rules.
- Framework implementation choices are out of scope except that dddjango greenfield implementation standard is Django Ninja.

## Source Status

ready

Canonical sources:

- `workspace/docs/spec.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/architecture-api/reference/final.md`

## Trigger Examples

- "주문 생성 API의 REST resource, method, status code, 오류 형식을 설계해줘."
- "중복 POST를 위한 Idempotency-Key 동작과 replay/conflict 응답을 정해줘."
- "목록 API pagination, filtering, sorting, versioning 기준을 잡아줘."
- "기존 클라이언트 하위 호환성과 deprecation 전략을 검토해줘."
- "OpenAPI에 어떤 request/response/error schema가 드러나야 하는지 정리해줘."

## Anti-Trigger Examples

- "Django Ninja Router와 Schema 코드를 구현해줘." -> `implementation-django-ninja`
- "주문 aggregate와 invariant를 설계해줘." -> `architecture-ddd`
- "idempotency key 저장 테이블과 unique index를 설계해줘." -> `architecture-db`
- "Django migration을 작성해줘." -> `implementation-django`
- "pytest API 테스트를 작성해줘." -> `implementation-test`
- "Django Ninja Router가 무엇인지 짧게 설명해줘." -> direct answer; no full API architecture

## Skill-Specific Hard Gates

- **Greenfield DRF violation**: recommends DRF Serializer/ViewSet/APIView as the greenfield implementation standard.
- **Business logic in adapter**: API contract or target design puts core state transitions/rules in the HTTP adapter.
- **Problem Details missing**: product-docs API error contract omits RFC 9457 style errors when errors are in scope.
- **Idempotency behavior missing**: duplicate/retry POST scenario omits key acceptance, replay response, conflict behavior, storage ownership handoff, or TTL/retention decision.
- **Status/method mismatch**: method safety/idempotency or status code semantics are inconsistent with REST contract.
- **OpenAPI impact missing**: scenario asks for contract/schema and answer omits request/response/error schema implications.
- **Verification honesty**: claims OpenAPI generation, API tests, or compatibility validation without evidence.
- **Workflow over-application**: short explanation or tiny endpoint naming request triggers full role workflow.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Data And API Consistency**: 5 when resources, methods, status, errors, idempotency, pagination/versioning, and OpenAPI are consistent with usecase and DB handoff.
- **Implementation Pragmatism**: 5 when the contract is implementable in Django Ninja without moving business logic into Router.
- **Test And Verification**: 5 when API contract tests and compatibility verification criteria are concrete and execution status is honest.
- **Domain Reasoning**: applicable when API exposes domain usecases; 5 requires preserving usecase/invariant boundaries and routing missing domain decisions.
- **Workflow Fit**: 5 when API-only work stays focused and composite/risky API work hands off to DB/Django/Test.

Score 1 if the output lists endpoints without error semantics, idempotency/retry behavior for risky POST, or OpenAPI implications.

## Reference-Derived Additions

Required reference coverage:

- Resource URLs use nouns, collections, stable hierarchy, filtering/sorting/query parameters where appropriate.
- HTTP methods align with safety and idempotency.
- Status codes distinguish validation, authn/authz, not found, conflict, and async behavior.
- Problem Details fields and extension semantics are used for errors.
- Pagination/versioning/backward compatibility/deprecation are considered when collection or client compatibility is in scope.
- Rate limiting and retry behavior are included when external clients or abuse limits are in scope.
- Idempotency-Key behavior covers accepted key, replay, conflict, storage owner, and OpenAPI/header documentation.
- OpenAPI impact includes request, response, error, auth, pagination/filtering, and headers as applicable.

## Required Public Fixtures

Positive prompt:

```text
주문 생성 REST API 계약을 설계해줘. 중복 요청 방지를 위한 Idempotency-Key, Problem Details 오류, OpenAPI 영향, 인증 실패와 재고 부족 응답도 포함해줘.
```

Negative prompt:

```text
Django Ninja Router 코드를 바로 작성해줘. API 계약 설계는 이미 끝났고 status code만 짧게 확인하면 돼.
```

Additional public fixtures may include usecase descriptions, existing endpoint list, client compatibility constraints, OpenAPI fragments, or error examples. Public fixtures must not expose expected routing, hidden status map, pass criteria, or private grader notes.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `architecture-api`; hand off idempotency storage/transaction to `architecture-db` and implementation to `implementation-django-ninja`.
- Negative prompt: if code implementation is requested, route to `implementation-django-ninja`; keep API architecture response minimal or confirm existing contract.

Expected answer evidence:

- Endpoint contract includes method, URL, request, response, status table, Problem Details error types, auth, idempotency behavior, and OpenAPI notes.
- Business rules remain in usecase/domain; API maps errors and representations.
- DB storage owner for idempotency is identified as handoff, not implemented here.
- Greenfield implementation target remains Django Ninja.

Failure criteria:

- DRF is recommended as new implementation standard.
- Idempotent duplicate POST behavior is omitted in duplicate-risk prompt.
- Error response is ad hoc JSON without Problem Details when required.
- Router/domain implementation is mixed into API contract without boundary.
- Public eval material leaks expected status map or routing.

Applicable hard gates: `Greenfield DRF violation`, `Business logic in adapter`, `Scenario-required consistency decision missing` for risky writes, `Verification honesty`, and API-specific gates above.

## Reference Loading Expectations

- Load `workspace/reference/architecture-api/reference/final.md` for REST resource, method, status, Problem Details, auth, pagination, versioning, rate limiting, idempotency, and OpenAPI criteria.
- Load `workspace/docs/spec.md` and `workspace/docs/reference-index.md` to confirm Django Ninja as greenfield implementation standard.
- Load DDD reference only when usecase or invariant ownership is unclear.
- Load DB reference when idempotency storage or transaction consistency must be designed.
- Load Django Ninja reference/fallback only for implementation handoff, not contract source replacement.

## Raw Artifact Checklist

- Endpoint table with method, URL, request, response, status codes.
- Problem Details error type table and examples when applicable.
- Auth/authz, pagination/filtering/sorting/versioning/rate limit notes when in scope.
- Idempotency-Key behavior and storage handoff.
- OpenAPI request/response/error/header impact notes.
- Compatibility/deprecation notes for existing clients.
- API test acceptance criteria and explicit "Not run" list for claimed validation.

## Scenario Tags

Primary tags: `api`, `django-ninja`, `drf-migration`, `risky-write`, `test`, `negative-simple`.

Usually N/A unless combined with other work: `db`, `migration`, `django-web`, `runtime`, `skill-folder`.

## Do Not Penalize

- Not writing Router/Schema code in an API contract-only answer.
- Deferring idempotency storage details to `architecture-db` while still specifying behavior.
- Keeping status/error mapping concise for a small endpoint question.
- Treating DRF as legacy migration input rather than greenfield target.
- Not adding pagination/versioning/rate limit when the endpoint is a single internal command and no client compatibility risk is present.
