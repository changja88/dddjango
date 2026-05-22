수정 대상: evaluator
원인 분류: evaluator undercheck

# architecture-db P4 direct coverage mixed-case 차단 계획

## 수정 파일

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 작업 순서

1. mixed/P5-adjacent coverage tag 목록을 상수로 추가한다.
2. `architecture_db_direct_tags()`에서 `case_id`가 `case-response-db-`로 시작하는지 확인한다.
3. 같은 함수에서 mixed/P5-adjacent tag가 하나라도 있으면 architecture-db P4 direct coverage로 세지 않는다.
4. `test_validate_eval_bucket_pack.py`에 mixed case가 all DB P4 tags와 architecture-db references를 갖고 있어도 direct coverage를 만족하지 못하는 regression test를 추가한다.
5. `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`를 실행한다.
6. `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`를 실행한다.

## 완료 조건

- mixed response answer가 DB tag와 DB reference를 넣어도 direct architecture-db P4 coverage를 대체할 수 없다.
- 실제 response bucket validator는 현재 direct DB cases로 통과한다.
