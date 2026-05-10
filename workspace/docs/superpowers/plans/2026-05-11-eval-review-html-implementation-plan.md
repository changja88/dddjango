# Eval Review HTML Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static evaluator-only HTML report that shows an eval run summary, a list of evaluation questions with baseline and with-dddjango scores, and a click-open side-by-side detail view.

**Architecture:** Add a focused renderer script instead of extending the existing response/code-specific report renderer. The renderer reads one bucket/run, shapes deterministic report data, then emits one self-contained `analysis/report.html` with inline CSS and small JavaScript for row selection.

**Tech Stack:** Python 3 standard library, `unittest`, static HTML/CSS/JavaScript, existing eval pack files under `workspace/develop/eval`.

---

## File Structure

- Create `workspace/scripts/render_eval_review_html.py`
  - Owns CLI parsing, eval artifact loading, summary shaping, sort order, and static HTML rendering.
  - Reads exactly one `--bucket` and one `--run-id`.
  - Writes to the bucket/run output pattern `workspace/develop/eval/{bucket}/runs/{run_id}/analysis/report.html`.
- Create `workspace/scripts/test_render_eval_review_html.py`
  - Unit tests for data shaping and HTML rendering with a temporary eval root.
  - Uses `importlib.util` to load the script, matching the existing script test style.
- Keep `workspace/scripts/render_plugin_eval_report.py` unchanged.
  - It remains the older response/code artifact viewer and should not become the new all-bucket review UI.

## Data Contract

The renderer produces this in-memory object and embeds it as `const REPORT_DATA = ...`:

```json
{
  "bucket": "response",
  "run_id": "sample-run",
  "generated_at": "2026-05-11 01:50 KST",
  "reportability": "reportable-with-warnings",
  "summary": {
    "total_cases": 1,
    "pass": 1,
    "partial": 0,
    "fail": 0,
    "blocked": 0,
    "unscored": 0,
    "baseline_average": "2.0",
    "with_dddjango_average": "5.0",
    "delta": "+3.0",
    "hard_gate_failures": 0,
    "missing_or_weak_evidence": 0
  },
  "cases": [
    {
      "id": "case-response-order-create",
      "bucket": "response",
      "question": "Django Ninja 주문 생성 API를 설계하고 구현 방향을 제시하라.",
      "status": "pass",
      "detail_status": "ready",
      "hard_gate": "ok",
      "delta": "+3.0",
      "baseline": {
        "score": "2 / 5",
        "score_value": 2.0,
        "verdict": "fail",
        "response": "Baseline response text",
        "evaluation": "Baseline evaluation text",
        "evidence": ["raw/case-response-order-create-baseline.txt"]
      },
      "with_dddjango": {
        "score": "5 / 5",
        "score_value": 5.0,
        "verdict": "pass",
        "response": "With dddjango response text",
        "evaluation": "With dddjango evaluation text",
        "evidence": ["raw/case-response-order-create-with-dddjango.txt"]
      },
      "evaluator_only": {
        "intent": "Validate specialist-positive reasoning.",
        "failed_checks": [],
        "leakage_notes": [],
        "evidence": ["raw/case-response-order-create-answer-oracle-evaluation.json"]
      }
    }
  ]
}
```

Missing raw outputs or missing answer-oracle evaluation must create `unscored` or `blocked` states. The renderer must never infer a passing score from missing artifacts.

## Task 1: Add Data Shaping Tests First

**Files:**
- Create: `workspace/scripts/test_render_eval_review_html.py`
- Create in Task 2: `workspace/scripts/render_eval_review_html.py`

- [ ] **Step 1: Write failing tests for a complete scored case and a missing-artifact case**

