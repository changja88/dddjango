#!/usr/bin/env python3
"""어댑터 고정 골격과 새 경로의 내용 검사를 실제 검사기로 검증한다."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT: Path = Path(__file__).resolve().parents[2]
SCRIPTS: Path = ROOT / "dddjango" / "scripts"
FIXTURES: Path = ROOT / "workspace" / "eval" / "fixtures"
ROLES: tuple[str, ...] = ("adapter", "command", "constant", "contract", "schema")
BUNDLES: tuple[str, ...] = (
    "anticorruption_layer/llm_access/intent_generation_adapter",
    "external_system/mailgun/notice_delivery_adapter",
    "ledger_load/django_adapter",
)


class AdapterLayoutTests(unittest.TestCase):
    def fixture(self, source: str = "skeleton/good_bc") -> Path:
        temporary: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        target: Path = Path(temporary.name) / "fixture"
        shutil.copytree(FIXTURES / source, target)
        return target

    def write(self, target: Path, relative: str, text: str = "") -> Path:
        path: Path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def bundle(self, target: Path, relative: str, bc: str = "orders") -> Path:
        base: Path = target / "application" / bc / "driven_layer" / "adapter"
        bundle: Path = base / relative
        bundle.mkdir(parents=True, exist_ok=True)
        for directory in (bundle, *bundle.parents):
            if directory == base:
                break
            (directory / "__init__.py").touch()
        for role in ROLES:
            (bundle / role).mkdir()
            (bundle / role / "__init__.py").touch()
        return bundle

    def check(self, target: Path, checker: str) -> tuple[int, list[dict], str]:
        output: Path = target.parent / "findings.jsonl"
        output.unlink(missing_ok=True)
        env: dict[str, str] = dict(os.environ)
        env.pop("DJR_FINDINGS_DIR", None)
        env["DJR_FINDINGS_JSON"] = str(output)
        run: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(SCRIPTS / checker), str(target)],
            cwd=ROOT, env=env, text=True, capture_output=True,
        )
        records: list[dict] = [
            json.loads(line) for line in output.read_text().splitlines()
        ] if output.exists() else []
        return run.returncode, records, run.stdout + run.stderr

    def assert_rule(self, result: tuple[int, list[dict], str], rule: str, path: str) -> None:
        self.assertEqual(result[0], 2, result[2])
        self.assertTrue(
            any(record.get("rule") == rule and str(record.get("file", "")).split(":", 1)[0].endswith(path)
                for record in result[1]),
            result[2],
        )

    def test_existing_empty_fixed_folders_are_required(self) -> None:
        target: Path = self.fixture()
        clean = self.check(target, "check-layer-skeleton.py")
        self.assertEqual(clean[0], 0, clean[2])
        for relative in (
            "application/orders/driving_layer/open_host_service/order_lookup/contract/request",
            "application/orders/domain_layer/order/entity",
        ):
            with self.subTest(relative=relative):
                folder: Path = target / relative
                shutil.rmtree(folder)
                self.assert_rule(self.check(target, "check-layer-skeleton.py"), "#488", relative)
                folder.mkdir()
                (folder / "__init__.py").touch()

    def test_all_adapter_families_allow_only_empty_role_packages(self) -> None:
        for relative in BUNDLES:
            with self.subTest(family=relative):
                target: Path = self.fixture()
                self.bundle(target, relative)
                result = self.check(target, "check-layer-skeleton.py")
                self.assertEqual(result[0], 0, result[2])

    def test_every_role_folder_and_initializer_is_required_without_content(self) -> None:
        for relative in BUNDLES:
            target: Path = self.fixture()
            bundle: Path = self.bundle(target, relative)
            for role in ROLES:
                with self.subTest(family=relative, role=role, missing="folder"):
                    folder: Path = bundle / role
                    shutil.rmtree(folder)
                    self.assert_rule(
                        self.check(target, "check-layer-skeleton.py"), "#488",
                        str(folder.relative_to(target)),
                    )
                    folder.mkdir()
                with self.subTest(family=relative, role=role, missing="initializer"):
                    self.assert_rule(
                        self.check(target, "check-layer-skeleton.py"), "#488",
                        str((folder / "__init__.py").relative_to(target)),
                    )
                    (folder / "__init__.py").touch()
            with self.subTest(family=relative, missing="bundle initializer"):
                (bundle / "__init__.py").unlink()
                self.assert_rule(
                    self.check(target, "check-layer-skeleton.py"), "#488",
                    str((bundle / "__init__.py").relative_to(target)),
                )

    def test_a_single_implementation_does_not_replace_the_fixed_folders(self) -> None:
        for relative in BUNDLES:
            with self.subTest(family=relative):
                target: Path = self.fixture()
                bundle: Path = self.bundle(target, relative)
                for role in ROLES:
                    shutil.rmtree(bundle / role)
                (bundle / (bundle.name + ".py")).write_text("class OnlyAdapter:\n    pass\n")
                result = self.check(target, "check-layer-skeleton.py")
                for role in ROLES:
                    self.assert_rule(result, "#488", str((bundle / role).relative_to(target)))

    def test_flat_files_and_unlisted_nested_folders_are_rejected(self) -> None:
        for relative in BUNDLES:
            with self.subTest(family=relative, form="flat"):
                target: Path = self.fixture()
                bundle: Path = self.bundle(target, relative)
                shutil.rmtree(bundle)
                flat: Path = bundle.with_suffix(".py")
                flat.write_text("class OnlyAdapter:\n    pass\n")
                self.assert_rule(self.check(target, "check-layer-skeleton.py"), "#490",
                                 str(flat.relative_to(target)))
            with self.subTest(family=relative, form="nested"):
                target = self.fixture()
                bundle = self.bundle(target, relative)
                extra: Path = bundle / "schema" / "extra"
                extra.mkdir()
                (extra / "__init__.py").touch()
                self.assert_rule(self.check(target, "check-layer-skeleton.py"), "#490",
                                 str(extra.relative_to(target)))

    def test_multiple_small_class_files_need_no_promotion_threshold(self) -> None:
        target: Path = self.fixture()
        bundle: Path = self.bundle(target, BUNDLES[0])
        for role in ("adapter", "command", "contract", "schema"):
            for name in ("first", "second"):
                stem: str = f"{name}_adapter" if role == "adapter" else name
                (bundle / role / f"{stem}.py").write_text(f"class {name.title()}:\n    pass\n")
        (bundle / "constant" / "prompt.py").write_text('FIRST: str = "first"\nSECOND: str = "second"\n')
        result = self.check(target, "check-layer-skeleton.py")
        self.assertEqual(result[0], 0, result[2])

    def test_implementation_file_must_keep_the_adapter_suffix(self) -> None:
        target: Path = self.fixture()
        bundle: Path = self.bundle(target, BUNDLES[0])
        bad: Path = bundle / "adapter" / "generation.py"
        bad.write_text("class LlmAccessGenerationAdapter:\n    pass\n")
        self.assert_rule(self.check(target, "check-layer-skeleton.py"), "#490",
                         str(bad.relative_to(target)))

    def test_initializers_cannot_hide_implementation_classes(self) -> None:
        target: Path = self.fixture()
        bundle: Path = self.bundle(target, BUNDLES[0])
        for directory in (bundle, *(bundle / role for role in ROLES)):
            with self.subTest(directory=directory.name):
                bad: Path = directory / "__init__.py"
                bad.write_text("class Hidden:\n    pass\n")
                self.assert_rule(self.check(target, "check-layer-skeleton.py"), "#640",
                                 str(bad.relative_to(target)))
                bad.write_text("")

    def test_constant_files_cannot_hide_schema_classes(self) -> None:
        target: Path = self.fixture("port_adapter_pairing/good")
        bundle: Path = self.bundle(target, BUNDLES[0])
        bad: Path = bundle / "constant" / "prompt.py"
        bad.write_text("class HiddenOutput:\n    pass\n")
        self.assert_rule(self.check(target, "check-port-adapter-pairing.py"), "#651",
                         str(bad.relative_to(target)))

    def test_technology_comes_from_the_bundle_for_multiple_implementations(self) -> None:
        target: Path = self.fixture("port_adapter_pairing/good")
        bundle: Path = self.bundle(target, BUNDLES[2])
        for name in ("single", "batch"):
            (bundle / "adapter" / f"{name}_adapter.py").write_text(
                "from application.orders.application_layer.port.ledger_load.ledger_load_port import LedgerLoadPort\n"
                "class DjangoLedgerLoadAdapter(LedgerLoadPort):\n    pass\n"
            )
        result = self.check(target, "check-port-adapter-pairing.py")
        self.assertEqual(result[0], 0, result[2])

    def test_each_class_file_counts_private_classes_too(self) -> None:
        for role in ("adapter", "command", "contract", "schema"):
            with self.subTest(role=role):
                target: Path = self.fixture("port_adapter_pairing/good")
                bundle: Path = self.bundle(target, BUNDLES[0])
                bad: Path = bundle / role / "two_classes.py"
                bad.write_text("class _First:\n    pass\n\nclass _Second:\n    pass\n")
                self.assert_rule(self.check(target, "check-port-adapter-pairing.py"), "#651",
                                 str(bad.relative_to(target)))

    def test_contract_builder_and_schema_alias_can_share_their_class_file(self) -> None:
        target: Path = self.fixture("port_adapter_pairing/good")
        self.write(target, "application/llm_access/application_layer/__init__.py")
        bundle: Path = self.bundle(target, BUNDLES[0])
        (bundle / "contract" / "message_contract.py").write_text(
            "from dataclasses import dataclass\n\n@dataclass(frozen=True)\n"
            "class MessageContract:\n    message: str\n\n"
            "def build_message_contract(message: str) -> MessageContract:\n"
            "    return MessageContract(message=message)\n"
        )
        (bundle / "schema" / "message_output.py").write_text(
            "from pydantic import BaseModel\n\ntype Result = str | None\n\n"
            "class MessageOutput(BaseModel):\n    result: Result\n"
        )
        (bundle / "command" / "generation_command.py").write_text(
            "from typing import Protocol\n\nclass GenerationCommand(Protocol):\n"
            "    def __call__(self, message: str) -> str: ...\n"
        )
        (bundle / "constant" / "prompt.py").write_text('PROMPT: str = "classify"\n')
        result = self.check(target, "check-port-adapter-pairing.py")
        self.assertEqual(result[0], 0, result[2])

    def test_nested_acl_implementation_keeps_naming_and_exception_checks(self) -> None:
        target: Path = self.fixture("context_isolation/good")
        bundle: Path = self.bundle(target, BUNDLES[0], "billing")
        implementation: Path = bundle / "adapter" / "intent_generation_adapter.py"
        implementation.write_text(
            "from application.llm_access.driving_layer.open_host_service.generation.generation_service "
            "import generate_structured_command\n\nclass WrongAdapter:\n"
            "    def generate(self):\n        return generate_structured_command()\n"
        )
        result = self.check(target, "check-context-isolation.py")
        self.assert_rule(result, "#363", str(implementation.relative_to(target)))
        self.assert_rule(result, "#473", str(implementation.relative_to(target)))

    def test_acl_contract_imports_need_no_exception_catch_but_keep_isolation(self) -> None:
        target: Path = self.fixture("context_isolation/good")
        bundle: Path = self.bundle(target, BUNDLES[0], "billing")
        contract: Path = bundle / "contract" / "generation_contract.py"
        contract.write_text(
            "from dataclasses import dataclass\n"
            "from application.llm_access.driving_layer.open_host_service.generation.contract.request."
            "generate_text_request import GenerationMessage\n\n@dataclass(frozen=True)\n"
            "class GenerationContract:\n    messages: tuple[GenerationMessage, ...]\n"
        )
        result = self.check(target, "check-context-isolation.py")
        self.assertEqual(result[0], 0, result[2])
        contract.write_text(
            "from application.orders.domain_layer.order.order import Order\n"
            "class GenerationContract:\n    order: Order\n"
        )
        result = self.check(target, "check-context-isolation.py")
        self.assertEqual(result[0], 2, result[2])
        self.assertTrue(any(str(r.get("file", "")).endswith(str(contract.relative_to(target)))
                            for r in result[1]), result[2])

    def test_external_implementation_is_found_and_socket_scope_is_preserved(self) -> None:
        target: Path = self.fixture("port_adapter_pairing/good")
        bundle: Path = self.bundle(target, BUNDLES[1])
        implementation: Path = bundle / "adapter" / "notice_delivery_adapter.py"
        implementation.write_text("import requests\n\nclass MailgunNoticeDeliveryAdapter:\n    pass\n")
        clean = self.check(target, "check-port-adapter-pairing.py")
        self.assertEqual(clean[0], 0, clean[2])
        implementation.write_text("import requests\n\nclass WrongAdapter:\n    pass\n")
        self.assert_rule(self.check(target, "check-port-adapter-pairing.py"), "#370",
                         str(implementation.relative_to(target)))

    def test_nested_django_implementation_keeps_orm_permission(self) -> None:
        for checker, source in (
            ("check-port-adapter-pairing.py", "port_adapter_pairing/good"),
            ("check-context-isolation.py", "context_isolation/good"),
        ):
            with self.subTest(checker=checker):
                target: Path = self.fixture(source)
                bundle: Path = self.bundle(target, BUNDLES[2], "billing")
                implementation: Path = bundle / "adapter" / "django_adapter.py"
                implementation.write_text(
                    "from application.billing.driven_layer.django_billing.models.entry_model import EntryModel\n"
                    "from application.billing.application_layer.port.ledger_load.ledger_load_port import LedgerLoadPort\n\n"
                    "class DjangoLedgerLoadAdapter(LedgerLoadPort):\n"
                    "    def load(self):\n        return EntryModel.objects.all()\n"
                )
                result = self.check(target, checker)
                self.assertEqual(result[0], 0, result[2])

    def test_fixed_adapter_bundle_names_are_allowed_without_a_root_body(self) -> None:
        target: Path = self.fixture("naming/good")
        for relative in BUNDLES:
            self.bundle(target, relative)
        result = self.check(target, "check-naming.py")
        self.assertEqual(result[0], 0, result[2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
