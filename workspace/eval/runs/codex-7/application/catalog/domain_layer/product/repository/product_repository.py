from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.catalog.domain_layer.product.product import Product


class ProductRepositoryError(Exception):
    pass


class ProductNotFound(ProductRepositoryError):
    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(f"Product {product_id} was not found.")


class ConcurrentProductUpdate(ProductRepositoryError):
    pass


@dataclass(frozen=True)
class LoadedProduct:
    product: Product
    version: int


class ProductRepository(ABC):
    @abstractmethod
    def get(self, product_id: int) -> LoadedProduct:
        raise NotImplementedError

    @abstractmethod
    def save(self, product: Product, expected_version: int) -> None:
        raise NotImplementedError
