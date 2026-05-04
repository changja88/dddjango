# 생태계 레퍼런스

## 1. django-ninja-extra

Django Ninja의 확장 패키지로, 클래스 기반 뷰(api_controller), 권한 시스템, 의존성 주입 등 고급 기능을 제공한다.

### 1.1 설치 및 설정

```bash
pip install django-ninja-extra
```

```python
# settings.py
INSTALLED_APPS = [
    ...,
    'ninja_extra',
]
```

```python
# api.py
from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()

# 함수 기반 뷰도 그대로 사용 가능
@api.get("/hello")
def hello(request):
    return "Hello world"
```

```python
# urls.py
from django.urls import path
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

### 1.2 @api_controller 데코레이터

클래스 기반 API 컨트롤러를 정의한다. URL 프리픽스, 태그, 인증, 권한을 클래스 레벨에서 설정할 수 있다.

```python
from ninja_extra import (
    api_controller,
    ControllerBase,
    http_get,
    http_post,
    http_delete,
)
from ninja_extra.controllers.response import Detail
from ninja_extra import status, pagination
from ninja import ModelSchema
from django.contrib.auth import get_user_model

class UserSchema(ModelSchema):
    class Config:
        model = get_user_model()
        model_fields = ['username', 'email', 'first_name']

@api_controller('/users')
class UsersController(ControllerBase):
    user_model = get_user_model()

    @http_post()
    def create_user(self, user: UserSchema):
        return dict(id=uuid.uuid4())

    @http_get("", response=pagination.PaginatedResponseSchema[UserSchema])
    @pagination.paginate(pagination.PageNumberPaginationExtra, page_size=50)
    def list_user(self):
        return self.user_model.objects.all()

    @http_get('/{user_id}', response=UserSchema)
    def get_user_by_id(self, user_id: int):
        user = self.get_object_or_exception(self.user_model, id=user_id)
        return user

    @http_delete(
        '/{int:user_id}',
        response=Detail(status_code=status.HTTP_204_NO_CONTENT),
    )
    def delete_user(self, user_id: int):
        user = self.get_object_or_exception(self.user_model, id=user_id)
        user.delete()
        return self.create_response('', status_code=status.HTTP_204_NO_CONTENT)

# 컨트롤러 등록
api.register_controllers(UsersController)
```

### 1.3 HTTP 메서드 데코레이터

| 데코레이터 | HTTP 메서드 |
|---|---|
| `@http_get` | GET |
| `@http_post` | POST |
| `@http_put` | PUT |
| `@http_patch` | PATCH |
| `@http_delete` | DELETE |
| `@http_generic` | 여러 메서드 지정 가능 |

```python
from ninja_extra import (
    api_controller,
    http_get, http_post, http_put,
    http_delete, http_patch, http_generic,
)

@api_controller('/items', tags=['Items'])
class ItemController:
    @http_get("/")
    def list_items(self):
        ...

    @http_post("/")
    def create_item(self):
        ...

    @http_put("/{item_id}")
    def update_item(self, item_id: int):
        ...

    @http_patch("/{item_id}")
    def partial_update(self, item_id: int):
        ...

    @http_delete("/{item_id}")
    def delete_item(self, item_id: int):
        ...

    @http_generic("/{item_id}/action", methods=["POST", "PATCH"])
    def item_action(self, item_id: int):
        ...
```

### 1.4 PermissionBase

컨트롤러 레벨과 라우트 레벨에서 권한을 설정한다.

#### 내장 권한 클래스

| 클래스 | 설명 |
|---|---|
| `permissions.AllowAny` | 모든 요청 허용 |
| `permissions.IsAuthenticated` | 인증된 사용자만 허용 |
| `permissions.IsAuthenticatedOrReadOnly` | 인증 사용자는 모두, 비인증은 읽기만 |
| `permissions.IsAdminUser` | 관리자(staff) 사용자만 허용 |

```python
from ninja_extra import permissions, api_controller, http_get, http_post

@api_controller("/posts", permissions=[permissions.IsAuthenticatedOrReadOnly])
class BlogController:
    @http_get("/")
    def list_posts(self):
        return {"posts": ["Post 1", "Post 2"]}

    @http_post("/")
    def create_post(self, request, title: str):
        return {"message": f"Post '{title}' created by {request.user.username}"}
