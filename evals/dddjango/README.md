# dddjango Purpose-Fit Evaluation

This directory contains the purpose-fit evaluation framework for `dddjango`.
Its final goal is to measure whether the plugin enforces its intended Django
standards: Django Ninja over DRF, DDD boundaries, DB/transaction discipline,
TDD quality, Korean-first usability, and subagent workflow behavior.

Current status: fixture smoke tests plus a live Codex comparison runner.
Fixture scores validate the evaluation pipeline, not the real plugin
performance. Use live scores for plugin value claims.

## Commands

```bash
python3 evals/dddjango/scripts/validate_eval_config.py
python3 evals/dddjango/scripts/run_calibration.py --write-report
python3 evals/dddjango/scripts/run_evaluation.py --mode fixture
python3 evals/dddjango/scripts/score_outputs.py --latest
python3 evals/dddjango/scripts/render_report.py --latest
```

Prefer the Makefile smoke command when changing the evaluator itself:

```bash
make eval-smoke
```

Run the installed-plugin comparison with:

```bash
make eval-dddjango
```

Optional filters:

```bash
make eval-dddjango SUITE=core-policy
make eval-dddjango CASE=c01-drf-order-api
make eval-dddjango CASE=c01-drf-order-api VARIANT=with-dddjango
```

`without-dddjango` runs with `--ignore-user-config --ignore-rules`.
`with-dddjango` runs with the normal Codex config, so the installed marketplace
plugin must be enabled before measuring.

Use calibration when changing gates, cases, or scoring:

```bash
make eval-calibrate
```

Generated run artifacts are written under `workspace/codex-eval/purpose-fit/`.
Those artifacts are local and intentionally not committed.
