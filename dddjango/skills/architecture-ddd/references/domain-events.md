# Domain Events And Consistency

Load this when state changes should produce events, multiple aggregates or contexts must react, external side effects exist, or event sourcing/saga is being considered.

## Domain Events

- Name events in past tense using domain language.
- Raise events from aggregate behavior after a meaningful business fact occurs.
- Collect events inside the aggregate or unit of work boundary; do not publish directly from random application code.
- Include enough identity and facts for consumers without leaking the whole aggregate state.

## Dispatch Timing

Always state dispatch timing when events affect consistency:

- Before commit: handlers participate in the same transaction and failure should roll back the operation.
- After commit: external side effects happen only after durable state exists.
- Outbox-style handoff: store the event/message with the state change, then publish asynchronously for reliable integration.

If payment, notification, message publishing, or another external effect is involved, do not leave timing implicit.

## Cross-Aggregate Consistency

- One transaction should usually modify one aggregate.
- If another aggregate must react, prefer a domain event and eventual consistency unless there is a strong local transaction reason.
- If the operation is a risky write, hand off transaction, idempotency, locking, and replay details to `architecture-db` and `architecture-api`.

## Event Sourcing And Saga

- Event sourcing is a modeling choice where state can be rebuilt from an event log. Use it only when audit/history/replay is central enough to justify the complexity.
- Saga coordinates long-running or distributed business transactions with compensating actions.
- Compensation must be idempotent.
- Detailed event store, outbox processor, and saga orchestration implementation belongs to `architecture-implementation-patterns` after the domain decision is made.

## Integration Events

- Domain events are internal to a bounded context.
- Integration events cross context boundaries and should use the published language of the integration contract.
- Translate external events through an anticorruption layer when the upstream language conflicts with the downstream model.
