# P1.5 Usage Cards

## Metadata

| field | value |
|---|---|
| work item id | `20260522-230605-p1-5-skill-usage-cards` |
| phase | `p1-5-usage-cards` |
| source inputs | P0 inventory evidence; P1 reference sufficiency evidence |
| card scope | high-risk trigger families for all 13 inventoried dddjango skills |
| downstream use | P2 `SKILL.md` description and handoff wording; P3 forward-test prompts; P5 eval case design |

## Selection Basis

P0 inventoried 13 runtime skills and their bundled references. P1 classified all
13 matching source references and recorded `needs-source` count `0`, with
`implementation-tdd`, `source-reference-audit`, and
`workflow-dddjango-subagents` remaining provisional for later completion claims.

P1.5 treats each skill-aligned trigger area as high risk because wrong routing
can load the wrong reference family, overclaim completion evidence, or mutate the
wrong phase artifact. The prompts below use user-facing wording first; taxonomy
labels are only used to identify the expected skill and card boundary.

## Coverage Summary

| trigger family | expected skill | positive prompts | exclusion prompts | main routing risk |
|---|---|---:|---:|---|
| REST API contract | `architecture-api` | 3 | 2 | confused with API implementation or DB idempotency storage |
| Relational DB integrity and rollout | `architecture-db` | 3 | 2 | confused with domain modeling or Django ORM code |
| Domain modeling and invariants | `architecture-ddd` | 3 | 2 | confused with schema design or repository pattern mechanics |
| Implementation architecture patterns | `architecture-implementation-patterns` | 3 | 2 | confused with concrete Django code or broad DDD modeling |
| Maintainability review and refactor | `implementation-cleancode` | 3 | 2 | confused with feature implementation or architecture redesign |
| Django ORM/service/migration implementation | `implementation-django` | 3 | 2 | confused with API router work or DB-only design |
| Django Ninja API implementation | `implementation-django-ninja` | 3 | 2 | confused with REST contract design or legacy DRF maintenance |
| Django server-rendered web | `implementation-django-web` | 3 | 2 | confused with API implementation or frontend-only SPA work |
| Python language and typing implementation | `implementation-python` | 3 | 2 | confused with Django/test/tool-specific work |
| TDD workflow | `implementation-tdd` | 3 | 2 | confused with pytest mechanics or proof of eval completion |
| pytest and Django test mechanics | `implementation-test` | 3 | 2 | confused with TDD methodology or production implementation |
| Source/reference governance | `source-reference-audit` | 3 | 2 | confused with domain implementation or runtime completion evidence |
| Coordinated dddjango workflow | `workflow-dddjango-subagents` | 3 | 2 | confused with real subagent execution proof or single-skill edits |

## Card 01 - REST API Contract

| field | value |
|---|---|
| expected skill | `architecture-api` |
| expected bundled resource load | Load only the relevant API contract reference: `rest-contracts.md`, `problem-details.md`, `idempotency-openapi.md`, or `pagination-versioning.md`. |
| expected artifact behavior | Produce REST contract decisions, endpoint/status/header/error shapes, OpenAPI impact notes when relevant, and handoff notes for implementation or DB persistence. Do not patch runtime API code unless the user explicitly asks for implementation. |
| common non-goal | Django Ninja router code, ORM transaction code, DDD aggregate discovery, GraphQL/gRPC/WebSocket/API gateway design. |
| expected handoff | If the request moves from contract to code, say: `API contract is set; implementation belongs in implementation-django-ninja.` If idempotency storage or locking is undecided, say: `Persistence and locking details belong in architecture-db.` |

Positive user prompts:

1. `주문 생성 API URL, status code, 에러 응답, Idempotency-Key 계약을 정리해줘.`
2. `PATCH /coupons/{id}에서 어떤 상태 코드와 Problem Details 필드를 써야 할지 설계해줘.`
3. `목록 API 페이지네이션과 버전 변경 정책을 OpenAPI에 어떻게 드러낼지 잡아줘.`

Exclusion prompts:

1. `Django Ninja Router랑 Schema 코드를 바로 만들어줘.` Expected route: `implementation-django-ninja`.
2. `Idempotency-Key를 저장할 테이블과 unique index를 설계해줘.` Expected route: `architecture-db`.

## Card 02 - Relational DB Integrity And Rollout

