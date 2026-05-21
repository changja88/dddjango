# Migrations

Use this reference for Django migration files, historical models, data migrations, rollout sequencing, backfills, indexes, and operational migration risk.

Source basis: Django official docs, Two Scoops of Django, Django for Professionals.

## Basic Rules

- Keep migration files in version control.
- Keep migrations small and reviewable.
- Use `python manage.py sqlmigrate <app> <migration>` when SQL shape, lock behavior, or index creation matters.
- Do not import current model classes in migrations. Use `apps.get_model()` to load the historical model state.
- Make reverse migrations explicit. Use a no-op reverse only when rollback cannot reconstruct data and that trade-off is acceptable.

## Data Migrations

- Keep data migrations idempotent when possible.
- Process large tables in batches rather than loading all rows into memory.
- Use `update_fields` for per-row saves when only selected columns change.
- Prefer set-based `update()` with `F()` expressions when signals, custom `save()`, and per-instance validation are not required.
- Document assumptions such as old value shape, nullability, uniqueness, and expected row count.

## Expand, Backfill, Contract

Use a staged rollout for risky production schema changes.

1. Expand: add nullable columns, tables, or compatible indexes without requiring new code to be the only deployed version.
2. Backfill: populate existing rows with a data migration, management command, or operational job.
3. Contract: enforce `NOT NULL`, remove old columns, tighten constraints, or delete compatibility code after the backfill and deployment window are safe.

Do not add a non-nullable field and deploy code that older application versions cannot satisfy.

## Constraints And Indexes

- Add DB constraints for invariants that must hold across all writers.
- Use explicit names for constraints and indexes when the project convention supports it.
- Add indexes for fields frequently used in `filter()`, `exclude()`, and `order_by()`, but verify the query plan when possible.
- Remember indexes speed reads but slow writes and increase storage.
- For PostgreSQL, consider concurrent index creation tooling or project-specific operations for large tables.
- Coordinate unique constraints with deduplication and application-level error handling.

## Rollout Checklist

- Identify the transaction owner for any backfill or data rewrite.
- Identify lock risk, table size, expected duration, and rollback behavior.
- Decide whether old and new application versions must run simultaneously.
- Decide whether the migration should be split from the code deployment.
- Verify SQL with `sqlmigrate` or a database review when risk is non-trivial.
- Add or request integration tests for migration-sensitive behavior when practical.
