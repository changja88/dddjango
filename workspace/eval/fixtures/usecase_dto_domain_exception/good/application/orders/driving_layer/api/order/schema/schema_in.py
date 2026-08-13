from ninja import Schema
from pydantic import Field


class PlaceOrderIn(Schema):
    quantity: int = Field(gt=0)