| field | value |
|---|---|
| expected skill | `architecture-db` |
| expected bundled resource load | Load only the relevant DB reference: `schema-modeling.md`, `constraints-indexes.md`, `transactions-locking.md`, or `rollout-constraints.md`. |
| expected artifact behavior | Produce schema, constraint, index, transaction, locking, migration rollout, backfill, and rollback decisions. Include API/Django handoff when the issue is outside DB ownership. |
| common non-goal | Domain language discovery, Django model code mechanics, REST status codes, UI rendering. |
| expected handoff | If domain rules are unclear, say: `The invariant needs domain modeling first; hand off to architecture-ddd.` If the schema is decided and only ORM code remains, say: `The implementation belongs in implementation-django.` |

Positive user prompts:

1. `쿠폰 중복 사용을 DB에서 막으려면 unique constraint랑 transaction을 어떻게 잡아야 해?`
2. `대량 주문 테이블에 상태 컬럼을 추가해야 하는데 lock 위험 없이 migration 순서를 짜줘.`
3. `예약 좌석 동시성 때문에 select_for_update랑 isolation level을 검토해줘.`

Exclusion prompts:

1. `Order aggregate가 어떤 불변식을 가져야 하는지 모델링해줘.` Expected route: `architecture-ddd`.
2. `Django model field와 migration 파일을 직접 수정해줘.` Expected route: `implementation-django`.

## Card 03 - Domain Modeling And Invariants

| field | value |
|---|---|
| expected skill | `architecture-ddd` |
| expected bundled resource load | Load only the relevant DDD reference: `strategic-design.md`, `tactical-patterns.md`, `context-map.md`, or `domain-events.md`. |
| expected artifact behavior | Produce bounded context, ubiquitous language, aggregate, value object, invariant, use-case, and domain event decisions. Defer storage/API/code details to owning skills. |
| common non-goal | Table/index design, HTTP contract details, Django model/migration code, simple CRUD wording. |
| expected handoff | If persistence choices become central, say: `DB constraints and transactions belong in architecture-db.` If code structure becomes central, say: `Implementation structure belongs in architecture-implementation-patterns or a concrete implementation skill.` |

Positive user prompts:

1. `환불 도메인에서 어떤 상태 전이와 불변식을 aggregate로 묶어야 할지 잡아줘.`
2. `주문과 결제 bounded context를 나눌지, 같은 모델로 둘지 판단해줘.`
3. `재고 차감 이벤트를 도메인 이벤트로 볼 수 있는지 모델링 관점에서 검토해줘.`

Exclusion prompts:

1. `orders 테이블 정규화와 foreign key를 설계해줘.` Expected route: `architecture-db`.
2. `Django 서비스 함수와 repository 코드를 작성해줘.` Expected route: `implementation-django` with possible `architecture-implementation-patterns` handoff first.

## Card 04 - Implementation Architecture Patterns

| field | value |
|---|---|
| expected skill | `architecture-implementation-patterns` |
| expected bundled resource load | Load only the relevant pattern reference: `pattern-selection.md`, `ports-adapters.md`, `repository-uow.md`, or `outbox-acl.md`. |
| expected artifact behavior | Produce dependency direction, service layer, repository/UoW, ports/adapters, outbox, ACL, CQRS, saga, and transaction-owner decisions. Keep concrete framework edits for implementation skills. |
| common non-goal | Pure DDD problem-space modeling, DB index tuning, simple one-file CRUD, Django syntax-only help. |
| expected handoff | If domain boundaries are unresolved, say: `Model the domain first with architecture-ddd.` If concrete Django code is ready, say: `Apply the chosen pattern with implementation-django or implementation-django-ninja.` |

Positive user prompts:

1. `결제 승인 후 재고 차감과 알림 발송을 outbox로 분리할지 서비스에서 바로 호출할지 판단해줘.`
2. `Django 프로젝트에서 repository/UoW를 넣어야 할지, service layer만으로 충분한지 봐줘.`
3. `외부 배송 API를 ports-adapters로 감싸려면 의존성 방향을 어떻게 잡아야 해?`

Exclusion prompts:

1. `쿠폰 정책의 ubiquitous language와 aggregate를 먼저 찾아줘.` Expected route: `architecture-ddd`.
2. `models.py와 services.py 코드를 지금 수정해줘.` Expected route: `implementation-django`.

## Card 05 - Maintainability Review And Refactor

