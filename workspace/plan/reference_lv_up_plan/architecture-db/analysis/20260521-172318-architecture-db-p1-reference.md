수정 대상: reference
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
원인 분류: source gap

# architecture-db P1 점검 결과

## 개선 대상 한 문장

`dddjango:architecture-db`는 관계형 데이터베이스 설계에서 도메인 불변식과 조회/쓰기 패턴을 보호할 스키마, 제약, 인덱스, 트랜잭션, 락, 멱등성 저장, 성능 검증, 운영 롤아웃 기준을 결정하고 구현 세부 작업은 관련 skill로 넘기는 skill이다.

## 기준 reference

- 기준 source reference는 `workspace/reference/architecture-db/reference/final.md`이다.
- source gap과 conflict 후보는 `workspace/reference/architecture-db/reference/review.md`, `internal.md`, `external.md`에서 확인했다.
- runtime evidence는 `dddjango/skills/architecture-db/SKILL.md`, `dddjango/skills/architecture-db/references/*.md`, `dddjango/skills/architecture-db/agents/openai.yaml`이다.
- source/runtime 경계 기준은 `workspace/reference/source-reference-audit/reference/final.md`에서 확인했다.

## reference 상태

`개선 필요`.

`workspace/reference/architecture-db/reference/final.md`는 관계형 DB 설계의 기본 축은 충분히 제공한다.

- 업무 파악부터 개념적, 논리적, 물리적 모델링으로 이어지는 모델링 순서가 있다.
- ERD 요소, 키, cardinality, optionality 기준이 있다.
- 1NF부터 BCNF까지의 정규화 기준과 정규화 우선, 필요 시 역정규화 원칙이 있다.
- B+Tree 인덱스 구조, 읽기/쓰기 비용, 복합 인덱스 순서, 커버링 인덱스, 부분 인덱스 기준이 있다.
- ACID, 격리 수준, 동시성 이상 현상, `EXPLAIN ANALYZE`, 스캔/조인 유형, N+1 기준이 있다.
- 계층 구조와 상속/다형성 모델링 패턴이 있다.

하지만 현재 runtime skill이 맡는 범위 중 일부는 source reference에서 충분히 결정되지 않았다.

- `SKILL.md`와 `transactions-locking.md`는 락 전략, 낙관적/비관적 락, 멱등성 저장 위치와 unique constraint, risky write consistency block, 외부 side effect timing, integration/concurrency test criteria를 runtime 의사결정 대상으로 둔다.
- `rollout-constraints.md`는 expand/backfill/contract, backfill batch와 monitoring, failed constraint/index creation, old/new application compatibility, rollback/forward-fix까지 runtime 기준으로 둔다.
- 반면 `final.md`는 첫머리에서 마이그레이션 도구를 범위 밖으로 제한하고, 본문도 트랜잭션 격리 수준과 쿼리 계획 중심이다. 행 수준 락, advisory lock, optimistic/pessimistic locking, duplicate prevention/idempotency storage, risky write handoff, staged rollout failure handling은 source decision으로 충분히 정리되어 있지 않다.

따라서 P1 결론은 `reference 개선 필요`이다. skill이 과도하게 잘못되었다기보다, runtime skill이 이미 책임지고 있는 운영/동시성/멱등성 범위의 source basis가 부족하다.

## skill 반영도

`reference gap 때문에 충분 판정 불가`.

반영이 충분한 항목:

- `description`은 ERD, schema modeling, normalization, keys, constraints, indexes, transaction, isolation, locking, idempotency storage, query performance, rollout/backfill/index-lock risk, migration safety를 트리거로 명시한다.
- `Routing`은 DDD invariant, implementation pattern, API contract, Django migration, pytest/concurrency test, workflow/subagent handoff를 분리한다.
- `Reference Loading`은 schema modeling, constraints/indexes, transactions/locking, rollout/performance를 네 개 reference로 나누어 progressive disclosure를 지킨다.
- `Runtime Rules`는 개념적 모델링에서 물리 설계로 진행하고, DB-enforceable invariant는 DB constraint로 보호하며, risky write consistency block을 요구한다.

