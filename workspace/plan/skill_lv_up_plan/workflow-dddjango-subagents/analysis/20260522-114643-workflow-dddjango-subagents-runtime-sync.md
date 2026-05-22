수정 대상: runtime-sync
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

# workflow runtime sync 분석

## 배경

`workflow-dddjango-subagents` runtime-facing wording을 수정한 뒤 `validate_skill_docs.py --phase all --skills-dir dddjango/skills`가 runtime cache와 source skill의 `SKILL.md`, `references/integration-checklist.md` 차이를 보고했다.

## 원인

원인 분류는 `runtime-sync`다. Workspace canonical source는 수정됐지만 Codex runtime cache가 아직 같은 변경을 반영하지 않았다.

## 수정 판단

두 파일만 source에서 runtime cache로 동기화한다. Role map이나 agents metadata는 변경하지 않았으므로 sync 범위를 넓히지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff` 또는 validator 결과로 cache/source parity 확인
