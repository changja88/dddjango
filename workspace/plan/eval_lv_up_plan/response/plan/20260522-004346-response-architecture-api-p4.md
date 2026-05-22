수정 대상: case

# architecture-api P4 평가 개선 계획

## 목표

response bucket이 `architecture-api` 개별 skill 목적과 source/runtime reference를 직접 검증하도록 positive/negative case를 보강한다.

## 수정 대상

- `workspace/develop/eval/response/cases/plugin/public/case-response-api-contract.md`
- `workspace/develop/eval/response/answer/case-response-api-contract.yaml`
- `workspace/develop/eval/response/cases/plugin/public/case-response-api-boundary-negative.md`
- `workspace/develop/eval/response/answer/case-response-api-boundary-negative.yaml`

## 절차

1. positive case를 추가한다.
   - REST resource/URL, method/status, request/response/header, Problem Details, auth/authz, content negotiation, pagination, versioning/deprecation, rate limit, `Idempotency-Key`, OpenAPI impact를 모두 요구한다.
   - Django code, DB schema, test code 구현은 제외하여 개별 `architecture-api` 평가로 유지한다.
2. negative boundary case를 추가한다.
   - GraphQL/WebSocket/HATEOAS/API Gateway 설계를 REST 계약 skill이 직접 소유하지 않도록 검증한다.
   - 필요한 경우 REST boundary만 짧게 제시하고, 비-REST 세부 설계와 Django Ninja 구현을 피하도록 한다.
3. answer oracle을 작성한다.
   - reference basis는 response eval goal, architecture-api source reference, runtime `SKILL.md`, bundled references로 제한한다.
   - public case에 evaluator-only 표현이나 private scoring 기준을 누설하지 않는다.
4. 검증을 실행한다.
   - `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
   - `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
   - `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
   - `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
   - `make eval-one BUCKET=response CASE=case-response-api-contract TRY_NUMBER=1 SCOPE=targeted TOPIC=architecture-api-p4 EXTRA_ARGS=--rerun JOBS=1`
   - `make eval-one BUCKET=response CASE=case-response-api-boundary-negative TRY_NUMBER=1 SCOPE=targeted TOPIC=architecture-api-p4 EXTRA_ARGS=--rerun JOBS=1`
5. 독립 리뷰를 실행한다.
   - skill-creator 관점: trigger, 목적, reference, progressive disclosure, validation integrity 판정
   - 독립 관점: P4 inventory, public leakage, oracle over/under-claim, evaluator alignment 판정
6. 리뷰 결과 Blocker/Major/열린 Minor가 있으면 case/answer를 좁게 재수정하고 검증을 반복한다.

## 완료 조건

- response bucket에 architecture-api 단독 positive/negative case가 존재한다.
- answer oracle이 source/runtime reference보다 과도하거나 부족한 요구를 하지 않는다.
- public case가 answer oracle, private 기준, 이전 run finding을 누설하지 않는다.
- 관련 validator와 targeted eval이 통과한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
