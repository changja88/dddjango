수정 대상: evaluator

# source eval 후속 분류 분석

## 평가 요약

source-reference-audit P1 독립 리뷰 중 `workspace/develop/eval/source/eval_goal.md`의 Reference Basis에 `dddjango/skills/source-reference-audit/SKILL.md`가 중복 기재된 것이 발견됐다. 이는 source inventory cleanliness를 약화하는 eval-pack 품질 문제지만, P1 금지 조건에 따라 이번 작업에서는 eval pack을 수정하지 않는다.

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

Subagent 리뷰/순차 fallback: 독립 P1 리뷰 subagent가 Minor로 보고했다. 메인 판단도 Minor 후속 작업으로 채택한다.

## 근거

- `workspace/develop/eval/source/eval_goal.md` Reference Basis에 같은 `dddjango/skills/source-reference-audit/SKILL.md`가 여러 번 등장한다.
- validator는 통과하지만, 중복은 source inventory를 읽는 사람에게 불필요한 혼선을 준다.

## 후속 대상

- bucket: `source`
- 성격: eval goal/reference basis cleanup
- 권장 수정 대상: `workspace/develop/eval/source/eval_goal.md`

## P1에서 수정하지 않는 이유

P1 목표는 source reference와 skill/runtime sync를 닫는 것이다. 사용자의 금지 조건은 eval 문제가 발견되면 P1에서 임의로 고치지 말고 `workspace/plan/eval_lv_up_plan/<bucket>/analysis/` 후속 대상으로 분류하라고 명시한다.

## 허용 claim

- source eval goal에 중복 reference-basis entry가 있어 후속 cleanup이 필요하다.
- 현재 validators는 이 중복을 실패로 보지 않는다.

## 금지 claim

- 이번 P1에서 source eval goal 중복을 수정했다고 말하지 않는다.
- 중복이 있다는 이유만으로 source-reference-audit P1 reference/skill runtime sync가 실패했다고 확대하지 않는다.
