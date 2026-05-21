# workflow-dddjango-subagents source reference

이 문서는 `workflow-dddjango-subagents` skill의 전용 source reference다. 목적은 composite 또는 risky Django/DDD 작업에서 역할 분해, 실제 subagent 실행 경계, sequential fallback, handoff, ownership, integration, runtime sync를 판단하는 기준을 고정하는 것이다.

---

## 1. 적용 목적

`workflow-dddjango-subagents`는 구현 skill이 아니라 coordination skill이다. 단일 역할로 안전하게 끝낼 수 없는 Django/DDD 작업에서 Domain, Architecture, DB, API, Django, Test, Review 관점을 분해하고, Coordinator가 결과를 통합하도록 돕는다.

이 skill은 다음을 보장해야 한다.

- composite work를 단순 구현처럼 축소하지 않는다.
- risky write의 domain invariant, data consistency, transaction, API, test 영향을 같은 흐름에서 다룬다.
- 실제 subagent를 실행했는지, sequential fallback인지, planned only인지 정직하게 구분한다.
- handoff contract와 file ownership을 먼저 정해 병렬 작업 충돌을 줄인다.
- integration 단계에서 각 role의 risk와 required follow-up을 닫거나 명시적으로 남긴다.

---

## 2. Routing 기준

### 2.1 workflow를 사용해야 하는 경우

다음 중 하나에 해당하면 workflow를 우선 고려한다.

| 조건 | 판단 기준 |
|---|---|
| 사용자 명시 요청 | subagent, subagents, 서브에이전트, role decomposition, 역할 분해, role map, 역할 맵, parallel review, 병렬 검토, handoff, sequential fallback, dddjango workflow 요청 |
| composite Django/DDD work | DDD, implementation pattern, DB schema/transaction, API contract, Django/Python implementation, test/TDD, review 중 둘 이상이 실제로 결합 |
| risky domain work | 주문, 결제, 재고, 예약, 환불, 권한, ledger 같은 도메인에서 상태 전이, transaction, schema, API, test 영향이 함께 존재 |
| review-focused composite work | 단일 코드 스타일 지적이 아니라 domain, DB, API, test, runtime honesty 위험을 함께 검토해야 하는 review |

### 2.2 workflow를 강제하지 말아야 하는 경우

다음 작업은 가장 관련 있는 단일 skill이나 직접 답변이 우선이다.

- 작은 단일 파일 수정
- 단순 field rename
- invariant, rollout, transaction risk가 없는 local CRUD 변경
- 짧은 개념 설명
- 사용자가 “subagent 계획은 필요 없어”처럼 workflow를 명시적으로 거부한 경우
- 여러 역할이 실제 책임을 갖지 않는 장식적 Role Map 요청
- 사용자가 순수 answer-only 형식, 문장 수, bullet 수 같은 고정 출력 형태를 요구한 경우

단순 작업이더라도 실제 검증, 변경 파일, 실행하지 않은 명령은 정직하게 보고한다. 다만 workflow section을 붙여 사용자의 요청 형태를 깨지 않는다.

---

## 3. Canonical Role Map

Composite 또는 risky workflow에서 canonical role map은 축소하지 않는다. 역할이 advisory 또는 read-only일 수는 있지만, role 자체와 관련 skill 목록을 임의로 줄이지 않는다.

| Role | Responsibility | Related skills |
|---|---|---|
| Coordinator | 작업 범위, role assignment, result integration | `workflow-dddjango-subagents` |
| Domain Agent | subdomain, bounded context, ubiquitous language, aggregate, invariant, domain event | `architecture-ddd` |
| Architecture Agent | implementation pattern, dependency direction, port/adapter, transaction boundary | `architecture-implementation-patterns` |
| DB Agent | schema, constraints, indexes, transactions, rollout constraints, backfill/index-lock risk | `architecture-db`, `implementation-django` |
| API Agent | REST contract, status code, Problem Details, OpenAPI | `architecture-api`, `implementation-django-ninja` |
| Django Agent | ORM, service, selector, concrete migration files, transaction, settings/security/performance, template/static/web, static files | `implementation-django`, `implementation-django-web`, `implementation-python` |
| Test Agent | TDD flow, pytest, fixtures, test doubles, API/integration tests, ownership of `tests/**` files | `implementation-tdd`, `implementation-test` |
| Review Agent | code quality, design risk, missing verification, regressions | `implementation-cleancode` |

Domain Agent의 invariant와 language 결정은 DB, API, Django, Test 결정을 선행한다. Architecture Agent는 구현 구조와 dependency direction을 정리하고, Coordinator는 충돌을 통합한다.

---

## 4. 실제 subagent 실행 승인 경계

이 workflow skill이 trigger됐다는 사실만으로 실제 subagent 실행이 승인된 것은 아니다. 실제 subagent는 다음 조건을 모두 만족할 때만 사용한다.

