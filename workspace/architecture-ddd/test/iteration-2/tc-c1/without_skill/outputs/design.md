# 자동차 보험 청구(Claim) 처리 시스템 - 도메인 모델 설계

## 1. 유비쿼터스 언어 (Ubiquitous Language)

| 용어 | 정의 |
|------|------|
| Claim (청구) | 고객이 사고 발생 후 보험금 지급을 요청하는 행위이자, 그 요청의 전체 생명주기를 나타내는 핵심 도메인 객체 |
| File (접수) | 고객이 청구를 최초로 제출하는 행위 |
| Incident (사고) | 보험 청구의 원인이 되는 사건. 일시, 장소, 유형, 예상 피해 금액을 포함 |
| IncidentType (사고 유형) | 충돌(Collision), 도난(Theft), 자연재해(NaturalDisaster)로 분류 |
| Assessor (심사관) | 청구를 배정받아 심사를 수행하는 담당자 |
| Assessment (심사) | 심사관이 청구를 검토하고 결정을 내리는 과정 |
| AssessmentDecision (심사 결정) | 승인(Approved), 거절(Rejected), 추가 조사(UnderInvestigation)의 심사 결과 |
| Settlement (보상 지급) | 승인된 청구에 대해 보상금을 산정하고 지급하는 행위 |
| Coverage (보장) | 가입 보험의 보장 한도를 나타내는 정보 |
| Escalation (에스컬레이션) | 심사가 기한 내 완료되지 않았을 때 상위 처리로 전환되는 행위 |

## 2. 도메인 모델 구조

### 2.1 Aggregate 경계

```
[Claim Aggregate] ─── root: Claim
  ├── Incident (Value Object)
  ├── Assessment (Entity)
  └── Settlement (Value Object)

[Policy Aggregate] ─── root: Policy
  └── Coverage (Value Object)

[Assessor Aggregate] ─── root: Assessor
```

- **Claim**이 핵심 Aggregate Root이며, Incident/Assessment/Settlement을 내부에 포함한다.
- **Policy**는 별도 Aggregate로 분리한다. Claim이 Policy를 참조하되 ID로만 참조하여 Aggregate 간 결합을 끊는다.
- **Assessor**는 독립 Aggregate이며, Claim은 AssessorId로만 참조한다.

### 2.2 Value Objects

```python
@dataclass(frozen=True)
class IncidentType:
    """사고 유형 - 열거형 Value Object"""
    COLLISION = "COLLISION"           # 충돌
    THEFT = "THEFT"                   # 도난
    NATURAL_DISASTER = "NATURAL_DISASTER"  # 자연재해

    value: str

    def __post_init__(self):
        if self.value not in (self.COLLISION, self.THEFT, self.NATURAL_DISASTER):
            raise ValueError(f"유효하지 않은 사고 유형: {self.value}")


@dataclass(frozen=True)
class Money:
    """금액 Value Object - 음수 불허"""
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("금액은 음수일 수 없습니다")

    def exceeds(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount > other.amount

    def _assert_same_currency(self, other: "Money"):
        if self.currency != other.currency:
            raise ValueError("통화 단위가 일치하지 않습니다")


@dataclass(frozen=True)
class Location:
    """사고 장소 Value Object"""
    address: str
    city: str
    district: str

    def __post_init__(self):
        if not self.address or not self.address.strip():
            raise ValueError("사고 장소 주소는 비어있을 수 없습니다")


@dataclass(frozen=True)
class Incident:
    """사고 정보 Value Object - 청구의 원인이 되는 사건"""
    occurred_at: datetime
    location: Location
    incident_type: IncidentType
    estimated_damage: Money

    def __post_init__(self):
        if self.occurred_at > datetime.now():
            raise ValueError("사고 일시는 미래일 수 없습니다")
        if self.estimated_damage.amount <= 0:
            raise ValueError("예상 피해 금액은 0보다 커야 합니다")


@dataclass(frozen=True)
class Coverage:
    """보장 한도 Value Object"""
    coverage_limit: Money
    deductible: Money  # 자기부담금

    def calculate_max_payout(self) -> Money:
        """보장 한도에서 자기부담금을 차감한 최대 지급액"""
        max_amount = self.coverage_limit.amount - self.deductible.amount
        return Money(amount=max(max_amount, Decimal("0")), currency=self.coverage_limit.currency)


@dataclass(frozen=True)
class Settlement:
    """보상 지급 Value Object"""
    settlement_amount: Money
    settled_at: datetime
```

