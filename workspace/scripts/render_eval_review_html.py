#!/usr/bin/env python3
"""Load and shape eval review data for the HTML renderer."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from eval_run_common import validate_oracle_schema


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "workspace/develop/eval"
BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
VARIANTS = ("baseline", "with-dddjango")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", choices=BUCKETS, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def block_lines(text: str, key: str) -> list[str]:
    match = re.search(rf"(?m)^(?P<indent>\s*){re.escape(key)}\s*:\s*(?:#.*)?\n", text)
    if not match:
        return []
    base_indent = len(match.group("indent"))
    lines: list[str] = []
    for line in text[match.end() :].splitlines():
        if line.strip() and len(line) - len(line.lstrip()) <= base_indent:
            break
        lines.append(line.strip())
    return [line for line in lines if line]


def yaml_list_values(text: str, key: str) -> list[str]:
    values: list[str] = []
    for line in block_lines(text, key):
        item = re.match(r"^-\s+(.+?)\s*$", line)
        if item:
            values.append(item.group(1).strip().strip("'\""))
    return [value for value in values if value]


def scalar_value(text: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*(.*?)\s*(?:#.*)?$", text)
    if not match:
        return ""
    return match.group(1).strip().strip("'\"")


def extract_question(public_text: str) -> str:
    section = re.search(r"(?ms)^## (?:User Request|Requests)\s*(.*?)(?=^## |\Z)", public_text)
    if not section:
        return public_text.strip()

    section_text = section.group(1).strip()
    fenced_blocks = [
        item.strip()
        for item in re.findall(r"```text\s*(.*?)\s*```", section_text, re.S)
        if item.strip()
    ]
    if len(fenced_blocks) == 1:
        return fenced_blocks[0]
    if fenced_blocks:
        return "\n\n".join(
            f"{index}. {request_text}" for index, request_text in enumerate(fenced_blocks, start=1)
        )
    return section_text


def load_json(path: Path) -> tuple[dict[str, object], str]:
    if not path.exists():
        return {}, "missing"
    try:
        value = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return {}, "invalid_json"
    if not isinstance(value, dict):
        return {}, "invalid_schema"
    return value, "ready"


def score_value(score: object, verdict: str = "") -> float | None:
    score_text = str(score or "").strip()
    ratio = re.search(r"(?P<value>[0-5](?:\.\d+)?)\s*/\s*5\b", score_text)
    if ratio:
        value = float(ratio.group("value"))
        return value if 0.0 <= value <= 5.0 else None
    scalar = re.fullmatch(r"[0-5](?:\.\d+)?", score_text)
    if scalar:
        value = float(score_text)
        return value if 0.0 <= value <= 5.0 else None

    normalized_verdict = verdict.strip().lower()
    if normalized_verdict == "pass":
        return 5.0
    if normalized_verdict in {"partial", "pass-limited", "pass-control"}:
        return 3.0
    if normalized_verdict in {"fail", "blocked"}:
        return 0.0
    return None


def format_average(values: list[float]) -> str:
    if not values:
        return "n/a"
    return f"{sum(values) / len(values):.1f}"


def format_signed_average(values: list[float]) -> str:
    if not values:
        return "n/a"
    return f"{sum(values) / len(values):+.1f}"


def format_delta(before: float | None, after: float | None) -> str:
    if before is None or after is None:
        return "n/a"
    return f"{after - before:+.1f}"


def normalize_verdict(verdict: object, has_response: bool, has_evaluation: bool) -> str:
    if not has_response or not has_evaluation:
        return "unscored"
    normalized = str(verdict or "").strip().lower()
    if normalized in {"pass", "partial", "fail", "blocked", "pass-limited", "pass-control"}:
        return normalized
    return "unscored"


def variant_data(run_dir: Path, case_id: str, variant: str, oracle: dict[str, object]) -> dict[str, object]:
    raw_name = f"{case_id}-{variant}.txt"
    raw_path = run_dir / "raw" / raw_name
    response = read_text(raw_path)
    variant_key = "with_dddjango" if variant == "with-dddjango" else "baseline"
    variant_oracle = oracle.get(variant_key)
    if not isinstance(variant_oracle, dict):
        variant_oracle = {}

    raw_score = variant_oracle.get("score")
    raw_verdict = str(variant_oracle.get("verdict") or "")
    evaluation = str(
        variant_oracle.get("evaluation") or variant_oracle.get("evaluation_summary") or ""
    ).strip()

    has_response = bool(response.strip())
    has_evaluation = bool(evaluation)
    verdict = normalize_verdict(raw_verdict, has_response, has_evaluation)
    score = str(raw_score).strip() if raw_score is not None and str(raw_score).strip() else "not scored"
    if not has_response:
        response = f"Missing artifact: raw/{raw_name}"
    if not has_evaluation:
        evaluation = "Missing answer-oracle evaluation for this variant."
    if verdict == "unscored":
        score = "not scored"
    parsed_score = score_value(raw_score, verdict) if verdict != "unscored" else None

    return {
        "score": score,
        "score_value": parsed_score,
        "verdict": verdict,
        "response": response,
        "evaluation": evaluation,
        "evidence": [f"raw/{raw_name}"],
    }


def hard_gate_from_oracle(oracle: dict[str, object]) -> str:
    status_text = str(oracle.get("status") or "")
    observations = oracle.get("observations")
    if isinstance(observations, list):
        status_text = " ".join([status_text, *[str(item) for item in observations]])
    else:
        status_text = " ".join([status_text, str(observations or "")])
    status_text = status_text.lower()
    if "leak" in status_text and "fail" in status_text:
        return "leakage fail"
    if "hard" in status_text and "fail" in status_text:
        return "hard fail"
    return "ok"


def case_status(case: dict[str, object]) -> str:
    if case.get("hard_gate") != "ok":
        return "blocked"
    verdicts = [
        str(case[key]["verdict"])
        for key in ("baseline", "with_dddjango")
        if isinstance(case.get(key), dict)
    ]
    if any(verdict == "unscored" for verdict in verdicts):
        return "unscored"
    if any(verdict == "blocked" for verdict in verdicts):
        return "blocked"
    if any(verdict == "fail" for verdict in verdicts):
        return "fail"
    if any(verdict in {"partial", "pass-limited", "pass-control"} for verdict in verdicts):
        return "partial"
    return "pass"


def build_case(bucket: str, public_case: Path, run_dir: Path) -> dict[str, object]:
    case_id = public_case.stem
    answer_text = read_text(EVAL_ROOT / bucket / "answer" / f"{case_id}.yaml")
    oracle, oracle_state = load_json(run_dir / "raw" / f"{case_id}-answer-oracle-evaluation.json")
    if oracle_state == "ready" and validate_oracle_schema(oracle, case_id) is not None:
        oracle_state = "invalid_schema"
    reportable_oracle = oracle if oracle_state == "ready" else {}
    baseline = variant_data(run_dir, case_id, "baseline", reportable_oracle)
    with_dddjango = variant_data(run_dir, case_id, "with-dddjango", reportable_oracle)
    baseline_score = baseline["score_value"]
    with_score = with_dddjango["score_value"]
    hard_gate = hard_gate_from_oracle(reportable_oracle)
    intent = scalar_value(answer_text, "intent") or "Not recorded."
    failed_checks = yaml_list_values(answer_text, "failure_modes")
    leakage_notes = yaml_list_values(answer_text, "leakage_checks")
    evidence_required = yaml_list_values(answer_text, "evidence_required")
    evaluator_only = {
        "intent": intent,
        "failed_checks": failed_checks,
        "leakage_notes": leakage_notes,
        "evidence": [f"raw/{case_id}-answer-oracle-evaluation.json"],
        "evidence_required": evidence_required,
    }
    case: dict[str, object] = {
        "id": case_id,
        "bucket": bucket,
        "question": extract_question(read_text(public_case)),
        "detail_status": {
            "ready": "ready",
            "missing": "missing oracle evaluation",
            "invalid_json": "invalid oracle json",
            "invalid_schema": "invalid oracle schema",
        }.get(oracle_state, "invalid oracle schema"),
        "evaluator_only": evaluator_only,
        "evidence": (
            reportable_oracle.get("observations")
            if isinstance(reportable_oracle.get("observations"), list)
            else []
        ),
        "hard_gate": hard_gate,
        "baseline": baseline,
        "with_dddjango": with_dddjango,
        "delta_value": (
            with_score - baseline_score
            if isinstance(with_score, float) and isinstance(baseline_score, float)
            else None
        ),
        "delta": format_delta(
            baseline_score if isinstance(baseline_score, float) else None,
            with_score if isinstance(with_score, float) else None,
        ),
    }
    case["status"] = case_status(case)
    return case


def case_ids_with_run_artifacts(raw_dir: Path, public_cases: list[Path]) -> set[str]:
    public_case_ids = {path.stem for path in public_cases}
    artifact_suffixes = [
        "-public-prompt.md",
        "-operator-prompt.txt",
        "-answer-oracle-evaluation.json",
        "-answer-oracle-evaluation.raw.txt",
        "-answer-oracle-evaluation.stderr.txt",
        "-answer-oracle-evaluation-command.txt",
        "-answer-oracle-evaluation-exit.txt",
    ]
    for variant in VARIANTS:
        artifact_suffixes.extend(
            [
                f"-{variant}.txt",
                f"-{variant}.stderr.txt",
                f"-{variant}-events.jsonl",
                f"-{variant}-command.txt",
                f"-{variant}-exit.txt",
                f"-{variant}-isolation.json",
                f"-{variant}-prompt-input.json",
                f"-{variant}-prompt-input.stderr.txt",
            ]
        )

    case_ids: set[str] = set()
    if not raw_dir.is_dir():
        return case_ids
    for artifact in raw_dir.iterdir():
        if not artifact.is_file():
            continue
        for suffix in artifact_suffixes:
            if not artifact.name.endswith(suffix):
                continue
            case_id = artifact.name[: -len(suffix)]
            if case_id in public_case_ids:
                case_ids.add(case_id)
            break
    return case_ids


def public_cases_for_run(bucket: str, run_dir: Path) -> list[Path]:
    public_dir = EVAL_ROOT / bucket / "cases/plugin/public"
    public_cases = sorted(public_dir.glob("case-*.md"))
    run_case_ids = case_ids_with_run_artifacts(run_dir / "raw", public_cases)
    if not run_case_ids:
        return public_cases
    return [case_path for case_path in public_cases if case_path.stem in run_case_ids]


def sort_key(case: dict[str, object]) -> tuple[int, float, str]:
    status_rank = {"blocked": 0, "fail": 1, "partial": 2, "unscored": 3, "pass": 4}
    delta = case.get("delta_value")
    abs_delta = abs(delta) if isinstance(delta, float) else -1.0
    return (status_rank.get(str(case.get("status")), 5), -abs_delta, str(case.get("id") or ""))


def build_summary(cases: list[dict[str, object]]) -> dict[str, object]:
    status_counts = {status: 0 for status in ("pass", "partial", "fail", "blocked", "unscored")}
    baseline_values: list[float] = []
    with_values: list[float] = []
    paired_delta_values: list[float] = []
    hard_gate_failures = 0
    missing_or_weak_evidence = 0

    for case in cases:
        status = str(case.get("status") or "unscored")
        status_counts[status] = status_counts.get(status, 0) + 1
        baseline_score = case.get("baseline", {}).get("score_value") if isinstance(case.get("baseline"), dict) else None
        with_score = (
            case.get("with_dddjango", {}).get("score_value")
            if isinstance(case.get("with_dddjango"), dict)
            else None
        )
        if isinstance(baseline_score, float):
            baseline_values.append(baseline_score)
        if isinstance(with_score, float):
            with_values.append(with_score)
        if isinstance(baseline_score, float) and isinstance(with_score, float):
            paired_delta_values.append(with_score - baseline_score)
        if case.get("hard_gate") != "ok":
            hard_gate_failures += 1
        if status in {"blocked", "unscored"}:
            missing_or_weak_evidence += 1

    return {
        "total_cases": len(cases),
        "pass": status_counts["pass"],
        "partial": status_counts["partial"],
        "fail": status_counts["fail"],
        "blocked": status_counts["blocked"],
        "unscored": status_counts["unscored"],
        "baseline_average": format_average(baseline_values),
        "with_dddjango_average": format_average(with_values),
        "delta": format_signed_average(paired_delta_values),
        "hard_gate_failures": hard_gate_failures,
        "missing_or_weak_evidence": missing_or_weak_evidence,
    }


def add_run_scope(
    summary: dict[str, object],
    *,
    total_public_cases: int,
    run_cases: int,
) -> dict[str, object]:
    return {
        "total_public_cases": total_public_cases,
        "run_cases": run_cases,
        "unrun_cases": max(total_public_cases - run_cases, 0),
        **summary,
    }


def reportability(summary: dict[str, object]) -> str:
    if int(summary.get("hard_gate_failures") or 0) > 0:
        return "blocked"
    if int(summary.get("missing_or_weak_evidence") or 0) > 0:
        return "reportable-with-warnings"
    return "reportable"


def build_report_data(bucket: str, run_id: str, run_dir: Path) -> dict[str, object]:
    public_dir = EVAL_ROOT / bucket / "cases/plugin/public"
    public_cases = sorted(public_dir.glob("case-*.md"))
    run_public_cases = public_cases_for_run(bucket, run_dir)
    run_case_ids = {path.stem for path in run_public_cases}
    cases = [build_case(bucket, public_case, run_dir) for public_case in run_public_cases]
    cases.sort(key=sort_key)
    summary = add_run_scope(
        build_summary(cases),
        total_public_cases=len(public_cases),
        run_cases=len(cases),
    )
    return {
        "bucket": bucket,
        "run_id": run_id,
        "generated_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds"),
        "reportability": reportability(summary),
        "summary": summary,
        "unrun_case_ids": [
            public_case.stem for public_case in public_cases if public_case.stem not in run_case_ids
        ],
        "cases": cases,
    }


def status_class(value: object) -> str:
    normalized = re.sub(r"[^a-z0-9_-]+", "-", str(value or "unscored").strip().lower())
    normalized = normalized.strip("-") or "unscored"
    return f"status-{normalized}"


def js_json(data: object) -> str:
    encoded = (
        json.dumps(data, ensure_ascii=False, indent=2)
        .replace("</", "<\\/")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    return encoded.replace("\\u003c\\/script\\u003e", "<\\/script>")


def render_html(data: dict[str, object]) -> str:
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    cases = data.get("cases") if isinstance(data.get("cases"), list) else []
    unrun_case_ids = data.get("unrun_case_ids") if isinstance(data.get("unrun_case_ids"), list) else []
    summary_keys = (
        ("total_public_cases", "전체 public"),
        ("run_cases", "이번 실행"),
        ("unrun_cases", "미실행"),
        ("pass", "pass"),
        ("partial", "partial"),
        ("fail", "fail"),
        ("blocked", "blocked"),
        ("unscored", "unscored"),
        ("baseline_average", "baseline 평균"),
        ("with_dddjango_average", "with-dddjango 평균"),
        ("delta", "delta"),
        ("hard_gate_failures", "hard gate failures"),
        ("missing_or_weak_evidence", "missing/weak evidence"),
    )
    summary_cards = "\n".join(
        f"""        <div class="metric {status_class(key) if key in {'pass', 'partial', 'fail', 'blocked', 'unscored'} else ''}">
          <div class="metric-label">{escape(label)}</div>
          <div class="metric-value">{escape(str(summary.get(key, 'n/a')))}</div>
        </div>"""
        for key, label in summary_keys
    )

    rows: list[str] = []
    for index, case in enumerate(cases):
        case_data = case if isinstance(case, dict) else {}
        baseline = case_data.get("baseline") if isinstance(case_data.get("baseline"), dict) else {}
        with_dddjango = (
            case_data.get("with_dddjango")
            if isinstance(case_data.get("with_dddjango"), dict)
            else {}
        )
        status = str(case_data.get("status") or "unscored")
        rows.append(
            f"""          <tr class="{status_class(status)}">
            <td class="question-cell">
              <div class="case-id">{escape(str(case_data.get("id") or ""))}</div>
              <div class="question-preview">{escape(str(case_data.get("question") or ""))}</div>
            </td>
            <td>{escape(str(case_data.get("bucket") or ""))}</td>
            <td class="score-cell">{escape(str(baseline.get("score") or "not scored"))}</td>
            <td class="score-cell">{escape(str(with_dddjango.get("score") or "not scored"))}</td>
            <td class="delta-cell">{escape(str(case_data.get("delta") or "n/a"))}</td>
            <td class="status-cell"><span class="status-pill {status_class(status)}">{escape(status)}</span></td>
            <td class="action-cell"><button type="button" class="detail-button" aria-haspopup="dialog" data-detail-index="{index}">상세</button></td>
          </tr>"""
        )

    rows_html = "\n".join(rows) or """          <tr><td colspan="7" class="empty">No cases found.</td></tr>"""
    run_scope_note = (
        f"""      <details class="run-scope-note">
        <summary>미실행 질문 {escape(str(summary.get('unrun_cases', 0)))}개</summary>
        <pre>{escape(chr(10).join(str(case_id) for case_id in unrun_case_ids) or '없음')}</pre>
      </details>"""
        if int(summary.get("unrun_cases") or 0) > 0
        else ""
    )
    report_data = js_json(data)
    title = (
        f"dddjango eval review: {escape(str(data.get('bucket') or 'unknown'))} / "
        f"{escape(str(data.get('run_id') or 'unknown'))}"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --text: #1d2433;
      --muted: #626d7f;
      --line: #d9dee8;
      --accent: #225ea8;
      --accent-soft: #eaf2ff;
      --pass: #17663a;
      --partial: #8a5a00;
      --fail: #a32929;
      --blocked: #6c3ca0;
      --unscored: #4e5968;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 6px; font-size: 24px; letter-spacing: 0; }}
    h2 {{ margin: 0 0 14px; font-size: 18px; letter-spacing: 0; }}
    .meta {{ margin: 0 0 20px; color: var(--muted); }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin-bottom: 18px;
      padding: 18px;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-left: 4px solid #9ba7b8;
      border-radius: 6px;
      padding: 10px 12px;
      min-height: 74px;
      background: #fbfcfe;
    }}
    .metric-label {{ color: var(--muted); font-size: 12px; }}
    .metric-value {{ margin-top: 6px; font-size: 22px; font-weight: 700; }}
    .table-wrap {{
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
      background: #fff;
    }}
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
    th, td {{
      border-bottom: 1px solid var(--line);
      border-right: 1px solid var(--line);
      padding: 10px;
      text-align: left;
      vertical-align: middle;
    }}
    th:last-child, td:last-child {{ border-right: 0; }}
    th {{ color: var(--muted); font-size: 12px; font-weight: 700; background: #f1f4f8; }}
    tbody tr:hover {{ background: var(--accent-soft); }}
    tbody tr:last-child td {{ border-bottom: 0; }}
    .question-cell {{ white-space: normal; word-break: break-word; }}
    .case-id {{
      margin-bottom: 4px;
      color: var(--muted);
      font: 12px/1.35 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    .question-preview {{
      display: -webkit-box;
      overflow: hidden;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 3;
    }}
    .score-cell, .delta-cell, .status-cell, .action-cell {{ text-align: center; }}
    .status-pill {{
      display: inline-block;
      min-width: 72px;
      border-radius: 999px;
      padding: 2px 8px;
      color: #fff;
      font-size: 12px;
      text-align: center;
    }}
    .status-pass {{ border-left-color: var(--pass); }}
    .status-partial, .status-pass-limited, .status-pass-control {{ border-left-color: var(--partial); }}
    .status-fail {{ border-left-color: var(--fail); }}
    .status-blocked {{ border-left-color: var(--blocked); }}
    .status-unscored {{ border-left-color: var(--unscored); }}
    .status-pill.status-pass {{ background: var(--pass); }}
    .status-pill.status-partial, .status-pill.status-pass-limited, .status-pill.status-pass-control {{ background: var(--partial); }}
    .status-pill.status-fail {{ background: var(--fail); }}
    .status-pill.status-blocked {{ background: var(--blocked); }}
    .status-pill.status-unscored {{ background: var(--unscored); }}
    .detail-button {{
      border: 1px solid var(--accent);
      border-radius: 6px;
      background: #fff;
      color: var(--accent);
      font-weight: 700;
      padding: 5px 10px;
      cursor: pointer;
    }}
    .detail-button:hover {{ background: var(--accent); color: #fff; }}
    dialog {{
      width: min(1180px, calc(100vw - 48px));
      max-height: calc(100vh - 48px);
      border: 0;
      border-radius: 8px;
      padding: 0;
      color: var(--text);
      box-shadow: 0 24px 80px rgba(29, 36, 51, 0.28);
    }}
    dialog::backdrop {{ background: rgba(29, 36, 51, 0.45); }}
    .dialog-shell {{ max-height: calc(100vh - 48px); overflow: auto; background: #fff; }}
    .dialog-header {{
      position: sticky;
      top: 0;
      z-index: 1;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    .dialog-header h2 {{ margin: 0 0 4px; }}
    .dialog-meta {{ color: var(--muted); font-size: 12px; }}
    .dialog-close {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--text);
      cursor: pointer;
      font-size: 18px;
      line-height: 1;
      min-width: 34px;
      min-height: 34px;
    }}
    .dialog-close:hover {{ border-color: var(--accent); color: var(--accent); }}
    .dialog-body {{ padding: 18px; }}
    .detail-question {{
      margin: 0 0 14px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fbfcfe;
      white-space: pre-wrap;
    }}
    .detail-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    .variant {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      min-width: 0;
    }}
    .variant h3 {{ margin: 0 0 8px; font-size: 16px; }}
    .score-line {{ margin-bottom: 12px; color: var(--muted); }}
    .section-label {{ margin: 14px 0 6px; font-weight: 700; }}
    pre {{
      margin: 0;
      padding: 12px;
      max-height: 420px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f8fafc;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
    }}
    details {{ margin-top: 14px; }}
    summary {{ cursor: pointer; font-weight: 700; }}
    .empty {{ color: var(--muted); text-align: center; }}
    @media (max-width: 900px) {{
      main {{ padding: 14px; }}
      dialog {{ width: calc(100vw - 20px); max-height: calc(100vh - 20px); }}
      .dialog-shell {{ max-height: calc(100vh - 20px); }}
      .detail-grid {{ grid-template-columns: 1fr; }}
      table {{ table-layout: auto; }}
      th, td {{ padding: 8px; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>평가 리뷰</h1>
      <p class="meta">bucket: {escape(str(data.get('bucket') or 'unknown'))} · run: {escape(str(data.get('run_id') or 'unknown'))} · generated: {escape(str(data.get('generated_at') or 'unknown'))} · reportability: {escape(str(data.get('reportability') or 'unknown'))}</p>
    </header>
    <section class="panel" aria-labelledby="summary-title">
      <h2 id="summary-title">평가 요약</h2>
      <div class="summary-grid">
{summary_cards}
      </div>
    </section>
    <section class="panel" aria-labelledby="cases-title">
      <h2 id="cases-title">평가 질문 목록</h2>
      <div class="table-wrap">
      <table>
        <colgroup>
          <col style="width: 38%">
          <col style="width: 10%">
          <col style="width: 12%">
          <col style="width: 14%">
          <col style="width: 8%">
          <col style="width: 10%">
          <col style="width: 8%">
        </colgroup>
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
      </div>
{run_scope_note}
    </section>
  </main>
  <dialog id="case-dialog" aria-labelledby="dialog-title">
    <div class="dialog-shell">
      <header class="dialog-header">
        <div>
          <h2 id="dialog-title">상세</h2>
          <div id="case-dialog-meta" class="dialog-meta"></div>
        </div>
        <button type="button" class="dialog-close" id="case-dialog-close" aria-label="닫기">×</button>
      </header>
      <div id="case-dialog-body" class="dialog-body"></div>
    </div>
  </dialog>
  <script>
    const REPORT_DATA = {report_data};

    function esc(value) {{
      return String(value ?? "").replace(/[&<>"']/g, function (char) {{
        return {{
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;"
        }}[char];
      }});
    }}

    function variantHtml(label, item) {{
      item = item || {{}};
      return `
        <article class="variant">
          <h3>${{esc(label)}}</h3>
          <div class="score-line">score: ${{esc(item.score || "not scored")}} · verdict: ${{esc(item.verdict || "unscored")}}</div>
          <div class="section-label">응답</div>
          <pre>${{esc(item.response || "")}}</pre>
          <div class="section-label">평가</div>
          <pre>${{esc(item.evaluation || "")}}</pre>
        </article>`;
    }}

    function evaluatorHtml(caseData) {{
      const evaluator = caseData.evaluator_only || {{}};
      return `
        <details>
          <summary>evaluator-only details</summary>
          <div class="section-label">intent</div>
          <pre>${{esc(evaluator.intent || "")}}</pre>
          <div class="section-label">failed checks</div>
          <pre>${{esc((evaluator.failed_checks || []).join("\\n"))}}</pre>
          <div class="section-label">leakage notes</div>
          <pre>${{esc((evaluator.leakage_notes || []).join("\\n"))}}</pre>
          <div class="section-label">evidence required</div>
          <pre>${{esc((evaluator.evidence_required || []).join("\\n"))}}</pre>
          <div class="section-label">evidence</div>
          <pre>${{esc((evaluator.evidence || []).join("\\n"))}}</pre>
        </details>`;
    }}

    const caseDialog = document.getElementById("case-dialog");
    const caseDialogBody = document.getElementById("case-dialog-body");
    const caseDialogMeta = document.getElementById("case-dialog-meta");
    const caseDialogClose = document.getElementById("case-dialog-close");

    function openDialog(index) {{
      const cases = REPORT_DATA.cases || [];
      const caseData = cases[index];
      if (!caseData || !caseDialog || !caseDialogBody || !caseDialogMeta) {{
        return;
      }}
      caseDialogMeta.textContent = `${{caseData.id || ""}} · ${{caseData.bucket || ""}} · delta ${{caseData.delta || "n/a"}}`;
      caseDialogBody.innerHTML = `
        <div class="detail-question"><strong>문제</strong>\\n${{esc(caseData.question || "")}}</div>
        <div class="detail-grid">
          ${{variantHtml("Baseline", caseData.baseline)}}
          ${{variantHtml("with-dddjango", caseData.with_dddjango)}}
        </div>
        ${{evaluatorHtml(caseData)}}`;
      if (typeof caseDialog.showModal === "function") {{
        caseDialog.showModal();
      }} else {{
        caseDialog.setAttribute("open", "");
      }}
    }}

    document.querySelectorAll("[data-detail-index]").forEach(function (node) {{
      node.addEventListener("click", function () {{
        openDialog(Number(node.dataset.detailIndex));
      }});
    }});
    if (caseDialog && caseDialogClose) {{
      caseDialogClose.addEventListener("click", function () {{
        caseDialog.close();
      }});
      caseDialog.addEventListener("click", function (event) {{
        if (event.target === caseDialog) {{
          caseDialog.close();
        }}
      }});
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    run_dir = EVAL_ROOT / args.bucket / "runs" / args.run_id
    raw_dir = run_dir / "raw"
    if not run_dir.is_dir():
        raise SystemExit(f"run directory does not exist: {run_dir}")
    if not raw_dir.is_dir():
        raise SystemExit(f"run raw directory does not exist: {raw_dir}")
    output = args.output or run_dir / "analysis/report.html"
    data = build_report_data(args.bucket, args.run_id, run_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(data), encoding="utf-8")
    try:
        display_path = output.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        display_path = output
    print(f"wrote {display_path}")


if __name__ == "__main__":
    main()
