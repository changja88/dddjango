# Post Eval Hardening Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the latest full eval insights into concrete improvements so `dddjango` evals measure reference-shaped DDD behavior, expose validation failures clearly, and avoid over-counting weak evidence.

**Architecture:** Keep public cases as user prompts, private answer files as evaluator authority, deterministic validators as artifact-integrity gates, and rendered reports as the operator-facing truth. Separate artifact validity from model-quality scoring so a weak baseline can be scored without making the whole run unreadable, while true invalid artifacts still fail the run.

**Tech Stack:** Markdown eval packs under `workspace/develop/eval`, Python stdlib validators and renderers under `workspace/scripts`, unittest/pytest script tests, `make eval-one`, `make eval-all`, and rendered HTML reports under ignored `runs/` and `latest/` directories.

---

## Current Signals

- `with-dddjango` improved every bucket in the latest full run: response `+0.9`, code `+0.6`, plugin `+2.0`, runtime `+1.3`, source `+1.6`, workflow `+1.1`.
- `code` is the main risk bucket: average is high (`4.9 / 5`) but integrated validation fails on `case-code-python-state baseline changed path is not allowed: apps/orders/services.py`.
- `case-code-ddd-order-placement` validates hidden behavior checks, but both baseline and `with-dddjango` scored `5 / 5`, so it is a DDD smoke test, not an uplift discriminator yet.
- `case-code-web-detail` regressed against baseline (`baseline 5 / 5`, `with-dddjango 4 / 5`) due to weaker display fallback/static linkage detail.
- `case-runtime-missing-metadata` remains `pass-limited` because the answer gathered prompt/source evidence but missed validation command output and semantic metadata alignment evidence.
- HTML now shows latest runs correctly, but report summaries still do not make run-level validation failure impossible to miss.

## File Structure

- Modify: `workspace/scripts/eval_run_identity.py`
  - Add first-class run validation manifest helpers that distinguish run validation from report rendering.
- Modify: `workspace/scripts/validate_eval_run.py`
  - Write a machine-readable failed or passed run validation manifest before exiting.
- Modify: `workspace/scripts/render_eval_review_html.py`
  - Display run validation status in summary/header and block reportability when validation failed or is missing.
- Modify: `workspace/scripts/test_render_eval_review_html.py`
  - Add regression tests for failed latest run visibility and validation status display.
- Modify: `workspace/scripts/validate_eval_code_artifacts.py`
  - Split artifact-hard failures from model-quality path-policy findings.
- Modify: `workspace/scripts/evaluate_eval_run.py`
  - Feed code policy findings to the answer-oracle evaluator so baseline overreach becomes a score signal.
- Modify: `workspace/scripts/run_eval_bucket.py`
  - Persist policy findings per case/variant after code capture.
- Modify: `workspace/scripts/test_validate_eval_code_artifacts.py`
  - Cover hard-vs-quality policy behavior.
- Modify: `workspace/develop/eval/code/answer/case-code-python-state.yaml`
  - Clarify whether `apps/orders/services.py` is a scoring defect or a hard artifact failure.
- Modify: `workspace/develop/eval/code/answer/case-code-ddd-order-placement.yaml`
  - Mark this as DDD smoke/regression evidence, not uplift evidence.
- Create: `workspace/develop/eval/code/cases/plugin/public/case-code-ddd-reservation-boundary.md`
  - Add a more discriminative DDD code case.
- Create: `workspace/develop/eval/code/answer/case-code-ddd-reservation-boundary.yaml`
  - Add private oracle for aggregate/context boundary decisions.
- Create: `workspace/develop/eval/code/fixtures/ddd_reservation_service/**`
  - Add a fixture where general coding skill is likely to mix domain boundaries unless guided by references.
- Modify: `workspace/scripts/eval_code_behavior_checks.py`
  - Add hidden behavior/source-shape checks for the new DDD reservation case and stronger web-detail checks.
- Modify: `dddjango/skills/implementation-django-web/SKILL.md`
  - Add a short, non-bloated acceptance checklist for display fallback/static linkage/render verification.
