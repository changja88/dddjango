# DRF 요청 전환

이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. APIView와
ModelSerializer는 금지 대상이므로 새 코드에 넣지 않습니다.

```python
from ninja import Router, Schema

router = Router()

class OrderIn(Schema):
    product_id: int
    quantity: int

class OrderOut(Schema):
    id: int
    status: str

class ProblemDetail(Schema):
    title: str
    detail: str

@router.post("/orders", response={201: OrderOut, 400: ProblemDetail})
def create_order(request, payload: OrderIn):
    pass
```

검증은 아직 실행하지 않았습니다. 실행할 명령은 `python manage.py check`와
`pytest`입니다.
