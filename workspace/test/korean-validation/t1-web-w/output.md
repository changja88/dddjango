# Django 템플릿 코드 리뷰

## 대상 코드

```htmldjango
{% extends "base_orders.html" %}
{% block title %}주문 목록{% endblock %}
{% block head_extra %}
    <link rel="stylesheet" href="{% static 'orders/css/orders.css' %}">
{% endblock %}
{% block body %}
<div class="order-list">
    {% for order in orders %}
        {% include "orders/order_card/order_card.html" with order=order %}
    {% endfor %}
</div>
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
<script>
    const orders = {{ orders_json }};
    fetch('/api/orders/reorder/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ order: orders.map(o => o.id) }) });
</script>
{% endblock %}
```

## 잘된 점

- `{% extends "base_orders.html" %}`를 사용하여 3-tier 상속 구조를 따르고 있다.
- `{% static 'orders/css/orders.css' %}`로 정적 파일을 참조하여 하드코딩을 피하고 있다.
- 앱 수준 네임스페이싱(`orders/css/orders.css`)을 올바르게 사용하고 있다.
- `{% include %}`로 `order_card` 컴포넌트를 분리하여 컴포넌트 합성 패턴을 적용하고 있다.

## 발견사항

### 1. XSS 취약점: `<script>` 안에서 `{{ orders_json }}` 직접 사용

```
[json_script 컨벤션] -- <script> 태그 안에서 {{ value }}를 직접 사용하면 XSS 공격에 취약하다. 서버에서 JS로 데이터를 전달할 때는 반드시 json_script 필터를 사용해야 한다. json_script는 <, >, & 등의 특수 문자를 안전하게 이스케이프하고 type="application/json"으로 렌더링하여 브라우저가 직접 실행하지 않는다.
```

### 2. SRI 속성 누락: CDN 스크립트에 `integrity`와 `crossorigin` 없음

```
[SRI 컨벤션] -- CDN에서 로드하는 SortableJS 스크립트에 integrity와 crossorigin="anonymous" 속성이 없다. CDN이 변조될 경우 악성 코드가 실행될 수 있으므로, 모든 CDN script/style 태그에 SRI 속성을 반드시 포함해야 한다.
```

### 3. CSRF 토큰 누락: `fetch` POST 요청에 `X-CSRFToken` 헤더 없음

```
[CSRF 컨벤션] -- fetch로 POST 요청을 보내면서 X-CSRFToken 헤더를 포함하지 않고 있다. Django의 CSRF 보호 메커니즘에 의해 이 요청은 403 Forbidden으로 거부된다. POST/PUT/PATCH/DELETE 요청에는 반드시 csrftoken 쿠키에서 토큰을 읽어 X-CSRFToken 헤더로 전달해야 한다.
```

### 4. `only` 키워드 누락: `{% include %}` 에서 암시적 컨텍스트 누출

```
[include only 컨벤션] -- {% include "orders/order_card/order_card.html" with order=order %}에 only 키워드가 없다. only 없이 include하면 부모 컨텍스트의 모든 변수가 하위 컴포넌트에 노출되어 암시적 의존이 생긴다. {% include ... with order=order only %}로 변경하여 컴포넌트 인터페이스를 명확히 해야 한다.
```

### 5. 인라인 `<script>`에 앱 로직 작성

```
[JS 분리 컨벤션] -- fetch를 사용한 reorder 로직이 인라인 <script>로 작성되어 있다. 앱 로직은 별도 JS 파일(static/orders/js/order_list.js 등)로 분리해야 한다. 인라인 <script>는 서버 데이터 전달(json_script)이나 FOUC 방지 등 즉시 실행이 필요한 예외적 경우에만 허용된다.
```

### 6. `{% load static %}` 누락

```
[load 태그 컨벤션] -- {% static %} 태그를 사용하고 있지만 {% load static %}이 없다. {% load %} 태그는 부모 템플릿에서 상속되지 않으므로, {% static %}을 사용하는 모든 자식 템플릿에서 직접 로드해야 한다. {% extends %} 바로 다음에 {% load static %}을 추가해야 한다.
```

### 7. 닫는 `{% endblock %}` 태그에 블록 이름 없음

```
[endblock 이름 컨벤션] -- {% endblock %}에 블록 이름이 명시되어 있지 않다. {% endblock title %}, {% endblock head_extra %}, {% endblock body %}처럼 블록 이름을 포함하여 닫으면 가독성이 향상되고, 긴 템플릿에서 어떤 블록이 닫히는지 즉시 파악할 수 있다.
```

### 8. `<script>` / `<style>` 태그에 용도 주석 없음

```
[script/style 주석 컨벤션] -- CDN 스크립트와 인라인 스크립트에 Django 템플릿 주석({# ... #})으로 용도가 설명되어 있지 않다. 외부 CDN은 라이브러리 이름과 용도를, 서버 데이터 전달은 어떤 데이터를 전달하는지 명시해야 한다.
```

## 리뷰 체크리스트

- [x] `{% static %}` 대신 하드코딩된 정적 파일 경로 -- 해당 없음 (올바르게 사용)
- [x] `json_script` 없이 `<script>` 안에 `{{ value }}` 사용 (XSS 위험) -- **발견 #1**
- [x] `integrity`와 `crossorigin` 속성이 없는 CDN 스크립트 (SRI) -- **발견 #2**
- [x] AJAX POST/PUT/PATCH/DELETE 요청에 CSRF 토큰 누락 -- **발견 #3**
- [x] `only` 키워드 없는 `{% include %}` (암시적 컨텍스트 누출) -- **발견 #4**
- [x] 디자인 토큰(`var()`) 대신 하드코딩된 색상/간격 값 -- 해당 없음 (CSS가 별도 파일)
- [x] 디자인 시스템 컴포넌트 스타일을 덮어쓰는 외부 CSS -- 해당 없음
- [x] 템플릿 내 인라인 `<style>` (별도 CSS 파일이어야 함) -- 해당 없음
- [x] `<script>` 내 인라인 앱 로직 (별도 JS 파일이어야 함) -- **발견 #5**
- [x] 부모 블록 콘텐츠를 보존해야 하는 곳에서 `{{ block.super }}` 누락 -- 해당 없음 (의도적 대체로 판단)
- [x] 자식 템플릿에서 `{% load %}` 누락 (부모에서 상속되지 않음) -- **발견 #6**
- [x] 인증 페이지에서 TemplateView에 `LoginRequiredMixin` 누락 -- 템플릿 단독으로는 판단 불가, 뷰 코드 확인 필요
- [x] 뷰에서 외부 서비스/API 호출 시 오류 처리 누락 -- 템플릿 단독으로는 판단 불가, 뷰 코드 확인 필요
- [x] 닫는 `{% endblock %}` 태그에 `{% block %}` 이름 없음 -- **발견 #7**
- [x] `var()` 폴백 값이 없는 디자인 토큰 -- 해당 없음 (CSS가 별도 파일)

## 교차 참조 안내

- 뷰의 접근 제어(`LoginRequiredMixin`)와 오류 처리 패턴에 대한 자세한 가이드는 **implementation-django-web** 스킬의 뷰 레이어 레퍼런스를 참조하세요.
- Django 코어 설정(모델, ORM, 마이그레이션)에 대한 자세한 가이드는 **implementation-django** 스킬을 참조하세요.
- API 엔드포인트(`/api/orders/reorder/`) 설계에 대한 자세한 가이드는 **implementation-django-ninja** 스킬을 참조하세요.
- API 설계 원칙에 대한 자세한 가이드는 **architecture-api** 스킬을 참조하세요.
