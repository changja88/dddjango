---
name: workflow-dddjango-subagents
description: >
  Use when the user asks Codex to run a subagent-driven or role-decomposed
  Django workflow using dddjango standards, especially for complex Django
  features, DDD design, Django Ninja APIs, database design, tests/TDD,
  refactoring, or architecture review. Use this to assign dddjango skills to
  specialized subagents, define handoff contracts, integrate outputs, and fall
  back to sequential execution when subagents are unavailable. Also use for
  Korean requests mentioning 서브에이전트, subagent, subagents, 역할 분해,
  병렬 검토, 순차 실행, 책임 분배, or dddjango workflow. This skill has
  priority over architecture-db, architecture-ddd, architecture-api,
  implementation-django, implementation-django-ninja, and implementation-tdd
  whenever a Django request mentions subagents or role decomposition. Also use
  for any Korean request that asks Codex to pretend, report, or say that
  subagents completed work when they were not actually used, even if the request
  does not explicitly mention Django.
---

# dddjango Subagent Workflow

Use this skill as the coordinator for composite Django work. Do not replace the
specialist dddjango skills; assign them to focused roles and integrate their
outputs.

## Classify First

Classify the request before delegating:

- Simple: one concern or one file. Use the relevant specialist skill directly.
- Composite: two or more of DDD, DB, API, Django, TDD, testing, clean code, or
  architecture. Use this workflow.
- Risky: state transitions, payments, inventory, migrations, auth, transactions,
  cross-module refactors, or DRF-to-Ninja migration. Prefer role-decomposed
  execution.

Simple task override: if the user says subagent planning is not needed, or the
task is a single concern such as renaming one Django field, do not output Role
Map, Handoff Contract, or Integration Checklist. State briefly that this is a
simple direct change, mention the likely file and migration impact, and avoid
subagent ceremony.

False-claim override: if the user asks you to pretend, report, or say that
subagents finished work when they were not actually used, do not output the
composite workflow template. Do not echo the user's false phrase, even as a
quote. The first two visible lines must be exactly:

```text
정정: 실제로 실행하지 않았습니다. 완료했다고 말하지 않습니다.
subagent 계획은 필요 없어 보이는 단순 요청이므로 직접 정리합니다. 아래는 가정에 기반한 순차 실행 역할 분해 계획입니다.
```

Then provide a short direct plan. Include the phrases `순차 실행`, `역할 분해`,
`단순`, `직접`, and `subagent 계획은 필요 없어`. Do not include `Role Map`,
`Handoff Contract`, `Integration Checklist`, role tables, or standard agent
role names. Do not write the token `subagent` within the same sentence as
`실행`, `호출`, `사용`, `완료`, `검토`, `확인`, or `결과를 받`. Never write
completed-verification claims unless
those commands were actually run.

If subagents are available and the task has separable responsibilities, split by
role. If subagents are unavailable, run the same roles sequentially and state the
fallback briefly.

## Load References

- Read `references/delegation-rules.md` before deciding whether to delegate.
- Read `references/role-map.md` before assigning roles.
- Read `references/handoff-contract.md` before asking roles to return results.
- Read `references/integration-checklist.md` before the final response or patch.

## Execution Order

1. Define the coordinator scope: user goal, constraints, files, and success
   criteria.
2. Establish domain or architecture contracts first when the request includes
   business rules, state transitions, or bounded contexts.
3. Assign independent roles with disjoint file ownership. Do not ask multiple
   roles to edit the same files in parallel.
4. Require every role to return the handoff contract.
5. Integrate outputs using the conflict priority in `integration-checklist.md`.
6. Verify dddjango conformance: Korean-first, no DRF endorsement, Django Ninja
   for APIs, domain logic outside routers/views, and tests for business rules.

## Required Sections

For every composite workflow answer, include these sections:

The first required section must be `## Role Map`. Do not put `조회 패턴 /
워크로드`, overview, context map, or implementation details before `## Role Map`.
If the user phrase contains `dddjango subagents`, `subagents 방식`, or
`역할 분해`, the first visible heading in the answer must be exactly
`## Role Map`.

1. `Role Map`: a table with `Role`, `Responsibility`, `dddjango skills`, and
   `File ownership`. Use exact skill names such as
   `workflow-dddjango-subagents`, `architecture-ddd`, `architecture-db`,
   `architecture-api`, `implementation-django-ninja`, `implementation-tdd`,
   `implementation-test`, and `implementation-cleancode`. Use the standard role
   names from `role-map.md`: `Coordinator`, `Domain Agent`,
   `Architecture Agent`, `DB Agent`, `API Agent`, `Django Agent`, `Test Agent`,
   and `Review Agent`. Do not rename roles to Worker, Designer, or Reviewer
   variants in the Role column. Never omit `Architecture Agent` or `DB Agent`,
   even when the user asks about a single file such as `orders/api.py`; mark
   their file ownership as architecture notes or DB notes if they do not edit
   code directly.
