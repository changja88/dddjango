# implementation-test P1 Reference Plan

## 수정 이유

`implementation-test` P1 기준은 Django Ninja `TestClient`와 idempotency/concurrency tests까지 source reference가 판단 가능해야 한다. 현재 `workspace/reference/implementation-test/reference/final.md`는 일반 pytest/test-quality 기준은 충분하지만 이 두 축이 빠져 있어 reference gap이 남는다.

## 수정 범위

- 수정 대상: `workspace/reference/implementation-test/reference/final.md`
- 추가 내용:
  - Django Ninja `TestClient` API 계약 테스트 기준
  - pytest-django DB 접근/transaction 테스트 선택 기준
  - idempotency/replay와 concurrency/row-lock 테스트 기준
  - 참고 문헌과 설치 도구 목록 보강

## 수정하지 말아야 할 범위

- `workspace/develop/eval/**` 평가 case, answer, evaluator는 수정하지 않는다.
- `dddjango/skills/implementation-test/**`는 reference gap이 닫힌 뒤 별도 skill 분석/계획을 작성하고 수정한다.
- 다른 skill/reference area는 수정하지 않는다.
- 기존 일반 pytest, Mock, factory, coverage, mutation 본문을 대규모 재작성하지 않는다.

## 작업 체크리스트

- [x] `final.md` 목차에 Django API/동시성 테스트 섹션을 추가한다.
- [x] Django Ninja `TestClient` 사용 기준과 예제를 추가한다.
- [x] pytest-django transaction/database 테스트 선택 기준을 추가한다.
- [x] idempotency replay, duplicate request, concurrency race 검증 예제를 추가한다.
- [x] 참고 문헌과 설치 도구 목록을 보강한다.
- [x] reference 보강 후 skill 반영도를 재평가한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Reference가 P1의 모든 테스트 구현 기준을 판단할 수 있다.
- Reference gap을 skill 문서만으로 덮지 않는다.
- 이후 skill 분석에서 Django Ninja `TestClient`, idempotency/concurrency guidance 반영 여부를 평가할 수 있다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0으로 닫힌다.
