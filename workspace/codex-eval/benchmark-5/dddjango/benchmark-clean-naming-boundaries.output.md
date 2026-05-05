**[주요 내용]**

Fixture 확인 결과 `/Users/hyun/Desktop/dddjango/none` 경로는 존재하지 않았습니다. 따라서 기존 코드 리뷰나 diff는 만들 수 없고, 팀 컨벤션으로 바로 쓸 수 있는 책임/네이밍 기준으로 정리합니다.

핵심 원칙은 하나입니다: `OrderManager`, `OrderService`, `OrderUseCase`처럼 “Order + 계층명”만 붙이면 책임이 드러나지 않습니다. 이름은 **무엇을 조율하는지**, **어떤 변경 이유를 갖는지**가 보여야 합니다.

| 이름 | 허용 기준 | 책임 | 금지 |
|---|---|---|---|
| `OrderManager` | Django ORM 진입점일 때만 | QuerySet 생성, 공통 필터, eager loading, lock query | 결제 호출, 이메일, 상태 전이 규칙, 트랜잭션 흐름 |
| `OrderQuerySet` | 체이닝 가능한 조회 조건 | `paid()`, `for_customer()`, `with_lines()` | 비즈니스 커맨드 실행 |
| `OrderService` | 기본적으로 금지. 너무 모호함 | 정말 필요하면 더 구체적 이름 사용 | “주문 관련 로직 모음” |
| `PlaceOrderUseCase` | 사용자/시스템 유스케이스 1개 조율 | 입력 검증, 트랜잭션, repository 호출, domain method 호출, on_commit 부수효과 예약 | 도메인 규칙 직접 구현 |
| `OrderDomainService` | 특정 엔티티/VO에 넣기 어려운 도메인 규칙일 때만 | 여러 애그리거트/정책이 필요한 순수 도메인 판단 | DB, HTTP, SDK, Django request 접근 |
| `OrderApplicationService` | 여러 use case를 한 클래스에 묶을 명확한 이유가 있을 때 | 유스케이스 오케스트레이션 | God service |

팀 컨벤션은 이렇게 잡는 것을 권합니다.

1. Django ORM 쿼리는 `OrderQuerySet` / `OrderManager`
2. 읽기 전용 화면/API 조회는 `orders/selectors.py`
3. 단순 커맨드는 `orders/services.py`의 함수형 네이밍
4. 복잡한 DDD 흐름은 `PlaceOrderUseCase`, `CancelOrderUseCase`처럼 동사 기반 UseCase
5. `OrderService`, `OrderUseCase` 같은 포괄명은 금지

프로젝트 규모별 기준은 다르게 둬야 합니다.

**작은 CRUD Django 앱**

서비스/유스케이스를 만들지 않습니다.

```python
class OrderQuerySet(models.QuerySet):
    def paid(self):
        return self.filter(status=Order.Status.PAID)

class Order(models.Model):
    objects = OrderQuerySet.as_manager()

    def cancel(self):
        if self.status == self.Status.SHIPPED:
            raise OrderAlreadyShippedError()
        self.status = self.Status.CANCELED
```

이 단계에서는 모델 메서드와 QuerySet이면 충분합니다. `OrderService`를 만들면 오히려 흐름이 흩어집니다.

**중간 규모 Django 앱**

뷰가 두꺼워지거나 트랜잭션/부수효과가 섞이면 command는 `services.py`, query는 `selectors.py`로 나눕니다.

```python
# orders/services.py
@transaction.atomic
def order_cancel(*, order_id: int, actor: User) -> None:
    order = Order.objects.select_for_update().get(id=order_id)
    order.cancel_by(actor)
    order.save(update_fields=["status"])
    transaction.on_commit(lambda: notify_order_canceled(order.id))
```

함수명은 Django 서비스 레이어에서는 `<entity>_<action>`를 기본으로 합니다. `OrderService.cancel()`보다 `order_cancel()`이 검색성과 의도가 낫습니다.

**복잡한 DDD 앱**

도메인 규칙은 애그리거트에 두고, UseCase는 조율만 합니다.

```python
class PlaceOrderUseCase:
    def execute(self, command: PlaceOrderCommand) -> OrderId:
        order = Order.place(
            customer_id=command.customer_id,
            lines=command.lines,
        )
        self.orders.save(order)
        return order.id
```

UseCase 이름은 반드시 유저 목표를 드러냅니다. `OrderUseCase` 금지, `PlaceOrderUseCase` 허용입니다.

최종 네이밍 규칙은 다음처럼 문서화하면 됩니다.

| 패턴 | 예시 |
|---|---|
| QuerySet method | `paid()`, `for_customer(customer_id)`, `with_lines()` |
| Selector | `order_get_detail()`, `order_list_for_customer()` |
| Service function | `order_cancel()`, `order_mark_paid()` |
| UseCase class | `PlaceOrderUseCase`, `CancelOrderUseCase` |
| Command DTO | `PlaceOrderCommand`, `CancelOrderCommand` |
| Domain method | `order.cancel()`, `order.mark_paid()` |
| Domain service/policy | `OrderPricingPolicy`, `ShippingEligibilityPolicy` |
| 금지명 | `OrderService`, `OrderUseCase`, `OrderManager`에 비즈니스 흐름 넣기 |

검증 기준:

```bash
rg "class OrderService|class OrderUseCase|class .*Manager" .
rg "transaction.atomic|on_commit|requests\\.|stripe|toss|send_mail" apps/orders
```

확인할 점은 단순합니다. `Manager` 안에 외부 호출이나 상태 전이 흐름이 있으면 빼고, `Service/UseCase` 이름이 명사형 포괄명이라면 유스케이스 동사형으로 바꿉니다.

---
> **관련 스킬 참조:**
> - Django 서비스 레이어와 selectors 분리 → **implementation-django** 스킬
> - UseCase/Application Service/Domain Service 책임 분리 → **architecture-ddd** 스킬