수정 이유: P3 source skill 수정으로 runtime cache와 source skill이 달라졌다. 종료 조건은 source skill과 runtime cache 동기화 확인을 요구한다.

작업 ID: 20260521-232258-architecture-db-p3-runtime-sync

## 수정 범위

- `dddjango/skills/architecture-db/SKILL.md`를 runtime cache 같은 상대 경로에 복사한다.
- `dddjango/skills/architecture-db/references/transactions-locking.md`를 runtime cache 같은 상대 경로에 복사한다.
- `dddjango/skills/architecture-db/agents/openai.yaml`을 runtime cache 같은 상대 경로에 복사한다.

## 수정하지 말아야 할 범위

- source reference는 수정하지 않는다.
- P3에서 바꾸지 않은 bundled references는 복사 대상이 아니다.
- runtime cache에 source와 다른 내용을 직접 작성하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` source를 runtime cache에 동기화한다.
- [x] `references/transactions-locking.md` source를 runtime cache에 동기화한다.
- [x] `agents/openai.yaml` source를 runtime cache에 동기화한다.
- [x] `diff -qr`로 source/runtime parity를 확인한다.
- [x] plan/skill validator를 실행해 runtime-sync 분석/계획 제약도 확인한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/architecture-db /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db`

## 완료 조건

- source skill과 runtime cache의 `architecture-db` 디렉터리 차이가 없다.
- runtime-sync 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

## 완료 판정

완료. `diff -qr dddjango/skills/architecture-db /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db` 출력 없음으로 architecture-db source/runtime parity를 확인했다.
