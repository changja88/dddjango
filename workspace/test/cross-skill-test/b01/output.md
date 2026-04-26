# B01: Django View에서 JsonResponse로 JSON 반환 코드 리뷰

**Skill:** implementation-django (Review mode)
**Code under review:**
```python
class OrderListView(View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).values('id', 'status', 'total')
        return JsonResponse({'orders': list(orders)})
```

## [주요 내용]

### 리뷰: 잘된 점

- `values()`로 필요한 필드만 선택하여 직렬화 효율적
- `request.user`로 사용자별 필터링 적용

### 리뷰: 개선 사항

[Convention: DRF/JsonResponse 대신 Django Ninja 사용] -- JSON API 엔드포인트는 Django Ninja Router + Schema로 구현해야 한다. `View + JsonResponse` 패턴은 타입 검증, OpenAPI 문서 생성, 인증/페이지네이션 통합이 불가능하다.

[Convention: 인증 보호 누락] -- `LoginRequiredMixin`이나 Django Ninja 인증 클래스 없이 `request.user`를 사용하면, 미인증 사용자가 AnonymousUser로 접근할 수 있다.

[Convention: 페이지네이션 누락] -- 목록 엔드포인트에 페이지네이션이 없다. 데이터가 증가하면 성능 문제가 발생한다.

[Convention: 에러 처리 없음] -- 데이터베이스 오류나 예외 발생 시 처리가 없다.

### 권장 Django Ninja 전환 (implementation-django-ninja 위임)

```python
from ninja import Router
from ninja.security import SessionAuth
from ninja.pagination import paginate

router = Router(tags=["orders"], auth=SessionAuth())

class OrderOut(Schema):
    id: int
    status: str
    total: int

@router.get("/", response=list[OrderOut])
@paginate
def list_orders(request):
    return Order.objects.filter(user=request.auth).all()
```

---
> **관련 스킬 참조:**
> - [Django Ninja Schema, Router, 인증] → **implementation-django-ninja** 스킬
> - [REST 페이지네이션, 에러 형식] → **architecture-api** 스킬
> - [QuerySet 최적화] → 이 스킬 `references/queryset-manager.md`