| field | value |
|---|---|
| expected skill | `implementation-cleancode` |
| expected bundled resource load | Load only the relevant maintainability reference: `responsibility.md`, `naming-functions.md`, `encapsulation-abstraction.md`, or `legacy-review.md`. |
| expected artifact behavior | Produce code review findings, refactor steps, naming/responsibility improvements, and small behavior-preserving patches when requested. Escalate architecture/domain/test gaps instead of hiding them inside refactor advice. |
| common non-goal | New feature design, whole-system architecture rewrite, DB/API contract decisions, formatter-only changes. |
| expected handoff | If the refactor exposes architecture pattern decisions, say: `Pattern ownership belongs in architecture-implementation-patterns.` If tests are missing for a risky refactor, say: `Add focused protection with implementation-test before changing behavior.` |

Positive user prompts:

1. `이 fat model을 더 읽기 쉽게 리팩터링해줘. 동작은 바꾸면 안 돼.`
2. `View 함수에 비즈니스 로직이 너무 많은데 책임을 어떻게 나누면 좋을지 리뷰해줘.`
3. `이 함수 이름과 분기 구조가 헷갈려서 clean code 관점으로 고쳐줘.`

Exclusion prompts:

1. `결제와 재고를 outbox로 분리하는 아키텍처 결정을 내려줘.` Expected route: `architecture-implementation-patterns`.
2. `pytest fixture와 factory_boy 구조를 잡아줘.` Expected route: `implementation-test`.

## Card 06 - Django ORM, Services, Migrations, Transactions

| field | value |
|---|---|
| expected skill | `implementation-django` |
| expected bundled resource load | Load only the relevant Django reference: `models-orm.md`, `services-selectors.md`, `migrations.md`, `transactions-performance-security.md`, or `coding-style-drf-maintenance.md`. |
| expected artifact behavior | Produce Django model, ORM, QuerySet/Manager, service/selector, migration, transaction, settings, caching, security, performance, or legacy DRF maintenance edits. Include tests when the change needs executable protection. |
| common non-goal | REST contract design, Django Ninja Router/Schema implementation, TemplateView/template rendering, pure Python typing theory. |
| expected handoff | If REST behavior is undecided, say: `Set the API contract first with architecture-api.` If the request is a greenfield API endpoint, say: `Use implementation-django-ninja for Router and Schema work.` |

Positive user prompts:

1. `Django 모델에 주문 상태를 추가하고 안전한 migration 순서까지 반영해줘.`
2. `이 QuerySet N+1을 줄이고 service/selector 구조로 정리해줘.`
3. `transaction.atomic 위치가 맞는지 보고 결제 저장 로직을 고쳐줘.`

Exclusion prompts:

1. `POST /orders API 응답 status code와 에러 포맷을 설계해줘.` Expected route: `architecture-api`.
2. `Django Ninja Router와 Schema를 새로 만들어줘.` Expected route: `implementation-django-ninja`.

## Card 07 - Django Ninja API Implementation

| field | value |
|---|---|
| expected skill | `implementation-django-ninja` |
| expected bundled resource load | Load only the relevant Django Ninja reference: `router-schema.md`, `problem-details-openapi.md`, `auth-pagination-filtering.md`, or `testclient.md`. |
| expected artifact behavior | Produce Router, Schema, ModelSchema, endpoint adapter, auth/permission, filtering/sorting, pagination, Problem Details mapping, OpenAPI, and TestClient acceptance-test edits. Preserve DRF only for legacy maintenance or migration contexts. |
| common non-goal | Framework-neutral REST design, DB lock/index design, server-rendered templates, legacy DRF ViewSet expansion as a greenfield standard. |
| expected handoff | If the contract is not decided, say: `REST contract belongs in architecture-api before Router code.` If persistence details are risky, say: `DB concurrency belongs in architecture-db and ORM code in implementation-django.` |

Positive user prompts:

1. `Django Ninja로 주문 생성 Router, request/response Schema, TestClient 테스트를 만들어줘.`
2. `Ninja endpoint에서 Problem Details 형태로 validation error를 맞춰줘.`
3. `DRF ViewSet으로 새로 만들려던 API를 Ninja Router 기준으로 바꿔줘.`

Exclusion prompts:

1. `API URL, status code, header 정책만 먼저 정리해줘.` Expected route: `architecture-api`.
2. `템플릿으로 주문 상세 페이지를 렌더링해줘.` Expected route: `implementation-django-web`.

## Card 08 - Django Server-Rendered Web

