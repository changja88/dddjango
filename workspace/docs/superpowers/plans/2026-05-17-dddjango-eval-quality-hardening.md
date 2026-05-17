# dddjango Eval Quality Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the dddjango eval system decision-grade enough to support regression tracking, product-value review, and plugin hardening without misleading report output or weak evidence.

**Architecture:** Harden the eval harness before tuning skills. Keep the public/private eval split intact, make report output conform to its validator, strengthen oracle schemas, add deterministic evidence for code-backed cases, then close the current source/workflow/routing residual findings with targeted eval runs.

**Tech Stack:** Python 3 stdlib, `unittest`, existing eval scripts in `workspace/scripts`, static HTML report rendering, existing `make eval-all` and `make eval-one` targets, dddjango skill markdown/reference files.

---

## File Structure

- Modify `workspace/scripts/render_eval_review_html.py`: emit `REPORT_DATA` in the `eval-report-v2` contract while preserving the current HTML category navigation and latest aliases.
- Modify `workspace/scripts/test_render_eval_review_html.py`: add v2 contract, template token, and embedded artifact regression tests.
- Modify `workspace/scripts/eval_run_common.py`: enforce strict answer-oracle score and verdict normalization.
- Modify `workspace/scripts/test_eval_run_common.py`: cover valid and invalid oracle score/verdict shapes.
- Modify `workspace/scripts/evaluate_eval_run.py`: keep evaluator output aligned with the stricter oracle contract.
- Modify `workspace/scripts/validate_eval_run.py`: scan both variants, oracle outputs, prompt inputs, and reports for forbidden absolute local paths.
- Modify `workspace/scripts/test_validate_eval_run.py`: cover both-variant path leakage and report path leakage.
- Modify `workspace/scripts/validate_eval_code_artifacts.py`: validate deterministic code checks from answer oracle metadata.
- Modify `workspace/scripts/test_validate_eval_code_artifacts.py` if it exists; otherwise create it next to the validator.
- Modify `workspace/develop/eval/code/answer/*.yaml`: add deterministic check declarations for code-backed cases.
- Modify `workspace/develop/eval/code/cases/plugin/code-capture.json`: add deterministic check metadata only if answer YAML alone is not enough.
- Create or modify `workspace/develop/eval/code/fixtures/django_shop_service/`: real Django/Django Ninja fixture for later decision-grade code coverage.
- Modify `dddjango/skills/source-reference-audit/SKILL.md`: require `expected evidence` in validation coverage matrices.
- Modify `dddjango/skills/source-reference-audit/agents/openai.yaml`: narrow validation/eval-traceability prompt wording to explicit-request scope.
- Modify `dddjango/skills/architecture-implementation-patterns/agents/openai.yaml`: change ambiguous “clean” wording to “clean-architecture”.
- Modify `dddjango/skills/implementation-python/agents/openai.yaml`: specify `pydantic v2 boundaries`.
- Modify `dddjango/skills/workflow-dddjango-subagents/SKILL.md` and `references/handoff-contract.md`: tighten disjoint parallel ownership.
- Modify relevant runtime routing skills only after targeted evidence shows the wrong-routing regression is real.

## Execution Rules

- Do not edit generated `workspace/develop/eval/*/runs/**` artifacts except by rerunning render/eval commands.
- Do not copy `answer/*.yaml` oracle wording into runtime skills, public cases, plugin metadata, or docs.
- Keep each task independently testable and commit after each green task.
- Run deterministic unit tests before model-backed evals.
- Use new canonical run IDs through `make eval-one` or `make eval-all`; do not hard-code run IDs in tests.

## Task 1: Align HTML Reports With `eval-report-v2`

**Files:**
- Modify: `workspace/scripts/render_eval_review_html.py`
- Modify: `workspace/scripts/test_render_eval_review_html.py`
- Verify: `workspace/scripts/validate_eval_report_readability.py`

- [ ] **Step 1: Add a failing renderer test for v2 schema**

Add a test that renders a minimal ready oracle and extracts the JSON assigned to `const REPORT_DATA`. Assert:

```python
self.assertEqual(data["schema_version"], "eval-report-v2")
self.assertIn("summary", data)
self.assertIsInstance(data["summary"]["sections"], list)
self.assertTrue(data["summary"]["sections"])
self.assertIn("evaluation_items", data)
self.assertTrue(data["evaluation_items"])
```

Expected before implementation: the test fails because current `REPORT_DATA` uses the legacy summary/cases shape.

- [ ] **Step 2: Add a failing template-token test**

Assert the rendered HTML contains:

```python
for token in (
    'id="report-summary"',
    'id="evaluation-filters"',
    'id="evaluation-items-table"',
    'id="comparison-modal"',
    "renderReportSummary",
    "renderEvaluationItems",
    "openComparisonModal",
    "closeComparisonModal",
):
    self.assertIn(token, html)
```

Expected before implementation: at least `report-summary` and `evaluation-items-table` are missing.

- [ ] **Step 3: Implement a legacy-to-v2 report data adapter**

In `render_eval_review_html.py`, add a function with this contract and keep helper functions local to the renderer:

```python
def report_v2_data(report: dict[str, object]) -> dict[str, object]:
    cases = report.get("cases", [])
    summary = report.get("summary", {})
    return {
        "schema_version": "eval-report-v2",
        "summary": report_v2_summary(summary, cases),
        "evaluation_items": [report_v2_item(case) for case in cases],
        "embeddedArtifacts": report.get("embeddedArtifacts", {}),
    }
```

It must produce:

```python
{
    "schema_version": "eval-report-v2",
    "summary": {
        "conclusion": "with-dddjango: 9 pass, 0 partial, 0 fail; average 4.8 / 5.",
        "risks": ["No previous comparable run for trend metrics."],
        "sections": [
            {"type": "numeric", "metrics": [{"label": "with-dddjango average", "value": "4.8"}]},
            {"type": "hard_gate", "metrics": [{"label": "hard gate failures", "value": "0"}]},
            {"type": "narrative", "metrics": [{"label": "reportability", "value": "reportable"}]},
        ],
    },
    "evaluation_items": [
        {
            "id": "case-response-order-create",
            "title": "case-response-order-create",
            "source_granularity": "case",
            "test_content_ko": "public case와 answer oracle 기준 비교",
            "score_type": "numeric",
            "score_type_source": "explicit",
            "baseline": {
                "score": "3 / 5",
                "response_summary": "baseline response summary",
                "response": "baseline response",
                "evaluation_summary": "baseline evaluation summary",
                "evaluation": "baseline evaluation",
                "evidence": [],
            },
            "with_dddjango": {
                "score": "4 / 5",
                "response_summary": "with-dddjango response summary",
                "response": "with-dddjango response",
                "evaluation_summary": "with-dddjango evaluation summary",
                "evaluation": "with-dddjango evaluation",
                "evidence": [],
            },
            "change": {"direction": "improved"},
        }
    ],
    "embeddedArtifacts": {},
}
```

Map each current case row to one `evaluation_items` row. Use `source_granularity: "case"`, `score_type: "numeric"` when both variants have numeric scores, `score_type_source: "explicit"` when the score came from oracle JSON, and `change.direction` from the existing run-change direction.

- [ ] **Step 4: Preserve current category navigation**

Keep the existing bucket tabs and `latest/report.html` redirects. The new v2 template must not reintroduce disabled tabs after full eval rendering.

- [ ] **Step 5: Verify renderer unit tests**

Run:

```bash
python3 -m unittest workspace/scripts/test_render_eval_review_html.py
```

Expected: all tests pass.

- [ ] **Step 6: Verify readability validator on all latest reports after re-render**

Re-render current latest runs:

```bash
python3 workspace/scripts/render_eval_review_html.py --bucket response --run-id 20260517-145735-response-try01-full-current-baseline
python3 workspace/scripts/render_eval_review_html.py --bucket code --run-id 20260517-145735-code-try01-full-current-baseline
python3 workspace/scripts/render_eval_review_html.py --bucket plugin --run-id 20260517-145735-plugin-try01-full-current-baseline
python3 workspace/scripts/render_eval_review_html.py --bucket runtime --run-id 20260517-152141-runtime-try01-full-current-baseline
python3 workspace/scripts/render_eval_review_html.py --bucket source --run-id 20260517-152835-source-try01-full-current-baseline
python3 workspace/scripts/render_eval_review_html.py --bucket workflow --run-id 20260517-154712-workflow-try01-full-current-baseline
```

Then run:

```bash
for b in response code plugin runtime source workflow; do
  run=$(find "workspace/develop/eval/$b/runs" -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1)
  python3 workspace/scripts/validate_eval_report_readability.py --report "$run/analysis/report.html"
done
```

Expected: each report prints `readability validation passed`.

- [ ] **Step 7: Commit**

```bash
git add workspace/scripts/render_eval_review_html.py workspace/scripts/test_render_eval_review_html.py
git commit -m "Align eval report renderer with v2 contract"
```

## Task 2: Make Answer-Oracle Scoring Strict

**Files:**
- Modify: `workspace/scripts/eval_run_common.py`
- Modify: `workspace/scripts/test_eval_run_common.py`
- Modify: `workspace/scripts/evaluate_eval_run.py`
- Verify: `workspace/scripts/validate_eval_run.py`

- [ ] **Step 1: Add failing tests for invalid verdict and score**

Add tests to `test_eval_run_common.py`:

```python
def test_validate_oracle_schema_rejects_unknown_verdict(self):
    oracle = self.valid_oracle()
    oracle["with_dddjango"]["verdict"] = "great"
    self.assertEqual(
        self.common.validate_oracle_schema(oracle, "case-example"),
        "with_dddjango.verdict is unsupported: great",
    )

def test_validate_oracle_schema_rejects_out_of_range_score(self):
    oracle = self.valid_oracle()
    oracle["with_dddjango"]["score"] = "6 / 5"
    self.assertEqual(
        self.common.validate_oracle_schema(oracle, "case-example"),
        "with_dddjango.score must be between 0 and 5",
    )
```

Expected before implementation: these tests fail because unknown verdicts and score ranges are not rejected.

- [ ] **Step 2: Implement shared verdict and score parsing**

In `eval_run_common.py`, add:

```python
ALLOWED_ORACLE_VERDICTS = {"pass", "partial", "pass-limited", "pass-control", "fail", "blocked"}

def parse_score_5(value: object) -> float | None:
    text = str(value or "").strip()
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:/\s*5)?", text)
    if not match:
        return None
    score = float(match.group(1))
    if score < 0 or score > 5:
        return None
    return score
```

Accept `4`, `4.0`, `4 / 5`, and `4/5`. Reject empty values, non-numeric values, values below `0`, values above `5`, and denominators other than `5`.

- [ ] **Step 3: Wire strict schema into `validate_oracle_schema`**

For both `baseline` and `with_dddjango`, require:

```python
verdict in ALLOWED_ORACLE_VERDICTS
parse_score_5(score) is not None
```

Keep `unscored` out of answer-oracle output. `unscored` may remain a renderer fallback for missing artifacts only.

- [ ] **Step 4: Update evaluator prompt guardrails**

In `evaluate_eval_run.py`, update the evaluator schema instructions so model-backed oracle JSON can only use:

```text
pass, partial, pass-limited, pass-control, fail, blocked
```

and scores must be `0 / 5` through `5 / 5`.

- [ ] **Step 5: Run schema tests**

```bash
python3 -m unittest workspace/scripts/test_eval_run_common.py workspace/scripts/test_evaluate_eval_run.py workspace/scripts/test_validate_eval_run.py
```

Expected: all tests pass.

- [ ] **Step 6: Revalidate latest runs**

