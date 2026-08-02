#!/usr/bin/env python3
"""Executable RED matrix for the planned dddjango API-error checkers.

The matrix intentionally uses only source text and checker subprocesses.  It is
an executable specification for the future ``dddjango-code-json`` checker CLI;
it must not import Django or Ninja itself.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final


REPOSITORY_ROOT: Final = Path(__file__).resolve().parents[2]
CHECKER_DIR: Final = REPOSITORY_ROOT / "dddjango" / "scripts"
TARGET_DIR: Final = "TARGET_DIR"

# This is deliberately the full public vocabulary of the future Coordinator
# command.  Keeping it here makes a changed prompt/checker CLI observable in
# one executable place instead of leaving a prose-only contract behind.
ARGUMENT_ARITY: Final = {
    "--error-profile": 1,
    "--scope": 1,
    "--api-module": 1,
    "--controller-module": 1,
    "--urlconf-module": 1,
    "--registrar-module": 1,
    "--scope-bc": 1,
    "--error-bc": 1,
    "--project-code-error-module": 1,
    "--project-preserve-error-module": 1,
}
SOURCE_PATH_ARGUMENTS: Final = frozenset(
    {
        "--api-module",
        "--controller-module",
        "--urlconf-module",
        "--registrar-module",
        "--project-code-error-module",
        "--project-preserve-error-module",
    }
)
SINGULAR_ARGUMENTS: Final = frozenset(
    {"--error-profile", "--scope", "--api-module", "--urlconf-module"}
)
CHECKER_ALLOWED_ARGUMENTS: Final = {
    "check-error-centralization.py": frozenset(
        {
            "--error-profile",
            "--scope",
            "--api-module",
            "--controller-module",
            "--scope-bc",
            "--error-bc",
            "--project-code-error-module",
            "--project-preserve-error-module",
        }
    ),
    "check-api-error-controller-contract.py": frozenset(
        {"--error-profile", "--scope", "--api-module", "--controller-module", "--scope-bc", "--error-bc"}
    ),
    "check-context-isolation.py": frozenset(
        {"--error-profile", "--scope", "--api-module", "--controller-module", "--scope-bc", "--error-bc"}
    ),
    "check-openapi-error-declaration.py": frozenset(
        {"--error-profile", "--scope", "--api-module", "--controller-module", "--scope-bc", "--error-bc"}
    ),
    "check-composition-root.py": frozenset(
        {"--error-profile", "--scope", "--api-module", "--urlconf-module", "--registrar-module"}
    ),
    "check-response-schema-bypass.py": frozenset({"--controller-module"}),
}

COMMON_ERROR_OUT = """from ninja import Schema


class ErrorOut(Schema):
    code: str
    title: str
    status: int
    detail: str
"""

LESSON_ERROR_OUT = """from enum import StrEnum
from common.ninja.response.error_out import ErrorOut


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"
    CONFLICT = "lesson_conflict"


class LessonErrorOut(ErrorOut):
    code: LessonErrorCode


class LessonNotFoundError(LessonErrorOut):
    code: LessonErrorCode = LessonErrorCode.NOT_FOUND
    title: str = "Lesson not found"
    status: int = 404
    detail: str = "The lesson does not exist."


class LessonConflictError(LessonErrorOut):
    code: LessonErrorCode = LessonErrorCode.CONFLICT
    title: str = "Lesson conflict"
    status: int = 409
    detail: str = "The lesson cannot be changed."
"""

CATALOG_DUPLICATE_ERROR_OUT = """from enum import StrEnum
from common.ninja.response.error_out import ErrorOut


class CatalogErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class CatalogErrorOut(ErrorOut):
    code: CatalogErrorCode


class CatalogNotFoundError(CatalogErrorOut):
    code: CatalogErrorCode = CatalogErrorCode.NOT_FOUND
    title: str = "Catalog entry not found"
    status: int = 404
    detail: str = "The catalog entry does not exist."
"""

BASE_FILES: Final = {
    "common/ninja/response/__init__.py": "",
    "common/ninja/response/error_out.py": COMMON_ERROR_OUT,
    "application/lesson/presentation_layer/schema/error_out.py": LESSON_ERROR_OUT,
    "config/api.py": "from ninja_extra import NinjaExtraAPI\n\napi = NinjaExtraAPI()\n",
    "application/lesson/presentation_layer/controller.py": "def get_lesson(request): return {'id': 1}\n",
}

CONTROLLER_FILES: Final = {
    **BASE_FILES,
    "application/lesson/application_layer/use_cases.py": """class LessonMissing(Exception):
    pass


def get_lesson(lesson_id: int):
    return {"id": lesson_id}
""",
    "application/lesson/presentation_layer/controller.py": """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: LessonNotFoundError})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        error = LessonNotFoundError()
        return Status(error.status, error)
    return lesson
