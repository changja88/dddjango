# Integration Checklist

Load this before finalizing composite dddjango work.

## Integration Priority

Resolve conflicts in this order:

1. Domain invariants
2. Data consistency
3. Transactions and security
4. API contract and backward compatibility
5. Testability
6. Django/Python idioms
7. Names and style

## Checklist

- Domain and invariants: domain invariant, state transition, and ubiquitous language do not conflict with implementation, tests, or API.
- Data and transaction: DB constraints, transaction boundary, locking/idempotency, and migration rollout risk are handled or explicitly assigned.
- API contract: Django Ninja Router/Schema mapping, status codes, Problem Details, OpenAPI impact, and no greenfield DRF implementation are confirmed.
- Implementation mapping: domain logic is not owned by Router, view, schema, or template; Django service/selector/model boundaries are clear.
- Tests and verification: domain rules, API contract, and migration risks have tests or explicit not-run verification notes.
- Integration owner: the Coordinator or another named owner is responsible for collecting role results, resolving conflicts, and closing or carrying follow-up.
- Role handoff closure: each role's `Risks` and `Required Follow-up` are either closed or carried as unresolved by the integration owner.
- Cache sync report: if plugin cache outside the workspace was edited, report the cache path, matching workspace canonical source, and validation status. For `workflow-dddjango-subagents` role-map changes, use `workspace/docs/workflow.md` as the responsibility parity source and confirm runtime/cache role names, responsibility scope, and related skills did not shrink.

## Risky Write Consistency Block

For risky writes such as order, payment, inventory, reservation, refund, permission, or ledger, ensure the relevant roles provide:

- transaction owner;
- locking strategy;
- uniqueness or idempotency storage location;
- `Idempotency-Key` API behavior;
- external side-effect timing such as Django `transaction.on_commit()` or domain event handling;
- isolation/retry decision;
- integration or concurrency test criteria.

If a decision is outside the current role, assign it to the responsible role rather than omitting it.

## Validation Honesty

Report executed validation separately from planned or recommended validation. Never say tests, review, browser checks, or subagent work completed unless they actually ran.
