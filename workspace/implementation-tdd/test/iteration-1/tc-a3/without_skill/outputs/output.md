# Outside-In TDD (London School) -- 결제 서비스 구현

## 개요

London School TDD(Mockist TDD)의 핵심 원칙:
- **바깥에서 안으로** 설계를 발견해 나간다
- 협력 객체(Collaborator)는 **Mock**으로 대체하여 단위를 격리한다
- **이중 루프**: 인수 테스트(Acceptance)가 RED인 상태에서, 안쪽 단위 테스트로 각 객체를 구현한다

```
┌─────────────────────────────────────────────┐
│  바깥 루프 (Acceptance Test) — RED          │
│                                             │
│   ┌─────────────────────────────────┐       │
│   │ 안쪽 루프 (Unit Test)           │       │
│   │  RED → GREEN → REFACTOR         │       │
│   │  RED → GREEN → REFACTOR         │       │
│   │  ...반복...                     │       │
│   └─────────────────────────────────┘       │
│                                             │
│  바깥 루프 — GREEN                          │
└─────────────────────────────────────────────┘
```

---

## STEP 0: 도메인 모델 정의

먼저 공유할 데이터 타입을 정의한다.

```python
# domain.py
from dataclasses import dataclass
from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentResult(Enum):
    SUCCESS = "success"
    DECLINED = "declined"
    ERROR = "error"


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_email: str
    amount: int          # 원 단위
    description: str
    status: OrderStatus = OrderStatus.PENDING


@dataclass(frozen=True)
class PaymentResponse:
    result: PaymentResult
    transaction_id: str
    message: str


@dataclass(frozen=True)
class Receipt:
    order_id: str
    transaction_id: str
    amount: int
    description: str
```

---

## STEP 1: Protocol로 역할(Role) 정의

Outside-In TDD에서는 구현 전에 **역할(인터페이스)**부터 발견한다.
Python의 `Protocol`을 사용하여 구조적 서브타이핑(structural subtyping)으로 정의한다.

```python
# protocols.py
from typing import Protocol

from domain import Order, PaymentResponse, Receipt


class OrderValidator(Protocol):
    """주문을 검증하는 역할"""
    def validate(self, order: Order) -> bool: ...


class PaymentGateway(Protocol):
    """외부 결제 API와 통신하는 역할"""
    def charge(self, order: Order) -> PaymentResponse: ...


class ReceiptSender(Protocol):
    """영수증을 발송하는 역할 (외부 이메일 API)"""
    def send(self, email: str, receipt: Receipt) -> bool: ...
```

---

## STEP 2: 바깥 루프 -- 인수 테스트 작성 (RED)

전체 흐름을 검증하는 인수 테스트를 먼저 작성한다.
아직 `PaymentService`가 존재하지 않으므로 **RED** 상태다.

