#!/usr/bin/env python3
"""현장 F4/F7/F8 회귀: 골격·의미 후보·앵커 전체 수집의 반대 대조를 고정한다."""
from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import json
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
isolation = _load_module(SCRIPTS / "check-context-isolation.py", "field_isolation")
domain = _load_module(SCRIPTS / "check-domain-model.py", "field_domain")
pairing = _load_module(SCRIPTS / "check-port-adapter-pairing.py", "field_pairing")
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

    def ohs_rules(self, source):
        self.write("application/lesson/application_layer/books/read/read_use_case.py", "class ReadUseCase: pass\n")
        self.write("application/lesson/composition_root/books.py", "from application.lesson.application_layer.books.read.read_use_case import ReadUseCase\ndef build_read_use_case() -> ReadUseCase: return ReadUseCase()\n")
        py = self.write("application/lesson/driving_layer/ohs/library/library_service.py", source)
        f, c = isolation.Findings(defer=True), isolation.Candidates(defer=True)
        isolation._check_ohs_service(py, str(py.relative_to(self.root)), f, c)
        return [e.rule for e in f.entries], [e.rule for e in c.entries]

    def test_ohs_execution_provenance_and_count(self):
        header = "from application.lesson.composition_root.books import build_read_use_case as prepare\n"
        cases = [
            ("unit = prepare()\n    unit.execute()", False),
            ("prepare().execute()", False),
            ("unit = prepare()\n    alias = unit\n    alias.execute()", False),
            ("unit = prepare()", True),
            ("unit = prepare()\n    unit.execute()\n    unit.execute()", True),
            ("cursor.execute()", True),
            ("unit = prepare()\n    for item in items:\n        unit.execute()", True),
            ("unit = prepare()\n    values = [unit.execute() for item in items]", True),
            ("unit = prepare()\n    unit = cursor\n    unit.execute()", True),
            ("unit = prepare()\n    if condition:\n        unit = cursor\n    unit.execute()", True),
            ("unit = prepare()\n    if condition:\n        unit = cursor\n    else:\n        unit = prepare()\n    unit.execute()", True),
            ("unit = prepare()\n    def unused():\n        unit.execute()", True),
            ("unit = prepare()\n    def unused():\n        unit.execute()\n    unit.execute()", False),
            ("unit = prepare()\n    class Unused:\n        def run(self): unit.execute()\n    unit.execute()", False),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                self.assertEqual("#153" in self.ohs_rules(header + "def read_query(request):\n    " + body + "\n")[1], expected)
        for header, expression in [
            ("import application.lesson.composition_root.books as wiring", "wiring.build_read_use_case().execute()"),
            ("from application.lesson.application_layer.books.read.read_use_case import ReadUseCase as Unit", "Unit().execute()"),
        ]:
            self.assertNotIn("#153", self.ohs_rules(header + "\ndef read_query(request):\n    " + expression + "\n")[1])
        self.assertNotIn("#153", self.ohs_rules("from application.lesson.application_layer.books.read.read_use_case import ReadUseCase as Unit\ndef read_query(request: Unit):\n    request.execute()\n")[1])
        for symbol in ("build_missing_use_case", "unrelated"):
            self.assertIn("#153", self.ohs_rules(f"from application.lesson.composition_root.books import {symbol}\ndef read_query(request):\n    {symbol}().execute()\n")[1])
        found, _ = self.ohs_rules("from application.lesson.domain_layer.book.error import BookError\ndef read_query(request):\n    try: work()\n    except BookError as exc: return exc.code\n")
        self.assertIn("#153", found)

    def enum_rules(self, source):
        py = self.write("application/lesson/domain_layer/book/value_object/kind.py", source)
        f, c = domain.Findings(defer=True), domain.Candidates(defer=True)
        domain._check_value_object_file(self.root, py, f, c)
        return [e.rule for e in f.entries], [e.rule for e in c.entries]

    def test_open_enum_reason_does_not_claim_constructor_raise_is_absent(self):
        for source, expected in (
            ("from enum import Enum\nclass Kind(Enum):\n    ONE = 1\n    def __init__(self, value):\n        if value < 0: raise ValueError()\n", "닫힌 표준 Enum 생성 검증을 확정할 수 없다"),
            ("class Kind:\n    value: str\n", "__init__/__post_init__ 에 raise 가 없다"),
        ):
            with self.subTest(source=source):
                self.write("application/lesson/domain_layer/book/value_object/kind.py", source)
                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "check-domain-model.py"), str(self.root)],
                                        capture_output=True, text=True, env=self.env)
                reasons = [line for line in (result.stdout + result.stderr).splitlines() if "[ⓓ#268]" in line]
                self.assertEqual(len(reasons), 1, result.stdout + result.stderr)
                self.assertIn(expected, reasons[0])
                if "Enum" in source:
                    self.assertNotIn("raise 가 없다", reasons[0])

    def test_closed_enum_validation_and_dynamic_opposites(self):
        for header, base in [("from enum import Enum", "Enum"), ("from enum import StrEnum as Closed", "Closed"), ("import enum as standard", "standard.IntEnum")]:
            with self.subTest(base=base):
                self.assertNotIn("#268", self.enum_rules(header + f"\nclass Kind({base}):\n    ONE = 1\n")[1])
        variants = [
            "from enum import Flag\nclass Kind(Flag):\n    ONE = 1",
            "from enum import IntFlag\nclass Kind(IntFlag):\n    ONE = 1",
            "from custom import Enum\nclass Kind(Enum):\n    ONE = 1",
            "from enum import Enum\nEnum = other\nclass Kind(Enum):\n    ONE = 1",
            "from enum import Enum\nclass Kind(Enum, metaclass=Meta):\n    ONE = 1",
            "from enum import Enum\nclass Kind(Mixin, Enum):\n    ONE = 1",
            "from enum import Enum\nclass Kind(Enum):\n    ONE = dynamic()",
            "from enum import Enum\nclass Kind(Enum):\n    ONE = 1\nKind._missing_ = classmethod(missing)",
            "from enum import Enum\nclass Kind(Enum):\n    ONE = 1\nAlias = Kind\nAlias._missing_ = classmethod(missing)",
        ]
        for method in ("_missing_", "__new__", "__init__", "__call__"):
            variants.append(f"from enum import Enum\nclass Kind(Enum):\n    ONE = 1\n    def {method}(self, value): return value")
        for source in variants:
            with self.subTest(source=source):
                self.assertIn("#268", self.enum_rules(source)[1])
        f, c = self.enum_rules("from enum import Enum\nclass Kind(Enum):\n    ONE = 1\n    id: int\n    def mutate(self): self.code = 2\n")
        self.assertIn("#264", f)
        self.assertIn("#259", c)

    def application_rules(self, body, header="", parameters="uow: Work"):
        source = ("from application.lesson.application_layer.port.unit_of_work.lesson_unit_of_work import LessonUnitOfWork as Work\n"
                  "from django.db import transaction\n" + header + "\ndef run(" + parameters + ", books: BookRepository, loans: LoanRepository):\n    " + body + "\n")
        self.write("application/lesson/application_layer/books/run/run_use_case.py", source)
        self.write("application/lesson/application_layer/port/unit_of_work/lesson_unit_of_work.py", "class LessonUnitOfWork: pass\n")
        f, c = domain.Findings(defer=True), domain.Candidates(defer=True)
        domain._check_application_side(self.root, self.root / "application/lesson", f, c)
        return [e.rule for e in f.entries], [e.rule for e in c.entries]

    def test_uow_lexical_regions_and_unknown_boundaries(self):
        cases = [
            ("with uow:\n        books.save(a)\n    with uow:\n        loans.save(b)", None),
            ("alias = uow\n    with alias:\n        books.save(a)\n    with alias:\n        loans.save(b)", None),
            ("with uow:\n        books.save(a)\n        loans.save(b)", "violation"),
            ("with uow:\n        books.save(a)\n        with uow:\n            loans.save(b)", "violation"),
            ("with uow, uow:\n        books.save(a)\n        loans.save(b)", "violation"),
            ("with transaction.atomic():\n        with uow:\n            books.save(a)\n        with uow:\n            loans.save(b)", "violation"),
            ("with lock:\n        books.save(a)\n    with lock:\n        loans.save(b)", "candidate"),
            ("books.save(a)\n    loans.save(b)", "candidate"),
            ("with mystery():\n        with uow:\n            books.save(a)\n        with uow:\n            loans.save(b)", "candidate"),
            ("transaction.begin()\n    with uow:\n        books.save(a)\n    with uow:\n        loans.save(b)", "candidate"),
            ("uow = dynamic()\n    with uow:\n        books.save(a)\n        loans.save(b)", "candidate"),
            ("if flag:\n        uow = dynamic()\n    else:\n        uow = Work()\n    with uow:\n        books.save(a)\n        loans.save(b)", "candidate"),
            ("with uow:\n        books.save(a)\n        def unused():\n            loans.save(b)", None),
            ("with uow:\n        books.save(a)\n        books.remove(b)", None),
            ("with make() as active:\n        books.save(a)\n    with make() as active:\n        loans.save(b)", None),
            ("with make() as active:\n        books.save(a)\n    with active:\n        loans.save(b)", "candidate"),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                f, c = self.application_rules(body, "def make() -> Work: return Work()\n")
                self.assertEqual("#546" in f, expected == "violation")
                self.assertEqual("#546" in c, expected == "candidate")
        f, c = self.application_rules("with uow:\n        books.save(a)\n    with uow:\n        loans.save(b)", "@transaction.atomic")
        self.assertIn("#546", f)
        f, c = self.application_rules("with uow:\n        items = books.list_all()\n        books.save_all(items)\n        root = books.get_one()\n        root.child.change()")
        self.assertIn("#550", f)
        self.assertIn("#257", f)

    def property_rules(self, source):
        self.write("application/lesson/domain_layer/book/kind.py", "class Kind: code: str\nclass Rejected(Exception): code: str\n")
        self.write("application/lesson/application_layer/port/books/response.py", "class BookResponse: status_code: str\n")
        self.write("application/lesson/application_layer/port/books/export.py", "from requests import Response as BookResponse\n")
        self.write("application/lesson/application_layer/port/books/reexport.py", "from .response import BookResponse\n")
        self.write("application/lesson/application_layer/port/books/cycle.py", "from .cycle import BookResponse\n")
        self.write("application/lesson/application_layer/books/read/read_use_case.py", source)
        f, c = pairing.Findings(defer=True), pairing.Candidates(defer=True)
        pairing._check_use_side(self.root, self.root / "application/lesson", set(), f, c)
        return [e.rule for e in f.entries], [e.rule for e in c.entries]

    def test_property_comparisons_use_actual_origin_on_both_sides(self):
        cases = [
            ("from application.lesson.domain_layer.book.kind import Kind as Value\ndef run(value: Value): return value.code == 'x'", None),
            ("from application.lesson.domain_layer.book.kind import Kind\ndef run():\n    value = Kind()\n    alias = value\n    return 'x' == alias.code", None),
            ("from application.lesson.application_layer.port.books.reexport import BookResponse\ndef run(value: BookResponse): return 200 == value.status_code", None),
            ("from application.lesson.application_layer.port.books.export import BookResponse\ndef run(value: BookResponse): return 200 == value.status_code", "violation"),
            ("from application.lesson.application_layer.port.books.missing import Response\ndef run(value: Response): return value.code == 1", "candidate"),
            ("from application.lesson.application_layer.port.books.cycle import BookResponse\ndef run(value: BookResponse): return value.code == 1", "candidate"),
            ("from django.db import IntegrityError as Failure\ndef run(error: Failure): return 1 == error.errno", "violation"),
            ("import httpx as http\ndef run(response: http.Response): return 200 == response.status_code == 200", "violation"),
            ("from requests import Response\ndef run():\n    response = Response()\n    return 200 == response.status_code", "violation"),
            ("def run(value): return value.code == 'x'", "candidate"),
            ("def run():\n    value = fetch()\n    return 'x' == value.code", "candidate"),
            ("from application.lesson.domain_layer.book.kind import Kind\ndef run(value: Kind):\n    value = fetch()\n    return value.code == 1", "candidate"),
            ("from application.lesson.domain_layer.book.kind import Kind\ndef run(value: Kind):\n    if flag: value = fetch()\n    else: value = Kind()\n    return value.code == 1", "candidate"),
            ("from vendor import WhateverError\ndef run():\n    try: fetch()\n    except WhateverError as error: return error.code == 1", "candidate"),
            ("from application.lesson.domain_layer.book.kind import Rejected\ndef run():\n    try: fetch()\n    except Rejected as error: return error.code == 1", None),
            ("from django.db.utils import IntegrityError\ndef run():\n    try: fetch()\n    except IntegrityError as error: return 1 == error.errno", "violation"),
            ("from django.db import IntegrityError\nfrom application.lesson.domain_layer.book.kind import Rejected\ndef run():\n    try: fetch()\n    except (Rejected, IntegrityError) as error: return error.code == 1", "candidate"),
            ("from requests import Response\nResponse = custom\ndef run(value: Response): return value.status_code == 1", "candidate"),
            ("from unrelated import Response\ndef run(value: Response): return value.status_code == 1", "candidate"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                f, c = self.property_rules(source)
                self.assertEqual(f.count("#557"), int(expected == "violation"))
                self.assertEqual(c.count("#557"), int(expected == "candidate"))
        f, c = self.property_rules("from requests import Response\ndef first():\n    value = Response()\n    return value.status_code == value.status_code\ndef second(value): return value.status_code == 1")
        self.assertEqual(f.count("#557"), 1)
        self.assertEqual(c.count("#557"), 1)

    def test_origin_scope_rebindings_remain_unknown(self):
        sources = [
            "from requests import Response\ndef run(value: Response): return value.status_code == 1\nResponse = custom",
            "from requests import Response\ndef run():\n    value = Response()\n    value, other = pair()\n    return value.status_code == 1",
        ]
        for source in sources:
            with self.subTest(source=source):
                f, c = self.property_rules(source)
                self.assertNotIn("#557", f)
                self.assertIn("#557", c)
        for source in [
            "import enum\nenum.Enum = custom\nclass Kind(enum.Enum):\n    ONE = 1",
            "from enum import Enum\nclass Kind(Enum):\n    ONE = 1\n    _missing_ = None",
        ]:
            with self.subTest(source=source): self.assertIn("#268", self.enum_rules(source)[1])
        f, c = self.application_rules("with uow:\n        books.save(a)\n    with uow:\n        loans.save(b)", parameters="uow: Missing")
        self.assertNotIn("#546", f)
        self.assertIn("#546", c)

    def test_uow_injected_fields_and_factory_alias_scope(self):
        source = "from application.lesson.application_layer.port.unit_of_work.lesson_unit_of_work import LessonUnitOfWork as Work\nclass Run:\n    def __init__(self, context: Work, books: BookRepository, loans: LoanRepository):\n        self.context = context\n        self.books = books\n        self.loans = loans\n    def execute(self):\n        with self.context:\n            self.books.save(a)\n        with self.context:\n            self.loans.save(b)\n"
        self.application_rules("pass")
        self.write("application/lesson/application_layer/books/run/run_use_case.py", source)
        f, c = domain.Findings(defer=True), domain.Candidates(defer=True)
        domain._check_application_side(self.root, self.root / "application/lesson", f, c)
        self.assertNotIn("#546", [e.rule for e in f.entries + c.entries])
        f, c = self.application_rules("with make() as active:\n        copy = active\n        books.save(a)\n    with copy:\n        loans.save(b)", "def make() -> Work: return Work()")
        self.assertNotIn("#546", f)
        self.assertIn("#546", c)

    def test_declared_usecase_and_enum_constructor_opposites(self):
        self.ohs_rules("def read_query(request): pass")
        self.write("application/lesson/composition_root/books.py", "def build_read_use_case(): return cursor()\n")
        py = self.write("application/lesson/driving_layer/ohs/library/library_service.py", "from application.lesson.composition_root.books import build_read_use_case\ndef read_query(request): build_read_use_case().execute()\n")
        f, c = isolation.Findings(defer=True), isolation.Candidates(defer=True)
        isolation._check_ohs_service(py, str(py), f, c)
        self.assertIn("#153", [e.rule for e in c.entries])
        self.assertIn("#153", self.ohs_rules("from application.lesson.application_layer.books.read.absent_use_case import Missing\ndef read_query(request: Missing): request.execute()\n")[1])

    def test_custom_enum_validation_does_not_prove_closed_members(self):
        self.assertIn("#268", self.enum_rules("from enum import Enum\nclass Kind(Enum):\n    ONE = 1\n    def __init__(self, value):\n        if value < 0: raise ValueError()\n")[1])

    def test_nested_repository_parameters_do_not_retype_outer_bindings(self):
        f, c = self.application_rules("with uow:\n        books.save(a)\n        loans.save(b)\n    def unused(books: LoanRepository): pass")
        self.assertIn("#546", f)

    def test_while_guard_execute_repeats_but_for_iterable_executes_once(self):
        header = "from application.lesson.composition_root.books import build_read_use_case as prepare\n"
        for statement, candidate in [("while unit.execute(): pass", True),
                                     ("for item in unit.execute(): pass", False)]:
            with self.subTest(statement=statement):
                _, c = self.ohs_rules(header + "def read_query(request):\n    unit = prepare()\n    " + statement + "\n")
                self.assertEqual("#153" in c, candidate)

    def test_later_import_shadow_invalidates_standard_enum_origin(self):
        for header, base in [
            ("from enum import Enum\nfrom custom import Enum", "Enum"),
            ("import enum as standard\nimport custom as standard", "standard.Enum"),
        ]:
            with self.subTest(header=header):
                self.assertIn("#268", self.enum_rules(header + f"\nclass Kind({base}):\n    ONE = 1\n")[1])

    def test_rebound_annotated_factory_is_not_revived(self):
        body = "with make():\n        books.save(a)\n    with make():\n        loans.save(b)"
        f, c = self.application_rules(body, "def make() -> Work: return Work()\nmake = dynamic")
        self.assertNotIn("#546", f)
        self.assertIn("#546", c)

    def test_constructor_branch_invalidates_uow_field_origin(self):
        self.application_rules("pass")
        source = "from application.lesson.application_layer.port.unit_of_work.lesson_unit_of_work import LessonUnitOfWork as Work\nclass Run:\n    def __init__(self, context: Work, books: BookRepository, loans: LoanRepository):\n        self.context = context\n        self.books = books\n        self.loans = loans\n        if flag: self.context = dynamic()\n    def execute(self):\n        with self.context:\n            self.books.save(a)\n        with self.context:\n            self.loans.save(b)\n"
        self.write("application/lesson/application_layer/books/run/run_use_case.py", source)
        f, c = domain.Findings(defer=True), domain.Candidates(defer=True)
        domain._check_application_side(self.root, self.root / "application/lesson", f, c)
        self.assertNotIn("#546", [e.rule for e in f.entries])
        self.assertIn("#546", [e.rule for e in c.entries])

    def test_constructor_branch_invalidates_contract_field_origin(self):
        source = "from application.lesson.domain_layer.book.kind import Kind\nclass Run:\n    def __init__(self, value: Kind):\n        self.value = value\n        if flag: self.value = dynamic()\n    def execute(self): return self.value.code == 1\n"
        f, c = self.property_rules(source)
        self.assertNotIn("#557", f)
        self.assertIn("#557", c)

    def test_initial_static_module_alias_preserves_origin_but_rebinding_does_not(self):
        for imported, comparison, expected in [
            ("from requests import Response as Source", "value.status_code == 200", "violation"),
            ("from application.lesson.domain_layer.book.kind import Kind as Source", "value.code == 1", None),
        ]:
            for suffix, wanted in [("", expected), ("Alias = dynamic\n", "candidate"),
                                   ("if flag: Alias = dynamic\n", "candidate")]:
                with self.subTest(imported=imported, suffix=suffix):
                    source = imported + "\nAlias = Source\n" + suffix + "def run(value: Alias): return " + comparison + "\n"
                    f, c = self.property_rules(source)
                    self.assertEqual("#557" in f, wanted == "violation")
                    self.assertEqual("#557" in c, wanted == "candidate")

    def test_later_module_compound_rebinding_invalidates_function_constructor(self):
        for imported, comparison in [
            ("from requests import Response as Source", "value.status_code == 200"),
            ("from application.lesson.domain_layer.book.kind import Kind as Source", "value.code == 1"),
        ]:
            for later in ["if flag: Alias = dynamic", "while flag: Alias = dynamic",
                          "for item in items: Alias = dynamic", "with context: Alias = dynamic",
                          "try: Alias = dynamic\nexcept Exception: pass"]:
                with self.subTest(imported=imported, later=later):
                    source = imported + "\nAlias = Source\ndef run():\n    value = Alias()\n    return " + comparison + "\n" + later + "\n"
                    f, c = self.property_rules(source)
                    self.assertNotIn("#557", f)
                    self.assertIn("#557", c)

    def test_nested_definition_bindings_do_not_rebind_module_constructor_alias(self):
        for imported, comparison, vendor in [
            ("from requests import Response as Source", "value.status_code == 200", True),
            ("from application.lesson.domain_layer.book.kind import Kind as Source", "value.code == 1", False),
        ]:
            for definition in ["def unused():", "class Unused:"]:
                with self.subTest(imported=imported, definition=definition):
                    source = imported + "\nAlias = Source\ndef run():\n    value = Alias()\n    return " + comparison + "\nif flag:\n    " + definition + "\n        Alias = dynamic\n"
                    f, c = self.property_rules(source)
                    self.assertEqual("#557" in f, vendor)
                    self.assertNotIn("#557", c)

    def test_later_with_item_rebinding_invalidates_function_constructor(self):
        for imported, comparison in [
            ("from requests import Response as Source", "value.status_code == 200"),
            ("from application.lesson.domain_layer.book.kind import Kind as Source", "value.code == 1"),
        ]:
            with self.subTest(imported=imported):
                source = imported + "\nAlias = Source\ndef run():\n    value = Alias()\n    return " + comparison + "\nwith context as Alias:\n    pass\n"
                f, c = self.property_rules(source)
                self.assertNotIn("#557", f)
                self.assertIn("#557", c)

    def admin_records(self, source):
        self.write("framework/admin/book.py", source)
        records = self.root / "findings.jsonl"
        records.unlink(missing_ok=True)
        run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'check-public-surface-annotation.py'),
                              str(self.root)], env=self.env, text=True, capture_output=True)
        self.assertIn(run.returncode, (0, 2), run.stdout + run.stderr)
        return [json.loads(line) for line in records.read_text().splitlines()] if records.exists() else []


    def test_admin_kwargs_actual_consumption_and_unknown_escape(self):
        prefix = ("from typing import Any\nfrom django.contrib.admin import ModelAdmin\n"
                  "from django.http import HttpResponse\nclass BookAdmin(ModelAdmin):\n"
                  "    def get_form(self, request: object, **kwargs: Any) -> HttpResponse:\n")
        for body, expected in [
            ("return super().get_form(request, **kwargs)", []),
            ("...", []),
            ("if kwargs['amount'] > 10:\n            charge(kwargs['amount'])\n        return super().get_form(request, **kwargs)", ['violation']),
            ("options = kwargs\n        charge(options['amount'])\n        return super().get_form(request, **kwargs)", ['violation']),
            ("unknown(kwargs)\n        return super().get_form(request, **kwargs)", ['info']),
        ]:
            with self.subTest(body=body):
                rows = self.admin_records(prefix + '        ' + body + '\n')
                self.assertEqual([r['severity'] for r in rows if r['rule'] == '#645'], expected, rows)
                self.assertTrue(any(r['rule'] == '#646' for r in rows), rows)
                self.assertFalse(any(r['rule'] == '#647' for r in rows), rows)
        rows = self.admin_records(prefix + "        import json\n        decoded: dict[str, object] = json.loads(request.body)\n        return super().get_form(request, **kwargs)\n")
        self.assertTrue(any(r['rule'] == '#650' for r in rows), rows)

    def test_ohs_module_definitions_invalidate_imported_builder(self):
        header = "from application.lesson.composition_root.books import build_read_use_case as _prepare\n"
        for definition, expected in [
            ('', False), ('def _prepare(): return cursor\n', True),
            ('async def _prepare(): return cursor\n', True), ('class _prepare: pass\n', True),
            ('def _unused():\n    def _prepare(): return cursor\n', False),
            ('class _Unused:\n    class _prepare: pass\n', False),
        ]:
            with self.subTest(definition=definition):
                f, c = self.ohs_rules(header + definition + 'def read_query(request):\n    _prepare().execute()\n')
                self.assertNotIn('#153', f)
                self.assertEqual('#153' in c, expected)

    def test_uow_module_class_shadow_keeps_unknown_region_candidate(self):
        body = "with uow:\n        books.save(a)\n    with uow:\n        loans.save(b)"
        for header, expected in [('', False), ('class Work: pass\n', True),
                                 ('class Other: pass\n', False),
                                 ('def unused():\n    class Work: pass\n', False)]:
            with self.subTest(header=header):
                f, c = self.application_rules(body, header)
                self.assertNotIn('#546', f)
                self.assertEqual('#546' in c, expected)

    def test_admin_context_real_parler_helper_and_business_opposite(self):
        source = """from typing import Any
from parler.admin import TranslatableAdmin
class BookAdmin(TranslatableAdmin):
    def changeform_view(self, request: object, extra_context: dict[str, Any] | None = None) -> HttpResponse:
        return self._render_failed_submission(request, extra_context)
    def _render_failed_submission(self, request: object, extra_context: dict[str, Any] | None) -> HttpResponse:
        form = self.get_form(request)(request.POST)
        inline_instances = self.get_inline_instances(request)
        media = self.media + form.media
        context: dict[str, Any] = self.admin_site.each_context(request)
        context.update({'form': form, 'inline_admin_formsets': inline_instances, 'media': media,
                        'is_popup': request.GET.get('_popup'), 'source_model': request.POST.get('source_model'),
                        'to_field': request.GET.get('_to_field')})
        context.update(extra_context or {})
        return self.render_change_form(request, context)
"""
        rows = self.admin_records(source)
        self.assertEqual([r for r in rows if r['rule'] in ('#645', '#647')], [])
        for consumption in ["charge(context['amount'])", "context['amount'] > 10", "self.total = context['amount']"]:
            with self.subTest(consumption=consumption):
                rows = self.admin_records(source.replace('        return self.render_change_form',
                                                         '        ' + consumption + '\n        return self.render_change_form'))
                self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
        rows = self.admin_records(source.replace('        return self.render_change_form',
                                                 '        unknown(context)\n        return self.render_change_form'))
        self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'info' for r in rows), rows)
        self.assertFalse(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)

    def test_admin_context_origin_alias_fixed_slots_and_local_business(self):
        source = """from typing import Any, TYPE_CHECKING
from django.contrib import admin as adm
if TYPE_CHECKING:
    Base = adm.ModelAdmin[Book]
else:
    Base = adm.ModelAdmin
class BookAdmin(Base):
    inlines: list[type[adm.TabularInline[Any]]] = []
    def get_form(self, request: object, **kwargs: Any) -> HttpResponse: ...
    def get_inline_instances(self, request: object) -> list[adm.InlineModelAdmin[Any]]: ...
    def render_change_form(self, request: object, context: dict[str, Any]) -> HttpResponse:
        copied: dict[str, Any] = {**context, 'title': 'edit'}
        copied = dict(copied)
        copied = copied.copy()
        if context is not None:
            copied['subtitle'] = 'book'
        return super().render_change_form(request, copied)
"""
        rows = self.admin_records(source)
        self.assertEqual([r for r in rows if r['rule'] in ('#645', '#647')], [])
        for prefix in ['class Base: pass\n', 'from unrelated import Base\n',
                       'from django.contrib.admin import ModelAdmin as Base\nBase = object\n']:
            rows = self.admin_records("from typing import Any\n" + prefix + source[source.index('class BookAdmin'):])
            self.assertTrue(any(r['rule'] == '#647' for r in rows), rows)
        rows = self.admin_records(source.replace("        copied: dict", "        payload: dict[str, Any] = {'amount': 10}\n        charge(payload['amount'])\n        copied: dict"))
        self.assertTrue(any(r['rule'] == '#647' and '`payload`' in r['message'] and r['severity'] == 'violation' for r in rows), rows)
        rows = self.admin_records(source.replace('class BookAdmin(Base):', 'class BookAdmin(adm.ModelAdmin[Book]):'))
        self.assertTrue(any(r['rule'] == '#646' for r in rows), rows)
        rows = self.admin_records(source.replace('request: object, context:', 'request, context:'))
        self.assertTrue(any(r['rule'] == '#493' for r in rows), rows)
        rows = self.admin_records(source.replace('        copied: dict', '        import json\n        decoded: dict[str, object] = json.loads(request.body)\n        copied: dict'))
        self.assertTrue(any(r['rule'] == '#650' for r in rows), rows)

    def test_admin_context_sources_consumption_rebind_and_bare_slots(self):
        source = """from typing import Any
from django.contrib.admin import ModelAdmin as Admin
from django.template.response import TemplateResponse as Response
class BookAdmin(Admin):
    def changelist_view(self, request: object) -> HttpResponse:
        bag: dict[str, Any] = self.admin_site.each_context(request)
        bag.update({'title': 'books'})
        return Response(request, 'book.html', bag)
"""
        for value in ["self.admin_site.each_context(request)", "{'title': 'books'}"]:
            rows = self.admin_records(source.replace('self.admin_site.each_context(request)', value))
            self.assertEqual([r for r in rows if r['rule'] in ('#645', '#647')], [], rows)
        for consumption in ["charge(bag.get('amount'))", "amount = len(bag)", "bag + other", "self.saved = bag"]:
            rows = self.admin_records(source.replace("        return Response", '        ' + consumption + '\n        return Response'))
            self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
        rows = self.admin_records(source.replace('self.admin_site.each_context(request)', 'unknown()'))
        self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'info' for r in rows), rows)
        rows = self.admin_records(source + "\nclass Bare(Admin):\n    def render_change_form(self, request: object, context: Any) -> Any: ...\n")
        self.assertTrue(any(r['rule'] == '#645' and '매개변수 `context`' in r['message'] and r['severity'] == 'violation' for r in rows), rows)
        # A once-valid alias that is rebound to a local fake cannot preserve origin.
        rows = self.admin_records(source.replace('class BookAdmin(Admin):', 'Alias = Admin\nAlias = object\nclass BookAdmin(Alias):'))
        self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)

    def test_admin_helper_return_cycles_and_mixed_bare_annotation(self):
        source = """from typing import Any
from parler.admin import TranslatableAdmin
class BookAdmin(TranslatableAdmin):
    def changeform_view(self, request: object, extra_context: dict[str, Any]) -> HttpResponse:
        bag: dict[str, Any] = self._first(extra_context)
        return super().changeform_view(request, extra_context=bag)
    def _first(self, value: dict[str, Any]) -> dict[str, Any]:
        return self._second(value)
    def _second(self, value: dict[str, Any]) -> dict[str, Any]:
        return dict(value)
"""
        rows = self.admin_records(source)
        self.assertEqual([r for r in rows if r['rule'] in ('#645', '#647')], [], rows)
        rows = self.admin_records(source.replace('return dict(value)', 'return self._first(value)'))
        self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'info' for r in rows), rows)
        self.assertFalse(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
        rows = self.admin_records(source.replace('extra_context: dict[str, Any]', 'extra_context: dict[str, Any] | Any'))
        self.assertTrue(any(r['rule'] == '#645' and r['severity'] == 'violation' for r in rows), rows)
        rows = self.admin_records(source.replace('class BookAdmin(TranslatableAdmin):', 'class BookAdmin(TranslatableAdmin):\n    inlines: list[Any] = []'))
        self.assertTrue(any(r['rule'] == '#645' and '`inlines`' in r['message'] for r in rows), rows)

    def test_admin_context_shadowed_transport_names_are_not_framework_proof(self):
        source = """from typing import Any
from parler.admin import TranslatableAdmin
from django.template.response import TemplateResponse as Response
class BookAdmin(TranslatableAdmin):
    def changeform_view(self, request: object, extra_context: dict[str, Any]) -> HttpResponse:
        bag: dict[str, Any] = dict(extra_context)
        return Response(request, 'book.html', bag)
"""
        variants = [source.replace('        bag:', insertion + '        bag:')
                    for insertion in ['        Response = unknown\n', '        dict = unknown\n']]
        variants.append(source.replace('class BookAdmin', 'dict = unknown\nclass BookAdmin'))
        for variant in variants:
            rows = self.admin_records(variant)
            self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'info' for r in rows), rows)
            self.assertFalse(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)

    def test_admin_augmented_write_and_module_super_shadow_preserve_diagnostics(self):
        source = """from typing import Any
from parler.admin import TranslatableAdmin
class BookAdmin(TranslatableAdmin):
    def changeform_view(self, request: object, extra_context: dict[str, Any]) -> HttpResponse:
        extra_context['title'] = 'Books'
        return super().changeform_view(request, extra_context=extra_context)
"""
        cases = [
            ('plain UI assignment', source, []),
            ('ordinary read', source.replace("extra_context['title'] = 'Books'", "total = extra_context['amount'] + 1"), ['violation']),
            ('augmented write', source.replace("extra_context['title'] = 'Books'", "extra_context['amount'] += 1"), ['violation']),
            ('module super shadow', source.replace('class BookAdmin', 'super = unknown\nclass BookAdmin'), ['info']),
        ]
        for label, variant, expected in cases:
            with self.subTest(case=label):
                rows = self.admin_records(variant)
                context_rows = [r for r in rows if r['rule'] in ('#645', '#647')]
                self.assertEqual([r['severity'] for r in context_rows], expected, context_rows)
                if expected:
                    self.assertEqual([r['rule'] for r in context_rows], ['#647'])
                    self.assertIn('매개변수 `extra_context`', context_rows[0]['message'])

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


class CacheInstanceRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="field-cache-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project"
        shutil.copytree(FIXTURES / "skeleton/good_bc", self.root)
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                        DJR_FINDINGS_JSON=str(Path(self.tmp.name) / "records.jsonl"),
                        DJR_VIOLATIONS_DIR=str(Path(self.tmp.name) / "violations"))

    def plant(self, relative, extra=None):
        path = self.root / relative
        (path / "nested/__pycache__").mkdir(parents=True, exist_ok=True)
        (path / "nested/__pycache__/old.cpython-314.pyc").write_bytes(b"cache")
        (path / "empty").mkdir(exist_ok=True)
        if extra is not None:
            (path / extra).write_text("", encoding="utf-8")
        return path

    def run_checker(self, script):
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), str(self.root)],
                                capture_output=True, text=True, env=self.env)
        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_cache_predicate_requires_cache_and_rejects_actual_files_links_and_read_errors(self):
        import checker_target
        predicate = checker_target.cache_only_instance
        path = self.plant("scratch")
        self.assertTrue(predicate(path))
        (path / "nested").rename(path / "deep")
        self.assertTrue(predicate(path))
        direct = self.root / "direct/__pycache__"
        direct.mkdir(parents=True)
        self.assertFalse(predicate(direct.parent))
        (direct / "cached.pyc").write_bytes(b"cache")
        self.assertTrue(predicate(direct.parent))
        (direct / "real.py").write_text("pass\n")
        self.assertFalse(predicate(direct.parent))
        for extra in ("real.py", "__init__.py", ".hidden", "notes.txt", "loose.pyc"):
            with self.subTest(extra=extra):
                (path / extra).write_bytes(b"")
                self.assertFalse(predicate(path))
                (path / extra).unlink()
        for name in ("link", "__pycache__/linked.pyc"):
            link = path / name
            link.parent.mkdir(exist_ok=True)
            link.symlink_to(path / "deep")
            self.assertFalse(predicate(path))
            link.unlink()
        with patch.object(Path, "iterdir", side_effect=PermissionError("denied")):
            self.assertFalse(predicate(path))
        with patch.object(Path, "open", side_effect=PermissionError("denied")):
            self.assertFalse(predicate(path))
        empty = self.root / "empty_only/nested"
        empty.mkdir(parents=True)
        self.assertFalse(predicate(empty.parent))
        self.assertFalse(predicate(self.root / "missing"))

    def test_optional_instances_skip_only_cache_and_keep_real_and_empty_diagnostics(self):
        cases = [
            ("domain_layer/vanished", "check-domain-model.py", ("#299", "#256")),
            ("application_layer/order/vanished", "check-usecase-dto-placement.py", ("#193", "#570", "#569")),
            ("driving_layer/open_host_service/vanished", "check-context-isolation.py", ("#152",)),
            ("application_layer/port/vanished", "check-port-adapter-pairing.py", ("#218", "#225")),
            ("application_layer/port/domain_bypass_query/vanished", "check-port-adapter-pairing.py", ("#234", "#238")),
            ("driven_layer/adapter/email_sender/vanished_adapter", "check-layer-skeleton.py", ("#488",)),
        ]
        for relative, script, rules in cases:
            path = self.plant("application/orders/" + relative)
            for extra in (None, "__init__.py", "source.py", ".hidden"):
                with self.subTest(slot=relative, extra=extra):
                    if extra:
                        (path / extra).write_text("pass\n" if extra == "source.py" else "")
                    output = self.run_checker(script)
                    hits = [line for line in output.splitlines() if "vanished" in line]
                    for rule in rules:
                        self.assertEqual(any(rule in line for line in hits), extra is not None, output)
                    if extra:
                        (path / extra).unlink()
            shutil.rmtree(path)
            path.mkdir()
            output = self.run_checker(script)
            for rule in rules:
                self.assertTrue(any(rule in line and "vanished" in line for line in output.splitlines()), output)
            shutil.rmtree(path)

    def direct_and_snapshot_results(self, script):
        gate = _load_module(SCRIPTS / "registry_gate.py", "field_cache_snapshot")
        with tempfile.TemporaryDirectory(prefix="field-cache-copy-") as temp:
            snapshot = Path(temp) / "snapshot"
            gate._snapshot_current(self.root, snapshot)
            results = []
            for target in (self.root, snapshot):
                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), str(target)],
                                        capture_output=True, text=True, env=self.env)
                results.append((result.returncode, result.stdout + result.stderr))
            return results

    def test_validation_scan_respects_owning_cache_only_area_and_usecase(self):
        for relative in ("order/vanished", "vanished_area/vanished"):
            for banned in ("validation", "validators"):
                path = self.plant("application/orders/application_layer/" + relative)
                (path / banned).mkdir()
                for source in (None, "__init__.py", "real.py"):
                    with self.subTest(instance=relative, banned=banned, source=source):
                        if source:
                            (path / source).write_text("pass\n" if source == "real.py" else "")
                        results = self.direct_and_snapshot_results("check-usecase-dto-placement.py")
                        for channel, (code, output) in zip(("direct", "snapshot"), results):
                            with self.subTest(channel=channel):
                                self.assertEqual(code, 2 if source else 0, output)
                                self.assertEqual(any("#183" in line and banned in line for line in output.splitlines()),
                                                 source is not None, output)
                        if source:
                            (path / source).unlink()
                shutil.rmtree(path)
                if relative.startswith("vanished_area"):
                    shutil.rmtree(path.parent)

    def test_cache_only_names_do_not_change_real_usecase_service_or_enum_candidates(self):
        cases = (
            ("domain_layer/place_order", "check-usecase-dto-placement.py", "#191"),
            ("domain_layer/order_lookup", "check-context-isolation.py", "#151"),
            ("application_layer/order/vanished", "check-domain-model.py", "#565"),
            ("application_layer/vanished_area/vanished", "check-domain-model.py", "#565"),
        )
        enum = self.root / "application/orders/domain_layer/order/value_object/workflow.py"
        enum.write_text("from enum import Enum\nclass Workflow(Enum):\n    VANISHED = 'vanished'\n")
        for relative, script, rule in cases:
            path = self.plant("application/orders/" + relative)
            for source in (None, "__init__.py", "real.py", "empty_instance"):
                with self.subTest(instance=relative, source=source, rule=rule):
                    if source == "empty_instance":
                        shutil.rmtree(path)
                        path.mkdir()
                    elif source:
                        (path / source).write_text("pass\n" if source == "real.py" else "")
                    results = self.direct_and_snapshot_results(script)
                    for channel, (code, output) in zip(("direct", "snapshot"), results):
                        with self.subTest(channel=channel):
                            self.assertIn(code, (0, 2), output)
                            hits = [line for line in output.splitlines() if "[ⓓ" + rule + "]" in line]
                            self.assertEqual(len(hits), 1 if source else 0, output)
                    if source and source != "empty_instance":
                        (path / source).unlink()
            shutil.rmtree(path)
            if relative.startswith("application_layer/vanished_area"):
                shutil.rmtree(path.parent)

    def test_cache_cannot_hide_fixed_skeleton_and_promoted_parts_have_no_floor(self):
        fixed = self.root / "application/orders/application_layer/port/unit_of_work"
        shutil.rmtree(fixed)
        self.plant(str(fixed.relative_to(self.root)))
        output = self.run_checker("check-layer-skeleton.py")
        self.assertTrue(any("#488" in line and "unit_of_work" in line for line in output.splitlines()), output)
        shutil.rmtree(self.root)
        shutil.copytree(FIXTURES / "skeleton/good_promoted", self.root)
        promoted = self.root / "application/orders/driving_layer/api/order/order_controller"
        part = promoted / "order_sse_renderer.py"
        for lines in (1, 49, 201):
            part.write_text("pass\n" * lines)
            output = self.run_checker("check-layer-skeleton.py")
            self.assertNotIn("#642", output)
            self.assertEqual(any("#644" in line and "order_sse_renderer.py" in line for line in output.splitlines()), lines == 201, output)
        part.unlink()
        self.assertIn("#643", self.run_checker("check-layer-skeleton.py"))
        part.write_text("pass\n")
        for change, rule in (("missing", "#638"), ("nested", "#641"), ("junk", "#640"), ("sibling", "#639")):
            with self.subTest(change=change):
                if change == "missing":
                    victim = promoted / "order_controller.py"
                    victim.unlink()
                elif change == "nested":
                    (promoted / "nested").mkdir()
                elif change == "junk":
                    (promoted / "utils.py").write_text("pass\n")
                else:
                    (promoted.parent / "order_controller.py").write_text("pass\n")
                self.assertIn(rule, self.run_checker("check-layer-skeleton.py"))


