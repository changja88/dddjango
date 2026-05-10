# Eval Runs

Run directories are generated local artifacts and are not part of the durable plugin source. Keep only this README in git.

Create one local directory per plugin response eval run:

```text
workspace/develop/eval/response/runs/<YYYYMMDD-HHMM>-<short-label>/
  analysis/
    <case-id>.html
  raw/
    <case-id>-public-prompt.md
    <case-id>-baseline.txt
    <case-id>-with-dddjango.txt
    <case-id>-prompt-input.json
  report.html
```

Use `workspace/develop/eval/response/templates/run-report.html` for `report.html`.
Use `workspace/develop/eval/response/templates/case-analysis.html` as the shape for case-level comparison analysis pages.

Do not store private evaluator keys inside `raw/` or any directory supplied to forward-test agents.
After a run is complete, consolidate durable response-eval decisions into `workspace/develop/eval/response/README.md`, `workspace/develop/eval/response/rubrics`, scripts, or commit history. Delete or leave the generated run directory ignored.
