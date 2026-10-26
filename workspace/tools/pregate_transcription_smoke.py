#!/usr/bin/env python3
"""pre-gate 전사 손실 회귀: 실제 파일 조치·검사기 판정·CLI skip 계약을 대조한다.

삭제 정리 제거, decorator 유실, TYPE_CHECKING 평탄화가 각각 이 검증을 red로 만든다.
반대 대조군은 전역 빈 폴더 정리와 무조건 dataclass/admin 면제를 잡는다.
F4-115 — update 도메인 서비스 서명(#304 · #305 · #307 · #308)과 OHS 번역 출처 칸(#474 · #62)의 선언 예보를 실검사기 판정 ·
후상태 줄 수와 대조한다(`DomainServiceForecastTest` · `CatchForecastTest`). 번들 검사기는 싣는 동안 `sys.modules` 에 있고 실패하면
이 적재가 올린 것만 걷는다(`BundledCheckerLoadTest` — 파이썬 판과 무관한 단언).
"""
from __future__ import annotations

import ast
import contextlib
import errno
import io
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pregate_fixture_run import _git, _load_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "dddjango/scripts"
pg = _load_module(SCRIPTS / "design_pregate.py", "transcription_pregate")
ci = _load_module(SCRIPTS / "check-context-isolation.py", "transcription_context")
ps = _load_module(SCRIPTS / "check-public-surface-annotation.py", "transcription_surface")
RESPONSE = "application/garden/driving_layer/open_host_service/catalog/contract/response/list_books_response.py"
PANEL = "application/garden/driven_layer/django_garden/admin/book/panel.py"
# F4-73 — 도메인 저장소 선언 예보(#355 · #597). 기준선 실물은 현장 저장소 꼴(애그리거트 · VO import · 기존 빚)을 줄였다.
DOMAIN = "application.fortune_record.domain_layer.fortune_record"
AGGREGATE = "application/fortune_record/domain_layer/fortune_record/fortune_record.py"
REPOSITORY = "application/fortune_record/domain_layer/fortune_record/fortune_record_repository.py"
REPOSITORY_BASELINE = (
    '"""Fortune record repository."""\nfrom __future__ import annotations\n\n'
    "from abc import ABC, abstractmethod\nfrom uuid import UUID\n\n"
    f"from {DOMAIN}.fortune_record import FortuneRecord\n"
    f"from {DOMAIN}.value_object.fortune_record_index import FortuneRecordIndex\n\n\n"
    "class FortuneRecordRepository(ABC):\n"
    "    @abstractmethod\n    def save(self, record: FortuneRecord) -> None: ...\n\n"
    "    @abstractmethod\n    def find(self, record_id: UUID) -> FortuneRecord | None: ...\n\n"
    "    @abstractmethod\n    def indexes(self, account_id: int) -> tuple[FortuneRecordIndex, ...]: ...\n\n"
    "    @abstractmethod\n    def legacy_ids(self, account_id: int) -> frozenset[UUID]: ...\n\n"
    "    @abstractmethod\n    def delete_old(self, account_id: int) -> None: ...\n")
FIELD_METHOD = "recorded_character_ids(account_id: int, character_ids: frozenset[UUID]) -> frozenset[UUID]"
FIELD_DETAIL = "`recorded_character_ids` 반환 `UUID.frozenset` 이 애그리거트도 값 객체도 아니다"
# 기준선에만 있는 프로젝트 출처는 후상태의 확정 근거가 아니다 — 구현이 같은 이름을 domain 에서 들이면 실검사기는 통과한다.
ORDER_DOMAIN = "application/orders/domain_layer/order"
ORDER_REPOSITORY = f"{ORDER_DOMAIN}/order_repository.py"
ORDER_HEAD = "from abc import ABC, abstractmethod\n"
ORDER_OUTSIDE = "from support.read_models import Summary\n"
ORDER_CLASS = "\n\nclass OrderRepository(ABC):\n    pass\n"
SUMMARY_VO = "application.orders.domain_layer.order.value_object.summary"
SUMMARY_DETAIL = "`summary` 반환 `Summary` 이 애그리거트도 값 객체도 아니다"
BASELINE_ONLY = "기준선에만 있는 출처"
# 같은 클래스의 기존 빚을 다시 적은 줄은 새 위반이 아니다(G2 registry 차분으로도 귀속 0) — 철자·감싸개만 바뀐 반환. 같은
# 파일의 베이스 클래스(조상)에게만 같은 판정문이 있으면 물려받은 빚인지 이 클래스의 새 위반인지 가를 수 없어 후보다. 클래스
# 본문 복합문 아래에만 있는 메서드는 검사기가 판정하지 않는 자리라 다시 적으면 후보다.
DEBT_BASELINE = (
    REPOSITORY_BASELINE.replace("from uuid import UUID\n", "from typing import TYPE_CHECKING, Optional\nfrom uuid import UUID\n")
    + "\n    @abstractmethod\n    def legacy_opt(self, account_id: int) -> Optional[UUID]: ...\n"
    "\n    @abstractmethod\n    def legacy_many(self, account_id: int) -> tuple[UUID, ...]: ...\n"
    "\n    @abstractmethod\n    def legacy_rows(self, account_id: int) -> dict[str, int]: ...\n"
    "\n    if TYPE_CHECKING:\n        def guarded(self, account_id: int) -> frozenset[UUID]: ...\n"
    "        def delete_guarded(self, account_id: int) -> None: ...\n"
    "\n\nclass ArchivedFortuneRecordRepository(FortuneRecordRepository):\n    pass\n")
DEBT_RESTATED = (DEBT_BASELINE.replace("-> Optional[UUID]", "-> UUID | None").replace("-> tuple[UUID, ...]", "-> list[UUID]")
                 .replace("-> dict[str, int]", "-> dict[str, str]"))
# 기존 빚은 그 줄의 소유자(클래스 · 메서드)에만 묶인다 — 다른 클래스의 새 메서드는 새 위반이고, 그 파일 안에서 확인되는 상속
# 사슬의 조상과만 겹치면 후보다.
OWNED_BASELINE = (
    DEBT_BASELINE.replace("from uuid import UUID\n",
                          f"from uuid import UUID\n\nfrom {DOMAIN}.base_repository import BaseRecordRepository\n")
    .replace("\n\nclass ArchivedFortuneRecordRepository",
             "\n    @abstractmethod\n    def count_records(self, account_id: int) -> int: ...\n"
             "\n\nclass ArchivedFortuneRecordRepository")
    + "\n\nclass DeepArchiveRepository(ArchivedFortuneRecordRepository):\n    pass\n"
    "\n\nclass UnrelatedRecordRepository(ABC):\n    pass\n"
    "\n\nclass ImportedBaseRepository(BaseRecordRepository):\n    pass\n")
LEGACY_ORDER_BASELINE = (ORDER_HEAD + "from uuid import UUID\n\n\nclass LegacyOrderRepository(ABC):\n"
                         "    @abstractmethod\n    def owner_id(self) -> UUID: ...\n" + ORDER_CLASS)
OWNER_DETAIL = "`owner_id` 반환 `UUID` 이 애그리거트도 값 객체도 아니다"
# 자식이 기준선에서 직접 정의하던 통과 메서드를 조상의 위반 꼴로 바꾸는 명세(재검토 반례 둘) — 실검사기는 자식에게도 새 줄을 낸다.
HEIR_OWNER_BASELINE = (ORDER_HEAD + "from uuid import UUID\n\n"
                       "from application.orders.domain_layer.order.value_object.owner_id import OwnerId\n\n\n"
                       "class LegacyOrderRepository(ABC):\n    @abstractmethod\n    def owner_id(self) -> UUID: ...\n\n\n"
                       "class OrderRepository(LegacyOrderRepository):\n"
                       "    @abstractmethod\n    def owner_id(self) -> OwnerId: ...\n")
HEIR_IDS_BASELINE = (ORDER_HEAD + "from uuid import UUID\n\nfrom application.orders.domain_layer.order.order import Order\n\n\n"
                     "class BaseOrderRepository(ABC):\n    @abstractmethod\n    def ids(self) -> frozenset[UUID]: ...\n\n\n"
                     "class OrderRepository(BaseOrderRepository):\n    @abstractmethod\n    def ids(self) -> Order | None: ...\n")
IDS_DETAIL = "`ids` 반환 `UUID.frozenset` 이 애그리거트도 값 객체도 아니다"


def heir_reason(ancestor: str, method: str) -> str:
    return f"예보 불확정: 같은 판정문의 기존 줄이 조상 `{ancestor}.{method}` 에 있다"


def own_def_reason(ancestor: str, method: str) -> str:
    return f"예보 불확정: 이 클래스가 기준선에서 직접 정의하던 반환을 조상 `{ancestor}.{method}` 의 기존 빚과 같은 꼴(같은 판정문)로 바꾼다"


def heir_question(ancestor: str) -> str:
    return f"물음: 이 메서드는 조상 `{ancestor}` 의 선언을 그대로 물려받는가"


def g2_clause(ancestor: str) -> str:
    return (f"이 클래스에서 재정의하는가(그러면 검사기가 이 클래스에도 새 줄을 낸다 · 조상 `{ancestor}` 의 줄과 같은 판정문이면 "
            "G2 registry 는 이것을 새 위반으로 귀속하지 않을 수 있다)")


def spec_text(paths: list[str], symbols: list[str] = (), imports: list[str] = ()) -> str:
    return ("<!-- machine: file-plan -->\n```paths\n" + "\n".join(paths) + "\n```\n"
            "<!-- machine: symbols -->\n```symbols\n" + "\n".join(symbols) + "\n```\n"
            "<!-- machine: boundary-imports -->\n```imports\n" + "\n".join(imports) + "\n```\n")


class ScratchLifecycleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="pregate-lifecycle-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "README.md").write_text("fixture\n")
        self.spec = self.root / "spec.md"
        self.spec.write_text(spec_text(["update README.md"]))
        _git(self.repo, "init", "-q", "--object-format=sha1")
        _git(self.repo, "add", "README.md")
        _git(self.repo, "commit", "-qm", "fixture")

    def test_repeated_pregate_cleans_scratch_without_starting_auto_maintenance(self) -> None:
        # SHA-1 fanout 17의 blob 8개: gc.auto=1이면 기존 git 호출의 자동 정리가 실제 발화한다.
        for seed in (507, 873, 1155, 1195, 1278, 1776, 1864, 1982):
            (self.repo / f"payload-{seed}.txt").write_text(f"pregate auto-maintenance probe {seed}\n")
        config = self.root / "gitconfig"
        config.write_text("[gc]\n auto = 1\n autoDetach = true\n"
                          "[maintenance]\n auto = true\n autoDetach = true\n")
        env = dict(os.environ, GIT_CONFIG_GLOBAL=str(config), GIT_CONFIG_NOSYSTEM="1")
        for iteration in range(3):
            with self.subTest(iteration=iteration):
                scratch_root = self.root / f"scratch-{iteration}"
                scratch_root.mkdir()
                trace = self.root / f"trace-{iteration}.jsonl"
                proc = subprocess.run([sys.executable, str(SCRIPTS / "design_pregate.py"),
                                       str(self.spec), str(self.repo)], capture_output=True, text=True,
                                      env=dict(env, TMPDIR=str(scratch_root), TMP=str(scratch_root),
                                               TEMP=str(scratch_root), GIT_TRACE2_EVENT=str(trace)))
                self.assertEqual(proc.returncode, 4, proc.stdout + proc.stderr)
                self.assertEqual(list(scratch_root.glob("design-pregate-*")), [])
                self.assertEqual(list((scratch_root / "dddjango").glob("*")), [])   # 임시 사본 뿌리 안도 비었다
                events = [json.loads(line) for line in trace.read_text().splitlines()]
                starts = [event["argv"] for event in events if event["event"] == "start"
                          and any(arg in ("maintenance", "gc", "repack", "pack-objects")
                                  for arg in event.get("argv", []))]
                self.assertEqual(starts, [], "격리 사본에서 자동 git 정리가 발화했다")

    def test_cleanup_failure_preserves_verdict_and_reports_manual_cleanup(self) -> None:
        scratch = self.root / "design-pregate-cleanup-failure"
        scratch.mkdir()
        real_rmdir = os.rmdir
        cleanup_error = OSError(errno.ENOTEMPTY, "injected concurrent writer", str(scratch))

        def raced_rmdir(path, *args, **kwargs):
            if Path(path) == scratch:
                raise cleanup_error
            return real_rmdir(path, *args, **kwargs)

        stderr = io.StringIO()
        (self.root / "tmp").mkdir()
        with mock.patch.object(pg.tempfile, "tempdir", str(self.root / "tmp")), \
                mock.patch.object(pg.tempfile, "mkdtemp", return_value=str(scratch)), \
                mock.patch.object(os, "rmdir", side_effect=raced_rmdir), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            code = pg.main([str(self.spec), str(self.repo)])
        self.assertEqual(code, 4, stderr.getvalue())
        self.assertEqual(stderr.getvalue(),
                         f"격리 사본 정리 실패: {scratch} — {cleanup_error} (수동 삭제 필요)\n")
        self.assertTrue(scratch.exists())


class TranscriptionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="pregate-transcription-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.env = dict(os.environ, DJR_FINDINGS_JSON=str(self.root / "findings.jsonl"),
                        DJR_VIOLATIONS_DIR=str(self.root / "violations"), PYTHONDONTWRITEBYTECODE="1")
        _git(self.repo, "init", "-q")
        self.write("README.md", "fixture\n")
        self.commit()

    def write(self, path: str, content: str = "") -> Path:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def commit(self) -> None:
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "fixture")

    def plan(self, paths: list[str], symbols: list[str] = (), imports: list[str] = ()):
        plan, errors = pg.parse_spec(spec_text(paths, symbols, imports))
        self.assertEqual(errors, [], "문법 전사 실패: " + " | ".join(errors))
        self.assertIsNotNone(plan)
        return plan

    def checker(self, name: str) -> str:
        result = subprocess.run([sys.executable, str(SCRIPTS / name), str(self.repo)],
                                env=self.env, text=True, capture_output=True)
        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
        return result.stdout

    def surface(self, source: str) -> tuple[list[str], list[str]]:
        mod = ast.parse(source)
        findings, candidates = ps.Findings(defer=True), ps.Candidates(defer=True)
        bindings, aliases, origins = ps._module_bindings(mod), ps._alias_defs(mod), ps._origin_bindings(mod)
        ps._scan_stmts(mod.body, "module", set(), Path(PANEL), findings, False, bindings, aliases, origins)
        ps._check_stub_generic_bases(mod, source, Path(PANEL), findings, candidates,
                                     origins, bindings, aliases)
        return [e.rule for e in findings.entries], [e.rule for e in candidates.entries]

    def response_rules(self, decorator: str, import_stmt: str, referenced: bool = True) -> list[str]:
        symbols = [f"{RESPONSE}::Sprout {{title: str}}"]
        if decorator:
            symbols.append(f"{RESPONSE}::Sprout @{decorator}")
        symbols.append(f"{RESPONSE}::ListBooksResponse {{books: tuple[{'Sprout' if referenced else 'str'}, ...]}}")
        plan = self.plan([f"add {RESPONSE}"], symbols, [f"{RESPONSE}  {import_stmt}"])
        self.write(RESPONSE, pg.render_stub(plan.entries[RESPONSE]))
        findings = ci.Findings(defer=True)
        ci._check_contract_kind((self.repo / RESPONSE).parent, "Response", "#160", "#161",
                                set(), Path("catalog"), findings)
        return [e.rule for e in findings.entries]

    def test_public_helper_dataclass_is_transcribed_with_import_aliases(self) -> None:
        for dec, imp in [("dataclass(frozen=True, slots=True, kw_only=True)", "from dataclasses import dataclass"),
                         ("dc", "from dataclasses import dataclass as dc"),
                         ("dc.dataclass()", "import dataclasses as dc")]:
            with self.subTest(decorator=dec):
                self.assertEqual(self.response_rules(dec, imp), [])

    def test_no_decorator_no_reference_and_fake_import_remain_violations(self) -> None:
        for dec, imp, ref in [("", "from dataclasses import dataclass", True),
                              ("dataclass", "from dataclasses import dataclass", False),
                              ("dataclass", "from impostor import dataclass", True)]:
            with self.subTest(decorator=dec, import_stmt=imp, referenced=ref):
                self.assertEqual(self.response_rules(dec, imp, ref), ["#160", "#484"])

    def test_decorator_order_arguments_and_signal_base_survive(self) -> None:
        plan = self.plan(["add tests/unit/test_book.py"], [
            "tests/unit/test_book.py::TestBook",
            "tests/unit/test_book.py::TestBook @outer(label='x')",
            "tests/unit/test_book.py::TestBook @inner(enabled=True)"])
        entry = plan.entries["tests/unit/test_book.py"]
        entry.signals = pg.Signals(base="TestCase")
        mod = ast.parse(pg.render_stub(entry))
        cls = next(n for n in mod.body if isinstance(n, ast.ClassDef))
        self.assertEqual([ast.unparse(n) for n in cls.decorator_list], ["outer(label='x')", "inner(enabled=True)"])
        self.assertEqual(ast.unparse(cls.bases[0]), "TestCase")

    def panel_plan(self, aliases: list[str], extra: list[str] = ()):
        return self.plan([f"add {PANEL}"], [f"{PANEL}::{row}" for row in aliases] + [
            f'{PANEL}::BookAdmin(_BookAdminBase) {{list_display = ("title",)}}', *extra],
            [f"{PANEL}  from typing import TYPE_CHECKING, TypeAlias",
             f"{PANEL}  from django.contrib import admin"])

    def test_type_checking_alias_preserves_both_branches_without_646(self) -> None:
        plan = self.panel_plan([
            "alias[TYPE_CHECKING] _BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]",
            "alias[else] _BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin"])
        source = pg.render_stub(plan.entries[PANEL])
        self.assertEqual(self.surface(source), ([], []))
        branch = next(n for n in ast.parse(source).body if isinstance(n, ast.If))
        self.assertEqual(ast.unparse(branch.test), "TYPE_CHECKING")
        self.assertEqual(ast.unparse(branch.body[0]), "_BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]")
        self.assertEqual(ast.unparse(branch.orelse[0]), "_BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin")

    def test_unconditional_alias_and_nonadmin_keep_real_findings(self) -> None:
        for row, expected in [
            ("alias _BookAdminBase = admin.ModelAdmin", (["#493", "#646"], [])),
            ("alias _BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin", (["#646"], [])),
            ("alias _BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]", ([], ["#646"]))]:
            with self.subTest(row=row):
                plan = self.panel_plan([row])
                self.assertEqual(self.surface(pg.render_stub(plan.entries[PANEL])), expected)
        plan = self.plan([f"add {PANEL}"], [f"{PANEL}::Helper {{cache = {{}}}}"])
        self.assertEqual(self.surface(pg.render_stub(plan.entries[PANEL])), (["#493"], []))

    def test_malformed_new_rows_fail_closed_even_for_update(self) -> None:
        cases = [
            ["Book @dataclass"], ["book", "book @dataclass"], ["Book", "Book @42"],
            ["alias[TYPE_CHECKING] _Base: TypeAlias = admin.ModelAdmin[Book]"],
            ["alias[else] _Base = admin.ModelAdmin"],
            ["alias[TYPE_CHECKING] _Base = admin.ModelAdmin[Book]", "alias[else] _Other = admin.ModelAdmin"],
            ["alias _Base = admin.ModelAdmin; fail()"], ["alias a = b = admin.ModelAdmin"],
            ["alias _Base = build_base()"], ["alias _Base = admin.ModelAdmin", "alias _Base = admin.ModelAdmin"],
            ["Book", "alias _Base = admin.ModelAdmin"],
            ["alias _Base: (yield 1) = Original"], ["alias __debug__ = Original"],
            ["Book", "Book @dataclass(frozen=True, frozen=False)"],
        ]
        for tag in ("add", "update"):
            for rows in cases:
                with self.subTest(tag=tag, rows=rows):
                    _, errors = pg.parse_spec(spec_text([f"{tag} {PANEL}"], [f"{PANEL}::{r}" for r in rows]))
                    self.assertTrue(errors, "형식 오류를 조용히 받아들였다")

    def test_existing_function_named_alias_remains_valid(self) -> None:
        for row in ("alias", "alias()", "alias -> str", "alias (value: int) -> str"):
            with self.subTest(row=row):
                plan = self.plan(["add framework/tools.py"], [f"framework/tools.py::{row}"])
                module = ast.parse(pg.render_stub(plan.entries["framework/tools.py"]))
                self.assertEqual([n.name for n in module.body if isinstance(n, ast.FunctionDef)], ["alias"])

    def test_update_alias_declaration_resolves_import_without_stub_mutation(self) -> None:
        self.write("framework/base.py", "old: int = 1\n")
        plan = self.plan(["update framework/base.py"], [
            "framework/base.py::alias[TYPE_CHECKING] _Base: TypeAlias = admin.ModelAdmin[Book]",
            "framework/base.py::alias[else] _Base: type[admin.ModelAdmin] = admin.ModelAdmin"],
            ["consumer.py  from framework.base import _Base"])
        result = pg.check_import_existence(self.repo, plan)
        self.assertEqual(result.defects, [])
        self.assertEqual((result.self_update, result.undecidable), (1, 0))
        self.assertIn("_Base", plan.entries["framework/base.py"].declared)
        self.assertEqual((self.repo / "framework/base.py").read_text(), "old: int = 1\n")

    def test_migration_ignored_alias_is_reported(self) -> None:
        for leaf in ("__init__.py", "0001_initial.py"):
            path = f"application/garden/driven_layer/django_garden/migrations/{leaf}"
            with self.subTest(leaf=leaf):
                plan = self.plan([f"add {path}"], [f"{path}::alias _Base = Original"])
                rendered = pg.render_stub(plan.entries[path])
                self.assertNotIn("_Base", rendered)
                self.assertTrue(any("alias" in note and path in note for note in plan.notes))

    def test_remove_prunes_only_its_empty_ancestors(self) -> None:
        self.write("framework/old/nested/a.py")
        (self.repo / "framework/alien").mkdir()
        self.commit()
        plan = self.plan(["remove framework/old/nested/a.py"])
        report = pg.materialize(self.repo, plan)
        self.assertFalse((self.repo / "framework/old").exists())
        self.assertTrue((self.repo / "framework/alien").is_dir())
        self.assertEqual(report["materialized"], ["removed framework/old/nested/a.py"])

    def test_remove_keeps_surviving_files_new_files_and_deferred_paths(self) -> None:
        for retained in ("__init__.py", "untracked.txt", "zero.py"):
            with self.subTest(retained=retained):
                parent = f"framework/keep_{Path(retained).stem}"
                self.write(f"{parent}/a.py")
                self.write(f"{parent}/{retained}")
                pg.materialize(self.repo, self.plan([f"remove {parent}/a.py"]))
                self.assertTrue((self.repo / f"{parent}/{retained}").is_file())
        for tag in ("add", "empty"):
            with self.subTest(tag=tag):
                self.write(f"framework/{tag}/old.py")
                pg.materialize(self.repo, self.plan([f"remove framework/{tag}/old.py", f"{tag} framework/{tag}/new.py"]))
                self.assertTrue((self.repo / f"framework/{tag}/new.py").is_file())
        self.write("framework/deferred/old.py")
        pg.materialize(self.repo, self.plan(["remove@L2 framework/deferred/old.py"]))
        self.assertTrue((self.repo / "framework/deferred/old.py").is_file())

    def test_pruning_does_not_traverse_symlink_ancestor(self) -> None:
        outside = self.root / "outside"
        (outside / "nested").mkdir(parents=True)
        (self.repo / "linked").symlink_to(outside, target_is_directory=True)
        pg.materialize(self.repo, self.plan(["remove linked/nested/absent.py"]))
        self.assertTrue((outside / "nested").is_dir())
        self.assertTrue((self.repo / "linked").is_symlink())

    def test_remove_whole_instances_eliminates_phantom_path_findings(self) -> None:
        for instance in ("domain_layer/book", "application_layer/catalog/delete_book",
                         "driven_layer/django_garden/admin/book"):
            with self.subTest(instance=instance):
                directory = self.repo / "application/garden" / instance
                directory.mkdir(parents=True, exist_ok=True)
                pg.materialize_skeleton(self.repo, "garden")
                files = sorted(p.relative_to(self.repo).as_posix() for p in directory.rglob("*") if p.is_file())
                self.assertTrue(files, "제거 대상이 비어 있는 헛검증")
                self.commit()
                pg.materialize(self.repo, self.plan([f"remove {p}" for p in files]))
                self.assertFalse(directory.exists())
                for checker in ("check-layer-skeleton.py", "check-domain-model.py", "check-usecase-dto-placement.py"):
                    output = self.checker(checker)
                    self.assertFalse(any(instance in line and "[#" in line for line in output.splitlines()), output)

    def test_partial_and_fixed_slot_removals_keep_path_diagnostics(self) -> None:
        directory = self.repo / "application/garden/domain_layer/book"
        directory.mkdir(parents=True)
        pg.materialize_skeleton(self.repo, "garden")
        self.commit()
        pg.materialize(self.repo, self.plan(["remove application/garden/domain_layer/book/book.py"]))
        self.assertIn("[#488]", self.checker("check-layer-skeleton.py"))
        self.assertTrue(directory.is_dir())
        pg.materialize(self.repo, self.plan(["remove application/garden/domain_layer/domain_service/__init__.py"]))
        output = self.checker("check-layer-skeleton.py")
        self.assertTrue(any("domain_service" in line and "[#488]" in line for line in output.splitlines()), output)

    def test_overlay_only_removal_skips_registry_and_never_regenerates_bc(self) -> None:
        path = "application/garden/domain_layer/book/book.py"
        self.write(path, "class Book: pass\n")
        self.commit()
        (self.repo / path).unlink()
        for imports, code in [((), 4), (["consumer.py  from framework.missing import Missing"], 5)]:
            with self.subTest(exit=code):
                spec = self.root / "spec.md"
                spec.write_text(spec_text([f"remove {path}"], imports=imports))
                result = subprocess.run([sys.executable, str(SCRIPTS / "design_pregate.py"), str(spec),
                                         str(self.repo), "--keep", "--report", str(self.root / "report.md")],
                                        env=self.env, capture_output=True, text=True)
                output = result.stdout + result.stderr
                self.assertEqual(result.returncode, code, output)
                self.assertIn("게이트를 부르지 않는다", output)
                match = re.search(r"격리 사본 보존: (.+)", result.stdout)
                self.assertIsNotNone(match, output)
                scratch = Path(match.group(1))
                import shutil
                self.addCleanup(shutil.rmtree, scratch)
                self.assertFalse(list(scratch.rglob("book.py")), output)
                self.assertFalse(any(p.name == "garden" for p in scratch.rglob("garden")), output)
                self.assertIn("빈 부모", (self.root / "report.md").read_text())


