# workflow try02 sequential-fallback-mode Review

## Result

- Targeted eval: `pass`
  - Run: `20260518-130131-workflow-try02-targeted-sequential-fallback-mode`
  - Case: `case-workflow-sequential-fallback`
  - with-ddjango: `5 / 5`
- Workflow full eval: `pass`
  - Run: `20260518-130438-workflow-try02-full-sequential-fallback-mode`
  - Cases: `13 / 13`
- All-bucket full eval: `pass`
  - response: `20260518-131953-response-try02-full-sequential-fallback-mode`
  - code: `20260518-131953-code-try02-full-sequential-fallback-mode`
  - plugin: `20260518-131953-plugin-try02-full-sequential-fallback-mode`
  - runtime: `20260518-134330-runtime-try02-full-sequential-fallback-mode`
  - source: `20260518-135207-source-try02-full-sequential-fallback-mode`
  - workflow: `20260518-141550-workflow-try02-full-sequential-fallback-mode`
- Latest reports: all six buckets are `reportable`, with six category links and zero disabled tabs.

## What Improved

- `case-workflow-sequential-fallback` no longer hard-gates.
- The with-ddjango response now explicitly says subagents are not executed and the work is handled as sequential fallback.
- Workflow latest report moved from `blocked` with one hard-gate failure to `reportable` with zero hard-gate failures.

## Remaining Risk

- Plugin latest has one `4 / 5` case: `case-plugin-leakage-sentinel`.
- Runtime latest has two `4 / 5` cases: `case-runtime-baseline-isolation`, `case-runtime-prompt-exposure`.
- Source eval quality still needs seeded conflict/provenance fixtures before source scoring is fully decision-grade.
- Workflow/report summary blocked wording was not changed in this try because the blocker is now cleared.

## Next Candidate

- Prioritize eval-quality hardening next:
  - source seeded conflict/provenance fixtures;
  - plugin/runtime oracle command/artifact specificity;
  - optional renderer/evaluator summary consistency if blocked cases reappear.

