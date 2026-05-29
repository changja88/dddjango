from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.orders.domain_layer.order.value_object.quantity import Quantity


@dataclass(frozen=True)
class ProductInventorySnapshot:
    product_id: int
    available_stock: int
    version: int


class ProductInventoryError(Exception):
    pass


class ProductNotFound(ProductInventoryError):
    pass


class InventoryConflict(ProductInventoryError):
    pass


class ProductInventoryPort(ABC):
    @abstractmethod
    def load_snapshot(self, product_id: int) -> ProductInventorySnapshot:
        raise NotImplementedError

    @abstractmethod
    def decrement_stock(
        self,
        snapshot: ProductInventorySnapshot,
        quantity: Quantity,
    ) -> None:
        raise NotImplementedError
