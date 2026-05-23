수정 대상: `workspace/plan/phases/p5-individual-eval/`, `workspace/plan/indexes/`, `workspace/plan/status/phase_status.md`

# P5 Model-Backed Installed-Runtime Analysis

## Scope

This work item attempts to move P5 from fixture-scored preflight evidence to the
required model-backed installed-runtime individual skill eval evidence.

P4.5 runtime parity is complete and proves source/cache/install/discovery parity.
It does not prove runtime-routing behavior and does not replace P5 model-backed
case execution.

## Current Preconditions

| precondition | observed state | result |
|---|---|---|
| P4.5 runtime parity | `complete` in `workspace/plan/status/phase_status.md` | satisfied |
| dddjango local marketplace | `dddjango-local` configured | satisfied by P4.5 evidence |
| installed plugin | `dddjango@dddjango-local` installed and enabled | satisfied |
| P5 fixture bucket | clean/scored, `model_backed=false` | preflight only |
| model-backed runtime | external Codex/OpenAI data-export approval granted by user; local OSS servers unavailable | satisfied via approved external run |

## Individual Eval Matrix

The P5 case surface remains the existing trigger-family matrix: one positive and
one negative case for each P1.5 trigger family. No new case count expansion is
needed before the first model-backed run.

| trigger family | positive case | negative case |
|---|---|---|
| REST API contract | `p5-architecture-api-positive` | `p5-architecture-api-negative` |
| Relational DB integrity and rollout | `p5-architecture-db-positive` | `p5-architecture-db-negative` |
| Domain modeling and invariants | `p5-architecture-ddd-positive` | `p5-architecture-ddd-negative` |
| Implementation architecture patterns | `p5-architecture-implementation-patterns-positive` | `p5-architecture-implementation-patterns-negative` |
| Maintainability review and refactor | `p5-implementation-cleancode-positive` | `p5-implementation-cleancode-negative` |
| Django ORM/service/migration implementation | `p5-implementation-django-positive` | `p5-implementation-django-negative` |
| Django Ninja API implementation | `p5-implementation-django-ninja-positive` | `p5-implementation-django-ninja-negative` |
| Django server-rendered web | `p5-implementation-django-web-positive` | `p5-implementation-django-web-negative` |
| Python language and typing implementation | `p5-implementation-python-positive` | `p5-implementation-python-negative` |
| TDD workflow | `p5-implementation-tdd-positive` | `p5-implementation-tdd-negative` |
| pytest and Django test mechanics | `p5-implementation-test-positive` | `p5-implementation-test-negative` |
| Source/reference governance | `p5-source-reference-audit-positive` | `p5-source-reference-audit-negative` |
| Coordinated dddjango workflow | `p5-workflow-dddjango-subagents-positive` | `p5-workflow-dddjango-subagents-negative` |

## Runtime Channel Classification

| channel | command shape | result | classification |
|---|---|---|---|
| external Codex/OpenAI | `codex exec --json --ephemeral ...` through `workspace/scripts/p5_individual_eval.py` | approved by user; targeted 2x and affected bucket all-cases pass | used for P5 completion |
| local Ollama | `codex --oss --local-provider ollama ...` | no running Ollama server detected | unavailable local provider |
| local LM Studio | `codex --oss --local-provider lmstudio ...` | LM Studio is not responding | unavailable local provider |

## Decision

The P5 case count remains the existing one-positive/one-negative-per-trigger
family matrix. The installed-runtime completion evidence is scoped to the
`with-plugin` variant because baseline uses `--ignore-user-config` and is not
installed-plugin runtime evidence.

The model-backed run required narrow runner/scorer fixes:

- accept process skills plus the expected dddjango skill in structured
  `loaded_skill` output;
- accept explicit `acceptable_loaded_skills` for negative surfaces where the
  correct result is "not this skill" and more than one behavior skill is valid;
- allow `validate-run` to accept a single all-cases bucket only when a matching
  stable two-iteration targeted-suite proof is present.

P5 individual eval is complete based on
`p5-individual-skills-model-approved-targeted-with-plugin-v4` and
`p5-individual-skills-model-approved-bucket-with-plugin-v4`. This does not
claim integration eval evidence and does not resolve the deferred P3b
runtime-routing gate for P7/P8.
