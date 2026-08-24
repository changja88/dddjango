from enum import StrEnum
from typing import Annotated, Literal

from framework.ninja.framework_error_schema import FrameworkErrorSchema
from pydantic import Field


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"


class LessonErrorSchema(FrameworkErrorSchema):
    code: LessonErrorCode | None


class LessonNullableNarrowError(LessonErrorSchema):
    # 경계 red — 공통 식별자 자리가 nullable(비-bare): 병존형 우회 불가
    code: Literal[LessonErrorCode.NOT_FOUND] = LessonErrorCode.NOT_FOUND
    title: str = "Lesson not found"
    status: int = 404
    detail: Annotated[str, Field(min_length=1)] = "The lesson does not exist."


class LessonMetadataNarrowError(LessonErrorSchema):
    # 경계 red — 공통 detail 이 Annotated-metadata 보유: 병존형 우회 불가
    code: LessonErrorCode | None = LessonErrorCode.NOT_FOUND
    title: str = "Lesson not found"
    status: int = 404
    detail: Literal["The lesson does not exist."] = "The lesson does not exist."
