## [주요 내용]

Article 도메인 서비스에 대한 테스트 코드를 Writing 모드로 작성한다. 외부 의존성(SMTP, Celery, 외부 ML HTTP API)이 다수이고 시간 의존 정책(`datetime.now()` 기준 30일 이내 예약 발행)·등급별 가격 산정 로직이 섞여 있으므로, **테스트 디렉토리 환경 분리(`tests/isolated/` vs `tests/real/`) → Django 테스트 settings 모듈 → conftest.py 계층 → factory_boy 팩토리 → 단위/통합 테스트** 순으로 모두 포함하여 제시한다.

핵심 원칙은 다음과 같다.

- [Convention: 환경 축이 범위 축보다 위] -- 1차 축은 **실행 환경**(`tests/isolated/`, `tests/real/`), 2차 축은 **범위**(`unit/`, `integration/`, `e2e/`)다. `tests/isolated/`는 통제된/제공된 테스트 환경(Fake, Mock, in-memory, testcontainers, 네트워크 차단, 시계 고정)에서 CI 기본 스위트로 항상 실행되고, `tests/real/`은 실제 운영 환경(실 DB, 실 SMTP, 실 외부 API)에서 사전 셋업이 필요한 pre-deploy 게이트로 실행된다. 평면 `tests/unit/`+`tests/integration/`은 회귀.
- [Convention: Django isolated는 별도 settings 모듈] -- `tests/isolated/`는 운영 settings가 아닌 `config/settings/test.py`로 실행한다. 이 settings는 `DATABASES`를 SQLite in-memory로, `EMAIL_BACKEND`를 `locmem`으로, `CACHES`를 `LocMemCache`로, `CELERY_TASK_ALWAYS_EAGER=True` + `CELERY_BROKER_URL="memory://"`로, `PASSWORD_HASHERS`를 `MD5PasswordHasher`로 차단한다. 운영 settings로 isolated 테스트를 돌리는 것은 회귀 -- 운영 DB/SMTP/Celery 브로커가 잘못 깨어날 수 있다.
- [Convention: 시간 모킹은 time-machine] -- freezegun은 순수 Python 구현인 반면 time-machine은 C 확장으로 구현되어 있어 동일 작업에서 100~200배 빠름. 시간 모킹이 많은 테스트 스위트에서 실질적인 실행 시간 차이가 발생하므로 CPython 프로젝트에서는 time-machine을 기본으로 한다.
- [Convention: HTTP 외부 호출은 responses 라이브러리] -- `@responses.activate` 데코레이터 + `responses.add(method, url, json=..., status=...)`로 외부 ML 카테고리 추론 API를 결정적으로 모킹한다.
- [Convention: 외부 의존성만 Mock, 핵심 로직은 실제 객체] -- 등급별 가격 산정처럼 도메인 핵심 로직은 실제 객체로 검증하고, 이메일/Celery/HTTP 등 외부 의존성만 더블로 교체한다.

---

### 1. 디렉토리 구조

```
repository_root/
├── pyproject.toml
├── manage.py
├── config/
│   ├── __init__.py
│   ├── urls.py
│   ├── wsgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       ├── production.py
│       ├── test.py            # tests/isolated/ 전용 -- 외부 의존성 차단
│       └── test_real.py       # tests/real/ 전용 -- 실 DB/SMTP/외부 API
├── apps/
│   └── articles/
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py          # Article, Author, MembershipTier 등
│       ├── services.py        # ArticleService.publish(article_id) 등
│       ├── pricing.py         # 등급 할인 가격 산정 (순수 함수)
│       ├── policies.py        # 30일 이내 예약 발행 검증
│       ├── tasks.py           # Celery 태스크 (search 색인 요청)
│       ├── notifications.py   # 작성자 알림 이메일
│       └── ml_classifier.py   # 외부 ML 카테고리 추론 HTTP 클라이언트
└── tests/
    ├── conftest.py            # 전역: 마커 자동 부착
    ├── factories.py           # factory_boy 팩토리 (양 환경 공유)
    ├── isolated/              # 통제된/제공된 환경 (CI 기본)
    │   ├── conftest.py        # 네트워크 차단 + 시계 고정 autouse
    │   ├── unit/
    │   │   ├── conftest.py
    │   │   ├── test_pricing.py             # 등급별 할인 가격 (순수 함수, parametrize)
    │   │   ├── test_policies.py            # 30일 이내 예약 발행 (time-machine)
    │   │   └── test_ml_classifier.py       # responses로 ML API 모킹
    │   └── integration/
    │       ├── conftest.py
    │       └── test_article_service_publish.py  # publish() end-to-end (Django ORM + locmem 메일 + eager Celery + responses)
    └── real/                  # 실 운영 환경 (pre-deploy 게이트)
        ├── conftest.py        # 자격 증명 가드, 실 DB 세션
        └── integration/
            └── test_article_service_real_smtp.py
```

