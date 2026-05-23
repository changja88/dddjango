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

- `runner=7b5a4104e6ceec65df86b9f8f2b9ef0f9e09a4e50bd00f5f81f0ea1671ddf403`
- `tests=5bee5fa5d1404d317ab7006fa2000aa28804578c678369fbdbdb21de555a38b4`
- `cases=3957fee5a65bc032cb9dbce1bb6557ca913ec00e5ea7f0a512f97deb45c6f2c7`
- `raw=ef2248f59ead010046c0224f8555cc944012b393b86bc826e6f2bdf74ee8a66e`
- `targeted_suite=7cb3e992c3986c288e67991eb61257bdcd0bfc16a5e5c00253be5b23dccc1a2d`
- `report_json=8440b6d06d2397e8835419576f684794ff0c1b10f9c57dba8ec92b0b92eaf472`
- `validation=1228fb562e214b726450cf980f6277354302716c825ef0a5cb6f17cef0e4f277`
- `metadata=c46855b7e0b0bd1cb1d2a98b288ad622194eeeb5639fb2e0f2898792f3238ac7`

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

Approval was later received, and P6 completion is recorded in
`workspace/plan/phases/p6-integration-eval/evidence/20260524-013349-p6-eval-model-backed-integration-runtime-evidence.md`.
