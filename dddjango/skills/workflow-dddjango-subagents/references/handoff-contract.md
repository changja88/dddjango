# Handoff Contract

Load this when assigning role work or integrating role outputs.

Each role handoff includes:

- `Scope`
- `Inputs Used`
- `Decisions`
- `Files`
- `Output`
- `Risks`
- `Required Follow-up`
- `dddjango Checks`

`Files` must include:

- `May edit`
- `Must not edit`

## Field Meanings

- `Scope`: the role's responsibility for this task.
- `Inputs Used`: docs, source files, user constraints, existing code, or prior role outputs used by the role.
- `Decisions`: both decisions made and decisions intentionally deferred.
- `Files`: ownership and edit limits.
- `Output`: expected artifact, patch, plan, review findings, or test criteria.
- `Risks`: unresolved correctness, migration, compatibility, or verification risks.
- `Required Follow-up`: questions or checks the next role or integrator must close.
- `dddjango Checks`: relevant domain, DB, API, Django, test, and review standards the role must satisfy.

## Handoff Discipline

- Make ownership explicit before parallel work.
- Do not assign overlapping write sets to multiple subagents.
- If a role only reviews, state that it must not edit files.
- If a role depends on an earlier decision, put that dependency in `Required Follow-up`.
- Close or carry forward each risk during integration.