### 2.3 Entities / Aggregate Roots

```python
class AssessmentDecision(Enum):
    """심사 결정"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"


class ClaimStatus(Enum):
    """청구 상태 - Claim의 생명주기"""
    FILED = "FILED"                         # 접수됨
    ASSESSOR_ASSIGNED = "ASSESSOR_ASSIGNED" # 심사관 배정됨
    UNDER_ASSESSMENT = "UNDER_ASSESSMENT"   # 심사 중
    APPROVED = "APPROVED"                   # 승인됨
    REJECTED = "REJECTED"                   # 거절됨
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"  # 추가 조사 중
    SETTLED = "SETTLED"                     # 지급 완료
    ESCALATED = "ESCALATED"                 # 에스컬레이션됨


class Assessment:
    """심사 Entity - Claim Aggregate 내부 Entity"""

    def __init__(self, assessor_id: str, assigned_at: datetime):
        self.assessor_id = assessor_id
        self.assigned_at = assigned_at
        self.decision: AssessmentDecision | None = None
        self.decided_at: datetime | None = None
        self.notes: str = ""

    @property
    def is_completed(self) -> bool:
        return self.decision is not None

    @property
    def is_overdue(self) -> bool:
        """30일 초과 여부"""
        if self.is_completed:
            return False
        elapsed = datetime.now() - self.assigned_at
        return elapsed.days > 30

    def decide(self, decision: AssessmentDecision, notes: str = ""):
        if self.is_completed:
            raise InvalidOperationError("이미 완료된 심사는 재결정할 수 없습니다")
        self.decision = decision
        self.decided_at = datetime.now()
        self.notes = notes


class Claim:
    """
    청구 Aggregate Root

    비즈니스 불변식:
    1. 청구는 반드시 유효한 사고 정보(Incident)를 포함해야 한다.
    2. 심사관은 접수(FILED) 상태의 청구에만 배정할 수 있다.
    3. 심사 결정은 심사관이 배정된(ASSESSOR_ASSIGNED) 상태에서만 가능하다.
    4. 보상금은 보장 한도를 초과할 수 없다.
    5. 지급은 승인(APPROVED) 상태의 청구에만 가능하다.
    6. 30일 이내 심사 미완료 시 자동 에스컬레이션 대상이 된다.
    """

    def __init__(self, claim_id: str, policy_id: str, incident: Incident, filed_at: datetime):
        # --- 불변식: 유효한 사고 정보 필수 ---
        if incident is None:
            raise ValueError("청구에는 반드시 사고 정보가 포함되어야 합니다")

        self._claim_id = claim_id
        self._policy_id = policy_id
        self._incident = incident
        self._filed_at = filed_at
        self._status = ClaimStatus.FILED
        self._assessment: Assessment | None = None
        self._settlement: Settlement | None = None
        self._domain_events: list = []

    # ── Properties ──

    @property
    def claim_id(self) -> str:
        return self._claim_id

    @property
    def status(self) -> ClaimStatus:
        return self._status

    @property
    def incident(self) -> Incident:
        return self._incident

    @property
    def assessment(self) -> Assessment | None:
        return self._assessment

    @property
    def settlement(self) -> Settlement | None:
        return self._settlement

    # ── Commands (상태 전이 메서드) ──

    def assign_assessor(self, assessor_id: str):
        """
        심사관 배정

        불변식: 접수(FILED) 상태에서만 심사관을 배정할 수 있다.
        """
        if self._status != ClaimStatus.FILED:
            raise InvalidOperationError(
                f"심사관 배정은 FILED 상태에서만 가능합니다. 현재 상태: {self._status.value}"
            )
        self._assessment = Assessment(assessor_id=assessor_id, assigned_at=datetime.now())
        self._status = ClaimStatus.ASSESSOR_ASSIGNED
        self._register_event(AssessorAssignedEvent(self._claim_id, assessor_id))

    def assess(self, decision: AssessmentDecision, notes: str = ""):
        """
        심사 결정 수행

        불변식: 심사관이 배정된 상태에서만 심사 결정이 가능하다.
        """
        if self._status != ClaimStatus.ASSESSOR_ASSIGNED:
            raise InvalidOperationError(
                f"심사는 ASSESSOR_ASSIGNED 상태에서만 가능합니다. 현재 상태: {self._status.value}"
            )
        self._assessment.decide(decision, notes)

        status_map = {
            AssessmentDecision.APPROVED: ClaimStatus.APPROVED,
            AssessmentDecision.REJECTED: ClaimStatus.REJECTED,
            AssessmentDecision.UNDER_INVESTIGATION: ClaimStatus.UNDER_INVESTIGATION,
        }
        self._status = status_map[decision]
        self._register_event(ClaimAssessedEvent(self._claim_id, decision))

    def settle(self, settlement_amount: Money, coverage: Coverage):
        """
        보상금 지급

        불변식:
        - 승인(APPROVED) 상태에서만 지급 가능하다.
        - 보상금은 보장 한도(보장 한도 - 자기부담금)를 초과할 수 없다.
        """
        if self._status != ClaimStatus.APPROVED:
            raise InvalidOperationError(
                f"지급은 APPROVED 상태에서만 가능합니다. 현재 상태: {self._status.value}"
            )

        max_payout = coverage.calculate_max_payout()
        if settlement_amount.exceeds(max_payout):
            raise BusinessRuleViolationError(
                f"보상금({settlement_amount.amount})이 "
                f"보장 한도({max_payout.amount})를 초과합니다"
            )

        self._settlement = Settlement(
            settlement_amount=settlement_amount,
            settled_at=datetime.now()
        )
        self._status = ClaimStatus.SETTLED
        self._register_event(ClaimSettledEvent(self._claim_id, settlement_amount))

    def escalate(self):
        """
        에스컬레이션

        불변식: 심사관이 배정된 상태에서 30일 초과 시에만 에스컬레이션 가능하다.
        """
        if self._assessment is None:
            raise InvalidOperationError("심사관이 배정되지 않은 청구는 에스컬레이션할 수 없습니다")
        if not self._assessment.is_overdue:
            raise InvalidOperationError("심사 기한(30일)이 경과하지 않아 에스컬레이션할 수 없습니다")
        if self._assessment.is_completed:
            raise InvalidOperationError("이미 심사가 완료된 청구는 에스컬레이션할 수 없습니다")

        self._status = ClaimStatus.ESCALATED
        self._register_event(ClaimEscalatedEvent(self._claim_id))

    # ── Domain Events ──

    def _register_event(self, event):
        self._domain_events.append(event)

    def pull_events(self) -> list:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


class Policy:
    """보험 정책 Aggregate Root"""

    def __init__(self, policy_id: str, holder_name: str, coverage: Coverage):
        self._policy_id = policy_id
        self._holder_name = holder_name
        self._coverage = coverage

    @property
    def policy_id(self) -> str:
        return self._policy_id

    @property
    def coverage(self) -> Coverage:
        return self._coverage
```

