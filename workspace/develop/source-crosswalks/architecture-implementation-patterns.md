# Source Coverage Crosswalk: architecture-implementation-patterns

## Status

- Skill: `architecture-implementation-patterns`
- Runtime target: `dddjango/skills/architecture-implementation-patterns/`
- Source status: provisional until dedicated source reference exists
- Source policy decision: `allow-provisional-with-fallback`
- Fallback sources: `architecture-ddd/reference/final.md`, `implementation-django/reference/final.md`, `implementation-python/reference/final.md`, and product docs
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `pattern-selection.md`, `ports-adapters.md`, `repository-uow.md`, `outbox-acl.md`
- Rubric status: not opened during draft; reserved for post-source-review verification

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
- `workspace/reference/architecture-ddd/reference/final.md` selected fallback sections
- `workspace/reference/implementation-django/reference/final.md` selected fallback sections
- `workspace/reference/implementation-python/reference/final.md` selected fallback sections

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | runtime path, this crosswalk | Plugin-bundled target and crosswalk location followed. |
| `## 실행 규칙` | included | this workflow | One skill at a time; rubrics not used during draft. |
| `## 구현 순서` | included | plan order | This follows `architecture-ddd`. |
| `## Skill별 작성 루프` | included | this crosswalk, review notes | Source scope, draft, review, and rubric sequencing tracked. |
| `## Source Coverage Crosswalk` | included | this file | Source headings and runtime treatment tracked. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter has only name/description; body is concise and procedural. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | Four one-level references summarize fallback sources. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata aligns with provisional status. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description | Korean triggers for 헥사고날, 클린 아키텍처, 의존성 역전, repository/UoW, outbox, ACL, and 프로젝트 구조 included. |
| `## Provisional Skill 처리` | included | `SKILL.md`, this status | Provisional status, source policy decision, and fallback source scope are explicit. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | Workflow, DDD, DB, API, and implementation boundaries included. |
| `## Review 기준` | included | Review Notes | Review types and findings tracked. |
| `## Completed 조건` | included | Review Notes, validation report | Completion requires zero remaining blocking/major/minor findings; provisional conditions tracked. |
| `## 검증` | included | validation commands | Only executed validation will be reported. |
| `## 완료 보고` | included | final report | Required report fields will be included. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt authoring content is not runtime behavior. |
| `spec.md` `## 관련 문서` | included | Sources Used | Linked product docs are covered. |
| `## 1. 목표` | included | `SKILL.md`, references | DDD model maps to implementation architecture before Django code. |
| `## 2. 설계 원칙` | included | references | Strategy before tactics, aggregate consistency, outbox, Django pragmatism, and adapter boundaries included. |
| `## 3. 스킬 종류` | included | `SKILL.md` Routing | Implementation-pattern responsibility and adjacent skill boundaries included. |
| `## 4. 산출물 기준` | included | `SKILL.md`, references | Pattern decisions, dependency direction, integration boundaries, and handoffs included. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/architecture-implementation-patterns/` | Plugin-bundled structure used; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name and responsibility preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for provisional skill used. |
| `## 8. 금지 사항` | included | file tree, `SKILL.md` | No auxiliary docs; no false validation claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` | Trigger/routing and boundaries are in description/body. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | Provisional status, patterns, Korean triggers, and negative routing included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | DDD precedes pattern selection; DB/API/implementation route away when primary. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align with provisional status. |
| `reference-index.md` `## Architecture` | included | `SKILL.md`, references | Implementation-pattern fallback source set followed. |
| `## Implementation` | included | references | Django and Python fallback sections used only for pattern boundary decisions. |
| `## Reference 사용 원칙` | included | references | Runtime references summarize source and avoid copying `final.md`. |
| `## Reference Gap` | included | `SKILL.md`, this status | Dedicated source gap and provisional treatment explicit. |
| `## DRF Guardrail` | delegated-to-other-skill | `implementation-django-ninja` | API framework choice outside implementation-pattern selection. |
| `## Reference에서 도출한 제품 결정` | included | references | Strategy before tactics, Django pragmatism, outbox/eventual consistency, and implementation mapping reflected. |

