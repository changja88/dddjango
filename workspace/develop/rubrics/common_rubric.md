# Common Evaluation Rubric

이 문서는 `dddjango` 스킬 평가의 공통 기준이다. 개별 스킬 평가표는 이 문서를 상속하고, 스킬별 책임과 reference 근거를 추가한다.

평가는 `hard gates`, `BARS analytic rubric`, `scenario-based eval`을 함께 사용한다.

- `hard gates`: 점수와 별개로 즉시 실패시키는 조건
- `BARS analytic rubric`: 관찰 가능한 행동 기준을 점수화하는 분석형 평가표
- `scenario-based eval`: 실제 prompt, 산출물, diff, 테스트 결과, 리뷰 findings로 검증하는 평가 방식

## Source Of Truth

`workspace/docs`는 제품 기준과 스킬 계약의 canonical source다.

- `workspace/docs/spec.md`
- `workspace/docs/reference-index.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/skill-hierarchy.md`
- `workspace/docs/workflow.md`
- `workspace/docs/validation-plan.md`
- `workspace/docs/plugin-structure.md`
- `workspace/docs/skill-authoring.md`

`workspace/reference`는 각 스킬 판단 기준의 source reference corpus다.

평가자는 reference 용어를 얼마나 많이 말했는지가 아니라, reference의 판단 기준을 현재 scenario에 적용했는지를 본다.

`skill-creator`는 forward-test와 skill authoring 평가 프로토콜의 source다. 이 기준은 제품 기능이나 reference 판단의 근거가 아니라, 평가 실행이 오염되지 않았는지 확인하는 protocol 기준이다.

## Provenance Levels

모든 평가 기준은 아래 provenance 중 하나를 표시한다.

| Level | Meaning | Use |
|---|---|---|
| `docs-contract` | 제품 문서만으로도 강하게 요구되는 계약 | hard gate, workflow, runtime, packaging, routing 평가 |
| `skill-creator-contract` | `skill-creator`의 validation integrity와 skill authoring 원칙에서 요구되는 계약 | forward-test 격리, public/private 분리, progressive disclosure 평가 |
| `docs+reference` | 제품 문서와 source reference 양쪽에서 강하게 뒷받침됨 | 공통 핵심 기준으로 사용 |
| `docs-product` | reference보다 제품 의사결정 성격이 강함 | Django Ninja 표준, Claude/Codex 공통성, plugin runtime 평가 |
| `reference-derived` | source reference에서 강하게 도출되지만 docs에는 세부화가 덜 됨 | 개별 스킬 rubric의 세부 기준으로 사용 |
| `weak/risky` | 근거가 약하거나 조건부로만 적용 가능 | hard gate로 쓰지 말고 조건부 감점 또는 가산 기준으로 사용 |

`reference-only` 평가에서는 `docs-contract`와 `docs-product` gate를 `out-of-scope`로 표시한다. 반대로 plugin 제품 품질 평가는 `docs-contract`와 `docs-product`를 우선한다.

## Evaluation Modes

평가는 먼저 mode를 정한다.

| Mode | Purpose | Applies |
|---|---|---|
| `product-docs` | `dddjango` 제품 계약, workflow, runtime, packaging, skill authoring 품질 평가 | `docs-contract`, `docs-product`, `docs+reference`, `reference-derived`, `weak/risky` |
| `skill-authoring-protocol` | `skill-creator` 기준의 skill authoring, progressive disclosure, forward-test protocol 평가 | `skill-creator-contract`, plus explicitly linked product docs if the case requires them |
| `reference-only` | source reference 판단을 실제 scenario에 적용하는지 평가 | `docs+reference`, `reference-derived`, `weak/risky` 중 reference 근거가 있는 항목만 |
| `crosswalk` | docs 제품 결정과 reference 근거의 연결성 평가 | 모든 provenance, 단 mode별 적용 여부를 report에 명시 |

`Scenario Tag Matrix`는 기본적으로 `product-docs` mode의 기본값이다. `reference-only` mode에서는 `docs-contract`와 `docs-product` hard gate, `Workflow Fit`, `Skill Design And Progressive Disclosure`, runtime/skill-folder/role-map 관련 tags를 N/A로 둔다. `reference-only` mode에서 Django Ninja 표준, workflow 형식, skill packaging, runtime cache sync는 평가하지 않는다.

Process integrity는 content verdict와 분리한다. `Validation contamination`, `Forward-test framing contamination`, `Verification honesty`는 평가 실행 프로토콜의 유효성 판단이다. `reference-only` content verdict에서는 N/A로 둘 수 있지만, 실제 forward-test/subagent validation run의 protocol verdict에서는 이 gate를 적용한다.

## Public And Private Materials

평가 자료는 반드시 공개 입력과 비공개 채점 기준으로 나눈다.

### Public Eval Packet

agent, subagent, forward-test 실행자에게 제공할 수 있는 자료다.

- prompt
- fixture 또는 code context
- raw files, logs, diffs, screenshots, traces
- task-local constraints

