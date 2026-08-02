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

BASE_FILES: Final = {
    "common/ninja/response/__init__.py": "",
    "common/ninja/response/error_out.py": COMMON_ERROR_OUT,
    "application/lesson/presentation_layer/schema/error_out.py": LESSON_ERROR_OUT,
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


def schema_args(*extra: str) -> tuple[str, ...]:
    return (
        TARGET_DIR,
        "--error-profile",
        "dddjango-code-json",
        "--scope",
        "public-v1",
        "--scope-bc",
        "lesson",
        "--error-bc",
        "lesson",
        "--project-code-error-module",
        "application.lesson.presentation_layer.schema.error_out",
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
        "config.api",
        "--controller-module",
        "application.lesson.presentation_layer.controller",
        "--scope-bc",
        "lesson",
        "--error-bc",
        "lesson",
        "--project-code-error-module",
        "application.lesson.presentation_layer.schema.error_out",
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
    }
    no_error_bc = dict(common_only)
    no_error_bc["application/catalog/presentation_layer/controller.py"] = "pass\n"
    preserve = {
        "legacy/errors.py": "class ErrorOut: pass\n",
        "common/ninja/response/__init__.py": "",
        "common/ninja/response/error_out.py": COMMON_ERROR_OUT,
    }
    duplicate_enum = LESSON_ERROR_OUT.replace("lesson_conflict", "lesson_not_found")
    return [
        Case("schema-clean-common-base-and-two-concrete", BASE_FILES, "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-clean-empty-error-bc", common_only, "check-error-centralization.py", schema_args("--error-bc", ""), 0, ""),
        Case("schema-clean-no-error-bc-in-scope", no_error_bc, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--scope-bc", "catalog", "--project-code-error-module", "common.ninja.response.error_out"), 0, ""),
        Case("schema-clean-same-profile-common-enum-reuse", BASE_FILES, "check-error-centralization.py", schema_args("--controller-module", "application.lesson.presentation_layer.other_controller", "--project-code-error-module", "application.lesson.presentation_layer.schema.error_out"), 0, ""),
        Case("schema-clean-canonical-looking-preserve-excluded", preserve, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "preserve-established", "--scope", "legacy", "--project-preserve-error-module", "legacy.errors"), 0, ""),
        Case("schema-missing-designated-error-bc-artifact", with_files(("application/lesson/presentation_layer/schema/error_out.py", "<REMOVE>")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-init-missing", with_files(("common/ninja/response/__init__.py", "<REMOVE>")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-error-out-missing", with_files(("common/ninja/response/error_out.py", "<REMOVE>")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-extra-common-response-file", with_files(("common/ninja/response/helper.py", "def make_error(): pass\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-common-concrete-error", with_files(("common/ninja/response/error_out.py", COMMON_ERROR_OUT + "\nclass GlobalNotFound(ErrorOut):\n    pass\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-outside-canonical-module", with_files(("application/lesson/presentation_layer/schema/not_found.py", "from .error_out import LessonErrorOut\nclass Other(LessonErrorOut): pass\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-missing-enum", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("class LessonErrorCode(StrEnum):\n    NOT_FOUND = \"lesson_not_found\"\n    CONFLICT = \"lesson_conflict\"\n\n\n", ""))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-duplicate-enum", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT + "\nclass OtherErrorCode(StrEnum):\n    BAD = 'bad'\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-missing-base", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("class LessonErrorOut(ErrorOut):\n    code: LessonErrorCode\n\n\n", ""))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-duplicate-base", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT + "\nclass AnotherErrorOut(ErrorOut):\n    code: LessonErrorCode\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-extra-defaulted-field", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("    code: LessonErrorCode\n", "    code: LessonErrorCode\n    retryable: bool = False\n", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-base-wrong-inheritance", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("class LessonErrorOut(ErrorOut):", "class LessonErrorOut:"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-extra-field", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("    detail: str = \"The lesson does not exist.\"", "    detail: str = \"The lesson does not exist.\"\n    retry_after: int = 1"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-validator", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT + "\nLessonNotFoundError.validate_status = lambda value: value\n")), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-field-alias", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("title: str = \"Lesson not found\"", "title: str = Field(alias='message', default='Lesson not found')"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-concrete-missing-default", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("    detail: str = \"The lesson does not exist.\"", "    detail: str"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-raw-string-code", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("code: LessonErrorCode = LessonErrorCode.NOT_FOUND", "code: str = 'lesson_not_found'"))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-project-duplicate-wire-code", with_files(("application/lesson/presentation_layer/schema/error_out.py", duplicate_enum)), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-literal-code", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("code: LessonErrorCode", "code: Literal['lesson_not_found']", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-str-code", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("code: LessonErrorCode", "code: str", 1))), "check-error-centralization.py", schema_args(), 2, "BLOCKER"),
        Case("schema-analysis-syntax", with_files(("application/lesson/presentation_layer/schema/error_out.py", "class Broken(:\n")), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-analysis-root-escape", {"../outside.py": "raise AssertionError('must not be written')\n"}, "check-error-centralization.py", schema_args(), 1, "escapes temporary root"),
        Case("schema-analysis-unresolved-base", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("from common.ninja.response.error_out import ErrorOut", "from missing import ErrorOut"))), "check-error-centralization.py", schema_args(), 1, "사용 오류"),
        Case("schema-analysis-missing-source", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--project-code-error-module", "application.lesson.presentation_layer.schema.error_out"), 1, "사용 오류"),
        Case("schema-analysis-missing-inventory", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "dddjango-code-json", "--scope", "public-v1", "--scope-bc", "lesson", "--error-bc", "lesson"), 1, "사용 오류"),
        Case("schema-analysis-error-bc-not-subset", BASE_FILES, "check-error-centralization.py", schema_args("--scope-bc", "catalog", "--error-bc", "lesson"), 1, "사용 오류"),
        Case("schema-analysis-candidate-absent-from-inventory", BASE_FILES, "check-error-centralization.py", schema_args("--project-code-error-module", "application.lesson.presentation_layer.schema.unknown"), 1, "사용 오류"),
        Case("schema-analysis-module-in-both-inventories", BASE_FILES, "check-error-centralization.py", schema_args("--project-preserve-error-module", "application.lesson.presentation_layer.schema.error_out"), 1, "사용 오류"),
        Case("schema-analysis-auto-profile", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--error-profile", "auto", "--scope", "public-v1"), 1, "사용 오류"),
        Case("schema-analysis-missing-profile-args", BASE_FILES, "check-error-centralization.py", (TARGET_DIR, "--scope", "public-v1"), 1, "사용 오류"),
        Case("schema-fp-tests-migrations-docstrings-logs", with_files(("application/lesson/tests/test_codes.py", "code = 'lesson_not_found'\n"), ("application/lesson/migrations/0001_initial.py", "code = 'lesson_not_found'\n"), ("application/lesson/presentation_layer/log.py", "'''code = lesson_not_found'''\nlogger.info('code=%s', 'lesson_not_found')\n")), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-fp-classvar-private-benign-config-import-alias", with_files(("application/lesson/presentation_layer/schema/error_out.py", LESSON_ERROR_OUT.replace("class LessonErrorOut(ErrorOut):\n    code: LessonErrorCode", "class LessonErrorOut(ErrorOut):\n    model_config = {'populate_by_name': True}\n    _cache: ClassVar[dict] = {}\n    code: LessonErrorCode"))), "check-error-centralization.py", schema_args(), 0, ""),
        Case("schema-fp-relative-import-local-assignment-ignored-cache", with_files(("application/lesson/presentation_layer/schema/alias.py", "from .error_out import LessonErrorOut as Error\nvalue = Error\n"), (".cache/generated.py", "code = 'ignored'\n"), ("__pycache__/bad.py", "code = 'ignored'\n")), "check-error-centralization.py", schema_args(), 0, ""),
        # Reviewer gap: whether the inventory is semantically complete and whether a
        # public code should exist cannot be inferred from source shape alone.
    ]


def controller_cases() -> list[Case]:
    """Controller shape cases; the checker is intentionally absent at this RED stage."""
    clean_async = CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("def get_lesson_controller", "async def get_lesson_controller").replace("lesson = get_lesson(lesson_id)", "lesson = await get_lesson(lesson_id)")
    clean_tuple = CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("except LessonMissing:", "except (LessonMissing, LookupError):")
    direct_base = CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("LessonNotFoundError()", "LessonErrorOut(code=LessonErrorCode.NOT_FOUND, title='missing', status=404, detail='missing')").replace("from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError", "from application.lesson.presentation_layer.schema.error_out import LessonErrorCode, LessonErrorOut")
    return [
        Case("controller-clean-sync-narrow-try", CONTROLLER_FILES, "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-async-narrow-try", with_files(("application/lesson/presentation_layer/controller.py", clean_async), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-tuple-catch-prepared-concrete", with_files(("application/lesson/presentation_layer/controller.py", clean_tuple), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-event-specific-base", with_files(("application/lesson/presentation_layer/controller.py", direct_base), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-result-none-direct-return", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return lesson", "result = lesson\n    if result is None:\n        return None\n    return result")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-approved-retry-after", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return Status(error.status, error)", "return Status(error.status, error, headers={'Retry-After': '1'})")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-clean-unselected-preserve-handler", with_files(("legacy/handler.py", "def handler(request, exc): return {'legacy': True}\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 0, ""),
        Case("controller-direct-presentation-helper", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .factory import make_error").replace("error = LessonNotFoundError()", "error = make_error()")), ("application/lesson/presentation_layer/factory.py", "from .schema.error_out import LessonNotFoundError\ndef make_error(): return LessonNotFoundError()\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-direct-serializer-mapping-helper", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from ninja import Router, Status\nfrom .mapping import serialize_error").replace("error = LessonNotFoundError()", "error = serialize_error()")), ("application/lesson/presentation_layer/mapping.py", "from .schema.error_out import LessonNotFoundError\ndef serialize_error(): return LessonNotFoundError()\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-registered-handler", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"] + "\n@router.exception_handler(LessonMissing)\ndef handler(request, exc): pass\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-wide-try", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("try:\n        lesson =", "try:\n        prepared = lesson_id\n        lesson =")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-success-transform-inside-try", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("lesson = get_lesson(lesson_id)", "lesson = get_lesson(lesson_id)\n        return {'lesson': lesson}")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-broad-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("except LessonMissing:", "except Exception:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-framework-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("except LessonMissing:", "except HttpError:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-raw-infra-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("except LessonMissing:", "except OSError:")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-immediate-raise-catch", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("lesson = get_lesson(lesson_id)", "raise LessonMissing()")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-reraises", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("error = LessonNotFoundError()\n        return Status(error.status, error)", "raise")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-raises-http-error", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("error = LessonNotFoundError()\n        return Status(error.status, error)", "raise HttpError(404, 'missing')")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-known-forwards-exception", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("error = LessonNotFoundError()\n        return Status(error.status, error)", "return forward_error(error)")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-no-direct-status", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return Status(error.status, error)", "return error")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-concrete-called-with-args", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("LessonNotFoundError()", "LessonNotFoundError(detail='missing')")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-error-tuple-raw-response-dict", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return Status(error.status, error)", "return 404, {'code': 'lesson_not_found'}")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-error-raw-response", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("return Status(error.status, error)", "return Response({'code': 'lesson_not_found'}, status=404)")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 2, "BLOCKER"),
        Case("controller-analysis-unresolved-status-reexport", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from ninja import Router, Status", "from .exports import Status\nfrom ninja import Router")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-unresolved-error-out-reexport", with_files(("application/lesson/presentation_layer/controller.py", CONTROLLER_FILES["application/lesson/presentation_layer/controller.py"].replace("from application.lesson.presentation_layer.schema.error_out import LessonNotFoundError", "from .exports import LessonNotFoundError")), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-selected-syntax", with_files(("application/lesson/presentation_layer/controller.py", "def broken(:\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-one-hop-syntax", with_files(("application/lesson/presentation_layer/factory.py", "def broken(:\n"), base=CONTROLLER_FILES), "check-api-error-controller-contract.py", controller_args(), 1, "사용 오류"),
        Case("controller-analysis-auto-profile", CONTROLLER_FILES, "check-api-error-controller-contract.py", (TARGET_DIR, "--error-profile", "auto", "--scope", "public-v1"), 1, "사용 오류"),
        Case("controller-analysis-missing-args", CONTROLLER_FILES, "check-api-error-controller-contract.py", (TARGET_DIR, "--scope", "public-v1"), 1, "사용 오류"),
        # Reviewer gaps deliberately remain outside the deterministic oracle:
        # application collaborator identity, broad exception hidden by re-export,
        # and two-hop/off-selection helpers.
    ]


def validate_checker_args(args: tuple[str, ...]) -> None:
    """Reject malformed matrix data before a subprocess hides the authoring error."""
    if args.count(TARGET_DIR) != 1:
        raise ValueError("checker_args must contain TARGET_DIR exactly once")
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
        index += arity + 1


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


def run_case(case: Case) -> tuple[bool, str]:
    validate_checker_args(case.checker_args)
    checker = CHECKER_DIR / case.checker
    with tempfile.TemporaryDirectory(prefix="dddjango-api-error-") as directory:
        fixture_root = Path(directory)
        try:
            write_fixture(fixture_root, case.files)
        except ValueError as exc:
            actual_exit = 1
            stdout = ""
            stderr = str(exc)
            output = f"{stdout}\n{stderr}"
            passed = actual_exit == case.expected_exit and case.expected_fragment in output
            if passed:
                return True, ""
            return False, (
                f"[{case.name}] expected exit={case.expected_exit}, fragment={case.expected_fragment!r}; "
                f"actual exit={actual_exit}\nstdout:\n{stdout or '<empty>'}\n"
                f"stderr:\n{stderr or '<empty>'}"
            )
        command = [sys.executable, str(checker)]
        command.extend(str(fixture_root) if arg == TARGET_DIR else arg for arg in case.checker_args)
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    output = f"{completed.stdout}\n{completed.stderr}"
    fragment_matches = not case.expected_fragment or case.expected_fragment in output
    passed = completed.returncode == case.expected_exit and fragment_matches
    if passed:
        return True, ""
    return False, (
        f"[{case.name}] expected exit={case.expected_exit}, fragment={case.expected_fragment!r}; "
        f"actual exit={completed.returncode}\nstdout:\n{completed.stdout or '<empty>'}\n"
        f"stderr:\n{completed.stderr or '<empty>'}"
    )


def main() -> int:
    cases = [*schema_cases(), *controller_cases()]
    passed = 0
    failed = 0
    for case in cases:
        try:
            ok, detail = run_case(case)
        except (OSError, ValueError) as exc:
            ok, detail = False, f"[{case.name}] runner failure: {exc}"
        if ok:
            passed += 1
        else:
            failed += 1
            print(detail)
    print(f"api-error backstop matrix: passed={passed} failed={failed} total={len(cases)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
