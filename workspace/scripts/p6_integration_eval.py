#!/usr/bin/env python3
"""P6 integration-flow scorer for the dddjango rebuild plan.

This runner reuses the P5 clean/scored mechanics but keeps P6 prompt assembly,
metadata, and guardrail checks separate so P5 completion artifacts stay tied to
their original runner fingerprint.
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import p5_individual_eval as base


VARIANTS = base.VARIANTS
PASS_STATUSES = base.PASS_STATUSES
FAIL_STATUSES = base.FAIL_STATUSES
MODEL_RUN_MODE = "model-backed-installed-runtime-p6-integration"
MODEL_ANSWER_SCHEMA = base.MODEL_ANSWER_SCHEMA
DEFAULT_FORBIDDEN_TEXT = (
    "workspace/reference/",
    "workspace/plan/",
    "workspace/develop/eval/",
    "/Users/hyun/",
    "/private/tmp/",
    "raw/run.json",
    "targeted-suite.json",
)


def metadata_digest_manifest(paths: base.Paths) -> dict[str, str]:
    roots = [
        paths.fixture_root / "cases.json",
        paths.repo_root / "workspace/plan/governance/eval_protocol.md",
        paths.repo_root / "workspace/scripts/p6_integration_eval.py",
        paths.repo_root / "workspace/scripts/p5_individual_eval.py",
        paths.repo_root / "dddjango/.codex-plugin/plugin.json",
        paths.repo_root / "dddjango/skills/source-reference-audit/references/source-governance.md",
        paths.repo_root / "dddjango/skills/workflow-dddjango-subagents/references/role-map.md",
        paths.repo_root / "dddjango/skills/workflow-dddjango-subagents/references/handoff-contract.md",
        paths.repo_root / "dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md",
        Path("/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/.codex-plugin/plugin.json"),
    ]
    manifest: dict[str, str] = {}
    for path in roots:
        if path.is_file():
            manifest[base.display_path(path, paths.repo_root)] = base.sha256_file(path)
    for path in sorted((paths.repo_root / "dddjango/skills").glob("*/SKILL.md")):
        manifest[path.relative_to(paths.repo_root).as_posix()] = base.sha256_file(path)
    return manifest


def expected_outcome_map(case: dict[str, Any]) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    for outcome in case.get("expected_outcomes", []):
        if isinstance(outcome, dict) and isinstance(outcome.get("id"), str):
            outcomes[outcome["id"]] = str(outcome.get("value", ""))
    return outcomes


def required_loaded_skills(oracle: dict[str, Any]) -> list[str]:
    required = oracle.get("required_loaded_skills")
    if isinstance(required, list) and all(isinstance(item, str) for item in required):
        return required
    loaded_skill = oracle.get("loaded_skill")
    return [loaded_skill] if isinstance(loaded_skill, str) else []


def forbidden_loaded_skills(oracle: dict[str, Any]) -> list[str]:
    forbidden = oracle.get("forbidden_loaded_skills")
    if isinstance(forbidden, list) and all(isinstance(item, str) for item in forbidden):
        return forbidden
    return []


def forbidden_answer_text(oracle: dict[str, Any]) -> list[str]:
    configured = oracle.get("forbidden_answer_substrings")
    if isinstance(configured, list) and all(isinstance(item, str) for item in configured):
        return list(dict.fromkeys([*DEFAULT_FORBIDDEN_TEXT, *configured]))
    return list(DEFAULT_FORBIDDEN_TEXT)


def text_contains(text: str, needle: str) -> bool:
    return needle.casefold() in text.casefold()


def score_p6_answer(*, case: dict[str, Any], variant: str, answer: dict[str, Any]) -> dict[str, Any]:
    result = base.score_model_answer(case=case, variant=variant, answer=answer)
    result["run_mode"] = MODEL_RUN_MODE
    oracle = case.get("oracle")
    if not isinstance(oracle, dict):
        return result

    actual_loaded_skill = answer.get("loaded_skill")
    required_skills = required_loaded_skills(oracle)
    missing_required_skills = [
        skill for skill in required_skills if not base.loaded_skill_matches(actual_loaded_skill, skill)
    ]
    result["checks"]["required_loaded_skills"] = {
        "required": required_skills,
        "actual": actual_loaded_skill,
        "missing": missing_required_skills,
        "ok": not missing_required_skills,
    }
    if missing_required_skills:
        result["failure_semantics"].append("handoff-boundary-missing")

    forbidden_skills = [
        skill for skill in forbidden_loaded_skills(oracle) if base.loaded_skill_matches(actual_loaded_skill, skill)
    ]
    result["checks"]["forbidden_loaded_skills"] = {
        "forbidden": forbidden_loaded_skills(oracle),
        "actual": actual_loaded_skill,
        "matched": forbidden_skills,
        "ok": not forbidden_skills,
    }
    if forbidden_skills:
        result["failure_semantics"].append("skill-responsibility-intrusion")

    answer_text = str(answer.get("answer_text", ""))
    leakage_hits = [marker for marker in forbidden_answer_text(oracle) if text_contains(answer_text, marker)]
    result["checks"]["source_runtime_leakage"] = {
        "forbidden_count": len(forbidden_answer_text(oracle)),
        "hit_count": len(leakage_hits),
        "hit_digests": [base.sha256_text(marker) for marker in leakage_hits],
        "ok": not leakage_hits,
    }
    if leakage_hits:
        result["failure_semantics"].append("source-leakage")

    if result["failure_semantics"]:
        result["status"] = "partial" if 0 < float(result.get("score") or 0) < 1 else "fail"
        if result["status"] == "pass":
            result["status"] = "fail"
    return result


def score_variant(*, case: dict[str, Any], variant: str) -> dict[str, Any]:
    result = base.score_variant(case=case, variant=variant)
    result["run_mode"] = "fixture-scored-p6-preflight"
    oracle = case.get("oracle")
    answer = case.get("answers", {}).get(variant) if isinstance(case.get("answers"), dict) else None
    if isinstance(oracle, dict) and isinstance(answer, dict):
        return score_p6_answer(case=case, variant=variant, answer=answer)
    return result


def model_answer_schema_path(output_dir: Path) -> Path:
    path = output_dir / "raw" / "model-answer.schema.json"
    base.write_json(path, MODEL_ANSWER_SCHEMA)
    return path


def model_case_prompt(case: dict[str, Any]) -> str:
    outcomes = expected_outcome_map(case)
    oracle = case.get("oracle") if isinstance(case.get("oracle"), dict) else {}
    required_claims = oracle.get("required_claims", []) if isinstance(oracle, dict) else []
    claim_lines = [
        f"- {claim}: {outcomes.get(claim, 'satisfy this integration criterion')}"
        for claim in required_claims
        if isinstance(claim, str)
    ]
    required_skills = required_loaded_skills(oracle) if isinstance(oracle, dict) else []
    return "\n".join(
        [
            "P6 dddjango integration eval. Answer the user's request using the installed runtime instructions that apply.",
            "Return only JSON matching the provided output schema.",
            "Set loaded_skill to the coordinating skill plus any dddjango skills explicitly used or handed off, separated by semicolons.",
            "For claims, include only the identifiers below when your answer satisfies the criterion:",
            *claim_lines,
            "Do not claim actual file edits, command execution, tests, subagent execution, runtime evidence, or broader phase completion unless it happened in this answer.",
            "Do not expose source-authoring paths, private evaluation material, run artifact paths, or non-public validation notes in answer_text.",
            "",
            f"Required loaded/handoff skill ids for this case: {', '.join(required_skills) or 'none'}",
            f"User prompt: {case.get('prompt', '')}",
        ]
    )


def build_model_command(
    *,
    runtime_channel: str,
    variant: str,
    case_workdir: Path,
    final_path: Path,
    schema_path: Path,
    prompt: str,
    model: str | None = None,
) -> list[str]:
    return base.build_model_command(
        runtime_channel=runtime_channel,
        variant=variant,
        case_workdir=case_workdir,
        final_path=final_path,
        schema_path=schema_path,
        prompt=prompt,
        model=model,
    )


def default_model_runner(command: list[str], *, cwd: Path, final_path: Path) -> subprocess.CompletedProcess[str]:
    del final_path
    cwd.mkdir(parents=True, exist_ok=True)
    return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)


def model_run_one(
    paths: base.Paths,
    *,
    case_id: str,
    variant: str,
    run_id: str,
    runtime_channel: str,
    work_root: Path,
    runner: Callable[..., Any] | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    if variant not in VARIANTS:
        raise base.EvalError(f"variant must be one of {', '.join(VARIANTS)}")
    case = base.case_by_id(paths.fixture_root, case_id)
    schema_path = model_answer_schema_path(paths.output_dir)
    case_workdir = work_root / run_id / f"{case_id}-{variant}"
    final_path = case_workdir / "final.json"
    stdout_path = paths.output_dir / "raw" / "model-executions" / f"{case_id}.{variant}.stdout.jsonl"
    stderr_path = paths.output_dir / "raw" / "model-executions" / f"{case_id}.{variant}.stderr.txt"
    command = build_model_command(
        runtime_channel=runtime_channel,
        variant=variant,
        case_workdir=case_workdir,
        final_path=final_path,
        schema_path=schema_path,
        prompt=model_case_prompt(case),
        model=model,
    )

    executor = runner or default_model_runner
    completed = executor(command, cwd=case_workdir, final_path=final_path)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(getattr(completed, "stdout", ""), encoding="utf-8")
    stderr_path.write_text(getattr(completed, "stderr", ""), encoding="utf-8")

    execution = {
        "command": command,
        "cwd": case_workdir.as_posix(),
        "returncode": getattr(completed, "returncode", 1),
        "stdout_path": base.display_path(stdout_path, paths.repo_root),
        "stderr_path": base.display_path(stderr_path, paths.repo_root),
        "final_path": final_path.as_posix(),
        "runtime_channel": runtime_channel,
        "variant_runtime": "installed-plugin" if variant == "with-plugin" else "baseline-ignore-user-config",
    }

    if execution["returncode"] != 0:
        result = {
            "case_id": case_id,
            "variant": variant,
            "surface": case.get("surface"),
            "skill_under_test": case.get("skill_under_test"),
            "expected_loaded_skill": case.get("oracle", {}).get("loaded_skill") if isinstance(case.get("oracle"), dict) else None,
            "actual_loaded_skill": None,
            "status": "not-scored",
            "score": None,
            "failure_semantics": ["model-runner-error"],
            "checks": {},
            "model_backed": True,
        }
    elif not final_path.is_file():
        result = {
            "case_id": case_id,
            "variant": variant,
            "surface": case.get("surface"),
            "skill_under_test": case.get("skill_under_test"),
            "expected_loaded_skill": case.get("oracle", {}).get("loaded_skill") if isinstance(case.get("oracle"), dict) else None,
            "actual_loaded_skill": None,
            "status": "not-scored",
            "score": None,
            "failure_semantics": ["missing-answer"],
            "checks": {},
            "model_backed": True,
        }
    else:
        try:
            answer = base.parse_model_answer(final_path.read_text(encoding="utf-8"))
        except base.EvalError:
            result = {
                "case_id": case_id,
                "variant": variant,
                "surface": case.get("surface"),
                "skill_under_test": case.get("skill_under_test"),
                "expected_loaded_skill": case.get("oracle", {}).get("loaded_skill") if isinstance(case.get("oracle"), dict) else None,
                "actual_loaded_skill": None,
                "status": "not-scored",
                "score": None,
                "failure_semantics": ["malformed-answer"],
                "checks": {},
                "model_backed": True,
            }
        else:
            result = score_p6_answer(case=case, variant=variant, answer=answer)

    result["run_id"] = run_id
    result["run_mode"] = MODEL_RUN_MODE
    result["execution"] = execution
    result["metadata_digests"] = metadata_digest_manifest(paths)
    result["metadata_digest"] = base.digest_for_data(result["metadata_digests"])
    base.write_json(paths.output_dir / "raw" / "one.json", result)
    return result


def run_bucket(paths: base.Paths, bucket: str, run_id: str, *, model_backed: bool = False, **model_kwargs: Any) -> dict[str, Any]:
    cases = [case for case in base.load_cases(paths.fixture_root) if case.get("bucket") == bucket]
    if not cases:
        raise base.EvalError(f"bucket not found or empty: {bucket}")
    variants = model_kwargs.pop("variants", VARIANTS)
    flake_history = model_kwargs.pop("flake_history", None)
    results: list[dict[str, Any]] = []
    for case in cases:
        for variant in variants:
            if model_backed:
                results.append(model_run_one(paths, case_id=str(case["id"]), variant=variant, run_id=run_id, **model_kwargs))
            else:
                results.append(score_variant(case=case, variant=variant))

    status_counts = {"pass": 0, "partial": 0, "fail": 0, "not-scored": 0}
    for result in results:
        status_counts[result["status"]] += 1
    hard_failures = [result for result in results if result["status"] in FAIL_STATUSES]
    raw = {
        "schema_version": "p6-integration-eval-run/v1",
        "run_id": run_id,
        "bucket": bucket,
        "fixture_root": paths.fixture_root.relative_to(paths.repo_root).as_posix(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "variants": list(variants),
        "run_mode": MODEL_RUN_MODE if model_backed else "fixture-scored-p6-preflight",
        "model_backed": model_backed,
        "runtime_parity_precondition": "complete",
        "runtime_channel": model_kwargs.get("runtime_channel") if model_backed else None,
        "runner_destination": "codex-exec" if model_backed else "fixture",
        "prompt_assembly_source": "workspace/scripts/p6_integration_eval.py:model_case_prompt",
        "oracle_model_config": "deterministic local oracle from P6 cases.json",
        "scoring_prompt_config": "deterministic scorer over structured model answer JSON with P6 guardrails",
        "flake_history": flake_history or ({"iterations": 1, "variance_status": "single-pass provisional"} if model_backed else None),
        "status": "fail" if hard_failures else "pass",
        "status_counts": status_counts,
        "hard_failure_count": len(hard_failures),
        "case_count": len(cases),
        "result_count": len(results),
        "metadata_digests": metadata_digest_manifest(paths),
        "results": results,
    }
    raw["metadata_digest"] = base.digest_for_data(raw["metadata_digests"])
    raw["raw_digest"] = base.digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})
    base.write_json(paths.output_dir / "raw" / "run.json", raw)
    return raw


def run_targeted_suite(
    paths: base.Paths,
    *,
    bucket: str,
    run_id: str,
    iterations: int,
    model_backed: bool = False,
    **model_kwargs: Any,
) -> dict[str, Any]:
    if iterations < 1:
        raise base.EvalError("iterations must be >= 1")
    runs = []
    for iteration in range(1, iterations + 1):
        iteration_run_id = f"{run_id}-targeted-{iteration}"
        raw = run_bucket(
            paths,
            bucket,
            iteration_run_id,
            model_backed=model_backed,
            flake_history={"iterations": iterations, "current_iteration": iteration, "variance_status": "pending"} if model_backed else None,
            **model_kwargs,
        )
        iteration_path = paths.output_dir / "raw" / f"targeted-run-{iteration}.json"
        base.write_json(iteration_path, raw)
        runs.append(
            {
                "iteration": iteration,
                "run_id": iteration_run_id,
                "artifact": base.display_path(iteration_path, paths.repo_root),
                "status": raw["status"],
                "status_counts": raw["status_counts"],
                "metadata_digest": raw["metadata_digest"],
            }
        )
    statuses = [run["status"] for run in runs]
    variance_status = "stable-pass" if statuses and all(status == "pass" for status in statuses) else "needs-classification"
    summary = {
        "schema_version": "p6-integration-model-targeted-suite/v1" if model_backed else "p6-integration-targeted-suite/v1",
        "run_id": run_id,
        "bucket": bucket,
        "iterations": iterations,
        "variants": list(model_kwargs.get("variants", VARIANTS)),
        "status": "pass" if variance_status == "stable-pass" else "fail",
        "model_backed": model_backed,
        "runtime_channel": model_kwargs.get("runtime_channel") if model_backed else None,
        "variance_status": variance_status,
        "runs": runs,
    }
    base.write_json(paths.output_dir / "raw" / "targeted-suite.json", summary)
    return summary


def render_report(output_dir: Path) -> dict[str, Any]:
    raw_path = output_dir / "raw" / "run.json"
    if not raw_path.is_file():
        raise base.EvalError(f"missing raw run artifact: {raw_path}")
    raw = base.read_json(raw_path)
    source_digest = base.digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})
    rows = []
    report_results = []
    for result in raw.get("results", []):
        semantics = ", ".join(result["failure_semantics"]) or "-"
        rows.append(
            "<tr>"
            f"<td>{html.escape(result['case_id'])}</td>"
            f"<td>{html.escape(result['variant'])}</td>"
            f"<td>{html.escape(str(result.get('surface')))}</td>"
            f"<td>{html.escape(str(result.get('skill_under_test')))}</td>"
            f"<td>{html.escape(result['status'])}</td>"
            f"<td>{html.escape(str(result.get('actual_loaded_skill')))}</td>"
            f"<td>{html.escape(semantics)}</td>"
            "</tr>"
        )
        report_results.append(
            {
                "case_id": result["case_id"],
                "variant": result["variant"],
                "surface": result.get("surface"),
                "skill_under_test": result.get("skill_under_test"),
                "status": result["status"],
                "actual_loaded_skill": result.get("actual_loaded_skill"),
                "failure_semantics": result["failure_semantics"],
            }
        )
    report_json = {
        "schema_version": "p6-integration-eval-report/v1",
        "run_id": raw["run_id"],
        "source_raw_path": raw_path.as_posix(),
        "source_raw_digest": source_digest,
        "status_counts": raw["status_counts"],
        "model_backed": raw.get("model_backed"),
        "runtime_parity_precondition": raw.get("runtime_parity_precondition"),
        "metadata_digest": raw.get("metadata_digest"),
        "results": report_results,
    }
    html_text = "\n".join(
        [
            "<!doctype html>",
            "<html><head><meta charset=\"utf-8\"><title>dddjango P6 integration eval report</title></head>",
            "<body>",
            f"<h1>{html.escape(raw['run_id'])}</h1>",
            f"<p>Model backed: {html.escape(str(raw.get('model_backed')))}</p>",
            f"<p>Runtime parity precondition: {html.escape(str(raw.get('runtime_parity_precondition')))}</p>",
            f"<p>Raw digest: {html.escape(source_digest)}</p>",
            "<table>",
            "<thead><tr><th>case</th><th>variant</th><th>surface</th><th>skill under test</th><th>status</th><th>actual loaded skill</th><th>failure semantics</th></tr></thead>",
            "<tbody>",
            *rows,
            "</tbody></table>",
            "</body></html>",
        ]
    )
    report_html = output_dir / "report" / "report.html"
    report_html.parent.mkdir(parents=True, exist_ok=True)
    report_html.write_text(html_text, encoding="utf-8")
    report_json["report_html_digest"] = base.sha256_file(report_html)
    base.write_json(output_dir / "report" / "report.json", report_json)
    return report_json


def validate_run(output_dir: Path, repo_root: Path) -> dict[str, Any]:
    result = base.validate_run(output_dir, repo_root)
    result["schema_version"] = "p6-integration-eval-validation/v1"
    raw_path = output_dir / "raw" / "run.json"
    failures = list(result.get("failures", []))
    if raw_path.is_file():
        raw = base.read_json(raw_path)
        forbidden_failure_classes = {
            "wrong-routing",
            "forbidden-overclaim",
            "handoff-boundary-missing",
            "skill-responsibility-intrusion",
            "source-leakage",
        }
        guardrail_hits = [
            item
            for scored in raw.get("results", [])
            for item in scored.get("failure_semantics", [])
            if item in forbidden_failure_classes
        ]
        if guardrail_hits:
            failures.append({"kind": "p6-guardrail-failure-present", "count": len(guardrail_hits)})
    result["failures"] = failures
    result["status"] = "fail" if failures else "pass"
    base.write_json(output_dir / "validation" / "validate-run.json", result)
    return result


def parse_variants(value: str) -> tuple[str, ...]:
    return base.parse_variants(value)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-root", default="workspace/develop/eval/fixtures/integration-flows")
    parser.add_argument("--output-dir", default="workspace/develop/eval/runs/p6-integration-flows-fixture")
    parser.add_argument("--repo-root", default=".")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_bucket_parser = subparsers.add_parser("run-bucket")
    run_bucket_parser.add_argument("--bucket", default="integration-flows")
    run_bucket_parser.add_argument("--run-id", default="p6-integration-flows-fixture")

    targeted_parser = subparsers.add_parser("run-targeted-suite")
    targeted_parser.add_argument("--bucket", default="integration-flows")
    targeted_parser.add_argument("--run-id", default="p6-integration-flows-fixture")
    targeted_parser.add_argument("--iterations", type=int, default=2)

    model_bucket_parser = subparsers.add_parser("model-run-bucket")
    model_bucket_parser.add_argument("--bucket", default="integration-flows")
    model_bucket_parser.add_argument("--run-id", default="p6-integration-flows-model")
    model_bucket_parser.add_argument("--runtime-channel", choices=("external", "ollama", "lmstudio"), default="external")
    model_bucket_parser.add_argument("--work-root", default="/private/tmp/dddjango-p6-model")
    model_bucket_parser.add_argument("--model")
    model_bucket_parser.add_argument("--variants", default="with-plugin")

    model_targeted_parser = subparsers.add_parser("model-run-targeted-suite")
    model_targeted_parser.add_argument("--bucket", default="integration-flows")
    model_targeted_parser.add_argument("--run-id", default="p6-integration-flows-model")
    model_targeted_parser.add_argument("--iterations", type=int, default=2)
    model_targeted_parser.add_argument("--runtime-channel", choices=("external", "ollama", "lmstudio"), default="external")
    model_targeted_parser.add_argument("--work-root", default="/private/tmp/dddjango-p6-model")
    model_targeted_parser.add_argument("--model")
    model_targeted_parser.add_argument("--variants", default="with-plugin")

    subparsers.add_parser("render-report")
    subparsers.add_parser("validate-run")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    paths = base.Paths(
        fixture_root=(repo_root / args.fixture_root).resolve(),
        output_dir=(repo_root / args.output_dir).resolve(),
        repo_root=repo_root,
    )
    try:
        if args.command == "run-bucket":
            raw = run_bucket(paths, args.bucket, args.run_id)
            print(json.dumps({"status": raw["status"], "status_counts": raw["status_counts"]}, ensure_ascii=False))
            return 0 if raw["status"] == "pass" else 1
        if args.command == "run-targeted-suite":
            summary = run_targeted_suite(paths, bucket=args.bucket, run_id=args.run_id, iterations=args.iterations)
            print(json.dumps({"status": summary["status"], "iterations": summary["iterations"]}, ensure_ascii=False))
            return 0 if summary["status"] == "pass" else 1
        if args.command == "model-run-bucket":
            raw = run_bucket(
                paths,
                args.bucket,
                args.run_id,
                model_backed=True,
                runtime_channel=args.runtime_channel,
                work_root=Path(args.work_root),
                model=args.model,
                variants=parse_variants(args.variants),
            )
            print(json.dumps({"status": raw["status"], "status_counts": raw["status_counts"]}, ensure_ascii=False))
            return 0 if raw["status"] == "pass" else 1
        if args.command == "model-run-targeted-suite":
            summary = run_targeted_suite(
                paths,
                bucket=args.bucket,
                run_id=args.run_id,
                iterations=args.iterations,
                model_backed=True,
                runtime_channel=args.runtime_channel,
                work_root=Path(args.work_root),
                model=args.model,
                variants=parse_variants(args.variants),
            )
            print(
                json.dumps(
                    {
                        "status": summary["status"],
                        "iterations": summary["iterations"],
                        "variance_status": summary["variance_status"],
                    },
                    ensure_ascii=False,
                )
            )
            return 0 if summary["status"] == "pass" else 1
        if args.command == "render-report":
            report = render_report(paths.output_dir)
            print(json.dumps({"status": "pass", "report": report["source_raw_path"]}, ensure_ascii=False))
            return 0
        if args.command == "validate-run":
            validation = validate_run(paths.output_dir, repo_root)
            print(json.dumps({"status": validation["status"], "failures": validation["failures"]}, ensure_ascii=False))
            return 0 if validation["status"] == "pass" else 1
    except base.EvalError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