| field | value |
|---|---|
| expected skill | `implementation-django-web` |
| expected bundled resource load | Load only the relevant web reference: `templates.md`, `templateview-htmx.md`, `csrf-ajax.md`, or `static-assets.md`. |
| expected artifact behavior | Produce TemplateView/CBV/FBV, templates, base includes, static CSS/JS, forms, HTMX, CSRF-for-AJAX, view auth, and render acceptance checks. Do not turn a page request into a REST API. |
| common non-goal | Django Ninja Router/Schema, REST contract design, ORM-heavy migration work, client-side SPA framework architecture. |
| expected handoff | If the user asks for JSON API behavior, say: `API implementation belongs in implementation-django-ninja.` If ORM or transaction changes dominate, say: `Django model/service work belongs in implementation-django.` |

Positive user prompts:

1. `주문 상세 Django 템플릿 페이지를 만들고 권한 체크까지 넣어줘.`
2. `HTMX로 쿠폰 검색 결과만 부분 렌더링되게 바꿔줘.`
3. `템플릿 폼에서 CSRF 포함 AJAX 제출이 되도록 고쳐줘.`

Exclusion prompts:

1. `주문 목록 JSON API에 pagination을 넣어줘.` Expected route: `implementation-django-ninja` with possible `architecture-api` handoff.
2. `재고 차감 transaction과 select_for_update를 고쳐줘.` Expected route: `implementation-django` or `architecture-db` if design is undecided.

## Card 09 - Python Language And Typing Implementation

| field | value |
|---|---|
| expected skill | `implementation-python` |
| expected bundled resource load | Load only the relevant Python reference: `typing.md`, `dataclasses-enums.md`, `protocols-boundaries.md`, or `pydantic-v2.md`. |
| expected artifact behavior | Produce Python type hints, Protocol/dataclass/Enum/TypedDict/pydantic v2 boundary, async/concurrency, exception, context manager, or version-gated implementation decisions and edits. Keep framework-specific mechanics in framework skills. |
| common non-goal | Django ORM design, pytest fixture design, REST API contract design, broad clean-code review with no Python-specific issue. |
| expected handoff | If Django behavior dominates, say: `Framework code belongs in implementation-django or implementation-django-ninja.` If test mechanics dominate, say: `Use implementation-test for pytest/factory/mock details.` |

Positive user prompts:

1. `이 함수에 Python 3.12 타입 힌트를 제대로 넣고 None 처리도 좁혀줘.`
2. `외부 결제 클라이언트를 Protocol로 감싸는 게 맞는지 코드로 정리해줘.`
3. `pydantic v2 DTO와 dataclass 도메인 객체 경계를 어떻게 나눌지 봐줘.`

Exclusion prompts:

1. `Django QuerySet 성능을 select_related로 고쳐줘.` Expected route: `implementation-django`.
2. `pytest mock과 fixture를 만들어줘.` Expected route: `implementation-test`.

## Card 10 - TDD Workflow

| field | value |
|---|---|
| expected skill | `implementation-tdd` |
| expected bundled resource load | Load only the relevant TDD reference: `test-list.md`, `red-green-refactor.md`, `inside-out-outside-in.md`, `bdd-atdd.md`, and only cautious wording from provisional `ai-assisted-tdd.md`. |
| expected artifact behavior | Produce a test list, failing-test-first loop, Red-Green-Refactor checkpoints, boundary cases, inside-out/outside-in choice, and refactor stopping points. Do not claim eval completion from AI-assisted TDD guidance. |
| common non-goal | pytest fixture mechanics without TDD workflow, coverage/mutation tooling, production implementation without a test-first loop. |
| expected handoff | If the user needs fixture/mock/factory details, say: `Test mechanics belong in implementation-test.` If domain/API/DB contracts are unclear, say which architecture skill must settle them before the TDD loop. |

Positive user prompts:

1. `쿠폰 할인 정책을 TDD로 진행할 테스트 목록부터 잡아줘.`
2. `실패하는 테스트를 먼저 만들고 Red-Green-Refactor 순서로 구현해줘.`
3. `이 기능은 outside-in으로 할지 inside-out으로 할지 TDD 관점에서 정해줘.`

Exclusion prompts:

1. `factory_boy fixture와 pytest mock 구조만 만들어줘.` Expected route: `implementation-test`.
2. `이미 구현된 코드의 커버리지와 mutation testing 설정을 봐줘.` Expected route: `implementation-test`.

## Card 11 - pytest And Django Test Mechanics

