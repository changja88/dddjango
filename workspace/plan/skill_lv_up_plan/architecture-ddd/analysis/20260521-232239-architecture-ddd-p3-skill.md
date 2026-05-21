수정 대상: skill
원인 분류: P3 responsibility handoff gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# architecture-ddd P3 skill 분석

## 평가 대상

- source skill: `dddjango/skills/architecture-ddd/`
- source reference: `workspace/reference/architecture-ddd/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/`
- 비교 대상 skill: `architecture-db`, `architecture-api`, `architecture-implementation-patterns`, `implementation-django`, `implementation-test`, `source-reference-audit`, `workflow-dddjango-subagents`

## P3 기준 평가

### Major 1, 해결됨

- `SKILL.md`는 DDD가 직접 소유하는 모델링 책임과 DB/API/Test handoff를 대부분 분리한다.
- 그러나 risky write runtime rule에서 transaction ownership, locking, idempotency storage, API behavior, isolation/retry, test criteria를 handoff하면서 `architecture-implementation-patterns`가 소유하는 pattern-level 선택을 명시하지 않는다.
- 이로 인해 outbox, saga, ACL, repository/UoW, transaction owner pattern 같은 구현 아키텍처 결정이 DDD skill, DB skill, workflow skill 사이에 흩어져 해석될 수 있다.
- source reference는 hexagonal, CQRS, repository/UoW, outbox, saga 세부 구현을 implementation-patterns reference로 분리해야 한다고 명시하므로, runtime skill도 같은 handoff를 드러내야 한다.

### Minor 0

- `SKILL.md`는 46줄로 500줄 미만이다.
- bundled reference 네 개는 모두 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- `SKILL.md`는 핵심 절차와 routing 중심이고 세부 DDD 설명은 bundled references에 있다.
- source reference 자체에는 implementation-pattern 전용 source가 생긴 뒤 stale boundary wording이 남아 있다. 이는 runtime skill blocker가 아니라 reference 후속 작업으로 분류했다.

## 수정 방향

- risky write rule에 `architecture-implementation-patterns` handoff를 명시한다.
- TDD sequencing 요청은 `implementation-tdd`로 넘기는 기준을 routing에 명시한다.
- DDD skill의 직접 책임은 invariant, aggregate, consistency boundary, domain event, side-effect timing의 domain-level decision으로 제한한다.
- concrete DB locking/isolation/idempotency storage, REST `Idempotency-Key` behavior, pytest mechanics, Django code는 기존 handoff를 유지한다.
- bundled reference와 source reference는 이번 수정 범위에서 변경하지 않는다.

## Subagent 리뷰/순차 fallback

- `skill-creator` 관점 real-subagent 리뷰: Blocker 0, Major 0, Minor 2, Note 5.
- 독립 P3 audit real-subagent 리뷰: runtime skill Blocker 0, Major 0, Minor 0, Note 5. Source reference Major 1, Minor 1은 `workspace/plan/reference_lv_up_plan/architecture-ddd/analysis/20260521-232239-architecture-ddd-p3-reference.md`로 후속 분류했다.
- 메인 판단: duplication risk는 현재 46줄의 핵심 runtime rule 수준이라 열린 Minor로 두지 않는다. TDD handoff Minor는 routing 문구 보강으로 닫았다.

## 재평가 결과

- `SKILL.md` risky write rule은 DDD-owned decision과 implementation-pattern, DB, API, Test/workflow handoff를 분리한다.
- `SKILL.md` routing은 domain rules가 clear한 TDD sequencing 요청을 implementation/TDD skill로 넘긴다.
- `SKILL.md`는 46줄로 500줄 미만이며 bundled references는 모두 1단계 직접 링크다.
- runtime cache sync 분석/계획을 작성하고 cache를 동기화했다.
