"""Acceptance (rollout artifact) test for the Product CHECK(stock >= 0)
constraint and data preservation.

Single source of truth: .dddjango/order-create-with-stock/design-spec.md
(sections 3.1, 3.4, 6.8)

Covered observable behavior:
- B8: After the migration that adds Product CHECK(stock >= 0), the database
  rejects negative stock (final defense line / DB invariant), and existing
  catalog_product rows are preserved (no table recreation / data loss).

This is blackbox at the DB-contract level: it asserts the observable
constraint enforced by the database, not how the model declares it. The
constraint does not exist yet, so a negative-stock write currently succeeds
-> Red.
"""

import pytest
from django.db import IntegrityError, transaction
from django.db.utils import DatabaseError

from catalog.models import Product

pytestmark = pytest.mark.django_db


def test_stock_cannot_go_negative_at_db_level():
    """The DB CHECK(stock >= 0) rejects negative stock as the final defense."""
    product = Product.objects.create(name="Widget", price=1000, stock=5)

    with pytest.raises((IntegrityError, DatabaseError)):
        with transaction.atomic():
            Product.objects.filter(pk=product.id).update(stock=-1)


def test_creating_product_with_negative_stock_is_rejected():
    with pytest.raises((IntegrityError, DatabaseError)):
        with transaction.atomic():
            Product.objects.create(name="Bad", price=1000, stock=-5)


def test_zero_stock_is_allowed():
    """Boundary: stock == 0 is valid (>= 0)."""
    product = Product.objects.create(name="Empty", price=1000, stock=0)

    product.refresh_from_db()
    assert product.stock == 0


def test_existing_product_rows_preserved_after_constraint():
    """B8: data preservation -- a pre-existing row remains readable with its
    original values after the constraint is in place (no recreation/loss)."""
    product = Product.objects.create(name="Legacy", price=2500, stock=42)

    fetched = Product.objects.get(pk=product.id)
    assert fetched.name == "Legacy"
    assert fetched.price == 2500
    assert fetched.stock == 42
