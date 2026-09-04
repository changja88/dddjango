from enum import StrEnum

from ninja import Schema


class OrdersErrorCode(StrEnum):
    ORDER_NOT_FOUND = "order_not_found"
    PAYMENT_NOT_FOUND = "payment_not_found"


class OrdersErrorSchema(Schema):
    code: OrdersErrorCode
    message: str
