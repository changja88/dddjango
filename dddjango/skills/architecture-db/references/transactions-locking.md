# Transactions And Locking

Load this for ACID, isolation levels, concurrency anomalies, transaction boundaries, locking strategy, risky writes, and side-effect timing.

## ACID And Isolation

- Atomicity: all operations in the transaction succeed or all fail.
- Consistency: constraints and invariants remain valid.
- Isolation: concurrent transactions do not break assumptions.
- Durability: committed data survives failure.

Common phenomena:

- Dirty read: reads uncommitted data.
- Non-repeatable read: repeated row read changes within a transaction.
- Phantom read: repeated predicate read returns a different row set.
- Serialization anomaly: concurrent result cannot match any serial order.

## Isolation Choice

- Read Committed is a practical default for many OLTP systems, but each SQL statement sees a new snapshot.
- Repeatable Read helps consistent read workloads but may require retry behavior.
- Serializable maximizes correctness for critical finance/payment-like operations but can reduce concurrency and requires retry handling.

Choose the lowest isolation level that protects the invariant, then add explicit locking or constraints when needed.

## Locking And Consistency

- Prefer unique constraints for duplicate prevention when the invariant is uniqueness.
- Use optimistic locking when conflicts are rare and retry is acceptable.
- Use pessimistic locking when concurrent writers would otherwise corrupt a high-value invariant.
- Document deadlock, timeout, and serialization failure retry behavior when the strategy can fail under load.

## Risky Write Consistency

For order, payment, inventory, reservation, refund, permission, ledger, or similar risky writes, include a `Risky Write Consistency Block` and record:

- transaction owner;
- locking strategy;
- uniqueness or idempotency storage key, owner, location, and unique constraint;
- API `Idempotency-Key` replay/conflict behavior handoff to `architecture-api`;
- external side-effect timing such as Django `transaction.on_commit()`, domain event, or outbox;
- isolation level and retry decision;
- integration or concurrency test criteria.

## Side Effects

Do not run external payment, notification, SDK, or message publishing inside a DB transaction without a clear consistency reason. In Django, prefer `transaction.on_commit()` for local post-commit handoff, or use a domain event/outbox-style handoff when the side effect needs reliable cross-process delivery.
