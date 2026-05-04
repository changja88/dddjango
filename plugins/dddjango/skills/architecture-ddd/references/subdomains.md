# 도메인, 하위 도메인, 증류

## 2.2 도메인과 하위 도메인

> 출처: [A][B][C], Evans 파란책, Millett

도메인은 소프트웨어가 해결하려는 비즈니스 영역이며, 여러 하위 도메인으로 구성된다. [C]에서는 하위 도메인을 "문제점 공간(problem space)"의 일부로 정의하고, 바운디드 컨텍스트를 "해결책 공간(solution space)"으로 분리하여 설명한다.

### 하위 도메인 유형 [B]

| 유형 | 경쟁 우위 | 복잡성 | 변동성 | 솔루션 전략 |
|------|----------|--------|--------|------------|
| 핵심(Core) | 직접적 경쟁력 | 높음 | 잦은 변경 | 사내 구현 필수 |
| 일반(Generic) | 없음 | 높음 (알려진 문제) | 낮음 | 외부 솔루션/오픈소스 |
| 지원(Supporting) | 없음 | 낮음 (CRUD 수준) | 낮음 | 하청 가능, RAD |

### 문제 공간과 솔루션 공간의 분리 (Millett)

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

## 2.6 증류 (Distillation)

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
