# DDD(도메인 주도 설계) 외부 자료 종합 가이드

> 이 문서는 내부 자료(도메인 주도 개발 시작하기[A], 도메인 주도 설계 첫걸음[B], 도메인 주도 설계 구현(빨간책)[C])에서 다루지 않은 **새로운 관점과 패턴**을 외부 권위 자료에서 종합한 것이다.

---

## 1. Eric Evans 원전 (파란책) 고유 개념

> 출처: Eric Evans, "Domain-Driven Design: Tackling Complexity in the Heart of Software" (Addison-Wesley, 2003)
> 참고: [DDD Reference 2015](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) -- Evans가 원전의 모든 패턴을 요약하고 3개 신규 패턴을 추가한 무료 레퍼런스

### 1.1 지식 탐구 (Knowledge Crunching)

내부 자료가 "유비쿼터스 언어를 만들어야 한다"고 결론만 다루는 반면, Evans는 그 **과정** 자체를 핵심으로 강조한다. 지식 탐구(Knowledge Crunching)란 도메인 전문가로부터 쏟아지는 정보의 홍수 속에서 관련 있는 것만 걸러내고, 하나의 조직 아이디어를 시도한 뒤 또 다른 아이디어로 교체하며, 복잡한 데이터를 단순하게 설명하는 관점을 찾아가는 반복 과정이다.

핵심 원칙:
- 모델은 한 번에 완성되지 않는다. 반복적인 정제(iterative refinement)를 통해 깊은 통찰(deeper insight)에 도달한다.
- 도메인 전문가와 개발자가 **함께** 모델을 만들어야 한다. 개발자가 단독으로 모델을 만들고 전문가에게 검증받는 방식은 지식 탐구가 아니다.
- "코드를 리팩터링하는 것이 아니라, 코드 아래에 있는 **모델을 리팩터링**한다"

```python
# 지식 탐구 전: 개발자가 기술적으로 해석한 모델
class Shipment:
    def __init__(self, cargo_id: str, origin: str, destination: str):
        self.cargo_id = cargo_id
        self.origin = origin
        self.destination = destination
        self.status = "pending"

    def update_status(self, new_status: str) -> None:
        self.status = new_status  # 비즈니스 규칙이 없는 단순 상태 변경


# 지식 탐구 후: 도메인 전문가와 반복 대화를 통해 발견한 모델
# "화물은 항해 일정(Itinerary)에 따라 이동하며,
#  각 구간(Leg)은 선박의 항해(Voyage)에 적재된다"
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Leg:
    """항해 구간 -- 하나의 Voyage에 실려 이동하는 단위"""
    voyage_id: str
    load_location: str
    unload_location: str


@dataclass(frozen=True)
class Itinerary:
    """운송 경로 -- Leg의 순서 있는 목록"""
    legs: tuple[Leg, ...]

    def final_destination(self) -> str:
        return self.legs[-1].unload_location if self.legs else ""


@dataclass
class Cargo:
    """화물 애그리거트 루트 -- 지식 탐구를 통해 발견된 핵심 개념"""
    tracking_id: str
    origin: str
    route_specification: "RouteSpecification"
    itinerary: Optional[Itinerary] = None

    def assign_to_route(self, itinerary: Itinerary) -> None:
        if not self.route_specification.is_satisfied_by(itinerary):
            raise ValueError("경로가 운송 요건을 충족하지 않습니다")
        self.itinerary = itinerary

    def is_misrouted(self) -> bool:
        """현재 경로가 요건에 맞지 않으면 True"""
        if self.itinerary is None:
            return True
        return not self.route_specification.is_satisfied_by(self.itinerary)
```

### 1.2 유연한 설계 (Supple Design)

Evans는 Part III에서 "유연한 설계"라는 이름으로 **모델 코드의 품질 패턴** 6가지를 제시한다. 이것은 내부 자료 [A][B][C] 어디에도 다루지 않는 파란책 고유의 핵심 내용이다.

