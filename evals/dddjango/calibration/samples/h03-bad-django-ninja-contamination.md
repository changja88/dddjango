# 잘못된 Starlette 답변

Starlette 요청이지만 Django Ninja Router를 섞는다.

```python
from ninja import Router

router = Router()


@router.post("/orders")
def create_order(request):
    return {"id": 1}
```
