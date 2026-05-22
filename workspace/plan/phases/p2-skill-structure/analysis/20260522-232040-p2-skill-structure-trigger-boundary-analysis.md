수정 대상: `dddjango/skills/**`, `workspace/plan/phases/p2-skill-structure/**`, `workspace/plan/indexes/**`, `workspace/plan/status/phase_status.md`

# P2 Skill Structure Analysis

## Metadata

| field | value |
|---|---|
| work item id | `20260522-232040-p2-skill-structure-trigger-boundary` |
| phase | `p2-skill-structure` |
| scope | `skill` |
| topic | `structure trigger boundary` |
| basis | P1.5 usage cards, skill-creator `openai_yaml.md`, plugin-creator `plugin-json-spec.md`, current runtime files |

## Preconditions

- P1.5 is complete in `workspace/plan/status/phase_status.md`.
- P1.5 usage cards cover 13 high-risk trigger families and provide positive/exclusion prompts, expected bundled resource loads, artifact behavior, common non-goals, and handoff wording.
- P1 recorded no `needs-source` reference gaps. Three provisional references carry forward: `implementation-tdd`, `source-reference-audit`, and `workflow-dddjango-subagents`.

## Initial Findings

| area | finding | action |
|---|---|---|
| `SKILL.md` frontmatter | All 13 skill files used only `name` and `description`; all names matched folder basenames. | Keep structure; verify with local validator and plugin validator equivalent. |
| description limits | All descriptions were below the hard limit of 180 words / 1200 chars. `source-reference-audit` and `workflow-dddjango-subagents` were over the 120-word target. | Tighten those two descriptions without changing trigger boundaries. |
| body size | All bodies were below 500 lines and 3500 words. | No body split needed. |
| bundled references | All references are one level below their owning skill and linked directly from the owning `SKILL.md`. No reference file exceeded 100 lines. | No resource move needed. |
| `agents/openai.yaml` | All 13 skills had `interface.display_name`, `interface.short_description`, and `interface.default_prompt`; no `dependencies.tools` or explicit policy existed. Several default prompts were longer than needed. | Align default prompts to concise P1.5-style usage triggers while preserving `$skill-name` mentions. |
| runtime boundary | Initial scan found explicit temporary absolute path examples in `implementation-django-web/SKILL.md`. `workspace/reference` appeared only in `source-reference-audit` audit-boundary wording. | Remove absolute path examples; keep source-reference audit mentions only as audit targets and non-runtime warnings. |
| prohibited skill files | No skill-local `README.md`, `INSTALLATION_GUIDE.md`, `QUICK_REFERENCE.md`, or `CHANGELOG.md` files existed. | No removal needed. |
| stale placeholders | No stale placeholder bundled resource was found. | Record as none. |
| plugin manifest | `dddjango/.codex-plugin/plugin.json` exists, names the plugin `dddjango`, points skills to `./skills/`, and has no hooks/apps/mcp companion paths. | Validate shape and path boundaries with plugin-creator-equivalent checks. |

## Skill-Creator Review Basis

- Frontmatter should include only `name` and `description` for this P2 pass.
- Description carries all trigger/use/exclusion information because it is the discovery surface.
- `agents/openai.yaml` strings should be quoted and include a default prompt that explicitly mentions `$skill-name`.
- `interface.short_description` should stay compact for UI scanning.

## Plugin-Creator Review Basis

- Manifest paths should be relative to plugin root and stay inside the archive.
- `skills` should resolve to `skills`.
- Unsupported manifest fields such as `hooks` should not be present.
- `apps` and `mcpServers` should be absent unless companion manifests exist.
- Runtime files should not depend on authoring-only source trees or absolute local paths.

## Scope Decision

The P2 edit is a narrow metadata/runtime-boundary cleanup. No source reference, eval case, runner, cache, marketplace, or external dependency change is required.
