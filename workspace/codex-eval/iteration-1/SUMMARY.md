# Codex dddjango Evaluation Iteration

## Environment

- dddjango version/tag:
- Codex version: codex-cli 0.128.0
- Model: Codex default
- Reasoning effort:
- Baseline environment: `codex exec --ignore-user-config --ephemeral --sandbox read-only --cd /private/tmp/dddjango-codex-eval --skip-git-repo-check`
- dddjango environment: `codex exec --ephemeral --sandbox read-only --cd /private/tmp/dddjango-codex-eval --skip-git-repo-check` with the user-installed `dddjango` plugin enabled

## Results

| Case | Category | Status | Notes |
| --- | --- | --- | --- |
| pilot-api-order-create | api-design | graded | baseline 88, dddjango 94; dddjango improved DDD/API boundaries and test criteria |
| pilot-implementation-coupon | implementation | graded | baseline 89, dddjango 91; dddjango improved DDD layering but was longer |
| pilot-review-fat-model | review | graded | baseline 87, dddjango 88; roughly equivalent, dddjango more structured |
| pilot-tdd-coupon | tdd | graded | baseline 78, dddjango 44; dddjango refused to provide concrete failing tests/code because no project files existed |
| pilot-db-orders | db-design | graded | baseline 84, dddjango 83; roughly equivalent, dddjango longer |
| pilot-review-view-logic | review | graded | baseline 89, dddjango 92; dddjango improved idempotency and use-case boundary guidance |
| pilot-api-standard | api-design | graded | baseline 86, dddjango 87; roughly equivalent |
| pilot-negative-drf | negative-control | failed | baseline 47, dddjango 46; both endorsed DRF Serializer/ViewSet/Router instead of rejecting |

## Summary

- Baseline average: 81.0
- Baseline average duration: 48.14 sec
- dddjango average: 78.12
- dddjango average duration: 98.73 sec
- Absolute lift: -2.88
- Percent lift: -3.56%
- Duration increase: +105.08%
- Baseline DRF violations: 1 (`pilot-negative-drf`)
- dddjango DRF violations: 1 (`pilot-negative-drf`)
- Baseline Korean-first rate: 100%
- Baseline Django Ninja compliance rate: 4/8 explicit usage; 1/8 explicit violation
- dddjango Korean-first rate: 100%
- dddjango Django Ninja compliance rate: 4/8 explicit usage; 1/8 explicit violation
- Pilot result: failed. The plugin did not meet the +15% quality lift target, did not eliminate DRF violations, and exceeded the +30% duration increase threshold.

## Follow-up

- Fix DRF policy enforcement first: API implementation prompts that request DRF must be rejected or rewritten as Django Ninja.
- Fix TDD behavior second: when no project files exist, the skill should still provide a concrete failing pytest example and minimal implementation sketch instead of only saying it cannot proceed.
- Re-run `pilot-negative-drf` and `pilot-tdd-coupon` after skill changes before running the full 8-case set again.
