Django Ninja 프로젝트에서는 보통 **각 Django app 안에 service layer를 두는 방식**이 가장 무난합니다.

예시:

```text
project/
  users/
    models.py
    api.py          # Django Ninja router
    schemas.py
    services.py     # users 도메인 서비스
    selectors.py    # 조회 전용 로직, 선택 사항
  orders/
    models.py
    api.py
    schemas.py
    services.py
```

추천 구조는 이렇습니다.

```python
# orders/api.py
@router.post("/")
def create_order(request, payload: OrderCreateSchema):
    order = order_services.create_order(
        user=request.user,
        data=payload,
    )
    return order
```

```python
# orders/services.py
from django.db import transaction

@transaction.atomic
def create_order(*, user, data):
    # validation, model 생성, 외부 호출, 이벤트 발행 등
    ...
```

기준은 간단합니다.

- `api.py`: HTTP 요청/응답, 인증, schema 변환
- `schemas.py`: 입출력 DTO
- `services.py`: 쓰기 작업, 비즈니스 로직, 트랜잭션
- `selectors.py`: 복잡한 조회 쿼리, read-only 로직
- `models.py`: DB 구조와 모델 자체에 가까운 작은 메서드

앱이 작으면 `services.py` 하나로 충분합니다. 커지면 이렇게 나눌 수 있습니다.

```text
orders/
  services/
    __init__.py
    create_order.py
    cancel_order.py
    payment.py
```

개인적으로는 Django Ninja에서 `api.py` 또는 `views.py` 안에 비즈니스 로직을 많이 넣는 건 피하는 편이 좋습니다. Ninja router는 얇게 두고, 실제 유스케이스는 app 내부 service에서 처리하는 구조가 테스트하기도 쉽고 나중에 Celery task, management command, admin action 등에서도 재사용하기 좋습니다.