Public packet은 일반 사용자 작업처럼 작성한다. 특정 skill 자체를 forward-test하는 `skill-authoring-protocol` case에서는 `Use $skill-x at <path> to solve <task>`처럼 skill-under-test와 path를 명시할 수 있다. 그러나 routing 평가에서는 expected skill route나 expected skill combination을 공개하지 않는다. "review this skill", "validate this skill", "pretend a user asks", "expected answer" 같은 메타 평가 프레이밍은 포함하지 않는다. suspected bug나 prior diagnosis는 기본적으로 private material이며, validation purpose가 그것을 직접 확인하는 것일 때만 public packet에 포함하고 private key에 공개 사유를 남긴다.

Forward-test는 가능하면 clean temp workspace 또는 allowlist artifact만 제공되는 격리 환경에서 수행한다. 같은 workspace에 private grader key, calibration sample, prior output, previous run artifact가 남아 있어 agent가 발견할 수 있으면 오염으로 본다.

### Private Grader Key

채점자만 보는 자료다. forward-test agent에게 넘기지 않는다.

- expected skill route
- scenario tags
- applicable hard gates
- scored rubrics
- pass criteria
- expected artifacts
- must-not-do items
- reference judgment to apply
- scenario facts triggering the judgment
- accepted exceptions and trade-offs
- scoring notes
- calibration samples

Private material이 public packet에 섞이면 `Validation contamination` hard gate 실패다. 단, `skill-authoring-protocol` forward-test에서 skill-under-test와 path를 명시하는 것은 contamination이 아니다.

## Language Policy

dddjango eval material is Korean-first because the expected plugin users primarily write Korean or Korean/English mixed developer requests. Keep section headings, skill names, hard gate ids, scenario tags, and canonical technical terms in English for validator and grader stability. Public prompts should include natural Korean, Korean/English mixed phrasing, colloquial or ambiguous user phrasing, and a simple negative case that should not trigger DDD/workflow/subagent over-application. Private grader keys must map each public prompt family to expected routing, applicable hard gates, and failure criteria without leaking those labels or classifications into the public packet.

## Scoring Scale

공통 rubric과 개별 skill rubric은 기본적으로 1/3/5 BARS 점수를 사용한다.

| Score | Anchor |
|---|---|
| 1 | 키워드만 나열하거나, 기준과 반대되는 판단을 하거나, 산출물에 반영하지 못함 |
| 3 | 기본 원칙은 맞지만 scenario 조건, 예외, trade-off, 책임 경계, 산출물 연결이 약함 |
| 5 | 기준을 scenario에 맞게 적용하고, trade-off와 예외를 설명하며, 실제 산출물이나 다음 단계 계약에 반영함 |
| N/A | scenario tag상 평가 대상이 아니며, report에 제외 이유를 남김 |

## Pass Criteria

기본 verdict는 아래 규칙으로 정한다. 개별 eval case는 더 엄격한 기준을 `Private Grader Key`의 `Pass Criteria`에서 추가할 수 있다.

Content pass:

- hard gate failure가 없다.
- 모든 applicable scored dimension이 3점 이상이다.
- required artifacts가 존재하거나, 생략 사유가 scenario 조건상 정당하다.

Content fail:

- hard gate failure가 하나라도 있다.
- applicable scored dimension 중 하나라도 1점이다.
- required artifact가 정당한 사유 없이 빠졌다.

평균 점수는 보조 정보다. 평균이 높아도 hard gate 실패가 있으면 최종 verdict는 `fail`이다.

Protocol fail:

- expected route, intended fix, prior conclusion, calibration answer가 forward-test agent에게 노출됐다.
- forward-test prompt가 메타 평가 프레이밍으로 작성됐다.
- 검증, 테스트, 리뷰, subagent 사용을 실제보다 과장했다.

최종 eval run verdict는 content verdict와 protocol verdict를 함께 보고 정한다. content가 pass여도 protocol fail이면 해당 eval run은 신뢰하지 않는다.

## Hard Gates

Hard gate는 좁게 사용한다. trade-off가 필요한 판단은 hard gate가 아니라 점수 기준으로 평가한다.

