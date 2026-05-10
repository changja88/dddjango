# Eval Report Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the eval report with a v2 evaluation-item-first report that shows a type-aware summary, filterable evaluation table, and large baseline-vs-dddjango comparison modal.

**Architecture:** Keep `workspace/scripts/render_plugin_eval_report.py` as the data builder and `workspace/develop/evals/templates/run-report.html` as a static HTML report. Add a v2 contract (`schema_version`, `summary`, `evaluation_items`) while preserving raw artifact embedding for evidence links. Move validation to the v2 contract so the old `caseStories`/`evaluationFlow` shape is no longer required.

**Tech Stack:** Python 3 standard library, static HTML/CSS/JavaScript, existing raw eval artifacts under `workspace/develop/evals/runs/*`, local browser checks through the in-app browser or Playwright MCP.

---

## Spec

Implement [2026-05-10-eval-report-redesign-design.md](/Users/hyun/Desktop/dddjango/workspace/docs/superpowers/specs/2026-05-10-eval-report-redesign-design.md).

## Scope Check

This is one coherent subsystem: the eval report data contract, renderer, template, and validator. It should not be split into separate specs because each task produces the same report surface and the validator is the acceptance gate for the renderer/template pair.

## File Map

- Modify `workspace/scripts/validate_eval_report_readability.py`
  - Responsibility: validate `schema_version: "eval-report-v2"`, required summary sections, required `evaluation_items` fields, variant field completeness, and v2 template anchors/tokens.
- Modify `workspace/scripts/render_plugin_eval_report.py`
  - Responsibility: build normalized v2 `evaluation_items`, type-aware summary sections, canonical variant keys, and change direction from current case-level evaluator data and code-artifact smoke data.
- Modify `workspace/develop/evals/templates/run-report.html`
  - Responsibility: render only the v2 primary screen (`#report-summary`, `#evaluation-filters`, `#evaluation-items-table`) and `#comparison-modal`, while retaining embedded artifact viewing helpers for evidence links.
- Regenerate `workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html`
  - Responsibility: comprehensive report using v2 contract and UI.
- Regenerate `workspace/develop/evals/runs/local-code-artifact-real/report.html`
  - Responsibility: focused code-backed report using v2 contract and UI.

## Task 1: Move Readability Validation To V2 Contract

**Files:**
- Modify: `workspace/scripts/validate_eval_report_readability.py`

- [ ] **Step 1: Run current validator to capture the baseline state**

Run:

```bash
python3 workspace/scripts/validate_eval_report_readability.py --report workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html
python3 workspace/scripts/validate_eval_report_readability.py --report workspace/develop/evals/runs/local-code-artifact-real/report.html --require-code-artifacts
```

Expected before this task: both commands pass against the old report contract.

- [ ] **Step 2: Replace old `caseStories` contract checks with v2 helpers**

In `workspace/scripts/validate_eval_report_readability.py`, keep `parse_args()` and `extract_report_data()`. Replace the current `main()` validation body with helpers shaped like this:

```python
V2_SCHEMA_VERSION = "eval-report-v2"
SCORE_TYPES = {"numeric", "pass_fail", "hard_gate", "narrative"}
SCORE_TYPE_SOURCES = {"explicit", "inferred"}
SOURCE_GRANULARITIES = {"case", "request", "rubric", "hard_gate", "artifact_check"}
CHANGE_DIRECTIONS = {"improved", "regressed", "unchanged", "mixed", "not_comparable"}
VARIANT_KEYS = ("baseline", "with_dddjango")
REQUIRED_VARIANT_KEYS = {
    "score",
    "response_summary",
    "response",
    "evaluation_summary",
    "evaluation",
    "evidence",
}


def require_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise AssertionError(f"{label} must be an object")
    return value


def require_non_empty_text(value: object, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise AssertionError(f"{label} must not be empty")
    return text


def require_keys(value: dict[str, object], keys: set[str], label: str) -> None:
    missing = sorted(keys - set(value))
    if missing:
        raise AssertionError(f"{label} missing: {', '.join(missing)}")


def validate_variant(variant: object, label: str) -> None:
    item = require_object(variant, label)
    require_keys(item, REQUIRED_VARIANT_KEYS, label)
    require_non_empty_text(item.get("score"), f"{label}.score")
    require_non_empty_text(item.get("response_summary"), f"{label}.response_summary")
    require_non_empty_text(item.get("response"), f"{label}.response")
    require_non_empty_text(item.get("evaluation_summary"), f"{label}.evaluation_summary")
    require_non_empty_text(item.get("evaluation"), f"{label}.evaluation")
    evidence = item.get("evidence")
    if not isinstance(evidence, list):
        raise AssertionError(f"{label}.evidence must be a list")


def validate_evaluation_item(item: object, index: int) -> str:
    row = require_object(item, f"evaluation_items[{index}]")
    required = {
        "id",
        "title",
        "source_granularity",
        "test_content_ko",
        "score_type",
        "score_type_source",
        "baseline",
        "with_dddjango",
        "change",
    }
    require_keys(row, required, f"evaluation_items[{index}]")
    require_non_empty_text(row.get("id"), f"evaluation_items[{index}].id")
    require_non_empty_text(row.get("title"), f"evaluation_items[{index}].title")
    require_non_empty_text(row.get("test_content_ko"), f"evaluation_items[{index}].test_content_ko")

    source_granularity = require_non_empty_text(
        row.get("source_granularity"),
        f"evaluation_items[{index}].source_granularity",
    )
    if source_granularity not in SOURCE_GRANULARITIES:
        raise AssertionError(f"unsupported source_granularity: {source_granularity}")

    score_type = require_non_empty_text(row.get("score_type"), f"evaluation_items[{index}].score_type")
    if score_type not in SCORE_TYPES:
        raise AssertionError(f"unsupported score_type: {score_type}")

    score_type_source = require_non_empty_text(
        row.get("score_type_source"),
        f"evaluation_items[{index}].score_type_source",
    )
    if score_type_source not in SCORE_TYPE_SOURCES:
        raise AssertionError(f"unsupported score_type_source: {score_type_source}")

    change = require_object(row.get("change"), f"evaluation_items[{index}].change")
    direction = require_non_empty_text(change.get("direction"), f"evaluation_items[{index}].change.direction")
    if direction not in CHANGE_DIRECTIONS:
        raise AssertionError(f"unsupported change.direction: {direction}")

    validate_variant(row.get("baseline"), f"evaluation_items[{index}].baseline")
    validate_variant(row.get("with_dddjango"), f"evaluation_items[{index}].with_dddjango")
    return score_type


def validate_v2_contract(data: dict[str, object]) -> None:
    if data.get("schema_version") != V2_SCHEMA_VERSION:
        raise AssertionError(f"schema_version must be {V2_SCHEMA_VERSION}")

    summary = require_object(data.get("summary"), "summary")
    sections = summary.get("sections")
    if not isinstance(sections, list) or not sections:
        raise AssertionError("summary.sections must be a non-empty list")
    require_non_empty_text(summary.get("conclusion"), "summary.conclusion")
    risks = summary.get("risks")
    if not isinstance(risks, list):
        raise AssertionError("summary.risks must be a list")

    evaluation_items = data.get("evaluation_items")
    if not isinstance(evaluation_items, list) or not evaluation_items:
        raise AssertionError("evaluation_items must be a non-empty list")
    present_types = {validate_evaluation_item(item, index) for index, item in enumerate(evaluation_items)}

    section_types = set()
    for index, section in enumerate(sections):
        section_obj = require_object(section, f"summary.sections[{index}]")
        section_type = require_non_empty_text(section_obj.get("type"), f"summary.sections[{index}].type")
        if section_type not in SCORE_TYPES:
            raise AssertionError(f"unsupported summary section type: {section_type}")
        metrics = section_obj.get("metrics")
        if not isinstance(metrics, list) or not metrics:
            raise AssertionError(f"summary.sections[{index}].metrics must be a non-empty list")
        section_types.add(section_type)

    missing_sections = sorted(present_types - section_types)
    if missing_sections:
        raise AssertionError(f"missing summary section for score_type: {', '.join(missing_sections)}")


def validate_v2_template(html: str) -> None:
    required_tokens = [
        'id="report-summary"',
        'id="evaluation-filters"',
        'id="evaluation-items-table"',
        'id="comparison-modal"',
        "renderReportSummary",
        "renderEvaluationItems",
        "openComparisonModal",
        "closeComparisonModal",
        "상세 보기",
        "Baseline",
        "With dddjango",
    ]
    missing_tokens = [token for token in required_tokens if token not in html]
    if missing_tokens:
        raise AssertionError(f"missing v2 template tokens: {', '.join(missing_tokens)}")
```

- [ ] **Step 3: Replace `main()` with the v2 validation flow**

Use this shape:

```python
def main() -> int:
    args = parse_args()
    html = args.report.read_text(encoding="utf-8")
    data = extract_report_data(html)

    validate_v2_contract(data)
    validate_v2_template(html)

    embedded = data.get("embeddedArtifacts", {})
    embedded_count = len(embedded) if isinstance(embedded, dict) else 0
    print(
        f"readability validation passed: {len(data['evaluation_items'])} evaluation items, "
        f"{embedded_count} embedded artifacts"
    )
    return 0
```

- [ ] **Step 4: Run validator to verify RED**

Run:

```bash
python3 workspace/scripts/validate_eval_report_readability.py --report workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html
python3 workspace/scripts/validate_eval_report_readability.py --report workspace/develop/evals/runs/local-code-artifact-real/report.html --require-code-artifacts
```

