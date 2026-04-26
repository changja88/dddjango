# T24: Django Ninja URL 설계에서 REST 리소스 명명 규칙과 상태 코드 매핑

**Skill:** implementation-django-ninja (Writing mode)
**Cross-skill references loaded:** architecture-api (URL 설계, 상태 코드)

## [주요 내용]

### REST 리소스 명명 규칙 (architecture-api 위임)

| 규칙 | 좋음 | 나쁨 |
|------|------|------|
| 명사 사용 (동사 아님) | `/orders` | `/create-order` |
| 복수 명사 (컬렉션) | `/customers/5` | `/customer/5` |
| 케밥 케이스, 소문자 | `/order-items` | `/orderItems` |
| 후행 슬래시 없음 | `/orders` | `/orders/` |
| 3단계 이하 깊이 | `/customers/5/orders` | `/a/b/c/d/e` |

### Django Ninja Router에서의 적용

```python
from ninja import Router

router = Router(tags=["orders"])

@router.get("/", response=list[OrderOut])
def list_orders(request) -> list[Order]:
    return Order.objects.select_related("customer").all()

@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderIn) -> tuple[int, Order]:
    order = Order.objects.create(**payload.dict())
    return 201, order

@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: int) -> Order:
    return get_object_or_404(Order, id=order_id)

@router.put("/{order_id}", response=OrderOut)
def replace_order(request, order_id: int, payload: OrderIn) -> Order:
    order = get_object_or_404(Order, id=order_id)
    for attr, value in payload.dict().items():
        setattr(order, attr, value)
    order.save()
    return order

@router.patch("/{order_id}", response=OrderOut)
def update_order(request, order_id: int, payload: PatchDict[OrderIn]) -> Order:
    order = get_object_or_404(Order, id=order_id)
    for attr, value in payload.items():
        setattr(order, attr, value)
    order.save()
    return order

@router.delete("/{order_id}", response={204: None})
def delete_order(request, order_id: int) -> tuple[int, None]:
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return 204, None
```

### 상태 코드 매핑 (architecture-api 위임)

| HTTP 메서드 | 성공 코드 | 의미 |
|-------------|-----------|------|
| GET | 200 | 조회 성공 |
| POST | 201 | 리소스 생성 (Location 헤더) |
| PUT | 200 | 전체 교체 성공 |
| PATCH | 200 | 부분 수정 성공 |
| DELETE | 204 | 삭제 성공, 응답 본문 없음 |

에러 응답은 RFC 9457 Problem Details 형식을 사용한다.

---
> **관련 스킬 참조:**
> - [URL/리소스 설계 원칙] → **architecture-api** 스킬
> - [Django 모델/QuerySet] → **implementation-django** 스킬
> - [Python 타입 힌트] → **implementation-python** 스킬
