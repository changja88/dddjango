#!/usr/bin/env python3
"""Executable RED matrix for the planned dddjango API-error checkers.

The matrix intentionally uses only source text and checker subprocesses.  It is
an executable specification for the future ``dddjango-code-json`` checker CLI;
it must not import Django or Ninja itself.
"""
from __future__ import annotations

import os
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
MATCH_SYNTAX_SUPPORTED: Final = sys.version_info >= (3, 10)

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


class FrameworkErrorSchema(Schema):
    code: str
    title: str
    status: int
    detail: str
"""

LESSON_ERROR_OUT = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"
    CONFLICT = "lesson_conflict"


class LessonErrorSchema(FrameworkErrorSchema):
    code: LessonErrorCode


class LessonNotFoundError(LessonErrorSchema):
    code: LessonErrorCode = LessonErrorCode.NOT_FOUND
    title: str = "Lesson not found"
    status: int = 404
    detail: str = "The lesson does not exist."


class LessonConflictError(LessonErrorSchema):
    code: LessonErrorCode = LessonErrorCode.CONFLICT
    title: str = "Lesson conflict"
    status: int = 409
    detail: str = "The lesson cannot be changed."
"""

ALIAS_COMMON_ERROR_OUT = COMMON_ERROR_OUT.replace(
    "from ninja import Schema",
    "from ninja import Schema as NinjaSchema",
).replace("class FrameworkErrorSchema(Schema):", "class FrameworkErrorSchema(NinjaSchema):")

ALIAS_LESSON_ERROR_OUT = (
    LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum as StringEnum")
    .replace(
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema",
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema as CommonErrorOut",
    )
    .replace("class LessonErrorCode(StrEnum):", "class LessonErrorCode(StringEnum):")
    .replace("class LessonErrorSchema(FrameworkErrorSchema):", "class LessonErrorSchema(CommonErrorOut):")
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

CUSTOM_COMMON_ERROR_OUT = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    is_show: bool
"""

CUSTOM_LESSON_ERROR_OUT = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = LessonErrorCode.NOT_FOUND
    msg: str = "The lesson does not exist."
    is_show: bool = True
"""

FLEXIBLE_COMMON_ERROR_OUT = """from ninja import Schema
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str = Field(default="An error occurred.", serialization_alias="message")
    is_show: bool = True
    metadata: dict[str, str] | None = None
    model_config = ConfigDict(alias_generator=to_camel)
"""

FLEXIBLE_LESSON_ERROR_OUT = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = LessonErrorCode.NOT_FOUND
"""

ALIASED_STATUS_COMMON_ERROR_OUT = """from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    error_type: str = Field(alias="type")
    http_status: int = Field(default=500, serialization_alias="statusCode")
    msg: str
"""

ALIASED_STATUS_LESSON_ERROR_OUT = """from enum import StrEnum
from pydantic import Field
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode = Field(alias="type")


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = Field(
        default=LessonErrorCode.NOT_FOUND,
        alias="type",
    )
    http_status: int = Field(default=404, serialization_alias="statusCode")
    msg: str = "The lesson does not exist."
"""

DEFAULTED_ALIAS_COMMON_ERROR_OUT = """from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    error_type: str = Field(default="lesson_not_found", alias="type")
    msg: str
"""

DEFAULTED_ALIAS_LESSON_ERROR_OUT = """from enum import StrEnum
from pydantic import Field
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode = Field(
        default=LessonErrorCode.NOT_FOUND,
        alias="type",
    )


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = Field(
        default=LessonErrorCode.NOT_FOUND,
        alias="type",
    )
    msg: str = "The lesson does not exist."
"""

NULLABLE_DISCRIMINATOR_COMMON_ERROR_OUT = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str | None
    msg: str
"""

NULLABLE_DISCRIMINATOR_LESSON_ERROR_OUT = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode | None


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode | None = LessonErrorCode.NOT_FOUND
    msg: str = "The lesson does not exist."
"""

CONTAINER_DISCRIMINATOR_COMMON_ERROR_OUT = CUSTOM_COMMON_ERROR_OUT.replace(
    "error_type: str",
    "error_type: list[str]",
)

CONTAINER_DISCRIMINATOR_LESSON_ERROR_OUT = CUSTOM_LESSON_ERROR_OUT.replace(
    "error_type: LessonErrorCode",
    "error_type: list[LessonErrorCode]",
).replace(
    "error_type: list[LessonErrorCode] = LessonErrorCode.NOT_FOUND",
    "error_type: list[LessonErrorCode] = [LessonErrorCode.NOT_FOUND]",
)

UNRESOLVED_ALIAS_COMMON_ERROR_OUT = """from ninja import Schema
from pydantic import Field

_ALIAS = "type"


class FrameworkErrorSchema(Schema):
    error_type: str = Field(alias=_ALIAS)
    msg: str
"""

UNRESOLVED_ALIAS_LESSON_ERROR_OUT = """from enum import StrEnum
from pydantic import Field
from framework.ninja.framework_error_schema import FrameworkErrorSchema

_ALIAS = "kind"


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode = Field(alias=_ALIAS)


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = Field(
        default=LessonErrorCode.NOT_FOUND,
        alias=_ALIAS,
    )
    msg: str = "The lesson does not exist."
"""

UNRESOLVED_DEFAULT_COMMON_ERROR_OUT = """from ninja import Schema

_DEFAULT = "lesson_not_found"


class FrameworkErrorSchema(Schema):
    error_type: str = _DEFAULT
    msg: str
"""

UNRESOLVED_DEFAULT_LESSON_ERROR_OUT = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema

_DEFAULT = None


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"
    CONFLICT = "lesson_conflict"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode = _DEFAULT


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = LessonErrorCode.NOT_FOUND
    msg: str = "The lesson does not exist."
"""

DECORATED_COMMON_ERROR_OUT = """from ninja import Schema
from pydantic import field_serializer, field_validator


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    is_show: bool

    @field_validator("msg")
    @classmethod
    def validate_msg(cls, value: str) -> str:
        return value.strip()

    @field_serializer("msg")
    def serialize_msg(self, value: str) -> str:
        return value
"""

STATIC_CONSTANT_COMMON_ERROR_OUT = """from ninja import Schema
from pydantic import Field

_ALIAS = "type"
_DEFAULT = "lesson_not_found"


class FrameworkErrorSchema(Schema):
    error_type: str = Field(default=_DEFAULT, alias=_ALIAS)
    msg: str
"""

STATIC_CONSTANT_LESSON_ERROR_OUT = """from enum import StrEnum
from pydantic import Field
from framework.ninja.framework_error_schema import FrameworkErrorSchema

_ALIAS = "type"


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"
    CONFLICT = "lesson_conflict"


_DEFAULT = LessonErrorCode.NOT_FOUND


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode = Field(default=_DEFAULT, alias=_ALIAS)


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = Field(default=_DEFAULT, alias=_ALIAS)
    msg: str = "The lesson does not exist."
"""

ANNOTATED_COMMON_ERROR_OUT = """from typing import Annotated
from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    error_type: Annotated[
        str,
        Field(default="lesson_not_found", alias="type"),
    ]
    http_status: Annotated[
        int,
        Field(default=500, serialization_alias="statusCode"),
    ]
    msg: str
"""

ANNOTATED_LESSON_ERROR_OUT = """from enum import StrEnum
from typing import Annotated
from pydantic import Field
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"
    CONFLICT = "lesson_conflict"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: Annotated[
        LessonErrorCode,
        Field(default=LessonErrorCode.NOT_FOUND, alias="type"),
    ]


class LessonNotFoundError(LessonErrorSchema):
    error_type: Annotated[
        LessonErrorCode,
        Field(default=LessonErrorCode.NOT_FOUND, alias="type"),
    ]
    http_status: Annotated[
        int,
        Field(default=404, serialization_alias="statusCode"),
    ]
    msg: str = "The lesson does not exist."
"""

ANNOTATED_CONTROLLER = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorSchema})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        error = LessonNotFoundError()
        return Status(error.http_status, error)
    return lesson
"""

ANNOTATED_BASE_CONTROLLER = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema

router = Router()


@router.get('/{lesson_id}', response={200: dict, 500: LessonErrorSchema})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        error = LessonErrorSchema(msg="The lesson does not exist.")
        return Status(error.http_status, error)
    return lesson
"""

TYPING_EXTENSIONS_ANNOTATED_COMMON_ERROR_OUT = ANNOTATED_COMMON_ERROR_OUT.replace(
    "from typing import Annotated",
    "from typing_extensions import Annotated",
)

TYPING_EXTENSIONS_ANNOTATED_LESSON_ERROR_OUT = ANNOTATED_LESSON_ERROR_OUT.replace(
    "from typing import Annotated",
    "from typing_extensions import Annotated",
)

NESTED_CONFIG_COMMON_ERROR_OUT = CUSTOM_COMMON_ERROR_OUT.replace(
    "    is_show: bool\n",
    "    is_show: bool\n\n"
    "    class Config:\n"
    "        populate_by_name = True\n",
)

ALIASED_STATUS_CONTROLLER = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: LessonErrorSchema})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        error = LessonNotFoundError()
        return Status(error.http_status, error)
    return lesson
"""

CUSTOM_CONTROLLER = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: LessonErrorSchema})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        error = LessonNotFoundError()
        return Status(404, error)
    return lesson
"""

CATALOG_DUPLICATE_ERROR_OUT = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class CatalogErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class CatalogErrorSchema(FrameworkErrorSchema):
    code: CatalogErrorCode


class CatalogNotFoundError(CatalogErrorSchema):
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
    "framework/ninja/__init__.py": "",
    "framework/ninja/framework_error_schema.py": COMMON_ERROR_OUT,
    "application/lesson/driving_layer/api/bc_error_schema.py": LESSON_ERROR_OUT,
    "config/api.py": "from ninja_extra import NinjaExtraAPI\n\napi = NinjaExtraAPI()\n",
    "application/lesson/driving_layer/controller.py": "def get_lesson(request): return {'id': 1}\n",
}

CONTROLLER_FILES: Final = {
    **BASE_FILES,
    "application/lesson/application_layer/use_cases.py": """class LessonMissing(Exception):
    pass


def get_lesson(lesson_id: int):
    return {"id": lesson_id}
""",
    "application/lesson/driving_layer/controller.py": """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError

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
        "application/lesson/driving_layer/controller.py",
        "--scope-bc",
        "lesson",
        "--error-bc",
        "lesson",
        "--project-code-error-module",
        "framework/ninja/framework_error_schema.py",
        "--project-code-error-module",
        "application/lesson/driving_layer/api/bc_error_schema.py",
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
        "application/lesson/driving_layer/controller.py",
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
        "framework/ninja/__init__.py": "",
        "framework/ninja/framework_error_schema.py": COMMON_ERROR_OUT,
        "config/api.py": BASE_FILES["config/api.py"],
        "application/lesson/driving_layer/controller.py": BASE_FILES["application/lesson/driving_layer/controller.py"],
    }
    no_error_bc = dict(common_only)
    no_error_bc["application/catalog/driving_layer/controller.py"] = "pass\n"
    preserve = {
        "legacy/errors.py": "class FrameworkErrorSchema: pass\n",
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": "def legacy(request): return {'error': 'old'}\n",
        "framework/ninja/__init__.py": "",
        "framework/ninja/framework_error_schema.py": COMMON_ERROR_OUT,
    }
    reused_surfaces = with_files(
        ("config/api.py", "api = object()\n"),
        ("config/api_v2.py", "api = object()\n"),
        ("application/lesson/driving_layer/controller.py", "def get_lesson(request): pass\n"),
        ("application/lesson/driving_layer/controller_v2.py", "def get_lesson_v2(request): pass\n"),
    )
    duplicate_project_code = with_files(
        ("application/catalog/driving_layer/api/bc_error_schema.py", CATALOG_DUPLICATE_ERROR_OUT),
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
        LESSON_ERROR_OUT.replace("class LessonErrorSchema(FrameworkErrorSchema):\n    code: LessonErrorCode\n\n\n", "")
        .replace("class LessonNotFoundError(LessonErrorSchema):", "class LessonNotFoundError(FrameworkErrorSchema):")
        .replace("class LessonConflictError(LessonErrorSchema):", "class LessonConflictError(FrameworkErrorSchema):")
    )
    preserve_empty_inventories = {
        "legacy/api.py": "api = object()\n",
        "legacy/controller.py": "def legacy(request): return {'error': 'old'}\n",
        "application/legacy/application_layer/use_case.py": (
            "def run():\n"
            "    status = 404\n"
            "    return status\n"
        ),
        "application/legacy/driving_layer/__init__.py": "",
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
        ("framework/ninja/framework_error_schema.py", ALIAS_COMMON_ERROR_OUT),
        ("application/lesson/driving_layer/api/bc_error_schema.py", ALIAS_LESSON_ERROR_OUT),
    )
    dynamic_required_files = with_files(
        ("framework/ninja/framework_error_schema.py", DYNAMIC_COMMON_ERROR_OUT),
        ("application/lesson/driving_layer/api/bc_error_schema.py", DYNAMIC_LESSON_ERROR_OUT),
    )
    missing_dynamic_default = DYNAMIC_LESSON_ERROR_OUT.replace(
        '    trace_id: str = "lesson-not-found"\n',
        "",
        1,
    )
    preserve_duplicate_error_out = LESSON_ERROR_OUT.replace("Lesson", "Legacy")
    code_with_preserve_duplicate = with_files(
        (
            "application/legacy/driving_layer/api/bc_error_schema.py",
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
        ".gitignore": "framework/ninja/ignored.py\n",
    }
    ignored_generated_files = {
        **ignored_generated_baseline,
        "framework/ninja/ignored.py": "def ignored_helper(): pass\n",
        "framework/ninja/generated/decoy.py": "def generated_helper(): pass\n",
    }
    foreign_enum_default = LESSON_ERROR_OUT.replace(
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema",
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema\n"
        "from application.catalog.driving_layer.api.bc_error_schema import CatalogErrorCode",
    ).replace(
        "code: LessonErrorCode = LessonErrorCode.NOT_FOUND",
        "code: LessonErrorCode = CatalogErrorCode.NOT_FOUND",
        1,
    )
    raw_string_controller = """from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError


def get_lesson(request):
    error = LessonNotFoundError()
    error.code = "lesson_not_found"
    return error
"""
    exact_concrete_code_annotation = LESSON_ERROR_OUT.replace(
        "class LessonNotFoundError(LessonErrorSchema):",
        "class PreparedLessonMissing(LessonErrorSchema):",
    )
    broadened_concrete_code_annotation = exact_concrete_code_annotation.replace(
        "code: LessonErrorCode = LessonErrorCode.NOT_FOUND",
        "code: object = LessonErrorCode.NOT_FOUND",
        1,
    )
    indirect_alias_model_config = LESSON_ERROR_OUT.replace(
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema",
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema\n"
        "from pydantic import ConfigDict",
    ).replace(
        "class LessonNotFoundError(LessonErrorSchema):",
        "class LessonNotFoundError(LessonErrorSchema):\n"
        "    _wire_config = ConfigDict(alias_generator=lambda value: 'x_' + value)\n"
        "    model_config = _wire_config",
    )
    benign_indirect_model_config = LESSON_ERROR_OUT.replace(
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema",
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema\n"
        "from pydantic import ConfigDict",
    ).replace(
        "class LessonNotFoundError(LessonErrorSchema):",
        "class LessonNotFoundError(LessonErrorSchema):\n"
        "    _unused_wire_config = ConfigDict(alias_generator=lambda value: 'x_' + value)\n"
        "    _benign_config = ConfigDict(title='Lesson error')\n"
        "    model_config = _benign_config",
    )
    nested_outside_concrete = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema


def build_error_type():
    class NestedLessonError(LessonErrorSchema):
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
    walrus_bound_error = """from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError


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
        "class LessonNotFoundError(LessonErrorSchema):",
        "class LessonNotFoundErrorOut(LessonErrorSchema):",
    )
    true_second_bc_base = LESSON_ERROR_OUT + """

class AnotherLessonErrorSchema(FrameworkErrorSchema):
    code: LessonErrorCode
"""
    shadowed_constructor_expressions = """from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError


def decoys(factories):
    return (
        (lambda LessonNotFoundError: LessonNotFoundError(code="ordinary"))(dict),
        [LessonNotFoundError(code="ordinary") for LessonNotFoundError in factories],
        {LessonNotFoundError(code="ordinary") for LessonNotFoundError in factories},
        {index: LessonNotFoundError(code="ordinary") for index, LessonNotFoundError in enumerate(factories)},
        tuple(LessonNotFoundError(code="ordinary") for LessonNotFoundError in factories),
    )
"""
    unshadowed_constructor_expressions = """from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError


def raw_errors(factories):
    return (
        (lambda factory: LessonNotFoundError(code="lesson_not_found"))(dict),
        [LessonNotFoundError(code="lesson_not_found") for factory in factories],
        {LessonNotFoundError(code="lesson_not_found") for factory in factories},
        {index: LessonNotFoundError(code="lesson_not_found") for index, factory in enumerate(factories)},
        tuple(LessonNotFoundError(code="lesson_not_found") for factory in factories),
    )
"""
    undefined_required_common = """from ninja import Schema
from pydantic import Field
from pydantic_core import PydanticUndefined


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str = Field(default=PydanticUndefined)
"""
    undefined_required_annotated_common = """from typing import Annotated
from ninja import Schema
from pydantic import Field
from pydantic_core import PydanticUndefined


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: Annotated[str, Field(default=PydanticUndefined)]
"""
    undefined_required_lesson = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = LessonErrorCode.NOT_FOUND
"""
    undefined_factory_common = undefined_required_common.replace(
        "Field(default=PydanticUndefined)",
        "Field(default=PydanticUndefined, default_factory=str)",
    )
    undefined_factory_reverse_common = undefined_required_common.replace(
        "Field(default=PydanticUndefined)",
        "Field(default_factory=str, default=PydanticUndefined)",
    )
    undefined_direct_common = undefined_required_common.replace(
        "msg: str = Field(default=PydanticUndefined)",
        "msg: str = PydanticUndefined",
    )
    undefined_direct_alias_common = undefined_direct_common.replace(
        "from pydantic_core import PydanticUndefined",
        "from pydantic_core import PydanticUndefined as Undefined",
    ).replace("msg: str = PydanticUndefined", "msg: str = Undefined")
    ellipsis_direct_common = undefined_required_common.replace(
        "msg: str = Field(default=PydanticUndefined)",
        "msg: str = ...",
    )
    annotated_merge_default_common = """from typing import Annotated
from ninja import Schema
from pydantic import Field
from pydantic_core import PydanticUndefined


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: Annotated[str, Field(default='missing')] = PydanticUndefined
"""
    annotated_merge_field_sentinel_common = annotated_merge_default_common.replace(
        "= PydanticUndefined",
        "= Field(default=PydanticUndefined)",
    )
    annotated_merge_ellipsis_common = annotated_merge_default_common.replace(
        "= PydanticUndefined",
        "= ...",
    )
    annotated_merge_factory_common = annotated_merge_default_common.replace(
        "Field(default='missing')",
        "Field(default_factory=str)",
    )
    annotated_metadata_sentinel_common = annotated_merge_default_common.replace(
        "] = PydanticUndefined",
        ", Field(default=PydanticUndefined)]",
    )
    annotated_default_clear_factory_common = annotated_merge_default_common.replace(
        "= PydanticUndefined",
        "= Field(default_factory=None)",
    )
    annotated_factory_clear_factory_common = annotated_merge_factory_common.replace(
        "= PydanticUndefined",
        "= Field(default_factory=None)",
    )
    conflicting_default_factory_common = undefined_required_common.replace(
        "Field(default=PydanticUndefined)",
        "Field(default='missing', default_factory=str)",
    )
    conflicting_annotated_default_factory_common = annotated_merge_default_common.replace(
        "Annotated[str, Field(default='missing')] = PydanticUndefined",
        "Annotated[str, Field(default='missing'), Field(default_factory=str)]",
    )
    nested_required_common = """from typing import Annotated
from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: Annotated[
        Annotated[str, Field(default_factory=str)],
        Field(default_factory=None),
    ]
"""
    nested_optional_common = nested_required_common.replace(
        "Annotated[str, Field(default_factory=str)],\n        Field(default_factory=None)",
        "Annotated[str, Field(default_factory=None)],\n        Field(default_factory=str)",
    )
    custom_generator_common = """from ninja import Schema
from pydantic import ConfigDict
from framework.ninja.aliasing import wire_name


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(alias_generator=wire_name)
"""
    custom_builder_common = """from ninja import Schema
from framework.ninja.configs import build_config


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = build_config()
"""
    custom_builder_support = """from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


def build_config():
    return ConfigDict(alias_generator=to_camel)


from framework.ninja import mutator
"""
    custom_builder_mutator = """import sys
from pydantic import ConfigDict


target = sys.modules['framework.ninja.configs']
target.build_config = lambda: ConfigDict(
    alias_generator=lambda value: f'actual_{value}'
)
"""
    schema_extra_support = """def enrich(schema: dict) -> None:
    schema['x-contract'] = 'changed'
"""
    model_config_schema_extra_common = """from ninja import Schema
from pydantic import ConfigDict
from framework.ninja.schema_extra import enrich


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(json_schema_extra=enrich)
"""
    class_header_schema_extra_common = """from ninja import Schema
from framework.ninja.schema_extra import enrich


class FrameworkErrorSchema(Schema, json_schema_extra=enrich):
    error_type: str
    msg: str
"""
    class_header_unpack_common = """from ninja import Schema
from framework.ninja.aliasing import wire_name


class FrameworkErrorSchema(
    Schema,
    **{'alias_generator': wire_name, 'validate_by_name': True},
):
    error_type: str
    msg: str
"""
    class_header_builder_common = """from ninja import Schema
from framework.ninja.configs import build_config


class FrameworkErrorSchema(Schema, **build_config()):
    error_type: str
    msg: str
"""
    class_header_builder_support = """from framework.ninja.aliasing import wire_name


def build_config():
    return {'alias_generator': wire_name, 'validate_by_name': True}
"""
    literal_schema_extra_common = """from ninja import Schema
from pydantic import ConfigDict


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(json_schema_extra={'x-contract': 'approved'})
"""
    literal_header_schema_extra_common = """from ninja import Schema


class FrameworkErrorSchema(Schema, json_schema_extra={'x-contract': 'approved'}):
    error_type: str
    msg: str
"""
    builtin_callable_schema_extra_common = """import builtins

from ninja import Schema
from pydantic import ConfigDict


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(json_schema_extra=builtins.dict.clear)
"""
    pydantic_alias_generator_wrong_slot_common = """from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(json_schema_extra=to_camel)
"""
    builtin_default_factory_common = """import builtins

from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    trace: str = Field(default_factory=builtins.print)
"""
    decorator_support = """from pydantic import ConfigDict


def apply_config(model):
    model.model_config = ConfigDict(json_schema_extra={'x-contract': 'changed'})
    model.model_rebuild(force=True)
    return model
"""
    decorated_common = """from ninja import Schema
from framework.ninja.schema_extra import apply_config


@apply_config
class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
"""
    legacy_config_support = """from framework.ninja.aliasing import wire_name


class ProjectErrorConfig:
    alias_generator = wire_name
    allow_population_by_field_name = True
"""
    inherited_legacy_config_common = """from ninja import Schema
from framework.ninja.configs import ProjectErrorConfig


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str

    class Config(ProjectErrorConfig):
        pass
"""
    subscript_mutated_model_config_common = """from ninja import Schema
from pydantic import ConfigDict
from framework.ninja.aliasing import wire_name


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(validate_by_name=True)
    model_config['alias_generator'] = wire_name
"""
    augmented_model_config_common = """from ninja import Schema
from pydantic import ConfigDict
from framework.ninja.aliasing import wire_name


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(validate_by_name=True)
    model_config |= {'alias_generator': wire_name}
"""
    imported_schema_mutator = """from ninja import Schema
from framework.ninja.aliasing import wire_name


Schema.model_config.update(
    alias_generator=wire_name,
    validate_by_name=True,
)
"""
    side_effect_import_common = """import framework.ninja.configure_schema
from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
"""
    nested_side_effect_import_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    import framework.ninja.configure_schema as _configure_schema

    error_type: str
    msg: str
"""
    direct_schema_mutation_common = """from ninja import Schema
from pydantic.alias_generators import to_camel


Schema.model_config.update(
    alias_generator=to_camel,
    validate_by_name=True,
)


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
"""
    private_iife_schema_mutation_common = """from ninja import Schema


_configured = (lambda: Schema.model_config.update(
    json_schema_extra=lambda schema: schema.clear(),
))()


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
"""
    private_deferred_schema_mutation_common = private_iife_schema_mutation_common.replace(
        "_configured = (lambda: Schema.model_config.update(\n"
        "    json_schema_extra=lambda schema: schema.clear(),\n"
        "))()",
        "_configured = lambda: Schema.model_config.update(\n"
        "    json_schema_extra=lambda schema: schema.clear(),\n"
        ")",
    )
    private_parameter_iife_schema_mutation_common = """from ninja import Schema


_configured = (
    lambda model: model.model_config.update(
        alias_generator=lambda value: f'wire_{value}',
        validate_by_name=True,
    )
)(Schema)


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
"""
    private_parameter_deferred_schema_mutation_common = (
        private_parameter_iife_schema_mutation_common.replace(
            "_configured = (\n    lambda model:",
            "_configured = lambda model:",
        ).replace("\n)(Schema)\n", "\n")
    )
    private_dunder_ior_schema_mutation_common = """from ninja import Schema


_configured = Schema.model_config.__ior__({'extra': 'forbid'})


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
"""
    private_dunder_init_schema_mutation_common = private_dunder_ior_schema_mutation_common.replace(
        ".__ior__({'extra': 'forbid'})",
        ".__init__({'extra': 'forbid'})",
    )
    private_type_setattr_schema_mutation_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str