Expected after Step 3: both fail with `schema_version must be eval-report-v2`.

- [ ] **Step 5: Commit validator RED**

```bash
git add workspace/scripts/validate_eval_report_readability.py
git commit -m "Require eval report v2 contract"
```

## Task 2: Build V2 Evaluation Items In The Renderer

**Files:**
- Modify: `workspace/scripts/render_plugin_eval_report.py`

- [ ] **Step 1: Add v2 constants and normalization helpers**

Add these near the existing constants after `CODE_ARTIFACT_TYPES`:

```python
V2_SCHEMA_VERSION = "eval-report-v2"
SCORE_TYPES = {"numeric", "pass_fail", "hard_gate", "narrative"}
PASS_FAIL_RANK = {
    "fail": 0,
    "blocked": 0,
    "partial": 1,
    "pass-limited": 1,
    "pass-control": 2,
    "pass": 2,
}
```

Add these helpers after `score_text()`:

```python
def response_summary(text: str, *, limit: int = 220) -> str:
    normalized = " ".join(str(text or "").strip().split())
    if not normalized:
        return "응답이 비어 있습니다."
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 1]}..."


def infer_score_type(score: object) -> str:
    text = str(score or "").strip().lower()
    if re.search(r"\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?", text):
        return "numeric"
    if text in PASS_FAIL_RANK:
        return "pass_fail"
    if "hard gate" in text or "gate" in text:
        return "hard_gate"
    if text in {"not scored", "n/a", "not evaluated"}:
        return "narrative"
    return "narrative"


def parse_score_ratio(score: object) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", str(score or ""))
    if not match:
        return None
    value = float(match.group(1))
    maximum = float(match.group(2))
    if maximum <= 0:
        return None
    return value / maximum


def compare_numeric_scores(baseline_score: str, with_score: str, *, higher_is_better: bool = True) -> str:
    baseline_ratio = parse_score_ratio(baseline_score)
    with_ratio = parse_score_ratio(with_score)
    if baseline_ratio is None or with_ratio is None:
        return "not_comparable"
    if baseline_ratio == with_ratio:
        return "unchanged"
    improved = with_ratio > baseline_ratio if higher_is_better else with_ratio < baseline_ratio
    return "improved" if improved else "regressed"


def compare_pass_fail_scores(baseline_score: str, with_score: str) -> str:
    baseline_rank = PASS_FAIL_RANK.get(str(baseline_score or "").strip().lower())
    with_rank = PASS_FAIL_RANK.get(str(with_score or "").strip().lower())
    if baseline_rank is None or with_rank is None:
        return "not_comparable"
    if baseline_rank == with_rank:
        return "unchanged"
    return "improved" if with_rank > baseline_rank else "regressed"


def change_direction(score_type: str, baseline_score: str, with_score: str) -> str:
    if score_type == "numeric":
        return compare_numeric_scores(baseline_score, with_score)
    if score_type == "pass_fail":
        return compare_pass_fail_scores(baseline_score, with_score)
    return "not_comparable"


def change_label(direction: str) -> str:
    labels = {
        "improved": "개선",
        "regressed": "하락",
        "unchanged": "동일",
        "mixed": "혼합",
        "not_comparable": "비교 불가",
    }
    return labels.get(direction, direction)
```

- [ ] **Step 2: Add v2 variant and item builders**

Add these helpers after `variant_story()`:

