수정 대상: evaluator
원인 분류: evaluator

# non-negative expected_delta 검증 분석

## 문제

closing review에서 `validate_eval_run.py`가 `expected_delta: positive`만 점수 차이를 검증하고 `expected_delta: non-negative`는 검증하지 않는 gap이 확인됐다. 그 결과 with-dddjango 점수가 baseline보다 낮아도 targeted run validation이 pass할 수 있었다.

## 수정 방향

- `expected_delta: non-negative`일 때 with-ddjango score가 baseline score보다 낮으면 실패한다.
- 기존 `positive` 검증은 유지한다.
- unit test에 non-negative 역전 실패 case를 추가한다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: 독립 closing review가 Major 2개로 동일 evaluator gap을 지적했다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
