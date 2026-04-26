# OrderService Test Code

```python
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from order_service import (
    EmailService,
    Order,
    OrderRepository,
    OrderService,
    OrderStatus,
    PaymentGateway,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_repo():
    return MagicMock(spec=OrderRepository)


@pytest.fixture
def mock_payment():
    return MagicMock(spec=PaymentGateway)


@pytest.fixture
def mock_email():
    return MagicMock(spec=EmailService)


@pytest.fixture
def service(mock_repo, mock_payment, mock_email):
    return OrderService(repo=mock_repo, payment=mock_payment, email=mock_email)


@pytest.fixture
def sample_items():
    return [
        {"name": "Widget", "price": 1000, "quantity": 2},
        {"name": "Gadget", "price": 2500, "quantity": 1},
    ]


@pytest.fixture
def pending_order(sample_items):
    return Order(
        id=1,
        customer_email="test@example.com",
        items=sample_items,
        status=OrderStatus.PENDING,
        created_at=datetime(2026, 1, 1),
        total=4500.0,
    )


@pytest.fixture
def confirmed_order(sample_items):
    return Order(
        id=2,
        customer_email="test@example.com",
        items=sample_items,
        status=OrderStatus.CONFIRMED,
        created_at=datetime(2026, 1, 1),
        total=4500.0,
    )


@pytest.fixture
def cancelled_order(sample_items):
    return Order(
        id=3,
        customer_email="test@example.com",
        items=sample_items,
        status=OrderStatus.CANCELLED,
        created_at=datetime(2026, 1, 1),
        total=4500.0,
    )


# ===========================================================================
# create_order
# ===========================================================================

class TestCreateOrder:
    """OrderService.create_order 메서드 테스트"""

    def test_create_order_success(self, service, mock_repo, sample_items):
        """정상적인 주문 생성 시 Order 객체가 반환된다."""
        saved_order = Order(
            id=1,
            customer_email="buyer@example.com",
            items=sample_items,
            total=4500.0,
            created_at=datetime(2026, 1, 1),
        )
        mock_repo.save.return_value = saved_order

        result = service.create_order("buyer@example.com", sample_items)

        assert result == saved_order
        mock_repo.save.assert_called_once()

    def test_create_order_calculates_total_correctly(
        self, service, mock_repo, sample_items
    ):
        """total이 price * quantity 합산으로 올바르게 계산된다."""
        mock_repo.save.side_effect = lambda order: order

        result = service.create_order("buyer@example.com", sample_items)

        # 1000*2 + 2500*1 = 4500
        assert result.total == 4500.0

    def test_create_order_sets_pending_status(self, service, mock_repo, sample_items):
        """생성된 주문의 상태는 PENDING이다."""
        mock_repo.save.side_effect = lambda order: order

        result = service.create_order("buyer@example.com", sample_items)

        assert result.status == OrderStatus.PENDING

    def test_create_order_sets_created_at(self, service, mock_repo, sample_items):
        """created_at이 현재 시각으로 설정된다."""
        mock_repo.save.side_effect = lambda order: order

        result = service.create_order("buyer@example.com", sample_items)

        assert result.created_at is not None
        assert isinstance(result.created_at, datetime)

    def test_create_order_stores_customer_email(self, service, mock_repo, sample_items):
        """customer_email이 올바르게 저장된다."""
        mock_repo.save.side_effect = lambda order: order

        result = service.create_order("buyer@example.com", sample_items)

        assert result.customer_email == "buyer@example.com"

    def test_create_order_stores_items(self, service, mock_repo, sample_items):
        """items 목록이 올바르게 저장된다."""
        mock_repo.save.side_effect = lambda order: order

        result = service.create_order("buyer@example.com", sample_items)

        assert result.items == sample_items

    def test_create_order_calls_repo_save(self, service, mock_repo, sample_items):
        """repo.save가 Order 객체와 함께 호출된다."""
        mock_repo.save.side_effect = lambda order: order

        service.create_order("buyer@example.com", sample_items)

        mock_repo.save.assert_called_once()
        saved_arg = mock_repo.save.call_args[0][0]
        assert isinstance(saved_arg, Order)

    def test_create_order_empty_items_raises_value_error(self, service):
        """빈 항목 리스트로 주문 시 ValueError가 발생한다."""
        with pytest.raises(ValueError, match="주문 항목이 비어있습니다"):
            service.create_order("buyer@example.com", [])

    def test_create_order_single_item(self, service, mock_repo):
        """단일 항목 주문이 정상적으로 처리된다."""
        items = [{"name": "Single", "price": 500, "quantity": 3}]
        mock_repo.save.side_effect = lambda order: order

        result = service.create_order("buyer@example.com", items)

        assert result.total == 1500.0


# ===========================================================================
# confirm_order
# ===========================================================================

class TestConfirmOrder:
    """OrderService.confirm_order 메서드 테스트"""

    def test_confirm_order_success(
        self, service, mock_repo, mock_payment, mock_email, pending_order
    ):
        """PENDING 주문이 정상적으로 확정된다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_payment.charge.return_value = True
        mock_repo.save.side_effect = lambda order: order

        result = service.confirm_order(1)

        assert result.status == OrderStatus.CONFIRMED

    def test_confirm_order_charges_payment(
        self, service, mock_repo, mock_payment, pending_order
    ):
        """결제 게이트웨이에 올바른 금액과 이메일이 전달된다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_payment.charge.return_value = True
        mock_repo.save.side_effect = lambda order: order

        service.confirm_order(1)

        mock_payment.charge.assert_called_once_with(
            pending_order.total, pending_order.customer_email
        )

    def test_confirm_order_saves_to_repo(
        self, service, mock_repo, mock_payment, pending_order
    ):
        """확정된 주문이 repo에 저장된다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_payment.charge.return_value = True
        mock_repo.save.side_effect = lambda order: order

        service.confirm_order(1)

        mock_repo.save.assert_called_once()
        saved_arg = mock_repo.save.call_args[0][0]
        assert saved_arg.status == OrderStatus.CONFIRMED

    def test_confirm_order_sends_email(
        self, service, mock_repo, mock_payment, mock_email, pending_order
    ):
        """확정 후 고객에게 이메일이 발송된다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_payment.charge.return_value = True
        mock_repo.save.side_effect = lambda order: order

        service.confirm_order(1)

        mock_email.send.assert_called_once_with(
            pending_order.customer_email,
            "주문 확정",
            f"주문 {pending_order.id}이 확정되었습니다.",
        )

    def test_confirm_order_not_found_raises_value_error(self, service, mock_repo):
        """존재하지 않는 주문 확정 시 ValueError가 발생한다."""
        mock_repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="주문 99을 찾을 수 없습니다"):
            service.confirm_order(99)

    def test_confirm_order_already_confirmed_raises_value_error(
        self, service, mock_repo, confirmed_order
    ):
        """이미 확정된 주문을 다시 확정하면 ValueError가 발생한다."""
        mock_repo.find_by_id.return_value = confirmed_order

        with pytest.raises(ValueError, match="확정할 수 없는 상태"):
            service.confirm_order(2)

    def test_confirm_order_cancelled_raises_value_error(
        self, service, mock_repo, cancelled_order
    ):
        """취소된 주문을 확정하면 ValueError가 발생한다."""
        mock_repo.find_by_id.return_value = cancelled_order

        with pytest.raises(ValueError, match="확정할 수 없는 상태"):
            service.confirm_order(3)

    def test_confirm_order_payment_failure_raises_runtime_error(
        self, service, mock_repo, mock_payment, pending_order
    ):
        """결제 실패 시 RuntimeError가 발생한다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_payment.charge.return_value = False

        with pytest.raises(RuntimeError, match="결제 실패"):
            service.confirm_order(1)

    def test_confirm_order_payment_failure_does_not_save(
        self, service, mock_repo, mock_payment, pending_order
    ):
        """결제 실패 시 주문이 저장되지 않는다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_payment.charge.return_value = False

        with pytest.raises(RuntimeError):
            service.confirm_order(1)

        mock_repo.save.assert_not_called()

    def test_confirm_order_payment_failure_does_not_send_email(
        self, service, mock_repo, mock_payment, mock_email, pending_order
    ):
        """결제 실패 시 이메일이 발송되지 않는다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_payment.charge.return_value = False

        with pytest.raises(RuntimeError):
            service.confirm_order(1)

        mock_email.send.assert_not_called()

    def test_confirm_order_status_not_changed_on_payment_failure(
        self, service, mock_repo, mock_payment, pending_order
    ):
        """결제 실패 시 주문 상태가 PENDING으로 유지된다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_payment.charge.return_value = False

        with pytest.raises(RuntimeError):
            service.confirm_order(1)

        assert pending_order.status == OrderStatus.PENDING


# ===========================================================================
# cancel_order
# ===========================================================================

class TestCancelOrder:
    """OrderService.cancel_order 메서드 테스트"""

    def test_cancel_pending_order_success(
        self, service, mock_repo, pending_order
    ):
        """PENDING 주문이 정상적으로 취소된다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_repo.save.side_effect = lambda order: order

        result = service.cancel_order(1)

        assert result.status == OrderStatus.CANCELLED

    def test_cancel_order_saves_to_repo(
        self, service, mock_repo, pending_order
    ):
        """취소된 주문이 repo에 저장된다."""
        mock_repo.find_by_id.return_value = pending_order
        mock_repo.save.side_effect = lambda order: order

        service.cancel_order(1)

        mock_repo.save.assert_called_once()
        saved_arg = mock_repo.save.call_args[0][0]
        assert saved_arg.status == OrderStatus.CANCELLED

    def test_cancel_order_not_found_raises_value_error(self, service, mock_repo):
        """존재하지 않는 주문 취소 시 ValueError가 발생한다."""
        mock_repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="주문 99을 찾을 수 없습니다"):
            service.cancel_order(99)

    def test_cancel_confirmed_order_raises_value_error(
        self, service, mock_repo, confirmed_order
    ):
        """확정된 주문을 취소하면 ValueError가 발생한다."""
        mock_repo.find_by_id.return_value = confirmed_order

        with pytest.raises(ValueError, match="확정된 주문은 취소할 수 없습니다"):
            service.cancel_order(2)

    def test_cancel_confirmed_order_does_not_save(
        self, service, mock_repo, confirmed_order
    ):
        """확정된 주문 취소 시도 시 repo.save가 호출되지 않는다."""
        mock_repo.find_by_id.return_value = confirmed_order

        with pytest.raises(ValueError):
            service.cancel_order(2)

        mock_repo.save.assert_not_called()

    def test_cancel_already_cancelled_order(
        self, service, mock_repo, cancelled_order
    ):
        """이미 취소된 주문을 다시 취소해도 정상 처리된다."""
        mock_repo.find_by_id.return_value = cancelled_order
        mock_repo.save.side_effect = lambda order: order

        result = service.cancel_order(3)

        assert result.status == OrderStatus.CANCELLED
```
