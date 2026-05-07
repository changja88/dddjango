# Integration Checklist

Use this before finalizing a role-decomposed answer or patch.

## Required Checks

- Domain terms from Domain Agent appear consistently in API, DB, and tests.
- Aggregate invariants are enforced outside routers/views.
- DB schema does not leak external API or payment-provider vocabulary into the
  domain model unless explicitly isolated by an anti-corruption layer.
- API uses Django Ninja Schema/Router and does not endorse DRF implementation.
- State transitions are modeled as explicit domain/application operations, not
  as arbitrary status-field mutation.
- Router/API handlers must call an application service or use case for state
  changes; they must not mutate aggregate status directly.
- Cross-aggregate side effects such as payment, inventory, or shipping should
  be checked for domain event/outbox needs instead of being hidden in the API
  handler.
- Transaction boundaries and locking/idempotency are described for non-idempotent
  writes.
- Tests include happy path, failure path, and at least one business invariant or
  edge case.
- File ownership conflicts are resolved before edits are applied.
- Final answer lists remaining risks only when they are actionable.

## Conflict Priority

Resolve conflicts in this order:

1. Domain invariants and ubiquitous language
2. Data consistency, transactions, security, and idempotency
3. Public API contract
4. Testability and regression coverage
5. Django/Django Ninja implementation details
6. Naming, style, and minor refactoring

## Final Response Shape

For implementation:
- summarize the role split or sequential fallback in one short sentence
- provide the integrated file/code plan or patch summary
- include verification commands

For review:
- lead with severity-ranked findings
- map findings to dddjango rules
- include concrete next actions

For design:
- present the domain contract first
- then DB/API/test implications
- include unresolved assumptions
