# 값 객체와 엔티티

## 3.1 값 객체 (Value Object)

> 출처: [A][B][C], Evans 파란책, Cosmic Python

고유 식별자가 없으며, 개념적으로 완전한 하나를 표현한다. 불변(immutable)이어야 한다.

**핵심 원칙:**
- 식별자 없이 속성의 조합으로 동등성을 판단한다
- 반드시 불변이어야 한다 (setter 금지)
- 부작용과 동시성 문제가 없다
- [B] 값 객체가 유비쿼터스 언어 자체가 될 수 있다: `_countryCode: str` 대신 `_country: CountryCode`

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class Money:
    """Python 3.10+ Value Object 권장 패턴

    frozen=True: 불변 보장 + __hash__ 자동 생성
    slots=True:  메모리 효율 향상 (Python 3.10+)
    """
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        """자기 검증 (Self-Validation): 생성 시점에 불변식 강제"""
        if not isinstance(self.amount, int):
            object.__setattr__(self, "amount", int(self.amount))
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")
        if not self.currency:
            raise ValueError("통화 코드는 필수입니다")

    def add(self, other: "Money") -> "Money":
        """부작용 없는 함수: 기존 객체를 변경하지 않고 새 객체를 반환"""
        self._ensure_same_currency(other)
        return replace(self, amount=self.amount + other.amount)

    def subtract(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("결과 금액이 음수입니다")
        return replace(self, amount=result)

    def multiply(self, factor: int) -> "Money":
        return replace(self, amount=self.amount * factor)

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")


@dataclass(frozen=True)
class Address:
    """주소 값 객체 - 개념적으로 완전한 하나를 표현"""
    city: str
    street: str
    zipcode: str


@dataclass(frozen=True)
class PhoneNumber:
    """전화번호 값 객체 [B] - 유효성 검사 로직을 캡슐화"""
    number: str

    def __post_init__(self):
        import re
        if not re.match(r"^\d{2,3}-\d{3,4}-\d{4}$", self.number):
            raise ValueError(f"유효하지 않은 전화번호: {self.number}")
```

## 3.2 엔티티 (Entity)

> 출처: [A][B][C], Millett
> **[의사결정 #1] External 채택**: 엔티티는 애그리거트의 일부로만 사용한다.

고유 식별자를 가지며, 라이프사이클 동안 상태가 변한다. 값이 같아도 식별자가 다르면 다른 객체다.

엔티티를 애그리거트 없이 독립 사용하면 일관성 경계가 모호해진다. Millett는 빈혈 도메인 모델을 "가장 흔한 DDD 실패 사례"로 지적하며, 엔티티가 풍부한 도메인 모델의 구성 요소로서 행동과 불변식을 캡슐화해야 한다고 주장한다.

```python
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Member:
    """회원 엔티티 -- 애그리거트의 일부로서 사용"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    email: str = ""
    _password: str = field(default="", repr=False)

    def change_password(self, old_pw: str, new_pw: str) -> None:
        """도메인 규칙이 엔티티 안에 위치한다"""
        if not self.match_password(old_pw):
            raise ValueError("기존 비밀번호가 일치하지 않습니다")
        if not new_pw:
            raise ValueError("새 비밀번호가 비어있습니다")
        self._password = new_pw

    def match_password(self, password: str) -> bool:
        return self._password == password

    def __eq__(self, other):
        """엔티티의 동등성은 식별자로만 판단"""
        if not isinstance(other, Member):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
```

### 빈혈 도메인 모델 vs 풍부한 도메인 모델 (Millett)

```python
# === 빈혈 도메인 모델 (Anemic Domain Model) -- 안티패턴 (나쁜 예) ===
# Martin Fowler가 2003년에 안티패턴으로 명명
@dataclass
class OrderAnemic:
    """데이터만 있고 행동이 없는 빈혈 모델"""
    id: str
    customer_id: str
    items: list
    status: str
    total: int


class OrderServiceAnemic:
    """모든 비즈니스 로직이 서비스에 집중 -- 절차적 프로그래밍과 동일"""

    def place_order(self, order: OrderAnemic) -> None:
        if not order.items:
            raise ValueError("상품이 없습니다")
        order.total = sum(i["price"] * i["qty"] for i in order.items)
        order.status = "placed"


# === 풍부한 도메인 모델 (Rich Domain Model) -- DDD 지향 (좋은 예) ===
@dataclass
class OrderRich:
    """행동과 불변식을 캡슐화한 풍부한 도메인 모델"""
    id: str
    customer_id: str
    _items: list = field(default_factory=list)
    _status: OrderStatus = OrderStatus.PLACED
    _total: int = 0

    def __post_init__(self):
        if not self._items:
            raise ValueError("최소 한 개의 상품이 필요합니다")
        self._recalculate()

    def cancel(self) -> None:
        """비즈니스 규칙이 도메인 객체 안에 있다"""
        if self._status not in (OrderStatus.PLACED, OrderStatus.PREPARING):
            raise ValueError(f"{self._status.value} 상태에서는 취소할 수 없습니다")
        self._status = OrderStatus.CANCELLED

    def _recalculate(self) -> None:
        self._total = sum(i["price"] * i["qty"] for i in self._items)
```
