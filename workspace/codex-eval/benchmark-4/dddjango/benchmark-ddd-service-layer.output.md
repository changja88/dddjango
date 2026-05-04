**주요 내용**

Django 프로젝트에서 application service는 보통 **각 도메인 앱 안의 `application/` 계층**에 두는 게 가장 균형이 좋습니다.

예시:

```text
apps/orders/
  api/
    schemas.py
    router.py
  application/
    services.py
  domain/
    models.py
    repositories.py
    exceptions.py
  infrastructure/
    repositories.py
  models.py              # Django ORM model
```

핵심 기준은 “HTTP도 아니고, ORM도 아니고, 비즈니스 규칙 자체도 아닌 유스케이스 조율 코드”를 application service에 둔다는 것입니다.

Ninja router는 얇게 유지합니다. Router의 책임은 요청 Schema 검증, 인증, path/query/body 파싱, 응답 Schema 변환, HTTP status/error 매핑입니다. 주문 확정, 결제 승인, 재고 차감 같은 흐름을 router 안에 직접 쓰기 시작하면 API 계층이 유스케이스를 소유하게 됩니다.

```python
# apps/orders/api/router.py
from ninja import Router

from apps.orders.api.schemas import ConfirmOrderIn, OrderOut
from apps.orders.application.services import OrderApplicationService

router = Router(tags=["orders"])


@router.post("/{order_id}/confirmation", response={200: OrderOut})
def confirm_order(request, order_id: str, payload: ConfirmOrderIn) -> OrderOut:
    service = OrderApplicationService()
    order = service.confirm_order(order_id=order_id, actor_id=request.user.id)
    return OrderOut.from_domain(order)
```

Application service는 유스케이스를 조율합니다. 트랜잭션 경계를 잡고, repository로 aggregate를 가져오고, domain model 메서드를 호출하고, 저장하고, 커밋 이후 부수효과를 예약합니다. 단, 비즈니스 판단 자체를 여기에 몰아넣으면 빈약한 도메인 모델이 됩니다.

```python
# apps/orders/application/services.py
from django.db import transaction

from apps.orders.domain.repositories import OrderRepository
from apps.orders.infrastructure.repositories import DjangoOrderRepository


class OrderApplicationService:
    def __init__(self, orders: OrderRepository | None = None) -> None:
        self.orders = orders or DjangoOrderRepository()

    @transaction.atomic
    def confirm_order(self, order_id: str, actor_id: int):
        order = self.orders.get(order_id)

        order.confirm(actor_id=actor_id)

        self.orders.save(order)
        events = order.collect_events()

        transaction.on_commit(lambda: publish_events(events))
        return order
```

Domain model은 비즈니스 규칙과 불변식을 지킵니다. 여기에는 `request`, `Schema`, `QuerySet`, `save()`, `transaction.atomic()` 같은 Django/API 관심사가 들어가지 않는 편이 좋습니다.

```python
# apps/orders/domain/models.py
class Order:
    """Invariant: paid order can be confirmed only once."""

    def confirm(self, actor_id: int) -> None:
        if self.is_confirmed:
            raise OrderAlreadyConfirmedError()

        if not self.is_paid:
            raise OrderNotPaidError()

        self.status = OrderStatus.CONFIRMED
        self._record_event(OrderConfirmedEvent(order_id=self.id, actor_id=actor_id))
```

Repository는 domain model과 저장소 사이의 경계입니다. 인터페이스는 사용하는 쪽, 즉 domain/application 쪽에 두고, Django ORM 구현은 infrastructure에 둡니다.

```python
# apps/orders/domain/repositories.py
from abc import ABC, abstractmethod

from apps.orders.domain.models import Order


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> Order: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...
```

```python
# apps/orders/infrastructure/repositories.py
class DjangoOrderRepository(OrderRepository):
    def get(self, order_id: str) -> Order:
        row = OrderModel.objects.get(id=order_id)
        return to_domain(row)

    def save(self, order: Order) -> None:
        row = OrderModel.objects.get(id=order.id)
        apply_domain(row, order)
        row.save(update_fields=["status", "updated_at"])
```

과설계를 피하는 기준은 간단합니다.

단순 CRUD라면 `api/router.py + schemas.py + Django model` 정도로 충분합니다. 읽기 전용 목록/상세 조회는 application service보다 `selectors.py`가 더 낫습니다. 예를 들어 “주문 목록 조회”는 domain aggregate를 만들지 말고 QuerySet 최적화에 집중하는 편이 실용적입니다.

Application service를 도입할 만한 신호는 다음입니다: 하나의 요청에서 여러 모델/aggregate를 조율한다, 트랜잭션 경계가 중요하다, 외부 API/이메일/이벤트 발행이 있다, 상태 전이나 비즈니스 예외가 있다, 같은 유스케이스가 API 외부에서도 재사용된다.

Repository 분리는 도메인 규칙이 의미 있게 커졌을 때 효과가 큽니다. Django ORM 모델이 사실상 데이터 저장만 하고, 비즈니스 규칙을 별도 domain model에서 다룰 필요가 있을 때 분리하세요. 반대로 백오피스 CRUD 수준이면 Django model 메서드와 QuerySet/selector만으로 충분합니다.

검증은 다음 정도면 실무적으로 충분합니다.

```bash
python manage.py test apps.orders
python manage.py check
rg "from apps.orders.api" apps/orders/domain apps/orders/application
rg "objects\\.|\\.save\\(" apps/orders/domain
```

첫 번째는 동작 검증, 두 번째는 Django 설정 검증, 세 번째는 안쪽 계층이 API를 import하지 않는지 확인, 네 번째는 domain model이 ORM 영속성에 새지 않았는지 확인하는 용도입니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬
> - DDD 계층/Repository 설계 → **architecture-ddd** 스킬
> - 레이어 의존성/헥사고날 경계 → **architecture-implementation-patterns** 스킬