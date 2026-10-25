#!/usr/bin/env python3
"""실제 전사·checker 회귀: OHS update의 명시 새 함수와 입장 표 첫 Python artifact.

update 전사 유실, 기존 바인딩 덮기, 무명시 raise 추론, support로 marker 전파를 잡는다.
F4-115 — update 도메인 서비스 서명 · OHS 번역 출처 칸의 선언 예보를 CLI · `--check-report` 처분과 2.26.1 배포판 대조로 고정한다.
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
# F4-73 — 현장 반례(8-D-2): update 저장소의 새 메서드 반환 `frozenset[UUID]` 가 G1 전 선언 확정으로 선다.
RECORD_DOMAIN = "application/fortune_record/domain_layer/fortune_record"
REPOSITORY = f"{RECORD_DOMAIN}/fortune_record_repository.py"
REPOSITORY_ORIGINAL = ('from __future__ import annotations\n\nfrom abc import ABC, abstractmethod\nfrom uuid import UUID\n\n'
                       'from application.fortune_record.domain_layer.fortune_record.fortune_record import FortuneRecord\n\n\n'
                       'class FortuneRecordRepository(ABC):\n'
                       '    @abstractmethod\n    def find(self, record_id: UUID) -> FortuneRecord | None: ...\n')
RECORDED_VO = f"{RECORD_DOMAIN}/value_object/recorded_character_ids.py"
# 기준선에만 있는 프로젝트 import 는 후상태의 확정 근거가 아니다(구현이 같은 이름을 domain 에서 들이면 실검사기는 통과한다).
ORDER_DOMAIN = "application/orders/domain_layer/order"
ORDER_REPOSITORY = f"{ORDER_DOMAIN}/order_repository.py"
ORDER_ORIGINAL = ('from abc import ABC, abstractmethod\nfrom support.read_models import Summary\n\n\n'
                  'class OrderRepository(ABC):\n    pass\n')
# F4-115 — 현장 꼴 둘(update 도메인 서비스의 새 공개 `-> bool` · update OHS 창구가 잡은 도메인 예외 값을 로그에 씀)과 낡은 출처 칸.
# «옛 판» 은 2.26.1 배포 커밋 고정(HEAD 금지 — 이 고침을 커밋한 뒤에도 옛 판이다).
_RELEASED_2261_COMMIT = "55ab56e5"
POLICY = "application/garden/domain_layer/domain_service/watering.py"
POLICY_ORIGINAL = ('"""Which plants need water."""\nfrom __future__ import annotations\n\n'
                   'from application.garden.domain_layer.plant.plant import Plant\n\n\n'
                   'class WateringPolicy:\n    def due(self, plants: tuple[Plant, ...]) -> tuple[Plant, ...]:\n'
                   '        return tuple(p for p in plants if self._dry(p))\n\n'
                   '    def _dry(self, plant: Plant) -> bool:\n        return True\n')
UNREADABLE = "application/garden/domain_layer/plant/exception/plant_unreadable.py"
CATCHING = ('"""Existing service."""\nfrom __future__ import annotations\n\n'
            'from application.garden.domain_layer.plant.exception.plant_unreadable import PlantUnreadable\n'
            'from application.garden.driving_layer.open_host_service.catalog.contract.exception.plant_unavailable_exception '
            'import PlantUnavailableException\n\n\n'
            'def read_plant_query(name: str) -> str:\n    try:\n        return _read(name)\n'
            '    except PlantUnreadable:\n        raise PlantUnavailableException() from None\n\n\n'
            'def _read(name: str) -> str:\n    raise PlantUnreadable(name)\n')


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

    def test_application_root_file_is_not_a_new_bc(self) -> None:
        # F4-42 — `application/` 바로 아래 «파일»은 BC 가 아니다(`application/__init__.py/__init__.py` 를 만들려다 실행 불능).
        root_init, bc_init = "application/__init__.py", "application/fortune/__init__.py"
        _, report = self.materialize(spec_text([f"empty {root_init}", f"empty {bc_init}"]))
        self.assertTrue((self.copy / root_init).is_file())
        self.assertIn(root_init, report["materialized"])
        self.assertTrue(any(p.is_dir() for p in (self.copy / "application/fortune").iterdir()))

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

    def cli(self, text, scripts=SCRIPTS):
        spec = self.root / 'design.md'
        spec.write_text(text)
        report = self.root / 'report.md'
        if report.exists(): report.unlink()
        run = subprocess.run([sys.executable, '-B', str(scripts / 'design_pregate.py'), str(spec),
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

    def repository_fixture(self) -> None:
        self.write(self.source, REPOSITORY, REPOSITORY_ORIGINAL)
        self.write(self.source, f'{RECORD_DOMAIN}/fortune_record.py', 'class FortuneRecord:\n    pass\n')
        self.write(self.source, RECORDED_VO, 'class RecordedCharacterIds:\n    pass\n')
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'repository fixture')

    def repository_spec(self, *methods, imports=()):
        return spec_text([f'update {REPOSITORY}'], [f'{REPOSITORY}::FortuneRecordRepository(ABC)',
                         *[f'{REPOSITORY}::FortuneRecordRepository.{m}' for m in methods]],
                         [f'{REPOSITORY}  {i}' for i in imports])

    def test_repository_return_forecast_blocks_without_materialization(self):
        self.repository_fixture()
        text = self.repository_spec(
            'recorded_character_ids(account_id: int, character_ids: frozenset[UUID]) -> frozenset[UUID]',
            'recorded_rows(account_id: int) -> dict[str, int]', 'exists_for(account_id: int) -> bool')
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn('실체화 0', run.stdout)
        self.assertIn('선언 확정 1건', run.stdout)
        stable = pg._stable_id(f'[#355] {REPOSITORY}')
        confirmed = pg._subsection(report, '선언 확정')
        self.assertEqual(confirmed.count(f'`{stable}`'), 1, confirmed)
        self.assertIn(f'- `{stable}` [#355] {REPOSITORY} — FortuneRecordRepository.recorded_character_ids: '
                      '`recorded_character_ids` 반환 `UUID.frozenset` 이 애그리거트도 값 객체도 아니다', confirmed)
        self.assertIn('FortuneRecordRepository.recorded_rows:', confirmed)
        self.assertIn('FortuneRecordRepository.exists_for:', pg._subsection(report, '선언 후보'))
        self.assertEqual(pg.check_report(text, report)[0], 3)
        disposed = report + f'\n- `{stable}` **ignored** 빚 매칭 검토\n'
        code, problems, info = pg.check_report(text, disposed)
        self.assertEqual(code, 0, problems)
        self.assertEqual((info['attributed'], info['declarations'], info['candidates']), ('0', '1', '1'))
        code, problems, _ = pg.check_report(text, disposed, current_digest='0' * 16)
        self.assertEqual(code, 3)
        self.assertTrue(any('stale(툴체인)' in p for p in problems), problems)
        self.assertEqual((self.source / REPOSITORY).read_text(), REPOSITORY_ORIGINAL)
        # 선언 예보의 검사기 판정은 수집만 한다 — 레코드 파일 · 위반 이력을 남기지 않는다(실체화 0 이라 게이트도 돌지 않았다).
        self.assertFalse(Path(self.env['DJR_FINDINGS_JSON']).exists())
        self.assertFalse(Path(self.env['DJR_VIOLATIONS_DIR']).exists())

    def test_repository_candidate_is_nonblocking_and_explicit_import_is_clean(self):
        self.repository_fixture()
        text = self.repository_spec('recorded(account_id: int) -> RecordedCharacterIds')
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        self.assertIn('예보 불확정', pg._subsection(report, '선언 후보'))
        self.assertEqual(pg.check_report(text, report)[0], 0)
        text = self.repository_spec('recorded(account_id: int) -> RecordedCharacterIds', imports=[
            'from application.fortune_record.domain_layer.fortune_record.value_object.recorded_character_ids '
            'import RecordedCharacterIds'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        self.assertNotIn(REPOSITORY, pg._subsection(report, '선언 확정') + pg._subsection(report, '선언 후보'))

    def test_repository_baseline_only_origin_is_candidate_until_the_spec_states_it(self):
        self.write(self.source, ORDER_REPOSITORY, ORDER_ORIGINAL)
        self.write(self.source, f'{ORDER_DOMAIN}/order.py', 'class Order:\n    pass\n')
        self.write(self.source, f'{ORDER_DOMAIN}/value_object/summary.py', 'class Summary:\n    pass\n')
        self.write(self.source, 'support/read_models.py', 'class Summary:\n    pass\n')
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'order repository fixture')
        rows = [f'{ORDER_REPOSITORY}::OrderRepository(ABC)', f'{ORDER_REPOSITORY}::OrderRepository.summary() -> Summary']
        detail = 'OrderRepository.summary: `summary` 반환 `Summary` 이 애그리거트도 값 객체도 아니다'
        stable = pg._stable_id(f'[#355] {ORDER_REPOSITORY}')
        text = spec_text([f'update {ORDER_REPOSITORY}'], rows)
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        self.assertNotIn(ORDER_REPOSITORY, pg._subsection(report, '선언 확정'))
        candidates = pg._subsection(report, '선언 후보')
        self.assertIn(f'- `{stable}` [#355] {ORDER_REPOSITORY} — {detail} — 예보 불확정: 반환 이름 `Summary` '
                      '출처 미해소(기준선에만 있는 출처', candidates)
        code, problems, info = pg.check_report(text, report)
        self.assertEqual(code, 0, problems)
        self.assertEqual((info['attributed'], info['declarations'], info['candidates']), ('0', '0', '1'))
        text = spec_text([f'update {ORDER_REPOSITORY}'], rows, [f'{ORDER_REPOSITORY}  from support.read_models import Summary'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn('선언 확정 1건', run.stdout)
        self.assertIn(f'- `{stable}` [#355] {ORDER_REPOSITORY} — {detail}\n', pg._subsection(report, '선언 확정') + '\n')
        self.assertNotIn(ORDER_REPOSITORY, pg._subsection(report, '선언 후보'))
        self.assertEqual(pg.check_report(text, report)[0], 3)
        self.assertEqual((self.source / ORDER_REPOSITORY).read_text(), ORDER_ORIGINAL)

    def test_repository_new_method_is_not_hidden_by_another_class_debt(self):
        self.write(self.source, ORDER_REPOSITORY, (
            'from abc import ABC, abstractmethod\nfrom uuid import UUID\n\n\n'
            'class LegacyOrderRepository(ABC):\n    @abstractmethod\n    def owner_id(self) -> UUID: ...\n\n\n'
            'class OrderRepository(ABC):\n    pass\n'))
        self.write(self.source, f'{ORDER_DOMAIN}/order.py', 'class Order:\n    pass\n')
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'legacy order repository fixture')
        text = spec_text([f'update {ORDER_REPOSITORY}'], [f'{ORDER_REPOSITORY}::OrderRepository(ABC)',
                         f'{ORDER_REPOSITORY}::OrderRepository.owner_id() -> UUID'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        stable = pg._stable_id(f'[#355] {ORDER_REPOSITORY}')
        self.assertIn(f'- `{stable}` [#355] {ORDER_REPOSITORY} — OrderRepository.owner_id: '
                      '`owner_id` 반환 `UUID` 이 애그리거트도 값 객체도 아니다\n', pg._subsection(report, '선언 확정') + '\n')
        self.assertEqual(pg.check_report(text, report)[0], 3)

    def test_repository_heir_regression_matching_only_an_ancestor_debt_is_a_candidate(self):
        # 자식이 이미 정상 계약으로 재정의한 메서드를 조상의 기존 빚 꼴로 되돌리는 명세 — 조용히 지우지 않고 후보로 낸다.
        original = ('from abc import ABC, abstractmethod\nfrom uuid import UUID\n\n'
                    'from application.orders.domain_layer.order.value_object.owner_id import OwnerId\n\n\n'
                    'class LegacyOrderRepository(ABC):\n    @abstractmethod\n    def owner_id(self) -> UUID: ...\n\n\n'
                    'class OrderRepository(LegacyOrderRepository):\n    @abstractmethod\n    def owner_id(self) -> OwnerId: ...\n')
        self.write(self.source, ORDER_REPOSITORY, original)
        self.write(self.source, f'{ORDER_DOMAIN}/order.py', 'class Order:\n    pass\n')
        self.write(self.source, f'{ORDER_DOMAIN}/value_object/owner_id.py', 'class OwnerId:\n    pass\n')
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'heir order repository fixture')
        text = spec_text([f'update {ORDER_REPOSITORY}'], [f'{ORDER_REPOSITORY}::OrderRepository(LegacyOrderRepository)',
                         f'{ORDER_REPOSITORY}::OrderRepository.owner_id() -> UUID'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        stable = pg._stable_id(f'[#355] {ORDER_REPOSITORY}')
        self.assertNotIn(ORDER_REPOSITORY, pg._subsection(report, '선언 확정'))
        self.assertIn(f'- `{stable}` [#355] {ORDER_REPOSITORY} — OrderRepository.owner_id: `owner_id` 반환 `UUID` 이 '
                      '애그리거트도 값 객체도 아니다 — 예보 불확정: 이 클래스가 기준선에서 직접 정의하던 반환을 조상 '
                      '`LegacyOrderRepository.owner_id` 의 기존 빚과 같은 꼴(같은 판정문)로 바꾼다 — 물음: 이 메서드는 조상 '
                      '`LegacyOrderRepository` 의 선언을 그대로 물려받는가(그러면 기존 빚이다) · 이 클래스에서 재정의하는가'
                      '(그러면 검사기가 이 클래스에도 새 줄을 낸다 · 조상 `LegacyOrderRepository` 의 줄과 같은 판정문이면 '
                      'G2 registry 는 이것을 새 위반으로 귀속하지 않을 수 있다)\n', pg._subsection(report, '선언 후보') + '\n')
        code, problems, info = pg.check_report(text, report)
        self.assertEqual(code, 0, problems)
        self.assertEqual((info['declarations'], info['candidates']), ('0', '1'))
        self.assertEqual((self.source / ORDER_REPOSITORY).read_text(), original)

    def test_repository_source_root_package_is_not_a_standard_library_origin(self):
        nested = f'src/{ORDER_REPOSITORY}'
        self.write(self.source, nested, ('from abc import ABC, abstractmethod\n'
                                         'from calendar.read_models import CalendarSummary\n\n\n'
                                         'class OrderRepository(ABC):\n    pass\n'))
        self.write(self.source, f'src/{ORDER_DOMAIN}/order.py', 'class Order:\n    pass\n')
        self.write(self.source, 'src/calendar/__init__.py', '')
        self.write(self.source, 'src/calendar/read_models.py', 'class CalendarSummary:\n    pass\n')
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'src layout fixture')
        text = spec_text([f'update {nested}'], [f'{nested}::OrderRepository(ABC)',
                         f'{nested}::OrderRepository.calendar_summary() -> CalendarSummary'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        self.assertNotIn(nested, pg._subsection(report, '선언 확정'))
        self.assertIn('OrderRepository.calendar_summary: `calendar_summary` 반환 `CalendarSummary` 이 애그리거트도 값 객체도 '
                      '아니다 — 예보 불확정: 반환 이름 `CalendarSummary` 출처 미해소(기준선에만 있는 출처',
                      pg._subsection(report, '선언 후보'))
        self.assertEqual(pg.check_report(text, report)[0], 0)

    def test_repository_add_shares_registry_id_and_needs_one_disposition(self):
        self.repository_fixture()
        added = 'application/fortune_record/domain_layer/character/character_repository.py'
        text = spec_text([f'add {added}'], [f'{added}::CharacterRepository(ABC)',
                         f'{added}::CharacterRepository.recorded_character_ids(account_id: int) -> frozenset[UUID]'],
                         [f'{added}  from uuid import UUID'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        stable = pg._stable_id(f'[#355] {added}')
        self.assertIn(f'`{stable}`', pg._subsection(report, '예보 항목'))
        self.assertIn(f'`{stable}`', pg._subsection(report, '선언 확정'))
        registry_ids = pg._REPORT_ID_RE.findall(pg._subsection(report, '예보 항목'))
        declared_ids = pg._REPORT_ID_RE.findall(pg._subsection(report, '선언 확정'))
        self.assertEqual((registry_ids.count(stable), declared_ids.count(stable)), (1, 1))
        # 두 채널에 실린 같은 ID 는 처분 한 줄로 닫힌다 — 그 한 줄이 없으면 나머지를 다 처분해도 불비다.
        others = ''.join(f'\n- `{i}` **ignored** 빚 매칭 검토' for i in sorted(set(registry_ids + declared_ids) - {stable}))
        self.assertEqual(pg.check_report(text, report + others + '\n')[0], 3)
        self.assertEqual(pg.check_report(text, report + others + f'\n- `{stable}` **ignored** 빚 매칭 검토\n')[0], 0)

    def test_repository_forecast_reads_dot_slash_plan_path(self):
        self.repository_fixture()
        dotted = f'./{REPOSITORY}'
        text = spec_text([f'update {dotted}'], [f'{dotted}::FortuneRecordRepository(ABC)',
                         f'{dotted}::FortuneRecordRepository.recorded_character_ids(account_id: int) -> frozenset[UUID]'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        stable = pg._stable_id(f'[#355] {REPOSITORY}')
        self.assertIn(f'- `{stable}` [#355] {REPOSITORY} — FortuneRecordRepository.recorded_character_ids: '
                      '`recorded_character_ids` 반환 `UUID.frozenset` 이 애그리거트도 값 객체도 아니다',
                      pg._subsection(report, '선언 확정'))
        self.assertEqual(pg.check_report(text, report)[0], 3)

    def garden_fixture(self) -> None:
        self.write(self.source, 'application/garden/domain_layer/plant/plant.py', 'class Plant:\n    pass\n')
        self.write(self.source, UNREADABLE, 'class PlantUnreadable(Exception):\n    pass\n')
        self.write(self.source, 'application/garden/domain_layer/domain_service/__init__.py', '')
        self.write(self.source, POLICY, POLICY_ORIGINAL)
        self.write(self.source, f'{SERVICE_DIR}/contract/exception/plant_unavailable_exception.py',
                   'class PlantUnavailableException(Exception):\n    pass\n')
        self.write(self.source, SERVICE, CATCHING)
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'garden fixture')

    def released_2261(self) -> Path:
        """2.26.1 배포 커밋의 scripts 사본(HEAD 금지)."""
        old = self.root / 'released-2261'
        if not old.exists():
            old.mkdir()
            archive = subprocess.run(['git', '-C', str(ROOT), 'archive', _RELEASED_2261_COMMIT, 'dddjango/scripts'],
                                     capture_output=True, check=True)
            subprocess.run(['tar', '-x', '-C', str(old)], input=archive.stdout, check=True)
        return old / 'dddjango' / 'scripts'

    def test_f115_domain_service_bool_declaration_blocks_without_materialization(self):
        # 현장 꼴 1 — update 도메인 서비스에 공개 `-> bool` 을 더한 symbols(2.26.1 은 귀속 0 · G2 에서야 #308).
        self.garden_fixture()
        text = spec_text([f'update {POLICY}'], [f'{POLICY}::WateringPolicy',
                         f'{POLICY}::WateringPolicy.due(plants: tuple[Plant, ...]) -> tuple[Plant, ...]',
                         f'{POLICY}::WateringPolicy.is_asked(plant: Plant, names: tuple[str, ...]) -> bool'])
        old, _ = self.cli(text, scripts=self.released_2261())
        self.assertEqual(old.returncode, 4, old.stdout + old.stderr)
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn('실체화 0', run.stdout)
        self.assertIn('선언 확정 1건', run.stdout)
        stable = pg._stable_id(f'[#308] {POLICY}')
        self.assertIn(f'- `{stable}` [#308] {POLICY} — WateringPolicy.is_asked: `is_asked` 이 bool 을 돌려준다 — '
                      '규칙 위반의 알림은 «도메인 예외»다\n', pg._subsection(report, '선언 확정') + '\n')
        self.assertIn(f'S5 update(OHS 서비스 본체 밖; marker 후상태 무기재 — 유지; 선언한 서명만 예보 · 본문 미검증): {POLICY}', report)
        self.assertEqual(pg.check_report(text, report)[0], 3)
        for label in ('ignored', 'filtered'):
            with self.subTest(disposition=label):
                code, problems, info = pg.check_report(text, report + f'\n- `{stable}` **{label}** 처분 검토\n')
                self.assertEqual(code, 0, problems)
                self.assertEqual((info['declarations'], info['candidates']), ('1', '0'))
        self.assertEqual((self.source / POLICY).read_text(), POLICY_ORIGINAL)
        self.assertFalse(Path(self.env['DJR_FINDINGS_JSON']).exists())

    def test_f115_ohs_catch_reading_the_caught_value_and_catch_all_block(self):
        # 현장 꼴 2 — update OHS 창구가 잡은 도메인 예외 값을 쓴다고 출처 칸에 적은 번역 행 둘 · `Exception` 출처 · 출처 칸 없는 행.
        self.garden_fixture()
        rows = [f'PlantUnavailableException  {SERVICE}  <= PlantUnreadable as',
                f'PlantGoneException  {SERVICE}  <= PlantUnreadable as',
                f'PlantSoldException  {SERVICE}  <= Exception',
                f'PlantLostException  {SERVICE}']
        text = spec_text([f'update {SERVICE}'], exceptions=rows)
        old, _ = self.cli(text, scripts=self.released_2261())
        self.assertEqual(old.returncode, 3, old.stdout + old.stderr)
        self.assertIn('exception-map 행 파싱 불가', old.stdout)
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        confirmed = pg._subsection(report, '선언 확정')
        stable474, stable62 = pg._stable_id(f'[#474] {SERVICE}'), pg._stable_id(f'[#62] {SERVICE}')
        self.assertEqual(sorted(set(pg._REPORT_ID_RE.findall(confirmed))), sorted({stable474, stable62}))
        self.assertIn('PlantUnavailableException ← PlantUnreadable: 도메인 예외를 `as _caught` 로 묶어 참조했다', confirmed)
        self.assertIn('PlantGoneException ← PlantUnreadable:', confirmed)
        self.assertIn('PlantSoldException ← Exception: `except Exception`/bare', confirmed)
        self.assertIn(f'채널 메모: S5 입구 catch 미검증(번역 출처 칸 무기재 — 이 행의 catch 꼴을 더하거나 바꾸면 '
                      f'`<= <잡는 예외>[ as]`): PlantLostException · {SERVICE}', report)
        self.assertIn('번역 출처 칸만 예보 · catch 본문 미검증', report)
        self.assertEqual(pg.check_report(text, report)[0], 3)
        self.assertEqual(pg.check_report(text, report + f'\n- `{stable474}` **filtered** S2 인용\n')[0], 3)
        code, problems, info = pg.check_report(text, report + f'\n- `{stable474}` **filtered** S2 인용\n'
                                               f'- `{stable62}` **ignored** 빚 매칭 검토\n')
        self.assertEqual(code, 0, problems)
        self.assertEqual(info['declarations'], '2')
        self.assertEqual((self.source / SERVICE).read_text(), CATCHING)

    def test_f115_existing_catch_debt_is_a_nonblocking_candidate(self):
        # 구현 검토 I1 — 기준선 창구 catch 가 이미 잡은 값을 쓰는(기존 #474 빚) 꼴에 R-3689 대로 출처 칸을 적으면 후보(비차단)다.
        self.garden_fixture()
        debt = CATCHING.replace('    except PlantUnreadable:\n', '    except PlantUnreadable as unreadable:\n        print(unreadable)\n')
        self.write(self.source, SERVICE, debt)
        _git(self.source, 'add', '-A')
        _git(self.source, 'commit', '-qm', 'existing catch debt')
        text = spec_text([f'update {SERVICE}'], exceptions=[f'PlantUnavailableException  {SERVICE}  <= PlantUnreadable as'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        self.assertIn('- (없음)', pg._subsection(report, '선언 확정'))
        self.assertIn('예보 불확정: 기준선 창구에 `PlantUnreadable` 를 잡는 catch 의 #474 줄이 이미 있다(기존 빚',
                      pg._subsection(report, '선언 후보'))
        self.assertEqual(pg.check_report(text, report)[0], 0)
        self.assertEqual((self.source / SERVICE).read_text(), debt)

    def test_f115_old_form_rows_keep_the_released_block_hash(self):
        # 셋째 칸이 없는 번역표 행은 2.26.1 과 블록 해시가 같다(캐시 skip 대조 무변) — 칸을 적으면 해시가 바뀐다.
        rows = [f'PlantUnavailableException  {SERVICE}', f'PlantGoneException\t{SERVICE}']
        text = spec_text([f'update {SERVICE}', f'add {RESPONSE}'], [f'{RESPONSE}::ListBooksResponse {{count: int}}'],
                         exceptions=rows)
        spec = self.root / 'hash.md'

        def block_hash(scripts, body):
            spec.write_text(body)
            run = subprocess.run([sys.executable, '-B', str(scripts / 'design_pregate.py'), str(spec), str(self.source),
                                  '--block-hash'], capture_output=True, text=True, env=self.env)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            return run.stdout.splitlines()[0]

        self.assertEqual(block_hash(SCRIPTS, text), block_hash(self.released_2261(), text))
        self.assertNotEqual(block_hash(SCRIPTS, text.replace(rows[0], rows[0] + '  <= PlantUnreadable')), block_hash(SCRIPTS, text))

    def test_f115_stale_source_cell_without_as_is_only_a_row_memo(self):
        # K8 — 출처 칸이 `as` 없이 남은 채 구현이 잡은 값을 쓰면 예보는 서지 않고(자기 신고 칸) 메모만 남는다 — G2 가 잡는다.
        self.garden_fixture()
        text = spec_text([f'update {SERVICE}'], exceptions=[f'PlantUnavailableException  {SERVICE}  <= PlantUnreadable'])
        run, report = self.cli(text)
        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
        self.assertIn('- (없음)', pg._subsection(report, '선언 확정'))
        self.assertIn('채널 메모: S5 입구 catch 확인(출처 칸 `as` 없음 — OHS 는 잡은 도메인 예외 값을 쓰지 않는다(R-3690) · 이 '
                      'catch 가 잡은 값을 쓰면(로그 · 메시지 · `from` · 속성) 출처 칸에 `as` 를 적는다 — #474): '
                      f'PlantUnavailableException ← PlantUnreadable · {SERVICE}', report)
        self.assertEqual(pg.check_report(text, report)[0], 0)
        self.write(self.source, SERVICE, CATCHING.replace('    except PlantUnreadable:\n',
                                                          '    except PlantUnreadable as unreadable:\n        print(unreadable)\n'))
        result = subprocess.run([sys.executable, str(SCRIPTS / 'check-api-error-controller-contract.py'), str(self.source),
                                 '--error-profile', 'auto'], capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(f'[#474] {SERVICE}:', result.stdout)


# 숨김 뺀 기준선 바로 앞 배포판(dddjango 2.24.2) — «지금 판과 같은 결과» 대조의 옛 판(HEAD 금지).
_RELEASED_2242_COMMIT = "2119e502"


class SnapshotLinkPregateTest(unittest.TestCase):
    """F4-97(2.23.1) — 격리 사본의 링크: 숨김 경로(문서 입력 제외)의 사본 밖 링크는 걷고 예보하며, 그 밖은 계획 스텁을
    쓰기 전에 이름 붙은 실행 불능이다. 겹침은 링크를 따라 쓰지 않는다. 2.25.0 — 기준선 · 겹침 · 승인 유입은 숨김 경로를
    빼므로 기록 링크는 사본에 들어오지 않는다(알림 없음 · 결과 같음). 남길 링크가 뺀 경로를 지나면 사본을 쓰기 전에
    지금 경로(전체 · 숨김 건너뛰기 없음)로 정한다."""

    SPEC: Path = ROOT / "workspace/eval/fixtures/pregate/green-spec.md"
    FORM_RED_SPEC: Path = ROOT / "workspace/eval/fixtures/pregate/update-target-spec.md"
    LINK_DIR: str = ".dddjango-web/20261012-0717-x/return1/browser-basetemp-2"
    NOTE: str = "숨김 경로의 사본 밖 심링크"
    SHARED: str = "application/orders/domain_layer/shared_value_object/rates.py"

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="pregate-link-")
        self.addCleanup(self.temp.cleanup)
        self.td = Path(self.temp.name)
        self.outside = self.td / "outside"
        self.outside.mkdir()

    def run_pregate(self, repo: Path, *extra: str, spec: "Path | None" = None,
                    scripts: Path = SCRIPTS) -> "tuple[subprocess.CompletedProcess[str], Path]":
        report = self.td / f"{repo.name}-{'old' if scripts != SCRIPTS else 'new'}-report.md"
        report.write_text("SENTINEL\n", encoding="utf-8")
        env = dict(os.environ)
        env.pop("DJR_FINDINGS_JSON", None)
        run = subprocess.run([sys.executable, str(scripts / "design_pregate.py"), str(spec or self.SPEC), str(repo),
                              "--report", str(report), *extra], capture_output=True, text=True, env=env)
        return run, report

    def released(self) -> Path:
        """2.24.2 배포 커밋의 scripts 사본(HEAD 금지 — 이 고침을 커밋한 뒤에도 옛 판이다)."""
        old = self.td / "released-2242"
        if not old.exists():
            old.mkdir()
            archive = subprocess.run(["git", "-C", str(ROOT), "archive", _RELEASED_2242_COMMIT, "dddjango/scripts"],
                                     capture_output=True, check=True)
            subprocess.run(["tar", "-x", "-C", str(old)], input=archive.stdout, check=True)
        return old / "dddjango" / "scripts"

    @staticmethod
    def verdict(run) -> "list[str]":
        return [line for line in run.stdout.splitlines() if line.startswith(("판정:", "요약:", "형식 red", "  update"))]

    def assert_same_verdict_without_note(self, repo: Path, *extra: str, spec: "Path | None" = None, code: int = 0,
                                         released: bool = False):
        """결과 같음(exit — `released` 면 판정 · 요약 줄까지 2.24.2 와 대조) · 알림 없음(stdout · 리포트)."""
        run, report = self.run_pregate(repo, *extra, spec=spec)
        self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        self.assertNotIn("Traceback", run.stderr)
        self.assertNotIn(self.NOTE, run.stdout)
        self.assertNotIn(self.NOTE, report.read_text(encoding="utf-8"))
        if released:
            old, _old_report = self.run_pregate(repo, *extra, spec=spec, scripts=self.released())
            self.assertEqual((run.returncode, self.verdict(run)), (old.returncode, self.verdict(old)))
        return run, report

    def hidden_shared(self, name: str) -> "tuple[Path, str]":
        """기준선에 숨김 폴더의 실물(`.h/rates.py`) — 숨김 아닌 링크가 그것을 가리키면 되돌림이다."""
        repo = _make_repo(self.td, name)
        (repo / ".h").mkdir()
        (repo / ".h/rates.py").write_text("RATE: int = 3\n", encoding="utf-8")
        return repo, self.commit(repo, "hidden shared module")

    def commit(self, repo: Path, message: str) -> str:
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", message)
        return _git(repo, "rev-parse", "HEAD")

    def assert_named_stop(self, run, report: Path, message: str) -> None:
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertNotIn("Traceback", run.stderr)
        self.assertIn(message, run.stderr)
        self.assertEqual(report.read_text(encoding="utf-8"), "SENTINEL\n")

    def test_L1_committed_record_links_forecast_normally(self) -> None:
        targets = {"abs-dangling": str(self.td / "gone" / "x1"), "abs-live": str(self.outside),
                   "rel-outside": "../../../../../outside-target"}
        for name, target in targets.items():
            with self.subTest(kind=name):
                repo = _make_repo(self.td, "l1-" + name)
                (repo / self.LINK_DIR).mkdir(parents=True)
                os.symlink(target, repo / self.LINK_DIR / "test_xcurrent")
                self.commit(repo, "record link")
                self.assert_same_verdict_without_note(repo, released=name == "abs-live")

    def test_L1c_old_base_holding_the_link(self) -> None:
        repo = _make_repo(self.td, "l1c")
        (repo / self.LINK_DIR).mkdir(parents=True)
        os.symlink(str(self.td / "gone" / "x1"), repo / self.LINK_DIR / "test_xcurrent")
        linked = self.commit(repo, "record link")
        _git(repo, "rm", "-q", f"{self.LINK_DIR}/test_xcurrent")
        self.commit(repo, "record link removed")
        self.assert_same_verdict_without_note(repo, "--base", linked)

    def test_L1d_uncommitted_record_link_and_regular_file_replaced_by_link(self) -> None:
        repo = _make_repo(self.td, "l1d")
        (repo / self.LINK_DIR).mkdir(parents=True)
        os.symlink(str(self.td / "gone" / "x1"), repo / self.LINK_DIR / "test_xcurrent")
        self.assert_same_verdict_without_note(repo)
        replaced = _make_repo(self.td, "l1d-replaced")
        (replaced / ".dddjango-web/x").mkdir(parents=True)
        (replaced / ".dddjango-web/x/current").write_text("regular\n", encoding="utf-8")
        self.commit(replaced, "regular record file")
        (replaced / ".dddjango-web/x/current").unlink()
        os.symlink(str(self.outside / "t.txt"), replaced / ".dddjango-web/x/current")
        self.assert_same_verdict_without_note(replaced)

    def test_L1e_record_link_arriving_by_approved_merge(self) -> None:
        repo = _make_repo(self.td, "l1e")
        base = _git(repo, "branch", "--show-current")
        _git(repo, "checkout", "-q", "-b", "lane")
        (repo / "lane_note.md").write_text("note\n", encoding="utf-8")
        before = self.commit(repo, "lane work")
        _git(repo, "checkout", "-q", base)
        (repo / self.LINK_DIR).mkdir(parents=True)
        os.symlink(str(self.td / "gone" / "x1"), repo / self.LINK_DIR / "test_xcurrent")
        self.commit(repo, "main: record link")
        _git(repo, "checkout", "-q", "lane")
        _git(repo, "merge", "-q", "--no-ff", "-m", "M merge main", base)
        merge = _git(repo, "rev-parse", "HEAD")
        approved = self.td / "l1e-approved.txt"
        approved.write_text(f"{merge} M\n", encoding="utf-8")
        self.assert_same_verdict_without_note(repo, "--base", before, "--approved-merge-file", str(approved))
        self.assert_same_verdict_without_note(repo)

    def test_L2_surface_links_stop_by_name_before_any_write(self) -> None:
        repo = _make_repo(self.td, "l2-committed")
        os.symlink(str(self.outside / "x.py"), repo / "application/orders/x.py")
        self.commit(repo, "surface link")
        run, report = self.run_pregate(repo)
        self.assert_named_stop(run, report, "트리의 심링크 application/orders/x.py 가 사본 밖을 가리킨다(절대 경로)")
        through = _make_repo(self.td, "l2-through")
        os.symlink(str(self.outside), through / ".x")
        os.symlink("../../.x/y.py", through / "application/orders/y.py")
        self.commit(through, "surface link through a hidden link")
        run, report = self.run_pregate(through)
        self.assert_named_stop(run, report, "트리의 심링크 application/orders/y.py 가 사본 밖을 가리킨다(저장소 밖 상대 경로)")
        order = _make_repo(self.td, "l2-order")
        (order / "zz").mkdir()
        os.symlink(str(self.outside), order / "zz/.x")
        os.symlink("../../zz/.x/y.py", order / "application/orders/y.py")
        self.commit(order, "surface link extracted before the hidden link")
        run, report = self.run_pregate(order)
        self.assert_named_stop(run, report, "격리 사본에 사본 밖을 가리키는 심링크 application/orders/y.py(기준선)")

    def test_L2b_uncommitted_and_inflow_surface_links_write_nothing_outside(self) -> None:
        billing = self.td / "outside-billing"
        billing.mkdir()
        repo = _make_repo(self.td, "l2b")
        os.symlink(str(billing), repo / "application/billing")
        run, report = self.run_pregate(repo)
        self.assert_named_stop(run, report, "격리 사본에 사본 밖을 가리키는 심링크 application/billing(미커밋 작업 트리)")
        self.assertEqual(sorted(billing.rglob("*")), [])
        replaced = _make_repo(self.td, "l2b-replaced")
        (replaced / "application/orders/x.py").write_text("X = 1\n", encoding="utf-8")
        self.commit(replaced, "regular file")
        (replaced / "application/orders/x.py").unlink()
        os.symlink(str(self.outside / "t.txt"), replaced / "application/orders/x.py")
        run, report = self.run_pregate(replaced)
        self.assert_named_stop(run, report, "격리 사본에 사본 밖을 가리키는 심링크 application/orders/x.py(미커밋 작업 트리)")
        inflow_out = self.td / "outside-inflow"
        inflow_out.mkdir()
        lane = _make_repo(self.td, "l2b-inflow")
        base = _git(lane, "branch", "--show-current")
        _git(lane, "checkout", "-q", "-b", "lane")
        (lane / "lane_note.md").write_text("note\n", encoding="utf-8")
        before = self.commit(lane, "lane work")
        _git(lane, "checkout", "-q", base)
        os.symlink(str(inflow_out), lane / "application/billing")
        self.commit(lane, "main: billing link")
        _git(lane, "checkout", "-q", "lane")
        _git(lane, "merge", "-q", "--no-ff", "-m", "M merge main", base)
        approved = self.td / "l2b-approved.txt"
        approved.write_text(f"{_git(lane, 'rev-parse', 'HEAD')} M\n", encoding="utf-8")
        run, report = self.run_pregate(lane, "--base", before, "--approved-merge-file", str(approved))
        self.assert_named_stop(run, report, "격리 사본에 사본 밖을 가리키는 심링크 application/billing(승인 유입)")
        self.assertEqual(sorted(inflow_out.rglob("*")), [])

    def test_overlay_never_writes_through_a_destination_link(self) -> None:
        repo = _make_repo(self.td, "overlay-in-copy")
        (repo / "application/orders/b.py").write_text("B = 1\n", encoding="utf-8")
        os.symlink("b.py", repo / "application/orders/a.py")
        self.commit(repo, "in-copy link a -> b")
        (repo / "application/orders/a.py").unlink()
        (repo / "application/orders/a.py").write_text("A = 2\n", encoding="utf-8")
        run, _report = self.run_pregate(repo, "--keep")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        kept = Path(run.stdout.rsplit("격리 사본 보존: ", 1)[1].splitlines()[0])
        self.addCleanup(shutil.rmtree, kept, True)
        self.assertFalse((kept / "copy/application/orders/a.py").is_symlink())
        self.assertEqual((kept / "copy/application/orders/a.py").read_text(encoding="utf-8"), "A = 2\n")
        self.assertEqual((kept / "copy/application/orders/b.py").read_text(encoding="utf-8"), "B = 1\n")
        target = self.outside / "record.txt"
        target.write_text("OUTSIDE-ORIGINAL\n", encoding="utf-8")
        hidden = _make_repo(self.td, "overlay-hidden")
        (hidden / ".dddjango-web/x").mkdir(parents=True)
        os.symlink(str(target), hidden / ".dddjango-web/x/out.txt")
        self.commit(hidden, "record link to an outside file")
        (hidden / ".dddjango-web/x/out.txt").unlink()
        (hidden / ".dddjango-web/x/out.txt").write_text("LANE-REGULAR\n", encoding="utf-8")
        run, _report = self.run_pregate(hidden)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), "OUTSIDE-ORIGINAL\n")
        # 커밋된 사본 안 폴더 링크 lnk -> real_dir — (가) 작업 트리에서 진짜 폴더로 바꿈: 링크를 지우고 폴더를 겹친다.
        dir_repo = self.inside_dir_link("overlay-dir")
        orders = dir_repo / "application/orders"
        (orders / "lnk").unlink()
        (orders / "lnk").mkdir()
        (orders / "lnk/new.txt").write_text("NEW\n", encoding="utf-8")
        run, _report = self.run_pregate(dir_repo, "--keep")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        kept = Path(run.stdout.rsplit("격리 사본 보존: ", 1)[1].splitlines()[0])
        self.addCleanup(shutil.rmtree, kept, True)
        self.assertFalse((kept / "copy/application/orders/lnk").is_symlink())
        self.assertEqual((kept / "copy/application/orders/lnk/new.txt").read_text(encoding="utf-8"), "NEW\n")
        self.assertFalse((kept / "copy/application/orders/real_dir/new.txt").exists())
        # (나) git mv 로 링크를 옮기고 옛 이름에 새 폴더를 들임: 링크가 조상인 자리에는 쓰지 않고 이름 붙여 멈춘다.
        moved = self.inside_dir_link("overlay-moved")
        _git(moved, "mv", "application/orders/lnk", "application/orders/lnk2")
        (moved / "application/orders/lnk").mkdir()
        (moved / "application/orders/lnk/new.txt").write_text("NEW\n", encoding="utf-8")
        _git(moved, "add", "application/orders/lnk/new.txt")
        run, report = self.run_pregate(moved)
        self.assert_named_stop(run, report, "미커밋 작업 트리 경로의 조상이 symlink 다(링크를 따라 쓸 위험): "
                                            "application/orders/lnk/new.txt")

    def inside_dir_link(self, name: str) -> Path:
        repo = _make_repo(self.td, name)
        orders = repo / "application/orders"
        (orders / "real_dir").mkdir()
        (orders / "real_dir/keep.txt").write_text("keep\n", encoding="utf-8")
        os.symlink("real_dir", orders / "lnk")
        self.commit(repo, "in-copy directory link")
        return repo

    def test_L1f_form_red_report_still_names_removed_links(self) -> None:
        repo = _make_repo(self.td, "l1f")
        (repo / self.LINK_DIR).mkdir(parents=True)
        os.symlink(str(self.td / "gone" / "x1"), repo / self.LINK_DIR / "test_xcurrent")
        self.commit(repo, "record link")
        self.assert_same_verdict_without_note(repo, spec=self.FORM_RED_SPEC, code=3)

    def test_P1_uncommitted_surface_link_into_a_hidden_baseline_folder_extracts_everything(self) -> None:
        repo, _base = self.hidden_shared("p1")
        os.symlink("../../../../.h/rates.py", repo / self.SHARED)
        run, _report = self.assert_same_verdict_without_note(repo, released=True)
        self.assertNotIn("실행 불능", run.stderr)

    def test_P2_inflow_surface_link_into_a_hidden_baseline_folder_extracts_everything(self) -> None:
        repo, _base = self.hidden_shared("p2")
        base = _git(repo, "branch", "--show-current")
        _git(repo, "checkout", "-q", "-b", "lane")
        (repo / "lane_note.md").write_text("note\n", encoding="utf-8")
        before = self.commit(repo, "lane work")
        _git(repo, "checkout", "-q", base)
        os.symlink("../../../../.h/rates.py", repo / self.SHARED)
        self.commit(repo, "main: surface link into the hidden folder")
        _git(repo, "checkout", "-q", "lane")
        _git(repo, "merge", "-q", "--no-ff", "-m", "M merge main", base)
        approved = self.td / "p2-approved.txt"
        approved.write_text(f"{_git(repo, 'rev-parse', 'HEAD')} M\n", encoding="utf-8")
        run, _report = self.assert_same_verdict_without_note(repo, "--base", before, "--approved-merge-file", str(approved),
                                                             released=True)
        self.assertIn("승인 유입: 1경로(추가 1", run.stdout)

    def test_P3_form_red_run_takes_the_same_decision_as_a_full_run(self) -> None:
        """되돌림은 사본을 쓰기 전에 정한다 — 겹침 링크만 걸고 형식 red 로 끝나는 실행도 지금 판과 글자까지 같다
        (전체를 풀어 기록 링크를 걷었다는 알림까지)."""
        repo, _base = self.hidden_shared("p3")
        (repo / self.LINK_DIR).mkdir(parents=True)
        os.symlink(str(self.td / "gone" / "x1"), repo / self.LINK_DIR / "test_xcurrent")
        self.commit(repo, "record link")
        os.symlink("../../../../.h/rates.py", repo / self.SHARED)
        run, report = self.run_pregate(repo, spec=self.FORM_RED_SPEC)
        old, old_report = self.run_pregate(repo, spec=self.FORM_RED_SPEC, scripts=self.released())
        self.assertEqual(run.returncode, 3, run.stdout + run.stderr)
        self.assertEqual((run.returncode, run.stdout, run.stderr), (old.returncode, old.stdout, old.stderr))
        self.assertIn(f"{self.NOTE} 1개는 사본에서 뺐다(사본 밖 내용을 읽지 않게 · 판정 무관): {self.LINK_DIR}/test_xcurrent",
                      run.stdout)

    def test_P5_folders_holding_only_hidden_entries_forecast_like_released_and_like_g2(self) -> None:
        """숨김 항목만 든 숨김 아닌 폴더(`config/logs/.gitkeep` · 비계만 만든 BC · 숨김 폴더만 든 폴더) — pre-gate 예보와
        G2(registry_gate) 판정이 모두 2.24.2 와 같고, 예보 귀속 0 = G2 귀속 0 이다."""
        repo = _make_repo(self.td, "p5")
        for rel, body in (("config/logs/.gitkeep", ""), ("application/payments/.gitkeep", ""),
                          ("application/orders/notes/.cache/f", "cache\n"), (".dddjango-web/r/log.txt", "log\n")):
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_text(body, encoding="utf-8")
        self.commit(repo, "dot-only folders + record")
        (repo / "notes.txt").write_text("lane\n", encoding="utf-8")
        run, _report = self.assert_same_verdict_without_note(repo, released=True)
        self.assertIn("예보 green", run.stdout)
        env = dict(os.environ)
        env.pop("DJR_FINDINGS_JSON", None)
        gates = {}
        for side, scripts in (("new", SCRIPTS), ("old", self.released())):
            gate = subprocess.run([sys.executable, str(scripts / "registry_gate.py"), str(repo), "--anchor", "HEAD"],
                                  capture_output=True, text=True, env=env)
            gates[side] = (gate.returncode, [line for line in gate.stdout.splitlines() if line.startswith("판정:")],
                           [line for line in gate.stdout.splitlines() if " :: [#" in line and line.startswith("  ")
                            and gate.stdout.index(line) < gate.stdout.index("== legacy")])
        self.assertEqual(gates["new"], gates["old"])
        self.assertEqual(gates["new"][0], 0, gates)

    def test_P8_folders_holding_only_hidden_folders_forecast_like_released_and_like_g2(self) -> None:
        """숨김 «폴더» 만 든 숨김 아닌 폴더(BC 뿌리 · 층 폴더)는 숨김을 빼면 pre-gate 사본에서 통째로 사라진다(사본을 커밋하므로
        빈 폴더가 남지 않는다) — 그런 폴더가 최종 사본(기준선 + 승인 유입 + 겹침)에 하나라도 생기면 그 실행은 전체 모드다.
        pre-gate 예보 = G2(registry_gate) = 2.24.2."""
        env = dict(os.environ)
        env.pop("DJR_FINDINGS_JSON", None)
        cases = {"bc": ("application/billing/.cache/x", None),
                 "layer": ("application/billing/domain_layer/shared_value_object/.cache/x", None),
                 "emptied": ("application/billing/.cache/x", "application/billing/keep.py")}
        for name, (hidden, deleted) in cases.items():
            with self.subTest(case=name):
                repo = _make_repo(self.td, "p8-" + name)
                for rel in (hidden, deleted):
                    if rel is not None:
                        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
                        (repo / rel).write_text("x\n", encoding="utf-8")
                self.commit(repo, "folder holding only a hidden folder")
                if deleted is not None:
                    (repo / deleted).unlink()        # 작업 트리에서 지움 — 겹침 뒤 최종 사본에서 그 폴더에는 숨김 폴더만 남는다
                (repo / "notes.txt").write_text("lane\n", encoding="utf-8")
                run, _report = self.assert_same_verdict_without_note(repo, released=True, code=2)
                self.assertIn("예보 red", run.stdout)
                gates = {}
                for side, scripts in (("new", SCRIPTS), ("old", self.released())):
                    gate = subprocess.run([sys.executable, str(scripts / "registry_gate.py"), str(repo), "--anchor", "HEAD"],
                                          capture_output=True, text=True, env=env)
                    gates[side] = (gate.returncode, [line for line in gate.stdout.splitlines() if line.startswith("판정:")])
                self.assertEqual(gates["new"], gates["old"])

    def test_P6_split_extraction_failure_falls_back_to_the_full_baseline(self) -> None:
        """NFD 로 커밋된 문서 입력 이름은 `:(literal)` 이 맞지 않는다(macOS git 의 argv NFC 바꿈) — 숨김 뺀 기준선 풀기가
        실패하면 사본을 비우고 지금처럼 전체를 푼다(실행 불능이 아니라 2.24.2 와 같은 예보)."""
        import unicodedata
        repo = _make_repo(self.td, "p6")
        (repo / ".dddjango-web/r").mkdir(parents=True)
        (repo / ".dddjango-web/r/log.txt").write_text("log\n", encoding="utf-8")
        self.commit(repo, "record")
        blob = subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"], input=b"# scope\n",
                              capture_output=True, check=True).stdout.decode("ascii").strip()
        subprocess.run(["git", "-C", str(repo), "-c", "core.precomposeunicode=false", "update-index", "--add", "--cacheinfo",
                        f"100644,{blob},{unicodedata.normalize('NFD', '.dddjango/결제/scope.md')}"],
                       capture_output=True, check=True)
        _git(repo, "commit", "-q", "-m", "nfd document input")
        _git(repo, "reset", "-q", "--hard")
        run, _report = self.assert_same_verdict_without_note(repo, released=True)
        self.assertNotIn("실행 불능", run.stderr)

    def test_P7_failures_keep_the_released_order(self) -> None:
        """사본을 쓰기 전에 승인 유입 · 겹칠 경로를 먼저 읽어도, 그 실패(`git diff-tree` · `git status`)는 2.24.2 와 같은
        자리에서 이름 붙는다 — 기준선 풀기 실패가 먼저면 그것이 먼저 나온다(stderr 글자까지 같음)."""
        outside = self.td / "outside-p7"
        outside.mkdir()
        repo = _make_repo(self.td, "p7")
        os.symlink(str(outside / "x.py"), repo / "application/orders/x.py")
        self.commit(repo, "surface link outside")
        base = _git(repo, "branch", "--show-current")
        _git(repo, "checkout", "-q", "-b", "lane")
        (repo / "lane_note.md").write_text("note\n", encoding="utf-8")
        before = self.commit(repo, "lane work")
        _git(repo, "checkout", "-q", base)
        (repo / "docs").mkdir()
        (repo / "docs/up.md").write_text("up\n", encoding="utf-8")
        self.commit(repo, "main change")
        _git(repo, "checkout", "-q", "lane")
        _git(repo, "merge", "-q", "--no-ff", "-m", "M merge main", base)
        approved = self.td / "p7-approved.txt"
        approved.write_text(f"{_git(repo, 'rev-parse', 'HEAD')} M\n", encoding="utf-8")
        runs = {}
        for name, word, extra in (("inflow", "diff-tree", ["--base", before, "--approved-merge-file", str(approved)]),
                                  ("status", "status", [])):
            shim = self.td / f"p7-shim-{name}"
            shim.mkdir()
            (shim / "git").write_text(f'#!/bin/bash\nfor a in "$@"; do if [ "$a" = "{word}" ]; then '
                                      f'echo "fatal: simulated {word} failure" >&2; exit 128; fi; done\n'
                                      'exec /usr/bin/git "$@"\n', encoding="utf-8")
            (shim / "git").chmod(0o755)
            env = dict(os.environ, PATH=f"{shim}:{os.environ.get('PATH', '')}")
            env.pop("DJR_FINDINGS_JSON", None)
            for side, scripts in (("new", SCRIPTS), ("old", self.released())):
                report = self.td / f"p7-{side}-{name}.md"
                run = subprocess.run([sys.executable, str(scripts / "design_pregate.py"), str(self.SPEC), str(repo),
                                      "--report", str(report), *extra], capture_output=True, text=True, env=env)
                runs[(side, name)] = (run.returncode, run.stderr)
        for name in ("inflow", "status"):
            self.assertEqual(runs[("new", name)], runs[("old", name)])
            self.assertEqual(runs[("new", name)][0], 1)
            self.assertIn("트리의 심링크 application/orders/x.py 가 사본 밖을 가리킨다(절대 경로)", runs[("new", name)][1])

    def test_P4_hidden_worktree_changes_and_inflow_stay_out_of_the_copy(self) -> None:
        repo = _make_repo(self.td, "p4")
        base = _git(repo, "branch", "--show-current")
        _git(repo, "checkout", "-q", "-b", "lane")
        (repo / "lane_note.md").write_text("note\n", encoding="utf-8")
        before = self.commit(repo, "lane work")
        _git(repo, "checkout", "-q", base)
        (repo / ".dddjango-web/r").mkdir(parents=True)
        (repo / ".dddjango-web/r/merged.txt").write_text("record\n", encoding="utf-8")
        (repo / "docs").mkdir()
        (repo / "docs/merged.md").write_text("doc\n", encoding="utf-8")
        self.commit(repo, "main: record + doc")
        _git(repo, "checkout", "-q", "lane")
        _git(repo, "merge", "-q", "--no-ff", "-m", "M merge main", base)
        approved = self.td / "p4-approved.txt"
        approved.write_text(f"{_git(repo, 'rev-parse', 'HEAD')} M\n", encoding="utf-8")
        run, report = self.run_pregate(repo, "--base", before, "--approved-merge-file", str(approved), "--keep")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        kept = Path(run.stdout.rsplit("격리 사본 보존: ", 1)[1].splitlines()[0])
        self.addCleanup(shutil.rmtree, kept, True)
        self.assertIn("승인 유입: 1경로(추가 1 · 수정 0 · 삭제 0)", run.stdout)
        self.assertIn("승인 유입: 1경로(추가 1 · 수정 0 · 삭제 0)", report.read_text(encoding="utf-8"))
        self.assertTrue((kept / "copy/docs/merged.md").is_file())
        self.assertFalse(os.path.lexists(kept / "copy/.dddjango-web"))
        (repo / ".dddjango-web/r/worktree.txt").write_text("lane record\n", encoding="utf-8")
        (repo / ".dddjango-web/r/merged.txt").write_text("lane edit\n", encoding="utf-8")
        (repo / "docs/worktree.md").write_text("lane doc\n", encoding="utf-8")
        run, _report = self.run_pregate(repo, "--keep")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        kept = Path(run.stdout.rsplit("격리 사본 보존: ", 1)[1].splitlines()[0])
        self.addCleanup(shutil.rmtree, kept, True)
        self.assertTrue((kept / "copy/docs/worktree.md").is_file())
        self.assertFalse(os.path.lexists(kept / "copy/.dddjango-web"))
        self.assertIn("dirty overlay 1건", run.stdout)

_SAVED_TMPDIR: "list[str | None]" = []


def setUpModule() -> None:
    """이 시험 파일 전체를 전용 임시 폴더(TMPDIR)에서 돈다 — pre-gate · 게이트의 시작 때 쓸기가 실제 임시 폴더의 다른
    실행 사본을 건드리지 않게."""
    _SAVED_TMPDIR.append(os.environ.get("TMPDIR"))
    private = tempfile.mkdtemp(prefix="pregate-smoke-tmp-")
    os.environ["TMPDIR"] = private
    tempfile.tempdir = private


def tearDownModule() -> None:
    private = tempfile.tempdir
    tempfile.tempdir = None
    saved = _SAVED_TMPDIR.pop()
    if saved is None:
        os.environ.pop("TMPDIR", None)
    else:
        os.environ["TMPDIR"] = saved
    if private:
        shutil.rmtree(private, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