부족하거나 근거가 약한 항목:

- runtime reference의 `transactions-locking.md`가 요구하는 락 전략과 멱등성 저장 기준은 `final.md`의 격리 수준 설명만으로는 충분히 뒷받침되지 않는다.
- runtime reference의 `rollout-constraints.md`가 요구하는 expand/backfill/contract와 실패 시 rollback/forward-fix 기준은 `final.md`에 명시적 source decision이 부족하다.
- DB/API/test/workflow handoff 자체는 적절하지만, risky write에서 DB skill이 소유해야 할 storage/locking/isolation/retry 기준의 source 근거가 얕다.

## 책임 경계

대체로 충분하다.

- 도메인 불변식과 aggregate boundary가 불명확하면 `architecture-ddd`로 넘긴다.
- repository/UoW, outbox, CQRS, hexagonal/ports-adapters, ACL 같은 구조 선택은 `architecture-implementation-patterns`로 넘긴다.
- REST resource, status code, Problem Details, `Idempotency-Key`, OpenAPI는 `architecture-api`로 넘긴다.
- concrete Django model, `RunPython`, `apps.get_model()`, `sqlmigrate`, migration file은 `implementation-django`로 넘긴다.
- pytest integration/concurrency test mechanics는 DB invariant와 transaction 기준이 정해진 뒤 `implementation-test`로 넘긴다.

주의할 점은 DB skill이 risky write에서 transaction owner, locking strategy, uniqueness/idempotency storage, isolation/retry 기준까지는 소유하되, API replay/conflict semantics와 test fixture mechanics를 직접 구현 책임으로 가져오지 않는 것이다. 현재 routing은 이 경계를 대체로 지킨다.

## eval 점검 필요 여부

P1에서는 eval 수정 후보를 확정하지 않는다.

다만 reference 개선 뒤 P4에서 `architecture-db` 평가가 다음 항목을 관찰하는지 확인할 필요가 있다.

- source gap이 보강된 락/멱등성/롤아웃 기준을 답변이 실제로 적용하는지.
- risky write consistency block이 DB/API/test/workflow 책임을 구분하는지.
- backfill, failed constraint validation, failed index creation, old/new application compatibility window를 과장 없이 다루는지.

관련 bucket은 이 문서에서 확정하지 않는다.

## 후속 분석 문서 위치

현재 문서:

`workspace/plan/reference_lv_up_plan/architecture-db/analysis/20260521-172318-architecture-db-p1-reference.md`

## 다음 단계

`reference 개선 계획`.

P1에서는 skill, reference, eval을 바로 수정하지 않는다. 다음 단계에서 같은 대상의 `plan/` 아래에 개선 계획을 작성한 뒤, `workspace/reference/architecture-db/reference/final.md`의 source basis를 락 전략, 멱등성 저장, risky write consistency, staged rollout/backfill/index-lock failure handling까지 보강한다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰를 실행했다.

- raw 요약: Blocker 0, Major 1, 열린 Minor 1.
- raw Major: source reference가 runtime 범위 일부인 locking strategy, idempotency storage, risky write consistency, side-effect timing, backfill/rollout/index-lock risk, migration safety를 충분히 뒷받침하지 못한다.
- raw Minor: skill/runtime 문서 설명문 대부분이 영어라 프로젝트의 한글 우선 문서 제약과 어긋날 수 있다.
- 통합 판단: raw Major는 `reference` 수정 후보로 채택한다. raw Minor는 P1의 reference 반영도 결론을 막는 열린 이슈로 유지하지 않고 Note로 내린다. 문서 언어 문제는 reference source gap을 닫은 뒤 P2 skill 반영도 또는 별도 skill 문서 품질 점검에서 다룰 수 있다.

## skill-creator 리뷰

real-subagent로 수행했다.