## Contracts, Workflow, And Standard Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Unclear domain boundaries route to DDD first. |
| `## architecture-implementation-patterns` | included | `SKILL.md`, references | Pattern choice, dependency direction, port/adapter, repository, CQRS, outbox, ACL, and non-use reasons covered. |
| `## architecture-db` / `## architecture-api` | delegated-to-other-skill | `SKILL.md` Routing | Schema/transaction/API contract design routes away. |
| `## implementation-django` / `## implementation-django-ninja` / `## implementation-django-web` | delegated-to-other-skill | implementation skills | Concrete Django code routes away after pattern decision. |
| `## implementation-python` | delegated-to-other-skill | `implementation-python` | Python syntax/type mechanics route away; Protocol boundary concept used as fallback. |
| `## implementation-cleancode` | delegated-to-other-skill | `implementation-cleancode` | General refactoring quality routes away unless architecture pattern decision is central. |
| `## implementation-tdd` / `## implementation-test` | delegated-to-other-skill | test skills | Test method and pytest mechanics route away. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Composite/subagent work routes to workflow. |
| `## 공통 필수 출력` / `### Risky Write Consistency Block` | included | `SKILL.md`, `outbox-acl.md` | Pattern skill identifies transaction owner and side-effect/reliability boundary, then hands DB locking/isolation, API idempotency, and test criteria to owning skills. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | Pattern skill sits after DDD and before DB/API/implementation when structure is unresolved. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Pattern choice follows DDD and precedes implementation mapping. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple work direct; composite/subagent work routes to workflow. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | Architecture Agent role belongs to workflow skill. |
| `## 4. Sequential Fallback` / `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow orchestration belongs elsewhere. |
| `## 6. 통합 우선순위` | merged | `SKILL.md`, references | Pattern decisions inform DB/API/Django/Test handoffs. |
| `## 7. Integration Checklist` | merged | references | Data/API/implementation/test follow-up boundaries included. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md` Runtime Rules | Only actual validation may be claimed. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | included | `SKILL.md`, `pattern-selection.md` | DDD model must be clear before patterns. |
| `## 2. 하위 도메인별 구현 강도` | included | `pattern-selection.md` | Core/supporting/generic affects pattern weight. |
| `## 3. 바운디드 컨텍스트와 언어` | delegated-to-other-skill | `architecture-ddd`, `ports-adapters.md` | DDD owns model; ACL uses language boundary when integration needs it. |
| `## 4. 애그리거트와 불변식` | delegated-to-other-skill | `architecture-ddd`, `repository-uow.md` | DDD owns aggregate; repository/UoW decisions depend on aggregate boundary. |
| `## 5. Domain Events` | included | `outbox-acl.md` | Dispatch timing, outbox, internal/integration event distinction included. |
| `## 6. Application Service와 Domain Service` | included | `repository-uow.md`, `ports-adapters.md` | Use case orchestration and boundary dependency direction reflected. |
| `## 7. Django ORM 매핑` | included | `pattern-selection.md`, `repository-uow.md` | Django model vs pure domain split decision included. |
| `## 8. Repository와 Transaction` | included | `repository-uow.md`, `outbox-acl.md` | Repository, transaction owner, side effect timing, and idempotency handoff reflected. |
| `## 9. API 매핑` | delegated-to-other-skill | `architecture-api`, `implementation-django-ninja` | API contract design and implementation route away; adapter boundary retained. |
| `## 10. Python 매핑` | delegated-to-other-skill | `implementation-python`, `ports-adapters.md` | Protocol boundary concept used; detailed Python mechanics delegated. |
| `## 11. 테스트 매핑` | delegated-to-other-skill | `implementation-test`, `implementation-tdd` | Test design consumes pattern decision; mechanics route away. |
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md`, validation report | Real prompt/artifact/diff/test evidence and over-application checks reflected. |
| `## 2. 대표 시나리오` / `### Architecture Pattern Selection` | included | `SKILL.md`, `pattern-selection.md`, `outbox-acl.md` | Hexagonal/repository/outbox prompt covered through need/cost comparison, ACL, transaction boundary, and outbox decision. |
| `### Negative Case: 단순 필드 rename` / `### Negative Case: 짧은 설명` | included | `SKILL.md` Routing | Simple field rename or short explanation must not trigger heavy pattern structure. |
| `### Negative Case: false subagent claim` | included | `SKILL.md` Runtime Rules | Only actually executed subagent work may be reported. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Pattern fit, anti-overapplication, source limitation, and verification honesty reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder will be checked; missing future skills are reported separately. |

