수정 대상: answer
원인 분류: answer

# P5 opt-out/restraint plugin routing 분석

## 범위

`plugin` bucket의 `case-plugin-trigger-routing`이 skill frontmatter와 routing boundary를 점검하지만, P5 opt-out/restraint 관점의 tiny edit, direct answer, false claim, output-shape preservation을 plugin-level trigger 품질로 직접 묶지 못하는지 확인했다.

## 발견 사항

현재 public case는 frontmatter description 기준 리뷰를 요구하므로 P5 plugin-level restraint의 좋은 진입점이다. 그러나 answer oracle의 required behavior가 opt-out, tiny edit, Direct Answer Mode, false claim refusal, meta-tail restraint를 명시적으로 요구하지 않아 P5 restraint routing을 통과 근거로 쓰기 어렵다.

## Inventory

| bucket | case id | 검증하는 restraint | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|
| plugin | `case-plugin-trigger-routing` | plugin-wide trigger/routing boundary | answer 수정 | 예 | 없음 | 미실행 |

## P4/P5 구분

이 case는 특정 individual skill negative가 아니라 skill bundle 전체의 frontmatter trigger와 boundary 품질을 묻는다. P5 plugin-level restraint로 분류하되, public prompt에는 private oracle이나 이전 run finding을 넣지 않는다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent가 plugin bucket에 dedicated P5 restraint routing 명시가 없다고 보고했다. 결과 수집 근거는 `wait_agent`로 완료 상태를 받은 `019e4df3-1389-7432-bfba-8346978b5fed`, `019e4df3-29e2-7d61-b972-cfbdd29b9d7f`이다.

skill-creator 리뷰: trigger description이 body-only restraint rule을 숨기지 않는지 확인해야 한다는 기준을 적용했다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 완료 조건

- `case-plugin-trigger-routing.yaml`이 P5 restraint routing을 answer-level 요구로 명시한다.
- `restraint_scope: plugin-level`과 `p5-plugin-restraint` tag가 붙는다.
- plugin bucket validator와 targeted eval이 통과한다.