```python
# test_acceptance.py
"""
바깥 루프: 인수 테스트 (Acceptance Test)
전체 시나리오를 검증한다. 이 테스트가 GREEN이 되면 기능 완성.
"""
import pytest
from unittest.mock import Mock, call

from domain import (
    Order, OrderStatus, PaymentResponse, PaymentResult, Receipt,
)
from protocols import OrderValidator, PaymentGateway, ReceiptSender


class TestPaymentServiceAcceptance:
    """
    시나리오: 고객이 주문을 결제하면
      주문이 확인되고 → 결제가 처리되고 → 영수증이 발송된다.
    """

    def test_successful_payment_flow(self):
        """성공 시나리오: 주문확인 → 결제처리 → 영수증발송"""
        # Given -- 협력 객체를 Mock으로 준비
        order = Order(
            order_id="ORD-001",
            customer_email="hyun@example.com",
            amount=50000,
            description="Python 책 1권",
        )

        validator: OrderValidator = Mock(spec=OrderValidator)
        validator.validate.return_value = True

        gateway: PaymentGateway = Mock(spec=PaymentGateway)
        gateway.charge.return_value = PaymentResponse(
            result=PaymentResult.SUCCESS,
            transaction_id="TXN-ABC-123",
            message="결제 완료",
        )

        sender: ReceiptSender = Mock(spec=ReceiptSender)
        sender.send.return_value = True

        # When -- 아직 존재하지 않는 PaymentService 호출
        from payment_service import PaymentService

        service = PaymentService(
            validator=validator,
            gateway=gateway,
            sender=sender,
        )
        result = service.process(order)

        # Then -- 전체 흐름이 순서대로 실행되었는지 검증
        assert result.status == OrderStatus.COMPLETED

        # 각 협력 객체가 올바른 인자로 호출되었는지 검증
        validator.validate.assert_called_once_with(order)
        gateway.charge.assert_called_once_with(order)
        sender.send.assert_called_once_with(
            "hyun@example.com",
            Receipt(
                order_id="ORD-001",
                transaction_id="TXN-ABC-123",
                amount=50000,
                description="Python 책 1권",
            ),
        )

    def test_payment_declined_flow(self):
        """실패 시나리오: 결제가 거절되면 영수증을 보내지 않는다"""
        order = Order(
            order_id="ORD-002",
            customer_email="hyun@example.com",
            amount=100000,
            description="비싼 키보드",
        )

        validator: OrderValidator = Mock(spec=OrderValidator)
        validator.validate.return_value = True

        gateway: PaymentGateway = Mock(spec=PaymentGateway)
        gateway.charge.return_value = PaymentResponse(
            result=PaymentResult.DECLINED,
            transaction_id="",
            message="잔액 부족",
        )

        sender: ReceiptSender = Mock(spec=ReceiptSender)

        from payment_service import PaymentService

        service = PaymentService(
            validator=validator,
            gateway=gateway,
            sender=sender,
        )
        result = service.process(order)

        # Then
        assert result.status == OrderStatus.FAILED
        validator.validate.assert_called_once_with(order)
        gateway.charge.assert_called_once_with(order)
        sender.send.assert_not_called()  # 영수증 발송 안 됨

    def test_invalid_order_flow(self):
        """실패 시나리오: 주문 검증 실패 시 결제/발송 모두 안 한다"""
        order = Order(
            order_id="ORD-003",
            customer_email="",
            amount=-1000,
            description="",
        )

        validator: OrderValidator = Mock(spec=OrderValidator)
        validator.validate.return_value = False

        gateway: PaymentGateway = Mock(spec=PaymentGateway)
        sender: ReceiptSender = Mock(spec=ReceiptSender)

        from payment_service import PaymentService

        service = PaymentService(
            validator=validator,
            gateway=gateway,
            sender=sender,
        )
        result = service.process(order)

        # Then
        assert result.status == OrderStatus.FAILED
        validator.validate.assert_called_once_with(order)
        gateway.charge.assert_not_called()   # 결제 시도 안 함
        sender.send.assert_not_called()      # 영수증 발송 안 함
```

### 실행 결과 -- 바깥 루프 RED

```
$ pytest test_acceptance.py -v

FAILED test_acceptance.py::TestPaymentServiceAcceptance::test_successful_payment_flow
    ModuleNotFoundError: No module named 'payment_service'
FAILED test_acceptance.py::TestPaymentServiceAcceptance::test_payment_declined_flow
    ModuleNotFoundError: No module named 'payment_service'
FAILED test_acceptance.py::TestPaymentServiceAcceptance::test_invalid_order_flow
    ModuleNotFoundError: No module named 'payment_service'

========== 3 failed ==========
```

> **바깥 루프는 RED 상태. 이제 안쪽 루프로 진입한다.**

---

## STEP 3: 안쪽 루프 -- 단위 테스트로 PaymentService 구현

### 3-1. 단위 테스트 작성 (안쪽 RED)

`PaymentService`의 행위를 하나씩 단위 테스트로 정의한다.

