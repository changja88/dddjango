**주요 내용**

현재 workspace에는 실제 Django 프로젝트 파일이 없어서, Django Ninja + dddjango 기준의 일반 권장 구조로 답하겠습니다.

Django Ninja 프로젝트에서 service layer는 **API 라우터 옆이 아니라 도메인 앱 내부**에 두는 것이 좋습니다. 핵심은 `Router`는 HTTP 입출력 변환만 하고, 유스케이스 실행은 서비스가 맡게 하는 것입니다.

가장 실용적인 기본 구조는 이렇습니다.

```text
apps/
  orders/
    models.py
    services.py       # 쓰기/명령 로직: order_create, order_confirm
    selectors.py      # 읽기/조회 로직: order_list, order_detail
    schemas.py        # Django Ninja 요청/응답 Schema
    api.py            # Router, HTTP status, auth, schema 변환
```

역할은 이렇게 나누면 됩니다.

```text
api.py
  - request/body/path/query를 받는다
  - Schema로 검증한다
  - service 또는 selector를 호출한다
  - HTTP status와 response schema로 변환한다

services.py
  - 쓰기 유스케이스를 처리한다
  - 여러 모델 변경, transaction.atomic, 외부 알림 예약 등을 담당한다
  - 네이밍은 order_create, order_confirm, user_register 처럼 <entity>_<action>

selectors.py
  - 읽기 전용 QuerySet 조립을 담당한다
  - select_related, prefetch_related, filter, annotate 등을 모은다

models.py
  - 단일 모델의 불변식과 상태 전이 메서드
  - 예: order.confirm(), order.cancel()
```

예를 들면 `api.py`는 얇게 둡니다.

```python
from ninja import Router

from .schemas import OrderCreateIn, OrderOut
from .services import order_create
from .selectors import order_detail

router = Router()


@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderCreateIn) -> tuple[int, OrderOut]:
    order = order_create(user=request.user, data=payload)
    return 201, order


@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: int) -> OrderOut:
    return order_detail(order_id=order_id, user=request.user)
```

규모가 커지고 DDD 경계를 명확히 가져가야 한다면, 앱 하나를 바운디드 컨텍스트로 보고 더 분리합니다.

```text
applications/
  orders/
    domain_layer/
      order/
        root.py
        value_objects.py
        events.py
      service/
        pricing/
      repository/
        order_repo.py        # Repository ABC
    application_layer/
      order_service.py       # 유스케이스 조율
    infra_layer/
      django_orders/
        models/
      repository/
        order_repo.py        # Django ORM 구현체
    presentation_layer/
      api/
        order_api.py         # Django Ninja Router
      schema/
        order_schema.py
```

이때도 “service layer”라는 이름 하나로 뭉개지 말고 둘을 구분하는 게 좋습니다.

```text
application_layer/*_service.py
  - 응용 서비스
  - 트랜잭션, repository 조회/저장, 유스케이스 흐름 조율
  - 비즈니스 규칙 자체는 직접 구현하지 않음

domain_layer/service/
  - 도메인 서비스
  - 특정 엔티티/값 객체에 넣기 애매한 순수 도메인 계산
  - 상태 없는 로직
```

실무 권장 순서는 이렇습니다.

1. 처음에는 `apps/<domain>/services.py` + `selectors.py`로 시작합니다.
2. 라우터가 비대해지면 먼저 `services.py`로 쓰기 로직을 뺍니다.
3. 조회 쿼리가 복잡해지면 `selectors.py`로 분리합니다.
4. 여러 애그리거트, 복잡한 불변식, 외부 시스템 통합이 많아지면 `application_layer`, `domain_layer`, `infra_layer`, `presentation_layer` 구조로 확장합니다.

피해야 할 위치는 명확합니다.

```text
config/api.py              # 라우터 합성만 담당
apps/orders/api.py         # HTTP 변환만 담당
apps/orders/schemas.py     # 데이터 검증/직렬화만 담당
shared/services.py         # 도메인별 책임이 흐려지기 쉬움
```

정리하면, **대부분의 Django Ninja 프로젝트는 앱 내부의 `services.py`와 `selectors.py`가 가장 좋은 출발점**입니다. DDD를 본격 적용하는 프로젝트라면 **유스케이스 서비스는 `application_layer`, 순수 도메인 서비스는 `domain_layer/service`**에 둡니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 계층 분리 → **implementation-django-ninja** 스킬
> - Django 서비스/셀렉터 패턴 → **implementation-django** 스킬
> - 응용 서비스와 도메인 서비스 구분 → **architecture-ddd** 스킬
> - 레이어/헥사고날 구조 확장 → **architecture-implementation-patterns** 스킬