""",
}


@dataclass(frozen=True)
class Case:
    """One real subprocess assertion against a literal temporary source tree."""

    name: str
    files: dict[str, str]
    checker: str
    checker_args: tuple[str, ...]
    expected_exit: int
    expected_fragment: str
    note: str = ""
    baseline_files: dict[str, str] | None = None
    allowed_arg_issues: frozenset[str] = frozenset()


def schema_args(*extra: str) -> tuple[str, ...]:
    return (
        TARGET_DIR,
        "--error-profile",
        "dddjango-code-json",
        "--scope",
        "public-v1",
        "--api-module",
        "config/api.py",
        "--controller-module",
        "application/lesson/presentation_layer/controller.py",
        "--scope-bc",
        "lesson",
        "--error-bc",
        "lesson",
        "--project-code-error-module",
        "common/ninja/response/error_out.py",
        "--project-code-error-module",
        "application/lesson/presentation_layer/schema/error_out.py",
        *extra,
    )


def controller_args(*extra: str) -> tuple[str, ...]:
    return (
        TARGET_DIR,
        "--error-profile",
        "dddjango-code-json",
        "--scope",
        "public-v1",
        "--api-module",
        "config/api.py",
        "--controller-module",
        "application/lesson/presentation_layer/controller.py",
        "--scope-bc",
        "lesson",
        "--error-bc",
        "lesson",
        *extra,
    )


def with_files(*pairs: tuple[str, str], base: dict[str, str] = BASE_FILES) -> dict[str, str]:
    """Return an independent literal-source fixture with the requested changes."""
    files = dict(base)
    for path, source in pairs:
        if source == "<REMOVE>":
            files.pop(path, None)
        else:
            files[path] = source
    return files


def schema_cases() -> list[Case]:
    """Schema/Enum shape, inventory, and analysis cases for the future checker."""
    common_only = {
        "common/ninja/response/__init__.py": "",
        "common/ninja/response/error_out.py": COMMON_ERROR_OUT,
        "config/api.py": BASE_FILES["config/api.py"],
        "application/lesson/presentation_layer/controller.py": BASE_FILES["application/lesson/presentation_layer/controller.py"],
    }
    no_error_bc = dict(common_only)
    no_error_bc["application/catalog/presentation_layer/controller.py"] = "pass\n"
    preserve = {
        "legacy/errors.py": "class ErrorOut: pass\n",
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": "def legacy(request): return {'error': 'old'}\n",
        "common/ninja/response/__init__.py": "",
        "common/ninja/response/error_out.py": COMMON_ERROR_OUT,
    }
    reused_surfaces = with_files(
        ("config/api.py", "api = object()\n"),
        ("config/api_v2.py", "api = object()\n"),
        ("application/lesson/presentation_layer/controller.py", "def get_lesson(request): pass\n"),
        ("application/lesson/presentation_layer/controller_v2.py", "def get_lesson_v2(request): pass\n"),
    )
    duplicate_project_code = with_files(
        ("application/catalog/presentation_layer/schema/error_out.py", CATALOG_DUPLICATE_ERROR_OUT),
    )
    missing_enum = (
        LESSON_ERROR_OUT.replace(
            'class LessonErrorCode(StrEnum):\n    NOT_FOUND = "lesson_not_found"\n    CONFLICT = "lesson_conflict"\n\n\n',
            "",
        )
        .replace("code: LessonErrorCode = LessonErrorCode.NOT_FOUND", 'code: str = "lesson_not_found"')
        .replace("code: LessonErrorCode = LessonErrorCode.CONFLICT", 'code: str = "lesson_conflict"')
        .replace("code: LessonErrorCode", "code: str")
    )
    missing_base = (
        LESSON_ERROR_OUT.replace("class LessonErrorOut(ErrorOut):\n    code: LessonErrorCode\n\n\n", "")
        .replace("class LessonNotFoundError(LessonErrorOut):", "class LessonNotFoundError(ErrorOut):")
        .replace("class LessonConflictError(LessonErrorOut):", "class LessonConflictError(ErrorOut):")
    )
    return [
        Case("schema-clean-common-base-and-two-concrete", BASE_FILES, "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-empty-error-bc", common_only, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--project-code-error-module", "common/ninja/response/error_out.py"), 0, ""),
        Case("schema-clean-no-error-bc-in-scope", no_error_bc, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/catalog/presentation_layer/controller.py", "--scope-bc", "catalog", "--project-code-error-module", "common/ninja/response/error_out.py"), 0, ""),
        Case("schema-clean-same-profile-common-enum-reuse-v1", reused_surfaces, "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-same-profile-common-enum-reuse-v2", reused_surfaces, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v2", "--api-module", "config/api_v2.py", "--controller-module", "application/lesson/presentation_layer/controller_v2.py", "--scope-bc", "lesson", "--error-bc", "lesson", "--project-code-error-module", "common/ninja/response/error_out.py", "--project-code-error-module", "application/lesson/presentation_layer/schema/error_out.py"), 0, ""),
        Case("schema-clean-canonical-looking-preserve-excluded", preserve, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "preserve-established", "--scope", "legacy", "--api-module", "legacy/api.py", "--controller-module", "legacy/controller.py", "--scope-bc", "legacy", "--error-bc", "legacy", "--project-code-error-module", "common/ninja/response/error_out.py", "--project-preserve-error-module", "legacy/errors.py"), 0, ""),
        Case("schema-missing-designated-error-bc-artifact", with_files(("application/lesson/presentation_layer/schema/error_out.py", "<REMOVE>")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-init-missing", with_files(("common/ninja/response/__init__.py", "<REMOVE>")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-error-out-missing", with_files(("common/ninja/response/error_out.py", "<REMOVE>")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-extra-common-response-file", with_files(("common/ninja/response/helper.py", "def make_error(): pass\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-concrete-error", with_files(("common/ninja/response/error_out.py", COMMON_ERROR_OUT + "\nclass GlobalNotFound(ErrorOut):\n    pass\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-outside-canonical-module", with_files(("application/lesson/presentation_layer/schema/not_found.py", "from .error_out import LessonErrorOut\nclass Other(LessonErrorOut): pass\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-missing-enum", with_files(("application/lesson/presentation_layer/schema/error_out.py", missing_enum)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-duplicate-enum", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT + "\nclass OtherErrorCode(StrEnum):\n    BAD = 'bad'\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-missing-base", with_files(("application/lesson/presentation_layer/schema/error_out.py", missing_base)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-duplicate-base", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT + "\nclass AnotherErrorOut(ErrorOut):\n    code: LessonErrorCode\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-extra-defaulted-field", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("    code: LessonErrorCode\n", "    code: LessonErrorCode\n    retryable: bool = False\n", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-wrong-inheritance", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("class LessonErrorOut(ErrorOut):", "class LessonErrorOut:"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-extra-field", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("    detail: str = \"The lesson does not exist.\"", "    detail: str = \"The lesson does not exist.\"\n    retry_after: int = 1"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-validator", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom pydantic import field_validator").replace("    detail: str = \"The lesson does not exist.\"", "    detail: str = \"The lesson does not exist.\"\n\n    @field_validator('status')\n    @classmethod\n    def validate_status(cls, value: int) -> int:\n        return value"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-field-alias", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom pydantic import Field").replace("title: str = \"Lesson not found\"", "title: str = Field(alias='message', default='Lesson not found')"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-missing-default", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("    detail: str = \"The lesson does not exist.\"", "    detail: str"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-raw-string-code", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("code: LessonErrorCode = LessonErrorCode.NOT_FOUND", "code: str = 'lesson_not_found'"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-project-duplicate-wire-code-across-bcs", duplicate_project_code, "check-error-centralization.py", schema_args("--scope-bc", "catalog", "--error-bc", "catalog", "--project-code-error-module", "application/catalog/presentation_layer/schema/error_out.py"), 2, "BLOCKER"),
        Case("schema-literal-code", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom typing import Literal").replace("code: LessonErrorCode", "code: Literal['lesson_not_found']", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-str-code", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("code: LessonErrorCode", "code: str", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-syntax", with_files(("application/lesson/presentation_layer/schema/error_out.py", "class Broken(:\n")), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-analysis-root-escape", BASE_FILES, "check-error-centralization.py", schema_args("--project-code-error-module", "../outside.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--project-code-error-module"})),
        Case("schema-analysis-unresolved-base", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("from common.ninja.response.error_out import ErrorOut", "from missing import ErrorOut"))), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-analysis-missing-source", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--project-code-error-module", "application/lesson/presentation_layer/schema/error_out.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--scope", "missing:--api-module", "missing:--controller-module", "missing:--scope-bc"})),
        Case("schema-analysis-missing-inventory", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--project-code-error-module"})),
        Case("schema-analysis-missing-selected-error-module-path", BASE_FILES, "check-error-centralization.py", schema_args("--project-code-error-module", "application/lesson/presentation_layer/schema/missing_error_out.py"), 1, "사용 오류"),
        Case("schema-analysis-error-bc-not-subset", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "catalog", "--error-bc", "lesson", "--project-code-error-module", "common/ninja/response/error_out.py", "--project-code-error-module", "application/lesson/presentation_layer/schema/error_out.py"), 1, "사용 오류"),
        Case("schema-analysis-candidate-absent-from-inventory", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson", "--project-code-error-module", "common/ninja/response/error_out.py"), 1, "사용 오류"),
        Case("schema-analysis-module-in-both-inventories", BASE_FILES, "check-error-centralization.py", schema_args("--project-preserve-error-module", "application/lesson/presentation_layer/schema/error_out.py"), 1, "사용 오류"),
        Case("schema-analysis-auto-profile", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "auto", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson", "--project-code-error-module", "common/ninja/response/error_out.py", "--project-code-error-module", "application/lesson/presentation_layer/schema/error_out.py"), 0, ""),
        Case("schema-analysis-missing-profile-args", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--error-profile", "missing:--api-module", "missing:--controller-module", "missing:--scope-bc", "missing:--project-code-error-module"})),
        Case("schema-fp-tests-migrations-docstrings-logs", with_files(("application/lesson/tests/test_codes.py", "code = 'lesson_not_found'\n"), ("application/lesson/migrations/0001_initial.py", "code = 'lesson_not_found'\n"), ("application/lesson/presentation_layer/log.py", "import logging\nlogger = logging.getLogger(__name__)\n'''code = lesson_not_found'''\nlogger.info('code=%s', 'lesson_not_found')\n")), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-fp-classvar-private-benign-config-import-alias", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom typing import ClassVar").replace("class LessonErrorOut(ErrorOut):\n    code: LessonErrorCode", "class LessonErrorOut(ErrorOut):\n    model_config = {'populate_by_name': True}\n    _cache: ClassVar[dict] = {}\n    code: LessonErrorCode"))), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-fp-relative-import-local-assignment-ignored-cache", with_files(("application/lesson/presentation_layer/schema/alias.py", "from .error_out import LessonErrorOut as Error\nvalue = Error\n"), (".cache/generated.py", "code = 'ignored'\n"), ("__pycache__/bad.py", "code = 'ignored'\n")), "check-error-centralization.py", schema_args(), 0, ""),
        # Reviewer gap: whether the inventory is semantically complete and whether a
        # public code should exist cannot be inferred from source shape alone.
    ]


def controller_cases() -> list[Case]:
    """Controller shape cases; the checker is intentionally absent at this RED stage."""
    clean_async = CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("def get_lesson_controller", "async def get_lesson_controller").replace("lesson = get_lesson(lesson_id)", "lesson = await get_lesson(lesson_id)")
    clean_tuple = CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("except LessonMissing:", "except (LessonMissing, LookupError):")
    direct_base = (
        CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"]
        .replace("LessonNotFoundError()", "LessonErrorOut(code=LessonErrorCode.NOT_FOUND, title='missing', status=404, detail='missing')")
        .replace("404: LessonNotFoundError", "404: LessonErrorOut")
        .replace("from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError", "from application.lesson.presentation_layer.schema.error_out import LessonErrorCode, LessonErrorOut")
    )
    return [
        Case("controller-clean-sync-narrow-try", CONTROLLER_FILES, "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-async-narrow-try", with_files(("application/lesson/presentation_layer/controller.py", clean_async), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-tuple-catch-prepared-concrete", with_files(("application/lesson/presentation_layer/controller.py", clean_tuple), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-event-specific-base", with_files(("application/lesson/presentation_layer/controller.py", direct_base), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-result-none-direct-return", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return lesson", "result = lesson\n    if result is None:\n        return None\n    return result")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-approved-retry-after", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from django.http import HttpResponse\nfrom ninja import Router, Status").replace("def get_lesson_controller(request, lesson_id: int):", "def get_lesson_controller(request, response: HttpResponse, lesson_id: int):").replace("        return Status(error.status, error)", "        response['Retry-After'] = '1'\n        return Status(error.status, error)")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-unselected-preserve-handler", with_files(("application/lesson/presentation_layer/preserve_controller.py", "def preserve_controller(request): return {'legacy': True}\n"), ("application/lesson/presentation_layer/preserve_handler.py", "def preserve_handler(request, exc): return {'legacy': True}\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-direct-presentation-helper", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .factory import make_error").replace("error = LessonNotFoundError()", "error = make_error()")), ("application/lesson/presentation_layer/factory.py", "from .schema.error_out import LessonNotFoundError\ndef make_error(): return LessonNotFoundError()\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-direct-one-hop-serializer-helper", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .serializer import serialize_error").replace("error = LessonNotFoundError()", "error = serialize_error()")), ("application/lesson/presentation_layer/serializer.py", "from .schema.error_out import LessonNotFoundError\ndef serialize_error(): return LessonNotFoundError()\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-direct-one-hop-mapping-helper", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .mapping import map_error").replace("error = LessonNotFoundError()", "error = map_error()")), ("application/lesson/presentation_layer/mapping.py", "from .schema.error_out import LessonNotFoundError\ndef map_error(): return LessonNotFoundError()\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-registered-handler", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"] + "\n@router.exception_handler(LessonMissing)\ndef handler(request, exc): pass\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-wide-try", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("try:\n        lesson =", "try:\n        prepared = lesson_id\n        lesson =")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-success-transform-inside-try", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("lesson = get_lesson(lesson_id)", "lesson = get_lesson(lesson_id)\n        return {'lesson': lesson}")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-broad-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("except LessonMissing:", "except Exception:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-framework-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom ninja.errors import HttpError").replace("except LessonMissing:", "except HttpError:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-raw-infra-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("except LessonMissing:", "except OSError:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-immediate-raise-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("    try:\n        lesson = get_lesson(lesson_id)", "    lesson = None\n    try:\n        raise LessonMissing()")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-reraises", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("error = LessonNotFoundError()\n        return Status(error.status, error)", "raise")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-raises-http-error", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom ninja.errors import HttpError").replace("error = LessonNotFoundError()\n        return Status(error.status, error)", "raise HttpError(404, 'missing')")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-forwards-exception", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .forwarder import forward_error").replace("return Status(error.status, error)", "return forward_error(error)")), ("application/lesson/presentation_layer/forwarder.py", "def forward_error(error): return error\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-no-direct-status", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return Status(error.status, error)", "return error")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-concrete-called-with-args", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("LessonNotFoundError()", "LessonNotFoundError(detail='missing')")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-error-tuple-raw-response-dict", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return Status(error.status, error)", "return 404, {'code': 'lesson_not_found'}")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-error-raw-response", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom ninja.responses import Response").replace("return Status(error.status, error)", "return Response({'code': 'lesson_not_found'}, status=404)")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-analysis-unresolved-status-reexport", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from .exports import Status\nfrom ninja import Router")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-unresolved-error-out-reexport", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError", "from .exports import LessonNotFoundError")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-selected-syntax", with_files(("application/lesson/presentation_layer/controller.py", "def broken(:\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-one-hop-syntax", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .factory import make_error")), ("application/lesson/presentation_layer/factory.py", "def broken(:\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-missing-selected-controller-path", CONTROLLER_FILES, "check-api-error-controller-contract.py", controller_args("--controller-module", "application/lesson/presentation_layer/missing_controller.py"), 1, "사용 오류"),
        Case("controller-analysis-auto-profile", CONTROLLER_FILES, "check-api-error-controller-contract.py", (TARGET_DIR, "--error-profile", "auto", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 0, ""),
        Case("controller-analysis-missing-args", CONTROLLER_FILES, "check-api-error-controller-contract.py", (TARGET_DIR, "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--error-profile", "missing:--api-module", "missing:--controller-module", "missing:--scope-bc", "missing:--error-bc"})),
        # Reviewer gaps deliberately remain outside the deterministic oracle:
        # application collaborator identity, broad exception hidden by re-export,
        # and two-hop/off-selection helpers.
    ]


CONTEXT_FILES: Final = {
    **BASE_FILES,
    "config/api.py": """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
