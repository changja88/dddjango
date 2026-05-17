---
name: source-reference-audit
description: >
  Use for dddjango source/reference governance audits: workspace docs, workspace/reference final/review/internal/external material, runtime bundled references, skill metadata/frontmatter description trigger routing, source provenance, source gap, conflict/gap ledger, provisional/fallback source status, validation coverage, eval traceability, and source/runtime boundary or leakage review. Use for source audit, 출처/근거 점검, provenance, traceability, source gap, provisional, validation coverage, skill 목록, 사용 시점, 경계, 트리거, 본문에 숨은 규칙. Prefer domain, DB, API, Django, Python, test, or workflow skills when the user is asking to design or implement application behavior rather than audit source/reference integrity.
---

# Source Reference Audit

Use this skill to audit whether dddjango source documents, source references, runtime references, validation scenarios, and eval materials stay traceable and separated. This skill reviews evidence and boundaries; it does not replace the domain, API, DB, Django, Python, test, or workflow skills for application design or implementation.

## Routing

- Use this for audits of `workspace/docs`, `workspace/reference`, `dddjango/skills/*/references`, source provenance, source gaps, provisional/fallback status, conflict decisions, DRF guardrails, eval traceability, validation coverage, and source/runtime boundary risks.
- If the request asks for actual DDD modeling, DB design, REST API design, Django implementation, Python typing, TDD, tests, clean-code review, or coordinated implementation, route to the corresponding dddjango skill.
- If the user provides a fixed answer shape or read-only policy, preserve it exactly.

## Source Loading

- For source-gap, conflict, or provisional audits, read `workspace/docs/reference-index.md` when it exists, then inspect the requested `workspace/reference/*/reference/final.md` files.
- Use `final.md` as the default decision source. Read `review.md`, `internal.md`, and `external.md` when final guidance is ambiguous, gap-related, or conflict-related.
- For runtime provenance, compare the relevant `workspace/docs` and `workspace/reference` sources with `dddjango/skills/<skill>/SKILL.md`, `agents/openai.yaml`, and `references/*.md`.
- For source/runtime cache sync, packaging sync, or provenance audits, list only source diffs, cache comparisons, provenance/package notes, validation output, and explicit not-run markers as evidence.
- For runtime wrong-routing audits that name role map, skill description, and reference routing, treat all named axes as required evidence. Compare visible skill metadata or `SKILL.md` descriptions, the workflow role-map reference plus `workspace/docs/workflow.md` canonical table, and the reference-routing/fallback status. Do not rank the role map as merely conditional or reference routing as merely auxiliary when the user asks which axes to compare.
- For leakage review, reject copying internal evaluation wording into runtime or public files; offer generalized product rules and, when useful, a local forbidden-token scan.
- For leakage review, do not propose runtime wording that repeats eval-only labels such as answer oracle, private scoring text, prior run findings, hidden target behavior, or case ids. Use product-facing terms such as private evaluation material, internal criteria, and non-public validation notes.

## Conflict And Gap Ledger

- For conflict, source-gap, or provisional audits, produce an item-level ledger instead of only grouped counts or area summaries.
- Include columns for area or item, status, source evidence, decision or current state, allowed claim, forbidden claim, and validation or source work to close.
- Use statuses such as resolved conflict, open gap, provisional/fallback, out of scope, or needs source decision. Do not mark an unresolved or provisional row complete.
- Source evidence must identify the source role or decision basis, such as `reference-index`, `final.md`, `review.md`, `internal.md`, `external.md`, product docs, or runtime reference. A document name alone is not enough if the row does not say what it proves.
- Every open gap or provisional/fallback row must state what can be claimed now and what must not be claimed until the gap is closed.
- If the allowed or forbidden claim is unknown, say that explicitly and name the source work needed to decide it.

## Eval Traceability

Use this section only when the user explicitly asks for eval traceability or validation coverage. Do not apply it to source/runtime cache sync, packaging sync, or provenance audits by default.

- Inspect public cases, eval goals, validation docs, and run artifacts that current instructions permit. Read private eval files only when explicitly allowed.
- Keep private evaluation material out of public cases, runtime skills, plugin metadata, and source docs.
- Tie every eval case to its bucket `eval_goal.md`; use that file as the bucket-level source for required observations and coverage intent.
- Preserve the eval-pack field names when designing or reviewing traceability: `reference_basis` names source files and basis, while `coverage_tags` are stable scenario labels for bucket coverage.
- Do not redefine `coverage_tags` as evidence-strength labels such as direct/derived/gap. If source strength is useful, put it in a separate field such as `basis_status` or `source_status`.
- For internal eval-pack audits, keep the per-case link intact: public case path, private eval-file path, `case_id`, `reference_basis`, `coverage_tags`, checks, and leakage boundary should be traceable together.
- Public cases should contain public task context only. Private eval files carry hidden target behavior and checks.
- Do not create a detached rubric directory that breaks the per-case public/private-eval connection.

## Validation Coverage

- For validation coverage audits, produce a coverage matrix instead of only a narrative summary.
- Include columns for scenario or dimension, source basis or `reference_basis`, `coverage_tags` when available, expected evidence, gap or residual risk, and negative or honesty check when relevant.
- Every validation coverage matrix must include an `expected evidence` column. If the user asks for a coverage map or table and the column is absent, revise the table before answering.
- Expected evidence must name concrete proof such as a validation command, eval run artifact, test file, review report, source crosswalk, or manual check. A validator pass alone is not enough unless it is tied to the scenario and artifact it proves.
- Do not add eval-run or private-eval evidence rows to source/runtime sync checklists unless eval coverage was explicitly requested.
- Check first-class dimensions from the source eval goal: DDD, implementation patterns, DB, API, Django, Django Ninja, Django Web, Python typing, Clean Code, TDD, Test, Workflow, negative cases, validation honesty, and runtime/source boundaries.
- Treat migration, transaction, concurrency, greenfield API standard, subagent-claim, and source-governance scenarios as explicit coverage rows when they are in scope.
- Mark missing source, missing scenario coverage, missing expected evidence, provisional/fallback source, or unrun validation as a gap; do not label those rows complete.

## Review Output

- Separate findings into resolved conflicts, open gaps, provisional/fallback decisions, and out-of-scope items.
- For each unresolved or provisional item, include the source evidence, what can be claimed, what cannot be claimed, and what validation or source work would close the gap.
- Do not present missing dedicated source coverage as complete reference coverage.
- Do not flatten `review.md` disagreements into final guidance unless the corresponding `final.md` or product docs make a clear decision.
- Report only commands, validation, reviews, or artifact checks that were actually executed. If a required check was not run or was forbidden by the current instructions, say so.
