#!/usr/bin/env python3
"""현장 F4/F7/F8 회귀: 골격·의미 후보·앵커 전체 수집의 반대 대조를 고정한다."""
from __future__ import annotations

import ast
import contextlib
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from pregate_fixture_run import _git, _load_module
import corpus_mirror_sync as corpus
from ontology_census import parse_sections
import api_error_backstop_matrix as backstop_matrix

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


class DomainServiceArgumentsRegression(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="field-domain-service-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        aggregate = self.root / "application/orders/domain_layer/order"
        aggregate.mkdir(parents=True)
        (aggregate / "order.py").write_text("class Order: pass\n", encoding="utf-8")
        (aggregate / "order_repository.py").write_text("class OrderRepository: pass\n", encoding="utf-8")
        self.service = aggregate.parent / "domain_service/order_rule.py"
        self.service.parent.mkdir()
        self.records = self.root / "findings.jsonl"
        self.env = dict(os.environ, DJR_FINDINGS_JSON=str(self.records),
                        DJR_VIOLATIONS_DIR=str(self.root / "violations"))

    def run_service(self, parameters, receiver="self", declaration="def", receiver_type="OrderRepository"):
        decorator = "    @classmethod\n" if receiver == "cls" else ""
        self.service.write_text(
            f"class OrderRule:\n{decorator}    {declaration} run({receiver}: {receiver_type}, {parameters}) -> None:\n"
            "        pass\n", encoding="utf-8")
        self.records.unlink(missing_ok=True)
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "check-domain-model.py"), str(self.root)],
                                capture_output=True, text=True, env=self.env)
        records = [json.loads(line) for line in self.records.read_text(encoding="utf-8").splitlines()] \
            if self.records.exists() else []
        identities = [{key: row[key] for key in ("schema", "checker", "rule", "file", "symbol", "severity", "message")}
                      for row in records]
        return result.returncode, result.stdout, result.stderr, identities

    def assert_parameter_shapes(self, rule, parameter, exit_code, severity):
        for receiver in ("self", "cls"):
            for declaration in ("def", "async def"):
                baseline = None
                for shape, parameters in (("positional", parameter), ("kw-only", "*, " + parameter),
                                          ("pos-only", parameter + ", /")):
                    with self.subTest(rule=rule, shape=shape, receiver=receiver, declaration=declaration):
                        result = self.run_service(parameters, receiver, declaration,
                                                  "Order" if rule == "#301" else "OrderRepository")
                        if shape == "positional":
                            baseline = result
                        self.assertEqual(result[0], exit_code, result[1] + result[2])
                        self.assertEqual(result[2], "")
                        self.assertEqual([(row["rule"], row["severity"]) for row in result[3]], [(rule, severity)])
                        marker = f"[ⓓ{rule}]" if severity == "info" else f"[{rule}]"
                        self.assertEqual(result[1].count(marker), 1, result[1])
                        self.assertEqual(result, baseline, "출력·발견 키·exit 는 위치 인자와 같아야 한다")

    def test_repository_parameter_shapes(self):
        self.assert_parameter_shapes("#304", "repository: OrderRepository", 2, "violation")

    def test_port_parameter_shapes(self):
        self.assert_parameter_shapes("#305", "port: PaymentPort", 2, "violation")

    def test_primitive_parameter_shapes(self):
        self.assert_parameter_shapes("#307", "amount: int", 2, "violation")

    def test_root_parameter_shapes(self):
        self.assert_parameter_shapes("#301", "order: Order", 0, "info")

    def test_mixed_parameter_order_and_value_object_opposite(self):
        result = self.run_service("repository: OrderRepository, /, port: PaymentPort, *, amount: int")
        self.assertEqual(result[0], 2, result[1] + result[2])
        self.assertEqual([row["rule"] for row in result[3]], ["#304", "#305"])
        result = self.run_service("amount: int, /, other: int, *, money: Money")
        self.assertEqual(result, (0, "", "", []))
        result = self.run_service("first: Order, /, amount: int, *, second: Order")
        self.assertEqual(result, (0, "", "", []))


ORDER_SOURCE = '''from __future__ import annotations


class Order:
    def __init__(self, order_id: int) -> None:
        self.id: int = order_id
        self.status: str = "NEW"

    def place(self) -> None:
        self.status = "PLACED"
'''
ORDER_REPOSITORY_SOURCE = '''from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: int) -> Order: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...
'''
ORDERS_UNIT_OF_WORK_SOURCE = '''from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from types import TracebackType


class OrdersUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self) -> "OrdersUnitOfWork": ...

    @abstractmethod
    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None,
                 traceback: TracebackType | None) -> None: ...

    @abstractmethod
    def after_commit(self, callback: Callable[[], None]) -> None: ...
'''
TRANSIENT_CONTRACT = "선행 계약(08-04 API-error) 소유"


