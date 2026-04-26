# Outside-In TDD로 결제 서비스 구현

요구사항: 주문 확인 -> 결제 처리 -> 영수증 발송
외부 의존성: 결제 게이트웨이(Mock), 이메일 서비스(Mock)
접근법: 런던 학파 Outside-In TDD, 이중 루프(Double Loop)

---

## 설계 개요

이중 루프 구조:

```
+-----------------------------------------------------------+
|  바깥 루프: 인수 테스트 (Acceptance Test)                     |
|  RED -> (전체 결제 플로우가 아직 없으므로 실패)                 |
|                                                             |
|   +---------------------------------------------------+    |
|   |  안쪽 루프 1: PaymentService 단위 테스트             |    |
|   |  RED -> GREEN -> REFACTOR                          |    |
|   +---------------------------------------------------+    |
|   +---------------------------------------------------+    |
|   |  안쪽 루프 2: OrderValidator 단위 테스트             |    |
|   +---------------------------------------------------+    |
|                                                             |
|  GREEN -> (단위 테스트를 충분히 통과시키면                     |
|            인수 테스트도 통과한다)                             |
+-----------------------------------------------------------+
```

Mock Roles, Not Objects 원칙에 따라 역할(Role)을 Protocol로 정의한다.
구체적인 구현 클래스(StripeGateway, SmtpEmailService)가 아닌 역할을 대체한다.

---

## Step 0: 역할(Role) 정의 -- Protocol

외부 시스템과의 경계를 Protocol로 선언한다.
프로덕션 코드와 테스트 코드 모두 이 역할에만 의존한다.

```python
# payment/protocols.py
from typing import Protocol
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    amount: int
    currency: str
    customer_email: str


@dataclass(frozen=True)
class PaymentResult:
    transaction_id: str
    success: bool


class PaymentGateway(Protocol):
    """결제 게이트웨이 역할 -- 외부 결제 API 추상화"""

    def charge(self, amount: int, currency: str) -> PaymentResult: ...


class EmailService(Protocol):
    """이메일 서비스 역할 -- 외부 이메일 API 추상화"""

    def send_receipt(
        self, to: str, order_id: str, transaction_id: str
    ) -> None: ...


class OrderRepository(Protocol):
    """주문 저장소 역할"""

    def find_by_id(self, order_id: str) -> Order | None: ...
    def update_status(self, order_id: str, status: str) -> None: ...
```

---

## Step 1: 바깥 루프 -- 인수 테스트 작성 (RED)

전체 결제 플로우를 블랙박스로 검증하는 인수 테스트를 먼저 작성한다.
`PaymentService`도, `OrderValidator`도 아직 존재하지 않으므로 이 테스트는 반드시 실패한다.

```python
# tests/test_acceptance_payment.py
import pytest
from unittest.mock import Mock, create_autospec

from payment.protocols import (
    Order, PaymentResult, PaymentGateway, EmailService, OrderRepository,
)
# PaymentService는 아직 존재하지 않는다 -- 이 import에서 실패한다
from payment.service import PaymentService


class TestAcceptancePaymentFlow:
    """바깥 루프: 주문확인 -> 결제 -> 영수증 전체 플로우"""

    def test_successful_payment_flow(self):
        order = Order(
            order_id="ORD-001",
            amount=50000,
            currency="KRW",
            customer_email="buyer@example.com",
        )

        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = order

        mock_gateway = create_autospec(PaymentGateway)
        mock_gateway.charge.return_value = PaymentResult(
            transaction_id="TXN-ABC", success=True
        )

        mock_email = create_autospec(EmailService)

        service = PaymentService(
            repository=mock_repo,
            gateway=mock_gateway,
            email_service=mock_email,
        )

        result = service.process_payment("ORD-001")

        assert result.transaction_id == "TXN-ABC"
        assert result.success is True

        mock_repo.find_by_id.assert_called_once_with("ORD-001")
        mock_repo.update_status.assert_called_once_with("ORD-001", "paid")
        mock_gateway.charge.assert_called_once_with(50000, "KRW")
        mock_email.send_receipt.assert_called_once_with(
            "buyer@example.com", "ORD-001", "TXN-ABC"
        )
```

