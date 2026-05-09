# Source Coverage Crosswalk: architecture-api

## Status

- Skill: `architecture-api`
- Runtime target: `dddjango/skills/architecture-api/`
- Source status: ready
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `rest-contracts.md`, `problem-details.md`, `pagination-versioning.md`, `idempotency-openapi.md`
- Rubric status: opened only after source self-review; review completed with no remaining blocking/major/minor findings

## Sources Used

- `workspace/develop/skill_goal_instructions.md`
- `workspace/docs/spec.md`
- `workspace/docs/plugin-structure.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/skill-hierarchy.md`
- `workspace/docs/skill-authoring.md`
- `workspace/docs/reference-index.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/workflow.md`
- `workspace/docs/validation-plan.md`
- `workspace/reference/architecture-api/reference/final.md`

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | runtime path, this crosswalk | Plugin-bundled target and crosswalk location followed. |
| `## 실행 규칙` | included | this workflow | One skill at a time; rubrics not used during draft. |
| `## 구현 순서` | included | plan order | This follows `architecture-db`. |
| `## Skill별 작성 루프` | included | this crosswalk, review notes | Source scope, draft, review, and rubric sequencing tracked. |
| `### Source Coverage Crosswalk` | included | this file | Source headings and runtime treatment tracked. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter has only name/description; body is concise and procedural. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | Four one-level references summarize source. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata aligns with source and runtime skill. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description | Korean triggers for REST 설계, API 계약, endpoint/엔드포인트, URL, HTTP method/메서드, status code/상태 코드, 오류 응답, Problem Details, 인증/인가, 헤더, 콘텐츠 협상, 페이지네이션, 버전 관리, 하위 호환, deprecation, rate limit, 멱등성, Idempotency-Key, and OpenAPI included. |
| `## Provisional Skill 처리` | omitted | n/a | This skill has dedicated source reference and is not provisional. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | Adjacent workflow, DDD, DB, Django Ninja implementation, and test boundaries included. |
| `## Review 기준` | included | Review Notes | Review types and findings tracked. |
| `## Completed 조건` | included | Review Notes, validation report | Completion requires zero remaining blocking/major/minor findings. |
| `## 검증` | included | validation commands | Only executed validation will be reported. |
| `## 완료 보고` | included | final report | Required report fields will be included. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt authoring content is not runtime behavior. |
| `spec.md` `## 관련 문서` | included | Sources Used | Linked product docs are covered. |
| `## 1. 목표` | included | `SKILL.md`, references | API contracts map domain use cases to external behavior. |
| `## 2. 설계 원칙` | included | `SKILL.md` Routing | API stays adapter-level; unclear domain rules route to DDD. |
| `## 3. 스킬 종류` | included | `SKILL.md` Routing | API responsibility and adjacent skill boundaries included. |
| `### Core DDD` | delegated-to-other-skill | `architecture-ddd`, `SKILL.md` Routing | Use cases, invariants, and aggregate boundaries route to DDD when unclear. |
| `### Implementation Mapping` | delegated-to-other-skill | `implementation-django-ninja`, `SKILL.md` Routing | Concrete Router/Schema/API test implementation routes away after contract design. |
| `### Supporting Architecture` | included | `SKILL.md`, references | REST contract, Problem Details, pagination, versioning, idempotency behavior, and OpenAPI impact are this skill's support scope. |
| `### Quality` | merged | `SKILL.md`, references | Verification honesty, anti-overapplication for simple API questions, and thin adapter boundaries are reflected. |
| `### Workflow` | delegated-to-other-skill | `SKILL.md` Routing, `workflow-dddjango-subagents` | Coordinated multi-role implementation or review routes to workflow; standalone API contract design stays here. |
| `## 4. 산출물 기준` | included | `SKILL.md`, references | Endpoint, request/response, status, Problem Details, and OpenAPI artifacts included. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/architecture-api/` | Plugin-bundled structure used; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name and responsibility preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for `architecture-api` used. |
| `## 8. 금지 사항` | included | file tree, `SKILL.md` | No auxiliary docs; no false validation claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` | Trigger/routing and boundaries are in description/body. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | API signals and anti-routes included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Workflow/DDD precede API when context is composite or domain-unclear; implementation routes away. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align. |
| `reference-index.md` `## Architecture` | included | references | API source reference used. |
| `## Implementation` | delegated-to-other-skill | implementation skills | Concrete Django Ninja/Python/test mechanics route away. |
| `## Reference 사용 원칙` | included | references | Runtime references summarize source and avoid copying `final.md`. |
| `## Reference Gap` | omitted | n/a | This skill has dedicated source reference. |
| `## DRF Guardrail` | delegated-to-other-skill | `SKILL.md`, `implementation-django-ninja` | Greenfield DRF implementation terms route to Django Ninja implementation while API contract remains framework-neutral. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md`, references | REST and RFC 9457 Problem Details are runtime defaults. |

## Contracts, Workflow, And Standard Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Unclear use cases and invariants route to DDD first. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | architecture patterns skill | Repository/UoW/outbox/CQRS/hexagonal/dependency direction is outside API contract. |
| `## architecture-db` | delegated-to-other-skill | `SKILL.md` Routing | Storage, uniqueness, transactions, constraints, and rollout risk route to DB; API behavior remains here. |
| `## architecture-api` | included | `SKILL.md`, references | REST resource, method, status, error, pagination, versioning, idempotency, and OpenAPI covered. |
| `## implementation-django-ninja` | delegated-to-other-skill | `SKILL.md` Routing | Router/Schema/auth/TestClient implementation routes away after contract. |
| `## implementation-django` / `## implementation-django-web` | delegated-to-other-skill | implementation skills | Django internals and web/template implementation route away. |
| `## implementation-python` / `## implementation-cleancode` | delegated-to-other-skill | implementation/quality skills | Python typing and refactoring quality route away unless they affect API contract assumptions. |
| `## implementation-tdd` / `## implementation-test` | delegated-to-other-skill | test skills | Test design consumes API contract criteria; TDD/pytest mechanics route away. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Coordinated multi-role implementation or review, subagent, and role-decomposed Django work routes to workflow; direct API contract design remains here. |
| `## 공통 필수 출력` / `### Risky Write Consistency Block` | delegated-to-other-skill | `architecture-db`, workflow | API owns user-visible idempotency behavior; full consistency block belongs to DB/workflow when risky writes are involved. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | API sits after DDD when domain behavior is unclear and before Django Ninja implementation. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | API follows DDD and informs implementation/test. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple work direct; coordinated multi-role or subagent work routes to workflow, while standalone API design stays here. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | API Agent role belongs to workflow skill. |
| `## 4. Sequential Fallback` / `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow orchestration belongs elsewhere. |
| `## 6. 통합 우선순위` / `## 7. Integration Checklist` | merged | `SKILL.md`, references | API contract feeds implementation/test handoffs. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md` Runtime Rules | Only actual validation may be claimed. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | included | `SKILL.md` Routing | Domain understanding precedes endpoint contract when unclear. |
| `## 2. 하위 도메인별 구현 강도` | delegated-to-other-skill | `architecture-ddd` | Domain complexity controls implementation intensity and routes to DDD when unclear. |
| `## 3. 바운디드 컨텍스트와 언어` | delegated-to-other-skill | `architecture-ddd` | Ubiquitous language and context boundaries precede API naming when unclear. |
| `## 4. 애그리거트와 불변식` | delegated-to-other-skill | `architecture-ddd` | API exposes use cases; it does not define aggregate invariants. |
| `## 5. Domain Events` | delegated-to-other-skill | `architecture-ddd`, `architecture-implementation-patterns` | Event semantics and dispatch timing route away; API records observable async/status effects when exposed to clients. |
| `## 6. Application Service와 Domain Service` | delegated-to-other-skill | `architecture-ddd`, implementation skills | Service ownership routes away; API stays at external contract and adapter boundaries. |
| `## 7. Django ORM 매핑` | delegated-to-other-skill | `implementation-django`, `architecture-db` | ORM mapping, QuerySet behavior, and database model implementation route away; API contracts must not expose ORM/query implementation details. |
| `## 8. Repository와 Transaction` | delegated-to-other-skill | `architecture-db`, patterns | Transaction/storage decisions route away. |
| `## 9. API 매핑` | included | `SKILL.md`, references | REST API as external use-case contract reflected. |
| `## 10. Python 매핑` | delegated-to-other-skill | `implementation-python` | Python type boundaries route to implementation skills. |
| `## 11. 테스트 매핑` | delegated-to-other-skill | `implementation-test` | API test criteria are output; pytest mechanics route away. |
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md`, validation report | Real validation only and over-application checks reflected. |
| `## 2. 대표 시나리오` | merged | `SKILL.md`, references, scenario coverage table | API scenarios are direct when contract-focused; composite implementation scenarios are delegated by boundary. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Data/API consistency, test/verification, and pragmatism reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder will be checked. |

