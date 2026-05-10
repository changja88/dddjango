# Initial Eval Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first reproducible end-to-end evaluation pipeline that runs baseline and with-dddjango variants, produces evaluator-only answer-oracle judgments, validates artifacts, and renders the existing HTML review report.

**Architecture:** Keep public cases and private answer oracles in the existing bucket structure. Add a small shared contract module, a generic bucket runner, an answer-oracle evaluator, a generic run validator, and a thin orchestration script. Existing `render_eval_review_html.py` remains the report surface and should consume the same oracle schema used by validation.

**Tech Stack:** Python 3 standard library, `unittest`, `subprocess`, Codex CLI, existing `workspace/develop/eval/{response,code,plugin,runtime,source,workflow}` buckets.

---

## File Structure

- Create: `workspace/scripts/eval_run_common.py`
  - Shared constants, bucket path resolution, selected case lookup, JSON extraction, oracle schema validation, and command/result file helpers.
- Create: `workspace/scripts/test_eval_run_common.py`
  - Unit coverage for bucket path resolution, case selection, JSON extraction, and oracle schema validation.
- Create: `workspace/scripts/run_eval_bucket.py`
  - Generic runner for one bucket. Writes raw variant outputs and prompt artifacts under `workspace/develop/eval/<bucket>/runs/<run-id>/raw/`.
- Create: `workspace/scripts/test_run_eval_bucket.py`
  - Unit coverage using temporary eval roots and fake command execution.
- Create: `workspace/scripts/evaluate_eval_run.py`
  - Private evaluator that reads public case, answer YAML, baseline output, with-ddjango output, and optional code artifacts, then writes `<case-id>-answer-oracle-evaluation.json`.
- Create: `workspace/scripts/test_evaluate_eval_run.py`
  - Unit coverage for evaluator prompt construction, strict JSON canonicalization, schema rejection, and command isolation.
- Create: `workspace/scripts/validate_eval_run.py`
  - Generic run validator for all buckets. Checks raw response artifacts, command artifacts, baseline isolation, oracle schema, and no stale/forbidden raw files.
- Create: `workspace/scripts/test_validate_eval_run.py`
  - Unit coverage for valid run, missing response, invalid oracle schema, stale prompt-input artifacts, and baseline contamination.
- Create: `workspace/scripts/run_initial_eval.py`
  - Thin orchestration command: run bucket variants, run answer-oracle evaluation, validate, render HTML.
- Create: `workspace/scripts/test_run_initial_eval.py`
  - Unit coverage for subprocess command ordering and `--keep-going` behavior.
- Modify: `workspace/scripts/render_eval_review_html.py`
  - Import shared oracle schema validation from `eval_run_common.py` instead of maintaining a second copy.
- Modify: `workspace/scripts/test_render_eval_review_html.py`
  - Keep existing behavior tests passing after the shared validation move.

Run artifacts under `workspace/develop/eval/*/runs/<run-id>/` stay uncommitted. Only scripts, tests, and documentation are committed.

---

### Task 1: Shared Eval Run Contract

**Files:**
- Create: `workspace/scripts/eval_run_common.py`
- Create: `workspace/scripts/test_eval_run_common.py`
- Modify: `workspace/scripts/render_eval_review_html.py`
- Modify: `workspace/scripts/test_render_eval_review_html.py`

- [ ] **Step 1: Write failing tests for shared helpers**

Add `workspace/scripts/test_eval_run_common.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("eval_run_common.py")


def load_common():
    spec = importlib.util.spec_from_file_location("eval_run_common", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvalRunCommonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.common = load_common()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.common.REPO_ROOT = self.root
        self.common.EVAL_ROOT = self.root / "workspace/develop/eval"

    def write_case(self, bucket: str, case_id: str) -> Path:
        path = self.common.EVAL_ROOT / bucket / "cases/plugin/public" / f"{case_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("사용자 요청입니다.\n", encoding="utf-8")
        return path

    def test_bucket_paths_use_existing_namespace(self) -> None:
        paths = self.common.bucket_paths("workflow")

        self.assertEqual(
            paths.public_cases_dir,
            self.common.EVAL_ROOT / "workflow/cases/plugin/public",
        )
        self.assertEqual(paths.answer_dir, self.common.EVAL_ROOT / "workflow/answer")
        self.assertEqual(paths.runs_dir, self.common.EVAL_ROOT / "workflow/runs")

    def test_selected_case_paths_reject_unknown_case(self) -> None:
        self.write_case("response", "case-response-one")

        with self.assertRaisesRegex(SystemExit, "Unknown case"):
            self.common.selected_case_paths("response", ["case-response-missing"])

    def test_extract_json_object_accepts_fenced_json(self) -> None:
        text = 'Here is the result:\\n```json\\n{"caseId": "case-a"}\\n```'

        value = self.common.extract_json_object(text)

        self.assertEqual(value, {"caseId": "case-a"})

    def test_validate_oracle_schema_requires_both_variants(self) -> None:
        error = self.common.validate_oracle_schema(
            {
                "caseId": "case-a",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "4 / 5",
                    "verdict": "pass",
                    "evaluation": "baseline ok",
                },
                "observations": ["with-dddjango missing"],
            },
            "case-a",
        )

        self.assertEqual(error, "with_dddjango must be an object")

    def test_validate_oracle_schema_accepts_summary_field(self) -> None:
        error = self.common.validate_oracle_schema(
            {
                "caseId": "case-a",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "2 / 5",
                    "verdict": "fail",
                    "evaluation_summary": "baseline weak",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "with-dddjango strong",
                },
                "observations": ["clear delta"],
            },
            "case-a",
        )

        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```bash
