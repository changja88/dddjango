# 잘못된 충돌 판단

API 사용성이 더 중요하므로 `PATCH /orders/{id}`에서 status를 직접 바꿉니다.
router에서 바로 저장하면 됩니다.

```python
@router.patch("/orders/{order_id}")
def patch_order(request, order_id: int, payload: dict):
    order.status = payload["status"]
    order.save()
```

도메인 쪽 규칙은 나중에 맞추면 됩니다.