## Validation Scenario Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `validation-plan.md` `### 주문 생성 API` | merged | `SKILL.md`, `idempotency-openapi.md`, `problem-details.md`, `workflow-dddjango-subagents` | API owns REST contract, Problem Details, OpenAPI impact, and user-visible idempotency behavior; multi-role implementation routes to workflow. |
| `### 쿠폰 정책 TDD` | delegated-to-other-skill | `architecture-ddd`, `implementation-tdd` | Coupon policy modeling and TDD mechanics route away unless API contract is explicitly in scope. |
| `### DRF to Django Ninja 전환` | included | `SKILL.md`, `rest-contracts.md`, `problem-details.md`, `implementation-django-ninja` | API owns compatibility, status/error/OpenAPI contract effects; concrete Django Ninja conversion routes to implementation. |
| `### Fat Model 리뷰`, `### View Logic 리뷰` | delegated-to-other-skill | `implementation-cleancode`, `architecture-ddd` | Review and ownership decisions route away unless API adapter contract or Router boundary is the main issue. |
| `### 운영 마이그레이션` | delegated-to-other-skill | `architecture-db`, `implementation-django` | Operational DB migration and rollout safety are outside API contract unless compatibility or status behavior changes. |
| `### 트랜잭션과 동시성` | delegated-to-other-skill | `architecture-db` | Transaction/locking/storage decisions route to DB; API keeps retry/conflict/idempotency behavior when user-visible. |
| `### Django Web` | delegated-to-other-skill | `implementation-django-web` | Template/static/web work routes away. |
| `### Python Typing` | delegated-to-other-skill | `implementation-python` | Python typing mechanics route away. |
| `### Architecture Pattern Selection` | delegated-to-other-skill | `architecture-implementation-patterns` | Pattern selection routes away; API keeps observable contract consequences only. |
| `### Negative Case: 단순 필드 rename`, `### Negative Case: 짧은 설명` | included | `SKILL.md` Routing | Simple field rename or short API question must not trigger full workflow. |
| `### Negative Case: false subagent claim` | included | `SKILL.md` Runtime Rules | Runtime forbids claiming tests, validation, review, browser checks, or subagent work not actually executed. |