- 사용자가 subagent, delegation, parallel agent work를 명시적으로 요청하거나 실행을 명확히 승인했다.
- subtask가 concrete, bounded, self-contained하다.
- subtask가 material하게 main task를 전진시킨다.
- immediate critical path blocker를 subagent에게 넘겨 기다리는 구조가 아니다.
- 병렬 write scope가 concrete file path 또는 module owner 기준으로 분리된다.
- 각 subagent의 result를 `wait_agent` 또는 `close_agent`로 수집할 수 있다.

승인이 없으면 real subagent를 실행하지 않는다. 그러나 composite/risky work라면 proposed role scopes, handoff boundaries, integration owner는 제안할 수 있다. 실행 상태는 `proposed`, `pending approval`, `not executed`, `sequential fallback`처럼 정확히 표시한다.

실행하지 않은 subagent review, validation, implementation을 완료했다고 쓰는 것은 금지한다.

---

## 5. Critical Path와 Sidecar Delegation

Coordinator는 먼저 전체 task를 빠르게 나누고 즉시 직접 처리해야 할 critical path를 정한다.

| 구분 | 기준 | 처리 |
|---|---|---|
| Critical path | 다음 local action이 이 결과 없이는 진행 불가 | 메인 에이전트가 직접 수행하는 것이 기본 |
| Sidecar task | 메인 작업과 병렬로 진행 가능하고 결과가 나중 통합에 도움 | subagent 위임 후보 |
| Advisory review | 파일 수정 없이 독립 위험, 누락, 설계 판단 검토 | subagent 또는 sequential fallback review 후보 |
| Shared write task | 같은 파일을 여러 role이 수정해야 함 | 단일 write owner 지정, 나머지는 read-only/advisory |

Subagent에게 urgent blocking work를 위임하고 기다리기만 하는 방식은 피한다. 병렬화의 목적은 critical path를 멈추지 않고 검토, verification, bounded patch를 진행하는 것이다.

---

## 6. Sequential Fallback

Subagent가 없거나 승인되지 않았거나 task가 병렬화에 맞지 않으면 sequential fallback으로 진행한다. Sequential fallback은 subagent 실행 주장이 아니라 같은 role order를 메인 에이전트가 순차로 적용하는 방식이다.

표준 순서는 다음과 같다.

1. Domain
2. Architecture
3. DB
4. API
5. Django
6. TDD/Test
7. Review
8. Integration

Workflow section을 출력하는 경우 `## Sequential Fallback`은 실제 subagent가 실행되지 않았다는 짧은 실행 상태 문장으로 시작해야 한다. Direct answer mode, 순수 answer-only 요청, explicit opt-out 응답에는 이 문장을 덧붙이지 않는다.

---

## 7. Handoff Contract

역할을 나누거나 subagent를 승인 요청할 때도 handoff contract를 먼저 채운다. 승인 전에는 `pending approval`, `not executed`, `read-only`, `unknown until code inspection` 같은 값을 사용할 수 있지만 field를 생략하지 않는다.

필수 field:

- `Scope`
- `Inputs Used`
- `Decisions`
- `Files`
- `Output`
- `Risks`
- `Required Follow-up`
- `dddjango Checks`

`Files`에는 반드시 다음을 포함한다.

- `May edit`
- `Must not edit`

Parallel `May edit` scope는 concrete file path 또는 module owner 기준으로 disjoint해야 한다. 두 role이 같은 파일을 수정해야 하면 한 role만 write owner가 되고 다른 role은 read-only review 또는 advisory로 제한한다.

---

## 8. Integration Checklist

Coordinator 또는 명시된 integration owner는 role 결과를 모은 뒤 아래 순서로 충돌을 해결한다.

1. Domain invariants
2. Data consistency
3. Transactions and security
4. API contract and backward compatibility
5. Testability
6. Django/Python idioms
7. Names and style

최종 통합에서는 다음을 확인한다.

- domain invariant와 state transition이 DB/API/implementation/test와 충돌하지 않는다.
- DB constraints, transaction boundary, locking, idempotency, rollout risk가 처리되거나 owning role에 배정됐다.
- API contract, status code, Problem Details, OpenAPI 영향이 구현과 맞는다.
- Router, view, schema, template가 핵심 domain policy를 소유하지 않는다.
- test나 explicit not-run verification note가 role별 risk에 연결된다.
- 각 role의 `Risks`와 `Required Follow-up`이 closed 또는 unresolved로 명시된다.
- 실제 실행하지 않은 validation, browser check, subagent review, eval을 실행했다고 쓰지 않는다.

---

## 9. Risky Write Consistency Block

주문, 결제, 재고, 예약, 환불, 권한, ledger처럼 risky write가 있는 workflow output에는 다음 항목을 visible block 또는 table로 포함한다.

