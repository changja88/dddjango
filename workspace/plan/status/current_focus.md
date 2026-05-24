# Current Focus

Current focus: P7 install packaging is complete. Start P8 full regression.

Current phase state:

- P3a prompt matrix is fixed.
- Original P3b runtime forward-tests remain deferred under `ADR-0004`.
- P4 fixture-only eval skeleton is complete.
- P4.5 source/cache/install/discovery parity is complete.
- P5 individual eval is complete using model-backed installed-runtime v4
  artifacts.
- P6 integration eval is complete using model-backed installed-runtime v2
  artifacts.
- P7 install packaging is complete and supplies equivalent installed-runtime
  user-like evidence for the P7/P8 completion path.

Next action:

1. Run P8 from
   `workspace/plan/goals/p8-full-regression/20260522-215616-p8-goal-full-regression-prompt.md`.
2. Use P7 equivalent installed-runtime user-like evidence as the current runtime
   evidence gate for P8.
3. P8 must still run full regression and prove `not-scored=0`,
   missing/malformed oracle `0`, leakage `0`, report stale `0`, current-file
   fingerprint match, unresolved flaky history `0`, and final review closure.
