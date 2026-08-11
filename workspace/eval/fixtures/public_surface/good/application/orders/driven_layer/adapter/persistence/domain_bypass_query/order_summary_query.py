from dataclasses import dataclass


@dataclass(frozen=True)
class OrderSummaryOut:
    order_id: str
    total: int


class DjangoOrderSummaryQuery:
    def fetch(self, order_id: str) -> OrderSummaryOut:
        return OrderSummaryOut(order_id=order_id, total=0)
