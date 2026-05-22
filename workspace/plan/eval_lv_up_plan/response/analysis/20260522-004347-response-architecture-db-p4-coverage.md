수정 대상: case
원인 분류: case coverage gap

# architecture-db P4 response 평가 분석

## 범위

- 대상 skill: `dddjango/skills/architecture-db/`
- source reference: `workspace/reference/architecture-db/reference/final.md`
- runtime reference: `dddjango/skills/architecture-db/references/*.md`
- 관련 bucket: `response`, `code`
- P4 제외: 여러 skill 연계와 subagent workflow 자체 평가는 P5로 넘긴다.

## 현재 inventory

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 |
|---|---|---|---|---|---|---|
| response | `case-response-order-create` | 주문 생성 API 설계에서 중복 생성 방지와 DB 제약을 묻는다. | DB uniqueness/idempotency storage, transaction boundary, locking/retry, side-effect timing을 요구한다. | answer oracle 기반 response 평가가 DB/API/DDD 혼합 응답을 판정한다. | 없음 | 대표 관련 case로 가능 |
| response | `case-response-operational-migration` | 운영 주문 테이블의 status backfill, NOT NULL, index 계획을 묻는다. | expand/backfill/contract, lock risk, batched backfill, nullable-to-not-null, rollback/forward-fix를 요구한다. | answer oracle 기반 response 평가가 rollout 안전성을 판정한다. | 없음 | 대표 관련 case로 가능 |
| response | `case-response-simple-rename` | 작은 field rename에서 과한 역할 분해를 피하게 한다. | workflow/DDD overreach를 금지한다. | negative restraint는 있으나 architecture-db의 제외 조건을 직접 검증하지 않는다. | 없음 | 낮음 |
| response | `case-response-db-schema-modeling` | 신규 direct positive로 schema/ERD, keys, cardinality, optionality, constraints/indexes를 묻는다. | architecture-db schema/constraints source basis에 맞춘 oracle을 추가했다. | answer oracle 기반 response 평가가 DB modeling 판단을 판정한다. | 추가됨 | 필요 |
| response | `case-response-db-query-plan` | 신규 direct positive로 EXPLAIN, query-shaped index, rollout risk를 묻는다. | architecture-db query/index/rollout source basis에 맞춘 oracle을 추가했다. | answer oracle 기반 response 평가가 query-plan과 index rollout 판단을 판정한다. | 추가됨 | 필요 |
| response | `case-response-db-local-crud-restraint` | 신규 direct negative로 low-risk local CRUD에서 과적용을 막는다. | architecture-db 제외 조건에 맞춘 restraint oracle을 추가했다. | answer oracle 기반 response 평가가 overapplication restraint를 판정한다. | 추가됨 | 필요 |
| response | `case-response-db-idempotency-locking` | 신규 direct positive 필요: risky write의 transaction/isolation/locking, idempotency storage, duplicate prevention을 architecture-db 단독으로 검증한다. | transactions-locking source basis에 맞춘 oracle이 필요하다. | answer oracle 기반 response 평가가 DB-owned risky write 결정을 판정해야 한다. | 추가 필요 | 필요 |
| code | `case-code-order-api` | fixture 코드에서 idempotency replay/conflict와 DB unique/service transaction을 요구한다. | service transaction boundary, idempotency storage, Problem Details, tests를 요구한다. | code artifact와 deterministic checks로 구현 산출물을 판정한다. | 없음 | 대표 관련 case로 가능 |
| code | `case-code-status-migration` | fixture 코드에서 status rollout migration 초안을 요구한다. | expand/backfill/contract, Django migration convention, hot-table lock/index risk를 요구한다. | code artifact와 deterministic checks로 migration 안전성 표현을 판정한다. | 없음 | 대표 관련 case로 가능 |

## P4 기준별 판정

1. schema/ERD, keys, constraints/indexes, transaction/isolation/locking, idempotency storage, duplicate prevention, EXPLAIN, rollout/backfill/migration safety 기준
   - 기존 혼합 case는 idempotency, duplicate prevention, transaction boundary, rollout/backfill/migration safety를 다룬다.
   - schema/ERD, keys/cardinality/optionality/normalization을 독립적으로 검증하는 direct architecture-db case가 없다.
   - EXPLAIN ANALYZE 기반 query-plan 해석과 index trade-off를 독립적으로 검증하는 direct architecture-db case가 없다.
   - 리뷰 결과, transaction/isolation/locking, idempotency storage, duplicate prevention도 혼합 API/DDD case가 아니라 direct architecture-db case로 분리해야 한다.
   - 따라서 response bucket에 direct DB architecture positive case를 보강해야 한다.
2. positive/negative 사용 조건과 제외 조건
   - positive는 혼합 API/코드 case 중심이라 architecture-db skill 단독 trigger를 검증하지 못한다.
   - negative는 simple rename restraint가 있지만 architecture-db의 `simple field rename/local CRUD/no invariant/no rollout risk` 제외 조건을 직접 확인하지 않는다.
   - 따라서 architecture-db-specific restraint case가 필요하다.
3. public case leakage
   - 기존 public case에서 answer field명, private scoring note, prior run finding 노출은 발견되지 않았다.
   - 새 case도 공개 요청문만 담고 answer oracle 필드명과 이전 run finding을 넣지 않는다.
4. answer oracle over/under-claim
   - 기존 answer는 reference 범위 안에서 idempotency와 rollout을 요구한다.
   - 새 answer는 `architecture-db` reference의 직접 기준만 요구하고 Django migration 구현, API contract, implementation-test 세부 실행은 handoff 또는 not-run honesty로 제한한다.
5. case, answer, evaluator 목적 일치
   - evaluator script는 answer oracle을 기준으로 baseline/with-dddjango 출력을 비교하므로 새 answer가 reference 기반 DB 기준을 정확히 담으면 목적 일치가 유지된다.
   - evaluator 구조 변경은 필요 없다.
6. P5 제외
   - workflow bucket의 risky-write consistency case는 architecture-db와 관련된 용어를 포함하지만 subagent/workflow 평가가 핵심이므로 이번 P4 수정 대상에서 제외한다.

## 수정 결정

- Blocker: 0
- Major: 1
  - architecture-db 단독 coverage가 부족하다. 특히 schema/ERD/keys와 EXPLAIN/query-plan 기준이 비어 있고, architecture-db-specific negative case가 없다.
  - 리뷰 후 추가 판정: risky-write DB 결정(transaction/isolation/locking, idempotency storage, duplicate prevention)도 direct case가 필요하다.
- 열린 Minor: 0

## 수정 대상

- `workspace/develop/eval/response/cases/plugin/public/`
- `workspace/develop/eval/response/answer/`

## 리뷰 방식

리뷰 방식: real-subagent

1차 real subagent 리뷰를 실행했다.

- skill-creator 관점 리뷰: Major 2, Blocker 1. direct risky-write DB coverage 부족, 일부 supporting answer source basis 약함, targeted run evidence invalid.
- 독립 리뷰: Major 4, Minor 1. direct risky-write DB coverage 부족, targeted eval evidence incomplete, validator coverage enforcement 부족, prompt-input artifact validation 약함.

coverage 부족은 이 문서의 case 수정 범위에 반영한다. answer source/evidence와 evaluator validator 문제는 별도 `answer`, `evaluator` 분석/계획으로 분리한다.

리뷰 결과: Blocker 1, Major 4, 열린 Minor 1
