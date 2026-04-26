# Python 클린 코드 리팩터링

## 원본 코드의 문제점 분석

```python
def process_order(order_data, db, mailer, logger):
    if order_data['type'] == 'standard':
        total = 0
        for item in order_data['items']:
            if item['quantity'] > 0:
                price = item['price'] * item['quantity']
                if item.get('discount'):
                    price = price * (1 - item['discount'] / 100)
                total += price
        if total > 100000:
            order_data['shipping'] = 0
        else:
            order_data['shipping'] = 3000
        order_data['total'] = total + order_data['shipping']
        db.save(order_data)
        mailer.send(order_data['email'], f'주문 완료: {order_data["total"]}원')
        logger.info(f'Order processed: {order_data["total"]}')
        return order_data
    elif order_data['type'] == 'subscription':
        # similar but different logic...
        pass
```

### 식별된 문제점

| # | 문제 | 위반 원칙 |
|---|------|-----------|
| 1 | 하나의 함수가 가격 계산, 배송비 결정, DB 저장, 메일 발송, 로깅을 모두 수행 | **SRP (단일 책임 원칙)** |
| 2 | `order_data` dict를 직접 변경(mutate)하여 부수 효과 추적이 어려움 | **부수 효과 최소화** |
| 3 | `100000`, `3000`, `100` 같은 숫자가 코드에 직접 등장 | **매직 넘버 제거** |
| 4 | `if/elif` 분기로 주문 유형을 처리하여 유형 추가 시 함수 수정 필요 | **OCP (개방-폐쇄 원칙)** |
| 5 | 비즈니스 로직과 인프라(DB, 메일) 코드가 혼재 | **관심사 분리** |
| 6 | dict 기반 데이터 구조로 키 오타 시 런타임 에러 발생 | **타입 안전성** |
| 7 | 중첩 깊이가 3단계 이상으로 가독성 저하 | **들여쓰기 깊이 제한** |

---

## 리팩터링 결과

### 1단계: 데이터 모델 정의 -- dict를 dataclass로 교체

dict 기반 구조는 키 이름 오타를 컴파일 타임에 잡을 수 없고, 어떤 필드가 존재하는지 코드를 읽어야만 알 수 있다. `dataclass`로 명시적 스키마를 만들면 IDE 자동완성과 타입 체커의 도움을 받을 수 있다.

```python
from dataclasses import dataclass, field


@dataclass
class OrderItem:
    price: int
    quantity: int
    discount: float = 0.0  # 퍼센트 단위 (0~100)

    @property
    def subtotal(self) -> int:
        """할인이 적용된 개별 아이템 소계를 반환한다."""
        if self.quantity <= 0:
            return 0
        base = self.price * self.quantity
        if self.discount:
            base = int(base * (1 - self.discount / 100))
        return base


@dataclass
class Order:
    type: str
    email: str
    items: list[OrderItem] = field(default_factory=list)
    shipping: int = 0
    total: int = 0
```

**변경 이유:**
- `item['price']` 같은 문자열 키 접근을 `item.price` 속성 접근으로 바꿔 오타 방지
- `subtotal` 계산을 `OrderItem`이 스스로 책임지게 하여 SRP 준수
- 할인 적용 로직이 아이템 내부에 캡슐화되어 외부에서 중복 구현할 필요 없음

---

### 2단계: 상수 추출 -- 매직 넘버 제거

코드 중간에 박힌 숫자는 의미를 전달하지 못한다. 이름이 붙은 상수로 추출하면 "왜 100000인가?"라는 질문에 변수 이름 자체가 답을 준다.

```python
# 배송비 정책 상수
FREE_SHIPPING_THRESHOLD = 100_000  # 이 금액 이상이면 무료 배송
DEFAULT_SHIPPING_FEE = 3_000
```

**변경 이유:**
- `100000`이 무료 배송 기준이라는 사실을 변수 이름이 설명
- 정책 변경 시 상수 하나만 수정하면 됨 (산탄총 수술 방지)
- `100_000` 리터럴로 자릿수 가독성 향상

---

### 3단계: 순수 함수로 비즈니스 로직 분리

가격 계산과 배송비 결정은 외부 시스템(DB, 메일)에 의존하지 않는 순수한 비즈니스 규칙이다. 이를 독립 함수로 추출하면 단위 테스트가 쉬워지고 재사용할 수 있다.

