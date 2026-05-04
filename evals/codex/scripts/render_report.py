#!/usr/bin/env python3
import argparse
import json
import re
from html import escape
from pathlib import Path


CRITERIA = [
    "domain_fit",
    "django_ninja_compliance",
    "actionability",
    "architecture_quality",
    "testing_quality",
    "korean_first",
    "conciseness",
    "safety",
]

USABILITY_FIELDS = [
    ("actionable", "Actionable"),
    ("concise", "Concise"),
    ("realistic_file_layout", "Realistic Layout"),
    ("korean_quality", "Korean Quality"),
]


def load_json(path):
    return json.loads(Path(path).read_text())


def total_score(grade):
    return sum(grade["scores"][criterion] for criterion in CRITERIA)


def usability_for(grade):
    usability = grade.get("usability", {})
    return {
        field_id: usability.get(field_id, 0)
        for field_id, _label in USABILITY_FIELDS
    } | {"notes": usability.get("notes", "")}


def usability_total(usability):
    return sum(usability.get(field_id, 0) for field_id, _label in USABILITY_FIELDS)


def usability_recorded(usability):
    return bool(usability.get("notes")) or usability_total(usability) > 0


def index_by_case_and_variant(records):
    indexed = {}
    for record in records:
        indexed[(record["case_id"], record["variant"])] = record
    return indexed


def load_case_metadata(iteration):
    indexed = {}
    answer_key_dir = Path(iteration) / "answer-key"
    for path in sorted(answer_key_dir.glob("*.json")):
        data = load_json(path)
        indexed[path.stem] = {
            "title": data.get("title", path.stem),
            "category": data.get("category", ""),
            "expectations": data.get("expectations", []),
            "trigger_type": data.get("trigger_type", ""),
            "expected_behavior": data.get("expected_behavior", ""),
        }
    return indexed


def average(values):
    return round(sum(values) / len(values), 2) if values else 0.0


def duration_for(timing, case_id, variant):
    record = timing.get((case_id, variant), {})
    value = record.get("duration_sec")
    return value if value is not None else 0.0


def returncode_for(timing, case_id, variant):
    record = timing.get((case_id, variant), {})
    return record.get("returncode")


def verdict(delta, dddjango_grade):
    flags = dddjango_grade.get("flags", {})
    if flags.get("drf_endorsed"):
        return "failed"
    if delta >= 5:
        return "improved"
    if delta <= -5:
        return "regressed"
    return "flat"


def css_class_for_verdict(value):
    return {
        "improved": "good",
        "flat": "neutral",
        "regressed": "bad",
        "failed": "bad",
    }[value]


def css_class_for_status(value):
    return {
        "complete": "good",
        "partial": "neutral",
        "pending": "neutral",
        "error": "bad",
    }[value]


def link(path, label):
    return f'<a href="{escape(str(path))}">{escape(label)}</a>'


def render_inline_markdown(text):
    rendered = escape(text)
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"`([^`]+)`", r"<code>\1</code>", rendered)
    return rendered


