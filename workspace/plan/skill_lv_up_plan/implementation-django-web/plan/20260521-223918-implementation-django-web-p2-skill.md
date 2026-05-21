# implementation-django-web P2 skill 수정 계획

## 수정 이유

P2 평가에서 `implementation-django-web`의 핵심 범위인 Generic CBV/FBV 선택이 frontmatter와 OpenAI UI metadata에 충분히 드러나지 않았다. 또한 Reference Loading map과 static asset runtime rule 일부가 source reference의 범위와 강도보다 덜 명확하다.

## 수정 범위

- `dddjango/skills/implementation-django-web/SKILL.md`
  - frontmatter `description`
  - 목적 문단
  - Reference Loading map
  - static asset runtime rule
- `dddjango/skills/implementation-django-web/agents/openai.yaml`
  - `short_description`
  - `default_prompt`

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-django-web/reference/final.md`는 수정하지 않는다.
- Bundled references는 source 내용을 이미 충분히 담고 있으므로 이번 계획에서는 수정하지 않는다.
- 다른 skill, 다른 plan area, eval pack은 수정하지 않는다.
- `agents/openai.yaml`에 icon, brand color, dependency, policy 같은 optional interface field를 추가하지 않는다.

## 수정 순서

1. `SKILL.md` frontmatter와 목적 문단에 Generic CBV/FBV 및 대표 CBV trigger를 반영한다.
2. Reference Loading map에서 `templateview-htmx.md`가 auth/permission도 담고 있음을 명시한다.
3. Static asset runtime rule을 source reference와 맞게 강화한다.
4. `agents/openai.yaml` metadata를 같은 범위로 맞춘다.
5. Source skill 수정 후 runtime cache sync 분석/계획을 작성하고 cache를 동기화한다.
6. 재평가와 검증을 실행한다.

## 체크리스트

- [x] Frontmatter description이 사용 조건, trigger, 제외 조건을 포함한다.
- [x] 본문 routing에만 숨은 핵심 trigger가 남지 않는다.
- [x] `agents/openai.yaml`이 SKILL.md 범위와 어긋나지 않는다.
- [x] Optional interface field를 추가하지 않는다.
- [x] Source skill과 runtime cache가 일치한다.
- [x] 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0으로 닫는다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web`

## 완료 조건

- `SKILL.md` 목적, trigger, 제외 조건이 source reference와 일치한다.
- Frontmatter description과 본문 routing/rule이 충돌하지 않는다.
- `agents/openai.yaml` metadata가 `SKILL.md`와 일치하고 OpenAI YAML 기준을 위반하지 않는다.
- Runtime cache sync가 확인된다.
- 검증 결과와 리뷰 결과가 최종 보고에 남는다.

## 실행 결과

- Source skill 수정 완료.
- Runtime cache sync 완료.
- 재평가 결과: Blocker 0, Major 0, 열린 Minor 0.
- 검증:
  - `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: passed
  - `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: passed
  - `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: passed
  - `diff -qr dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web`: passed, no output
