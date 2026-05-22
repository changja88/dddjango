수정 대상: evaluator
원인 분류: evaluator

# P5 trigger-routing validator 분석

## 범위

`case-plugin-trigger-routing`은 plugin-level P5 restraint case로 `restraint_scope: plugin-level`과 `p5-plugin-restraint`를 가진다. 이 case가 요구하는 opt-out, tiny edit, Direct Answer Mode, false-claim refusal, no meta-tail restraint가 static validator에서 보존되는지 점검했다.

## 발견 사항

기존 validator는 `trigger-quality`에 대해 frontmatter description, positive/negative routing, Korean trigger, body-only trigger rejection만 확인했다. 따라서 `case-plugin-trigger-routing.yaml`에서 P5 restraint-specific 요구가 삭제되어도 tag와 scope만 남으면 static validator가 통과할 수 있었다.

## Inventory

| bucket | case id | 검증하는 restraint | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|
| plugin | `case-plugin-trigger-routing` | opt-out/tiny/direct-answer/false-claim/meta-tail trigger routing | evaluator 수정 | 예 | 없음 | 미실행 |

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent `019e4dff-ce55-7823-8b98-82bea9feedf1` 결과를 `wait_agent`로 수집했고, P5 trigger-routing semantic undercheck를 Major로 보고했다.

skill-creator 리뷰: real subagent `019e4dff-e538-7680-88b7-da8d3464f938` 결과는 Blocker 0, Major 0, 열린 Minor 0으로 보고했다. 두 리뷰가 충돌했으나, validator가 구체 P5 dimension을 보존하지 못한다는 지적은 재현 가능한 evaluator gap이므로 메인 판단에서 수정 대상으로 채택했다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 완료 조건

- `validate_plugin_governance_answer`가 `p5-plugin-restraint` + `trigger-quality` 조합에서 opt-out, tiny edit, Direct Answer Mode, false-claim refusal, no meta-tail restraint, trigger/routing surface를 요구한다.
- 해당 undercheck를 잡는 unit test와 정상 case를 받는 unit test가 있다.
- plugin bucket validator와 targeted eval이 통과한다.
