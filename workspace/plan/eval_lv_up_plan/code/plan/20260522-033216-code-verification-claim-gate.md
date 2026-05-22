수정 대상: evaluator

# code eval 검증 주장 gate 개선 계획

## 수정 대상

- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_run.py`
- `workspace/develop/eval/code/cases/plugin/public/case-code-python-state.md`

## 절차

1. code artifact validator에 variant output 검증 도구 claim scan을 추가한다.
2. captured check command 목록을 읽고 claim tool과 matching command가 없으면 fail한다.
3. unit test로 `pytest` claim + `python3 -m unittest` artifact 조합이 실패하는지 확인한다.
4. public case에 exact command-name reporting 조건을 추가한다.
5. validator tests와 targeted eval을 재실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `make eval-one BUCKET=code CASE=case-code-python-state TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-python-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- false verification tool claim이 run validation에서 실패한다.
- targeted eval은 command claim과 artifact가 일치하는 상태로 pass한다.
