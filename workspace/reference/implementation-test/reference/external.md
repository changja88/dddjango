# Python 테스트 코드 작성 종합 가이드 (외부 자료 기반)

> 이 문서는 내부 자료에서 이미 다룬 기본 내용(pytest 기본 패턴, fixture, mock 기본, parametrize, conftest, monkeypatch, tmp_path)과 중복되지 않는 심화/확장 내용에 집중한다.

---

## 목차

1. [테스트 전략과 피라미드](#1-테스트-전략과-피라미드)
2. [pytest 심화 설정](#2-pytest-심화-설정)
3. [pytest 마커 시스템 심화](#3-pytest-마커-시스템-심화)
4. [pytest 플러그인 생태계](#4-pytest-플러그인-생태계)
5. [unittest.mock 심화](#5-unittestmock-심화)
6. [Property-Based Testing (Hypothesis)](#6-property-based-testing-hypothesis)
7. [테스트 데이터 팩토리 (factory_boy + Faker)](#7-테스트-데이터-팩토리-factory_boy--faker)
8. [시간 모킹 (freezegun / time-machine)](#8-시간-모킹-freezegun--time-machine)
9. [HTTP 모킹 (responses / aioresponses)](#9-http-모킹-responses--aioresponses)
10. [Docker 기반 통합 테스트 (testcontainers)](#10-docker-기반-통합-테스트-testcontainers)
11. [커버리지 설정 (coverage.py)](#11-커버리지-설정-coveragepy)
12. [멀티환경 테스트 (tox / nox)](#12-멀티환경-테스트-tox--nox)
13. [테스트 코드 품질 원칙](#13-테스트-코드-품질-원칙)
14. [테스트 안티패턴](#14-테스트-안티패턴)
15. [참고 서적](#15-참고-서적)

---

## 1. 테스트 전략과 피라미드

### 1.1 Martin Fowler의 테스트 피라미드

Mike Cohn이 "Succeeding with Agile"에서 처음 제안하고, Martin Fowler가 확장한 개념이다.

```
        /  E2E  \          <- 적게, 느리지만 높은 신뢰도
       /----------\
      / Integration \      <- 중간 수준
     /----------------\
    /    Unit Tests     \  <- 많이, 빠르고 저렴
   /--------------------\
```

**핵심 비율 (Google 기준)**:
- 단위 테스트: ~80%
- 통합 테스트: ~15%
- E2E 테스트: ~5%

**계층별 특성**:

| 구분 | 단위 | 통합 | E2E |
|------|------|------|-----|
| 속도 | 밀리초 | 초 | 분 |
| 범위 | 함수/클래스 | 모듈 간 | 전체 시스템 |
| 격리 | 완전 격리 | 부분 격리 | 실제 환경 |
| 유지비용 | 낮음 | 중간 | 높음 |

**Martin Fowler의 핵심 조언**: "상위 레벨 테스트에서 버그를 발견하면, 해당 버그를 재현하는 단위 테스트를 먼저 작성한 후 수정하라."

> 출처: [The Practical Test Pyramid - Ham Vocke](https://martinfowler.com/articles/practical-test-pyramid.html) (Martin Fowler 사이트에 게시), [Test Pyramid - Martin Fowler](https://martinfowler.com/bliki/TestPyramid.html)

### 1.2 Google의 SMURF 프레임워크

Google Testing Blog(2024.10)에서 발표한 테스트 피라미드의 확장 모델이다. 테스트 스위트가 성장하면서 단순한 피라미드만으로는 부족한 트레이드오프를 다루기 위한 5가지 차원을 제시한다.

**SMURF = Speed + Maintainability + Utilization + Reliability + Fidelity**

- **Speed(속도)**: 단위 테스트는 빠르므로 자주 실행할 수 있고, 문제를 일찍 발견한다.
- **Maintainability(유지보수성)**: 테스트 디버깅과 유지보수의 누적 비용은 빠르게 증가한다. 큰 시스템을 테스트할수록 의존성 변경과 요구사항 드리프트에 노출된다.
- **Utilization(활용도)**: 테스트가 실제로 결함을 발견하는 빈도와 효과.
- **Reliability(신뢰성)**: 테스트 결과의 일관성. flaky 테스트는 신뢰를 떨어뜨린다.
- **Fidelity(충실도)**: 실제 운영 환경(실제 DB, 실제 트래픽)에 가까운 테스트일수록 프로덕션 동작을 정확히 예측한다.

**핵심 인사이트**: 이 5개 차원은 종종 긴장 관계에 있다. 한 차원을 개선하면 다른 차원이 영향받을 수 있지만, 다른 차원을 해치지 않으면서 개선할 수 있다면 반드시 그렇게 해야 한다.

> 출처: [Google Testing Blog: SMURF: Beyond the Test Pyramid](https://testing.googleblog.com/2024/10/smurf-beyond-test-pyramid.html)

### 1.3 Google의 테스트 크기 분류

Google은 테스트를 유형(unit/integration/e2e)보다 **크기(size)**로 분류한다.

| 크기 | 제약 |
|------|------|
| Small | 단일 스레드, 단일 프로세스, 단일 머신, I/O 금지, sleep 금지, 블로킹 콜 금지 |
| Medium | 단일 머신, 다중 프로세스 허용 |
| Large | 다중 머신 허용, 네트워크 호출 허용 |

"테스트의 크기는 코드 줄 수가 아니라, 어떻게 실행되고 무엇이 허용되며 얼마나 많은 자원을 소비하는지로 결정된다." - Adam Bender, Software Engineering at Google

> 출처: [Software Engineering at Google - Chapter 11](https://abseil.io/resources/swe-book/html/ch11.html) (Adam Bender 저), [Google Testing Blog: Just Say No to More End-to-End Tests](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)

---

## 2. pytest 심화 설정

### 2.1 pyproject.toml 종합 설정

```toml
[tool.pytest.ini_options]
# 최소 pytest 버전 요구
minversion = "8.0"

# 테스트 검색 경로
testpaths = ["tests"]

# Python path에 추가할 디렉토리
pythonpath = ["src"]

# 기본 명령줄 옵션
addopts = [
    "-ra",                  # 실패/스킵 이유 요약 출력
    "-q",                   # 간결한 출력
    "--strict-markers",     # 미등록 마커 사용 시 에러
    "--strict-config",      # 설정 오류 시 에러
    "-v",                   # 상세 출력
    "--tb=short",           # 짧은 트레이스백
    "--no-header",          # 헤더 생략
]

# 테스트 파일/클래스/함수 패턴
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# 커스텀 마커 등록
markers = [
    "slow: 실행 시간이 긴 테스트",
    "integration: 외부 서비스 필요",
    "database: DB 연결 필요",
    "e2e: 엔드투엔드 테스트",
]

# 경고 필터
filterwarnings = [
    "error",                           # 모든 경고를 에러로
    "ignore::DeprecationWarning",      # DeprecationWarning 무시
]

# xfail 마크된 테스트가 통과하면 실패 처리
xfail_strict = true

# 로그 설정
log_cli = true
log_cli_level = "INFO"
```

### 2.2 conftest.py 계층 구조

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

> 출처: [pytest Configuration Reference](https://docs.pytest.org/en/stable/reference/customize.html), [Good Integration Practices - pytest](https://docs.pytest.org/en/stable/explanation/goodpractices.html)

---

## 3. pytest 마커 시스템 심화

### 3.1 내장 마커: skip, skipif, xfail

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

# 여러 조건 조합
@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Python 3.11+ 필요 (ExceptionGroup 지원)"
)
def test_exception_group():
    pass

# 예상 실패 (xfail)
@pytest.mark.xfail(reason="알려진 버그 #1234, 다음 릴리스에서 수정 예정")
def test_known_bug():
    assert buggy_function() == expected  # 실패해도 테스트 스위트는 통과

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

### 3.2 커스텀 마커와 마커 활용 패턴

```python
# pyproject.toml에 등록
# markers = ["slow: 느린 테스트", "database: DB 필요"]

import pytest

@pytest.mark.slow
def test_heavy_computation():
    """느린 테스트"""
    result = compute_for_minutes()
    assert result is not None

@pytest.mark.database
def test_user_creation():
    """DB 필요한 테스트"""
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
# 느린 테스트 제외
pytest -m "not slow"

# DB 테스트만 실행
pytest -m "database"

# 복합 조건: 느리지 않은 DB 테스트
pytest -m "database and not slow"

# 여러 마커 OR 조건
pytest -m "slow or database"
```

### 3.3 마커에서 fixture로 데이터 전달

```python
import pytest

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
    """마커를 통해 특정 DB 이름을 fixture에 전달"""
    result = db_connection.execute("SELECT COUNT(*) FROM events")
    assert result > 0
```

> 출처: [How to mark test functions - pytest docs](https://docs.pytest.org/en/stable/how-to/mark.html), [Working with custom markers - pytest docs](https://docs.pytest.org/en/stable/example/markers.html)

---

## 4. pytest 플러그인 생태계

### 4.1 pytest-xdist: 병렬 테스트 실행

테스트를 여러 CPU에 분산 실행하여 속도를 향상시킨다.

```bash
# 설치
pip install pytest-xdist

# 자동 CPU 감지 (물리 코어 수)
pytest -n auto

# 논리 코어 수 기준
pytest -n logical

# 명시적 워커 수 지정
pytest -n 8
```

**분산 전략**:

```bash
# load (기본): 라운드 로빈 분배
pytest -n auto --dist load

# loadscope: 모듈/클래스 단위로 같은 워커에 배치
# -> 비싼 모듈/클래스 레벨 fixture가 있을 때 유용
pytest -n auto --dist loadscope

# loadfile: 같은 파일의 테스트를 같은 워커에 배치
pytest -n auto --dist loadfile

# loadgroup: xdist_group 마커로 그룹 지정
pytest -n auto --dist loadgroup
```

```python
import pytest

# loadgroup 사용 예시: 같은 워커에서 실행되어야 하는 테스트
@pytest.mark.xdist_group("database_sequential")
def test_create_user():
    pass

@pytest.mark.xdist_group("database_sequential")
def test_update_user():
    pass
```

> 출처: [pytest-xdist Documentation](https://pytest-xdist.readthedocs.io/en/stable/distribution.html), [pytest-xdist PyPI](https://pypi.org/project/pytest-xdist/)

### 4.2 pytest-asyncio: 비동기 테스트

```bash
pip install pytest-asyncio
```

**설정 (pyproject.toml)**:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"   # auto | strict
```

**모드 비교**:
- **auto**: 모든 `async def` 테스트와 fixture를 자동으로 비동기 처리. 프로젝트가 asyncio만 사용할 때 권장.
- **strict**: `@pytest_asyncio.fixture`를 명시적으로 데코레이터로 붙여야 함. asyncio와 trio 같은 여러 비동기 라이브러리를 동시 사용할 때 권장.

```python
import pytest
import httpx

# auto 모드: @pytest.mark.asyncio 불필요
async def test_async_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/health")
    assert response.status_code == 200

# strict 모드에서의 async fixture
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client():
    async with httpx.AsyncClient(base_url="http://testserver") as client:
        yield client

async def test_with_client(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
```

> 출처: [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/en/latest/concepts.html), [pytest-asyncio Configuration](https://pytest-asyncio.readthedocs.io/en/latest/reference/configuration.html)

### 4.3 pytest-cov: 커버리지 통합

```bash
pip install pytest-cov

# 기본 사용
pytest --cov=src tests/

# HTML 리포트 생성
pytest --cov=src --cov-report=html tests/

# 최소 커버리지 강제
pytest --cov=src --cov-fail-under=80 tests/

# 분기 커버리지 포함
pytest --cov=src --cov-branch tests/

# xdist와 함께 사용 (자동 .coverage 파일 결합)
pytest -n auto --cov=src tests/
```

pytest-cov는 `coverage run`을 직접 사용하는 것보다 `.coverage` 파일 자동 삭제/결합과 기본 리포팅을 제공하며, xdist와 함께 사용할 때 각 워커의 커버리지 데이터를 자동으로 결합한다.

> 출처: [pytest-cov Documentation](https://pytest-cov.readthedocs.io/), [Distributed Testing - pytest-cov](https://pytest-cov.readthedocs.io/en/latest/xdist.html)

### 4.4 pytest-randomly: 테스트 순서 무작위화

테스트 간 암묵적 의존성을 발견하기 위해 실행 순서를 무작위로 섞는다.

```bash
pip install pytest-randomly

# 자동 적용 (설치만 하면 활성화)
pytest

# 시드 고정으로 재현 가능한 순서
pytest -p randomly --randomly-seed=12345

# 마지막 실행 시드로 재현
pytest -p randomly --randomly-seed=last

# 비활성화
pytest -p no:randomly
```

> 출처: [pytest-randomly PyPI](https://pypi.org/project/pytest-randomly/)

### 4.5 pytest-timeout: 테스트 시간 제한

```bash
pip install pytest-timeout

# 전역 타임아웃 설정 (초 단위)
pytest --timeout=30

# 개별 테스트에 마커로 적용
```

```python
import pytest

@pytest.mark.timeout(5)
def test_should_be_fast():
    """5초 안에 완료되어야 하는 테스트"""
    result = quick_operation()
    assert result is not None

@pytest.mark.timeout(120)
def test_allowed_to_be_slow():
    """2분까지 허용"""
    result = batch_processing()
    assert result.success
```

```toml
# pyproject.toml에서 전역 설정
[tool.pytest.ini_options]
timeout = 30
```

> 출처: [pytest-timeout PyPI](https://pypi.org/project/pytest-timeout/)

---

## 5. unittest.mock 심화

내부 자료에서 다룬 기본 mock/patch를 넘어서는 고급 패턴이다.

### 5.1 PropertyMock: 프로퍼티 모킹

```python
from unittest.mock import patch, PropertyMock

class DatabaseConnection:
    @property
    def is_connected(self):
        return self._check_connection()

    @property
    def latency_ms(self):
        return self._measure_latency()

# 프로퍼티를 모킹
def test_connection_status():
    with patch.object(
        DatabaseConnection,
        "is_connected",
        new_callable=PropertyMock,
        return_value=True
    ):
        conn = DatabaseConnection()
        assert conn.is_connected is True

# 프로퍼티가 호출될 때마다 다른 값 반환
def test_latency_fluctuation():
    with patch.object(
        DatabaseConnection,
        "latency_ms",
        new_callable=PropertyMock,
        side_effect=[10, 50, 200]  # 순서대로 반환
    ):
        conn = DatabaseConnection()
        assert conn.latency_ms == 10
        assert conn.latency_ms == 50
        assert conn.latency_ms == 200
```

### 5.2 AsyncMock: 비동기 함수 모킹

Python 3.8+에서 제공되며, 비동기 함수를 모킹할 때 사용한다.

```python
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

class AsyncService:
    async def fetch_data(self, url: str) -> dict:
        ...

    async def process(self) -> str:
        data = await self.fetch_data("https://api.example.com/data")
        return data["result"]

# AsyncMock 기본 사용
@pytest.mark.asyncio
async def test_async_service():
    service = AsyncService()
    service.fetch_data = AsyncMock(
        return_value={"result": "success"}
    )
    result = await service.process()
    assert result == "success"
    service.fetch_data.assert_awaited_once_with(
        "https://api.example.com/data"
    )

# async 컨텍스트 매니저 모킹
@pytest.mark.asyncio
async def test_async_context_manager():
    mock_session = MagicMock()
    # __aenter__와 __aexit__는 자동으로 AsyncMock
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = False

    async with mock_session as session:
        assert session is mock_session

# async 이터레이터 모킹
@pytest.mark.asyncio
async def test_async_iterator():
    mock_stream = MagicMock()
    mock_stream.__aiter__.return_value = iter([
        {"id": 1}, {"id": 2}, {"id": 3}
    ])

    results = []
    async for item in mock_stream:
        results.append(item)
    assert len(results) == 3
```

### 5.3 seal(): Mock 객체 봉인

`seal()`은 Mock 객체를 봉인하여, 미리 설정하지 않은 속성/메서드에 접근하면 에러를 발생시킨다. 오타나 잘못된 속성 접근을 방지한다.

```python
from unittest.mock import MagicMock, seal

def test_sealed_mock():
    user = MagicMock()
    user.name = "Alice"
    user.email = "alice@example.com"

    seal(user)

    # 설정된 속성은 정상 접근
    assert user.name == "Alice"

    # 미설정 속성 접근 시 AttributeError 발생
    with pytest.raises(AttributeError):
        _ = user.phone  # seal 되었으므로 에러

def test_sealed_with_spec():
    """create_autospec + seal = 가장 안전한 mock"""
    from unittest.mock import create_autospec

    class UserService:
        def get_user(self, user_id: int) -> dict: ...
        def delete_user(self, user_id: int) -> bool: ...

    mock_service = create_autospec(UserService)
    mock_service.get_user.return_value = {"id": 1, "name": "Alice"}
    seal(mock_service)

    # 스펙에 있는 메서드는 정상 호출
    assert mock_service.get_user(1) == {"id": 1, "name": "Alice"}

    # 스펙에 없는 메서드 호출 시 에러
    with pytest.raises(AttributeError):
        mock_service.update_user(1, name="Bob")
```

### 5.4 side_effect 고급 활용

```python
from unittest.mock import MagicMock

# 호출 인자에 따라 다른 값 반환
def test_dynamic_side_effect():
    def route_response(url):
        responses = {
            "/users": [{"id": 1}],
            "/products": [{"id": 100}],
        }
        if url in responses:
            return responses[url]
        raise ValueError(f"Unknown URL: {url}")

    mock_api = MagicMock(side_effect=route_response)

    assert mock_api("/users") == [{"id": 1}]
    assert mock_api("/products") == [{"id": 100}]

    with pytest.raises(ValueError):
        mock_api("/unknown")

# 순차적 결과 + 예외 혼합
def test_retry_logic():
    mock_call = MagicMock(side_effect=[
        ConnectionError("1차 실패"),
        ConnectionError("2차 실패"),
        {"status": "success"},  # 3차에 성공
    ])

    for attempt in range(3):
        try:
            result = mock_call()
            break
        except ConnectionError:
            continue

    assert result == {"status": "success"}
    assert mock_call.call_count == 3
```

> 출처: [Python unittest.mock 공식 문서](https://docs.python.org/3/library/unittest.mock.html), [unittest.mock - getting started](https://docs.python.org/3/library/unittest.mock-examples.html)

---

## 6. Property-Based Testing (Hypothesis)

전통적 테스트는 특정 입력값을 직접 선택하지만, Property-Based Testing은 **코드가 만족해야 할 속성(property)**을 정의하고, 프레임워크가 자동으로 수백 가지 입력을 생성하여 검증한다.

### 6.1 기본 사용법

```bash
pip install hypothesis
```

```python
from hypothesis import given, example, settings
from hypothesis import strategies as st

# 기본: 정수에 대한 속성 테스트
@given(st.integers())
def test_integer_negation_is_involutory(n):
    """이중 부정은 원래 값과 같다"""
    assert -(-n) == n

# 문자열 인코딩 라운드트립
@given(st.text())
def test_encode_decode_roundtrip(s):
    """UTF-8 인코딩 후 디코딩하면 원본과 같다"""
    assert s.encode("utf-8").decode("utf-8") == s

# 리스트 정렬 속성
@given(st.lists(st.integers()))
def test_sorted_list_properties(lst):
    sorted_lst = sorted(lst)
    # 길이 보존
    assert len(sorted_lst) == len(lst)
    # 정렬 순서 보장
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]
    # 원소 보존
    assert sorted(sorted_lst) == sorted_lst
```

### 6.2 전략(Strategies) 조합

```python
from hypothesis import strategies as st

# 기본 전략
integers = st.integers(min_value=0, max_value=100)
texts = st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L",)))
floats = st.floats(allow_nan=False, allow_infinity=False)

# 복합 전략: 사전 생성
user_strategy = st.fixed_dictionaries({
    "name": st.text(min_size=1, max_size=30),
    "age": st.integers(min_value=0, max_value=150),
    "email": st.emails(),
})

@given(user=user_strategy)
def test_user_validation(user):
    """자동 생성된 사용자 데이터로 검증 로직 테스트"""
    assert validate_user(user) or not is_valid_age(user["age"])

# 재귀적 전략: 트리 구조 생성
json_strategy = st.recursive(
    # 기본 케이스: 단순 값
    st.none() | st.booleans() | st.integers() | st.text(max_size=10),
    # 재귀 케이스: 리스트 또는 딕셔너리로 감싸기
    lambda children: st.lists(children, max_size=3)
                   | st.dictionaries(st.text(max_size=5), children, max_size=3),
    max_leaves=20,
)

@given(data=json_strategy)
def test_json_roundtrip(data):
    """임의의 JSON-like 구조의 직렬화/역직렬화 라운드트립"""
    import json
    assert json.loads(json.dumps(data)) == data
```

### 6.3 @example: 경계값 명시

```python
from hypothesis import given, example
from hypothesis import strategies as st

@given(st.integers())
@example(0)        # 반드시 0을 테스트
@example(-1)       # 반드시 -1을 테스트
@example(2**31)    # 큰 정수 경계값
def test_absolute_value(n):
    result = abs(n)
    assert result >= 0
    assert result == n or result == -n
```

### 6.4 settings로 실행 제어

```python
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

@settings(
    max_examples=500,           # 기본 100 -> 500으로 증가
    deadline=1000,              # 단일 예제 실행 제한 (ms)
    suppress_health_check=[
        HealthCheck.too_slow,   # 느린 테스트 경고 억제
    ],
)
@given(st.lists(st.integers(), min_size=100))
def test_large_list_sorting(lst):
    assert sorted(lst) == list(sorted(lst))

# CI에서는 더 많은 예제, 로컬에서는 적게
@settings(max_examples=int(os.environ.get("HYPOTHESIS_MAX_EXAMPLES", "100")))
@given(st.text())
def test_string_processing(s):
    process(s)  # 에러가 발생하지 않아야 함
```

### 6.5 Stateful Testing: 시퀀스 기반 테스트

상태를 가진 시스템(예: 데이터베이스, 캐시)을 테스트할 때, Hypothesis가 작업 시퀀스를 자동 생성한다.

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize
from hypothesis import strategies as st

class SetMachine(RuleBasedStateMachine):
    """파이썬 set과 동일하게 동작하는지 검증하는 상태 머신"""

    def __init__(self):
        super().__init__()
        self.model = set()       # 참조 모델 (정답)
        self.impl = MyCustomSet()  # 테스트 대상 구현체

    @rule(value=st.integers())
    def add_value(self, value):
        self.model.add(value)
        self.impl.add(value)
        assert self.impl.contains(value)

    @rule(value=st.integers())
    def remove_value(self, value):
        self.model.discard(value)
        self.impl.discard(value)
        assert not self.impl.contains(value) or value in self.model

    @rule()
    def check_size(self):
        assert len(self.impl) == len(self.model)

    @rule()
    def check_contents(self):
        for item in self.model:
            assert self.impl.contains(item)

# pytest가 자동으로 이 클래스를 테스트로 실행
TestSetMachine = SetMachine.TestCase
```

> 출처: [Hypothesis 공식 문서](https://hypothesis.readthedocs.io/), [Hypothesis Quickstart](https://hypothesis.readthedocs.io/en/latest/quickstart.html), [Stateful Testing](https://hypothesis.readthedocs.io/en/latest/stateful.html)

---

## 7. 테스트 데이터 팩토리 (factory_boy + Faker)

### 7.1 factory_boy 기본 개념

factory_boy는 테스트 객체 생성을 위한 "청사진" 역할을 한다. JSON fixture 파일 대신 Python 코드로 테스트 데이터를 선언적으로 정의한다.

```bash
pip install factory_boy faker
```

### 7.2 기본 팩토리 정의

```python
import factory
from factory import fuzzy
from myapp.models import User, Post, Comment

class UserFactory(factory.Factory):
    class Meta:
        model = User

    # Sequence: 고유한 값 보장
    username = factory.Sequence(lambda n: f"user_{n}")

    # Faker: 현실적인 가짜 데이터
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    # LazyAttribute: 다른 필드 값에 기반한 계산
    email = factory.LazyAttribute(
        lambda obj: f"{obj.first_name.lower()}.{obj.last_name.lower()}@example.com"
    )

    # LazyFunction: 인자 없이 매번 새 값 생성
    created_at = factory.LazyFunction(datetime.now)

    # Fuzzy: 범위 내 무작위 값
    age = fuzzy.FuzzyInteger(18, 80)
```

### 7.3 관계 처리: SubFactory, RelatedFactory

```python
class PostFactory(factory.Factory):
    class Meta:
        model = Post

    title = factory.Faker("sentence", nb_words=6)
    content = factory.Faker("paragraph", nb_sentences=5)

    # SubFactory: 부모 객체를 자동 생성
    author = factory.SubFactory(UserFactory)

class CommentFactory(factory.Factory):
    class Meta:
        model = Comment

    text = factory.Faker("sentence")
    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)

# 사용 예시
def test_comment_creation():
    comment = CommentFactory()
    # author, post, post.author가 모두 자동 생성됨
    assert comment.author is not None
    assert comment.post.author is not None

    # 특정 필드 오버라이드
    specific_user = UserFactory(username="admin")
    comment = CommentFactory(author=specific_user)
    assert comment.author.username == "admin"
```

### 7.4 Trait: 변형 객체 생성

```python
class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    status = "pending"
    total_amount = fuzzy.FuzzyDecimal(10.0, 500.0)
    shipped_at = None
    paid_at = None

    class Params:
        # Trait: 단일 불린 값으로 여러 필드를 한꺼번에 변경
        paid = factory.Trait(
            status="paid",
            paid_at=factory.LazyFunction(datetime.now),
        )
        shipped = factory.Trait(
            status="shipped",
            shipped_at=factory.LazyFunction(datetime.now),
            paid_at=factory.LazyFunction(datetime.now),
        )
        cancelled = factory.Trait(
            status="cancelled",
            total_amount=0,
        )

# 사용
def test_order_states():
    pending = OrderFactory()
    assert pending.status == "pending"

    paid = OrderFactory(paid=True)
    assert paid.status == "paid"
    assert paid.paid_at is not None

    shipped = OrderFactory(shipped=True)
    assert shipped.status == "shipped"

    cancelled = OrderFactory(cancelled=True)
    assert cancelled.total_amount == 0
```

### 7.5 배치 생성과 재현성

```python
def test_batch_creation():
    # 한 번에 10명의 사용자 생성
    users = UserFactory.create_batch(10)
    assert len(users) == 10

    # 오버라이드와 함께 배치 생성
    admins = UserFactory.create_batch(
        5,
        username=factory.Iterator(["admin1", "admin2", "admin3", "admin4", "admin5"]),
    )

def test_reproducible_data():
    """시드를 고정하여 재현 가능한 테스트 데이터"""
    import factory.random
    factory.random.reseed_random(42)

    user1 = UserFactory()
    factory.random.reseed_random(42)
    user2 = UserFactory()

    assert user1.first_name == user2.first_name
```

### 7.6 SQLAlchemy / Django ORM 통합

```python
# SQLAlchemy
class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = Session  # 세션 객체 지정
        sqlalchemy_session_persistence = "commit"  # commit | flush | none

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")

# Django
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "auth.User"  # 앱.모델 문자열도 가능
        django_get_or_create = ("username",)  # 중복 방지

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")
```

> 출처: [factory_boy 공식 문서](https://factoryboy.readthedocs.io/), [factory_boy Reference](https://factoryboy.readthedocs.io/en/stable/reference.html), [Using factory_boy with ORMs](https://factoryboy.readthedocs.io/en/stable/orms.html)

---

## 8. 시간 모킹 (freezegun / time-machine)

### 8.1 freezegun

순수 Python 구현으로 `datetime.now()`, `date.today()`, `time.time()` 등을 모킹한다.

```bash
pip install freezegun
```

```python
from freezegun import freeze_time
from datetime import datetime, date, timedelta

# 데코레이터로 사용
@freeze_time("2024-01-15 10:30:00")
def test_current_time():
    assert datetime.now() == datetime(2024, 1, 15, 10, 30, 0)
    assert date.today() == date(2024, 1, 15)

# 컨텍스트 매니저로 사용
def test_time_travel():
    with freeze_time("2024-06-01"):
        assert date.today() == date(2024, 6, 1)
    # 블록 밖에서는 실제 시간 복원
    assert date.today() != date(2024, 6, 1)

# 시간 흐름 시뮬레이션
@freeze_time("2024-01-01", tick=True)
def test_time_passes():
    """tick=True면 시간이 실제로 흐른다 (시작점만 고정)"""
    start = datetime.now()
    import time
    time.sleep(0.1)
    assert datetime.now() > start

# 시간 이동
def test_time_move():
    with freeze_time("2024-01-01") as frozen:
        assert date.today() == date(2024, 1, 1)
        frozen.move_to("2024-07-01")
        assert date.today() == date(2024, 7, 1)
        frozen.tick(timedelta(days=30))
        assert date.today() == date(2024, 7, 31)
```

### 8.2 time-machine

C 확장 기반으로 freezegun보다 100~200배 빠르다. C 레벨에서 시간 함수 포인터를 교체하므로, 프로젝트 크기와 무관하게 일정한 성능을 유지한다.

```bash
pip install time-machine
```

```python
import time_machine
from datetime import datetime, timezone

# 데코레이터로 사용
@time_machine.travel("2024-01-15 10:30:00")
def test_fixed_time():
    assert datetime.now().year == 2024

# 컨텍스트 매니저로 사용
def test_context_manager():
    with time_machine.travel("2024-06-01 12:00:00"):
        assert datetime.now().hour == 12

# 시간 이동
def test_time_shift():
    with time_machine.travel("2024-01-01", tick=False) as traveller:
        assert datetime.now() == datetime(2024, 1, 1)
        traveller.shift(timedelta(days=30))
        assert datetime.now() == datetime(2024, 1, 31)

# UTC 시간 고정
@time_machine.travel(datetime(2024, 1, 1, tzinfo=timezone.utc))
def test_utc_time():
    assert datetime.now(timezone.utc).year == 2024

# pytest fixture로 사용
@pytest.fixture
def frozen_time():
    with time_machine.travel("2024-03-15 09:00:00") as traveller:
        yield traveller

def test_with_fixture(frozen_time):
    assert datetime.now().month == 3
    frozen_time.shift(timedelta(hours=5))
    assert datetime.now().hour == 14
```

### 8.3 비교 및 선택 기준

| 항목 | freezegun | time-machine |
|------|-----------|--------------|
| 성능 | 느림 (순수 Python) | 100~200배 빠름 (C 확장) |
| CPython 외 지원 | 모든 Python 구현체 | CPython만 |
| 선택적 패치 | 가능 | 불가 (전체 패치) |
| 성숙도 | 오래된 커뮤니티, 안정적 | 비교적 최신, Adam Johnson 개발 |
| 추천 환경 | PyPy 사용, 선택적 패치 필요 | 일반 CPython 프로젝트 |

> 출처: [freezegun PyPI](https://pypi.org/project/freezegun/), [time-machine PyPI](https://pypi.org/project/time-machine/), [Time-machine vs Freezegun - Better Stack](https://betterstack.com/community/guides/testing/time-machine-vs-freezegun/), [Introducing time-machine - Adam Johnson](https://adamj.eu/tech/2020/06/03/introducing-time-machine/)

---

## 9. HTTP 모킹 (responses / aioresponses)

### 9.1 responses: requests 라이브러리 모킹

```bash
pip install responses
```

```python
import responses
import requests

# 데코레이터로 사용
@responses.activate
def test_simple_get():
    responses.add(
        responses.GET,
        "https://api.example.com/users/1",
        json={"id": 1, "name": "Alice"},
        status=200,
    )

    resp = requests.get("https://api.example.com/users/1")
    assert resp.json()["name"] == "Alice"
    assert len(responses.calls) == 1

# 여러 응답 등록
@responses.activate
def test_pagination():
    responses.add(
        responses.GET,
        "https://api.example.com/users",
        json={"page": 1, "data": [{"id": 1}]},
    )
    responses.add(
        responses.GET,
        "https://api.example.com/users",
        json={"page": 2, "data": []},
    )

    # 첫 번째 호출
    resp1 = requests.get("https://api.example.com/users")
    assert resp1.json()["page"] == 1

    # 두 번째 호출 (같은 URL이지만 다음 응답)
    resp2 = requests.get("https://api.example.com/users")
    assert resp2.json()["page"] == 2

# 콜백으로 동적 응답
@responses.activate
def test_dynamic_response():
    def request_callback(request):
        payload = request.body
        return (201, {}, json.dumps({"created": True}))

    responses.add_callback(
        responses.POST,
        "https://api.example.com/users",
        callback=request_callback,
    )

    resp = requests.post(
        "https://api.example.com/users",
        json={"name": "Bob"},
    )
    assert resp.status_code == 201

# 에러 시뮬레이션
@responses.activate
def test_connection_error():
    responses.add(
        responses.GET,
        "https://api.example.com/health",
        body=ConnectionError("서버 연결 실패"),
    )

    with pytest.raises(ConnectionError):
        requests.get("https://api.example.com/health")
```

### 9.2 aioresponses: aiohttp 모킹

```bash
pip install aioresponses
```

```python
from aioresponses import aioresponses
import aiohttp

# 컨텍스트 매니저로 사용
@pytest.mark.asyncio
async def test_async_api_call():
    with aioresponses() as mocked:
        mocked.get(
            "https://api.example.com/data",
            payload={"result": "success"},
            status=200,
        )

        async with aiohttp.ClientSession() as session:
            resp = await session.get("https://api.example.com/data")
            data = await resp.json()
            assert data["result"] == "success"

# POST 요청 모킹
@pytest.mark.asyncio
async def test_async_post():
    with aioresponses() as mocked:
        mocked.post(
            "https://api.example.com/users",
            payload={"id": 1, "created": True},
            status=201,
        )

        async with aiohttp.ClientSession() as session:
            resp = await session.post(
                "https://api.example.com/users",
                json={"name": "Alice"},
            )
            assert resp.status == 201

# 에러 시뮬레이션
@pytest.mark.asyncio
async def test_async_timeout():
    with aioresponses() as mocked:
        mocked.get(
            "https://api.example.com/slow",
            exception=asyncio.TimeoutError(),
        )

        async with aiohttp.ClientSession() as session:
            with pytest.raises(asyncio.TimeoutError):
                await session.get("https://api.example.com/slow")
```

### 9.3 HTTPretty: 소켓 레벨 인터셉트

HTTPretty는 Python의 `socket` 모듈을 몽키패치하여 HTTP 라이브러리에 관계없이 동작한다.

```bash
pip install httpretty
```

```python
import httpretty
import requests
import urllib.request

@httpretty.activate
def test_any_http_library():
    """requests, urllib 등 어떤 라이브러리든 인터셉트"""
    httpretty.register_uri(
        httpretty.GET,
        "https://api.example.com/data",
        body='{"key": "value"}',
        content_type="application/json",
    )

    # requests로 호출
    resp1 = requests.get("https://api.example.com/data")
    assert resp1.json()["key"] == "value"

    # urllib로 호출 (같은 URL이 인터셉트됨)
    resp2 = urllib.request.urlopen("https://api.example.com/data")
    assert b"value" in resp2.read()
```

**선택 가이드**:
| 라이브러리 | 대상 | 특징 |
|-----------|------|------|
| responses | requests | 가장 많이 사용, 간결한 API |
| aioresponses | aiohttp | async/await 전용 |
| HTTPretty | 모든 HTTP 라이브러리 | 소켓 레벨 인터셉트 |

> 출처: [responses - PyPI](https://pypi.org/project/responses/), [aioresponses - GitHub](https://github.com/pnuckowski/aioresponses), [HTTPretty Documentation](https://httpretty.readthedocs.io/)

---

## 10. Docker 기반 통합 테스트 (testcontainers)

testcontainers-python은 실제 Docker 컨테이너를 사용하여 통합 테스트를 수행한다. mock이나 인메모리 대체물이 아닌 **실제 서비스**로 테스트한다.

### 10.1 설치

```bash
# 기본 설치
pip install testcontainers

# 특정 서비스용 extras
pip install testcontainers[postgres]
pip install testcontainers[redis]
pip install testcontainers[kafka]
pip install testcontainers[mongodb]
```

### 10.2 PostgreSQL 통합 테스트

```python
import pytest
from testcontainers.postgres import PostgresContainer
import sqlalchemy

@pytest.fixture(scope="session")
def postgres_container():
    """세션 스코프: 전체 테스트 스위트에서 1번만 시작"""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="function")
def db_engine(postgres_container):
    """각 테스트마다 새 엔진 (트랜잭션 롤백으로 격리)"""
    engine = sqlalchemy.create_engine(
        postgres_container.get_connection_url()
    )
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """각 테스트를 트랜잭션으로 감싸서 격리"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_user_crud(db_session):
    """실제 PostgreSQL에서 CRUD 테스트"""
    user = User(name="Alice", email="alice@example.com")
    db_session.add(user)
    db_session.flush()

    found = db_session.query(User).filter_by(name="Alice").first()
    assert found is not None
    assert found.email == "alice@example.com"
```

### 10.3 Redis 통합 테스트

```python
from testcontainers.redis import RedisContainer
import redis

@pytest.fixture(scope="module")
def redis_client():
    with RedisContainer("redis:7-alpine") as container:
        client = redis.Redis.from_url(container.get_connection_url())
        yield client

@pytest.fixture(autouse=True)
def _clean_redis(redis_client):
    """각 테스트 후 Redis 데이터 초기화"""
    yield
    redis_client.flushall()

def test_cache_set_get(redis_client):
    redis_client.set("key", "value")
    assert redis_client.get("key") == b"value"

def test_cache_expiry(redis_client):
    redis_client.setex("temp", 1, "temporary")
    assert redis_client.get("temp") == b"temporary"
    import time
    time.sleep(1.1)
    assert redis_client.get("temp") is None
```

### 10.4 여러 서비스 동시 사용

```python
@pytest.fixture(scope="session")
def services():
    """여러 서비스를 한 번에 시작"""
    with PostgresContainer("postgres:16") as pg, \
         RedisContainer("redis:7") as redis_container:
        yield {
            "postgres_url": pg.get_connection_url(),
            "redis_url": redis_container.get_connection_url(),
        }

def test_full_integration(services):
    """실제 DB + 실제 캐시로 통합 테스트"""
    db = create_engine(services["postgres_url"])
    cache = redis.from_url(services["redis_url"])

    # 비즈니스 로직 테스트
    user_service = UserService(db=db, cache=cache)
    user = user_service.create("Alice")
    assert user_service.get_cached(user.id) is not None
```

> 출처: [testcontainers-python 공식 문서](https://testcontainers-python.readthedocs.io/), [Testcontainers Getting Started](https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/), [Testcontainers for Python - Docker Docs](https://docs.docker.com/guides/testcontainers-python-getting-started/)

---

## 11. 커버리지 설정 (coverage.py)

### 11.1 pyproject.toml 종합 설정

```toml
[tool.coverage.run]
# 측정 대상 소스 디렉토리
source = ["src"]

# 분기 커버리지 활성화
branch = true

# 측정 제외 패턴 (정규식)
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/__init__.py",
    "*/conftest.py",
]

# 병렬 실행 시 데이터 결합
parallel = true

[tool.coverage.report]
# 최소 커버리지 (미달 시 실패)
fail_under = 80

# 리포트에서 제외할 라인 패턴
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
    "raise NotImplementedError",
    "pass",
    "\\.\\.\\.",           # 추상 메서드의 ...
    "@abstractmethod",
]

# 부분 분기 제외 패턴
exclude_also = [
    "if typing.TYPE_CHECKING:",
]

# 완전히 커버되지 않은 파일 표시
show_missing = true

# 정밀도 (소수점 자릿수)
precision = 2

# 빈 파일 건너뛰기
skip_empty = true

[tool.coverage.html]
# HTML 리포트 출력 디렉토리
directory = "htmlcov"

# CSS 파일 제목
title = "My Project Coverage"

[tool.coverage.xml]
# XML 리포트 출력 파일 (CI 연동용)
output = "coverage.xml"
```

### 11.2 활용 명령어

```bash
# 커버리지 측정 실행
coverage run -m pytest tests/

# 콘솔 리포트
coverage report

# HTML 리포트
coverage html

# XML 리포트 (CI 연동)
coverage xml

# 여러 실행 결과 결합 (병렬 실행 후)
coverage combine
coverage report
```

> 출처: [Coverage.py Configuration Reference](https://coverage.readthedocs.io/en/latest/config.html)

---

## 12. 멀티환경 테스트 (tox / nox)

여러 Python 버전과 의존성 조합에서 테스트를 자동 실행하는 도구이다. 라이브러리 개발 시 필수적이다.

### 12.1 tox: 선언적 설정

```bash
pip install tox
```

**pyproject.toml 방식 (tox 4+)**:

```toml
[tool.tox]
env_list = ["py311", "py312", "py313", "lint", "typecheck"]

[tool.tox.env_run_base]
description = "run tests"
deps = [
    "pytest>=8.0",
    "pytest-cov",
]
commands = [
    ["pytest", "--cov=src", "tests/"],
]

[tool.tox.env.lint]
description = "run linters"
deps = ["ruff"]
commands = [["ruff", "check", "src/"]]

[tool.tox.env.typecheck]
description = "run type checker"
deps = ["mypy"]
commands = [["mypy", "src/"]]
```

**실행**:

```bash
# 모든 환경 실행
tox

# 특정 환경만
tox -e py312

# 여러 환경 지정
tox -e py311,py312

# 병렬 실행
tox -p auto
```

### 12.2 nox: Python 코드 기반 설정

tox보다 유연하며, 설정 파일이 일반 Python 코드이므로 복잡한 로직을 작성할 수 있다.

```bash
pip install nox
```

**noxfile.py**:

```python
import nox

# 전역 설정
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["tests", "lint"]

@nox.session(python=["3.11", "3.12", "3.13"])
def tests(session):
    """여러 Python 버전에서 테스트 실행"""
    session.install("pytest", "pytest-cov")
    session.install("-e", ".")
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "tests/",
    )

@nox.session
def lint(session):
    """린트 검사"""
    session.install("ruff")
    session.run("ruff", "check", "src/", "tests/")

@nox.session
def typecheck(session):
    """타입 검사"""
    session.install("mypy", ".")
    session.run("mypy", "src/")

# 파라미터화: Django 버전별 테스트
@nox.session
@nox.parametrize("django", ["4.2", "5.0", "5.1"])
def test_django(session, django):
    session.install(f"django=={django}", "pytest", "pytest-django")
    session.install("-e", ".")
    session.run("pytest", "tests/")

# 커버리지 리포트 생성 전용 세션
@nox.session
def coverage(session):
    """커버리지 리포트 생성"""
    session.install("coverage[toml]")
    session.run("coverage", "combine")
    session.run("coverage", "report", "--fail-under=80")
    session.run("coverage", "html")
```

**실행**:

```bash
# 기본 세션 실행
nox

# 특정 세션
nox -s tests

# 파라미터화된 세션 중 하나
nox -s "test_django(django='5.1')"

# 가상환경 재사용 (개발 시 빠른 반복)
nox -R

# 사용 가능한 세션 목록
nox -l
```

### 12.3 tox vs nox 비교

| 항목 | tox | nox |
|------|-----|-----|
| 설정 형식 | INI/TOML (선언적) | Python 코드 (프로그래밍 가능) |
| 학습 곡선 | 낮음 | 약간 높음 |
| 유연성 | 중간 | 높음 (조건문, 반복문 사용 가능) |
| 커뮤니티 | 더 오래됨, 넓은 사용자 기반 | 성장 중, Google 프로젝트에서 사용 |
| 추천 | 단순한 멀티버전 테스트 | 복잡한 빌드/테스트 워크플로 |

> 출처: [tox Documentation](https://tox.wiki/en/latest/user_guide.html), [Nox Documentation](https://nox.thea.codes/), [Automating Python Multi-Version Testing - DZone](https://dzone.com/articles/automating-python-testing-across-versions-with-tox-and-nox)

---

## 13. 테스트 코드 품질 원칙

### 13.1 FIRST 원칙

Robert C. Martin이 "Clean Code"에서 제안한 좋은 테스트의 5가지 원칙이다.

**F - Fast (빠르게)**
테스트는 빨라야 한다. 느리면 자주 실행하지 않게 되고, 문제를 늦게 발견한다.

```python
# 나쁜 예: 실제 API 호출
def test_slow_api_call():
    response = requests.get("https://real-api.example.com/data")
    assert response.status_code == 200

# 좋은 예: mock으로 빠르게
@responses.activate
def test_fast_api_call():
    responses.add(responses.GET, "https://real-api.example.com/data", status=200)
    response = requests.get("https://real-api.example.com/data")
    assert response.status_code == 200
```

**I - Independent (독립적으로)**
테스트 간에 상태를 공유하지 않는다. 어떤 순서로 실행해도 결과가 같아야 한다.

```python
# 나쁜 예: 전역 상태 공유
_created_user_id = None

def test_create_user():
    global _created_user_id
    _created_user_id = create_user("Alice")

def test_get_user():
    user = get_user(_created_user_id)  # 위 테스트에 의존!
    assert user.name == "Alice"

# 좋은 예: 각 테스트가 독립적
def test_create_user(db_session):
    user_id = create_user("Alice")
    assert user_id is not None

def test_get_user(db_session):
    user_id = create_user("Bob")  # 자체적으로 데이터 생성
    user = get_user(user_id)
    assert user.name == "Bob"
```

**R - Repeatable (반복 가능하게)**
어떤 환경에서든 같은 결과를 내야 한다. 외부 서비스, 시간, 난수에 의존하지 않는다.

```python
# 나쁜 예: 현재 시간에 의존
def test_is_weekend():
    assert is_weekend() == (datetime.now().weekday() >= 5)

# 좋은 예: 시간을 고정
@time_machine.travel("2024-01-13")  # 토요일
def test_is_weekend_saturday():
    assert is_weekend() is True

@time_machine.travel("2024-01-15")  # 월요일
def test_is_weekend_monday():
    assert is_weekend() is False
```

**S - Self-Validating (자가 검증)**
테스트 결과를 사람이 수동으로 확인할 필요 없이, assert로 자동 판별되어야 한다.

```python
# 나쁜 예: print로 수동 확인
def test_calculation():
    result = complex_calculation(42)
    print(f"결과: {result}")  # 사람이 눈으로 확인??

# 좋은 예: 자동 검증
def test_calculation():
    result = complex_calculation(42)
    assert result == 1764
    assert isinstance(result, int)
```

**T - Timely (적시에)**
프로덕션 코드를 작성하기 직전 또는 직후에 테스트를 작성한다. TDD에서는 프로덕션 코드보다 먼저.

> 출처: Robert C. Martin, "Clean Code: A Handbook of Agile Software Craftsmanship" (2008), [FIRST Principles - DZone](https://dzone.com/articles/first-principles-solid-rules-for-tests)

### 13.2 AAA 패턴 심화 (Arrange-Act-Assert)

Bill Wake가 처음 명명한 테스트 구조화 패턴이다.

```python
def test_user_discount_calculation():
    # ---- Arrange (준비) ----
    # 테스트에 필요한 모든 전제조건과 입력값을 설정
    user = UserFactory(membership="gold", joined_years_ago=3)
    product = ProductFactory(price=100.00, category="electronics")
    discount_service = DiscountService()

    # ---- Act (실행) ----
    # 테스트하려는 동작을 정확히 하나만 실행
    discount = discount_service.calculate(user, product)

    # ---- Assert (검증) ----
    # 결과를 검증 (논리적으로 관련된 assert를 그룹화)
    assert discount.percentage == 15.0
    assert discount.final_price == 85.00
    assert discount.reason == "골드 회원 3년차 할인"
```

**AAA 심화 규칙**:

1. **Act 섹션은 가능한 한 줄**: 테스트 대상 동작을 명확히 하기 위해 Act은 단일 함수 호출이어야 한다.
2. **여러 AAA 블록 금지**: 하나의 테스트에 여러 Act-Assert 쌍이 있으면 테스트를 분리해야 한다.
3. **Arrange가 복잡하면 fixture로 추출**: 설정 코드가 길어지면 fixture나 팩토리 함수로 분리한다.

```python
# 나쁜 예: 여러 AAA 블록
def test_user_lifecycle():
    # AAA 블록 1
    user = create_user("Alice")
    assert user.is_active

    # AAA 블록 2 (이것은 별도 테스트여야 함)
    deactivate(user)
    assert not user.is_active

    # AAA 블록 3
    reactivate(user)
    assert user.is_active

# 좋은 예: 분리된 테스트
def test_new_user_is_active():
    user = create_user("Alice")
    assert user.is_active

def test_deactivated_user_is_inactive():
    user = create_user("Alice")
    deactivate(user)
    assert not user.is_active

def test_reactivated_user_is_active():
    user = create_user("Alice")
    deactivate(user)
    reactivate(user)
    assert user.is_active
```

> 출처: [AAA Pattern - Semaphore](https://semaphore.io/blog/aaa-pattern-test-automation), [Manning: Making Better Unit Tests](https://freecontent.manning.com/making-better-unit-tests-part-1-the-aaa-pattern/)

---

## 14. 테스트 안티패턴

### 14.1 코드 수준 안티패턴

테스트 코드에서 흔히 발생하는 나쁜 패턴들이다.

**The Liar (거짓말쟁이)**
실행은 되지만 실제로 검증하는 것이 없는 테스트.

```python
# 나쁜 예
def test_user_creation():
    user = create_user("Alice")
    assert user is not None  # 이것만으로는 올바른 생성을 검증하지 못함

# 좋은 예
def test_user_creation():
    user = create_user("Alice")
    assert user.name == "Alice"
    assert user.is_active is True
    assert user.created_at is not None
```

**Excessive Setup (과도한 설정)**
수백 줄의 설정 코드로 테스트 대상이 무엇인지 파악하기 어렵다.

```python
# 나쁜 예: 모든 것을 직접 설정
def test_order_total():
    db = create_database()
    db.connect()
    user = db.create_user(name="Alice", email="a@b.com", ...)
    product1 = db.create_product(name="Widget", price=10, ...)
    product2 = db.create_product(name="Gadget", price=20, ...)
    cart = db.create_cart(user_id=user.id)
    # ... 50줄 더 ...
    assert order.total == 30

# 좋은 예: fixture와 팩토리로 단순화
def test_order_total(order_with_two_items):
    assert order_with_two_items.total == 30
```

**The Giant (거인)**
수천 줄에 수십 개의 assert를 포함하는 테스트. 시스템이 God Object일 가능성을 나타낸다.

**Slow Poke (느림보)**
실행에 수 분이 걸리는 테스트. 개발자가 테스트를 피하게 만든다.

**The Inspector (검사관)**
구현 세부사항을 너무 많이 알고 있어서, 리팩토링할 때마다 깨진다.

```python
# 나쁜 예: 내부 구현에 결합
def test_sort_uses_quicksort(mocker):
    spy = mocker.spy(sort_module, "_partition")
    sort_module.sort([3, 1, 2])
    spy.assert_called()  # 정렬 알고리즘 변경하면 깨짐

# 좋은 예: 동작만 검증
def test_sort_returns_sorted_list():
    assert sort_module.sort([3, 1, 2]) == [1, 2, 3]
```

**Free Ride (무임승차)**
기존 테스트에 관련 없는 assert를 추가하는 패턴.

```python
# 나쁜 예: 하나의 테스트에 관련 없는 검증 추가
def test_create_user():
    user = create_user("Alice")
    assert user.name == "Alice"
    assert user.email_is_valid()  # 별도 테스트여야 함
    assert user.default_settings_applied()  # 별도 테스트여야 함
```

**Mockery (과도한 모킹)**
너무 많은 mock으로 실제 시스템을 전혀 테스트하지 않게 되는 패턴.

```python
# 나쁜 예: 모든 것을 mock
def test_process_order(mocker):
    mock_db = mocker.Mock()
    mock_cache = mocker.Mock()
    mock_email = mocker.Mock()
    mock_payment = mocker.Mock()
    mock_inventory = mocker.Mock()
    mock_logger = mocker.Mock()
    # 6개의 mock... 실제로 뭘 테스트하는 건지?

# 좋은 예: 외부 의존성만 mock, 핵심 로직은 실제 실행
def test_process_order(mocker):
    mock_payment = mocker.Mock(return_value=PaymentResult(success=True))
    service = OrderService(payment_gateway=mock_payment)
    result = service.process(order)
    assert result.is_completed
```

**Generous Leftovers (관대한 잔여물)**
한 테스트가 남긴 데이터를 다른 테스트가 사용하는 패턴.

**Local Hero (로컬 영웅)**
특정 개발 환경에서만 통과하는 테스트.

**Secret Catcher (비밀 포획자)**
assert 없이 예외가 발생하지 않는 것만으로 "통과"하는 테스트.

**Dodger (회피자)**
쉬운 테스트만 작성하고 핵심 비즈니스 로직은 테스트하지 않는 패턴.

**Cuckoo (뻐꾸기)**
관련 없는 테스트 클래스/파일에 들어있는 테스트.

**The Nitpicker (트집잡이)**
의미 없는 세부사항까지 검증하는 테스트.

```python
# 나쁜 예: 전체 HTML 비교
def test_render_page():
    html = render_page()
    assert html == "<html><head>...</head><body>...</body></html>"  # 깨지기 쉬움

# 좋은 예: 중요한 부분만 검증
def test_render_page():
    html = render_page()
    assert "<h1>Welcome</h1>" in html
    assert "user-dashboard" in html
```

### 14.2 전략 수준 안티패턴

Codepipes Blog의 "Software Testing Anti-patterns"에서 정리한 상위 수준 안티패턴이다.

1. **단위 테스트만 있고 통합 테스트 없음** (또는 그 반대)
2. **잘못된 테스트 유형 선택**: 단위 테스트로 충분한데 E2E로 작성
3. **테스트를 개발 프로세스의 별도 단계로 취급**: 코딩 후 나중에 한꺼번에 테스트 작성
4. **테스트 코드를 프로덕션 코드보다 낮은 품질로 작성**
5. **비결정적(flaky) 테스트를 방치**
6. **느린 테스트를 개선하지 않음**
7. **테스트를 수동으로 실행** (CI/CD 미연동)
8. **코드 커버리지에만 집착**: 커버리지 100%가 버그 0%를 의미하지 않음

> 출처: [Software Testing Anti-patterns - Codepipes Blog](https://blog.codepipes.com/testing/software-testing-antipatterns.html), [Unit Testing Anti-Patterns Full List - DZone](https://dzone.com/articles/unit-testing-anti-patterns-full-list), [Unit Testing Anti-Patterns - Yegor Bugayenko](https://www.yegor256.com/2018/12/11/unit-testing-anti-patterns.html)

---

## 15. 참고 서적

### 15.1 "Python Testing with pytest" (2nd Edition) - Brian Okken

**출판**: Pragmatic Bookshelf, 2022 (Python 3.10 + pytest 7 기준)

pytest 전문서로, 다음 심화 주제를 다룬다:
- **고급 fixture 패턴**: 마커에서 fixture로 데이터 전달, 동적 fixture 생성, fixture 파라미터화 심화
- **플러그인 개발**: 직접 pytest 플러그인을 만드는 방법, 훅 시스템 이해
- **conftest.py 계층**: 디렉토리별 conftest 배치와 fixture 스코프 관리
- **tox/coverage 통합**: 멀티환경 테스트와 커버리지 측정 연동
- **기존 unittest 테스트와의 공존**: unittest 기반 기존 테스트를 pytest에서 실행

> 출처: [Python Testing with pytest, 2nd Edition - Pragmatic Bookshelf](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)

### 15.2 "Test-Driven Development with Python" - Harry Percival

**출판**: O'Reilly (무료 온라인 공개)

Django 기반 웹 애플리케이션의 TDD를 다룬다:
- **기능 테스트(Functional Test)**: Selenium을 사용한 브라우저 기반 E2E 테스트
- **Outside-In TDD**: 기능 테스트 -> 단위 테스트 -> 구현 순서의 워크플로
- **JavaScript 테스트**: 프론트엔드 코드 테스트 방법
- **CI/CD 연동**: 테스트 자동화 파이프라인 구성

> 출처: [Test-Driven Development with Python - O'Reilly](https://www.oreilly.com/library/view/test-driven-development-with/9781491958698/)

### 15.3 "Architecture Patterns with Python" - Harry Percival, Bob Gregory

**출판**: O'Reilly, 2020 (무료 온라인 공개: cosmicpython.com)

테스트 전략을 아키텍처 관점에서 다룬다:
- **Repository 패턴과 Fake Repository**: 단위 테스트에서 DB 의존성 제거
- **Service Layer 테스트**: FakeRepository를 사용한 서비스 레이어 단위 테스트
- **Edge-to-Edge 테스트**: Fake과 의존성 주입을 활용한 경계 간 테스트
- **E2E 테스트 전략**: 실제 DB와 API를 사용하는 최소한의 E2E 테스트
- **포트와 어댑터(Hexagonal Architecture)**에서의 테스트 계층

> 출처: [Architecture Patterns with Python - O'Reilly](https://www.oreilly.com/library/view/architecture-patterns-with/9781492052197/)

### 15.4 "Unit Testing Principles, Practices, and Patterns" - Vladimir Khorikov

**출판**: Manning, 2020

언어 독립적인 테스트 원칙서로, Python에도 직접 적용 가능하다:
- **좋은 단위 테스트의 4대 기둥**: 회귀 방지, 리팩토링 내성, 빠른 피드백, 유지보수성
- **런던파 vs 고전파**: Mock 중심 테스트 vs 상태 중심 테스트의 비교
- **테스트 더블 분류**: Dummy, Stub, Spy, Mock, Fake의 정확한 구분

> 출처: [Unit Testing - Manning](https://www.manning.com/books/unit-testing)

---

## 부록: 도구 설치 한눈에 보기

```bash
# 핵심 테스트 프레임워크
pip install pytest

# pytest 플러그인
pip install pytest-cov pytest-xdist pytest-asyncio pytest-timeout pytest-randomly pytest-mock

# Property-Based Testing
pip install hypothesis

# 테스트 데이터
pip install factory_boy faker

# 시간 모킹
pip install freezegun time-machine

# HTTP 모킹
pip install responses aioresponses httpretty

# Docker 통합 테스트
pip install testcontainers[postgres,redis,kafka]

# 커버리지
pip install coverage[toml]

# 멀티환경 테스트
pip install tox  # 또는 nox
```

---

> 이 문서는 공식 문서, 권위 있는 서적, Google/Martin Fowler의 테스트 전략 자료를 기반으로 작성되었다. 각 섹션의 출처를 참고하여 최신 공식 문서를 확인하는 것을 권장한다.
