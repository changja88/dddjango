"""계정 교체 후 한도 거부 시행만 별도 기록으로 한 번 재개한다."""

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from experiment import digest, grade_constructor, grade_guard
from run_experiments import parse_answer, write_json

ROOT = Path(__file__).resolve().parent


def retry_candidates(rows: list[dict], already_retried: set[str]) -> list[dict]:
    return sorted([row for row in rows
                   if row["trial"] not in already_retried and row.get("error") and row.get("grade") is None
                   and (row.get("response") or {}).get("api_error_status") == 429
                   and (row.get("response") or {}).get("modelUsage") == {}], key=lambda row: row["started_utc"])


def reconcile_trials(originals: list[dict], retries: list[dict]) -> list[dict]:
    by_id = {row["trial"]: row for row in originals}
    eligible = {row["trial"] for row in retry_candidates(originals, set())}
    seen: set[str] = set()
    for retry in retries:
        key = retry.get("retry_of")
        if key not in eligible or key in seen:
            raise ValueError("unknown, duplicate or ineligible retry")
        original = by_id[key]
        for field in ["trial", "case", "arm", "repeat", "prompt_sha256", "command"]:
            if retry.get(field) != original.get(field):
                raise ValueError("retry changed registered input or identity")
        seen.add(key)
        by_id[key] = retry
    return [by_id[row["trial"]] for row in originals]


def run() -> None:
    config = json.loads((ROOT / "cases.json").read_text())
    manifest = json.loads((ROOT / "manifest.json").read_text())
    if manifest["cases_sha256"] != digest((ROOT / "cases.json").read_text()):
        raise ValueError("registered cases changed")
    originals = [json.loads(path.read_text()) for path in sorted((ROOT / "trials").glob("*.json"))]
    retry_dir = ROOT / "retries/round-1"
    retry_dir.mkdir(parents=True, exist_ok=True)
    previous = [json.loads(path.read_text()) for path in sorted(retry_dir.glob("*.json"))]
    reconcile_trials(originals, previous)
    candidates = retry_candidates(originals, {row["retry_of"] for row in previous})
    for row in previous:
        if row["original_record_sha256"] != digest((ROOT / "trials" / f"{row['retry_of']}.json").read_text()):
            raise ValueError("original attempt changed")
    version = subprocess.check_output(["claude", "--version"], text=True).strip()
    if version != "2.1.261 (Claude Code)":
        raise ValueError("Claude version differs from registered run")
    baseline_command = originals[0]["command"]
    if any(row["command"] != baseline_command for row in originals):
        raise ValueError("original commands differ")
    if baseline_command[0] != "claude" or baseline_command[baseline_command.index("--tools") + 1] != "":
        raise ValueError("expected tool-free Claude command")
    resume_path = ROOT / "resume.json"
    if not resume_path.exists():
        write_json(resume_path, {"started_utc": datetime.now(timezone.utc).isoformat(), "runtime": version,
                                 "account_change": "user reports account replacement; no account identity or credentials collected",
                                 "preflight": "same model returned READY, exit 0, standard speed, no permission denials",
                                 "candidate_trials": [row["trial"] for row in candidates],
                                 "original_record_sha256": {row["trial"]: digest((ROOT / "trials" / f"{row['trial']}.json").read_text()) for row in originals},
                                 "frozen_manifest_sha256": digest((ROOT / "manifest.json").read_text()),
                                 "reporting": "account/cache/provider changes remain a separate execution batch"})
        with (ROOT / "summary-before-resume.json").open("xb") as backup:
            backup.write((ROOT / "summary.json").read_bytes())
    for original in candidates:
        name = original["trial"]
        packet = manifest["packets"][original["case"]][original["arm"]]
        prompt = (ROOT / packet["file"]).read_text()
        if digest(prompt) != packet["sha256"] or original["prompt_sha256"] != packet["sha256"]:
            raise ValueError("prompt differs from original attempt")
        started_utc = datetime.now(timezone.utc).isoformat()
        print(json.dumps({"trial": name, "status": "retry started", "utc": started_utc}), flush=True)
        started = time.perf_counter()
        try:
            process = subprocess.run(original["command"], input=prompt, text=True, capture_output=True, timeout=900)
            raw, stderr, exit_code = process.stdout, process.stderr, process.returncode
        except subprocess.TimeoutExpired as error:
            raw = error.stdout.decode() if isinstance(error.stdout, bytes) else error.stdout or ""
            stderr, exit_code = "900-second timeout", None
        wall_ms = (time.perf_counter() - started) * 1000
        response, answer, grade, error_text = None, None, None, None
        try:
            response = json.loads(raw)
            if exit_code != 0 or not isinstance(response, dict) or response.get("is_error") or response.get("subtype") != "success":
                raise ValueError("model/harness error")
            if config["model"] not in response.get("modelUsage", {}) or response.get("permission_denials"):
                raise ValueError("primary model missing or permission denial")
            answer = parse_answer(response["result"])
            grade = grade_guard(answer.get("code", "")) if original["case"] == "guard" else grade_constructor(answer)
        except (ValueError, KeyError, TypeError) as error:
            error_text = str(error)
        result = {**{key: original[key] for key in ["trial", "case", "arm", "repeat", "command", "prompt_sha256", "prompt_bytes"]},
                  "retry_of": name, "retry_number": 1, "execution_batch": "user-switched-account",
                  "original_record_sha256": digest((ROOT / "trials" / f"{name}.json").read_text()),
                  "started_utc": started_utc, "wall_ms": wall_ms, "exit_code": exit_code,
                  "response": response, "raw_unparsed": raw if response is None else None,
                  "stderr": stderr, "answer": answer, "grade": grade, "error": error_text}
        with (retry_dir / f"{name}.json").open("x") as output:
            json.dump(result, output, ensure_ascii=False, indent=2)
            output.write("\n")
        print(json.dumps({"trial": name, "status": "retry finished", "wall_s": round(wall_ms / 1000, 3),
                          "all_pass": grade["all_pass"] if grade else None, "error": error_text}), flush=True)
        if (response or {}).get("api_error_status") == 429:
            print("Quota still blocked; no further retries attempted.", flush=True)
            break


if __name__ == "__main__":
    run()
