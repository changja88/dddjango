from typing import Annotated
from ninja import Schema
from pydantic import Field, RootModel
from common import A, B


class X(Schema, RootModel[Annotated[A | B, Field(discriminator="kind")]]):
    pass


def make() -> X:
    return X(root=A(kind="a", x=1))
