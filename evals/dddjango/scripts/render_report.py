#!/usr/bin/env python3
"""Render dddjango purpose-fit evaluation HTML reports."""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any

from eval_lib import (
    EVAL_ROOT,
    VARIANTS,
    load_cases,
    load_dimensions,
    load_reference_matrix,
    markdown_to_html,
    read_json,
    run_dir_from_args,
)


def td(value: object) -> str:
    return f"<td>{html.escape(str(value))}</td>"


def score_badge(score: object) -> str:
    if score == "":
        return "<span class=\"muted\">-</span>"
    value = int(score)
    klass = "good" if value >= 80 else "warn" if value >= 60 else "bad"
    return f"<span class=\"score {klass}\">{value}</span>"


def render_artifacts(run_dir: Path, cases: list[dict[str, Any]]) -> None:
    artifact_dir = run_dir / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for output_path in sorted((run_dir / "outputs").glob("*.md")):
        title = output_path.stem
        html_path = artifact_dir / f"{output_path.stem}.html"
        html_path.write_text(markdown_to_html(output_path.read_text(), title=title))
    for case in cases:
        baseline_path = EVAL_ROOT / case["baseline"]
        html_path = artifact_dir / f"{case['id']}.baseline.html"
        html_path.write_text(markdown_to_html(baseline_path.read_text(), title=f"{case['id']} baseline"))


def load_score_map(run_dir: Path) -> dict[tuple[str, str], dict[str, Any]]:
    score_map: dict[tuple[str, str], dict[str, Any]] = {}
    for score_path in sorted((run_dir / "scores").glob("*.score.json")):
        score = read_json(score_path)
        score_map[(score["case_id"], score["variant"])] = score
    return score_map


def render_mode_notice(metadata: dict[str, Any], summary: dict[str, Any]) -> str:
    mode = metadata.get("mode", "-")
    interpretation = summary.get("score_interpretation", "-")
    if mode == "live":
        return (
            "<section class=\"notice live\"><h2>Interpretation</h2>"
            "<p>이 리포트는 실제 Codex 실행 결과입니다. 단, 자동 점수는 낮은 신뢰도의 signal이므로 "
            "artifact 수동 검토와 함께 해석해야 합니다.</p>"
            "</section>"
        )
    return (
        "<section class=\"notice fixture\"><h2>Interpretation</h2>"
        "<p><strong>이 리포트는 플러그인 성능 평가가 아닙니다.</strong> "
        "fixture/smoke 결과는 평가 파이프라인, 채점기, HTML 렌더링이 동작하는지만 확인합니다. "
        "with-dddjango 점수와 delta를 플러그인 가치 판단에 사용하지 마세요.</p>"
        f"<p class=\"muted\">mode={html.escape(str(mode))}, interpretation={html.escape(str(interpretation))}</p>"
        "</section>"
    )


def render_summary(summary: dict[str, Any], metadata: dict[str, Any]) -> str:
    rows = []
    for variant, data in summary.get("by_variant", {}).items():
        rows.append(
            "<tr>"
            + td(variant)
            + f"<td>{score_badge(data.get('average', ''))}</td>"
            + td(data.get("case_count", 0))
            + td(len(data.get("critical_failures", [])))
            + "</tr>"
        )
    delta = summary.get("skill_value_delta")
    if metadata.get("mode") == "live":
        delta_html = "<p class=\"metric\">Skill value delta: <strong>{}</strong></p>".format(
            html.escape(str(delta)) if delta is not None else "-"
        )
    else:
        delta_html = (
            "<p class=\"metric\">Skill value delta: <strong>not applicable</strong> "
            "<span class=\"muted\">fixture/smoke 점수는 성능 lift로 해석하지 않는다.</span></p>"
        )
    return (
        "<section><h2>Summary</h2>"
        + delta_html
        + "<table><thead><tr><th>Variant</th><th>Average</th><th>Cases</th><th>Critical failures</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></section>"
    )