class CheckerArgumentKindsRegression(unittest.TestCase):
    """F4-76 과 뿌리가 같은 인자 수집 — 위치 전용 · kw-only 인자도 위치 인자와 같은 판정을 낸다(#287 · #533 · transient
    핸들러 판별 · #195 · #197 · #280 · #14 · #11 · #545). 꼴마다 첫 항목이 위치 인자 기준이다."""

    IDENTITY = ("schema", "checker", "rule", "contract_ref", "file", "symbol", "severity", "message")

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="field-argument-kinds-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project"
        self.records = Path(self.tmp.name) / "findings.jsonl"
        self.env = dict(os.environ, DJR_FINDINGS_JSON=str(self.records),
                        DJR_VIOLATIONS_DIR=str(Path(self.tmp.name) / "violations"))

    def run_checker(self, checker, files):
        for rel, source in files.items():
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")
        self.records.unlink(missing_ok=True)
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / checker), str(self.root)],
                                capture_output=True, text=True, env=self.env)
        records = [json.loads(line) for line in self.records.read_text(encoding="utf-8").splitlines()] \
            if self.records.exists() else []
        identities = [{key: row[key] for key in self.IDENTITY} for row in records]
        return result.returncode, result.stdout, result.stderr, identities

    def assert_shapes(self, checker, build, shapes, exit_code, rules):
        baseline = None
        for shape, signature in shapes:
            with self.subTest(checker=checker, shape=shape, signature=signature):
                result = self.run_checker(checker, build(signature))
                if baseline is None:
                    baseline = result
                self.assertEqual(result[0], exit_code, result[1] + result[2])
                self.assertEqual(result[2], "")
                self.assertEqual([row["rule"] or row["contract_ref"] for row in result[3]], rules, result[1])
                self.assertEqual(result, baseline, "출력·발견 키·exit 는 위치 인자 꼴과 같아야 한다")

    @staticmethod
    def repository(method):
        def build(parameters):
            return {
                "application/orders/domain_layer/order/order.py": ORDER_SOURCE,
                "application/orders/domain_layer/order/order_repository.py":
                    "from __future__ import annotations\n\nfrom abc import ABC, abstractmethod\n\n"
                    "from application.orders.domain_layer.order.order import Order\n\n\n"
                    "class OrderRepository(ABC):\n    @abstractmethod\n"
                    f"    def {method}(self, {parameters}) -> None: ...\n",
            }
        return build

    def test_repository_write_arguments_287(self):
        self.assert_shapes("check-transaction-boundary.py", self.repository("save"), (
            ("positional", "order: Order, force: bool"), ("kw-only", "*, order: Order, force: bool"),
            ("pos-only", "order: Order, force: bool, /"), ("pos-only + positional", "order: Order, /, force: bool"),
            ("positional + kw-only", "order: Order, *, force: bool = False"),
        ), 2, ["#287"])
        self.assert_shapes("check-transaction-boundary.py", self.repository("remove"), (
            ("positional", "order_id: int"), ("kw-only", "*, order_id: int"), ("pos-only", "order_id: int, /"),
        ), 2, ["#287"])
        self.assert_shapes("check-transaction-boundary.py", self.repository("save"), (
            ("positional", "order: Order"), ("kw-only", "*, order: Order"), ("pos-only", "order: Order, /"),
        ), 0, [])

    @staticmethod
    def external_broker(parameters):
        port = ('"""external 브로커 계약.\n\n'
                "보장: at-least-once — 반드시 도달하고 두 번 올 수 있다. 발행은 outbox 를 거치고,\n"
                "실패는 dead_letter 로 간다. ordering 은 보장하지 않는다. 직렬화(serializer)는 JSON,\n"
                '스키마 version 필드를 싣는다.\n"""\n'
                "from __future__ import annotations\n\nfrom abc import ABC, abstractmethod\n"
                "from dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass EventEnvelope:\n"
                "    source: str\n    event_id: str\n    version: int\n    body: bytes\n\n\n"
                "class ExternalBrokerPort(ABC):\n    @abstractmethod\n"
                f"    def publish(self, {parameters}) -> None: ...\n")
        broker = ("from __future__ import annotations\n\n"
                  "from framework.broker.external.external_broker_port import EventEnvelope, ExternalBrokerPort\n\n\n"
                  f"class ExternalBroker(ExternalBrokerPort):\n    def publish(self, {parameters}) -> None:\n"
                  "        raise NotImplementedError\n")
        return {"framework/broker/external/external_broker_port.py": port,
                "framework/broker/external/external_broker.py": broker}

    def test_external_publish_envelope_533(self):
        self.assert_shapes("check-broker-contract.py", self.external_broker, (
            ("positional", "envelope: EventEnvelope"), ("kw-only", "*, envelope: EventEnvelope"),
            ("pos-only", "envelope: EventEnvelope, /"),
        ), 0, [])
        # 인자 이름이 봉투가 아니면(`msg`) 이름 갈래가 아니라 주석(`…Envelope`) 갈래만 봉투를 인정한다.
        self.assert_shapes("check-broker-contract.py", self.external_broker, (
            ("positional", "msg: EventEnvelope"), ("kw-only", "*, msg: EventEnvelope"), ("pos-only", "msg: EventEnvelope, /"),
        ), 0, [])
        self.assert_shapes("check-broker-contract.py", self.external_broker, (
            ("positional", "fact: object, event_id: str, source: str"),
            ("kw-only", "fact: object, *, event_id: str, source: str"),
            ("pos-only", "fact: object, event_id: str, source: str, /"),
        ), 0, [])
        self.assert_shapes("check-broker-contract.py", self.external_broker, (
            ("positional", "fact: object"), ("kw-only", "*, fact: object"), ("pos-only", "fact: object, /"),
        ), 2, ["#533", "#533"])

    @staticmethod
    def transient_handler(branch):
        guard = ('    if getattr(exc.__cause__, "sqlstate", None) not in {"40001", "40P01"}:\n'
                 '        return JsonResponse({"code": "INTERNAL"}, status=500)\n') if branch else ""

        def build(parameters):
            return {"config/api.py":
                    "from __future__ import annotations\n\nfrom django.db import OperationalError\n"
                    "from django.http import HttpRequest, JsonResponse\nfrom ninja_extra import NinjaExtraAPI\n\n"
                    f"api = NinjaExtraAPI()\n\n\ndef on_operational_error({parameters}) -> JsonResponse:\n{guard}"
                    '    return JsonResponse({"code": "UNAVAILABLE"}, status=503)\n\n\n'
                    "api.add_exception_handler(OperationalError, on_operational_error)\n"}
        return build

    def test_transient_handler_annotation(self):
        shapes = (("positional", "request: HttpRequest, exc: OperationalError"),
                  ("kw-only", "request: HttpRequest, *, exc: OperationalError"),
                  ("pos-only", "request: HttpRequest, exc: OperationalError, /"))
        self.assert_shapes("check-transient-overmapping.py", self.transient_handler(False), shapes, 2,
                           [TRANSIENT_CONTRACT])
        self.assert_shapes("check-transient-overmapping.py", self.transient_handler(True), shapes, 0, [])

    USE_CASE_SHAPES = (
        ("positional", "order_repository: OrderRepository, unit_of_work: OrdersUnitOfWork"),
        ("kw-only", "*, order_repository: OrderRepository, unit_of_work: OrdersUnitOfWork"),
        ("pos-only", "order_repository: OrderRepository, unit_of_work: OrdersUnitOfWork, /"),
        ("pos-only repository", "order_repository: OrderRepository, /, unit_of_work: OrdersUnitOfWork"),
        ("pos-only unit of work", "unit_of_work: OrdersUnitOfWork, /, order_repository: OrderRepository"),
    )

    @staticmethod
    def use_case(body, returns):
        def build(parameters):
            return {
                "application/orders/domain_layer/order/order.py": ORDER_SOURCE,
                "application/orders/domain_layer/order/order_repository.py": ORDER_REPOSITORY_SOURCE,
                "application/orders/application_layer/port/unit_of_work/orders_unit_of_work.py":
                    ORDERS_UNIT_OF_WORK_SOURCE,
                "application/orders/application_layer/order/place_order/place_order_use_case.py":
                    "from __future__ import annotations\n\n"
                    "from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import "
                    "OrdersUnitOfWork\nfrom application.orders.domain_layer.order.order import Order\n"
                    "from application.orders.domain_layer.order.order_repository import OrderRepository\n\n\n"
                    f"class PlaceOrderUseCase:\n    def __init__(self, {parameters}) -> None:\n"
                    "        self._order_repository = order_repository\n        self._unit_of_work = unit_of_work\n\n"
                    f"    def execute(self, order_id: int) -> {returns}:\n        with self._unit_of_work:\n{body}",
            }
        return build

    def test_use_case_write_discipline_195_197(self):
        field_write = ("            order = self._order_repository.get(order_id)\n"
                       '            order.status = "PLACED"\n            self._order_repository.save(order)\n')
        root_write = ("            order = self._order_repository.get(order_id)\n            order.place()\n"
                      "            self._order_repository.save(order)\n")
        read_only = "            return self._order_repository.get(order_id)\n"
        self.assert_shapes("check-transaction-boundary.py", self.use_case(field_write, "None"),
                           self.USE_CASE_SHAPES, 2, ["#195", "#195"])
        self.assert_shapes("check-transaction-boundary.py", self.use_case(read_only, "Order"),
                           self.USE_CASE_SHAPES, 2, ["#197"])
        self.assert_shapes("check-transaction-boundary.py", self.use_case(root_write, "None"),
                           self.USE_CASE_SHAPES, 0, [])

    @staticmethod
    def event_handler(argument):
        def build(parameters):
            return {
                "application/orders/published_event/order_placed.py":
                    "from __future__ import annotations\n\nfrom dataclasses import dataclass\n\n\n"
                    "@dataclass(frozen=True)\nclass OrderPlaced:\n    sku: str\n    quantity: int\n",
                "application/orders/domain_layer/order/order.py": ORDER_SOURCE,
                "application/inventory/domain_layer/stock/stock.py":
                    "from __future__ import annotations\n\n\nclass Stock:\n"
                    "    def __init__(self, sku: str, quantity: int) -> None:\n        self.sku: str = sku\n"
                    "        self.quantity: int = quantity\n\n    def reduce(self, quantity: int) -> None:\n"
                    "        self.quantity -= quantity\n",
                "application/inventory/domain_layer/stock/stock_repository.py":
                    "from __future__ import annotations\n\nfrom abc import ABC, abstractmethod\n\n"
                    "from application.inventory.domain_layer.stock.stock import Stock\n\n\n"
                    "class StockRepository(ABC):\n    @abstractmethod\n    def get(self, sku: str) -> Stock: ...\n\n"
                    "    @abstractmethod\n    def save(self, stock: Stock) -> None: ...\n",
                "application/inventory/application_layer/stock/reduce_stock/reduce_stock_use_case.py":
                    "from __future__ import annotations\n\n"
                    "from application.inventory.domain_layer.stock.stock_repository import StockRepository\n"
                    "from application.orders.published_event.order_placed import OrderPlaced\n\n\n"
                    "class ReduceStockUseCase:\n    def __init__(self, stock_repository: StockRepository) -> None:\n"
                    "        self._stock_repository = stock_repository\n\n"
                    f"    def execute(self, {parameters}) -> None:\n"
                    "        stock = self._stock_repository.get(event.sku)\n"
                    f"        stock.reduce({argument})\n        self._stock_repository.save(stock)\n",
            }
        return build

    def test_event_handler_translation_280(self):
        shapes = (("positional", "event: OrderPlaced"), ("kw-only", "*, event: OrderPlaced"),
                  ("pos-only", "event: OrderPlaced, /"))
        self.assert_shapes("check-event-publish.py", self.event_handler("event"), shapes, 2, ["#280"])
        self.assert_shapes("check-event-publish.py", self.event_handler("event.quantity"), shapes, 0, [])

    @staticmethod
    def cross_port_use_case(body):
        def build(parameters):
            return {
                "application/orders/application_layer/port/price_quote/price_quote_port.py":
                    "from __future__ import annotations\n\nfrom abc import ABC, abstractmethod\n\n\n"
                    "class PriceQuotePort(ABC):\n    @abstractmethod\n"
                    "    def quote(self, order_id: int) -> int: ...\n",
                "application/orders/application_layer/port/unit_of_work/orders_unit_of_work.py":
                    ORDERS_UNIT_OF_WORK_SOURCE,
                "application/orders/driven_layer/adapter/anticorruption_layer/pricing/pricing_price_quote_adapter.py":
                    "from __future__ import annotations\n\n"
                    "from application.orders.application_layer.port.price_quote.price_quote_port import "
                    "PriceQuotePort\n\n\nclass PricingPriceQuoteAdapter(PriceQuotePort):\n"
                    "    def quote(self, order_id: int) -> int:\n        return 0\n",
                "application/orders/application_layer/order/place_order/place_order_use_case.py":
                    "from __future__ import annotations\n\n"
                    "from application.orders.application_layer.port.price_quote.price_quote_port import "
                    "PriceQuotePort\n"
                    "from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import "
                    "OrdersUnitOfWork\n\n\n"
                    f"class PlaceOrderUseCase:\n    def __init__(self, {parameters}) -> None:\n"
                    "        self._price_quote_port = price_quote_port\n        self._unit_of_work = unit_of_work\n\n"
                    f"    def execute(self, order_id: int) -> int:\n{body}",
            }
        return build

    def test_cross_port_inside_unit_of_work_14(self):
        shapes = (("positional", "price_quote_port: PriceQuotePort, unit_of_work: OrdersUnitOfWork"),
                  ("kw-only", "*, price_quote_port: PriceQuotePort, unit_of_work: OrdersUnitOfWork"),
                  ("pos-only", "price_quote_port: PriceQuotePort, unit_of_work: OrdersUnitOfWork, /"),
                  ("pos-only port", "price_quote_port: PriceQuotePort, /, unit_of_work: OrdersUnitOfWork"))
        inside = "        with self._unit_of_work:\n            return self._price_quote_port.quote(order_id)\n"
        outside = ("        price = self._price_quote_port.quote(order_id)\n        with self._unit_of_work:\n"
                   "            return price\n")
        self.assert_shapes("check-context-isolation.py", self.cross_port_use_case(inside), shapes, 2, ["#14"])
        self.assert_shapes("check-context-isolation.py", self.cross_port_use_case(outside), shapes, 0, [])

    @staticmethod
    def export_port(parameters):
        return {"application/orders/application_layer/port/order_export/order_export_port.py":
                "from __future__ import annotations\n\nfrom abc import ABC, abstractmethod\n\n\n"
                "class OrderExportPort(ABC):\n    @abstractmethod\n"
                f"    def export(self, {parameters}) -> int: ...\n"}

    def test_boundary_annotation_11(self):
        self.assert_shapes("check-context-isolation.py", self.export_port, (
            ("positional", "rows: QuerySet"), ("kw-only", "*, rows: QuerySet"), ("pos-only", "rows: QuerySet, /"),
        ), 2, ["#11"])
        self.assert_shapes("check-context-isolation.py", self.export_port, (
            ("positional", "order_ids: tuple[int, ...]"), ("kw-only", "*, order_ids: tuple[int, ...]"),
            ("pos-only", "order_ids: tuple[int, ...], /"),
        ), 0, [])

    @staticmethod
    def repository_adapter(guard):
        guard_source = ('        if order.pending_events:\n            raise RuntimeError("uncollected events")\n'
                        if guard else "")

        def build(parameters):
            return {
                "application/orders/domain_layer/order/order.py":
                    "from __future__ import annotations\n\n\nclass Order:\n"
                    "    def __init__(self, order_id: int) -> None:\n        self.id: int = order_id\n"
                    '        self.status: str = "NEW"\n        self._pending_events: list[object] = []\n\n'
                    '    def place(self) -> None:\n        self.status = "PLACED"\n'
                    "        self._pending_events.append(object())\n\n    @property\n"
                    "    def pending_events(self) -> tuple[object, ...]:\n        return tuple(self._pending_events)\n\n"
                    "    def pull_events(self) -> tuple[object, ...]:\n"
                    "        events: tuple[object, ...] = tuple(self._pending_events)\n"
                    "        self._pending_events.clear()\n        return events\n",
                "application/orders/domain_layer/order/order_repository.py": ORDER_REPOSITORY_SOURCE,
                "application/orders/driven_layer/adapter/persistence/repository/order_repository.py":
                    "from __future__ import annotations\n\n"
                    "from application.orders.django_orders.models import OrderModel\n"
                    "from application.orders.domain_layer.order.order import Order\n"
                    "from application.orders.domain_layer.order.order_repository import OrderRepository\n\n\n"
                    "class DjangoOrderRepository(OrderRepository):\n"
                    "    def get(self, order_id: int) -> Order:\n        row = OrderModel.objects.get(id=order_id)\n"
                    f"        return Order(row.id)\n\n    def save(self, {parameters}) -> None:\n{guard_source}"
                    '        OrderModel.objects.update_or_create(id=order.id, defaults={"status": order.status})\n',
            }
        return build

    def test_repository_save_guard_545(self):
        shapes = (("positional", "order: Order"), ("kw-only", "*, order: Order"), ("pos-only", "order: Order, /"))
        self.assert_shapes("check-port-adapter-pairing.py", self.repository_adapter(True), shapes, 0, [])
        self.assert_shapes("check-port-adapter-pairing.py", self.repository_adapter(False), shapes, 2, ["#545"])


# ── F4-80 · F4-79 — 오류 설명의 사건 값(--event-value) ─────────────────────────────────────────
# 설계 `f80/design.md` A.8(+ 덧붙임 1) — 양성 P · 음성 N(변종 하나씩) · 줄은 표지(marker)가 가리키는 원문 행으로 고정한다.
EV_A = "application/accounts"
EV_CTRL = f"{EV_A}/driving_layer/api/account/account_controller.py"
EV_EXC_DIR = f"{EV_A}/domain_layer/account/exception"
EV_PORT_EXC = f"{EV_A}/application_layer/port/login_block/exception.py"
EV_OHS = f"{EV_A}/driving_layer/open_host_service/session_user/session_user_service.py"
EV_HOOK = f"{EV_A}/driving_layer/api/webhook/provider/provider_controller.py"
EV_DOM = "application.accounts.domain_layer.account.exception"
EV_SUSP = f"{EV_DOM}.account_suspended.AccountSuspended"
EV_UNTIL, EV_DECIDED, EV_REVIEW = f"{EV_SUSP}.blocked_until", f"{EV_SUSP}.decided_at", f"{EV_SUSP}.review_at"
EV_LABEL, EV_CODE, EV_STRIKES = f"{EV_SUSP}.reason_label", f"{EV_SUSP}.reason_code", f"{EV_SUSP}.strikes"
EV_APP = "application.accounts.application_layer.port.login_block.exception.LoginBlocked"
EV_SELECT = ["--scope", "accounts", "--api-module", "spring_dream_server/api.py", "--controller-module", EV_CTRL,
             "--scope-bc", "accounts", "--error-bc", "accounts"]
EV_C1 = "caught exception field read not approved by slot 10"
EV_C2 = "caught exception read outside the approved event-value form"
EV_FWD_D = "caught domain exception forwarding forbidden"
EV_FWD_A = "caught application exception forwarding forbidden"
EV_ARM = "managed catch must directly construct FrameworkErrorSchema and return Status"
EV_OWN_C = "FrameworkErrorSchema construction is not owned by an approved catch/Result arm"
EV_OWN_S = "error Status mapping is not owned by an approved catch/Result arm"
EV_CATCH62 = "catch must be direct own-BC application/domain exception"


