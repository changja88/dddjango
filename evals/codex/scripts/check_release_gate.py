#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_conformance(iteration):
    path = Path(iteration) / "conformance.json"
    if not path.exists():
        raise RuntimeError(
            f"missing conformance report: {path}. "
            "Run the matching evaluation target first, for example "
            "`make eval-conformance` or `make eval-plugin-real`."
        )
    return json.loads(path.read_text())


def failed_gate_items(conformance):
    gate = conformance.get("summary", {}).get("release_gate", {})
    return {
        name: item
        for name, item in gate.items()
        if not item.get("passed", False)
    }


def check_release_gate(iteration):
    conformance = load_conformance(iteration)
    summary = conformance.get("summary", {})
    failed = failed_gate_items(conformance)
    return {
        "iteration": str(iteration),
        "variant": summary.get("dddjango_variant", ""),
        "conformance": summary.get("dddjango_avg_conformance"),
        "required_rule_pass_rate": summary.get("dddjango_required_rule_pass_rate"),
        "critical_violations": summary.get("critical_violations"),
        "forbidden_pattern_count": summary.get("forbidden_pattern_count"),
        "failed": failed,
        "passed": not failed,
    }


def print_result(result):
    status = "PASS" if result["passed"] else "FAIL"
    print(f"release gate: {status}")
    print(f"- iteration: {result['iteration']}")
    print(f"- variant: {result['variant']}")
    print(f"- conformance: {result['conformance']}")
    print(f"- required rule pass rate: {result['required_rule_pass_rate']}")
    print(f"- critical violations: {result['critical_violations']}")
    print(f"- forbidden pattern count: {result['forbidden_pattern_count']}")
    if result["failed"]:
        print("- failed gate items:")
        for name, item in result["failed"].items():
            print(
                f"  - {name}: value={item.get('value')} "
                f"required={item.get('required')}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Check whether an evaluation iteration passes the conformance release gate."
    )
    parser.add_argument("iteration")
    args = parser.parse_args()

    try:
        result = check_release_gate(Path(args.iteration))
    except RuntimeError as exc:
        print(f"release gate: FAIL")
        print(f"- reason: {exc}")
        return 1

    print_result(result)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
