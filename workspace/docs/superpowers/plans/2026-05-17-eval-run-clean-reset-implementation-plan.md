# Eval Run Clean Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce one eval run naming scheme, metadata-driven latest report selection, and a clean reset for generated eval artifacts across all buckets.

**Architecture:** Add a small shared run identity module, then make runners, validators, and renderers consume that module instead of duplicating run-id logic. Add one cleanup script that deletes only generated eval artifacts after an explicit confirmation flag. Keep eval definitions and plugin source untouched.

**Tech Stack:** Python standard library, `unittest`, existing `workspace/scripts` entrypoints, generated static HTML reports.

---

## File Structure

- Create `workspace/scripts/eval_run_identity.py`
  - Owns production run-id parsing, generation, metadata schema, metadata loading/writing, and latest candidate checks.
- Create `workspace/scripts/test_eval_run_identity.py`
  - Unit tests for run-id format, metadata, and latest candidate filtering.
- Create `workspace/scripts/clean_eval_artifacts.py`
  - Dry-run and confirmed deletion for generated `runs`, `latest`, and `lv_up_plan` iteration files.
- Create `workspace/scripts/test_clean_eval_artifacts.py`
  - Unit tests for cleanup discovery, deletion scope, and preservation scope.
- Modify `workspace/scripts/run_eval_bucket.py`
  - Adds metadata CLI options, compliant default run-id generation, and `RUN_META.json` writing.
- Modify `workspace/scripts/run_initial_eval.py`
  - Generates per-bucket run IDs when `--run-id` is omitted and rejects one explicit run ID for multiple buckets.
- Modify `workspace/scripts/evaluate_eval_run.py`
  - Uses shared safe run-id validation.
- Modify `workspace/scripts/validate_eval_run.py`
  - Validates `RUN_META.json` and rejects metadata mismatch for production runs.
- Modify `workspace/scripts/render_eval_review_html.py`
  - Reads metadata, displays try/scope/topic/created_at, and chooses latest scored reports using metadata.
- Modify related tests:
  - `workspace/scripts/test_run_eval_bucket.py`
  - `workspace/scripts/test_run_initial_eval.py`
  - `workspace/scripts/test_evaluate_eval_run.py`
  - `workspace/scripts/test_validate_eval_run.py`
  - `workspace/scripts/test_render_eval_review_html.py`

### Shared Values

Use these constants in `eval_run_identity.py`:

```python
RUN_ID_PATTERN = re.compile(
    r"^(?P<stamp>\d{8}-\d{6})-"
    r"(?P<bucket>response|code|plugin|runtime|source|workflow)-"
    r"try(?P<try_number>\d{2})-"
    r"(?P<scope>full|targeted|adjacent|rerun|manual)-"
    r"(?P<topic>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
TOPIC_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SCOPE_CHOICES = ("full", "targeted", "adjacent", "rerun", "manual")
```

---

## Task 1: Shared Run Identity Module

**Files:**
- Create: `workspace/scripts/eval_run_identity.py`
- Create: `workspace/scripts/test_eval_run_identity.py`

- [ ] **Step 1: Write failing run-id and metadata tests**

