---
name: source-reference-audit
description: >
  Use for dddjango source/reference governance audits: workspace/reference final/review/internal/external evidence, runtime bundled references, skill metadata/frontmatter description/openai.yaml trigger routing, runtime metadata alignment, source provenance, source gap, conflict/gap ledger, provisional/fallback source status, DRF guardrail source decisions, wrong-routing/role-map/reference-routing audits, source/runtime cache or package sync, source/runtime boundary or leakage review, and validation coverage or eval traceability only when the question is about source evidence, review scope, or explicit internal eval-pack traceability. Use for source audit, 출처/근거 점검, provenance, source gap, provisional, skill 목록, 사용 시점, 경계, 트리거, 본문에 숨은 규칙, DRF 가드레일, 역할 맵, 라우팅 오류, 캐시 동기화. Prefer domain, DB, API, Django, Python, test, or workflow skills when the user is asking to design, implement, test, or run application behavior rather than audit source/reference integrity.
---

# Source Reference Audit

Use this skill to audit whether dddjango source documents, source references, runtime references, validation scenarios, and eval materials stay traceable and separated. This skill reviews evidence and boundaries; it does not replace the domain, API, DB, Django, Python, test, or workflow skills for application design or implementation.

## Routing

- Use this for audits of `workspace/reference`, `dddjango/skills/*/references`, source provenance, source gaps, provisional/fallback status, conflict decisions, DRF guardrails, source-governance validation coverage, explicit eval traceability, and source/runtime boundary risks.
- If the request asks for actual DDD modeling, DB design, REST API design, Django implementation, Python typing, TDD, tests, clean-code review, or coordinated implementation, route to the corresponding dddjango skill.
- If the request asks for test coverage mechanics, eval execution, evaluator implementation, or application validation rather than source basis or traceability, route to the owning test, workflow, implementation, or process task instead.
- If the user provides a fixed answer shape or read-only policy, preserve it exactly.

## Source Loading

- Read [source-governance.md](references/source-governance.md) when the audit needs the runtime-local summary of source/reference role, path-boundary, provenance, metadata, cache-sync, leakage, validation, or eval-traceability decisions.
- For source-gap, conflict, provenance, metadata/cache sync, leakage, validation coverage, or eval traceability audits, load only the requested source-authoring evidence and apply `source-governance.md`.
- Keep this `SKILL.md` as routing guidance. Use `source-governance.md` as the source for detailed artifact-role, path-boundary, leakage, cache-sync, and eval-traceability rules.

## Leakage Evidence Protocol

- Name the permitted surfaces and concrete artifacts actually checked.
- Mark skipped or unavailable surfaces as `not run` or `not provided`; do not infer safety from checks that did not run.
- If the user asks for a method, checklist, or verification procedure rather than an artifact audit, do not turn available current-run artifacts into findings or include an inspected/not-run status ledger. Describe evidence to capture as future/proposed proof unless the user explicitly asks you to inspect current artifacts.
- Keep private evaluation material, internal criteria, and non-public validation notes out of runtime/public wording; use redacted placeholders for private sentinels or validator-only literals.

## Public Boundary Wording

- Boundary/leakage review answers are public-facing by default.
- Unless explicitly reviewing internal eval-pack files or traceability manifests, translate internal concepts into public-facing terms such as source evidence, review scope, validation conditions, required proof, leakage risks, private evaluation material, internal criteria, and non-public validation notes.
- Keep evaluator internals and private field names out of user-facing wording unless the user explicitly asks for internal eval-pack work.

## Runtime-Facing Path Boundary

- Authoring/source analysis and cache/source parity evidence may cite source-authoring paths as evidence.
- Internal eval/oracle work may cite permitted private eval paths only when explicitly requested.
- Runtime-facing guidance must use runtime bundle-relative paths, skill-local references, dddjango skill ids, and sanitized package metadata.
- Do not present `workspace/reference/**` as runtime-facing allowed refs, final runtime instructions, bundled runtime source paths, or `runtime_skill_reference.allow_refs` entries.

## Dedicated Source And DRF Guardrail

- Use `source-governance.md` for dedicated-source, provisional/fallback, and DRF guardrail decisions.
- Keep REST contract, greenfield Django Ninja implementation, and existing DRF maintenance or migration as separate source axes.

## Conflict And Gap Ledger

- For conflict, source-gap, or provisional audits, produce item-level rows with status, source evidence, allowed claim, forbidden claim, and validation or source work to close.
- Do not mark unresolved or provisional rows complete.

## Eval Traceability

Use this section only when the user explicitly asks to design or review eval traceability files, answer oracles, private eval-pack structure, or traceability manifests. Do not apply it to source/runtime cache sync, packaging sync, provenance audits, or general boundary/leakage answers by default.

- Inspect only permitted public cases, eval goals, validation docs, private eval files, and run artifacts.
- Keep public case context, evaluator-only checks, source basis, scenario labels, validation checks, and leakage boundary traceable per case.
- Keep private evaluation material out of public cases, runtime skills, plugin metadata, and source docs.

## Validation Coverage

- For validation coverage audits, produce a matrix with scenario or dimension, source evidence or source basis, review scope, expected evidence, gap or residual risk, and negative or honesty check.
- Expected evidence must name concrete proof; validator pass output only proves the artifact and scenario it actually covers.
- Mark missing source, missing scenario coverage, missing expected evidence, provisional/fallback source, or unrun validation as a gap.

## Review Output

- Separate findings into resolved conflicts, open gaps, provisional/fallback decisions, and out-of-scope items.
- For each unresolved or provisional item, include the source evidence, what can be claimed, what cannot be claimed, and what validation or source work would close the gap.
- Do not present missing dedicated source coverage as complete reference coverage.
- Do not flatten `review.md` disagreements into final guidance unless the corresponding `final.md` or product docs make a clear decision.
- Report only commands, validation, reviews, or artifact checks that were actually executed. If a required check was not run or was forbidden by the current instructions, say so.
