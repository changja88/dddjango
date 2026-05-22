수정 대상: evaluator

# code small rename unittest validator 계획

## 수정 범위

- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_run.py`

## 절차

1. generic validator evidence pattern에 `unittest`를 추가한다.
2. code response가 `검증: python3 -m unittest`를 보고할 때 matching check artifact가 있으면 통과하는 테스트를 추가한다.
3. `test_validate_eval_run.py`와 code bucket validator를 실행한다.
4. 실패 run을 재검증하고, 필요하면 `case-code-small-rename` targeted eval을 재실행한다.

## 완료 조건

- 실제 `python3 -m unittest` 실행 artifact가 있는 code run은 generic `검증` 문구 때문에 실패하지 않는다.
- unsupported pytest/ruff/mypy/validator claim hard gate는 유지된다.
