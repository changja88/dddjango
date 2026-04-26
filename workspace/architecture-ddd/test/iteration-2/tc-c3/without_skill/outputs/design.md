# 대출 심사 시스템 - 대출 승인 규칙 설계

## 1. 설계 방향

대출 승인 규칙을 **Specification 패턴**으로 설계한다. 각 규칙을 독립적인 Specification 객체로 캡슐화하여 개별 검증과 조합을 모두 지원한다. 새로운 규칙 추가 시 기존 코드를 수정하지 않고 새 Specification 클래스만 추가하면 된다.

---

## 2. 도메인 모델

### 2.1 대출 신청 (Value Object)

```python
@dataclass(frozen=True)
class LoanApplication:
    applicant_name: str
    credit_score: int
    annual_income: int
    total_debt: int
    employment_months: int
    has_delinquency_history: bool
    requested_amount: int

    @property
    def dti_ratio(self) -> float:
        if self.annual_income == 0:
            return float('inf')
        return (self.total_debt / self.annual_income) * 100

    @property
    def income_multiplier(self) -> float:
        if self.annual_income == 0:
            return float('inf')
        return self.requested_amount / self.annual_income
```

### 2.2 심사 결과 (Value Object)

```python
class ApprovalStatus(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    ADDITIONAL_REVIEW = "additional_review"

@dataclass(frozen=True)
class RuleResult:
    rule_name: str
    passed: bool
    reason: str

@dataclass(frozen=True)
class ApprovalResult:
    status: ApprovalStatus
    rule_results: list[RuleResult]
    requires_additional_review: bool

    @property
    def failed_rules(self) -> list[RuleResult]:
        return [r for r in self.rule_results if not r.passed]
```

---

## 3. Specification 패턴 구조

### 3.1 기본 인터페이스

```python
class LoanSpecification(ABC):
    @abstractmethod
    def is_satisfied_by(self, application: LoanApplication) -> RuleResult:
        ...

    def and_spec(self, other: "LoanSpecification") -> "AndSpecification":
        return AndSpecification(self, other)

    def or_spec(self, other: "LoanSpecification") -> "OrSpecification":
        return OrSpecification(self, other)
```

### 3.2 조합 Specification

```python
class AndSpecification(LoanSpecification):
    def __init__(self, left: LoanSpecification, right: LoanSpecification):
        self._left = left
        self._right = right

    def is_satisfied_by(self, application: LoanApplication) -> RuleResult:
        left_result = self._left.is_satisfied_by(application)
        if not left_result.passed:
            return left_result
        return self._right.is_satisfied_by(application)


class OrSpecification(LoanSpecification):
    def __init__(self, left: LoanSpecification, right: LoanSpecification):
        self._left = left
        self._right = right

    def is_satisfied_by(self, application: LoanApplication) -> RuleResult:
        left_result = self._left.is_satisfied_by(application)
        if left_result.passed:
            return left_result
        return self._right.is_satisfied_by(application)
```

---

## 4. 개별 규칙 Specification

### 4.1 신용 점수 규칙

```python
class CreditScoreSpecification(LoanSpecification):
    def __init__(self, minimum_score: int = 700):
        self._minimum_score = minimum_score

    def is_satisfied_by(self, application: LoanApplication) -> RuleResult:
        passed = application.credit_score >= self._minimum_score
        return RuleResult(
            rule_name="신용점수 검증",
            passed=passed,
            reason=f"신용점수 {application.credit_score}점 "
                   f"(기준: {self._minimum_score}점 이상)"
                   if passed else
                   f"신용점수 {application.credit_score}점으로 "
                   f"기준 {self._minimum_score}점 미달",
        )
```

### 4.2 DTI 비율 규칙