```bash
python3 workspace/scripts/validate_eval_run.py --bucket response --run-id 20260517-145735-response-try01-full-current-baseline
python3 workspace/scripts/validate_eval_run.py --bucket code --run-id 20260517-145735-code-try01-full-current-baseline
python3 workspace/scripts/validate_eval_run.py --bucket plugin --run-id 20260517-145735-plugin-try01-full-current-baseline
python3 workspace/scripts/validate_eval_run.py --bucket runtime --run-id 20260517-152141-runtime-try01-full-current-baseline
python3 workspace/scripts/validate_eval_run.py --bucket source --run-id 20260517-152835-source-try01-full-current-baseline
python3 workspace/scripts/validate_eval_run.py --bucket workflow --run-id 20260517-154712-workflow-try01-full-current-baseline
```

Expected: all six latest runs remain valid.

- [ ] **Step 7: Commit**

```bash
git add workspace/scripts/eval_run_common.py workspace/scripts/test_eval_run_common.py workspace/scripts/evaluate_eval_run.py workspace/scripts/test_evaluate_eval_run.py workspace/scripts/test_validate_eval_run.py
git commit -m "Tighten eval oracle scoring schema"
```

## Task 3: Block Absolute Local Path Leakage In Eval Artifacts

**Files:**
- Modify: `workspace/scripts/validate_eval_run.py`
- Modify: `workspace/scripts/test_validate_eval_run.py`

- [ ] **Step 1: Add failing tests for with-dddjango path leakage**

In `test_validate_eval_run.py`, create a run fixture where `raw/case-example-with-dddjango.txt` contains:

```text
/Users/hyun/Desktop/dddjango/workspace/develop/eval/code/answer/case-example.yaml
```

Expected finding:

```text
raw/case-example-with-dddjango.txt: output contains forbidden local path
```

- [ ] **Step 2: Add failing tests for prompt-input and report path leakage**

Use the same fixture style for:

```text
raw/case-example-with-dddjango-prompt-input.json
analysis/report.html
```

Expected: validation fails for both files when forbidden absolute paths appear.

- [ ] **Step 3: Implement a shared artifact scanner**

In `validate_eval_run.py`, add:

```python
def forbidden_local_path_markers() -> list[str]:
    roots = [REPO_ROOT, Path("/private/tmp")]
    return sorted({root.resolve(strict=False).as_posix() for root in roots})

def validate_no_forbidden_local_paths(run_dir: Path, case_id: str, variants: list[str]) -> list[str]:
    findings: list[str] = []
    markers = forbidden_local_path_markers()
    for path in artifact_paths_to_scan(run_dir, case_id, variants):
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(marker in text for marker in markers):
            findings.append(f"{path.relative_to(run_dir)}: output contains forbidden local path")
    return findings
```

Scan response `.txt`, prompt-input `.json`, stderr, events, answer-oracle evaluation JSON, and `analysis/report.html`. Allow run-relative paths. Reject absolute paths into the repo root, `/private/tmp`, and evaluator-only answer/private/run directories.

- [ ] **Step 4: Preserve baseline isolation semantics**

Keep the existing baseline-specific hidden repo path checks, but call the new scanner for both variants after common artifacts are present.

- [ ] **Step 5: Run validation tests**

```bash
python3 -m unittest workspace/scripts/test_validate_eval_run.py
```

Expected: pass.

- [ ] **Step 6: Run latest validation and record expected current failures**

Run:

```bash
python3 workspace/scripts/validate_eval_run.py --bucket code --run-id 20260517-145735-code-try01-full-current-baseline
```

Expected immediately after adding stricter scanning: current generated artifacts may fail because old raw outputs contain absolute paths. Do not weaken the validator; regenerate affected runs or mark old runs as pre-strict artifacts.

- [ ] **Step 7: Add path-sanitizing prompt text only if regeneration still leaks**

If fresh runs still leak local paths, update `run_eval_bucket.py` operator prompt wording to say:

```text
Use repo-relative paths only. Do not print /Users, /private/tmp, or absolute local workspace paths in the final answer.
```

- [ ] **Step 8: Commit**

```bash
git add workspace/scripts/validate_eval_run.py workspace/scripts/test_validate_eval_run.py workspace/scripts/run_eval_bucket.py
git commit -m "Reject local path leakage in eval artifacts"
```

## Task 4: Add Deterministic Code Artifact Checks