Create `workspace/scripts/test_eval_run_identity.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import eval_run_identity as identity


class EvalRunIdentityTests(unittest.TestCase):
    def test_build_and_parse_run_id(self) -> None:
        created = datetime(2026, 5, 17, 14, 30, 12, tzinfo=ZoneInfo("Asia/Seoul"))

        run_id = identity.build_run_id(
            bucket="runtime",
            try_number=1,
            scope="full",
            topic="current-baseline",
            created_at=created,
        )

        self.assertEqual(run_id, "20260517-143012-runtime-try01-full-current-baseline")
        parsed = identity.parse_run_id(run_id)
        self.assertEqual(parsed.bucket, "runtime")
        self.assertEqual(parsed.try_number, 1)
        self.assertEqual(parsed.scope, "full")
        self.assertEqual(parsed.topic, "current-baseline")
        self.assertEqual(parsed.created_at, "2026-05-17T14:30:12+09:00")

    def test_invalid_production_run_ids_are_rejected(self) -> None:
        invalid_ids = [
            "",
            "../escape",
            "nested/run",
            "/tmp/escape",
            "20260517-runtime-try1-full-current-baseline",
            "20260517-143012-runtime-try1-full-current-baseline",
            "20260517-143012-runtime-try01-smoke-current-baseline",
            "20260517-143012-runtime-try01-full-Current",
        ]

        for run_id in invalid_ids:
            with self.subTest(run_id=run_id):
                with self.assertRaises(SystemExit):
                    identity.validate_production_run_id(run_id)

    def test_write_and_load_run_meta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "20260517-143012-runtime-try01-full-current-baseline"
            run_dir = root / "workspace/develop/eval/runtime/runs" / run_id
            run_dir.mkdir(parents=True)

            meta = identity.write_run_meta(
                run_dir,
                run_id=run_id,
                lv_up_analysis="workspace/develop/lv_up_plan/runtime/analysis/20260517-143000-try01-current-baseline.md",
                lv_up_plan="workspace/develop/lv_up_plan/runtime/plan/20260517-143000-try01-current-baseline.md",
            )

            self.assertEqual(meta["bucket"], "runtime")
            self.assertEqual(meta["try_number"], 1)
            self.assertEqual(meta["scope"], "full")
            self.assertEqual(meta["topic"], "current-baseline")
            loaded = identity.load_run_meta(run_dir)
            self.assertEqual(loaded["run_id"], run_id)

    def test_invalid_meta_mismatch_reports_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_id = "20260517-143012-runtime-try01-full-current-baseline"
            run_dir = Path(tmp) / run_id
            run_dir.mkdir()
            (run_dir / "RUN_META.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "run_id": run_id,
                        "bucket": "plugin",
                        "try_number": 1,
                        "scope": "full",
                        "topic": "current-baseline",
                        "created_at": "2026-05-17T14:30:12+09:00",
                        "lv_up_analysis": "",
                        "lv_up_plan": "",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            errors = identity.validate_run_meta(run_dir)

        self.assertIn("RUN_META.json bucket must match run id bucket: runtime", errors)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new test and confirm it fails**

Run:

```bash
python3 -m unittest workspace/scripts/test_eval_run_identity.py
```

Expected: FAIL with `ModuleNotFoundError: No module named 'eval_run_identity'`.

- [ ] **Step 3: Implement `eval_run_identity.py`**

Create `workspace/scripts/eval_run_identity.py`:

```python
#!/usr/bin/env python3
"""Shared eval run naming and metadata helpers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
SCOPE_CHOICES = ("full", "targeted", "adjacent", "rerun", "manual")
RUN_META_FILENAME = "RUN_META.json"
RUN_ID_PATTERN = re.compile(
    r"^(?P<stamp>\d{8}-\d{6})-"
    r"(?P<bucket>response|code|plugin|runtime|source|workflow)-"
    r"try(?P<try_number>\d{2})-"
    r"(?P<scope>full|targeted|adjacent|rerun|manual)-"
    r"(?P<topic>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
TOPIC_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class RunIdentity:
    run_id: str
    stamp: str
    bucket: str
    try_number: int
    scope: str
    topic: str
    created_at: str


def now_kst() -> datetime:
    return datetime.now(ZoneInfo("Asia/Seoul"))


def timestamp_text(created_at: datetime) -> str:
    return created_at.astimezone(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d-%H%M%S")


def parse_created_at(stamp: str) -> str:
    parsed = datetime.strptime(stamp, "%Y%m%d-%H%M%S")
    return parsed.replace(tzinfo=ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")


def validate_topic(topic: str) -> str:
    if not TOPIC_PATTERN.fullmatch(topic):
        raise SystemExit(f"invalid run topic slug: {topic}")
    return topic


def validate_try_number(try_number: int) -> int:
    if try_number < 1 or try_number > 99:
        raise SystemExit(f"try number must be between 1 and 99: {try_number}")
    return try_number


def build_run_id(
    *,
    bucket: str,
    try_number: int,
    scope: str,
    topic: str,
    created_at: datetime | None = None,
) -> str:
    if bucket not in BUCKETS:
        raise SystemExit(f"unsupported bucket: {bucket}")
    if scope not in SCOPE_CHOICES:
        raise SystemExit(f"unsupported run scope: {scope}")
    validate_try_number(try_number)
    validate_topic(topic)
    stamp = timestamp_text(created_at or now_kst())
    return f"{stamp}-{bucket}-try{try_number:02d}-{scope}-{topic}"


def parse_run_id(run_id: str) -> RunIdentity:
    match = RUN_ID_PATTERN.fullmatch(run_id)
    if not match:
        raise SystemExit(f"invalid production run id: {run_id}")
    stamp = match.group("stamp")
    return RunIdentity(
        run_id=run_id,
        stamp=stamp,
        bucket=match.group("bucket"),
        try_number=int(match.group("try_number")),
        scope=match.group("scope"),
        topic=match.group("topic"),
        created_at=parse_created_at(stamp),
    )


def validate_production_run_id(run_id: str) -> str:
    path = Path(run_id)
    if (
        not run_id
        or path.is_absolute()
        or len(path.parts) != 1
        or run_id in {".", ".."}
        or ".." in run_id
        or "/" in run_id
        or "\\" in run_id
    ):
        raise SystemExit(f"unsafe run id: {run_id}")
    parse_run_id(run_id)
    return run_id


def build_run_meta(
    *,
    run_id: str,
    lv_up_analysis: str = "",
    lv_up_plan: str = "",
) -> dict[str, Any]:
    parsed = parse_run_id(run_id)
    return {
        "schema_version": 1,
        "run_id": parsed.run_id,
        "bucket": parsed.bucket,
        "try_number": parsed.try_number,
        "scope": parsed.scope,
        "topic": parsed.topic,
        "created_at": parsed.created_at,
        "lv_up_analysis": lv_up_analysis,
        "lv_up_plan": lv_up_plan,
    }


def write_run_meta(
    run_dir: Path,
    *,
    run_id: str,
    lv_up_analysis: str = "",
    lv_up_plan: str = "",
) -> dict[str, Any]:
    meta = build_run_meta(
        run_id=run_id,
        lv_up_analysis=lv_up_analysis,
        lv_up_plan=lv_up_plan,
    )
    path = run_dir / RUN_META_FILENAME
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


def load_run_meta(run_dir: Path) -> dict[str, Any]:
    path = run_dir / RUN_META_FILENAME
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_run_meta(run_dir: Path) -> list[str]:
    path = run_dir / RUN_META_FILENAME
    if not path.is_file():
        return [f"missing RUN_META.json: {path}"]
    try:
        meta = load_run_meta(run_dir)
    except (json.JSONDecodeError, ValueError) as exc:
        return [f"invalid RUN_META.json: {path}: {exc}"]

    errors: list[str] = []
    run_id = str(meta.get("run_id") or "")
    try:
        parsed = parse_run_id(run_id)
    except SystemExit:
        return [f"RUN_META.json run_id is invalid: {run_id}"]

    if run_dir.name != run_id:
        errors.append(f"RUN_META.json run_id must match directory name: {run_dir.name}")
    for key, expected in (
        ("bucket", parsed.bucket),
        ("try_number", parsed.try_number),
        ("scope", parsed.scope),
        ("topic", parsed.topic),
        ("created_at", parsed.created_at),
    ):
        if meta.get(key) != expected:
            errors.append(f"RUN_META.json {key} must match run id {key}: {expected}")

    for key in ("lv_up_analysis", "lv_up_plan"):
        if key not in meta or not isinstance(meta.get(key), str):
            errors.append(f"RUN_META.json {key} must be a string")
    if meta.get("schema_version") != 1:
        errors.append("RUN_META.json schema_version must be 1")
    return errors


def has_answer_oracle_evaluation(run_dir: Path) -> bool:
    raw_dir = run_dir / "raw"
    return raw_dir.is_dir() and any(raw_dir.glob("*-answer-oracle-evaluation.json"))


def exit_artifacts_are_clean(run_dir: Path) -> bool:
    raw_dir = run_dir / "raw"
    exit_files = list(raw_dir.glob("*-exit.txt")) if raw_dir.is_dir() else []
    if not exit_files:
        return True
    return all(path.read_text(encoding="utf-8", errors="replace").strip() == "0" for path in exit_files)
```

- [ ] **Step 4: Run the new test and confirm it passes**

Run:

```bash
python3 -m unittest workspace/scripts/test_eval_run_identity.py
```

Expected: OK.

- [ ] **Step 5: Commit Task 1**

Run:

```bash
git add workspace/scripts/eval_run_identity.py workspace/scripts/test_eval_run_identity.py
git commit -m "Add eval run identity helpers"
```

---

## Task 2: Cleanup Script For Generated Artifacts

**Files:**
- Create: `workspace/scripts/clean_eval_artifacts.py`
- Create: `workspace/scripts/test_clean_eval_artifacts.py`

- [ ] **Step 1: Write failing cleanup tests**

Create `workspace/scripts/test_clean_eval_artifacts.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("clean_eval_artifacts.py")


def load_cleaner():
    spec = importlib.util.spec_from_file_location("clean_eval_artifacts", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CleanEvalArtifactsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cleaner = load_cleaner()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.eval_root = self.root / "workspace/develop/eval"
        self.lv_root = self.root / "workspace/develop/lv_up_plan"
        self.cleaner.REPO_ROOT = self.root
        self.cleaner.EVAL_ROOT = self.eval_root
        self.cleaner.LV_UP_PLAN_ROOT = self.lv_root

    def write_tree(self) -> None:
        for bucket in self.cleaner.BUCKETS:
            (self.eval_root / bucket / "runs/run-one/raw").mkdir(parents=True)
            (self.eval_root / bucket / "latest").mkdir(parents=True)
            (self.eval_root / bucket / "eval_goal.md").write_text("goal\n", encoding="utf-8")
            (self.eval_root / bucket / "cases/plugin/public").mkdir(parents=True)
            (self.eval_root / bucket / "answer").mkdir(parents=True)
            for section in ("analysis", "plan", "review"):
                path = self.lv_root / bucket / section / "20260517-120000-try01-topic.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("iteration\n", encoding="utf-8")
        (self.lv_root / "bucket_goal_loop_prompt.md").write_text("prompt\n", encoding="utf-8")

    def test_collect_delete_targets_only_generated_artifacts(self) -> None:
        self.write_tree()

        targets = self.cleaner.collect_delete_targets()
        target_text = sorted(path.relative_to(self.root).as_posix() for path in targets)

        self.assertIn("workspace/develop/eval/runtime/runs/run-one", target_text)
        self.assertIn("workspace/develop/eval/runtime/latest", target_text)
        self.assertIn(
            "workspace/develop/lv_up_plan/runtime/analysis/20260517-120000-try01-topic.md",
            target_text,
        )
        self.assertNotIn("workspace/develop/eval/runtime/eval_goal.md", target_text)
        self.assertNotIn("workspace/develop/lv_up_plan/bucket_goal_loop_prompt.md", target_text)

    def test_dry_run_does_not_delete(self) -> None:
        self.write_tree()

        result = self.cleaner.main([])

        self.assertEqual(result, 0)
        self.assertTrue((self.eval_root / "runtime/runs/run-one").exists())
        self.assertTrue((self.lv_root / "runtime/analysis/20260517-120000-try01-topic.md").exists())

    def test_confirmed_delete_removes_targets_and_preserves_sources(self) -> None:
        self.write_tree()

        result = self.cleaner.main(["--confirm-delete-generated-eval-artifacts"])

        self.assertEqual(result, 0)
        self.assertFalse((self.eval_root / "runtime/runs/run-one").exists())
        self.assertFalse((self.eval_root / "runtime/latest").exists())
        self.assertFalse((self.lv_root / "runtime/analysis/20260517-120000-try01-topic.md").exists())
        self.assertTrue((self.eval_root / "runtime/eval_goal.md").is_file())
        self.assertTrue((self.lv_root / "bucket_goal_loop_prompt.md").is_file())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run cleanup tests and confirm failure**

Run:

```bash
python3 -m unittest workspace/scripts/test_clean_eval_artifacts.py
```

Expected: FAIL with `FileNotFoundError` or module import failure because `clean_eval_artifacts.py` does not exist.

- [ ] **Step 3: Implement cleanup script**

Create `workspace/scripts/clean_eval_artifacts.py`:

```python
#!/usr/bin/env python3
"""Clean generated eval run and lv_up_plan iteration artifacts."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "workspace/develop/eval"
LV_UP_PLAN_ROOT = REPO_ROOT / "workspace/develop/lv_up_plan"
BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
ITERATION_DIRS = ("analysis", "plan", "review")
CONFIRM_FLAG = "--confirm-delete-generated-eval-artifacts"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        CONFIRM_FLAG,
        dest="confirmed",
        action="store_true",
        help="Delete generated eval artifacts. Without this flag the script only prints targets.",
    )
    return parser.parse_args(argv)