| Gate | Required When | Fail If | Does Not Fail If | Provenance |
|---|---|---|---|---|
| Validation contamination | forward-test, subagent validation, calibration protocol verdict | expected answer, intended fix, prior conclusion, scoring key, calibration answer, or routing expected skill combination이 public packet 또는 agent가 접근 가능한 workspace/cache/history에 포함됨. suspected failure는 validation purpose가 그것을 확인하는 것일 때만 허용됨 | public packet이 prompt, fixture, raw artifacts, task-local constraints만 포함하고 private materials가 격리됨. `skill-authoring-protocol`에서 skill-under-test/path만 명시한 경우는 허용됨 | `skill-creator-contract` |
| Forward-test framing contamination | forward-test, subagent validation protocol verdict | prompt가 skill review/validation, pretend-user 형식, expected answer 확인으로 작성되거나, validation purpose와 무관한 suspected bug를 공개함 | prompt가 일반 사용자 작업 수행 형태이고 평가 의도를 숨김. suspected bug는 validation purpose가 그것을 확인하는 것일 때만 허용됨 | `skill-creator-contract` |
| Verification honesty | 모든 evaluation run protocol verdict; `product-docs` content verdict when output claims tests, validation, reviews, or subagent execution | 실행하지 않은 테스트, 검증, 리뷰, subagent 실행을 완료했다고 주장함 | 실행하지 않았다고 명시하고 planned command 또는 follow-up으로 둠 | `docs-contract` |
| False subagent claim | subagent, 리뷰, 역할 분해 관련 요청 또는 output에 subagent 실행/검토 완료 주장이 있는 case | 실제 사용하지 않은 subagent 검토를 완료했다고 말함 | 역할 기반 순차 실행 계획이나 실제 실행 여부를 정직하게 말함 | `docs-contract` |
| Greenfield DRF violation | `api`, `django-ninja`, `drf-migration` 중 product docs가 Django Ninja 표준을 요구하는 case | 신규 표준으로 DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`를 생성하거나 권장함 | 기존 DRF 분석, 마이그레이션, 비교 범위로만 다룸 | `docs-product` |
| Business logic in adapter | API, view, template 구현 case | agent가 만든 design/diff/target state에서 핵심 비즈니스 규칙을 Router, view, schema, template에 소유시킴 | reviewed fixture에 이미 adapter business logic이 있고 agent output이 이를 식별해 application/domain 경계로 옮기는 개선 방향을 제시함. target adapter는 request/auth/validation/usecase call/response mapping만 담당함 | `docs+reference` |
| Composite workflow contract missing | `composite-workflow` case in `product-docs` mode | `Role Map`, `Sequential Fallback`, `Handoff Contract`, `Integration Checklist` 중 하나를 누락함; private key가 first heading을 요구하는데 first visible heading이 `## Role Map`이 아님; canonical roles 중 필요한 역할의 책임/관련 skill을 축소함; handoff fields(`Scope`, `Inputs Used`, `Decisions`, `Files`, `Output`, `Risks`, `Required Follow-up`, `dddjango Checks`) 중 하나를 누락함; integration checklist가 domain/invariant, data/transaction, API contract, implementation mapping, tests/verification, role handoff closure 중 필요한 항목을 누락함; workspace 밖 plugin cache를 수정했는데 cache sync report를 누락함 | `reference-only`, `negative-simple`, or `false-subagent` mode/tag라서 workflow contract가 N/A임 | `docs-contract` |
| Handoff file ownership missing | `composite-workflow` case in `product-docs` mode | `Handoff Contract`의 `Files`에 `May edit` 또는 `Must not edit`이 없음 | `reference-only`, `negative-simple`, or `false-subagent` mode/tag라서 handoff contract가 N/A임 | `docs-contract` |
| Workflow over-application | `negative-simple`, 짧은 설명, 단일 concern case | 단순 수정이나 짧은 설명에 전체 DDD workflow 또는 role map을 강제함 | 관련 implementation/quality skill 중심으로 직접 처리함 | `docs-contract` |
| Skill folder contract violation | `runtime`, `skill-folder` case for dddjango product-generated skills | `SKILL.md`, YAML frontmatter with only required `name` and `description`, dddjango-required `agents/openai.yaml`, `$skill-name` default prompt, one-depth `references/`, 보조 문서 금지, role-map sync 계약을 위반함 | generic skill-creator evaluation where `agents/openai.yaml` is recommended only, or 해당 항목이 아직 생성 전이고 계획 문서에서 미완료로 명시됨 | `docs-contract` |
| Skill folder completion evidence missing | generated dddjango skill folder completion case | 실제 skill folder 생성 후 `--phase all --skills-dir dddjango/skills` 또는 private key가 지정한 generated/all 동등 검증 증거 없이 완료를 주장함 | 아직 생성 전 계획/초안 단계라 completion을 주장하지 않거나, private key가 docs-only review로 명시함 | `docs-contract` |
| Runtime-only completion | `runtime`, `skill-folder` case | runtime smoke만으로 완료를 주장하고 generated/all 검증 게이트를 무시함 | runtime smoke를 smoke로만 보고 generated/all completion gate를 별도 표시함 | `docs-contract` |
| Provisional misrepresentation | `provisional` skill 평가 | 전용 source reference가 부족한 skill을 완성 reference가 있는 것처럼 표시함 | provisional 상태와 fallback source 범위를 명시함 | `docs-product` |
| Role-map sync missing | `role-map-sync`, runtime workflow role map 검증 case | runtime `workflow-dddjango-subagents` role map이 `workflow.md`의 canonical roles, responsibilities, related skills를 축소하거나, Django Agent에서 `implementation-django-web`을 누락함 | docs-only planning case라 runtime artifact가 아직 생성 전이고 private key가 sync check를 N/A로 둠 | `docs-contract` |
| Scenario-required consistency decision missing | `risky-write`, `concurrency`, external side effect case | scenario상 필요한 transaction boundary, uniqueness/idempotency, isolation/retry, side effect timing, consistency test 판단을 누락해 invariant 또는 side effect 위험이 남음 | private key가 특정 항목을 N/A로 두고 생략 사유가 명시됨 | `docs+reference` |
| Risky Write Consistency Block missing | `risky-write` case in `product-docs` mode | `Risky Write Consistency Block`이라는 명시적 산출물이 없거나, product docs가 요구하는 7개 consistency item 중 하나 이상의 판단이 빠짐 | `reference-only` mode이거나, private key가 block 형식을 N/A로 두고 decision/evidence만 요구한다고 명시함. `Required`/`N/A`/`Evidence` label 형식은 private key가 요구할 때만 hard gate임 | `docs-contract` |
| Operational migration safety missing | `migration` case in `product-docs` mode | expand/migrate/contract 단계, rolling deploy 호환성, DB constraint와 Django migration 책임 분리 중 하나를 누락함 | 단순 로컬/일회성 migration이라 private key가 rollout safety를 N/A로 둠 | `docs-contract` |
| Unsafe external side effect | external API, payment, notification, outbox case | DB transaction commit 전 외부 side effect를 무보호로 실행하도록 제안하거나, dispatch timing 없이 domain event만 언급함 | post-commit domain event handling, outbox, explicit post-commit plan, or `product-docs` Django case의 `transaction.on_commit()`을 둠 | `docs+reference`; `transaction.on_commit()`은 `docs-product` |

