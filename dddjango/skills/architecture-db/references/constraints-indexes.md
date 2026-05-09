# Constraints And Indexes

Load this for relational constraints, B+Tree index trade-offs, composite index order, covering indexes, partial indexes, and write-cost decisions.

## Constraints

- Use primary keys for row identity.
- Use foreign keys to protect references where the database can enforce the relationship.
- Use unique constraints for natural uniqueness, duplicate prevention, and idempotency storage.
- Use check constraints for local value invariants.
- Use not-null only after existing data is backfilled and rollout safety is clear.
- Choose cascade behavior deliberately: restrict, protect, cascade, set null, or soft delete depending on domain ownership and audit needs.

Constraints should support domain invariants. Do not abandon a DB-enforceable invariant because the ORM can validate it in application code.

## Index Trade-Off

- B+Tree indexes improve reads but slow writes because every insert/update/delete must update relevant indexes.
- Avoid indexes on low-cardinality columns unless paired with other filters or partial index conditions.
- Audit unused indexes in mature systems.
- Benchmark before adding many overlapping indexes.

## Composite Indexes

- Order columns by the query shapes the index must serve.
- Put equality filters before range filters.
- Respect the leftmost-prefix rule: an index on `(a, b, c)` can serve `(a)`, `(a, b)`, and `(a, b, c)` but not `(b)` alone.
- Do not rely on the “most selective first” myth without considering equality/range predicates and query coverage.

## Covering And Partial Indexes

- Use covering indexes when the query can be answered from index columns alone.
- Use included columns when the database supports them and they avoid heap/table lookup.
- Use partial indexes for meaningful subsets such as active records, soft-delete uniqueness, or common filtered states.
- Partial unique indexes are useful for constraints such as unique email among non-deleted users.

## Index Output

For each proposed index, state:

- query or invariant it supports;
- columns and order;
- whether it is unique, partial, or covering;
- write/storage cost;
- expected validation method such as EXPLAIN ANALYZE or query plan comparison.
