**결론**

Django Ninja 프로젝트에서 service layer는 `Router` 옆이 아니라 **앱의 application layer**에 두는 게 가장 무난합니다.

추천 구조는 이렇습니다.

```text
orders/
  api/
    router.py        # Django Ninja Router: HTTP 입출력
    schemas.py       # Ninja Schema: 요청/응답 검증
  application/
    services.py      # 유스케이스 조율
    commands.py      # 요청 의도를 표현하는 DTO
  domain/
    models.py        # 도메인 모델: 규칙, 상태 전이, 불변식
    repositories.py  # Repository 인터페이스
  infrastructure/
    repositories.py  # Django ORM 기반 Repository 구현
```

**책임 분리**

`api/router.py`는 HTTP 경계입니다. 인증, path/query/body 파싱, `Schema` 검증, 상태 코드, 응답 변환만 담당하고 비즈니스 판단은 하지 않습니다.

```python
# orders/api/router.py
from ninja import Router

from orders.api.schemas import CreateOrderIn, OrderOut
from orders.application.commands import CreateOrderCommand
from orders.application.services import OrderApplicationService
from orders.infrastructure.repositories import DjangoOrderRepository

router = Router(tags=["orders"])


@router.post("/", response={201: OrderOut})
def create_order(request, payload: CreateOrderIn) -> tuple[int, OrderOut]:
    service = OrderApplicationService(order_repo=DjangoOrderRepository())

    order = service.create_order(
        CreateOrderCommand(
            customer_id=payload.customer_id,
            lines=payload.lines,
        )
    )

    return 201, OrderOut.from_domain(order)
```

`application/services.py`는 유스케이스를 조율합니다. 트랜잭션 경계, repository 호출, 도메인 모델 메서드 호출, 이벤트 발행 연결은 여기 둡니다. 단, 도메인 규칙 자체를 여기에 쓰면 service layer가 비대해집니다.

```python
# orders/application/services.py
from dataclasses import dataclass
from django.db import transaction

from orders.application.commands import CreateOrderCommand
from orders.domain.models import Order
from orders.domain.repositories import OrderRepository


@dataclass
class OrderApplicationService:
    order_repo: OrderRepository

    @transaction.atomic
    def create_order(self, command: CreateOrderCommand) -> Order:
        order = Order.create(
            customer_id=command.customer_id,
            lines=command.lines,
        )
        self.order_repo.save(order)
        return order
```

`domain/models.py`는 비즈니스 규칙을 가집니다. 예를 들어 주문 생성 가능 여부, 상태 전이, 금액 계산, 취소 가능 조건 같은 것은 application service가 아니라 도메인 모델에 있어야 합니다.

`domain/repositories.py`는 “저장소가 무엇을 해줘야 하는가”를 정의합니다. Django ORM을 직접 아는 구현은 `infrastructure/repositories.py`에 둡니다.

```python
# orders/domain/repositories.py
from abc import ABC, abstractmethod

from orders.domain.models import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        ...
```

**규모별 판단 기준**

작은 CRUD 프로젝트라면 `orders/services.py` 하나로 시작해도 됩니다. 단순 목록, 상세, 생성 정도이고 재사용되는 유스케이스나 트랜잭션 조율이 거의 없다면 Router에서 ORM을 바로 호출하는 것도 현실적으로 괜찮습니다. 대신 Router가 길어지기 시작하면 바로 분리합니다.

중간 규모라면 `api/`, `application/`, `domain/`, `infrastructure/`로 나누는 편이 좋습니다. 여러 엔드포인트가 같은 유스케이스를 공유하거나, 트랜잭션이 필요하거나, 외부 API/이벤트/권한 규칙이 붙으면 application service를 둡니다.

복잡한 도메인이라면 repository 인터페이스는 domain 또는 application이 소유하고, Django ORM 구현은 infrastructure에 둡니다. 도메인 모델은 저장 방법을 몰라야 하고, repository는 애그리거트 저장/조회 책임만 가져야 합니다. 테이블별 repository보다 `OrderRepository`, `AuctionRepository`처럼 애그리거트 단위가 낫습니다.

**검증 기준**

확인할 것은 네 가지입니다.

```text
1. Router가 Ninja Schema와 HTTP만 다루는가?
2. Application service가 유스케이스 조율만 하고 도메인 규칙을 직접 판단하지 않는가?
3. Domain model이 핵심 비즈니스 규칙과 상태 전이를 가지고 있는가?
4. Repository가 ORM 세부사항을 숨기고 애그리거트 단위로 저장/조회하는가?
```

현 워크스페이스에서는 `config.toml` 파일을 찾을 수 없어 프로젝트별 추가 규칙은 확인하지 못했습니다.

---
> **관련 스킬 참조:**
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬
> - service/repository 책임 분리와 DDD 경계 → **architecture-ddd** 스킬
> - layered/hexagonal 구조 선택 기준 → **architecture-implementation-patterns** 스킬