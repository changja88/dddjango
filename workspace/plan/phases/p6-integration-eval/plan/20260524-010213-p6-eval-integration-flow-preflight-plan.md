수정 대상: workspace/develop/eval/fixtures/integration-flows/, workspace/scripts/p6_integration_eval.py, workspace/scripts/test_p6_integration_eval.py

# P6 Integration Flow Preflight Plan

## Matrix

1. Add a dedicated `integration-flows` eval fixture bucket with four cases:
   composite DDD/DB/API/Django/Test, tiny edit restraint, source/runtime
   governance, and subagent/workflow honesty.
2. Add a P6 runner that reuses the P5 clean/scored mechanics but keeps P6 prompt
   assembly, metadata, schema, and guardrail checks separate from P5 completion
   artifacts.
3. Add unit tests for:
   - clean fixture bucket scoring
   - source/runtime leakage failure
   - tiny edit workflow-overreach failure
   - model-backed targeted-suite proof
   - model-backed affected bucket validation with targeted proof
4. Run fixture preflight targeted 2x, fixture bucket all-cases, report
   regeneration, validate-run, and related eval unit tests.
5. After P6-specific external runtime approval, run:

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-model-approved-targeted-with-plugin-v1 model-run-targeted-suite --bucket integration-flows --run-id p6-integration-flows-model-approved-targeted-with-plugin-v1 --iterations 2 --runtime-channel external --work-root /private/tmp/dddjango-p6-model --variants with-plugin
```

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-model-approved-bucket-with-plugin-v1 model-run-bucket --bucket integration-flows --run-id p6-integration-flows-model-approved-bucket-with-plugin-v1 --runtime-channel external --work-root /private/tmp/dddjango-p6-model --variants with-plugin
```

6. Regenerate report, copy stable targeted-suite proof into the affected bucket
   artifact if needed for single-pass bucket validation, run validate-run, and
   compare raw/report/validation digests.
7. Update evidence, closure, indexes, and phase status only after model-backed
   completion gates pass.

## Completion Gate

P6 is incomplete until model-backed installed-runtime evidence shows:

- targeted 2x pass for all new integration cases
- affected bucket all-cases pass
- `not-scored=0`
- missing/malformed oracle or answer count is 0
- responsibility intrusion, false claim, and source leakage count is 0
- current-file fingerprint matches run evidence
