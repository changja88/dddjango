from typing import Annotated, Literal
from ninja import Schema
from pydantic import Field


class Resp(Schema):
    id: int


class Base(Schema):
    code: str = "base"
    message: str = "base"


class C1(Base):
    code: str = "c1"


class C2(Base):
    code: str = "c2"


class A(Schema):
    kind: Literal["a"]
    x: int


class B(Schema):
    kind: Literal["b"]
    y: str