class RepositoryForecastTest(unittest.TestCase):
    """F4-73 — add/update 저장소 메서드 서명이 실검사기 #355·#597 판정으로 선언 예보된다(물리 전사 없이)."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="pregate-repository-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.scratch = self.root / "scratch"
        self.scratch.mkdir()
        self.env = dict(os.environ, DJR_FINDINGS_JSON=str(self.root / "findings.jsonl"),
                        DJR_VIOLATIONS_DIR=str(self.root / "violations"), PYTHONDONTWRITEBYTECODE="1")
        self.write(REPOSITORY, REPOSITORY_BASELINE)
        self.write(AGGREGATE, "class FortuneRecord:\n    pass\n")
        _git(self.repo, "init", "-q")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "fixture")

    def write(self, path: str, content: str) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def snapshot(self) -> dict[str, bytes]:
        return {p.relative_to(self.repo).as_posix(): p.read_bytes() for p in sorted(self.repo.rglob("*"))
                if p.is_file() and ".git" not in p.relative_to(self.repo).parts}

    def forecast(self, methods: list[str], *, tag: str = "update", path: str = REPOSITORY,
                 owner: str = "FortuneRecordRepository(ABC)", imports: list[str] = (), aliases: list[str] = ()):
        name = owner.split("(", 1)[0]
        rows = [f"{path}::alias {a}" for a in aliases] + [f"{path}::{owner}"] + [f"{path}::{name}.{m}" for m in methods]
        plan, errors = pg.parse_spec(spec_text([f"{tag} {path}"], rows, [f"{path}  {i}" for i in imports]))
        self.assertEqual(errors, [], " | ".join(errors))
        baseline = pg.repository_baseline(self.repo, plan)
        if tag == "add":
            pg.materialize(self.repo, plan)
        before = self.snapshot()
        found = pg.check_repository_forecast(plan, self.repo, self.scratch, baseline)
        self.assertEqual(self.snapshot(), before, "분석 투영 밖 실물이 바뀌었다")
        return found

    def outcome(self, methods: list[str], **kwargs) -> list[tuple[str, bool]]:
        return sorted((f.rule, f.confirmed) for f in self.forecast(methods, **kwargs))

    def test_field_counterexample_is_confirmed_with_checker_text(self) -> None:
        plan, errors = pg.parse_spec(spec_text([f"update {REPOSITORY}"], [
            f"{REPOSITORY}::FortuneRecordRepository(ABC)", f"{REPOSITORY}::FortuneRecordRepository.{FIELD_METHOD}"]))
        self.assertEqual(errors, [])
        entry = plan.entries[REPOSITORY]
        self.assertEqual((entry.symbols, entry.declarations[0].methods[0].ret), ([], "frozenset[UUID]"))
        found = self.forecast([FIELD_METHOD])
        self.assertEqual([(f.rule, f.path, f.owner, f.detail, f.confirmed) for f in found],
                         [("#355", REPOSITORY, "FortuneRecordRepository.recorded_character_ids", FIELD_DETAIL, True)])
        self.assertTrue(list((self.scratch / "repository-declarations").rglob("fortune_record_repository.py")))
        # 같은 서명을 실물에 넣으면 실검사기가 같은 진단문을 낸다(판정·문면 복제 0).
        self.write(REPOSITORY, REPOSITORY_BASELINE + f"\n    @abstractmethod\n    def {FIELD_METHOD}: ...\n")
        result = subprocess.run([sys.executable, str(SCRIPTS / "check-transaction-boundary.py"), str(self.repo)],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertRegex(result.stdout, rf"\[#355\] {re.escape(REPOSITORY)}:\d+: {re.escape(FIELD_DETAIL)}")

    def test_update_baseline_scopes_new_or_changed_returns_only(self) -> None:
        for methods, expected in [
            (["find(record_id: UUID) -> dict[str, int]"], [("#355", True)]),
            (["find(record_id: UUID) -> FortuneRecord | None"], []),
            (["find(record_id: UUID, lock: bool) -> FortuneRecord | None"], []),
            (["find(record_id: UUID) -> 'FortuneRecord | None'"], []),
            (["legacy_ids(account_id: int) -> frozenset[UUID]"], []),
            (["legacy_ids(account_id: int, limit: int) -> frozenset[UUID]"], []),
            (["delete_old(account_id: int, force: bool) -> None"], []),
        ]:
            with self.subTest(methods=methods):
                self.assertEqual(self.outcome(methods), expected)

    def test_checker_policy_is_preserved_not_tightened(self) -> None:
        for methods, expected in [
            (["latest(account_id: int) -> FortuneRecord | None", "all_for(account_id: int) -> list[FortuneRecord]",
              "summaries(account_id: int) -> tuple[FortuneRecordIndex, ...]", "touch(account_id: int) -> None",
              "pairs(account_id: int) -> tuple[FortuneRecord, UUID]", "unique(account_id: int) -> frozenset[FortuneRecord]",
              "page(account_id: int) -> Page[FortuneRecord]", "untyped(account_id: int)"], []),
            (["save_many(records: list[FortuneRecord]) -> int", "remove_by_ids(ids: frozenset[UUID]) -> frozenset[UUID]",
              "save(record: FortuneRecord) -> dict[str, int]"], []),
            (["exists_for(account_id: int) -> bool"], [("#355", False)]),
            (["count_records(account_id: int) -> int"], [("#355", False)]),
            (["record_numbers(account_id: int) -> list[int]"], [("#355", False)]),
            (["saveSomething(record: FortuneRecord) -> frozenset[UUID]"], [("#355", True)]),
            (["rows(account_id: int) -> QuerySet[FortuneRecord]"], [("#355", True)]),
            (["model(account_id: int) -> FortuneRecordModel"], [("#355", True)]),
            (["delete_many(ids: frozenset[UUID]) -> frozenset[UUID]"], [("#355", True), ("#597", True)]),
            (["delete_many(ids: frozenset[UUID]) -> None"], [("#597", True)]),
            (["store(record: FortuneRecord) -> None", "persist_all(records: list[FortuneRecord]) -> None"],
             [("#597", True), ("#597", True)]),
            (["add_all(records: list[FortuneRecord]) -> None", "update_score(record_id: UUID, score: int) -> None"], []),
        ]:
            with self.subTest(methods=methods):
                self.assertEqual(self.outcome(methods), expected)

    def test_provenance_only_decides_confirmed_or_candidate(self) -> None:
        vo = f"{DOMAIN}.value_object.recorded_character_ids"
        for methods, imports, aliases, expected in [
            (["recorded(account_id: int) -> RecordedCharacterIds"], [], [], [("#355", False)]),
            (["recorded(account_id: int) -> RecordedCharacterIds"], [f"from {vo} import RecordedCharacterIds"], [], []),
            (["recorded(account_id: int) -> Ids"], [f"from {vo} import RecordedCharacterIds as Ids"], [], []),
            (["recorded(account_id: int) -> RecordedCharacterIds"],
             ["from application.fortune_record.domain_layer import RecordedCharacterIds"], [], []),
            (["token(account_id: int) -> Token"], ["from application.shared.a import Token"], [], [("#355", True)]),
            (["token(account_id: int) -> Token"],
             ["from application.shared.a import Token", "from application.shared.b import Token"], [], [("#355", False)]),
            (["token(account_id: int) -> Token"], ["from application.shared.types import *"], [], [("#355", False)]),
            (["ids(account_id: int) -> Ids"], [], ["Ids = frozenset[UUID]"], [("#355", False)]),
        ]:
            with self.subTest(methods=methods, imports=imports, aliases=aliases):
                found = self.forecast(methods, imports=imports, aliases=aliases)
                self.assertEqual(sorted((f.rule, f.confirmed) for f in found), expected)
                for item in found:
                    if not item.confirmed:
                        self.assertIn("예보 불확정", item.detail)
                        self.assertIn("애그리거트도 값 객체도 아니다", item.detail)

    def test_baseline_only_origin_never_confirms_what_the_checker_passes_afterwards(self) -> None:
        baseline = ORDER_HEAD + ORDER_OUTSIDE + ORDER_CLASS
        self.write(ORDER_REPOSITORY, baseline)
        order = dict(path=ORDER_REPOSITORY, owner="OrderRepository(ABC)")
        found = self.forecast(["summary() -> Summary"], **order)
        self.assertEqual([(f.rule, f.path, f.owner, f.confirmed) for f in found],
                         [("#355", ORDER_REPOSITORY, "OrderRepository.summary", False)])
        self.assertIn(f"{SUMMARY_DETAIL} — 예보 불확정: 반환 이름 `Summary` 출처 미해소({BASELINE_ONLY}", found[0].detail)
        self.assertIn("domain 에서 들이면 통과", found[0].detail)
        # 같은 import 를 명세가 적으면 그것이 후상태다 → 확정(문면은 검사기 그대로).
        stated = self.forecast(["summary() -> Summary"], imports=[ORDER_OUTSIDE.strip()], **order)
        self.assertEqual([(f.rule, f.owner, f.detail, f.confirmed) for f in stated],
                         [("#355", "OrderRepository.summary", SUMMARY_DETAIL, True)])
        # 후상태 대조 — 기준선 import 를 그대로 두고 domain import 를 더한 구현은 실검사기 #355 0 · 더하지 않은 구현은 같은 진단문.
        declared = ORDER_CLASS.replace("    pass\n", "    @abstractmethod\n    def summary(self) -> Summary: ...\n")
        for added, hits in [(f"from {SUMMARY_VO} import Summary\n", 0), ("", 1)]:
            with self.subTest(added=added):
                self.write(ORDER_REPOSITORY, ORDER_HEAD + ORDER_OUTSIDE + added + declared)
                result = subprocess.run([sys.executable, str(SCRIPTS / "check-transaction-boundary.py"), str(self.repo)],
                                        env=self.env, capture_output=True, text=True)
                self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
                self.assertEqual(result.stdout.count(f"[#355] {ORDER_REPOSITORY}:"), hits, result.stdout)
                self.assertEqual(len(re.findall(re.escape(SUMMARY_DETAIL), result.stdout)), hits, result.stdout)

    def test_baseline_origin_confirms_only_when_stated_or_standard_library(self) -> None:
        outside = ORDER_HEAD + ORDER_OUTSIDE + ORDER_CLASS
        standard = ORDER_HEAD + "from datetime import datetime\nfrom decimal import Decimal\nfrom uuid import UUID\n" + ORDER_CLASS
        own_class = ORDER_HEAD + "\n\nclass Summary:\n    pass\n" + ORDER_CLASS
        for label, baseline, methods, imports, expected, why in [
            ("기준선에만 있는 프로젝트 import", outside, ["summary() -> Summary"], [], [("#355", False)], BASELINE_ONLY),
            ("같은 import 를 명세가 명시", outside, ["summary() -> Summary"], [ORDER_OUTSIDE.strip()], [("#355", True)], ""),
            ("기준선의 표준 라이브러리 import", standard,
             ["token() -> UUID", "seen_at() -> datetime", "total() -> Decimal"], [], [("#355", True)] * 3, ""),
            ("기준선 밖 + 명세의 다른 밖(상충)", outside, ["summary() -> Summary"],
             ["from support.other_models import Summary"], [("#355", False)], "출처 미해소"),
            ("기준선의 상대 import — 표준 라이브러리와 같은 이름의 형제 모듈", ORDER_HEAD + "from .calendar import Event\n" + ORDER_CLASS,
             ["events() -> Event"], [], [("#355", False)], BASELINE_ONLY),
            ("기준선 밖 + 명세의 domain(같은 이름) — 실검사기 통과 그대로", outside, ["summary() -> Summary"],
             [f"from {SUMMARY_VO} import Summary"], [], ""),
            ("기준선 파일 자기 클래스", own_class, ["summary() -> Summary"], [], [("#355", False)], BASELINE_ONLY),
            ("명세가 선언한 클래스", ORDER_HEAD + ORDER_CLASS, ["twin() -> OrderRepository"], [], [("#355", True)], ""),
        ]:
            with self.subTest(label=label):
                self.write(ORDER_REPOSITORY, baseline)
                found = self.forecast(methods, path=ORDER_REPOSITORY, owner="OrderRepository(ABC)", imports=imports)
                self.assertEqual(sorted((f.rule, f.confirmed) for f in found), expected)
                for item in found:
                    self.assertEqual("예보 불확정" in item.detail, not item.confirmed, item.detail)
                    self.assertEqual(BASELINE_ONLY in item.detail, why == BASELINE_ONLY, item.detail)
                    self.assertIn(why, item.detail)

    def test_root_module_shadowing_a_standard_library_name_is_a_project_origin(self) -> None:
        self.write(ORDER_REPOSITORY, ORDER_HEAD + "from calendar import Event\n" + ORDER_CLASS)
        order = dict(path=ORDER_REPOSITORY, owner="OrderRepository(ABC)")
        self.assertEqual(self.outcome(["events() -> Event"], **order), [("#355", True)])
        self.write("calendar/__init__.py", "class Event:\n    pass\n")
        found = self.forecast(["events() -> Event"], **order)
        self.assertEqual([(f.rule, f.confirmed) for f in found], [("#355", False)])
        self.assertIn(BASELINE_ONLY, found[0].detail)

    def test_source_root_package_shadowing_a_standard_library_name_is_a_project_origin(self) -> None:
        # source root 는 저장소 루트다(검사기가 고르는 BC 는 뿌리 `application/` 에만 있다) — 그 아래 패키지 `calendar` 가 표준 라이브러리
        # 이름을 가린다.
        order = dict(path=ORDER_REPOSITORY, owner="OrderRepository(ABC)")
        self.write(ORDER_REPOSITORY, ORDER_HEAD + "from calendar.read_models import CalendarSummary\n" + ORDER_CLASS)
        self.write("calendar/__init__.py", "")
        self.write("calendar/read_models.py", "class CalendarSummary:\n    pass\n")
        found = self.forecast(["calendar_summary() -> CalendarSummary"], **order)
        self.assertEqual([(f.rule, f.path, f.owner, f.confirmed) for f in found],
                         [("#355", ORDER_REPOSITORY, "OrderRepository.calendar_summary", False)])
        self.assertIn(BASELINE_ONLY, found[0].detail)
        # 후상태 대조 — 구현이 같은 이름의 domain 값 객체를 들이면 실검사기는 그 메서드를 통과시킨다.
        self.write(ORDER_REPOSITORY, ORDER_HEAD + f"from {SUMMARY_VO.replace('.summary', '.calendar_summary')} import CalendarSummary\n"
                   + ORDER_CLASS.replace("    pass\n", "    @abstractmethod\n    def calendar_summary(self) -> CalendarSummary: ...\n"))
        result = subprocess.run([sys.executable, str(SCRIPTS / "check-transaction-boundary.py"), str(self.repo)],
                                env=self.env, capture_output=True, text=True)
        self.assertIn(f"[#355] {REPOSITORY}:", result.stdout)
        self.assertNotIn(ORDER_REPOSITORY, result.stdout)
        for label, baseline, method, expected in [
            ("source root 의 패키지를 첫 마디로 들임", ORDER_HEAD + "from calendar import Event\n", "events() -> Event", False),
            ("가림 없는 표준 라이브러리 import", ORDER_HEAD + "from uuid import UUID\n", "token() -> UUID", True),
            ("표준 라이브러리 패키지의 하위 모듈", ORDER_HEAD + "from collections.abc import Mapping\n",
             "index() -> Mapping[int, int]", True),
        ]:
            with self.subTest(label=label):
                self.write(ORDER_REPOSITORY, baseline + ORDER_CLASS)
                found = self.forecast([method], **order)
                self.assertEqual([(f.rule, f.confirmed) for f in found], [("#355", expected)])
                self.assertEqual(BASELINE_ONLY in found[0].detail, not expected, found[0].detail)
        # 가리는 폴더를 못 찾아도(다른 import 경로 · 네임스페이스), 표준 `fractions` 는 하위 모듈을 가진 패키지가 아니라서
        # `fractions.read_models` 는 표준 라이브러리 출처로 치지 않는다. 첫 마디로 들인 표준 모듈은 그대로 확정 근거다.
        for label, baseline, method, expected in [
            ("패키지가 아닌 표준 모듈의 하위 모듈 꼴", ORDER_HEAD + "from fractions.read_models import Ratio\n",
             "ratio() -> Ratio", False),
            ("표준 모듈 첫 마디(가림 없음)", ORDER_HEAD + "from fractions import Fraction\n", "ratio() -> Fraction", True),
        ]:
            with self.subTest(label=label):
                self.write(ORDER_REPOSITORY, baseline + ORDER_CLASS)
                found = self.forecast([method], path=ORDER_REPOSITORY, owner="OrderRepository(ABC)")
                self.assertEqual([(f.rule, f.confirmed) for f in found], [("#355", expected)])

    def test_baseline_debt_of_another_class_does_not_hide_a_new_method(self) -> None:
        # F4-115 검토 반례 K11 꼴 — G2 registry 집합 차분은 이 줄을 기존으로 보지만(귀속 0) 실검사기 줄은 1 → 2 다. 저장소 예보는
        # 그대로 엄격하게 확정한다(F4-73 차단 A · 도메인 서비스 예보의 «다른 소유자» 셋 가름과 기준이 다르다 — S5 사각 문구).
        self.write(ORDER_REPOSITORY, LEGACY_ORDER_BASELINE)

        def order_lines() -> int:
            result = subprocess.run([sys.executable, str(SCRIPTS / "check-transaction-boundary.py"), str(self.repo)],
                                    env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            return len(re.findall(rf"\[#355\] {re.escape(ORDER_REPOSITORY)}:\d+: {re.escape(OWNER_DETAIL)}", result.stdout))

        found = self.forecast(["owner_id() -> UUID"], path=ORDER_REPOSITORY, owner="OrderRepository(ABC)")
        self.assertEqual([(f.rule, f.owner, f.detail, f.confirmed) for f in found],
                         [("#355", "OrderRepository.owner_id", OWNER_DETAIL, True)])
        # 후상태 대조 — 실검사기는 새 클래스의 메서드에도 줄을 낸다(1 → 2).
        self.assertEqual(order_lines(), 1)
        self.write(ORDER_REPOSITORY, LEGACY_ORDER_BASELINE.replace(
            ORDER_CLASS, ORDER_CLASS.replace("    pass\n", "    @abstractmethod\n    def owner_id(self) -> UUID: ...\n")))
        self.assertEqual(order_lines(), 2)

    def test_baseline_debt_is_excluded_only_for_its_owner_and_in_file_heirs_get_a_candidate(self) -> None:
        restated = ["legacy_ids(account_id: int) -> frozenset[UUID]", "delete_old(account_id: int) -> None"]
        new = [("#355", True), ("#597", True)]
        inherited = [("#355", False), ("#597", False)]
        heirs = {"파일 안 직계 상속", "파일 안 2단 상속", "새 클래스 — 파일 안 베이스", "물려받은 bool/int 후보 다시 적기"}
        ambiguous = OWNED_BASELINE.replace("from uuid import UUID\n", "from uuid import UUID\n\n"
                                           "from application.legacy.repositories import FortuneRecordRepository\n", 1)
        for label, baseline, owner, methods, expected in [
            ("상속 관계 없는 다른 클래스", OWNED_BASELINE, "UnrelatedRecordRepository(ABC)", restated, new),
            ("파일 안 직계 상속", OWNED_BASELINE, "ArchivedFortuneRecordRepository(FortuneRecordRepository)", restated,
             inherited),
            ("파일 안 2단 상속", OWNED_BASELINE, "DeepArchiveRepository(ArchivedFortuneRecordRepository)", restated, inherited),
            ("새 클래스 — 파일 안 베이스", OWNED_BASELINE, "FreshRepository(FortuneRecordRepository)", restated, inherited),
            ("새 클래스 — 베이스 ABC", OWNED_BASELINE, "FreshRepository(ABC)", restated, new),
            ("같은 클래스지만 명세의 베이스가 다름", OWNED_BASELINE, "ArchivedFortuneRecordRepository(ABC)", restated, new),
            ("베이스가 다른 파일의 클래스", OWNED_BASELINE, "ImportedBaseRepository(BaseRecordRepository)", restated, new),
            ("베이스 이름이 import 와 그 파일의 클래스 둘", ambiguous,
             "ArchivedFortuneRecordRepository(FortuneRecordRepository)", restated, new),
            ("베이스 클래스 정의가 기준선에 둘", OWNED_BASELINE + "\n\nclass FortuneRecordRepository(ABC):\n    pass\n",
             "FreshRepository(FortuneRecordRepository)", restated, new),
            ("같은 소유자의 bool/int 후보 다시 적기", OWNED_BASELINE, "FortuneRecordRepository(ABC)",
             ["count_records(account_id: int) -> bool"], []),
            ("물려받은 bool/int 후보 다시 적기", OWNED_BASELINE, "ArchivedFortuneRecordRepository(FortuneRecordRepository)",
             ["count_records(account_id: int) -> bool"], [("#355", False)]),
            ("다른 소유자의 같은 bool/int 후보", OWNED_BASELINE, "UnrelatedRecordRepository(ABC)",
             ["count_records(account_id: int) -> bool"], [("#355", False)]),
            ("조상에게는 복합문 아래에만 있는 메서드(검사기 줄 없음)를 자식이 적음", OWNED_BASELINE,
             "ArchivedFortuneRecordRepository(FortuneRecordRepository)", ["guarded(account_id: int) -> frozenset[UUID]"],
             [("#355", True)]),
        ]:
            with self.subTest(label=label):
                self.write(REPOSITORY, baseline)
                found = self.forecast(methods, owner=owner)
                self.assertEqual(sorted((f.rule, f.confirmed) for f in found), expected)
                # 조상과만 겹친 후보는 겹친 조상(여기서는 줄을 가진 유일한 조상)을 사유에 적는다 — 다른 칸에는 없다.
                for item in found:
                    self.assertEqual(heir_reason("FortuneRecordRepository", item.owner.split(".")[1]) in item.detail,
                                     label in heirs, item.detail)

    def test_heir_turning_its_own_passing_method_into_the_ancestor_debt_is_a_candidate(self) -> None:
        # 재검토 반례 둘 — 자식이 기준선에서 직접 정의하던 통과 메서드를 조상의 위반 꼴로 바꾼다. 판정문이 조상의 기존 줄과
        # 같아도 지우지 않는다(실검사기는 자식에게도 새 줄을 낸다 · 1 → 2).
        def order_lines(detail: str) -> int:
            result = subprocess.run([sys.executable, str(SCRIPTS / "check-transaction-boundary.py"), str(self.repo)],
                                    env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            return len(re.findall(rf"\[#355\] {re.escape(ORDER_REPOSITORY)}:\d+: {re.escape(detail)}", result.stdout))

        for label, baseline, ancestor, method, detail, changed in [
            ("값 객체 반환 → 조상의 원시 식별자", HEIR_OWNER_BASELINE, "LegacyOrderRepository", "owner_id() -> UUID",
             OWNER_DETAIL, ("def owner_id(self) -> OwnerId", "def owner_id(self) -> UUID")),
            ("애그리거트 반환 → 조상의 frozenset", HEIR_IDS_BASELINE, "BaseOrderRepository", "ids() -> frozenset[UUID]",
             IDS_DETAIL, ("def ids(self) -> Order | None", "def ids(self) -> frozenset[UUID]")),
        ]:
            with self.subTest(label=label):
                self.write(ORDER_REPOSITORY, baseline)
                name = method.split("(")[0]
                found = self.forecast([method], path=ORDER_REPOSITORY, owner=f"OrderRepository({ancestor})")
                self.assertEqual([(f.rule, f.path, f.owner, f.confirmed) for f in found],
                                 [("#355", ORDER_REPOSITORY, f"OrderRepository.{name}", False)])
                # 자식이 기준선에서 직계로 정의하던 메서드다 — 사유는 «예보가 가를 수 없다» 가 아니라 그 사실을 적는다.
                self.assertTrue(found[0].detail.startswith(f"{detail} — {own_def_reason(ancestor, name)} — "), found[0].detail)
                self.assertNotIn(heir_reason(ancestor, name), found[0].detail)
                self.assertIn(f" — {heir_question(ancestor)}", found[0].detail)
                self.assertTrue(found[0].detail.endswith(g2_clause(ancestor)), found[0].detail)
                # 후상태 대조 — 자식의 반환을 명세대로 바꾼 구현은 실검사기 같은 판정문 줄이 1 → 2.
                self.assertEqual(order_lines(detail), 1)
                self.write(ORDER_REPOSITORY, baseline.replace(*changed))
                self.assertEqual(order_lines(detail), 2)
        # 같은 클래스 자기의 기존 빚을 다시 적으면(조상에도 같은 판정문) 지금처럼 뺀다.
        own = HEIR_OWNER_BASELINE.replace("def owner_id(self) -> OwnerId", "def owner_id(self) -> UUID")
        self.write(ORDER_REPOSITORY, own)
        self.assertEqual(self.outcome(["owner_id() -> UUID"], path=ORDER_REPOSITORY,
                                      owner="OrderRepository(LegacyOrderRepository)"), [])
        # 조상이 여럿이면 사슬에서 처음 겹친(가까운) 조상 하나를 적는다.
        middle = own.replace("class OrderRepository(LegacyOrderRepository):",
                             "class MiddleOrderRepository(LegacyOrderRepository):")
        middle += "\n\nclass ArchivedOrderRepository(MiddleOrderRepository):\n    pass\n"
        self.write(ORDER_REPOSITORY, middle)
        found = self.forecast(["owner_id() -> UUID"], path=ORDER_REPOSITORY,
                              owner="ArchivedOrderRepository(MiddleOrderRepository)")
        self.assertEqual([(f.rule, f.confirmed) for f in found], [("#355", False)])
        self.assertIn(heir_reason("MiddleOrderRepository", "owner_id"), found[0].detail)
        self.assertNotIn("LegacyOrderRepository", found[0].detail)
        self.assertTrue(found[0].detail.endswith(g2_clause("MiddleOrderRepository")), found[0].detail)

    def test_heir_candidate_names_the_nearest_definition_when_an_intermediate_ancestor_redefines(self) -> None:
        # 사이 조상 — 기존 빚은 먼 조상 `A` 에 있고 가까운 조상 `B` 가 같은 메서드를 다른 꼴로 직계 정의한다. 자식이 실제로
        # 물려받는 정의는 `B` 다 — 사유 · 물음이 «물려받는 정의» 와 «기존 빚이 있는 조상» 을 가른다(판정은 후보 그대로).
        head = (ORDER_HEAD + "from uuid import UUID\n\n"
                "from application.orders.domain_layer.order.value_object.owner_id import OwnerId\n\n\n"
                "class A(ABC):\n    @abstractmethod\n    def b_id(self) -> UUID: ...\n\n\n")
        middle = "class B(A):\n    @abstractmethod\n    def b_id(self) -> OwnerId: ...\n\n\n"
        heir = "class OrderRepository(B):\n    pass\n"
        detail = "`b_id` 반환 `UUID` 이 애그리거트도 값 객체도 아니다"
        self.write(ORDER_REPOSITORY, head + middle + heir)
        found = self.forecast(["b_id() -> UUID"], path=ORDER_REPOSITORY, owner="OrderRepository(B)")
        self.assertEqual([(f.rule, f.path, f.owner, f.confirmed, f.detail) for f in found], [(
            "#355", ORDER_REPOSITORY, "OrderRepository.b_id", False,
            f"{detail} — 예보 불확정: 같은 판정문의 기존 줄이 조상 `A.b_id` 에 있지만 이 클래스가 물려받는 정의는 더 가까운 "
            "조상 `B.b_id` 이고 그 정의에는 같은 판정문의 줄이 없다(이 클래스에서 재정의하는 것인지 예보가 가를 수 없다) — "
            "물음: 이 메서드는 가장 가까운 정의(`B.b_id`)를 그대로 물려받는가(그러면 검사기는 이 클래스에 줄을 내지 않는다) · "
            + g2_clause("A"))])
        # 자식도 기준선에서 직계로 정의하던 꼴 — 사유는 그 사실, 물음의 «물려받는 정의» 는 여전히 가까운 조상 `B`.
        self.write(ORDER_REPOSITORY, head + middle + heir.replace("    pass\n",
                                                                "    @abstractmethod\n    def b_id(self) -> OwnerId: ...\n"))
        found = self.forecast(["b_id() -> UUID"], path=ORDER_REPOSITORY, owner="OrderRepository(B)")
        self.assertEqual([(f.rule, f.path, f.owner, f.confirmed) for f in found],
                         [("#355", ORDER_REPOSITORY, "OrderRepository.b_id", False)])
        self.assertTrue(found[0].detail.startswith(f"{detail} — {own_def_reason('A', 'b_id')} — 물음: 이 메서드는 가장 가까운 "
                                                   "정의(`B.b_id`)를 그대로 물려받는가"), found[0].detail)
        # 사이 조상이 그 메서드를 정의하지 않으면 물려받는 정의 = 기존 빚이 있는 조상 — 지금처럼 하나만 적는다.
        self.write(ORDER_REPOSITORY, head + "class B(A):\n    pass\n\n\n" + heir)
        found = self.forecast(["b_id() -> UUID"], path=ORDER_REPOSITORY, owner="OrderRepository(B)")
        self.assertEqual([(f.rule, f.path, f.owner, f.confirmed) for f in found],
                         [("#355", ORDER_REPOSITORY, "OrderRepository.b_id", False)])
        self.assertTrue(found[0].detail.startswith(f"{detail} — {heir_reason('A', 'b_id')}(물려받은 빚을"), found[0].detail)
        self.assertIn(f" — {heir_question('A')}(그러면 기존 빚이다) · {g2_clause('A')}", found[0].detail)
        self.assertNotIn("`B", found[0].detail)
        # 후상태 대조 — 사이 조상 꼴에서 명세대로 자식이 재정의하면 실검사기 같은 판정문 줄이 1 → 2(물려받으면 1 그대로).
        lines = []
        for body in (head + middle + heir, head + middle + heir.replace(
                "    pass\n", "    @abstractmethod\n    def b_id(self) -> UUID: ...\n")):
            self.write(ORDER_REPOSITORY, body)
            result = subprocess.run([sys.executable, str(SCRIPTS / "check-transaction-boundary.py"), str(self.repo)],
                                    env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            lines.append(len(re.findall(rf"\[#355\] {re.escape(ORDER_REPOSITORY)}:\d+: {re.escape(detail)}", result.stdout)))
        self.assertEqual(lines, [1, 2])

    def test_heir_candidate_says_the_class_changes_its_own_baseline_definition(self) -> None:
        # 자식 직계 정의 — 자식이 기준선에서 직접 정의하던 반환을 조상의 기존 빚 꼴로 바꾸는 명세. 예보는 그 사실을 이미 안다 —
        # 사유를 «예보가 가를 수 없다» 가 아니라 사실대로 적는다(판정은 후보 그대로).
        self.write(ORDER_REPOSITORY, HEIR_OWNER_BASELINE)
        found = self.forecast(["owner_id() -> UUID"], path=ORDER_REPOSITORY, owner="OrderRepository(LegacyOrderRepository)")
        self.assertEqual([(f.rule, f.path, f.owner, f.confirmed, f.detail) for f in found], [(
            "#355", ORDER_REPOSITORY, "OrderRepository.owner_id", False,
            f"{OWNER_DETAIL} — 예보 불확정: 이 클래스가 기준선에서 직접 정의하던 반환을 조상 `LegacyOrderRepository.owner_id` "
            "의 기존 빚과 같은 꼴(같은 판정문)로 바꾼다 — 물음: 이 메서드는 조상 `LegacyOrderRepository` 의 선언을 그대로 "
            "물려받는가(그러면 기존 빚이다) · " + g2_clause("LegacyOrderRepository"))])
        # 자식이 기준선에서 정의하지 않던 꼴(물려받은 빚을 다시 적음)은 «가를 수 없다» 사유 그대로다.
        self.write(ORDER_REPOSITORY, LEGACY_ORDER_BASELINE.replace("class OrderRepository(ABC):",
                                                                   "class OrderRepository(LegacyOrderRepository):"))
        found = self.forecast(["owner_id() -> UUID"], path=ORDER_REPOSITORY, owner="OrderRepository(LegacyOrderRepository)")
        self.assertEqual([(f.rule, f.path, f.owner, f.confirmed) for f in found],
                         [("#355", ORDER_REPOSITORY, "OrderRepository.owner_id", False)])
        self.assertTrue(found[0].detail.startswith(f"{OWNER_DETAIL} — {heir_reason('LegacyOrderRepository', 'owner_id')}"
                                                   "(물려받은 빚을 다시 적은 것인지"), found[0].detail)
        self.assertNotIn("직접 정의하던", found[0].detail)

    def test_method_only_under_a_compound_statement_is_a_candidate(self) -> None:
        self.write(REPOSITORY, DEBT_BASELINE)
        for label, method, expected in [
            ("반환 그대로", "guarded(account_id: int) -> frozenset[UUID]", [("#355", False)]),
            ("반환을 금지 이름으로", "guarded(account_id: int) -> dict[str, int]", [("#355", False)]),
            ("쓰기 이름", "delete_guarded(account_id: int) -> None", [("#597", False)]),
            ("통과하는 반환", "guarded(account_id: int) -> FortuneRecord | None", []),
        ]:
            with self.subTest(label=label):
                found = self.forecast([method])
                self.assertEqual([(f.rule, f.confirmed) for f in found], expected)
                for item in found:
                    self.assertIn(f"예보 불확정: 기준선 메서드 `FortuneRecordRepository.{method.split('(')[0]}` 가 클래스 직계가 "
                                  "아니라 조건·복합문 아래에 있다", item.detail)
                    self.assertIn("물음: 구현 뒤 이 메서드를 클래스 직계에 두는가", item.detail)

        # 후상태 대조 — 실검사기는 클래스 직계 정의만 본다: 직계로 올리면 새 줄이 서고, 그 자리에 두면 반환을 바꿔도 0줄이다.
        def judged_lines() -> set[str]:
            result = subprocess.run([sys.executable, str(SCRIPTS / "check-transaction-boundary.py"), str(self.repo)],
                                    env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            return {re.sub(r":\d+", ":N", line.strip()) for line in result.stdout.splitlines()
                    if REPOSITORY in line and line.strip().startswith(("[#355]", "[#597]"))}

        nested = ("    if TYPE_CHECKING:\n        def guarded(self, account_id: int) -> frozenset[UUID]: ...\n"
                  "        def delete_guarded(self, account_id: int) -> None: ...\n")
        self.assertIn(nested, DEBT_BASELINE)
        before = judged_lines()
        self.write(REPOSITORY, DEBT_BASELINE.replace(nested, nested.replace("    if TYPE_CHECKING:\n", "").replace("        def", "    def")))
        self.assertEqual(judged_lines() - before, {
            f"[#355] {REPOSITORY}:N: `guarded` 반환 `UUID.frozenset` 이 애그리거트도 값 객체도 아니다",
            f"[#597] {REPOSITORY}:N: 쓰기 메서드 `delete_guarded` — 애그리거트 리포지토리의 쓰기 이름은 save·remove 로 시작한다"
            "(갈리면 「한 트랜잭션 = 애그리거트 하나」(#546) 검사가 못 선다)"})
        self.write(REPOSITORY, DEBT_BASELINE.replace("def guarded(self, account_id: int) -> frozenset[UUID]",
                                                    "def guarded(self, account_id: int) -> dict[str, int]"))
        self.assertEqual(judged_lines(), before)

    def test_forecast_leaves_no_records_or_violation_history(self) -> None:
        # 기준선 판정(위반 · 후보)과 대상 선택(#282 — 이름이 어긋난 저장소 파일)이 모두 도는 배치.
        self.write(REPOSITORY, OWNED_BASELINE)
        self.write("application/fortune_record/domain_layer/fortune_record/record_repository.py", "class Store:\n    pass\n")
        marker = self.repo / ".dddjango"
        marker.mkdir()
        records = self.root / "records.jsonl"
        history = self.root / "history"
        methods = ["other_ids(account_id: int) -> frozenset[UUID]", "delete_new(account_id: int) -> None",
                   "exists_for(account_id: int) -> bool"]
        expected = [("#355", False), ("#355", True), ("#597", True)]
        base = {key: value for key, value in os.environ.items() if key not in ("DJR_FINDINGS_JSON", "DJR_VIOLATIONS_DIR")}
        for label, extra in [("레코드 파일", {"DJR_FINDINGS_JSON": str(records)}),
                             ("위반 이력 폴더", {"DJR_VIOLATIONS_DIR": str(history)}),
                             ("설치 표식 저장소", {})]:
            with self.subTest(sink=label), mock.patch.dict(os.environ, dict(base, **extra), clear=True), \
                    mock.patch.object(pg.findings, "_target_root", self.repo), \
                    contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(self.outcome(methods), expected)
                self.assertEqual(out.getvalue(), "")
                self.assertFalse(records.exists())
                self.assertFalse(history.exists())
                self.assertEqual(list(marker.iterdir()), [])

    def test_restated_baseline_debt_is_not_forecast_again(self) -> None:
        self.write(REPOSITORY, DEBT_BASELINE)
        archived = "ArchivedFortuneRecordRepository(FortuneRecordRepository)"
        own = "FortuneRecordRepository(ABC)"
        for label, owner, methods, expected in [
            ("Optional → | None", own, ["legacy_opt(account_id: int) -> UUID | None"], []),
            ("tuple → list", own, ["legacy_many(account_id: int) -> list[UUID]"], []),
            ("dict 값 타입만", own, ["legacy_rows(account_id: int) -> dict[str, str]"], []),
            ("물려받은 메서드(조상과만 겹침 = 후보)", archived, ["legacy_ids(account_id: int) -> frozenset[UUID]",
                                                  "delete_old(account_id: int) -> None"], [("#355", False), ("#597", False)]),
            ("금지 A → 금지 B", own, ["legacy_opt(account_id: int) -> dict[str, int]"], [("#355", True)]),
            ("정상 → 위반", own, ["find(record_id: UUID) -> UUID | None"], [("#355", True)]),
            ("같은 반환의 새 이름", own, ["other_ids(account_id: int) -> frozenset[UUID]"], [("#355", True)]),
            ("물려받은 메서드의 반환 변경", archived, ["legacy_ids(account_id: int) -> dict[str, int]"], [("#355", True)]),
            ("새 쓰기 이름", archived, ["delete_new(account_id: int) -> None"], [("#597", True)]),
        ]:
            with self.subTest(label=label):
                self.assertEqual(self.outcome(methods, owner=owner), expected)

        # 실검사기 대조 — 다시 적은 후상태의 저장소 줄은 행 번호만 지우면 기준선과 같다(registry 차분 = 귀속 0).
        def repository_lines() -> set[str]:
            result = subprocess.run([sys.executable, str(SCRIPTS / "check-transaction-boundary.py"), str(self.repo)],
                                    env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            return {re.sub(r":\d+", ":N", line.strip()) for line in result.stdout.splitlines() if REPOSITORY in line}

        before = repository_lines()
        self.assertIn(f"[#355] {REPOSITORY}:N: `legacy_opt` 반환 `UUID` 이 애그리거트도 값 객체도 아니다", before)
        self.write(REPOSITORY, DEBT_RESTATED)
        self.assertEqual(repository_lines(), before)

    def test_one_certainly_outside_name_confirms_and_uppercase_builtins_do_not(self) -> None:
        warning = f"from {DOMAIN}.value_object.warning import Warning"
        for label, methods, imports, expected in [
            ("섞인 꼴 — 새 값 객체 + 표준 라이브러리 이름", ["pairs_of(account_id: int) -> tuple[RecordKind, UUID]"], [],
             [("#355", True)]),
            ("import 없는 frozenset[새 값 객체] — 소문자 내장", ["kinds(account_id: int) -> frozenset[RecordKind]"], [],
             [("#355", True)]),
            ("소문자 내장", ["raw(account_id: int) -> bytes"], [], [("#355", True)]),
            ("대문자 내장과 같은 이름 — import 무기재", ["warnings(account_id: int) -> tuple[Warning, ...]"], [],
             [("#355", False)]),
            ("대문자 내장과 같은 이름 — domain import 명시", ["warnings(account_id: int) -> tuple[Warning, ...]"], [warning], []),
            ("import * 는 표준 라이브러리 import 도 가린다", ["ids(account_id: int) -> tuple[UUID, ...]"],
             ["from application.shared.types import *"], [("#355", False)]),
        ]:
            with self.subTest(label=label):
                found = self.forecast(methods, imports=imports)
                self.assertEqual(sorted((f.rule, f.confirmed) for f in found), expected)
                for item in found:
                    self.assertEqual("출처 미해소(import 무기재" in item.detail, not item.confirmed, item.detail)
        # 후상태 대조 — 값 객체 `Warning` 을 domain 에서 들인 구현은 실검사기가 그 메서드를 통과시킨다.
        self.write(REPOSITORY, REPOSITORY_BASELINE.replace("\n\n\nclass", f"\n{warning}\n\n\nclass")
                   + "\n    @abstractmethod\n    def warnings(self, account_id: int) -> tuple[Warning, ...]: ...\n")
        result = subprocess.run([sys.executable, str(SCRIPTS / "check-transaction-boundary.py"), str(self.repo)],
                                env=self.env, capture_output=True, text=True)
        self.assertIn("`legacy_ids` 반환", result.stdout)
        self.assertNotIn("`warnings`", result.stdout)

    def test_plan_path_spelling_does_not_hide_the_repository(self) -> None:
        for spelled in (f"./{REPOSITORY}", REPOSITORY.replace("/", "//", 1)):
            with self.subTest(path=spelled):
                found = self.forecast([FIELD_METHOD], path=spelled)
                self.assertEqual([(f.rule, f.path, f.owner, f.detail, f.confirmed) for f in found],
                                 [("#355", REPOSITORY, "FortuneRecordRepository.recorded_character_ids", FIELD_DETAIL, True)])

    def test_baseline_is_read_before_the_spec_is_materialized(self) -> None:
        spec = self.root / "design.md"
        spec.write_text(spec_text([f"update {REPOSITORY}"], [
            f"{REPOSITORY}::FortuneRecordRepository(ABC)", f"{REPOSITORY}::FortuneRecordRepository.{FIELD_METHOD}"]),
            encoding="utf-8")
        real_materialize = pg.materialize

        def transcribing(copy: Path, plan, **kwargs):
            # 전사가 저장소 파일에 새 서명을 써 넣는다고 해도, 비교 기준선은 그 «전» 실물이어야 한다.
            report = real_materialize(copy, plan, **kwargs)
            target = copy / REPOSITORY
            target.write_text(target.read_text(encoding="utf-8") + "\n    @abstractmethod\n    def "
                              + FIELD_METHOD.replace("(", "(self, ", 1) + ": ...\n", encoding="utf-8")
            return report

        out = io.StringIO()
        quiet = {key: self.env[key] for key in ("DJR_FINDINGS_JSON", "DJR_VIOLATIONS_DIR")}
        with mock.patch.object(pg, "materialize", side_effect=transcribing), mock.patch.dict(os.environ, quiet), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = pg.main([str(spec), str(self.repo), "--report", str(self.root / "report.md")])
        self.assertEqual(code, 2, out.getvalue())
        self.assertIn(f"FortuneRecordRepository.recorded_character_ids: {FIELD_DETAIL}", out.getvalue())

    def test_targets_follow_checker_selection_without_name_or_base_rules(self) -> None:
        self.assertEqual(self.outcome(["ids(account_id: int) -> frozenset[UUID]"], owner="Store"), [("#355", True)])
        # 이름이 어긋난 파일도 대상이고, 자기 애그리거트는 폴더 이름(`FortuneRecord`)이 아니라 파일 이름(`record_repository` → `Record`)이다.
        misnamed = "application/fortune_record/domain_layer/fortune_record/record_repository.py"
        found = self.forecast(["mine(account_id: int) -> frozenset[Record]", "latest(account_id: int) -> Record | None",
                               "theirs(account_id: int) -> frozenset[FortuneRecord]"], tag="add", path=misnamed, owner="Store")
        self.assertEqual([(f.rule, f.owner, f.detail, f.confirmed) for f in found],
                         [("#355", "Store.theirs", "`theirs` 반환 `FortuneRecord.frozenset` 이 애그리거트도 값 객체도 아니다", True)])
        for outside in ("application/fortune_record/domain_layer/fortune_record/repository/fortune_record_repository.py",
                        "application/fortune_record/driven_layer/fortune_record/fortune_record_repository.py"):
            with self.subTest(path=outside):
                self.assertEqual(self.outcome([FIELD_METHOD], tag="add", path=outside,
                                              imports=["from uuid import UUID"]), [])

    def test_add_counts_every_declared_method_despite_own_stub(self) -> None:
        added = "application/fortune_record/domain_layer/character/character_repository.py"
        found = self.forecast([FIELD_METHOD, "exists_for(account_id: int) -> bool"], tag="add", path=added,
                              owner="CharacterRepository(ABC)", imports=["from uuid import UUID"])
        self.assertIn("recorded_character_ids", (self.repo / added).read_text())
        self.assertEqual(sorted((f.rule, f.owner, f.confirmed) for f in found),
                         [("#355", "CharacterRepository.exists_for", False),
                          ("#355", "CharacterRepository.recorded_character_ids", True)])

    def test_unreadable_or_ambiguous_baseline_never_confirms(self) -> None:
        duplicate = REPOSITORY_BASELINE + "\n\nclass FortuneRecordRepository(ABC):\n    pass\n"
        for baseline in (duplicate, REPOSITORY_BASELINE.replace("def legacy_ids", "def find"),
                         "class FortuneRecordRepository(:\n"):
            with self.subTest(baseline=baseline[-40:]):
                self.write(REPOSITORY, baseline)
                found = self.forecast(["find(record_id: UUID) -> dict[str, int]"])
                self.assertEqual([(f.rule, f.confirmed) for f in found], [("#355", False)])
                self.assertIn("예보 불확정", found[0].detail)
        # 비교 불능(기준선 중복) 후보는 «기준선에 같은 판정문이 있다» 로 지우지 않는다 — 어느 정의와 견줄지 모르기 때문이다.
        for baseline, method, why in [
            (duplicate, "legacy_ids(account_id: int) -> frozenset[UUID]", "기준선 클래스 `FortuneRecordRepository` 중복"),
            (REPOSITORY_BASELINE.replace("def legacy_ids", "def find"), "find(record_id: UUID) -> frozenset[UUID]",
             "기준선 메서드 `FortuneRecordRepository.find` 중복"),
        ]:
            with self.subTest(why=why):
                self.write(REPOSITORY, baseline)
                found = self.forecast([method])
                self.assertEqual([(f.rule, f.confirmed) for f in found], [("#355", False)])
                self.assertIn(f"예보 불확정: {why}", found[0].detail)

    def test_bundled_checker_load_failure_is_run_error(self) -> None:
        plan, _ = pg.parse_spec(spec_text([f"update {REPOSITORY}"], [
            f"{REPOSITORY}::FortuneRecordRepository(ABC)", f"{REPOSITORY}::FortuneRecordRepository.{FIELD_METHOD}"]))
        with mock.patch.object(pg, "TRANSACTION_CHECKER", self.root / "missing-checker.py"), \
                mock.patch.object(pg, "_TRANSACTION_CHECKER_MODULE", None):
            with self.assertRaises(pg.RunError):
                pg.check_repository_forecast(plan, self.repo, self.scratch, pg.repository_baseline(self.repo, plan))


# F4-115 — update 도메인 서비스 칸 서명(#304 · #305 · #307 · #308)과 OHS 창구 번역 출처 칸(#474 · #62)의 선언 예보. 가짜 이름(정원 · 식물).
GARDEN = "application/garden"
PLANT_IMPORT = "from application.garden.domain_layer.plant.plant import Plant\n"
REPOSITORY_IMPORT = "from application.garden.domain_layer.plant.plant_repository import PlantRepository\n"
POLICY = f"{GARDEN}/domain_layer/domain_service/watering.py"
POLICY_HEAD = '"""Which plants need water."""\nfrom __future__ import annotations\n\n' + PLANT_IMPORT
DUE = "    def due(self, plants: tuple[Plant, ...]) -> tuple[Plant, ...]:\n        return plants\n"
LEGACY = "    def is_legacy(self, plant: Plant) -> bool:\n        return False\n"
POLICY_BASELINE = POLICY_HEAD + "\n\nclass WateringPolicy:\n" + DUE + "\n" + LEGACY
DUE_ROW = f"{POLICY}::WateringPolicy.due(plants: tuple[Plant, ...]) -> tuple[Plant, ...]"
CATALOG = f"{GARDEN}/driving_layer/open_host_service/catalog"
CATALOG_SERVICE = f"{CATALOG}/catalog_service.py"
UNREADABLE_IMPORT = "from application.garden.domain_layer.plant.exception.plant_unreadable import PlantUnreadable"
CATALOG_BASELINE = ('"""Garden catalog open host service."""\nfrom __future__ import annotations\n\n'
                    f"{UNREADABLE_IMPORT}\n"
                    "from application.garden.driving_layer.open_host_service.catalog.contract.exception."
                    "plant_unavailable_exception import PlantUnavailableException\n\n\n"
                    "def read_plant_query(name: str) -> str:\n    try:\n        return _read(name)\n"
                    "    except PlantUnreadable:\n        raise PlantUnavailableException() from None\n\n\n"
                    "def _read(name: str) -> str:\n    raise PlantUnreadable(name)\n")
CATALOG_LOGGED = CATALOG_BASELINE.replace(
    "    except PlantUnreadable:\n",
    "    except PlantUnreadable as unreadable:\n        print(unreadable)\n")
CAUGHT_DETAIL = "도메인 예외를 `as _caught` 로 묶어 참조했다 — 입구 파일은 도메인 예외를 «타입»으로만 쓴다"
STALE_MEMO = "S5 입구 catch 확인(출처 칸 `as` 없음 — OHS 는 잡은 도메인 예외 값을 쓰지 않는다(R-3690)"
BLANK_MEMO = "S5 입구 catch 미검증(번역 출처 칸 무기재"
OUTSIDE_MEMO = "번역 출처 칸 판정 밖(검사기 OHS 창구 아님 — 판정 0)"


def bool_detail(name: str) -> str:
    return f"`{name}` 이 bool 을 돌려준다 — 규칙 위반의 알림은 «도메인 예외»다"


def catch_spec(paths: list[str], rows: list[str], symbols: list[str] = (), imports: list[str] = ()) -> str:
    return (spec_text(paths, symbols, imports)
            + "<!-- machine: exception-map -->\n```exceptions\n" + "\n".join(rows) + "\n```\n")


class GardenFixture(unittest.TestCase):
    """정원 BC(애그리거트 plant · 도메인 서비스 · OHS 창구) — 선언 예보는 사본 실물을 바꾸지 않고 칸마다 빈 폴더를 지운다."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="pregate-garden-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.scratch = self.root / "scratch"
        self.scratch.mkdir()
        self.env = dict(os.environ, DJR_FINDINGS_JSON=str(self.root / "findings.jsonl"),
                        DJR_VIOLATIONS_DIR=str(self.root / "violations"), PYTHONDONTWRITEBYTECODE="1")
        for path, content in {
            f"{GARDEN}/__init__.py": "", f"{GARDEN}/domain_layer/__init__.py": "",
            f"{GARDEN}/domain_layer/plant/__init__.py": "",
            f"{GARDEN}/domain_layer/plant/plant.py": "class Plant:\n    pass\n",
            f"{GARDEN}/domain_layer/plant/plant_repository.py": "class PlantRepository:\n    pass\n",
            f"{GARDEN}/domain_layer/plant/exception/__init__.py": "",
            f"{GARDEN}/domain_layer/plant/exception/plant_unreadable.py": "class PlantUnreadable(Exception):\n    pass\n",
            f"{GARDEN}/domain_layer/domain_service/__init__.py": "",
            POLICY: POLICY_BASELINE,
            f"{CATALOG}/contract/exception/plant_unavailable_exception.py": "class PlantUnavailableException(Exception):\n    pass\n",
            CATALOG_SERVICE: CATALOG_BASELINE,
        }.items():
            self.write(path, content)

    def write(self, path: str, content: str) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def snapshot(self) -> dict[str, bytes]:
        return {p.relative_to(self.repo).as_posix(): p.read_bytes() for p in sorted(self.repo.rglob("*")) if p.is_file()}

    def assert_cells_removed(self) -> None:
        for folder in ("domain-service", "catch"):
            if (self.scratch / folder).exists():
                self.assertEqual(list((self.scratch / folder).iterdir()), [], f"칸 폴더가 남았다: {folder}")

    def checker_lines(self, checker: str, rule: str, path: str) -> list[str]:
        """실검사기를 사본째 돌려 그 파일 · 규칙의 줄(줄 번호 지움)을 센다 — 후상태 대조."""
        extra = ["--error-profile", "auto"] if checker == "check-api-error-controller-contract.py" else []  # registry 의 auto 호출
        result = subprocess.run([sys.executable, str(SCRIPTS / checker), str(self.repo), *extra], env=self.env,
                                capture_output=True, text=True)
        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
        return [re.sub(rf"{re.escape(path)}:\d+", f"{path}:N", line.strip()) for line in result.stdout.splitlines()
                if line.strip().startswith(f"[{rule}] {path}:")]


