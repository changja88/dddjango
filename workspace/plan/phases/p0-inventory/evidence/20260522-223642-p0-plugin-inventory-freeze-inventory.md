# P0 Plugin Inventory Freeze

## Evidence Metadata

| field | value |
|---|---|
| work item id | `20260522-223642-p0-plugin-inventory-freeze` |
| phase | `p0-inventory` |
| scope | `plugin` |
| topic | `inventory freeze` |
| command/run | `pwd -P`; `git rev-parse --show-toplevel`; `git status --short`; `rg --files`; `find dddjango ...`; `find workspace/reference ...`; `shasum -a 256 ...`; `python3 -B workspace/scripts/validate_plan_governance.py`; `git diff --name-only` |
| raw artifact path | `workspace/plan/phases/p0-inventory/evidence/20260522-223642-p0-plugin-inventory-freeze-inventory.md` |
| digest | self-digest not embedded because editing this file changes its own digest; inspected source digests are listed below and the final inventory artifact digest is recorded in `workspace/plan/indexes/evidence_index.md` |
| result | inventory recorded; `validate_plan_governance.py` passed; final P0 completion scope gate blocked by pre-existing out-of-scope tracked diffs |
| current-file match status | current for inspected runtime/source files; `git diff -- dddjango workspace/reference` returned no diff |

## Scope Boundary

P0 is inventory-only. This evidence did not modify:

- `dddjango/**`
- `workspace/reference/**`

Allowed write targets for this inventory are:

- `workspace/plan/phases/p0-inventory/evidence/`
- `workspace/plan/indexes/artifact_index.md`
- `workspace/plan/status/phase_status.md`
- `workspace/plan/indexes/evidence_index.md`

Pre-existing tracked diffs were observed before inventory edits:

- `workspace/plan/indexes/artifact_index.md`
- `workspace/plan/indexes/evidence_index.md`
- `workspace/plan/indexes/goal_index.md`
- `workspace/plan/indexes/review_index.md`

The `goal_index.md` and `review_index.md` diffs are outside this P0 inventory edit scope and were not changed by this inventory.

## Manifest Inventory

Manifest path: `dddjango/.codex-plugin/plugin.json`

Manifest digest:

| path | sha256 |
|---|---|
| `dddjango/.codex-plugin/plugin.json` | `38b40eb1b7cd1020c8f6ca8bbca4ea286bd0a02cc90a49ce784b30181451743a` |

Present manifest fields:

| field | inventory |
|---|---|
| `name` | present: `dddjango` |
| `version` | present: `0.1.10` |
| `description` | present |
| `author` | present: `name`, `url` |
| `homepage` | present |
| `repository` | present |
| `license` | present: `MIT` |
| `keywords` | present: 9 values |
| `skills` | present: `./skills/` |
| `interface` | present |
| `interface.displayName` | present: `dddjango` |
| `interface.shortDescription` | present |
| `interface.longDescription` | present |
| `interface.developerName` | present: `Hyun` |
| `interface.category` | present: `Coding` |
| `interface.capabilities` | present: `Interactive`, `Read`, `Write` |
| `interface.websiteURL` | present |
| `interface.defaultPrompt` | present: 3 prompts |
| `interface.brandColor` | present: `#0C4A6E` |
| `interface.screenshots` | present: empty list |

Manifest path fields:

| path field | value | starts with `./` | resolves under plugin root | exists now | status |
|---|---|---:|---:|---:|---|
| `skills` | `./skills/` | yes | yes | yes, `dddjango/skills/` | known |

Codex local/private baseline:

| criterion | inventory |
|---|---|
| P0-P8 scope basis | `workspace/plan/plugin_build_plan.md` states P8까지 local/private Codex plugin 기준 |
| public marketplace claim | not claimed in P0 |
| installed Codex cache evidence | not collected in P0; deferred to later runtime parity/install phases |
| manifest local/private flag | no explicit local/private flag present in `plugin.json`; status `unknown` as manifest metadata |
| repository/homepage URLs | present, but P0 does not treat them as public marketplace evidence |

## Plugin Component Set

Component inventory from `find dddjango -maxdepth 3 -type f -print` and targeted component search:

| component | current state | paths/count | status |
|---|---|---:|---|
| plugin root | present | `dddjango/` | known |
| manifest | present | `dddjango/.codex-plugin/plugin.json` | known |
| `.codex-plugin/` contents | present | `plugin.json` only | known |
| skills directory | present | `dddjango/skills/` | known |
| skill `SKILL.md` files | present | 13 | known |
| `agents/openai.yaml` | present per skill | 13 | known |
| skill-local `references/` | present per skill | 51 markdown files total | known |
| top-level `dddjango/references/` | absent | 0 | missing |
| skill-local `scripts/` | absent | 0 | missing |
| top-level `dddjango/scripts/` | absent | 0 | missing |
| skill-local `assets/` | absent | 0 | missing |
| top-level `dddjango/assets/` | absent | 0 | missing |
| hooks | absent | 0 | missing |
| `.mcp.json` | absent | 0 | missing |
| `.app.json` | absent | 0 | missing |

Missing component rows are inventory findings only. P0 does not add or fix them.

## Skill Resource Inventory

| skill | `SKILL.md` | `agents/openai.yaml` | bundled references | bundled scripts | bundled assets | primary source `final.md` |
|---|---:|---:|---|---:|---:|---|
| `architecture-api` | yes | yes | 4: `idempotency-openapi.md`, `pagination-versioning.md`, `problem-details.md`, `rest-contracts.md` | no | no | yes |
| `architecture-db` | yes | yes | 4: `constraints-indexes.md`, `rollout-constraints.md`, `schema-modeling.md`, `transactions-locking.md` | no | no | yes |
| `architecture-ddd` | yes | yes | 4: `context-map.md`, `domain-events.md`, `strategic-design.md`, `tactical-patterns.md` | no | no | yes |
| `architecture-implementation-patterns` | yes | yes | 4: `outbox-acl.md`, `pattern-selection.md`, `ports-adapters.md`, `repository-uow.md` | no | no | yes |
| `implementation-cleancode` | yes | yes | 4: `encapsulation-abstraction.md`, `legacy-review.md`, `naming-functions.md`, `responsibility.md` | no | no | yes |
| `implementation-django` | yes | yes | 5: `coding-style-drf-maintenance.md`, `migrations.md`, `models-orm.md`, `services-selectors.md`, `transactions-performance-security.md` | no | no | yes |
| `implementation-django-ninja` | yes | yes | 4: `auth-pagination-filtering.md`, `problem-details-openapi.md`, `router-schema.md`, `testclient.md` | no | no | yes |
| `implementation-django-web` | yes | yes | 4: `csrf-ajax.md`, `static-assets.md`, `templates.md`, `templateview-htmx.md` | no | no | yes |
| `implementation-python` | yes | yes | 4: `dataclasses-enums.md`, `protocols-boundaries.md`, `pydantic-v2.md`, `typing.md` | no | no | yes |
| `implementation-tdd` | yes | yes | 5: `ai-assisted-tdd.md`, `bdd-atdd.md`, `inside-out-outside-in.md`, `red-green-refactor.md`, `test-list.md` | no | no | yes |
| `implementation-test` | yes | yes | 5: `coverage-mutation.md`, `django-api-concurrency.md`, `factories-property-tests.md`, `pytest-fixtures.md`, `test-doubles.md` | no | no | yes |
| `source-reference-audit` | yes | yes | 1: `source-governance.md` | no | no | yes |
| `workflow-dddjango-subagents` | yes | yes | 4: `delegation-rules.md`, `handoff-contract.md`, `integration-checklist.md`, `role-map.md` | no | no | yes |

## Source Reference Inventory

`workspace/reference/*/reference/final.md` files:

| source reference | `final.md` | supplemental `review.md` | supplemental `internal.md` | supplemental `external.md` | sha256 |
|---|---:|---:|---:|---:|---|
| `architecture-api` | yes | yes | yes | yes | `b9e58b49d98a1ca8374a8cbdb9c2ba98ef8308e3535407aece3f3e258b92a815` |
| `architecture-db` | yes | yes | yes | yes | `4f0f03f08dfc8d28d6d63c66d7121683001335d13954a0e9555c253d5c485b7b` |
| `architecture-ddd` | yes | yes | yes | yes | `6d08f560b488fb4bbffa71f33184f4861fe22d217eddc36e1d8b2fae4e910af9` |
| `architecture-implementation-patterns` | yes | no | no | no | `4ca24ed5617e653038d46e75ca1a549d13084459bb20146f80bbbda91c5d4180` |
| `implementation-cleancode` | yes | yes | yes | yes | `99ea21452d355bb0b71a0ef10fdfd49d51fc3db6006db8701f8254554f0eea43` |
| `implementation-django` | yes | no | no | no | `3bb24d368f3f294c8834222ffb682fa54cfeaeab7331b25bc5766714c31cd5f3` |
| `implementation-django-ninja` | yes | no | no | no | `bf233e891608667693d7ff805e1c4ffbbb1cdf1b5963bf8fcda7c453ece4138e` |
| `implementation-django-web` | yes | no | no | no | `70dd766924dc41c10bbfb02057f3593f38da3fc0245a13f7d7203f9bdef58202` |
| `implementation-python` | yes | yes | yes | yes | `20add04b9307eeaad4d4e575edbba56395413207babb62a7123127267113b581` |
| `implementation-tdd` | yes | yes | yes | yes | `80b94308adfc7f71d088603af721a7e6a98b23eb8037316318d23a7bd8c6060b` |
| `implementation-test` | yes | yes | yes | yes | `18defc6f81e22e40cabb9a298642fa8384a8e3a55b8a70dc0d4431c6d6adebab` |
| `source-reference-audit` | yes | no | no | no | `ac3efd00c84603242bb8f0283fafeab524daf94a8b9bd819bae29139be14df68` |
| `workflow-dddjango-subagents` | yes | no | no | no | `c6e158eca5c1fc13304659e051aacea58b465ca55b0a0ed78a1c9c72198e9abd` |

## Skill To Source Reference Relationship

Classification rules used for P0:

- `known`: exact skill slug has a matching `workspace/reference/<slug>/reference/final.md`.
- `provisional`: exact match exists, but supplemental `review.md`, `internal.md`, and `external.md` are not all present, so P0 does not claim conflict-free or sufficient source coverage.
- `missing`: no matching primary `final.md` exists.
- `unknown`: relationship cannot be determined from current file paths and headings without later P1 semantic review.

| skill | primary source relation | relationship status | notes |
|---|---|---|---|
| `architecture-api` | `workspace/reference/architecture-api/reference/final.md` | known | exact slug match; supplemental materials present |
| `architecture-db` | `workspace/reference/architecture-db/reference/final.md` | known | exact slug match; supplemental materials present |
| `architecture-ddd` | `workspace/reference/architecture-ddd/reference/final.md` | known | exact slug match; supplemental materials present |
| `architecture-implementation-patterns` | `workspace/reference/architecture-implementation-patterns/reference/final.md` | provisional | exact slug match; supplemental materials not present |
| `implementation-cleancode` | `workspace/reference/implementation-cleancode/reference/final.md` | known | exact slug match; supplemental materials present |
| `implementation-django` | `workspace/reference/implementation-django/reference/final.md` | provisional | exact slug match; supplemental materials not present |
| `implementation-django-ninja` | `workspace/reference/implementation-django-ninja/reference/final.md` | provisional | exact slug match; supplemental materials not present |
| `implementation-django-web` | `workspace/reference/implementation-django-web/reference/final.md` | provisional | exact slug match; supplemental materials not present |
| `implementation-python` | `workspace/reference/implementation-python/reference/final.md` | known | exact slug match; supplemental materials present |
| `implementation-tdd` | `workspace/reference/implementation-tdd/reference/final.md` | known | exact slug match; supplemental materials present |
| `implementation-test` | `workspace/reference/implementation-test/reference/final.md` | known | exact slug match; supplemental materials present |
| `source-reference-audit` | `workspace/reference/source-reference-audit/reference/final.md` | provisional | exact slug match; source explicitly states supplemental material is not present for this area |
| `workflow-dddjango-subagents` | `workspace/reference/workflow-dddjango-subagents/reference/final.md` | provisional | exact slug match; supplemental materials not present |

Relationship summary:

| status | count | items |
|---|---:|---|
| known | 7 | `architecture-api`, `architecture-db`, `architecture-ddd`, `implementation-cleancode`, `implementation-python`, `implementation-tdd`, `implementation-test` |
| provisional | 6 | `architecture-implementation-patterns`, `implementation-django`, `implementation-django-ninja`, `implementation-django-web`, `source-reference-audit`, `workflow-dddjango-subagents` |
| missing | 0 | - |
| unknown | 0 | - |

P0 does not upgrade any `provisional` row to complete source sufficiency. P1 must decide whether these source references are sufficient.

## Skill File Digests

| skill file | sha256 |
|---|---|
| `dddjango/skills/architecture-api/SKILL.md` | `50ac87ab37197bd8190bf30a05627b8ce72085b5bb03930af779bd490370e7b6` |
| `dddjango/skills/architecture-db/SKILL.md` | `531f93587437a4ce430fe3d96565f1349ffebc4611e95987ee2a121d6c97d579` |
| `dddjango/skills/architecture-ddd/SKILL.md` | `a1c235f263549efdf78dc6d815367653b5220df97d92c08159be3b2d57e1428a` |
| `dddjango/skills/architecture-implementation-patterns/SKILL.md` | `5a20832fa4039434ea098a3b296ac21cc63d496d6d4fa9dd700a4cb0b034787c` |
| `dddjango/skills/implementation-cleancode/SKILL.md` | `ac72f0f5092227ac19d07ee4e7b97795c51fcc352336b11e78f01b71b07958a0` |
| `dddjango/skills/implementation-django-ninja/SKILL.md` | `f0a45bd8fcfb9d3e4074586f73128c1fafba26e9308aae96eaf512f44f5af54e` |
| `dddjango/skills/implementation-django-web/SKILL.md` | `1372981290fd76c97bc06fb0edf5e7643ddf1cf8b499df3ec57433a4616bcf4a` |
| `dddjango/skills/implementation-django/SKILL.md` | `8803c152a3eaa6fdef0f0de248a47f9e50c0b1b46580881520d4f5915f8d7bcf` |
| `dddjango/skills/implementation-python/SKILL.md` | `a9e6cd500d4ba4412229eb099652d8d3c0b34bca42606dac53ae115ce97ffb6d` |
| `dddjango/skills/implementation-tdd/SKILL.md` | `5ae3be3892e217d6f4792f4f88d8b3305cd4fe230290d1ee2d54dfc3229d6706` |
| `dddjango/skills/implementation-test/SKILL.md` | `a947b8acfdedb07e3fdf8680bb5bd346623d9ea0bf6b5cfa48517d1cb85aa5b3` |
| `dddjango/skills/source-reference-audit/SKILL.md` | `31b852951559912ea5cf69f93f70309c7b233562ea76ad0131332441ab3cb6a9` |
| `dddjango/skills/workflow-dddjango-subagents/SKILL.md` | `fe1c861e8f32b5b421686bba30872a97d217928d38e500075f07de91dfb7e7a8` |

## P0 Issues For Later Phases

| item | classification | evidence | P0 action |
|---|---|---|---|
| `plugin.json` explicit local/private flag | unknown | manifest has no explicit local/private field; plan says P0-P8 use local/private Codex scope | record only |
| absent top-level and skill-local scripts | missing | no `scripts/` files found under `dddjango/` | record only |
| absent assets | missing | no `assets/` files found under `dddjango/` | record only |
| absent hooks | missing | no `hooks/` files found under `dddjango/` | record only |
| absent `.mcp.json` | missing | no file found | record only |
| absent `.app.json` | missing | no file found | record only |
| source sufficiency for 6 exact-match source relationships | provisional | primary `final.md` exists but supplemental materials are not all present | defer to P1 |
| pre-existing tracked out-of-scope diffs | issue | `git diff --name-only` before edits included `goal_index.md` and `review_index.md` | preserve; report scope gate honestly |

## Verification Results

| command | result |
|---|---|
| `python3 -B workspace/scripts/validate_plan_governance.py` | pass: `OK: plan governance validation passed` |
| `git diff --name-only` | blocked for P0 completion scope: output includes allowed P0 edits plus pre-existing out-of-scope tracked diffs in `workspace/plan/indexes/goal_index.md` and `workspace/plan/indexes/review_index.md` |
| `git diff -- dddjango workspace/reference` | pass: no output; runtime plugin body and source reference body are unmodified |
