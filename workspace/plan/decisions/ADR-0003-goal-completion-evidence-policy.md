# ADR-0003: Goal Completion Evidence Policy

Status: accepted
Date: 2026-05-22
Phase: p0
Decision Owner: codex
Supersedes: none
Superseded by: none

## Context

Earlier work exposed a failure mode where goal status, targeted runs, HTML
reports, or stale artifacts could look like completion while scoring or current
file evidence was missing.

## Options Considered

- Trust goal status text.
- Require repo evidence indexed to the goal and phase gate.

## Decision

A goal is complete only when the required current-file evidence is recorded in
the repo and linked from the goal index and phase status. Goal text alone is not
completion evidence.

## Consequences

- Goal prompts must include allowed scope, required gates, approval behavior,
  and completion evidence.
- `infrastructure-blocked` is not complete.
- Missing oracle, not scored, stale report, and digest mismatch keep the goal
  incomplete.

## Evidence

- `workspace/plan/indexes/goal_index.md`
- `workspace/plan/status/phase_status.md`
- `workspace/plan/governance/failure_taxonomy.md`

