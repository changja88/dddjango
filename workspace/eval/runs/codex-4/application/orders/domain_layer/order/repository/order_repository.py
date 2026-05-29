from abc import ABC, abstractmethod

from application.orders.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> Order:
        raise NotImplementedError