def ev_tree(name: str) -> str:
    return f"도메인 예외를 `as {name}` 로 묶어 참조했다 — 입구 파일은 도메인 예외를 «타입»으로만 쓴다"


EV_SUSPENDED_SRC = '''from __future__ import annotations

from datetime import datetime


class AccountSuspended(Exception):
    """정지로 로그인이 막혔다 — 풀리는 때가 없으면 끝 없는 정지다."""

    reason_label: str

    def __init__(
        self,
        blocked_until: datetime | None,
        *,
        decided_at: datetime,
        review_at: datetime | None = None,
        reason_label: str = "policy",
        reason_code: str = "R-1",
        strikes: int = 1,
    ) -> None:
        super().__init__("Account is suspended.")
        self.blocked_until: datetime | None = blocked_until
        self.decided_at: datetime = decided_at
        self.review_at: datetime | None = review_at
        self.reason_label = reason_label
        self.reason_code: str = reason_code
        self.strikes: int = strikes
        self._secret: str = "internal"

    def describe(self) -> str:
        return self.reason_label
'''
EV_LOCKED_SRC = '''from __future__ import annotations


class LockBase(Exception):
    def __init__(self, lock_note: str) -> None:
        super().__init__(lock_note)
        self.lock_note: str = lock_note


class AccountLocked(LockBase):
    """잠긴 계정."""
'''
EV_LOGIN_BLOCKED_SRC = '''from __future__ import annotations

from datetime import datetime


class LoginBlockUnavailable(Exception):
    """service_policy 에 묻지 못했다."""


class LoginBlocked(Exception):
    """로그인이 막혀 있다."""

    def __init__(
        self,
        *,
        blocked_until: datetime | None,
        decided_at: datetime,
        review_at: datetime | None = None,
        reason_label: str = "policy",
        reason_code: str = "R-1",
        strikes: int = 1,
    ) -> None:
        super().__init__("Login is blocked.")
        self.blocked_until: datetime | None = blocked_until
        self.decided_at: datetime = decided_at
        self.review_at: datetime | None = review_at
        self.reason_label: str = reason_label
        self.reason_code: str = reason_code
        self.strikes: int = strikes
        self._secret: str = "internal"

    def describe(self) -> str:
        return self.reason_label


class LoginThrottled(Exception):
    def __init__(self, reason_label: str) -> None:
        super().__init__(reason_label)
        self.reason_label: str = reason_label
'''
EV_ERRORS_SRC = '''from enum import StrEnum
from typing import Literal

from framework.ninja.framework_error_schema import FrameworkErrorSchema


class AccountsErrorCode(StrEnum):
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_SUSPENDED = "account_suspended"
    ACCOUNT_LOCKED = "account_locked"
    LOGIN_BLOCK_MISSING = "login_block_missing"


class AccountsErrorSchema(FrameworkErrorSchema):
    error: AccountsErrorCode


class InvalidCredentialsError(AccountsErrorSchema):
    error: AccountsErrorCode = AccountsErrorCode.INVALID_CREDENTIALS
    message: str = "Credentials are invalid."


class AccountSuspendedError(AccountsErrorSchema):
    error: AccountsErrorCode = AccountsErrorCode.ACCOUNT_SUSPENDED
    message: str = "Account is suspended."


class AccountSuspendedNarrowError(AccountsErrorSchema):
    error: AccountsErrorCode = AccountsErrorCode.ACCOUNT_SUSPENDED
    message: Literal["Account is suspended."] = "Account is suspended."


class AccountLockedError(AccountsErrorSchema):
    error: AccountsErrorCode = AccountsErrorCode.ACCOUNT_LOCKED
    message: str = "Account is locked."


class LoginBlockMissingError(AccountsErrorSchema):
    error: AccountsErrorCode = AccountsErrorCode.LOGIN_BLOCK_MISSING
    message: str = "No login block is recorded."
'''
EV_CONTROLLER = '''from datetime import UTC

from django.http import HttpRequest, HttpResponse
from ninja import Status
from ninja_extra import api_controller, route

from application.accounts.application_layer.account.authenticate_account.authenticate_account_command import (
    AuthenticateAccountCommand,
)
from application.accounts.application_layer.account.authenticate_account.authenticate_account_result import (
    AuthenticateAccountResult,
)
from application.accounts.application_layer.account.authenticate_account.authenticate_account_use_case import (
    AuthenticateAccountUseCase,
)
from application.accounts.composition_root.dependency_wiring import build_authenticate_account_use_case
from application.accounts.domain_layer.account.exception.account_suspended import AccountSuspended
from application.accounts.domain_layer.account.exception.invalid_credentials import InvalidCredentials
from application.accounts.driving_layer.api.account.schema.schema_in import AccountLoginIn
from application.accounts.driving_layer.api.account.schema.schema_out import AccountOut
from application.accounts.driving_layer.api.bc_error_schema import (
    AccountsErrorSchema,
    AccountSuspendedError,
    InvalidCredentialsError,
)
__IMPORTS__
_LOGIN_BLOCKED_REASON_HEADER: str = "Login-Blocked-Reason"
_LOGIN_BLOCKED_UNTIL_HEADER: str = "Login-Blocked-Until"
__MODULE__

@api_controller("/accounts", tags=["accounts"], auto_import=False)
class AccountController:
    """계정 자원의 HTTP 입구."""

    @route.post(
        "/sessions",
        response={200: AccountOut, 403: InvalidCredentialsError | AccountSuspendedError},
        summary="로그인",
    )
    def create_session(
        self,
        request: HttpRequest,
        response: HttpResponse,
        payload: AccountLoginIn,
    ) -> AccountOut | Status[AccountsErrorSchema]:
        command: AuthenticateAccountCommand = AuthenticateAccountCommand(email=payload.email, password=payload.password)
        use_case: AuthenticateAccountUseCase = build_authenticate_account_use_case()
__PRE__        try:
            result: AuthenticateAccountResult = use_case.execute(command)
        except InvalidCredentials:
            invalid_credentials: AccountsErrorSchema = InvalidCredentialsError()
            return Status(403, invalid_credentials)
__ARM__        return AccountOut(account_id=result.account_id, email=result.email)
__OPS__'''
EV_STATIC_ARM = '''suspended_error: AccountsErrorSchema = AccountSuspendedError()
response[_LOGIN_BLOCKED_REASON_HEADER] = "account_suspended"
return Status(403, suspended_error)
'''


def ev_arm(body: str, head: str = "AccountSuspended as suspended") -> str:
    return f"        except {head}:\n" + textwrap.indent(textwrap.dedent(body), " " * 12)


def ev_controller(arm: str | None = None, imports: str = "", module: str = "", pre: str = "", ops: str = "") -> str:
    return (EV_CONTROLLER.replace("__ARM__", ev_arm(EV_STATIC_ARM) if arm is None else arm)
            .replace("__IMPORTS__\n", imports).replace("__MODULE__\n", module)
            .replace("__PRE__", pre).replace("__OPS__", ops))


EV_BASE = {
    "spring_dream_server/__init__.py": "",
    "spring_dream_server/api.py": 'from ninja_extra import NinjaExtraAPI\n\napi: NinjaExtraAPI = NinjaExtraAPI(urls_namespace="api")\n',
    "framework/__init__.py": "",
    "framework/ninja/__init__.py": "",
    "framework/ninja/framework_error_schema.py":
        "from ninja import Schema\n\n\nclass FrameworkErrorSchema(Schema):\n    error: str\n    message: str\n",
    "application/__init__.py": "",
    f"{EV_A}/__init__.py": "",
    f"{EV_A}/domain_layer/__init__.py": "",
    f"{EV_A}/domain_layer/account/__init__.py": "",
    f"{EV_EXC_DIR}/__init__.py": "",
    f"{EV_EXC_DIR}/account_suspended.py": EV_SUSPENDED_SRC,
    f"{EV_EXC_DIR}/account_locked.py": EV_LOCKED_SRC,
    f"{EV_EXC_DIR}/invalid_credentials.py": "class InvalidCredentials(Exception):\n    pass\n",
    f"{EV_A}/application_layer/__init__.py": "",
    f"{EV_A}/application_layer/account/__init__.py": "",
    f"{EV_A}/application_layer/account/authenticate_account/__init__.py": "",
    f"{EV_A}/application_layer/account/authenticate_account/authenticate_account_command.py":
        "class AuthenticateAccountCommand:\n    pass\n",
    f"{EV_A}/application_layer/account/authenticate_account/authenticate_account_result.py":
        "class AuthenticateAccountResult:\n    pass\n",
    f"{EV_A}/application_layer/account/authenticate_account/authenticate_account_use_case.py":
        "class AuthenticateAccountUseCase:\n    pass\n",
    f"{EV_A}/application_layer/port/__init__.py": "",
    f"{EV_A}/application_layer/port/login_block/__init__.py": "",
    EV_PORT_EXC: EV_LOGIN_BLOCKED_SRC,
    f"{EV_A}/composition_root/__init__.py": "",
    f"{EV_A}/composition_root/dependency_wiring.py": "def build_authenticate_account_use_case():\n    return None\n",
    f"{EV_A}/driving_layer/__init__.py": "",
    f"{EV_A}/driving_layer/api/__init__.py": "",
    f"{EV_A}/driving_layer/api/bc_error_schema.py": EV_ERRORS_SRC,
    f"{EV_A}/driving_layer/api/account/__init__.py": "",
    f"{EV_A}/driving_layer/api/account/schema/__init__.py": "",
    f"{EV_A}/driving_layer/api/account/schema/schema_in.py":
        "from ninja import Schema\n\n\nclass AccountLoginIn(Schema):\n    email: str\n    password: str\n",
    f"{EV_A}/driving_layer/api/account/schema/schema_out.py":
        "from ninja import Schema\n\n\nclass AccountOut(Schema):\n    account_id: int\n    email: str\n",
    EV_CTRL: ev_controller(),
}
EV_APP_IMPORT = "from application.accounts.application_layer.port.login_block.exception import LoginBlocked\n"
EV_LOCKED_IMPORT = "from application.accounts.domain_layer.account.exception.account_locked import AccountLocked\n"


def ev_app(arm: str) -> str:
    """같은 꼴을 응용 예외(포트 예외 LoginBlocked)로 — C2 를 보는 판."""
    return arm.replace("AccountSuspended as suspended", "LoginBlocked as blocked").replace("suspended.", "blocked.")


def ev_files(arm: str | None = None, *, imports: str = "", module: str = "", pre: str = "", ops: str = "",
             app: bool = False, **extra: str) -> dict[str, str]:
    """사례 하나의 덮어쓰기 — 컨트롤러 본문 + 그 밖의 파일(경로=키)."""
    if app and arm is not None:
        arm = ev_app(arm)
        imports = EV_APP_IMPORT + imports
    files = {EV_CTRL: ev_controller(arm, imports=imports, module=module, pre=pre, ops=ops)}
    files.update({path.replace("__", "/"): text for path, text in extra.items()})
    return files


# P1 레인 꼴(꼴 2) — 값 있는 가지만 값을 읽고 else 는 다른 정적 문구.
EV_P1 = '''if suspended.blocked_until is not None:
    until_error: AccountsErrorSchema = AccountSuspendedError(
        message=f"Account is suspended until {suspended.blocked_until.astimezone(UTC).isoformat()}."
    )
    response[_LOGIN_BLOCKED_REASON_HEADER] = "account_suspended"
    response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.blocked_until.astimezone(UTC).isoformat()
    return Status(403, until_error)
else:
    indefinite_error: AccountsErrorSchema = AccountSuspendedError(message="Account is suspended indefinitely.")
    response[_LOGIN_BLOCKED_REASON_HEADER] = "account_suspended"
    return Status(403, indefinite_error)
'''


def ev_form2(present: str, absent: str, test: str = "suspended.blocked_until is not None") -> str:
    return (f"if {test}:\n" + textwrap.indent(textwrap.dedent(present), "    ")
            + "else:\n" + textwrap.indent(textwrap.dedent(absent), "    "))