```python
# test_payment_service.py
"""
안쪽 루프: PaymentService 단위 테스트
각 협력 객체와의 상호작용을 개별적으로 검증한다.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import replace

from domain import (
    Order, OrderStatus, PaymentResponse, PaymentResult, Receipt,
)
from protocols import OrderValidator, PaymentGateway, ReceiptSender


@pytest.fixture
def order():
    return Order(
        order_id="ORD-TEST",
        customer_email="test@example.com",
        amount=30000,
        description="테스트 상품",
    )


@pytest.fixture
def mock_validator():
    return Mock(spec=OrderValidator)


@pytest.fixture
def mock_gateway():
    return Mock(spec=PaymentGateway)


@pytest.fixture
def mock_sender():
    return Mock(spec=ReceiptSender)


@pytest.fixture
def service(mock_validator, mock_gateway, mock_sender):
    from payment_service import PaymentService
    return PaymentService(
        validator=mock_validator,
        gateway=mock_gateway,
        sender=mock_sender,
    )


class TestValidationStep:
    """안쪽 루프 1: 주문 검증 단계"""

    def test_validates_order_first(
        self, service, order, mock_validator, mock_gateway
    ):
        """첫 번째로 주문을 검증해야 한다"""
        # RED -> 아직 PaymentService.process가 없다
        mock_validator.validate.return_value = True
        mock_gateway.charge.return_value = PaymentResponse(
            result=PaymentResult.SUCCESS,
            transaction_id="TXN-1",
            message="ok",
        )

        service.process(order)

        mock_validator.validate.assert_called_once_with(order)

    def test_returns_failed_when_validation_fails(
        self, service, order, mock_validator, mock_gateway, mock_sender
    ):
        """검증 실패 시 FAILED 상태를 반환한다"""
        mock_validator.validate.return_value = False

        result = service.process(order)

        assert result.status == OrderStatus.FAILED
        mock_gateway.charge.assert_not_called()
        mock_sender.send.assert_not_called()


class TestPaymentStep:
    """안쪽 루프 2: 결제 처리 단계"""

    def test_charges_order_after_validation(
        self, service, order, mock_validator, mock_gateway
    ):
        """검증 통과 후 결제를 시도한다"""
        mock_validator.validate.return_value = True
        mock_gateway.charge.return_value = PaymentResponse(
            result=PaymentResult.SUCCESS,
            transaction_id="TXN-1",
            message="ok",
        )

        service.process(order)

        mock_gateway.charge.assert_called_once_with(order)

    def test_returns_failed_when_payment_declined(
        self, service, order, mock_validator, mock_gateway, mock_sender
    ):
        """결제 거절 시 FAILED 상태를 반환한다"""
        mock_validator.validate.return_value = True
        mock_gateway.charge.return_value = PaymentResponse(
            result=PaymentResult.DECLINED,
            transaction_id="",
            message="잔액 부족",
        )

        result = service.process(order)

        assert result.status == OrderStatus.FAILED
        mock_sender.send.assert_not_called()

    def test_returns_failed_when_payment_errors(
        self, service, order, mock_validator, mock_gateway, mock_sender
    ):
        """결제 에러 시 FAILED 상태를 반환한다"""
        mock_validator.validate.return_value = True
        mock_gateway.charge.return_value = PaymentResponse(
            result=PaymentResult.ERROR,
            transaction_id="",
            message="게이트웨이 타임아웃",
        )

        result = service.process(order)

        assert result.status == OrderStatus.FAILED
        mock_sender.send.assert_not_called()


class TestReceiptStep:
    """안쪽 루프 3: 영수증 발송 단계"""

    def test_sends_receipt_after_successful_payment(
        self, service, order, mock_validator, mock_gateway, mock_sender
    ):
        """결제 성공 후 영수증을 발송한다"""
        mock_validator.validate.return_value = True
        mock_gateway.charge.return_value = PaymentResponse(
            result=PaymentResult.SUCCESS,
            transaction_id="TXN-999",
            message="결제 완료",
        )
        mock_sender.send.return_value = True

        service.process(order)

        expected_receipt = Receipt(
            order_id="ORD-TEST",
            transaction_id="TXN-999",
            amount=30000,
            description="테스트 상품",
        )
        mock_sender.send.assert_called_once_with(
            "test@example.com", expected_receipt
        )

    def test_returns_completed_on_full_success(
        self, service, order, mock_validator, mock_gateway, mock_sender
    ):
        """전체 흐름 성공 시 COMPLETED 상태를 반환한다"""
        mock_validator.validate.return_value = True
        mock_gateway.charge.return_value = PaymentResponse(
            result=PaymentResult.SUCCESS,
            transaction_id="TXN-999",
            message="ok",
        )
        mock_sender.send.return_value = True

        result = service.process(order)

        assert result.status == OrderStatus.COMPLETED
```

### 실행 결과 -- 안쪽 루프 RED

