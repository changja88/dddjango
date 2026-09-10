#!/usr/bin/env python3
"""현장 F4/F7/F8 회귀: 골격·의미 후보·앵커 전체 수집의 반대 대조를 고정한다."""
from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pregate_fixture_run import _git, _load_module
import corpus_mirror_sync as corpus
from ontology_census import parse_sections

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "dddjango/scripts"
FIXTURES = ROOT / "workspace/eval/fixtures"
sys.path.insert(0, str(SCRIPTS))
comp = _load_module(SCRIPTS / "check-composition-root.py", "field_composition")
dto = _load_module(SCRIPTS / "check-usecase-dto-placement.py", "field_dto")
controller = _load_module(SCRIPTS / "check-api-error-controller-contract.py", "field_controller")
CODE = "application/lesson/driving_layer/controller.py"
TREE = "application/orders/driving_layer/api/payment/payment_controller.py"
SELECTORS = ["--error-profile", "dddjango-code-json", "--scope", "lesson",
             "--api-module", "config/api.py", "--controller-module", CODE,
             "--scope-bc", "lesson", "--error-bc", "lesson"]


class CheckerRegression(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="field-checker-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = dict(os.environ, DJR_FINDINGS_JSON=str(self.root / "findings.jsonl"),
                        DJR_VIOLATIONS_DIR=str(self.root / "violations"))

    def write(self, rel: str, source: str = "") -> Path:
        target = self.root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
        return target

    def api_rules(self) -> list[str]:
        findings, candidates = comp.Findings(defer=True), comp.Candidates(defer=True)
        bc = self.root / "application/lesson"
        comp._check_api_dir(self.root, bc, Path("application/lesson"), findings, candidates, frozenset())
        return [e.rule for e in findings.entries]

    def test_empty_api_content_is_not_an_active_registrar(self) -> None:
        self.write("application/lesson/driving_layer/api/api_router.py")
        for source in ("", "# planned\n", '"""planned"""\n'):
            with self.subTest(source=source):
                self.write("application/lesson/driving_layer/api/book/book_controller.py", source)
                self.assertNotIn("#107", self.api_rules())
                self.write("application/lesson/driving_layer/api/api_router.py", source)
                self.assertNotIn("#107", self.api_rules())
        self.write("application/lesson/driving_layer/api/webhook/provider/__init__.py")
        self.write("application/lesson/driving_layer/api/webhook/provider/handler.py", '"""planned"""\n')
        self.assertNotIn("#107", self.api_rules())

    def test_real_controller_webhook_and_explicit_registrar_keep_107(self) -> None:
        self.write("application/lesson/driving_layer/api/api_router.py")
        self.write("config/urls.py")
        for rel, source in (
            ("application/lesson/driving_layer/api/book/book_controller.py", "class BookController: pass\n"),
            ("application/lesson/driving_layer/api/webhook/provider/handler.py", "def handle(): pass\n"),
            ("config/api.py", "from application.lesson.driving_layer.api.api_router import register_lesson_api\n"),
        ):
            with self.subTest(rel=rel):
                target = self.write(rel, source)
                self.assertIn("#107", self.api_rules())
                target.unlink()

    def result_rules(self, source: str) -> tuple[list[str], list[str]]:
        folder = "application/lesson/application_layer/library/record_fortune_failure"
        name = "record_fortune_failure"
        for suffix in ("command", "query", "use_case"):
            self.write(f"{folder}/{name}_{suffix}.py")
        self.write(f"{folder}/{name}_result.py", source)
        findings, candidates = dto.Findings(defer=True), dto.Candidates(defer=True)
        dto._check_use_case(self.root / folder, Path(folder), set(), findings, candidates)
        return ([e.rule for e in findings.entries], [e.rule for e in candidates.entries])

    def test_domain_failure_name_is_a_question_not_a_blocker(self) -> None:
        for name, field in (("RecordFortuneFailureResult", "failure_id: str"),
                            ("OperationFailureResult", "reason: str"),
                            ("RecordExceptionResult", "exception_id: str")):
            with self.subTest(name=name):
                found, candidates = self.result_rules(f"class {name}:\n    {field}\n")
                self.assertEqual(found, [])
                self.assertEqual(candidates, ["#571"])

    def test_multiple_shapes_stay_blocked_and_field_words_stay_neutral(self) -> None:
        found, _ = self.result_rules("class Completed: pass\nclass Rejected: pass\n")
        self.assertEqual(found, ["#571"])
        for field in ("code: str", "error: float", "outcome: str"):
            with self.subTest(field=field):
                self.assertEqual(self.result_rules(f"class RecordedResult:\n    {field}\n"), ([], []))

    def mixed_fixture(self, *, tree: bool = True) -> None:
        shutil.copytree(FIXTURES / "api_error_controller_code/bad_rules", self.root, dirs_exist_ok=True)
        if tree:
            self.write(TREE, (FIXTURES / "api_error_controller/bad_rules" / TREE).read_text())

    def commit(self) -> str:
        _git(self.root, "init", "-q")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "fixture anchor")
        return _git(self.root, "rev-parse", "HEAD").strip()

    def cli(self, extra: list[str], selectors: list[str] = SELECTORS) -> tuple[int, str]:
        result = subprocess.run([sys.executable, str(SCRIPTS / "check-api-error-controller-contract.py"),
                                 str(self.root), *selectors, *extra], env=self.env,
                                text=True, capture_output=True)
        return result.returncode, result.stdout + result.stderr

    def test_anchor_collects_existing_tree_and_code_findings(self) -> None:
        self.mixed_fixture()
        anchor = self.commit()
        self.write("note.txt", "harmless change\n")
        code, output = self.cli(["--anchor", anchor])
        self.assertEqual(code, 0, output)
        self.assertIn("신규분(앵커 이후) 0건 · 앵커 기존분(잔존) 4건", output)
        self.assertIn("bare catch forbidden", output)
        self.assertIn("[#648]", output)

    def test_new_code_stays_new_with_old_tree(self) -> None:
        self.mixed_fixture()
        source = (self.root / CODE).read_text()
        self.write(CODE, source.replace("    except:\n", "    except LessonMissing:\n"))
        anchor = self.commit()
        self.write(CODE, source)
        code, output = self.cli(["--anchor", anchor])
        self.assertEqual(code, 2, output)
        self.assertIn("신규분(앵커 이후) 1건 · 앵커 기존분(잔존) 3건", output)
        self.assertIn("bare catch forbidden", output.split("== 신규분")[1].split("== 앵커 기존분")[0])

    def test_new_tree_stays_new_with_old_code(self) -> None:
        self.mixed_fixture(tree=False)
        anchor = self.commit()
        self.write(TREE, (FIXTURES / "api_error_controller/bad_rules" / TREE).read_text())
        code, output = self.cli(["--anchor", anchor])
        self.assertEqual(code, 2, output)
        self.assertIn("신규분(앵커 이후) 1건 · 앵커 기존분(잔존) 3건", output)

    def test_plain_tree_preemption_and_code_only_baseline_are_preserved(self) -> None:
        self.mixed_fixture()
        code, output = self.cli([])
        self.assertEqual(code, 2, output)
        self.assertNotIn("code-profile", output)
        shutil.rmtree(self.root / "application/orders")
        anchor = self.commit()
        self.write("note.txt", "harmless\n")
        code, output = self.cli(["--anchor", anchor])
        self.assertEqual(code, 0, output)
        self.assertIn("신규분(앵커 이후) 0건 · 앵커 기존분(잔존) 3건", output)

    def test_baseline_local_exits_and_argument_guards(self) -> None:
        self.mixed_fixture()
        code, output = self.cli(["--anchor-baseline"])
        self.assertEqual(code, 2, output)
        self.assertIn("code-profile", output)
        self.assertNotIn("앵커 차분", output)
        code, output = self.cli(["--anchor-baseline"], ["--error-profile", "auto"])
        self.assertEqual(code, 2, output)
        self.assertNotIn("사용 오류", output)
        shutil.rmtree(self.root / "application/orders")
        code, output = self.cli(["--anchor-baseline"], ["--error-profile", "auto"])
        self.assertEqual(code, 0, output)
        anchor = self.commit()
        self.assertEqual(self.cli(["--anchor-baseline"])[0], 1)
        self.assertEqual(self.cli(["--anchor", anchor, "--anchor-baseline"])[0], 1)

    def test_incomplete_baseline_analysis_is_not_successful_collection(self) -> None:
        self.mixed_fixture()
        issue = "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED unresolved discriminator"
        finding = controller.Finding(Path(CODE), 1, "bare catch forbidden", "except:", rule="#62")
        with patch.object(controller, "_run", return_value=([issue], [finding])), \
                patch.object(controller.anchor_diff, "partition_exit") as partition, \
                patch.dict(os.environ, self.env), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()) as stderr:
            code = controller.main(["checker", str(self.root), *SELECTORS, "--anchor-baseline"])
        self.assertEqual(code, 1)
        self.assertIn(issue, stderr.getvalue())
        partition.assert_not_called()


