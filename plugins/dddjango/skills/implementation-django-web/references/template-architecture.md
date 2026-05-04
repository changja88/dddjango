# 템플릿 아키텍처 레퍼런스

> Django 템플릿 계층 구조, 베이스 템플릿, 컴포넌트 기반 구성 패턴을 다룬다.

---

## 1. 베이스 템플릿 (Base Template)

모든 페이지의 공통 레이아웃을 정의하는 최상위 템플릿이다. 각 페이지는 `{% block %}`을 오버라이드하여 콘텐츠를 채운다.

출처: Django 공식 문서 — Template inheritance (https://docs.djangoproject.com/en/5.2/ref/templates/language/#template-inheritance)

### 표준 블록 구성

```htmldjango
{# base.html #}
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
    <meta charset="utf-8">
    <title>{% block title %}서비스명{% endblock title %}</title>
    <meta name="description" content="{% block meta_description %}기본 설명{% endblock meta_description %}">
    {% block meta_extra %}{# OG 태그, Twitter Card 등 #}{% endblock meta_extra %}
    {% block head_extra %}{# 페이지별 CSS 등 #}{% endblock head_extra %}
</head>
<body>
    {% block navbar %}{% include "design_system/navigation/_navbar.html" %}{% endblock navbar %}
    {% block body %}{% endblock body %}
    {% block footer %}{% include "design_system/layout/_footer.html" %}{% endblock footer %}
    {% block scripts %}{# 페이지별 JS — body 맨 하단 #}{% endblock scripts %}
</body>
</html>
```

### 블록 역할

| 블록 | 역할 | 기본값 |
|------|------|--------|
| `title` | 페이지 제목 | 서비스명 |
| `meta_description` | SEO 설명 | 서비스 기본 설명 |
| `meta_extra` | 추가 메타 태그 (OG 등) | 비어있음 |
| `head_extra` | 추가 head 요소 (CSS 등) | 비어있음 |
| `navbar` | 네비게이션 바 | 기본 navbar include |
| `body` | 메인 콘텐츠 | 비어있음 |
| `footer` | 푸터 | 기본 footer include |
| `scripts` | 페이지별 JS | 비어있음 |

- `navbar`, `footer` 블록을 비워서 특정 페이지에서 숨길 수 있다
- 글로벌 JS/CSS는 `base.html`에서 직접 로드한다
- `{% endblock name %}` 닫는 태그에 블록명을 명시하면 가독성이 향상된다

### 템플릿 상속 규칙

출처: Django 공식 문서 — Template inheritance (https://docs.djangoproject.com/en/5.2/ref/templates/language/#template-inheritance)

- `{% extends %}`는 반드시 템플릿의 **첫 번째 태그**여야 한다
- 같은 템플릿 내에서 **동일한 블록명을 중복 정의할 수 없다**
- `{% load %}` 태그는 **상속되지 않는다** — 자식 템플릿에서 별도로 로드해야 한다

### {{ block.super }}

자식 템플릿에서 부모 블록의 내용을 유지하면서 추가할 때 사용한다. 부모 블록을 완전히 대체하지 않고 확장하는 핵심 기법이다.

출처: Django 공식 문서 — Template inheritance (https://docs.djangoproject.com/en/5.2/ref/templates/language/#template-inheritance)

```htmldjango
{# 부모 블록에 스크립트를 추가 #}
{% block scripts %}
    {{ block.super }}
    <script src="{% static 'orders/js/order_list.js' %}"></script>
{% endblock scripts %}

{# 부모 블록에 CSS를 추가 #}
{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'orders/css/orders.css' %}">
{% endblock head_extra %}
```

- `{{ block.super }}`는 부모 블록의 내용을 해당 위치에 삽입한다
- 위에 두면 부모 내용 뒤에 추가(append), 아래에 두면 앞에 추가(prepend)

---

## 2. Django 표준 3-tier 상속

Django 공식 문서와 Two Scoops of Django는 3단계 템플릿 상속을 권장한다.

출처: Django 공식 문서 — Template inheritance (https://docs.djangoproject.com/en/5.2/ref/templates/language/#template-inheritance), Two Scoops of Django 3.x — Chapter 13: Templates

```
base.html                          # 1단계: 사이트 전체 레이아웃
└── base_<section>.html            # 2단계: 섹션별 레이아웃 (선택적)
    └── <page>.html                # 3단계: 개별 페이지
```

```htmldjango
{# base.html — 사이트 전체 #}
<html>
<body>{% block body %}{% endblock %}</body>
</html>

{# base_orders.html — 주문 섹션 공통 #}
{% extends "base.html" %}
{% block body %}
  <nav>주문 관련 네비게이션</nav>
  {% block content %}{% endblock %}
{% endblock %}

{# orders/order_list.html — 개별 페이지 #}
{% extends "base_orders.html" %}
{% block content %}
  <h1>주문 목록</h1>
{% endblock %}
```

---

## 3. Root 템플릿 패턴 (Composition 기반)

3-tier 상속의 대안으로, 상속 대신 조합(composition)으로 페이지를 구성하는 패턴이다. `<page>_root.html`을 진입점으로 두고, `{% include %}`로만 구성한다. 이 패턴은 Django 공식 표준이 아니라 프로젝트 규약이며, 섹션 간 독립성이 높고 페이지마다 구성이 크게 다른 경우에 유리하다.

### 폴더 구조

```
web/templates/<page>/
├── <page>_root.html               # 진입점 — include만 존재
├── <section_a>/                   # 컴포넌트 폴더
│   ├── <section_a>.html           # HTML 마크업
│   └── <section_a>.css            # 컴포넌트 스타일 (빌드 도구가 수집)
└── <section_b>/
    ├── <section_b>.html
    └── <section_b>-scripts.html   # 외부 CDN + 앱 스크립트 로드 (필요시)
```

### Root 템플릿 작성법

```htmldjango
{# orders/orders_root.html #}
{% extends "base.html" %}

{% block body %}
  {% include "orders/order_list/order_list.html" %}
  {% include "orders/order_summary/order_summary.html" %}
  {% include "orders/order_summary/order_summary-scripts.html" %}
{% endblock %}
```

핵심 규칙:
- root 템플릿: `{% extends %}` + `{% block %}` 안에서 `{% include %}`만 사용
- 컴포넌트 폴더: `html` (+ 필요시 `scripts.html`)을 한 폴더에 배치
- 재사용 컴포넌트: 여러 페이지에서 쓰이면 `design_system/`으로 이동

### 3-tier vs Root 패턴 비교

| 기준 | 3-tier 상속 | Root (Composition) |
|------|-------------|-------------------|
| 섹션 공통 레이아웃 | `base_section.html`에서 자연스럽게 공유 | 공유가 필요하면 별도 include로 분리 |
| 페이지별 구성 차이 | 블록 오버라이드로 제한적 변형 | include 조합으로 자유롭게 구성 |
| 적합한 경우 | 섹션 내 페이지가 유사한 레이아웃 | 페이지마다 구성이 크게 다른 경우 |
| 복잡도 | 상속 체인이 깊어질 수 있음 | include 중첩이 깊어질 수 있음 |

### 예외

| 상황 | 허용 |
|------|------|
| 단순 페이지 | 섹션 분리 불필요 시 `<page>.html` 단일 파일 |
| 인증 플로우 | OAuth 콜백 등은 root + section 패턴 불필요 |
| DEBUG 전용 | 개발용 테스트 페이지는 패턴 예외 허용 |

---

## 4. {% include %}와 컨텍스트

`{% include %}` 태그는 완전히 독립된 렌더링 프로세스이다. include된 템플릿 간에 상태가 공유되지 않는다.

출처: Django 공식 문서 — include tag (https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#include)

### 데이터 전달

```htmldjango
{# 부모 템플릿에서 컴포넌트 호출 #}
{% include "orders/order_card/order_card.html" with order=order show_actions=True %}
```

### only 키워드 (컨텍스트 격리)

`only` 키워드를 사용하면 부모 컨텍스트 전체가 아닌 명시적으로 전달한 변수만 사용할 수 있다. 컴포넌트의 의존성을 명확히 하고 예기치 않은 변수 참조를 방지한다.

```htmldjango
{# only 없이 — 부모 컨텍스트의 모든 변수가 접근 가능 (암묵적 의존) #}
{% include "orders/order_card/order_card.html" with order=order %}

{# only 사용 — order만 접근 가능 (명시적 의존) #}
{% include "orders/order_card/order_card.html" with order=order only %}
```

- 디자인 시스템 컴포넌트에서는 `only`를 사용하여 인터페이스를 명확히 한다
- `only`는 성능 향상이 아닌 유지보수성과 디버깅 용이성을 위한 것이다

### 컴포넌트 필수 변수 문서화

```htmldjango
{# orders/order_card/order_card.html #}
{# 필수 변수: order (Order 객체), show_actions (bool) #}
<div class="order-card">
    <h3>{{ order.title }}</h3>
    <p>{{ order.description }}</p>
    {% if show_actions %}
        <button>편집</button>
    {% endif %}
</div>
```

- 컴포넌트 상단에 Django 주석(`{# #}`)으로 필수 변수와 타입을 명시한다

### 주의사항

- `{% include %}` 안의 `{% block %}`은 이미 평가된 상태이므로 오버라이드할 수 없다
- include는 각각 독립된 렌더링 프로세스이므로, 깊은 중첩은 성능에 영향을 줄 수 있다
- Two Scoops of Django: "Flat is better than nested" — 과도한 include 중첩은 피한다

---

## 5. Django 6.0 템플릿 파트셜

Django 6.0부터 `{% partialdef %}`와 `{% partial %}` 태그가 내장되어, 같은 템플릿 내에서 재사용 가능한 블록을 정의할 수 있다. HTMX와 함께 부분 렌더링에 특히 유용하다.

출처: Django 6.0 릴리스 노트 (https://docs.djangoproject.com/en/6.0/releases/6.0/)

```htmldjango
{# 파트셜 정의 — 인라인으로 렌더링되면서 재사용 가능 #}
{% partialdef order-row inline %}
<tr>
    <td>{{ order.id }}</td>
    <td>{{ order.title }}</td>
    <td>{{ order.status }}</td>
</tr>
{% endpartialdef %}

{# 같은 템플릿에서 재사용 #}
<table>
{% for order in orders %}
    {% partial order-row %}
{% endfor %}
</table>
```

- `inline` 옵션: 정의 위치에서 즉시 렌더링 + 나중에 재사용 가능
- `inline` 생략: 정의 위치에서 렌더링하지 않고 `{% partial %}`로만 사용

---

## 6. TEMPLATES 설정

템플릿 로딩 순서와 탐색 경로를 결정하는 핵심 설정이다.

출처: Django 공식 문서 — Templates settings (https://docs.djangoproject.com/en/5.2/ref/settings/#templates)

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # 프로젝트 레벨 템플릿
        "APP_DIRS": True,                   # 앱별 templates/ 자동 탐색
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

### 템플릿 탐색 순서

1. `DIRS`에 지정된 디렉토리 (순서대로)
2. `APP_DIRS=True`이면 각 앱의 `templates/` 디렉토리

### 프로젝트 vs 앱 템플릿

| 위치 | 용도 |
|------|------|
| `DIRS` (프로젝트 레벨) | `base.html`, 사이트 공통 템플릿, `design_system/` |
| 앱별 `templates/` | 해당 앱 전용 템플릿 |

앱별 템플릿은 네임스페이싱한다: `myapp/templates/myapp/page.html`