```
$ pytest test_payment_service.py -v

FAILED - ModuleNotFoundError: No module named 'payment_service'

========== 7 failed ==========
```

---

### 3-2. PaymentService 최소 구현 (안쪽 GREEN)

단위 테스트를 통과시키기 위한 최소 구현을 작성한다.

```python
# payment_service.py
"""
Outside-In TDD로 발견된 PaymentService.
Protocol로 정의된 역할(협력 객체)에 의존한다.
"""
from dataclasses import replace

from domain import (
    Order, OrderStatus, PaymentResponse, PaymentResult, Receipt,
)
from protocols import OrderValidator, PaymentGateway, ReceiptSender


class PaymentService:
    """
    결제 처리 서비스.

    주문 확인 -> 결제 처리 -> 영수증 발송의 흐름을 조율한다.
    각 단계는 Protocol로 정의된 협력 객체에 위임한다.
    """

    def __init__(
        self,
        validator: OrderValidator,
        gateway: PaymentGateway,
        sender: ReceiptSender,
    ) -> None:
        self._validator = validator
        self._gateway = gateway
        self._sender = sender

    def process(self, order: Order) -> Order:
        # Step 1: 주문 검증
        if not self._validator.validate(order):
            return replace(order, status=OrderStatus.FAILED)

        # Step 2: 결제 처리
        payment_response = self._gateway.charge(order)

        if payment_response.result != PaymentResult.SUCCESS:
            return replace(order, status=OrderStatus.FAILED)

        # Step 3: 영수증 발송
        receipt = Receipt(
            order_id=order.order_id,
            transaction_id=payment_response.transaction_id,
            amount=order.amount,
            description=order.description,
        )
        self._sender.send(order.customer_email, receipt)

        return replace(order, status=OrderStatus.COMPLETED)
```

### 실행 결과 -- 안쪽 루프 GREEN

```
$ pytest test_payment_service.py -v

PASSED test_payment_service.py::TestValidationStep::test_validates_order_first
PASSED test_payment_service.py::TestValidationStep::test_returns_failed_when_validation_fails
PASSED test_payment_service.py::TestPaymentStep::test_charges_order_after_validation
PASSED test_payment_service.py::TestPaymentStep::test_returns_failed_when_payment_declined
PASSED test_payment_service.py::TestPaymentStep::test_returns_failed_when_payment_errors
PASSED test_payment_service.py::TestReceiptStep::test_sends_receipt_after_successful_payment
PASSED test_payment_service.py::TestReceiptStep::test_returns_completed_on_full_success

========== 7 passed ==========
```

---

## STEP 4: 바깥 루프 재실행 -- GREEN 확인

안쪽 루프에서 구현을 완료했으므로, 바깥 루프(인수 테스트)를 다시 실행한다.

```
$ pytest test_acceptance.py -v

PASSED test_acceptance.py::TestPaymentServiceAcceptance::test_successful_payment_flow
PASSED test_acceptance.py::TestPaymentServiceAcceptance::test_payment_declined_flow
PASSED test_acceptance.py::TestPaymentServiceAcceptance::test_invalid_order_flow

========== 3 passed ==========
```

> **바깥 루프 GREEN -- 기능 완성!**

---

## STEP 5: REFACTOR -- 안쪽 루프에서 추가 엣지 케이스

리팩터링 단계에서 엣지 케이스에 대한 테스트를 추가한다.

```python
# test_payment_service.py (추가)

class TestEdgeCases:
    """리팩터링 단계: 엣지 케이스 보강"""

    def test_gateway_raises_exception(
        self, service, order, mock_validator, mock_gateway, mock_sender
    ):
        """결제 게이트웨이 예외 발생 시 FAILED를 반환한다"""
        mock_validator.validate.return_value = True
        mock_gateway.charge.side_effect = ConnectionError("네트워크 장애")

        result = service.process(order)

        assert result.status == OrderStatus.FAILED
        mock_sender.send.assert_not_called()

    def test_sender_raises_exception_still_returns_completed(
        self, service, order, mock_validator, mock_gateway, mock_sender
    ):
        """영수증 발송 실패해도 결제는 성공으로 처리한다"""
        mock_validator.validate.return_value = True
        mock_gateway.charge.return_value = PaymentResponse(
            result=PaymentResult.SUCCESS,
            transaction_id="TXN-X",
            message="ok",
        )
        mock_sender.send.side_effect = ConnectionError("메일 서버 장애")

        result = service.process(order)

        # 결제는 이미 성공했으므로 COMPLETED
        assert result.status == OrderStatus.COMPLETED
```

