# Handoff Contract

Require each role to return this structure. The Coordinator should reject vague
outputs and ask for a concrete follow-up when required fields are missing.

```md
## Scope
What this role inspected, designed, or changed.

## Inputs Used
dddjango skills and references used.

## Decisions
Concrete decisions made, including alternatives rejected when relevant.

## Files
- May edit:
- Must not edit:

## Output
Concrete design, code sketch, patch summary, test plan, or review findings.

## Risks
Remaining risks, assumptions, or unresolved conflicts.

## Required Follow-up
Items the Coordinator or another role must apply.

## dddjango Checks
- Korean-first response preserved.
- DRF is not endorsed.
- Django Ninja is used for APIs.
- Domain logic is not placed in routers/views.
- Tests cover business rules or known edge cases.
```

## Role-Specific Additions

Domain Agent:
- Include ubiquitous language terms.
- Identify aggregate boundaries and invariants.
- State which rules must be tested.

DB Agent:
- Start from query patterns.
- Include constraints, indexes, transaction/locking strategy, and migration
  verification commands.

API Agent:
- Include Django Ninja Router/Schema shape.
- Include status-code response mapping and error format.
- Avoid `Serializer`, `ViewSet`, `APIView`, `rest_framework`, and DRF routers.

Test Agent:
- Include RED expected failures before GREEN implementation.
- Include pytest structure, fixtures, edge cases, and verification commands.

Review Agent:
- Lead with severity-ranked findings.
- Distinguish correctness risks from style improvements.
- Include concrete remediation, not only principles.

