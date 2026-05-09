---
name: architecture-api
description: >
  Use for REST API contract architecture: resources, endpoint and URL structure, HTTP methods, status codes, RFC 9457 Problem Details, request/response contracts, headers, content negotiation, authentication/authorization semantics, pagination, versioning, backward compatibility, deprecation, rate limiting, Idempotency-Key, and OpenAPI. Use for REST 설계, API 계약, endpoint/엔드포인트, URL, HTTP method/메서드, status code/상태 코드, 오류 형식, Problem Details, 페이지네이션, 버전 관리, rate limit, 멱등성, OpenAPI. Prefer workflow-dddjango-subagents for composite/risky/subagent Django work, architecture-ddd when use cases or invariants are unclear, architecture-db for storage/transaction/idempotency persistence, and implementation-django-ninja for Django Ninja Router/Schema/code/API tests.
---

# API Architecture

Use this skill to turn use cases and client needs into REST contracts. This skill designs external API behavior; it does not implement framework code.

## Routing

- If the user explicitly asks for subagents, subagent/subagents, 서브에이전트, 역할 분해, 병렬 검토, 책임 분배, or dddjango workflow in a Django task, use `workflow-dddjango-subagents` first.
- If a Django/DDD task combines API contract, domain rules, DB schema, implementation, tests, duplicate prevention, or risky nouns such as 주문, 결제, 재고, 예약, 환불, 권한, or ledger, prefer `workflow-dddjango-subagents` before this skill.
- If the use case, aggregate boundary, invariant, state transition, or ubiquitous language is unclear, use `architecture-ddd` before finalizing endpoints.
- If idempotency persistence, uniqueness, transaction boundaries, constraints, indexes, or rollout migration risk are central, use `architecture-db`; keep user-visible API behavior here.
- If the main work is Django Ninja `Router`, `Schema`, `ModelSchema`, auth implementation, OpenAPI generation, or API tests, use `implementation-django-ninja` after the contract is clear.
- If the user asks for greenfield DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`, or `rest_framework` implementation, use `implementation-django-ninja` to convert the implementation target to Django Ninja; keep framework-neutral REST contract decisions here.
- If the user asks for pytest/API contract tests, use `implementation-test` after contract criteria are known.
- For a simple status-code, URL naming, or error-format question, answer directly without forcing a full DDD workflow.

## Reference Loading

- Read [rest-contracts.md](references/rest-contracts.md) for REST resources, URL shape, HTTP methods, status codes, headers, auth/authz, content negotiation, and cache semantics.
- Read [problem-details.md](references/problem-details.md) for RFC 9457 error contracts and status/error consistency.
- Read [pagination-versioning.md](references/pagination-versioning.md) for pagination, versioning, backward compatibility, deprecation, and rate limiting.
- Read [idempotency-openapi.md](references/idempotency-openapi.md) for `Idempotency-Key`, duplicate POST behavior, and OpenAPI contract impact.

## Runtime Rules

- Start from the external use case, resource identity, client workflow, authorization needs, error conditions, compatibility constraints, and expected query patterns.
- Choose resources and URLs as stable nouns; avoid leaking database table names or imperative action names into URLs.
- Choose HTTP methods by safety and idempotency. Use POST for creation/actions, PUT for full replacement, PATCH for partial update, DELETE for deletion, and GET only for safe reads.
- Specify status codes with response body expectations, especially 201 with `Location`, 202 for accepted async work, 204 for no-content delete, 409 for conflicts, 422 for semantic validation, 429 for rate limits, and 503 with retry guidance.
- Use RFC 9457 Problem Details consistently for API errors; keep `status` aligned with the HTTP response and keep `title` reusable while `detail` describes the occurrence.
- Keep API adapters thin. Do not place domain decisions in Router/view/schema logic; route unclear rules to `architecture-ddd` and implementation to `implementation-django-ninja`.
- For duplicate-sensitive POSTs, define `Idempotency-Key` acceptance, replay response, conflict behavior, and storage handoff to `architecture-db`.
- Choose pagination from scenario facts: offset for small/admin use, cursor or keyset for large or changing datasets, and include next-page metadata.
- Treat response field removal, type changes, required request additions, URL changes, status changes, and error shape changes as breaking unless versioned or migrated.
- Record OpenAPI impact whenever endpoints, schemas, status responses, auth, pagination, rate limits, or idempotency behavior change.
- Report only tests, validation, review, browser checks, or subagent work that was actually executed. If not executed, say so.
