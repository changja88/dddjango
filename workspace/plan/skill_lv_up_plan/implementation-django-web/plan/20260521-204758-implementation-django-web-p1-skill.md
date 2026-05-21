# implementation-django-web P1 skill 개선 계획

## 수정 이유

Dedicated Django Web source reference가 생성됐으므로 source skill과 bundled references가 더 이상 provisional/fallback 상태를 안내하면 안 된다. Skill은 source reference의 책임 범위, routing, TemplateView/templates/static/HTMX/CSRF/forms/auth/render acceptance 기준을 runtime에서 찾기 쉽게 반영해야 한다.

## 수정 범위

- 수정: `dddjango/skills/implementation-django-web/SKILL.md`
- 수정: `dddjango/skills/implementation-django-web/references/templates.md`
- 수정: `dddjango/skills/implementation-django-web/references/templateview-htmx.md`
- 수정: `dddjango/skills/implementation-django-web/references/static-assets.md`
- 수정: `dddjango/skills/implementation-django-web/references/csrf-ajax.md`
- 수정: `dddjango/skills/implementation-django-web/agents/openai.yaml`

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-django-web/reference/final.md`는 skill gap을 덮기 위해 불필요하게 바꾸지 않는다.
- runtime cache는 source skill 수정 후 별도 `runtime-sync` 분석/계획을 거쳐 동기화한다.
- eval pack은 P1에서 임의로 고치지 않는다.
- Django Ninja/API, ORM/DB, 테스트 도구 상세는 해당 skill로 handoff하는 기준만 둔다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter에서 provisional/fallback 문구를 제거한다.
- [x] routing 기준을 Django Web 책임과 owning skill handoff 중심으로 정리한다.
- [x] reference loading이 skill-local bundled references를 정확히 안내하게 한다.
- [x] runtime rules에 template presentation-only, thin view, explicit ModelForm fields, HTMX/AJAX CSRF, optional display value, static asset wiring, verification honesty를 포함한다.
- [x] bundled references 네 파일을 한글로 갱신하고 dedicated source 기준의 세부 판단을 반영한다.
- [x] `agents/openai.yaml`의 short description/default prompt에서 provisional 문구를 제거한다.
- [x] 수정 후 skill 반영도를 재평가하고 analysis 문서를 갱신한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- SKILL.md, bundled references, agents metadata가 source reference와 충돌하지 않는다.
- SKILL.md는 concise하고 references를 필요할 때만 읽도록 안내한다.
- skill-creator 관점 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
