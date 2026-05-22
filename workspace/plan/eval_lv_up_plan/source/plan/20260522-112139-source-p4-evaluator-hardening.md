수정 대상: evaluator

# source P4 evaluator hardening 계획

## 수정 범위

- `workspace/scripts/test_validate_eval_bucket_pack.py`
- `workspace/scripts/validate_eval_bucket_pack.py`

## 절차

1. Public case가 `hard_gates`, `expected_outcomes`, `control_case`, `with_dddjango` 같은 answer-only field를 포함하면 실패하는 test를 먼저 추가한다.
2. `case-source-provisional-drf` validator test가 `architecture-implementation-patterns`와 `implementation-django-web` source basis 누락을 실패시키도록 보강한다.
3. metadata/cache sync answer가 `SKILL.md`, `agents/openai.yaml`, bundled reference, validation output, cache/source parity를 요구하지 않으면 실패하는 test를 추가한다.
4. routing exclusion answer가 positive source audit routing과 implementation/test exclusion을 요구하지 않으면 실패하는 test를 추가한다.
5. 실패를 확인한 뒤 `validate_eval_bucket_pack.py`의 public leakage patterns와 source-specific semantic validators를 보강한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket source`
- 관련 bucket validator 전체 실행

## 완료 조건

- 추가한 failing tests가 validator 보강 후 통과한다.
- source bucket validator가 9개 source case를 통과한다.
- public leakage validator가 answer-only field 누출을 차단한다.