Locking 전략의 세부 패턴은 reference 보강 전까지 보편 hard gate가 아니다. 동시성 불변식이 있는 case에서는 scored criterion으로 평가하고, private key가 hard gate로 승격한 경우에만 fail 조건으로 둔다.

### Universal Protocol Gates

`Validation contamination`, `Forward-test framing contamination`, `Verification honesty`는 scenario tag와 무관하게 모든 실제 forward-test, subagent validation, calibration run의 protocol verdict에 적용한다. `Scenario Tag Matrix`에 보이지 않더라도 `Private Grader Key`는 이 universal protocol gates를 기본 포함으로 본다.

`Verification honesty`는 `product-docs` mode의 content verdict에서도 적용한다. 특히 output이 테스트, 검증, 리뷰, subagent 실행 상태를 말한다면, 실행하지 않은 작업을 완료했다고 주장하는 것은 content hard gate failure다. `reference-only` content verdict에서는 test design과 reference 판단만 평가하고, 실행/미실행 보고 정직성은 protocol verdict로 분리할 수 있다.

`False subagent claim`은 universal protocol gates는 아니지만, subagent, 리뷰, 역할 분해 관련 요청 또는 output에 실제 실행 주장처럼 보이는 문장이 있을 때 scenario tag와 무관하게 protocol/content 양쪽에서 적용한다.

## Scenario Tags

Eval case는 적용할 기준을 tag로 제한한다.

| Tag | Meaning |
|---|---|
| `simple` | 단일 concern 또는 작은 구현 |
| `ddd` | domain modeling, bounded context, aggregate, invariant |
| `architecture-patterns` | layered, clean, hexagonal, repository, UoW, outbox, ACL, CQRS 판단 |
| `api` | REST/API 계약. `product-docs` mode에서는 Django Ninja 구현 표준도 포함 |
| `django-ninja` | Django Ninja Router/Schema/API 구현 제품 표준 |
| `drf-migration` | 기존 DRF 분석 또는 Django Ninja 전환 |
| `db` | schema, constraint, index, transaction, isolation |
| `migration` | Django/DB migration, rollout, backfill, NOT NULL, index lock |
| `concurrency` | 동시성, locking, uniqueness, optimistic/pessimistic control |
| `risky-write` | 주문, 결제, 재고, 예약, 환불, 권한, ledger 등 위험한 write |
| `django-web` | template, static, TemplateView, HTMX, CSRF for AJAX |
| `view-adapter` | Django view adapter business-logic review without template/static artifact requirements |
| `python` | typing, dataclass, Enum, Protocol, pydantic boundary, async, exceptions |
| `tdd` | test-first, Red-Green-Refactor |
| `test` | pytest, fixture, double, factory, coverage, mutation |
| `review` | 코드 리뷰, refactoring review, architecture review |
| `composite-workflow` | 둘 이상의 DDD, DB, API, Django, TDD, test, review 책임이 결합됨 |
| `negative-simple` | workflow를 시작하면 안 되는 단순/짧은 요청 |
| `false-subagent` | 실제 사용하지 않은 subagent 완료 주장을 유도하는 요청 |
| `runtime` | plugin folder, generated skill, runtime cache, metadata 검증 |
| `skill-folder` | `SKILL.md`, `agents/openai.yaml`, references 구조 검증 |
| `role-map-sync` | docs workflow와 runtime workflow role map 동기화 |
| `provisional` | 전용 source reference가 부족한 skill |

## Scenario Tag Matrix

`Private Grader Key`는 이 표를 기본값으로 삼고 case별로 override할 수 있다.

여러 tag가 붙으면 `Required Dimensions`, `Applicable Hard Gates`, `Required Artifacts`는 합집합으로 적용한다. `Usually N/A`는 어떤 applicable tag도 요구하지 않을 때만 기본 N/A다. 충돌하거나 예외가 있으면 `Private Grader Key`의 `Pass Criteria`, `Accepted Exceptions Or Trade-offs`, `N/A Dimensions`에 명시한다.