EV_PRESENT_STATIC = '''until_error: AccountsErrorSchema = AccountSuspendedError()
response[_LOGIN_BLOCKED_REASON_HEADER] = "account_suspended"
return Status(403, until_error)
'''
EV_ABSENT_STATIC = '''indefinite_error: AccountsErrorSchema = AccountSuspendedError(message="Account is suspended indefinitely.")
response[_LOGIN_BLOCKED_REASON_HEADER] = "account_suspended"
return Status(403, indefinite_error)
'''
EV_OWN4 = [("-", "until_error: AccountsErrorSchema", EV_OWN_C), ("-", "return Status(403, until_error)", EV_OWN_S),
           ("-", "indefinite_error: AccountsErrorSchema", EV_OWN_C), ("-", "return Status(403, indefinite_error)", EV_OWN_S)]
EV_OWN2 = [("-", "suspended_error: AccountsErrorSchema", EV_OWN_C), ("-", "return Status(403, suspended_error)", EV_OWN_S)]


def ev_single(ctor_kw: str = "", headers: tuple[str, ...] = (), extra: tuple[str, ...] = ()) -> str:
    lines = [f"suspended_error: AccountsErrorSchema = AccountSuspendedError({ctor_kw})", *extra,
             'response[_LOGIN_BLOCKED_REASON_HEADER] = "account_suspended"', *headers,
             "return Status(403, suspended_error)"]
    return "\n".join(lines) + "\n"


