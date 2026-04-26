# myapp pytest 설정 -- src/ 레이아웃 기반

## 프로젝트 구조

```
myapp/
  pyproject.toml
  src/
    myapp/
      __init__.py
  tests/
    __init__.py
    conftest.py
    unit/
      __init__.py
      conftest.py
      test_placeholder.py
    integration/
      __init__.py
      conftest.py
      test_placeholder.py
    e2e/
      __init__.py
      conftest.py
      test_placeholder.py
```

---

## pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.11"

[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-cov",
    "pytest-xdist",
    "pytest-randomly",
    "pytest-timeout",
    "coverage[toml]",
]
dev = [
    "myapp[test]",
    "ruff",
]

# ---------------------------------------------------------------------------
# pytest
# ---------------------------------------------------------------------------
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
pythonpath = ["src"]
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--no-header",
]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: 실행 시간이 긴 테스트",
    "integration: 외부 서비스 연동 테스트",
    "database: DB 연결이 필요한 테스트",
    "e2e: 엔드투엔드 테스트",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]
xfail_strict = true
timeout = 30

# ---------------------------------------------------------------------------
# coverage
# ---------------------------------------------------------------------------
[tool.coverage.run]
source = ["myapp"]
branch = true
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/__init__.py",
    "*/conftest.py",
]
parallel = true

[tool.coverage.report]
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
    "raise NotImplementedError",
    "pass",
    "\\.\\.\\.",
    "@abstractmethod",
]
show_missing = true
precision = 2
skip_empty = true

[tool.coverage.html]
directory = "htmlcov"
title = "myapp Coverage"

[tool.coverage.xml]
output = "coverage.xml"

# ---------------------------------------------------------------------------
# ruff
# ---------------------------------------------------------------------------
[tool.ruff]
target-version = "py311"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "PT",   # flake8-pytest-style
]

[tool.ruff.lint.isort]
known-first-party = ["myapp"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]
```

---

## tests/conftest.py -- 전역

모든 테스트 레벨에서 공유되는 설정과 fixture를 정의한다.
`pytest_collection_modifyitems` 훅으로 디렉토리 경로 기반 마커를 자동 부여하므로, 개별 테스트에 마커를 일일이 붙이지 않아도 된다.

```python
from __future__ import annotations

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """디렉토리 경로 기반으로 마커를 자동 부여한다."""
    for item in items:
        if "/integration/" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "/e2e/" in item.nodeid:
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(scope="session")
def app_config():
    """세션 전체에서 공유되는 테스트용 설정."""
    return {
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "LOG_LEVEL": "DEBUG",
    }
```

---

## tests/unit/conftest.py -- 단위 테스트

단위 테스트는 외부 의존성과 완전히 격리되어야 한다.
`_disable_network` fixture가 `autouse=True`로 적용되어, 실수로 네트워크 호출을 시도하면 즉시 실패한다.

```python
from __future__ import annotations

import socket

import pytest


@pytest.fixture(autouse=True)
def _disable_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """단위 테스트에서 실수로 네트워크에 접근하는 것을 차단한다."""

    def _guard(*args, **kwargs):
        raise RuntimeError(
            "단위 테스트에서 네트워크 호출이 감지되었습니다. "
            "외부 의존성은 mock/stub으로 대체하세요."
        )

    monkeypatch.setattr(socket, "socket", _guard)
```

---

## tests/integration/conftest.py -- 통합 테스트

통합 테스트는 실제 외부 서비스(DB 등)와 연동하되, 각 테스트는 서로 독립적으로 실행된다.
session 스코프로 비싼 자원을 한 번만 생성하고, function 스코프로 테스트별 격리를 보장한다.

```python
from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def database_url():
    """통합 테스트용 DB URL.

    실제 프로젝트에서는 testcontainers로 Docker 기반
    DB를 사용하거나 별도 테스트 DB를 가리킨다.
    """
    return "sqlite:///tests/integration/test.db"


@pytest.fixture(autouse=True)
def _clean_database(database_url):
    """각 통합 테스트 실행 전후로 DB 상태를 초기화한다.

    실제 프로젝트에서는 트랜잭션 롤백 패턴을 사용한다.
    """
    yield
```

---

## tests/e2e/conftest.py -- E2E 테스트

E2E 테스트는 전체 시스템을 실제 환경에 가깝게 구동한다.
실행 시간이 길므로 timeout을 넉넉하게 설정한다.

```python
from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def base_url():
    """E2E 테스트 대상 서버 URL.

    실제 프로젝트에서는 subprocess로 서버를 구동하거나
    docker-compose로 전체 스택을 올린다.
    """
    return "http://localhost:8000"


@pytest.fixture(autouse=True)
def _e2e_timeout(request: pytest.FixtureRequest) -> None:
    """E2E 테스트의 기본 timeout을 120초로 설정한다."""
    if "timeout" not in {m.name for m in request.node.iter_markers()}:
        request.node.add_marker(pytest.mark.timeout(120))
```

---

## tests/unit/test_placeholder.py -- 단위 테스트 예시

```python
from __future__ import annotations


def test_placeholder():
    """프로젝트 초기 설정이 올바르게 동작하는지 확인한다."""
    assert 1 + 1 == 2
```

---

## tests/integration/test_placeholder.py -- 통합 테스트 예시

```python
from __future__ import annotations


def test_placeholder(database_url):
    """통합 테스트 인프라가 올바르게 동작하는지 확인한다."""
    assert database_url is not None
```

---

## tests/e2e/test_placeholder.py -- E2E 테스트 예시

```python
from __future__ import annotations


def test_placeholder(base_url):
    """E2E 테스트 인프라가 올바르게 동작하는지 확인한다."""
    assert base_url.startswith("http")
```

---

## 사용법

```bash
# 의존성 설치
pip install -e ".[dev]"

# 전체 테스트 실행
pytest

# 단위 테스트만 (느린 테스트 제외)
pytest tests/unit/ -m "not slow"

# 통합 테스트만
pytest tests/integration/ -m integration

# E2E 테스트만
pytest tests/e2e/ -m e2e

# 병렬 실행 (xdist)
pytest -n auto

# 병렬 실행 + 모듈 단위 그룹핑 (비싼 fixture 공유)
pytest -n auto --dist loadscope

# 커버리지 측정
pytest --cov=myapp --cov-report=term-missing tests/

# 커버리지 + 분기 커버리지 + HTML 리포트
pytest --cov=myapp --cov-branch --cov-report=html tests/

# 커버리지 + 병렬 실행
pytest -n auto --cov=myapp tests/

# 최소 커버리지 80% 강제 (CI에서 사용)
pytest --cov=myapp --cov-fail-under=80 tests/

# 마커 조합
pytest -m "database and not slow"
pytest -m "slow or integration"

# ruff 린트
ruff check src/ tests/

# ruff 자동 수정
ruff check --fix src/ tests/
```
