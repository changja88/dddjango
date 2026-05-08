# TDD 외부 자료 종합 가이드

> 이 문서는 내부 자료(테스트주도 개발 - Kent Beck, 파이썬코딩의기술)에서 다루지 않은 **외부 권위 있는 자료**의 새로운 관점과 패턴을 정리한다.

---

## 1. TDD 학파 비교: 고전 학파 vs 런던 학파

### 1.1 두 학파의 기원과 핵심 차이 [Fowler - Mocks Aren't Stubs]

Martin Fowler는 "Mocks Aren't Stubs" 아티클에서 TDD의 두 진영을 명확히 구분한다.

| 구분 | 고전 학파 (Detroit/Chicago) | 런던 학파 (London/Mockist) |
|------|---------------------------|--------------------------|
| 별칭 | Classicist, Inside-Out, Bottom-Up | Mockist, Outside-In, Top-Down |
| 단위(Unit) 정의 | 모듈 단위 (단일 클래스 ~ 밀접한 클래스 집합) | 단일 클래스 |
| 협력 객체 처리 | 실제 객체 사용 | Mock으로 대체 |
| 검증 방식 | **상태 검증** (State Verification) | **행위 검증** (Behavior Verification) |
| 테스트 관점 | 블랙박스 테스트 | 화이트박스 테스트 |
| 개발 방향 | 도메인 내부에서 외부로 | 외부 인터페이스에서 내부로 |
| 리팩토링 내성 | 높음 (구현 변경에 강함) | 낮음 (구현 변경 시 테스트도 변경) |
| 대표 인물 | Kent Beck | Steve Freeman, Nat Pryce |

### 1.2 상태 검증 vs 행위 검증 [Fowler - Mocks Aren't Stubs]

```python
import pytest
from unittest.mock import Mock, call


# === 상태 검증 (고전 학파) ===
class Order:
    def __init__(self):
        self.items: list[str] = []

    def add_item(self, item: str) -> None:
        self.items.append(item)

    def item_count(self) -> int:
        return len(self.items)


def test_order_state_verification():
    """상태 검증: 행위 실행 후 객체의 '상태'를 확인한다."""
    order = Order()
    order.add_item("사과")
    order.add_item("바나나")

    # 상태(state)를 검증
    assert order.item_count() == 2
    assert "사과" in order.items


# === 행위 검증 (런던 학파) ===
class OrderService:
    def __init__(self, repository, notifier):
        self.repository = repository
        self.notifier = notifier

    def place_order(self, user_id: str, items: list[str]) -> None:
        order = {"user_id": user_id, "items": items}
        self.repository.save(order)
        self.notifier.send(user_id, f"주문 {len(items)}건 접수")


def test_order_behavior_verification():
    """행위 검증: 협력 객체에 올바른 '메시지'를 보냈는지 확인한다."""
    mock_repo = Mock()
    mock_notifier = Mock()
    service = OrderService(mock_repo, mock_notifier)

    service.place_order("user-1", ["사과", "바나나"])

    # 행위(behavior)를 검증
    mock_repo.save.assert_called_once_with(
        {"user_id": "user-1", "items": ["사과", "바나나"]}
    )
    mock_notifier.send.assert_called_once_with("user-1", "주문 2건 접수")
```

### 1.3 Inside-Out vs Outside-In TDD

**Inside-Out TDD (고전 학파)**

도메인 모델의 핵심부터 시작하여 바깥으로 나아간다. Mock이 거의 필요 없다.

```python
# 1단계: 도메인 핵심 (Money) 먼저 구현
def test_money_addition():
    five = Money(5, "USD")
    ten = Money(10, "USD")
    assert five.plus(ten) == Money(15, "USD")


# 2단계: 도메인 서비스 구현 (실제 Money 사용)
def test_exchange_service():
    service = ExchangeService(rate=1100)
    result = service.convert(Money(10, "USD"), "KRW")
    assert result == Money(11000, "KRW")


# 3단계: API 계층 구현 (실제 서비스 사용)
def test_exchange_endpoint(client):
    response = client.post("/exchange", json={"amount": 10, "from": "USD", "to": "KRW"})
    assert response.json()["amount"] == 11000
```

**Outside-In TDD (런던 학파)**

사용자 인터페이스(외부)에서 시작하여 안쪽으로 파고든다. Mock으로 아직 구현되지 않은 계층을 대체한다.

```python
# 1단계: 외부 인터페이스(API)부터 시작, 내부는 Mock
def test_exchange_endpoint(client, mocker):
    mock_service = mocker.patch("app.exchange_service")
    mock_service.convert.return_value = Money(11000, "KRW")

    response = client.post("/exchange", json={"amount": 10, "from": "USD", "to": "KRW"})

    assert response.json()["amount"] == 11000
    mock_service.convert.assert_called_once()


# 2단계: 서비스 계층 구현, 하위는 Mock
def test_exchange_service(mocker):
    mock_rate_provider = mocker.patch("app.rate_provider")
    mock_rate_provider.get_rate.return_value = 1100

    service = ExchangeService(mock_rate_provider)
    result = service.convert(Money(10, "USD"), "KRW")

    assert result == Money(11000, "KRW")


# 3단계: 가장 안쪽 도메인 구현
def test_money_addition():
    five = Money(5, "USD")
    ten = Money(10, "USD")
    assert five.plus(ten) == Money(15, "USD")
```

### 1.4 실전 권고: 두 학파의 결합

두 접근법은 배타적이지 않다. 실전에서는 상황에 따라 혼합하는 것이 효과적이다.

| 상황 | 권장 접근법 |
|------|-----------|
| 순수 도메인 로직 | 고전 학파 (실제 객체, 상태 검증) |
| 외부 시스템 연동 (DB, API) | 런던 학파 (Mock, 행위 검증) |
| 새로운 기능의 전체 설계 탐색 | Outside-In (런던 학파) |
| 복잡한 알고리즘 구현 | Inside-Out (고전 학파) |

---

## 2. 테스트 더블 공식 분류 체계

### 2.1 Gerard Meszaros의 5가지 분류 [xUnit Test Patterns]

Gerard Meszaros는 "xUnit Test Patterns"에서 영화의 스턴트 더블에서 영감을 받아 **테스트 더블(Test Double)** 이라는 포괄적 용어를 정의했다.

```
                    Test Double
                        |
        +-------+-------+-------+-------+
        |       |       |       |       |
      Dummy   Stub    Spy    Mock    Fake
```

