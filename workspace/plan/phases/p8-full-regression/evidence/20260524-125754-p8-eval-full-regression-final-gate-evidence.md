수정 대상: `workspace/develop/eval/**`, `workspace/scripts/**`, `workspace/plan/phases/p8-full-regression/**`, `workspace/plan/indexes/**`, `workspace/plan/status/phase_status.md`

# P8 Full Regression Final Evidence

## Status

P8 is complete. Final P5/P6 model-backed installed-runtime full regression
artifacts pass, P7 equivalent installed-runtime evidence is current, raw/report
leakage is zero, current-file fingerprints match, and independent review has
Blocker 0, Major 0, and Open Minor 0.

## Primary Aggregate Artifact

| item | value |
|---|---|
| raw artifact | `workspace/plan/phases/p8-full-regression/evidence/20260524-125754-p8-eval-full-regression-aggregate-check-raw.json` |
| digest | `0b2765ee93b97b6579a22efd46dc5a70c6878265bcb23f209fb17b46d951ec97` |
| result | pass |
| current-file match | current |

Aggregate command:

```bash
python3 -B workspace/scripts/p8_full_regression_check.py --review-raw workspace/plan/reviews/raw/20260524-125754-p8-review-full-regression-final-raw.md --review-summary workspace/plan/reviews/summaries/20260524-125754-p8-review-full-regression-final-review.md --output workspace/plan/phases/p8-full-regression/evidence/20260524-125754-p8-eval-full-regression-aggregate-check-raw.json
```

Observed result:

```json
{"status": "pass", "failures": []}
```

## Final Full Runs

| bucket | run id | targeted 2x | all-cases raw | validate-run | not scored | raw digest | metadata digest |
|---|---|---|---|---|---:|---|---|
| P5 individual skills | `p8-full-regression-p5-model-installed-runtime` | pass, stable-pass | pass, 26/26 | pass, failures `[]` | 0 | `a0b7f5b1adb53f7f9acacd4e49b23c7f53f8d64642f85c772e852de8c0b5d84b` | `d4ae063b07ee71de88de0245c3d45cf71ba7f3ebe503edefaa15e1c1d86a8703` |
| P6 integration flows | `p8-full-regression-p6-model-installed-runtime` | pass, stable-pass | pass, 4/4 | pass, failures `[]` | 0 | `67a3cd5e907f9f1000d4d0364115cd7677c06917d99474c3f25db12ab476ad9d` | `5877c95ce08e1394894192d703e16077411caf2623c0daa207cecbd94848f078` |

P5 commands:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime model-run-targeted-suite --bucket individual-skills --run-id p8-full-regression-p5-model-installed-runtime --iterations 2 --runtime-channel external --work-root /private/tmp/dddjango-p8-model --variants with-plugin
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime model-run-bucket --bucket individual-skills --run-id p8-full-regression-p5-model-installed-runtime --runtime-channel external --work-root /private/tmp/dddjango-p8-model --variants with-plugin
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime render-report
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime validate-run
```

P6 commands:

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime model-run-targeted-suite --bucket integration-flows --run-id p8-full-regression-p6-model-installed-runtime --iterations 2 --runtime-channel external --work-root /private/tmp/dddjango-p8-model --variants with-plugin
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime model-run-bucket --bucket integration-flows --run-id p8-full-regression-p6-model-installed-runtime --runtime-channel external --work-root /private/tmp/dddjango-p8-model --variants with-plugin
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime render-report
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime validate-run
```

## Report And Leakage

| check | result |
|---|---|
| P5 report raw digest | matches final P5 raw digest |
| P6 report raw digest | matches final P6 raw digest |
| P5 report HTML digest | `5264bb28b1ba3da2a0ef9a5bfdbb7fea393e367b84ccb1f26a01578e3d7a2663` |
| P6 report HTML digest | `75f692e440664159eff2ea41a081ec20b377e157c6adc99588b9c2063e7e8c21` |
| HTML latest | no separate `latest` alias exists; final report paths are explicit and contain final run id/raw digest |
| raw/report leakage scan | pass; zero hits for `/Users/hyun`, `/private/tmp`, `__FORBIDDEN_LOCAL_PATH_SENTINEL__`, `__PRIVATE_FIELD_SENTINEL__` |

Leakage command:

```bash
rg -n "/Users/hyun|/private/tmp|__FORBIDDEN_LOCAL_PATH_SENTINEL__|__PRIVATE_FIELD_SENTINEL__" workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime/raw workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime/report workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime/raw workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime/report
```

Observed result: no matches.

## P7 Current Evidence

| check | result |
|---|---|
| source/cache diff | pass, empty |
| P7 runtime analysis | pass |
| P7 case/family coverage | 26 cases, 13 high-risk trigger families |
| P7 failures | 0 |
| routing/cache/final-answer pass counts | 26 / 26 / 26 |
| aggregate P7 section | pass |

P7 source/cache command:

```bash
diff -qr dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10
```

Observed result: empty output.

## Independent Review

