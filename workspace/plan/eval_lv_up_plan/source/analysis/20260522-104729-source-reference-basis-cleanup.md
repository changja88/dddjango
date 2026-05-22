수정 대상: answer
원인 분류: answer cleanup

# source reference basis cleanup 분석

## 문제

source P4 review에서 `workspace/develop/eval/source/eval_goal.md`와 `case-source-docs-coherence.yaml`의 `reference_basis`에 `dddjango/skills/source-reference-audit/SKILL.md`가 중복 기재되어 있다는 열린 Minor가 확인됐다.

중복은 source decision을 틀리게 만들지는 않지만, P4 종료 조건인 열린 Minor 0을 만족하려면 source inventory cleanliness를 정리해야 한다.

## 대상

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 |
|---|---|---|---|---|---|---|
| source | `case-source-docs-coherence` | 변경 없음 | 중복 `reference_basis` 제거 | 구조 validator와 answer oracle traceability에 관련 | answer 수정 | 예 |
| source | bucket goal | 해당 없음 | 해당 없음 | source inventory 기준 문서 | eval_goal cleanup | 아니오 |

## 판단

- public case에는 answer oracle, private 기준, 이전 run finding 누설이 없다.
- 중복 제거는 reference보다 강하거나 약한 요구를 만들지 않는다.
- `case-source-docs-coherence` answer를 수정했으므로 targeted eval이 필요하다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

Subagent 리뷰/순차 fallback: 두 review 중 하나는 중복을 Note로, 다른 하나는 P4 gate상 Minor로 분류했다. 메인 판단은 P4의 열린 Minor 0 조건에 맞춰 수정 대상으로 채택한다.