```python
def calculate_item_total(items: list[OrderItem]) -> int:
    """모든 아이템의 소계를 합산한다."""
    return sum(item.subtotal for item in items)


def determine_shipping_fee(item_total: int) -> int:
    """상품 합계에 따른 배송비를 결정한다."""
    if item_total >= FREE_SHIPPING_THRESHOLD:
        return 0
    return DEFAULT_SHIPPING_FEE
```

**변경 이유:**
- 입력 -> 출력만 존재하는 순수 함수로, DB나 네트워크 없이 테스트 가능
- `calculate_item_total`은 아이템 목록만, `determine_shipping_fee`는 금액만 알면 동작
- 함수 이름이 곧 문서: "아이템 합계를 계산한다", "배송비를 결정한다"

---

### 4단계: 전략 패턴으로 주문 유형 확장 -- OCP 준수

`if/elif`로 주문 유형을 분기하면 새 유형 추가 시 기존 함수를 수정해야 한다. 전략 패턴을 적용하면 새로운 주문 유형을 기존 코드 변경 없이 추가할 수 있다.

```python
from abc import ABC, abstractmethod


class OrderProcessor(ABC):
    """주문 처리 전략의 추상 인터페이스."""

    @abstractmethod
    def calculate(self, order: Order) -> Order:
        """주문 금액을 계산하여 Order를 반환한다."""
        ...


class StandardOrderProcessor(OrderProcessor):
    """일반 주문 처리: 아이템 합산 + 배송비."""

    def calculate(self, order: Order) -> Order:
        item_total = calculate_item_total(order.items)
        shipping = determine_shipping_fee(item_total)

        order.shipping = shipping
        order.total = item_total + shipping
        return order


class SubscriptionOrderProcessor(OrderProcessor):
    """구독 주문 처리: 구독 전용 로직."""

    def calculate(self, order: Order) -> Order:
        # 구독 전용 계산 로직 구현
        item_total = calculate_item_total(order.items)
        order.shipping = 0  # 구독은 배송비 무료
        order.total = item_total
        return order
```

**변경 이유:**
- 새 주문 유형(예: `wholesale`) 추가 시 새 클래스만 만들면 됨 (OCP)
- 각 전략이 자신의 계산 로직만 책임 (SRP)
- `if/elif` 체인 제거로 코드 복잡도 감소

---

### 5단계: 레지스트리로 전략 선택 자동화

전략 패턴의 클래스가 많아지면 선택 로직도 깔끔하게 관리해야 한다. dict 기반 레지스트리로 유형 문자열과 전략을 매핑한다.

```python
ORDER_PROCESSORS: dict[str, OrderProcessor] = {
    "standard": StandardOrderProcessor(),
    "subscription": SubscriptionOrderProcessor(),
}


def get_processor(order_type: str) -> OrderProcessor:
    """주문 유형에 맞는 프로세서를 반환한다."""
    processor = ORDER_PROCESSORS.get(order_type)
    if processor is None:
        raise ValueError(f"지원하지 않는 주문 유형: {order_type}")
    return processor
```

**변경 이유:**
- 유형 추가 시 dict에 한 줄만 등록하면 끝
- 잘못된 유형이 들어오면 명확한 에러 메시지로 빠르게 실패 (Fail Fast)

---

### 6단계: 오케스트레이터 함수 -- 조립만 담당

최종 `process_order` 함수는 더 이상 비즈니스 로직을 직접 수행하지 않는다. 각 단계를 올바른 순서로 호출하는 조율자(orchestrator) 역할만 한다.

```python
def process_order(
    order: Order,
    db,
    mailer,
    logger,
) -> Order:
    """주문을 처리하고 저장, 알림, 로깅을 수행한다."""
    processor = get_processor(order.type)
    processed = processor.calculate(order)

    db.save(processed)
    mailer.send(processed.email, f"주문 완료: {processed.total}원")
    logger.info(f"Order processed: {processed.total}")

    return processed
```

**변경 이유:**
- 함수 본문이 4줄로 축약되어 전체 흐름을 한눈에 파악 가능
- 계산, 저장, 알림이 명확히 분리되어 각각 독립적으로 테스트/교체 가능
- 주문 유형별 분기가 함수 내부에서 완전히 사라짐

---

## 전체 리팩터링 코드

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# ──────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────
FREE_SHIPPING_THRESHOLD = 100_000
DEFAULT_SHIPPING_FEE = 3_000


# ──────────────────────────────────────────────
# 데이터 모델
# ──────────────────────────────────────────────
@dataclass
class OrderItem:
    price: int
    quantity: int
    discount: float = 0.0

    @property
    def subtotal(self) -> int:
        if self.quantity <= 0:
            return 0
        base = self.price * self.quantity
        if self.discount:
            base = int(base * (1 - self.discount / 100))
        return base


