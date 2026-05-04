# pytest 설정과 마커 레퍼런스

pyproject.toml 설정, 마커 시스템, conftest 훅에 대한 상세 규칙과 예시.

---

## 1. pyproject.toml 종합 설정

```toml
[tool.pytest.ini_options]
minversion = "8.0"
# 1차 축은 실행 환경(isolated/real). 두 디렉토리를 모두 등록해
# 평면 `tests/` 또는 한쪽 누락으로 회귀하는 것을 막는다.
testpaths = ["tests/isolated", "tests/real"]
pythonpath = ["src"]
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "-v",
    "--tb=short",
    "--no-header",
]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    # 환경 마커 -- 디렉토리에서 자동 부착된다 (conftest 훅 참고)
    "isolated: 통제된/제공된 테스트 환경에서 수행 (네트워크/시계 차단, CI 기본)",
    "real: 실제 운영 환경에서 수행 (실 DB/실 서비스, 사전 셋업 필요)",
    # 범위 마커
    "integration: 통합 범위 테스트",
    "e2e: 엔드투엔드 테스트",
    # 보조 마커
    "slow: 실행 시간이 긴 테스트",
    "database: DB 연결 필요",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]
xfail_strict = true
log_cli = true
log_cli_level = "INFO"
```

CI 기본 스위트는 `pytest tests/isolated` 또는 `pytest -m "not real"`로 실행하고,
배포 직전 게이트에서 `pytest tests/real`을 별도로 돌린다. `real` 스위트는
실 DB/외부 서비스가 필요하므로 자격 증명이 없는 환경에서 자동 스킵되도록
`tests/real/conftest.py`에서 fixture를 통해 가드한다.

---

## 2. conftest.py 계층 구조

테스트 디렉토리는 1차로 **실행 환경**(`isolated`/`real`), 2차로 **범위**(`unit`/`integration`/`e2e`)로 분리한다. conftest.py는 디렉토리별로 배치되며, pytest가 테스트 수집 시 각 디렉토리의 conftest.py를 자동으로 로드한다. 환경별 강제 규칙(isolated의 네트워크/시계 차단, real의 실 DB 연결)은 각 환경의 conftest.py에 둔다.

```
tests/
  conftest.py                      # 전역 -- 마커 자동 부착, 공통 픽스처
  isolated/                        # 통제된/제공된 테스트 환경 (CI 기본)
    conftest.py                    # 네트워크 차단, 시계 고정 autouse
    unit/
      conftest.py                  # 단위 전용 픽스처 (Fake, Stub)
      test_pricing.py
      test_reservation_service.py
    integration/
      conftest.py                  # in-memory/testcontainers 픽스처
      test_repository_inmemory.py
      test_api_with_fakes.py
  real/                            # 실제 운영 환경 (사전 셋업 필요)
    conftest.py                    # 실 DB 세션, 자격 증명 가드
    integration/
      conftest.py                  # 실 DB 트랜잭션 롤백 픽스처
      test_repository_postgres.py
    e2e/
      conftest.py                  # 브라우저, 실 서비스 클라이언트
      test_checkout_flow.py
```

### tests/conftest.py -- 전역

```python
# tests/conftest.py
import pytest


def pytest_collection_modifyitems(config, items):
    """디렉토리 위치로부터 환경/범위 마커를 자동 부착한다.

    수동 마킹을 강제하면 누락이 생기므로, 디렉토리 자체를 단일 진실로
    삼는다. tests/isolated/** 는 isolated, tests/real/** 는 real.
    """
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

### tests/isolated/conftest.py -- 격리 강제

```python
# tests/isolated/conftest.py
import socket

import pytest


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    """isolated 스위트에서 실수로 네트워크에 나가는 것을 방지.

    실 외부 서비스에 의존하면 결정성과 속도가 모두 깨지므로, 이 환경에서
    소켓 생성을 즉시 실패시킨다. HTTP는 responses/respx로 모킹한다.
    """
    def guard(*args, **kwargs):
        raise RuntimeError(
            "tests/isolated/ 에서는 네트워크 호출이 금지된다. "
            "responses/respx로 모킹하거나 testcontainers를 사용한다."
        )
    monkeypatch.setattr(socket, "socket", guard)