```
$ pytest tests/test_acceptance_payment.py

E   ModuleNotFoundError: No module named 'payment.service'

FAILED -- 바깥 루프 RED 확인
```

인수 테스트가 RED인 상태를 유지한 채 안쪽 루프로 진입한다.

---

## Step 2: 안쪽 루프 1 -- 주문 검증 (RED -> GREEN -> REFACTOR)

### 2-1. RED: 존재하지 않는 주문 검증

```python
# tests/test_order_validator.py
import pytest
from unittest.mock import create_autospec

from payment.protocols import Order, OrderRepository
from payment.validator import OrderValidator  # 아직 없다


class TestOrderValidator:
    def test_raises_when_order_not_found(self):
        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = None

        validator = OrderValidator(mock_repo)

        with pytest.raises(ValueError, match="Order not found"):
            validator.validate("ORD-MISSING")
```

```
$ pytest tests/test_order_validator.py::TestOrderValidator::test_raises_when_order_not_found

E   ModuleNotFoundError: No module named 'payment.validator'

FAILED -- RED
```

### 2-2. GREEN: 최소 구현

```python
# payment/validator.py
from payment.protocols import Order, OrderRepository


class OrderValidator:
    def __init__(self, repository: OrderRepository):
        self._repository = repository

    def validate(self, order_id: str) -> Order:
        order = self._repository.find_by_id(order_id)
        if order is None:
            raise ValueError("Order not found")
        return order
```

```
$ pytest tests/test_order_validator.py::TestOrderValidator::test_raises_when_order_not_found

PASSED -- GREEN
```

### 2-3. RED: 금액이 0 이하인 주문 검증

```python
# tests/test_order_validator.py (추가)
    def test_raises_when_amount_is_zero(self):
        order = Order(
            order_id="ORD-002", amount=0, currency="KRW",
            customer_email="test@example.com",
        )
        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = order

        validator = OrderValidator(mock_repo)

        with pytest.raises(ValueError, match="Invalid order amount"):
            validator.validate("ORD-002")
```

```
$ pytest tests/test_order_validator.py::TestOrderValidator::test_raises_when_amount_is_zero

FAILED -- ValueError not raised -- RED
```

### 2-4. GREEN: 금액 검증 추가

```python
# payment/validator.py
from payment.protocols import Order, OrderRepository


class OrderValidator:
    def __init__(self, repository: OrderRepository):
        self._repository = repository

    def validate(self, order_id: str) -> Order:
        order = self._repository.find_by_id(order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.amount <= 0:
            raise ValueError("Invalid order amount")
        return order
```

```
$ pytest tests/test_order_validator.py

2 passed -- GREEN
```

### 2-5. RED: 정상 주문은 Order 반환

```python
# tests/test_order_validator.py (추가)
    def test_returns_order_when_valid(self):
        order = Order(
            order_id="ORD-003", amount=50000, currency="KRW",
            customer_email="buyer@example.com",
        )
        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = order

        validator = OrderValidator(mock_repo)
        result = validator.validate("ORD-003")

        assert result == order
        mock_repo.find_by_id.assert_called_once_with("ORD-003")
```

```
$ pytest tests/test_order_validator.py

3 passed -- GREEN (Obvious Implementation: 이미 반환하고 있었다)
```

### REFACTOR

코드가 간결하므로 리팩터링 불필요. 안쪽 루프 1 완료.

---

## Step 3: 안쪽 루프 2 -- PaymentService (RED -> GREEN -> REFACTOR)

### 3-1. RED: 결제 처리 성공 경로

