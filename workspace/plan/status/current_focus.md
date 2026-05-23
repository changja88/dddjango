# Current Focus

Current focus: P4.5 runtime parity is complete. Resume P5 individual eval with
model-backed installed-runtime evidence.

Current phase state:

- P3a prompt matrix is fixed.
- P3b runtime forward-tests remain infrastructure-blocked under `ADR-0004`.
- P4 fixture-only eval skeleton is complete.
- P4.5 source/cache/install/discovery parity is complete.
- P5 fixture preflight is clean but incomplete because it is not model-backed.

Next action:

1. Run P5 from
   `workspace/plan/goals/p5-individual-eval/20260522-215616-p5-goal-individual-eval-prompt.md`.
2. Use the P5 preflight artifacts only as fixture/scoring evidence, not as P5
   completion evidence.
3. P5 completion requires model-backed installed-runtime evidence after the
   current P4.5 parity proof.
4. Keep `p3-forward-tests` as not fully complete until P3b runtime evidence
   exists.
5. Do not mark P7 or P8 complete until P3b or equivalent installed-runtime
   user-like evidence is current.
