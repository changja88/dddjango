Django Ninja에서는 DRF의 `Serializer`를 새로 만들어 요청 검증에 쓰기보다는, **`ninja.Schema` 기반의 요청 DTO/Input Schema**를 만드는 게 맞습니다. Ninja가 내부적으로 Pydantic 검증을 사용하므로 API 함수 파라미터에 타입으로 연결하면 자동 검증됩니다.

예시:

```python
# app/schemas.py
from ninja import Schema
from pydantic import Field, field_validator


class CreateOrderRequest(Schema):
    product_id: int
    quantity: int = Field(gt=0)
    memo: str | None = Field(default=None, max_length=500)

    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("product_id must be positive")
        return value
```

```python
# app/api.py
from ninja import Router

from .schemas import CreateOrderRequest

router = Router()


@router.post("/orders")
def create_order(request, payload: CreateOrderRequest):
    # 여기까지 왔으면 payload는 이미 검증됨
    return {
        "product_id": payload.product_id,
        "quantity": payload.quantity,
    }
```

요청이 잘못되면 Ninja가 자동으로 `422` 응답을 반환합니다.

주의할 점은 이름을 `Serializer`라고 붙일 수는 있지만, Django Ninja 프로젝트라면 보통 `CreateSomethingRequest`, `SomethingInput`, `SomethingSchema`처럼 명명하는 편이 더 명확합니다. DRF의 `rest_framework.serializers.Serializer`를 섞으면 Ninja의 타입 기반 검증 흐름과 어긋납니다.

현재 `/private/tmp/dddjango-codex-eval` 디렉터리는 비어 있고, 세션도 읽기 전용이라 실제 파일은 수정하지 못했습니다. 프로젝트 파일을 넣어주면 기존 구조에 맞춰 정확한 위치와 클래스 이름으로 패치 형태까지 잡아드릴 수 있습니다.