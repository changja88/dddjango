# Claude dddjango Evaluation Iteration

## Environment

- dddjango version/tag: v0.1.7
- Claude version: Claude Code CLI, `claude -p`
- Model: default Claude CLI model
- Reasoning effort: default
- Baseline environment: clean cwd `/private/tmp/dddjango-claude-eval`, slash commands disabled
- dddjango environment: clean cwd `/private/tmp/dddjango-claude-eval`, `--plugin-dir /Users/hyun/Desktop/dddjango`

## Results

| Case | Category | Status | Notes |
| --- | --- | --- | --- |
| pilot-api-order-create | api-design | pending | |
| pilot-implementation-coupon | implementation | pending | |
| pilot-review-fat-model | review | pending | |
| pilot-tdd-coupon | tdd | pending | |
| pilot-db-orders | db-design | pending | |
| pilot-review-view-logic | review | pending | |
| pilot-api-standard | api-design | pending | |
| pilot-negative-drf | negative-control | blocked | Claude Code subscription access is disabled for this organization; `ANTHROPIC_API_KEY` is unset. |

## Summary

- Baseline average: not measured
- dddjango average: not measured
- Absolute lift: not measured
- Percent lift: not measured
- DRF violations: not measured
- Korean-first rate: not measured
- Django Ninja compliance rate: not measured
- Blocker: Claude CLI returned `Your organization has disabled Claude subscription access for Claude Code · Use an Anthropic API key instead, or ask your admin to enable access`.

## Follow-up

- Set `ANTHROPIC_API_KEY` or enable Claude Code subscription access for the organization.
- Re-run `pilot-negative-drf` for baseline and dddjango first.
- If the pilot succeeds, run all 8 cases for both variants, grade outputs, and render the Claude HTML report again.
