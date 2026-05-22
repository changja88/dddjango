수정 대상: case

# coupon TDD pytest claim 계획

## 수정 범위

- `workspace/develop/eval/code/cases/plugin/public/case-code-coupon-tdd.md`

## 수정 순서

1. public case의 검증 요청을 `unittest`로 좁힌다.
2. pytest를 실제 실행하지 않았으면 pytest 결과를 보고하지 말라는 validation honesty 문장을 추가한다.
3. code bucket validator를 실행한다.
4. targeted eval을 재실행해 unsupported pytest claim이 사라지고 RUN_VALIDATION pass가 남는지 확인한다.

## 완료 조건

- public case가 TDD/code 검증 목적과 같은 unittest artifact를 유도한다.
- pytest 미실행 결과 claim이 발생하지 않는다.
- `case-code-coupon-tdd` targeted eval이 pass run을 남긴다.