class NormativeContractRegression(unittest.TestCase):
    """문면 전파 대조이며 역할 에이전트의 실제 수행 증명은 아니다."""

    def test_internal_normalization_and_public_500_are_distinct_in_six_sources(self):
        for rel in (
            "dddjango/agents/design-architect.md", "dddjango/agents/design-review-api.md",
            "dddjango/agents/discipline-reviewer.md", "dddjango/skills/implementation-django-ninja/SKILL.md",
            "dddjango/skills/implementation-django-ninja/references/final.md",
        ):
            with self.subTest(path=rel):
                text = (ROOT / rel).read_text()
                expected_count = 2 if rel.endswith("discipline-reviewer.md") else 1
                for phrase in ("이미 잡은 IntegrityError", "일반 저장소 실패 계약", "기존 safe 500", "새로 catch-all하지 않는다"):
                    self.assertEqual(text.count(phrase), expected_count, (rel, phrase))

    def test_admin_policy_names_actual_consumption_boundary(self):
        for rel in ("dddjango/skills/discipline-houserules/SKILL.md", "dddjango/agents/design-architect.md",
                    "dddjango/agents/discipline-reviewer.md"):
            with self.subTest(path=rel):
                text = (ROOT / rel).read_text()
                for phrase in ("private 전달 helper", "업무 읽기·비교·계산·상태 변경", "출처나 소비가 미해소"):
                    self.assertIn(phrase, text)

    def test_promotion_has_no_birth_floor_and_keeps_zero_part_reversion(self):
        skill = (ROOT / "dddjango/skills/discipline-houserules/SKILL.md").read_text()
        reference = (ROOT / "dddjango/skills/discipline-houserules/references/final.md").read_text()
        self.assertNotIn("개별 50행 이상", skill)
        self.assertNotIn("출생 하한", reference)
        self.assertIn("부품이 0개", reference)
        for rel in ("docs/file_tree.html", "docs/mkrev2.py"):
            self.assertNotIn("새 승격 부품은 각 50행 이상", (ROOT / rel).read_text())

    def test_optional_effects_poststate_and_s1_limits_are_explicit(self):
        architect = (ROOT / "dddjango/agents/design-architect.md").read_text()
        coordinator = (ROOT / "dddjango/commands/dddjango.md").read_text()
        for phrase in ("<!-- machine: use-case-effects -->", "read-only", "uow=none", "module pytestmark 최종 목록", "출처 결합 DTO"):
            self.assertIn(phrase, architect)
        for phrase in ("효과 블록이 없으면 기존 해시", "선언 확정", "S1 미검증"):
            self.assertIn(phrase, coordinator)


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