## 3. 도메인 이벤트 (Domain Events)

```python
@dataclass(frozen=True)
class ClaimFiledEvent:
    claim_id: str
    policy_id: str
    incident_type: IncidentType
    filed_at: datetime

@dataclass(frozen=True)
class AssessorAssignedEvent:
    claim_id: str
    assessor_id: str

@dataclass(frozen=True)
class ClaimAssessedEvent:
    claim_id: str
    decision: AssessmentDecision

@dataclass(frozen=True)
class ClaimSettledEvent:
    claim_id: str
    settlement_amount: Money

@dataclass(frozen=True)
class ClaimEscalatedEvent:
    claim_id: str
```

## 4. Claim 상태 전이 다이어그램

```
FILED
  │
  ├─ assign_assessor() ──> ASSESSOR_ASSIGNED
  │                            │
  │                            ├─ assess(APPROVED) ──> APPROVED
  │                            │                          │
  │                            │                          └─ settle() ──> SETTLED
  │                            │
  │                            ├─ assess(REJECTED) ──> REJECTED
  │                            │
  │                            ├─ assess(UNDER_INVESTIGATION) ──> UNDER_INVESTIGATION
  │                            │
  │                            └─ escalate() [30일 초과] ──> ESCALATED
```

## 5. 비즈니스 불변식 요약

