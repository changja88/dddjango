#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


VARIANTS = ("baseline", "dddjango")


def load_cases(path):
    cases = []
    for line_number, line in enumerate(Path(path).read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            cases.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
    return cases


def load_schema(path):
    return json.loads(Path(path).read_text())


def slug(value):
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip())
    return cleaned.strip("-").lower()


def prompt_markdown(case, variant):
    return (
        f"# {case['id']}\n\n"
        f"Variant: {variant}\n"
        f"Category: {case['category']}\n"
        f"Title: {case['title']}\n"
        f"Fixture: {case.get('fixture', 'none')}\n"
        f"Mode: {case.get('mode', 'manual')}\n\n"
        "## Prompt\n\n"
        f"{case['prompt']}\n"
    )


def answer_key(case):
    return {
        "case_id": case["id"],
        "category": case["category"],
        "title": case["title"],
        "expectations": case["expectations"],
        "scoring_focus": case["scoring_focus"],
        "prompt": case["prompt"],
    }


def empty_grade(case, variant, schema):
    return {
        "case_id": case["id"],
        "variant": variant,
        "scores": {criterion["id"]: 0 for criterion in schema["criteria"]},
        "notes": "",
        "flags": {
            "korean_first": False,
            "django_ninja_used": False,
            "drf_endorsed": False,
            "negative_control_passed": False,
        },
    }


def empty_timing(case, variant):
    return {
        "case_id": case["id"],
        "variant": variant,
        "duration_sec": None,
        "approx_tokens_in": None,
        "approx_tokens_out": None,
        "tool_calls": None,
        "model": "",
        "reasoning_effort": "",
        "notes": "",
    }


def summary_markdown(cases):
    rows = "\n".join(f"| {case['id']} | {case['category']} | pending | |" for case in cases)
    return (
        "# Codex dddjango Evaluation Iteration\n\n"
        "## Environment\n\n"
        "- dddjango version/tag:\n"
        "- Codex version:\n"
        "- Model:\n"
        "- Reasoning effort:\n"
        "- Baseline environment:\n"
        "- dddjango environment:\n\n"
        "## Results\n\n"
        "| Case | Category | Status | Notes |\n"
        "| --- | --- | --- | --- |\n"
        f"{rows}\n\n"
        "## Summary\n\n"
        "- Baseline average:\n"
        "- dddjango average:\n"
        "- Absolute lift:\n"
        "- Percent lift:\n"
        "- DRF violations:\n"
        "- Korean-first rate:\n"
        "- Django Ninja compliance rate:\n\n"
        "## Follow-up\n\n"
        "-\n"
    )


def create_iteration(cases_path, schema_path, output_path):
    cases = load_cases(cases_path)
    schema = load_schema(schema_path)
    output = Path(output_path)
    output.mkdir(parents=True, exist_ok=True)

    grades = []
    timing = []
    answer_key_dir = output / "answer-key"
    answer_key_dir.mkdir(exist_ok=True)
    for variant in VARIANTS:
        variant_dir = output / variant
        variant_dir.mkdir(exist_ok=True)
        for case in cases:
            file_name = f"{slug(case['id'])}.prompt.md"
            (variant_dir / file_name).write_text(prompt_markdown(case, variant))
            grades.append(empty_grade(case, variant, schema))
            timing.append(empty_timing(case, variant))

    for case in cases:
        file_name = f"{slug(case['id'])}.json"
        (answer_key_dir / file_name).write_text(
            json.dumps(answer_key(case), ensure_ascii=False, indent=2) + "\n"
        )

    (output / "grades.json").write_text(json.dumps(grades, ensure_ascii=False, indent=2) + "\n")
    (output / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2) + "\n")
    (output / "SUMMARY.md").write_text(summary_markdown(cases))
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Create a manual Codex plugin evaluation iteration workspace."
    )
    parser.add_argument(
        "--cases",
        default="evals/codex/cases/pilot.jsonl",
        help="Path to evaluation cases JSONL.",
    )
    parser.add_argument(
        "--schema",
        default="evals/codex/rubrics/grading-schema.json",
        help="Path to grading schema JSON.",
    )
    parser.add_argument(
        "--output",
        default="workspace/codex-eval/iteration-1",
        help="Directory to create for this evaluation iteration.",
    )
    args = parser.parse_args()

    output = create_iteration(args.cases, args.schema, args.output)
    print(f"created evaluation iteration: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