환경별 강제 규칙은 각 환경의 `conftest.py`에 둔다. `tests/isolated/conftest.py`는 네트워크 차단과 시계 고정을 autouse 픽스처로 강제하고, `tests/real/conftest.py`는 자격 증명이 없으면 자동 스킵하고 실 DB 세션을 픽스처로 제공한다.

---

### 2. pyproject.toml -- pytest 설정

```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "8.0"
DJANGO_SETTINGS_MODULE = "config.settings.test"
# 1차 축은 실행 환경(isolated/real). 두 디렉토리를 모두 등록해
# 평면 `tests/` 또는 한쪽 누락으로 회귀하는 것을 막는다.
testpaths = ["tests/isolated", "tests/real"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--reuse-db",
]
markers = [
    # 환경 마커 -- 디렉토리에서 자동 부착됨 (tests/conftest.py 참고)
    "isolated: 통제된/제공된 테스트 환경에서 수행 (네트워크/시계 차단, CI 기본)",
    "real: 실제 운영 환경에서 수행 (실 DB/실 SMTP/실 외부 API, 사전 셋업 필요)",
    # 범위 마커
    "integration: 통합 범위 테스트",
    "e2e: 엔드투엔드 테스트",
    # 보조 마커
    "slow: 실행 시간이 긴 테스트",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]
xfail_strict = true

[tool.coverage.run]
source = ["apps"]
branch = true

[tool.coverage.report]
fail_under = 85
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

CI 파이프라인은 두 단계로 분리한다.

```bash
# CI 잡 1: isolated -- 모든 PR/푸시에서 실행 (결정적, 빠름)
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/

# CI 잡 2: real -- pre-deploy 게이트 (자격 증명 주입)
DJANGO_SETTINGS_MODULE=config.settings.test_real pytest tests/real/
```

테스트 격리 검증을 위해 **`pytest-randomly`** 를 함께 사용한다 -- 테스트 순서 의존성으로 인한 hidden state leak을 잡는다.

```bash
pip install pytest-randomly
pytest --randomly-seed=last  # 직전 시드 재현
```

---

### 3. Django 테스트 settings 모듈

#### 3.1 `config/settings/test.py` -- isolated 환경 (외부 의존성 전부 차단)

```python
# config/settings/test.py
"""tests/isolated/ 전용 settings.

이 settings는 외부 의존성을 모두 더블로 교체한다. 운영 settings로
isolated 테스트를 돌리는 것은 회귀 -- 운영 DB/SMTP/Celery 브로커가
잘못 깨어날 수 있다.
"""
import tempfile

from .base import *  # noqa: F401,F403

# DB: SQLite in-memory가 가장 빠르다. PostgreSQL 호환성 검증이 필요하면
# testcontainers로 교체한다.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# 이메일: 실 SMTP 호출 차단 -- 메모리에 저장된 메시지를
# `django.core.mail.outbox`로 검증한다.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# 캐시: 프로세스 내 dict로 동작 -- Redis 호출 차단.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery: 브로커 없이 호출 즉시 실행 -- 비동기 큐 의존성 제거.
# search 색인 태스크가 실제 큐로 나가지 않고 동일 프로세스에서 즉시 실행된다.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"

# 스토리지: 임시 디렉토리 -- 운영 S3/미디어 디렉토리 보호.
MEDIA_ROOT = tempfile.mkdtemp()
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# 패스워드 해싱: argon2/bcrypt는 의도적으로 느리므로 테스트에서는 MD5.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# 마이그레이션 비활성화로 DB 셋업 시간 단축.
class _DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = _DisableMigrations()

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"
```

#### 3.2 `config/settings/test_real.py` -- real 환경 (실 DB/실 외부 서비스)

```python
# config/settings/test_real.py
"""tests/real/ 전용 settings.

실 stage DB, 실 SMTP, 실 ML API에 붙어 배포 직전 통합을 검증한다.
자격 증명은 환경 변수에서 주입받으며, 자격 증명이 없으면
tests/real/conftest.py에서 자동 스킵된다.
"""
import os

