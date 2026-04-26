# Python 주문 도메인 Value Object 구현

## 개요

DDD(Domain-Driven Design)에서 Value Object는 다음 특성을 가집니다:

- **불변성(Immutability)**: 생성 후 상태 변경 불가
- **동등성(Equality)**: 속성 값이 같으면 같은 객체로 취급
- **자기 유효성 검증(Self-Validation)**: 생성 시점에 유효성을 보장

Python의 `frozen dataclass`를 사용하면 이 특성들을 자연스럽게 구현할 수 있습니다.

## 전체 코드

```python
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from typing import Optional


# ============================================================
# Currency Enum
# ============================================================

class Currency(str, Enum):
    """지원 통화 목록."""
    KRW = "KRW"
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"


# ============================================================
# Money Value Object
# ============================================================

@dataclass(frozen=True, slots=True)
class Money:
    """
    금액을 나타내는 Value Object.

    - 불변(frozen) 객체로, 생성 후 금액/통화 변경 불가
    - Decimal을 사용하여 부동소수점 오류 방지
    - 동일 통화끼리만 연산 가능
    """

    amount: Decimal
    currency: Currency = Currency.KRW

    def __post_init__(self) -> None:
        # frozen이므로 object.__setattr__를 사용하여 정규화
        if not isinstance(self.amount, Decimal):
            try:
                object.__setattr__(self, "amount", Decimal(str(self.amount)))
            except (InvalidOperation, TypeError, ValueError) as e:
                raise ValueError(f"유효하지 않은 금액입니다: {self.amount!r}") from e

        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

        if not isinstance(self.currency, Currency):
            raise TypeError(f"유효하지 않은 통화입니다: {self.currency!r}")

    # --- 동등성 / 해시 ---

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    # --- 산술 연산 ---

    def _check_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"통화가 다릅니다: {self.currency.value} != {other.currency.value}"
            )

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_same_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("금액 계산 결과가 음수입니다.")
        return Money(amount=result, currency=self.currency)

    def __mul__(self, multiplier: int | float | Decimal) -> Money:
        if isinstance(multiplier, (int, float, Decimal)):
            result = self.amount * Decimal(str(multiplier))
            if result < 0:
                raise ValueError("금액 계산 결과가 음수입니다.")
            return Money(
                amount=result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                currency=self.currency,
            )
        return NotImplemented

    # --- 비교 연산 ---

    def __lt__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_same_currency(other)
        return self.amount >= other.amount

    # --- 유틸리티 ---

    @staticmethod
    def zero(currency: Currency = Currency.KRW) -> Money:
        """0원 Money 객체를 반환합니다."""
        return Money(amount=Decimal("0"), currency=currency)

    @staticmethod
    def won(amount: int | float | Decimal) -> Money:
        """KRW 통화의 Money를 간편 생성합니다."""
        return Money(amount=Decimal(str(amount)), currency=Currency.KRW)

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency='{self.currency.value}')"

    def __str__(self) -> str:
        if self.currency == Currency.KRW:
            return f"{self.amount:,.0f}원"
        elif self.currency == Currency.USD:
            return f"${self.amount:,.2f}"
        elif self.currency == Currency.EUR:
            return f"\u20ac{self.amount:,.2f}"
        elif self.currency == Currency.JPY:
            return f"\u00a5{self.amount:,.0f}"
        return f"{self.amount} {self.currency.value}"


# ============================================================
# Address Value Object
# ============================================================

@dataclass(frozen=True, slots=True)
class Address:
    """
    배송 주소를 나타내는 Value Object.

    - 불변(frozen) 객체로, 생성 후 주소 변경 불가
    - 모든 필수 필드 유효성 검증 포함
    """

    city: str
    district: str
    street: str
    detail: str
    zip_code: str
    recipient_name: str
    phone: str
    country: str = "KR"
    extra_note: Optional[str] = None

    def __post_init__(self) -> None:
        # 필수 필드 공백 검증
        required_fields = {
            "city": self.city,
            "district": self.district,
            "street": self.street,
            "detail": self.detail,
            "zip_code": self.zip_code,
            "recipient_name": self.recipient_name,
            "phone": self.phone,
        }
        for name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"'{name}'은(는) 비어 있을 수 없습니다.")

        # 공백 제거된 값으로 재설정 (frozen이므로 object.__setattr__ 사용)
        for name, value in required_fields.items():
            object.__setattr__(self, name, value.strip())

        # 우편번호 형식 검증 (한국: 5자리 숫자)
        if self.country == "KR" and (
            len(self.zip_code) != 5 or not self.zip_code.isdigit()
        ):
            raise ValueError(
                f"한국 우편번호는 5자리 숫자여야 합니다: '{self.zip_code}'"
            )

    # --- 동등성 / 해시 ---

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Address):
            return NotImplemented
        return (
            self.city == other.city
            and self.district == other.district
            and self.street == other.street
            and self.detail == other.detail
            and self.zip_code == other.zip_code
            and self.recipient_name == other.recipient_name
            and self.phone == other.phone
            and self.country == other.country
        )

    def __hash__(self) -> int:
        return hash((
            self.city,
            self.district,
            self.street,
            self.detail,
            self.zip_code,
            self.recipient_name,
            self.phone,
            self.country,
        ))

    # --- 유틸리티 ---

    @property
    def full_address(self) -> str:
        """전체 주소 문자열을 반환합니다."""
        base = f"({self.zip_code}) {self.city} {self.district} {self.street} {self.detail}"
        if self.extra_note:
            base += f" ({self.extra_note})"
        return base

    @property
    def shipping_label(self) -> str:
        """배송 라벨용 문자열을 반환합니다."""
        return (
            f"[{self.recipient_name}] {self.phone}\n"
            f"{self.full_address}"
        )

    def with_detail(self, new_detail: str) -> Address:
        """상세주소만 변경한 새 Address를 반환합니다 (불변성 유지)."""
        return Address(
            city=self.city,
            district=self.district,
            street=self.street,
            detail=new_detail,
            zip_code=self.zip_code,
            recipient_name=self.recipient_name,
            phone=self.phone,
            country=self.country,
            extra_note=self.extra_note,
        )

    def with_recipient(self, name: str, phone: str) -> Address:
        """수령인 정보만 변경한 새 Address를 반환합니다 (불변성 유지)."""
        return Address(
            city=self.city,
            district=self.district,
            street=self.street,
            detail=self.detail,
            zip_code=self.zip_code,
            recipient_name=name,
            phone=phone,
            country=self.country,
            extra_note=self.extra_note,
        )

    def __repr__(self) -> str:
        return (
            f"Address(city='{self.city}', district='{self.district}', "
            f"street='{self.street}', zip_code='{self.zip_code}')"
        )

    def __str__(self) -> str:
        return self.full_address


# ============================================================
# 사용 예시
# ============================================================

if __name__ == "__main__":
    # --- Money 사용 ---
    price = Money.won(15000)
    shipping_fee = Money(amount=Decimal("3000"), currency=Currency.KRW)

    total = price + shipping_fee
    print(f"상품가: {price}")          # 15,000원
    print(f"배송비: {shipping_fee}")    # 3,000원
    print(f"합계:   {total}")          # 18,000원

    # 수량 곱셈
    triple = price * 3
    print(f"3개:    {triple}")         # 45,000원

    # 비교
    print(f"price > shipping_fee: {price > shipping_fee}")  # True

    # 동등성 확인
    same_price = Money.won(15000)
    print(f"price == same_price: {price == same_price}")    # True

    # set/dict에서 활용 (해시 가능)
    price_set = {price, same_price, shipping_fee}
    print(f"set 크기: {len(price_set)}")  # 2 (price와 same_price는 같음)

    # USD
    usd = Money(amount=Decimal("29.99"), currency=Currency.USD)
    print(f"USD: {usd}")  # $29.99

    print()

    # --- Address 사용 ---
    addr = Address(
        city="서울특별시",
        district="강남구",
        street="테헤란로 123",
        detail="OO빌딩 5층",
        zip_code="06234",
        recipient_name="홍길동",
        phone="010-1234-5678",
        extra_note="정문 출입",
    )
    print(f"전체 주소: {addr}")
    print(f"배송 라벨:\n{addr.shipping_label}")

    # 불변성 확인: 아래 코드는 FrozenInstanceError 발생
    # addr.city = "부산광역시"

    # with_ 패턴으로 새 객체 생성
    new_addr = addr.with_recipient("김철수", "010-9999-0000")
    print(f"\n수령인 변경: {new_addr.shipping_label}")

    # 동등성 확인
    addr2 = Address(
        city="서울특별시",
        district="강남구",
        street="테헤란로 123",
        detail="OO빌딩 5층",
        zip_code="06234",
        recipient_name="홍길동",
        phone="010-1234-5678",
        extra_note="정문 출입",
    )
    print(f"\naddr == addr2: {addr == addr2}")  # True
    print(f"hash 동일: {hash(addr) == hash(addr2)}")  # True
```

## 설계 포인트 정리

| 항목 | 구현 방식 |
|------|-----------|
| **불변성** | `@dataclass(frozen=True)` - 필드 재할당 시 `FrozenInstanceError` 발생 |
| **메모리 효율** | `slots=True` - `__dict__` 제거, 메모리 절약 및 속성 접근 속도 향상 |
| **동등성** | `__eq__` 명시 구현 - 모든 필드 값 비교 |
| **해시** | `__hash__` 명시 구현 - `set`, `dict` 키로 사용 가능 |
| **자기 검증** | `__post_init__`에서 생성 시점 유효성 검사 |
| **부동소수점 안전** | `Decimal` 사용 - 금융 계산의 정밀도 보장 |
| **통화 안전** | 다른 통화끼리 연산 시 `ValueError` 발생 |
| **값 변경 패턴** | `with_*` 메서드로 일부 필드만 변경한 새 객체 반환 |
| **타입 힌트** | `from __future__ import annotations`로 전방 참조 지원 |
