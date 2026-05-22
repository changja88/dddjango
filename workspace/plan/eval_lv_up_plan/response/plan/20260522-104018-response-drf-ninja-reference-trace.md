수정 대상: answer

# DRF-to-Ninja answer reference trace 보강 계획

## 목표

`case-response-drf-ninja` answer oracle이 DRF auth/filtering/sorting/pagination compatibility 요구의 bundled source basis를 직접 추적하게 한다.

## 작업

1. `case-response-drf-ninja.yaml`의 `reference_basis`에 `auth-pagination-filtering.md`를 추가한다.
2. response bucket validator와 관련 테스트를 다시 실행한다.
3. targeted eval pass evidence는 여전히 별도 필요하므로 완료 조건으로 오판하지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`

## 완료 기준

- answer oracle의 bundled reference trace가 required behavior와 일치한다.
- 로컬 validator가 통과한다.
- targeted eval pass run이 없으면 P4 자체는 complete가 아니다.
