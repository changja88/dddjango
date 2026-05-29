from application.catalog.domain_layer.product.product import Product
from application.catalog.infra_layer.repository.product_repository import (
    ProductRepository,
)


class PlaceOrderApp:
    def __init__(self) -> None:
        self._products = ProductRepository()

    def execute(self, product_id: int, quantity: int) -> None:
        product: Product = self._products.get(product_id)
        product.deduct(quantity)
        self._products.save(product)