python3 -m unittest workspace/scripts/test_eval_run_common.py
```

Expected: fail because `workspace/scripts/eval_run_common.py` does not exist.

- [ ] **Step 3: Add the shared module**

Create `workspace/scripts/eval_run_common.py` with these public functions and constants:

```python
#!/usr/bin/env python3
"""Shared contracts for dddjango eval run scripts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "workspace/develop/eval"
BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
VARIANTS = ("baseline", "with-dddjango")


@dataclass(frozen=True)
class BucketPaths:
    bucket: str
    root: Path
    public_cases_dir: Path
    answer_dir: Path
    runs_dir: Path


def bucket_paths(bucket: str) -> BucketPaths:
    if bucket not in BUCKETS:
        raise SystemExit(f"Unknown bucket: {bucket}")
    root = EVAL_ROOT / bucket
    return BucketPaths(
        bucket=bucket,
        root=root,
        public_cases_dir=root / "cases/plugin/public",
        answer_dir=root / "answer",
        runs_dir=root / "runs",
    )


def selected_case_paths(bucket: str, selected: list[str] | None = None) -> list[Path]:
    paths = sorted(bucket_paths(bucket).public_cases_dir.glob("case-*.md"))
    if not selected:
        if not paths:
            raise SystemExit(f"No public cases found for bucket: {bucket}")
        return paths
    wanted = set(selected)
    found = {path.stem for path in paths}
    missing = sorted(wanted - found)
    if missing:
        raise SystemExit(f"Unknown case id(s) for {bucket}: {', '.join(missing)}")
    return [path for path in paths if path.stem in wanted]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_json_object(text: str) -> dict[str, Any]:
    fenced = re.search(r"```(?:json)?\\s*(\\{.*?\\})\\s*```", text, re.S)
    candidates = [fenced.group(1)] if fenced else []
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidates.append(text[first_brace : last_brace + 1])
    candidates.append(text.strip())
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("no JSON object found")


def has_non_empty_text(value: object) -> bool:
    return bool(str(value or "").strip())


def validate_oracle_schema(oracle: dict[str, object], case_id: str) -> str | None:
    if oracle.get("caseId") != case_id:
        return "caseId mismatch"
    if oracle.get("answerOracleEvaluated") is not True:
        return "answerOracleEvaluated must be true"
    for variant_key in ("baseline", "with_dddjango"):
        variant_oracle = oracle.get(variant_key)
        if not isinstance(variant_oracle, dict):
            return f"{variant_key} must be an object"
        if not has_non_empty_text(variant_oracle.get("score")):
            return f"{variant_key}.score is required"
        if not has_non_empty_text(variant_oracle.get("verdict")):
            return f"{variant_key}.verdict is required"
        if not (
            has_non_empty_text(variant_oracle.get("evaluation"))
            or has_non_empty_text(variant_oracle.get("evaluation_summary"))
        ):
            return f"{variant_key}.evaluation is required"
    observations = oracle.get("observations")
    if not isinstance(observations, list) or not observations:
        return "observations must be a non-empty list"
    return None
```

- [ ] **Step 4: Make the renderer import the shared schema validator**

In `workspace/scripts/render_eval_review_html.py`, import `validate_oracle_schema` from the new module and remove the local duplicate function plus `has_non_empty_text`.

Use this import near the top:

```python
from eval_run_common import validate_oracle_schema
```

Keep the existing call site:

```python
if oracle_state == "ready" and validate_oracle_schema(oracle, case_id) is not None:
    oracle_state = "invalid_schema"
```

- [ ] **Step 5: Run shared and renderer tests**

Run:

```bash
python3 -m unittest workspace/scripts/test_eval_run_common.py workspace/scripts/test_render_eval_review_html.py
```

Expected: all tests pass.

- [ ] **Step 6: Commit the shared contract**

```bash
git add workspace/scripts/eval_run_common.py workspace/scripts/test_eval_run_common.py workspace/scripts/render_eval_review_html.py workspace/scripts/test_render_eval_review_html.py
git commit -m "Add shared eval run contract"
```

---

### Task 2: Generic Bucket Runner

**Files:**
- Create: `workspace/scripts/run_eval_bucket.py`
- Create: `workspace/scripts/test_run_eval_bucket.py`

- [ ] **Step 1: Write failing tests for artifact generation**

Create `workspace/scripts/test_run_eval_bucket.py` with tests that call `main(argv)` against a temporary eval root and monkeypatch command execution:

```python
#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("run_eval_bucket.py")


def load_runner():
    spec = importlib.util.spec_from_file_location("run_eval_bucket", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RunEvalBucketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = load_runner()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.runner.REPO_ROOT = self.root
        self.runner.EVAL_ROOT = self.root / "workspace/develop/eval"

    def write_case(self, bucket: str = "response", case_id: str = "case-response-one") -> None:
        case_path = self.runner.EVAL_ROOT / bucket / "cases/plugin/public" / f"{case_id}.md"
        answer_path = self.runner.EVAL_ROOT / bucket / "answer" / f"{case_id}.yaml"
        case_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        case_path.write_text("사용자 요청입니다.\n", encoding="utf-8")
        answer_path.write_text(
            f"id: {case_id}\ncase_id: {case_id}\nbucket: {bucket}\nkind: {bucket}\n",
            encoding="utf-8",
        )

    def fake_run_command(self, command, *, prompt, cwd, timeout_seconds):
        stdout = "fake final response\n" if "exec" in command else '{"messages": []}\n'
        return subprocess.CompletedProcess(command, 0, stdout, "")

    def test_skip_exec_writes_required_raw_artifacts_for_both_variants(self) -> None:
        self.write_case()

        result = self.runner.main([
            "--bucket", "response",
            "--run-id", "run-one",
            "--skip-exec",
        ])

        self.assertEqual(result, 0)
        raw = self.runner.EVAL_ROOT / "response/runs/run-one/raw"
        self.assertTrue((raw / "case-response-one-public-prompt.md").is_file())
        self.assertTrue((raw / "case-response-one-operator-prompt.txt").is_file())
        self.assertTrue((raw / "case-response-one-baseline.txt").is_file())
        self.assertTrue((raw / "case-response-one-with-ddjango.txt").is_file())
        self.assertTrue((raw / "case-response-one-baseline-isolation.json").is_file())
        self.assertFalse((raw / "case-response-one-baseline-prompt-input.json").exists())

    def test_exec_mode_writes_command_exit_stdout_and_stderr(self) -> None:
        self.write_case()

        with patch.object(self.runner, "run_command", side_effect=self.fake_run_command):
            result = self.runner.main([
                "--bucket", "response",
                "--run-id", "run-two",
                "--case", "case-response-one",
            ])

        self.assertEqual(result, 0)
        raw = self.runner.EVAL_ROOT / "response/runs/run-two/raw"
        self.assertEqual((raw / "case-response-one-baseline-exit.txt").read_text(encoding="utf-8"), "0\n")
        self.assertEqual((raw / "case-response-one-with-ddjango-exit.txt").read_text(encoding="utf-8"), "0\n")
        self.assertIn("--ignore-user-config", (raw / "case-response-one-baseline-command.txt").read_text(encoding="utf-8"))
        self.assertNotIn("--ignore-user-config", (raw / "case-response-one-with-ddjango-command.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_eval_bucket.py
```

Expected: fail because `run_eval_bucket.py` does not exist.

- [ ] **Step 3: Implement `run_eval_bucket.py`**

Implement these behaviors:

- CLI:
  - `--bucket {response,code,plugin,runtime,source,workflow}` required
  - `--run-id` optional, default `YYYYMMDD-HHMM-<bucket>-eval`
  - `--case` repeatable
  - `--variant {baseline,with-dddjango}` repeatable, default both
  - `--model`, default `gpt-5.5`
  - `--reasoning`, default `xhigh`
  - `--timeout-seconds`, default `1800`
  - `--rerun`
  - `--skip-exec`
  - `--workspace-root`, default `/private/tmp/dddjango-eval-workspaces`
- For each case:
  - copy public case to `raw/<case-id>-public-prompt.md`
  - write operator prompt to `raw/<case-id>-operator-prompt.txt`
  - write with-ddjango prompt-input debug to `raw/<case-id>-with-ddjango-prompt-input.json`
  - never write baseline prompt-input debug
  - for each variant write:
    - `raw/<case-id>-<variant>.txt`
    - `raw/<case-id>-<variant>-events.jsonl`
    - `raw/<case-id>-<variant>.stderr.txt`
    - `raw/<case-id>-<variant>-command.txt`
    - `raw/<case-id>-<variant>-exit.txt`
  - for baseline write `raw/<case-id>-baseline-isolation.json`
- Use `codex exec --ephemeral -C <isolated-workspace> -s read-only -o <output> -` for non-code buckets.
- Use `-s workspace-write` and capture changed files only for code bucket cases marked with `captureCode: true` in `workspace/develop/eval/code/cases/plugin/code-capture.json`.
- Baseline command must include `--ignore-user-config --ignore-rules`.
- With-ddjango command must not include those two flags.
- Exclude all `answer/`, all `runs/`, and all private eval paths from isolated workspaces.

Use existing `run_plugin_eval.py` as a source for implementation details, but keep the new script generic instead of renaming or deleting the old script.

- [ ] **Step 4: Run runner tests**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_eval_bucket.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit the generic runner**

```bash
git add workspace/scripts/run_eval_bucket.py workspace/scripts/test_run_eval_bucket.py
git commit -m "Add generic eval bucket runner"
```

---

### Task 3: Answer-Oracle Evaluator

**Files:**
- Create: `workspace/scripts/evaluate_eval_run.py`
- Create: `workspace/scripts/test_evaluate_eval_run.py`

- [ ] **Step 1: Write failing tests for evaluator JSON handling**

Create `workspace/scripts/test_evaluate_eval_run.py` with tests for canonical JSON output and strict schema rejection:

```python
#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("evaluate_eval_run.py")


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluate_eval_run", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvaluateEvalRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluator = load_evaluator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.evaluator.REPO_ROOT = self.root
        self.evaluator.EVAL_ROOT = self.root / "workspace/develop/eval"

    def write_case_and_run(self) -> Path:
        case_id = "case-response-one"
        bucket_root = self.evaluator.EVAL_ROOT / "response"
        public_path = bucket_root / "cases/plugin/public" / f"{case_id}.md"
        answer_path = bucket_root / "answer" / f"{case_id}.yaml"
        raw = bucket_root / "runs/run-one/raw"
        public_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        raw.mkdir(parents=True, exist_ok=True)
        public_path.write_text("사용자 요청입니다.\n", encoding="utf-8")
        answer_path.write_text(
            f"id: {case_id}\ncase_id: {case_id}\nbucket: response\nkind: response\n"
            "target_behavior:\n  required:\n    - answer the request\n"
            "scoring_checks:\n  - pass if answer is grounded\n",
            encoding="utf-8",
        )
        (raw / f"{case_id}-baseline.txt").write_text("baseline answer\n", encoding="utf-8")
        (raw / f"{case_id}-with-ddjango.txt").write_text("with answer\n", encoding="utf-8")
        return raw

    def test_evaluator_writes_canonical_oracle_json(self) -> None:
        self.write_case_and_run()
        payload = {
            "caseId": "case-response-one",
            "answerOracleEvaluated": True,
            "baseline": {"score": "2 / 5", "verdict": "fail", "evaluation": "weak"},
            "with_ddjango": {"score": "5 / 5", "verdict": "pass", "evaluation": "strong"},
            "observations": ["clear improvement"],
            "status": "ok",
        }

        def fake_run(command, *, prompt, cwd, timeout_seconds):
            self.assertIn("--ignore-user-config", command)
            self.assertIn("--ignore-rules", command)
            self.assertIn("EVALUATOR-ONLY ANSWER ORACLE", prompt)
            return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

        with patch.object(self.evaluator, "run_command", side_effect=fake_run):
            result = self.evaluator.main([
                "--bucket", "response",
                "--run-id", "run-one",
                "--case", "case-response-one",
            ])

        self.assertEqual(result, 0)
        output = self.evaluator.EVAL_ROOT / "response/runs/run-one/raw/case-response-one-answer-oracle-evaluation.json"
        value = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(value["with_ddjango"]["verdict"], "pass")

    def test_invalid_schema_exits_without_canonical_oracle(self) -> None:
        self.write_case_and_run()

        def fake_run(command, *, prompt, cwd, timeout_seconds):
            return subprocess.CompletedProcess(command, 0, '{"caseId": "case-response-one"}', "")

        with patch.object(self.evaluator, "run_command", side_effect=fake_run):
            with self.assertRaises(SystemExit):
                self.evaluator.main([
                    "--bucket", "response",
                    "--run-id", "run-one",
                    "--case", "case-response-one",
                ])

        output = self.evaluator.EVAL_ROOT / "response/runs/run-one/raw/case-response-one-answer-oracle-evaluation.json"
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest workspace/scripts/test_evaluate_eval_run.py
```

Expected: fail because `evaluate_eval_run.py` does not exist.

- [ ] **Step 3: Implement `evaluate_eval_run.py`**

Implement these behaviors:

- CLI:
  - `--bucket` required
  - `--run-id` required
  - `--case` repeatable
  - `--model`, default `gpt-5.5`
  - `--reasoning`, default `high`
  - `--timeout-seconds`, default `1800`
  - `--rerun`
- For each selected case:
  - read public case
  - read evaluator-only answer YAML
  - read `raw/<case-id>-baseline.txt`
  - read `raw/<case-id>-with-ddjango.txt`
  - include code artifacts for code bucket if present:
    - `code/<case-id>/baseline/diff.patch`
    - `code/<case-id>/with-ddjango/diff.patch`
    - `code/<case-id>/baseline/changed-files.json`
    - `code/<case-id>/with-ddjango/changed-files.json`
  - cap each artifact excerpt at 80,000 characters and mark truncation explicitly
  - build a private evaluator prompt with this exact output schema:

```json
{
  "caseId": "case-id",
  "answerOracleEvaluated": true,
  "baseline": {
    "score": "0 / 5",
    "verdict": "fail",
    "evaluation": "One concise evaluator-only explanation grounded in the answer oracle."
  },
  "with_ddjango": {
    "score": "0 / 5",
    "verdict": "fail",
    "evaluation": "One concise evaluator-only explanation grounded in the answer oracle."
  },
  "observations": [
    "One run-level note about delta, evidence, leakage, or hard gate status."
  ],
  "status": "ok"
}
```

- Evaluator command:
  - use `codex exec --ephemeral --ignore-user-config --ignore-rules -s read-only`
  - write raw evaluator stdout to `raw/<case-id>-answer-oracle-evaluation.raw.txt`
  - write stderr to `raw/<case-id>-answer-oracle-evaluation.stderr.txt`
  - write command to `raw/<case-id>-answer-oracle-evaluation-command.txt`
  - write exit to `raw/<case-id>-answer-oracle-evaluation-exit.txt`
  - parse JSON from stdout
  - validate with `eval_run_common.validate_oracle_schema`
  - only then write canonical JSON to `raw/<case-id>-answer-oracle-evaluation.json`
- If schema validation fails, raise `SystemExit` and leave only raw evaluator artifacts.

- [ ] **Step 4: Run evaluator tests**

Run:

```bash
python3 -m unittest workspace/scripts/test_evaluate_eval_run.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit the evaluator**

```bash
git add workspace/scripts/evaluate_eval_run.py workspace/scripts/test_evaluate_eval_run.py
git commit -m "Add answer oracle eval runner"
```

---

### Task 4: Generic Run Validator

**Files:**
- Create: `workspace/scripts/validate_eval_run.py`
- Create: `workspace/scripts/test_validate_eval_run.py`

- [ ] **Step 1: Write failing tests for generic run validation**

Create `workspace/scripts/test_validate_eval_run.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_eval_run.py")


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_eval_run", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateEvalRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.validator.REPO_ROOT = self.root
        self.validator.EVAL_ROOT = self.root / "workspace/develop/eval"

    def write_valid_run(self) -> None:
        bucket_root = self.validator.EVAL_ROOT / "response"
        case_id = "case-response-one"
        public = bucket_root / "cases/plugin/public" / f"{case_id}.md"
        answer = bucket_root / "answer" / f"{case_id}.yaml"
        raw = bucket_root / "runs/run-one/raw"
        public.parent.mkdir(parents=True, exist_ok=True)
        answer.parent.mkdir(parents=True, exist_ok=True)
        raw.mkdir(parents=True, exist_ok=True)
        public.write_text("사용자 요청입니다.\n", encoding="utf-8")
        answer.write_text(f"id: {case_id}\ncase_id: {case_id}\nbucket: response\nkind: response\n", encoding="utf-8")
        (raw / f"{case_id}-public-prompt.md").write_text("사용자 요청입니다.\n", encoding="utf-8")
        (raw / f"{case_id}-operator-prompt.txt").write_text("operator prompt\n", encoding="utf-8")
        (raw / f"{case_id}-with-ddjango-prompt-input.json").write_text("{}\n", encoding="utf-8")
        (raw / f"{case_id}-with-ddjango-prompt-input.stderr.txt").write_text("", encoding="utf-8")
        for variant in ("baseline", "with-ddjango"):
            (raw / f"{case_id}-{variant}.txt").write_text(f"{variant} answer\n", encoding="utf-8")
            (raw / f"{case_id}-{variant}-events.jsonl").write_text("", encoding="utf-8")
            (raw / f"{case_id}-{variant}.stderr.txt").write_text("", encoding="utf-8")
            (raw / f"{case_id}-{variant}-command.txt").write_text("codex exec\n", encoding="utf-8")
            (raw / f"{case_id}-{variant}-exit.txt").write_text("0\n", encoding="utf-8")
        (raw / f"{case_id}-baseline-isolation.json").write_text(
            json.dumps({
                "pass": True,
                "forbiddenPathsAbsent": True,
                "commandUsesIgnoreUserConfig": True,
                "commandUsesIgnoreRules": True,
                "runsFromOriginalRepoRoot": False,
                "operatorPromptContainsOriginalRepoRoot": False,
                "operatorPromptDddjangoSkillMetadataMentions": [],
            }),
            encoding="utf-8",
        )
        (raw / f"{case_id}-answer-oracle-evaluation.json").write_text(
            json.dumps({
                "caseId": case_id,
                "answerOracleEvaluated": True,
                "baseline": {"score": "2 / 5", "verdict": "fail", "evaluation": "weak"},
                "with_ddjango": {"score": "5 / 5", "verdict": "pass", "evaluation": "strong"},
                "observations": ["clear improvement"],
            }),
            encoding="utf-8",
        )

    def test_valid_run_passes(self) -> None:
        self.write_valid_run()

        result = self.validator.main(["--bucket", "response", "--run-id", "run-one"])

        self.assertEqual(result, 0)

    def test_stale_baseline_prompt_input_fails(self) -> None:
        self.write_valid_run()
        raw = self.validator.EVAL_ROOT / "response/runs/run-one/raw"
        (raw / "case-response-one-baseline-prompt-input.json").write_text("{}\n", encoding="utf-8")

        with self.assertRaises(SystemExit):
            self.validator.main(["--bucket", "response", "--run-id", "run-one"])

    def test_invalid_oracle_schema_fails(self) -> None:
        self.write_valid_run()
        raw = self.validator.EVAL_ROOT / "response/runs/run-one/raw"
        (raw / "case-response-one-answer-oracle-evaluation.json").write_text('{"caseId": "case-response-one"}', encoding="utf-8")

        with self.assertRaises(SystemExit):
            self.validator.main(["--bucket", "response", "--run-id", "run-one"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest workspace/scripts/test_validate_eval_run.py
```

Expected: fail because `validate_eval_run.py` does not exist.

- [ ] **Step 3: Implement `validate_eval_run.py`**

Implement these checks:

- CLI:
  - `--bucket` required
  - `--run-id` required
  - `--case` repeatable
  - `--variant` repeatable, default both
  - `--skip-oracle`
- For every selected case:
  - public case exists
  - answer YAML exists and contains matching `case_id`, `bucket`, and `kind`
  - `raw/<case-id>-public-prompt.md` exists
  - `raw/<case-id>-operator-prompt.txt` exists
  - no stale `raw/<case-id>-prompt-input.json`
  - no `raw/<case-id>-baseline-prompt-input.json`
  - with-ddjango prompt-input files exist when with-ddjango variant is selected
  - each selected variant has response, events, stderr, command, and exit files
  - selected variant exit file is `0`
  - baseline isolation JSON exists and has `pass: true` when baseline is selected
  - answer-oracle evaluation JSON exists and passes `validate_oracle_schema` unless `--skip-oracle` is used
  - baseline output must not contain obvious dddjango plugin/cache/source markers
- For code bucket cases with `captureCode: true`:
  - `code/<case-id>/<variant>/changed-files.json` exists
  - `code/<case-id>/<variant>/diff.patch` exists

- [ ] **Step 4: Run validator tests**

Run:

```bash
python3 -m unittest workspace/scripts/test_validate_eval_run.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit the validator**

```bash
git add workspace/scripts/validate_eval_run.py workspace/scripts/test_validate_eval_run.py
git commit -m "Add generic eval run validator"
```

---

### Task 5: Initial Eval Orchestrator

**Files:**
- Create: `workspace/scripts/run_initial_eval.py`
- Create: `workspace/scripts/test_run_initial_eval.py`

- [ ] **Step 1: Write failing tests for orchestration order**

Create `workspace/scripts/test_run_initial_eval.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("run_initial_eval.py")


def load_orchestrator():
    spec = importlib.util.spec_from_file_location("run_initial_eval", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RunInitialEvalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = load_orchestrator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.orchestrator.REPO_ROOT = self.root

    def test_bucket_pipeline_runs_runner_evaluator_validator_and_renderer(self) -> None:
        commands: list[list[str]] = []

        def fake_run(command, cwd, text, capture_output):
            commands.append(command)
            return subprocess.CompletedProcess(command, 0, "ok\n", "")

        with patch.object(self.orchestrator.subprocess, "run", side_effect=fake_run):
            result = self.orchestrator.main([
                "--bucket", "response",
                "--run-id", "run-one",
                "--case", "case-response-one",
            ])

        self.assertEqual(result, 0)
        joined = [" ".join(command) for command in commands]
        self.assertIn("workspace/scripts/run_eval_bucket.py", joined[0])
        self.assertIn("workspace/scripts/evaluate_eval_run.py", joined[1])
        self.assertIn("workspace/scripts/validate_eval_run.py", joined[2])
        self.assertIn("workspace/scripts/render_eval_review_html.py", joined[3])

    def test_keep_going_runs_next_bucket_after_failure(self) -> None:
        commands: list[list[str]] = []

        def fake_run(command, cwd, text, capture_output):
            commands.append(command)
            code = 1 if "run_eval_bucket.py" in command and "--bucket" in command and "response" in command else 0
            return subprocess.CompletedProcess(command, code, "", "failed\n" if code else "")

        with patch.object(self.orchestrator.subprocess, "run", side_effect=fake_run):
            with self.assertRaises(SystemExit):
                self.orchestrator.main([
                    "--bucket", "response",
                    "--bucket", "workflow",
                    "--run-id", "run-one",
                    "--keep-going",
                ])

        joined = "\n".join(" ".join(command) for command in commands)
        self.assertIn("--bucket response", joined)
        self.assertIn("--bucket workflow", joined)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_initial_eval.py
```

Expected: fail because `run_initial_eval.py` does not exist.

- [ ] **Step 3: Implement `run_initial_eval.py`**

Implement these behaviors:

- CLI:
  - `--bucket` repeatable, choices include six buckets and `all`; default `all`
  - `--run-id` optional, default `YYYYMMDD-HHMM-initial-eval`
  - `--case` repeatable and passed through to every selected bucket
  - `--model`, default `gpt-5.5`
  - `--reasoning`, default `xhigh`
  - `--evaluator-model`, default same as `--model`
  - `--evaluator-reasoning`, default `high`
  - `--timeout-seconds`, default `1800`
  - `--rerun`
  - `--skip-exec`
  - `--skip-oracle`
  - `--render-only`
  - `--keep-going`
- For each selected bucket:
  - unless `--render-only`, call `run_eval_bucket.py`
  - unless `--skip-oracle` or `--render-only`, call `evaluate_eval_run.py`
  - call `validate_eval_run.py`
  - call `render_eval_review_html.py`
- Print final report paths:
  - `workspace/develop/eval/<bucket>/runs/<run-id>/analysis/report.html`
- Return nonzero if any bucket fails. With `--keep-going`, continue later buckets but still exit nonzero.

- [ ] **Step 4: Run orchestrator tests**

Run:

```bash
python3 -m unittest workspace/scripts/test_run_initial_eval.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit the orchestrator**

```bash
git add workspace/scripts/run_initial_eval.py workspace/scripts/test_run_initial_eval.py
git commit -m "Add initial eval orchestration"
```

---

### Task 6: End-to-End Verification Without Real Model Spend

**Files:**
- No new files.
- Uses all scripts from Tasks 1-5.

- [ ] **Step 1: Run the full unit suite for eval scripts**

Run:

```bash
python3 -m unittest \
  workspace/scripts/test_eval_run_common.py \
  workspace/scripts/test_run_eval_bucket.py \
  workspace/scripts/test_evaluate_eval_run.py \
  workspace/scripts/test_validate_eval_run.py \
  workspace/scripts/test_run_initial_eval.py \
  workspace/scripts/test_render_eval_review_html.py \
  workspace/scripts/test_validate_eval_bucket_pack.py
```

Expected: all tests pass.

- [ ] **Step 2: Validate committed eval bucket packs**

Run:

```bash
python3 workspace/scripts/validate_eval_bucket_pack.py
```

Expected:

```text
eval bucket pack validation passed: response=9, code=8, plugin=7, runtime=7, source=7, workflow=9
```

- [ ] **Step 3: Run a no-model artifact smoke**

Run:

```bash
python3 workspace/scripts/run_initial_eval.py \
  --bucket response \
  --run-id local-skip-exec-smoke \
  --case case-response-order-create \
  --skip-exec \
  --skip-oracle
```

Expected:

- command exits `0`
- report is written to `workspace/develop/eval/response/runs/local-skip-exec-smoke/analysis/report.html`
- validator is called with `--skip-oracle`
- report shows the case as unscored, not pass

- [ ] **Step 4: Confirm generated run artifacts are not staged**

Run:

```bash
git status --short
```

Expected: only script/test changes before their commits, and no `workspace/develop/eval/*/runs/local-skip-exec-smoke/...` files staged because runs directories are ignored.

- [ ] **Step 5: Clean smoke run if it is not needed**

Run:

```bash
rm -rf workspace/develop/eval/response/runs/local-skip-exec-smoke
```

Expected: the smoke run directory is removed and `git status --short` stays clean after committed source changes.

---

### Task 7: First Real Evaluation Run

**Files:**
- No source changes expected.
- Generated artifacts stay under ignored `workspace/develop/eval/<bucket>/runs/<run-id>/`.

- [ ] **Step 1: Run a one-case paid execution check**

Run:

```bash
python3 workspace/scripts/run_initial_eval.py \
  --bucket response \
  --run-id 20260511-initial-pilot \
  --case case-response-order-create \
  --model gpt-5.5 \
  --reasoning xhigh \
  --evaluator-model gpt-5.5 \
  --evaluator-reasoning high
```

Expected:

- baseline and with-ddjango raw outputs exist
- answer-oracle evaluation JSON exists
- validator passes
- HTML report exists
- report top summary shows `total_cases: 9` because the renderer currently lists all bucket cases, with non-run cases shown as unscored

- [ ] **Step 2: Inspect the pilot HTML manually**

Open:

```text
workspace/develop/eval/response/runs/20260511-initial-pilot/analysis/report.html
```

Acceptance criteria:

- top summary is visible without scrolling
- case list shows evaluation question, baseline score, with-ddjango score, and detail button
- selected detail shows problem at top
- baseline and with-ddjango columns show score, response, and evaluation
- cases without oracle JSON are unscored and not treated as pass

- [ ] **Step 3: Run all buckets for the first reportable evaluation**

Run:

```bash
python3 workspace/scripts/run_initial_eval.py \
  --bucket all \
  --run-id 20260511-initial-full \
  --model gpt-5.5 \
  --reasoning xhigh \
  --evaluator-model gpt-5.5 \
  --evaluator-reasoning high \
  --keep-going
```

Expected:

- each bucket gets its own report:
  - `workspace/develop/eval/response/runs/20260511-initial-full/analysis/report.html`
  - `workspace/develop/eval/code/runs/20260511-initial-full/analysis/report.html`
  - `workspace/develop/eval/plugin/runs/20260511-initial-full/analysis/report.html`
  - `workspace/develop/eval/runtime/runs/20260511-initial-full/analysis/report.html`
  - `workspace/develop/eval/source/runs/20260511-initial-full/analysis/report.html`
  - `workspace/develop/eval/workflow/runs/20260511-initial-full/analysis/report.html`
- failed buckets are reported without hiding later bucket results
- source files remain unmodified except ignored run artifacts

- [ ] **Step 4: Summarize first-run findings**

Prepare a short report in the final response with:

- run id
- bucket success/failure list
- report paths
- validation command results
- known limitations, including timeout, evaluator uncertainty, missing case artifacts, or CLI failures

Do not commit generated run artifacts.

---

## Implementation Notes

- Keep `run_plugin_eval.py` in place during this work. It is useful prior art and may still be referenced by existing manual workflows.
- Do not place answer oracle text into public cases, prompt-input artifacts, or fixture files.
- The answer-oracle evaluator is allowed to read `answer/*.yaml`; baseline and with-ddjango subjects are not.
- Generated run artifacts are evaluator-only. They should stay under ignored `runs/` directories.
- Prefer exact schema rejection over permissive rendering. A malformed oracle should make a case unscored or fail validation rather than silently becoming a pass.
- The first full run may be slow and expensive. The implementation must support one-case pilot execution before full-bucket execution.

## Self-Review

- Spec coverage: The plan covers raw model execution, answer-oracle judgment generation, validation, HTML rendering, and first-run reporting.
- Leakage boundary: Public cases and subject prompts never receive answer YAML or scoring text. Only `evaluate_eval_run.py` receives evaluator-only material.
- Existing structure: The plan preserves `cases/plugin/public`, `answer`, and `runs` layout for every bucket.
- No stale artifacts: Smoke and real run artifacts remain under ignored `runs/`; only scripts/tests/docs are committed.
- Known limitation: The renderer currently lists all bucket cases even when a pilot run selects one case, so non-selected cases will appear unscored. This is acceptable for the pilot but should be revisited if pilot reports need a selected-case-only view.