_configured = type.__setattr__(FrameworkErrorSchema, 'model_config', {'extra': 'forbid'})
"""
    private_config_alias_schema_mutation_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str


_error_config = FrameworkErrorSchema.model_config
_configured = _error_config.update(extra='forbid')
"""
    private_bound_mutator_alias_schema_mutation_common = (
        private_config_alias_schema_mutation_common.replace(
            "_error_config = FrameworkErrorSchema.model_config\n"
            "_configured = _error_config.update(extra='forbid')",
            "_mutate = FrameworkErrorSchema.model_config.update\n"
            "_configured = _mutate(extra='forbid')",
        )
    )
    private_read_only_config_alias_common = private_config_alias_schema_mutation_common.replace(
        "_configured = _error_config.update(extra='forbid')",
        "_configured = _error_config.get('extra')",
    )
    private_named_lambda_schema_mutation_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str


_mutate = lambda model: model.model_config.update(extra='forbid')
_configured = _mutate(FrameworkErrorSchema)
"""
    private_named_lambda_deferred_common = (
        private_named_lambda_schema_mutation_common.replace(
            "_configured = _mutate(FrameworkErrorSchema)\n",
            "",
        )
    )
    private_named_lambda_alias_mutation_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str


_mutate = lambda: Schema.model_config.update(extra='forbid')
_alias = _mutate
_configured = _alias()
"""
    private_named_lambda_alias_deferred_common = (
        private_named_lambda_alias_mutation_common.replace(
            "_configured = _alias()\n",
            "",
        )
    )
    private_named_lambda_unpack_alias_mutation_common = (
        private_named_lambda_alias_mutation_common.replace(
            "_alias = _mutate",
            "_alias, = (_mutate,)",
        )
    )
    private_named_lambda_unpack_alias_deferred_common = (
        private_named_lambda_unpack_alias_mutation_common.replace(
            "_configured = _alias()\n",
            "",
        )
    )
    bc_schema_mutator = """from framework.ninja.framework_error_schema import FrameworkErrorSchema


FrameworkErrorSchema.model_config.update(
    alias_generator=lambda value: f'wire_{value}',
    validate_by_name=True,
)
FrameworkErrorSchema.model_rebuild(force=True)
"""
    side_effect_import_lesson = CUSTOM_LESSON_ERROR_OUT.replace(
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema",
        "from framework.ninja.framework_error_schema import FrameworkErrorSchema\n"
        "import application.lesson.driving_layer.api.configure_error_out",
    )
    nested_side_effect_import_lesson = CUSTOM_LESSON_ERROR_OUT.replace(
        "class LessonErrorSchema(FrameworkErrorSchema):",
        "class LessonErrorSchema(FrameworkErrorSchema):\n"
        "    import application.lesson.driving_layer.api.configure_error_out as _configure_error_out",
    )
    lambda_model_alias_common = """from ninja import Schema
from pydantic import ConfigDict


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(
        alias_generator=lambda value: f'wire_{value}',
    )
"""
    lambda_schema_extra_common = """from ninja import Schema
from pydantic import ConfigDict


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(
        json_schema_extra=lambda schema: schema.update({'x-contract': 'changed'}),
    )
"""
    lambda_header_alias_common = """from ninja import Schema


class FrameworkErrorSchema(
    Schema,
    alias_generator=lambda value: f'wire_{value}',
):
    error_type: str
    msg: str
"""
    lambda_legacy_alias_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str

    class Config:
        alias_generator = lambda value: f'wire_{value}'
"""
    lambda_header_unpack_common = """from ninja import Schema


class FrameworkErrorSchema(
    Schema,
    **{'alias_generator': lambda value: f'wire_{value}'},
):
    error_type: str
    msg: str
"""
    lambda_decorated_common = """from ninja import Schema


@(lambda model: model)
class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
"""
    lambda_mutated_model_config_common = """from ninja import Schema
from pydantic import ConfigDict


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(validate_by_name=True)
    model_config['alias_generator'] = lambda value: f'wire_{value}'
"""
    executable_class_body_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    (lambda: Schema.model_config.update(
        alias_generator=lambda value: f'wire_{value}',
        validate_by_name=True,
    ))()

    error_type: str
    msg: str
"""
    dynamic_private_class_binding_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    _configured = (
        lambda: Schema.model_config.update(
            alias_generator=lambda value: f'wire_{value}',
            validate_by_name=True,
        )
    )()

    error_type: str
    msg: str
"""
    dynamic_classvar_binding_common = """from typing import ClassVar

from ninja import Schema


class FrameworkErrorSchema(Schema):
    mutation_marker: ClassVar[None] = (
        lambda: Schema.model_config.update(
            json_schema_extra=lambda schema: schema.clear(),
        )
    )()

    error_type: str
    msg: str
"""
    static_private_class_binding_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    _APPROVED_STATUS = 500

    error_type: str
    msg: str
"""
    static_symbol_classvar_common = """from typing import ClassVar

from ninja import Schema


class FrameworkErrorSchema(Schema):
    wire_type: ClassVar[type] = str

    error_type: str
    msg: str
"""
    dynamic_public_field_default_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    side_effect_marker: int = (
        lambda: (
            Schema.model_config.update(
                json_schema_extra=lambda schema: None,
            ),
            1,
        )[1]
    )()
"""
    pydantic_subclass_hook_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        cls.model_config.update(
            alias_generator=lambda value: f'wire_{value}',
            validate_by_name=True,
        )
        cls.model_rebuild(force=True)
"""
    declarative_class_body_control_common = """from ninja import Schema


class FrameworkErrorSchema(Schema):
    \"\"\"Approved exact transport shape.\"\"\"

    error_type: str
    msg: str
    pass
"""
    executable_bc_class_body = CUSTOM_LESSON_ERROR_OUT.replace(
        "class LessonErrorSchema(FrameworkErrorSchema):\n    error_type: LessonErrorCode",
        "class LessonErrorSchema(FrameworkErrorSchema):\n"
        "    (lambda: FrameworkErrorSchema.model_config.update(validate_by_name=True))()\n"
        "    error_type: LessonErrorCode",
    )
    dynamic_bc_classvar_binding = CUSTOM_LESSON_ERROR_OUT.replace(
        "from enum import StrEnum",
        "from enum import StrEnum\nfrom typing import ClassVar",
    ).replace(
        "class LessonErrorSchema(FrameworkErrorSchema):\n    error_type: LessonErrorCode",
        "class LessonErrorSchema(FrameworkErrorSchema):\n"
        "    mutation_marker: ClassVar[None] = (\n"
        "        lambda: FrameworkErrorSchema.model_config.update(\n"
        "            json_schema_extra=lambda schema: schema.clear(),\n"
        "        )\n"
        "    )()\n\n"
        "    error_type: LessonErrorCode",
    )
    static_bc_classvar_control = CUSTOM_LESSON_ERROR_OUT.replace(
        "from enum import StrEnum",
        "from enum import StrEnum\nfrom typing import ClassVar",
    ).replace(
        "class LessonErrorSchema(FrameworkErrorSchema):\n    error_type: LessonErrorCode",
        "class LessonErrorSchema(FrameworkErrorSchema):\n"
        "    contract_revision: ClassVar[int] = 1\n\n"
        "    error_type: LessonErrorCode",
    )
    static_symbol_bc_classvar_control = static_bc_classvar_control.replace(
        "contract_revision: ClassVar[int] = 1",
        "wire_type: ClassVar[type] = str",
    )
    custom_generator_lesson = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = LessonErrorCode.NOT_FOUND
    msg: str = "missing"
"""
    custom_generator_raw_controller = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema


def get_lesson(request):
    return LessonErrorSchema(wire_error_type="lesson_not_found", wire_msg="missing")
"""
    custom_generator_enum_controller = custom_generator_raw_controller.replace(
        "import LessonErrorSchema",
        "import LessonErrorCode, LessonErrorSchema",
    ).replace(
        'wire_error_type="lesson_not_found"',
        "wire_error_type=LessonErrorCode.NOT_FOUND",
    ).replace('wire_msg="missing"', "wire_msg=str()")
    custom_generator_unrelated_literal_controller = custom_generator_enum_controller.replace(
        "wire_msg=str()",
        'wire_msg="lesson_not_found"',
    )
    custom_generator_typo_controller = custom_generator_raw_controller.replace(
        'wire_error_type="lesson_not_found"',
        'wire_error_type="lesson_missing_typo"',
    )
    static_raw_controller = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema

_RAW_CODE = "lesson_not_found"


def get_lesson(request):
    return LessonErrorSchema(code=_RAW_CODE, title="missing", status=404, detail="missing")
"""
    alias_path_common = """from ninja import Schema
from pydantic import AliasPath, Field


class FrameworkErrorSchema(Schema):
    error_type: str = Field(validation_alias=AliasPath('payload', 'kind'))
    msg: str
"""
    alias_path_lesson = """from enum import StrEnum
from pydantic import AliasPath, Field
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode = Field(validation_alias=AliasPath('payload', 'kind'))


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = Field(
        default=LessonErrorCode.NOT_FOUND,
        validation_alias=AliasPath('payload', 'kind'),
    )
    msg: str = "missing"
"""
    alias_path_raw_controller = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema


def get_lesson(request):
    return LessonErrorSchema(payload={'kind': 'lesson_not_found'}, msg='missing')
"""
    alias_path_enum_controller = alias_path_raw_controller.replace(
        "import LessonErrorSchema",
        "import LessonErrorCode, LessonErrorSchema",
    ).replace("'lesson_not_found'", "LessonErrorCode.NOT_FOUND")
    alias_path_unrelated_literal_controller = alias_path_enum_controller.replace(
        "{'kind': LessonErrorCode.NOT_FOUND}",
        "{'kind': LessonErrorCode.NOT_FOUND, 'note': 'lesson_not_found'}",
    )
    alias_choices_common = alias_path_common.replace(
        "from pydantic import AliasPath, Field",
        "from pydantic import AliasChoices, AliasPath, Field",
    ).replace(
        "AliasPath('payload', 'kind')",
        "AliasChoices(AliasPath('payload', 'kind'))",
    )
    alias_choices_lesson = alias_path_lesson.replace(
        "from pydantic import AliasPath, Field",
        "from pydantic import AliasChoices, AliasPath, Field",
    ).replace(
        "AliasPath('payload', 'kind')",
        "AliasChoices(AliasPath('payload', 'kind'))",
    )
    known_typo_controller = static_raw_controller.replace(
        "code=_RAW_CODE",
        "code='lesson_typo'",
    )
    literal_unpack_controller = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema


def get_lesson(request):
    return LessonErrorSchema(**{'code': 'lesson_not_found', 'title': 'missing', 'status': 404, 'detail': 'missing'})
"""
    dynamic_unpack_controller = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema


def get_lesson(request, payload):
    return LessonErrorSchema(**payload)
"""
    alias_path_named_static_raw_controller = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema

_PAYLOAD = {'kind': 'lesson_not_found'}


def get_lesson(request):
    return LessonErrorSchema(payload=_PAYLOAD, msg='missing')
"""
    alias_path_named_enum_controller = alias_path_named_static_raw_controller.replace(
        "import LessonErrorSchema",
        "import LessonErrorCode, LessonErrorSchema",
    ).replace("'lesson_not_found'", "LessonErrorCode.NOT_FOUND")
    alias_path_dynamic_payload_controller = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema


def get_lesson(request, payload):
    return LessonErrorSchema(payload=payload, msg='missing')
"""
    alias_path_nested_unpack_raw_controller = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema


def get_lesson(request):
    return LessonErrorSchema(
        payload={
            'kind': LessonErrorCode.NOT_FOUND,
            **{'kind': 'lesson_not_found'},
        },
        msg='missing',
    )
