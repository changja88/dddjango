**[주요 내용]**

팀 컨벤션으로는 먼저 이 원칙을 잡는 게 좋습니다: `OrderManager`, `OrderService`, `OrderUseCase`를 같은 문제에 동시에 쓰지 않습니다. 이름이 비슷하면 책임도 겹치고, 결국 “어디에 비즈니스 로직을 넣어야 하지?”가 매번 논쟁이 됩니다.

| 이름 | 책임 | 허용되는 코드 | 금지 |
|---|---|---|---|
| `OrderManager` / `OrderQuerySet` | Django ORM 조회/생성 편의 | 필터, preload, lock, bulk update, DB 친화적 쿼리 | 주문 확정, 결제 승인, 재고 차감 같은 업무 규칙 |
| `PlaceOrderUseCase` | 하나의 사용자/시스템 유스케이스 조율 | 트랜잭션, 권한/입력 조립, 도메인 메서드 호출, repository/save, on_commit | 가격 계산 규칙, 상태 전이 규칙 자체 |
| `OrderService` | 기본적으로 사용 금지. 너무 넓고 모호함 | 예외적으로 `OrderPricingService`, `ShippingFeePolicy`처럼 구체적 도메인 서비스만 허용 | `OrderService.create()`, `OrderService.update_status()` 같은 God Service |

핵심 기준은 이겁니다.

`Manager`는 **DB 접근 언어**입니다.  
`UseCase`는 **애플리케이션 흐름 언어**입니다.  
`Domain Service`는 **특정 엔티티에 넣기 애매한 도메인 규칙 언어**입니다.

예를 들어 주문 확정은 이렇게 나뉩니다.

```python
class OrderQuerySet(models.QuerySet):
    def payable(self):
        return self.filter(status=Order.Status.PENDING)

    def with_lines(self):
        return self.prefetch_related("lines")


class ConfirmOrderUseCase:
    def execute(self, order_id: int) -> None:
        order = self.order_repository.get(order_id)
        order.confirm()
        self.order_repository.save(order)
```

`order.confirm()` 안에는 “어떤 상태에서 확정 가능한가” 같은 불변식이 들어갑니다. `ConfirmOrderUseCase`는 그 규칙을 판단하지 않고, 트랜잭션과 저장 흐름만 조율합니다. `OrderManager.payable()`은 조회 조건만 표현합니다.

프로젝트 규모별 기준은 이렇게 가져가면 과한 추상화를 피할 수 있습니다.

| 규모 | 추천 구조 |
|---|---|
| 단순 CRUD | `Model` + `Manager/QuerySet` + View/Form. `Service`, `UseCase` 만들지 않음 |
| 중간 규모 | 여러 모델 변경, 외부 API, 트랜잭션이 생기면 `services.py`에 함수형 서비스: `order_confirm(...)`, `order_cancel(...)` |
| DDD 적용 규모 | `PlaceOrderUseCase`, `CancelOrderUseCase`, `Order` Aggregate, `OrderRepository`. 이때도 `OrderService`는 피함 |
| 복잡한 도메인 규칙 | `OrderPricingService`, `DiscountPolicy`, `ShippingFeePolicy`처럼 구체 이름의 Domain Service만 도입 |

팀 네이밍 룰은 아래처럼 고정하는 것을 권합니다.

1. Entity 단독 이름 + `Service` 금지  
   `OrderService`, `PaymentService`, `UserService` 금지. 너무 넓습니다.

2. UseCase는 동사 + 목적어  
   `PlaceOrderUseCase`, `CancelOrderUseCase`, `ConfirmPaymentUseCase`.

3. Django Manager/QuerySet 메서드는 조회 의도를 드러냄  
   `for_customer()`, `payable()`, `with_lines()`, `locked_by_id()`.

4. 도메인 메서드는 업무 행위 이름  
   `order.confirm()`, `order.cancel()`, `order.mark_as_paid()`.  
   `update_status()` 같은 CRUD 이름은 피합니다.

5. Domain Service는 규칙 이름으로 명명  
   `OrderPricingService`, `CouponDiscountPolicy`, `ShippingFeeCalculator`.  
   “주문을 처리한다”가 아니라 “가격을 계산한다”처럼 좁아야 합니다.

6. Application Service와 UseCase 중 하나만 선택  
   팀에서 `UseCase`를 쓰기로 했다면 `OrderApplicationService`를 만들지 않습니다.  
   팀에서 `ApplicationService`를 쓰기로 했다면 `PlaceOrderApplicationService`처럼 유스케이스 단위로 이름 붙입니다.

권장 기본안은 이겁니다.

```text
작은 Django 앱:
- Order
- OrderQuerySet / OrderManager
- services.order_confirm()

DDD 앱:
- Order
- OrderRepository
- ConfirmOrderUseCase
- OrderPricingService   # 필요할 때만
```

검증 기준은 PR 리뷰에서 이렇게 보면 됩니다.

```text
- Manager에 if status == ... 같은 업무 규칙이 들어갔는가?
- UseCase가 상태 전이 규칙을 직접 판단하고 있지 않은가?
- OrderService가 5개 이상의 서로 다른 유스케이스를 품고 있지 않은가?
- 이름만 보고 DB 조회인지, 유스케이스 조율인지, 도메인 규칙인지 구분되는가?
```

---
> **관련 스킬 참조:**
> - Django 서비스 레이어와 DDD 책임 분리 → **implementation-django**, **architecture-ddd** 스킬