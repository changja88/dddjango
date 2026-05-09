# architecture-ddd Rubric

## Skill Scope

`architecture-ddd`는 DDD/domain modeling 판단을 담당하는 스킬이다. 평가 대상은 subdomain classification, bounded context, context map, ubiquitous language, aggregate, entity, value object, invariant, domain service, domain event, consistency boundary, and usecase candidates.

책임 경계:

- DB schema, constraints, indexes, isolation, rollout risk는 `architecture-db`가 담당한다.
- REST resource/status/error/OpenAPI 계약은 `architecture-api`가 담당한다.
- Django model/migration/service/Router/template implementation은 implementation skills가 담당한다.
- 전략 설계 없이 entity/repository/service 같은 전술 패턴을 먼저 강제하지 않는다.
- 단순 CRUD 또는 supporting domain에 풍부한 DDD 구조를 강제하지 않는다.

## Source Status

ready

Canonical sources:

- `workspace/docs/spec.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/workflow.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/architecture-ddd/reference/final.md`

## Trigger Examples

- "주문 생성 유스케이스를 DDD 기준으로 모델링해줘."
- "이 도메인의 bounded context와 context map을 정리해줘."
- "쿠폰 정책의 aggregate, value object, invariant를 판단해줘."
- "도메인 이벤트를 써야 하는지, dispatch timing과 consistency boundary를 정해줘."
- "Core/Supporting/Generic 하위 도메인별 구현 강도를 판단해줘."

## Anti-Trigger Examples

- "주문 테이블의 index와 unique constraint를 설계해줘." -> `architecture-db`
- "주문 생성 REST endpoint의 status code를 정해줘." -> `architecture-api`
- "Django model과 migration을 구현해줘." -> `implementation-django`
- "Ninja Router와 Schema를 만들어줘." -> `implementation-django-ninja`
- "pytest fixture를 작성해줘." -> `implementation-test`
- "Django Ninja Router가 무엇인지 짧게 설명해줘." -> direct short answer; no DDD workflow

## Skill-Specific Hard Gates

- **Strategy skipped**: tactical patterns are proposed before subdomain, bounded context, or ubiquitous language judgment when scenario requires DDD.
- **DDD over-application**: simple CRUD/supporting-domain prompt receives heavy aggregate/repository/event architecture without need.
- **Aggregate invariant missing**: aggregate is named but the protected invariant and transaction consistency boundary are absent.
- **Context language collapse**: different bounded-context meanings are forced into one shared model without trade-off.
- **Event timing missing**: domain/integration event proposal omits internal vs external event, commit timing, and outbox/eventual consistency judgment when relevant.
- **Business logic in adapter**: DDD output accepts core rules in API/view/template adapter as target architecture.
- **Verification honesty**: claims review/subagent/validation execution without evidence.
- **Workflow over-application**: simple non-domain prompt triggers full role map.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Domain Reasoning**: 5 when strategic design precedes tactical patterns and scenario facts drive subdomain/context/aggregate/invariant decisions.
- **Workflow Fit**: 5 when DDD is applied only where domain complexity warrants it and simple requests are routed elsewhere.
- **Implementation Pragmatism**: 5 when the model maps to Django/Python without forcing pure-domain separation by default.
- **Data And API Consistency**: applicable when domain decisions imply transaction/API/event constraints; 5 requires handoff to DB/API roles.
- **Test And Verification**: applicable when domain rules require executable specification; 5 identifies testable invariants and edge cases.

Score 1 if the answer lists DDD vocabulary without using scenario facts to make a concrete boundary or invariant decision.

## Reference-Derived Additions

Required reference coverage:

- Strategy before tactics: subdomain, bounded context, context map, ubiquitous language first.
- Core/Supporting/Generic subdomain classification changes implementation weight.
- Bounded context owns language; same word can have different meaning in different contexts.
- Context map relation and integration style are required when contexts interact.
- Aggregate protects a minimal invariant boundary and should avoid cross-aggregate transaction coupling by default.
- Value objects represent meaning and validation by value, not identity.
- Domain events are past-tense domain facts; event scope, dispatch timing, and outbox/eventual consistency are explicit when used.
- Application service coordinates flow; domain service is only for domain rules that do not fit an entity/value object.

## Required Public Fixtures

Positive prompt:

```text
주문 생성 유스케이스를 DDD 기준으로 설계해줘. 중복 요청 방지, 주문 상태 전이, 결제 승인 이후 이벤트도 고려해줘.
```

Negative prompt:

```text
관리자 화면의 단순 카테고리 CRUD 모델 이름만 정리해줘. 복잡한 DDD 설계는 필요 없어.
```

Additional public fixtures may include domain glossary, state transition notes, event examples, existing model snippets, or business rules. Public fixtures must not expose expected routing, hidden aggregate decisions, scoring keys, or private grader notes.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `architecture-ddd`; likely handoff to `architecture-db`, `architecture-api`, `implementation-django`, `implementation-tdd`, and workflow if full implementation is requested.
- Negative prompt: no DDD ceremony; route to simple implementation/clean-code handling.

Expected answer evidence:

- Subdomain type and implementation weight are stated.
- Bounded context and ubiquitous language are context-specific.
- Aggregate candidate includes invariant and transaction boundary.
- Event proposal includes internal/integration distinction and dispatch timing.
- Handoff questions for DB/API/Django/test are explicit when needed.

Failure criteria:

- Starts with repository/entity/service class structure before strategic design.
- Names aggregate without invariant.
- Forces generic/shared model across conflicting contexts.
- Proposes domain events without timing/consistency decision.
- Public eval packet leaks expected aggregate or routing.

Applicable hard gates: `Workflow over-application`, `Business logic in adapter`, `Scenario-required consistency decision missing` for risky writes, `Unsafe external side effect` when event/external effects are present, plus DDD-specific gates above.

## Reference Loading Expectations

- Load `workspace/reference/architecture-ddd/reference/final.md` for all DDD strategic/tactical judgment.
- Load `workspace/docs/ddd-implementation-standard.md` for Django mapping and subdomain implementation weight.
- Load `workspace/docs/workflow.md` only when request is composite/risky or asks for roles/subagents.
- Load DB/API/Django/Test references only after domain handoff questions are identified.

## Raw Artifact Checklist

- Domain terms and context-specific glossary.
- Subdomain classification and reasoning.
- Bounded context and context map relation.
- Aggregate/value object/entity/invariant list.
- Domain event list with timing and consistency notes.
- Usecase/application service responsibility candidates.
- Handoff notes to DB/API/Django/Test roles and explicit "Not run" status for any claimed review/validation.

## Scenario Tags

Primary tags: `ddd`, `risky-write`, `concurrency`, `test`, `review`, `negative-simple`.

Usually N/A unless combined with implementation: `django-ninja`, `django-web`, `migration`, `runtime`, `skill-folder`.

## Do Not Penalize

- Declining rich DDD patterns for simple CRUD or supporting subdomains.
- Using Django model as domain object when invariant complexity is low and behavior is explicit.
- Deferring schema, endpoint, or migration details to the correct architecture/implementation skill.
- Not using domain events when no cross-aggregate/context/external effect needs them.
- Marking unresolved domain questions as assumptions rather than pretending certainty.
