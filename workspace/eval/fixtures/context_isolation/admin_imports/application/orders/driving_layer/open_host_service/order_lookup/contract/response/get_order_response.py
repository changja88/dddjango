from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderResponse:
    code: str
    order_id: str
