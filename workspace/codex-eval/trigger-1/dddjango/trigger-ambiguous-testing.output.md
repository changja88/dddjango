**주요 내용**

현재 `/private/tmp/dddjango-codex-eval`은 빈 디렉터리이고, `config.toml`도 없습니다. 세션도 `read-only`라 파일 생성/수정과 pytest 실행은 불가능했습니다. 따라서 실제 적용 완료나 테스트 통과는 주장하지 않습니다.

이 프로젝트의 테스트 구조는 dddjango 지침 기준으로 아래처럼 바꾸는 것이 맞습니다.

```text
tests/
  conftest.py
  isolated/
    conftest.py
    unit/
    integration/
  real/
    conftest.py
    integration/
    e2e/
config/
  settings/
    base.py
    test.py
    test_real.py
```

[Before]

```text
tests/
  unit/
  integration/
```

[After]

```text
tests/
  isolated/      # 통제된/제공된 환경: Fake, Mock, in-memory, testcontainers, 네트워크 차단, 시계 고정
    unit/
    integration/
  real/          # 실제 운영 또는 운영 동등 환경: 실 DB, 실 외부 서비스, pre-deploy 게이트
    integration/
    e2e/
```

[Reason] Test Isolation -- `unit/integration`을 1차 축으로 두면 isolated 통합 테스트와 real 통합 테스트가 섞입니다. 실행 정책은 “범위”보다 “환경”이 먼저 결정되어야 하므로 `tests/isolated/`, `tests/real/`을 1차 축으로 둡니다.

`pyproject.toml`의 pytest 설정은 이렇게 둡니다.

```toml
[tool.pytest.ini_options]
minversion = "8.0"
DJANGO_SETTINGS_MODULE = "config.settings.test"
testpaths = ["tests/isolated", "tests/real"]
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
markers = [
    "isolated: 통제된/제공된 테스트 환경에서 수행",
    "real: 실제 운영 또는 운영 동등 환경에서 수행",
    "integration: 통합 범위 테스트",
    "e2e: 엔드투엔드 테스트",
    "slow: 느린 테스트",
]
xfail_strict = true
filterwarnings = ["error"]
```

Django isolated settings는 운영 settings가 아니라 별도 `config/settings/test.py`를 사용해야 합니다.

```python
from .base import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

DEBUG = False
```

`tests/isolated/conftest.py`에는 환경 강제 규칙을 둡니다.

```python
import socket

import pytest
import time_machine


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    def guard(*args, **kwargs):
        raise RuntimeError("tests/isolated/에서는 네트워크 호출이 금지됩니다.")

    monkeypatch.setattr(socket, "socket", guard)


@pytest.fixture(autouse=True)
def _freeze_clock():
    with time_machine.travel("2026-01-01T00:00:00Z", tick=False):
        yield
```

시간 모킹은 기본적으로 `time-machine`을 사용합니다. `freezegun`은 순수 Python 구현인 반면 `time-machine`은 C 확장으로 구현되어 있어 동일 작업에서 100~200배 빠릅니다. 시간 모킹이 많은 테스트 스위트에서는 실제 실행 시간 차이가 납니다. 시간 단위가 중요한 테스트는 “밀리초 단위” 또는 “마이크로초 단위”처럼 구체적으로 명시합니다.

`tests/real/conftest.py`는 실 환경 자격 증명 없을 때 자동 스킵합니다.

```python
import os

import pytest


def pytest_collection_modifyitems(config, items):
    if os.getenv("REAL_DB_URL"):
        return

    skip_real = pytest.mark.skip(reason="REAL_DB_URL 미설정 -- real 스위트 스킵")
    for item in items:
        if "/tests/real/" in str(item.path):
            item.add_marker(skip_real)
```

**RED 테스트 예시**

```python
# tests/isolated/unit/test_test_settings_contract.py
from django.conf import settings


def test_isolated_settings_use_provided_dependencies():
    assert settings.EMAIL_BACKEND == "django.core.mail.backends.locmem.EmailBackend"
    assert settings.CACHES["default"]["BACKEND"] == "django.core.cache.backends.locmem.LocMemCache"
    assert settings.CELERY_TASK_ALWAYS_EAGER is True
    assert settings.CELERY_BROKER_URL == "memory://"
    assert settings.PASSWORD_HASHERS == ["django.contrib.auth.hashers.MD5PasswordHasher"]
```

예상 실패 이유: 현재 workspace에는 Django 프로젝트, `config.settings.test`, `pyproject.toml`, `tests/isolated/`가 없으므로 import 또는 settings contract 검증 단계에서 실패해야 합니다.

**GREEN 최소 구현**

위의 `pyproject.toml`, `config/settings/test.py`, `tests/isolated/conftest.py`, `tests/real/conftest.py`를 추가하면 최소 구조가 잡힙니다. API 테스트가 필요하면 이 프로젝트는 DRF가 아니라 Django Ninja를 사용하므로 `Serializer/ViewSet/APIView` 테스트 대신 Ninja `Router`/`Schema` 기준으로 작성합니다.

**REFACTOR 방향**

테스트 데이터는 `factory_boy`로 빼고, 외부 Repository/Gateway는 `MagicMock` 남발 대신 `InMemoryRepository` Fake로 둡니다. HTTP 외부 호출은 `responses` 또는 `respx`로 막고, Mock이 필요한 경우에는 `create_autospec()` 또는 `spec=`을 사용합니다. 테스트 순서 의존성 검출은 `pytest-randomly`로 확인합니다.

```bash
pip install pytest-randomly
pytest --randomly-seed=last
```

실행 명령은 다음처럼 분리합니다.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/ -q
DJANGO_SETTINGS_MODULE=config.settings.test_real pytest tests/real/ -q
pytest -m "not real" -q
```

이번 세션에서는 파일이 없고 read-only라 위 명령을 실행하지 못했습니다.

---
> **관련 스킬 참조:**
> - 테스트 구조/pytest fixture/Mock 개선 → **implementation-test** 스킬
> - Red-Green-Refactor로 구조 변경 검증 → **implementation-tdd** 스킬
> - Django settings와 pytest-django 구성 → **implementation-django** 스킬