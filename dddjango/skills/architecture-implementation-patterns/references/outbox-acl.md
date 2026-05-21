# Outbox, ACL, And Integration Patterns

Load this when domain events cross aggregate or context boundaries, external side effects exist, upstream models conflict with the domain, or event sourcing/saga is being considered.

## Domain Events And Integration Events

- Domain events are internal business facts raised by aggregate behavior.
- Integration events cross bounded context or service boundaries and should use the published language of the integration contract.
- Keep event names past tense and scoped to the language of the owning context.
- Do not expose internal aggregate structure as an integration event contract.

## Outbox

Use outbox when state change and message delivery must be reliably connected.

Decision points:

- What transaction writes the aggregate and the outbox message?
- Who owns dispatch after commit?
- Is delivery at-least-once, and are consumers idempotent?
- What retry/dead-letter behavior is needed?
- Which event fields form the published language?

For simple in-process follow-up after a successful Django transaction, `transaction.on_commit()` may be enough. For cross-service publication, prefer a durable outbox-style handoff.

## Event Sourcing

Use event sourcing only when history, audit, replay, or temporal reconstruction is central to the domain.

- Domain events do not imply event sourcing.
- Simple audit logs or integration notifications are not enough reason.
- Event schema evolution, projection rebuild, and replay operations must be explicit responsibilities.

## Saga

Use saga when a long-running or distributed business process spans multiple local transactions and the product accepts eventual consistency.

- Choreography keeps services autonomous but can hide the process flow.
- Orchestration centralizes the process but can concentrate workflow logic.
- Compensation must be explicit and idempotent.
- Product and operations criteria must tolerate eventual consistency between steps.

Do not use saga for a single local invariant that can be protected by one transaction.

## Anticorruption Layer

Use ACL to protect a downstream model from an upstream or legacy language.

- Translate external identifiers, statuses, units, and lifecycle concepts.
- Keep translation near the integration boundary.
- Do not let legacy terms leak into aggregates, value objects, or ubiquitous language.

## Risky Write Consistency Block Handoff

For payment, inventory, reservation, refund, permission, ledger, or similar risky writes, output a visible `Risky Write Consistency Block`. This skill owns the architecture pattern decision but should leave concrete DB/API/test details to the owning skills.

Record:

- transaction owner or owning use case;
- pattern decision: Django-native transaction, service layer, port/adapter, outbox, saga, ACL, or no extra pattern;
- side-effect timing: after commit, outbox, saga step, or another reliable handoff;
- whether uniqueness/idempotency storage is needed;
- follow-up owner for DB locking, isolation, and retry details;
- follow-up owner for `Idempotency-Key`, status code, and Problem Details API behavior;
- follow-up owner for integration, replay, or concurrency tests.