```python
def variant_v2(case: dict[str, object], case_id: str, variant: str) -> dict[str, object]:
    is_with = variant == "with-dddjango"
    score_key = "with" if is_with else "baseline"
    good_key = "with_good" if is_with else "baseline_good"
    gap_key = "with_poor" if is_with else "baseline_poor"
    response_text = read(RAW_DIR / f"{case_id}-{variant}.txt").strip()
    score = score_text(case, score_key)
    strengths = str(case.get(good_key) or "").strip()
    gaps = str(case.get(gap_key) or "").strip()
    evaluation_parts = [part for part in [strengths, gaps, str(case.get("score_note") or "").strip()] if part]
    evidence = captured_artifacts(
        [
            artifact("response", f"raw/{case_id}-{variant}.txt"),
            artifact("command", f"raw/{case_id}-{variant}-command.txt"),
            artifact("events", f"raw/{case_id}-{variant}-events.jsonl"),
            artifact("stderr", f"raw/{case_id}-{variant}.stderr.txt"),
        ]
    )
    if case_evidence_mode(case_id, load_code_capture_metadata()) == "code-backed":
        evidence.extend(
            captured_artifacts(
                [
                    artifact("changed files", f"code/{case_id}/{variant}/changed-files.json"),
                    artifact("diff", f"code/{case_id}/{variant}/diff.patch"),
                ]
            )
        )
    return {
        "score": score,
        "response_summary": response_summary(response_text),
        "response": response_text or "응답이 캡처되지 않았습니다.",
        "evaluation_summary": strengths or str(case.get("score_note") or "평가 요약이 없습니다."),
        "evaluation": "\n\n".join(evaluation_parts) or "평가를 실행하지 않았습니다.",
        "evidence": evidence,
    }


def evaluation_item_v2(case: dict[str, object]) -> dict[str, object]:
    case_id = str(case["case"])
    prompt_text = read(RAW_DIR / f"{case_id}-public-prompt.md") or str(case.get("prompt") or "")
    test_content = extract_request_text(prompt_text) or str(case.get("prompt") or "")
    baseline = variant_v2(case, case_id, "baseline")
    with_dddjango = variant_v2(case, case_id, "with-dddjango")
    score_type = infer_score_type(baseline["score"])
    if score_type == "narrative":
        score_type = infer_score_type(with_dddjango["score"])
    direction = change_direction(score_type, str(baseline["score"]), str(with_dddjango["score"]))
    return {
        "id": case_id,
        "title": str(case["title"]),
        "source_granularity": "case",
        "source_case_ids": [case_id],
        "test_content_ko": test_content,
        "description_ko": str(case.get("prompt") or test_content),
        "score_type": score_type,
        "score_type_source": "inferred",
        "higher_is_better": True,
        "baseline": baseline,
        "with_dddjango": with_dddjango,
        "change": {
            "direction": direction,
            "label": change_label(direction),
        },
    }
```

- [ ] **Step 3: Add v2 summary builder**

Add after `evaluation_item_v2()`:

```python
def metric(label: str, value: object) -> dict[str, str]:
    return {"label": label, "value": str(value)}


def build_numeric_summary(items: list[dict[str, object]]) -> dict[str, object]:
    baseline_values = []
    with_values = []
    for item in items:
        baseline_ratio = parse_score_ratio(str(item["baseline"]["score"]))
        with_ratio = parse_score_ratio(str(item["with_dddjango"]["score"]))
        if baseline_ratio is not None and with_ratio is not None:
            baseline_values.append(baseline_ratio)
            with_values.append(with_ratio)
    metrics = [metric("항목 수", len(items))]
    if baseline_values and with_values:
        baseline_avg = sum(baseline_values) / len(baseline_values)
        with_avg = sum(with_values) / len(with_values)
        metrics.extend(
            [
                metric("baseline 평균", f"{baseline_avg * 100:.1f}%"),
                metric("with-dddjango 평균", f"{with_avg * 100:.1f}%"),
                metric("변화", f"{(with_avg - baseline_avg) * 100:+.1f}%p"),
            ]
        )
    return {"type": "numeric", "title": "정량 점수 항목", "metrics": metrics}


def build_pass_fail_summary(items: list[dict[str, object]]) -> dict[str, object]:
    def count_for(variant: str, value: str) -> int:
        return sum(1 for item in items if str(item[variant]["score"]).lower() == value)

    return {
        "type": "pass_fail",
        "title": "Pass/Fail 항목",
        "metrics": [
            metric("항목 수", len(items)),
            metric("baseline pass", count_for("baseline", "pass")),
            metric("baseline partial", count_for("baseline", "partial")),
            metric("baseline fail", count_for("baseline", "fail")),
            metric("with-dddjango pass", count_for("with_dddjango", "pass")),
            metric("with-dddjango partial", count_for("with_dddjango", "partial")),
            metric("with-dddjango fail", count_for("with_dddjango", "fail")),
        ],
    }


def build_generic_summary(score_type: str, title: str, items: list[dict[str, object]]) -> dict[str, object]:
    return {
        "type": score_type,
        "title": title,
        "metrics": [
            metric("항목 수", len(items)),
            metric("개선", sum(1 for item in items if item["change"]["direction"] == "improved")),
            metric("하락", sum(1 for item in items if item["change"]["direction"] == "regressed")),
            metric("동일", sum(1 for item in items if item["change"]["direction"] == "unchanged")),
        ],
    }


def build_summary_v2(items: list[dict[str, object]]) -> dict[str, object]:
    by_type = {
        score_type: [item for item in items if item["score_type"] == score_type]
        for score_type in SCORE_TYPES
    }
    sections = []
    if by_type["numeric"]:
        sections.append(build_numeric_summary(by_type["numeric"]))
    if by_type["pass_fail"]:
        sections.append(build_pass_fail_summary(by_type["pass_fail"]))
    if by_type["hard_gate"]:
        sections.append(build_generic_summary("hard_gate", "Hard Gate 항목", by_type["hard_gate"]))
    if by_type["narrative"]:
        sections.append(build_generic_summary("narrative", "서술형 평가 항목", by_type["narrative"]))

    improved = sum(1 for item in items if item["change"]["direction"] == "improved")
    regressed = sum(1 for item in items if item["change"]["direction"] == "regressed")
    return {
        "sections": sections,
        "conclusion": f"with-ddjango 개선 항목 {improved}개, 하락 항목 {regressed}개입니다.",
        "risks": [
            "평가 항목은 현재 저장된 evaluator judgment 기준입니다.",
            "case 내부 요청별 세부 평가는 별도 evaluator artifact가 있을 때 request/rubric row로 확장합니다.",
        ],
    }


def attach_v2_contract(data: dict[str, object], cases: list[dict[str, object]]) -> dict[str, object]:
    evaluation_items = [evaluation_item_v2(case) for case in cases]
    data["schema_version"] = V2_SCHEMA_VERSION
    data["summary"] = build_summary_v2(evaluation_items)
    data["evaluation_items"] = evaluation_items
    return data
```

