# 리포지토리, 도메인 서비스, 응용 서비스

## 3.4 리포지토리 (Repository)

> 출처: [A][B][C], Cosmic Python

애그리거트 단위로 도메인 객체의 영속성을 처리한다. 도메인 영역에 인터페이스를 정의하고, 인프라 영역에서 구현한다 (DIP).

> "ORM이 도메인 모델을 임포트하게 하라. 도메인 모델이 ORM을 임포트하면 안 된다." -- Cosmic Python

```python
from abc import ABC, abstractmethod
from typing import Optional


# 도메인 영역: 리포지토리 인터페이스 (고수준 모듈)
class OrderRepository(ABC):
    """주문 리포지토리 인터페이스
    - 애그리거트 단위로 저장/조회한다
    - OrderLineItem을 위한 별도 리포지토리는 만들지 않는다
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

## 3.5 도메인 서비스 (Domain Service)

> 출처: [A][B][C], Cosmic Python
> **[의사결정 #3] External 채택**: 애그리거트가 도메인 서비스를 모르도록 분리한다.

여러 애그리거트에 걸친 도메인 로직을 구현한다. **상태 없이(stateless) 로직만 구현**한다.

**응용 서비스 vs 도메인 서비스 구분법** [A]:
- 해당 로직이 애그리거트의 상태를 변경하거나 상태 값을 계산하는가? -> 도메인 서비스
- 트랜잭션 처리, 도메인 객체 조회/저장 조율인가? -> 응용 서비스

응용 서비스(또는 핸들러)가 도메인 서비스를 호출하고, 애그리거트는 순수 도메인 로직(엔티티 상태 변경, 이벤트 발행)만 담당하도록 분리한다. 애그리거트는 외부 의존성을 받지 않는다 (Cosmic Python).

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
    """할인 계산 도메인 서비스

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


# 좋은 예: 응용 서비스가 도메인 서비스를 호출하고 결과를 애그리거트에 전달
class OrderApplicationService:
    def apply_discount(self, order_id: str, coupons: List[Coupon], grade: MemberGrade):
        order = self._order_repo.find_by_id(order_id)
        discount = self._discount_service.calculate_discount(
            order.order_lines, coupons, grade
        )
        order.apply_discount(discount)  # 애그리거트는 Money 값만 받음 (서비스 모름)
        self._order_repo.save(order)


# 나쁜 예: 애그리거트가 도메인 서비스를 직접 파라미터로 받음
class OrderBad:
    def calculate_payment(
        self,
        discount_service: DiscountCalculationService,  # 외부 의존성!
        coupons: List[Coupon],
        member_grade: MemberGrade,
    ) -> None:
        discount = discount_service.calculate_discount(
            self.order_lines, coupons, member_grade
        )
        self._payment_amounts = Money(
            max(0, self._total_amounts.amount - discount.amount)
        )
```

## 3.6 응용 서비스 (Application Service)

> 출처: [A][C], Cosmic Python

도메인 영역과 표현 영역을 연결하는 매개체(파사드) 역할이다. 비즈니스 로직을 직접 구현하지 않으며, 도메인 객체에 위임한다.

**응용 서비스의 책임:**
- 리포지토리에서 애그리거트를 조회한다
- 애그리거트의 도메인 기능을 실행한다
- 트랜잭션을 관리한다
- 결과를 리턴한다

**응용 서비스가 하면 안 되는 것:**
- 도메인 로직을 직접 구현하면 안 된다
- 표현 영역에 의존하면 안 된다 (HttpRequest 등을 파라미터로 받지 말 것)

```python
@dataclass
class PlaceOrderCommand:
    """응용 서비스 입력 DTO"""
    orderer_id: str
    items: List[dict]
    shipping_address: dict
    coupon_codes: List[str]


class OrderApplicationService:
    """주문 응용 서비스

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
        """주문 접수 유스케이스"""
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
        """주문 취소 - 단순한 흐름 제어만 담당"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.cancel()  # 도메인 로직은 Order 애그리거트에 위임

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
