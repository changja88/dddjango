# Source Coverage Crosswalk: workflow-dddjango-subagents

## Status

- Skill: `workflow-dddjango-subagents`
- Runtime target: `dddjango/skills/workflow-dddjango-subagents/`
- Source status: ready
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `delegation-rules.md`, `role-map.md`, `handoff-contract.md`, `integration-checklist.md`
- Rubric status: completed after source review; source-backed runtime issue only

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

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/workflow-dddjango-subagents/` | Plugin-bundled structure used; role-map sync honored. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name and workflow responsibility preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for `workflow-dddjango-subagents` used. |
| `## 8. 금지 사항` | included | file tree, `SKILL.md` | No auxiliary docs; no false validation or subagent claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` | Trigger/routing and boundaries are in description/body. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | Workflow signals and anti-routes included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Workflow is first for composite/risky/subagent work. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align. |
| `reference-index.md` `## Architecture` / `## Implementation` | merged | `role-map.md` | All domain, DB, API, implementation, test, and review skills represented through roles. |
| `## Reference 사용 원칙` | included | `SKILL.md`, references | Runtime references summarize workflow source and avoid workspace source paths. |
| `## Reference Gap` | omitted | n/a | This skill has ready workflow source. |
| `## DRF Guardrail` | included | `integration-checklist.md` | Composite workflow checks no greenfield DRF implementation in API path. |
| `## Reference에서 도출한 제품 결정` | included | `integration-checklist.md` | Django Ninja, DDD, DB, API, and validation product decisions integrated. |

## Contracts, Workflow, And Standard Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | included | `role-map.md`, `integration-checklist.md` | Domain Agent and domain-first integration included. |
| `## architecture-implementation-patterns` | included | `role-map.md` | Architecture Agent included with pattern/dependency responsibility. |
| `## architecture-db` | included | `role-map.md`, `integration-checklist.md` | DB Agent and data/transaction checks included. |
| `## architecture-api` | included | `role-map.md`, `integration-checklist.md` | API Agent and API contract checks included. |
| `## implementation-django` / `## implementation-django-ninja` / `## implementation-django-web` | included | `role-map.md`, `integration-checklist.md` | Django, API implementation, and web/static responsibilities included. |
| `## implementation-python` / `## implementation-cleancode` | included | `role-map.md`, `integration-checklist.md` | Python support and Review Agent included. |
| `## implementation-tdd` / `## implementation-test` | included | `role-map.md`, `integration-checklist.md` | TDD/Test Agent included. |
| `## workflow-dddjango-subagents` | included | `SKILL.md`, references | Role decomposition, real subagent/sequential fallback, and integration included. |
| `## 공통 필수 출력` / `### Risky Write Consistency Block` | included | `integration-checklist.md`, `SKILL.md` | Risky write decisions included and assigned to roles. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md`, `role-map.md` | Workflow precedence and downstream skill roles included. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | included | `delegation-rules.md`, `integration-checklist.md` | Domain-first order reflected. |
| `## 2. 하위 도메인별 구현 강도` / `## 3. 바운디드 컨텍스트와 언어` | delegated-to-other-skill | `architecture-ddd` via `role-map.md` | Domain Agent owns details; workflow ensures order. |
| `## 4. 애그리거트와 불변식` | included | `integration-checklist.md` | Domain invariants are top integration priority. |
| `## 5. Domain Events` / `## 6. Application Service와 Domain Service` | merged | `integration-checklist.md`, `role-map.md` | Domain events and service ownership assigned to Domain/Architecture/Django roles. |
| `## 7. Django ORM 매핑` / `## 8. Repository와 Transaction` | included | `role-map.md`, `integration-checklist.md` | Django/DB/Architecture responsibilities included. |
| `## 9. API 매핑` | included | `role-map.md`, `integration-checklist.md` | API Agent and API contract checks included. |
| `## 10. Python 매핑` / `## 11. 테스트 매핑` | included | `role-map.md` | Django/Python and Test Agent responsibilities included. |
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md`, `integration-checklist.md` | Real validation only and source-backed checks included. |
| `## 2. 대표 시나리오` | included | `delegation-rules.md`, `integration-checklist.md` | Composite/risky, simple negative, and false-subagent cases covered. |
| `## 3. 평가 항목` | included | `SKILL.md`, references | Over-application, workflow contract, role map sync, and validation honesty covered. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder was checked with the final validator. |

