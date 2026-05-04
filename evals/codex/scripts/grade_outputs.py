#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text())


def validate_grade(grade, schema):
    required = {"case_id", "variant", "scores"}
    missing = sorted(required - set(grade))
    if missing:
        raise ValueError(f"grade is missing required fields: {', '.join(missing)}")

    allowed_criteria = {item["id"]: item["weight"] for item in schema["criteria"]}
    score_keys = set(grade["scores"])
    missing_scores = sorted(set(allowed_criteria) - score_keys)
    extra_scores = sorted(score_keys - set(allowed_criteria))
    if missing_scores:
        raise ValueError(
            f"{grade['case_id']}:{grade['variant']} missing scores: "
            + ", ".join(missing_scores)
        )
    if extra_scores:
        raise ValueError(
            f"{grade['case_id']}:{grade['variant']} has unknown scores: "
            + ", ".join(extra_scores)
        )

    for criterion_id, value in grade["scores"].items():
        if not isinstance(value, (int, float)):
            raise ValueError(f"{criterion_id} score must be numeric")
        maximum = allowed_criteria[criterion_id]
        if value < 0 or value > maximum:
            raise ValueError(
                f"{criterion_id} score must be between 0 and {maximum}, got {value}"
            )

    validate_usability(grade, schema)


def validate_usability(grade, schema):
    if "usability" not in grade:
        return

    usability = grade["usability"]
    if not isinstance(usability, dict):
        raise ValueError(f"{grade['case_id']}:{grade['variant']} usability must be an object")

    allowed = {item["id"]: item["max"] for item in schema.get("usability_criteria", [])}
    allowed_with_notes = set(allowed) | {"notes"}
    extra = sorted(set(usability) - allowed_with_notes)
    if extra:
        raise ValueError(
            f"{grade['case_id']}:{grade['variant']} has unknown usability fields: "
            + ", ".join(extra)
        )

    for field_id, maximum in allowed.items():
        value = usability.get(field_id, 0)
        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_id} usability score must be numeric")
        if value < 0 or value > maximum:
            raise ValueError(
                f"{field_id} usability score must be between 0 and {maximum}, got {value}"
            )


def total_score(grade, schema):
    validate_grade(grade, schema)
    return round(sum(grade["scores"][item["id"]] for item in schema["criteria"]), 2)


def usability_score(grade, schema):
    validate_grade(grade, schema)
    usability = grade.get("usability")
    if not usability or not usability_is_recorded(grade, schema):
        return None
    return round(
        sum(usability.get(item["id"], 0) for item in schema.get("usability_criteria", [])),
        2,
    )


def usability_is_recorded(grade, schema):
    usability = grade.get("usability", {})
    return bool(usability.get("notes")) or any(
        usability.get(item["id"], 0) > 0 for item in schema.get("usability_criteria", [])
    )


def is_pending_grade(grade):
    scores = grade.get("scores", {})
    flags = grade.get("flags", {})
    return (
        all(value == 0 for value in scores.values())
        and not grade.get("notes")
        and not any(flags.values())
    )


def summarize_grades(grades, schema):
    buckets = {}
    pending = {}
    for grade in grades:
        if is_pending_grade(grade):
            pending.setdefault(grade["variant"], []).append(grade["case_id"])
            continue
        score = total_score(grade, schema)
        manual_usability = usability_score(grade, schema)
        variant = grade["variant"]
        buckets.setdefault(
            variant,
            {
                "count": 0,
                "total_score": 0.0,
                "case_scores": {},
                "usability_count": 0,
                "usability_total": 0.0,
            },
        )
        buckets[variant]["count"] += 1
        buckets[variant]["total_score"] += score
        buckets[variant]["case_scores"][grade["case_id"]] = score
        if manual_usability is not None:
            buckets[variant]["usability_count"] += 1
            buckets[variant]["usability_total"] += manual_usability

    variants = {}
    for variant, bucket in sorted(buckets.items()):
        variants[variant] = {
            "count": bucket["count"],
            "average_score": round(bucket["total_score"] / bucket["count"], 2),
            "case_scores": bucket["case_scores"],
        }
        if bucket["usability_count"]:
            variants[variant]["average_usability"] = round(
                bucket["usability_total"] / bucket["usability_count"],
                2,
            )

    lift = {}
    if "baseline" in variants and "dddjango" in variants:
        baseline = variants["baseline"]["average_score"]
        dddjango = variants["dddjango"]["average_score"]
        absolute = round(dddjango - baseline, 2)
        percent = 0.0 if baseline == 0 else round((absolute / baseline) * 100, 2)
        lift = {"absolute": absolute, "percent": percent}

    return {"variants": variants, "pending": pending, "lift": lift}


def main():
    parser = argparse.ArgumentParser(
        description="Summarize manual Codex plugin evaluation grades."
    )
    parser.add_argument(
        "--schema",
        default="evals/codex/rubrics/grading-schema.json",
        help="Path to grading-schema.json.",
    )
    parser.add_argument("grades", help="Path to grades JSON file.")
    args = parser.parse_args()

    schema = load_json(args.schema)
    grades = load_json(args.grades)
    summary = summarize_grades(grades, schema)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
