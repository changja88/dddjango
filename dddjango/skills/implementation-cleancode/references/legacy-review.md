# Legacy Review

Use this reference for code smells, safe refactoring, characterization tests, seams, sprout/wrap methods, and legacy risk handling.

## Code Smells

- Long method, long parameter list, large class, primitive obsession, data clumps.
- Divergent change, shotgun surgery, parallel inheritance hierarchies.
- Speculative generality, dead code, lazy class, duplicated code.
- Feature envy, middle man, inappropriate intimacy, message chains.
- Treat smells as investigation triggers, not automatic refactoring commands.

## Refactoring

- Preserve externally visible behavior unless the user explicitly asks for behavior change.
- Prefer small steps: extract method, introduce parameter/value object, decompose conditional, replace nested conditional with guard clauses, or move method to the data owner.
- Use table-driven logic only when it reduces branching complexity and keeps policy visible.
- Keep refactoring separate from feature changes when the blast radius is significant.

## Legacy Code

- Treat untested code as risky even if it looks clean.
- Add characterization tests before risky restructuring when practical.
- Use seams to separate hard dependencies for testing: object seams, injected collaborators, or controlled monkeypatch points.
- Use sprout method when adding new behavior beside dangerous legacy code.
- Use wrap method when adding before/after behavior while keeping the old behavior observable.
- If tests cannot be added, keep edits smaller and report the residual risk.