def children(path: Path) -> list[Path]:
    if not path.is_dir():
        return []
    return sorted(path.iterdir())


def collect_delete_targets() -> list[Path]:
    targets: list[Path] = []
    for bucket in BUCKETS:
        targets.extend(children(EVAL_ROOT / bucket / "runs"))
        targets.extend(children(EVAL_ROOT / bucket / "latest"))
        for section in ITERATION_DIRS:
            targets.extend(children(LV_UP_PLAN_ROOT / bucket / section))
    return targets


def remove_target(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    targets = collect_delete_targets()
    mode = "DELETE" if args.confirmed else "DRY-RUN"
    print(f"{mode}: {len(targets)} generated eval artifact path(s)")
    for path in targets:
        print(path.relative_to(REPO_ROOT).as_posix())
    if args.confirmed:
        for path in targets:
            remove_target(path)
    else:
        print(f"Re-run with {CONFIRM_FLAG} to delete these paths.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run cleanup tests and confirm pass**

Run:

```bash
python3 -m unittest workspace/scripts/test_clean_eval_artifacts.py
```

Expected: OK.

- [ ] **Step 5: Commit Task 2**

Run:

```bash
git add workspace/scripts/clean_eval_artifacts.py workspace/scripts/test_clean_eval_artifacts.py
git commit -m "Add generated eval artifact cleanup script"
```

---

## Task 3: Runner Metadata And Production Run ID Enforcement

**Files:**
- Modify: `workspace/scripts/run_eval_bucket.py`
- Modify: `workspace/scripts/test_run_eval_bucket.py`

- [ ] **Step 1: Add failing runner tests**

Append tests to `RunEvalBucketTests` in `workspace/scripts/test_run_eval_bucket.py`:

```python
    def test_skip_exec_generates_compliant_run_id_and_meta_when_run_id_omitted(self) -> None:
        self.write_case()

        result = self.runner.main(
            [
                "--bucket",
                "response",
                "--try-number",
                "1",
                "--scope",
                "full",
                "--topic",
                "current-baseline",
                "--workspace-root",
                str(self.workspace_root),
                "--skip-exec",
            ]
        )

        self.assertEqual(result, 0)
        runs = list((self.runner.common.EVAL_ROOT / "response/runs").iterdir())
        self.assertEqual(len(runs), 1)
        run_id = runs[0].name
        self.assertRegex(run_id, r"^\d{8}-\d{6}-response-try01-full-current-baseline$")
        meta = json.loads((runs[0] / "RUN_META.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["run_id"], run_id)
        self.assertEqual(meta["bucket"], "response")
        self.assertEqual(meta["try_number"], 1)
        self.assertEqual(meta["scope"], "full")
        self.assertEqual(meta["topic"], "current-baseline")

    def test_explicit_invalid_production_run_id_is_rejected(self) -> None:
        self.write_case()

        with self.assertRaises(SystemExit) as raised:
            self.runner.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "run-one",
                    "--workspace-root",
                    str(self.workspace_root),
                    "--skip-exec",
                ]
            )

        self.assertIn("invalid production run id", str(raised.exception))
```

- [ ] **Step 2: Run focused runner tests and confirm failure**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_eval_bucket.py -k "run_id or meta"
```

Expected: FAIL because the runner has no `--try-number`, `--scope`, `--topic`, and does not write `RUN_META.json`.

- [ ] **Step 3: Update `run_eval_bucket.py` imports and args**

Modify the import block:

```python
import eval_run_common as common
import eval_run_identity as run_identity
import extract_subagent_trace
```

Add parser options:

```python
    parser.add_argument("--try-number", type=int, default=1)
    parser.add_argument("--scope", choices=run_identity.SCOPE_CHOICES, default="full")
    parser.add_argument("--topic", default="current-baseline")
    parser.add_argument("--lv-up-analysis", default="")
    parser.add_argument("--lv-up-plan", default="")
```

- [ ] **Step 4: Replace `validate_run_id` and default generation**

Replace the local `validate_run_id` body with:

```python
def validate_run_id(run_id: str) -> str:
    return run_identity.validate_production_run_id(run_id)
```

In `main`, replace:

```python
    run_id = validate_run_id(args.run_id or f"{now_text()}-{args.bucket}-eval")
```

with:

```python
    if args.run_id:
        run_id = validate_run_id(args.run_id)
    else:
        run_id = run_identity.build_run_id(
            bucket=args.bucket,
            try_number=args.try_number,
            scope=args.scope,
            topic=args.topic,
        )
```

- [ ] **Step 5: Write metadata after `RUN_ID.txt`**

After:

```python
    common.write_text(run_dir / "RUN_ID.txt", run_id + "\n")
```

add:

```python
    run_identity.write_run_meta(
        run_dir,
        run_id=run_id,
        lv_up_analysis=args.lv_up_analysis,
        lv_up_plan=args.lv_up_plan,
    )
```

- [ ] **Step 6: Run runner tests and update old synthetic IDs**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_eval_bucket.py
```

Expected: existing tests using `--run-id run-one` now fail. Replace production-entrypoint run IDs in this test file with compliant IDs such as:

```python
"20260517-143012-response-try01-full-current-baseline"
"20260517-143013-response-try01-targeted-case-response-one"
"20260517-143014-code-try01-targeted-case-code-one"
```

Keep synthetic IDs only inside helper paths that do not call `run_eval_bucket.main`.

- [ ] **Step 7: Run runner tests again**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_eval_bucket.py
```

Expected: OK.

- [ ] **Step 8: Commit Task 3**

Run:

```bash
git add workspace/scripts/run_eval_bucket.py workspace/scripts/test_run_eval_bucket.py
git commit -m "Enforce eval bucket run identity metadata"
```

---

## Task 4: Orchestrator, Evaluator, And Validator Integration

**Files:**
- Modify: `workspace/scripts/run_initial_eval.py`
- Modify: `workspace/scripts/evaluate_eval_run.py`
- Modify: `workspace/scripts/validate_eval_run.py`
- Modify: `workspace/scripts/test_run_initial_eval.py`
- Modify: `workspace/scripts/test_evaluate_eval_run.py`
- Modify: `workspace/scripts/test_validate_eval_run.py`

- [ ] **Step 1: Add failing orchestrator tests**

Add tests to `RunInitialEvalTests`:

```python
    def test_all_bucket_without_run_id_generates_per_bucket_run_ids(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--bucket",
                    "runtime",
                    "--try-number",
                    "1",
                    "--scope",
                    "full",
                    "--topic",
                    "current-baseline",
                    "--skip-exec",
                    "--skip-oracle",
                ]
            )

        self.assertEqual(result, 0)
        runner_commands = [
            command for command in self.commands if Path(command[1]).name == "run_eval_bucket.py"
        ]
        run_ids = [
            command[command.index("--run-id") + 1]
            for command in runner_commands
        ]
        self.assertEqual(len(run_ids), 2)
        self.assertRegex(run_ids[0], r"^\d{8}-\d{6}-response-try01-full-current-baseline$")
        self.assertRegex(run_ids[1], r"^\d{8}-\d{6}-runtime-try01-full-current-baseline$")

    def test_explicit_run_id_with_multiple_buckets_is_rejected(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--bucket",
                    "runtime",
                    "--run-id",
                    "20260517-143012-response-try01-full-current-baseline",
                ]
            )

        self.assertIn("explicit --run-id can only be used with one bucket", str(raised.exception))
