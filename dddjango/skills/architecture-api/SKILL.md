---
name: architecture-api
description: >
  Use for REST API contract architecture: resource/URL shape, HTTP method/status behavior, RFC 9457 Problem Details, request/response/header contracts, auth/authz, content negotiation, pagination, versioning, deprecation, rate limits, Idempotency-Key behavior, and OpenAPI impact. Use for REST 설계, API 계약, endpoint/URL, HTTP 메서드와 상태 코드, 오류 응답, 인증/인가, 헤더, 콘텐츠 협상, 페이지네이션, 버전, 레이트 리밋, 멱등성, OpenAPI. Prefer workflow-dddjango-subagents for coordinated multi-role or subagent work; architecture-ddd when use cases/invariants are unclear; architecture-db for idempotency persistence, uniqueness, locking, transactions, or rollout risk; implementation-django-ninja for Router/Schema/API adapter or greenfield DRF implementation requests; and implementation-test for pytest/API contract mechanics. Do not use for GraphQL, gRPC, SOAP, WebSocket, HATEOAS, or API Gateway design except to state the REST boundary if relevant.
---

# API Architecture

사용 사례와 client workflow를 REST API 계약으로 바꿀 때 사용한다. 이 skill은 외부 API 동작과 계약을 설계하며, framework adapter, ORM, migration, pytest 구현은 직접 소유하지 않는다.

## Routing

- 사용자가 coordinated implementation/review, subagents/서브에이전트, 역할 분해, 병렬 검토, 책임 분배, dddjango workflow를 요청하면 `workflow-dddjango-subagents`를 먼저 사용한다.
- REST resource, URL, HTTP method/status, request/response/header contract, Problem Details, auth semantics, pagination, versioning, deprecation, rate limit, `Idempotency-Key`, OpenAPI 계약이 주 질문이면 이 skill이 직접 맡는다.
- use case, aggregate boundary, invariant, state transition, ubiquitous language가 불명확하면 endpoint를 확정하기 전에 `architecture-ddd`로 넘긴다.
- idempotency storage, uniqueness, constraint, index, locking, transaction isolation, rollout migration risk가 중심이면 `architecture-db`로 넘기고, user-visible API behavior만 이 skill에 남긴다.
- Django Ninja `Router`, `Schema`, `ModelSchema`, auth 구현, exception handler, OpenAPI generation, API adapter code가 주 작업이면 계약 확정 뒤 `implementation-django-ninja`로 넘긴다.
- greenfield DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`, `rest_framework` 구현 요청은 `implementation-django-ninja`에서 Django Ninja 목표로 전환하게 하고, framework-neutral REST 계약만 여기서 다룬다.
- pytest, Django Ninja `TestClient`, fixture, mock, concurrency test mechanics가 주 작업이면 계약 기준을 정한 뒤 `implementation-test`로 넘긴다.
- GraphQL, gRPC, SOAP, WebSocket, HATEOAS, API Gateway design은 이 REST 계약 skill의 범위가 아니다. 필요한 경우 REST boundary만 짧게 말한다.
- 단순 status code, URL naming, error-format 질문은 전체 workflow를 강제하지 말고 바로 답한다.

## Reference Loading

- 현재 API 계약 판단에 필요한 reference만 읽는다.
- REST resource, URL shape, HTTP methods/status, request/response/header contract, auth/authz, content negotiation, cache semantics는 [rest-contracts.md](references/rest-contracts.md)를 읽는다.
- RFC 9457 error contract, Problem Details field semantics, status/error consistency는 [problem-details.md](references/problem-details.md)를 읽는다.
- pagination 선택, versioning, backward compatibility, deprecation, rate limiting은 [pagination-versioning.md](references/pagination-versioning.md)를 읽는다.
- `Idempotency-Key`, duplicate POST retry/replay/conflict behavior, OpenAPI contract impact는 [idempotency-openapi.md](references/idempotency-openapi.md)를 읽는다.

## Runtime Rules

- 먼저 외부 use case, client workflow, resource identity, authorization need, error condition, compatibility constraint, query pattern을 확인한다.
- 계약 산출물은 endpoint 단위로 `resource/URL`, `method`, `request`, `response by status`, `headers`, `Problem Details`, `auth/authz`, `pagination/versioning/rate limit`, `idempotency`, `OpenAPI impact`를 필요한 만큼 명시한다.
- domain rule이나 invariant가 API shape를 좌우하면 결정을 만들지 말고 `architecture-ddd` handoff를 남긴다.
- DB durability, uniqueness, locking, transaction, rollout이 계약 성패를 좌우하면 API-visible behavior만 정하고 storage/transaction decision은 `architecture-db` handoff로 남긴다.
- adapter 구현, schema mapping, exception handler, generated OpenAPI wiring은 `implementation-django-ninja` 책임으로 넘긴다.
- test code, fixtures, mocks, concurrency harness, detailed pytest mechanics는 `implementation-test` 책임으로 넘기고, 이 skill은 acceptance criteria만 적는다.
- duplicate-sensitive POST처럼 여러 책임이 결합된 경우 API contract, DB storage, implementation, test acceptance를 분리해 handoff한다. 사용자가 role decomposition을 요청했으면 `workflow-dddjango-subagents`를 먼저 적용한다.
- 실행하지 않은 tests, validation, review, browser check, subagent work, Serena 사용을 실행한 것처럼 보고하지 않는다.
