# implementation-django-ninja P1 reference 개선 계획

대상: implementation-django-ninja
생성 시각: 2026-05-21 20:48:29 KST
분석 문서: `workspace/plan/reference_lv_up_plan/implementation-django-ninja/analysis/20260521-204829-implementation-django-ninja-p1-reference.md`

## 수정 이유

`workspace/reference/implementation-django-ninja/reference/final.md`가 없어
`implementation-django-ninja` skill이 전용 source reference 없이 provisional runtime
guidance에 의존한다. P1 종료 조건인 source reference 충분성을 만족하려면 전용 final
reference를 생성해야 한다.

## 수정 범위

- 생성: `workspace/reference/implementation-django-ninja/reference/final.md`
- 포함 기준: Router, Schema/ModelSchema, endpoint operation, auth/permission,
  filtering/sorting, pagination, Problem Details, OpenAPI, TestClient,
  DRF-to-Ninja migration, 관련 skill 라우팅

## 수정하지 말아야 할 범위

- eval case, answer oracle, evaluator, report는 수정하지 않는다.
- DRF를 greenfield 표준으로 되돌리지 않는다.
- Django service/ORM/transaction 세부 구현은 `implementation-django` reference에 위임한다.
- pytest fixture/mock/factory mechanics는 `implementation-test` reference에 위임한다.

## 작업 체크리스트

- [x] reference area 디렉터리를 생성한다.
- [x] Django Ninja 공식 문서와 기존 dddjango reference 경계를 확인한다.
- [x] final source reference를 작성한다.
- [x] source skill이 새 reference를 반영하도록 별도 skill 계획으로 수정한다.
- [x] runtime cache 동기화가 필요한지 별도 runtime-sync 계획으로 확인한다.
- [x] 독립 리뷰 결과를 통합해 열린 Blocker/Major/Minor를 닫는다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `workspace/reference/implementation-django-ninja/reference/final.md`가 존재한다.
- P1 요구 항목을 판단할 수 있는 source 기준이 있다.
- source reference 문제를 skill 수정으로 덮지 않았다.
- review 결과에서 reference 관련 Blocker 0, Major 0, 열린 Minor 0이다.

완료 상태: 충족.
