# DDD(도메인 주도 설계) 종합 가이드

## P1 Source Sufficiency

| field | value |
|---|---|
| purpose | DDD/domain modeling decisions: subdomain discovery, bounded context, ubiquitous language, aggregates, invariants, domain events/services, and consistency boundaries. |
| use when | Domain language, business policy, state transition, aggregate boundary, or context boundary is unclear. |
| exclude/handoff | Do not use for schema tuning, REST status codes, Django code mechanics, or pytest fixture mechanics except as domain input to owning references. |
| core criteria | Strategic design before tactical patterns; model with domain experts and ubiquitous language; aggregate boundaries protect invariants; cross-aggregate consistency and events require explicit tradeoffs. |
| source priority | 1 primary DDD books/reference material by Evans and Vernon; 2 primary/reputable DDD and architecture books; 3 reputable engineering articles by Fowler, Bogard, Microsoft, and DDD community sources; 4 internal Korean summaries only as synthesis. |
| P1 classification | sufficient |

> **Internal 출처:** [A] 도메인 주도 개발 시작하기, [B] 도메인 주도 설계 첫걸음, [C] 도메인 주도 설계 구현(빨간책)
> **External 출처:** Eric Evans 파란책, Vaughn Vernon "Effective Aggregate Design" / "DDD Distilled", Scott Millett, Harry Percival & Bob Gregory "Cosmic Python", Greg Young, Martin Fowler, Alberto Brandolini

---

## 1. DDD란 무엇인가

DDD(Domain-Driven Design)는 복잡한 소프트웨어를 비즈니스 도메인 중심으로 설계하는 방법론이다. 소프트웨어의 핵심은 비즈니스 도메인이며, 도메인 전문가와 개발자가 공통 언어를 사용하여 모델을 구축하고 이를 코드로 구현한다.

### 1.1 DDD의 핵심 요약

> "DDD는 명시적으로 경계 지어진 컨텍스트 안에서 솔루션을 모델링하고, 다른 바운디드 컨텍스트와의 통합을 지원하는 것이다." -- Vaughn Vernon, DDD Distilled

### 1.2 전략 설계 우선 원칙

