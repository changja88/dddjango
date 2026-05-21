수정 이유: source `architecture-db` skill과 runtime cache가 달라졌으므로 P2 종료 조건의 runtime sync를 만족할 수 없다.

작업 ID: 20260521-222104-architecture-db-p2-runtime-sync

## 수정 범위

- `dddjango/skills/architecture-db/SKILL.md`를 runtime cache의 같은 상대 경로로 동기화한다.
- `dddjango/skills/architecture-db/agents/openai.yaml`을 runtime cache의 같은 상대 경로로 동기화한다.
- `dddjango/skills/architecture-db/references/schema-modeling.md`를 runtime cache의 같은 상대 경로로 동기화한다.
- `dddjango/skills/architecture-db/references/transactions-locking.md`를 runtime cache의 같은 상대 경로로 동기화한다.
- 동기화 후 directory diff로 source/cache parity를 확인한다.

## 수정하지 말아야 할 범위

- runtime cache의 다른 skill 디렉터리
- source reference `workspace/reference/**`
- eval pack과 generated run artifact

## 작업 체크리스트

- [x] runtime cache `SKILL.md`를 source와 동일하게 만든다.
- [x] runtime cache `agents/openai.yaml`을 source와 동일하게 만든다.
- [x] runtime cache `references/schema-modeling.md`를 source와 동일하게 만든다.
- [x] runtime cache `references/transactions-locking.md`를 source와 동일하게 만든다.
- [x] `diff -qr`로 source skill directory와 runtime cache directory가 같은지 확인한다.
- [x] validators를 실행한다.

## 검증 명령

- `diff -qr dddjango/skills/architecture-db /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `diff -qr` 출력이 없다.
- runtime cache가 source skill의 P2 trigger/metadata/reference boundary를 그대로 포함한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0으로 닫힌다.

## 완료 판정

완료. `diff -qr` 출력이 없고, validators 통과 후 최종 read-only subagent 재평가에서 source/runtime parity가 닫혔다.