"""
    return [
        Case("schema-required-pydantic-undefined-default", with_files(("framework/ninja/framework_error_schema.py", undefined_required_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-required-pydantic-undefined-annotated", with_files(("framework/ninja/framework_error_schema.py", undefined_required_annotated_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-clean-pydantic-undefined-with-real-factory", with_files(("framework/ninja/framework_error_schema.py", undefined_factory_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-pydantic-undefined-with-real-factory-reversed", with_files(("framework/ninja/framework_error_schema.py", undefined_factory_reverse_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-required-direct-pydantic-undefined", with_files(("framework/ninja/framework_error_schema.py", undefined_direct_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-required-direct-pydantic-undefined-import-alias", with_files(("framework/ninja/framework_error_schema.py", undefined_direct_alias_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-required-direct-ellipsis", with_files(("framework/ninja/framework_error_schema.py", ellipsis_direct_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-clean-annotated-default-survives-direct-undefined", with_files(("framework/ninja/framework_error_schema.py", annotated_merge_default_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-annotated-default-survives-field-undefined", with_files(("framework/ninja/framework_error_schema.py", annotated_merge_field_sentinel_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-annotated-default-survives-ellipsis", with_files(("framework/ninja/framework_error_schema.py", annotated_merge_ellipsis_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-annotated-factory-survives-direct-undefined", with_files(("framework/ninja/framework_error_schema.py", annotated_merge_factory_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-annotated-default-survives-later-metadata-sentinel", with_files(("framework/ninja/framework_error_schema.py", annotated_metadata_sentinel_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-annotated-default-survives-factory-clear", with_files(("framework/ninja/framework_error_schema.py", annotated_default_clear_factory_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-required-annotated-factory-cleared", with_files(("framework/ninja/framework_error_schema.py", annotated_factory_clear_factory_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-conflicting-default-and-factory", with_files(("framework/ninja/framework_error_schema.py", conflicting_default_factory_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-analysis-conflicting-annotated-default-and-factory", with_files(("framework/ninja/framework_error_schema.py", conflicting_annotated_default_factory_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-nested-annotated-outer-factory-clear-is-required", with_files(("framework/ninja/framework_error_schema.py", nested_required_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-clean-nested-annotated-outer-factory", with_files(("framework/ninja/framework_error_schema.py", nested_optional_common), ("application/lesson/driving_layer/api/bc_error_schema.py", undefined_required_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-analysis-custom-alias-generator-raw-wire-code", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson), ("application/lesson/driving_layer/controller.py", custom_generator_raw_controller)), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-analysis-custom-alias-generator-requires-runtime-proof", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson), ("application/lesson/driving_layer/controller.py", custom_generator_enum_controller)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-custom-config-builder-prepared-path-requires-runtime-proof", with_files(("framework/ninja/configs.py", custom_builder_support), ("framework/ninja/mutator.py", custom_builder_mutator), ("framework/ninja/framework_error_schema.py", custom_builder_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson), ("application/lesson/driving_layer/controller.py", "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError\n\n\ndef get_lesson(request):\n    return LessonNotFoundError()\n")), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-project-model-config-schema-extra-requires-runtime-proof", with_files(("framework/ninja/schema_extra.py", schema_extra_support), ("framework/ninja/framework_error_schema.py", model_config_schema_extra_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-project-class-header-schema-extra-requires-runtime-proof", with_files(("framework/ninja/schema_extra.py", schema_extra_support), ("framework/ninja/framework_error_schema.py", class_header_schema_extra_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-project-class-header-unpack-requires-runtime-proof", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/framework_error_schema.py", class_header_unpack_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-project-class-header-builder-requires-runtime-proof", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/configs.py", class_header_builder_support), ("framework/ninja/framework_error_schema.py", class_header_builder_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-project-class-decorator-requires-runtime-proof", with_files(("framework/ninja/schema_extra.py", decorator_support), ("framework/ninja/framework_error_schema.py", decorated_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-project-legacy-config-base-requires-runtime-proof", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/configs.py", legacy_config_support), ("framework/ninja/framework_error_schema.py", inherited_legacy_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-model-config-subscript-mutation-requires-runtime-proof", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/framework_error_schema.py", subscript_mutated_model_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-model-config-augmented-mutation-requires-runtime-proof", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/framework_error_schema.py", augmented_model_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-project-import-side-effect-requires-runtime-proof", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/configure_schema.py", imported_schema_mutator), ("framework/ninja/framework_error_schema.py", side_effect_import_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-common-class-project-import-side-effect-requires-runtime-proof", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/configure_schema.py", imported_schema_mutator), ("framework/ninja/framework_error_schema.py", nested_side_effect_import_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-common-module-direct-schema-mutation-blocked", with_files(("framework/ninja/framework_error_schema.py", direct_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-module-private-iife-schema-mutation-blocked", with_files(("framework/ninja/framework_error_schema.py", private_iife_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-common-module-private-deferred-mutation-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", private_deferred_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-common-module-private-parameter-iife-schema-mutation-blocked", with_files(("framework/ninja/framework_error_schema.py", private_parameter_iife_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-common-module-private-parameter-deferred-mutation-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", private_parameter_deferred_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-common-module-private-dunder-ior-schema-mutation-blocked", with_files(("framework/ninja/framework_error_schema.py", private_dunder_ior_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-module-private-dunder-init-schema-mutation-blocked", with_files(("framework/ninja/framework_error_schema.py", private_dunder_init_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-module-private-type-setattr-schema-mutation-blocked", with_files(("framework/ninja/framework_error_schema.py", private_type_setattr_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-module-private-config-alias-mutation-blocked", with_files(("framework/ninja/framework_error_schema.py", private_config_alias_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-module-private-bound-mutator-alias-blocked", with_files(("framework/ninja/framework_error_schema.py", private_bound_mutator_alias_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-module-private-named-lambda-invocation-blocked", with_files(("framework/ninja/framework_error_schema.py", private_named_lambda_schema_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-private-named-lambda-deferred-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", private_named_lambda_deferred_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-common-module-private-named-lambda-alias-invocation-blocked", with_files(("framework/ninja/framework_error_schema.py", private_named_lambda_alias_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-private-named-lambda-alias-deferred-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", private_named_lambda_alias_deferred_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-common-module-private-named-lambda-unpack-alias-invocation-blocked", with_files(("framework/ninja/framework_error_schema.py", private_named_lambda_unpack_alias_mutation_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-private-named-lambda-unpack-alias-deferred-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", private_named_lambda_unpack_alias_deferred_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-common-module-private-read-only-config-alias", with_files(("framework/ninja/framework_error_schema.py", private_read_only_config_alias_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-bc-project-import-side-effect-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/configure_error_out.py", bc_schema_mutator), ("application/lesson/driving_layer/api/bc_error_schema.py", side_effect_import_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-bc-class-project-import-side-effect-blocked", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/configure_error_out.py", bc_schema_mutator), ("application/lesson/driving_layer/api/bc_error_schema.py", nested_side_effect_import_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-inline-model-alias-callable-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", lambda_model_alias_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-inline-schema-extra-callable-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", lambda_schema_extra_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-inline-class-header-alias-callable-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", lambda_header_alias_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-inline-legacy-config-alias-callable-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", lambda_legacy_alias_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-inline-class-header-unpack-callable-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", lambda_header_unpack_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-inline-class-decorator-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", lambda_decorated_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-inline-model-config-mutation-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", lambda_mutated_model_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-common-executable-class-body-mutation-blocked", with_files(("framework/ninja/framework_error_schema.py", executable_class_body_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-common-dynamic-private-class-binding-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", dynamic_private_class_binding_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-common-dynamic-classvar-mutation-blocked", with_files(("framework/ninja/framework_error_schema.py", dynamic_classvar_binding_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-clean-common-static-private-class-binding-control", with_files(("framework/ninja/framework_error_schema.py", static_private_class_binding_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-common-static-symbol-classvar-control", with_files(("framework/ninja/framework_error_schema.py", static_symbol_classvar_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-analysis-common-dynamic-public-field-default-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", dynamic_public_field_default_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-common-pydantic-subclass-hook-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", pydantic_subclass_hook_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-clean-common-docstring-pass-control", with_files(("framework/ninja/framework_error_schema.py", declarative_class_body_control_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-bc-executable-class-body-blocked", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", executable_bc_class_body)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-bc-dynamic-classvar-binding-blocked", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", dynamic_bc_classvar_binding)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-clean-bc-static-classvar-control", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", static_bc_classvar_control)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-bc-static-symbol-classvar-control", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", static_symbol_bc_classvar_control)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-literal-model-config-schema-extra", with_files(("framework/ninja/framework_error_schema.py", literal_schema_extra_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-literal-class-header-schema-extra", with_files(("framework/ninja/framework_error_schema.py", literal_header_schema_extra_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-analysis-builtin-config-callable-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", builtin_callable_schema_extra_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-pydantic-alias-generator-in-schema-extra-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", pydantic_alias_generator_wrong_slot_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-builtin-default-factory-requires-runtime-proof", with_files(("framework/ninja/framework_error_schema.py", builtin_default_factory_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson)), "check-error-centralization.py", schema_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("schema-analysis-custom-alias-generator-unrelated-literal", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson), ("application/lesson/driving_layer/controller.py", custom_generator_unrelated_literal_controller)), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-analysis-custom-alias-generator-unknown-raw-typo", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", custom_generator_lesson), ("application/lesson/driving_layer/controller.py", custom_generator_typo_controller)), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-static-raw-wire-code-constructor", with_files(("application/lesson/driving_layer/controller.py", static_raw_controller)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-alias-path-nested-raw-wire-code", with_files(("framework/ninja/framework_error_schema.py", alias_path_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_lesson), ("application/lesson/driving_layer/controller.py", alias_path_raw_controller)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-clean-alias-path-nested-enum-member", with_files(("framework/ninja/framework_error_schema.py", alias_path_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_lesson), ("application/lesson/driving_layer/controller.py", alias_path_enum_controller)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-alias-path-unrelated-wire-literal", with_files(("framework/ninja/framework_error_schema.py", alias_path_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_lesson), ("application/lesson/driving_layer/controller.py", alias_path_unrelated_literal_controller)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-alias-choices-nested-raw-wire-code", with_files(("framework/ninja/framework_error_schema.py", alias_choices_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_choices_lesson), ("application/lesson/driving_layer/controller.py", alias_path_raw_controller)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-clean-alias-choices-nested-enum-member", with_files(("framework/ninja/framework_error_schema.py", alias_choices_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_choices_lesson), ("application/lesson/driving_layer/controller.py", alias_path_enum_controller)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-known-discriminator-raw-typo", with_files(("application/lesson/driving_layer/controller.py", known_typo_controller)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-known-discriminator-literal-kwargs-unpack", with_files(("application/lesson/driving_layer/controller.py", literal_unpack_controller)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-dynamic-kwargs-unpack", with_files(("application/lesson/driving_layer/controller.py", dynamic_unpack_controller)), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-alias-path-named-static-raw-wire-code", with_files(("framework/ninja/framework_error_schema.py", alias_path_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_lesson), ("application/lesson/driving_layer/controller.py", alias_path_named_static_raw_controller)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-clean-alias-path-named-enum-member", with_files(("framework/ninja/framework_error_schema.py", alias_path_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_lesson), ("application/lesson/driving_layer/controller.py", alias_path_named_enum_controller)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-analysis-alias-path-dynamic-payload", with_files(("framework/ninja/framework_error_schema.py", alias_path_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_lesson), ("application/lesson/driving_layer/controller.py", alias_path_dynamic_payload_controller)), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-alias-path-later-nested-unpack-raw-wire-code", with_files(("framework/ninja/framework_error_schema.py", alias_path_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_lesson), ("application/lesson/driving_layer/controller.py", alias_path_nested_unpack_raw_controller)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-bc-base-class-keyword-config", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("class LessonErrorSchema(FrameworkErrorSchema):", 'class LessonErrorSchema(FrameworkErrorSchema, extra="forbid"):', 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-class-decorator", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from dataclasses import dataclass\nfrom enum import StrEnum").replace("class LessonNotFoundError(LessonErrorSchema):", "@dataclass\nclass LessonNotFoundError(LessonErrorSchema):", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-decorator-proxy", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom pydantic import field_serializer").replace('    detail: str = "The lesson does not exist."', '    detail: str = "The lesson does not exist."\n    _serialize = field_serializer("detail")(lambda self, value: value)', 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-post-definition-model-rebuild", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT + "\nLessonErrorSchema.model_rebuild()\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case(
            "schema-clean-project-approved-custom-field-shape",
            with_files(
                ("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    CUSTOM_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-project-approved-default-nullable-alias-config-shape",
            with_files(
                ("framework/ninja/framework_error_schema.py", FLEXIBLE_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    FLEXIBLE_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-analysis-project-approved-common-validator-serializer-requires-runtime-proof",
            with_files(
                ("framework/ninja/framework_error_schema.py", DECORATED_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    CUSTOM_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            1,
            "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED",
        ),
        Case(
            "schema-clean-approved-static-alias-default-bindings",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    STATIC_CONSTANT_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    STATIC_CONSTANT_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-approved-annotated-defaults",
            with_files(
                ("framework/ninja/framework_error_schema.py", ANNOTATED_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    ANNOTATED_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-approved-typing-extensions-annotated-defaults",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    TYPING_EXTENSIONS_ANNOTATED_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    TYPING_EXTENSIONS_ANNOTATED_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-approved-common-legacy-config",
            with_files(
                ("framework/ninja/framework_error_schema.py", NESTED_CONFIG_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    CUSTOM_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-project-approved-repeated-alias-and-body-status-field",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    ALIASED_STATUS_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    ALIASED_STATUS_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-approved-defaulted-aliased-discriminator",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    DEFAULTED_ALIAS_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    DEFAULTED_ALIAS_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-clean-approved-required-nullable-discriminator",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    NULLABLE_DISCRIMINATOR_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    NULLABLE_DISCRIMINATOR_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-invalid-container-discriminator",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    CONTAINER_DISCRIMINATOR_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    CONTAINER_DISCRIMINATOR_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-invalid-different-static-field-alias-symbol",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    UNRESOLVED_ALIAS_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    UNRESOLVED_ALIAS_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-invalid-different-static-field-default-symbol",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    UNRESOLVED_DEFAULT_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    UNRESOLVED_DEFAULT_LESSON_ERROR_OUT,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-custom-discriminator-raw-string-constructor",
            with_files(
                ("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    CUSTOM_LESSON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/controller.py",
                    "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema\n\n"
                    "def get_lesson(request):\n"
                    "    return LessonErrorSchema(error_type='lesson_not_found', msg='missing', is_show=True)\n",
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-custom-discriminator-raw-string-assignment",
            with_files(
                ("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    CUSTOM_LESSON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/controller.py",
                    "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError\n\n"
                    "def get_lesson(request):\n"
                    "    error = LessonNotFoundError()\n"
                    "    error.error_type = 'lesson_not_found'\n"
                    "    return error\n",
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-fresh-clean-concrete-code-annotation-exact",
            with_files(
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    broadened_concrete_code_annotation,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-fresh-invalid-child-model-config-binding",
            with_files(
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    benign_indirect_model_config,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-fresh-invalid-private-model-config-alias-binding",
            with_files(
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    indirect_alias_model_config,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-invalid-child-legacy-config",
            with_files(
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    LESSON_ERROR_OUT.replace(
                        "class LessonErrorSchema(FrameworkErrorSchema):\n    code: LessonErrorCode",
                        "class LessonErrorSchema(FrameworkErrorSchema):\n"
                        "    code: LessonErrorCode\n\n"
                        "    class Config:\n"
                        "        populate_by_name = True",
                    ),
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
                    "application/lesson/driving_layer/nested.py",
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
                    "application/lesson/driving_layer/nested.py",
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
                    "application/lesson/driving_layer/controller.py",
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
                    "application/lesson/driving_layer/controller.py",
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
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
                    "application/lesson/driving_layer/controller.py",
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
                    "application/lesson/driving_layer/controller.py",
                    unshadowed_constructor_expressions,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case("schema-clean-common-base-and-two-concrete", BASE_FILES, "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-empty-error-bc", common_only, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/driving_layer/controller.py", "--scope-bc", "lesson", "--project-code-error-module", "framework/ninja/framework_error_schema.py"), 0, ""),
        Case("schema-clean-no-error-bc-in-scope", no_error_bc, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/catalog/driving_layer/controller.py", "--scope-bc", "catalog", "--project-code-error-module", "framework/ninja/framework_error_schema.py"), 0, ""),
        Case("schema-clean-same-profile-common-enum-reuse-v1", reused_surfaces, "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-same-profile-common-enum-reuse-v2", reused_surfaces, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v2", "--api-module", "config/api_v2.py", "--controller-module", "application/lesson/driving_layer/controller_v2.py", "--scope-bc", "lesson", "--error-bc", "lesson", "--project-code-error-module", "framework/ninja/framework_error_schema.py", "--project-code-error-module", "application/lesson/driving_layer/api/bc_error_schema.py"), 0, ""),
        Case("schema-clean-canonical-looking-preserve-excluded", preserve, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "preserve-established", "--scope", "legacy", "--api-module", "legacy/api.py", "--controller-module", "legacy/controller.py", "--scope-bc", "legacy", "--error-bc", "legacy", "--project-code-error-module", "framework/ninja/framework_error_schema.py", "--project-preserve-error-module", "legacy/errors.py"), 0, ""),
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
            with_files(("framework/ninja/framework_error_schema.py", "class Broken(:\n")),
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
                "application/legacy/driving_layer/api/bc_error_schema.py",
            ),
            0,
            "",
        ),
        Case(
            "schema-clean-unprefixed-wire-code",
            with_files(
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
        Case("schema-missing-designated-error-bc-artifact", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", "<REMOVE>")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-init-missing", with_files(("framework/ninja/__init__.py", "<REMOVE>")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-error-out-missing", with_files(("framework/ninja/framework_error_schema.py", "<REMOVE>")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        # #414·#417 — framework/ninja/ 는 공유 <technology> 폴더다: 오류 계약 밖 <module>.py 는 허용
        # (옛 response/ 전용 패키지의 extra 금지는 패키지 소멸과 함께 걷었다 — 2026-08-12 리뷰).
        Case("schema-framework-ninja-extra-module-allowed", with_files(("framework/ninja/helper.py", "def make_error(): pass\n")), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-common-concrete-error", with_files(("framework/ninja/framework_error_schema.py", COMMON_ERROR_OUT + "\nclass GlobalNotFound(FrameworkErrorSchema):\n    pass\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-outside-canonical-module", with_files(("application/lesson/driving_layer/api/not_found.py", "from .bc_error_schema import LessonErrorSchema\nclass Other(LessonErrorSchema): pass\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-missing-enum", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", missing_enum)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-duplicate-enum", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT + "\nclass OtherErrorCode(StrEnum):\n    BAD = 'bad'\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-missing-base", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", missing_base)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-duplicate-base", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT + "\nclass AnotherErrorOut(FrameworkErrorSchema):\n    code: LessonErrorCode\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-extra-defaulted-field", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("    code: LessonErrorCode\n", "    code: LessonErrorCode\n    retryable: bool = False\n", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-wrong-inheritance", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("class LessonErrorSchema(FrameworkErrorSchema):", "class LessonErrorSchema:"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-extra-field", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("    detail: str = \"The lesson does not exist.\"", "    detail: str = \"The lesson does not exist.\"\n    retry_after: int = 1"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-validator", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom pydantic import field_validator").replace("    detail: str = \"The lesson does not exist.\"", "    detail: str = \"The lesson does not exist.\"\n\n    @field_validator('status')\n    @classmethod\n    def validate_status(cls, value: int) -> int:\n        return value"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-private-field-serializer", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom pydantic import field_serializer").replace("    detail: str = \"The lesson does not exist.\"", "    detail: str = \"The lesson does not exist.\"\n\n    @field_serializer('detail')\n    def _serialize_detail(self, value: str) -> str:\n        return value", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-private-computed-field", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom pydantic import computed_field").replace("class LessonErrorSchema(FrameworkErrorSchema):\n    code: LessonErrorCode", "class LessonErrorSchema(FrameworkErrorSchema):\n    code: LessonErrorCode\n\n    @computed_field\n    @property\n    def _wire_hint(self) -> str:\n        return 'hint'"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-field-alias", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom pydantic import Field").replace("title: str = \"Lesson not found\"", "title: str = Field(alias='message', default='Lesson not found')"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-field-type-drift", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("title: str = \"Lesson not found\"", "title: int = 1", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-field-metadata-drift", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom pydantic import Field").replace("title: str = \"Lesson not found\"", "title: str = Field(default='Lesson not found', exclude=True)", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-default-kind-drift", with_files(("framework/ninja/framework_error_schema.py", DEFAULTED_ALIAS_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", DEFAULTED_ALIAS_LESSON_ERROR_OUT.replace("default=LessonErrorCode.NOT_FOUND,", "default_factory=lambda: LessonErrorCode.NOT_FOUND,", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-annotated-default-wire-drift", with_files(("framework/ninja/framework_error_schema.py", ANNOTATED_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", ANNOTATED_LESSON_ERROR_OUT.replace("Field(default=LessonErrorCode.NOT_FOUND, alias=\"type\")", "Field(default=LessonErrorCode.CONFLICT, alias=\"type\")", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-imported-string-default-is-not-enum", with_files(("application/lesson/constants.py", "DEFAULT_ID = 'lesson_not_found'\n"), ("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT.replace("from ninja import Schema", "from ninja import Schema\nfrom application.lesson.constants import DEFAULT_ID").replace("error_type: str", "error_type: str = DEFAULT_ID")), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom application.lesson.constants import DEFAULT_ID").replace("class LessonErrorSchema(FrameworkErrorSchema):\n    error_type: LessonErrorCode", "class LessonErrorSchema(FrameworkErrorSchema):\n    error_type: LessonErrorCode = DEFAULT_ID"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        # 승인 canon(2026-08-15) 양방향 고정 — 식별자 field 를 ErrorCode 로 «정확히» 좁히며
        # 공통 default 를 잃어 required 가 되는 모양만 pass 이고, 그 밖의 required/default·
        # annotation·타 field 변화는 계속 BLOCKER 다(과면제 가드).
        Case("schema-clean-base-narrowed-discriminator-drops-common-default", with_files(("framework/ninja/framework_error_schema.py", DEFAULTED_ALIAS_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", DEFAULTED_ALIAS_LESSON_ERROR_OUT.replace("        default=LessonErrorCode.NOT_FOUND,\n", "", 1))), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-base-narrowed-plain-defaulted-discriminator-to-required", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT.replace("error_type: str", 'error_type: str = "about:blank"')), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT)), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-base-drops-default-and-nullability", with_files(("framework/ninja/framework_error_schema.py", NULLABLE_DISCRIMINATOR_COMMON_ERROR_OUT.replace("error_type: str | None", "error_type: str | None = None")), ("application/lesson/driving_layer/api/bc_error_schema.py", NULLABLE_DISCRIMINATOR_LESSON_ERROR_OUT.replace("    error_type: LessonErrorCode | None\n", "    error_type: LessonErrorCode\n", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-other-field-drops-common-default", with_files(("framework/ninja/framework_error_schema.py", FLEXIBLE_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", FLEXIBLE_LESSON_ERROR_OUT.replace("class LessonErrorSchema(FrameworkErrorSchema):\n    error_type: LessonErrorCode\n", "class LessonErrorSchema(FrameworkErrorSchema):\n    error_type: LessonErrorCode\n    msg: str\n", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-missing-default", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("    detail: str = \"The lesson does not exist.\"", "    detail: str"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-raw-string-code", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("code: LessonErrorCode = LessonErrorCode.NOT_FOUND", "code: str = 'lesson_not_found'"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-project-duplicate-wire-code-across-bcs", duplicate_project_code, "check-error-centralization.py", schema_args("--scope-bc", "catalog", "--error-bc", "catalog", "--project-code-error-module", "application/catalog/driving_layer/api/bc_error_schema.py"), 2, "BLOCKER"),
        Case("schema-literal-code", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom typing import Literal").replace("code: LessonErrorCode", "code: Literal['lesson_not_found']", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-str-code", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("code: LessonErrorCode", "code: str", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case(
            "schema-concrete-missing-dynamic-required-default",
            with_files(
                ("framework/ninja/framework_error_schema.py", DYNAMIC_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    missing_dynamic_default,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-common-init-reexport-allowed",
            with_files(
                (
                    "framework/ninja/__init__.py",
                    "from .framework_error_schema import FrameworkErrorSchema\n",
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
        ),
        Case(
            "schema-common-helper",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    COMMON_ERROR_OUT + "\ndef make_error():\n    return FrameworkErrorSchema\n",
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
                    "framework/ninja/framework_error_schema.py",
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
                    "framework/ninja/framework_error_schema.py",
                    COMMON_ERROR_OUT
                    + "\nclass FrameworkErrorSchema(Schema):\n"
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
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    foreign_enum_default,
                ),
                (
                    "application/catalog/driving_layer/api/bc_error_schema.py",
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
                "application/catalog/driving_layer/api/bc_error_schema.py",
            ),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-raw-string-code-selected-controller",
            with_files(
                (
                    "application/lesson/driving_layer/controller.py",
                    raw_string_controller,
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            2,
            "BLOCKER",
        ),
        Case(
            "schema-untracked-framework-ninja-module-allowed",
            with_files(
                (
                    "framework/ninja/helper.py",
                    "def make_error(): pass\n",
                ),
            ),
            "check-error-centralization.py",
            schema_args(),
            0,
            "",
            baseline_files=BASE_FILES,
        ),
        Case("schema-analysis-syntax", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", "class Broken(:\n")), "check-error-centralization.py", schema_args(), 2, "파싱하지"),
        Case(
            "schema-analysis-dynamic-enum-value",
            with_files(
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
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
                "application/lesson/driving_layer/api/bc_error_schema.py",
            ),
            1,
            "사용 오류",
            allowed_arg_issues=frozenset(
                {"duplicate:--project-code-error-module"}
            ),
        ),
        Case("schema-analysis-root-escape", BASE_FILES, "check-error-centralization.py", schema_args("--project-code-error-module", "../outside.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--project-code-error-module"})),
        Case("schema-analysis-unresolved-base", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from framework.ninja.framework_error_schema import FrameworkErrorSchema", "from missing import FrameworkErrorSchema"))), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-analysis-missing-source", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--project-code-error-module", "application/lesson/driving_layer/api/bc_error_schema.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--scope", "missing:--api-module", "missing:--controller-module", "missing:--scope-bc"})),
        Case("schema-analysis-missing-inventory", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/driving_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--project-code-error-module"})),
        Case("schema-analysis-missing-selected-error-module-path", BASE_FILES, "check-error-centralization.py", schema_args("--project-code-error-module", "application/lesson/driving_layer/api/missing_error_out.py"), 1, "사용 오류"),
        Case("schema-analysis-error-bc-not-subset", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/driving_layer/controller.py", "--scope-bc", "catalog", "--error-bc", "lesson", "--project-code-error-module", "framework/ninja/framework_error_schema.py", "--project-code-error-module", "application/lesson/driving_layer/api/bc_error_schema.py"), 1, "사용 오류"),
        Case("schema-analysis-candidate-absent-from-inventory", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/driving_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson", "--project-code-error-module", "framework/ninja/framework_error_schema.py"), 1, "사용 오류"),
        Case("schema-analysis-module-in-both-inventories", BASE_FILES, "check-error-centralization.py", schema_args("--project-preserve-error-module", "application/lesson/driving_layer/api/bc_error_schema.py"), 1, "사용 오류"),
        Case("schema-analysis-auto-profile", BASE_FILES, "check-error-centralization.py", AUTO_PROFILE_ARGS, 0, ""),
        Case("schema-analysis-missing-profile-args", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--error-profile", "missing:--api-module", "missing:--controller-module", "missing:--scope-bc", "missing:--project-code-error-module"})),
        Case("schema-fp-tests-migrations-docstrings-logs", with_files(("application/lesson/tests/test_codes.py", "code = 'lesson_not_found'\n"), ("application/lesson/migrations/0001_initial.py", "code = 'lesson_not_found'\n"), ("application/lesson/driving_layer/log.py", "import logging\nlogger = logging.getLogger(__name__)\n'''code = lesson_not_found'''\nlogger.info('code=%s', 'lesson_not_found')\n")), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-fp-classvar-private-import-alias", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", LESSON_ERROR_OUT.replace("from enum import StrEnum", "from enum import StrEnum\nfrom typing import ClassVar").replace("class LessonErrorSchema(FrameworkErrorSchema):\n    code: LessonErrorCode", "class LessonErrorSchema(FrameworkErrorSchema):\n    _cache: ClassVar[dict] = {}\n    code: LessonErrorCode"))), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-fp-relative-import-local-assignment-ignored-cache", with_files(("application/lesson/driving_layer/api/alias.py", "from .error_out import LessonErrorSchema as Error\nvalue = Error\n"), (".cache/generated.py", "code = 'ignored'\n"), ("__pycache__/bad.py", "code = 'ignored'\n")), "check-error-centralization.py", schema_args(), 0, ""),
        # Reviewer gap: whether the inventory is semantically complete and whether a
        # public code should exist cannot be inferred from source shape alone.
    ]


def controller_cases() -> list[Case]:
    """Controller shape cases; the checker is intentionally absent at this RED stage."""
    clean_sync_annassign = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "lesson = get_lesson(lesson_id)",
        "lesson: dict = get_lesson(lesson_id)",
    )
    clean_async = (
        CONTROLLER_FILES["application/lesson/driving_layer/controller.py"]
        .replace("def get_lesson_controller", "async def get_lesson_controller")
        .replace("lesson = get_lesson(lesson_id)", "await get_lesson(lesson_id)")
        .replace("    return lesson\n", "    return {'ok': True}\n")
    )
    clean_tuple = (
        CONTROLLER_FILES["application/lesson/driving_layer/controller.py"]
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
from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError

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
        ("application/lesson/driving_layer/api/bc_error_schema.py", "<REMOVE>"),
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
        CONTROLLER_FILES["application/lesson/driving_layer/controller.py"]
        .replace(
            "LessonNotFoundError()",
            "LessonErrorSchema(code=LessonErrorCode.NOT_FOUND, title='missing', "
            "status=404, detail='missing', trace_id='lesson-missing')",
        )
        .replace("404: LessonNotFoundError", "404: LessonErrorSchema")
        .replace("from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError", "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema")
    )
    direct_base_extra_field = direct_base.replace(
        "trace_id='lesson-missing')",
        "trace_id='lesson-missing', retryable=False)",
    )
    direct_base_omits_defaulted_fields = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorSchema})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        error = LessonErrorSchema(errorType=LessonErrorCode.NOT_FOUND)
        return Status(404, error)
    return lesson
"""
    direct_base_missing_required_field = direct_base_omits_defaulted_fields.replace(
        "LessonErrorSchema(errorType=LessonErrorCode.NOT_FOUND)",
        "LessonErrorSchema()",
    )
    relative_alias_controller = """from ninja import Router, Status as ApiStatus
from ..application_layer.use_cases import LessonMissing as MissingLesson, get_lesson as load_lesson
from .api.bc_error_schema import LessonNotFoundError as MissingLessonOut

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
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from ninja import Router, Status\nfrom .transport import emit",
    )
    serializer_helper = """from django.http import JsonResponse
from .api.bc_error_schema import LessonErrorSchema


def emit(value: LessonErrorSchema):
    return JsonResponse(value.model_dump(), status=value.status)
"""
    mapping_controller = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from ninja import Router, Status\nfrom .bridge import convert",
    )
    mapping_helper = """from application.lesson.application_layer.use_cases import LessonMissing
from .api.bc_error_schema import LessonNotFoundError


def convert(value):
    if isinstance(value, LessonMissing):
        return LessonNotFoundError()
    return None
"""
    forwarded_exception = (
        CONTROLLER_FILES["application/lesson/driving_layer/controller.py"]
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
        CONTROLLER_FILES["application/lesson/driving_layer/controller.py"]
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
        "application/lesson/driving_layer/controller.py"
    ] + """

def registered_handler(request, exc):
    return None


router.add_exception_handler(LessonMissing, registered_handler)
"""
    bare_catch = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace("except LessonMissing:", "except:")
    tuple_base_exception = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "except LessonMissing:",
        "except (LessonMissing, BaseException):",
    )
    explicit_reraise = (
        CONTROLLER_FILES["application/lesson/driving_layer/controller.py"]
        .replace("except LessonMissing:", "except LessonMissing as exc:")
        .replace(
            "error = LessonNotFoundError()\n        return Status(error.status, error)",
            "raise exc",
        )
    )
    hardcoded_status = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "return Status(error.status, error)",
        "return Status(404, error)",
    )
    match_status_capture = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "    try:\n",
        "    match lesson_id:\n"
        "        case Status if enabled:\n"
        "            pass\n"
        "    try:\n",
    )
    match_error_out_capture = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "    try:\n",
        "    match values:\n"
        "        case [*LessonNotFoundError] if enabled:\n"
        "            pass\n"
        "    try:\n",
    )
    match_exception_capture = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "    try:\n",
        "    match values:\n"
        "        case {'value': captured, **LessonMissing} if enabled:\n"
        "            pass\n"
        "    try:\n",
    )
    match_unrelated_capture = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "    try:\n",
        "    match values:\n"
        "        case {'value': captured, **rest} if enabled:\n"
        "            pass\n"
        "    try:\n",
    )
    class_body_classvar_common = DYNAMIC_COMMON_ERROR_OUT.replace(
        "class FrameworkErrorSchema(Schema):\n",
        "class FrameworkErrorSchema(Schema):\n"
        "    from typing import ClassVar as Metadata\n"
        "    registry: Metadata[dict] = {}\n",
    )
    module_classvar_common = DYNAMIC_COMMON_ERROR_OUT.replace(
        "from ninja import Schema",
        "from ninja import Schema\nfrom typing import ClassVar as Metadata",
    ).replace(
        "class FrameworkErrorSchema(Schema):\n",
        "class FrameworkErrorSchema(Schema):\n    registry: Metadata[dict] = {}\n",
    )
    direct_base_passes_classvar = direct_base.replace(
        "trace_id='lesson-missing')",
        "trace_id='lesson-missing', registry={})",
    )
    function_handler_call = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ] + """


def install_handlers():
    router.add_exception_handler(LessonMissing, registered_handler)
"""
    nested_handler_decorator = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ] + """


def install_handlers():
    @router.exception_handler(LessonMissing)
    def registered_handler(request, exc):
        return None
    return registered_handler
"""
    conditional_handler_call = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ] + """


if handlers_enabled:
    router.add_exception_handler(LessonMissing, registered_handler)
"""
    class_method_handler_call = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ] + """


class Installer:
    def install(self):
        router.add_exception_handler(LessonMissing, registered_handler)
"""
    arbitrary_handler_receiver = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
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
from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError

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
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorSchema})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing as exc:
        error = LessonErrorSchema(
            code=LessonErrorCode.NOT_FOUND,
            title='missing',
            status=404,
            detail=(lambda: exc),
        )
        return Status(error.status, error)
    return lesson
"""
    temporal_serializer_helper = """from django.http import JsonResponse
from .api.bc_error_schema import LessonErrorCode, LessonErrorSchema


def emit(value):
    response = JsonResponse(value.model_dump(), status=200)
    value = LessonErrorSchema(
        code=LessonErrorCode.NOT_FOUND,
        title='missing',
        status=404,
        detail='missing',
    )
    return response
"""
    temporal_serializer_controller = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError
from application.lesson.driving_layer.transport import emit

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
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from ninja import Router, Status\nfrom .assembler import assemble",
    )
    nested_prepared_factory = """from .api.bc_error_schema import LessonNotFoundError


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
        "application/lesson/driving_layer/controller.py"
    ] + """


def registered_handler(request, exc):
    return None


if True:
    branch_router = Router()
branch_router.add_exception_handler(LessonMissing, registered_handler)
"""
    ambiguous_branch_handler = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ] + """


def registered_handler(request, exc):
    return None


if handlers_enabled:
    selected_receiver = Router()
selected_receiver.add_exception_handler(LessonMissing, registered_handler)
"""
    arbitrary_branch_handler = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
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
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema
from application.lesson.driving_layer.forwarder import forward_error

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorSchema})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing as exc:
        error = LessonErrorSchema(
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
from .api.bc_error_schema import LessonNotFoundError


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
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from ninja import Router, Status\nfrom .transport import maybe_emit",
    )
    operation_nested_factory = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
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
    local_class_factory = """from .api.bc_error_schema import LessonNotFoundError


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
    direct_aliased_base_controller = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorSchema})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        error = LessonErrorSchema(type=LessonErrorCode.NOT_FOUND, http_status=404, msg='missing')
        return Status(error.http_status, error)
    return lesson
"""
    direct_custom_base_controller = """from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorSchema})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        error = LessonErrorSchema(error_type=LessonErrorCode.NOT_FOUND, msg='missing', is_show=True)
        return Status(404, error)
    return lesson
"""
    direct_nullable_omission_controller = direct_custom_base_controller.replace(
        "error_type=LessonErrorCode.NOT_FOUND, msg='missing', is_show=True",
        "msg='missing'",
    )
    validate_alias_false_common = """from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    is_show: bool = True
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=False)
"""
    dynamic_config_common = """from ninja import Schema
from framework.ninja.configs import build_config


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    is_show: bool = True
    model_config = build_config()
"""
    dynamic_config_support = """from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


def build_config():
    return ConfigDict(alias_generator=to_camel)
"""
    shadowed_config_builder_support = dynamic_config_support + """

build_config = lambda: ConfigDict(validate_by_name=True)
"""
    rebound_config_global_support = dynamic_config_support + """

to_camel = lambda value: f'wire_{value}'
"""
    indirectly_shadowed_config_builder_support = dynamic_config_support + """

globals()['build_config'] = lambda: ConfigDict(
    alias_generator=lambda value: f'actual_{value}'
)
"""
    namedexpr_shadowed_config_builder_support = dynamic_config_support + """

shadow = (
    build_config := lambda: ConfigDict(
        alias_generator=lambda value: f'actual_{value}'
    )
)
"""
    while_shadowed_config_builder_support = dynamic_config_support + """

while True:
    build_config = lambda: ConfigDict(
        alias_generator=lambda value: f'actual_{value}'
    )
    break
