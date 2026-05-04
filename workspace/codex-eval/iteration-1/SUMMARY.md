# Codex dddjango Evaluation Iteration

## Environment

- dddjango version/tag:
- Codex version: codex-cli 0.128.0
- Model: Codex default
- Reasoning effort:
- Baseline environment: `codex exec --ignore-user-config --ephemeral --sandbox read-only --cd /private/tmp/dddjango-codex-eval --skip-git-repo-check`
- dddjango environment: `codex exec --ephemeral --sandbox read-only --cd /private/tmp/dddjango-codex-eval --skip-git-repo-check` with local dddjango skill instructions injected by `evals/codex/scripts/run_prompts.py`

## Results

| Case | Category | Status | Notes |
| --- | --- | --- | --- |
| pilot-api-order-create | api-design | graded | baseline 88, dddjango 93; dddjango improved DDD/API boundaries, idempotency, payment port, transaction, select_for_update, and concise router code |
| pilot-implementation-coupon | implementation | graded | baseline 89, dddjango 94; dddjango kept DDD layering, Django model/service, Ninja endpoint, and RED pytest checks while cutting output size |
| pilot-review-fat-model | review | graded | baseline 87, dddjango 94; dddjango gave severity-ranked gateway, aggregate, transaction, N+1, assertNumQueries, and refactoring findings |
| pilot-tdd-coupon | tdd | graded | baseline 78, dddjango 94; dddjango recovered the read-only fallback and provided RED/GREEN/REFACTOR plus Django Ninja API artifacts |
| pilot-db-orders | db-design | graded | baseline 84, dddjango 93; dddjango improved model constraints, idempotency, locking, on_commit strategy, pytest checks, and migration validation |
| pilot-review-view-logic | review | graded | baseline 89, dddjango 93; dddjango improved thin endpoint guidance, application service split, idempotency, transaction.on_commit, and error contract guidance |
| pilot-api-standard | api-design | graded | baseline 86, dddjango 92; dddjango produced a copyable Django Ninja pagination/error convention with Problem Details, exception handlers, response mappings, and edge-case checklist |
| pilot-negative-drf | negative-control | passed | baseline 47, dddjango 93; dddjango rejected DRF and provided RED tests plus correct Django Ninja Schema/Router/NinjaAPI.add_router code |

## Summary

- Baseline average: 81.0
- Baseline average duration: 48.14 sec
- dddjango average: 93.25
- dddjango average duration: 60.86 sec
- Absolute lift: +12.25
- Percent lift: +15.12%
- Duration increase: +26.41%
- Baseline DRF violations: 1 (`pilot-negative-drf`)
- dddjango DRF violations: 0
- Baseline Korean-first rate: 100%
- Baseline Django Ninja compliance rate: 4/8 explicit usage; 1/8 explicit violation
- dddjango Korean-first rate: 100%
- dddjango Django Ninja compliance rate: 100% on API-relevant cases
- TDD quality rate: 100% on TDD cases
- Negative-control pass rate: 100%
- Pilot result: passed. The plugin meets the pilot gate: quality lift is above +15%, DRF violations are 0, Korean-first and Django Ninja compliance are 100%, TDD quality passes, and duration increase is below +30%.

## Follow-up

- Keep the scoped developer instruction strategy; it reduced duration increase from about +153% to +26.41%.
- Keep large implementation/design cases under explicit word budgets to avoid cost regressions.
- Keep DRF and TDD regression tests locked: both previously failed and now pass.