```

- [ ] **Step 2: Add failing validator metadata test**

Add a test to `ValidateEvalRunTests`:

```python
    def test_missing_run_meta_is_invalid(self) -> None:
        run_id = "20260517-143012-response-try01-full-current-baseline"
        self.write_valid_run(run_id=run_id)

        with self.assertRaises(SystemExit) as raised:
            self.validator.main(["--bucket", "response", "--run-id", run_id])

        self.assertIn("missing RUN_META.json", str(raised.exception))
```

- [ ] **Step 3: Run focused tests and confirm failure**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_initial_eval.py -k "run_id or bucket"
python3 -m unittest workspace/scripts/test_validate_eval_run.py -k "run_meta"
```

Expected: FAIL because metadata options and metadata validation are not implemented.

- [ ] **Step 4: Update `run_initial_eval.py`**

Import the helper:

```python
import eval_run_identity as run_identity
```

Add args:

```python
    parser.add_argument("--try-number", type=int, default=1)
    parser.add_argument("--scope", choices=run_identity.SCOPE_CHOICES, default="full")
    parser.add_argument("--topic", default="current-baseline")
    parser.add_argument("--lv-up-analysis", default="")
    parser.add_argument("--lv-up-plan", default="")
```

Replace local `validate_run_id` with:

```python
def validate_run_id(run_id: str) -> str:
    return run_identity.validate_production_run_id(run_id)
```

