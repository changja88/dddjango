# Delegation Rules

Load this to decide whether to use real subagents, sequential fallback, or a direct single-skill answer.

## When To Role-Decompose

Use role decomposition when:

- two or more of DDD, DB, API, Django, tests, TDD, or review are genuinely coupled;
- the user explicitly asks for subagents, role decomposition, parallel review, responsibility split, handoff, or sequential fallback;
- risky domain nouns such as order, payment, inventory, reservation, refund, permission, or ledger appear together with state transitions, transactions, schema, API contracts, or tests.

## When To Stay Direct

Do not force the workflow for:

- small single-file edits;
- simple model field renames;
- local CRUD changes with no invariant or rollout risk;
- short conceptual explanations;
- decorative requests to put a simple task into workflow or Role Map format when no real multi-role responsibility exists;
- tasks where the user explicitly says no subagent plan is needed.

Use the relevant implementation, architecture, test, or clean-code skill directly in these cases.

## Real Subagents

Use real subagents only when they are actually available, the user has authorized subagent/delegation/parallel work, and the task can be split into concrete independent work. Give each subagent:

- a role;
- scope;
- inputs;
- owned files or responsibility;
- expected output;
- constraints on what not to edit;
- validation expectations.

Do not claim a subagent review, implementation, or validation happened unless it actually ran.

## Sequential Fallback

If subagents are unavailable or not authorized, keep the role order and execute the reasoning sequentially:

1. Domain
2. Architecture
3. DB
4. API
5. Django
6. TDD/Test
7. Review
8. Integration

Sequential fallback is still a workflow. It is not a claim that subagents ran.
