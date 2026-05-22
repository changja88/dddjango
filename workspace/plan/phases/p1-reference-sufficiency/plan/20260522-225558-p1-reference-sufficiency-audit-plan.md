수정 대상: workspace/reference/*/reference/final.md

# P1 Reference Sufficiency Plan

## Work Item

| field | value |
|---|---|
| work item id | `20260522-225558-p1-reference-sufficiency-audit` |
| phase | `p1-reference-sufficiency` |
| scope | `reference` |
| topic | `sufficiency audit` |

## Allowed Edits

- `workspace/reference/**/reference/final.md`
- `workspace/plan/phases/p1-reference-sufficiency/{analysis,plan,evidence,closure}/`
- `workspace/plan/indexes/{artifact_index.md,evidence_index.md}`
- `workspace/plan/status/phase_status.md`

## Forbidden Edits

- `dddjango/skills/**`
- eval runner, case, answer, fixture, report, or validator files
- source-free runtime skill rewrites

## Steps

1. Add a narrow `P1 Source Sufficiency` section near the top of each
   `workspace/reference/*/reference/final.md`.
2. Keep existing substantive guidance intact; do not rewrite source decisions
   or bundled runtime instructions.
3. In each P1 block, record:
   - purpose
   - use conditions
   - exclusion or handoff conditions
   - core judgment criteria
   - source priority
   - P1 classification
4. Keep direct OpenAPI source usage limited to `architecture-api` and
   `implementation-django-ninja`; all other OpenAPI mentions remain handoff or
   boundary references.
5. Write P1 evidence with the full classification table, needs-source count,
   provisional restrictions, command results, and digests.
6. Update `workspace/plan/phases/p1-reference-sufficiency/index.md`,
   `workspace/plan/indexes/artifact_index.md`,
   `workspace/plan/indexes/evidence_index.md`, and
   `workspace/plan/status/phase_status.md`.
7. Run:
   - `python3 -B workspace/scripts/validate_plan_governance.py`
   - `git diff --name-only`
   - `git diff -- dddjango workspace/develop/eval`
   - `git diff --check`

## Expected Classification

| classification | expected count | note |
|---|---:|---|
| sufficient | 10 | reference has enough dedicated source basis for P2 skill rebuild input |
| provisional | 3 | usable as cautious source guidance, but not P5/P6/P8 completion evidence |
| needs-source | 0 | no source gap remains after metadata/provenance blocks are added |

Expected provisional rows:

- `implementation-tdd`: AI-assisted TDD guidance includes recent community
  articles that are weaker than official/primary methodology sources.
- `source-reference-audit`: local governance source is sufficient for current
  P1 work, but cache-sync and review-closure claims require later phase evidence.
- `workflow-dddjango-subagents`: local workflow governance is sufficient for
  planning and routing, but real subagent execution and cache-sync claims
  require later phase evidence.
