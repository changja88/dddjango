# implementation-django-ninja P1 skill 개선 계획

대상: implementation-django-ninja
생성 시각: 2026-05-21 20:48:29 KST
분석 문서: `workspace/plan/skill_lv_up_plan/implementation-django-ninja/analysis/20260521-204829-implementation-django-ninja-p1-skill.md`

## 수정 이유

전용 source reference를 생성하면 source skill의 provisional/fallback 설명과
`agents/openai.yaml` metadata가 더 이상 정확하지 않다. Skill은 새 source reference의
결정을 충분히 반영하되, runtime context를 과하게 늘리지 않도록 bundled references에
세부 기준을 분산해야 한다.

## 수정 범위

- `dddjango/skills/implementation-django-ninja/SKILL.md`
- `dddjango/skills/implementation-django-ninja/agents/openai.yaml`
- `dddjango/skills/implementation-django-ninja/references/router-schema.md`
- `dddjango/skills/implementation-django-ninja/references/auth-pagination-filtering.md`
- `dddjango/skills/implementation-django-ninja/references/problem-details-openapi.md`
- `dddjango/skills/implementation-django-ninja/references/testclient.md`

## 수정하지 말아야 할 범위

- eval case, answer oracle, evaluator, generated run artifact는 수정하지 않는다.
- 다른 skill의 source/reference/runtime guidance는 수정하지 않는다.
- Django Ninja syntax를 프로젝트 설치 버전으로 검증하지 않고 실행 완료로 주장하지 않는다.
- SKILL.md에 source reference 전체를 복붙하지 않는다.

## 작업 체크리스트

- [x] source reference gap을 먼저 닫는다.
- [x] SKILL.md의 provisional/fallback 설명을 dedicated source 기준으로 바꾼다.
- [x] Reference Loading과 Runtime Rules가 새 source reference의 판단 축을 반영하게 한다.
- [x] bundled references의 stale provisional 표현을 제거하고 coverage를 보강한다.
- [x] `agents/openai.yaml`을 source skill 목적과 맞춘다.
- [x] 독립 리뷰 결과를 통합하고 열린 findings를 닫는다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- SKILL.md가 dedicated source reference 기반 skill로 읽힌다.
- bundled references가 Router, Schema, endpoint, auth/permission, pagination,
  filtering/sorting, Problem Details, OpenAPI, TestClient, DRF-to-Ninja migration을
  빠짐없이 안내한다.
- `agents/openai.yaml`이 SKILL.md 목적과 충돌하지 않는다.
- review 결과에서 skill 관련 Blocker 0, Major 0, 열린 Minor 0이다.

완료 상태: 충족.