""",
    "application/lesson/presentation_layer/controller.py": """from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError

def get_lesson(request):
    return LessonNotFoundError()
""",
    "application/lesson/domain_layer/model.py": "class Lesson: pass\n",
    "application/lesson/published_service/public/contract/query.py": "class LessonQuery: pass\n",
}


def context_args(*extra: str) -> tuple[str, ...]:
    return (
        TARGET_DIR,
        "--error-profile",
        "dddjango-code-json",
        "--scope",
        "public-v1",
        "--api-module",
        "config/api.py",
        "--controller-module",
        "application/lesson/presentation_layer/controller.py",
        "--scope-bc",
        "lesson",
        "--error-bc",
        "lesson",
        *extra,
    )


def context_cases() -> list[Case]:
    """Context, root-purity, layer-purity, and grandfathering cases."""
    legacy_http = """from ninja import HttpError

def load_lesson():
    raise HttpError(404, "missing")
"""
    clean_legacy = "def load_lesson(): return None\n"
    preserve_args = (
        TARGET_DIR,
        "--error-profile",
        "preserve-established",
        "--scope",
        "legacy-v1",
        "--api-module",
        "legacy/api.py",
        "--controller-module",
        "legacy/controller.py",
        "--scope-bc",
        "legacy",
        "--error-bc",
        "legacy",
    )
    return [
        Case("context-clean-own-bc-presentation-error-import", CONTEXT_FILES, "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-upstream-exception-translated-in-acl", with_files(("application/lesson/infra_layer/acl/catalog.py", "from application.catalog.domain_layer.exceptions import CatalogMissing\nfrom application.lesson.domain_layer.exceptions import LessonCatalogUnavailable\n\n\ndef load_catalog(fetch):\n    try:\n        return fetch()\n    except CatalogMissing as exc:\n        raise LessonCatalogUnavailable() from exc\n"), ("application/catalog/domain_layer/exceptions.py", "class CatalogMissing(Exception): pass\n"), ("application/lesson/domain_layer/exceptions.py", "class LessonCatalogUnavailable(Exception): pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 0, ""),
        Case("context-clean-separated-preserve-scope", with_files(("legacy/api.py", "api = object()\n"), ("legacy/controller.py", "def legacy(request): return {'error': 'old'}\n"), base=CONTEXT_FILES), "check-context-isolation.py", preserve_args, 0, ""),
        Case("context-clean-existing-s1-s3-permitted-directions", with_files(("application/lesson/domain_layer/service.py", "from application.lesson.domain_layer.model import Lesson\n"), ("application/catalog/published_service/public/contract/query.py", "class CatalogQuery: pass\n"), ("application/lesson/application_layer/use_catalog.py", "from application.catalog.published_service.public.contract.query import CatalogQuery\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 0, ""),
        Case("context-root-api-imports-bc", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\nfrom application.lesson.presentation_layer.controller import get_lesson\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-root-api-local-global-error-code", with_files(("config/api.py", "from enum import StrEnum\nfrom ninja_extra import NinjaExtraAPI\nclass GlobalErrorCode(StrEnum):\n    BAD = 'bad'\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-root-api-local-error-out", with_files(("config/api.py", "from ninja import Schema\nfrom ninja_extra import NinjaExtraAPI\nclass ErrorOut(Schema):\n    detail: str\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-root-api-local-error-catalog", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\nERROR_CATALOG = {'missing': (404, 'lesson_not_found')}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-root-api-local-exception-mapping", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef map_exception(exc):\n    if isinstance(exc, LookupError):\n        return 404, {'code': 'lesson_not_found'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-root-api-path-specific-error-branch", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef handle(request):\n    if request.path.startswith('/lessons'):\n        return 404, {'code': 'lesson_not_found'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-domain-imports-ninja", with_files(("application/lesson/domain_layer/model.py", "from ninja import Status\nclass Lesson: pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-application-imports-django-http", with_files(("application/lesson/application_layer/use_case.py", "from django.http import JsonResponse\ndef run(): return None\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-infra-imports-common-error-out", with_files(("application/lesson/infra_layer/repository.py", "from common.ninja.response.error_out import ErrorOut\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-application-imports-own-bc-error-out", with_files(("application/lesson/application_layer/use_case.py", "from application.lesson.presentation_layer.schema.error_out import LessonErrorOut\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-layer-imports-other-bc-error-code", with_files(("application/lesson/application_layer/use_case.py", "from application.catalog.presentation_layer.schema.error_out import CatalogErrorCode\n"), ("application/catalog/presentation_layer/schema/error_out.py", CATALOG_DUPLICATE_ERROR_OUT), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "BLOCKER"),
        Case("context-layer-imports-other-bc-error-out", with_files(("application/lesson/infra_layer/repository.py", "from application.catalog.presentation_layer.schema.error_out import CatalogErrorOut\n"), ("application/catalog/presentation_layer/schema/error_out.py", CATALOG_DUPLICATE_ERROR_OUT), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "BLOCKER"),
        Case("context-cross-bc-exception-outside-acl", with_files(("application/lesson/presentation_layer/controller.py", "from application.catalog.domain_layer.exceptions import CatalogMissing\n"), ("application/catalog/domain_layer/exceptions.py", "class CatalogMissing(Exception): pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "BLOCKER"),
        Case("context-existing-s1-cross-bc-internal", with_files(("application/lesson/domain_layer/service.py", "from application.catalog.infra_layer.repository import CatalogRepository\n"), ("application/catalog/infra_layer/repository.py", "class CatalogRepository: pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "BLOCKER"),
        Case("context-existing-s2-contract-layer-import", with_files(("application/lesson/published_service/public/contract/query.py", "from application.lesson.domain_layer.model import Lesson\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-existing-s3-own-published-import", with_files(("application/lesson/application_layer/use_case.py", "from application.lesson.published_service.public.contract.query import LessonQuery\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-preserve-untouched-application-http-grandfathered", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http}, "check-context-isolation.py", preserve_args, 0, "", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http}),
        Case("context-preserve-touched-application-http-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http}, "check-context-isolation.py", preserve_args, 2, "BLOCKER", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": clean_legacy}),
        Case("context-preserve-untracked-application-http-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http}, "check-context-isolation.py", preserve_args, 2, "BLOCKER", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n"}),
        Case("context-analysis-multiple-api-instances", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\npublic_api = NinjaExtraAPI()\ninternal_api = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 1, "사용 오류"),
        Case("context-analysis-api-controller-overlap", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "config/api.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"overlap:--api-module/--controller-module"})),
        Case("context-analysis-selected-api-syntax", with_files(("config/api.py", "api = (\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 1, "사용 오류"),
        Case("context-analysis-selected-controller-read", CONTEXT_FILES, "check-context-isolation.py", context_args("--controller-module", "application/lesson/presentation_layer/missing.py"), 1, "사용 오류"),
        Case("context-analysis-selected-root-escape", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "../outside.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--api-module"})),
        Case("context-analysis-incomplete-code-source-args", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--api-module", "missing:--controller-module", "missing:--scope-bc", "missing:--error-bc"})),
        Case("context-clean-auto-profile-legacy-rules", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "auto", "--scope", "diagnostic", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 0, ""),
        Case("context-clean-legacy-positional-help", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR,), 0, ""),
        Case("context-fp-tests-migrations-cache-venv", {**CONTEXT_FILES, "application/lesson/application_layer/tests/test_leak.py": "from ninja import Status\n", "application/lesson/application_layer/migrations/0001_leak.py": "from ninja import Status\n", "application/lesson/application_layer/.cache/leak.py": "from ninja import Status\n", "application/lesson/application_layer/.venv/leak.py": "from ninja import Status\n"}, "check-context-isolation.py", context_args(), 0, ""),
        Case("context-fp-unignored-generated-path", {**CONTEXT_FILES, ".gitignore": "application/lesson/application_layer/ignored_leak.py\n", "application/lesson/application_layer/generated/leak.py": "from application.lesson.published_service.public.contract.query import LessonQuery\n"}, "check-context-isolation.py", context_args(), 0, "", baseline_files={**CONTEXT_FILES, ".gitignore": "application/lesson/application_layer/ignored_leak.py\n"}),
        Case("context-fp-git-ignored-selected-path", {**CONTEXT_FILES, ".gitignore": "application/lesson/application_layer/ignored_leak.py\n", "application/lesson/application_layer/ignored_leak.py": "from application.lesson.published_service.public.contract.query import LessonQuery\n"}, "check-context-isolation.py", context_args(), 0, "", baseline_files={**CONTEXT_FILES, ".gitignore": "application/lesson/application_layer/ignored_leak.py\n"}),
        # Reviewer-only: dynamic/relative import equivalents, semantic root
        # mapping lookalikes, and source-surface membership completeness.
    ]


COMPOSITION_CLEAN_FILES: Final = {
    "application/lesson/application_layer/use_case.py": "def run(): return None\n",
    "application/lesson/composition_root.py": "def build_use_case(): return object()\n",
}

REGISTRAR_FILES: Final = {
    "config/api.py": """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
