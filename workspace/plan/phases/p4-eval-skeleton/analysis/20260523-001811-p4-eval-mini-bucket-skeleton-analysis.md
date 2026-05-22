수정 대상: `workspace/plan/governance/eval_protocol.md`, `workspace/develop/eval/**`, `workspace/scripts/**`, `workspace/plan/phases/p4-eval-skeleton/**`, `workspace/plan/indexes/**`, `workspace/plan/status/phase_status.md`

# P4 Eval Mini-Bucket Skeleton Analysis

## Entry Condition

- P3a static/user-prompt matrix is recorded as current in
  `workspace/plan/status/phase_status.md`.
- P3b runtime forward-test remains `infrastructure-blocked`.
- `workspace/plan/decisions/ADR-0004-p3-runtime-forward-test-deferral.md` is
  accepted, so P4 may proceed only as evaluator-mechanics work.

## Problem

The rebuild plan forbids adding large skill-specific eval cases before the
runner, oracle schema, scoring semantics, validator, and report renderer prove
that they distinguish success from evaluator failures. The existing workspace
had no `workspace/develop/eval/**` skeleton, no eval protocol, and no
mini-bucket fixture artifacts.

## Required Failure Classes

P4 must prove these classes are separated before P5/P6:

- scored pass
- scored partial
- scored fail
- missing oracle
- malformed oracle
- stale report
- local path leakage
- sanitizer-only pre-redaction leakage
- private field leakage
- `expected_outcomes` conflict
- Korean negation false-positive avoidance
- prompt-only command claim rejection

## Design Decision

Use a fixture-only stdlib Python CLI in `workspace/scripts/eval_skeleton.py`.
The CLI reads deterministic JSON fixtures and writes raw, report, and validator
artifacts under `workspace/develop/eval/runs/<run-id>/`.

This is deliberately not model-backed. It validates evaluator semantics only.
Runtime-routing evidence remains deferred and must be resolved before P7/P8 by
P3b or an accepted equivalent installed-runtime evidence gate.
