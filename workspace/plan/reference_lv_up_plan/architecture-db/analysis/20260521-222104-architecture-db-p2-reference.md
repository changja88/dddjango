수정 대상: reference
원인 분류: source follow-up
작업 ID: 20260521-222104-architecture-db-p2-reference

## 평가 범위

- source reference final: `workspace/reference/architecture-db/reference/final.md`
- source review gap ledger: `workspace/reference/architecture-db/reference/review.md`
- runtime skill: `dddjango/skills/architecture-db/SKILL.md`
- bundled reference: `dddjango/skills/architecture-db/references/schema-modeling.md`

## 후속 분류

`workspace/reference/architecture-db/reference/review.md`의 `[D-1] 파티셔닝 전략`은 range/hash/list partitioning, pruning, tenant/time partitioning, operational trade-off 같은 상세 기준이 source final에 없다고 기록한다. 현재 final은 물리 모델링 산출물로 partitioning을 짧게 언급할 뿐, runtime skill이 독립 guidance로 사용할 설계 기준을 제공하지 않는다.

## P2 처리 결정

P2에서 partitioning guidance를 새로 만들지 않는다. Source final이 충분하지 않은 상태에서 runtime skill을 상세 partitioning 설계 skill처럼 보이게 하면 source/runtime overclaim이 된다.

따라서 P2에서는 runtime skill의 partitioning claim을 제거하거나 source-backed 범위로 축소하고, partitioning strategy 자체는 reference 후속 과제로 남긴다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: P2 독립 subagent가 partitioning을 Major로 제기했다. Main agent가 `review.md`와 source final, runtime skill을 대조해 source follow-up으로 분류했다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 후속 작업

- 향후 reference 개선에서 range/hash/list partitioning, partition pruning, tenant/time partitioning, index/constraint interaction, rollout/backfill impact를 source-backed 기준으로 다룰지 결정한다.
- Source final이 보강되기 전까지 runtime skill은 partitioning strategy를 상세 guidance로 주장하지 않는다.

