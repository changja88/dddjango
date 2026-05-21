수정 대상: skill

## 수정 이유

P2 기준에서는 `agents/openai.yaml` metadata가 `SKILL.md`와 의미상 일치할 뿐 아니라 OpenAI metadata field 제약도 따라야 한다. 현재 `short_description`은 skill 범위를 과도하게 길게 나열해 quick-scan blurb 길이 제약을 넘으므로, 범위 의미를 유지하면서 25-64자 안으로 줄인다. 또한 본문 routing에 있는 explicit subagent/역할 분해/병렬 검토 trigger가 frontmatter에 충분히 노출되지 않아 body-only trigger가 되므로 description에 반영한다.

## 수정 범위

- `dddjango/skills/implementation-django/SKILL.md`
  - frontmatter `description`의 workflow routing trigger를 본문과 맞춘다.
- `dddjango/skills/implementation-django/agents/openai.yaml`
  - `interface.short_description`을 짧고 넓게 조정한다.

## 수정하지 말아야 할 범위

- `SKILL.md` 본문 routing, runtime rules, reference loading 구조는 현재 P2 기준을 만족하므로 수정하지 않는다.
- optional interface fields(`icon_small`, `icon_large`, `brand_color`, dependencies, policy 등)는 추가하지 않는다.
- source reference는 P2에서 억지로 바꾸지 않는다.
- runtime cache는 source skill 수정 후 별도 runtime-sync analysis/plan을 남기고 동기화한다.

## 작업 체크리스트

- [x] frontmatter `description`에 body-only workflow trigger 반영
- [x] `short_description`을 25-64자 범위로 축약
- [x] `display_name`, `default_prompt`가 `SKILL.md`와 계속 일치하는지 재확인
- [x] optional interface field가 추가되지 않았는지 확인
- [x] source skill과 runtime cache 차이 확인
- [x] runtime-sync 필요 시 별도 analysis/plan 후 cache sync
- [x] real-subagent 리뷰 결과 통합

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-django /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django`

## 완료 조건

- `agents/openai.yaml` metadata가 `SKILL.md` 목적과 충돌하지 않는다.
- `SKILL.md` frontmatter와 본문 routing 사이에 body-only trigger가 남지 않는다.
- `short_description`이 OpenAI metadata quick-scan 제약을 만족한다.
- optional interface field가 추가되지 않았다.
- source skill과 runtime cache 동기화가 확인된다.
- P2 재평가 결과 Blocker 0, Major 0, 열린 Minor 0이다.