from .base import *  # noqa: F401,F403

# 실 DB (stage 또는 dev 환경의 PostgreSQL)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["REAL_DB_NAME"],
        "USER": os.environ["REAL_DB_USER"],
        "PASSWORD": os.environ["REAL_DB_PASSWORD"],
        "HOST": os.environ["REAL_DB_HOST"],
        "PORT": os.environ.get("REAL_DB_PORT", "5432"),
    }
}

# 실 SMTP -- 별도 테스트용 inbox 도메인 사용 권장
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ["REAL_SMTP_HOST"]
EMAIL_HOST_USER = os.environ["REAL_SMTP_USER"]
EMAIL_HOST_PASSWORD = os.environ["REAL_SMTP_PASSWORD"]
EMAIL_PORT = int(os.environ.get("REAL_SMTP_PORT", "587"))
EMAIL_USE_TLS = True

# 실 Celery 브로커
CELERY_BROKER_URL = os.environ["REAL_CELERY_BROKER_URL"]
CELERY_TASK_ALWAYS_EAGER = False

# 실 ML 추론 API (sandbox)
ML_CLASSIFIER_URL = os.environ["REAL_ML_CLASSIFIER_URL"]

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
```

---

### 4. conftest.py 계층

#### 4.1 `tests/conftest.py` -- 전역 (마커 자동 부착)

```python
# tests/conftest.py
"""전역 conftest -- 디렉토리 위치로부터 환경/범위 마커를 자동 부착한다.

수동 마킹은 누락이 생기므로, 디렉토리 자체를 단일 진실 원천으로 삼는다.
"""
import pytest


def pytest_collection_modifyitems(config, items):
    for item in items:
        path = str(item.path)
        if "/tests/isolated/" in path:
            item.add_marker(pytest.mark.isolated)
        elif "/tests/real/" in path:
            item.add_marker(pytest.mark.real)
        if "/integration/" in path:
            item.add_marker(pytest.mark.integration)
        elif "/e2e/" in path:
            item.add_marker(pytest.mark.e2e)
```

#### 4.2 `tests/isolated/conftest.py` -- 네트워크 차단 + 시계 고정

```python
# tests/isolated/conftest.py
"""isolated 환경 강제 규칙.

- 네트워크 호출 차단 (실수로 외부 API에 나가는 것을 방지)
- 시계 고정 (시간 의존 테스트의 비결정성 제거)
- locmem 이메일 outbox 자동 비우기

개별 테스트가 시간을 다르게 잡고 싶다면 time_machine.travel()로
이 픽스처를 덮어쓴다.
"""
import socket

import pytest
import time_machine
from django.core import mail


# isolated 스위트의 기준 시각 -- 30일 정책 검증의 anchor
FROZEN_NOW = "2026-04-27T09:00:00+00:00"


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    """isolated 스위트에서 실수로 네트워크에 나가는 것을 방지.

    HTTP는 responses로 모킹하고, DB는 SQLite in-memory를 사용한다.
    실수로 requests.get(...)을 직접 호출하면 즉시 실패한다.
    """
    real_socket = socket.socket

    def guard(*args, **kwargs):
        raise RuntimeError(
            "tests/isolated/ 에서는 네트워크 호출이 금지된다. "
            "responses로 모킹하거나 testcontainers를 사용한다."
        )

    monkeypatch.setattr(socket, "socket", guard)


@pytest.fixture(autouse=True)
def _freeze_clock():
    """isolated 스위트의 시계를 FROZEN_NOW로 고정.

    time-machine은 C 확장이라 freezegun보다 100~200배 빠르다.
    시간 모킹이 많은 스위트에서 실질적인 실행 시간 차이가 발생하므로
    CPython 프로젝트에서는 time-machine을 기본으로 한다.
    """
    with time_machine.travel(FROZEN_NOW, tick=False) as traveller:
        yield traveller


