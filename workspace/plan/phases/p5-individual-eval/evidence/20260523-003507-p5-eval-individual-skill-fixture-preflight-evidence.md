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
| blocker | P4.5 runtime parity is `not-started`; model-backed installed-runtime run not executed |

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
| `python3 -B workspace/scripts/test_p5_individual_eval.py` | stdout | pass, 5 tests |
| `python3 -B workspace/scripts/test_eval_skeleton.py` | stdout | pass, 7 tests |
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

## Digests

| artifact | digest |
|---|---|
| `workspace/scripts/p5_individual_eval.py` | `88cec02563faa5f83b3228c3d3c6c357b2c586a58d97710e4df4fcb54955cb07` |
| `workspace/scripts/test_p5_individual_eval.py` | `87318cec56eba4f1fb9d24561cccc9220f47d33a14ef0d3ee7926e8af489622e` |
| `workspace/develop/eval/fixtures/individual-skills/cases.json` | `2dafba64cc23479eb0b4f8d9d04f33c5886f3a9f84bb5b31b6a94af329287e4e` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/raw/run.json` | `97b6a92c3103438ca80627b6e671c1a64d7edf1466383d0fbca32e3098469fb6` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/raw/run.json` internal `raw_digest` | `7dba58d87804a50ce249ecaa5ea47b0b3ad5e0eef0ba5d1ebda87b479597bb88` |
| run metadata digest | `9d4ba93b0946ef38278e85489d303d4fdf222365dc542528aff0ee0d81a4cc02` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/raw/targeted-suite.json` | `53040ff613a85c7519c6451f1589e2a74e9a94204fbbd7943ef6e7419a6994cf` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/report/report.json` | `c4bb90c62fc3aa3c662dcb29fa80162ae23d2809f1eb1d5820997d1318c15eca` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/report/report.html` | `c13d8d9b89e759ea46f945e515644245983d0c68c50ed348860cdc005cab2226` |
| `workspace/develop/eval/runs/p5-individual-skills-fixture/validation/validate-run.json` | `95a84fcbe0df0edf2d83ddebece7df5868c4dbb463154b9d8434e3183373c0ed` |

## Current-File Match Status

`validate-run` recomputed the metadata digest for the cases file, P1.5 usage
cards, P4 eval protocol, P5 runner, and all `dddjango/skills/*/SKILL.md` files.
It returned `pass` with no failures.

## Limitation

This evidence proves only the deterministic P5 fixture preflight bucket. It is
not model-backed, not installed-runtime evidence, and not valid P5 completion
evidence while P4.5 remains incomplete.
