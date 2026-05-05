# Django Ninja 에러 표준

Problem Details와 `application/problem+json`을 표준으로 사용합니다. 목록 성공
응답은 `items`와 `meta` envelope를 사용합니다.

```python
from enum import Enum
from ninja import Router, Schema

router = Router()

class ErrorCode(str, Enum):
    VALIDATION_ERROR = "validation_error"

class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    code: ErrorCode

class OrderOut(Schema):
    id: int

class OrderListOut(Schema):
    items: list[OrderOut]
    meta: dict

@router.get("/orders", response={200: OrderListOut, 400: ProblemDetail, 404: ProblemDetail, 422: ProblemDetail})
def list_orders(request):
    pass
```

검증은 아직 실행하지 않았습니다.
