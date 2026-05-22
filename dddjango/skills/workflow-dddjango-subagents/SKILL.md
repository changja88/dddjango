---
name: workflow-dddjango-subagents
description: >
  Use for role-decomposed dddjango workflows in composite or risky Django/DDD work spanning domain rules, DB, API, implementation, tests, or review; also use when the user asks for subagent/subagents, delegation, parallel agent work, role decomposition, role map, responsibility split, parallel review, sequential fallback, handoff, dddjango workflow, 서브에이전트, 역할 분해, 역할 맵, 병렬 검토, 책임 분배, 순차 실행, 핸드오프, 통합 체크리스트, 검증 분담, or 위험 작업. Use for 주문/결제/재고/예약/환불/권한/ledger work when state transition, transaction, schema, API, or test impact is coupled. Selecting this workflow does not authorize real subagent execution; without explicit request or approval, use sequential fallback. Do not use for simple single-file changes, small field renames, pure answer-only/tiny direct answers, decorative role-map-only requests, 서브에이전트 계획 필요 없음, or when the user opts out of subagent planning.
---

# dddjango Workflow

Composite 또는 risky Django/DDD 작업을 Domain, Architecture, DB, API, Django, Test, Review 책임으로 나누고 Coordinator가 통합할 때 사용한다. 이 skill이 선택됐다는 사실만으로 실제 subagent 실행이 승인된 것은 아니다. 실제 subagent는 사용자가 명시적으로 요청하거나 승인했고, bounded sidecar 작업으로 나눌 수 있을 때만 실행한다. 그렇지 않으면 같은 role order를 sequential fallback으로 적용한다.

## Routing

- 사용자가 subagent/subagents, delegation, parallel agent work, role decomposition, role map, responsibility split, parallel review, sequential fallback, handoff, dddjango workflow, 서브에이전트, 역할 분해, 역할 맵, 병렬 검토, 책임 분배, 순차 실행, 핸드오프를 요청하면 이 skill을 먼저 고려한다.
- DDD, implementation patterns, DB schema/transactions, REST API contract, Django/Python implementation, tests/TDD, review 중 둘 이상이 실제로 결합된 composite Django/DDD work에 사용한다.
- 주문, 결제, 재고, 예약, 환불, 권한, ledger 같은 risky domain에서 state transition, transaction, schema, API, test 영향이 함께 있으면 사용한다.
- 작은 단일 파일 변경, 작은 field rename, invariant나 rollout risk 없는 local CRUD, 짧은 설명, 이미 결정된 단순 구현에는 강제하지 않는다.
- 단순 작업을 장식적으로 Role Map 형식에 넣어 달라는 요청이면 실제 multi-role 책임이 있는지 먼저 판단한다.
- 사용자가 `subagent 계획은 필요 없어`처럼 opt out하면 full role map을 출력하지 말고 가장 관련 있는 implementation 또는 architecture skill로 진행한다.
- 실행하지 않은 subagent work, review, validation을 완료했다고 말하라는 요청은 거절하고 실제 실행 상태만 보고한다.
- Direct Answer Mode: short explanation, tiny edit, explicit opt-out, pure answer-only 요청에서는 사용자가 요구한 출력 형태를 보존한다. workflow section, subagent status, validation footer, command-honesty boilerplate, command/check note, skill/reference loading report를 덧붙이지 않는다.

## Reference Loading

- 현재 workflow에 필요한 reference만 읽는다.
- 실제 subagent, sequential fallback, direct answer 판단은 [delegation-rules.md](references/delegation-rules.md)를 읽는다.
- canonical roles, responsibilities, related skills는 [role-map.md](references/role-map.md)를 읽는다. 이 role map을 축소하지 않는다.
- role handoff와 file ownership은 [handoff-contract.md](references/handoff-contract.md)를 읽는다.
- integration priority, risky write consistency, validation honesty, Cache sync report는 [integration-checklist.md](references/integration-checklist.md)를 읽는다.

## Canonical Roles

Use [role-map.md](references/role-map.md) for exact role responsibilities and related skills; do not shrink that role map in workflow output. Runtime-visible role routing summary:

- Coordinator: `workflow-dddjango-subagents`
- Domain Agent: `architecture-ddd`
- Architecture Agent: `architecture-implementation-patterns`
- DB Agent: `architecture-db`, `implementation-django`
- API Agent: `architecture-api`, `implementation-django-ninja`
- Django Agent: `implementation-django`, `implementation-django-web`, `implementation-python`; includes template/static/web and templates/static files ownership when in scope.
- Test Agent: `implementation-tdd`, `implementation-test`
- Review Agent: `implementation-cleancode`

Domain Agent 결정은 DB, API, Django, Test 결정에 선행한다. Architecture Agent가 advisory여도 composite/risky workflow에서는 역할을 유지하고, Coordinator 또는 명시된 Integration owner가 결과를 통합한다. DB Agent는 schema, constraint, locking, isolation, transaction policy를 소유하고, Django Agent는 결정된 DB/API/pattern boundary 안에서 ORM, migration file, service transaction implementation을 소유한다. Source/reference governance, metadata, leakage, eval traceability, validation coverage, broader provenance/cache audit가 주된 작업이면 `source-reference-audit`로 넘기고, 이 workflow는 coordination 중 발견한 follow-up과 workflow-local parity evidence만 기록한다.

## Output Shape

