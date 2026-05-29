from contextlib import nullcontext
from unittest.mock import patch

from django.db import OperationalError
from django.test import SimpleTestCase

from application.orders.domain_layer.order.port.product_inventory_port import (
    InventoryConflict,
)
from application.orders.infra_layer.service.transaction_runner import (
    DjangoTransactionRunner,
)


class FakeConnection:
    def __init__(self, *, vendor: str) -> None:
        self.vendor = vendor


class DjangoTransactionRunnerTests(SimpleTestCase):
    def test_translates_sqlite_lock_operational_error_to_inventory_conflict(
        self,
    ) -> None:
        runner = DjangoTransactionRunner()

        with (
            patch(
                "application.orders.infra_layer.service.transaction_runner.connection",
                FakeConnection(vendor="sqlite"),
            ),
            patch(
                "application.orders.infra_layer.service.transaction_runner.transaction.atomic",
                return_value=nullcontext(),
            ),
            self.assertRaises(InventoryConflict),
        ):
            runner.run(lambda: self._raise_operational_error("database is locked"))

    def test_leaves_unexpected_operational_error_untranslated(self) -> None:
        runner = DjangoTransactionRunner()

        with (
            patch(
                "application.orders.infra_layer.service.transaction_runner.connection",
                FakeConnection(vendor="sqlite"),
            ),
            patch(
                "application.orders.infra_layer.service.transaction_runner.transaction.atomic",
                return_value=nullcontext(),
            ),
            self.assertRaisesMessage(OperationalError, "no such table: catalog_product"),
        ):
            runner.run(
                lambda: self._raise_operational_error("no such table: catalog_product")
            )

    def test_leaves_non_sqlite_operational_error_untranslated(self) -> None:
        runner = DjangoTransactionRunner()

        with (
            patch(
                "application.orders.infra_layer.service.transaction_runner.connection",
                FakeConnection(vendor="postgresql"),
            ),
            patch(
                "application.orders.infra_layer.service.transaction_runner.transaction.atomic",
                return_value=nullcontext(),
            ),
            self.assertRaisesMessage(OperationalError, "database is locked"),
        ):
            runner.run(lambda: self._raise_operational_error("database is locked"))

    def _raise_operational_error(self, message: str) -> None:
        raise OperationalError(message)