""",
    "application/lesson/presentation_layer/controller.py": "class LessonController: pass\n",
    "application/lesson/presentation_layer/registrar.py": """from .controller import LessonController

def register_lesson_api(api):
    api.register_controllers(LessonController)
""",
    "application/catalog/presentation_layer/controller.py": "class CatalogController: pass\n",
    "application/catalog/presentation_layer/registrar.py": """from .controller import CatalogController

def register_catalog_api(api):
    api.register_controllers(CatalogController)
""",
    "config/urls.py": """from config.api import api
from application.lesson.presentation_layer.registrar import register_lesson_api
from application.catalog.presentation_layer.registrar import register_catalog_api

register_lesson_api(api)
register_catalog_api(api)
urlpatterns = []
""",
}


def composition_args(*extra: str) -> tuple[str, ...]:
    return (
        TARGET_DIR,
        "--error-profile",
        "dddjango-code-json",
        "--scope",
        "public-v1",
        "--api-module",
        "config/api.py",
        "--urlconf-module",
        "config/urls.py",
        "--registrar-module",
        "application/lesson/presentation_layer/registrar.py",
        "--registrar-module",
        "application/catalog/presentation_layer/registrar.py",
        *extra,
    )


def composition_cases() -> list[Case]:
    """Legacy DI placement and future URLconf/registrar composition cases."""
    registrar_imports_api = REGISTRAR_FILES["application/lesson/presentation_layer/registrar.py"].replace(
        "from .controller import LessonController",
        "from .controller import LessonController\nfrom config.api import api",
    )
    top_level_registration = (
        REGISTRAR_FILES["application/lesson/presentation_layer/registrar.py"]
        + "\nfrom .registration_probe import registration_probe\n"
        + "registration_probe.register_controllers(LessonController)\n"
    )
    preserve_selector_args = (
        TARGET_DIR,
        "--error-profile",
        "preserve-established",
        "--scope",
        "legacy-v1",
        "--api-module",
        "legacy/api.py",
        "--urlconf-module",
        "legacy/urls.py",
        "--registrar-module",
        "legacy/registrar.py",
    )
    auto_selector_args = (
        TARGET_DIR,
        "--error-profile",
        "auto",
        "--scope",
        "diagnostic",
        "--api-module",
        "legacy/api.py",
        "--urlconf-module",
        "legacy/urls.py",
        "--registrar-module",
        "legacy/registrar.py",
    )
    inactive_registrar_files = {
        "legacy/api.py": "api = object()\n",
        "legacy/urls.py": "from legacy.api import api\n",
        "legacy/registrar.py": "from legacy.api import api\napi.register_controllers(object)\n",
    }
    return [
        Case("composition-legacy-clean-root-file", COMPOSITION_CLEAN_FILES, "check-composition-root.py", (TARGET_DIR,), 0, ""),
        Case("composition-legacy-clean-empty-application-layer-exempt", {"application/catalog/application_layer/__init__.py": ""}, "check-composition-root.py", (TARGET_DIR,), 0, ""),
        Case("composition-legacy-v1-off-tree-folder", {**COMPOSITION_CLEAN_FILES, "application/lesson/composition/provider.py": "def provide(): return object()\n"}, "check-composition-root.py", (TARGET_DIR,), 2, "BLOCKER"),
        Case("composition-legacy-v2-misplaced-composition-root", {"application/lesson/application_layer/use_case.py": "def run(): return None\n", "application/lesson/infra_layer/composition_root.py": "def build(): return object()\n"}, "check-composition-root.py", (TARGET_DIR,), 2, "BLOCKER"),
        Case("composition-legacy-v3-required-root-absent", {"application/lesson/application_layer/use_case.py": "def run(): return None\n"}, "check-composition-root.py", (TARGET_DIR,), 2, "BLOCKER"),
        Case("composition-code-clean-selected-registrars-called-once", REGISTRAR_FILES, "check-composition-root.py", composition_args(), 0, ""),
        Case("composition-code-clean-unselected-preserve-urlconf-registrar", {**REGISTRAR_FILES, "legacy/api.py": "api = object()\n", "legacy/urls.py": "from legacy.api import api\nfrom legacy.registrar import register_legacy_api\nregister_legacy_api(api)\n", "legacy/registrar.py": "def register_legacy_api(api): api.register_controllers(object)\n"}, "check-composition-root.py", composition_args(), 0, ""),
        Case("composition-registrar-imports-project-api", with_files(("application/lesson/presentation_layer/registrar.py", registrar_imports_api), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registrar-module-top-level-register-controllers", with_files(("application/lesson/presentation_layer/registrar.py", top_level_registration), ("application/lesson/presentation_layer/registration_probe.py", "class RegistrationProbe:\n    def register_controllers(self, controller): pass\n\n\nregistration_probe = RegistrationProbe()\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-urlconf-omits-registrar-call", with_files(("config/urls.py", REGISTRAR_FILES["config/urls.py"].replace("register_catalog_api(api)\n", "")), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-urlconf-duplicates-registrar-call", with_files(("config/urls.py", REGISTRAR_FILES["config/urls.py"] + "register_lesson_api(api)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registration-occurs-outside-registrar", with_files(("config/urls.py", REGISTRAR_FILES["config/urls.py"] + "api.register_controllers(object)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-code-v1-di-still-blocked", {**REGISTRAR_FILES, "application/lesson/composition/provider.py": "def provide(): return object()\n"}, "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-code-v2-di-still-blocked", {**REGISTRAR_FILES, "application/lesson/infra_layer/composition_root.py": "def build(): return object()\n"}, "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-code-v3-di-still-blocked", {**REGISTRAR_FILES, "application/lesson/application_layer/use_case.py": "def run(): return None\n"}, "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-preserve-registrar-rules-na", inactive_registrar_files, "check-composition-root.py", preserve_selector_args, 0, ""),
        Case("composition-auto-registrar-rules-na", inactive_registrar_files, "check-composition-root.py", auto_selector_args, 0, ""),
        Case("composition-preserve-existing-di-v3-still-runs", {**inactive_registrar_files, "application/legacy/application_layer/use_case.py": "def run(): return None\n"}, "check-composition-root.py", preserve_selector_args, 2, "BLOCKER"),
        Case("composition-auto-existing-di-v1-still-runs", {**inactive_registrar_files, "application/legacy/domain_layer/model.py": "class Model: pass\n", "application/legacy/composition/provider.py": "def provide(): return object()\n"}, "check-composition-root.py", auto_selector_args, 2, "BLOCKER"),
        Case("composition-analysis-missing-urlconf-selector", REGISTRAR_FILES, "check-composition-root.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--registrar-module", "application/lesson/presentation_layer/registrar.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--urlconf-module"})),
        Case("composition-analysis-missing-registrar-selector", REGISTRAR_FILES, "check-composition-root.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--urlconf-module", "config/urls.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--registrar-module"})),
        Case("composition-analysis-duplicate-urlconf-selector", REGISTRAR_FILES, "check-composition-root.py", composition_args("--urlconf-module", "config/urls.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"cardinality:--urlconf-module"})),
        Case("composition-analysis-duplicate-registrar-selector", REGISTRAR_FILES, "check-composition-root.py", composition_args("--registrar-module", "application/lesson/presentation_layer/registrar.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"duplicate:--registrar-module"})),
        Case("composition-analysis-urlconf-registrar-overlap", REGISTRAR_FILES, "check-composition-root.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--urlconf-module", "config/urls.py", "--registrar-module", "config/urls.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"overlap:--urlconf-module/--registrar-module"})),
        Case("composition-analysis-selected-urlconf-syntax", with_files(("config/urls.py", "urlpatterns = [\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 1, "사용 오류"),
        Case("composition-analysis-selected-registrar-syntax", with_files(("application/lesson/presentation_layer/registrar.py", "def broken(:\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 1, "사용 오류"),
        Case("composition-analysis-selected-registrar-read", REGISTRAR_FILES, "check-composition-root.py", composition_args("--registrar-module", "application/missing/presentation_layer/registrar.py"), 1, "사용 오류"),
        Case("composition-analysis-selected-root-escape", REGISTRAR_FILES, "check-composition-root.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--urlconf-module", "../outside.py", "--registrar-module", "application/lesson/presentation_layer/registrar.py", "--registrar-module", "application/catalog/presentation_layer/registrar.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--urlconf-module"})),
        Case("composition-fp-tests-migrations-cache-venv", {**COMPOSITION_CLEAN_FILES, "application/lesson/tests/composition_root.py": "pass\n", "application/lesson/migrations/composition_root.py": "pass\n", "application/lesson/.cache/composition_root.py": "pass\n", "application/lesson/.venv/composition_root.py": "pass\n"}, "check-composition-root.py", (TARGET_DIR,), 0, ""),
        Case("composition-fp-unignored-generated-path", {**COMPOSITION_CLEAN_FILES, ".gitignore": "application/lesson/infra_layer/ignored/composition_root.py\n", "application/lesson/infra_layer/generated/composition_root.py": "pass\n"}, "check-composition-root.py", (TARGET_DIR,), 0, "", baseline_files={**COMPOSITION_CLEAN_FILES, ".gitignore": "application/lesson/infra_layer/ignored/composition_root.py\n"}),
        Case("composition-fp-git-ignored-selected-path", {**COMPOSITION_CLEAN_FILES, ".gitignore": "application/lesson/infra_layer/ignored/composition_root.py\n", "application/lesson/infra_layer/ignored/composition_root.py": "pass\n"}, "check-composition-root.py", (TARGET_DIR,), 0, "", baseline_files={**COMPOSITION_CLEAN_FILES, ".gitignore": "application/lesson/infra_layer/ignored/composition_root.py\n"}),
        # Reviewer-only: dynamic/re-export calls and semantic completeness of
        # the controller set registered inside each registrar.
    ]


OPENAPI_CONTROLLER = """from ninja import Router, Status
from application.lesson.presentation_layer.schema.error_out import LessonConflictError, LessonErrorOut, LessonNotFoundError

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: LessonErrorOut, 409: LessonErrorOut})
def get_lesson(request, lesson_id: int):
    if lesson_id == 0:
        error = LessonNotFoundError()
        return Status(error.status, error)
    if lesson_id < 0:
        error = LessonConflictError()
        return Status(error.status, error)
    return {"id": lesson_id}
