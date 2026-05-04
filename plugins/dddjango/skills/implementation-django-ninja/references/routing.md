# 라우팅과 프로젝트 구조 레퍼런스

> Django Ninja 공식 문서 기반 레퍼런스. Router, add_router, 중첩 라우터, Path 파라미터, API 버전 관리, 프로젝트 구조를 다룬다.

---

## 1. Router() vs NinjaAPI()

`NinjaAPI`는 최상위 API 인스턴스이고, `Router`는 API를 여러 모듈로 분할할 때 사용하는 하위 라우터다. 각 앱 모듈에서는 `Router`를 사용하고, 메인 프로젝트에서 `NinjaAPI`에 연결하는 구조가 권장된다.

### Router 기본 사용

```python
# events/api.py
from ninja import Router
from .models import Event

router = Router()

@router.get('/')
def list_events(request):
    return [
        {"id": e.id, "title": e.title}
        for e in Event.objects.all()
    ]

@router.get('/{event_id}')
def event_details(request, event_id: int):
    event = Event.objects.get(id=event_id)
    return {"title": event.title, "details": event.details}
```

### NinjaAPI에 라우터 연결

```python
# myproject/api.py
from ninja import NinjaAPI
from events.api import router as events_router

api = NinjaAPI()
api.add_router("/events/", events_router)
```

---

## 2. add_router() 조합

### 직접 임포트 방식

```python
from ninja import NinjaAPI
from events.api import router as events_router
from news.api import router as news_router

api = NinjaAPI()
api.add_router("/events/", events_router)
api.add_router("/news/", news_router)
```

### Python 경로 문자열 방식

모듈을 직접 임포트하지 않고 문자열 경로로 지정할 수 있다:

```python
api = NinjaAPI()
api.add_router("/events/", events_router)
api.add_router("/news/", "news.api.router")      # 문자열 경로
api.add_router("/blogs/", "blogs.api.router")     # 문자열 경로
```

### 라우터 인증 설정

```python
# add_router()에서 인증 지정
api.add_router("/events/", events_router, auth=BasicAuth())

# Router 생성자에서 인증 지정
router = Router(auth=BasicAuth())
```

### 라우터 태그 설정

OpenAPI 문서에서 작업을 그룹화한다:

```python
# add_router()에서 태그 지정
api.add_router("/events/", events_router, tags=["events"])

# Router 생성자에서 태그 지정
router = Router(tags=["events"])
```

---

## 3. 중첩 라우터

라우터는 다른 라우터를 재귀적으로 포함할 수 있다. `api`와 `router` 인스턴스 모두 `add_router()` 메서드를 가진다:

```python
from ninja import NinjaAPI, Router

api = NinjaAPI()
first_router = Router()
second_router = Router()
third_router = Router()

@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}

@first_router.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}

@second_router.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}

@third_router.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}

second_router.add_router("l3", third_router)
first_router.add_router("l2", second_router)
api.add_router("l1", first_router)
```

생성되는 엔드포인트:
- `/api/add` -- api 직접
- `/api/l1/add` -- first_router
- `/api/l1/l2/add` -- second_router
- `/api/l1/l2/l3/add` -- third_router

---

## 4. Path(...) URL 파라미터

### 기본 경로 파라미터

Python 포맷 문자열 구문으로 경로 파라미터를 정의한다:

```python
@api.get("/items/{item_id}")
def read_item(request, item_id: int):
    return {"item_id": item_id}
```

타입 어노테이션으로 자동 파싱과 유효성 검증이 수행된다. `item_id: int`로 선언하면 정수가 아닌 값에 대해 검증 오류가 발생한다.

### Django 경로 컨버터

Django의 경로 컨버터 구문을 사용하여 URL 수준에서 타입을 강제할 수 있다:

```python
@api.get("/items/{int:item_id}")
def read_item(request, item_id: int):
    return {"item_id": item_id}
```

잘못된 타입은 404 오류를 반환한다.

### path 컨버터 (슬래시 포함)

```python
@api.get('/dir/{path:value}')
def someview(request, value: str):
    return value
# /dir/some/path/with-slashes -> value = "some/path/with-slashes"
```

### 다중 경로 파라미터

```python
@api.get("/events/{year}/{month}/{day}")
def events(request, year: int, month: int, day: int):
    return {"date": [year, month, day]}
```

### Schema 기반 경로 파라미터

상호 의존적인 경로 파라미터를 스키마로 캡슐화한다:

```python
import datetime
from ninja import Schema, Path

class PathDate(Schema):
    year: int
    month: int
    day: int

    def value(self):
        return datetime.date(self.year, self.month, self.day)

@api.get("/events/{year}/{month}/{day}")
def events(request, date: Path[PathDate]):
    return {"date": date.value()}
```

### 중첩 라우터에서 상위 경로 파라미터 접근

`Path(...)`를 사용하여 상위 라우트의 파라미터를 하위 라우터에서 접근한다:

```python
from ninja import NinjaAPI, Path, Router

api = NinjaAPI()
router = Router()

@api.get("/add/{a}/{b}")
def add(request, a: int, b: int):
    return {"result": a + b}

@router.get("/multiply/{c}")
def multiply(request, c: int, a: int = Path(...), b: int = Path(...)):
    return {"result": (a + b) * c}

api.add_router("add/{a}/{b}", router)
```

생성되는 엔드포인트:
- `/api/add/{a}/{b}` -- add
- `/api/add/{a}/{b}/multiply/{c}` -- multiply (상위의 a, b 접근 가능)

---

## 5. API 버전 관리

### Multiple NinjaAPI Instances

여러 `NinjaAPI` 인스턴스를 생성하여 API 버전을 관리한다:

```python
# api_v1.py
from ninja import NinjaAPI

api = NinjaAPI(version='1.0.0')

@api.get('/hello')
def hello(request):
    return {'message': 'Hello from V1'}
```

```python
# api_v2.py
from ninja import NinjaAPI

api = NinjaAPI(version='2.0.0')

@api.get('/hello')
def hello(request):
    return {'message': 'Hello from V2'}
```

```python
# urls.py
from api_v1 import api as api_v1
from api_v2 import api as api_v2

urlpatterns = [
    path('api/v1/', api_v1.urls),
    path('api/v2/', api_v2.urls),
]
```

각 버전은 독립적인 OpenAPI 문서 페이지를 가진다:
- `http://127.0.0.1/api/v1/docs`
- `http://127.0.0.1/api/v2/docs`

### urls_namespace

여러 `NinjaAPI` 인스턴스를 사용할 때 각 인스턴스는 서로 다른 `version` 또는 `urls_namespace`를 가져야 한다:

```python
api = NinjaAPI(auth=token_auth, urls_namespace='public_api')
api_private = NinjaAPI(auth=session_auth, urls_namespace='private_api')

urlpatterns = [
    path('api/', api.urls),
    path('internal-api/', api_private.urls),
]
```

URL 역방향 해석에서 네임스페이스를 활용한다:

```python
from django.urls import reverse_lazy

# 버전 기반
reverse_lazy("api-2:users")

# 커스텀 네임스페이스 기반
reverse_lazy("private_api:admins")
```

기본 URL 네임스페이스는 `api-` 접두사에 버전을 붙여 자동 생성된다.

---

## 6. 프로젝트 구조

### 권장 디렉토리 구조

```
myproject/
├── myproject/
│   ├── api.py          # 메인 NinjaAPI 인스턴스, 라우터 연결
│   ├── settings.py
│   └── urls.py         # api.urls 포함
├── events/
│   ├── __init__.py
│   ├── api.py          # Router() 정의, 이벤트 엔드포인트
│   └── models.py
├── news/
│   ├── __init__.py
│   ├── api.py          # Router() 정의, 뉴스 엔드포인트
│   └── models.py
└── blogs/
    ├── __init__.py
    ├── api.py          # Router() 정의, 블로그 엔드포인트
    └── models.py
```

### 핵심 패턴

1. **각 앱에 `api.py`**: 앱별로 `Router` 인스턴스와 엔드포인트를 정의한다
2. **메인 `api.py`**: 프로젝트 루트에서 `NinjaAPI` 인스턴스를 생성하고 각 앱의 라우터를 `add_router()`로 연결한다
3. **`urls.py`에서 등록**: `path('api/', api.urls)`로 Django URL 설정에 포함한다

```python
# myproject/api.py
from ninja import NinjaAPI
from events.api import router as events_router

api = NinjaAPI()
api.add_router("/events/", events_router)
api.add_router("/news/", "news.api.router")
api.add_router("/blogs/", "blogs.api.router")
```

```python
# myproject/urls.py
from django.urls import path
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

### 파라미터 자동 감지 규칙

Django Ninja는 함수 파라미터의 위치와 타입으로 소스를 자동 감지한다:

| 조건 | 파라미터 소스 |
|------|-------------|
| URL 경로에 `{param}` 존재 | Path 파라미터 |
| 단순 타입 (int, str, float, bool) | Query 파라미터 |
| Schema/BaseModel 타입 | Request Body |
