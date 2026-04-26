# Django Template JavaScript Review

**File:** `dashboard/chart_section/chart_section.html`

---

## 1. XSS (Cross-Site Scripting) Vulnerabilities

### 1-1. `{{ chart_data|safe }}` -- Critical

```javascript
window.__CHART_DATA__ = {{ chart_data|safe }};
```

`|safe` 필터는 Django의 자동 이스케이프를 완전히 비활성화한다. `chart_data`에 사용자 입력이 포함되어 있거나, DB에서 가져온 값 중 악의적인 문자열이 있을 경우 임의의 JavaScript가 실행될 수 있다.

**권장 수정:**

```htmldjango
window.__CHART_DATA__ = JSON.parse('{{ chart_data_json|escapejs }}');
```

또는 뷰에서 `json.dumps()`로 직렬화한 후 `json_script` 필터를 사용한다.

```htmldjango
{{ chart_data|json_script:"chart-data" }}
<script>
    window.__CHART_DATA__ = JSON.parse(
        document.getElementById('chart-data').textContent
    );
</script>
```

`json_script`는 Django 2.1에서 도입된 내장 필터로, `<script type="application/json">` 태그를 생성하며 XSS에 안전한 이스케이프를 자동으로 수행한다. 이 방법이 가장 권장된다.

### 1-2. `{{ user.profile.theme }}` / `{{ user.profile.locale }}` -- High

```javascript
theme: '{{ user.profile.theme }}',
locale: '{{ user.profile.locale }}'
```

문자열 리터럴 내부에 Django 변수를 직접 삽입하고 있다. 프로필 값에 작은따옴표(`'`)나 백슬래시(`\`)가 포함되면 JavaScript 구문이 깨지거나, 악의적인 값이 들어오면 XSS가 발생할 수 있다.

**권장 수정:**

```htmldjango
theme: '{{ user.profile.theme|escapejs }}',
locale: '{{ user.profile.locale|escapejs }}'
```

`escapejs` 필터는 JavaScript 문자열 내에서 위험한 문자를 유니코드 이스케이프 시퀀스로 변환한다. 문자열 리터럴에 Django 변수를 삽입할 때는 반드시 사용해야 한다.

---

## 2. CSRF Token 누락 -- Critical

```javascript
fetch('/api/stats/revenue/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ period: 'monthly' })
})
```

Django는 POST 요청에 CSRF 토큰을 요구한다. 현재 코드에는 `X-CSRFToken` 헤더가 없으므로, `CsrfViewMiddleware`가 활성화된 환경에서 이 요청은 **403 Forbidden**으로 거부된다.

**권장 수정:**

```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

