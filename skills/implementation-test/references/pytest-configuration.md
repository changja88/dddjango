# pytest 설정과 마커 레퍼런스

pyproject.toml 설정, 마커 시스템, conftest 훅에 대한 상세 규칙과 예시.

---

## 1. pyproject.toml 종합 설정

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
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
    "slow: 실행 시간이 긴 테스트",
    "integration: 외부 서비스 필요",
    "database: DB 연결 필요",
    "e2e: 엔드투엔드 테스트",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]
xfail_strict = true
log_cli = true
log_cli_level = "INFO"
```

---

## 2. conftest.py 계층 구조

conftest.py는 디렉토리별로 배치할 수 있으며, pytest가 테스트 수집 시 각 디렉토리의 conftest.py를 자동으로 로드한다.

```
tests/
  conftest.py              # 전역 fixture (DB 연결, 앱 인스턴스)
  unit/
    conftest.py            # 단위 테스트 전용 fixture (mock, stub)
    test_models.py
    test_services.py
  integration/
    conftest.py            # 통합 테스트 전용 fixture (실제 DB)
    test_api.py
    test_repository.py
  e2e/
    conftest.py            # E2E 전용 fixture (브라우저, 서버)
    test_workflows.py
```

```python
# tests/conftest.py - 전역 설정
import pytest

def pytest_configure(config):
    """pytest 설정 훅 - 전역 설정을 여기서 수행"""
    config.addinivalue_line("markers", "slow: 느린 테스트")

def pytest_collection_modifyitems(config, items):
    """테스트 수집 후 동적으로 마커 추가/필터링"""
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

# tests/unit/conftest.py - 단위 테스트 전용
@pytest.fixture(autouse=True)
def _disable_network(monkeypatch):
    """단위 테스트에서 실수로 네트워크 호출하는 것을 방지"""
    import socket
    def guard(*args, **kwargs):
        raise RuntimeError("단위 테스트에서 네트워크 호출 금지!")
    monkeypatch.setattr(socket, "socket", guard)
```

---

## 3. 내장 마커: skip, skipif, xfail

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

## 4. 커스텀 마커와 활용 패턴

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

## 5. 마커에서 fixture로 데이터 전달

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