```python
# tests/test_payment_service.py
import pytest
from unittest.mock import Mock, create_autospec, call

from payment.protocols import (
    Order, PaymentResult, PaymentGateway, EmailService, OrderRepository,
)
from payment.service import PaymentService  # 아직 없다


class TestPaymentService:
    def setup_method(self):
        self.order = Order(
            order_id="ORD-001",
            amount=50000,
            currency="KRW",
            customer_email="buyer@example.com",
        )
        self.mock_repo = create_autospec(OrderRepository)
        self.mock_repo.find_by_id.return_value = self.order

        self.mock_gateway = create_autospec(PaymentGateway)
        self.mock_gateway.charge.return_value = PaymentResult(
            transaction_id="TXN-ABC", success=True
        )

        self.mock_email = create_autospec(EmailService)

    def test_successful_payment_charges_gateway(self):
        service = PaymentService(
            repository=self.mock_repo,
            gateway=self.mock_gateway,
            email_service=self.mock_email,
        )

        result = service.process_payment("ORD-001")

        self.mock_gateway.charge.assert_called_once_with(50000, "KRW")
        assert result.transaction_id == "TXN-ABC"
        assert result.success is True
```

```
$ pytest tests/test_payment_service.py

E   ModuleNotFoundError: No module named 'payment.service'

FAILED -- RED
```

### 3-2. GREEN: 최소 구현 -- 결제만 처리

```python
# payment/service.py
from payment.protocols import (
    PaymentResult, PaymentGateway, EmailService, OrderRepository,
)
from payment.validator import OrderValidator


class PaymentService:
    def __init__(
        self,
        repository: OrderRepository,
        gateway: PaymentGateway,
        email_service: EmailService,
    ):
        self._validator = OrderValidator(repository)
        self._repository = repository
        self._gateway = gateway
        self._email_service = email_service

    def process_payment(self, order_id: str) -> PaymentResult:
        order = self._validator.validate(order_id)
        result = self._gateway.charge(order.amount, order.currency)
        return result
```

```
$ pytest tests/test_payment_service.py::TestPaymentService::test_successful_payment_charges_gateway

PASSED -- GREEN
```

### 3-3. RED: 결제 성공 후 주문 상태 업데이트

```python
# tests/test_payment_service.py (추가)
    def test_successful_payment_updates_order_status(self):
        service = PaymentService(
            repository=self.mock_repo,
            gateway=self.mock_gateway,
            email_service=self.mock_email,
        )

        service.process_payment("ORD-001")

        self.mock_repo.update_status.assert_called_once_with("ORD-001", "paid")
```

```
$ pytest tests/test_payment_service.py::TestPaymentService::test_successful_payment_updates_order_status

E   AssertionError: Expected call not found

FAILED -- RED
```

### 3-4. GREEN: 상태 업데이트 추가

```python
# payment/service.py -- process_payment 수정
    def process_payment(self, order_id: str) -> PaymentResult:
        order = self._validator.validate(order_id)
        result = self._gateway.charge(order.amount, order.currency)
        if result.success:
            self._repository.update_status(order_id, "paid")
        return result
```

```
$ pytest tests/test_payment_service.py -k "updates_order"

PASSED -- GREEN
```

### 3-5. RED: 결제 성공 후 영수증 발송

```python
# tests/test_payment_service.py (추가)
    def test_successful_payment_sends_receipt(self):
        service = PaymentService(
            repository=self.mock_repo,
            gateway=self.mock_gateway,
            email_service=self.mock_email,
        )

        service.process_payment("ORD-001")

        self.mock_email.send_receipt.assert_called_once_with(
            "buyer@example.com", "ORD-001", "TXN-ABC"
        )
```

```
$ pytest tests/test_payment_service.py::TestPaymentService::test_successful_payment_sends_receipt

E   AssertionError: Expected call not found

FAILED -- RED
```

### 3-6. GREEN: 영수증 발송 추가

```python
# payment/service.py -- process_payment 수정
    def process_payment(self, order_id: str) -> PaymentResult:
        order = self._validator.validate(order_id)
        result = self._gateway.charge(order.amount, order.currency)
        if result.success:
            self._repository.update_status(order_id, "paid")
            self._email_service.send_receipt(
                order.customer_email, order_id, result.transaction_id
            )
        return result
```