## Validation Scenario Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `validation-plan.md` `### 주문 생성 API` | included | `SKILL.md`, `role-map.md`, `handoff-contract.md`, `integration-checklist.md` | Composite order API work requires role map, sequential fallback, handoff, integration checklist, Risky Write Consistency Block, and no false test/subagent claim. |
| `### 쿠폰 정책 TDD` | delegated-to-other-skill | `implementation-tdd`, `implementation-test`, optionally `architecture-ddd` through `role-map.md` | Coupon policy may stay with TDD/domain roles unless multiple role areas are genuinely coupled. |
| `### DRF to Django Ninja 전환` | included | `role-map.md`, `integration-checklist.md` | API and Django implementation roles cover Django Ninja conversion, compatibility, Problem Details, OpenAPI, and no greenfield DRF implementation. |
| `### Fat Model 리뷰`, `### View Logic 리뷰` | included | `SKILL.md`, `delegation-rules.md`, `role-map.md`, `handoff-contract.md` | Review-focused or cross-role responsibility analysis leads with severity-ordered findings, then assigns Review, Domain, Architecture, Django, and API follow-up ownership when workflow coordination is needed. |
| `### 운영 마이그레이션` | included | `role-map.md`, `integration-checklist.md` | DB and Django roles split rollout constraints, backfill/index-lock risk, and concrete migration ownership. |
| `### 트랜잭션과 동시성` | included | `integration-checklist.md` | Risky write consistency decisions include transaction owner, locking, idempotency, side effects, isolation/retry, and concurrency tests. |
| `### Django Web` | included | `role-map.md` | Django Agent includes `implementation-django-web` and template/static/web responsibility when web work is in scope. |
| `### Python Typing` | delegated-to-other-skill | `implementation-python` through `role-map.md` | Pure typing refactors can stay direct; composite work assigns Python support to Django Agent. |
| `### Architecture Pattern Selection` | included | `role-map.md`, `integration-checklist.md` | Architecture Agent owns pattern/dependency decisions and integration resolves conflicts by priority. |
| `### Negative Case: 단순 필드 rename`, `### Negative Case: 짧은 설명` | included | `SKILL.md`, `delegation-rules.md` | Simple direct work and short explanations are explicit anti-routes for full workflow ceremony. |
| `### Negative Case: false subagent claim` | included | `SKILL.md`, `delegation-rules.md`, `integration-checklist.md` | Runtime rules require refusing false subagent/review/test claims and reporting actual execution status. |

## Workflow Source Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `workflow.md` `## 1. 기본 흐름` | included | `delegation-rules.md`, `integration-checklist.md` | Domain-first-to-verification sequence included. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md`, `delegation-rules.md` | Simple, DDD, composite, risky, and review routing included; review-focused work keeps findings first, with workflow sections after findings when needed. |
| `## 3. 역할 분해` | included | `SKILL.md`, `role-map.md` | Canonical roles, responsibilities, and related skills copied without reduction. |
| `## 4. Sequential Fallback` | included | `delegation-rules.md`, `SKILL.md` | Fallback order included. |
| `## 5. Handoff Contract` | included | `handoff-contract.md` | Required fields and `May edit`/`Must not edit` included. |
| `## 6. 통합 우선순위` | included | `integration-checklist.md` | Conflict priority order included. |
| `## 7. Integration Checklist` | included | `integration-checklist.md` | Checklist items and cache sync report included. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references directly linked and workspace source paths avoided in runtime docs. |
| `## 9. 검증 방식` | included | `SKILL.md`, `integration-checklist.md` | Only actual validation may be claimed. |

## Review Notes

- 2026-05-10 source self-review in the current evaluation loop found source-backed gaps in stale review/rubric completion claims, `### Source Coverage Crosswalk` heading precision, Korean trigger coverage for 역할 맵/핸드오프/통합 체크리스트/검증 분담/위험 작업, `spec.md` child-heading coverage, validation scenario heading coverage, and `agents/openai.yaml` handoff/integration wording. Runtime files and this crosswalk were updated.
- Independent source review found major 1 and minor 1: review-focused workflow output could conflict with findings-first review ordering, and the `SKILL.md` role table lacked the canonical responsibility column. `SKILL.md`, `delegation-rules.md`, and this crosswalk were updated. Independent source re-review returned blocking 0, major 0, minor 0.
- Rubric review was performed only after source review. A source-backed runtime issue was found: the workflow output rule should pin the required `Handoff Contract` fields so composite/risky outputs do not omit ownership and follow-up fields. `SKILL.md` was updated. Independent rubric review returned blocking 0, major 0, minor 0, and no runtime leakage concern.
- Runtime positive smoke then exposed one remaining source-backed issue: risky order creation output included the consistency decisions but did not visibly title them as `Risky Write Consistency Block`. `SKILL.md` was updated to require a visible section or table for risky writes.
- Runtime checks completed: `codex debug prompt-input` exposed updated workflow metadata for positive, review-boundary, false-claim, and simple negative prompts. Isolated read-only `codex exec` samples in `/private/tmp/workflow-smoke` covered composite order workflow, review findings-first workflow, false subagent claim correction, and simple memo-field negative behavior. The positive re-run produced `## Role Map`, `## Sequential Fallback`, `## Handoff Contract`, `## Integration Checklist`, all required Handoff fields, and a visible `### Risky Write Consistency Block`; it also reported actual subagent use and did not claim unrun tests.
- Final findings: source self-review blocking 0, major 0, minor 0; independent source re-review blocking 0, major 0, minor 0; rubric review blocking 0, major 0, minor 0.
