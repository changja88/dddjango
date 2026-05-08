# DDD(도메인 주도 설계) 종합 가이드

> 출처: [A] 도메인 주도 개발 시작하기, [B] 도메인 주도 설계 첫걸음, [C] 도메인 주도 설계 구현(빨간책)

---

## 1. DDD란 무엇인가

DDD(Domain-Driven Design)는 복잡한 소프트웨어를 비즈니스 도메인 중심으로 설계하는 방법론이다. 소프트웨어의 핵심은 비즈니스 도메인이며, 도메인 전문가와 개발자가 공통 언어를 사용하여 모델을 구축하고 이를 코드로 구현한다.

### 3권의 관점 차이

| 관점 | [A] 도메인 주도 개발 시작하기 | [B] 도메인 주도 설계 첫걸음 | [C] 도메인 주도 설계 구현(빨간책) |
|------|--------------------------|--------------------------|-------------------------------|
| 초점 | 전술 패턴 중심의 실무 구현 | 전략 패턴 중심의 비즈니스 분석 | 전략+전술을 아키텍처와 함께 종합 |
| 대상 | DDD 입문자 | 비즈니스 설계자/아키텍트 | 실무 구현 개발자 |
| 강조점 | 계층 아키텍처와 DIP | 하위 도메인 유형과 바운디드 컨텍스트 경계 | 핵사고날 아키텍처와 CQRS |

---

## 2. 전략 패턴 (Strategic Patterns)

### 2.1 도메인과 하위 도메인 [A][B][C]

도메인은 소프트웨어가 해결하려는 비즈니스 영역이며, 여러 하위 도메인으로 구성된다.

**하위 도메인 유형** [B]:

| 유형 | 경쟁 우위 | 복잡성 | 변동성 | 솔루션 전략 |
|------|----------|--------|--------|------------|
| 핵심(Core) | 직접적 경쟁력 | 높음 | 잦은 변경 | 사내 구현 필수 |
| 일반(Generic) | 없음 | 높음 (알려진 문제) | 낮음 | 외부 솔루션/오픈소스 |
| 지원(Supporting) | 없음 | 낮음 (CRUD 수준) | 낮음 | 하청 가능, RAD |

[C]에서는 하위 도메인을 "문제점 공간(problem space)"의 일부로 정의하고, 바운디드 컨텍스트를 "해결책 공간(solution space)"으로 분리하여 설명한다. 하위 도메인과 바운디드 컨텍스트를 1:1로 묶으려는 시도는 바람직한 목표이지만, 반드시 그래야 하는 것은 아니다.

```python
from dataclasses import dataclass
from enum import Enum


class SubdomainType(Enum):
    CORE = "core"           # 핵심: 경쟁 우위의 원천
    GENERIC = "generic"     # 일반: 모든 회사가 동일하게 수행
    SUPPORTING = "supporting"  # 지원: 비즈니스 활동 보조


@dataclass(frozen=True)
class Subdomain:
    name: str
    type: SubdomainType
    description: str

    @property
    def should_build_in_house(self) -> bool:
        return self.type == SubdomainType.CORE


# 예시: 온라인 쇼핑몰 도메인 분석
recommendation_engine = Subdomain(
    name="추천 엔진",
    type=SubdomainType.CORE,
    description="사용자 행동 기반 개인화 추천 알고리즘",
)

authentication = Subdomain(
    name="인증/권한",
    type=SubdomainType.GENERIC,
    description="사용자 로그인 및 권한 관리",
)

admin_panel = Subdomain(
    name="관리자 페이지",
    type=SubdomainType.SUPPORTING,
    description="상품/주문 CRUD 인터페이스",
)
```

### 2.2 유비쿼터스 언어 (Ubiquitous Language) [A][B][C]

도메인 전문가, 관계자, 개발자가 공통으로 사용하는 언어다. 코드, 문서, 대화 모든 곳에서 동일한 용어를 사용한다.

**3권 공통 원칙:**
- 기술 용어가 아닌 비즈니스 용어로 구성해야 한다
- 모호성이 없어야 하며 하나의 용어는 하나의 의미만 가져야 한다
- 유비쿼터스 언어는 바운디드 컨텍스트 경계 안에서만 보편적으로 적용된다

[B]는 유비쿼터스 언어를 포착하는 도구로 **거킨 테스트(Gherkin test)**를 강조한다:

```gherkin
Scenario: 에이전트에게 새로운 지원 케이스를 알린다
  Given: 빈센트 줄스는 새로운 지원 케이스를 제출한다
  When: 티켓이 울프씨에게 할당된다
  Then: 에이전트는 새로운 티켓에 대해 알림을 받는다
```

```python
# 유비쿼터스 언어가 반영되지 않은 코드 (나쁜 예)
class OrderManager:
    def process(self, data: dict):
        data["status"] = 2  # 매직 넘버, 비즈니스 의미 불명확
        self.db.update(data)


# 유비쿼터스 언어가 반영된 코드 (좋은 예)
class Order:
    """주문 애그리거트 - '주문'이라는 도메인 용어를 그대로 사용"""

    def place(self) -> None:
        """주문을 '접수'한다"""
        self._status = OrderStatus.PLACED

    def ship(self) -> None:
        """주문을 '출고'한다"""
        if not self._status.is_shippable:
            raise OrderCannotBeShippedException("출고 가능한 상태가 아닙니다")
        self._status = OrderStatus.SHIPPED
```