| 종류 | 목적 | 간접 입력 제어 | 간접 출력 검증 | 실제 동작 |
|------|------|:-----------:|:-----------:|:--------:|
| **Dummy** | 매개변수 채우기 | - | - | - |
| **Stub** | 사전 정의된 응답 반환 | O | - | - |
| **Spy** | 호출 기록 + 응답 반환 | O | O | - |
| **Mock** | 기대값 사전 설정 + 자체 검증 | O | O | - |
| **Fake** | 경량 실제 구현 | O | - | O |

### 2.2 각 테스트 더블의 Python 구현

```python
import pytest
from unittest.mock import Mock, MagicMock, call
from typing import Protocol


# --- 프로덕션 코드 ---
class UserRepository(Protocol):
    def find_by_id(self, user_id: str) -> dict | None: ...
    def save(self, user: dict) -> None: ...
    def count(self) -> int: ...


class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class Logger(Protocol):
    def log(self, message: str) -> None: ...


# =============================================
# 1. Dummy: 전달만 되고 실제 사용되지 않는 객체
# =============================================
def test_dummy():
    """Dummy는 매개변수 목록을 채우기 위해서만 존재한다."""
    dummy_logger = Mock(spec=Logger)  # 전달되지만 호출되지 않음

    user_service = UserService(
        repository=InMemoryUserRepository(),
        logger=dummy_logger,  # 이 테스트에서 logger는 사용되지 않음
    )
    result = user_service.get_user("user-1")
    assert result is not None


# =============================================
# 2. Stub: 미리 정해진 응답을 반환하는 객체
# =============================================
def test_stub():
    """Stub은 테스트에 필요한 간접 입력(indirect input)을 제공한다."""
    stub_repo = Mock(spec=UserRepository)
    stub_repo.find_by_id.return_value = {"id": "user-1", "name": "홍길동"}

    service = UserService(repository=stub_repo, logger=Mock())
    user = service.get_user("user-1")

    # Stub에 대해서는 호출 여부를 검증하지 않는다 (상태 검증)
    assert user["name"] == "홍길동"


# =============================================
# 3. Spy: 호출 기록을 남기는 Stub
# =============================================
class SpyEmailSender:
    """Spy는 직접 구현하여 호출 기록을 수집한다."""
    def __init__(self):
        self.sent_emails: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent_emails.append({"to": to, "subject": subject, "body": body})


def test_spy():
    """Spy는 호출 이력을 기록하고, 테스트에서 나중에 검증한다."""
    spy_sender = SpyEmailSender()
    service = NotificationService(email_sender=spy_sender)

    service.notify_welcome("user@example.com")

    assert len(spy_sender.sent_emails) == 1
    assert spy_sender.sent_emails[0]["to"] == "user@example.com"
    assert "환영" in spy_sender.sent_emails[0]["subject"]


# =============================================
# 4. Mock: 기대값을 사전 설정하고 스스로 검증하는 객체
# =============================================
def test_mock():
    """Mock은 '어떤 호출이 일어나야 하는지' 사전 기대를 갖고 자체 검증한다."""
    mock_repo = Mock(spec=UserRepository)
    service = UserService(repository=mock_repo, logger=Mock())

    service.create_user({"id": "user-2", "name": "이순신"})

    # Mock 자체의 기대값 검증 (행위 검증)
    mock_repo.save.assert_called_once_with({"id": "user-2", "name": "이순신"})


# =============================================
# 5. Fake: 경량 실제 구현을 가진 객체
# =============================================
class InMemoryUserRepository:
    """Fake는 실제 동작하는 경량 구현이다. (프로덕션에는 부적합)"""
    def __init__(self):
        self._store: dict[str, dict] = {}

    def find_by_id(self, user_id: str) -> dict | None:
        return self._store.get(user_id)

    def save(self, user: dict) -> None:
        self._store[user["id"]] = user

    def count(self) -> int:
        return len(self._store)


def test_fake():
    """Fake는 실제 로직을 수행하지만 프로덕션 의존성(DB 등)을 우회한다."""
    fake_repo = InMemoryUserRepository()
    service = UserService(repository=fake_repo, logger=Mock())

    service.create_user({"id": "user-3", "name": "세종대왕"})
    user = service.get_user("user-3")

    assert user["name"] == "세종대왕"
    assert fake_repo.count() == 1
```

### 2.3 Stub과 Mock의 핵심 차이 [Fowler - Mocks Aren't Stubs]

> "Stub은 상태 검증을 사용하고, Mock은 행위 검증을 사용한다. 둘의 차이는 테스트에서 검증하는 대상이 다르다는 것이다." (의역)
> -- Martin Fowler

- **Stub**: SUT(System Under Test)에 간접 입력을 제공한다. 테스트는 SUT의 **결과 상태**를 검증한다.
- **Mock**: SUT의 간접 출력을 검증한다. 테스트는 SUT가 협력 객체에 보내는 **메시지(호출)**를 검증한다.

---

## 3. 좋은 단위 테스트의 4대 특성 [Khorikov - Unit Testing Principles]

### 3.1 네 가지 기둥 (Four Pillars)

Vladimir Khorikov는 좋은 단위 테스트의 가치를 평가하는 4가지 기둥을 제시한다.

```
                    좋은 단위 테스트
                          |
        +--------+--------+--------+--------+
        |        |        |        |        |
    회귀 방지   리팩토링   빠른     유지
    (Protection  내성     피드백   보수성
     against   (Resistance (Fast   (Maintain-
     Regressions) to      Feedback) ability)
               Refactoring)
```

| 기둥 | 설명 | 측정 기준 |
|------|------|----------|
| **회귀 방지** | 테스트가 버그를 얼마나 잘 잡는가 | 코드 커버리지, 실행되는 코드량 |
| **리팩토링 내성** | 내부 구현을 바꿔도 테스트가 깨지지 않는가 | 거짓 양성(false positive) 빈도 |
| **빠른 피드백** | 테스트가 빠르게 실행되는가 | 실행 시간 |
| **유지보수성** | 테스트를 이해하고 실행하기 쉬운가 | 테스트 크기, 외부 의존성 수 |

### 3.2 CAP 정리와의 유사성

Khorikov의 핵심 통찰: 처음 세 기둥(회귀 방지, 리팩토링 내성, 빠른 피드백)은 **상호 배타적**이다. 세 가지를 동시에 최대화할 수 없다. CAP 정리처럼 둘을 선택하면 나머지 하나는 희생된다.

