# Django Ninja API 엔드포인트: Schema와 Router 패턴

모델과 서비스 레이어가 준비되어 있으므로, Django Ninja의 Schema로 요청/응답을 정의하고 Router로 엔드포인트를 구성하는 패턴을 작성한다.

## 1. Schema 정의

### 기본 Schema -- 요청과 응답 분리

요청(In)과 응답(Out) Schema를 분리한다. 응답 Schema에 선언된 필드만 클라이언트에 반환되므로, 민감한 필드가 자동으로 제외된다.

```python
# apps/articles/schemas.py
from ninja import Schema, ModelSchema, Field
from datetime import datetime
from .models import Article


class ArticleIn(Schema):
    title: str
    content: str
    category_id: int


class ArticleOut(Schema):
    id: int
    title: str
    content: str
    author_name: str
    created_at: datetime

    @staticmethod
    def resolve_author_name(obj):
        return f"{obj.author.first_name} {obj.author.last_name}"
```

### ModelSchema -- 모델 기반 자동 생성

모델 필드가 많을 때 `ModelSchema`로 반복을 줄인다. 반드시 `fields`를 명시적으로 나열한다. `'__all__'`은 민감한 데이터 노출 위험이 있으므로 사용하지 않는다.

```python
# apps/articles/schemas.py
from ninja import ModelSchema
from .models import Article


class ArticleOut(ModelSchema):
    author_name: str = ""

    class Meta:
        model = Article
        fields = ["id", "title", "content", "status", "created_at"]

    @staticmethod
    def resolve_author_name(obj):
        return f"{obj.author.first_name} {obj.author.last_name}"
```

### PATCH용 PatchDict

PATCH 요청에서는 `PatchDict`를 사용하여 실제 전송된 필드만 포함하는 딕셔너리를 받는다. 모든 필드를 Optional로 변환할 필요 없이 기존 Schema를 재사용한다.

```python
from ninja import PatchDict


class ArticleUpdate(Schema):
    title: str
    content: str
    category_id: int


@router.patch("/{article_id}", response=ArticleOut)
def update_article(request, article_id: int, payload: PatchDict[ArticleUpdate]):
    article = get_object_or_404(Article, id=article_id)
    for attr, value in payload.items():
        setattr(article, attr, value)
    article.save(update_fields=list(payload.keys()))
    return article
```

### 중첩 Schema와 목록 응답

관계 데이터는 중첩 Schema로 표현한다. QuerySet을 직접 반환하면 자동으로 리스트로 평가된다.

```python
class CategoryOut(Schema):
    id: int
    name: str


class ArticleDetailOut(Schema):
    id: int
    title: str
    content: str
    category: CategoryOut
    author_name: str
    created_at: datetime

    @staticmethod
    def resolve_author_name(obj):
        return f"{obj.author.first_name} {obj.author.last_name}"
```

### resolver 메서드로 계산 필드

모델에 없는 필드를 동적으로 계산한다. `@staticmethod`로 정의하고, `context` 파라미터로 request 객체에 접근할 수 있다.

```python
class ArticleOut(Schema):
    id: int
    title: str
    is_bookmarked: bool = False

    @staticmethod
    def resolve_is_bookmarked(obj, context):
        request = context["request"]
        if not request.user.is_authenticated:
            return False
        return obj.bookmarks.filter(user=request.user).exists()
```

## 2. Router 구성

### 앱별 Router 정의

각 앱의 `api.py`에서 `Router()`를 생성하고 엔드포인트를 등록한다. 서비스 레이어를 호출하여 비즈니스 로직을 위임한다.

```python
# apps/articles/api.py
from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List

from .models import Article
from .schemas import ArticleIn, ArticleOut, ArticleDetailOut
from .services import article_create, article_publish
from .selectors import article_list, article_detail

router = Router(tags=["articles"])


@router.get("/", response=List[ArticleOut])
def list_articles(request, status: str | None = None):
    return article_list(status=status)


@router.get("/{article_id}", response=ArticleDetailOut)
def get_article(request, article_id: int):
    return article_detail(article_id=article_id)


@router.post("/", response={201: ArticleOut})
def create_article(request, payload: ArticleIn):
    article = article_create(
        author=request.user,
        title=payload.title,
        content=payload.content,
        category_id=payload.category_id,
    )
    return 201, article


@router.post("/{article_id}/publish", response=ArticleOut)
def publish_article(request, article_id: int):
    article = get_object_or_404(Article, id=article_id)
    return article_publish(article=article)


@router.delete("/{article_id}", response={204: None})
def delete_article(request, article_id: int):
    article = get_object_or_404(Article, id=article_id)
    article.delete()
    return 204, None
```

### 서비스/셀렉터 레이어 연동

Router의 엔드포인트는 얇게 유지한다. 비즈니스 로직은 서비스 함수에, 읽기 쿼리는 셀렉터에 위임한다. `<entity>_<action>` 네이밍을 따른다.

