# 자동차 보험 청구(Claim) 처리 시스템 -- 도메인 모델 설계

## 1. 전략 설계

### 1.1 하위 도메인 식별

| 하위 도메인 | 유형 | 설명 |
|------------|------|------|
| 청구 심사 (Claim Assessment) | 핵심(Core) | 청구 접수, 심사, 승인/거절 판정 -- 보험사의 경쟁 우위이자 핵심 비즈니스 로직 |
| 보험 계약 (Policy) | 지원(Supporting) | 고객의 보험 가입 정보, 보장 한도 관리 |
| 보상 지급 (Settlement) | 지원(Supporting) | 승인된 청구에 대한 보상금 산정 및 지급 처리 |
| 고객 관리 (Customer) | 일반(Generic) | 고객 기본 정보 관리 |
| 인증/권한 (Identity & Access) | 일반(Generic) | 심사관, 고객 등 사용자 인증 및 권한 |

### 1.2 바운디드 컨텍스트 정의

같은 용어가 다른 의미로 쓰이는 지점이 바운디드 컨텍스트의 경계다.

| 바운디드 컨텍스트 | 포함 하위 도메인 | 핵심 유비쿼터스 언어 |
|-----------------|-----------------|-------------------|
| **청구 컨텍스트 (Claiming)** | 청구 심사 | 청구(Claim), 접수(file), 심사(assess), 승인(approve), 거절(reject), 추가 조사(investigate), 에스컬레이션(escalate) |
| **보험 계약 컨텍스트 (Underwriting)** | 보험 계약 | 보험 증권(Policy), 보장 한도(CoverageLimit), 피보험자(Insured) |
| **보상 컨텍스트 (Settlement)** | 보상 지급 | 보상금(Compensation), 지급(settle), 산정(calculate) |
| **고객 컨텍스트 (Customer)** | 고객 관리, 인증/권한 | 고객(Customer), 계정(Account) |

### 1.3 컨텍스트 맵

```
[고객 컨텍스트] ---(OHS/PL)---> [청구 컨텍스트]
                                      |
                           (Customer-Supplier)
                                      |
                                      v
[보험 계약 컨텍스트] ---(ACL)---> [청구 컨텍스트]
                                      |
                              (Domain Event)
                                      |
                                      v
                              [보상 컨텍스트]
```

- **고객 -> 청구**: 고객 컨텍스트가 Open Host Service로 고객 정보를 제공하고, 청구 컨텍스트는 필요한 정보만 값 객체로 변환하여 사용한다.
- **보험 계약 -> 청구**: 청구 컨텍스트가 보험 계약 정보를 조회할 때 ACL을 통해 자신의 모델(PolicySnapshot)로 변환한다. 보험 계약 컨텍스트의 모델 변경이 청구 컨텍스트를 오염시키지 않도록 방어한다.
- **청구 -> 보상**: 청구가 승인(ClaimApproved 이벤트)되면, 보상 컨텍스트가 이를 구독하여 보상금 산정 및 지급을 처리한다. 결과적 일관성으로 연결한다.

---

## 2. 유비쿼터스 언어 사전

청구 컨텍스트의 핵심 용어를 정의한다. 코드의 클래스명, 메서드명이 이 용어와 정확히 일치해야 한다.

