---
name: workflow-dddjango-subagents
description: >
  Use when the user asks Codex to run a subagent-driven or role-decomposed
  Django workflow using dddjango standards, especially for complex Django
  features, DDD design, Django Ninja APIs, database design, tests/TDD,
  refactoring, or architecture review. Use this to assign dddjango skills to
  specialized subagents, define handoff contracts, integrate outputs, and fall
  back to sequential execution when subagents are unavailable.
---

# dddjango Subagent Workflow

Use this skill as the coordinator for composite Django work. Do not replace the
specialist dddjango skills; assign them to focused roles and integrate their
outputs.

## Classify First

Classify the request before delegating:

- Simple: one concern or one file. Use the relevant specialist skill directly.
- Composite: two or more of DDD, DB, API, Django, TDD, testing, clean code, or
  architecture. Use this workflow.
- Risky: state transitions, payments, inventory, migrations, auth, transactions,
  cross-module refactors, or DRF-to-Ninja migration. Prefer role-decomposed
  execution.

If subagents are available and the task has separable responsibilities, split by
role. If subagents are unavailable, run the same roles sequentially and state the
fallback briefly.

## Load References

- Read `references/delegation-rules.md` before deciding whether to delegate.
- Read `references/role-map.md` before assigning roles.
- Read `references/handoff-contract.md` before asking roles to return results.
- Read `references/integration-checklist.md` before the final response or patch.

## Execution Order

1. Define the coordinator scope: user goal, constraints, files, and success
   criteria.
2. Establish domain or architecture contracts first when the request includes
   business rules, state transitions, or bounded contexts.
3. Assign independent roles with disjoint file ownership. Do not ask multiple
   roles to edit the same files in parallel.
4. Require every role to return the handoff contract.
5. Integrate outputs using the conflict priority in `integration-checklist.md`.
6. Verify dddjango conformance: Korean-first, no DRF endorsement, Django Ninja
   for APIs, domain logic outside routers/views, and tests for business rules.

## Required Sections

For every composite workflow answer, include these sections:

1. `Role Map`: a table with `Role`, `Responsibility`, `dddjango skills`, and
   `File ownership`. Use exact skill names such as
   `workflow-dddjango-subagents`, `architecture-ddd`, `architecture-db`,
   `architecture-api`, `implementation-django-ninja`, `implementation-tdd`,
   `implementation-test`, and `implementation-cleancode`. Use the standard role
   names from `role-map.md`: `Coordinator`, `Domain Agent`,
   `Architecture Agent`, `DB Agent`, `API Agent`, `Django Agent`, `Test Agent`,
   and `Review Agent`. Do not rename roles to Worker, Designer, or Reviewer
   variants in the Role column.
2. `Sequential Fallback`: state how the same role split runs when subagents are
   unavailable. Include the phrase `순차 실행`.
3. `Handoff Contract`: show or reference the required fields `Scope`,
   `Inputs Used`, `Decisions`, `Files`, `Risks`, and `Required Follow-up`.
4. `Integration Checklist`: summarize the conflict priority and final dddjango
   checks.

For API or DRF-to-Ninja work, include at least one Django Ninja route with an
explicit status-code response mapping, for example
`@router.post("/orders", response={201: OrderOut, 400: ProblemDetail})`.

## Output Rules

- Keep the final answer concise and implementation-oriented.
- Mention subagent roles only when role decomposition affected the work.
- If no subagents were used, phrase it as role-based sequential execution, not
  as a missing capability.
- Never claim that validation, tests, or subagents ran unless they actually did.
