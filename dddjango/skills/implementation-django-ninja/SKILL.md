---
name: implementation-django-ninja
description: >
  Use for Django Ninja API implementation: Router/라우터, Schema/스키마, ModelSchema, endpoint adapter, auth/permission, filtering/sorting, pagination, Problem Details, OpenAPI, TestClient acceptance criteria, and DRF-to-Ninja migration. Use when implementing Router/Schema endpoints, making tiny Router edits, answering short Django Ninja implementation questions, or converting greenfield DRF Serializer/ViewSet/APIView/DefaultRouter/rest_framework requests to Django Ninja. Legacy DRF review/migration is allowed only for compatibility or migration work. Prefer workflow-dddjango-subagents for risky DDD+DB/API+test work or subagents/서브에이전트/역할 분해/병렬 검토/책임 분배 requests; architecture-api for undecided REST/header/content negotiation contracts; architecture-db for idempotency/locking; architecture-ddd for unclear domain rules; implementation-django for ORM/service/migration; implementation-test for pytest/API contract test mechanics.
---

# Django Ninja 구현

REST 계약, 도메인 동작, 저장소/트랜잭션 판단이 충분히 정해진 뒤 Django Ninja HTTP adapter를 구현할 때 사용한다. 이 skill의 runtime 지침은 Router, Schema, auth/permission wiring, API error mapping, OpenAPI 영향, TestClient acceptance criteria에 집중한다.

## Source 경계

- Django Ninja source는 Router, Schema/ModelSchema, endpoint adapter 경계, auth/permission wiring, filtering/sorting, pagination hook, Problem Details exception mapping, OpenAPI 영향, TestClient 확인, DRF-to-Ninja migration 기준을 제공한다.
- `architecture-api`는 resource, HTTP method, status code, RFC 9457 Problem Details 계약, header/content negotiation, pagination strategy, versioning, rate limiting, idempotency, OpenAPI 계약 결정을 맡는다.
- `implementation-django`는 HTTP adapter 밖의 ORM, selector, service, transaction, migration, caching, security 구현을 맡는다.
- Django/DRF 자료는 legacy review, DRF-to-Ninja migration, compatibility, comparison에만 사용한다.

## Routing

- 주문/결제/재고처럼 위험한 도메인에서 DDD, DB/API contract, Django 구현, test, transaction, duplicate prevention이 함께 얽히면 `workflow-dddjango-subagents`를 먼저 사용한다.
- REST resource, URL shape, status code, error contract, pagination strategy, versioning, rate limiting, idempotency behavior가 미정이면 `architecture-api`를 먼저 사용한다.
- HTTP header, `Content-Type`, `Accept`, language negotiation, cache semantics, content negotiation behavior가 미정이면 `architecture-api`를 먼저 사용한다.
- idempotency storage, unique constraint, locking, transaction isolation, retry behavior, DB consistency 결정이 미정이면 API 구현 전에 `architecture-db`를 사용한다.
- domain rule, state transition, invariant, bounded context가 불명확하면 `architecture-ddd`를 먼저 사용한다.
- ORM model, service, selector, transaction, migration이 주 작업이면 `implementation-django`를 사용한다.
- pytest fixture, mock, factory, test double, concurrency test mechanics, coverage, 상세 test 구현이 주 작업이면 `implementation-test`를 사용한다. 이 skill은 endpoint 구현도 범위에 있을 때 Django Ninja TestClient와 API contract acceptance criteria를 제시한다.
- 새 작업에서 DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`, `rest_framework`를 요청하면, 명시적인 legacy review/migration이 아닌 한 구현 목표를 Django Ninja로 전환한다.
- 사용자가 subagents/서브에이전트, 역할 분해, 병렬 검토, 책임 분배를 요청하면 `workflow-dddjango-subagents`를 먼저 사용한다.
- 짧은 Django Ninja 설명이나 작은 기존 Router 문자열 수정은 DDD/workflow 절차 없이 바로 답하거나 수정한다.

## 출력 형태

- 순수 answer-only 요청은 사용자가 요구한 답만 출력한다. 문장 수나 bullet 수가 고정되어 있으면 정확히 그 수만 반환하고 멈춘다.
- 사용자가 지정한 출력 형태는 명시 지시다. command, check, tool, skill/reference loading 보고 습관보다 우선한다.
- 정의 질문은 요청한 Django Ninja 개념과 일반적 사용만 정의한다. 사용자가 요구하지 않은 구현 조언, 테스트 메모, service-layer 조언을 덧붙이지 않는다.
- Skill/reference loading command는 사용자 작업 검증이 아니므로 실행 명령으로 보고하지 않는다.

## Reference Loading

- 현재 Django Ninja 작업에 관련된 reference 파일만 읽는다.
- Router, Schema/ModelSchema, endpoint adapter 경계, request/response mapping, DRF-to-Ninja conversion은 [router-schema.md](references/router-schema.md)를 읽는다.
- auth/permission, `FilterSchema`/query filtering, sorting, pagination hook, rate limiting, versioning 구현 관심사는 [auth-pagination-filtering.md](references/auth-pagination-filtering.md)를 읽는다.
- RFC 9457 Problem Details, exception handler, validation error mapping, idempotency, status code, compatibility, OpenAPI 영향은 [problem-details-openapi.md](references/problem-details-openapi.md)를 읽는다.
- Django Ninja API test acceptance criteria와 honest verification reporting은 [testclient.md](references/testclient.md)를 읽는다.

## Runtime 규칙

- Router 함수는 request schema validation, auth/permission 연결, usecase/service 호출, domain/application error 변환, response schema mapping, OpenAPI 영향으로 얇게 유지한다.
- 핵심 business rule, state transition, 복잡한 ORM query, 외부 SDK 호출은 Router, Schema, filter code에 두지 않는다.
- business behavior와 transaction ownership은 `implementation-django`의 service/usecase 경계를 따른다.
- request schema, response schema, public filtering/sorting parameter는 API contract에 맞게 의도적으로 좁힌다. model field를 우연히 노출하지 않는다.
- 기존 API contract가 legacy shape를 명시적으로 요구하지 않는 한 API error는 RFC 9457 Problem Details를 사용한다.
- duplicate-prone POST endpoint는 `Idempotency-Key` 동작을 service transaction과 storage owner와 함께 맞춘다.
- DRF에서 migration할 때는 status code, field, pagination, auth behavior, error shape, OpenAPI 변경을 비교해 client compatibility를 보존한다.
- 구현 작업에서는 실제 실행한 검증만 보고한다. TestClient, pytest, OpenAPI generation, compatibility check, schema check를 실행하지 않았으면 실행했다고 말하지 않는다. 순수 answer-only 요청에서는 verification-not-run 보고를 생략한다.