Create `workspace/scripts/test_render_eval_review_html.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("render_eval_review_html.py")


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_eval_review_html", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvalReviewHtmlRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = load_renderer()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.renderer.REPO_ROOT = self.root
        self.renderer.EVAL_ROOT = self.root / "workspace/develop/eval"

    def write_case(
        self,
        *,
        bucket: str = "response",
        case_id: str = "case-response-order-create",
        public_text: str = "Django Ninja 주문 생성 API를 설계하고 구현 방향을 제시하라.\n",
        baseline_response: str | None = "Baseline response text",
        with_response: str | None = "With dddjango response text",
        oracle: dict[str, object] | None = None,
    ) -> Path:
        bucket_root = self.renderer.EVAL_ROOT / bucket
        public_path = bucket_root / "cases/plugin/public" / f"{case_id}.md"
        answer_path = bucket_root / "answer" / f"{case_id}.yaml"
        raw_dir = bucket_root / "runs/sample-run/raw"
        public_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        raw_dir.mkdir(parents=True, exist_ok=True)
        public_path.write_text(public_text, encoding="utf-8")
        answer_path.write_text(
            f"""id: {case_id}
case_id: {case_id}
bucket: {bucket}
kind: {bucket}
public_case: workspace/develop/eval/{bucket}/cases/plugin/public/{case_id}.md
intent: Validate specialist-positive reasoning.
reference_basis:
  - path: workspace/develop/eval/{bucket}/eval_goal.md
    basis: test basis
target_behavior:
  required:
    - Required behavior.
scoring_checks:
  - pass if checked.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
coverage_tags:
  - specialist-positive
""",
            encoding="utf-8",
        )
        if baseline_response is not None:
            (raw_dir / f"{case_id}-baseline.txt").write_text(baseline_response, encoding="utf-8")
        if with_response is not None:
            (raw_dir / f"{case_id}-with-dddjango.txt").write_text(with_response, encoding="utf-8")
        if oracle is None:
            oracle = {
                "caseId": case_id,
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "2 / 5",
                    "verdict": "fail",
                    "evaluation_summary": "Missing dddjango-specific API and idempotency guidance.",
                    "evaluation": "Baseline evaluation text",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "Meets DDD, API, DB, and test expectations.",
                    "evaluation": "With dddjango evaluation text",
                },
                "observations": ["with-dddjango improves the response"],
            }
        (raw_dir / f"{case_id}-answer-oracle-evaluation.json").write_text(
            json.dumps(oracle, ensure_ascii=False),
            encoding="utf-8",
        )
        return bucket_root / "runs/sample-run"

    def test_build_report_data_includes_summary_rows_and_detail(self) -> None:
        run_dir = self.write_case()

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        self.assertEqual(data["summary"]["total_cases"], 1)
        self.assertEqual(data["summary"]["baseline_average"], "2.0")
        self.assertEqual(data["summary"]["with_dddjango_average"], "5.0")
        self.assertEqual(data["summary"]["delta"], "+3.0")
        row = data["cases"][0]
        self.assertEqual(row["question"], "Django Ninja 주문 생성 API를 설계하고 구현 방향을 제시하라.")
        self.assertEqual(row["baseline"]["score"], "2 / 5")
        self.assertEqual(row["with_dddjango"]["score"], "5 / 5")
        self.assertEqual(row["baseline"]["response"], "Baseline response text")
        self.assertEqual(row["with_dddjango"]["evaluation"], "With dddjango evaluation text")

    def test_missing_artifacts_are_unscored_not_pass(self) -> None:
        run_dir = self.write_case(baseline_response=None, oracle={})

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["baseline"]["verdict"], "unscored")
        self.assertEqual(row["baseline"]["score"], "not scored")
        self.assertIn(row["status"], {"blocked", "unscored"})
        self.assertGreaterEqual(data["summary"]["missing_or_weak_evidence"], 1)

    def test_render_html_contains_required_review_surfaces(self) -> None:
        run_dir = self.write_case()
        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertIn("평가 요약", html)
        self.assertIn("평가 질문", html)
        self.assertIn("baseline 점수", html)
        self.assertIn("with-dddjango 점수", html)
        self.assertIn("Baseline", html)
        self.assertIn("with-dddjango", html)
        self.assertIn("const REPORT_DATA =", html)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify they fail because the renderer does not exist**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/dddjango-pycache python3 -m unittest workspace/scripts/test_render_eval_review_html.py
```

