# dddjango Purpose-Fit Evaluation

This directory contains the purpose-fit evaluation framework for `dddjango`.
Its final goal is to measure whether the plugin enforces its intended Django
standards: Django Ninja over DRF, DDD boundaries, DB/transaction discipline,
TDD quality, concrete code/file structure, Korean-first usability, subagent
workflow behavior, and holdout/adversarial robustness against keyword
overfitting.

Subagent workflow scoring is intentionally stricter than section-name checks.
It evaluates role decomposition, dddjango skill mapping, handoff fields,
execution planning, integration conflict handling, and false subagent claim
prevention.

Current status: fixture smoke tests plus a live Codex comparison runner.
Fixture scores validate the evaluation pipeline, not the real plugin
performance. Fixture reports show `Skill value delta: not applicable` on
purpose; use only full live scores for plugin value claims.

Release gates do not pass on low-confidence automatic signals alone. A full
live run can produce `needs_review` when artifacts still require manual/judge
review before treating the result as a publish-quality verdict.

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