```
$ pytest tests/test_payment_service.py

3 passed -- GREEN
```

### 3-7. RED: 결제 실패 시 영수증 미발송

```python
# tests/test_payment_service.py (추가)
    def test_failed_payment_does_not_send_receipt(self):
        self.mock_gateway.charge.return_value = PaymentResult(
            transaction_id="", success=False
        )

        service = PaymentService(
            repository=self.mock_repo,
            gateway=self.mock_gateway,
            email_service=self.mock_email,
        )

        result = service.process_payment("ORD-001")

        assert result.success is False
        self.mock_email.send_receipt.assert_not_called()
        self.mock_repo.update_status.assert_not_called()
```

```
$ pytest tests/test_payment_service.py -k "does_not_send"

PASSED -- GREEN (이미 if result.success 분기가 있었다 -- Obvious Implementation)
```

### 3-8. RED: 결제 게이트웨이 예외 전파

```python
# tests/test_payment_service.py (추가)
    def test_gateway_exception_propagates(self):
        self.mock_gateway.charge.side_effect = RuntimeError("Gateway timeout")

        service = PaymentService(
            repository=self.mock_repo,
            gateway=self.mock_gateway,
            email_service=self.mock_email,
        )

        with pytest.raises(RuntimeError, match="Gateway timeout"):
            service.process_payment("ORD-001")

        self.mock_email.send_receipt.assert_not_called()
        self.mock_repo.update_status.assert_not_called()
```

```
$ pytest tests/test_payment_service.py -k "gateway_exception"

PASSED -- GREEN (예외가 자연스럽게 전파된다)
```

### REFACTOR

모든 테스트가 GREEN이다. 리팩터링 기회를 점검한다.

```python
# payment/service.py -- 최종 리팩터링 결과
from payment.protocols import (
    PaymentResult, PaymentGateway, EmailService, OrderRepository,
)
from payment.validator import OrderValidator


class PaymentService:
    def __init__(
        self,
        repository: OrderRepository,
        gateway: PaymentGateway,
        email_service: EmailService,
    ):
        self._validator = OrderValidator(repository)
        self._repository = repository
        self._gateway = gateway
        self._email_service = email_service

    def process_payment(self, order_id: str) -> PaymentResult:
        order = self._validator.validate(order_id)
        result = self._gateway.charge(order.amount, order.currency)
        if result.success:
            self._confirm_payment(order_id, order.customer_email, result.transaction_id)
        return result

    def _confirm_payment(
        self, order_id: str, customer_email: str, transaction_id: str
    ) -> None:
        self._repository.update_status(order_id, "paid")
        self._email_service.send_receipt(customer_email, order_id, transaction_id)
```

성공 경로의 부수 효과(상태 업데이트 + 영수증)를 `_confirm_payment`로 추출했다.
Tell, Don't Ask: PaymentService가 결과를 질의하여 분기하는 것이 아니라, 성공 시 확인 행위를 수행한다.

```
$ pytest tests/test_payment_service.py

5 passed -- 리팩터링 후에도 GREEN 유지
```

---

## Step 4: 바깥 루프 다시 확인 (RED -> GREEN)

안쪽 루프에서 모든 구성 요소를 구현했다. 인수 테스트를 다시 실행한다.

```
$ pytest tests/test_acceptance_payment.py

PASSED -- 바깥 루프 GREEN!
```

인수 테스트가 통과한다. 이중 루프가 완성되었다.

---

## Step 5: 추가 인수 테스트 -- 실패 경로 (RED -> GREEN)

### 5-1. RED: 결제 실패 인수 테스트

