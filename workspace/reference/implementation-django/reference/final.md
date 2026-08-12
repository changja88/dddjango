# Django 프레임워크 특화 가이드

## P1 Source Sufficiency

| field | value |
|---|---|
| purpose | Django implementation decisions: models, ORM/QuerySet/Manager, service/selector shape, migrations, transactions, settings, caching, security, performance, and legacy DRF maintenance. |
| use when | Concrete Django 5.x implementation, ORM behavior, migration safety, service/selector placement, or existing DRF maintenance is the main concern. |
| exclude/handoff | Do not use as REST contract authority, greenfield API implementation standard, DB isolation authority, TDD methodology source, or pytest mechanics source. |
| core criteria | Follow Django official philosophy and current LTS behavior first; keep model/service/selector responsibilities explicit; use DB constraints and transactions for durable invariants; keep DRF limited to legacy/maintenance/migration contexts. |
| source priority | 1 official Django/DRF/OWASP docs; 2 primary project docs and Django release notes; 3 reputable Django books/styleguides; 4 community anti-pattern material only as secondary guidance. |
| P1 classification | sufficient |

> Django에서만 적용되는 관례, 설계 철학, 코딩 패턴을 정리한 문서.
> 범용 클린코드 원칙(네이밍, SOLID 등)은 `workspace/reference/discipline-cleancode/reference/final.md`, Python 관용구는 `workspace/reference/implementation-python/reference/final.md`에서 다룬다.
> Django 5.x(LTS 5.2) 기준으로 최신 패턴을 기본으로 제시한다.
>
> **출처 약어:**
> - **[DDoc]** Django 공식 문서 (https://docs.djangoproject.com/)
> - **[DDP]** Django Design Philosophies (https://docs.djangoproject.com/en/5.2/misc/design-philosophies/)
> - **[DCS]** Django Coding Style (https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
> - **[TSD]** Two Scoops of Django 3.x (Daniel & Audrey Feldroy)
> - **[DfP]** Django for Professionals (William Vincent)
> - **[TDD]** Test-Driven Development with Python (Harry Percival)
> - **[HS]** HackSoft Django Styleguide (https://github.com/HackSoftware/Django-Styleguide)
> - **[DRF]** Django REST Framework 공식 문서 (https://www.django-rest-framework.org/)
> - **[CP]** Architecture Patterns with Python / Cosmic Python (Harry Percival & Bob Gregory)
> - **[OWASP]** Django Security Cheat Sheet (https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)

---

## 목차

1. [Django 설계 철학](#1-django-설계-철학)
2. [Django 코딩 스타일](#2-django-코딩-스타일)
3. [프로젝트 구조와 앱 설계](#3-프로젝트-구조와-앱-설계)
4. [모델 설계 패턴](#4-모델-설계-패턴)
5. [QuerySet과 Manager 패턴](#5-queryset과-manager-패턴)
6. [뷰 패턴: CBV vs FBV](#6-뷰-패턴-cbv-vs-fbv)
7. [폼과 유효성 검증](#7-폼과-유효성-검증)
8. [REST API 경계와 기존 DRF 유지보수](#8-rest-api-경계와-기존-drf-유지보수)
9. [시그널 사용 가이드라인](#9-시그널-사용-가이드라인)
10. [마이그레이션 베스트 프랙티스](#10-마이그레이션-베스트-프랙티스)
11. [성능 최적화](#11-성능-최적화)
12. [캐싱 전략](#12-캐싱-전략)
13. [보안](#13-보안)
14. [테스트 패턴](#14-테스트-패턴)
15. [미들웨어](#15-미들웨어)
16. [Django와 서비스 레이어 아키텍처](#16-django와-서비스-레이어-아키텍처)
17. [Django 5.x 새 기능](#17-django-5x-새-기능)

---

## 1. Django 설계 철학

Django 공식 문서에 명시된 설계 철학은 모든 Django 코드 작성의 기반이다. **[DDP]**

### 1.1 전체 철학 (Overall)

| 원칙 | 설명 |
|------|------|
| **Loose Coupling** | 프레임워크의 각 계층은 서로에 대해 최소한만 안다. 템플릿은 웹 요청을 모르고, 데이터베이스 계층은 화면 표시를 모른다. |
| **Less Code** | 앱은 최소한의 코드로 작성되어야 하며, 보일러플레이트를 배제한다. Python의 동적 기능(인트로스펙션 등)을 최대한 활용한다. |
| **Quick Development** | 웹 개발의 지루한 측면을 빠르게 처리하는 것이 프레임워크의 존재 이유다. |
| **Don't Repeat Yourself (DRY)** | 모든 고유한 개념과 데이터는 하나의 장소에만 존재해야 한다. 중복은 나쁘고, 정규화가 좋다. |
| **Explicit is Better Than Implicit** | PEP 20의 원칙. "마법"은 그것이 달성하기 어려운 거대한 편의를 제공하면서도 개발자를 혼동시키지 않을 때만 사용한다. |
| **Consistency** | 저수준(코딩 스타일)부터 고수준(사용 경험)까지 일관성을 유지한다. |

### 1.2 모델 철학 (Models) [DDP]

- **모델은 객체의 모든 측면을 캡슐화한다** -- Martin Fowler의 Active Record 패턴을 따른다.
- 데이터와 데이터에 관한 메타정보(사람이 읽는 이름, 기본 정렬 등) 모두 모델 클래스에 정의한다.
- 하나의 모델을 이해하는 데 필요한 모든 정보가 모델 안에 있어야 한다.

### 1.3 데이터베이스 API 철학 (Database API) [DDP]

| 원칙 | 설명 |
|------|------|
| **SQL Efficiency** | SQL 문을 최소한으로 실행하고, 내부적으로 최적화한다. `save()`는 명시적 호출 필요. |
| **Terse, Powerful Syntax** | 최소 구문으로 풍부하고 표현력 있는 문장을 허용한다. 조인은 뒷단에서 자동 수행된다. |
| **Drop Into Raw SQL** | ORM은 지름길이지 끝이 아니다. 커스텀 SQL을 쉽게 작성할 수 있어야 한다. |

### 1.4 URL 설계 철학 (URL Design) [DDP]

- URL은 Python 함수명에 결합되면 안 된다 (Loose Coupling).
- 어떤 URL 설계든 허용할 수 있는 **무한한 유연성**을 제공한다.
- 예쁜 URL을 만드는 것이 못생긴 URL을 만드는 것보다 쉽거나 같아야 한다.
- URL에 파일 확장자를 포함시키지 않는다.

### 1.5 템플릿 시스템 철학 (Template System) [DDP]

- **로직과 표현을 분리한다** -- 템플릿은 표현과 표현 관련 로직만 제어한다.
- **프로그래밍 언어를 발명하지 않는다** -- 분기와 반복 등 표현에 필수적인 기능만 제공한다.
- HTML에 종속되지 않는다 -- 모든 텍스트 기반 형식을 생성할 수 있다.
- 안전과 보안이 기본이다 -- 악의적인 코드 실행을 원천 차단한다.

### 1.6 뷰 철학 (Views) [DDP]

- 뷰 작성은 Python 함수 작성만큼 단순해야 한다 -- 함수로 충분할 때 클래스를 인스턴스화하지 않는다.
- 요청 객체를 전역 변수가 아닌 직접 전달받아 테스트를 쉽게 만든다.
- GET과 POST를 명확히 구분한다.

---

## 2. Django 코딩 스타일

Django 공식 코딩 스타일은 PEP 8을 기반으로 하되, 고유한 규칙을 추가한다. **[DCS]**

### 2.1 포매팅 기본 규칙 [DCS]

- **black** 포매터를 사용한다.
- 코드 줄 길이는 **88자** (black 기준), 문서/주석/독스트링은 **79자**.
- Python은 **4칸 들여쓰기**, HTML 템플릿은 **2칸 들여쓰기**.

### 2.2 임포트 순서 [DCS]

임포트는 다음 그룹 순서로 정렬하며, 그룹 내에서는 알파벳순으로 정렬한다.

```python
# 1. future
from __future__ import annotations

# 2. standard library
import json
from itertools import chain

# 3. third-party
import bcrypt

# 4. Django 컴포넌트
from django.http import Http404
from django.http.response import (
    HttpResponse,
    HttpResponseNotAllowed,
    StreamingHttpResponse,
)

# 5. 로컬 Django 컴포넌트 (한 점 상대 임포트)
from .models import LogEntry

# 6. try/except
try:
    import yaml
except ImportError:
    yaml = None
```

- `isort`를 사용하여 자동 정렬한다.
- **편의 임포트를 사용한다**: `from django.views import View` (O), `from django.views.generic.base import View` (X).
- 여러 점 상대 임포트(`from ...utils import`)를 피하고 절대 임포트를 사용한다.

### 2.3 문자열 포매팅 [DCS]

```python
# 좋은 예: f-string 내에서 단순 속성 접근
f"hello {user}"
f"hello {user.name}"
f"hello {self.user.name}"

# 나쁜 예: f-string 내에서 함수 호출이나 연산
f"hello {get_user()}"                   # 함수 호출 금지
f"you are {user.age * 365.25} days old" # 연산 금지

# 좋은 예: 복잡한 표현은 지역 변수로 분리
user = get_user()
f"hello {user}"

# 번역 대상 문자열에는 f-string을 사용하지 않는다
_("Hello %(name)s") % {"name": user.name}  # O
_(f"Hello {user.name}")                      # X
```

### 2.4 모델 코딩 스타일 [DCS]

```python
class Person(models.Model):
    # 1. 데이터베이스 필드 (all lowercase with underscores)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=40)
    email = models.EmailField(unique=True)

    # 2. 커스텀 Manager
    objects = PersonManager()

    # 3. class Meta
    class Meta:
        verbose_name_plural = "people"
        ordering = ["last_name", "first_name"]

    # 4. __str__ 및 기타 Python 매직 메서드
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # 5. save(), delete()
    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    # 6. get_absolute_url()
    def get_absolute_url(self):
        return reverse("person-detail", kwargs={"pk": self.pk})

    # 7. 커스텀 메서드
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
```

### 2.5 선택지(Choices) 정의 [DCS]

```python
# 순수 인프라 필드(도메인 판정 없음) 또는 기존 관례 프로젝트: TextChoices 자체 선언
class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.DRAFT,
    )

# Django 5.0+ 딕셔너리 구문도 가능
class Shirt(models.Model):
    size = models.CharField(
        max_length=2,
        choices={"S": "Small", "M": "Medium", "L": "Large"},
    )
```

**계층 소유 — 도메인 판정에 쓰이는 값 집합의 단일 출처는 domain_layer의 `StrEnum`이다.** 위 TextChoices 자체 선언은 도메인 판정에 쓰이지 않는 **순수 인프라 필드에 한정**한다 — 도메인 상태를 TextChoices로 선언하면 domain이 판정 시 ORM 타입을 역참조하게 된다(`architecture-ddd` §3.2). 도메인 상태 필드는 domain Enum에서 파생시킨다. 순수 인프라 필드였던 값에 도메인 판정이 처음 생기는 슬라이스에서 파생형으로 전환한다(값 불변이면 `choices` 변경은 DB 무영향). 기존 TextChoices 실물이 여러 곳에 보여도 그것은 규약이 아니라 아직 안 갚은 빚이다 — 값 집합의 배치에 기존 배치는 입력이 아니다(`discipline-houserules` §1.1·§4 — 2026-08-12).

```python
# domain_layer/order/value_object/order_status.py — 단일 출처
class OrderStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"

# driven_layer/django_order/models/order_model.py — 파생 (사람용 라벨(i18n) 필요 시 명시 매핑 병기)
class OrderModel(models.Model):
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name.title()) for s in OrderStatus],
        default=OrderStatus.PENDING.value,  # .value 평탄화 — 아래 참조
    )
```

**`.value` 평탄화**: `default=` 등 마이그레이션이 직렬화하는 자리에 순수 StrEnum **멤버를 직접 두면** Django `EnumSerializer`가 마이그레이션 파일에 **살아있는 enum 참조**(`OrderStatus["PENDING"]` + domain import)를 박는다 — 값 동결 직렬화(`ChoicesSerializer`)는 `models.Choices` 전용이다. domain Enum 파생 시에는 `.value`로 평탄화한다(단일 출처에서의 파생이므로 심볼 소비로 인정). `CheckConstraint`(`check=`)·부분 인덱스의 `Q()` 조건 값도 같은 파생으로 쓴다.

**소비 규율**: `choices`/Enum이 선언된 필드 값의 비교·분기·`.filter()`·대입·`default`는 반드시 심볼로 참조한다 — `.filter(status="pending")` 금지 → `.filter(status=OrderStatus.PENDING)`. 비교는 `==`(`is` 금지 — 필드 값은 plain str로 흐른다). 복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티다(`architecture-ddd` §3.2) — 심볼 치환이 판정 소유를 면책하지 않는다. 승격 판정·리터럴 허용 목록은 `discipline-cleancode` §2.14.

### 2.6 템플릿 코딩 스타일 [DCS]

템플릿 코딩 스타일과 표현 계층 규칙은 `implementation-django-web`(§4)가 소유한다.

### 2.7 뷰 코딩 스타일 [DCS]

```python
# 좋은 예: 첫 번째 매개변수는 반드시 request
def my_view(request, article_id):
    ...

# 나쁜 예
def my_view(req, article_id):   # req가 아닌 request 사용
    ...
```

---

## 3. 프로젝트 구조와 앱 설계

### 3.1 프로젝트 레이아웃 [TSD]

Two Scoops of Django가 권장하는 구조.

```
repository_root/
    .gitignore
    requirements/
        base.txt
        dev.txt
        prod.txt
    config/                  # 프로젝트 설정 (TSD는 config/ 사용 권장)
        __init__.py
        settings/
            __init__.py
            base.py          # 공통 설정
            local.py         # 개발 설정
            production.py    # 운영 설정
            test.py          # 테스트 설정
        urls.py
        wsgi.py
        asgi.py
    apps/
        users/
            __init__.py
            models.py
            views.py
            urls.py
            forms.py
            services.py      # 서비스 레이어 (HS 패턴)
            selectors.py     # 셀렉터 (HS 패턴)
            tests/                       # 의미군으로 분리(평면 나열 금지); 조직 규칙은 implementation-test §4.2 소유
                __init__.py
                unit/
                integration/
            admin.py
        orders/
            ...
    manage.py
    docker-compose.yml
    Dockerfile
```

> 테스트 디렉터리 조직(`unit`/`integration`/`e2e` 의미군 분리, 디렉터리별 conftest)은 `implementation-test` §4.2가 소유한다. 위 `tests/`는 앱별 배치 시의 형태 예시이며, 테스트 파일을 한 디렉터리에 평면으로 나열하지 않는다.

> dddjango가 *생성하는 코드*의 구체 표준 파일트리는 `discipline-houserules` 스킬이 소유한다(표준 트리는 그 `reference/final.md`) — §3.1의 설정 분할·앱 단위 조직을 토대로 구체화한 표준이며, 생성 코드 배치 권위는 그 문서가 갖는다. 여기 §3.1은 그 표준의 배경이다.

### 3.2 앱 분리 기준 [TSD]

```python
# 좋은 예: 앱은 하나의 응집된 도메인 개념에 대응
# users/ -- 사용자 관리
# orders/ -- 주문 관리
# products/ -- 상품 관리

# 나쁜 예: 모든 것이 하나의 앱에
# core/ -- 사용자, 주문, 상품, 결제 전부 포함
# api/  -- 모든 API 엔드포인트를 하나의 앱에
```

- 앱 이름은 **간결한 복수형 단어** 사용: `users`, `orders`, `payments`.
- 한 문장으로 앱의 목적을 설명할 수 없다면 분리가 필요하다.
- 앱 간 순환 의존이 생기면 설계를 재검토한다.

### 3.3 설정(Settings) 분리 [TSD] [DfP]

```python
# config/settings/base.py
import environ

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env()

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

# config/settings/local.py
from .base import *  # noqa: F401,F403

DEBUG = True
INSTALLED_APPS += ["debug_toolbar"]

# config/settings/production.py
from .base import *  # noqa: F401,F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

- **비밀 정보는 절대 코드에 하드코딩하지 않는다** -- `django-environ` 또는 `python-decouple`로 환경 변수에서 읽는다.
- `.env` 파일은 `.gitignore`에 추가한다.

### 3.4 settings 접근 시 주의사항 [DCS]

```python
# 나쁜 예: 모듈 최상위에서 settings 접근
from django.conf import settings
from django.urls import get_callable

default_view = get_callable(settings.FOO_VIEW)  # 임포트 시점에 실행됨

# 좋은 예: 함수/메서드 내에서 지연 접근
from django.conf import settings

def get_default_view():
    from django.urls import get_callable
    return get_callable(settings.FOO_VIEW)
```

모듈 임포트 시점에 settings를 사용하면 `settings.configure()`를 통한 수동 설정이 불가능해진다. **[DCS]**

---

## 4. 모델 설계 패턴

### 4.1 Fat Model, Thin View 원칙 [TSD]

비즈니스 로직은 뷰가 아닌 모델(또는 서비스 레이어)에 둔다. Two Scoops of Django는 이를 **"Fat Models, Utility Modules, Thin Views, Stupid Templates"**로 정리한다.

```python
# 나쁜 예: 뷰에 비즈니스 로직 집중
class OrderView(View):
    def post(self, request):
        order = Order.objects.get(pk=request.POST["order_id"])
        if order.total > 100:
            order.discount = order.total * 0.1
        order.status = "confirmed"
        order.save()
        send_mail("Order confirmed", ..., [order.user.email])
        return redirect("order-detail", pk=order.pk)

# 좋은 예: 모델에 비즈니스 로직 캡슐화
class Order(models.Model):
    # ... fields ...

    def confirm(self):
        """주문을 확정하고 할인을 적용한다."""
        if self.total > 100:
            self.discount = self.total * Decimal("0.1")
        self.status = self.Status.CONFIRMED
        self.save(update_fields=["discount", "status"])
        self.send_confirmation_email()

    def send_confirmation_email(self):
        send_mail("Order confirmed", ..., [self.user.email])

# 뷰는 얇게
class OrderConfirmView(View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order.confirm()
        return redirect("order-detail", pk=order.pk)
```

단, 모델이 2000줄 이상으로 비대해지면 서비스 레이어 분리를 검토한다 (16장 참조).

### 4.2 모델 상속 패턴 [DDoc]

Django는 세 가지 모델 상속을 제공한다.

#### Abstract Base Class (추상 베이스 클래스) -- 권장

```python
# 좋은 예: 공통 필드를 추상 클래스로 추출
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # 테이블을 생성하지 않음

class Article(TimeStampedModel):
    title = models.CharField(max_length=200)
    body = models.TextField()
    # created_at, updated_at 자동 상속
```

- 테이블을 생성하지 않아 조인 비용이 없다.
- 여러 모델에서 공통 필드를 재사용할 때 가장 적합하다.

#### Multi-table Inheritance -- 주의해서 사용

```python
# 주의: 각 모델마다 별도 테이블 생성 + 암묵적 OneToOneField
class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

class Restaurant(Place):  # place_ptr 자동 생성
    serves_pizza = models.BooleanField(default=False)
```

- 조회 시 자동으로 JOIN이 발생하여 성능 저하 가능.
- 대부분의 경우 **Abstract Base Class + 명시적 ForeignKey**가 더 낫다. **[TSD]**

#### Proxy Model -- Python 레벨 동작 변경

```python
class Order(models.Model):
    status = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class ExpensiveOrder(Order):
    """고가 주문만 필터링하는 프록시 모델."""
    class Meta:
        proxy = True

    objects = ExpensiveOrderManager()

    def apply_premium_discount(self):
        self.amount *= Decimal("0.95")
        self.save(update_fields=["amount"])
```

- 테이블 구조를 변경하지 않고 Python 레벨 동작(매니저, 메서드)만 변경한다.
- 기존 테이블 위에 다른 인터페이스를 제공할 때 유용하다.

### 4.3 필드 선택 가이드 [DDoc]

```python
# 나쁜 예: BooleanField 남발로 상태 폭발
class Task(models.Model):
    is_started = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    # is_started=True, is_completed=True, is_cancelled=True 같은
    # 불가능한 상태 조합이 가능

# 좋은 예: TextChoices로 상태를 하나의 필드에 표현
class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        STARTED = "started", "Started"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
    )
```

- `CharField` + `TextChoices`는 DB에서 직접 읽을 때 가독성이 좋다.
- 단 이 `Status`가 도메인 판정(전이·terminal)에 쓰이면 §2.5 계층 소유대로 domain Enum 파생으로 선언한다.
- `IntegerChoices`는 저장 공간이 약간 효율적이나, 쿼리 성능 차이는 거의 없다. **[DDoc]**
- `JSONField`는 스키마 없는 데이터에만 사용하고, 구조화된 데이터에는 정규 필드를 사용한다.
- `DecimalField`를 금액에 사용하고, `FloatField`는 피한다.

### 4.4 모델 유효성 검증 [DDoc]

```python
class Event(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        """모델 레벨 교차 필드 유효성 검증."""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": "종료일은 시작일 이후여야 합니다."}
            )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="event_end_after_start",
            ),
        ]
```

- `clean()` 메서드로 Python 레벨 검증을 수행한다.
- `CheckConstraint`로 데이터베이스 레벨 제약도 함께 건다 (이중 방어).
- `full_clean()`은 `save()` 시 자동 호출되지 않으므로, 폼이나 Serializer를 통해 호출되도록 한다.

---

## 5. QuerySet과 Manager 패턴

### 5.1 Custom Manager와 QuerySet [DDoc] [TSD]

```python
class ArticleStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=ArticleStatus.PUBLISHED)  # 소비 규율(§2.5): 리터럴 아닌 심볼

    def by_author(self, user):
        return self.filter(author=user)

    def recent(self):
        return self.order_by("-published_at")


class ArticleManager(models.Manager):
    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class Article(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=ArticleStatus)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField(null=True)

    # 방법 1: Manager + QuerySet 분리
    objects = ArticleManager()

    # 방법 2: QuerySet.as_manager() 사용 (더 간결)
    # objects = PublishedQuerySet.as_manager()
```

- **QuerySet 메서드로 체이닝을 가능하게 한다**: `Article.objects.published().by_author(user).recent()`
- `as_manager()`를 사용하면 별도의 Manager 클래스 없이 QuerySet을 매니저로 승격시킬 수 있다.
- Manager에서 `get_queryset()`을 오버라이드하여 기본 필터를 적용할 때는 주의한다 -- 관리자 페이지에서 예상과 다르게 동작할 수 있다.

### 5.2 QuerySet 최적화 필수 패턴 [DDoc]

```python
# 나쁜 예: N+1 문제 -- 각 book마다 author를 별도 쿼리
books = Book.objects.all()
for book in books:
    print(book.author.name)  # N번의 추가 쿼리

# 좋은 예: select_related -- ForeignKey/OneToOne에 SQL JOIN 사용
books = Book.objects.select_related("author").all()
for book in books:
    print(book.author.name)  # 추가 쿼리 없음 (1번의 JOIN 쿼리)

# 좋은 예: prefetch_related -- ManyToMany/역참조에 별도 쿼리 + Python 조인
books = Book.objects.prefetch_related("tags").all()
for book in books:
    print(list(book.tags.all()))  # 2번의 쿼리 (books + tags IN (...))

# 좋은 예: Prefetch 객체로 커스텀 쿼리셋 사용
from django.db.models import Prefetch

books = Book.objects.prefetch_related(
    Prefetch(
        "reviews",
        queryset=Review.objects.filter(rating__gte=4).order_by("-created_at"),
        to_attr="top_reviews",  # list로 캐싱
    )
)
```

**선택 기준:**
| 관계 유형 | 사용할 메서드 |
|-----------|--------------|
| ForeignKey, OneToOneField | `select_related()` |
| ManyToManyField, 역참조 ForeignKey | `prefetch_related()` |
| 조건부 프리페치 | `Prefetch()` 객체 |

### 5.3 only(), defer(), values() [DDoc]

```python
# only(): 지정한 필드만 로드 (나머지는 지연 로드)
users = User.objects.only("id", "username", "email")

# defer(): 지정한 필드를 지연 로드 (나머지는 즉시 로드)
articles = Article.objects.defer("body")  # 큰 텍스트 필드 지연

# values(): 딕셔너리 리스트 반환 (모델 인스턴스가 아님)
stats = Order.objects.values("status").annotate(count=Count("id"))

# values_list(): 튜플 리스트 반환
emails = User.objects.values_list("email", flat=True)
```

- `only()`/`defer()`는 대용량 텍스트나 변환 비용이 큰 필드에 효과적이다.
- **프로파일링 없이 공격적으로 사용하지 않는다** -- DB는 대부분의 비텍스트 데이터를 어차피 디스크에서 읽는다. **[DDoc]**
- `values()` 후에 `only()`/`defer()`를 호출하면 `TypeError`가 발생한다.

### 5.4 annotate()와 aggregate() [DDoc]

```python
from django.db.models import Count, Avg, F, Q

# aggregate(): 전체 QuerySet에 대한 집계값 반환 (딕셔너리)
result = Book.objects.aggregate(
    avg_price=Avg("price"),
    total=Count("id"),
)
# {'avg_price': Decimal('25.50'), 'total': 150}

# annotate(): 각 객체에 계산 필드 추가
authors = Author.objects.annotate(
    book_count=Count("book"),
    avg_rating=Avg("book__reviews__rating"),
).filter(book_count__gte=5)

# alias(): 최종 결과에 포함하지 않으면서 필터/정렬에 사용 (Django 3.2+)
authors = Author.objects.alias(
    book_count=Count("book"),
).filter(book_count__gte=5)
```

- `annotate()`와 `filter()`의 순서가 결과에 영향을 준다 -- 교환 법칙이 성립하지 않는다. **[DDoc]**
- 최종 결과에 불필요한 계산 필드가 있으면 `alias()`를 사용하여 DB 부담을 줄인다.

### 5.5 bulk 연산 [DDoc]

```python
# 나쁜 예: 루프 내에서 개별 save()
for item in items:
    item.price *= 1.1
    item.save()  # N번의 UPDATE

# 좋은 예: bulk_update()
for item in items:
    item.price *= 1.1
Product.objects.bulk_update(items, ["price"], batch_size=500)

# 좋은 예: bulk_create()
Product.objects.bulk_create(
    [Product(name=name) for name in product_names],
    batch_size=500,
)

# 좋은 예: update()로 DB 레벨 일괄 수정
Product.objects.filter(category="books").update(
    price=F("price") * 1.1
)
```

---

## 6. 뷰 패턴: CBV vs FBV

서버 렌더링 화면의 뷰(CBV/FBV 선택, Generic CBV, Mixin, FBV 작성)는 표현 계층이므로 `implementation-django-web`(§2)가 소유한다. JSON API endpoint의 라우팅/스키마는 `implementation-django-ninja`, REST 계약은 `architecture-api`가 소유한다. 이 문서(코어)는 뷰가 호출하는 service/selector 경계(§16)만 다룬다.

---

## 7. 폼과 유효성 검증

웹 폼(Form/ModelForm 작성, 검증 순서, 커스텀 validator)은 표현 계층이므로 `implementation-django-web`(§6)가 소유한다. 다만 form과 model이 공유하는 durable invariant·validator는 model/DB 경계에서도 보장한다(§4 모델 설계). 도메인 규칙 자체는 `architecture-ddd`가 소유한다.

---

## 8. REST API 경계와 기존 DRF 유지보수

신규 REST API의 리소스 계약, HTTP 상태 코드, 오류 응답, pagination, versioning, idempotency는 Django 모델/ORM 구현 문제가 아니라 API 계약 문제로 먼저 다룬다. dddjango runtime에서는 greenfield endpoint 구현의 기본 경로를 Django Ninja Router/Schema로 두며, 이 문서의 DRF 내용은 기존 DRF 코드 유지보수, 레거시 migration review, 또는 이미 DRF를 표준으로 채택한 프로젝트 안에서만 적용한다.

신규 코드에서 DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`를 기본 권장안처럼 제시하지 않는다. 기존 DRF surface를 다룰 때도 도메인 규칙은 serializer/viewset에 흩뿌리지 말고 모델 메서드, service, selector, database constraint 같은 Django-side boundary에 둔다.

### 8.1 기존 DRF Serializer 설계 [DRF]

```python
# 좋은 예: 읽기/쓰기 Serializer 분리
class ArticleListSerializer(serializers.ModelSerializer):
    """목록 조회용 -- 최소 필드."""
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title", "author_name", "published_at"]

class ArticleDetailSerializer(serializers.ModelSerializer):
    """상세 조회/수정용 -- 전체 필드."""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title", "body", "author", "tags", "created_at", "updated_at"]

class ArticleCreateSerializer(serializers.ModelSerializer):
    """생성용 -- 쓰기 필드만."""
    class Meta:
        model = Article
        fields = ["title", "body", "category"]

    def validate_title(self, value):
        if Article.objects.filter(title=value).exists():
            raise serializers.ValidationError("이미 존재하는 제목입니다.")
        return value
```

- 기존 DRF 코드에서는 목록/상세/생성/수정 시나리오마다 Serializer를 분리하면 보안과 성능 모두 개선된다.
- `fields = "__all__"` 을 피한다 -- ModelForm과 같은 이유.
- `source` 파라미터로 모델 필드명과 API 필드명을 분리할 수 있다.
- 검증이 serializer에만 갇히면 다른 entry point에서 불변식이 깨질 수 있다. 여러 entry point가 공유하는 규칙은 모델, service, DB constraint로 올린다.

### 8.2 기존 DRF ViewSet과 Router [DRF]

```python
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related("author").prefetch_related("tags")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return ArticleListSerializer
        if self.action == "create":
            return ArticleCreateSerializer
        return ArticleDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        article = self.get_object()
        article.publish()
        return Response({"status": "published"})

# urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("articles", ArticleViewSet)
urlpatterns = router.urls
```

- 기존 DRF 코드에서는 `get_serializer_class()`를 오버라이드하여 액션별 Serializer를 분리한다.
- `@action`에 `permission_classes`를 별도 지정할 수 있다.
- `DefaultRouter`를 사용하면 URL 패턴이 자동 생성된다.
- viewset은 HTTP adapter다. transaction owner, external side effect timing, domain state transition은 명시적인 model/service boundary로 빼서 재사용 가능하게 둔다.

### 8.3 Permission 패턴 [DRF]

```python
from rest_framework.permissions import BasePermission

class IsAuthorOrReadOnly(BasePermission):
    """작성자만 수정/삭제 가능, 나머지는 읽기만."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
```

- 전역 기본 permission은 `settings.py`의 `DEFAULT_PERMISSION_CLASSES`에 설정.
- ViewSet 레벨에서 `permission_classes`로 오버라이드.
- 객체 레벨 권한은 `has_object_permission()`에서 처리.

### 8.4 Pagination 설정 [DRF]

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# 커스텀 페이지네이션
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000
```

- Generic views/ViewSet에서는 자동 적용된다.
- `APIView`를 직접 사용하면 수동으로 페이지네이션을 호출해야 한다.

### 8.5 기존 DRF API 버전 관리 [DRF]

```python
# settings.py -- Accept Header 방식 (DRF 공식 권장)
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.AcceptHeaderVersioning",
    "DEFAULT_VERSION": "1.0",
    "ALLOWED_VERSIONS": ["1.0", "2.0"],
}

# 또는 URL Path 방식 (가장 흔한 실용적 선택)
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}

# urls.py
urlpatterns = [
    path("api/v1/", include("apps.api.v1.urls")),
    path("api/v2/", include("apps.api.v2.urls")),
]

# 뷰에서 버전 확인
class ArticleViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.request.version == "2.0":
            return ArticleV2Serializer
        return ArticleV1Serializer
```

- 기존 DRF 프로젝트에서 **AcceptHeaderVersioning**은 URL을 깔끔하게 유지하며 일반적으로 best practice로 간주된다 (DRF 공식 문서). 단, 프로젝트 요구에 따라 URLPathVersioning 등 다른 방식도 적합할 수 있다. **[DRF]**
- **URLPathVersioning**은 가장 직관적이고 널리 사용된다.
- 버전 간 호환성 유지를 위해 필드 추가는 허용하되, 기존 필드 삭제/변경은 새 버전에서만 수행한다.

---

## 9. 시그널 사용 가이드라인

시그널은 Django에서 가장 논쟁적인 기능 중 하나다. **올바른 사용 시나리오를 명확히 알아야 한다.**

### 9.1 시그널을 사용해야 하는 경우 [DDoc]

```python
# 좋은 예 1: 서드파티 라이브러리 모델에 후크 (코드를 직접 수정 불가)
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# 좋은 예 2: 순환 의존 방지
# app_a가 app_b에 의존하는데, app_b에서 app_a의 동작을 트리거해야 할 때
# app_b는 시그널을 보내고, app_a는 리시버를 연결한다.
```

**시그널이 적절한 경우:**
- 제어할 수 없는 서드파티 모델에 반응할 때
- 순환 의존을 만들지 않고 앱 간 통신이 필요할 때
- 많은 수의 모델에 같은 핸들러를 일괄 적용할 때

### 9.2 시그널을 피해야 하는 경우 (안티패턴) [HS]

```python
# 나쁜 예: 같은 앱 내에서 시그널 사용 -- 직접 호출이 더 명확
@receiver(post_save, sender=Order)
def send_order_email(sender, instance, created, **kwargs):
    if created:
        send_confirmation_email(instance)

# 좋은 예: save() 오버라이드 또는 서비스 함수에서 직접 호출
class Order(models.Model):
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            send_confirmation_email(self)

# 또는 서비스 레이어에서
def order_create(*, user, items):
    order = Order.objects.create(user=user)
    order.add_items(items)
    send_confirmation_email(order)
    return order
```

**시그널을 피해야 하는 경우:**
- 두 컴포넌트가 이미 결합되어 있을 때 -- 시그널은 진정한 디커플링이 아닌 암묵적 결합만 만든다.
- `save()`/`delete()` 오버라이드로 충분할 때.
- `request_started`/`request_finished`는 미들웨어로 대체 가능.
- 시그널은 **동기적**으로 실행되며, 예외가 발생하면 트리거한 함수로 전파된다.

---

## 10. 마이그레이션 베스트 프랙티스

### 10.1 기본 원칙 [DDoc] [TSD]

```python
# 마이그레이션을 작게 유지한다
# sqlmigrate로 실제 SQL을 확인한다
python manage.py sqlmigrate myapp 0002

# 마이그레이션 파일은 반드시 버전 관리에 포함한다
# .gitignore에 migrations/를 추가하지 않는다
```

### 10.2 데이터 마이그레이션 — 금지 [DDoc]

**`migrations/` 에는 `makemigrations` 가 생성한 것만 둔다.** 사람이 `RunPython`/`RunSQL` 로 데이터를 채우는 마이그레이션 파일을 만들지 않는다. 마이그레이션은 「돌았다 / 안 돌았다」 두 상태뿐이라, §11.2 가 대형 backfill 에 요구하는 넷 — 배치 크기·pause 정책, 실패 배치의 멱등 재실행, 진행률·오류율 모니터링, 부분 완료 시 rollback/forward-fix 결정 — 을 구조적으로 하나도 만족시키지 못한다.

대량 데이터 채우기는 파일의 자리 문제가 아니라 **배포 절차의 한 «단계»** 다 — Expand → **Backfill** → Contract(§11.1). Backfill 코드는 트리 밖 저장소 루트 `scripts/` 에 둔다(일회성 — 규정하지 않는다). 스키마 변경과 «순서»가 묶인 소량 정리(NOT NULL 을 걸기 전 NULL 채움 등)도 같은 3단계로 사람이 배포 절차에서 순서를 관리한다 — 마이그레이션 파일 하나로 접지 않는다.

아래는 «이렇게 하지 않는다»의 반례다 — 상한 없는 루프가 한 트랜잭션 안에서 전 행을 건마다 저장한다(100만 행 = 100만 `.save()`).

```python
# ✗ 금지 — makemigrations 가 만들지 않은 손 편집 데이터 마이그레이션
def forward_func(apps, schema_editor):
    User = apps.get_model("users", "User")
    for user in User.objects.filter(display_name=""):   # 상한 없는 루프
        user.display_name = user.username
        user.save(update_fields=["display_name"])
```

- squash 정정: 데이터 마이그레이션은 기본값(`elidable=False`)에서 `squashmigrations` 때 **보존되며, 대신 그 지점에서 최적화가 끊긴다.** 지워지는 것은 `elidable=True` 를 명시했을 때뿐이다.

### 10.3 무중단(Zero-Downtime) 마이그레이션 [DfP]

```python
# 나쁜 예: NOT NULL 컬럼 추가와 동시에 배포
# -> 구버전 코드가 INSERT할 때 새 컬럼을 모르므로 제약 위반

# 좋은 예: 3단계 배포
# 1단계: NULL 허용 컬럼 추가 + 배포
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name="order",
            name="tracking_number",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]

# 2단계: 데이터 채우기 + NOT NULL로 변경
# 3단계: 구버전 코드 제거
```

- 대형 테이블에서는 락 시간을 최소화하기 위해 마이그레이션을 작은 단위로 분할한다.
- PostgreSQL에서는 `django-pg-zero-downtime-migrations` 같은 도구를 고려한다.
- `AddIndex`는 PostgreSQL에서 `CREATE INDEX CONCURRENTLY`를 사용하도록 설정할 수 있다.

### 10.4 이미 이주가 결정된 뒤의 마이그레이션 이력 보존 [TSD] [DfP]

기존 Django 앱(이미 `0001_initial`·`db_table`·`label`을 가진 앱)이 판정·불변식을
새로 소유해 표준 4계층 구조로 **이주가 이미 결정된 뒤**, 그 *마이그레이션 이력*을
파괴 없이 보존하는 메커니즘이다. *언제* 이주하느냐(판정 소유 기준)는 여기 범위가
아니라 `architecture-ddd` §3.2가 정한다 — 여기서는 결정된 이주를 *어떻게* 이력
파괴 없이 수행하느냐(HOW)만 다룬다. 핵심 함정: 앱을 `driven_layer/django_<bounded_context>/`로
옮기며 ORM 클래스를 `<Name>Model`로 바꾸면 기본 테이블명(`<label>_<modelname>`)이
달라져, 코더가 기존 `0001`을 *재작성*(fresh `initial`)하기 쉽다. 그러면 이미
`0001_initial`을 적용한 기존 DB에서 그 마이그레이션이 skip되어 테이블이 안 생기거나
후속 마이그레이션과 어긋난다(이력 불변 위반).

```python
# 1) 앱을 driven_layer/django_<bounded_context>/로 옮긴다 — AppConfig.name 은 새 점경로지만
#    label 은 기존 값을 유지한다(이력은 (label, migration) 키로 추적되므로 label 이
#    바뀌면 기존 0001 적용 기록과 끊긴다. import 점경로만 바뀌는 것은 무해).
# driven_layer/django_catalog/apps.py
class CatalogConfig(AppConfig):
    name = "application.catalog.driven_layer.django_catalog"  # 새 점경로
    label = "catalog"                                        # 기존 label 유지

# 2) ORM 클래스명은 표준상 <Name>Model 이 되지만 테이블명은 기존 것을 명시 보존한다.
# driven_layer/django_catalog/models/product_model.py
class ProductModel(models.Model):          # 기존 class Product 에서 rename
    class Meta:
        db_table = "catalog_product"       # 기존 테이블명 — 클래스 rename 이 바꾸지 못하게

# 3) 기존 0001_initial 은 불변(재작성·삭제 금지). 클래스 rename 은 새 0002 에서
#    state-only 로 반영한다 — database_operations=[] 라 실제 DDL 이 없어 "0001 불변"과
#    양립한다. 단 0001 의 CreateModel 에는 db_table 이 없어 state 의 기본 테이블명이
#    클래스 rename 으로 catalog_productmodel 로 재계산되므로, AlterModelTable 을 state 에
#    함께 넣어 실제 db_table(catalog_product)과 맞춘다 — 아니면 makemigrations --check 가
#    드리프트(AlterModelTable)를 보고한다.
# migrations/0002_rename_product_to_productmodel.py
class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameModel("Product", "ProductModel"),
                migrations.AlterModelTable(name="productmodel", table="catalog_product"),
            ],
            database_operations=[],        # db_table 불변 → 실제 DDL 없음
        ),
    ]
```

- `--fake-initial`은 이 경로의 기본 도구가 아니다 — 이미 `0001_initial`이 *적용된*
  기존 앱(label 재사용)에서는 no-op이다(skip할 0001이 없다). 마이그레이션 기록이
  *전무한* legacy 앱을 처음 편입할 때(테이블은 있으나 `django_migrations`에 행이 없을
  때)에만 조건부로 쓴다.
- 검증: `python manage.py makemigrations --check`로 드리프트가 0인지(미생성
  마이그레이션 없음) 확인하고, `python manage.py sqlmigrate <app> 0002`로 0002가 **DDL을
  발행하지 않는지**(state-only) 확인한다 — DDL이 찍히면 db_table 보존이 빠진 것이다.
- **이주 완료 = 옛 루트 `<app>/` 통째 삭제**(`git rm -r <app>/`): 새 경로가 `0001`을
  보존하므로 옛 루트 앱 패키지·`migrations/`를 남기지 않는다. `MIGRATION_MODULES`로 옛 루트
  `<app>.migrations`를 가리키는 잔존 핀도 두지 않는다(새 경로 단일 소유) — 옛 루트가 남으면
  앱이 두 곳에 존재하는 미완 이주(`discipline-houserules` §0 배타성)다. *왜* — step 1의
  "옮긴다(move)"가 옛 루트 소멸을 함의하나, 명시 안 하면 코더가 move를 copy로 떨어뜨려(새 트리만
  만들고 옛 루트 git 방치) 앱이 두 곳에 남는다.
- 신규 모델의 db_table 규약(`<app_label>_<entity_snake>`·`Model` 제거·snake)은
  `discipline-houserules` §4가 정한다(결정적 백스톱 `check-db-table.py`). §10.4는 그와
  별개로 **이미 적용된** 기존 테이블명을 *보존*하는 경로다 — 이주 결과 테이블명이 신규
  규약과 우연히 같든(`catalog_product`) legacy 그대로든(`tbl_product`) 이력 보존이
  우선이다. 백스톱 `check-db-table.py`는 db_table **존재**만 보고 값 형태는 보지 않으므로,
  이주가 신규 파일로 떨어져도 보존 db_table을 *명시*했으면(§10.4가 요구하는 그대로) 통과한다
  — 보존명이 규약(`<app_label>_<entity_snake>`)과 달라도 무방.
- **historical value 리터럴 동결**: 마이그레이션 파일 안의 choices·상태·default 값은
  살아있는 도메인 Enum을 참조하지 않는다 — Enum 변경이 과거 이력의 의미를 소급 변경하면
  안 된다(위 "이력 보존"과 동형 원리). 모델 `default=`를 `.value`로 평탄화하면(§2.5)
  makemigrations가 리터럴로 동결한다; StrEnum 멤버를 직접 두면 `EnumSerializer`가 산 참조
  (`OrderStatus["PENDING"]` + domain import)를 직렬화하므로 금지. 수기 데이터
  마이그레이션에서도 Enum import 대신 리터럴을 쓴다.

---

## 11. 성능 최적화

### 11.1 N+1 문제 탐지와 해결 [DDoc]

아래 profiler는 탐색에 사용할 수 있지만 query-count 테스트는 승인된 성능 계약과 독자 production
failure가 중앙 입장 심사에서 `add/update`인 뒤에만 작성한다. 미입장 상태에서는 debug toolbar·silk·
nplusone으로 관찰하고 exact query-count test를 만들지 않는다.

```python
# 탐지 도구
# 1. django-debug-toolbar -- 개발 환경에서 쿼리 수 실시간 확인
# 2. django-silk -- 프로파일링 미들웨어
# 3. nplusone -- N+1 쿼리 자동 탐지 및 경고
# 4. assertNumQueries -- 테스트에서 쿼리 수 검증

# 테스트에서 쿼리 수 검증
from django.test import TestCase

class ArticleTestCase(TestCase):
    def test_article_list_query_count(self):
        """목록 조회가 일정 쿼리 수 이내인지 검증."""
        self._create_test_articles(count=50)
        with self.assertNumQueries(2):  # articles + authors
            list(Article.objects.select_related("author").all())
```

### 11.2 데이터베이스 인덱스 전략 [DDoc]

```python
class ArticleStatus(models.TextChoices):  # module-level — Meta 스코프에서도 참조 가능(§2.5 소비 규율)
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)       # unique=True가 인덱스 생성
    status = models.CharField(max_length=20, choices=ArticleStatus, db_index=True)  # 단일 인덱스
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # FK에 자동 인덱스
    published_at = models.DateTimeField(null=True)
    category = models.CharField(max_length=50)

    class Meta:
        indexes = [
            # 복합 인덱스: status + published_at 함께 필터하는 쿼리에 효과적
            models.Index(fields=["status", "-published_at"], name="idx_status_pub"),
            # 부분 인덱스: 발행된 글만 인덱싱 (PostgreSQL)
            models.Index(
                fields=["published_at"],
                name="idx_published_only",
                condition=models.Q(status=ArticleStatus.PUBLISHED),
            ),
        ]
```

**인덱스 추가 기준:**
- `filter()`, `exclude()`, `order_by()`에 자주 사용되는 필드.
- 그러나 쓰기 성능 저하가 있으므로, 프로파일링 후 추가한다.
- Django Debug Toolbar로 느린 쿼리를 식별하고, `EXPLAIN ANALYZE`로 확인한다.

### 11.3 save(update_fields=...) [DDoc]

```python
# 나쁜 예: 모든 필드를 업데이트
article.title = "New Title"
article.save()  # 모든 컬럼이 SET 절에 포함

# 좋은 예: 변경된 필드만 업데이트
article.title = "New Title"
article.save(update_fields=["title"])  # title만 UPDATE
```

- 동시성이 높은 환경에서 다른 필드의 변경을 덮어쓰는 것을 방지한다.
- 업데이트되는 데이터 양을 줄여 성능이 개선된다.

### 11.4 exists()와 count() [DDoc]

```python
# 나쁜 예: 전체 쿼리셋을 평가하여 존재 여부 확인
if Article.objects.filter(status=ArticleStatus.PUBLISHED):  # 모든 행을 로드
    ...

# 좋은 예: exists()로 존재 여부만 확인
if Article.objects.filter(status=ArticleStatus.PUBLISHED).exists():  # LIMIT 1
    ...

# 나쁜 예: len()으로 개수 확인
count = len(Article.objects.all())  # 모든 객체를 메모리에 로드

# 좋은 예: count()로 DB에서 카운트
count = Article.objects.count()  # SELECT COUNT(*)
```

---

## 12. 캐싱 전략

### 12.1 캐싱 수준 [DDoc]

Django는 세 가지 수준의 캐싱을 제공한다.

```python
# 1. Per-View 캐싱: 전체 응답을 캐싱
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15분
def article_list(request):
    articles = Article.objects.published()
    return render(request, "articles/list.html", {"articles": articles})

# CBV에서는 URLconf에서 적용
from django.views.decorators.cache import cache_page
urlpatterns = [
    path("articles/", cache_page(60 * 15)(ArticleListView.as_view())),
]

# 2. 템플릿 프래그먼트 캐싱: 템플릿의 특정 부분만 캐싱
# {% load cache %}
# {% cache 300 sidebar request.user.id %}
#   ... 비용이 큰 사이드바 렌더링 ...
# {% endcache %}

# 3. Low-Level 캐싱: 가장 세밀한 제어
from django.core.cache import cache

def get_expensive_data():
    cache_key = "expensive_data_v1"
    data = cache.get(cache_key)
    if data is None:
        data = compute_expensive_result()
        cache.set(cache_key, data, timeout=60 * 30)  # 30분
    return data
```

### 12.2 캐시 무효화 패턴 [DDoc]

```python
# 버전 기반 캐시 키
def get_article_cache_key(article_id):
    article = Article.objects.only("updated_at").get(pk=article_id)
    return f"article:{article_id}:v{article.updated_at.timestamp()}"

# 모델 save 시 관련 캐시 삭제
class Article(models.Model):
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f"article:{self.pk}")
        cache.delete("article_list")
```

- 자주 변경되는 데이터는 캐싱 효과가 낮다 -- 캐시 적합성을 먼저 판단한다.
- 캐시 키에 **버전 정보**를 포함하면 수동 무효화 빈도를 줄일 수 있다.
- 운영 환경에서는 Redis 또는 Memcached를 사용한다 (로컬 메모리 캐시는 멀티프로세스에서 공유 불가).

---

## 13. 보안

### 13.1 Django 내장 보안 기능 [DDoc] [OWASP]

Django는 주요 웹 취약점에 대한 방어를 내장하고 있다.

| 공격 유형 | Django 방어 | 주의사항 |
|-----------|------------|----------|
| **CSRF** | `CsrfViewMiddleware` + `{% csrf_token %}` | `@csrf_exempt`는 극히 제한적으로 사용 |
| **XSS** | 템플릿 자동 이스케이핑 | `|safe`, `mark_safe()` 사용 시 주의 |
| **SQL Injection** | ORM이 파라미터화 쿼리 사용 | `raw()`, `extra()`에서 직접 문자열 보간 금지 |
| **Clickjacking** | `XFrameOptionsMiddleware` | `X_FRAME_OPTIONS = "DENY"` 설정 |

### 13.2 보안 설정 체크리스트 [DDoc] [OWASP]

```python
# config/settings/production.py

# HTTPS 강제
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 쿠키 보안
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True  # 주의: Django 공식 문서는 CSRF에 대한 실질적 보호 효과가 없다고 명시. 보안 감사 요구사항이 있을 때만 사용. AJAX 사용 시 문제 발생 가능

# 콘텐츠 보안
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Django 보안 체크 실행
# python manage.py check --deploy
```

### 13.3 Raw SQL 안전하게 사용 [DDoc]

```python
# 나쁜 예: 문자열 보간으로 SQL Injection 취약
Model.objects.raw(f"SELECT * FROM app_model WHERE name = '{user_input}'")

# 좋은 예: 파라미터화 쿼리
Model.objects.raw("SELECT * FROM app_model WHERE name = %s", [user_input])

# 나쁜 예: extra()에서 직접 보간
queryset.extra(where=[f"name = '{user_input}'"])

# 좋은 예: extra()에서 파라미터 사용
queryset.extra(where=["name = %s"], params=[user_input])
```

### 13.4 인증과 인가 [DDoc]

```python
# 뷰 레벨 인증 (FBV)
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required("articles.change_article", raise_exception=True)
def edit_article(request, pk):
    ...

# 뷰 레벨 인증 (CBV)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class EditArticleView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "articles.change_article"
    ...
```

---

## 14. 테스트 패턴

이 절은 `discipline-tdd` 입장 심사에서 `add`/`update`된 테스트의 Django mechanics를 고르는 작성 recipe다. framework class·fixture·transaction framework 자체를 시험하기 위해 테스트를 만들지 않으며, 실제 승인된 테스트가 있을 때만 아래 class와 layout을 선택한다.

### 14.1 TestCase 선택 기준 [DDoc]

| 클래스 | 특징 | 사용 시나리오 |
|--------|------|-------------|
| `SimpleTestCase` | DB 접근 불가, 가장 빠름 | 유틸리티 함수, 폼 검증 테스트 |
| `TestCase` | 트랜잭션 롤백으로 격리, 빠름 | **대부분의 테스트** |
| `TransactionTestCase` | 실제 트랜잭션 커밋, 느림 | `select_for_update()`, DB 트리거 테스트 |
| `LiveServerTestCase` | 실제 서버 실행 | Selenium 통합 테스트 |

```python
from django.test import TestCase

class ArticleModelTest(TestCase):
    def test_publish_sets_published_at(self):
        """publish()가 published_at을 설정하는지 검증."""
        article = Article.objects.create(title="Test", author=self.user)
        article.publish()
        article.refresh_from_db()
        self.assertIsNotNone(article.published_at)
        self.assertEqual(article.status, Article.Status.PUBLISHED)
```

### 14.2 Factory Boy 활용 [TDD]

```python
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")

class ArticleFactory(DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Faker("sentence", nb_words=5)
    body = factory.Faker("paragraph")
    author = factory.SubFactory(UserFactory)
    status = Article.Status.DRAFT

    class Params:
        published = factory.Trait(
            status=Article.Status.PUBLISHED,
            published_at=factory.LazyFunction(timezone.now),
        )

# 테스트에서 사용
class ArticleServiceTest(TestCase):
    def test_publish_article(self):
        article = ArticleFactory()  # draft 상태
        article.publish()
        self.assertEqual(article.status, Article.Status.PUBLISHED)

    def test_published_articles_queryset(self):
        ArticleFactory.create_batch(3, published=True)
        ArticleFactory.create_batch(2)  # draft
        self.assertEqual(Article.objects.published().count(), 3)
```

- `SubFactory`로 관련 객체를 자동 생성한다.
- `Trait`로 특정 상태의 팩토리 변형을 정의한다.
- `create_batch()`로 여러 객체를 한 번에 생성한다.

### 14.3 pytest-django 활용 [TDD]

```python
import pytest
from django.test import Client

@pytest.fixture
def api_client():
    return Client()

@pytest.fixture
def authenticated_user(db):
    user = UserFactory()
    return user

@pytest.mark.django_db
class TestArticleAPI:
    def test_create_article(self, api_client, authenticated_user):
        api_client.force_login(authenticated_user)
        response = api_client.post("/api/articles/", {
            "title": "Test Article",
            "body": "Content",
        })
        assert response.status_code == 201
        assert Article.objects.count() == 1

    def test_list_published_articles(self, api_client):
        ArticleFactory.create_batch(3, published=True)
        response = api_client.get("/api/articles/")
        assert response.status_code == 200
        assert len(response.json()["results"]) == 3
```

- `@pytest.mark.django_db`로 DB 접근을 명시한다.
- pytest 픽스처로 테스트 설정 코드를 50% 이상 줄일 수 있다.
- 쿼리 수가 승인된 성능 계약이고 독자 failure로 입장된 테스트에서만 `assertNumQueries`로 회귀를 방지한다.

### 14.4 테스트에서의 Django 공식 규칙 [DCS]

```python
# 좋은 예: assertIs(x, True) -- 타입까지 검증
self.assertIs(article.is_published, True)

# 나쁜 예: assertTrue() -- truthy 값도 통과
self.assertTrue(article.is_published)  # 1, "yes" 등도 통과

# 좋은 예: assertRaisesMessage() -- 에러 메시지까지 검증
with self.assertRaisesMessage(ValidationError, "이미 등록된 이메일"):
    form.clean_email()

# 독스트링은 기대 동작을 바로 서술 (Tests that... 같은 전치사 없이)
def test_publish_sets_status(self):
    """publish() sets status to PUBLISHED and saves published_at."""
```

---

## 15. 미들웨어

### 15.1 미들웨어 실행 순서 [DDoc]

```
요청 -> SecurityMiddleware -> SessionMiddleware -> CommonMiddleware
     -> CsrfViewMiddleware -> AuthenticationMiddleware -> MessageMiddleware
     -> XFrameOptionsMiddleware -> 뷰
응답 <- (역순)
```

- 요청은 `MIDDLEWARE` 리스트의 **위에서 아래**로, 응답은 **아래에서 위로** 흐른다.
- `SecurityMiddleware`는 반드시 첫 번째, `SessionMiddleware`는 `AuthenticationMiddleware` 앞에 위치한다.

### 15.2 커스텀 미들웨어 작성 [DDoc]

```python
import time
import logging

logger = logging.getLogger(__name__)

class RequestTimingMiddleware:
    """각 요청의 처리 시간을 로깅하는 미들웨어."""

    def __init__(self, get_response):
        self.get_response = get_response
        # 서버 시작 시 한 번만 실행

    def __call__(self, request):
        # 요청 처리 전 (process_request에 해당)
        start_time = time.monotonic()

        response = self.get_response(request)

        # 응답 처리 후 (process_response에 해당)
        duration = time.monotonic() - start_time
        logger.info(
            "method=%s path=%s status=%s duration=%.3fs",
            request.method,
            request.path,
            response.status_code,
            duration,
        )
        return response

    def process_exception(self, request, exception):
        """뷰에서 예외 발생 시 호출."""
        logger.exception("Unhandled exception in %s", request.path)
        return None  # None 반환 시 기본 예외 처리 계속
```

- 미들웨어는 **모든 요청**에 실행되므로 가볍게 유지한다.
- 하나의 미들웨어는 하나의 관심사만 담당한다.
- `get_response` 호출 전 코드는 요청 경로, 호출 후 코드는 응답 경로에서 실행된다.

---

## 16. Django와 서비스 레이어 아키텍처

### 16.1 서비스 레이어가 필요한 시점 [TSD] [HS] [CP]

Fat Model이 비대해졌다는 판단은 파일 길이보다 변경 이유와 orchestration 복잡도로 한다. 단순한 한 모델의 행위는 모델 메서드나 custom QuerySet으로 충분하며, service layer는 다음 기준 중 하나 이상이 실제로 있을 때 도입한다.

- 하나의 use case가 여러 모델, 여러 aggregate, 또는 여러 adapter를 조율한다.
- 같은 비즈니스 흐름이 view, API, management command, task, signal 등 여러 entry point에 중복된다.
- use case가 명시적인 transaction boundary를 소유한다.
- 이메일, 결제, 파일, 메시지 publish 같은 외부 side effect가 DB write와 함께 정렬되어야 한다.
- 모델이 domain behavior보다 persistence/orchestration 세부사항 때문에 이해하기 어려워진다.

파일 크기 자체는 보조 신호일 뿐이다. 실제로 함께 이해되고 함께 바뀌는 짧은 절차는 service로 억지 분리하지 않는다.

### 16.2 HackSoft 서비스/셀렉터 패턴 [HS]

```python
# services.py -- 쓰기(Command) 로직
def user_create(*, email: str, password: str) -> User:
    """사용자를 생성하고 환영 이메일을 보낸다."""
    user = User.objects.create_user(email=email, password=password)
    Profile.objects.create(user=user)
    send_welcome_email(user=user)
    return user

def order_confirm(*, order: Order) -> Order:
    """주문을 확정한다."""
    if order.status != Order.Status.PENDING:
        raise ValidationError("확정할 수 없는 상태입니다.")
    order.status = Order.Status.CONFIRMED
    order.confirmed_at = timezone.now()
    order.save(update_fields=["status", "confirmed_at"])
    notify_warehouse(order=order)
    return order

# selectors.py -- 읽기(Query) 로직
def article_list(*, author: User | None = None, status: str | None = None):
    """필터 조건에 따라 기사 목록을 반환한다."""
    qs = Article.objects.select_related("author")
    if author:
        qs = qs.filter(author=author)
    if status:
        qs = qs.filter(status=status)
    return qs.order_by("-published_at")
```

위 `order_confirm`의 `Order.Status` 참조는 평면 Django(기존 관례) 예시다 — 표준 4계층 트리에서는 상태 판정·전이가 도메인 애그리거트 소유이고 값 집합은 domain Enum에서 파생한다(§2.5 계층 소유·`architecture-ddd` §3.2). 어느 경우든 상태 값은 심볼로만 소비한다(리터럴 비교 금지).

**네이밍 규칙: `<entity>_<action>`** -- `user_create`, `order_confirm`, `article_list`

- 네임스페이싱: `user_` 접두사로 사용자 관련 서비스를 묶는다.
- 검색 용이: `grep "def user_"` 로 모든 사용자 관련 동작을 찾을 수 있다.

### 16.3 DDD와 Django의 트레이드오프 [CP]

```python
# Django ORM은 Active Record 패턴 -- 도메인 모델과 영속성 모델이 같은 객체
# DDD의 Repository 패턴을 적용하려면 수동 변환 레이어가 필요

# 방법 A: Django ORM 직접 사용 (대부분의 프로젝트에 적합)
# - Django의 배터리(admin, forms, migrations)를 그대로 활용
# - 도메인 로직은 모델 메서드 + 서비스 레이어에 배치

# 방법 B: Repository 패턴 도입 (복잡한 도메인에 적합)
class ArticleRepository:
    def get_by_id(self, article_id: int) -> Article:
        return Article.objects.get(pk=article_id)

    def save(self, article: Article) -> None:
        article.save()

    def published_by_author(self, author: User) -> QuerySet:
        return Article.objects.filter(
            author=author, status=Article.Status.PUBLISHED
        )
# 장점: 테스트에서 Fake Repository로 교체 가능
# 단점: Django의 풍부한 QuerySet API를 래핑하는 추가 비용
```

**실용적 권고:**
- 대부분의 Django 프로젝트에서는 **모델 메서드 + 서비스 함수**로 충분하다.
- 도메인이 정말 복잡해질 때만 Repository 패턴을 점진적으로 도입한다.
- DDD의 모든 패턴을 Django에 강제하면 Django의 장점(admin, migrations, forms)을 재구현하게 된다. **[CP]**
- 서비스 레이어는 좋은 출발점 -- 뷰와 모델 사이에 얇은 계층을 두어 비즈니스 로직을 격리한다.

### 16.4 트랜잭션과 일관성 경계 [DDoc] [CP]

Django write flow는 use case 단위로 commit/rollback 경계를 정한다. 모든 코드를 큰 transaction으로 감싸는 것이 아니라, 함께 성공하거나 함께 실패해야 하는 최소 블록에 `transaction.atomic()`을 둔다.

```python
from django.db import transaction

def order_confirm(*, order: Order) -> Order:
    with transaction.atomic():
        order = (
            Order.objects
            .select_for_update()
            .get(pk=order.pk)
        )
        order.confirm()
        order.save(update_fields=["status", "confirmed_at"])

        transaction.on_commit(lambda: notify_warehouse(order_id=order.id))

    return order
```

- `transaction.atomic()`의 owner는 model method보다 application service가 되는 경우가 많다. 여러 모델 write, 여러 invariant, 외부 side effect가 하나의 use case에 묶일 때 특히 그렇다.
- `select_for_update()`는 pessimistic lock이 필요한 경우에만 사용한다. 잠금 범위, DB backend 지원, 테스트 환경에서 실제 lock 동작을 검증할 수 있는지 함께 확인한다.
- 중복 write 방지는 application-level check만 믿지 않는다. 반드시 지켜야 하는 invariant는 `UniqueConstraint`, `CheckConstraint`, partial unique index, idempotency storage 같은 DB boundary와 함께 설계한다.
- 개발용 **sqlite에서 `select_for_update()`는 no-op**이다(락 SQL 미발행). 이 한계를 커스텀 DB 백엔드(`BEGIN IMMEDIATE` 등)로 우회하지 말 것 — 운영(Postgres) 정합을 위해 잠금 코드는 두되, 불변식은 `CheckConstraint`(위 항목)가 최종 방어선이고 race 패자의 `IntegrityError`는 표현 계층에서 상태 코드(예: 409)로 변환한다. 잠금이 부족해 보여도 백엔드를 만들지 말고 DB architecture 검토(`architecture-db` §9.5 락·동시성 제어)로 돌린다. **이 금지는 출처-불문이다** — `DatabaseWrapper` 상속뿐 아니라 런타임 몽키패치, `connection_created` 시그널, `OPTIONS`의 `init_command`로 `BEGIN`/PRAGMA 주입, `isolation_level` 조작, DB 미들웨어, 테스트 conftest 패치 등 *어떤 형태로든* 엔진/연결의 트랜잭션·락·격리 의미를 바꾸면 동일한 위반이다(테스트 격리 전용이라도 프로덕션 경로에 새면 안 된다). **필요한 연결 튜닝은 stock `OPTIONS`로만** 한다 — `transaction_mode`(5.1+)로 begin 모드, `timeout`으로 busy 대기, 안전 PRAGMA(`foreign_keys`·`busy_timeout`·`synchronous`·`cache_size`)까지가 허용 범위이고, 격리·락 의미를 바꾸는 변경(`journal_mode`=WAL·`isolation_level`·`locking_mode`·`read_uncommitted`·커스텀 begin 모드)은 설계가 명시 승인할 때만 한다(`architecture-db` §9.5).
- 외부 side effect는 commit 전에 실행하지 않는다. DB write가 rollback될 수 있으면 `transaction.on_commit()`으로 email, message publish, payment follow-up, cache invalidation 시점을 정렬한다.
- isolation level, retry, optimistic/pessimistic locking 선택은 DB 특성과 실패 모드에 따라 달라진다. 결정이 불명확하면 DB architecture 검토가 먼저다.
- HTTP로 노출된 risky write는 API layer의 `Idempotency-Key` 계약과 DB idempotency storage가 서로 맞아야 한다.

Risky write를 구현하거나 리뷰할 때는 다음 항목을 명시한다.

| 항목 | 확인 내용 |
|------|-----------|
| transaction owner | 어떤 service/use case가 atomic boundary를 소유하는가 |
| lock/idempotency | `select_for_update`, optimistic check, unique constraint, idempotency table 중 무엇으로 중복과 race를 막는가 |
| DB constraint | application bug나 다른 writer가 있어도 DB가 지켜야 하는 invariant는 무엇인가 |
| side effect timing | email/payment/message/cache invalidation이 commit 전후 어디에서 실행되는가 |
| isolation/retry | serialization failure, deadlock, duplicate key 같은 실패를 retry할지 forward-fix할지 |
| verification candidates | transaction/constraint/race/rollback 등 보호할 위험·failure 후보와 근거. `TransactionTestCase`, concurrency/integration test, query-count check는 입장 결정 뒤 선택할 mechanics이고 migration SQL review는 별도 비테스트 검증 |

`verification candidates` 행은 테스트 의무가 아니며 결정은 `discipline-tdd`가 소유한다. DB unique/race/rollback/CAS가 다른 boundary와 독립된 production failure일 때만 coder가 `add`할 수 있고, HTTP 등이 같은 제품 failure를 이미 잡으며 독자 DB mechanism이 없으면 `reuse`한다. `add`된 테스트의 일반 DB-backed behavior에는 `TestCase`를 쓰고, commit hook·lock·DB trigger·transaction isolation을 실제로 보호해야 할 때만 `TransactionTestCase`나 실제 DB 기반 integration test를 쓴다. class 선택이나 transaction framework 자체는 새 테스트의 근거가 아니다.

### 16.5 트랜잭셔널 Outbox 구현 [DDoc]

메시지 유실이 허용되지 않는 외부 발행은 Outbox로 구현한다(채택 기준은 `architecture-ddd` §3.7, 전달 보장·dead-letter 정책은 `architecture-db` §9.7). Django에서는 outbox 행을 비즈니스 write와 **같은 `transaction.atomic()` 블록**에서 저장하고, 별도 디스패처가 발행한다.

```python
# domain_layer/order/event/event_type.py -- 발행 이벤트 종류의 단일 출처
# (1종째부터 enum·append-only: birth-enum, architecture-ddd §3.7)
class OrderEventType(StrEnum):
    ORDER_CONFIRMED = "order.confirmed"


# models.py
class OutboxMessage(models.Model):
    event_type = models.CharField(max_length=200)  # 값은 OrderEventType에서만 -- 대입·filter 소비도 심볼로(§2.5 소비 규율)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["published_at", "id"])]


# services.py -- 비즈니스 write와 같은 트랜잭션에 outbox 기록
def confirm_order(*, order: Order) -> Order:
    with transaction.atomic():
        order.confirm()
        order.save(update_fields=["status", "confirmed_at"])
        OutboxMessage.objects.create(
            event_type=OrderEventType.ORDER_CONFIRMED,
            payload={"order_id": order.id},
        )
    return order
```

디스패처는 management command(또는 Celery beat/cron)로 주기 실행한다. 여러 워커가 같은 행을 집지 않도록 `select_for_update(skip_locked=True)`로 미발행 행을 잠그고, 발행에 성공하면 `published_at`을 찍는다.

```python
# management/commands/dispatch_outbox.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            rows = (
                OutboxMessage.objects
                .select_for_update(skip_locked=True)
                .filter(published_at__isnull=True)
                .order_by("id")[:100]
            )
            for msg in rows:
                try:
                    broker.publish(msg.event_type, msg.payload)
                    msg.published_at = timezone.now()
                    msg.save(update_fields=["published_at"])
                except BrokerError:
                    msg.retry_count += 1
                    msg.save(update_fields=["retry_count"])
                    # retry_count가 한계를 넘으면 dead-letter로 이동(별도 플래그/테이블)
```

- 디스패처가 발행 후 `published_at` 기록 전에 죽으면 재실행 시 같은 메시지를 다시 발행한다 -> **at-least-once**. 소비자는 멱등해야 한다(`architecture-db` §9.7).
- 단순 in-process 후속 작업(유실 허용)은 outbox 없이 `transaction.on_commit()`으로 충분하다(§16.4).

---

## 17. Django 5.x 새 기능

### 17.1 Django 5.0 주요 기능 [DDoc]

#### db_default -- 데이터베이스 기본값

```python
from django.db.models.functions import Now, Pi

class Event(models.Model):
    # Python 기본값이 아닌 DB 기본값 사용
    created_at = models.DateTimeField(db_default=Now())
    pi_value = models.FloatField(db_default=Pi())
```

- `default`는 Python에서 계산, `db_default`는 DB에서 계산된다.
- `DEFAULT` 절이 SQL에 직접 포함되어, `bulk_create` 등에서도 올바르게 동작한다.

#### GeneratedField -- DB 생성 필드

```python
class Rectangle(models.Model):
    width = models.IntegerField()
    height = models.IntegerField()
    area = models.GeneratedField(
        expression=F("width") * F("height"),
        output_field=models.IntegerField(),
        db_persist=True,  # True: stored, False: virtual
    )
```

- `db_persist=True`: 저장 시 계산하여 디스크에 저장 (인덱싱 가능).
- `db_persist=False`: 읽기 시마다 계산 (저장 공간 절약).

#### 딕셔너리 기반 Choices

```python
# Django 5.0+ 간결한 구문
class Shirt(models.Model):
    size = models.CharField(
        max_length=2,
        choices={"S": "Small", "M": "Medium", "L": "Large"},
    )
```

### 17.2 Django 5.1 주요 기능 [DDoc]

```python
# LoginRequiredMiddleware -- 전체 사이트에 로그인 요구
MIDDLEWARE = [
    ...
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
]

# 개별 뷰에서 제외
from django.contrib.auth.decorators import login_not_required

@login_not_required
def public_page(request):
    ...
```

### 17.3 Django 5.2 주요 기능 (LTS) [DDoc]

#### Composite Primary Key -- 복합 기본키

```python
from django.db.models import CompositePrimaryKey

class OrderItem(models.Model):
    pk = CompositePrimaryKey("order_id", "product_id")
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
```

- `pk` 속성은 구성 필드 값의 **튜플**이다.
- ⚠ 위 `OrderItem`은 복합 PK 기능 데모이며 `order`·`product` FK는 *같은 BC 내* 가정이다. `product`가 **다른 BC**의 애그리거트면 `ForeignKey(Product)` 대신 `product_id` 값 참조로 둔다(BC 경계 ORM FK 금지 — `architecture-ddd` §3.3 규칙3 영속성 확장).
- **제약사항**: 기존 모델에서 복합 PK로 마이그레이션 불가, ForeignKey가 복합 PK 모델을 가리킬 수 없음, admin 미지원.

#### 자동 모델 임포트 in shell

```bash
# Django 5.2+: shell 실행 시 모든 앱의 모델이 자동 임포트됨
python manage.py shell
>>> Article.objects.count()  # 별도 import 불필요
```

#### 모델 제약 유효성 검증 개선

```python
# Django 5.2: GeneratedField를 사용하는 CheckConstraint 검증 지원
# GeneratedField가 자동으로 DB에서 리프레시 (SQLite, PostgreSQL, Oracle)
```

- Django 5.2는 **LTS** (Long-Term Support)로, 2028년 4월까지 보안 업데이트를 받는다.
- Python 3.10 ~ 3.13을 지원한다 (3.14는 5.2.8+부터 추가).

---

## 참고 자료

### 공식 문서
- [Django Design Philosophies](https://docs.djangoproject.com/en/5.2/misc/design-philosophies/)
- [Django Coding Style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- [Django Security](https://docs.djangoproject.com/en/5.2/topics/security/)
- [Django Database Optimization](https://docs.djangoproject.com/en/5.2/topics/db/optimization/)
- [Django Testing](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Django 5.2 Release Notes](https://docs.djangoproject.com/en/5.2/releases/5.2/)
- [DRF Official Docs](https://www.django-rest-framework.org/)
- [OWASP Django Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)

### 서적
- Two Scoops of Django 3.x (Daniel & Audrey Feldroy)
- Django for Professionals (William Vincent)
- Test-Driven Development with Python (Harry Percival)
- Architecture Patterns with Python (Harry Percival & Bob Gregory)

### 커뮤니티 가이드
- [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide)
- [Django Anti-Patterns](https://www.django-antipatterns.com/)
- [Django Best Practices (Lincoln Loop)](https://lincolnloop.com/blog/django-anti-patterns-signals/)