| 용어 (한국어) | 용어 (코드) | 정의 |
|-------------|------------|------|
| 청구 | `Claim` | 고객이 보험 사고 발생 시 보상을 요청하는 행위이자, 그 요청의 전체 생명주기를 나타내는 애그리거트 |
| 접수하다 | `file()` | 고객이 사고 정보를 제출하여 새로운 청구를 생성하는 행위 |
| 심사하다 | `assess()` | 배정된 심사관이 청구를 검토하여 판정을 내리는 행위 |
| 승인하다 | `approve()` | 심사 결과 보상이 타당하다고 판정하는 행위 |
| 거절하다 | `reject()` | 심사 결과 보상이 부당하다고 판정하는 행위 |
| 추가 조사하다 | `investigate()` | 판정을 위해 추가 정보가 필요하다고 결정하는 행위 |
| 에스컬레이션하다 | `escalate()` | 심사 기한(30일) 초과 시 상위 권한으로 이관하는 행위 |
| 지급하다 | `settle()` | 승인된 보상금을 고객에게 지급 완료하는 행위 |
| 심사관 | `AssessorId` | 청구 심사를 담당하는 인물 (ID 참조) |
| 사고 정보 | `IncidentDetails` | 사고 일시, 장소, 유형을 묶은 값 객체 |
| 사고 유형 | `IncidentType` | 충돌, 도난, 자연재해 등 사고의 분류 |
| 예상 피해 금액 | `EstimatedDamage` (Money) | 고객이 신고한 예상 손해 금액 |
| 보장 한도 | `CoverageLimit` (Money) | 보험 계약에서 정한 최대 보상 가능 금액 |
| 보상금 | `Compensation` (Money) | 승인 후 실제 지급할 금액 |
| 보험 증권 스냅샷 | `PolicySnapshot` | 청구 시점의 보험 계약 정보를 캡처한 값 객체 |

---

## 3. 전술 설계 -- 청구 컨텍스트

### 3.1 값 객체 (Value Objects)

값 객체는 불변이며 속성의 조합으로 동등성을 판단한다. 원시 타입 대신 값 객체를 사용하여 비즈니스 의미를 코드에 드러낸다.

```python
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum


# --- 공통 값 객체 ---

@dataclass(frozen=True, slots=True)
class Money:
    """금액 값 객체 -- 부작용 없는 함수와 자기 검증을 구현한다"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, int):
            object.__setattr__(self, "amount", int(self.amount))
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def add(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return replace(self, amount=self.amount + other.amount)

    def subtract(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        if self.amount < other.amount:
            raise ValueError("결과 금액이 음수입니다")
        return replace(self, amount=self.amount - other.amount)

    def is_within(self, limit: Money) -> bool:
        """금액이 한도 이내인지 확인한다"""
        self._ensure_same_currency(limit)
        return self.amount <= limit.amount

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")


# --- 청구 도메인 값 객체 ---

class IncidentType(Enum):
    """사고 유형 -- 유비쿼터스 언어에서 정의한 사고 분류"""
    COLLISION = "collision"         # 충돌
    THEFT = "theft"                 # 도난
    NATURAL_DISASTER = "natural_disaster"  # 자연재해


@dataclass(frozen=True, slots=True)
class IncidentDetails:
    """사고 정보 값 객체 -- 사고 일시, 장소, 유형을 하나의 개념으로 묶는다

    자기 검증: 사고 일시는 미래일 수 없다.
    """
    occurred_at: datetime
    location: str
    incident_type: IncidentType

    def __post_init__(self) -> None:
        if self.occurred_at > datetime.now():
            raise ValueError("사고 일시는 미래일 수 없습니다")
        if not self.location or not self.location.strip():
            raise ValueError("사고 장소는 필수입니다")


@dataclass(frozen=True, slots=True)
class PolicySnapshot:
    """보험 증권 스냅샷 값 객체 -- 청구 시점의 보험 계약 정보를 캡처한다

    ACL 패턴: 보험 계약 컨텍스트의 모델을 청구 컨텍스트의 값 객체로 변환하여 사용한다.
    보험 계약 모델이 변경되어도 청구 컨텍스트는 영향을 받지 않는다.
    """
    policy_id: str
    policyholder_name: str
    coverage_limit: Money

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("보험 증권 ID는 필수입니다")


class AssessmentDecision(Enum):
    """심사 판정 결과 -- 유비쿼터스 언어의 세 가지 판정"""
    APPROVED = "approved"           # 승인
    REJECTED = "rejected"           # 거절
    INVESTIGATION_NEEDED = "investigation_needed"  # 추가 조사
```

### 3.2 청구 애그리거트 (Claim Aggregate)

Claim은 애그리거트 루트다. 모든 비즈니스 불변식은 이 경계 안에서 보호된다.

