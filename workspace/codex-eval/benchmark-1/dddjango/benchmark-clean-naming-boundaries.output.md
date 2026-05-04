**주요 내용**

기준을 하나로 잡으면 됩니다: **`Manager`는 Django ORM 전용, `Service`는 책임이 분명할 때만, `UseCase`는 가능하면 동사형 Handler/ApplicationService로 대체**하세요.

| 이름 | 사용 여부 | 책임 | 예시 | 금지 기준 |
|---|---:|---|---|---|
| `OrderManager` | 제한적 사용 | Django ORM `Manager`/`QuerySet` | `OrderQuerySet.paid()`, `OrderManager.from_queryset(...)` | 주문 생성, 결제, 취소 같은 비즈니스 유스케이스 금지 |
| `OrderService` | 비권장 | 너무 넓고 모호함 | 가능하면 쓰지 않음 | “주문 관련 아무거나”가 들어가는 God Class가 되기 쉬움 |
| `OrderUseCase` | 비권장 | 이름이 추상적이고 책임 범위가 불명확 | 가능하면 쓰지 않음 | 어떤 유스케이스인지 이름만 보고 알 수 없음 |
| `OrderApplicationService` | 사용 가능 | 주문 유스케이스 조율 | `place_order`, `cancel_order` | 할인 계산, 상태 전이 규칙 직접 구현 금지 |
| `PlaceOrderHandler` | 권장 | 유스케이스 하나 처리 | `handle(command)` | 여러 유스케이스를 한 클래스에 누적 금지 |
| `DiscountCalculationService` | 조건부 권장 | 도메인 서비스 | 여러 애그리거트/VO를 사용한 할인 계산 | DB 조회, 트랜잭션, HTTP 의존 금지 |
| `Order` | 필수 중심 | Aggregate Root | `order.cancel()`, `order.confirm_payment()` | 단순 데이터 컨테이너로 두고 모든 로직을 서비스로 빼는 것 금지 |

내 기준은 이렇게 잡겠습니다.

1. **Django `Manager`는 쿼리 표현 전용**
   
   `OrderManager`는 Django 모델의 `objects`에 붙는 ORM 도구일 때만 씁니다.

   ```python
   class OrderQuerySet(models.QuerySet):
       def paid(self):
           return self.filter(status=OrderStatus.PAID)

       def waiting_for_payment(self):
           return self.filter(status=OrderStatus.WAITING_FOR_PAYMENT)


   class OrderModel(models.Model):
       objects = OrderQuerySet.as_manager()
   ```

   여기에 `place_order()`, `cancel_order()`, `pay_order()` 같은 유스케이스를 넣으면 DDD 경계가 흐려집니다.

2. **`OrderService`라는 이름은 기본적으로 금지**
   
   `OrderService`는 책임이 너무 넓습니다. 실제 책임에 따라 이름을 바꿔야 합니다.

   ```text
   bad:
   OrderService.place_order()
   OrderService.cancel_order()
   OrderService.calculate_discount()
   OrderService.notify_order_created()

   good:
   OrderApplicationService.place_order()
   OrderCancellationPolicy.can_cancel()
   DiscountCalculationService.calculate()
   OrderNotificationGateway.send_order_created()
   ```

3. **Application Service는 유스케이스 조율자**
   
   `OrderApplicationService`는 다음만 합니다.

   - Command DTO를 받는다
   - Repository에서 Aggregate를 조회한다
   - 도메인 객체의 메서드를 호출한다
   - 트랜잭션을 관리한다
   - Repository에 저장한다
   - `transaction.on_commit()`으로 후속 작업을 연결한다

   하지 말아야 할 것:

   - `if order.status == "paid"` 같은 상태 전이 규칙 직접 구현
   - 할인, 취소 가능 여부, 재고 차감 규칙 직접 계산
   - Django `HttpRequest`, Ninja `Schema`, ORM 모델을 도메인 내부로 넘기기

4. **유스케이스가 많아지면 `ApplicationService`보다 Handler가 낫다**
   
   작은 앱이면:

   ```python
   class OrderApplicationService:
       def place_order(self, command: PlaceOrderCommand) -> OrderId: ...
       def cancel_order(self, command: CancelOrderCommand) -> None: ...
   ```

   커지면 유스케이스 단위로 나눕니다.

   ```python
   class PlaceOrderHandler:
       def handle(self, command: PlaceOrderCommand) -> OrderId: ...


   class CancelOrderHandler:
       def handle(self, command: CancelOrderCommand) -> None: ...
   ```

   이 경우 `OrderUseCase` 같은 포괄 이름은 쓰지 말고, 반드시 **동사 + 목적어**로 씁니다: `PlaceOrder`, `CancelOrder`, `ConfirmPayment`, `ShipOrder`.

