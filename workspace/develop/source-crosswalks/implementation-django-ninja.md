# Source Coverage Crosswalk: implementation-django-ninja

## Status

- Skill: `implementation-django-ninja`
- Runtime target: `dddjango/skills/implementation-django-ninja/`
- Source status: provisional until dedicated Django Ninja source reference exists
- Source policy decision: `allow-provisional-with-fallback`
- Fallback source: `workspace/reference/architecture-api/reference/final.md`, `workspace/docs` product decisions, and `workspace/reference/implementation-django/reference/final.md` DRF section only for legacy review/migration/comparison
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `router-schema.md`, `auth-pagination-filtering.md`, `problem-details-openapi.md`, `testclient.md`
- Rubric status: not opened during draft; reserved for post-source-review verification

## Sources Used

- `workspace/develop/skill_goal_instructions.md`
- `workspace/docs/plugin-structure.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/skill-hierarchy.md`
- `workspace/docs/skill-authoring.md`
- `workspace/docs/reference-index.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/workflow.md`
- `workspace/docs/validation-plan.md`
- `workspace/reference/architecture-api/reference/final.md`
- `workspace/reference/implementation-django/reference/final.md` section `## 8. Django REST Framework 패턴`

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | `SKILL.md`, this crosswalk | Runtime target and crosswalk path followed. |
| `## 실행 규칙` | included | this crosswalk, review notes | One-skill sequencing, rubric isolation, honest verification followed. |
| `## 구현 순서` | included | `plan.md` update | Continued after completed `implementation-django`. |
| `## Skill별 작성 루프` / `### Source Coverage Crosswalk` | included | this crosswalk | Source coverage tracked before rubric. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter only `name` and `description`; concise body with direct references. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | Source summarized into runtime references; no source copy. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata is aligned and provisional. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description/routing | Korean/mixed triggers include Router/Schema 구현, 인증/인가, 페이지네이션, 필터링/정렬, 오류 응답, API 계약 테스트 기준, Problem Details/OpenAPI, and DRF ViewSet/APIView/Serializer를 Ninja로 전환. |
| `## Provisional Skill 처리` | included | `SKILL.md`, this crosswalk, `agents/openai.yaml` | Source limitation, fallback source, and policy decision recorded. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | Delegates REST contract, domain, ORM/migration, web, explicit subagent, and composite/risky workflow cases. |
| `## Review 기준` | included | review notes | Source/rubric categories used. |
| `## Completed 조건` | included | review notes, validation | Provisional completed criteria checked. |
| `## 검증` | included | final report | Validation commands tracked. |
| `## 완료 보고` | included | final report | Required report fields tracked. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt template for future runs; not runtime skill guidance, but accounted for by this crosswalk. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files are under repo-root plugin artifact. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/implementation-django-ninja/` | Plugin-bundled structure used; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, boundaries only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name, responsibility, Django Ninja standard, and verification rules preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before draft. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Used exact split for `implementation-django-ninja`. |
| `## 8. 금지 사항` | included | file tree | No README/changelog/install guide; no false validation claim. |
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Unclear domain rules route to DDD. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | `SKILL.md` Routing | Implementation architecture decisions are outside this skill. |
| `## architecture-db` | delegated-to-other-skill | `SKILL.md`, `problem-details-openapi.md` | Undecided idempotency storage, unique constraints, locking, isolation, retry, and DB consistency decisions route to DB architecture. |
| `## architecture-api` | delegated-to-other-skill | `SKILL.md` Routing | Undecided REST contract belongs to API architecture. |
| `## implementation-django` | delegated-to-other-skill | `SKILL.md` Routing | ORM/service/migration/transaction implementation belongs to Django skill. |
| `## implementation-django-ninja` | included | `SKILL.md`, all references | Router, URL registration, Schema/ModelSchema, auth, pagination, FilterSchema, Problem Details, OpenAPI, TestClient covered. |
| `## implementation-django-web` | delegated-to-other-skill | `SKILL.md` Routing | Template/static/page work is not API implementation. |
| `## implementation-python` | delegated-to-other-skill | `router-schema.md` | Python typing details are not owned here. |
| `## implementation-tdd` | delegated-to-other-skill | `testclient.md` | TDD methodology belongs to TDD skill. |
| `## implementation-test` | delegated-to-other-skill | `SKILL.md`, `testclient.md` | Fixture/mock, concurrency test mechanics, and detailed pytest implementation belong to test skill; this skill states Django Ninja TestClient acceptance criteria. |
| `## implementation-cleancode` | delegated-to-other-skill | runtime rules | Broad refactoring/review belongs to clean-code skill. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Role decomposition requests route to workflow. |
| `## 공통 필수 출력` / `### Risky Write Consistency Block` | merged | `problem-details-openapi.md`, `testclient.md` | API-facing idempotency and test criteria included; full block owned by composite workflow/risky write context. |
| `reference-index.md` `## Architecture` | merged | `problem-details-openapi.md`, `auth-pagination-filtering.md` | API source is fallback for API behavior. |
| `## Implementation` | included | `SKILL.md` Fallback Source | Django Ninja source gap and fallback reflected. |
| `## Reference 사용 원칙` | included | this crosswalk | Used final source; did not copy long prose. |
| `## Reference Gap` | included | `SKILL.md`, this crosswalk | Provisional policy recorded. |
| `## DRF Guardrail` | included | `SKILL.md`, `router-schema.md` | DRF only for legacy/migration/comparison; greenfield standard is Ninja. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md` | Django Ninja product decision and API standards reflected. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` frontmatter | Description is trigger/routing centered. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | Draft, positive signals, negative routing, Korean triggers merged. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Simple implementation direct; undecided contracts route upward. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Provisional metadata aligned. |
| `skill-hierarchy.md` all headings | included | `SKILL.md` Routing | Bottom implementation skill with upward delegation. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Relevant API implementation point reflected. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple API implementation stays direct; composite/risky DDD+DB/API+test or duplicate-prevention work routes to workflow. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow role map belongs to workflow skill. |
| `## 4. Sequential Fallback` | delegated-to-other-skill | `workflow-dddjango-subagents` | Not this skill’s runtime responsibility. |
| `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Not this skill’s runtime responsibility. |
| `## 6. 통합 우선순위` | merged | `SKILL.md`, references | API contract after domain/data/transaction priorities reflected through routing. |
| `## 7. Integration Checklist` | merged | `problem-details-openapi.md`, `testclient.md` | API contract, implementation mapping, and tests reflected. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references are directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md`, `testclient.md` | Honest verification rule included. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | merged | `SKILL.md` Routing | Domain/DB/API decisions precede implementation when unclear. |
| `## 2. 하위 도메인별 구현 강도` | merged | `SKILL.md` | Does not force DDD/workflow for simple API implementation. |
| `## 3. 바운디드 컨텍스트와 언어` | delegated-to-other-skill | `architecture-ddd` | Strategic modeling responsibility. |
| `## 4. 애그리거트와 불변식` | merged | `SKILL.md`, `router-schema.md` | Router must not own invariants. |
| `## 5. Domain Events` | delegated-to-other-skill | `implementation-django`, workflow | Event dispatch timing belongs to service/domain implementation. |
| `## 6. Application Service와 Domain Service` | merged | `SKILL.md`, `router-schema.md` | Router calls usecase/service; does not own core rules. |
| `## 7. Django ORM 매핑` | delegated-to-other-skill | `implementation-django` | ORM/domain mapping belongs to Django implementation. |
| `## 8. Repository와 Transaction` | merged | `problem-details-openapi.md` | Idempotency and transaction coordination included; transaction implementation delegated. |
| `## 9. API 매핑` | included | `SKILL.md`, all references | Thin Router, Problem Details, response schema, OpenAPI included. |
| `## 10. Python 매핑` | delegated-to-other-skill | `implementation-python` | Python typing details belong elsewhere. |
| `## 11. 테스트 매핑` | included | `testclient.md` | Django Ninja API TestClient acceptance criteria included. |
| `validation-plan.md` `## 1. 검증 원칙` | included | review notes | Real artifacts and honest verification used. |
| `## 2. 대표 시나리오` | merged | references | 주문 생성 API and DRF-to-Ninja scenarios reflected; unrelated scenarios delegated. |
| `### 주문 생성 API` | included | `problem-details-openapi.md`, `testclient.md` | Problem Details, idempotency, OpenAPI, and API contract test criteria included. |
| `### DRF to Django Ninja 전환` | included | `router-schema.md`, `problem-details-openapi.md`, `testclient.md` | Legacy DRF conversion and compatibility reflected. |
| `### Negative Case: false subagent claim` | included | `SKILL.md`, `testclient.md` | Verification honesty reflected. |
| `## 3. 평가 항목` | included | review notes | Product checks used in source review. |
| `## 4. Skill Folder 검증` | included | validation | Folder structure and commands followed where possible. |