def render_release_gates(summary: dict[str, Any]) -> str:
    release_status = summary.get("release_gate_status", {})
    rows = []
    for result in release_status.get("results", []):
        rows.append(
            "<tr>"
            + td(result.get("gate", ""))
            + td(result.get("status", ""))
            + td(result.get("actual", ""))
            + td(result.get("expected", ""))
            + (f"<td class=\"muted\">{html.escape(', '.join(result.get('cases', [])[:8]))}</td>" if result.get("cases") else "<td class=\"muted\">-</td>")
            + "</tr>"
        )
    if not rows:
        rows.append(
            "<tr><td colspan=\"5\" class=\"muted\">"
            + html.escape(release_status.get("message", "No release gate result"))
            + "</td></tr>"
        )
    message = release_status.get("message", "")
    message_html = f"<p class=\"muted\">{html.escape(message)}</p>" if message else ""
    return (
        "<section><h2>Release Gates</h2>"
        f"<p class=\"metric\">Status: <strong>{html.escape(str(release_status.get('status', '-')))}</strong> "
        f"<span class=\"muted\">mode={html.escape(str(release_status.get('mode', '-')))}</span></p>"
        + message_html
        + "<table><thead><tr><th>Gate</th><th>Status</th><th>Actual</th><th>Expected</th><th>Cases</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></section>"
    )


def render_variant_table(run_dir: Path, cases: list[dict[str, Any]], score_map: dict[tuple[str, str], dict[str, Any]]) -> str:
    rows = []
    for case in cases:
        baseline_link = html.escape(str(Path("artifacts") / f"{case['id']}.baseline.html"))
        cells = [
            td(case["id"]),
            td(case["title"]),
            f"<td><a href=\"{baseline_link}\">baseline</a></td>",
        ]
        for variant in VARIANTS:
            score = score_map.get((case["id"], variant))
            if score:
                artifact = Path("artifacts") / f"{case['id']}.{variant}.html"
                cells.append(
                    "<td>"
                    + score_badge(score["total_score"])
                    + f" <a href=\"{html.escape(str(artifact))}\">artifact</a>"
                    + f"<div class=\"muted\">{html.escape(score['gate_status'])}</div>"
                    + f"<div class=\"muted\">{html.escape(score.get('score_kind', ''))}</div>"
                    + "</td>"
                )
            else:
                cells.append("<td class=\"muted\">missing</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        "<section><h2>Variant Comparison</h2>"
        "<table><thead><tr><th>Case</th><th>Title</th><th>Baseline</th><th>without-dddjango</th><th>with-dddjango</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></section>"
    )


def render_dimension_table(score_map: dict[tuple[str, str], dict[str, Any]]) -> str:
    dimensions = load_dimensions()
    rows = []
    for dimension, meta in dimensions.items():
        values: dict[str, list[int]] = {variant: [] for variant in VARIANTS}
        for (_, variant), score in score_map.items():
            if dimension in score.get("dimension_scores", {}):
                values[variant].append(score["dimension_scores"][dimension])
        if not any(values.values()):
            continue
        cells = [td(meta["label"])]
        for variant in VARIANTS:
            if values[variant]:
                average = round(sum(values[variant]) / len(values[variant]))
                cells.append(f"<td>{score_badge(average)}</td>")
            else:
                cells.append("<td class=\"muted\">-</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        "<section><h2>Dimension Scores</h2>"
        "<table><thead><tr><th>Dimension</th><th>without-dddjango</th><th>with-dddjango</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></section>"
    )


def render_gate_table(score_map: dict[tuple[str, str], dict[str, Any]]) -> str:
    rows = []
    for (case_id, variant), score in sorted(score_map.items()):
        for result in score.get("gate_results", []):
            if result["status"] != "fail":
                continue
            rows.append(
                "<tr>"
                + td(case_id)
                + td(variant)
                + td(result["gate"])
                + td(result["severity"])
                + td(", ".join(result.get("evidence", [])))
                + td(result.get("message", ""))
                + "</tr>"
            )
    if not rows:
        rows.append("<tr><td colspan=\"6\" class=\"muted\">No gate failures</td></tr>")
    return (
        "<section><h2>Fail-Fast Gates</h2>"
        "<table><thead><tr><th>Case</th><th>Variant</th><th>Gate</th><th>Severity</th><th>Evidence</th><th>Message</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></section>"
    )


