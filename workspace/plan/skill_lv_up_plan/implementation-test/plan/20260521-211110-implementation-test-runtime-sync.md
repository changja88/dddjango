# implementation-test P1 Runtime Sync Plan

## 수정 이유

P1 skill 보강 후 source skill과 runtime cache가 달라졌다. runtime cache가 이전 상태로 남으면 실제 Codex runtime에서 업데이트된 bundled reference와 routing metadata를 사용할 수 없다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/agents/openai.yaml`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/references/django-api-concurrency.md`

## 수정하지 말아야 할 범위

- 다른 runtime cache skill은 수정하지 않는다.
- Source reference나 eval pack은 runtime sync 단계에서 수정하지 않는다.
- runtime cache에 source에 없는 분석/계획 문서를 넣지 않는다.

## 작업 체크리스트

- [x] source skill의 `SKILL.md`를 runtime cache에 반영한다.
- [x] source skill의 `agents/openai.yaml`을 runtime cache에 반영한다.
- [x] 새 bundled reference를 runtime cache에 추가한다.
- [x] `diff -ru dddjango/skills/implementation-test <runtime-cache>`로 동기화 여부를 확인한다.
- [x] validator를 실행한다.

## 검증 명령

- `diff -ru dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Source skill과 runtime cache의 `implementation-test` skill이 일치한다.
- Runtime cache에 P1 보강된 reference loading, metadata, bundled reference가 존재한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
