# T29: context processor를 dataclass와 Protocol로 구현하려면?

**Skill:** implementation-django-web (Writing mode)
**Cross-skill references loaded:** implementation-python (dataclass, Protocol)

## [주요 내용]

### Protocol로 context processor 인터페이스 정의 (implementation-python 위임)

```python
# web/protocols.py
from typing import Protocol
from django.http import HttpRequest

class ContextProcessor(Protocol):
    def __call__(self, request: HttpRequest) -> dict:
        ...
```

### dataclass로 네비게이션 컨텍스트 구조화 (implementation-python 위임)

```python
# web/context_processors.py
from dataclasses import dataclass
from django.http import HttpRequest

@dataclass(frozen=True)
class NavItem:
    url: str
    label: str
    icon: str
    active: bool

@dataclass(frozen=True)
class NavigationContext:
    items: list[NavItem]
    current_path: str

    def as_dict(self) -> dict:
        return {"navigation": self}

def navigation(request: HttpRequest) -> dict:
    """네비게이션 context processor -- ContextProcessor Protocol을 만족"""
    nav = NavigationContext(
        current_path=request.path,
        items=[
            NavItem(
                url="/orders/",
                label="주문",
                icon="shopping-cart",
                active=request.path.startswith("/orders/"),
            ),
            NavItem(
                url="/dashboard/",
                label="대시보드",
                icon="chart-bar",
                active=request.path.startswith("/dashboard/"),
            ),
        ],
    )
    return nav.as_dict()
```

### settings.py 등록

```python
TEMPLATES = [
    {
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "web.context_processors.navigation",
            ],
        },
    },
]
```

### 템플릿에서 사용

```htmldjango
{% for item in navigation.items %}
<a href="{{ item.url }}"
   class="nav-link {% if item.active %}active{% endif %}">
    {{ item.label }}
</a>
{% endfor %}
```

frozen dataclass로 불변성을 보장하고, Protocol로 인터페이스를 명시적으로 정의한다.

---
> **관련 스킬 참조:**
> - [dataclass, Protocol, frozen] → **implementation-python** 스킬
> - [context processor 상세] → 이 스킬 `references/view-layer.md`
> - [디자인 토큰, 컴포넌트 CSS] → 이 스킬 `references/design-system.md`
