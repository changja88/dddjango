# P6 Model-Backed Integration Runtime Evidence

## Status

Result: `pass`

P6 completion evidence uses model-backed installed-runtime v2 artifacts, not the
fixture preflight and not P5 individual cases.

## Model-Backed Targeted 2x

Command:

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-model-approved-targeted-with-plugin-v2 model-run-targeted-suite --bucket integration-flows --run-id p6-integration-flows-model-approved-targeted-with-plugin-v2 --iterations 2 --runtime-channel external --work-root /private/tmp/dddjango-p6-model --variants with-plugin
```

Result:

```json
{"status": "pass", "iterations": 2, "variance_status": "stable-pass"}
```

Raw artifact:
`workspace/develop/eval/runs/p6-integration-flows-model-approved-targeted-with-plugin-v2/raw/targeted-suite.json`

Digest: `targeted_suite=9c2085b5ac75ccd7b34f214e626dd7918fa96e11d76bd3d17a978c7d79e2e950`

## Affected Bucket All-Cases

Command:

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2 model-run-bucket --bucket integration-flows --run-id p6-integration-flows-model-approved-bucket-with-plugin-v2 --runtime-channel external --work-root /private/tmp/dddjango-p6-model --variants with-plugin
```

Result:

```json
{"status": "pass", "status_counts": {"pass": 4, "partial": 0, "fail": 0, "not-scored": 0}}
```

Raw artifact:
`workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2/raw/run.json`

Digest:

- `bucket_raw_file=1e82cdcae3a5f3e9b27830d138d9436e85367257841b1d3cdc55b4b48a559221`
- `bucket_raw_digest=1a21d81efced72178b85a9e745b4b1a2d9b00da53264a38c351843d140661def`
- `bucket_report=bb618850eeaf44fa87200ebb4c91f4cc7d282f3a6f69444ef77f309fcde78dae`
- `bucket_validation=4612d1fa4d136f14d7568b33cd778d843eb2d4fbe6f7b4338cb78b6b8950b02f`
- `metadata=c46855b7e0b0bd1cb1d2a98b288ad622194eeeb5639fb2e0f2898792f3238ac7`

## Validate-Run

Command:

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v2 validate-run
```

Result:

```json
{"status": "pass", "failures": []}
```

Raw/report/validation digest check:

- raw internal digest: `1a21d81efced72178b85a9e745b4b1a2d9b00da53264a38c351843d140661def`
- report `source_raw_digest`: `1a21d81efced72178b85a9e745b4b1a2d9b00da53264a38c351843d140661def`
- validation `raw_digest`: `1a21d81efced72178b85a9e745b4b1a2d9b00da53264a38c351843d140661def`
- raw metadata digest: `c46855b7e0b0bd1cb1d2a98b288ad622194eeeb5639fb2e0f2898792f3238ac7`
- validation metadata digest: `c46855b7e0b0bd1cb1d2a98b288ad622194eeeb5639fb2e0f2898792f3238ac7`

Current-file match: `current`.

## Clean/Scored Gate

- `case_count=4`
- `result_count=4`
- `model_backed=true`
- `variants=["with-plugin"]`
- `status_counts={"pass": 4, "partial": 0, "fail": 0, "not-scored": 0}`
- missing/malformed oracle or answer failure semantics: 0
- responsibility intrusion, false claim, source leakage failure semantics: 0

## Responsibility Boundary And Handoff Summary

- Composite flow: passes with workflow coordination plus DDD, DB, API, Django,
  and Test handoff skills represented in structured loaded-skill evidence.
- Tiny edit restraint: passes with no workflow/subagent overreach; empty or
  `none` loaded-skill is accepted only because the case explicitly allows direct
  tiny-edit handling.
- Source/runtime governance: passes with `dddjango:source-reference-audit` and
  zero source/runtime leakage markers.
- Subagent/workflow honesty: passes with workflow plus role handoffs and zero
  claim of actual subagent execution without artifacts.

## Verification Commands

```bash
python3 -B workspace/scripts/test_p6_integration_eval.py
python3 -B workspace/scripts/test_p5_individual_eval.py
python3 -B workspace/scripts/test_eval_skeleton.py
python3 -B workspace/scripts/validate_plan_governance.py
git diff --check
```

Final command results are recorded in the P6 closure.
