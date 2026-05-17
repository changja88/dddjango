# Eval Run Clean Reset And Naming Design

## Context

The eval workspace currently mixes several run directory naming styles:

- date-only names such as `20260513-runtime-full-gate`
- date-time names such as `20260511-0413-initial-full`
- bucket names placed before or after try markers
- try markers written as `try6`, `try-6`, or suffixes such as `final-full-try6`
- generated `latest/report.html` aliases that can point to old runs if the latest run has no report yet

The `lv_up_plan` files are more regular, but they still do not share a strict timestamp and try identity with the eval run directories. This makes it hard to answer a basic question: which evaluated report is the latest result for a bucket, and which improvement try produced it?

The approved direction is a clean reset across all eval buckets. Legacy run artifacts and legacy `lv_up_plan` analysis, plan, and review history will be deleted rather than archived. The current plugin and skill source already contains the useful improvements, and retaining legacy history would keep the latest-selection rules complex.

## Goals

- Reset all six buckets to one naming and traceability scheme.
- Make future run IDs lexically sortable by creation time.
- Make the latest report selection deterministic from metadata, not directory mtime or accidental report existence.
- Show try number, scope, topic, and created time in generated reports.
- Link each run to the `lv_up_plan` analysis and plan documents that governed it.
- Keep the eval pack and plugin source files intact.

## Non-Goals

- Do not preserve legacy run artifacts.
- Do not migrate old run IDs to new names.
- Do not keep legacy directories as latest-selection fallback candidates.
- Do not delete eval definitions, answer oracles, public cases, scripts, plugin source, or reference documents.
- Do not make the renderer infer improvement history from old Markdown documents.

## Buckets

The reset applies to every bucket:

- `response`
- `code`
- `plugin`
- `runtime`
- `source`
- `workflow`

## Reset Scope

Delete these generated or iterative artifacts for each bucket:

```text
workspace/develop/eval/<bucket>/runs/*
workspace/develop/eval/<bucket>/latest/*
workspace/develop/lv_up_plan/<bucket>/analysis/*
workspace/develop/lv_up_plan/<bucket>/plan/*
workspace/develop/lv_up_plan/<bucket>/review/*
```

Keep these source and eval definition files:

```text
workspace/develop/eval/<bucket>/eval_goal.md
workspace/develop/eval/<bucket>/cases/
workspace/develop/eval/<bucket>/answer/
workspace/develop/eval/<bucket>/templates/
workspace/develop/eval/<bucket>/manual_protocol.md
workspace/develop/lv_up_plan/bucket_goal_loop_prompt.md
workspace/scripts/
dddjango/
.agents/
workspace/docs/
```

The cleanup must be implemented through a dedicated script with an explicit confirmation flag. It must print the exact paths it will delete before deletion. The implementation should not rely on shell glob deletion in normal use.

## Run ID Format

Future run directories must use this format:

```text
YYYYMMDD-HHMMSS-<bucket>-tryNN-<scope>-<topic>
```

Examples:

```text
20260517-143012-runtime-try01-full-current-baseline
20260517-143455-plugin-try01-targeted-trigger-routing
20260517-144010-code-try01-adjacent-coupon-tdd
```

Rules:

- Timestamp is Asia/Seoul local time.
- Timestamp has seconds, not just minutes.
- `bucket` must be one of the known bucket names.
- `tryNN` is zero-padded to two digits.
- `scope` must be one of `full`, `targeted`, `adjacent`, `rerun`, or `manual`.
- `topic` is a lowercase slug using ASCII letters, digits, and hyphens.
- The runner rejects unsafe IDs and rejects new IDs that do not match the format.
- Existing tests may still use short synthetic IDs only when the module under test is not validating production run IDs. Production entrypoints must enforce the new format.

## lv_up_plan File Format

The `lv_up_plan` path already carries the bucket, so filenames do not repeat it.

```text
workspace/develop/lv_up_plan/<bucket>/analysis/YYYYMMDD-HHMMSS-tryNN-<topic>.md
workspace/develop/lv_up_plan/<bucket>/plan/YYYYMMDD-HHMMSS-tryNN-<topic>.md
workspace/develop/lv_up_plan/<bucket>/review/YYYYMMDD-HHMMSS-tryNN-<kind>.md
```

Examples:

```text
workspace/develop/lv_up_plan/runtime/analysis/20260517-143000-try01-current-baseline.md
workspace/develop/lv_up_plan/runtime/plan/20260517-143000-try01-current-baseline.md
workspace/develop/lv_up_plan/runtime/review/20260517-144210-try01-targeted-eval-result.md
```

