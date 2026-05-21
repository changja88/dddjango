# Implementation Django Ninja P2 Skill Plan

## 수정 이유

P2 평가에서 `implementation-django-ninja` skill의 전반적 목적과 source reference 반영은 적절하지만, 일부 routing 조건이 본문에만 더 명시적으로 남아 있고 `agents/openai.yaml`의 `short_description`이 OpenAI YAML 기준의 25-64자 범위를 만족하지 않는 문제가 확인됐다.

## 수정 범위

- `dddjango/skills/implementation-django-ninja/SKILL.md`
- `dddjango/skills/implementation-django-ninja/agents/openai.yaml`
- Source 수정 후 runtime cache 동기화: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja/`

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-django-ninja/**`는 수정하지 않는다.
- `dddjango/skills/implementation-django-ninja/references/*.md`는 새 source alignment finding 없이는 수정하지 않는다.
- 다른 skill과 runtime cache는 수정하지 않는다.
- `workspace/develop/eval/**`는 수정하지 않는다.
- `agents/openai.yaml`에 optional interface field를 새로 추가하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter에 작은 Router 수정, 짧은 Django Ninja 구현 질문, `architecture-ddd` handoff, `서브에이전트` trigger를 반영한다.
- [x] `SKILL.md` 본문 routing의 subagent trigger 표현을 frontmatter와 맞춘다.
- [x] `agents/openai.yaml`의 `short_description`을 25-64자 범위로 수정한다.
- [x] `agents/openai.yaml`의 `default_prompt`가 `$implementation-django-ninja`와 Router/Schema adapter, TestClient 기준, DRF-to-Ninja migration을 반영하게 한다.
- [x] Source skill 수정 후 runtime cache를 동일 내용으로 동기화한다.
- [x] 동일 P2 기준으로 재평가해 Blocker 0, Major 0, 열린 Minor 0인지 확인한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-django-ninja /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja`

## 완료 조건

- `SKILL.md` 목적, trigger, 제외 조건이 frontmatter와 본문에서 충돌 없이 드러난다.
- 본문에만 숨은 P2 routing trigger가 없다.
- `agents/openai.yaml`이 OpenAI YAML field 기준과 `SKILL.md` 범위를 함께 만족한다.
- Source skill과 runtime cache가 `diff -qr` 기준 동일하다.
- 검증 명령이 통과한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

## 완료 결과

- P2 source skill 수정과 runtime cache sync를 완료했다.
- Required validator와 source/runtime diff를 통과했다.
- 최종 리뷰 결과는 Blocker 0, Major 0, 열린 Minor 0이다.
