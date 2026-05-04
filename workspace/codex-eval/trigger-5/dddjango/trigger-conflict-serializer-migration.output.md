이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

요청 검증용 클래스는 `Serializer`가 아니라 Django Ninja의 `Schema`로 만들면 됩니다. 보통 `schemas.py`에 요청/응답 스키마를 분리합니다.

```python
# accounts/schemas.py
from ninja import Schema, Field


class UserCreateIn(Schema):
    email: str = Field(..., min_length=5, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class UserOut(Schema):
    id: int
    email: str
    name: str
```

```python
# accounts/api.py
from ninja import Router

from .models import User
from .schemas import UserCreateIn, UserOut

router = Router(tags=["accounts"])


@router.post("/", response={201: UserOut})
def create_user(request, payload: UserCreateIn) -> tuple[int, User]:
    user = User.objects.create_user(
        email=payload.email,
        name=payload.name,
        password=payload.password,
    )
    return 201, user
```

```python
# config/api.py
from ninja import NinjaAPI

from accounts.api import router as accounts_router

api = NinjaAPI()
api.add_router("/users/", accounts_router)
```

```python
# config/urls.py
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

핵심은 `payload: UserCreateIn`처럼 엔드포인트 파라미터에 `Schema` 타입을 붙이는 것입니다. 그러면 Django Ninja가 JSON body를 자동 파싱하고 타입/필드 검증을 수행하며, 실패 시 검증 오류 응답을 반환합니다. 응답도 `response=...`에 `Schema`를 지정하면 선언한 필드만 직렬화됩니다.

검증은 여기서 실행하지 못했습니다. 적용 후에는 다음을 돌리면 됩니다.

```bash
python manage.py check
pytest
```

---
> **관련 스킬 참조:**
> - 요청/응답 검증과 라우팅 구현 → **implementation-django-ninja** 스킬