# 주문 도메인: Aggregate/Repository를 헥사고날 포트/어댑터로 구조화하기

주문 도메인에서 Aggregate와 Repository가 이미 설계되어 있다면, 핵심은 **의존성 방향을 안쪽(도메인)으로 고정**하면서 포트와 어댑터를 식별하는 것이다. DDD의 전술적 패턴은 헥사고날 아키텍처의 안쪽(Application 핵심)에 자연스럽게 위치하며, Repository 인터페이스가 곧 Driven Port가 된다.

## 1. 포트/어댑터 매핑

헥사고날 아키텍처에서 포트는 "애플리케이션의 목적 있는 대화(purposeful conversation)"를 정의하는 인터페이스다. 주문 도메인을 기준으로 매핑하면 다음과 같다.

| 구분 | Driving (Primary) | Driven (Secondary) |
|---|---|---|
| 방향 | 외부 -> 애플리케이션 | 애플리케이션 -> 외부 |
| 역할 | 애플리케이션을 구동 | 애플리케이션이 구동 |
| 주문 도메인 예시 | REST API, CLI, 테스트 하네스 | DB Repository, 결제 게이트웨이, 알림 서비스 |

### Driving Port (Primary) -- 유스케이스 인터페이스

외부 액터(사용자, 다른 시스템)가 주문 애플리케이션에 요청하는 진입점이다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PlaceOrderCommand:
    orderer_id: str
    items: List[dict]
    shipping_address: dict


@dataclass(frozen=True)
class PlaceOrderResult:
    order_id: str