# 사례 표 — 이름 → (덮어쓸 파일, --event-value 목록, 실행별 기대). 기대: 실행 → (exit, [(tag, 표지, category[, 경로])])
# tag "#474" · "#62" = violation, "-" = 08-04 계약. 표지가 가리키는 행의 원문이 그 줄의 끝이다(트리 #474 는 원문 없음).
# 실행: auto = `--error-profile auto` · cj = code-json(+flag) · bl = code-json(+flag) --anchor-baseline · pre = preserve(flag 없음 — usage 기대 사례만 flag).
# usage 기대는 (1, "stderr 조각").
T474 = ev_tree("suspended")
EV_CASES: dict[str, tuple[dict[str, str], list[str], dict[str, tuple[int, object]]]] = {
    "base": (ev_files(), [], {"auto": (0, []), "cj": (0, []), "bl": (0, []), "pre": (0, [])}),
    "P1": (ev_files(ev_arm(EV_P1)), [EV_UNTIL], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P2": (ev_files(ev_arm('''until_error: AccountsErrorSchema = AccountSuspendedError(
    message=f"Account is suspended until {suspended.blocked_until.astimezone(UTC).isoformat()}."
)
response[_LOGIN_BLOCKED_REASON_HEADER] = "account_suspended"
response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.blocked_until.astimezone(UTC).isoformat()
return Status(403, until_error)
''', head="AccountSuspendedUntil as suspended") + ev_arm('''indefinite_error: AccountsErrorSchema = AccountSuspendedError(message="Account is suspended indefinitely.")
response[_LOGIN_BLOCKED_REASON_HEADER] = "account_suspended"
return Status(403, indefinite_error)
''', head="AccountSuspendedIndefinitely"),
        imports="from application.accounts.domain_layer.account.exception.account_suspended_indefinitely import (\n"
                "    AccountSuspendedIndefinitely,\n)\n"
                "from application.accounts.domain_layer.account.exception.account_suspended_until import AccountSuspendedUntil\n",
        **{f"{EV_EXC_DIR}/account_suspended_until.py": '''from __future__ import annotations

from datetime import datetime


class AccountSuspendedUntil(Exception):
    def __init__(self, blocked_until: datetime) -> None:
        super().__init__("Account is suspended.")
        self.blocked_until: datetime = blocked_until
''', f"{EV_EXC_DIR}/account_suspended_indefinitely.py": '''from __future__ import annotations


class AccountSuspendedIndefinitely(Exception):
    """끝 없는 정지."""
'''}), [f"{EV_DOM}.account_suspended_until.AccountSuspendedUntil.blocked_until"],
        {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P3": (ev_files(ev_arm(ev_single(headers=(
        "response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.decided_at.astimezone(UTC).isoformat()",)))),
        [EV_DECIDED], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P4": (ev_files(ev_arm(ev_single('message="Account is suspended for now."'), head="AccountSuspended")),
           [], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P5": (ev_files(ev_arm(ev_single("message=suspended.reason_label", headers=(
        'response["Login-Blocked-Label"] = suspended.reason_label',)))),
        [EV_LABEL], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P6": (ev_files(ev_arm(ev_single('message=f"Suspended after {suspended.strikes} strikes."', headers=(
        'response["Login-Strikes"] = f"{suspended.strikes}"',)))),
        [EV_STRIKES], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P7": (ev_files(ev_arm('''suspended_error: AccountsErrorSchema = AccountsErrorSchema(
    error=AccountsErrorCode.ACCOUNT_SUSPENDED,
    message=f"Account was suspended at {suspended.decided_at.astimezone(UTC).isoformat()}.",
)
return Status(403, suspended_error)
'''), imports="from application.accounts.driving_layer.api.bc_error_schema import AccountsErrorCode\n"),
        [EV_DECIDED], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P9": (ev_files(ev_arm(EV_P1), app=True), [f"{EV_APP}.blocked_until"],
           {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P10": ({EV_CTRL: ev_controller(ev_arm(ev_single(headers=(
        "response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.decided_at.astimezone(UTC).isoformat()",)),
        head="Suspended as suspended")).replace(
        "account_suspended import AccountSuspended\n", "account_suspended import AccountSuspended as Suspended\n")},
        [EV_DECIDED], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P11": ({EV_CTRL: ev_controller(ev_arm(ev_single(headers=(
        "response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.decided_at.astimezone(Z).isoformat()",)))).replace(
        "from datetime import UTC\n", "from datetime import UTC as Z\n"),
        f"{EV_EXC_DIR}/account_suspended.py": EV_SUSPENDED_SRC.replace(
            "from datetime import datetime\n", "from datetime import datetime as dt\n").replace(
            "self.decided_at: datetime = decided_at", "self.decided_at: dt = decided_at").replace(
            "decided_at: datetime,", "decided_at: dt,").replace("datetime | None", "dt | None")},
        [EV_DECIDED], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P12": (ev_files(ev_arm(ev_single(
        'message=f"Account was suspended at {suspended.decided_at.astimezone(UTC).isoformat()}."', headers=(
            "response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.decided_at.astimezone(UTC).isoformat()",)))),
        [EV_DECIDED], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P13": (ev_files(imports="from application.accounts.driving_layer.api.bc_error_schema import LoginBlockMissingError\n",
                     ops='''
    @route.get("/me/login-block", response={200: AccountOut, 404: LoginBlockMissingError}, summary="내 로그인 막힘")
    def get_my_login_block(self, request: HttpRequest) -> AccountOut | Status[AccountsErrorSchema]:
        use_case: AuthenticateAccountUseCase = build_authenticate_account_use_case()
        result: AccountOut | None = use_case.find()
        if result is None:
            missing: AccountsErrorSchema = LoginBlockMissingError(message="No login block is recorded yet.")
            return Status(404, missing)
        return result
'''), [], {"cj": (0, []), "bl": (0, [])}),
    # P17 — 꼴 2 에서 값이 늘 있는 다른 승인 필드(`reason_label: str`)는 두 가지 어디서든 읽는다(R-3655 — 값 있는 가지에 묶이는
    # 것은 검사식이 본 `T | None` 필드뿐 · 그 음성은 N12k).
    "P17": (ev_files(ev_arm(ev_form2('''until_error: AccountsErrorSchema = AccountSuspendedError(
    message=f"Account is suspended until {suspended.blocked_until.astimezone(UTC).isoformat()}."
)
response[_LOGIN_BLOCKED_REASON_HEADER] = suspended.reason_label
response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.blocked_until.astimezone(UTC).isoformat()
return Status(403, until_error)
''', '''indefinite_error: AccountsErrorSchema = AccountSuspendedError(message=suspended.reason_label)
response[_LOGIN_BLOCKED_REASON_HEADER] = suspended.reason_label
return Status(403, indefinite_error)
'''))), [EV_UNTIL, EV_LABEL], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    # ── 음성(변종 하나씩) ───────────────────────────────────────────────────────────────────
    "N1": (ev_files(ev_arm(ev_single("message=str(suspended)"))), [],
           {"auto": (2, [("#474", "message=str(suspended)", T474)]),
            "cj": (2, [("#474", "message=str(suspended)", T474)]),
            "bl": (2, [("#474", "except AccountSuspended as suspended", EV_FWD_D),
                       ("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2])}),
    "N2": (ev_files(ev_arm(ev_single("message=suspended"))), [],
           {"auto": (2, [("#474", "message=suspended)", T474)]),
            "bl": (2, [("#474", "except AccountSuspended as suspended", EV_FWD_D),
                       ("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2])}),
    "N3": (ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Code"] = suspended.reason_code',)))), [EV_UNTIL],
           {"auto": (0, []), "cj": (2, [("#474", "suspended.reason_code", EV_C1)]),
            "bl": (2, [("#474", "suspended.reason_code", EV_C1)])}),
    "N4": (ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = suspended.reason_label',)))), [],
           {"auto": (0, []), "cj": (2, [("#474", "suspended.reason_label", EV_C1)]),
            "bl": (2, [("#474", "suspended.reason_label", EV_C1)])}),
}


def _ev_out_of_form(name: str, header_value: str, *, extra_bl: tuple = (), app_extra: tuple = (),
                    imports: str = "") -> None:
    """머리 값 자리의 꼴 밖 읽기 한 변종 — 도메인 판(트리 #474) · 응용 판(C2) 둘."""
    arm = ev_arm(ev_single(headers=(f'response["Login-Blocked-X"] = {header_value}',)))
    EV_CASES[name] = (ev_files(arm, imports=imports), [EV_LABEL],
                      {"auto": (2, [("#474", header_value, T474)]), "cj": (2, [("#474", header_value, T474)]),
                       "bl": (2, [("#474", header_value, T474), *extra_bl])})
    app_value = header_value.replace("suspended.", "blocked.")
    EV_CASES[name + "-app"] = (ev_files(arm, app=True, imports=imports), [f"{EV_APP}.reason_label"],
                               {"auto": (0, []), "cj": (2, [("-", app_value, EV_C2), *app_extra]),
                                "bl": (2, [("-", app_value, EV_C2), *app_extra])})


EV_HEADER_CALL = (("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2)
EV_HEADER_CALL_APP = (("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2)
_ev_out_of_form("N5a", "suspended.args")
_ev_out_of_form("N5b", "suspended._secret")
_ev_out_of_form("N5c", "suspended.__dict__")
_ev_out_of_form("N5d", "suspended.describe()", extra_bl=EV_HEADER_CALL, app_extra=EV_HEADER_CALL_APP)
_ev_out_of_form("N9a", "suspended.decided_at.isoformat()", extra_bl=EV_HEADER_CALL, app_extra=EV_HEADER_CALL_APP)
_ev_out_of_form("N9b", 'suspended.decided_at.strftime("%Y-%m-%d")', extra_bl=EV_HEADER_CALL,
                app_extra=EV_HEADER_CALL_APP)
_ev_out_of_form("N9c", "suspended.decided_at.astimezone(timezone.utc).isoformat()", extra_bl=EV_HEADER_CALL,
                app_extra=EV_HEADER_CALL_APP, imports="from datetime import timezone\n")
_ev_out_of_form("N12l", "suspended.blocked_until.astimezone(UTC).isoformat()", extra_bl=EV_HEADER_CALL,
                app_extra=EV_HEADER_CALL_APP)
EV_CASES["N18"] = (ev_files(ev_arm(ev_single(headers=('response[suspended.reason_label] = "y"',)))), [EV_LABEL],
                   {"auto": (2, [("#474", "response[suspended.reason_label]", T474)]),
                    "bl": (2, [("#474", "response[suspended.reason_label]", T474)])})
EV_CASES["N18-app"] = (ev_files(ev_arm(ev_single(headers=('response[suspended.reason_label] = "y"',))), app=True),
                       [f"{EV_APP}.reason_label"],
                       {"auto": (0, []), "cj": (2, [("-", "response[blocked.reason_label]", EV_C2)])})


def _ev_message_out_of_form(name: str, message: str, marker: str) -> None:
    """설명 keyword 자리의 꼴 밖 읽기 — 도메인 판은 수집 실행에서 forwarding · ⑶ · ⑹, 응용 판은 C2 + 같은 줄들."""
    arm = ev_arm(ev_single(f"message={message}"))
    EV_CASES[name] = (ev_files(arm, module="\n\ndef _fmt(value: object) -> str:\n    return str(value)\n"), [EV_LABEL],
                      {"auto": (2, [("#474", marker, T474)]), "cj": (2, [("#474", marker, T474)]),
                       "bl": (2, [("#474", "except AccountSuspended as suspended", EV_FWD_D),
                                  ("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2])})
    EV_CASES[name + "-app"] = (
        ev_files(arm, app=True, module="\n\ndef _fmt(value: object) -> str:\n    return str(value)\n"),
        [f"{EV_APP}.reason_label"],
        {"auto": (0, []),
         "cj": (2, [("-", marker.replace("suspended", "blocked"), EV_C2), ("-", "except LoginBlocked as blocked", EV_FWD_A),
                    ("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2])})


_ev_message_out_of_form("N8", "_fmt(suspended.decided_at)", "_fmt(suspended.decided_at)")
_ev_message_out_of_form("N10b", 'f"{suspended.reason_label!s}"', "reason_label!s")
_ev_message_out_of_form("N10c", 'f"{suspended.reason_label!r}"', "reason_label!r")
_ev_message_out_of_form("N10d", 'f"{suspended.decided_at:%Y}"', "decided_at:%Y")
_ev_message_out_of_form("N10e", 'f"{suspended.strikes + 1}"', "strikes + 1")
_ev_message_out_of_form("N10f", '"Suspended: " + suspended.reason_label', '"Suspended: " + suspended.reason_label')

EV_CASES.update({
    "N6": (ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Note"] = failed.note',)),
                           head="PaymentFailed as failed").replace("suspended_error", "failed_error"),
                    imports="from application.billing.domain_layer.payment.exception.payment_failed import PaymentFailed\n",
                    **{"application/billing/__init__.py": "", "application/billing/domain_layer/__init__.py": "",
                       "application/billing/domain_layer/payment/__init__.py": "",
                       "application/billing/domain_layer/payment/exception/__init__.py": "",
                       "application/billing/domain_layer/payment/exception/payment_failed.py":
                           "class PaymentFailed(Exception):\n    def __init__(self, note: str) -> None:\n"
                           "        super().__init__(note)\n        self.note: str = note\n"}), [],
           {"auto": (2, [("#474", "failed.note", ev_tree("failed"))]),
            "bl": (2, [("#474", "failed.note", ev_tree("failed")),
                       ("#62", "except PaymentFailed as failed", EV_CATCH62)])}),
    "N7a": (ev_files(ev_arm('''suspended_error: AccountsErrorSchema = AccountsErrorSchema(error=suspended.reason_code, message="Account is suspended.")
return Status(403, suspended_error)
'''), imports="from application.accounts.driving_layer.api.bc_error_schema import AccountsErrorCode\n"), [EV_CODE],
        {"auto": (0, []),
         "cj": (2, [("#474", "except AccountSuspended as suspended", EV_FWD_D),
                    ("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2])}),
    "N7b": (ev_files(ev_arm(ev_single("error=AccountsErrorCode.ACCOUNT_SUSPENDED"), head="AccountSuspended"),
                     imports="from application.accounts.driving_layer.api.bc_error_schema import AccountsErrorCode\n"),
            [], {"auto": (0, []), "cj": (2, [("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2])}),
    "N10a": (ev_files(ev_arm(ev_single('message=f"{suspended.reason_label} / {suspended.reason_code}"'))), [EV_LABEL],
             {"auto": (0, []), "cj": (2, [("#474", "suspended_error: AccountsErrorSchema", EV_C1)])}),
    "N11": (ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = suspended.reason_label',)),
                            head="(AccountSuspended, AccountLocked) as suspended"), imports=EV_LOCKED_IMPORT),
            [EV_LABEL], {"auto": (2, [("#474", "= suspended.reason_label", T474)]),
                         "bl": (2, [("#474", "= suspended.reason_label", T474)])}),
    "N11-app": (ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = blocked.reason_label',)),
                                head="(LoginBlocked, LoginThrottled) as blocked"),
                         imports="from application.accounts.application_layer.port.login_block.exception import (\n"
                                 "    LoginBlocked,\n    LoginThrottled,\n)\n"),
                [f"{EV_APP}.reason_label"], {"auto": (0, []), "cj": (2, [("-", "= blocked.reason_label", EV_C2)])}),
    "N12a": (ev_files(ev_arm(ev_form2(EV_PRESENT_STATIC, EV_ABSENT_STATIC, "suspended.blocked_until is None"))),
             [EV_UNTIL], {"auto": (2, [("#474", "if suspended.blocked_until is None", T474)]),
                          "bl": (2, [("#474", "if suspended.blocked_until is None", T474),
                                     ("-", "if suspended.blocked_until is None", EV_ARM), *EV_OWN4])}),
    "N12b": (ev_files(ev_arm(ev_form2(EV_PRESENT_STATIC, EV_ABSENT_STATIC, "suspended.blocked_until"))),
             [EV_UNTIL], {"auto": (2, [("#474", "if suspended.blocked_until:", T474)]),
                          "bl": (2, [("#474", "if suspended.blocked_until:", T474),
                                     ("-", "if suspended.blocked_until:", EV_ARM), *EV_OWN4])}),
    "N12c": (ev_files(ev_arm('''if suspended.blocked_until is not None:
    until_error: AccountsErrorSchema = AccountSuspendedError()
    return Status(403, until_error)
elif suspended.review_at is not None:
    review_error: AccountsErrorSchema = AccountSuspendedError()
    return Status(403, review_error)
else:
    indefinite_error: AccountsErrorSchema = AccountSuspendedError()
    return Status(403, indefinite_error)
''')), [EV_UNTIL, EV_REVIEW],
        {"auto": (2, [("#474", "if suspended.blocked_until is not None", T474)]),
         "bl": (2, [("#474", "if suspended.blocked_until is not None", T474),
                    ("-", "if suspended.blocked_until is not None", EV_ARM), *EV_OWN4,
                    ("-", "review_error: AccountsErrorSchema", EV_OWN_C),
                    ("-", "return Status(403, review_error)", EV_OWN_S)])}),
    "N12d": (ev_files(ev_arm(ev_form2('''until_error: AccountsErrorSchema = AccountSuspendedError()
if _NOTICE:
    response["Login-Notice"] = "yes"
return Status(403, until_error)
''', EV_ABSENT_STATIC)), module="_NOTICE: bool = True\n"), [EV_UNTIL],
        {"auto": (0, []), "cj": (2, [("-", "if suspended.blocked_until is not None", EV_ARM), *EV_OWN4])}),
    "N12e": (ev_files(ev_arm('''if suspended.blocked_until is not None:
    until_error: AccountsErrorSchema = AccountSuspendedError()
    return Status(403, until_error)
indefinite_error: AccountsErrorSchema = AccountSuspendedError()
return Status(403, indefinite_error)
''')), [EV_UNTIL], {"auto": (2, [("#474", "if suspended.blocked_until is not None", T474)]),
                     "bl": (2, [("#474", "if suspended.blocked_until is not None", T474),
                                ("-", "if suspended.blocked_until is not None", EV_ARM), *EV_OWN4])}),
    "N12f": (ev_files(ev_arm(ev_form2(EV_PRESENT_STATIC, EV_ABSENT_STATIC.replace(
        'AccountSuspendedError(message="Account is suspended indefinitely.")', "AccountLockedError()"))),
        imports="from application.accounts.driving_layer.api.bc_error_schema import AccountLockedError\n"), [EV_UNTIL],
        {"auto": (0, []), "cj": (2, [("-", "if suspended.blocked_until is not None", EV_ARM), *EV_OWN4])}),
    "N12g": (ev_files(ev_arm(ev_form2(EV_PRESENT_STATIC, EV_ABSENT_STATIC.replace(
        "return Status(403, indefinite_error)", "return Status(409, indefinite_error)")))), [EV_UNTIL],
        {"auto": (0, []), "cj": (2, [("-", "if suspended.blocked_until is not None", EV_ARM), *EV_OWN4[:3],
                                     ("-", "return Status(409, indefinite_error)", EV_OWN_S)])}),
    "N12h": (ev_files(ev_arm(ev_form2(
        'until_error: AccountsErrorSchema = AccountsErrorSchema(error=AccountsErrorCode.ACCOUNT_SUSPENDED, message="a")\n'
        "return Status(403, until_error)\n",
        'indefinite_error: AccountsErrorSchema = AccountsErrorSchema(error=AccountsErrorCode.ACCOUNT_LOCKED, message="b")\n'
        "return Status(403, indefinite_error)\n")),
        imports="from application.accounts.driving_layer.api.bc_error_schema import AccountsErrorCode\n"), [EV_UNTIL],
        {"auto": (0, []), "cj": (2, [("-", "if suspended.blocked_until is not None", EV_ARM), *EV_OWN4])}),
    "N12i": (ev_files(ev_arm(ev_form2(EV_PRESENT_STATIC, EV_ABSENT_STATIC, "suspended.review_at is not None"))),
             [EV_UNTIL], {"auto": (0, []), "cj": (2, [("#474", "if suspended.review_at is not None", EV_C1)])}),
    "N12j": (ev_files(ev_arm(ev_form2(EV_PRESENT_STATIC, EV_ABSENT_STATIC, "suspended.decided_at is not None"))),
             [EV_DECIDED], {"auto": (2, [("#474", "if suspended.decided_at is not None", T474)]),
                            "bl": (2, [("#474", "if suspended.decided_at is not None", T474),
                                       ("-", "if suspended.decided_at is not None", EV_ARM), *EV_OWN4])}),
    "N12k": (ev_files(ev_arm(ev_form2(EV_PRESENT_STATIC, '''indefinite_error: AccountsErrorSchema = AccountSuspendedError(
    message=f"Until {suspended.blocked_until.astimezone(UTC).isoformat()}."
)
return Status(403, indefinite_error)
'''))), [EV_UNTIL], {"auto": (2, [("#474", 'message=f"Until', T474)]),
                     "bl": (2, [("#474", "except AccountSuspended as suspended", EV_FWD_D),
                                ("-", "if suspended.blocked_until is not None", EV_ARM), *EV_OWN4])}),
    "N12m": (ev_files(ev_arm(ev_form2(EV_PRESENT_STATIC, EV_ABSENT_STATIC, "_present(suspended)")),
                      module="\n\ndef _present(value: object) -> bool:\n    return value is not None\n"), [EV_UNTIL],
             {"auto": (2, [("#474", "if _present(suspended)", T474)]),
              "bl": (2, [("#474", "except AccountSuspended as suspended", EV_FWD_D),
                         ("-", "if _present(suspended)", EV_ARM), *EV_OWN4])}),
    # 덧붙임 1 ③ — 검사식이 본 필드가 아닌 별개 optional 필드를 값 있는 가지에서 읽는다
    "N12n": (ev_files(ev_arm(ev_form2('''until_error: AccountsErrorSchema = AccountSuspendedError()
response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.review_at.astimezone(UTC).isoformat()
return Status(403, until_error)
''', EV_ABSENT_STATIC))), [EV_UNTIL, EV_REVIEW],
        {"auto": (2, [("#474", "suspended.review_at.astimezone", T474)]),
         "bl": (2, [("#474", "suspended.review_at.astimezone", T474),
                    ("-", "if suspended.blocked_until is not None", EV_ARM), *EV_OWN4])}),
    "N13": (ev_files(ev_arm(ev_single(extra=("label_text: str = suspended.reason_label",)))), [EV_LABEL],
            {"auto": (2, [("#474", "label_text: str = suspended.reason_label", T474)]),
             "bl": (2, [("#474", "label_text: str = suspended.reason_label", T474),
                        ("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2])}),
    "N15": (ev_files(ev_arm(ev_single('message="Account is suspended."').replace(
        "AccountSuspendedError(", "AccountSuspendedNarrowError("), head="AccountSuspended"),
        imports="from application.accounts.driving_layer.api.bc_error_schema import AccountSuspendedNarrowError\n"), [],
        {"auto": (0, []), "cj": (2, [("-", "suspended_error: AccountsErrorSchema", EV_ARM),
                                     ("-", "suspended_error: AccountsErrorSchema", EV_OWN_C),
                                     ("-", "return Status(403, suspended_error)", EV_OWN_S)])}),
    # N16a · N16b — «꼴 맞는» managed catch 꼴(route 데코 operation · 생성 → 머리 → 반환)이어도 OHS · webhook 은 비켜 주지 않는다.
    "N16a": (ev_files(**{EV_OHS: '''from datetime import UTC

from django.http import HttpResponse
from ninja import Router, Status

from application.accounts.domain_layer.account.exception.account_suspended import AccountSuspended
from application.accounts.driving_layer.api.bc_error_schema import AccountsErrorSchema, AccountSuspendedError

router = Router()


@router.get("/login-block")
def find_login_block_query(request: object, response: HttpResponse) -> dict[str, str] | Status[AccountsErrorSchema]:
    try:
        return {}
    except AccountSuspended as suspended:
        suspended_error: AccountsErrorSchema = AccountSuspendedError()
        response["Login-Blocked-Until"] = suspended.decided_at.astimezone(UTC).isoformat()
        return Status(403, suspended_error)
''', f"{EV_A}/driving_layer/open_host_service/__init__.py": "",
        f"{EV_A}/driving_layer/open_host_service/session_user/__init__.py": ""}), [EV_DECIDED],
        {"auto": (2, [("#474", "suspended.decided_at", T474, EV_OHS)]),
         "cj": (2, [("#474", "suspended.decided_at", T474, EV_OHS)]),
         "bl": (2, [("#474", "suspended.decided_at", T474, EV_OHS)])}),
    "N16b": (ev_files(**{EV_HOOK: '''from datetime import UTC

from django.http import HttpRequest, HttpResponse
from ninja import Status
from ninja_extra import api_controller, route

from application.accounts.domain_layer.account.exception.account_suspended import AccountSuspended
from application.accounts.driving_layer.api.bc_error_schema import AccountsErrorSchema, AccountSuspendedError


@api_controller("/webhooks/provider", auto_import=False)
class ProviderController:
    @route.post("/events", response={200: dict, 403: AccountSuspendedError})
    def handle_provider_event(
        self, request: HttpRequest, response: HttpResponse
    ) -> dict[str, str] | Status[AccountsErrorSchema]:
        try:
            self.accept(request)
        except AccountSuspended as suspended:
            suspended_error: AccountsErrorSchema = AccountSuspendedError()
            response["Login-Blocked-Until"] = suspended.decided_at.astimezone(UTC).isoformat()
            return Status(403, suspended_error)
        return {}
''', f"{EV_A}/driving_layer/api/webhook/__init__.py": "",
        f"{EV_A}/driving_layer/api/webhook/provider/__init__.py": ""}), [EV_DECIDED],
        {"auto": (2, [("#474", "suspended.decided_at", T474, EV_HOOK)]),
         "cj": (2, [("#474", "suspended.decided_at", T474, EV_HOOK)])}),
    "N17a": (ev_files(), [EV_UNTIL], {"auto": (1, "auto profile에는 selector를 전달하지 않음")}),
    "N17b": (ev_files(), [EV_UNTIL], {"pre": (1, "preserve-established profile에는 --event-value 를 전달하지 않음")}),
    "N17c": (ev_files(), ["application.billing.domain_layer.payment.exception.payment_failed.PaymentFailed.note"],
             {"cj": (1, "--event-value 의 BC 가 --error-bc 밖: application.billing.")}),
    "N17d1": (ev_files(), [f"{EV_DOM}.account_suspended._Hidden.blocked_until"],
              {"cj": (1, "잘못된 --event-value: application.accounts.domain_layer.account.exception.account_suspended._Hidden.")}),
    "N17d2": (ev_files(), [f"{EV_SUSP}._secret"], {"cj": (1, f"잘못된 --event-value: {EV_SUSP}._secret")}),
    "N17e": (ev_files(), [EV_UNTIL, EV_UNTIL], {"cj": (1, "반복 인자 중복: --event-value")}),
    "N17f1": (ev_files(), ["application.accounts.domain_layer.blocked_until"],
              {"cj": (1, "잘못된 --event-value: application.accounts.domain_layer.blocked_until")}),
    "N17f2": (ev_files(), ["application.accounts.driving_layer.api.AccountSuspendedError.message"],
              {"cj": (1, "잘못된 --event-value: application.accounts.driving_layer.api.")}),
    "N19": (ev_files(ev_arm(ev_single(headers=("response[header_name] = suspended.reason_label",))),
                     pre="        header_name: str = payload.email\n"), [EV_LABEL],
            {"auto": (0, []), "cj": (2, [("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2])}),
    "N20a": (ev_files(ev_arm(ev_single(headers=(
        "response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.decided_at.astimezone(UTC).isoformat()",))),
        imports="from datetime import timezone\n", pre="        UTC = timezone.utc\n"), [EV_DECIDED],
        {"auto": (2, [("#474", "suspended.decided_at.astimezone(UTC)", T474)]),
         "bl": (2, [("#474", "suspended.decided_at.astimezone(UTC)", T474), *EV_HEADER_CALL])}),
    "N20b": (ev_files(ev_arm(ev_single(headers=(
        "response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.decided_at.astimezone(UTC).isoformat()",))),
        imports="from datetime import timezone\n", module="UTC = timezone.utc\n"), [EV_DECIDED],
        {"auto": (2, [("#474", "suspended.decided_at.astimezone(UTC)", T474)]),
         "bl": (2, [("#474", "suspended.decided_at.astimezone(UTC)", T474), *EV_HEADER_CALL])}),
    "N23": (ev_files(ev_arm(ev_single(headers=(
        "response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.decided_at.astimezone(UTC).isoformat()",))),
        **{f"{EV_EXC_DIR}/account_suspended.py": EV_SUSPENDED_SRC.replace(
            "from datetime import datetime\n", "from datetime import datetime\n\nInstant = datetime\n").replace(
            "self.decided_at: datetime = decided_at", "self.decided_at: Instant = decided_at")}), [EV_DECIDED],
        {"auto": (2, [("#474", "suspended.decided_at.astimezone(UTC)", T474)]),
         "bl": (2, [("#474", "suspended.decided_at.astimezone(UTC)", T474), *EV_HEADER_CALL])}),
    "N24": (ev_files(ev_arm(ev_single(headers=(
        "response[_LOGIN_BLOCKED_UNTIL_HEADER] = suspended.decided_at.astimezone(UTC).isoformat()",)))), [],
        {"pre": (2, [("#474", "suspended.decided_at.astimezone(UTC)", T474)])}),
    "N26": (ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = blocked.reason_label',)),
                            head="LoginBlocked as blocked"),
                     imports="from application.accounts.application_layer.account.authenticate_account.authenticate_account_use_case import LoginBlocked\n",
                     **{f"{EV_A}/application_layer/account/authenticate_account/authenticate_account_use_case.py":
                        "from application.accounts.application_layer.port.login_block.exception import LoginBlocked\n\n\n"
                        "class AuthenticateAccountUseCase:\n    pass\n"}),
            [f"{EV_APP}.reason_label"], {"auto": (0, []), "cj": (2, [("-", "= blocked.reason_label", EV_C2)])}),
    "N27": (ev_files(ev_arm(ev_single(headers=('response["Login-Lock-Note"] = locked.lock_note',)),
                            head="AccountLocked as locked").replace("suspended_error", "locked_error"),
                     imports=EV_LOCKED_IMPORT), [f"{EV_DOM}.account_locked.AccountLocked.lock_note"],
            {"auto": (2, [("#474", "locked.lock_note", ev_tree("locked"))]),
             "bl": (2, [("#474", "locked.lock_note", ev_tree("locked"))])}),
    # 설계가 «그대로» 라 한 셋 — 고치기 전 검사기와 같은 출력(옛 · 새 검사기 대조: scratch f80/impl/extra_cases.py).
    # N21 은 모듈 별칭 대입 `Suspended = AccountSuspended` 뒤 catch — 트리(도메인 import 이름 아님)도 code lane(꼴 밖 · 도메인)도
    # 줄을 내지 않는다(기존 틈 · 이 수리로 넓어지지 않음 — 다음 판 후보).
    "N14": (ev_files(ops='''
    @route.get("/me/login-block", response={200: AccountOut, 403: AccountSuspendedError}, summary="내 로그인 막힘")
    def get_my_login_block(self, request: HttpRequest, response: HttpResponse) -> AccountOut | Status[AccountsErrorSchema]:
        use_case: AuthenticateAccountUseCase = build_authenticate_account_use_case()
        result: AccountOut = use_case.find()
        if result.outcome == "suspended":
            suspended_outcome: AccountsErrorSchema = AccountSuspendedError()
            response[_LOGIN_BLOCKED_UNTIL_HEADER] = result.until_text
            return Status(403, suspended_outcome)
        return result
'''), [EV_UNTIL], {"auto": (0, []), "pre": (0, []),
                     "cj": (2, [("-", 'if result.outcome == "suspended"', controller.RESULT_VARIANT_BRANCH_FORBIDDEN)]),
                     "bl": (2, [("-", 'if result.outcome == "suspended"', controller.RESULT_VARIANT_BRANCH_FORBIDDEN)])}),
    "N21": (ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = suspended.reason_label',)),
                            head="Suspended as suspended"), module="Suspended = AccountSuspended\n"), [EV_LABEL],
            {"auto": (0, []), "cj": (0, []), "bl": (0, []), "pre": (0, [])}),
    "N22": (ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = suspended.reason_label',))),
                     module="AccountSuspended = InvalidCredentials\n"), [EV_LABEL],
            {mode: (2, [("#474", '= suspended.reason_label', T474)]) for mode in ("auto", "cj", "bl", "pre")}),
    # 덧붙임 1 ① — 12-slot 없음 + 오류 status 선언 없음 + 꼴 맞는 승인 밖 읽기: auto 는 비켜 준다(반송은 Coordinator R-0331 몫)
    # (구현 검토 보완) 입력 조건을 그대로 만든다 — `response=` 에 오류 status 선언이 없고 두 가지 모두 raw 403 이다.
    "N29": ({EV_CTRL: ev_controller(ev_arm('''payload_error: AccountsErrorSchema = AccountSuspendedError(message=suspended.reason_code)
return JsonResponse(payload_error.model_dump(), status=403)
'''), imports="from django.http import JsonResponse\n").replace(
        "response={200: AccountOut, 403: InvalidCredentialsError | AccountSuspendedError},", "response={200: AccountOut},").replace(
        "            invalid_credentials: AccountsErrorSchema = InvalidCredentialsError()\n"
        "            return Status(403, invalid_credentials)\n",
        '            return JsonResponse({"error": "invalid_credentials"}, status=403)\n')}, [], {"auto": (0, [])}),
})


def _ev_whole_in_header(name: str, template: str, form: str = "f2") -> None:
    """잡은 예외를 «통째» 로, 호출 없이 머리 대입(값 · 키)에 싣는 한 변종(구현 검토 차단 1) — forwarding 은 호출 인자만 본다.

    도메인 판은 트리 #474(모든 프로필) · 응용 판은 code-json 에서 C2(그 머리 행) + 가지 문법 줄 · auto 는 code lane 이
    없어 응용 판이 통과한다(R-0331 몫). form: f2 = 꼴 2 의 값 있는 가지 · f1ev = 꼴 1 + 승인 사건 값 · f1no = 사건 값 없는 가지."""
    for suffix, caught, head, origin in (("", "suspended", "AccountSuspended as suspended", EV_SUSP),
                                         ("-app", "blocked", "LoginBlocked as blocked", EV_APP)):
        line = template.replace("NAME", caught)
        if form == "f2":
            present = ("until_error: AccountsErrorSchema = AccountSuspendedError()\n"
                       f"response[_LOGIN_BLOCKED_UNTIL_HEADER] = {caught}.blocked_until.astimezone(UTC).isoformat()\n"
                       f"{line}\nreturn Status(403, until_error)\n")
            body = ev_form2(present, EV_ABSENT_STATIC, f"{caught}.blocked_until is not None")
            flags = [f"{origin}.blocked_until"]
            code_lane = [("-", f"if {caught}.blocked_until is not None", EV_ARM), *EV_OWN4]
        else:
            body = ev_single(f"message={caught}.reason_label" if form == "f1ev" else "", headers=(line,))
            flags = [f"{origin}.reason_label"] if form == "f1ev" else []
            code_lane = [("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2]
        files = ev_files(ev_arm(body, head=head), imports=EV_APP_IMPORT if suffix else "")
        if suffix:
            expectations = {"auto": (0, []), "cj": (2, [("-", line, EV_C2), *code_lane]),
                            "bl": (2, [("-", line, EV_C2), *code_lane])}
        else:
            expectations = {"auto": (2, [("#474", line, T474)]), "cj": (2, [("#474", line, T474)]),
                            "bl": (2, [("#474", line, T474), *code_lane])}
        EV_CASES[name + suffix] = (files, flags, expectations)


_ev_whole_in_header("N30a", 'response["Login-Blocked-Debug"] = f"{NAME}"')
_ev_whole_in_header("N30b", 'response[f"{NAME}"] = "x"')
_ev_whole_in_header("N30c", 'response["Login-Blocked-Debug"] = "%s" % NAME')
_ev_whole_in_header("N30d", 'response["Login-Blocked-Debug"] = "blocked: " + NAME')
_ev_whole_in_header("N30e", 'response["Login-Blocked-Debug"] = NAME')
_ev_whole_in_header("N30f", 'response["Login-Blocked-Debug"] = (lambda: NAME)')
_ev_whole_in_header("N31", 'response["Login-Blocked-Debug"] = f"{NAME}"', form="f1ev")
_ev_whole_in_header("N32a", 'response["Login-Blocked-Debug"] = f"{NAME}"', form="f1no")
_ev_whole_in_header("N32b", 'response[f"{NAME}"] = "x"', form="f1no")

# N33 — 비켜 주기는 managed catch(operation 본문의 try handler)에만 건다(Claude 구현 검토 차단 1). route 아닌 메서드 · 모듈
# 함수 · operation 안 중첩 함수의 catch 는 code lane 이 보지 않으므로, 꼴이 맞아도 트리 #474 가 그대로 선다(모든 프로필).
EV_UNMANAGED_READ = '''try:
    use_case.execute(command)
except AccountSuspended as suspended:
    marker: str = "x"
    response["Login-Blocked-Code"] = suspended.reason_code
'''
EV_UNMANAGED_474 = [("#474", 'response["Login-Blocked-Code"] = suspended.reason_code', T474)]
EV_UNMANAGED_RUNS = {"auto": (2, EV_UNMANAGED_474), "cj": (2, EV_UNMANAGED_474), "bl": (2, EV_UNMANAGED_474)}
EV_CASES.update({
    "N33a": (ev_files(ops='''
    def _mark(self, use_case: AuthenticateAccountUseCase, command: AuthenticateAccountCommand, response: HttpResponse) -> None:
''' + textwrap.indent(EV_UNMANAGED_READ, " " * 8)), [EV_CODE], EV_UNMANAGED_RUNS),
    "N33b": (ev_files(module='''

def _mark(use_case: AuthenticateAccountUseCase, command: AuthenticateAccountCommand, response: HttpResponse) -> None:
''' + textwrap.indent(EV_UNMANAGED_READ, " " * 4) + "\n"), [EV_CODE], EV_UNMANAGED_RUNS),
    "N33c": (ev_files(pre="        def _mark() -> None:\n" + textwrap.indent(EV_UNMANAGED_READ, " " * 12)),
             [EV_CODE], EV_UNMANAGED_RUNS),
    # 끝까지 실리는 흐름 — operation 의 try 가 메서드를 부르고, 그 메서드가 승인 안 된 필드를 머리에 쓴 뒤 다시 던진다
    "N33d": ({EV_CTRL: ev_controller(ev_arm(EV_STATIC_ARM, head="AccountSuspended"), ops='''
    def _authenticate(
        self, use_case: AuthenticateAccountUseCase, command: AuthenticateAccountCommand, response: HttpResponse
    ) -> AuthenticateAccountResult:
        try:
            return use_case.execute(command)
        except AccountSuspended as suspended:
            marker: str = "x"
            response["Login-Blocked-Code"] = suspended.reason_code
            raise
''').replace("= use_case.execute(command)\n        except InvalidCredentials",
             "= self._authenticate(use_case, command, response)\n        except InvalidCredentials")},
             [], EV_UNMANAGED_RUNS),
})
# N34 — 머리 값 S 문법: 승인 필드 원자와 다른 값을 한 f-string 머리에 섞는다(꼴 · 승인은 맞으므로 auto 통과 · code-json ⑷)
for _suffix in ("", "-app"):
    EV_CASES["N34" + _suffix] = (
        ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = f"{suspended.reason_label}/{payload.email}"',))),
                 app=bool(_suffix)),
        [f"{EV_APP if _suffix else EV_SUSP}.reason_label"],
        {"auto": (0, []), "cj": (2, [("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2]),
         "bl": (2, [("-", "suspended_error: AccountsErrorSchema", EV_ARM), *EV_OWN2])})

# N35 — «선언 필드» 는 클래스 본문 `f: T` 또는 `__init__` 의 `self.f: T = …` 뿐이다(R-3654): 주석 없는 대입 `self.f = f` 만 있는
# 필드를 읽으면 승인 flag 를 넘겨도 비켜 주지 않는다(상속 필드는 N27).
EV_UNDECLARED_SRC = EV_SUSPENDED_SRC.replace("    reason_label: str\n\n", "")
assert EV_UNDECLARED_SRC != EV_SUSPENDED_SRC and "self.reason_label = reason_label" in EV_UNDECLARED_SRC
EV_CASES["N35"] = (
    ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = suspended.reason_label',))),
             **{f"{EV_EXC_DIR}/account_suspended.py": EV_UNDECLARED_SRC}),
    [EV_LABEL], {mode: (2, [("#474", "= suspended.reason_label", T474)]) for mode in ("auto", "cj", "bl", "pre")})

# lesson 꼴(트리 밖 `driving_layer/controller.py` — code lane 행렬 픽스처와 같은 자리)
EV_LESSON_CTRL = "application/lesson/driving_layer/controller.py"
EV_LESSON_SELECT = ["--scope", "lesson", "--api-module", "config/api.py", "--controller-module", EV_LESSON_CTRL,
                    "--scope-bc", "lesson", "--error-bc", "lesson"]
EV_GONE = "application.lesson.domain_layer.lesson.exception.lesson_gone.LessonGone"
EV_LESSON_BASE = {
    "framework/ninja/__init__.py": "",
    "config/api.py": "from ninja_extra import NinjaExtraAPI\n\napi = NinjaExtraAPI()\n",
    "application/lesson/application_layer/use_cases.py": "def get_lesson(lesson_id: int):\n    return {'id': lesson_id}\n",
    "application/lesson/domain_layer/lesson/exception/lesson_gone.py": '''from __future__ import annotations

from datetime import datetime


class LessonGone(Exception):
    def __init__(self, *, until: datetime | None, label: str, http_status: int) -> None:
        super().__init__(label)
        self.until: datetime | None = until
        self.label: str = label
        self.http_status: int = http_status
''',
}
EV_LESSON_CONTROLLER = '''from datetime import UTC

from ninja import Router, Status

from application.lesson.application_layer.use_cases import get_lesson
from application.lesson.domain_layer.lesson.exception.lesson_gone import LessonGone
from application.lesson.driving_layer.api.bc_error_schema import __NAMES__

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: LessonNotFoundError})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonGone as gone:
__ARM__    return lesson
'''


def ev_lesson(common: str, bc: str, arm: str, names: str = "LessonErrorCode, LessonErrorSchema, LessonNotFoundError") -> dict[str, str]:
    return {**EV_LESSON_BASE, "framework/ninja/framework_error_schema.py": common,
            "application/lesson/driving_layer/api/bc_error_schema.py": bc,
            EV_LESSON_CTRL: EV_LESSON_CONTROLLER.replace("__NAMES__", names).replace(
                "__ARM__", textwrap.indent(textwrap.dedent(arm), " " * 8))}


EV_UNCERTAIN_COMMON = '''from ninja import Schema
from pydantic import Field