def render_reference_matrix(cases: list[dict[str, Any]]) -> str:
    matrix = load_reference_matrix().get("cases", {})
    rows = []
    for case in cases:
        entry = matrix.get(case["id"], {})
        references = entry.get("reference_paths", [])
        guards = entry.get("guard_paths", [])
        ref_text = "<br>".join(html.escape(path) for path in references) if references else "<span class=\"muted\">-</span>"
        guard_text = "<br>".join(html.escape(path) for path in guards) if guards else "<span class=\"muted\">-</span>"
        rows.append(
            "<tr>"
            + td(case["id"])
            + td(", ".join(entry.get("expected_skills", [])))
            + f"<td>{ref_text}</td>"
            + f"<td>{guard_text}</td>"
            + td(entry.get("diagnostic_use", ""))
            + "</tr>"
        )

    return (
        "<section><h2>Reference Matrix</h2>"
        "<table><thead><tr><th>Case</th><th>Expected skills</th><th>References</th><th>Guard paths</th><th>Diagnostic use</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></section>"
    )


def render_report(run_dir: Path, suite: str | None = None, case_id: str | None = None) -> Path:
    cases = load_cases(suite)
    if case_id:
        cases = [case for case in cases if case["id"] == case_id]
    render_artifacts(run_dir, cases)
    summary = read_json(run_dir / "scores/summary.json")
    score_map = load_score_map(run_dir)
    metadata = read_json(run_dir / "metadata.json") if (run_dir / "metadata.json").exists() else {}

    html_doc = "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"ko\">",
            "<head>",
            "  <meta charset=\"utf-8\">",
            "  <title>dddjango Purpose-Fit Evaluation</title>",
            "  <style>",
            "    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 32px; color: #111827; line-height: 1.5; }",
            "    h1, h2 { margin-top: 0; }",
            "    section { margin-top: 32px; }",
            "    table { border-collapse: collapse; width: 100%; font-size: 14px; }",
            "    th, td { border: 1px solid #d1d5db; padding: 8px 10px; vertical-align: top; }",
            "    th { background: #f3f4f6; text-align: left; }",
            "    a { color: #0f766e; }",
            "    .muted { color: #6b7280; font-size: 12px; }",
            "    .metric { font-size: 16px; }",
            "    .score { display: inline-block; min-width: 34px; padding: 2px 6px; border-radius: 4px; text-align: center; font-weight: 700; }",
            "    .good { background: #dcfce7; color: #166534; }",
            "    .warn { background: #fef3c7; color: #92400e; }",
            "    .bad { background: #fee2e2; color: #991b1b; }",
            "    .notice { border: 1px solid #d1d5db; padding: 12px 14px; border-radius: 6px; }",
            "    .notice.fixture { background: #fff7ed; border-color: #fed7aa; }",
            "    .notice.live { background: #ecfdf5; border-color: #a7f3d0; }",
            "  </style>",
            "</head>",
            "<body>",
            "  <main>",
            "    <h1>dddjango Purpose-Fit Evaluation</h1>",
            f"    <p class=\"muted\">Run: {html.escape(run_dir.name)} / Mode: {html.escape(str(metadata.get('mode', '-')))}</p>",
            render_mode_notice(metadata, summary),
            render_summary(summary, metadata),
            render_release_gates(summary),
            render_variant_table(run_dir, cases, score_map),
            render_dimension_table(score_map),
            render_gate_table(score_map),
            render_reference_matrix(cases),
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )
    report_path = run_dir / "report.html"
    report_path.write_text(html_doc)
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id")
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--suite")
    parser.add_argument("--case")
    args = parser.parse_args()

    run_dir = run_dir_from_args(args.run_id, args.latest)
    report = render_report(run_dir, args.suite, args.case)
    print(f"HTML 리포트 생성 완료: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