| 항목 | 확인 기준 |
|---|---|
| transaction owner | 어떤 application service, use case, command handler, DB layer가 transaction boundary를 소유하는지 |
| locking strategy | pessimistic lock, optimistic concurrency, constraint 기반 방어, 또는 lock 불필요 판단 |
| uniqueness/idempotency storage | idempotency key, unique constraint, processed event table, ledger uniqueness 등 저장 위치 |
| `Idempotency-Key` API behavior | key 필수 여부, replay response, conflict response, TTL/retention, status code |
| external side-effect timing | `transaction.on_commit()`, outbox, domain/integration event, retry boundary |
| isolation/retry decision | isolation level, retry 가능 오류, duplicate prevention, lost update 방어 |
| test criteria | integration/concurrency/idempotency test 또는 명시적 not-run reason |

현재 role에서 결정할 수 없는 항목은 생략하지 않고 owning role에 배정한다.

---

## 10. Output Shape와 실행 정직성

Composite 또는 risky implementation/planning workflow answer는 첫 visible heading을 `## Role Map`으로 두고, 이어서 `## Sequential Fallback`, `## Handoff Contract`, `## Integration Checklist`를 포함한다. 내용은 줄일 수 있지만 section 자체는 제거하지 않는다.

Review-focused workflow는 findings를 먼저 제시하고, 필요하면 그 뒤에 workflow sections를 둔다.

Actual subagent를 사용한 경우 report에는 role, task, result, result collection method를 적는다. `wait_agent` 또는 `close_agent`로 결과를 수집하지 못한 subagent는 completed result로 통합하지 않는다.

Direct Answer Mode에서는 사용자 출력 형태가 우선이다. 짧은 설명, tiny edit, explicit opt-out, pure answer-only 요청에는 workflow boilerplate, subagent status, command honesty footer, skill/reference loading report를 덧붙이지 않는다.

---

## 11. Runtime Bundle과 Reference 분리

Runtime skill은 source authoring path를 runtime-facing allowed reference처럼 제시하지 않는다. `SKILL.md`에서는 skill-local bundled references인 `references/*.md`만 load 대상으로 안내한다.

Bundled references의 역할:

- `delegation-rules.md`: real subagent, sequential fallback, direct answer 판단
- `role-map.md`: canonical role과 related skill 목록
- `handoff-contract.md`: 역할별 handoff field와 ownership discipline
- `integration-checklist.md`: 통합 우선순위, risky write consistency, validation honesty, cache sync report

Source reference의 역할:

- 위 runtime instruction이 어떤 source decision을 반영하는지 판단하는 기준
- P1 분석, source gap, runtime sync, validation coverage 평가의 evidence

---

## 12. Runtime Cache Sync

Source skill과 runtime cache는 실제 diff 또는 cmp evidence로 확인해야 한다. Cache path 자체는 parity evidence로만 보고하며 runtime-facing guidance의 allowed reference로 제시하지 않는다.

Cache 밖 workspace source를 수정한 뒤 runtime cache가 다르면 다음을 수행한다.

1. `수정 대상: runtime-sync` 분석을 `workspace/plan/skill_lv_up_plan/workflow-dddjango-subagents/analysis/`에 작성한다.
2. 같은 timestamp 파일명으로 sync 계획을 `plan/`에 작성한다.
3. workspace canonical source에서 runtime cache로 동기화한다.
4. `SKILL.md`, `references/*.md`, `agents/openai.yaml`의 diff가 없는지 확인한다.
5. 최종 보고에 cache path, workspace canonical source, validation status를 적는다.

`role-map.md`가 바뀐 경우 runtime cache의 role names, responsibility scope, related skills가 source skill의 `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`보다 축소되지 않았는지 명시적으로 비교한다.

---

## 13. Eval 문제 분류

P1 중 eval case, answer oracle, evaluator, report 문제가 발견되면 이 source/skill P1 안에서 직접 수정하지 않는다. 다음 위치에 후속 분석 대상으로 분류한다.

- `workspace/plan/eval_lv_up_plan/<bucket>/analysis/`

분석 첫 줄은 해당 문제 성격에 따라 `수정 대상: case`, `수정 대상: answer`, `수정 대상: evaluator`, `수정 대상: report`, `수정 대상: model-variance` 중 하나를 사용한다. Eval run artifact는 source decision이나 runtime reference를 대체하지 않는다.

---

## 14. P1 Completion Gate

`workflow-dddjango-subagents` P1은 다음 증거가 모두 있을 때 완료 후보가 된다.

- 이 dedicated source reference가 존재하고 P1 판단 축을 모두 다룬다.
- `SKILL.md`가 source decision을 runtime rule로 반영한다.
- bundled references가 source decision을 skill-local runtime guidance로 나누어 담고, source authoring path를 runtime allowed reference처럼 노출하지 않는다.
- `agents/openai.yaml`이 skill 목적, trigger, negative routing과 충돌하지 않는다.
- source skill과 runtime cache의 sync 여부가 실제 diff 또는 cmp로 확인됐다.
- analysis/plan 문서가 constraint에 맞고, plan이 있으면 같은 파일명의 analysis가 있다.
- 필요한 validators가 통과했다.
- review 결과가 `Blocker 0, Major 0, 열린 Minor 0`이다.
- 실행하지 않은 subagent, validator, eval, Serena 사용을 실행했다고 기록하지 않았다.