- [ ] **Step 4: Attach v2 contract in both report builders**

In `build_report_data()`, keep the current returned dictionary contents intact and only wrap the return value:

```diff
-    return {
+    data = {
         "title": "dddjango Plugin Eval Report",
         "run": {
```

At the end of that same dictionary, return the wrapped v2 contract:

```diff
-    }
+    }
+    return attach_v2_contract(data, CASE_EVALS)
```

In `build_code_artifact_report_data(cases)`, make the same wrapper change:

```diff
-    return {
+    data = {
         "title": "dddjango Code Artifact Eval Report",
         "run": {
```

At the end of that dictionary, return:

```diff
-    }
+    }
+    return attach_v2_contract(data, cases)
```

Do not remove the existing report keys during this task. Keeping them in `data` lets `collect_embedded_artifacts(data)` continue to discover evidence links while the template is being migrated.

- [ ] **Step 5: Render reports and verify validator still fails on template tokens**

Run:

```bash
python3 workspace/scripts/render_plugin_eval_report.py
python3 workspace/scripts/render_plugin_eval_report.py --run-id local-code-artifact-real --code-artifact-run
python3 workspace/scripts/validate_eval_report_readability.py --report workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html
```

Expected after renderer changes and before template changes: validation fails with missing v2 template tokens such as `#report-summary` or `openComparisonModal`.

- [ ] **Step 6: Commit renderer v2 data**

```bash
git add workspace/scripts/render_plugin_eval_report.py workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html workspace/develop/evals/runs/local-code-artifact-real/report.html
git commit -m "Build eval report v2 data"
```

## Task 3: Replace The Template With The V2 Report Surface

**Files:**
- Modify: `workspace/develop/evals/templates/run-report.html`

- [ ] **Step 1: Replace the section navigation and main body with v2 anchors**

In `workspace/develop/evals/templates/run-report.html`, make the visible app shell contain these required anchors:

```html
<nav aria-label="Report sections">
  <a href="#report-summary">Summary</a>
  <a href="#evaluation-items">Evaluation Items</a>
  <a href="#evidence-artifacts">Evidence Artifacts</a>
</nav>

<main>
  <section id="report-summary" aria-labelledby="report-summary-heading">
    <h2 id="report-summary-heading">Summary</h2>
    <div id="summary-sections" class="summary-grid"></div>
    <div id="summary-conclusion" class="callout"></div>
  </section>

  <section id="evaluation-items" aria-labelledby="evaluation-items-heading">
    <h2 id="evaluation-items-heading">Evaluation Items</h2>
    <div id="evaluation-filters" class="toolbar" aria-label="Evaluation item filters"></div>
    <div class="table-wrap">
      <table id="evaluation-items-table">
        <thead>
          <tr>
            <th>평가 항목</th>
            <th>Type</th>
            <th>Baseline 점수</th>
            <th>With dddjango 점수</th>
            <th>변화</th>
            <th>Baseline 응답/평가</th>
            <th>With dddjango 응답/평가</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
      <div id="evaluation-empty-state" class="empty" hidden>조건에 맞는 평가 항목이 없습니다.</div>
    </div>
  </section>

  <section id="evidence-artifacts" aria-labelledby="evidence-artifacts-heading">
    <h2 id="evidence-artifacts-heading">Evidence Artifacts</h2>
    <div class="callout">
      상세 모달의 evidence 링크는 가능한 경우 내장 artifact viewer에서 열립니다.
    </div>
    <div id="artifact-index-content"></div>
  </section>
</main>
```

- [ ] **Step 2: Add the comparison modal markup**

Keep the existing artifact viewer if useful, but add this separate modal:

```html
<div id="comparison-modal" class="comparison-modal-backdrop" hidden>
  <div class="comparison-modal" role="dialog" aria-modal="true" aria-labelledby="comparison-modal-title">
    <div class="comparison-modal-header">
      <div>
        <span id="comparison-modal-meta"></span>
        <h2 id="comparison-modal-title">Evaluation Item</h2>
      </div>
      <button type="button" id="comparison-modal-close">Close</button>
    </div>
    <div id="comparison-modal-body" class="comparison-modal-body"></div>
  </div>
</div>
```

