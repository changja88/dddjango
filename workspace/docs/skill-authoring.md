# Skill Authoring Inputs

이 문서는 실제 `SKILL.md` 작성 직전에 사용할 frontmatter 입력 문서다. `spec.md`의 일부가 아니며, 스킬 trigger와 description을 제품 spec에 섞지 않기 위해 별도로 둔다.

## 1. 작성 원칙

각 skill의 `SKILL.md` frontmatter에는 `name`과 `description`이 반드시 필요하다.

`description`은 Codex가 스킬을 사용할지 판단하는 핵심 입력이다. 따라서 description에는 다음이 들어가야 한다.

- 언제 이 skill을 써야 하는지
- 어떤 요청에서는 다른 skill을 우선해야 하는지
- 관련 skill과의 경계
- 금지해야 할 잘못된 라우팅

긴 예시와 상세 절차는 `SKILL.md` body나 `references/`로 분리한다.

`architecture-implementation-patterns`, `implementation-django-ninja`, `implementation-django-web`은 전용 source reference가 아직 부족하다. 이 세 skill은 전용 reference를 먼저 만들거나 provisional skill로 표시한 뒤 작성한다.

## 2. Frontmatter 입력 표

아래 표는 최종 문구가 아니라 작성 입력이다. 실제 `SKILL.md`를 만들 때 더 짧고 명확한 description으로 다듬는다.

최종 frontmatter `description`은 `Description Draft`만 복사하지 않는다. 반드시 `Description Draft`, `Positive Signals`, `Negative / Prefer Instead`, 한국어 trigger, 관련 skill precedence를 하나의 자연스러운 설명으로 병합한다.

| Skill | Description Draft | Positive Signals | Negative / Prefer Instead |
|---|---|---|---|
| `source-reference-audit` | dddjango source/reference governance audit: workspace docs, source references, runtime bundled references, provenance, conflict/gap ledger, provisional/fallback source status, validation coverage, eval traceability, source/runtime boundary. | source audit, reference provenance, source gap, provisional, conflict/gap, 출처, 근거, traceability, validation coverage | 실제 DDD/Django 설계나 구현은 해당 architecture/implementation skill |
| `architecture-ddd` | DDD/domain modeling: subdomain, bounded context, context map, ubiquitous language, aggregate, invariant, domain event, domain service. | 도메인 규칙, 상태 전이, 정책, 불변식, 바운디드 컨텍스트, 애그리거트 | DB schema는 `architecture-db`; HTTP API는 `architecture-api`; Django 구현은 implementation skills |
| `architecture-implementation-patterns` | Provisional until dedicated source reference exists; implementation architecture patterns for DDD mapping: layered, hexagonal, clean architecture, ports/adapters, repository, CQRS, outbox, ACL, dependency direction. Use fallback source until finalized. | 헥사고날, 클린 아키텍처, 의존성 역전, repository, outbox, ACL, 프로젝트 구조 | 단순 CRUD는 implementation skill 직접 사용 |
| `architecture-db` | Relational DB design supporting the domain model: schema, constraints, indexes, transactions, isolation, locking, rollout constraints. | ERD, 정규화, 인덱스, constraint, transaction, locking, migration risk | Django migration file 구현은 `implementation-django` |
| `architecture-api` | REST API contract design: resources, URL, methods, status codes, Problem Details, pagination, versioning, rate limit, idempotency, OpenAPI. | REST 설계, API 계약, 상태 코드, 오류 형식, OpenAPI | Django Ninja code는 `implementation-django-ninja` |
| `implementation-django` | Django implementation: models, ORM, QuerySet, Manager, service, selector, migration files, transaction, settings, security, performance. | Django model, migration, service, selector, ORM 최적화 | API Router/Schema는 `implementation-django-ninja`; web template은 `implementation-django-web` |
| `implementation-django-ninja` | Provisional until dedicated source reference exists; Django Ninja API implementation: Router, Schema/ModelSchema, auth, pagination, FilterSchema, Problem Details, OpenAPI, TestClient. Use fallback source until finalized. Convert DRF greenfield requests to Ninja. | Django Ninja, Router, Schema, DRF-to-Ninja, API test | DRF ViewSet/Serializer/APIView 신규 구현 금지 |
| `implementation-django-web` | Provisional until dedicated source reference exists; Django web/template/static implementation: TemplateView, templates, static files, base template, component include, HTMX, CSRF for AJAX. Use fallback source until finalized. | template, static, CSS/JS, TemplateView, HTMX | REST API는 `implementation-django-ninja` |
| `implementation-python` | Python implementation quality: type hints, dataclass, Enum/StrEnum, Protocol, pydantic v2 boundaries, async, exceptions, Ruff/typecheck. | Python typing, dataclass, Protocol, pydantic, async | 일반 클린코드 리뷰는 `implementation-cleancode`와 함께 사용 |
| `implementation-tdd` | TDD methodology: test list, Red-Green-Refactor, Inside-Out/Outside-In, failing tests before implementation. | TDD, 실패 테스트, Red-Green-Refactor | pytest fixtures/mock details는 `implementation-test` |
| `implementation-test` | Python/Django test implementation: pytest, fixtures, test doubles, fake/mock/stub, factories, property-based tests, coverage, mutation testing. | pytest, fixture, mock, factory, coverage, testcontainers | TDD 흐름 자체는 `implementation-tdd` |
| `implementation-cleancode` | Clean code/review/refactoring: responsibility, naming, functions, encapsulation, SOLID, duplication, errors, legacy code findings. | 코드 리뷰, 리팩터링, 책임 분리, 품질 개선 | 도메인 모델링은 `architecture-ddd` |
| `workflow-dddjango-subagents` | Role-decomposed dddjango workflow for composite or risky Django/DDD work; coordinates Domain, Architecture, DB, API, Django, Test, Review roles. | subagent, 역할 분해, 병렬 검토, DDD+DB+API+테스트 복합 작업 | 단순 단일 파일 수정이나 짧은 설명은 직접 처리 |

