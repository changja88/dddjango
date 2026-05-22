수정 대상: evaluator

# source validation-coverage unrun negation 계획

## 수정 범위

- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_run.py`

## 절차

1. source validation coverage raw output line을 기준으로 회귀 테스트를 추가한다.
2. 한국어 `못 한`/`못한` 문맥을 generic execution claim에서 제외한다.
3. `test_validate_eval_run.py`를 실행한다.
4. `case-source-validation-coverage` run을 `validate_eval_run.py`로 재검증한다.

## 완료 조건

- expected evidence table의 `실행했거나 못 한 검증 보고`가 실행 완료 claim으로 오탐되지 않는다.
- `test_validate_eval_run.py`가 통과한다.
- `20260522-140700-source-try01-targeted-source-validation-coverage` validation이 통과한다.
