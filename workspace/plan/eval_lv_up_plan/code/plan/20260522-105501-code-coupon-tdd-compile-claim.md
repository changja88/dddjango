수정 대상: answer

# coupon TDD compile claim 계획

## 수정 범위

- `workspace/develop/eval/code/answer/case-code-coupon-tdd.yaml`

## 수정 순서

1. deterministic check에 `python3 -m compileall -q apps tests`를 추가한다.
2. unit test check는 그대로 둔다.
3. code bucket validator를 다시 실행한다.
4. targeted eval을 같은 case/topic으로 재실행해 RUN_VALIDATION pass를 확인한다.

## 완료 조건

- compileall 실행 주장이 raw output에 있어도 matching command artifact가 존재한다.
- `case-code-coupon-tdd` targeted eval이 pass run을 남긴다.