### 2.3 바운디드 컨텍스트 (Bounded Context) [A][B][C]

유비쿼터스 언어가 적용되는 명시적 경계다. 같은 용어(예: "리드")가 마케팅과 영업에서 다른 의미를 가질 때, 각각을 별도의 바운디드 컨텍스트로 분리한다.

**3권의 관점 차이:**
- [B]: "하위 도메인은 발견하고, 바운디드 컨텍스트는 설계한다"는 점을 가장 강조. 바운디드 컨텍스트는 물리적/소유권 경계이며, 한 팀에서만 구현/유지관리해야 한다.
- [C]: 바운디드 컨텍스트를 "도메인 모델을 적용할 수 있는 개념적 경계"로 정의. 하나의 바운디드 컨텍스트는 하나의 프로젝트 안에 머물러야 하며, 유스케이스 집합을 포함한다.
- [A]: 바운디드 컨텍스트보다는 도메인 영역 내부의 모듈 구성에 집중한다.

```python
# 마케팅 컨텍스트에서의 '리드'
# marketing/domain/lead.py
@dataclass
class Lead:
    """잠재 고객 - 마케팅 채널을 통해 유입된 연락처"""
    contact_id: str
    source_channel: str  # 유입 채널
    campaign_id: str     # 캠페인 ID

    def qualify(self) -> None:
        """리드를 검증하여 MQL(Marketing Qualified Lead)로 전환"""
        ...


# 영업 컨텍스트에서의 '리드'
# sales/domain/lead.py
@dataclass
class Lead:
    """영업 기회 - 영업 파이프라인에 진입한 잠재 거래"""
    opportunity_id: str
    estimated_revenue: Money
    assigned_sales_rep: str

    def convert_to_deal(self) -> "Deal":
        """리드를 거래(Deal)로 전환"""
        ...
```

### 2.4 컨텍스트 맵 (Context Map) [B][C]

바운디드 컨텍스트 간의 관계를 시각적으로 표현한 도식이다.

**연동 패턴 정리** [B][C]:

| 패턴 그룹 | 패턴 | 설명 |
|-----------|------|------|
| 협력형 | 파트너십(Partnership) | 양 팀이 애드훅 방식으로 API 변경을 조정 |
| 협력형 | 공유 커널(Shared Kernel) | 모델의 일부를 공유, 중복 비용 > 조율 비용일 때만 사용 |
| 사용자-제공자 | 순응주의자(Conformist) | 업스트림 모델을 그대로 수용 |
| 사용자-제공자 | 충돌 방지 계층(ACL) | 업스트림 모델을 자신의 모델로 변환 |
| 사용자-제공자 | 오픈 호스트 서비스(OHS) | 퍼블릭 인터페이스로 제공자가 내부 모델 번역 구현 |
| 분리형 | 분리형 노선(Separated Ways) | 협력하지 않고 기능 중복 허용 |

[C]는 추가로 **발행된 언어(Published Language)**, **큰 진흙공(Big Ball of Mud)** 패턴도 설명한다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


# === 충돌 방지 계층(ACL) 패턴 구현 예시 ===

# 외부 시스템(업스트림)의 모델 - 우리가 제어할 수 없음
@dataclass
class ExternalUserDTO:
    """외부 인증 시스템의 사용자 데이터"""
    usr_id: str
    usr_nm: str
    usr_email: str
    role_cd: int


# 우리 도메인(다운스트림)의 모델
@dataclass(frozen=True)
class Author:
    """협업 컨텍스트에서의 작성자 값 객체"""
    user_id: str
    display_name: str
    email: str


# ACL: 외부 모델을 내부 모델로 변환하는 계층
class CollaboratorTranslator:
    """충돌 방지 계층 - 외부 인증 컨텍스트의 모델을
    협업 컨텍스트의 도메인 모델로 변환한다"""

    def to_author(self, external_user: ExternalUserDTO) -> Author:
        return Author(
            user_id=external_user.usr_id,
            display_name=external_user.usr_nm,
            email=external_user.usr_email,
        )


# === 오픈 호스트 서비스(OHS) 패턴 개념 ===

class ProductCatalogService(ABC):
    """오픈 호스트 서비스: 카탈로그 컨텍스트가 제공하는 퍼블릭 API
    내부 구현 모델의 변경으로부터 사용자(다운스트림)를 보호한다"""

    @abstractmethod
    def get_product_summary(self, product_id: str) -> dict:
        """발행된 언어(Published Language)로 제품 정보를 반환"""
        ...
