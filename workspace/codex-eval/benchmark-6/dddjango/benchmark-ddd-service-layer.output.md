fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 fixture 파일은 없었습니다. 코드 변경은 하지 않고 설명만 정리합니다.

**주요 내용**

Django 프로젝트에서 application service는 보통 각 도메인 앱 안의 `application` 계층에 둡니다.

```text
apps/orders/
  api/
    router.py
    schemas.py
  application/
    services.py
  domain/
    models.py
    repositories.py
  infrastructure/
    django_repositories.py
```

핵심 기준은 “use case를 조율하는 코드”를 application service에 둔다는 점입니다. 예를 들어 `주문 생성`, `입찰 등록`, `결제 확정`처럼 한 요청이 도메인 객체 로드, 규칙 실행, 저장, 트랜잭션, 후속 작업을 묶어야 하면 application service가 맞습니다.

Ninja router는 입출력 변환에 집중합니다. `HttpRequest`, `Schema`, URL 파라미터, HTTP 상태, 인증 컨텍스트를 다루고, 실제 유스케이스는 service에 위임합니다. router 안에서 ORM 조회, 상태 전이, 외부 API 호출, 트랜잭션 조율이 늘어나면 Fat endpoint가 됩니다.

```python
# apps/orders/api/router.py
from django.http import HttpRequest
from ninja import Router

from apps.orders.api.schemas import OrderCreateIn, OrderOut
from apps.orders.application.services import OrderApplicationService

router = Router()


@router.post("/", response=OrderOut)
def create_order(request: HttpRequest, payload: OrderCreateIn) -> OrderOut:
    service = OrderApplicationService()
    order = service.create_order(
        customer_id=request.user.id,
        lines=payload.lines,
    )
    return OrderOut.from_domain(order)


@router.get("/", response=list[OrderOut])
def list_orders(request: HttpRequest) -> list[OrderOut]:
    service = OrderApplicationService()
    return [OrderOut.from_domain(order) for order in service.list_orders(request.user.id)]
```

Application service는 use case의 흐름을 조율합니다. 트랜잭션 경계, repository 호출, domain model 메서드 호출, 저장, `transaction.on_commit()` 같은 커밋 이후 부수효과를 다룹니다. 다만 핵심 도메인 규칙을 service에 몰아넣으면 빈약한 도메인 모델이 됩니다.

```python
# apps/orders/application/services.py
from django.db import transaction

from apps.orders.domain.models import Order
from apps.orders.infrastructure.django_repositories import DjangoOrderRepository


class OrderApplicationService:
    def __init__(self, repository: DjangoOrderRepository | None = None) -> None:
        self.repository = repository or DjangoOrderRepository()

    def create_order(self, customer_id: int, lines: list[dict]) -> Order:
        with transaction.atomic():
            order = Order.create(customer_id=customer_id, lines=lines)
            self.repository.save(order)
            return order
```

Domain model은 비즈니스 규칙과 불변식을 지킵니다. 예를 들어 “빈 주문은 만들 수 없다”, “결제 완료 주문은 취소할 수 없다”, “입찰가는 현재가보다 높아야 한다” 같은 규칙은 router나 repository가 아니라 domain model의 메서드에 있어야 합니다.

Repository는 저장소 경계입니다. 애그리거트 단위로 `get`, `save` 같은 의도를 제공하고, Django ORM 세부사항을 숨깁니다. repository 안에는 비즈니스 규칙을 넣지 않습니다. 복잡한 도메인에서는 repository 인터페이스를 `domain/repositories.py`에 두고 Django 구현체를 `infrastructure/django_repositories.py`에 둡니다.

작은 기능에서는 과설계를 피해도 됩니다. 단순 CRUD이고 도메인 규칙이 거의 없으며 한 모델만 읽고 쓰는 수준이면 `apps/orders/services.py` 하나로 시작해도 충분합니다. 분리 기준은 파일 개수가 아니라 변경 이유입니다. router가 HTTP와 유스케이스를 동시에 처리하거나, service가 규칙과 저장소 세부사항을 동시에 알거나, 같은 도메인 규칙이 여러 endpoint에 중복되기 시작하면 `api / application / domain / infrastructure`로 나누는 편이 좋습니다.

검증할 때는 다음을 보면 됩니다.

```bash
python manage.py check
pytest
```

리뷰 기준은 간단합니다. Ninja router에 ORM과 상태 전이가 많이 있으면 application service로 옮깁니다. application service에 핵심 비즈니스 조건문이 많으면 domain model 메서드로 옮깁니다. domain model이 `HttpRequest`, `Schema`, `QuerySet`, 외부 SDK를 알면 경계가 새고 있는 것입니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 경계 설계 → **implementation-django-ninja** 스킬
> - Repository/Application Service 계층 분리 → **architecture-implementation-patterns** 스킬