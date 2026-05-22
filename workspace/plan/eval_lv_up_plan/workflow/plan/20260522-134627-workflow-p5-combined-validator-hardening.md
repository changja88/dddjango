수정 대상: evaluator

# workflow P5 combined validator hardening 계획

## 수정 범위

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`
- `workspace/develop/eval/workflow/answer/case-workflow-risky-write.yaml`

## 순서

1. Combined P5 helper가 필수 용어를 `target_behavior.required`에서만 찾도록 바꾼다.
2. Role decomposition과 handoff field required groups를 추가한다.
3. 지정된 P5 combined case id를 case-level로 요구한다.
4. Positive/negative 단위 테스트를 새 기준에 맞게 보강한다.
5. Risky-write와 positive-composite answer oracle에 full handoff field set을 명시한다.
6. workflow bucket validator와 관련 unit test를 실행한다.

## 완료 조건

- Forbidden text만으로 combined P5 coverage가 통과하지 않는다.
- Role names와 handoff fields가 required text에 있어야 combined P5 coverage로 인정된다.
- `case-workflow-risky-write`와 `case-workflow-positive-composite`가 각각 P5 combined shape를 유지해야 한다.
- 독립 review Major 2, Minor 1이 닫힌다.