```python
# === 회귀 방지 높음 + 리팩토링 내성 높음 = 느린 피드백 (통합 테스트) ===
def test_end_to_end_order_flow(real_db, real_email_service):
    """실제 객체를 사용하여 버그를 잘 잡고 리팩토링에도 강하지만, 느리다."""
    service = OrderService(real_db, real_email_service)
    service.place_order("user-1", ["사과"])

    orders = real_db.query("SELECT * FROM orders WHERE user_id = 'user-1'")
    assert len(orders) == 1


# === 회귀 방지 높음 + 빠른 피드백 = 리팩토링 내성 낮음 (과도한 Mock) ===
def test_over_mocked_order(mocker):
    """Mock으로 빠르고 버그도 잡지만, 구현 변경 시 테스트도 깨진다."""
    mock_db = mocker.patch("app.db")
    mock_email = mocker.patch("app.email")
    service = OrderService(mock_db, mock_email)

    service.place_order("user-1", ["사과"])

    # 내부 구현에 결합된 검증 -> 리팩토링하면 깨진다
    mock_db.execute.assert_called_with(
        "INSERT INTO orders (user_id, items) VALUES (?, ?)",
        ("user-1", '["사과"]'),
    )


# === 리팩토링 내성 높음 + 빠른 피드백 = 회귀 방지 낮음 (너무 단순한 테스트) ===
def test_trivial():
    """빠르고 리팩토링에 강하지만, 의미 있는 버그를 잡지 못한다."""
    assert 1 + 1 == 2
```

### 3.3 세 가지 테스트 스타일 [Khorikov]

| 스타일 | 검증 대상 | 회귀 방지 | 리팩토링 내성 | 유지보수성 |
|--------|----------|:---------:|:-----------:|:---------:|
| **출력 기반** (Output-based) | 반환값 | 높음 | 높음 | 높음 |
| **상태 기반** (State-based) | 객체 상태 | 높음 | 높음 | 중간 |
| **통신 기반** (Communication-based) | 메서드 호출 | 중간 | 낮음 | 낮음 |

```python
# === 출력 기반 테스트 (가장 권장) ===
def calculate_discount(price: float, is_vip: bool) -> float:
    """순수 함수: 부수효과 없이 입력만으로 출력 결정."""
    return price * 0.8 if is_vip else price


def test_output_based():
    """SUT의 반환값만 검증한다. 가장 리팩토링에 강하다."""
    assert calculate_discount(1000, is_vip=True) == 800.0
    assert calculate_discount(1000, is_vip=False) == 1000.0


# === 상태 기반 테스트 ===
class ShoppingCart:
    def __init__(self):
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)


def test_state_based():
    """행위 실행 후 SUT의 상태를 검증한다."""
    cart = ShoppingCart()
    cart.add("사과")

    assert cart.items == ["사과"]  # 상태 검증


# === 통신 기반 테스트 ===
def test_communication_based(mocker):
    """SUT가 협력 객체에 보내는 메시지를 검증한다."""
    mock_sender = mocker.Mock()
    service = NotificationService(mock_sender)

    service.notify("user@test.com", "안녕하세요")

    mock_sender.send.assert_called_once_with("user@test.com", "안녕하세요")
```

Khorikov의 권고: **출력 기반 > 상태 기반 > 통신 기반** 순으로 선호하라. 가능하면 비즈니스 로직을 순수 함수로 추출하여 출력 기반 테스트를 극대화하라.

---

## 4. 테스트의 3대 품질 속성 [Osherove - The Art of Unit Testing]

### 4.1 세 기둥: 신뢰성, 유지보수성, 가독성

Roy Osherove는 좋은 단위 테스트의 세 가지 핵심 품질 속성을 제시한다.

| 속성 | 의미 | 위반 징후 |
|------|------|----------|
| **신뢰성** (Trustworthiness) | 테스트 결과를 믿을 수 있다 | 테스트가 실패해도 무시하게 됨 |
| **유지보수성** (Maintainability) | 코드 변경 시 테스트 수정이 적다 | 사소한 변경에도 테스트가 대량으로 깨짐 |
| **가독성** (Readability) | 테스트 의도를 빠르게 파악할 수 있다 | 테스트 코드를 읽는 데 원본보다 오래 걸림 |

### 4.2 테스트 명명 규칙 [Osherove]

Osherove는 테스트 이름에 세 가지 요소를 포함할 것을 제안한다.

```
[테스트 대상 단위]_[상태/조건]_[기대 행위]
```

```python
# Osherove 명명 규칙 적용

def test_divide__divisor_is_zero__raises_value_error():
    """divide 함수가 0으로 나눌 때 ValueError를 발생시킨다."""
    with pytest.raises(ValueError, match="0으로 나눌 수 없습니다"):
        divide(10, 0)


def test_withdraw__amount_exceeds_balance__returns_insufficient_funds():
    """출금액이 잔액을 초과하면 잔액 부족 오류를 반환한다."""
    account = Account(balance=1000)
    result = account.withdraw(1500)
    assert result.error == "잔액 부족"


def test_parse_email__valid_format__returns_parsed_parts():
    """유효한 이메일 형식이면 파싱된 부분들을 반환한다."""
    result = parse_email("user@example.com")
    assert result.local == "user"
    assert result.domain == "example.com"
```

### 4.3 AAA 패턴: Arrange-Act-Assert [Osherove]

```python
def test_transfer_funds():
    # --- Arrange: 테스트에 필요한 객체와 상태를 준비한다 ---
    source = Account(balance=5000)
    target = Account(balance=1000)
    service = TransferService()

    # --- Act: 테스트 대상 행위를 실행한다 (단 하나만) ---
    result = service.transfer(source, target, amount=2000)

    # --- Assert: 기대 결과를 검증한다 ---
    assert result.success is True
    assert source.balance == 3000
    assert target.balance == 3000
```

---

## 5. Outside-In TDD와 Mock 중심 설계 [Freeman & Pryce - GOOS]

### 5.1 이중 루프 TDD (Double Loop TDD)

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

### 5.2 Walking Skeleton

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

### 5.3 Mock Roles, Not Objects [Freeman, Pryce, Mackinnon, Walnes — OOPSLA 2004]

> 참고: "Mock Roles, Not Objects"는 GOOS(Growing Object-Oriented Software)와 별도의 OOPSLA 2004 논문이다.

