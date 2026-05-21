수정 이유: `architecture-db` runtime skill이 다루는 constraints, locking/concurrency, idempotency storage, rollout/backfill/migration safety가 source reference final에 충분히 채택되어 있지 않다.

작업 ID: 20260521-203058-architecture-db-p1-reference

## 수정 범위

- `workspace/reference/architecture-db/reference/final.md`에 source-level DB architecture 결정을 추가한다.
- 추가 주제:
  - PK/FK/unique/check/not-null/cascade 제약조건 선택 기준
  - duplicate prevention과 idempotency storage의 DB 설계 기준
  - optimistic/pessimistic locking, unique constraint 기반 동시성 제어, retry/deadlock/serialization failure 기준
  - expand/backfill/contract, index-lock risk, failed constraint/index/backfill rollback 또는 forward-fix 기준

## 수정하지 말아야 할 범위

- `dddjango/skills/architecture-db/**`는 reference 보강 후 재평가 전까지 수정하지 않는다.
- concrete Django migration file 작성법은 `implementation-django` reference와 skill 책임으로 남긴다.
- REST `Idempotency-Key` 계약의 HTTP status, header, Problem Details 세부사항은 `architecture-api` 책임으로 남긴다.
- eval case, answer, evaluator, report는 이번 reference plan에서 수정하지 않는다.

## 작업 체크리스트

- [x] source final의 목차와 본문에 constraints/duplicate prevention 섹션을 추가한다.
- [x] source final의 트랜잭션 섹션을 locking/concurrency/idempotency storage까지 확장한다.
- [x] source final에 operational rollout/backfill/migration safety 섹션을 추가한다.
- [x] 참고 문헌에 source basis를 반영한다.
- [x] reference 보강 후 skill 반영도와 runtime sync를 재평가한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/architecture-db /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db`

## 완료 조건

- source final이 P1 기준의 DB 설계 축을 모두 판단할 수 있다.
- runtime skill의 constraints, locking, idempotency storage, rollout/backfill guidance가 source final에 trace된다.
- reference 보강으로 skill/runtime overclaim Major가 닫힌다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이 될 때까지 필요한 후속 skill/runtime-sync plan을 별도로 작성한다.

## 완료 판정

완료. 후속 skill plan과 runtime-sync plan을 작성 및 실행했고, 최종 재평가 결과는 Blocker 0, Major 0, 열린 Minor 0이다.
