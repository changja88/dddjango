수정 대상: evaluator

# plugin generic execution claim false positive 분석

## 배경

plugin targeted run `20260522-160000-plugin-try01-targeted-p5-plugin-all`은 answer-oracle evaluation 후 `validate_eval_run.py`에서 두 건의 generic execution claim failure가 발생했다.

## 원인 분류

- 분류: `evaluator`
- 문제 1: `case-plugin-cache-source-mismatch` with-ddjango 출력의 evidence table row가 "validator 통과 결과"를 필요한 증거로 말했지만 validator 실행 claim으로 오탐됐다.
- 문제 2: `case-plugin-leakage-sentinel` baseline 출력의 "eval 전용 내부 판정 문구"가 eval 실행 claim으로 오탐됐다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

generic execution claim detector에서 evidence requirement/result wording과 eval-only wording을 실행 완료 claim으로 보지 않도록 제외 조건을 좁게 추가한다.
