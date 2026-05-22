수정 대상: evaluator

# P5 trigger-routing validator 수정 계획

1. `workspace/scripts/validate_eval_bucket_pack.py`의 `validate_plugin_governance_answer`에서 `trigger-quality`와 `p5-plugin-restraint` tag가 함께 있을 때 P5 restraint-specific dimension을 검사한다.
2. `workspace/scripts/test_validate_eval_bucket_pack.py`에 누락 case가 실패하는 테스트와 모든 dimension이 있는 case가 통과하는 테스트를 추가한다.
3. `test_validate_eval_bucket_pack.py`, plugin bucket validator, 전체 관련 bucket validator를 실행한다.
4. `case-plugin-trigger-routing` targeted eval과 `validate_eval_run.py`는 model-backed eval 승인 후 실행한다.