fetch('/api/stats/revenue/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ period: 'monthly' })
})
```

또는 템플릿에서 `{% csrf_token %}` 태그가 렌더링한 hidden input의 값을 직접 참조할 수도 있다.

```javascript
'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
```

---

## 3. 존재하지 않는 요소 참조 -- Bug

```javascript
document.getElementById('refresh-btn').addEventListener('click', () => {
```

템플릿에 `id="refresh-btn"` 요소가 정의되어 있지 않다. 이 코드는 런타임에 `TypeError: Cannot read properties of null (reading 'addEventListener')`를 발생시킨다.

**권장 수정:**

템플릿에 해당 버튼을 추가하거나, null 체크를 수행한다.

```htmldjango
<button id="refresh-btn" type="button">새로고침</button>
```

또는 방어적 코드:

```javascript
const refreshBtn = document.getElementById('refresh-btn');
if (refreshBtn) {
    refreshBtn.addEventListener('click', () => { /* ... */ });
}
```

---

## 4. 정의되지 않은 함수 호출 -- Bug

```javascript
.then(data => updateChart(data));
```

`updateChart` 함수가 이 템플릿 내에 정의되어 있지 않다. 호출 시 `ReferenceError: updateChart is not defined`가 발생한다. 차트를 실제로 갱신하는 로직을 구현해야 한다.

**권장 수정:**

```javascript
const chart = new Chart(ctx, { /* ... */ });

function updateChart(data) {
    chart.data = data;
    chart.update();
}
```

Chart.js 인스턴스를 변수에 저장하고, `update()` 메서드를 호출하여 차트를 다시 렌더링해야 한다.

---

## 5. 외부 CDN 스크립트 로딩 관련 문제

### 5-1. Subresource Integrity (SRI) 미적용

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
```

CDN이 침해되거나 중간자 공격을 받을 경우, 변조된 스크립트가 실행될 수 있다. `integrity` 속성과 `crossorigin` 속성을 추가해야 한다.

**권장 수정:**

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"
        integrity="sha384-<해시값>"
        crossorigin="anonymous"></script>
```

### 5-2. 스크립트 로딩 순서 의존성

Chart.js CDN 스크립트가 로드되기 전에 아래의 인라인 스크립트가 실행되면 `Chart is not defined` 에러가 발생할 수 있다. 현재 코드에서는 `<script>` 태그 순서에 의존하고 있어 일반적으로는 동작하지만, `async` 또는 `defer` 속성이 추가되면 문제가 된다.

### 5-3. 버전 고정 부재

`chart.js@4`는 메이저 버전만 지정하고 있어, 마이너/패치 업데이트가 자동으로 반영된다. 예기치 않은 breaking change 가능성이 있으므로 정확한 버전(예: `chart.js@4.4.1`)을 고정하는 것이 안전하다.

---

## 6. 에러 핸들링 부재

```javascript
fetch('/api/stats/revenue/', { /* ... */ })
    .then(r => r.json())
    .then(data => updateChart(data));
```

`.catch()` 핸들러가 없다. 네트워크 오류, 서버 500 에러, JSON 파싱 실패 등의 상황에서 에러가 조용히 무시되며 사용자에게 아무 피드백도 제공되지 않는다. 또한 HTTP 응답 상태 코드도 검사하지 않고 있다 (`fetch`는 4xx/5xx 응답에서도 reject되지 않는다).

**권장 수정:**

```javascript
fetch('/api/stats/revenue/', { /* ... */ })
    .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
    })
    .then(data => updateChart(data))
    .catch(err => {
        console.error('차트 데이터 갱신 실패:', err);
        // 사용자에게 에러 상태를 표시하는 UI 처리
    });
```

---

## 7. 전역 네임스페이스 오염

```javascript
window.__CHART_DATA__ = {{ chart_data|safe }};
window.__USER_PREFS__ = { /* ... */ };
```

`window` 객체에 직접 속성을 추가하고 있다. 다른 스크립트나 서드파티 라이브러리와 이름이 충돌할 수 있다. 특히 대시보드처럼 여러 위젯이 포함되는 페이지에서는 문제가 될 수 있다.

**권장 수정:**

즉시 실행 함수(IIFE)로 스코프를 격리하거나, `json_script` 필터를 사용하여 데이터를 DOM에서 읽어오는 방식으로 변경한다.

```javascript
(function() {
    const chartData = JSON.parse(
        document.getElementById('chart-data').textContent
    );
    // ... 이후 로직
})();
```

---

## 요약

| # | 항목 | 심각도 | 분류 |
|---|------|--------|------|
| 1-1 | `chart_data\|safe` XSS 취약점 | Critical | Security |
| 1-2 | 프로필 변수 escapejs 미사용 | High | Security |
| 2 | CSRF 토큰 누락 | Critical | Security |
| 3 | `refresh-btn` 요소 미존재 | High | Bug |
| 4 | `updateChart` 함수 미정의 | High | Bug |
| 5 | CDN SRI 미적용, 버전 미고정 | Medium | Security |
| 6 | fetch 에러 핸들링 부재 | Medium | Reliability |
| 7 | 전역 네임스페이스 오염 | Low | Maintainability |
