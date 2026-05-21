# Delegation Rules

실제 subagent 실행, sequential fallback, direct answer 중 무엇을 선택할지 판단할 때 읽는다.

## When To Role-Decompose

다음 경우에는 role decomposition을 사용한다.

- DDD, DB, API, Django, tests, TDD, review 중 둘 이상이 실제로 결합되어 있다.
- 사용자가 subagent/subagents, delegation, parallel agent work, role decomposition, role map, responsibility split, parallel review, handoff, sequential fallback, dddjango workflow, 서브에이전트, 역할 분해, 역할 맵, 병렬 검토, 책임 분배, 순차 실행, 핸드오프를 명시적으로 요청했다.
- order, payment, inventory, reservation, refund, permission, ledger 같은 risky domain noun이 state transition, transaction, schema, API contract, tests와 함께 등장한다.

## When To Stay Direct

다음 경우에는 workflow를 강제하지 않는다.

- small single-file edit
- simple model field rename
- invariant 또는 rollout risk가 없는 local CRUD change
- short conceptual explanation
- 실제 multi-role 책임이 없는 장식적 workflow 또는 Role Map 요청
- 사용자가 subagent plan이 필요 없다고 명시한 작업

Pure answer-only 요청에는 사용자가 요구한 내용만 답한다. 문장 수, bullet 수 같은 고정 형식이 있으면 모든 단위가 질문에 답해야 하며 마지막 요청 단위에서 멈춘다. 사용자가 묻지 않은 meta note를 앞뒤에 붙이지 않는다. 예: tests not run, commands not run, no subagents used, skill/reference loading, `Commands run`, `commands run`, `Checks not run`, `checks not run`, `실행한 명령`, `명령 실행`, `체크`, `체크: 미실행`, `검증 미실행`, `Serena`.

Direct implementation work에서는 changed files와 verification은 정직하게 보고하되 compact하게 유지한다. 작업이 composite 또는 risky로 바뀌지 않는 한 workflow sections를 추가하지 않는다.

## Critical Path And Sidecar Work

Coordinator는 delegation 전에 다음을 구분한다.

| 구분 | 기준 | 처리 |
|---|---|---|
| Critical path | 다음 local action이 이 결과 없이는 진행 불가 | 메인 에이전트가 직접 수행하는 것이 기본 |
| Sidecar task | 메인 작업과 병렬로 진행 가능하고 나중 통합에 도움 | real subagent 후보 |
| Advisory review | 파일 수정 없이 위험, 누락, 설계 판단을 독립 검토 | subagent 또는 sequential fallback review 후보 |
| Shared write task | 같은 파일을 여러 role이 수정해야 함 | 단일 write owner 지정, 나머지는 read-only/advisory |

Urgent blocking work를 subagent에게 넘긴 뒤 기다리기만 하지 않는다. Subagent는 critical path를 멈추지 않는 bounded sidecar work에 가장 적합하다.

## Real Subagents

Real subagents는 실제로 사용 가능하고, 사용자가 subagent/delegation/parallel work를 명시적으로 요청하거나 승인했으며, task가 concrete independent work로 나뉠 때만 사용한다. 각 subagent에는 다음을 준다.

- role
- scope
- inputs
- owned files 또는 responsibility
- expected output
- constraints on what not to edit
- validation expectations

승인이 아직 없으면 spawn하지 않고 completed review를 주장하지 않는다. 대신 concrete role split과 proposed handoff를 먼저 제시한다. Composite 또는 risky work에서는 Architecture Agent를 advisory로라도 포함하고 Coordinator 또는 explicit Integration owner를 지정한다.

Subagent review, implementation, validation은 실제로 실행됐을 때만 완료로 보고한다.
After spawning real subagents, collect each result with `wait_agent` or `close_agent` before integrating it or reporting it as complete. Spawned 또는 pending subagent는 completed review가 아니다.
Before writing the final answer, confirm every spawned subagent has a completed result collection event. If result collection is unavailable or times out, report blocked or partial execution and do not integrate missing subagent results. Do not write `wait_agent`, `close_agent`, or result summaries unless those calls actually completed.

## Sequential Fallback

Subagent가 없거나 승인되지 않았거나 병렬화에 맞지 않으면 role order를 유지한 채 순차로 수행한다.

1. Domain
2. Architecture
3. DB
4. API
5. Django
6. TDD/Test
7. Review
8. Integration

Sequential fallback은 subagent가 실행됐다는 주장이 아니다.
When using sequential fallback, explicitly state that real subagents were not executed and that the workflow is being handled as sequential fallback.
Workflow-section output에서 `## Sequential Fallback`은 다음 문장으로 시작한다: `Real subagents were not executed; this is sequential fallback in the role order below.`
Direct single-skill answer, pure answer-only request, explicit opt-out response에는 이 문장을 추가하지 않는다.

## Review-Focused Work

Review request는 severity 순 findings를 evidence와 함께 먼저 제시한다. Review가 여러 role area에 걸치면 findings 이후 role map, handoff, integration check로 coordination과 follow-up ownership을 보여준다.
