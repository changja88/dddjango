Django Ninja에서도 service layer는 **Django app 내부에 두는 방식**이 가장 무난합니다.

보통은 이렇게 둡니다.

```text
project/
  users/
    api.py
    schemas.py
    models.py
    services.py
    selectors.py
```

또는 서비스가 커지면 패키지로 나눕니다.

```text
users/
  api.py
  schemas.py
  models.py
  services/
    __init__.py
    user_service.py
    auth_service.py
  selectors/
    __init__.py
    user_selector.py
```

추천 구조는 다음 기준입니다.

- `api.py`: Django Ninja 라우터, request/response 처리만 담당
- `schemas.py`: 입력/출력 스키마
- `services.py`: 상태를 바꾸는 비즈니스 로직
- `selectors.py`: 조회 전용 쿼리 로직
- `models.py`: 데이터 구조와 아주 기본적인 도메인 제약

예를 들면:

```python
# users/api.py
@router.post("/users")
def create_user(request, payload: UserCreateSchema):
    user = user_service.create_user(payload)
    return user
```

```python
# users/services.py
from django.db import transaction

@transaction.atomic
def create_user(payload):
    user = User.objects.create(
        email=payload.email,
        name=payload.name,
    )
    return user
```

핵심은 **Ninja 라우터에 비즈니스 로직을 넣지 않는 것**입니다. Ninja는 DRF의 ViewSet보다 가볍기 때문에, 라우터 함수가 금방 커지기 쉽습니다. 그래서 `api.py`는 얇게 유지하고, 실제 유스케이스는 `services.py`로 빼는 편이 테스트와 유지보수에 좋습니다.

앱을 넘나드는 유스케이스가 많다면 `common/services.py` 같은 전역 위치보다, 가능하면 **주도권을 가진 app의 service**에 두는 게 좋습니다.

예:

```text
orders/services.py
```

`주문 생성`이 사용자, 결제, 쿠폰을 건드리더라도 핵심 유스케이스가 주문이면 `orders` 앱에 둡니다.