# Code Eval Runs

Code eval run directories are generated local artifacts.

Expected generated layout:

```text
workspace/develop/eval/code/runs/<YYYYMMDD-HHMM>-<short-label>/
  raw/
  code/
  reports/
```

Only this README is tracked. Generated run directories should stay ignored unless a specific artifact is promoted into a durable fixture, rubric, or documented decision.