- [ ] **Step 3: Add CSS for the v2 table and modal**

Use stable dimensions and internal scrolling:

```css
.comparison-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.72);
  padding: 16px;
}

.comparison-modal-backdrop[hidden] {
  display: none;
}

.comparison-modal {
  width: min(95vw, 1600px);
  height: min(90vh, 1000px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.comparison-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
}

.comparison-modal-body {
  min-height: 0;
  flex: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
  padding: 16px;
}

.comparison-column {
  min-width: 0;
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
  background: #fff;
}

.evaluation-item-title {
  max-width: 42rem;
  white-space: normal;
}

.detail-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
  padding: 6px 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
  color: var(--text);
  cursor: pointer;
}

@media (max-width: 900px) {
  .comparison-modal {
    width: calc(100vw - 12px);
    height: calc(100vh - 12px);
  }

  .comparison-modal-body {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 4: Add v2 JavaScript renderers**

Replace old report-section render calls with these functions while keeping reusable helpers such as `escapeHtml`, `badge`, `renderMarkdownArtifact`, `renderCodeBlock`, and artifact viewer helpers:

```javascript
let activeTypeFilter = "";
let activeChangeFilter = "";
let activeSearch = "";
let lastModalTrigger = null;

const evaluationItems = () => REPORT_DATA.evaluation_items || [];

const renderReportSummary = () => {
  const summary = REPORT_DATA.summary || { sections: [], conclusion: "", risks: [] };
  const container = document.getElementById("summary-sections");
  container.innerHTML = (summary.sections || []).map((section) => `
    <div class="summary-card">
      <span>${escapeHtml(section.title || section.type)}</span>
      ${(section.metrics || []).map((metric) => `
        <strong>${escapeHtml(metric.label)}: ${escapeHtml(metric.value)}</strong>
      `).join("")}
    </div>
  `).join("");

  document.getElementById("summary-conclusion").innerHTML = `
    <p><strong>Conclusion:</strong> ${escapeHtml(summary.conclusion || "")}</p>
    ${(summary.risks || []).length ? `<ul>${summary.risks.map((risk) => `<li>${escapeHtml(risk)}</li>`).join("")}</ul>` : ""}
  `;
};

const optionButton = (kind, value, label, count) => `
  <button type="button" class="filter-button" data-filter-kind="${kind}" data-filter-value="${escapeHtml(value)}">
    ${escapeHtml(label)} <span>${escapeHtml(count)}</span>
  </button>
`;

const renderEvaluationFilters = () => {
  const items = evaluationItems();
  const typeCounts = Object.fromEntries(["", "numeric", "pass_fail", "hard_gate", "narrative"].map((type) => [
    type,
    type ? items.filter((item) => item.score_type === type).length : items.length,
  ]));
  const changeCounts = Object.fromEntries(["", "improved", "regressed", "unchanged", "mixed", "not_comparable"].map((direction) => [
    direction,
    direction ? items.filter((item) => (item.change || {}).direction === direction).length : items.length,
  ]));

  document.getElementById("evaluation-filters").innerHTML = `
    ${optionButton("type", "", "전체", typeCounts[""])}
    ${optionButton("type", "numeric", "정량", typeCounts.numeric)}
    ${optionButton("type", "pass_fail", "Pass/Fail", typeCounts.pass_fail)}
    ${optionButton("type", "hard_gate", "Hard Gate", typeCounts.hard_gate)}
    ${optionButton("type", "narrative", "서술형", typeCounts.narrative)}
    ${optionButton("change", "improved", "개선", changeCounts.improved)}
    ${optionButton("change", "regressed", "하락", changeCounts.regressed)}
    ${optionButton("change", "unchanged", "동일", changeCounts.unchanged)}
    <label class="visually-hidden" for="evaluation-search">Search evaluation items</label>
    <input id="evaluation-search" type="search" value="${escapeHtml(activeSearch)}" placeholder="Search evaluation item, summary, score">
  `;

  document.querySelectorAll("[data-filter-kind]").forEach((button) => {
    button.addEventListener("click", () => {
      const kind = button.dataset.filterKind;
      const value = button.dataset.filterValue || "";
      if (kind === "type") activeTypeFilter = value;
      if (kind === "change") activeChangeFilter = value;
      renderEvaluationItems();
      renderEvaluationFilters();
    });
  });

  document.getElementById("evaluation-search").addEventListener("input", (event) => {
    activeSearch = event.target.value.toLowerCase();
    renderEvaluationItems();
  });
};