@pytest.fixture(autouse=True)
def _freeze_clock():
    """isolated 스위트의 시계를 고정해 시간 의존 테스트의 비결정성을 제거.

    개별 테스트가 시간을 다르게 잡고 싶다면 time_machine.travel()로
    덮어쓰면 된다.
    """
    import time_machine
    with time_machine.travel("2025-01-01T00:00:00Z", tick=False):
        yield
```

### tests/real/conftest.py -- 실 환경 가드

```python
# tests/real/conftest.py
import os

import pytest


def pytest_collection_modifyitems(config, items):
    """실 DB/외부 서비스 자격 증명이 없으면 real 스위트를 자동 스킵한다.

    개발자 로컬이나 자격 증명이 없는 CI 잡에서 real 테스트가 실패로
    잡히는 것을 방지한다. 자격 증명이 있는 pre-deploy 잡에서만 실행된다.
    """
    if not os.getenv("REAL_DB_URL"):
        skip_real = pytest.mark.skip(reason="REAL_DB_URL 미설정 -- real 스위트 스킵")
        for item in items:
            if "/tests/real/" in str(item.path):
                item.add_marker(skip_real)


@pytest.fixture(scope="session")
def real_db_engine():
    """세션 동안 유지되는 실 DB 엔진."""
    from sqlalchemy import create_engine
    engine = create_engine(os.environ["REAL_DB_URL"])
    yield engine
    engine.dispose()


@pytest.fixture
def real_db_session(real_db_engine):
    """각 테스트마다 트랜잭션을 열고 끝나면 롤백 -- 테스트 간 격리."""
    connection = real_db_engine.connect()
    transaction = connection.begin()
    from sqlalchemy.orm import Session
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

### isolated vs real 분류 기준

| 의존성 | 분류 | 근거 |
|---|---|---|
| 순수 함수, in-memory Fake | `isolated/unit` | 외부 의존성 없음 |
| Mock(spec=...) 외부 SDK | `isolated/unit` 또는 `isolated/integration` | 제공된 더블 |
| testcontainers PostgreSQL | `isolated/integration` | 컨테이너로 제공된 인프라 |
| HTTP responses/respx 모킹 | `isolated/*` | 가짜 응답 |
| 실 stage/dev DB | `real/integration` | 운영 동등 인프라 |
| 외부 PG사 sandbox API | `real/integration` | 실 외부 서비스 |
| 브라우저 + 실 백엔드 | `real/e2e` | 운영과 동등한 전체 경로 |

---

## 3. Django 프로젝트의 환경별 settings

Django 프로젝트에서 `tests/isolated/`는 운영 settings가 아닌 **별도의 테스트 settings 모듈**에서 실행한다. 운영 settings로 테스트를 돌리면 운영 DB 연결, SMTP, Celery 브로커가 잘못 깨어날 수 있어 회귀 위험이 크다. 환경 축을 settings 모듈로 매핑한다.

```
config/settings/
  base.py          # 공통 설정 (INSTALLED_APPS, MIDDLEWARE 등)
  local.py         # 개발자 로컬 (DEBUG=True)
  production.py    # 운영
  test.py          # tests/isolated/ 전용 -- 외부 의존성 모두 차단
  test_real.py     # tests/real/ 전용 -- 실 DB/외부 서비스 자격 증명
```

### config/settings/test.py -- isolated 환경

```python
# config/settings/test.py
from .base import *  # noqa: F401,F403

# DB: SQLite in-memory가 가장 빠르다. ORM 호환성 검증이 필요하면
# testcontainers PostgreSQL로 바꾼다.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# 이메일: 실 SMTP 호출 차단, 메모리에 저장된 메시지를
# `django.core.mail.outbox`로 검증한다.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# 캐시: 프로세스 내 dict로 동작 -- Redis 호출 차단.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery: 브로커 없이 호출 즉시 실행 -- 비동기 큐 의존성 제거.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"

# 스토리지: 임시 디렉토리 -- 운영 S3/미디어 디렉토리 보호.
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# 패스워드 해싱: bcrypt/argon2는 의도적으로 느리므로 테스트에서는 MD5.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# 마이그레이션 비활성화로 DB 셋업 시간 단축 (선택).
class _DisableMigrations:
    def __contains__(self, item): return True
    def __getitem__(self, item): return None
MIGRATION_MODULES = _DisableMigrations()

# 디버그 도구 OFF -- 테스트 출력에 잡음 제거.
DEBUG = False
```