```

---

## 3. 전술 패턴 (Tactical Patterns)

### 3.1 값 객체 (Value Object) [A][B][C]

고유 식별자가 없으며, 개념적으로 완전한 하나를 표현한다. 불변(immutable)이어야 한다.

**3권 공통 원칙:**
- 식별자 없이 속성의 조합으로 동등성을 판단한다
- 반드시 불변이어야 한다 (setter 금지)
- 부작용과 동시성 문제가 없다

[B]는 값 객체가 유비쿼터스 언어 자체가 될 수 있음을 강조한다: `_countryCode: str` 대신 `_country: CountryCode`로 표현하면 짧은 변수명으로도 의도가 명확해진다.

```python
from dataclasses import dataclass


@dataclass(frozen=True)  # frozen=True로 불변 보장
class Money:
    """금액 값 객체 [A][B]"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("금액은 0 이상이어야 합니다")

    def add(self, other: "Money") -> "Money":
        """새로운 Money 객체를 생성하여 반환 (불변 유지)"""
        if self.currency != other.currency:
            raise ValueError("통화가 다릅니다")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def multiply(self, factor: int) -> "Money":
        return Money(amount=self.amount * factor, currency=self.currency)


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


# 사용 예
price = Money(1000)
total = price.multiply(3)  # '정수 연산'이 아니라 '금액 계산' [A]
```

### 3.2 엔티티 (Entity) [A][B][C]

고유 식별자를 가지며, 라이프사이클 동안 상태가 변한다. 값이 같아도 식별자가 다르면 다른 객체다.

**[A] vs [B]의 관점 차이:**
- [A]: 엔티티가 도메인 기능을 포함하되, 하나의 함수가 같은 엔티티의 다른 함수를 호출하지 않도록 해야 한다.
- [B]: 엔티티는 독립적 패턴이 아닌 애그리거트의 일부로서만 사용된다.

```python
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Member:
    """회원 엔티티 [A]"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    email: str = ""
    _password: str = field(default="", repr=False)

    def change_password(self, old_pw: str, new_pw: str) -> None:
        """도메인 규칙이 엔티티 안에 위치한다 [A]"""
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

### 3.3 애그리거트 (Aggregate) [A][B][C]

연관된 엔티티와 값 객체를 하나로 묶은 개념적 단위다. 일관성 관리의 기준이 되며, 트랜잭션 경계이기도 하다.

**3권 공통 핵심 원칙:**
1. 애그리거트 루트를 통해서만 내부 객체에 접근한다
2. 한 트랜잭션에서는 한 개의 애그리거트만 수정한다
3. 다른 애그리거트는 ID로 참조한다 (직접 참조 금지)
4. 리포지토리는 애그리거트 단위로 존재한다

**3권의 관점 차이:**
- [A]: 경계 설정의 기준은 "함께 생성되는 구성요소"이며 "A가 B를 갖는다"는 관계만으로 같은 애그리거트에 넣으면 안 된다.
- [B]: 자유도를 줄이는 수단으로 설명. 비즈니스 불변성을 감싸서 복잡성을 낮춘다. 커맨드(상태 변경 메서드)를 통해서만 상태를 변경해야 한다.
- [C]: "DDD의 전술 도구 가운데 가장 이해도가 낮은 도구"라며, 작은 객체 클러스터로 일관성 경계를 구축할 것을 권고한다.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from uuid import uuid4


# --- 값 객체들 ---
@dataclass(frozen=True)
class OrderLineItem:
    product_id: str
    product_name: str
    price: Money
    quantity: int

    @property
    def amounts(self) -> Money:
        return self.price.multiply(self.quantity)


class OrderStatus(Enum):
    PAYMENT_WAITING = "payment_waiting"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

    @property
    def is_shippable(self) -> bool:
        return self in (OrderStatus.PAYMENT_WAITING, OrderStatus.PREPARING)


@dataclass(frozen=True)
class ShippingInfo:
    receiver_name: str
    receiver_phone: str
    address: Address


