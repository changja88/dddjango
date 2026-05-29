from typing import Any, Dict

from ninja import Field, Schema


class ReserveStockIn(Schema):
    quantity: int = Field(..., ge=1)


RESERVE_STOCK_REQUEST_BODY_OPENAPI: Dict[str, Any] = {
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": ReserveStockIn.model_json_schema(),
            },
        },
    },
}
