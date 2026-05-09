# Rollout Constraints And Query Performance

Load this for EXPLAIN ANALYZE, query optimization, N+1, operational migrations, backfills, index-lock risk, rollout sequencing, and rollback considerations.

## Query Optimization

- Start with slow query evidence before denormalizing.
- Use `EXPLAIN ANALYZE` to compare estimates and actual execution.
- Check row estimates, actual time, loops, and buffer hits/reads.
- If estimated rows and actual rows diverge heavily, refresh statistics or revisit predicates.
- Watch scan types: sequential scan on large tables may be a warning, index scan suits selective reads, bitmap heap scan sits between, and index-only scan avoids heap access when possible.
- Watch join strategy: nested loop fits small outer sets with indexed inner lookups, hash join fits larger unsorted sets, and merge join fits pre-sorted or index-ordered join keys.
- Prefer JOIN over subqueries when it gives the optimizer clearer or cheaper access paths, but verify with the actual plan.
- Prefer filtering in the database, selecting only needed columns, using LIMIT where appropriate, and avoiding N+1 lazy-loading patterns.

## Performance Order

1. Optimize slow queries.
2. Add or adjust indexes.
3. Use application caching where it reduces repeated load.
4. Denormalize as a last resort with consistency maintenance.

## Operational Rollout

For production data changes, separate design from concrete Django migration implementation.

- Expand: add nullable columns, tables, or indexes without breaking old code.
- Backfill: populate data in batches with monitoring and retry safety.
- Contract: add NOT NULL/unique/check constraints or remove old structures after compatibility is proven.

Hand concrete migration file operations, `RunPython`, `apps.get_model()`, `sqlmigrate`, and Django migration code to `implementation-django`.

## Backfill And Index Risk

- Large backfills can lock rows, increase replication lag, and overload workers.
- Adding constraints before data is clean can fail deploys.
- Adding indexes can lock or slow writes depending on database and options.
- Validate whether concurrent/online index creation is needed.
- Plan rollback or forward-fix for partially completed data changes.

## Rollout Output

Record:

- current data risk;
- expand/backfill/contract sequence;
- lock/index risk;
- batching or monitoring needs;
- rollback or forward-fix approach;
- tests or verification commands that were run, or explicitly not run.
