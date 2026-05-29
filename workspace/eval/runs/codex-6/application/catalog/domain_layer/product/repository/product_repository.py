from abc import ABC, abstractmethod
from typing import Optional

from application.catalog.domain_layer.product.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def get(self, product_id: int) -> Optional[Product]:
        raise NotImplementedError

    @abstractmethod
    def save(self, product: Product) -> bool:
        raise NotImplementedError
