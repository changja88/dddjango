from typing import List, Optional

from ninja import Schema


class FieldErrorOut(Schema):
    field: str
    message: str
    code: str


class ProblemDetailsOut(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: Optional[List[FieldErrorOut]] = None
    product_id: Optional[int] = None
    requested_quantity: Optional[int] = None
    available_stock: Optional[int] = None
    retryable: Optional[bool] = None

