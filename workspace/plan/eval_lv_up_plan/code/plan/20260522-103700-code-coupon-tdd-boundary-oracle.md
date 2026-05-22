수정 대상: answer

# coupon TDD code oracle boundary 계획

## 수정 범위

- `workspace/develop/eval/code/answer/case-code-coupon-tdd.yaml`

## 수정 순서

1. target behavior required에 최소 주문 금액의 accepted boundary와 nearest rejected/complement case를 명시한다.
2. 만료일 당일 accepted와 만료 다음 날 rejected를 별도 expected behavior로 명시한다.
3. Red-Green-Refactor 실행 정직성, policy outcome/state verification, broad DB/API architecture 금지를 coverage tag와 required/forbidden text에 보강한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- targeted eval:
  - `make eval-one BUCKET=code CASE=case-code-coupon-tdd TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-tdd-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- answer oracle이 boundary case를 source reference 수준으로 요구한다.
- public prompt에는 private answer 기준이 누설되지 않는다.
- targeted eval run id/status가 기록된다.

