수정 대상: reference
원인 분류: P3 source boundary stale split wording
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# architecture-ddd P3 reference 후속 분석

## 평가 대상

- source reference: `workspace/reference/architecture-ddd/reference/final.md`
- dedicated implementation-patterns source: `workspace/reference/architecture-implementation-patterns/reference/final.md`
- runtime skill: `dddjango/skills/architecture-ddd/SKILL.md`

## Finding

### Reference Major 1, 후속 작업으로 분류

- `architecture-ddd` source reference의 `아키텍처`, `구현 패턴`, `의사결정 요약` 구간이 layered/DIP, hexagonal, CQRS, package structure, Data Mapper, Repository/UoW 같은 implementation-pattern 결정을 아직 넓게 포함한다.
- 같은 결정을 전담하는 `workspace/reference/architecture-implementation-patterns/reference/final.md`가 이미 존재하며, 해당 문서는 구현 구조, dependency direction, ports/adapters, repository, UoW, CQRS, event sourcing, saga, outbox, ACL, service layer 선택 기준을 전용 source로 제공한다.
- 따라서 source-authoring 기준에서는 `architecture-ddd` source reference와 `architecture-implementation-patterns` source reference 사이의 경계 정리가 필요하다.

### Reference Minor 1, 후속 작업으로 분류

- `workspace/reference/architecture-ddd/reference/final.md`에는 implementation-pattern 세부 설명을 향후 분리하고 그 전까지 fallback 기준을 따른다는 문장이 남아 있다.
- 현재 dedicated source가 존재하므로 해당 wording은 stale 상태다.

## P3 skill 반영 판단

- Runtime `architecture-ddd` skill은 이미 implementation pattern 질문을 `architecture-implementation-patterns`로 넘기고, risky write에서도 repository/UoW, outbox, saga, ACL, transaction-owner structure를 `architecture-implementation-patterns`로 handoff한다.
- 이 gap은 runtime skill에 더 많은 source 내용을 넣어 해결할 문제가 아니라 source reference 정리 작업이다.
- 이번 P3에서는 `architecture-ddd` skill을 억지로 넓히지 않고 reference 후속 작업으로 분류한다.

## 후속 수정 범위 제안

- `workspace/reference/architecture-ddd/reference/final.md`에서 implementation-pattern 전용 세부 결정을 축약하거나 cross-reference 역할로 낮춘다.
- stale `향후 분리` 및 fallback 문구를 현재 dedicated source 존재에 맞게 갱신한다.
- `architecture-implementation-patterns` source와 충돌하지 않도록 DDD source는 strategic design, bounded context, aggregate, invariant, domain event, consistency boundary 중심으로 정리한다.

## Subagent 리뷰/순차 fallback

- 독립 P3 audit real-subagent가 source reference Major 1, Minor 1을 보고했다.
- 메인 판단은 이 결과를 runtime skill blocker로 채택하지 않고 reference 후속 분류로 채택한다.
- `skill-creator` 관점 real-subagent는 runtime skill progressive disclosure와 source/runtime cache parity를 통과로 보았다.

## 완료 판단

- P3 skill 작업에서는 reference gap을 숨기지 않고 후속 분석으로 분류했다.
- reference 자체 수정은 별도 reference 개선 작업에서 수행한다.
