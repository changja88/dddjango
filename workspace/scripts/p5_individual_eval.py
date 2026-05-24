#!/usr/bin/env python3
"""P5 individual-skill fixture scorer for the dddjango rebuild plan.

This runner is intentionally local and deterministic. It scores the P5
individual-skill matrix against explicit answer/oracle fixture data, records
current-file digests in run metadata, and validates raw/report consistency.
It is not model-backed runtime evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


VARIANTS = ("baseline", "with-plugin")
PASS_STATUSES = {"pass"}
FAIL_STATUSES = {"partial", "fail", "not-scored"}
MODEL_RUN_MODE = "model-backed-installed-runtime"
MODEL_ANSWER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["loaded_skill", "claims", "overclaims", "answer_text"],
    "properties": {
        "loaded_skill": {"type": "string"},
        "claims": {
            "type": "array",
            "items": {"type": "string"},
        },
        "overclaims": {"type": "boolean"},
        "answer_text": {"type": "string"},
    },
}
INSTALLED_CACHE_ROOT = Path("/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10")
REDACTED_PATH_MARKERS = ("<repo-root>", "<installed-cache-root>", "<home>", "<tmp>")
LOCAL_LEAK_PATTERNS = ("/Users/hyun", "/private/tmp", "__FORBIDDEN_LOCAL_PATH_SENTINEL__", "__PRIVATE_FIELD_SENTINEL__")


class EvalError(Exception):
    """Raised for command contract errors."""


@dataclass(frozen=True)
class Paths:
    fixture_root: Path
    output_dir: Path
    repo_root: Path


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_for_data(data: Any) -> str:
    return sha256_text(canonical_json(data))


def redact_local_paths(text: str, repo_root: Path | None = None) -> str:
    redacted = text
    if repo_root is not None:
        redacted = redacted.replace(repo_root.as_posix(), "<repo-root>")
    redacted = redacted.replace(INSTALLED_CACHE_ROOT.as_posix(), "<installed-cache-root>")
    redacted = redacted.replace(Path.home().as_posix(), "<home>")
    redacted = redacted.replace("/private/tmp", "<tmp>")
    redacted = redacted.replace("/tmp", "<tmp>")
    return redacted


def redact_nested_paths(value: Any, repo_root: Path | None = None) -> Any:
    if isinstance(value, str):
        return redact_local_paths(value, repo_root)
    if isinstance(value, list):
        return [redact_nested_paths(item, repo_root) for item in value]
    if isinstance(value, dict):
        return {key: redact_nested_paths(item, repo_root) for key, item in value.items()}
    return value


def contains_unredacted_local_path(text: str) -> bool:
    return any(marker in text for marker in LOCAL_LEAK_PATTERNS)


def safe_artifact_path(path: Path, repo_root: Path | None = None) -> str:
    resolved = path.resolve()
    if repo_root is not None:
        try:
            return resolved.relative_to(repo_root).as_posix()
        except ValueError:
            pass
    return redact_local_paths(resolved.as_posix(), repo_root)


def metadata_display_key(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return f"installed-cache:{resolved.relative_to(INSTALLED_CACHE_ROOT).as_posix()}"
    except ValueError:
        pass
    return display_path(resolved, repo_root)


def metadata_path_for_key(key: str, repo_root: Path) -> Path:
    if key.startswith("installed-cache:"):
        return INSTALLED_CACHE_ROOT / key.removeprefix("installed-cache:")
    return Path(key) if Path(key).is_absolute() else repo_root / key


def redacted_model_stream(text: str, repo_root: Path) -> str:
    return redact_local_paths(text, repo_root)


def observed_runtime_skill_slugs(stream_text: str) -> list[str]:
    marker = "<installed-cache-root>/skills/"
    slugs: list[str] = []
    for line in stream_text.splitlines():
        start = line.find(marker)
        if start == -1:
            continue
        rest = line[start + len(marker) :]
        slug = rest.split("/", 1)[0].strip()
        if slug and slug not in slugs:
            slugs.append(slug)
    return slugs


def skill_id_to_slug(skill_id: str) -> str:
    return skill_id.removeprefix("dddjango:")


def apply_runtime_loaded_skill_evidence(
    result: dict[str, Any],
    *,
    expected_skills: list[str],
    stdout_path: Path,
) -> dict[str, Any]:
    stream_text = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.is_file() else ""
    observed_slugs = observed_runtime_skill_slugs(stream_text)
    observed_skill_ids = [f"dddjango:{slug}" for slug in observed_slugs]
    matched_expected = [
        expected
        for expected in expected_skills
        if skill_id_to_slug(expected) in observed_slugs
    ]
    result["checks"]["runtime_loaded_skill"] = {
        "expected": expected_skills,
        "observed": observed_skill_ids,
        "matched": matched_expected,
        "ok": bool(matched_expected),
    }
    if (
        result.get("status") == "fail"
        and result.get("score") == 1.0
        and result.get("failure_semantics") == ["wrong-routing"]
        and matched_expected
    ):
        result["failure_semantics"] = []
        result["status"] = "pass"
        result["checks"]["loaded_skill"]["self_report_ok"] = False
        result["checks"]["loaded_skill"]["ok"] = True
        result["checks"]["loaded_skill"]["resolved_by_runtime_evidence"] = True
    return result


def scan_persisted_artifacts_for_local_leakage(output_dir: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    scanned_roots = [output_dir / "raw", output_dir / "report"]
    for root in scanned_roots:
        if not root.exists():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            text = path.read_text(encoding="utf-8", errors="replace")
            hits = [pattern for pattern in LOCAL_LEAK_PATTERNS if pattern in text]
            if hits:
                findings.append(
                    {
                        "path": safe_artifact_path(path),
                        "hit_count": len(hits),
                        "hit_digests": [sha256_text(pattern) for pattern in hits],
                    }
                )
    return findings


def load_cases(fixture_root: Path) -> list[dict[str, Any]]:
    path = fixture_root / "cases.json"
    cases = read_json(path)
    if not isinstance(cases, list):
        raise EvalError("cases.json must contain a list")
    return cases


def case_by_id(fixture_root: Path, case_id: str) -> dict[str, Any]:
    for case in load_cases(fixture_root):
        if case.get("id") == case_id:
            return case
    raise EvalError(f"case not found: {case_id}")


def metadata_digest_manifest(paths: Paths) -> dict[str, str]:
    roots = [
        paths.fixture_root / "cases.json",
        paths.repo_root / "workspace/plan/phases/p1-5-usage-cards/cards/20260522-230605-p1-5-skill-usage-cards-evidence.md",
        paths.repo_root / "workspace/plan/governance/eval_protocol.md",
        paths.repo_root / "workspace/scripts/p5_individual_eval.py",
        paths.repo_root / "dddjango/.codex-plugin/plugin.json",
        Path("/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/.codex-plugin/plugin.json"),
    ]
    manifest: dict[str, str] = {}
    for path in roots:
        if not path.is_file():
            continue
        manifest[metadata_display_key(path, paths.repo_root)] = sha256_file(path)
    for path in sorted((paths.repo_root / "dddjango/skills").glob("*/SKILL.md")):
        manifest[path.relative_to(paths.repo_root).as_posix()] = sha256_file(path)
    return manifest


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def expected_outcome_conflict(case: dict[str, Any]) -> str | None:
    seen: dict[str, Any] = {}
    for outcome in case.get("expected_outcomes", []):
        if not isinstance(outcome, dict):
            return "expected-outcomes-malformed"
        key = outcome.get("id")
        value = outcome.get("value")
        if not key:
            return "expected-outcomes-malformed"
        if key in seen and seen[key] != value:
            return "expected-outcomes-conflict"
        seen[str(key)] = value
    return None


def loaded_skill_matches(actual: Any, expected: Any) -> bool:
    if expected is None:
        return True
    if actual == expected:
        return True
    if not isinstance(actual, str) or not isinstance(expected, str):
        return False
    observed = [part.strip() for part in actual.replace(",", ";").replace("+", ";").split(";")]
    return any(part == expected or part.startswith(f"{expected} ") for part in observed)


def expected_loaded_skills(oracle: dict[str, Any]) -> list[str]:
    acceptable = oracle.get("acceptable_loaded_skills")
    if isinstance(acceptable, list) and all(isinstance(item, str) for item in acceptable):
        return acceptable
    loaded_skill = oracle.get("loaded_skill")
    return [loaded_skill] if isinstance(loaded_skill, str) else []


def score_variant(*, case: dict[str, Any], variant: str) -> dict[str, Any]:
    case_id = str(case.get("id"))
    result: dict[str, Any] = {
        "case_id": case_id,
        "variant": variant,
        "surface": case.get("surface"),
        "skill_under_test": case.get("skill_under_test"),
        "expected_loaded_skill": None,
        "actual_loaded_skill": None,
        "status": "not-scored",
        "score": None,
        "failure_semantics": [],
        "checks": {},
    }

    conflict = expected_outcome_conflict(case)
    if conflict:
        result["failure_semantics"].append(conflict)
        return result

    oracle = case.get("oracle")
    answers = case.get("answers")
    if not isinstance(oracle, dict):
        result["failure_semantics"].append("malformed-oracle")
        return result
    if not isinstance(answers, dict) or variant not in answers:
        result["failure_semantics"].append("missing-answer")
        return result
    answer = answers[variant]
    if not isinstance(answer, dict):
        result["failure_semantics"].append("malformed-answer")
        return result

    required_claims = oracle.get("required_claims")
    if not isinstance(required_claims, list) or not all(isinstance(item, str) for item in required_claims):
        result["failure_semantics"].append("malformed-oracle")
        return result

    answer_claims = set(answer.get("claims", []))
    matched_claims = [claim for claim in required_claims if claim in answer_claims]
    claim_total = len(required_claims)
    claim_score = len(matched_claims) / claim_total if claim_total else 1.0
    result["checks"]["claims"] = {
        "required": required_claims,
        "matched": matched_claims,
        "score": claim_score,
    }

    accepted_loaded_skills = expected_loaded_skills(oracle)
    expected_loaded_skill = accepted_loaded_skills[0] if accepted_loaded_skills else oracle.get("loaded_skill")
    actual_loaded_skill = answer.get("loaded_skill")
    result["expected_loaded_skill"] = expected_loaded_skill
    result["actual_loaded_skill"] = actual_loaded_skill
    if accepted_loaded_skills:
        loaded_skill_ok = any(loaded_skill_matches(actual_loaded_skill, expected) for expected in accepted_loaded_skills)
        result["checks"]["loaded_skill"] = {
            "expected": expected_loaded_skill,
            "accepted": accepted_loaded_skills,
            "actual": actual_loaded_skill,
            "ok": loaded_skill_ok,
        }
        if not loaded_skill_ok:
            result["failure_semantics"].append("wrong-routing")

    if answer.get("overclaims"):
        result["failure_semantics"].append("forbidden-overclaim")

    if result["failure_semantics"]:
        result["score"] = claim_score
        result["status"] = "partial" if 0 < claim_score < 1 else "fail"
        return result

    result["score"] = claim_score
    if claim_score == 1.0:
        result["status"] = "pass"
    elif claim_score == 0:
        result["status"] = "fail"
        result["failure_semantics"].append("oracle-mismatch")
    else:
        result["status"] = "partial"
        result["failure_semantics"].append("oracle-partial")
    return result


def parse_model_answer(text: str) -> dict[str, Any]:
    try:
        answer = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EvalError(f"malformed model answer JSON: {exc}") from exc
    if not isinstance(answer, dict):
        raise EvalError("model answer must be a JSON object")
    claims = answer.get("claims")
    if not isinstance(answer.get("loaded_skill"), str):
        raise EvalError("model answer loaded_skill must be a string")
    if not isinstance(claims, list) or not all(isinstance(item, str) for item in claims):
        raise EvalError("model answer claims must be a list of strings")
    if not isinstance(answer.get("overclaims"), bool):
        raise EvalError("model answer overclaims must be a boolean")
    if not isinstance(answer.get("answer_text"), str):
        raise EvalError("model answer answer_text must be a string")
    return answer


def parse_variants(value: str) -> tuple[str, ...]:
    variants = tuple(part.strip() for part in value.split(",") if part.strip())
    if not variants:
        raise EvalError("variants must not be empty")
    unknown = [variant for variant in variants if variant not in VARIANTS]
    if unknown:
        raise EvalError(f"unknown variants: {', '.join(unknown)}")
    return variants


def score_model_answer(*, case: dict[str, Any], variant: str, answer: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "case_id": str(case.get("id")),
        "variant": variant,
        "surface": case.get("surface"),
        "skill_under_test": case.get("skill_under_test"),
        "expected_loaded_skill": None,
        "actual_loaded_skill": answer.get("loaded_skill"),
        "status": "not-scored",
        "score": None,
        "failure_semantics": [],
        "checks": {},
        "model_backed": True,
        "answer_text_digest": sha256_text(str(answer.get("answer_text", ""))),
    }

    conflict = expected_outcome_conflict(case)
    if conflict:
        result["failure_semantics"].append(conflict)
        return result

    oracle = case.get("oracle")
    if not isinstance(oracle, dict):
        result["failure_semantics"].append("malformed-oracle")
        return result

    required_claims = oracle.get("required_claims")
    if not isinstance(required_claims, list) or not all(isinstance(item, str) for item in required_claims):
        result["failure_semantics"].append("malformed-oracle")
        return result

    answer_claims = set(answer.get("claims", []))
    matched_claims = [claim for claim in required_claims if claim in answer_claims]
    claim_total = len(required_claims)
    claim_score = len(matched_claims) / claim_total if claim_total else 1.0
    result["checks"]["claims"] = {
        "required": required_claims,
        "matched": matched_claims,
        "score": claim_score,
    }

    accepted_loaded_skills = expected_loaded_skills(oracle)
    expected_loaded_skill = accepted_loaded_skills[0] if accepted_loaded_skills else oracle.get("loaded_skill")
    result["expected_loaded_skill"] = expected_loaded_skill
    if accepted_loaded_skills:
        loaded_skill_ok = any(loaded_skill_matches(answer.get("loaded_skill"), expected) for expected in accepted_loaded_skills)
        result["checks"]["loaded_skill"] = {
            "expected": expected_loaded_skill,
            "accepted": accepted_loaded_skills,
            "actual": answer.get("loaded_skill"),
            "ok": loaded_skill_ok,
        }
        if not loaded_skill_ok:
            result["failure_semantics"].append("wrong-routing")

    if answer.get("overclaims"):
        result["failure_semantics"].append("forbidden-overclaim")

    result["score"] = claim_score
    if result["failure_semantics"]:
        result["status"] = "partial" if 0 < claim_score < 1 else "fail"
        return result
    if claim_score == 1.0:
        result["status"] = "pass"
    elif claim_score == 0:
        result["status"] = "fail"
        result["failure_semantics"].append("oracle-mismatch")
    else:
        result["status"] = "partial"
        result["failure_semantics"].append("oracle-partial")
    return result


def model_answer_schema_path(output_dir: Path) -> Path:
    path = output_dir / "raw" / "model-answer.schema.json"
    write_json(path, MODEL_ANSWER_SCHEMA)
    return path


def model_case_prompt(case: dict[str, Any]) -> str:
    return "\n".join(
        [
            "P5 individual skill eval. Answer the user's request using the installed runtime instructions that apply.",
            "Return only JSON matching the provided output schema.",
            "For claims, include only these stable identifiers when your answer satisfies the criterion:",
            "- reference-criterion-coverage: the answer covers the reference criterion for this request's appropriate skill boundary.",
            "- required-observations: the answer states the key observations, handoffs, assumptions, or limits needed for this request.",
            "- forbidden-overclaim: the answer avoids claiming file changes, runtime evidence, implementation, tests, or broader completion that it did not actually perform.",
            "A complete P5 answer normally includes all three claims; omit a claim only when your answer does not satisfy that criterion.",
            "",
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
    if runtime_channel == "external":
        command = ["codex"]
    elif runtime_channel in {"ollama", "lmstudio"}:
        command = ["codex", "--oss", "--local-provider", runtime_channel]
    else:
        raise EvalError("runtime_channel must be external, ollama, or lmstudio")
    if model:
        command.extend(["--model", model])
    command.extend(
        [
            "-a",
            "never",
            "exec",
            "--json",
            "--ephemeral",
            "--skip-git-repo-check",
            "-C",
            case_workdir.as_posix(),
            "-s",
            "read-only",
            "--output-schema",
            schema_path.as_posix(),
            "-o",
            final_path.as_posix(),
        ]
    )
    if variant == "baseline":
        command.append("--ignore-user-config")
    command.append(prompt)
    return command


def default_model_runner(command: list[str], *, cwd: Path, final_path: Path) -> subprocess.CompletedProcess[str]:
    del final_path
    cwd.mkdir(parents=True, exist_ok=True)
    return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)


def model_run_one(
    paths: Paths,
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
        raise EvalError(f"variant must be one of {', '.join(VARIANTS)}")
    case = case_by_id(paths.fixture_root, case_id)
    schema_path = model_answer_schema_path(paths.output_dir)
    case_workdir = work_root / run_id / f"{case_id}-{variant}"
    final_path = case_workdir / "final.json"
    stdout_path = paths.output_dir / "raw" / "model-executions" / f"{case_id}.{variant}.stdout.jsonl"
    stderr_path = paths.output_dir / "raw" / "model-executions" / f"{case_id}.{variant}.stderr.txt"
    prompt = model_case_prompt(case)
    command = build_model_command(
        runtime_channel=runtime_channel,
        variant=variant,
        case_workdir=case_workdir,
        final_path=final_path,
        schema_path=schema_path,
        prompt=prompt,
        model=model,
    )

    executor = runner or default_model_runner
    completed = executor(command, cwd=case_workdir, final_path=final_path)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(redacted_model_stream(getattr(completed, "stdout", ""), paths.repo_root), encoding="utf-8")
    stderr_path.write_text(redacted_model_stream(getattr(completed, "stderr", ""), paths.repo_root), encoding="utf-8")

    execution = {
        "command": redact_nested_paths(command, paths.repo_root),
        "command_digest": digest_for_data(command),
        "cwd": safe_artifact_path(case_workdir, paths.repo_root),
        "cwd_digest": sha256_text(case_workdir.as_posix()),
        "returncode": getattr(completed, "returncode", 1),
        "stdout_path": display_path(stdout_path, paths.repo_root),
        "stderr_path": display_path(stderr_path, paths.repo_root),
        "final_path": safe_artifact_path(final_path, paths.repo_root),
        "final_path_digest": sha256_text(final_path.as_posix()),
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
            answer = parse_model_answer(final_path.read_text(encoding="utf-8"))
        except EvalError:
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
            result = score_model_answer(case=case, variant=variant, answer=answer)
            oracle = case.get("oracle")
            expected_skills = expected_loaded_skills(oracle) if isinstance(oracle, dict) else []
            result = apply_runtime_loaded_skill_evidence(
                result,
                expected_skills=expected_skills,
                stdout_path=stdout_path,
            )

    result["run_id"] = run_id
    result["run_mode"] = MODEL_RUN_MODE
    result["execution"] = execution
    result["metadata_digests"] = metadata_digest_manifest(paths)
    result["metadata_digest"] = digest_for_data(result["metadata_digests"])
    write_json(paths.output_dir / "raw" / "one.json", result)
    return result


def model_run_bucket(
    paths: Paths,
    *,
    bucket: str,
    run_id: str,
    runtime_channel: str,
    work_root: Path,
    variants: tuple[str, ...] = VARIANTS,
    runner: Callable[..., Any] | None = None,
    model: str | None = None,
    flake_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cases = [case for case in load_cases(paths.fixture_root) if case.get("bucket") == bucket]
    if not cases:
        raise EvalError(f"bucket not found or empty: {bucket}")

    results: list[dict[str, Any]] = []
    for case in cases:
        for variant in variants:
            results.append(
                model_run_one(
                    paths,
                    case_id=str(case["id"]),
                    variant=variant,
                    run_id=run_id,
                    runtime_channel=runtime_channel,
                    work_root=work_root,
                    runner=runner,
                    model=model,
                )
            )

    status_counts: dict[str, int] = {"pass": 0, "partial": 0, "fail": 0, "not-scored": 0}
    for result in results:
        status_counts[result["status"]] += 1
    hard_failures = [result for result in results if result["status"] in FAIL_STATUSES]
    raw = {
        "schema_version": "p5-individual-eval-run/v1",
        "run_id": run_id,
        "bucket": bucket,
        "fixture_root": paths.fixture_root.relative_to(paths.repo_root).as_posix(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "variants": list(variants),
        "run_mode": MODEL_RUN_MODE,
        "model_backed": True,
        "runtime_parity_precondition": "complete",
        "runtime_channel": runtime_channel,
        "runner_destination": "codex-exec",
        "prompt_assembly_source": "workspace/scripts/p5_individual_eval.py:model_case_prompt",
        "system_developer_prompt_template": "installed Codex runtime plus installed dddjango plugin for with-plugin variant",
        "tool_sandbox_policy": {"codex_approval_policy": "never", "sandbox": "read-only"},
        "oracle_model_config": "deterministic local oracle from cases.json",
        "scoring_prompt_config": "deterministic scorer over structured model answer JSON",
        "flake_history": flake_history or {"iterations": 1, "variance_status": "single-pass provisional"},
        "status": "fail" if hard_failures else "pass",
        "status_counts": status_counts,
        "hard_failure_count": len(hard_failures),
        "case_count": len(cases),
        "result_count": len(results),
        "metadata_digests": metadata_digest_manifest(paths),
        "results": results,
    }
    raw["metadata_digest"] = digest_for_data(raw["metadata_digests"])
    raw["raw_digest"] = digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})
    write_json(paths.output_dir / "raw" / "run.json", raw)
    return raw


def model_run_targeted_suite(
    paths: Paths,
    *,
    bucket: str,
    run_id: str,
    iterations: int,
    runtime_channel: str,
    work_root: Path,
    variants: tuple[str, ...] = VARIANTS,
    runner: Callable[..., Any] | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    if iterations < 1:
        raise EvalError("iterations must be >= 1")
    runs = []
    for iteration in range(1, iterations + 1):
        iteration_run_id = f"{run_id}-targeted-{iteration}"
        raw = model_run_bucket(
            paths,
            bucket=bucket,
            run_id=iteration_run_id,
            runtime_channel=runtime_channel,
            work_root=work_root,
            variants=variants,
            runner=runner,
            model=model,
            flake_history={"iterations": iterations, "current_iteration": iteration, "variance_status": "pending"},
        )
        iteration_path = paths.output_dir / "raw" / f"targeted-run-{iteration}.json"
        write_json(iteration_path, raw)
        runs.append(
            {
                "iteration": iteration,
                "run_id": iteration_run_id,
                "artifact": display_path(iteration_path, paths.repo_root),
                "status": raw["status"],
                "status_counts": raw["status_counts"],
                "metadata_digest": raw["metadata_digest"],
            }
        )
    statuses = [run["status"] for run in runs]
    variance_status = "stable-pass" if statuses and all(status == "pass" for status in statuses) else "needs-classification"
    summary = {
        "schema_version": "p5-individual-model-targeted-suite/v1",
        "run_id": run_id,
        "bucket": bucket,
        "iterations": iterations,
        "variants": list(variants),
        "status": "pass" if variance_status == "stable-pass" else "fail",
        "model_backed": True,
        "runtime_channel": runtime_channel,
        "variance_status": variance_status,
        "runs": runs,
    }
    write_json(paths.output_dir / "raw" / "targeted-suite.json", summary)
    return summary


def run_one(paths: Paths, case_id: str, variant: str, run_id: str) -> dict[str, Any]:
    if variant not in VARIANTS:
        raise EvalError(f"variant must be one of {', '.join(VARIANTS)}")
    case = case_by_id(paths.fixture_root, case_id)
    result = score_variant(case=case, variant=variant)
    result["run_id"] = run_id
    result["metadata_digests"] = metadata_digest_manifest(paths)
    result["metadata_digest"] = digest_for_data(result["metadata_digests"])
    write_json(paths.output_dir / "raw" / "one.json", result)
    return result


def run_bucket(paths: Paths, bucket: str, run_id: str) -> dict[str, Any]:
    cases = [case for case in load_cases(paths.fixture_root) if case.get("bucket") == bucket]
    if not cases:
        raise EvalError(f"bucket not found or empty: {bucket}")

    results: list[dict[str, Any]] = []
    for case in cases:
        for variant in VARIANTS:
            results.append(score_variant(case=case, variant=variant))

    status_counts: dict[str, int] = {"pass": 0, "partial": 0, "fail": 0, "not-scored": 0}
    for result in results:
        status_counts[result["status"]] += 1

    hard_failures = [result for result in results if result["status"] in FAIL_STATUSES]
    raw = {
        "schema_version": "p5-individual-eval-run/v1",
        "run_id": run_id,
        "bucket": bucket,
        "fixture_root": paths.fixture_root.relative_to(paths.repo_root).as_posix(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "variants": list(VARIANTS),
        "run_mode": "fixture-scored-p5-preflight",
        "model_backed": False,
        "runtime_parity_precondition": "complete",
        "status": "fail" if hard_failures else "pass",
        "status_counts": status_counts,
        "hard_failure_count": len(hard_failures),
        "case_count": len(cases),
        "result_count": len(results),
        "metadata_digests": metadata_digest_manifest(paths),
        "results": results,
    }
    raw["metadata_digest"] = digest_for_data(raw["metadata_digests"])
    raw["raw_digest"] = digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})
    write_json(paths.output_dir / "raw" / "run.json", raw)
    return raw


def run_targeted_suite(paths: Paths, bucket: str, run_id: str, iterations: int) -> dict[str, Any]:
    if iterations < 1:
        raise EvalError("iterations must be >= 1")
    runs = []
    for iteration in range(1, iterations + 1):
        iteration_run_id = f"{run_id}-targeted-{iteration}"
        raw = run_bucket(paths, bucket, iteration_run_id)
        iteration_path = paths.output_dir / "raw" / f"targeted-run-{iteration}.json"
        write_json(iteration_path, raw)
        runs.append(
            {
                "iteration": iteration,
                "run_id": iteration_run_id,
                "artifact": display_path(iteration_path, paths.repo_root),
                "status": raw["status"],
                "status_counts": raw["status_counts"],
                "metadata_digest": raw["metadata_digest"],
            }
        )
    summary = {
        "schema_version": "p5-individual-targeted-suite/v1",
        "run_id": run_id,
        "bucket": bucket,
        "iterations": iterations,
        "status": "pass" if all(run["status"] == "pass" for run in runs) else "fail",
        "runs": runs,
    }
    write_json(paths.output_dir / "raw" / "targeted-suite.json", summary)
    return summary


def render_report(output_dir: Path) -> dict[str, Any]:
    raw_path = output_dir / "raw" / "run.json"
    if not raw_path.is_file():
        raise EvalError(f"missing raw run artifact: {raw_path}")
    raw = read_json(raw_path)
    source_digest = digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})
    report_results: list[dict[str, Any]] = []
    rows = []
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
        "schema_version": "p5-individual-eval-report/v1",
        "run_id": raw["run_id"],
        "source_raw_path": safe_artifact_path(raw_path),
        "source_raw_digest": source_digest,
        "status_counts": raw["status_counts"],
        "model_backed": raw.get("model_backed"),
        "runtime_parity_precondition": raw.get("runtime_parity_precondition"),
        "metadata_digest": raw.get("metadata_digest"),
        "results": report_results,
    }
    write_json(output_dir / "report" / "report.json", report_json)
    html_text = "\n".join(
        [
            "<!doctype html>",
            "<html><head><meta charset=\"utf-8\"><title>dddjango P5 individual eval report</title></head>",
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
    report_json["report_html_digest"] = sha256_file(report_html)
    write_json(output_dir / "report" / "report.json", report_json)
    return report_json


def validate_run(output_dir: Path, repo_root: Path) -> dict[str, Any]:
    raw_path = output_dir / "raw" / "run.json"
    report_path = output_dir / "report" / "report.json"
    failures: list[dict[str, Any]] = []
    if not raw_path.is_file():
        failures.append({"kind": "missing-raw-artifact", "path": raw_path.as_posix()})
    if not report_path.is_file():
        failures.append({"kind": "missing-report-artifact", "path": report_path.as_posix()})
    if failures:
        result = {"schema_version": "p5-individual-eval-validation/v1", "status": "fail", "failures": failures}
        write_json(output_dir / "validation" / "validate-run.json", result)
        return result

    raw = read_json(raw_path)
    report = read_json(report_path)
    raw_digest = digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})
    if raw.get("raw_digest") != raw_digest:
        failures.append({"kind": "raw-digest-mismatch"})
    if report.get("source_raw_digest") != raw_digest:
        failures.append({"kind": "stale-report", "expected": raw_digest, "actual": report.get("source_raw_digest")})
    if report.get("status_counts") != raw.get("status_counts"):
        failures.append({"kind": "report-status-count-mismatch"})
    leakage_findings = scan_persisted_artifacts_for_local_leakage(output_dir)
    if leakage_findings:
        failures.append({"kind": "local-path-or-private-leakage-present", "count": len(leakage_findings)})

    raw_result_keys = {
        (item["case_id"], item["variant"]): (
            item["surface"],
            item["skill_under_test"],
            item["status"],
            item["actual_loaded_skill"],
            tuple(item["failure_semantics"]),
        )
        for item in raw.get("results", [])
    }
    report_result_keys = {
        (item["case_id"], item["variant"]): (
            item["surface"],
            item["skill_under_test"],
            item["status"],
            item["actual_loaded_skill"],
            tuple(item["failure_semantics"]),
        )
        for item in report.get("results", [])
    }
    if raw_result_keys != report_result_keys:
        failures.append({"kind": "report-raw-result-mismatch"})

    not_scored = [key for key, value in raw_result_keys.items() if value[2] == "not-scored"]
    if not_scored:
        failures.append({"kind": "not-scored-present", "count": len(not_scored)})
    non_pass = [key for key, value in raw_result_keys.items() if value[2] != "pass"]
    if non_pass:
        failures.append({"kind": "non-pass-result-present", "count": len(non_pass)})

    missing_or_malformed = [
        item
        for result in raw.get("results", [])
        for item in result.get("failure_semantics", [])
        if item.startswith("missing-") or item.startswith("malformed-")
    ]
    if missing_or_malformed:
        failures.append({"kind": "missing-or-malformed-oracle-or-answer", "count": len(missing_or_malformed)})

    if raw.get("model_backed") is True:
        flake_history = raw.get("flake_history")
        if not isinstance(flake_history, dict):
            failures.append({"kind": "model-backed-flake-history-missing"})
        else:
            iterations = flake_history.get("iterations")
            variance_status = flake_history.get("variance_status")
            if iterations == 1 and variance_status == "single-pass provisional":
                targeted_suite_path = output_dir / "raw" / "targeted-suite.json"
                if targeted_suite_path.is_file():
                    targeted_suite = read_json(targeted_suite_path)
                    targeted_iterations = targeted_suite.get("iterations")
                    targeted_variance_status = targeted_suite.get("variance_status")
                    targeted_variants = targeted_suite.get("variants")
                    if (
                        targeted_suite.get("model_backed") is True
                        and targeted_suite.get("status") == "pass"
                        and isinstance(targeted_iterations, int)
                        and targeted_iterations >= 2
                        and targeted_variance_status == "stable-pass"
                        and targeted_variants == raw.get("variants")
                    ):
                        flake_history["targeted_suite_artifact"] = display_path(targeted_suite_path, repo_root)
                        flake_history["targeted_suite_digest"] = sha256_file(targeted_suite_path)
                    else:
                        failures.append({"kind": "model-backed-single-pass-provisional"})
                else:
                    failures.append({"kind": "model-backed-single-pass-provisional"})
            elif not isinstance(iterations, int) or iterations < 2:
                failures.append({"kind": "model-backed-targeted-iterations-missing"})
            elif variance_status not in {"stable-pass", "pending"}:
                failures.append({"kind": "model-backed-variance-status-invalid", "actual": variance_status})

    current_metadata: dict[str, str] = {}
    missing_metadata_files = []
    for rel_path in sorted(raw.get("metadata_digests", {})):
        path = metadata_path_for_key(rel_path, repo_root)
        if not path.is_file():
            missing_metadata_files.append(rel_path)
            continue
        current_metadata[rel_path] = sha256_file(path)
    if missing_metadata_files:
        failures.append({"kind": "metadata-file-missing", "paths": missing_metadata_files})
    if current_metadata != raw.get("metadata_digests"):
        failures.append({"kind": "metadata-digest-mismatch"})
    if digest_for_data(raw.get("metadata_digests", {})) != raw.get("metadata_digest"):
        failures.append({"kind": "metadata-digest-field-mismatch"})

    result = {
        "schema_version": "p5-individual-eval-validation/v1",
        "status": "fail" if failures else "pass",
        "raw_path": raw_path.as_posix(),
        "report_path": report_path.as_posix(),
        "raw_digest": raw_digest,
        "metadata_digest": raw.get("metadata_digest"),
        "status_counts": raw.get("status_counts"),
        "case_count": raw.get("case_count"),
        "result_count": raw.get("result_count"),
        "model_backed": raw.get("model_backed"),
        "runtime_parity_precondition": raw.get("runtime_parity_precondition"),
        "failures": failures,
        "leakage_findings": leakage_findings,
    }
    write_json(output_dir / "validation" / "validate-run.json", result)
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-root", default="workspace/develop/eval/fixtures/individual-skills")
    parser.add_argument("--output-dir", default="workspace/develop/eval/runs/p5-individual-skills-fixture")
    parser.add_argument("--repo-root", default=".")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_one_parser = subparsers.add_parser("run-one")
    run_one_parser.add_argument("--case-id", required=True)
    run_one_parser.add_argument("--variant", choices=VARIANTS, required=True)
    run_one_parser.add_argument("--run-id", default="p5-individual-skills-targeted")

    run_bucket_parser = subparsers.add_parser("run-bucket")
    run_bucket_parser.add_argument("--bucket", default="individual-skills")
    run_bucket_parser.add_argument("--run-id", default="p5-individual-skills-fixture")

    targeted_parser = subparsers.add_parser("run-targeted-suite")
    targeted_parser.add_argument("--bucket", default="individual-skills")
    targeted_parser.add_argument("--run-id", default="p5-individual-skills-fixture")
    targeted_parser.add_argument("--iterations", type=int, default=2)

    model_one_parser = subparsers.add_parser("model-run-one")
    model_one_parser.add_argument("--case-id", required=True)
    model_one_parser.add_argument("--variant", choices=VARIANTS, required=True)
    model_one_parser.add_argument("--run-id", default="p5-individual-skills-model")
    model_one_parser.add_argument("--runtime-channel", choices=("external", "ollama", "lmstudio"), default="external")
    model_one_parser.add_argument("--work-root", default="/private/tmp/dddjango-p5-model")
    model_one_parser.add_argument("--model")

    model_bucket_parser = subparsers.add_parser("model-run-bucket")
    model_bucket_parser.add_argument("--bucket", default="individual-skills")
    model_bucket_parser.add_argument("--run-id", default="p5-individual-skills-model")
    model_bucket_parser.add_argument("--runtime-channel", choices=("external", "ollama", "lmstudio"), default="external")
    model_bucket_parser.add_argument("--work-root", default="/private/tmp/dddjango-p5-model")
    model_bucket_parser.add_argument("--model")
    model_bucket_parser.add_argument("--variants", default="baseline,with-plugin")

    model_targeted_parser = subparsers.add_parser("model-run-targeted-suite")
    model_targeted_parser.add_argument("--bucket", default="individual-skills")
    model_targeted_parser.add_argument("--run-id", default="p5-individual-skills-model")
    model_targeted_parser.add_argument("--iterations", type=int, default=2)
    model_targeted_parser.add_argument("--runtime-channel", choices=("external", "ollama", "lmstudio"), default="external")
    model_targeted_parser.add_argument("--work-root", default="/private/tmp/dddjango-p5-model")
    model_targeted_parser.add_argument("--model")
    model_targeted_parser.add_argument("--variants", default="baseline,with-plugin")

    subparsers.add_parser("render-report")
    subparsers.add_parser("validate-run")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    paths = Paths(
        fixture_root=(repo_root / args.fixture_root).resolve(),
        output_dir=(repo_root / args.output_dir).resolve(),
        repo_root=repo_root,
    )
    try:
        if args.command == "run-one":
            result = run_one(paths, args.case_id, args.variant, args.run_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["status"] in PASS_STATUSES else 1
        if args.command == "run-bucket":
            raw = run_bucket(paths, args.bucket, args.run_id)
            print(json.dumps({"status": raw["status"], "status_counts": raw["status_counts"]}, ensure_ascii=False))
            return 0 if raw["status"] == "pass" else 1
        if args.command == "run-targeted-suite":
            summary = run_targeted_suite(paths, args.bucket, args.run_id, args.iterations)
            print(json.dumps({"status": summary["status"], "iterations": summary["iterations"]}, ensure_ascii=False))
            return 0 if summary["status"] == "pass" else 1
        if args.command == "model-run-one":
            result = model_run_one(
                paths,
                case_id=args.case_id,
                variant=args.variant,
                run_id=args.run_id,
                runtime_channel=args.runtime_channel,
                work_root=Path(args.work_root),
                model=args.model,
            )
            print(json.dumps({"status": result["status"], "failure_semantics": result["failure_semantics"]}, ensure_ascii=False))
            return 0 if result["status"] in PASS_STATUSES else 1
        if args.command == "model-run-bucket":
            raw = model_run_bucket(
                paths,
                bucket=args.bucket,
                run_id=args.run_id,
                runtime_channel=args.runtime_channel,
                work_root=Path(args.work_root),
                variants=parse_variants(args.variants),
                model=args.model,
            )
            print(json.dumps({"status": raw["status"], "status_counts": raw["status_counts"]}, ensure_ascii=False))
            return 0 if raw["status"] == "pass" else 1
        if args.command == "model-run-targeted-suite":
            summary = model_run_targeted_suite(
                paths,
                bucket=args.bucket,
                run_id=args.run_id,
                iterations=args.iterations,
                runtime_channel=args.runtime_channel,
                work_root=Path(args.work_root),
                variants=parse_variants(args.variants),
                model=args.model,
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
            result = validate_run(paths.output_dir, repo_root)
            print(json.dumps({"status": result["status"], "failures": result["failures"]}, ensure_ascii=False))
            return 0 if result["status"] == "pass" else 1
    except EvalError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
