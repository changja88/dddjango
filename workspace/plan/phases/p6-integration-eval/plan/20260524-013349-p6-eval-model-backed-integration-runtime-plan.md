수정 대상: workspace/develop/eval/runs/p6-integration-flows-model-approved-targeted-with-plugin-v2/, workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2/

# P6 Model-Backed Integration Runtime Plan

## Commands

Run model-backed targeted suite:

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-model-approved-targeted-with-plugin-v2 model-run-targeted-suite --bucket integration-flows --run-id p6-integration-flows-model-approved-targeted-with-plugin-v2 --iterations 2 --runtime-channel external --work-root /private/tmp/dddjango-p6-model --variants with-plugin
```

Run affected bucket all-cases:

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2 model-run-bucket --bucket integration-flows --run-id p6-integration-flows-model-approved-bucket-with-plugin-v2 --runtime-channel external --work-root /private/tmp/dddjango-p6-model --variants with-plugin
```

Attach the stable targeted-suite proof to the affected bucket artifact:

```bash
cp workspace/develop/eval/runs/p6-integration-flows-model-approved-targeted-with-plugin-v2/raw/targeted-suite.json workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2/raw/targeted-suite.json
```

Regenerate report and validate:

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2 render-report
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2 validate-run
```

Run final verification:

```bash
python3 -B workspace/scripts/test_p6_integration_eval.py
python3 -B workspace/scripts/test_p5_individual_eval.py
python3 -B workspace/scripts/test_eval_skeleton.py
python3 -B workspace/scripts/validate_plan_governance.py
git diff --check
```

## Completion Gate

Close P6 only if:

- targeted 2x status is `pass`
- targeted variance status is `stable-pass`
- affected bucket all-cases status is `pass`
- affected bucket `not-scored=0`
- missing/malformed oracle or answer failures are 0
- responsibility intrusion, false claim, and source leakage failures are 0
- raw/report/validation raw digests match
- current metadata digest matches run metadata digest
