# Payment 모델 코드 리뷰

## 1. 금액 필드에 FloatField 사용 (심각도: 높음)

```python
amount = models.FloatField()
```

**문제:** `FloatField`는 부동소수점 연산의 정밀도 문제로 인해 금액 계산 시 오차가 발생한다. 예를 들어 `0.1 + 0.2 = 0.30000000000000004`와 같은 결과가 나올 수 있다. 결제 금액처럼 정확성이 필수인 도메인에서 이는 실제 금전적 오류로 이어진다.

**개선:**
```python
amount = models.DecimalField(max_digits=12, decimal_places=2)
```

---

## 2. Multi-Table Inheritance로 인한 성능 문제 (심각도: 높음)

```python
class CardPayment(Payment): ...
class BankTransfer(Payment): ...
class VirtualAccountPayment(Payment): ...
```

**문제:** Django의 Multi-Table Inheritance(MTI)는 자식 클래스마다 별도의 테이블을 생성하고, 조회 시 JOIN이 필요하다. `Payment.objects.filter(user=request.user)`로 조회하면 부모 테이블만 조회되어 자식 타입 정보에 접근할 수 없고, 자식 데이터에 접근하려면 추가 쿼리가 발생한다.

**개선 방안:**
- 결제 수단별 고유 필드가 적다면 **단일 테이블 + `type` 필드** 방식 고려
- 또는 `django-polymorphic` 라이브러리 사용으로 다형성 쿼리를 효율적으로 처리
- 혹은 결제 수단 상세 정보를 별도 모델로 분리하고 `GenericForeignKey` 또는 `OneToOneField`로 연결

---

## 3. N+1 쿼리 문제 (심각도: 높음)

```python
payments = Payment.objects.filter(user=request.user)
for p in payments:
    try:
        data['card'] = p.cardpayment.card_number[-4:]
    except CardPayment.DoesNotExist:
        pass
```

**문제:** 루프 안에서 `p.cardpayment`에 접근할 때마다 추가 SQL 쿼리가 실행된다. 결제 건수가 N개면 최소 N+1개의 쿼리가 발생한다.

**개선:**
```python
payments = Payment.objects.filter(user=request.user).select_related('cardpayment')
```

---

## 4. 카드번호 평문 저장 (심각도: 높음)

```python
card_number = models.CharField(max_length=16)
```

**문제:** 카드번호 전체(16자리)를 평문으로 DB에 저장하는 것은 PCI-DSS 규정 위반이다. 카드 정보 유출 시 법적 책임과 막대한 과징금이 발생할 수 있다.

**개선:**
- 카드번호 전체를 저장하지 말 것. 뒤 4자리(`last_four_digits`)만 저장
- 결제 처리는 PG사(결제 대행사)의 토큰 기반 방식을 사용하고, 토큰만 저장
- 불가피하게 저장해야 한다면 암호화 필수

---

## 5. 계좌번호 평문 저장 (심각도: 중간)

```python
account_number = models.CharField(max_length=30)
```

**문제:** 은행 계좌번호 역시 민감한 개인정보다. 평문 저장은 개인정보보호법 위반 소지가 있다.

**개선:** 마스킹 처리된 형태로 저장하거나, 암호화하여 저장해야 한다.

---

## 6. BankTransfer, VirtualAccountPayment 조회 누락 (심각도: 중간)

```python
try:
    data['card'] = p.cardpayment.card_number[-4:]
except CardPayment.DoesNotExist:
    pass
```

**문제:** `CardPayment`만 확인하고 `BankTransfer`와 `VirtualAccountPayment`는 완전히 무시한다. 사용자에게 결제 수단 정보를 전혀 보여줄 수 없다.

**개선:** 모든 결제 타입에 대한 처리가 필요하다. 결제 타입을 구분하는 필드를 두거나, 각 자식 모델에 `get_display_info()` 같은 공통 메서드를 정의하여 다형적으로 처리해야 한다.

---

## 7. 인증/권한 검사 없음 (심각도: 중간)

```python
class PaymentListView(View):
    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
```

**문제:** `View`를 직접 상속하면서 인증 확인이 없다. `request.user`가 `AnonymousUser`일 경우에도 쿼리가 실행된다(에러 또는 빈 결과).

**개선:**
```python
from django.contrib.auth.mixins import LoginRequiredMixin

class PaymentListView(LoginRequiredMixin, View):
    ...
```

---

## 8. installment_months 유효성 검증 부재 (심각도: 낮음)

```python
installment_months = models.IntegerField(default=1)
```

**문제:** 0이나 음수, 또는 비현실적으로 큰 값(예: 999)이 들어올 수 있다. 일반적으로 할부 개월은 1~12개월이다.

**개선:**
```python
from django.core.validators import MinValueValidator, MaxValueValidator

installment_months = models.IntegerField(
    default=1,
    validators=[MinValueValidator(1), MaxValueValidator(12)]
)
```

---

## 9. paid_at에 auto_now_add 사용 (심각도: 낮음)

```python
paid_at = models.DateTimeField(auto_now_add=True)
```

**문제:** `auto_now_add=True`는 레코드 생성 시점을 기록한다. 하지만 결제 시점과 DB 레코드 생성 시점이 반드시 같지는 않다(PG사 응답 지연, 비동기 처리 등). 또한 이 필드는 `editable=False`가 되어 관리자 페이지에서도 수정할 수 없다.

**개선:**
```python
paid_at = models.DateTimeField()  # 결제 완료 시점을 명시적으로 설정
```

---

## 10. 결제 상태(status) 필드 부재 (심각도: 중간)

**문제:** 결제에는 대기, 완료, 취소, 환불 등 다양한 상태가 존재하지만 이를 관리할 필드가 없다. 현재 구조로는 결제 취소나 환불 처리를 할 수 없다.

**개선:**
```python
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        COMPLETED = 'completed', '완료'
        CANCELLED = 'cancelled', '취소'
        REFUNDED = 'refunded', '환불'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
```

---

## 요약

| 항목 | 심각도 | 핵심 |
|------|--------|------|
| FloatField로 금액 처리 | 높음 | DecimalField 사용 필수 |
| Multi-Table Inheritance | 높음 | JOIN 비용, 다형성 쿼리 비효율 |
| N+1 쿼리 | 높음 | select_related 적용 |
| 카드번호 평문 저장 | 높음 | PCI-DSS 위반, 토큰 방식 전환 |
| 계좌번호 평문 저장 | 중간 | 암호화 또는 마스킹 필요 |
| 일부 결제 타입 조회 누락 | 중간 | 모든 결제 타입 처리 필요 |
| 인증 검사 없음 | 중간 | LoginRequiredMixin 적용 |
| 결제 상태 필드 부재 | 중간 | status 필드 추가 |
| installment_months 검증 없음 | 낮음 | validator 추가 |
| auto_now_add 사용 | 낮음 | 명시적 시점 기록 권장 |