Rules:

- The analysis and plan for one try share the same timestamp, try number, and topic.
- Review files may use later timestamps, but must keep the same try number.
- A new try starts at `try01` after the reset.
- A try fixes one failure family only.
- Analysis and plan documents must be written before the corresponding source or skill changes.

## Run Metadata

Each run directory must contain `RUN_META.json` in addition to `RUN_ID.txt`.

Required schema:

```json
{
  "schema_version": 1,
  "run_id": "20260517-143012-runtime-try01-full-current-baseline",
  "bucket": "runtime",
  "try_number": 1,
  "scope": "full",
  "topic": "current-baseline",
  "created_at": "2026-05-17T14:30:12+09:00",
  "lv_up_analysis": "workspace/develop/lv_up_plan/runtime/analysis/20260517-143000-try01-current-baseline.md",
  "lv_up_plan": "workspace/develop/lv_up_plan/runtime/plan/20260517-143000-try01-current-baseline.md"
}
```

Rules:

- `run_id` must match the directory name.
- `bucket`, `try_number`, `scope`, and `topic` must match the run ID.
- `created_at` is the source of truth for latest selection.
- `lv_up_analysis` and `lv_up_plan` may be empty only for an initial full baseline run explicitly marked as such by `scope: "full"` and `topic: "current-baseline"`.
- Metadata without matching raw artifacts is not enough to count as a scored run.

## Latest Report Selection

The renderer selects the latest report per bucket using this order:

1. Candidate run has valid `RUN_META.json`.
2. Candidate run has at least one answer-oracle evaluation JSON.
3. Candidate run has no known invalid execution status for the artifacts it claims to include.
4. Sort candidates by `RUN_META.json.created_at`.
5. If timestamps tie, sort by `run_id`.

Runs without valid metadata are excluded from latest selection after the reset. This is intentional. It prevents legacy naming drift and missing-report artifacts from influencing the latest report.

`workspace/develop/eval/<bucket>/latest/report.html` remains a redirect alias, but it is regenerated only from the metadata-selected latest scored run.

## Report Display

Generated reports should display:

- bucket
- run ID
- try number
- scope
- topic
- created time
- report generation time
- reportability
- linked analysis document when present
- linked plan document when present

The bucket tabs should continue to use `latest/report.html` aliases rather than embedding concrete run IDs. This keeps old generated HTML from freezing navigation to an obsolete run.

## Script Behavior

`run_eval_bucket.py` should:

- generate a compliant run ID when `--run-id` is omitted
- validate supplied run IDs against the new production format
- accept explicit `--try-number`, `--scope`, and `--topic` options, or derive them from a valid `--run-id`
- write `RUN_META.json`

`run_initial_eval.py` should:

- generate compliant full baseline run IDs per bucket
- pass metadata options through to the bucket runner

`render_eval_review_html.py` should:

- read `RUN_META.json`
- expose metadata in `REPORT_DATA`
- select latest scored reports from valid metadata only
- regenerate latest aliases after rendering

Validation scripts should:

- fail production runs with missing or inconsistent metadata
- retain path traversal protection
- report metadata mismatch errors with the bucket and run ID

## Testing

Add focused tests for:

- valid run ID generation with second-level timestamps
- invalid run ID rejection
- metadata writing and schema consistency
- latest report selection by `created_at`
- metadata-less run exclusion after reset
- `latest/report.html` alias generation
- report display of try, scope, topic, and created time
- cleanup script dry-run output and confirmed deletion scope
- preservation of eval definitions and source files during cleanup

## Rollout

1. Add naming and metadata helpers.
2. Add tests for the new helpers and renderer selection.
3. Update runners, validator, and renderer.
4. Add the clean reset script.
5. Run the reset across all buckets only after tests pass.
6. Start new `try01` analysis and plan files per bucket as needed.
7. Generate new full or targeted runs under the new naming scheme.

## Risks

- Deleting existing artifacts removes historical evidence. This is accepted because the project now prioritizes a simple, deterministic future eval workflow.
- A full reset means current reports disappear until new runs are generated.
- If model-backed evals are blocked by usage limits, some buckets may temporarily have no latest report.
- Strict metadata enforcement may require updating tests that rely on short synthetic run IDs at production entrypoints.

## Decision

Use a clean reset across all buckets. Do not archive legacy run artifacts or legacy `lv_up_plan` history. Enforce the new naming format and metadata for all future production eval runs.
