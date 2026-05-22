수정 대상: evaluator
원인 분류: evaluator undercheck

# architecture-db P4 evaluator 수정 계획

## 수정 파일

- `workspace/scripts/test_validate_eval_bucket_pack.py`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_run.py`
- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_protocol.py`
- `workspace/scripts/validate_eval_protocol.py`

## TDD 작업 순서

1. `test_validate_eval_bucket_pack.py`에 response bucket이 architecture-db P4 coverage tags를 요구하는 실패 테스트를 추가한다.
   - fixture answer에서 tag 하나를 누락하면 `architecture-db P4 coverage_tags missing` finding이 나와야 한다.
2. 실패를 확인한다.
   - `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
3. `validate_eval_bucket_pack.py`에 response-only architecture-db P4 required tag 검사를 추가한다.
4. 테스트를 통과시킨다.
   - `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
5. `test_validate_eval_run.py`에 zero-byte 또는 invalid JSON prompt-input artifact 실패 테스트를 추가한다.
   - with-dddjango prompt-input 파일이 비어 있으면 finding이 나와야 한다.
6. 실패를 확인한다.
   - `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
7. `validate_eval_run.py`에서 prompt-input artifact를 non-empty JSON object 또는 array로 검증한다.
8. 테스트를 통과시킨다.
   - `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
9. `test_validate_eval_protocol.py`에 zero-byte prompt-input artifact 실패 테스트를 추가한다.
10. 실패를 확인한다.
   - `.venv/bin/python -B workspace/scripts/test_validate_eval_protocol.py`
11. `validate_eval_protocol.py`에서 prompt-input artifact를 non-empty JSON object 또는 array로 검증한다.
12. 테스트를 통과시킨다.
   - `.venv/bin/python -B workspace/scripts/test_validate_eval_protocol.py`
13. 관련 validator를 실행한다.
   - `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
   - `.venv/bin/python -B workspace/scripts/validate_eval_run.py --bucket response --run-id 20260522-004622-response-try01-targeted-architecture-db-p4 --case case-response-db-schema-modeling`
   - `.venv/bin/python -B workspace/scripts/validate_eval_protocol.py --run-dir workspace/develop/eval/response/runs/20260522-004622-response-try01-targeted-architecture-db-p4 --case case-response-db-schema-modeling`

## 완료 조건

- response bucket structural validator가 architecture-db P4 coverage gap을 놓치지 않는다.
- run/protocol validator가 empty/invalid prompt-input artifact를 놓치지 않는다.
- 실패한 targeted run은 실제 run failure와 missing oracle evaluation을 계속 실패로 보고해야 한다.
