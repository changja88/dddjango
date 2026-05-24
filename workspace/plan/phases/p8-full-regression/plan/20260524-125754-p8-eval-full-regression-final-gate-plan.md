수정 대상: `workspace/develop/eval/**`, `workspace/scripts/**`, `workspace/plan/phases/p8-full-regression/**`, `workspace/plan/reviews/**`, `workspace/plan/indexes/**`, `workspace/plan/status/phase_status.md`

# P8 Full Regression Final Gate Plan

## Plan

1. Apply only final narrow eval infrastructure fixes needed for P8 gates.
2. Verify runner unit tests and current P7 source/cache parity.
3. Obtain explicit P8 external model-backed runtime approval.
4. Run P5 individual-skill installed-runtime targeted suite twice.
5. Run P5 individual-skill installed-runtime all-cases bucket.
6. Run P6 integration-flow installed-runtime targeted suite twice.
7. Run P6 integration-flow installed-runtime all-cases bucket.
8. Regenerate reports from current raw artifacts and validate both runs.
9. Cross-check raw/report status counts, stale report digest, metadata digest,
   missing/malformed oracle, expected outcome conflict, leakage, and flaky
   history.
10. Verify P7 evidence remains current against present source/manifest/cache.
11. Perform independent final review and store raw, summary, and closure under
    `workspace/plan/reviews/`.
12. Run `workspace/scripts/p8_full_regression_check.py` against final P5/P6
    output dirs, P7 evidence, and review artifacts.
13. Update P8 evidence, closure, indexes, and phase status only if every gate is
    proven by current artifacts.

## Approval Boundary

The model-backed steps export P5/P6 public eval prompts, installed dddjango
runtime skill instructions/context, project instructions/context, and structured
output schema to the external Codex/OpenAI runtime. They must not run without
explicit P8 approval.

## Completion Gate

P8 is complete only when final model-backed full-run artifacts pass with
`not-scored=0`, missing/malformed oracle 0, leakage 0, stale report 0,
metadata/fingerprint mismatch 0, unresolved flaky history 0, current P7
equivalent installed-runtime evidence, and final independent review with
Blocker 0, Major 0, open Minor 0.