"""
    async_shadowed_config_builder_support = dynamic_config_support + """

async def build_config():
    return ConfigDict(alias_generator=lambda value: f'actual_{value}')
"""
    dynamic_config_generated_controller = direct_custom_base_controller.replace(
        "error_type=", "errorType="
    ).replace("is_show=", "isShow=")
    custom_prepared_controller = CUSTOM_CONTROLLER
    static_module_status_controller = CUSTOM_CONTROLLER.replace(
        "router = Router()",
        "router = Router()\nERROR_STATUS = 404",
    ).replace("Status(404, error)", "Status(ERROR_STATUS, error)")
    alias_priority_common = """from ninja import Schema
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel


class FrameworkErrorSchema(Schema):
    error_type: str = Field(alias='kind', alias_priority=1)
    msg: str
    is_show: bool = True
    model_config = ConfigDict(alias_generator=to_camel)
"""
    alias_priority_controller = direct_custom_base_controller.replace(
        "error_type=LessonErrorCode.NOT_FOUND",
        "errorType=LessonErrorCode.NOT_FOUND",
    ).replace(", is_show=True", "")
    deprecated_population_common = """from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    error_type: str = Field(alias='type')
    msg: str
    is_show: bool = True

    class Config:
        allow_population_by_field_name = True
"""
    direct_undefined_common = """from ninja import Schema
from pydantic_core import PydanticUndefined as Undefined


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str = Undefined
"""
    direct_ellipsis_common = direct_undefined_common.replace(
        "msg: str = Undefined",
        "msg: str = ...",
    )
    direct_required_lesson = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = 'lesson_not_found'


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = LessonErrorCode.NOT_FOUND
"""
    direct_required_omission_controller = direct_custom_base_controller.replace(
        "error_type=LessonErrorCode.NOT_FOUND, msg='missing', is_show=True",
        "error_type=LessonErrorCode.NOT_FOUND",
    )
    alias_none_common = CUSTOM_COMMON_ERROR_OUT.replace(
        "from ninja import Schema",
        "from ninja import Schema\nfrom pydantic import Field",
    ).replace("error_type: str", "error_type: str = Field(alias=None)")
    validation_alias_none_common = alias_none_common.replace(
        "Field(alias=None)",
        "Field(validation_alias=None)",
    )
    two_field_direct = direct_custom_base_controller.replace(", is_show=True", "")
    repeated_config_common = """from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(alias_generator=to_camel)
    model_config = ConfigDict(validate_by_name=True)
"""
    repeated_config_generated = two_field_direct.replace("error_type=", "errorType=")
    header_override_common = repeated_config_common.replace(
        "class FrameworkErrorSchema(Schema):",
        "class FrameworkErrorSchema(Schema, alias_generator=None):",
    ).replace("    model_config = ConfigDict(validate_by_name=True)\n", "")
    field_merge_common = """from typing import Annotated
from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    error_type: Annotated[
        str,
        Field(validation_alias='legacyType'),
        Field(alias='wireType'),
    ]
    msg: str
"""
    field_merge_wire = two_field_direct.replace("error_type=", "wireType=")
    field_merge_legacy = two_field_direct.replace("error_type=", "legacyType=")
    alias_clear_common = """from typing import Annotated
from ninja import Schema
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel


class FrameworkErrorSchema(Schema):
    error_type: Annotated[str, Field(alias='wireType'), Field(alias=None)]
    msg: str
    model_config = ConfigDict(alias_generator=to_camel)
"""
    nested_alias_common = """from typing import Annotated
from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    error_type: Annotated[
        Annotated[str, Field(alias='innerType')],
        Field(alias='outerType'),
    ]
    msg: str
"""
    alias_path_controller_common = """from ninja import Schema
from pydantic import AliasPath, Field


class FrameworkErrorSchema(Schema):
    error_type: str = Field(validation_alias=AliasPath('payload', 'kind'))
    msg: str
"""
    alias_path_controller_bc = """from enum import StrEnum
from pydantic import AliasPath, Field
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = 'lesson_not_found'


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode = Field(validation_alias=AliasPath('payload', 'kind'))


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = Field(
        default=LessonErrorCode.NOT_FOUND,
        validation_alias=AliasPath('payload', 'kind'),
    )
    msg: str = 'missing'
"""
    alias_path_controller = two_field_direct.replace(
        "error_type=LessonErrorCode.NOT_FOUND, msg='missing'",
        "payload={'kind': LessonErrorCode.NOT_FOUND}, msg='missing'",
    )
    alias_path_raw_controller = alias_path_controller.replace(
        "LessonErrorCode.NOT_FOUND", "'lesson_not_found'", 1
    )
    alias_path_dynamic_controller = alias_path_controller.replace(
        "def get_lesson_controller(request, lesson_id: int):",
        "def get_lesson_controller(request, lesson_id: int, payload):",
    ).replace("payload={'kind': LessonErrorCode.NOT_FOUND}", "payload=payload")
    custom_generator_explicit_common = """from ninja import Schema
from pydantic import ConfigDict, Field
from framework.ninja.aliasing import wire_name


class FrameworkErrorSchema(Schema):
    error_type: str = Field(validation_alias='kind')
    msg: str = Field(validation_alias='message')
    model_config = ConfigDict(alias_generator=wire_name)
"""
    custom_generator_explicit_controller = two_field_direct.replace(
        "error_type=", "kind="
    ).replace("msg=", "message=")
    custom_generator_common = """from ninja import Schema
from pydantic import ConfigDict
from framework.ninja.aliasing import wire_name


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    model_config = ConfigDict(alias_generator=wire_name)
"""
    custom_generator_controller = two_field_direct.replace(
        "error_type=", "wire_error_type="
    ).replace("msg=", "wire_msg=")
    custom_generator_handler_controller = custom_generator_controller.replace(
        "router = Router()\n",
        "router = Router()\n\n\n"
        "@router.exception_handler(LessonMissing)\n"
        "def custom_error_handler(request, exc):\n"
        "    return None\n",
    )
    custom_generator_typo_controller = custom_generator_controller.replace(
        "wire_error_type=", "wire_error_typo="
    )
    complex_generator_support = """def wire_name(value: str) -> str:
    if value.startswith('_'):
        return value
    return f'wire_{value}'
"""
    repr_generator_support = """def wire_name(value: str) -> str:
    return f'wire_{value!r}'
"""
    shadowed_generator_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


wire_name = lambda value: f'actual_{value}'
"""
    indirectly_shadowed_generator_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


globals()['wire_name'] = lambda value: f'actual_{value}'
"""
    namedexpr_shadowed_generator_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


shadow = (wire_name := lambda value: f'actual_{value}')
"""
    try_shadowed_generator_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


try:
    wire_name = lambda value: f'actual_{value}'
except Exception:
    pass
"""
    async_shadowed_generator_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


async def wire_name(value: str) -> str:
    return f'actual_{value}'
"""
    star_shadowed_generator_support = """def Field(value: str) -> str:
    return f'wire_{value}'


from pydantic import *
"""
    star_shadowed_generator_common = custom_generator_common.replace(
        "wire_name", "Field"
    )
    set_call_shadowed_generator_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


def set():
    globals()['wire_name'] = lambda value: f'actual_{value}'


shadow = set()
"""
    iterator_shadowed_generator_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


from framework.ninja.mutator import EVIL

for _ in EVIL:
    pass
"""
    iterator_mutator_support = """import sys


class Evil:
    def __iter__(self):
        target = sys.modules['framework.ninja.aliasing']
        target.wire_name = lambda value: f'actual_{value}'
        return iter(())


EVIL = Evil()
"""
    pure_generator_module_control = """'pure alias helper module'

__all__ = ['wire_name']
MARKER = 'stable'


def wire_name(value: str) -> str:
    return f'wire_{value}'
"""
    status_string_field_controller = CUSTOM_CONTROLLER.replace(
        "Status(404, error)", "Status(error.msg, error)"
    )
    digit_camel_common = """from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class FrameworkErrorSchema(Schema):
    error2type: str
    msg: str
    model_config = ConfigDict(alias_generator=to_camel)
"""
    digit_camel_bc = CUSTOM_LESSON_ERROR_OUT.replace("error_type", "error2type")
    digit_camel_controller = two_field_direct.replace("error_type=", "error2Type=")
    nested_required_common = """from typing import Annotated
from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: Annotated[
        Annotated[str, Field(default_factory=str)],
        Field(default_factory=None),
    ]
"""
    nested_optional_common = nested_required_common.replace(
        "Annotated[str, Field(default_factory=str)],\n        Field(default_factory=None)",
        "Annotated[str, Field(default_factory=None)],\n        Field(default_factory=str)",
    )
    omitted_msg_controller = two_field_direct.replace(", msg='missing'", "")
    explicit_config_common = """from ninja import Schema
from pydantic import ConfigDict, Field


class FrameworkErrorSchema(Schema):
    error_type: str = Field(alias='kind')
    msg: str
    model_config = ConfigDict(validate_by_name=False, populate_by_name=True)
"""
    explicit_config_alias_controller = two_field_direct.replace("error_type=", "kind=")
    explicit_true_common = explicit_config_common.replace(
        "validate_by_name=False, populate_by_name=True",
        "validate_by_name=True, populate_by_name=False",
    )
    negative_alias_priority_common = alias_priority_common.replace(
        "alias_priority=1", "alias_priority=-1"
    )
    none_alias_priority_common = alias_priority_common.replace(
        "alias_priority=1", "alias_priority=None"
    )
    none_alias_priority_controller = two_field_direct.replace("error_type=", "kind=")
    nullable_status_common = CUSTOM_COMMON_ERROR_OUT.replace(
        "    is_show: bool\n", "    is_show: bool\n    response_code: int | None\n"
    )
    nullable_status_lesson = CUSTOM_LESSON_ERROR_OUT.replace(
        "    is_show: bool = True\n",
        "    is_show: bool = True\n    response_code: int | None = 404\n",
    )
    nullable_status_controller = CUSTOM_CONTROLLER.replace(
        "Status(404, error)", "Status(error.response_code, error)"
    )
    literal_status_common = nullable_status_common.replace(
        "int | None", "Literal[404]"
    ).replace("from ninja import Schema", "from typing import Literal\nfrom ninja import Schema")
    literal_status_lesson = nullable_status_lesson.replace(
        "int | None", "Literal[404]"
    ).replace("from enum import StrEnum", "from enum import StrEnum\nfrom typing import Literal")
    computed_status_common = """from ninja import Schema
from pydantic import computed_field


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str

    @computed_field
    @property
    def transport_code(self) -> int:
        return 404