| item | value |
|---|---|
| raw review | `workspace/plan/reviews/raw/20260524-125754-p8-review-full-regression-final-raw.md` |
| summary | `workspace/plan/reviews/summaries/20260524-125754-p8-review-full-regression-final-review.md` |
| closure | `workspace/plan/reviews/closures/20260524-125754-p8-review-full-regression-final-closure.md` |
| finding counts | Blocker 0, Major 0, Open Minor 0 |

## Runner And Validator Fixes

The final P8 runner includes two narrow fixes:

- persisted model execution artifacts redact local runtime paths and fail
  `validate-run` if local path/private sentinel leakage remains;
- P5 scoring resolves a final-answer `loaded_skill` self-report typo only when
  required claims are complete and raw JSONL shows the expected installed-cache
  `SKILL.md` was actually loaded.

The P5 targeted suite was rerun after this fix and is stable-pass across two
iterations.

## Executed Checks

| command/run | result |
|---|---|
| `diff -qr dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10` | pass, empty output |
| `shasum -a 256 dddjango/.codex-plugin/plugin.json /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/.codex-plugin/plugin.json .agents/plugins/marketplace.json` | source/cache manifest match; marketplace digest recorded |
| `python3 -B workspace/scripts/p5_individual_eval.py ... validate-run` on previous P5 model-backed bucket before the runner fix | pass, failures `[]`; historical P5 evidence only |
| `python3 -B workspace/scripts/p6_integration_eval.py ... validate-run` on previous P6 model-backed bucket before the runner fix | pass, failures `[]`; historical P6 evidence only |
| P7 runtime-analysis raw summary | pass; 26 cases, 13 families, failure count 0 |
| `python3 -B workspace/scripts/test_p5_individual_eval.py` | pass; 15 tests |
| `python3 -B workspace/scripts/test_p6_integration_eval.py` | pass; 6 tests |
| `python3 -B workspace/scripts/test_p8_full_regression_check.py` | pass; 2 tests |
| `python3 -B workspace/scripts/test_eval_skeleton.py` | pass; 8 tests |
| P5 targeted full-regression run, 2 iterations | pass; stable-pass |
| P5 all-cases full-regression bucket | pass; 26 pass, 0 partial, 0 fail, 0 not-scored |
| P5 `validate-run` | pass; failures `[]` |
| P6 targeted full-regression run, 2 iterations | pass; stable-pass |
| P6 all-cases full-regression bucket | pass; 4 pass, 0 partial, 0 fail, 0 not-scored |
| P6 `validate-run` | pass; failures `[]` |
| raw/report leakage scan | pass; no matches |
| `python3 -B workspace/scripts/p8_full_regression_check.py ... --output workspace/plan/phases/p8-full-regression/evidence/20260524-125754-p8-eval-full-regression-aggregate-check-raw.json` | pass; failures `[]` |

## Narrow Runner Fix

The P8 leakage gate scans persisted raw/report artifacts for local path and
private sentinel leakage. The model-backed runner previously persisted absolute
runtime paths in execution metadata and captured Codex JSONL stdout/stderr.

The narrow fix:

- redacts persisted `/Users/hyun`, installed cache root, and `/private/tmp`
  paths in model stdout/stderr and execution metadata;
- stores digests for actual command, cwd, and final path instead of exposing the
  concrete local paths;
- uses `installed-cache:<relative-path>` keys for installed cache metadata
  fingerprints and resolves them during validation;
- fails `validate-run` when persisted raw/report artifacts contain unredacted
  local path or private sentinel markers.

Unit tests now cover P5 and P6 model execution redaction.

## Aggregate P8 Validator

`workspace/scripts/p8_full_regression_check.py` was added as the final local
aggregate validator. It checks:

- P5 and P6 final raw/report/validation status, raw digest, report staleness,
  status counts, missing/malformed/conflict semantics, current metadata
  fingerprints, targeted-suite two-iteration stability, and raw/report leakage.
- P7 source/cache current state, runtime-analysis high-risk trigger coverage,
  and manifest digest freshness.
- Final independent review raw/summary existence and finding counts.

The aggregate result before final full run was an expected fail because P8 final
P5/P6 raw/report/validation and review artifacts were missing. The final
aggregate result after approved model-backed execution is:

| item | value |
|---|---|
| raw artifact | `workspace/plan/phases/p8-full-regression/evidence/20260524-125754-p8-eval-full-regression-aggregate-check-raw.json` |
| digest | `0b2765ee93b97b6579a22efd46dc5a70c6878265bcb23f209fb17b46d951ec97` |
| result | pass; failures `[]` |
| P7 section | pass |

## P8 Judgment

P8 is complete. The final full regression passes all requested gates:
`not-scored=0`, missing/malformed oracle 0, expected-outcome conflict 0,
validator false positive 0, local path/private leakage 0, stale report 0,
current-file fingerprint mismatch 0, unresolved flaky history 0, current P7
equivalent installed-runtime evidence, and final independent review with
Blocker 0, Major 0, Open Minor 0.
