수정 대상: evaluator

# implementation-python code 평가 validator 개선 계획

## 수정 대상

- `workspace/develop/eval/code/answer/case-code-python-state.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. `case-code-python-state.yaml`의 reference basis를 implementation-python source/runtime/bundled reference로 보강한다.
2. coverage tag에 code-backed implementation-python tag를 추가한다.
3. target behavior에 type contract, Enum/StrEnum, value object, Protocol/pydantic restraint, Ruff/typecheck/test reporting honesty를 명시한다.
4. validator에 code bucket implementation-python P4 coverage set과 direct source-backed case 확인을 추가한다.
5. code branch에서도 `validate_implementation_python_answer()`를 실행한다.
6. unit test로 missing coverage/reference를 검증한다.
7. code bucket validator와 targeted eval `case-code-python-state`를 재실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `make eval-one BUCKET=code CASE=case-code-python-state TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-python-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- code-backed implementation-python case가 source/runtime/bundled reference에 trace된다.
- validator가 code bucket의 implementation-python coverage 누락을 실패로 만든다.
- public case에는 answer oracle/schema/private finding 누설이 없다.
- targeted eval이 재실행되고 통과한다.
