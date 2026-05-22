수정 대상: case

# P5 Django implementation 연계 평가 계획

1. `case-response-django-implementation-handoff.md`를 추가한다. Public prompt는 주문 확정 구현 전 handoff 계획만 요구하고, 실제 파일 수정/테스트/subagent 실행을 금지한다.
2. `case-response-django-implementation-handoff.yaml`을 추가한다. Required behavior는 다음 책임 경계를 평가한다.
   - architecture-api 계약 vs implementation-django-ninja Router/Schema adapter
   - architecture-db transaction/constraint/rollout policy vs implementation-django service/migration implementation
   - implementation-django-web view/context/template/static/form boundary vs domain/template leakage
   - implementation-python typing/value object/Enum boundary
   - implementation-tdd 절차 vs implementation-test pytest mechanics
   - implementation-cleancode review findings vs production implementation ownership
   - workflow/subagent 실행 정직성
3. `case-response-django-web-one-line-edit.md`를 추가한다. Public prompt는 한 줄 Django template copy edit만 요구하고 workflow/subagent/TDD/DB/API 설계를 제외한다.
4. `case-response-django-web-one-line-edit.yaml`을 추가한다. Required behavior는 concise direct answer, Django Web 파일 영향 범위, 실행하지 않은 검증의 not-run 처리, workflow 과적용 금지를 평가한다.
5. code bucket은 full-role omnibus case를 새로 만들지 않는다. `case-code-order-api`는 `implementation_supporting`으로 유지하고, P5 completion evidence에는 response/workflow/plugin handoff case와 code bucket surface별 supporting targeted rerun을 분리해 보고한다.
6. `validate_plan_constraints.py`, `test_validate_plan_constraints.py`, `validate_eval_bucket_pack.py --bucket response`를 실행한다.
7. 새 response case 2개에 targeted eval을 실행한다.
   - `make eval-one BUCKET=response CASE=case-response-django-implementation-handoff TRY_NUMBER=1 SCOPE=targeted TOPIC=django-implementation-p5-integration EXTRA_ARGS=--rerun JOBS=1`
   - `make eval-one BUCKET=response CASE=case-response-django-web-one-line-edit TRY_NUMBER=1 SCOPE=targeted TOPIC=django-implementation-p5-integration EXTRA_ARGS=--rerun JOBS=1`
8. pass run마다 `validate_eval_run.py`로 run artifact를 확인한다. Sandbox/authorization 실패 시 명령과 데이터 전송 위험을 명시해 승인 요청 후 계속한다.
