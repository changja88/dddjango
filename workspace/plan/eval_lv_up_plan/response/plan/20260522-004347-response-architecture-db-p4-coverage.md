수정 대상: case
원인 분류: case coverage gap

# architecture-db P4 response 평가 계획

## 목표

`architecture-db` 개별 skill 평가가 source reference의 DB 설계 범위를 직접 검증하도록 response bucket에 공개 case와 answer oracle을 보강한다.

## 수정 파일

- 추가: `workspace/develop/eval/response/cases/plugin/public/case-response-db-schema-modeling.md`
- 추가: `workspace/develop/eval/response/answer/case-response-db-schema-modeling.yaml`
- 추가: `workspace/develop/eval/response/cases/plugin/public/case-response-db-query-plan.md`
- 추가: `workspace/develop/eval/response/answer/case-response-db-query-plan.yaml`
- 추가: `workspace/develop/eval/response/cases/plugin/public/case-response-db-idempotency-locking.md`
- 추가: `workspace/develop/eval/response/answer/case-response-db-idempotency-locking.yaml`
- 추가: `workspace/develop/eval/response/cases/plugin/public/case-response-db-local-crud-restraint.md`
- 추가: `workspace/develop/eval/response/answer/case-response-db-local-crud-restraint.yaml`

## 작업 순서

1. `case-response-db-schema-modeling` public case를 작성한다.
   - 사용자는 예약 도메인의 RDB schema/ERD, keys, cardinality, optionality, constraints/indexes를 묻는다.
   - 공개 요청문에는 answer oracle field명, private 기준, prior run finding을 넣지 않는다.
2. 같은 id의 answer oracle을 작성한다.
   - `architecture-db` source/runtime reference를 basis로 둔다.
   - conceptual/logical/physical modeling, PK/FK/unique/check/not-null, cardinality/optionality, normalization/denormalization trade-off, index write cost를 required로 둔다.
   - Django migration 파일 작성, API contract, subagent workflow 요구는 forbidden 또는 handoff로 둔다.
3. `case-response-db-query-plan` public case를 작성한다.
   - 사용자는 `EXPLAIN ANALYZE` 일부와 slow query 상황을 주고 index/query tuning과 rollout risk를 묻는다.
   - denormalization을 먼저 하거나 index를 무차별 추가하지 않도록 유도한다.
4. 같은 id의 answer oracle을 작성한다.
   - plan estimates vs actual rows, scan/join type, composite index order, covering/partial index 판단, write/storage cost, concurrent/online index rollout, validation method를 required로 둔다.
5. `case-response-db-idempotency-locking` public case를 작성한다.
   - 사용자는 결제 승인 retry/동시 요청에서 DB 중복 방지와 idempotency 저장소를 묻는다.
   - API 세부 계약과 outbox/saga 구현은 제외하고 DB-owned transaction/isolation/locking/storage 결정을 요구한다.
6. 같은 id의 answer oracle을 작성한다.
   - DB transaction boundary, unique/idempotency key scope, request fingerprint, stored result/replay reference, retention/cleanup, locking strategy, isolation/retry, side-effect timing handoff를 required로 둔다.
   - API `Idempotency-Key` replay/conflict contract, concrete Django implementation, test mechanics는 handoff로 제한한다.
7. `case-response-db-local-crud-restraint` public case를 작성한다.
   - 사용자는 작은 internal CRUD table 추가만 묻고 DB invariant, rollout risk, high contention이 없다고 명시한다.
   - 답변은 짧고 scoped해야 한다.
8. 같은 id의 answer oracle을 작성한다.
   - full ERD, locking/isolation, idempotency table, workflow/subagent plan을 금지한다.
   - 필요한 최소 schema/migration 영향과 verification honesty만 요구한다.
9. response bucket validator를 실행한다.
   - 명령: `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
10. 필수 공통 validator를 실행한다.
   - `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
   - `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
   - `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
11. targeted eval을 실행한다.
   - 우선 새 representative case 1개 이상을 `make eval-one BUCKET=response CASE=<case-id> TRY_NUMBER=1 SCOPE=targeted TOPIC=architecture-db-p4 EXTRA_ARGS=--rerun JOBS=1`로 확인한다.
   - 시간이 허용되면 새 positive/negative case를 모두 실행한다.
12. skill-creator 관점 subagent와 독립 subagent review를 실행한다.
    - trigger, 목적, reference, progressive disclosure, validation integrity를 판정한다.
    - Blocker/Major/open Minor가 있으면 다시 수정한다.

## 완료 조건

- response bucket에 architecture-db 단독 positive/negative coverage가 있다.
- public case가 evaluator-only answer material이나 prior run finding을 누설하지 않는다.
- answer oracle 요구가 `architecture-db` reference보다 과도하거나 부족하지 않다.
- case, answer, evaluator가 같은 DB architecture 목적을 검증한다.
- 필수 validator와 targeted eval 결과를 최종 보고에 남긴다.
