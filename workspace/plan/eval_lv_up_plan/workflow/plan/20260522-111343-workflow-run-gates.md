수정 대상: evaluator

# workflow run gate P4 계획

## 수정 순서

1. `validate_eval_run.py`의 expected outcome validation에 `with_dddjango` verdict expectation check를 추가한다.
2. workflow execution gate validation이 `partial` 또는 `pass-limited` stale verdict도 실패 처리하도록 조정한다.
3. 각 동작을 `test_validate_eval_run.py`에 unit test로 고정한다.
4. 관련 tests와 workflow bucket validator를 실행한다.

## 완료 조건

- hard gate violation이 `pass`, `partial`, `pass-limited`, `pass-control` 등 non-fail verdict를 통과시키지 않는다.
- `expected_outcomes.with_dddjango` 선언과 실제 verdict가 충돌하면 validator가 실패한다.
