from enum import StrEnum
from typing import Literal

from framework.django_ninja.error_schema import FrameworkErrorSchema


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"
    CONFLICT = "lesson_conflict"


class LessonErrorSchema(FrameworkErrorSchema):
    code: LessonErrorCode


class LessonLegacyErrorSchema(FrameworkErrorSchema):
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
    hint: str = "Retry after the current change is finished."


class LessonBareLiteralError(LessonErrorSchema):
    # R-3401 경계 red — Literal 좁힘에 default 부재(tarot형): 무인자 생성 불가
    code: Literal[LessonErrorCode.NOT_FOUND]
    title: str = "Lesson not found"
    status: int = 404
    detail: Literal["The lesson does not exist."]


class LessonMismatchedLiteralError(LessonErrorSchema):
    # R-3401 경계 red — 좁힘값 ≠ default 값(단일 출처 위반)
    code: Literal[LessonErrorCode.NOT_FOUND] = LessonErrorCode.CONFLICT
    title: str = "Lesson conflict"
    status: int = 409
    detail: Literal["The lesson does not exist."] = "wrong"
