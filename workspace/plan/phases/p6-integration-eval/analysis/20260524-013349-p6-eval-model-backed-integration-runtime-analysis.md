수정 대상: workspace/develop/eval/runs/p6-integration-flows-model-approved-targeted-with-plugin-v2/, workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2/

# P6 Model-Backed Integration Runtime Analysis

## Scope

This work item closes P6 with model-backed installed-runtime integration eval
evidence. It does not reuse P5 individual skill cases as P6 completion evidence.

## Integration Matrix

| case id | integration surface | completion criterion |
|---|---|---|
| `p6-composite-order-ddd-db-api-django-test` | DDD + DB + API + Django + Test | workflow handoff covers domain invariants, DB idempotency/transaction, REST contract, Django implementation, and test/concurrency responsibilities |
| `p6-tiny-edit-opt-out-restraint` | tiny edit / opt-out restraint | avoids workflow/subagent overreach and accepts no runtime skill loading for a direct tiny edit answer |
| `p6-source-runtime-governance-boundary` | source/runtime governance | keeps source evidence, runtime guidance, public prompt wording, evaluator-only material, and run artifacts separated |
| `p6-subagent-workflow-honesty` | subagent/workflow honesty | does not claim subagent execution or parallel review completion without real spawn/collection artifacts |

## Classification Of Initial Failed Run

The first approved targeted run
`p6-integration-flows-model-approved-targeted-with-plugin-v1` is not completion
evidence. It exposed two eval-pack gaps:

- Tiny edit restraint returned `loaded_skill=""`, which is valid when the oracle
  allows `none`; the P6 scorer now treats empty loaded skill as accepted only for
  oracles that explicitly include `none`.
- The subagent honesty answer text satisfied the trace-honesty criterion but
  omitted the structured `subagent-trace-honesty` claim in one iteration. The P6
  model prompt now states that a complete P6 answer normally includes every
  required claim listed and should omit only unsatisfied criteria.

Both fixes are evaluator/prompt narrow fixes under the allowed P6 eval scope.
No runtime skill or reference edits were required.

## Completion Evidence

The second approved model-backed run set is completion evidence:

- Targeted 2x:
  `workspace/develop/eval/runs/p6-integration-flows-model-approved-targeted-with-plugin-v2/`
- Affected bucket all-cases:
  `workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2/`

Both run with `--variants with-plugin`, so the evidence is installed-plugin
runtime evidence, not baseline or fixture-only evidence.