"""

OPENAPI_FILES: Final = {
    **BASE_FILES,
    "config/api.py": """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
""",
    "application/lesson/presentation_layer/controller.py": OPENAPI_CONTROLLER,
}


def openapi_args(*extra: str) -> tuple[str, ...]:
    return (
        TARGET_DIR,
        "--error-profile",
        "dddjango-code-json",
        "--scope",
        "public-v1",
        "--api-module",
        "config/api.py",
        "--controller-module",
        "application/lesson/presentation_layer/controller.py",
        "--scope-bc",
        "lesson",
        "--error-bc",
        "lesson",
        *extra,
    )


def openapi_cases() -> list[Case]:
    """Returned-error/status/schema agreement and OpenAPI purity cases."""
    preserve_files = {
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": """from ninja import Router

router = Router()

@router.get("/legacy", response={200: dict, 400: dict})
def legacy(request):
    return 400, {"error": "legacy"}
""",
    }
    clean_with_preserve = {**OPENAPI_FILES, **preserve_files}
    metadata_controller = OPENAPI_CONTROLLER.replace(
        'response={200: dict, 404: LessonErrorOut, 409: LessonErrorOut})',
        'response={200: dict, 404: LessonErrorOut, 409: LessonErrorOut}, openapi_extra={"security": [{"Bearer": []}], "examples": {"ok": {"value": {"id": 1}}}})',
    )
    missing_409 = OPENAPI_CONTROLLER.replace(
        "response={200: dict, 404: LessonErrorOut, 409: LessonErrorOut}",
        "response={200: dict, 404: LessonErrorOut}",
    )
    framework_base = OPENAPI_CONTROLLER.replace(
        "    if lesson_id == 0:\n        error = LessonNotFoundError()\n        return Status(error.status, error)\n",
        "",
    )

    def framework_advertisement(status: int) -> str:
        return framework_base.replace(
            "response={200: dict, 404: LessonErrorOut, 409: LessonErrorOut}",
            f"response={{200: dict, 409: LessonErrorOut, {status}: LessonErrorOut}}",
        )

    preserve_extra = """from ninja import Router