```python
# tests/test_acceptance_payment.py (추가)
    def test_failed_payment_does_not_confirm_order(self):
        order = Order(
            order_id="ORD-002",
            amount=30000,
            currency="KRW",
            customer_email="buyer2@example.com",
        )

        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = order

        mock_gateway = create_autospec(PaymentGateway)
        mock_gateway.charge.return_value = PaymentResult(
            transaction_id="", success=False
        )

        mock_email = create_autospec(EmailService)

        service = PaymentService(
            repository=mock_repo,
            gateway=mock_gateway,
            email_service=mock_email,
        )

        result = service.process_payment("ORD-002")

        assert result.success is False
        mock_repo.update_status.assert_not_called()
        mock_email.send_receipt.assert_not_called()
```

```
$ pytest tests/test_acceptance_payment.py

2 passed -- 이미 구현되어 있으므로 즉시 GREEN
```

### 5-2. RED: 존재하지 않는 주문 인수 테스트

```python
# tests/test_acceptance_payment.py (추가)
    def test_nonexistent_order_raises_error(self):
        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = None

        mock_gateway = create_autospec(PaymentGateway)
        mock_email = create_autospec(EmailService)

        service = PaymentService(
            repository=mock_repo,
            gateway=mock_gateway,
            email_service=mock_email,
        )

        with pytest.raises(ValueError, match="Order not found"):
            service.process_payment("ORD-GHOST")

        mock_gateway.charge.assert_not_called()
        mock_email.send_receipt.assert_not_called()
```

```
$ pytest tests/test_acceptance_payment.py

3 passed -- GREEN
```

---

## 최종 코드 전체

### payment/protocols.py

```python
from typing import Protocol
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    amount: int
    currency: str
    customer_email: str


@dataclass(frozen=True)
class PaymentResult:
    transaction_id: str
    success: bool


class PaymentGateway(Protocol):
    def charge(self, amount: int, currency: str) -> PaymentResult: ...


class EmailService(Protocol):
    def send_receipt(self, to: str, order_id: str, transaction_id: str) -> None: ...


class OrderRepository(Protocol):
    def find_by_id(self, order_id: str) -> Order | None: ...
    def update_status(self, order_id: str, status: str) -> None: ...
```

### payment/validator.py

```python
from payment.protocols import Order, OrderRepository


class OrderValidator:
    def __init__(self, repository: OrderRepository):
        self._repository = repository

    def validate(self, order_id: str) -> Order:
        order = self._repository.find_by_id(order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.amount <= 0:
            raise ValueError("Invalid order amount")
        return order
```

### payment/service.py

```python
from payment.protocols import (
    PaymentResult, PaymentGateway, EmailService, OrderRepository,
)
from payment.validator import OrderValidator


class PaymentService:
    def __init__(
        self,
        repository: OrderRepository,
        gateway: PaymentGateway,
        email_service: EmailService,
    ):
        self._validator = OrderValidator(repository)
        self._repository = repository
        self._gateway = gateway
        self._email_service = email_service

    def process_payment(self, order_id: str) -> PaymentResult:
        order = self._validator.validate(order_id)
        result = self._gateway.charge(order.amount, order.currency)
        if result.success:
            self._confirm_payment(order_id, order.customer_email, result.transaction_id)
        return result

    def _confirm_payment(
        self, order_id: str, customer_email: str, transaction_id: str
    ) -> None:
        self._repository.update_status(order_id, "paid")
        self._email_service.send_receipt(customer_email, order_id, transaction_id)
```

### tests/test_order_validator.py

```python
import pytest
from unittest.mock import create_autospec

from payment.protocols import Order, OrderRepository
from payment.validator import OrderValidator


class TestOrderValidator:
    def test_raises_when_order_not_found(self):
        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = None

        validator = OrderValidator(mock_repo)

        with pytest.raises(ValueError, match="Order not found"):
            validator.validate("ORD-MISSING")

    def test_raises_when_amount_is_zero(self):
        order = Order(
            order_id="ORD-002", amount=0, currency="KRW",
            customer_email="test@example.com",
        )
        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = order

        validator = OrderValidator(mock_repo)

        with pytest.raises(ValueError, match="Invalid order amount"):
            validator.validate("ORD-002")

    def test_returns_order_when_valid(self):
        order = Order(
            order_id="ORD-003", amount=50000, currency="KRW",
            customer_email="buyer@example.com",
        )
        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = order

        validator = OrderValidator(mock_repo)
        result = validator.validate("ORD-003")

        assert result == order
        mock_repo.find_by_id.assert_called_once_with("ORD-003")
```