### pytest-django에 settings 주입

```toml
# pyproject.toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
testpaths = ["tests/isolated", "tests/real"]
```

`tests/real/`는 다른 settings로 실행해야 하므로 conftest.py에서 동적으로 교체한다.

```python
# tests/real/conftest.py
import os

import django


def pytest_configure(config):
    """real 스위트는 test_real.py를 사용 -- 실 DB/실 외부 서비스 연결.

    isolated가 먼저 로드되어 settings가 잠겨 있을 수 있으므로,
    real 디렉토리에서 수집된 테스트가 있을 때만 settings를 재구성한다.
    """
    if any("/tests/real/" in str(item) for item in config.args):
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test_real"
        # 이미 setup된 경우 재초기화
        if django.apps.apps.ready:
            from django.conf import settings
            settings._wrapped = django.conf.empty
            django.setup()
```

실제 프로젝트에서는 이 분기를 단순화하기 위해 CI 잡 자체를 둘로 분리하는 것이 일반적이다 -- isolated 잡과 real 잡이 각자 자기 settings로 pytest를 호출한다.

```bash
# CI: isolated 잡
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/

# CI: real 잡 (자격 증명 주입된 pre-deploy)
DJANGO_SETTINGS_MODULE=config.settings.test_real pytest tests/real/
```

> Django 특화 테스트 디테일(TestCase 선택, pytest-django 마크, Factory Boy)은
> implementation-django의 `references/testing.md`를 따른다.

---

## 4. 내장 마커: skip, skipif, xfail

```python
import pytest
import sys

# 무조건 스킵
@pytest.mark.skip(reason="아직 구현되지 않은 기능")
def test_future_feature():
    pass

# 조건부 스킵
@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Windows에서는 지원하지 않음"
)
def test_unix_only():
    pass

# Python 버전 조건
@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Python 3.11+ 필요 (ExceptionGroup 지원)"
)
def test_exception_group():
    pass

# 예상 실패 (xfail)
@pytest.mark.xfail(reason="알려진 버그 #1234, 다음 릴리스에서 수정 예정")
def test_known_bug():
    assert buggy_function() == expected

# strict xfail: 예상대로 실패하지 않으면 테스트 실패
@pytest.mark.xfail(strict=True, reason="이 버그는 반드시 존재해야 함")
def test_strict_xfail():
    assert broken() == wrong_value

# 특정 예외만 xfail
@pytest.mark.xfail(raises=NotImplementedError)
def test_not_implemented():
    unfinished_function()

# xfail + run=False: 테스트를 아예 실행하지 않음
@pytest.mark.xfail(run=False, reason="세그폴트 발생 가능")
def test_dangerous():
    pass
```

---

## 5. 커스텀 마커와 활용 패턴

```python
@pytest.mark.slow
def test_heavy_computation():
    result = compute_for_minutes()
    assert result is not None

@pytest.mark.database
def test_user_creation():
    user = create_user("test@example.com")
    assert user.id is not None

# 여러 마커 중첩
@pytest.mark.slow
@pytest.mark.database
def test_full_migration():
    run_migration()
```

**마커 기반 실행**:

```bash
pytest -m "not slow"              # 느린 테스트 제외
pytest -m "database"              # DB 테스트만 실행
pytest -m "database and not slow" # 복합 조건
pytest -m "slow or database"      # OR 조건
```

---

## 6. 마커에서 fixture로 데이터 전달

```python
@pytest.fixture
def db_connection(request):
    """마커의 인자를 fixture에서 읽는 패턴"""
    marker = request.node.get_closest_marker("database")
    if marker is None:
        db_name = "test_default"
    else:
        db_name = marker.args[0] if marker.args else "test_default"
    conn = create_connection(db_name)
    yield conn
    conn.close()

@pytest.mark.database("analytics_db")
def test_analytics_query(db_connection):
    result = db_connection.execute("SELECT COUNT(*) FROM events")
    assert result > 0
```

> 출처: [pytest Configuration Reference](https://docs.pytest.org/en/stable/reference/customize.html), [Good Integration Practices - pytest](https://docs.pytest.org/en/stable/explanation/goodpractices.html)

> 출처: [How to mark test functions - pytest docs](https://docs.pytest.org/en/stable/how-to/mark.html), [Working with custom markers - pytest docs](https://docs.pytest.org/en/stable/example/markers.html)
