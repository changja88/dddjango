Fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 fixture 파일이 없었습니다. 그래서 파일 수정이나 diff 없이, 지정된 dddjango 지침 기준으로 설명합니다.

**주요 내용**

Django 프로젝트에서 application service는 보통 “Django 앱 내부의 application 계층”에 둡니다. 핵심 기준은 위치 이름보다 책임입니다.

추천 구조는 이렇습니다.

```text
apps/orders/
  api/
    schemas.py
    router.py
  application/
    services.py        # 또는 confirm_order.py 같은 use case 단위 파일
  domain/
    models.py          # Order, Money, 상태 전이, 불변식
    repositories.py    # OrderRepository 인터페이스
  infrastructure/
    repositories.py    # Django ORM 기반 구현
```

작은 기능이면 처음부터 이 구조를 모두 만들 필요는 없습니다. 단순 CRUD이고 도메인 규칙이 거의 없으면 `api/router.py` + `models.py` + 얇은 `services.py` 정도로 충분합니다. 다만 아래 신호가 보이면 application service를 분리하는 편이 좋습니다.

- 하나의 요청이 여러 모델 저장, 외부 API 호출, 알림, 트랜잭션을 조율한다.
- router 함수가 비즈니스 규칙을 직접 판단하기 시작한다.
- Django model 안에 결제, 배송, 재고 같은 다른 관심사가 섞인다.
- 테스트에서 HTTP 요청 없이 use case만 검증하고 싶다.

역할 분리는 이렇게 잡습니다.

`Ninja router`는 입출력 변환에 집중합니다. `Schema`로 요청을 받고 응답 `Schema`로 변환하며, 인증, path/query/body 파싱, HTTP 상태 코드 매핑을 담당합니다. use case 흐름을 길게 쓰지 않습니다.

`application service`는 use case를 조율합니다. 트랜잭션 경계, repository 호출, domain model 메서드 호출, 커밋 후 부수효과 예약 같은 흐름을 담당합니다. 단, “주문은 결제 전 취소 가능하다” 같은 도메인 규칙 자체를 service에 흩뿌리면 빈약한 도메인 모델이 됩니다.

`domain model`은 비즈니스 규칙과 불변식을 가집니다. 상태 전이, 금액 계산, 유효성 검증처럼 도메인 언어로 설명되는 행위는 `order.confirm_payment()` 같은 메서드에 둡니다. ORM 저장 방식이나 HTTP 요청을 몰라야 합니다.

`repository`는 애그리거트 저장/조회 경계입니다. 도메인 또는 application 쪽에 인터페이스를 두고, Django ORM 구현은 infrastructure 쪽에 둡니다. repository는 “테이블별 DAO”가 아니라 `Order` 같은 애그리거트를 저장하고 복원하는 역할입니다.

예시는 최소한으로 보면 이 정도입니다.

```python
# apps/orders/api/router.py
from django.http import HttpRequest
from ninja import Router

from orders.api.schemas import OrderOut, OrderCreateIn
from orders.application.services import OrderApplicationService

router = Router()


@router.post("/", response={201: OrderOut})
def create_order(request: HttpRequest, payload: OrderCreateIn) -> tuple[int, OrderOut]:
    service = OrderApplicationService()
    order = service.create_order(user_id=request.user.id, items=payload.items)
    return 201, OrderOut.from_domain(order)


@router.get("/", response=list[OrderOut])
def list_orders(request: HttpRequest) -> list[OrderOut]:
    service = OrderApplicationService()
    return [OrderOut.from_domain(order) for order in service.list_orders(request.user.id)]
```

```python
# apps/orders/application/services.py
from django.db import transaction

from orders.domain.repositories import OrderRepository
from orders.infrastructure.repositories import DjangoOrderRepository


class OrderApplicationService:
    def __init__(self, repository: OrderRepository | None = None) -> None:
        self.repository = repository or DjangoOrderRepository()

    @transaction.atomic
    def create_order(self, user_id: int, items: list[dict]) -> "Order":
        order = Order.create(user_id=user_id, items=items)
        self.repository.save(order)
        return order

    def list_orders(self, user_id: int) -> list["Order"]:
        return self.repository.find_by_user_id(user_id)
```

```python
# apps/orders/domain/repositories.py
from abc import ABC, abstractmethod


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: "Order") -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_user_id(self, user_id: int) -> list["Order"]:
        raise NotImplementedError
```

핵심은 router가 “HTTP 어댑터”, application service가 “use case 조율자”, domain model이 “규칙의 주인”, repository가 “영속성 경계”라는 점입니다. 작은 기능에서는 `application/services.py` 하나로 시작하고, 규칙과 변경 이유가 분명히 갈라질 때만 `domain/`, `infrastructure/`를 더 세분화하는 게 낫습니다.

검증은 코드가 생긴 뒤 다음 정도를 봅니다.

```bash
python manage.py check
pytest
```

API가 추가되었다면 Ninja `TestClient`로 router가 service를 호출하는지, domain 규칙은 HTTP 없이 단위 테스트 가능한지도 확인합니다.

---
> **관련 스킬 참조:**
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬
> - application service / repository 경계 → **architecture-implementation-patterns** 스킬
> - domain model 책임 설계 → **architecture-ddd** 스킬