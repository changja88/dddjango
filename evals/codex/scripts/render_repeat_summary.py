#!/usr/bin/env python3
import argparse
import json
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


def load_json(path, default):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text())


def average(values):
    return round(sum(values) / len(values), 2) if values else 0.0


def total_score(record):
    return sum(record["scores"].get(criterion, 0) for criterion in CRITERIA)


def iteration_label(path):
    return Path(path).name


def load_case_categories(iteration):
    categories = {}
    answer_key_dir = Path(iteration) / "answer-key"
    for path in sorted(answer_key_dir.glob("*.json")):
        data = load_json(path, {})
        categories[path.stem] = data.get("category", "")
    return categories


def summarize_iteration(iteration):
    iteration = Path(iteration)
    grades = load_json(iteration / "grades.json", [])
    timing = load_json(iteration / "timing.json", [])
    categories = load_case_categories(iteration)

    scores = {"baseline": [], "dddjango": []}
    durations = {"baseline": [], "dddjango": []}
    returncodes = {"baseline": [], "dddjango": []}
    category_scores = {}

    for record in grades:
        variant = record["variant"]
        if variant not in scores:
            continue
        score = total_score(record)
        scores[variant].append(score)
        category = categories.get(record["case_id"], "")
        category_scores.setdefault(category, {"baseline": [], "dddjango": []})
        category_scores[category][variant].append(score)

    for record in timing:
        variant = record.get("variant")
        if variant not in durations:
            continue
        if record.get("duration_sec") is not None:
            durations[variant].append(record["duration_sec"])
        if record.get("returncode") is not None:
            returncodes[variant].append(record["returncode"])

    baseline_avg = average(scores["baseline"])
    dddjango_avg = average(scores["dddjango"])
    delta = round(dddjango_avg - baseline_avg, 2)
    lift_percent = round((delta / baseline_avg * 100), 2) if baseline_avg else 0.0
    baseline_time = average(durations["baseline"])
    dddjango_time = average(durations["dddjango"])
    time_delta_percent = (
        round((dddjango_time - baseline_time) / baseline_time * 100, 2)
        if baseline_time
        else 0.0
    )

    return {
        "iteration": iteration_label(iteration),
        "path": str(iteration),
        "report": str(iteration / "report.html"),
        "baseline_count": len(scores["baseline"]),
        "dddjango_count": len(scores["dddjango"]),
        "baseline_returncode_ok": sum(1 for code in returncodes["baseline"] if code == 0),
        "dddjango_returncode_ok": sum(1 for code in returncodes["dddjango"] if code == 0),
        "baseline_avg": baseline_avg,
        "dddjango_avg": dddjango_avg,
        "delta": delta,
        "lift_percent": lift_percent,
        "baseline_time": baseline_time,
        "dddjango_time": dddjango_time,
        "time_delta_percent": time_delta_percent,
        "categories": {
            category: {
                "baseline_avg": average(values["baseline"]),
                "dddjango_avg": average(values["dddjango"]),
                "delta": round(
                    average(values["dddjango"]) - average(values["baseline"]),
                    2,
                ),
                "count": len(values["baseline"]),
            }
            for category, values in sorted(category_scores.items())
            if values["baseline"] and values["dddjango"]
        },
    }


def summarize_overall(iterations):
    baseline = []
    dddjango = []
    baseline_time = []
    dddjango_time = []
    categories = {}
    for summary in iterations:
        baseline.append(summary["baseline_avg"])
        dddjango.append(summary["dddjango_avg"])
        baseline_time.append(summary["baseline_time"])
        dddjango_time.append(summary["dddjango_time"])
        for category, values in summary["categories"].items():
            categories.setdefault(category, {"baseline": [], "dddjango": []})
            categories[category]["baseline"].append(values["baseline_avg"])
            categories[category]["dddjango"].append(values["dddjango_avg"])

    baseline_avg = average(baseline)
    dddjango_avg = average(dddjango)
    delta = round(dddjango_avg - baseline_avg, 2)
    baseline_time_avg = average(baseline_time)
    dddjango_time_avg = average(dddjango_time)
    return {
        "baseline_avg": baseline_avg,
        "dddjango_avg": dddjango_avg,
        "delta": delta,
        "lift_percent": round((delta / baseline_avg * 100), 2) if baseline_avg else 0.0,
        "baseline_time": baseline_time_avg,
        "dddjango_time": dddjango_time_avg,
        "time_delta_percent": (
            round((dddjango_time_avg - baseline_time_avg) / baseline_time_avg * 100, 2)
            if baseline_time_avg
            else 0.0
        ),
        "categories": {
            category: {
                "baseline_avg": average(values["baseline"]),
                "dddjango_avg": average(values["dddjango"]),
                "delta": round(
                    average(values["dddjango"]) - average(values["baseline"]),
                    2,
                ),
            }
            for category, values in sorted(categories.items())
        },
    }


