# Django 웹 템플릿 + Django Ninja REST API 동시 구현 구조

## 핵심 원칙

모델과 비즈니스 로직(서비스 레이어)은 공유하고, 프레젠테이션 레이어만 분리한다. Fat Model, Thin View 원칙에 따라 비즈니스 로직을 모델 메서드와 서비스 함수에 집중시키면, 웹 뷰와 API 엔드포인트 모두 동일한 로직을 얇은 레이어로 호출할 수 있다.

## 프로젝트 레이아웃

```
repository_root/
    config/
        __init__.py
        settings/
            __init__.py
            base.py
            local.py
            production.py
            test.py
        urls.py              # 루트 URL: web + api 분기
        wsgi.py
        asgi.py
    apps/
        articles/
            __init__.py
            models.py         # 도메인 모델 (웹/API 공유)
            services.py       # 쓰기 로직 (웹/API 공유)
            selectors.py      # 읽기 로직 (웹/API 공유)
            forms.py          # 웹 전용: ModelForm
            views.py          # 웹 전용: CBV/FBV (TemplateView)
            urls.py           # 웹 전용: URL 패턴
            api.py            # API 전용: Django Ninja Router
            schemas.py        # API 전용: Django Ninja Schema
            templates/
                articles/
                    list.html
                    detail.html
                    create.html
            tests/
                __init__.py
                test_models.py
                test_services.py
                test_views.py
                test_api.py
            admin.py
    manage.py
```

각 도메인 앱 안에서 파일 역할이 명확히 나뉜다:

| 파일 | 역할 | 사용처 |
|------|------|--------|
| `models.py` | 도메인 모델, 검증, 상태 전이 | 웹 + API 공유 |
| `services.py` | 쓰기(Command) 비즈니스 로직 | 웹 + API 공유 |
| `selectors.py` | 읽기(Query) 로직 | 웹 + API 공유 |
| `forms.py` | ModelForm, 폼 검증 | 웹 전용 |
| `views.py` | CBV/FBV, 템플릿 렌더링 | 웹 전용 |
| `urls.py` | 웹 URL 패턴 | 웹 전용 |
| `api.py` | Django Ninja Router, 엔드포인트 | API 전용 |
| `schemas.py` | Django Ninja Schema (입출력) | API 전용 |

## 공유 레이어: 모델 + 서비스

### models.py -- 웹과 API가 공유하는 도메인 모델

```python
from decimal import Decimal

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Article(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="articles",
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.DRAFT,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(title__length__gte=1),
                name="article_title_not_empty",
            ),
        ]

    def __str__(self):
        return self.title

    def publish(self):
        """기사를 발행한다."""
        self.status = self.Status.PUBLISHED
        self.save(update_fields=["status", "updated_at"])
```

### services.py -- 쓰기 로직 (웹 뷰와 API 엔드포인트 모두 호출)

```python
from django.db import transaction
from django.utils import timezone

from apps.articles.models import Article


def article_create(*, title: str, body: str, author) -> Article:
    """기사를 생성한다."""
    article = Article.objects.create(
        title=title,
        body=body,
        author=author,
    )
    return article


def article_publish(*, article: Article) -> Article:
    """기사를 발행하고 알림을 보낸다."""
    with transaction.atomic():
        article.publish()

    transaction.on_commit(
        lambda: _notify_subscribers(article=article)
    )
    return article


def _notify_subscribers(*, article: Article):
    """구독자에게 알림을 보낸다 (부수 효과)."""
    ...
```

### selectors.py -- 읽기 로직 (웹 뷰와 API 엔드포인트 모두 호출)

```python
from django.db.models import QuerySet

from apps.articles.models import Article


def article_list(
    *,
    author=None,
    status: str | None = None,
) -> QuerySet[Article]:
    """필터 조건에 따라 기사 목록을 반환한다."""
    qs = Article.objects.select_related("author")
    if author:
        qs = qs.filter(author=author)
    if status:
        qs = qs.filter(status=status)
    return qs.order_by("-created_at")


def article_detail(*, article_id: int) -> Article:
    """기사 상세를 반환한다."""
    return Article.objects.select_related("author").get(pk=article_id)
```

## 웹 프레젠테이션 레이어 (Template)

### forms.py

```python
from django import forms

from apps.articles.models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body"]
```

### views.py -- 서비스/셀렉터를 호출하는 얇은 뷰

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, ListView

from apps.articles.forms import ArticleForm
from apps.articles.models import Article
from apps.articles.selectors import article_list
from apps.articles.services import article_create


class ArticleListView(ListView):
    paginate_by = 20
    template_name = "articles/list.html"
    context_object_name = "articles"

    def get_queryset(self):
        return article_list(
            status=self.request.GET.get("status"),
        )


class ArticleDetailView(DetailView):
    queryset = Article.objects.select_related("author")
    template_name = "articles/detail.html"
    context_object_name = "article"


