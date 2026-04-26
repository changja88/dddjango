# /refactor 커맨드 실행 결과

## 커맨드 메타데이터

- **커맨드**: `/refactor`
- **입력**: Django View 코드 (OrderView)
- **모드**: Refactoring

---

## 1단계: 기본 스킬 로드

| # | 스킬 | 상태 |
|---|------|------|
| 1 | `implementation-cleancode/SKILL.md` | 로드 완료 |
| 2 | `implementation-python/SKILL.md` | 로드 완료 |
| 3 | `implementation-django/SKILL.md` | 로드 완료 |

---

## 2단계: 코드 분석 및 추가 스킬 선택

### 코드 특성 분석

| 코드 특성 | 해당 여부 | 판단 근거 |
|----------|----------|----------|
| Django Ninja Schema/Router/API 코드 | X | Django Ninja 사용 없음 -- 순수 Django View + JsonResponse |
| Django 템플릿, 정적 파일, TemplateView | X | JsonResponse만 사용, 템플릿 없음 |
| 테스트 코드 (pytest, TestCase) | X | 테스트 코드 아님 |
| 헥사고날/CQRS/이벤트소싱 구조 | X | 해당 패턴 없음 |
| DDD 패턴 (Aggregate, Repository, VO) | X | DDD 패턴 미사용 |
| DB 스키마/인덱스/쿼리 최적화 이슈 | X | 스키마 정의 코드 아님 (쿼리 비효율은 있으나 DB 설계 이슈는 아님) |
| **REST API 설계 이슈 (URL, 상태코드)** | **O** | JsonResponse로 REST API를 구현하고 있으며, 에러 처리/상태 코드 개선이 필요 |

### 추가 로드 스킬

| # | 스킬 | 상태 |
|---|------|------|
| 4 | `architecture-api/SKILL.md` | 로드 완료 |

---

## 3단계: Refactoring 모드 실행

### 참조 파일 로드 내역

변경 사항을 제시하기 전에 적용한 각 패턴의 참조 파일을 읽었다:

- `implementation-cleancode/references/functions.md` -- 함수 설계, 한 가지만 해라, 추상화 수준
- `implementation-cleancode/references/error-handling.md` -- 예외 사용, 보호절, 방어적 프로그래밍
- `implementation-cleancode/references/refactoring.md` -- Feature Envy, Extract Method, Fat View
- `implementation-python/references/type-hints.md` -- 타입 어노테이션, X | None 구문
- `implementation-python/references/data-modeling.md` -- dataclass, Enum, frozen=True
- `implementation-django/references/views.md` -- Fat Model Thin View, get_object_or_404
- `implementation-django/references/service-layer.md` -- 서비스 레이어 패턴, entity_action 네이밍
- `implementation-django/references/model-design.md` -- TextChoices, 모델 메서드 캡슐화
- `architecture-api/references/status-codes-errors.md` -- RFC 9457, 404 처리

---

### 원본 코드

```python
class OrderView(View):
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        items = OrderItem.objects.filter(order=order)
        total = sum(i.price * i.qty for i in items)
        return JsonResponse({
            'id': order.id,
            'status': order.status,
            'items': [{'name': i.name, 'price': i.price, 'qty': i.qty} for i in items],
            'total': total
        })

    def post(self, request):
        data = json.loads(request.body)
        order = Order.objects.create(user=request.user, status='pending')
        for item in data['items']:
            OrderItem.objects.create(order=order, **item)
        return JsonResponse({'id': order.id}, status=201)
```

---

### 변경 사항

#### 변경 1: 존재하지 않는 주문 접근 시 예외 처리 누락

```
[Before]
order = Order.objects.get(pk=pk)

[After]
order = get_object_or_404(Order, pk=pk)

[Reason] Django 뷰 컨벤션 + 에러 처리 -- Order.objects.get()은 존재하지 않는
pk에 대해 DoesNotExist 예외를 발생시키며, 이는 500 에러로 변환된다.
get_object_or_404는 적절한 404 응답을 반환하여 REST 원칙(존재하지 않는 리소스는 404)을
준수하고, 클라이언트에게 의미 있는 에러를 제공한다.
```

#### 변경 2: Fat View -- 비즈니스 로직(총액 계산)이 뷰에 위치

