**[주요 내용]**

Django Ninja 프로젝트의 service layer는 **Router 옆이 아니라 앱/바운디드 컨텍스트 내부의 application layer**에 두는 게 가장 좋습니다. 핵심은 위치보다 책임입니다.

권장 구조는 규모에 따라 다릅니다.

```text
apps/orders/
  api.py                    # Django Ninja Router: HTTP 입출력만
  schemas.py                # Django Ninja Schema: request/response 검증
  selectors.py              # read-only 조회
  application/
    services.py             # use case 조율
  domain/
    models.py               # 도메인 규칙, 상태 전이, 불변식
    repositories.py         # Repository interface
  infrastructure/
    django_repositories.py  # Django ORM 구현체
```

작은 CRUD 앱이면 이렇게 줄여도 됩니다.

```text
apps/orders/
  api.py
  schemas.py
  services.py
  selectors.py
```

기준은 이렇습니다.

- **단순 CRUD**: service layer 없이 `api.py` + `schemas.py` + `selectors.py`로 충분합니다.
- **트랜잭션, 여러 모델 조합, 외부 API, 이메일/알림, 권한 정책**이 있으면 `services.py`를 둡니다.
- **도메인 규칙, 상태 전이, 불변식**이 중요하면 `application/services.py`, `domain/`, `infrastructure/`로 나눕니다.
- **여러 앱에서 공유되는 서비스**를 `common/services.py` 같은 곳에 두는 것은 피합니다. 대부분 바운디드 컨텍스트 경계가 흐려집니다.

Router는 application service를 호출만 해야 합니다.

```python
# apps/orders/api.py
from ninja import Router

from .application.services import OrderApplicationService
from .infrastructure.django_repositories import DjangoOrderRepository
from .schemas import OrderCreateIn, OrderOut

router = Router()


@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderCreateIn) -> tuple[int, OrderOut]:
    service = OrderApplicationService(
        orders=DjangoOrderRepository(),
    )
    order = service.create_order(
        user_id=request.user.id,
        items=payload.items,
    )
    return 201, OrderOut.from_domain(order)
```

Application service는 유스케이스를 조율합니다. HTTP, Ninja Schema, request 객체를 몰라야 합니다.

```python
# apps/orders/application/services.py
from django.db import transaction

from apps.orders.domain.repositories import OrderRepository


class OrderApplicationService:
    def __init__(self, orders: OrderRepository) -> None:
        self.orders = orders

    @transaction.atomic
    def create_order(self, user_id: int, items: list[dict]) -> "Order":
        order = Order.create(user_id=user_id, items=items)
        self.orders.save(order)
        return order
```

도메인 모델은 비즈니스 규칙을 가집니다. 저장을 직접 하지 않습니다.

```python
# apps/orders/domain/models.py
class Order:
    def __init__(self, user_id: int, items: list[dict]) -> None:
        self.user_id = user_id
        self.items = items

    @classmethod
    def create(cls, user_id: int, items: list[dict]) -> "Order":
        if not items:
            raise EmptyOrderError()
        return cls(user_id=user_id, items=items)
```

Repository는 도메인이 원하는 영속성 계약입니다. ORM 구현은 infrastructure에 둡니다.

```python
# apps/orders/domain/repositories.py
from typing import Protocol


class OrderRepository(Protocol):
    def save(self, order: "Order") -> None: ...
```

정리하면: **Django Ninja Router는 얇게, application service는 유스케이스 조율, domain model은 규칙, repository는 영속성 경계**를 맡기면 됩니다. 처음부터 헥사고날 구조를 강제하지 말고, 복잡도가 생길 때 `services.py` → `application/domain/infrastructure`로 확장하는 방식이 가장 실용적입니다.

검증할 때는 다음을 보면 됩니다.

```bash
python manage.py test
python manage.py check
```

API 테스트에서는 `ninja.testing.TestClient`로 router 응답을 확인하고, application service는 HTTP 없이 단위 테스트로 검증하세요.

---
> **관련 스킬 참조:**
> - Django Ninja Router/Schema 구현 → **implementation-django-ninja** 스킬
> - Django service layer와 selectors → **implementation-django** 스킬
> - application service, domain model, repository 책임 분리 → **architecture-ddd** 스킬