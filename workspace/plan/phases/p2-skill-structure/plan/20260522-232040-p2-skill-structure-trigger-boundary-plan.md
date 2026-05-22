수정 대상: `dddjango/skills/**`, `workspace/plan/phases/p2-skill-structure/**`, `workspace/plan/indexes/**`, `workspace/plan/status/phase_status.md`

# P2 Skill Structure Plan

## Metadata

| field | value |
|---|---|
| work item id | `20260522-232040-p2-skill-structure-trigger-boundary` |
| phase | `p2-skill-structure` |
| scope | `skill` |
| topic | `structure trigger boundary` |

## Allowed Edits

- `dddjango/skills/**`
- `workspace/plan/phases/p2-skill-structure/{analysis,plan,evidence,closure}/`
- `workspace/plan/indexes/**`
- `workspace/plan/status/phase_status.md`

## Steps

1. Verify P1.5 usage-card completion and load the usage-card coverage matrix.
2. Audit all 13 `SKILL.md` files for:
   - frontmatter keys exactly `name` and `description`;
   - folder-basename name match;
   - description below 180 words and 1200 chars, with 120 words as target;
   - body below 500 lines and 3500 words;
   - direct links to bundled references.
3. Audit all `agents/openai.yaml` files against `skill-creator/references/openai_yaml.md`:
   - strings are quoted;
   - `display_name`, `short_description`, and `default_prompt` are present;
   - `default_prompt` mentions `$skill-name`;
   - no policy or dependency conflicts are present.
4. Apply narrow runtime edits:
   - tighten over-target descriptions;
   - shorten default prompts so they match P1.5 usage-card trigger intent;
   - remove explicit absolute local path examples from runtime skill text.
5. Audit bundled resources:
   - confirm references are one level deep;
   - confirm references over 100 lines have TOC or no such file exists;
   - confirm no skill-local prohibited docs or stale placeholder resources exist.
6. Review plugin manifest and runtime path boundary from a plugin-creator perspective.
7. Write P2 evidence and closure, update P2 index, artifact index, evidence index, and phase status.
8. Run verification:
   - `python3 -B workspace/scripts/validate_plan_governance.py`;
   - skill-creator quick validator if available, otherwise local equivalent with the same frontmatter/naming constraints plus P2 limits;
   - plugin-creator validator if available, otherwise local equivalent for manifest/path/skill-agent shape;
   - runtime boundary scans;
   - `git diff --check`;
   - allowed-scope diff checks.

## Completion Criteria

- All 13 skills pass frontmatter, description, body size, and direct-reference-link checks.
- All 13 `agents/openai.yaml` files align with the matching `SKILL.md` trigger intent and do not declare conflicting policy or dependency requirements.
- Runtime plugin files contain no absolute local path, path traversal, source-tree dependency, stale placeholder bundled resource, or prohibited skill-local auxiliary document.
- Plugin manifest validates from the plugin-creator perspective.
- Plan governance validation passes.
