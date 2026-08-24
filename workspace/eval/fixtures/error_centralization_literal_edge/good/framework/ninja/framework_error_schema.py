from typing import Annotated

from ninja import Schema
from pydantic import Field


class FrameworkErrorSchema(Schema):
    code: str | None
    title: str
    status: int
    detail: Annotated[str, Field(min_length=1)]
