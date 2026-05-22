수정 대상: workspace/reference/*/reference/final.md

# P1 Reference Sufficiency Analysis

## Work Item

| field | value |
|---|---|
| work item id | `20260522-225558-p1-reference-sufficiency-audit` |
| phase | `p1-reference-sufficiency` |
| scope | `reference` |
| topic | `sufficiency audit` |

## Inputs Read

- `workspace/plan/status/phase_status.md`
- `workspace/plan/phases/p0-inventory/evidence/20260522-223642-p0-plugin-inventory-freeze-inventory.md`
- `workspace/plan/plugin_build_plan.md`
- `workspace/plan/constraint_rules.md`
- `workspace/plan/phases/p1-reference-sufficiency/index.md`
- `workspace/reference/*/reference/final.md`
- `dddjango:source-reference-audit` bundled `source-governance.md`

## P0 Baseline

P0 records 13 skill-to-source relationships and 13 matching
`workspace/reference/*/reference/final.md` files.

P0 classified these relationships as:

| P0 status | count | items |
|---|---:|---|
| known | 7 | `architecture-api`, `architecture-db`, `architecture-ddd`, `implementation-cleancode`, `implementation-python`, `implementation-tdd`, `implementation-test` |
| provisional | 6 | `architecture-implementation-patterns`, `implementation-django`, `implementation-django-ninja`, `implementation-django-web`, `source-reference-audit`, `workflow-dddjango-subagents` |
| missing | 0 | - |
| unknown | 0 | - |

P1 must not modify `dddjango/skills/**` or eval material.

## Sufficiency Criteria

Each `final.md` was checked for:

- purpose
- use conditions
- exclusion or handoff conditions
- core judgment criteria
- source provenance and source priority

Source priority categories are:

1. official standards or official documentation
2. primary project documentation
3. reputable engineering article or recognized engineering book
4. unsupported blog, weak community source, or memory-based criterion

## Findings

The substantive guidance exists in all 13 source references, but the P1 audit
fields are not uniformly explicit. Some documents express scope and exclusion
only in prose or handoff sections, and several documents do not make source
priority visible near the top of the file.

OpenAPI appears in API-related references. P1 allows direct OpenAPI source use
only for `architecture-api` and `implementation-django-ninja`; other references
may mention OpenAPI only as a handoff or boundary. The current content respects
that boundary, but `architecture-api` needs an explicit official OpenAPI
Specification provenance entry because its OpenAPI section previously pointed
only to existing project notes.

## Needs-Source Rows Before Fix

| reference | issue | required source-only fix |
|---|---|---|
| all 13 `final.md` files | P1 metadata fields are unevenly explicit | add a narrow `P1 Source Sufficiency` block with purpose, use, exclude, core criteria, source priority, and classification |
| `architecture-api` | OpenAPI provenance is not explicit enough for direct OpenAPI contract guidance | include official OpenAPI Specification as source-priority 1 in the P1 block |

No source gap requires modifying runtime skills, eval cases, eval answers,
runner code, or bundled runtime references.

## Network Decision

No network lookup is required for this fix. The P1 change records provenance
from already-present source references and the existing plan ledger. No new
OpenAI/Codex claim is added, and no OpenAI source reference is changed.