@pytest.fixture(autouse=True)
def _clear_mail_outbox():
    """각 테스트마다 outbox를 비워 테스트 간 누설을 차단."""
    mail.outbox = []
    yield
    mail.outbox = []
```

#### 4.3 `tests/isolated/unit/conftest.py` -- 단위 전용 픽스처

```python
# tests/isolated/unit/conftest.py
"""단위 테스트 전용 픽스처.

InMemoryFake와 Mock(spec=...)을 제공한다. MagicMock 남발(Mockery 안티패턴)
대신 InMemoryRepository Fake로 핵심 협력자를 교체한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from unittest.mock import create_autospec

import pytest

from apps.articles.ml_classifier import MLClassifierClient
from apps.articles.notifications import EmailNotifier


@dataclass
class InMemoryArticleRepository:
    """ArticleRepository의 in-memory Fake.

    실 ORM 호출 없이 도메인 서비스 로직을 단위 테스트하기 위한
    간소화된 실제 구현 (Meszaros: Fake).
    """
    _store: dict[int, "Article"] = field(default_factory=dict)

    def add(self, article):
        self._store[article.id] = article

    def get(self, article_id: int):
        return self._store[article_id]

    def save(self, article):
        self._store[article.id] = article


@pytest.fixture
def article_repo():
    return InMemoryArticleRepository()


@pytest.fixture
def email_notifier():
    """spec 강제 -- 존재하지 않는 메서드 호출 시 즉시 실패."""
    return create_autospec(EmailNotifier, instance=True)


@pytest.fixture
def ml_classifier():
    """ML 추론 클라이언트 spec mock. 실제 HTTP는 responses로 모킹한다."""
    return create_autospec(MLClassifierClient, instance=True)
```

#### 4.4 `tests/isolated/integration/conftest.py` -- DB 통합 픽스처

```python
# tests/isolated/integration/conftest.py
"""통합 테스트 픽스처 -- pytest-django의 db fixture와 함께 동작한다.

여기서는 실 ORM(SQLite in-memory) + locmem 메일 + eager Celery로
ArticleService.publish() 전체 플로우를 검증한다.
"""
import pytest

from tests.factories import ArticleFactory, AuthorFactory


@pytest.fixture
def author(db):
    return AuthorFactory()


@pytest.fixture
def draft_article(db, author):
    return ArticleFactory(author=author)
```

#### 4.5 `tests/real/conftest.py` -- 자격 증명 가드 + 실 DB 세션

```python
# tests/real/conftest.py
"""real 환경 강제 규칙.

자격 증명이 없는 환경(개발자 로컬, 일반 CI 잡)에서 real 스위트는
자동 스킵된다. pre-deploy 잡에서만 자격 증명이 주입되어 실행된다.
"""
import os

import pytest


def pytest_collection_modifyitems(config, items):
    required = ("REAL_DB_NAME", "REAL_SMTP_HOST", "REAL_ML_CLASSIFIER_URL")
    if all(os.getenv(k) for k in required):
        return
    skip_real = pytest.mark.skip(
        reason="real 자격 증명 미설정 (REAL_DB_*, REAL_SMTP_*, REAL_ML_*) -- real 스위트 스킵"
    )
    for item in items:
        if "/tests/real/" in str(item.path):
            item.add_marker(skip_real)


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """real 환경에서는 마이그레이션을 그대로 실행한다."""
    yield
```

#### 4.6 `tests/factories.py` -- factory_boy 팩토리 (양 환경 공유)

```python
# tests/factories.py
"""factory_boy 팩토리.