- Modify: `dddjango/skills/source-reference-audit/SKILL.md`
  - Add concise guidance to capture validation command output for metadata/runtime audits.
- Modify: `workspace/develop/eval/runtime/answer/case-runtime-missing-metadata.yaml`
  - Require validation output and semantic alignment evidence, not only file existence.

---

## Task 1: Make Run Validation First-Class In Reports

**Files:**
- Modify: `workspace/scripts/eval_run_identity.py`
- Modify: `workspace/scripts/validate_eval_run.py`
- Modify: `workspace/scripts/render_eval_review_html.py`
- Modify: `workspace/scripts/test_render_eval_review_html.py`

- [x] **Step 1: Write failing renderer test for failed latest validation**

Add a test that creates a latest code run with a failed run validation manifest and asserts the rendered report summary/header includes `validation: failed`, the failure text, and `reportability: blocked`.

Expected failure before implementation: the report only shows oracle summary and does not surface run-level validation failure.

- [x] **Step 2: Add run validation manifest helpers**

Add a new filename constant in `eval_run_identity.py`:

```python
RUN_VALIDATION_FILENAME = "RUN_VALIDATION.json"
```

Add writer/loader helpers that support:

```json
{
  "schema_version": 1,
  "run_id": "...",
  "bucket": "code",
  "scope": "full",
  "status": "failed",
  "case_ids": ["case-code-python-state"],
  "variants": ["baseline", "with-dddjango"],
  "findings": ["case-code-python-state baseline changed path is not allowed: apps/orders/services.py"],
  "created_at": "..."
}
```

`has_successful_validation(run_dir)` should prefer `RUN_VALIDATION.json` when present. Keep a fallback to existing `VALIDATION.json` for legacy runs only.

- [x] **Step 3: Write run validation manifest from `validate_eval_run.py`**

At the end of validation:

```python
if findings:
    run_identity.write_run_validation_manifest(..., status="failed", findings=findings)
    for finding in findings:
        print(f"FAIL: {finding}")
    raise SystemExit(1)

run_identity.write_run_validation_manifest(..., status="passed", findings=[])
print(...)
```

Expected: even failing runs leave machine-readable failure state for the report renderer.

- [x] **Step 4: Stop using report rendering as run validation**

Change `render_eval_report(..., record_validation_manifest=True)` so report-render checks do not make a failed run look validated. Either remove that write or write a separate `REPORT_VALIDATION.json`; do not write successful run validation from the renderer.

- [x] **Step 5: Render validation state**

Add `run_validation` to `build_report_data` and show it in the header/summary:

```text
validation: failed
validation findings: case-code-python-state baseline changed path is not allowed: apps/orders/services.py
```

If the latest attempt has no run validation manifest, show `validation: missing` and block reportability.

- [x] **Step 6: Verify**

Run:

```bash
uv run pytest workspace/scripts/test_render_eval_review_html.py workspace/scripts/test_eval_run_identity.py workspace/scripts/test_validate_eval_run.py
uv run python -B workspace/scripts/render_eval_review_html.py --refresh-latest
```

Expected: latest failed runs are visible, but their report summary cannot be mistaken for a clean pass.

---

## Task 2: Separate Artifact Integrity From Model-Quality Path Findings

**Files:**
- Modify: `workspace/scripts/validate_eval_code_artifacts.py`
- Modify: `workspace/scripts/run_eval_bucket.py`
- Modify: `workspace/scripts/evaluate_eval_run.py`
- Modify: `workspace/scripts/test_validate_eval_code_artifacts.py`
- Modify: `workspace/scripts/test_run_eval_bucket.py`
- Modify: `workspace/scripts/test_evaluate_eval_run.py`
- Modify: `workspace/develop/eval/code/answer/case-code-python-state.yaml`

- [x] **Step 1: Write failing tests for quality-only path violations**

Add a test where baseline changes a path outside `allowed_paths`, but the changed path is not generated, private, or evaluator-owned. Expected after implementation:

```text
validate_eval_code_artifacts exits 0
code/<case>/<variant>/policy-findings.json contains severity=quality
```