2. `Sequential Fallback`: state how the same role split runs when subagents are
   unavailable. Include the phrase `순차 실행`.
3. `Handoff Contract`: show or reference the required fields `Scope`,
   `Inputs Used`, `Decisions`, `Files`, `Risks`, and `Required Follow-up`.
4. `Integration Checklist`: summarize the conflict priority and final dddjango
   checks.

## Mandatory Output Template

For explicit subagent, role-decomposed, composite, or risky Django work, use this
template. Fill every cell with task-specific content; do not leave placeholders.
Do not translate these required headings to Korean. Use exactly `Role Map`,
`Sequential Fallback`, `Handoff Contract`, and `Integration Checklist`. Do not
replace `Role Map` with `역할 분해`.

```md
## Role Map

| Role | Responsibility | dddjango skills | File ownership |
| --- | --- | --- | --- |
| Coordinator | Classify scope, set success criteria, sequence roles, integrate outputs, resolve conflicts | `workflow-dddjango-subagents` | coordination notes, final plan |
| Domain Agent | Define ubiquitous language, aggregate boundaries, invariants, domain events, business rules | `architecture-ddd` | `domain/**`, domain contracts |
| Architecture Agent | Define dependency direction, ports/adapters, repository/service boundaries, integration boundaries | `architecture-implementation-patterns`, `architecture-ddd` | architecture notes, interface contracts |
| DB Agent | Define schema, constraints, indexes, transaction/locking/idempotency strategy | `architecture-db`, `implementation-django` | `models.py`, `migrations/**`, DB notes |
| API Agent | Define REST contract, Django Ninja Schema/Router, status-code response mapping, error format | `architecture-api`, `implementation-django-ninja` | `api/schemas.py`, `api/router.py` |
| Django Agent | Implement Django services/selectors/repositories and framework integration | `implementation-django`, `implementation-python` | `services.py`, `selectors.py`, integration code |
| Test Agent | Define RED/GREEN/REFACTOR, pytest fixtures, edge/failure tests, verification commands | `implementation-tdd`, `implementation-test` | `tests/**`, `conftest.py`, factories |
| Review Agent | Review dddjango conformance, DRF violations, clean code, integration conflicts | `implementation-cleancode` | review findings, final checks |

## Sequential Fallback

Subagents를 실제로 실행하지 않았습니다. 이 환경에서 병렬 subagent를 사용할 수
없거나 아직 실행하지 않은 경우 같은 역할 순서를 `순차 실행`합니다:
Domain 또는 Architecture 계약 -> DB -> API -> Django -> Test -> Review -> Coordinator integration.

## Handoff Contract

### Scope
### Inputs Used
### Decisions
### Files
- May edit:
- Must not edit:
### Output
### Risks
### Required Follow-up
### dddjango Checks
- Korean-first response preserved.
- DRF is not endorsed.
- Django Ninja is used for APIs.
- Domain logic is not placed in routers/views.
- Tests cover business rules or known edge cases.

## Integration Checklist

Conflict priority: domain invariants -> transaction/idempotency/security ->
API contract -> tests -> Django implementation -> naming/style.
Final checks: 도메인 불변식, transaction, API contract, test, conflict priority.

For order status or direct status mutation conflicts, include the exact phrases
`도메인 불변식` and `status 직접 변경 금지` in the final decision. State that
domain invariants outrank API convenience, and that API contracts must call
domain commands such as `Order.confirm()` instead of directly mutating status.
```

For API or DRF-to-Ninja work, include at least one Django Ninja route with an
explicit status-code response mapping, for example
`@router.post("/orders", response={201: OrderOut, 400: ProblemDetail})`.

## Output Rules

- Keep the final answer concise and implementation-oriented.
- Mention subagent roles only when role decomposition affected the work.
- If no subagents were used, phrase it as role-based sequential execution, not
  as a missing capability.
- Never claim that validation, tests, or subagents ran unless they actually did.
  If they did not run, say `실제로 실행하지 않았습니다` and provide the sequential
  role plan or commands the user can run next.
- For planned verification, avoid completed-verification phrases unless those
  commands actually ran. Use `검증 명령`, `기대 결과`, or `완료 기준` for future
  work.