```python
# apps/articles/services.py
from django.db import transaction
from .models import Article


def article_create(*, author, title: str, content: str, category_id: int) -> Article:
    article = Article.objects.create(
        author=author,
        title=title,
        content=content,
        category_id=category_id,
    )
    return article


def article_publish(*, article: Article) -> Article:
    if article.status != Article.Status.DRAFT:
        from ninja.errors import HttpError
        raise HttpError(409, "Only draft articles can be published.")
    article.status = Article.Status.PUBLISHED
    article.save(update_fields=["status"])
    transaction.on_commit(lambda: notify_subscribers(article=article))
    return article
```

```python
# apps/articles/selectors.py
from .models import Article


def article_list(*, status: str | None = None):
    qs = Article.objects.select_related("author", "category")
    if status:
        qs = qs.filter(status=status)
    return qs.order_by("-created_at")


def article_detail(*, article_id: int):
    return (
        Article.objects
        .select_related("author", "category")
        .get(id=article_id)
    )
```

### NinjaAPI에 라우터 합성

프로젝트의 메인 `api.py`에서 `NinjaAPI` 인스턴스를 생성하고 각 앱의 라우터를 연결한다.

```python
# config/api.py
from ninja import NinjaAPI

api = NinjaAPI(title="My API", version="1.0.0")

api.add_router("/articles/", "apps.articles.api.router")
api.add_router("/users/", "apps.users.api.router")
api.add_router("/categories/", "apps.categories.api.router")
```

```python
# config/urls.py
from django.urls import path
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

### 페이지네이션 적용

목록 엔드포인트에는 페이지네이션을 적용한다. `@paginate` 데코레이터를 사용하면 뷰 함수는 전체 QuerySet을 반환하고, 실제 슬라이싱은 페이지네이터가 처리한다.

```python
from ninja.pagination import paginate, PageNumberPagination


@router.get("/", response=List[ArticleOut])
@paginate(PageNumberPagination, page_size=20)
def list_articles(request, status: str | None = None):
    return article_list(status=status)
```

### 다중 응답 스키마

성공과 에러를 동일 엔드포인트에서 타입 안전하게 처리한다. `return 상태코드, 데이터` 패턴으로 반환한다.

```python
class ErrorOut(Schema):
    message: str


@router.post(
    "/{article_id}/publish",
    response={200: ArticleOut, 409: ErrorOut},
)
def publish_article(request, article_id: int):
    article = get_object_or_404(Article, id=article_id)
    if article.status != Article.Status.DRAFT:
        return 409, {"message": "Only draft articles can be published."}
    return 200, article_publish(article=article)
```

## 3. 에러 처리

모든 API 에러는 RFC 9457 Problem Details 형식으로 반환한다.

```python
# config/api.py
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from django.http import JsonResponse


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""


api = NinjaAPI(title="My API", version="1.0.0")


@api.exception_handler(HttpError)
def handle_http_error(request, exc):
    return JsonResponse(
        ProblemDetail(
            title=str(exc),
            status=exc.status_code,
            detail=str(exc),
            instance=request.path,
        ).model_dump(),
        status=exc.status_code,
        content_type="application/problem+json",
    )
```

## 4. 권장 프로젝트 구조

```
config/
    api.py          # NinjaAPI 인스턴스, add_router() 합성
    urls.py         # path("api/", api.urls)
apps/
    articles/
        __init__.py
        models.py
        schemas.py  # ArticleIn, ArticleOut, ArticleDetailOut
        api.py      # Router(), 엔드포인트 정의
        services.py # article_create, article_publish
        selectors.py# article_list, article_detail
    users/
        __init__.py
        models.py
        schemas.py
        api.py
        services.py
        selectors.py
```

각 앱에 `schemas.py`, `api.py`, `services.py`, `selectors.py`를 배치한다. Schema는 요청/응답 정의, api.py는 Router와 엔드포인트, services.py는 쓰기 로직, selectors.py는 읽기 로직을 담당한다.

---
> **관련 스킬 참조:**
> - [인증과 보안 (HttpBearer, APIKey, SessionAuth)] → **implementation-django-ninja** 스킬 (references/authentication.md)
> - [필터링 (FilterSchema, FilterLookup)] → **implementation-django-ninja** 스킬 (references/input-filtering.md)
> - [async 뷰] → **implementation-django-ninja** 스킬 (references/async-support.md)
> - [테스팅 (TestClient)] → **implementation-django-ninja** 스킬 (references/testing.md)
> - [모델 설계 (Fat Model, TextChoices, Abstract Base Class)] → **implementation-django** 스킬
> - [QuerySet 최적화 (select_related, prefetch_related)] → **implementation-django** 스킬
> - [REST API 설계 원칙 (URL, 상태 코드, 버저닝)] → **architecture-api** 스킬
> - [아키텍처 패턴 (헥사고날, CQRS)] → **architecture-implementation-patterns** 스킬
> - [Python 타입 힌트, async 관용구] → **implementation-python** 스킬
