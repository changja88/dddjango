# Raw Review - Phase Goal Prompts

## Input

- `workspace/plan/plugin_build_plan.md`
- `workspace/plan/constraint_rules.md`
- `workspace/plan/governance/naming_convention.md`
- plugin-creator skill guidance
- skill-creator skill guidance

## plugin-creator Perspective

Findings before finalization:

- The prompts must not treat plugin root files outside `.codex-plugin/plugin.json` and `skills/` as arbitrary planning storage.
- P7 must explicitly validate manifest path fields, source/cache parity, and installed runtime discovery.
- P4.5 and P7 must request approval before Codex install/cache/app-server operations.
- Marketplace/public distribution must stay out of P0-P8 unless a later decision changes scope.

Closure:

- P4.5 and P7 prompts now require manifest/path validation, source/cache diff, discovery evidence, and approval behavior.
- P0-P8 prompts keep local/private Codex plugin scope.
- Planning artifacts are kept under `workspace/plan/**`, not `dddjango/skills/**`.

## skill-creator Perspective

Findings before finalization:

- P2 must prevent bloated `SKILL.md` files and force progressive disclosure through direct bundled references.
- P2 must keep `agents/openai.yaml` aligned with `SKILL.md`.
- P3 must validate skills with user-like prompts without leaking expected answers to the forward-test.
- P5/P6/P8 must not allow goal completion on targeted pass, HTML report, or unscored output alone.

Closure:

- P2 prompt now includes frontmatter, description size, body size, direct reference links, stale resource, and openai.yaml checks.
- P3 prompt now requires fresh isolated/user-like forward-tests and forbids expected answer leakage.
- P5/P6/P8 prompts require current-file evidence, all-cases/full run checks, `not scored == 0`, and missing/malformed oracle checks.

## Final Finding Count

- Blocker 0
- Major 0
- Open Minor 0

## Remaining Risk

These prompts cannot guarantee runner availability, model stability, or policy approval. They are designed to prevent false completion and to classify blocked execution as `infrastructure-blocked` instead of success.
