수정 이유: `architecture-db`의 risky-write guidance가 DB-owned 결정과 adjacent skill의 pattern/API/test/implementation 결정을 모두 같은 수준으로 기록하게 해 `architecture-implementation-patterns`, `architecture-api`, `implementation-django`, `implementation-test`, `workflow-dddjango-subagents`와 책임 경계가 흐려질 수 있다.

작업 ID: 20260521-232258-architecture-db-p3-skill

## 수정 범위

- `dddjango/skills/architecture-db/SKILL.md`의 risky-write runtime rule을 DB-owned 결정과 handoff 결정으로 분리한다.
- `dddjango/skills/architecture-db/references/transactions-locking.md`의 risky-write 및 side-effect guidance를 DB 관점 기록과 handoff 기준으로 좁힌다.
- `dddjango/skills/architecture-db/agents/openai.yaml` default prompt에 concrete Django migration file handoff를 드러낸다.

## 수정하지 말아야 할 범위

- source reference는 이번 P3에서 충분하므로 수정하지 않는다.
- adjacent skill의 책임 문구는 이번 작업 범위 밖이다.
- `agents/openai.yaml`은 default prompt만 보강하고 optional interface field는 추가하지 않는다.
- runtime cache는 source 수정 후 별도 runtime-sync 분석/계획으로 처리한다.
- bundled reference 내용을 `SKILL.md`에 장황하게 복사하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` risky-write rule에서 DB-owned 항목을 명시한다.
- [x] pattern-level transaction owner, outbox/saga/ACL, side-effect reliability는 `architecture-implementation-patterns` handoff로 둔다.
- [x] `Idempotency-Key` replay/conflict behavior는 `architecture-api` handoff로 둔다.
- [x] concrete Django transaction/migration code는 `implementation-django` handoff로 둔다.
- [x] pytest/integration/concurrency test mechanics는 `implementation-test` handoff로 둔다.
- [x] `transactions-locking.md`에서 DB skill이 outbox/saga를 직접 선택하는 듯한 문구를 줄인다.
- [x] `agents/openai.yaml` default prompt에 concrete Django migration file handoff를 드러낸다.
- [x] 수정 후 real subagent review 결과를 통합해 Blocker 0, Major 0, 열린 Minor 0 상태로 닫는다.
- [x] source/runtime cache drift가 있으면 runtime-sync 분석/계획을 작성하고 동기화한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/architecture-db /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db`

## 완료 조건

- 직접 책임과 handoff 기준이 명확하다.
- risky-write guidance가 adjacent architecture/API/implementation/test/workflow skill과 충돌하지 않는다.
- `SKILL.md`는 핵심 절차 중심이고 500줄 미만이다.
- bundled references는 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- 불필요한 중복과 깊은 reference 연결이 없다.
- runtime cache가 source skill과 동기화된다.
- 검증 명령이 통과한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0으로 닫힌다.

## 완료 판정

architecture-db 범위의 수정과 runtime cache sync는 완료했다. Real subagent 리뷰에서 제기된 architecture-db Blocker, Major, 열린 Minor는 0으로 닫혔다. 최종 검증 명령 4개는 현재 worktree 기준 모두 통과했다.