isolated/real 양쪽에서 공유 -- ORM 호환이라 양 settings에서 동일하게
동작한다. Trait으로 발행/예약 발행 변형을 정의한다.
"""
from datetime import timedelta
from decimal import Decimal

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.articles.models import Article, Author, MembershipTier


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    email = factory.Sequence(lambda n: f"author_{n}@example.com")
    name = factory.Faker("name")
    membership_tier = MembershipTier.NORMAL


class ArticleFactory(DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Faker("sentence", nb_words=5)
    body = factory.Faker("paragraph")
    author = factory.SubFactory(AuthorFactory)
    status = Article.Status.DRAFT
    base_price = Decimal("10000")
    scheduled_publish_at = None
    published_at = None
    category = ""

    class Params:
        published = factory.Trait(
            status=Article.Status.PUBLISHED,
            published_at=factory.LazyFunction(timezone.now),
        )
        scheduled_within_30d = factory.Trait(
            scheduled_publish_at=factory.LazyFunction(
                lambda: timezone.now() + timedelta(days=15)
            ),
        )
        scheduled_beyond_30d = factory.Trait(
            scheduled_publish_at=factory.LazyFunction(
                lambda: timezone.now() + timedelta(days=45)
            ),
        )
```

---

### 5. 단위 테스트

#### 5.1 `tests/isolated/unit/test_pricing.py` -- 등급별 할인 가격 (parametrize + 경계값)

```python
# tests/isolated/unit/test_pricing.py
"""유료 기사 가격 = 단가 * (1 - 등급 할인) 검증.

등급(NORMAL/PREMIUM/VIP)과 단가 조합을 parametrize로 검증한다.
mutation testing 관점에서 boundary +/-1(0원, 1원, 최대값)도 포함한다.
순수 함수이므로 DB 없이 검증 가능 -- isolated/unit에 배치.
"""
from decimal import Decimal

import pytest

from apps.articles.models import MembershipTier
from apps.articles.pricing import calculate_price


class TestCalculatePrice:
    """단가 * (1 - 등급 할인)으로 최종 가격을 계산한다."""

    @pytest.mark.parametrize(
        "tier, base_price, expected",
        [
            # NORMAL: 할인 0%
            (MembershipTier.NORMAL, Decimal("10000"), Decimal("10000")),
            (MembershipTier.NORMAL, Decimal("1"), Decimal("1")),
            # PREMIUM: 할인 10%
            (MembershipTier.PREMIUM, Decimal("10000"), Decimal("9000")),
            (MembershipTier.PREMIUM, Decimal("1000"), Decimal("900")),
            # VIP: 할인 25%
            (MembershipTier.VIP, Decimal("10000"), Decimal("7500")),
            (MembershipTier.VIP, Decimal("4"), Decimal("3")),  # 보정 후 정수
        ],
    )
    def test_returns_discounted_price(self, tier, base_price, expected):
        # Arrange-Act-Assert
        assert calculate_price(base_price, tier) == expected

    def test_zero_base_price_returns_zero(self):
        """경계값: 단가 0원이면 등급과 무관하게 0원."""
        assert calculate_price(Decimal("0"), MembershipTier.VIP) == Decimal("0")

    def test_negative_base_price_raises(self):
        """경계값: 음수 단가는 도메인 위반 -- 즉시 실패."""
        with pytest.raises(ValueError, match="음수"):
            calculate_price(Decimal("-1"), MembershipTier.NORMAL)

    def test_unknown_tier_raises(self):
        """미등록 등급은 명시적으로 실패시킨다 (조용한 fallback 금지)."""
        with pytest.raises(ValueError, match="등급"):
            calculate_price(Decimal("10000"), tier="UNKNOWN")  # type: ignore[arg-type]
```

#### 5.2 `tests/isolated/unit/test_policies.py` -- 30일 이내 예약 발행 (time-machine)

```python
# tests/isolated/unit/test_policies.py
"""'오늘로부터 30일 이내의 예약 발행' 정책 검증.

time-machine으로 `datetime.now()`를 고정한다. freezegun은 순수 Python
구현인 반면 time-machine은 C 확장으로 구현되어 있어 동일 작업에서
100~200배 빠름. 시간 모킹이 많은 테스트 스위트에서 실질적인 실행 시간
차이가 발생하므로 CPython 프로젝트에서는 time-machine을 기본으로 한다.

