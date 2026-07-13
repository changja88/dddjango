#!/usr/bin/env python3
"""Q6 current-contract 평가용 결정적 runtime seed와 blind control 생성기."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


FORMAT = "dddjango-q6-v6"
PROJECT_RUNNER = "python3 -m unittest discover -s tests -p 'test_*.py' -v"
REPO_ROOT = Path(__file__).resolve().parents[3]
INVENTORY_COLUMNS = [
    "surface/version",
    "consumer/support",
    "persisted data/event",
    "deprecation window",
    "security/privacy/regulatory",
    "negative/absence",
    "evidence path",
    "status(retain/end/unknown)",
]
CASE_SUPPORT_END = "q6-01"
CASE_SUPPORTED_VERSIONS = "q6-02"
CASE_PERSISTED_READ = "q6-03"
CASE_PROPERTY_WITNESS = "q6-04"
CASE_CHARACTERIZATION = "q6-05"
CASE_EXTERNAL_MIGRATION = "q6-06"
CASE_EXPLICIT_ABSENCE = "q6-07"


COMMON_FILES = {
    "manage.py": "#!/usr/bin/env python3\n# Q6 seed marker; evaluator relays the project runner from its control plane.\n",
    "contract_app/__init__.py": "",
    "contract_app/apps.py": (
        "from django.apps import AppConfig\n\n"
        "class ContractAppConfig(AppConfig):\n"
        "    name = \"contract_app\"\n"
    ),
    "contract_app/models.py": "# Current Django model declarations belong here.\n",
    "config/__init__.py": "",
    "config/settings.py": (
        "SECRET_KEY = \"q6-fixture-only\"\n"
        "INSTALLED_APPS = [\"contract_app\"]\n"
    ),
    "tests/__init__.py": "",
    "tests/test_unrelated_health.py": (
        "import unittest\n\n"
        "class UnrelatedHealthTest(unittest.TestCase):\n"
        "    def test_unrelated_project_health(self):\n"
        "        self.assertEqual(\"STABLE\", \"stable\".upper())\n"
    ),
}


def row(
    obligation_id: str,
    surface: str,
    consumer: str,
    persisted: str,
    deprecation: str,
    security: str,
    absence: str,
    evidence: str,
    status: str,
) -> dict[str, str]:
    return {
        "obligation_id": obligation_id,
        "surface/version": surface,
        "consumer/support": consumer,
        "persisted data/event": persisted,
        "deprecation window": deprecation,
        "security/privacy/regulatory": security,
        "negative/absence": absence,
        "evidence path": evidence,
        "status(retain/end/unknown)": status,
    }


SCENARIOS: dict[str, dict[str, object]] = {
    CASE_SUPPORT_END: {
        "user_input": (
            "X의 지원 계약만 종료한다. wire/state에 X가 남아 있어도 허용하며, "
            "X의 부재를 새 계약으로 만들지 않는다."
        ),
        "g0_answers": {
            "mode": "modify",
            "lenses": ["ddd", "api"],
            "artifact": f"new:{CASE_SUPPORT_END}",
            "inventory_confirmation": "support consumer 0; absence obligation none",
        },
        "g1_answers": {
            "decision": "approve",
            "required_status": "end",
            "absence": "none",
        },
        "expected_adjustments": {
            "tests.test_public_x.PublicXTest.test_x_is_supported": "delete",
        },
        "forbidden_new_tests": ["X absence/nonexistence contract"],
        "evidence_rows": [
            row(
                "x-support",
                "payload.X/current",
                "no supported consumer",
                "none",
                "none",
                "none",
                "none; wire/state residue allowed",
                "evidence/support-policy.md",
                "end",
            )
        ],
        "files": {
            "contract_app/current_contract.py": (
                "def payload() -> dict[str, str]:\n"
                "    return {\"x\": \"legacy\", \"stable\": \"ok\"}\n"
            ),
            "tests/test_public_x.py": (
                "import unittest\n\n"
                "from contract_app.current_contract import payload\n\n"
                "class PublicXTest(unittest.TestCase):\n"
                "    def test_x_is_supported(self):\n"
                "        self.assertEqual(\"legacy\", payload()[\"x\"])\n"
            ),
            "evidence/support-policy.md": (
                "X has zero supported consumers. Its support ends now. "
                "No absence contract is created; residue is allowed.\n"
            ),
        },
    },
    CASE_SUPPORTED_VERSIONS: {
        "user_input": "v2의 display_name을 'CURRENT: Current Name'으로 변경하되 지원 중인 v1과 v1의 개인정보 마스킹 의무는 유지한다.",
        "g0_answers": {
            "mode": "modify",
            "lenses": ["ddd", "api"],
            "artifact": f"new:{CASE_SUPPORTED_VERSIONS}",
            "inventory_confirmation": "v1/v2 supported; v1/v2 privacy masking active",
        },
        "g1_answers": {
            "decision": "approve",
            "v1": "retain",
            "v2": "update display_name to CURRENT: Current Name",
        },
        "expected_adjustments": {
            "tests.test_versions.VersionContractTest.test_v1_contract_and_masking": "retain",
            "tests.test_versions.VersionContractTest.test_v2_contract": "update",
        },
        "evidence_rows": [
            row(
                "profile-v1",
                "profile/v1",
                "mobile-v1; supported",
                "none",
                "through 2027-01-01",
                "email must remain masked",
                "none",
                "evidence/v1-support-and-privacy.md",
                "retain",
            ),
            row(
                "profile-v2",
                "profile/v2",
                "web-v2; supported",
                "none",
                "none",
                "email masked",
                "none",
                "evidence/v2-change.md",
                "retain",
            ),
        ],
        "files": {
            "contract_app/current_contract.py": (
                "def v1(email: str) -> dict[str, str]:\n"
                "    return {\"display_name\": \"legacy name\", \"email\": \"***\"}\n\n"
                "def v2(email: str) -> dict[str, str]:\n"
                "    return {\"display_name\": \"Current Name\", \"email\": \"***\"}\n"
            ),
            "tests/test_versions.py": (
                "import unittest\n\n"
                "from contract_app.current_contract import v1, v2\n\n"
                "class VersionContractTest(unittest.TestCase):\n"
                "    def test_v1_contract_and_masking(self):\n"
                "        self.assertEqual({\"display_name\": \"legacy name\", \"email\": \"***\"}, v1(\"person@example.com\"))\n\n"
                "    def test_v2_contract(self):\n"
                "        self.assertEqual({\"display_name\": \"Current Name\", \"email\": \"***\"}, v2(\"person@example.com\"))\n"
            ),
            "evidence/v1-support-and-privacy.md": (
                "mobile-v1 is supported through 2027-01-01. Email masking is a current privacy obligation.\n"
            ),
            "evidence/v2-change.md": (
                "v2 email masking remains a current privacy obligation. "
                "Display-name formatting is the only approved change.\n"
            ),
        },
    },
    CASE_PERSISTED_READ: {
        "user_input": "앞으로 기록하는 이벤트를 {'schema_version': 2, 'display_name': <name>} 형식으로 바꾸되 저장된 {'name': <name>} v1 row와 이미 발행된 v1 이벤트는 계속 읽는다.",
        "g0_answers": {
            "mode": "modify",
            "lenses": ["ddd", "db"],
            "artifact": f"new:{CASE_PERSISTED_READ}",
            "inventory_confirmation": "v1 persisted/event reads remain current",
        },
        "g1_answers": {
            "decision": "approve",
            "v1_read": "retain {'name': <name>}",
            "v2_write": "add {'schema_version': 2, 'display_name': <name>}",
        },
        "expected_adjustments": {
            "tests.test_persisted_contract.PersistedContractTest.test_reads_v1_row_and_event": "retain",
        },
        "expected_new_test_obligations": [
            {
                "obligation_id": "persisted-v2-write",
                "action": "add",
                "required_behavior": (
                    "writes {'schema_version': 2, 'display_name': <name>} and is "
                    "collected, executed, and passing"
                ),
                "node_id": "runtime-selected; exact name is not graded",
            }
        ],
        "evidence_rows": [
            row(
                "persisted-v1-read",
                "record/event-v1 read",
                "current replay consumer",
                "stored rows and published events",
                "none",
                "none",
                "none",
                "evidence/persisted-read.md",
                "retain",
            ),
            row(
                "persisted-v2-write",
                "record/event-v2 write",
                "current writers/readers",
                "new rows and events",
                "none",
                "none",
                "none",
                "evidence/persisted-read.md",
                "retain",
            ),
        ],
        "files": {
            "contract_app/current_contract.py": (
                "def read_record(value: dict[str, str]) -> str:\n"
                "    return value.get(\"display_name\") or value[\"name\"]\n"
            ),
            "tests/test_persisted_contract.py": (
                "import unittest\n\n"
                "from contract_app.current_contract import read_record\n\n"
                "class PersistedContractTest(unittest.TestCase):\n"
                "    def test_reads_v1_row_and_event(self):\n"
                "        self.assertEqual(\"legacy\", read_record({\"name\": \"legacy\"}))\n"
            ),
            "evidence/persisted-read.md": (
                "Current replay and stored-row readers consume v1 indefinitely. "
                "New writes use schema_version 2 with display_name.\n"
            ),
        },
    },
    CASE_PROPERTY_WITNESS: {
        "user_input": "인접 계산 코드를 리팩터링하되 현재 불변식 ‘정규화 결과는 음수가 아니다’를 유지한다.",
        "g0_answers": {
            "mode": "modify",
            "lenses": ["ddd"],
            "artifact": f"new:{CASE_PROPERTY_WITNESS}",
            "inventory_confirmation": "non-negative invariant remains current",
        },
        "g1_answers": {"decision": "approve", "property": "retain"},
        "expected_adjustments": {
            "tests.test_property_witness.PropertyWitnessTest.test_counterexample_for_current_non_negative_property": "retain"
        },
        "evidence_rows": [
            row(
                "normalization-nonnegative",
                "normalization/current",
                "all current callers",
                "none",
                "none",
                "none",
                "none",
                "evidence/current-invariant.md",
                "retain",
            )
        ],
        "files": {
            "contract_app/current_contract.py": "def normalize(value: int) -> int:\n    return max(0, value)\n",
            "tests/test_property_witness.py": (
                "import unittest\n\n"
                "from contract_app.current_contract import normalize\n\n"
                "class PropertyWitnessTest(unittest.TestCase):\n"
                "    def test_counterexample_for_current_non_negative_property(self):\n"
                "        self.assertEqual(0, normalize(-7))\n"
            ),
            "evidence/current-invariant.md": "The non-negative result is a current invariant, not bug-history metadata.\n",
        },
    },
    CASE_CHARACTERIZATION: {
        "user_input": "현재 승인된 합계 동작을 보존하면서 legacy 계산 코드를 리팩터링한다.",
        "g0_answers": {
            "mode": "modify",
            "lenses": ["ddd"],
            "artifact": f"new:{CASE_CHARACTERIZATION}",
            "inventory_confirmation": "only documented total behavior is permanent",
        },
        "g1_answers": {"decision": "approve", "total_behavior": "retain"},
        "expected_adjustments": {
            "tests.test_current_total.CurrentTotalTest.test_current_total": "retain",
            "tests.test_legacy_characterization.LegacyCharacterizationTest.test_temporary_single_iteration_detail": "delete",
        },
        "evidence_rows": [
            row(
                "current-total",
                "total/current",
                "checkout; supported",
                "none",
                "none",
                "none",
                "none",
                "evidence/current-total.md",
                "retain",
            )
        ],
        "files": {
            "contract_app/current_contract.py": "def total(values: list[int]) -> int:\n    return sum(values)\n",
            "tests/test_current_total.py": (
                "import unittest\n\n"
                "from contract_app.current_contract import total\n\n"
                "class CurrentTotalTest(unittest.TestCase):\n"
                "    def test_current_total(self):\n"
                "        self.assertEqual(5, total([2, 3]))\n"
            ),
            "tests/test_legacy_characterization.py": (
                "import unittest\n\n"
                "from contract_app.current_contract import total\n\n"
                "class LegacyCharacterizationTest(unittest.TestCase):\n"
                "    # Temporary investigation witness: iteration count is not an approved contract.\n"
                "    def test_temporary_single_iteration_detail(self):\n"
                "        events = []\n\n"
                "        class RecordingValues:\n"
                "            def __iter__(self):\n"
                "                events.append(\"iterated\")\n"
                "                return iter([2, 3])\n\n"
                "        self.assertEqual(5, total(RecordingValues()))\n"
                "        self.assertEqual([\"iterated\"], events)\n"
            ),
            "evidence/current-total.md": "Only the observable sum is approved; incidental call order is not a contract.\n",
        },
    },
    CASE_EXTERNAL_MIGRATION: {
        "user_input": "display() 결과를 'CURRENT'로 바꾸고 ProfileRecord에 display_label = models.CharField(max_length=80, default='')를 추가한다. migration lifecycle은 외부 절차가 소유한다.",
        "g0_answers": {
            "mode": "modify",
            "lenses": ["ddd", "db"],
            "artifact": f"new:{CASE_EXTERNAL_MIGRATION}",
            "inventory_confirmation": "migration files/settings/tests are external-owned",
            "external_owned_opaque_paths": [
                "tests/test_schema_history.py",
                "contract_app/migrations/0001_initial.py",
            ],
        },
        "g1_answers": {
            "decision": "approve",
            "display_result": "CURRENT",
            "model_delta": "ProfileRecord.display_label CharField(max_length=80, default='')",
            "schema_impact": "yes",
        },
        "expected_adjustments": {
            "tests.test_current_display.CurrentDisplayTest.test_current_display": "update",
        },
        "expected_untouched_external_paths": [
            "tests/test_schema_history.py",
            "contract_app/migrations/0001_initial.py",
        ],
        "expected_application_changes": {
            "contract_app/current_contract.py": "display() returns CURRENT",
            "contract_app/models.py": (
                "ProfileRecord.display_label is CharField(max_length=80, default='')"
            ),
        },
        "runtime_environment": {"Q6_EXTERNAL_MIGRATION_FAILURE": "1"},
        "expected_completion": "blocked_external_dependency",
        "evidence_rows": [
            row(
                "current-display",
                "display/current",
                "web; supported",
                "none",
                "none",
                "none",
                "none",
                "evidence/application-change.md",
                "retain",
            ),
            row(
                "current-profile-record-declaration",
                "ProfileRecord/current model declaration",
                "application persistence adapter",
                "schema-affecting declaration",
                "none",
                "none",
                "none",
                "evidence/application-change.md",
                "retain",
            ),
        ],
        "files": {
            "contract_app/current_contract.py": "def display() -> str:\n    return \"current\"\n",
            "contract_app/models.py": (
                "from django.db import models\n\n"
                "class ProfileRecord(models.Model):\n"
                "    name = models.CharField(max_length=80)\n"
            ),
            "contract_app/migrations/__init__.py": "",
            "contract_app/migrations/0001_initial.py": "# External owner fixture. Do not edit.\noperations = []\n",
            "tests/test_current_display.py": (
                "import unittest\n\n"
                "from contract_app.current_contract import display\n\n"
                "class CurrentDisplayTest(unittest.TestCase):\n"
                "    def test_current_display(self):\n"
                "        self.assertEqual(\"current\", display())\n"
            ),
            "tests/test_schema_history.py": (
                "import os\n"
                "import unittest\n"
                "from pathlib import Path\n\n"
                "class ExternalMigrationAssetTest(unittest.TestCase):\n"
                "    def test_external_migration_asset_exists(self):\n"
                "        if os.environ.get(\"Q6_EXTERNAL_MIGRATION_FAILURE\") == \"1\":\n"
                "            self.fail(\"simulated external-owned migration lifecycle dependency\")\n"
                "        self.assertTrue(Path(\"contract_app/migrations/0001_initial.py\").is_file())\n"
            ),
            "evidence/application-change.md": (
                "The web consumer currently requires display() to return CURRENT. "
                "The application persistence adapter currently requires "
                "ProfileRecord.display_label as CharField(max_length=80, default=''). "
                "Schema impact is yes; migration verification remains external and unverified.\n"
            ),
        },
    },
    CASE_EXPLICIT_ABSENCE: {
        "user_input": (
            "공개 profile의 display_name을 'CURRENT: <name>'으로 바꾼다. "
            "현재 개인정보 계약인 internal_note 비노출은 유지하고, 보안상 debug_token도 "
            "응답에 절대 노출하지 않는 현행 금지 계약으로 추가한다."
        ),
        "g0_answers": {
            "mode": "modify",
            "lenses": ["ddd", "api"],
            "artifact": f"new:{CASE_EXPLICIT_ABSENCE}",
            "inventory_confirmation": (
                "internal_note absence remains current; debug_token absence is a new "
                "explicit current security obligation"
            ),
        },
        "g1_answers": {
            "decision": "approve",
            "display_name": "update to CURRENT: <name>",
            "internal_note_absence": "retain",
            "debug_token_absence": "add",
        },
        "expected_adjustments": {
            "tests.test_profile_absence.ProfileAbsenceTest.test_current_display_name": "update",
            "tests.test_profile_absence.ProfileAbsenceTest.test_internal_note_is_not_exposed": "retain",
        },
        "expected_new_test_obligations": [
            {
                "obligation_id": "profile-debug-token-absence",
                "action": "add",
                "required_behavior": (
                    "debug_token is observably absent from the public profile and the "
                    "test is collected, executed, and passing"
                ),
                "node_id": "runtime-selected; exact name is not graded",
            }
        ],
        "evidence_rows": [
            row(
                "profile-display-current",
                "profile/current",
                "web; supported",
                "none",
                "none",
                "none",
                "none",
                "evidence/profile-security.md",
                "retain",
            ),
            row(
                "profile-internal-note-absence",
                "profile/current",
                "web; supported",
                "none",
                "none",
                "internal_note is private",
                "internal_note must be absent from public response",
                "evidence/profile-security.md",
                "retain",
            ),
            row(
                "profile-debug-token-absence",
                "profile/current",
                "web; supported",
                "none",
                "none",
                "debug_token is security-sensitive",
                "debug_token must be absent from public response",
                "evidence/profile-security.md",
                "retain",
            ),
        ],
        "files": {
            "contract_app/current_contract.py": (
                "def public_profile(record: dict[str, str]) -> dict[str, str]:\n"
                "    return {\n"
                "        \"display_name\": record[\"display_name\"],\n"
                "        \"debug_token\": record.get(\"debug_token\", \"\"),\n"
                "    }\n"
            ),
            "tests/test_profile_absence.py": (
                "import unittest\n\n"
                "from contract_app.current_contract import public_profile\n\n"
                "class ProfileAbsenceTest(unittest.TestCase):\n"
                "    def test_current_display_name(self):\n"
                "        result = public_profile({\"display_name\": \"Current Name\"})\n"
                "        self.assertEqual(\"Current Name\", result[\"display_name\"])\n\n"
                "    def test_internal_note_is_not_exposed(self):\n"
                "        result = public_profile({\"display_name\": \"Current Name\", \"internal_note\": \"private\"})\n"
                "        self.assertNotIn(\"internal_note\", result)\n"
            ),
            "evidence/profile-security.md": (
                "internal_note non-disclosure remains a current privacy obligation. "
                "debug_token non-disclosure is an explicit new current security obligation. "
                "Both are observable absence contracts on the public profile response.\n"
            ),
        },
    },
}


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _manifest_version(path: Path) -> str:
    value = json.loads(path.read_text(encoding="utf-8"))
    version = value.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"manifest version is missing: {path}")
    return version


def _fixture_hashes(fixture: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(item for item in fixture.rglob("*") if item.is_file()):
        relative = path.relative_to(fixture).as_posix()
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def stage_runtime_fixture(
    bundle_root: Path,
    scenario: str,
    runtime_root: Path,
) -> dict[str, object]:
    """control bundle 밖에 runtime-visible fixture만 복사하고 CRIB를 반환한다."""
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario}")
    bundle = bundle_root.resolve()
    runtime = runtime_root.expanduser().resolve(strict=False)
    try:
        runtime.relative_to(bundle)
    except ValueError:
        pass
    else:
        raise ValueError("runtime workspace must be outside the fixture/control bundle")
    if runtime.exists() or runtime.is_symlink():
        raise ValueError(f"runtime workspace must not exist: {runtime}")
    source = bundle / "fixtures" / scenario
    if not source.is_dir():
        raise ValueError(f"fixture is missing: {source}")
    if any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError(f"fixture contains a symlink: {source}")
    manifest_path = (
        bundle / "evaluator-control" / scenario / "FIXTURE-MANIFEST.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_manifest = {
        "format": FORMAT,
        "scenario": scenario,
        "sha256": _fixture_hashes(source),
    }
    if manifest != expected_manifest:
        raise ValueError(f"fixture manifest mismatch: {source}")
    runtime.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, runtime)
    crib_path = bundle / "evaluator-control" / scenario / "CRIB.json"
    value = json.loads(crib_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"CRIB is not an object: {crib_path}")
    return value


def build_all(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    if any(output_root.iterdir()):
        raise ValueError(f"output directory must be empty: {output_root}")

    fixtures_root = output_root / "fixtures"
    control_root = output_root / "evaluator-control"
    fixtures_root.mkdir()
    control_root.mkdir()

    claude_version = _manifest_version(
        REPO_ROOT / "dddjango" / ".claude-plugin" / "plugin.json"
    )
    codex_version = _manifest_version(
        REPO_ROOT / "codex-dddjango" / ".codex-plugin" / "plugin.json"
    )
    if claude_version != codex_version:
        raise ValueError(
            "Claude/Codex manifest versions differ: "
            f"{claude_version!r} != {codex_version!r}"
        )

    _write(
        control_root / "EVALUATION-MANIFEST.json",
        _json(
            {
                "format": FORMAT,
                "plugin_version": claude_version,
                "scenario_order": sorted(SCENARIOS),
                "source_parity_required_before_live_run": True,
                "runtime_visible": [
                    "an isolated copy of fixtures/<scenario> staged outside this bundle",
                    "CRIB user_input_verbatim/gate answers/project_runner/runtime_environment relayed by the evaluator",
                ],
                "runtime_forbidden": [
                    "evaluator-control/<scenario>/ORACLE.json",
                    "evaluator-control/<scenario>/FIXTURE-MANIFEST.json",
                    "evaluator-control/EVALUATION-MANIFEST.json",
                    "q6_fixture_builder.py and Q6-CURRENT-CONTRACT.md",
                ],
                "live_run_status": "not executed by this builder",
            }
        ),
    )

    for slug, scenario in SCENARIOS.items():
        fixture = fixtures_root / slug
        control = control_root / slug
        files = dict(COMMON_FILES)
        files.update(scenario["files"])
        for relative, content in sorted(files.items()):
            _write(fixture / relative, content)

        crib = {
            "user_input_verbatim": scenario["user_input"],
            "g0_answers": scenario["g0_answers"],
            "g1_answers": scenario["g1_answers"],
            "g2_answers": {
                "decision": "approve only after all retain/update/add tests and the full suite pass",
                "on_incomplete": "request revision; never coerce Green",
            },
            "project_runner": PROJECT_RUNNER,
            "runtime_environment": scenario.get("runtime_environment", {}),
        }
        oracle = {
            "scenario": slug,
            "inventory_columns": INVENTORY_COLUMNS,
            "inventory_comparison": {
                "obligation_id": (
                    "evaluator-only stable key; runtime table does not need this column"
                ),
                "exact_fields": ["status(retain/end/unknown)"],
                "normalized_path_fields": ["evidence path"],
                "semantic_fields": [
                    column
                    for column in INVENTORY_COLUMNS
                    if column not in {"status(retain/end/unknown)", "evidence path"}
                ],
                "rule": (
                    "blind grader matches required current facts; wording and row order "
                    "are not graded"
                ),
            },
            "expected_inventory_obligations": scenario["evidence_rows"],
            "expected_adjustments": scenario["expected_adjustments"],
            "expected_new_test_obligations": scenario.get(
                "expected_new_test_obligations", []
            ),
            "forbidden_new_tests": scenario.get("forbidden_new_tests", []),
            "expected_untouched_external_paths": scenario.get(
                "expected_untouched_external_paths", []
            ),
            "expected_application_changes": scenario.get(
                "expected_application_changes", {}
            ),
            "expected_completion": scenario.get("expected_completion", "g2_pass"),
        }
        _write(control / "CRIB.json", _json(crib))
        _write(control / "ORACLE.json", _json(oracle))
        _write(
            control / "FIXTURE-MANIFEST.json",
            _json({"format": FORMAT, "scenario": slug, "sha256": _fixture_hashes(fixture)}),
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        build_all(args.output.resolve())
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
