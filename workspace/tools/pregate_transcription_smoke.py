#!/usr/bin/env python3
"""pre-gate 전사 손실 회귀: 실제 파일 조치·검사기 판정·CLI skip 계약을 대조한다.

삭제 정리 제거, decorator 유실, TYPE_CHECKING 평탄화가 각각 이 검증을 red로 만든다.
반대 대조군은 전역 빈 폴더 정리와 무조건 dataclass/admin 면제를 잡는다.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pregate_fixture_run import _git, _load_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "dddjango/scripts"
pg = _load_module(SCRIPTS / "design_pregate.py", "transcription_pregate")
ci = _load_module(SCRIPTS / "check-context-isolation.py", "transcription_context")
ps = _load_module(SCRIPTS / "check-public-surface-annotation.py", "transcription_surface")
RESPONSE = "application/garden/driving_layer/open_host_service/catalog/contract/response/list_books_response.py"
PANEL = "application/garden/driven_layer/django_garden/admin/book/panel.py"


def spec_text(paths: list[str], symbols: list[str] = (), imports: list[str] = ()) -> str:
    return ("<!-- machine: file-plan -->\n```paths\n" + "\n".join(paths) + "\n```\n"
            "<!-- machine: symbols -->\n```symbols\n" + "\n".join(symbols) + "\n```\n"
            "<!-- machine: boundary-imports -->\n```imports\n" + "\n".join(imports) + "\n```\n")


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