def markdown_to_html(text):
    html = []
    in_code = False
    in_list = False
    paragraph = []

    def flush_paragraph():
        if paragraph:
            html.append(f"<p>{render_inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            html.append("</ul>")
            in_list = False

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                html.append("</code></pre>")
                in_code = False
            else:
                html.append("<pre><code>")
                in_code = True
            continue

        if in_code:
            html.append(escape(line))
            continue

        if not stripped:
            flush_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            html.append(f"<h{level}>{render_inline_markdown(heading.group(2))}</h{level}>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append(f"<li>{render_inline_markdown(stripped[2:])}</li>")
            continue

        numbered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if numbered:
            flush_paragraph()
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append(f"<li>{render_inline_markdown(numbered.group(1))}</li>")
            continue

        paragraph.append(stripped)

    flush_paragraph()
    close_list()
    if in_code:
        html.append("</code></pre>")
    return "\n".join(html)


def artifact_viewer_html(title, source_path):
    source_path = Path(source_path)
    if source_path.exists():
        body = source_path.read_text()
    else:
        body = f"Missing artifact: {source_path}"
    if source_path.suffix == ".md":
        rendered_body = f'<article class="markdown">{markdown_to_html(body)}</article>'
    else:
        rendered_body = f"<pre>{escape(body)}</pre>"
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>{escape(title)}</title>
  <style>
    body {{
      margin: 0;
      background: #f6f7f9;
      color: #17202a;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 20px 28px;
      border-bottom: 1px solid #d9dee7;
      background: #ffffff;
    }}
    h1 {{
      margin: 0;
      font-size: 20px;
      letter-spacing: 0;
    }}
    main {{
      padding: 24px 28px;
    }}
    article.markdown {{
      max-width: 980px;
      padding: 20px 24px;
      border: 1px solid #d9dee7;
      border-radius: 8px;
      background: #ffffff;
    }}
    article.markdown h1,
    article.markdown h2,
    article.markdown h3,
    article.markdown h4 {{
      margin: 22px 0 10px;
      letter-spacing: 0;
    }}
    article.markdown h1:first-child,
    article.markdown h2:first-child {{
      margin-top: 0;
    }}
    article.markdown p,
    article.markdown li {{
      font-size: 14px;
      line-height: 1.65;
    }}
    article.markdown pre {{
      margin: 14px 0;
    }}
    pre {{
      margin: 0;
      padding: 18px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      border: 1px solid #d9dee7;
      border-radius: 8px;
      background: #ffffff;
      font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
    }}
    .path {{
      margin-top: 6px;
      color: #667085;
      font-size: 13px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{escape(title)}</h1>
    <div class="path">{escape(str(source_path))}</div>
  </header>
  <main>
    {rendered_body}
  </main>
</body>
</html>
"""


def write_artifact_viewers(iteration, rows):
    artifact_dir = Path(iteration) / "artifacts"
    artifact_dir.mkdir(exist_ok=True)
    for row in rows:
        artifacts = [
            (
                "baseline_output",
                "baseline",
                Path(iteration) / "baseline" / f"{row['case_id']}.output.md",
            ),
            (
                "dddjango_output",
                "dddjango",
                Path(iteration) / "dddjango" / f"{row['case_id']}.output.md",
            ),
            (
                "answer_key",
                "answer-key",
                Path(iteration) / "answer-key" / f"{row['case_id']}.json",
            ),
        ]
        for row_key, label, source_path in artifacts:
            viewer_name = f"{row['case_id']}-{label}.html"
            viewer_path = artifact_dir / viewer_name
            title = f"{row['case_id']} {label}"
            viewer_path.write_text(artifact_viewer_html(title, source_path))
            row[row_key] = Path("artifacts") / viewer_name


def run_status(iteration, case_id, timing):
    baseline_output = Path(iteration) / "baseline" / f"{case_id}.output.md"
    dddjango_output = Path(iteration) / "dddjango" / f"{case_id}.output.md"
    baseline_code = returncode_for(timing, case_id, "baseline")
    dddjango_code = returncode_for(timing, case_id, "dddjango")
    if baseline_code not in {None, 0} or dddjango_code not in {None, 0}:
        return "error"
    if baseline_output.exists() and dddjango_output.exists():
        return "complete"
    if baseline_output.exists() or dddjango_output.exists():
        return "partial"
    return "pending"


def build_rows(iteration, grades, timing, case_metadata):
    case_ids = sorted({case_id for case_id, _variant in grades})
    rows = []
    for case_id in case_ids:
        baseline = grades.get((case_id, "baseline"))
        dddjango = grades.get((case_id, "dddjango"))
        if not baseline or not dddjango:
            continue

        baseline_score = total_score(baseline)
        dddjango_score = total_score(dddjango)
        delta = round(dddjango_score - baseline_score, 2)
        baseline_duration = duration_for(timing, case_id, "baseline")
        dddjango_duration = duration_for(timing, case_id, "dddjango")
        result = verdict(delta, dddjango)
        case = case_metadata.get(case_id, {})
        trigger = dddjango.get("trigger", {})

        rows.append(
            {
                "case_id": case_id,
                "title": case.get("title", case_id),
                "category": case.get("category", ""),
                "expectations": ", ".join(case.get("expectations", [])),
                "trigger_type": case.get("trigger_type", "") or trigger.get("type", ""),
                "expected_behavior": case.get("expected_behavior", "")
                or trigger.get("expected", ""),
                "trigger_observed": trigger.get("observed", ""),
                "trigger_passed": trigger.get("passed"),
                "status": run_status(iteration, case_id, timing),
                "baseline_score": baseline_score,
                "dddjango_score": dddjango_score,
                "delta": delta,
                "baseline_duration": baseline_duration,
                "dddjango_duration": dddjango_duration,
                "duration_delta": round(dddjango_duration - baseline_duration, 2),
                "verdict": result,
                "baseline_note": baseline.get("notes", ""),
                "dddjango_note": dddjango.get("notes", ""),
                "baseline_usability": usability_for(baseline),
                "dddjango_usability": usability_for(dddjango),
                "dddjango_scores": dddjango.get("scores", {}),
                "dddjango_flags": dddjango.get("flags", {}),
                "drf_failed": dddjango.get("flags", {}).get("drf_endorsed", False),
                "baseline_output": Path("baseline") / f"{case_id}.output.md",
                "dddjango_output": Path("dddjango") / f"{case_id}.output.md",
                "answer_key": Path("answer-key") / f"{case_id}.json",
            }
        )
    return rows


def build_trigger_gate_rows(rows):
    trigger_rows = [row for row in rows if row["trigger_type"]]
    if not trigger_rows:
        return ""

    positive_rows = [row for row in trigger_rows if row["trigger_type"] == "positive"]
    negative_rows = [row for row in trigger_rows if row["trigger_type"] == "negative"]
    ambiguous_rows = [row for row in trigger_rows if row["trigger_type"] == "ambiguous"]
    conflict_rows = [row for row in trigger_rows if row["trigger_type"] == "conflict"]

    def pass_rate(selected):
        return percent(sum(1 for row in selected if row["trigger_passed"]), len(selected))

    return "\n".join(
        [
            gate_row("Trigger Recall", pass_rate(positive_rows) >= 95, f"{pass_rate(positive_rows):.2f}%", ">= 95%"),
            gate_row("Trigger Precision", pass_rate(negative_rows) >= 95, f"{pass_rate(negative_rows):.2f}%", ">= 95%"),
            gate_row("Ambiguous Handling", pass_rate(ambiguous_rows) >= 80, f"{pass_rate(ambiguous_rows):.2f}%", ">= 80%"),
            gate_row("Conflict Handling", pass_rate(conflict_rows) >= 80, f"{pass_rate(conflict_rows):.2f}%", ">= 80%"),
        ]
    )


def build_trigger_matrix(rows):
    trigger_rows = [row for row in rows if row["trigger_type"]]
    if not trigger_rows:
        return ""

    table_rows = "\n".join(
        f"""
        <tr>
          <td><span class="pill neutral">{escape(row["trigger_type"])}</span></td>
          <td>
            <strong>{escape(row["title"])}</strong>
            <small><code>{escape(row["case_id"])}</code></small>
          </td>
          <td>{escape(row["expected_behavior"])}</td>
          <td>{escape(row["trigger_observed"])}</td>
          <td><span class="pill {'good' if row["trigger_passed"] else 'bad'}">{'PASS' if row["trigger_passed"] else 'BLOCKED'}</span></td>
          <td class="links">
            {link(row["baseline_output"], "baseline")}
            {link(row["dddjango_output"], "dddjango")}
            {link(row["answer_key"], "answer key")}
          </td>
        </tr>
        """
        for row in trigger_rows
    )

    return f"""
    <section class="section">
      <h2>Trigger Matrix</h2>
      <table>
        <thead>
          <tr>
            <th>Trigger Type</th>
            <th>Evaluation Item</th>
            <th>Expected Behavior</th>
            <th>Observed Behavior</th>
            <th>Verdict</th>
            <th>Artifacts</th>
          </tr>
        </thead>
        <tbody>
          {table_rows}
        </tbody>
      </table>
    </section>
    """


def build_usability_summary(rows):
    reviewed_rows = [row for row in rows if usability_recorded(row["dddjango_usability"])]
    if not reviewed_rows:
        return """
        <section class="section">
          <h2>Usability Summary</h2>
          <p class="empty">No manual usability scores recorded.</p>
        </section>
        """

    table_rows = "\n".join(
        f"""
        <tr>
          <td>
            <strong>{escape(row["title"])}</strong>
            <small><code>{escape(row["case_id"])}</code></small>
          </td>
          <td class="number">{row["dddjango_usability"]["actionable"]:.1f}</td>
          <td class="number">{row["dddjango_usability"]["concise"]:.1f}</td>
          <td class="number">{row["dddjango_usability"]["realistic_file_layout"]:.1f}</td>
          <td class="number">{row["dddjango_usability"]["korean_quality"]:.1f}</td>
          <td class="number">{usability_total(row["dddjango_usability"]):.1f}</td>
          <td>{escape(row["dddjango_usability"]["notes"])}</td>
        </tr>
        """
        for row in reviewed_rows
    )

    return f"""
    <section class="section">
      <h2>Usability Summary</h2>
      <table>
        <thead>
          <tr>
            <th>Case</th>
            <th>Actionable</th>
            <th>Concise</th>
            <th>Realistic Layout</th>
            <th>Korean Quality</th>
            <th>Total</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {table_rows}
        </tbody>
      </table>
    </section>
    """


def metric_card(title, value, subtitle="", tone="neutral"):
    return (
        f'<section class="metric {tone}">'
        f"<span>{escape(title)}</span>"
        f"<strong>{escape(str(value))}</strong>"
        f"<small>{escape(subtitle)}</small>"
        "</section>"
    )


def gate_row(label, passed, value, threshold):
    tone = "good" if passed else "bad"
    status = "PASS" if passed else "BLOCKED"
    return (
        f"<tr>"
        f"<td>{escape(label)}</td>"
        f'<td><span class="pill {tone}">{status}</span></td>'
        f"<td>{escape(str(value))}</td>"
        f"<td>{escape(str(threshold))}</td>"
        f"</tr>"
    )


def percent(count, total):
    return round((count / total) * 100, 2) if total else 0.0


def build_gate_rows(rows, lift_percent, duration_lift, drf_violations):
    total = len(rows)
    korean_rate = percent(
        sum(1 for row in rows if row["dddjango_flags"].get("korean_first")),
        total,
    )
    ninja_relevant = [
        row
        for row in rows
        if row["category"] in {"api-design", "implementation", "negative-control"}
        or row["case_id"] == "pilot-review-view-logic"
    ]
    ninja_rate = percent(
        sum(1 for row in ninja_relevant if row["dddjango_flags"].get("django_ninja_used")),
        len(ninja_relevant),
    )
    tdd_rows = [row for row in rows if row["category"] == "tdd" or "tdd" in row["case_id"]]
    tdd_rate = percent(
        sum(1 for row in tdd_rows if row["dddjango_scores"].get("testing_quality", 0) >= 8),
        len(tdd_rows),
    )
    negative_rows = [row for row in rows if row["category"] == "negative-control"]
    negative_rate = percent(
        sum(1 for row in negative_rows if row["dddjango_flags"].get("negative_control_passed")),
        len(negative_rows),
    )

    return "\n".join(
        [
            gate_row("Quality lift", lift_percent >= 15, f"{lift_percent:+.2f}%", ">= +15%"),
            gate_row("DRF violations", drf_violations == 0, drf_violations, "0"),
            gate_row("Korean-first rate", korean_rate >= 95, f"{korean_rate:.2f}%", ">= 95%"),
            gate_row("Django Ninja compliance", ninja_rate >= 90, f"{ninja_rate:.2f}%", ">= 90%"),
            gate_row("TDD quality", tdd_rate >= 80, f"{tdd_rate:.2f}%", ">= 80%"),
            gate_row("Time/cost increase", duration_lift <= 30, f"{duration_lift:+.2f}%", "<= +30%"),
            gate_row(
                "Negative-control pass rate",
                negative_rate >= 80,
                f"{negative_rate:.2f}%",
                ">= 80%",
            ),
        ]
    )


def render_html(iteration, rows, *, platform="Codex"):
    baseline_avg = average([row["baseline_score"] for row in rows])
    dddjango_avg = average([row["dddjango_score"] for row in rows])
    lift = round(dddjango_avg - baseline_avg, 2)
    lift_percent = round((lift / baseline_avg) * 100, 2) if baseline_avg else 0.0
    baseline_duration = average([row["baseline_duration"] for row in rows])
    dddjango_duration = average([row["dddjango_duration"] for row in rows])
    duration_lift = (
        round(((dddjango_duration / baseline_duration) - 1) * 100, 2)
        if baseline_duration
        else 0.0
    )
    drf_violations = sum(1 for row in rows if row["drf_failed"])
    complete_count = sum(1 for row in rows if row["status"] == "complete")
    usability_values = [
        usability_total(row["dddjango_usability"])
        for row in rows
        if usability_recorded(row["dddjango_usability"])
    ]
    usability_avg = average(usability_values)
    trigger_gate_rows = build_trigger_gate_rows(rows)
    gate_rows = "\n".join(
        item
        for item in [
            build_gate_rows(rows, lift_percent, duration_lift, drf_violations),
            trigger_gate_rows,
        ]
        if item
    )
    usability_summary = build_usability_summary(rows)
    trigger_matrix = build_trigger_matrix(rows)

    table_rows = "\n".join(
        f"""
        <tr>
          <td><span class="pill {css_class_for_status(row["status"])}">{escape(row["status"])}</span></td>
          <td>
            <strong>{escape(row["title"])}</strong>
            <small><code>{escape(row["case_id"])}</code></small>
          </td>
          <td>{escape(row["category"])}</td>
          <td>{escape(row["expectations"])}</td>
          <td class="number">{row["baseline_score"]:.1f}</td>
          <td class="number">{row["dddjango_score"]:.1f}</td>
          <td class="number {'good' if row["delta"] > 0 else 'bad' if row["delta"] < 0 else 'neutral'}">{row["delta"]:+.1f}</td>
          <td class="number">{row["baseline_duration"]:.2f}s</td>
          <td class="number">{row["dddjango_duration"]:.2f}s</td>
          <td><span class="pill {css_class_for_verdict(row["verdict"])}">{escape(row["verdict"])}</span></td>
          <td>{escape(row["baseline_note"])}</td>
          <td>{escape(row["dddjango_note"])}</td>
          <td class="links">
            {link(row["baseline_output"], "baseline")}
            {link(row["dddjango_output"], "dddjango")}
            {link(row["answer_key"], "answer key")}
          </td>
        </tr>
        """
        for row in rows
    )

    failure_items = "\n".join(
        f"<li><strong>{escape(row['case_id'])}</strong>: {escape(row['dddjango_note'])}</li>"
        for row in rows
        if row["verdict"] in {"failed", "regressed"}
    )

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>dddjango {escape(platform)} Evaluation Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #667085;
      --line: #d9dee7;
      --good: #087443;
      --good-bg: #e7f6ee;
      --bad: #b42318;
      --bad-bg: #fdecec;
      --neutral: #475467;
      --neutral-bg: #eef2f6;
      --accent: #0c4a6e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    header {{
      padding: 32px 40px 20px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      letter-spacing: 0;
    }}
    .subhead {{ color: var(--muted); max-width: 920px; }}
    main {{ padding: 24px 40px 40px; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
    }}
    .metric span, .metric small {{
      display: block;
      color: var(--muted);
      font-size: 13px;
    }}
    .metric strong {{
      display: block;
      margin: 6px 0;
      font-size: 24px;
    }}
    .metric.good strong {{ color: var(--good); }}
    .metric.bad strong {{ color: var(--bad); }}
    .section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin-top: 16px;
      overflow: hidden;
    }}
    .section h2 {{
      margin: 0;
      padding: 16px 18px;
      font-size: 18px;
      border-bottom: 1px solid var(--line);
    }}
    .failures {{ padding: 0 18px 18px; color: var(--bad); }}
    .empty {{ padding: 0 18px 18px; color: var(--muted); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
      text-align: left;
    }}
    th {{
      position: sticky;
      top: 0;
      background: #f8fafc;
      color: #344054;
      font-weight: 650;
      z-index: 1;
    }}
    .number {{ text-align: right; white-space: nowrap; }}
    .good {{ color: var(--good); }}
    .bad {{ color: var(--bad); }}
    .neutral {{ color: var(--neutral); }}
    .pill {{
      display: inline-block;
      min-width: 72px;
      padding: 3px 8px;
      border-radius: 999px;
      text-align: center;
      font-size: 12px;
      font-weight: 650;
    }}
    .pill.good {{ background: var(--good-bg); }}
    .pill.bad {{ background: var(--bad-bg); }}
    .pill.neutral {{ background: var(--neutral-bg); }}
    .links a {{
      display: block;
      color: var(--accent);
      text-decoration: none;
      margin-bottom: 4px;
    }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    @media (max-width: 900px) {{
      header, main {{ padding-left: 18px; padding-right: 18px; }}
      .section {{ overflow-x: auto; }}
      table {{ min-width: 1180px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>dddjango {escape(platform)} Evaluation Report</h1>
    <div class="subhead">Baseline과 dddjango 플러그인 활성화 결과를 같은 평가 케이스로 비교합니다. 점수는 100점 만점 rubric 기준이며, 링크는 같은 iteration 디렉터리 안의 raw output과 answer key를 엽니다.</div>
  </header>
  <main>
    <div class="metrics">
      {metric_card("Baseline Score", baseline_avg, "case average")}
      {metric_card("dddjango Score", dddjango_avg, "case average", "good" if dddjango_avg > baseline_avg else "bad")}
      {metric_card("Quality Lift", f"{lift:+.2f}", f"{lift_percent:+.2f}% vs baseline", "good" if lift > 0 else "bad")}
      {metric_card("Baseline Time", f"{baseline_duration:.2f}s", "average duration")}
      {metric_card("dddjango Time", f"{dddjango_duration:.2f}s", f"{duration_lift:+.2f}% vs baseline", "bad" if duration_lift > 30 else "neutral")}
      {metric_card("DRF Violations", drf_violations, "dddjango variant", "bad" if drf_violations else "good")}
      {metric_card("Completed Cases", f"{complete_count}/{len(rows)}", "with and without skill")}
      {metric_card("Manual Usability", f"{usability_avg:.2f}", "dddjango average / 20" if usability_values else "pending / 20")}
    </div>

    <section class="section">
      <h2>Failure Highlights</h2>
      <ul class="failures">
        {failure_items or "<li>No failed or regressed cases.</li>"}
      </ul>
    </section>

    <section class="section">
      <h2>Release Gate</h2>
      <table>
        <thead>
          <tr>
            <th>Gate</th>
            <th>Status</th>
            <th>Current</th>
            <th>Required</th>
          </tr>
        </thead>
        <tbody>
          {gate_rows}
        </tbody>
      </table>
    </section>

    <section class="section">
      <h2>Case Comparison: Without Skill vs With dddjango</h2>
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>Evaluation Item</th>
            <th>Category</th>
            <th>Expectations</th>
            <th>Without Skill</th>
            <th>With dddjango</th>
            <th>Delta</th>
            <th>Without Time</th>
            <th>With Time</th>
            <th>Verdict</th>
            <th>Without Note</th>
            <th>With Note</th>
            <th>Artifacts</th>
          </tr>
        </thead>
        <tbody>
          {table_rows}
        </tbody>
      </table>
    </section>
{usability_summary}
{trigger_matrix}
  </main>
</body>
</html>
"""


def render_report(iteration, *, platform="Codex"):
    iteration = Path(iteration)
    grades = index_by_case_and_variant(load_json(iteration / "grades.json"))
    timing = index_by_case_and_variant(load_json(iteration / "timing.json"))
    case_metadata = load_case_metadata(iteration)
    rows = build_rows(iteration, grades, timing, case_metadata)
    write_artifact_viewers(iteration, rows)
    html = render_html(iteration, rows, platform=platform)
    report_path = iteration / "report.html"
    report_path.write_text(html)
    return report_path


def main():
    parser = argparse.ArgumentParser(description="Render a static HTML eval report.")
    parser.add_argument("iteration", help="Evaluation iteration directory.")
    parser.add_argument("--platform", default="Codex", help="Platform label for the report title.")
    args = parser.parse_args()

    report_path = render_report(Path(args.iteration), platform=args.platform)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
