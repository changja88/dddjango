수정 대상: workspace/develop/eval/fixtures/integration-flows/, workspace/scripts/p6_integration_eval.py, workspace/scripts/test_p6_integration_eval.py

# P6 Integration Flow Preflight Analysis

## Scope

P6 evaluates integration behavior, not individual skill trigger coverage. P5
individual cases are not reused as P6 completion evidence.

The P6 fixture matrix covers four representative integration surfaces:

| case id | surface | required boundary |
|---|---|---|
| `p6-composite-order-ddd-db-api-django-test` | DDD + DB + API + Django + Test | workflow coordination with explicit handoffs across domain invariants, DB idempotency/transaction, REST contract, Django service/model, and pytest/concurrency checks |
| `p6-tiny-edit-opt-out-restraint` | tiny edit / opt-out restraint | no workflow/subagent overreach for an explicit one-line typo fix opt-out |
| `p6-source-runtime-governance-boundary` | source/runtime governance | separation of source evidence, runtime guidance, public prompt wording, evaluator-only material, and run artifacts |
| `p6-subagent-workflow-honesty` | subagent/workflow honesty | no completed subagent or parallel review claim without real spawn/collection artifacts |

## Gap Classification

- No runtime skill edits are currently required. The integration gaps are
  evaluator coverage gaps, so edits stay under `workspace/develop/eval/**` and
  `workspace/scripts/**`.
- The runner adds P6-specific guardrails on top of the P5 clean/scored eval
  mechanics: required handoff skills, forbidden workflow overreach, and
  source/runtime leakage marker checks.
- The current preflight is fixture-scored and `model_backed=false`; it proves
  fixture shape, scorer behavior, report consistency, and clean/scored status
  only. It is not P6 completion evidence.

## Runtime State

P5 individual eval completion remains the model-backed installed-runtime v4
artifacts. P6 requires fresh model-backed installed-runtime integration evidence.
An external Codex runtime run was attempted after risk disclosure, but the
reviewer rejected it because this P6 turn did not contain a P6-specific explicit
approval for exporting P6 public prompts, installed dddjango runtime context, and
the structured output schema to the external model.

## Current Decision

Keep P6 phase active. Completion is pending model-backed targeted 2x and
affected bucket all-cases evidence.
