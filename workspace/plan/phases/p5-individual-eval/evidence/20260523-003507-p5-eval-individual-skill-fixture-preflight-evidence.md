# P5 Individual Skill Fixture Preflight Evidence

## Summary

| field | value |
|---|---|
| work item id | `20260523-003507-p5-eval-individual-skill-fixture-preflight` |
| phase | `p5-individual-eval` |
| bucket | `individual-skills` |
| run id | `p5-individual-skills-fixture` |
| run mode | `fixture-scored-p5-preflight` |
| model-backed | `false` |
| P5 completion status | incomplete |
| blocker | model-backed installed-runtime run not executed |

## Individual Eval Matrix

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

## Commands And Results

| command/run | raw artifact | result |
|---|---|---|
| `python3 -B workspace/scripts/test_p5_individual_eval.py` | stdout | pass, 13 tests |
| `python3 -B workspace/scripts/test_eval_skeleton.py` | stdout | pass, 8 tests |
| `python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-fixture run-targeted-suite --bucket individual-skills --run-id p5-individual-skills-fixture --iterations 2` | `workspace/develop/eval/runs/p5-individual-skills-fixture/raw/targeted-suite.json` | pass, 2 iterations |
| `python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-fixture run-bucket --bucket individual-skills --run-id p5-individual-skills-fixture` | `workspace/develop/eval/runs/p5-individual-skills-fixture/raw/run.json` | pass, 52 pass / 0 partial / 0 fail / 0 not-scored |
| `python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-fixture render-report` | `workspace/develop/eval/runs/p5-individual-skills-fixture/report/report.json`, `workspace/develop/eval/runs/p5-individual-skills-fixture/report/report.html` | pass |
| `python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-fixture validate-run` | `workspace/develop/eval/runs/p5-individual-skills-fixture/validation/validate-run.json` | pass, failures `[]` |
| raw/report/validation consistency check | stdout | raw status `pass`; status counts match; report digest matches validation raw digest; metadata digest current |
| `rg -n "__FORBIDDEN_LOCAL_PATH_SENTINEL__|__PRIVATE_FIELD_SENTINEL__" ...` | stdout | no matches, exit 1 expected |

## Run Results

| check | result |
|---|---|
| targeted iterations | 2 |
| targeted iteration 1 | pass, 52 pass / 0 partial / 0 fail / 0 not-scored |
| targeted iteration 2 | pass, 52 pass / 0 partial / 0 fail / 0 not-scored |
| affected bucket all-cases | pass |
| affected bucket not scored | 0 |
| missing/malformed oracle or answer findings | 0 |
| validate-run | pass |
| report/raw row consistency | pass |
| current-file metadata digest | pass |
| runtime parity precondition metadata | `complete` |

## Digests

| artifact | digest |
|---|---|
| `workspace/scripts/p5_individual_eval.py` | `7db3628e4a243f84c9de8963288eef5dd86933773ca37f520e44fb0c90945b6b` |
| `workspace/scripts/test_p5_individual_eval.py` | `3e0007bb69b84680107535e7de65326d5043b3adade0e0d0484e59e47609fd8a` |
| `workspace/develop/eval/fixtures/individual-skills/cases.json` | `b5a53b96a15d887d13c74b232d31de8d59fa7de989b1b31369513b988c47376a` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/raw/run.json` | `f1e8c44d0b5e2dc878c10413f906a3dd0b117cb8a8250b22268ebcad880d172b` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/raw/run.json` internal `raw_digest` | `f692b0cc9bbb67f257381524ab9f42f2998dbeebabd15d424c326c9a0012be83` |
| run metadata digest | `502cb2b7fc183d42a9e88e5606a808cff7e73bc70a504bb58db985b93ae44bfd` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/report/report.json` | `928bdb112ef9eb9c30814436b277caf5260667bd5147455a232806fb99cb321b` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/validation/validate-run.json` | `2114d557439774bcf0df6ba51805425eb8ab2c27cbc0ede52fc24a9035560d04` |

## Current-File Match Status

`validate-run` recomputed the metadata digest for the cases file, P1.5 usage
cards, P4 eval protocol, P5 runner, plugin manifests, and all
`dddjango/skills/*/SKILL.md` files. It returned `pass` with no failures.

## Limitation

This evidence proves only the deterministic P5 fixture preflight bucket. It is
not model-backed, not installed-runtime evidence, and not valid P5 completion
evidence.