## API Reference Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `architecture-api/final.md` `## 목차` | omitted | n/a | Navigation only. |
| `## 1. REST 아키텍처 원칙` | included | `rest-contracts.md` | Resource, representation, stateless, uniform interface included. |
| `### 1.1 REST 정의` / `### 1.2 구성 요소` | merged | `rest-contracts.md` | REST concept summarized as runtime contract shape. |
| `### 1.3 핵심 원칙` | included | `rest-contracts.md` | Stateless, resource-based, uniform interface included. |
| `### 1.4 REST의 한계` | included | `rest-contracts.md` | Practical trade-off note included. |
| `## 2. HTTP 메서드와 멱등성` | included | `rest-contracts.md`, `idempotency-openapi.md` | Method semantics and duplicate-sensitive POSTs included. |
| `### 2.1 메서드별 안전성과 멱등성` | included | `rest-contracts.md` | Safe/idempotent method matrix summarized. |
| `### 2.2 PUT vs PATCH` | included | `rest-contracts.md` | Full replacement vs partial update included. |
| `### 2.3 메서드-리소스 매트릭스` | merged | `rest-contracts.md` | Resource/method mapping guidance summarized. |
| `## 3. URL/리소스 설계 규칙` | included | `rest-contracts.md` | URL naming, subresources, query patterns included. |
| `### 3.1 명명 규칙` | included | `rest-contracts.md` | Nouns, plural, kebab-case, no DB leakage included. |
| `### 3.2 계층적 하위 리소스` | included | `rest-contracts.md` | Parent-child and depth limit included. |
| `### 3.3 필터링, 정렬, 검색 패턴` | included | `rest-contracts.md` | Query parameter usage included. |
| `## 4. HTTP 상태 코드` | included | `rest-contracts.md` | Common 2xx/4xx/5xx API statuses included. |
| `### 4.1 분류` / `### 4.2 API에서 자주 사용하는 상태 코드` | included | `rest-contracts.md` | Status categories and common codes included. |
| `### 4.3 PRG (POST/Redirect/GET) 패턴` | included | `rest-contracts.md`, `idempotency-openapi.md` | `303 See Other` and PRG duplicate prevention guidance included. |
| `## 5. 에러 응답 형식 (RFC 9457)` | included | `problem-details.md` | Problem Details contract included. |
| `### 5.1 Problem Details for HTTP APIs` | included | `problem-details.md` | Core fields included. |
| `### 5.2 예시` | merged | `problem-details.md` | Example semantics converted to field guidance. |
| `### 5.3 핵심 규칙` | included | `problem-details.md` | Stable type/title/detail consistency included. |
| `## 6. HTTP 헤더와 콘텐츠 협상` | included | `rest-contracts.md` | Representation, negotiation, cache headers included. |
| `### 6.1 표현 관련 헤더` / `### 6.2 콘텐츠 협상` | included | `rest-contracts.md` | Content-Type and Accept-family headers included. |
| `### 6.3 캐시 관련 헤더` | included | `rest-contracts.md` | Cache validators and 304 included. |
| `## 7. 인증과 인가` | included | `rest-contracts.md` | Authentication/authorization distinction and security principles included. |
| `### 7.1 인증 vs 인가` | included | `rest-contracts.md` | 401 vs 403 included. |
| `### 7.2 인증 메커니즘 선택 기준` | included | `rest-contracts.md` | API key, OAuth 2.0, and JWT contract selection included without framework implementation detail. |
| `### 7.3 API 요청의 보안 원칙` | included | `rest-contracts.md` | Authorization header, no secrets in query, HTTPS included. |
| `## 8. 페이지네이션` | included | `pagination-versioning.md` | Offset, cursor, keyset and response metadata included. |
| `### 8.1 세 가지 접근법` / `### 8.2 선택 기준` | included | `pagination-versioning.md` | Selection by dataset and consistency included. |
| `### 8.3 실전 원칙` | included | `pagination-versioning.md` | Stable unique ordering, opaque cursor, `has_more`/`next_cursor` included. |
| `## 9. 버전 관리` | included | `pagination-versioning.md` | URL/header/query strategy and consistency included. |
| `### 9.1 세 가지 전략` / `### 9.2 Stripe의 날짜 기반 버전 관리` | merged | `pagination-versioning.md` | Versioning options and common compromise included. |
| `### 9.3 실전 원칙` | included | `pagination-versioning.md` | Consistent strategy and migration path included. |
| `## 10. 하위 호환성과 Deprecation` | included | `pagination-versioning.md` | Breaking changes and deprecation process included. |
| `### 10.1 Breaking vs Non-Breaking Change` | included | `pagination-versioning.md` | Breaking/non-breaking examples included. |
| `### 10.2 Deprecation 프로세스` | included | `pagination-versioning.md` | Notice, sunset/deprecation, migration window included. |
| `### 10.3 실전 원칙` | included | `pagination-versioning.md` | Additive changes and versioning for breaking changes included. |
| `## 11. Rate Limiting` | included | `pagination-versioning.md` | Headers, 429, algorithm choices included. |
| `### 11.1 Rate Limit 헤더` / `### 11.2 429 Too Many Requests` | included | `pagination-versioning.md` | Retry and quota headers included. |
| `### 11.3 알고리즘 선택 기준` / `### 11.4 실전 원칙` | included | `pagination-versioning.md` | Algorithm selection and early checks included. |
| `## 12. 멱등성 키 (Idempotency-Key)` | included | `idempotency-openapi.md` | Duplicate-sensitive POST contract included. |
| `### 12.1 문제` | included | `idempotency-openapi.md` | Lost response/retry duplicate risk included. |
| `### 12.2 Idempotency-Key 패턴` | included | `idempotency-openapi.md` | Key generation, replay, retention behavior summarized. |
| `### 12.3 실전 원칙` | included | `idempotency-openapi.md` | Durable storage and race handoff included. |
| `## 13. OpenAPI` | included | `idempotency-openapi.md` | OpenAPI contract impact included. |
| `### 13.1 OpenAPI란` / `### 13.2 용도` | merged | `idempotency-openapi.md` | API testing, consistency, SDK/doc uses summarized. |
| `### 13.3 실전 원칙` | included | `idempotency-openapi.md` | Keep OpenAPI aligned with design included. |
| `## 14. 참고 문헌` | omitted | n/a | Bibliography is source provenance, not runtime behavior. |