**Vernon 규칙 적용:**
- 규칙 1: 진정한 불변식(상태 전이 규칙, 보장 한도 초과 검증)을 일관성 경계 안에서 보호한다.
- 규칙 2: Claim 루트 엔티티와 값 객체(IncidentDetails, PolicySnapshot, Money)로 구성한 작은 애그리거트다.
- 규칙 3: 심사관(Assessor)은 별도 바운디드 컨텍스트의 개념이므로 AssessorId(str)로만 참조한다. Policy도 PolicySnapshot 값 객체로 캡처한다.
- 규칙 4: 승인 후 보상 지급은 도메인 이벤트(ClaimApproved)를 통한 결과적 일관성으로 처리한다.

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4


class ClaimStatus(Enum):
    """청구 상태 -- 비즈니스 생명주기를 표현한다"""
    FILED = "filed"                     # 접수됨
    UNDER_ASSESSMENT = "under_assessment"  # 심사 중
    APPROVED = "approved"               # 승인됨
    REJECTED = "rejected"               # 거절됨
    UNDER_INVESTIGATION = "under_investigation"  # 추가 조사 중
    SETTLED = "settled"                 # 지급 완료
    ESCALATED = "escalated"             # 에스컬레이션됨


# --- 도메인 이벤트 ---

@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ClaimFiled(DomainEvent):
    """청구가 접수되었다"""
    claim_id: str = ""
    policy_id: str = ""
    incident_type: str = ""


@dataclass(frozen=True)
class AssessorAssigned(DomainEvent):
    """심사관이 배정되었다"""
    claim_id: str = ""
    assessor_id: str = ""


@dataclass(frozen=True)
class ClaimApproved(DomainEvent):
    """청구가 승인되었다 -- 보상 컨텍스트가 이 이벤트를 구독한다"""
    claim_id: str = ""
    policy_id: str = ""
    compensation_amount: int = 0
    currency: str = "KRW"


@dataclass(frozen=True)
class ClaimRejected(DomainEvent):
    """청구가 거절되었다"""
    claim_id: str = ""
    reason: str = ""


@dataclass(frozen=True)
class ClaimEscalated(DomainEvent):
    """청구가 에스컬레이션되었다 -- 30일 초과"""
    claim_id: str = ""
    days_elapsed: int = 0


@dataclass(frozen=True)
class ClaimSettled(DomainEvent):
    """보상금이 지급 완료되었다"""
    claim_id: str = ""
    compensation_amount: int = 0


# --- 애그리거트 루트 ---

ASSESSMENT_DEADLINE_DAYS = 30


