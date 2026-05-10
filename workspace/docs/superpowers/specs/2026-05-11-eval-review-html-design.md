# Eval Review HTML Design

## Purpose

Build a static evaluator-only HTML report for reviewing dddjango eval runs before improving the plugin. The first version must make it easy for a human reviewer to see the run summary, compare baseline versus with-dddjango answers, and inspect the evaluator judgment for each case.

## Selected Layout

Use the **Master List + Detail Below** layout.

The page has three vertical sections:

1. Run summary at the top.
2. Evaluation question list below the summary.
3. Selected case detail below the list.

This matches the review flow: first decide whether the run is worth reading, then scan the cases, then open one case and compare both variants.

## Run Summary

The top summary must show:

- run id
- generated timestamp
- reportability status
- total case count
- pass, partial, and fail counts
- baseline average score
- with-dddjango average score
- score delta
- hard gate failure count
- missing or weak evidence count

The summary should prioritize decision-making over decoration. If the run has leakage, missing oracle evaluation, missing raw artifacts, or schema errors, the summary must make that visible before the reviewer reads individual scores.

## Evaluation Question List

The list must show one row per case:

- evaluation question
- bucket
- baseline score
- with-dddjango score
- delta
- hard gate or review status
- detail action

Default ordering:

1. hard gate failures
2. failed cases
3. partial cases
4. largest positive or negative delta
5. passing cases

The list is the main navigation surface. It should let the reviewer quickly find cases that need attention without opening every case.

## Case Detail

Clicking a detail action opens the selected case detail below the list.

The detail panel starts with the public problem statement. Below that, the panel is split into two equal columns:

- left: baseline
- right: with-dddjango

Each side must use the same structure:

- score and verdict
- response
- evaluation

Below the two-column comparison, include evaluator-only details in a secondary area:

- evidence links or artifact names
- failed checks
- leakage notes
- reviewer note

The public problem statement and evaluator-only judgment material must be visually separated. The report itself is evaluator-only, but the UI should still make the boundary obvious so future exported or copied material does not mix public case text with hidden oracle details.

## Data Inputs

The renderer reads from the existing eval pack structure:

- `workspace/develop/eval/<bucket>/cases/plugin/public/*.md`
- `workspace/develop/eval/<bucket>/answer/*.yaml`
- `workspace/develop/eval/<bucket>/runs/<run-id>/raw/*`
- `workspace/develop/eval/<bucket>/runs/<run-id>/analysis/*`

The first implementation should support one bucket and one run at a time. Cross-bucket aggregation can be added later without changing the case detail structure.

## Output

Write the report to:

```text
workspace/develop/eval/<bucket>/runs/<run-id>/analysis/report.html
```

The output is a static HTML file. It should be viewable directly in a browser without a dev server. Small embedded JavaScript is acceptable for expanding case details and switching selected rows.

## Validation Integrity

The renderer must not infer a passing score from missing data. Missing artifacts should produce explicit blocked or unscored states.

The report must distinguish:

- public case text
- model responses
- answer oracle evaluation
- validation or command artifacts
- human reviewer notes

Hard gate failures such as answer leakage, public case leakage, missing required oracle fields, and missing raw artifacts must be visible in both the summary and the affected case row.

## First Version Scope

Include:

- one-bucket report rendering
- run summary
- case list
- selected case detail
- baseline and with-dddjango side-by-side comparison
- blocked, pass, partial, fail, and unscored states
- artifact/evidence names when available
- static HTML with inline CSS and minimal JavaScript

Exclude:

- persisted manual edits from the browser
- cross-run comparison
- charts
- server-side viewer
- interactive filtering beyond basic row selection
- automatic eval execution

## Testing

Add focused tests for the report data shaping logic where practical. At minimum, verify:

- missing artifacts render as blocked or unscored, not pass
- case rows include the expected question and both scores
- selected case detail includes problem, baseline response/evaluation, and with-dddjango response/evaluation
- evaluator-only fields are not written into public case files

Run existing eval validators after implementation:

```text
python3 workspace/scripts/validate_eval_bucket_pack.py
git diff --check
```

If a renderer-specific readability validator exists or is extended, run it too.