Keep hard failure tests for:

```text
db.sqlite3
__pycache__
workspace/develop/eval/**
dddjango/**
missing diff/source evidence
```

- [x] **Step 2: Persist policy findings**

Add per-variant output:

```text
code/<case>/<variant>/policy-findings.json
```

Shape:

```json
{
  "caseId": "case-code-python-state",
  "variant": "baseline",
  "findings": [
    {
      "severity": "quality",
      "rule": "allowed_paths",
      "path": "apps/orders/services.py",
      "message": "changed path is outside scoring allowed_paths"
    }
  ]
}
```

- [x] **Step 3: Keep artifact-hard failures hard**

The validator must still fail immediately on generated artifacts, forbidden evaluator/private paths, unsafe artifact paths, missing copied files, and behavior-check evidence mismatch.

- [x] **Step 4: Feed findings to evaluator**

Update `evaluate_eval_run.py` so answer-oracle prompts include policy findings next to `changed-files.json`, `diff.patch`, deterministic checks, and behavior checks.

Expected: baseline overreach lowers oracle score without invalidating the whole run.

- [x] **Step 5: Re-run the problematic validation**

Run:

```bash
uv run python -B workspace/scripts/validate_eval_run.py --bucket code --run-id 20260518-172633-code-try01-full-current-baseline
```

Expected after implementation: pass if the only remaining issue is baseline quality overreach; fail if hard artifact integrity is still broken.

---

## Task 3: Make Direct DDD Code Cases More Discriminative

**Files:**
- Create: `workspace/develop/eval/code/cases/plugin/public/case-code-ddd-reservation-boundary.md`
- Create: `workspace/develop/eval/code/answer/case-code-ddd-reservation-boundary.yaml`
- Create: `workspace/develop/eval/code/fixtures/ddd_reservation_service/README.md`
- Create: `workspace/develop/eval/code/fixtures/ddd_reservation_service/pyproject.toml`
- Create: `workspace/develop/eval/code/fixtures/ddd_reservation_service/apps/reservations/models.py`
- Create: `workspace/develop/eval/code/fixtures/ddd_reservation_service/apps/reservations/services.py`
- Create: `workspace/develop/eval/code/fixtures/ddd_reservation_service/tests/test_reservations.py`
- Modify: `workspace/develop/eval/code/cases/plugin/code-capture.json`
- Modify: `workspace/scripts/eval_code_behavior_checks.py`

- [x] **Step 1: Reclassify current DDD order case**

Update `case-code-ddd-order-placement.yaml`:

```yaml
score_interpretation: DDD smoke/regression score; use this to prove hidden behavior checks work, not as primary uplift evidence.
```

- [x] **Step 2: Add a business prompt that does not spoon-feed every tactical term**

Create public case:

```markdown
예약 요청/확정/만료 흐름을 DDD 기준에 맞게 리팩터링해줘.

요구사항:
- Reservation bounded context 안에서 사용하는 유비쿼터스 언어가 코드 이름과 테스트에 드러나야 해.
- Reservation aggregate root가 숙박일 수, 확정, 만료 상태 전이 규칙을 보호해야 해.
- room availability나 inventory는 같은 aggregate 안의 자식 객체처럼 섞지 말고 외부 경계로 표현해.
- 과한 repository/UoW/hexagonal 구조는 만들지 마.
- `python3 -m unittest discover -s tests` 결과를 보고해줘.
```

- [x] **Step 3: Add fixture that tempts procedural service logic**

Starter `services.py` directly mutates reservation status and room holds. Starter tests prove happy paths so both variants must add missing boundary tests.

- [x] **Step 4: Add private DDD oracle**

Set:

```yaml
case_role: ddd_direct
expected_outcomes:
  baseline: partial
  with_dddjango: pass
```

Require:

```yaml
ddd_observations:
  bounded_context: Reservation
  aggregate_root: Reservation
  invariants:
    - a reservation must be requested for at least one night
    - a reservation can be confirmed only from requested status
    - a confirmed reservation cannot be expired
  application_service_boundary: service coordinates reservation persistence and room availability handoff without owning lifecycle rules
```

