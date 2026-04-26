# Refactoring: DRF OrderViewSet -> Django Ninja

## 1. DRF Serializer -> Django Ninja ModelSchema

```
[Before]
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

[After]
class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ['id', 'status', 'total', 'created_at', 'updated_at']

class OrderIn(Schema):
    status: str
    total: Decimal

[Reason] Schema 설계 -- ModelSchema를 사용하여 모델 기반 스키마를 자동 생성한다. fields = '__all__'은 민감한 데이터가 노출될 수 있으므로 명시적 필드 목록으로 제한한다. 요청(In)과 응답(Out) 스키마를 분리하여 입력 검증과 출력 직렬화를 명확히 구분한다.
```

## 2. DRF ViewSet -> Router + 데코레이터 엔드포인트

```
[Before]
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

[After]
from ninja import Router, ModelSchema, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate, LimitOffsetPagination
from ninja.security import HttpBearer
from typing import List
from decimal import Decimal
from .models import Order


class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        user = Token.objects.filter(key=token).select_related('user').first()
        if user:
            return user.user
        return None


class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ['id', 'status', 'total', 'created_at', 'updated_at']


class OrderIn(Schema):
    status: str
    total: Decimal


router = Router(tags=["orders"], auth=AuthBearer())


@router.get("/", response=List[OrderOut])
@paginate(LimitOffsetPagination)
def list_orders(request) -> List[OrderOut]:
    return Order.objects.all()


@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: int) -> OrderOut:
    order = Order.objects.filter(id=order_id).first()
    if not order:
        raise HttpError(404, "Order not found")
    return order


@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderIn) -> tuple:
    order = Order.objects.create(**payload.dict())
    return 201, order


@router.put("/{order_id}", response=OrderOut)
def update_order(request, order_id: int, payload: OrderIn) -> OrderOut:
    order = Order.objects.filter(id=order_id).first()
    if not order:
        raise HttpError(404, "Order not found")
    for attr, value in payload.dict().items():
        setattr(order, attr, value)
    order.save()
    return order


@router.delete("/{order_id}", response={204: None})
def delete_order(request, order_id: int) -> tuple:
    order = Order.objects.filter(id=order_id).first()
    if not order:
        raise HttpError(404, "Order not found")
    order.delete()
    return 204, None

[Reason] 라우팅 -- ViewSet을 Router + 개별 데코레이터 엔드포인트로 분해한다. 각 CRUD 작업이 독립된 함수로 분리되어 가독성과 유지보수성이 향상된다. Router(tags=["orders"])로 OpenAPI 문서에서 그룹화한다.
```

## 3. DRF permission_classes -> Django Ninja 인증 클래스

```
[Before]
permission_classes = [permissions.IsAuthenticated]

[After]
from ninja.security import HttpBearer

class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        user = Token.objects.filter(key=token).select_related('user').first()
        if user:
            return user.user
        return None

router = Router(tags=["orders"], auth=AuthBearer())

[Reason] 인증 -- DRF의 permission_classes 대신 Django Ninja의 내장 인증 클래스 HttpBearer를 사용한다. Router 수준에서 auth를 지정하여 라우터의 모든 엔드포인트에 인증을 일괄 적용한다. 인증 실패 시 자동으로 HTTP 401이 반환된다.
```

## 4. 타입 힌트 추가

```
[Before]
# DRF ViewSet에는 엔드포인트 매개변수와 반환 타입에 타입 힌트가 없음

[After]
@router.get("/", response=List[OrderOut])
@paginate(LimitOffsetPagination)
def list_orders(request) -> List[OrderOut]:
    ...

@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: int) -> OrderOut:
    ...

@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderIn) -> tuple:
    ...

@router.put("/{order_id}", response=OrderOut)
def update_order(request, order_id: int, payload: OrderIn) -> OrderOut:
    ...

@router.delete("/{order_id}", response={204: None})
def delete_order(request, order_id: int) -> tuple:
    ...

[Reason] 기준 요구사항 -- 모든 엔드포인트 매개변수(order_id: int, payload: OrderIn)와 반환 타입(-> OrderOut, -> tuple)에 타입 힌트를 명시한다. response= 데코레이터 매개변수로 응답 스키마도 지정하여 OpenAPI 문서 자동 생성과 런타임 검증을 활성화한다.
```

## 5. fields = '__all__' -> 명시적 필드 목록

```
[Before]
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

[After]
class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ['id', 'status', 'total', 'created_at', 'updated_at']

[Reason] Schema 설계 -- fields = '__all__'은 모델에 추가되는 새 필드가 자동으로 API에 노출되어 민감한 데이터 유출의 위험이 있다. 명시적 필드 목록으로 API가 노출하는 데이터를 의도적으로 통제한다.
```

## 6. 페이지네이션 추가

```
[Before]
# DRF ModelViewSet의 list 액션에 명시적 페이지네이션 설정 없음

[After]
from ninja.pagination import paginate, LimitOffsetPagination

@router.get("/", response=List[OrderOut])
@paginate(LimitOffsetPagination)
def list_orders(request) -> List[OrderOut]:
    return Order.objects.all()

[Reason] 페이지네이션 -- 목록 엔드포인트에 @paginate 데코레이터와 LimitOffsetPagination을 적용한다. 페이지네이션 없이 전체 데이터를 반환하면 대량 데이터에서 성능 문제와 메모리 과부하가 발생할 수 있다. 뷰 함수는 전체 QuerySet을 반환하고 실제 슬라이싱은 페이지네이터가 처리한다.
```

## 7. 에러 처리 추가

```
[Before]
# DRF ModelViewSet은 내장 에러 처리를 제공하지만
# Django Ninja로 전환 시 명시적 에러 처리가 필요

[After]
from ninja.errors import HttpError

@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: int) -> OrderOut:
    order = Order.objects.filter(id=order_id).first()
    if not order:
        raise HttpError(404, "Order not found")
    return order

[Reason] 에러 처리 -- HttpError를 사용하여 존재하지 않는 리소스에 대해 명확한 404 응답을 반환한다. RFC 9457 Problem Details 형식의 전역 에러 핸들러와 결합하면 일관된 에러 응답 구조를 제공할 수 있다.
```

---

## 적용하지 않은 항목과 근거

- **I/O가 있는 sync 엔드포인트 -> async 변환**: 이 코드는 단순 ORM CRUD 작업만 수행하므로 async 변환의 실익이 크지 않다. async 뷰 선택 가이드에 따르면 단순 ORM CRUD는 sync가 권장된다.
- **수동 필터링 -> FilterSchema 변환**: 원본 코드에 필터링 로직이 없으므로 해당하지 않는다.
- **Fat 엔드포인트 -> 서비스 레이어 추출**: 각 엔드포인트가 단일 책임을 가지며 복잡한 비즈니스 로직이 없으므로 현재 수준에서 서비스 레이어 분리는 불필요하다.
- **커스텀 에러 형식 -> RFC 9457**: 원본 코드에 커스텀 에러 형식이 없으므로 변환 대상이 아니다. 다만 프로젝트 수준에서 RFC 9457 전역 핸들러 등록을 권장한다.

---

Django 모델(Order) 정의, ORM QuerySet, 마이그레이션에 대한 자세한 안내는 **implementation-django** 스킬을 참조하세요.

API 설계 원칙(REST, URL 설계, 상태 코드, 버저닝, 페이지네이션 전략)에 대한 자세한 안내는 **architecture-api** 스킬을 참조하세요.

타입 힌트, dataclasses, async 패턴 등 Python 전용 컨벤션에 대한 자세한 안내는 **implementation-python** 스킬을 참조하세요.
