# Source Governance Reference

This runtime-local reference summarizes the source-reference-audit source decision. Use it to keep source-authoring evidence, runtime skill guidance, public prompts, evaluator-only material, and run artifacts in separate roles.

## Artifact Roles

| Surface | Allowed use | Forbidden use |
|---|---|---|
| Source-authoring evidence | Product decisions, source basis, provenance, source-gap decisions | Runtime-facing allowed reference, runtime bundle source path, run result promoted to source truth |
| Runtime skill | Agent procedure, bundled reference guidance, skill-local references, UI metadata | Private evaluation material, non-public validation notes, source-authoring path as allowed runtime reference |
| Public prompt or case | User-facing task context, scenario label, validation condition | Private evaluation material, scoring note, prior run output |
| Evaluator-only material | Internal checks, scoring, traceability to source basis | Runtime/public wording, source truth |
| Run artifact | Execution evidence and diagnostics | Source basis, runtime reference, future expected answer |

## Source Evidence Rules

- Treat `final.md` as the default decision source for a reference area.
- Read `review.md`, `internal.md`, and `external.md` when final guidance is ambiguous, gap-related, or conflict-related.
- If supplemental material is absent, report it as `not present` or `not provided`; do not imply it was inspected or treat absence as proof of complete conflict coverage.
- Treat source-authoring paths as evidence paths only. Do not list them as runtime-facing allowed references or bundled runtime source paths.

## Provenance And Gaps

- A dedicated source reference requires an existing final decision that actually covers the skill's main decisions. File existence alone is not enough.
- Mark missing final decisions, unresolved supplemental conflicts, source decisions weaker than runtime claims, or eval/run-only support as `open gap`, `provisional/fallback`, or `needs source decision`.
- For conflict, source-gap, or provisional audits, produce item-level rows with source evidence, decision/current state, allowed claim, forbidden claim, and expected evidence.

## DRF Guardrail

- Keep framework-neutral REST contract decisions, greenfield Django Ninja implementation, and existing DRF maintenance or migration as separate source axes.
- Do not treat DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`, or `rest_framework` material as the greenfield API implementation standard unless source evidence explicitly says the context is legacy, migration, comparison, or DRF-standardized maintenance.
- If DRF guardrail and provisional source status are both in scope, use separate rows so each source basis and forbidden claim can be checked independently.

## Metadata And Cache Sync

- Metadata audits must compare `SKILL.md`, `agents/openai.yaml`, validation output, and manual semantic alignment; file existence alone is not enough.
- Check that frontmatter description includes trigger vocabulary, scope, and negative routing.
- Check that `display_name`, `short_description`, and `default_prompt` match the skill purpose and do not expose private evaluation material, internal criteria, or non-public validation notes.
- Treat physical runtime cache paths as source/runtime parity evidence only, not as runtime-facing allowed references.

## Leakage And Public Wording

- Prefer product-facing categories such as `private evaluation material`, `internal criteria`, and `non-public validation notes`.
- Redact exact private sentinel strings or validator-only literals as placeholders such as `[private-eval-sentinel]`.
- Boundary/leakage answers should name inspected surfaces and explicit not-run or not-provided surfaces. Do not infer safety from scans that were not run.

## Eval Traceability And Validation Coverage

- Eval traceability applies when the user explicitly asks to design or review eval traceability files, answer oracles, private eval-pack structure, or traceability manifests.
- Keep public case context, evaluator-only checks, source basis, coverage labels, leakage boundary, and run evidence traceable per case when internal eval-pack work is explicitly in scope.
- Validation coverage matrices must include scenario or dimension, source evidence or basis, review scope, expected evidence, gap or residual risk, and negative or honesty check.
- A validator pass is evidence only for the artifact and scenario it actually covers.
