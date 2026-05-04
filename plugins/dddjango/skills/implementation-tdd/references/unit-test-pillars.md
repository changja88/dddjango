# 좋은 단위 테스트의 4대 특성 레퍼런스

Khorikov의 4가지 기둥, CAP 유사성과 트레이드오프, 3가지 테스트 스타일, Osherove의 3대 속성을 정리한다.

---

## 네 가지 기둥 (Four Pillars)

> 출처: Vladimir Khorikov, *Unit Testing: Principles, Practices, and Patterns*

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

---

## 회귀 방지의 위상

> 출처: Vladimir Khorikov, *Unit Testing: Principles, Practices, and Patterns*

회귀 방지(Protection against Regressions)는 단순히 버그 발견 시 사후에 작성하는 회귀 테스트를 넘어, **모든 테스트가 처음부터 갖춰야 할 설계 원칙**이다. 테스트 설계 시점부터 "이 테스트가 향후 회귀를 얼마나 잘 방지하는가"를 고려해야 한다.

실전 적용: 시스템 장애가 보고될 때에도 가장 먼저 할 일은 그 장애로 인하여 실패하는 테스트, 그리고 통과할 경우엔 장애가 수정되었다고 볼 수 있는 테스트를 작성하는 것이다. [테스트주도 개발]

```python
def test_division_by_zero_returns_error():
    """버그 리포트 #42: 0으로 나눌 때 ZeroDivisionError 대신 None 반환됨"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

---

## 리팩토링 내성

> 출처: Vladimir Khorikov, *Unit Testing: Principles, Practices, and Patterns*

리팩토링 내성(Resistance to Refactoring)은 독립적 품질 기둥이다. 거짓 양성(false positive) 빈도로 측정하며, Mock 과용이 구현에 결합된 테스트를 만들어 "내부 구현을 바꿀 때마다 테스트가 깨지는" 문제를 야기한다.

---

## CAP 정리와의 유사성

> 출처: Vladimir Khorikov, *Unit Testing: Principles, Practices, and Patterns*

Khorikov의 핵심 통찰: 처음 세 기둥(회귀 방지, 리팩토링 내성, 빠른 피드백)은 **상호 배타적**이다. 세 가지를 동시에 최대화할 수 없다.

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

---

## 세 가지 테스트 스타일

> 출처: Vladimir Khorikov, *Unit Testing: Principles, Practices, and Patterns*

| 스타일 | 검증 대상 | 회귀 방지 | 리팩토링 내성 | 유지보수성 |
|--------|----------|:---------:|:-----------:|:---------:|
| **출력 기반** (Output-based) | 반환값 | 높음 | 높음 | 높음 |
| **상태 기반** (State-based) | 객체 상태 | 높음 | 높음 | 중간 |
| **통신 기반** (Communication-based) | 메서드 호출 | 중간 | 낮음 | 낮음 |

Khorikov의 권고: **출력 기반 > 상태 기반 > 통신 기반** 순으로 선호하라. 가능하면 비즈니스 로직을 순수 함수로 추출하여 출력 기반 테스트를 극대화하라.

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

---

## 테스트 품질 3대 속성

> 출처: Roy Osherove, *The Art of Unit Testing*

| 속성 | 의미 | 위반 징후 |
|------|------|----------|
| **신뢰성** (Trustworthiness) | 테스트 결과를 믿을 수 있다 | 테스트가 실패해도 무시하게 됨 |
| **유지보수성** (Maintainability) | 코드 변경 시 테스트 수정이 적다 | 사소한 변경에도 테스트가 대량으로 깨짐 |
| **가독성** (Readability) | 테스트 의도를 빠르게 파악할 수 있다 | 테스트 코드를 읽는 데 원본보다 오래 걸림 |