**Files:**
- Modify: `workspace/scripts/validate_eval_code_artifacts.py`
- Create or modify: `workspace/scripts/test_validate_eval_code_artifacts.py`
- Modify: `workspace/develop/eval/code/answer/*.yaml`

- [ ] **Step 1: Add answer YAML fields for deterministic checks**

For each code case that expects code, add:

```yaml
deterministic_checks:
  - id: unit-tests
    command: python -m unittest
    expected_exit: 0
    evidence: command-artifact
```

For no-code cases, add:

```yaml
deterministic_checks: []
```

- [ ] **Step 2: Add failing validator test for missing deterministic evidence**

Create a test run with a valid `changed-files.json` but no command evidence for a code-expected case. Expected failure:

```text
case-code-example with-ddjango missing deterministic check evidence: unit-tests
```

- [ ] **Step 3: Implement deterministic check parsing**

In `validate_eval_code_artifacts.py`, parse `deterministic_checks` from the answer YAML with a minimal YAML-block parser matching the existing script style. For each check, require a run artifact under:

```text
code/<case_id>/<variant>/checks/<check_id>-command.txt
code/<case_id>/<variant>/checks/<check_id>-exit.txt
code/<case_id>/<variant>/checks/<check_id>-stdout.txt
code/<case_id>/<variant>/checks/<check_id>-stderr.txt
```

Require `exit.txt` to match `expected_exit`.

- [ ] **Step 4: Teach code capture to record check artifacts**

Find the code-capture writer in `workspace/scripts/run_eval_bucket.py` or helper scripts. Add execution of declared deterministic checks inside the captured subject workspace after the model run. Store command/stdout/stderr/exit under the path required by Step 3.

- [ ] **Step 5: Run unit tests**

```bash
python3 -m unittest workspace/scripts/test_validate_eval_code_artifacts.py workspace/scripts/test_run_eval_bucket.py workspace/scripts/test_validate_eval_run.py
```

Expected: pass.

- [ ] **Step 6: Run a targeted code case**

```bash
make eval-one BUCKET=code CASE=case-code-coupon-tdd TRY_NUMBER=2 SCOPE=targeted TOPIC=deterministic-code-checks EXTRA_ARGS=--rerun JOBS=1
```

Expected: run completes, `validate_eval_code_artifacts.py` checks deterministic command evidence, and the rendered report embeds changed-files and diff artifacts.

- [ ] **Step 7: Commit**

```bash
git add workspace/scripts/validate_eval_code_artifacts.py workspace/scripts/test_validate_eval_code_artifacts.py workspace/scripts/run_eval_bucket.py workspace/scripts/test_run_eval_bucket.py workspace/develop/eval/code/answer
git commit -m "Add deterministic checks for code eval artifacts"
```

## Task 5: Add A Real Django/Django Ninja Code Fixture

**Files:**
- Create: `workspace/develop/eval/code/fixtures/django_shop_service/`
- Modify: `workspace/develop/eval/code/cases/plugin/public/*.md` for selected real-Django cases
- Modify: `workspace/develop/eval/code/cases/plugin/code-capture.json`
- Modify: `workspace/develop/eval/code/answer/*.yaml`

- [ ] **Step 1: Create a minimal Django project fixture**

Add a fixture with:

```text
django_shop_service/
  manage.py
  pyproject.toml
  shop_service/settings.py
  shop_service/urls.py
  apps/orders/models.py
  apps/orders/services.py
  apps/orders/api.py
  apps/orders/tests/test_order_api.py
```

Use SQLite. Keep external services out. Add Django Ninja only if it is available in the local eval environment; otherwise keep API contract cases in phase A and record a blocker for real Ninja runtime tests.

- [ ] **Step 2: Add deterministic commands**

Each real-Django fixture case must have checks:

```yaml
deterministic_checks:
  - id: django-tests
    command: python manage.py test
    expected_exit: 0
    evidence: command-artifact
  - id: django-check
    command: python manage.py check
    expected_exit: 0
    evidence: command-artifact
```

For migration cases, add:

```yaml
  - id: migration-plan
    command: python manage.py migrate --plan
    expected_exit: 0
    evidence: command-artifact
```

