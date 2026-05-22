수정 대상: `workspace/plan/governance/eval_protocol.md`, `workspace/develop/eval/**`, `workspace/scripts/**`, `workspace/plan/phases/p4-eval-skeleton/**`, `workspace/plan/indexes/**`, `workspace/plan/status/phase_status.md`

# P4 Eval Mini-Bucket Skeleton Plan

## Steps

1. Define `workspace/plan/governance/eval_protocol.md` with case, answer, oracle,
   scoring, artifact, failure, report, command, and affected-bucket semantics.
2. Add a `mini-bucket` fixture with baseline and with-plugin variants for each
   required P4 failure class.
3. Implement fixture-only CLI commands:
   - `run-one`
   - `run-bucket`
   - `render-report`
   - `validate-run`
4. Add stdlib unit tests for scorer, leakage, command evidence, Korean negation,
   stale report detection, and raw/report validation.
5. Generate raw mini-bucket run artifacts and regenerate the report from raw.
6. Run validator and record that injected `not-scored` keeps the run failed.
7. Update P4 phase evidence, indexes, and phase status with the P3b deferred
   limit.

## Acceptance Evidence

- Unit tests pass.
- `run-one` pass fixture exits 0.
- `run-bucket` exits 1 because the fixture intentionally contains partial,
  fail, and not-scored cases.
- `render-report` exits 0 and writes report artifacts from current raw.
- `validate-run` exits 1 with `not-scored-present`, and validation JSON records
  zero fixture mismatches plus observed failure semantics.
- `validate_plan_governance.py` passes after plan/index/status updates.
