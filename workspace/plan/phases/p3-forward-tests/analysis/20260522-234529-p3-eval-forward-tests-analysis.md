수정 대상: workspace/plan/phases/p3-forward-tests/prompts/20260522-234529-p3-eval-forward-tests-prompt.md, workspace/plan/phases/p3-forward-tests/evidence/20260522-234529-p3-eval-forward-tests-raw.md, workspace/plan/phases/p3-forward-tests/evidence/20260522-234529-p3-eval-forward-tests-evidence.md, workspace/plan/phases/p3-forward-tests/closure/20260522-234529-p3-eval-forward-tests-closure.md, workspace/plan/indexes/artifact_index.md, workspace/plan/indexes/evidence_index.md, workspace/plan/phases/p3-forward-tests/index.md, workspace/plan/status/phase_status.md

# P3 Forward Tests Analysis

## Scope

P3 must verify that the 13 high-risk dddjango trigger families behave correctly for realistic user prompts before building the formal eval system. The phase requires happy and exclusion results, raw output, loaded skill/routing observation, final answer, overclaim classification, and contamination boundaries.

## Inputs Reviewed

- P1.5 usage cards: `workspace/plan/phases/p1-5-usage-cards/cards/20260522-230605-p1-5-skill-usage-cards-evidence.md`
- P2 status: `workspace/plan/status/phase_status.md`
- P3 plan gate: `workspace/plan/plugin_build_plan.md`
- Current runtime skill files under `dddjango/skills/**`

## Prompt Selection

The prompt set fixes one happy prompt and one exclusion prompt per trigger family. The prompts are copied from the P1.5 usage cards and preserve user-like wording. The matrix target and expected route are retained only as observation metadata; they must not be passed to Codex runtime.

## Execution Finding

The first fresh runtime pilot was attempted with `codex exec --json --ephemeral --skip-git-repo-check` from a clean temporary workspace. The sandbox escalation reviewer rejected the model invocation because it would export project-specific prompt/context to an external service without explicit user approval after risk disclosure.

## Failure Classification

| item | classification | rationale |
|---|---|---|
| Runtime pilot execution | `runtime-sync` | The prompt set and local skill files are available, but the actual model-backed Codex runtime forward-test could not execute under the current approval policy. |
| Skill/reference content | `none` | No wrong routing, overclaim, or leakage was observed because no model-backed response was produced. There is no basis for a skill or reference change. |

## Completion Impact

P3 cannot be marked complete. The plan explicitly says that if fresh forward-test or Codex trigger smoke cannot run, the phase must be recorded as `infrastructure-blocked` rather than complete.
