수정 대상: answer

# workflow P5 answer basis 계획

## 수정 범위

- `workspace/develop/eval/workflow/answer/case-workflow-parallel-ownership.yaml`
- `workspace/develop/eval/workflow/answer/case-workflow-positive-composite.yaml`

## 순서

1. `case-workflow-parallel-ownership`의 scoring check와 expected outcome을 runtime 제한이 있는 actual-subagent 평가에 맞춘다.
2. `case-workflow-positive-composite`의 reference basis에 `delegation-rules.md`, `handoff-contract.md`, `integration-checklist.md`를 추가한다.
3. `case-workflow-positive-composite`의 coverage tags에 P5 integration 축을 추가한다.
4. workflow bucket validator를 실행한다.
5. 수정한 두 case를 targeted eval로 재실행하고 `validate_eval_run.py` 결과를 확인한다.

## 완료 조건

- answer oracle이 public case보다 과도한 구조를 강제하지 않는다.
- runtime 제한은 `pass-limited`로 표현 가능하고, actual subagent를 거짓으로 요구하지 않는다.
- positive composite case가 role-map뿐 아니라 handoff, delegation, integration checklist owning references를 직접 근거로 든다.
- Targeted eval pass run 또는 pass-limited 허용 run이 현재 파일 기준으로 남는다.
