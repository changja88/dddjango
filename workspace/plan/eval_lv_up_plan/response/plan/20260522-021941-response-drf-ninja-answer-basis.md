수정 대상: answer

목표:

- `case-response-drf-ninja`가 DRF guardrail뿐 아니라 implementation-django-ninja의 DRF-to-Ninja migration 기준을 직접 검증하게 한다.

수정 순서:

1. `workspace/develop/eval/response/answer/case-response-drf-ninja.yaml`의 reference basis를 implementation-django-ninja source/runtime/bundled refs로 보강한다.
2. coverage tags에 implementation-django-ninja 관련 tag를 추가해 validator source checks가 적용되게 한다.
3. target behavior와 failure modes를 source reference 기준으로 좁게 보강한다.
4. public prompt는 수정하지 않는다.

검증:

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- targeted eval: `make eval-one BUCKET=response CASE=case-response-drf-ninja TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-ninja-p4 EXTRA_ARGS=--rerun JOBS=1`

완료 조건:

- response bucket validator가 통과한다.
- public case 누설 없이 answer oracle만 보강된다.
- targeted eval run id와 pass/fail status를 inventory에 기록한다.
