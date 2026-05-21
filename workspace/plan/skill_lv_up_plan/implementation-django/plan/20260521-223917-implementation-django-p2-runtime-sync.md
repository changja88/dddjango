수정 대상: runtime-sync

## 수정 이유

P2 metadata/frontmatter 수정 후 source skill과 runtime cache가 달라졌다. 실제 Codex runtime이 같은 skill 내용을 사용하도록 runtime cache의 implementation-django skill directory를 source와 동기화해야 한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/agents/openai.yaml`

## 수정하지 말아야 할 범위

- 다른 skill runtime cache는 수정하지 않는다.
- source skill과 다른 runtime-only 변경을 만들지 않는다.
- runtime cache에 analysis/plan 문서를 넣지 않는다.

## 작업 체크리스트

- [x] source `implementation-django` skill 변경 파일을 runtime cache로 복사
- [x] `diff -qr`로 source/runtime parity 확인
- [x] P2 skill analysis/plan 재평가에 sync 결과 반영

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-django /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django`

## 완료 조건

- source skill과 runtime cache의 `diff -qr` 출력이 없다.
- runtime-sync 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
