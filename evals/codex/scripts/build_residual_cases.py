#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_jsonl(path):
    cases = {}
    for line_number, line in enumerate(Path(path).read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
        cases[case["id"]] = case
    return cases


def dddjango_variant(conformance):
    summary = conformance.get("summary", {})
    return summary.get("dddjango_variant") or "dddjango"


def is_residual_failure(record):
    return bool(
        record.get("failed_rules")
        or record.get("critical_violations")
        or record.get("forbidden_patterns")
    )


def residual_case_ids(conformance, *, variant=None):
    target_variant = variant or dddjango_variant(conformance)
    case_ids = []
    for record in conformance.get("cases", []):
        if record.get("variant") != target_variant:
            continue
        if is_residual_failure(record):
            case_id = record["case_id"]
            if case_id not in case_ids:
                case_ids.append(case_id)
    return case_ids


def build_residual_cases(conformance_path, source_cases_path, output_path, *, variant=None):
    conformance = json.loads(Path(conformance_path).read_text())
    source_cases = load_jsonl(source_cases_path)
    case_ids = residual_case_ids(conformance, variant=variant)
    missing = [case_id for case_id in case_ids if case_id not in source_cases]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"residual case(s) not found in source cases: {joined}")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps(source_cases[case_id], ensure_ascii=False, separators=(",", ":"))
        for case_id in case_ids
    ]
    output.write_text("\n".join(lines) + ("\n" if lines else ""))
    return case_ids


def main():
    parser = argparse.ArgumentParser(
        description="Build a JSONL suite containing failed dddjango conformance cases."
    )
    parser.add_argument("--source-conformance", required=True)
    parser.add_argument("--source-cases", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--variant",
        default="",
        help="Variant to inspect. Defaults to summary.dddjango_variant.",
    )
    args = parser.parse_args()

    case_ids = build_residual_cases(
        args.source_conformance,
        args.source_cases,
        args.output,
        variant=args.variant or None,
    )
    if not case_ids:
        print("residual cases: none")
        return 0
    print(f"residual cases ({len(case_ids)}): {', '.join(case_ids)}")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