5. **도메인 규칙은 Aggregate Root 또는 Domain Service에 둔다**
   
   주문 상태 전이처럼 주문 하나의 불변식이면 `Order` 안에 둡니다.

   ```python
   class Order:
       """Aggregate Root.

       Invariants:
       - 결제 완료 전에는 배송 시작할 수 없다.
       - 배송 시작 후에는 주문 취소할 수 없다.
       - 취소된 주문은 다시 결제할 수 없다.
       """

       def cancel(self) -> None:
           if not self.status.can_cancel():
               raise OrderCannotBeCancelledError(self.id)

           self.status = OrderStatus.CANCELLED
           self._record_event(OrderCancelledEvent(order_id=self.id))
   ```

   여러 애그리거트나 정책이 섞이는 계산이면 Domain Service로 뺍니다.

   ```python
   class DiscountCalculationService:
       def calculate(
           self,
           order_lines: list[OrderLine],
           coupons: list[Coupon],
           member_grade: MemberGrade,
       ) -> Money:
           ...
   ```

6. **Repository는 Aggregate 단위**
   
   `OrderLineRepository`는 보통 만들지 않습니다. `Order`가 Aggregate Root라면 저장/조회도 `OrderRepository` 기준입니다.

   ```python
   class OrderRepository(ABC):
       def find_by_id(self, order_id: OrderId) -> Order | None: ...
       def save(self, order: Order) -> None: ...


   class DjangoOrderRepository(OrderRepository):
       ...
   ```

**권장 네이밍 사전**

| 개념 | 권장 이름 | 금지/주의 이름 | 기준 |
|---|---|---|---|
| 주문 애그리거트 | `Order` | `OrderEntity`, `OrderData` | 도메인 핵심 명사 그대로 |
| 주문 ORM 모델 | `OrderModel` 또는 Django 앱 관례상 `Order` | 도메인 `Order`와 같은 모듈에서 충돌 | 도메인 모델과 ORM 모델을 분리한다면 `OrderModel`이 명확함 |
| 주문 저장소 인터페이스 | `OrderRepository` | `OrderDAO`, `OrderStore` | Aggregate 단위 영속성 Port |
| Django 저장소 구현 | `DjangoOrderRepository` | `OrderRepositoryImpl` | 기술 어댑터를 접두어로 명시 |
| 주문 유스케이스 조율 | `OrderApplicationService` | `OrderService` | 여러 주문 유스케이스를 묶을 때 |
| 주문 생성 유스케이스 | `PlaceOrderHandler` | `OrderUseCase`, `CreateOrderService` | 동사형 유비쿼터스 언어 사용 |
| 주문 취소 정책 | `OrderCancellationPolicy` | `CancelManager` | 규칙/정책이면 Policy |
| 할인 계산 | `DiscountCalculationService` | `OrderDiscountHelper` | 특정 엔티티에 귀속되지 않는 도메인 계산 |
| 읽기 전용 조회 | `order_list`, `get_order_detail`, `OrderQueryService` | `OrderService.get_orders` | Query는 Command와 분리 |

**최종 규칙**

```text
Manager
= Django ORM 확장 전용

ApplicationService
= 여러 유스케이스를 조율하는 애플리케이션 계층 클래스

Handler
= 유스케이스 하나를 처리하는 애플리케이션 계층 클래스

DomainService
= 특정 Aggregate에 넣기 어색한 순수 도메인 규칙

Policy / Calculator / Specification
= 규칙의 성격이 더 구체적일 때 Service보다 우선

Repository
= Aggregate 저장/조회 Port

DjangoXRepository
= Django ORM 기반 Adapter
```

따라서 지금 섞여 있다면 정리 방향은 보통 이렇게 갑니다.

```text
OrderManager
→ ORM 쿼리만 남기고 OrderQuerySet/OrderManager로 제한

OrderService.place_order()
→ OrderApplicationService.place_order()
또는 PlaceOrderHandler.handle()

OrderService.cancel_order()
→ OrderApplicationService.cancel_order()
또는 CancelOrderHandler.handle()

OrderService.calculate_discount()
→ DiscountCalculationService.calculate()
또는 DiscountPolicy.apply()

OrderUseCase
→ PlaceOrderHandler / CancelOrderHandler / ConfirmPaymentHandler
```

Django DDD 프로젝트에서는 **이름이 계층을 말하게 만드는 것**이 중요합니다. `OrderService`처럼 모든 것을 담을 수 있는 이름은 피하고, `PlaceOrderHandler`, `OrderCancellationPolicy`, `DjangoOrderRepository`처럼 책임과 위치가 바로 드러나는 이름을 표준으로 잡는 게 좋습니다.

---
> **관련 스킬 참조:**
> - DDD 책임 분리와 Aggregate 설계 → **architecture-ddd** 스킬
> - Django 계층/서비스/Repository 구현 → **implementation-django** 스킬
> - 의존성 방향과 포트/어댑터 구조 → **architecture-implementation-patterns** 스킬
> - 네이밍과 책임 기반 클래스 분리 → **implementation-cleancode** 스킬