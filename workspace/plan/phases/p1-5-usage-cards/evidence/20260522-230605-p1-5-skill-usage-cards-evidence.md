# P1.5 Usage Cards Evidence

## Evidence Metadata

| field | value |
|---|---|
| work item id | `20260522-230605-p1-5-skill-usage-cards` |
| phase | `p1-5-usage-cards` |
| scope | `skill` |
| topic | `usage cards` |
| command/run | `pwd -P`; `git rev-parse --show-toplevel`; `git status --short`; `sed -n ...` on P0/P1 evidence and plan constraints; `shasum -a 256 ...`; `python3 -B workspace/scripts/validate_plan_governance.py`; `git diff --name-only`; `git diff -- dddjango/skills workspace/reference`; `git diff --check` |
| raw artifact path | `workspace/plan/phases/p1-5-usage-cards/cards/20260522-230605-p1-5-skill-usage-cards-evidence.md` |
| digest | self-digest not embedded because editing this file changes its own digest; card and closure digests are recorded in `workspace/plan/indexes/evidence_index.md` |
| result | P1.5 usage cards created for all high-risk trigger families; validator passed; diff boundary checks show no `dddjango/skills/**` or `workspace/reference/**` changes |
| current-file match status | current after validation and diff boundary checks |

## Preconditions Verified

| precondition | evidence | result |
|---|---|---|
| P0 inventory complete | `workspace/plan/phases/p0-inventory/evidence/20260522-223642-p0-plugin-inventory-freeze-inventory.md` | P0 inventories 13 skills, 13 `SKILL.md`, 13 `agents/openai.yaml`, and bundled references. |
| P1 reference sufficiency complete | `workspace/plan/phases/p1-reference-sufficiency/evidence/20260522-225558-p1-reference-sufficiency-audit-evidence.md` | P1 classifies 10 references `sufficient`, 3 `provisional`, and 0 `needs-source`. |
| P1.5 edit scope | goal prompt and `workspace/plan/constraint_rules.md` | Only usage-card, evidence, closure, index, and phase-status paths were edited. |

## High-Risk Trigger Family Decision

P1.5 selected all 13 skill-aligned trigger families as high risk because each
family affects later `SKILL.md` descriptions, trigger handoff wording, bundled
resource loading, and eval/forward-test routing.

| trigger family | expected skill | card status |
|---|---|---|
| REST API contract | `architecture-api` | covered |
| Relational DB integrity and rollout | `architecture-db` | covered |
| Domain modeling and invariants | `architecture-ddd` | covered |
| Implementation architecture patterns | `architecture-implementation-patterns` | covered |
| Maintainability review and refactor | `implementation-cleancode` | covered |
| Django ORM/service/migration implementation | `implementation-django` | covered |
| Django Ninja API implementation | `implementation-django-ninja` | covered |
| Django server-rendered web | `implementation-django-web` | covered |
| Python language and typing implementation | `implementation-python` | covered |
| TDD workflow | `implementation-tdd` | covered |
| pytest and Django test mechanics | `implementation-test` | covered |
| Source/reference governance | `source-reference-audit` | covered |
| Coordinated dddjango workflow | `workflow-dddjango-subagents` | covered |

Coverage count:

| metric | count |
|---|---:|
| high-risk trigger families | 13 |
| positive user prompts | 39 |
| exclusion prompts | 26 |
| cards with expected skill | 13 |
| cards with expected bundled resource load | 13 |
| cards with expected artifact behavior | 13 |
| cards with common non-goal | 13 |
| cards with expected handoff wording | 13 |

## Downstream Use

The usage-card artifact is the required input for:

- P2 `SKILL.md` description and trigger handoff revisions.
- P3 forward-test prompts and expected-routing observations.
- P5 individual eval case design.

No `SKILL.md` description, `agents/openai.yaml` trigger metadata, or bundled
runtime reference was changed in P1.5.

## Provisional Carry-Forward

P1 provisional restrictions remain in force:

- `implementation-tdd`: AI-assisted TDD guidance may inform cautious wording but
  is not P5/P6/P8 completion evidence.
- `source-reference-audit`: cache-sync, review-closure, and eval-completion
  claims require later phase evidence.
- `workflow-dddjango-subagents`: real subagent execution, runtime cache sync, and
  eval/regression completion claims require later phase evidence.

The P1.5 cards include these restrictions where those families are expected to
route or hand off work.

## Boundary Checks

| check | result |
|---|---|
| `dddjango/skills/**` modified | no; `git diff -- dddjango/skills workspace/reference` returned no output |
| `workspace/reference/**` modified | no; `git diff -- dddjango/skills workspace/reference` returned no output |
| usage card before skill trigger edits | pass; no runtime skill files were edited |
| external runner | not used; P1.5 does not require one |
| network | not used |
| Serena | skipped: no Serena MCP tools were available in this session; repository path was verified with `pwd -P` and `git rev-parse --show-toplevel`, and planning/reference evidence was inspected with `sed`/`rg`/`find` |

## Verification Results

| command | result |
|---|---|
| `python3 -B workspace/scripts/validate_plan_governance.py` | pass: `OK: plan governance validation passed` |
| `git diff --name-only` | pass: modified tracked paths are limited to P1.5 phase index, plan indexes, and phase status; untracked paths are only P1.5 card/evidence/closure artifacts |
| `git diff -- dddjango/skills workspace/reference` | pass: no output |
| `git diff --check` | pass: no output |

