# architecture-implementation-patterns Rubric

## Skill Scope

`architecture-implementation-patterns`는 DDD/domain decisions를 구현 구조로 옮길 때 필요한 architecture pattern 선택을 담당하는 스킬이다. 평가 대상은 layered architecture, clean/hexagonal/onion architecture, ports/adapters, repository, unit of work, CQRS, event sourcing, outbox, dependency inversion, anti-corruption layer, dependency direction, and non-use decisions.

책임 경계:

- 하위 도메인, bounded context, aggregate, invariant 발견은 `architecture-ddd`가 먼저 담당한다.
- DB schema/constraint/index/isolation은 `architecture-db`가 담당한다.
- REST contract는 `architecture-api`가 담당한다.
- Django/Python concrete implementation은 implementation skills가 담당한다.
- 단순 CRUD에 repository/UoW/interface/hexagonal architecture를 기본값으로 강제하지 않는다.

## Source Status

provisional

Dedicated implementation-patterns source reference is not yet available. Fallback sources:

- `workspace/docs/spec.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/architecture-ddd/reference/final.md`
- `workspace/reference/implementation-django/reference/final.md`
- `workspace/reference/implementation-python/reference/final.md`

The rubric must not present pattern guidance as fully sourced beyond these fallback boundaries.

## Trigger Examples

- "결제 승인 유스케이스에 hexagonal architecture, repository, outbox를 적용해야 하는지 판단해줘."
- "외부 배송사 모델을 내부 주문 도메인에 오염시키지 않도록 ACL을 둬야 할지 봐줘."
- "Django 프로젝트에서 service/repository/port adapter 경계를 어디까지 둘지 정해줘."
- "CQRS나 event sourcing이 이 조회/쓰기 모델에 필요한지 판단해줘."
- "의존성 방향과 infrastructure adapter 소유권을 정리해줘."

## Anti-Trigger Examples

- "주문 aggregate와 invariant를 먼저 설계해줘." -> `architecture-ddd`
- "주문 테이블 index와 transaction isolation을 설계해줘." -> `architecture-db`
- "주문 생성 API status code와 Problem Details를 설계해줘." -> `architecture-api`
- "Django model/service 코드를 구현해줘." -> `implementation-django`
- "단순 CRUD model을 만들어줘." -> direct implementation skill; no pattern ceremony
- "테스트 fixture를 작성해줘." -> `implementation-test`

## Skill-Specific Hard Gates

- **Provisional misrepresentation**: claims a dedicated implementation-patterns source exists or hides fallback-source limitation.
- **Pattern cargo cult**: applies repository/UoW/hexagonal/CQRS/event sourcing/outbox without scenario evidence of complexity, replacement need, external boundary, scale, or consistency risk.
- **Strategy skipped**: chooses tactical architecture before DDD boundary/invariant/usecase is known when the prompt is domain-heavy.
- **Dependency direction violation**: core domain/application policy directly depends on SDK, HTTP, framework adapter, filesystem, or volatile infrastructure without justification.
- **Unsafe external side effect**: external payment/notification/event publish pattern lacks post-commit/outbox/domain-event timing when consistency risk exists.
- **Workflow over-application**: small Django implementation task receives full pattern architecture.
- **Verification honesty**: claims architecture review/subagent validation without evidence.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Implementation Pragmatism**: 5 when pattern use/non-use is justified by domain complexity, change axis, external boundary, testability, and Django cost.
- **Domain Reasoning**: 5 when pattern decisions preserve aggregate/invariant and bounded context decisions from `architecture-ddd`.
- **Maintainability**: 5 when dependency direction and abstractions reduce real coupling without creating shallow layers.
- **Data And API Consistency**: applicable for outbox/CQRS/event sourcing/external API cases; 5 requires transaction and contract implications.
- **Workflow Fit**: 5 when simple cases skip architecture ceremony and composite/risky cases get handoff-ready structure.
- **Skill Design And Progressive Disclosure**: applicable for skill-authoring; 5 requires provisional status and fallback reference boundaries.