Add helper:

```python
def run_id_for_bucket(args: argparse.Namespace, bucket: str, bucket_count: int) -> str:
    if args.run_id:
        if bucket_count != 1:
            raise SystemExit("explicit --run-id can only be used with one bucket")
        parsed = run_identity.parse_run_id(validate_run_id(args.run_id))
        if parsed.bucket != bucket:
            raise SystemExit(f"--run-id bucket {parsed.bucket} does not match selected bucket {bucket}")
        return args.run_id
    return run_identity.build_run_id(
        bucket=bucket,
        try_number=args.try_number,
        scope=args.scope,
        topic=args.topic,
    )
```

Update `runner_command` to pass metadata args:

```python
    command.extend(
        [
            "--lv-up-analysis",
            args.lv_up_analysis,
            "--lv-up-plan",
            args.lv_up_plan,
        ]
    )
```

In `main`, compute `run_id` per bucket inside the loop:

```python
    buckets = selected_buckets(args.bucket)
    ok = True
    for bucket in buckets:
        run_id = run_id_for_bucket(args, bucket, len(buckets))
        ok = run_bucket(args, bucket, run_id) and ok
        if not ok and not args.keep_going:
            break
    return 0 if ok else 1
```

- [ ] **Step 5: Update `evaluate_eval_run.py`**

