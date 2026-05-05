# dddjango Codex Evaluation Summary

This document preserves the meaningful results from prior local evaluation runs after
raw workspace artifacts were removed from the repository.

## Repository Policy

- Evaluation definitions live in `evals/`.
- Evaluation automation lives in `evals/codex/scripts/`, `tests/`, and `Makefile`.
- Generated run artifacts live under `workspace/codex-eval/` or
  `workspace/claude-eval/` and are not committed.
- When a run result matters for release history, summarize the numbers in `docs/`
  instead of committing raw prompts, outputs, logs, and generated HTML artifacts.

## Current Codex Findings

| Run | Scope | Baseline | dddjango | Delta | Required rules | Critical | Forbidden | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| conformance-rerun-1 | 5 cases | 87.22 | 100.00 | +12.78 | 100.00 | 0 | 0 | PASS |
| plugin-real-residual-1 | 2 cases | n/a | 100.00 | n/a | 100.00 | 0 | 0 | PASS |
| real-repo-1 | 6 cases | 81.39 | 100.00 | +18.61 | 100.00 | 0 | 0 | PASS |
| hard-benchmark-1 | 8 cases | 72.31 | 90.02 | +17.71 | 90.02 | 0 | 0 | PASS |
| benchmark-6 | 24 cases | 68.66 | 89.97 | +21.31 | 89.97 | 0 | 0 | PARTIAL |

## Interpretation

- dddjango is valuable when evaluated against its actual purpose: enforcing Django
  Ninja, DDD boundaries, DB design discipline, TDD structure, clean-code refactoring,
  and negative-control behavior.
- The important release signal is conformance rather than generic answer quality.
  Generic score lift understated the plugin value because baseline Codex answers were
  already broadly competent while often missing dddjango-specific conventions.
- `conformance-rerun-1`, `plugin-real-residual-1`, and `real-repo-1` are the strongest
  release-readiness signals from the prior runs.
- `benchmark-6` is retained here only as historical context. It was generated before
  the final residual fixes and missed the required-rule gate by 0.03 percentage points.

## Reproduction

Use these commands to regenerate local artifacts when needed:

```bash
make eval-conformance
make eval-plugin-real
make eval-release-gate
```

The regenerated reports are intentionally ignored by Git.
