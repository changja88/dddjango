수정 대상: skill

## 수정 이유

source reference가 보강된 뒤 runtime-facing skill surface가 같은 범위와 경계를 보여야 한다. 특히 UI metadata가 skill scope를 좁게 표현하면 사용자가 settings, caching, security, performance, Django acceptance criteria 작업에 skill을 떠올리지 못할 수 있다. 또한 기존 DRF 유지보수 boundary는 greenfield DRF 금지와 함께 명시해야 routing 오해를 줄일 수 있다.

## 수정 범위

- `dddjango/skills/implementation-django/SKILL.md`
  - 기존 DRF 코드 유지보수에서 adapter와 durable rule boundary를 구분하는 runtime rule을 추가한다.
  - Django coding style과 기존 DRF 유지보수 reference loading 경로를 추가한다.
- `dddjango/skills/implementation-django/agents/openai.yaml`
  - `short_description`과 `default_prompt`를 source/skill 범위와 맞춘다.
- `dddjango/skills/implementation-django/references/*.md`
  - source basis를 짧게 표시한다.
  - Django coding style과 기존 DRF 유지보수 exception을 bundled reference로 제공한다.

## 수정하지 말아야 할 범위

- bundled reference를 불필요하게 장문화하지 않는다. source 전체를 복제하지 않고 runtime 판단에 필요한 condensed guidance만 둔다.
- DRF Serializer/ViewSet/DefaultRouter를 greenfield 표준처럼 되돌리지 않는다.
- API contract 설계나 Django Ninja endpoint 구현 guidance를 이 skill로 흡수하지 않는다.
- runtime cache는 source skill 수정 후 별도 runtime-sync analysis/plan을 남기고 동기화한다.

## 작업 체크리스트

- [x] `SKILL.md` runtime rule에 기존 DRF adapter boundary 추가
- [x] Django coding style과 existing DRF maintenance bundled reference 추가
- [x] bundled reference source basis 표시
- [x] `agents/openai.yaml` metadata scope 보정
- [x] source skill과 runtime cache 차이 확인
- [x] runtime-sync 필요 시 별도 analysis/plan 후 cache sync
- [x] validator 실행

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `SKILL.md`, bundled references, `agents/openai.yaml`이 source reference와 충돌하지 않는다.
- greenfield API routing은 `architecture-api`/`implementation-django-ninja`로 남고, 기존 DRF 유지보수는 adapter boundary로 제한된다.
- skill reflection에 대한 Blocker 0, Major 0, 열린 Minor 0 상태를 재평가로 확인한다.