Expected:

```text
FileNotFoundError: [Errno 2] No such file or directory: '.../workspace/scripts/render_eval_review_html.py'
```

Do not change the tests to make this pass.

## Task 2: Implement Renderer Data Loading

**Files:**
- Create: `workspace/scripts/render_eval_review_html.py`
- Test: `workspace/scripts/test_render_eval_review_html.py`

- [ ] **Step 1: Create the renderer skeleton and helper functions**

Create `workspace/scripts/render_eval_review_html.py` with these definitions:

```python
#!/usr/bin/env python3
"""Render a static evaluator-only HTML review page for one eval bucket run."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "workspace/develop/eval"
BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
VARIANTS = ("baseline", "with-dddjango")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", required=True, choices=BUCKETS)
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path. Defaults to workspace/develop/eval/{bucket}/runs/{run_id}/analysis/report.html.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def block_lines(text: str, key: str) -> list[str]:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if re.match(rf"^\s*{re.escape(key)}\s*:", line):
            start = index + 1
            break
    if start is None:
        return []
    result: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith(" "):
            break
        if line.strip():
            result.append(line)
    return result


def yaml_list_values(text: str, key: str) -> list[str]:
    values: list[str] = []
    for line in block_lines(text, key):
        match = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if match:
            values.append(match.group(1).strip().strip("'\""))
    return [value for value in values if value]


def scalar_value(text: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", text)
    return match.group(1).strip().strip("'\"") if match else ""


def extract_question(public_text: str) -> str:
    request_section = re.search(r"## (?:User )?Requests?\s*(.*?)(?:\n## |\Z)", public_text, re.S)
    if request_section:
        section_text = request_section.group(1).strip()
        fenced = [
            item.strip()
            for item in re.findall(r"```text\s*(.*?)\s*```", section_text, re.S)
            if item.strip()
        ]
        if len(fenced) == 1:
            return fenced[0]
        if fenced:
            return "\n\n".join(f"{index}. {item}" for index, item in enumerate(fenced, start=1))
        return section_text
    return public_text.strip()


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}
```

- [ ] **Step 2: Add score and variant shaping functions**

Append:

```python
def score_value(score: object, verdict: object = "") -> float | None:
    text = str(score or "").strip().lower()
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*/\s*5", text)
    if match:
        return float(match.group(1))
    if text in {"5", "4", "3", "2", "1", "0"}:
        return float(text)
    verdict_text = str(verdict or "").strip().lower()
    if verdict_text == "pass":
        return 5.0
    if verdict_text in {"partial", "pass-limited", "pass-control"}:
        return 3.0
    if verdict_text in {"fail", "blocked"}:
        return 0.0
    return None


def format_average(values: list[float]) -> str:
    if not values:
        return "n/a"
    return f"{sum(values) / len(values):.1f}"


def format_delta(before: float | None, after: float | None) -> str:
    if before is None or after is None:
        return "n/a"
    value = after - before
    return f"{value:+.1f}"


def normalize_verdict(verdict: object, *, has_response: bool, has_evaluation: bool) -> str:
    text = str(verdict or "").strip().lower()
    if not has_response or not has_evaluation:
        return "unscored"
    if text in {"pass", "partial", "fail", "blocked", "pass-limited", "pass-control"}:
        return text
    return "unscored"


def variant_data(
    *,
    run_dir: Path,
    case_id: str,
    variant: str,
    oracle: dict[str, object],
) -> dict[str, object]:
    raw_name = f"{case_id}-{variant}.txt"
    raw_path = run_dir / "raw" / raw_name
    response = read_text(raw_path).strip()
    oracle_key = "with_dddjango" if variant == "with-dddjango" else "baseline"
    oracle_variant = oracle.get(oracle_key)
    oracle_variant = oracle_variant if isinstance(oracle_variant, dict) else {}
    evaluation = str(
        oracle_variant.get("evaluation")
        or oracle_variant.get("evaluation_summary")
        or ""
    ).strip()
    verdict = normalize_verdict(
        oracle_variant.get("verdict"),
        has_response=bool(response),
        has_evaluation=bool(evaluation),
    )
    score_text = str(oracle_variant.get("score") or "").strip()
    numeric_score = score_value(score_text, verdict)
    if numeric_score is None:
        score_text = "not scored"
    elif not score_text:
        score_text = f"{numeric_score:g} / 5"
    return {
        "score": score_text,
        "score_value": numeric_score,
        "verdict": verdict,
        "response": response or f"Missing artifact: raw/{raw_name}",
        "evaluation": evaluation or "Missing answer-oracle evaluation for this variant.",
        "evidence": [f"raw/{raw_name}"],
    }
```