## Fallback Reference Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `architecture-ddd/final.md` `## 5. 아키텍처` | included | `pattern-selection.md`, `ports-adapters.md` | Layered architecture, DIP, hexagonal, CQRS, and large structure reflected. |
| `### 5.1 계층 아키텍처` | included | `pattern-selection.md`, `ports-adapters.md` | Layered default and inward dependencies included. |
| `### 5.2 DIP` | included | `ports-adapters.md` | High-level modules depend on abstractions; implementation in adapters. |
| `### 5.3 핵사고날 아키텍처` | included | `pattern-selection.md`, `ports-adapters.md` | Ports/adapters decision and provisional limitation included. |
| `### 5.4 CQRS` | included | `pattern-selection.md` | CQRS as optional, not top-level default, included. |
| `### 5.5 대규모 구조` | merged | `pattern-selection.md` | Large-scale structure treated as conditional, not default upfront design. |
| `architecture-ddd/final.md` `## 6. 구현 패턴` | included | references | Package, data mapper, repository/UoW, event sourcing, saga, simple logic, and microservice integration reflected. |
| `### 6.1 패키지 구조` | included | `pattern-selection.md`, `ports-adapters.md` | Four-layer fallback and Django simplified structure included. |
| `### 6.2 SQLAlchemy Data Mapper 패턴` | merged | `repository-uow.md` | Data Mapper split condition reflected; SQLAlchemy-specific mechanics omitted from Django-focused runtime. |
| `### 6.3 Repository + Unit of Work 패턴` | included | `repository-uow.md` | Repository and UoW decision criteria included. |
| `### 6.4 Event Sourcing` | included | `outbox-acl.md`, `pattern-selection.md` | Event sourcing as conditional history/replay choice included. |
| `### 6.5 Saga 패턴` | included | `outbox-acl.md`, `pattern-selection.md` | Saga triggers and compensation included. |
| `### 6.6 단순한 비즈니스 로직 패턴` | included | `pattern-selection.md` | Transaction script/simple service path for supporting domains included. |
| `### 6.7 마이크로서비스와 DDD` | included | `outbox-acl.md`, `ports-adapters.md` | Integration events, ACL, and bounded-context integration included. |
| `implementation-django/final.md` `## 3. 프로젝트 구조와 앱 설계` | included | `pattern-selection.md`, `ports-adapters.md` | Django project/app structure informs pragmatic structure decisions. |
| `### 3.1 프로젝트 레이아웃` | merged | `pattern-selection.md` | Project layout informs Django-native default; exact tree omitted. |
| `### 3.2 앱 분리 기준` | included | `pattern-selection.md` | App cohesion and cycle checks reflected. |
| `implementation-django/final.md` `## 4. 모델 설계 패턴` / `### 4.1 Fat Model, Thin View` | included | `repository-uow.md`, `ports-adapters.md` | Model/service/adapter boundary reflected. |
| `implementation-django/final.md` `## 16. Django와 서비스 레이어 아키텍처` | included | `repository-uow.md`, `pattern-selection.md` | Service layer triggers, services/selectors, and Django-vs-DDD trade-offs included. |
| `### 16.1 서비스 레이어가 필요한 시점` | included | `repository-uow.md` | Multi-model logic, duplication, external service triggers included. |
| `### 16.2 HackSoft 서비스/셀렉터 패턴` | included | `repository-uow.md` | Write services and read selectors included. |
| `### 16.3 DDD와 Django의 트레이드오프` | included | `pattern-selection.md`, `repository-uow.md` | Django direct use vs repository trade-off included. |
| `implementation-python/final.md` `## 9. Protocol 심화` | included | `ports-adapters.md` | Protocol boundaries used for structural seams. |
| `### 9.1`-`### 9.5 Protocol` | merged | `ports-adapters.md` | Protocol use, composition, and runtime_checkable caution summarized. |
| `implementation-python/final.md` `## 21. Repository / Unit of Work` | source-gap | `SKILL.md`, this status | Python source itself points to future dedicated implementation-pattern reference; fallback status retained. |

## Review Notes

- Source self-review: local review found 1 minor issue: `agents/openai.yaml` did not make the provisional/fallback status explicit enough; fixed; remaining blocking/major/minor findings 0.
- Skill-creator/writing-skills review: no extraneous files, direct reference links, concise `SKILL.md`, one-level references, explicit provisional source policy, and frontmatter length under 1024; remaining blocking/major/minor findings 0 by local review.
- Independent subagent review: first pass found 0 blocking, 3 major, and 0 minor; fixes applied for validation-plan crosswalk coverage, risky-write common output coverage, and frontmatter `architecture-api` boundary; re-review reported blocking/major/minor findings 0.
- Rubric review: source-backed runtime issues 0 after prior source-review fixes; eval-only/private rubric details were not copied into runtime docs; rubric defects 0; accepted trade-offs 0; remaining blocking/major/minor findings 0.