- [ ] **Step 3: Move one high-value code case first**

Start with `case-code-order-api`. Point it to the real fixture in `code-capture.json`. Keep all other code cases on the existing fixture until this path is green.

- [ ] **Step 4: Run targeted real-Django case**

```bash
make eval-one BUCKET=code CASE=case-code-order-api TRY_NUMBER=2 SCOPE=targeted TOPIC=real-django-order-api EXTRA_ARGS=--rerun JOBS=1
```

Expected: deterministic Django checks run and are captured.

- [ ] **Step 5: Expand only after one real case is green**

Move `case-code-status-migration` and `case-code-web-detail` next. Do not migrate all code cases in one commit.

- [ ] **Step 6: Commit**

```bash
git add workspace/develop/eval/code/fixtures/django_shop_service workspace/develop/eval/code/cases/plugin workspace/develop/eval/code/answer
git commit -m "Add real Django fixture for code evals"
```

## Task 6: Close Current with-dddjango Partial And Regressions

**Files:**
- Modify: `dddjango/skills/source-reference-audit/SKILL.md`
- Modify: `dddjango/skills/source-reference-audit/agents/openai.yaml`
- Modify: `dddjango/skills/architecture-implementation-patterns/agents/openai.yaml`
- Modify: `dddjango/skills/implementation-python/agents/openai.yaml`
- Modify: `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- Modify: `dddjango/skills/workflow-dddjango-subagents/references/handoff-contract.md`

- [ ] **Step 1: Fix source validation coverage partial**

In `source-reference-audit/SKILL.md`, strengthen `Validation Coverage`:

```markdown
- Every validation coverage matrix must include an `expected evidence` column. If the user asks for a coverage map/table and the column is absent, revise the table before answering.
```

Targeted eval:

```bash
make eval-one BUCKET=source CASE=case-source-validation-coverage TRY_NUMBER=2 SCOPE=targeted TOPIC=expected-evidence-column EXTRA_ARGS=--rerun JOBS=1
```

Expected: `with-dddjango` becomes `pass`, not `partial`.

- [ ] **Step 2: Tighten eval-leakage wording**

In `source-reference-audit/SKILL.md`, keep leakage guidance generic:

```markdown
- For leakage review, do not propose runtime wording that repeats eval-only labels such as answer oracle, private scoring text, prior run findings, hidden target behavior, or case ids. Use product-facing terms such as private evaluation material, internal criteria, and non-public validation notes.
```

Targeted eval:

```bash
make eval-one BUCKET=response CASE=case-response-eval-leakage TRY_NUMBER=2 SCOPE=targeted TOPIC=generic-leakage-language EXTRA_ARGS=--rerun JOBS=1
```

Expected: `with-dddjango` returns to `5 / 5` or at least no longer regresses against baseline.

- [ ] **Step 3: Tighten wrong-routing contrast**

Inspect `case-runtime-wrong-routing` oracle and current with-ddjango evaluation before editing. If the miss is workflow role-map priority, update `workflow-dddjango-subagents` routing text. If the miss is Django web routing, update `implementation-django-web` routing text. Do not edit both unless the oracle evidence requires both.

Targeted eval:

```bash
make eval-one BUCKET=runtime CASE=case-runtime-wrong-routing TRY_NUMBER=2 SCOPE=targeted TOPIC=wrong-routing-contrast EXTRA_ARGS=--rerun JOBS=1
```

Expected: `with-dddjango` reaches `5 / 5` or the evaluation summary no longer says role-map priority was undervalued.

- [ ] **Step 4: Tighten parallel ownership**

In `workflow-dddjango-subagents/references/handoff-contract.md`, add:

```markdown
- Parallel `May edit` scopes must be disjoint by concrete file path or module owner. If two roles need the same file, assign a single write owner and make the other role read-only review or advisory.
```

In `workflow-dddjango-subagents/SKILL.md`, add the same rule in one concise runtime bullet.

Targeted eval:

```bash
make eval-one BUCKET=workflow CASE=case-workflow-parallel-ownership TRY_NUMBER=2 SCOPE=targeted TOPIC=disjoint-parallel-ownership EXTRA_ARGS=--rerun JOBS=1
```

Expected: `with-dddjango` returns to `5 / 5`.

- [ ] **Step 5: Fix metadata nits from product review**

Change:

```yaml
architecture-implementation-patterns/agents/openai.yaml:
  short_description: "Provisional clean-architecture, hexagonal, CQRS, outbox patterns."