# --- 애그리거트 루트 ---
@dataclass
class Order:
    """주문 애그리거트 [A][B][C]

    - Order가 애그리거트 루트이다
    - OrderLineItem, ShippingInfo는 애그리거트 내부 구성요소
    - 모든 상태 변경은 Order를 통해서만 수행한다
    - 다른 애그리거트(Member)는 ID로만 참조한다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    orderer_id: str = ""  # Member 애그리거트를 ID로 참조 [A][B][C]
    order_lines: List[OrderLineItem] = field(default_factory=list)
    shipping_info: ShippingInfo = None
    _status: OrderStatus = field(default=OrderStatus.PAYMENT_WAITING)

    def __post_init__(self):
        self._verify_at_least_one_order_line()
        self._calculate_total_amounts()

    def _verify_at_least_one_order_line(self) -> None:
        if not self.order_lines:
            raise ValueError("최소 한 종류 이상의 상품을 주문해야 합니다")

    def _calculate_total_amounts(self) -> None:
        """애그리거트 루트가 내부 객체를 조합해서 기능을 완성 [A]"""
        total = Money(0)
        for line in self.order_lines:
            total = total.add(line.amounts)
        self._total_amounts = total

    @property
    def total_amounts(self) -> Money:
        return self._total_amounts

    @property
    def status(self) -> OrderStatus:
        return self._status

    def change_shipping_info(self, new_info: ShippingInfo) -> None:
        """배송지 변경 - 도메인 규칙을 애그리거트 루트에서 관리 [A]"""
        if not self._status.is_shippable:
            raise ValueError("배송지를 변경할 수 없는 상태입니다")
        self.shipping_info = new_info

    def ship(self) -> None:
        """출고 처리"""
        if self._status != OrderStatus.PREPARING:
            raise ValueError("준비 상태에서만 출고할 수 있습니다")
        self._status = OrderStatus.SHIPPED

    def place(self) -> None:
        """주문 접수 확인 -> 준비 상태로 전환"""
        if self._status != OrderStatus.PAYMENT_WAITING:
            raise ValueError("결제 대기 상태에서만 접수할 수 있습니다")
        self._status = OrderStatus.PREPARING
```

#### 애그리거트를 팩토리로 사용하기 [A]

애그리거트가 다른 애그리거트를 생성할 때, 도메인 로직을 애그리거트 안에 둘 수 있다.

```python
@dataclass
class Store:
    """상점 애그리거트 [A]"""
    id: str
    name: str
    _is_blocked: bool = False

    def create_product(self, product_id: str, name: str, price: Money) -> "Product":
        """팩토리 메서드 - 도메인 로직(신고 차단 여부)을 애그리거트 안에 유지 [A]"""
        if self._is_blocked:
            raise PermissionError("차단된 상점은 상품을 등록할 수 없습니다")
        return Product(id=product_id, store_id=self.id, name=name, price=price)
```

### 3.4 리포지토리 (Repository) [A][B][C]

애그리거트 단위로 도메인 객체의 영속성을 처리한다. 도메인 영역에 인터페이스를 정의하고, 인프라 영역에서 구현한다 (DIP).

```python
from abc import ABC, abstractmethod
from typing import Optional


# 도메인 영역: 리포지토리 인터페이스 (고수준 모듈)
class OrderRepository(ABC):
    """주문 리포지토리 인터페이스 [A][C]
    - 애그리거트 단위로 저장/조회한다
    - OrderLine을 위한 별도 리포지토리는 만들지 않는다
    """

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...

    @abstractmethod
    def delete(self, order: Order) -> None:
        ...


# 인프라 영역: 리포지토리 구현 (저수준 모듈)
class DjangoOrderRepository(OrderRepository):
    """Django ORM 기반 리포지토리 구현체"""

    def find_by_id(self, order_id: str) -> Optional[Order]:
        try:
            orm_order = OrderModel.objects.get(id=order_id)
            return self._to_domain(orm_order)
        except OrderModel.DoesNotExist:
            return None

    def save(self, order: Order) -> None:
        # Order 애그리거트에 속한 모든 객체를 함께 저장
        orm_order = self._to_orm(order)
        orm_order.save()

    def delete(self, order: Order) -> None:
        OrderModel.objects.filter(id=order.id).delete()

    def _to_domain(self, orm_obj) -> Order:
        """ORM 모델 -> 도메인 모델 변환"""
        ...

    def _to_orm(self, domain_obj: Order):
        """도메인 모델 -> ORM 모델 변환"""
        ...
```

### 3.5 도메인 서비스 (Domain Service) [A][B][C]

여러 애그리거트에 걸친 도메인 로직을 구현한다. **상태 없이(stateless) 로직만 구현**한다.

**응용 서비스 vs 도메인 서비스 구분법** [A]:
- 해당 로직이 애그리거트의 상태를 변경하거나 상태 값을 계산하는가? -> 도메인 서비스
- 트랜잭션 처리, 도메인 객체 조회/저장 조율인가? -> 응용 서비스

```python
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Coupon:
    code: str
    discount_amount: Money


class MemberGrade(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    VIP = "vip"


class DiscountCalculationService:
    """할인 계산 도메인 서비스 [A][B]

    - 상태가 없다 (stateless)
    - 여러 애그리거트(주문, 쿠폰, 회원)의 데이터를 사용하여 계산
    - 한 애그리거트에 넣기 애매한 로직을 명시적으로 표현
    """

    def calculate_discount(
        self,
        order_lines: List[OrderLineItem],
        coupons: List[Coupon],
        member_grade: MemberGrade,
    ) -> Money:
        coupon_discount = Money(0)
        for coupon in coupons:
            coupon_discount = coupon_discount.add(coupon.discount_amount)

        grade_discount = self._calculate_grade_discount(member_grade, order_lines)
        return coupon_discount.add(grade_discount)

    def _calculate_grade_discount(
        self, grade: MemberGrade, order_lines: List[OrderLineItem]
    ) -> Money:
        total = Money(0)
        for line in order_lines:
            total = total.add(line.amounts)

        rate = {
            MemberGrade.BRONZE: 0,
            MemberGrade.SILVER: 0.01,
            MemberGrade.GOLD: 0.03,
            MemberGrade.VIP: 0.05,
        }.get(grade, 0)

        return Money(int(total.amount * rate))


# 애그리거트가 도메인 서비스를 사용하는 패턴 [A]
@dataclass
class OrderWithDiscount(Order):
    def calculate_payment(
        self,
        discount_service: DiscountCalculationService,
        coupons: List[Coupon],
        member_grade: MemberGrade,
    ) -> None:
        """도메인 서비스 객체를 파라미터로 전달 (주입하지 않는다) [A]"""
        discount = discount_service.calculate_discount(
            self.order_lines, coupons, member_grade
        )
        self._payment_amounts = Money(
            max(0, self._total_amounts.amount - discount.amount)
        )
```

#### 외부 시스템 연동과 도메인 서비스 [A]

```python
from abc import ABC, abstractmethod


class SurveyPermissionChecker(ABC):
    """설문 조사 권한 확인 도메인 서비스 인터페이스 [A]
    외부 시스템(역할 관리 시스템)과의 연동을 추상화"""

    @abstractmethod
    def has_creation_permission(self, user_id: str) -> bool:
        ...


# 인프라 영역에서 실제 외부 시스템 연동 구현
class ExternalSurveyPermissionChecker(SurveyPermissionChecker):
    def __init__(self, api_client):
        self._api_client = api_client

    def has_creation_permission(self, user_id: str) -> bool:
        response = self._api_client.get(f"/users/{user_id}/permissions")
        return "CREATE_SURVEY" in response.get("permissions", [])
```

### 3.6 응용 서비스 (Application Service) [A][C]

도메인 영역과 표현 영역을 연결하는 매개체(파사드) 역할이다. 비즈니스 로직을 직접 구현하지 않으며, 도메인 객체에 위임한다.

**응용 서비스의 책임** [A][C]:
- 리포지토리에서 애그리거트를 조회한다
- 애그리거트의 도메인 기능을 실행한다
- 트랜잭션을 관리한다
- 결과를 리턴한다

**응용 서비스가 하면 안 되는 것** [A]:
- 도메인 로직을 직접 구현하면 안 된다
- 표현 영역에 의존하면 안 된다 (HttpRequest 등을 파라미터로 받지 말 것)

```python
from dataclasses import dataclass


@dataclass
class PlaceOrderCommand:
    """응용 서비스 입력 DTO"""
    orderer_id: str
    items: List[dict]  # [{"product_id": ..., "quantity": ...}]
    shipping_address: dict
    coupon_codes: List[str]


class OrderApplicationService:
    """주문 응용 서비스 [A][C]

    - 비즈니스 로직이 없다 (도메인에 위임)
    - 트랜잭션 관리
    - 도메인 객체 간의 흐름을 제어
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        member_repository: "MemberRepository",
        product_repository: "ProductRepository",
        discount_service: DiscountCalculationService,
    ):
        self._order_repo = order_repository
        self._member_repo = member_repository
        self._product_repo = product_repository
        self._discount_service = discount_service

    def place_order(self, cmd: PlaceOrderCommand) -> str:
        """주문 접수 유스케이스 [A][C]"""
        # 1. 리포지토리에서 필요한 애그리거트를 조회한다
        member = self._member_repo.find_by_id(cmd.orderer_id)
        if member is None:
            raise ValueError("회원을 찾을 수 없습니다")

        # 2. 도메인 객체를 조합하여 새 애그리거트를 생성한다
        order_lines = self._create_order_lines(cmd.items)
        shipping_info = ShippingInfo(
            receiver_name=cmd.shipping_address["name"],
            receiver_phone=cmd.shipping_address["phone"],
            address=Address(
                city=cmd.shipping_address["city"],
                street=cmd.shipping_address["street"],
                zipcode=cmd.shipping_address["zipcode"],
            ),
        )

        order = Order(
            orderer_id=member.id,
            order_lines=order_lines,
            shipping_info=shipping_info,
        )

        # 3. 리포지토리에 저장한다
        self._order_repo.save(order)
        return order.id

    def cancel_order(self, order_id: str) -> None:
        """주문 취소 [A] - 단순한 흐름 제어만 담당"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.cancel()  # 도메인 로직은 Order 애그리거트에 위임

    def change_shipping_info(
        self, order_id: str, new_info_data: dict, use_as_member_addr: bool = False
    ) -> None:
        """배송지 변경 [A]

        두 애그리거트를 수정해야 할 경우,
        애그리거트에서 다른 애그리거트를 직접 수정하지 말고
        응용 서비스에서 각각 수정하도록 구현한다.
        """
        order = self._order_repo.find_by_id(order_id)
        new_info = ShippingInfo(**new_info_data)
        order.change_shipping_info(new_info)

        if use_as_member_addr:
            member = self._member_repo.find_by_id(order.orderer_id)
            member.change_address(new_info.address)  # 별도 애그리거트 수정

    def _create_order_lines(self, items: List[dict]) -> List[OrderLineItem]:
        result = []
        for item in items:
            product = self._product_repo.find_by_id(item["product_id"])
            result.append(
                OrderLineItem(
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    quantity=item["quantity"],
                )
            )
        return result
```

---

## 4. 아키텍처 [A][C]

### 4.1 계층 아키텍처 [A][C]

전형적인 4계층 구조:

```
표현(Presentation) -> 응용(Application) -> 도메인(Domain) -> 인프라(Infrastructure)
```

**핵심 규칙** [A][C]:
- 상위 계층에서 하위 계층으로만 의존한다 (하위 -> 상위 절대 불가)
- 도메인 영역, 응용 영역, 표현 영역은 인프라의 구현 기술을 직접 사용하지 않는다
- DIP를 적용하여 도메인 영역에 정의한 인터페이스를 인프라에서 구현한다

### 4.2 DIP (의존성 역전 원칙) [A][C]

고수준 모듈이 저수준 모듈에 의존하지 않도록 추상화에 의존한다. 인터페이스는 고수준(도메인) 영역에 위치해야 한다.

```python
from abc import ABC, abstractmethod


# 도메인 영역 (고수준): 인터페이스 정의
class RuleDiscounter(ABC):
    """할인 규칙 인터페이스 - 도메인(고수준)에 위치 [A]"""

    @abstractmethod
    def apply_rules(
        self, customer_id: str, order_lines: List[OrderLineItem]
    ) -> Money:
        ...


# 인프라 영역 (저수준): 구현체
class DroolsRuleDiscounter(RuleDiscounter):
    """Drools 엔진 기반 구현 - 인프라(저수준)에 위치 [A]"""

    def apply_rules(
        self, customer_id: str, order_lines: List[OrderLineItem]
    ) -> Money:
        # Drools 엔진 호출 로직
        ...


class SimpleRuleDiscounter(RuleDiscounter):
    """간단한 규칙 기반 구현 - 인프라(저수준)에 위치"""

    def apply_rules(
        self, customer_id: str, order_lines: List[OrderLineItem]
    ) -> Money:
        # 직접 계산 로직
        ...


# 응용 서비스: 추상화에만 의존
class CalculateDiscountService:
    """DIP 적용 예시 [A]
    - RuleDiscounter 인터페이스에만 의존
    - Drools든 Simple이든 상관없이 동작
    - 테스트 시 Mock 객체 주입 가능
    """

    def __init__(self, rule_discounter: RuleDiscounter):
        self._rule_discounter = rule_discounter

    def calculate_discount(
        self, order_lines: List[OrderLineItem], customer_id: str
    ) -> Money:
        return self._rule_discounter.apply_rules(customer_id, order_lines)
```

### 4.3 핵사고날 아키텍처 (포트와 어댑터) [C]

[C]가 가장 상세하게 다루는 아키텍처 스타일이다. 외부(어댑터)와 내부(도메인+응용)를 분리하며, 다양한 클라이언트가 동등한 지위에서 시스템과 상호작용한다.

```python
from abc import ABC, abstractmethod


# === 포트(Port): 내부와 외부의 경계 인터페이스 ===

# 입력 포트 (Primary/Driving Port)
class PlaceOrderUseCase(ABC):
    """주문 접수 유스케이스 포트 - 도메인 영역에 정의"""

    @abstractmethod
    def execute(self, cmd: PlaceOrderCommand) -> str:
        ...


# 출력 포트 (Secondary/Driven Port)
class OrderPersistencePort(ABC):
    """주문 영속화 포트 - 도메인 영역에 정의"""

    @abstractmethod
    def save(self, order: Order) -> None:
        ...

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        ...


class NotificationPort(ABC):
    """알림 발송 포트"""

    @abstractmethod
    def send_order_confirmation(self, order_id: str, email: str) -> None:
        ...


# === 내부(도메인+응용): 유스케이스 구현 ===

class PlaceOrderService(PlaceOrderUseCase):
    """입력 포트의 구현 - 응용 서비스"""

    def __init__(
        self,
        persistence: OrderPersistencePort,
        notification: NotificationPort,
    ):
        self._persistence = persistence
        self._notification = notification

    def execute(self, cmd: PlaceOrderCommand) -> str:
        order = Order(orderer_id=cmd.orderer_id, order_lines=[], ...)
        self._persistence.save(order)
        self._notification.send_order_confirmation(order.id, "user@example.com")
        return order.id


# === 어댑터(Adapter): 외부 기술과 연결 ===

# 입력 어댑터 (HTTP -> 유스케이스)
class OrderRestAdapter:
    """REST API 입력 어댑터 [C]"""

    def __init__(self, use_case: PlaceOrderUseCase):
        self._use_case = use_case

    def post_order(self, request_body: dict) -> dict:
        cmd = PlaceOrderCommand(**request_body)
        order_id = self._use_case.execute(cmd)
        return {"order_id": order_id, "status": "created"}


# 출력 어댑터 (유스케이스 -> DB)
class PostgresOrderAdapter(OrderPersistencePort):
    """PostgreSQL 출력 어댑터"""

    def save(self, order: Order) -> None:
        # SQL INSERT 로직
        ...

    def find_by_id(self, order_id: str) -> Optional[Order]:
        # SQL SELECT 로직
        ...


# 출력 어댑터 (유스케이스 -> 이메일)
class SmtpNotificationAdapter(NotificationPort):
    """SMTP 이메일 출력 어댑터"""

    def send_order_confirmation(self, order_id: str, email: str) -> None:
        # 이메일 발송 로직
        ...
```

### 4.4 CQRS (커맨드-쿼리 책임 분리) [C]

커맨드(상태 변경)와 쿼리(데이터 조회)의 모델을 분리한다.

**핵심 원칙** [C]: "질문하는 행동이 대답을 바꿔서는 안 된다"

```python
# === 커맨드 모델: 상태 변경만 담당 ===

class OrderCommandModel:
    """커맨드 모델의 애그리거트 [C]
    - 쿼리 메서드(getter) 없이 커맨드 메서드만 포함
    - ID 기반 조회만 지원
    """

    def __init__(self, order_id: str):
        self._id = order_id
        self._status = OrderStatus.PAYMENT_WAITING

    @property
    def id(self) -> str:
        return self._id

    def place(self) -> None:
        """커맨드: 주문 접수"""
        self._status = OrderStatus.PREPARING

    def ship(self) -> None:
        """커맨드: 출고"""
        self._status = OrderStatus.SHIPPED


# 커맨드 모델 리포지토리: save + ID 기반 조회만
class OrderCommandRepository(ABC):
    @abstractmethod
    def save(self, order: OrderCommandModel) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[OrderCommandModel]: ...


# === 쿼리 모델: 데이터 조회만 담당 ===

@dataclass(frozen=True)
class OrderSummaryView:
    """쿼리 모델: 표시용 데이터 뷰 [C]
    - 비정규화된 데이터
    - 한 가지 종류의 클라이언트 뷰를 위한 데이터
    - 조인 없이 단순 쿼리로 조회
    """
    order_id: str
    orderer_name: str
    total_amount: int
    item_count: int
    status: str
    ordered_at: str


class OrderQueryService:
    """쿼리 서비스 [C]
    - 커맨드 모델과 완전히 분리된 조회 전용 서비스
    - 조인 없이 비정규화된 뷰 테이블에서 직접 조회
    """

    def get_order_summary(self, order_id: str) -> OrderSummaryView:
        # SELECT * FROM order_summary_view WHERE order_id = ?
        ...

    def list_orders_by_member(
        self, member_id: str, page: int, size: int
    ) -> List[OrderSummaryView]:
        # SELECT * FROM order_summary_view WHERE orderer_id = ? LIMIT ? OFFSET ?
        ...
```

---

## 5. 단순한 비즈니스 로직 패턴 [B]

[B]는 DDD의 전술 패턴이 모든 상황에 적합하지 않음을 강조하며, 단순한 비즈니스 로직을 위한 패턴을 소개한다.

### 5.1 트랜잭션 스크립트

절차지향 스크립트로 비즈니스 로직을 구현한다. 지원 하위 도메인에 적합하다.

```python
class FileConversionScript:
    """트랜잭션 스크립트 패턴 [B]
    - 단순한 절차지향 스크립트
    - 지원 하위 도메인, ETL 등에 적합
    """

    def convert_json_to_xml(self, job_id: str) -> None:
        db.start_transaction()
        try:
            job = db.load_next_job(job_id)
            json_data = load_file(job.source)
            xml_data = convert_json_to_xml(json_data)
            write_file(job.destination, xml_data)
            db.mark_job_as_completed(job)
            db.commit()
        except Exception:
            db.rollback()
            raise
```

### 5.2 액티브 레코드

데이터베이스 테이블 행을 감싸는 객체로, CRUD와 간단한 유효성 검사를 포함한다. [B]는 이를 "빈약한 도메인 모델 안티패턴"이라고도 부른다.

```python
class UserRecord:
    """액티브 레코드 패턴 [B]
    - 복잡한 자료구조의 DB 매핑을 캡슐화
    - Django Model과 유사한 패턴
    - 비즈니스 로직이 단순한 경우에만 적합
    """

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def validate(self) -> bool:
        return "@" in self.email and len(self.name) > 0

    def save(self) -> None:
        if not self.validate():
            raise ValueError("유효하지 않은 데이터")
        # INSERT/UPDATE SQL 실행
        ...
```

---

## 6. 패키지 구조 (모듈 구성) [A][C]

### Django 프로젝트에 DDD 적용 [A]

```
order/                          # 바운디드 컨텍스트 (또는 Django App)
  views/                        # 표현 계층 + 응용 계층 (1층)
    order_view.py               #   - HTTP 요청/응답 처리
    serializers.py              #   - dataclass -> JSON 변환
  services/                     # 도메인 서비스 + 서비스 계층 (2층)
    order_service.py            #   - 비즈니스 로직 조율
    discount_service.py         #   - 도메인 서비스
  domain/                       # 도메인 계층 (3층) - DIP의 기준
    order.py                    #   - 엔티티, 값 객체, 애그리거트
    order_repository.py         #   - 리포지토리 인터페이스
  infrastructure/               # 인프라 계층 (4층)
    django_order_repository.py  #   - 리포지토리 구현체
    email_service.py            #   - 외부 시스템 연동 구현
```

### 일반적인 DDD 프로젝트 [C]

```
com.mycompany.order/                   # 바운디드 컨텍스트
  presentation/                        # 사용자 인터페이스 계층
  application/                         # 응용 계층
  domain/
    model/                             # 도메인 모델 (엔티티, 값 객체, 애그리거트)
    service/                           # 도메인 서비스
    repository/                        # 리포지토리 인터페이스
  infrastructure/                      # 인프라 계층 (리포지토리 구현, 메시징 등)
```

---

## 7. 도메인 이벤트 [B][C]

비즈니스 도메인에서 발생한 중요한 사건을 나타낸다. 애그리거트 커맨드 실행의 결과로 발행된다.

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    """도메인 이벤트 기본 클래스 [B][C]"""
    occurred_on: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderPlacedEvent(DomainEvent):
    """주문 접수됨 이벤트
    - 비즈니스 도메인에서 일어난 일을 간결하고 정확하게 반영 [B]
    """
    order_id: str = ""
    orderer_id: str = ""
    total_amount: int = 0


@dataclass(frozen=True)
class TicketEscalatedEvent(DomainEvent):
    """티켓 에스컬레이션 이벤트 [B]"""
    ticket_id: str = ""
    reason: str = ""


# 애그리거트에서 도메인 이벤트를 발행하는 패턴 [B][C]
@dataclass
class Ticket:
    """티켓 애그리거트 - 도메인 이벤트 발행 예시"""
    id: str = ""
    is_escalated: bool = False
    remaining_time_percentage: float = 1.0
    _domain_events: List[DomainEvent] = field(default_factory=list)

    def request_escalation(self, reason: str) -> None:
        if not self.is_escalated and self.remaining_time_percentage <= 0:
            self.is_escalated = True
            event = TicketEscalatedEvent(ticket_id=self.id, reason=reason)
            self._domain_events.append(event)

    def collect_domain_events(self) -> List[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
```

---

## 8. 복잡성 관리 원칙 [B]

[B]는 DDD의 전술 패턴이 궁극적으로 **시스템의 자유도를 줄여 복잡성을 낮추는 수단**임을 설명한다.

핵심 통찰:
- 복잡한 것을 불변성으로 감싸서 복잡성을 낮춘다 -- 이것이 애그리거트와 값 객체 패턴이 하는 것이다
- 값 객체의 상태 관련 모든 비즈니스 로직은 자신의 경계 안에 있다
- 비즈니스 로직은 비즈니스 불변성을 감싸고 보호하여 자유도를 줄인다

```python
# 자유도 3: 세 값을 독립적으로 변경 가능 -> 예측 어려움
class ClassA:
    def __init__(self):
        self.a = 0  # 자유
        self.b = 0  # 자유
        self.c = 0  # 자유


# 자유도 1: a만 알면 b, c가 결정됨 -> 예측 쉬움
class ClassB:
    def __init__(self):
        self._a = 0

    @property
    def a(self) -> int:
        return self._a

    @a.setter
    def a(self, value: int):
        self._a = value
        self._b = value // 2  # 불변성: a에 의해 결정
        self._c = value // 3  # 불변성: a에 의해 결정

    @property
    def b(self) -> int:
        return self._b

    @property
    def c(self) -> int:
        return self._c
```

---

## 9. 핵심 요약

| 구분 | 패턴 | 핵심 규칙 |
|------|------|----------|
| 전략 | 바운디드 컨텍스트 | 유비쿼터스 언어가 적용되는 명시적 경계. 하위 도메인은 발견, 바운디드 컨텍스트는 설계한다 |
| 전략 | 유비쿼터스 언어 | 모든 이해관계자가 동일한 비즈니스 용어 사용. 바운디드 컨텍스트 내에서만 유효 |
| 전략 | 컨텍스트 맵 | 바운디드 컨텍스트 간의 관계(파트너십, ACL, OHS 등)를 시각화 |
| 전술 | 값 객체 | 불변, 식별자 없음, 속성 조합으로 동등성 판단 |
| 전술 | 엔티티 | 고유 식별자 보유, 라이프사이클 동안 상태 변경 |
| 전술 | 애그리거트 | 일관성 경계이자 트랜잭션 경계. 루트를 통해서만 접근. ID로 타 애그리거트 참조 |
| 전술 | 리포지토리 | 애그리거트 단위로 영속성 처리. 도메인에 인터페이스, 인프라에 구현 |
| 전술 | 도메인 서비스 | 여러 애그리거트에 걸친 무상태 도메인 로직 |
| 전술 | 응용 서비스 | 도메인과 표현의 매개체. 비즈니스 로직 없이 흐름 제어와 트랜잭션 관리 |
| 전술 | 도메인 이벤트 | 비즈니스 도메인에서 발생한 중요한 사건을 표현 |