Freeman과 Pryce의 핵심 원칙: Mock의 대상은 구체적인 객체가 아니라 **역할(Role)** 이다.

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

### 5.4 Tell, Don't Ask 원칙 [Freeman & Pryce - GOOS]

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

---

## 6. 레거시 코드 다루기 [Feathers - Working Effectively with Legacy Code]

### 6.1 레거시 코드의 정의

> "레거시 코드는 단순히 **테스트가 없는 코드**다. 테스트가 없는 코드는 아무리 잘 작성되었어도 나쁜 코드다."
> -- Michael Feathers

### 6.2 레거시 코드 변경 알고리즘 (The Legacy Code Change Algorithm)

```
1. 변경 지점을 식별한다 (Identify change points)
2. 테스트 지점을 찾는다 (Find test points)
3. 의존성을 깨뜨린다 (Break dependencies)
4. 테스트를 작성한다 (Write tests)
5. 변경하고 리팩토링한다 (Make changes and refactor)
```

### 6.3 Seam 모델 [Feathers]

**Seam(솔기)**: 코드를 편집하지 않고도 동작을 변경할 수 있는 지점이다. 모든 Seam에는 **Enabling Point(활성화 지점)** 가 있다.

| Seam 종류 | 설명 | Enabling Point | Python 적용 |
|-----------|------|---------------|-------------|
| **Object Seam** | 다형성을 이용해 동작 교체 | 객체 생성 시점 | 의존성 주입, Protocol |
| **Link Seam** | 링크/임포트 시점에 교체 | 빌드/임포트 설정 | `unittest.mock.patch` |
| **Preprocessing Seam** | 전처리기에서 교체 | 매크로 정의 | Python에서는 해당 없음 |

```python
# === Object Seam: 의존성 주입으로 테스트 가능하게 만들기 ===

# Before: 테스트 불가능 (내부에서 직접 생성)
class ReportGenerator:
    def generate(self):
        db = PostgresDatabase()  # 직접 생성 -> Seam이 없다
        data = db.query("SELECT * FROM sales")
        return format_report(data)


# After: Object Seam 도입 (의존성 주입)
class ReportGenerator:
    def __init__(self, database):  # Seam: 생성자에서 주입
        self.database = database   # Enabling Point: 객체 생성 시점

    def generate(self):
        data = self.database.query("SELECT * FROM sales")
        return format_report(data)


def test_report_generator():
    """Object Seam을 활용하여 Fake DB를 주입한다."""
    fake_db = InMemoryDatabase({"sales": [{"amount": 1000}, {"amount": 2000}]})
    generator = ReportGenerator(fake_db)
    report = generator.generate()
    assert "3000" in report


# === Link Seam: unittest.mock.patch로 임포트 교체 ===
def test_report_with_link_seam(mocker):
    """모듈 수준의 임포트를 patch로 교체한다 (Link Seam)."""
    mock_db_module = mocker.patch("app.reports.PostgresDatabase")
    mock_db_module.return_value.query.return_value = [{"amount": 500}]

    generator = ReportGenerator()
    report = generator.generate()
    assert "500" in report
```

### 6.4 특성화 테스트 (Characterization Test) [Feathers]

기존 코드의 **현재 동작을 그대로 캡처**하는 테스트. 코드가 "올바른지"가 아니라 "지금 무엇을 하는지"를 기록한다.

```python
# 특성화 테스트 작성 절차:
# 1. 코드를 테스트 하네스에 넣는다
# 2. 의도적으로 틀린 단언을 작성한다
# 3. 실패 메시지에서 실제 동작을 확인한다
# 4. 실제 동작을 단언으로 기록한다

def test_characterize_legacy_tax_calculator():
    """레거시 세금 계산기의 현재 동작을 기록한다.
    이 테스트는 '올바름'을 보장하지 않는다.
    리팩토링 중 동작이 변하지 않음을 보장할 뿐이다."""
    calculator = LegacyTaxCalculator()

    # 현재 동작을 기록 (버그가 있더라도)
    assert calculator.calculate(10000) == 1050  # 10.5%? 의도된 건지 버그인지 모름
    assert calculator.calculate(0) == 0
    assert calculator.calculate(-100) == -10  # 음수 처리도 기록


def test_characterize_legacy_parser():
    """레거시 파서의 엣지케이스 동작을 탐색적으로 기록한다."""
    parser = LegacyCSVParser()

    assert parser.parse("a,b,c") == ["a", "b", "c"]
    assert parser.parse("a,,c") == ["a", "", "c"]      # 빈 필드 처리 확인
    assert parser.parse('a,"b,c",d') == ["a", "b,c", "d"]  # 인용부호 처리 확인
    assert parser.parse("") == []                        # 빈 입력 처리 확인
```

### 6.5 의존성 깨뜨리기 기법 [Feathers]

| 기법 | 설명 | 사용 시기 |
|------|------|----------|
| **Sprout Method** | 새 기능을 별도 메서드로 추출하고 기존 코드에서 호출 | 기존 알고리즘이 명확하고 새 동작이 그 안에 속할 때 |
| **Sprout Class** | 새 기능을 별도 클래스로 추출 | 기존 클래스가 너무 복잡하거나 테스트 하네스에 넣기 어려울 때 |
| **Wrap Method** | 기존 메서드 이름을 바꾸고, 원래 이름의 새 메서드에서 전/후 처리 추가 | 기존 동작과 동등한 수준의 새 동작을 추가할 때 |
| **Wrap Class** | 기존 클래스를 감싸는 새 클래스 생성 (데코레이터 패턴) | 기존 클래스를 변경하지 않고 동작을 추가할 때 |

