---
name: architecture-api
description: >
  Use for REST API contract architecture: resources, endpoint/URL shape, HTTP methods/status, RFC 9457 Problem Details, request/response contracts, headers/content negotiation, auth/authz, pagination/versioning/deprecation/rate limits, Idempotency-Key, and OpenAPI. Use for REST 설계, API 계약, 엔드포인트, HTTP 메서드, 상태 코드, 오류 응답, 인증/인가, 헤더, 콘텐츠 협상, 페이지네이션, 버전, 레이트 리밋, 멱등성, OpenAPI. Prefer workflow-dddjango-subagents for coordinated multi-role work, architecture-ddd when use cases/invariants are unclear, architecture-db for idempotency persistence/transactions, implementation-django-ninja for Router/Schema implementation or greenfield DRF Serializer/ViewSet/APIView/rest_framework implementation requests, and implementation-test for pytest/API contract test mechanics.
---

# API Architecture

Use this skill to turn use cases and client needs into REST contracts. This skill designs external API behavior; it does not implement framework code.

## Routing

- If the user asks for coordinated implementation or review across multiple role areas, or asks for subagents, 서브에이전트, 역할 분해, 병렬 검토, 책임 분배, or dddjango workflow, use `workflow-dddjango-subagents` first.
- Keep direct API contract questions here, including risky or duplicate-sensitive endpoints, status/error/idempotency behavior, pagination, versioning, deprecation, auth semantics, and OpenAPI impact, when the user is asking for API architecture rather than multi-role implementation.
- If the use case, aggregate boundary, invariant, state transition, or ubiquitous language is unclear, use `architecture-ddd` before finalizing endpoints.
- If idempotency persistence, uniqueness, transaction boundaries, constraints, indexes, or rollout migration risk are central, use `architecture-db`; keep user-visible API behavior here.
- If the main work is Django Ninja `Router`, `Schema`, `ModelSchema`, auth implementation, OpenAPI generation, or API tests, use `implementation-django-ninja` after the contract is clear.
- If the user asks for greenfield DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`, or `rest_framework` implementation, use `implementation-django-ninja` to convert the implementation target to Django Ninja; keep framework-neutral REST contract decisions here.
- If the user asks for pytest/API contract tests, use `implementation-test` after contract criteria are known.
- For a simple status-code, URL naming, or error-format question, answer directly without forcing a full DDD workflow.

## Reference Loading

- Load only the reference file(s) relevant to the current API contract task.
- Read [rest-contracts.md](references/rest-contracts.md) for REST resources, URL shape, HTTP methods, status codes, request/response contracts, headers, auth/authz, content negotiation, and cache semantics.
- Read [problem-details.md](references/problem-details.md) for RFC 9457 error contracts and status/error consistency.
- Read [pagination-versioning.md](references/pagination-versioning.md) for pagination, versioning, backward compatibility, deprecation, and rate limiting.
- Read [idempotency-openapi.md](references/idempotency-openapi.md) for `Idempotency-Key`, duplicate POST behavior, and OpenAPI contract impact.

## Runtime Rules

- Start from the external use case, resource identity, client workflow, authorization needs, error conditions, compatibility constraints, and expected query patterns.
- Choose resources and URLs as stable nouns; avoid leaking database table names or imperative action names into URLs.
- Choose HTTP methods by safety and idempotency. Use POST for creation/actions, PUT for full replacement, PATCH for partial update, DELETE for deletion, and GET only for safe reads.
- Specify status codes with response body expectations, especially 201 with `Location`, 202 for accepted async work, 204 for no-content delete, 409 for conflicts, 422 for semantic validation, 429 for rate limits, and 503 with retry guidance.
- Define request and response contracts as a status/body/header combination: required and optional inputs, validation, response schemas by status, `Location`, retry/deprecation/rate-limit headers, and no-body responses.
- Use RFC 9457 Problem Details consistently for API errors; keep `status` aligned with the HTTP response and keep `title` reusable while `detail` describes the occurrence.
- Keep API adapters thin. Do not place domain decisions in Router/view/schema logic; route unclear rules to `architecture-ddd` and implementation to `implementation-django-ninja`.
- For duplicate-sensitive POSTs, define `Idempotency-Key` acceptance, replay response, conflict behavior, and storage handoff to `architecture-db`.
- Choose pagination from scenario facts: offset for small/admin use, cursor or keyset for large or changing datasets, and include next-page metadata.
- Treat response field removal, type changes, required request additions, URL changes, status changes, and error shape changes as breaking unless versioned or migrated.
- Record OpenAPI impact whenever endpoints, schemas, status responses, auth, pagination, rate limits, or idempotency behavior change.
- State API contract acceptance criteria for status codes, Problem Details, idempotency replay/conflict, pagination, and compatibility when relevant; hand pytest/TestClient mechanics to `implementation-test` or `implementation-django-ninja`.
- Report only tests, validation, review, browser checks, or subagent work that was actually executed. If not executed, say so.