router = Router()

@router.get("/legacy", response={200: dict}, openapi_extra={"responses": {"400": {"description": "legacy"}}})
def legacy(request):
    return {"ok": True}
"""
    preserve_args = (
        TARGET_DIR,
        "--error-profile",
        "preserve-established",
        "--scope",
        "legacy-v1",
        "--api-module",
        "legacy/api.py",
        "--controller-module",
        "application/legacy/presentation_layer/controller.py",
        "--scope-bc",
        "legacy",
        "--error-bc",
        "legacy",
    )
    framework_extra = OPENAPI_CONTROLLER.replace(
        'response={200: dict, 404: LessonErrorOut, 409: LessonErrorOut})',
        'response={200: dict, 404: LessonErrorOut, 409: LessonErrorOut}, openapi_extra={"responses": {"401": {"description": "unauthorized"}}})',
    )
    override_api = """from ninja_extra import NinjaExtraAPI

class ProjectAPI(NinjaExtraAPI):
    def get_openapi_schema(self, *args, **kwargs):
        schema = super().get_openapi_schema(*args, **kwargs)
        schema["x-errors"] = True
        return schema

api = ProjectAPI()
"""
    monkeypatch_api = """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
original_get_openapi_schema = api.get_openapi_schema

def patched_schema(*args, **kwargs):
    schema = original_get_openapi_schema(*args, **kwargs)
    schema["x-errors"] = True
    return schema

api.get_openapi_schema = patched_schema
"""
    postprocessor_api = """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()

def build_openapi_schema():
    schema = api.get_openapi_schema()
    schema["components"]["schemas"]["Error"] = {"type": "object"}
    return schema
"""
    excluded_violation = """from ninja import Router
router = Router()
@router.get("/ignored", response={200: dict}, openapi_extra={"responses": {"500": {"description": "ignored"}}})
def ignored(request): return {"ok": True}
"""
    return [
        Case("openapi-clean-direct-404-409-same-bc-base", OPENAPI_FILES, "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-framework-statuses-not-advertised", OPENAPI_FILES, "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-separated-preserve-response-behavior", clean_with_preserve, "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-security-examples-metadata", with_files(("application/lesson/presentation_layer/controller.py", metadata_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-returned-409-missing-from-response", with_files(("application/lesson/presentation_layer/controller.py", missing_409), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-returned-error-mapped-to-other-bc-base", with_files(("application/catalog/presentation_layer/schema/error_out.py", CATALOG_DUPLICATE_ERROR_OUT), ("application/lesson/presentation_layer/controller.py", OPENAPI_CONTROLLER.replace("409: LessonErrorOut", "409: CatalogErrorOut").replace("from application.lesson.presentation_layer.schema.error_out import", "from application.catalog.presentation_layer.schema.error_out import CatalogErrorOut\nfrom application.lesson.presentation_layer.schema.error_out import")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "BLOCKER"),
        Case("openapi-returned-error-mapped-to-common-base", with_files(("application/lesson/presentation_layer/controller.py", OPENAPI_CONTROLLER.replace("409: LessonErrorOut", "409: ErrorOut").replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom common.ninja.response.error_out import ErrorOut")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-returned-error-mapped-to-concrete", with_files(("application/lesson/presentation_layer/controller.py", OPENAPI_CONTROLLER.replace("409: LessonErrorOut", "409: LessonConflictError")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-401-bc-error-advertised", with_files(("application/lesson/presentation_layer/controller.py", framework_advertisement(401)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-403-bc-error-advertised", with_files(("application/lesson/presentation_layer/controller.py", framework_advertisement(403)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-route-404-bc-error-advertised", with_files(("application/lesson/presentation_layer/controller.py", framework_advertisement(404)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-422-bc-error-advertised", with_files(("application/lesson/presentation_layer/controller.py", framework_advertisement(422)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-429-bc-error-advertised", with_files(("application/lesson/presentation_layer/controller.py", framework_advertisement(429)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-500-bc-error-advertised", with_files(("application/lesson/presentation_layer/controller.py", framework_advertisement(500)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-response-openapi-extra", with_files(("application/lesson/presentation_layer/controller.py", framework_extra), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-get-openapi-schema-override", with_files(("config/api.py", override_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-get-openapi-schema-monkeypatch", with_files(("config/api.py", monkeypatch_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-get-openapi-schema-postprocessor", with_files(("config/api.py", postprocessor_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-preserve-untouched-openapi-extra-grandfathered", {"legacy/api.py": "api = object()\n", "application/legacy/presentation_layer/controller.py": preserve_extra}, "check-openapi-error-declaration.py", preserve_args, 0, "", baseline_files={"legacy/api.py": "api = object()\n", "application/legacy/presentation_layer/controller.py": preserve_extra}),
        Case("openapi-preserve-touched-openapi-extra-blocked", {"legacy/api.py": "api = object()\n", "application/legacy/presentation_layer/controller.py": preserve_extra}, "check-openapi-error-declaration.py", preserve_args, 2, "BLOCKER", baseline_files={"legacy/api.py": "api = object()\n", "application/legacy/presentation_layer/controller.py": preserve_files["legacy/controller.py"]}),
        Case("openapi-analysis-unresolved-required-response-mapping", with_files(("application/lesson/presentation_layer/controller.py", OPENAPI_CONTROLLER.replace("response={200: dict, 404: LessonErrorOut, 409: LessonErrorOut}", "response=build_responses()")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-analysis-api-controller-overlap", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "config/api.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"overlap:--api-module/--controller-module"})),
        Case("openapi-analysis-selected-controller-syntax", with_files(("application/lesson/presentation_layer/controller.py", "def broken(:\n"), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-analysis-selected-controller-read", OPENAPI_FILES, "check-openapi-error-declaration.py", openapi_args("--controller-module", "application/lesson/presentation_layer/missing.py"), 1, "사용 오류"),
        Case("openapi-analysis-selected-root-escape", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "../outside.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--api-module"})),
        Case("openapi-clean-auto-profile-legacy-rules", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "auto", "--scope", "diagnostic", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 0, ""),
        Case("openapi-analysis-missing-code-source-args", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--api-module", "missing:--controller-module", "missing:--scope-bc", "missing:--error-bc"})),
        Case("openapi-clean-legacy-positional-help", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, ""),
        Case("openapi-fp-tests-migrations-cache-venv", {**OPENAPI_FILES, "application/lesson/presentation_layer/tests/test_openapi.py": excluded_violation, "application/lesson/presentation_layer/migrations/0001_openapi.py": excluded_violation, "application/lesson/presentation_layer/.cache/openapi.py": excluded_violation, "application/lesson/presentation_layer/.venv/openapi.py": excluded_violation}, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, ""),
        Case("openapi-fp-unignored-generated-path", {**OPENAPI_FILES, ".gitignore": "application/lesson/presentation_layer/ignored_openapi.py\n", "application/lesson/presentation_layer/generated/openapi.py": excluded_violation}, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, "", baseline_files={**OPENAPI_FILES, ".gitignore": "application/lesson/presentation_layer/ignored_openapi.py\n"}),
        Case("openapi-fp-git-ignored-selected-path", {**OPENAPI_FILES, ".gitignore": "application/lesson/presentation_layer/ignored_openapi.py\n", "application/lesson/presentation_layer/ignored_openapi.py": excluded_violation}, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, "", baseline_files={**OPENAPI_FILES, ".gitignore": "application/lesson/presentation_layer/ignored_openapi.py\n"}),
        # Reviewer-only: dynamic response mappings and status-specific code
        # subset precision for a shared BC base schema.
    ]


SUCCESS_SCHEMA = """from ninja import Schema