const itemMatchesFilters = (item) => {
  const change = item.change || {};
  const baseline = item.baseline || {};
  const withDddjango = item.with_dddjango || {};
  const haystack = [
    item.title,
    item.test_content_ko,
    baseline.response_summary,
    baseline.evaluation_summary,
    baseline.score,
    withDddjango.response_summary,
    withDddjango.evaluation_summary,
    withDddjango.score,
  ].join(" ").toLowerCase();
  return (!activeTypeFilter || item.score_type === activeTypeFilter)
    && (!activeChangeFilter || change.direction === activeChangeFilter)
    && (!activeSearch || haystack.includes(activeSearch));
};

const renderVariantCell = (item, variantKey, label) => {
  const variant = item[variantKey] || {};
  return `
    <div>${escapeHtml(variant.response_summary || "")}</div>
    <button type="button" class="detail-button" data-item-id="${escapeHtml(item.id)}" data-variant="${escapeHtml(variantKey)}">
      상세 보기
    </button>
  `;
};

const renderEvaluationItems = () => {
  const rows = evaluationItems().filter(itemMatchesFilters);
  const tbody = document.querySelector("#evaluation-items-table tbody");
  tbody.innerHTML = rows.map((item) => `
    <tr data-item-id="${escapeHtml(item.id)}">
      <td class="evaluation-item-title">
        <strong>${escapeHtml(item.title)}</strong>
        <div>${escapeHtml(item.test_content_ko)}</div>
      </td>
      <td>${badge(item.score_type)}</td>
      <td>${escapeHtml((item.baseline || {}).score)}</td>
      <td>${escapeHtml((item.with_dddjango || {}).score)}</td>
      <td>${badge((item.change || {}).label || (item.change || {}).direction)}</td>
      <td>${renderVariantCell(item, "baseline", "Baseline")}</td>
      <td>${renderVariantCell(item, "with_dddjango", "With dddjango")}</td>
    </tr>
  `).join("");

  document.getElementById("evaluation-empty-state").hidden = rows.length !== 0;
  tbody.querySelectorAll(".detail-button").forEach((button) => {
    button.addEventListener("click", () => openComparisonModal(button.dataset.itemId, button));
  });
};

const renderComparisonColumn = (heading, variant) => `
  <section class="comparison-column">
    <h3>${escapeHtml(heading)}</h3>
    <p><strong>Score:</strong> ${escapeHtml(variant.score || "")}</p>
    <h4>평가 요약</h4>
    <p>${escapeHtml(variant.evaluation_summary || "")}</p>
    <h4>응답</h4>
    ${renderMarkdownArtifact(variant.response || "")}
    <h4>상세 평가</h4>
    ${renderMarkdownArtifact(variant.evaluation || "")}
    <h4>Evidence</h4>
    <div class="artifact-actions">${links(variant.evidence || [])}</div>
  </section>
`;

const openComparisonModal = (itemId, trigger) => {
  const item = evaluationItems().find((candidate) => candidate.id === itemId);
  if (!item) return;
  lastModalTrigger = trigger || document.activeElement;
  document.getElementById("comparison-modal-title").textContent = item.title;
  document.getElementById("comparison-modal-meta").textContent = `${item.score_type} | ${(item.change || {}).label || ""}`;
  document.getElementById("comparison-modal-body").innerHTML = `
    ${renderComparisonColumn("Baseline", item.baseline || {})}
    ${renderComparisonColumn("With dddjango", item.with_dddjango || {})}
  `;
  document.getElementById("comparison-modal").hidden = false;
  document.getElementById("comparison-modal-close").focus();
};

const closeComparisonModal = () => {
  document.getElementById("comparison-modal").hidden = true;
  document.getElementById("comparison-modal-body").innerHTML = "";
  if (lastModalTrigger && typeof lastModalTrigger.focus === "function") lastModalTrigger.focus();
};
```

- [ ] **Step 5: Wire modal close and startup**

Update the DOMContentLoaded/init area to call only v2 renderers plus artifact viewer helpers:

```javascript
document.getElementById("comparison-modal-close").addEventListener("click", closeComparisonModal);
document.getElementById("comparison-modal").addEventListener("click", (event) => {
  if (event.target.id === "comparison-modal") closeComparisonModal();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !document.getElementById("comparison-modal").hidden) {
    closeComparisonModal();
  }
});

renderReportSummary();
renderEvaluationFilters();
renderEvaluationItems();
attachArtifactViewer();
```

- [ ] **Step 6: Regenerate and validate**

Run:

```bash
python3 workspace/scripts/render_plugin_eval_report.py
python3 workspace/scripts/render_plugin_eval_report.py --run-id local-code-artifact-real --code-artifact-run
python3 workspace/scripts/validate_eval_report_readability.py --report workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html
python3 workspace/scripts/validate_eval_report_readability.py --report workspace/develop/evals/runs/local-code-artifact-real/report.html --require-code-artifacts
```

Expected: both validation commands pass and print `readability validation passed`.

- [ ] **Step 7: Commit template migration**

```bash
git add workspace/develop/evals/templates/run-report.html workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html workspace/develop/evals/runs/local-code-artifact-real/report.html
git commit -m "Render eval report v2 UI"
```

## Task 4: Browser Acceptance Check

**Files:**
- Read: `workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html`
- Read: `workspace/develop/evals/runs/local-code-artifact-real/report.html`

- [ ] **Step 1: Start a local static server**

Run from repo root:

```bash
python3 -m http.server 8787
```

Expected: server listens on `http://127.0.0.1:8787/`. If 8787 is already occupied, use the next free port and update the URLs in the next steps.