> **[의사결정 #6] External 채택**: 전략 설계(바운디드 컨텍스트, 컨텍스트 맵)가 반드시 전술 패턴보다 먼저다.

Vernon은 많은 팀이 전술 패턴(Entity, Repository 등)에만 집중하는 실수를 지적하며, 전략 설계가 먼저라는 원칙을 강조한다 (Vernon, DDD Distilled):

1. 핵심 도메인을 식별하라
2. 바운디드 컨텍스트를 설계하라
3. 컨텍스트 매핑을 정의하라
4. **그 다음에** 전술 패턴을 적용하라

전술 패턴 중심의 실무 가이드 ([A] 도메인 주도 개발 시작하기)는 구현 단계에서 활용하되, 전략 설계 없이 전술 패턴만 적용하면 "잘못된 경계에서 좋은 코드를 작성하는 결과"가 된다.

### 1.3 주요 참고 자료의 관점 차이

| 관점 | [A] 도메인 주도 개발 시작하기 | [B] 도메인 주도 설계 첫걸음 | [C] 도메인 주도 설계 구현(빨간책) |
|------|--------------------------|--------------------------|-------------------------------|
| 초점 | 전술 패턴 중심의 실무 구현 | 전략 패턴 중심의 비즈니스 분석 | 전략+전술을 아키텍처와 함께 종합 |
| 대상 | DDD 입문자 | 비즈니스 설계자/아키텍트 | 실무 구현 개발자 |
| 강조점 | 계층 아키텍처와 DIP | 하위 도메인 유형과 바운디드 컨텍스트 경계 | 핵사고날 아키텍처와 CQRS |

---

## 2. 전략 패턴 (Strategic Patterns)

### 2.1 지식 탐구 (Knowledge Crunching)

> 출처: Eric Evans, "DDD" Part I

Evans는 유비쿼터스 언어를 만드는 **과정** 자체를 핵심으로 강조한다. 지식 탐구(Knowledge Crunching)란 도메인 전문가로부터 쏟아지는 정보의 홍수 속에서 관련 있는 것만 걸러내고, 하나의 조직 아이디어를 시도한 뒤 또 다른 아이디어로 교체하며, 복잡한 데이터를 단순하게 설명하는 관점을 찾아가는 반복 과정이다.

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
from dataclasses import dataclass
from typing import Optional


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

### 2.2 도메인과 하위 도메인

> 출처: [A][B][C], Evans 파란책, Millett

도메인은 소프트웨어가 해결하려는 비즈니스 영역이며, 여러 하위 도메인으로 구성된다. [C]에서는 하위 도메인을 "문제점 공간(problem space)"의 일부로 정의하고, 바운디드 컨텍스트를 "해결책 공간(solution space)"으로 분리하여 설명한다.

**하위 도메인 유형** [B]:

| 유형 | 경쟁 우위 | 복잡성 | 변동성 | 솔루션 전략 |
|------|----------|--------|--------|------------|
| 핵심(Core) | 직접적 경쟁력 | 높음 | 잦은 변경 | 사내 구현 필수 |
| 일반(Generic) | 없음 | 높음 (알려진 문제) | 낮음 | 외부 솔루션/오픈소스 |
| 지원(Supporting) | 없음 | 낮음 (CRUD 수준) | 낮음 | 하청 가능, RAD |

**문제 공간과 솔루션 공간의 분리** (Millett):

| 구분 | 문제 공간 (Problem Space) | 솔루션 공간 (Solution Space) |
|------|-------------------------|---------------------------|
| 질문 | "비즈니스가 해결해야 할 문제는 무엇인가?" | "문제를 어떻게 소프트웨어로 해결할 것인가?" |
| 도구 | 도메인, 하위 도메인 | 바운디드 컨텍스트, 컨텍스트 맵 |
| 활동 | 도메인 발견, 지식 탐구 | 모델링, 설계, 구현 |
| 산출물 | 도메인 비전 선언문, 하위 도메인 맵 | 유비쿼터스 언어, 도메인 모델, 코드 |

```python
from dataclasses import dataclass
from enum import Enum


class SubdomainType(Enum):
    CORE = "core"           # 핵심: 경쟁 우위의 원천
    GENERIC = "generic"     # 일반: 모든 회사가 동일하게 수행
    SUPPORTING = "supporting"  # 지원: 비즈니스 활동 보조


@dataclass(frozen=True)
class Subdomain:
    name: str
    type: SubdomainType
    description: str

    @property
    def should_build_in_house(self) -> bool:
        return self.type == SubdomainType.CORE


# 예시: 온라인 쇼핑몰 도메인 분석
recommendation_engine = Subdomain(
    name="추천 엔진",
    type=SubdomainType.CORE,
    description="사용자 행동 기반 개인화 추천 알고리즘",
)

authentication = Subdomain(
    name="인증/권한",
    type=SubdomainType.GENERIC,
    description="사용자 로그인 및 권한 관리",
)

admin_panel = Subdomain(
    name="관리자 페이지",
    type=SubdomainType.SUPPORTING,
    description="상품/주문 CRUD 인터페이스",
)
```

### 2.3 유비쿼터스 언어 (Ubiquitous Language)

> 출처: [A][B][C], Evans 파란책

도메인 전문가, 관계자, 개발자가 공통으로 사용하는 언어다. 코드, 문서, 대화 모든 곳에서 동일한 용어를 사용한다.

**핵심 원칙:**
- 기술 용어가 아닌 비즈니스 용어로 구성해야 한다
- 모호성이 없어야 하며 하나의 용어는 하나의 의미만 가져야 한다
- 유비쿼터스 언어는 바운디드 컨텍스트 경계 안에서만 보편적으로 적용된다

[B]는 유비쿼터스 언어를 포착하는 도구로 **거킨 테스트(Gherkin test)**를 강조한다:

```gherkin
Scenario: 에이전트에게 새로운 지원 케이스를 알린다
  Given: 빈센트 줄스는 새로운 지원 케이스를 제출한다
  When: 티켓이 울프씨에게 할당된다
  Then: 에이전트는 새로운 티켓에 대해 알림을 받는다
```

```python
# 유비쿼터스 언어가 반영되지 않은 코드 (나쁜 예)
class OrderManager:
    def process(self, data: dict):
        data["status"] = 2  # 매직 넘버, 비즈니스 의미 불명확
        self.db.update(data)


# 유비쿼터스 언어가 반영된 코드 (좋은 예)
class Order:
    """주문 애그리거트 - '주문'이라는 도메인 용어를 그대로 사용"""

    def place(self) -> None:
        """주문을 '접수'한다"""
        self._status = OrderStatus.PLACED

    def ship(self) -> None:
        """주문을 '출고'한다"""
        if not self._status.is_shippable:
            raise OrderCannotBeShippedException("출고 가능한 상태가 아닙니다")
        self._status = OrderStatus.SHIPPED
```

### 2.4 바운디드 컨텍스트 (Bounded Context)

> 출처: [A][B][C], Evans 파란책

유비쿼터스 언어가 적용되는 명시적 경계다. 같은 용어(예: "리드")가 마케팅과 영업에서 다른 의미를 가질 때, 각각을 별도의 바운디드 컨텍스트로 분리한다.

**관점 차이:**
- [B]: "하위 도메인은 발견하고, 바운디드 컨텍스트는 설계한다"는 점을 가장 강조. 바운디드 컨텍스트는 물리적/소유권 경계이며, 한 팀에서만 구현/유지관리해야 한다.
- [C]: 바운디드 컨텍스트를 "도메인 모델을 적용할 수 있는 개념적 경계"로 정의. 하나의 바운디드 컨텍스트는 하나의 프로젝트 안에 머물러야 하며, 유스케이스 집합을 포함한다.
- [A]: 바운디드 컨텍스트보다는 도메인 영역 내부의 모듈 구성에 집중한다.

하위 도메인과 바운디드 컨텍스트를 1:1로 묶으려는 시도는 바람직한 목표이지만, 반드시 그래야 하는 것은 아니다 [C].

```python
# 마케팅 컨텍스트에서의 '리드'
# marketing/domain/lead.py
@dataclass
class Lead:
    """잠재 고객 - 마케팅 채널을 통해 유입된 연락처"""
    contact_id: str
    source_channel: str  # 유입 채널
    campaign_id: str     # 캠페인 ID

    def qualify(self) -> None:
        """리드를 검증하여 MQL(Marketing Qualified Lead)로 전환"""
        ...


# 영업 컨텍스트에서의 '리드'
# sales/domain/lead.py
@dataclass
class Lead:
    """영업 기회 - 영업 파이프라인에 진입한 잠재 거래"""
    opportunity_id: str
    estimated_revenue: Money
    assigned_sales_rep: str

    def convert_to_deal(self) -> "Deal":
        """리드를 거래(Deal)로 전환"""
        ...
```

### 2.5 컨텍스트 맵 (Context Map)

> 출처: [B][C], Evans 파란책 Chapter 14, Open Group DDD Strategic Patterns

바운디드 컨텍스트 간의 관계를 시각적으로 표현한 도식이다.

**전체 연동 패턴 정리:**

| 패턴 그룹 | 패턴 | 설명 | 선택 기준 |
|-----------|------|------|----------|
| 협력형 | 파트너십(Partnership) | 양 팀이 애드훅 방식으로 API 변경을 조정 | 두 컨텍스트의 개발 실패가 양쪽 모두의 배포 실패를 야기할 때 |
| 협력형 | 공유 커널(Shared Kernel) | 모델의 일부를 공유 | 중복 비용 > 조율 비용일 때만 사용. 공유 범위 최소화 필수 |
| 사용자-제공자 | 고객-공급자(Customer-Supplier) | 업스트림이 다운스트림 요구를 계획에 반영 | 업스트림이 다운스트림 없이도 성공 가능할 때 |
| 사용자-제공자 | 순응주의자(Conformist) | 업스트림 모델을 그대로 수용 | 업스트림이 다운스트림 요구를 수용할 의지/능력이 없을 때 |
| 사용자-제공자 | 충돌 방지 계층(ACL) | 업스트림 모델을 자신의 모델로 변환 | 업스트림 모델이 다운스트림 도메인과 맞지 않을 때 |
| 제공형 | 오픈 호스트 서비스(OHS) | 퍼블릭 프로토콜로 다수 다운스트림에 서비스 | REST API, gRPC 등 공개 인터페이스 |
| 제공형 | 발행된 언어(Published Language) | OHS와 함께 사용하는 공유 언어 | JSON Schema, Protobuf, Avro 등 |
| 분리형 | 분리된 노선(Separated Ways) | 통합하지 않고 기능 중복 허용 | 통합 비용 > 기능 중복 비용일 때 |
| 분리형 | 큰 진흙공(Big Ball of Mud) | 경계가 없는 혼돈 상태 | ACL을 두어 진흙 공이 퍼지지 않도록 방어 |

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


# === 충돌 방지 계층(ACL) 패턴 구현 예시 ===

# 외부 시스템(업스트림)의 모델 - 우리가 제어할 수 없음
@dataclass
class ExternalUserDTO:
    """외부 인증 시스템의 사용자 데이터"""
    usr_id: str
    usr_nm: str
    usr_email: str
    role_cd: int


# 우리 도메인(다운스트림)의 모델
@dataclass(frozen=True)
class Author:
    """협업 컨텍스트에서의 작성자 값 객체"""
    user_id: str
    display_name: str
    email: str


# ACL: 외부 모델을 내부 모델로 변환하는 계층
class CollaboratorTranslator:
    """충돌 방지 계층 - 외부 인증 컨텍스트의 모델을
    협업 컨텍스트의 도메인 모델로 변환한다"""

    def to_author(self, external_user: ExternalUserDTO) -> Author:
        return Author(
            user_id=external_user.usr_id,
            display_name=external_user.usr_nm,
            email=external_user.usr_email,
        )


# === 레거시 ERP ACL 예시 (External) ===

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

**ACL을 선택하는 조건:**
- 외부/레거시 용어가 애그리거트, 값 객체, 유비쿼터스 언어로 누수될 위험이 있다.
- 업스트림 lifecycle과 다운스트림 lifecycle이 다르다.
- 공개 통합 계약과 내부 모델의 의미가 다르다.

**회피하는 조건:**
- 외부 모델이 이미 바운디드 컨텍스트 언어와 일치한다.
- 단순 field rename 수준이며 별도 의미 번역이 없다.

ACL은 경계 근처에 둔다. 여러 도메인 객체 내부에 번역 로직을 산발적으로 넣지 않는다. 데이터 형태뿐 아니라 status, 단위, 식별자, lifecycle 의미를 번역한다. 공개 API의 published language와 versioning이 관련되면 `architecture-api`로 넘긴다.

**BC 간 enum·상수 공유 경계.** 상수·Enum은 기본적으로 그것을 소유한 바운디드 컨텍스트 내부 자산이다 — 다른 BC가 내부 Enum을 직접 import하지 않는다(유비쿼터스 언어는 BC 경계 안에서만 보편 §2.3; 같은 철자라도 컨텍스트마다 다른 개념). BC 간 연결은 published service 계약 타입 또는 wire value로 하고, 같은 wire 값을 BC마다 각자 선언하는 것은 지식의 중복이 아니라 **published language 수용**이다 — 상대 모델의 의미가 어긋나면 그때 ACL로 번역한다. 공용 승격은 **공유 커널 결정**이다: 같은 철자를 넘어 같은 지식임이 확인되고, 결정 가능한 대리 기준으로 **두 BC가 같은 변경 사유로 함께 수정된다는 근거가 명세에 있을 때만** — 공유 범위 최소화 필수(위 표). 승격된 enum은 `common/enum/`에 두며, 공유 커널은 도메인의 일부로 취급되어 domain_layer가 의존할 수 있는 유일한 외부다(배치·의존 예외는 `discipline-houserules`). 발행 이벤트 봉투의 discriminator enum(§3.7 birth-enum)도 같은 원리다 — 발행 BC 내부 자산이고, 소비 BC는 wire 값을 각자 수용하며 발행 enum을 import하지 않는다.

### 2.6 증류 (Distillation)

> 출처: Evans 파란책 Chapter 15

핵심 도메인을 식별하고 나머지로부터 분리하는 체계적 기법이다.

| 패턴 | 설명 |
|------|------|
| 핵심 도메인 (Core Domain) | 시스템의 가장 가치 있는 부분. 최고의 인재를 투입해야 한다 |
| 일반 하위 도메인 (Generic Subdomain) | 프로젝트의 동기가 아닌 부분. 별도 모듈에 제네릭 모델로 분리 |
| 도메인 비전 선언문 (Domain Vision Statement) | 핵심 도메인의 가치와 차별점을 한 페이지로 서술한 문서 |
| 하이라이트 코어 (Highlighted Core) | 핵심 도메인의 핵심 요소를 간결하게 3~7페이지 문서로 정리하거나, 코드에서 핵심 부분을 마킹 |
| 응집력 있는 메커니즘 (Cohesive Mechanism) | 복잡한 계산/알고리즘을 별도 라이브러리로 추출. 도메인 모델은 "무엇을"만 표현 |
| 분리된 핵심 (Segregated Core) | 핵심 도메인을 별도 모듈로 물리적 분리 |
| 추상 핵심 (Abstract Core) | 핵심 개념들의 추상화를 별도 모듈에 배치. 구현은 하위 모듈에 위임 |

```python
from abc import ABC, abstractmethod


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

    def calculate_vat(self, amount: "Money", country_code: str) -> "Money":
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
        return sorted(destinations)  # 단순화된 예시
```

### 2.7 Event Storming (이벤트 스토밍)

> 출처: Alberto Brandolini, "Introducing EventStorming"; Vernon "DDD Distilled"

도메인 발견 기법이다. DDD의 전략 설계(바운디드 컨텍스트 식별, 핵심 도메인 발견)를 실행하기 위한 워크숍 방법론이다.

**포스트잇 색상 체계:**

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

**세 가지 변형:**

| 변형 | 목적 | 참여자 | 결과물 |
|------|------|--------|--------|
| Big Picture | 전체 비즈니스 프로세스를 조감도로 파악 | 10~30명, 다양한 부서 | 바운디드 컨텍스트 경계 후보 |
| Process Modelling | 특정 비즈니스 프로세스를 상세 모델링 | 5~10명, 도메인 전문가 + 개발자 | 커맨드, 이벤트, 정책 흐름 |
| Software Design | 구체적인 소프트웨어 설계로 전환 | 3~5명, 개발 팀 | 애그리거트, 읽기 모델, 외부 시스템 설계 |

### 2.8 전략 DDD와 팀 토폴로지

> 출처: Matthew Skelton & Manuel Pais, "Team Topologies" (2019); Martin Fowler, Conway's Law

**Conway의 법칙:** "시스템을 설계하는 조직은 자신의 커뮤니케이션 구조를 복제하는 설계를 산출하게 된다."

**역 Conway 기동(Inverse Conway Maneuver):** 원하는 소프트웨어 아키텍처를 먼저 설계하고, 그에 맞게 팀 구조를 의도적으로 재편한다.

| 팀 토폴로지 유형 | DDD 개념 매핑 |
|---------------|-------------|
| Stream-aligned Team | 핵심/지원 하위 도메인의 바운디드 컨텍스트를 소유 |
| Platform Team | 일반 하위 도메인에 해당. 공통 인프라를 OHS로 제공 |
| Enabling Team | 컨텍스트 매핑에서 Partnership 관계 |
| Complicated Subsystem Team | 응집력 있는 메커니즘(Cohesive Mechanism) 담당 |

---

## 3. 전술 패턴 (Tactical Patterns)

### 3.1 값 객체 (Value Object)

> 출처: [A][B][C], Evans 파란책, Cosmic Python

고유 식별자가 없으며, 개념적으로 완전한 하나를 표현한다. 불변(immutable)이어야 한다.

**핵심 원칙:**
- 식별자 없이 속성의 조합으로 동등성을 판단한다
- 반드시 불변이어야 한다 (setter 금지)
- 부작용과 동시성 문제가 없다
- [B] 값 객체가 유비쿼터스 언어 자체가 될 수 있다: `_countryCode: str` 대신 `_country: CountryCode`

```python
from dataclasses import dataclass, replace


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
            object.__setattr__(self, "amount", int(self.amount))
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")
        if not self.currency:
            raise ValueError("통화 코드는 필수입니다")

    def add(self, other: "Money") -> "Money":
        """부작용 없는 함수: 기존 객체를 변경하지 않고 새 객체를 반환"""
        self._ensure_same_currency(other)
        return replace(self, amount=self.amount + other.amount)

    def subtract(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("결과 금액이 음수입니다")
        return replace(self, amount=result)

    def multiply(self, factor: int) -> "Money":
        return replace(self, amount=self.amount * factor)

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")


@dataclass(frozen=True)
class Address:
    """주소 값 객체 - 개념적으로 완전한 하나를 표현"""
    city: str
    street: str
    zipcode: str


@dataclass(frozen=True)
class PhoneNumber:
    """전화번호 값 객체 [B] - 유효성 검사 로직을 캡슐화"""
    number: str

    def __post_init__(self):
        import re
        if not re.match(r"^\d{2,3}-\d{3,4}-\d{4}$", self.number):
            raise ValueError(f"유효하지 않은 전화번호: {self.number}")
```

### 3.2 엔티티 (Entity)

> 출처: [A][B][C], Millett
> **[의사결정 #1] External 채택**: 엔티티는 애그리거트의 일부로만 사용한다.

고유 식별자를 가지며, 라이프사이클 동안 상태가 변한다. 값이 같아도 식별자가 다르면 다른 객체다.

엔티티를 애그리거트 없이 독립 사용하면 일관성 경계가 모호해진다. Millett는 빈혈 도메인 모델을 "가장 흔한 DDD 실패 사례"로 지적하며, 엔티티가 풍부한 도메인 모델의 구성 요소로서 행동과 불변식을 캡슐화해야 한다고 주장한다.

```python
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Member:
    """회원 엔티티 -- 애그리거트의 일부로서 사용"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    email: str = ""
    _password: str = field(default="", repr=False)

    def change_password(self, old_pw: str, new_pw: str) -> None:
        """도메인 규칙이 엔티티 안에 위치한다"""
        if not self.match_password(old_pw):
            raise ValueError("기존 비밀번호가 일치하지 않습니다")
        if not new_pw:
            raise ValueError("새 비밀번호가 비어있습니다")
        self._password = new_pw

    def match_password(self, password: str) -> bool:
        return self._password == password

    def __eq__(self, other):
        """엔티티의 동등성은 식별자로만 판단"""
        if not isinstance(other, Member):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
```

**빈혈 도메인 모델 vs 풍부한 도메인 모델** (Millett):

```python
# === 빈혈 도메인 모델 (Anemic Domain Model) -- 안티패턴 ===
# Martin Fowler가 2003년에 안티패턴으로 명명
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


# === 풍부한 도메인 모델 (Rich Domain Model) -- DDD 지향 ===
@dataclass
class OrderRich:
    """행동과 불변식을 캡슐화한 풍부한 도메인 모델"""
    id: str
    customer_id: str
    _items: list = field(default_factory=list)
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

**판정·불변식은 도메인이 소유하고 프로덕션 경로에서 실행된다(빈혈 차단).** 비즈니스 판정과 불변식은 도메인 애그리거트(단일 애그리거트에 담기지 않으면 도메인 서비스)가 소유하고(불변식 보호는 §3.3 규칙1), 응용 서비스는 *조회 → 도메인 기능 실행(판정·상태 변경; 위반 시 도메인 예외) → 영속화* 순서로 그것을 프로덕션 쓰기 경로에서 **실제로 호출**한다(§3.6). 응용 서비스·리포지토리·인프라(SQL/ORM)는 그 판정을 대신 내리거나 복제하지 않는다 — 판정을 인프라로 옮기면 같은 판정의 도메인 메서드가 호출되지 않는 죽은 코드가 되어 위 빈혈 모델로 회귀한다. 동시성 안전이 필요해도 판정을 SQL로 옮기지 말고, 인프라엔 경합 가드(낙관적 `version`/CAS)만 두고 충돌 시 응용 서비스가 재조회 후 도메인 메서드부터 재실행한다(메커니즘 `architecture-db` §9.5).

**상태·종류 값 집합의 표기와 계층 소유 — 단일 출처는 도메인 enum이다.** 생명주기·상태 전이·terminal 여부를 갖는 도메인 상태값과 종류 코드(type code)는 낱개 문자열 상수가 아니라 domain_layer의 `StrEnum`(또는 순수 `Enum`) 하나로 선언하고, ORM `choices`/`CheckConstraint`·presentation Schema는 거기서 파생한다 — import 방향은 infra/presentation→domain만 허용한다(`models.TextChoices` 자체 선언은 도메인 판정에 쓰이지 않는 순수 인프라 필드 한정; ORM `default=` 등 직렬화 경계는 `.value` 평탄화 — `implementation-django` §2.5). 소비는 심볼로만, 비교는 `==`로 한다 — 원시 리터럴 비교는 오타가 조용한 False로 잠복하고, `is`는 str로 흐르는 값에서 수화 누락 시 같은 실패를 오타 없이 만든다. 단 심볼 비교 자체가 목적지가 아니다: 도메인 어휘로 진술되는 복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티(§3.3의 `OrderStatus.is_shippable`)이고, 심볼 비교는 그 술어 내부·리포지토리 필터·ACL 정규화 같은 잔여 위치에 남는다(승격 판정·허용 목록은 `discipline-cleancode` §2.14). 값에 검증·연산·불변식이 붙으면(집합의 폐쇄성과 무관하게) enum이 아니라 값 객체 승격 대상이다(§3.1의 `CountryCode`·`PhoneNumber`가 그 예).

**판정을 소유하면 그 코드는 도메인 컨텍스트가 되어 표준 구조로 이주한다 — 소유는 구조까지 정한다.** 스코프가 기존 평면 코드(판정 없는 Django 모델 등)에 새 판정·불변식을 얹게 되면, 그 코드는 판정을 소유하는 도메인 컨텍스트가 된 것이므로 `domain_layer`의 애그리거트로 존재해야 한다 — 평면 모델에 판정 메서드를 직접 얹지 않는다(ORM≠도메인, 빈혈 회귀). 이주 기준은 *"레거시냐"가 아니라 "판정·불변식을 소유하느냐"*다: (1) 판정·불변식을 소유하면 도메인 컨텍스트 → 표준 구조로 이주한다. (2) 판정을 다른 컨텍스트가 소유하고 이 코드는 단순 상류 데이터 소스(필드·DB 제약만, 판정 없음)면 **도메인 판정 *실내용*(애그리거트 루트·도메인서비스의 판정 `.py` 코드)만 비운다** — 빈혈 회귀 방지로 평면 모델에 판정 메서드를 얹지 않는다. **표준 트리 *골격*은 데이터소스도 예외 없이 빈 패키지(`__init__.py`)로 실현한다 — `discipline-houserules` §0(위치·4계층·개념 1차·종류 2차) 불변식에 *깊이 면제는 없다*(이전의 '4계층/애그리거트 전개 면제'는 2026-06-08 폐지; 면제는 판정 실내용에 한정).** 데이터소스 BC: 위치 `application/<bounded_context>/`; `driven_layer/django_<bounded_context>/`에 ORM 실체; `domain_layer/<aggregate>/`에 *빈* 애그리거트 골격(종류 폴더 전부) — **애그리거트 1차 폴더명은 ORM 모델명에서 도출**(`ProductModel`→`domain_layer/product/`); 유스케이스(application feature)를 다른 BC가 소유해 이 BC엔 feature가 없으면 `application_layer`는 빈 계층 폴더로 둔다(§0-3 개념 1차는 *개념 식별 시*). `driven_layer`의 `repository`/`acl`/`adapter`·`driving_layer`의 `api`/`schema` 의미군은 빈 패키지로 존속한다. `test` 의미군은 `discipline-tdd` 입장 심사에서 실제 테스트가 승인된 경우에만 패키지와 레이아웃을 만든다. 루트 평면 `<app>/`은 `discipline-houserules` §0-1 위반이다. 이 골격 실현은 *이번 작업이 touched한* 그 코드에 한정하며, 무관·미관여 기존 앱은 §1.1로 존중한다. (3) 컨텍스트 간 접근은 ACL 또는 open_host_service(OHS)로만 한다 — 다른 컨텍스트의 `domain_layer`/`driven_layer`를 직접 import하지 않는다(패턴 §2.5, 배치 `discipline-houserules` `references/final.md` §2 컨텍스트 간 통신). 이 이주는 *판정이 새로 얹히는 그 코드*에 한정한다 — 무관·미관여 기존 코드를 표준으로 일괄 강제하지 않는다(`discipline-houserules` §1.1 — 단 기존 배치가 몇 곳에 일관돼 보여도 그것은 «확립된 규약»이 아니라 아직 안 갚은 빚이고, 트리 결정의 입력이 아니다 — 2026-08-12).

### 3.3 애그리거트 (Aggregate)

> 출처: [A][B][C], Vernon "Effective Aggregate Design"

연관된 엔티티와 값 객체를 하나로 묶은 개념적 단위다. 일관성 관리의 기준이 되며, 트랜잭션 경계이기도 하다.

#### Vernon의 4가지 설계 규칙

**규칙 1: 진짜 불변식을 일관성 경계 안에서 보호하라**

하나의 트랜잭션에서는 하나의 애그리거트만 수정한다. 애그리거트 경계는 비즈니스 불변식(invariant)이 반드시 함께 지켜져야 하는 범위와 일치해야 한다.

**규칙 2: 작은 애그리거트를 설계하라**

> "루트 엔티티와 최소한의 속성/값 객체로 제한하라. 올바른 최소치는 일관성을 유지하는 데 필요한 만큼이며, 그 이상은 아니다." -- Vernon

**규칙 3: 다른 애그리거트는 ID로만 참조하라**

직접 객체 참조(object reference) 대신 식별자(identity)로 참조하면 결합도가 낮아지고, 로딩 시간과 메모리 사용이 줄어든다.

**이 규칙은 도메인 객체 레벨에 그치지 않고 영속성/ORM 레벨까지 적용된다 — BC(바운디드 컨텍스트) 경계를 넘는 ORM 관계(`ForeignKey`·`OneToOneField`·`ManyToManyField`)를 두지 않는다.** 타 BC의 애그리거트는 ID 값(`PositiveIntegerField` 등)으로만 저장·참조하고, 무결성은 ① 생성 시점 존재 검증 = ACL/OHS 포트 조회 ② 삭제·변경 생애주기 = 상류 BC의 도메인 이벤트·published 계약으로 보장한다(하류가 상류를 역참조하지 않는다 — 상류 BC는 하류를 모른다). 하류가 상류 모델을 FK로 결합하면 상류의 테이블 형상·삭제 정책이 하류로 누수되고 마이그레이션이 상류에 묶인다(모듈 간 DB 결합). 경계는 셋이다 — **같은 애그리거트 내부** = ORM FK 자유(루트가 일관성 경계), **같은 BC의 다른 애그리거트** = ORM FK 허용(도메인 모델은 위 결합도 근거로 ID 참조 권장), **다른 BC** = ORM FK 금지(ID 값 참조). *왜* — Vernon의 Reference-by-Identity 원문은 도메인 객체 레벨이고, ORM 자동 관계 매핑 배제와 BC 경계 FK 금지는 Fowler(Bounded Context)·모듈러 모놀리스(모듈 간 DB 결합 회피) 합의를 더한 것이다. 플랫폼 횡단 공유(`settings.AUTH_USER_MODEL`·공유 커널 값객체)는 예외다.

**규칙 4: 일관성 경계 밖에서는 결과적 일관성을 사용하라**

> **[의사결정 #4] External 채택**: 서로 다른 애그리거트 간의 일관성은 도메인 이벤트를 통한 결과적 일관성(eventual consistency)으로 달성한다.

> 실무 참고: 동일 데이터베이스 내 단순 케이스에서는 같은 트랜잭션에서 복수 애그리거트를 수정하는 것도 용인할 수 있다. 단, 이는 원칙의 예외이며 시스템이 분산되면 즉시 결과적 일관성으로 전환해야 한다.
>
> ⚠ 이 '복수 애그리거트 수정 용인'은 **런타임 트랜잭션 원자성**에 관한 것이지 **영속성 FK 결합을 허가하지 않는다**(규칙3의 ORM 확장과 직교한다). FK 없이도 같은 atomic 트랜잭션이 성립한다 — 응용 서비스/ACL이 같은 connection에서 두 애그리거트를 원자적으로 쓰면 된다. "한 트랜잭션에 묶인다"를 BC 경계 ORM FK의 근거로 끌어쓰지 마라.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from uuid import uuid4


# --- 값 객체들 ---
@dataclass(frozen=True)
class OrderLineItem:
    product_id: str
    product_name: str
    price: Money
    quantity: int

    @property
    def amounts(self) -> Money:
        return self.price.multiply(self.quantity)


class OrderStatus(Enum):
    PAYMENT_WAITING = "payment_waiting"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

    @property
    def is_shippable(self) -> bool:
        return self in (OrderStatus.PAYMENT_WAITING, OrderStatus.PREPARING)


@dataclass(frozen=True)
class ShippingInfo:
    receiver_name: str
    receiver_phone: str
    address: Address


# --- 안티패턴: 너무 큰 애그리거트 (Vernon 규칙 2 위반) ---
@dataclass
class BigProduct:
    """모든 것을 하나의 애그리거트에 넣은 나쁜 예"""
    id: str
    name: str
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
    """리뷰 애그리거트 -- Product와 ID로만 연결 (규칙 3)"""
    id: str
    product_id: str  # Product를 ID로 참조
    reviewer_id: str
    rating: int
    content: str


# --- 애그리거트 루트: 도메인 이벤트와 결과적 일관성 (규칙 4) ---
@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    customer_id: str
    total_amount: int
    occurred_at: datetime


@dataclass
class Order:
    """주문 애그리거트

    - Order가 애그리거트 루트이다
    - OrderLineItem, ShippingInfo는 애그리거트 내부 구성요소
    - 모든 상태 변경은 Order를 통해서만 수행한다
    - 다른 애그리거트(Member)는 ID로만 참조한다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    orderer_id: str = ""  # Member 애그리거트를 ID로 참조
    order_lines: List[OrderLineItem] = field(default_factory=list)
    shipping_info: ShippingInfo = None
    _status: OrderStatus = field(default=OrderStatus.PAYMENT_WAITING)
    _events: List = field(default_factory=list)

    def __post_init__(self):
        self._verify_at_least_one_order_line()
        self._calculate_total_amounts()

    def _verify_at_least_one_order_line(self) -> None:
        if not self.order_lines:
            raise ValueError("최소 한 종류 이상의 상품을 주문해야 합니다")

    def _calculate_total_amounts(self) -> None:
        total = Money(0)
        for line in self.order_lines:
            total = total.add(line.amounts)
        self._total_amounts = total

    def change_shipping_info(self, new_info: ShippingInfo) -> None:
        if not self._status.is_shippable:
            raise ValueError("배송지를 변경할 수 없는 상태입니다")
        self.shipping_info = new_info

    def place(self) -> None:
        """주문 접수 -- 결과적 일관성을 위해 이벤트를 발행"""
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

    def ship(self) -> None:
        if self._status != OrderStatus.PREPARING:
            raise ValueError("준비 상태에서만 출고할 수 있습니다")
        self._status = OrderStatus.SHIPPED

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events


# 별도 핸들러에서 결과적 일관성으로 처리
class InventoryEventHandler:
    def handle_order_placed(self, event: OrderPlacedEvent) -> None:
        """별도 트랜잭션에서 재고 차감 -- 결과적 일관성"""
        pass

class LoyaltyEventHandler:
    def handle_order_placed(self, event: OrderPlacedEvent) -> None:
        """별도 트랜잭션에서 포인트 적립 -- 결과적 일관성"""
        pass
```

#### 애그리거트를 팩토리로 사용하기 [A]

```python
@dataclass
class Store:
    """상점 애그리거트"""
    id: str
    name: str
    _is_blocked: bool = False

    def create_product(self, product_id: str, name: str, description: str, price: int) -> "Product":
        """팩토리 메서드 - 도메인 로직(신고 차단 여부)을 애그리거트 안에 유지"""
        if self._is_blocked:
            raise PermissionError("차단된 상점은 상품을 등록할 수 없습니다")
        return Product(id=product_id, name=name, description=description, price=price)
```

### 3.4 리포지토리 (Repository)

> 출처: [A][B][C], Cosmic Python

애그리거트 단위로 도메인 객체의 영속성을 처리한다. 도메인 영역에 인터페이스를 정의하고, 인프라 영역에서 구현한다 (DIP).

> "ORM이 도메인 모델을 임포트하게 하라. 도메인 모델이 ORM을 임포트하면 안 된다." -- Cosmic Python

```python
from abc import ABC, abstractmethod
from typing import Optional


# 도메인 영역: 리포지토리 인터페이스 (고수준 모듈)
class OrderRepository(ABC):
    """주문 리포지토리 인터페이스
    - 애그리거트 단위로 저장/조회한다
    - OrderLineItem을 위한 별도 리포지토리는 만들지 않는다
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


# 인프라 영역: 리포지토리 구현 (저수준 모듈)
class DjangoOrderRepository(OrderRepository):
    """Django ORM 기반 리포지토리 구현체"""

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

### 3.5 도메인 서비스 (Domain Service)

> 출처: [A][B][C], Cosmic Python
> **[의사결정 #3] External 채택**: 애그리거트가 도메인 서비스를 모르도록 분리한다.

여러 애그리거트에 걸친 도메인 로직을 구현한다. **상태 없이(stateless) 로직만 구현**한다.

**응용 서비스 vs 도메인 서비스 구분법** [A]:
- 해당 로직이 애그리거트의 상태를 변경하거나 상태 값을 계산하는가? -> 도메인 서비스
- 트랜잭션 처리, 도메인 객체 조회/저장 조율인가? -> 응용 서비스

응용 서비스(또는 핸들러)가 도메인 서비스를 호출하고, 애그리거트는 순수 도메인 로직(엔티티 상태 변경, 이벤트 발행)만 담당하도록 분리한다. 애그리거트는 외부 의존성을 받지 않는다 (Cosmic Python).

```python
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Coupon:
    code: str
    discount_amount: Money


class MemberGrade(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    VIP = "vip"


class DiscountCalculationService:
    """할인 계산 도메인 서비스

    - 상태가 없다 (stateless)
    - 여러 애그리거트(주문, 쿠폰, 회원)의 데이터를 사용하여 계산
    - 한 애그리거트에 넣기 애매한 로직을 명시적으로 표현
    """

    def calculate_discount(
        self,
        order_lines: List[OrderLineItem],
        coupons: List[Coupon],
        member_grade: MemberGrade,
    ) -> Money:
        coupon_discount = Money(0)
        for coupon in coupons:
            coupon_discount = coupon_discount.add(coupon.discount_amount)

        grade_discount = self._calculate_grade_discount(member_grade, order_lines)
        return coupon_discount.add(grade_discount)

    def _calculate_grade_discount(
        self, grade: MemberGrade, order_lines: List[OrderLineItem]
    ) -> Money:
        total = Money(0)
        for line in order_lines:
            total = total.add(line.amounts)

        rate = {
            MemberGrade.BRONZE: 0,
            MemberGrade.SILVER: 0.01,
            MemberGrade.GOLD: 0.03,
            MemberGrade.VIP: 0.05,
        }.get(grade, 0)

        return Money(int(total.amount * rate))


# 좋은 예: 응용 서비스가 도메인 서비스를 호출하고 결과를 애그리거트에 전달
class OrderApplicationService:
    def apply_discount(self, order_id: str, coupons: List[Coupon], grade: MemberGrade):
        order = self._order_repo.find_by_id(order_id)
        discount = self._discount_service.calculate_discount(
            order.order_lines, coupons, grade
        )
        order.apply_discount(discount)  # 애그리거트는 Money 값만 받음 (서비스 모름)
        self._order_repo.save(order)


# 나쁜 예: 애그리거트가 도메인 서비스를 직접 파라미터로 받음
class OrderBad:
    def calculate_payment(
        self,
        discount_service: DiscountCalculationService,  # 외부 의존성!
        coupons: List[Coupon],
        member_grade: MemberGrade,
    ) -> None:
        discount = discount_service.calculate_discount(
            self.order_lines, coupons, member_grade
        )
        self._payment_amounts = Money(
            max(0, self._total_amounts.amount - discount.amount)
        )
```

### 3.6 응용 서비스 (Application Service)

> 출처: [A][C], Cosmic Python

도메인 영역과 표현 영역을 연결하는 매개체(파사드) 역할이다. 비즈니스 로직을 직접 구현하지 않으며, 도메인 객체에 위임한다.

**응용 서비스의 책임:**
- 리포지토리에서 애그리거트를 조회한다
- 애그리거트의 도메인 기능을 실행한다
- 트랜잭션을 관리한다
- 결과를 리턴한다

**응용 서비스가 하면 안 되는 것:**
- 도메인 로직을 직접 구현하면 안 된다
- 표현 영역에 의존하면 안 된다 (HttpRequest 등을 파라미터로 받지 말 것)

```python
@dataclass
class PlaceOrderCommand:
    """응용 서비스 입력 DTO"""
    # ※ 이 메시지-어휘(…Command=입력 DTO)는 CQRS 이론 *교육*이다. 이 플러그인 *생성 코드*는 입력을 …Request로, 쓰기 *실행*을 …Command 인터랙터로 명명한다(houserules 권위). 두 어휘를 섞지 말 것.
    orderer_id: str
    items: List[dict]
    shipping_address: dict
    coupon_codes: List[str]


class OrderApplicationService:
    """주문 응용 서비스

    - 비즈니스 로직이 없다 (도메인에 위임)
    - 트랜잭션 관리
    - 도메인 객체 간의 흐름을 제어
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        member_repository: "MemberRepository",
        product_repository: "ProductRepository",
        discount_service: DiscountCalculationService,
    ):
        self._order_repo = order_repository
        self._member_repo = member_repository
        self._product_repo = product_repository
        self._discount_service = discount_service

    def place_order(self, cmd: PlaceOrderCommand) -> str:
        """주문 접수 유스케이스"""
        # 1. 리포지토리에서 필요한 애그리거트를 조회한다
        member = self._member_repo.find_by_id(cmd.orderer_id)
        if member is None:
            raise ValueError("회원을 찾을 수 없습니다")

        # 2. 도메인 객체를 조합하여 새 애그리거트를 생성한다
        order_lines = self._create_order_lines(cmd.items)
        shipping_info = ShippingInfo(
            receiver_name=cmd.shipping_address["name"],
            receiver_phone=cmd.shipping_address["phone"],
            address=Address(
                city=cmd.shipping_address["city"],
                street=cmd.shipping_address["street"],
                zipcode=cmd.shipping_address["zipcode"],
            ),
        )

        order = Order(
            orderer_id=member.id,
            order_lines=order_lines,
            shipping_info=shipping_info,
        )

        # 3. 리포지토리에 저장한다
        self._order_repo.save(order)
        return order.id

    def cancel_order(self, order_id: str) -> None:
        """주문 취소 - 단순한 흐름 제어만 담당"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.cancel()  # 도메인 로직은 Order 애그리거트에 위임

    def _create_order_lines(self, items: List[dict]) -> List[OrderLineItem]:
        result = []
        for item in items:
            product = self._product_repo.find_by_id(item["product_id"])
            result.append(
                OrderLineItem(
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    quantity=item["quantity"],
                )
            )
        return result
```

### 3.7 도메인 이벤트 (Domain Event)

> 출처: [B][C], Jimmy Bogard, Cosmic Python
> **[의사결정 #7] External 채택**: UoW 커밋 전후 디스패치 타이밍을 명시한다.

비즈니스 도메인에서 발생한 중요한 사건을 나타낸다. 애그리거트 커맨드 실행의 결과로 발행된다.

**이벤트 수집 -> 디스패치 패턴:**
1. 애그리거트 안에 `_domain_events` 리스트를 두고 이벤트를 수집한다
2. Unit of Work가 커밋 **직전**(동일 트랜잭션 내 부수 효과) 또는 **직후**(외부 통합)에 디스패치한다
3. 디스패치 타이밍이 명시되지 않으면 이벤트 유실이나 트랜잭션 불일치가 발생한다

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Type


@dataclass(frozen=True)
class DomainEvent:
    """도메인 이벤트 기본 클래스"""
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


# === 이벤트 디스패처와 Unit of Work 연동 ===

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


class UnitOfWork:
    """Unit of Work -- 트랜잭션 경계에서 이벤트를 디스패치"""

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    def commit(self) -> None:
        ...  # DB 커밋 로직

    def _dispatch_events(self, aggregate: AggregateRoot) -> None:
        """커밋 직전에 수집된 이벤트를 디스패치"""
        for event in aggregate.domain_events:
            self._event_bus.publish(event)
        aggregate.clear_events()
```

#### Outbox 패턴

이벤트의 신뢰성 있는 발행을 보장하기 위해, 이벤트를 애그리거트와 같은 트랜잭션에서 Outbox 테이블에 저장하고, 별도 프로세스가 Outbox에서 이벤트를 읽어 메시지 브로커에 발행한다.

발행 메시지의 스키마, 디스패처 구현, 전달 보장(at-least-once)·재시도·dead-letter는 **전달 메커니즘**이므로 이 문서가 다루지 않는다(아래 handoff). 이 문서는 "이벤트를 같은 트랜잭션에 적재한다"는 결정과 채택 여부만 소유한다.

**Outbox를 선택하는 조건:**
- DB 커밋 이후 외부 메시지 전달이 유실되면 안 된다.
- at-least-once 전달과 consumer 멱등성을 설계할 수 있다.
- retry, dead-letter, dispatch ownership이 필요하다.

**회피하는 조건:**
- 외부 부수효과가 없다.
- 단순 in-process 후속 작업이며 `transaction.on_commit()`으로 충분하다.
- 유실 가능성을 제품이 수용하거나 별도 운영 부담이 과하다.

**Outbox 채택 시 명시할 항목:** 애그리거트와 outbox 메시지를 쓰는 트랜잭션 owner, dispatcher owner, 전달 보장(delivery guarantee), consumer 멱등성 기준, retry/dead-letter 정책의 소유 영역, 발행 언어(published language) 필드. 전달 메커니즘(at-least-once, consumer 멱등성, retry/dead-letter, 디스패처 운영)은 `architecture-db`(§9.7)가 소유하고, Django 트랜잭셔널 outbox 구체 구현은 `implementation-django`(§16.5)가 담당한다. 신뢰성 검증 항목은 자동 테스트 세트가 아니라 `discipline-tdd` 입장 심사에 제출할 위험·failure 후보이며, `add` 결정 뒤의 작성 mechanics만 `implementation-test`가 담당한다.

#### 발행 이벤트 타입 — 1종째부터 enum (birth-enum)

**우리 BC가 발행하는 이벤트 봉투의 타입 판별자(discriminator — `event_type` 류)는 이벤트 종류가 1종일 때부터 domain_layer의 `StrEnum` 하나로 선언한다.** 트리거는 위치다: 발행 봉투의 판별자라는 구조 자체가 종류 확장의 증거이고, 이 값은 outbox 저장(위 Outbox·`implementation-django` §16.5)과 wire 노출로 §3.2 계층 소유의 승격 앵커(저장·계약 노출)에 기본 도달한다 — "분기가 생기면 승격"의 판정을 확장 시점의 코더에게 미루지 않고 탄생 시점에 확정한다(판단형 규칙은 준수율이 낮고, 승격 누락은 신호 없이 표류하며 이벤트가 늘수록 비쌈). 이름 기반 트리거는 여전히 금지다 — 이름이 type/kind라는 이유의 승격 금지, pass-through 상류 type 필드·데이터소스 BC 면제는 `discipline-cleancode` §2.14 그대로.

- **배치·소유**: 발행 BC domain_layer의 이벤트 슬롯 `domain_layer/<aggregate>/event/event_type.py`(`discipline-houserules` §2). BC 내부 소유 — 다른 BC가 직접 import하지 않는다(§2.5 published language: 소비 BC는 wire 값을 각자 수용). 경계-로컬(presentation 봉투 모듈) 배치를 쓰지 않는 이유: outbox 리포지토리(infra)가 enum을 소비하므로 infra→presentation 역방향 import를 강제하게 된다 — domain 배치면 infra/presentation→domain 허용 방향으로 전원 접근 가능.
- **파생 표기**: 봉투 계약 Schema의 태그 필드는 `Literal[EventType.X] = EventType.X`로 파생한다 — 평(non-Literal) Enum 필드는 discriminator로 쓸 수 없으므로(Pydantic) Literal 파생이 유일 경로다(wire 표기·봉투 union은 `implementation-django-ninja` §3.1). union-enum 동기 검증은 `discipline-tdd` 입장 심사 후보이며, 공개/wire 드리프트가 독자 production failure이고 기존 권위 테스트가 보호하지 않을 때만 `add`한다. 승인 뒤 mechanics는 `implementation-test` §15.5를 따른다. ORM `default=`·마이그레이션 경계는 `.value` 평탄화(`implementation-django` §2.5).
- **수명 — append-only**: 멤버는 추가만 한다. **값 변경·삭제 금지** — 발행된 메시지·outbox 행·소비자 계약에 옛 값이 살아 있다(protobuf enum 진화 규칙·마이그레이션 historical value와 동형). 이벤트 폐기는 멤버 삭제가 아니라 발행 중단+주석 표기. 스키마 비호환 변경은 기존 값 수정이 아니라 새 버전 태그(필요시 새 멤버) 추가+upcasting이다(Greg Young — "old version에서 convertible하지 않으면 새 버전이 아니라 새 이벤트다"; CloudEvents 동방향).
- **제외(짝 조항)**: `payload_schema_version` 등 스키마 버전 태그는 판별자와 형태가 같지만(단일 멤버 Literal+같은 기본값) **리터럴 동결 유지** — 발행 순간 동결되는 계약 표식이라 enum화는 "수정 가능한 중앙 등록부"라는 잘못된 어포던스를 만든다. 상류 이벤트를 중계만 하는 **소비 측** 스키마의 태그도 비대상(published language 수용). **OHS published contract(`open_host_service/*/contract/`)로 발행 봉투를 노출할 때의 discriminator 자리도 비대상** — contract 무의존(`discipline-houserules` §2 OHS 내부 구조)이 우선해 wire `Literal["…"]`을 유지한다. 드리프트 검증 후보도 위 입장 심사에서 독자 failure와 기존 보호를 판정한다(`discipline-cleancode` §2.14 재예외).
- **소비자 측 짝 규칙**: 소비 BC는 미지 event_type 처리 방침(UNKNOWN 폴백 또는 명시적 거부)을 함께 정한다 — 발행자의 멤버 추가는 소비자의 완전(match) 분기를 깨므로, 무방침 정규화는 신규 이벤트 도착 시 수집 경로를 죽인다(`discipline-cleancode` §2.14 열린 집합 조항 준용).

### 3.8 Specification 패턴

> 출처: Eric Evans & Martin Fowler, "Specifications" (1997)

비즈니스 규칙을 독립적인 객체로 캡슐화하고, 논리 연산(AND, OR, NOT)으로 조합할 수 있게 하는 패턴이다.

**세 가지 용도:**

| 용도 | 설명 | 예시 |
|------|------|------|
| 검증 (Validation) | 객체가 비즈니스 규칙을 만족하는지 확인 | `eligible_for_premium.is_satisfied_by(customer)` |
| 선택 (Selection/Query) | 컬렉션에서 조건에 맞는 객체를 필터링 | `[c for c in customers if spec.is_satisfied_by(c)]` |
| 생성 (Construction) | 규칙을 만족하는 새 객체를 생성하도록 빌더에 전달 | 팩토리가 Specification을 참조하여 기본값 결정 |

```python
from __future__ import annotations
from abc import ABC, abstractmethod
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


# 실무 적용 예시
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Customer:
    id: str
    name: str
    total_purchases: int
    registered_at: datetime
    is_verified: bool


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
```

---

## 4. 유연한 설계 (Supple Design)

> 출처: Evans 파란책 Chapter 10

Evans가 제시하는 모델 코드의 품질 패턴 6가지다.

### 4.1 의도를 드러내는 인터페이스 (Intention-Revealing Interfaces)

클래스와 메서드의 이름이 **무엇을 하는지**(what)를 드러내야 하며, **어떻게 하는지**(how)는 숨겨야 한다.

```python
@dataclass(frozen=True)
class Paint:
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

### 4.2 부작용 없는 함수 (Side-Effect-Free Functions)

가능한 한 많은 도메인 로직을 부작용 없는 함수로 배치하라. 값 객체의 메서드가 대표적이다.

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
```

### 4.3 단언 (Assertions)

연산의 사후 조건(post-condition)과 클래스의 불변식(invariant)을 명시적으로 선언한다.

```python
@dataclass
class BankAccount:
    account_id: str
    _balance: int = 0

    def deposit(self, amount: int) -> None:
        old_balance = self._balance
        self._balance += amount
        assert self._balance == old_balance + amount, "입금 후 잔액 불일치"
        assert self._balance >= 0, "잔액은 음수가 될 수 없다"
```

### 4.4 개념적 윤곽 (Conceptual Contours)

도메인의 자연스러운 경계선을 따라 설계를 분해한다. **"함께 변하는 것은 함께 두고, 따로 변하는 것은 분리하라."**

### 4.5 독립형 클래스 (Standalone Classes)

클래스 간 결합을 최소화하여 각 클래스를 독립적으로 이해할 수 있게 하라. 모든 불필요한 의존성을 제거하면 개별 개념의 복잡성이 크게 줄어든다.

### 4.6 연산의 닫힘 (Closure of Operations)

반환 타입이 인자의 타입과 동일한 연산을 정의하면, 해당 타입의 인스턴스 집합 안에서 연산이 "닫혀" 있게 된다.

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

---

## 5. 아키텍처

> **[의사결정 #5] Internal 채택**: 계층+DIP 기반 동기적 흐름을 기본으로 한다 (메시지 주도는 별도 고급 주제로 다룸).

### 5.1 계층 아키텍처

> 출처: [A][C]

```
표현(Presentation) -> 응용(Application) -> 도메인(Domain) -> 인프라(Infrastructure)
```

**핵심 규칙:**
- 상위 계층에서 하위 계층으로만 의존한다 (하위 -> 상위 절대 불가)
- 도메인 영역, 응용 영역, 표현 영역은 인프라의 구현 기술을 직접 사용하지 않는다
- DIP를 적용하여 도메인 영역에 정의한 인터페이스를 인프라에서 구현한다

### 5.2 DIP (의존성 역전 원칙)

> 출처: [A][C]

고수준 모듈이 저수준 모듈에 의존하지 않도록 추상화에 의존한다. 인터페이스는 고수준(도메인) 영역에 위치해야 한다.

```python
from abc import ABC, abstractmethod


# 도메인 영역 (고수준): 인터페이스 정의
class RuleDiscounter(ABC):
    """할인 규칙 인터페이스 - 도메인(고수준)에 위치"""

    @abstractmethod
    def apply_rules(
        self, customer_id: str, order_lines: List[OrderLineItem]
    ) -> Money:
        ...


# 인프라 영역 (저수준): 구현체
class DroolsRuleDiscounter(RuleDiscounter):
    """Drools 엔진 기반 구현 - 인프라(저수준)에 위치"""

    def apply_rules(
        self, customer_id: str, order_lines: List[OrderLineItem]
    ) -> Money:
        ...


# 응용 서비스: 추상화에만 의존
class CalculateDiscountService:
    """DIP 적용 예시
    - RuleDiscounter 인터페이스에만 의존
    - Drools든 Simple이든 상관없이 동작
    - 테스트 시 Mock 객체 주입 가능
    """

    def __init__(self, rule_discounter: RuleDiscounter):
        self._rule_discounter = rule_discounter

    def calculate_discount(
        self, order_lines: List[OrderLineItem], customer_id: str
    ) -> Money:
        return self._rule_discounter.apply_rules(customer_id, order_lines)
```

### 5.3 핵사고날 아키텍처 (포트와 어댑터)

> 출처: [C]

[C]는 헥사고날 아키텍처를 DDD 구현의 주요 아키텍처 스타일로 권장한다. 의존성은 항상 정책(도메인/응용) 쪽으로 향하고, 포트는 응용/도메인이 필요로 하는 역할이며 어댑터는 프레임워크나 외부 세부사항을 번역한다.

**핵사고날을 선택하는 조건:**
- 외부 서비스, 브로커, 결제/재고/권한 provider, 레거시 시스템이 도메인 모델을 오염시킬 위험이 있다.
- 영속성 형태(persistence shape)와 도메인 언어가 다르다.
- 프레임워크 없이 유스케이스를 테스트하는 가치가 크다.
- 교체 가능성이 실제 요구이거나 장애 격리, 계약 안정성이 중요하다.

**회피하는 조건:**
- Django 관례가 흐름을 더 명확하게 만든다.
- 포트가 기술명만 감춘 얇은 wrapper다.
- 구현이 하나뿐이고 바뀔 가능성도 낮으며 테스트 seam도 필요 없다.

**포트 작성 기준:**
- 포트 이름은 기술이 아니라 역할을 표현한다(예: `PaymentGateway`, `InventoryReservationPort`).
- 포트 메서드는 좁고 유스케이스 언어를 따른다. 입출력은 도메인/응용 DTO, 값 객체, 식별자를 사용한다.
- Python에서는 구조적 협력이면 `Protocol`을 우선 고려하고, 명시적 상속이나 런타임 등록이 필요할 때 ABC를 고려한다. 모든 클래스에 인터페이스를 만들지 않는다.

**어댑터 배치 기준:**
- Django view, Ninja router, DRF view/serializer, template view, form, management command, Celery task, message handler는 **인터페이스 어댑터**다.
- ORM 리포지토리, 외부 SDK 클라이언트, 브로커 publisher, cache/filesystem 구현은 **인프라 어댑터**다.
- 어댑터는 입력 검증, 인증 연결, DTO 변환, 유스케이스 호출, 응답 매핑을 담당할 수 있지만 핵심 정책을 소유하지 않는다.

### 5.4 CQRS (커맨드-쿼리 책임 분리)

> 출처: [C], Greg Young, Martin Fowler
> **[의사결정 #2] External 채택**: CQRS는 보조 패턴으로 선택적 적용한다.

> "CQRS는 최상위 아키텍처가 아니다! 보조 패턴으로 취급하고, 선택적으로 일부 바운디드 컨텍스트에만 적용하라." -- Greg Young (CQRS 창시자)

커맨드(상태 변경)와 쿼리(데이터 조회)의 모델을 분리한다. 핵심 원칙: "질문하는 행동이 대답을 바꿔서는 안 된다." 시스템 전체가 아닌 필요한 컨텍스트에만 선택 적용하는 것이 안전하다.

**CQRS를 선택하는 조건:**
- 쓰기 불변식(write invariant)과 읽기 projection/집계가 서로 다른 모델을 요구한다.
- 읽기 측 성능, 비정규화 projection, reporting 모델이 커맨드 모델을 왜곡한다.
- 커맨드 처리와 쿼리 최적화의 변경 이유가 분리되어 있다.

**회피하는 조건:**
- selector 또는 QuerySet 최적화로 충분하다.
- 읽기/쓰기 분리가 단순 CRUD를 더 어렵게만 만든다.
- eventual consistency를 감당할 제품/운영 기준이 없다.

### 5.5 대규모 구조 (Large-Scale Structure)

> 출처: Evans 파란책 Chapter 16

시스템 전체에 적용되는 고수준 조직 패턴이다.

| 패턴 | 설명 |
|------|------|
| 진화하는 질서 (Evolving Order) | 대규모 구조를 처음부터 완벽히 설계하지 말고, 시스템과 함께 진화시켜라 |
| 시스템 은유 (System Metaphor) | 시스템 전체를 관통하는 비유를 찾아 명시화하라 |
| 책임 계층 (Responsibility Layers) | 도메인 모델을 의미 있는 책임 계층으로 구조화하라 |
| 지식 수준 (Knowledge Level) | 운영 수준의 핵심 동작을 구성할 수 있는 메타 수준을 분리하라 |
| 플러그형 컴포넌트 프레임워크 | 핵심 추상화와 구현을 플러그인 구조로 분리하라 |

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# === 지식 수준 (Knowledge Level) 패턴 ===

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
```

---

## 6. 구현 패턴

### 6.1 패키지 구조

> **[의사결정 #8] External 채택**: 4계층 명확 분리를 기본으로 한다.

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
│   │   │   ├── orm.py               # ORM 매핑 (Django ORM 등)
│   │   │   ├── repository.py        # 리포지토리 구현체
│   │   │   ├── unit_of_work.py      # UoW 구현체
│   │   │   └── event_publisher.py   # 이벤트 발행 구현
│   │   │
│   │   └── interface/               # 표현 계층 (입력 어댑터)
│   │       ├── __init__.py
│   │       ├── api.py               # 입력 어댑터 (REST/Web)
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
├── tests/                            # 승인된 테스트가 실제 있을 때만 구성
│   ├── unit/                        # 도메인 로직 단위 테스트
│   ├── integration/                 # 인프라 통합 테스트
│   └── e2e/                         # 엔드투엔드 테스트
│
└── pyproject.toml
```

`tests/` 하위 트리는 `discipline-tdd` 입장 심사에서 실제 테스트가 승인된 뒤 적용하는 레이아웃 예시다. 구조 규칙만으로 빈 test 패키지·새 파일·case를 만들지 않는다.

**핵심 의존성 규칙:**
- `domain/` -- 어디에도 의존하지 않는다. 순수 Python만 사용
- `application/` -- `domain/`에만 의존한다
- `infrastructure/` -- `domain/`과 `application/`에 의존한다 (인터페이스 구현)
- `interface/` -- `application/`에 의존한다 (유스케이스 호출)

> Django 등 프레임워크 제약 시 [A]의 간소화된 구조(`views/`, `services/`, `domain/`, `infrastructure/`)를 차선으로 허용한다.

> dddjango가 *생성하는 코드*의 구체 표준 파일트리는 `discipline-houserules` 스킬이 소유한다(표준 트리는 그 `reference/final.md`) — §6.1의 4계층을 `application/<bounded_context>/{domain_layer, application_layer, driven_layer, driving_layer}/`로 구체화한 표준이며, 생성 코드 배치 권위는 그 문서가 갖는다. 여기 §6.1은 그 표준이 파생된 이론적 배경이다.

### 6.2 Data Mapper 패턴

> 출처: Cosmic Python

ORM은 도메인 모델을 임포트해야 하며, 도메인 모델이 ORM에 의존해서는 안 된다. Data Mapper 스타일의 구체 구현은 아래 §6.3 Repository + Unit of Work 코드를 따르고, Django ORM 환경에서의 적용(모델 분리 비용, 서비스/셀렉터 경계)은 `implementation-django`(§16)가 소유한다.

### 6.3 Repository + Unit of Work 패턴

> 출처: Cosmic Python

Repository는 애그리거트 영속성을 컬렉션처럼 추상화하고, Unit of Work는 트랜잭션 경계를 한 단위로 묶는다. 도메인/응용 계층은 **추상 인터페이스**에만 의존하고, 구체 구현(ORM)은 인프라 계층에 둔다.

```python
from abc import ABC, abstractmethod
from typing import Optional


# 도메인 계층: 추상 리포지토리 (영속성 기술에 의존하지 않음)
class AbstractBatchRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch) -> None: ...

    @abstractmethod
    def get(self, reference: str) -> Optional[Batch]: ...


# 응용 계층: 트랜잭션 경계를 묶는 Unit of Work
class AbstractUnitOfWork(ABC):
    batches: AbstractBatchRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...


# 응용 서비스는 추상 UoW에만 의존한다 (구체 ORM을 모른다)
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

구체 구현은 영속성 기술이 결정한다. 이 코퍼스의 대상인 Django에서는 Repository를 `implementation-django` §16.3(QuerySet/Manager 기반)으로, Unit of Work를 `transaction.atomic()`(§16.4)으로 실현한다. ORM별 매핑 비용과 서비스/셀렉터 경계도 `implementation-django`(§16)가 소유한다.

### 6.4 Event Sourcing

> 출처: Greg Young, Martin Fowler

> "Event Sourcing의 정의: 언제든 애플리케이션 상태를 날려버리고 이벤트 로그에서 자신 있게 재구축할 수 있다." -- Martin Fowler

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
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


class EventSourcedAggregate(ABC):
    """이벤트 소싱 기반 애그리거트 루트의 기반 클래스"""

    def __init__(self):
        self._uncommitted_events: List[DomainEvent] = []
        self._version: int = 0

    def _apply(self, event: DomainEvent) -> None:
        self._route_event(event)
        self._uncommitted_events.append(event)
        self._version += 1

    @abstractmethod
    def _route_event(self, event: DomainEvent) -> None:
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
            self.account_id = event.account_id
            self.owner_name = event.owner_name
            self.balance = event.initial_balance
        elif isinstance(event, MoneyDeposited):
            self.balance += event.amount
        elif isinstance(event, MoneyWithdrawn):
            self.balance -= event.amount
```

### 6.5 Saga 패턴 (분산 트랜잭션)

> 출처: Hector Garcia-Molina & Kenneth Salem, "Sagas" (1987)

여러 애그리거트/서비스에 걸친 비즈니스 트랜잭션을 관리하는 패턴이다.

| 방식 | 설명 | 장점 | 단점 |
|------|------|------|------|
| Choreography | 각 서비스가 이벤트를 발행/구독하여 자율 실행 | 단순, 느슨한 결합 | 순환 의존 위험, 흐름 파악 어려움 |
| Orchestration | 중앙 오케스트레이터가 각 서비스에 지시 | 흐름이 명확, 서비스 추가 용이 | 오케스트레이터에 로직 집중 |

핵심은 **보상 트랜잭션(Compensating Transaction)**이다. 중간 단계가 실패하면, 이미 완료된 단계를 되돌리는 보상 행동을 실행한다. 보상 트랜잭션은 반드시 멱등성(idempotent)이 있어야 한다.

```python
from dataclasses import dataclass
from enum import Enum
from typing import List
import logging

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    name: str
    action: callable
    compensation: callable
    status: StepStatus = StepStatus.PENDING


class SagaOrchestrator:
    """Saga 오케스트레이터: 단계별 실행과 보상을 관리"""

    def __init__(self, steps: List[SagaStep]):
        self._steps = steps
        self._completed_steps: List[SagaStep] = []

    def execute(self) -> bool:
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
```

### 6.6 단순한 비즈니스 로직 패턴

> 출처: [B]

DDD의 전술 패턴이 모든 상황에 적합하지 않다. 단순한 비즈니스 로직을 위한 패턴도 알아야 한다.

**트랜잭션 스크립트** -- 절차지향 스크립트로 비즈니스 로직을 구현한다. 지원 하위 도메인에 적합하다.

```python
class FileConversionScript:
    """트랜잭션 스크립트 패턴 [B]
    - 단순한 절차지향 스크립트
    - 지원 하위 도메인, ETL 등에 적합
    """

    def convert_json_to_xml(self, job_id: str) -> None:
        db.start_transaction()
        try:
            job = db.load_next_job(job_id)
            json_data = load_file(job.source)
            xml_data = convert_json_to_xml(json_data)
            write_file(job.destination, xml_data)
            db.mark_job_as_completed(job)
            db.commit()
        except Exception:
            db.rollback()
            raise
```

### 6.7 마이크로서비스와 DDD

> 출처: Microsoft Learn -- Tactical DDD for Microservices

바운디드 컨텍스트는 마이크로서비스의 자연스러운 경계가 된다. 각 마이크로서비스는 하나의 바운디드 컨텍스트에 대응하며, 자체 데이터베이스를 소유하고, 다른 서비스와는 API 또는 이벤트로 통신한다.

| 컨텍스트 매핑 패턴 | 마이크로서비스 통합 방식 |
|----------------|-------------------|
| OHS + Published Language | REST API, gRPC, GraphQL |
| ACL | API Gateway, 어댑터 서비스 |
| Event-Driven | 메시지 브로커 (Kafka, RabbitMQ) |
| Shared Kernel | 공유 라이브러리 (최소화 필수) |
| Separate Ways | 기능 중복 허용 |

**통합 이벤트와 도메인 이벤트의 구분:**

```python
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class OrderEventType(StrEnum):
    """발행 BC(주문 컨텍스트)가 소유하는 발행 이벤트 종류 — 1종째부터 enum·append-only (§3.7 birth-enum)"""
    ORDER_COMPLETED = "order.completed"


@dataclass(frozen=True)
class IntegrationEvent:
    """바운디드 컨텍스트 간 통신을 위한 통합 이벤트
    도메인 이벤트(내부용)와 달리, Published Language로 직렬화된다."""
    event_id: str
    event_type: str  # wire 형은 str — 발행 시점 값의 단일 출처는 발행 BC의 OrderEventType, 소비 BC는 wire 값으로 수용(§2.5)
    occurred_at: datetime
    source_context: str
    payload: dict


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

### 6.8 패턴 선택 절차와 Risky Write 라우팅

> 전술/구현 패턴은 도메인 전략을 대신하지 않는다. 도메인 모델이 어느 정도 확인된 뒤, 다음 순서로 가장 가벼운 패턴을 고른다.

1. 바운디드 컨텍스트, 애그리거트, 불변식, 유스케이스, 외부 통합 경계를 확인한다.
2. 실제 압력을 분류한다: 프레임워크 누수, 영속성 매핑, 트랜잭션 경계, 읽기/쓰기 모델 분기, 외부 부수효과 신뢰성, 레거시/업스트림 언어 충돌, 테스트 seam, 교체 필요.
3. 현재 압력을 해결하는 가장 가벼운 패턴을 선택한다.
4. 선택하지 않은 무거운 패턴과 그 이유를 함께 기록한다.

단순 CRUD, 작은 필드 변경, 지원 하위 도메인의 직선적 흐름에는 리포지토리, 커스텀 Unit of Work, CQRS, 이벤트 소싱, saga, outbox, ACL을 기본으로 도입하지 않는다.

**Risky Write(결제, 재고, 예약, 환불, 권한, ledger 등) 라우팅:** 패턴 선택은 여기서 정하고, 세부 구현/검증은 소유 영역으로 넘긴다.

| 항목 | 소유 |
|---|---|
| 패턴 결정 (Django-native 트랜잭션 / 서비스 레이어 / 포트·어댑터 / outbox / saga / ACL / 추가 패턴 없음) | 이 문서(§5~§6) |
| 트랜잭션 owner, 부수효과 타이밍 | `implementation-django`(§16) |
| 락, 격리 수준, 인덱스, rollout | `architecture-db` |
| 멱등성 저장, `Idempotency-Key`, status code | `architecture-api` |
| 테스트 후보 입장 결정 | `discipline-tdd` |
| `add`된 통합/동시성/멱등성 테스트 mechanics | `implementation-test` |

---

## 7. 복잡성 관리 원칙

> 출처: [B]

DDD의 전술 패턴은 궁극적으로 **시스템의 자유도를 줄여 복잡성을 낮추는 수단**이다.

핵심 통찰:
- 복잡한 것을 불변성으로 감싸서 복잡성을 낮춘다 -- 이것이 애그리거트와 값 객체 패턴이 하는 것이다
- 값 객체의 상태 관련 모든 비즈니스 로직은 자신의 경계 안에 있다
- 비즈니스 로직은 비즈니스 불변성을 감싸고 보호하여 자유도를 줄인다

```python
# 자유도 3: 세 값을 독립적으로 변경 가능 -> 예측 어려움
class ClassA:
    def __init__(self):
        self.a = 0  # 자유
        self.b = 0  # 자유
        self.c = 0  # 자유


# 자유도 1: a만 알면 b, c가 결정됨 -> 예측 쉬움
class ClassB:
    def __init__(self):
        self._a = 0

    @property
    def a(self) -> int:
        return self._a

    @a.setter
    def a(self, value: int):
        self._a = value
        self._b = value // 2  # 불변성: a에 의해 결정
        self._c = value // 3  # 불변성: a에 의해 결정
```

---

## 8. 의사결정 요약

| # | 주제 | 채택 | 근거 |
|---|------|------|------|
| 1 | 엔티티의 독립적 사용 | External | 엔티티는 애그리거트의 일부로만 사용 (Millett, Evans) |
| 2 | CQRS 적용 범위 | External | 보조 패턴으로 선택적 적용 (Greg Young 본인의 입장) |
| 3 | 도메인 서비스 전달 방식 | External | 애그리거트가 도메인 서비스를 모르도록 분리 (Cosmic Python) |
| 4 | 복수 애그리거트 수정 | External | 결과적 일관성 원칙 (Vernon 규칙 4) |
| 5 | 아키텍처 스타일 | Internal | 계층+DIP 기반 동기적 흐름 (메시지 주도는 별도 고급 주제) |
| 6 | 전략 vs 전술 우선순위 | External | 전략 설계 우선 (Vernon DDD Distilled) |
| 7 | 도메인 이벤트 발행 타이밍 | External | UoW 커밋 전후 디스패치 타이밍 명시 (Bogard, Cosmic Python) |
| 8 | 패키지 구조 | External | 4계층 명확 분리 (Cosmic Python, [C]) |

---

## 9. 핵심 요약

| 구분 | 패턴 | 핵심 규칙 |
|------|------|----------|
| 전략 | 바운디드 컨텍스트 | 유비쿼터스 언어가 적용되는 명시적 경계. 하위 도메인은 발견, 바운디드 컨텍스트는 설계한다 |
| 전략 | 유비쿼터스 언어 | 모든 이해관계자가 동일한 비즈니스 용어 사용. 바운디드 컨텍스트 내에서만 유효 |
| 전략 | 컨텍스트 맵 | 바운디드 컨텍스트 간의 관계(파트너십, ACL, OHS 등)를 시각화 |
| 전략 | 증류 | 핵심 도메인을 식별하고 일반/지원 하위 도메인으로부터 분리 |
| 전술 | 값 객체 | 불변, 식별자 없음, 속성 조합으로 동등성 판단 |
| 전술 | 엔티티 | 고유 식별자 보유. 애그리거트의 일부로만 사용 |
| 전술 | 애그리거트 | 일관성 경계이자 트랜잭션 경계. 루트를 통해서만 접근. ID로 타 애그리거트 참조 |
| 전술 | 리포지토리 | 애그리거트 단위로 영속성 처리. 도메인에 인터페이스, 인프라에 구현 |
| 전술 | 도메인 서비스 | 여러 애그리거트에 걸친 무상태 도메인 로직. 애그리거트는 서비스를 모른다 |
| 전술 | 응용 서비스 | 도메인과 표현의 매개체. 비즈니스 로직 없이 흐름 제어와 트랜잭션 관리 |
| 전술 | 도메인 이벤트 | 비즈니스 도메인에서 발생한 사건. UoW 커밋 전후에 디스패치 |
| 아키텍처 | 계층+DIP | 4계층 구조에 의존성 역전 적용. 도메인이 인프라를 모른다 |
| 아키텍처 | 핵사고날 | 포트와 어댑터로 내부/외부 분리 |
| 아키텍처 | CQRS | 보조 패턴으로 선택적 적용. 읽기/쓰기 모델 분리 |

---

## 출처 종합

### 서적
- Eric Evans, "Domain-Driven Design: Tackling Complexity in the Heart of Software" (Addison-Wesley, 2003)
- Eric Evans, [DDD Reference 2015](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) (무료 PDF)
- Vaughn Vernon, "Domain-Driven Design Distilled" (Addison-Wesley, 2016)
- Scott Millett & Nick Tune, "Patterns, Principles, and Practices of Domain-Driven Design" (Wrox, 2015)
- Harry Percival & Bob Gregory, "Architecture Patterns with Python" (O'Reilly, 2020) -- [cosmicpython.com](https://www.cosmicpython.com/)
- Alberto Brandolini, "Introducing EventStorming" (Leanpub) -- [eventstorming.com](https://www.eventstorming.com/)
- Matthew Skelton & Manuel Pais, "Team Topologies" (2019)
- [A] 도메인 주도 개발 시작하기
- [B] 도메인 주도 설계 첫걸음
- [C] 도메인 주도 설계 구현(빨간책)

### 논문/시리즈
- Vaughn Vernon, ["Effective Aggregate Design" Part I-III](https://www.dddcommunity.org/library/vernon_2011/) (2011)
- Hector Garcia-Molina & Kenneth Salem, "Sagas" (1987)
- Eric Evans & Martin Fowler, "Specifications" (1997)
- Jimmy Bogard, "A better domain events pattern" (2014)

### 웹 자료
- Martin Fowler, [CQRS](https://martinfowler.com/bliki/CQRS.html), [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html), [What do you mean by "Event-Driven"?](https://martinfowler.com/articles/201701-event-driven.html)
- Greg Young, "CQRS Documents" (2010)
- [Microsoft Learn -- CQRS Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Microsoft Learn -- Event Sourcing Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
- [Microsoft Learn -- Saga Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)
- [Microsoft Learn -- Tactical DDD for Microservices](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-ddd)
- [Context Mapper](https://contextmapper.org/docs/)
- [DDD Crew -- Context Mapping](https://github.com/ddd-crew/context-mapping)
