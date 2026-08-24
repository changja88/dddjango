from enum import StrEnum
from typing import Annotated, Literal

from framework.ninja.framework_error_schema import FrameworkErrorSchema
from pydantic import Field


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    code: LessonErrorCode | None


class LessonNullableOkError(LessonErrorSchema):
    code: LessonErrorCode | None = LessonErrorCode.NOT_FOUND
    title: str = "Lesson not found"
    status: int = 404
    detail: Annotated[str, Field(min_length=1)] = "The lesson does not exist."
