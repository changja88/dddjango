# Review: orders/order_list.html

## 잘된 점

- `{% extends "base_orders.html" %}` 로 3-tier 상속 패턴을 올바르게 사용하고 있다.
- `{% static %}` 태그로 CSS 파일을 참조하고 있다.
- `{% include %}` 와 `with order=order` 를 사용하여 컴포넌트에 데이터를 전달하고 있다.
- `{% for %}` 루프로 주문 목록을 반복 렌더링하는 구조가 명확하다.

## 발견된 문제

### 1. `{% load static %}` 누락

```
[Convention] -- {% load %} 태그는 부모 템플릿에서 상속되지 않는다. 이 템플릿에서 {% static %} 태그를 사용하고 있으므로 {% extends %} 바로 다음에 {% load static %}을 선언해야 한다. 현재 상태에서는 TemplateSyntaxError가 발생한다.
```

> 근거: template-architecture.md -- "{% load %} 태그는 상속되지 않는다 -- 자식 템플릿에서 별도로 로드해야 한다"

### 2. `{{ orders_json }}` 을 `<script>` 내에서 직접 사용 (XSS 위험)

```
[Convention] -- {{ orders_json }}을 <script> 태그 안에서 직접 출력하면 XSS 공격에 취약하다. 악의적 데이터가 orders_json에 포함될 경우 스크립트 주입이 가능하다. json_script 필터를 사용하여 안전하게 서버 데이터를 JavaScript에 전달해야 한다.
```

> 근거: asset-management.md -- "json_script 템플릿 필터를 사용한다. <, >, & 등의 특수 문자를 안전하게 이스케이프하여 XSS를 방지한다", "window.__ 전역 변수에 직접 할당하는 패턴은 XSS 취약점이 있으므로 사용하지 않는다"

올바른 패턴:

```htmldjango
{{ orders_json|json_script:"orders-data" }}
<script>
    const orders = JSON.parse(
        document.getElementById('orders-data').textContent
    );
</script>
```

### 3. CDN 스크립트에 SRI(`integrity`, `crossorigin`) 누락

```
[Convention] -- SortableJS CDN 스크립트에 integrity와 crossorigin 속성이 없다. CDN이 변조될 경우 악성 코드가 실행될 수 있다. 모든 CDN 스크립트에는 Subresource Integrity 속성을 반드시 포함해야 한다.
```

> 근거: asset-management.md -- "CDN에서 외부 스크립트를 로드할 때 Subresource Integrity(SRI) 속성을 반드시 포함한다. CDN이 변조되더라도 무결성을 검증할 수 있다."

올바른 패턴:

```htmldjango
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>
```

### 4. AJAX POST 요청에 CSRF 토큰 누락

```
[Convention] -- fetch()로 POST 요청을 보내고 있으나 X-CSRFToken 헤더가 포함되지 않았다. Django의 CSRF 보호 미들웨어에 의해 403 Forbidden 응답이 반환된다. POST/PUT/PATCH/DELETE 요청에는 반드시 CSRF 토큰을 포함해야 한다.
```

> 근거: view-layer.md -- "POST/PUT/PATCH/DELETE 요청에 X-CSRFToken 헤더 필수", "CSRF 토큰은 csrftoken 쿠키에서 가져온다"

올바른 패턴:

```javascript
fetch('/api/orders/reorder/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
    },
    mode: 'same-origin',
    body: JSON.stringify({ order: orders.map(o => o.id) })
});
```

### 5. `{% include %}` 에 `only` 키워드 누락

```
[Convention] -- {% include "orders/order_card/order_card.html" with order=order %}에 only 키워드가 없다. 부모 컨텍스트의 모든 변수가 컴포넌트에 암묵적으로 전달되어 의존성이 불명확해진다. only를 사용하여 명시적으로 전달하는 변수만 접근 가능하게 해야 한다.
```

> 근거: template-architecture.md -- "only 사용 -- order만 접근 가능 (명시적 의존)", design-system.md -- "only 키워드를 사용하여 컴포넌트에 전달되는 변수를 명시적으로 제한한다"

올바른 패턴:

```htmldjango
{% include "orders/order_card/order_card.html" with order=order only %}
```

### 6. 인라인 `<script>` 에 앱 로직 작성

```
[Convention] -- Sortable 초기화와 fetch 호출 로직이 템플릿에 인라인으로 작성되어 있다. 앱 로직은 별도 JS 파일(static/orders/js/order_list.js)로 분리해야 한다. 인라인 스크립트는 json_script 데이터 전달이나 FOUC 방지 등 즉시 실행이 필요한 경우에만 예외적으로 허용된다.
```

> 근거: asset-management.md -- "HTML 컴포넌트에 앱 로직을 인라인 <script>로 작성하지 않는다", "예외: 서버 데이터 전달(json_script), FOUC 방지 등 즉시 실행이 필요한 경우"

