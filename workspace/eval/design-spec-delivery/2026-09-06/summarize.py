"""보존된 원자료만 집계한다. 실험이나 모델을 재실행하지 않는다."""

import argparse
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

from experiment import digest, grade_constructor, grade_guard
from retry_blocked import reconcile_trials

ROOT = Path(__file__).resolve().parent


def distribution(values: list[float]) -> dict | None:
    return {"median": statistics.median(values), "min": min(values), "max": max(values)} if values else None


def group_trials(rows: list[dict]) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[f"{row['case']}/{row['arm']}"].append(row)
    result = {}
    for key, group in sorted(groups.items()):
        errors = sum(bool(r.get("error")) for r in group)
        valid = [r for r in group if not r.get("error") and r.get("grade") is not None]
        primary = [(r.get("response") or {}).get("modelUsage", {}).get("claude-fable-5-1", {}) for r in group]
        input_totals = [p.get("inputTokens", 0) + p.get("cacheReadInputTokens", 0) + p.get("cacheCreationInputTokens", 0)
                        for p in primary if p]
        result[key] = {"attempts": len(group), "errors": errors, "all_trials_valid": len(valid) == len(group),
                       "valid_model_trials": len(valid),
                       "all_pass": sum(bool((r.get("grade") or {}).get("all_pass")) for r in group),
                       "wall_ms_all_attempts": distribution([r["wall_ms"] for r in group]),
                       "wall_ms_valid_model_trials": distribution([r["wall_ms"] for r in valid]),
                       "api_ms_valid_model_trials": distribution([r["response"]["duration_api_ms"] for r in valid
                                               if (r.get("response") or {}).get("duration_api_ms") is not None]),
                       "input_tokens_including_cache": distribution(input_totals),
                       "cache_read_tokens": distribution([p.get("cacheReadInputTokens", 0) for p in primary if p]),
                       "cache_creation_tokens": distribution([p.get("cacheCreationInputTokens", 0) for p in primary if p]),
                       "output_tokens_including_thinking": distribution([p.get("outputTokens", 0) for p in primary if p]),
                       "thinking_tokens": distribution([p.get("thinkingTokens", 0) for p in primary if p])}
    return result


