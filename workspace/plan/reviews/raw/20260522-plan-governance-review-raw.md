# Raw Review Notes: Plan Governance

This file preserves the actionable raw review findings from three independent
review perspectives. It is summarized in
`workspace/plan/reviews/summaries/20260522-plan-governance-review-summary.md`.

## Skill-Creator Perspective

Verdict before fixes: Blocker 1 / Major 4 / Minor 2.

Findings:

- Missing `workspace/plan/constraint_rules.md` made document creation and
  filename constraints unverifiable.
- The artifact policy defined inventory, usage cards, eval protocol, reviews,
  forward tests, and install evidence, but not phase analysis, plan, evidence,
  closure, goal prompt, decision, and status placement.
- Missing phase status board could let completion be inferred from scattered
  documents.
- Missing filename grammar made related analysis/plan/evidence/review files hard
  to join mechanically.
- Review evidence lacked a closure ledger that maps finding to work item and
  evidence.
- Documentation taxonomy should separate user need and artifact purpose.
- Naming needed timezone, precision, slug, ASCII/kebab-case, and superseded
  rules.

## Traceability/Reliability Perspective

Verdict before fixes: Blocker 0 / Major 4 / Minor 3.

Findings:

- Missing phase state tracking file.
- Missing decision records for scope, eval trust, goal completion, and taxonomy.
- Evidence immutability existed as a principle but lacked an index/schema.
- Goal run and artifact linkage schema was missing.
- Filename rules needed phase, scope, artifact kind, timestamp, and slug.
- Superseded document policy was missing.
- Human-facing rebuild changelog was missing.

## External Practice Perspective

Verdict before fixes: Blocker 0 / Major 5 / Minor 4.

Findings:

- Flat `workspace/plan` taxonomy was too weak for long-running phase work.
- File naming lacked phase, scope, target, sequence, and status.
- Status index was missing.
- ADR/decision records were missing.
- Evidence and review manifests were missing.
- Review summary/raw separation should be explicit.
- Forward-test and install evidence should be phase-owned, not ambiguous logs.
- The master plan had too many roles and needed execution state separated.
- Superseded/archive policy was missing.

## External Basis Used

- OpenAI Codex Skills: skills use progressive disclosure and are structured as
  `SKILL.md` with optional `scripts/`, `references/`, `assets/`, and
  `agents/openai.yaml`.
- OpenAI Codex Build Plugins: plugin source structure is separate from planning
  records; only `plugin.json` belongs inside `.codex-plugin/`.
- OpenAI Evaluation Best Practices: evals require objectives, datasets,
  metrics, run/compare loops, and continuous evaluation.
- OpenAI Graders: grader design should be iterative and grounded in explicit
  reference/sample structures.
- ADR practice: decisions should be short records with status, context,
  decision, and consequences.
- Documentation taxonomy practice: operational docs should separate reference,
  how-to, evidence, decisions, and status.

