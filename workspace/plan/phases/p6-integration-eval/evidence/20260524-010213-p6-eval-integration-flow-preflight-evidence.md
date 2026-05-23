# P6 Integration Flow Preflight Evidence

## Status

Result: `pass-preflight-incomplete`

This evidence is fixture-scored and `model_backed=false`. It proves the P6
integration bucket shape and scorer/report/validator mechanics only. It is not
P6 completion evidence.

## Commands

```bash
python3 -B workspace/scripts/test_p6_integration_eval.py
```

Result: 5 tests, OK.

```bash
python3 -B workspace/scripts/test_p5_individual_eval.py
```

Result: 13 tests, OK.

```bash
python3 -B workspace/scripts/test_eval_skeleton.py
```

Result: 8 tests, OK.

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-fixture run-targeted-suite --bucket integration-flows --run-id p6-integration-flows-fixture --iterations 2
```

Result: `{"status": "pass", "iterations": 2}`.

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-fixture run-bucket --bucket integration-flows --run-id p6-integration-flows-fixture
```

Result: `{"status": "pass", "status_counts": {"pass": 8, "partial": 0, "fail": 0, "not-scored": 0}}`.

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-fixture render-report
```

Result: report regenerated from current raw artifact.

```bash
python3 -B workspace/scripts/p6_integration_eval.py --fixture-root workspace/develop/eval/fixtures/integration-flows --output-dir workspace/develop/eval/runs/p6-integration-flows-fixture validate-run
```

Result: `{"status": "pass", "failures": []}`.

## Raw Artifacts

- `workspace/develop/eval/runs/p6-integration-flows-fixture/raw/run.json`
- `workspace/develop/eval/runs/p6-integration-flows-fixture/raw/targeted-suite.json`
- `workspace/develop/eval/runs/p6-integration-flows-fixture/report/report.json`
- `workspace/develop/eval/runs/p6-integration-flows-fixture/report/report.html`
- `workspace/develop/eval/runs/p6-integration-flows-fixture/validation/validate-run.json`

## Digest

- `runner=33f9d2dd125d534cbfe009e604e48f37d5360a8be509c4ffaa3d95b3a37bbb98`
- `tests=46e0ab61bff81c362ec0ff7a6bc6d6605ec28f3beea6d94c306c917142d68b04`
- `cases=3957fee5a65bc032cb9dbce1bb6557ca913ec00e5ea7f0a512f97deb45c6f2c7`
- `raw=95ce9db7ace3c94439c6c6a7b2dc4b14e32f4264005bdc6cab98750018a06c9e`
- `targeted_suite=015637cadffc4ed8221066a41fe99111a8e897891b0bf8e2dae3d778ced2d28e`
- `report_json=1ef450e71d470746e69909c17e946abb66b57d2e7a6fcc4b7c0f3d7103f16227`
- `validation=37fc4249c11a181a4ae3b3844ca337f69cb0b7eeaa8eeacfb53ed931d52470b4`
- `metadata=b11d43617d71a38a3ffd6d0429d7b490580c3ffbd05244644a1b52fa2c03368f`

Current-file match: `current` for the preflight artifacts above.

## Clean/Scored Summary

- `case_count=4`
- `result_count=8`
- `status_counts={"pass": 8, "partial": 0, "fail": 0, "not-scored": 0}`
- missing/malformed oracle or answer failure semantics: 0
- responsibility intrusion, false claim, source leakage failure semantics: 0

## External Runtime Approval Blocker

The P6 model-backed installed-runtime command was not executed. The attempted
external run was rejected by the reviewer because this P6 turn did not include a
P6-specific explicit approval after the data export risk was disclosed.

Required approval wording:

```text
P6 model-backed installed-runtime eval을 승인한다. 외부 Codex runtime으로 P6 공개 프롬프트, 설치된 dddjango runtime skill 지침/context, 구조화 출력 schema가 전송될 수 있음을 이해했고, 아래 targeted 2회 run과 affected bucket all-cases run 실행을 허용한다.
```

Until that approval is received and model-backed runs pass, P6 remains
incomplete.
