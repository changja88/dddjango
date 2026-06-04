# Python 테스트 코드 작성 종합 가이드


> 이 문서는 테스트 코드 **작성법**에 집중한다. TDD 방법론(Red-Green-Refactor 등)은 `workspace/reference/discipline-tdd/reference/final.md`에서 다룬다.

---

## 목차

1. [테스트 전략과 피라미드](#1-테스트-전략과-피라미드)
2. [테스트 더블 분류 체계](#2-테스트-더블-분류-체계)
3. [pytest 기본 구조와 Fixture](#3-pytest-기본-구조와-fixture)
4. [pytest 심화 설정](#4-pytest-심화-설정)
5. [pytest 마커 시스템](#5-pytest-마커-시스템)
6. [pytest 플러그인 생태계](#6-pytest-플러그인-생태계)
7. [Mock과 테스트 더블 실전](#7-mock과-테스트-더블-실전)
8. [Property-Based Testing (Hypothesis)](#8-property-based-testing-hypothesis)
9. [테스트 데이터 팩토리 (factory_boy + Faker)](#9-테스트-데이터-팩토리-factory_boy--faker)
10. [시간 모킹 (freezegun / time-machine)](#10-시간-모킹-freezegun--time-machine)
11. [HTTP 모킹 (responses / aioresponses)](#11-http-모킹-responses--aioresponses)
12. [Docker 기반 통합 테스트 (testcontainers)](#12-docker-기반-통합-테스트-testcontainers)
13. [커버리지 설정 (coverage.py)](#13-커버리지-설정-coveragepy)
14. [멀티환경 테스트 (tox / nox)](#14-멀티환경-테스트-tox--nox)
15. [테스트 코드 품질 원칙](#15-테스트-코드-품질-원칙)
16. [테스트 안티패턴](#16-테스트-안티패턴)
17. [Mutation Testing](#17-mutation-testing-mutmut)
18. [BDD pytest-bdd 구현](#18-bdd-pytest-bdd-구현)
19. [Django Ninja TestClient API 계약 테스트](#19-django-ninja-testclient-api-계약-테스트)
20. [Idempotency와 동시성 테스트](#20-idempotency와-동시성-테스트)
21. [테스트 디버깅 기법](#21-테스트-디버깅-기법)
22. [참고 문헌](#22-참고-문헌)

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

> 출처: [The Practical Test Pyramid - Ham Vocke](https://martinfowler.com/articles/practical-test-pyramid.html), [Test Pyramid - Martin Fowler](https://martinfowler.com/bliki/TestPyramid.html)

### 1.2 Google의 SMURF 프레임워크

Google Testing Blog(2024.10)에서 발표한 테스트 피라미드의 확장 모델이다. 테스트 스위트가 성장하면서 단순한 피라미드만으로는 부족한 트레이드오프를 다루기 위한 5가지 차원을 제시한다.

**SMURF = Speed + Maintainability + Utilization + Reliability + Fidelity**

- **Speed(속도)**: 단위 테스트는 빠르므로 자주 실행할 수 있고, 문제를 일찍 발견한다.
- **Maintainability(유지보수성)**: 테스트 디버깅과 유지보수의 누적 비용은 빠르게 증가한다.
- **Utilization(활용도)**: 테스트가 실제로 결함을 발견하는 빈도와 효과.
- **Reliability(신뢰성)**: 테스트 결과의 일관성. flaky 테스트는 신뢰를 떨어뜨린다.
- **Fidelity(충실도)**: 실제 운영 환경에 가까운 테스트일수록 프로덕션 동작을 정확히 예측한다.

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

> 출처: [Software Engineering at Google - Chapter 11](https://abseil.io/resources/swe-book/html/ch11.html), [Google Testing Blog: Just Say No to More End-to-End Tests](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)

---

## 2. 테스트 더블 분류 체계

Meszaros의 5분류를 기본으로 사용한다. 테스트 의도를 명확히 전달하고, Mock과 Stub의 혼용을 방지하기 위해 세밀한 분류가 필요하다. [Unit Testing - Khorikov]

| 종류 | 역할 | 예시 |
|------|------|------|
| **Dummy** | 빈 값 전달용. 호출되지 않는다 | 생성자에 넣는 `None` |
| **Stub** | 미리 정해진 값을 반환한다 | `mock.return_value = 25.0` |
| **Spy** | 호출 기록을 남겨 나중에 검증한다 | `assert_called_once_with(...)` |
| **Mock** | 호출 자체를 검증한다 (통신 기반 테스트) | `mock.assert_called_with("서울")` |
| **Fake** | 간소화된 실제 구현을 제공한다 | 메모리 내 데이터베이스, FakeRepository |

> 출처: [Unit Testing Principles, Practices, and Patterns - Vladimir Khorikov](https://www.manning.com/books/unit-testing)

---

## 3. pytest 기본 구조와 Fixture

### 3.1 pytest 기본 구조 [파이썬코딩의기술]

```python
# test_calculator.py
import pytest


class TestCalculator:
    """연관된 행동 방식을 TestCase 하위 클래스로 그룹화한다"""

    def test_add_positive_numbers(self):
        assert add(2, 3) == 5

    def test_add_negative_numbers(self):
        assert add(-1, -2) == -3

    def test_add_raises_on_invalid_type(self):
        with pytest.raises(TypeError):
            add("a", 1)
```

### 3.2 Fixture (setUp/tearDown) [테스트주도 개발 + 파이썬코딩의기술]

여러 테스트에서 공통으로 사용하는 객체들을 생성할 때 픽스처를 사용한다.

**xUnit 스타일 (unittest)**:

```python
from unittest import TestCase


class TestDatabase(TestCase):
    def setUp(self):
        """각 테스트 메서드 실행 전에 호출"""
        self.db = create_test_database()
        self.db.connect()

    def tearDown(self):
        """각 테스트 메서드 실행 후에 호출 (자원 해제)"""
        self.db.disconnect()

    def test_query(self):
        result = self.db.query("SELECT 1")
        self.assertEqual(result, 1)
```

**pytest 스타일 (권장)**:

```python
import pytest


@pytest.fixture
def db():
    """픽스처: 테스트 전 DB 연결, 테스트 후 해제"""
    database = create_test_database()
    database.connect()
    yield database  # 테스트에 database 제공
    database.disconnect()  # teardown


@pytest.fixture
def empty_cart():
    return ShoppingCart()


def test_query(db):
    result = db.query("SELECT 1")
    assert result == 1


def test_empty_cart_total(empty_cart):
    assert empty_cart.total() == 0
```

**모듈 단위 픽스처** (비용이 큰 통합 테스트용) [파이썬코딩의기술]:

```python
import pytest


@pytest.fixture(scope="module")
def database_server():
    """모듈당 한 번만 실행 -- 비싼 자원 초기화"""
    server = start_database_server()
    yield server
    server.shutdown()


@pytest.fixture
def db_connection(database_server):
    """각 테스트마다 새 연결"""
    conn = database_server.connect()
    yield conn
    conn.close()
```

### 3.3 xUnit 패턴과 pytest 매핑 [테스트주도 개발 + 파이썬코딩의기술]

| xUnit 개념 | pytest 대응 |
|-----------|-----------|
| setUp() | `@pytest.fixture` 또는 `setup_method()` |
| tearDown() | fixture의 `yield` 이후 코드 |
| setUpModule() | `@pytest.fixture(scope="module")` |
| tearDownModule() | module 스코프 fixture의 teardown |
| TestSuite | `pytest.mark` 또는 디렉토리 구조 |

### 3.4 단언(Assertion) [테스트주도 개발]

프로그램이 자동으로 코드가 동작하는지에 대한 판단을 수행하도록 해야 한다. 판단 결과가 불리언 값이어야 하며 컴퓨터에 의해 검증되어야 한다.

```python
# pytest의 다양한 단언 패턴
def test_assertions():
    # 동등성
    assert result == expected

    # 포함
    assert "error" in message

    # 예외
    with pytest.raises(ValueError, match="invalid"):
        parse_input("bad")

    # 근사값 (부동소수점)
    assert result == pytest.approx(3.14, abs=0.01)
```

### 3.5 예외 테스트 [테스트주도 개발]

예외가 발생하는 것이 정상인 경우에는, 예상되는 예외를 잡아서 무시하고, 예외가 발생하지 않은 경우에 한해서 테스트가 실패하게 만든다.

```python
def test_invalid_input_raises():
    with pytest.raises(ValueError) as exc_info:
        process_input(-1)
    assert "음수" in str(exc_info.value)
```

### 3.6 파라미터화 테스트

```python
@pytest.mark.parametrize("input_val, expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (-1, 1),
])
def test_square(input_val, expected):
    assert square(input_val) == expected
```

### 3.7 conftest.py를 활용한 공유 픽스처

```python
# conftest.py
import pytest


@pytest.fixture(scope="session")
def app():
    """세션 전체에서 공유되는 앱 인스턴스"""
    app = create_app(testing=True)
    yield app


@pytest.fixture
def client(app):
    """각 테스트마다 새로운 테스트 클라이언트"""
    return app.test_client()
```

### 3.8 monkeypatch를 활용한 환경 격리

```python
def test_api_url(monkeypatch):
    monkeypatch.setenv("API_URL", "http://test.example.com")
    config = load_config()
    assert config.api_url == "http://test.example.com"
```

> 시간 모킹의 경우 monkeypatch 직접 교체 대신 freezegun/time-machine 전용 라이브러리 사용을 권장한다. (10장 참고)

### 3.9 tmp_path를 활용한 파일 테스트

```python
def test_file_processing(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world")

    output_file = tmp_path / "output.txt"
    process_file(input_file, output_file)

    assert output_file.read_text() == "HELLO WORLD"
```

### 3.10 전체 테스트 실행

```bash
# pytest로 전체 테스트 실행
pytest tests/

# 특정 마커만 실행
pytest -m "not slow"

# 특정 패턴 매칭
pytest -k "test_auth"

# 실패한 테스트만 재실행
pytest --lf
```

---

## 4. pytest 심화 설정

### 4.1 pyproject.toml 종합 설정

pytest-django는 `DJANGO_SETTINGS_MODULE`로 settings를 잡고 DB 라이프사이클을 관리한다. 값은 **프로젝트의 `manage.py`/환경에서 감지한 실제 settings 경로**(흔히 평면 `config.settings`)를 쓴다 — `<project>.settings.test`처럼 settings 분할이 **실제로 존재할 때만** test 모듈을 가리키고, 분할이 없으면 평면 모듈을 그대로 쓴다(`settings.test`를 임의로 하드코딩하지 않는다).

```toml
[tool.pytest.ini_options]
# 최소 pytest 버전 요구
minversion = "8.0"

# pytest-django: settings 모듈 — 값은 프로젝트 manage.py/env에서 감지한 실제 경로.
# 분할이 있으면 그 test 모듈(예: config.settings.test), 없으면 평면 모듈을 쓴다.
DJANGO_SETTINGS_MODULE = "config.settings"

# 테스트 검색 경로 — 앱별 test 루트(application/<app>/test/{unit,integration}/).
# 생략하고 rootdir 자동 수집에 맡겨도 되며, 명시하려면 앱 test 루트를 나열한다.
testpaths = ["application"]

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

# 테스트 파일/클래스/함수 패턴 (pytest 기본 함수형 테스트)
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

# xfail 마크된 테스트가 통과하면 실패 처리
xfail_strict = true

# 로그 설정
log_cli = true
log_cli_level = "INFO"
```

> **Django에서 `filterwarnings = ["error", ...]` 같은 전역 경고-에러는 두지 않는다** — Django·서드파티가 흘리는 Deprecation 경고가 그린 테스트 스위트를 레드바로 만들어 의미 없는 실패를 낳는다. 경고는 pytest 기본값으로 두거나, 잡으려면 **명시적으로 범위가 좁은 `error::...` 한두 줄**(자기 코드가 내는 특정 경고 카테고리·모듈)로만 한정한다.

### 4.2 conftest.py 계층 구조

conftest.py는 디렉토리별로 배치할 수 있으며, pytest가 테스트 수집 시 각 디렉토리의 conftest.py를 자동으로 로드한다. 이 표준의 테스트는 **앱별 의미군 트리**에 산다(트리 단일 출처는 `discipline-houserules` §2 — 의미군 조직은 본 절 §4.2 소유). 루트 `conftest.py` 하나가 settings·공유 픽스처를 이고, 각 앱은 `application/<app>/test/{unit,integration}/`(필요 시 `e2e/`)로 의미군을 나눈다.

```
conftest.py                            # 루트 — DJANGO_SETTINGS_MODULE·공유 fixture·transactional_db
application/
  <app>/
    test/
      unit/
        conftest.py                    # 단위 전용 fixture (mock, stub) — 도메인·응용
        test_models.py
        test_services.py
      integration/
        conftest.py                    # 통합 전용 fixture (실제 DB) — 리포지토리·HTTP 엔드포인트
        test_repository.py
        test_api.py
```

```python
# conftest.py (루트) - 전역 설정
import pytest

def pytest_configure(config):
    """pytest 설정 훅 - 전역 설정을 여기서 수행"""
    config.addinivalue_line("markers", "slow: 느린 테스트")

def pytest_collection_modifyitems(config, items):
    """테스트 수집 후 동적으로 마커 추가/필터링"""
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

# application/<app>/test/unit/conftest.py - 단위 테스트 전용
@pytest.fixture(autouse=True)
def _disable_network(monkeypatch):
    """단위 테스트에서 실수로 네트워크 호출하는 것을 방지"""
    import socket
    def guard(*args, **kwargs):
        raise RuntimeError("단위 테스트에서 네트워크 호출 금지!")
    monkeypatch.setattr(socket, "socket", guard)
```

> **루트 `conftest.py`는 `DJANGO_SETTINGS_MODULE`·픽스처·`transactional_db`만 이고, 연결/트랜잭션 의미(PRAGMA·`BEGIN`·`isolation_level`)를 conftest로 주입하지 않는다** — connection/transaction/lock/isolation을 conftest에서 조작하는 것은 기존 메커니즘-소유권 blocker에 해당한다(`implementation-django` §16.4: 트랜잭션·락·격리 메커니즘은 architect 소유, *출처-불문* 금지 — 테스트 conftest 패치 포함). 필요한 연결 튜닝은 stock `OPTIONS`로만 한다(§20.5 참조).

> 출처: [pytest Configuration Reference](https://docs.pytest.org/en/stable/reference/customize.html), [Good Integration Practices - pytest](https://docs.pytest.org/en/stable/explanation/goodpractices.html)

---

## 5. pytest 마커 시스템

### 5.1 내장 마커: skip, skipif, xfail

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

### 5.2 커스텀 마커와 마커 활용 패턴

```python
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

### 5.3 마커에서 fixture로 데이터 전달

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

## 6. pytest 플러그인 생태계

테스트 스택 동반 패키지(pytest-django, factory_boy, freezegun, responses 등)를 새로 들일 때는 훈련 기억의 버전을 적지 말고 **`discipline-houserules` §6.2 버전-핀 규율**(무핀으로 resolve → *실제 설치 버전*을 매니페스트에 핀)을 따른다 — resolve가 기존 Django/핵심 의존성 핀을 올리려 들면 호환 한계 신호이니 기존 핀 안에서 핀하거나 보고한다(설계 반송). 핀 *표기*·매니페스트 위치는 `implementation-django` §3.1·`implementation-django-ninja` §2.1 소유.

### 6.1 pytest-xdist: 병렬 테스트 실행

```bash
pip install pytest-xdist

# 자동 CPU 감지 (물리 코어 수)
pytest -n auto

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

> 출처: [pytest-xdist Documentation](https://pytest-xdist.readthedocs.io/en/stable/distribution.html)

### 6.2 pytest-asyncio: 비동기 테스트

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
- **strict**: `@pytest_asyncio.fixture`를 명시적으로 데코레이터로 붙여야 함. 여러 비동기 라이브러리를 동시 사용할 때 권장.

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

> 출처: [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/en/latest/concepts.html)

### 6.3 pytest-cov: 커버리지 통합

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

> 출처: [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

### 6.4 pytest-randomly: 테스트 순서 무작위화

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

### 6.5 pytest-timeout: 테스트 시간 제한

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

## 7. Mock과 테스트 더블 실전

기본 mock 도구는 pytest-mock `mocker` 픽스처다(자동 teardown). 패치는 `mocker.patch`/`mocker.patch.object`, 유틸은 `mocker.Mock`/`MagicMock`/`AsyncMock`/`ANY`/`call`/`sentinel`/`PropertyMock`/`seal`/`mock_open`, autospec은 `mocker.patch(..., autospec=True)`. **유일한 예외는 standalone `create_autospec`** — 패치 밖에서 쓸 때만 `from unittest.mock import create_autospec`. raw `unittest.mock`로 패치하지 않는다. (이 절은 mock의 *도구*만 정한다 — *무엇을·얼마나* mock하는지의 교리는 §7.1이 불변으로 소유한다.)

### 7.1 검증 방식 우선순위 [Unit Testing - Khorikov + 파이썬코딩의기술]

Mock 사용 범위에 대한 올바른 접근: 의존성 주입으로 테스트 용이성을 확보하되, **과도한 Mock은 안티패턴**("Mockery")이다. 검증 방식은 다음 우선순위를 따른다.

| 우선순위 | 검증 방식 | 설명 | 예시 |
|----------|-----------|------|------|
| 1 | **출력 기반** | 함수의 반환값을 검증 | `assert calculate(2, 3) == 5` |
| 2 | **상태 기반** | 행위 후 객체 상태를 검증 | `cart.add(item); assert cart.total == 100` |
| 3 | **통신 기반** | 외부 호출 여부를 검증 (Mock) | `mock_email.send.assert_called_once()` |

**원칙**: 외부 의존성(결제 게이트웨이, 이메일 등)만 Mock하고, 핵심 비즈니스 로직은 실제 객체로 테스트한다.

### 7.2 Mock 기본 사용법 [파이썬코딩의기술]

```python
def test_weather_report(mocker):
    # 1. Mock 객체 생성 (spec으로 인터페이스 강제)
    mock_api = mocker.Mock(spec=WeatherAPI)
    mock_api.get_temperature.return_value = 25.0

    result = get_weather_report(mock_api, "서울")

    mock_api.get_temperature.assert_called_once_with("서울")
    assert "25.0" in result

    # 4. ANY를 사용한 유연한 검증
    mock_api.get_temperature.assert_called_with(mocker.ANY, "서울")


# 2. 예외 발생 모킹 (side_effect)
def test_weather_report_timeout(mocker):
    mock_api = mocker.Mock(spec=WeatherAPI)
    mock_api.get_temperature.side_effect = ConnectionError("타임아웃")

    with pytest.raises(ConnectionError):
        get_weather_report(mock_api, "서울")


# 3. mocker.patch로 모듈 레벨 모킹 (데코레이터 대신 본문에서 패치 — 자동 teardown)
def test_fetch_weather(mocker):
    mock_get = mocker.patch("myapp.weather.requests.get")
    mock_get.return_value.json.return_value = {"temp": 25.0}
    result = fetch_weather("서울")
    assert result["temp"] == 25.0
```

### 7.3 의존 관계 캡슐화로 모킹을 쉽게 만들기 [파이썬코딩의기술]

테스트 코드를 처음 보고 이해하기 어렵다면, 더 나은 추상화를 사용하여 목이나 테스트를 더 쉽게 작성할 수 있다.

```python
# 나쁨: 의존 관계가 흩어져 있어 모킹이 복잡하다
def process_order(order_id):
    db = get_database()
    order = db.query(f"SELECT * FROM orders WHERE id={order_id}")
    email_service = get_email_service()
    email_service.send(order.customer_email, "주문 완료")


# 좋음: 의존 관계를 주입받아 모킹이 쉽다
class OrderProcessor:
    def __init__(self, db, email_service):
        self.db = db
        self.email_service = email_service

    def process(self, order_id):
        order = self.db.get_order(order_id)
        self.email_service.send(order.customer_email, "주문 완료")


def test_process_order(mocker):
    mock_db = mocker.Mock()
    mock_db.get_order.return_value = Order(email="test@test.com")
    mock_email = mocker.Mock()

    processor = OrderProcessor(mock_db, mock_email)
    processor.process(1)

    mock_email.send.assert_called_once_with("test@test.com", "주문 완료")
```

> 단, 모든 의존성을 Mock으로 대체하면 "실제로 뭘 테스트하는 건지" 의문이 된다. 외부 의존성(이메일, 결제 등)만 Mock하고, 핵심 로직은 실제로 실행해야 한다. [Codepipes Blog]

### 7.4 PropertyMock: 프로퍼티 모킹

```python
class DatabaseConnection:
    @property
    def is_connected(self):
        return self._check_connection()

    @property
    def latency_ms(self):
        return self._measure_latency()

# 프로퍼티를 모킹
def test_connection_status(mocker):
    mocker.patch.object(
        DatabaseConnection,
        "is_connected",
        new_callable=mocker.PropertyMock,
        return_value=True,
    )
    conn = DatabaseConnection()
    assert conn.is_connected is True

# 프로퍼티가 호출될 때마다 다른 값 반환
def test_latency_fluctuation(mocker):
    mocker.patch.object(
        DatabaseConnection,
        "latency_ms",
        new_callable=mocker.PropertyMock,
        side_effect=[10, 50, 200],  # 순서대로 반환
    )
    conn = DatabaseConnection()
    assert conn.latency_ms == 10
    assert conn.latency_ms == 50
    assert conn.latency_ms == 200
```

### 7.5 AsyncMock: 비동기 함수 모킹

Python 3.8+에서 제공되며, 비동기 함수를 모킹할 때 사용한다.

```python
class AsyncService:
    async def fetch_data(self, url: str) -> dict:
        ...

    async def process(self) -> str:
        data = await self.fetch_data("https://api.example.com/data")
        return data["result"]

# AsyncMock 기본 사용
@pytest.mark.asyncio
async def test_async_service(mocker):
    service = AsyncService()
    service.fetch_data = mocker.AsyncMock(
        return_value={"result": "success"}
    )
    result = await service.process()
    assert result == "success"
    service.fetch_data.assert_awaited_once_with(
        "https://api.example.com/data"
    )

# async 컨텍스트 매니저 모킹
@pytest.mark.asyncio
async def test_async_context_manager(mocker):
    mock_session = mocker.MagicMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = False

    async with mock_session as session:
        assert session is mock_session

# async 이터레이터 모킹
@pytest.mark.asyncio
async def test_async_iterator(mocker):
    mock_stream = mocker.MagicMock()
    mock_stream.__aiter__.return_value = iter([
        {"id": 1}, {"id": 2}, {"id": 3}
    ])

    results = []
    async for item in mock_stream:
        results.append(item)
    assert len(results) == 3
```

### 7.6 seal(): Mock 객체 봉인

`seal()`은 Mock 객체를 봉인하여, 미리 설정하지 않은 속성/메서드에 접근하면 에러를 발생시킨다. 오타나 잘못된 속성 접근을 방지한다.

```python
def test_sealed_mock(mocker):
    user = mocker.MagicMock()
    user.name = "Alice"
    user.email = "alice@example.com"

    mocker.seal(user)

    # 설정된 속성은 정상 접근
    assert user.name == "Alice"

    # 미설정 속성 접근 시 AttributeError 발생
    with pytest.raises(AttributeError):
        _ = user.phone  # seal 되었으므로 에러

def test_sealed_with_spec(mocker):
    """create_autospec + seal = 가장 안전한 mock"""
    # 패치 없이 클래스를 직접 오토스펙할 때만 standalone create_autospec을 쓴다(유일한 예외).
    from unittest.mock import create_autospec

    class UserService:
        def get_user(self, user_id: int) -> dict: ...
        def delete_user(self, user_id: int) -> bool: ...

    mock_service = create_autospec(UserService)
    mock_service.get_user.return_value = {"id": 1, "name": "Alice"}
    mocker.seal(mock_service)

    # 스펙에 있는 메서드는 정상 호출
    assert mock_service.get_user(1) == {"id": 1, "name": "Alice"}

    # 스펙에 없는 메서드 호출 시 에러
    with pytest.raises(AttributeError):
        mock_service.update_user(1, name="Bob")
```

### 7.7 side_effect 고급 활용

```python
# 호출 인자에 따라 다른 값 반환
def test_dynamic_side_effect(mocker):
    def route_response(url):
        responses = {
            "/users": [{"id": 1}],
            "/products": [{"id": 100}],
        }
        if url in responses:
            return responses[url]
        raise ValueError(f"Unknown URL: {url}")

    mock_api = mocker.MagicMock(side_effect=route_response)

    assert mock_api("/users") == [{"id": 1}]
    assert mock_api("/products") == [{"id": 100}]

    with pytest.raises(ValueError):
        mock_api("/unknown")

# 순차적 결과 + 예외 혼합
def test_retry_logic(mocker):
    mock_call = mocker.MagicMock(side_effect=[
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

### 7.8 호출 순서 검증

여러 호출의 **순서**가 중요하면 `assert_has_calls` 또는 `mock_calls`로 순서를 검증한다. (개별 호출 여부만 보는 `assert_called_once_with`로는 순서를 보장하지 못한다.)

```python
def test_lifecycle_order(mocker):
    mock = mocker.Mock()
    run_lifecycle(mock)  # setup -> run -> teardown 순으로 호출되어야 한다

    # 지정한 호출들이 이 순서대로 일어났는지 검증
    mock.assert_has_calls([
        mocker.call.setup(),
        mocker.call.run("test_method"),
        mocker.call.teardown(),
    ])

    # 전체 호출 시퀀스를 정확히 비교하려면 mock_calls를 직접 확인한다
    assert mock.mock_calls == [
        mocker.call.setup(),
        mocker.call.run("test_method"),
        mocker.call.teardown(),
    ]
```

---

## 8. Property-Based Testing (Hypothesis)

전통적 테스트는 특정 입력값을 직접 선택하지만, Property-Based Testing은 **코드가 만족해야 할 속성(property)**을 정의하고, 프레임워크가 자동으로 수백 가지 입력을 생성하여 검증한다.

### 8.1 기본 사용법

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

### 8.2 전략(Strategies) 조합

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
    st.none() | st.booleans() | st.integers() | st.text(max_size=10),
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

### 8.3 @example: 경계값 명시

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

### 8.4 settings로 실행 제어

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

### 8.5 Stateful Testing: 시퀀스 기반 테스트

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

## 9. 테스트 데이터 팩토리 (factory_boy + Faker)

### 9.1 기본 개념

factory_boy는 테스트 객체 생성을 위한 "청사진" 역할을 한다. JSON fixture 파일 대신 Python 코드로 테스트 데이터를 선언적으로 정의한다.

```bash
pip install factory_boy faker
```

factory_boy는 **ORM 애그리거트/엔티티 영속 픽스처의 기본**이다 — 모든 객체에 강제하지 않는다. *정확한 필드 값*이 검증의 핵심인 행(동시성·경계 테스트; 예: §20.5의 CAS-충돌 스파이는 `ProductModel.objects.create(stock=5, version=0)`으로 일부러 정확한 행을 만든다)과 VO/dataclass 구성은 직접 생성이 더 명확하므로 그대로 둔다. 팩토리는 **`application/<app>/test/factories/`**(패키지)에 둔다 — 이 폴더는 테스트 트리 단일 출처(`discipline-houserules` §2)에 별도로 추가되므로 여기서는 위치만 가리킨다.

### 9.2 기본 팩토리 정의

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

### 9.3 관계 처리: SubFactory, RelatedFactory

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

### 9.4 Trait: 변형 객체 생성

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

### 9.5 배치 생성과 재현성

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

### 9.6 SQLAlchemy / Django ORM 통합

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

## 10. 시간 모킹 (freezegun / time-machine)

시간 모킹에는 전용 라이브러리를 사용한다. monkeypatch로 datetime을 직접 교체하는 방식은 패치 대상 모듈 경로를 정확히 지정해야 하고, 여러 모듈에서 datetime을 import하면 누락이 발생하므로 비권장한다.

### 10.1 freezegun

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

### 10.2 time-machine

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

### 10.3 비교 및 선택 기준

| 항목 | freezegun | time-machine |
|------|-----------|--------------|
| 성능 | 느림 (순수 Python) | 100~200배 빠름 (C 확장) |
| CPython 외 지원 | 모든 Python 구현체 | CPython만 |
| 선택적 패치 | 가능 | 불가 (전체 패치) |
| 성숙도 | 오래된 커뮤니티, 안정적 | 비교적 최신, Adam Johnson 개발 |
| 추천 환경 | PyPy 사용, 선택적 패치 필요 | 일반 CPython 프로젝트 |

> 출처: [freezegun PyPI](https://pypi.org/project/freezegun/), [time-machine PyPI](https://pypi.org/project/time-machine/), [Time-machine vs Freezegun - Better Stack](https://betterstack.com/community/guides/testing/time-machine-vs-freezegun/), [Introducing time-machine - Adam Johnson](https://adamj.eu/tech/2020/06/03/introducing-time-machine/)

---

## 11. HTTP 모킹 (responses / aioresponses)

### 11.1 responses: requests 라이브러리 모킹

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

    resp1 = requests.get("https://api.example.com/users")
    assert resp1.json()["page"] == 1

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

### 11.2 aioresponses: aiohttp 모킹

```bash
pip install aioresponses
```

```python
from aioresponses import aioresponses
import aiohttp

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

### 11.3 HTTPretty: 소켓 레벨 인터셉트

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

    resp1 = requests.get("https://api.example.com/data")
    assert resp1.json()["key"] == "value"

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

## 12. Docker 기반 통합 테스트 (testcontainers)

testcontainers-python은 실제 Docker 컨테이너를 사용하여 통합 테스트를 수행한다. mock이나 인메모리 대체물이 아닌 **실제 서비스**로 테스트한다.

### 12.1 PostgreSQL 통합 테스트

```bash
pip install testcontainers[postgres]
```

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
    """각 테스트를 트랜잭션으로 감싸서 격리 (SQLAlchemy 2.0 스타일)"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(connection)

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

### 12.2 Redis 통합 테스트

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

### 12.3 여러 서비스 동시 사용

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

    user_service = UserService(db=db, cache=cache)
    user = user_service.create("Alice")
    assert user_service.get_cached(user.id) is not None
```

> 출처: [testcontainers-python 공식 문서](https://testcontainers-python.readthedocs.io/), [Testcontainers Getting Started](https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/)

---

## 13. 커버리지 설정 (coverage.py)

### 13.1 pyproject.toml 종합 설정

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
directory = "htmlcov"
title = "My Project Coverage"

[tool.coverage.xml]
output = "coverage.xml"
```

### 13.2 활용 명령어

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

## 14. 멀티환경 테스트 (tox / nox)

여러 Python 버전과 의존성 조합에서 테스트를 자동 실행하는 도구이다. 라이브러리 개발 시 필수적이다.

### 14.1 tox: 선언적 설정

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

```bash
# 모든 환경 실행
tox

# 특정 환경만
tox -e py312

# 병렬 실행
tox -p auto
```

### 14.2 nox: Python 코드 기반 설정

tox보다 유연하며, 설정 파일이 일반 Python 코드이므로 복잡한 로직을 작성할 수 있다.

```python
# noxfile.py
import nox

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
```

```bash
# 기본 세션 실행
nox

# 특정 세션
nox -s tests

# 가상환경 재사용 (개발 시 빠른 반복)
nox -R

# 사용 가능한 세션 목록
nox -l
```

### 14.3 tox vs nox 비교

| 항목 | tox | nox |
|------|-----|-----|
| 설정 형식 | INI/TOML (선언적) | Python 코드 (프로그래밍 가능) |
| 학습 곡선 | 낮음 | 약간 높음 |
| 유연성 | 중간 | 높음 (조건문, 반복문 사용 가능) |
| 커뮤니티 | 더 오래됨, 넓은 사용자 기반 | 성장 중, Google 프로젝트에서 사용 |
| 추천 | 단순한 멀티버전 테스트 | 복잡한 빌드/테스트 워크플로 |

> 출처: [tox Documentation](https://tox.wiki/en/latest/user_guide.html), [Nox Documentation](https://nox.thea.codes/)

---

## 15. 테스트 코드 품질 원칙

### 15.1 FIRST 원칙 [Clean Code - Robert C. Martin]

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
테스트는 적절한 시점에 작성한다. 다만 **언제·어떤 순서로** 테스트를 작성하는지(test-first, Red-Green 리듬 등 작성 시점의 실천)는 작성법이 아니라 방법론이므로 `workspace/reference/discipline-tdd/reference/final.md`가 다룬다.

> 출처: Robert C. Martin, "Clean Code" (2008), [FIRST Principles - DZone](https://dzone.com/articles/first-principles-solid-rules-for-tests)

### 15.2 AAA 패턴 (Arrange-Act-Assert)

Bill Wake가 처음 명명한 테스트 구조화 패턴이다. AAA 패턴을 기본으로 하되, **논리적으로 하나의 행위를 검증하는 관련 assert는 허용**한다.

```python
def test_user_discount_calculation():
    # ---- Arrange (준비) ----
    user = UserFactory(membership="gold", joined_years_ago=3)
    product = ProductFactory(price=100.00, category="electronics")
    discount_service = DiscountService()

    # ---- Act (실행) ----
    # 테스트하려는 동작을 정확히 하나만 실행
    discount = discount_service.calculate(user, product)

    # ---- Assert (검증) ----
    # 동일한 Act에 대한 관련 assert는 허용
    assert discount.percentage == 15.0
    assert discount.final_price == 85.00
    assert discount.reason == "골드 회원 3년차 할인"
```

**AAA 핵심 규칙**:

1. **Act 섹션은 가능한 한 줄**: 테스트 대상 동작을 명확히 하기 위해 Act은 단일 함수 호출이어야 한다.
2. **여러 AAA 블록은 별도 테스트로 분리**: 하나의 테스트에 여러 Act-Assert 쌍이 있으면 분리해야 한다.
3. **동일한 Act에 대한 관련 assert는 허용**: 논리적으로 하나의 행위를 검증하는 여러 assert는 같은 테스트에 둘 수 있다.

```python
# 나쁜 예: 여러 AAA 블록 (별도 테스트로 분리해야 함)
def test_user_lifecycle():
    user = create_user("Alice")
    assert user.is_active        # AAA 블록 1

    deactivate(user)
    assert not user.is_active    # AAA 블록 2

    reactivate(user)
    assert user.is_active        # AAA 블록 3

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

> 출처: [AAA Pattern - Semaphore](https://semaphore.io/blog/aaa-pattern-test-automation), [Manning: Making Better Unit Tests](https://freecontent.manning.com/making-better-unit-tests-part-1-the-aaa-pattern/), Clean Code (Robert C. Martin)

### 15.3 화이트박스 테스트를 피하라 [테스트주도 개발 + Codepipes Blog]

구현 세부사항에 결합하지 않는 테스트를 작성해야 한다. 이 문제는 **설계 관점**과 **테스트 기법 관점** 양쪽에서 접근해야 한다.

**설계 관점** [테스트주도 개발 - Kent Beck]: 화이트박스 테스트를 바라는 것은 테스팅 문제가 아니라 설계 문제다. 내부 구현을 들여다봐야 한다면, 그것은 인터페이스 설계가 잘못된 것이므로 프로덕션 코드의 설계를 개선해야 한다. public 프로토콜만을 이용해서 테스트를 작성해야 한다.

**테스트 기법 관점** [Codepipes Blog]: 내부 구현에 결합된 테스트("The Inspector" 안티패턴)는 리팩토링할 때마다 깨진다. 테스트 작성 시 **입력과 출력만 검증**하는 습관을 들여야 한다.

```python
# 나쁜 예: 내부 구현에 결합 (정렬 알고리즘이 quicksort인지 검증)
def test_sort_uses_quicksort(mocker):
    spy = mocker.spy(sort_module, "_partition")
    sort_module.sort([3, 1, 2])
    spy.assert_called()  # 정렬 알고리즘 변경하면 깨짐

# 좋은 예: 동작만 검증 (결과가 정렬되어 있는지 확인)
def test_sort_returns_sorted_list():
    assert sort_module.sort([3, 1, 2]) == [1, 2, 3]
```

---

## 16. 테스트 안티패턴

### 16.1 코드 수준 안티패턴

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

**기타 안티패턴**:
- **Generous Leftovers (관대한 잔여물)**: 한 테스트가 남긴 데이터를 다른 테스트가 사용
- **Local Hero (로컬 영웅)**: 특정 개발 환경에서만 통과하는 테스트
- **Secret Catcher (비밀 포획자)**: assert 없이 예외가 발생하지 않는 것만으로 "통과"
- **Dodger (회피자)**: 쉬운 테스트만 작성하고 핵심 비즈니스 로직은 테스트하지 않음
- **Cuckoo (뻐꾸기)**: 관련 없는 테스트 클래스/파일에 들어있는 테스트
- **The Nitpicker (트집잡이)**: 의미 없는 세부사항까지 검증하는 테스트

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

### 16.2 전략 수준 안티패턴 [Codepipes Blog]

1. **단위 테스트만 있고 통합 테스트 없음** (또는 그 반대)
2. **잘못된 테스트 유형 선택**: 단위 테스트로 충분한데 E2E로 작성
3. **테스트를 개발 프로세스의 별도 단계로 취급**: 코딩 후 나중에 한꺼번에 테스트 작성
4. **테스트 코드를 프로덕션 코드보다 낮은 품질로 작성**
5. **비결정적(flaky) 테스트를 방치**
6. **느린 테스트를 개선하지 않음**
7. **테스트를 수동으로 실행** (CI/CD 미연동)
8. **코드 커버리지에만 집착**: 커버리지 100%가 버그 0%를 의미하지 않음

> 출처: [Software Testing Anti-patterns - Codepipes Blog](https://blog.codepipes.com/testing/software-testing-antipatterns.html), [Unit Testing Anti-Patterns Full List - DZone](https://dzone.com/articles/unit-testing-anti-patterns-full-list)

---

## 17. Mutation Testing [mutmut]

### 17.1 개념: 테스트의 테스트

뮤테이션 테스트는 소스 코드에 의도적으로 **작은 변형(mutant)** 을 가하고, 테스트 스위트가 이를 **감지(kill)** 하는지 확인한다. 감지하지 못한 변형은 테스트에 구멍이 있음을 의미한다.

```
원본 코드:  if x > 0:
변형 1:     if x >= 0:    # 비교 연산자 변경
변형 2:     if x < 0:     # 비교 연산자 반전
변형 3:     if True:       # 조건 상수화
```

### 17.2 뮤테이션 종류

| 뮤테이션 유형 | 원본 | 변형 |
|-------------|------|------|
| 산술 연산자 | `a + b` | `a - b` |
| 비교 연산자 | `x > 0` | `x >= 0` |
| 논리 연산자 | `a and b` | `a or b` |
| 상수 변형 | `return 0` | `return 1` |
| 부정 제거 | `not x` | `x` |
| 문장 삭제 | `x += 1` | `(삭제)` |

### 17.3 mutmut 사용법

```bash
# 설치
pip install mutmut

# 실행: 소스 코드에 뮤턴트를 생성하고 테스트 실행
mutmut run --paths-to-mutate "src/" --tests-dir "tests/"

# 결과 확인
mutmut results

# 개별 뮤턴트 상세 확인
mutmut show 42
```

### 17.4 결과 해석

```
뮤테이션 점수(Mutation Score) = 죽인 뮤턴트 / 전체 뮤턴트 x 100

- Killed (죽음): 테스트가 변형을 감지함 -> 좋음
- Survived (생존): 테스트가 변형을 감지 못함 -> 테스트 보강 필요
- Timeout: 뮤턴트가 무한루프 유발 -> 보통 죽인 것으로 간주
- Suspicious: 비정상 종료 -> 수동 확인 필요
```

```python
# === 뮤테이션 테스트에 취약한 코드 ===
def calculate_discount(price: float, quantity: int) -> float:
    if quantity > 10:
        return price * 0.9  # 10% 할인
    return price


def test_discount_weak():
    """이 테스트는 mutmut에서 생존하는 뮤턴트를 남긴다."""
    assert calculate_discount(1000, 15) == 900  # quantity > 10 만 테스트
    # mutmut이 > 를 >= 로 바꾸면? quantity=10 케이스가 없어서 감지 못함!


# === 뮤테이션 테스트에 강한 코드 ===
def test_discount_strong():
    """경계값을 포함하여 뮤턴트를 죽인다."""
    assert calculate_discount(1000, 15) == 900   # > 10: 할인 적용
    assert calculate_discount(1000, 10) == 1000  # == 10: 할인 미적용 (경계)
    assert calculate_discount(1000, 11) == 900   # == 11: 할인 적용 (경계+1)
    assert calculate_discount(1000, 5) == 1000   # < 10: 할인 미적용
```

### 17.5 뮤테이션 점수 목표

80% 이상의 뮤테이션 점수가 테스트 스위트의 강력한 결함 감지 능력을 나타낸다. 100%를 목표로 하기보다는 **생존한 뮤턴트를 분석**하여 의미 있는 테스트를 추가하는 것이 중요하다.

---

## 18. BDD pytest-bdd 구현

### 18.1 Given-When-Then [Daniel Terhorst-North & Chris Matts]

```gherkin
# features/order.feature
Feature: 주문 처리
    사용자가 상품을 주문하고 결제할 수 있다.

    Scenario: 재고가 있는 상품 주문
        Given 상품 "노트북"의 재고가 5개 있다
        And 사용자의 장바구니에 "노트북" 1개가 담겨있다
        When 사용자가 주문을 확정한다
        Then 주문이 성공적으로 생성된다
        And 재고가 4개로 감소한다

    Scenario: 재고 부족 시 주문 실패
        Given 상품 "태블릿"의 재고가 0개 있다
        And 사용자의 장바구니에 "태블릿" 1개가 담겨있다
        When 사용자가 주문을 확정한다
        Then "재고 부족" 오류가 발생한다
```

### 18.2 pytest-bdd로 구현

```python
# tests/test_order.py
import pytest
from pytest_bdd import scenario, given, when, then, parsers


@scenario("../features/order.feature", "재고가 있는 상품 주문")
def test_order_with_stock():
    pass


@scenario("../features/order.feature", "재고 부족 시 주문 실패")
def test_order_without_stock():
    pass


# --- Given 단계: 초기 상태 설정 ---
@given(
    parsers.parse('상품 "{product}"의 재고가 {count:d}개 있다'),
    target_fixture="inventory",
)
def inventory_with_stock(product, count):
    inventory = Inventory()
    inventory.set_stock(product, count)
    return inventory


@given(
    parsers.parse('사용자의 장바구니에 "{product}" {count:d}개가 담겨있다'),
    target_fixture="cart",
)
def cart_with_item(product, count):
    cart = ShoppingCart()
    cart.add(product, count)
    return cart


# --- When 단계: 행위 실행 ---
@when("사용자가 주문을 확정한다", target_fixture="order_result")
def place_order(inventory, cart):
    service = OrderService(inventory)
    try:
        order = service.place_order(cart)
        return {"success": True, "order": order}
    except InsufficientStockError as e:
        return {"success": False, "error": str(e)}


# --- Then 단계: 결과 검증 ---
@then("주문이 성공적으로 생성된다")
def order_created(order_result):
    assert order_result["success"] is True


@then(parsers.parse("재고가 {count:d}개로 감소한다"))
def stock_decreased(inventory, count):
    assert inventory.get_stock("노트북") == count


@then(parsers.parse('"{message}" 오류가 발생한다'))
def error_occurred(order_result, message):
    assert order_result["success"] is False
    assert message in order_result["error"]
```

---

## 19. Django Ninja TestClient API 계약 테스트

Django Ninja API는 Django 표준 test client로도 테스트할 수 있지만, router/API 단위 계약을 빠르게 확인할 때는 `ninja.testing.TestClient`를 사용한다. 이 client는 middleware와 URL resolver 계층을 통과하지 않고 API surface를 직접 호출하므로, endpoint의 요청/응답 계약을 좁게 검증하기 좋다.

### 19.1 Router 단위 응답 계약

```python
from ninja.testing import TestClient

from orders.api import router


client = TestClient(router)


def test_order_detail_contract(order_factory):
    order = order_factory(status="paid", total_amount="120.00")

    response = client.get(f"/orders/{order.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": order.id,
        "status": "paid",
        "total_amount": "120.00",
    }
```

검증 대상은 public API contract다. 내부 service 호출 여부, private helper, ORM query 문자열처럼 구현 세부사항은 직접 검증하지 않는다.

### 19.2 요청 검증과 오류 응답

```python
def test_create_order_validation_problem():
    response = client.post(
        "/orders",
        json={"items": []},
    )

    assert response.status_code in {400, 422}
    body = response.json()
    assert "type" in body or "detail" in body
    assert "items" in str(body)
```

프로젝트가 RFC 9457 Problem Details를 표준 오류 형식으로 채택했다면 `type`, `title`, `status`, `detail`, `instance`, field error 확장 키를 계약으로 고정한다. 아직 오류 계약이 정해지지 않았다면 `architecture-api`에서 먼저 결정한 뒤 테스트에 반영한다.

### 19.3 인증, 페이지네이션, 필터링

```python
def test_order_list_requires_auth():
    response = client.get("/orders")

    assert response.status_code in {401, 403}


def test_order_list_pagination_contract(auth_headers, order_factory):
    order_factory.create_batch(3)

    response = client.get(
        "/orders",
        headers=auth_headers,
        query={"limit": 2, "offset": 0},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) >= {"items", "count"}
    assert len(body["items"]) == 2
```

인증 우회, user fixture, header 이름은 프로젝트의 auth contract에 맞춘다. 권한/페이지네이션/필터링 계약이 불명확하면 API 설계를 먼저 확정한다.

### 19.4 pytest-django DB 접근 선택

Django ORM을 사용하는 API 테스트는 pytest-django의 DB access 규칙을 따른다. 기본적으로 DB 접근은 차단되며, DB가 필요한 테스트는 `pytest.mark.django_db`, `db`, `transactional_db` 중 하나로 의도를 명시한다.

```python
import pytest
from ninja.testing import TestClient

from orders.api import router


client = TestClient(router)


@pytest.mark.django_db
def test_order_detail_reads_database(order_factory):
    order = order_factory()

    response = client.get(f"/orders/{order.id}")

    assert response.status_code == 200
```

일반 ORM read/write 검증은 `pytest.mark.django_db`로 충분하다. commit/rollback 효과, `transaction.on_commit`, row lock, 별도 connection 관찰처럼 실제 transaction 경계가 테스트 대상이면 `pytest.mark.django_db(transaction=True)` 또는 `transactional_db` fixture를 사용한다.

> 출처: [Django Ninja Testing](https://django-ninja.dev/guides/testing/), [pytest-django Database access](https://pytest-django.readthedocs.io/en/latest/database.html), [pytest-django helpers](https://pytest-django.readthedocs.io/en/latest/helpers.html)

---

## 20. Idempotency와 동시성 테스트

중복 요청, 재시도, race condition, row lock은 일반 unit test만으로 충분히 보호되지 않는 경우가 많다. 도메인 규칙은 빠른 unit test로 먼저 고정하고, DB unique constraint, transaction, lock, idempotency storage가 관여하는 부분은 integration/API contract test로 검증한다.

### 20.1 Idempotency replay 계약

Idempotency-Key를 지원하는 write API는 같은 key와 같은 payload의 재전송이 같은 결과를 반환하거나 기존 처리 결과를 재사용해야 한다. 서로 다른 payload가 같은 key를 재사용하면 충돌로 실패해야 한다.

```python
import pytest
from ninja.testing import TestClient

from orders.api import router


client = TestClient(router)


@pytest.mark.django_db
def test_create_order_idempotency_replays_same_result(auth_headers):
    headers = {**auth_headers, "Idempotency-Key": "order-create-001"}
    payload = {"sku": "BOOK-1", "quantity": 1}

    first = client.post("/orders", json=payload, headers=headers)
    second = client.post("/orders", json=payload, headers=headers)

    assert first.status_code == 201
    assert second.status_code in {200, 201}
    assert second.json()["id"] == first.json()["id"]
    assert Order.objects.count() == 1
```

```python
@pytest.mark.django_db
def test_create_order_idempotency_rejects_payload_mismatch(auth_headers):
    headers = {**auth_headers, "Idempotency-Key": "order-create-002"}

    first = client.post(
        "/orders",
        json={"sku": "BOOK-1", "quantity": 1},
        headers=headers,
    )
    second = client.post(
        "/orders",
        json={"sku": "BOOK-1", "quantity": 2},
        headers=headers,
    )

    assert first.status_code == 201
    assert second.status_code in {400, 409, 422}
    assert Order.objects.count() == 1
```

정확한 status code와 response body는 `architecture-api`에서 정한 idempotency contract를 따른다. 저장소 스키마, uniqueness, transaction boundary가 불명확하면 `architecture-db`를 먼저 사용한다.

### 20.2 중복 생성 방지와 DB 제약

```python
import pytest
from django.db import IntegrityError


@pytest.mark.django_db
def test_idempotency_key_is_unique_per_actor(idempotency_record_factory, user):
    idempotency_record_factory(user=user, key="same-key")

    with pytest.raises(IntegrityError):
        idempotency_record_factory(user=user, key="same-key")
```

서비스 계층 test가 "중복이면 기존 결과 반환"을 검증하더라도, DB unique constraint test는 데이터 불변식을 별도로 보호한다. DB 제약이 동작의 일부라면 mock repository만으로 끝내지 않는다.

### 20.3 Transaction과 row lock 테스트

Django `TestCase` 계열은 각 테스트를 transaction으로 감싸므로 `select_for_update()`의 transaction 요구를 정확히 드러내지 못할 수 있다. row lock, commit/rollback, 별도 connection 관찰을 테스트할 때는 `TransactionTestCase` 또는 pytest-django의 `transaction=True`를 사용한다. **이 `TransactionTestCase → @pytest.mark.django_db(transaction=True)/transactional_db` 매핑은 실제 transaction 경계·스레드 race 테스트(§20.3·§20.4)에만 적용한다** — 단일 connection·단일 스레드로 충분한 결정적 테스트(§20.5 CAS-충돌 스파이)에까지 `transaction=True`를 다는 것은 연결 의미를 바꾸는 과(過)번역이다(거기선 plain `@pytest.mark.django_db`).

```python
import pytest
from django.db import transaction


@pytest.mark.django_db(transaction=True)
def test_inventory_reservation_uses_transactional_lock(product_factory):
    product = product_factory(stock=1)

    with transaction.atomic():
        locked = (
            Product.objects
            .select_for_update()
            .get(id=product.id)
        )
        locked.stock -= 1
        locked.save(update_fields=["stock"])

    product.refresh_from_db()
    assert product.stock == 0
```

이 예시는 transaction-capable test 선택을 보여주는 최소 형태다. 실제 동시성 보장은 두 connection, thread/process, lock timeout, `nowait=True`/`skip_locked=True`, 또는 DB별 격리 수준까지 포함해 검증해야 할 수 있다.

### 20.4 Race condition 재현 테스트

```python
from concurrent.futures import ThreadPoolExecutor

import pytest


@pytest.mark.django_db(transaction=True)
def test_only_one_concurrent_reservation_succeeds(product_factory):
    product = product_factory(stock=1)

    def reserve_once():
        return reserve_product(product.id, quantity=1)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: reserve_once(), range(2)))

    assert sorted(result.success for result in results) == [False, True]
    product.refresh_from_db()
    assert product.stock == 0
```

동시성 테스트는 DB backend와 connection 관리에 민감하다. SQLite처럼 row-lock 의미가 다른 backend에서는 이 검증이 충분하지 않을 수 있으므로 PostgreSQL 등 운영 DB와 같은 backend를 testcontainers로 띄우는 것을 고려한다. flaky test가 되면 skip으로 숨기기 전에 lock timeout, barrier, transaction boundary, cleanup fixture, random seed, DB isolation을 먼저 분석한다.

> 출처: [Django testing tools](https://docs.djangoproject.com/en/dev/topics/testing/tools/), [Django QuerySet select_for_update](https://docs.djangoproject.com/en/4.0/ref/models/querysets/#select-for-update), [pytest-django Database access](https://pytest-django.readthedocs.io/en/latest/database.html)

### 20.5 결정적 CAS-충돌 재시도 테스트 (스파이)

§20.4의 스레드 race 테스트는 가드가 실제 경합에서 무너지지 않는지 *관찰*하기 위한 것이지만, SQLite에서 비결정적이고 flaky하기 쉽다. 낙관적 동시성 가드(`version` CAS + 재시도 루프, `architecture-db` §9.5)의 **정확성은 결정론적으로 먼저 증명**한다 — 실제 스레드 없이, *다른 트랜잭션이 먼저 `version`을 올린 상황*을 흉내 내 CAS 0행을 1회 강제하고, 응용 서비스가 재조회→도메인 메서드 재실행으로 일관되게 수렴하는지 검증한다.

스파이는 실제 리포지토리를 상속해 version-guarded save만 가로채고, 첫 저장 직전 DB의 `version`을 한 번 올린다(다른 트랜잭션이 먼저 커밋한 상황의 시뮬레이션). 이후 시도는 개입하지 않으므로 정상 저장된다.

```python
class ConflictOnceRepository(DjangoProductRepository):
    """첫 CAS 저장 직전에 version을 한 번 올려 CAS 0행을 결정론적으로 유발하는 스파이."""

    def __init__(self) -> None:
        self.save_attempts = 0

    def save_with_version_guard(self, product, expected_version: int) -> bool:
        self.save_attempts += 1
        if self.save_attempts == 1:
            # 첫 시도 직전 외부 갱신 — 캡처한 version을 무효화(다른 트랜잭션 흉내).
            ProductModel.objects.filter(pk=product.id).update(version=expected_version + 1)
        return super().save_with_version_guard(product, expected_version)


@pytest.mark.django_db
def test_cas_conflict_once_then_retry_converges():
    product = ProductModel.objects.create(stock=5, version=0)
    app = ReserveStockApp(ConflictOnceRepository())

    result = app.execute(ReserveStockCommand(product_id=product.id, quantity=2))

    product.refresh_from_db()
    assert product.stock == 3  # 첫 CAS 0행 → 재시도 성공, 정확히 한 번만 차감
```

이 테스트는 단일 connection·단일 스레드이므로 `transaction=True`가 필요 없다 — 스파이의 `.update()`와 응용 서비스의 재조회가 같은 connection에서 일어나 갱신된 `version`을 그대로 본다. 실제 별도 connection·스레드 경합 관찰은 §20.4의 영역이다.

이 테스트는 빠르고 결정적이어서 동시성 가드 회귀를 막는 1차 방어다. 단, 스파이가 구체 리포지토리의 `save_with_version_guard` 시그니처에 결합하므로 그 메서드명·시그니처가 바뀌면 함께 갱신한다(가드의 *내부 CAS 구현* 변경에는 영향받지 않는다). 스레드 기반 §20.4는 통합 신뢰를 위한 보조이며, 운영과 같은 backend(PostgreSQL 등)를 testcontainers로 띄워 돌리는 편이 SQLite보다 안정적이다.

**연결 의미를 바꿔 테스트를 성립시키지 않는다.** SQLite에서 race를 *관찰*하려고 `BEGIN IMMEDIATE`·격리 수준·begin 모드가 필요해 보여도, 그것을 **커스텀 `DatabaseWrapper`/DB 백엔드로 구현하지 않는다** — 트랜잭션·락·격리 *메커니즘*은 architect가 소유하며(`architecture-db` §9.5 연결 설정 경계), 코더가 환경 한계를 이유로 임의 대체하는 것은 *출처-불문* 금지다(`implementation-django` §16.4). 필요한 연결 튜닝은 **stock `OPTIONS`만**으로 한다(IMMEDIATE는 `transaction_mode`[Django 5.1+], busy 대기는 `timeout`, 안전 PRAGMA 화이트리스트). 위 결정적 CAS-충돌 스파이는 애초에 이런 연결 조작이 필요 없다 — 그래서 §16.4 위반 압력 없이 동시성 기준을 검증한다.

---

## 21. 테스트 디버깅 기법

범용 Python 디버깅(repr, pdb, breakpoint)은 `workspace/reference/implementation-python/reference/final.md`를 참조한다.

### 21.1 pytest에서 디버거 진입

```bash
# 테스트 실패 시 자동으로 pdb 진입
pytest --pdb

# 마지막 실패 테스트만 재실행하며 pdb 진입
pytest --lf --pdb

# 첫 번째 실패에서 즉시 중단 + pdb
pytest -x --pdb

# 특정 테스트만 디버깅
pytest --pdb -k "test_specific_case"
```

---

## 22. 참고 문헌

| 출처 | 다룬 내용 |
|------|---------|
| 테스트주도 개발 (Kent Beck) | xUnit 패턴, 픽스처, 단언, 예외 테스트, 화이트박스 테스트 설계 관점 |
| 파이썬코딩의기술 (Brett Slatkin) | TestCase, setUp/tearDown, Mock, 의존 관계 캡슐화, repr, pdb |
| Unit Testing (Vladimir Khorikov) | 테스트 더블 5분류, 검증 방식 우선순위, 좋은 단위 테스트의 4대 기둥 |
| Clean Code (Robert C. Martin) | FIRST 원칙, AAA 패턴 |
| Python Testing with pytest (Brian Okken) | pytest 심화, 플러그인 개발, conftest 계층 |
| Architecture Patterns with Python (Percival, Gregory) | Repository 패턴, Fake, 테스트 계층 설계 |
| Martin Fowler / Ham Vocke | 테스트 피라미드, Practical Test Pyramid |
| Google Testing Blog | SMURF 프레임워크, 테스트 크기 분류 |
| Codepipes Blog | 테스트 안티패턴, 전략 수준 안티패턴 |
| Django Ninja 공식 문서 | `TestClient`, API/router 단위 테스트 |
| pytest-django 공식 문서 | `django_db`, `db`, `transactional_db`, transaction test 선택 |
| Django 공식 문서 | `TransactionTestCase`, `TestCase`, `select_for_update` 테스트 주의 |

---

## 부록: 도구 설치 한눈에 보기

```bash
# 핵심 테스트 프레임워크
pip install pytest

# pytest 플러그인
pip install pytest-cov pytest-xdist pytest-asyncio pytest-timeout pytest-randomly pytest-mock pytest-bdd pytest-django

# Property-Based Testing
pip install hypothesis

# Mutation Testing
pip install mutmut

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
