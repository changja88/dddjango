# D12: architecture-implementation-patterns + architecture-ddd 연동 테스트

**Prompt:** "헥사고날 아키텍처에서 도메인 레이어의 모델을 어떻게 설계해야 해? 애그리거트 경계를 잘 잡고 싶은데."

**Primary Skill:** architecture-implementation-patterns (설계 모드)
**Delegated Skill:** architecture-ddd (애그리거트 설계, 전술적 패턴)

---

## 응답

헥사고날 아키텍처에서 도메인 레이어를 설계할 때, 아키텍처 구조와 도메인 모델링은 별개의 관심사이지만 밀접하게 연결된다. 아키텍처 스타일은 의존성 방향과 계층 경계를 정의하고, 도메인 모델링은 그 안쪽 계층의 내부 구조를 결정한다.

### 1단계: 헥사고날 구조에서 도메인의 위치 확정

헥사고날 아키텍처에서 도메인 모델은 가장 안쪽에 위치한다. 핵심 원칙은 **의존성이 항상 안쪽을 향한다**는 것이다. 도메인은 인프라를 모르고, 포트(인터페이스)를 통해서만 외부와 소통한다.

```
adapters/
  driving/         # REST Controller, CLI, Test Harness
  driven/          # DB Adapter, 외부 API Adapter, Mock
application/
  ports/
    driving/       # Use Case 인터페이스 (외부 -> 애플리케이션)
    driven/        # Repository 인터페이스 등 (애플리케이션 -> 외부)
  services/        # 응용 서비스 (유스케이스 오케스트레이션)
domain/
  model/           # 애그리거트, 엔티티, 값 객체
  services/        # 도메인 서비스
  events/          # 도메인 이벤트
```

여기서 `application/ports/driven/`에 정의되는 리포지토리 인터페이스는 **사용하는 계층(도메인/애플리케이션)이 소유**한다. 구현체는 `adapters/driven/`에 위치한다. 이것이 소유권 역전(Ownership Inversion)이다.

### 2단계: 애그리거트 경계 설계 -- Vernon의 4가지 규칙

도메인 레이어 내부 구조는 DDD 전술적 패턴으로 조직한다. 애그리거트 경계를 잡을 때 Vernon의 4가지 규칙을 적용한다.

**규칙 1. 진짜 불변식을 일관성 경계 안에서 보호하라**

하나의 트랜잭션에서는 하나의 애그리거트만 수정한다. "주문에는 최소 하나의 주문 항목이 있어야 한다"는 불변식이라면, `Order`와 `OrderLineItem`은 같은 애그리거트에 속해야 한다.

**규칙 2. 작은 애그리거트를 설계하라**

루트 엔티티와 최소한의 값 객체로 제한한다. 불변식을 유지하는 데 필요한 만큼만 포함하고, 그 이상은 포함하지 않는다.

```python
# 나쁜 예: 너무 큰 애그리거트
@dataclass
class BigProduct:
    id: str
    name: str
    reviews: List[Review]       # 수천 건 -- 불변식과 무관
    images: List[ProductImage]  # 별도 관심사
    inventory: Inventory        # 별도 관심사

# 좋은 예: 분리된 작은 애그리거트
@dataclass
class Product:
    id: str
    name: str
    description: str
    price: Money  # 값 객체

@dataclass
class ProductReview:
    id: str
    product_id: str   # ID로만 참조 (규칙 3)
    reviewer_id: str
    rating: int
    content: str
```

**규칙 3. 다른 애그리거트는 ID로만 참조하라**

직접 객체 참조 대신 식별자로 참조하면 결합도가 낮아지고, 로딩 시간과 메모리 사용이 줄어든다.

**규칙 4. 일관성 경계 밖에서는 결과적 일관성을 사용하라**

서로 다른 애그리거트 간의 일관성은 도메인 이벤트를 통한 결과적 일관성(eventual consistency)으로 달성한다.