### tests/test_payment_service.py

```python
import pytest
from unittest.mock import create_autospec

from payment.protocols import (
    Order, PaymentResult, PaymentGateway, EmailService, OrderRepository,
)
from payment.service import PaymentService


class TestPaymentService:
    def setup_method(self):
        self.order = Order(
            order_id="ORD-001",
            amount=50000,
            currency="KRW",
            customer_email="buyer@example.com",
        )
        self.mock_repo = create_autospec(OrderRepository)
        self.mock_repo.find_by_id.return_value = self.order

        self.mock_gateway = create_autospec(PaymentGateway)
        self.mock_gateway.charge.return_value = PaymentResult(
            transaction_id="TXN-ABC", success=True,
        )

        self.mock_email = create_autospec(EmailService)

    def _make_service(self) -> PaymentService:
        return PaymentService(
            repository=self.mock_repo,
            gateway=self.mock_gateway,
            email_service=self.mock_email,
        )

    def test_successful_payment_charges_gateway(self):
        service = self._make_service()

        result = service.process_payment("ORD-001")

        self.mock_gateway.charge.assert_called_once_with(50000, "KRW")
        assert result.transaction_id == "TXN-ABC"
        assert result.success is True

    def test_successful_payment_updates_order_status(self):
        service = self._make_service()

        service.process_payment("ORD-001")

        self.mock_repo.update_status.assert_called_once_with("ORD-001", "paid")

    def test_successful_payment_sends_receipt(self):
        service = self._make_service()

        service.process_payment("ORD-001")

        self.mock_email.send_receipt.assert_called_once_with(
            "buyer@example.com", "ORD-001", "TXN-ABC"
        )

    def test_failed_payment_does_not_send_receipt(self):
        self.mock_gateway.charge.return_value = PaymentResult(
            transaction_id="", success=False,
        )
        service = self._make_service()

        result = service.process_payment("ORD-001")

        assert result.success is False
        self.mock_email.send_receipt.assert_not_called()
        self.mock_repo.update_status.assert_not_called()

    def test_gateway_exception_propagates(self):
        self.mock_gateway.charge.side_effect = RuntimeError("Gateway timeout")
        service = self._make_service()

        with pytest.raises(RuntimeError, match="Gateway timeout"):
            service.process_payment("ORD-001")

        self.mock_email.send_receipt.assert_not_called()
        self.mock_repo.update_status.assert_not_called()
```

### tests/test_acceptance_payment.py

