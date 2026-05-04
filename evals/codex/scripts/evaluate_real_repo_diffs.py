#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


VARIANTS = ("baseline", "dddjango")


def load_json(path):
    return json.loads(Path(path).read_text())


def extract_diff_blocks(text):
    blocks = []
    lines = text.splitlines()
    in_fence = False
    fence_lines = []
    fence_lang = ""

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_fence:
                block = "\n".join(fence_lines).strip()
                if "diff --git " in block and (fence_lang == "diff" or block.startswith("diff --git ")):
                    blocks.append(block)
                in_fence = False
                fence_lines = []
                fence_lang = ""
            else:
                in_fence = True
                fence_lang = stripped.removeprefix("```").strip().lower()
            continue
        if in_fence:
            fence_lines.append(line)

    if blocks:
        return blocks

    for index, line in enumerate(lines):
        if line.startswith("diff --git "):
            return ["\n".join(lines[index:]).strip()]
    return []


def combined_diff(text):
    blocks = extract_diff_blocks(text)
    if not blocks:
        return ""
    return "\n\n".join(block.rstrip() for block in blocks) + "\n"


def run_command(command, *, cwd, input_text=None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=30,
        )
    except FileNotFoundError as exc:
        return {
            "status": "skipped",
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "failed",
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": "command timed out",
        }

    return {
        "status": "passed" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def module_available(module_name, *, cwd):
    result = run_command(
        [sys.executable, "-c", f"import {module_name}"],
        cwd=cwd,
    )
    return result["status"] == "passed"


def command_summary(result, limit=500):
    output = (result.get("stderr") or result.get("stdout") or "").strip()
    if len(output) > limit:
        return output[:limit] + "..."
    return output


def run_optional_checks(workspace_path):
    if not (workspace_path / "manage.py").exists():
        return {
            "django_check": {"status": "skipped", "notes": "manage.py not found"},
            "pytest": {"status": "skipped", "notes": "manage.py not found"},
        }

    if not module_available("django", cwd=workspace_path):
        return {
            "django_check": {"status": "skipped", "notes": "django is not installed"},
            "pytest": {"status": "skipped", "notes": "django is not installed"},
        }

    django_check = run_command(
        [sys.executable, "manage.py", "check"],
        cwd=workspace_path,
    )
    django_check["notes"] = command_summary(django_check)

    if module_available("pytest", cwd=workspace_path):
        pytest_result = run_command(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=workspace_path,
        )
    else:
        pytest_result = {"status": "skipped", "notes": "pytest is not installed"}
    pytest_result["notes"] = pytest_result.get("notes", command_summary(pytest_result))

    return {
        "django_check": django_check,
        "pytest": pytest_result,
    }


def evaluate_output_diff(output_text, *, fixture_path, workspace_path, run_checks=True):
    diff_text = combined_diff(output_text)
    workspace_path = Path(workspace_path)
    fixture_path = Path(fixture_path)

    if workspace_path.exists():
        shutil.rmtree(workspace_path)
    shutil.copytree(fixture_path, workspace_path)

    result = {
        "diff_found": bool(diff_text),
        "patch_check": "pending",
        "patch_applied": "pending",
        "django_check": "skipped",
        "pytest": "skipped",
        "notes": "",
    }
    if not diff_text:
        result.update(
            {
                "patch_check": "failed",
                "patch_applied": "failed",
                "notes": "No unified diff block found.",
            }
        )
        return result

    check = run_command(
        ["git", "apply", "--recount", "--check", "-"],
        cwd=workspace_path,
        input_text=diff_text,
    )
    result["patch_check"] = check["status"]
    if check["status"] != "passed":
        result.update(
            {
                "patch_applied": "failed",
                "notes": command_summary(check),
            }
        )
        return result

    apply_result = run_command(
        ["git", "apply", "--recount", "-"],
        cwd=workspace_path,
        input_text=diff_text,
    )
    result["patch_applied"] = apply_result["status"]
    if apply_result["status"] != "passed":
        result["notes"] = command_summary(apply_result)
        return result

    if run_checks:
        checks = run_optional_checks(workspace_path)
        result["django_check"] = checks["django_check"]["status"]
        result["pytest"] = checks["pytest"]["status"]
        notes = []
        for name in ["django_check", "pytest"]:
            note = checks[name].get("notes", "")
            if note:
                notes.append(f"{name}: {note}")
        result["notes"] = " | ".join(notes)
    else:
        result["notes"] = "Patch applied; runtime checks skipped."

    return result


def load_answer_keys(iteration):
    cases = {}
    for path in sorted((Path(iteration) / "answer-key").glob("*.json")):
        data = load_json(path)
        cases[path.stem] = data
    return cases


def summarize(records):
    summary = {}
    for variant in VARIANTS:
        selected = [record for record in records if record["variant"] == variant]
        summary[variant] = {
            "count": len(selected),
            "diff_found": sum(1 for record in selected if record["diff_found"]),
            "patch_check": sum(1 for record in selected if record["patch_check"] == "passed"),
            "patch_applied": sum(1 for record in selected if record["patch_applied"] == "passed"),
            "django_check_passed": sum(1 for record in selected if record["django_check"] == "passed"),
            "pytest_passed": sum(1 for record in selected if record["pytest"] == "passed"),
        }
    return summary


def evaluate_iteration(iteration, *, root, run_checks=True):
    iteration = Path(iteration)
    root = Path(root)
    cases = load_answer_keys(iteration)
    records = []

    for case_id, case in cases.items():
        fixture = case.get("fixture", "")
        if not fixture:
            continue
        fixture_path = root / fixture
        for variant in VARIANTS:
            output_path = iteration / variant / f"{case_id}.output.md"
            if not output_path.exists():
                continue
            workspace_path = iteration / "real-repo-work" / variant / case_id
            result = evaluate_output_diff(
                output_path.read_text(),
                fixture_path=fixture_path,
                workspace_path=workspace_path,
                run_checks=run_checks,
            )
            records.append(
                {
                    "case_id": case_id,
                    "variant": variant,
                    "fixture": fixture,
                    "workspace": str(workspace_path.relative_to(iteration)),
                    **result,
                }
            )

    payload = {
        "summary": summarize(records),
        "records": records,
    }
    output_path = iteration / "real_repo_evaluation.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate real-repo unified diffs by applying them to fixture copies."
    )
    parser.add_argument("iteration", help="Evaluation iteration directory.")
    parser.add_argument("--root", default=".", help="Repository root containing fixture paths.")
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Only run git apply checks; skip Django check and pytest.",
    )
    args = parser.parse_args()

    output_path = evaluate_iteration(
        args.iteration,
        root=args.root,
        run_checks=not args.skip_checks,
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