| # | 불변식 | 보호 위치 | 보호 방식 |
|---|--------|-----------|-----------|
| 1 | 청구는 반드시 유효한 사고 정보를 포함해야 한다 | `Claim.__init__` | 생성자에서 None 검증, Incident VO 내부에서 각 필드 자체 검증 |
| 2 | 사고 일시는 미래일 수 없다 | `Incident.__post_init__` | Value Object 생성 시점에 검증 |
| 3 | 금액은 음수일 수 없다 | `Money.__post_init__` | Value Object 생성 시점에 검증 |
| 4 | 심사관은 FILED 상태에서만 배정 가능하다 | `Claim.assign_assessor` | 상태 가드 조건 |
| 5 | 심사 결정은 ASSESSOR_ASSIGNED 상태에서만 가능하다 | `Claim.assess` | 상태 가드 조건 |
| 6 | 보상금은 보장 한도를 초과할 수 없다 | `Claim.settle` | Coverage의 max_payout과 비교 |
| 7 | 지급은 APPROVED 상태에서만 가능하다 | `Claim.settle` | 상태 가드 조건 |
| 8 | 완료된 심사는 재결정할 수 없다 | `Assessment.decide` | is_completed 가드 |
| 9 | 30일 초과 미완료 심사만 에스컬레이션 가능하다 | `Claim.escalate` | is_overdue + is_completed 가드 |

## 6. 커스텀 예외

```python
class InvalidOperationError(Exception):
    """도메인 상태 전이 규칙 위반 시 발생"""
    pass

class BusinessRuleViolationError(Exception):
    """비즈니스 불변식 위반 시 발생"""
    pass
```

## 7. 에스컬레이션 정책 (Domain Service)

30일 자동 에스컬레이션은 Aggregate 외부에서 주기적으로 실행되는 Domain Service가 담당한다. Claim 자체는 `escalate()` 메서드를 통해 에스컬레이션 가능 여부를 판단하고, 실제 스케줄링은 인프라 계층에 위임한다.

```python
class EscalationService:
    """에스컬레이션 도메인 서비스 - 30일 초과 미완료 심사 자동 에스컬레이션"""

    def __init__(self, claim_repository: ClaimRepository):
        self._claim_repository = claim_repository

    def escalate_overdue_claims(self):
        """미완료 심사 중 30일이 경과한 청구를 일괄 에스컬레이션"""
        pending_claims = self._claim_repository.find_by_status(ClaimStatus.ASSESSOR_ASSIGNED)
        for claim in pending_claims:
            if claim.assessment and claim.assessment.is_overdue:
                claim.escalate()
                self._claim_repository.save(claim)
```

## 8. 설계 결정 근거

1. **Incident를 Value Object로 설계**: 사고 정보는 청구 접수 시 확정되며 이후 변경되지 않는다. 고유 식별자가 필요 없고, 속성의 동등성으로 비교하므로 Value Object가 적합하다.

2. **Assessment를 Entity로 설계**: 심사는 배정 후 결정이 내려지기까지 상태가 변화하며, Claim 내에서 고유하게 식별 가능해야 한다. 다만 Claim 외부에서 독립적으로 존재하지 않으므로 Aggregate 내부 Entity로 둔다.

3. **Settlement를 Value Object로 설계**: 지급은 한 번 확정되면 변경되지 않는 최종 결과이다. 금액과 시점의 조합으로 동등성을 판단하므로 Value Object가 적합하다.

4. **Policy를 별도 Aggregate로 분리**: Policy는 Claim과 생명주기가 다르다. Claim이 생성되기 전에 이미 존재하며, 여러 Claim이 하나의 Policy를 참조할 수 있다. ID 참조를 통해 Aggregate 간 결합을 느슨하게 유지한다.

5. **settle() 메서드에 Coverage를 파라미터로 전달**: Claim이 Policy Aggregate를 직접 참조하지 않도록 Coverage Value Object를 외부에서 주입받는다. 이는 Application Service 계층에서 Policy를 조회한 후 Coverage를 추출하여 전달하는 방식으로 구현한다.
