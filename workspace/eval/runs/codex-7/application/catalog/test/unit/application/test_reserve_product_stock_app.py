from typing import Optional

from django.db import OperationalError
from django.test import SimpleTestCase

from application.catalog.application_layer.reserve_stock.command.reserve_product_stock_app import (
    ConcurrentProductUpdate,
    ProductNotFound,
    ReserveProductStockApp,
    StockReservationConflict,
)
from application.catalog.application_layer.reserve_stock.dto.reserve_product_stock_command import (
    ReserveProductStockCommand,
)
from application.catalog.domain_layer.product.exception import InsufficientStock
from application.catalog.domain_layer.product.product import Product
from application.catalog.domain_layer.product.repository.product_repository import (
    LoadedProduct,
    ProductRepository,
)


class FakeProductRepository(ProductRepository):
    def __init__(
        self,
        product: Optional[Product],
        save_failures: int = 0,
        lock_failures: int = 0,
    ) -> None:
        self.product = product
        self.version = 0
        self.save_failures = save_failures
        self.lock_failures = lock_failures
        self.load_count = 0

    def get(self, product_id: int) -> LoadedProduct:
        self.load_count += 1
        if self.product is None:
            raise ProductNotFound(product_id)
        return LoadedProduct(
            product=Product(
                id=self.product.id,
                name=self.product.name,
                price=self.product.price,
                stock=self.product.stock,
            ),
            version=self.version,
        )

    def save(self, product: Product, expected_version: int) -> None:
        if self.save_failures:
            self.save_failures -= 1
            raise ConcurrentProductUpdate()
        if self.lock_failures:
            self.lock_failures -= 1
            raise OperationalError("database table is locked: catalog_product")
        self.product = product
        self.version = expected_version + 1


class ReserveProductStockAppTests(SimpleTestCase):
    def test_reserve_product_stock_decrements_stock(self):
        repository = FakeProductRepository(
            Product(id=1, name="Widget", price=1000, stock=10)
        )
        app = ReserveProductStockApp(repository)

        result = app.reserve(ReserveProductStockCommand(product_id=1, quantity=3))

        self.assertEqual(result.product_id, 1)
        self.assertEqual(result.stock, 7)
        self.assertEqual(repository.product.stock, 7)

    def test_insufficient_stock_is_raised_by_domain_decision(self):
        repository = FakeProductRepository(
            Product(id=1, name="Widget", price=1000, stock=2)
        )
        app = ReserveProductStockApp(repository)

        with self.assertRaises(InsufficientStock):
            app.reserve(ReserveProductStockCommand(product_id=1, quantity=3))

        self.assertEqual(repository.product.stock, 2)

    def test_retries_after_concurrent_update(self):
        repository = FakeProductRepository(
            Product(id=1, name="Widget", price=1000, stock=10),
            save_failures=1,
        )
        app = ReserveProductStockApp(repository, max_attempts=2)

        result = app.reserve(ReserveProductStockCommand(product_id=1, quantity=3))

        self.assertEqual(result.stock, 7)
        self.assertEqual(repository.load_count, 2)

    def test_retries_after_sqlite_table_lock(self):
        repository = FakeProductRepository(
            Product(id=1, name="Widget", price=1000, stock=10),
            lock_failures=1,
        )
        app = ReserveProductStockApp(repository, max_attempts=2)

        result = app.reserve(ReserveProductStockCommand(product_id=1, quantity=3))

        self.assertEqual(result.stock, 7)
        self.assertEqual(repository.load_count, 2)

    def test_raises_conflict_after_retry_budget_is_exhausted(self):
        repository = FakeProductRepository(
            Product(id=1, name="Widget", price=1000, stock=10),
            save_failures=2,
        )
        app = ReserveProductStockApp(repository, max_attempts=2)

        with self.assertRaises(StockReservationConflict):
            app.reserve(ReserveProductStockCommand(product_id=1, quantity=3))