| field | value |
|---|---|
| expected skill | `implementation-test` |
| expected bundled resource load | Load only the relevant test reference: `pytest-fixtures.md`, `test-doubles.md`, `factories-property-tests.md`, `django-api-concurrency.md`, or `coverage-mutation.md`. |
| expected artifact behavior | Produce pytest tests, fixtures, conftest, parametrization, assertions, fakes/mocks/stubs/spies, factory_boy/Faker, Hypothesis, time/HTTP mocking, testcontainers, coverage, mutation, BDD mechanics, Django Ninja TestClient tests, or idempotency/concurrency tests. |
| common non-goal | TDD methodology planning, production code design, unresolved API/DB/domain contracts. |
| expected handoff | If the user wants a test-first workflow, say: `TDD loop planning belongs in implementation-tdd.` If the behavior under test is not specified, hand off to the relevant architecture or implementation skill first. |

Positive user prompts:

1. `pytest fixture랑 factory_boy로 주문 테스트 데이터를 정리해줘.`
2. `Django Ninja TestClient로 주문 생성 API contract test를 작성해줘.`
3. `Idempotency-Key 동시성 테스트를 pytest로 재현하게 만들어줘.`

Exclusion prompts:

1. `이 기능을 TDD로 어떤 순서로 개발할지 테스트 목록을 짜줘.` Expected route: `implementation-tdd`.
2. `transaction.atomic 위치를 실제 서비스 코드에서 고쳐줘.` Expected route: `implementation-django` after DB design if needed.

## Card 12 - Source And Reference Governance

| field | value |
|---|---|
| expected skill | `source-reference-audit` |
| expected bundled resource load | Load `source-governance.md` when the task involves provenance, source/reference roles, runtime/source boundary, cache-sync evidence, leakage, validation coverage, or eval traceability. |
| expected artifact behavior | Produce source-gap, provenance, boundary, leakage, metadata/cache-sync, or validation/eval traceability audit artifacts. Keep source-authoring paths as evidence paths only, not runtime references. Do not use provisional governance rows as later phase completion proof. |
| common non-goal | Application design, Django implementation, actual runtime cache completion, domain/API/DB/test decisions. |
| expected handoff | If the request asks to change application behavior, say: `This is not source governance; route to the owning domain/API/DB/Django/test skill.` If it asks for subagent workflow, say: `Routing/delegation belongs in workflow-dddjango-subagents unless the question is source evidence.` |

Positive user prompts:

1. `각 skill이 어떤 reference를 근거로 삼는지 provenance gap을 점검해줘.`
2. `workspace/reference 경로가 runtime skill에 새지 않았는지 boundary audit 해줘.`
3. `SKILL.md description과 openai.yaml trigger가 source evidence와 맞는지 감사해줘.`

Exclusion prompts:

1. `주문 생성 API를 설계하고 구현해줘.` Expected route: `architecture-api` then `implementation-django-ninja` as needed.
2. `subagent 역할 분담으로 결제 기능 작업 계획을 세워줘.` Expected route: `workflow-dddjango-subagents`.

## Card 13 - Coordinated dddjango Workflow

| field | value |
|---|---|
| expected skill | `workflow-dddjango-subagents` |
| expected bundled resource load | Load only the relevant workflow reference: `role-map.md`, `delegation-rules.md`, `handoff-contract.md`, or `integration-checklist.md`. |
| expected artifact behavior | Produce role decomposition, sequential fallback, handoff contracts, integration checklists, and verification responsibility splits for composite/risky dddjango work. Do not claim real subagent execution, cache sync, or eval/regression completion without later phase evidence. |
| common non-goal | Simple single-file changes, small field renames, decorative role maps, source provenance audits, or direct application code when a single skill owns the work. |
| expected handoff | If source evidence is the real question, say: `Source/reference governance belongs in source-reference-audit.` If a single concrete implementation area owns the work, say: `Use the owning implementation or architecture skill directly; no workflow split is needed.` |

Positive user prompts:

1. `주문 결제 기능을 DDD, DB, API, 테스트 역할로 나눠서 진행 계획을 세워줘.`
2. `subagent로 병렬 검토해야 할 위험한 Django 변경인데 역할과 handoff를 정리해줘.`
3. `재고 예약 작업이 도메인, 락, API, pytest까지 걸쳐 있어. 순차 fallback까지 포함해서 workflow를 짜줘.`

Exclusion prompts:

1. `이 한 줄 import 오류만 고쳐줘.` Expected route: no workflow skill; use the concrete implementation/test skill or direct edit.
2. `reference final.md 출처와 provisional 상태를 감사해줘.` Expected route: `source-reference-audit`.
