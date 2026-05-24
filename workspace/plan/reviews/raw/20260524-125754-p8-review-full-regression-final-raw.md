# P8 Full Regression Independent Review Raw

Reviewer perspective: independent final gate reviewer for eval reliability,
runtime evidence currency, leakage boundary, report staleness, and completion
claim discipline.

Input artifacts reviewed:

- `workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime/raw/targeted-suite.json`
- `workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime/raw/run.json`
- `workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime/report/report.json`
- `workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime/report/report.html`
- `workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime/validation/validate-run.json`
- `workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime/raw/targeted-suite.json`
- `workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime/raw/run.json`
- `workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime/report/report.json`
- `workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime/report/report.html`
- `workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime/validation/validate-run.json`
- `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-runtime-analysis-raw.json`
- `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-manifest-validation-raw.json`
- current source/cache diff check for `dddjango/` and installed cache

Review checks performed:

- P5 targeted suite records `status=pass`, `iterations=2`,
  `variance_status=stable-pass`, with `variants=["with-plugin"]`.
- P5 all-cases raw records `status=pass`, `case_count=26`,
  `result_count=26`, `status_counts.pass=26`, and `not-scored=0`.
- P5 validate-run records `status=pass`, `failures=[]`, and matching raw and
  metadata digests.
- P6 targeted suite records `status=pass`, `iterations=2`,
  `variance_status=stable-pass`, with `variants=["with-plugin"]`.
- P6 all-cases raw records `status=pass`, `case_count=4`, `result_count=4`,
  `status_counts.pass=4`, and `not-scored=0`.
- P6 validate-run records `status=pass`, `failures=[]`, and matching raw and
  metadata digests.
- Raw/report leakage scan for `/Users/hyun`, `/private/tmp`,
  `__FORBIDDEN_LOCAL_PATH_SENTINEL__`, and `__PRIVATE_FIELD_SENTINEL__` returned
  no hits.
- Source/cache diff is empty.
- P7 runtime analysis remains pass with 26 cases, 13 families, zero failures,
  26 routing passes, 26 cache-path passes, and 26 final-answer passes.
- P8 report HTML files contain the final run ids and raw digests through the
  report generator outputs; no separate `latest` symlink or alias exists in
  `workspace/develop/eval/runs`, so the final run paths are the authoritative
  report paths.

Findings:

- Blocker: 0.
- Major: 0.
- Open Minor: 0.

Notes:

- A P5 targeted rerun encountered a self-reported skill-id typo in a final JSON
  answer while raw runtime stdout showed the expected installed-cache skill was
  loaded. The scorer was narrowed to resolve `wrong-routing` only when required
  claims are complete and raw runtime loaded-skill evidence matches the oracle.
  The final P5 targeted suite and all-cases bucket both pass after this fix.
- No unresolved flaky history remains in final P8 artifacts: both final targeted
  suites are stable-pass across two iterations.
