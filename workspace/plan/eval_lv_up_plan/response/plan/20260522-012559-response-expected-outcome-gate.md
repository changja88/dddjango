수정 대상: evaluator

# architecture-ddd P4 expected outcome 검증 계획

## 수정 범위

- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_run.py`
- `workspace/develop/eval/response/answer/case-response-ddd-subscription-boundary.yaml`
- `workspace/develop/eval/code/answer/case-code-ddd-order-placement.yaml`

## 절차

1. run validator에 expected outcome과 oracle evaluation 비교 함수를 추가한다.
2. baseline pass 금지와 positive delta 미충족을 실패로 만드는 regression test를 추가한다.
3. baseline도 통과한 representative direct/smoke case는 expected outcome을 실제 성격에 맞게 정정한다.
4. 기존 targeted run을 다시 `validate_eval_run.py`로 검증한다.
5. 필수 validator와 test를 다시 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_run.py --bucket response --run-id 20260522-010823-response-try01-targeted-architecture-ddd-direct --case case-response-ddd-subscription-boundary`
- `.venv/bin/python -B workspace/scripts/validate_eval_run.py --bucket code --run-id 20260522-011120-code-try01-targeted-architecture-ddd-order-lifecycle --case case-code-ddd-order-placement`
- 필수 plan/skill/eval bucket validator 전체를 다시 실행한다.

## 완료 조건

- expected outcome과 실제 oracle evaluation 충돌이 validator에서 실패한다.
- 현재 architecture-ddd targeted runs가 정정된 expected outcome과 일치한다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0으로 닫힌다.

