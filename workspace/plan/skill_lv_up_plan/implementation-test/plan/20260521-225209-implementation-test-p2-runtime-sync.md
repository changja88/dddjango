# implementation-test P2 Runtime Sync Plan

## 수정 이유

P2 source skill 수정으로 `dddjango/skills/implementation-test/`와 runtime cache가 달라졌다. runtime cache를 동기화해야 실제 runtime에서 P2 개선된 frontmatter와 UI metadata를 사용한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/agents/openai.yaml`

## 수정하지 말아야 할 범위

- Runtime cache의 다른 skill은 수정하지 않는다.
- Source reference, bundled references, eval pack은 runtime sync 단계에서 수정하지 않는다.
- Runtime cache에 source에 없는 분석/계획 문서를 넣지 않는다.

## 작업 체크리스트

- [x] source `SKILL.md`를 runtime cache에 반영한다.
- [x] source `agents/openai.yaml`을 runtime cache에 반영한다.
- [x] `diff -qr`로 source/runtime cache 일치를 확인한다.
- [x] required validators를 실행한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Source skill과 runtime cache의 `implementation-test` skill이 일치한다.
- Runtime cache에 P2 frontmatter와 metadata 수정이 반영된다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.

## 검증 결과

- `diff -qr dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`: 통과, 출력 없음
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과
