# 대출 심사 시스템 -- 대출 승인 규칙 도메인 모델 설계

## 1. 전략 설계

### 1.1 하위 도메인 식별

| 하위 도메인 | 유형 | 설명 |
|------------|------|------|
| 대출 심사(Loan Underwriting) | 핵심(Core) | 대출 승인 규칙의 정의와 평가 -- 금융사의 리스크 관리 역량이자 경쟁 우위의 원천 |
| 신용 평가(Credit Scoring) | 일반(Generic) | 외부 신용평가기관(CB)의 점수 조회 -- 모든 금융사가 동일 방식 |
| 고객 관리(Customer Management) | 지원(Supporting) | 고객 정보 관리 CRUD |

### 1.2 바운디드 컨텍스트

대출 심사는 핵심 도메인이므로 독립된 바운디드 컨텍스트로 설계한다.

- **대출 심사 컨텍스트(Loan Underwriting Context)**: 대출 신청 접수, 승인 규칙 평가, 심사 결과 결정
- **신용 평가 컨텍스트(Credit Scoring Context)**: 외부 CB 연동, 신용 점수 조회 (일반 하위 도메인 -- ACL로 격리)
- **고객 컨텍스트(Customer Context)**: 고객 기본 정보, 소득, 재직 정보 관리

### 1.3 컨텍스트 맵

```
[고객 컨텍스트] ----(고객-공급자)----> [대출 심사 컨텍스트]
[신용 평가 컨텍스트] ----(ACL)----> [대출 심사 컨텍스트]
```

- 신용 평가 컨텍스트는 외부 시스템이므로 충돌 방지 계층(ACL)을 두어 외부 모델이 대출 심사 도메인을 오염시키지 않도록 한다.
- 고객 컨텍스트는 고객-공급자 관계로, 대출 심사 컨텍스트가 필요한 고객 데이터를 요청한다.

---

## 2. 유비쿼터스 언어

| 용어 | 정의 |
|------|------|
| 대출 신청(LoanApplication) | 고객이 제출한 대출 요청. 심사의 대상이 되는 애그리거트 |
| 심사(Underwriting) | 대출 신청에 대해 승인 규칙들을 평가하는 행위 |
| 승인 규칙(ApprovalRule) | 대출 승인 여부를 판단하는 개별 비즈니스 규칙 |
| 심사 결과(UnderwritingResult) | 모든 승인 규칙의 평가 결과를 종합한 최종 판정 |
| 신용 점수(CreditScore) | 신용평가기관에서 산출한 고객의 신용도 수치 |
| 부채 소득 비율(DebtToIncomeRatio) | 연 소득 대비 총 부채의 비율. DTI라고도 부른다 |
| 추가 심사(AdditionalReview) | 기본 규칙은 통과했으나 특정 조건에 해당하여 별도 검토가 필요한 상태 |

---

## 3. 전술 설계

### 3.1 값 객체 (Value Objects)

값 객체로 원시 타입을 대체하여 도메인 개념을 명시적으로 표현하고, 자기 검증을 통해 불변식을 보장한다.

```python
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class CreditScore:
    """신용 점수 값 객체"""
    value: int

    def __post_init__(self) -> None:
        if not (0 <= self.value <= 1000):
            raise ValueError(f"신용 점수는 0~1000 범위여야 합니다: {self.value}")

    def meets_minimum(self, minimum: int) -> bool:
        """최소 신용 점수 기준을 충족하는지 판단한다"""
        return self.value >= minimum


@dataclass(frozen=True, slots=True)
class DebtToIncomeRatio:
    """부채 소득 비율(DTI) 값 객체

    total_debt와 annual_income을 받아 비율을 계산한다.
    비율은 백분율로 표현한다 (예: 35.5%).
    """
    total_debt: int
    annual_income: int

    def __post_init__(self) -> None:
        if self.annual_income <= 0:
            raise ValueError(f"연 소득은 양수여야 합니다: {self.annual_income}")
        if self.total_debt < 0:
            raise ValueError(f"총 부채는 0 이상이어야 합니다: {self.total_debt}")

    @property
    def ratio_percent(self) -> float:
        """DTI를 백분율로 반환한다"""
        return (self.total_debt / self.annual_income) * 100

    def is_within_limit(self, limit_percent: float) -> bool:
        """DTI가 한도 이내인지 판단한다"""
        return self.ratio_percent <= limit_percent


@dataclass(frozen=True, slots=True)
class EmploymentDuration:
    """재직 기간 값 객체 (월 단위)"""
    months: int

    def __post_init__(self) -> None:
        if self.months < 0:
            raise ValueError(f"재직 기간은 0 이상이어야 합니다: {self.months}")

    @property
    def years(self) -> float:
        return self.months / 12

    def meets_minimum_years(self, minimum_years: int) -> bool:
        """최소 재직 기간(년)을 충족하는지 판단한다"""
        return self.months >= minimum_years * 12


@dataclass(frozen=True, slots=True)
class Money:
    """금액 값 객체"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def exceeds_multiple_of(self, base_amount: int, multiple: int) -> bool:
        """기준 금액의 배수를 초과하는지 판단한다"""
        return self.amount > base_amount * multiple


class DelinquencyStatus(Enum):
    """연체 이력 상태"""
    NONE = "none"               # 연체 이력 없음
    PAST_RESOLVED = "resolved"  # 과거 연체 후 해소
    ACTIVE = "active"           # 현재 연체 중
```

