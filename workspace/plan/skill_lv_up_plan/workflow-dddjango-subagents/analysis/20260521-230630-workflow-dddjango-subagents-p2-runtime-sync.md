수정 대상: runtime-sync

# workflow-dddjango-subagents P2 runtime-sync analysis

## 범위

- Workspace canonical source: `dddjango/skills/workflow-dddjango-subagents/`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/`

## 원인

P2 skill 수정으로 workspace canonical source의 다음 파일이 변경됐다.

- `SKILL.md`
- `agents/openai.yaml`
- `references/delegation-rules.md`
- `references/role-map.md`

Runtime cache는 workspace source와 같은 내용을 가리켜야 하므로, cache sync 없이는 P2 종료 조건의 source/runtime parity를 증명할 수 없다.

## 동기화 대상

Workspace canonical source에서 runtime cache로 다음 파일을 복사한다.

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`
- `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
- `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`
- 변경되지 않은 bundled reference도 최종 `diff -qr`로 parity를 확인한다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: P2 read-only subagent 리뷰에서 cache sync risk를 확인했고, 수정 전 `diff`는 동일했다. 수정 후 workspace source가 바뀌었으므로 runtime-sync가 필요하다.

skill-creator 리뷰: metadata와 trigger 수정이 runtime cache에도 반영되어야 한다.

## 리뷰 결과

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Runtime sync 자체의 추가 설계 이슈는 없다. Sync 후 `diff -qr`와 validators로 완료 여부를 확인한다.

## 동기화 후 재평가

- Runtime cache에 workspace canonical source의 `SKILL.md`, `agents/openai.yaml`, `references/delegation-rules.md`, `references/role-map.md`를 동기화했다.
- `diff -qr dddjango/skills/workflow-dddjango-subagents /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents` 결과 출력이 없어 source/cache parity가 확인됐다.
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills` 결과 `OK: validation passed with 0 warning(s)`로 runtime-visible role map과 metadata 검증이 통과했다.
