# Python pytest Setup for `myapp` (src layout)

## Project Directory Structure

```
myapp/
├── pyproject.toml
├── src/
│   └── myapp/
│       ├── __init__.py
│       └── ...
├── tests/
│   ├── conftest.py              # Global conftest
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Unit-level conftest
│   │   └── test_example.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Integration-level conftest
│   │   └── test_example.py
│   └── e2e/
│       ├── __init__.py
│       ├── conftest.py          # E2E-level conftest
│       └── test_example.py
```

---

## 1. `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "myapp"
version = "0.1.0"
description = "My application"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0,<9.0",
    "pytest-cov>=5.0,<6.0",
    "pytest-xdist>=3.5,<4.0",
    "pytest-socket>=0.7,<1.0",
    "coverage[toml]>=7.4,<8.0",
    "ruff>=0.4,<1.0",
]

# ---------------------------------------------------------------------------
# pytest
# ---------------------------------------------------------------------------
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

# Default flags:
#   -ra       : show summary of all non-passing tests
#   --strict-markers : error on unknown markers
#   --strict-config  : error on config parse warnings
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
]

# Custom markers
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests that touch external services or databases",
    "database: marks tests that require a live database connection",
    "e2e: marks end-to-end tests",
]

# Minimum Python warnings to surface
filterwarnings = [
    "error",
    "ignore::DeprecationWarning:third_party.*",
]

# ---------------------------------------------------------------------------
# coverage
# ---------------------------------------------------------------------------
[tool.coverage.run]
source = ["myapp"]
branch = true
parallel = true          # Required for xdist; merges .coverage.* files

[tool.coverage.paths]
source = [
    "src/myapp",
    "*/site-packages/myapp",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
skip_empty = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
    "@(abc\\.)?abstractmethod",
    "raise NotImplementedError",
]

[tool.coverage.html]
directory = "htmlcov"

# ---------------------------------------------------------------------------
# ruff
# ---------------------------------------------------------------------------
[tool.ruff]
target-version = "py311"
line-length = 120
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
    "A",    # flake8-builtins
    "S",    # flake8-bandit (security)
    "T20",  # flake8-print
    "PT",   # flake8-pytest-style
    "RUF",  # ruff-specific rules
]
ignore = [
    "S101",  # allow assert in tests
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",   # assert allowed in tests
    "S105",   # hardcoded passwords ok in tests
    "S106",   # hardcoded passwords ok in tests
]

[tool.ruff.lint.isort]
known-first-party = ["myapp"]
```

---

## 2. `tests/conftest.py` -- Global (root-level)

```python
"""
Global conftest.py -- shared fixtures and hooks for the entire test suite.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Autouse: make test-level log output visible when -s is passed
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _configure_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Ensure captured logs include DEBUG-level messages."""
    caplog.set_level(logging.DEBUG)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def tmp_data_dir(tmp_path: object) -> object:
    """Provide a temporary directory pre-populated with a 'data' subfolder."""
    data = tmp_path / "data"  # type: ignore[operator]
    data.mkdir()
    return data


@pytest.fixture()
def sample_config() -> dict[str, object]:
    """Return a minimal configuration dictionary usable across test levels."""
    return {
        "debug": True,
        "database_url": "sqlite:///:memory:",
        "log_level": "DEBUG",
    }


# ---------------------------------------------------------------------------
# Session-scoped: report slow tests at the end
# ---------------------------------------------------------------------------
_slow_tests: list[tuple[str, float]] = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item) -> Iterator[None]:
    """Collect execution time for tests marked 'slow'."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and "slow" in {m.name for m in item.iter_markers()}:
        _slow_tests.append((item.nodeid, report.duration))


def pytest_terminal_summary(terminalreporter: object) -> None:
    """Print a summary of slow tests at session end."""
    if _slow_tests:
        tr = terminalreporter
        tr.write_sep("=", "SLOW TESTS")  # type: ignore[attr-defined]
        for nodeid, duration in sorted(_slow_tests, key=lambda x: -x[1]):
            tr.write_line(f"  {duration:>8.3f}s  {nodeid}")  # type: ignore[attr-defined]
```

---

## 3. `tests/unit/conftest.py` -- Unit-level

```python
"""
Unit test conftest -- network access is BLOCKED here.