경계값(정확히 30일째 자정, 30일 + 1마이크로초)을 모두 검증한다.
"""
from datetime import datetime, timedelta, timezone

import pytest
import time_machine

from apps.articles.policies import (
    ScheduledTooFarError,
    ensure_scheduled_within_30d,
)


NOW = datetime(2026, 4, 27, 9, 0, 0, tzinfo=timezone.utc)


class TestEnsureScheduledWithin30d:
    """예약 시각이 now() 기준 30일 이내인지 검증한다."""

    @time_machine.travel(NOW, tick=False)
    def test_today_is_allowed(self):
        ensure_scheduled_within_30d(NOW + timedelta(seconds=1))

    @time_machine.travel(NOW, tick=False)
    def test_exactly_30_days_is_allowed(self):
        """경계값: 정확히 30일째 같은 시각은 허용."""
        ensure_scheduled_within_30d(NOW + timedelta(days=30))

    @time_machine.travel(NOW, tick=False)
    def test_30_days_plus_one_microsecond_rejected(self):
        """경계값: 30일 + 1마이크로초는 거부 (boundary +1 mutation 잡기)."""
        with pytest.raises(ScheduledTooFarError):
            ensure_scheduled_within_30d(
                NOW + timedelta(days=30, microseconds=1)
            )

    @time_machine.travel(NOW, tick=False)
    def test_past_time_rejected(self):
        """과거 시각은 예약 발행이 아니므로 거부."""
        with pytest.raises(ScheduledTooFarError):
            ensure_scheduled_within_30d(NOW - timedelta(seconds=1))

    @pytest.mark.parametrize(
        "delta_days, should_pass",
        [
            (0, True),
            (1, True),
            (15, True),
            (29, True),
            (30, True),       # 경계: 정확히 30일은 통과
            (31, False),      # 경계 + 1
            (60, False),
            (365, False),
        ],
    )
    @time_machine.travel(NOW, tick=False)
    def test_30_day_boundary_parametrized(self, delta_days, should_pass):
        target = NOW + timedelta(days=delta_days)
        if should_pass:
            ensure_scheduled_within_30d(target)
        else:
            with pytest.raises(ScheduledTooFarError):
                ensure_scheduled_within_30d(target)
```

#### 5.3 `tests/isolated/unit/test_ml_classifier.py` -- HTTP 모킹 (responses)

```python
# tests/isolated/unit/test_ml_classifier.py
"""외부 ML 카테고리 추론 API HTTP 클라이언트 검증.

requests 라이브러리 호출은 `@responses.activate` + `responses.add`로
모킹한다. tests/isolated/conftest.py가 socket을 차단하지만,
responses는 별도 인터셉트로 동작하므로 정상 모킹된다.

타임아웃/5xx 오류 등 실패 경로도 검증한다.
"""
import pytest
import requests
import responses

from apps.articles.ml_classifier import (
    MLClassifierClient,
    MLClassifierUnavailable,
)


ML_URL = "https://ml.example.com/v1/classify"


class TestMLClassifierClient:
    """외부 ML 서비스에 본문을 보내고 카테고리를 받아온다."""

    @responses.activate
    def test_returns_category_from_api(self):
        responses.add(
            method=responses.POST,
            url=ML_URL,
            json={"category": "tech", "confidence": 0.92},
            status=200,
        )

        client = MLClassifierClient(base_url="https://ml.example.com")
        category = client.classify("Django 5.x 새 기능 정리")

        assert category == "tech"
        assert len(responses.calls) == 1
        # 호출 인자 검증 (assert_called_once만이 아닌 인자까지)
        sent_body = responses.calls[0].request.body
        assert b"Django 5.x" in sent_body

    @responses.activate
    def test_raises_when_api_returns_5xx(self):
        responses.add(
            responses.POST, ML_URL, json={"error": "down"}, status=503
        )

        client = MLClassifierClient(base_url="https://ml.example.com")

        with pytest.raises(MLClassifierUnavailable):
            client.classify("anything")

    @responses.activate
    def test_raises_on_connection_error(self):
        responses.add(
            responses.POST,
            ML_URL,
            body=requests.ConnectionError("timeout"),
        )

        client = MLClassifierClient(base_url="https://ml.example.com")

        with pytest.raises(MLClassifierUnavailable):
            client.classify("anything")

    @pytest.mark.parametrize(
        "confidence, expected_category",
        [
            (0.95, "tech"),
            (0.50, "tech"),       # threshold = 0.5 정확히
            (0.49, "uncategorized"),  # 경계 -1
            (0.0, "uncategorized"),
        ],
    )
    @responses.activate
    def test_confidence_threshold_boundary(
        self, confidence, expected_category
    ):
        """신뢰도 임계값(0.5) 경계 -- mutation testing 보호."""
        responses.add(
            responses.POST,
            ML_URL,
            json={"category": "tech", "confidence": confidence},
            status=200,
        )

        client = MLClassifierClient(base_url="https://ml.example.com")
        result = client.classify("body", min_confidence=0.5)

        assert result == expected_category
```

---

### 6. 통합 테스트 (Django ORM + locmem + eager Celery)

#### 6.1 `tests/isolated/integration/test_article_service_publish.py`

```python
# tests/isolated/integration/test_article_service_publish.py
"""ArticleService.publish() end-to-end 검증.

