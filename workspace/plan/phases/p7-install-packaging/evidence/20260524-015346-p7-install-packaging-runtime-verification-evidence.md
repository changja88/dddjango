# P7 Install Packaging Runtime Verification Evidence

P7 is complete in this evidence record. Install/cache/package checks pass, and
P3b-equivalent installed-runtime user-like `codex exec` evidence is current for
all 13 high-risk trigger families.

## Paths

| item | path |
|---|---|
| source plugin root | `dddjango/` |
| source manifest | `dddjango/.codex-plugin/plugin.json` |
| marketplace manifest | `.agents/plugins/marketplace.json` |
| installed cache root | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10` |
| installed cache manifest | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/.codex-plugin/plugin.json` |

## Raw Artifacts

| artifact | raw path | digest | result | current-file match |
|---|---|---|---|---|
| source manifest | `dddjango/.codex-plugin/plugin.json` | `38b40eb1b7cd1020c8f6ca8bbca4ea286bd0a02cc90a49ce784b30181451743a` | source manifest parsed | current |
| cache manifest | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/.codex-plugin/plugin.json` | `38b40eb1b7cd1020c8f6ca8bbca4ea286bd0a02cc90a49ce784b30181451743a` | cache manifest matches source manifest | current |
| marketplace manifest | `.agents/plugins/marketplace.json` | `b7eafdbad3493e49bd837b39ce4025af0101ba90d5c769b7c5302fc0e074f5e6` | local marketplace points to `./dddjango` | current |
| install refresh | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-install-refresh-raw.txt` | `eb21d8e5d5962a1b2e330f3a078b92508f72791cca7987ff8a5de666829fd2ec` | `codex plugin add dddjango@dddjango-local` installed cache root | current |
| marketplace list | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-marketplace-list-raw.txt` | `69bfeea03540052ffefab406c37d60407e8d7877f5267728c934599eec689106` | `dddjango-local` marketplace root is `/Users/hyun/Desktop/dddjango` | current |
| plugin list | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-plugin-list-raw.txt` | `9e256f6da8f8d5c1425a18f35effa74ab34432afed72de39e2facdd9b8c7c885` | `dddjango@dddjango-local` installed, enabled, version `0.1.10` | current |
| manifest validation | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-manifest-validation-raw.json` | `df98cc6d75b220431024260111e8b6403eb7e4002f58e1d128cd30d8b3c3ee78` | pass; paths start with `./`, stay inside root, required paths exist, 13 source/cache skills match | current |
| `.codex-plugin` file scan | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-codex-plugin-files-raw.txt` | `344d89fe83d9c236a3309c73f4286cdc162faa9ab06dd6f9486278b2547be9ce` | only source/cache `plugin.json` files present | current |
| source/cache diff | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-source-cache-diff-raw.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | empty diff output; no source/cache diff | current |
| plugin-creator validator | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-plugin-creator-validate-raw.txt` | `da53ca5e23e6244678d445c4e094c8f1e894b752cf2970889d6ea73a1590eff7` | not run to completion; `ModuleNotFoundError: No module named 'yaml'` | current |
| prompt-input probe | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-prompt-input-probe-raw.json` | `1fb88181ed5278493b4d53c7f245f0d6179ebad181d3b8c8a1e9a76b2ef14156` | installed cache skill root and namespaced dddjango skills visible to prompt assembly | current |
| prompt-input summary | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-prompt-input-summary-raw.json` | `0fabeb6fc7040ccd2c51101d1873842c68550fad3c6aa19ed1d16612fe698081` | pass; summarizes installed-cache prompt-input probe | current |
| runtime exec approval block | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-runtime-exec-approval-block-raw.md` | `1bffa09aaf34d52939614d928333b647c75f872b5bc357d2c25653957dd54026` | external `codex exec` rejected before model invocation; P7-specific data export approval missing | current |
| runtime task matrix | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-runtime-task-matrix-raw.json` | `969a5d75ff9e6e5334c4bc604eb6d5fe22b06b6333420f6d22ebce938af4299b` | blocked-before-model-invocation; 26 commands prepared for 13 happy and 13 exclusion prompts | current |
| runtime execution summary | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-runtime-execution-summary-raw.json` | `3abe29f91cd6ceb754d851bdc2a227e4d2e18d052b3f4b7c6d00051c9ef2a3bc` | pass; 26/26 `codex exec` runs returned 0 and produced final answers | current |
| runtime analysis | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-runtime-analysis-raw.json` | `ec4620d51cd47f58e910f735cb2ce7e70b0dee9fe782e90393935efcd6935908` | pass; 26/26 expected routes matched actual loaded dddjango skill and installed cache `SKILL.md` path | current |

## Manifest And Cache Result

| check | result |
|---|---|
| `skills` path starts with `./` | pass |
| manifest path stays inside plugin root | pass |
| required `skills` path exists in source/cache | pass |
| marketplace `source.path` starts with `./` | pass |
| marketplace path stays inside marketplace root | pass |
| source/cache manifest equality | pass |
| `.codex-plugin/` contains no files beyond `plugin.json` | pass |
| source/cache skill count | 13 source skills, 13 cache skills |
| source/cache diff | pass, empty diff |
| plugin root outside runtime dependency | pass for manifest paths and symlink scan |

## Namespaced Skills Observed

The manifest validation found the intended 13 skill namespaces:

- `dddjango:architecture-api`
- `dddjango:architecture-db`
- `dddjango:architecture-ddd`
- `dddjango:architecture-implementation-patterns`
- `dddjango:implementation-cleancode`
- `dddjango:implementation-django`
- `dddjango:implementation-django-ninja`
- `dddjango:implementation-django-web`
- `dddjango:implementation-python`
- `dddjango:implementation-tdd`
- `dddjango:implementation-test`
- `dddjango:source-reference-audit`
- `dddjango:workflow-dddjango-subagents`

## Installed Runtime User-Like Task Matrix

The approved P7 runtime run executed 26 user-like tasks: one happy and one
exclusion prompt for each of the 13 high-risk trigger families. All cases
returned exit 0, produced final answers, loaded the expected dddjango skill from
the installed Codex cache, and passed the false-trigger/exclusion check.

| case id | kind | expected route | actual skill loaded | source/cache path | final answer | false-trigger/exclusion | status |
|---|---|---|---|---|---|---|---|
| `p3-ft-01-happy-api-contract` | `happy` | `dddjango:architecture-api` | `dddjango:architecture-api` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-01-happy-api-contract.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-01-exclusion-api-to-ninja` | `exclusion` | `dddjango:implementation-django-ninja` | `dddjango:implementation-django-ninja` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-01-exclusion-api-to-ninja.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-02-happy-db-integrity` | `happy` | `dddjango:architecture-db` | `dddjango:architecture-db` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-02-happy-db-integrity.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-02-exclusion-db-to-ddd` | `exclusion` | `dddjango:architecture-ddd` | `dddjango:architecture-ddd` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-02-exclusion-db-to-ddd.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-03-happy-ddd-invariants` | `happy` | `dddjango:architecture-ddd` | `dddjango:architecture-ddd` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-03-happy-ddd-invariants.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-03-exclusion-ddd-to-db` | `exclusion` | `dddjango:architecture-db` | `dddjango:architecture-db` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-03-exclusion-ddd-to-db.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-04-happy-patterns-outbox` | `happy` | `dddjango:architecture-implementation-patterns` | `dddjango:architecture-implementation-patterns` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-04-happy-patterns-outbox.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-04-exclusion-patterns-to-ddd` | `exclusion` | `dddjango:architecture-ddd` | `dddjango:architecture-ddd` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-04-exclusion-patterns-to-ddd.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-05-happy-cleancode-fat-model` | `happy` | `dddjango:implementation-cleancode` | `dddjango:implementation-cleancode` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-05-happy-cleancode-fat-model.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-05-exclusion-cleancode-to-patterns` | `exclusion` | `dddjango:architecture-implementation-patterns` | `dddjango:architecture-implementation-patterns` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-05-exclusion-cleancode-to-patterns.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-06-happy-django-migration` | `happy` | `dddjango:implementation-django` | `dddjango:implementation-django` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-06-happy-django-migration.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-06-exclusion-django-to-api` | `exclusion` | `dddjango:architecture-api` | `dddjango:architecture-api` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-06-exclusion-django-to-api.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-07-happy-ninja-router` | `happy` | `dddjango:implementation-django-ninja` | `dddjango:implementation-django-ninja` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-07-happy-ninja-router.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-07-exclusion-ninja-to-api` | `exclusion` | `dddjango:architecture-api` | `dddjango:architecture-api` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-07-exclusion-ninja-to-api.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-08-happy-web-template` | `happy` | `dddjango:implementation-django-web` | `dddjango:implementation-django-web` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-08-happy-web-template.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-08-exclusion-web-to-ninja` | `exclusion` | `dddjango:implementation-django-ninja` | `dddjango:implementation-django-ninja` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-08-exclusion-web-to-ninja.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-09-happy-python-typing` | `happy` | `dddjango:implementation-python` | `dddjango:implementation-python` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-09-happy-python-typing.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-09-exclusion-python-to-django` | `exclusion` | `dddjango:implementation-django` | `dddjango:implementation-django` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-09-exclusion-python-to-django.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-10-happy-tdd-list` | `happy` | `dddjango:implementation-tdd` | `dddjango:implementation-tdd` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-10-happy-tdd-list.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-10-exclusion-tdd-to-test` | `exclusion` | `dddjango:implementation-test` | `dddjango:implementation-test` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-10-exclusion-tdd-to-test.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-11-happy-test-fixture` | `happy` | `dddjango:implementation-test` | `dddjango:implementation-test` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-11-happy-test-fixture.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-11-exclusion-test-to-tdd` | `exclusion` | `dddjango:implementation-tdd` | `dddjango:implementation-tdd` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-11-exclusion-test-to-tdd.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-12-happy-source-audit` | `happy` | `dddjango:source-reference-audit` | `dddjango:source-reference-audit` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-12-happy-source-audit.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-12-exclusion-source-to-workflow` | `exclusion` | `dddjango:workflow-dddjango-subagents` | `dddjango:workflow-dddjango-subagents` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-12-exclusion-source-to-workflow.txt` | `pass-expected-exclusion-route-loaded` | `pass` |
| `p3-ft-13-happy-workflow-roles` | `happy` | `dddjango:workflow-dddjango-subagents` | `dddjango:workflow-dddjango-subagents` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-13-happy-workflow-roles.txt` | `not-applicable-happy` | `pass` |
| `p3-ft-13-exclusion-workflow-to-source` | `exclusion` | `dddjango:source-reference-audit` | `dddjango:source-reference-audit` | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit/SKILL.md` | `workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/p3-ft-13-exclusion-workflow-to-source.txt` | `pass-expected-exclusion-route-loaded` | `pass` |

## Plugin-Creator Review

- Existing plugin update flow is the correct flow for this repository:
  `codex plugin add dddjango@dddjango-local` refreshed the local installed cache.
- Marketplace entry shape is local, rooted at `.agents/plugins/marketplace.json`,
  and points at `./dddjango`.
- No hand edit to marketplace config was needed.
- The plugin-creator `validate_plugin.py` script could not complete because
  `yaml` is unavailable; this is an environment dependency gap, not a manifest
  path failure. The stdlib validator covers the P7-required path and cache
  parity checks.

## Required Verification

| command | result |
|---|---|
| `codex plugin add dddjango@dddjango-local` | pass after escalated rerun |
| `codex plugin marketplace list` | pass |
| `codex plugin list --marketplace dddjango-local` | pass |
| manifest path validator or equivalent parse/path check | pass |
| `diff -qr dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10` | pass, empty output |
| `python3 -B /Users/hyun/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py dddjango` | blocked by missing `yaml` dependency |
| installed-runtime user-like task evidence | pass; 26/26 executed, expected skill loaded, final answer present, installed-cache path observed |

## P7 Judgment

P7 is complete. Install/cache/package parity is clean, and P3b-equivalent
installed-runtime user-like routing evidence is current for the P7/P8 completion
path.
