import time
from dataclasses import dataclass

from django.db import OperationalError, transaction

from catalog.models import InsufficientStock, InvalidReservationQuantity
from catalog.repositories import (
    DjangoProductRepository,
    ProductNotFound,
    StockReservationConflict,
)


@dataclass(frozen=True)
class ReservationResult:
    product_id: int
    reserved_quantity: int
    remaining_stock: int


def reserve_product_stock(product_id: int, quantity: int, *, max_attempts: int = 5) -> ReservationResult:
    repository = DjangoProductRepository()

    for attempt in range(max_attempts):
        try:
            with transaction.atomic():
                product = repository.get_for_reservation(product_id)
                product.reserve(quantity)
                repository.save_reserved(product)
                return ReservationResult(
                    product_id=product.pk,
                    reserved_quantity=quantity,
                    remaining_stock=product.stock,
                )
        except StockReservationConflict:
            _pause_before_retry(attempt)
        except OperationalError as exc:
            if not _is_retryable_sqlite_lock(exc):
                raise
            _pause_before_retry(attempt)

    raise StockReservationConflict("Could not reserve stock due to concurrent updates.")


def _is_retryable_sqlite_lock(exc: OperationalError) -> bool:
    return "database is locked" in str(exc).lower()


def _pause_before_retry(attempt: int) -> None:
    time.sleep(0.01 * (attempt + 1))


__all__ = [
    "InsufficientStock",
    "InvalidReservationQuantity",
    "ProductNotFound",
    "ReservationResult",
    "StockReservationConflict",
    "reserve_product_stock",
]