# --- Driving Port: 주문 유스케이스 인터페이스 ---
class PlaceOrderUseCase(ABC):
    """Driving Port -- 외부 액터가 호출하는 인터페이스"""

    @abstractmethod
    def execute(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        ...


class CancelOrderUseCase(ABC):
    @abstractmethod
    def execute(self, order_id: str) -> None:
        ...


class ShipOrderUseCase(ABC):
    @abstractmethod
    def execute(self, order_id: str) -> None:
        ...
```

### Driven Port (Secondary) -- 인프라 인터페이스

애플리케이션이 외부 시스템에 요청하는 인터페이스다. **Repository 인터페이스가 대표적인 Driven Port**이다. 인터페이스의 소유권은 도메인 계층에 있다 (소유권 역전).

```python
from abc import ABC, abstractmethod
from typing import Optional


# --- Driven Port: 리포지토리 인터페이스 (도메인 계층이 소유) ---
class OrderRepository(ABC):
    """Driven Port -- 애그리거트 단위로 저장/조회
    - OrderLineItem을 위한 별도 리포지토리는 만들지 않는다
    - ORM이 도메인 모델을 임포트하게 하라. 도메인 모델이 ORM을 임포트하면 안 된다.
    """

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...

    @abstractmethod
    def delete(self, order: Order) -> None:
        ...


# --- Driven Port: 외부 결제 서비스 ---
class PaymentGateway(ABC):
    """Driven Port -- 결제 처리를 위한 외부 시스템 인터페이스"""

    @abstractmethod
    def charge(self, order_id: str, amount: Money) -> PaymentResult:
        ...


# --- Driven Port: 이벤트 발행 ---
class DomainEventPublisher(ABC):
    """Driven Port -- 도메인 이벤트를 외부로 발행"""

    @abstractmethod
    def publish(self, events: list) -> None:
        ...
```

## 2. 애플리케이션 핵심 (포트 안쪽)

Aggregate는 도메인 계층에, Application Service는 유스케이스 구현체로서 Driving Port를 구현한다. Application Service는 비즈니스 로직을 직접 구현하지 않고, Aggregate에 위임한다.

```python
class PlaceOrderService(PlaceOrderUseCase):
    """Driving Port 구현 -- 유스케이스 오케스트레이션만 담당
    비즈니스 로직은 Order Aggregate에 위임한다.
    """

    def __init__(
        self,
        order_repository: OrderRepository,       # Driven Port 주입
        member_repository: MemberRepository,      # Driven Port 주입
        event_publisher: DomainEventPublisher,    # Driven Port 주입
    ):
        self._order_repo = order_repository
        self._member_repo = member_repository
        self._event_publisher = event_publisher

    def execute(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        # 1. Driven Port를 통해 필요한 Aggregate 조회
        member = self._member_repo.find_by_id(command.orderer_id)
        if member is None:
            raise ValueError("회원을 찾을 수 없습니다")

        # 2. Aggregate 생성 -- 도메인 로직은 Order 내부에서 수행
        order = Order(
            orderer_id=member.id,
            order_lines=self._build_order_lines(command.items),
            shipping_info=self._build_shipping_info(command.shipping_address),
        )
        order.place()

        # 3. Driven Port를 통해 저장 및 이벤트 발행
        self._order_repo.save(order)
        self._event_publisher.publish(order.collect_domain_events())

        return PlaceOrderResult(order_id=order.id)
```

## 3. 어댑터 (포트 바깥쪽)

### Driving Adapter -- REST Controller

```python
# adapters/driving/rest_api.py
class OrderController:
    """Driving Adapter -- REST 요청을 Driving Port 호출로 변환"""

    def __init__(self, place_order: PlaceOrderUseCase):
        self._place_order = place_order

    def post_order(self, request_body: dict) -> dict:
        command = PlaceOrderCommand(
            orderer_id=request_body["orderer_id"],
            items=request_body["items"],
            shipping_address=request_body["shipping_address"],
        )
        result = self._place_order.execute(command)
        return {"order_id": result.order_id}
```

### Driven Adapter -- DB Repository

```python
# adapters/driven/django_order_repository.py
class DjangoOrderRepository(OrderRepository):
    """Driven Adapter -- Django ORM으로 Driven Port를 구현"""

    def find_by_id(self, order_id: str) -> Optional[Order]:
        try:
            orm_order = OrderModel.objects.get(id=order_id)
            return self._to_domain(orm_order)
        except OrderModel.DoesNotExist:
            return None

    def save(self, order: Order) -> None:
        orm_order = self._to_orm(order)
        orm_order.save()

    def delete(self, order: Order) -> None:
        OrderModel.objects.filter(id=order.id).delete()

    def _to_domain(self, orm_obj) -> Order:
        """ORM 모델 -> 도메인 모델 변환"""
        ...

    def _to_orm(self, domain_obj: Order):
        """도메인 모델 -> ORM 모델 변환"""
        ...
```

## 4. 프로젝트 구조

```
src/
├── ordering/                          # 바운디드 컨텍스트: 주문
│   ├── domain/                        # 도메인 계층 (의존성 없음, 순수 Python)
│   │   ├── model.py                   # Order Aggregate, 값 객체
│   │   ├── events.py                  # OrderPlacedEvent 등 도메인 이벤트
│   │   └── repository.py             # OrderRepository (Driven Port = ABC)
│   │
│   ├── application/                   # 응용 계층
│   │   ├── ports/
│   │   │   └── driving.py            # PlaceOrderUseCase 등 (Driving Port)
│   │   └── services.py               # PlaceOrderService (Driving Port 구현)
│   │
│   ├── adapters/
│   │   ├── driving/                   # Driving Adapter
│   │   │   └── rest_api.py           # REST Controller
│   │   └── driven/                    # Driven Adapter
│   │       ├── django_repository.py  # DjangoOrderRepository
│   │       ├── stripe_payment.py     # StripePaymentGateway
│   │       └── kafka_publisher.py    # KafkaDomainEventPublisher
│   │
│   └── config.py                      # DI 조립 (어댑터 -> 포트 연결)
```

**핵심 의존성 규칙:**
- `domain/` -- 어디에도 의존하지 않는다. 순수 Python만 사용
- `application/` -- `domain/`에만 의존한다
- `adapters/` -- `domain/`과 `application/`에 의존한다 (포트 구현)
- Aggregate는 외부 의존성을 받지 않는다

## 5. DDD 패턴과 헥사고날의 대응 관계

| DDD 개념 | 헥사고날 위치 | 역할 |
|---|---|---|
| Aggregate (Order) | 도메인 계층 (핵심 안쪽) | 비즈니스 불변식 보호, 상태 변경 |
| Repository 인터페이스 | Driven Port (도메인이 소유) | 영속성 추상화 |
| Repository 구현체 | Driven Adapter (바깥쪽) | 구체적 DB 기술 |
| Application Service | Driving Port 구현 | 유스케이스 오케스트레이션 |
| Domain Event | 도메인 계층 | Aggregate 간 결과적 일관성 |
| Event Publisher 인터페이스 | Driven Port | 이벤트 발행 추상화 |
| REST Controller | Driving Adapter (바깥쪽) | HTTP 요청을 커맨드로 변환 |

핵심 원칙: Repository 인터페이스를 도메인 계층에 두는 것 자체가 DIP의 적용이며, 이것이 곧 헥사고날의 Driven Port가 된다. 기존에 설계한 Aggregate와 Repository 인터페이스를 그대로 유지하면서, 어댑터만 바깥쪽에 배치하면 헥사고날 구조가 완성된다.

---
> **관련 스킬 참조:**
> - 헥사고날/클린/CQRS 패턴의 상세 구현과 비교 -> **architecture-implementation-patterns** 스킬
> - Aggregate 설계 규칙, 도메인 이벤트, 바운디드 컨텍스트 -> **architecture-ddd** 스킬
> - Django ORM과 Repository 패턴 통합, 서비스 레이어 구성 -> **implementation-django** 스킬
> - 데이터베이스 스키마 설계, 인덱스, 트랜잭션 관리 -> **architecture-db** 스킬
> - REST API 엔드포인트 설계, 상태 코드, 버저닝 -> **architecture-api** 스킬
