# 테스트 더블과 검증 방식 레퍼런스

테스트 더블 분류 체계와 검증 방식 우선순위에 대한 상세 규칙과 예시.

---

## 1. Meszaros의 5분류

테스트 의도를 명확히 전달하고, Mock과 Stub의 혼용을 방지하기 위해 세밀한 분류가 필요하다. [Unit Testing - Khorikov]

| 종류 | 역할 | 예시 |
|------|------|------|
| **Dummy** | 빈 값 전달용. 호출되지 않는다 | 생성자에 넣는 `None` |
| **Stub** | 미리 정해진 값을 반환한다 | `mock.return_value = 25.0` |
| **Spy** | 호출 기록을 남겨 나중에 검증한다 | `assert_called_once_with(...)` |
| **Mock** | 호출 자체를 검증한다 (통신 기반 테스트) | `mock.assert_called_with("서울")` |
| **Fake** | 간소화된 실제 구현을 제공한다 | 메모리 내 데이터베이스, FakeRepository |

> 출처: Unit Testing Principles, Practices, and Patterns - Vladimir Khorikov

---

## 2. 검증 방식 우선순위

Mock 사용 범위에 대한 올바른 접근: 의존성 주입으로 테스트 용이성을 확보하되, **과도한 Mock은 안티패턴**("Mockery")이다. 검증 방식은 다음 우선순위를 따른다.

| 우선순위 | 검증 방식 | 설명 | 예시 |
|----------|-----------|------|------|
| 1 | **출력 기반** | 함수의 반환값을 검증 | `assert calculate(2, 3) == 5` |
| 2 | **상태 기반** | 행위 후 객체 상태를 검증 | `cart.add(item); assert cart.total == 100` |
| 3 | **통신 기반** | 외부 호출 여부를 검증 (Mock) | `mock_email.send.assert_called_once()` |

**원칙**: 외부 의존성(결제 게이트웨이, 이메일 등)만 Mock하고, 핵심 비즈니스 로직은 실제 객체로 테스트한다.

---

## 3. 의존 관계 캡슐화로 모킹을 쉽게 만들기

테스트 코드를 처음 보고 이해하기 어렵다면, 더 나은 추상화를 사용하여 목이나 테스트를 더 쉽게 작성할 수 있다.

```python
# 나쁨: 의존 관계가 흩어져 있어 모킹이 복잡하다
def process_order(order_id):
    db = get_database()
    order = db.query(f"SELECT * FROM orders WHERE id={order_id}")
    email_service = get_email_service()
    email_service.send(order.customer_email, "주문 완료")


# 좋음: 의존 관계를 주입받아 모킹이 쉽다
from unittest.mock import Mock

class OrderProcessor:
    def __init__(self, db, email_service):
        self.db = db
        self.email_service = email_service

    def process(self, order_id):
        order = self.db.get_order(order_id)
        self.email_service.send(order.customer_email, "주문 완료")


def test_process_order():
    mock_db = Mock()
    mock_db.get_order.return_value = Order(email="test@test.com")
    mock_email = Mock()

    processor = OrderProcessor(mock_db, mock_email)
    processor.process(1)

    mock_email.send.assert_called_once_with("test@test.com", "주문 완료")
```

> 단, 모든 의존성을 Mock으로 대체하면 "실제로 뭘 테스트하는 건지" 의문이 된다. 외부 의존성(이메일, 결제 등)만 Mock하고, 핵심 로직은 실제로 실행해야 한다.

> 출처: [Unit Testing Principles, Practices, and Patterns - Vladimir Khorikov](https://www.manning.com/books/unit-testing)
