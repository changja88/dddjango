# Source Coverage Crosswalk: architecture-implementation-patterns

## Status

- Skill: `architecture-implementation-patterns`
- Runtime target: `dddjango/skills/architecture-implementation-patterns/`
- Source status: provisional until dedicated source reference exists
- Source policy decision: `allow-provisional-with-fallback`
- Fallback sources: `architecture-ddd/reference/final.md`, `implementation-django/reference/final.md`, `implementation-python/reference/final.md`, and product docs
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `pattern-selection.md`, `ports-adapters.md`, `repository-uow.md`, `outbox-acl.md`
- Rubric status: completed after source review; only source-backed runtime issues were reflected

## Sources Used

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
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Coordinated multi-role implementation or review, subagent, and role-decomposed Django work routes to workflow. Direct risky pattern selection remains this skill's responsibility. |
| `## 공통 필수 출력` | merged | `SKILL.md`, `outbox-acl.md` | Pattern skill owns pattern choice, transaction owner/use case, side-effect timing, reliability boundary, and uniqueness/idempotency storage need before handing detailed DB/API/Test work to owning skills. |
| `### Risky Write Consistency Block` | merged | `SKILL.md`, `outbox-acl.md` | Runtime now requires a visible section or table titled `Risky Write Consistency Block` with pattern decisions plus handoff for concrete locking/isolation/retry, `Idempotency-Key` behavior, and integration/concurrency tests. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | Pattern skill sits after DDD and before DB/API/implementation when structure is unresolved. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Pattern choice follows DDD and precedes implementation mapping. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple work direct; coordinated multi-role or subagent work routes to workflow, while standalone pattern selection stays here. |
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
| `## 2. 대표 시나리오` | merged | `SKILL.md`, references, scenario coverage table | Architecture-pattern scenario is direct; adjacent scenarios are delegated or merged by boundary. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Pattern fit, anti-overapplication, source limitation, and verification honesty reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder was checked with the final validator; missing future skills are reported separately. |

## Validation Scenario Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `validation-plan.md` `### 주문 생성 API` | merged | `SKILL.md`, `outbox-acl.md`, `repository-uow.md` | Order creation can need service layer, transaction owner, outbox, and idempotency storage decisions before DB/API/test details route away. |
| `### 쿠폰 정책 TDD` | delegated-to-other-skill | `architecture-ddd`, `implementation-tdd` | Coupon policy modeling and TDD mechanics route away unless pattern structure is explicitly requested. |
| `### DRF to Django Ninja 전환` | delegated-to-other-skill | `implementation-django-ninja`, `architecture-api` | API framework migration and REST contract decisions route away; pattern skill may only advise adapter boundaries if needed. |
| `### Fat Model 리뷰`, `### View Logic 리뷰` | merged | `repository-uow.md`, `ports-adapters.md`, `implementation-cleancode` | Pattern skill can identify service/selector or adapter boundaries; concrete review and refactor routing belongs to clean-code or implementation skills. |
| `### 운영 마이그레이션`, `### 트랜잭션과 동시성` | merged | `outbox-acl.md`, `repository-uow.md`, `architecture-db` | Pattern skill identifies transaction owner and reliability boundary; locking, isolation, and rollout details route to DB. |
| `### Django Web` | delegated-to-other-skill | `implementation-django-web` | Template/static/web implementation routes away unless adapter boundary is the central question. |
| `### Python Typing` | delegated-to-other-skill | `implementation-python`, `ports-adapters.md` | Protocol boundary concept is included; detailed typing mechanics route away. |
| `### Architecture Pattern Selection` | included | `SKILL.md`, `pattern-selection.md`, `ports-adapters.md`, `repository-uow.md`, `outbox-acl.md` | Hexagonal, repository, outbox, ACL, and transaction-boundary trade-offs are this skill's primary scenario. |
| `### Negative Case: 단순 필드 rename`, `### Negative Case: 짧은 설명` | included | `SKILL.md` Routing | Simple field rename or short explanation must not trigger heavy pattern structure. |
| `### Negative Case: false subagent claim` | included | `SKILL.md` Runtime Rules | Runtime forbids claiming tests, validation, review, browser checks, or subagent work not actually executed. |

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

- 2026-05-10 source self-review in the current evaluation loop found source-backed gaps in composite/risky workflow routing, Korean trigger coverage, layered dependency wording, `spec.md` child-heading tracking, validation scenario heading coverage, Risky Write Consistency Block handoff coverage, metadata specificity, and stale review completion claims from an earlier draft. Runtime files and this crosswalk were updated.
- 2026-05-10 independent source review found 1 major issue: direct risky pattern-selection prompts were routed too broadly to workflow. Runtime routing was narrowed so coordinated multi-role implementation/review goes to workflow, while direct hexagonal/repository/outbox/ACL/CQRS/saga decisions remain in this skill.
- 2026-05-10 rubric review found 1 source-backed runtime issue: risky-write outputs needed the named consistency block required by product docs. `SKILL.md` and `outbox-acl.md` were updated; rubric re-check returned blocking 0, major 0, minor 0.
- 2026-05-10 positive runtime smoke initially produced correct pattern decisions but missed the visible risky-write block heading. `SKILL.md` and `outbox-acl.md` now require a visible section or table titled `Risky Write Consistency Block`.
- Source and rubric review loops are closed with blocking 0, major 0, minor 0 after the runtime-smoke wording fix.
- Runtime checks completed: `codex debug prompt-input` exposed updated metadata for positive, boundary, and negative prompts. Read-only `codex exec` samples in `/private/tmp/pattern-smoke` covered direct payment pattern selection, coordinated workflow boundary, and simple `verbose_name` negative behavior. The positive re-check produced a visible `Risky Write Consistency Block`; boundary output used workflow headings and did not claim subagents; negative output stayed direct.
- Validator, leakage checks, cache diff, and plan update were executed after runtime cache sync.
