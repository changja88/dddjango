# Eval Runs

Create one directory per comprehensive plugin eval run:

```text
workspace/develop/evals/runs/<YYYYMMDD-HHMM>-<short-label>/
  analysis/
    <case-id>.html
  raw/
    <case-id>-public-prompt.md
    <case-id>-baseline.txt
    <case-id>-with-dddjango.txt
    <case-id>-prompt-input.json
  findings.md
  reruns.md
  report.html
```

Use `workspace/develop/evals/templates/run-report.html` for `report.html`.
Use `workspace/develop/evals/templates/case-analysis.html` as the shape for case-level comparison analysis pages.

Do not store private evaluator keys inside `raw/` or any directory supplied to forward-test agents.
