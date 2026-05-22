수정 대상: evaluator

# prompt-input private material leakage 계획

## 수정 범위

- 수정: `workspace/scripts/validate_eval_run.py`
- 수정: `workspace/scripts/test_validate_eval_run.py`

## 절차

1. with-ddjango prompt-input artifact에 private eval sentinel이 들어가면 실패하는 테스트를 추가한다.
2. prompt-input artifact 전용 private material scan을 validator에 추가한다.
3. 기존 prompt-input JSON object/array 허용과 local path marker scan은 유지한다.
4. validator unit test와 필수 eval validators를 재실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- 관련 targeted eval 재검증

## 완료 조건

- prompt-input artifact에 validator-only private material marker가 있으면 run validation이 실패한다.
- 정상 message-array prompt-input artifact는 계속 통과한다.
