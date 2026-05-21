수정 대상: runtime-sync

## 수정 이유

P1 skill 수정으로 source skill과 runtime cache가 달라졌다. 종료 조건에는 source skill과 runtime cache 동기화 확인이 포함되므로 runtime cache를 source와 동일하게 갱신해야 한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/agents/openai.yaml`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/references/*.md`

## 수정하지 말아야 할 범위

- 다른 skill runtime cache는 수정하지 않는다.
- source skill과 다른 runtime-only 변경을 만들지 않는다.
- eval pack은 수정하지 않는다.

## 작업 체크리스트

- [x] source implementation-django skill directory를 runtime cache로 복사
- [x] `diff -qr`로 source/runtime parity 확인
- [x] required validators 실행

## 검증 명령

- `diff -qr dddjango/skills/implementation-django /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- source skill과 runtime cache의 `diff -qr` 출력이 없다.
- runtime-sync 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
