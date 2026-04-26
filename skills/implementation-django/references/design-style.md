# Django 설계 철학과 코딩 스타일

## 설계 철학 [DDP]

| 원칙 | 설명 |
|------|------|
| **Loose Coupling** | 프레임워크의 각 계층은 서로에 대해 최소한만 안다. 템플릿은 웹 요청을 모르고, 데이터베이스 계층은 화면 표시를 모른다. |
| **Less Code** | 앱은 최소한의 코드로 작성되어야 하며, 보일러플레이트를 배제한다. Python의 동적 기능(인트로스펙션 등)을 최대한 활용한다. |
| **Quick Development** | 웹 개발의 지루한 측면을 빠르게 처리하는 것이 프레임워크의 존재 이유다. |
| **DRY** | 모든 고유한 개념과 데이터는 하나의 장소에만 존재해야 한다. 중복은 나쁘고, 정규화가 좋다. |
| **Explicit > Implicit** | PEP 20의 원칙. "마법"은 거대한 편의를 제공하면서도 개발자를 혼동시키지 않을 때만 사용한다. |
| **Consistency** | 저수준(코딩 스타일)부터 고수준(사용 경험)까지 일관성을 유지한다. |

### 모델 철학
- 모델은 객체의 모든 측면을 캡슐화한다 (Active Record 패턴).
- 데이터와 데이터에 관한 메타정보(사람이 읽는 이름, 기본 정렬 등) 모두 모델 클래스에 정의한다.

### 데이터베이스 API 철학
- SQL 문을 최소한으로 실행하고, 내부적으로 최적화한다.
- 최소 구문으로 풍부하고 표현력 있는 문장을 허용한다. 조인은 뒷단에서 자동 수행된다.
- ORM은 지름길이지 끝이 아니다. 커스텀 SQL을 쉽게 작성할 수 있어야 한다.

### URL 설계 철학
- URL은 Python 함수명에 결합되면 안 된다 (Loose Coupling).
- 어떤 URL 설계든 허용할 수 있는 무한한 유연성을 제공한다.
- URL에 파일 확장자를 포함시키지 않는다.

### 뷰 철학
- 뷰 작성은 Python 함수 작성만큼 단순해야 한다.
- 요청 객체를 전역 변수가 아닌 직접 전달받아 테스트를 쉽게 만든다.
- GET과 POST를 명확히 구분한다.

## 코딩 스타일 [DCS]

### 포매팅 기본 규칙
- **black** 포매터를 사용한다. 코드 줄 길이는 **88자**, 문서/주석/독스트링은 **79자**.
- Python은 **4칸 들여쓰기**, HTML 템플릿은 **2칸 들여쓰기**.

### 임포트 순서 (6그룹, 그룹 내 알파벳순)

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

### 문자열 포매팅

```python
# 좋은 예: f-string 내에서 단순 속성 접근
f"hello {user}"
f"hello {user.name}"

# 나쁜 예: f-string 내에서 함수 호출이나 연산
f"hello {get_user()}"
f"you are {user.age * 365.25} days old"

# 좋은 예: 복잡한 표현은 지역 변수로 분리
user = get_user()
f"hello {user}"

# 번역 대상 문자열에는 f-string을 사용하지 않는다
_("Hello %(name)s") % {"name": user.name}  # O
_(f"Hello {user.name}")                      # X
```

### 모델 코딩 스타일

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

### 선택지(Choices) 정의

```python
# 좋은 예: Enumeration 타입 (Django 3.0+, 권장)
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

### 템플릿 코딩 스타일

```html
{# 좋은 예 #}
{% extends "base.html" %}

{% load i18n l10n static %}

{% block header %}
  <h1>{{ page_title }}</h1>
{% endblock header %}

{% if user.is_authenticated %}
  <p>{{ user.name|lower }}</p>
{% endif %}
```

- `{% extends %}` 는 첫 번째 비주석 줄에 위치한다.
- `{% load %}` 라이브러리는 알파벳순으로 나열한다.
- `{{ variable }}`, `{% tag %}` 안에 정확히 **한 칸** 공백을 둔다.
- `{% endblock header %}` 처럼 블록 이름을 명시한다.

### 뷰 코딩 스타일

```python
# 좋은 예: 첫 번째 매개변수는 반드시 request
def my_view(request, article_id):
    ...

# 나쁜 예
def my_view(req, article_id):   # req가 아닌 request 사용
    ...
```
