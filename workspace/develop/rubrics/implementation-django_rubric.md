# implementation-django Rubric

## Skill Scope

`implementation-django`는 확정되었거나 충분히 좁혀진 도메인/DB/API 판단을 Django 코드로 매핑하는 스킬이다. 평가 대상은 Django model, field, QuerySet, Manager, service, selector, concrete migration file, `RunPython`, `apps.get_model()`, `sqlmigrate`, transaction, settings/security/performance, Django 통합 테스트 acceptance criteria다.

책임 경계:

- `architecture-ddd`가 담당할 하위 도메인, bounded context, aggregate, invariant 발견을 Django 구조부터 시작하지 않는다.
- `architecture-db`가 담당할 schema, index, constraint, isolation, rollout 판단을 ORM convenience로 대체하지 않는다.
- `architecture-api`와 `implementation-django-ninja`가 담당할 REST 계약, Router, Schema, Problem Details 구현을 소유하지 않는다.
- `implementation-django-web`이 담당할 template/static/UI 구현을 소유하지 않는다.
- 핵심 비즈니스 규칙을 view, form, serializer/schema, signal에 흩어놓지 않는다.

## Source Status

ready

Canonical sources:

- `workspace/docs/spec.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/workflow.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/implementation-django/reference/final.md`

DRF 내용은 legacy review, migration, comparison, compatibility 맥락에서만 참조한다. 신규 API 구현 기준으로 사용하면 실패다.

## Trigger Examples

- "Django 모델에 주문 상태 필드를 추가하고 migration까지 작성해줘."
- "Order QuerySet을 N+1 없이 최적화하고 selector/service 기준으로 정리해줘."
- "운영 중인 테이블에 nullable 컬럼을 추가한 뒤 backfill, NOT NULL, index를 적용하는 Django migration을 만들어줘."
- "Django service에서 `transaction.atomic()`과 `transaction.on_commit()`을 어떻게 배치할지 구현해줘."
- "도메인 판단은 끝났고 Django model/service 코드로 옮겨줘."

## Anti-Trigger Examples

- "주문 도메인의 bounded context와 aggregate를 설계해줘." -> `architecture-ddd`
- "주문 테이블의 unique constraint와 locking 전략을 설계해줘." -> `architecture-db`
- "주문 생성 REST endpoint의 status code와 오류 계약을 설계해줘." -> `architecture-api`
- "Django Ninja Router와 Schema를 구현해줘." -> `implementation-django-ninja`
- "TemplateView 기반 주문 상세 페이지와 static 구조를 만들어줘." -> `implementation-django-web`
- "Python dataclass/Enum으로 상태 전이를 표현해줘." -> `implementation-python`
- "Order 모델이 너무 커졌는지 리뷰해줘." -> `implementation-cleancode` plus `architecture-ddd` when domain boundaries matter

## Skill-Specific Hard Gates

- **Business logic in adapter**: target implementation puts core rules in view, Router, form, schema, signal, or template instead of model/usecase/service/domain boundary.
- **Operational migration safety missing**: production migration cases omit expand/migrate/contract, rolling deploy compatibility, or DB/Django responsibility split.
- **Scenario-required consistency decision missing**: risky write cases omit transaction owner, locking/idempotency, side-effect timing, isolation/retry, or test criteria.
- **Unsafe external side effect**: payment, notification, external API call, or event publish is executed before commit without `transaction.on_commit()`, outbox, or equivalent post-commit plan.
- **Greenfield DRF violation**: new API implementation is routed to DRF Serializer/ViewSet/APIView instead of Django Ninja.
- **Workflow over-application**: simple Django field rename or small model edit triggers full DDD role workflow despite no domain uncertainty.
- **Verification honesty**: claims migrations/tests/lint/sqlmigrate were executed without command evidence.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Implementation Pragmatism**: 5 when the answer chooses Django-native model/query/service/migration structure that is proportional to domain complexity and existing project shape.
- **Data And API Consistency**: 5 when model constraints, migrations, transactions, and API implications are aligned without moving API design into this skill.
- **Test And Verification**: 5 when Django integration/API acceptance criteria and executed/not-run status are explicit.
- **Maintainability**: 5 when responsibility split follows change reasons, not file size or blanket service-layer rules.
- **Domain Reasoning**: applicable only when the implementation contains domain rules; 5 requires preserving aggregate/invariant decisions from the input or escalating to `architecture-ddd` when absent.
- **Workflow Fit**: 5 when simple Django work is handled directly and composite/risky work is routed to workflow or architecture skills only when needed.