```
[Before]
items = OrderItem.objects.filter(order=order)
total = sum(i.price * i.qty for i in items)

[After]
# Order 모델에 메서드 추가
class Order(models.Model):
    ...
    def calculate_total(self) -> Decimal:
        """주문의 총액을 계산한다."""
        return sum(
            item.price * item.qty
            for item in self.items.all()
        )

[Reason] Fat Model, Thin View (implementation-django) + 한 가지만 해라 (implementation-cleancode)
-- 총액 계산은 주문 도메인의 비즈니스 로직이다. 뷰에 두면 다른 뷰나 서비스에서
같은 로직을 중복해야 하고(Feature Envy 스멜), 테스트도 HTTP 요청을 통해서만 가능하다.
모델 메서드로 추출하면 단일 권위 있는 소스가 되고, 단위 테스트가 쉬워진다.
```

#### 변경 3: 직접 OrderItem.objects.filter() 대신 역방향 관계(related_name) 활용

```
[Before]
items = OrderItem.objects.filter(order=order)

[After]
# related_name='items'가 설정되어 있다고 가정
order.items.all()

[Reason] Django QuerySet 컨벤션 -- 역방향 관계를 통한 접근이 Django의 관용적 패턴이다.
order 객체를 통해 접근하면 의도가 명확해지고, prefetch_related와의 호환성도 좋아진다.
```

#### 변경 4: 직렬화 로직이 뷰에 산재 -- 응답 구성을 전용 메서드로 추출

```
[Before]
return JsonResponse({
    'id': order.id,
    'status': order.status,
    'items': [{'name': i.name, 'price': i.price, 'qty': i.qty} for i in items],
    'total': total
})

[After]
# Order 모델에 직렬화 메서드 추가
def to_detail_dict(self) -> dict:
    """주문 상세 정보를 딕셔너리로 변환한다."""
    items = self.items.all()
    return {
        "id": self.id,
        "status": self.status,
        "items": [
            {"name": item.name, "price": item.price, "qty": item.qty}
            for item in items
        ],
        "total": self.calculate_total(),
    }

[Reason] 함수는 하나의 추상화 수준에서 하나의 일만 한다 (implementation-cleancode)
+ Feature Envy 해소 (refactoring) -- 직렬화 로직이 Order의 내부 데이터에
지나치게 의존하고 있다(Feature Envy). 모델 메서드로 이동시키면 뷰는 "요청 처리"
라는 본연의 역할에 집중하고, 직렬화 로직은 모델 가까이에서 유지보수된다.
```

#### 변경 5: 매직 문자열 'pending' 하드코딩

```
[Before]
order = Order.objects.create(user=request.user, status='pending')

[After]
# Order 모델에 TextChoices 정의
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
    )

# 뷰에서 사용
order = Order.objects.create(user=request.user, status=Order.Status.PENDING)

[Reason] 매직 문자열 제거 (implementation-cleancode) + TextChoices 사용 (implementation-django)
-- 문자열 리터럴 'pending'은 타입 체커가 검증할 수 없고, 오타가 런타임에서만
발견된다. TextChoices는 유효한 상태 값을 열거하여 잘못된 상태를 컴파일 타임에
방지하고, 코드 검색과 자동 완성을 지원한다.
```

#### 변경 6: 주문 생성 로직이 뷰에 위치 -- 서비스 함수로 추출

```
[Before]
def post(self, request):
    data = json.loads(request.body)
    order = Order.objects.create(user=request.user, status='pending')
    for item in data['items']:
        OrderItem.objects.create(order=order, **item)
    return JsonResponse({'id': order.id}, status=201)

[After]
# services.py
from django.db import transaction

def order_create(*, user: User, items: list[dict]) -> Order:
    """주문과 주문 항목을 원자적으로 생성한다."""
    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            status=Order.Status.PENDING,
        )
        OrderItem.objects.bulk_create([
            OrderItem(order=order, **item_data)
            for item_data in items
        ])
    return order

[Reason] 서비스 레이어 패턴 (implementation-django) + 트랜잭션 원자성 + 벌크 작업
-- 원본 코드는 세 가지 문제를 가진다:
(1) 뷰에 비즈니스 로직이 있어 재사용 불가 (Fat View).
(2) Order와 OrderItem 생성이 트랜잭션으로 묶이지 않아, 중간에 실패하면
    아이템 없는 주문이 남을 수 있다.
(3) 루프 내 개별 create()는 N번의 INSERT 쿼리를 발생시킨다.
    bulk_create로 단일 쿼리로 통합한다.
서비스 함수는 entity_action 네이밍(order_create)을 따르고, 키워드 전용 인수(*)로
호출 의도를 명확히 한다.
```

#### 변경 7: json.loads(request.body) 검증 없이 직접 사용

