# Blocker: Trigger Routing Verification Incomplete

## Status

Resolved/superseded.

This blocker no longer represents the active stop condition. Try 9 and later runs completed the trigger-routing targeted scoring that was blocked here.

## Why This Blocks Completion

The complete hard gate requires latest targeted eval scoring, full bucket scoring when needed, final multi-faceted skill review, and `skill-creator` review with no open findings.

After try 8:

- Raw targeted eval artifacts for `case-plugin-trigger-routing` were produced.
- Raw artifact validation passed with `--skip-oracle`.
- The required answer-oracle scoring command was rejected by the environment usage limit before it could run.
- The raw with-ddjango output still contains medium findings, so the trigger-routing family cannot be considered closed without another fix-and-score loop.

At the time this blocker was written, a required verification step had not run and open findings remained, so `update_goal(status="complete")` could not be called.

Later evidence:

- Try 9 targeted `case-plugin-trigger-routing`: `20260513-try9-trigger-body-only-boundaries`, `with-ddjango = pass`.
- Fresh full run before later source-reference edits: `20260513-final-full-plugin-try12`, `case-plugin-trigger-routing` `with-ddjango = pass`.

Current completion state is governed by the later final-full usage-limit blocker, not this resolved try 8 blocker.

## Evidence

- Try 8 raw run: `workspace/develop/eval/plugin/runs/20260512-try8-trigger-boundary-precision`
- Raw validation:
  - `python3 workspace/scripts/validate_eval_run.py --bucket plugin --run-id 20260512-try8-trigger-boundary-precision --case case-plugin-trigger-routing --skip-oracle`
  - Result: pass.
- Oracle scoring command blocked:
  - `python3 workspace/scripts/evaluate_eval_run.py --bucket plugin --run-id 20260512-try8-trigger-boundary-precision --case case-plugin-trigger-routing --timeout-seconds 1800 --rerun`
  - Result: rejected by environment usage limit.
- Retry on 2026-05-13:
  - Same command retried with required escalation.
  - Result: rejected again by environment usage limit.

## Remaining Open Findings From Try 8 Raw Output

- `workflow-dddjango-subagents` frontmatter still does not separate workflow selection from real subagent execution permission strongly enough.
- `implementation-django-ninja` answer-only/fixed-output-shape rule is body-only.
- `implementation-django-web` Korean boundary for composite/risky work still reads stronger in the body.
- `implementation-django` greenfield DRF guardrail is body-only.
- Minor Korean alias gaps remain for DDD, implementation-patterns, and Django Ninja.

## Local Try 9 Update

On 2026-05-13, try 9 made local frontmatter-only fixes for the try 8 raw findings:

- `workflow-dddjango-subagents`: added the selection-vs-real-subagent-execution boundary.
- `implementation-django-ninja`: added fixed answer shape/tool-report restraint and missing Korean/API-test aliases.
- `implementation-django-web`: added Korean composite/risky workflow routing boundary.
- `implementation-django`: added greenfield DRF-to-Ninja routing.
- `architecture-ddd`: added Korean policy/entity/value-object aliases.
- `architecture-implementation-patterns`: added Korean port-adapter/dependency-inversion aliases.

Local checks after try 9:

- `python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: pass.
- `python3 workspace/scripts/validate_eval_bucket_pack.py --bucket plugin`: pass.
- `git diff --check`: pass.
- leakage scan for case ids/oracle fields/prior run ids in runtime and public prompt surfaces: no new leak findings beyond the intended general `source-reference-audit` guardrail.

Model-backed targeted eval and answer-oracle scoring for try 9 have not run because the environment usage limit was still active before the stated reset time.

## Local Checks That Still Pass

- `python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `python3 workspace/scripts/validate_eval_bucket_pack.py --bucket plugin`
- `git diff --check`
- `python3 workspace/scripts/validate_eval_run.py --bucket plugin --run-id 20260512-try8-trigger-boundary-precision --case case-plugin-trigger-routing --skip-oracle`

## Next Try When Model Evaluation Is Available

Start a new try only if willing to continue the trigger-routing family. The next scoped target should be either:

1. Fix the try 8 raw medium findings and rerun `case-plugin-trigger-routing`, or
2. Treat the repeated trigger-frontmatter review churn as an oracle/review-scope blocker and revise the review criteria.

Do not mark the goal complete until the required oracle scoring, bucket-level hard gates, leakage scan, final multi-faceted review, and `skill-creator` review all pass.
