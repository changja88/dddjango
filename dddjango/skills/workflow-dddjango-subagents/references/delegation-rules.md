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

For pure answer-only requests, answer with the requested content only. If the user asks for a fixed shape such as a sentence count or bullet count, treat that shape as the user's explicit instruction: every requested unit should answer the user's question and the response should stop at the final requested unit. Do not prepend, append, or embed meta notes such as tests not run, commands not run, no subagents used, skill/reference loading, `Commands run`, `commands run`, `Checks not run`, `checks not run`, `실행한 명령`, `명령 실행`, `체크`, `체크: 미실행`, `검증 미실행`, or `Serena` unless that is the user's question.

For direct implementation work, still report changed files and verification honestly, but keep it compact and do not add workflow sections unless the work becomes composite or risky.

## Real Subagents

Use real subagents only when they are actually available, the user has authorized subagent/delegation/parallel work, and the task can be split into concrete independent work. Give each subagent:

- a role;
- scope;
- inputs;
- owned files or responsibility;
- expected output;
- constraints on what not to edit;
- validation expectations.

If authorization is not yet granted, do not spawn agents or claim completed review. Ask for approval, but still propose the concrete role split first. For composite or risky work, include the canonical roles that apply, including Architecture Agent even when advisory, and name the Coordinator or explicit Integration owner. Avoid role names alone: provide bounded scope, inputs, owned files or read-only status, forbidden files, expected output, risks, required follow-up, and the integration responsibility for each proposed role.

Do not claim a subagent review, implementation, or validation happened unless it actually ran.
After spawning real subagents, collect each result with `wait_agent` or `close_agent` before integrating it or reporting it as complete. A spawned or pending subagent is not a completed review.
Before writing the final answer, confirm every spawned subagent has a completed result collection event. If result collection is unavailable or times out, report blocked or partial execution and do not integrate missing subagent results. Do not write `wait_agent`, `close_agent`, or role result summaries unless those calls actually completed.

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
When using sequential fallback, explicitly state that real subagents were not executed and that the workflow is being handled as sequential fallback.
Do not add this statement to direct single-skill answers, pure answer-only requests, or explicit opt-out responses.

## Review-Focused Work

For review requests, lead with findings ordered by severity and grounded in evidence. If the review spans multiple role areas, use the role map and handoff/integration checks after the findings to show coordination and follow-up ownership.
