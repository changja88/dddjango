수정 대상: workspace/plan/phases/p3-forward-tests/prompts/20260522-234529-p3-eval-forward-tests-prompt.md, workspace/plan/phases/p3-forward-tests/evidence/20260522-234529-p3-eval-forward-tests-raw.md, workspace/plan/phases/p3-forward-tests/evidence/20260522-234529-p3-eval-forward-tests-evidence.md, workspace/plan/phases/p3-forward-tests/closure/20260522-234529-p3-eval-forward-tests-closure.md, workspace/plan/indexes/artifact_index.md, workspace/plan/indexes/evidence_index.md, workspace/plan/phases/p3-forward-tests/index.md, workspace/plan/status/phase_status.md

# P3 Forward Tests Plan

## Intended Runtime Procedure

1. Use `workspace/plan/phases/p3-forward-tests/prompts/20260522-234529-p3-eval-forward-tests-prompt.md` as the fixed P3 prompt set.
2. For each matrix row, pass only the `forward-test prompt` text to a fresh Codex runtime session.
3. Use a clean temporary workspace and `--ephemeral` execution so prior `workspace/plan/**`, eval outputs, and previous forward-test artifacts are not available to the runtime task.
4. Store raw output, final answer, loaded skill/routing observation, overclaim/leakage status, and contamination status in P3 evidence.
5. If a case fails, classify the target as `none`, `reference`, `skill`, `trigger`, or `runtime-sync` before any edit.
6. Edit `dddjango/skills/**` only if a classified skill/trigger failure proves a narrow skill fix is necessary, then rerun the same forward-test.

## Current-Turn Execution Limit

The first runtime pilot was blocked by escalation policy before model invocation. This is not a skill/reference failure. Do not modify runtime skills from this evidence.

## Current-Turn Artifact Plan

1. Commit the prompt set as a P3 prompt artifact.
2. Preserve the rejected runtime attempt as raw P3 evidence.
3. Mark the P3 work item and phase as `infrastructure-blocked`.
4. Run governance validation so the blocked state remains traceable and does not masquerade as completion.

## Resume Condition

To continue P3, obtain explicit user approval for external Codex model invocation after risk disclosure, or provide an approved local/offline Codex runtime that can execute fresh user-like prompts without exporting project-specific context.