```python
@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    customer_id: str
    total_amount: int
    occurred_at: datetime

@dataclass
class Order:
    """주문 애그리거트 루트"""
    id: str = field(default_factory=lambda: str(uuid4()))
    orderer_id: str = ""          # Member를 ID로만 참조
    order_lines: List[OrderLineItem] = field(default_factory=list)
    shipping_info: ShippingInfo = None
    _status: OrderStatus = field(default=OrderStatus.PAYMENT_WAITING)
    _events: List = field(default_factory=list)

    def __post_init__(self):
        self._verify_at_least_one_order_line()  # 불변식 보호

    def place(self) -> None:
        """주문 접수 -- 이벤트를 발행하여 결과적 일관성 구현"""
        if self._status != OrderStatus.PAYMENT_WAITING:
            raise ValueError("결제 대기 상태에서만 접수할 수 있습니다")
        self._status = OrderStatus.PREPARING
        self._events.append(
            OrderPlacedEvent(
                order_id=self.id,
                customer_id=self.orderer_id,
                total_amount=self._total_amounts.amount,
                occurred_at=datetime.now(),
            )
        )
```

### 3단계: 도메인 모델 구성 요소의 역할 분담

| 구성 요소 | 역할 | 헥사고날 위치 |
|---|---|---|
| 값 객체 | 불변, 속성 조합으로 동등성 판단, 자기 검증 | `domain/model/` |
| 엔티티 | 고유 식별자, 생명주기, 비즈니스 규칙 캡슐화 | `domain/model/` |
| 애그리거트 루트 | 일관성 경계의 진입점, 이벤트 수집 | `domain/model/` |
| 도메인 서비스 | 여러 애그리거트에 걸친 stateless 로직 | `domain/services/` |
| 도메인 이벤트 | 애그리거트 간 결과적 일관성 매개체 | `domain/events/` |
| 리포지토리 인터페이스 | 애그리거트 단위의 영속성 추상화 | `application/ports/driven/` |
| 응용 서비스 | 유스케이스 오케스트레이션, 트랜잭션 관리 | `application/services/` |

핵심 원칙: **풍부한 도메인 모델을 지향한다.** 비즈니스 로직은 엔티티와 값 객체 내부에 속한다. 데이터만 있고 행동이 없는 빈약한 도메인 모델(Anemic Domain Model)은 안티패턴이다. `updateStatus()` 같은 범용 메서드 대신 `confirm()`, `cancel()`, `ship()`처럼 비즈니스 의도를 드러내는 메서드를 사용한다.

### 4단계: 경계 판단 체크리스트

애그리거트 경계를 확정하기 전에 다음을 검증한다.

- [ ] 이 데이터들이 반드시 같은 트랜잭션에서 일관성을 유지해야 하는가? (Yes -> 같은 애그리거트)
- [ ] 불변식 없이 독립적으로 변경 가능한 데이터가 포함되어 있지 않은가? (Yes -> 분리)
- [ ] 다른 애그리거트를 직접 객체 참조하고 있지 않은가? (Yes -> ID 참조로 교체)
- [ ] 애그리거트 간 동기적 일관성이 정말 필요한가? (대부분 결과적 일관성으로 충분)
- [ ] 리포지토리가 애그리거트 단위인가? (내부 엔티티/값 객체에 별도 리포지토리를 만들지 않는다)

---
> **관련 스킬 참조:**
> - 바운디드 컨텍스트 경계 정의, 컨텍스트 맵, 전략적 설계 -> **architecture-ddd** 스킬
> - CQRS 적용, 이벤트 소싱, 영속성 패턴(Repository, UoW, Data Mapper) -> **architecture-implementation-patterns** 스킬
> - 데이터베이스 스키마 설계(정규화, 인덱스) -> **architecture-db** 스킬
> - Django 프로젝트에서의 도메인 모델 구현 -> **implementation-django** 스킬
> - Python 컨벤션(dataclass, 타입 힌트) -> **implementation-python** 스킬
