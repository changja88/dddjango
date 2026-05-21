# implementation-django-web P3 수정 계획

## 수정 이유

P3 기준상 `implementation-django-web`의 직접 책임과 handoff는 대체로 명확하지만, `SKILL.md` Runtime Rules에 bundled reference와 중복되는 세부 규칙이 남아 있고, render/browser acceptance와 detailed test mechanics의 handoff 문구가 더 명확해야 한다.

## 수정 범위

- 수정 대상: `dddjango/skills/implementation-django-web/SKILL.md`
- 수정 성격:
  - Runtime Rules를 핵심 절차와 routing 판단 중심으로 압축한다.
  - 세부 규칙은 기존 bundled references로 위임한다.
  - web render/browser acceptance 기준과 detailed pytest/browser automation mechanics의 책임을 분리해 표현한다.

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-django-web/reference/final.md`는 충분하므로 수정하지 않는다.
- 인접 skill인 `implementation-test`는 이번 target-scope 밖이므로 수정하지 않는다.
- bundled reference의 세부 규칙은 현재 충분하고 1단계로 발견 가능하므로 불필요하게 재작성하지 않는다.
- `agents/openai.yaml`은 semantic drift가 없으면 수정하지 않는다.

## 체크리스트

- [x] `SKILL.md`에서 duplicated detailed acceptance rule을 reference loading으로 넘긴다.
- [x] `SKILL.md`에서 web implementation acceptance와 detailed test mechanics handoff를 분명히 한다.
- [x] `SKILL.md`가 500줄 미만인지 확인한다.
- [x] source skill과 runtime cache 차이를 확인한다.
- [x] runtime cache가 달라졌으면 runtime-sync 분석/계획을 작성하고 동기화한다.
- [x] subagent 리뷰 결과를 재평가해 Blocker 0, Major 0, 열린 Minor 0으로 닫는다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web
```

## 완료 조건

- 직접 책임과 handoff 기준이 명확하다.
- 다른 skill과 책임 충돌이 없다.
- `SKILL.md`는 핵심 절차 중심이고 bundled reference는 1단계 링크로 발견 가능하다.
- 중복된 상세 규칙이 줄어든다.
- source skill과 runtime cache 동기화가 확인된다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