Import helper:

```python
import eval_run_identity as run_identity
```

Replace local `validate_run_id` with:

```python
def validate_run_id(run_id: str) -> str:
    return run_identity.validate_production_run_id(run_id)
```

- [ ] **Step 6: Update `validate_eval_run.py`**

Import helper:

```python
import eval_run_identity as run_identity
```

Replace local `validate_run_id` with:

```python
def validate_run_id(run_id: str) -> str:
    return run_identity.validate_production_run_id(run_id)
```

After `run_dir` and `raw_dir` are resolved in `main`, add:

```python
    meta_errors = run_identity.validate_run_meta(run_dir)
    if meta_errors:
        raise SystemExit("\n".join(meta_errors))
```

Update `write_valid_run` helper in `test_validate_eval_run.py` to write metadata when `run_id` is compliant:

```python
        if self.validator.run_identity.RUN_ID_PATTERN.fullmatch(run_id):
            self.validator.run_identity.write_run_meta(run_dir, run_id=run_id)
```

- [ ] **Step 7: Update old production-entrypoint test IDs**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_initial_eval.py workspace/scripts/test_evaluate_eval_run.py workspace/scripts/test_validate_eval_run.py
```

Expected: failures from old `run-one` IDs. Replace IDs passed to production `main()` calls with compliant IDs. Keep non-entrypoint helper IDs synthetic only when no production validation is invoked.

- [ ] **Step 8: Run integration tests again**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_initial_eval.py workspace/scripts/test_evaluate_eval_run.py workspace/scripts/test_validate_eval_run.py
```

Expected: OK.

- [ ] **Step 9: Commit Task 4**

Run:

```bash
git add workspace/scripts/run_initial_eval.py workspace/scripts/evaluate_eval_run.py workspace/scripts/validate_eval_run.py workspace/scripts/test_run_initial_eval.py workspace/scripts/test_evaluate_eval_run.py workspace/scripts/test_validate_eval_run.py
git commit -m "Validate eval run metadata across entrypoints"
```

---

## Task 5: Renderer Metadata Latest Selection And Display

**Files:**
- Modify: `workspace/scripts/render_eval_review_html.py`
- Modify: `workspace/scripts/test_render_eval_review_html.py`

- [ ] **Step 1: Add failing renderer tests**

In `test_render_eval_review_html.py`, update `write_case` so it can write metadata for compliant IDs:

```python
        if self.renderer.run_identity.RUN_ID_PATTERN.fullmatch(run_id):
            self.renderer.run_identity.write_run_meta(bucket_root / f"runs/{run_id}", run_id=run_id)
```

Add a test:

```python
    def test_latest_scored_report_uses_run_meta_created_at(self) -> None:
        old_run_id = "20260517-100000-runtime-try01-full-current-baseline"
        new_run_id = "20260517-110000-runtime-try01-targeted-prompt-exposure"
        self.write_case(bucket="runtime", case_id="case-runtime-one", run_id=old_run_id)
        self.write_case(bucket="runtime", case_id="case-runtime-one", run_id=new_run_id)

        latest = self.renderer.latest_scored_report_path("runtime")

        self.assertEqual(latest, self.renderer.report_path("runtime", new_run_id))

    def test_metadata_less_run_is_excluded_from_latest_selection(self) -> None:
        legacy_run = self.write_case(bucket="runtime", case_id="case-runtime-one", run_id="legacy-run")
        current_run_id = "20260517-110000-runtime-try01-targeted-prompt-exposure"
        self.write_case(bucket="runtime", case_id="case-runtime-one", run_id=current_run_id)
        (legacy_run / "RUN_META.json").unlink(missing_ok=True)

        latest = self.renderer.latest_scored_report_path("runtime")

        self.assertEqual(latest, self.renderer.report_path("runtime", current_run_id))
```

