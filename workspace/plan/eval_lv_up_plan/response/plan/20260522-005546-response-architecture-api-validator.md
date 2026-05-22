수정 대상: evaluator

# architecture-api P4 validator 개선 계획

## 목표

`response` bucket pack validation이 `architecture-api` P4 coverage drift를 구조적으로 잡고, 두 new case의 oracle이 source/runtime reference보다 과도하지 않게 한다.

## 수정 대상

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`
- `workspace/develop/eval/response/answer/case-response-api-contract.yaml`
- `workspace/develop/eval/response/answer/case-response-api-boundary-negative.yaml`
- `workspace/develop/eval/response/cases/plugin/public/case-response-api-boundary-negative.md`

## 절차

1. `validate_eval_bucket_pack.py`에 response bucket 전용 architecture-api P4 coverage tag set을 추가한다.
2. 새 architecture-api P4 validator test를 추가한다.
3. positive case answer에 REST 계약 세부 coverage tag를 추가하고 `204` negative justification 요구를 제거한다.
4. negative boundary case는 gRPC/SOAP 제외 조건을 포함하되, REST boundary를 과확장하지 않도록 oracle overclaim을 줄인다.
5. 다음 검증을 실행한다.
   - `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
   - `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
   - 필수 검증 command 전체
   - 수정 case targeted eval 재실행

## 완료 조건

- architecture-api P4 coverage tag가 빠지면 `validate_eval_bucket_pack.py --bucket response`가 실패한다.
- public prompt에 private oracle 표현이 누설되지 않는다.
- answer oracle이 source/runtime reference보다 과도한 요구를 하지 않는다.
- targeted eval이 다시 통과한다.