Composite 또는 risky implementation/planning workflow 답변은 첫 visible heading을 `## Role Map`으로 두고, 이어서 `## Sequential Fallback`, `## Handoff Contract`, `## Integration Checklist`를 포함한다. section 내용은 줄일 수 있지만 section 자체는 제거하지 않는다.

When using sequential fallback, explicitly state that real subagents were not executed and that the workflow is being handled as sequential fallback. `## Sequential Fallback` section은 정확히 이 한 문장으로 시작한다: `Real subagents were not executed; this is sequential fallback in the role order below.` 그 다음 Domain, Architecture, DB, API, Django, TDD/Test, Review, Integration 순서를 적는다. 이 규칙은 workflow-section output에만 적용하고 Direct Answer Mode, pure answer-only, explicit opt-out에는 붙이지 않는다.

Review-focused workflow는 findings를 먼저 제시하고, 필요한 경우 그 뒤에 `## Role Map`, `## Sequential Fallback`, `## Handoff Contract`, `## Integration Checklist`를 둔다.

Subagent 실행 승인 전에도 proposed workflow contract를 제공한다. Composite/risky work에서는 Architecture Agent를 advisory로라도 유지하고 Coordinator 또는 explicit Integration owner를 지정한다. 실행 상태는 proposed, pending approval, not executed처럼 표시한다.

`Handoff Contract`에는 `Scope`, `Inputs Used`, `Decisions`, `Files` with `May edit` and `Must not edit`, `Output`, `Risks`, `Required Follow-up`, `dddjango Checks`를 모두 포함한다.

Risky write가 있으면 `## Integration Checklist` 안에 visible `Risky Write Consistency Block` section 또는 table을 포함한다. transaction owner, locking strategy, uniqueness or idempotency storage, `Idempotency-Key` API behavior, external side-effect timing, isolation/retry decision, integration or concurrency test criteria를 생략하지 말고, 현재 role에서 결정할 수 없으면 owning role에 배정한다.

Actual subagents를 사용했다면 role, task, result, result collection method를 적는다. Result collection requires `wait_agent` or `close_agent`; pending 또는 in-progress subagent를 completed result로 보고하지 않는다. Before writing the final answer, confirm every spawned subagent has a completed result collection event. If result collection is unavailable or times out, report that as blocked and do not integrate or summarize missing subagent results. Do not write `wait_agent`, `close_agent`, or result summaries in the final answer unless those calls actually completed.

Subagent를 쓰지 않았으면 sequential fallback 또는 planned only였다고 말한다. Plugin cache outside workspace를 수정했다면 Cache sync report에 cache path, workspace canonical source, validation status를 적는다. `workflow-dddjango-subagents` role-map 변경 시 `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`와 runtime/cache를 비교해 role responsibilities와 related skills가 축소되지 않았는지 확인한다.

Runtime wrong-routing audit에서는 skill description metadata만으로 충분하다고 보지 말고, role-map reference와 canonical workflow table도 함께 비교한다.

## Runtime Rules

- 먼저 작업을 simple, DDD-focused, composite, risky, review-focused 중 어디에 둘지 결정한다.
- Domain decisions가 DB, API, Django, Test decisions를 안내한다.
- Real subagents는 concrete, bounded, parallelizable sidecar task에만 사용한다. Immediate critical-path blocker는 메인 에이전트가 직접 처리하는 것이 기본이다.
- Critical path, sidecar task, advisory review, shared write task를 구분한다. Shared write는 단일 write owner를 지정하고 다른 role은 read-only/advisory로 둔다.
- Subagent 승인 전에는 실행하지 않고도 role scope, handoff boundary, integration ownership을 제안할 수 있다. Approval은 execution을 막는 것이지 planning detail을 막는 것이 아니다.
- Parallel `May edit` scope는 concrete file path 또는 module owner 기준으로 disjoint해야 한다.
- Sequential fallback의 role order는 Domain, Architecture, DB, API, Django, TDD/Test, Review, Integration 순서를 보존한다.
- Risky writes에는 `Risky Write Consistency Block` 결정을 포함하거나 responsible role에 배정한다.
- Final integration은 각 role의 risks와 required follow-up을 닫거나 unresolved로 명시한다.
- Runtime-facing guidance에서는 source authoring path를 allowed reference처럼 제시하지 않는다. Runtime references는 skill-local bundled reference로 안내한다.
- Source/reference governance, metadata, leakage, validation coverage, broader provenance/cache audit는 `source-reference-audit`로 넘긴다. Workflow 중 validation-pack, scoring, report, or run-variance 문제가 발견되면 이 skill에서 직접 고치지 말고 owning follow-up으로 분류하며 project planning constraints를 따른다.
- Plugin cache outside workspace를 수정했다면 Cache sync report에 workspace canonical source mapping을 적는다. `workflow-dddjango-subagents`에서는 role-map parity, runtime skill/reference paths, validation run 또는 not-run status를 포함한다. Broader provenance/cache audit는 `source-reference-audit` 책임이다.
- 실행한 tests, validation, review, browser checks, subagent work, eval, Serena만 실행했다고 보고한다. 실행하지 않았으면 not run이라고 말한다.
- Direct implementation work의 final report는 concrete changed files와 필요한 verification만 간결히 보고하고, 작업이 composite/risky로 바뀌지 않는 한 workflow sections를 추가하지 않는다.