implementation-python/agents/openai.yaml:
  default_prompt: "Use $implementation-python to apply modern Python typing, dataclasses, Protocols, enums, pydantic v2 boundaries, and Ruff."

source-reference-audit/agents/openai.yaml:
  default_prompt: "Use $source-reference-audit to audit dddjango source provenance, conflict/gap/provisional status, and source/runtime boundaries; include validation coverage or eval traceability only when explicitly requested and permitted."
```

- [ ] **Step 6: Run skill validation**

```bash
python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

Expected: `OK: validation passed with 0 warning(s)`.

- [ ] **Step 7: Commit**

```bash
git add dddjango/skills/source-reference-audit dddjango/skills/architecture-implementation-patterns/agents/openai.yaml dddjango/skills/implementation-python/agents/openai.yaml dddjango/skills/workflow-dddjango-subagents
git commit -m "Close residual dddjango eval findings"
```

## Task 7: Rebuild Latest Reports And Browser-Check Navigation

**Files:**
- Generated only: `workspace/develop/eval/*/latest/report.html`
- Generated only: `workspace/develop/eval/*/runs/<run-id>/analysis/report.html`

- [ ] **Step 1: Run targeted evals for fixed cases**

Run the targeted commands from Task 6. Do not proceed until all targeted runs validate.

- [ ] **Step 2: Run bucket-level regressions**

For each touched bucket:

```bash
make eval-one BUCKET=source TRY_NUMBER=2 SCOPE=full TOPIC=source-audit-hardening EXTRA_ARGS=--rerun JOBS=3
make eval-one BUCKET=response TRY_NUMBER=2 SCOPE=full TOPIC=leakage-language-hardening EXTRA_ARGS=--rerun JOBS=3
make eval-one BUCKET=runtime TRY_NUMBER=2 SCOPE=full TOPIC=routing-hardening EXTRA_ARGS=--rerun JOBS=3
make eval-one BUCKET=workflow TRY_NUMBER=2 SCOPE=full TOPIC=ownership-hardening EXTRA_ARGS=--rerun JOBS=3
```

Expected: no `with-dddjango` fail, blocked, unscored, or missing artifacts.

- [ ] **Step 3: Run full eval after harness changes**

```bash
make eval-all TRY_NUMBER=2 SCOPE=full TOPIC=eval-quality-hardening EXTRA_ARGS=--rerun JOBS=3
```

Expected: all six buckets finish, final refresh renders category links to latest reports, and all `latest/report.html` redirect to canonical latest run IDs.

- [ ] **Step 4: Validate all packs and runs**

```bash
for b in response code plugin runtime source workflow; do
  python3 workspace/scripts/validate_eval_bucket_pack.py --bucket "$b"
done
```

Then validate the new run IDs emitted by `make eval-all`. Capture them from the printed `workspace/develop/eval/<bucket>/runs/<run-id>/analysis/report.html` lines:

```bash
python3 workspace/scripts/validate_eval_run.py --bucket response --run-id 20260517-180000-response-try02-full-eval-quality-hardening
python3 workspace/scripts/validate_eval_run.py --bucket code --run-id 20260517-180000-code-try02-full-eval-quality-hardening
python3 workspace/scripts/validate_eval_run.py --bucket plugin --run-id 20260517-180000-plugin-try02-full-eval-quality-hardening
python3 workspace/scripts/validate_eval_run.py --bucket runtime --run-id 20260517-180000-runtime-try02-full-eval-quality-hardening
python3 workspace/scripts/validate_eval_run.py --bucket source --run-id 20260517-180000-source-try02-full-eval-quality-hardening
python3 workspace/scripts/validate_eval_run.py --bucket workflow --run-id 20260517-180000-workflow-try02-full-eval-quality-hardening
```

