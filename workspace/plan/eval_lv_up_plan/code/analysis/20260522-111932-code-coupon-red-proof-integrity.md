수정 대상: evaluator
원인 분류: evaluator

# coupon TDD red-proof integrity 분석

## 범위

- bucket: `code`
- case: `case-code-coupon-tdd`
- evaluator: `workspace/scripts/eval_code_behavior_checks.py`

## 현상

최종 리뷰에서 hidden red-proof check가 exit code만으로 red proof 성공과 mutation 실패를 구분하지 못한다는 Blocker가 확인됐다. 기존 구현은 사용 쿠폰 guard 제거 후 테스트가 실패하면 exit 1을 반환했지만, guard 제거에 실패하거나 테스트가 여전히 통과하는 실패 상태도 `AssertionError`로 exit 1이 될 수 있었다.

또한 guard 제거가 exact string replacement에 의존해 `coupon.used is True`나 다른 error message 같은 유효한 구현 변형을 mutating하지 못할 수 있었다.

## 판단

원인은 evaluator integrity 부족이다. red-proof 성공은 "guard를 제거했고, 그 결과 테스트가 실패했다"로 정의해야 한다. guard 제거 실패 또는 테스트가 계속 통과하는 경우는 별도 exit 2로 분리해 answer oracle의 `expected_exit: 1`과 구분한다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

재평가 결과: red-proof 성공은 exit 1, mutation 실패/통과는 exit 2로 분리됐다. `20260522-112629-code-try01-targeted-implementation-tdd-p4`가 passed이고 RUN_VALIDATION findings가 없다.