isolated 환경 구성:
- DB: SQLite in-memory (Django ORM 실제 동작)
- 메일: locmem -- django.core.mail.outbox로 검증
- Celery: ALWAYS_EAGER -- 태스크가 동일 프로세스에서 즉시 실행
- ML API: responses로 HTTP 모킹

운영 settings로 이 테스트를 돌리는 것은 회귀 -- 실 SMTP/실 Celery
브로커가 잘못 깨어날 수 있다.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
import responses
import time_machine
from django.core import mail

from apps.articles.models import Article
from apps.articles.services import ArticleService, ScheduledTooFarError
from tests.factories import ArticleFactory


pytestmark = pytest.mark.django_db


ML_URL = "https://ml.example.com/v1/classify"
NOW = datetime(2026, 4, 27, 9, 0, 0, tzinfo=timezone.utc)


class TestArticleServicePublish:
    """publish(article_id)는 상태/시각/이메일/색인 태스크/카테고리를 모두 처리한다."""

    @responses.activate
    @time_machine.travel(NOW, tick=False)
    def test_publish_sets_status_and_published_at(self, draft_article):
        responses.add(
            responses.POST, ML_URL,
            json={"category": "tech", "confidence": 0.9}, status=200,
        )
        service = ArticleService()

        service.publish(draft_article.id)

        draft_article.refresh_from_db()
        assert draft_article.status == Article.Status.PUBLISHED
        assert draft_article.published_at == NOW

    @responses.activate
    @time_machine.travel(NOW, tick=False)
    def test_publish_sends_notification_email_to_author(
        self, draft_article
    ):
        responses.add(
            responses.POST, ML_URL,
            json={"category": "tech", "confidence": 0.9}, status=200,
        )
        service = ArticleService()

        service.publish(draft_article.id)

        # 상태 기반 검증 (mock.assert_called가 아닌 outbox 실제 메시지)
        assert len(mail.outbox) == 1
        sent = mail.outbox[0]
        assert sent.to == [draft_article.author.email]
        assert draft_article.title in sent.subject

    @responses.activate
    @time_machine.travel(NOW, tick=False)
    def test_publish_dispatches_search_index_task(self, draft_article):
        responses.add(
            responses.POST, ML_URL,
            json={"category": "tech", "confidence": 0.9}, status=200,
        )
        service = ArticleService()

        with patch("apps.articles.tasks.index_article.delay") as mock_delay:
            service.publish(draft_article.id)

        # 호출 인자 검증 (assert_called_once_with -- 단순 assert_called가 아닌)
        mock_delay.assert_called_once_with(article_id=draft_article.id)

    @responses.activate
    @time_machine.travel(NOW, tick=False)
    def test_publish_sets_category_from_ml_api(self, draft_article):
        responses.add(
            responses.POST, ML_URL,
            json={"category": "tech", "confidence": 0.92}, status=200,
        )
        service = ArticleService()

        service.publish(draft_article.id)

        draft_article.refresh_from_db()
        assert draft_article.category == "tech"
        assert len(responses.calls) == 1

    @responses.activate
    @time_machine.travel(NOW, tick=False)
    def test_publish_with_scheduled_within_30d_succeeds(self, author):
        responses.add(
            responses.POST, ML_URL,
            json={"category": "tech", "confidence": 0.9}, status=200,
        )
        article = ArticleFactory(
            author=author, scheduled_within_30d=True
        )
        service = ArticleService()

        service.publish(article.id)

        article.refresh_from_db()
        assert article.status == Article.Status.PUBLISHED

    @time_machine.travel(NOW, tick=False)
    def test_publish_rejects_scheduled_beyond_30d(self, author):
        """30일을 넘는 예약 발행은 거부된다 -- 부수 효과 없음."""
        article = ArticleFactory(
            author=author, scheduled_beyond_30d=True
        )
        service = ArticleService()

        with pytest.raises(ScheduledTooFarError):
            service.publish(article.id)

        # 부수 효과가 일어나지 않았는지 검증
        article.refresh_from_db()
        assert article.status == Article.Status.DRAFT
        assert article.published_at is None
        assert mail.outbox == []
        assert len(responses.calls) == 0

    @responses.activate
    @time_machine.travel(NOW, tick=False)
    def test_publish_continues_when_ml_api_unavailable(
        self, draft_article
    ):
        """ML API 실패는 발행 자체를 막지 않는다 -- category만 빈 값."""
        responses.add(responses.POST, ML_URL, status=503)
        service = ArticleService()

        service.publish(draft_article.id)

        draft_article.refresh_from_db()
        assert draft_article.status == Article.Status.PUBLISHED
        assert draft_article.category == ""
