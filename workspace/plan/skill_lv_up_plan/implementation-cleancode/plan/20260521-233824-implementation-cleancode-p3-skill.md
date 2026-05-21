# implementation-cleancode P3 skill 수정 계획

## 수정 이유

`implementation-cleancode`는 앱 코드의 유지보수성 review/refactor가 직접 책임이다. P3 점검 결과 source/reference governance와 Django server-rendered web implementation handoff가 routing 표면에 빠져 있어 `source-reference-audit` 및 `implementation-django-web`과 경계가 흐려질 수 있다.

## 수정 범위

- `dddjango/skills/implementation-cleancode/SKILL.md`
  - frontmatter description의 handoff 목록에 `implementation-django-web`과 `source-reference-audit`를 추가한다.
  - `## Routing`에 source/reference governance, metadata, bundled reference, cache sync, leakage review 요청은 `source-reference-audit`로 넘긴다는 기준을 추가한다.
  - `## Routing`에 TemplateView/templates/static/HTMX/server-rendered web implementation primary work는 `implementation-django-web`로 넘긴다는 기준을 추가한다.
  - Python/Django implementation 관련 문장은 primary owner와 clean-code co-use 조건이 분리되도록 다듬는다.

## 수정하지 말아야 할 범위

- `workspace/reference/**`는 source gap이 발견될 때만 별도 reference 계획으로 다룬다.
- bundled references는 새로 만들거나 중복 내용을 늘리지 않는다.
- 다른 skill, eval pack, validator script는 수정하지 않는다.
- runtime cache는 source skill 수정 뒤 별도 `runtime-sync` 분석/계획을 남긴 후 동기화한다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter handoff 문장을 수정한다.
- [x] `SKILL.md` routing에 `source-reference-audit` handoff를 추가한다.
- [x] `SKILL.md` routing에 `implementation-django-web` handoff를 추가한다.
- [x] primary implementation owner와 clean-code advisory/co-use 기준을 명확히 한다.
- [x] subagent가 지적한 progressive disclosure 중복을 줄이기 위해 Runtime Rules의 세부 기준을 bundled reference로 되돌린다.
- [x] source 수정 후 `diff -qr`로 runtime cache drift를 확인한다.
- [x] drift가 있으면 별도 runtime-sync 분석/계획을 작성하고 cache를 동기화한다.
- [x] 검증 명령과 subagent 리뷰 결과를 통합해 Blocker 0, Major 0, 열린 Minor 0인지 재평가한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-cleancode /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode`

## 완료 조건

- 직접 책임과 handoff 기준이 architecture, implementation, test, source audit, workflow 역할과 충돌하지 않는다.
- `SKILL.md`는 500줄 미만이고 핵심 routing/procedure만 담는다.
- bundled references는 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- source skill과 runtime cache 동기화가 확인된다.
- 검증 명령이 통과하고 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