Replace the example timestamp `20260517-180000` with the concrete timestamp printed by the command output. Do not put these example IDs into tests or source code.

- [ ] **Step 5: Validate readability for all latest reports**

```bash
for b in response code plugin runtime source workflow; do
  run=$(find "workspace/develop/eval/$b/runs" -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1)
  python3 workspace/scripts/validate_eval_report_readability.py --report "$run/analysis/report.html"
done
```

Expected: all six pass.

- [ ] **Step 6: Browser check**

Serve:

```bash
python3 -m http.server 8767 --bind 127.0.0.1 --directory workspace/develop/eval
```

Open:

```text
http://127.0.0.1:8767/response/latest/report.html
```

Check:

- category tabs are clickable
- each tab navigates to its latest bucket
- summary metrics are visible
- case detail modal opens
- no visible `unscored` or disabled category tab appears in latest reports unless the run really has unscored cases

## Task 8: Final Review And Commit Strategy

**Files:**
- Commit only source changes.
- Do not commit generated `runs/**` unless the user explicitly asks to version generated eval output.
- Commit `latest/report.html` only if the repository policy keeps latest aliases tracked.

- [ ] **Step 1: Run deterministic final checks**

```bash
python3 -m unittest \
  workspace/scripts/test_eval_run_common.py \
  workspace/scripts/test_evaluate_eval_run.py \
  workspace/scripts/test_validate_eval_run.py \
  workspace/scripts/test_validate_eval_bucket_pack.py \
  workspace/scripts/test_validate_skill_docs.py \
  workspace/scripts/test_render_eval_review_html.py \
  workspace/scripts/test_run_initial_eval.py

python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills

for b in response code plugin runtime source workflow; do
  python3 workspace/scripts/validate_eval_bucket_pack.py --bucket "$b"
done

git diff --check
```

Expected: all pass.

- [ ] **Step 2: Review dirty worktree**

Run:

```bash
git status --short
```

Classify files into:

- source changes to commit
- generated eval outputs to leave uncommitted
- unrelated pre-existing user changes to leave untouched

- [ ] **Step 3: Commit source changes in logical groups**

Recommended commits:

```bash
git add workspace/scripts/render_eval_review_html.py workspace/scripts/test_render_eval_review_html.py
git commit -m "Align eval report renderer with v2 contract"

git add workspace/scripts/eval_run_common.py workspace/scripts/test_eval_run_common.py workspace/scripts/evaluate_eval_run.py workspace/scripts/test_evaluate_eval_run.py workspace/scripts/validate_eval_run.py workspace/scripts/test_validate_eval_run.py
git commit -m "Harden eval schema and artifact validation"

git add workspace/scripts/validate_eval_code_artifacts.py workspace/scripts/test_validate_eval_code_artifacts.py workspace/scripts/run_eval_bucket.py workspace/scripts/test_run_eval_bucket.py workspace/develop/eval/code/answer workspace/develop/eval/code/cases/plugin workspace/develop/eval/code/fixtures/django_shop_service
git commit -m "Add deterministic code eval evidence"

git add dddjango/skills workspace/docs workspace/develop/eval/source/answer workspace/develop/eval/workflow/answer
git commit -m "Close residual dddjango skill eval findings"
```

Adjust staged files to the actual diff. Do not stage unrelated dirty files.

## Self-Review

- Spec coverage: covers report contract drift, code behavior evidence, permissive scoring, path leakage, current partial/regression cases, source-provisional metadata nits, latest report navigation, and final verification.
- Red-flag scan: plan avoids fake source/test values. Example run IDs are marked as command-output examples and must not be hard-coded.
- Type consistency: uses the existing `baseline` and `with-dddjango` artifact names, renderer `with_dddjango` data key, and `eval-report-v2` validator schema names.

## Execution Choice

Plan complete and saved here. Recommended execution is task-by-task with a checkpoint after each commit. Start with Task 1 because the current report contract failure makes the dashboard less trustworthy even when eval runs validate.
