# Python 테스트 코드 작성 종합 가이드
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->


> 이 문서는 `discipline-tdd` §5.5가 영구 테스트 입장 결정을 끝낸 **뒤** 사용하는 테스트 코드 작성 mechanics다. `add`·`update`와 명시 승인된 `retain` 의미 보존 재조직에만 이 문서의 recipe를 적용한다. `retain` 재조직은 새 case·assertion·Red를 만들지 않고 전후 같은 보호를 유지한다. candidate나 `reuse`·`reject`를 새 test file·case·assertion·helper 의무로 바꾸지 않으며, 무엇을 테스트하고 유지·갱신·분리·삭제할지는 `discipline-tdd`가 소유한다.

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
19. [Django Ninja API 계약 테스트](#19-django-ninja-api-계약-테스트)
20. [Idempotency와 동시성 테스트](#20-idempotency와-동시성-테스트)
21. [테스트 디버깅 기법](#21-테스트-디버깅-기법)
22. [참고 문헌](#22-참고-문헌)

---

## 1. 테스트 전략과 피라미드

### 1.1 Martin Fowler의 테스트 피라미드
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

Mike Cohn이 "Succeeding with Agile"에서 처음 제안하고, Martin Fowler가 확장한 개념이다.

```
        /  E2E  \          <- 적게, 느리지만 높은 신뢰도
       /----------\
      / Integration \      <- 중간 수준
     /----------------\
    /    Unit Tests     \  <- 많이, 빠르고 저렴
   /--------------------\
```

**역사적으로 소개된 분포 예시**:
- 단위 테스트: ~80%
- 통합 테스트: ~15%
- E2E 테스트: ~5%

80/15/5는 기존 피라미드를 설명할 때 자주 인용된 예시일 뿐 프로젝트 목표·quota·완료 조건이 아니다. 피라미드의 모양, coverage 수치, 실행 속도만으로 새 테스트를 `add`하지 않는다. 입장된 계약과 독자 failure에 맞는 경계를 선택하며, 유효한 domain/application/DB/adapter/public contract 테스트를 비율 때문에 복제하거나 제거하지 않는다.

**계층별 특성**:

| 구분 | 단위 | 통합 | E2E |
|------|------|------|-----|
| 속도 | 밀리초 | 초 | 분 |
| 범위 | 함수/클래스 | 모듈 간 | 전체 시스템 |
| 격리 | 완전 격리 | 부분 격리 | 실제 환경 |
| 유지비용 | 낮음 | 중간 | 높음 |

상위 레벨 테스트에서 발견한 버그는 새 unit test의 자동 의무가 아니라 `discipline-tdd` §5.5의 candidate다. 같은 계약·boundary·failure mechanism을 기존 권위 테스트가 이미 보호하면 `reuse`하고, 다른 층에서 독립 production failure를 보호할 때만 별도 `add`가 될 수 있다.

> 출처: [The Practical Test Pyramid - Ham Vocke](https://martinfowler.com/articles/practical-test-pyramid.html), [Test Pyramid - Martin Fowler](https://martinfowler.com/bliki/TestPyramid.html)

### 1.2 Google의 SMURF 프레임워크
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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

### 1.4 Migration 전용 테스트와 DB-backed 현행 동작 테스트 식별
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

이 절은 테스트의 **기술적 오라클**만 식별한다. 무엇을 만들고 기존 테스트를 유지·갱신·분리·삭제할지는 `discipline-tdd` §5.5가 소유한다.

| 구분 | 테스트가 성공·실패를 판정하는 근거 | 예 |
|---|---|---|
| migration 전용 | migration 파일·번호·dependency graph·operation·적용 순서·과거 model state·forward/reverse·DDL 자체 | `MigrationExecutor`로 두 migration state를 오가며 데이터 변환을 단언 |
| DB-backed 현행 동작 | 현재 model·ORM·service·API 응답·현재 DB constraint | 현재 모델 저장이 유니크 제약을 지키는지, 서비스 호출 뒤 현재 row가 올바른지 단언 |

Django 테스트 DB 준비 과정에서 migration이 내부 실행된다는 사실만으로 migration 전용 테스트가 되지는 않는다. 반대로 파일명이 일반 통합 테스트처럼 보여도 과거 state나 forward/reverse 결과가 오라클이면 migration 전용이다. 현재 model 테스트는 migration rollout·backfill·reverse 안전의 대체 증거가 아니다.

---

## 2. 테스트 더블 분류 체계
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

이 절은 이미 입장된 case가 승인 의미를 분명하게 판정하도록 assertion을 쓰는 recipe다. assertion 문법이나 더 많은 값을 단언할 수 있다는 사실은 새 case/assertion의 입장 근거가 아니다. 프로그램이 자동으로 코드가 동작하는지 판단하도록 하고, 승인된 결과를 컴퓨터가 검증하게 한다.

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

pytest-django는 `DJANGO_SETTINGS_MODULE`로 settings를 잡고 DB 라이프사이클을 관리한다. 값은 **프로젝트의 `manage.py`/환경에서 감지한 실제 settings 경로**(흔히 평면 `config.settings`)를 쓴다 — `<project>.settings.test`처럼 settings 분할이 **실제로 존재할 때만** test 모듈을 가리키고, 분할이 없으면 평면 모듈을 그대로 쓴다(`settings.test`를 임의로 하드코딩하지 않는다).

```toml
[tool.pytest.ini_options]
# 최소 pytest 버전 요구
minversion = "8.0"

# pytest-django: settings 모듈 — 값은 프로젝트 manage.py/env에서 감지한 실제 경로.
# 분할이 있으면 그 test 모듈(예: config.settings.test), 없으면 평면 모듈을 쓴다.
DJANGO_SETTINGS_MODULE = "config.settings"

# 테스트 검색 경로 — 앱별 test 루트(application/<bounded_context>/test/{unit,integration}/).
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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

conftest.py는 디렉토리별로 배치할 수 있으며, pytest가 테스트 수집 시 각 디렉토리의 conftest.py를 자동으로 로드한다. 하지만 아래 구조는 생성 목록이 아니다. 입장 표의 `owner/path`에 실제 승인된 test artifact가 있는 branch만 만들고, 그 테스트가 실제 공유하는 fixture가 있을 때만 가장 좁은 공통 경로에 `conftest.py`를 둔다. 사용하지 않는 디렉터리·`conftest.py`·예시 test file·빈 package를 만들지 않는다. 의미군 위치의 단일 출처는 `discipline-houserules` §2다.

```
application/
  <app>/
    test/
      integration/                     # 이 의미군에 승인된 테스트가 있을 때만
        test_order_api.py              # 입장 표가 지정한 실제 owner/path 한 예
```

프로젝트 공통 pytest 설정이나 둘 이상의 승인 테스트가 공유하는 fixture가 이미 필요할 때만 루트 또는 공통 `conftest.py`를 사용한다. 연결/트랜잭션 의미(PRAGMA·`BEGIN`·`isolation_level`)를 conftest로 주입하지 않는다. connection/transaction/lock/isolation 메커니즘은 architect 소유이며 필요한 연결 튜닝은 stock `OPTIONS`로만 한다(`implementation-django` §16.4, 본문 §20.5).

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
def test_database_backed_order_creation():
    order = create_order()
    assert order.pk is not None
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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

테스트 스택 동반 패키지(pytest-django, factory_boy, freezegun, responses 등)를 새로 들일 때는 훈련 기억의 버전을 적지 말고 **`implementation-django-ninja` §2.1 버전-핀 규율**(무핀으로 resolve → *실제 설치 버전*을 매니페스트에 핀)을 따른다 — resolve가 기존 Django/핵심 의존성 핀을 올리려 들면 호환 한계 신호이니 기존 핀 안에서 핀하거나 보고한다(설계 반송). 핀 *표기*·매니페스트 위치는 `implementation-django` §3.1·`implementation-django-ninja` §2.1 소유.

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

pytest-cov는 입장된 테스트가 실행하는 경로를 진단하는 도구다. 수치 threshold를 새로 걸어 suite를
실패시키거나 미달 line을 새 test admission 근거로 쓰지 않는다. 프로젝트에 이미 별도 승인된 조직
coverage 정책이 있으면 그 설정은 보존하되 중앙 decision 없이 테스트를 추가하지 않는다.

```bash
pip install pytest-cov

# 기본 사용
pytest --cov=src tests/

# HTML 리포트 생성
pytest --cov=src --cov-report=html tests/

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

기본 mock 도구는 pytest-mock `mocker` 픽스처다(자동 teardown). 패치는 `mocker.patch`/`mocker.patch.object`, 유틸은 `mocker.Mock`/`MagicMock`/`AsyncMock`/`ANY`/`call`/`sentinel`/`PropertyMock`/`seal`/`mock_open`, autospec은 `mocker.patch(..., autospec=True)`. **유일한 예외는 standalone `create_autospec`** — 패치 밖에서 쓸 때만 `from unittest.mock import create_autospec`. raw `unittest.mock`로 패치하지 않는다. (이 절은 mock의 *도구*만 정한다 — *무엇을·얼마나* mock하는지의 교리는 §7.1이 불변으로 소유한다.)

### 7.1 검증 방식 우선순위 [Unit Testing - Khorikov + 파이썬코딩의기술]
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

이 절은 `discipline-tdd` §5.5에서 `add`·`update`된 속성 계약을 표현하는 mechanics다. Hypothesis가 수백 가지 입력을 생성하거나 경계값을 찾을 수 있다는 이유만으로 새 영구 테스트·`@example`·assertion을 추가하지 않는다.

전통적 테스트는 특정 입력값을 직접 선택하지만, Property-Based Testing은 **이미 승인된 코드 속성(property)**을 정의하고 프레임워크가 여러 입력을 생성하여 검증한다.

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

factory_boy는 테스트 객체 생성을 위한 "청사진" 역할을 한다. JSON fixture 파일 대신 Python 코드로 테스트 데이터를 선언적으로 정의한다.

```bash
pip install factory_boy faker
```

factory_boy는 **ORM 애그리거트/엔티티 영속 픽스처의 기본**이다 — 모든 객체에 강제하지 않는다. *정확한 필드 값*이 검증의 핵심인 행(동시성·경계 테스트; 예: §20.5의 CAS-충돌 스파이는 `ProductModel.objects.create(stock=5, version=0)`으로 일부러 정확한 행을 만든다)과 VO/dataclass 구성은 직접 생성이 더 명확하므로 그대로 둔다. 팩토리는 **`application/<bounded_context>/test/factories/`**(패키지)에 둔다 — 이 폴더는 테스트 트리 단일 출처(`discipline-houserules` §2)에 별도로 추가되므로 여기서는 위치만 가리킨다.

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

coverage는 입장된 테스트가 어떤 코드를 실행하는지 진단하는 도구다. 미달 수치나 uncovered line만으로 제품 계약과 독자 failure가 생기지는 않으므로, coverage 목표를 채우기 위한 새 case/assertion을 만들지 않는다.

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
테스트는 적절한 시점에 작성한다. 다만 **언제·어떤 순서로** 테스트를 작성하는지(test-first, Red-Green 리듬 등 작성 시점의 실천)는 작성법이 아니라 방법론이므로 `discipline-tdd` 스킬이 다룬다.

> 출처: Robert C. Martin, "Clean Code" (2008), [FIRST Principles - DZone](https://dzone.com/articles/first-principles-solid-rules-for-tests)

### 15.2 AAA 패턴 (Arrange-Act-Assert)
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

Bill Wake가 처음 명명한 테스트 구조화 패턴이다. 이 절의 AAA·Act 분리·관련 assert 기준은 이미 입장된 case를 읽기 쉽게 표현하는 recipe다. 하나의 테스트를 여러 함수로 나눌 수 있거나 Free Ride를 발견했다는 사실이 새 case/assertion의 근거는 아니다. AAA 패턴을 기본으로 하되, **논리적으로 하나의 승인 행위를 검증하는 관련 assert는 허용**한다.

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
2. **여러 AAA 블록은 입장된 의미 안에서 분리**: 하나의 승인 case에 여러 Act-Assert 쌍이 있으면 가독성을 위해 나눌 수 있다. 분리된 각 함수가 새 제품 의미를 추가하지 않게 한다.
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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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

### 15.4 외부 계약 기댓값은 리터럴로 — 프로덕션 상수 역수입 금지 [Google Testing Blog] [Khorikov]
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

외부 관찰 계약(HTTP 응답 본문·DB 저장값·발행 이벤트 payload)을 검증하는 테스트의 **assert 기댓값**은 완성형 리터럴로 하드코딩한다. 프로덕션 Enum·상수를 import해 기댓값으로 재사용하면 상수 값이 잘못 바뀌어도 테스트가 함께 통과하는 자기참조 오라클(동어반복)이 된다 — wire·DB에 노출된 `.value`는 published/영속 계약이라 그 변경은 내부 리팩터링이 아니라 계약 파괴이고, 리터럴 기댓값의 시끄러운 실패가 의도된 보호다. BC 사유 DB라도 기존 행과의 호환 자체가 계약이다.

```python
# 나쁜 예 — 자기참조 오라클: DeliveryStatus.DELIVERED 값이 "deliverd"로 오타 나도 통과
assert response.json()["status"] == DeliveryStatus.DELIVERED.value

# 좋은 예 — 계약을 리터럴로 고정: 값 회귀 시 시끄럽게 실패
assert response.json()["status"] == "delivered"
```

경계 셋: ① **도메인 내부 단위 테스트**의 심볼 단언(`assert order.status == OrderStatus.DELIVERED`)은 허용 — 거기서의 계약은 전이 행위이지 철자가 아니고, 철자 회귀는 위 계약 테스트가 잡는다. ② 리터럴 동결 대상은 **철자가 곧 계약인 값**(enum 코드·상태 문자열·필드명)이다 — 계산 결과값의 기댓값 표현은 `discipline-tdd` '명백한 데이터'가 소유한다(SUT를 호출하지 않는 독립 산식으로 관계를 드러내는 것 허용). ③ 테스트의 **arrange/act**(픽스처 생성·`.filter()` 준비)는 심볼 사용을 권장한다 — 리터럴 강제는 외부 계약을 관찰하는 assert에만 적용되므로 프로덕션 소비 규율(`discipline-cleancode` §2.14)과 같은 테스트 안에서 충돌하지 않는다.

### 15.5 발행 이벤트 봉투의 union-enum 동기 후보
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

태그드 유니온과 `StrEnum` 파생을 함께 쓰는 구조는 테스트 의무가 아니라 `discipline-tdd` §5.5의 candidate signal이다. 실제 published/wire consumer가 두 목록의 드리프트 때문에 이벤트를 발행·역직렬화·디스패치하지 못하는 **독자 production failure**가 있고, 기존 권위 있는 wire/consumer 테스트가 그 failure를 보호하지 않을 때만 `add`할 수 있다.

입장됐다면 내부 타입 목록을 자명하게 서로 비교하는 데 그치지 말고, 승인된 public literal 태그가 실제 publisher/serializer/consumer boundary에서 보존되는 의미를 검증한다. 기존 계약 테스트가 같은 literal과 failure mechanism을 이미 보호하면 `reuse`다. `isinstance(EventType.X, str)`, `typing.get_args()` 결과, enum·union 멤버 집합처럼 Python/Pydantic 구조만 다시 확인하는 테스트는 별도 공개 Python consumer 계약이 없는 한 `reject`한다.

---

## 16. 테스트 안티패턴

### 16.1 코드 수준 안티패턴
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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

**The Liar 변종 — 산출물 오귀속.** 테스트가 *겨냥한* 새 산출물(명시 제약·새 가드)을 검증하는데, 술어가 *동치인 기존 암묵 가드*(필드 타입의 암묵 CHECK — 예 `PositiveIntegerField`의 `>=0`)가 먼저 통과시키면, 그 테스트는 산출물을 *구별 증명*하지 못한다 — 그 산출물만 약화·제거해도 다른 가드가 green이라 false green이다(예: 명명 `CheckConstraint(stock>=0)`를 약화해도 `PositiveIntegerField`가 `IntegrityError`를 내 통과). 다층 방어로 제약을 병행하는 것 자체는 정상이다(`architecture-db` §9.5 불변식 CHECK 백스톱 병행 권장 — *제거하지 않는다*). 고칠 것은 *테스트 귀속*이다: 명시 제약이 필드 가드와 술어 동치면 그 사실을 docstring에 밝히고(이 테스트는 다층 백스톱을 검증), 제약이 *strictly stronger*(상한·복합·`>=N`)일 때만 그 추가분을 구별하는 단언을 둔다.

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

관련 없는 assertion을 떼어낼 때도 별도 테스트를 자동 생성하지 않는다. 보호할 제품 계약·독자 failure 는 입장 심사 대상으로 소유자(`discipline-tdd` §5.5)에게 보내 decision 을 먼저 받고, 여기서는 기존에 입장된 의미의 가독성만 정리한다.

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

1. **입장된 독립 integration failure가 있는데 그 boundary 보호가 없음** (반대 방향도 동일 — 단순히 한 계층만 존재한다는 이유로 다른 계층 테스트를 추가하지 않음)
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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

이 절은 이미 입장된 테스트가 주장한 failure를 실제로 감지하는지 진단하는 mechanics다. mutation score·생존 mutant·도구 권고는 새 영구 test case/assertion을 승인하지 않는다. 생존 mutant는 `discipline-tdd` §5.5의 candidate로 보내며, 제품 계약과 독자 failure가 없거나 기존 보호와 중복이면 `reject`·`reuse`한다.

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
- Survived (생존): 테스트가 변형을 감지 못함 -> 입장 심사가 필요한 잠재 공백
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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

뮤테이션 점수는 진단 정보이지 목표 quota나 완료 조건이 아니다. 생존 mutant를 분석하되, 승인된 제품 계약의 독자 failure가 확인된 `add/update`에만 테스트를 작성한다.

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

## 19. Django Ninja API 계약 테스트
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

이 절의 client·assert 예시는 `discipline-tdd` §5.5에서 입장된 API 계약의 작성 mechanics다. framework 동작이나 도구 사용법을 확인하기 위해 endpoint·status·Schema 테스트를 추가하지 않는다.

Django Ninja의 **공개 HTTP 계약**은 실제 URLconf에 mount된 endpoint를 Django test client로 호출해 검증한다. 그래야 registrar·URL prefix·middleware·인증과 실제 API instance를 함께 지난다.

`ninja.testing.TestClient(router)`나 `ninja_extra.testing.TestClient(Controller)`는 별도 입장된 **adapter-local 계약**에서 mount와 무관한 독자 failure를 보호할 때만 쓸 수 있다. middleware·URL resolver·registrar를 통과하지 않으므로 public HTTP/OpenAPI 증거를 대신하지 못하고, 같은 failure를 mounted 테스트가 이미 보호하면 `reuse`다.

### 19.1 Mounted 공개 응답 계약
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

```python
from django.test import Client


client = Client()


def test_order_detail_contract(order_factory):
    order = order_factory(status="paid", total_amount="120.00")

    response = client.get(f"/api/orders/{order.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": order.id,
        "status": "paid",
        "total_amount": "120.00",
    }
```

검증 대상은 입장된 public API contract다. 내부 service 호출 여부, private helper, ORM query 문자열처럼 구현 세부사항은 직접 검증하지 않는다.

### 19.2 요청 검증과 오류 응답
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

`discipline-tdd` §5.5의 decision row가 `add`·`update`인 오류 계약에만 이 절을 적용한다.
오류 Schema가 존재하거나 framework가 응답을 직렬화한다는 사실만으로 테스트를 만들지 않는다.

#### 19.2.1 승인된 HTTP 오류 계약
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

승인된 controller mapping은 실제 URLconf에 mount된 Django client 요청으로 관찰한다. application
collaborator가 승인된 구체 예외를 내게 하고, 응답의 HTTP status, 승인된 body와 error-sensitive
header 값·부재를 리터럴로 검증한다. serializer, helper, factory, mapping, handler 내부를 mock하거나
직접 unit test하지 않는다.

기댓값은 해당 decision row의 승인된 리터럴을 쓰되, dddjango가 고정하는 공통 오류 schema property
목록은 없다. 기존 공통 오류 schema shape를 바꾸려면 별도의 명시적 사용자
승인이 필요하며, 승인 전에는 변경도 그 변경을 전제로 한 assertion도 만들지 않는다.

framework-owned 401/403/route 404/422/429/`HttpError`/500은 별도 입장 행에서 승인된 경우에만
검증한다. 별도 승인 또는 실제 deployed consumer evidence가 없는 Django Ninja/Pydantic 기본 body,
직렬화, coercion은 제품 계약처럼 exact snapshot하지 않고 status와 민감 정보 비노출만 smoke한다.
반대로 기존 지원 계약이나 consumer가 의존하는 public wire field가 입장됐다면 그 관련 field만
리터럴로 검증한다. 전체 framework body snapshot이나 private metadata까지 넓히지 않는다.

#### 19.2.2 공개 Python Schema 계약
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

Schema를 Python에서 직접 검증하는 테스트를 일괄 금지하지 않는다. HTTP와 별개로 실제 public
Python consumer 또는 승인된 지원 계약이 확인되면 **별도 decision row**로 입장시켜, 그 consumer가
의존하는 field·signature·기본값·생성 의미만 검증한다. HTTP wire 테스트를 내부 Schema 호출로
대체하거나 하나의 행에 섞지 않는다.

별도 공개 계약이 없는 다음 항목은 자동 제품 테스트가 아니다.

- Pydantic private API와 decorator/validator 배치
- `ValidationError.loc`의 framework 표현
- callable source digest와 source/AST/import 형태
- model config, hook, serializer, computed-field inventory
- nominal inheritance나 Python/Django/Pydantic 기본 동작만 확인하는 assertion

#### 19.2.3 공개 OpenAPI 계약
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

OpenAPI가 승인된 public consumer contract이면 실제 URLconf에 mount된 문서 endpoint를 Django
client로 요청하고, 관련 operation·status·media type·schema만 검증한다. 전체 document나 무관한
component를 snapshot하지 않는다.

`api.get_openapi_schema()`, schema helper, postprocessor 같은 내부 직접 호출은 실제 mounted generated
document를 대신하지 않는다. OpenAPI가 공개 계약으로 승인되지 않았거나 기존 권위 테스트가 같은
operation/status/schema drift를 보호하면 새 테스트를 만들지 않는다.


### 19.3 인증, 페이지네이션, 필터링
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

```python
def test_order_list_requires_auth():
    response = client.get("/api/orders")

    assert response.status_code in {401, 403}


def test_order_list_pagination_contract(auth_headers, order_factory):
    order_factory.create_batch(3)

    response = client.get("/api/orders", {"limit": 2, "offset": 0}, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert set(body) >= {"items", "count"}
    assert len(body["items"]) == 2
```

인증 우회, user fixture, header 이름은 프로젝트의 auth contract에 맞춘다. 권한/페이지네이션/필터링 계약이 불명확하면 API 설계를 먼저 확정한다.

### 19.4 pytest-django DB 접근 선택
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

Django ORM을 사용하는 API 테스트는 pytest-django의 DB access 규칙을 따른다. 기본적으로 DB 접근은 차단되며, DB가 필요한 테스트는 `pytest.mark.django_db`, `db`, `transactional_db` 중 하나로 의도를 명시한다.

```python
import pytest
from django.test import Client


client = Client()


@pytest.mark.django_db
def test_order_detail_reads_database(order_factory):
    order = order_factory()

    response = client.get(f"/api/orders/{order.id}")

    assert response.status_code == 200
```

일반 ORM read/write 검증은 `pytest.mark.django_db`로 충분하다. commit/rollback 효과, `transaction.on_commit`, row lock, 별도 connection 관찰처럼 실제 transaction 경계가 테스트 대상이면 `pytest.mark.django_db(transaction=True)` 또는 `transactional_db` fixture를 사용한다.

> 출처: [Django Ninja Testing](https://django-ninja.dev/guides/testing/), [pytest-django Database access](https://pytest-django.readthedocs.io/en/latest/database.html), [pytest-django helpers](https://pytest-django.readthedocs.io/en/latest/helpers.html)

---

## 20. Idempotency와 동시성 테스트
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

이 절의 idempotency·transaction·race·CAS·spy recipe는 `discipline-tdd` §5.5에서 `add`·`update`된 case의 mechanics다. 동시성이라는 주제, DB 사용, 예제의 존재, 결정성·속도 개선만으로 새 테스트 수를 늘리지 않는다. domain/application/DB/adapter/public contract에서 독립 failure mechanism이 확인되면 각각 유효할 수 있고, 기존 권위 테스트가 같은 계약·boundary·failure를 보호하면 `reuse`한다.

입장된 중복 요청, 재시도, race condition, row lock 계약은 일반 unit test만으로 충분히 보호되지 않을 수 있다. 보호하려는 failure mechanism에 DB unique constraint, transaction, lock, idempotency storage가 관여하면 integration/API contract mechanics를 선택한다.

### 20.1 Idempotency replay 계약
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

Idempotency-Key를 지원하는 write API는 같은 key와 같은 payload의 재전송이 같은 결과를 반환하거나 기존 처리 결과를 재사용해야 한다. 서로 다른 payload가 같은 key를 재사용하면 충돌로 실패해야 한다.

```python
import json

import pytest
from django.test import Client


client = Client()


@pytest.mark.django_db
def test_create_order_idempotency_replays_same_result(auth_headers):
    headers = {**auth_headers, "Idempotency-Key": "order-create-001"}
    payload = {"sku": "BOOK-1", "quantity": 1}

    first = client.post(
        "/api/orders", data=json.dumps(payload), content_type="application/json", headers=headers
    )
    second = client.post(
        "/api/orders", data=json.dumps(payload), content_type="application/json", headers=headers
    )

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
        "/api/orders",
        data=json.dumps({"sku": "BOOK-1", "quantity": 1}),
        content_type="application/json",
        headers=headers,
    )
    second = client.post(
        "/api/orders",
        data=json.dumps({"sku": "BOOK-1", "quantity": 2}),
        content_type="application/json",
        headers=headers,
    )

    assert first.status_code == 201
    assert second.status_code in {400, 409, 422}
    assert Order.objects.count() == 1
```

정확한 status code와 response body는 `architecture-api`에서 정한 idempotency contract를 따른다. 저장소 스키마, uniqueness, transaction boundary가 불명확하면 `architecture-db`를 먼저 사용한다.

### 20.2 중복 생성 방지와 DB 제약
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

```python
import pytest
from django.db import IntegrityError


@pytest.mark.django_db
def test_idempotency_key_is_unique_per_actor(idempotency_record_factory, user):
    idempotency_record_factory(user=user, key="same-key")

    with pytest.raises(IntegrityError):
        idempotency_record_factory(user=user, key="same-key")
```

서비스 계층 test와 DB unique constraint 후보가 서로 다른 failure mechanism을 보호하고 기존 DB 보장이 없다면 DB-backed `add`가 될 수 있다. 같은 계약·boundary·failure를 이미 보호하면 별도 테스트를 만들지 않는다. 입장된 DB 제약이 동작의 일부라면 mock repository로 대체하지 않는다.

### 20.3 Transaction과 row lock 테스트
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

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
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

입장된 CAS 재시도 failure를 결정적으로 검증해야 할 때 이 recipe를 쓴다. §20.4의 스레드 race 테스트는 실제 경합을 관찰하지만 SQLite에서 비결정적이고 flaky하기 쉽다. 실제 스레드 없이 *다른 트랜잭션이 먼저 `version`을 올린 상황*을 흉내 내 CAS 0행을 1회 강제하고, 쓰기 연산이 재조회→도메인 메서드 재실행으로 일관되게 수렴하는지 검증할 수 있다. 이 결정적 recipe가 스레드 테스트를 자동으로 추가하거나 복제할 근거는 아니다.

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
    reserve_stock = ReserveStockCommand(ConflictOnceRepository())

    result = reserve_stock.execute(ReserveStockRequest(product_id=product.id, quantity=2))

    product.refresh_from_db()
    assert product.stock == 3  # 첫 CAS 0행 → 재시도 성공, 정확히 한 번만 차감
```

이 테스트는 단일 connection·단일 스레드이므로 `transaction=True`가 필요 없다 — 스파이의 `.update()`와 쓰기 연산의 재조회가 같은 connection에서 일어나 갱신된 `version`을 그대로 본다. 실제 별도 connection·스레드 경합 관찰은 §20.4의 영역이다.

이 테스트는 빠르고 결정적이어서 동시성 가드 회귀를 막는 1차 방어다. 단, 스파이가 구체 리포지토리의 `save_with_version_guard` 시그니처에 결합하므로 그 메서드명·시그니처가 바뀌면 함께 갱신한다(가드의 *내부 CAS 구현* 변경에는 영향받지 않는다). 스레드 기반 §20.4는 통합 신뢰를 위한 보조이며, 운영과 같은 backend(PostgreSQL 등)를 testcontainers로 띄워 돌리는 편이 SQLite보다 안정적이다.

**연결 의미를 바꿔 테스트를 성립시키지 않는다.** SQLite에서 race를 *관찰*하려고 `BEGIN IMMEDIATE`·격리 수준·begin 모드가 필요해 보여도, 그것을 **커스텀 `DatabaseWrapper`/DB 백엔드로 구현하지 않는다** — 트랜잭션·락·격리 *메커니즘*은 architect가 소유하며(`architecture-db` §9.5 연결 설정 경계), 코더가 환경 한계를 이유로 임의 대체하는 것은 *출처-불문* 금지다(`implementation-django` §16.4). 필요한 연결 튜닝은 **stock `OPTIONS`만**으로 한다(IMMEDIATE는 `transaction_mode`[Django 5.1+], busy 대기는 `timeout`, 안전 PRAGMA 화이트리스트). 위 결정적 CAS-충돌 스파이는 애초에 이런 연결 조작이 필요 없다 — 그래서 §16.4 위반 압력 없이 동시성 기준을 검증한다.

---

## 21. 테스트 디버깅 기법
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

범용 Python 디버깅(repr, pdb, breakpoint)은 `implementation-python` 스킬을 참조한다.

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