이 테스트는 RED -- 현재 구현은 예외를 처리하지 않는다.

### 예외 처리 추가 (GREEN)

```python
# payment_service.py (리팩터링)
class PaymentService:

    def __init__(
        self,
        validator: OrderValidator,
        gateway: PaymentGateway,
        sender: ReceiptSender,
    ) -> None:
        self._validator = validator
        self._gateway = gateway
        self._sender = sender

    def process(self, order: Order) -> Order:
        # Step 1: 주문 검증
        if not self._validator.validate(order):
            return replace(order, status=OrderStatus.FAILED)

        # Step 2: 결제 처리
        try:
            payment_response = self._gateway.charge(order)
        except Exception:
            return replace(order, status=OrderStatus.FAILED)

        if payment_response.result != PaymentResult.SUCCESS:
            return replace(order, status=OrderStatus.FAILED)

        # Step 3: 영수증 발송 (결제 성공 후이므로 실패해도 COMPLETED)
        receipt = Receipt(
            order_id=order.order_id,
            transaction_id=payment_response.transaction_id,
            amount=order.amount,
            description=order.description,
        )
        try:
            self._sender.send(order.customer_email, receipt)
        except Exception:
            pass  # 영수증 발송 실패는 별도 재시도 큐로 처리 (범위 밖)

        return replace(order, status=OrderStatus.COMPLETED)
```

### 실행 결과 -- 전체 GREEN

```
$ pytest test_payment_service.py test_acceptance.py -v

PASSED test_payment_service.py::TestValidationStep::test_validates_order_first
PASSED test_payment_service.py::TestValidationStep::test_returns_failed_when_validation_fails
PASSED test_payment_service.py::TestPaymentStep::test_charges_order_after_validation
PASSED test_payment_service.py::TestPaymentStep::test_returns_failed_when_payment_declined
PASSED test_payment_service.py::TestPaymentStep::test_returns_failed_when_payment_errors
PASSED test_payment_service.py::TestReceiptStep::test_sends_receipt_after_successful_payment
PASSED test_payment_service.py::TestReceiptStep::test_returns_completed_on_full_success
PASSED test_payment_service.py::TestEdgeCases::test_gateway_raises_exception
PASSED test_payment_service.py::TestEdgeCases::test_sender_raises_exception_still_returns_completed
PASSED test_acceptance.py::TestPaymentServiceAcceptance::test_successful_payment_flow
PASSED test_acceptance.py::TestPaymentServiceAcceptance::test_payment_declined_flow
PASSED test_acceptance.py::TestPaymentServiceAcceptance::test_invalid_order_flow

========== 12 passed ==========
```

---

## STEP 6: 선택적 구현체 예시

Protocol의 실제 구현체를 보여준다. 이들은 통합 테스트에서 사용된다.

```python
# implementations.py
"""
Protocol의 실제 구현체 예시.
Outside-In TDD에서는 이들을 나중에 구현한다.
"""
from domain import Order, PaymentResponse, PaymentResult, Receipt


class SimpleOrderValidator:
    """OrderValidator Protocol의 구현체"""

    def validate(self, order: Order) -> bool:
        if not order.order_id:
            return False
        if not order.customer_email or "@" not in order.customer_email:
            return False
        if order.amount <= 0:
            return False
        if not order.description:
            return False
        return True


class StripePaymentGateway:
    """PaymentGateway Protocol의 구현체 (외부 API 연동)"""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def charge(self, order: Order) -> PaymentResponse:
        # 실제로는 Stripe API 호출
        # response = stripe.Charge.create(amount=order.amount, ...)
        raise NotImplementedError("실제 Stripe 연동 필요")


class SmtpReceiptSender:
    """ReceiptSender Protocol의 구현체 (외부 이메일 API 연동)"""

    def __init__(self, smtp_host: str, smtp_port: int) -> None:
        self._host = smtp_host
        self._port = smtp_port

    def send(self, email: str, receipt: Receipt) -> bool:
        # 실제로는 SMTP 서버를 통해 이메일 발송
        # smtplib.SMTP(self._host, self._port).send_message(...)
        raise NotImplementedError("실제 SMTP 연동 필요")
```

