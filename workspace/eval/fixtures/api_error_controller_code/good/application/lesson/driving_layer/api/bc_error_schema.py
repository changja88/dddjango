from enum import StrEnum
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
