수정 대상: case

# workflow validation sharing P4 계획

## 목표

`case-workflow-parallel-ownership`이 병렬 역할의 파일 ownership뿐 아니라 검증 책임 분담과 통합 handoff까지 확인하도록 좁게 보강한다.

## 수정

1. Public case에 각 subagent/role이 맡을 검증 책임과 실행/미실행 검증을 최종 통합에 넘기는 방식을 요청하는 문장을 추가한다.
2. Answer oracle의 `reference_basis`에 `integration-checklist.md`를 추가해 validation honesty와 role handoff closure 기준을 명확히 연결한다.
3. `target_behavior.required`, `workflow_execution_expectation.responsibility_rule`, `scoring_checks`, `failure_modes`, `evidence_required`, `coverage_tags`에 validation sharing 요구를 추가한다.
4. `eval_goal.md`의 case family와 minimum workflow checks에 validation sharing 축을 추가한다.

## 검증

1. `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
2. `make eval-one BUCKET=workflow CASE=case-workflow-parallel-ownership TRY_NUMBER=1 SCOPE=targeted TOPIC=workflow-validation-sharing EXTRA_ARGS=--rerun JOBS=1`
3. 결과 run id/status와 raw stdout/stderr, RUN_VALIDATION/report 확인