from framework.ninja.alias_source import message_alias


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str = Field(alias=message_alias())
'''
EV_LESSON_OWN = [("-", "error: LessonErrorSchema", EV_OWN_C), ("-", "return Status(404, error)", EV_OWN_S)]
EV_LESSON_CASES = {
    "P14": (ev_lesson(backstop_matrix.CUSTOM_COMMON_ERROR_OUT, backstop_matrix.CUSTOM_LESSON_ERROR_OUT,
                      'error: LessonErrorSchema = LessonNotFoundError(msg=f"Lesson {gone.label} is gone.")\n'
                      "return Status(404, error)\n"), [f"{EV_GONE}.label"], {"auto": (0, []), "cj": (0, []), "bl": (0, [])}),
    "P15": (ev_lesson(backstop_matrix.FLEXIBLE_COMMON_ERROR_OUT, backstop_matrix.FLEXIBLE_LESSON_ERROR_OUT,
                      "error: LessonErrorSchema = LessonNotFoundError(msg=gone.label)\nreturn Status(404, error)\n"),
            [f"{EV_GONE}.label"], {"cj": (0, []), "bl": (0, [])}),
    "N7c": (ev_lesson(backstop_matrix.COMMON_ERROR_OUT, backstop_matrix.LESSON_ERROR_OUT,
                      "error: LessonErrorSchema = LessonErrorSchema(code=LessonErrorCode.NOT_FOUND, title=\"Gone\", "
                      "status=gone.http_status, detail=\"Gone.\")\nreturn Status(404, error)\n"),
            # `int` 필드 맨 읽기는 꼴 밖(F3 — f-string 안만) — base 생성 인자 판정(⑶)은 꼴 맞는 원자만 보므로 forwarding 만
            # 선다(꼴 밖 읽기에 ⑶ 을 더하면 재현 e2b · e3 의 수집 출력이 바뀐다 — S3 무변).
            [f"{EV_GONE}.http_status"], {"cj": (2, [("#474", "except LessonGone as gone", EV_FWD_D)])}),
    "N7d": (ev_lesson(backstop_matrix.CUSTOM_COMMON_ERROR_OUT, backstop_matrix.CUSTOM_LESSON_ERROR_OUT,
                      "error: LessonErrorSchema = LessonErrorSchema(error_type=LessonErrorCode.NOT_FOUND, msg=\"Gone.\", "
                      "is_show=gone.label)\nreturn Status(404, error)\n"),
            [f"{EV_GONE}.label"], {"cj": (2, [("#474", "except LessonGone as gone", EV_FWD_D),
                                              ("-", "error: LessonErrorSchema", EV_ARM), *EV_LESSON_OWN])}),
    "N25": (ev_lesson(backstop_matrix.COMMON_ERROR_OUT, backstop_matrix.LESSON_ERROR_OUT,
                      'error: LessonErrorSchema = LessonNotFoundError(detail=f"Gone: {gone.label}")\nreturn Status(404, error)\n'),
            [f"{EV_GONE}.label"], {"cj": (2, [("#474", "except LessonGone as gone", EV_FWD_D),
                                              ("-", "error: LessonErrorSchema", EV_ARM), *EV_LESSON_OWN])}),
    "N28": (ev_lesson(EV_UNCERTAIN_COMMON, backstop_matrix.CUSTOM_LESSON_ERROR_OUT,
                      'error: LessonErrorSchema = LessonNotFoundError(msg=f"Lesson {gone.label} is gone.")\n'
                      "return Status(404, error)\n"),
            [f"{EV_GONE}.label"], {"cj": (1, "alias constructor-key 분석 불능: msg")}),
    # 덧붙임 1 ② — 두 가지의 status 는 «같은 오류 칸 읽기» 라도 생성 호출이 정한 값이 같아야 한다
    "N12g2": (ev_lesson(backstop_matrix.COMMON_ERROR_OUT, backstop_matrix.LESSON_ERROR_OUT, '''if gone.until is not None:
    until_error: LessonErrorSchema = LessonErrorSchema(code=LessonErrorCode.NOT_FOUND, title="Gone", status=404, detail="Gone.")
    return Status(until_error.status, until_error)