class SourceMirrorRegression(unittest.TestCase):
    """규범 개정 뒤에도 이관 원문 주소와 현재 렌더 주소를 혼동하지 않는다."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="field-mirror-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.paths = corpus.paths_for(self.root, "architecture-ddd")
        old = "## Policy\n\nOriginal approved policy.\n"
        current = "## Policy\n\nAmended approved policy.\n"
        self.original = old
        self.current = current
        for path in self.paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)
        deployed = "# Reference\n\n" + current.replace("## Policy\n", "## Policy\n" + corpus.GRAPH_MARKER + "\n")
        self.paths["dep"].write_text(deployed)
        self.paths["codex"].write_text(deployed)
        self.paths["src"].write_text("# Source provenance\n\n" + old)
        ledger = self.root / "ontology/LEDGER.tsv"
        ledger.parent.mkdir()
        key = next(s["section_key"] for s in parse_sections(deployed.encode()) if s["heading"] == "Policy")
        row = {"doc_key": "architecture-ddd-final", "section_key": key, "owner": "graph",
               "baseline_sha256": hashlib.sha256(current.encode()).hexdigest(),
               "migrated_sha256": hashlib.sha256(old.encode()).hexdigest()}
        with ledger.open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row), delimiter="\t")
            writer.writeheader()
            writer.writerow(row)

    def test_rebaseline_keeps_frozen_source_and_supports_existing_current_mirrors(self) -> None:
        for source in (self.original, self.current):
            with self.subTest(source=source):
                self.paths["src"].write_text("# Source provenance\n\n" + source)
                before = self.paths["src"].read_bytes()
                result = corpus.check_skill(self.root, "architecture-ddd")
                self.assertEqual(result["status"], "in_sync", result)
                corpus.write_skill(self.root, "architecture-ddd", result)
                self.assertEqual(self.paths["src"].read_bytes(), before)

    def test_unapproved_source_changes_and_ambiguous_spans_remain_structure_errors(self) -> None:
        for source in (self.original.replace("Original", "Tampered"), self.original + self.current):
            with self.subTest(source=source):
                self.paths["src"].write_text("# Source provenance\n\n" + source)
                result = corpus.check_skill(self.root, "architecture-ddd")
                self.assertEqual(result["status"], "structure", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
