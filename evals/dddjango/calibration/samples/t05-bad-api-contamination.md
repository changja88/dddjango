# 잘못된 템플릿 페이지 답변

템플릿 페이지 요청이지만 Django Ninja API로 처리합니다.

```python
from ninja import Router

router = Router()

@router.get("/orders")
def order_list(request):
    return []
```
