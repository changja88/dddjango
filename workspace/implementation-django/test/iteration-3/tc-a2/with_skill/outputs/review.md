# Payment Model Code Review

## Findings

### 1. Multi-table Inheritance

```
[Model Design -- Multi-table Inheritance] -- Payment를 concrete 모델로 두고 CardPayment, BankTransfer, VirtualAccountPayment가 이를 상속하는 구조는 multi-table inheritance다. 각 자식 모델마다 별도 테이블이 생성되고, 조회 시 암묵적 OneToOneField를 통한 JOIN이 발생하여 성능이 저하된다. 대부분의 경우 Abstract Base Class + 명시적 ForeignKey 또는 TextChoices를 이용한 단일 테이블 설계가 더 낫다. 결제 수단별로 필드가 크게 다르다면 ABC + 별도 테이블로 분리하고, 공통 조회가 필요하면 결제 타입을 TextChoices로 관리하는 단일 모델이 적합하다.
```

### 2. FloatField for Money

```
[Model Design -- Field Selection] -- amount에 FloatField를 사용하고 있다. 부동소수점 연산은 금액 계산에서 정밀도 오류를 일으킨다 (예: 0.1 + 0.2 != 0.3). 금액 필드에는 반드시 DecimalField(max_digits=..., decimal_places=2)를 사용해야 한다.
```

### 3. N+1 Query in View

```
[QuerySet -- N+1 Problem] -- PaymentListView에서 Payment.objects.filter(user=request.user)로 조회한 뒤, 루프 안에서 p.cardpayment에 접근하고 있다. 이는 결제 건마다 cardpayment 테이블에 추가 쿼리를 발생시키는 전형적인 N+1 문제다. select_related("cardpayment")를 사용하여 JOIN으로 한 번에 가져와야 한다. 또한 BankTransfer, VirtualAccountPayment에 대한 접근이 필요하다면 해당 역참조도 함께 select_related해야 한다.
```

### 4. Multi-table Inheritance Downcasting Pattern

```
[Model Design -- Multi-table Inheritance] -- p.cardpayment로 자식 모델에 접근하는 패턴은 multi-table inheritance의 대표적인 안티패턴이다. try/except로 CardPayment.DoesNotExist를 잡아야 하고, BankTransfer와 VirtualAccountPayment에 대한 처리가 누락되어 있다. 결제 수단 유형이 추가될 때마다 뷰 코드를 수정해야 하므로 OCP(Open-Closed Principle)를 위반한다. 단일 테이블 + TextChoices 또는 각 모델에 다형적 메서드를 정의하는 방식이 더 낫다.
```

### 5. Fat View with Business Logic

```
[View -- Fat Model, Thin View] -- PaymentListView의 get() 메서드에서 결제 데이터의 직렬화 로직(카드 번호 마스킹, 딕셔너리 구성)을 직접 수행하고 있다. 이 로직은 모델의 커스텀 메서드나 별도의 Serializer로 분리해야 한다. 뷰는 요청 흐름 제어에만 집중해야 한다.
```

### 6. Missing Model Validation

```
[Model Design -- Validation] -- Payment 모델에 amount에 대한 유효성 검증이 없다. 음수 금액이나 0원 결제가 가능한 상태다. clean() 메서드로 Python 레벨 검증을 수행하고, CheckConstraint로 DB 레벨 제약도 함께 걸어야 한다 (이중 방어).
```

### 7. Missing `__str__` Method

```
[Design Style -- Model Coding Style] -- 모든 모델에 __str__() 메서드가 없다. Django 코딩 스타일에 따르면 필드 -> Manager -> Meta -> __str__ -> save()/delete() -> custom methods 순서로 정의하며, __str__은 admin과 디버깅에서 필수적이다.
```

### 8. Card Number Storage

```
[Security] -- CardPayment 모델에 card_number를 CharField(max_length=16)로 평문 저장하고 있다. PCI DSS 규정상 카드 번호 전체를 평문으로 저장해서는 안 된다. 마지막 4자리만 별도 필드로 저장하거나, 토큰화 방식을 사용해야 한다.
```

### 9. Missing Authentication Check

```
[View -- Auth] -- PaymentListView에서 request.user를 사용하지만 LoginRequiredMixin이 적용되지 않았다. 미인증 사용자가 접근하면 AnonymousUser로 필터링되어 예기치 않은 결과가 반환될 수 있다. LoginRequiredMixin을 상속하거나, Django 5.1의 LoginRequiredMiddleware를 활용해야 한다.
```

### 10. Django 5.x Features Not Used

```
[Django 5.x] -- paid_at = DateTimeField(auto_now_add=True) 대신 Django 5.0의 db_default=Now()를 사용하면 bulk_create 등에서도 DB 레벨에서 기본값이 올바르게 적용된다. VirtualAccountPayment의 expires_at도 db_default와 함께 CheckConstraint로 현재 시각 이후인지 검증할 수 있다.
```

## Review Checklist

- [ ] Project structure: settings split, apps isolated, no circular deps -- **N/A** (코드 조각만 제공됨)
- [x] Model field ordering: fields -> managers -> Meta -> __str__ -> save -> custom methods -- **위반: __str__ 누락**
- [ ] Boolean flag proliferation -- **해당 없음**
- [x] Missing select_related/prefetch_related on FK/M2M access in loops -- **위반: Finding #3**
- [x] N+1 queries in views or templates -- **위반: Finding #3**
- [ ] save() without update_fields -- **해당 없음** (save 호출 없음)
- [ ] Signals used for same-app logic -- **해당 없음**
- [ ] fields = "__all__" or exclude in ModelForm/Serializer -- **해당 없음**
- [x] Multi-table inheritance where Abstract Base Class suffices -- **위반: Finding #1**
- [ ] Raw SQL with string interpolation -- **해당 없음**
- [ ] Missing CSRF protection or @csrf_exempt -- **해당 없음**
- [ ] CBV with 4+ Mixins or deeply customized generic view -- **해당 없음**
- [x] Fat views with business logic that belongs in model/service -- **위반: Finding #5**
- [ ] Missing assertNumQueries in performance-critical test paths -- **N/A** (테스트 코드 없음)
- [x] Django 5.x features not used where applicable -- **위반: Finding #10**
