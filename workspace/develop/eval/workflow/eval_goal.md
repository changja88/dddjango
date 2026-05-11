# Workflow Eval Goal

## Goal

`workflow` 평가는 복합 Django/DDD 작업에서 `dddjango`가 역할 분해, handoff, sequential fallback, integration checklist, risky write consistency, 실제 subagent 사용 여부 보고를 안정적으로 수행하는지 평가한다.

핵심 목표는 필요한 경우에는 전문 역할을 빠짐없이 조합하고, 필요하지 않은 경우에는 workflow를 과적용하지 않는 균형을 reference와 runtime role map 기준으로 확인하는 것이다.

## Reference Basis

평가 case는 다음 source를 함께 반영해야 한다.

- `workspace/docs/workflow.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/validation-plan.md`
- `workspace/docs/ddd-implementation-standard.md`
- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/references/{delegation-rules,role-map,handoff-contract,integration-checklist}.md`
- 관련 role의 runtime `SKILL.md` and references for DDD, implementation patterns, DB, API, Django, Ninja, Web, TDD/Test, Clean Code, Python

## Case Families

- Positive composite workflow: 주문/결제/재고/예약/환불/권한/ledger처럼 DDD, DB, API, Django, Test가 얽힌 위험 작업에서 `Role Map`, `Sequential Fallback`, `Handoff Contract`, `Integration Checklist`가 유지되는가.
- Review-focused workflow: 리뷰 작업에서는 findings가 먼저 나오고, 필요한 경우 workflow sections가 뒤에 붙는 예외를 지키는가.
- Handoff contract: `Scope`, `Inputs Used`, `Decisions`, `Files` with `May edit` and `Must not edit`, `Output`, `Risks`, `Required Follow-up`, `dddjango Checks`가 구체적인가.
- Risky Write Consistency Block: transaction owner, locking, uniqueness/idempotency storage, `Idempotency-Key`, external side effect timing, isolation/retry, integration/concurrency test criteria가 빠지지 않는가.
- Role-map sync: Domain Agent 판단이 DB/API/Django/Test 기준으로 이어지고, Django Agent에 template/static/web 책임이 있을 때 `implementation-django-web`이 포함되는가.
- Delegation honesty: 실제 subagent를 사용하지 않았는데 사용했다고 말하지 않고, sequential fallback이면 그렇게 보고하는가.
- Negative workflow restraint: 단순 단일 파일 수정, 작은 rename, 짧은 설명, user opt-out에서 전체 역할 분해를 출력하지 않는가.
- Direct answer shape: 설계-only 또는 answer-only 요청에서 사용자가 요구한 bullet/sentence 개수와 종료 지점을 보존하고 command/check/tool footer를 붙이지 않는가.
- Critical-path delegation restraint: subagent를 허용하더라도 즉시 필요한 핵심 판단은 main agent가 먼저 내리고, sidecar 검토만 병렬 위임하는가.
- Parallel ownership: 병렬 역할 분해에서 `May edit`/`Must not edit`가 겹치지 않고 integration owner가 명확한가.
- Integration closure: 각 role의 risk와 required follow-up이 최종 통합 판단에서 닫히거나 명시적으로 남는가.

## Minimum Coverage

완성된 workflow eval pack은 positive composite, review-focused, sequential fallback, actual-subagent trace, subagent opt-out, false-execution claim, tiny-task restraint, risky write consistency, cache sync report case를 각각 덮어야 한다. workflow를 response bucket의 일부 smoke case로만 완료 처리하지 않는다.

Workflow checks는 다음을 명시적으로 평가한다.

- Architecture Agent coverage: pattern choice, dependency direction, ports/adapters, repository/UoW, outbox, ACL, CQRS가 필요한 경우 Architecture Agent 책임으로 연결되는가.
- Sequential fallback order: Domain, Architecture, DB, API, Django, TDD/Test, Review, Integration 순서가 유지되는가.
- Full handoff fields: `Scope`, `Inputs Used`, `Decisions`, `Files` with `May edit`/`Must not edit`, `Output`, `Risks`, `Required Follow-up`, `dddjango Checks`.
- Risk closure: 각 role의 risks와 required follow-up이 통합 판단에서 닫히거나 다음 action으로 carry-forward 되는가.
- Direct answer and meta-tail restraint: pure answer-only/design-only 요청에서 사용자가 요구한 형식 뒤에 실행 명령, 미실행 체크, tool/Serena 보고를 추가하지 않는가.
- Critical-path delegation boundary: 즉시 필요한 blocking decision을 위임해 대기하지 않고, 병렬화 가능한 sidecar 검토만 구체적으로 나누는가.
- Parallel file ownership: 병렬 역할의 `May edit` 범위가 겹치지 않고, 겹칠 수 있는 파일은 단일 owner나 read-only review로 제한되는가.

## Answer Oracle

각 workflow case는 `answer/case-*.yaml`에 evaluator-only oracle을 둔다.

`answer`는 최소한 다음을 담는다.

- workflow type: positive, review-focused, negative, false-claim, opt-out
- required sections and allowed section ordering
- required role decisions and handoff fields
- risky write consistency requirements when applicable
- required delegation honesty statement
- forbidden over-ceremony or false subagent claim
- source refs for each expected workflow rule

## Evidence To Capture

- workflow response transcript
- role map and handoff artifact
- sequential fallback or actual subagent execution trace
- integration checklist
- risky write consistency block
- review findings and resolution notes
- answer oracle evaluation notes

## Non-Goals

- 실제로 실행하지 않은 subagent나 review를 완료했다고 주장하지 않는다.
- 역할 이름만 나열하고 concrete decisions, risks, follow-up 없이 통과 처리하지 않는다.
- 단순 작업에 workflow contract를 강제해 사용성을 떨어뜨리지 않는다.

## Completion Gate

Workflow eval은 `workspace/develop/eval/workflow/cases/plugin/public/`에 하나 이상의 `case-*.md`가 있고, 같은 id의 `answer/case-*.yaml`이 존재할 때만 완료 후보가 된다.

현재 runner에 workflow 전용 run path가 없으면 workflow case를 response eval runner로 실행할 수 있게 mirror하거나 runner를 확장해야 한다. mirror 방식을 쓰더라도 canonical case와 `answer` oracle, fixture, raw transcript, parsed section score, analysis result는 `workspace/develop/eval/workflow/` 아래에 남아야 한다. mirrored response artifacts는 workflow case id와 `answer` file로 되돌아가는 machine-checkable mapping을 가져야 한다. 어떤 방식을 쓰든 selected workflow case count가 0이면 통과가 아니다.

완료 판정은 runtime `workflow-dddjango-subagents` skill과 `workspace/docs/workflow.md`의 canonical role map이 같은 책임을 유지하고, response/run artifact가 answer oracle의 workflow 질문을 실제로 덮으며, positive/review/negative/false-claim/opt-out case가 모두 평가될 때만 가능하다.