- [ ] **Step 2: Open the comprehensive report**

Open:

```text
http://127.0.0.1:8787/workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html
```

Verify:

- Top summary is visible before the table.
- `Evaluation Items` table is visible.
- The first row shows Korean test content in the first column.
- Type/change filters update the visible rows.
- Text search filters by Korean test content and summaries.

- [ ] **Step 3: Verify baseline detail modal**

Click the first row's baseline `상세 보기` button.

Expected:

- `#comparison-modal` opens.
- Modal title matches the row.
- Both `Baseline` and `With dddjango` columns are visible.
- Baseline response/evaluation and with-ddjango response/evaluation are both present.
- Long code or markdown content scrolls inside columns instead of expanding the page.
- Escape closes the modal and focus returns to the clicked button.

- [ ] **Step 4: Verify with-ddjango detail modal**

Click the first row's with-ddjango `상세 보기` button.

Expected:

- The same comparison modal opens.
- Both variants are visible.
- The modal can be closed with the close button.

- [ ] **Step 5: Repeat the modal smoke on the code-backed report**

Open:

```text
http://127.0.0.1:8787/workspace/develop/evals/runs/local-code-artifact-real/report.html
```

Verify:

- Summary and evaluation table render.
- The `case-101` row shows the Korean code request.
- Modal shows generated source/diff evidence links when available.

- [ ] **Step 6: Stop the local server**

Stop the `python3 -m http.server 8787` process with `Ctrl-C`.

## Task 5: Final Static Verification

**Files:**
- Read: `workspace/scripts/validate_eval_report_readability.py`
- Read: `workspace/scripts/render_plugin_eval_report.py`
- Read: `workspace/develop/evals/templates/run-report.html`
- Read: generated report files

- [ ] **Step 1: Re-run renderer and validator from a clean command sequence**

Run:

```bash
python3 workspace/scripts/render_plugin_eval_report.py
python3 workspace/scripts/render_plugin_eval_report.py --run-id local-code-artifact-real --code-artifact-run
python3 workspace/scripts/validate_eval_report_readability.py --report workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html
python3 workspace/scripts/validate_eval_report_readability.py --report workspace/develop/evals/runs/local-code-artifact-real/report.html --require-code-artifacts
```

Expected: both validation commands pass.

- [ ] **Step 2: Inspect final staged diff**

Run:

```bash
git diff --stat
git diff -- workspace/scripts/render_plugin_eval_report.py workspace/scripts/validate_eval_report_readability.py workspace/develop/evals/templates/run-report.html
```

Expected:

- Renderer contains v2 contract builders.
- Validator requires `schema_version: "eval-report-v2"`.
- Template contains `#report-summary`, `#evaluation-filters`, `#evaluation-items-table`, and `#comparison-modal`.
- Old case-story/table sections are not the primary rendered UI.

- [ ] **Step 3: Commit final verification artifacts when generated reports changed**

Check whether Task 5 changed the generated reports:

```bash
git diff --quiet -- workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html workspace/develop/evals/runs/local-code-artifact-real/report.html
echo $?
```

If the command prints `1`, commit those generated report changes:

```bash
git add workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html workspace/develop/evals/runs/local-code-artifact-real/report.html
git commit -m "Refresh eval report v2 artifacts"
```

If the command prints `0`, do not create a commit for this step.

## Integration Notes

- Preserve unrelated dirty worktree changes. Stage only files listed in each task.
- Do not edit plugin cache paths outside this repository for this feature.
- Do not claim browser or validation success unless the commands/checks in Tasks 3-5 were run in the current implementation session.
- Report Serena usage honestly. This plan does not require Serena because the intended changes are localized renderer/template/validator edits, but execution agents should re-check if they perform symbol renames or broad reference changes.

## Self-Review

- Spec coverage: The plan covers v2 schema, Korean test content, canonical variant keys, normalized score type, type-specific summary, filters, large comparison modal, accessibility behavior, validation rules, and browser acceptance checks.
- Placeholder scan: No task relies on unspecified future work.
- Type consistency: The plan consistently uses `schema_version`, `summary`, `evaluation_items`, `baseline`, `with_dddjango`, `score_type`, `score_type_source`, `source_granularity`, and `change.direction`.
