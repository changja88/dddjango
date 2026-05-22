수정 대상: evaluator

# response protocol prompt-input 검증 계획

## 수정 범위

- 수정: `workspace/scripts/validate_eval_protocol.py`
- 수정: `workspace/scripts/test_validate_eval_protocol.py`

## 절차

1. prompt-input artifact가 top-level message array일 수 있음을 테스트로 고정한다.
2. prompt-input 전용 validator만 object 또는 array를 허용한다.
3. 기존 answer oracle, run metadata 등 object schema가 필요한 artifact 검증은 변경하지 않는다.
4. protocol unit test와 필수 검증을 재실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_protocol.py`
- 필수 공통 validator 재실행

## 완료 조건

- `validate_eval_protocol.py`가 prompt-input object/array 둘 다 허용한다.
- object-only artifact 검증은 유지된다.
