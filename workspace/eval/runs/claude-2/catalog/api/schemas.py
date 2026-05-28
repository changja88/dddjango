"""Ninja Schema — request/response 분리, problem+json(error_out) (설계 명세 section 2.4, 2.6)."""

from __future__ import annotations

from ninja import Schema
from pydantic import Field


class CreateOrderIn(Schema):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)


class CreateOrderOut(Schema):
    order_id: int
    product_id: int
    quantity: int
    status: str
    remaining_stock: int


class ProblemDetail(Schema):
    """RFC 9457 problem+json 응답 스키마(공통 필드)."""

    type: str
    title: str
    status: int
    detail: str
    instance: str
