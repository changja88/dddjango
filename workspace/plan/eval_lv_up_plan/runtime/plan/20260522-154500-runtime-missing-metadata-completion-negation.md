수정 대상: evaluator

# runtime missing-metadata completion negation 계획

## 수정 범위

- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_run.py`

## 절차

1. 실패 run의 raw output line을 기준으로 회귀 테스트를 추가한다.
2. 한국어 `완료라고 볼 수 없...` 문맥을 generic execution claim에서 제외한다.
3. `test_validate_eval_run.py`를 실행한다.
4. `case-runtime-missing-metadata` 실패 run을 `validate_eval_run.py`로 재검증한다.

## 완료 조건

- 회귀 테스트가 실패 원문과 같은 문장 구조를 포함한다.
- `test_validate_eval_run.py`가 통과한다.
- `20260522-154141-runtime-try01-targeted-p5-runtime-fixes`의 `case-runtime-missing-metadata` validation이 통과한다.
