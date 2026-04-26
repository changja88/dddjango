# b01-drf-redirect

- Prompt: "DRF ModelSerializer로 주문 API를 만들려고 해. Serializer 구성 좀 도와줘."
- Skill: `implementation-django-ninja`
- Expected: DRF 요청을 Django Ninja 패턴으로 리디렉션

---

## 응답

이 프로젝트는 **DRF(Django REST Framework)를 사용하지 않습니다.** 모든 API 코드는 Django Ninja로 구현합니다. DRF의 `ModelSerializer` 대신 Django Ninja의 `ModelSchema`를 사용하여 주문 API를 구성하겠습니다.

DRF `ModelSerializer`에 대응하는 Django Ninja 패턴은 `ModelSchema`입니다. 동일한 목적(모델 기반 자동 직렬화)을 더 간결하게 달성합니다.

```python
from ninja import ModelSchema, Schema, Router, PatchDict
from orders.models import Order

# --- Schema 정의 ---

class OrderIn(Schema):
    """주문 생성 요청용 Schema"""
    product_id: int
    quantity: int
    shipping_address: str

class OrderOut(ModelSchema):
    """주문 응답용 ModelSchema — 노출할 필드를 명시적으로 선택"""
    class Meta:
        model = Order
        fields = ["id", "product_id", "quantity", "shipping_address", "status", "created_at"]

class OrderPatch(Schema):
    """주문 부분 수정용 Schema"""
    quantity: int | None = None
    shipping_address: str | None = None

# --- Router 정의 ---

router = Router(tags=["orders"])

@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderIn) -> Order:
    return Order.objects.create(**payload.dict())

@router.get("/{int:order_id}", response=OrderOut)
def get_order(request, order_id: int) -> Order:
    return Order.objects.get(id=order_id)

@router.patch("/{int:order_id}", response=OrderOut)
def update_order(request, order_id: int, payload: PatchDict[OrderPatch]) -> Order:
    order = Order.objects.get(id=order_id)
    for key, value in payload.items():
        setattr(order, key, value)
    order.save()
    return order
```

**DRF와의 주요 차이점:**

| DRF 패턴 | Django Ninja 대응 |
|---|---|
| `ModelSerializer` | `ModelSchema` (Pydantic 기반) |
| `fields = '__all__'` | `Meta.fields`에 명시적 필드 목록 (전체 노출 금지) |
| `ViewSet` + `DefaultRouter` | `Router()` + 데코레이터 (`@router.get`, `@router.post`) |
| `serializer.is_valid()` | Schema가 자동 검증 (Pydantic 타입 시스템) |
| `SerializerMethodField` | `resolve_<field>` resolver 메서드 |

---

> **관련 스킬 참조:**
> - [Schema 설계와 ModelSchema 상세] -> **implementation-django-ninja** 스킬 (references/schema-validation.md)
> - [Order 모델 정의, ORM 패턴] -> **implementation-django** 스킬
> - [REST URL 설계, 상태 코드 선택] -> **architecture-api** 스킬

---

## 경계 검증 결과

| 항목 | 결과 |
|---|---|
| DRF 요청 감지 | PASS -- "DRF ModelSerializer"를 정확히 인식 |
| 경계 리디렉션 | PASS -- DRF 대신 Django Ninja 패턴으로 전환 권고 |
| 대체 패턴 제공 | PASS -- ModelSerializer -> ModelSchema 매핑 제시 |
| 스킬 규칙 준수 | PASS -- "DRF 코드를 발견하면 Django Ninja 패턴으로 전환을 권고한다" 적용 |
| 응답 구조 준수 | PASS -- [주요 내용] + [관련 스킬 참조] 형식 사용 |
| Writing 모드 적용 | PASS -- 코드가 스스로 말하게, 컨벤션 설명 인라인 주석 없음 |
