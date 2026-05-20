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
- For source/reference boundary, leakage, public wording, eval traceability, validation coverage, or source/runtime path-boundary reviews, use `workspace/reference/source-reference-audit/reference/final.md` as the source decision before comparing runtime/public artifacts.
- Use `final.md` as the default decision source. Read `review.md`, `internal.md`, and `external.md` when final guidance is ambiguous, gap-related, or conflict-related.
- For runtime provenance, compare the relevant `workspace/docs` and `workspace/reference` sources with `dddjango/skills/<skill>/SKILL.md`, `agents/openai.yaml`, and `references/*.md`.
- For source/runtime cache sync, packaging sync, or provenance audits, list only source diffs, cache comparisons, provenance/package notes, validation output, and explicit not-run markers as evidence.
- For runtime metadata audits, treat SKILL.md and `agents/openai.yaml` file existence as insufficient by itself. Capture validation command output and compare semantic alignment between skill description, UI metadata, and default prompt before marking metadata quality complete.
- For runtime wrong-routing audits that name role map, skill description, and reference routing, treat all named axes as required evidence. Compare visible skill metadata or `SKILL.md` descriptions, the workflow role-map reference plus `workspace/docs/workflow.md` canonical table, and the reference-routing/fallback status. Do not rank the role map as merely conditional or reference routing as merely auxiliary when the user asks which axes to compare.
- For leakage review, reject copying internal evaluation wording into runtime or public files; offer generalized product rules and, when useful, a local forbidden-token scan.
- For leakage review, avoid spelling out non-public validation wording in runtime/public files. Describe it by category, such as private evaluation material, internal criteria, non-public validation notes, or internal identifiers.
- If a runtime/public prompt asks which strings or path patterns to scan, do not enumerate exact private sentinel tokens, validator-only literals, or internal script filenames. Use redacted placeholders and product-facing categories instead.

## Leakage Evidence Protocol

- For leakage and boundary reviews, inspect the permitted surfaces when current instructions and artifacts allow it: runtime skill files, bundled references, plugin metadata, public docs/cases, and current-run prompt/output/debug artifacts.
- Report the exact surfaces and concrete artifacts checked, such as repo-relative paths, commands, run files, or provided logs. If a surface was not checked, mark it `not run` or `not provided`; do not infer absence from an unrun scan.
- Treat user-provided prompt text as task context, but do not copy non-public validation wording, internal criteria, previous-run conclusions, non-public validation notes, or internal identifiers into runtime/public wording.
- Prefer product-facing categories such as `private evaluation material`, `internal criteria`, and `non-public validation notes`.
- In runtime/public answers, replace exact internal tokens with redacted placeholders such as `[private-eval-sentinel]`; do not quote validator-only literals even as examples.
- Keep the output bounded to the requested audit scope; broad scans are useful evidence only when they match the user's question and the available permissions.

## Public Boundary Wording

- Boundary/leakage review answers are public-facing by default. Unless the user explicitly asks to design or review internal eval-pack files, private answer oracles, or traceability manifests, translate internal eval-pack concepts into public-facing terms.
- Use terms such as source evidence, source basis, review scope, scenario label, validation conditions, mandatory safeguards, required proof, leakage risks, private evaluation material, internal criteria, and non-public validation notes.
- Do not present a glossary of internal evaluator terms to end users. Use the public-facing terms directly, and keep internal field names only for explicit internal eval-pack work.

## Runtime-Facing Path Boundary

- Separate path rules by context. Authoring/source analysis and cache/source parity evidence may cite `workspace/docs/**` and `workspace/reference/**` as source evidence. Internal eval/oracle work may cite permitted private eval paths when explicitly requested.
- Runtime-facing guidance includes `SKILL.md`, bundled `references/*.md`, `agents/openai.yaml`, prompt-input/runtime-exposed guidance, public runtime instructions, and runtime policy examples. For those surfaces, use only runtime bundle-relative or skill-local references such as `references/*.md`, `dddjango/skills/<skill>/...`, dddjango skill ids, and sanitized package metadata.
- Do not present `workspace/docs/**` or `workspace/reference/**` as runtime-facing allowed refs, final runtime instructions, bundled runtime source paths, or `runtime_skill_reference.allow_refs` entries. If a boundary matrix or YAML-like policy is needed, put workspace paths only under source-authoring, source-evidence, internal-eval, or cache/source parity surfaces.

## Conflict And Gap Ledger

- For conflict, source-gap, or provisional audits, produce an item-level ledger instead of only grouped counts or area summaries.
- Include columns for area or item, status, source evidence, decision or current state, allowed claim, forbidden claim, and validation or source work to close.
- Use statuses such as resolved conflict, open gap, provisional/fallback, out of scope, or needs source decision. Do not mark an unresolved or provisional row complete.
- Source evidence must identify the source role or decision basis, such as `reference-index`, `final.md`, `review.md`, `internal.md`, `external.md`, product docs, or runtime reference. A document name alone is not enough if the row does not say what it proves.
- Every open gap or provisional/fallback row must state what can be claimed now and what must not be claimed until the gap is closed.
- If the allowed or forbidden claim is unknown, say that explicitly and name the source work needed to decide it.

## Eval Traceability

Use this section only when the user explicitly asks to design or review eval traceability files, answer oracles, private eval-pack structure, or traceability manifests. Do not apply it to source/runtime cache sync, packaging sync, provenance audits, or general boundary/leakage answers by default.

- Inspect public cases, eval goals, validation docs, and run artifacts that current instructions permit. Read private eval files only when explicitly allowed.
- Keep private evaluation material out of public cases, runtime skills, plugin metadata, and source docs.
- Tie every eval case to its bucket `eval_goal.md`; use that file as the bucket-level source for required observations and coverage intent.
- Preserve the eval-pack field names only for explicit internal eval-pack work: `reference_basis` names source files and basis, while `coverage_tags` are stable scenario labels for bucket coverage. For general boundary/leakage answers, translate these concepts into source evidence and review scope.
- Do not redefine `coverage_tags` as evidence-strength labels such as direct/derived/gap. If source strength is useful, put it in a separate field such as `basis_status` or `source_status`.
- For internal eval-pack audits, keep the per-case link intact: public case path, private eval-file path, `case_id`, `reference_basis`, `coverage_tags`, checks, and leakage boundary should be traceable together.
- Public cases should contain public task context only. Non-public validation files carry internal review notes and checks.
- Do not create a detached rubric directory that breaks the per-case public/private-eval connection.

## Validation Coverage

- For validation coverage audits, produce a coverage matrix instead of only a narrative summary.
- Include columns for scenario or dimension, source evidence or source basis, review scope or scenario label, expected evidence, gap or residual risk, and negative or honesty check when relevant.
- Use internal eval-pack fields such as `reference_basis` and `coverage_tags` only when explicitly reviewing internal eval-pack files, answer oracles, or traceability manifests.
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