class LessonOut(Schema):
    id: int
"""


def success_files(controller: str) -> dict[str, str]:
    return {
        "application/lesson/presentation_layer/schema.py": SUCCESS_SCHEMA,
        "application/lesson/presentation_layer/controller.py": controller,
    }


def success_args(*extra: str) -> tuple[str, ...]:
    return (
        TARGET_DIR,
        "--controller-module",
        "application/lesson/presentation_layer/controller.py",
        *extra,
    )


def success_cases() -> list[Case]:
    """Declared JSON-success bypass and non-JSON response carve-outs."""
    schema_object = """from ninja import Router
from .schema import LessonOut
router = Router()
@router.get("/{lesson_id}", response={200: LessonOut})
def get_lesson(request, lesson_id: int):
    return LessonOut(id=lesson_id)
"""
    success_status = """from ninja import Router, Status
from .schema import LessonOut
router = Router()
@router.post("/", response={201: LessonOut})
def create_lesson(request):
    return Status(201, LessonOut(id=1))
"""
    file_response = """from ninja import Router
from django.http import FileResponse
router = Router()
@router.get("/export")
def export(request):
    return FileResponse(open("lesson.csv", "rb"))
"""
    file_alias = file_response.replace("FileResponse\n", "FileResponse as Download\n").replace("FileResponse(open", "Download(open")
    stream_direct = """from ninja import Router
from django.http import StreamingHttpResponse
router = Router()
@router.get("/stream")
def stream(request):
    return StreamingHttpResponse(iter([b"lesson"]))
"""
    stream_alias = """from ninja import Router
from django.http import StreamingHttpResponse as Stream
router = Router()
@router.get("/stream")
def stream(request):
    return Stream(iter([b"lesson"]))
"""
    redirect_direct = """from ninja import Router
from django.shortcuts import redirect
router = Router()
@router.get("/latest")
def latest(request):
    return redirect("/lessons/1")
"""
    redirect_alias = """from ninja import Router
from django.shortcuts import redirect as go_to
router = Router()
@router.get("/latest")
def latest(request):
    return go_to("/lessons/1")
"""
    no_content = """from ninja import Router
from django.http import HttpResponse
router = Router()
@router.delete("/{lesson_id}", response={204: None})
def delete_lesson(request, lesson_id: int):
    return HttpResponse(status=204)
"""
    raw_200 = """from ninja import Router
from django.http import JsonResponse
from .schema import LessonOut
router = Router()
@router.get("/", response={200: LessonOut})
def list_lessons(request):
    return JsonResponse({"id": 1})
"""
    raw_200_decoy = raw_200.replace(
        "from .schema import LessonOut",
        "from application.lesson.presentation_layer.schema import LessonOut",
    )
    raw_201_alias = """from ninja import Router
from django.http import JsonResponse as Json
from .schema import LessonOut
router = Router()
@router.post("/", response={201: LessonOut})
def create_lesson(request):
    return Json({"id": 1}, status=201)
"""
    raw_202 = """from ninja import Router
from django.http import HttpResponse
from .schema import LessonOut
router = Router()
@router.post("/async", response={202: LessonOut})
def queue_lesson(request):
    return HttpResponse('{"id": 1}', status=202, content_type="application/json")
"""
    raw_203_alias = """from ninja import Router
from django.http import HttpResponse as RawResponse
from .schema import LessonOut
router = Router()
@router.get("/proxy", response={203: LessonOut})
def proxy_lesson(request):
    return RawResponse('{"id": 1}', status=203, content_type="application/json")
