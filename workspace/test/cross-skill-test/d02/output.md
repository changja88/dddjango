# D02: DRF 코드를 Django Ninja로 리팩토링 (implementation-django-ninja 스킬)

**Skill:** implementation-django-ninja (Refactoring mode)
**Code to refactor:**
```python
from rest_framework import serializers, viewsets, permissions
class OrderSerializer(serializers.ModelSerializer):
    class Meta: model=Order; fields='__all__'
class OrderViewSet(viewsets.ModelViewSet):
    queryset=Order.objects.all()
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]
```

## [주요 내용]

### 리팩토링 변경 사항

[Before]
```python
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
```

[After]
```python
class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ["id", "status", "total", "created_at"]
```

[Reason] DRF Serializer -> Django Ninja Schema -- ModelSchema는 Pydantic 기반이며 명시적 필드 목록으로 민감한 데이터 노출을 방지한다.

---

[Before]
```python
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
```

[After]
```python
from ninja import Router
from ninja.security import SessionAuth
from ninja.pagination import paginate, LimitOffsetPagination

router = Router(tags=["orders"], auth=SessionAuth())

@router.get("/", response=list[OrderOut])
@paginate(LimitOffsetPagination)
def list_orders(request):
    return Order.objects.select_related("customer").all()

@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: int):
    return get_object_or_404(Order, id=order_id)

@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderIn):
    order = Order.objects.create(**payload.dict())
    return 201, order

@router.patch("/{order_id}", response=OrderOut)
def update_order(request, order_id: int, payload: PatchDict[OrderIn]):
    order = get_object_or_404(Order, id=order_id)
    for attr, val in payload.items():
        setattr(order, attr, val)
    order.save(update_fields=list(payload.keys()) + ["updated_at"])
    return order

@router.delete("/{order_id}", response={204: None})
def delete_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return 204, None
```

[Reason] DRF ViewSet -> Router + 데코레이터 -- ViewSet의 암시적 URL 매핑 대신 명시적 데코레이터 패턴을 사용한다. 타입 힌트가 필수이며, select_related로 N+1을 방지하고, @paginate로 페이지네이션을 적용한다.

---

[Before]
```python
permission_classes = [permissions.IsAuthenticated]
```

[After]
```python
router = Router(auth=SessionAuth())
```

[Reason] DRF permission_classes -> Ninja 인증 클래스 -- Django Ninja의 내장 인증(SessionAuth, HttpBearer, APIKeyHeader)을 라우터 수준에서 적용한다.

---
> **관련 스킬 참조:**
> - [Django 모델, QuerySet 최적화] → **implementation-django** 스킬
> - [REST URL 설계, 상태 코드] → **architecture-api** 스킬
> - [에러 처리, RFC 9457] → 이 스킬 `references/error-throttling.md`
