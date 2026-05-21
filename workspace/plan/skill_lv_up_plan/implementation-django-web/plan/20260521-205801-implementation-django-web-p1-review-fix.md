# implementation-django-web P1 review 보완 계획

## 수정 이유

Real-subagent skill-creator 리뷰에서 runtime wording, auth/permission bundled reference, agents metadata alignment 문제가 발견됐다. Blocker는 없지만 Major와 열린 Minor가 있으므로 P1 종료 전에 같은 루프에서 보완한다.

## 수정 범위

- 수정: `dddjango/skills/implementation-django-web/SKILL.md`
- 수정: `dddjango/skills/implementation-django-web/references/templateview-htmx.md`
- 수정: `dddjango/skills/implementation-django-web/agents/openai.yaml`
- 동기화: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/`

## 수정하지 말아야 할 범위

- Source reference를 review finding에 맞춰 불필요하게 바꾸지 않는다.
- Validator exact phrase를 만족하기 위해 source보다 더 좁은 업무 예시를 runtime rule에 넣지 않는다.
- Eval case, answer, evaluator는 수정하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md`에서 hardcoded placeholder 예시와 특정 optional field list를 제거한다.
- [x] `templateview-htmx.md`에 unauthorized/forbidden/redirect behavior가 project standard와 test expectation을 따라야 한다는 기준을 추가한다.
- [x] `agents/openai.yaml`에 web forms와 view auth/permissions를 포함한다.
- [x] Runtime cache를 source skill과 동기화한다.
- [x] `diff -qr`와 required validators를 실행한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Real-subagent 리뷰의 Major와 Minor가 source skill 수정으로 닫힌다.
- Runtime cache와 source skill의 diff가 없다.
- Required validators가 통과한다.
- 최종 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
