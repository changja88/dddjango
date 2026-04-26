```python
from datetime import datetime
from unittest.mock import create_autospec

import pytest

from order_service import (
    EmailService,
    Order,
    OrderRepository,
    OrderService,
    OrderStatus,
    PaymentGateway,
)


@pytest.fixture
def repo():
    return create_autospec(OrderRepository, instance=True)


@pytest.fixture
def payment():
    return create_autospec(PaymentGateway, instance=True)


@pytest.fixture
def email():
    return create_autospec(EmailService, instance=True)


@pytest.fixture
def service(repo, payment, email):
    return OrderService(repo=repo, payment=payment, email=email)


@pytest.fixture
def sample_items():
    return [
        {"name": "Widget", "price": 100.0, "quantity": 2},
        {"name": "Gadget", "price": 50.0, "quantity": 1},
    ]


@pytest.fixture
def pending_order(sample_items):
    return Order(
        id=1,
        customer_email="buyer@example.com",
        items=sample_items,
        status=OrderStatus.PENDING,
        total=250.0,
        created_at=datetime(2026, 1, 1),
    )


@pytest.fixture
def confirmed_order(sample_items):
    return Order(
        id=2,
        customer_email="buyer@example.com",
        items=sample_items,
        status=OrderStatus.CONFIRMED,
        total=250.0,
        created_at=datetime(2026, 1, 1),
    )


# ---------------------------------------------------------------------------
# create_order
# ---------------------------------------------------------------------------


class TestCreateOrder:

    def test_calculates_total_and_saves(self, service, repo, sample_items):
        """주문 생성 시 항목 가격 합계를 계산하고 저장소에 저장한다."""
        saved = Order(
            id=1,
            customer_email="buyer@example.com",
            items=sample_items,
            total=250.0,
            created_at=datetime(2026, 1, 1),
        )
        repo.save.return_value = saved

        result = service.create_order("buyer@example.com", sample_items)

        assert result.id == 1
        assert result.total == 250.0
        assert result.customer_email == "buyer@example.com"
        assert result.status == OrderStatus.PENDING

    def test_passes_correct_total_to_repo(self, service, repo, sample_items):
        """저장소에 전달되는 Order 객체의 total이 올바르게 계산되었는지 확인한다."""
        repo.save.return_value = Order(
            id=1,
            customer_email="buyer@example.com",
            items=sample_items,
            total=250.0,
        )

        service.create_order("buyer@example.com", sample_items)

        saved_order = repo.save.call_args[0][0]
        assert saved_order.total == pytest.approx(250.0)

    def test_empty_items_raises_value_error(self, service):
        with pytest.raises(ValueError, match="주문 항목이 비어있습니다"):
            service.create_order("buyer@example.com", [])

    @pytest.mark.parametrize(
        "items, expected_total",
        [
            ([{"name": "A", "price": 10.0, "quantity": 1}], 10.0),
            ([{"name": "A", "price": 10.0, "quantity": 3}], 30.0),
            (
                [
                    {"name": "A", "price": 10.0, "quantity": 2},
                    {"name": "B", "price": 5.0, "quantity": 4},
                ],
                40.0,
            ),
        ],
        ids=["single-item", "single-item-multiple-qty", "multiple-items"],
    )
    def test_total_calculation_variants(
        self, service, repo, items, expected_total
    ):
        """다양한 항목 조합에서 합계가 올바르게 계산된다."""
        repo.save.side_effect = lambda order: order

        result = service.create_order("buyer@example.com", items)

        assert result.total == pytest.approx(expected_total)


# ---------------------------------------------------------------------------
# confirm_order
# ---------------------------------------------------------------------------


class TestConfirmOrder:

    def test_confirms_pending_order_after_payment(
        self, service, repo, payment, pending_order
    ):
        """결제 성공 시 주문 상태가 CONFIRMED로 변경된다."""
        repo.find_by_id.return_value = pending_order
        payment.charge.return_value = True
        repo.save.side_effect = lambda order: order

        result = service.confirm_order(1)

        assert result.status == OrderStatus.CONFIRMED

    def test_charges_correct_amount(
        self, service, repo, payment, pending_order
    ):
        """결제 게이트웨이에 올바른 금액과 이메일이 전달된다."""
        repo.find_by_id.return_value = pending_order
        payment.charge.return_value = True
        repo.save.side_effect = lambda order: order

        service.confirm_order(1)

        payment.charge.assert_called_once_with(250.0, "buyer@example.com")

    def test_sends_confirmation_email(
        self, service, repo, payment, email, pending_order
    ):
        """확정 후 고객에게 확인 이메일을 발송한다."""
        repo.find_by_id.return_value = pending_order
        payment.charge.return_value = True
        repo.save.side_effect = lambda order: order

        service.confirm_order(1)

        email.send.assert_called_once_with(
            "buyer@example.com",
            "주문 확정",
            f"주문 {pending_order.id}이 확정되었습니다.",
        )

    def test_nonexistent_order_raises_value_error(self, service, repo):
        repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="주문 99을 찾을 수 없습니다"):
            service.confirm_order(99)

    def test_non_pending_order_raises_value_error(
        self, service, repo, confirmed_order
    ):
        repo.find_by_id.return_value = confirmed_order

        with pytest.raises(ValueError, match="확정할 수 없는 상태"):
            service.confirm_order(2)

    def test_payment_failure_raises_runtime_error(
        self, service, repo, payment, pending_order
    ):
        """결제가 실패하면 RuntimeError가 발생하고 주문 상태가 변경되지 않는다."""
        repo.find_by_id.return_value = pending_order
        payment.charge.return_value = False

        with pytest.raises(RuntimeError, match="결제 실패"):
            service.confirm_order(1)

        assert pending_order.status == OrderStatus.PENDING
        repo.save.assert_not_called()

    def test_payment_failure_does_not_send_email(
        self, service, repo, payment, email, pending_order
    ):
        """결제 실패 시 이메일이 발송되지 않는다."""
        repo.find_by_id.return_value = pending_order
        payment.charge.return_value = False

        with pytest.raises(RuntimeError):
            service.confirm_order(1)

        email.send.assert_not_called()


# ---------------------------------------------------------------------------
# cancel_order
# ---------------------------------------------------------------------------


class TestCancelOrder:

    def test_cancels_pending_order(self, service, repo, pending_order):
        """대기 중인 주문을 취소하면 CANCELLED 상태가 된다."""
        repo.find_by_id.return_value = pending_order
        repo.save.side_effect = lambda order: order

        result = service.cancel_order(1)

        assert result.status == OrderStatus.CANCELLED

    def test_nonexistent_order_raises_value_error(self, service, repo):
        repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="주문 42을 찾을 수 없습니다"):
            service.cancel_order(42)

    def test_confirmed_order_cannot_be_cancelled(
        self, service, repo, confirmed_order
    ):
        repo.find_by_id.return_value = confirmed_order

        with pytest.raises(ValueError, match="확정된 주문은 취소할 수 없습니다"):
            service.cancel_order(2)

    def test_cancelled_order_stays_cancelled(self, service, repo, sample_items):
        """이미 취소된 주문에 대해 cancel_order를 호출하면 상태가 유지된다."""
        cancelled = Order(
            id=3,
            customer_email="buyer@example.com",
            items=sample_items,
            status=OrderStatus.CANCELLED,
            total=250.0,
        )
        repo.find_by_id.return_value = cancelled
        repo.save.side_effect = lambda order: order

        result = service.cancel_order(3)

        assert result.status == OrderStatus.CANCELLED
```