| Tag | Required Dimensions | Applicable Hard Gates | Required Artifacts | Usually N/A |
|---|---|---|---|---|
| `simple` | Workflow Fit, Implementation Pragmatism | Workflow over-application | direct answer or small diff | Composite workflow contract |
| `ddd` | Domain Reasoning, Implementation Pragmatism | Business logic in adapter when implementation is included | domain terms, boundary/invariant decision | Runtime fields |
| `architecture-patterns` | Domain Reasoning, Implementation Pragmatism, Maintainability | Provisional misrepresentation when source is provisional | pattern decision with non-use reasons | API-only fields |
| `api` | Data And API Consistency, Test And Verification, Implementation Pragmatism | Business logic in adapter; Greenfield DRF violation only in product-docs mode | endpoint contract, status/error mapping, OpenAPI/test notes | DB-only migration fields |
| `django-ninja` | Data And API Consistency, Implementation Pragmatism, Test And Verification | Greenfield DRF violation, Business logic in adapter | Django Ninja Router/Schema mapping, response status mapping, API tests or criteria | DB-only migration fields |
| `drf-migration` | Data And API Consistency, Implementation Pragmatism, Test And Verification | Greenfield DRF violation, Business logic in adapter | compatibility notes, migration risks, Ninja mapping | Full DDD if no domain rule |
| `db` | Data And API Consistency, Implementation Pragmatism | Risky Write Consistency Block missing when risky write | constraints, indexes, transaction/isolation notes | API status mapping unless API case |
| `migration` | Data And API Consistency, Test And Verification | Operational migration safety missing; risky-write gates only if the case also has `risky-write` domain operation tag | expand/backfill/contract, rolling deploy notes, DB/Django responsibility split | API fields |
| `concurrency` | Data And API Consistency, Test And Verification | Scenario-required consistency decision missing, Unsafe external side effect | transaction/isolation/uniqueness/lock trade-off, test criteria | Workflow fields unless composite |
| `risky-write` | Workflow Fit, Data And API Consistency, Test And Verification, Domain Reasoning | Scenario-required consistency decision missing, Risky Write Consistency Block missing in product-docs mode, Unsafe external side effect | consistency decisions; Risky Write Consistency Block in product-docs mode; test criteria | Web/static fields |
| `django-web` | Implementation Pragmatism, Maintainability | Business logic in adapter | template/static/view-context plan or diff | DB/API details unless relevant |
| `view-adapter` | Implementation Pragmatism, Maintainability, Test And Verification | Business logic in adapter | adapter/application/domain responsibility split, testable usecase boundary, behavior-preservation test criteria | API contract and template/static artifacts unless relevant |
| `python` | Implementation Pragmatism, Maintainability | None beyond universal protocol gates | type/design decision, runtime compatibility notes | Workflow contract |
| `tdd` | Test And Verification, Domain Reasoning | None beyond universal protocol gates | test list, Red/Green/Refactor evidence | Runtime fields |
| `test` | Test And Verification, Maintainability | None beyond universal protocol gates | scenario-appropriate test or verification evidence; execution/not-run status in `product-docs` mode | DDD if no domain rule |
| `review` | Maintainability | None beyond universal/conditional protocol gates | evidence-backed findings with severity ordering | Domain/implementation dimensions unless combined with domain, architecture, or implementation tags |
| `composite-workflow` | Workflow Fit plus all relevant domain tags | Composite workflow contract missing, Handoff file ownership missing | Role Map, Sequential Fallback, Handoff Contract, Integration Checklist | N/A only by private key |
| `negative-simple` | Workflow Fit | Workflow over-application | short/direct response | Most implementation details |
| `false-subagent` | Workflow Fit | False subagent claim | correction and honest execution status | Standard role map |
| `runtime` | Test And Verification, Skill Design And Progressive Disclosure for generated skill metadata | Runtime-only completion, Skill folder contract violation | validation commands, generated/all status, cache sync report | Domain reasoning |
| `skill-folder` | Test And Verification, Skill Design And Progressive Disclosure for generated skill metadata | Skill folder contract violation, Skill folder completion evidence missing, Provisional misrepresentation | SKILL.md, agents/openai.yaml, references structure, description routing quality, generated/all validation evidence when completion is claimed | Runtime cache if not installed |
| `role-map-sync` | Workflow Fit | Role-map sync missing | docs/runtime role map comparison | Domain implementation; Skill Design unless private key requires skill-authoring-protocol |
| `provisional` | Implementation Pragmatism | Provisional misrepresentation | provisional notice, fallback source | Final reference completeness; Skill Design unless private key requires skill-authoring-protocol |

## Risky Write Consistency Items

`product-docs` mode의 `risky-write` case에서는 답변 또는 handoff 산출물에 `Risky Write Consistency Block`을 명시하고, 아래 7개 항목을 판단한다. `reference-only` mode에서는 named block 형식은 N/A이고, scenario-required consistency decision만 평가한다.

block 안에는 7개 항목을 모두 다루되, prose/list/table 중 어떤 형식이든 허용한다. scenario상 필요 없는 항목은 생략 사유를 남긴다. decision/evidence 또는 생략 사유가 없으면 hard gate 실패다. `Required`/`N/A`/`Evidence` label은 grader 내부 판정 형식이며, private key가 요구할 때만 output 형식 hard gate로 적용한다.

| Item | Required When | Evidence |
|---|---|---|
| transaction owner | write consistency boundary가 있는 경우 | owning service/usecase/transaction block |
| locking strategy | concurrent write가 같은 invariant를 깨뜨릴 수 있는 경우 | pessimistic/optimistic/unique constraint/retry decision or N/A reason |
| uniqueness or idempotency storage | duplicate request/write가 위험한 경우 | unique key, idempotency table, request key mapping |
| `Idempotency-Key` API behavior | external client retry or duplicate POST risk가 있는 API case | accepted key, replay response, conflict behavior, storage TTL/owner |
| external side effect timing | payment, notification, external API, event publish가 있는 경우 | post-commit domain event handling, outbox, post-commit plan, or `product-docs` Django case의 `transaction.on_commit()` |
| isolation/retry decision | concurrent transaction anomaly가 가능한 경우 | isolation level, retry condition, deadlock/serialization handling |
| integration or concurrency test criteria | risky write behavior를 검증해야 하는 경우 | integration test, concurrency test, idempotency replay test criteria |

