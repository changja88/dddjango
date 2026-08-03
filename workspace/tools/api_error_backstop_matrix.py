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
AUTO_PROFILE_ARGS: Final = (TARGET_DIR, "--error-profile", "auto")

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
TARGET_ONLY_CHECKERS: Final = frozenset(
    {
        "check-error-centralization.py",
        "check-context-isolation.py",
        "check-composition-root.py",
        "check-openapi-error-declaration.py",
        "check-response-schema-bypass.py",
    }
)
PROFILE_REQUIRED_ARGUMENTS: Final = {
    "dddjango-code-json": {
        "check-error-centralization.py": frozenset(
            {
                "--scope",
                "--api-module",
                "--controller-module",
                "--scope-bc",
                "--project-code-error-module",
            }
        ),
        "check-api-error-controller-contract.py": frozenset(
            {"--scope", "--api-module", "--controller-module", "--scope-bc"}
        ),
        "check-context-isolation.py": frozenset(
            {"--scope", "--api-module", "--controller-module", "--scope-bc"}
        ),
        "check-openapi-error-declaration.py": frozenset(
            {"--scope", "--api-module", "--controller-module", "--scope-bc"}
        ),
        "check-composition-root.py": frozenset(
            {"--scope", "--api-module", "--urlconf-module", "--registrar-module"}
        ),
    },
    "preserve-established": {
        "check-error-centralization.py": frozenset(
            {"--scope", "--api-module", "--controller-module", "--scope-bc"}
        ),
        "check-api-error-controller-contract.py": frozenset(
            {"--scope", "--api-module", "--controller-module", "--scope-bc"}
        ),
        "check-context-isolation.py": frozenset(
            {"--scope", "--api-module", "--controller-module", "--scope-bc"}
        ),
        "check-openapi-error-declaration.py": frozenset(
            {"--scope", "--api-module", "--controller-module", "--scope-bc"}
        ),
        "check-composition-root.py": frozenset({"--scope", "--api-module"}),
    },
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

ALIAS_COMMON_ERROR_OUT = COMMON_ERROR_OUT.replace(
    "from ninja import Schema",
    "from ninja import Schema as NinjaSchema",
).replace("class ErrorOut(Schema):", "class ErrorOut(NinjaSchema):")

ALIAS_LESSON_ERROR_OUT = (
    LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum as StringEnum")
    .replace(
        "from common.ninja.response.error_out import ErrorOut",
        "from common.ninja.response.error_out import ErrorOut as CommonErrorOut",
    )
    .replace("class LessonErrorCode(StrEnum):", "class LessonErrorCode(StringEnum):")
    .replace("class LessonErrorOut(ErrorOut):", "class LessonErrorOut(CommonErrorOut):")
)

DYNAMIC_COMMON_ERROR_OUT = COMMON_ERROR_OUT + "    trace_id: str\n"

DYNAMIC_LESSON_ERROR_OUT = (
    LESSON_ERROR_OUT.replace(
        '    detail: str = "The lesson does not exist."\n',
        '    detail: str = "The lesson does not exist."\n'
        '    trace_id: str = "lesson-not-found"\n',
    ).replace(
        '    detail: str = "The lesson cannot be changed."\n',
        '    detail: str = "The lesson cannot be changed."\n'
        '    trace_id: str = "lesson-conflict"\n',
    )
)

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

VALID_CATALOG_ERROR_OUT = CATALOG_DUPLICATE_ERROR_OUT.replace(
    'NOT_FOUND = "lesson_not_found"',
    'NOT_FOUND = "catalog_not_found"',
)

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
    preserve_empty_inventories = {
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": "def legacy(request): return {'error': 'old'}\n",
        "application/legacy/application_layer/use_case.py": (
            "def run():\n"
            "    status = 404\n"
            "    return status\n"
        ),
    }
    preserve_empty_inventory_args = (
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
    )
    alias_import_files = with_files(
        ("common/ninja/response/error_out.py", ALIAS_COMMON_ERROR_OUT),
        ("application/lesson/presentation_layer/schema/error_out.py", ALIAS_LESSON_ERROR_OUT),
    )
    dynamic_required_files = with_files(
        ("common/ninja/response/error_out.py", DYNAMIC_COMMON_ERROR_OUT),
        ("application/lesson/presentation_layer/schema/error_out.py", DYNAMIC_LESSON_ERROR_OUT),
    )
    missing_dynamic_default = DYNAMIC_LESSON_ERROR_OUT.replace(
        '    trace_id: str = "lesson-not-found"\n',
        "",
        1,
    )
    preserve_duplicate_error_out = LESSON_ERROR_OUT.replace("Lesson", "Legacy")
    code_with_preserve_duplicate = with_files(
        (
            "application/legacy/presentation_layer/schema/error_out.py",
            preserve_duplicate_error_out,
        ),
    )
    shared_code_concretes = (
        LESSON_ERROR_OUT.replace(
            "code: LessonErrorCode = LessonErrorCode.CONFLICT",
            "code: LessonErrorCode = LessonErrorCode.NOT_FOUND",
        )
        .replace('title: str = "Lesson conflict"', 'title: str = "Lesson not found"')
        .replace("status: int = 409", "status: int = 404")
    )
    ignored_generated_baseline = {
        **BASE_FILES,
        ".gitignore": "common/ninja/response/ignored.py\n",
    }
    ignored_generated_files = {
        **ignored_generated_baseline,
        "common/ninja/response/ignored.py": "def ignored_helper(): pass\n",
        "common/ninja/response/generated/decoy.py": "def generated_helper(): pass\n",
    }
    foreign_enum_default = LESSON_ERROR_OUT.replace(
        "from common.ninja.response.error_out import ErrorOut",
        "from common.ninja.response.error_out import ErrorOut\n"
        "from application.catalog.presentation_layer.schema.error_out import CatalogErrorCode",
    ).replace(
        "code: LessonErrorCode = LessonErrorCode.NOT_FOUND",
        "code: LessonErrorCode = CatalogErrorCode.NOT_FOUND",
        1,
    )
    raw_string_controller = """from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError


def get_lesson(request):
    error = LessonNotFoundError()
    error.code = "lesson_not_found"
    return error
"""
    exact_concrete_code_annotation = LESSON_ERROR_OUT.replace(
        "class LessonNotFoundError(LessonErrorOut):",
        "class PreparedLessonMissing(LessonErrorOut):",
    )
    broadened_concrete_code_annotation = exact_concrete_code_annotation.replace(
        "code: LessonErrorCode = LessonErrorCode.NOT_FOUND",
        "code: object = LessonErrorCode.NOT_FOUND",
        1,
    )
    indirect_alias_model_config = LESSON_ERROR_OUT.replace(
        "from common.ninja.response.error_out import ErrorOut",
        "from common.ninja.response.error_out import ErrorOut\n"
        "from pydantic import ConfigDict",
    ).replace(
        "class LessonNotFoundError(LessonErrorOut):",
        "class LessonNotFoundError(LessonErrorOut):\n"
        "    _wire_config = ConfigDict(alias_generator=lambda value: 'x_' + value)\n"
        "    model_config = _wire_config",
    )
    benign_indirect_model_config = LESSON_ERROR_OUT.replace(
        "from common.ninja.response.error_out import ErrorOut",
        "from common.ninja.response.error_out import ErrorOut\n"
        "from pydantic import ConfigDict",
    ).replace(
        "class LessonNotFoundError(LessonErrorOut):",
        "class LessonNotFoundError(LessonErrorOut):\n"
        "    _unused_wire_config = ConfigDict(alias_generator=lambda value: 'x_' + value)\n"
        "    _benign_config = ConfigDict(title='Lesson error')\n"
        "    model_config = _benign_config",
    )
    nested_outside_concrete = """from application.lesson.presentation_layer.schema.error_out import LessonErrorCode, LessonErrorOut


def build_error_type():
    class NestedLessonError(LessonErrorOut):
        code: LessonErrorCode = LessonErrorCode.NOT_FOUND
        title: str = "Nested"
        status: int = 404
        detail: str = "Nested outside the canonical module."
    return NestedLessonError
"""
    unrelated_nested_class = """def build_record_type():
    class NestedRecord:
        code = "ordinary_record"
    return NestedRecord
"""
    walrus_bound_error = """from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError


def get_lesson(request):
    (error := LessonNotFoundError())
    error.code = "lesson_not_found"
    return error
"""
    unrelated_walrus_object = """class Box:
    pass


def get_lesson(request):
    (box := Box())
    box.code = "ordinary_value"
    return box
"""
    concrete_name_ending_error_out = LESSON_ERROR_OUT.replace(
        "class LessonNotFoundError(LessonErrorOut):",
        "class LessonNotFoundErrorOut(LessonErrorOut):",
    )
    true_second_bc_base = LESSON_ERROR_OUT + """

class AnotherLessonErrorOut(ErrorOut):
    code: LessonErrorCode
"""
    shadowed_constructor_expressions = """from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError


def decoys(factories):
    return (
        (lambda LessonNotFoundError: LessonNotFoundError(code="ordinary"))(dict),
        [LessonNotFoundError(code="ordinary") for LessonNotFoundError in factories],
        {LessonNotFoundError(code="ordinary") for LessonNotFoundError in factories},
        {index: LessonNotFoundError(code="ordinary") for index, LessonNotFoundError in enumerate(factories)},
        tuple(LessonNotFoundError(code="ordinary") for LessonNotFoundError in factories),
    )
"""
    unshadowed_constructor_expressions = """from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError


def raw_errors(factories):
    return (
        (lambda factory: LessonNotFoundError(code="lesson_not_found"))(dict),
        [LessonNotFoundError(code="lesson_not_found") for factory in factories],
        {LessonNotFoundError(code="lesson_not_found") for factory in factories},
        {index: LessonNotFoundError(code="lesson_not_found") for index, factory in enumerate(factories)},
        tuple(LessonNotFoundError(code="lesson_not_found") for factory in factories),
    )
"""
    return [
        Case(
            "schema-fresh-clean-concrete-code-annotation-exact",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    exact_concrete_code_annotation,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-fresh-invalid-concrete-code-annotation-broadened",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    broadened_concrete_code_annotation,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-fresh-clean-private-and-benign-model-config-bindings",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    benign_indirect_model_config,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-fresh-invalid-private-model-config-alias-binding",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    indirect_alias_model_config,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-fresh-clean-unrelated-nested-class",
            with_files(
                (
                    "application/lesson/presentation_layer/nested.py",
                    unrelated_nested_class,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-fresh-invalid-nested-concrete-outside-canonical-module",
            with_files(
                (
                    "application/lesson/presentation_layer/nested.py",
                    nested_outside_concrete,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-fresh-clean-unrelated-walrus-object-code",
            with_files(
                (
                    "application/lesson/presentation_layer/controller.py",
                    unrelated_walrus_object,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-fresh-invalid-walrus-bound-error-code",
            with_files(
                (
                    "application/lesson/presentation_layer/controller.py",
                    walrus_bound_error,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-fresh-clean-concrete-name-ending-error-out",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    concrete_name_ending_error_out,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-fresh-invalid-true-second-bc-base",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    true_second_bc_base,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-fresh-clean-shadowed-lambda-and-comprehension-constructors",
            with_files(
                (
                    "application/lesson/presentation_layer/controller.py",
                    shadowed_constructor_expressions,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-fresh-invalid-unshadowed-lambda-and-comprehension-constructors",
            with_files(
                (
                    "application/lesson/presentation_layer/controller.py",
                    unshadowed_constructor_expressions,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case("schema-clean-common-base-and-two-concrete", BASE_FILES, "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-empty-error-bc", common_only, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--project-code-error-module", "common/ninja/response/error_out.py"), 0, ""),
        Case("schema-clean-no-error-bc-in-scope", no_error_bc, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/catalog/presentation_layer/controller.py", "--scope-bc", "catalog", "--project-code-error-module", "common/ninja/response/error_out.py"), 0, ""),
        Case("schema-clean-same-profile-common-enum-reuse-v1", reused_surfaces, "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-same-profile-common-enum-reuse-v2", reused_surfaces, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v2", "--api-module", "config/api_v2.py", "--controller-module", "application/lesson/presentation_layer/controller_v2.py", "--scope-bc", "lesson", "--error-bc", "lesson", "--project-code-error-module", "common/ninja/response/error_out.py", "--project-code-error-module", "application/lesson/presentation_layer/schema/error_out.py"), 0, ""),
        Case("schema-clean-canonical-looking-preserve-excluded", preserve, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "preserve-established", "--scope", "legacy", "--api-module", "legacy/api.py", "--controller-module", "legacy/controller.py", "--scope-bc", "legacy", "--error-bc", "legacy", "--project-code-error-module", "common/ninja/response/error_out.py", "--project-preserve-error-module", "legacy/errors.py"), 0, ""),
        Case(
            "schema-clean-preserve-empty-inventories",
            preserve_empty_inventories,
            "check-error-centralization.py",
            preserve_empty_inventory_args,
            0,
            "",
        ),
        Case(
            "schema-clean-target-only-auto-na",
            with_files(("common/ninja/response/error_out.py", "class Broken(:\n")),
            "check-error-centralization.py",
            (TARGET_DIR,),
            0,
            "",
        ),
        Case(
            "schema-clean-required-import-aliases",
            alias_import_files,
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-dynamic-common-required-field",
            dynamic_required_files,
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-code-profile-preserve-duplicate-excluded",
            code_with_preserve_duplicate,
            "check-error-centralization.py",
            schema_args(
                "--project-preserve-error-module",
                "application/legacy/presentation_layer/schema/error_out.py",
            ),
            0,
            "",
        ),
        Case(
            "schema-clean-unprefixed-wire-code",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    LESSON_ERROR_OUT.replace("lesson_not_found", "not_found").replace(
                        "lesson_conflict",
                        "conflict",
                    ),
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-multiple-concrete-share-one-code",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    shared_code_concretes,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-git-ignored-generated-decoys",
            ignored_generated_files,
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
            baseline_files=ignored_generated_baseline,
        ),
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
        Case(
            "schema-concrete-missing-dynamic-required-default",
            with_files(
                ("common/ninja/response/error_out.py", DYNAMIC_COMMON_ERROR_OUT),
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    missing_dynamic_default,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-common-init-nonempty",
            with_files(
                (
                    "common/ninja/response/__init__.py",
                    "from .error_out import ErrorOut\n",
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-common-helper",
            with_files(
                (
                    "common/ninja/response/error_out.py",
                    COMMON_ERROR_OUT + "\ndef make_error():\n    return ErrorOut\n",
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-common-enum",
            with_files(
                (
                    "common/ninja/response/error_out.py",
                    COMMON_ERROR_OUT
                    + "\nfrom enum import StrEnum\n\n"
                    + "class CommonErrorCode(StrEnum):\n"
                    + '    NOT_FOUND = "not_found"\n',
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-common-duplicate-errorout",
            with_files(
                (
                    "common/ninja/response/error_out.py",
                    COMMON_ERROR_OUT
                    + "\nclass ErrorOut(Schema):\n"
                    + "    code: str\n"
                    + "    title: str\n"
                    + "    status: int\n"
                    + "    detail: str\n",
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-enum-wrong-inheritance",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import Enum").replace(
                        "class LessonErrorCode(StrEnum):",
                        "class LessonErrorCode(Enum):",
                    ),
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-enum-wire-not-snake-case",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    LESSON_ERROR_OUT.replace("lesson_not_found", "Lesson-Not-Found"),
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-project-duplicate-wire-code-within-enum",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    LESSON_ERROR_OUT.replace("lesson_conflict", "lesson_not_found"),
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-base-code-has-default",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    LESSON_ERROR_OUT.replace(
                        "    code: LessonErrorCode\n",
                        "    code: LessonErrorCode = LessonErrorCode.NOT_FOUND\n",
                        1,
                    ),
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-concrete-code-default-from-other-enum",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    foreign_enum_default,
                ),
                (
                    "application/catalog/presentation_layer/schema/error_out.py",
                    VALID_CATALOG_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(
                "--scope-bc",
                "catalog",
                "--error-bc",
                "catalog",
                "--project-code-error-module",
                "application/catalog/presentation_layer/schema/error_out.py",
            ),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-raw-string-code-selected-controller",
            with_files(
                (
                    "application/lesson/presentation_layer/controller.py",
                    raw_string_controller,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-extra-untracked-common-file",
            with_files(
                (
                    "common/ninja/response/helper.py",
                    "def make_error(): pass\n",
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
            baseline_files=BASE_FILES,
        ),
        Case("schema-analysis-syntax", with_files(("application/lesson/presentation_layer/schema/error_out.py", "class Broken(:\n")), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case(
            "schema-analysis-dynamic-enum-value",
            with_files(
                (
                    "application/lesson/presentation_layer/schema/error_out.py",
                    LESSON_ERROR_OUT.replace(
                        'NOT_FOUND = "lesson_not_found"',
                        "NOT_FOUND = make_code()",
                    ),
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            1,
            "사용 오류",
        ),
        Case(
            "schema-analysis-duplicate-inventory-selector",
            BASE_FILES,
            "check-error-centralization.py",
            schema_args(
                "--project-code-error-module",
                "application/lesson/presentation_layer/schema/error_out.py",
            ),
            1,
            "사용 오류",
            allowed_arg_issues=frozenset(
                {"duplicate:--project-code-error-module"}
            ),
        ),
        Case("schema-analysis-root-escape", BASE_FILES, "check-error-centralization.py", schema_args("--project-code-error-module", "../outside.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--project-code-error-module"})),
        Case("schema-analysis-unresolved-base", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("from common.ninja.response.error_out import ErrorOut", "from missing import ErrorOut"))), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-analysis-missing-source", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--project-code-error-module", "application/lesson/presentation_layer/schema/error_out.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--scope", "missing:--api-module", "missing:--controller-module", "missing:--scope-bc"})),
        Case("schema-analysis-missing-inventory", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--project-code-error-module"})),
        Case("schema-analysis-missing-selected-error-module-path", BASE_FILES, "check-error-centralization.py", schema_args("--project-code-error-module", "application/lesson/presentation_layer/schema/missing_error_out.py"), 1, "사용 오류"),
        Case("schema-analysis-error-bc-not-subset", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "catalog", "--error-bc", "lesson", "--project-code-error-module", "common/ninja/response/error_out.py", "--project-code-error-module", "application/lesson/presentation_layer/schema/error_out.py"), 1, "사용 오류"),
        Case("schema-analysis-candidate-absent-from-inventory", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson", "--project-code-error-module", "common/ninja/response/error_out.py"), 1, "사용 오류"),
        Case("schema-analysis-module-in-both-inventories", BASE_FILES, "check-error-centralization.py", schema_args("--project-preserve-error-module", "application/lesson/presentation_layer/schema/error_out.py"), 1, "사용 오류"),
        Case("schema-analysis-auto-profile", BASE_FILES, "check-error-centralization.py", AUTO_PROFILE_ARGS, 0, ""),
        Case("schema-analysis-missing-profile-args", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--error-profile", "missing:--api-module", "missing:--controller-module", "missing:--scope-bc", "missing:--project-code-error-module"})),
        Case("schema-fp-tests-migrations-docstrings-logs", with_files(("application/lesson/tests/test_codes.py", "code = 'lesson_not_found'\n"), ("application/lesson/migrations/0001_initial.py", "code = 'lesson_not_found'\n"), ("application/lesson/presentation_layer/log.py", "import logging\nlogger = logging.getLogger(__name__)\n'''code = lesson_not_found'''\nlogger.info('code=%s', 'lesson_not_found')\n")), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-fp-classvar-private-benign-config-import-alias", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom typing import ClassVar").replace("class LessonErrorOut(ErrorOut):\n    code: LessonErrorCode", "class LessonErrorOut(ErrorOut):\n    model_config = {'populate_by_name': True}\n    _cache: ClassVar[dict] = {}\n    code: LessonErrorCode"))), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-fp-relative-import-local-assignment-ignored-cache", with_files(("application/lesson/presentation_layer/schema/alias.py", "from .error_out import LessonErrorOut as Error\nvalue = Error\n"), (".cache/generated.py", "code = 'ignored'\n"), ("__pycache__/bad.py", "code = 'ignored'\n")), "check-error-centralization.py", schema_args(), 0, ""),
        # Reviewer gap: whether the inventory is semantically complete and whether a
        # public code should exist cannot be inferred from source shape alone.
    ]


def controller_cases() -> list[Case]:
    """Controller shape cases; the checker is intentionally absent at this RED stage."""
    clean_sync_annassign = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "lesson = get_lesson(lesson_id)",
        "lesson: dict = get_lesson(lesson_id)",
    )
    clean_async = (
        CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"]
        .replace("def get_lesson_controller", "async def get_lesson_controller")
        .replace("lesson = get_lesson(lesson_id)", "await get_lesson(lesson_id)")
        .replace("    return lesson\n", "    return {'ok': True}\n")
    )
    clean_tuple = (
        CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"]
        .replace(
            "LessonMissing, get_lesson",
            "LessonMissing, LessonUnavailable, get_lesson",
        )
        .replace("except LessonMissing:", "except (LessonMissing, LessonUnavailable):")
    )
    clean_tuple_use_cases = CONTROLLER_FILES[
        "application/lesson/application_layer/use_cases.py"
    ].replace(
        "\n\ndef get_lesson",
        "\n\nclass LessonUnavailable(Exception):\n    pass\n\n\ndef get_lesson",
    )
    clean_result_none = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonID, get_lesson
from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: LessonNotFoundError})
def get_lesson_controller(request, lesson_id: int):
    result = get_lesson(LessonID(lesson_id))
    if result is None:
        error = LessonNotFoundError()
        return Status(error.status, error)
    return result
"""
    clean_result_none_use_cases = CONTROLLER_FILES[
        "application/lesson/application_layer/use_cases.py"
    ].replace(
        "class LessonMissing(Exception):",
        "class LessonID(int):\n"
        "    pass\n\n\n"
        "class LessonMissing(Exception):",
    )
    empty_error_bc_files = with_files(
        ("application/lesson/presentation_layer/schema/error_out.py", "<REMOVE>"),
    )
    preserve_controller_files = {
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": """from django.http import JsonResponse
from ninja import NinjaAPI

legacy_api = NinjaAPI()


@legacy_api.exception_handler(LookupError)
def legacy_error_handler(request, exc):
    return JsonResponse({"error": "legacy failure"}, status=404)

def legacy_controller(request):
    return JsonResponse({"error": "legacy missing"}, status=404)
""",
    }
    preserve_controller_args = (
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
    direct_base = (
        CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"]
        .replace(
            "LessonNotFoundError()",
            "LessonErrorOut(code=LessonErrorCode.NOT_FOUND, title='missing', "
            "status=404, detail='missing', trace_id='lesson-missing')",
        )
        .replace("404: LessonNotFoundError", "404: LessonErrorOut")
        .replace("from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError", "from application.lesson.presentation_layer.schema.error_out import LessonErrorCode, LessonErrorOut")
    )
    direct_base_extra_field = direct_base.replace(
        "trace_id='lesson-missing')",
        "trace_id='lesson-missing', retryable=False)",
    )
    relative_alias_controller = """from ninja import Router, Status as ApiStatus
from ..application_layer.use_cases import LessonMissing as MissingLesson, get_lesson as load_lesson
from .schema.error_out import LessonNotFoundError as MissingLessonOut

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: MissingLessonOut})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = load_lesson(lesson_id)
    except MissingLesson:
        error = MissingLessonOut()
        return ApiStatus(error.status, error)
    return lesson
"""
    unselected_preserve_handler = """from ninja import NinjaAPI

legacy_api = NinjaAPI()


@legacy_api.exception_handler(LookupError)
def preserve_handler(request, exc):
    return {"legacy": True}
"""
    serializer_controller = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from ninja import Router, Status\nfrom .transport import emit",
    )
    serializer_helper = """from django.http import JsonResponse
from .schema.error_out import LessonErrorOut


def emit(value: LessonErrorOut):
    return JsonResponse(value.model_dump(), status=value.status)
"""
    mapping_controller = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from ninja import Router, Status\nfrom .bridge import convert",
    )
    mapping_helper = """from application.lesson.application_layer.use_cases import LessonMissing
from .schema.error_out import LessonNotFoundError


def convert(value):
    if isinstance(value, LessonMissing):
        return LessonNotFoundError()
    return None
"""
    forwarded_exception = (
        CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"]
        .replace(
            "from ninja import Router, Status",
            "from ninja import Router, Status\nfrom .forwarder import forward_error",
        )
        .replace("except LessonMissing:", "except LessonMissing as exc:")
        .replace(
            "error = LessonNotFoundError()\n        return Status(error.status, error)",
            "return forward_error(exc)",
        )
    )
    multiple_peer_calls = (
        CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"]
        .replace(
            "LessonMissing, get_lesson",
            "LessonMissing, get_lesson, record_access",
        )
        .replace(
            "lesson = get_lesson(lesson_id)",
            "lesson, audit = get_lesson(lesson_id), record_access(lesson_id)",
        )
    )
    multiple_peer_use_cases = CONTROLLER_FILES[
        "application/lesson/application_layer/use_cases.py"
    ] + "\n\ndef record_access(lesson_id: int):\n    return {'lesson_id': lesson_id}\n"
    add_handler_call = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ] + """

def registered_handler(request, exc):
    return None


router.add_exception_handler(LessonMissing, registered_handler)
"""
    bare_catch = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace("except LessonMissing:", "except:")
    tuple_base_exception = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "except LessonMissing:",
        "except (LessonMissing, BaseException):",
    )
    explicit_reraise = (
        CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"]
        .replace("except LessonMissing:", "except LessonMissing as exc:")
        .replace(
            "error = LessonNotFoundError()\n        return Status(error.status, error)",
            "raise exc",
        )
    )
    hardcoded_status = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "return Status(error.status, error)",
        "return Status(404, error)",
    )
    match_status_capture = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "    try:\n",
        "    match lesson_id:\n"
        "        case Status if enabled:\n"
        "            pass\n"
        "    try:\n",
    )
    match_error_out_capture = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "    try:\n",
        "    match values:\n"
        "        case [*LessonNotFoundError] if enabled:\n"
        "            pass\n"
        "    try:\n",
    )
    match_exception_capture = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "    try:\n",
        "    match values:\n"
        "        case {'value': captured, **LessonMissing} if enabled:\n"
        "            pass\n"
        "    try:\n",
    )
    match_unrelated_capture = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "    try:\n",
        "    match values:\n"
        "        case {'value': captured, **rest} if enabled:\n"
        "            pass\n"
        "    try:\n",
    )
    class_body_classvar_common = DYNAMIC_COMMON_ERROR_OUT.replace(
        "class ErrorOut(Schema):\n",
        "class ErrorOut(Schema):\n"
        "    from typing import ClassVar as Metadata\n"
        "    registry: Metadata[dict] = {}\n",
    )
    module_classvar_common = DYNAMIC_COMMON_ERROR_OUT.replace(
        "from ninja import Schema",
        "from ninja import Schema\nfrom typing import ClassVar as Metadata",
    ).replace(
        "class ErrorOut(Schema):\n",
        "class ErrorOut(Schema):\n    registry: Metadata[dict] = {}\n",
    )
    direct_base_passes_classvar = direct_base.replace(
        "trace_id='lesson-missing')",
        "trace_id='lesson-missing', registry={})",
    )
    function_handler_call = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ] + """


def install_handlers():
    router.add_exception_handler(LessonMissing, registered_handler)
"""
    nested_handler_decorator = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ] + """


def install_handlers():
    @router.exception_handler(LessonMissing)
    def registered_handler(request, exc):
        return None
    return registered_handler
"""
    conditional_handler_call = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ] + """


if handlers_enabled:
    router.add_exception_handler(LessonMissing, registered_handler)
"""
    class_method_handler_call = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ] + """


class Installer:
    def install(self):
        router.add_exception_handler(LessonMissing, registered_handler)
"""
    arbitrary_handler_receiver = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ] + """


class Registry:
    def add_exception_handler(self, *args):
        return None


registry = Registry()


def install_handlers():
    registry.add_exception_handler(LessonMissing, registered_handler)
"""
    builtin_isinstance_result = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonNotFoundError})
def get_lesson_controller(request, lesson_id: int):
    result = get_lesson(lesson_id)
    if isinstance(result, LessonMissing):
        error = LessonNotFoundError()
        return Status(error.status, error)
    return result
"""
    shadowed_isinstance_result = builtin_isinstance_result.replace(
        "    result = get_lesson(lesson_id)",
        "    isinstance = custom_predicate\n    result = get_lesson(lesson_id)",
    )
    shadowed_isinstance_helper = mapping_helper.replace(
        "def convert(value):\n    if isinstance(value, LessonMissing):",
        "def convert(value):\n"
        "    isinstance = custom_predicate\n"
        "    if isinstance(value, LessonMissing):",
    )
    forwarded_exception_container = forwarded_exception.replace(
        "return forward_error(exc)",
        "return forward_error({'caught': exc})",
    )
    nested_lambda_exception_reference = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.presentation_layer.schema.error_out import LessonErrorCode, LessonErrorOut

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorOut})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing as exc:
        error = LessonErrorOut(
            code=LessonErrorCode.NOT_FOUND,
            title='missing',
            status=404,
            detail=(lambda: exc),
        )
        return Status(error.status, error)
    return lesson
"""
    temporal_serializer_helper = """from django.http import JsonResponse
from .schema.error_out import LessonErrorCode, LessonErrorOut


def emit(value):
    response = JsonResponse(value.model_dump(), status=200)
    value = LessonErrorOut(
        code=LessonErrorCode.NOT_FOUND,
        title='missing',
        status=404,
        detail='missing',
    )
    return response
"""
    temporal_serializer_controller = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError
from application.lesson.presentation_layer.transport import emit

router = Router()


@router.get('/{lesson_id}', response={404: LessonNotFoundError})
def get_lesson_controller(request, lesson_id: int):
    value = get_lesson(lesson_id)
    emit(value)
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        value = LessonNotFoundError()
        return Status(value.status, value)
    return lesson
"""
    selected_nested_helper_controller = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from ninja import Router, Status\nfrom .assembler import assemble",
    )
    nested_prepared_factory = """from .schema.error_out import LessonNotFoundError


def assemble():
    def build():
        return LessonNotFoundError()
    return build()
"""
    nested_factory_control = """def assemble():
    def build():
        return {'ok': True}
    return build()
"""
    raw_dict_error_status = """from ninja import Router, Status

router = Router()


@router.get('/raw', response={200: dict})
def raw_error(request):
    return Status(404, {'code': 'lesson_not_found'})
"""
    raw_name_error_status = """from ninja import Router, Status

router = Router()


@router.get('/raw', response={200: dict})
def raw_error(request):
    payload = {'code': 'lesson_unavailable'}
    return Status(503, payload)
"""
    success_status = """from ninja import Router, Status

router = Router()


@router.get('/raw', response={200: dict})
def raw_success(request):
    return Status(200, {'ok': True})
"""
    branch_router_handler = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ] + """


def registered_handler(request, exc):
    return None


if True:
    branch_router = Router()
branch_router.add_exception_handler(LessonMissing, registered_handler)
"""
    ambiguous_branch_handler = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ] + """


def registered_handler(request, exc):
    return None


if handlers_enabled:
    selected_receiver = Router()
selected_receiver.add_exception_handler(LessonMissing, registered_handler)
"""
    arbitrary_branch_handler = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ] + """


class Registry:
    def add_exception_handler(self, *args):
        return None


if True:
    ordinary_receiver = Registry()
ordinary_receiver.add_exception_handler(LessonMissing, registered_handler)
"""
    module_shadowed_isinstance_result = builtin_isinstance_result.replace(
        "router = Router()",
        "router = Router()\nisinstance = lambda *args: True",
    )
    lambda_default_forwarding = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.presentation_layer.schema.error_out import LessonErrorCode, LessonErrorOut
from application.lesson.presentation_layer.forwarder import forward_error

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorOut})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing as exc:
        error = LessonErrorOut(
            code=LessonErrorCode.NOT_FOUND,
            title=(lambda hidden=forward_error(exc): hidden)(),
            status=404,
            detail='missing',
        )
        return Status(error.status, error)
    return lesson
"""
    lambda_keyword_default_forwarding = lambda_default_forwarding.replace(
        "lambda hidden=forward_error(exc): hidden",
        "lambda *, hidden=forward_error(exc): hidden",
    )
    lambda_body_forwarding_control = lambda_default_forwarding.replace(
        "title=(lambda hidden=forward_error(exc): hidden)(),",
        "title='missing',\n            detail=lambda: forward_error(exc),",
    ).replace("            detail='missing',\n", "", 1)
    lambda_nonforwarding_default_control = lambda_default_forwarding.replace(
        "forward_error(exc)",
        "forward_error('safe')",
    )
    conditional_error_serializer = """from django.http import JsonResponse
from .schema.error_out import LessonNotFoundError


def maybe_emit(value: LessonNotFoundError, success, use_success: bool):
    if use_success:
        value = success
    return JsonResponse(value.model_dump(), status=200)
"""
    proven_success_serializer = conditional_error_serializer.replace(
        "    if use_success:\n        value = success\n",
        "    if use_success:\n        value = success\n    else:\n        value = success\n",
    )
    literal_true_success_serializer = conditional_error_serializer.replace(
        "if use_success:", "if True:"
    )
    literal_false_error_serializer = conditional_error_serializer.replace(
        "if use_success:", "if False:"
    )
    selected_serializer_controller = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from ninja import Router, Status\nfrom .transport import maybe_emit",
    )
    operation_nested_factory = CONTROLLER_FILES[
        "application/lesson/presentation_layer/controller.py"
    ].replace(
        "    try:\n",
        "    def make_error():\n"
        "        return LessonNotFoundError()\n\n"
        "    try:\n",
    )
    operation_nested_benign = operation_nested_factory.replace(
        "        return LessonNotFoundError()",
        "        return None",
    )
    local_class_factory = """from .schema.error_out import LessonNotFoundError


def assemble():
    class LocalFactory:
        def make(self):
            return LessonNotFoundError()
    return LocalFactory
"""
    local_class_benign = local_class_factory.replace(
        "            return LessonNotFoundError()",
        "            return None",
    )
    return [
        Case("controller-clean-sync-narrow-try", with_files(("application/lesson/presentation_layer/controller.py", clean_sync_annassign), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-async-narrow-try", with_files(("application/lesson/presentation_layer/controller.py", clean_async), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-tuple-catch-prepared-concrete", with_files(("application/lesson/presentation_layer/controller.py", clean_tuple), ("application/lesson/application_layer/use_cases.py", clean_tuple_use_cases), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-event-specific-base", with_files(("common/ninja/response/error_out.py", DYNAMIC_COMMON_ERROR_OUT), ("application/lesson/presentation_layer/schema/error_out.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/presentation_layer/controller.py", direct_base), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-result-none-prepared-errorout-status", with_files(("application/lesson/presentation_layer/controller.py", clean_result_none), ("application/lesson/application_layer/use_cases.py", clean_result_none_use_cases), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-approved-retry-after", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from django.http import HttpResponse\nfrom ninja import Router, Status").replace("def get_lesson_controller(request, lesson_id: int):", "def get_lesson_controller(request, response: HttpResponse, lesson_id: int):").replace("        return Status(error.status, error)", "        response['Retry-After'] = '1'\n        return Status(error.status, error)")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-relative-as-import-provenance", with_files(("application/lesson/presentation_layer/controller.py", relative_alias_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-unselected-preserve-handler", with_files(("application/lesson/presentation_layer/preserve_controller.py", "def preserve_controller(request): return {'legacy': True}\n"), ("application/lesson/presentation_layer/preserve_handler.py", unselected_preserve_handler), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-empty-error-bc", empty_error_bc_files, "check-api-error-controller-contract.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson"), 0, ""),
        Case("controller-clean-preserve-profile-na", preserve_controller_files, "check-api-error-controller-contract.py", preserve_controller_args, 0, ""),
        Case("controller-direct-presentation-helper", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .assembler import assemble").replace("error = LessonNotFoundError()", "error = assemble()")), ("application/lesson/presentation_layer/assembler.py", "from .schema.error_out import LessonNotFoundError\ndef assemble(): return LessonNotFoundError()\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-direct-one-hop-serializer-helper", with_files(("application/lesson/presentation_layer/controller.py", serializer_controller), ("application/lesson/presentation_layer/transport.py", serializer_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-direct-one-hop-mapping-helper", with_files(("application/lesson/presentation_layer/controller.py", mapping_controller), ("application/lesson/presentation_layer/bridge.py", mapping_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-registered-handler", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"] + "\n@router.exception_handler(LessonMissing)\ndef handler(request, exc): pass\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-add-exception-handler-call", with_files(("application/lesson/presentation_layer/controller.py", add_handler_call), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-wide-try", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("try:\n        lesson =", "try:\n        prepared = lesson_id\n        lesson =")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-multiple-peer-outer-calls-one-statement", with_files(("application/lesson/presentation_layer/controller.py", multiple_peer_calls), ("application/lesson/application_layer/use_cases.py", multiple_peer_use_cases), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-success-transform-inside-try", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("lesson = get_lesson(lesson_id)", "lesson = get_lesson(lesson_id)\n        return {'lesson': lesson}")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-broad-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("except LessonMissing:", "except Exception:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-bare-catch", with_files(("application/lesson/presentation_layer/controller.py", bare_catch), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-tuple-catch-includes-base-exception", with_files(("application/lesson/presentation_layer/controller.py", tuple_base_exception), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-framework-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom ninja.errors import HttpError").replace("except LessonMissing:", "except HttpError:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-raw-infra-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from django.db import DatabaseError as StorageFailure\nfrom ninja import Router, Status").replace("except LessonMissing:", "except StorageFailure:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-immediate-raise-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("    try:\n        lesson = get_lesson(lesson_id)", "    lesson = None\n    try:\n        raise LessonMissing()")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-reraises", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("error = LessonNotFoundError()\n        return Status(error.status, error)", "raise")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-explicit-reraise", with_files(("application/lesson/presentation_layer/controller.py", explicit_reraise), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-raises-http-error", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom ninja.errors import HttpError").replace("error = LessonNotFoundError()\n        return Status(error.status, error)", "raise HttpError(404, 'missing')")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-forwards-exception", with_files(("application/lesson/presentation_layer/controller.py", forwarded_exception), ("application/lesson/presentation_layer/forwarder.py", "def forward_error(exc): return exc\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-no-direct-status", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return Status(error.status, error)", "return error")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-status-does-not-use-body-status", with_files(("application/lesson/presentation_layer/controller.py", hardcoded_status), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-concrete-called-with-args", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("LessonNotFoundError()", "LessonNotFoundError(detail='missing')")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-base-extra-constructor-field", with_files(("common/ninja/response/error_out.py", DYNAMIC_COMMON_ERROR_OUT), ("application/lesson/presentation_layer/schema/error_out.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/presentation_layer/controller.py", direct_base_extra_field), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-error-tuple-raw-response-dict", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return Status(error.status, error)", "return 404, {'code': 'lesson_not_found'}")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-error-raw-response", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom ninja.responses import Response").replace("return Status(error.status, error)", "return Response({'code': 'lesson_not_found'}, status=404)")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-analysis-unresolved-status-reexport", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from .exports import Status\nfrom ninja import Router")), ("application/lesson/presentation_layer/exports.py", "from ninja import Status\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-unresolved-error-out-reexport", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError", "from .exports import LessonNotFoundError")), ("application/lesson/presentation_layer/exports.py", "from .schema.error_out import LessonNotFoundError\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-selected-syntax", with_files(("application/lesson/presentation_layer/controller.py", "def broken(:\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-one-hop-syntax", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .factory import make_error")), ("application/lesson/presentation_layer/factory.py", "def broken(:\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-missing-selected-controller-path", CONTROLLER_FILES, "check-api-error-controller-contract.py", controller_args("--controller-module", "application/lesson/presentation_layer/missing_controller.py"), 1, "사용 오류"),
        Case("controller-analysis-selected-root-escape", CONTROLLER_FILES, "check-api-error-controller-contract.py", controller_args("--controller-module", "../outside.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--controller-module"})),
        Case("controller-analysis-duplicate-controller-selector", CONTROLLER_FILES, "check-api-error-controller-contract.py", controller_args("--controller-module", "application/lesson/presentation_layer/controller.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"duplicate:--controller-module"})),
        Case("controller-analysis-auto-profile", CONTROLLER_FILES, "check-api-error-controller-contract.py", AUTO_PROFILE_ARGS, 0, ""),
        Case("controller-analysis-missing-args", CONTROLLER_FILES, "check-api-error-controller-contract.py", (TARGET_DIR, "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--error-profile", "missing:--api-module", "missing:--controller-module", "missing:--scope-bc"})),
        Case("controller-analysis-matchas-status-capture", with_files(("application/lesson/presentation_layer/controller.py", match_status_capture), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-matchstar-errorout-capture", with_files(("application/lesson/presentation_layer/controller.py", match_error_out_capture), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-matchmapping-exception-capture", with_files(("application/lesson/presentation_layer/controller.py", match_exception_capture), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case(
            "controller-clean-match-unrelated-capture",
            with_files(
                (
                    "application/lesson/presentation_layer/controller.py",
                    match_unrelated_capture,
                ),
                base=CONTROLLER_FILES,
            ),
            "check-api-error-controller-contract.py",
            controller_args(),
            0 if sys.version_info >= (3, 10) else 1,
            "" if sys.version_info >= (3, 10) else "사용 오류",
        ),
        Case("controller-clean-class-body-classvar-alias-five-fields", with_files(("common/ninja/response/error_out.py", class_body_classvar_common), ("application/lesson/presentation_layer/schema/error_out.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/presentation_layer/controller.py", direct_base), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-class-body-classvar-cannot-be-passed", with_files(("common/ninja/response/error_out.py", class_body_classvar_common), ("application/lesson/presentation_layer/schema/error_out.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/presentation_layer/controller.py", direct_base_passes_classvar), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-module-classvar-alias-control", with_files(("common/ninja/response/error_out.py", module_classvar_common), ("application/lesson/presentation_layer/schema/error_out.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/presentation_layer/controller.py", direct_base), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-function-add-exception-handler-call", with_files(("application/lesson/presentation_layer/controller.py", function_handler_call), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-nested-exception-handler-decorator", with_files(("application/lesson/presentation_layer/controller.py", nested_handler_decorator), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-module-if-add-exception-handler-call", with_files(("application/lesson/presentation_layer/controller.py", conditional_handler_call), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-class-method-add-exception-handler-call", with_files(("application/lesson/presentation_layer/controller.py", class_method_handler_call), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-arbitrary-nested-handler-receiver", with_files(("application/lesson/presentation_layer/controller.py", arbitrary_handler_receiver), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-analysis-shadowed-isinstance-result-predicate", with_files(("application/lesson/presentation_layer/controller.py", shadowed_isinstance_result), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-clean-builtin-isinstance-result-predicate", with_files(("application/lesson/presentation_layer/controller.py", builtin_isinstance_result), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-analysis-shadowed-isinstance-helper-predicate", with_files(("application/lesson/presentation_layer/controller.py", mapping_controller), ("application/lesson/presentation_layer/bridge.py", shadowed_isinstance_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-caught-exception-forwarded-in-container", with_files(("application/lesson/presentation_layer/controller.py", forwarded_exception_container), ("application/lesson/presentation_layer/forwarder.py", "def forward_error(exc): return exc\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "caught exception forwarding forbidden"),
        Case("controller-clean-caught-exception-nested-lambda-scope", with_files(("application/lesson/presentation_layer/controller.py", nested_lambda_exception_reference), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-serializer-before-later-errorout-assignment", with_files(("application/lesson/presentation_layer/controller.py", temporal_serializer_controller), ("application/lesson/presentation_layer/transport.py", temporal_serializer_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-one-hop-nested-prepared-factory", with_files(("application/lesson/presentation_layer/controller.py", selected_nested_helper_controller), ("application/lesson/presentation_layer/assembler.py", nested_prepared_factory), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "prepared ErrorOut factory/helper forbidden"),
        Case("controller-clean-one-hop-nested-helper-without-errorout", with_files(("application/lesson/presentation_layer/controller.py", selected_nested_helper_controller), ("application/lesson/presentation_layer/assembler.py", nested_factory_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-direct-raw-dict-error-status-outside-arm", with_files(("application/lesson/presentation_layer/controller.py", raw_dict_error_status), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-direct-raw-name-error-status-outside-arm", with_files(("application/lesson/presentation_layer/controller.py", raw_name_error_status), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-direct-success-status", with_files(("application/lesson/presentation_layer/controller.py", success_status), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-branch-created-router-handler", with_files(("application/lesson/presentation_layer/controller.py", branch_router_handler), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "custom Ninja add_exception_handler forbidden"),
        Case("controller-fresh-analysis-ambiguous-branch-handler-receiver", with_files(("application/lesson/presentation_layer/controller.py", ambiguous_branch_handler), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-fresh-clean-arbitrary-branch-handler-receiver", with_files(("application/lesson/presentation_layer/controller.py", arbitrary_branch_handler), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-analysis-module-shadowed-isinstance-predicate", with_files(("application/lesson/presentation_layer/controller.py", module_shadowed_isinstance_result), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-fresh-clean-true-builtin-isinstance-predicate", with_files(("application/lesson/presentation_layer/controller.py", builtin_isinstance_result), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-caught-exception-forwarded-in-lambda-default", with_files(("application/lesson/presentation_layer/controller.py", lambda_default_forwarding), ("application/lesson/presentation_layer/forwarder.py", "def forward_error(value): return value\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "caught exception forwarding forbidden"),
        Case("controller-fresh-caught-exception-forwarded-in-lambda-keyword-default", with_files(("application/lesson/presentation_layer/controller.py", lambda_keyword_default_forwarding), ("application/lesson/presentation_layer/forwarder.py", "def forward_error(value): return value\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "caught exception forwarding forbidden"),
        Case("controller-fresh-clean-caught-exception-in-lambda-body-scope", with_files(("application/lesson/presentation_layer/controller.py", lambda_body_forwarding_control), ("application/lesson/presentation_layer/forwarder.py", "def forward_error(value): return value\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-clean-nonforwarding-lambda-default", with_files(("application/lesson/presentation_layer/controller.py", lambda_nonforwarding_default_control), ("application/lesson/presentation_layer/forwarder.py", "def forward_error(value): return value\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-conditional-errorout-raw-serializer", with_files(("application/lesson/presentation_layer/controller.py", selected_serializer_controller), ("application/lesson/presentation_layer/transport.py", conditional_error_serializer), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "ErrorOut raw HTTP serializer helper forbidden"),
        Case("controller-fresh-clean-all-paths-success-serializer", with_files(("application/lesson/presentation_layer/controller.py", selected_serializer_controller), ("application/lesson/presentation_layer/transport.py", proven_success_serializer), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-literal-true-success-serializer", with_files(("application/lesson/presentation_layer/controller.py", selected_serializer_controller), ("application/lesson/presentation_layer/transport.py", literal_true_success_serializer), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-literal-false-errorout-serializer", with_files(("application/lesson/presentation_layer/controller.py", selected_serializer_controller), ("application/lesson/presentation_layer/transport.py", literal_false_error_serializer), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "ErrorOut raw HTTP serializer helper forbidden"),
        Case("controller-fresh-operation-nested-prepared-factory", with_files(("application/lesson/presentation_layer/controller.py", operation_nested_factory), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "prepared ErrorOut factory/helper forbidden"),
        Case("controller-fresh-clean-operation-nested-benign-helper", with_files(("application/lesson/presentation_layer/controller.py", operation_nested_benign), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-local-class-method-prepared-factory", with_files(("application/lesson/presentation_layer/controller.py", selected_nested_helper_controller), ("application/lesson/presentation_layer/assembler.py", local_class_factory), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "prepared ErrorOut factory/helper forbidden"),
        Case("controller-fresh-clean-local-class-method-benign-helper", with_files(("application/lesson/presentation_layer/controller.py", selected_nested_helper_controller), ("application/lesson/presentation_layer/assembler.py", local_class_benign), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
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
    legacy_http_error = """from ninja import HttpError

def load_lesson():
    raise HttpError(404, "missing")
"""
    legacy_http_import_only = """from django.http import JsonResponse
from ninja import Status


def load_lesson():
    return None
"""
    legacy_raw_http_response = """from django.http import JsonResponse


def load_lesson():
    return JsonResponse({"error": "missing"})
"""
    legacy_http_error_status = """from django.http import JsonResponse as NativeJsonResponse


def load_lesson():
    return NativeJsonResponse({"error": "missing"}, status=404)
"""
    legacy_django_http_import_only = """from django.http import JsonResponse


def load_lesson():
    return None
"""
    legacy_raw_status_only = """def load_lesson():
    status = 404
    return status
"""
    malformed_legacy_raw_status = """def load_lesson(:
    status = 404
"""
    clean_legacy = "def load_lesson(): return None\n"
    tracked_s1_files = with_files(
        (
            "application/lesson/domain_layer/service.py",
            "from application.catalog.infra_layer.repository import CatalogRepository\n",
        ),
        (
            "application/catalog/infra_layer/repository.py",
            "class CatalogRepository: pass\n",
        ),
        base=CONTEXT_FILES,
    )
    preserve_tracked_s1_files = {
        **tracked_s1_files,
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": "def legacy(request): return {'legacy': True}\n",
    }
    code_touched_status_files = with_files(
        (
            "application/lesson/application_layer/use_case.py",
            legacy_raw_status_only,
        ),
        base=CONTEXT_FILES,
    )
    code_touched_status_baseline = with_files(
        (
            "application/lesson/application_layer/use_case.py",
            clean_legacy,
        ),
        base=CONTEXT_FILES,
    )
    cross_bc_error_import_files = with_files(
        (
            "application/lesson/presentation_layer/controller.py",
            "from application.catalog.presentation_layer.schema.error_out "
            "import CatalogErrorCode, CatalogErrorOut\n\n"
            "def get_lesson(request):\n"
            "    return {'id': 1}\n",
        ),
        (
            "application/catalog/presentation_layer/schema/error_out.py",
            CATALOG_DUPLICATE_ERROR_OUT,
        ),
        base=CONTEXT_FILES,
    )
    preserve_django_import_files = {
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": "pass\n",
        "application/legacy/application_layer/use_case.py": legacy_django_http_import_only,
    }
    preserve_django_import_baseline = {
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": "pass\n",
        "application/legacy/application_layer/use_case.py": clean_legacy,
    }
    preserve_malformed_files = {
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": "pass\n",
        "application/legacy/application_layer/use_case.py": malformed_legacy_raw_status,
    }
    preserve_malformed_baseline = {
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": "pass\n",
        "application/legacy/application_layer/use_case.py": clean_legacy,
    }
    empty_error_bc_files = with_files(
        (
            "application/lesson/presentation_layer/controller.py",
            "def get_lesson(request): return {'id': 1}\n",
        ),
        ("application/lesson/presentation_layer/schema/error_out.py", "<REMOVE>"),
        base=CONTEXT_FILES,
    )
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
        Case("context-clean-empty-error-bc", empty_error_bc_files, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson"), 0, ""),
        Case("context-preserve-unchanged-tracked-s1-grandfathered", preserve_tracked_s1_files, "check-context-isolation.py", preserve_args, 0, "", baseline_files=preserve_tracked_s1_files),
        Case("context-preserve-touched-django-http-import-only-clean", preserve_django_import_files, "check-context-isolation.py", preserve_args, 0, "", baseline_files=preserve_django_import_baseline),
        Case("context-clean-root-path-business-size", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef route_limits(request):\n    if request.path.startswith('/limits'):\n        return {'page_size': 500}\n    return {'page_size': 100}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-path-postal-code", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef route_address(request):\n    if request.path.startswith('/addresses'):\n        return {'postal_code': '12345'}\n    return {'postal_code': '00000'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-error-named-metric-helper", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef calculate_error_rate(samples):\n    return {'code': 'sample_limit'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-error-named-metric-argument", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef summarize(error_rate: float):\n    return {'code': 'sample_limit'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-exception-arg-business-payload", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef summarize(exc):\n    return {'sample_size': 500}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-path-nested-return-scope", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef route_docs(request):\n    if request.path.startswith('/docs'):\n        def default_status():\n            return 404\n        return {'ok': True}\n    return {'ok': False}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-imports-bc", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\nfrom application.lesson.infra_layer.repository import LessonRepository\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "root API"),
        Case("context-root-api-local-global-error-code", with_files(("config/api.py", "from enum import StrEnum\nfrom ninja_extra import NinjaExtraAPI\nclass GlobalErrorCode(StrEnum):\n    BAD = 'bad'\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-root-api-local-error-out", with_files(("config/api.py", "from ninja import Schema\nfrom ninja_extra import NinjaExtraAPI\nclass ProblemPayload(Schema):\n    code: str\n    status: int\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "root API"),
        Case("context-root-api-local-error-catalog", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\nPROBLEM_CATALOG: dict = {}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "root API"),
        Case("context-root-api-local-exception-mapping", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef choose(exc):\n    return 404, {'code': 'lesson_not_found'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "root API"),
        Case("context-root-api-path-specific-error-branch", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef handle(request):\n    if request.path.startswith('/lessons'):\n        return {'ok': True}\n    else:\n        return 404, {'code': 'lesson_not_found'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "root API"),
        Case("context-root-api-custom-exception-handler", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\n\napi = NinjaExtraAPI()\n\n\n@api.exception_handler(LookupError)\ndef handle_lookup(request, exc):\n    return None\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-domain-imports-ninja", with_files(("application/lesson/domain_layer/model.py", "import ninja\nclass Lesson: pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "layer purity"),
        Case("context-application-imports-django-http", with_files(("application/lesson/application_layer/use_case.py", "from django.http import JsonResponse\ndef run(): return None\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-infra-imports-common-error-out", with_files(("application/lesson/infra_layer/repository.py", "from common.ninja.response.error_out import ErrorOut\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-application-imports-own-bc-error-out", with_files(("application/lesson/application_layer/use_case.py", "from application.lesson.presentation_layer.schema.error_out import LessonErrorOut\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-layer-imports-other-bc-error-code", with_files(("application/lesson/application_layer/use_case.py", "from application.catalog.presentation_layer.schema.error_out import CatalogErrorCode\n"), ("application/catalog/presentation_layer/schema/error_out.py", CATALOG_DUPLICATE_ERROR_OUT), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "BLOCKER"),
        Case("context-layer-imports-other-bc-error-out", with_files(("application/lesson/infra_layer/repository.py", "from application.catalog.presentation_layer.schema.error_out import CatalogErrorOut\n"), ("application/catalog/presentation_layer/schema/error_out.py", CATALOG_DUPLICATE_ERROR_OUT), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "BLOCKER"),
        Case("context-selected-controller-imports-other-bc-error-language", cross_bc_error_import_files, "check-context-isolation.py", context_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "BLOCKER"),
        Case("context-cross-bc-exception-outside-acl", with_files(("application/lesson/presentation_layer/controller.py", "from application.catalog.domain_layer.exceptions import CatalogMissing\n"), ("application/catalog/domain_layer/exceptions.py", "class CatalogMissing(Exception): pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "BLOCKER"),
        Case("context-existing-s1-cross-bc-internal", with_files(("application/lesson/domain_layer/service.py", "from application.catalog.infra_layer.repository import CatalogRepository\n"), ("application/catalog/infra_layer/repository.py", "class CatalogRepository: pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "BLOCKER"),
        Case("context-code-unchanged-tracked-s1-blocked", tracked_s1_files, "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "BLOCKER", baseline_files=tracked_s1_files),
        Case("context-existing-s2-contract-layer-import", with_files(("application/lesson/published_service/public/contract/query.py", "from application.lesson.domain_layer.model import Lesson\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-existing-s3-own-published-import", with_files(("application/lesson/application_layer/use_case.py", "from application.lesson.published_service.public.contract.query import LessonQuery\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "BLOCKER"),
        Case("context-code-touched-application-http-status-signal", code_touched_status_files, "check-context-isolation.py", context_args(), 2, "BLOCKER", baseline_files=code_touched_status_baseline),
        Case("context-preserve-untouched-application-http-grandfathered", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error}, "check-context-isolation.py", preserve_args, 0, "", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error}),
        Case("context-preserve-touched-application-http-error-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error}, "check-context-isolation.py", preserve_args, 2, "BLOCKER", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": clean_legacy}),
        Case("context-preserve-touched-application-http-import-only-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_import_only}, "check-context-isolation.py", preserve_args, 2, "BLOCKER", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": clean_legacy}),
        Case("context-preserve-touched-application-raw-http-response-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_raw_http_response}, "check-context-isolation.py", preserve_args, 2, "BLOCKER", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": clean_legacy}),
        Case("context-preserve-touched-application-http-status-keyword-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error_status}, "check-context-isolation.py", preserve_args, 2, "BLOCKER", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": clean_legacy}),
        Case("context-preserve-untracked-application-http-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error}, "check-context-isolation.py", preserve_args, 2, "BLOCKER", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n"}),
        Case("context-preserve-http-signal-without-application-container", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "legacy/application_layer/use_case.py": legacy_raw_status_only}, "check-context-isolation.py", preserve_args, 2, "BLOCKER"),
        Case("context-preserve-malformed-python-raw-http-signal", preserve_malformed_files, "check-context-isolation.py", preserve_args, 2, "BLOCKER", baseline_files=preserve_malformed_baseline),
        Case("context-analysis-multiple-api-instances", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\npublic_api = NinjaExtraAPI()\ninternal_api = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 1, "사용 오류"),
        Case("context-analysis-shadowed-api-constructor", with_files(("config/api.py", "from ninja import NinjaAPI\ndef NinjaAPI():\n    return object()\napi = NinjaAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 1, "사용 오류"),
        Case("context-analysis-conditionally-shadowed-api-constructor", with_files(("config/api.py", "from ninja import NinjaAPI\n\nif USE_FAKE_API:\n    NinjaAPI = object\n\napi = NinjaAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 1, "사용 오류"),
        Case("context-analysis-api-controller-overlap", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "config/api.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"overlap:--api-module/--controller-module"})),
        Case("context-analysis-selected-api-syntax", with_files(("config/api.py", "api = (\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 1, "사용 오류"),
        Case("context-analysis-selected-controller-read", CONTEXT_FILES, "check-context-isolation.py", context_args("--controller-module", "application/lesson/presentation_layer/missing.py"), 1, "사용 오류"),
        Case("context-analysis-selected-root-escape", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "../outside.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--api-module"})),
        Case("context-analysis-incomplete-code-source-args", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--api-module", "missing:--controller-module", "missing:--scope-bc"})),
        Case("context-analysis-missing-scope-bc-production-tree", CONTEXT_FILES, "check-context-isolation.py", context_args("--scope-bc", "catalog"), 1, "사용 오류"),
        Case("context-clean-auto-profile-legacy-rules", CONTEXT_FILES, "check-context-isolation.py", AUTO_PROFILE_ARGS, 0, ""),
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
    preserve_common_args = (
        TARGET_DIR,
        "--error-profile",
        "preserve-established",
        "--scope",
        "legacy-v1",
        "--api-module",
        "legacy/api.py",
    )
    auto_selector_args = AUTO_PROFILE_ARGS
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
        Case("composition-registrar-rebinds-api-parameter", with_files(("application/lesson/presentation_layer/registrar.py", "from .controller import LessonController\n\ndef register_lesson_api(api):\n    api = replacement_api\n    api.register_controllers(LessonController)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registrar-handler-sees-rebound-api-parameter", with_files(("application/lesson/presentation_layer/registrar.py", "from .controller import LessonController\n\ndef register_lesson_api(api):\n    try:\n        api = replacement_api\n        raise RuntimeError\n    except RuntimeError:\n        api.register_controllers(LessonController)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registrar-imports-project-api", with_files(("application/lesson/presentation_layer/registrar.py", registrar_imports_api), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registrar-module-top-level-register-controllers", with_files(("application/lesson/presentation_layer/registrar.py", top_level_registration), ("application/lesson/presentation_layer/registration_probe.py", "class RegistrationProbe:\n    def register_controllers(self, controller): pass\n\n\nregistration_probe = RegistrationProbe()\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-urlconf-omits-registrar-call", with_files(("config/urls.py", REGISTRAR_FILES["config/urls.py"].replace("register_catalog_api(api)\n", "")), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-urlconf-duplicates-registrar-call", with_files(("config/urls.py", REGISTRAR_FILES["config/urls.py"] + "register_lesson_api(api)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registration-occurs-outside-registrar", with_files(("config/urls.py", REGISTRAR_FILES["config/urls.py"] + "api.register_controllers(object)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-code-v1-di-still-blocked", {**REGISTRAR_FILES, "application/lesson/composition/provider.py": "def provide(): return object()\n"}, "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-code-v2-di-still-blocked", {**REGISTRAR_FILES, "application/lesson/infra_layer/composition_root.py": "def build(): return object()\n"}, "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-code-v3-di-still-blocked", {**REGISTRAR_FILES, "application/lesson/application_layer/use_case.py": "def run(): return None\n"}, "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-preserve-common-selectors-registrar-na", inactive_registrar_files, "check-composition-root.py", preserve_common_args, 0, ""),
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
    empty_error_bc_files = with_files(
        (
            "application/lesson/presentation_layer/controller.py",
            """from ninja import Router

router = Router()


@router.get("/{lesson_id}", response={200: dict})
def get_lesson(request, lesson_id: int):
    return {"id": lesson_id}
""",
        ),
        ("application/lesson/presentation_layer/schema/error_out.py", "<REMOVE>"),
        base=OPENAPI_FILES,
    )
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

    def flow_controller(body: str, response: str = "{200: dict}") -> str:
        indented = "\n".join(
            f"    {line}" if line else "" for line in body.splitlines()
        )
        return (
            "from ninja import Router, Status\n"
            "from application.lesson.presentation_layer.schema.error_out import "
            "LessonErrorOut, LessonNotFoundError\n\n"
            "router = Router()\n\n"
            f"@router.get('/{{lesson_id}}', response={response})\n"
            "def get_lesson(request, lesson_id: int):\n"
            f"{indented}\n"
        )

    match_body = """match lesson_id:
    case _:
        error = LessonNotFoundError()
        return Status(error.status, error)"""
    trystar_body = """try:
    error = LessonNotFoundError()
    return Status(error.status, error)
except* Exception:
    raise"""
    if_join_body = """if lesson_id:
    error = LessonNotFoundError()
else:
    error = LessonNotFoundError()
return Status(error.status, error)"""
    with_join_body = """with request_scope():
    error = LessonNotFoundError()
return Status(error.status, error)"""
    try_join_body = """try:
    error = LessonNotFoundError()
except LookupError:
    error = LessonNotFoundError()
return Status(error.status, error)"""
    alias_body = """error = LessonNotFoundError()
alias = error
return Status(alias.status, alias)"""
    ambiguous_join_body = """if lesson_id:
    error = LessonNotFoundError()
else:
    error = None
return Status(error.status, error)"""
    module_match_controller = """from ninja import Router, Status
from application.lesson.presentation_layer.schema.error_out import LessonErrorOut, LessonNotFoundError

router = Router()

match 1:
    case 1:
        @router.get('/{lesson_id}', response={200: dict})
        def get_lesson(request, lesson_id: int):
            error = LessonNotFoundError()
            return Status(error.status, error)
"""

    no_direct_common = """from ninja import Router
from common.ninja.response.error_out import ErrorOut

router = Router()

@router.get('/lessons', response={200: dict, 401: ErrorOut})
def list_lessons(request):
    return []
"""
    no_direct_concrete = """from ninja import Router
from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError

router = Router()

@router.get('/lessons', response={200: dict, 401: LessonNotFoundError})
def list_lessons(request):
    return []
"""
    no_direct_base = no_direct_concrete.replace(
        "LessonNotFoundError", "LessonErrorOut"
    )
    no_direct_dict = """from ninja import Router

router = Router()

@router.get('/lessons', response={200: dict, 401: dict})
def list_lessons(request):
    return []
"""
    no_direct_framework_schema = """from ninja import Router
from ninja.errors import AuthenticationError

router = Router()

@router.get('/lessons', response={200: dict, 401: AuthenticationError})
def list_lessons(request):
    return []
"""
    empty_error_bc_args = (
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
    )

    selected_method_alias = """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
schema_builder = api.get_openapi_schema
schema_builder()
"""
    selected_setattr = """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
setattr(api, 'get_openapi_schema', replacement)
"""
    arbitrary_receiver = """from ninja_extra import NinjaExtraAPI
from vendor import external_api

api = NinjaExtraAPI()
external_api.get_openapi_schema()
"""
    arbitrary_setattr = """from ninja_extra import NinjaExtraAPI
from vendor import external_api

api = NinjaExtraAPI()
setattr(external_api, 'get_openapi_schema', replacement)
"""
    arbitrary_class = """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()

class DocumentationCache:
    def get_openapi_schema(self):
        return {}
"""
    ambiguous_selected_alias = """from ninja_extra import NinjaExtraAPI
from vendor import external_api

api = NinjaExtraAPI()
alias = api
if enabled:
    alias = external_api
alias.get_openapi_schema()
"""
    match_rebound_alias = """from ninja_extra import NinjaExtraAPI
from vendor import external_api

api = NinjaExtraAPI()
alias = api
match 1:
    case 1:
        alias = external_api
alias.get_openapi_schema()
"""
    trystar_rebound_alias = """from ninja_extra import NinjaExtraAPI
from vendor import external_api

api = NinjaExtraAPI()
alias = api
try:
    alias = external_api
except* Exception:
    alias = external_api
alias.get_openapi_schema()
"""
    selected_controller_call = """from ninja import Router
from config.api import api

router = Router()
api.get_openapi_schema()

@router.get('/lessons', response={200: dict})
def list_lessons(request):
    return []
"""
    arbitrary_controller_call = selected_controller_call.replace(
        "from config.api import api", "from vendor import api"
    )

    ninja_status_extra = """from ninja import Router, status

router = Router()

@router.get('/lessons', response={200: dict}, openapi_extra={'responses': {status.HTTP_401_UNAUTHORIZED: {}}})
def list_lessons(request):
    return []
"""
    http_status_extra = """from http import HTTPStatus
from ninja import Router

router = Router()

@router.get('/lessons', response={200: dict}, openapi_extra={'responses': {HTTPStatus.UNAUTHORIZED: {}}})
def list_lessons(request):
    return []
"""
    success_status_extra = ninja_status_extra.replace(
        "HTTP_401_UNAUTHORIZED", "HTTP_200_OK"
    )
    early_return_instance = """from ninja import Router, Status
from application.lesson.presentation_layer.schema.error_out import LessonConflictError, LessonErrorOut, LessonNotFoundError

router = Router()

@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorOut, 409: LessonErrorOut})
def get_lesson(request, lesson_id: int):
    error = LessonNotFoundError()
    if lesson_id:
        error = LessonConflictError()
        return Status(error.status, error)
    return Status(error.status, error)
"""
    early_return_selected_api = """from ninja_extra import NinjaExtraAPI
from vendor import external_api

api = NinjaExtraAPI()

def build_schema(enabled):
    alias = api
    if enabled:
        alias = external_api
        return {}
    return alias.get_openapi_schema()
"""
    unreachable_match_error = flow_controller(
        """match 1:
    case 2:
        error = LessonNotFoundError()
        return Status(error.status, error)
    case 1:
        return {"id": lesson_id}"""
    )
    unreachable_match_selected_api = """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()

match 1:
    case 2:
        api.get_openapi_schema()
    case 1:
        pass
"""
    shadowed_setattr = """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()

def install(setattr):
    setattr(api, "get_openapi_schema", replacement)
"""
    two_step_instance_alias = flow_controller(
        """error = LessonNotFoundError()
first = error
second = first
return Status(second.status, second)"""
    )
    one_step_standard_status_alias = """from ninja import Router, status

router = Router()
unauthorized = status.HTTP_401_UNAUTHORIZED

@router.get('/lessons', response={200: dict}, openapi_extra={'responses': {unauthorized: {}}})
def list_lessons(request):
    return []
"""
    unselected_controller_call = """from ninja import Router
from config.api import api

router = Router()
api.get_openapi_schema()

@router.get('/catalog', response={200: dict})
def list_catalog(request):
    return []
"""
    mandatory_finally_error = """from ninja import Router, Status
from application.lesson.presentation_layer.schema.error_out import LessonErrorOut, LessonNotFoundError

router = Router()

@router.get('/{lesson_id}', response={200: dict})
def get_lesson(request, lesson_id: int):
    try:
        return {'id': lesson_id}
    finally:
        error = LessonNotFoundError()
        return Status(error.status, error)
"""
    mandatory_finally_selected_api = """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()

def build_schema():
    try:
        return {}
    finally:
        api.get_openapi_schema()
"""
    terminal_try_benign_finally = """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()

def build_schema():
    try:
        return {}
    finally:
        pass
    api.get_openapi_schema()
"""
    return [
        Case("openapi-clean-direct-404-409-same-bc-base", OPENAPI_FILES, "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-framework-statuses-not-advertised", OPENAPI_FILES, "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-separated-preserve-response-behavior", clean_with_preserve, "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-security-examples-metadata", with_files(("application/lesson/presentation_layer/controller.py", metadata_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-empty-error-bc", empty_error_bc_files, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/presentation_layer/controller.py", "--scope-bc", "lesson"), 0, ""),
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
        Case("openapi-clean-auto-profile-legacy-rules", OPENAPI_FILES, "check-openapi-error-declaration.py", AUTO_PROFILE_ARGS, 0, ""),
        Case("openapi-analysis-missing-code-source-args", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--api-module", "missing:--controller-module", "missing:--scope-bc"})),
        Case("openapi-clean-legacy-positional-help", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, ""),
        Case("openapi-fp-tests-migrations-cache-venv", {**OPENAPI_FILES, "application/lesson/presentation_layer/tests/test_openapi.py": excluded_violation, "application/lesson/presentation_layer/migrations/0001_openapi.py": excluded_violation, "application/lesson/presentation_layer/.cache/openapi.py": excluded_violation, "application/lesson/presentation_layer/.venv/openapi.py": excluded_violation}, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, ""),
        Case("openapi-fp-unignored-generated-path", {**OPENAPI_FILES, ".gitignore": "application/lesson/presentation_layer/ignored_openapi.py\n", "application/lesson/presentation_layer/generated/openapi.py": excluded_violation}, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, "", baseline_files={**OPENAPI_FILES, ".gitignore": "application/lesson/presentation_layer/ignored_openapi.py\n"}),
        Case("openapi-fp-git-ignored-selected-path", {**OPENAPI_FILES, ".gitignore": "application/lesson/presentation_layer/ignored_openapi.py\n", "application/lesson/presentation_layer/ignored_openapi.py": excluded_violation}, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, "", baseline_files={**OPENAPI_FILES, ".gitignore": "application/lesson/presentation_layer/ignored_openapi.py\n"}),
        Case("openapi-flow-match-return-missing-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(match_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2 if sys.version_info >= (3, 10) else 1, "BLOCKER" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-flow-match-return-correct-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(match_body, "{200: dict, 404: LessonErrorOut}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-flow-module-match-operation", with_files(("application/lesson/presentation_layer/controller.py", module_match_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2 if sys.version_info >= (3, 10) else 1, "BLOCKER" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-flow-trystar-return-missing-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(trystar_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2 if sys.version_info >= (3, 11) else 1, "BLOCKER" if sys.version_info >= (3, 11) else "사용 오류"),
        Case("openapi-flow-trystar-return-correct-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(trystar_body, "{200: dict, 404: LessonErrorOut}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 11) else 1, "" if sys.version_info >= (3, 11) else "사용 오류"),
        Case("openapi-flow-if-join-missing-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(if_join_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-flow-if-join-correct-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(if_join_body, "{200: dict, 404: LessonErrorOut}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-flow-with-join-missing-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(with_join_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-flow-with-join-correct-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(with_join_body, "{200: dict, 404: LessonErrorOut}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-flow-try-join-missing-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(try_join_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-flow-try-join-correct-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(try_join_body, "{200: dict, 404: LessonErrorOut}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-flow-error-instance-alias-missing-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(alias_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-flow-error-instance-alias-correct-response", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(alias_body, "{200: dict, 404: LessonErrorOut}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-analysis-error-instance-ambiguous-join", with_files(("application/lesson/presentation_layer/controller.py", flow_controller(ambiguous_join_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-framework-common-error-advertised", with_files(("application/lesson/presentation_layer/controller.py", no_direct_common), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-common-error-advertised-empty-error-bc", with_files(("application/lesson/presentation_layer/controller.py", no_direct_common), ("application/lesson/presentation_layer/schema/error_out.py", "<REMOVE>"), base=OPENAPI_FILES), "check-openapi-error-declaration.py", empty_error_bc_args, 2, "BLOCKER"),
        Case("openapi-framework-bc-base-error-advertised", with_files(("application/lesson/presentation_layer/controller.py", no_direct_base), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-concrete-error-advertised", with_files(("application/lesson/presentation_layer/controller.py", no_direct_concrete), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-clean-framework-dict-error-status", with_files(("application/lesson/presentation_layer/controller.py", no_direct_dict), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-framework-owned-error-schema", with_files(("application/lesson/presentation_layer/controller.py", no_direct_framework_schema), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-code-selected-bound-method-call", with_files(("config/api.py", selected_method_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-selected-literal-setattr", with_files(("config/api.py", selected_setattr), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-selected-controller-import-call", with_files(("application/lesson/presentation_layer/controller.py", selected_controller_call), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-clean-arbitrary-schema-receiver", with_files(("config/api.py", arbitrary_receiver), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-arbitrary-schema-setattr", with_files(("config/api.py", arbitrary_setattr), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-arbitrary-schema-class", with_files(("config/api.py", arbitrary_class), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-arbitrary-controller-receiver", with_files(("application/lesson/presentation_layer/controller.py", arbitrary_controller_call), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-analysis-conditionally-rebound-selected-receiver", with_files(("config/api.py", ambiguous_selected_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-clean-match-rebound-selected-receiver", with_files(("config/api.py", match_rebound_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-clean-trystar-rebound-selected-receiver", with_files(("config/api.py", trystar_rebound_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 11) else 1, "" if sys.version_info >= (3, 11) else "사용 오류"),
        Case("openapi-extra-ninja-status-constant", with_files(("application/lesson/presentation_layer/controller.py", ninja_status_extra), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-extra-httpstatus-constant", with_files(("application/lesson/presentation_layer/controller.py", http_status_extra), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-clean-extra-success-status-constant", with_files(("application/lesson/presentation_layer/controller.py", success_status_extra), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-round3-clean-early-return-error-instance", with_files(("application/lesson/presentation_layer/controller.py", early_return_instance), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-round3-selected-api-after-early-return", with_files(("config/api.py", early_return_selected_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-round3-clean-unreachable-match-error-return", with_files(("application/lesson/presentation_layer/controller.py", unreachable_match_error), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-round3-clean-unreachable-match-selected-api", with_files(("config/api.py", unreachable_match_selected_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-round3-clean-shadowed-setattr", with_files(("config/api.py", shadowed_setattr), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-round3-clean-two-step-error-instance-alias", with_files(("application/lesson/presentation_layer/controller.py", two_step_instance_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-round3-one-step-standard-status-alias", with_files(("application/lesson/presentation_layer/controller.py", one_step_standard_status_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-round3-clean-unselected-controller-api-call", with_files(("application/catalog/presentation_layer/controller.py", unselected_controller_call), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-round4-mandatory-finally-error-return", with_files(("application/lesson/presentation_layer/controller.py", mandatory_finally_error), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-round4-mandatory-finally-selected-api", with_files(("config/api.py", mandatory_finally_selected_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-round4-clean-terminal-try-benign-finally", with_files(("config/api.py", terminal_try_benign_finally), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
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
    compile_invalid = """from ninja import Router
from .schema import LessonOut
router = Router()
@router.get("/", response={200: LessonOut})
def endpoint(request):
    continue
"""
    conditional_response_rebind = """import os
from ninja import Router
from django.http import JsonResponse
from .schema import LessonOut
router = Router()
if os.getenv("CUSTOM_RESPONSE"):
    def JsonResponse(*args, **kwargs):
        return object()
@router.get("/", response={200: LessonOut})
def endpoint(request):
    return JsonResponse({"id": 1})
"""
    conditional_router_rebind = """import os
from ninja import Router
from django.http import JsonResponse
from .schema import LessonOut
router = Router()
if os.getenv("CUSTOM_ROUTER"):
    router = object()
@router.get("/", response={200: LessonOut})
def endpoint(request):
    return JsonResponse({"id": 1})
"""
    deterministic_response_rebind = conditional_response_rebind.replace(
        'if os.getenv("CUSTOM_RESPONSE"):\n    def JsonResponse(*args, **kwargs):\n        return object()\n',
        "def JsonResponse(*args, **kwargs):\n    return object()\n",
    )
    deterministic_router_rebind = conditional_router_rebind.replace(
        'if os.getenv("CUSTOM_ROUTER"):\n    router = object()\n',
        "router = object()\n",
    )
    match_capture_shadows = """from ninja import Router
from django.http import JsonResponse as MatchAsResponse
from django.http import JsonResponse as MatchStarResponse
from django.http import JsonResponse as MappingRestResponse
from django.http import JsonResponse as NestedResponse
from .schema import LessonOut
router = Router()
@router.get("/match-as", response={200: LessonOut})
def match_as_endpoint(request, payload):
    match payload:
        case MatchAsResponse:
            pass
    return MatchAsResponse({"id": 1})
@router.get("/match-star", response={200: LessonOut})
def match_star_endpoint(request, payload):
    match payload:
        case [*MatchStarResponse]:
            pass
    return MatchStarResponse({"id": 1})
@router.get("/mapping-rest", response={200: LessonOut})
def mapping_rest_endpoint(request, payload):
    match payload:
        case {"factory": _, **MappingRestResponse}:
            pass
    return MappingRestResponse({"id": 1})
@router.get("/nested", response={200: LessonOut})
def nested_endpoint(request, payload):
    match payload:
        case {"factory": [NestedResponse]}:
            pass
    return NestedResponse({"id": 1})
"""
    lexical_shadow_controls = """from ninja import Router
from django.http import JsonResponse as ParameterResponse
from django.http import JsonResponse as AssignedResponse
from django.http import JsonResponse as ImportedResponse
from .schema import LessonOut
router = Router()
@router.get("/parameter", response={200: LessonOut})
def parameter_endpoint(request, ParameterResponse):
    return ParameterResponse({"id": 1})
@router.get("/assignment", response={200: LessonOut})
def assignment_endpoint(request):
    AssignedResponse = lambda value: value
    return AssignedResponse({"id": 1})
@router.get("/local-import", response={200: LessonOut})
def import_endpoint(request):
    from application.responses import ImportedResponse
    return ImportedResponse({"id": 1})
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
        Case("success-fresh-analysis-selected-compile-invalid", success_files(compile_invalid), "check-response-schema-bypass.py", success_args(), 1, "사용 오류"),
        Case("success-fresh-analysis-compile-invalid-precedes-blocker", {**success_files(compile_invalid), "application/catalog/presentation_layer/controller.py": raw_200_decoy}, "check-response-schema-bypass.py", success_args("--controller-module", "application/catalog/presentation_layer/controller.py"), 1, "사용 오류"),
        Case("success-fresh-clean-unselected-compile-invalid", {**success_files(schema_object), "application/catalog/presentation_layer/controller.py": compile_invalid}, "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-fresh-analysis-conditional-response-rebind", success_files(conditional_response_rebind), "check-response-schema-bypass.py", success_args(), 1, "사용 오류"),
        Case("success-fresh-analysis-conditional-router-rebind", success_files(conditional_router_rebind), "check-response-schema-bypass.py", success_args(), 1, "사용 오류"),
        Case("success-fresh-clean-deterministic-rebind-away", {**success_files(deterministic_response_rebind), "application/catalog/presentation_layer/controller.py": deterministic_router_rebind}, "check-response-schema-bypass.py", success_args("--controller-module", "application/catalog/presentation_layer/controller.py"), 0, ""),
        Case("success-fresh-clean-match-capture-shadows", success_files(match_capture_shadows), "check-response-schema-bypass.py", success_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("success-fresh-clean-lexical-shadow-controls", success_files(lexical_shadow_controls), "check-response-schema-bypass.py", success_args(), 0, ""),
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
        if case.checker not in TARGET_ONLY_CHECKERS:
            raise ValueError(f"[{case.name}] checker does not support target-only invocation")
        if case.allowed_arg_issues:
            raise ValueError(f"[{case.name}] target-only command cannot allow argument issues")
        return

    allowed_arguments = CHECKER_ALLOWED_ARGUMENTS.get(case.checker)
    if allowed_arguments is None:
        raise ValueError(f"unsupported checker in matrix: {case.checker}")
    unsupported = set(values_by_argument) - allowed_arguments
    if unsupported:
        raise ValueError(f"[{case.name}] unsupported checker-specific arguments: {sorted(unsupported)}")

    issues: set[str] = set()
    profile_values = values_by_argument.get("--error-profile", [])
    if case.checker == "check-response-schema-bypass.py":
        required_arguments = {"--controller-module"}
    elif not profile_values:
        required_arguments = {
            "--error-profile",
            *PROFILE_REQUIRED_ARGUMENTS["dddjango-code-json"][case.checker],
        }
    elif len(profile_values) != 1:
        required_arguments = set()
    elif profile_values == ["auto"]:
        required_arguments = set()
        for argument in set(values_by_argument) - {"--error-profile"}:
            issues.add(f"auto-selector:{argument}")
    elif profile_values[0] in PROFILE_REQUIRED_ARGUMENTS:
        required_arguments = set(
            PROFILE_REQUIRED_ARGUMENTS[profile_values[0]][case.checker]
        )
        if (
            profile_values == ["preserve-established"]
            and case.checker == "check-composition-root.py"
            and set(values_by_argument) & {"--urlconf-module", "--registrar-module"}
        ):
            required_arguments.update(
                {"--urlconf-module", "--registrar-module"}
            )
    else:
        required_arguments = set()
        issues.add("value:--error-profile")

    issues.update(
        f"missing:{argument}"
        for argument in required_arguments
        if not values_by_argument.get(argument)
    )

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
