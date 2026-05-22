# P4 Eval Mini-Bucket Skeleton Evidence

## Scope

This evidence covers fixture-only eval mechanics for P4:

- eval protocol
- mini-bucket fixture matrix
- runner/scorer
- validator
- report renderer
- raw/report/validator consistency

Runtime-routing evidence is deferred by
`workspace/plan/decisions/ADR-0004-p3-runtime-forward-test-deferral.md`.
This evidence does not prove installed Codex runtime skill routing.

## Raw Artifacts

| artifact | path |
|---|---|
| eval protocol | `workspace/plan/governance/eval_protocol.md` |
| runner/scorer/validator/report CLI | `workspace/scripts/eval_skeleton.py` |
| unit tests | `workspace/scripts/test_eval_skeleton.py` |
| fixture matrix source | `workspace/develop/eval/fixtures/mini-bucket/cases.json` |
| run-one raw output | `workspace/develop/eval/runs/p4-mini-bucket-fixture/raw/one.json` |
| full run raw output | `workspace/develop/eval/runs/p4-mini-bucket-fixture/raw/run.json` |
| report JSON | `workspace/develop/eval/runs/p4-mini-bucket-fixture/report/report.json` |
| report HTML | `workspace/develop/eval/runs/p4-mini-bucket-fixture/report/report.html` |
| validator result | `workspace/develop/eval/runs/p4-mini-bucket-fixture/validation/validate-run.json` |

## Commands And Results

| command | exit | result |
|---|---:|---|
| `python3 -B workspace/scripts/test_eval_skeleton.py` | 0 | 8 unit tests passed |
| `python3 -B workspace/scripts/eval_skeleton.py --fixture-root workspace/develop/eval/fixtures/mini-bucket --output-dir workspace/develop/eval/runs/p4-mini-bucket-fixture run-one --case-id p4-pass --variant baseline` | 0 | pass fixture scored as `pass` |
| `python3 -B workspace/scripts/eval_skeleton.py --fixture-root workspace/develop/eval/fixtures/mini-bucket --output-dir workspace/develop/eval/runs/p4-mini-bucket-fixture run-bucket --bucket mini-bucket --run-id p4-mini-bucket-fixture` | 1 | expected fixture run failure: `pass=6`, `partial=2`, `fail=12`, `not-scored=4` |
| `python3 -B workspace/scripts/eval_skeleton.py --output-dir workspace/develop/eval/runs/p4-mini-bucket-fixture render-report` | 0 | report regenerated from current raw; CLI output names `report/report.json`, `report/report.html`, and `raw/run.json` |
| `python3 -B workspace/scripts/eval_skeleton.py --output-dir workspace/develop/eval/runs/p4-mini-bucket-fixture validate-run` | 1 | expected validator failure: `not-scored-present`, count `4` |
| `rg -n "<redacted-local-path-marker>\|<redacted-private-field-marker>" workspace/develop/eval/runs/p4-mini-bucket-fixture workspace/plan/governance/eval_protocol.md workspace/plan/phases/p4-eval-skeleton` | 1 | no private marker literal persisted in run/report/protocol/phase evidence surfaces; marker names are redacted in this evidence row |
| `python3 -B workspace/scripts/validate_plan_governance.py` | 0 | `OK: plan governance validation passed` |
| `git diff --check` | 0 | no whitespace errors |

The nonzero `run-bucket` and `validate-run` exits are expected P4 evidence:
the mini-bucket intentionally contains failure fixtures, and `not-scored` must
keep a run failed rather than being treated as success.

## Fixture Result Matrix

