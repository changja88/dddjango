수정 대상: answer
원인 분류: answer underclaim

# architecture-db P4 answer oracle 수정 계획

## 수정 파일

- `workspace/develop/eval/response/answer/case-response-db-schema-modeling.yaml`
- `workspace/develop/eval/response/answer/case-response-db-query-plan.yaml`
- `workspace/develop/eval/response/answer/case-response-db-local-crud-restraint.yaml`
- `workspace/develop/eval/response/answer/case-response-db-idempotency-locking.yaml`
- `workspace/develop/eval/response/answer/case-response-order-create.yaml`
- `workspace/develop/eval/response/answer/case-response-operational-migration.yaml`

## 작업 순서

1. 신규 direct DB answer oracle의 `evidence_required`를 response eval goal과 맞춘다.
   - public prompt packet
   - baseline and with-dddjango response
   - baseline isolation artifact
   - with-dddjango prompt-input artifact
   - command, exit code, event stream, stderr
   - answer-oracle evaluation notes
   - machine-readable answer-oracle evaluation artifact
2. mixed/supporting case의 DB source traceability를 강화한다.
   - `case-response-order-create`에 `workspace/reference/architecture-db/reference/final.md`, `dddjango/skills/architecture-db/references/transactions-locking.md`, `dddjango/skills/architecture-db/references/constraints-indexes.md`를 추가한다.
   - `case-response-operational-migration`에 `dddjango/skills/architecture-db/SKILL.md`, `dddjango/skills/architecture-db/references/rollout-constraints.md`, `dddjango/skills/architecture-db/references/constraints-indexes.md`를 추가한다.
3. `case-response-order-create`의 mixed-skill source traceability를 강화한다.
   - `workspace/reference/architecture-ddd/reference/final.md`
   - `workspace/reference/architecture-api/reference/final.md`
   - `workspace/reference/implementation-django-ninja/reference/final.md`
   - `workspace/reference/implementation-test/reference/final.md`
   - 필요한 runtime bundled references
4. `case-response-order-create`와 `case-response-operational-migration`의 `evidence_required`를 response eval goal과 맞춘다.
5. public case는 수정하지 않는다.
   - leakage boundary를 유지한다.
6. validator를 실행한다.
   - `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`

## 완료 조건

- answer oracle이 eval goal evidence보다 부족하지 않다.
- DB 판단을 요구하는 answer가 architecture-db source/runtime reference에 traceable하다.
- mixed case의 non-DB 요구도 owning reference에 traceable하다.
- public prompt leakage가 없다.