Uses `pytest-socket` to disable all socket connections so unit tests
remain fast and deterministic.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Block network for every unit test automatically
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _disable_network(socket_disabled: None) -> None:  # noqa: ARG001
    """Inject the pytest-socket fixture that blocks all socket calls.

    `socket_disabled` is provided by pytest-socket. Any attempt to open a
    socket inside a unit test will raise `SocketBlockedError`.
    """


# ---------------------------------------------------------------------------
# Unit-specific fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def mock_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set up a deterministic environment for unit tests.

    Returns the dict of env vars that were set so the test can inspect them.
    """
    env = {
        "APP_ENV": "testing",
        "DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key-do-not-use-in-production",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return env
```

---

## 4. `tests/integration/conftest.py` -- Integration-level

```python
"""
Integration test conftest -- fixtures that interact with real (but isolated)
external resources such as databases and message queues.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator


# ---------------------------------------------------------------------------
# Auto-apply the integration marker
# ---------------------------------------------------------------------------
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Automatically add the 'integration' marker to every test in this directory."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


# ---------------------------------------------------------------------------
# Database fixture (example: SQLite for lightweight integration tests)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def db_url() -> str:
    """Return the database URL used throughout the integration suite."""
    return "sqlite:///test_integration.db"


@pytest.fixture()
def db_connection(db_url: str) -> Iterator[object]:
    """Provide a database connection that is rolled back after each test.

    Replace the body with your real DB engine logic (SQLAlchemy, asyncpg, etc.).
    """
    # --- Example placeholder ---
    # from sqlalchemy import create_engine
    # engine = create_engine(db_url)
    # connection = engine.connect()
    # transaction = connection.begin()
    # yield connection
    # transaction.rollback()
    # connection.close()
    yield {"url": db_url, "placeholder": True}


@pytest.fixture()
def clean_state(db_connection: object) -> object:
    """Ensure each integration test starts with a clean database state."""
    # Add truncation / reset logic here
    return db_connection
