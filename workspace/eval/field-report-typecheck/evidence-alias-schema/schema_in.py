from ninja import Schema as _Schema
from pydantic import BaseModel as _BaseModel, ConfigDict


class ListFortuneTypesIn(_Schema):
    model_config = ConfigDict(extra="forbid")
    query: str


class RelationRow(_BaseModel):
    model_config = ConfigDict(frozen=True)
    fortune_id: str