```

---

### 7. real 환경 통합 테스트 (예시)

```python
# tests/real/integration/test_article_service_real_smtp.py
"""실 SMTP/실 ML API에 붙어 배포 직전 통합을 검증한다.

자격 증명이 없으면 tests/real/conftest.py에서 자동 스킵된다.
이 테스트는 pre-deploy 게이트에서만 실행된다.
"""
import os

import pytest

from apps.articles.services import ArticleService
from tests.factories import ArticleFactory


pytestmark = [pytest.mark.django_db, pytest.mark.real]


class TestArticleServicePublishReal:
    def test_publish_actually_sends_email_to_test_inbox(self):
        """실 SMTP로 메일이 전송되는지 확인 -- test inbox 도메인 사용."""
        article = ArticleFactory(
            author__email=os.environ["REAL_TEST_INBOX_ADDRESS"]
        )
        service = ArticleService()

        service.publish(article.id)

        # 실제 inbox 폴링은 별도 헬퍼로 위임 (생략)
        # assert poll_inbox_for_article_published(article.title)
```

---

### 8. 적용된 핵심 원칙 요약

- **AAA 구조**: 모든 테스트가 Arrange-Act-Assert 단일 행위로 정렬되어 있다. 한 테스트는 하나의 동작만 검증한다.
- **검증 우선순위**: 출력 기반(`calculate_price` 반환값) > 상태 기반(`article.status`, `mail.outbox`) > 통신 기반(`mock_delay.assert_called_once_with`)을 따른다. 외부 의존성(SMTP, Celery, HTTP)만 더블로 교체했다.
- **Fake vs Mock**: `InMemoryArticleRepository`는 Fake(간소화된 실제 구현). HTTP는 responses로 모킹. Mock은 `create_autospec`으로 인터페이스를 강제해 API drift를 잡는다.
- **time-machine**: freezegun은 순수 Python 구현인 반면 time-machine은 C 확장으로 구현되어 있어 동일 작업에서 100~200배 빠름. 시간 모킹이 많은 스위트에서 실질적인 실행 시간 차이가 발생하므로 CPython 프로젝트에서는 time-machine을 기본으로 한다.
- **경계값 + parametrize**: 30일 정책은 0/30/30+1마이크로초로, 가격 산정은 NORMAL/PREMIUM/VIP × 단가로, ML threshold는 0.5/0.49로 mutation testing 관점의 boundary를 모두 덮었다.
- **테스트 격리**: `pytest-randomly`로 순서 무작위화하여 hidden state leak을 잡는다 (`pip install pytest-randomly`, `pytest --randomly-seed=last`).
- **autouse 가드**: `_block_network`, `_freeze_clock`, `_clear_mail_outbox`가 isolated 환경의 결정성을 보장한다.

---

> **관련 스킬 참조:**
> - 도메인 모델·서비스의 실제 구현(`ArticleService`, `Article`, `MembershipTier`) → **implementation-django** 스킬
> - 발행 정책·가격 산정의 도메인 모델링(VO/Aggregate/Domain Service 분리) → **architecture-ddd** 스킬
> - ML 클라이언트·이메일·Celery 호출 경계의 헥사고날 포트/어댑터 분리 → **architecture-implementation-patterns** 스킬
> - TDD 사이클(Red-Green-Refactor)로 위 테스트를 견인하며 구현 → **implementation-tdd** 스킬
> - 외부 ML 추론 API의 HTTP 인터페이스 설계(상태 코드, 오류 포맷) → **architecture-api** 스킬