```

---

## 5. `tests/e2e/conftest.py` -- E2E-level

```python
"""
End-to-end test conftest -- fixtures for full application lifecycle testing.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator


# ---------------------------------------------------------------------------
# Auto-apply the e2e marker
# ---------------------------------------------------------------------------
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Automatically add the 'e2e' marker to every test in this directory."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


# ---------------------------------------------------------------------------
# Application fixture (full stack)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def app_config() -> dict[str, object]:
    """Full application configuration for e2e tests."""
    return {
        "debug": False,
        "testing": True,
        "database_url": "sqlite:///test_e2e.db",
        "log_level": "WARNING",
    }


@pytest.fixture(scope="session")
def app(app_config: dict[str, object]) -> Iterator[object]:
    """Start the full application for the e2e test session.

    Replace with your actual app factory.
    """
    # --- Example placeholder ---
    # from myapp.main import create_app
    # application = create_app(app_config)
    # yield application
    yield {"config": app_config, "placeholder": True}


@pytest.fixture()
def client(app: object) -> object:
    """HTTP test client for the running application.

    Replace with your actual test client (httpx, requests, etc.).
    """
    # --- Example placeholder ---
    # from httpx import Client
    # with Client(app=app, base_url="http://test") as c:
    #     yield c
    return {"app": app, "placeholder": True}
```

---

## 6. `tests/unit/__init__.py`

```python
```

## 7. `tests/integration/__init__.py`

```python
```

## 8. `tests/e2e/__init__.py`

```python
```

---

## 9. `tests/unit/test_example.py` -- Sample unit test

```python
"""Example unit tests demonstrating markers and fixtures."""
from __future__ import annotations

import pytest


class TestExample:
    """Basic unit test examples."""

    def test_addition(self) -> None:
        assert 1 + 1 == 2

    def test_sample_config_fixture(self, sample_config: dict[str, object]) -> None:
        """Uses the global fixture from root conftest."""
        assert sample_config["debug"] is True
        assert "database_url" in sample_config

    def test_mock_env(self, mock_env: dict[str, str]) -> None:
        """Uses the unit-level fixture that sets environment variables."""
        import os

        assert os.environ["APP_ENV"] == "testing"
        assert mock_env["APP_ENV"] == "testing"

    def test_network_blocked(self) -> None:
        """Verify that socket access is blocked in unit tests."""
        import socket

        with pytest.raises(Exception):  # SocketBlockedError
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @pytest.mark.slow
    def test_slow_operation(self) -> None:
        """Marked as slow -- skippable via: pytest -m 'not slow'."""
        total = sum(range(100_000))
        assert total > 0
```

---

## 10. `tests/integration/test_example.py` -- Sample integration test

```python
"""Example integration tests demonstrating database fixtures."""
from __future__ import annotations

import pytest


@pytest.mark.integration
@pytest.mark.database
class TestDatabaseIntegration:
    """Integration tests that exercise database interactions."""

    def test_db_connection_available(self, db_connection: object) -> None:
        """Ensure the db_connection fixture provides something."""
        assert db_connection is not None

    def test_clean_state(self, clean_state: object) -> None:
        """Ensure clean_state fixture works."""
        assert clean_state is not None
```

---

## 11. `tests/e2e/test_example.py` -- Sample e2e test

```python
"""Example end-to-end tests demonstrating full-stack fixtures."""
from __future__ import annotations

import pytest


@pytest.mark.e2e
class TestEndToEnd:
    """E2E tests that exercise the full application."""

    def test_app_starts(self, app: object) -> None:
        assert app is not None

    def test_client_available(self, client: object) -> None:
        assert client is not None
```

---

## 12. `src/myapp/__init__.py`

```python
"""myapp -- application root."""

__version__ = "0.1.0"
```

---

## Common Commands

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage (single process)
pytest --cov --cov-report=term-missing --cov-report=html

# Run with coverage + parallel execution (xdist)
pytest -n auto --cov --cov-report=term-missing --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest -m integration

# Run only e2e tests
pytest -m e2e

# Exclude slow tests
pytest -m "not slow"

# Exclude slow + e2e (fast feedback loop)
pytest -m "not slow and not e2e"

# Run specific test file in parallel
pytest -n 4 tests/unit/test_example.py

# Lint with ruff
ruff check src/ tests/
ruff format --check src/ tests/

# Auto-fix lint issues
ruff check --fix src/ tests/
ruff format src/ tests/
```

---

## Design Decisions

### src/ layout
The `pythonpath = ["src"]` setting in `pyproject.toml` ensures pytest can import `myapp` from the `src/` directory without installing the package. This avoids accidental imports from the working directory.

### Network blocking in unit tests
`pytest-socket` is applied via an `autouse` fixture in `tests/unit/conftest.py`. Every unit test automatically has socket access disabled. Any accidental HTTP call or database socket connection raises `SocketBlockedError` immediately.

### xdist + coverage
`parallel = true` in `[tool.coverage.run]` tells coverage to write separate `.coverage.<hostname>.<pid>` files. `pytest-cov` automatically combines them at the end of the run. No manual `coverage combine` step is needed.

### Marker auto-application
Integration and e2e conftest files use `pytest_collection_modifyitems` to auto-tag tests by directory. You can still add markers explicitly on individual tests or classes for finer filtering (e.g., `@pytest.mark.database` on tests that specifically need a database).

### Coverage threshold
`fail_under = 80` in `[tool.coverage.report]` causes `pytest --cov` to exit with a non-zero code if line coverage drops below 80%. This integrates cleanly with CI pipelines.
