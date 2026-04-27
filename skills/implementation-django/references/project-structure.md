# 프로젝트 구조와 설정

## 프로젝트 레이아웃 [TSD]

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
            test.py          # tests/isolated/ 전용 (외부 의존성 차단)
            test_real.py     # tests/real/ 전용 (실 DB/외부 서비스)
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
            admin.py
        orders/
            ...
    tests/                   # 1차: 환경, 2차: 범위 (implementation-test 참조)
        conftest.py
        isolated/            # 통제된/제공된 환경 (CI 기본)
            conftest.py      # 네트워크 차단, 시계 고정 autouse
            unit/
                test_models.py
                test_services.py
            integration/
                test_api_with_fakes.py
        real/                # 실 운영 환경 (pre-deploy 게이트)
            conftest.py      # 자격 증명 가드, 실 DB 세션
            integration/
                test_repository_postgres.py
            e2e/
                test_checkout_flow.py
    manage.py
    docker-compose.yml
    Dockerfile
```

## 앱 분리 기준 [TSD]

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

## 설정(Settings) 분리 [TSD] [DfP]

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

## settings 접근 시 주의사항 [DCS]

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

모듈 임포트 시점에 settings를 사용하면 `settings.configure()`를 통한 수동 설정이 불가능해진다.
