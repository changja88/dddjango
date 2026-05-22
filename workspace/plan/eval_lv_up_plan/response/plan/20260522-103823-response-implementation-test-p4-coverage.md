수정 대상: case

# implementation-test response P4 계획

## 수정 대상

- `workspace/develop/eval/response/cases/plugin/public/case-response-test-suite-strategy.md`
- `workspace/develop/eval/response/answer/case-response-test-suite-strategy.yaml`
- `workspace/develop/eval/response/cases/plugin/public/case-response-test-tiny-assertion.md`
- `workspace/develop/eval/response/answer/case-response-test-tiny-assertion.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. direct positive public case에 pytest 구조, fixture/conftest, parametrization, assertion, double, factory, property, time/HTTP mocking, testcontainers, coverage/mutation, BDD, flaky, TestClient, idempotency/concurrency 판단을 자연스럽게 요구한다.
2. direct negative public case에 짧은 pytest assertion 질문과 과적용 금지를 명시한다.
3. answer oracle은 `workspace/reference/implementation-test/reference/final.md`, `dddjango/skills/implementation-test/SKILL.md`, 관련 bundled references를 source basis로 연결한다.
4. response bucket validator가 direct implementation-test P4 coverage와 negative/exclusion case를 구조적으로 확인하게 한다.
5. unit test로 missing tag, missing source reference, mixed/P5 tag exclusion을 검증한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `make eval-one BUCKET=response CASE=case-response-test-suite-strategy TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-test-p4 EXTRA_ARGS=--rerun JOBS=1`
- `make eval-one BUCKET=response CASE=case-response-test-tiny-assertion TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-test-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- public case와 answer oracle이 같은 implementation-test 목적을 검증한다.
- answer oracle이 source reference보다 과도하거나 부족한 기준을 요구하지 않는다.
- public case에 answer oracle, private 기준, 이전 run finding이 노출되지 않는다.
- response bucket validator와 targeted eval이 통과한다.
