from enum import StrEnum
from typing import Literal

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


class LessonPinnedNotFoundError(LessonErrorSchema):
    # R-3401 병존형 — 단일값 Literal 좁힘 + 동일 plain `=` default (무인자 생성 유지)
    code: Literal[LessonErrorCode.NOT_FOUND] = LessonErrorCode.NOT_FOUND
    title: str = "Lesson not found"
    status: int = 404
    detail: Literal["The lesson does not exist."] = "The lesson does not exist."