| case | baseline | with-plugin | observed failure semantics |
|---|---:|---:|---|
| `p4-pass` | pass | pass | - |
| `p4-partial` | partial | partial | `oracle-partial` |
| `p4-fail` | fail | fail | `oracle-mismatch` |
| `p4-missing-oracle` | pass | not-scored | `missing-oracle` |
| `p4-malformed-oracle` | not-scored | pass | `malformed-oracle` |
| `p4-stale-report` | fail | fail | `stale-report` |
| `p4-local-path-leak` | fail | fail | `raw-leakage`, `persisted-leakage` |
| `p4-sanitizer-only-leak` | fail | fail | `raw-leakage` |
| `p4-private-field-leak` | fail | fail | `raw-leakage`, `persisted-leakage` |
| `p4-expected-outcomes-conflict` | not-scored | not-scored | `expected-outcomes-conflict` |
| `p4-korean-negation-false-positive` | pass | pass | - |
| `p4-prompt-only-command-claim` | fail | fail | `missing-structured-command-evidence` |

Validator result:

- `status`: `fail`
- `fixture_mismatch_count`: `0`
- `status_counts`: `{"pass": 6, "partial": 2, "fail": 12, "not-scored": 4}`
- `observed_failure_semantics`: `expected-outcomes-conflict`,
  `malformed-oracle`, `missing-oracle`,
  `missing-structured-command-evidence`, `oracle-mismatch`,
  `oracle-partial`, `persisted-leakage`, `raw-leakage`, `stale-report`

## Digest

| artifact | sha256 |
|---|---|
| `workspace/plan/governance/eval_protocol.md` | `e6b2195bed0423a331f53b2a9793e6726bb2ed3ec3abb84d993a933711a6333f` |
| `workspace/scripts/eval_skeleton.py` | `985c65dae7fd0da228fd0dc771fbe43e45e8eca0c3d55c5adf8587b6915a03da` |
| `workspace/scripts/test_eval_skeleton.py` | `aa1fc8dcaab2f382aaa3772fa8acee20965210737439d2afe283325194d53f64` |
| `workspace/develop/eval/fixtures/mini-bucket/cases.json` | `d8f6cbf8f5e8ff0f0ecae95d60750a460c6b39999a4bba2fdd9c7f02dafcb9c4` |
| `workspace/develop/eval/runs/p4-mini-bucket-fixture/raw/run.json` | `ebee44fc7d45f2306e69d8d2f2533f65814b72b1ec61f5ef833d8eac536dfbf8` |
| `workspace/develop/eval/runs/p4-mini-bucket-fixture/report/report.json` | `1072f7f10b9432b44a8637893e676c83b4fd83e9f26d9bc31bcfada7ddde552c` |
| `workspace/develop/eval/runs/p4-mini-bucket-fixture/report/report.html` | `a5c9378cb7a0adb8b81ca08dbfa56fcdc8ed151eb3f1c4bebea1c393cb807b2f` |
| `workspace/develop/eval/runs/p4-mini-bucket-fixture/validation/validate-run.json` | `13eb4be95530235afe84f5cacb965cff10cf4500cfc2c906199e686bdd695af9` |

Raw run internal digest:
`505cc3a708a3a99f9b462756f416956737993f3ae012377c2d241b6fd2d16720`.
`report/report.json.source_raw_digest` and
`validation/validate-run.json.raw_digest` match this value.

Current-file match status: current after the 2026-05-23 rerun for the files
listed in this digest table. This evidence file's own digest is recorded in
`workspace/plan/indexes/evidence_index.md` after final evidence edits, because
embedding a file's own final digest in its contents would immediately change
that digest.

## Result

P4 fixture-only eval skeleton behavior is verified:

- pass, partial, fail, and not-scored are separated.
- missing and malformed oracles are not-scored and keep the run failed.
- stale report, raw leakage, persisted leakage, sanitizer-only leakage, and
  private-field leakage are failures.
- Korean negation prose is not treated as routing evidence.
- command claims require structured command/tool events.
- report rows and status counts match raw artifacts.

P4 remains limited by deferred P3b runtime-routing evidence. P7/P8 still require
P3b or equivalent installed-runtime user-like evidence before final plugin
completion can be claimed.
