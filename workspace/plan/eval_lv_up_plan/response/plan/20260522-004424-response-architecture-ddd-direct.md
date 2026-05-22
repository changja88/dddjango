수정 대상: evaluator

# architecture-ddd P4 response 평가 개선 계획

## 수정 범위

- `workspace/develop/eval/response/cases/plugin/public/case-response-ddd-subscription-boundary.md`
- `workspace/develop/eval/response/answer/case-response-ddd-subscription-boundary.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`

## 절차

1. public case는 구독/사용권 도메인 설계 요청으로 작성한다.
2. answer oracle은 architecture-ddd source reference에 맞춰 subdomain, bounded context, ubiquitous language, aggregate, entity/value object, invariant, domain event/service, use case, consistency boundary를 판정한다.
3. evaluator는 response answer의 `architecture-ddd-direct` coverage tag를 감지해 `ddd_observations` 필수 필드를 검증한다.
4. validator와 targeted eval을 실행해 case/answer/evaluator 정합성을 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- 필수 전체 검증 단계에서 `validate_plan_constraints.py`, `test_validate_plan_constraints.py`, `validate_skill_docs.py --phase all`, 관련 bucket validator를 다시 실행한다.
- targeted eval: `make eval-one BUCKET=response CASE=case-response-ddd-subscription-boundary TRY_NUMBER=1 SCOPE=targeted TOPIC=architecture-ddd-direct EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- response bucket validator가 architecture-ddd direct coverage를 구조적으로 확인한다.
- public case에는 private answer 기준이나 이전 run finding이 없다.
- answer oracle은 source reference보다 과도한 구현 패턴, DB/API/Workflow 요구를 강제하지 않는다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0 상태로 닫힌다.

