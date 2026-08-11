from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderQuery:
    order_id: str