Score 1 if the output recommends a clean/hexagonal architecture template without explaining why the current problem needs it.

## Reference-Derived Additions

Required reference coverage:

- DDD strategic/tactical decisions come before implementation architecture pattern selection.
- Django model/service/query patterns can be sufficient for simple or supporting domains.
- Repository/UoW is useful only when domain collection abstraction, persistence replacement, or test isolation benefit outweighs wrapper cost.
- Ports/adapters/hexagonal patterns fit volatile external systems and domain protection, not every app.
- ACL protects internal language from external/legacy model pollution.
- Outbox/domain event timing is required for external side effects tied to committed state.
- CQRS/event sourcing require clear read/write asymmetry, audit/history, or event reconstruction needs; they are not default complexity.

## Required Public Fixtures

Positive prompt:

```text
결제 승인 유스케이스에 hexagonal architecture, repository, anti-corruption layer, outbox를 적용해야 하는지 판단해줘. 외부 결제사 SDK와 트랜잭션 경계도 고려해줘.
```

Negative prompt:

```text
단순 상품 카테고리 CRUD를 Django 모델과 기본 admin으로 처리하려고 해. repository와 hexagonal architecture까지 꼭 넣어야 해?
```

Additional public fixtures may include current package structure, external SDK code, domain model notes, transaction flow, or event publishing code. Public materials must not expose expected pattern decisions, hidden scoring notes, or private failure criteria.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `architecture-implementation-patterns`; also `architecture-ddd` if domain boundaries are missing and `architecture-db`/`implementation-django` for transaction implementation follow-up.
- Negative prompt: answer should recommend minimal Django structure and reject unnecessary pattern ceremony.

Expected answer evidence:

- Pattern decisions include apply/not-apply reasons.
- External SDK/legacy model risk leads to port/adapter or ACL only when justified.
- Outbox/post-commit event timing is considered for external side effects.
- Dependency direction keeps core policy away from infrastructure.
- Provisional source status is explicit in skill/rubric evaluation contexts.

Failure criteria:

- Blanket "use repository/UoW/hexagonal for DDD" recommendation.
- Domain/application layer directly imports volatile SDK without adapter discussion in a scenario that requires isolation.
- External side effect timing omitted for payment/event flow.
- Public eval material leaks the expected pattern decision.
- Dedicated source status is misrepresented.

Applicable hard gates: `Provisional misrepresentation`, `Workflow over-application`, `Unsafe external side effect`, `Scenario-required consistency decision missing` for risky writes, plus pattern-specific gates above.

## Reference Loading Expectations

- Load product docs and `workspace/docs/reference-index.md` to confirm provisional status.
- Load `workspace/reference/architecture-ddd/reference/final.md` for domain boundary, aggregate, context, and event criteria.
- Load `workspace/reference/implementation-django/reference/final.md` for Django service/model pragmatism.
- Load `workspace/reference/implementation-python/reference/final.md` for Protocol and boundary typing only when needed.
- Load DB/API references only when the pattern decision affects transaction/schema/API contracts.

## Raw Artifact Checklist

- Existing architecture/package boundaries or proposed module map.
- Pattern decision table with apply/not-apply reasons.
- Dependency direction notes and port/adapter ownership.
- External system/ACL/outbox/event timing notes when applicable.
- Risks, trade-offs, and follow-up ownership for DB/API/Django/Test roles.
- Explicit "Not run" or "review not executed" status for claimed validation.

## Scenario Tags

Primary tags: `architecture-patterns`, `ddd`, `risky-write`, `concurrency`, `review`, `provisional`, `negative-simple`.

Usually N/A unless combined with implementation: `django-ninja`, `django-web`, `migration`, `runtime`, `skill-folder`.

## Do Not Penalize

- Rejecting repository, UoW, CQRS, event sourcing, or hexagonal architecture when scenario complexity does not justify them.
- Keeping Django-native service/model structure for simple or supporting domains.
- Deferring aggregate discovery back to `architecture-ddd`.
- Using direct concrete dependencies for stable local helpers.
- Stating source limitations instead of pretending complete pattern reference coverage.
