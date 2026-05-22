수정 대상: case

# implementation-python P4 평가 개선 계획

## 수정 대상

- `workspace/develop/eval/response/cases/plugin/public/case-response-python-boundaries.md`
- `workspace/develop/eval/response/answer/case-response-python-boundaries.yaml`
- `workspace/develop/eval/response/cases/plugin/public/case-response-python-tiny-type-hint.md`
- `workspace/develop/eval/response/answer/case-response-python-tiny-type-hint.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. direct positive public case는 Python 3.11/3.12 target 확인, external JSON shape, status type, Protocol boundary, context manager, pydantic v2, async, exceptions, Ruff/mypy/pyright 보고 정직성을 묻되 public prompt에는 answer schema와 private 기준을 넣지 않는다.
2. tiny negative public case는 짧은 type hint 질문에 직접 답하게 하고 workflow, DDD, DB/API/Django 설계로 확장하지 않게 한다.
3. answer oracle은 implementation-python source final, `SKILL.md`, `typing.md`, `dataclasses-enums.md`, `protocols-boundaries.md`, `pydantic-v2.md`에 trace한다.
4. evaluator에 implementation-python P4 coverage tag set과 answer validator를 추가한다.
5. validator unit test를 추가해 coverage gap과 reference basis 누락을 실패로 만든다.
6. 관련 validator와 targeted eval을 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- targeted eval:
  - `make eval-one BUCKET=response CASE=case-response-python-boundaries TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-python-p4 EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=response CASE=case-response-python-tiny-type-hint TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-python-p4 EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=code CASE=case-code-python-state TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-python-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- implementation-python positive/negative coverage가 source reference와 runtime bundled reference에 trace된다.
- public case에 oracle/schema/private finding 누설이 없다.
- response/code bucket validator가 통과한다.
- 추가/대표 관련 case의 targeted eval이 실행된다.
- independent review 후 Blocker 0, Major 0, 열린 Minor 0 상태다.