```python
# === Sprout Method ===
class LegacyOrderProcessor:
    def process(self, order):
        # ... 기존 복잡한 로직 (200줄) ...
        self._validate_inventory(order)  # Sprout: 새 기능을 별도 메서드로
        # ... 나머지 기존 로직 ...

    def _validate_inventory(self, order):
        """새로 추출한 메서드 -> 독립적으로 테스트 가능."""
        for item in order.items:
            if not self.inventory.has_stock(item):
                raise OutOfStockError(item)


def test_validate_inventory():
    """Sprout Method는 독립적으로 테스트할 수 있다."""
    processor = LegacyOrderProcessor(inventory=FakeInventory({"사과": 5}))
    order = Order(items=["사과"])
    processor._validate_inventory(order)  # 예외 없이 통과

    order_out = Order(items=["두리안"])
    with pytest.raises(OutOfStockError):
        processor._validate_inventory(order_out)


# === Wrap Method ===
class LegacyPaymentProcessor:
    def _process_payment_original(self, payment):
        """기존 메서드 이름 변경 (원래 이름: process_payment)."""
        # ... 기존 결제 로직 ...
        pass

    def process_payment(self, payment):
        """새 메서드: 기존 동작을 감싸고 로깅을 추가한다."""
        self.audit_logger.log(f"결제 시작: {payment.amount}")
        result = self._process_payment_original(payment)
        self.audit_logger.log(f"결제 완료: {result.transaction_id}")
        return result


# === Wrap Class (데코레이터 패턴) ===
class AuditedProcessor:
    """Wrap Class: 기존 클래스를 변경하지 않고 감싼다."""
    def __init__(self, wrapped: LegacyPaymentProcessor, logger):
        self._wrapped = wrapped
        self._logger = logger

    def process_payment(self, payment):
        self._logger.log(f"감사 시작: {payment.amount}")
        result = self._wrapped.process_payment(payment)
        self._logger.log(f"감사 완료: {result.transaction_id}")
        return result
```

---

## 7. 테스트 냄새 카탈로그 [Meszaros - xUnit Test Patterns]

### 7.1 행위 냄새 (Behavior Smells)

테스트를 실행할 때 발생하는 문제들.

| 냄새 | 설명 | 해결책 |
|------|------|--------|
| **Assertion Roulette** | 여러 단언 중 어느 것이 실패했는지 알기 어려움 | 각 단언에 메시지 추가, 테스트 분리 |
| **Erratic Test** | 같은 코드인데 때로 성공, 때로 실패 | 공유 상태 제거, 테스트 격리 |
| **Fragile Test** | 관련 없는 코드 변경에도 깨짐 | 구현이 아닌 행위에 대해 테스트 |
| **Frequent Debugging** | 테스트 실패 시 원인을 디버깅해야만 알 수 있음 | 테스트를 작게, 단언을 명확하게 |
| **Slow Test** | 전체 테스트 실행이 수 분~수 시간 소요 | 외부 의존성 제거, 병렬 실행 |
| **Manual Intervention** | 테스트 실행에 사람의 수동 개입 필요 | 완전 자동화 |

```python
# === Assertion Roulette (나쁨) ===
def test_user_creation_roulette():
    user = create_user("홍길동", "hong@test.com", 30)
    assert user.name == "홍길동"       # 이 줄이 실패? 아래 줄이 실패?
    assert user.email == "hong@test.com"
    assert user.age == 30
    assert user.is_active is True


# === Assertion Roulette 해결: 단언 메시지 추가 또는 테스트 분리 ===
def test_user_has_correct_name():
    user = create_user("홍길동", "hong@test.com", 30)
    assert user.name == "홍길동"


def test_user_is_active_by_default():
    user = create_user("홍길동", "hong@test.com", 30)
    assert user.is_active is True


# === Erratic Test (나쁨): 공유 상태로 인한 불안정 ===
shared_list = []  # 전역 공유 상태 -> 테스트 순서에 따라 결과 달라짐

def test_add_item_erratic():
    shared_list.append("item")
    assert len(shared_list) == 1  # 다른 테스트가 먼저 실행되면 실패


# === Erratic Test 해결: 각 테스트에서 독립적인 상태 사용 ===
@pytest.fixture
def fresh_list():
    return []

def test_add_item_stable(fresh_list):
    fresh_list.append("item")
    assert len(fresh_list) == 1  # 항상 성공
```

### 7.2 코드 냄새 (Code Smells)

테스트 코드 자체의 구조적 문제.

| 냄새 | 설명 |
|------|------|
| **Obscure Test** | 테스트를 읽어도 무엇을 테스트하는지 이해하기 어려움 |
| **Conditional Test Logic** | 테스트 안에 if/else, try/catch 등 분기 로직이 있음 |
| **Hard-Coded Test Data** | 테스트 데이터가 매직 넘버로 하드코딩되어 의미 불명 |
| **Test Code Duplication** | 여러 테스트에서 동일한 설정/검증 코드가 반복됨 |
| **Eager Test** | 하나의 테스트에서 너무 많은 조건을 검증하려 함 |

```python
# === Obscure Test (나쁨) ===
def test_x():
    r = f(42, True, None, "abc")
    assert r == 17  # 무엇을 테스트하는가?


# === Obscure Test 해결: 의도를 드러내는 이름과 변수 ===
def test_calculate_shipping_fee_for_domestic_order():
    weight_kg = 42
    is_fragile = True
    coupon = None
    destination = "서울"

    fee = calculate_shipping(weight_kg, is_fragile, coupon, destination)

    expected_fee = 17000  # 42kg * 400원 + 취급비 200원
    assert fee == expected_fee
```

---

## 8. Property-Based Testing [Hypothesis]

### 8.1 예제 기반 테스트의 한계

전통적인 예제 기반 테스트는 개발자가 **선택한 특정 입력값**만 검증한다. Property-Based Testing은 **속성(property)** 을 정의하고 수백~수천 가지 무작위 입력으로 검증한다.

```python
from hypothesis import given, assume, settings, example
from hypothesis import strategies as st


# === 예제 기반 테스트: 개발자가 선택한 케이스만 검증 ===
def test_sort_example_based():
    assert sort_list([3, 1, 2]) == [1, 2, 3]
    assert sort_list([]) == []
    assert sort_list([1]) == [1]
    # 개발자가 떠올리지 못한 엣지케이스는? 음수? 중복값? 매우 큰 리스트?


# === Property-Based 테스트: 속성으로 정의하고 무작위 검증 ===
@given(st.lists(st.integers()))
def test_sort_preserves_length(xs):
    """속성: 정렬해도 리스트 길이는 변하지 않는다."""
    assert len(sort_list(xs)) == len(xs)


@given(st.lists(st.integers()))
def test_sort_is_ordered(xs):
    """속성: 정렬 결과의 모든 인접 쌍은 오름차순이다."""
    result = sort_list(xs)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]


@given(st.lists(st.integers()))
def test_sort_preserves_elements(xs):
    """속성: 정렬 후에도 동일한 원소들이 존재한다."""
    assert sorted(sort_list(xs)) == sorted(xs)
```

### 8.2 Hypothesis 주요 전략(Strategy)

