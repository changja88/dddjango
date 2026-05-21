수정 대상: reference
원인 분류: source gap
작업 ID: 20260521-203058-architecture-db-p1-reference

## 평가 범위

- 대상 source reference: `workspace/reference/architecture-db/reference/final.md`
- 비교 대상 runtime skill: `dddjango/skills/architecture-db/SKILL.md`, `dddjango/skills/architecture-db/references/*.md`, `dddjango/skills/architecture-db/agents/openai.yaml`
- runtime cache 비교 대상: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/`
- 평가 기준: schema modeling, normalization, keys, constraints, indexes, transactions, isolation, locking, concurrency, idempotency storage, duplicate prevention, query performance, rollout/backfill, migration safety

## 현재 평가

`final.md`는 ERD, 개념/논리/물리 모델링, 키, 정규화/역정규화, B+Tree 인덱스, 복합/커버링/부분 인덱스, ACID, 격리 수준, EXPLAIN ANALYZE, 쿼리 최적화, 계층 구조, 상속/다형성은 판단 근거로 충분하다.

부족한 source 결정은 다음과 같다.

| 항목 | 현재 상태 | 문제 |
|---|---|---|
| constraints | PK와 FK는 모델링 맥락에 있고 partial unique index 예시는 있으나, FK/unique/check/not-null/cascade를 도메인 불변식과 연결하는 체계적 기준이 없다. | runtime bundled reference의 constraints guidance가 source final에 충분히 trace되지 않는다. |
| duplicate prevention | soft-delete unique 예시는 있으나 자연 유니크, 요청 중복, 멱등성 저장소를 구분하지 않는다. | duplicate-sensitive write 기준을 판단하기 어렵다. |
| locking/concurrency | 격리 수준과 phenomena는 있으나 row lock, optimistic/pessimistic locking, retry/deadlock handling 기준이 없다. | `transactions-locking.md`의 locking guidance가 source보다 앞서 있다. |
| idempotency storage | source final에 저장 key scope, request hash, response snapshot, unique constraint, replay/conflict 저장 정책이 없다. | `Risky Write Consistency Block`의 idempotency storage 항목을 source가 뒷받침하지 못한다. |
| rollout/backfill/migration safety | external/review에는 expand-contract와 migration boundary 논의가 있으나 final에는 채택 결정이 없다. | runtime의 rollout/backfill/rollback/index-lock guidance가 source final에 trace되지 않는다. |

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent 2개를 실행했다. 하나는 P1 source/runtime 감사 관점, 하나는 `skill-creator` 관점으로 읽기 전용 검토를 수행했다.

리뷰 증거:

- 초기 P1 source/runtime 감사: agent `019e4a4d-5ac9-7260-bdb7-236fac5582e9`, read-only, 결과 수집 완료. 초기 발견은 Blocker 0건, Major 3건, Minor 한 건이었다.
- 초기 skill-creator 관점 감사: agent `019e4a4d-73c1-70d2-be6b-452b2e0f498f`, read-only, 결과 수집 완료. 초기 발견은 Blocker 0건, Major 2건, Minor 한 건이었다.
- 최종 P1 재평가: agent `019e4a54-41aa-7ab3-b06c-01fd79874d90`, read-only, 결과 수집 완료. 최종 결과는 Blocker 0, Major 0, Minor 0이었다.
- 최종 skill-creator 재평가: agent `019e4a54-5a19-70c2-aca1-15b90a5c05d6`, read-only, 결과 수집 완료. Review-trail 재현성 지적 1건은 이 문서의 trace ID 보강으로 후속 조치했다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

skill-creator 리뷰: `SKILL.md`의 목적, trigger description, progressive disclosure는 양호하지만 runtime locking guidance가 source final보다 앞서고, validator pass만으로 semantic source-to-runtime fidelity를 증명할 수 없다고 판정했다. Reference loading의 per-reference negative condition 약점은 source 보강 후 skill 점검에서 다룰 열린 Minor로 분류한다.

## 통합 판단

이 문제는 skill만 좁혀서 덮을 문제가 아니다. `architecture-db`의 목적은 relational database architecture이고, runtime skill이 이미 constraints, locking, idempotency storage, rollout/backfill을 필요한 DB 설계 축으로 올바르게 다룬다. 따라서 source reference를 보강해 runtime guidance의 근거를 충분하게 만드는 것이 P1 목표에 맞다.

## 수정 대상

- `workspace/reference/architecture-db/reference/final.md`

수정하지 말아야 할 범위:

- `workspace/develop/eval/**` eval pack은 이번 P1에서 수정하지 않는다.
- concrete Django migration code, `RunPython`, `apps.get_model()`, `sqlmigrate` 사용법은 `implementation-django` 영역으로 남긴다.
- API `Idempotency-Key` status code, Problem Details, OpenAPI 계약은 `architecture-api` 영역으로 남기고 DB storage handoff만 다룬다.

## 재평가

Reference final에 constraints, duplicate prevention, idempotency storage, locking/concurrency, risky write consistency, rollout/backfill/migration safety 결정을 추가했다. 최종 subagent 재평가와 validator 결과 기준으로 reference source gap은 닫혔다.
