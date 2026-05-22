수정 대상: case

# coupon expiration boundary public case 계획

## 수정 범위

- `workspace/develop/eval/code/cases/plugin/public/case-code-coupon-tdd.md`

## 수정 순서

1. 요구사항의 만료일 항목을 "만료일 당일과 다음 날"로 좁힌다.
2. answer oracle은 이미 해당 기준을 요구하므로 유지한다.
3. code bucket validator를 실행한다.
4. targeted eval을 재실행해 with-ddjango verdict pass와 RUN_VALIDATION pass를 확인한다.

## 완료 조건

- public case, answer oracle, evaluator가 같은 expiration boundary 목적을 검증한다.
- targeted eval pass run이 남는다.

