# D01: DRF 코드 리뷰 (implementation-django 스킬)

**Skill:** implementation-django (Review mode)
**Code under review:**
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

### 리뷰 결과

[Convention: DRF 사용 금지] -- **DRF(Django REST Framework)는 사용하지 않는다.** 모든 API 코드는 Django Ninja로 구현한다. DRF의 Serializer, ViewSet, APIView, permission_classes를 발견하면 Django Ninja 패턴으로 전환을 권고한다.

[Convention: fields = '__all__' 금지] -- `fields = '__all__'`은 해시된 비밀번호 등 민감한 데이터가 노출될 수 있다. 명시적 필드 목록을 사용해야 한다.

[Convention: select_related 누락] -- `Order.objects.all()`에서 FK 관계 접근 시 N+1 문제가 발생한다. `select_related()`/`prefetch_related()`를 적용해야 한다.

[Convention: 페이지네이션 누락] -- 목록 엔드포인트에 페이지네이션이 없으면 대량 데이터에서 성능 문제가 발생한다.

### 권장 Django Ninja 전환 (implementation-django-ninja 위임)

```python
from ninja import Router, ModelSchema
from ninja.pagination import paginate

router = Router(tags=["orders"])

class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ["id", "status", "total", "created_at"]

@router.get("/", response=list[OrderOut], auth=SessionAuth())
@paginate
def list_orders(request):
    return Order.objects.select_related("customer").all()
```

---
> **관련 스킬 참조:**
> - [DRF -> Django Ninja 전환] → **implementation-django-ninja** 스킬
> - [QuerySet 최적화] → 이 스킬 `references/queryset-manager.md`
> - [REST 페이지네이션 전략] → **architecture-api** 스킬