> 출처: Evans, "DDD" Chapter 10 -- Supple Design; [DDD Reference 2015](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
> 참고: [herbertograca.com -- DDD.10 Supple Design](https://herbertograca.com/2015/12/07/ddd-10-supple-design/)

#### (1) 의도를 드러내는 인터페이스 (Intention-Revealing Interfaces)

클래스와 메서드의 이름이 **무엇을 하는지**(what)를 드러내야 하며, **어떻게 하는지**(how)는 숨겨야 한다. 호출자가 내부 구현을 이해할 필요 없이 이름만으로 효과를 예측할 수 있어야 한다.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Paint:
    """페인트 값 객체 -- Evans 원전의 페인트 혼합 예제"""
    red: int
    yellow: int
    blue: int

    # 나쁜 예: 이름이 구현 방식을 드러냄
    # def add_rgb_values(self, other: "Paint") -> "Paint": ...

    # 좋은 예: 의도를 드러냄 -- "페인트를 혼합한다"
    def mix_with(self, other: "Paint") -> "Paint":
        """두 페인트를 혼합하여 새로운 색을 만든다"""
        return Paint(
            red=min(self.red + other.red, 255),
            yellow=min(self.yellow + other.yellow, 255),
            blue=min(self.blue + other.blue, 255),
        )
```

#### (2) 부작용 없는 함수 (Side-Effect-Free Functions)

상태를 절대 변경하지 않는 함수는 데드락을 일으키지 않고, 동시에 실행되는 다른 메서드의 동작을 바꾸지 않으며, 같은 입력에 항상 같은 결과를 반환한다. 가능한 한 많은 도메인 로직을 부작용 없는 함수로 배치하라.

```python
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

    def add(self, other: "Money") -> "Money":
        """부작용 없는 함수: 기존 객체를 변경하지 않고 새 객체를 반환"""
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def percentage(self, rate: float) -> "Money":
        """부작용 없는 함수: 계산 결과를 새 객체로 반환"""
        return Money(amount=int(self.amount * rate), currency=self.currency)
```

#### (3) 단언 (Assertions)

연산의 사후 조건(post-condition)과 클래스의 불변식(invariant)을 명시적으로 선언한다. 코드 내 assert문이나 단위 테스트로 강제한다.

```python
@dataclass
class BankAccount:
    account_id: str
    _balance: int = 0

    def deposit(self, amount: int) -> None:
        """사후 조건: 잔액은 반드시 입금액만큼 증가한다"""
        old_balance = self._balance
        self._balance += amount
        # 단언: 사후 조건을 명시적으로 검증
        assert self._balance == old_balance + amount, "입금 후 잔액 불일치"
        assert self._balance >= 0, "잔액은 음수가 될 수 없다"

    def withdraw(self, amount: int) -> None:
        """사전 조건: 잔액 >= 출금액, 사후 조건: 잔액 감소"""
        if amount > self._balance:
            raise ValueError("잔액이 부족합니다")
        self._balance -= amount
        assert self._balance >= 0, "불변식 위반: 잔액이 음수"
```

#### (4) 개념적 윤곽 (Conceptual Contours)

도메인의 자연스러운 경계선을 따라 설계를 분해한다. 너무 세분화하면 의미 있는 조합이 어려워지고, 너무 크게 묶으면 유연성이 떨어진다. **"함께 변하는 것은 함께 두고, 따로 변하는 것은 분리하라."**

#### (5) 독립형 클래스 (Standalone Classes)

클래스 간 결합을 최소화하여 각 클래스를 독립적으로 이해할 수 있게 하라. 모든 의존성을 제거할 수는 없지만, 모든 불필요한 의존성을 제거하면 개별 개념의 복잡성이 크게 줄어든다.

#### (6) 연산의 닫힘 (Closure of Operations)

반환 타입이 인자의 타입과 동일한 연산을 정의하면, 해당 타입의 인스턴스 집합 안에서 연산이 "닫혀" 있게 된다. 수학의 닫힌 연산(예: 실수 + 실수 = 실수)에서 착안한 개념이다.

```python
@dataclass(frozen=True)
class Color:
    """연산의 닫힘 예시: Color + Color -> Color"""
    r: int
    g: int
    b: int

    def blend(self, other: "Color") -> "Color":
        """Color 타입의 연산이 Color 타입으로 닫혀 있다"""
        return Color(
            r=(self.r + other.r) // 2,
            g=(self.g + other.g) // 2,
            b=(self.b + other.b) // 2,
        )

    def invert(self) -> "Color":
        """단항 연산도 닫힘: Color -> Color"""
        return Color(r=255 - self.r, g=255 - self.g, b=255 - self.b)
```

### 1.3 증류 (Distillation)

Evans는 Part IV에서 대규모 시스템의 복잡성을 관리하는 전략 패턴으로 **증류(Distillation)**를 제시한다. 핵심 도메인을 식별하고 나머지로부터 분리하는 체계적 기법이다.

> 출처: Evans, "DDD" Chapter 15 -- Distillation
> 참고: [herbertograca.com -- DDD.15 Distillation](https://herbertograca.com/2016/05/09/ddd-15-distillation/)

| 패턴 | 설명 |
|------|------|
| 핵심 도메인 (Core Domain) | 시스템의 가장 가치 있는 부분. 최고의 인재를 투입해야 한다 |
| 일반 하위 도메인 (Generic Subdomain) | 프로젝트의 동기가 아닌 부분. 별도 모듈에 제네릭 모델로 분리 |
| 도메인 비전 선언문 (Domain Vision Statement) | 핵심 도메인의 가치와 차별점을 한 페이지로 서술한 문서 |
| 하이라이트 코어 (Highlighted Core) | 핵심 도메인의 핵심 요소를 간결하게 3~7페이지 문서로 정리하거나, 코드에서 핵심 부분을 마킹 |
| 응집력 있는 메커니즘 (Cohesive Mechanism) | 복잡한 계산/알고리즘을 별도 라이브러리로 추출. 도메인 모델은 "무엇을"만 표현 |
| 분리된 핵심 (Segregated Core) | 핵심 도메인을 별도 모듈로 물리적 분리. 의존성을 줄여 핵심에만 집중 |
| 추상 핵심 (Abstract Core) | 핵심 개념들의 추상화를 별도 모듈에 배치. 구현은 하위 모듈에 위임 |

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


# === 증류 예시: 전자상거래 시스템 ===

# 핵심 도메인 (Core Domain) -- 최고 인재가 집중
class PricingEngine(ABC):
    """가격 결정 엔진 -- 우리 회사의 경쟁 우위의 원천"""

    @abstractmethod
    def calculate_dynamic_price(
        self, product_id: str, customer_segment: str, demand_level: float
    ) -> "Money":
        """실시간 수요/고객 세그먼트 기반 동적 가격 산출"""
        ...


# 일반 하위 도메인 (Generic Subdomain) -- 외부 솔루션 또는 표준 구현
class TaxCalculator:
    """세금 계산 -- 모든 회사가 동일한 규칙을 따름.
    외부 라이브러리 사용을 권장."""

    def calculate_vat(self, amount: Money, country_code: str) -> Money:
        rates = {"KR": 0.10, "US": 0.0, "DE": 0.19}
        rate = rates.get(country_code, 0.10)
        return Money(amount=int(amount.amount * rate), currency=amount.currency)


# 응집력 있는 메커니즘 (Cohesive Mechanism) -- 복잡한 알고리즘을 분리
class RouteOptimizer:
    """배송 경로 최적화 알고리즘 -- 도메인 모델은 '최적 경로를 찾아라'만 표현,
    실제 TSP 풀이 알고리즘은 이 메커니즘에 캡슐화."""

    def find_optimal_route(
        self, warehouse: str, destinations: list[str]
    ) -> list[str]:
        # 실제로는 복잡한 최적화 알고리즘
        return sorted(destinations)  # 단순화된 예시
```

### 1.4 대규모 구조 (Large-Scale Structure)

> 출처: Evans, "DDD" Chapter 16 -- Large-Scale Structure

시스템 전체에 적용되는 고수준 조직 패턴이다. 내부 자료에서는 거의 다루지 않는 파란책 Part IV의 고유 내용이다.

| 패턴 | 설명 |
|------|------|
| 진화하는 질서 (Evolving Order) | 대규모 구조를 처음부터 완벽히 설계하지 말고, 시스템과 함께 진화시켜라 |
| 시스템 은유 (System Metaphor) | 시스템 전체를 관통하는 비유를 찾아 명시화하라 (XP에서 차용) |
| 책임 계층 (Responsibility Layers) | 도메인 모델을 의미 있는 책임 계층으로 구조화하라 |
| 지식 수준 (Knowledge Level) | 운영 수준의 핵심 동작을 구성(configure)할 수 있는 메타 수준을 분리하라 |
| 플러그형 컴포넌트 프레임워크 (Pluggable Component Framework) | 핵심 추상화와 구현을 플러그인 구조로 분리하라 |

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# === 지식 수준 (Knowledge Level) 패턴 ===
# 운영 수준: 실제 비즈니스 객체
# 지식 수준: 운영 수준의 구조와 규칙을 정의하는 메타 객체

class FieldType(Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    CHOICE = "choice"


@dataclass(frozen=True)
class FieldDefinition:
    """지식 수준(Knowledge Level): 필드의 구조를 정의하는 메타 객체"""
    name: str
    field_type: FieldType
    required: bool = True
    choices: tuple[str, ...] = ()


@dataclass(frozen=True)
class FormTemplate:
    """지식 수준: 양식의 구조를 정의"""
    template_name: str
    field_definitions: tuple[FieldDefinition, ...]


@dataclass
class FormInstance:
    """운영 수준(Operational Level): 실제 사용자가 작성하는 양식 인스턴스"""
    template: FormTemplate
    values: dict[str, Any] = field(default_factory=dict)

    def set_field(self, field_name: str, value: Any) -> None:
        """지식 수준의 정의에 따라 운영 수준의 동작이 제어된다"""
        definition = self._find_definition(field_name)
        if definition is None:
            raise ValueError(f"템플릿에 '{field_name}' 필드가 없습니다")
        if definition.field_type == FieldType.CHOICE and value not in definition.choices:
            raise ValueError(f"허용된 선택지가 아닙니다: {definition.choices}")
        self.values[field_name] = value

    def _find_definition(self, name: str) -> FieldDefinition | None:
        return next(
            (d for d in self.template.field_definitions if d.name == name), None
        )


# 사용 예시: 지식 수준에서 '휴가 신청서' 양식 구조를 정의
leave_form_template = FormTemplate(
    template_name="휴가 신청서",
    field_definitions=(
        FieldDefinition(name="휴가유형", field_type=FieldType.CHOICE,
                        choices=("연차", "병가", "경조사")),
        FieldDefinition(name="사유", field_type=FieldType.TEXT),
    ),
)

# 운영 수준에서 실제 양식을 작성
form = FormInstance(template=leave_form_template)
form.set_field("휴가유형", "연차")
form.set_field("사유", "가족 여행")
```

---

## 2. Vaughn Vernon의 효과적 애그리거트 설계

> 출처: Vaughn Vernon, "Effective Aggregate Design" Part I-III (2011)
> 원문: [DDD Community -- Vernon 2011](https://www.dddcommunity.org/library/vernon_2011/), [Part I PDF](https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_1.pdf)
> 참고: [Kalele -- Effective Aggregate Design](https://kalele.io/effective-aggregate-design/), [ArchiLab -- Aggregate Design Rules](https://www.archi-lab.io/infopages/ddd/aggregate-design-rules-vernon.html)

내부 자료 [C]가 Vernon의 애그리거트 기본 개념을 다루지만, "Effective Aggregate Design" 시리즈에서 제시하는 **4가지 설계 규칙과 그 근거**는 별도로 정리할 가치가 있다.

### 2.1 규칙 1: 진짜 불변식을 일관성 경계 안에서 보호하라

하나의 트랜잭션에서는 하나의 애그리거트만 수정한다. 애그리거트 경계는 **비즈니스 불변식**(invariant)이 반드시 함께 지켜져야 하는 범위와 일치해야 한다.

```python
from dataclasses import dataclass, field
from typing import List
from uuid import uuid4


@dataclass
class OrderLine:
    product_id: str
    quantity: int
    unit_price: int


@dataclass
class Order:
    """애그리거트 루트 -- 불변식: 주문 총액은 항상 라인 합계와 일치해야 한다"""
    id: str = field(default_factory=lambda: str(uuid4()))
    lines: List[OrderLine] = field(default_factory=list)
    _total: int = field(default=0, init=False)

    def add_line(self, line: OrderLine) -> None:
        self.lines.append(line)
        self._recalculate_total()

    def remove_line(self, product_id: str) -> None:
        self.lines = [l for l in self.lines if l.product_id != product_id]
        self._recalculate_total()

    def _recalculate_total(self) -> None:
        """불변식 보호: 모든 변경 후 총액을 즉시 재계산"""
        self._total = sum(l.quantity * l.unit_price for l in self.lines)

    @property
    def total(self) -> int:
        return self._total
```

### 2.2 규칙 2: 작은 애그리거트를 설계하라

> "루트 엔티티와 최소한의 속성/값 객체로 제한하라. 올바른 최소치는 일관성을 유지하는 데 필요한 만큼이며, 그 이상은 아니다."

**큰 애그리거트의 문제점:**
- 트랜잭션 실패 가능성 증가 (동시 접근으로 인한 충돌)
- 메모리 사용량 증가, 로딩 시간 증가
- 가비지 컬렉션 부담 증가

```python
# --- 안티패턴: 너무 큰 애그리거트 ---
@dataclass
class BigProduct:
    """모든 것을 하나의 애그리거트에 넣은 나쁜 예"""
    id: str
    name: str
    description: str
    price: int
    reviews: List["Review"] = field(default_factory=list)       # 수천 건
    images: List["ProductImage"] = field(default_factory=list)   # 수십 건
    inventory: "Inventory" = None                                # 별도 관심사
    # 리뷰 추가 시 Product 전체를 로딩하고 락을 잡아야 함 -> 성능 저하


# --- 좋은 예: 분리된 작은 애그리거트 ---
@dataclass
class Product:
    """상품 애그리거트 -- 핵심 속성만 포함"""
    id: str
    name: str
    description: str
    price: int


@dataclass
class ProductReview:
    """리뷰 애그리거트 -- Product와 ID로만 연결"""
    id: str
    product_id: str  # Product를 ID로 참조 (규칙 3)
    reviewer_id: str
    rating: int
    content: str
```

### 2.3 규칙 3: 다른 애그리거트는 ID로만 참조하라

직접 객체 참조(object reference) 대신 식별자(identity)로 참조하면:
- 애그리거트가 자동으로 작아진다 (즉시 로딩 방지)
- 로딩 시간과 메모리 사용이 줄어든다
- 바운디드 컨텍스트 간 참조도 가능해진다

```python
# --- 안티패턴: 직접 객체 참조 ---
@dataclass
class OrderBad:
    customer: "Customer"     # 객체를 직접 보유 -> 결합도 높음
    product: "Product"       # Order 로딩 시 Customer, Product도 함께 로딩


# --- 좋은 예: ID 참조 ---
@dataclass
class OrderGood:
    customer_id: str         # ID만 보유 -> 느슨한 결합
    product_id: str          # 필요할 때만 별도 조회
```

### 2.4 규칙 4: 일관성 경계 밖에서는 결과적 일관성을 사용하라

서로 다른 애그리거트 간의 일관성은 도메인 이벤트를 통한 **결과적 일관성(eventual consistency)**으로 달성한다. 즉시 일관성이 필요한 것처럼 보이는 경우에도, 도메인 전문가에게 물어보면 지연이 허용되는 경우가 많다.

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List


# 도메인 이벤트 정의
@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    customer_id: str
    total_amount: int
    occurred_at: datetime


@dataclass
class Order:
    id: str
    customer_id: str
    total: int
    events: List = field(default_factory=list)

    def place(self) -> None:
        """주문 확정 시 이벤트를 발행하여 다른 애그리거트에 알린다.
        재고 차감, 포인트 적립 등은 별도 트랜잭션에서 결과적으로 일관성을 달성."""
        self.events.append(
            OrderPlacedEvent(
                order_id=self.id,
                customer_id=self.customer_id,
                total_amount=self.total,
                occurred_at=datetime.now(),
            )
        )


# 별도 핸들러에서 결과적 일관성으로 처리
class InventoryEventHandler:
    def handle_order_placed(self, event: OrderPlacedEvent) -> None:
        """별도 트랜잭션에서 재고 차감 -- 결과적 일관성"""
        # inventory_repo.find_by_product_id(...)
        # inventory.decrease_stock(...)
        pass

class LoyaltyEventHandler:
    def handle_order_placed(self, event: OrderPlacedEvent) -> None:
        """별도 트랜잭션에서 포인트 적립 -- 결과적 일관성"""
        # loyalty_repo.find_by_customer_id(...)
        # loyalty.add_points(...)
        pass
```

---

## 3. Event Storming (이벤트 스토밍)

> 출처: Alberto Brandolini, "Introducing EventStorming" (Leanpub, 2013~)
> 참고: [eventstorming.com](https://www.eventstorming.com/), [Wikipedia -- Event Storming](https://en.wikipedia.org/wiki/Event_storming), [Qlerify -- Event Storming Complete Guide](https://www.qlerify.com/post/event-storming-the-complete-guide)

내부 자료에서 다루지 않는 **도메인 발견 기법**이다. DDD의 전략 설계(바운디드 컨텍스트 식별, 핵심 도메인 발견)를 실행하기 위한 워크숍 방법론이다.

### 3.1 핵심 개념

Event Storming은 개발자와 도메인 전문가가 함께 "넓은 벽(wide wall)"에 포스트잇을 붙여가며 비즈니스 프로세스를 탐색하는 워크숍 기법이다. 컴퓨터 없이 진행하며, 결과물은 벽에 붙은 포스트잇이다.

**워크숍에 필요한 사람:**
- "질문을 잘 하는 사람" (보통 개발자)
- "답을 아는 사람" (도메인 전문가, 프로덕트 오너)

### 3.2 포스트잇 색상 체계

| 색상 | 개념 | 설명 | 시제 |
|------|------|------|------|
| 주황색 | 도메인 이벤트 (Domain Event) | 비즈니스에서 발생한 사건 | 과거형 ("주문이 접수되었다") |
| 파란색 | 커맨드 (Command) | 이벤트를 유발하는 의도적 행동 | 현재형 ("주문을 접수하라") |
| 노란색 | 애그리거트 (Aggregate) | 커맨드를 받아 이벤트를 발생시키는 주체 | -- |
| 라일락(lilac) | 정책/프로세스 (Policy) | 이벤트에 반응하여 새로운 커맨드를 생성하는 비즈니스 규칙 | -- |
| 초록색 | 읽기 모델 (Read Model) | 사용자가 커맨드를 실행하기 위해 보는 정보 | -- |
| 분홍색 | 외부 시스템 (External System) | 도메인 밖에서 커맨드를 유발하는 시스템 | -- |
| 작은 노란색 | 액터 (Actor/Person) | 커맨드를 실행하는 사용자 역할 | -- |
| 빨간색/핫핑크 | 핫스팟 (Hot Spot) | 논쟁, 질문, 불확실한 영역 | -- |

### 3.3 세 가지 변형

#### Big Picture Event Storming
- 목적: 전체 비즈니스 프로세스를 조감도로 파악
- 참여자: 10~30명, 다양한 부서
- 결과물: 바운디드 컨텍스트의 경계 후보 식별

#### Process Modelling Event Storming
- 목적: 특정 비즈니스 프로세스를 상세히 모델링
- 참여자: 5~10명, 해당 도메인 전문가 + 개발자
- 결과물: 커맨드, 이벤트, 정책의 흐름

#### Software Design Event Storming
- 목적: 구체적인 소프트웨어 설계로 전환
- 참여자: 3~5명, 개발 팀
- 결과물: 애그리거트, 읽기 모델, 외부 시스템 연동 설계

```python
# Event Storming 결과를 코드로 옮기는 예시
# 워크숍에서 발견된 흐름:
#   [액터: 고객] -> [커맨드: 주문 접수] -> [애그리거트: 주문]
#   -> [이벤트: 주문 접수됨] -> [정책: 결제 시작] -> [외부: PG사]
#   -> [이벤트: 결제 완료됨] -> [정책: 재고 차감] -> [애그리거트: 재고]

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Protocol


# 도메인 이벤트 (주황색 포스트잇)
@dataclass(frozen=True)
class OrderAccepted:
    order_id: str
    customer_id: str
    items: tuple
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PaymentCompleted:
    order_id: str
    payment_id: str
    amount: int
    occurred_at: datetime = field(default_factory=datetime.now)


# 커맨드 (파란색 포스트잇)
@dataclass(frozen=True)
class AcceptOrder:
    customer_id: str
    items: list


@dataclass(frozen=True)
class ProcessPayment:
    order_id: str
    amount: int


# 정책 (라일락 포스트잇)
class PaymentPolicy:
    """'주문 접수됨' 이벤트에 반응하여 '결제 처리' 커맨드를 생성하는 정책"""

    def handle(self, event: OrderAccepted) -> ProcessPayment:
        total = sum(item["price"] * item["quantity"] for item in event.items)
        return ProcessPayment(order_id=event.order_id, amount=total)


class InventoryPolicy:
    """'결제 완료됨' 이벤트에 반응하여 재고 차감을 트리거하는 정책"""

    def handle(self, event: PaymentCompleted) -> None:
        # 재고 차감 커맨드 생성
        pass
```

---

## 4. 컨텍스트 매핑 패턴 상세

> 출처: Eric Evans, "DDD" Chapter 14; [Open Group -- DDD Strategic Patterns](https://pubs.opengroup.org/architecture/o-aa-standard/DDD-strategic-patterns.html)
> 참고: [Context Mapper](https://contextmapper.org/docs/), [DDD Crew -- Context Mapping](https://github.com/ddd-crew/context-mapping)

내부 자료 [B][C]가 6개 패턴을 표로 나열하지만, 각 패턴의 **선택 기준과 구현 방식**은 깊이 있게 다루지 않는다. 여기서는 9개 전체 패턴을 선택 지침과 함께 정리한다.

### 4.1 협력 패턴 (Cooperation)

#### Partnership (파트너십)
- **관계:** 양방향 대등, 상호 의존
- **조건:** 두 컨텍스트의 개발 실패가 양쪽 모두의 배포 실패를 야기할 때
- **실행:** 공동 기획, 공동 릴리스 일정, 인터페이스 변경 시 양측 합의
- **위험:** 팀 간 일정 조율 비용이 높다

#### Shared Kernel (공유 커널)
- **관계:** 양방향, 모델의 일부를 명시적으로 공유
- **조건:** 중복 비용 > 조율 비용일 때만 사용
- **실행:** 공유 범위를 최소화, CI에서 양쪽 테스트가 모두 통과해야 머지
- **위험:** 공유 범위가 커지면 사실상 하나의 모놀리스가 된다

### 4.2 사용자-제공자 패턴 (Customer-Supplier)

#### Customer-Supplier (고객-공급자)
- **관계:** 비대칭. 업스트림(공급자)이 API를 제공하고 다운스트림(고객)이 소비
- **조건:** 업스트림이 다운스트림 없이도 성공 가능하지만, 다운스트림의 요구를 계획에 반영
- **실행:** 다운스트림 팀이 업스트림 팀의 백로그에 항목을 추가할 수 있는 권한

#### Conformist (순응주의자)
- **관계:** 비대칭. 다운스트림이 업스트림 모델을 그대로 채택
- **조건:** 업스트림이 다운스트림의 요구를 수용할 의지/능력이 없을 때
- **장점:** 번역 레이어 불필요, 유비쿼터스 언어 공유
- **단점:** 다운스트림 설계의 자유도 포기

#### Anticorruption Layer -- ACL (충돌 방지 계층)
- **관계:** 비대칭. 다운스트림이 업스트림 모델을 **번역**하여 사용
- **조건:** 업스트림의 모델이 다운스트림 도메인과 맞지 않을 때
- **실행:** 번역기(Translator) + 퍼사드(Facade) 계층을 다운스트림에 구현

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


# === Customer-Supplier: 업스트림이 다운스트림 요구를 수용 ===

# 업스트림 (공급자): 상품 카탈로그 컨텍스트
class ProductCatalogAPI:
    """업스트림이 제공하는 API -- 다운스트림의 요구를 반영"""

    def get_product(self, product_id: str) -> dict:
        return {
            "id": product_id,
            "name": "고급 노트북",
            "price": 1500000,
            "stock_status": "in_stock",  # 다운스트림 요청으로 추가된 필드
        }

# 다운스트림 (고객): 주문 컨텍스트 -- 업스트림 API를 직접 사용


# === Conformist: 업스트림 모델을 그대로 채택 ===
# 구글 캘린더 API의 이벤트 모델을 그대로 사용하는 경우
@dataclass
class GoogleCalendarEvent:
    """업스트림(구글) 모델을 그대로 사용 -- Conformist"""
    summary: str
    start: dict   # {"dateTime": "...", "timeZone": "..."}
    end: dict
    attendees: list


# === ACL: 업스트림 모델을 우리 모델로 번역 ===
# 레거시 ERP 시스템의 모델을 우리 도메인 모델로 변환
@dataclass
class LegacyERPOrder:
    """레거시 ERP의 주문 데이터 구조"""
    ORD_NO: str
    CUST_CD: str
    ORD_DT: str  # "20240101" 형식
    TOT_AMT: float
    STAT_CD: int  # 1=대기, 2=확정, 3=취소


@dataclass(frozen=True)
class OrderSummary:
    """우리 도메인의 주문 요약 값 객체"""
    order_number: str
    customer_id: str
    order_date: str  # ISO 형식
    total_amount: int
    is_confirmed: bool


class ERPAnticorruptionLayer:
    """ACL: 레거시 ERP -> 우리 도메인 모델 번역"""

    STATUS_MAP = {1: False, 2: True, 3: False}

    def translate(self, erp_order: LegacyERPOrder) -> OrderSummary:
        return OrderSummary(
            order_number=erp_order.ORD_NO,
            customer_id=erp_order.CUST_CD,
            order_date=f"{erp_order.ORD_DT[:4]}-{erp_order.ORD_DT[4:6]}-{erp_order.ORD_DT[6:8]}",
            total_amount=int(erp_order.TOT_AMT),
            is_confirmed=self.STATUS_MAP.get(erp_order.STAT_CD, False),
        )
```

### 4.3 제공 패턴 (Supplier)

#### Open Host Service -- OHS (오픈 호스트 서비스)
- **관계:** 업스트림이 퍼블릭 프로토콜을 정의하여 다수의 다운스트림에 서비스
- **실행:** REST API, gRPC 등 공개 인터페이스. 특이한 요구는 별도 번역기로 처리

#### Published Language (발행된 언어)
- **관계:** OHS와 함께 사용. 컨텍스트 간 통신의 공유 언어
- **예시:** JSON Schema, Protobuf, XML Schema, Avro

### 4.4 분리 패턴

#### Separate Ways (분리된 노선)
- **관계:** 통합하지 않음
- **조건:** 통합 비용 > 기능 중복 비용일 때
- **예시:** 각 팀이 독립적으로 알림 기능을 구현

#### Big Ball of Mud (큰 진흙 공)
- **관계:** 경계가 없는 혼돈 상태
- **대응:** 이 영역 바깥에 ACL을 두어 진흙 공이 퍼지지 않도록 방어

---

## 5. 전략 DDD와 팀 토폴로지

> 출처: Matthew Skelton & Manuel Pais, "Team Topologies" (2019)
> 참고: [archman.dev -- Team Topologies and Conway's Law Alignment](https://archman.dev/docs/domain-driven-design/strategic-design/team-topologies-and-conways-law-alignment), [Martin Fowler -- Conway's Law](https://martinfowler.com/bliki/ConwaysLaw.html), [ardalis.com -- Conway's Law, DDD, and Microservices](https://ardalis.com/conways-law-ddd-and-microservices/)

### 5.1 Conway의 법칙과 역 Conway 기동

**Conway의 법칙:** "시스템을 설계하는 조직은 자신의 커뮤니케이션 구조를 복제하는 설계를 산출하게 된다."

**역 Conway 기동(Inverse Conway Maneuver):** 원하는 소프트웨어 아키텍처를 먼저 설계하고, 그에 맞게 팀 구조를 의도적으로 재편한다.

DDD의 바운디드 컨텍스트는 이 과정에서 핵심 도구가 된다:
1. 도메인 분석으로 바운디드 컨텍스트를 식별한다
2. 각 바운디드 컨텍스트를 하나의 팀이 소유하도록 조직을 구성한다
3. 팀 경계 = 컨텍스트 경계 = 서비스 경계가 된다

### 5.2 팀 토폴로지와 DDD 매핑

| 팀 토폴로지 유형 | DDD 개념 매핑 |
|---------------|-------------|
| Stream-aligned Team | 핵심/지원 하위 도메인의 바운디드 컨텍스트를 소유. End-to-end로 가치를 전달 |
| Platform Team | 일반 하위 도메인에 해당. 공통 인프라를 OHS로 제공 |
| Enabling Team | 컨텍스트 매핑에서 Partnership 관계. 다른 팀의 역량 향상을 지원 |
| Complicated Subsystem Team | 복잡한 알고리즘/수학적 모델 등 응집력 있는 메커니즘(Cohesive Mechanism) 담당 |

| 팀 상호작용 모드 | 컨텍스트 매핑 패턴 |
|----------------|----------------|
| Collaboration | Partnership, Shared Kernel |
| X-as-a-Service | OHS + Published Language, Customer-Supplier |
| Facilitating | (직접 매핑 없음 -- Enabling Team의 역할) |

---

## 6. Specification 패턴

> 출처: Eric Evans & Martin Fowler, "Specifications" (1997 -- Evans의 파란책에도 포함)
> 참고: [Wikipedia -- Specification Pattern](https://en.wikipedia.org/wiki/Specification_pattern), [Douwe van der Meij -- Specification Pattern in Python](https://douwevandermeij.medium.com/specification-pattern-in-python-ff2bd0b603f6)

비즈니스 규칙을 독립적인 객체로 캡슐화하고, 논리 연산(AND, OR, NOT)으로 조합할 수 있게 하는 패턴이다. 내부 자료에서는 다루지 않는 전술 패턴이다.

### 6.1 기본 구현

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """Specification 패턴 기본 클래스"""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        ...

    def __and__(self, other: Specification[T]) -> AndSpecification[T]:
        return AndSpecification(self, other)

    def __or__(self, other: Specification[T]) -> OrSpecification[T]:
        return OrSpecification(self, other)

    def __invert__(self) -> NotSpecification[T]:
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return (
            self._left.is_satisfied_by(candidate)
            and self._right.is_satisfied_by(candidate)
        )


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return (
            self._left.is_satisfied_by(candidate)
            or self._right.is_satisfied_by(candidate)
        )


class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]):
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self._spec.is_satisfied_by(candidate)
```

### 6.2 실무 적용 예시

```python
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Customer:
    id: str
    name: str
    email: str
    total_purchases: int
    registered_at: datetime
    is_verified: bool


# 개별 비즈니스 규칙을 Specification으로 캡슐화
class IsVerified(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.is_verified


class HasMinimumPurchases(Specification[Customer]):
    def __init__(self, minimum: int):
        self._minimum = minimum

    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.total_purchases >= self._minimum


class RegisteredMoreThanDaysAgo(Specification[Customer]):
    def __init__(self, days: int):
        self._days = days

    def is_satisfied_by(self, customer: Customer) -> bool:
        cutoff = datetime.now() - timedelta(days=self._days)
        return customer.registered_at <= cutoff


# 조합하여 복합 비즈니스 규칙 생성
eligible_for_premium = (
    IsVerified()
    & HasMinimumPurchases(minimum=100_000)
    & RegisteredMoreThanDaysAgo(days=90)
)

eligible_for_promotion = (
    IsVerified()
    & ~HasMinimumPurchases(minimum=50_000)  # 구매액이 적은 고객 대상 프로모션
)

# 사용
customer = Customer(
    id="C001",
    name="김철수",
    email="kim@example.com",
    total_purchases=200_000,
    registered_at=datetime(2024, 1, 1),
    is_verified=True,
)

assert eligible_for_premium.is_satisfied_by(customer) is True
assert eligible_for_promotion.is_satisfied_by(customer) is False
```

### 6.3 Specification의 세 가지 용도

| 용도 | 설명 | 예시 |
|------|------|------|
| 검증 (Validation) | 객체가 비즈니스 규칙을 만족하는지 확인 | `eligible_for_premium.is_satisfied_by(customer)` |
| 선택 (Selection/Query) | 컬렉션에서 조건에 맞는 객체를 필터링 | `[c for c in customers if spec.is_satisfied_by(c)]` |
| 생성 (Construction) | 규칙을 만족하는 새 객체를 생성하도록 빌더에 전달 | 팩토리가 Specification을 참조하여 기본값 결정 |

---

## 7. CQRS + Event Sourcing 상세

> 출처: Greg Young, "CQRS Documents" (2010); Martin Fowler, [CQRS](https://martinfowler.com/bliki/CQRS.html), [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html), [What do you mean by "Event-Driven"?](https://martinfowler.com/articles/201701-event-driven.html)
> 참고: [Microsoft Learn -- CQRS Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs), [Microsoft Learn -- Event Sourcing Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)

### 7.1 Martin Fowler의 이벤트 주도 아키텍처 4가지 의미

Fowler는 "이벤트 주도"라는 용어가 최소 4가지 다른 패턴을 지칭한다고 정리했다.

| 패턴 | 설명 | 특징 |
|------|------|------|
| Event Notification | 이벤트 발생을 알리되, 상세 데이터는 포함하지 않음 | 낮은 결합도, 필요시 소스에 질의 |
| Event-Carried State Transfer | 이벤트에 상태 데이터를 포함하여 소비자가 로컬 복사본을 유지 | 가용성 향상, 결과적 일관성 |
| Event Sourcing | 상태를 이벤트 시퀀스로 저장. 언제든 이벤트 로그에서 상태를 재구축 가능 | 감사 추적, 시간 여행 질의 |
| CQRS | 읽기 모델과 쓰기 모델을 분리 | 독립적 확장, 복잡한 도메인에 적합 |

### 7.2 CQRS 패턴 상세

> "CQRS는 최상위 아키텍처가 아니다! 보조 패턴으로 취급하고, 선택적으로 일부 바운디드 컨텍스트에만 적용하라." -- Greg Young

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4


# === 쓰기 측 (Command Side) ===

@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: str
    items: tuple


@dataclass(frozen=True)
class CancelOrderCommand:
    order_id: str
    reason: str


class OrderCommandHandler:
    """커맨드 핸들러: 쓰기 모델을 사용하여 상태를 변경"""

    def __init__(self, order_repo: "OrderRepository"):
        self._repo = order_repo

    def handle_create(self, cmd: CreateOrderCommand) -> str:
        order_id = str(uuid4())
        order = Order(id=order_id, customer_id=cmd.customer_id)
        for item in cmd.items:
            order.add_line(OrderLine(**item))
        self._repo.save(order)
        return order_id

    def handle_cancel(self, cmd: CancelOrderCommand) -> None:
        order = self._repo.find_by_id(cmd.order_id)
        order.cancel(cmd.reason)
        self._repo.save(order)


# === 읽기 측 (Query Side) ===

@dataclass(frozen=True)
class OrderSummaryView:
    """읽기 전용 DTO -- 비정규화된 뷰"""
    order_id: str
    customer_name: str
    item_count: int
    total_amount: int
    status: str
    created_at: str


class OrderQueryHandler:
    """쿼리 핸들러: 읽기 전용 저장소에서 비정규화된 뷰를 조회"""

    def __init__(self, read_store: "OrderReadStore"):
        self._store = read_store

    def get_order_summary(self, order_id: str) -> Optional[OrderSummaryView]:
        return self._store.find_summary(order_id)

    def list_customer_orders(self, customer_id: str) -> List[OrderSummaryView]:
        return self._store.find_by_customer(customer_id)


# === 프로젝션 (읽기 모델 동기화) ===

class OrderProjection:
    """이벤트를 소비하여 읽기 모델을 업데이트하는 프로젝션"""

    def __init__(self, read_store: "OrderReadStore"):
        self._store = read_store

    def on_order_created(self, event: "OrderCreatedEvent") -> None:
        """쓰기 측에서 발행된 이벤트를 받아 읽기 모델을 구축"""
        self._store.upsert_summary(OrderSummaryView(
            order_id=event.order_id,
            customer_name=event.customer_name,
            item_count=event.item_count,
            total_amount=event.total_amount,
            status="CREATED",
            created_at=event.occurred_at.isoformat(),
        ))

    def on_order_cancelled(self, event: "OrderCancelledEvent") -> None:
        summary = self._store.find_summary(event.order_id)
        if summary:
            # 기존 뷰를 업데이트 (비정규화 저장소 특성상 전체 교체)
            self._store.upsert_summary(OrderSummaryView(
                order_id=summary.order_id,
                customer_name=summary.customer_name,
                item_count=summary.item_count,
                total_amount=summary.total_amount,
                status="CANCELLED",
                created_at=summary.created_at,
            ))
```

### 7.3 Event Sourcing 패턴 상세

> "Event Sourcing의 정의: 언제든 애플리케이션 상태를 날려버리고 이벤트 로그에서 자신 있게 재구축할 수 있다." -- Martin Fowler

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import uuid4


# === 도메인 이벤트 ===

@dataclass(frozen=True)
class DomainEvent:
    """모든 도메인 이벤트의 기본 클래스"""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class AccountOpened(DomainEvent):
    account_id: str = ""
    owner_name: str = ""
    initial_balance: int = 0


@dataclass(frozen=True)
class MoneyDeposited(DomainEvent):
    account_id: str = ""
    amount: int = 0


@dataclass(frozen=True)
class MoneyWithdrawn(DomainEvent):
    account_id: str = ""
    amount: int = 0


# === 이벤트 소싱 애그리거트 ===

class EventSourcedAggregate(ABC):
    """이벤트 소싱 기반 애그리거트 루트의 기반 클래스"""

    def __init__(self):
        self._uncommitted_events: List[DomainEvent] = []
        self._version: int = 0

    def _apply(self, event: DomainEvent) -> None:
        """이벤트를 적용하여 상태를 변경하고 미커밋 목록에 추가"""
        self._route_event(event)
        self._uncommitted_events.append(event)
        self._version += 1

    @abstractmethod
    def _route_event(self, event: DomainEvent) -> None:
        """서브클래스에서 이벤트 타입별 핸들러로 라우팅"""
        ...

    def load_from_history(self, events: List[DomainEvent]) -> None:
        """저장된 이벤트를 순서대로 재생하여 상태를 복원"""
        for event in events:
            self._route_event(event)
            self._version += 1

    @property
    def uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)

    def clear_events(self) -> None:
        self._uncommitted_events.clear()


class BankAccount(EventSourcedAggregate):
    """이벤트 소싱 기반 은행 계좌 애그리거트"""

    def __init__(self):
        super().__init__()
        self.account_id: str = ""
        self.owner_name: str = ""
        self.balance: int = 0

    # --- 커맨드 메서드: 비즈니스 규칙 검증 후 이벤트 생성 ---

    def open(self, account_id: str, owner: str, initial_balance: int) -> None:
        if initial_balance < 0:
            raise ValueError("초기 잔액은 0 이상이어야 합니다")
        self._apply(AccountOpened(
            account_id=account_id,
            owner_name=owner,
            initial_balance=initial_balance,
        ))

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("입금액은 0보다 커야 합니다")
        self._apply(MoneyDeposited(account_id=self.account_id, amount=amount))

    def withdraw(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("출금액은 0보다 커야 합니다")
        if amount > self.balance:
            raise ValueError("잔액이 부족합니다")
        self._apply(MoneyWithdrawn(account_id=self.account_id, amount=amount))

    # --- 이벤트 핸들러: 이벤트를 적용하여 상태를 변경 (부작용 없음) ---

    def _route_event(self, event: DomainEvent) -> None:
        if isinstance(event, AccountOpened):
            self._on_account_opened(event)
        elif isinstance(event, MoneyDeposited):
            self._on_money_deposited(event)
        elif isinstance(event, MoneyWithdrawn):
            self._on_money_withdrawn(event)

    def _on_account_opened(self, event: AccountOpened) -> None:
        self.account_id = event.account_id
        self.owner_name = event.owner_name
        self.balance = event.initial_balance

    def _on_money_deposited(self, event: MoneyDeposited) -> None:
        self.balance += event.amount

    def _on_money_withdrawn(self, event: MoneyWithdrawn) -> None:
        self.balance -= event.amount


# === 이벤트 스토어 ===

class EventStore:
    """인메모리 이벤트 스토어 (프로덕션에서는 DB/Kafka 등 사용)"""

    def __init__(self):
        self._store: dict[str, List[DomainEvent]] = {}

    def save(self, aggregate_id: str, events: List[DomainEvent]) -> None:
        if aggregate_id not in self._store:
            self._store[aggregate_id] = []
        self._store[aggregate_id].extend(events)

    def load(self, aggregate_id: str) -> List[DomainEvent]:
        return list(self._store.get(aggregate_id, []))


# === 이벤트 소싱 리포지토리 ===

class BankAccountRepository:
    """이벤트 소싱 기반 리포지토리: 이벤트를 저장/로딩하여 애그리거트 복원"""

    def __init__(self, event_store: EventStore):
        self._store = event_store

    def save(self, account: BankAccount) -> None:
        self._store.save(account.account_id, account.uncommitted_events)
        account.clear_events()

    def find_by_id(self, account_id: str) -> BankAccount:
        events = self._store.load(account_id)
        if not events:
            raise ValueError(f"계좌를 찾을 수 없습니다: {account_id}")
        account = BankAccount()
        account.load_from_history(events)  # 이벤트 재생으로 상태 복원
        return account


# 사용 예시
store = EventStore()
repo = BankAccountRepository(store)

# 계좌 생성 및 거래
account = BankAccount()
account.open("ACC-001", "김철수", 100_000)
account.deposit(50_000)
account.withdraw(30_000)
repo.save(account)

# 이벤트 로그에서 상태 복원
restored = repo.find_by_id("ACC-001")
assert restored.balance == 120_000  # 100000 + 50000 - 30000
```

---

## 8. Saga 패턴 (분산 트랜잭션)

> 출처: Hector Garcia-Molina & Kenneth Salem, "Sagas" (1987 -- 원논문)
> 참고: [Microsoft Learn -- Saga Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga), [microservices.io -- Saga](https://microservices.io/patterns/data/saga.html), [Temporal -- Mastering Saga Patterns](https://temporal.io/blog/mastering-saga-patterns-for-distributed-transactions-in-microservices)

여러 애그리거트/서비스에 걸친 비즈니스 트랜잭션을 관리하는 패턴이다. 분산 환경에서 2PC(Two-Phase Commit) 대신 사용한다.

### 8.1 두 가지 구현 방식

| 방식 | 설명 | 장점 | 단점 |
|------|------|------|------|
| Choreography (코레오그래피) | 각 서비스가 이벤트를 발행하고 구독하여 자율적으로 다음 단계를 실행 | 단순, 느슨한 결합 | 순환 의존 위험, 흐름 파악 어려움 |
| Orchestration (오케스트레이션) | 중앙 오케스트레이터가 각 서비스에 무엇을 해야 하는지 지시 | 흐름이 명확, 서비스 추가 용이 | 오케스트레이터에 로직 집중 |

### 8.2 보상 트랜잭션 (Compensating Transaction)

Saga의 핵심은 **보상 트랜잭션**이다. 중간 단계가 실패하면, 이미 완료된 단계를 되돌리는 보상 행동을 실행한다. 보상 트랜잭션은 반드시 **멱등성(idempotent)**이 있어야 하며 재시도 가능해야 한다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


# === Orchestration 방식 Saga 구현 ===

class StepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    """Saga의 각 단계를 정의"""
    name: str
    action: callable       # 실행할 동작
    compensation: callable  # 보상 동작 (롤백)
    status: StepStatus = StepStatus.PENDING


class SagaOrchestrator:
    """Saga 오케스트레이터: 단계별 실행과 보상을 관리"""

    def __init__(self, steps: List[SagaStep]):
        self._steps = steps
        self._completed_steps: List[SagaStep] = []

    def execute(self) -> bool:
        """모든 단계를 순서대로 실행. 실패 시 보상 트랜잭션 실행."""
        for step in self._steps:
            try:
                logger.info(f"실행 중: {step.name}")
                step.action()
                step.status = StepStatus.COMPLETED
                self._completed_steps.append(step)
            except Exception as e:
                logger.error(f"실패: {step.name} - {e}")
                step.status = StepStatus.FAILED
                self._compensate()
                return False
        return True

    def _compensate(self) -> None:
        """완료된 단계를 역순으로 보상"""
        for step in reversed(self._completed_steps):
            try:
                logger.info(f"보상 중: {step.name}")
                step.compensation()
                step.status = StepStatus.COMPENSATED
            except Exception as e:
                logger.error(f"보상 실패: {step.name} - {e}")
                # 보상 실패 시 알림/수동 처리 필요


# === 주문 생성 Saga 예시 ===

class OrderService:
    def create_order(self, order_id: str) -> None:
        print(f"[주문] 주문 {order_id} 생성")

    def cancel_order(self, order_id: str) -> None:
        print(f"[주문] 주문 {order_id} 취소 (보상)")


class PaymentService:
    def process_payment(self, order_id: str, amount: int) -> None:
        print(f"[결제] 주문 {order_id} 결제 처리: {amount}원")

    def refund_payment(self, order_id: str) -> None:
        print(f"[결제] 주문 {order_id} 환불 (보상)")


class InventoryService:
    def reserve_stock(self, order_id: str, items: list) -> None:
        print(f"[재고] 주문 {order_id} 재고 예약")
        # 재고 부족 시 예외 발생을 시뮬레이션하려면 아래 주석 해제
        # raise Exception("재고 부족")

    def release_stock(self, order_id: str) -> None:
        print(f"[재고] 주문 {order_id} 재고 해제 (보상)")


# Saga 구성 및 실행
order_svc = OrderService()
payment_svc = PaymentService()
inventory_svc = InventoryService()

order_id = "ORD-001"

create_order_saga = SagaOrchestrator(steps=[
    SagaStep(
        name="주문 생성",
        action=lambda: order_svc.create_order(order_id),
        compensation=lambda: order_svc.cancel_order(order_id),
    ),
    SagaStep(
        name="결제 처리",
        action=lambda: payment_svc.process_payment(order_id, 50_000),
        compensation=lambda: payment_svc.refund_payment(order_id),
    ),
    SagaStep(
        name="재고 예약",
        action=lambda: inventory_svc.reserve_stock(order_id, ["item1"]),
        compensation=lambda: inventory_svc.release_stock(order_id),
    ),
])

success = create_order_saga.execute()
# 재고 예약이 실패하면: 결제 환불 -> 주문 취소 순으로 보상 실행
```

---

## 9. Domain Events 상세 패턴

> 출처: Udi Dahan, "Domain Events -- Salvation" (2009); Jimmy Bogard, "A better domain events pattern" (2014)
> 참고: [Microsoft Learn -- Domain Events Design and Implementation](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation), [microservices.io -- Domain Event](https://microservices.io/patterns/data/domain-event.html)

### 9.1 이벤트 수집 패턴 (Internal Event Collection)

> Jimmy Bogard의 "더 나은 도메인 이벤트 패턴": 이벤트를 즉시 발행하지 않고, 엔티티 내부에 수집했다가 트랜잭션 커밋 직전/직후에 디스패치한다.

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ItemAddedToCart(DomainEvent):
    cart_id: str = ""
    product_id: str = ""
    quantity: int = 0


@dataclass(frozen=True)
class CartCheckedOut(DomainEvent):
    cart_id: str = ""
    total_amount: int = 0


class AggregateRoot:
    """이벤트 수집 기능을 가진 애그리거트 루트 기반 클래스"""

    def __init__(self):
        self._domain_events: List[DomainEvent] = []

    def _raise_event(self, event: DomainEvent) -> None:
        """이벤트를 내부 컬렉션에 수집 (즉시 발행하지 않음)"""
        self._domain_events.append(event)

    @property
    def domain_events(self) -> List[DomainEvent]:
        return list(self._domain_events)

    def clear_events(self) -> None:
        self._domain_events.clear()


@dataclass
class CartItem:
    product_id: str
    quantity: int
    unit_price: int


class ShoppingCart(AggregateRoot):
    def __init__(self, cart_id: str):
        super().__init__()
        self.cart_id = cart_id
        self.items: List[CartItem] = []

    def add_item(self, product_id: str, quantity: int, unit_price: int) -> None:
        self.items.append(CartItem(product_id, quantity, unit_price))
        self._raise_event(ItemAddedToCart(
            cart_id=self.cart_id,
            product_id=product_id,
            quantity=quantity,
        ))

    def checkout(self) -> None:
        if not self.items:
            raise ValueError("장바구니가 비어 있습니다")
        total = sum(item.quantity * item.unit_price for item in self.items)
        self._raise_event(CartCheckedOut(
            cart_id=self.cart_id,
            total_amount=total,
        ))
```

### 9.2 이벤트 디스패처와 Unit of Work 연동

```python
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Type


class EventBus:
    """인프로세스 이벤트 버스 -- 이벤트 타입별 핸들러 등록 및 디스패치"""

    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)


class UnitOfWork(ABC):
    """Unit of Work -- 트랜잭션 경계에서 이벤트를 디스패치"""

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    @abstractmethod
    def commit(self) -> None:
        ...

    def _dispatch_events(self, aggregate: AggregateRoot) -> None:
        """커밋 직전에 수집된 이벤트를 디스패치"""
        for event in aggregate.domain_events:
            self._event_bus.publish(event)
        aggregate.clear_events()


# 사용 예시
event_bus = EventBus()

# 핸들러 등록
def send_checkout_email(event: CartCheckedOut) -> None:
    print(f"[이메일] 장바구니 {event.cart_id} 결제 완료 알림 발송")

def update_analytics(event: ItemAddedToCart) -> None:
    print(f"[분석] 상품 {event.product_id} 장바구니 추가 기록")

event_bus.subscribe(CartCheckedOut, send_checkout_email)
event_bus.subscribe(ItemAddedToCart, update_analytics)
```

### 9.3 Outbox 패턴

이벤트의 신뢰성 있는 발행을 보장하기 위해, 이벤트를 애그리거트와 같은 트랜잭션에서 Outbox 테이블에 저장하고, 별도 프로세스가 Outbox에서 이벤트를 읽어 메시지 브로커에 발행한다.

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OutboxMessage:
    """Outbox 테이블에 저장되는 메시지"""
    id: str
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: str         # JSON 직렬화된 이벤트 데이터
    created_at: datetime
    published: bool = False


class OutboxProcessor:
    """별도 프로세스/스케줄러: Outbox에서 미발행 메시지를 읽어 브로커에 발행"""

    def __init__(self, outbox_repo: "OutboxRepository", broker: "MessageBroker"):
        self._repo = outbox_repo
        self._broker = broker

    def process(self) -> None:
        messages = self._repo.find_unpublished()
        for msg in messages:
            self._broker.publish(topic=msg.event_type, message=msg.payload)
            msg.published = True
            self._repo.update(msg)
```

---

## 10. Python DDD 구현 패턴

> 출처: Harry Percival & Bob Gregory, "Architecture Patterns with Python" (O'Reilly, 2020)
> 원문: [cosmicpython.com](https://www.cosmicpython.com/book/preface.html)
> 참고: [eventsourcing.readthedocs.io](https://eventsourcing.readthedocs.io/en/stable/topics/domain.html), [dddinpython.com](https://dddinpython.com/index.php/2022/11/09/implementing-the-repository-pattern-using-sqlalchemy/)

### 10.1 Python Value Object 고급 패턴

```python
from dataclasses import dataclass, replace
from functools import total_ordering


@dataclass(frozen=True, slots=True)
class Money:
    """Python 3.10+ Value Object 권장 패턴

    frozen=True: 불변 보장 + __hash__ 자동 생성
    slots=True:  메모리 효율 향상 (Python 3.10+)
    """
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        """자기 검증 (Self-Validation): 생성 시점에 불변식 강제"""
        if not isinstance(self.amount, int):
            # frozen=True이므로 object.__setattr__ 사용
            object.__setattr__(self, "amount", int(self.amount))
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")
        if not self.currency:
            raise ValueError("통화 코드는 필수입니다")

    def add(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        return replace(self, amount=self.amount + other.amount)

    def subtract(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("결과 금액이 음수입니다")
        return replace(self, amount=result)

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")


# frozen=True로 인해 __eq__와 __hash__가 자동 생성됨
m1 = Money(1000, "KRW")
m2 = Money(1000, "KRW")
assert m1 == m2                   # __eq__: 값 동등성
assert hash(m1) == hash(m2)       # __hash__: set/dict에서 사용 가능
assert m1 is not m2               # 다른 인스턴스이지만 동등

# dataclasses.replace로 복사 생성 (불변 객체의 변경)
m3 = replace(m1, amount=2000)
assert m3 == Money(2000, "KRW")
```

### 10.2 SQLAlchemy Data Mapper 패턴

> "ORM이 도메인 모델을 임포트하게 하라. 도메인 모델이 ORM을 임포트하면 안 된다." -- Cosmic Python

```python
# domain/model.py -- 순수 도메인 모델 (ORM 의존성 없음)
from dataclasses import dataclass, field
from typing import List


@dataclass
class OrderLine:
    sku: str
    quantity: int


@dataclass
class Batch:
    reference: str
    sku: str
    quantity: int
    allocated: List[OrderLine] = field(default_factory=list)

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self.allocated.append(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.quantity

    @property
    def available_quantity(self) -> int:
        return self.quantity - sum(l.quantity for l in self.allocated)


# infrastructure/orm.py -- ORM이 도메인 모델에 매핑
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData
from sqlalchemy.orm import registry, relationship

metadata = MetaData()
mapper_registry = registry()

order_lines = Table(
    "order_lines", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("quantity", Integer),
)

batches = Table(
    "batches", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("quantity", Integer),
)

allocations = Table(
    "allocations", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("batch_id", Integer, ForeignKey("batches.id")),
    Column("orderline_id", Integer, ForeignKey("order_lines.id")),
)


def start_mappers():
    """도메인 모델에 ORM 매핑을 적용 -- Imperative (Classical) Mapping
    도메인 모델 코드에는 SQLAlchemy 의존성이 전혀 없다."""
    lines_mapper = mapper_registry.map_imperatively(OrderLine, order_lines)
    mapper_registry.map_imperatively(Batch, batches, properties={
        "allocated": relationship(lines_mapper, secondary=allocations),
    })
```

### 10.3 Repository + Unit of Work 패턴 (SQLAlchemy)

```python
from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.orm import Session


# 도메인 계층: 추상 리포지토리
class AbstractBatchRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch) -> None: ...

    @abstractmethod
    def get(self, reference: str) -> Optional[Batch]: ...


# 인프라 계층: SQLAlchemy 구현
class SqlAlchemyBatchRepository(AbstractBatchRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, batch: Batch) -> None:
        self._session.add(batch)

    def get(self, reference: str) -> Optional[Batch]:
        return (
            self._session.query(Batch)
            .filter_by(reference=reference)
            .first()
        )


# Unit of Work: 트랜잭션 경계 관리
class AbstractUnitOfWork(ABC):
    batches: AbstractBatchRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def __enter__(self):
        self._session: Session = self._session_factory()
        self.batches = SqlAlchemyBatchRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()


# 사용 예시: 응용 서비스에서 UoW 사용
class AllocationService:
    def allocate(self, line: OrderLine, uow: AbstractUnitOfWork) -> str:
        with uow:
            batch = uow.batches.get("batch-001")
            if batch is None:
                raise ValueError("배치를 찾을 수 없습니다")
            batch.allocate(line)
            uow.commit()
            return batch.reference
```

### 10.4 Message Bus 패턴 (Python)

> Cosmic Python의 핵심 패턴: 메시지 버스가 커맨드와 이벤트를 핸들러에 라우팅한다.

```python
from dataclasses import dataclass
from typing import Callable, Dict, List, Type, Union


# 메시지 타입 구분
class Command:
    """커맨드: 정확히 하나의 핸들러가 처리"""
    pass


class Event:
    """이벤트: 0개 이상의 핸들러가 처리"""
    pass


Message = Union[Command, Event]


@dataclass
class Allocate(Command):
    order_id: str
    sku: str
    quantity: int


@dataclass
class BatchCreated(Event):
    reference: str
    sku: str
    quantity: int


@dataclass
class AllocationRequired(Event):
    order_id: str
    sku: str
    quantity: int


class MessageBus:
    """메시지 버스: 커맨드는 단일 핸들러, 이벤트는 복수 핸들러"""

    def __init__(self):
        self._command_handlers: Dict[Type[Command], Callable] = {}
        self._event_handlers: Dict[Type[Event], List[Callable]] = {}

    def register_command(self, cmd_type: Type[Command], handler: Callable) -> None:
        self._command_handlers[cmd_type] = handler

    def register_event(self, event_type: Type[Event], handler: Callable) -> None:
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def handle(self, message: Message) -> None:
        if isinstance(message, Command):
            handler = self._command_handlers.get(type(message))
            if handler is None:
                raise ValueError(f"핸들러가 없습니다: {type(message)}")
            handler(message)
        elif isinstance(message, Event):
            for handler in self._event_handlers.get(type(message), []):
                handler(message)


# 핸들러 등록 예시
bus = MessageBus()

def handle_allocate(cmd: Allocate) -> None:
    print(f"재고 할당: {cmd.sku} x {cmd.quantity} for {cmd.order_id}")

def send_allocation_notification(event: AllocationRequired) -> None:
    print(f"알림: {event.order_id}에 대한 할당이 필요합니다")

def log_allocation_event(event: AllocationRequired) -> None:
    print(f"로그: AllocationRequired 이벤트 기록")

bus.register_command(Allocate, handle_allocate)
bus.register_event(AllocationRequired, send_allocation_notification)
bus.register_event(AllocationRequired, log_allocation_event)

# 커맨드: 정확히 1개의 핸들러가 처리
bus.handle(Allocate(order_id="O-001", sku="DESK-001", quantity=2))

# 이벤트: 등록된 모든 핸들러가 처리
bus.handle(AllocationRequired(order_id="O-001", sku="DESK-001", quantity=2))
```

### 10.5 Python DDD 프로젝트 구조

> 참고: [qu3vipon/python-ddd](https://github.com/qu3vipon/python-ddd), [iktakahiro/dddpy](https://github.com/iktakahiro/dddpy), [thinhdanggroup.github.io](https://thinhdanggroup.github.io/python-code-structure/)

```
my_project/
├── src/
│   ├── ordering/                    # 바운디드 컨텍스트: 주문
│   │   ├── domain/                  # 도메인 계층 (의존성 없음)
│   │   │   ├── __init__.py
│   │   │   ├── model.py             # 엔티티, 값 객체, 애그리거트
│   │   │   ├── events.py            # 도메인 이벤트 정의
│   │   │   ├── commands.py          # 커맨드 정의
│   │   │   ├── specifications.py    # Specification 패턴
│   │   │   └── repository.py        # 리포지토리 인터페이스 (ABC)
│   │   │
│   │   ├── application/             # 응용 계층
│   │   │   ├── __init__.py
│   │   │   ├── services.py          # 유스케이스/응용 서비스
│   │   │   ├── handlers.py          # 커맨드/이벤트 핸들러
│   │   │   └── unit_of_work.py      # UoW 인터페이스
│   │   │
│   │   ├── infrastructure/          # 인프라 계층
│   │   │   ├── __init__.py
│   │   │   ├── orm.py               # SQLAlchemy 매핑
│   │   │   ├── repository.py        # 리포지토리 구현체
│   │   │   ├── unit_of_work.py      # UoW 구현체
│   │   │   └── event_publisher.py   # 이벤트 발행 구현
│   │   │
│   │   └── interface/               # 표현 계층 (입력 어댑터)
│   │       ├── __init__.py
│   │       ├── api.py               # REST API (FastAPI/Flask)
│   │       └── schemas.py           # 요청/응답 스키마
│   │
│   ├── inventory/                   # 바운디드 컨텍스트: 재고
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── interface/
│   │
│   └── shared_kernel/               # 공유 커널 (공통 값 객체)
│       ├── __init__.py
│       ├── money.py
│       └── events.py                # 통합 이벤트 기반 클래스
│
├── tests/
│   ├── unit/                        # 도메인 로직 단위 테스트
│   ├── integration/                 # 인프라 통합 테스트
│   └── e2e/                         # 엔드투엔드 테스트
│
└── pyproject.toml
```

**핵심 의존성 규칙:**
- `domain/` -- 어디에도 의존하지 않는다. 순수 Python만 사용
- `application/` -- `domain/`에만 의존한다
- `infrastructure/` -- `domain/`과 `application/`에 의존한다 (인터페이스 구현)
- `interface/` -- `application/`에 의존한다 (유스케이스 호출)

---

## 11. DDD Distilled (Vaughn Vernon) 핵심 요약

> 출처: Vaughn Vernon, "Domain-Driven Design Distilled" (Addison-Wesley, 2016)
> 참고: [Amazon](https://www.amazon.com/Domain-Driven-Design-Distilled-Vaughn-Vernon/dp/0134434420), [happycoders.eu](https://www.happycoders.eu/books/domain-driven-design-distilled/)

내부 자료에서 다루지 않는 Vernon의 핵심 강조점을 정리한다.

### 11.1 "DDD는 주로 바운디드 컨텍스트 안에서 모델링하는 것"

Vernon은 DDD의 핵심을 한 문장으로 요약한다: "DDD는 명시적으로 경계 지어진 컨텍스트 안에서 솔루션을 모델링하고, 다른 바운디드 컨텍스트와의 통합을 지원하는 것이다."

### 11.2 Event Storming을 도메인 발견의 핵심 도구로 제시

DDD Distilled는 Event Storming을 전략 설계의 실행 방법론으로 상세히 다룬다. 이는 Evans의 파란책에는 없는 내용이다.

### 11.3 전략 설계 우선 (Strategic Design First)

Vernon은 많은 팀이 전술 패턴(Entity, Repository 등)에만 집중하는 실수를 지적하며, **전략 설계가 먼저**라는 원칙을 강조한다:

1. 핵심 도메인을 식별하라
2. 바운디드 컨텍스트를 설계하라
3. 컨텍스트 매핑을 정의하라
4. **그 다음에** 전술 패턴을 적용하라

---

## 12. Patterns, Principles, and Practices of DDD (Scott Millett)

> 출처: Scott Millett & Nick Tune, "Patterns, Principles, and Practices of Domain-Driven Design" (Wrox, 2015)
> 참고: [Amazon](https://www.amazon.com/Patterns-Principles-Practices-Domain-Driven-Design/dp/1118714709), [Wiley](https://www.wiley.com/en-us/Patterns,+Principles,+and+Practices+of+Domain+Driven+Design-p-9781118714706)

### 12.1 빈혈 도메인 모델 vs 풍부한 도메인 모델

Millett는 두 모델의 차이를 가장 실무적으로 설명한다.

```python
# === 빈혈 도메인 모델 (Anemic Domain Model) -- 안티패턴 ===
# Martin Fowler가 2003년에 안티패턴으로 명명
# Millett는 이것이 "가장 흔한 DDD 실패 사례"라고 지적

@dataclass
class OrderAnemic:
    """데이터만 있고 행동이 없는 빈혈 모델"""
    id: str
    customer_id: str
    items: list
    status: str
    total: int


class OrderServiceAnemic:
    """모든 비즈니스 로직이 서비스에 집중 -- 절차적 프로그래밍과 동일"""

    def place_order(self, order: OrderAnemic) -> None:
        if not order.items:
            raise ValueError("상품이 없습니다")
        order.total = sum(i["price"] * i["qty"] for i in order.items)
        order.status = "placed"
        # 도메인 객체는 단순 데이터 홀더에 불과함

    def cancel_order(self, order: OrderAnemic) -> None:
        if order.status not in ("placed", "preparing"):
            raise ValueError("취소 불가")
        order.status = "cancelled"


# === 풍부한 도메인 모델 (Rich Domain Model) -- DDD 지향 ===

class OrderStatus(Enum):
    PLACED = "placed"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


@dataclass
class OrderRich:
    """행동과 불변식을 캡슐화한 풍부한 도메인 모델"""
    id: str
    customer_id: str
    _items: List[dict] = field(default_factory=list)
    _status: OrderStatus = OrderStatus.PLACED
    _total: int = 0

    def __post_init__(self):
        if not self._items:
            raise ValueError("최소 한 개의 상품이 필요합니다")
        self._recalculate()

    def cancel(self) -> None:
        """비즈니스 규칙이 도메인 객체 안에 있다"""
        if self._status not in (OrderStatus.PLACED, OrderStatus.PREPARING):
            raise ValueError(f"{self._status.value} 상태에서는 취소할 수 없습니다")
        self._status = OrderStatus.CANCELLED

    def _recalculate(self) -> None:
        self._total = sum(i["price"] * i["qty"] for i in self._items)
```

### 12.2 문제 공간과 솔루션 공간의 명확한 분리

Millett는 DDD의 두 공간을 체계적으로 구분한다:

| 구분 | 문제 공간 (Problem Space) | 솔루션 공간 (Solution Space) |
|------|-------------------------|---------------------------|
| 질문 | "비즈니스가 해결해야 할 문제는 무엇인가?" | "문제를 어떻게 소프트웨어로 해결할 것인가?" |
| 도구 | 도메인, 하위 도메인 | 바운디드 컨텍스트, 컨텍스트 맵 |
| 활동 | 도메인 발견, 지식 탐구 | 모델링, 설계, 구현 |
| 산출물 | 도메인 비전 선언문, 하위 도메인 맵 | 유비쿼터스 언어, 도메인 모델, 코드 |

---

## 13. DDD와 마이크로서비스

> 참고: [Microsoft Learn -- Use Tactical DDD to Design Microservices](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-ddd), [Microsoft Learn -- Identify Microservice Domain Model Boundaries](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/architect-microservice-container-applications/identify-microservice-domain-model-boundaries)

### 13.1 바운디드 컨텍스트 = 마이크로서비스 경계

바운디드 컨텍스트는 마이크로서비스의 자연스러운 경계가 된다. 각 마이크로서비스는:
- 하나의 바운디드 컨텍스트에 대응
- 자체 데이터베이스를 소유 (Database per Service)
- 다른 서비스와는 API 또는 이벤트로 통신

### 13.2 컨텍스트 매핑 패턴의 마이크로서비스 적용

| 컨텍스트 매핑 패턴 | 마이크로서비스 통합 방식 |
|----------------|-------------------|
| OHS + Published Language | REST API, gRPC, GraphQL |
| ACL | API Gateway, 어댑터 서비스 |
| Event-Driven | 메시지 브로커 (Kafka, RabbitMQ) |
| Shared Kernel | 공유 라이브러리 (최소화 필수) |
| Separate Ways | 기능 중복 허용 |

```python
# 마이크로서비스 간 통합 이벤트 (Integration Event)
# 도메인 이벤트와 구분해야 한다

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class IntegrationEvent:
    """바운디드 컨텍스트 간 통신을 위한 통합 이벤트
    도메인 이벤트(내부용)와 달리, Published Language로 직렬화된다."""
    event_id: str
    event_type: str
    occurred_at: datetime
    source_context: str
    payload: dict


# 주문 컨텍스트가 발행하는 통합 이벤트
order_completed_event = IntegrationEvent(
    event_id="evt-001",
    event_type="ordering.order_completed",
    occurred_at=datetime.now(),
    source_context="ordering",
    payload={
        "order_id": "ORD-001",
        "customer_id": "CUST-001",
        "total_amount": 150000,
        "items": [
            {"sku": "PROD-001", "quantity": 2},
            {"sku": "PROD-002", "quantity": 1},
        ],
    },
)


# 재고 컨텍스트의 ACL: 통합 이벤트를 내부 도메인 커맨드로 변환
class InventoryACL:
    """재고 컨텍스트의 충돌 방지 계층:
    주문 컨텍스트의 통합 이벤트를 재고 도메인의 언어로 번역"""

    def translate_order_completed(self, event: IntegrationEvent) -> list:
        commands = []
        for item in event.payload["items"]:
            commands.append({
                "type": "decrease_stock",
                "sku": item["sku"],
                "quantity": item["quantity"],
                "reason": f"주문 {event.payload['order_id']} 확정",
            })
        return commands
```

---

## 출처 종합

### 서적
- Eric Evans, "Domain-Driven Design: Tackling Complexity in the Heart of Software" (Addison-Wesley, 2003)
- Eric Evans, [DDD Reference 2015](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) (무료 PDF)
- Vaughn Vernon, "Domain-Driven Design Distilled" (Addison-Wesley, 2016)
- Scott Millett & Nick Tune, "Patterns, Principles, and Practices of Domain-Driven Design" (Wrox, 2015)
- Harry Percival & Bob Gregory, "Architecture Patterns with Python" (O'Reilly, 2020) -- [cosmicpython.com](https://www.cosmicpython.com/)
- Alberto Brandolini, "Introducing EventStorming" (Leanpub) -- [eventstorming.com](https://www.eventstorming.com/)

### 논문/시리즈
- Vaughn Vernon, ["Effective Aggregate Design" Part I-III](https://www.dddcommunity.org/library/vernon_2011/) (2011)
- Hector Garcia-Molina & Kenneth Salem, "Sagas" (1987)

### 웹 자료
- Martin Fowler, [CQRS](https://martinfowler.com/bliki/CQRS.html)
- Martin Fowler, [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
- Martin Fowler, [What do you mean by "Event-Driven"?](https://martinfowler.com/articles/201701-event-driven.html)
- Martin Fowler, [Bounded Context](https://martinfowler.com/bliki/BoundedContext.html)
- Martin Fowler, [DDD Tagged Articles](https://martinfowler.com/tags/domain%20driven%20design.html)
- Martin Fowler, [Conway's Law](https://martinfowler.com/bliki/ConwaysLaw.html)
- [Microsoft Learn -- CQRS Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Microsoft Learn -- Event Sourcing Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
- [Microsoft Learn -- Saga Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)
- [Microsoft Learn -- Tactical DDD for Microservices](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-ddd)
- [microservices.io -- Saga Pattern](https://microservices.io/patterns/data/saga.html)
- [microservices.io -- Domain Event](https://microservices.io/patterns/data/domain-event.html)
- [Open Group -- DDD Strategic Patterns](https://pubs.opengroup.org/architecture/o-aa-standard/DDD-strategic-patterns.html)
- [Context Mapper](https://contextmapper.org/docs/)
- [DDD Crew -- Context Mapping](https://github.com/ddd-crew/context-mapping)
- [Wikipedia -- Specification Pattern](https://en.wikipedia.org/wiki/Specification_pattern)
- [Wikipedia -- Event Storming](https://en.wikipedia.org/wiki/Event_storming)
- [eventsourcing (Python library)](https://eventsourcing.readthedocs.io/en/stable/)
- [Ardalis -- Conway's Law, DDD, and Microservices](https://ardalis.com/conways-law-ddd-and-microservices/)
- [ArchMan -- Team Topologies and Conway's Law Alignment](https://archman.dev/docs/domain-driven-design/strategic-design/team-topologies-and-conways-law-alignment)