```python
class DtiRatioSpecification(LoanSpecification):
    def __init__(self, maximum_ratio: float = 40.0):
        self._maximum_ratio = maximum_ratio

    def is_satisfied_by(self, application: LoanApplication) -> RuleResult:
        dti = application.dti_ratio
        passed = dti <= self._maximum_ratio
        return RuleResult(
            rule_name="DTI 비율 검증",
            passed=passed,
            reason=f"DTI {dti:.1f}% (기준: {self._maximum_ratio}% 이하)"
                   if passed else
                   f"DTI {dti:.1f}%로 기준 {self._maximum_ratio}% 초과",
        )
```

### 4.3 재직 기간 규칙

```python
class EmploymentPeriodSpecification(LoanSpecification):
    def __init__(self, minimum_months: int = 12):
        self._minimum_months = minimum_months

    def is_satisfied_by(self, application: LoanApplication) -> RuleResult:
        passed = application.employment_months >= self._minimum_months
        return RuleResult(
            rule_name="재직기간 검증",
            passed=passed,
            reason=f"재직기간 {application.employment_months}개월 "
                   f"(기준: {self._minimum_months}개월 이상)"
                   if passed else
                   f"재직기간 {application.employment_months}개월로 "
                   f"기준 {self._minimum_months}개월 미달",
        )
```

### 4.4 연체 이력 규칙

```python
class NoDelinquencySpecification(LoanSpecification):
    def is_satisfied_by(self, application: LoanApplication) -> RuleResult:
        passed = not application.has_delinquency_history
        return RuleResult(
            rule_name="연체이력 검증",
            passed=passed,
            reason="연체 이력 없음" if passed else "연체 이력 존재",
        )
```

### 4.5 추가 심사 판별 규칙

```python
class AdditionalReviewSpecification(LoanSpecification):
    def __init__(self, income_multiplier_limit: float = 5.0):
        self._income_multiplier_limit = income_multiplier_limit

    def is_satisfied_by(self, application: LoanApplication) -> RuleResult:
        needs_review = application.income_multiplier > self._income_multiplier_limit
        return RuleResult(
            rule_name="추가심사 판별",
            passed=not needs_review,
            reason=f"신청금액이 연소득의 "
                   f"{application.income_multiplier:.1f}배 "
                   f"(기준: {self._income_multiplier_limit}배 이하)"
                   if not needs_review else
                   f"신청금액이 연소득의 "
                   f"{application.income_multiplier:.1f}배로 "
                   f"추가 심사 필요",
        )
```

---

## 5. 심사 엔진

```python
class LoanApprovalEngine:
    def __init__(
        self,
        mandatory_specs: list[LoanSpecification],
        additional_review_spec: LoanSpecification,
    ):
        self._mandatory_specs = mandatory_specs
        self._additional_review_spec = additional_review_spec

    def evaluate(self, application: LoanApplication) -> ApprovalResult:
        results: list[RuleResult] = []

        # 필수 규칙 전체 평가 (하나라도 실패하면 거절)
        for spec in self._mandatory_specs:
            result = spec.is_satisfied_by(application)
            results.append(result)

        # 추가 심사 판별
        review_result = self._additional_review_spec.is_satisfied_by(application)
        results.append(review_result)

        failed = [r for r in results if not r.passed and r.rule_name != "추가심사 판별"]
        needs_additional = not review_result.passed

        if failed:
            status = ApprovalStatus.REJECTED
        elif needs_additional:
            status = ApprovalStatus.ADDITIONAL_REVIEW
        else:
            status = ApprovalStatus.APPROVED

        return ApprovalResult(
            status=status,
            rule_results=results,
            requires_additional_review=needs_additional,
        )
```

---

## 6. 조립 및 사용 예시

### 6.1 기본 구성

```python
def create_default_engine() -> LoanApprovalEngine:
    mandatory = [
        CreditScoreSpecification(minimum_score=700),
        DtiRatioSpecification(maximum_ratio=40.0),
        EmploymentPeriodSpecification(minimum_months=12),
        NoDelinquencySpecification(),
    ]
    additional_review = AdditionalReviewSpecification(income_multiplier_limit=5.0)

    return LoanApprovalEngine(mandatory, additional_review)
```

### 6.2 개별 규칙 단독 사용