@dataclass
class Claim:
    """청구 애그리거트 루트

    비즈니스 불변식:
    1. 청구 상태 전이는 정해진 순서를 따라야 한다
    2. 심사관이 배정되어야만 심사를 시작할 수 있다
    3. 보상금은 보험의 보장 한도를 초과할 수 없다
    4. 30일 이내에 심사가 완료되지 않으면 에스컬레이션된다
    5. 이미 지급 완료되거나 거절된 청구는 재심사할 수 없다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    customer_id: str = ""                              # Customer 애그리거트를 ID로 참조
    incident_details: IncidentDetails = None
    estimated_damage: Money = None
    policy_snapshot: PolicySnapshot = None
    _status: ClaimStatus = field(default=ClaimStatus.FILED)
    _assessor_id: Optional[str] = field(default=None)  # Assessor를 ID로 참조
    _compensation: Optional[Money] = field(default=None)
    _filed_at: datetime = field(default_factory=datetime.now)
    _assessed_at: Optional[datetime] = field(default=None)
    _rejection_reason: Optional[str] = field(default=None)
    _events: List[DomainEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        """접수 시점의 불변식을 검증한다"""
        if self.incident_details is None:
            raise ValueError("사고 정보는 필수입니다")
        if self.estimated_damage is None:
            raise ValueError("예상 피해 금액은 필수입니다")
        if self.policy_snapshot is None:
            raise ValueError("보험 증권 정보는 필수입니다")
        if not self.customer_id:
            raise ValueError("고객 ID는 필수입니다")

    # --- 팩토리 메서드: 유비쿼터스 언어 'file(접수하다)' ---

    @classmethod
    def file(
        cls,
        customer_id: str,
        incident_details: IncidentDetails,
        estimated_damage: Money,
        policy_snapshot: PolicySnapshot,
    ) -> Claim:
        """청구를 접수한다

        유비쿼터스 언어: '고객이 사고 발생 시 청구를 접수한다'
        """
        claim = cls(
            customer_id=customer_id,
            incident_details=incident_details,
            estimated_damage=estimated_damage,
            policy_snapshot=policy_snapshot,
        )
        claim._events.append(
            ClaimFiled(
                claim_id=claim.id,
                policy_id=policy_snapshot.policy_id,
                incident_type=incident_details.incident_type.value,
            )
        )
        return claim

    # --- 심사관 배정 ---

    def assign_assessor(self, assessor_id: str) -> None:
        """심사관을 배정한다

        불변식: FILED 또는 ESCALATED 상태에서만 심사관을 배정할 수 있다.
        """
        if self._status not in (ClaimStatus.FILED, ClaimStatus.ESCALATED):
            raise ValueError(
                f"{self._status.value} 상태에서는 심사관을 배정할 수 없습니다"
            )
        self._assessor_id = assessor_id
        self._status = ClaimStatus.UNDER_ASSESSMENT
        self._events.append(
            AssessorAssigned(claim_id=self.id, assessor_id=assessor_id)
        )

    # --- 심사 판정: 유비쿼터스 언어 'assess(심사하다)' ---

    def assess(self, decision: AssessmentDecision, reason: str = "") -> None:
        """심사 판정을 내린다

        불변식:
        - UNDER_ASSESSMENT 또는 UNDER_INVESTIGATION 상태에서만 심사할 수 있다
        - 심사관이 배정되어 있어야 한다
        """
        if self._status not in (
            ClaimStatus.UNDER_ASSESSMENT,
            ClaimStatus.UNDER_INVESTIGATION,
        ):
            raise ValueError(
                f"{self._status.value} 상태에서는 심사할 수 없습니다"
            )
        if self._assessor_id is None:
            raise ValueError("심사관이 배정되지 않았습니다")

        if decision == AssessmentDecision.APPROVED:
            self._approve()
        elif decision == AssessmentDecision.REJECTED:
            self._reject(reason)
        elif decision == AssessmentDecision.INVESTIGATION_NEEDED:
            self._investigate()

    def _approve(self) -> None:
        """승인한다 -- 보상금을 산정하고 보장 한도를 검증한다

        불변식: 보상금은 보험의 보장 한도를 초과할 수 없다
        """
        compensation = self._calculate_compensation()
        self._compensation = compensation
        self._status = ClaimStatus.APPROVED
        self._assessed_at = datetime.now()
        self._events.append(
            ClaimApproved(
                claim_id=self.id,
                policy_id=self.policy_snapshot.policy_id,
                compensation_amount=compensation.amount,
                currency=compensation.currency,
            )
        )

    def _reject(self, reason: str) -> None:
        """거절한다"""
        if not reason:
            raise ValueError("거절 사유는 필수입니다")
        self._status = ClaimStatus.REJECTED
        self._rejection_reason = reason
        self._assessed_at = datetime.now()
        self._events.append(
            ClaimRejected(claim_id=self.id, reason=reason)
        )

    def _investigate(self) -> None:
        """추가 조사를 결정한다"""
        self._status = ClaimStatus.UNDER_INVESTIGATION

    def _calculate_compensation(self) -> Money:
        """보상금을 산정한다

        불변식: 보상금은 예상 피해 금액과 보장 한도 중 작은 값이다.
        보장 한도를 절대 초과할 수 없다.
        """
        coverage_limit = self.policy_snapshot.coverage_limit
        if self.estimated_damage.is_within(coverage_limit):
            return self.estimated_damage
        return coverage_limit

    # --- 지급: 유비쿼터스 언어 'settle(지급하다)' ---

    def settle(self) -> None:
        """보상금을 지급 완료한다

        불변식: 승인된 청구만 지급할 수 있다.
        """
        if self._status != ClaimStatus.APPROVED:
            raise ValueError(
                f"{self._status.value} 상태에서는 지급할 수 없습니다. "
                f"승인된 청구만 지급 가능합니다."
            )
        if self._compensation is None:
            raise ValueError("보상금이 산정되지 않았습니다")
        self._status = ClaimStatus.SETTLED
        self._events.append(
            ClaimSettled(
                claim_id=self.id,
                compensation_amount=self._compensation.amount,
            )
        )

    # --- 에스컬레이션: 30일 규칙 ---

    def check_escalation(self) -> None:
        """심사 기한 초과 여부를 확인하고 에스컬레이션한다

        불변식: 접수 후 30일 이내에 심사가 완료되지 않으면
        자동으로 에스컬레이션된다.
        """
        if self._status in (
            ClaimStatus.APPROVED,
            ClaimStatus.REJECTED,
            ClaimStatus.SETTLED,
            ClaimStatus.ESCALATED,
        ):
            return  # 이미 완료되었거나 에스컬레이션된 청구는 무시

        deadline = self._filed_at + timedelta(days=ASSESSMENT_DEADLINE_DAYS)
        if datetime.now() > deadline:
            days_elapsed = (datetime.now() - self._filed_at).days
            self._status = ClaimStatus.ESCALATED
            self._events.append(
                ClaimEscalated(
                    claim_id=self.id,
                    days_elapsed=days_elapsed,
                )
            )

    # --- 조회 메서드 ---

    @property
    def status(self) -> ClaimStatus:
        return self._status

    @property
    def compensation(self) -> Optional[Money]:
        return self._compensation

    @property
    def assessor_id(self) -> Optional[str]:
        return self._assessor_id

    @property
    def is_overdue(self) -> bool:
        """심사 기한(30일)이 초과되었는지 확인한다"""
        if self._assessed_at is not None:
            return False
        deadline = self._filed_at + timedelta(days=ASSESSMENT_DEADLINE_DAYS)
        return datetime.now() > deadline

    # --- 도메인 이벤트 수집 ---

    def collect_domain_events(self) -> List[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events
```

### 3.3 상태 전이 다이어그램

```
FILED ---(assign_assessor)---> UNDER_ASSESSMENT
  |                                |
  |                          (assess: approve)---> APPROVED ---(settle)---> SETTLED
  |                                |
  |                          (assess: reject)----> REJECTED
  |                                |
  |                          (assess: investigate)-> UNDER_INVESTIGATION
  |                                                    |
  |                                              (assess: approve/reject/investigate)
  |                                                    |
  +---(check_escalation: 30일 초과)---> ESCALATED ---(assign_assessor)---> UNDER_ASSESSMENT
```

허용되는 상태 전이:

| 현재 상태 | 허용 행위 | 다음 상태 |
|----------|----------|----------|
| FILED | assign_assessor | UNDER_ASSESSMENT |
| FILED | check_escalation (30일 초과) | ESCALATED |
| UNDER_ASSESSMENT | assess(APPROVED) | APPROVED |
| UNDER_ASSESSMENT | assess(REJECTED) | REJECTED |
| UNDER_ASSESSMENT | assess(INVESTIGATION_NEEDED) | UNDER_INVESTIGATION |
| UNDER_ASSESSMENT | check_escalation (30일 초과) | ESCALATED |
| UNDER_INVESTIGATION | assess(APPROVED) | APPROVED |
| UNDER_INVESTIGATION | assess(REJECTED) | REJECTED |
| UNDER_INVESTIGATION | assess(INVESTIGATION_NEEDED) | UNDER_INVESTIGATION (유지) |
| UNDER_INVESTIGATION | check_escalation (30일 초과) | ESCALATED |
| ESCALATED | assign_assessor | UNDER_ASSESSMENT |
| APPROVED | settle | SETTLED |

종결 상태: REJECTED, SETTLED

### 3.4 비즈니스 불변식 요약

애그리거트 경계 안에서 보호되는 불변식 목록이다.

| # | 불변식 | 보호 위치 | 보호 방식 |
|---|-------|----------|----------|
| 1 | 상태 전이는 정해진 순서를 따른다 | Claim.assess(), assign_assessor(), settle() | 현재 상태 검증 후 거부(ValueError) |
| 2 | 심사관이 배정되어야만 심사할 수 있다 | Claim.assess() | `_assessor_id is None` 검증 |
| 3 | 보상금은 보장 한도를 초과할 수 없다 | Claim._calculate_compensation() | `estimated_damage.is_within(coverage_limit)` 비교 |
| 4 | 30일 이내 미완료 시 에스컬레이션 | Claim.check_escalation() | `_filed_at + 30일` 과 현재 시각 비교 |
| 5 | 거절 시 사유가 반드시 있어야 한다 | Claim._reject() | `reason` 빈 문자열 검증 |
| 6 | 사고 일시는 미래일 수 없다 | IncidentDetails.__post_init__() | 생성 시점 자기 검증 |
| 7 | 금액은 0 이상이어야 한다 | Money.__post_init__() | 생성 시점 자기 검증 |

### 3.5 리포지토리

리포지토리는 애그리거트 단위로 제공한다. IncidentDetails, PolicySnapshot 등 내부 값 객체를 위한 별도 리포지토리는 만들지 않는다.

```python
from abc import ABC, abstractmethod
from typing import List, Optional


class ClaimRepository(ABC):
    """청구 리포지토리 인터페이스

    도메인 영역에 인터페이스를 정의하고, 인프라 영역에서 구현한다 (DIP).
    """

    @abstractmethod
    def find_by_id(self, claim_id: str) -> Optional[Claim]:
        ...

    @abstractmethod
    def save(self, claim: Claim) -> None:
        ...

    @abstractmethod
    def find_overdue_claims(self) -> List[Claim]:
        """심사 기한(30일)이 초과된 미완료 청구 목록을 조회한다

        에스컬레이션 배치 처리에 사용된다.
        """
        ...
```

### 3.6 충돌 방지 계층 (ACL)

보험 계약 컨텍스트의 모델을 청구 컨텍스트의 PolicySnapshot으로 변환한다.

```python
@dataclass
class ExternalPolicyDTO:
    """보험 계약 컨텍스트의 외부 모델 -- 우리가 제어할 수 없다"""
    pol_no: str
    holder_nm: str
    max_coverage_amt: float
    coverage_currency: str
    effective_from: str
    effective_to: str


class PolicyAnticorruptionLayer:
    """ACL: 보험 계약 컨텍스트 -> 청구 컨텍스트 번역

    보험 계약 모델의 변경이 청구 컨텍스트를 오염시키지 않도록
    번역 계층에서 차단한다.
    """

    def to_policy_snapshot(self, external: ExternalPolicyDTO) -> PolicySnapshot:
        return PolicySnapshot(
            policy_id=external.pol_no,
            policyholder_name=external.holder_nm,
            coverage_limit=Money(
                amount=int(external.max_coverage_amt),
                currency=external.coverage_currency,
            ),
        )
```

### 3.7 응용 서비스 (유스케이스 조율)

응용 서비스는 도메인 로직을 포함하지 않는다. 리포지토리 조회, 애그리거트 호출, 트랜잭션 관리만 담당한다.

```python
@dataclass
class FileClaimCommand:
    """청구 접수 커맨드"""
    customer_id: str
    incident_occurred_at: datetime
    incident_location: str
    incident_type: str
    estimated_damage_amount: int
    policy_id: str


class ClaimApplicationService:
    """청구 응용 서비스 -- 도메인 로직 없이 흐름만 제어한다"""

    def __init__(
        self,
        claim_repository: ClaimRepository,
        policy_acl: PolicyAnticorruptionLayer,
        policy_client: "PolicyServiceClient",
    ):
        self._claim_repo = claim_repository
        self._policy_acl = policy_acl
        self._policy_client = policy_client

    def file_claim(self, cmd: FileClaimCommand) -> str:
        """청구 접수 유스케이스"""
        # 1. 보험 계약 조회 후 ACL로 변환
        external_policy = self._policy_client.fetch(cmd.policy_id)
        policy_snapshot = self._policy_acl.to_policy_snapshot(external_policy)

        # 2. 값 객체 생성
        incident_details = IncidentDetails(
            occurred_at=cmd.incident_occurred_at,
            location=cmd.incident_location,
            incident_type=IncidentType(cmd.incident_type),
        )
        estimated_damage = Money(amount=cmd.estimated_damage_amount)

        # 3. 애그리거트 생성 (도메인 로직은 Claim.file()에 위임)
        claim = Claim.file(
            customer_id=cmd.customer_id,
            incident_details=incident_details,
            estimated_damage=estimated_damage,
            policy_snapshot=policy_snapshot,
        )

        # 4. 저장
        self._claim_repo.save(claim)
        return claim.id

    def assign_assessor(self, claim_id: str, assessor_id: str) -> None:
        """심사관 배정 유스케이스"""
        claim = self._claim_repo.find_by_id(claim_id)
        if claim is None:
            raise ValueError("청구를 찾을 수 없습니다")
        claim.assign_assessor(assessor_id)  # 도메인 로직에 위임
        self._claim_repo.save(claim)

    def assess_claim(
        self, claim_id: str, decision: str, reason: str = ""
    ) -> None:
        """심사 판정 유스케이스"""
        claim = self._claim_repo.find_by_id(claim_id)
        if claim is None:
            raise ValueError("청구를 찾을 수 없습니다")
        claim.assess(
            decision=AssessmentDecision(decision),
            reason=reason,
        )
        self._claim_repo.save(claim)

    def settle_claim(self, claim_id: str) -> None:
        """보상금 지급 유스케이스"""
        claim = self._claim_repo.find_by_id(claim_id)
        if claim is None:
            raise ValueError("청구를 찾을 수 없습니다")
        claim.settle()  # 도메인 로직에 위임
        self._claim_repo.save(claim)


class EscalationBatchService:
    """에스컬레이션 배치 서비스 -- 주기적으로 실행된다"""

    def __init__(self, claim_repository: ClaimRepository):
        self._claim_repo = claim_repository

    def check_and_escalate_overdue_claims(self) -> None:
        """기한 초과 청구를 에스컬레이션한다"""
        overdue_claims = self._claim_repo.find_overdue_claims()
        for claim in overdue_claims:
            claim.check_escalation()  # 도메인 로직에 위임
            self._claim_repo.save(claim)
```

---

## 4. 설계 결정 근거 요약

| 설계 결정 | 근거 |
|----------|------|
| Claim을 단일 애그리거트로 설계 | 모든 비즈니스 불변식(상태 전이, 보장 한도 검증)이 하나의 트랜잭션 경계에서 보호되어야 한다 (Vernon 규칙 1) |
| PolicySnapshot을 값 객체로 캡처 | 청구 시점의 보험 정보를 불변으로 보존한다. 이후 보험 계약이 변경되어도 청구 판정에 영향이 없다 |
| Assessor를 ID(str)로만 참조 | 심사관은 별도 바운디드 컨텍스트의 개념이다. 직접 참조 대신 ID 참조로 결합도를 낮춘다 (Vernon 규칙 3) |
| 승인 후 보상 처리를 도메인 이벤트로 연결 | 청구 승인과 보상 지급은 서로 다른 바운디드 컨텍스트의 관심사다. 결과적 일관성으로 처리한다 (Vernon 규칙 4) |
| `file()`, `assess()`, `settle()` 등 비즈니스 의도를 드러내는 메서드명 | `updateStatus()` 대신 유비쿼터스 언어를 코드에 반영한다 (의도를 드러내는 인터페이스) |
| Money, IncidentDetails 등 값 객체 적극 활용 | 원시 타입(int, str) 대신 값 객체로 비즈니스 의미를 부여하고, 불변성으로 부작용을 제거한다 |
| ACL로 보험 계약 컨텍스트 모델을 변환 | 외부 모델(ExternalPolicyDTO)이 청구 컨텍스트를 오염시키지 않도록 번역 계층에서 차단한다 |
| 에스컬레이션을 Claim 내부 메서드로 구현 | 30일 규칙은 Claim 애그리거트의 비즈니스 불변식이다. 외부 서비스가 아닌 도메인 객체 안에서 보호한다 |