```

#### 커스텀 권한

```python
from ninja_extra import permissions, api_controller, http_get
from django.http import HttpRequest

class HasAPIKey(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, controller):
        api_key = request.headers.get('X-API-Key')
        return api_key == 'your-secret-key'

@api_controller(permissions=[HasAPIKey])
class APIKeyProtectedController:
    @http_get("/protected")
    def protected_endpoint(self):
        return {"message": "Access granted with valid API key"}
```

#### 역할 기반 권한

```python
from ninja_extra import permissions, api_controller, http_get, http_post, http_delete

class HasRole(permissions.BasePermission):
    def __init__(self, required_role: str):
        self.required_role = required_role

    def has_permission(self, request, controller):
        return request.user.has_perm(self.required_role)

@api_controller("/articles", permissions=[permissions.IsAuthenticated])
class ArticleController:
    @http_get("/", permissions=[HasRole("articles.view")])
    def list_articles(self):
        return {"articles": ["Article 1", "Article 2"]}

    @http_post("/", permissions=[HasRole("articles.add")])
    def create_article(self, title: str):
        return {"message": f"Article '{title}' created"}

    @http_delete("/{id}", permissions=[HasRole("articles.delete")])
    def delete_article(self, id: int):
        return {"message": f"Article {id} deleted"}
```

#### 권한 조합 (비트 연산자)

```python
from ninja_extra import permissions, api_controller, http_get

class HasPremiumSubscription(permissions.BasePermission):
    def has_permission(self, request, controller):
        return request.user.has_perm('premium_subscription')

@api_controller("/content")
class ContentController:
    # OR: 인증됨 또는 프리미엄
    @http_get("/basic", permissions=[
        permissions.IsAuthenticated | HasPremiumSubscription()
    ])
    def basic_content(self):
        return {"content": "Basic content"}

    # AND: 인증됨 그리고 프리미엄
    @http_get("/premium", permissions=[
        permissions.IsAuthenticated & HasPremiumSubscription()
    ])
    def premium_content(self):
        return {"content": "Premium content"}

    # NOT: 인증됨 그리고 프리미엄 아님
    @http_get("/non-premium", permissions=[
        permissions.IsAuthenticated & ~HasPremiumSubscription()
    ])
    def non_premium_content(self):
        return {"content": "Content for non-premium users"}
```

#### 객체 레벨 권한

```python
from ninja_extra import permissions, api_controller, http_get
from .models import Post

class IsPostAuthor(permissions.BasePermission):
    def has_object_permission(self, request, controller, obj: Post):
        return obj.author == request.user

@api_controller("/posts")
class PostController:
    @http_get("/{post_id}", permissions=[
        permissions.IsAuthenticated & IsPostAuthor()
    ])
    def get_post(self, request, post_id: int):
        post = self.get_object_or_exception(Post, id=post_id)
        return {"title": post.title, "content": post.content}
```

### 1.5 의존성 주입

django-ninja-extra는 `injector` 패키지를 통한 의존성 주입을 지원한다. 서비스 클래스를 컨트롤러에 주입하여 비즈니스 로직을 분리한다.

```python
from injector import inject
from ninja_extra import api_controller, http_get

# 서비스 클래스
class UserService:
    def get_user_details(self, user_id: int):
        return {"user_id": user_id, "status": "active"}

# 컨트롤러에 서비스 주입
@api_controller('/users', tags=['Users'])
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @http_get('/{user_id}')
    def get_user(self, user_id: int):
        return self.user_service.get_user_details(user_id)
```

#### Injector 모듈 등록

```python
from injector import Module, singleton

class AppModule(Module):
    def configure(self, binder):
        binder.bind(UserService, to=UserService, scope=singleton)
        binder.bind(EmailService, to=EmailService, scope=singleton)