class ArticleCreateView(LoginRequiredMixin, CreateView):
    form_class = ArticleForm
    template_name = "articles/create.html"

    def form_valid(self, form):
        article = article_create(
            title=form.cleaned_data["title"],
            body=form.cleaned_data["body"],
            author=self.request.user,
        )
        return redirect("article-detail", pk=article.pk)
```

### urls.py (앱 레벨)

```python
from django.urls import path

from apps.articles.views import (
    ArticleCreateView,
    ArticleDetailView,
    ArticleListView,
)

urlpatterns = [
    path("", ArticleListView.as_view(), name="article-list"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="article-detail"),
    path("create/", ArticleCreateView.as_view(), name="article-create"),
]
```

## API 프레젠테이션 레이어 (Django Ninja)

### schemas.py

```python
from datetime import datetime

from ninja import Schema


class ArticleIn(Schema):
    title: str
    body: str


class ArticleOut(Schema):
    id: int
    title: str
    body: str
    status: str
    author_id: int
    created_at: datetime
    updated_at: datetime
```

### api.py -- 서비스/셀렉터를 호출하는 얇은 엔드포인트

```python
from django.shortcuts import get_object_or_404
from ninja import Router

from apps.articles.models import Article
from apps.articles.schemas import ArticleIn, ArticleOut
from apps.articles.selectors import article_list
from apps.articles.services import article_create, article_publish

router = Router(tags=["articles"])


@router.get("/", response=list[ArticleOut])
def list_articles(request, status: str | None = None):
    return article_list(status=status)


@router.get("/{article_id}/", response=ArticleOut)
def get_article(request, article_id: int):
    return get_object_or_404(Article, pk=article_id)


@router.post("/", response={201: ArticleOut})
def create_article(request, payload: ArticleIn):
    article = article_create(
        title=payload.title,
        body=payload.body,
        author=request.auth,
    )
    return 201, article


@router.post("/{article_id}/publish/", response=ArticleOut)
def publish_article(request, article_id: int):
    article = get_object_or_404(Article, pk=article_id)
    return article_publish(article=article)
```

## 루트 URL 통합

### config/urls.py

```python
from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI

api = NinjaAPI(
    title="My Project API",
    version="1.0.0",
    urls_namespace="api",
)

# 각 앱의 Ninja Router를 등록
from apps.articles.api import router as articles_router

api.add_router("/articles/", articles_router)

urlpatterns = [
    path("admin/", admin.site.urls),

    # 웹 (템플릿) -- /articles/, /articles/1/, ...
    path("articles/", include("apps.articles.urls")),

    # API (Django Ninja) -- /api/articles/, /api/articles/1/, ...
    path("api/", api.urls),
]
```

## 아키텍처 흐름 요약

```
[웹 브라우저]                        [모바일 앱]
     |                                    |
     v                                    v
 views.py (CBV/FBV)                  api.py (Ninja Router)
 forms.py (ModelForm)                schemas.py (Ninja Schema)
 templates/ (HTML)                   JSON 응답
     |                                    |
     +----------------+-------------------+
                      |
                      v
              services.py  (쓰기 로직)
              selectors.py (읽기 로직)
                      |
                      v
                 models.py (도메인 모델)
                      |
                      v
                  Database
```

핵심은 서비스 레이어(`services.py`, `selectors.py`)가 웹 뷰와 API 엔드포인트 사이의 공유 계층 역할을 한다는 점이다. 뷰와 API 엔드포인트는 각각의 입출력 변환(Form/Template vs Schema/JSON)만 담당하고, 비즈니스 로직은 서비스에 위임한다.

## 이 구조의 장점

1. **로직 중복 방지** -- `article_create`를 한 번만 구현하면 웹과 API 모두 사용한다. 비즈니스 규칙 변경 시 한 곳만 수정하면 된다.
2. **테스트 용이** -- 서비스 함수를 단독으로 테스트하면 웹과 API 양쪽의 핵심 로직이 검증된다.
3. **프레젠테이션 독립** -- 웹에서 필요한 컨텍스트 데이터와 API에서 필요한 JSON 스키마를 각각 최적화할 수 있다.
4. **점진적 확장** -- 새로운 프레젠테이션 레이어(GraphQL, CLI 등)를 추가해도 서비스 레이어를 재사용할 수 있다.

---

웹 페이지(템플릿, 정적 파일, 디자인 시스템, TemplateView)의 상세 패턴은 **implementation-django-web** 스킬을 참조하세요.

Django Ninja API 패턴(Schema, Router, 인증, 페이지네이션, 필터링, 에러 처리)의 상세 안내는 **implementation-django-ninja** 스킬을 참조하세요.

헥사고날 아키텍처, CQRS, 이벤트 소싱 등 고급 아키텍처 패턴은 **architecture-implementation-patterns** 스킬을 참조하세요.

REST API 설계 원칙(엔드포인트, 상태 코드, 버저닝)은 **architecture-api** 스킬을 참조하세요.

Python 전용 관용구(타입 힌트, dataclasses, async)는 **implementation-python** 스킬을 참조하세요.
