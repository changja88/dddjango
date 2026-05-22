수정 대상: evaluator
원인 분류: evaluator

# P5 plugin run validation honesty 분석

## 문제

최종 독립 리뷰에서 plugin P5 targeted run validator가 subagent trace/result collection은 검증하지만, 응답 본문이 validator, eval, browser, Serena 실행 완료를 허위로 주장하는 경우를 deterministic hard gate로 충분히 잡지 못한다고 지적했다.

현재 `validate_eval_run.py`는 code bucket의 command/test claim에는 비교적 강한 검증이 있으나, plugin/workflow/response 같은 read-only bucket의 일반 실행 claim은 evaluator 자연어 판정에 더 의존한다.

## 영향

P5 기준의 "실행하지 않은 validator, eval, browser, Serena, subagent review를 실행했다고 쓰지 않는다"가 plugin-level run validation에서 구조적으로 닫히지 않는다. answer oracle은 이를 요구하지만 validator가 직접 보조하지 않으면 evaluator undercheck가 남는다.

## 수정 방향

- read-only eval output의 validation/eval/browser/Serena completion claim을 conservative하게 탐지한다.
- not-run, skipped, did not run 같은 부정/미실행 보고는 실패시키지 않는다.
- 실행 claim이 있으면 해당 variant event stream에 관련 tool/command evidence가 있어야 한다.
- plugin/workflow P5 run validation에서 이 hard gate를 적용한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 최종 workflow-integrity review subagent가 run validator undercheck를 Major로 보고했다.

skill-creator 리뷰: 해당 없음. 이 문서는 eval run validator 보강 분석이다.