### 3.2 Specification 패턴 -- 승인 규칙

Specification 패턴을 적용하여 각 비즈니스 규칙을 독립된 객체로 캡슐화한다. 규칙의 개별 검증, 논리 연산자를 통한 조합, 새 규칙 추가가 모두 가능하다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Generic, List

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """Specification 패턴 기본 클래스

    - is_satisfied_by: 후보가 규칙을 만족하는지 판단한다
    - &, |, ~ 연산자로 조합할 수 있다
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """규칙의 비즈니스 설명을 반환한다"""
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

    @property
    def description(self) -> str:
        return f"({self._left.description}) AND ({self._right.description})"

    def is_satisfied_by(self, candidate: T) -> bool:
        return (
            self._left.is_satisfied_by(candidate)
            and self._right.is_satisfied_by(candidate)
        )


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    @property
    def description(self) -> str:
        return f"({self._left.description}) OR ({self._right.description})"

    def is_satisfied_by(self, candidate: T) -> bool:
        return (
            self._left.is_satisfied_by(candidate)
            or self._right.is_satisfied_by(candidate)
        )


class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]):
        self._spec = spec

    @property
    def description(self) -> str:
        return f"NOT ({self._spec.description})"

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self._spec.is_satisfied_by(candidate)
```

### 3.3 대출 신청 엔티티 -- Specification의 검증 대상

```python
@dataclass
class LoanApplication:
    """대출 신청 -- 심사 대상이 되는 정보를 보유한다

    Specification의 candidate로 사용된다.
    """
    applicant_id: str
    credit_score: CreditScore
    dti: DebtToIncomeRatio
    employment_duration: EmploymentDuration
    delinquency_status: DelinquencyStatus
    requested_amount: Money
    annual_income: int
```

### 3.4 개별 승인 규칙 Specification 구현

각 규칙은 독립형 클래스(Standalone Class)로 설계하여 개별 이해와 테스트가 가능하다. 비즈니스 규칙의 임계값을 생성자 파라미터로 받아 유연성을 확보한다.

```python
class MinimumCreditScoreRule(Specification[LoanApplication]):
    """신용 점수 최소 기준 규칙"""

    def __init__(self, minimum_score: int = 700):
        self._minimum_score = minimum_score

    @property
    def description(self) -> str:
        return f"신용 점수가 {self._minimum_score}점 이상이어야 한다"

    def is_satisfied_by(self, application: LoanApplication) -> bool:
        return application.credit_score.meets_minimum(self._minimum_score)


class MaximumDTIRule(Specification[LoanApplication]):
    """부채 소득 비율(DTI) 상한 규칙"""

    def __init__(self, max_dti_percent: float = 40.0):
        self._max_dti_percent = max_dti_percent

    @property
    def description(self) -> str:
        return f"DTI가 {self._max_dti_percent}% 이하여야 한다"

    def is_satisfied_by(self, application: LoanApplication) -> bool:
        return application.dti.is_within_limit(self._max_dti_percent)


class MinimumEmploymentDurationRule(Specification[LoanApplication]):
    """최소 재직 기간 규칙"""

    def __init__(self, minimum_years: int = 1):
        self._minimum_years = minimum_years

    @property
    def description(self) -> str:
        return f"재직 기간이 {self._minimum_years}년 이상이어야 한다"

    def is_satisfied_by(self, application: LoanApplication) -> bool:
        return application.employment_duration.meets_minimum_years(
            self._minimum_years
        )


class NoDelinquencyHistoryRule(Specification[LoanApplication]):
    """연체 이력 없음 규칙"""

    @property
    def description(self) -> str:
        return "기존 연체 이력이 없어야 한다"

    def is_satisfied_by(self, application: LoanApplication) -> bool:
        return application.delinquency_status == DelinquencyStatus.NONE


class AdditionalReviewRequiredRule(Specification[LoanApplication]):
    """추가 심사 필요 여부 판단 규칙

    신청 금액이 연 소득의 일정 배수를 초과하면 추가 심사가 필요하다.
    """

    def __init__(self, income_multiple: int = 5):
        self._income_multiple = income_multiple

    @property
    def description(self) -> str:
        return f"신청 금액이 연 소득의 {self._income_multiple}배를 초과하면 추가 심사가 필요하다"

    def is_satisfied_by(self, application: LoanApplication) -> bool:
        return application.requested_amount.exceeds_multiple_of(
            application.annual_income, self._income_multiple
        )
```

### 3.5 심사 결과 값 객체

```python
class UnderwritingDecision(Enum):
    """심사 판정"""
    APPROVED = "approved"                    # 승인
    REJECTED = "rejected"                    # 거절
    ADDITIONAL_REVIEW_REQUIRED = "additional_review_required"  # 추가 심사 필요


@dataclass(frozen=True)
class RuleEvaluationResult:
    """개별 규칙 평가 결과 값 객체"""
    rule_description: str
    is_satisfied: bool

    @property
    def is_violated(self) -> bool:
        return not self.is_satisfied


@dataclass(frozen=True)
class UnderwritingResult:
    """심사 결과 값 객체

    모든 규칙의 평가 결과와 최종 판정을 포함한다.
    불변이며, 심사 이력 추적에 활용된다.
    """
    decision: UnderwritingDecision
    rule_results: tuple[RuleEvaluationResult, ...]
    requires_additional_review: bool

    @property
    def violated_rules(self) -> list[RuleEvaluationResult]:
        """위반된 규칙 목록을 반환한다"""
        return [r for r in self.rule_results if r.is_violated]

    @property
    def satisfied_rules(self) -> list[RuleEvaluationResult]:
        """충족된 규칙 목록을 반환한다"""
        return [r for r in self.rule_results if r.is_satisfied]
```

### 3.6 도메인 서비스 -- 심사 엔진

심사 엔진은 여러 규칙(Specification)을 조합하여 대출 신청을 평가하는 도메인 서비스다. 상태 없이(stateless) 로직만 구현한다. 규칙 목록을 외부에서 주입받으므로 규칙의 추가/변경/조합이 자유롭다.

```python
class LoanUnderwritingService:
    """대출 심사 도메인 서비스

    - 상태가 없다 (stateless)
    - 여러 승인 규칙(Specification)을 조합하여 심사한다
    - 규칙 목록은 외부에서 주입받아 유연하게 변경 가능하다
    """

    def __init__(
        self,
        approval_rules: list[Specification[LoanApplication]],
        additional_review_rule: Specification[LoanApplication],
    ):
        self._approval_rules = approval_rules
        self._additional_review_rule = additional_review_rule

    def evaluate(self, application: LoanApplication) -> UnderwritingResult:
        """대출 신청에 대해 모든 승인 규칙을 평가하고 결과를 반환한다"""
        rule_results: list[RuleEvaluationResult] = []

        for rule in self._approval_rules:
            result = RuleEvaluationResult(
                rule_description=rule.description,
                is_satisfied=rule.is_satisfied_by(application),
            )
            rule_results.append(result)

        all_rules_satisfied = all(r.is_satisfied for r in rule_results)
        requires_additional_review = self._additional_review_rule.is_satisfied_by(
            application
        )

        if not all_rules_satisfied:
            decision = UnderwritingDecision.REJECTED
        elif requires_additional_review:
            decision = UnderwritingDecision.ADDITIONAL_REVIEW_REQUIRED
        else:
            decision = UnderwritingDecision.APPROVED

        return UnderwritingResult(
            decision=decision,
            rule_results=tuple(rule_results),
            requires_additional_review=requires_additional_review,
        )
```

### 3.7 규칙 조합 및 사용 예시

```python
# === 기본 규칙 세트 구성 ===
approval_rules: list[Specification[LoanApplication]] = [
    MinimumCreditScoreRule(minimum_score=700),
    MaximumDTIRule(max_dti_percent=40.0),
    MinimumEmploymentDurationRule(minimum_years=1),
    NoDelinquencyHistoryRule(),
]

additional_review_rule = AdditionalReviewRequiredRule(income_multiple=5)

underwriting_service = LoanUnderwritingService(
    approval_rules=approval_rules,
    additional_review_rule=additional_review_rule,
)


# === 심사 실행 ===
application = LoanApplication(
    applicant_id="APP-001",
    credit_score=CreditScore(value=750),
    dti=DebtToIncomeRatio(total_debt=20_000_000, annual_income=60_000_000),
    employment_duration=EmploymentDuration(months=24),
    delinquency_status=DelinquencyStatus.NONE,
    requested_amount=Money(amount=200_000_000),
    annual_income=60_000_000,
)

result = underwriting_service.evaluate(application)
# result.decision -> UnderwritingDecision.APPROVED
# result.requires_additional_review -> False


# === 개별 규칙 단독 검증 ===
credit_rule = MinimumCreditScoreRule(minimum_score=700)
credit_rule.is_satisfied_by(application)  # True


# === 연산자로 규칙 조합 ===
# 신용 점수 700 이상 AND DTI 40% 이하
basic_eligibility = (
    MinimumCreditScoreRule(minimum_score=700)
    & MaximumDTIRule(max_dti_percent=40.0)
)
basic_eligibility.is_satisfied_by(application)  # True

# 신용 점수 800 이상이면 DTI 50%까지 허용 (우대 조건)
premium_eligibility = (
    MinimumCreditScoreRule(minimum_score=800)
    & MaximumDTIRule(max_dti_percent=50.0)
)

# 일반 조건 OR 우대 조건
flexible_eligibility = basic_eligibility | premium_eligibility
flexible_eligibility.is_satisfied_by(application)  # True


# === 새 규칙 추가 예시 -- 기존 코드 변경 없이 확장 ===
class MinimumAgeRule(Specification[LoanApplication]):
    """최소 연령 규칙 -- 새로 추가된 비즈니스 규칙"""

    def __init__(self, minimum_age: int = 19):
        self._minimum_age = minimum_age

    @property
    def description(self) -> str:
        return f"만 {self._minimum_age}세 이상이어야 한다"

    def is_satisfied_by(self, application: LoanApplication) -> bool:
        return application.age >= self._minimum_age  # LoanApplication에 age 필드 추가 필요

# 기존 규칙 목록에 추가하기만 하면 된다
approval_rules.append(MinimumAgeRule(minimum_age=19))
```

---

## 4. 설계 근거

### 4.1 Specification 패턴을 선택한 이유

대출 승인 규칙은 Specification 패턴의 **검증(Validation)** 용도에 정확히 해당한다. 이 패턴을 적용함으로써 다음을 달성한다.

- **개별 검증**: 각 규칙이 독립된 Specification 클래스이므로 단독으로 `is_satisfied_by`를 호출할 수 있다.
- **조합 가능**: `&`(AND), `|`(OR), `~`(NOT) 연산자로 규칙을 자유롭게 조합한다. 예를 들어 "신용 점수 800 이상이면 DTI 50%까지 허용"과 같은 우대 조건을 기존 규칙의 조합으로 표현할 수 있다.
- **유연한 확장**: 새 규칙을 추가할 때 `Specification[LoanApplication]`을 구현하는 클래스를 하나 만들고 규칙 목록에 추가하면 된다. 기존 코드를 수정할 필요가 없다(OCP).

### 4.2 값 객체로 원시 타입을 대체한 이유

- `CreditScore`, `DebtToIncomeRatio`, `EmploymentDuration` 등을 원시 타입(`int`, `float`) 대신 값 객체로 표현하여 유비쿼터스 언어를 코드에 반영했다.
- 각 값 객체가 자기 검증(`__post_init__`)을 수행하므로 유효하지 않은 값이 시스템에 유입되지 않는다.
- 판단 로직(`meets_minimum`, `is_within_limit`)을 값 객체 안에 두어 풍부한 도메인 모델을 유지한다.

### 4.3 도메인 서비스로 심사 엔진을 설계한 이유

심사 로직은 여러 규칙(Specification)의 평가와 종합 판정이라는 특성상 특정 엔티티 하나에 속하지 않는다. 따라서 상태 없는(stateless) 도메인 서비스(`LoanUnderwritingService`)로 구현했다. 응용 서비스가 이 도메인 서비스를 호출하고, 결과를 대출 신청 애그리거트에 전달하는 구조다.

### 4.4 심사 결과를 값 객체로 설계한 이유

`UnderwritingResult`는 불변 값 객체다. 심사 결과는 한번 결정되면 변경되지 않으며, 어떤 규칙이 충족/위반되었는지를 함께 기록하여 심사 이력을 투명하게 추적할 수 있다. 이는 금융 도메인에서 감사(audit) 요구사항에도 부합한다.

### 4.5 추가 심사 규칙을 분리한 이유

`AdditionalReviewRequiredRule`은 거절/승인을 결정하는 규칙이 아니라, 승인 이후 추가 검토가 필요한지를 판단하는 규칙이다. 성격이 다르므로 승인 규칙 목록(`approval_rules`)과 별도로 주입받아 심사 흐름에서의 역할을 명확히 구분했다.
