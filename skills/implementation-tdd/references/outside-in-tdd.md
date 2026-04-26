# Outside-In TDD 레퍼런스

이중 루프 TDD, Walking Skeleton, Mock Roles Not Objects, Tell Don't Ask 원칙에 대한 패턴 모음.

---

## 이중 루프 TDD (Double Loop TDD)

"Growing Object-Oriented Software, Guided by Tests"의 핵심 개념. 바깥 루프(인수 테스트)와 안쪽 루프(단위 테스트)를 동시에 운용한다.

```
+---------------------------------------------------+
|  바깥 루프: 인수 테스트 (Acceptance Test)            |
|  RED -> (아직 기능이 없으므로 실패)                   |
|                                                     |
|   +-------------------------------------------+    |
|   |  안쪽 루프: 단위 테스트 (Unit Test)          |    |
|   |  RED -> GREEN -> REFACTOR (반복)            |    |
|   +-------------------------------------------+    |
|                                                     |
|  GREEN -> (단위 테스트를 충분히 통과시키면            |
|            인수 테스트도 통과한다)                    |
+---------------------------------------------------+
```

```python
# === 바깥 루프: 인수 테스트 (End-to-End) ===
def test_acceptance_user_registration(client):
    """전체 시스템을 블랙박스로 취급한다."""
    response = client.post("/register", json={
        "email": "new@example.com",
        "password": "secure123",
    })
    assert response.status_code == 201

    # 실제로 로그인이 되는지 확인
    login_response = client.post("/login", json={
        "email": "new@example.com",
        "password": "secure123",
    })
    assert login_response.status_code == 200


# === 안쪽 루프: 단위 테스트 (Mock 사용) ===
def test_registration_service_saves_user(mocker):
    """서비스 계층이 repository에 올바르게 저장하는지 확인."""
    mock_repo = mocker.Mock()
    mock_hasher = mocker.Mock()
    mock_hasher.hash.return_value = "hashed_pw"

    service = RegistrationService(mock_repo, mock_hasher)
    service.register("new@example.com", "secure123")

    mock_repo.save.assert_called_once()
    saved_user = mock_repo.save.call_args[0][0]
    assert saved_user["email"] == "new@example.com"
    assert saved_user["password"] == "hashed_pw"
```

> 출처: Freeman & Pryce - Growing Object-Oriented Software, Guided by Tests (GOOS)

---

## Walking Skeleton

GOOS의 첫 번째 단계: **가장 얇은 슬라이스의 실제 기능**을 구현하여 빌드, 배포, 테스트가 끝까지(end-to-end) 동작하는 것을 확인한다.

```python
# Walking Skeleton: 최소한의 end-to-end 경로

# 1. 가장 단순한 인수 테스트 작성
def test_walking_skeleton_health_check(client):
    """시스템이 기동되어 응답할 수 있는지 확인하는 가장 얇은 슬라이스."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# 이 테스트가 통과하려면:
# - 웹 서버 기동
# - 라우팅 설정
# - 응답 직렬화
# - 테스트 인프라 (클라이언트 fixture)
# 위의 모든 것이 동작해야 한다 -> 아키텍처 결정을 강제한다
```

> 출처: Freeman & Pryce - Growing Object-Oriented Software, Guided by Tests (GOOS)

---

## Mock Roles, Not Objects

Mock의 대상은 구체적인 객체가 아니라 **역할(Role)** 이다.

```python
from typing import Protocol


# 역할(Role)을 Protocol로 정의
class PaymentGateway(Protocol):
    def charge(self, amount: int, currency: str) -> str: ...


class ReceiptSender(Protocol):
    def send_receipt(self, order_id: str, email: str) -> None: ...


# 프로덕션 코드는 역할(인터페이스)에 의존
class CheckoutService:
    def __init__(self, gateway: PaymentGateway, receipt: ReceiptSender):
        self.gateway = gateway
        self.receipt = receipt

    def checkout(self, order_id: str, amount: int, email: str) -> str:
        transaction_id = self.gateway.charge(amount, "KRW")
        self.receipt.send_receipt(order_id, email)
        return transaction_id


def test_checkout_charges_and_sends_receipt(mocker):
    """역할(PaymentGateway, ReceiptSender)을 Mock한다.
    구체적 구현 클래스(StripeGateway, SmtpSender)가 아닌 역할을 대체."""
    mock_gateway = mocker.Mock(spec=PaymentGateway)
    mock_gateway.charge.return_value = "txn-001"
    mock_receipt = mocker.Mock(spec=ReceiptSender)

    service = CheckoutService(mock_gateway, mock_receipt)
    txn_id = service.checkout("order-1", 50000, "buyer@test.com")

    assert txn_id == "txn-001"
    mock_gateway.charge.assert_called_once_with(50000, "KRW")
    mock_receipt.send_receipt.assert_called_once_with("order-1", "buyer@test.com")
```

> 출처: Freeman, Pryce, Mackinnon, Walnes -- OOPSLA 2004

---

## Tell, Don't Ask 원칙

> "객체에게 정보를 요청해서 우리가 답을 계산하지 말고, 우리가 진짜 원하는 것을 객체에게 말하라(Tell)."

```python
# --- 나쁨: Ask (정보를 가져와서 외부에서 판단) ---
class BadOrderProcessor:
    def process(self, order):
        if order.get_status() == "pending":
            if order.get_total() > 0:
                order.set_status("confirmed")
                self.notifier.send(order.get_email(), "확인됨")


# --- 좋음: Tell (객체에게 행위를 위임) ---
class GoodOrderProcessor:
    def process(self, order):
        order.confirm(self.notifier)  # 객체에게 "확인하라"고 말한다


class Order:
    def confirm(self, notifier):
        """주문 스스로가 확인 로직을 수행한다."""
        if self.status == "pending" and self.total > 0:
            self.status = "confirmed"
            notifier.send(self.email, "확인됨")
```

> 출처: Freeman & Pryce - Growing Object-Oriented Software, Guided by Tests (GOOS)
