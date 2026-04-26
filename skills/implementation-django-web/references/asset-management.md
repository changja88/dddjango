# 자산 관리 레퍼런스

> Django 프로젝트에서 CSS, JavaScript, 이미지 등 정적 자산의 설정, 구조, 관리 규칙을 다룬다.

---

## 1. 정적 파일 핵심 설정

Django의 `django.contrib.staticfiles` 앱이 정적 파일 탐색, 수집, 서빙을 담당한다.

출처: Django 공식 문서 — Managing static files (https://docs.djangoproject.com/en/5.2/howto/static-files/), Settings (https://docs.djangoproject.com/en/5.2/ref/settings/#static-files)

```python
# settings.py 핵심 설정
STATIC_URL = "static/"                        # URL 접두사
STATIC_ROOT = BASE_DIR / "staticfiles"        # collectstatic 수집 경로
STATICFILES_DIRS = [BASE_DIR / "static"]      # 추가 정적 파일 디렉토리

INSTALLED_APPS = [
    "django.contrib.staticfiles",             # 필수
    # ...
]
```

| 설정 | 역할 |
|------|------|
| `STATIC_URL` | 정적 파일의 URL 접두사 (예: `/static/`) |
| `STATIC_ROOT` | `collectstatic` 명령이 파일을 수집하는 디렉토리 (프로덕션 전용) |
| `STATICFILES_DIRS` | 앱 외부의 추가 정적 파일 디렉토리 목록 |

### STATICFILES_FINDERS

Django가 정적 파일을 탐색하는 순서를 결정한다.

출처: Django 공식 문서 — staticfiles finders (https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#finders-module)

```python
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",      # STATICFILES_DIRS 탐색
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",   # 앱별 static/ 탐색
]
```

- `FileSystemFinder`: `STATICFILES_DIRS`에 지정된 디렉토리를 탐색
- `AppDirectoriesFinder`: 각 앱의 `static/` 하위 디렉토리를 탐색
- `findstatic` 명령으로 파일 탐색 경로를 디버깅할 수 있다: `python manage.py findstatic css/style.css`

---

## 2. 정적 파일 구조

### 앱별 네임스페이싱 (Django 권장)

Django 공식 문서는 앱별 정적 파일에 네임스페이싱을 권장한다. 앱 간 파일명 충돌을 방지하기 위함이다.

출처: Django 공식 문서 — Managing static files (https://docs.djangoproject.com/en/5.2/howto/static-files/)

```
myapp/
└── static/
    └── myapp/                     # 네임스페이스 (앱명과 동일)
        ├── css/
        ├── js/
        └── images/
```

```htmldjango
{% load static %}
<link rel="stylesheet" href="{% static 'myapp/css/style.css' %}">
```

### 프로젝트 레벨 정적 파일

앱에 속하지 않는 공통 자산은 `STATICFILES_DIRS`에 등록된 프로젝트 레벨 디렉토리에 둔다.

```
static/                                # STATICFILES_DIRS에 등록
├── js/                                # 공통 JS
│   └── components.js                  # 공유 인터랙션 컴포넌트
├── css/                               # 공통 CSS
├── images/                            # 공통 이미지 (로고, 파비콘 등)
├── fonts/                             # 폰트 파일
└── dist/                              # 빌드 출력물 (CSS 프레임워크 등, 선택적)
```

---

## 3. collectstatic과 프로덕션 배포

### collectstatic

모든 정적 파일을 `STATIC_ROOT`에 수집한다. 프로덕션 배포 전 필수 단계이다.

출처: Django 공식 문서 — collectstatic (https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#collectstatic)

```bash
python manage.py collectstatic

# 유용한 옵션
python manage.py collectstatic --clear      # 기존 파일 삭제 후 수집
python manage.py collectstatic --dry-run    # 실제 수집 없이 미리보기
python manage.py collectstatic --noinput    # 확인 프롬프트 없이 실행
```

### ManifestStaticFilesStorage (캐시 버스팅)

파일 내용의 MD5 해시를 파일명에 추가하여 브라우저 캐시 무효화를 자동화한다.

출처: Django 공식 문서 — ManifestStaticFilesStorage (https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#manifeststaticfilesstorage)

```python
# settings.py
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}
```

- `style.css` → `style.abc123def.css` 형태로 변환
- `staticfiles.json` 매니페스트 파일이 원본-해시 매핑을 관리
- `{% static %}` 태그가 자동으로 해시된 파일명을 출력
- 파일 내용이 변경되면 해시가 바뀌어 브라우저 캐시가 자동 갱신

### WhiteNoise (프로덕션 정적 파일 서빙)

Django 앱에서 직접 정적 파일을 서빙하는 경량 솔루션이다. Nginx 없이 프로덕션 배포가 가능하다.

출처: WhiteNoise 공식 문서 (https://whitenoise.readthedocs.io/en/stable/django.html)

```python
# settings.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",    # SecurityMiddleware 바로 다음
    # ...
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

- `CompressedManifestStaticFilesStorage`: 캐시 버스팅 + Gzip/Brotli 압축
- CDN 없이도 프로덕션에서 효율적으로 정적 파일 서빙 가능

### 개발 vs 프로덕션

| 환경 | 정적 파일 서빙 |
|------|----------------|
| 개발 (`DEBUG=True`) | `runserver`가 자동으로 서빙 (`staticfiles` 앱) |
| 프로덕션 (`DEBUG=False`) | `collectstatic` → WhiteNoise / Nginx / CDN |

---

## 4. CSS 관리 규칙

### 원칙

- HTML 템플릿에 `<style>` 인라인 작성 **금지** — 별도 `.css` 파일로 분리
- 컴포넌트별 CSS는 HTML과 동일 폴더에 배치 (빌드 도구가 수집)
- 글로벌 스타일시트에서 `@import`로 컴포넌트 CSS를 로드

### CSS 프레임워크 통합 (Tailwind CSS 등)

빌드 도구가 필요한 CSS 프레임워크를 Django와 통합하는 패턴이다.

출처: django-tailwind (https://github.com/timonweb/django-tailwind), django-tailwind-cli (https://github.com/django-commons/django-tailwind-cli)

```
assets/src/css/
└── style.css                      # 프레임워크 디렉티브 + 커스텀 토큰

static/dist/
└── tailwind.css                   # 빌드 출력
```

### django-compressor

CSS/JS 파일을 결합하고 압축하는 도구이다. SCSS/LESS 전처리도 지원한다.

출처: django-compressor 공식 문서 (https://django-compressor.readthedocs.io/en/stable/)

```htmldjango
{% load compress %}
{% compress css %}
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    <link rel="stylesheet" href="{% static 'css/components.css' %}">
{% endcompress %}
{# 프로덕션에서 하나의 압축된 파일로 결합됨 #}
```

---

## 5. JavaScript 관리 규칙

### 분류별 배치

| 종류 | 위치 | 설명 |
|------|------|------|
| 서버 데이터 전달 | 컴포넌트 HTML (json_script) | XSS-safe한 서버 데이터 직렬화 |
| 앱 스크립트 | `static/<app>/js/<component>.js` | 비즈니스 로직 |
| 외부 라이브러리 (CDN) | `<section>-scripts.html` | 앱 스크립트 앞에 로드, SRI 필수 |
| 페이지 전체 스크립트 | `{% block scripts %}` | base.html의 scripts 블록 |
| 공유 컴포넌트 | `static/js/components.js` | base.html에서 글로벌 로드 |

### 서버 → JS 데이터 전달 (json_script)

서버에서 JavaScript로 데이터를 전달할 때 `json_script` 템플릿 필터를 사용한다. `<`, `>`, `&` 등의 특수 문자를 안전하게 이스케이프하여 XSS를 방지한다.

출처: Django 공식 문서 — json_script (https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#json-script)

```htmldjango
{# 서버 → JS 데이터 전달: 주문 통계 #}
{{ order_stats|json_script:"order-stats" }}
<script>
const orderStats = JSON.parse(
    document.getElementById('order-stats').textContent
);
</script>
```

```html
<!-- 렌더링 결과: XSS-safe한 <script> 태그 -->
<script id="order-stats" type="application/json">
    {"total": 42, "pending": 5}
</script>
```

- `{{ value|json_script:"element-id" }}`로 안전한 JSON `<script>` 태그 생성
- `type="application/json"`이므로 브라우저가 실행하지 않음
- `JSON.parse()`로 JavaScript 객체로 변환하여 사용
- `window.__` 전역 변수에 직접 할당하는 패턴은 XSS 취약점이 있으므로 사용하지 않는다

### 외부 라이브러리 로드 (SRI)

CDN에서 외부 스크립트를 로드할 때 Subresource Integrity(SRI) 속성을 반드시 포함한다. CDN이 변조되더라도 무결성을 검증할 수 있다.

출처: MDN — Subresource Integrity (https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity)

```htmldjango
{# chart-scripts.html #}

{# Chart.js — 차트 렌더링 라이브러리 #}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>

{# 차트 초기화 앱 스크립트 #}
<script src="{% static 'dashboard/js/chart.js' %}"></script>
```

- `integrity`: 파일의 해시값 (sha256/sha384/sha512)
- `crossorigin="anonymous"`: CORS 요청 시 인증 정보 제외

### 스크립트 로드 순서

```htmldjango
{# section-scripts.html 패턴 #}

{# 1. 외부 CDN (SRI 포함) #}
<script src="https://cdn.example.com/lib.js" integrity="sha384-..." crossorigin="anonymous"></script>

{# 2. 서버 데이터 전달 #}
{{ chart_data|json_script:"chart-data" }}

{# 3. 앱 스크립트 (위 데이터를 소비) #}
<script src="{% static 'page/js/chart.js' %}"></script>
```

### 금지 사항

- HTML 컴포넌트에 앱 로직을 인라인 `<script>`로 작성하지 않는다
- 예외: 서버 데이터 전달(`json_script`), FOUC 방지 등 즉시 실행이 필요한 경우

### 모던 빌드 도구 통합

ES 모듈, HMR, 트리 쉐이킹이 필요한 경우 django-vite를 사용할 수 있다.

출처: django-vite (https://github.com/MrBin99/django-vite)

```python
# settings.py
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_host": "localhost",
        "dev_server_port": 5173,
    }
}
```

```htmldjango
{% load django_vite %}
{% vite_hmr_client %}
{% vite_asset 'src/main.js' %}
```

---

## 6. `<script>` / `<style>` 주석 규칙

HTML 템플릿에 `<script>` 또는 `<style>` 태그를 작성할 때 반드시 Django 템플릿 주석(`{# ... #}`)으로 용도를 설명한다.

```htmldjango
{# Alpine.js — 선언적 UI 인터랙션 #}
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>

{# 서버 → JS 데이터 전달: 국가별 통계 #}
{{ country_stats|json_script:"country-stats" }}

{# FOUC 방지 — 페이지 로드 전 기본 레이아웃 적용 (인라인 예외) #}
<style>.page-wrap { display: flex; flex-direction: column; min-height: 100dvh; }</style>
```

- 외부 CDN: 라이브러리 이름과 용도 명시
- 서버 데이터: 어떤 데이터를 전달하는지 명시
- 인라인 스타일: 왜 인라인이 필요한지 사유 명시 (예외 상황)

---

## 7. Content Security Policy (CSP)

Django 6.0부터 CSP 미들웨어가 내장되어, 인라인 스크립트/스타일 실행을 제어할 수 있다.

출처: Django 공식 문서 — CSP (https://docs.djangoproject.com/en/6.0/ref/middleware/#content-security-policy-middleware)

```python
# settings.py
MIDDLEWARE = [
    # ...
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
]

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'", "cdn.jsdelivr.net"],
        "style-src": ["'self'", "'unsafe-inline'"],  # 인라인 스타일 허용 시
    },
}
```

- CSP를 적용하면 인라인 `<script>`/`<style>`가 기본 차단됨
- `json_script`는 `type="application/json"`이므로 CSP에 의해 차단되지 않음
- 외부 CDN 도메인을 `script-src`에 명시해야 함

---

## 8. 이미지 관리

```
static/<app>/images/                # 앱별 이미지
static/images/                      # 공통 이미지 (로고, 파비콘 등)
```

```htmldjango
{% load static %}
<img src="{% static 'orders/images/empty-state.svg' %}" alt="주문 없음">
```

- `{% static %}` 태그를 사용하여 경로를 생성한다 (하드코딩 금지)
- `ManifestStaticFilesStorage` 사용 시 자동으로 해시된 URL 출력
- 프로덕션에서 `collectstatic`으로 수집 후 WhiteNoise/Nginx/CDN에서 서빙