@dataclass
class Order:
    type: str
    email: str
    items: list[OrderItem] = field(default_factory=list)
    shipping: int = 0
    total: int = 0


# ──────────────────────────────────────────────
# 순수 비즈니스 로직
# ──────────────────────────────────────────────
def calculate_item_total(items: list[OrderItem]) -> int:
    return sum(item.subtotal for item in items)


def determine_shipping_fee(item_total: int) -> int:
    if item_total >= FREE_SHIPPING_THRESHOLD:
        return 0
    return DEFAULT_SHIPPING_FEE


# ──────────────────────────────────────────────
# 전략 패턴
# ──────────────────────────────────────────────
class OrderProcessor(ABC):
    @abstractmethod
    def calculate(self, order: Order) -> Order: ...


class StandardOrderProcessor(OrderProcessor):
    def calculate(self, order: Order) -> Order:
        item_total = calculate_item_total(order.items)
        shipping = determine_shipping_fee(item_total)
        order.shipping = shipping
        order.total = item_total + shipping
        return order


class SubscriptionOrderProcessor(OrderProcessor):
    def calculate(self, order: Order) -> Order:
        item_total = calculate_item_total(order.items)
        order.shipping = 0
        order.total = item_total
        return order


ORDER_PROCESSORS: dict[str, OrderProcessor] = {
    "standard": StandardOrderProcessor(),
    "subscription": SubscriptionOrderProcessor(),
}


def get_processor(order_type: str) -> OrderProcessor:
    processor = ORDER_PROCESSORS.get(order_type)
    if processor is None:
        raise ValueError(f"지원하지 않는 주문 유형: {order_type}")
    return processor


# ──────────────────────────────────────────────
# 오케스트레이터
# ──────────────────────────────────────────────
def process_order(order: Order, db, mailer, logger) -> Order:
    processor = get_processor(order.type)
    processed = processor.calculate(order)

    db.save(processed)
    mailer.send(processed.email, f"주문 완료: {processed.total}원")
    logger.info(f"Order processed: {processed.total}")

    return processed
```

---

## 테스트 용이성 비교

### 원본: 테스트하려면 DB, 메일, 로거를 모두 목(mock)해야 함

```python
# 원본 - 가격 계산만 테스트하고 싶어도 전체 인프라 목 필요
def test_total_calculation():
    mock_db = Mock()
    mock_mailer = Mock()
    mock_logger = Mock()
    order_data = {
        'type': 'standard',
        'email': 'test@test.com',
        'items': [{'price': 10000, 'quantity': 2, 'discount': 10}],
    }
    result = process_order(order_data, mock_db, mock_mailer, mock_logger)
    assert result['total'] == 21000  # 가격 검증에 3개의 목이 필요
```

### 리팩터링 후: 순수 함수를 독립 테스트

```python
# 리팩터링 후 - 목 없이 순수 로직만 테스트
def test_item_subtotal_with_discount():
    item = OrderItem(price=10000, quantity=2, discount=10)
    assert item.subtotal == 18000

def test_free_shipping_over_threshold():
    assert determine_shipping_fee(150_000) == 0

def test_standard_shipping_under_threshold():
    assert determine_shipping_fee(50_000) == 3_000

def test_standard_order_total():
    order = Order(
        type="standard",
        email="test@test.com",
        items=[OrderItem(price=10000, quantity=2, discount=10)],
    )
    processor = StandardOrderProcessor()
    result = processor.calculate(order)
    assert result.total == 21_000  # 18000 + 3000 배송비
```

---

## 적용된 클린 코드 원칙 요약

| 원칙 | 원본 | 리팩터링 |
|------|------|----------|
| **SRP** | 하나의 함수에 5가지 책임 | 함수/클래스별 단일 책임 |
| **OCP** | `if/elif`로 유형 분기 | 전략 패턴으로 확장 가능 |
| **매직 넘버** | `100000`, `3000` 하드코딩 | 이름 있는 상수로 추출 |
| **타입 안전성** | dict 키 기반 접근 | dataclass 속성 접근 |
| **테스트 용이성** | 항상 목 3개 필요 | 순수 함수 독립 테스트 가능 |
| **함수 크기** | 20줄 이상 단일 함수 | 최대 5줄 이내 함수들 |
| **들여쓰기 깊이** | 최대 4단계 중첩 | 최대 2단계 |
