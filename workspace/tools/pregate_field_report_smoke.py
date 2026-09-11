#!/usr/bin/env python3
"""실제 전사·checker 회귀: OHS update의 명시 새 함수와 입장 표 첫 Python artifact.

update 전사 유실, 기존 바인딩 덮기, 무명시 raise 추론, support로 marker 전파를 잡는다.
"""
from __future__ import annotations

import ast
import os
import json
from unittest.mock import patch
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pregate_fixture_run import _git, _load_module, _make_repo

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

    def effects(self, text, *rows):
        return text + '<!-- machine: use-case-effects -->\n```effects\n' + '\n'.join(rows) + '\n```\n'

    def test_effect_declaration_contract_and_hash(self):
        path = 'application/garden/application_layer/books/list_books/list_books_use_case.py'
        uow = 'application.garden.application_layer.port.unit_of_work.book_unit_of_work'
        for effect, declared, injected, expected in [
            ('read-only', 'none', False, []), ('read-only', 'BookUnitOfWork', False, [('#197', True)]),
            ('read-only', 'none', True, [('#197', True)]), ('write', 'BookUnitOfWork', True, []),
            ('write', 'none', True, [])]:
            with self.subTest(effect=effect, declared=declared, injected=injected):
                text = spec_text([f'update {path}'], [f'{path}::ListBooksUseCase'] +
                    ([f'{path}::ListBooksUseCase.__init__(self, uow: BookUnitOfWork)'] if injected else []),
                    [f'{path}  from {uow} import BookUnitOfWork'])
                text = self.effects(text, f'{path}::ListBooksUseCase  {effect}  uow={declared}')
                plan, errors = pg.parse_spec(text)
                self.assertEqual(errors, [])
                self.assertEqual([(x.rule, x.confirmed) for x in pg.check_declarations(plan, self.source)], expected)
                if effect == 'write' and declared == 'none':
                    self.assertTrue(any('채널' in n or '불일치' in n for n in plan.notes))
        base = spec_text([f'update {path}'], [f'{path}::ListBooksUseCase'])
        # Legacy literal hash protects cache compatibility without effects.
        import hashlib
        parts = []
        for name in ['file-plan', 'symbols', 'boundary-imports', 'exception-map']:
            parts += [f'<!-- machine: {name} -->', *pg._machine_blocks(base, [])[name]]
        parts += ['<!-- physical-signals -->']
        self.assertEqual(pg.block_hash(base), hashlib.sha256('\n'.join(parts).encode()).hexdigest()[:12])
        first = self.effects(base, f'{path}::ListBooksUseCase  read-only  uow=none')
        self.assertNotEqual(pg.block_hash(first), pg.block_hash(base))
        self.assertEqual(pg.block_hash(first), pg.block_hash(first + '\nprose'))
        self.assertNotEqual(pg.block_hash(first), pg.block_hash(first.replace('uow=none', 'uow=X')))
        for row in [f'{path}::ListBooksUseCase  other  uow=none', f'{path}::ListBooksUseCase  write  uow=',
                    f'{path}::Missing  write  uow=none', f'unlisted.py::ListBooksUseCase  write  uow=none',
                    f'{path}::ListBooksUseCase  write  uow=[',
                    f'{path}::ListBooksUseCase  write  uow=none\n{path}::ListBooksUseCase  write  uow=none']:
            self.assertTrue(pg.parse_spec(self.effects(base, row))[1], row)

    def test_update_marker_final_state_and_preservation(self):
        originals = ['from __future__ import annotations\nimport pytest\npytestmark = pytest.mark.django_db\n\ndef test_case(): return 42\n',
                     'from __future__ import annotations\n\ndef test_case(): return 42\n']
        for original in originals:
            for markers in ['', 'django_db', 'slow']:
                with self.subTest(original=original, markers=markers):
                    self.write(self.source, TEST, original)
                    _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers: {markers}]'))
                    updated = (self.copy / TEST).read_text()
                    self.assertIn('def test_case(): return 42', updated)
                    self.assertIn('pytestmark = [' + ', '.join('pytest.mark.' + m for m in markers.split(',') if m) + ']', updated)
                    self.assertIn(TEST, report['materialized'])
                    compile(updated, TEST, 'exec')
        for tail in ['pytestmark = pytest.mark.django_db(transaction=True)\n',
                     'pytestmark = calculate()\n', 'pytestmark = []\npytestmark = []\n',
                     'if True:\n    pytestmark = []\n', 'pytestmark = []\npytestmark += []\n',
                     'pytest = object()\npytestmark = []\n']:
            original = 'import pytest\n' + tail + 'def test_case(): pass\n'
            self.write(self.source, TEST, original)
            _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers: django_db]'))
            self.assertEqual((self.copy / TEST).read_text(), original)
            self.assertNotIn(TEST, report['materialized'])
            self.assertTrue(report['unsimulated'])
        self.write(self.source, TEST, 'import pytest as pt\npytestmark: list = (pt.mark.slow,)\n@pt.mark.django_db\nclass TestBook: pass\n')
        self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers:]'))
        self.assertIn('@pt.mark.django_db', (self.copy / TEST).read_text())
        self.assertIn('pytestmark = []', (self.copy / TEST).read_text())
        for owner in [f'{TEST}::case [markers: django_db]', f'{TEST}::TestBook [markers: django_db]',
                      f'{TEST} [markers: django_db(transaction=True)]', f'{TEST} [base: TestCase] [client: yes]', TEST]:
            self.materialize(spec_text([f'update {TEST}'], owner=owner))
            self.assertEqual((self.copy / TEST).read_bytes(), (self.source / TEST).read_bytes())
        conflict = spec_text([f'update {TEST}'], owner=f'{TEST} [markers: slow]')
        conflict += f'| second | persisted | omitted | none | update | {TEST} [markers: django_db] |\n'
        self.assertTrue(pg.parse_spec(conflict)[1])

    def test_dto_type_provenance_nested_alias_forward_and_candidates(self):
        result = 'application/garden/application_layer/books/list_books/list_books_result.py'
        entity = 'application/garden/domain/books/aggregate/book.py'
        # Actual canonical tree uses domain/aggregate families; field provenance must be explicit.
        entity = 'application/garden/domain_layer/books/aggregate/book.py'
        module = entity[:-3].replace('/', '.')
        self.write(self.source, entity, 'class Book: pass\n')
        self.write(self.source, result, 'class ListBooksResult:\n    old: int\n\nclass Kept:\n    book: int\n')
        for annotation in ['Book', 'list[Book]', 'dict[str, tuple[Book, ...]]', 'Optional[Book]',
                           "'list[Book]'", '_Item', 'Rows', 'Book | None']:
            with self.subTest(annotation=annotation):
                text = spec_text([f'update {result}'], [f'{result}::alias Rows = list[Book]',
                    f'{result}::_Item {{book: Book}}', f'{result}::ListBooksResult {{items: {annotation}}}'],
                    [f'{result}  from {module} import Book', f'{result}  from typing import Optional'])
                plan, errors = pg.parse_spec(text)
                self.assertEqual(errors, [])
                findings = pg.check_declarations(plan, self.source)
                self.assertEqual([(x.rule, x.confirmed) for x in findings], [('#202', True)])
                self.assertEqual((self.source / result).read_text(), 'class ListBooksResult:\n    old: int\n\nclass Kept:\n    book: int\n')
        for declaration, imports, expected in [
            ('Book', [], [('#202', False)]), ('int', [], []), ('Literal["Book"]', ['from typing import Literal'], []),
            ('money.Book', ['import external.money as money'], []),
            ('Book', ['from application.garden.domain_layer.books.value_object.book import Book'], [])]:
            plan, errors = pg.parse_spec(spec_text([f'update {result}'], [f'{result}::ListBooksResult {{item: {declaration}}}'],
                                                  [f'{result}  {i}' for i in imports]))
            self.assertEqual(errors, [])
            self.assertEqual([(x.rule, x.confirmed) for x in pg.check_declarations(plan, self.source)], expected)
        for aliases in [[f'{result}::alias A = B', f'{result}::alias B = A'],
                        [f'{result}::alias[TYPE_CHECKING] A = Book', f'{result}::alias[else] A = int']]:
            plan, errors = pg.parse_spec(spec_text([f'update {result}'], [*aliases, f'{result}::ListBooksResult {{item: A}}'],
                [f'{result}  from {module} import Book']))
            self.assertEqual(errors, [])
            self.assertEqual([(x.rule, x.confirmed) for x in pg.check_declarations(plan, self.source)], [('#202', False)])

    def cli(self, text):
        spec = self.root / 'design.md'
        spec.write_text(text)
        report = self.root / 'report.md'
        if report.exists(): report.unlink()
        run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'design_pregate.py'), str(spec),
                              str(self.source), '--report', str(report)], capture_output=True, text=True, env=self.env)
        return run, report.read_text() if report.exists() else ''

    def test_generated_admin_cli_defers_open_slots_but_keeps_bare_any(self):
        path = 'framework/admin/book.py'
        text = spec_text([f'add {path}'], [f'{path}::BookAdmin(admin.ModelAdmin)',
            f'{path}::BookAdmin._context(context: dict[str, Any], payload: dict[str, object], opaque: Any) -> dict[str, object]',
            f'{path}::OtherAdmin(admin.ModelAdmin)',
            f'{path}::OtherAdmin._context(context: dict[str, Any]) -> dict[str, object]'],
            [f'{path}  from django.contrib import admin', f'{path}  from typing import Any'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        section = report.split('### 생성 본문 S1 미검증', 1)[1].split('###', 1)[0]
        self.assertIn('S1:', section)
        self.assertIn('매개변수 `context`', section)
        self.assertIn('매개변수 `payload`', section)  # original #647 candidate must remain visible
        self.assertIn('반환 타입', section)
        self.assertNotIn('매개변수 `opaque`', section)
        self.assertIn('매개변수 `opaque`', report)
        checked = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'design_pregate.py'),
            str(self.root / 'design.md'), str(self.source), '--check-report', str(self.root / 'report.md')],
            capture_output=True, text=True, env=self.env)
        self.assertEqual(checked.returncode, 3, checked.stdout + checked.stderr)
        self.assertIn('S1 미검증', checked.stdout)

    def test_generated_admin_exact_multiline_slots_and_mixed_cohorts(self):
        path = 'framework/admin/book.py'
        self.write(self.source, path, """from typing import Any
from parler.admin import TranslatableAdmin
class First(TranslatableAdmin):
    def _context(
        self,
        renamed: dict[str, Any],
        payload: dict[str, object],
        opaque: Any,
        nested: list[Any],
    ) -> dict[str, object]:
        raise NotImplementedError
class Second(TranslatableAdmin):
    def _context(self, renamed: dict[str, Any]) -> dict[str, object]:
        raise NotImplementedError
""")
        records_path = self.root / 'findings.jsonl'
        run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'check-public-surface-annotation.py'), str(self.source)],
            capture_output=True, text=True, env=self.env)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        rows = [json.loads(line) for line in records_path.read_text().splitlines()]
        rows = [r for r in rows if r['file'].startswith(path + ':')]
        lines = lambda records: list(dict.fromkeys(f"{r['checker']} :: {pg.registry._normalize(pg.findings.line_of_record(r), ())}" for r in records))
        violations = [r for r in rows if r['severity'] == 'violation']
        candidates = [r for r in rows if r['severity'] == 'info']
        gate = dict(raw_exit=2, raw_stdout=run.stdout, attributed_lines=lines(violations), records=violations,
                    unmatched_lines=[], candidate_lines=lines(candidates), candidate_records=candidates)
        generated = {path: [dict(owner='First', method='_context', lineno=4, end_lineno=11),
                            dict(owner='Second', method='_context', lineno=13, end_lineno=14)]}
        retained, deferred = pg.partition_generated_findings(gate, generated, self.source)
        self.assertEqual(len(retained), 1, retained)
        self.assertIn('`opaque`', retained[0])
        self.assertEqual(len(deferred), 3, deferred)
        self.assertTrue(any('`renamed`' in line for line in deferred))
        self.assertTrue(any('`payload`' in line for line in deferred))
        self.assertFalse(any('`nested`' in line for line in deferred))
        # Same normalized key spans both classes. One non-generated location retains all of it.
        retained, deferred = pg.partition_generated_findings(gate, {path: generated[path][:1]}, self.source)
        self.assertEqual(len(retained), 3, retained)
        self.assertEqual(len(deferred), 1, deferred)
        # A signature diagnostic at the argument line is not def-line evidence.
        shifted = dict(gate, records=[dict(r, file=f'{path}:6') if '매개변수 `renamed`' in r['message'] else r for r in violations])
        retained, deferred = pg.partition_generated_findings(shifted, generated, self.source)
        self.assertTrue(any('`renamed`' in line for line in retained), retained)
        # Neither free prose nor file_raw nor a normalized :N can recover a slot.
        for changes in [dict(message='context must be typed'), dict(file=f'{path}:N', file_raw=f'/tmp/{path}:4'),
                        dict(checker='other-checker.py')]:
            altered = [dict(violations[0], **changes), *violations[1:]]
            bad = dict(gate, records=altered, attributed_lines=lines(altered))
            retained, deferred = pg.partition_generated_findings(bad, generated, self.source)
            self.assertIn(lines(altered)[0], retained)
        self.assertEqual(pg.partition_generated_findings(gate, {}, self.source), (gate['attributed_lines'], []))

    def test_admin_source_business_body_is_legacy_not_generated_s1(self):
        path = 'framework/admin/book.py'
        original = """from typing import Any
from parler.admin import TranslatableAdmin
class BookAdmin(TranslatableAdmin):
    def changeform_view(self, request: object, extra_context: dict[str, Any]) -> HttpResponse:
        return self._context(extra_context)
    def _context(self, payload: dict[str, Any]) -> dict[str, Any]:
        charge(payload['amount'])
        return payload
"""
        self.write(self.source, path, original)
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'actual admin baseline')
        text = spec_text([f'update {path}'], [f'{path}::BookAdmin(TranslatableAdmin)',
                            f'{path}::BookAdmin._context(payload: dict[str, Any]) -> dict[str, Any]'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        self.assertIn('실체화 0건', run.stdout)
        self.assertNotIn('S1:', report)
        self.assertEqual((self.source / path).read_text(), original)
        records = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'check-public-surface-annotation.py'), str(self.source)],
            capture_output=True, text=True, env=self.env)
        self.assertEqual(records.returncode, 2, records.stdout + records.stderr)
        self.assertIn('[#647]', records.stdout)

    def uow_fixture(self):
        shutil.rmtree(self.source)
        self.source = _make_repo(self.root, 'uow-source')
        pg.materialize_skeleton(self.source, 'orders')
        port = 'application/orders/application_layer/port/unit_of_work/order_unit_of_work.py'
        impl = 'application/orders/driven_layer/adapter/persistence/unit_of_work/order_unit_of_work.py'
        self.write(self.source, port, 'from abc import ABC, abstractmethod\nclass OrdersUnitOfWork(ABC):\n'
                   '    @abstractmethod\n    def __enter__(self): ...\n'
                   '    @abstractmethod\n    def __exit__(self, *args): ...\n'
                   '    @abstractmethod\n    def after_commit(self, callback): ...\n')
        self.write(self.source, impl, 'class DjangoOrdersUnitOfWork:\n'
                   '    def after_commit(self, callback):\n'
                   '        transaction.on_commit(callback, robust=True)\n')
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'uow baseline')
        return port, impl

    def test_generated_uow_cli_defers_only_generated_body_and_preserves_original(self):
        port, impl = self.uow_fixture()
        # Baseline port exists, while a newly planned implementation is generated.
        _git(self.source, 'rm', impl)
        _git(self.source, 'commit', '-qm', 'implementation pending')
        text = spec_text([f'add {impl}'], [f'{impl}::DjangoOrdersUnitOfWork',
            f'{impl}::DjangoOrdersUnitOfWork.after_commit(callback: object) -> None'])
        before = {p.relative_to(self.source): p.read_bytes() for p in self.source.rglob('*.py')}
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn('생성 본문 S1 미검증 (1건)', report)
        self.assertIn('원 registry 결과: exit 2 · 귀속 1건 · 유지 0건 · S1 미검증 1건', report)
        self.assertIn('[#376]', report)
        self.assertEqual({p.relative_to(self.source): p.read_bytes() for p in self.source.rglob('*.py')}, before)
        checked = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'design_pregate.py'),
            str(self.root / 'design.md'), str(self.source), '--check-report', str(self.root / 'report.md')],
            capture_output=True, text=True, env=self.env)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertIn('S1 미검증 1건', checked.stdout)
        # Declaration-confirmed errors still block when the only registry finding is deferred.
        response = 'application/orders/application_layer/orders/read_orders/read_orders_result.py'
        self.write(self.source, response, 'class ReadOrdersResult: pass\n')
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'declaration fixture')
        combined = self.effects(text.replace('```paths\n', f'```paths\nupdate {response}\n')
                                .replace('```symbols\n', f'```symbols\n{response}::ReadOrdersResult\n'),
                                f'{response}::ReadOrdersResult  read-only  uow=OrdersUnitOfWork')
        run, report = self.cli(combined)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn('생성 본문 S1 미검증 (1건)', report)
        self.assertIn('선언 확정 (1건)', report)
        self.assertEqual(pg.check_report(combined, report)[0], 3)

    def test_real_uow_cli_retains_bad_body_and_missing_robust_even_stub_text(self):
        port, impl = self.uow_fixture()
        added = 'application/orders/domain_layer/shared_value_object/lane_marker.py'
        text = spec_text([f'update {impl}', f'add {added}'], [f'{added}::LaneMarker {{value: str}}'])
        for body, rule in [('raise NotImplementedError', '#376'),
                           ('transaction.on_commit(callback)', '#566')]:
            original = ('"""pre-gate 팬텀 스텁."""\nclass DjangoOrdersUnitOfWork:\n'
                        '    def after_commit(self, callback):\n        ' + body + '\n')
            self.write(self.source, impl, original)
            result = pg.run_gate(self.source, self.root, sys.executable)
            self.assertEqual(result['raw_exit'], 2, result['raw_stdout'])
            retained, deferred = pg.partition_generated_findings(result, {})
            self.assertTrue(any(f'[{rule}]' in line for line in retained), retained)
            self.assertEqual(deferred, [])
            self.assertEqual((self.source / impl).read_text(), original)
            # Pregate's ordinary dirty update is in its own anchor: it remains legacy.
            run, report = self.cli(text)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn('생성 본문 S1 미검증 (0건)', report)
            self.assertEqual((self.source / impl).read_text(), original)

    def test_provenance_records_only_current_render_ast_ranges(self):
        path = 'application/garden/driven_layer/adapter/persistence/unit_of_work/garden_unit_of_work.py'
        text = spec_text([f'add {path}', f'update {SERVICE}'], [f'{path}::DjangoGardenUnitOfWork',
            f'{path}::DjangoGardenUnitOfWork.after_commit(callback: object) -> None',
            f'{path}::DjangoGardenUnitOfWork.__enter__() -> None', f'{SERVICE}::new_query() -> str'])
        _, report = self.materialize(text)
        generated = report['generated_methods']
        module = ast.parse((self.copy / path).read_text())
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef))
        methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
        self.assertEqual(generated[path], [dict(owner='DjangoGardenUnitOfWork', method=node.name,
            lineno=node.lineno, end_lineno=node.end_lineno) for node in methods])
        self.assertEqual([item['method'] for item in generated[SERVICE]], ['new_query'])
        new_node = next(node for node in ast.parse((self.copy / SERVICE).read_text()).body
                        if isinstance(node, ast.FunctionDef) and node.name == 'new_query')
        self.assertEqual(generated[SERVICE][0]['lineno'], new_node.lineno)
        self.assertEqual(generated[SERVICE][0]['end_lineno'], new_node.end_lineno)
        self.assertTrue((self.copy / SERVICE).read_bytes().startswith(ORIGINAL.encode()))
        self.write(self.source, path, 'class DjangoGardenUnitOfWork:\n'
                   '    def after_commit(self, callback):\n        raise NotImplementedError\n')
        _, report = self.materialize(spec_text([f'update {path}']))
        self.assertNotIn(path, report['generated_methods'])

    def test_generated_ranges_follow_final_marker_composition(self):
        originals = [ORIGINAL, ORIGINAL.replace('from decimal import Decimal\n',
            'from decimal import Decimal\nimport pytest\npytestmark = [\n    pytest.mark.fast,\n]\n')]
        for original in originals:
            with self.subTest(original=original):
                self.write(self.source, SERVICE, original)
                text = spec_text([f'update {SERVICE}'], [f'{SERVICE}::new_query() -> str'],
                                 owner=f'{SERVICE} [markers: slow]')
                _, report = self.materialize(text)
                final = (self.copy / SERVICE).read_text()
                module = ast.parse(final)
                generated = report['generated_methods'][SERVICE]
                self.assertEqual([(item['owner'], item['method']) for item in generated], [('', 'new_query')])
                new_query = next(node for node in module.body
                                 if isinstance(node, ast.FunctionDef) and node.name == 'new_query')
                self.assertEqual((generated[0]['lineno'], generated[0]['end_lineno']),
                                 (new_query.lineno, new_query.end_lineno))
                self.assertIn('pytestmark = [pytest.mark.slow]', final)
                old_query = next(node for node in module.body
                                 if isinstance(node, ast.FunctionDef) and node.name == 'old_query')
                self.assertEqual(ast.get_source_segment(final, old_query),
                                 'def old_query() -> str:\n    return "unchanged"')
                self.assertEqual((self.source / SERVICE).read_text(), original)

    def test_generated_partition_uses_full_normalized_cohort_and_all_raw_locations(self):
        path = 'application/orders/driven_layer/adapter/persistence/unit_of_work/order_unit_of_work.py'
        message = 'after_commit 구현이 transaction.on_commit 으로 채워지지 않았다'
        line = f'check-port-adapter-pairing.py :: [#376] {path}:N: {message}'
        records = [dict(checker='check-port-adapter-pairing.py', rule='#376', severity='error',
                        file=f'{path}:{n}', message=message) for n in (5, 15)]
        generated = {path: [dict(owner='First', method='after_commit', lineno=5, end_lineno=6),
                            dict(owner='Second', method='after_commit', lineno=15, end_lineno=16)]}
        def gate(rows, unmatched=(), lines=None):
            return dict(raw_exit=2, raw_stdout='raw', attributed_lines=lines or [line], records=rows,
                        unmatched_lines=list(unmatched), candidate_lines=[], candidate_records=[])
        for rows, provenance, unmatched, want in [
            (records, generated, [], (0, 1)),
            (records, {path: generated[path][:1]}, [], (1, 0)),
            ([records[0], dict(records[1], file=path)], generated, [], (1, 0)),
            ([records[0], dict(records[1], file=f'{path}:N', file_raw=f'/tmp/raw/{path}:15')],
             generated, [], (1, 0)),
            ([], generated, [], (1, 0)),
            (records, generated, [line], (1, 0)),
            (records, {}, [], (1, 0)),
            (records, {path: [dict(generated[path][0], method='other')]}, [], (1, 0)),
        ]:
            with self.subTest(rows=rows, provenance=provenance, unmatched=unmatched):
                retained, deferred = pg.partition_generated_findings(gate(rows, unmatched), provenance)
                self.assertEqual((len(retained), len(deferred)), want)
        # Same rule/path with a different message is a different attribution key.
        other = dict(records[1], file=f'{path}:25', message='other diagnostic')
        other_line = f'check-port-adapter-pairing.py :: [#376] {path}:N: other diagnostic'
        retained, deferred = pg.partition_generated_findings(gate(records + [other], lines=[line, other_line]), generated)
        self.assertEqual(retained, [other_line])
        self.assertEqual(len(deferred), 1)
        robust = dict(records[0], rule='#566')
        robust_line = line.replace('#376', '#566')
        self.assertEqual(pg.partition_generated_findings(gate([robust], lines=[robust_line]), generated), ([robust_line], []))

    def test_run_gate_preserves_complete_material_and_optional_candidates(self):
        record = dict(checker='checker.py', rule='#376', severity='error', file='sample.py:5', message='bad')
        line = 'checker.py :: [#376] sample.py:N: bad'
        payload = dict(attributed_lines=[line], records=[record], unmatched_lines=[])
        for candidates in ({}, dict(candidate_lines=['candidate'], candidate_records=[dict(record, severity='info')])):
            (self.root / 'introduced.json').write_text(json.dumps(dict(payload, **candidates)))
            proc = subprocess.CompletedProcess([], 2, 'raw stdout untouched', '')
            with patch.object(pg.subprocess, 'run', return_value=proc):
                result = pg.run_gate(self.source, self.root, sys.executable)
            self.assertEqual(result['raw_exit'], 2)
            self.assertEqual(result['raw_stdout'], 'raw stdout untouched')
            self.assertEqual(result['attributed_lines'], [line])
            self.assertEqual(result['records'], [record])
            self.assertEqual(result['unmatched_lines'], [])
            self.assertEqual(result['candidate_lines'], candidates.get('candidate_lines', []))
            self.assertEqual(result['candidate_records'], candidates.get('candidate_records', []))

    def test_run_gate_rejects_missing_material_and_unexplained_raw_red(self):
        complete = dict(attributed_lines=[], records=[], unmatched_lines=[])
        for code, payload in [(1, complete), (2, complete), (0, {}),
                (0, dict(complete, records=None)), (0, dict(complete, candidate_lines=[])),
                (0, dict(complete, unmatched_lines=None)), (0, dict(complete, attributed_lines=None))]:
            with self.subTest(code=code, payload=payload):
                (self.root / 'introduced.json').write_text(json.dumps(payload))
                proc = subprocess.CompletedProcess([], code, 'raw stdout', '')
                with patch.object(pg.subprocess, 'run', return_value=proc):
                    with self.assertRaises(pg.RunError):
                        pg.run_gate(self.source, self.root, sys.executable)

    def test_declaration_only_cli_and_report_dispositions(self):
        text = self.effects(spec_text([f'update {SERVICE}'], [f'{SERVICE}::ReadBooks']),
                            f'{SERVICE}::ReadBooks  read-only  uow=BookUnitOfWork')
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn('선언 확정', report)
        self.assertEqual(pg.check_report(text, report)[0], 3)
        stable = pg._stable_id(f'[#197] {SERVICE}')
        disposed = report + f'\n- `{stable}` **ignored** 명시 검토\n'
        self.assertEqual(pg.check_report(text, disposed)[0], 0)
        self.assertEqual(pg.check_report(text, disposed)[2].get("declarations"), "1")
        self.assertEqual(pg.check_report(text.replace('uow=BookUnitOfWork', 'uow=Other'), disposed)[0], 3)
        result = f'{SERVICE_DIR}/contract/response/list_books_response.py'
        self.write(self.source, result, 'class ListBooksResponse: pass\n')
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'response fixture')
        text = spec_text([f'update {result}'], [f'{result}::ListBooksResponse {{item: Unknown}}'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        self.assertIn('선언 후보', report)
        self.assertIn('출처', report)
        self.assertEqual(pg.check_report(text, report)[0], 0)
        text = text.replace('```imports\n', f'```imports\n{result}  from application.missing import Unknown\n')
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 5, run.stdout + run.stderr)

    def test_marker_update_cli_real_test_config_rule(self):
        unit = 'application/garden/test/unit/test_book.py'
        for original, marker, expected in [
            ('def test_book(): pass\n', 'django_db', True),
            ('import pytest\npytestmark = pytest.mark.django_db\ndef test_book(): pass\n', '', False),
            ('import pytest\npytestmark = ()\n@pytest.mark.django_db\ndef test_book(): pass\n', '', False)]:
            self.write(self.source, unit, original)
            _git(self.source, 'add', '-A')
            _git(self.source, 'commit', '-qm', 'marker fixture')
            text = spec_text([f'update {unit}'], owner=f'{unit} [markers: {marker}]')
            run, report = self.cli(text)
            self.assertIn(run.returncode, (0, 2), run.stdout + run.stderr)
            self.assertEqual('[#387]' in report, expected, report)
            self.assertEqual((self.source / unit).read_text(), original)
        # Direct checker retains class/function DB evidence after clearing only module marks.
        self.materialize(text)
        self.assertIn('[#387]', self.checker('check-test-config.py'))

    def test_typegraph_real_tree_cross_module_alias_cycles_and_ohs_imports(self):
        result = 'application/garden/application_layer/books/list_books/list_books_result.py'
        aggregate = 'application/garden/domain_layer/book/book.py'
        entity = 'application/garden/domain_layer/book/entity/page.py'
        helper = 'application/garden/application_layer/books/list_books/item.py'
        self.write(self.source, aggregate, 'class Book: pass\n')
        self.write(self.source, entity, 'class Page: pass\n')
        self.write(self.source, helper, 'from .list_books_result import ListBooksResult\n'
                   'from application.garden.domain_layer.book.book import Book\n'
                   'class _Item:\n    parent: ListBooksResult\n    book: Book\n')
        for annotation, imports in [('_Item', ['from .item import _Item']),
                                    ('book.Book', ['import application.garden.domain_layer.book.book as book']),
                                    ('Page', ['from application.garden.domain_layer.book.entity.page import Page']),
                                    ('application.garden.domain_layer.book.book.Book', [])]:
            text = spec_text([f'add {result}'], [f'{result}::ListBooksResult {{item: {annotation}}}'],
                             [f'{result}  {i}' for i in imports])
            plan, _ = self.materialize(text)
            findings = pg.check_declarations(plan, self.copy)
            self.assertEqual([(f.rule, f.confirmed) for f in findings], [('#202', True)], annotation)
        # Same-name local value object wins over the aggregate catalog.
        vo = 'application/garden/domain_layer/book/shared_value_object/book.py'
        self.write(self.source, vo, 'class Book:\n    text: str\n')
        text = spec_text([f'add {result}'], [f'{result}::ListBooksResult {{item: Book}}'],
                        [f'{result}  from application.garden.domain_layer.book.shared_value_object.book import Book'])
        plan, _ = self.materialize(text)
        self.assertEqual(pg.check_declarations(plan, self.copy), [])
        # Result consumption must not synthesize a domain import into OHS.
        text = self.service_spec(imports=['from application.garden.application_layer.books.list_books.list_books_result import ListBooksResult'],
                                extra_paths=[f'add {result}'], extra_symbols=[f'{result}::ListBooksResult {{item: Book}}'])
        plan, _ = self.materialize(text)
        self.assertEqual([(f.rule, f.confirmed) for f in pg.check_declarations(plan, self.copy)], [('#202', False)])
        self.assertNotIn('[#95]', self.checker('check-context-isolation.py'))
        self.assertNotIn('[#96]', self.checker('check-event-publish.py'))
        self.materialize(self.service_spec(imports=['from application.garden.domain_layer.book.book import Book']))
        self.assertIn('[#95]', self.checker('check-context-isolation.py'))
        self.assertIn('[#96]', self.checker('check-event-publish.py'))

    def test_unresolved_uow_never_confirms_and_declaration_owners_group(self):
        for effect, expected in [('read-only', [('#197', False)]), ('write', [])]:
            text = self.effects(spec_text([f'update {SERVICE}'], [f'{SERVICE}::ListBooks',
                f'{SERVICE}::ListBooks.__init__(self, uow: StrangeUnitOfWork)']),
                f'{SERVICE}::ListBooks  {effect}  uow=none')
            plan, errors = pg.parse_spec(text)
            self.assertEqual(errors, [])
            self.assertEqual([(f.rule, f.confirmed) for f in pg.check_declarations(plan, self.source)], expected)
        text = self.effects(spec_text([f'update {SERVICE}'], [f'{SERVICE}::First', f'{SERVICE}::Second']),
                            f'{SERVICE}::First  read-only  uow=X', f'{SERVICE}::Second  read-only  uow=Y')
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn('First:', report)
        self.assertIn('Second:', report)
        stable = pg._stable_id(f'[#197] {SERVICE}')
        self.assertEqual(report.count(f'`{stable}`'), 1)
        self.assertEqual(pg.check_report(text, report + f'\n- `{stable}` **filtered** reviewed\n')[0], 0)

    def test_marker_update_noop_and_import_binding_are_preserved(self):
        for original in ['import pytest\npytestmark = []\ndef test_case(): pass\n',
                         'from somewhere import pytestmark\ndef test_case(): pass\n']:
            self.write(self.source, TEST, original)
            _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers:]'))
            self.assertEqual((self.copy / TEST).read_text(), original)
            self.assertEqual(report['materialized'], [])

    def test_typegraph_container_identity_and_literal_alias(self):
        result = 'application/garden/application_layer/books/list_books/list_books_result.py'
        domain_import = f'{result}  from application.garden.domain_layer.book.book import Book'
        for annotation, symbols, imports, expected in [
            ('Mapping[Book]', [f'{result}::Mapping {{value: int}}'], [], [('#202', False)]),
            ('list[Book]', [f'{result}::alias list = Mapping'], [], [('#202', False)]),
            ('LiteralName["Book"]', [], [f'{result}  from typing import Literal as LiteralName'], []),
            ('Mapping[str, Book]', [], [f'{result}  from typing import Mapping'], [('#202', True)]),
            ('Mapping[str, Book]', [], [], [('#202', False)])]:
            with self.subTest(annotation=annotation, imports=imports):
                plan, errors = pg.parse_spec(spec_text([f'update {result}'], [*symbols,
                    f'{result}::ListBooksResult {{value: {annotation}}}'], [domain_import, *imports]))
                self.assertEqual(errors, [])
                self.assertEqual([(f.rule, f.confirmed) for f in pg.check_declarations(plan, self.source)], expected)

    def test_marker_new_list_evaluates_after_pytest_binding(self):
        from types import ModuleType, SimpleNamespace
        from unittest.mock import patch
        fake_pytest = ModuleType('pytest')
        fake_pytest.mark = SimpleNamespace(slow='slow', django_db='django_db')
        for prefix in ['', '"""기존 문서."""\nfrom __future__ import annotations\n']:
            with self.subTest(prefix=prefix):
                original = prefix + 'import pytest\ndef test_case():\n    return "original body"\n'
                self.write(self.source, TEST, original)
                _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers: slow]'))
                updated = (self.copy / TEST).read_text()
                namespace = {}
                with patch.dict(sys.modules, {'pytest': fake_pytest}):
                    exec(compile(updated, TEST, 'exec'), namespace)
                self.assertEqual(namespace['pytestmark'], ['slow'])
                self.assertEqual(namespace['test_case'](), 'original body')
                self.assertIn('import pytest\ndef test_case():\n    return "original body"\n', updated)
                self.assertTrue(updated.startswith(prefix))
                self.assertEqual((self.source / TEST).read_bytes(), original.encode())
                self.assertEqual(report['materialized'], [TEST])

    def test_marker_subscript_mutations_remain_s5_without_writes(self):
        from types import ModuleType, SimpleNamespace
        from unittest.mock import patch
        fake_pytest = ModuleType('pytest')
        fake_pytest.mark = SimpleNamespace(slow='slow', django_db='django_db')
        for mutation in ['pytestmark[0] = pytest.mark.django_db', 'del pytestmark[0]',
                         'pytestmark[:] = [pytest.mark.django_db]',
                         'pytestmark[0] += pytest.mark.django_db',
                         'if True:\n    pytestmark[0] = pytest.mark.django_db']:
            for markers in ['', 'slow']:
                with self.subTest(mutation=mutation, markers=markers):
                    original = 'import pytest\npytestmark = [pytest.mark.slow]\n' + mutation + '\n'
                    self.write(self.source, TEST, original)
                    namespace = {}
                    with patch.dict(sys.modules, {'pytest': fake_pytest}):
                        exec(compile(original, TEST, 'exec'), namespace)
                    if mutation == 'pytestmark[0] = pytest.mark.django_db':
                        self.assertEqual(namespace['pytestmark'], ['django_db'])
                    _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers: {markers}]'))
                    self.assertEqual((self.copy / TEST).read_bytes(), original.encode())
                    self.assertEqual((self.source / TEST).read_bytes(), original.encode())
                    self.assertEqual(report['materialized'], [])
                    self.assertTrue(any('S5' in note and 'subscript' in note for note in report['unsimulated']), report)

    def test_marker_method_mutations_preserve_bytes_and_report_s5(self):
        for mutation in ['pytestmark.append(pytest.mark.django_db)', 'pytestmark.pop()',
                         'if True:\n    pytestmark.extend([pytest.mark.django_db])']:
            for markers in ['', 'slow']:
                with self.subTest(mutation=mutation, markers=markers):
                    original = 'import pytest\npytestmark = [pytest.mark.slow]\n' + mutation + '\n'
                    self.write(self.source, TEST, original)
                    text = spec_text([f'update {TEST}'], owner=f'{TEST} [markers: {markers}]')
                    _, report = self.materialize(text)
                    self.assertEqual((self.copy / TEST).read_bytes(), original.encode())
                    self.assertEqual((self.source / TEST).read_bytes(), original.encode())
                    self.assertEqual(report['materialized'], [])
                    self.assertTrue(any('S5' in note and 'method' in note for note in report['unsimulated']), report)
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'synthetic marker mutation fixture')
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        self.assertIn('S5', report)
        self.assertIn('method', report)
        self.assertEqual(pg.check_report(text, report)[0], 0)
        self.assertEqual((self.source / TEST).read_bytes(), original.encode())

    def test_unresolved_named_uow_alias_keeps_declaration_candidate(self):
        path = 'application/garden/application_layer/books/list_books/list_books_use_case.py'
        for effect in ['read-only', 'write']:
            for annotation, aliases, expected in [
                ('StrangeUnitOfWork', [], [('#197', False)]),
                ('U', ['alias U = StrangeUnitOfWork'], [('#197', False)]),
                ('U', ['alias U = V', 'alias V = StrangeUnitOfWork'], [('#197', False)]),
                ('U', ['alias U = list[StrangeUnitOfWork]'], [('#197', False)]),
                ('U', ['alias U = P'], []),
                ('U', ['alias U = int'], []),
                ('U', ['alias U = StrangeUnitOfWork', 'StrangeUnitOfWork {value: int}'], []),
            ]:
                with self.subTest(effect=effect, aliases=aliases):
                    text = self.effects(spec_text([f'update {path}'], [
                        *[f'{path}::{alias}' for alias in aliases], f'{path}::ListBooks',
                        f'{path}::ListBooks.__init__(self, uow: {annotation})']),
                        f'{path}::ListBooks {effect} uow=none')
                    plan, errors = pg.parse_spec(text)
                    self.assertEqual(errors, [])
                    found = pg.check_declarations(plan, self.source)
                    self.assertEqual([(f.rule, f.confirmed) for f in found], expected if effect == 'read-only' else [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
