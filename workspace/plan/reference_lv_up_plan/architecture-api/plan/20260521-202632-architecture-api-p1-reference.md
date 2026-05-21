# Architecture API P1 Reference Plan

## 수정 이유

`workspace/reference/architecture-api/reference/final.md`는 P1 주요 영역을 포함하지만 `Idempotency-Key`, request/response contract, OpenAPI 계약 표면의 판단 기준이 runtime reference보다 약하다. source reference가 runtime guidance의 기준 근거가 되도록 세부 결정을 보강한다.

## 수정 범위

- `workspace/reference/architecture-api/reference/final.md`
- 추가 또는 보강할 내용:
  - request/response 계약 산출물 체크 기준
  - 상태 코드와 response body/header 조합 기준
  - `Idempotency-Key` key scope, same-key different-content conflict, original-result replay, retention, concurrency handoff
  - OpenAPI path/method/request/response/error/auth/pagination/rate-limit/idempotency/versioning 반영 표면
  - PATCH method의 idempotency nuance

## 수정하지 말아야 할 범위

- `workspace/develop/eval/**`는 수정하지 않는다.
- runtime skill은 reference 보강 후 별도 skill 분석/계획에 따라 수정한다.
- architecture-api 범위 밖 프로토콜이나 API gateway 운영 정책은 추가하지 않는다.

## 작업 체크리스트

- [x] `final.md`의 목차에 request/response contract 항목을 추가한다.
- [x] 상태 코드 섹션 뒤에 request/response contract 체크 기준을 추가한다.
- [x] `Idempotency-Key` 섹션을 replay/conflict/scope 중심으로 보강한다.
- [x] OpenAPI 섹션을 계약 변경 표면 중심으로 보강한다.
- [x] PATCH 설명에 patch document가 멱등하게 설계될 수 있음을 추가한다.
- [x] reference 보강 후 skill 반영 부족 여부를 재평가한다.

## 완료 결과

- Reference 관련 Blocker 0, Major 0, 열린 Minor 0으로 재평가했다.
- 검증 명령은 모두 통과했다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- P1 reference 평가 항목을 `final.md`만으로 판단할 수 있다.
- runtime bundled reference가 source reference보다 강한 unsupported claim을 하지 않는다.
- 리뷰 결과에서 reference 관련 Blocker 0, Major 0, 열린 Minor 0이다.
