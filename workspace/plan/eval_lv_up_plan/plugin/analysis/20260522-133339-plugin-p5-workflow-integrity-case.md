수정 대상: case
원인 분류: case

# P5 plugin-level workflow integrity case 분석

## 문제

현재 `workflow` bucket은 `workflow-dddjango-subagents` 개별 skill의 P4 성격 검증을 넓게 갖고 있다. 반면 `plugin`, `runtime`, `source` bucket은 cache/source, metadata, leakage, provenance를 각각 검증하지만, 설치된 plugin 노출과 workflow subagent 정직성 규칙을 하나의 P5 plugin-level 시나리오로 묶어 검증하는 case가 없다.

그 결과 다음 규칙이 plugin 평가에서 end-to-end로 닫히지 않는다.

- 실제 subagent는 명시 승인과 bounded sidecar 조건에서만 실행한다.
- pending 또는 in-progress subagent를 completed result로 주장하지 않는다.
- `wait_agent` 또는 `close_agent`로 결과를 수집한 경우에만 통합한다.
- 병렬 작업은 disjoint ownership과 handoff contract를 가진다.
- 실행하지 않은 validator, eval, browser, Serena, subagent review를 실행했다고 쓰지 않는다.
- cache/source와 runtime metadata evidence 없이 plugin-level 완료를 주장하지 않는다.

## 영향

P4 workflow skill 평가가 pass여도 P5 plugin-level 평가가 같은 workflow 정직성을 보장한다고 말하기 어렵다. 특히 plugin bucket에서 subagent trace/result collection evidence와 cache/source completion honesty가 결합된 평가가 없으면, plugin 단위 report가 workflow 실행 정직성을 과대 주장할 수 있다.

## 수정 방향

- `plugin` bucket에 P5 workflow-integrity public case와 answer oracle을 추가한다.
- case는 실제 subagent 병렬 실행을 명시 승인한 상황을 주되, role별 write ownership, result collection, not-run validation handoff, cache/source evidence를 함께 요구한다.
- public case에는 answer oracle, scoring, hidden criteria를 노출하지 않는다.
- answer oracle은 P5 plugin-level case임을 coverage tag로 드러내고, workflow trace/result collection evidence와 completion honesty를 hard gate로 둔다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: eval bucket 독립 subagent가 `workflow` bucket은 P4 개별 skill 평가이고, `plugin/runtime/source`에는 end-to-end P5 workflow case가 없다고 보고했다.

skill-creator 리뷰: 해당 없음. 이 문서는 eval case gap 분석이며 skill 자체 문구는 별도 skill 분석에서 처리한다.
