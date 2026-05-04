# 지식 탐구와 유비쿼터스 언어

## 2.1 지식 탐구 (Knowledge Crunching)

> 출처: Eric Evans, "DDD" Part I

Evans는 유비쿼터스 언어를 만드는 **과정** 자체를 핵심으로 강조한다. 지식 탐구(Knowledge Crunching)란 도메인 전문가로부터 쏟아지는 정보의 홍수 속에서 관련 있는 것만 걸러내고, 하나의 조직 아이디어를 시도한 뒤 또 다른 아이디어로 교체하며, 복잡한 데이터를 단순하게 설명하는 관점을 찾아가는 반복 과정이다.

**핵심 원칙:**
- 모델은 한 번에 완성되지 않는다. 반복적인 정제(iterative refinement)를 통해 깊은 통찰(deeper insight)에 도달한다.
- 도메인 전문가와 개발자가 **함께** 모델을 만들어야 한다. 개발자가 단독으로 모델을 만들고 전문가에게 검증받는 방식은 지식 탐구가 아니다.
- "코드를 리팩터링하는 것이 아니라, 코드 아래에 있는 **모델을 리팩터링**한다"

```python
# 지식 탐구 전: 개발자가 기술적으로 해석한 모델 (나쁜 예)
class Shipment:
    def __init__(self, cargo_id: str, origin: str, destination: str):
        self.cargo_id = cargo_id
        self.origin = origin
        self.destination = destination
        self.status = "pending"

    def update_status(self, new_status: str) -> None:
        self.status = new_status  # 비즈니스 규칙이 없는 단순 상태 변경


# 지식 탐구 후: 도메인 전문가와 반복 대화를 통해 발견한 모델 (좋은 예)
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

## 2.3 유비쿼터스 언어 (Ubiquitous Language)

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