- 목적 명확성: 충분하다. relational DB architecture와 구현 제외 범위가 명확하다.
- trigger description: 충분하다. positive trigger와 negative routing이 모두 들어 있다.
- progressive disclosure: 충분하다. `SKILL.md`는 짧고, 세부 기준은 네 개 bundled reference로 분리되어 있다.
- reference 중복/누락: 누락이 있다. runtime 범위 중 락 전략, 멱등성 저장, risky write consistency, staged rollout failure handling에 대응하는 source reference가 부족하다.
- validation integrity: 실제 실행하지 않은 검증, 리뷰, subagent 작업을 주장하지 말라는 규칙이 있다.

## 통합 리뷰 결과

`architecture-db`의 runtime skill은 관계형 DB 설계 skill로서 목적, routing, reference loading, handoff가 대체로 명확하다. 문제는 source reference가 runtime이 이미 요구하는 운영/동시성/멱등성 기준을 충분히 뒷받침하지 못한다는 점이다. 수정 대상 후보는 `reference`이다.

## 산출 형식 요약

```text
수정 대상 후보: reference
기준 reference: workspace/reference/architecture-db/reference/final.md
reference 상태: 개선 필요
skill 반영도: reference gap 때문에 충분 판정 불가. 모델링/정규화/인덱스/격리/쿼리 기준은 반영됐지만 locking/idempotency/risky write/rollout source basis가 약함
책임 경계: 대체로 충분함. DDD/API/implementation-django/implementation-test/workflow handoff 유지
eval 점검 필요 여부: P1에서는 확정하지 않음. reference 개선 후 P4에서 risky write, 멱등성 저장, 롤아웃 평가 coverage 확인 필요
후속 분석 문서 위치: workspace/plan/reference_lv_up_plan/architecture-db/analysis/20260521-172318-architecture-db-p1-reference.md
다음 단계: reference 개선 계획
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
Subagent 리뷰/순차 fallback: real-subagent 실행, 원결과 Major 1은 reference 수정 후보로 채택, 원결과 Minor 1은 Note/P2 이후 점검 항목으로 정리
skill-creator 리뷰: real-subagent 수행
통합 리뷰 결과: 수정 대상 후보 reference, reference 상태 개선 필요, 열린 Blocker/Major/Minor 없음
종료 조건 충족 여부: 충족
검증/미검증: validate_plan_constraints.py 및 test_validate_plan_constraints.py 통과. skill docs validator, eval validator, runtime cache sync는 P1 범위에서 미실행
```

## 리뷰 결과

- Blocker: 0개.
- Major: 0개.
- 열린 Minor: 0개.
- Note: skill/runtime 문서 언어의 한글 우선 제약은 P1의 source reference gap 결론을 바꾸지 않는다. reference 개선 후 P2 또는 별도 skill 품질 점검에서 함께 확인한다.
- Note: eval coverage는 P1에서 수정 대상으로 확정하지 않는다. reference 개선 뒤 P4에서 확인한다.

## 종료 조건 충족 여부

- 기준 reference 상태: `개선 필요`로 확정.
- 수정 대상 후보: `reference`.
- Blocker/Major: 0개.
- 열린 Minor: 0개.
- Subagent 리뷰: real-subagent 실행.
- skill-creator 리뷰: real-subagent 실행.
- 다음 단계: `reference 개선 계획`.
- 후속 분석 문서: 작성 완료.
- P1에서 개선 계획 문서, skill 수정, reference 수정, eval 수정은 하지 않음.
- 실제로 실행하지 않은 검증, 리뷰, subagent 작업을 수행한 것처럼 쓰지 않음.

## 검증/미검증

- 검증 완료: `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- 검증 완료: `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- 미검증: skill docs validator, eval validator, runtime cache sync. P1 범위에서는 skill/reference/eval/runtime artifact를 수정하지 않았다.

## Serena

Serena: skipped because this P1 work was document/source-boundary analysis without symbol tracing and no Serena MCP resources were available; verified with scoped file reads, `rg`, `nl`, and real-subagent review.
