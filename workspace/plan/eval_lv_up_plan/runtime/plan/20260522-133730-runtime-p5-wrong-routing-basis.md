수정 대상: answer

# P5 runtime wrong-routing basis 수정 계획

## 수정 범위

- `workspace/develop/eval/runtime/answer/case-runtime-wrong-routing.yaml`

## 순서

1. `reference_basis`에 `implementation-django-web` skill metadata와 template/static references를 추가한다.
2. target behavior에 role-map, runtime skill description, web skill metadata 비교를 모두 요구한다.
3. runtime bucket validator를 실행한다.
4. 수정 case targeted eval을 실행하고 pass run에 `validate_eval_run.py`를 실행한다.

## 완료 조건

- wrong-routing 평가가 metadata 존재만이 아니라 web skill responsibility와 role-map parity를 함께 검증한다.
