from typing import Annotated, Literal

from ninja import Schema
from pydantic import Field, RootModel


class CardPaymentOut(Schema):
    kind: Literal["card"]
    payment_id: str
    last4: str


class PointPaymentOut(Schema):
    kind: Literal["point"]
    payment_id: str
    points: int


class PaymentOut(RootModel[Annotated[CardPaymentOut | PointPaymentOut, Field(discriminator="kind")]]):
    """성공 union 응답 — 이름 붙은 RootModel 하나(ninja Schema 병행 상속 금지 · #649 · ninja §3.1)."""