"""
    return [
        Case("success-clean-declared-schema-object", success_files(schema_object), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-clean-declared-status-wrapper", success_files(success_status), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-clean-file-response-direct", success_files(file_response), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-clean-file-response-as-alias", success_files(file_alias), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-clean-streaming-response-direct", success_files(stream_direct), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-clean-streaming-response-as-alias", success_files(stream_alias), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-clean-redirect-direct", success_files(redirect_direct), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-clean-redirect-as-alias", success_files(redirect_alias), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-clean-schema-less-204", success_files(no_content), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-raw-json-response-200", success_files(raw_200), "check-response-schema-bypass.py", success_args(), 2, "BLOCKER"),
        Case("success-raw-json-response-alias-201", success_files(raw_201_alias), "check-response-schema-bypass.py", success_args(), 2, "BLOCKER"),
        Case("success-raw-http-response-202", success_files(raw_202), "check-response-schema-bypass.py", success_args(), 2, "BLOCKER"),
        Case("success-raw-http-response-alias-203", success_files(raw_203_alias), "check-response-schema-bypass.py", success_args(), 2, "BLOCKER"),
        Case("success-analysis-selected-syntax", success_files("def broken(:\n"), "check-response-schema-bypass.py", success_args(), 1, "사용 오류"),
        Case("success-analysis-selected-read", success_files(schema_object), "check-response-schema-bypass.py", success_args("--controller-module", "application/lesson/presentation_layer/missing.py"), 1, "사용 오류"),
        Case("success-fp-tests-migrations-cache-venv", {**success_files(schema_object), "application/lesson/presentation_layer/tests/test_bypass.py": raw_200_decoy, "application/lesson/presentation_layer/migrations/0001_bypass.py": raw_200_decoy, "application/lesson/presentation_layer/.cache/bypass.py": raw_200_decoy, "application/lesson/presentation_layer/.venv/bypass.py": raw_200_decoy}, "check-response-schema-bypass.py", (TARGET_DIR,), 0, ""),
        Case("success-fp-unignored-generated-path", {**success_files(schema_object), ".gitignore": "application/lesson/presentation_layer/ignored_bypass.py\n", "application/lesson/presentation_layer/generated/bypass.py": raw_200_decoy}, "check-response-schema-bypass.py", (TARGET_DIR,), 0, "", baseline_files={**success_files(schema_object), ".gitignore": "application/lesson/presentation_layer/ignored_bypass.py\n"}),
        Case("success-fp-git-ignored-selected-path", {**success_files(schema_object), ".gitignore": "application/lesson/presentation_layer/ignored_bypass.py\n", "application/lesson/presentation_layer/ignored_bypass.py": raw_200_decoy}, "check-response-schema-bypass.py", (TARGET_DIR,), 0, "", baseline_files={**success_files(schema_object), ".gitignore": "application/lesson/presentation_layer/ignored_bypass.py\n"}),
        # Reviewer-only: helper/re-export/subclass-mediated success bypasses.
    ]


def validate_checker_args(case: Case) -> None:
    """Reject malformed matrix data unless the case names every intended issue."""
    args = case.checker_args
    if args.count(TARGET_DIR) != 1 or not args or args[0] != TARGET_DIR:
        raise ValueError("checker_args must contain TARGET_DIR exactly once")
    values_by_argument: dict[str, list[str]] = {}
    index = 0
    while index < len(args):
        token = args[index]
        if token == TARGET_DIR:
            index += 1
            continue
        arity = ARGUMENT_ARITY.get(token)
        if arity is None:
            raise ValueError(f"unsupported checker argument in matrix: {token}")
        if index + arity >= len(args):
            raise ValueError(f"missing value for checker argument: {token}")
        values_by_argument.setdefault(token, []).append(args[index + 1])
        index += arity + 1

    if not values_by_argument:
        if case.allowed_arg_issues:
            raise ValueError(f"[{case.name}] target-only command cannot allow argument issues")
        return

    allowed_arguments = CHECKER_ALLOWED_ARGUMENTS.get(case.checker)
    if allowed_arguments is None:
        raise ValueError(f"unsupported checker in matrix: {case.checker}")
    unsupported = set(values_by_argument) - allowed_arguments
    if unsupported:
        raise ValueError(f"[{case.name}] unsupported checker-specific arguments: {sorted(unsupported)}")

    required_arguments = {
        "check-error-centralization.py": {
            "--error-profile",
            "--scope",
            "--api-module",
            "--controller-module",
            "--scope-bc",
            "--project-code-error-module",
        },
        "check-api-error-controller-contract.py": {
            "--error-profile",
            "--scope",
            "--api-module",
            "--controller-module",
            "--scope-bc",
            "--error-bc",
        },
        "check-context-isolation.py": {
            "--error-profile",
            "--scope",
            "--api-module",
            "--controller-module",
            "--scope-bc",
            "--error-bc",
        },
        "check-openapi-error-declaration.py": {
            "--error-profile",
            "--scope",
            "--api-module",
            "--controller-module",
            "--scope-bc",
            "--error-bc",
        },
        "check-composition-root.py": {
            "--error-profile",
            "--scope",
            "--api-module",
            "--urlconf-module",
            "--registrar-module",
        },
        "check-response-schema-bypass.py": {"--controller-module"},
    }[case.checker]
    issues = {
        f"missing:{argument}"
        for argument in required_arguments
        if not values_by_argument.get(argument)
    }

    profile_values = values_by_argument.get("--error-profile", [])
    if profile_values == ["preserve-established"] and case.checker == "check-error-centralization.py":
        if not values_by_argument.get("--project-preserve-error-module"):
            issues.add("missing:--project-preserve-error-module")

    for argument, values in values_by_argument.items():
        if argument in SINGULAR_ARGUMENTS and len(values) != 1:
            issues.add(f"cardinality:{argument}")
        if argument not in SINGULAR_ARGUMENTS and len(values) != len(set(values)):
            issues.add(f"duplicate:{argument}")
        if argument not in SOURCE_PATH_ARGUMENTS:
            continue
        for value in values:
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                issues.add(f"root-escape:{argument}")
            elif "/" not in value or not value.endswith(".py") or path.as_posix() != value:
                issues.add(f"invalid-source-path:{argument}")

    api_modules = set(values_by_argument.get("--api-module", []))
    controller_modules = set(values_by_argument.get("--controller-module", []))
    if api_modules & controller_modules:
        issues.add("overlap:--api-module/--controller-module")
    urlconf_modules = set(values_by_argument.get("--urlconf-module", []))
    registrar_modules = set(values_by_argument.get("--registrar-module", []))
    if urlconf_modules & registrar_modules:
        issues.add("overlap:--urlconf-module/--registrar-module")

    if issues != set(case.allowed_arg_issues):
        raise ValueError(
            f"[{case.name}] checker argument issues differ: "
            f"actual={sorted(issues)}, allowed={sorted(case.allowed_arg_issues)}"
        )


def write_fixture(root: Path, files: dict[str, str]) -> None:
    """Write fixture sources while rejecting absolute and root-escaping paths."""
    root = root.resolve()
    for relative, source in files.items():
        candidate = root / relative
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"fixture path escapes temporary root: {relative}") from exc
        if Path(relative).is_absolute():
            raise ValueError(f"fixture path must be relative: {relative}")
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(source, encoding="utf-8")


def initialize_git_fixture(root: Path, baseline_files: dict[str, str]) -> None:
    """Commit a deterministic baseline so touched/grandfather cases are real."""
    write_fixture(root, baseline_files)
    commands = (
        ("git", "init", "--quiet"),
        ("git", "add", "."),
        (
            "git",
            "-c",
            "user.name=API Error Matrix",
            "-c",
            "user.email=matrix@example.invalid",
            "commit",
            "--quiet",
            "--allow-empty",
            "-m",
            "fixture baseline",
        ),
    )
    for command in commands:
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise OSError(
                f"git fixture setup failed ({' '.join(command)}): "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )


def run_case(case: Case) -> tuple[bool, str, int]:
    validate_checker_args(case)
    checker = CHECKER_DIR / case.checker
    with tempfile.TemporaryDirectory(prefix="dddjango-api-error-") as directory:
        fixture_root = Path(directory)
        if case.baseline_files is not None:
            initialize_git_fixture(fixture_root, case.baseline_files)
        write_fixture(fixture_root, case.files)
        command = [sys.executable, str(checker)]
        command.extend(str(fixture_root) if arg == TARGET_DIR else arg for arg in case.checker_args)
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    output = f"{completed.stdout}\n{completed.stderr}"
    tracebacks = output.count("Traceback (most recent call last):")
    fragment_matches = not case.expected_fragment or case.expected_fragment in output
    passed = completed.returncode == case.expected_exit and fragment_matches
    if passed:
        return True, "", tracebacks
    return False, (
        f"[{case.name}] expected exit={case.expected_exit}, fragment={case.expected_fragment!r}; "
        f"actual exit={completed.returncode}\nstdout:\n{completed.stdout or '<empty>'}\n"
        f"stderr:\n{completed.stderr or '<empty>'}"
    ), tracebacks


def main() -> int:
    cases = [
        *schema_cases(),
        *controller_cases(),
        *context_cases(),
        *composition_cases(),
        *openapi_cases(),
        *success_cases(),
    ]
    passed = 0
    checker_mismatches = 0
    runner_failures = 0
    tracebacks = 0
    for case in cases:
        try:
            ok, detail, case_tracebacks = run_case(case)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            runner_failures += 1
            print(f"[{case.name}] runner failure: {exc}")
            continue
        tracebacks += case_tracebacks
        if ok:
            passed += 1
        else:
            checker_mismatches += 1
            print(detail)
    print(
        "api-error backstop matrix: "
        f"passed={passed} checker_mismatches={checker_mismatches} "
        f"runner_failures={runner_failures} tracebacks={tracebacks} total={len(cases)}"
    )
    return 1 if checker_mismatches or runner_failures or tracebacks else 0


if __name__ == "__main__":
    raise SystemExit(main())