else:
    forever_error: LessonErrorSchema = LessonErrorSchema(code=LessonErrorCode.NOT_FOUND, title="Gone", status=410, detail="Gone.")
    return Status(forever_error.status, forever_error)
'''), [f"{EV_GONE}.until"], {"cj": (2, [("-", "if gone.until is not None", EV_ARM),
                                       ("-", "until_error: LessonErrorSchema", EV_OWN_C),
                                       ("-", "return Status(until_error.status, until_error)", EV_OWN_S),
                                       ("-", "forever_error: LessonErrorSchema", EV_OWN_C),
                                       ("-", "return Status(forever_error.status, forever_error)", EV_OWN_S)])}),
    "P12g2": (ev_lesson(backstop_matrix.COMMON_ERROR_OUT, backstop_matrix.LESSON_ERROR_OUT, '''if gone.until is not None:
    until_error: LessonErrorSchema = LessonErrorSchema(code=LessonErrorCode.NOT_FOUND, title="Gone", status=404, detail="Gone.")
    return Status(until_error.status, until_error)
else:
    forever_error: LessonErrorSchema = LessonErrorSchema(code=LessonErrorCode.NOT_FOUND, title="Gone", status=404, detail="Gone.")
    return Status(404, forever_error)
'''), [f"{EV_GONE}.until"], {"cj": (0, []), "bl": (0, [])}),
}
EV_LINE = re.compile(r"^  (?:\[(#\d+)\]|(-)) (\S+?):(\d+): (.*)$")


class EventValueRegression(unittest.TestCase):
    """F4-80 — 잡은 예외의 승인 필드 값(사건 값)을 설명 칸 · 머리 값에만 싣는 꼴(꼴 1 · 꼴 2)과 `--event-value` 승인 대조.

    auto 는 «꼴» 만 보고 비켜 준다(확인 1) · code-json 은 승인 목록 대조(C1) · 응용 예외의 꼴 밖 읽기(C2) ·
    가지 문법 · 생성 인자 · 머리를 본다 · preserve 는 #474 를 그대로 낸다. 줄은 표지 행 원문까지 고정한다.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="field-event-value-")
        self.addCleanup(self.tmp.cleanup)
        self.env = {"DJR_VIOLATIONS_DIR": str(Path(self.tmp.name) / "violations")}

    def project(self, name: str, base: dict[str, str], files: dict[str, str]) -> Path:
        root = Path(self.tmp.name) / name
        for rel, source in {**base, **files}.items():
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")
        return root

    def run_main(self, root: Path, args: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, self.env), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = controller.main(["checker", str(root), *args])
        return code, out.getvalue(), err.getvalue()

    @staticmethod
    def found(stdout: str) -> list[tuple[str, str, int, str]]:
        rows = []
        for line in stdout.splitlines():
            hit = EV_LINE.match(line)
            if hit:
                rows.append((hit.group(1) or "-", hit.group(3), int(hit.group(4)), hit.group(5)))
        return sorted(rows)

    @staticmethod
    def expected(root: Path, entries: list[tuple], default: str) -> list[tuple[str, str, int, str]]:
        rows = []
        for entry in entries:
            tag, marker, category = entry[:3]
            path = entry[3] if len(entry) > 3 else default
            source = (root / path).read_text(encoding="utf-8").splitlines()
            hits = [index for index, text in enumerate(source, 1) if marker in text]
            assert hits, (path, marker)
            line = hits[0]
            shown = source[line - 1].strip()
            message = category if category.startswith("도메인 예외를") else f"{category}: {shown}"
            rows.append((tag, path, line, message))
        return sorted(rows)

    def assert_cases(self, cases: dict, base: dict[str, str], select: list[str], default: str) -> None:
        modes = {"auto": ["--error-profile", "auto"], "cj": ["--error-profile", "dddjango-code-json", *select],
                 "bl": ["--error-profile", "dddjango-code-json", *select, "--anchor-baseline"],
                 "pre": ["--error-profile", "preserve-established", *select]}
        for name, (files, flags, expectations) in cases.items():
            root = self.project(name, base, files)
            event_args = [token for value in flags for token in ("--event-value", value)]
            for mode, (exit_code, entries) in expectations.items():
                args = modes[mode] + (event_args if mode in ("cj", "bl") or exit_code == 1 else [])
                with self.subTest(case=name, mode=mode):
                    code, stdout, stderr = self.run_main(root, args)
                    self.assertEqual(code, exit_code, stdout + stderr)
                    if exit_code == 1:
                        self.assertIn(entries, stderr)
                        continue
                    self.assertEqual(self.found(stdout), self.expected(root, entries, default), stdout + stderr)
                    if exit_code == 0:
                        self.assertEqual(stderr, "")

    def test_event_value_shapes_on_standard_tree(self) -> None:
        self.assert_cases(EV_CASES, EV_BASE, EV_SELECT, EV_CTRL)

    def test_event_value_shapes_on_code_lane_matrix_fixture(self) -> None:
        self.assert_cases(EV_LESSON_CASES, {}, EV_LESSON_SELECT, EV_LESSON_CTRL)

    def anchor_run(self, anchor_files: dict[str, str], current: dict[str, str], flags: list[str]) -> tuple[int, str]:
        root = Path(self.tmp.name) / "anchored"
        self.project("anchored", anchor_files, {})
        _git(root, "init", "-q")
        _git(root, "add", "-A")
        _git(root, "commit", "-qm", "anchor")
        anchor = _git(root, "rev-parse", "HEAD").strip()
        for rel, source in current.items():
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")
        args = ["--error-profile", "dddjango-code-json", *EV_SELECT, "--anchor", anchor]
        args += [token for value in flags for token in ("--event-value", value)]
        done = subprocess.run([sys.executable, "-B", str(SCRIPTS / "check-api-error-controller-contract.py"),
                               str(root), *args], capture_output=True, text=True, env={**os.environ, **self.env})
        return done.returncode, done.stdout + done.stderr

    def test_anchor_baseline_keeps_event_value_without_bc_usage_error(self) -> None:
        # P16 — 앵커에 없는 새 BC: 기준선 재실행은 --error-bc 를 걷고 --event-value 는 남긴다(사용 오류 없이 돈다).
        stray = {f"{EV_A}/driving_layer/api/account/ninja_helpers.py": "VALUE: int = 1\n"}
        # 앵커에 `application/` 은 있고 그 BC 만 없어야 anchor_diff 가 --scope-bc · --error-bc 를 걷는다(없으면 다른 사용
        # 오류로 positional 기준선 강등 — BC 대조 건너뜀을 지운 변이도 통과하던 헛도는 꼴이었다 · 구현 검토 보완).
        anchor_only = {path: text for path, text in EV_BASE.items()
                       if not path.startswith("application/") or path == "application/__init__.py"}
        code, output = self.anchor_run(anchor_only, {**EV_BASE, **EV_CASES["P1"][0], **stray}, [EV_UNTIL])
        self.assertEqual(code, 2, output)
        self.assertIn("기준선=selector 렌더 재실행", output)
        self.assertIn("신규분(앵커 이후) 1건 · 앵커 기존분(잔존) 0건", output)
        self.assertNotIn("사용 오류", output)

    def test_anchor_baseline_with_new_exception_file(self) -> None:
        # P16b — 앵커에 없는 새 예외 파일(P2 의 AccountSuspendedUntil): 모듈은 읽기가 나올 때만 푼다.
        stray = {f"{EV_A}/driving_layer/api/account/ninja_helpers.py": "VALUE: int = 1\n"}
        files, flags, _ = EV_CASES["P2"]
        code, output = self.anchor_run(EV_BASE, {**EV_BASE, **files, **stray}, flags)
        self.assertEqual(code, 2, output)
        self.assertIn("기준선=selector 렌더 재실행", output)
        self.assertIn("신규분(앵커 이후) 1건 · 앵커 기존분(잔존) 0건", output)
        self.assertNotIn("사용 오류", output)

    def test_anchor_new_out_of_form_read_is_not_hidden_by_existing_unapproved_read(self) -> None:
        # C1(꼴 맞는 읽기의 승인 밖 — 앵커 기존분)이 같은 catch 에 새로 더한 «꼴 밖 읽기»의 트리 #474 를 가리지 않는다.
        # 앞 레인이 승인받은 읽기가 있는 catch 를 뒤 레인이 flag 없이 다시 열어 `n._secret` 읽기를 더한 꼴.
        before = ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = suspended.reason_label',))))
        after = ev_files(ev_arm(ev_single(headers=('response["Login-Blocked-Label"] = suspended.reason_label',
                                                   'response["Login-Blocked-Secret"] = suspended._secret'))))
        code, output = self.anchor_run({**EV_BASE, **before}, after, [])
        self.assertEqual(code, 2, output)
        self.assertIn("기준선=selector 렌더 재실행", output)
        self.assertIn("신규분(앵커 이후) 1건 · 앵커 기존분(잔존) 1건", output)
        new_part = output.split("== 신규분")[1].split("== 앵커 기존분")[0]
        self.assertIn("suspended._secret", (Path(self.tmp.name) / "anchored" / EV_CTRL).read_text(encoding="utf-8"))
        self.assertIn(T474, new_part)
        self.assertIn(EV_C1, output.split("== 앵커 기존분")[1])

    def test_n29_fixture_declares_no_error_status(self) -> None:
        # 덧붙임 1 의 누락 사례 입력 조건 — 12-slot 없이(auto) `response=` 에 오류 status 선언이 없고 raw 403 으로 답한다.
        source = EV_CASES["N29"][0][EV_CTRL]
        declared = [key.value for node in ast.walk(ast.parse(source)) if isinstance(node, ast.keyword)
                    and node.arg == "response" and isinstance(node.value, ast.Dict)
                    for key in node.value.keys if isinstance(key, ast.Constant)]
        self.assertEqual(declared, [200])
        self.assertNotIn("Status(4", source)
        self.assertEqual(source.count("status=403"), 2)
        self.assertIn("message=suspended.reason_code", source)

    def test_event_value_review_duties_are_written(self) -> None:
        """R1 ~ R7 · A.10 · B — 기계 밖 책임이 개정 문장에 글로 있다(문장 있음 대조 · 레인 실제 대조는 G1 · G2 몫)."""
        phrases = {
            "dddjango/agents/discipline-reviewer.md": (
                "slot 10 이 정한 머리 누락", "메시지와 머리의 날짜 불일치", "slot 10 이 정하지 않은 머리",
                "`str(다른 예외)`", "시간대를 갖는 aware datetime 인지", "구현된 operation `description`", "`--event-value`"),
            "dddjango/agents/design-review-api.md": ("`str(다른 예외)`", "operation `description`", "생략의 뜻"),
            "dddjango/agents/design-architect.md": (
                "사건 값", "operation `description`", "발주자 도출 · 설계 가정", "같은 concrete · 코드 · 실제 status 값으로"),
            "dddjango/commands/dddjango.md": (
                "`--event-value`", "`response=` 선언 유무와 관계없이", "사건 값 읽기에 승인된 code-json scope 가 없으면"),
            "dddjango/skills/implementation-django-ninja/references/final.md": (
                "`n.f.astimezone(UTC).isoformat()`", "`if <n>.<f> is not None:`",
                "`__init__`의 `self.f: T = …`", "값이 늘 있는 다른 승인 필드는 어느 가지에서든 읽을 수 있다"),
            "dddjango/skills/discipline-houserules/references/final.md": ("`<project>/settings` 의 문자열로 등록해",),
        }
        for rel, expected in phrases.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            for phrase in expected:
                with self.subTest(path=rel, phrase=phrase):
                    self.assertIn(phrase, text)
        codex = {
            "codex-dddjango/skills/dddjango/SKILL.md": (
                "`--event-value`", "`response=` 선언 유무와 관계없이", "사건 값 읽기에 승인된 code-json scope 가 없으면"),
            "codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md": (
                "slot 10 이 정한 머리 누락", "시간대를 갖는 aware datetime 인지", "구현된 operation `description`"),
            "codex-dddjango/skills/dddjango-design-review-api/SKILL.md": ("`str(다른 예외)`",),
            "codex-dddjango/skills/dddjango-design-architect/SKILL.md": (
                "사건 값", "발주자 도출 · 설계 가정", "같은 concrete · 코드 · 실제 status 값으로"),
        }
        for rel, expected in codex.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            for phrase in expected:
                with self.subTest(path=rel, phrase=phrase):
                    self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