def summarize(require_complete: bool) -> dict:
    config = json.loads((ROOT / "cases.json").read_text())
    manifest = json.loads((ROOT / "manifest.json").read_text())
    offline = json.loads((ROOT / "offline-results.json").read_text())
    engine = json.loads((ROOT / "engine-results.json").read_text())
    originals = [json.loads(path.read_text()) for path in sorted((ROOT / "trials").glob("*.json"))]
    retries = [json.loads(path.read_text()) for path in sorted((ROOT / "retries/round-1").glob("*.json"))]
    for retry in retries:
        original_path = ROOT / "trials" / f"{retry['retry_of']}.json"
        if retry.get("original_record_sha256") != digest(original_path.read_text()):
            raise ValueError("retry original record hash differs")
    rows = reconcile_trials(originals, retries)
    all_attempts = originals + retries
    expected = {f"{repeat}-{case['id']}-{arm}" for repeat in range(1, config["model_repeats"] + 1)
                for case in config["cases"] for arm in ["full", "search", "linked"]}
    if require_complete and {r["trial"] for r in rows} != expected:
        raise ValueError("not all registered trials are present")
    if manifest["cases_sha256"] != digest((ROOT / "cases.json").read_text()):
        raise ValueError("cases differ from frozen manifest")
    if offline["manifest_sha256"] != digest((ROOT / "manifest.json").read_text()):
        raise ValueError("manifest differs from offline input")
    for snapshot in manifest["snapshots"]:
        if digest((ROOT / snapshot["file"]).read_text()) != snapshot["sha256"]:
            raise ValueError("frozen source digest differs")
    for row in all_attempts:
        packet = manifest["packets"][row["case"]][row["arm"]]
        if row["prompt_sha256"] != packet["sha256"] or digest((ROOT / packet["file"]).read_text()) != packet["sha256"]:
            raise ValueError("trial prompt differs from frozen input")
        if row["grade"] is not None:
            fresh = grade_guard(row["answer"].get("code", "")) if row["case"] == "guard" else grade_constructor(row["answer"])
            if fresh != row["grade"]:
                raise ValueError("fresh grade differs from recorded result")
    retrieval = {}
    for mode in ["body", "context", "explicit_relations", "curated"]:
        selected = [r for r in offline["retrieval"] if r["mode"] == mode]
        retrieval[mode] = {"queries": len(selected), "all_obligations_found": sum(r["coverage"]["all_pass"] for r in selected),
                           "obligations_found": sum(len(r["coverage"]["passed"]) for r in selected),
                           "obligations_total": sum(len(r["coverage"]["passed"]) + len(r["coverage"]["missing"]) for r in selected),
                           "raw_bytes": distribution([r["bytes"] for r in selected]),
                           "query_median_ms": distribution([r["median_ms"] for r in selected])}
    read_probes = []
    for path in sorted((ROOT / "read-probes").glob("*.json")):
        row = json.loads(path.read_text())
        tool_results = row["trace"]["tool_results"]
        content = tool_results[0].get("content", "") if len(tool_results) == 1 else ""
        stripped = re.sub(r"(?m)^\d+\t", "", content) if isinstance(content, str) else ""
        source = Path(row["requested"]["file_path"]).read_text()
        read_probes.append({"probe": row["probe"], "exact_request": row["trace"]["exact_one_requested_read"],
                            "read_succeeded": row["trace"]["read_succeeded"], "read_failed": row["trace"]["read_failed"],
                            "read_content_byte_exact_after_line_numbers_removed": stripped == source,
                            "source_sha_matches": digest(source) == row["source_sha256"], "wall_ms": row["wall_ms"]})
    valid = [r for r in rows if not r.get("error") and r.get("grade") is not None]
    adjudications = []
    reviewed_rows = []
    for row in rows:
        reviewed_grade = row["grade"]
        if row["case"] == "guard" and not row.get("error") and row.get("answer"):
            reviewed_grade = grade_guard(row["answer"].get("code", ""), allow_replace=True)
            attempt_file = ("retries/round-1/" if row.get("retry_of") else "trials/") + row["trial"] + ".json"
            adjudications.append({"trial": row["trial"], "attempt_file": attempt_file,
                                  "attempt_sha256": digest((ROOT / attempt_file).read_text()),
                                  "code_sha256": digest(row["answer"].get("code", "")),
                                  "default_grade": row["grade"], "reviewed_grade": reviewed_grade,
                                  "changed": reviewed_grade != row["grade"],
                                  "method": "post-run allow_replace=True; same ten behavior checks, applied to every valid guard response"})
        reviewed_rows.append({**row, "grade": reviewed_grade})
    pending_probes = sorted({"original-250-lines", "chunk-first", "chunk-large-revision", "chunk-longest-line-followup"}
                            - {r["probe"] for r in read_probes})
    return {"registered_trials": len(expected), "recorded_trials": len(rows), "all_registered_trials_present": {r["trial"] for r in rows} == expected,
            "recorded_original_trials": len(originals), "recorded_attempts": len(all_attempts), "recorded_retries": len(retries),
            "original_attempt_errors": sum(bool(r.get("error")) for r in originals),
            "default_all_pass_count": sum(bool((r.get("grade") or {}).get("all_pass")) for r in rows),
            "reviewed_all_pass_count": sum(bool((r.get("grade") or {}).get("all_pass")) for r in reviewed_rows),
            "adjudications": adjudications, "reviewed_groups": group_trials(reviewed_rows),
            "valid_model_trials": len(valid), "all_registered_trials_valid": {r["trial"] for r in valid} == expected,
            "invalid_or_missing_trials": sorted(expected - {r["trial"] for r in valid}), "pending_read_probes": pending_probes,
            "frozen_digests_valid": True, "fresh_grades_match": True,
            "groups": group_trials(rows), "original_groups": group_trials(originals), "resumed_groups": group_trials(retries),
            "read_probes": read_probes, "retrieval": retrieval,
            "engine_equivalence": engine["exact_equivalence"],
            "engine_warm_ms": {name: {key: values[key] for key in ["median_ms", "min_ms", "max_ms"]}
                               for name, values in engine["warm_queries"].items()},
            "trial_details": [{"trial": row["trial"], "case": row["case"], "arm": row["arm"], "wall_ms": row["wall_ms"],
                               "execution_batch": row.get("execution_batch", "original-session"), "retry_of": row.get("retry_of"),
                               "grade": row["grade"], "error": row["error"], "exit_code": row["exit_code"],
                               "api_error_status": (row.get("response") or {}).get("api_error_status"),
                               "error_message": (row.get("response") or {}).get("result") if row.get("error") else None,
                               "primary_model": config["model"] in (row.get("response") or {}).get("modelUsage", {}),
                               "permission_denials": (row.get("response") or {}).get("permission_denials"),
                               "num_turns": (row.get("response") or {}).get("num_turns"),
                               "usage": (row.get("response") or {}).get("usage"),
                               "model_usage": (row.get("response") or {}).get("modelUsage")} for row in all_attempts],
            "measurement_limits": ["Two known frozen tasks, not independent holdouts or end-to-end dddjango.",
                                   "Full input bypasses historical Read failure; curated input is manual and its preparation cost is unmeasured.",
                                   "Cache, reasoning length, provider load and CLI auxiliary requests can affect wall time; no pure prefill causal claim.",
                                   "Retries after a user-reported account replacement are a separate batch. Combined groups mix accounts/time/cache conditions; consult original_groups and resumed_groups separately.",
                                   "Default grades remain unchanged. A post-run allow_replace adjudication is separately recorded for all valid guard responses because the task allowed literal string replacement.",
                                   "All-attempt time includes errors and must not be used for speed comparisons. Valid-model time is separate, including valid but quality-failing trials if present; incomplete repetitions remain incomplete.",
                                   "All-pass covers only registered limited behavior/decision probes, not overall design and code quality."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--partial", action="store_true")
    args = parser.parse_args()
    result = summarize(not args.partial)
    if not args.partial:
        (ROOT / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        (ROOT / "adjudications.json").write_text(json.dumps(result["adjudications"], ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ["recorded_trials", "groups", "read_probes", "retrieval", "engine_equivalence", "engine_warm_ms"]}, ensure_ascii=False))