```python
from hypothesis import strategies as st

# --- 기본 전략 ---
st.integers()                        # 임의의 정수
st.integers(min_value=0, max_value=100)  # 범위 제한
st.floats(allow_nan=False)           # NaN 제외한 실수
st.text(min_size=1, max_size=50)     # 1~50자 텍스트
st.booleans()                        # True/False
st.none()                            # None
st.binary()                          # 바이트열

# --- 컬렉션 전략 ---
st.lists(st.integers(), min_size=1, max_size=20)  # 정수 리스트
st.sets(st.text())                   # 문자열 집합
st.dictionaries(st.text(), st.integers())  # 딕셔너리
st.tuples(st.integers(), st.text())  # 튜플

# --- 조합 전략 ---
st.one_of(st.integers(), st.text())  # 정수 또는 텍스트
st.integers() | st.none()            # 정수 또는 None (동일)
```

### 8.3 복합 전략 (@composite)

```python
from hypothesis import strategies as st
from hypothesis.strategies import composite
from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int
    email: str


@composite
def users(draw):
    """복합 전략: 여러 전략을 조합하여 커스텀 객체를 생성한다."""
    name = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=("L",)  # 문자만
    )))
    age = draw(st.integers(min_value=0, max_value=150))
    email = draw(st.emails())
    return User(name=name, age=age, email=email)


@given(users())
def test_user_display_name_contains_name(user):
    """생성된 모든 User에 대해 display_name이 name을 포함한다."""
    assert user.name in user.display_name()
```

### 8.4 assume()과 축소(Shrinking)

```python
from hypothesis import given, assume
from hypothesis import strategies as st


@given(st.integers(), st.integers())
def test_division_is_inverse_of_multiplication(a, b):
    """나눗셈은 곱셈의 역연산이다. (0 제외)"""
    assume(b != 0)  # b가 0인 경우는 버린다
    assert (a * b) / b == pytest.approx(a)


# Shrinking: Hypothesis가 버그를 찾으면 가능한 한 가장 단순한 반례를 보고한다.
# 예: [1000, -523, 47, 0, 256] 에서 실패 -> [0] 으로 축소
@given(st.lists(st.integers(), min_size=1))
def test_max_is_greater_than_or_equal_to_all(xs):
    """리스트의 최대값은 모든 원소 이상이다."""
    m = max(xs)
    for x in xs:
        assert m >= x
```

### 8.5 settings와 example

```python
from hypothesis import given, settings, example
from hypothesis import strategies as st


@settings(max_examples=500, deadline=None)
@example(xs=[0, 0, 0])   # 반드시 이 입력도 테스트에 포함
@example(xs=[-1, 1])      # 특정 엣지케이스를 명시적으로 추가
@given(st.lists(st.integers()))
def test_sum_of_sorted_equals_sum_of_original(xs):
    """정렬 전후의 합계는 동일하다."""
    assert sum(sorted(xs)) == sum(xs)
```

---

## 9. Mutation Testing [mutmut]

### 9.1 개념: 테스트의 테스트

뮤테이션 테스트는 소스 코드에 의도적으로 **작은 변형(mutant)** 을 가하고, 테스트 스위트가 이를 **감지(kill)** 하는지 확인한다. 감지하지 못한 변형은 테스트에 구멍이 있음을 의미한다.

```
원본 코드:  if x > 0:
변형 1:     if x >= 0:    # 비교 연산자 변경
변형 2:     if x < 0:     # 비교 연산자 반전
변형 3:     if True:       # 조건 상수화
```

### 9.2 뮤테이션 종류

| 뮤테이션 유형 | 원본 | 변형 |
|-------------|------|------|
| 산술 연산자 | `a + b` | `a - b` |
| 비교 연산자 | `x > 0` | `x >= 0` |
| 논리 연산자 | `a and b` | `a or b` |
| 상수 변형 | `return 0` | `return 1` |
| 부정 제거 | `not x` | `x` |
| 문장 삭제 | `x += 1` | `(삭제)` |

### 9.3 mutmut 사용법

```bash
# 설치
pip install mutmut

# 실행: 소스 코드에 뮤턴트를 생성하고 테스트 실행
mutmut run --paths-to-mutate "src/" --tests-dir "tests/"

# 결과 확인
mutmut results

# 개별 뮤턴트 상세 확인
mutmut show 42
```

### 9.4 결과 해석

```
뮤테이션 점수(Mutation Score) = 죽인 뮤턴트 / 전체 뮤턴트 x 100

- Killed (죽음): 테스트가 변형을 감지함 -> 좋음
- Survived (생존): 테스트가 변형을 감지 못함 -> 테스트 보강 필요
- Timeout: 뮤턴트가 무한루프 유발 -> 보통 죽인 것으로 간주
- Suspicious: 비정상 종료 -> 수동 확인 필요
```

```python
# === 뮤테이션 테스트에 취약한 코드 ===
def calculate_discount(price: float, quantity: int) -> float:
    if quantity > 10:
        return price * 0.9  # 10% 할인
    return price


def test_discount_weak():
    """이 테스트는 mutmut에서 생존하는 뮤턴트를 남긴다."""
    assert calculate_discount(1000, 15) == 900  # quantity > 10 만 테스트
    # mutmut이 > 를 >= 로 바꾸면? quantity=10 케이스가 없어서 감지 못함!


# === 뮤테이션 테스트에 강한 코드 ===
def test_discount_strong():
    """경계값을 포함하여 뮤턴트를 죽인다."""
    assert calculate_discount(1000, 15) == 900   # > 10: 할인 적용
    assert calculate_discount(1000, 10) == 1000  # == 10: 할인 미적용 (경계)
    assert calculate_discount(1000, 11) == 900   # == 11: 할인 적용 (경계+1)
    assert calculate_discount(1000, 5) == 1000   # < 10: 할인 미적용
```

### 9.5 뮤테이션 점수 목표

80% 이상의 뮤테이션 점수가 테스트 스위트의 강력한 결함 감지 능력을 나타낸다. 100%를 목표로 하기보다는 **생존한 뮤턴트를 분석**하여 의미 있는 테스트를 추가하는 것이 중요하다.

---

## 10. BDD (Behavior-Driven Development) [Cucumber, pytest-bdd]

### 10.1 TDD와 BDD의 관계

BDD는 TDD의 **진화형**이다. TDD가 개발자 중심의 코드 정확성에 집중한다면, BDD는 비즈니스 요구사항을 자연어로 표현하여 이해관계자와의 소통을 중시한다.

