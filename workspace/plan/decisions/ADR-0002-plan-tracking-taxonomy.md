# ADR-0002: Plan Tracking Taxonomy

Status: accepted
Date: 2026-05-22
Phase: p0
Decision Owner: codex
Supersedes: none
Superseded by: none

## Context

The rebuild has many phase outputs: analysis, plans, evidence, reviews, goal
prompts, closures, and decision records. Without a taxonomy and indexes, the
repo can accumulate logs that look complete but are not traceable.

## Options Considered

- Keep a flat `workspace/plan` directory.
- Separate evergreen plan, phase work, status, indexes, evidence, goals,
  reviews, decisions, and archive.

## Decision

Use the structured `workspace/plan` taxonomy defined in
`constraint_rules.md` and `governance/naming_convention.md`.

## Consequences

- `status/phase_status.md` is the progress source of truth.
- `indexes/*` files connect work items to evidence, reviews, and goals.
- Phase-specific work goes under `phases/<phase-name>/`.
- Superseded work is preserved and indexed.

## Evidence

- `workspace/plan/constraint_rules.md`
- `workspace/plan/governance/naming_convention.md`
- `workspace/plan/reviews/summaries/20260522-plan-governance-review-summary.md`

