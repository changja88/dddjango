# 바운디드 컨텍스트와 컨텍스트 맵

## 2.4 바운디드 컨텍스트 (Bounded Context)

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

## 2.5 컨텍스트 맵 (Context Map)

> 출처: [B][C], Evans 파란책 Chapter 14, Open Group DDD Strategic Patterns

바운디드 컨텍스트 간의 관계를 시각적으로 표현한 도식이다.

### 전체 연동 패턴 정리

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

### 충돌 방지 계층(ACL) 패턴 구현 예시

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
