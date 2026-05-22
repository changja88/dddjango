# Eval Protocol

This protocol defines the P4 evaluator contract before real skill-specific cases
are expanded. Runtime routing evidence remains deferred under
`workspace/plan/decisions/ADR-0004-p3-runtime-forward-test-deferral.md`; P4
results prove evaluator mechanics only, not installed runtime routing quality.

## Case Schema

Case files live under `workspace/develop/eval/fixtures/<bucket>/cases.json`.
Each case uses `eval-case/v1` semantics even when stored in the bucket list.

Required fields:

- `id`: stable kebab-case case id.
- `bucket`: bucket name, for example `mini-bucket`.
- `prompt`: user-facing prompt text. It may contain natural language claims, but
  prompt text is never command/tool execution evidence.
- `expected_outcomes`: list of `{id, value}` assertions. Duplicate `id` entries
  with different `value` are an `expected-outcomes-conflict` failure before
  scoring.
- `fixture_expected`: P4 fixture-only expected status by variant. Allowed values
  are `pass`, `partial`, `fail`, and `not-scored`.

Optional fields:

- `injected_failures`: deterministic fixture failures such as `stale-report`.

Every scored case must have both variants: `baseline` and `with-plugin`.

## Answer Schema

Answers live under
`workspace/develop/eval/fixtures/<bucket>/answers/<case-id>.<variant>.json`.

Required fields:

- `schema_version`: `eval-answer/v1`.
- `case_id`, `variant`: must match the file name and case.
- `loaded_skill`: structured loaded-skill observation when available. Free-text
  mentions of skill names are not routing evidence.
- `claims`: structured answer claims used by the scorer.
- `answer_text`: persisted/redacted answer text.
- `pre_redaction_text`: ephemeral raw text scanned before sanitizer output is
  trusted.
- `structured_events`: command/tool events. Command claims are valid only when a
  structured event contains the expected command or tool.

## Oracle Output Schema

Oracles live under
`workspace/develop/eval/fixtures/<bucket>/oracles/<case-id>.<variant>.json`.

Required fields:

- `schema_version`: `eval-oracle/v1`.
- `case_id`, `variant`: must match the file name and case.
- `loaded_skill`: expected structured loaded skill when routing is in scope.
- `required_claims`: list of structured claims required for scoring.

Optional fields:

- `required_command`: command/tool string that must appear in
  `structured_events`. Prompt text, answer prose, stdout prose, or report text
  cannot satisfy this requirement.

Missing, empty, or malformed oracle JSON is `not-scored` and keeps the run
failed. `not-scored` is never a success status.

## Scoring Semantics

The scorer reads the raw case, answer, and oracle artifacts. It does not infer
pass/fail from HTML, chat summaries, prompt wording, or negated prose.

- `pass`: all required claims match, structured routing checks match, structured
  command requirements match, and no failure semantics are present.
- `partial`: at least one but not all required claims match, or an otherwise
  scored fixture has injected failure semantics. Partial is scored, but it is
  not a success.
- `fail`: the oracle is valid, scoring ran, and required claims/checks fail or
  leakage/report failure semantics are present.
- `not-scored`: scoring could not run because required evaluator inputs are
  missing, malformed, or contradictory.

Run status is `fail` when any result is `partial`, `fail`, or `not-scored`.

## Failure Semantics

The evaluator must distinguish these failure classes:

- `missing-oracle`: no oracle file for a required `case x variant`.
- `malformed-oracle`: oracle JSON cannot be parsed or lacks required schema.
- `expected-outcomes-conflict`: case expectations contradict each other before
  scoring.
- `oracle-partial`: scored answer matched only part of the required oracle.
- `oracle-mismatch`: scored answer matched none of the required oracle claims.
- `wrong-routing`: structured loaded-skill field differs from oracle.
- `missing-structured-command-evidence`: required command/tool evidence is
  claimed only in prompt/prose, not in a structured command/tool event.
- `raw-leakage`: pre-redaction raw input contains a forbidden local path or
  private-field marker. Sanitizer success does not convert this to pass.
- `persisted-leakage`: persisted/redacted answer/report input still contains a
  forbidden marker.
- `stale-report`: report source digest or case rows do not match current raw
  artifacts.

Leakage findings stored in run artifacts must be sanitized summaries: count,
class, marker hash, and artifact kind. Do not store real local paths or private
evaluation literals in user-facing reports.

## Artifact Names

For a run id `<run-id>`, artifacts are written below
`workspace/develop/eval/runs/<run-id>/`:

- `raw/run.json`: primary raw run artifact and scorer output.
- `report/report.json`: machine-readable report generated from current raw.
- `report/report.html`: human-readable report generated from current raw.
- `validation/validate-run.json`: validator result comparing raw and report.

P4 plan/evidence artifacts live under
`workspace/plan/phases/p4-eval-skeleton/{analysis,plan,fixtures,evidence,closure}/`.

## Report Invariants

The report is never primary truth. It is valid only when all invariants hold:

- `report.json.source_raw_digest` equals the digest of current `raw/run.json`
  excluding the stored digest field.
- report status counts equal raw status counts.
- every report row has the same `(case_id, variant, status,
  expected_fixture_status, failure_semantics)` tuple as raw.
- report output records runtime-routing evidence as deferred when P3b is still
  unresolved.
- report display never downgrades `partial`, `fail`, or `not-scored` to success.

## Command Contract

All commands are fixture-only in P4 and require no model-backed runtime.

```bash
python3 -B workspace/scripts/eval_skeleton.py run-one \
  --fixture-root workspace/develop/eval/fixtures/mini-bucket \
  --output-dir workspace/develop/eval/runs/p4-mini-bucket-fixture \
  --case-id p4-pass \
  --variant baseline
```

Runs one `case x variant`, writes `raw/one.json`, and exits nonzero unless the
result status is `pass`.

```bash
python3 -B workspace/scripts/eval_skeleton.py run-bucket \
  --fixture-root workspace/develop/eval/fixtures/mini-bucket \
  --output-dir workspace/develop/eval/runs/p4-mini-bucket-fixture \
  --bucket mini-bucket \
  --run-id p4-mini-bucket-fixture
```

Runs all `baseline` and `with-plugin` variants in the bucket, writes
`raw/run.json`, and exits nonzero when any result is `partial`, `fail`, or
`not-scored`. For P4 mini-bucket this nonzero exit is expected because injected
failure fixtures prove the failure semantics.

```bash
python3 -B workspace/scripts/eval_skeleton.py render-report \
  --output-dir workspace/develop/eval/runs/p4-mini-bucket-fixture
```

Regenerates `report/report.json` and `report/report.html` from current raw.

```bash
python3 -B workspace/scripts/eval_skeleton.py validate-run \
  --output-dir workspace/develop/eval/runs/p4-mini-bucket-fixture
```

Compares current raw and report artifacts. It exits nonzero when report/raw are
stale or mismatched, when fixture status mismatches exist, or when `not-scored`
is present. P4 evidence must record the nonzero result for the injected
mini-bucket and confirm that the failure classes match the fixture matrix.

## Affected Bucket Table

| change | affected bucket |
|---|---|
| case prompt, answer, or oracle changes | the case's bucket |
| bucket-local validator/report configuration | that bucket |
| shared runner, scorer, oracle schema, validator, report renderer, sanitizer, or digest logic | all buckets |
| skill/reference/runtime cache change | every bucket that references the affected skill/reference/runtime surface |
| plugin manifest/install/cache metadata change | plugin, runtime, source, workflow buckets and smoke checks |
| eval protocol change | all eval buckets until mini-bucket fixture evidence is regenerated |
