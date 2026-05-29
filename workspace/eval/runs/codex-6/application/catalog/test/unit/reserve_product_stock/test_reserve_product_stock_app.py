from unittest import TestCase
from typing import Optional

from application.catalog.application_layer.reserve_product_stock.command.reserve_product_stock_app import (
    ProductNotFound,
    ReserveProductStockApp,
    StockReservationConflict,
)
from application.catalog.application_layer.reserve_product_stock.dto.reserve_product_stock_command import (
    ReserveProductStockCommand,
)
from application.catalog.domain_layer.product.exception import InsufficientStock
from application.catalog.domain_layer.product.product import Product
from application.catalog.domain_layer.product.repository.product_repository import (
    ProductRepository,
)


class FakeProductRepository(ProductRepository):
    def __init__(
        self,
        products: list[Product],
        save_results: Optional[list[bool]] = None,
    ) -> None:
        self._products = products
        self._save_results = save_results or [True]
        self.saved_products: list[Product] = []

    def get(self, product_id: int) -> Optional[Product]:
        if not self._products:
            return None
        product = self._products.pop(0)
        return Product(id=product.id, stock=product.stock, version=product.version)

    def save(self, product: Product) -> bool:
        self.saved_products.append(product)
        if not self._save_results:
            return True
        return self._save_results.pop(0)


class ReserveProductStockAppTests(TestCase):
    def test_reserve_returns_updated_stock_after_successful_save(self) -> None:
        repository = FakeProductRepository([Product(id=1, stock=10, version=0)])
        app = ReserveProductStockApp(repository=repository)

        result = app.reserve(ReserveProductStockCommand(product_id=1, quantity=3))

        self.assertEqual(result.product_id, 1)
        self.assertEqual(result.stock, 7)
        self.assertEqual(repository.saved_products[0].stock, 7)

    def test_reserve_reloads_and_retries_after_cas_miss(self) -> None:
        repository = FakeProductRepository(
            [
                Product(id=1, stock=10, version=0),
                Product(id=1, stock=8, version=1),
            ],
            save_results=[False, True],
        )
        app = ReserveProductStockApp(repository=repository)

        result = app.reserve(ReserveProductStockCommand(product_id=1, quantity=3))

        self.assertEqual(result.stock, 5)
        self.assertEqual([product.stock for product in repository.saved_products], [7, 5])

    def test_reserve_raises_product_not_found_when_repository_has_no_product(self) -> None:
        app = ReserveProductStockApp(repository=FakeProductRepository([]))

        with self.assertRaises(ProductNotFound):
            app.reserve(ReserveProductStockCommand(product_id=999, quantity=1))

    def test_reserve_raises_insufficient_stock_without_saving(self) -> None:
        repository = FakeProductRepository([Product(id=1, stock=2, version=0)])
        app = ReserveProductStockApp(repository=repository)

        with self.assertRaises(InsufficientStock):
            app.reserve(ReserveProductStockCommand(product_id=1, quantity=3))

        self.assertEqual(repository.saved_products, [])

    def test_reserve_raises_conflict_after_retry_budget_is_exhausted(self) -> None:
        repository = FakeProductRepository(
            [
                Product(id=1, stock=10, version=0),
                Product(id=1, stock=9, version=1),
            ],
            save_results=[False, False],
        )
        app = ReserveProductStockApp(repository=repository, max_attempts=2)

        with self.assertRaises(StockReservationConflict):
            app.reserve(ReserveProductStockCommand(product_id=1, quantity=1))
