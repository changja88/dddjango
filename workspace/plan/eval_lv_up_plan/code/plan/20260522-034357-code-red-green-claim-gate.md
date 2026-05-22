수정 대상: evaluator

# code eval red-green 검증 주장 gate 계획

## 수정 대상

- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_run.py`

## 절차

1. raw output에서 exact `python3 -m unittest...` command claim을 추출한다.
2. claim이 captured check command 목록과 정확히 일치하지 않으면 실패한다.
3. raw output에서 구현 전 실패/red-green/failing test claim을 추출한다.
4. non-zero check artifact가 없으면 실패한다.
5. unit test를 추가하고 기존 최신 run이 fail하는지 확인한다.
6. targeted eval을 재실행해 새 run이 stricter validator를 통과하는지 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_run.py --bucket code --run-id 20260522-033438-code-try01-targeted-implementation-python-p4 --case case-code-python-state` 는 실패해야 한다.
- `make eval-one BUCKET=code CASE=case-code-python-state TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-python-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- unsupported exact command/red-green claims가 run validation을 통과하지 못한다.
- 최신 targeted eval run이 pass한다.
