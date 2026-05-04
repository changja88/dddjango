Django Ninja 프로젝트에서는 보통 **각 Django app 안에 service layer를 두는 방식**이 가장 좋습니다.

추천 구조:

```text
project/
  users/
    models.py
    schemas.py
    api.py
    services.py
    selectors.py
  orders/
    models.py
    schemas.py
    api.py
    services.py
    selectors.py
```

역할은 이렇게 나누는 게 깔끔합니다.

- `api.py`: Django Ninja router, HTTP 요청/응답 처리
- `schemas.py`: 입력/출력 스키마
- `services.py`: 비즈니스 로직, 상태 변경, 트랜잭션
- `selectors.py`: 조회 쿼리, read-only 데이터 접근
- `models.py`: DB 모델과 모델 자체의 불변 조건

예를 들면:

```python
# orders/api.py
@router.post("/orders")
def create_order(request, payload: OrderCreateSchema):
    order = order_services.create_order(
        user=request.user,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )
    return order
```

```python
# orders/services.py
from django.db import transaction

@transaction.atomic
def create_order(*, user, product_id: int, quantity: int):
    product = Product.objects.select_for_update().get(id=product_id)

    if product.stock < quantity:
        raise ValueError("Not enough stock")

    order = Order.objects.create(
        user=user,
        product=product,
        quantity=quantity,
    )

    product.stock -= quantity
    product.save(update_fields=["stock"])

    return order
```

개인적으로는 이 기준을 권합니다.

```text
작은 앱이면: app/services.py
커지면: app/services/order_service.py, app/services/payment_service.py
조회가 복잡하면: app/selectors.py 분리
여러 앱을 엮는 유스케이스면: 별도 app 또는 domain/usecases 계층 고려
```

즉, 처음부터 `core/services/` 같은 전역 폴더에 몰아넣기보다는 **도메인별 Django app 내부에 두는 것**이 유지보수에 더 좋습니다. API가 얇아지고, 테스트도 service 단위로 잡기 쉬워집니다.