class DomainServiceForecastTest(GardenFixture):
    """F4-115 A1 — update 도메인 서비스 칸의 symbols 서명이 실검사기 #304 · #305 · #307 · #308 판정으로 선언 예보된다(물리 전사 없이)."""

    def forecast(self, rows: list[str], *, paths: "list[str] | None" = None, imports: list[str] = ()):
        plan, errors = pg.parse_spec(spec_text([f"update {p}" for p in (paths or [POLICY])], rows,
                                               [f"{(paths or [POLICY])[0]}  {i}" for i in imports]))
        self.assertEqual(errors, [], " | ".join(errors))
        baseline = pg.forecast_baseline(self.repo, plan)
        before = self.snapshot()
        found = pg.check_domain_service_forecast(plan, self.repo, self.scratch, baseline)
        self.assertEqual(self.snapshot(), before, "분석 투영 밖 실물이 바뀌었다")
        self.assert_cells_removed()
        return found

    def outcome(self, rows: list[str], **kwargs) -> list[tuple[str, str, bool]]:
        return sorted((f.rule, f.owner, f.confirmed) for f in self.forecast(rows, **kwargs))

    def test_new_public_bool_is_confirmed_with_checker_text(self) -> None:
        found = self.forecast([f"{POLICY}::WateringPolicy", DUE_ROW, f"{POLICY}::WateringPolicy.is_due(plant: Plant) -> bool"])
        self.assertEqual([(f.rule, f.path, f.owner, f.detail, f.confirmed) for f in found],
                         [("#308", POLICY, "WateringPolicy.is_due", bool_detail("is_due"), True)])
        # 같은 서명을 실물에 넣으면 실검사기가 같은 진단문을 낸다(판정 · 문면 복제 0).
        self.write(POLICY, POLICY_BASELINE + "\n    def is_due(self, plant: Plant) -> bool:\n        return True\n")
        self.assertIn(f"[#308] {POLICY}:N: {bool_detail('is_due')}", self.checker_lines("check-domain-model.py", "#308", POLICY))

    def test_unchanged_signatures_and_same_owner_debt_are_not_forecast(self) -> None:
        legacy = f"{POLICY}::WateringPolicy.is_legacy"
        for label, rows in [
            ("같은 서명 다시 적음", [f"{legacy}(plant: Plant) -> bool"]),
            ("문자열 주석", [f"{legacy}(plant: 'Plant') -> 'bool'"]),
            ("인자만 바뀐 기존 bool(같은 소유자 · 같은 판정문)", [f"{legacy}(plant: Plant, strict: bool) -> bool"]),
            ("기존 공개 메서드 서명 그대로", [DUE_ROW]),
        ]:
            with self.subTest(label=label):
                self.assertEqual(self.outcome([f"{POLICY}::WateringPolicy", *rows]), [])

    def test_existing_method_changed_to_bool_is_confirmed(self) -> None:
        self.assertEqual(self.outcome([f"{POLICY}::WateringPolicy",
                                       f"{POLICY}::WateringPolicy.due(plants: tuple[Plant, ...]) -> bool"]),
                         [("#308", "WateringPolicy.due", True)])

    def test_other_owner_of_the_same_verdict_splits_three_ways(self) -> None:
        # 기존 빚 열쇠 = G2 와 같은 «파일 · 규칙 · 판정문». 다른 소유자는 (가) 기존 줄이 이 명세로 사라짐 · (나) 함수 이름이
        # 다름(#304 · #305 의 같은 인자 이름) → 확정, (다) 같은 함수 이름의 다른 자리(옮김 · 개명 · 다시 적기) → 후보.
        due_repo = "    def due(self, plants: tuple[Plant, ...], repository: PlantRepository) -> tuple[Plant, ...]:\n        return plants\n"
        for label, baseline, rows, expected, why in [
            ("K1 클래스 이름만 바꿈", POLICY_BASELINE,
             [f"{POLICY}::WateringRule", f"{POLICY}::WateringRule.is_legacy(plant: Plant) -> bool"],
             [("#308", "WateringRule.is_legacy", False)], "`WateringPolicy.is_legacy`"),
            ("K3 모듈 함수 → 메서드", POLICY_HEAD + "\n\ndef is_legacy(plant: Plant) -> bool:\n    return False\n"
             "\n\nclass WateringPolicy:\n" + DUE,
             [f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_legacy(plant: Plant) -> bool"],
             [("#308", "WateringPolicy.is_legacy", False)], "`is_legacy`"),
            ("K4 조상 정의 다시 적음", POLICY_HEAD + "\n\nclass _Base:\n" + LEGACY + "\n\nclass WateringPolicy(_Base):\n" + DUE,
             [f"{POLICY}::WateringPolicy(_Base)", f"{POLICY}::WateringPolicy.is_legacy(plant: Plant) -> bool"],
             [("#308", "WateringPolicy.is_legacy", False)], "`_Base.is_legacy`"),
            ("중첩 함수의 같은 이름", POLICY_HEAD + "\n\nclass WateringPolicy:\n" + DUE.replace(
                "        return plants\n", "        def is_legacy(plant: Plant) -> bool:\n            return False\n"
                "        return plants\n"),
             [f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_legacy(plant: Plant) -> bool"],
             [("#308", "WateringPolicy.is_legacy", False)], "`WateringPolicy.due().is_legacy`"),
            ("두 소유자 가운데 하나만 고침", POLICY_BASELINE + "\n\nclass DrainPolicy:\n" + LEGACY,
             [f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_legacy(plant: Plant) -> int",
              f"{POLICY}::_Gauge", f"{POLICY}::_Gauge.is_legacy(plant: Plant) -> bool"],
             [("#308", "_Gauge.is_legacy", False)], "`DrainPolicy.is_legacy`, `WateringPolicy.is_legacy`"),
            ("K2 같은 인자 이름의 새 정의(나)", POLICY_HEAD + REPOSITORY_IMPORT + "\n\nclass WateringPolicy:\n" + due_repo,
             [f"{POLICY}::WateringPolicy",
              f"{POLICY}::WateringPolicy.drain(plants: tuple[Plant, ...], repository: PlantRepository) -> tuple[Plant, ...]"],
             [("#304", "WateringPolicy.drain", True)], "함수 이름이 다르다"),
            ("바꿔치기 — 기존 소유자를 고치고 다른 소유자에 같은 판정문(가)", POLICY_BASELINE,
             [f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_legacy(plant: Plant) -> int",
              f"{POLICY}::_Gauge {{level: int = 0}}", f"{POLICY}::_Gauge.is_legacy(plant: Plant) -> bool"],
             [("#308", "_Gauge.is_legacy", True)], "이 명세가 고쳐 사라진다"),
        ]:
            with self.subTest(label=label):
                self.write(POLICY, baseline)
                found = self.forecast(rows)
                self.assertEqual(sorted((f.rule, f.owner, f.confirmed) for f in found), expected)
                for item in found:
                    self.assertIn(why, item.detail)
                    self.assertEqual("예보 불확정" in item.detail, not item.confirmed, item.detail)
                    if not item.confirmed:
                        self.assertIn("G2 registry 는 같은 파일 · 같은 판정문을 기존으로 본다", item.detail)
                        self.assertIn("물음: 이 자리에서 새로 들이는 위반인가", item.detail)

    def test_other_owner_split_matches_the_real_checker_line_counts(self) -> None:
        # 후상태 대조 — (나) K2 · (가) 바꿔치기는 실검사기에 새 줄이 서고(G2 집합 차분은 지운다), (다) K1 은 줄 수가 그대로다.
        due_repo = ("    def due(self, plants: tuple[Plant, ...], repository: PlantRepository) -> tuple[Plant, ...]:\n"
                    "        return plants\n")
        base_k2 = POLICY_HEAD + REPOSITORY_IMPORT + "\n\nclass WateringPolicy:\n" + due_repo
        for label, baseline, implemented, rule, expected in [
            ("K2 — 1 → 2", base_k2, base_k2 + "\n" + due_repo.replace("def due", "def drain"), "#304", (1, 2)),
            ("바꿔치기 — 줄 하나가 다른 자리로(옛 줄은 사라짐)", POLICY_BASELINE,
             POLICY_BASELINE.replace(LEGACY, LEGACY.replace("-> bool", "-> int").replace("False", "0"))
             + "\n\nclass _Gauge:\n" + LEGACY, "#308", (1, 1)),
            ("K1 — 클래스 이름만 바꿈", POLICY_BASELINE, POLICY_BASELINE.replace("WateringPolicy", "WateringRule"),
             "#308", (1, 1)),
        ]:
            with self.subTest(label=label):
                self.write(POLICY, baseline)
                before = len(self.checker_lines("check-domain-model.py", rule, POLICY))
                self.write(POLICY, implemented)
                self.assertEqual((before, len(self.checker_lines("check-domain-model.py", rule, POLICY))), expected)

    def test_repository_port_and_primitive_arguments_are_confirmed(self) -> None:
        found = self.forecast([
            f"{POLICY}::WateringPolicy",
            f"{POLICY}::WateringPolicy.drain(plants: tuple[Plant, ...], store: PlantRepository) -> tuple[Plant, ...]",
            f"{POLICY}::WateringPolicy.ping(plants: tuple[Plant, ...], clock: ClockPort) -> tuple[Plant, ...]",
            f"{POLICY}::WateringPolicy.score(level: int, name: str) -> Plant"])
        self.assertEqual(sorted((f.rule, f.owner, f.confirmed) for f in found),
                         [("#304", "WateringPolicy.drain", True), ("#305", "WateringPolicy.ping", True),
                          ("#307", "WateringPolicy.score", True)])
        self.assertFalse([f.detail for f in found if "기존 줄" in f.detail or "예보 불확정" in f.detail])

    def test_private_names_are_skipped_and_private_class_public_methods_are_judged(self) -> None:
        self.assertEqual(self.outcome([f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy._is_dry(plant: Plant) -> bool",
                                       f"{POLICY}::_hidden(plant: Plant) -> bool"]), [])
        self.assertEqual(self.outcome([f"{POLICY}::_Gauge {{level: int = 0}}", f"{POLICY}::_Gauge.is_low(plant: Plant) -> bool"]),
                         [("#308", "_Gauge.is_low", True)])

    def test_module_function_rows_are_judged(self) -> None:
        self.write(POLICY, POLICY_HEAD + "\n\ndef watered(plant: Plant) -> Plant:\n    return plant\n")
        self.assertEqual(self.outcome([f"{POLICY}::is_ready(plant: Plant) -> bool", f"{POLICY}::watered(plant: Plant) -> Plant"]),
                         [("#308", "is_ready", True)])
        self.assertEqual(self.outcome([f"{POLICY}::watered(plant: Plant) -> bool"]), [("#308", "watered", True)])

    def test_unreadable_or_ambiguous_baseline_never_confirms_and_names_the_checker_rule(self) -> None:
        drain = f"{POLICY}::WateringPolicy.drain(plants: tuple[Plant, ...], store: PlantRepository) -> tuple[Plant, ...]"
        for label, baseline, rows, expected, why in [
            ("기준선 파싱 불능", "class WateringPolicy(:\n", [f"{POLICY}::WateringPolicy", drain],
             [("#304", "WateringPolicy.drain", False)], "기준선 실물을 읽거나 파싱하지 못했다"),
            ("기준선 파싱 불능 · 위반 없는 선언", "class WateringPolicy(:\n", [f"{POLICY}::WateringPolicy", DUE_ROW], [], ""),
            ("기준선 클래스 중복", POLICY_BASELINE + "\n\nclass WateringPolicy:\n    pass\n",
             [f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_legacy(plant: Plant) -> bool"],
             [("#308", "WateringPolicy.is_legacy", False)], "기준선 클래스 `WateringPolicy` 중복"),
            ("기준선 메서드 중복", POLICY_BASELINE + "\n" + LEGACY,
             [f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_legacy(plant: Plant) -> bool"],
             [("#308", "WateringPolicy.is_legacy", False)], "기준선 메서드 `WateringPolicy.is_legacy` 중복"),
            ("기준선 함수 중복", POLICY_HEAD + "\n\ndef ready(plant: Plant) -> Plant:\n    return plant\n"
             "\n\ndef ready(plant: Plant) -> Plant:\n    return plant\n",
             [f"{POLICY}::ready(plant: Plant) -> bool"], [("#308", "ready", False)], "기준선 함수 `ready` 중복"),
        ]:
            with self.subTest(label=label):
                self.write(POLICY, baseline)
                found = self.forecast(rows)
                self.assertEqual(sorted((f.rule, f.owner, f.confirmed) for f in found), expected)
                for item in found:
                    self.assertIn(f"예보 불확정: {why}", item.detail)

    def test_two_cells_of_one_bc_are_judged_in_their_own_folders(self) -> None:
        rule_a, rule_b = (f"{GARDEN}/domain_layer/domain_service/{n}.py" for n in ("rule_a", "rule_b"))
        for path, name in ((rule_a, "RuleA"), (rule_b, "RuleB")):
            self.write(path, POLICY_HEAD + f"\n\nclass {name}:\n    def keep(self, plant: Plant) -> Plant:\n        return plant\n")
        found = self.forecast([f"{rule_a}::RuleA", f"{rule_a}::RuleA.is_x(plant: Plant) -> bool",
                               f"{rule_b}::RuleB", f"{rule_b}::RuleB.calc(plant: Plant) -> Plant"], paths=[rule_a, rule_b])
        self.assertEqual([(f.rule, f.path, f.owner, f.confirmed) for f in found], [("#308", rule_a, "RuleA.is_x", True)])

    def test_promoted_body_and_plan_path_spelling_are_matched(self) -> None:
        body = f"{GARDEN}/domain_layer/domain_service/watering/watering.py"
        (self.repo / POLICY).unlink()
        self.write(f"{GARDEN}/domain_layer/domain_service/watering/__init__.py", "")
        self.write(body, POLICY_BASELINE)
        for spelled in (POLICY, f"./{POLICY}"):
            with self.subTest(path=spelled):
                found = self.forecast([f"{spelled}::WateringPolicy", f"{spelled}::WateringPolicy.is_due(plant: Plant) -> bool"],
                                      paths=[spelled])
                self.assertEqual([(f.rule, f.path, f.owner, f.confirmed) for f in found],
                                 [("#308", POLICY, "WateringPolicy.is_due", True)])
        # 기준선 실물(본체)의 기존 빚은 그대로 빠진다.
        self.assertEqual(self.outcome([f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_legacy(plant: Plant) -> bool"]),
                         [])

    def test_targets_follow_checker_selection_and_add_is_left_to_the_registry(self) -> None:
        for path in (f"{GARDEN}/domain_layer/plant/watering.py", f"{GARDEN}/domain_layer/domain_service/sub/watering.py",
                     f"{GARDEN}/domain_layer/domain_service/__init__.py"):
            with self.subTest(path=path):
                self.write(path, POLICY_HEAD)
                self.assertEqual(self.outcome([f"{path}::WateringPolicy", f"{path}::WateringPolicy.is_due(plant: Plant) -> bool"],
                                              paths=[path]), [])
        added = f"{GARDEN}/domain_layer/domain_service/feeding.py"
        plan, errors = pg.parse_spec(spec_text([f"add {added}"], [f"{added}::FeedingPolicy",
                                                                   f"{added}::FeedingPolicy.is_due(plant: Plant) -> bool"]))
        self.assertEqual(errors, [])
        self.assertEqual(pg.check_domain_service_forecast(plan, self.repo, self.scratch, pg.forecast_baseline(self.repo, plan)), [])

    def test_bundled_checker_is_loaded_only_for_target_cells_and_load_failure_is_run_error(self) -> None:
        rows = [f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_due(plant: Plant) -> bool"]
        with mock.patch.object(pg, "DOMAIN_MODEL_CHECKER", self.root / "missing-checker.py"), \
                mock.patch.dict(pg._BUNDLED_CHECKERS, clear=True):
            self.assertEqual(self.outcome([f"{CATALOG_SERVICE}::read_plant_query(name: str) -> str"],
                                          paths=[CATALOG_SERVICE]), [])
            with self.assertRaises(pg.RunError):
                self.forecast(rows)

    def test_forecast_leaves_no_records_or_violation_history(self) -> None:
        records = self.root / "records.jsonl"
        history = self.root / "history"
        base = {key: value for key, value in os.environ.items() if key not in ("DJR_FINDINGS_JSON", "DJR_VIOLATIONS_DIR")}
        rows = [f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_due(plant: Plant) -> bool",
                f"{POLICY}::WateringPolicy.is_legacy(plant: Plant, strict: bool) -> bool"]
        with mock.patch.dict(os.environ, dict(base, DJR_FINDINGS_JSON=str(records), DJR_VIOLATIONS_DIR=str(history)),
                             clear=True), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(self.outcome(rows), [("#308", "WateringPolicy.is_due", True)])
        self.assertEqual(out.getvalue(), "")
        self.assertFalse(records.exists())
        self.assertFalse(history.exists())

    def test_two_hundred_cells_are_all_forecast_without_leftovers(self) -> None:
        # 칸 수에 선형(칸마다 빈 폴더 둘) — 시간은 단언하지 않고 결과만 본다.
        paths = [f"{GARDEN}/domain_layer/domain_service/rule_{n:03d}.py" for n in range(200)]
        rows: list[str] = []
        for n, path in enumerate(paths):
            self.write(path, POLICY_HEAD + f"\n\nclass Rule{n:03d}:\n    def keep(self, plant: Plant) -> Plant:\n        return plant\n")
            rows += [f"{path}::Rule{n:03d}", f"{path}::Rule{n:03d}.is_x(plant: Plant) -> bool",
                     f"{path}::Rule{n:03d}.keep(plant: Plant) -> Plant"]
        found = self.forecast(rows, paths=paths)
        self.assertEqual(sorted((f.path, f.owner, f.confirmed) for f in found),
                         [(path, f"Rule{n:03d}.is_x", True) for n, path in enumerate(paths)])


class CatchForecastTest(GardenFixture):
    """F4-115 A2 — 예외 번역표 행의 선택 «번역 출처» 칸이 실검사기 트리 슬라이스 #474 · #62 판정으로 선언 예보된다."""

    def forecast(self, rows: list[str], *, paths: "list[str] | None" = None, symbols: list[str] = (),
                 imports: list[str] = ()):
        plan, errors = pg.parse_spec(catch_spec(paths or [f"update {CATALOG_SERVICE}"], rows, symbols, imports))
        self.assertEqual(errors, [], " | ".join(errors))
        baseline = pg.forecast_baseline(self.repo, plan)
        before = self.snapshot()
        found, memos = pg.check_catch_forecast(plan, self.repo, self.scratch, baseline)
        self.assertEqual(self.snapshot(), before, "분석 투영 밖 실물이 바뀌었다")
        self.assert_cells_removed()
        return found, memos

    def test_baseline_domain_origin_with_as_is_confirmed_like_the_real_checker(self) -> None:
        found, memos = self.forecast([f"PlantUnavailableException  {CATALOG_SERVICE}  <= PlantUnreadable as"])
        self.assertEqual([(f.rule, f.path, f.owner, f.confirmed) for f in found],
                         [("#474", CATALOG_SERVICE, "PlantUnavailableException ← PlantUnreadable", True)])
        self.assertTrue(found[0].detail.startswith(f"{CAUGHT_DETAIL} — 번역 출처 칸 `<= PlantUnreadable as`(출처 기준선 "
                                                   f"`{UNREADABLE_IMPORT}`)"), found[0].detail)
        self.assertEqual(memos, [])
        # 후상태 대조 — 잡은 값을 로그에 쓰는 구현은 실검사기가 #474 를 낸다(타입으로만 쓰면 0).
        self.assertEqual(self.checker_lines("check-api-error-controller-contract.py", "#474", CATALOG_SERVICE), [])
        self.write(CATALOG_SERVICE, CATALOG_LOGGED)
        self.assertEqual(len(self.checker_lines("check-api-error-controller-contract.py", "#474", CATALOG_SERVICE)), 1)

    def test_origin_is_resolved_by_the_first_source_found(self) -> None:
        withered = f"{GARDEN}/domain_layer/plant/exception/plant_withered.py"
        app_error = f"{GARDEN}/application_layer/plant_reading/plant_unreadable_error.py"
        app_import = "from application.garden.application_layer.plant_reading.plant_unreadable_error import PlantUnreadableError"
        for label, paths, row, symbols, imports, expected in [
            ("symbols 의 같은 이름 domain 클래스", [f"update {CATALOG_SERVICE}", f"add {withered}"], "<= PlantWithered as",
             [f"{withered}::PlantWithered(Exception)"], [], [("#474", True)]),
            ("boundary-imports 의 응용 예외", [f"update {CATALOG_SERVICE}"], "<= PlantUnreadableError as", [],
             [app_import], []),
            ("K10 — boundary-imports 응용 · symbols domain 같은 이름(처음 찾은 출처)",
             [f"update {CATALOG_SERVICE}", f"add {GARDEN}/domain_layer/plant/exception/plant_unreadable_error.py"],
             "<= PlantUnreadableError as", [f"{GARDEN}/domain_layer/plant/exception/plant_unreadable_error.py::"
                                            "PlantUnreadableError(Exception)"], [app_import], []),
            ("boundary-imports 의 domain 별칭", [f"update {CATALOG_SERVICE}"], "<= Unreadable as", [],
             [f"{UNREADABLE_IMPORT} as Unreadable"], [("#474", True)]),
            ("boundary-imports 소비 경로 표기 `./`", [f"update {CATALOG_SERVICE}"], "<= Unreadable as", [],
             [f"{UNREADABLE_IMPORT} as Unreadable"], [("#474", True)]),
            ("상대 import 는 domain 이 아니다", [f"update {CATALOG_SERVICE}"], "<= Local as", [],
             ["from .errors import Local"], []),
            ("출처를 가를 수 없음", [f"update {CATALOG_SERVICE}"], "<= PlantGone as", [], [], [("#474", False)]),
            ("symbols 에 같은 이름 클래스 둘", [f"update {CATALOG_SERVICE}", f"add {withered}", f"add {app_error}"],
             "<= PlantWithered as", [f"{withered}::PlantWithered(Exception)", f"{app_error}::PlantWithered(Exception)"], [],
             [("#474", False)]),
            ("내장 예외", [f"update {CATALOG_SERVICE}"], "<= ValueError as", [], [], []),
        ]:
            with self.subTest(label=label):
                consumer = f"./{CATALOG_SERVICE}" if "`./`" in label else CATALOG_SERVICE
                plan_imports = [f"{consumer}  {i}" for i in imports]
                found, memos = self.forecast([f"PlantUnavailableException  {CATALOG_SERVICE}  {row}"], paths=paths,
                                             symbols=symbols, imports=plan_imports)
                self.assertEqual(sorted((f.rule, f.confirmed) for f in found), expected)
                for item in found:
                    self.assertEqual("예보 불확정" in item.detail, not item.confirmed, item.detail)
                self.assertEqual(memos, [])

    def test_catch_all_source_is_62_regardless_of_as(self) -> None:
        for source in ("Exception", "Exception as", "BaseException", "BaseException as"):
            with self.subTest(source=source):
                found, memos = self.forecast([f"PlantUnavailableException  {CATALOG_SERVICE}  <= {source}"])
                self.assertEqual([(f.rule, f.confirmed) for f in found], [("#62", True)])
                self.assertIn("`except Exception`/bare", found[0].detail)
                self.assertEqual(memos, [])

    def test_rows_without_as_or_source_leave_row_memos(self) -> None:
        found, memos = self.forecast([f"PlantUnavailableException  {CATALOG_SERVICE}  <= PlantUnreadable",
                                      f"PlantGoneException  {CATALOG_SERVICE}  <= PlantGone",
                                      f"PlantDryException  {CATALOG_SERVICE}  <= ValueError",
                                      f"PlantLostException  {CATALOG_SERVICE}",
                                      f"PlantSoldException  {CATALOG_SERVICE}"])
        self.assertEqual(found, [])
        self.assertEqual([next(kind for kind, head in (("stale", STALE_MEMO), ("blank", BLANK_MEMO)) if m.startswith(head))
                          for m in memos], ["stale", "stale", "blank", "blank"])
        self.assertTrue(memos[0].startswith(STALE_MEMO) and memos[0].endswith(
            f"PlantUnavailableException ← PlantUnreadable · {CATALOG_SERVICE}"), memos[0])
        self.assertTrue(memos[2].startswith(BLANK_MEMO) and memos[2].endswith(f"PlantLostException · {CATALOG_SERVICE}"))
        # add 창구의 출처 칸 없는 행은 메모를 남기지 않는다(본문 전부가 스텁이다).
        added = f"{CATALOG}/sale_service.py"
        self.assertEqual(self.forecast([f"PlantSoldException  {added}"], paths=[f"add {added}"]), ([], []))

    def test_only_rows_of_checker_selected_ohs_files_are_judged(self) -> None:
        nested = f"{CATALOG}/a/b/x_service.py"
        helper = f"{CATALOG}/x_helper.py"
        value_object = f"{GARDEN}/domain_layer/plant/value_object/water_level.py"
        self.write(value_object, "class WaterLevel:\n    pass\n")
        for stub in (nested, helper):  # add 창구는 실체화(스텁) 뒤에 판정한다
            self.write(stub, "")
        found, memos = self.forecast([f"PlantUnavailableException  {nested}  <= Unreadable as",
                                      f"PlantUnavailableException  {helper}  <= Unreadable as",
                                      f"WaterLevelInvalid  {value_object}  <= PlantUnreadable as",
                                      f"WaterLevelGone  {value_object}"],
                                     paths=[f"add {nested}", f"add {helper}", f"update {value_object}"],
                                     imports=[f"{p}  {UNREADABLE_IMPORT} as Unreadable" for p in (nested, helper)])
        self.assertEqual([(f.rule, f.path, f.confirmed) for f in found], [("#474", nested, True)])
        self.assertEqual(memos, [f"{OUTSIDE_MEMO}: PlantUnavailableException ← Unreadable · {helper}",
                                 f"{OUTSIDE_MEMO}: WaterLevelInvalid ← PlantUnreadable · {value_object}"])

    def test_promoted_service_body_is_the_baseline(self) -> None:
        body = f"{CATALOG}/catalog_service/catalog_service.py"
        (self.repo / CATALOG_SERVICE).unlink()
        self.write(f"{CATALOG}/catalog_service/__init__.py", "")
        self.write(body, CATALOG_BASELINE)
        found, _ = self.forecast([f"PlantUnavailableException  {CATALOG_SERVICE}  <= PlantUnreadable as"])
        self.assertEqual([(f.rule, f.path, f.confirmed) for f in found], [("#474", CATALOG_SERVICE, True)])

    def test_grammar_and_unchanged_rows(self) -> None:
        for bad in ("<- PlantUnreadable", "<= PlantUnreadable as unreadable", "<= plant.PlantUnreadable", "<= PlantUnreadable AS",
                    "<=PlantUnreadable as", "<= (PlantUnreadable, PlantGone)", "<= PlantUnreadable  # 주석"):
            with self.subTest(row=bad):
                _, errors = pg.parse_spec(catch_spec([f"update {CATALOG_SERVICE}"], [f"PlantUnavailableException  {CATALOG_SERVICE}  {bad}"]))
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("[<탭|2+공백><= <잡는 예외 맨 이름>[ as]]", errors[0])
        for good, source, bound in (("<= PlantUnreadable", "PlantUnreadable", False), ("<=\tPlantUnreadable  as", "PlantUnreadable", True),
                                    ("", "", False)):
            with self.subTest(row=good):
                plan, errors = pg.parse_spec(catch_spec([f"update {CATALOG_SERVICE}"],
                                                        [f"PlantUnavailableException\t{CATALOG_SERVICE}\t{good}".rstrip()]))
                self.assertEqual(errors, [])
                self.assertEqual([(t.published, t.source, t.bound) for t in plan.entries[CATALOG_SERVICE].translations],
                                 [("PlantUnavailableException", source, bound)])
                self.assertEqual(plan.entries[CATALOG_SERVICE].raises, ["PlantUnavailableException"])

    def test_api_checker_is_loaded_only_for_sourced_rows_and_load_failure_is_run_error(self) -> None:
        # 검사기는 출처 칸이 있는 행이 있을 때만 적재한다 — 출처 칸 없는 행의 메모 (a) 는 앞 거름 꼴로만 낸다(2.26.1 과 같은 비용).
        value_object = f"{GARDEN}/domain_layer/plant/value_object/water_level.py"
        self.write(value_object, "class WaterLevel:\n    pass\n")
        with mock.patch.object(pg, "API_ERROR_CHECKER", self.root / "missing-checker.py"), \
                mock.patch.dict(pg._BUNDLED_CHECKERS, clear=True):
            found, memos = self.forecast([f"WaterLevelInvalid  {value_object}  <= PlantUnreadable as"],
                                         paths=[f"update {value_object}"])
            self.assertEqual((found, [m.split(":", 1)[0] for m in memos]), ([], [OUTSIDE_MEMO]))
            found, memos = self.forecast([f"PlantUnavailableException  {CATALOG_SERVICE}",
                                          f"PlantGoneException  {CATALOG_SERVICE}"])
            self.assertEqual(found, [])
            self.assertEqual([m.split("(", 1)[0] for m in memos], [BLANK_MEMO.split("(", 1)[0]] * 2)
            self.assertEqual(pg._BUNDLED_CHECKERS, {})
            for row in ("<= PlantUnreadable as", "<= PlantUnreadable"):
                with self.subTest(row=row), self.assertRaises(pg.RunError):
                    self.forecast([f"PlantUnavailableException  {CATALOG_SERVICE}  {row}"])
            self.assert_cells_removed()

    def test_existing_catch_debt_is_keyed_by_the_catch_that_raises_the_published_exception(self) -> None:
        # 구현 검토 I1 · I1′ — 기존 빚 열쇠: 기준선 창구에 그 규칙 줄을 낸 catch(빚 catch)가 있으면 행의 published 예외를 누가 내는지로
        # 그 행이 고칠 catch 를 가린다. #474 는 같은 출처를 잡는 catch 만 · #62 는 어느 catch-all 빚이든(이름 무관). ① 빚 catch 가 냄 →
        # 후보 ② 빚 없는 catch 가 냄 → 확정 ③ 둘 다 아님 → 후보. 여덟 꼴 · 열쇠 변이를 막는 여덟과 실검사기 줄 수(기준선 → 구현 뒤).
        peek = ("\n\ndef peek_plant_query(name: str) -> str:\n    try:\n        return _read(name)\n"
                "    except PlantUnreadable as {bound}:\n        print({bound})\n        return ''\n")
        clean_catch = "    except PlantUnreadable:\n"
        logged = "    except PlantUnreadable as unreadable:\n        print(unreadable)\n"
        debt_474 = CATALOG_BASELINE.replace(clean_catch, logged)
        other_same, other_named = (CATALOG_BASELINE + peek.format(bound=b) for b in ("unreadable", "error"))
        catch_all = CATALOG_BASELINE.replace(clean_catch, "    except BaseException:\n")
        other_62 = CATALOG_BASELINE + ("\n\ndef peek_plant_query(name: str) -> str:\n    try:\n        return _read(name)\n"
                                       "    except BaseException:\n        return ''\n")
        gone_exc = f"{CATALOG}/contract/exception/plant_gone_exception.py"
        row_474 = f"PlantUnavailableException  {CATALOG_SERVICE}  <= PlantUnreadable as"
        gone_import = UNREADABLE_IMPORT.replace("plant_unreadable import PlantUnreadable", "plant_gone import PlantGone")
        other_source = CATALOG_BASELINE.replace(f"{UNREADABLE_IMPORT}\n", f"{UNREADABLE_IMPORT}\n{gone_import}\n") + (
            "\n\ndef gone_plant_query(name: str) -> str:\n    try:\n        return _read(name)\n"
            "    except PlantGone as gone:\n        print(gone)\n        raise PlantUnavailableException() from None\n")
        bare = CATALOG_BASELINE.replace(clean_catch, "    except:\n")
        tupled = CATALOG_BASELINE.replace(clean_catch, "    except (PlantUnreadable, ValueError) as unreadable:\n        print(unreadable)\n")
        gone_exc_import = ("from application.garden.driving_layer.open_host_service.catalog.contract.exception.plant_gone_exception "
                           "import PlantGoneException")
        debt_to_gone = CATALOG_BASELINE.replace(f"{UNREADABLE_IMPORT}\n", f"{UNREADABLE_IMPORT}\n{gone_import}\n{gone_exc_import}\n").replace(
            "    except PlantUnreadable:\n        raise PlantUnavailableException() from None\n",
            "    except PlantUnreadable as unreadable:\n        print(unreadable)\n        raise PlantGoneException() from None\n") + (
            "\n\ndef gone_plant_query(name: str) -> str:\n    try:\n        return _read(name)\n"
            "    except PlantGone:\n        raise PlantUnavailableException() from None\n")
        both = debt_474 + ("\n\ndef peek_plant_query(name: str) -> str:\n    try:\n        return _read(name)\n"
                           "    except PlantUnreadable:\n        raise PlantUnavailableException() from None\n")
        bare_raise = debt_474.replace("raise PlantUnavailableException() from None", "raise PlantUnavailableException from None")
        dotted = debt_474.replace(f"{UNREADABLE_IMPORT}\n", f"{UNREADABLE_IMPORT}\n"
                                  "from application.garden.domain_layer.plant.exception import plant_unreadable as errors\n").replace(
            "    except PlantUnreadable as unreadable:\n", "    except errors.PlantUnreadable as unreadable:\n")
        again = ("        print(unreadable)\n", "        print(unreadable)\n        print('again')\n")
        for label, baseline, implemented, row, paths, symbols, confirmed, why, rule, lines in [
            ("C1b 빚 catch 의 본문만 바꿈 — ①", debt_474, debt_474.replace("        print(unreadable)\n",
                                                                       "        print(unreadable)\n        print('again')\n"),
             row_474, None, [], False, "#474 빚 catch(`read_plant_query` 의 `except PlantUnreadable as unreadable`)가 이 행의 "
             "published 예외 `PlantUnavailableException` 를 낸다", "#474", (1, 1)),
            ("C1 빚 catch 의 번역 대상만 바꿈 — ③", debt_474,
             debt_474.replace("raise PlantUnavailableException()", "raise PlantGoneException()"),
             f"PlantGoneException  {CATALOG_SERVICE}  <= PlantUnreadable as", [f"update {CATALOG_SERVICE}", f"add {gone_exc}"],
             [f"{gone_exc}::PlantGoneException(Exception)"], False, "published 예외 `PlantGoneException` 를 내는 같은 출처를 잡는 catch "
             "는 없다", "#474", (1, 1)),
            ("C2 기존 `except Exception` 의 본문만 바꿈 — ①", CATALOG_BASELINE.replace(clean_catch, "    except Exception:\n"),
             CATALOG_BASELINE.replace(clean_catch, "    except Exception:\n        print('fail')\n"),
             f"PlantUnavailableException  {CATALOG_SERVICE}  <= Exception", None, [], False,
             "#62 빚 catch(`read_plant_query` 의 `except Exception`)가 이 행의 published 예외", "#62", (1, 1)),
            ("C3 다른 함수의 같은 묶음 이름 빚 · 빚 없는 catch 가 값을 읽음 — ②", other_same,
             other_same.replace(clean_catch, logged, 1), row_474, None, [], True,
             "빚 없는 같은 출처를 잡는 catch(`read_plant_query` 의 `except PlantUnreadable`)가 낸다", "#474", (1, 2)),
            ("C4 다른 함수의 다른 묶음 이름 빚 — ②", other_named, other_named.replace(clean_catch, logged, 1), row_474, None, [],
             True, "묶음 이름이 `error` 와 다르면 G2 registry 가 새 줄로 막고", "#474", (1, 2)),
            ("C5 빚 없는 창구의 새 #474", CATALOG_BASELINE, CATALOG_LOGGED, row_474, None, [], True, "", "#474", (0, 1)),
            ("C6 다른 함수의 catch-all 빚 · 빚 없는 catch 를 `except Exception` 으로 — ②", other_62,
             other_62.replace(clean_catch, "    except Exception:\n", 1), f"PlantUnavailableException  {CATALOG_SERVICE}  <= Exception",
             None, [], True, "빚 없는 catch(`read_plant_query` 의 `except PlantUnreadable`)가 낸다", "#62", (1, 2)),
            ("C7 기존 `except BaseException` 을 `except Exception` 으로 좁힘 — ①(이름 무관)", catch_all,
             catch_all.replace("    except BaseException:\n", "    except Exception:\n"),
             f"PlantUnavailableException  {CATALOG_SERVICE}  <= Exception", None, [], False,
             "#62 빚 catch(`read_plant_query` 의 `except BaseException`)가 이 행의 published 예외", "#62", (1, 1)),
            # 열쇠를 넓히거나 규칙끼리 섞는 변이를 막는 꼴 — 다른 출처 catch 의 #474 빚 · #474 빚과 #62 행 · bare `except:` · 튜플 catch.
            ("N1 다른 예외를 잡는 catch 의 #474 빚은 같은 published 예외를 내도 낮추지 않음 — 빚 없음", other_source,
             other_source.replace(clean_catch, logged, 1), row_474, None, [], True, "", "#474", (1, 2)),
            ("N2 #474 빚은 #62 행을 낮추지 않음 — 빚 없음", debt_474, debt_474.replace(logged, "    except Exception:\n"),
             f"PlantUnavailableException  {CATALOG_SERVICE}  <= Exception", None, [], True, "", "#62", (0, 1)),
            ("N3 bare `except:` 빚 + `<= BaseException as` — ①", bare,
             bare.replace("    except:\n", "    except BaseException as error:\n        print(error)\n"),
             f"PlantUnavailableException  {CATALOG_SERVICE}  <= BaseException as", None, [], False,
             "#62 빚 catch(`read_plant_query` 의 `except`)가 이 행의 published 예외", "#62", (1, 1)),
            ("N4 튜플 catch 의 #474 빚 — ①", tupled,
             tupled.replace("        print(unreadable)\n", "        print(unreadable)\n        print('again')\n"), row_474, None, [],
             False, "#474 빚 catch(`read_plant_query` 의 `except (PlantUnreadable, ValueError) as unreadable`)가 이 행의 published 예외",
             "#474", (1, 1)),
            ("N5 다른 출처 catch 가 published 예외를 내도 #474 ② 로 보지 않음 — ③", debt_to_gone,
             debt_to_gone.replace("raise PlantGoneException() from None", "raise PlantUnavailableException() from None"), row_474, None,
             [], False, "published 예외 `PlantUnavailableException` 를 내는 같은 출처를 잡는 catch 는 없다", "#474", (1, 1)),
            ("N6 빚 catch 와 빚 없는 catch 가 같은 published 예외를 냄 — ①(② 보다 먼저)", both, both.replace(clean_catch, logged), row_474,
             None, [], False, "#474 빚 catch(`read_plant_query` 의 `except PlantUnreadable as unreadable`)가 이 행의 published 예외",
             "#474", (1, 2)),
            ("N7 빚 catch 가 published 예외를 부르지 않고 냄(`raise X from None`) — ①", bare_raise, bare_raise.replace(*again), row_474,
             None, [], False, "#474 빚 catch(`read_plant_query` 의 `except PlantUnreadable as unreadable`)가 이 행의 published 예외",
             "#474", (1, 1)),
            ("N8 점 이름 catch(`except errors.PlantUnreadable as`)의 #474 빚 — ①", dotted, dotted.replace(*again), row_474, None, [],
             False, "#474 빚 catch(`read_plant_query` 의 `except errors.PlantUnreadable as unreadable`)가 이 행의 published 예외",
             "#474", (1, 1)),
        ]:
            with self.subTest(label=label):
                self.write(f"{GARDEN}/domain_layer/plant/exception/plant_gone.py", "class PlantGone(Exception):\n    pass\n")
                self.write(gone_exc, "class PlantGoneException(Exception):\n    pass\n")
                self.write(CATALOG_SERVICE, baseline)
                found, _ = self.forecast([row], paths=paths, symbols=symbols)
                self.assertEqual([(f.rule, f.confirmed) for f in found], [(rule, confirmed)])
                self.assertIn(why, found[0].detail)
                if not why:
                    self.assertNotIn("빚 catch", found[0].detail)
                self.assertNotIn("G2 도 0", found[0].detail)
                self.assertNotIn("기존 줄로 본다", found[0].detail)
                if not confirmed:
                    self.assertIn("물음: 이 행이 고치는 catch 는 어느 것인가", found[0].detail)
                    self.assertIn("이 행이 그 catch 를 고치는 것이면 기존 빚이다 · 새 catch 이거나 다른 catch 면 실검사기 새 줄이다",
                                  found[0].detail)
                # 후상태 대조 — 명세대로 구현한 실검사기 줄 수(기준선 → 구현 뒤).
                before = len(self.checker_lines("check-api-error-controller-contract.py", rule, CATALOG_SERVICE))
                self.write(CATALOG_SERVICE, implemented)
                self.assertEqual((before, len(self.checker_lines("check-api-error-controller-contract.py", rule, CATALOG_SERVICE))),
                                 lines)
        # add 창구는 기준선이 없다 — 빚으로 낮추지 않는다.
        added = f"{CATALOG}/sale_service.py"
        self.write(added, debt_474)
        found, _ = self.forecast([f"PlantUnavailableException  {added}  <= PlantUnreadable as"], paths=[f"add {added}"],
                                 imports=[f"{added}  {UNREADABLE_IMPORT}"])
        self.assertEqual([(f.rule, f.confirmed) for f in found], [("#474", True)])
        # 기준선 판정의 사건 좌표를 catch 에 맞추지 못하면(좌표 수가 판정 수와 다름) 기존 빚인지 가를 수 없다 — 확정하지 않고 묻는다.
        ck = pg._bundled_checker(pg.API_ERROR_CHECKER, "_pregate_api_error_contract")
        real_slice = ck._slice_check_controller_ast

        def unmatched(*args: object) -> None:
            real_slice(*args)
            args[4].append(None)

        self.write(CATALOG_SERVICE, debt_474)
        with mock.patch.object(ck, "_slice_check_controller_ast", unmatched):
            found, _ = self.forecast([row_474])
        self.assertEqual([(f.rule, f.confirmed) for f in found], [("#474", False)])
        self.assertIn("기준선 창구의 #474 줄을 catch 에 맞추지 못했다(기존 빚인지 가를 수 없다)", found[0].detail)


class BundledCheckerLoadTest(unittest.TestCase):
    """번들 검사기 적재 세 곳(`_bundled_checker` · `_transaction_checker` · `_generated_admin_slots`)은 싣는 동안 `sys.modules` 에
    올린다 — dataclass 가 클래스를 만들 때 그 모듈을 찾는다(파이썬 3.12 ~ 3.14). 가짜 검사기가 «싣는 동안 sys.modules 에 없으면»
    스스로 실패하므로 판과 무관하게 가린다. 실패한 적재는 자기가 올린 모듈만 걷고 앞서 실린 같은 이름 모듈은 되돌린다."""

    NAMES: "tuple[str, ...]" = ("_pregate_load_probe", "_pregate_transaction_boundary", "_pregate_public_surface")

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="pregate-load-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        saved: "dict[str, object]" = {name: sys.modules.get(name) for name in self.NAMES}

        def restore() -> None:
            for name, module in saved.items():
                if module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module

        self.addCleanup(restore)

    def fake(self, name: str) -> Path:
        path = self.root / name
        path.write_text("import sys\nfrom dataclasses import dataclass\n\nif sys.modules.get(__name__) is None:\n"
                        "    raise ImportError('싣는 동안 sys.modules 에 없다')\n\n\n@dataclass\nclass Row:\n    rule: 'str'\n",
                        encoding="utf-8")
        return path

    def test_every_load_site_registers_the_checker_while_loading(self) -> None:
        with mock.patch.dict(pg._BUNDLED_CHECKERS, clear=True):
            module = pg._bundled_checker(self.fake("check-probe.py"), "_pregate_load_probe")
        self.assertIs(sys.modules.get("_pregate_load_probe"), module)
        self.assertEqual(module.Row("#1").rule, "#1")
        with mock.patch.object(pg, "TRANSACTION_CHECKER", self.fake("check-transaction-boundary.py")), \
                mock.patch.object(pg, "_TRANSACTION_CHECKER_MODULE", None):
            module = pg._transaction_checker()
            self.assertIs(sys.modules.get("_pregate_transaction_boundary"), module)
        self.fake("check-public-surface-annotation.py")
        with mock.patch.object(pg, "SCRIPTS_DIR", self.root):
            self.assertEqual(pg._generated_admin_slots(self.root, {}), set())
        self.assertEqual(sys.modules["_pregate_public_surface"].__file__, str(self.root / "check-public-surface-annotation.py"))

    def test_failed_load_removes_only_its_own_module(self) -> None:
        bad = self.root / "check-bad.py"
        bad.write_text("raise ValueError('깨진 검사기')\n", encoding="utf-8")
        with mock.patch.dict(pg._BUNDLED_CHECKERS, clear=True):
            sys.modules.pop("_pregate_load_probe", None)
            with self.assertRaises(pg.RunError):
                pg._bundled_checker(bad, "_pregate_load_probe")
            self.assertNotIn("_pregate_load_probe", sys.modules)
            good = pg._bundled_checker(self.fake("check-probe.py"), "_pregate_load_probe")
            pg._BUNDLED_CHECKERS.clear()
            with self.assertRaises(pg.RunError):
                pg._bundled_checker(bad, "_pregate_load_probe")
            self.assertIs(sys.modules.get("_pregate_load_probe"), good)


class ForecastScopeTest(GardenFixture):
    """F4-115 구현 검토 S3 — update 칸 미시뮬레이션 사유의 «… 만 예보» 꼬리는 실제 예보 대상 칸에만 붙는다(검사기 선택 안 ∧
    선언한 서명 · 번역 출처 칸이 있음)."""

    def test_scope_follows_selection_and_declarations(self) -> None:
        outside = "lib/garden/domain_layer/domain_service/watering.py"
        self.write(outside, POLICY_BASELINE)
        sale = f"{CATALOG}/sale_service.py"
        self.write(sale, CATALOG_BASELINE)
        rows = [f"{POLICY}::WateringPolicy", f"{POLICY}::WateringPolicy.is_due(plant: Plant) -> bool",
                f"{outside}::WateringPolicy", f"{outside}::WateringPolicy.is_due(plant: Plant) -> bool"]
        plan, errors = pg.parse_spec(catch_spec(
            [f"update {POLICY}", f"update {outside}", f"update {GARDEN}/domain_layer/domain_service/__init__.py",
             f"update {CATALOG_SERVICE}", f"update {sale}"], [f"PlantUnavailableException  {CATALOG_SERVICE}  <= PlantUnreadable",
                                                                f"PlantSoldException  {sale}"], rows))
        self.assertEqual(errors, [])
        self.assertEqual(pg.forecast_scope(plan, self.repo), {
            POLICY: "; 선언한 서명만 예보 · 본문 미검증", CATALOG_SERVICE: "; 번역 출처 칸만 예보 · catch 본문 미검증"})
        bare, _ = pg.parse_spec(catch_spec([f"update {POLICY}", f"update {sale}"], [f"PlantSoldException  {sale}"]))
        self.assertEqual(pg.forecast_scope(bare, self.repo), {})
        report = pg.materialize(self.repo, plan, declared_scope=pg.forecast_scope(plan, self.repo))
        notes = {line.rsplit(": ", 1)[1]: line for line in report["unsimulated"]}
        self.assertTrue(notes[POLICY].endswith(f"; 선언한 서명만 예보 · 본문 미검증): {POLICY}"), notes[POLICY])
        self.assertNotIn("예보", notes[outside])
        self.assertNotIn("예보", notes[sale])


def _equivalence_tree(root: Path, rnd: "random.Random") -> None:
    """선택 같음 대조용 가짜 사본 — 훑기 선택과 바로 맞추기가 갈릴 수 있는 꼴을 섞는다: `src/` · `build/` · `dist/` · `__pycache__/` ·
    `.hidden/` · `generated/` · `migrations/` 조상 · 점 이름 BC · BC 안의 `application` · 승격 본체와 부품 · 하위 폴더 · 대소문자
    `Application` · 조상 링크 폴더 · `application` 링크 · BC 링크 · 창구 아래 링크 폴더 · 저장소 칸 밖 이름."""
    def put(rel: str) -> None:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("class R:\n    def ok(self, x: int) -> bool:\n        return True\n", encoding="utf-8")

    for top in ("", "src/", "build/", "a/b/", ".hidden/", "__pycache__/", "dist/x/", "generated/", "x/migrations/"):
        for bc in ("garden", ".dot", "plant_bc"):
            if rnd.random() >= 0.6:
                continue
            base = f"{top}application/{bc}"
            put(f"{base}/domain_layer/domain_service/rule.py")
            put(f"{base}/domain_layer/domain_service/__init__.py")
            put(f"{base}/domain_layer/plant/plant_repository.py")
            put(f"{base}/domain_layer/plant/other_repository.py")
            put(f"{base}/driving_layer/open_host_service/catalog/catalog_service.py")
            put(f"{base}/driving_layer/open_host_service/catalog/catalog_helper.py")
            if rnd.random() < 0.5:
                put(f"{base}/domain_layer/domain_service/body/body.py")
                put(f"{base}/domain_layer/domain_service/body/part.py")
                put(f"{base}/driving_layer/open_host_service/sale/sale_service/sale_service.py")
            if rnd.random() < 0.3:
                put(f"{base}/domain_layer/domain_service/sub/deep.py")
                put(f"{base}/domain_layer/domain_service/x_repository.py")
                put(f"{base}/domain_layer/shared_value_object/y_repository.py")
                put(f"{base}/driving_layer/open_host_service/a/b/deep_service.py")
            if rnd.random() < 0.3:
                put(f"{base}/application/inner/domain_layer/domain_service/nested.py")
                put(f"{base}/application/inner/domain_layer/leaf/leaf_repository.py")
                put(f"{base}/application/inner/driving_layer/open_host_service/inner_service.py")
    if rnd.random() < 0.7:
        put("Application/garden/domain_layer/domain_service/caps.py")
        put("Application/garden/domain_layer/plant/plant_repository.py")
    if rnd.random() < 0.7 and (root / "src").is_dir():
        (root / "linked").symlink_to("src", target_is_directory=True)
    if rnd.random() < 0.5 and (root / "application").is_dir():
        (root / "alias_app").mkdir()
        (root / "alias_app" / "application").symlink_to("../application", target_is_directory=True)
    if rnd.random() < 0.5 and (root / "application" / "garden").is_dir():
        (root / "application" / "garden_link").symlink_to("garden", target_is_directory=True)
    ohs = root / "application" / "garden" / "driving_layer" / "open_host_service"
    if rnd.random() < 0.5 and ohs.is_dir() and (root / "src").is_dir():
        (ohs / "via_link").symlink_to(root / "src", target_is_directory=True)


class SelectionEquivalenceTest(unittest.TestCase):
    """F4-115 구현 검토 I2 · S2 — 선언 예보의 대상 선택(계획 경로로 BC 를 바로 맞춤)이 검사기 선택(사본 전체 훑기)과 같다:
    도메인 서비스(`check-domain-model.py`) · 저장소(`check-transaction-boundary.py` — F4-73) · OHS 창구(`check-api-error-controller-contract.py`
    트리 슬라이스). 시드 고정 무작위 트리에서 후보 꼴마다 다름 0 을 단언한다."""

    SEEDS: "range" = range(30)

    @classmethod
    def setUpClass(cls) -> None:
        cls.dm = pg._bundled_checker(pg.DOMAIN_MODEL_CHECKER, "_pregate_domain_model")
        cls.tx = pg._transaction_checker()
        cls.api = pg._bundled_checker(pg.API_ERROR_CHECKER, "_pregate_api_error_contract")

    def walked(self, root: Path) -> "dict[str, set[tuple[str, ...]]]":
        """검사기 선택 그대로(사본 전체 훑기)."""
        sel: "dict[str, set[tuple[str, ...]]]" = {"ds": set(), "repo": set(), "ohs": set()}
        for bc in self.dm.vocab.server_bc_dirs(root):
            ds = bc / "domain_layer" / "domain_service"
            if self.dm._has_adoption_signal(bc) and ds.is_dir():
                sel["ds"] |= {p.relative_to(root).parts for p in self.dm.checker_target.slot_glob(ds, "*.py")
                              if p.name != "__init__.py"}
        sink = self.tx.Findings(defer=True)
        for bc in self.tx._find_bcs(root):
            if self.tx._has_adoption_signal(bc):
                sel["repo"] |= {p.relative_to(root).parts for p in self.tx._check_repository_files(root, bc, sink)}
        for bc in self.api._tree_bcs2(root):
            ohs = bc / "driving_layer" / "open_host_service"
            if ohs.is_dir():
                sel["ohs"] |= {p.relative_to(root).parts for p in ohs.rglob("*_service.py")}
        return sel

    def test_direct_selection_equals_the_checker_walk(self) -> None:
        sink = self.tx.Findings(defer=True)
        counts = {"ds": 0, "repo": 0, "ohs": 0}
        with tempfile.TemporaryDirectory(prefix="pregate-equiv-") as tmp:
            for seed in self.SEEDS:
                root = Path(tmp) / f"t{seed}"
                root.mkdir()
                _equivalence_tree(root, random.Random(seed))
                walked = self.walked(root)
                for dirpath, _dirs, files in os.walk(root, followlinks=True):
                    for name in files:
                        parts = (Path(dirpath) / name).relative_to(root).parts
                        for kind, shaped, direct in (
                                ("ds", pg._domain_service_slot_shape(parts),
                                 lambda: pg._domain_service_selected(self.dm, root, parts)),
                                ("repo", name.endswith("_repository.py"),
                                 lambda: pg._repository_selected(self.tx, root, parts, sink)),
                                ("ohs", pg._ohs_catch_slot(parts), lambda: pg._ohs_selected(self.api, root, parts))):
                            if not shaped:
                                continue
                            counts[kind] += 1
                            with self.subTest(seed=seed, kind=kind, path="/".join(parts)):
                                self.assertEqual(direct(), parts in walked[kind])
        self.assertTrue(all(n > 200 for n in counts.values()), counts)

    def test_selection_does_not_walk_the_copy(self) -> None:
        # 대상 칸이 있어도 사본 전체 훑기(`server_bc_dirs` · `_find_bcs` · `_tree_bcs2`)를 부르지 않는다 — 저장소 예보의 표준 라이브러리
        # 가림 판단만 그것을 물을 때 한 번 훑는다(결과는 미리 잰 집합과 같다).
        with tempfile.TemporaryDirectory(prefix="pregate-nowalk-") as tmp:
            root = Path(tmp)
            _equivalence_tree(root, random.Random(7))
            walk = mock.Mock(side_effect=AssertionError("사본 전체 훑기"))
            with mock.patch.object(self.dm.vocab, "server_bc_dirs", walk), mock.patch.object(self.tx, "_find_bcs", walk), \
                    mock.patch.object(self.api, "_tree_bcs2", walk):
                self.assertTrue(pg._domain_service_selected(self.dm, root, ("application", "garden", "domain_layer",
                                                                            "domain_service", "rule.py"))
                                or not (root / "application/garden").is_dir())
                pg._repository_selected(self.tx, root, ("application", "garden", "domain_layer", "plant",
                                                        "plant_repository.py"), self.tx.Findings(defer=True))
                pg._ohs_selected(self.api, root, ("application", "garden", "driving_layer", "open_host_service", "catalog",
                                                  "catalog_service.py"))
            calls: list[int] = []
            real_find = self.tx._find_bcs
            with mock.patch.object(self.tx, "_find_bcs", side_effect=lambda r: calls.append(1) or real_find(r)):
                stdlib = pg._ShadowAwareStdlib(self.tx, root)
                self.assertEqual(calls, [])
                self.assertIn("uuid", stdlib)
                self.assertIn("json", stdlib)
                self.assertEqual(calls, [1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
