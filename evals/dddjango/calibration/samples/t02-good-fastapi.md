# FastAPI 주문 생성

FastAPI 요청이므로 Django Ninja나 dddjango 정책을 적용하지 않습니다.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class OrderIn(BaseModel):
    product_id: int
    quantity: int

@app.post("/orders")
def create_order(payload: OrderIn):
    return {"status": "created"}
```

검증은 `pytest`와 FastAPI TestClient로 진행합니다. 실제 테스트는 실행하지
않았습니다.