- [ ] **Step 3: Add case and summary shaping functions**

Append:

```python
def case_status(case: dict[str, object]) -> str:
    hard_gate = str(case.get("hard_gate") or "")
    if hard_gate != "ok":
        return "blocked"
    verdicts = {
        str(case["baseline"]["verdict"]),
        str(case["with_dddjango"]["verdict"]),
    }
    if "unscored" in verdicts:
        return "unscored"
    if "blocked" in verdicts:
        return "blocked"
    if "fail" in verdicts:
        return "fail"
    if verdicts & {"partial", "pass-limited", "pass-control"}:
        return "partial"
    return "pass"


def hard_gate_from_oracle(oracle: dict[str, object]) -> str:
    observations = oracle.get("observations")
    observation_text = " ".join(str(item) for item in observations) if isinstance(observations, list) else ""
    status_text = str(oracle.get("status") or "")
    combined = f"{status_text} {observation_text}".lower()
    if "leak" in combined and "fail" in combined:
        return "leakage fail"
    if "hard" in combined and "fail" in combined:
        return "hard fail"
    return "ok"


def build_case(bucket: str, public_case: Path, run_dir: Path) -> dict[str, object]:
    case_id = public_case.stem
    bucket_root = EVAL_ROOT / bucket
    answer_path = bucket_root / "answer" / f"{case_id}.yaml"
    answer_text = read_text(answer_path)
    oracle_path = run_dir / "raw" / f"{case_id}-answer-oracle-evaluation.json"
    oracle = load_json(oracle_path)
    baseline = variant_data(run_dir=run_dir, case_id=case_id, variant="baseline", oracle=oracle)
    with_dddjango = variant_data(run_dir=run_dir, case_id=case_id, variant="with-dddjango", oracle=oracle)
    delta = format_delta(
        baseline["score_value"] if isinstance(baseline["score_value"], float) else None,
        with_dddjango["score_value"] if isinstance(with_dddjango["score_value"], float) else None,
    )
    case = {
        "id": case_id,
        "bucket": bucket,
        "question": extract_question(read_text(public_case)),
        "status": "unscored",
        "detail_status": "ready" if oracle else "missing oracle evaluation",
        "hard_gate": hard_gate_from_oracle(oracle),
        "delta": delta,
        "baseline": baseline,
        "with_dddjango": with_dddjango,
        "evaluator_only": {
            "intent": scalar_value(answer_text, "intent") or "Not recorded.",
            "failed_checks": yaml_list_values(answer_text, "failure_modes"),
            "leakage_notes": yaml_list_values(answer_text, "leakage_checks"),
            "evidence": [f"raw/{oracle_path.name}"],
        },
    }
    case["status"] = case_status(case)
    return case


def sort_key(case: dict[str, object]) -> tuple[int, float, str]:
    status_rank = {
        "blocked": 0,
        "fail": 1,
        "partial": 2,
        "unscored": 3,
        "pass": 4,
    }.get(str(case.get("status")), 5)
    delta = str(case.get("delta") or "n/a")
    delta_value = 0.0 if delta == "n/a" else abs(float(delta))
    return (status_rank, -delta_value, str(case.get("id")))


def build_summary(cases: list[dict[str, object]]) -> dict[str, object]:
    baseline_scores = [
        float(case["baseline"]["score_value"])
        for case in cases
        if isinstance(case["baseline"]["score_value"], float)
    ]
    with_scores = [
        float(case["with_dddjango"]["score_value"])
        for case in cases
        if isinstance(case["with_dddjango"]["score_value"], float)
    ]
    baseline_average = format_average(baseline_scores)
    with_average = format_average(with_scores)
    delta = "n/a"
    if baseline_scores and with_scores:
        delta = f"{float(with_average) - float(baseline_average):+.1f}"
    return {
        "total_cases": len(cases),
        "pass": sum(1 for case in cases if case["status"] == "pass"),
        "partial": sum(1 for case in cases if case["status"] == "partial"),
        "fail": sum(1 for case in cases if case["status"] == "fail"),
        "blocked": sum(1 for case in cases if case["status"] == "blocked"),
        "unscored": sum(1 for case in cases if case["status"] == "unscored"),
        "baseline_average": baseline_average,
        "with_dddjango_average": with_average,
        "delta": delta,
        "hard_gate_failures": sum(1 for case in cases if case["hard_gate"] != "ok"),
        "missing_or_weak_evidence": sum(1 for case in cases if case["status"] in {"blocked", "unscored"}),
    }
```

