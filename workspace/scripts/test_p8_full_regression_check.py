#!/usr/bin/env python3
"""Unit tests for the P8 full-regression aggregate validator."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P5_SCRIPT = ROOT / "workspace/scripts/p5_individual_eval.py"
P6_SCRIPT = ROOT / "workspace/scripts/p6_integration_eval.py"
P8_SCRIPT = ROOT / "workspace/scripts/p8_full_regression_check.py"
P5_FIXTURE_ROOT = ROOT / "workspace/develop/eval/fixtures/individual-skills"
P6_FIXTURE_ROOT = ROOT / "workspace/develop/eval/fixtures/integration-flows"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


p5 = load_module("p5_individual_eval", P5_SCRIPT)
p6 = load_module("p6_integration_eval", P6_SCRIPT)
p8 = load_module("p8_full_regression_check", P8_SCRIPT)


@dataclass
class FakeCompletedProcess:
    returncode: int
    stdout: str
    stderr: str


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class P8FullRegressionCheckTests(unittest.TestCase):
    def p5_paths(self, output_dir: Path) -> p5.Paths:
        return p5.Paths(fixture_root=P5_FIXTURE_ROOT, output_dir=output_dir, repo_root=ROOT)

    def p6_paths(self, output_dir: Path) -> p5.Paths:
        return p5.Paths(fixture_root=P6_FIXTURE_ROOT, output_dir=output_dir, repo_root=ROOT)

    def fake_p5_runner(self, command: list[str], *, cwd: Path, final_path: Path) -> FakeCompletedProcess:
        del command, cwd
        case_variant = final_path.parent.name
        variant = "with-plugin" if case_variant.endswith("-with-plugin") else "baseline"
        case_id = case_variant.removesuffix(f"-{variant}")
        case = p5.case_by_id(P5_FIXTURE_ROOT, case_id)
        oracle = case["oracle"]
        final_path.parent.mkdir(parents=True, exist_ok=True)
        final_path.write_text(
            json.dumps(
                {
                    "loaded_skill": oracle["loaded_skill"],
                    "claims": oracle["required_claims"],
                    "overclaims": False,
                    "answer_text": f"model answer for {case_id}",
                }
            ),
            encoding="utf-8",
        )
        return FakeCompletedProcess(returncode=0, stdout='{"event":"done"}\n', stderr="")

    def fake_p6_runner(self, command: list[str], *, cwd: Path, final_path: Path) -> FakeCompletedProcess:
        del command, cwd
        case_variant = final_path.parent.name
        variant = "with-plugin" if case_variant.endswith("-with-plugin") else "baseline"
        case_id = case_variant.removesuffix(f"-{variant}")
        case = p5.case_by_id(P6_FIXTURE_ROOT, case_id)
        oracle = case["oracle"]
        final_path.parent.mkdir(parents=True, exist_ok=True)
        final_path.write_text(
            json.dumps(
                {
                    "loaded_skill": "; ".join(p6.required_loaded_skills(oracle)) or oracle["loaded_skill"],
                    "claims": oracle["required_claims"],
                    "overclaims": False,
                    "answer_text": f"model answer for {case_id}",
                }
            ),
            encoding="utf-8",
        )
        return FakeCompletedProcess(returncode=0, stdout='{"event":"done"}\n', stderr="")

    def make_eval_outputs(self, tmp: Path) -> tuple[Path, Path]:
        p5_output = tmp / "p5-run"
        p6_output = tmp / "p6-run"
        p5.model_run_targeted_suite(
            self.p5_paths(p5_output),
            bucket="individual-skills",
            run_id="unit-p8-p5",
            iterations=2,
            runtime_channel="external",
            work_root=tmp / "work",
            variants=("with-plugin",),
            runner=self.fake_p5_runner,
        )
        p5.model_run_bucket(
            self.p5_paths(p5_output),
            bucket="individual-skills",
            run_id="unit-p8-p5",
            runtime_channel="external",
            work_root=tmp / "work",
            variants=("with-plugin",),
            runner=self.fake_p5_runner,
        )
        p5.render_report(p5_output)
        p5.validate_run(p5_output, ROOT)

        p6.run_targeted_suite(
            self.p6_paths(p6_output),
            bucket="integration-flows",
            run_id="unit-p8-p6",
            iterations=2,
            model_backed=True,
            runtime_channel="external",
            work_root=tmp / "work",
            variants=("with-plugin",),
            runner=self.fake_p6_runner,
        )
        p6.run_bucket(
            self.p6_paths(p6_output),
            "integration-flows",
            "unit-p8-p6",
            model_backed=True,
            runtime_channel="external",
            work_root=tmp / "work",
            variants=("with-plugin",),
            runner=self.fake_p6_runner,
        )
        p6.render_report(p6_output)
        p6.validate_run(p6_output, ROOT)
        return p5_output, p6_output

    def make_p7_inputs(self, tmp: Path) -> tuple[Path, Path, Path, Path]:
        source = tmp / "source-plugin"
        cache = tmp / "cache-plugin"
        write_json(source / ".codex-plugin/plugin.json", {"name": "dddjango"})
        write_json(cache / ".codex-plugin/plugin.json", {"name": "dddjango"})
        (source / "skills/example").mkdir(parents=True)
        (cache / "skills/example").mkdir(parents=True)
        (source / "skills/example/SKILL.md").write_text("# Example\n", encoding="utf-8")
        (cache / "skills/example/SKILL.md").write_text("# Example\n", encoding="utf-8")
        runtime = tmp / "p7-runtime.json"
        manifest = tmp / "p7-manifest.json"
        write_json(
            runtime,
            {
                "status": "pass",
                "case_count": 26,
                "family_count": 13,
                "happy_count": 13,
                "exclusion_count": 13,
                "failure_count": 0,
                "routing_pass_count": 26,
                "cache_path_pass_count": 26,
                "final_answer_pass_count": 26,
            },
        )
        write_json(
            manifest,
            {
                "status": "pass",
                "source_manifest_sha256": p5.sha256_file(source / ".codex-plugin/plugin.json"),
                "cache_manifest_sha256": p5.sha256_file(cache / ".codex-plugin/plugin.json"),
            },
        )
        return source, cache, runtime, manifest

    def make_review(self, tmp: Path) -> tuple[Path, Path]:
        raw = tmp / "review-raw.md"
        summary = tmp / "review-summary.md"
        raw.write_text("Independent P8 review raw output.\n", encoding="utf-8")
        summary.write_text(
            "\n".join(
                [
                    "# Review Summary",
                    f"raw review output path: {raw}",
                    "Blocker 0",
                    "Major 0",
                    "Open Minor 0",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return raw, summary

    def test_full_regression_check_passes_clean_model_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            p5_output, p6_output = self.make_eval_outputs(tmp)
            source, cache, runtime, manifest = self.make_p7_inputs(tmp)
            review_raw, review_summary = self.make_review(tmp)

            args = p8.parse_args(
                [
                    "--repo-root",
                    str(ROOT),
                    "--p5-output-dir",
                    str(p5_output),
                    "--p6-output-dir",
                    str(p6_output),
                    "--source-plugin-root",
                    str(source),
                    "--installed-cache-root",
                    str(cache),
                    "--p7-runtime-analysis",
                    str(runtime),
                    "--p7-manifest-validation",
                    str(manifest),
                    "--review-raw",
                    str(review_raw),
                    "--review-summary",
                    str(review_summary),
                ]
            )
            result = p8.check_full_regression(args)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["p5"]["status_counts"]["not-scored"], 0)
        self.assertEqual(result["p6"]["status_counts"]["not-scored"], 0)
        self.assertEqual(result["review"]["finding_counts"], {"Blocker": 0, "Major": 0, "Open Minor": 0})

    def test_review_open_major_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            raw, summary = self.make_review(tmp)
            summary.write_text(
                f"raw review output path: {raw}\nBlocker 0\nMajor 1\nOpen Minor 0\n",
                encoding="utf-8",
            )

            result = p8.check_review_gate(raw, summary, ROOT)

        self.assertEqual(result["status"], "fail")
        self.assertIn("review-major-open", {failure["kind"] for failure in result["failures"]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
