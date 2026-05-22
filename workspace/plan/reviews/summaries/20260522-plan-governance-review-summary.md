# Plan Governance Review Summary

Review id: rev-20260522-plan-governance
Date: 2026-05-22
Scope: `workspace/plan` taxonomy, filenames, phase status, evidence, reviews,
goals, and decisions.

## Inputs

- `workspace/plan/plugin_build_plan.md`
- `workspace/plan/reviews/20260522-plugin-build-plan-review.md`
- Existing `workspace/plan/**` files
- OpenAI Codex Skills documentation
- OpenAI Codex Build Plugins documentation
- OpenAI Evaluation Best Practices and Graders documentation
- ADR and documentation taxonomy external references

## Review Perspectives

- Skill-creator: Blocker 1, Major 4, Minor 2 before fixes.
- Long-term traceability/reliability: Blocker 0, Major 4, Minor 3 before fixes.
- External-practice/documentation architecture: Blocker 0, Major 5, Minor 4
  before fixes.

## Findings Closed

| finding | closure |
|---|---|
| Missing `constraint_rules.md` | Added `workspace/plan/constraint_rules.md`; widened scope to rebuild-related docs under `workspace/plan/**`, `workspace/reference/**`, `workspace/develop/eval/**`, and `dddjango/skills/**`. |
| `AGENTS.md` referenced missing `workspace/plan/master_plan.md` | Updated `AGENTS.md` to reference `workspace/plan/plugin_build_plan.md`. |
| Missing phase taxonomy | Added `workspace/plan/phases/p0-inventory` through `workspace/plan/phases/p8-full-regression`, each with a phase `index.md` and phase-owned subdirectories. |
| Missing phase status board | Added `workspace/plan/status/phase_status.md` as the single progress board. |
| P0 gate path inconsistent with master plan | Updated `workspace/plan/status/phase_status.md` to use `workspace/plan/phases/p0-inventory/evidence/<work-item>-inventory.md`. |
| Missing filename grammar | Added `workspace/plan/governance/naming_convention.md`. |
| Governance work item IDs did not follow the new grammar | Updated artifact, evidence, and review index ids to canonical work item style. |
| Bootstrap review filenames predate the new grammar | Kept historical filenames for durability and indexed them as `bootstrap-pre-convention-reviews` in `artifact_index.md`; new files must use the canonical grammar. |
| Missing review closure mapping | Added this closure table and linked the review from `workspace/plan/indexes/review_index.md`. |
| Review/evidence indexes had pending digest/open-count fields | Added digest values available at the time of closure and explicit final-refresh status in `workspace/plan/indexes/*.md`. |
| Missing evidence and artifact manifests | Added and populated `workspace/plan/indexes/artifact_index.md` and `workspace/plan/indexes/evidence_index.md`. |
| Missing goal-run linkage | Added `workspace/plan/indexes/goal_index.md` and `workspace/plan/goals/README.md`. |
| Missing decision records | Added `workspace/plan/decisions/index.md` and ADR-0001 through ADR-0003. |
| Missing superseded policy | Added `workspace/plan/status/superseded_index.md`, archive directory, and superseded rules in `constraint_rules.md`. |
| Missing failure classification | Added `workspace/plan/governance/failure_taxonomy.md`. |
| Missing human-facing rebuild summary | Added `workspace/plan/status/rebuild_changelog.md`. |
| Runtime/process document separation unclear | Added `workspace/plan/README.md` and plugin build plan links to the governance files. |

## Remaining Risk

Read-only rechecks after fixes found only document-ledger issues. Those were
closed by updating `AGENTS.md`, aligning P0 gate wording, canonicalizing
governance work item IDs, updating index digest/status fields, adding this
closure table, and widening `constraint_rules.md` scope. Remaining open count
before final digest refresh: Blocker 0 / Major 0 / Open Minor 0.

## External Sources

- OpenAI Codex Skills: https://developers.openai.com/codex/skills
- OpenAI Codex Build Plugins: https://developers.openai.com/codex/plugins/build
- OpenAI Evaluation Best Practices: https://platform.openai.com/docs/guides/evaluation-best-practices
- OpenAI Graders: https://platform.openai.com/docs/guides/graders
- Diataxis: https://diataxis.fr/
- ADR overview: https://adr.github.io/
- Keep a Changelog: https://keepachangelog.com/en/1.1.0/