```python
# test_order_validator.py
"""SimpleOrderValidator의 단위 테스트 (안쪽 루프 추가)"""
import pytest
from domain import Order, OrderStatus
from implementations import SimpleOrderValidator


class TestSimpleOrderValidator:

    @pytest.fixture
    def validator(self):
        return SimpleOrderValidator()

    def test_valid_order(self, validator):
        order = Order(
            order_id="ORD-1",
            customer_email="a@b.com",
            amount=1000,
            description="상품",
        )
        assert validator.validate(order) is True

    def test_empty_order_id(self, validator):
        order = Order(
            order_id="",
            customer_email="a@b.com",
            amount=1000,
            description="상품",
        )
        assert validator.validate(order) is False

    def test_invalid_email(self, validator):
        order = Order(
            order_id="ORD-1",
            customer_email="invalid",
            amount=1000,
            description="상품",
        )
        assert validator.validate(order) is False

    def test_zero_amount(self, validator):
        order = Order(
            order_id="ORD-1",
            customer_email="a@b.com",
            amount=0,
            description="상품",
        )
        assert validator.validate(order) is False

    def test_negative_amount(self, validator):
        order = Order(
            order_id="ORD-1",
            customer_email="a@b.com",
            amount=-500,
            description="상품",
        )
        assert validator.validate(order) is False

    def test_empty_description(self, validator):
        order = Order(
            order_id="ORD-1",
            customer_email="a@b.com",
            amount=1000,
            description="",
        )
        assert validator.validate(order) is False
```

---

## 최종 파일 구조

```
payment-service/
├── domain.py                 # 도메인 모델 (Order, Receipt, etc.)
├── protocols.py              # Protocol 역할 정의
├── payment_service.py        # 핵심 서비스 (TDD로 구현)
├── implementations.py        # Protocol 구현체
├── test_acceptance.py        # 바깥 루프: 인수 테스트
├── test_payment_service.py   # 안쪽 루프: 단위 테스트
└── test_order_validator.py   # 안쪽 루프: 검증기 단위 테스트
```

---

## 이중 루프 TDD 진행 흐름 요약

| 단계 | 루프 | 상태 | 행위 |
|------|------|------|------|
| 1 | 바깥 | RED | 인수 테스트 3개 작성. `PaymentService` 미존재 |
| 2 | 안쪽 | RED | `TestValidationStep` 단위 테스트 작성 |
| 3 | 안쪽 | GREEN | `process()` 검증 로직 구현 |
| 4 | 안쪽 | RED | `TestPaymentStep` 단위 테스트 작성 |
| 5 | 안쪽 | GREEN | `process()` 결제 로직 구현 |
| 6 | 안쪽 | RED | `TestReceiptStep` 단위 테스트 작성 |
| 7 | 안쪽 | GREEN | `process()` 영수증 로직 구현 |
| 8 | 바깥 | GREEN | 인수 테스트 3개 모두 통과 |
| 9 | 안쪽 | RED | `TestEdgeCases` 엣지 케이스 추가 |
| 10 | 안쪽 | GREEN | 예외 처리 추가 |
| 11 | 바깥 | GREEN | 전체 12개 테스트 통과 |

---

## Outside-In TDD 핵심 원칙 정리

1. **바깥에서 시작**: 사용자 시나리오(인수 테스트)를 먼저 작성한다
2. **역할을 발견**: 테스트를 작성하면서 필요한 협력 객체의 역할(Protocol)이 드러난다
3. **Mock으로 격리**: 외부 의존성(결제 게이트웨이, 이메일 서비스)은 Mock으로 대체한다
4. **상호작용 검증**: 상태가 아니라 **메시지 전달**(어떤 메서드가 어떤 인자로 호출되었는지)을 검증한다
5. **안쪽으로 진행**: 인수 테스트가 RED인 상태에서, 단위 테스트로 각 객체를 하나씩 구현한다
6. **바깥 루프로 복귀**: 안쪽 루프가 GREEN이 되면 바깥 루프를 다시 실행하여 전체 통과를 확인한다