```python
application = LoanApplication(
    applicant_name="홍길동",
    credit_score=750,
    annual_income=50_000_000,
    total_debt=15_000_000,
    employment_months=24,
    has_delinquency_history=False,
    requested_amount=200_000_000,
)

# 신용점수만 검증
credit_spec = CreditScoreSpecification(minimum_score=700)
result = credit_spec.is_satisfied_by(application)
# -> RuleResult(rule_name="신용점수 검증", passed=True, reason="신용점수 750점 (기준: 700점 이상)")
```

### 6.3 규칙 조합 사용

```python
# 신용점수 AND DTI 동시 충족 검증
combined = CreditScoreSpecification(700).and_spec(DtiRatioSpecification(40.0))
result = combined.is_satisfied_by(application)

# 신용점수 800 이상이면 DTI 50%까지 허용 (OR 조합)
relaxed = (
    CreditScoreSpecification(800)
    .and_spec(DtiRatioSpecification(50.0))
    .or_spec(
        CreditScoreSpecification(700)
        .and_spec(DtiRatioSpecification(40.0))
    )
)
```

### 6.4 전체 심사 실행

```python
engine = create_default_engine()
approval = engine.evaluate(application)

print(f"심사 결과: {approval.status.value}")
print(f"추가 심사 필요: {approval.requires_additional_review}")
for r in approval.rule_results:
    mark = "PASS" if r.passed else "FAIL"
    print(f"  [{mark}] {r.rule_name}: {r.reason}")
```

출력:
```
심사 결과: additional_review
추가 심사 필요: True
  [PASS] 신용점수 검증: 신용점수 750점 (기준: 700점 이상)
  [PASS] DTI 비율 검증: DTI 30.0% (기준: 40.0% 이하)
  [PASS] 재직기간 검증: 재직기간 24개월 (기준: 12개월 이상)
  [PASS] 연체이력 검증: 연체 이력 없음
  [FAIL] 추가심사 판별: 신청금액이 연소득의 4.0배로 추가 심사 필요
```

---

## 7. 새 규칙 추가 예시

담보 비율 규칙을 추가하는 경우, 기존 코드를 수정하지 않고 새 클래스만 작성한다.

```python
class CollateralRatioSpecification(LoanSpecification):
    def __init__(self, minimum_ratio: float = 120.0):
        self._minimum_ratio = minimum_ratio

    def is_satisfied_by(self, application: LoanApplication) -> RuleResult:
        # LoanApplication에 collateral_value 필드가 추가되었다고 가정
        ratio = (application.collateral_value / application.requested_amount) * 100
        passed = ratio >= self._minimum_ratio
        return RuleResult(
            rule_name="담보비율 검증",
            passed=passed,
            reason=f"담보비율 {ratio:.1f}% (기준: {self._minimum_ratio}% 이상)"
                   if passed else
                   f"담보비율 {ratio:.1f}%로 기준 {self._minimum_ratio}% 미달",
        )
```

엔진 구성 시 리스트에 추가하기만 하면 된다.

```python
mandatory = [
    CreditScoreSpecification(700),
    DtiRatioSpecification(40.0),
    EmploymentPeriodSpecification(12),
    NoDelinquencySpecification(),
    CollateralRatioSpecification(120.0),  # 새 규칙 추가
]
```

---

## 8. 설계 특성 요약

| 관점 | 설계 결정 |
|---|---|
| **패턴** | Specification 패턴 |
| **개별 검증** | 각 Specification을 독립적으로 `is_satisfied_by()` 호출 |
| **조합 검증** | `and_spec()`, `or_spec()`으로 체이닝 |
| **전체 심사** | `LoanApprovalEngine`이 규칙 리스트를 순회하며 평가 |
| **규칙 추가** | `LoanSpecification`을 구현한 새 클래스 작성 후 리스트에 등록 |
| **임계값 변경** | 각 Specification의 생성자 파라미터로 조정 |
| **심사 결과** | 승인/거절/추가심사 3단계, 개별 규칙별 사유 포함 |