### 7. `{% endblock %}` 닫는 태그에 블록명 누락

```
[Convention] -- {% endblock %} 닫는 태그에 블록명이 명시되지 않았다. {% endblock title %}, {% endblock head_extra %}, {% endblock body %}처럼 블록명을 포함하면 가독성이 향상된다.
```

> 근거: template-architecture.md -- "{% endblock name %} 닫는 태그에 블록명을 명시하면 가독성이 향상된다"

### 8. `{% block head_extra %}` 에서 `{{ block.super }}` 누락

```
[Convention] -- head_extra 블록을 오버라이드하면서 {{ block.super }}를 사용하지 않았다. 부모 템플릿(base_orders.html)의 head_extra에 이미 콘텐츠가 있다면 완전히 대체된다. 부모 콘텐츠를 유지하면서 추가할 의도라면 {{ block.super }}를 포함해야 한다.
```

> 근거: template-architecture.md -- "자식 템플릿에서 부모 블록의 내용을 유지하면서 추가할 때 사용한다. 부모 블록을 완전히 대체하지 않고 확장하는 핵심 기법이다."

### 9. CDN 스크립트와 인라인 스크립트에 Django 템플릿 주석 누락

```
[Convention] -- <script> 태그에 용도를 설명하는 Django 템플릿 주석({# ... #})이 없다. CDN 스크립트에는 라이브러리 이름과 용도를, 서버 데이터 전달에는 어떤 데이터를 전달하는지 명시해야 한다.
```

> 근거: asset-management.md -- "HTML 템플릿에 <script> 또는 <style> 태그를 작성할 때 반드시 Django 템플릿 주석({# ... #})으로 용도를 설명한다"

## 검증 체크리스트

| # | 검증 항목 | 결과 |
|---|-----------|------|
| 1 | 하드코딩된 정적 파일 경로 | Pass -- `{% static %}` 사용 중 |
| 2 | `{{ value }}` inside `<script>` without `json_script` (XSS) | **FAIL** -- `{{ orders_json }}` 직접 사용 |
| 3 | CDN 스크립트에 `integrity`/`crossorigin` 누락 (SRI) | **FAIL** -- SortableJS에 SRI 없음 |
| 4 | AJAX POST 요청에 CSRF 토큰 누락 | **FAIL** -- fetch POST에 X-CSRFToken 없음 |
| 5 | `{% include %}` 에 `only` 키워드 누락 | **FAIL** -- only 없이 include 사용 |
| 6 | 하드코딩된 color/spacing 값 | N/A -- CSS 인라인 없음 |
| 7 | 외부 CSS가 디자인 시스템 컴포넌트 스타일 오버라이드 | N/A -- 해당 없음 |
| 8 | 인라인 `<style>` | Pass -- 인라인 스타일 없음 |
| 9 | 인라인 `<script>` 에 앱 로직 | **FAIL** -- Sortable 초기화/fetch 로직이 인라인 |
| 10 | `{{ block.super }}` 누락 | **FAIL** -- head_extra 블록에서 누락 (부모에 내용이 있을 경우) |
| 11 | `{% load %}` 누락 | **FAIL** -- `{% load static %}` 선언 없음 |
| 12 | TemplateView에 `LoginRequiredMixin` 누락 | N/A -- 뷰 코드 미제공 |
| 13 | 외부 서비스/API 호출 시 에러 처리 누락 | N/A -- 뷰 코드 미제공 |
| 14 | `{% endblock %}` 닫는 태그에 블록명 누락 | **FAIL** -- 모든 endblock에 블록명 없음 |
| 15 | 디자인 토큰에 `var()` 폴백 값 누락 | N/A -- CSS 코드 미제공 |

## 요약

총 **9건**의 문제가 발견되었다. 이 중 보안 관련 이슈가 3건(XSS, SRI, CSRF)으로 가장 우선 수정이 필요하다. `{% load static %}` 누락은 템플릿 렌더링 자체가 실패하는 치명적 오류이다. 나머지는 유지보수성과 코드 품질 관련 이슈이다.

**우선순위:**
1. `{% load static %}` 누락 -- 렌더링 실패
2. `{{ orders_json }}` XSS 취약점 -- 보안
3. CSRF 토큰 누락 -- 보안 / 기능 오류 (403)
4. CDN SRI 누락 -- 보안
5. `{% include %}` 에 `only` 키워드 추가 -- 유지보수성
6. 인라인 스크립트를 별도 JS 파일로 분리 -- 코드 구조
7. `{{ block.super }}` 추가 검토 -- 정확성
8. `{% endblock %}` 에 블록명 추가 -- 가독성
9. `<script>` 태그에 Django 주석 추가 -- 가독성