Add display assertions to an existing render test:

```python
        self.assertIn("try: 1", html)
        self.assertIn("scope: full", html)
        self.assertIn("topic: current-baseline", html)
        self.assertIn("created: 2026-05-17T10:00:00+09:00", html)
```

- [ ] **Step 2: Run renderer tests and confirm failure**

Run:

```bash
python3 -m unittest workspace/scripts/test_render_eval_review_html.py -k "latest or metadata"
```

Expected: FAIL because renderer still uses raw mtime and does not expose metadata.

- [ ] **Step 3: Update renderer imports and report data**

Add import:

```python
import eval_run_identity as run_identity
```

Add helper:

```python
def run_metadata(run_dir: Path) -> dict[str, object]:
    try:
        return run_identity.load_run_meta(run_dir)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return {}
```

In `build_report_data`, load metadata:

```python
    metadata = run_metadata(run_dir)
```

Add to returned data:

```python
        "run_meta": metadata,
```

- [ ] **Step 4: Replace latest scored selection**

Replace `latest_scored_run_dir` with:

```python
def latest_scored_run_dir(bucket: str) -> Path | None:
    runs_dir = EVAL_ROOT / bucket / "runs"
    if not runs_dir.is_dir():
        return None

    candidates: list[tuple[str, str, Path]] = []
    for path in runs_dir.iterdir():
        if not path.is_dir():
            continue
        errors = run_identity.validate_run_meta(path)
        if errors:
            continue
        if not run_identity.has_answer_oracle_evaluation(path):
            continue
        if not run_identity.exit_artifacts_are_clean(path):
            continue
        metadata = run_identity.load_run_meta(path)
        candidates.append((str(metadata["created_at"]), path.name, path))
    if not candidates:
        return None
    return sorted(candidates)[-1][2]
```

- [ ] **Step 5: Display metadata in the report meta line**

In `render_html`, add:

```python
    run_meta = data.get("run_meta") if isinstance(data.get("run_meta"), dict) else {}
    run_meta_text = ""
    if run_meta:
        run_meta_text = (
            f" · try: {escape(str(run_meta.get('try_number')))}"
            f" · scope: {escape(str(run_meta.get('scope')))}"
            f" · topic: {escape(str(run_meta.get('topic')))}"
            f" · created: {escape(str(run_meta.get('created_at')))}"
        )
```

Append `{run_meta_text}` inside the existing `<p class="meta">` line after the run ID.

- [ ] **Step 6: Run renderer tests**

Run:

```bash
python3 -m unittest workspace/scripts/test_render_eval_review_html.py
```

Expected: OK after old latest-selection tests are updated to create compliant metadata.

- [ ] **Step 7: Commit Task 5**

Run:

```bash
git add workspace/scripts/render_eval_review_html.py workspace/scripts/test_render_eval_review_html.py
git commit -m "Select eval reports from run metadata"
```

---

## Task 6: Run Full Test Suite For Changed Scripts

**Files:**
- No new files.

- [ ] **Step 1: Run focused test suite**

Run:

```bash
python3 -m unittest \
  workspace/scripts/test_eval_run_identity.py \
  workspace/scripts/test_clean_eval_artifacts.py \
  workspace/scripts/test_run_eval_bucket.py \
  workspace/scripts/test_run_initial_eval.py \
  workspace/scripts/test_evaluate_eval_run.py \
  workspace/scripts/test_validate_eval_run.py \
  workspace/scripts/test_render_eval_review_html.py
```

Expected: OK.

- [ ] **Step 2: Run diff whitespace check**

Run:

```bash
git diff --check -- workspace/scripts workspace/docs/superpowers
```

Expected: no output.

- [ ] **Step 3: Commit verification-only test updates if needed**

If Step 1 required test-only corrections, commit them:

```bash
git add workspace/scripts
git commit -m "Align eval run tests with metadata naming"
```

If there are no additional changes, skip this commit.

---

## Task 7: Execute Clean Reset

**Files:**
- Generated artifacts under `workspace/develop/eval/<bucket>/runs/`
- Generated aliases under `workspace/develop/eval/<bucket>/latest/`
- Iteration files under `workspace/develop/lv_up_plan/<bucket>/{analysis,plan,review}/`

- [ ] **Step 1: Dry-run cleanup and inspect target count**

Run:

```bash
python3 workspace/scripts/clean_eval_artifacts.py
```

Expected:

```text
DRY-RUN: <number> generated eval artifact path(s)
...
Re-run with --confirm-delete-generated-eval-artifacts to delete these paths.
```

Check that output contains only:

```text
workspace/develop/eval/<bucket>/runs/<child>
workspace/develop/eval/<bucket>/latest/<child>
workspace/develop/lv_up_plan/<bucket>/analysis/<child>
workspace/develop/lv_up_plan/<bucket>/plan/<child>
workspace/develop/lv_up_plan/<bucket>/review/<child>
```

- [ ] **Step 2: Confirm cleanup**

