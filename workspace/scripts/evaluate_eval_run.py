#!/usr/bin/env python3
"""Evaluate completed dddjango eval runs against private answer oracles."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import eval_run_common as common
import eval_run_identity as run_identity
import workflow_execution_gate as workflow_gate


REPO_ROOT = common.REPO_ROOT
EVAL_ROOT = common.EVAL_ROOT
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING = "high"
MAX_ARTIFACT_CHARS = 80_000

OUTPUT_SCHEMA = """{
  "caseId": "case-id",
  "answerOracleEvaluated": true,
  "baseline": {
    "score": "0 / 5",
    "verdict": "fail",
    "evaluation_summary": "answer oracle에 근거한 한국어 한 문장 요약.",
    "evaluation": "answer oracle에 근거한 한국어 평가 설명."
  },
  "with_dddjango": {
    "score": "0 / 5",
    "verdict": "fail",
    "evaluation_summary": "answer oracle에 근거한 한국어 한 문장 요약.",
    "evaluation": "answer oracle에 근거한 한국어 평가 설명."
  },
  "observations": [
    "delta, evidence, leakage, hard gate 상태에 대한 한국어 실행 단위 관찰."
  ],
  "status": "ok"
}"""

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", choices=common.BUCKETS, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--case", action="append", help="Case id to evaluate. Repeatable.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning", default=DEFAULT_REASONING)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--rerun", action="store_true")
    return parser.parse_args(argv)


def validate_run_id(run_id: str) -> str:
    run_identity.validate_production_run_id(run_id)
    return run_id


def resolved_under(root: Path, *parts: str | Path, description: str) -> Path:
    root_resolved = root.resolve()
    path = root.joinpath(*parts)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise SystemExit(f"{description} escapes intended root: {path}") from exc
    return path


def run_command(
    command: list[str],
    *,
    prompt: str | None,
    cwd: Path,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("NO_COLOR", "1")
    return subprocess.run(
        command,
        cwd=cwd,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        env=env,
        check=False,
    )


def response_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def required_text(path: Path, description: str) -> str:
    if not path.is_file():
        raise SystemExit(f"missing {description}: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def excerpt_text(text: str) -> str:
    if len(text) <= MAX_ARTIFACT_CHARS:
        return text
    return text[:MAX_ARTIFACT_CHARS] + f"\n[TRUNCATED after {MAX_ARTIFACT_CHARS} characters]\n"


def artifact_section(title: str, path: Path, text: str) -> str:
    return (
        f"### {title}\n"
        f"Path: {path.as_posix()}\n"
        "```text\n"
        f"{excerpt_text(text).rstrip()}\n"
        "```\n"
    )


def binary_looking(contents: bytes) -> bool:
    sample = contents[:4096]
    if b"\0" in sample:
        return True
    if not sample:
        return False
    text = sample.decode("utf-8", errors="replace")
    replacement_ratio = text.count("\ufffd") / max(len(text), 1)
    if replacement_ratio > 0.05:
        return True
    control_chars = sum(
        1 for char in text if ord(char) < 32 and char not in "\n\r\t\f\b"
    )
    return control_chars / max(len(text), 1) > 0.30


def read_text_artifact(path: Path) -> str | None:
    contents = path.read_bytes()
    if binary_looking(contents):
        return None
    return contents.decode("utf-8", errors="replace")


def optional_code_artifacts(run_dir: Path, case_id: str) -> list[tuple[str, Path, str]]:
    artifacts: list[tuple[str, Path, str]] = []
    base = run_dir / "code" / case_id
    for variant in common.VARIANTS:
        variant_root = base / variant
        if not variant_root.is_dir():
            continue
        variant_root_resolved = variant_root.resolve()
        paths = sorted(path for path in variant_root.rglob("*") if path.is_file())
        for path in paths:
            resolved = path.resolve(strict=False)
            try:
                rel_path = resolved.relative_to(variant_root_resolved)
            except ValueError:
                continue
            text = read_text_artifact(path)
            if text is None:
                continue
            display_path = Path("code") / case_id / variant / rel_path
            artifacts.append((f"{variant} {rel_path.as_posix()}", display_path, text))
    return artifacts


def optional_workflow_trace_artifacts(run_dir: Path, case_id: str) -> list[tuple[str, Path, str]]:
    artifacts: list[tuple[str, Path, str]] = []
    for variant in common.VARIANTS:
        rel_path = Path("raw") / f"{case_id}-{variant}-subagent-trace.json"
        path = run_dir / rel_path
        if path.is_file():
            artifacts.append((f"{variant} trace", rel_path, path.read_text(encoding="utf-8", errors="replace")))
    return artifacts


def build_prompt(
    *,
    bucket: str,
    case_id: str,
    public_case: str,
    answer_oracle: str,
    baseline_output: str,
    with_ddjango_output: str,
    code_artifacts: list[tuple[str, Path, str]],
    workflow_trace_artifacts: list[tuple[str, Path, str]],
) -> str:
    with_variant = common.VARIANTS[1]
    sections = [
        "EVALUATOR-ONLY ANSWER ORACLE",
        "",
        "You are privately evaluating a completed dddjango eval run.",
        "Use the evaluator-only answer oracle below as the scoring authority.",
        "Compare the baseline output and with-ddjango output against the public case and oracle.",
        "All human-readable evaluator strings MUST be written in Korean.",
        "한국어로 작성해야 하는 필드: baseline.evaluation_summary, baseline.evaluation, "
        "with_dddjango.evaluation_summary, with_dddjango.evaluation, observations.",
        "Keep allowed enum-like fields in the schema language, such as verdict and status.",
        "Return only one JSON object matching the exact output schema. Do not include prose.",
        "",
        "Exact output schema:",
        "```json",
        OUTPUT_SCHEMA,
        "```",
        "",
        f"Bucket: {bucket}",
        f"Case ID: {case_id}",
        "",
        artifact_section("Public case", Path(f"cases/plugin/public/{case_id}.md"), public_case),
        artifact_section("Evaluator-only answer oracle", Path(f"answer/{case_id}.yaml"), answer_oracle),
        artifact_section("Baseline output", Path(f"raw/{case_id}-baseline.txt"), baseline_output),
        artifact_section(
            "With-ddjango output",
            Path(f"raw/{case_id}-{with_variant}.txt"),
            with_ddjango_output,
        ),
    ]
    if workflow_trace_artifacts:
        sections.extend(
            [
                "Workflow subagent trace summary",
                "Use this only as supporting evidence about execution trace availability and "
                "claim/evidence consistency. Do not use rolesMentioned alone as scoring proof; "
                "responsibility split quality must be judged from the final response and answer oracle.",
                "If the workflow oracle includes workflow_execution_expectation, use it to judge "
                "whether subagents were required, forbidden, consent-gated, or optional, and whether "
                "responsibility assignment was concrete enough.",
                "",
            ]
        )
    for title, path, text in workflow_trace_artifacts:
        sections.append(artifact_section(f"Workflow trace: {title}", path, text))
    for title, path, text in code_artifacts:
        sections.append(artifact_section(f"Code artifact: {title}", path, text))
    return "\n".join(sections)


def codex_evaluator_command(*, model: str, reasoning: str) -> list[str]:
    return [
        "codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "-s",
        "read-only",
        "-m",
        model,
        "-c",
        f'model_reasoning_effort="{reasoning}"',
        "-",
    ]


def write_command_artifact(path: Path, command: list[str]) -> None:
    common.write_text(path, shlex.join(command) + "\n")


def write_raw_evaluator_artifacts(
    *,
    raw_dir: Path,
    case_id: str,
    command: list[str],
    stdout: str,
    stderr: str,
    exit_text: str,
) -> None:
    prefix = f"{case_id}-answer-oracle-evaluation"
    common.write_text(raw_dir / f"{prefix}.raw.txt", stdout)
    common.write_text(raw_dir / f"{prefix}.stderr.txt", stderr)
    write_command_artifact(raw_dir / f"{prefix}-command.txt", command)
    common.write_text(raw_dir / f"{prefix}-exit.txt", exit_text)


def canonical_oracle_path(raw_dir: Path, case_id: str) -> Path:
    return raw_dir / f"{case_id}-answer-oracle-evaluation.json"


def parse_and_validate(stdout: str, case_id: str) -> dict[str, Any]:
    try:
        oracle = common.extract_json_object(stdout)
    except ValueError as exc:
        raise SystemExit(f"{case_id}: evaluator stdout did not contain a JSON object") from exc
    normalize_oracle(oracle)
    error = common.validate_oracle_schema(oracle, case_id)
    if error is not None:
        raise SystemExit(f"{case_id}: invalid oracle schema: {error}")
    language_error = validate_oracle_language(oracle)
    if language_error is not None:
        raise SystemExit(f"{case_id}: invalid oracle language: {language_error}")
    return oracle


def load_workflow_trace(raw_dir: Path, case_id: str, variant: str) -> dict[str, Any]:
    path = raw_dir / f"{case_id}-{variant}-subagent-trace.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"traceStatus": "missing trace"}
    if not isinstance(value, dict):
        return {"traceStatus": "missing trace"}
    return value


def variant_oracle_key(variant: str) -> str:
    return "with_dddjango" if variant == common.VARIANTS[1] else variant


def apply_workflow_execution_gate(
    *,
    oracle: dict[str, Any],
    answer_oracle: str,
    raw_dir: Path,
    case_id: str,
) -> None:
    for variant in common.VARIANTS:
        key = variant_oracle_key(variant)
        variant_oracle = oracle.get(key)
        if not isinstance(variant_oracle, dict):
            continue

        gate = workflow_gate.gate_findings(
            answer_text=answer_oracle,
            trace=load_workflow_trace(raw_dir, case_id, variant),
            case_id=case_id,
            variant=variant,
        )
        if not gate.findings:
            continue

        finding_text = "; ".join(gate.findings)
        variant_oracle["score"] = "0 / 5"
        variant_oracle["verdict"] = "fail"
        variant_oracle["evaluation_summary"] = (
            f"workflow 실행 모드 hard gate 위반: {finding_text}"
        )
        existing = str(variant_oracle.get("evaluation") or "").strip()
        variant_oracle["evaluation"] = (
            f"workflow 실행 모드 hard gate 위반: {finding_text}"
            + (f"\n\n기존 평가: {existing}" if existing else "")
        )

        observations = oracle.get("observations")
        if not isinstance(observations, list):
            observations = []
            oracle["observations"] = observations
        observations.append(f"workflow 실행 모드 hard gate: {finding_text}")


def contains_korean(text: object) -> bool:
    return bool(re.search(r"[가-힣]", str(text or "")))


def validate_oracle_language(oracle: dict[str, Any]) -> str | None:
    for variant_key in ("baseline", "with_dddjango"):
        variant_oracle = oracle.get(variant_key)
        if not isinstance(variant_oracle, dict):
            continue
        for field in ("evaluation_summary", "evaluation"):
            if not contains_korean(variant_oracle.get(field)):
                return f"{variant_key}.{field} must include Korean"

    observations = oracle.get("observations")
    if isinstance(observations, list):
        for index, observation in enumerate(observations):
            if not contains_korean(observation):
                return f"observations[{index}] must include Korean"
    return None


def normalize_oracle(oracle: dict[str, Any]) -> None:
    for variant_key in ("baseline", "with_dddjango"):
        variant_oracle = oracle.get(variant_key)
        if not isinstance(variant_oracle, dict):
            continue
        evaluation = variant_oracle.get("evaluation")
        summary = variant_oracle.get("evaluation_summary")
        if common.has_non_empty_text(evaluation) and not common.has_non_empty_text(summary):
            variant_oracle["evaluation_summary"] = evaluation
        elif common.has_non_empty_text(summary) and not common.has_non_empty_text(evaluation):
            variant_oracle["evaluation"] = summary


def evaluate_case(
    *,
    bucket: common.BucketPaths,
    run_dir: Path,
    raw_dir: Path,
    case_path: Path,
    model: str,
    reasoning: str,
    timeout_seconds: int,
    rerun: bool,
) -> None:
    case_id = case_path.stem
    canonical_path = canonical_oracle_path(raw_dir, case_id)
    if canonical_path.exists() and not rerun:
        print(f"skip existing {case_id}")
        return
    canonical_path.unlink(missing_ok=True)

    public_case = required_text(case_path, "public case")
    answer_oracle = required_text(bucket.answer_dir / f"{case_id}.yaml", "answer oracle")
    baseline_output = required_text(raw_dir / f"{case_id}-baseline.txt", "baseline output")
    with_variant = common.VARIANTS[1]
    with_ddjango_output = required_text(
        raw_dir / f"{case_id}-{with_variant}.txt",
        "with-ddjango output",
    )
    code_artifacts = optional_code_artifacts(run_dir, case_id) if bucket.bucket == "code" else []
    workflow_trace_artifacts = (
        optional_workflow_trace_artifacts(run_dir, case_id) if bucket.bucket == "workflow" else []
    )
    prompt = build_prompt(
        bucket=bucket.bucket,
        case_id=case_id,
        public_case=public_case,
        answer_oracle=answer_oracle,
        baseline_output=baseline_output,
        with_ddjango_output=with_ddjango_output,
        code_artifacts=code_artifacts,
        workflow_trace_artifacts=workflow_trace_artifacts,
    )
    command = codex_evaluator_command(model=model, reasoning=reasoning)

    try:
        result = run_command(
            command,
            prompt=prompt,
            cwd=REPO_ROOT,
            timeout_seconds=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        write_raw_evaluator_artifacts(
            raw_dir=raw_dir,
            case_id=case_id,
            command=command,
            stdout=response_text(exc.stdout),
            stderr=response_text(exc.stderr),
            exit_text=f"timeout after {timeout_seconds}s\n",
        )
        raise SystemExit(f"{case_id}: evaluator timed out after {timeout_seconds}s") from exc

    write_raw_evaluator_artifacts(
        raw_dir=raw_dir,
        case_id=case_id,
        command=command,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_text=str(result.returncode) + "\n",
    )
    oracle = parse_and_validate(result.stdout, case_id)
    if bucket.bucket == "workflow":
        apply_workflow_execution_gate(
            oracle=oracle,
            answer_oracle=answer_oracle,
            raw_dir=raw_dir,
            case_id=case_id,
        )
    common.write_text(
        canonical_path,
        json.dumps(oracle, ensure_ascii=False, indent=2) + "\n",
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_id = validate_run_id(args.run_id)
    identity = run_identity.parse_run_id(run_id)
    if identity.bucket != args.bucket:
        raise SystemExit(
            f"run id bucket mismatch: run id bucket={identity.bucket}, --bucket={args.bucket}"
        )
    bucket = common.bucket_paths(args.bucket)
    cases = common.selected_case_paths(args.bucket, args.case)
    run_dir = resolved_under(bucket.runs_dir, run_id, description="run path")
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    for case_path in cases:
        evaluate_case(
            bucket=bucket,
            run_dir=run_dir,
            raw_dir=raw_dir,
            case_path=case_path,
            model=args.model,
            reasoning=args.reasoning,
            timeout_seconds=args.timeout_seconds,
            rerun=args.rerun,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
