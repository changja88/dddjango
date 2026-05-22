수정 대상: evaluator
원인 분류: evaluator undercheck

# architecture-db P4 local CRUD negative coverage 계획

## 수정 파일

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`
- `workspace/develop/eval/response/answer/case-response-db-local-crud-restraint.yaml`

## 작업 순서

1. `RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS`에 `db-local-crud-restraint`를 추가한다.
2. `test_response_bucket_requires_architecture_db_p4_coverage_tags` fixture에 `migration-safety`를 명시해 production tag set과 test fixture를 맞춘다.
3. 같은 테스트가 새 `db-local-crud-restraint` 누락도 `architecture-db P4 direct coverage_tags missing` finding으로 잡도록 둔다.
4. `case-response-db-local-crud-restraint.yaml`에 `db-local-crud-restraint` coverage tag를 추가한다.
5. `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`를 실행한다.
6. `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`를 실행한다.
7. 수정한 answer case이므로 `case-response-db-local-crud-restraint` targeted eval을 실행한다.

## 완료 조건

- DB-specific local CRUD negative case가 구조적으로 필요한 architecture-db P4 direct coverage가 된다.
- response bucket validator가 통과한다.
- targeted eval 결과를 최종 보고에 남긴다.
