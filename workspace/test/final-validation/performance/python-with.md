```python
"""주문 도메인 Value Object 모듈.

Money(금액)와 Address(주소)를 불변 값 객체로 정의한다.
frozen dataclass로 구현하여 동등성 비교와 해시 기반 컬렉션 사용을 보장한다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Money:
    """통화가 지정된 금액을 나타내는 값 객체.

    불변이며 dict 키나 set 원소로 사용할 수 있다.
    동일 통화 간 산술 연산을 지원한다.
    """

    amount: int
    currency: str

    def add(self, other: Money, /) -> Money:
        """동일 통화의 두 금액을 더한다.

        Raises:
            ValueError: 통화가 일치하지 않을 때.
        """
        if self.currency != other.currency:
            raise ValueError(
                f"통화 불일치: {self.currency!r} != {other.currency!r}"
            )
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: Money, /) -> Money:
        """동일 통화의 금액을 뺀다.

        Raises:
            ValueError: 통화가 일치하지 않을 때.
        """
        if self.currency != other.currency:
            raise ValueError(
                f"통화 불일치: {self.currency!r} != {other.currency!r}"
            )
        return Money(self.amount - other.amount, self.currency)

    def multiply(self, factor: int, /) -> Money:
        """금액에 정수 배율을 곱한다."""
        return Money(self.amount * factor, self.currency)

    def is_positive(self) -> bool:
        """금액이 양수인지 확인한다."""
        return self.amount > 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __repr__(self) -> str:
        return f"Money(amount={self.amount!r}, currency={self.currency!r})"

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"


@dataclass(frozen=True, slots=True)
class Address:
    """배송 주소를 나타내는 값 객체.

    모든 필드가 불변이며, 동일 주소 비교와 해시를 지원한다.
    """

    city: str
    street: str
    zipcode: str
    detail: str = ""

    def full_address(self) -> str:
        """사람이 읽을 수 있는 전체 주소 문자열을 반환한다."""
        base = f"{self.city} {self.street} {self.zipcode}"
        if self.detail:
            return f"{base} ({self.detail})"
        return base

    def with_detail(self, detail: str, /) -> Address:
        """상세 주소만 변경한 새 Address를 반환한다."""
        return Address(
            city=self.city,
            street=self.street,
            zipcode=self.zipcode,
            detail=detail,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Address):
            return NotImplemented
        return (
            self.city == other.city
            and self.street == other.street
            and self.zipcode == other.zipcode
            and self.detail == other.detail
        )

    def __hash__(self) -> int:
        return hash((self.city, self.street, self.zipcode, self.detail))

    def __repr__(self) -> str:
        return (
            f"Address(city={self.city!r}, street={self.street!r}, "
            f"zipcode={self.zipcode!r}, detail={self.detail!r})"
        )

    def __str__(self) -> str:
        return self.full_address()
```

`frozen=True`는 `__eq__`와 `__hash__`를 자동 생성하므로 명시적 구현 없이도 동작한다.
위 코드에서 명시적으로 정의한 이유는 세 가지다.

1. **`__eq__`에서 `NotImplemented` 반환** -- `frozen=True`의 자동 생성 `__eq__`는
   다른 타입과 비교 시 `False`를 반환한다. 명시적 구현은 `NotImplemented`를
   반환하여 Python이 상대 객체의 `__eq__`를 시도할 수 있게 한다.

2. **`__hash__` 투명성** -- 해시에 어떤 필드가 포함되는지 코드에서 바로 보인다.
   `frozen=True`의 자동 해시는 모든 필드를 포함하므로 동작은 동일하지만,
   도메인 객체에서는 명시적 선언이 의도를 드러낸다.

3. **`__repr__` 커스터마이징** -- `dataclass`의 자동 `__repr__`도 충분하지만,
   `__str__`을 별도로 정의하여 사용자 출력(`print`)과 디버그 출력(`repr`)을
   구분했다.

사용 예시:

```python
price = Money(amount=15000, currency="KRW")
discounted = Money(amount=3000, currency="KRW")
total = price.subtract(discounted)
# Money(amount=12000, currency='KRW')

addr = Address(city="서울", street="강남대로 123", zipcode="06100")
addr_with_detail = addr.with_detail("5층 501호")
# Address(city='서울', street='강남대로 123', zipcode='06100', detail='5층 501호')

# set/dict 키로 사용 가능 (frozen + __hash__)
unique_addresses: set[Address] = {addr, addr_with_detail}
price_map: dict[Money, str] = {price: "기본가", total: "할인가"}
```

---
> **관련 스킬 참조:**
> - 도메인 엔티티, 애그리게이트 설계 시 클린코드 원칙 적용 -> **implementation-cleancode** 스킬
> - 외부 API 입력 검증이 필요한 경우 pydantic v2 모델링 -> **implementation-python** 스킬 (데이터 모델링 섹션)
> - Value Object 단위 테스트 작성 -> **testing** 스킬