## Review Notes

- 2026-05-10 source self-review in the current evaluation loop found source-backed gaps in direct API contract vs workflow routing, Korean trigger coverage for auth/header/compatibility language, `### Source Coverage Crosswalk` heading tracking, `spec.md` child-heading coverage, `ddd-implementation-standard.md` heading coverage, validation scenario heading coverage, metadata specificity, and stale review/rubric completion claims from an earlier draft. Runtime files and this crosswalk were updated.
- Independent source review initially found a minor crosswalk gap for `ddd-implementation-standard.md` `## 7. Django ORM 매핑`; this crosswalk was updated to delegate ORM mapping to `implementation-django` and `architecture-db`. Independent source re-review returned blocking 0, major 0, minor 0.
- Rubric review was performed only after source review. A source-backed runtime issue was found: API contract output should state acceptance criteria for status codes, Problem Details, idempotency replay/conflict, pagination, and compatibility when relevant. `SKILL.md` was updated with that runtime rule. Independent rubric review returned blocking 0, major 0, minor 0, and no runtime leakage concern.
- Runtime checks were executed with `codex debug prompt-input` for a positive API contract prompt, a coordinated DDD/DB/API/Django/test boundary prompt, and a simple Django field-rename negative prompt. The positive prompt exposed `architecture-api`; the boundary prompt exposed the workflow/API metadata needed for coordinated routing; the negative prompt did not require API contract work.
- Isolated read-only `codex exec` smoke outputs were written under `/private/tmp/api-smoke`. The positive sample produced REST contract, status code, Problem Details, `Idempotency-Key`, OpenAPI, auth/error, and no-test-claim behavior. The boundary sample produced `Role Map`, `Sequential Fallback`, `Handoff Contract`, and `Integration Checklist` without claiming actual subagent execution. The negative sample stayed outside API/OpenAPI design and reported no target Django code.
- Validator, leakage check, cache diff, and plan update are part of the final completion commands for this skill. Completion requires those commands to pass after this crosswalk update.