"""
    computed_status_controller = two_field_direct.replace(
        "Status(404, error)", "Status(error.transport_code, error)"
    )
    plain_computed_status_common = computed_status_common.replace(
        "    @property\n", ""
    )
    cached_computed_status_common = computed_status_common.replace(
        "from ninja import Schema",
        "from functools import cached_property\nfrom ninja import Schema",
    ).replace("    @property", "    @cached_property")
    controller_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    LessonErrorSchema.model_config.update(\n"
        "        alias_generator=lambda value: f'wire_{value}',\n"
        "        validate_by_name=True,\n"
        "    )\n"
        "    LessonErrorSchema.model_rebuild(force=True)\n"
        "    try:",
    )
    controller_aliased_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    error_config = LessonErrorSchema.model_config\n"
        "    error_config.update(\n"
        "        alias_generator=lambda value: f'wire_{value}',\n"
        "        validate_by_name=True,\n"
        "    )\n"
        "    rebuild_error_model = LessonErrorSchema.model_rebuild\n"
        "    rebuild_error_model(force=True)\n"
        "    try:",
    )
    controller_business_config_alias_control = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    request_options = request.options\n"
        "    request_options.update({'trace': True})\n"
        "    try:",
    )
    controller_read_only_model_config_control = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    config_snapshot = LessonErrorSchema.model_config\n"
        "    config_title = config_snapshot.get('title')\n"
        "    try:",
    )
    controller_module_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "router = Router()",
        "LessonErrorSchema.model_config.update(\n"
        "    alias_generator=lambda value: f'wire_{value}',\n"
        "    validate_by_name=True,\n"
        ")\n"
        "LessonErrorSchema.model_rebuild(force=True)\n\n"
        "router = Router()",
    )
    controller_module_setattr_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "router = Router()",
        "setattr(LessonErrorSchema, 'model_config', {'extra': 'forbid'})\n\nrouter = Router()",
    )
    controller_local_delattr_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    delattr(LessonErrorSchema, 'model_config')\n"
        "    try:",
    )
    controller_aliased_schema_setattr_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    error_model = LessonErrorSchema\n"
        "    setattr(error_model, 'model_config', {'extra': 'forbid'})\n"
        "    try:",
    )
    controller_module_qualified_setattr_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError\n"
        "import application.lesson.driving_layer.api.bc_error_schema as error_models",
    ).replace(
        "router = Router()",
        "setattr(error_models.LessonErrorSchema, 'model_config', {'extra': 'forbid'})\n\n"
        "router = Router()",
    )
    controller_aliased_builtin_setattr_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from builtins import setattr as replace_attribute\nfrom ninja import Router, Status",
    ).replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "router = Router()",
        "replace_attribute(LessonErrorSchema, 'model_config', {'extra': 'forbid'})\n\n"
        "router = Router()",
    )
    controller_getattr_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    error_config = getattr(LessonErrorSchema, 'model_config')\n"
        "    error_config.update(json_schema_extra=lambda schema: schema.clear())\n"
        "    rebuild_error_model = getattr(LessonErrorSchema, 'model_rebuild')\n"
        "    rebuild_error_model(force=True)\n"
        "    try:",
    )
    controller_bound_config_mutator_alias = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    update_error_config = LessonErrorSchema.model_config.update\n"
        "    update_error_config(json_schema_extra=lambda schema: schema.clear())\n"
        "    try:",
    )
    controller_iife_model_config_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    (lambda: (\n"
        "        LessonErrorSchema.model_config.update(\n"
        "            json_schema_extra=lambda schema: schema.clear(),\n"
        "        ),\n"
        "        LessonErrorSchema.model_rebuild(force=True),\n"
        "    ))()\n"
        "    try:",
    )
    controller_iife_deferred_lambda_control = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    deferred = (lambda: (\n"
        "        lambda: LessonErrorSchema.model_config.update(\n"
        "            json_schema_extra=lambda schema: schema.clear(),\n"
        "        )\n"
        "    ))()\n"
        "    try:",
    )
    controller_builtin_module_alias_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "import builtins as py_builtins\nfrom ninja import Router, Status",
    ).replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "router = Router()",
        "assign = py_builtins.setattr\n"
        "fetch = py_builtins.getattr\n"
        "assign(LessonErrorSchema, 'model_config', {'extra': 'forbid'})\n"
        "rebuild = fetch(LessonErrorSchema, 'model_rebuild')\n"
        "rebuild(force=True)\n\n"
        "router = Router()",
    )
    controller_reflected_builtin_alias_mutation = controller_builtin_module_alias_mutation.replace(
        "assign = py_builtins.setattr\nfetch = py_builtins.getattr",
        "assign = getattr(py_builtins, 'setattr')\n"
        "fetch = getattr(py_builtins, 'getattr')",
    )
    controller_nested_mutation_helper = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    def mutate_error_model():\n"
        "        LessonErrorSchema.model_config.update(extra='forbid')\n"
        "        LessonErrorSchema.model_rebuild(force=True)\n"
        "    mutate_error_model()\n"
        "    try:",
    )
    controller_default_captured_mutation_helper = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    def mutate_error_model(\n"
        "        config=LessonErrorSchema.model_config,\n"
        "        rebuild=LessonErrorSchema.model_rebuild,\n"
        "    ):\n"
        "        config.update(extra='forbid')\n"
        "        rebuild(force=True)\n"
        "    mutate_error_model()\n"
        "    try:",
    )
    controller_lambda_default_capture_mutation = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    (lambda config=LessonErrorSchema.model_config, "
        "rebuild=LessonErrorSchema.model_rebuild: (\n"
        "        config.update(extra='forbid'),\n"
        "        rebuild(force=True),\n"
        "    ))()\n"
        "    try:",
    )
    controller_builtin_module_getattr_read_only_control = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "import builtins as py_builtins\nfrom ninja import Router, Status",
    ).replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    fetch = py_builtins.getattr\n"
        "    config_snapshot = fetch(LessonErrorSchema, 'model_config')\n"
        "    config_title = config_snapshot.get('title')\n"
        "    try:",
    )
    controller_unrelated_setattr_control = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    setattr(request.options, 'model_config', {'trace': True})\n"
        "    try:",
    )
    controller_getattr_read_only_model_config_control = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError",
        "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError",
    ).replace(
        "def get_lesson_controller(request, lesson_id: int):\n    try:",
        "def get_lesson_controller(request, lesson_id: int):\n"
        "    config_snapshot = getattr(LessonErrorSchema, 'model_config')\n"
        "    config_title = config_snapshot.get('title')\n"
        "    try:",
    )
    mutation_import = (
        "from application.lesson.driving_layer.api.bc_error_schema import "
        "LessonErrorSchema, LessonNotFoundError"
    )
    base_error_import = (
        "from application.lesson.driving_layer.api.bc_error_schema import "
        "LessonNotFoundError"
    )

    def inject_controller(source: str) -> str:
        return CONTROLLER_FILES[
            "application/lesson/driving_layer/controller.py"
        ].replace(base_error_import, mutation_import).replace(
            "def get_lesson_controller(request, lesson_id: int):\n    try:",
            "def get_lesson_controller(request, lesson_id: int):\n"
            f"{source}"
            "    try:",
        )

    controller_parameter_helper_mutation = inject_controller(
        "    def mutate(model):\n"
        "        model.model_config.update(extra='forbid')\n"
        "        model.model_rebuild(force=True)\n"
        "    mutate(LessonErrorSchema)\n"
    )
    controller_parameter_helper_business_control = inject_controller(
        "    def mutate(model):\n"
        "        model.model_config.update(extra='forbid')\n"
        "    mutate(request.options)\n"
    )
    controller_config_parameter_helper_mutation = inject_controller(
        "    def mutate(config):\n"
        "        config.update(extra='forbid')\n"
        "    mutate(LessonErrorSchema.model_config)\n"
    )
    controller_config_copy_parameter_control = inject_controller(
        "    def mutate(config):\n"
        "        config.update(extra='forbid')\n"
        "    mutate(LessonErrorSchema.model_config.copy())\n"
    )
    controller_assigned_lambda_mutation = inject_controller(
        "    mutate = lambda model: model.model_config.update(extra='forbid')\n"
        "    mutate(LessonErrorSchema)\n"
    )
    controller_uninvoked_helper_control = inject_controller(
        "    def mutate(model):\n"
        "        model.model_config.update(extra='forbid')\n"
    )
    controller_if_branch_alias_mutation = inject_controller(
        "    if request.mutate:\n"
        "        config = LessonErrorSchema.model_config\n"
        "    else:\n"
        "        config = {}\n"
        "    config.update(extra='forbid')\n"
    )
    controller_ifexp_alias_mutation = inject_controller(
        "    config = LessonErrorSchema.model_config if request.mutate else {}\n"
        "    config.update(extra='forbid')\n"
    )
    controller_boolop_alias_mutation = inject_controller(
        "    config = request.mutate and LessonErrorSchema.model_config\n"
        "    config.update(extra='forbid')\n"
    )
    controller_for_alias_mutation = inject_controller(
        "    for config in (LessonErrorSchema.model_config,):\n"
        "        config.update(extra='forbid')\n"
    )
    controller_comprehension_alias_mutation = inject_controller(
        "    changed = [\n"
        "        config.update(extra='forbid')\n"
        "        for config in (LessonErrorSchema.model_config,)\n"
        "    ]\n"
    )
    controller_unbound_dict_mutation = inject_controller(
        "    dict.update(LessonErrorSchema.model_config, extra='forbid')\n"
    )
    controller_operator_mutation = inject_controller(
        "    import operator\n"
        "    operator.setitem(LessonErrorSchema.model_config, 'extra', 'forbid')\n"
    )
    controller_dunder_config_mutation = inject_controller(
        "    LessonErrorSchema.model_config.__ior__({'extra': 'forbid'})\n"
        "    LessonErrorSchema.model_config.__init__(extra='forbid')\n"
    )
    controller_type_setattr_mutation = inject_controller(
        "    type.__setattr__(LessonErrorSchema, 'model_config', {'extra': 'forbid'})\n"
    )
    controller_shadowed_setattr_control = inject_controller(
        "    def setattr(target, name, value):\n"
        "        return (target, name, value)\n"
        "    setattr(LessonErrorSchema, 'model_config', {'extra': 'forbid'})\n"
    )
    controller_parameter_setattr_control = inject_controller("").replace(
        "def get_lesson_controller(request, lesson_id: int):",
        "def get_lesson_controller(request, lesson_id: int, setattr=None):",
    ).replace(
        "    try:",
        "    setattr(LessonErrorSchema, 'model_config', {'extra': 'forbid'})\n"
        "    try:",
        1,
    )
    controller_imported_setattr_control = inject_controller(
        "    setattr(LessonErrorSchema, 'model_config', {'extra': 'forbid'})\n"
    ).replace(
        "from ninja import Router, Status",
        "from application.lesson.driving_layer.safe import observe as setattr\n"
        "from ninja import Router, Status",
    )
    controller_fake_builtins_control = inject_controller(
        "    builtins.setattr(LessonErrorSchema, 'model_config', {'extra': 'forbid'})\n"
    ).replace(
        "from ninja import Router, Status",
        "import application.lesson.driving_layer.safe as builtins\n"
        "from ninja import Router, Status",
    )
    controller_unrelated_error_suffix_control = inject_controller(
        "    RetryError.model_config.update(extra='forbid')\n"
    ).replace(
        "from ninja import Router, Status",
        "from application.lesson.domain.retry import RetryError\n"
        "from ninja import Router, Status",
    )
    one_hop_mutation_controller = CONTROLLER_FILES[
        "application/lesson/driving_layer/controller.py"
    ].replace(
        "from ninja import Router, Status",
        "from application.lesson.driving_layer.config_patch import install_config\n"
        "from ninja import Router, Status",
    )
    one_hop_mutation_module = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema

setattr(LessonErrorSchema, "model_config", {"extra": "forbid"})


def install_config():
    return None
"""
    selected_api_mutation = """from ninja_extra import NinjaExtraAPI
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema

setattr(LessonErrorSchema, "model_config", {"extra": "forbid"})

api = NinjaExtraAPI()
"""
    external_mutation_module = """from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema


def install_schema(value):
    LessonErrorSchema.model_config.update(extra="forbid")
    LessonErrorSchema.model_rebuild(force=True)
    return value


def install_config(config):
    config.update(extra="forbid")


def observe(value=None):
    return value
"""

    def external_api(source: str, *, include_schema: bool = False) -> str:
        schema_import = (
            "from application.lesson.driving_layer.api.bc_error_schema import "
            "LessonErrorSchema\n"
            if include_schema
            else ""
        )
        return (
            "from config.config_patch import install_config, install_schema, observe\n"
            f"{schema_import}"
            "from ninja_extra import NinjaExtraAPI\n\n"
            f"{source}\n"
            "api = NinjaExtraAPI()\n"
        )

    external_for_api = external_api(
        "for _ in (1,):\n    install_schema(None)\n"
    )
    external_while_api = external_api(
        "while True:\n    install_schema(None)\n    break\n"
    )
    external_with_api = external_api(
        "from contextlib import nullcontext\n\n"
        "with nullcontext():\n    install_schema(None)\n"
    )
    external_try_api = external_api(
        "try:\n    install_schema(None)\nexcept ValueError:\n    pass\n"
    )
    external_for_else_api = external_api(
        "for _ in ():\n    pass\nelse:\n    install_schema(None)\n"
    )
    external_decorator_api = external_api(
        "@install_schema\ndef observed():\n    return None\n"
    )
    external_branch_callable_api = external_api(
        "flag = bool(object())\n"
        "action = install_schema if flag else observe\n"
        "action(None)\n"
    )
    external_lazy_generator_api = external_api(
        "pending = (install_schema(None) for _ in (1,))\n"
    )
    external_eager_generator_api = external_api(
        "configured = list(install_schema(None) for _ in (1,))\n"
    )
    external_short_circuit_control_api = external_api(
        "configured = False and install_schema(None)\n"
    )
    external_live_bool_api = external_api(
        "configured = True and install_schema(None)\n"
    )
    external_config_alias_api = external_api(
        "target = LessonErrorSchema.model_config\ninstall_config(target)\n",
        include_schema=True,
    )
    external_branch_kind_api = external_api(
        "flag = bool(object())\n"
        "target = LessonErrorSchema.model_config if flag else {}\n"
        "install_config(target)\n",
        include_schema=True,
    )
    external_business_config_control_api = external_api(
        "target = {}\ninstall_config(target)\n"
    )
    external_match_unknown_guard_api = external_api(
        "import os\n"
        "flag = os.getenv('DDDJANGO_SKIP')\n"
        "match 1:\n"
        "    case 1 if flag:\n"
        "        observe()\n"
        "    case 1:\n"
        "        install_schema(None)\n"
    )
    external_match_true_guard_control_api = external_api(
        "match 1:\n"
        "    case 1 if True:\n"
        "        observe()\n"
        "    case 1:\n"
        "        install_schema(None)\n"
    )
    external_match_unmatched_baseline_api = external_api(
        "action = install_schema\n"
        "match 1:\n"
        "    case 2:\n"
        "        action = observe\n"
        "action(None)\n"
    )
    external_for_normal_else_control_api = external_api(
        "action = install_schema\n"
        "for _ in (1,):\n"
        "    pass\n"
        "else:\n"
        "    action = observe\n"
        "action(None)\n"
    )
    external_for_break_state_api = external_api(
        "action = observe\n"
        "for _ in (1,):\n"
        "    action = install_schema\n"
        "    break\n"
        "action(None)\n"
    )
    external_try_partial_state_api = external_api(
        "action = observe\n"
        "try:\n"
        "    action = install_schema\n"
        "    raise ValueError('stop')\n"
        "except ValueError:\n"
        "    action(None)\n"
    )
    external_try_handler_overwrite_control_api = external_api(
        "action = observe\n"
        "try:\n"
        "    action = install_schema\n"
        "    raise ValueError('stop')\n"
        "except ValueError:\n"
        "    action = observe\n"
        "    action(None)\n"
    )
    external_inert_try_handler_control_api = external_api(
        "try:\n"
        "    marker = 1\n"
        "except Exception:\n"
        "    install_schema(None)\n"
    )
    external_empty_listcomp_control_api = external_api(
        "configured = [install_schema(None) for _ in ()]\n"
    )
    external_false_filter_listcomp_control_api = external_api(
        "configured = [install_schema(None) for _ in (1,) if False]\n"
    )
    external_live_filter_listcomp_api = external_api(
        "configured = [install_schema(None) for _ in (1,) if True]\n"
    )
    external_generator_dunder_next_api = external_api(
        "configured = (install_schema(None) for _ in (1,)).__next__()\n"
    )
    external_numeric_short_circuit_control_api = external_api(
        "configured = 0 and install_schema(None)\n"
    )
    external_numeric_live_bool_api = external_api(
        "configured = 0 or install_schema(None)\n"
    )
    external_while_body_else_state_api = external_api(
        "import os\n"
        "flag = os.getenv('DDDJANGO_CONFIGURE')\n"
        "action = observe\n"
        "while flag:\n"
        "    action = install_schema\n"
        "    flag = ''\n"
        "else:\n"
        "    action(None)\n"
    )
    external_namedexpr_config_alias_api = external_api(
        "bound = (target := LessonErrorSchema.model_config)\n"
        "install_config(target)\n",
        include_schema=True,
    )
    external_for_target_config_alias_api = external_api(
        "for target in (LessonErrorSchema.model_config,):\n"
        "    install_config(target)\n",
        include_schema=True,
    )
    external_listcomp_target_config_alias_api = external_api(
        "configured = [\n"
        "    install_config(target)\n"
        "    for target in (LessonErrorSchema.model_config,)\n"
        "]\n",
        include_schema=True,
    )
    external_for_target_callable_alias_api = external_api(
        "for action in (install_schema,):\n"
        "    action(None)\n"
    )
    external_business_namedexpr_control_api = external_api(
        "bound = (target := {})\n"
        "install_config(target)\n"
    )
    external_business_for_target_control_api = external_api(
        "for target in ({},):\n"
        "    install_config(target)\n"
    )
    external_business_listcomp_target_control_api = external_api(
        "configured = [install_config(target) for target in ({},)]\n"
    )
    operation_empty_for_import_control = inject_controller(
        "    for _ in ():\n"
        "        from application.lesson.driving_layer.config_patch import install_config\n"
    )
    operation_false_while_import_control = inject_controller(
        "    while False:\n"
        "        from application.lesson.driving_layer.config_patch import install_config\n"
    )
    operation_for_break_else_import_control = inject_controller(
        "    for _ in (1,):\n"
        "        break\n"
        "    else:\n"
        "        from application.lesson.driving_layer.config_patch import install_config\n"
    )
    operation_match_false_guard_import_control = inject_controller(
        "    match 1:\n"
        "        case 1 if False:\n"
        "            from application.lesson.driving_layer.config_patch import install_config\n"
    )
    operation_match_unknown_guard_import = inject_controller(
        "    match 1:\n"
        "        case 1 if request.skip_config:\n"
        "            pass\n"
        "        case 1:\n"
        "            from application.lesson.driving_layer.config_patch import install_config\n"
    )
    controller_empty_for_mutation_control = inject_controller(
        "    for _ in ():\n"
        "        LessonErrorSchema.model_config.update(extra='forbid')\n"
    )
    controller_false_while_mutation_control = inject_controller(
        "    while False:\n"
        "        LessonErrorSchema.model_config.update(extra='forbid')\n"
    )
    controller_for_break_else_mutation_control = inject_controller(
        "    for _ in (1,):\n"
        "        break\n"
        "    else:\n"
        "        LessonErrorSchema.model_config.update(extra='forbid')\n"
    )
    controller_match_false_guard_mutation_control = inject_controller(
        "    match 1:\n"
        "        case 1 if False:\n"
        "            LessonErrorSchema.model_config.update(extra='forbid')\n"
    )
    controller_try_terminates_control = inject_controller(
        "    def configure():\n"
        "        try:\n"
        "            return\n"
        "        except ValueError:\n"
        "            return\n"
        "        LessonErrorSchema.model_config.update(extra='forbid')\n"
        "    configure()\n"
    )
    match_block_exit = 2 if MATCH_SYNTAX_SUPPORTED else 1
    match_clean_exit = 0 if MATCH_SYNTAX_SUPPORTED else 1
    match_block_fragment = (
        "model config mutation" if MATCH_SYNTAX_SUPPORTED else "invalid syntax"
    )
    match_clean_fragment = "" if MATCH_SYNTAX_SUPPORTED else "invalid syntax"
    return [
        Case("controller-error-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-aliased-error-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_aliased_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-module-error-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_module_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-module-setattr-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_module_setattr_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-local-delattr-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_local_delattr_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-aliased-schema-setattr-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_aliased_schema_setattr_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-module-qualified-setattr-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_module_qualified_setattr_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-aliased-builtin-setattr-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_aliased_builtin_setattr_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-getattr-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_getattr_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-bound-config-mutator-alias-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_bound_config_mutator_alias), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-iife-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_iife_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-builtin-module-alias-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_builtin_module_alias_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-reflected-builtin-alias-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_reflected_builtin_alias_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-nested-helper-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_nested_mutation_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-default-captured-helper-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_default_captured_mutation_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-lambda-default-capture-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_lambda_default_capture_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-parameter-helper-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_parameter_helper_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-config-parameter-helper-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_config_parameter_helper_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-assigned-lambda-model-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_assigned_lambda_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-if-branch-config-alias-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_if_branch_alias_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-ifexp-config-alias-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_ifexp_alias_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-boolop-config-alias-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_boolop_alias_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-for-target-config-alias-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_for_alias_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-comprehension-target-config-alias-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_comprehension_alias_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-unbound-dict-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_unbound_dict_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-operator-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_operator_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-dunder-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_dunder_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-type-setattr-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", controller_type_setattr_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-managed-one-hop-config-mutation-blocked", with_files(("application/lesson/driving_layer/controller.py", one_hop_mutation_controller), ("application/lesson/driving_layer/config_patch.py", one_hop_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-selected-api-config-mutation-blocked", with_files(("config/api.py", selected_api_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-for-call-blocked", with_files(("config/api.py", external_for_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-while-call-blocked", with_files(("config/api.py", external_while_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-with-call-blocked", with_files(("config/api.py", external_with_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-try-call-blocked", with_files(("config/api.py", external_try_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-for-else-call-blocked", with_files(("config/api.py", external_for_else_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-decorator-call-blocked", with_files(("config/api.py", external_decorator_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-branch-callable-blocked", with_files(("config/api.py", external_branch_callable_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-eager-generator-blocked", with_files(("config/api.py", external_eager_generator_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-live-bool-blocked", with_files(("config/api.py", external_live_bool_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-config-alias-blocked", with_files(("config/api.py", external_config_alias_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-branch-kind-blocked", with_files(("config/api.py", external_branch_kind_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-match-unknown-guard-fallthrough-blocked", with_files(("config/api.py", external_match_unknown_guard_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), match_block_exit, match_block_fragment),
        Case("controller-external-entry-match-unmatched-baseline-blocked", with_files(("config/api.py", external_match_unmatched_baseline_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), match_block_exit, match_block_fragment),
        Case("controller-external-entry-for-break-state-blocked", with_files(("config/api.py", external_for_break_state_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-try-partial-state-blocked", with_files(("config/api.py", external_try_partial_state_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-live-listcomp-filter-blocked", with_files(("config/api.py", external_live_filter_listcomp_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-generator-dunder-next-blocked", with_files(("config/api.py", external_generator_dunder_next_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-numeric-live-bool-blocked", with_files(("config/api.py", external_numeric_live_bool_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-while-body-else-state-blocked", with_files(("config/api.py", external_while_body_else_state_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-namedexpr-config-alias-blocked", with_files(("config/api.py", external_namedexpr_config_alias_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-for-target-config-alias-blocked", with_files(("config/api.py", external_for_target_config_alias_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-listcomp-target-config-alias-blocked", with_files(("config/api.py", external_listcomp_target_config_alias_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-external-entry-for-target-callable-alias-blocked", with_files(("config/api.py", external_for_target_callable_alias_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-clean-external-entry-lazy-generator-control", with_files(("config/api.py", external_lazy_generator_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-short-circuit-control", with_files(("config/api.py", external_short_circuit_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-business-config-control", with_files(("config/api.py", external_business_config_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-match-true-guard-control", with_files(("config/api.py", external_match_true_guard_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), match_clean_exit, match_clean_fragment),
        Case("controller-clean-external-entry-for-normal-else-overwrite-control", with_files(("config/api.py", external_for_normal_else_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-try-handler-overwrite-control", with_files(("config/api.py", external_try_handler_overwrite_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-inert-try-handler-control", with_files(("config/api.py", external_inert_try_handler_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-empty-listcomp-control", with_files(("config/api.py", external_empty_listcomp_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-false-filter-listcomp-control", with_files(("config/api.py", external_false_filter_listcomp_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-numeric-short-circuit-control", with_files(("config/api.py", external_numeric_short_circuit_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-business-namedexpr-control", with_files(("config/api.py", external_business_namedexpr_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-business-for-target-control", with_files(("config/api.py", external_business_for_target_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-external-entry-business-listcomp-target-control", with_files(("config/api.py", external_business_listcomp_target_control_api), ("config/config_patch.py", external_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-operation-empty-for-import-control", with_files(("application/lesson/driving_layer/controller.py", operation_empty_for_import_control), ("application/lesson/driving_layer/config_patch.py", one_hop_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-operation-false-while-import-control", with_files(("application/lesson/driving_layer/controller.py", operation_false_while_import_control), ("application/lesson/driving_layer/config_patch.py", one_hop_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-operation-for-break-skips-else-import-control", with_files(("application/lesson/driving_layer/controller.py", operation_for_break_else_import_control), ("application/lesson/driving_layer/config_patch.py", one_hop_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-operation-match-false-guard-import-control", with_files(("application/lesson/driving_layer/controller.py", operation_match_false_guard_import_control), ("application/lesson/driving_layer/config_patch.py", one_hop_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), match_clean_exit, match_clean_fragment),
        Case("controller-operation-match-unknown-guard-fallthrough-import-blocked", with_files(("application/lesson/driving_layer/controller.py", operation_match_unknown_guard_import), ("application/lesson/driving_layer/config_patch.py", one_hop_mutation_module), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), match_block_exit, match_block_fragment),
        Case("controller-clean-empty-for-mutation-control", with_files(("application/lesson/driving_layer/controller.py", controller_empty_for_mutation_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-false-while-mutation-control", with_files(("application/lesson/driving_layer/controller.py", controller_false_while_mutation_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-for-break-skips-else-mutation-control", with_files(("application/lesson/driving_layer/controller.py", controller_for_break_else_mutation_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-match-false-guard-mutation-control", with_files(("application/lesson/driving_layer/controller.py", controller_match_false_guard_mutation_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), match_clean_exit, match_clean_fragment),
        Case("controller-clean-try-terminates-before-mutation-control", with_files(("application/lesson/driving_layer/controller.py", controller_try_terminates_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-business-config-alias-control", with_files(("application/lesson/driving_layer/controller.py", controller_business_config_alias_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-parameter-helper-business-model-control", with_files(("application/lesson/driving_layer/controller.py", controller_parameter_helper_business_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-config-copy-parameter-control", with_files(("application/lesson/driving_layer/controller.py", controller_config_copy_parameter_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-uninvoked-mutation-helper-control", with_files(("application/lesson/driving_layer/controller.py", controller_uninvoked_helper_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-shadowed-setattr-control", with_files(("application/lesson/driving_layer/controller.py", controller_shadowed_setattr_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-parameter-shadowed-setattr-control", with_files(("application/lesson/driving_layer/controller.py", controller_parameter_setattr_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-imported-shadowed-setattr-control", with_files(("application/lesson/driving_layer/controller.py", controller_imported_setattr_control), ("application/lesson/driving_layer/safe.py", "def observe(*args):\n    return args\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-fake-builtins-module-control", with_files(("application/lesson/driving_layer/controller.py", controller_fake_builtins_control), ("application/lesson/driving_layer/safe.py", "def setattr(*args):\n    return args\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-unrelated-error-suffix-control", with_files(("application/lesson/driving_layer/controller.py", controller_unrelated_error_suffix_control), ("application/lesson/domain/retry.py", "class RetryError:\n    model_config = {}\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-read-only-model-config-control", with_files(("application/lesson/driving_layer/controller.py", controller_read_only_model_config_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-unrelated-setattr-control", with_files(("application/lesson/driving_layer/controller.py", controller_unrelated_setattr_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-getattr-read-only-model-config-control", with_files(("application/lesson/driving_layer/controller.py", controller_getattr_read_only_model_config_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-iife-deferred-lambda-control", with_files(("application/lesson/driving_layer/controller.py", controller_iife_deferred_lambda_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-builtin-module-getattr-read-only-control", with_files(("application/lesson/driving_layer/controller.py", controller_builtin_module_getattr_read_only_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-repeated-model-config-replaces-generator", with_files(("framework/ninja/framework_error_schema.py", repeated_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", repeated_config_generated), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-repeated-model-config-final-name-clean", with_files(("framework/ninja/framework_error_schema.py", repeated_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", two_field_direct), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-class-header-config-overrides-body-generator", with_files(("framework/ninja/framework_error_schema.py", header_override_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", repeated_config_generated), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-fieldinfo-later-alias-resets-validation-alias", with_files(("framework/ninja/framework_error_schema.py", field_merge_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", field_merge_wire), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fieldinfo-stale-validation-alias-rejected", with_files(("framework/ninja/framework_error_schema.py", field_merge_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", field_merge_legacy), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-fieldinfo-alias-none-lets-generator-win", with_files(("framework/ninja/framework_error_schema.py", alias_clear_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", repeated_config_generated), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fieldinfo-cleared-stale-alias-rejected", with_files(("framework/ninja/framework_error_schema.py", alias_clear_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", field_merge_wire), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-nested-annotated-outer-alias-clean", with_files(("framework/ninja/framework_error_schema.py", nested_alias_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", two_field_direct.replace("error_type=", "outerType=")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-nested-annotated-inner-alias-rejected", with_files(("framework/ninja/framework_error_schema.py", nested_alias_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", two_field_direct.replace("error_type=", "innerType=")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-alias-path-populated-base", with_files(("framework/ninja/framework_error_schema.py", alias_path_controller_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_controller_bc), ("application/lesson/driving_layer/controller.py", alias_path_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-alias-path-raw-discriminator-rejected", with_files(("framework/ninja/framework_error_schema.py", alias_path_controller_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_controller_bc), ("application/lesson/driving_layer/controller.py", alias_path_raw_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-analysis-alias-path-dynamic-payload", with_files(("framework/ninja/framework_error_schema.py", alias_path_controller_common), ("application/lesson/driving_layer/api/bc_error_schema.py", alias_path_controller_bc), ("application/lesson/driving_layer/controller.py", alias_path_dynamic_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-custom-generator-explicit-validation-alias-escape", with_files(("framework/ninja/aliasing.py", "def wire_name(value: str) -> str:\n    return f'wire_{value}'\n"), ("framework/ninja/framework_error_schema.py", custom_generator_explicit_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_explicit_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-statically-provable-custom-generator", with_files(("framework/ninja/aliasing.py", "def wire_name(value: str) -> str:\n    return f'wire_{value}'\n"), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-analysis-custom-generator-repr-conversion", with_files(("framework/ninja/aliasing.py", repr_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-custom-generator-final-shadow", with_files(("framework/ninja/aliasing.py", shadowed_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-dynamic-shape-marker-does-not-hide-custom-handler", with_files(("framework/ninja/aliasing.py", shadowed_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_handler_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "custom Ninja exception_handler forbidden"),
        Case("controller-dynamic-shape-marker-does-not-hide-mutation", with_files(("framework/ninja/aliasing.py", shadowed_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", controller_model_config_mutation), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "model config mutation"),
        Case("controller-analysis-custom-generator-indirect-final-shadow", with_files(("framework/ninja/aliasing.py", indirectly_shadowed_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-custom-generator-namedexpr-shadow", with_files(("framework/ninja/aliasing.py", namedexpr_shadowed_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-custom-generator-try-shadow", with_files(("framework/ninja/aliasing.py", try_shadowed_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-custom-generator-async-shadow", with_files(("framework/ninja/aliasing.py", async_shadowed_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-custom-generator-star-import-shadow", with_files(("framework/ninja/aliasing.py", star_shadowed_generator_support), ("framework/ninja/framework_error_schema.py", star_shadowed_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-custom-generator-set-call-shadow", with_files(("framework/ninja/aliasing.py", set_call_shadowed_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-custom-generator-imported-iterator-shadow", with_files(("framework/ninja/aliasing.py", iterator_shadowed_generator_support), ("framework/ninja/mutator.py", iterator_mutator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-clean-pure-custom-generator-module-control", with_files(("framework/ninja/aliasing.py", pure_generator_module_control), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-custom-generator-typo-rejected", with_files(("framework/ninja/aliasing.py", "def wire_name(value: str) -> str:\n    return f'wire_{value}'\n"), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_typo_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-dynamic-shape-runtime-proof-handoff", with_files(("framework/ninja/aliasing.py", complex_generator_support), ("framework/ninja/framework_error_schema.py", custom_generator_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_generator_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-body-status-must-be-integer-field", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", status_string_field_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-to-camel-digit-lowercase-segment", with_files(("framework/ninja/framework_error_schema.py", digit_camel_common), ("application/lesson/driving_layer/api/bc_error_schema.py", digit_camel_bc), ("application/lesson/driving_layer/controller.py", digit_camel_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-nested-annotated-cleared-factory-is-required", with_files(("framework/ninja/framework_error_schema.py", nested_required_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", omitted_msg_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-nested-annotated-outer-factory-is-optional", with_files(("framework/ninja/framework_error_schema.py", nested_optional_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", omitted_msg_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-explicit-validate-by-name-dominates-populate-false", with_files(("framework/ninja/framework_error_schema.py", explicit_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", two_field_direct), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-explicit-validate-by-name-false-alias-clean", with_files(("framework/ninja/framework_error_schema.py", explicit_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", explicit_config_alias_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-explicit-validate-by-name-true-dominates-populate", with_files(("framework/ninja/framework_error_schema.py", explicit_true_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", two_field_direct), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-negative-alias-priority-lets-generator-win", with_files(("framework/ninja/framework_error_schema.py", negative_alias_priority_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", alias_priority_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-none-alias-priority-keeps-explicit-alias", with_files(("framework/ninja/framework_error_schema.py", none_alias_priority_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", none_alias_priority_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-approved-nullable-integer-body-status", with_files(("framework/ninja/framework_error_schema.py", nullable_status_common), ("application/lesson/driving_layer/api/bc_error_schema.py", nullable_status_lesson), ("application/lesson/driving_layer/controller.py", nullable_status_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-approved-literal-integer-body-status", with_files(("framework/ninja/framework_error_schema.py", literal_status_common), ("application/lesson/driving_layer/api/bc_error_schema.py", literal_status_lesson), ("application/lesson/driving_layer/controller.py", nullable_status_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-approved-computed-integer-body-status", with_files(("framework/ninja/framework_error_schema.py", computed_status_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", computed_status_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-approved-plain-computed-integer-status", with_files(("framework/ninja/framework_error_schema.py", plain_computed_status_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", computed_status_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-approved-cached-computed-integer-status", with_files(("framework/ninja/framework_error_schema.py", cached_computed_status_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", computed_status_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-direct-base-validation-alias", with_files(("framework/ninja/framework_error_schema.py", ALIASED_STATUS_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", ALIASED_STATUS_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_aliased_base_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-base-required-nullable-discriminator-omitted", with_files(("framework/ninja/framework_error_schema.py", NULLABLE_DISCRIMINATOR_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", NULLABLE_DISCRIMINATOR_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_nullable_omission_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-base-enum-value-descendant-forbidden", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_custom_base_controller.replace("LessonErrorCode.NOT_FOUND", "LessonErrorCode.NOT_FOUND.value")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-validate-by-alias-false-implies-name", with_files(("framework/ninja/framework_error_schema.py", validate_alias_false_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_custom_base_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-project-config-builder-rejects-field-name", with_files(("framework/ninja/configs.py", dynamic_config_support), ("framework/ninja/framework_error_schema.py", dynamic_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_custom_base_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-statically-provable-project-config-builder", with_files(("framework/ninja/configs.py", dynamic_config_support), ("framework/ninja/framework_error_schema.py", dynamic_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", dynamic_config_generated_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-analysis-project-config-builder-final-shadow", with_files(("framework/ninja/configs.py", shadowed_config_builder_support), ("framework/ninja/framework_error_schema.py", dynamic_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", dynamic_config_generated_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-project-config-builder-global-rebind", with_files(("framework/ninja/configs.py", rebound_config_global_support), ("framework/ninja/framework_error_schema.py", dynamic_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", dynamic_config_generated_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-project-config-builder-indirect-final-shadow", with_files(("framework/ninja/configs.py", indirectly_shadowed_config_builder_support), ("framework/ninja/framework_error_schema.py", dynamic_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", dynamic_config_generated_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-project-config-builder-namedexpr-shadow", with_files(("framework/ninja/configs.py", namedexpr_shadowed_config_builder_support), ("framework/ninja/framework_error_schema.py", dynamic_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", dynamic_config_generated_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-project-config-builder-while-shadow", with_files(("framework/ninja/configs.py", while_shadowed_config_builder_support), ("framework/ninja/framework_error_schema.py", dynamic_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", dynamic_config_generated_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-analysis-project-config-builder-async-shadow", with_files(("framework/ninja/configs.py", async_shadowed_config_builder_support), ("framework/ninja/framework_error_schema.py", dynamic_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", dynamic_config_generated_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("controller-clean-dynamic-model-config-prepared-concrete", with_files(("framework/ninja/configs.py", dynamic_config_support), ("framework/ninja/framework_error_schema.py", dynamic_config_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", custom_prepared_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-module-static-integer-status", with_files(("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", static_module_status_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-alias-priority-generator-wins", with_files(("framework/ninja/framework_error_schema.py", alias_priority_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", alias_priority_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-deprecated-population-config-does-not-enable-name", with_files(("framework/ninja/framework_error_schema.py", deprecated_population_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_custom_base_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-base-omits-direct-pydantic-undefined-required", with_files(("framework/ninja/framework_error_schema.py", direct_undefined_common), ("application/lesson/driving_layer/api/bc_error_schema.py", direct_required_lesson), ("application/lesson/driving_layer/controller.py", direct_required_omission_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-base-omits-direct-ellipsis-required", with_files(("framework/ninja/framework_error_schema.py", direct_ellipsis_common), ("application/lesson/driving_layer/api/bc_error_schema.py", direct_required_lesson), ("application/lesson/driving_layer/controller.py", direct_required_omission_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-field-alias-none", with_files(("framework/ninja/framework_error_schema.py", alias_none_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_custom_base_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-field-validation-alias-none", with_files(("framework/ninja/framework_error_schema.py", validation_alias_none_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_custom_base_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case(
            "controller-clean-project-approved-custom-shape-literal-status",
            with_files(
                ("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    CUSTOM_LESSON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/controller.py",
                    CUSTOM_CONTROLLER,
                ),
                base=CONTROLLER_FILES,
            ),
            "check-api-error-controller-contract.py",
            controller_args(),
            0,
            "",
        ),
        Case(
            "controller-clean-project-approved-aliased-body-status-field",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    ALIASED_STATUS_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    ALIASED_STATUS_LESSON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/controller.py",
                    ALIASED_STATUS_CONTROLLER,
                ),
                base=CONTROLLER_FILES,
            ),
            "check-api-error-controller-contract.py",
            controller_args(),
            0,
            "",
        ),
        Case(
            "controller-unknown-body-status-field",
            with_files(
                (
                    "application/lesson/driving_layer/controller.py",
                    CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace(
                        "Status(error.status, error)",
                        "Status(error.not_a_contract_field, error)",
                    ),
                ),
                base=CONTROLLER_FILES,
            ),
            "check-api-error-controller-contract.py",
            controller_args(),
            2,
            "BLOCKER",
        ),
        Case("controller-clean-sync-narrow-try", with_files(("application/lesson/driving_layer/controller.py", clean_sync_annassign), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-async-narrow-try", with_files(("application/lesson/driving_layer/controller.py", clean_async), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-tuple-catch-prepared-concrete", with_files(("application/lesson/driving_layer/controller.py", clean_tuple), ("application/lesson/application_layer/use_cases.py", clean_tuple_use_cases), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-event-specific-base", with_files(("framework/ninja/framework_error_schema.py", DYNAMIC_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_base), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-base-omits-approved-defaulted-fields", with_files(("framework/ninja/framework_error_schema.py", FLEXIBLE_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", FLEXIBLE_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_base_omits_defaulted_fields), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-base-omits-annotated-defaulted-fields", with_files(("framework/ninja/framework_error_schema.py", ANNOTATED_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", ANNOTATED_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", ANNOTATED_BASE_CONTROLLER), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-result-none-prepared-errorout-status", with_files(("application/lesson/driving_layer/controller.py", clean_result_none), ("application/lesson/application_layer/use_cases.py", clean_result_none_use_cases), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-approved-retry-after", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("from ninja import Router, Status", "from django.http import HttpResponse\nfrom ninja import Router, Status").replace("def get_lesson_controller(request, lesson_id: int):", "def get_lesson_controller(request, response: HttpResponse, lesson_id: int):").replace("        return Status(error.status, error)", "        response['Retry-After'] = '1'\n        return Status(error.status, error)")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-relative-as-import-provenance", with_files(("application/lesson/driving_layer/controller.py", relative_alias_controller), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-unselected-preserve-handler", with_files(("application/lesson/driving_layer/preserve_controller.py", "def preserve_controller(request): return {'legacy': True}\n"), ("application/lesson/driving_layer/preserve_handler.py", unselected_preserve_handler), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-empty-error-bc", empty_error_bc_files, "check-api-error-controller-contract.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/driving_layer/controller.py", "--scope-bc", "lesson"), 0, ""),
        Case("controller-clean-preserve-profile-na", preserve_controller_files, "check-api-error-controller-contract.py", preserve_controller_args, 0, ""),
        Case("controller-direct-presentation-helper", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .assembler import assemble").replace("error = LessonNotFoundError()", "error = assemble()")), ("application/lesson/driving_layer/assembler.py", "from .api.bc_error_schema import LessonNotFoundError\ndef assemble(): return LessonNotFoundError()\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-direct-one-hop-serializer-helper", with_files(("application/lesson/driving_layer/controller.py", serializer_controller), ("application/lesson/driving_layer/transport.py", serializer_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-direct-one-hop-mapping-helper", with_files(("application/lesson/driving_layer/controller.py", mapping_controller), ("application/lesson/driving_layer/bridge.py", mapping_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-registered-handler", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"] + "\n@router.exception_handler(LessonMissing)\ndef handler(request, exc): pass\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-add-exception-handler-call", with_files(("application/lesson/driving_layer/controller.py", add_handler_call), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-wide-try", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("try:\n        lesson =", "try:\n        prepared = lesson_id\n        lesson =")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-multiple-peer-outer-calls-one-statement", with_files(("application/lesson/driving_layer/controller.py", multiple_peer_calls), ("application/lesson/application_layer/use_cases.py", multiple_peer_use_cases), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-success-transform-inside-try", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("lesson = get_lesson(lesson_id)", "lesson = get_lesson(lesson_id)\n        return {'lesson': lesson}")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-broad-catch", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("except LessonMissing:", "except Exception:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-bare-catch", with_files(("application/lesson/driving_layer/controller.py", bare_catch), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-tuple-catch-includes-base-exception", with_files(("application/lesson/driving_layer/controller.py", tuple_base_exception), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-framework-catch", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom ninja.errors import HttpError").replace("except LessonMissing:", "except HttpError:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-raw-infra-catch", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("from ninja import Router, Status", "from django.db import DatabaseError as StorageFailure\nfrom ninja import Router, Status").replace("except LessonMissing:", "except StorageFailure:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-immediate-raise-catch", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("    try:\n        lesson = get_lesson(lesson_id)", "    lesson = None\n    try:\n        raise LessonMissing()")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-reraises", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("error = LessonNotFoundError()\n        return Status(error.status, error)", "raise")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-explicit-reraise", with_files(("application/lesson/driving_layer/controller.py", explicit_reraise), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-raises-http-error", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom ninja.errors import HttpError").replace("error = LessonNotFoundError()\n        return Status(error.status, error)", "raise HttpError(404, 'missing')")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-forwards-exception", with_files(("application/lesson/driving_layer/controller.py", forwarded_exception), ("application/lesson/driving_layer/forwarder.py", "def forward_error(exc): return exc\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-no-direct-status", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("return Status(error.status, error)", "return error")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-literal-http-status", with_files(("application/lesson/driving_layer/controller.py", hardcoded_status), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-concrete-called-with-args", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("LessonNotFoundError()", "LessonNotFoundError(detail='missing')")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-base-extra-constructor-field", with_files(("framework/ninja/framework_error_schema.py", DYNAMIC_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_base_extra_field), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-base-missing-required-field", with_files(("framework/ninja/framework_error_schema.py", FLEXIBLE_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", FLEXIBLE_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_base_missing_required_field), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-error-tuple-raw-response-dict", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("return Status(error.status, error)", "return 404, {'code': 'lesson_not_found'}")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-error-raw-response", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom ninja.responses import Response").replace("return Status(error.status, error)", "return Response({'code': 'lesson_not_found'}, status=404)")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-analysis-unresolved-status-reexport", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("from ninja import Router, Status", "from .exports import Status\nfrom ninja import Router")), ("application/lesson/driving_layer/exports.py", "from ninja import Status\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-unresolved-error-out-reexport", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError", "from .exports import LessonNotFoundError")), ("application/lesson/driving_layer/exports.py", "from .api.bc_error_schema import LessonNotFoundError\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-selected-syntax", with_files(("application/lesson/driving_layer/controller.py", "def broken(:\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-one-hop-syntax", with_files(("application/lesson/driving_layer/controller.py", CONTROLLER_FILES["application/lesson/driving_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .factory import make_error")), ("application/lesson/driving_layer/factory.py", "def broken(:\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-missing-selected-controller-path", CONTROLLER_FILES, "check-api-error-controller-contract.py", controller_args("--controller-module", "application/lesson/driving_layer/missing_controller.py"), 1, "사용 오류"),
        Case("controller-analysis-selected-root-escape", CONTROLLER_FILES, "check-api-error-controller-contract.py", controller_args("--controller-module", "../outside.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--controller-module"})),
        Case("controller-analysis-duplicate-controller-selector", CONTROLLER_FILES, "check-api-error-controller-contract.py", controller_args("--controller-module", "application/lesson/driving_layer/controller.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"duplicate:--controller-module"})),
        Case("controller-analysis-auto-profile", CONTROLLER_FILES, "check-api-error-controller-contract.py", AUTO_PROFILE_ARGS, 0, ""),
        Case("controller-analysis-missing-args", CONTROLLER_FILES, "check-api-error-controller-contract.py", (TARGET_DIR, "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--error-profile", "missing:--api-module", "missing:--controller-module", "missing:--scope-bc"})),
        Case("controller-analysis-matchas-status-capture", with_files(("application/lesson/driving_layer/controller.py", match_status_capture), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-matchstar-errorout-capture", with_files(("application/lesson/driving_layer/controller.py", match_error_out_capture), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-matchmapping-exception-capture", with_files(("application/lesson/driving_layer/controller.py", match_exception_capture), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case(
            "controller-clean-match-unrelated-capture",
            with_files(
                (
                    "application/lesson/driving_layer/controller.py",
                    match_unrelated_capture,
                ),
                base=CONTROLLER_FILES,
            ),
            "check-api-error-controller-contract.py",
            controller_args(),
            0 if sys.version_info >= (3, 10) else 1,
            "" if sys.version_info >= (3, 10) else "사용 오류",
        ),
        Case("controller-clean-class-body-classvar-alias-five-fields", with_files(("framework/ninja/framework_error_schema.py", class_body_classvar_common), ("application/lesson/driving_layer/api/bc_error_schema.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_base), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-class-body-classvar-cannot-be-passed", with_files(("framework/ninja/framework_error_schema.py", class_body_classvar_common), ("application/lesson/driving_layer/api/bc_error_schema.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_base_passes_classvar), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-module-classvar-alias-control", with_files(("framework/ninja/framework_error_schema.py", module_classvar_common), ("application/lesson/driving_layer/api/bc_error_schema.py", DYNAMIC_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_base), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-function-add-exception-handler-call", with_files(("application/lesson/driving_layer/controller.py", function_handler_call), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-nested-exception-handler-decorator", with_files(("application/lesson/driving_layer/controller.py", nested_handler_decorator), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-module-if-add-exception-handler-call", with_files(("application/lesson/driving_layer/controller.py", conditional_handler_call), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-class-method-add-exception-handler-call", with_files(("application/lesson/driving_layer/controller.py", class_method_handler_call), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-arbitrary-nested-handler-receiver", with_files(("application/lesson/driving_layer/controller.py", arbitrary_handler_receiver), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-analysis-shadowed-isinstance-result-predicate", with_files(("application/lesson/driving_layer/controller.py", shadowed_isinstance_result), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-clean-builtin-isinstance-result-predicate", with_files(("application/lesson/driving_layer/controller.py", builtin_isinstance_result), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-analysis-shadowed-isinstance-helper-predicate", with_files(("application/lesson/driving_layer/controller.py", mapping_controller), ("application/lesson/driving_layer/bridge.py", shadowed_isinstance_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-caught-exception-forwarded-in-container", with_files(("application/lesson/driving_layer/controller.py", forwarded_exception_container), ("application/lesson/driving_layer/forwarder.py", "def forward_error(exc): return exc\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "caught exception forwarding forbidden"),
        Case("controller-clean-caught-exception-nested-lambda-scope", with_files(("application/lesson/driving_layer/controller.py", nested_lambda_exception_reference), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-serializer-before-later-errorout-assignment", with_files(("application/lesson/driving_layer/controller.py", temporal_serializer_controller), ("application/lesson/driving_layer/transport.py", temporal_serializer_helper), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-one-hop-nested-prepared-factory", with_files(("application/lesson/driving_layer/controller.py", selected_nested_helper_controller), ("application/lesson/driving_layer/assembler.py", nested_prepared_factory), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "prepared FrameworkErrorSchema factory/helper forbidden"),
        Case("controller-clean-one-hop-nested-helper-without-errorout", with_files(("application/lesson/driving_layer/controller.py", selected_nested_helper_controller), ("application/lesson/driving_layer/assembler.py", nested_factory_control), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-direct-raw-dict-error-status-outside-arm", with_files(("application/lesson/driving_layer/controller.py", raw_dict_error_status), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-direct-raw-name-error-status-outside-arm", with_files(("application/lesson/driving_layer/controller.py", raw_name_error_status), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-clean-direct-success-status", with_files(("application/lesson/driving_layer/controller.py", success_status), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-branch-created-router-handler", with_files(("application/lesson/driving_layer/controller.py", branch_router_handler), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "custom Ninja add_exception_handler forbidden"),
        Case("controller-fresh-analysis-ambiguous-branch-handler-receiver", with_files(("application/lesson/driving_layer/controller.py", ambiguous_branch_handler), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-fresh-clean-arbitrary-branch-handler-receiver", with_files(("application/lesson/driving_layer/controller.py", arbitrary_branch_handler), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-analysis-module-shadowed-isinstance-predicate", with_files(("application/lesson/driving_layer/controller.py", module_shadowed_isinstance_result), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-fresh-clean-true-builtin-isinstance-predicate", with_files(("application/lesson/driving_layer/controller.py", builtin_isinstance_result), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-caught-exception-forwarded-in-lambda-default", with_files(("application/lesson/driving_layer/controller.py", lambda_default_forwarding), ("application/lesson/driving_layer/forwarder.py", "def forward_error(value): return value\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "caught exception forwarding forbidden"),
        Case("controller-fresh-caught-exception-forwarded-in-lambda-keyword-default", with_files(("application/lesson/driving_layer/controller.py", lambda_keyword_default_forwarding), ("application/lesson/driving_layer/forwarder.py", "def forward_error(value): return value\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "caught exception forwarding forbidden"),
        Case("controller-fresh-clean-caught-exception-in-lambda-body-scope", with_files(("application/lesson/driving_layer/controller.py", lambda_body_forwarding_control), ("application/lesson/driving_layer/forwarder.py", "def forward_error(value): return value\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-clean-nonforwarding-lambda-default", with_files(("application/lesson/driving_layer/controller.py", lambda_nonforwarding_default_control), ("application/lesson/driving_layer/forwarder.py", "def forward_error(value): return value\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-conditional-errorout-raw-serializer", with_files(("application/lesson/driving_layer/controller.py", selected_serializer_controller), ("application/lesson/driving_layer/transport.py", conditional_error_serializer), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "FrameworkErrorSchema raw HTTP serializer helper forbidden"),
        Case("controller-fresh-clean-all-paths-success-serializer", with_files(("application/lesson/driving_layer/controller.py", selected_serializer_controller), ("application/lesson/driving_layer/transport.py", proven_success_serializer), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-literal-true-success-serializer", with_files(("application/lesson/driving_layer/controller.py", selected_serializer_controller), ("application/lesson/driving_layer/transport.py", literal_true_success_serializer), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-literal-false-errorout-serializer", with_files(("application/lesson/driving_layer/controller.py", selected_serializer_controller), ("application/lesson/driving_layer/transport.py", literal_false_error_serializer), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "FrameworkErrorSchema raw HTTP serializer helper forbidden"),
        Case("controller-fresh-operation-nested-prepared-factory", with_files(("application/lesson/driving_layer/controller.py", operation_nested_factory), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "prepared FrameworkErrorSchema factory/helper forbidden"),
        Case("controller-fresh-clean-operation-nested-benign-helper", with_files(("application/lesson/driving_layer/controller.py", operation_nested_benign), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-fresh-local-class-method-prepared-factory", with_files(("application/lesson/driving_layer/controller.py", selected_nested_helper_controller), ("application/lesson/driving_layer/assembler.py", local_class_factory), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "prepared FrameworkErrorSchema factory/helper forbidden"),
        Case("controller-fresh-clean-local-class-method-benign-helper", with_files(("application/lesson/driving_layer/controller.py", selected_nested_helper_controller), ("application/lesson/driving_layer/assembler.py", local_class_benign), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        # Reviewer gaps deliberately remain outside the deterministic oracle:
        # application collaborator identity, broad exception hidden by re-export,
        # and two-hop/off-selection helpers.
    ]


CONTEXT_FILES: Final = {
    **BASE_FILES,
    "config/api.py": """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
""",
    "application/lesson/driving_layer/controller.py": """from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError

def get_lesson(request):
    return LessonNotFoundError()
""",
    "application/lesson/domain_layer/model.py": "class Lesson: pass\n",
    "application/lesson/driving_layer/open_host_service/public/public_service.py": "",
    "application/lesson/driving_layer/open_host_service/public/contract/request/lesson_query_request.py": "class LessonQueryRequest: pass\n",
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
        "application/lesson/driving_layer/controller.py",
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
            "from application.catalog.driven_layer.repository import CatalogRepository\n",
        ),
        (
            "application/catalog/driven_layer/repository.py",
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
            "application/lesson/driving_layer/controller.py",
            "from application.catalog.driving_layer.api.bc_error_schema "
            "import CatalogErrorCode, CatalogErrorSchema\n\n"
            "def get_lesson(request):\n"
            "    return {'id': 1}\n",
        ),
        (
            "application/catalog/driving_layer/api/bc_error_schema.py",
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
            "application/lesson/driving_layer/controller.py",
            "def get_lesson(request): return {'id': 1}\n",
        ),
        ("application/lesson/driving_layer/api/bc_error_schema.py", "<REMOVE>"),
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
        Case("context-upstream-domain-exception-in-acl-blocked", with_files(("application/lesson/driven_layer/adapter/anticorruption_layer/catalog/catalog_adapter.py", "from application.catalog.domain_layer.exceptions import CatalogMissing\nfrom application.lesson.domain_layer.exceptions import LessonCatalogUnavailable\n\n\ndef load_catalog(fetch):\n    try:\n        return fetch()\n    except CatalogMissing as exc:\n        raise LessonCatalogUnavailable() from exc\n"), ("application/catalog/domain_layer/exceptions.py", "class CatalogMissing(Exception): pass\n"), ("application/lesson/domain_layer/exceptions.py", "class LessonCatalogUnavailable(Exception): pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "blocker"),
        Case("context-clean-separated-preserve-scope", with_files(("legacy/api.py", "api = object()\n"), ("legacy/controller.py", "def legacy(request): return {'error': 'old'}\n"), base=CONTEXT_FILES), "check-context-isolation.py", preserve_args, 0, ""),
        Case("context-existing-s1-s3-directions-blocked", with_files(("application/lesson/domain_layer/service.py", "from application.lesson.domain_layer.model import Lesson\n"), ("application/catalog/published_service/public/contract/query.py", "class CatalogQuery: pass\n"), ("application/lesson/application_layer/use_catalog.py", "from application.catalog.published_service.public.contract.query import CatalogQuery\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "blocker"),
        Case("context-clean-empty-error-bc", empty_error_bc_files, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/driving_layer/controller.py", "--scope-bc", "lesson"), 0, ""),
        Case("context-preserve-unchanged-tracked-s1-blocked", preserve_tracked_s1_files, "check-context-isolation.py", preserve_args, 2, "blocker", baseline_files=preserve_tracked_s1_files),
        Case("context-preserve-touched-django-http-import-only-blocked", preserve_django_import_files, "check-context-isolation.py", preserve_args, 2, "blocker", baseline_files=preserve_django_import_baseline),
        Case("context-clean-root-path-business-size", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef route_limits(request):\n    if request.path.startswith('/limits'):\n        return {'page_size': 500}\n    return {'page_size': 100}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-path-postal-code", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef route_address(request):\n    if request.path.startswith('/addresses'):\n        return {'postal_code': '12345'}\n    return {'postal_code': '00000'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-error-named-metric-helper", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef calculate_error_rate(samples):\n    return {'code': 'sample_limit'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-error-named-metric-argument", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef summarize(error_rate: float):\n    return {'code': 'sample_limit'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-exception-arg-business-payload", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef summarize(exc):\n    return {'sample_size': 500}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-clean-root-path-nested-return-scope", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef route_docs(request):\n    if request.path.startswith('/docs'):\n        def default_status():\n            return 404\n        return {'ok': True}\n    return {'ok': False}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-imports-bc", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\nfrom application.lesson.driven_layer.repository import LessonRepository\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-local-global-error-code", with_files(("config/api.py", "from enum import StrEnum\nfrom ninja_extra import NinjaExtraAPI\nclass GlobalErrorCode(StrEnum):\n    BAD = 'bad'\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-local-error-out", with_files(("config/api.py", "from ninja import Schema\nfrom ninja_extra import NinjaExtraAPI\nclass ProblemErrorOut(Schema):\n    error_type: str\n    msg: str\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-business-schema-with-code-status", with_files(("config/api.py", "from ninja import Schema\nfrom ninja_extra import NinjaExtraAPI\nclass BuildRecord(Schema):\n    code: str\n    status: int\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-local-error-catalog", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\nPROBLEM_CATALOG: dict = {}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-local-exception-mapping", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef choose(exc):\n    return 404, {'code': 'lesson_not_found'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-custom-discriminator-converter", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef convert(exc):\n    return {'error_type': 'lesson_not_found'}\napi = NinjaExtraAPI()\n"), ("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-path-specific-error-branch", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\ndef handle(request):\n    if request.path.startswith('/lessons'):\n        return {'ok': True}\n    else:\n        return 404, {'code': 'lesson_not_found'}\napi = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-root-api-custom-exception-handler", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\n\napi = NinjaExtraAPI()\n\n\n@api.exception_handler(LookupError)\ndef handle_lookup(request, exc):\n    return None\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-domain-imports-ninja", with_files(("application/lesson/domain_layer/model.py", "import ninja\nclass Lesson: pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "#2"),
        Case("context-application-imports-django-http", with_files(("application/lesson/application_layer/use_case.py", "from django.http import JsonResponse\ndef run(): return None\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "blocker"),
        Case("context-infra-imports-common-error-out", with_files(("application/lesson/driven_layer/repository.py", "from framework.ninja.framework_error_schema import FrameworkErrorSchema\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-application-imports-own-bc-error-out", with_files(("application/lesson/application_layer/use_case.py", "from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "blocker"),
        Case("context-layer-imports-other-bc-error-code", with_files(("application/lesson/application_layer/use_case.py", "from application.catalog.driving_layer.api.bc_error_schema import CatalogErrorCode\n"), ("application/catalog/driving_layer/api/bc_error_schema.py", CATALOG_DUPLICATE_ERROR_OUT), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "blocker"),
        Case("context-layer-imports-other-bc-error-out", with_files(("application/lesson/driven_layer/repository.py", "from application.catalog.driving_layer.api.bc_error_schema import CatalogErrorSchema\n"), ("application/catalog/driving_layer/api/bc_error_schema.py", CATALOG_DUPLICATE_ERROR_OUT), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "blocker"),
        Case("context-selected-controller-imports-other-bc-error-language", cross_bc_error_import_files, "check-context-isolation.py", context_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "blocker"),
        Case("context-cross-bc-exception-outside-acl", with_files(("application/lesson/driving_layer/controller.py", "from application.catalog.domain_layer.exceptions import CatalogMissing\n"), ("application/catalog/domain_layer/exceptions.py", "class CatalogMissing(Exception): pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "blocker"),
        Case("context-existing-s1-cross-bc-internal", with_files(("application/lesson/domain_layer/service.py", "from application.catalog.driven_layer.repository import CatalogRepository\n"), ("application/catalog/driven_layer/repository.py", "class CatalogRepository: pass\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "blocker"),
        Case("context-code-unchanged-tracked-s1-blocked", tracked_s1_files, "check-context-isolation.py", context_args("--scope-bc", "catalog"), 2, "blocker", baseline_files=tracked_s1_files),
        Case("context-existing-s2-contract-layer-import", with_files(("application/lesson/driving_layer/open_host_service/public/contract/request/lesson_query_request.py", "from application.lesson.domain_layer.model import Lesson\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "blocker"),
        Case("context-existing-s3-own-published-import", with_files(("application/lesson/application_layer/use_case.py", "from application.lesson.driving_layer.open_host_service.public.contract.request.lesson_query_request import LessonQueryRequest\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 2, "blocker"),
        Case("context-code-touched-application-http-status-signal", code_touched_status_files, "check-context-isolation.py", context_args(), 0, "", baseline_files=code_touched_status_baseline),
        Case("context-preserve-untouched-application-http-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error}, "check-context-isolation.py", preserve_args, 2, "blocker", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error}),
        Case("context-preserve-touched-application-http-error-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error}, "check-context-isolation.py", preserve_args, 2, "blocker", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": clean_legacy}),
        Case("context-preserve-touched-application-http-import-only-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_import_only}, "check-context-isolation.py", preserve_args, 2, "blocker", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": clean_legacy}),
        Case("context-preserve-touched-application-raw-http-response-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_raw_http_response}, "check-context-isolation.py", preserve_args, 2, "blocker", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": clean_legacy}),
        Case("context-preserve-touched-application-http-status-keyword-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error_status}, "check-context-isolation.py", preserve_args, 2, "blocker", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": clean_legacy}),
        Case("context-preserve-untracked-application-http-blocked", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "application/legacy/application_layer/use_case.py": legacy_http_error}, "check-context-isolation.py", preserve_args, 2, "blocker", baseline_files={"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n"}),
        Case("context-preserve-http-signal-without-application-container", {"legacy/api.py": "api = object()\n", "legacy/controller.py": "pass\n", "legacy/application_layer/use_case.py": legacy_raw_status_only}, "check-context-isolation.py", preserve_args, 0, ""),
        Case("context-preserve-malformed-python-raw-http-signal", preserve_malformed_files, "check-context-isolation.py", preserve_args, 0, "", baseline_files=preserve_malformed_baseline),
        Case("context-analysis-multiple-api-instances", with_files(("config/api.py", "from ninja_extra import NinjaExtraAPI\npublic_api = NinjaExtraAPI()\ninternal_api = NinjaExtraAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-analysis-shadowed-api-constructor", with_files(("config/api.py", "from ninja import NinjaAPI\ndef NinjaAPI():\n    return object()\napi = NinjaAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-analysis-conditionally-shadowed-api-constructor", with_files(("config/api.py", "from ninja import NinjaAPI\n\nif USE_FAKE_API:\n    NinjaAPI = object\n\napi = NinjaAPI()\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-analysis-api-controller-overlap", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "config/api.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 0, "", allowed_arg_issues=frozenset({"overlap:--api-module/--controller-module"})),
        Case("context-analysis-selected-api-syntax", with_files(("config/api.py", "api = (\n"), base=CONTEXT_FILES), "check-context-isolation.py", context_args(), 0, ""),
        Case("context-analysis-selected-controller-read", CONTEXT_FILES, "check-context-isolation.py", context_args("--controller-module", "application/lesson/driving_layer/missing.py"), 0, ""),
        Case("context-analysis-selected-root-escape", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "../outside.py", "--controller-module", "application/lesson/driving_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 0, "", allowed_arg_issues=frozenset({"root-escape:--api-module"})),
        Case("context-analysis-incomplete-code-source-args", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1"), 0, "", allowed_arg_issues=frozenset({"missing:--api-module", "missing:--controller-module", "missing:--scope-bc"})),
        Case("context-analysis-missing-scope-bc-production-tree", CONTEXT_FILES, "check-context-isolation.py", context_args("--scope-bc", "catalog"), 0, ""),
        Case("context-clean-auto-profile-legacy-rules", CONTEXT_FILES, "check-context-isolation.py", AUTO_PROFILE_ARGS, 0, ""),
        Case("context-clean-legacy-positional-help", CONTEXT_FILES, "check-context-isolation.py", (TARGET_DIR,), 0, ""),
        Case("context-tests-migrations-cache-still-scanned", {**CONTEXT_FILES, "application/lesson/application_layer/tests/test_leak.py": "from ninja import Status\n", "application/lesson/application_layer/migrations/0001_leak.py": "from ninja import Status\n", "application/lesson/application_layer/.cache/leak.py": "from ninja import Status\n", "application/lesson/application_layer/.venv/leak.py": "from ninja import Status\n"}, "check-context-isolation.py", context_args(), 2, "blocker"),
        Case("context-generated-path-still-scanned", {**CONTEXT_FILES, ".gitignore": "application/lesson/application_layer/ignored_leak.py\n", "application/lesson/application_layer/generated/leak.py": "from application.lesson.driving_layer.open_host_service.public.contract.request.lesson_query_request import LessonQueryRequest\n"}, "check-context-isolation.py", context_args(), 2, "blocker", baseline_files={**CONTEXT_FILES, ".gitignore": "application/lesson/application_layer/ignored_leak.py\n"}),
        Case("context-git-ignored-path-still-scanned", {**CONTEXT_FILES, ".gitignore": "application/lesson/application_layer/ignored_leak.py\n", "application/lesson/application_layer/ignored_leak.py": "from application.lesson.driving_layer.open_host_service.public.contract.request.lesson_query_request import LessonQueryRequest\n"}, "check-context-isolation.py", context_args(), 2, "blocker", baseline_files={**CONTEXT_FILES, ".gitignore": "application/lesson/application_layer/ignored_leak.py\n"}),
        # Reviewer-only: dynamic/relative import equivalents, semantic root
        # mapping lookalikes, and source-surface membership completeness.
    ]


COMPOSITION_CLEAN_FILES: Final = {
    "application/lesson/application_layer/use_case.py": "def run(): return None\n",
    "application/lesson/composition_root/dependency_wiring.py": "def build_use_case(): return object()\n",
}

REGISTRAR_FILES: Final = {
    "config/api.py": """from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
""",
    "application/lesson/driving_layer/controller.py": "class LessonController: pass\n",
    "application/lesson/driving_layer/api/api_router.py": """from .controller import LessonController

def register_lesson_api(api):
    api.register_controllers(LessonController)
""",
    "application/catalog/driving_layer/controller.py": "class CatalogController: pass\n",
    "application/catalog/driving_layer/api/api_router.py": """from .controller import CatalogController

def register_catalog_api(api):
    api.register_controllers(CatalogController)
""",
    "config/urls.py": """from config.api import api
from application.lesson.driving_layer.api.api_router import register_lesson_api
from application.catalog.driving_layer.api.api_router import register_catalog_api

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
        "application/lesson/driving_layer/api/api_router.py",
        "--registrar-module",
        "application/catalog/driving_layer/api/api_router.py",
        *extra,
    )


def composition_cases() -> list[Case]:
    """Legacy DI placement and future URLconf/registrar composition cases."""
    registrar_imports_api = REGISTRAR_FILES["application/lesson/driving_layer/api/api_router.py"].replace(
        "from .controller import LessonController",
        "from .controller import LessonController\nfrom config.api import api",
    )
    top_level_registration = (
        REGISTRAR_FILES["application/lesson/driving_layer/api/api_router.py"]
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
        Case("composition-clean-root-folder", COMPOSITION_CLEAN_FILES, "check-composition-root.py", (TARGET_DIR,), 0, ""),
        Case("composition-v2-single-root-file-off-tree", {"application/lesson/application_layer/use_case.py": "def run(): return None\n", "application/lesson/composition_root.py": "def build_use_case(): return object()\n"}, "check-composition-root.py", (TARGET_DIR,), 2, "BLOCKER"),
        Case("composition-legacy-clean-empty-application-layer-exempt", {"application/catalog/application_layer/__init__.py": ""}, "check-composition-root.py", (TARGET_DIR,), 0, ""),
        Case("composition-legacy-v1-off-tree-folder", {**COMPOSITION_CLEAN_FILES, "application/lesson/composition/provider.py": "def provide(): return object()\n"}, "check-composition-root.py", (TARGET_DIR,), 2, "BLOCKER"),
        Case("composition-legacy-v2-misplaced-composition-root", {"application/lesson/application_layer/use_case.py": "def run(): return None\n", "application/lesson/driven_layer/composition_root.py": "def build(): return object()\n"}, "check-composition-root.py", (TARGET_DIR,), 2, "BLOCKER"),
        Case("composition-legacy-v3-required-root-absent", {"application/lesson/application_layer/use_case.py": "def run(): return None\n"}, "check-composition-root.py", (TARGET_DIR,), 2, "BLOCKER"),
        Case("composition-code-clean-selected-registrars-called-once", REGISTRAR_FILES, "check-composition-root.py", composition_args(), 0, ""),
        Case("composition-code-clean-unselected-preserve-urlconf-registrar", {**REGISTRAR_FILES, "legacy/api.py": "api = object()\n", "legacy/urls.py": "from legacy.api import api\nfrom legacy.registrar import register_legacy_api\nregister_legacy_api(api)\n", "legacy/registrar.py": "def register_legacy_api(api): api.register_controllers(object)\n"}, "check-composition-root.py", composition_args(), 0, ""),
        Case("composition-registrar-rebinds-api-parameter", with_files(("application/lesson/driving_layer/api/api_router.py", "from .controller import LessonController\n\ndef register_lesson_api(api):\n    api = replacement_api\n    api.register_controllers(LessonController)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registrar-handler-sees-rebound-api-parameter", with_files(("application/lesson/driving_layer/api/api_router.py", "from .controller import LessonController\n\ndef register_lesson_api(api):\n    try:\n        api = replacement_api\n        raise RuntimeError\n    except RuntimeError:\n        api.register_controllers(LessonController)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registrar-imports-project-api", with_files(("application/lesson/driving_layer/api/api_router.py", registrar_imports_api), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registrar-module-top-level-register-controllers", with_files(("application/lesson/driving_layer/api/api_router.py", top_level_registration), ("application/lesson/driving_layer/registration_probe.py", "class RegistrationProbe:\n    def register_controllers(self, controller): pass\n\n\nregistration_probe = RegistrationProbe()\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-urlconf-omits-registrar-call", with_files(("config/urls.py", REGISTRAR_FILES["config/urls.py"].replace("register_catalog_api(api)\n", "")), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-urlconf-duplicates-registrar-call", with_files(("config/urls.py", REGISTRAR_FILES["config/urls.py"] + "register_lesson_api(api)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-registration-occurs-outside-registrar", with_files(("config/urls.py", REGISTRAR_FILES["config/urls.py"] + "api.register_controllers(object)\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-code-v1-di-still-blocked", {**REGISTRAR_FILES, "application/lesson/composition/provider.py": "def provide(): return object()\n"}, "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-code-v2-di-still-blocked", {**REGISTRAR_FILES, "application/lesson/driven_layer/composition_root.py": "def build(): return object()\n"}, "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-code-v3-di-still-blocked", {**REGISTRAR_FILES, "application/lesson/application_layer/use_case.py": "def run(): return None\n"}, "check-composition-root.py", composition_args(), 2, "BLOCKER"),
        Case("composition-preserve-common-selectors-registrar-na", inactive_registrar_files, "check-composition-root.py", preserve_common_args, 0, ""),
        Case("composition-preserve-registrar-rules-na", inactive_registrar_files, "check-composition-root.py", preserve_selector_args, 0, ""),
        Case("composition-auto-registrar-rules-na", inactive_registrar_files, "check-composition-root.py", auto_selector_args, 0, ""),
        Case("composition-preserve-existing-di-v3-still-runs", {**inactive_registrar_files, "application/legacy/application_layer/use_case.py": "def run(): return None\n"}, "check-composition-root.py", preserve_selector_args, 2, "BLOCKER"),
        Case("composition-auto-existing-di-v1-still-runs", {**inactive_registrar_files, "application/legacy/domain_layer/model.py": "class Model: pass\n", "application/legacy/composition/provider.py": "def provide(): return object()\n"}, "check-composition-root.py", auto_selector_args, 2, "BLOCKER"),
        Case("composition-analysis-missing-urlconf-selector", REGISTRAR_FILES, "check-composition-root.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--registrar-module", "application/lesson/driving_layer/api/api_router.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--urlconf-module"})),
        Case("composition-analysis-missing-registrar-selector", REGISTRAR_FILES, "check-composition-root.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--urlconf-module", "config/urls.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--registrar-module"})),
        Case("composition-analysis-duplicate-urlconf-selector", REGISTRAR_FILES, "check-composition-root.py", composition_args("--urlconf-module", "config/urls.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"cardinality:--urlconf-module"})),
        Case("composition-analysis-duplicate-registrar-selector", REGISTRAR_FILES, "check-composition-root.py", composition_args("--registrar-module", "application/lesson/driving_layer/api/api_router.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"duplicate:--registrar-module"})),
        Case("composition-analysis-urlconf-registrar-overlap", REGISTRAR_FILES, "check-composition-root.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--urlconf-module", "config/urls.py", "--registrar-module", "config/urls.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"overlap:--urlconf-module/--registrar-module"})),
        Case("composition-analysis-selected-urlconf-syntax", with_files(("config/urls.py", "urlpatterns = [\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 1, "사용 오류"),
        Case("composition-analysis-selected-registrar-syntax", with_files(("application/lesson/driving_layer/api/api_router.py", "def broken(:\n"), base=REGISTRAR_FILES), "check-composition-root.py", composition_args(), 1, "사용 오류"),
        Case("composition-analysis-selected-registrar-read", REGISTRAR_FILES, "check-composition-root.py", composition_args("--registrar-module", "application/missing/driving_layer/api/api_router.py"), 1, "사용 오류"),
        Case("composition-analysis-selected-root-escape", REGISTRAR_FILES, "check-composition-root.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--urlconf-module", "../outside.py", "--registrar-module", "application/lesson/driving_layer/api/api_router.py", "--registrar-module", "application/catalog/driving_layer/api/api_router.py"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--urlconf-module"})),
        Case("composition-fp-tests-migrations-cache-venv", {**COMPOSITION_CLEAN_FILES, "application/lesson/tests/composition_root.py": "pass\n", "application/lesson/migrations/composition_root.py": "pass\n", "application/lesson/.cache/composition_root.py": "pass\n", "application/lesson/.venv/composition_root.py": "pass\n"}, "check-composition-root.py", (TARGET_DIR,), 0, ""),
        Case("composition-fp-unignored-generated-path", {**COMPOSITION_CLEAN_FILES, ".gitignore": "application/lesson/driven_layer/ignored/composition_root.py\n", "application/lesson/driven_layer/generated/composition_root.py": "pass\n"}, "check-composition-root.py", (TARGET_DIR,), 0, "", baseline_files={**COMPOSITION_CLEAN_FILES, ".gitignore": "application/lesson/driven_layer/ignored/composition_root.py\n"}),
        Case("composition-fp-git-ignored-selected-path", {**COMPOSITION_CLEAN_FILES, ".gitignore": "application/lesson/driven_layer/ignored/composition_root.py\n", "application/lesson/driven_layer/ignored/composition_root.py": "pass\n"}, "check-composition-root.py", (TARGET_DIR,), 0, "", baseline_files={**COMPOSITION_CLEAN_FILES, ".gitignore": "application/lesson/driven_layer/ignored/composition_root.py\n"}),
        # Reviewer-only: dynamic/re-export calls and semantic completeness of
        # the controller set registered inside each registrar.
    ]


OPENAPI_CONTROLLER = """from ninja import Router, Status
from application.lesson.driving_layer.api.bc_error_schema import LessonConflictError, LessonErrorSchema, LessonNotFoundError

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: LessonErrorSchema, 409: LessonErrorSchema})
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
    "application/lesson/driving_layer/controller.py": OPENAPI_CONTROLLER,
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
        "application/lesson/driving_layer/controller.py",
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
            "application/lesson/driving_layer/controller.py",
            """from ninja import Router

router = Router()


@router.get("/{lesson_id}", response={200: dict})
def get_lesson(request, lesson_id: int):
    return {"id": lesson_id}
""",
        ),
        ("application/lesson/driving_layer/api/bc_error_schema.py", "<REMOVE>"),
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
        'response={200: dict, 404: LessonErrorSchema, 409: LessonErrorSchema})',
        'response={200: dict, 404: LessonErrorSchema, 409: LessonErrorSchema}, openapi_extra={"security": [{"Bearer": []}], "examples": {"ok": {"value": {"id": 1}}}})',
    )
    missing_409 = OPENAPI_CONTROLLER.replace(
        "response={200: dict, 404: LessonErrorSchema, 409: LessonErrorSchema}",
        "response={200: dict, 404: LessonErrorSchema}",
    )
    framework_base = OPENAPI_CONTROLLER.replace(
        "    if lesson_id == 0:\n        error = LessonNotFoundError()\n        return Status(error.status, error)\n",
        "",
    )

    def framework_advertisement(status: int) -> str:
        return framework_base.replace(
            "response={200: dict, 404: LessonErrorSchema, 409: LessonErrorSchema}",
            f"response={{200: dict, 409: LessonErrorSchema, {status}: LessonErrorSchema}}",
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
        "application/legacy/driving_layer/controller.py",
        "--scope-bc",
        "legacy",
        "--error-bc",
        "legacy",
    )
    framework_extra = OPENAPI_CONTROLLER.replace(
        'response={200: dict, 404: LessonErrorSchema, 409: LessonErrorSchema})',
        'response={200: dict, 404: LessonErrorSchema, 409: LessonErrorSchema}, openapi_extra={"responses": {"401": {"description": "unauthorized"}}})',
    )
    override_api = """from ninja_extra import NinjaExtraAPI

class ProjectAPI(NinjaExtraAPI):
    def get_openapi_schema(self, *args, **kwargs):
        schema = super().get_openapi_schema(*args, **kwargs)
        schema["x-errors"] = True
        return schema

api = ProjectAPI()
"""
    no_op_override_api = """from ninja_extra import NinjaExtraAPI


class ProjectAPI(NinjaExtraAPI):
    def get_openapi_schema(self, *args, **kwargs):
        return super().get_openapi_schema(*args, **kwargs)


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
            "from application.lesson.driving_layer.api.bc_error_schema import "
            "LessonErrorSchema, LessonNotFoundError\n\n"
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
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError

router = Router()

match 1:
    case 1:
        @router.get('/{lesson_id}', response={200: dict})
        def get_lesson(request, lesson_id: int):
            error = LessonNotFoundError()
            return Status(error.status, error)
"""

    no_direct_common = """from ninja import Router
from framework.ninja.framework_error_schema import FrameworkErrorSchema

router = Router()

@router.get('/lessons', response={200: dict, 401: FrameworkErrorSchema})
def list_lessons(request):
    return []
"""
    no_direct_concrete = """from ninja import Router
from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError

router = Router()

@router.get('/lessons', response={200: dict, 401: LessonNotFoundError})
def list_lessons(request):
    return []
"""
    no_direct_base = no_direct_concrete.replace(
        "LessonNotFoundError", "LessonErrorSchema"
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
        "application/lesson/driving_layer/controller.py",
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
from application.lesson.driving_layer.api.bc_error_schema import LessonConflictError, LessonErrorSchema, LessonNotFoundError

router = Router()

@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorSchema, 409: LessonErrorSchema})
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
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError

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
    module_static_status_error_out = LESSON_ERROR_OUT.replace(
        "from enum import StrEnum",
        "from enum import StrEnum\n\n_NOT_FOUND_STATUS = 404",
    ).replace("status: int = 404", "status: int = _NOT_FOUND_STATUS", 1)
    class_static_status_error_out = LESSON_ERROR_OUT.replace(
        '    code: LessonErrorCode = LessonErrorCode.NOT_FOUND\n    title: str = "Lesson not found"',
        '    _DEFAULT_HTTP_STATUS = 404\n    code: LessonErrorCode = LessonErrorCode.NOT_FOUND\n    title: str = "Lesson not found"',
        1,
    ).replace("status: int = 404", "status: int = _DEFAULT_HTTP_STATUS", 1)
    postponed_common = """from __future__ import annotations
from ninja import Schema

_DEFAULT_HTTP_STATUS = 500


class FrameworkErrorSchema(Schema):
    error_type: str
    marker: (_DEFAULT_HTTP_STATUS := int) = 1
    http_status: int = _DEFAULT_HTTP_STATUS
    msg: str
"""
    postponed_lesson = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = 'lesson_not_found'


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = LessonErrorCode.NOT_FOUND
    msg: str = 'missing'
"""
    postponed_controller = """from ninja import Router, Status
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorSchema, LessonNotFoundError

router = Router()


@router.get('/{lesson_id}', response={200: dict, 500: LessonErrorSchema})
def get_lesson(request, lesson_id: int):
    error = LessonNotFoundError()
    return Status(error.http_status, error)
"""
    direct_alias_status_controller = """from ninja import Router, Status
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorSchema})
def get_lesson(request, lesson_id: int):
    error = LessonErrorSchema(type=LessonErrorCode.NOT_FOUND, http_status=404, msg='missing')
    return Status(error.http_status, error)
"""
    generated_alias_common = """from ninja import Schema
from pydantic.alias_generators import to_camel


class FrameworkErrorSchema(Schema):
    error_type: str
    http_status: int = 500
    msg: str
    model_config = {'alias_generator': to_camel}
"""
    generated_alias_legacy_common = generated_alias_common.replace(
        "    model_config = {'alias_generator': to_camel}",
        "    class Config:\n        alias_generator = to_camel",
    )
    generated_alias_lesson = """from enum import StrEnum
from framework.ninja.framework_error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = 'lesson_not_found'


class LessonErrorSchema(FrameworkErrorSchema):
    error_type: LessonErrorCode


class LessonNotFoundError(LessonErrorSchema):
    error_type: LessonErrorCode = LessonErrorCode.NOT_FOUND
    http_status: int = 404
    msg: str = 'missing'
"""
    generated_alias_controller = """from ninja import Router, Status
from application.lesson.driving_layer.api.bc_error_schema import LessonErrorCode, LessonErrorSchema

router = Router()


@router.get('/{lesson_id}', response={200: dict, 404: LessonErrorSchema})
def get_lesson(request, lesson_id: int):
    error = LessonErrorSchema(errorType=LessonErrorCode.NOT_FOUND, httpStatus=404, msg='missing')
    return Status(error.http_status, error)
"""
    custom_alias_openapi_common = generated_alias_common.replace(
        "from pydantic.alias_generators import to_camel",
        "from pydantic import ConfigDict\nfrom framework.ninja.aliasing import wire_name",
    ).replace(
        "model_config = {'alias_generator': to_camel}",
        "model_config = ConfigDict(alias_generator=wire_name)",
    )
    custom_alias_openapi_controller = generated_alias_controller.replace(
        "errorType=",
        "wire_error_type=",
    ).replace("httpStatus=", "wire_http_status=").replace(
        "msg='missing'",
        "wire_msg='missing'",
    )
    custom_alias_openapi_wrong_declaration = custom_alias_openapi_controller.replace(
        "404: LessonErrorSchema",
        "500: LessonErrorSchema",
    )
    project_config_support = """from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


def build_config():
    return ConfigDict(alias_generator=to_camel)
"""
    shadowed_project_config_support = project_config_support + """

build_config = lambda: ConfigDict(validate_by_name=True)
"""
    rebound_project_config_global_support = project_config_support + """

to_camel = lambda value: f'wire_{value}'
"""
    indirectly_shadowed_project_config_support = project_config_support + """

globals()['build_config'] = lambda: ConfigDict(
    alias_generator=lambda value: f'actual_{value}'
)
"""
    namedexpr_shadowed_project_config_support = project_config_support + """

shadow = (
    build_config := lambda: ConfigDict(
        alias_generator=lambda value: f'actual_{value}'
    )
)
"""
    while_shadowed_project_config_support = project_config_support + """

while True:
    build_config = lambda: ConfigDict(
        alias_generator=lambda value: f'actual_{value}'
    )
    break
"""
    async_shadowed_project_config_support = project_config_support + """

async def build_config():
    return ConfigDict(alias_generator=lambda value: f'actual_{value}')
"""
    project_config_openapi_common = generated_alias_common.replace(
        "from pydantic.alias_generators import to_camel",
        "from framework.ninja.configs import build_config",
    ).replace(
        "model_config = {'alias_generator': to_camel}",
        "model_config = build_config()",
    )
    project_config_wrong_declaration = generated_alias_controller.replace(
        "404: LessonErrorSchema", "500: LessonErrorSchema"
    )
    complex_alias_support = """def wire_name(value: str) -> str:
    if value.startswith('_'):
        return value
    return f'wire_{value}'
"""
    repr_alias_support = """def wire_name(value: str) -> str:
    return f'wire_{value!r}'
"""
    shadowed_alias_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


wire_name = lambda value: f'actual_{value}'
"""
    indirectly_shadowed_alias_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


globals()['wire_name'] = lambda value: f'actual_{value}'
"""
    namedexpr_shadowed_alias_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


shadow = (wire_name := lambda value: f'actual_{value}')
"""
    try_shadowed_alias_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


try:
    wire_name = lambda value: f'actual_{value}'
except Exception:
    pass
"""
    async_shadowed_alias_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


async def wire_name(value: str) -> str:
    return f'actual_{value}'
"""
    star_shadowed_alias_support = """def Field(value: str) -> str:
    return f'wire_{value}'


from pydantic import *
"""
    star_shadowed_openapi_common = custom_alias_openapi_common.replace(
        "wire_name", "Field"
    )
    set_call_shadowed_alias_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


def set():
    globals()['wire_name'] = lambda value: f'actual_{value}'


shadow = set()
"""
    iterator_shadowed_alias_support = """def wire_name(value: str) -> str:
    return f'wire_{value}'


from framework.ninja.mutator import EVIL

for _ in EVIL:
    pass
"""
    openapi_iterator_mutator_support = """import sys


class Evil:
    def __iter__(self):
        target = sys.modules['framework.ninja.aliasing']
        target.wire_name = lambda value: f'actual_{value}'
        return iter(())


EVIL = Evil()
"""
    pure_alias_module_control = """'pure alias helper module'

__all__ = ['wire_name']
MARKER = 'stable'


def wire_name(value: str) -> str:
    return f'wire_{value}'
"""
    nested_status_lesson = LESSON_ERROR_OUT.replace(
        "from enum import StrEnum",
        "from enum import StrEnum\nfrom typing import Annotated\nfrom pydantic import Field",
    ).replace(
        "    status: int = 404",
        "    status: Annotated[Annotated[int, Field(default=404)], Field(default=500)]",
        1,
    )
    nested_status_correct_controller = OPENAPI_CONTROLLER.replace(
        "404: LessonErrorSchema", "500: LessonErrorSchema"
    )
    sentinel_status_lesson = LESSON_ERROR_OUT.replace(
        "from enum import StrEnum",
        "from enum import StrEnum\nfrom typing import Annotated\nfrom pydantic import Field\nfrom pydantic_core import PydanticUndefined",
    ).replace(
        "    status: int = 404",
        "    status: Annotated[int, Field(default=404)] = PydanticUndefined",
        1,
    )
    field_sentinel_status_lesson = sentinel_status_lesson.replace(
        "= PydanticUndefined", "= Field(default=PydanticUndefined)", 1
    )
    clear_factory_status_lesson = sentinel_status_lesson.replace(
        "= PydanticUndefined", "= Field(default_factory=None)", 1
    )
    required_status_lesson = sentinel_status_lesson.replace(
        "Annotated[int, Field(default=404)] = PydanticUndefined",
        "int = PydanticUndefined",
        1,
    )
    computed_status_common = """from ninja import Schema
from pydantic import computed_field


class FrameworkErrorSchema(Schema):
    error_type: str
    msg: str
    is_show: bool

    @computed_field
    @property
    def transport_code(self) -> int:
        return 404
"""
    computed_status_controller = CUSTOM_CONTROLLER.replace(
        "Status(404, error)", "Status(error.transport_code, error)"
    )
    dynamic_computed_status_common = computed_status_common.replace(
        "        return 404", "        return int(self.msg)"
    )
    plain_computed_status_common = computed_status_common.replace(
        "    @property\n", ""
    )
    cached_computed_status_common = computed_status_common.replace(
        "from ninja import Schema",
        "from functools import cached_property\nfrom ninja import Schema",
    ).replace("    @property", "    @cached_property")
    return [
        Case("openapi-nested-annotated-outer-status-default-wins", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", nested_status_lesson), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-clean-nested-annotated-outer-status-declaration", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", nested_status_lesson), ("application/lesson/driving_layer/controller.py", nested_status_correct_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-annotated-status-default-survives-undefined", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", sentinel_status_lesson), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-annotated-status-default-survives-field-undefined", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", field_sentinel_status_lesson), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-annotated-status-default-survives-factory-clear", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", clear_factory_status_lesson), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-analysis-truly-required-status-default", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", required_status_lesson), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-clean-computed-literal-body-status", with_files(("framework/ninja/framework_error_schema.py", computed_status_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", computed_status_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-analysis-dynamic-computed-body-status", with_files(("framework/ninja/framework_error_schema.py", dynamic_computed_status_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", computed_status_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-clean-plain-computed-literal-status", with_files(("framework/ninja/framework_error_schema.py", plain_computed_status_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", computed_status_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-cached-computed-literal-status", with_files(("framework/ninja/framework_error_schema.py", cached_computed_status_common), ("application/lesson/driving_layer/api/bc_error_schema.py", CUSTOM_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", computed_status_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-module-static-status-default", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", module_static_status_error_out), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-class-static-status-default", with_files(("application/lesson/driving_layer/api/bc_error_schema.py", class_static_status_error_out), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-postponed-annotation-does-not-rebind-static-status", with_files(("framework/ninja/framework_error_schema.py", postponed_common), ("application/lesson/driving_layer/api/bc_error_schema.py", postponed_lesson), ("application/lesson/driving_layer/controller.py", postponed_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-direct-base-aliased-status-override", with_files(("framework/ninja/framework_error_schema.py", ALIASED_STATUS_COMMON_ERROR_OUT), ("application/lesson/driving_layer/api/bc_error_schema.py", ALIASED_STATUS_LESSON_ERROR_OUT), ("application/lesson/driving_layer/controller.py", direct_alias_status_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-dict-alias-generator-direct-status", with_files(("framework/ninja/framework_error_schema.py", generated_alias_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", generated_alias_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-legacy-config-alias-generator-direct-status", with_files(("framework/ninja/framework_error_schema.py", generated_alias_legacy_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", generated_alias_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-analysis-digit-string-response-status", with_files(("application/lesson/driving_layer/controller.py", OPENAPI_CONTROLLER.replace("404: LessonErrorSchema", "'404': LessonErrorSchema")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-clean-statically-provable-custom-alias-generator", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-analysis-custom-alias-generator-repr-conversion", with_files(("framework/ninja/aliasing.py", repr_alias_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-custom-alias-generator-final-shadow", with_files(("framework/ninja/aliasing.py", shadowed_alias_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-dynamic-shape-marker-does-not-hide-api-override", with_files(("config/api.py", no_op_override_api), ("framework/ninja/aliasing.py", shadowed_alias_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "get_openapi_schema override"),
        Case("openapi-analysis-custom-alias-generator-indirect-final-shadow", with_files(("framework/ninja/aliasing.py", indirectly_shadowed_alias_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-custom-alias-generator-namedexpr-shadow", with_files(("framework/ninja/aliasing.py", namedexpr_shadowed_alias_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-custom-alias-generator-try-shadow", with_files(("framework/ninja/aliasing.py", try_shadowed_alias_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-custom-alias-generator-async-shadow", with_files(("framework/ninja/aliasing.py", async_shadowed_alias_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-custom-alias-generator-star-import-shadow", with_files(("framework/ninja/aliasing.py", star_shadowed_alias_support), ("framework/ninja/framework_error_schema.py", star_shadowed_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-custom-alias-generator-set-call-shadow", with_files(("framework/ninja/aliasing.py", set_call_shadowed_alias_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-custom-alias-generator-imported-iterator-shadow", with_files(("framework/ninja/aliasing.py", iterator_shadowed_alias_support), ("framework/ninja/mutator.py", openapi_iterator_mutator_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-clean-pure-custom-alias-module-control", with_files(("framework/ninja/aliasing.py", pure_alias_module_control), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-custom-alias-generator-wrong-status", with_files(("framework/ninja/aliasing.py", 'def wire_name(value: str) -> str:\n    return f"wire_{value}"\n'), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_wrong_declaration), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-clean-statically-provable-project-config-builder", with_files(("framework/ninja/configs.py", project_config_support), ("framework/ninja/framework_error_schema.py", project_config_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", generated_alias_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-analysis-project-config-builder-final-shadow", with_files(("framework/ninja/configs.py", shadowed_project_config_support), ("framework/ninja/framework_error_schema.py", project_config_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", generated_alias_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-project-config-builder-global-rebind", with_files(("framework/ninja/configs.py", rebound_project_config_global_support), ("framework/ninja/framework_error_schema.py", project_config_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", generated_alias_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-project-config-builder-indirect-final-shadow", with_files(("framework/ninja/configs.py", indirectly_shadowed_project_config_support), ("framework/ninja/framework_error_schema.py", project_config_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", generated_alias_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-project-config-builder-namedexpr-shadow", with_files(("framework/ninja/configs.py", namedexpr_shadowed_project_config_support), ("framework/ninja/framework_error_schema.py", project_config_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", generated_alias_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-project-config-builder-while-shadow", with_files(("framework/ninja/configs.py", while_shadowed_project_config_support), ("framework/ninja/framework_error_schema.py", project_config_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", generated_alias_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-analysis-project-config-builder-async-shadow", with_files(("framework/ninja/configs.py", async_shadowed_project_config_support), ("framework/ninja/framework_error_schema.py", project_config_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", generated_alias_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case("openapi-project-config-builder-wrong-status", with_files(("framework/ninja/configs.py", project_config_support), ("framework/ninja/framework_error_schema.py", project_config_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", project_config_wrong_declaration), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-dynamic-shape-runtime-proof-handoff", with_files(("framework/ninja/aliasing.py", complex_alias_support), ("framework/ninja/framework_error_schema.py", custom_alias_openapi_common), ("application/lesson/driving_layer/api/bc_error_schema.py", generated_alias_lesson), ("application/lesson/driving_layer/controller.py", custom_alias_openapi_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED"),
        Case(
            "openapi-clean-project-approved-custom-shape-literal-status",
            with_files(
                ("framework/ninja/framework_error_schema.py", CUSTOM_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    CUSTOM_LESSON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/controller.py",
                    CUSTOM_CONTROLLER,
                ),
                base=OPENAPI_FILES,
            ),
            "check-openapi-error-declaration.py",
            openapi_args(),
            0,
            "",
        ),
        Case(
            "openapi-clean-project-approved-aliased-body-status-field",
            with_files(
                (
                    "framework/ninja/framework_error_schema.py",
                    ALIASED_STATUS_COMMON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    ALIASED_STATUS_LESSON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/controller.py",
                    ALIASED_STATUS_CONTROLLER,
                ),
                base=OPENAPI_FILES,
            ),
            "check-openapi-error-declaration.py",
            openapi_args(),
            0,
            "",
        ),
        Case(
            "openapi-clean-annotated-body-status-default",
            with_files(
                ("framework/ninja/framework_error_schema.py", ANNOTATED_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    ANNOTATED_LESSON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/controller.py",
                    ANNOTATED_CONTROLLER,
                ),
                base=OPENAPI_FILES,
            ),
            "check-openapi-error-declaration.py",
            openapi_args(),
            0,
            "",
        ),
        Case(
            "openapi-clean-annotated-base-status-default",
            with_files(
                ("framework/ninja/framework_error_schema.py", ANNOTATED_COMMON_ERROR_OUT),
                (
                    "application/lesson/driving_layer/api/bc_error_schema.py",
                    ANNOTATED_LESSON_ERROR_OUT,
                ),
                (
                    "application/lesson/driving_layer/controller.py",
                    ANNOTATED_BASE_CONTROLLER,
                ),
                base=OPENAPI_FILES,
            ),
            "check-openapi-error-declaration.py",
            openapi_args(),
            0,
            "",
        ),
        Case("openapi-clean-direct-404-409-same-bc-base", OPENAPI_FILES, "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-framework-statuses-not-advertised", OPENAPI_FILES, "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-separated-preserve-response-behavior", clean_with_preserve, "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-security-examples-metadata", with_files(("application/lesson/driving_layer/controller.py", metadata_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-empty-error-bc", empty_error_bc_files, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "application/lesson/driving_layer/controller.py", "--scope-bc", "lesson"), 0, ""),
        Case("openapi-returned-409-missing-from-response", with_files(("application/lesson/driving_layer/controller.py", missing_409), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-returned-error-mapped-to-other-bc-base", with_files(("application/catalog/driving_layer/api/bc_error_schema.py", CATALOG_DUPLICATE_ERROR_OUT), ("application/lesson/driving_layer/controller.py", OPENAPI_CONTROLLER.replace("409: LessonErrorSchema", "409: CatalogErrorSchema").replace("from application.lesson.driving_layer.api.bc_error_schema import", "from application.catalog.driving_layer.api.bc_error_schema import CatalogErrorSchema\nfrom application.lesson.driving_layer.api.bc_error_schema import")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args("--scope-bc", "catalog", "--error-bc", "catalog"), 2, "BLOCKER"),
        Case("openapi-returned-error-mapped-to-common-base", with_files(("application/lesson/driving_layer/controller.py", OPENAPI_CONTROLLER.replace("409: LessonErrorSchema", "409: FrameworkErrorSchema").replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom framework.ninja.framework_error_schema import FrameworkErrorSchema")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-returned-error-mapped-to-concrete", with_files(("application/lesson/driving_layer/controller.py", OPENAPI_CONTROLLER.replace("409: LessonErrorSchema", "409: LessonConflictError")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-401-bc-error-advertised", with_files(("application/lesson/driving_layer/controller.py", framework_advertisement(401)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-403-bc-error-advertised", with_files(("application/lesson/driving_layer/controller.py", framework_advertisement(403)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-route-404-bc-error-advertised", with_files(("application/lesson/driving_layer/controller.py", framework_advertisement(404)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-422-bc-error-advertised", with_files(("application/lesson/driving_layer/controller.py", framework_advertisement(422)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-429-bc-error-advertised", with_files(("application/lesson/driving_layer/controller.py", framework_advertisement(429)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-500-bc-error-advertised", with_files(("application/lesson/driving_layer/controller.py", framework_advertisement(500)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-response-openapi-extra", with_files(("application/lesson/driving_layer/controller.py", framework_extra), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-get-openapi-schema-override", with_files(("config/api.py", override_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-get-openapi-schema-monkeypatch", with_files(("config/api.py", monkeypatch_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-get-openapi-schema-postprocessor", with_files(("config/api.py", postprocessor_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-preserve-untouched-openapi-extra-blocked", {"legacy/api.py": "api = object()\n", "application/legacy/driving_layer/controller.py": preserve_extra}, "check-openapi-error-declaration.py", preserve_args, 2, "#63", baseline_files={"legacy/api.py": "api = object()\n", "application/legacy/driving_layer/controller.py": preserve_extra}),
        Case("openapi-preserve-touched-openapi-extra-blocked", {"legacy/api.py": "api = object()\n", "application/legacy/driving_layer/controller.py": preserve_extra}, "check-openapi-error-declaration.py", preserve_args, 2, "BLOCKER", baseline_files={"legacy/api.py": "api = object()\n", "application/legacy/driving_layer/controller.py": preserve_files["legacy/controller.py"]}),
        Case("openapi-analysis-unresolved-required-response-mapping", with_files(("application/lesson/driving_layer/controller.py", OPENAPI_CONTROLLER.replace("response={200: dict, 404: LessonErrorSchema, 409: LessonErrorSchema}", "response=build_responses()")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-analysis-api-controller-overlap", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "config/api.py", "--controller-module", "config/api.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"overlap:--api-module/--controller-module"})),
        Case("openapi-analysis-selected-controller-syntax", with_files(("application/lesson/driving_layer/controller.py", "def broken(:\n"), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-analysis-selected-controller-read", OPENAPI_FILES, "check-openapi-error-declaration.py", openapi_args("--controller-module", "application/lesson/driving_layer/missing.py"), 1, "사용 오류"),
        Case("openapi-analysis-selected-root-escape", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--api-module", "../outside.py", "--controller-module", "application/lesson/driving_layer/controller.py", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류", allowed_arg_issues=frozenset({"root-escape:--api-module"})),
        Case("openapi-clean-auto-profile-legacy-rules", OPENAPI_FILES, "check-openapi-error-declaration.py", AUTO_PROFILE_ARGS, 0, ""),
        Case("openapi-analysis-missing-code-source-args", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1"), 1, "사용 오류", allowed_arg_issues=frozenset({"missing:--api-module", "missing:--controller-module", "missing:--scope-bc"})),
        Case("openapi-clean-legacy-positional-help", OPENAPI_FILES, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, ""),
        Case("openapi-fp-tests-migrations-cache-venv", {**OPENAPI_FILES, "application/lesson/driving_layer/tests/test_openapi.py": excluded_violation, "application/lesson/driving_layer/migrations/0001_openapi.py": excluded_violation, "application/lesson/driving_layer/.cache/openapi.py": excluded_violation, "application/lesson/driving_layer/.venv/openapi.py": excluded_violation}, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, ""),
        Case("openapi-fp-unignored-generated-path", {**OPENAPI_FILES, ".gitignore": "application/lesson/driving_layer/ignored_openapi.py\n", "application/lesson/driving_layer/generated/openapi.py": excluded_violation}, "check-openapi-error-declaration.py", (TARGET_DIR,), 0, "", baseline_files={**OPENAPI_FILES, ".gitignore": "application/lesson/driving_layer/ignored_openapi.py\n"}),
        Case("openapi-git-ignored-path-still-scanned", {**OPENAPI_FILES, ".gitignore": "application/lesson/driving_layer/ignored_openapi.py\n", "application/lesson/driving_layer/ignored_openapi.py": excluded_violation}, "check-openapi-error-declaration.py", (TARGET_DIR,), 2, "#63", baseline_files={**OPENAPI_FILES, ".gitignore": "application/lesson/driving_layer/ignored_openapi.py\n"}),
        Case("openapi-flow-match-return-missing-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(match_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2 if sys.version_info >= (3, 10) else 1, "BLOCKER" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-flow-match-return-correct-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(match_body, "{200: dict, 404: LessonErrorSchema}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-flow-module-match-operation", with_files(("application/lesson/driving_layer/controller.py", module_match_controller), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2 if sys.version_info >= (3, 10) else 1, "BLOCKER" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-flow-trystar-return-missing-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(trystar_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2 if sys.version_info >= (3, 11) else 1, "BLOCKER" if sys.version_info >= (3, 11) else "사용 오류"),
        Case("openapi-flow-trystar-return-correct-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(trystar_body, "{200: dict, 404: LessonErrorSchema}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 11) else 1, "" if sys.version_info >= (3, 11) else "사용 오류"),
        Case("openapi-flow-if-join-missing-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(if_join_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-flow-if-join-correct-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(if_join_body, "{200: dict, 404: LessonErrorSchema}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-flow-with-join-missing-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(with_join_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-flow-with-join-correct-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(with_join_body, "{200: dict, 404: LessonErrorSchema}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-flow-try-join-missing-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(try_join_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-flow-try-join-correct-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(try_join_body, "{200: dict, 404: LessonErrorSchema}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-flow-error-instance-alias-missing-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(alias_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-flow-error-instance-alias-correct-response", with_files(("application/lesson/driving_layer/controller.py", flow_controller(alias_body, "{200: dict, 404: LessonErrorSchema}")), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-analysis-error-instance-ambiguous-join", with_files(("application/lesson/driving_layer/controller.py", flow_controller(ambiguous_join_body)), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-framework-common-error-advertised", with_files(("application/lesson/driving_layer/controller.py", no_direct_common), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-common-error-advertised-empty-error-bc", with_files(("application/lesson/driving_layer/controller.py", no_direct_common), ("application/lesson/driving_layer/api/bc_error_schema.py", "<REMOVE>"), base=OPENAPI_FILES), "check-openapi-error-declaration.py", empty_error_bc_args, 2, "BLOCKER"),
        Case("openapi-framework-bc-base-error-advertised", with_files(("application/lesson/driving_layer/controller.py", no_direct_base), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-framework-concrete-error-advertised", with_files(("application/lesson/driving_layer/controller.py", no_direct_concrete), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-clean-framework-dict-error-status", with_files(("application/lesson/driving_layer/controller.py", no_direct_dict), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-framework-owned-error-schema", with_files(("application/lesson/driving_layer/controller.py", no_direct_framework_schema), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-code-selected-bound-method-call", with_files(("config/api.py", selected_method_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-selected-literal-setattr", with_files(("config/api.py", selected_setattr), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-code-selected-controller-import-call", with_files(("application/lesson/driving_layer/controller.py", selected_controller_call), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-clean-arbitrary-schema-receiver", with_files(("config/api.py", arbitrary_receiver), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-arbitrary-schema-setattr", with_files(("config/api.py", arbitrary_setattr), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-arbitrary-schema-class", with_files(("config/api.py", arbitrary_class), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-clean-arbitrary-controller-receiver", with_files(("application/lesson/driving_layer/controller.py", arbitrary_controller_call), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-analysis-conditionally-rebound-selected-receiver", with_files(("config/api.py", ambiguous_selected_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 1, "사용 오류"),
        Case("openapi-clean-match-rebound-selected-receiver", with_files(("config/api.py", match_rebound_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-clean-trystar-rebound-selected-receiver", with_files(("config/api.py", trystar_rebound_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 11) else 1, "" if sys.version_info >= (3, 11) else "사용 오류"),
        Case("openapi-extra-ninja-status-constant", with_files(("application/lesson/driving_layer/controller.py", ninja_status_extra), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-extra-httpstatus-constant", with_files(("application/lesson/driving_layer/controller.py", http_status_extra), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-extra-success-status-blocked", with_files(("application/lesson/driving_layer/controller.py", success_status_extra), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "#63"),
        Case("openapi-round3-clean-early-return-error-instance", with_files(("application/lesson/driving_layer/controller.py", early_return_instance), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-round3-selected-api-after-early-return", with_files(("config/api.py", early_return_selected_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-round3-clean-unreachable-match-error-return", with_files(("application/lesson/driving_layer/controller.py", unreachable_match_error), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-round3-clean-unreachable-match-selected-api", with_files(("config/api.py", unreachable_match_selected_api), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("openapi-round3-clean-shadowed-setattr", with_files(("config/api.py", shadowed_setattr), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-round3-clean-two-step-error-instance-alias", with_files(("application/lesson/driving_layer/controller.py", two_step_instance_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-round3-one-step-standard-status-alias", with_files(("application/lesson/driving_layer/controller.py", one_step_standard_status_alias), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
        Case("openapi-round3-clean-unselected-controller-api-call", with_files(("application/catalog/driving_layer/controller.py", unselected_controller_call), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 0, ""),
        Case("openapi-round4-mandatory-finally-error-return", with_files(("application/lesson/driving_layer/controller.py", mandatory_finally_error), base=OPENAPI_FILES), "check-openapi-error-declaration.py", openapi_args(), 2, "BLOCKER"),
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
        "application/lesson/driving_layer/schema.py": SUCCESS_SCHEMA,
        "application/lesson/driving_layer/controller.py": controller,
    }


def success_args(*extra: str) -> tuple[str, ...]:
    return (
        TARGET_DIR,
        "--controller-module",
        "application/lesson/driving_layer/controller.py",
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
        "from application.lesson.driving_layer.api import LessonOut",
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
    conditional_response_status_500 = conditional_response_rebind.replace(
        'return JsonResponse({"id": 1})',
        'return JsonResponse({"id": 1}, status=500)',
    )
    conditional_response_dynamic_kwargs = conditional_response_rebind.replace(
        "def endpoint(request):\n    return JsonResponse({\"id\": 1})",
        "def endpoint(request, options):\n    return JsonResponse({\"id\": 1}, **options)",
    )
    conditional_response_status_200 = conditional_response_rebind.replace(
        'return JsonResponse({"id": 1})',
        'return JsonResponse({"id": 1}, status=200)',
    )
    conditional_http_response_default_200 = conditional_response_rebind.replace(
        "from django.http import JsonResponse",
        "from django.http import HttpResponse",
    ).replace(
        "JsonResponse",
        "HttpResponse",
    ).replace(
        'return HttpResponse({"id": 1})',
        "return HttpResponse('{\"id\": 1}', content_type=\"application/json\")",
    )
    conditional_router_no_content = """import os
from ninja import Router
from django.http import HttpResponse
router = Router()
if os.getenv("CUSTOM_ROUTER"):
    router = object()
@router.delete("/", response={204: None})
def endpoint(request):
    return HttpResponse(status=204)
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
        Case("success-analysis-selected-read", success_files(schema_object), "check-response-schema-bypass.py", success_args("--controller-module", "application/lesson/driving_layer/missing.py"), 1, "사용 오류"),
        Case("success-fresh-analysis-selected-compile-invalid", success_files(compile_invalid), "check-response-schema-bypass.py", success_args(), 1, "사용 오류"),
        Case("success-fresh-analysis-compile-invalid-precedes-blocker", {**success_files(compile_invalid), "application/catalog/driving_layer/controller.py": raw_200_decoy}, "check-response-schema-bypass.py", success_args("--controller-module", "application/catalog/driving_layer/controller.py"), 1, "사용 오류"),
        Case("success-fresh-clean-unselected-compile-invalid", {**success_files(schema_object), "application/catalog/driving_layer/controller.py": compile_invalid}, "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-fresh-analysis-conditional-response-rebind", success_files(conditional_response_rebind), "check-response-schema-bypass.py", success_args(), 1, "사용 오류"),
        Case("success-fresh-analysis-conditional-router-rebind", success_files(conditional_router_rebind), "check-response-schema-bypass.py", success_args(), 1, "사용 오류"),
        Case("success-fresh-clean-deterministic-rebind-away", {**success_files(deterministic_response_rebind), "application/catalog/driving_layer/controller.py": deterministic_router_rebind}, "check-response-schema-bypass.py", success_args("--controller-module", "application/catalog/driving_layer/controller.py"), 0, ""),
        Case("success-fresh-clean-match-capture-shadows", success_files(match_capture_shadows), "check-response-schema-bypass.py", success_args(), 0 if sys.version_info >= (3, 10) else 1, "" if sys.version_info >= (3, 10) else "사용 오류"),
        Case("success-fresh-clean-lexical-shadow-controls", success_files(lexical_shadow_controls), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-scope-clean-ambiguous-response-literal-500", success_files(conditional_response_status_500), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-scope-clean-ambiguous-response-dynamic-kwargs", success_files(conditional_response_dynamic_kwargs), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-scope-clean-ambiguous-router-schema-less-204", success_files(conditional_router_no_content), "check-response-schema-bypass.py", success_args(), 0, ""),
        Case("success-scope-analysis-selected-ambiguous-response-literal-200", success_files(conditional_response_status_200), "check-response-schema-bypass.py", success_args(), 1, "사용 오류"),
        Case("success-scope-analysis-selected-ambiguous-response-default-200", success_files(conditional_http_response_default_200), "check-response-schema-bypass.py", success_args(), 1, "사용 오류"),
        Case("success-scope-clean-positional-ambiguous-response-default-200", success_files(conditional_http_response_default_200), "check-response-schema-bypass.py", (TARGET_DIR,), 0, ""),
        Case("success-scope-clean-positional-ambiguous-router-declared-200", success_files(conditional_router_rebind), "check-response-schema-bypass.py", (TARGET_DIR,), 0, ""),
        Case("success-fp-tests-migrations-cache-venv", {**success_files(schema_object), "application/lesson/driving_layer/tests/test_bypass.py": raw_200_decoy, "application/lesson/driving_layer/migrations/0001_bypass.py": raw_200_decoy, "application/lesson/driving_layer/.cache/bypass.py": raw_200_decoy, "application/lesson/driving_layer/.venv/bypass.py": raw_200_decoy}, "check-response-schema-bypass.py", (TARGET_DIR,), 0, ""),
        Case("success-fp-unignored-generated-path", {**success_files(schema_object), ".gitignore": "application/lesson/driving_layer/ignored_bypass.py\n", "application/lesson/driving_layer/generated/bypass.py": raw_200_decoy}, "check-response-schema-bypass.py", (TARGET_DIR,), 0, "", baseline_files={**success_files(schema_object), ".gitignore": "application/lesson/driving_layer/ignored_bypass.py\n"}),
        Case("success-fp-git-ignored-selected-path", {**success_files(schema_object), ".gitignore": "application/lesson/driving_layer/ignored_bypass.py\n", "application/lesson/driving_layer/ignored_bypass.py": raw_200_decoy}, "check-response-schema-bypass.py", (TARGET_DIR,), 0, "", baseline_files={**success_files(schema_object), ".gitignore": "application/lesson/driving_layer/ignored_bypass.py\n"}),
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
        # 사용자 환경의 DJR_FINDINGS_JSON 을 상속하면 이 하네스가 사용자의 실제 레코드
        # 파일에 테스트 레코드를 append 한다(T2-1 적대 검증 레인 S 7번 —
        # checker_baseline_matrix 판형). exit·fragment 만 재는 도구이므로 sink 를 끊는다.
        env = dict(os.environ)
        env.pop("DJR_FINDINGS_JSON", None)
        completed = subprocess.run(command, capture_output=True, text=True, check=False, env=env)
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
