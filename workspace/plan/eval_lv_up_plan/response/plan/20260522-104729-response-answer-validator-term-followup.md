수정 대상: answer

# response answer validator term follow-up 계획

## 수정 범위

- `workspace/develop/eval/response/answer/case-response-django-ninja-endpoint.yaml`
- `workspace/develop/eval/response/answer/case-response-drf-ninja.yaml`
- `workspace/develop/eval/response/answer/case-response-test-suite-strategy.yaml`

## 절차

1. Django Ninja endpoint answer에 DRF-to-Ninja migration compatibility를 `target_behavior.required`로 명시한다.
2. DRF-to-Ninja answer에 Schema/ModelSchema, authentication/permission, filtering/sorting compatibility를 명시한다.
3. Implementation-test answer에 conftest, assertion, test double, fake/mock, factory/Faker, Hypothesis invariant, stakeholder BDD, barrier/lock timeout/no arbitrary sleeps 기준을 명시한다.
4. Public case는 수정하지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- 수정한 각 answer case의 targeted eval:
  - `make eval-one BUCKET=response CASE=case-response-django-ninja-endpoint TRY_NUMBER=1 SCOPE=targeted TOPIC=response-oracle-validator-terms EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=response CASE=case-response-drf-ninja TRY_NUMBER=1 SCOPE=targeted TOPIC=response-oracle-validator-terms EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=response CASE=case-response-test-suite-strategy TRY_NUMBER=1 SCOPE=targeted TOPIC=response-oracle-validator-terms EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- response bucket validator가 통과한다.
- answer oracle이 source reference보다 과도하거나 부족한 요구를 하지 않는다.
- targeted eval 결과 또는 실패 run artifact와 원인 분류를 남긴다.