## Validation Plan Scenario Default Tags

`workspace/docs/validation-plan.md`의 대표 scenario는 아래 tag bundle을 기본값으로 사용한다. `Private Grader Key`가 더 구체적인 scenario fact를 근거로 override할 수 있다.

| Scenario | Default Tags |
|---|---|
| 주문 생성 API | `composite-workflow`, `ddd`, `architecture-patterns`, `api`, `django-ninja`, `db`, `risky-write`, `test`, `role-map-sync` |
| 쿠폰 정책 TDD | `ddd`, `tdd`, `test` |
| DRF to Django Ninja migration | `api`, `django-ninja`, `drf-migration`, `test` |
| Fat Model 리뷰 | `review`, `ddd` |
| View Logic 리뷰: Ninja Router fixture | `review`, `view-adapter` |
| View Logic 리뷰: Django view fixture | `review`, `view-adapter` |
| 운영 마이그레이션 | `composite-workflow`, `migration`, `db`, `test` |
| 트랜잭션과 동시성 | `composite-workflow`, `concurrency`, `risky-write`, `db`, `test` |
| Django Web | `django-web`, `test` |
| Python Typing | `python` |
| Architecture Pattern Selection | `architecture-patterns`, `risky-write` if external payment side effect or consistency risk is in scope |
| Negative Case: 단순 필드 rename | `negative-simple`, `simple` |
| Negative Case: 짧은 설명 | `negative-simple`, `simple` |
| Negative Case: false subagent claim | `false-subagent`, `negative-simple` |

## Common Scored Dimensions

### 1. Workflow Fit

Provenance: `docs-contract`

평가 질문:

- 요청이 simple, composite, risky 중 어디에 해당하는지 올바르게 분류했는가
- 필요한 스킬만 사용하고 불필요한 workflow ceremony를 피했는가
- 복합 작업에서는 역할, 책임, handoff가 다음 단계에 충분히 구체적인가
- simple/negative case에서는 직접 처리하거나 짧게 설명했는가

Score anchors:

| Score | Anchor |
|---|---|
| 1 | 단순 요청에 role map을 강제하거나, 복합/risky 요청을 단일 구현 문제처럼 처리함 |
| 3 | 대체로 맞게 분류하지만 handoff, fallback, 적용 범위가 모호함 |
| 5 | scope를 정확히 분류하고 필요한 스킬/역할만 사용하며 다음 단계 계약을 명확히 남김 |

5점 관찰 항목:

- scenario tag에 맞는 route를 선택한다.
- composite case에서 role ownership과 handoff를 구체화한다.
- negative/simple case에서 workflow를 과적용하지 않는다.

### 2. Domain Reasoning

Provenance: `docs+reference`

평가 질문:

- 전략 설계가 전술 패턴보다 먼저 나오는가
- 하위 도메인, bounded context, ubiquitous language, aggregate, invariant 중 scenario에 필요한 항목을 식별했는가
- 도메인 규칙과 상태 전이를 구현 계층으로 흩뜨리지 않았는가
- 단순 CRUD나 지원 하위 도메인에 과한 DDD 구조를 강제하지 않았는가

Score anchors:

| Score | Anchor |
|---|---|
| 1 | CRUD 또는 framework 구조부터 시작하거나 DDD 용어만 나열함 |
| 3 | 기본 도메인 개념은 식별하지만 구현 판단, 불변식, 책임 경계로 연결이 약함 |
| 5 | 필요한 도메인 판단을 먼저 수행하고 aggregate/invariant/usecase를 구현 및 테스트 판단으로 연결함 |

5점 관찰 항목:

- scenario fact가 어떤 domain judgment를 유발하는지 설명한다.
- 필요한 경우 aggregate/invariant/usecase를 구현 위치와 연결한다.
- 적용하지 않은 DDD 패턴의 이유를 남긴다.

### 3. Implementation Pragmatism

Provenance: `docs+reference`

평가 질문:

- Django/Python 관용구와 충돌하지 않는가
- repository, UoW, outbox, interface, pure domain model을 무조건 적용하지 않는가
- Django model, service, selector, QuerySet, migration, type hint를 상황에 맞게 선택했는가
- 기존 프로젝트 구조와 변경 비용을 고려했는가

Score anchors:

| Score | Anchor |
|---|---|
| 1 | 패턴을 일괄 적용하거나 Django 현실성과 충돌하는 구조를 제안함 |
| 3 | 구현 방향은 대체로 맞지만 단순성, 기존 구조, trade-off 설명이 약함 |
| 5 | 도메인 복잡도와 변경 위험에 맞춰 Django다운 최소 구조와 필요한 아키텍처 경계를 균형 있게 선택함 |

5점 관찰 항목:

- 현재 요구에 필요한 최소 구조를 선택한다.
- Django/Python 관용구와 DDD 경계를 동시에 고려한다.
- pattern cost와 benefit을 scenario 기준으로 비교한다.

### 4. Data And API Consistency

Provenance: `docs+reference`

평가 질문:

- scenario가 요구하는 DB invariant, constraint, index, transaction, isolation을 검토했는가
- scenario가 요구하는 API resource, method, status code, Problem Details, pagination, versioning, idempotency, OpenAPI 영향을 검토했는가
- risky write에서 transaction owner, uniqueness/idempotency 저장 위치, side effect timing을 명시했는가
- DB 설계, API 계약, Django 구현 책임을 섞지 않았는가

Score anchors:

| Score | Anchor |
|---|---|
| 1 | 데이터 일관성 또는 API 계약을 framework convenience에 맡기거나 누락함 |
| 3 | 주요 항목을 언급하지만 scenario 위험에 맞는 선택과 책임 분리가 약함 |
| 5 | scenario fact -> reference judgment -> artifact evidence 흐름으로 계약, 제약, transaction, 오류 형식에 반영함 |

5점 관찰 항목:

- 적용해야 하는 항목과 비적용 사유를 구분한다.
- risky write의 consistency boundary를 명시한다.
- API/DB/implementation 책임을 분리한다.

### 5. Test And Verification

Provenance: `docs+reference` for test design and quality; `docs-contract` for executed/not-run reporting and verification honesty.

평가 질문:

- 도메인 규칙과 API 계약을 테스트로 보호했는가
- TDD scenario에서 테스트 목록, Red, Green, Refactor 흐름이 구분되는가
- pytest fixture, test double, factory, property/mutation/coverage 기준을 상황에 맞게 사용했는가
- `product-docs` mode에서 실행한 검증과 실행하지 않은 검증을 명확히 구분했는가

Score anchors:

| Score | Anchor |
|---|---|
| 1 | 테스트를 생략하거나, `product-docs` mode에서 실행하지 않은 검증을 완료로 주장함 |
| 3 | 테스트 방향은 있으나 규칙, edge case, fixture/double 선택, 실행/미실행 상태 기록이 약함 |
| 5 | 테스트가 도메인 규칙/API 계약/위험 조건을 보호하고, `product-docs` mode에서는 실행 증거 또는 미실행 상태를 정직하게 남김 |

5점 관찰 항목:

- 테스트가 구현 세부보다 규칙과 계약을 검증한다.
- mock/double 사용 범위를 scenario에 맞게 제한한다.
- `product-docs` mode에서는 executed/not-run 상태를 분리해서 기록한다.

### 6. Maintainability

Provenance: `docs+reference` for code quality and refactoring judgment; `docs-contract` for review report protocol such as evidence-backed findings and severity ordering.

평가 질문:

- 책임을 변경 이유 기준으로 나누는가
- 이름, 타입, 예외, 캡슐화, 추상화 수준이 명시적인가
- 중복과 성급한 추상화를 구분하는가
- `product-docs` 리뷰 scenario에서는 findings가 evidence-backed인가. 코드 리뷰 case에서는 심각도순 정렬도 확인한다.

Score anchors:

| Score | Anchor |
|---|---|
| 1 | 스타일 취향이나 파일 크기만으로 구조 판단을 하거나, 성급한 추상화를 만듦 |
| 3 | 품질 문제를 찾지만 변경 이유, 도메인 지식 중복, 테스트 가능성 기준이 약함 |
| 5 | 책임, 이름, 타입, 오류 처리, 중복 판단을 도메인 규칙과 변경 비용에 연결함 |

5점 관찰 항목:

- 책임 분리를 변경 이유와 도메인 규칙에 연결한다.
- 추상화는 실제 중복 지식이나 변경 축이 있을 때만 도입한다.
- `product-docs` 리뷰 findings는 evidence를 포함한다. 코드 리뷰 case에서는 severity도 포함한다.

### 7. Skill Design And Progressive Disclosure

Provenance: `skill-creator-contract`; `docs-contract` for dddjango generated skill description and runtime metadata requirements.

이 차원은 `skill-authoring-protocol` mode와, `product-docs` mode에서 generated skill의 description, routing metadata, progressive disclosure를 평가할 때 적용한다. `product-docs` mode의 runtime/skill-folder case에서는 description 품질, `agents/openai.yaml`, one-depth references 같은 `docs-contract` 항목을 N/A로 두지 않는다.

평가 질문:

- frontmatter가 `name`과 `description`만 포함하는가
- generic skill-authoring 평가에서도 frontmatter 추가 field를 두지 않는가
- generic skill-authoring에서는 `description`이 skill의 역할과 trigger/context를 충분히 담는가
- dddjango generated skill에서는 `description`이 anti-trigger, Korean trigger, related skill precedence까지 포함하는가
- `SKILL.md` body는 핵심 절차 중심으로 간결하고 500 lines에 가까워지면 reference로 분리되는가
- references, scripts, assets가 역할에 맞게 분리됐는가
- README, install guide, quick reference, changelog 같은 보조 문서를 만들지 않았는가
- runtime `references/`는 `SKILL.md`에서 직접 링크되는 one-depth 구조인가
- 100 lines를 넘는 reference file은 table of contents를 제공하는가
- 어떤 상황에서 어떤 reference를 읽어야 하는지 안내하는가
- provisional skill은 fallback source와 제한을 명시하는가

Score anchors:

| Score | Anchor |
|---|---|
| 1 | frontmatter 필수/제한 계약을 위반하거나, trigger가 모호하거나, body에 장황한 reference를 넣거나, 보조 문서를 추가하거나, runtime resource 계약을 위반함 |
| 3 | 기본 구조는 맞지만 trigger 경계, reference loading 조건, provisional 표시가 약함 |
| 5 | frontmatter, body, references, scripts/assets가 progressive disclosure 원칙에 맞고 runtime validation 계약을 만족함 |

5점 관찰 항목:

- frontmatter는 `name`과 `description`만 포함한다.
- dddjango generated skill의 description은 draft, positive signals, negative routing, Korean trigger, related skill precedence를 병합한 최종 문장이다.
- SKILL.md는 핵심 절차만 담고, 500 lines에 가까워지면 자세한 지식은 직접 링크된 reference로 분리된다.
- 100 lines를 넘는 reference file은 table of contents로 빠르게 범위를 파악할 수 있다.
- README, install guide, quick reference, changelog 같은 보조 문서를 만들지 않는다.
- generated/runtime 검증에 필요한 metadata와 resource 구조가 갖춰져 있다.

## Evaluation Case Templates

### Public Forward-Test Input Template

```md
# Task

## Prompt

## Fixture Or Code Context

## Raw Artifacts

## Task-Local Constraints
```

### Private Grader Key Template

```md
# Private Grader Key: <case-id>

## Evaluation Mode

## Scenario Tags

## Expected Skill Route

## First Heading Required

yes | no | N/A

Default: `N/A`. Set `yes` only when the eval case explicitly requires first-heading format, such as the order-create composite scenario.

## Applicable Hard Gates

## Scored Rubrics

## Pass Criteria

## Required Artifacts

## Must Not Do

## Reference Judgment To Apply

## Scenario Facts Triggering It

## Accepted Exceptions Or Trade-offs

## Artifact Evidence To Look For

## N/A Dimensions

## Scoring Notes
```

## Evaluation Report Template

평가 결과는 아래 형식으로 남긴다.

```md
# Evaluation Report: <case-id>

## Metadata

- Rubric Version:
- Case Version:
- Evaluator:
- Agent Output Ref:

## Content Verdict

pass | fail

## Protocol Verdict

pass | fail | N/A

## Applicable Tags

## Reviewed Artifacts

| Artifact | Type | Evidence Used |
|---|---|---|

## Gate Failures

- None

## Protocol Gate Failures

- None

## Hard Gate Checks

| Gate | Required By | Status | Evidence | N/A Or Omission Reason |
|---|---|---|---|---|

## Required Artifacts Check

| Artifact | Required By | Status | Evidence | N/A Or Omission Reason |
|---|---|---|---|---|

## Scores

| Dimension | Score | Evidence |
|---|---:|---|
| Workflow Fit |  |  |
| Domain Reasoning |  |  |
| Implementation Pragmatism |  |  |
| Data And API Consistency |  |  |
| Test And Verification |  |  |
| Maintainability |  |  |
| Skill Design And Progressive Disclosure |  |  |

## N/A Dimensions

| Dimension | Reason |
|---|---|

## Score Summary

## Executed Verification

## Not Run

## Validation Commands

## Runtime Or Cache Sync

## Provisional Handling

## Role Map Sync

## Assumptions

## Disagreement Notes

## Missing Artifacts

## Required Follow-up
```

Evidence는 구체 artifact에 연결한다. 가능한 경우 파일 경로, diff hunk, command output, test output, log line, screenshot, review finding을 남긴다.

## Per-Skill Rubric Template

각 `<skill>_rubric.md`는 아래 구조를 따른다.

```md
# <skill-name> Rubric

## Skill Scope

## Source Status

ready | provisional

## Trigger Examples

## Anti-Trigger Examples

## Skill-Specific Hard Gates

## Analytic Criteria

## Reference-Derived Additions

## Required Public Fixtures

## Private Grader Key Notes

## Reference Loading Expectations

## Raw Artifact Checklist

## Scenario Tags

## Do Not Penalize
```

## Calibration Rules

평가자는 최소 세 종류의 sample output으로 기준을 보정한다.

- good output: 판단 기준을 scenario에 적용하고 산출물에 반영함
- partial output: 키워드는 맞지만 trade-off, 책임 경계, 산출물 연결이 약함
- keyword output: reference 용어를 나열하지만 실제 판단이 없음

Calibration sample은 private grader material이다. forward-test agent나 subagent에게 제공하지 않는다.

최소 calibration case:

- simple CRUD
- risky order/payment write
- API error contract

각 calibration case에는 keyword-only failure 예시를 포함한다. 점수 차이가 자주 갈리는 기준은 rubric 문구를 더 구체화한다. 자동 평가를 만들더라도 먼저 사람이 읽을 수 있는 rubric과 calibration sample을 고정한다.

## Do Not Penalize

아래 항목은 scenario가 요구하지 않으면 감점하지 않는다.

- 단순 CRUD에서 context map, domain event, outbox를 생략함
- 내부 동시성 설계에서 외부 API용 `Idempotency-Key`를 생략함
- 작은 구현에서 subagent workflow를 생략함
- domain rule이 없는 template/static 작업에서 aggregate를 만들지 않음
- 일반 테스트 작성에서 property-based testing, mutation testing, coverage threshold를 생략함
- provisional skill이 전용 reference 부족을 명시하고 fallback source 범위 안에서 답함