- [x] **Step 5: Add hidden source-shape checks**

Extend `eval_code_behavior_checks.py` with:

```text
case-code-ddd-reservation-boundary
```

Check:
- `Reservation` exposes request, confirm, and expire behavior.
- room availability hold is represented as a boundary concept.
- service does not directly assign reservation status.
- invalid lifecycle transitions raise in the in-memory fixture.

- [ ] **Step 6: Verify targeted run before full run**

Run:

```bash
make eval-one BUCKET=code SCOPE=targeted TOPIC=ddd-reservation-boundary CASE=case-code-ddd-reservation-boundary EXTRA_ARGS=--rerun
```

Expected: evaluator sees a real difference between general code generation and reference-shaped DDD guidance.

---

## Task 4: Fix Django Web Skill Weakness Exposed By `case-code-web-detail`

**Files:**
- Modify: `dddjango/skills/implementation-django-web/SKILL.md`
- Modify: `workspace/develop/eval/code/answer/case-code-web-detail.yaml`
- Modify: `workspace/scripts/eval_code_behavior_checks.py`

- [x] **Step 1: Add a concise acceptance checklist to the skill**

Keep this short to respect skill-creator context rules:

```markdown
Before finishing template/static work:
- view/context code provides display-ready fallback values for optional fields
- templates render display values and avoid business-state decisions
- static files changed by the task are referenced by the rendered page or explicitly reported as unused
- run a render/template test when the project has one; otherwise state the limitation
```

- [x] **Step 2: Add hidden check for web-detail**

Extend `eval_code_behavior_checks.py` for `case-code-web-detail` to inspect captured files:
- template does not access `order.status`, `order.memo`, or other domain object fields directly
- context has fallback for empty memo
- changed static CSS is referenced by template or no CSS is changed

- [ ] **Step 3: Re-run targeted case**

Run:

```bash
make eval-one BUCKET=code SCOPE=targeted TOPIC=web-detail-quality CASE=case-code-web-detail EXTRA_ARGS=--rerun
```

Expected: `with-dddjango` no longer loses to baseline on display fallback/static linkage.

---

## Task 5: Strengthen Runtime Metadata Audit Evidence

**Files:**
- Modify: `dddjango/skills/source-reference-audit/SKILL.md`
- Modify: `workspace/develop/eval/runtime/answer/case-runtime-missing-metadata.yaml`
- Modify: `workspace/scripts/validate_eval_bucket_pack.py`

- [x] **Step 1: Add a small validation-output rule to the skill**

Add concise guidance:

```markdown
When auditing skill metadata/runtime cache consistency, preserve command evidence for:
- generated skill source vs runtime cache skill list
- `SKILL.md` frontmatter vs `agents/openai.yaml` semantic alignment
- validation command output, especially `workspace/scripts/validate_skill_docs.py` when available
```

- [x] **Step 2: Tighten runtime answer oracle**

Require these evidence points:
- skill source list
- runtime prompt/input or cache list
- `agents/openai.yaml` semantic alignment, not only existence
- validation command output or explicit reason it could not be run

- [x] **Step 3: Add pack validation if answer schema needs it**

If runtime answers start using structured evidence fields, add a restricted schema check in `validate_eval_bucket_pack.py` rather than relying on prose.

- [ ] **Step 4: Re-run targeted runtime case**

Run:

```bash
make eval-one BUCKET=runtime SCOPE=targeted TOPIC=metadata-audit-evidence CASE=case-runtime-missing-metadata EXTRA_ARGS=--rerun
```

Expected: `with-dddjango` includes validation output and can move from `pass-limited` to `pass`.

---

## Task 6: Restore Comparable Trend Metrics

**Files:**
- Modify: `workspace/scripts/render_eval_review_html.py`
- Modify: `workspace/scripts/test_render_eval_review_html.py`

- [x] **Step 1: Add a failing trend test**

Create two full runs with comparable bucket/case set but different run IDs. The latest report should show previous run metrics instead of:

```text
No previous comparable run for trend metrics.
```