```
[Before]
data = json.loads(request.body)
for item in data['items']:
    OrderItem.objects.create(order=order, **item)

[After]
def post(self, request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON in request body"},
            status=400,
        )
    if "items" not in data or not isinstance(data["items"], list):
        return JsonResponse(
            {"error": "Field 'items' is required and must be a list"},
            status=400,
        )

[Reason] 방어적 프로그래밍 + 신뢰 경계에서 검증 (implementation-cleancode)
+ 400 Bad Request (architecture-api) -- 외부 입력은 신뢰 경계에서 반드시 검증해야
한다. 잘못된 JSON이나 누락된 필드에 대해 500 대신 의미 있는 400 응답을 반환한다.
원본 코드는 KeyError가 500으로 변환되어 클라이언트가 문제를 진단할 수 없다.
```

#### 변경 8: 타입 힌트 누락

```
[Before]
def get(self, request, pk):
def post(self, request):

[After]
def get(self, request: HttpRequest, pk: int) -> JsonResponse:
def post(self, request: HttpRequest) -> JsonResponse:

[Reason] 타입 힌트 필수 (implementation-python) -- 모든 공개 함수와 메서드에
타입 어노테이션을 작성한다. 타입 힌트는 코드를 읽는 사람과 타입 체커에게
계약을 전달하며, 런타임 전에 버그를 발견할 수 있게 한다.
```

---

### 전체 리팩토링된 코드

#### `models.py`

```python
from __future__ import annotations

from decimal import Decimal

from django.db import models


class Order(models.Model):
    """주문."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
    )

    def calculate_total(self) -> Decimal:
        """주문의 총액을 계산한다."""
        return sum(
            item.price * item.qty
            for item in self.items.all()
        )

    def to_detail_dict(self) -> dict:
        """주문 상세 정보를 딕셔너리로 변환한다."""
        items = self.items.all()
        return {
            "id": self.id,
            "status": self.status,
            "items": [
                {"name": item.name, "price": item.price, "qty": item.qty}
                for item in items
            ],
            "total": self.calculate_total(),
        }

    def __str__(self) -> str:
        return f"Order #{self.pk} ({self.status})"


class OrderItem(models.Model):
    """주문 항목."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.name} x{self.qty}"
```

#### `services.py`

```python
from __future__ import annotations

from django.contrib.auth.models import User
from django.db import transaction

from .models import Order, OrderItem


def order_create(*, user: User, items: list[dict]) -> Order:
    """주문과 주문 항목을 원자적으로 생성한다."""
    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            status=Order.Status.PENDING,
        )
        OrderItem.objects.bulk_create([
            OrderItem(order=order, **item_data)
            for item_data in items
        ])
    return order
```

#### `views.py`

```python
from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from .models import Order
from .services import order_create


class OrderView(View):
    """주문 조회 및 생성 API."""

    def get(self, request: HttpRequest, pk: int) -> JsonResponse:
        """단일 주문의 상세 정보를 반환한다."""
        order = get_object_or_404(Order, pk=pk)
        return JsonResponse(order.to_detail_dict())

    def post(self, request: HttpRequest) -> JsonResponse:
        """새 주문을 생성한다."""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON in request body"},
                status=400,
            )

        if "items" not in data or not isinstance(data["items"], list):
            return JsonResponse(
                {"error": "Field 'items' is required and must be a list"},
                status=400,
            )

        order = order_create(user=request.user, items=data["items"])
        return JsonResponse({"id": order.id}, status=201)
```

---

### 적용된 스킬별 체크리스트 검증

#### implementation-cleancode (Refactoring 모드)

- [x] 에러 코드 또는 dict 반환 -> 도메인 예외로 대체: `get_object_or_404` 적용
- [ ] 불변이어야 할 가변 데이터 -> frozen 값 객체로 변환: 해당 없음
- [ ] 타입 기반 반복 조건문 -> Strategy 또는 Polymorphism 적용: 해당 없음
- [ ] 산재된 None 검사 -> Null Object 도입: 해당 없음
- [ ] God Class -> 변경 빈도에 따라 분해: 해당 없음
- [ ] 중첩된 if문 -> 가드 절로 평탄화: 해당 없음 (중첩 없음)
- [x] 숨겨진 부수 효과 -> 별도의 커맨드로 추출: 서비스 함수로 분리
- [ ] 테스트 불가능한 의존성 -> Protocol을 통해 주입: 해당 없음
- [x] 매직 넘버 -> 이름 있는 상수: `'pending'` -> `Order.Status.PENDING`
- [x] 중복된 지식 -> 단일 권위 있는 소스: `calculate_total()` 모델 메서드로 통합
- [x] 관련 스킬 참조 포함

