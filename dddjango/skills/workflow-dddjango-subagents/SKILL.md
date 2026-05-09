---
name: workflow-dddjango-subagents
description: >
  Use for role-decomposed dddjango workflows in composite or risky Django/DDD work spanning domain rules, DB, API, implementation, tests, or review; also use when the user asks for subagents, subagent/subagents, 서브에이전트, 역할 분해, 역할 맵, 병렬 검토, 책임 분배, 순차 실행, handoff/핸드오프, 통합 체크리스트, 검증 분담, 위험 작업, or dddjango workflow. Do not use for simple single-file changes, small field renames, short explanations, or when the user opts out of subagent planning.
---

# dddjango Workflow

Use this skill to coordinate complex dddjango work across domain, architecture, DB, API, Django, test, and review responsibilities. Real subagents may be used only when actually available and explicitly requested or clearly authorized by the user; otherwise keep the same role order as a sequential fallback.

## Routing

- Use this first when the user explicitly asks for subagents, role decomposition, parallel review, responsibility split, sequential fallback, handoff, or dddjango workflow.
- Use this for composite Django/DDD work where two or more of domain modeling, implementation patterns, DB schema/transactions, REST API contract, Django/Python implementation, tests/TDD, or review are genuinely coupled.
- Use this for risky Django/DDD work involving 주문, 결제, 재고, 예약, 환불, 권한, ledger, or similar domains when state transition, transaction, schema, API, or test impact is present.
- Do not force this workflow for a simple single-file change, small field rename, local CRUD edit, short explanation, or already-decided implementation task.
- If a simple task asks for decorative workflow ceremony such as a Role Map, avoid the full workflow unless multiple real responsibilities are involved.
- If the user says `subagent 계획은 필요 없어` or otherwise opts out, do not output a full role map; proceed with the most relevant implementation or architecture skill.
- If the user asks you to say subagents completed work without actually running them, refuse that claim and report the actual execution status.

## Reference Loading

- Read [delegation-rules.md](references/delegation-rules.md) for when to use real subagents, when to run sequential fallback, and when to avoid role decomposition.
- Read [role-map.md](references/role-map.md) for the canonical roles, responsibilities, and related skills. Do not shrink this role map.
- Read [handoff-contract.md](references/handoff-contract.md) for required handoff fields and file ownership format.
- Read [integration-checklist.md](references/integration-checklist.md) for integration priority, risky write consistency, validation honesty, and cache sync reporting.

## Canonical Roles

| Role | Responsibility | Related skills |
|---|---|---|
| Coordinator | Work scope, role assignment, result integration | `workflow-dddjango-subagents` |
| Domain Agent | Subdomain, context, language, aggregate, invariant, domain event | `architecture-ddd` |
| Architecture Agent | Implementation pattern, dependency direction, port/adapter, transaction boundary | `architecture-implementation-patterns` |
| DB Agent | Schema, constraints, indexes, transactions, rollout constraints, backfill/index-lock risk | `architecture-db`, `implementation-django` |
| API Agent | REST contract, status code, Problem Details, OpenAPI | `architecture-api`, `implementation-django-ninja` |
| Django Agent | ORM, service, selector, concrete migration files, transaction, settings/security/performance, template/static/web, templates/static files | `implementation-django`, `implementation-django-web`, `implementation-python` |
| Test Agent | TDD flow, pytest, fixtures, test doubles, API/integration tests, ownership of `tests/**` files | `implementation-tdd`, `implementation-test` |
| Review Agent | Code quality, design risk, missing verification, regressions | `implementation-cleancode` |

## Output Shape

For composite or risky implementation/planning workflow answers, the first visible heading must be `## Role Map`, followed by `## Sequential Fallback`, `## Handoff Contract`, and `## Integration Checklist`. Shorten the content inside those sections if needed, but do not remove the sections.

For review-focused work, findings must lead, ordered by severity with evidence. If the review also needs coordinated workflow output, include `## Role Map`, `## Sequential Fallback`, `## Handoff Contract`, and `## Integration Checklist` after the findings instead of before them.

`Handoff Contract` must include `Scope`, `Inputs Used`, `Decisions`, `Files` with `May edit` and `Must not edit`, `Output`, `Risks`, `Required Follow-up`, and `dddjango Checks`.

For risky writes, `## Integration Checklist` must include a visible `Risky Write Consistency Block` section or table with transaction owner, locking strategy, uniqueness or idempotency storage, `Idempotency-Key` API behavior, external side-effect timing, isolation/retry decision, and integration or concurrency test criteria. If a decision is outside the current role, assign it to the responsible role rather than omitting it.

If actual subagents are used, list their role, task, and result. If subagents are not used, say the workflow was executed sequentially or planned only; never imply a review or implementation happened in a subagent when it did not. Include a Cache sync report when plugin cache outside the workspace was edited, naming the cache path and workspace canonical source.

## Runtime Rules

- Start by deciding whether the work is simple, DDD-focused, composite, risky, or review-focused.
- Let Domain decisions guide DB, API, Django, and Test decisions.
- Use real subagents only for concrete, bounded, parallelizable tasks with honest handoff; do not delegate the immediate critical-path blocker when you need it locally.
- Keep file ownership explicit in handoffs with `May edit` and `Must not edit`.
- Preserve the role order in sequential fallback: Domain, Architecture, DB, API, Django, TDD/Test, Review, Integration.
- For risky writes, include the `Risky Write Consistency Block` decisions or assign the missing decisions to the responsible role.
- Final integration must close each role's risks and required follow-up or explicitly leave them unresolved.
- If plugin cache outside the workspace was edited, report the Cache sync report with the workspace canonical source mapping.
- Report only tests, validation, review, browser checks, or subagent work that was actually executed. If not executed, say so.
