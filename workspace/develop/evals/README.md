# dddjango Plugin Eval Pack

This directory contains the comprehensive plugin eval prompt pack for `dddjango`.

Use this pack after the individual skill rubrics and the workflow rubric have already passed. The source of truth for scoring is `workspace/develop/rubrics/plugin_rubric.md`; this directory only turns that rubric into executable prompt packets, private evaluator guidance, and an HTML run-report template.

## Directory Layout

```text
workspace/develop/evals/
  cases/plugin/public/
    case-001.md ... case-017.md
  cases/plugin/private/
    case-map.md
  templates/
    case-analysis.html
    public-packet.md
    private-evaluator.md
    run-report.html
  runs/
```

## Execution Rules

- Give forward-test agents or prompt runners only files from `cases/plugin/public/` plus task-local fixture files.
- Do not give forward-test agents `cases/plugin/private/`, rubric files, prior findings, expected routes, scoring notes, or intended fixes.
- Store raw outputs under `workspace/develop/evals/runs/<run-id>/raw/`.
- Store case-level human analysis pages under `workspace/develop/evals/runs/<run-id>/analysis/`.
- Store findings, reruns, and the final HTML report under the same run directory.
- Copy `templates/run-report.html` to `runs/<run-id>/report.html` and edit the embedded `REPORT_DATA` object for the run.
- The HTML report is self-contained and must work from `file://`; do not make it depend on external assets, CDN links, or local JSON fetched with browser APIs.
- Record baseline and with-dddjango results against the same public packets so the report can show score, pass-rate, routing, hard-gate, finding, and scenario-family deltas.
- Artifact links in the HTML report are relative links from the run directory. Create analysis artifacts such as `analysis/<case-id>.html` and raw artifacts such as `raw/<case-id>-public-prompt.md`, `raw/<case-id>-baseline.txt`, `raw/<case-id>-with-dddjango.txt`, prompt-input JSON, command logs, screenshots, and leakage-scan logs before marking an artifact as present.
- Case-level analysis HTML should explain the prompt, baseline setup, with-dddjango setup, what each variant did well or poorly, hard-gate/routing differences, score rationale, final score, and links back to raw evidence.
- If runtime cache is used, record the cache path and compare it with canonical source `dddjango/`.
- If a command, smoke check, review, or subagent pass was not run, mark it as not run with a reason.

## Required Run Artifacts

Each complete run records:

- git commit or working-tree state
- plugin version from `dddjango/.codex-plugin/plugin.json`
- validation command output
- `git diff --check` output
- runtime leakage scan command, scope, patterns, output, and semantic review note
- runtime cache path and source/cache comparison when cache is used
- prompt-input or equivalent metadata exposure artifact
- public packet paths actually supplied
- case-level analysis HTML for baseline vs with-dddjango comparisons
- raw outputs and transcripts
- findings with severity, scenario family, case id, defect type, failed gate or dimension, artifact path, and rerun scope
- rerun evidence after fixes
- final not-run list

## Completion Rule

The comprehensive plugin eval is complete only when:

- every public case in this pack has been run or is explicitly marked not-run as a blocker
- plugin-level and applicable common hard gate failures are 0
- blocking, major, and minor findings are all 0
- every required scenario family in `plugin_rubric.md` has passing evidence
- generated/all validation passes against `dddjango/skills`
- runtime leakage scan finds no private evaluation material under runtime paths
- runtime cache is not used, or it matches canonical `dddjango/` source for the evaluated version

Do not mark the plugin eval complete from smoke checks alone.