```

```python
# settings.py
INJECTOR_MODULES = [
    'myapp.modules.AppModule',
]
```

## 2. django-ninja-jwt

Django Ninja를 위한 JWT(JSON Web Token) 인증 플러그인이다. `django-ninja-extra`에 의존한다.

### 2.1 설치 및 설정

```bash
pip install django-ninja-jwt
```

```python
# settings.py
INSTALLED_APPS = [
    ...,
    'ninja_jwt',
    'ninja_extra',
]
```

### 2.2 기본 설정 (NinjaJWTDefaultController)

가장 간단한 방법으로 3개의 엔드포인트가 자동 생성된다: `obtain_token`, `refresh_token`, `verify_token`.

```python
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)
```

### 2.3 토큰 발급 테스트

```bash
# 토큰 발급
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "mypassword"}' \
  http://localhost:8000/api/token/pair

# 응답 예시
# {"access": "eyJ...", "refresh": "eyJ..."}
```

### 2.4 커스텀 컨트롤러

기본 컨트롤러를 상속하여 커스텀할 수 있다.

```python
from ninja_extra import api_controller
from ninja_jwt.controller import TokenObtainPairController

@api_controller('token', tags=['Auth'])
class MyCustomController(TokenObtainPairController):
    """obtain_token과 refresh_token만 제공"""
    pass

api.register_controllers(MyCustomController)
```

### 2.5 JWT 인증 클래스 사용

발급된 토큰으로 API를 보호한다.

```python
from ninja_jwt.authentication import JWTAuth
from ninja_extra import api_controller, http_get

@api_controller('/protected', tags=['Protected'], auth=JWTAuth())
class ProtectedController:
    @http_get('/data')
    def get_data(self, request):
        return {"user": request.user.username}
```

## 3. Model Controller (자동 CRUD)

django-ninja-extra의 `ModelControllerBase`를 사용하면 Django 모델로부터 CRUD API를 자동 생성한다.

### 3.1 모델 정의

```python
from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=100)

class Event(models.Model):
    title = models.CharField(max_length=100)
    category = models.OneToOneField(
        Category, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='events',
    )
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.title
```

### 3.2 기본 ModelController 설정

`ModelConfig`만 지정하면 CRUD 엔드포인트가 자동 생성된다.

```python
from ninja_extra import (
    ModelConfig,
    ModelControllerBase,
    api_controller,
    NinjaExtraAPI,
)
from .models import Event

@api_controller("/events")
class EventModelController(ModelControllerBase):
    model_config = ModelConfig(
        model=Event,
    )

api = NinjaExtraAPI()
api.register_controllers(EventModelController)
```

자동 생성되는 엔드포인트:
- `POST /events/` - create
- `GET /events/{id}` - find_one
- `PUT /events/{id}` - update
- `PATCH /events/{id}` - patch
- `DELETE /events/{id}` - delete
- `GET /events/` - list

### 3.3 자동 생성 스키마

ModelController는 모델 필드를 기반으로 Pydantic 스키마를 자동 생성한다.

```python
# 자동 생성되는 스키마 예시
class EventCreateSchema(Schema):
    title: str
    start_date: date
    end_date: date
    category: Optional[int] = None

class EventSchema(Schema):
    id: int
    title: str
    start_date: date
    end_date: date
    category: Optional[int] = None
```

### 3.4 allowed_routes로 라우트 제한

필요한 엔드포인트만 선택적으로 생성한다.

```python
@api_controller("/events")
class EventModelController(ModelControllerBase):
    model_config = ModelConfig(
        model=Event,
        allowed_routes=["list", "find_one"],  # 읽기 전용
    )
```

사용 가능한 라우트 이름: `"create"`, `"find_one"`, `"update"`, `"patch"`, `"delete"`, `"list"`

### 3.5 async 라우트 지원

```python
@api_controller("/events")
class EventModelController(ModelControllerBase):
    model_config = ModelConfig(
        model=Event,
        async_routes=True,
    )
```

### 3.6 패키지 비교

| 기능 | django-ninja (core) | django-ninja-extra | django-ninja-jwt |
|---|---|---|---|
| 함수 기반 뷰 | O | O | - |
| 클래스 기반 컨트롤러 | X | O | - |
| 권한 시스템 | X | O | - |
| 의존성 주입 | X | O | - |
| 자동 CRUD | X | O | - |
| JWT 인증 | X | - | O |
| NinjaExtraAPI 필요 | X | O | O |
