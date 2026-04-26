# T25: Schema에서 PEP 695 제네릭과 Protocol을 활용하려면?

**Skill:** implementation-django-ninja (Writing mode)
**Cross-skill references loaded:** implementation-python (PEP 695, Protocol)

## [주요 내용]

### PEP 695 제네릭 Schema (Python 3.12+, implementation-python 위임)

PEP 695의 `type` 문과 제네릭 구문을 Django Ninja Schema에 적용한다.

```python
from ninja import Schema
from typing import Protocol

# PEP 695 타입 별칭
type OrderId = int
type Money = int

# 제네릭 응답 래퍼 Schema
class PaginatedResponse[T](Schema):
    items: list[T]
    total: int
    has_more: bool

class ErrorResponse(Schema):
    type: str
    title: str
    status: int
    detail: str

# 사용
@router.get("/orders", response=PaginatedResponse[OrderOut])
def list_orders(request) -> dict:
    ...
```

### Protocol 기반 Schema 인터페이스 (implementation-python 위임)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Identifiable(Protocol):
    id: int

@runtime_checkable
class Timestamped(Protocol):
    created_at: datetime
    updated_at: datetime

class OrderOut(Schema):
    """Identifiable + Timestamped Protocol을 만족하는 Schema"""
    id: int
    status: str
    total: Money
    created_at: datetime
    updated_at: datetime

# Protocol로 타입 안전한 서비스 레이어
class OrderService:
    def get_by_id[T: Identifiable](self, model: type[T], pk: int) -> T:
        return model.objects.get(id=pk)
```

### resolver에서 PEP 695 활용

```python
class OrderDetailOut[T: Schema](Schema):
    id: int
    computed_field: str

    @staticmethod
    def resolve_computed_field(obj, context) -> str:
        return f"order-{obj.id}"
```

---
> **관련 스킬 참조:**
> - [PEP 695 제네릭, Protocol, type 문] → **implementation-python** 스킬
> - [Schema resolver, ModelSchema] → 이 스킬 `references/schema-validation.md`
> - [SOLID, 인터페이스 분리] → **implementation-cleancode** 스킬