- [ ] **Step 4: Add top-level `build_report_data`**

Append:

```python
def reportability(summary: dict[str, object]) -> str:
    if int(summary["hard_gate_failures"]) > 0:
        return "blocked"
    if int(summary["missing_or_weak_evidence"]) > 0:
        return "reportable-with-warnings"
    return "reportable"


def build_report_data(bucket: str, run_id: str, run_dir: Path) -> dict[str, object]:
    public_dir = EVAL_ROOT / bucket / "cases/plugin/public"
    cases = [build_case(bucket, path, run_dir) for path in sorted(public_dir.glob("case-*.md"))]
    cases.sort(key=sort_key)
    summary = build_summary(cases)
    return {
        "bucket": bucket,
        "run_id": run_id,
        "generated_at": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M KST"),
        "reportability": reportability(summary),
        "summary": summary,
        "cases": cases,
    }
```

- [ ] **Step 5: Run tests and verify Task 1 data tests pass or expose implementation bugs**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/dddjango-pycache python3 -m unittest workspace/scripts/test_render_eval_review_html.py
```

Expected at this stage:

```text
FAILED ... AttributeError: module 'render_eval_review_html' has no attribute 'render_html'
```

The first two tests should pass; the HTML test should fail until Task 3.

## Task 3: Implement Static HTML Rendering and CLI

**Files:**
- Modify: `workspace/scripts/render_eval_review_html.py`
- Test: `workspace/scripts/test_render_eval_review_html.py`

- [ ] **Step 1: Add CSS class and status helpers**

Append:

```python
def status_class(value: object) -> str:
    text = str(value or "").lower()
    if text in {"pass", "reportable"}:
        return "good"
    if text in {"partial", "unscored", "reportable-with-warnings", "pass-limited", "pass-control"}:
        return "warn"
    if text in {"fail", "blocked"} or "fail" in text:
        return "bad"
    return "muted"


