# workflow-dddjango-subagents P1 runtime sync 계획

## 수정 이유

Source skill bundle이 새 source reference를 반영하도록 수정됐지만 active runtime cache는 이전 내용이다. Runtime cache를 동기화하지 않으면 P1의 runtime sync 종료 조건을 만족할 수 없다.

## 수정 범위

- Source: `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- Source: `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`
- Source: `dddjango/skills/workflow-dddjango-subagents/references/*.md`
- Runtime cache target: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/`

## 수정하지 말아야 할 범위

- 다른 runtime skill cache
- 다른 workspace skill
- source reference 문서
- eval pack

## 작업 체크리스트

- [x] Source skill generated validation을 먼저 통과시킨다.
- [x] Workspace canonical source files를 runtime cache target으로 복사한다.
- [x] `diff -rq`로 source/cache parity를 확인한다.
- [x] `validate_skill_docs.py --phase all --skills-dir dddjango/skills`로 runtime parity와 workflow role-map checks를 확인한다.
- [x] Sync 분석 문서의 review 결과를 실제 재평가 결과로 닫는다.

## 검증 명령

- `diff -rq dddjango/skills/workflow-dddjango-subagents /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Source skill과 runtime cache의 runtime-facing files가 일치한다.
- Role map parity가 source보다 축소되지 않았다.
- Runtime cache sync가 실제 실행 증거로 확인됐다.
- Review 결과가 Blocker 0, Major 0, 열린 Minor 0으로 닫힌다.

## 완료 확인

Runtime cache sync를 수행했고 source/cache diff가 비어 있음을 확인했다. `validate_skill_docs.py --phase all --skills-dir dddjango/skills`도 통과했다.
