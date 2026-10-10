#!/usr/bin/env python3
"""pre-gate 전사 손실 회귀: 실제 파일 조치·검사기 판정·CLI skip 계약을 대조한다.

삭제 정리 제거, decorator 유실, TYPE_CHECKING 평탄화가 각각 이 검증을 red로 만든다.
반대 대조군은 전역 빈 폴더 정리와 무조건 dataclass/admin 면제를 잡는다.
"""
from __future__ import annotations

import ast
import contextlib
import errno
import io
import json
import os
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
# 기존 빚을 다시 적은 줄은 새 위반이 아니다(G2 registry 차분으로도 귀속 0) — 철자·감싸개만 바뀐 반환 · 같은 파일의 베이스
# 클래스에서 물려받은 메서드 · 클래스 본문 복합문 아래 메서드.
DEBT_BASELINE = (
    REPOSITORY_BASELINE.replace("from uuid import UUID\n", "from typing import TYPE_CHECKING, Optional\nfrom uuid import UUID\n")
    + "\n    @abstractmethod\n    def legacy_opt(self, account_id: int) -> Optional[UUID]: ...\n"
    "\n    @abstractmethod\n    def legacy_many(self, account_id: int) -> tuple[UUID, ...]: ...\n"
    "\n    @abstractmethod\n    def legacy_rows(self, account_id: int) -> dict[str, int]: ...\n"
    "\n    if TYPE_CHECKING:\n        def guarded(self, account_id: int) -> frozenset[UUID]: ...\n"
    "\n\nclass ArchivedFortuneRecordRepository(FortuneRecordRepository):\n    pass\n")
DEBT_RESTATED = (DEBT_BASELINE.replace("-> Optional[UUID]", "-> UUID | None").replace("-> tuple[UUID, ...]", "-> list[UUID]")
                 .replace("-> dict[str, int]", "-> dict[str, str]"))


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
        with mock.patch.object(pg.tempfile, "mkdtemp", return_value=str(scratch)), \
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
        bindings, aliases = ps._module_bindings(mod), ps._alias_defs(mod)
        ps._scan_stmts(mod.body, "module", set(), Path(PANEL), findings, False, bindings, aliases)
        ps._check_stub_generic_bases(mod, source, Path(PANEL), findings, candidates,
                                     ps._origin_bindings(mod), bindings, aliases)
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

    def test_restated_baseline_debt_is_not_forecast_again(self) -> None:
        self.write(REPOSITORY, DEBT_BASELINE)
        archived = "ArchivedFortuneRecordRepository(FortuneRecordRepository)"
        own = "FortuneRecordRepository(ABC)"
        for label, owner, methods, expected in [
            ("Optional → | None", own, ["legacy_opt(account_id: int) -> UUID | None"], []),
            ("tuple → list", own, ["legacy_many(account_id: int) -> list[UUID]"], []),
            ("dict 값 타입만", own, ["legacy_rows(account_id: int) -> dict[str, str]"], []),
            ("클래스 본문 if 아래 메서드", own, ["guarded(account_id: int) -> frozenset[UUID]"], []),
            ("물려받은 메서드", archived, ["legacy_ids(account_id: int) -> frozenset[UUID]",
                                    "delete_old(account_id: int) -> None"], []),
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

    def test_bundled_checker_load_failure_is_run_error(self) -> None:
        plan, _ = pg.parse_spec(spec_text([f"update {REPOSITORY}"], [
            f"{REPOSITORY}::FortuneRecordRepository(ABC)", f"{REPOSITORY}::FortuneRecordRepository.{FIELD_METHOD}"]))
        with mock.patch.object(pg, "TRANSACTION_CHECKER", self.root / "missing-checker.py"), \
                mock.patch.object(pg, "_TRANSACTION_CHECKER_MODULE", None):
            with self.assertRaises(pg.RunError):
                pg.check_repository_forecast(plan, self.repo, self.scratch, pg.repository_baseline(self.repo, plan))


if __name__ == "__main__":
    unittest.main(verbosity=2)