def format_signed(value):
    return f"{value:+.2f}"


def render_table(headers, rows):
    html = ["<table>", "<thead><tr>"]
    html.extend(f"<th>{escape(header)}</th>" for header in headers)
    html.append("</tr></thead><tbody>")
    for row in rows:
        html.append("<tr>")
        html.extend(f"<td>{cell}</td>" for cell in row)
        html.append("</tr>")
    html.append("</tbody></table>")
    return "\n".join(html)


def render_repeat_summary(iterations, output, title="dddjango Benchmark Repeat Summary"):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    iteration_summaries = [summarize_iteration(path) for path in iterations]
    overall = summarize_overall(iteration_summaries)
    summary = {"iterations": iteration_summaries, "overall": overall}

    iteration_rows = []
    for item in iteration_summaries:
        report = escape(item["report"])
        iteration_rows.append(
            [
                f'<a href="{report}">{escape(item["iteration"])}</a>',
                str(item["baseline_count"]),
                str(item["dddjango_count"]),
                f'{item["baseline_avg"]:.2f}',
                f'{item["dddjango_avg"]:.2f}',
                format_signed(item["delta"]),
                f'{format_signed(item["lift_percent"])}%',
                f'{item["baseline_time"]:.2f}s',
                f'{item["dddjango_time"]:.2f}s',
                f'{format_signed(item["time_delta_percent"])}%',
            ]
        )

    category_rows = []
    for category, item in overall["categories"].items():
        category_rows.append(
            [
                escape(category),
                f'{item["baseline_avg"]:.2f}',
                f'{item["dddjango_avg"]:.2f}',
                format_signed(item["delta"]),
            ]
        )

    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #172033; }}
    h1 {{ margin-bottom: 6px; }}
    .summary {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 24px 0; }}
    .metric {{ border: 1px solid #d8dee8; border-radius: 8px; padding: 14px 16px; min-width: 170px; }}
    .metric strong {{ display: block; font-size: 24px; margin-top: 4px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 18px 0 30px; }}
    th, td {{ border: 1px solid #d8dee8; padding: 8px 10px; text-align: left; }}
    th {{ background: #f6f8fb; }}
    a {{ color: #0b5cad; }}
  </style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <p>with/without dddjango 반복 측정 요약입니다.</p>
  <section class="summary">
    <div class="metric">Baseline Avg<strong>{overall["baseline_avg"]:.2f}</strong></div>
    <div class="metric">dddjango Avg<strong>{overall["dddjango_avg"]:.2f}</strong></div>
    <div class="metric">Delta<strong>{format_signed(overall["delta"])}</strong></div>
    <div class="metric">Lift<strong>{format_signed(overall["lift_percent"])}%</strong></div>
    <div class="metric">Time Change<strong>{format_signed(overall["time_delta_percent"])}%</strong></div>
  </section>
  <h2>Iteration Summary</h2>
  {render_table([
      "Iteration", "Baseline Cases", "dddjango Cases", "Baseline Avg",
      "dddjango Avg", "Delta", "Lift", "Baseline Time", "dddjango Time",
      "Time Change"
  ], iteration_rows)}
  <h2>Category Summary</h2>
  {render_table(["Category", "Baseline Avg", "dddjango Avg", "Delta"], category_rows)}
</body>
</html>
"""
    output.write_text(html)
    summary_path = output.with_suffix(".json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Render an aggregate HTML report for repeated benchmark iterations."
    )
    parser.add_argument("iterations", nargs="+", help="Iteration directories to summarize.")
    parser.add_argument(
        "--output",
        default="workspace/codex-eval/benchmark-repeat-summary/report.html",
    )
    parser.add_argument("--title", default="dddjango Benchmark Repeat Summary")
    args = parser.parse_args()

    render_repeat_summary(args.iterations, args.output, title=args.title)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