```
TDD 진화 경로:
TDD (코드 정확성) -> ATDD (인수 테스트) -> BDD (행위 명세 + 소통)
```

| 구분 | TDD | BDD |
|------|-----|-----|
| 관점 | 개발자 중심 | 사용자/비즈니스 중심 |
| 명세 언어 | 프로그래밍 언어 | 자연어 (Gherkin) |
| 테스트 단위 | 함수/클래스 | 시나리오/행위 |
| 산출물 | 단위 테스트 | 살아있는 문서(living documentation) |
| 참여자 | 개발자 | 개발자 + 기획자 + QA |

### 10.2 Given-When-Then [Daniel Terhorst-North & Chris Matts]

```gherkin
# features/order.feature
Feature: 주문 처리
    사용자가 상품을 주문하고 결제할 수 있다.

    Scenario: 재고가 있는 상품 주문
        Given 상품 "노트북"의 재고가 5개 있다
        And 사용자의 장바구니에 "노트북" 1개가 담겨있다
        When 사용자가 주문을 확정한다
        Then 주문이 성공적으로 생성된다
        And 재고가 4개로 감소한다

    Scenario: 재고 부족 시 주문 실패
        Given 상품 "태블릿"의 재고가 0개 있다
        And 사용자의 장바구니에 "태블릿" 1개가 담겨있다
        When 사용자가 주문을 확정한다
        Then "재고 부족" 오류가 발생한다
```

### 10.3 pytest-bdd로 구현

```python
# tests/test_order.py
import pytest
from pytest_bdd import scenario, given, when, then, parsers


@scenario("../features/order.feature", "재고가 있는 상품 주문")
def test_order_with_stock():
    pass


@scenario("../features/order.feature", "재고 부족 시 주문 실패")
def test_order_without_stock():
    pass


# --- Given 단계: 초기 상태 설정 ---
@given(
    parsers.parse('상품 "{product}"의 재고가 {count:d}개 있다'),
    target_fixture="inventory",
)
def inventory_with_stock(product, count):
    inventory = Inventory()
    inventory.set_stock(product, count)
    return inventory


@given(
    parsers.parse('사용자의 장바구니에 "{product}" {count:d}개가 담겨있다'),
    target_fixture="cart",
)
def cart_with_item(product, count):
    cart = ShoppingCart()
    cart.add(product, count)
    return cart


# --- When 단계: 행위 실행 ---
@when("사용자가 주문을 확정한다", target_fixture="order_result")
def place_order(inventory, cart):
    service = OrderService(inventory)
    try:
        order = service.place_order(cart)
        return {"success": True, "order": order}
    except InsufficientStockError as e:
        return {"success": False, "error": str(e)}


# --- Then 단계: 결과 검증 ---
@then("주문이 성공적으로 생성된다")
def order_created(order_result):
    assert order_result["success"] is True


@then(parsers.parse("재고가 {count:d}개로 감소한다"))
def stock_decreased(inventory, count):
    # inventory fixture를 통해 재고 확인
    assert inventory.get_stock("노트북") == count


@then(parsers.parse('"{message}" 오류가 발생한다'))
def error_occurred(order_result, message):
    assert order_result["success"] is False
    assert message in order_result["error"]
```

---

## 11. TDD와 AI 코딩의 관계

### 11.1 TDD as Prompt Engineering

> "TDD는 프롬프트 엔지니어링이다. 테스트가 AI에게 '무엇을' 만들고 '언제 완료인지'를 알려준다."

TDD의 Red-Green-Refactor 사이클은 AI 코딩 도구와 자연스럽게 결합된다.

```
전통 TDD:     개발자가 테스트 작성 -> 개발자가 구현
AI 보조 TDD:  개발자가 테스트 작성 -> AI가 구현 제안 -> 개발자가 검증
TDAID:        Plan -> Red -> Green(AI) -> Refactor(AI+개발자) -> Validate
```

### 11.2 AI 보조 TDD 워크플로우

```python
# 1단계: 개발자가 명세로서의 테스트를 작성한다 (Red)
def test_parse_korean_date():
    """한국어 날짜 문자열을 파싱한다."""
    assert parse_date("2026년 4월 4일") == date(2026, 4, 4)
    assert parse_date("2026년 12월 25일") == date(2026, 12, 25)


def test_parse_korean_date_edge_cases():
    """엣지케이스를 포함한다."""
    with pytest.raises(ValueError):
        parse_date("잘못된 날짜")
    with pytest.raises(ValueError):
        parse_date("2026년 13월 1일")  # 13월은 없다

# 2단계: AI에게 구현을 요청한다 (Green)
# "위 테스트를 통과하는 parse_date 함수를 구현해줘"
# -> AI가 구현 제안

# 3단계: 개발자가 AI 구현을 검증하고 리팩토링한다 (Refactor)
# - 테스트가 통과하는가?
# - 코드가 의도대로인가?
# - 보안 문제나 환각(hallucination)이 없는가?
```

### 11.3 TDD가 AI 코딩에서 더 중요한 이유

| 위험 | TDD의 방어 효과 |
|------|---------------|
| AI 환각 (hallucinated code) | 실패하는 테스트가 잘못된 구현을 즉시 감지 |
| 의도와 다른 구현 | 테스트가 명세 역할을 하여 의도를 명시 |
| 보안 취약점 | 보안 테스트가 AI 생성 코드의 취약점 포착 |
| 과도한 신뢰 | Red-Green 사이클이 점진적 검증을 강제 |

### 11.4 Test-Driven AI Development (TDAID) 5단계

```
1. Plan     : 기능 요구사항을 테스트 목록으로 변환
2. Red      : 실패하는 테스트 작성 (개발자)
3. Green    : 테스트를 통과하는 구현 (AI 보조)
4. Refactor : 코드 품질 개선 (AI + 개발자 협업)
5. Validate : AI 생성 코드의 정확성, 보안, 성능 최종 검증
```

---

## 12. Python 테스트 생태계 심화

### 12.1 pytest-mock: mocker fixture

