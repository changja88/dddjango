수정 대상: skill

# implementation-django P3 수정 계획

## 수정 이유

`implementation-django`는 concrete Django 구현을 맡고, pattern-level architecture decision과 web adapter/page work는 다른 skill로 넘겨야 한다. 현재 skill은 전반적으로 간결하지만 `architecture-implementation-patterns` handoff와 forms/views wording이 충분히 선명하지 않아 P3 책임 경계 기준에서 보강이 필요하다.

## 수정 범위

- `dddjango/skills/implementation-django/SKILL.md`
  - existing DRF maintenance/review trigger를 frontmatter description에 추가한다.
  - frontmatter description에 `architecture-implementation-patterns` handoff를 추가한다.
  - `Routing`에 repository/UoW/ports/outbox/ACL/service-layer pattern decision handoff를 추가한다.
  - risky write block을 already-decided implementation inputs 요약으로 한정하고, 미정 항목은 owning skill로 넘긴다.
  - `models-orm.md` reference 설명을 app layout, settings, models, fields, validation, managers, QuerySets, and ORM-adjacent form/view/signal boundary로 좁힌다.
- `dddjango/skills/implementation-django/references/models-orm.md`
  - 첫 문단의 forms/views wording을 ORM/service 인접 경계 판단으로 좁힌다.
  - web page composition, templates/static, HTMX, web forms 구현은 `implementation-django-web`로 넘긴다고 명시한다.
- `dddjango/skills/implementation-django/agents/openai.yaml`
  - existing DRF maintenance/review가 UI metadata와 default prompt에서도 발견되도록 보강한다.

## 수정하지 말아야 할 범위

- source reference `workspace/reference/implementation-django/reference/final.md`는 수정하지 않는다.
- 다른 skill의 routing이나 reference는 수정하지 않는다.
- unrelated dirty worktree 변경은 건드리지 않는다.
- 새 reference 파일을 추가하지 않는다.
- `implementation-django`에 세부 Django 규칙을 본문으로 되돌려 붙이지 않는다.

## 체크리스트

- [x] `SKILL.md`가 500줄 미만을 유지한다.
- [x] bundled reference가 `SKILL.md`에서 1단계 직접 링크로 유지된다.
- [x] existing DRF maintenance/review trigger가 metadata와 default prompt에 드러난다.
- [x] pattern-level decision은 `architecture-implementation-patterns`로 handoff된다.
- [x] risky write 미정 항목은 owning architecture/API/DB/pattern/test skill로 handoff된다.
- [x] web/template/static/form page 구현은 `implementation-django-web`로 handoff된다.
- [x] source skill과 runtime cache를 동기화한다.
- [x] subagent 또는 순차 fallback 리뷰 결과를 Blocker/Major/Minor로 통합한다.
- [x] required validation command를 실행한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/implementation-django /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django
```

## 완료 조건

- `implementation-django`의 직접 책임과 다른 skill handoff 기준이 `SKILL.md`와 bundled reference에서 충돌 없이 드러난다.
- `SKILL.md`는 핵심 절차와 routing 판단 중심이며 500줄 미만이다.
- 상세 Django 규칙은 직접 링크된 bundled reference에만 남는다.
- source skill과 runtime cache가 동일하다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- 검증 명령이 통과한다.
