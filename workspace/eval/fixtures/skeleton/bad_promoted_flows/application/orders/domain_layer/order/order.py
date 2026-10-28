from dataclasses import dataclass

from application.orders.domain_layer.order.value_object.payment_route import PaymentRoute


@dataclass
class Order:
    order_id: int
    paid: bool = False
    stock_held: bool = False

    def payment_route(self, requested: str) -> PaymentRoute:
        return PaymentRoute(requested)

    def hold_stock(self) -> bool:
        self.stock_held = True
        return True

    def pay(self, amount: int) -> bool:
        self.paid = amount > 0
        return self.paid
