수정 대상: runtime-sync

# workflow-dddjango-subagents P2 runtime-sync plan

## 수정 이유

Workspace canonical source skill을 P2 기준에 맞게 수정했으므로 runtime cache가 같은 내용을 가리키도록 동기화해야 한다.

## 수정 범위

- Runtime cache path:
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/SKILL.md`
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/agents/openai.yaml`
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/references/delegation-rules.md`
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/references/role-map.md`

## 수정하지 말아야 할 범위

- 다른 runtime cache skill은 수정하지 않는다.
- Workspace source가 아닌 임의 내용을 runtime cache에 직접 작성하지 않는다.
- Optional OpenAI metadata field를 추가하지 않는다.

## 체크리스트

- [ ] Workspace canonical source에서 runtime cache로 수정 파일을 복사한다.
- [ ] `diff -qr`로 source/cache parity를 확인한다.
- [ ] Validators를 실행해 plan constraints와 skill docs를 확인한다.
- [ ] Cache sync report에 cache path, workspace canonical source, validation status를 남긴다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/workflow-dddjango-subagents /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents`

## 완료 조건

- Runtime cache의 `SKILL.md`, `agents/openai.yaml`, bundled references가 workspace canonical source와 동일하다.
- 검증 명령이 통과한다.
- P2 최종 재평가에서 Blocker 0, Major 0, 열린 Minor 0 상태다.
