#!/usr/bin/env python3
"""실제 전사·checker 회귀: OHS update의 명시 새 함수와 입장 표 첫 Python artifact.

update 전사 유실, 기존 바인딩 덮기, 무명시 raise 추론, support로 marker 전파를 잡는다.
"""
from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pregate_fixture_run import _git, _load_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "dddjango/scripts"
pg = _load_module(SCRIPTS / "design_pregate.py", "field_report_pregate")
SERVICE_DIR = "application/garden/driving_layer/open_host_service/catalog"
SERVICE = f"{SERVICE_DIR}/catalog_service.py"
RESPONSE = f"{SERVICE_DIR}/contract/response/list_books_response.py"
EXCEPTION = f"{SERVICE_DIR}/contract/exception/invalid_selection.py"
TEST = "application/garden/test/integration/test_catalog.py"
SUPPORT = "application/garden/test/integration/test_support.py"
ORIGINAL = ('"""Existing service. 원문 보존."""\nfrom __future__ import annotations\n'
            'from decimal import Decimal\n\n'
            'def old_query() -> str:\n    return "unchanged"\n')


def spec_text(paths, symbols=(), imports=(), exceptions=(), owner="") -> str:
    text = ""
    for channel, fence, rows in [("file-plan", "paths", paths), ("symbols", "symbols", symbols),
                                  ("boundary-imports", "imports", imports),
                                  ("exception-map", "exceptions", exceptions)]:
        text += f"<!-- machine: {channel} -->\n```{fence}\n" + "\n".join(rows) + "\n```\n"
    if owner:
        text += ("| candidate | protected contract/evidence | unique production failure | "
                 "existing authoritative coverage | decision | owner/path |\n"
                 "|---|---|---|---|---|---|\n"
                 f"| selection | persisted books | omitted insert | none | add | {owner} |\n")
    return text


class FieldReportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="pregate-field-report-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.write(self.source, SERVICE, ORIGINAL)
        _git(self.source, "init", "-q")
        _git(self.source, "add", "-A")
        _git(self.source, "commit", "-qm", "fixture")
        self.copy = self.root / "copy"
        self.env = dict(os.environ, DJR_FINDINGS_JSON=str(self.root / "findings.jsonl"),
                        DJR_VIOLATIONS_DIR=str(self.root / "violations"), PYTHONDONTWRITEBYTECODE="1")

    def write(self, root: Path, path: str, content: str) -> None:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def materialize(self, text: str):
        if self.copy.exists():
            shutil.rmtree(self.copy)
        shutil.copytree(self.source, self.copy)
        before = {p.relative_to(self.source): p.read_bytes() for p in self.source.rglob("*.py")}
        plan, errors = pg.parse_spec(text)
        self.assertEqual(errors, [])
        self.assertIsNotNone(plan)
        report = pg.materialize(self.copy, plan)
        self.assertEqual({p.relative_to(self.source): p.read_bytes() for p in self.source.rglob("*.py")}, before)
        return plan, report

    def checker(self, name: str) -> str:
        result = subprocess.run([sys.executable, str(SCRIPTS / name), str(self.copy)],
                                env=self.env, capture_output=True, text=True)
        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
        return result.stdout

    def service_spec(self, operation="list_books_query() -> ListBooksResponse", imports=(), raises=(),
                     extra_symbols=(), extra_paths=()) -> str:
        return spec_text([f"update {SERVICE}", f"add {RESPONSE}", *extra_paths],
                         [f"{SERVICE}::{operation}", f"{RESPONSE}::ListBooksResponse {{count: int}}", *extra_symbols],
                         [f"{SERVICE}  {s}" for s in imports], raises)

    def test_new_operation_clears_pair_finding_and_preserves_source_body(self) -> None:
        self.materialize(self.service_spec("another_query() -> str"))
        self.assertIn("[#483]", self.checker("check-context-isolation.py"))
        _, report = self.materialize(self.service_spec(imports=["from decimal import Decimal",
                                                               "from __future__ import annotations"]))
        source = (self.copy / SERVICE).read_text()
        self.assertTrue(source.startswith(ORIGINAL))
        self.assertNotIn("[#483]", self.checker("check-context-isolation.py"))
        self.assertIn(SERVICE, report["materialized"])
        self.assertTrue(any(SERVICE in s and "S5" in s for s in report["unsimulated"]))
        compile(source, SERVICE, "exec")

    def test_wrong_operation_name_and_signature_remain_real_findings(self) -> None:
        for operation, rule in [("another_query() -> str", "#483"),
                                ("list_books_query(value: int) -> ListBooksResponse", "#633"),
                                ("list_books() -> ListBooksResponse", "#482")]:
            with self.subTest(operation=operation):
                self.materialize(self.service_spec(operation))
                self.assertIn(f"[{rule}]", self.checker("check-context-isolation.py"))

    def test_explicit_service_raise_only_clears_exception_finding(self) -> None:
        for mapped, contract_raise, want in [(False, False, True), (True, False, False), (True, True, True)]:
            with self.subTest(mapped=mapped, contract_raise=contract_raise):
                raises = [f"InvalidSelection  {SERVICE}"] if mapped else []
                if contract_raise:
                    raises.append(f"InvalidSelection  {RESPONSE}")
                self.materialize(self.service_spec(raises=raises, extra_paths=[f"add {EXCEPTION}"],
                                                   extra_symbols=[f"{EXCEPTION}::InvalidSelection(Exception)"]))
                output = self.checker("check-public-surface-annotation.py")
                self.assertEqual("[#456]" in output, want, output)

    def test_existing_names_and_unmodeled_updates_are_never_replaced(self) -> None:
        variants = ["old_query(value: int) -> int", "Decimal", "Hidden", "alias renamed = Decimal"]
        for row in variants:
            with self.subTest(row=row):
                _, report = self.materialize(spec_text([f"update {SERVICE}"], [f"{SERVICE}::{row}"],
                                                       exceptions=[f"InvalidSelection  {SERVICE}"]))
                self.assertEqual((self.copy / SERVICE).read_bytes(), ORIGINAL.encode())
                self.assertEqual(report["materialized"], [])
                self.assertTrue(report["unsimulated"])
        _, report = self.materialize(spec_text([f"update {SERVICE}"], imports=[f"{SERVICE}  import fractions"],
                                               exceptions=[f"InvalidSelection  {SERVICE}"]))
        self.assertEqual((self.copy / SERVICE).read_bytes(), ORIGINAL.encode())
        self.assertEqual(report["materialized"], [])

    def test_safe_imports_transcribe_but_conflicts_reject_the_whole_entry(self) -> None:
        for statement, safe in [("from fractions import Fraction as Amount", True),
                                 ("from decimal import Decimal", True),
                                 ("from impostor import Decimal", False),
                                 ("import fractions as old_query", False),
                                 ("import fractions as list_books_query", False),
                                 ("from fractions import *", False),
                                 ("from __future__ import barry_as_FLUFL", False),
                                 ("import fractions; old_query = 1", False),
                                 ("from fractions import Fraction as Amount; from decimal import Decimal as Amount", False)]:
            with self.subTest(statement=statement):
                _, report = self.materialize(self.service_spec(imports=[statement]))
                source = (self.copy / SERVICE).read_text()
                self.assertEqual(SERVICE in report["materialized"], safe)
                if safe:
                    self.assertIn("def list_books_query(", source)
                    self.assertTrue(source.startswith(ORIGINAL))
                    if "Amount" in statement:
                        self.assertIn(statement, source)
                else:
                    self.assertEqual(source, ORIGINAL)
                    self.assertTrue(any(SERVICE in s and "import" in s for s in report["unsimulated"]))
                compile(source, SERVICE, "exec")

    def test_module_bindings_and_raise_helper_collisions_are_preserved(self) -> None:
        for binding in ["class list_books_query: pass\n", "list_books_query = old_query\n",
                        "for list_books_query in []: pass\n", "with context() as list_books_query: pass\n",
                        "try:\n    pass\nexcept Exception as list_books_query:\n    pass\n",
                        "match value:\n    case {'x': list_books_query}: pass\n",
                        "from foreign import *\n"]:
            with self.subTest(binding=binding):
                original = ORIGINAL + binding
                self.write(self.source, SERVICE, original)
                _, report = self.materialize(self.service_spec())
                self.assertEqual((self.copy / SERVICE).read_text(), original)
                self.assertNotIn(SERVICE, report["materialized"])
        self.write(self.source, SERVICE, ORIGINAL + "def _pregate_raise_invalidselection():\n    return 1\n")
        _, report = self.materialize(self.service_spec(raises=[f"InvalidSelection  {SERVICE}"]))
        self.assertNotIn(SERVICE, report["materialized"])
        self.assertEqual((self.copy / SERVICE).read_bytes(), (self.source / SERVICE).read_bytes())

    def test_compile_failure_is_reported_without_partial_update(self) -> None:
        _, report = self.materialize(self.service_spec("list_books_query(x: int, x: int) -> str"))
        self.assertEqual((self.copy / SERVICE).read_text(), ORIGINAL)
        self.assertNotIn(SERVICE, report["materialized"])
        self.assertTrue(any("compile" in s for s in report["unsimulated"]))

    def test_class_global_surface_rejects_the_entire_service_update(self) -> None:
        for class_body in ["    global list_books_query\n    list_books_query = 42\n",
                           "    if True:\n        global list_books_query\n        list_books_query = 42\n"]:
            with self.subTest(class_body=class_body):
                original = ORIGINAL + "class Old:\n" + class_body
                self.write(self.source, SERVICE, original)
                _, report = self.materialize(self.service_spec(imports=["import fractions"],
                    raises=[f"InvalidSelection  {SERVICE}"]))
                self.assertNotIn(SERVICE, report["materialized"])
                self.assertEqual((self.copy / SERVICE).read_bytes(), original.encode())
                self.assertTrue(any(SERVICE in s and "class global" in s for s in report["unsimulated"]))

    def test_class_local_names_do_not_block_new_module_functions(self) -> None:
        original = ORIGINAL + "class Old:\n    list_books_query = 42\n"
        self.write(self.source, SERVICE, original)
        _, report = self.materialize(self.service_spec())
        self.assertIn(SERVICE, report["materialized"])
        self.assertTrue((self.copy / SERVICE).read_bytes().startswith(original.encode()))
        self.assertNotIn("[#483]", self.checker("check-context-isolation.py"))

    def test_signature_named_expressions_reject_the_entire_service_update(self) -> None:
        original = ORIGINAL + "LIMIT: int = 1\n"
        self.write(self.source, SERVICE, original)
        for operation in [
            "list_books_query(request: BooksRequest = (Decimal := 0)) -> BooksResponse",
            "list_books_query(request: BooksRequest = (LIMIT := 2)) -> BooksResponse",
            "list_books_query(*, request: BooksRequest = (LIMIT := 2)) -> BooksResponse",
            "list_books_query(request: (LIMIT := 2)) -> BooksResponse",
            "list_books_query -> (LIMIT := 2)",
        ]:
            with self.subTest(operation=operation):
                _, report = self.materialize(self.service_spec(operation, imports=["import fractions"],
                    raises=[f"InvalidSelection  {SERVICE}"]))
                self.assertNotIn(SERVICE, report["materialized"])
                self.assertEqual((self.copy / SERVICE).read_bytes(), original.encode())
                self.assertTrue(any(SERVICE in s and "NamedExpr" in s for s in report["unsimulated"]))

    def test_plain_signature_defaults_remain_transcribable(self) -> None:
        for default in ["None", "0", "'book'"]:
            with self.subTest(default=default):
                _, report = self.materialize(self.service_spec(
                    f"list_books_query(request: BooksRequest = {default}) -> BooksResponse"))
                self.assertIn(SERVICE, report["materialized"])
                source = (self.copy / SERVICE).read_text()
                self.assertTrue(source.startswith(ORIGINAL))
                namespace = {}
                exec(compile(source, SERVICE, "exec"), namespace)
                self.assertEqual(namespace["list_books_query"].__defaults__, (ast.literal_eval(default),))
                self.assertEqual(namespace["Decimal"]("1.25").as_tuple().exponent, -2)

    def test_only_exact_real_ohs_service_paths_are_updated(self) -> None:
        promoted = f"{SERVICE_DIR}/catalog_service/catalog_service.py"
        (self.source / SERVICE).unlink()
        _, report = self.materialize(spec_text([f"update {SERVICE}"], [f"{SERVICE}::list_books_query() -> str"]))
        self.assertNotIn(SERVICE, report["materialized"])
        self.assertFalse((self.copy / SERVICE).exists())
        self.assertTrue(report["unsimulated"])
        self.write(self.source, promoted, ORIGINAL)
        cases = [(SERVICE, False), (promoted, False), (f"{SERVICE_DIR}/helper.py", False),
                 ("framework/catalog_service.py", False), (f"{SERVICE_DIR}/missing_service.py", False)]
        for path, expected in cases:
            with self.subTest(path=path):
                if path not in (SERVICE, f"{SERVICE_DIR}/missing_service.py"):
                    self.write(self.source, path, ORIGINAL)
                _, report = self.materialize(spec_text([f"update {path}"], [f"{path}::list_books_query() -> str"]))
                self.assertEqual(path in report["materialized"], expected)
                self.assertTrue(report["unsimulated"])
                if not expected and (self.source / path).is_file():
                    self.assertEqual((self.copy / path).read_bytes(), (self.source / path).read_bytes())

    def test_existing_class_decorator_and_alias_remain_s5_alongside_new_function(self) -> None:
        original = ORIGINAL + "class Hidden: pass\n"
        self.write(self.source, SERVICE, original)
        text = spec_text([f"update {SERVICE}"], [f"{SERVICE}::alias Other = Decimal",
                         f"{SERVICE}::Hidden", f"{SERVICE}::Hidden @decorator",
                         f"{SERVICE}::Hidden.method(self, value: int) -> int", f"{SERVICE}::new_query() -> str"])
        _, report = self.materialize(text)
        source = (self.copy / SERVICE).read_text()
        self.assertTrue(source.startswith(original))
        module = ast.parse(source)
        cls = next(n for n in module.body if isinstance(n, ast.ClassDef))
        self.assertEqual(cls.decorator_list, [])
        self.assertEqual(len(cls.body), 1)
        self.assertNotIn("Other", [n.id for n in ast.walk(module) if isinstance(n, ast.Name)])
        self.assertIn(SERVICE, report["materialized"])
        self.assertTrue(any("S5" in s for s in report["unsimulated"]))

    def test_signals_use_first_python_artifact_and_strip_nodeid(self) -> None:
        for owner in [f"{TEST} [markers: django_db]", f"`{TEST}` [markers: django_db]",
                      f"{TEST}::test_case [markers: django_db]", f"`{TEST}::test_case` [markers: django_db]",
                      f"`add` `{TEST}` [markers: django_db]", f"[markers: django_db] `add` {TEST}::case",
                      f"`{TEST}` + support `{SUPPORT}` [markers: django_db]",
                      f"[markers: django_db] {TEST} coverage {SUPPORT}::case"]:
            with self.subTest(owner=owner):
                self.materialize(spec_text([f"add {TEST}", f"add {SUPPORT}"],
                    [f"{TEST}::test_case() -> None", f"{SUPPORT}::test_support() -> None"], owner=owner))
                output = self.checker("check-test-config.py")
                findings = [line for line in output.splitlines() if "[#389]" in line]
                self.assertFalse(any(TEST in line for line in findings), output)
                self.assertTrue(any(SUPPORT in line for line in findings), output)

    def test_unlisted_first_artifact_nonadd_and_missing_markers_do_not_signal(self) -> None:
        self.write(self.source, TEST, "def test_case() -> None: pass\n")
        for owner, tag in [(f"unlisted/test_first.py `{SUPPORT}` [markers: django_db]", "add"),
                           (f"`{SUPPORT}`", "add"),
                           (f"`{TEST}` [markers: django_db] `{SUPPORT}`", "update")]:
            with self.subTest(owner=owner):
                paths = [f"add {SUPPORT}"] + ([f"{tag} {TEST}"] if tag == "update" else [])
                self.materialize(spec_text(paths, [f"{SUPPORT}::test_support() -> None"], owner=owner))
                output = self.checker("check-test-config.py")
                self.assertTrue(any("[#389]" in line and SUPPORT in line for line in output.splitlines()), output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