```python
# pytest-mock은 unittest.mock을 pytest fixture로 감싼 얇은 래퍼이다.
# mocker fixture는 자동으로 테스트 종료 시 patch를 해제한다.

def test_with_mocker(mocker):
    # --- mocker.patch: 모듈 수준 객체 교체 ---
    mock_requests = mocker.patch("app.service.requests")
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {"data": "value"}

    result = fetch_data("https://api.example.com/data")
    assert result == {"data": "value"}

    # --- mocker.patch.object: 특정 객체의 메서드 교체 ---
    calculator = Calculator()
    mocker.patch.object(calculator, "complex_computation", return_value=42)
    assert calculator.complex_computation(1, 2, 3) == 42

    # --- mocker.spy: 실제 동작을 유지하면서 호출 추적 ---
    spy = mocker.spy(calculator, "add")
    result = calculator.add(3, 4)
    assert result == 7          # 실제 결과 반환
    spy.assert_called_once_with(3, 4)  # 호출 추적도 가능


def test_side_effect(mocker):
    """side_effect로 동적 동작을 시뮬레이션한다."""
    mock_db = mocker.Mock()

    # 호출마다 다른 값 반환
    mock_db.query.side_effect = [
        [{"id": 1}],  # 첫 번째 호출
        [{"id": 2}],  # 두 번째 호출
        Exception("DB 연결 끊김"),  # 세 번째 호출에서 예외
    ]

    assert mock_db.query("SELECT 1") == [{"id": 1}]
    assert mock_db.query("SELECT 2") == [{"id": 2}]
    with pytest.raises(Exception, match="DB 연결 끊김"):
        mock_db.query("SELECT 3")
```

### 12.2 pytest 고급 fixture 패턴

```python
import pytest


# --- 팩토리 패턴 fixture ---
@pytest.fixture
def make_user():
    """팩토리 fixture: 다양한 변형의 User를 생성할 수 있다."""
    def _make_user(name="기본이름", age=25, is_active=True):
        return User(name=name, age=age, is_active=is_active)
    return _make_user


def test_inactive_user_cannot_login(make_user):
    user = make_user(name="비활성", is_active=False)
    assert user.can_login() is False


def test_active_user_can_login(make_user):
    user = make_user(name="활성", is_active=True)
    assert user.can_login() is True


# --- 매개변수화 fixture ---
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    """동일한 테스트를 여러 DB 백엔드로 실행한다."""
    db = create_database(request.param)
    yield db
    db.cleanup()


def test_insert_and_retrieve(database):
    """세 가지 DB 백엔드 모두에서 동일한 테스트가 실행된다."""
    database.insert({"id": 1, "name": "test"})
    result = database.get(1)
    assert result["name"] == "test"


# --- conftest.py를 활용한 계층적 fixture 공유 ---
# tests/conftest.py (최상위)
@pytest.fixture(scope="session")
def app():
    """세션 전체에서 한 번만 생성되는 앱 인스턴스."""
    return create_app(testing=True)


# tests/api/conftest.py (하위 디렉토리)
@pytest.fixture
def client(app):
    """상위 conftest의 app fixture를 활용한다."""
    return app.test_client()
```

### 12.3 pytest.mark.parametrize 심화

```python
import pytest


# --- 기본 매개변수화 ---
@pytest.mark.parametrize("input_val, expected", [
    (1, "1"),
    (100, "100"),
    (-5, "-5"),
    (0, "0"),
])
def test_int_to_string(input_val, expected):
    assert str(input_val) == expected


# --- pytest.param으로 ID와 마커 지정 ---
@pytest.mark.parametrize("email, is_valid", [
    pytest.param("user@example.com", True, id="valid-standard"),
    pytest.param("user+tag@example.com", True, id="valid-with-plus"),
    pytest.param("invalid", False, id="no-at-sign"),
    pytest.param("@no-local.com", False, id="no-local-part"),
    pytest.param(
        "a" * 255 + "@test.com", False,
        id="too-long",
        marks=pytest.mark.xfail(reason="길이 제한 미구현"),
    ),
])
def test_email_validation(email, is_valid):
    assert validate_email(email) == is_valid


# --- 여러 매개변수 조합 (데카르트 곱) ---
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [10, 20])
def test_addition_combinations(x, y):
    """4가지 조합 실행: (1,10), (1,20), (2,10), (2,20)"""
    assert add(x, y) == x + y
```

---

## 참고 문헌

| 출처 | 다룬 내용 |
|------|---------|
| Martin Fowler, "Mocks Aren't Stubs" (2007) | 상태 검증 vs 행위 검증, 고전 학파 vs 런던 학파, 테스트 더블 분류 |
| Steve Freeman & Nat Pryce, "Growing Object-Oriented Software, Guided by Tests" (2009) | 이중 루프 TDD, Walking Skeleton, Outside-In TDD, Mock Roles Not Objects, Tell Don't Ask |
| Gerard Meszaros, "xUnit Test Patterns" (2007) | 테스트 더블 5가지 분류, 테스트 냄새 카탈로그 (18종), 테스트 리팩토링 패턴 |
| Vladimir Khorikov, "Unit Testing Principles, Practices, and Patterns" (2020) | 좋은 테스트의 4대 기둥, 세 가지 테스트 스타일, 고전 학파 vs 런던 학파 비교 |
| Michael Feathers, "Working Effectively with Legacy Code" (2004) | 레거시 코드 정의, Seam 모델, 특성화 테스트, 의존성 깨뜨리기 기법 |
| Roy Osherove, "The Art of Unit Testing" 3rd ed. (2024) | 신뢰성/유지보수성/가독성 3대 속성, 테스트 명명 규칙, AAA 패턴 |
| Hypothesis 공식 문서 (hypothesis.readthedocs.io) | Property-Based Testing, 전략(Strategy), 축소(Shrinking) |
| mutmut 공식 문서 (mutmut.readthedocs.io) | Mutation Testing 개념, 뮤테이션 종류, 점수 해석 |
| pytest-bdd 공식 문서 (pytest-bdd.readthedocs.io) | BDD와 TDD의 관계, Given-When-Then, Gherkin 시나리오 |
| pytest-mock 공식 문서 (pytest-mock.readthedocs.io) | mocker fixture, patch, spy, side_effect |
| Thoughtworks, "TDD and Pair Programming: Perfect Companions for Copilot" (2024) | AI 보조 TDD, 페어 프로그래밍과 AI |
| Simon Willison, "Red/Green TDD - Agentic Engineering Patterns" (2025) | AI 시대의 Red-Green-Refactor, 테스트를 명세로 활용 |
| Awesome Testing, "Test-Driven AI Development (TDAID)" (2025) | TDAID 5단계 워크플로우 |