def js_json(data: dict[str, object]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
```

- [ ] **Step 2: Add `render_html`**

Append:

```python
def render_html(data: dict[str, object]) -> str:
    encoded = js_json(data)
    cases = data["cases"]
    rows = []
    for index, case in enumerate(cases):
        rows.append(
            "<tr "
            f"data-index=\"{index}\" onclick=\"selectCase({index})\""
            f" class=\"case-row {'selected' if index == 0 else ''}\">"
            f"<td>{escape(str(case['question']))}</td>"
            f"<td>{escape(str(case['bucket']))}</td>"
            f"<td><span class=\"pill {status_class(case['baseline']['verdict'])}\">{escape(str(case['baseline']['score']))}</span></td>"
            f"<td><span class=\"pill {status_class(case['with_dddjango']['verdict'])}\">{escape(str(case['with_dddjango']['score']))}</span></td>"
            f"<td>{escape(str(case['delta']))}</td>"
            f"<td><span class=\"pill {status_class(case['status'])}\">{escape(str(case['status']))}</span></td>"
            "<td><button type=\"button\">상세</button></td>"
            "</tr>"
        )
    rows_html = "\n".join(rows)
    summary = data["summary"]
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>dddjango Eval Review - {escape(str(data['bucket']))}/{escape(str(data['run_id']))}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0f172a;
      --panel: #111827;
      --panel-2: #1e293b;
      --line: #334155;
      --text: #e5e7eb;
      --muted: #94a3b8;
      --good: #86efac;
      --warn: #fde68a;
      --bad: #fecaca;
      --blue: #93c5fd;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    main {{ width: min(1500px, calc(100vw - 32px)); margin: 24px auto 48px; }}
    header {{ display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 16px; }}
    h1, h2, h3 {{ margin: 0; letter-spacing: 0; }}
    .muted {{ color: var(--muted); }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metric, .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }}
    .metric {{ padding: 12px; min-height: 82px; }}
    .metric span {{ display: block; color: var(--muted); font-size: 12px; }}
    .metric strong {{ display: block; margin-top: 5px; font-size: 23px; }}
    .panel {{ padding: 14px; margin-top: 14px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; table-layout: fixed; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 600; }}
    tr.case-row {{ cursor: pointer; }}
    tr.case-row:hover, tr.selected {{ background: #1d2a3d; }}
    button {{ background: transparent; color: var(--blue); border: 1px solid #2563eb; border-radius: 5px; padding: 4px 8px; cursor: pointer; }}
    .pill {{ display: inline-flex; border-radius: 999px; padding: 3px 8px; border: 1px solid var(--line); white-space: nowrap; }}
    .good {{ color: var(--good); border-color: #14532d; background: #052e16; }}
    .warn {{ color: var(--warn); border-color: #713f12; background: #422006; }}
    .bad {{ color: var(--bad); border-color: #7f1d1d; background: #450a0a; }}
    .detail-question {{ border-bottom: 1px solid var(--line); padding-bottom: 12px; margin-bottom: 12px; }}
    .comparison {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .variant {{ background: var(--panel-2); border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 0; }}
    .variant-head {{ display: flex; justify-content: space-between; gap: 10px; align-items: center; margin-bottom: 10px; }}
    .label {{ color: var(--muted); font-size: 12px; margin-top: 12px; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #0b1120; border: 1px solid var(--line); border-radius: 6px; padding: 10px; max-height: 420px; overflow: auto; }}
    details {{ margin-top: 12px; color: var(--muted); }}
    @media (max-width: 980px) {{
      .summary-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .comparison {{ grid-template-columns: 1fr; }}
      table {{ table-layout: auto; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>dddjango Eval Review</h1>
      <div class="muted">bucket {escape(str(data['bucket']))} · run {escape(str(data['run_id']))} · {escape(str(data['generated_at']))}</div>
    </div>
    <span class="pill {status_class(data['reportability'])}">{escape(str(data['reportability']))}</span>
  </header>

  <section class="panel" aria-label="평가 요약">
    <h2>평가 요약</h2>
    <div class="summary-grid">
      <div class="metric"><span>Total</span><strong>{summary['total_cases']}</strong></div>
      <div class="metric"><span>Pass / Partial / Fail</span><strong>{summary['pass']} / {summary['partial']} / {summary['fail']}</strong></div>
      <div class="metric"><span>Baseline Avg</span><strong>{escape(str(summary['baseline_average']))}</strong></div>
      <div class="metric"><span>with-dddjango Avg</span><strong>{escape(str(summary['with_dddjango_average']))}</strong></div>
      <div class="metric"><span>Delta</span><strong>{escape(str(summary['delta']))}</strong></div>
      <div class="metric"><span>Hard Gates</span><strong>{summary['hard_gate_failures']}</strong></div>
    </div>
    <div class="muted">Missing or weak evidence: {summary['missing_or_weak_evidence']} · Blocked: {summary['blocked']} · Unscored: {summary['unscored']}</div>
  </section>

  <section class="panel" aria-label="평가 질문 리스트">
    <h2>평가 질문 리스트</h2>
    <table>
      <thead>
        <tr>
          <th>평가 질문</th>
          <th>bucket</th>
          <th>baseline 점수</th>
          <th>with-dddjango 점수</th>
          <th>delta</th>
          <th>status</th>
          <th>상세</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </section>

  <section class="panel" aria-label="상세" id="detail"></section>
</main>
<script>
const REPORT_DATA = {encoded};

function text(value) {{
  return value === null || value === undefined ? "" : String(value);
}}

function escapeHtml(value) {{
  return text(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}}

function statusClass(value) {{
  const textValue = text(value).toLowerCase();
  if (["pass", "reportable"].includes(textValue)) return "good";
  if (["partial", "unscored", "reportable-with-warnings", "pass-limited", "pass-control"].includes(textValue)) return "warn";
  if (["fail", "blocked"].includes(textValue) || textValue.includes("fail")) return "bad";
  return "muted";
}}

function variantHtml(title, variant) {{
  return `
    <div class="variant">
      <div class="variant-head">
        <h3>${{escapeHtml(title)}}</h3>
        <span class="pill ${{statusClass(variant.verdict)}}">${{escapeHtml(variant.score)}} · ${{escapeHtml(variant.verdict)}}</span>
      </div>
      <div class="label">응답</div>
      <pre>${{escapeHtml(variant.response)}}</pre>
      <div class="label">평가</div>
      <pre>${{escapeHtml(variant.evaluation)}}</pre>
    </div>
  `;
}}

function selectCase(index) {{
  const item = REPORT_DATA.cases[index];
  document.querySelectorAll(".case-row").forEach((row) => row.classList.remove("selected"));
  const row = document.querySelector(`[data-index="${{index}}"]`);
  if (row) row.classList.add("selected");
  document.getElementById("detail").innerHTML = `
    <div class="detail-question">
      <h2>문제</h2>
      <p>${{escapeHtml(item.question)}}</p>
      <div class="muted">case ${{escapeHtml(item.id)}} · hard gate ${{escapeHtml(item.hard_gate)}} · detail ${{escapeHtml(item.detail_status)}}</div>
    </div>
    <div class="comparison">
      ${{variantHtml("Baseline", item.baseline)}}
      ${{variantHtml("with-dddjango", item.with_dddjango)}}
    </div>
    <details>
      <summary>evaluator-only evidence</summary>
      <pre>${{escapeHtml(JSON.stringify(item.evaluator_only, null, 2))}}</pre>
    </details>
  `;
}}

if (REPORT_DATA.cases.length) {{
  selectCase(0);
}}
</script>
</body>
</html>
"""
```

- [ ] **Step 3: Add CLI `main`**

Append:

```python
def main() -> int:
    args = parse_args()
    run_dir = EVAL_ROOT / args.bucket / "runs" / args.run_id
    output = args.output or run_dir / "analysis/report.html"
    data = build_report_data(args.bucket, args.run_id, run_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(data), encoding="utf-8")
    print(f"wrote {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests and verify all renderer tests pass**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/dddjango-pycache python3 -m unittest workspace/scripts/test_render_eval_review_html.py
```

Expected:

```text
Ran 3 tests
OK
```

- [ ] **Step 5: Commit renderer implementation**

Run:

```bash
git add workspace/scripts/render_eval_review_html.py workspace/scripts/test_render_eval_review_html.py
git commit -m "Add eval review HTML renderer"
```

Expected: commit succeeds with only the renderer and test files staged.

## Task 4: Verify Against Existing Eval Pack and a Synthetic Run

**Files:**
- Modify only if verification exposes a bug:
  - `workspace/scripts/render_eval_review_html.py`
  - `workspace/scripts/test_render_eval_review_html.py`

- [ ] **Step 1: Run existing eval pack validator**

Run:

```bash
python3 workspace/scripts/validate_eval_bucket_pack.py
```

Expected:

```text
eval bucket pack validation passed: response=9, code=8, plugin=7, runtime=7, source=7, workflow=9
```

- [ ] **Step 2: Run Python compile check**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/dddjango-pycache python3 -m py_compile workspace/scripts/render_eval_review_html.py workspace/scripts/test_render_eval_review_html.py
```

Expected: no output and exit code 0.

- [ ] **Step 3: Create a synthetic run through the unit test fixture only**

Do not commit synthetic run output. Use the unit tests as the synthetic run source. The test already creates a temporary eval tree and exercises `build_report_data` and `render_html`, so no `workspace/develop/eval/*/runs` files are needed for this step.

- [ ] **Step 4: Run whitespace check**

Run:

```bash
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 5: Remove development-only caches**

Run:

```bash
find workspace -name __pycache__ -o -name .DS_Store
```

Expected: no output. If output appears, remove only generated cache files that were created by this task.

- [ ] **Step 6: Commit verification fixes if any**

If Task 4 required code changes, run:

```bash
git add workspace/scripts/render_eval_review_html.py workspace/scripts/test_render_eval_review_html.py
git commit -m "Tighten eval review HTML verification"
```

Expected: commit succeeds. If no changes were needed, do not create an empty commit.

## Task 5: Manual Browser Check

**Files:**
- No committed files unless defects are found.

- [ ] **Step 1: Render a real report only when a real run id exists**

Check for run ids:

```bash
find workspace/develop/eval/response/runs -mindepth 1 -maxdepth 1 -type d -print
```

If there is no run directory beyond `.gitignore`, skip this step and report that no real run exists yet.

If a real run id exists, render the first discovered response run with this exact shell sequence:

```bash
RUN_ID="$(find workspace/develop/eval/response/runs -mindepth 1 -maxdepth 1 -type d | sed 's#.*/##' | head -n 1)"
python3 workspace/scripts/render_eval_review_html.py --bucket response --run-id "$RUN_ID"
```

Expected:

```text
wrote workspace/develop/eval/response/runs/$RUN_ID/analysis/report.html
```

- [ ] **Step 2: Open the HTML manually**

If a report was rendered, open it from:

```text
workspace/develop/eval/response/runs/$RUN_ID/analysis/report.html
```

Confirm these visible surfaces:

- top summary appears first
- list has `평가 질문`, `baseline 점수`, `with-dddjango 점수`, and `상세`
- selecting a row shows `문제` above the detail
- detail center is split into baseline and with-dddjango columns
- each column shows score, response, and evaluation

- [ ] **Step 3: Do not commit run output**

Unless the user explicitly asks to preserve the generated report, leave generated `runs/{run_id}/analysis/report.html` files untracked. The user's standing rule is that development-only generated artifacts should not be committed.

## Final Verification Checklist

Run these commands before reporting completion:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/dddjango-pycache python3 -m unittest workspace/scripts/test_render_eval_review_html.py
python3 workspace/scripts/validate_eval_bucket_pack.py
PYTHONPYCACHEPREFIX=/private/tmp/dddjango-pycache python3 -m py_compile workspace/scripts/render_eval_review_html.py workspace/scripts/test_render_eval_review_html.py
git diff --check
git status --short
```

Expected:

- renderer tests pass
- eval bucket pack validation passes
- py_compile has no output
- `git diff --check` has no output
- `git status --short` is clean after committed source changes and after deleting development-only generated files
