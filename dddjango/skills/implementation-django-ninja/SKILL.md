---
name: implementation-django-ninja
description: >
  Provisional until dedicated source reference exists; use with fallback source for Django Ninja API implementation: Router, Schema/ModelSchema, auth, pagination, FilterSchema, Problem Details, OpenAPI, TestClient acceptance criteria, and DRF-to-Ninja migration. Use for Router/Schema 구현, 인증/인가, 페이지네이션, 필터링/정렬, 오류 응답, API 계약 테스트 기준, Problem Details/OpenAPI, DRF ViewSet/APIView/Serializer를 Ninja로 전환. Prefer workflow-dddjango-subagents for DDD+DB/API+tests or risky duplicate-prevention work, architecture-api for undecided REST/header/content-negotiation contracts, architecture-db for idempotency storage/locking/isolation decisions, implementation-django for ORM/service/migration work, and implementation-test for pytest/fixture/test double/concurrency test details.
---

# Django Ninja Implementation

This skill is provisional. Dedicated Django Ninja source reference does not exist yet; use the fallback source named below and verify exact framework syntax against the project’s installed Django Ninja version and existing code conventions.

## Fallback Source

- Use the dddjango REST API architecture source for resources, HTTP methods, status codes, RFC 9457 Problem Details, auth/permission concepts, pagination, versioning, rate limiting, idempotency, and OpenAPI.
- Use the dddjango product decision that new API implementation uses Django Ninja, not DRF.
- Use the Django/DRF fallback material only for legacy review, DRF-to-Ninja migration, compatibility, or comparison.

## Routing

- If the request combines DDD, DB/API contract, Django implementation, tests, transactions, or duplicate prevention for risky domains such as orders/payments/inventory, use `workflow-dddjango-subagents` first.
- If REST resources, URL shape, status codes, error contract, pagination strategy, versioning, rate limiting, or idempotency behavior are not decided, use `architecture-api` first.
- If HTTP headers, `Content-Type`, `Accept`, language negotiation, cache semantics, or other content negotiation behavior is undecided, use `architecture-api` first.
- If idempotency storage, unique constraints, locking, transaction isolation, retry behavior, or DB consistency decisions are undecided, use `architecture-db` before API implementation.
- If domain rules, state transitions, invariants, or bounded context are unclear, use `architecture-ddd` first.
- If ORM models, services, selectors, transactions, or migrations are the main work, use `implementation-django`.
- If the work is pytest fixtures, mocks, factories, test doubles, concurrency test mechanics, coverage, or detailed test implementation, use `implementation-test`; this skill states Django Ninja TestClient and API contract acceptance criteria unless endpoint implementation is also in scope.
- If the user asks for DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`, or `rest_framework` for new work, convert the implementation target to Django Ninja unless the task is explicitly legacy review or migration.
- If the user asks for subagents, 역할 분해, 병렬 검토, or 책임 분배, use `workflow-dddjango-subagents` first.
- For a short Django Ninja explanation or a tiny existing Router string edit, answer or edit directly without DDD/workflow ceremony.

## Reference Loading

- Read [router-schema.md](references/router-schema.md) for Router, Schema/ModelSchema, endpoint adapter boundaries, request/response mapping, and DRF-to-Ninja conversion.
- Read [auth-pagination-filtering.md](references/auth-pagination-filtering.md) for auth/permission, filtering, sorting, pagination, rate limiting, and versioning implementation concerns.
- Read [problem-details-openapi.md](references/problem-details-openapi.md) for RFC 9457 Problem Details, idempotency, status codes, compatibility, and OpenAPI effects.
- Read [testclient.md](references/testclient.md) for Django Ninja API test acceptance criteria and honest verification reporting.

## Runtime Rules

- Keep Router functions thin: request schema validation, auth/permission connection, usecase/service call, domain/application error translation, response schema mapping, and OpenAPI impact.
- Do not put core business rules, state transitions, complex ORM queries, or external SDK calls in Router, Schema, or filter code.
- Use service/usecase boundaries from `implementation-django` for business behavior and transaction ownership.
- Use RFC 9457 Problem Details for API errors unless the existing API contract explicitly requires a compatible legacy shape.
- For duplicate-prone POST endpoints, coordinate `Idempotency-Key` behavior with the service transaction and storage owner.
- Preserve client compatibility when migrating from DRF; compare status codes, fields, pagination, auth behavior, error shape, and OpenAPI changes.
- Report only verification actually run. If TestClient, pytest, OpenAPI generation, compatibility checks, or schema checks were not run, say so.