## 3. Cross-Skill Precedence

복합 작업에서 충돌하면 다음 순서로 판단한다.

1. `workflow-dddjango-subagents`
2. `architecture-ddd`
3. `architecture-implementation-patterns`
4. `architecture-db` / `architecture-api`
5. implementation skills
6. quality skills

단순 작업은 이 우선순위를 전부 타지 않는다. 도메인 규칙이 거의 없는 단일 concern 작업은 관련 implementation 또는 quality skill만 사용한다.

## 4. Agents Metadata Inputs

`agents/openai.yaml`은 최종 `SKILL.md`를 기준으로 생성하거나 갱신한다.

각 skill의 metadata에는 다음 입력이 필요하다.

| Skill | display_name | short_description | default_prompt |
|---|---|---|---|
| `source-reference-audit` | Source Reference Audit | Audit source provenance, gaps, provisional status. | `$source-reference-audit` |
| `architecture-ddd` | DDD Architecture | Model bounded contexts, aggregates, invariants, and domain events. | `$architecture-ddd` |
| `architecture-implementation-patterns` | Implementation Patterns | Provisional until dedicated source reference exists; use fallback source to choose clean, hexagonal, CQRS, repository, outbox, and integration patterns. | `$architecture-implementation-patterns` |
| `architecture-db` | DB Architecture | Design relational schemas, constraints, indexes, transactions, and rollout constraints. | `$architecture-db` |
| `architecture-api` | API Architecture | Design REST contracts, Problem Details, pagination, idempotency, and OpenAPI. | `$architecture-api` |
| `implementation-django` | Django Implementation | Implement Django models, ORM, services, selectors, migrations, and transactions. | `$implementation-django` |
| `implementation-django-ninja` | Django Ninja Implementation | Provisional until dedicated source reference exists; use fallback source to implement Django Ninja routers, schemas, auth, errors, OpenAPI, and API tests. | `$implementation-django-ninja` |
| `implementation-django-web` | Django Web Implementation | Provisional until dedicated source reference exists; use fallback source to implement Django templates, static files, TemplateView, HTMX, and CSRF-aware web flows. | `$implementation-django-web` |
| `implementation-python` | Python Implementation | Apply modern Python typing, dataclasses, Protocols, enums, pydantic boundaries, and Ruff. | `$implementation-python` |
| `implementation-tdd` | TDD Implementation | Drive work through test lists, failing tests, Red-Green-Refactor, and TDD choices. | `$implementation-tdd` |
| `implementation-test` | Test Implementation | Write pytest tests, fixtures, doubles, factories, property tests, and coverage strategy. | `$implementation-test` |
| `implementation-cleancode` | Clean Code | Review and refactor responsibility, naming, encapsulation, duplication, and legacy risks. | `$implementation-cleancode` |
| `workflow-dddjango-subagents` | dddjango Workflow | Coordinate role-decomposed DDD/Django work across domain, DB, API, implementation, test, and review roles. | `$workflow-dddjango-subagents` |