#### implementation-python (Refactoring 모드)

- [ ] 레거시 `Optional[X]` / `Union[X, Y]`: 해당 없음
- [ ] `typing.List` / `typing.Dict`: 해당 없음
- [ ] pydantic v1 API: 해당 없음
- [ ] 구조화된 데이터를 위한 일반 dict -> `@dataclass`: 해당 없음 (Django 모델이 적합)
- [ ] 단일 메서드의 ABC -> Protocol: 해당 없음
- [ ] 수동 리소스 정리: 해당 없음
- [ ] eager 리스트 -> 제너레이터: 해당 없음 (queryset은 이미 lazy)
- [x] 매직 문자열/정수 -> Enum: `TextChoices` 적용
- [ ] 문자열 연결 -> f-strings: 해당 없음
- [ ] isinstance 체인 -> match/case: 해당 없음
- [x] 누락된 어노테이션 -> 타입 힌트 추가: 모든 메서드에 적용

#### implementation-django (Refactoring 모드)

- [ ] 구조화되지 않은 설정: 해당 없음
- [x] 불리언 플래그 필드 -> TextChoices: `Status` TextChoices 도입
- [ ] 다중 테이블 상속: 해당 없음
- [ ] prefetch/select_related 누락: 현재 단일 주문 조회로 영향 미미
- [x] 루프 내 개별 save() -> bulk_create: `OrderItem.objects.bulk_create` 적용
- [ ] 같은 앱 시그널: 해당 없음
- [ ] fields = "__all__": 해당 없음
- [ ] 문자열 보간 raw SQL: 해당 없음
- [x] 비즈니스 로직이 있는 Fat 뷰 -> 모델 메서드 + 서비스: 추출 완료
- [ ] DRF Serializer/ViewSet: 해당 없음
- [x] 뷰 내 bare queryset -> 모델 메서드로 추출: `to_detail_dict` 메서드 도입
- [ ] 모델 검증 누락: 별도 이슈 (현재 스코프 외)
- [ ] 레거시 Django 패턴: 해당 없음

#### architecture-api (Refactoring 모드)

- [ ] URL의 동사: 해당 없음 (URL 정의가 코드에 없음)
- [ ] 잘못된 HTTP 메서드: GET/POST 사용 적절
- [x] 잘못된 상태 코드: DoesNotExist -> 500 문제를 get_object_or_404로 해결 (404)
- [x] 비표준 에러 응답: 입력 검증 실패 시 400 + error 메시지 반환
- [ ] 단수 컬렉션 이름: 해당 없음
- [ ] 목록 엔드포인트 페이지네이션: 현재 단일 조회만 존재
- [ ] 버저닝: 현재 스코프 외
- [ ] URL의 민감한 데이터: 해당 없음
- [ ] 멱등성 없는 POST: 고려 사항이나 현재 스코프에서는 과도

---

### 동작 변경 사항

이 리팩토링은 다음의 관찰 가능한 동작 변경을 포함한다:

1. **존재하지 않는 주문 조회**: 기존에는 `Order.DoesNotExist` 예외로 인해 500 응답이 반환되었으나, 이제 404 응답을 반환한다.
2. **잘못된 JSON 입력**: 기존에는 `json.JSONDecodeError`로 500 응답이 반환되었으나, 이제 400 응답과 에러 메시지를 반환한다.
3. **items 필드 누락**: 기존에는 `KeyError`로 500 응답이 반환되었으나, 이제 400 응답과 안내 메시지를 반환한다.
4. **트랜잭션 원자성**: 기존에는 Order가 생성된 후 OrderItem 생성이 실패하면 아이템 없는 주문이 남을 수 있었으나, 이제 전체가 롤백된다.
5. **벌크 INSERT**: 기존 N번의 INSERT 쿼리가 1번의 bulk_create로 통합된다.

모든 변경은 기존 동작을 개선하는 방향이며, 정상적인 입력에 대한 응답 형식은 동일하게 유지된다.

---

> **관련 스킬 참조:**
> - [Django Ninja로 API 레이어 전환] -> **implementation-django-ninja** 스킬
> - [주문 도메인이 복잡해지면 헥사고날/CQRS 도입] -> **architecture-implementation-patterns** 스킬
> - [리팩토링된 코드의 테스트 작성] -> **implementation-test** 스킬
> - [주문 상태 전이 설계 (상태 머신)] -> **architecture-ddd** 스킬
> - [API 에러 형식을 RFC 9457로 표준화] -> **architecture-api** 스킬
