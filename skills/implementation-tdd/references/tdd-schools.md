# TDD 학파 비교 레퍼런스

고전 학파와 런던 학파의 핵심 차이, 상태 검증 vs 행위 검증, Inside-Out vs Outside-In TDD, 실전 권고를 정리한다.

---

## 두 학파의 기원과 핵심 차이

> 출처: Martin Fowler, *Mocks Aren't Stubs*

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

---

## 상태 검증 vs 행위 검증

> 출처: Martin Fowler, *Mocks Aren't Stubs*

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

---

## Inside-Out vs Outside-In TDD

두 접근법은 배타적이지 않다. 실전에서는 상황에 따라 혼합하는 것이 효과적이다.

### Inside-Out TDD (고전 학파)

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

### Outside-In TDD (런던 학파)

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

---

## 실전 권고: 상황별 선택

| 상황 | 권장 접근법 |
|------|-----------|
| 순수 도메인 로직 | 고전 학파 (실제 객체, 상태 검증) |
| 외부 시스템 연동 (DB, API) | 런던 학파 (Mock, 행위 검증) |
| 새로운 기능의 전체 설계 탐색 | Outside-In (런던 학파) |
| 복잡한 알고리즘 구현 | Inside-Out (고전 학파) |
