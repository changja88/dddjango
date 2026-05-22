수정 대상: evaluator

# coupon TDD red-proof integrity 계획

## 수정 범위

- `workspace/scripts/eval_code_behavior_checks.py`
- `workspace/scripts/test_eval_code_behavior_checks.py`
- `workspace/scripts/validate_eval_bucket_pack.py`

## 수정 순서

1. `coupon.used`를 참조하는 `if` guard를 AST 기반으로 제거한다.
2. red-proof 성공은 guard 제거 후 unittest가 실패한 경우로 한정해 exit 1을 반환한다.
3. guard 제거 실패 또는 guard 제거 후 unittest 통과는 exit 2로 반환한다.
4. exact string guard, `coupon.used is True` guard, guard missing case에 대한 회귀 테스트를 추가한다.
5. validation-honesty required-term gate에서 loose `unless` 계열만으로 통과하지 못하게 조인다.
6. code/response bucket validator와 targeted eval을 재실행한다.

## 완료 조건

- red-proof success와 evaluator failure가 exit code로 구분된다.
- implementation-tdd targeted code eval이 새 evaluator로 pass run을 남긴다.
- 최종 리뷰의 Blocker/Major가 닫힌다.