Score 1 if the output starts from framework folders and never connects to the relevant invariant, migration risk, or transaction boundary.

## Reference-Derived Additions

Required reference coverage:

- Django design philosophy: loose coupling, less code, explicitness, model encapsulation.
- Model method vs service/usecase choice based on invariant complexity and change reason.
- QuerySet/Manager/selector usage for query reuse and N+1/performance control.
- Migration safety: expand/backfill/contract, `RunPython` with historical models, `sqlmigrate` or equivalent review when relevant.
- Transaction mapping: usecase-owned `transaction.atomic()`, commit-after side effects, concurrency/idempotency choices for risky writes.
- Security/performance checks when touching settings, auth, permissions, query shape, caching, or external input.
- Django tests: ORM/transaction/constraint/query behavior is integration-tested when unit tests are insufficient.

Do not copy long Django reference prose into eval materials. The grader checks whether these judgments appear in the artifact decisions.

## Required Public Fixtures

Positive prompt:

```text
Order에 status 컬럼을 추가하고 기존 데이터 backfill 후 NOT NULL과 index를 적용하는 Django migration을 구현해줘. 운영 배포 중 호환성도 고려해줘.
```

Negative prompt:

```text
Order 모델의 memo 필드를 note로 바꾸는 작은 Django 수정만 해줘. subagent 계획은 필요 없어.
```

Additional public fixtures may include existing `models.py`, migration files, failing test output, query count output, or service code. Public fixtures must not reveal expected routing, scoring keys, hidden failure criteria, or the private answer.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `implementation-django`; also `architecture-db` if schema/rollout decisions are not already specified.
- Negative prompt: `implementation-django` direct handling; no full workflow, no role map.

Expected answer evidence:

- Positive case includes expand/migrate/contract plan or migration sequence, historical model use for data migration, rollback/rolling deploy notes, DB constraint/index timing, and test/verification commands.
- Negative case keeps scope small, identifies migration impact, and avoids DDD/subagent ceremony.

Failure criteria:

- Missing required section from this rubric-derived eval packet.
- Core business rule moved into adapter/signal without justification.
- Production migration jumps directly to NOT NULL/index without rollout reasoning.
- Claims `pytest`, `sqlmigrate`, or migration execution without evidence.
- Uses DRF as greenfield implementation standard.
- Public eval packet exposes this expected routing or failure criteria.

Applicable hard gates: `Verification honesty`, `Operational migration safety missing`, `Scenario-required consistency decision missing` when risky writes are present, `Unsafe external side effect` when external effects are present, `Workflow over-application` for simple negative cases.

## Reference Loading Expectations

- Always load `workspace/docs/skill-contracts.md`, `workspace/docs/ddd-implementation-standard.md`, and `workspace/docs/reference-index.md` for rubric authoring or grader calibration.
- Load `workspace/reference/implementation-django/reference/final.md` for Django model, QuerySet, Manager, migration, transaction, performance, security, and test criteria.
- Load `workspace/reference/architecture-db/reference/final.md` only when schema/transaction/isolation judgment is not already supplied.
- Load `workspace/reference/architecture-ddd/reference/final.md` only when aggregate/invariant ownership is unclear.
- Do not use DRF reference sections as a source for new API implementation.

## Raw Artifact Checklist

- Relevant model/service/query/migration files or proposed diffs.
- Migration operation list and data migration strategy when applicable.
- `sqlmigrate`, `makemigrations --check`, `pytest`, query count, or equivalent command output when claimed.
- Test files or acceptance criteria for ORM, transaction, constraint, and migration behavior.
- Review findings with file/line evidence for refactoring/review cases.
- Explicit "Not run" list for commands not executed.

## Scenario Tags

Primary tags: `simple`, `db`, `migration`, `concurrency`, `risky-write`, `test`, `review`, `negative-simple`.

Usually N/A unless combined with other work: `django-ninja`, `django-web`, `composite-workflow`, `runtime`, `skill-folder`.

## Do Not Penalize

- Keeping domain behavior on a Django model when the invariant is simple and model methods make the rule explicit.
- Avoiding repository/UoW abstractions for straightforward QuerySet-backed work.
- Not producing a full DDD role map for a small field rename or single migration fix.
- Not adding property-based or mutation tests when scenario risk does not require them.
- Marking API Router, Schema, or template work as follow-up for the appropriate skill instead of implementing it here.
