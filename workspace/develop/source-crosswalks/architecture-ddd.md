# Source Coverage Crosswalk: architecture-ddd

## Status

- Skill: `architecture-ddd`
- Runtime target: `dddjango/skills/architecture-ddd/`
- Source status: ready
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `strategic-design.md`, `tactical-patterns.md`, `context-map.md`, `domain-events.md`
- Rubric status: completed after source review; only source-backed runtime issues may be reflected

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
- `workspace/reference/architecture-ddd/reference/final.md`

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | runtime path, this crosswalk | Plugin-bundled target and crosswalk location followed. |
| `## 실행 규칙` | included | this workflow | One skill at a time; rubrics not used during draft. |
| `## 구현 순서` | included | plan order | This follows `implementation-test`. |
| `## Skill별 작성 루프` | included | this crosswalk, review notes | Source scope, draft, review, and rubric sequencing tracked. |
| `### Source Coverage Crosswalk` | included | this file | Source headings and runtime treatment tracked. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter has only name/description; body is concise and procedural. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | Four one-level references summarize source rather than copying it. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata aligns with source and runtime skill. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description | Korean triggers for DDD 설계, 도메인 모델링, 도메인 규칙, 상태 전이, 정책, 불변식, 하위 도메인, 바운디드 컨텍스트, 유비쿼터스 언어, 애그리거트, 컨텍스트 맵, 도메인 이벤트, and 일관성 경계 included. |
| `## Provisional Skill 처리` | omitted | n/a | This skill has dedicated source reference and is not provisional. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | Adjacent workflow, DB, API, implementation-pattern, and implementation boundaries included. |
| `## Review 기준` | included | Review Notes | Review types and findings tracked. |
| `## Completed 조건` | included | Review Notes, validation evidence | Completion requires zero remaining blocking/major/minor findings with executed validation evidence. |
| `## 검증` | included | Review Notes, validation commands | Only executed validation is reported. |
| `## 완료 보고` | included | plan and final report | Required report fields are tracked after completion. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt authoring content is not runtime behavior. |
| `spec.md` `## 관련 문서` | included | Sources Used | Linked product docs are covered. |
| `## 1. 목표` | included | `SKILL.md`, references | DDD model decisions guide DB/API/Django/test work. |
| `## 2. 설계 원칙` | included | `SKILL.md`, references | Domain boundary before implementation and adapter boundaries reflected. |
| `## 3. 스킬 종류` | included | `SKILL.md` Routing | DDD responsibility and adjacent skill boundaries included. |
| `### Core DDD` | included | `SKILL.md`, references | DDD modeling responsibilities are this skill's core scope. |
| `### Implementation Mapping` | delegated-to-other-skill | `SKILL.md` Routing | Django/Python concrete implementation routes away after domain decisions. |
| `### Supporting Architecture` | merged | `SKILL.md` Routing | DB/API/pattern architecture receives DDD decisions through handoffs. |
| `### Quality` | merged | `SKILL.md`, references | DDD quality boundaries, anemic-model warning, and validation honesty are reflected. |
| `### Workflow` | delegated-to-other-skill | `SKILL.md` Routing, `workflow-dddjango-subagents` | Composite/risky role decomposition routes to workflow. |
| `## 4. 산출물 기준` | included | `SKILL.md`, references | Context, invariant, event, and use-case outputs included. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/architecture-ddd/` | Plugin-bundled structure used; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name and responsibility preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for `architecture-ddd` used. |
| `## 8. 금지 사항` | included | file tree, `SKILL.md` | No auxiliary docs; no false validation claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` | Trigger/routing and boundaries are in description/body. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | DDD/domain modeling signals and anti-routes included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Workflow precedes DDD only for composite/subagent work; DDD precedes DB/API when boundaries are unclear. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align. |
| `reference-index.md` `## Architecture` | included | references | DDD source reference used; implementation-pattern gap delegated. |
| `## Implementation` | delegated-to-other-skill | implementation skills | Implementation references are not DDD source except for handoffs. |
| `## Reference 사용 원칙` | included | references | Runtime references summarize source and avoid copying `final.md`. |
| `## Reference Gap` | included | `SKILL.md` Routing | Implementation-pattern provisional gap is delegated. |
| `## DRF Guardrail` | delegated-to-other-skill | `implementation-django-ninja` | API framework choice outside DDD modeling. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md`, references | Strategy before tactics and subdomain intensity reflected. |

## Contracts, Workflow, And DDD Standard Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | included | `SKILL.md`, references | Subdomains, bounded contexts, context map, language, aggregates, invariants, events, and use cases covered. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | `SKILL.md` Routing | Ports/adapters/repository implementation/CQRS/outbox structure routes away after DDD decisions. |
| `## architecture-db` / `## architecture-api` | delegated-to-other-skill | `SKILL.md` Routing | Schema/transaction/API contract design routes away after DDD boundaries. |
| `## implementation-django` / `## implementation-django-ninja` / `## implementation-django-web` | delegated-to-other-skill | `SKILL.md` Routing | Django code implementation is outside DDD modeling. |
| `## implementation-python` / `## implementation-cleancode` | delegated-to-other-skill | implementation skills | Python/refactor details route away unless naming/domain model quality is the current concern. |
| `## implementation-tdd` / `## implementation-test` | delegated-to-other-skill | test skills | Test method and pytest mechanics route away after invariants are known. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Composite, risky, subagent, and role-decomposed Django work routes to workflow. |
| `## 공통 필수 출력` | merged | workflow/implementation skills, `SKILL.md`, `domain-events.md` | DDD owns invariant, aggregate boundary, consistency boundary, and event/side-effect timing; transaction, locking, idempotency storage, API behavior, retry, and test criteria are assigned to workflow/DB/API/Test responsibilities unless this step explicitly owns them. |
| `### Risky Write Consistency Block` | merged | `SKILL.md`, `domain-events.md` | Runtime now requires a DDD-owned risky-write handoff before DB/API/test roles decide transaction ownership, locking, idempotency storage, `Idempotency-Key`, isolation/retry, and concurrency tests. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | DDD is a higher-order architecture skill before DB/API/implementation when rules are unclear. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Domain decisions feed DB/API/Django/Test handoffs. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple work direct; composite/risky/subagent work routes to workflow. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | Domain Agent role belongs to workflow skill. |
| `## 4. Sequential Fallback` / `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow orchestration belongs elsewhere. |
| `## 6. 통합 우선순위` | merged | `SKILL.md`, references | Domain/invariant decisions come before data/API/implementation/test details. |
| `## 7. Integration Checklist` | merged | `SKILL.md`, references | Domain and invariant checklist reflected. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md` Runtime Rules | Only actual validation may be claimed. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | included | `SKILL.md`, references | Domain first, then implementation handoff reflected. |
| `## 2. 하위 도메인별 구현 강도` | included | `strategic-design.md` | Core/supporting/generic intensity included. |
| `## 3. 바운디드 컨텍스트와 언어` | included | `strategic-design.md`, `context-map.md` | Context-scoped language included. |
| `## 4. 애그리거트와 불변식` | included | `tactical-patterns.md` | Aggregate boundary and invariant rules included. |
| `## 5. Domain Events` | included | `domain-events.md` | Event and dispatch timing included. |
| `## 6. Application Service와 Domain Service` | included | `tactical-patterns.md` | Service responsibility split included. |
| `## 7. Django ORM 매핑` / `## 8. Repository와 Transaction` | delegated-to-other-skill | `architecture-db`, `implementation-django`, `architecture-implementation-patterns` | Persistence design and concrete implementation route away. |
| `## 9. API 매핑` | delegated-to-other-skill | `architecture-api`, `implementation-django-ninja` | REST/API implementation routes away. |
| `## 10. Python 매핑` | delegated-to-other-skill | `implementation-python` | Python typing implementation routes away. |
| `## 11. 테스트 매핑` | delegated-to-other-skill | `implementation-tdd`, `implementation-test` | Tests consume DDD invariants; mechanics route away. |
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md` | Real executed validation only. |
| `## 2. 대표 시나리오` | merged | `SKILL.md`, references | Order API and coupon policy scenarios need DDD decisions before implementation/test. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Domain language, invariants, and over-application boundary reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder will be checked. |

