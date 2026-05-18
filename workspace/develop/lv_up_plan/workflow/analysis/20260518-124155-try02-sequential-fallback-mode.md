# workflow try02 sequential-fallback-mode Analysis

## Evidence

- Latest run: `20260518-012546-workflow-try01-full-current-baseline`
- Report: `workspace/develop/eval/workflow/runs/20260518-012546-workflow-try01-full-current-baseline/analysis/report.html`
- Case reviewed:
  - `case-workflow-sequential-fallback`: baseline `5 / 5` pass, with-dddjango `0 / 5` fail after hard gate override.
- Raw output:
  - `workspace/develop/eval/workflow/runs/20260518-012546-workflow-try01-full-current-baseline/raw/case-workflow-sequential-fallback-with-dddjango.txt`
- Oracle evaluation:
  - `workspace/develop/eval/workflow/runs/20260518-012546-workflow-try01-full-current-baseline/raw/case-workflow-sequential-fallback-answer-oracle-evaluation.json`
- Trace artifact:
  - `workspace/develop/eval/workflow/runs/20260518-012546-workflow-try01-full-current-baseline/raw/case-workflow-sequential-fallback-with-dddjango-subagent-trace.json`
- Subagent reviews:
  - Eval quality reviewer found workflow execution gate/oracle mode alignment risk.
  - Plugin source reviewer independently identified `workflow-dddjango-subagents` sequential fallback as the highest-risk procedure gap.
  - Latest report reviewer confirmed the only latest reportability blocker is this workflow case.

## Root Cause

- Primary root cause: `procedure gap`
- The with-dddjango answer preserved the required role order and produced a `## Sequential Fallback` section, but it did not explicitly state that real subagents were not executed.
- The trace parser therefore recorded `explicitFallbackClaims: []` and `traceStatus: "no-trace"` for the with-ddjango response.
- The hard gate then rejected the detected execution mode with: `workflow execution mode direct is not in acceptable_modes`.
- This is not only an eval artifact: the raw response does not contain a direct statement such as "actual subagents were not executed" or "this is a sequential fallback, not subagent output."
- This is not a one-off low-severity issue: it is the only blocked latest bucket result and turns an otherwise partial `4 / 5` answer into a hard-gated `0 / 5`.

## Decision

- Action: `harden plugin`
- Target files:
  - `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
  - `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
- Expected small change:
  - When using sequential fallback because subagents are unavailable, not authorized, or assumed unavailable, the final answer must explicitly say that real subagents were not executed and that the workflow is being handled as sequential fallback.
- Non-goals:
  - Do not weaken `case-workflow-sequential-fallback` answer oracle.
  - Do not change workflow role order.
  - Do not add broad subagent ceremony to direct-answer or opt-out cases.
  - Do not fix report conclusion wording in this try; treat that as a separate `runtime/report gap` candidate.

