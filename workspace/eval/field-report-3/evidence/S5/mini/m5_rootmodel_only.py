from typing import Annotated
from pydantic import Field, RootModel
from common import A, B


class X(RootModel[Annotated[A | B, Field(discriminator="kind")]]):
    pass


def make() -> X:
    return X(root=A(kind="a", x=1))