## Validation Scenario Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `validation-plan.md` `### 주문 생성 API` | included | `SKILL.md`, `tactical-patterns.md`, `domain-events.md` | Order creation needs use case, invariant, aggregate/consistency boundary, event timing, and handoff decisions before DB/API/test implementation. |
| `### 쿠폰 정책 TDD` | included | `SKILL.md`, `tactical-patterns.md` | Coupon policy needs domain rule, invariant, value object/entity choice, and example boundaries before TDD/test mechanics. |
| `### DRF to Django Ninja 전환` | delegated-to-other-skill | `implementation-django-ninja`, `architecture-api` | API framework migration routes away unless domain language or adapter business-rule ownership is unclear. |
| `### Fat Model 리뷰`, `### View Logic 리뷰` | merged | `SKILL.md`, `tactical-patterns.md`, `implementation-cleancode` | DDD identifies misplaced domain rules and target domain/application ownership; concrete clean-code review routes away. |
| `### 운영 마이그레이션`, `### 트랜잭션과 동시성` | delegated-to-other-skill | `architecture-db`, this skill | DB mechanics route away; DDD supplies invariant and consistency boundary when unclear. |
| `### Django Web` | delegated-to-other-skill | `implementation-django-web` | Template/static/web implementation routes away; DDD only applies if web logic owns domain policy. |
| `### Python Typing` | delegated-to-other-skill | `implementation-python` | Typing implementation routes away. |
| `### Architecture Pattern Selection` | merged | `architecture-implementation-patterns`, this skill | Pattern selection routes away after DDD model, boundary, and invariant decisions are clear. |
| `### Negative Case: 단순 필드 rename`, `### Negative Case: 짧은 설명` | included | `SKILL.md` Routing | Simple CRUD, field rename, or tiny wording explanation stays direct without forced aggregates, context maps, or event storming. |
| `### Negative Case: false subagent claim` | included | `SKILL.md` Runtime Rules | Runtime forbids claiming tests, validation, review, browser checks, or subagent work not actually executed. |

