# workflow-dddjango-subagents P3 runtime-sync 계획

## 수정 이유

P3 source skill 수정 뒤 runtime cache의 `SKILL.md`, `references/role-map.md`, `references/integration-checklist.md`가 source와 달라졌다. Codex plugin runtime은 cache의 skill bundle을 사용하므로 runtime cache를 workspace canonical source와 동기화해야 한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/references/role-map.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/references/integration-checklist.md`

## 수정하지 말아야 할 범위

- Runtime cache의 다른 skill은 수정하지 않는다.
- Workspace source skill 밖의 source/reference/eval 파일은 runtime-sync 대상으로 삼지 않는다.
- `agents/openai.yaml`, `references/delegation-rules.md`, `references/handoff-contract.md`는 source와 이미 같으면 복사하지 않는다.

## 체크리스트

- [x] Source 수정 파일을 runtime cache에 복사한다.
- [x] `diff -qr`로 source/cache parity를 확인한다.
- [x] `validate_skill_docs.py --phase all`로 runtime/source parity validation을 확인한다.
- [x] Runtime-sync 분석 문서에 동기화 후 재평가를 남긴다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/workflow-dddjango-subagents /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents`

## 완료 조건

- Source skill과 runtime cache가 같은 내용을 가진다.
- Role-map parity와 source-audit handoff 보강이 runtime cache에도 반영된다.
- Runtime sync 관련 Blocker 0, Major 0, 열린 Minor 0이다.