```python
import pytest
from unittest.mock import create_autospec

from payment.protocols import (
    Order, PaymentResult, PaymentGateway, EmailService, OrderRepository,
)
from payment.service import PaymentService


class TestAcceptancePaymentFlow:
    def test_successful_payment_flow(self):
        order = Order(
            order_id="ORD-001", amount=50000, currency="KRW",
            customer_email="buyer@example.com",
        )

        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = order

        mock_gateway = create_autospec(PaymentGateway)
        mock_gateway.charge.return_value = PaymentResult(
            transaction_id="TXN-ABC", success=True,
        )

        mock_email = create_autospec(EmailService)

        service = PaymentService(
            repository=mock_repo,
            gateway=mock_gateway,
            email_service=mock_email,
        )

        result = service.process_payment("ORD-001")

        assert result.transaction_id == "TXN-ABC"
        assert result.success is True
        mock_repo.find_by_id.assert_called_once_with("ORD-001")
        mock_repo.update_status.assert_called_once_with("ORD-001", "paid")
        mock_gateway.charge.assert_called_once_with(50000, "KRW")
        mock_email.send_receipt.assert_called_once_with(
            "buyer@example.com", "ORD-001", "TXN-ABC",
        )

    def test_failed_payment_does_not_confirm_order(self):
        order = Order(
            order_id="ORD-002", amount=30000, currency="KRW",
            customer_email="buyer2@example.com",
        )

        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = order

        mock_gateway = create_autospec(PaymentGateway)
        mock_gateway.charge.return_value = PaymentResult(
            transaction_id="", success=False,
        )

        mock_email = create_autospec(EmailService)

        service = PaymentService(
            repository=mock_repo,
            gateway=mock_gateway,
            email_service=mock_email,
        )

        result = service.process_payment("ORD-002")

        assert result.success is False
        mock_repo.update_status.assert_not_called()
        mock_email.send_receipt.assert_not_called()

    def test_nonexistent_order_raises_error(self):
        mock_repo = create_autospec(OrderRepository)
        mock_repo.find_by_id.return_value = None

        mock_gateway = create_autospec(PaymentGateway)
        mock_email = create_autospec(EmailService)

        service = PaymentService(
            repository=mock_repo,
            gateway=mock_gateway,
            email_service=mock_email,
        )

        with pytest.raises(ValueError, match="Order not found"):
            service.process_payment("ORD-GHOST")

        mock_gateway.charge.assert_not_called()
        mock_email.send_receipt.assert_not_called()
```

---

## 이중 루프 TDD 흐름 요약

| 단계 | 루프 | 상태 | 설명 |
|------|------|------|------|
| 1 | 바깥 | RED | 인수 테스트 작성 -- `PaymentService`가 없어 실패 |
| 2 | 안쪽 | RED->GREEN | `OrderValidator` -- 주문 미존재 검증 |
| 3 | 안쪽 | RED->GREEN | `OrderValidator` -- 금액 검증 |
| 4 | 안쪽 | GREEN | `OrderValidator` -- 정상 주문 반환 |
| 5 | 안쪽 | RED->GREEN | `PaymentService` -- 결제 게이트웨이 호출 |
| 6 | 안쪽 | RED->GREEN | `PaymentService` -- 주문 상태 업데이트 |
| 7 | 안쪽 | RED->GREEN | `PaymentService` -- 영수증 발송 |
| 8 | 안쪽 | GREEN | `PaymentService` -- 실패 시 미발송 (이미 통과) |
| 9 | 안쪽 | GREEN | `PaymentService` -- 예외 전파 (이미 통과) |
| 10 | 안쪽 | REFACTOR | `_confirm_payment` 메서드 추출 |
| 11 | 바깥 | GREEN | 인수 테스트 통과 -- 이중 루프 완성 |
| 12 | 바깥 | GREEN | 추가 인수 테스트(실패 경로, 미존재 주문) 통과 |

## 적용된 원칙 정리

- **Outside-In TDD (런던 학파)**: 바깥(인수 테스트)에서 시작하여 안쪽(단위 테스트)으로 진입
- **이중 루프**: 인수 테스트 RED 유지 상태에서 단위 테스트 RED->GREEN->REFACTOR 반복
- **Mock Roles, Not Objects**: `PaymentGateway`, `EmailService`, `OrderRepository`는 Protocol(역할)이며, 구체 클래스가 아닌 역할을 Mock
- **Tell, Don't Ask**: `PaymentService`가 결과를 받아 분기하는 대신, `_confirm_payment`으로 확인 행위를 위임
- **행위 검증**: `assert_called_once_with`로 협력 객체에 올바른 메시지를 보냈는지 검증
- **create_autospec**: Protocol의 시그니처를 준수하는 Mock 생성으로 타입 안전성 확보
- **Green Bar 전략**: Fake It 없이 Obvious Implementation 위주 (요구사항이 명확하므로)
- **Three Laws 준수**: 모든 프로덕션 코드는 실패하는 테스트가 먼저 존재한 후에만 작성
