from typing import Annotated, Literal

from ninja import Schema
from pydantic import Field, RootModel


class CardPaymentOut(Schema):
    kind: Literal["card"]
    payment_id: str


class PointPaymentOut(Schema):
    kind: Literal["point"]
    payment_id: str


class PaymentOut(Schema, RootModel[Annotated[CardPaymentOut | PointPaymentOut, Field(discriminator="kind")]]):
    pass


class PaymentErrorOut(Schema):
    code: str
