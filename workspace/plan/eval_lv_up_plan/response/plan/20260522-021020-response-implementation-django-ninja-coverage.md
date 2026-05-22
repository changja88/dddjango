수정 대상: case

목표:

- implementation-django-ninja 개별 skill 평가가 source reference 기반으로 Router, Schema/ModelSchema, endpoint adapter, auth/permission, filtering/sorting, pagination, Problem Details, OpenAPI, TestClient, DRF-to-Ninja 경계를 검증하게 만든다.

수정 순서:

1. `workspace/develop/eval/response/cases/plugin/public/case-response-django-ninja-endpoint.md`를 추가한다.
2. `workspace/develop/eval/response/answer/case-response-django-ninja-endpoint.yaml`을 추가한다.
3. answer oracle의 `reference_basis`에는 implementation-django-ninja source reference, SKILL.md, bundled references를 포함한다.
4. target behavior는 Django Ninja adapter 구현 기준으로 좁히고, REST 계약 결정, DB transaction/storage, domain invariant, detailed pytest mechanics는 handoff 또는 out-of-scope로 둔다.
5. public case가 answer field, private scoring text, 이전 run finding, local absolute path를 누설하지 않는지 확인한다.

검증:

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- 추가 case targeted eval: `make eval-one BUCKET=response CASE=case-response-django-ninja-endpoint TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-ninja-p4 EXTRA_ARGS=--rerun JOBS=1`

완료 조건:

- 신규 public/answer pair가 response bucket 구조 검증을 통과한다.
- 신규 answer가 reference보다 과도하거나 부족한 요구를 하지 않는다.
- targeted eval run id와 pass/fail status를 inventory에 기록한다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