## Fallback Source Heading Coverage

| Heading | Status | Runtime location | Reason |
|---|---|---|---|
| `architecture-api/final.md` `## 목차` | omitted | n/a | Source navigation only. |
| `## 1. REST 아키텍처 원칙` | merged | `router-schema.md` | Resource/representation/stateless adapter ideas reflected. |
| `### 1.1 REST 정의` | merged | `router-schema.md` | REST as API contract background, not copied. |
| `### 1.2 구성 요소` | included | `router-schema.md` | Resource/method/representation mapped to Router/Schema. |
| `### 1.3 핵심 원칙` | included | `router-schema.md` | Stateless and uniform interface reflected. |
| `### 1.4 REST의 한계` | omitted | n/a | General background not runtime procedure. |
| `## 2. HTTP 메서드와 멱등성` | included | `problem-details-openapi.md` | Method/status/idempotency behavior reflected. |
| `### 2.1 메서드별 안전성과 멱등성` | included | `problem-details-openapi.md` | POST/idempotency and method behavior included. |
| `### 2.2 PUT vs PATCH` | delegated-to-other-skill | `architecture-api` | Contract choice belongs to API architecture if undecided. |
| `### 2.3 메서드-리소스 매트릭스` | delegated-to-other-skill | `architecture-api` | Resource/method design belongs to API architecture. |
| `## 3. URL/리소스 설계 규칙` | delegated-to-other-skill | `architecture-api` | URL/resource design must be decided before implementation. |
| `### 3.1 명명 규칙` | delegated-to-other-skill | `architecture-api` | Naming contract is API architecture. |
| `### 3.2 계층적 하위 리소스` | delegated-to-other-skill | `architecture-api` | Resource hierarchy is API architecture. |
| `### 3.3 필터링, 정렬, 검색 패턴` | included | `auth-pagination-filtering.md` | Implementation validates filters/sorts once contract exists. |
| `## 4. HTTP 상태 코드` | included | `problem-details-openapi.md` | Status-code implementation mapping included. |
| `### 4.1 분류` | merged | `problem-details-openapi.md` | Categories summarized into implementation rules. |
| `### 4.2 API에서 자주 사용하는 상태 코드` | included | `problem-details-openapi.md` | Common statuses included. |
| `### 4.3 PRG 패턴` | delegated-to-other-skill | `implementation-django-web` | Web form redirect pattern, not API implementation. |
| `## 5. 에러 응답 형식 (RFC 9457)` | included | `problem-details-openapi.md` | Problem Details standard included. |
| `### 5.1 Problem Details for HTTP APIs` | included | `problem-details-openapi.md` | Required fields, `application/problem+json`, and `instance` reflected. |
| `### 5.2 예시` | merged | `problem-details-openapi.md` | Example generalized, not copied. |
| `### 5.3 핵심 규칙` | included | `problem-details-openapi.md` | `type`, `title`, `detail`, consistency rules included. |
| `## 6. HTTP 헤더와 콘텐츠 협상` | merged | `auth-pagination-filtering.md`, `problem-details-openapi.md` | Headers relevant to auth/rate/idempotency/cache reflected. |
| `### 6.1 표현 관련 헤더` | merged | `problem-details-openapi.md` | Content-Type status/error handling reflected. |
| `### 6.2 콘텐츠 협상` | delegated-to-other-skill | `SKILL.md` Routing | Fallback API source covers content negotiation; undecided header/media/language behavior routes to `architecture-api` because no dedicated Django Ninja source exists. |
| `### 6.3 캐시 관련 헤더` | delegated-to-other-skill | `architecture-api` / `implementation-django` | Cache contract/storage not central to Ninja implementation. |
| `## 7. 인증과 인가` | included | `auth-pagination-filtering.md` | 401/403, header auth, boundary included. |
| `### 7.1 인증 vs 인가` | included | `auth-pagination-filtering.md` | 401 vs 403 included. |
| `### 7.2 인증 메커니즘 선택 기준` | delegated-to-other-skill | `architecture-api` | Mechanism selection is API architecture unless already chosen. |
| `### 7.3 API 요청의 보안 원칙` | included | `auth-pagination-filtering.md` | Authorization header, no query secrets, and HTTPS included. |
| `## 8. 페이지네이션` | included | `auth-pagination-filtering.md` | Pagination implementation concerns included. |
| `### 8.1 세 가지 접근법` | merged | `auth-pagination-filtering.md` | Offset/cursor/keyset summarized. |
| `### 8.2 선택 기준` | included | `auth-pagination-filtering.md` | Strategy choice reflected, undecided choice routes to API architecture. |
| `### 8.3 실전 원칙` | included | `auth-pagination-filtering.md` | Max page size and cursor stability included. |
| `## 9. 버전 관리` | included | `auth-pagination-filtering.md` | Versioning compatibility guidance included. |
| `### 9.1 세 가지 전략` | delegated-to-other-skill | `architecture-api` | Strategy selection is API architecture. |
| `### 9.2 Stripe의 날짜 기반 버전 관리` | omitted | n/a | Provider example not runtime guidance. |
| `### 9.3 실전 원칙` | merged | `auth-pagination-filtering.md` | Consistent strategy and migration route reflected. |
| `## 10. 하위 호환성과 Deprecation` | included | `router-schema.md`, `auth-pagination-filtering.md` | Compatibility and additive-change guidance included. |
| `### 10.1 Breaking vs Non-Breaking Change` | included | `router-schema.md` | Breaking-change examples generalized. |
| `### 10.2 Deprecation 프로세스` | merged | `auth-pagination-filtering.md` | Deprecation window guidance summarized. |
| `### 10.3 실전 원칙` | included | `auth-pagination-filtering.md` | Additive changes and robustness reflected. |
| `## 11. Rate Limiting` | included | `auth-pagination-filtering.md` | Rate-limit implementation notes included. |
| `### 11.1 Rate Limit 헤더` | included | `auth-pagination-filtering.md` | Limit, remaining, and reset header guidance included when project exposes them. |
| `### 11.2 429 Too Many Requests` | included | `auth-pagination-filtering.md`, `problem-details-openapi.md` | 429 and `Retry-After` included. |
| `### 11.3 알고리즘 선택 기준` | delegated-to-other-skill | `architecture-api` | Algorithm selection is API architecture unless already chosen. |
| `### 11.4 실전 원칙` | included | `auth-pagination-filtering.md` | Check before expensive work and document policy. |
| `## 12. 멱등성 키 (Idempotency-Key)` | included | `problem-details-openapi.md`, `testclient.md` | Idempotency behavior and tests included. |
| `### 12.1 문제` | included | `problem-details-openapi.md` | Duplicate POST risk reflected. |
| `### 12.2 Idempotency-Key 패턴` | included | `problem-details-openapi.md` | Storage/replay/conflict included. |
| `### 12.3 실전 원칙` | included | `problem-details-openapi.md`, `testclient.md` | Risky POST, durable storage, race handling included. |
| `## 13. OpenAPI` | included | `problem-details-openapi.md` | OpenAPI effects and verification included. |
| `### 13.1 OpenAPI란` | omitted | n/a | General definition not runtime procedure. |
| `### 13.2 용도` | merged | `problem-details-openapi.md` | Schema tests/consistency reflected. |
| `### 13.3 실전 원칙` | included | `problem-details-openapi.md` | Keep documentation and implementation aligned. |
| `## 14. 참고 문헌` | omitted | n/a | Bibliography not runtime guidance. |
| `implementation-django/final.md` `## 8. Django REST Framework 패턴` | merged | `router-schema.md` | Used only for DRF legacy conversion/comparison. |
| `### 8.1 Serializer 설계` | merged | `router-schema.md` | Converted to request/response schema split; not DRF standard. |
| `### 8.2 ViewSet과 Router` | merged | `router-schema.md` | Converted to explicit Ninja operations; no greenfield DRF. |
| `### 8.3 Permission 패턴` | merged | `auth-pagination-filtering.md` | Permission boundary reflected, not DRF-specific classes. |
| `### 8.4 Pagination 설정` | merged | `auth-pagination-filtering.md` | Pagination compatibility reflected, not DRF-specific settings. |
| `### 8.5 API 버전 관리` | merged | `auth-pagination-filtering.md` | Version compatibility reflected, not DRF-specific versioning classes. |

## Review Notes

- Source self-review: fixed 1 major finding before external review: runtime `SKILL.md` no longer exposes workspace-only source paths as final reference paths while still naming the provisional fallback source. Later evaluation pass fixed test implementation boundary wording, `Goal Objective Template` crosswalk coverage, `architecture-db` idempotency/locking routing, Korean trigger coverage, and content negotiation delegation. Blocking 0, major 0, minor 0 after fix.
- Skill-creator review: 0 findings after checking frontmatter-only metadata, trigger-centered description, concise body, direct one-level reference links, provisional disclosure, no TODO placeholders, no banned auxiliary docs, and no runtime rubric leakage.
- Independent review subagent `Meitner` executed: fixed 4 major and 4 minor findings from the first pass, then fixed 1 major and 1 minor from re-review by making composite/risky workflow precedence the first routing rule and updating stale trigger text in the crosswalk. Final re-review reported blocking 0, major 0, minor 0.
- Rubric review: fixed 2 source-backed minor runtime issues after opening rubric: made simple explanation/tiny Router edit anti-overapplication explicit, and added URL registration plus `FilterSchema` coverage. Eval-only rubric material was not copied into runtime docs. Blocking 0, major 0, minor 0 after fix.
