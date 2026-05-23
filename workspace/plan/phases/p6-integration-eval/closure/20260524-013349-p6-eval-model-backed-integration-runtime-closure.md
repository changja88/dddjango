# P6 Model-Backed Integration Runtime Closure

## Decision

P6 Integration Eval is complete.

Completion is based on model-backed installed-runtime v2 artifacts:

- targeted 2x:
  `workspace/develop/eval/runs/p6-integration-flows-model-approved-targeted-with-plugin-v2/`
- affected bucket all-cases:
  `workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2/`

The fixture preflight remains useful evaluator coverage but is not P6 completion
evidence.

## Gate Results

| gate | result |
|---|---|
| all new integration cases targeted pass | pass |
| model-backed targeted iterations | pass, 2 iterations |
| targeted variance | stable-pass |
| affected bucket all-cases | pass |
| affected bucket `not-scored` | 0 |
| missing/malformed oracle or answer | 0 |
| responsibility intrusion / false claim / source leakage | 0 |
| raw/report/validation digest match | pass |
| current metadata digest match | pass |

## Residual Risk

P3b runtime-routing evidence remains deferred under ADR-0004. P7/P8 completion
still requires P3b or equivalent installed-runtime user-like evidence.

The failed v1 targeted attempt is classified as eval-pack prompt/scorer gap and
is not used as completion evidence.

## Final Verification

- `python3 -B workspace/scripts/test_p6_integration_eval.py`: 6 tests, OK
- `python3 -B workspace/scripts/test_p5_individual_eval.py`: 13 tests, OK
- `python3 -B workspace/scripts/test_eval_skeleton.py`: 8 tests, OK
- `python3 -B workspace/scripts/validate_plan_governance.py`: OK
- `python3 -B workspace/scripts/p6_integration_eval.py ... validate-run`: pass, failures `[]`
- `git diff --check`: pass