- [x] **Step 2: Add fallback comparable selection**

If fingerprint is missing or changed by eval-pack evolution, use a conservative fallback:
- same bucket
- same scope `full`
- previous run has overlapping case IDs
- exclude targeted/manual runs

- [x] **Step 3: Render trend confidence**

Show whether comparison is:

```text
fingerprint-exact
case-overlap-fallback
unavailable
```

Expected: operators can tell whether trend is exact or approximate.

---

## Task 7: Verification Sequence

**Files:**
- Generated only: `workspace/develop/eval/*/runs/**`
- Generated only: `workspace/develop/eval/*/latest/**`

- [x] **Step 1: Static tests**

Run:

```bash
uv run pytest workspace/scripts/test_eval_answer_yaml.py \
  workspace/scripts/test_validate_eval_code_artifacts.py \
  workspace/scripts/test_validate_eval_bucket_pack.py \
  workspace/scripts/test_validate_eval_run.py \
  workspace/scripts/test_run_eval_bucket.py \
  workspace/scripts/test_render_eval_review_html.py
```

- [x] **Step 2: Pack validation**

Run:

```bash
uv run python -B workspace/scripts/validate_eval_bucket_pack.py
```

- [ ] **Step 3: Targeted evals**

Run:

```bash
make eval-one BUCKET=code SCOPE=targeted TOPIC=python-state-policy CASE=case-code-python-state EXTRA_ARGS=--rerun
make eval-one BUCKET=code SCOPE=targeted TOPIC=ddd-reservation-boundary CASE=case-code-ddd-reservation-boundary EXTRA_ARGS=--rerun
make eval-one BUCKET=code SCOPE=targeted TOPIC=web-detail-quality CASE=case-code-web-detail EXTRA_ARGS=--rerun
make eval-one BUCKET=runtime SCOPE=targeted TOPIC=metadata-audit-evidence CASE=case-runtime-missing-metadata EXTRA_ARGS=--rerun
```

- [ ] **Step 4: Full eval**

Run:

```bash
make eval-all TRY_NUMBER=1 SCOPE=full TOPIC=post-eval-hardening JOBS=3
```

- [ ] **Step 5: Report refresh and browser check**

Run:

```bash
uv run python -B workspace/scripts/render_eval_review_html.py --refresh-latest
```

Open:

```text
http://127.0.0.1:8765/code/latest/report.html
```

Expected:
- latest report points to newest full attempt
- validation status is visible
- category navigation works
- hard validation failure is not hidden behind high oracle scores

---

## Skill-Creator Review

- **Concise skill updates:** Pass with constraint. Skill edits must be short checklists in `SKILL.md`; detailed examples belong in eval answer files or hidden validators, not in skill bodies.
- **Appropriate degrees of freedom:** Needs explicit split. Fragile validation belongs in scripts (`eval_code_behavior_checks.py`, validators). Skills should give judgment heuristics, not long executable procedures.
- **Validation integrity:** Needs improvement. Current DDD direct case leaked too much target shape through the public prompt and baseline also passed. New discriminative cases should use realistic business prompts and keep exact scoring criteria in private answers/hidden checks.
- **Progressive disclosure:** Pass if web/runtime skill changes stay small. Do not paste eval-specific oracle details into runtime skills.
- **Agents metadata alignment:** Runtime metadata audit should verify `agents/openai.yaml` semantic alignment when that is the task, but normal implementation skills should not load metadata unless relevant.
- **Forward testing:** Required before full run. Targeted evals for `case-code-python-state`, `case-code-ddd-reservation-boundary`, `case-code-web-detail`, and `case-runtime-missing-metadata` should pass before `make eval-all`.

## Open Decisions

- Whether baseline quality path violations should always be non-fatal, or only non-fatal for `allowed_paths` while `forbidden_paths` remains hard for both variants.
- Whether `case-code-ddd-order-placement` should stay as smoke evidence or be made harder. Current recommendation: keep it as smoke and add a new discriminator instead.
- Whether reportability should become `blocked` on missing validation manifests for all latest attempts. Current recommendation: yes, because latest can be visible without implying success.
