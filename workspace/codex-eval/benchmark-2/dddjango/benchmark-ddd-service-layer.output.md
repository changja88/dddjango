**주요 내용**

Django 프로젝트에서 application service는 “Django 앱 내부의 application 계층”에 두는 게 가장 무난합니다. 전역 `services/` 폴더보다 바운디드 컨텍스트 또는 Django app 기준으로 붙이는 편이 응집도가 좋습니다.

예시 구조:

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
  infrastructure/
    repositories.py
```

핵심 역할은 이렇게 나누면 됩니다.

`Ninja Router`는 HTTP 입출력 변환에 집중합니다. `Schema`로 요청을 검증하고, application service를 호출하고, 결과를 응답 `Schema`로 변환합니다. 비즈니스 규칙, 트랜잭션 흐름, ORM 조합을 router에 넣기 시작하면 endpoint가 use case를 먹어버립니다.

`Application Service`는 use case를 조율합니다. 트랜잭션 경계, repository 호출, domain model 메서드 호출, 도메인 이벤트 수집, `transaction.on_commit()` 부수효과 예약 같은 “절차”를 담당합니다. 단, 할인 계산, 주문 확정 가능 여부 같은 비즈니스 판단 자체는 domain model 안에 있어야 합니다.

`Domain Model`은 비즈니스 규칙과 불변식을 가집니다. Django `request`, Ninja `Schema`, ORM `.save()`를 몰라야 합니다.

`Repository`는 aggregate 저장/조회 책임입니다. 인터페이스는 도메인 언어로 정의하고, 구현은 Django ORM을 사용하는 infrastructure에 둡니다. 테이블 단위가 아니라 aggregate 단위로 잡습니다.

작은 예시는 이 정도면 충분합니다.

```python
# apps/orders/domain/repositories.py
from typing import Protocol
from .models import Order, OrderId

class OrderRepository(Protocol):
    def get(self, order_id: OrderId) -> Order: ...
    def save(self, order: Order) -> None: ...
```

```python
# apps/orders/application/services.py
from django.db import transaction
from apps.orders.domain.models import OrderId
from apps.orders.domain.repositories import OrderRepository

class ConfirmOrderService:
    def __init__(self, orders: OrderRepository) -> None:
        self.orders = orders

    @transaction.atomic
    def confirm(self, order_id: OrderId) -> None:
        order = self.orders.get(order_id)
        order.confirm()
        self.orders.save(order)
```

```python
# apps/orders/api/router.py
from ninja import Router, Schema
from apps.orders.application.services import ConfirmOrderService
from apps.orders.infrastructure.repositories import DjangoOrderRepository

router = Router()

class ConfirmOrderIn(Schema):
    order_id: str

@router.post("/orders/confirm", response={204: None})
def confirm_order(request, payload: ConfirmOrderIn):
    service = ConfirmOrderService(DjangoOrderRepository())
    service.confirm(order_id=payload.order_id)
    return 204, None
```

실제 REST 설계라면 URL은 동사보다 리소스 중심으로 다듬는 편이 좋습니다. 예를 들어 `POST /orders/{order_id}/confirmation`처럼 표현할 수 있습니다. 중요한 점은 URL 이름보다 router가 “HTTP 어댑터” 역할에 머무르는 것입니다.

과설계를 피하는 기준은 단순합니다.

CRUD에 가깝고 규칙이 거의 없으면 `api/router.py + schemas.py + selectors.py` 정도로 시작해도 됩니다. 모델 메서드 하나로 충분한 규칙을 굳이 `domain/`, `application/`, `infrastructure/`까지 나누지 않아도 됩니다.

다만 다음 신호가 보이면 application service를 분리하는 게 맞습니다.

- 하나의 요청에서 여러 모델/aggregate를 조율한다.
- 트랜잭션 경계가 중요하다.
- 외부 API, 이메일, 이벤트 발행 같은 부수효과가 있다.
- 같은 use case가 API, admin command, Celery task 등 여러 entrypoint에서 재사용된다.
- router가 20~30줄을 넘으며 절차적 흐름을 갖기 시작한다.
- 도메인 규칙을 테스트하려는데 HTTP나 DB 준비가 계속 필요하다.

검증은 이렇게 보면 됩니다.

```text
1. router에 비즈니스 if 문이 쌓이지 않는가?
2. domain model이 Django request, Ninja Schema, ORM save를 import하지 않는가?
3. application service가 use case 흐름과 transaction을 명확히 갖는가?
4. repository 구현만 ORM을 알고, interface는 aggregate 언어를 쓰는가?
5. 작은 CRUD에 불필요한 계층을 강제하지 않았는가?
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬
> - Repository/Application Service 분리 → **architecture-implementation-patterns** 스킬
> - Domain Model 책임 설계 → **architecture-ddd** 스킬