## DDD Reference Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `architecture-ddd/final.md` `## 1. DDD란 무엇인가` | included | `SKILL.md`, `strategic-design.md` | DDD as domain-centered modeling and bounded-context solution reflected. |
| `### 1.1 DDD의 핵심 요약` | included | `SKILL.md` | Explicit bounded context and integration focus included. |
| `### 1.2 전략 설계 우선 원칙` | included | `SKILL.md`, `strategic-design.md` | Strategy-before-tactics rule included. |
| `### 1.3 주요 참고 자료의 관점 차이` | omitted | n/a | Source provenance comparison is not runtime behavior. |
| `## 2. 전략 패턴` | included | `strategic-design.md`, `context-map.md` | Strategic design concepts reflected. |
| `### 2.1 지식 탐구` | included | `strategic-design.md` | Iterative domain expert modeling reflected. |
| `### 2.2 도메인과 하위 도메인` | included | `strategic-design.md` | Core/supporting/generic and problem/solution split included. |
| `### 2.3 유비쿼터스 언어` | included | `strategic-design.md` | Context-scoped language included. |
| `### 2.4 바운디드 컨텍스트` | included | `strategic-design.md`, `context-map.md` | Bounded context design and ownership included. |
| `### 2.5 컨텍스트 맵` | included | `context-map.md` | Relationship patterns and direction included. |
| `### 2.6 증류` | included | `strategic-design.md` | Core domain distillation included. |
| `### 2.7 Event Storming` | included | `strategic-design.md` | Discovery technique included. |
| `### 2.8 전략 DDD와 팀 토폴로지` | included | `strategic-design.md` | Team ownership and topology mapping summarized. |
| `## 3. 전술 패턴` | included | `tactical-patterns.md`, `domain-events.md` | Tactical patterns included after strategy boundary. |
| `### 3.1 값 객체` | included | `tactical-patterns.md` | Immutability, self-validation, and equality by attributes included. |
| `### 3.2 엔티티` | included | `tactical-patterns.md` | Identity and aggregate membership included. |
| `### 3.3 애그리거트` | included | `tactical-patterns.md`, `domain-events.md` | Invariants, small aggregates, root access, ID references, eventual consistency included. |
| `### 3.4 리포지토리` | merged | `tactical-patterns.md`, `SKILL.md` Routing | Repository as aggregate persistence concept included; implementation details delegated. |
| `### 3.5 도메인 서비스` | included | `tactical-patterns.md` | Stateless domain rule and aggregate separation included. |
| `### 3.6 응용 서비스` | included | `tactical-patterns.md` | Use-case orchestration vs business rules included. |
| `### 3.7 도메인 이벤트` | included | `domain-events.md` | Domain event collection, timing, and outbox handoff included. |
| `### 3.8 Specification 패턴` | included | `tactical-patterns.md` | Reusable business predicates included. |
| `## 4. 유연한 설계` | included | `tactical-patterns.md` | Domain model quality principles included. |
| `### 4.1 의도를 드러내는 인터페이스` | included | `tactical-patterns.md` | Intention-revealing domain names included. |
| `### 4.2 부작용 없는 함수` | included | `tactical-patterns.md` | Side-effect-free value object behavior included. |
| `### 4.3 단언` | included | `tactical-patterns.md` | Invariants and postconditions included. |
| `### 4.4 개념적 윤곽` | included | `tactical-patterns.md` | Natural domain contours included. |
| `### 4.5 독립형 클래스` | merged | `tactical-patterns.md` | Low coupling and standalone concept guidance merged into supple design. |
| `### 4.6 연산의 닫힘` | merged | `tactical-patterns.md` | Value object operation closure reflected at concept level. |
| `## 5. 아키텍처` | delegated-to-other-skill | `architecture-implementation-patterns` | Architecture pattern choice is adjacent skill; DDD only routes/hands off. |
| `### 5.1 계층 아키텍처` | delegated-to-other-skill | `architecture-implementation-patterns` | Layering implementation belongs to pattern skill. |
| `### 5.2 DIP` | delegated-to-other-skill | `architecture-implementation-patterns` | Dependency direction belongs to pattern skill. |
| `### 5.3 핵사고날 아키텍처` | delegated-to-other-skill | `architecture-implementation-patterns` | Ports/adapters belong to pattern skill. |
| `### 5.4 CQRS` | delegated-to-other-skill | `architecture-implementation-patterns` | CQRS selection belongs to pattern skill. |
| `### 5.5 대규모 구조` | merged | `strategic-design.md` | Team/context ownership and evolving structure reflected; detailed patterns omitted as advanced structure. |
| `## 6. 구현 패턴` | delegated-to-other-skill | `architecture-implementation-patterns`, implementation skills | Implementation mechanics are outside DDD modeling. |
| `### 6.1 패키지 구조` | delegated-to-other-skill | `architecture-implementation-patterns` | Package structure belongs to pattern skill. |
| `### 6.2 SQLAlchemy Data Mapper 패턴` | delegated-to-other-skill | `architecture-implementation-patterns` | Data mapper implementation delegated. |
| `### 6.3 Repository + Unit of Work 패턴` | delegated-to-other-skill | `architecture-implementation-patterns` | UoW/repository implementation delegated; repository concept retained. |
| `### 6.4 Event Sourcing` | merged | `domain-events.md` | Event sourcing as domain modeling choice included; implementation delegated. |
| `### 6.5 Saga 패턴` | merged | `domain-events.md` | Saga as long-running consistency choice included; implementation delegated. |
| `### 6.6 단순한 비즈니스 로직 패턴` | included | `SKILL.md`, `strategic-design.md` | Simple CRUD/supporting domains should avoid over-applied DDD. |
| `### 6.7 마이크로서비스와 DDD` | merged | `context-map.md`, `domain-events.md` | Context boundary, integration events, and ACL reflected. |
| `## 7. 복잡성 관리 원칙` | included | `tactical-patterns.md`, `SKILL.md` | Invariants reduce freedom and complexity; aggregate/value-object guidance included. |
| `## 8. 의사결정 요약` | included | `SKILL.md`, references | Decisions reflected across strategic/tactical/event references. |
| `## 9. 핵심 요약` | included | references | Core pattern summaries represented in split references. |
| `## 출처 종합` | omitted | n/a | Bibliography is source provenance, not runtime behavior. |
| `### 서적` / `### 논문/시리즈` / `### 웹 자료` | omitted | n/a | Bibliography details are not runtime behavior. |

## Review Notes

- 2026-05-10 source review loop is closed with blocking 0, major 0, minor 0 after fixing Korean trigger coverage, risky/composite workflow routing, `spec.md` child-heading tracking, validation scenario heading coverage, Risky Write Consistency Block handoff coverage, metadata specificity, combined-work implementation wording, and stale completion claims from an earlier draft.
- 2026-05-10 rubric review loop is closed with blocking 0, major 0, minor 0. No source-backed runtime issue remained, and evaluation-only material was not copied into runtime docs.
- 2026-05-10 runtime checks covered positive DDD modeling, composite/risky workflow handoff, and simple negative naming prompts. `codex debug prompt-input` exposed the updated skill metadata, and read-only `codex exec` samples in `/private/tmp/ddd-smoke` produced the expected architecture behavior without file edits or false validation claims.