Run:

```bash
python3 workspace/scripts/clean_eval_artifacts.py --confirm-delete-generated-eval-artifacts
```

Expected: same target list printed with `DELETE:` and exit code 0.

- [ ] **Step 3: Verify preserved files still exist**

Run:

```bash
python3 -c 'from pathlib import Path
buckets=("response","code","plugin","runtime","source","workflow")
for bucket in buckets:
    for rel in ("eval_goal.md","cases","answer"):
        path=Path("workspace/develop/eval")/bucket/rel
        assert path.exists(), path
assert Path("workspace/develop/lv_up_plan/bucket_goal_loop_prompt.md").exists()
print("preserved source and eval definitions exist")
'
```

Expected:

```text
preserved source and eval definitions exist
```

- [ ] **Step 4: Verify generated artifact dirs are empty or absent**

Run:

```bash
python3 -c 'from pathlib import Path
buckets=("response","code","plugin","runtime","source","workflow")
for bucket in buckets:
    for rel in ("runs","latest"):
        path=Path("workspace/develop/eval")/bucket/rel
        assert not path.exists() or not any(path.iterdir()), path
    for section in ("analysis","plan","review"):
        path=Path("workspace/develop/lv_up_plan")/bucket/section
        assert not path.exists() or not any(path.iterdir()), path
print("generated eval artifacts are clean")
'
```

Expected:

```text
generated eval artifacts are clean
```

- [ ] **Step 5: Commit cleanup result**

Run:

```bash
git add workspace/develop/eval workspace/develop/lv_up_plan
git commit -m "Clean reset generated eval artifacts"
```

---

## Task 8: Start New Naming Era With A Dry Production Run

**Files:**
- Generated one raw run under `workspace/develop/eval/response/runs/`

- [ ] **Step 1: Run a no-model dry production run for naming verification**

Run:

```bash
python3 workspace/scripts/run_eval_bucket.py \
  --bucket response \
  --try-number 1 \
  --scope full \
  --topic current-baseline \
  --case case-response-order-create \
  --skip-exec
```

Expected: exit code 0 and a run directory named like:

```text
workspace/develop/eval/response/runs/YYYYMMDD-HHMMSS-response-try01-full-current-baseline/
```

- [ ] **Step 2: Verify metadata exists**

Run:

```bash
python3 -c 'import json
from pathlib import Path
runs=sorted(Path("workspace/develop/eval/response/runs").iterdir())
run=runs[-1]
meta=json.loads((run/"RUN_META.json").read_text())
assert meta["run_id"] == run.name
assert meta["bucket"] == "response"
assert meta["try_number"] == 1
assert meta["scope"] == "full"
assert meta["topic"] == "current-baseline"
print(run.name)
'
```

Expected: prints the new compliant run ID.

- [ ] **Step 3: Remove the dry unscored run**

Run:

```bash
python3 workspace/scripts/clean_eval_artifacts.py --confirm-delete-generated-eval-artifacts
```

Expected: dry production run is removed. This keeps the reset state clean because the run has no oracle score.

- [ ] **Step 4: Commit if cleanup script behavior changed during verification**

Run only if Step 3 required code changes:

```bash
git add workspace/scripts
git commit -m "Fix eval artifact cleanup verification"
```

---

## Task 9: Final Verification

**Files:**
- No new files.

- [ ] **Step 1: Run focused test suite**

Run:

```bash
python3 -m unittest \
  workspace/scripts/test_eval_run_identity.py \
  workspace/scripts/test_clean_eval_artifacts.py \
  workspace/scripts/test_run_eval_bucket.py \
  workspace/scripts/test_run_initial_eval.py \
  workspace/scripts/test_evaluate_eval_run.py \
  workspace/scripts/test_validate_eval_run.py \
  workspace/scripts/test_render_eval_review_html.py
```

Expected: OK.

- [ ] **Step 2: Confirm there are no generated report aliases after reset**

Run:

```bash
find workspace/develop/eval -path '*/latest/*' -print
```

Expected: no output unless a later scored run has been intentionally generated.

- [ ] **Step 3: Confirm no legacy run directories remain**

Run:

```bash
find workspace/develop/eval -path '*/runs/*' -maxdepth 4 -print
```

Expected: no output after the cleanup verification run has been removed.

- [ ] **Step 4: Final diff review**

Run:

```bash
git status --short
git diff --stat
```

Expected: only intended code, test, docs, and cleanup changes remain.

---

## Self-Review

Spec coverage:

- Clean reset across all buckets: Task 2 and Task 7.
- New run-id format: Task 1 and Task 3.
- `lv_up_plan` deletion scope: Task 2 and Task 7.
- Metadata source of truth: Task 1, Task 3, Task 4, Task 5.
- Latest report selection from metadata: Task 5.
- Report display of try/scope/topic/created time: Task 5.
- Tests: Tasks 1 through 6 and Task 9.

Scope notes:

- This plan does not run model-backed full evals. It resets and enforces the future naming system. New scored reports require later model-backed `run_initial_eval.py` or `run_eval_bucket.py` execution under the new naming scheme.
- This plan intentionally deletes legacy generated artifacts instead of archiving them, matching the approved design.
