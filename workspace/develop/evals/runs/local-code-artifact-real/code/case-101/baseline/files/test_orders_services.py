from decimal import Decimal

from orders.services import create_order_summary


def test_create_order_summary_returns_total_and_line_count():
    lines = [
        {"quantity": 2, "unit_price": Decimal("3.50")},
        {"quantity": 1, "unit_price": Decimal("4.00")},
    ]

    summary = create_order_summary(lines)

    assert summary == {
        "total": Decimal("11.00"),
        "line_count": 2,
    }
