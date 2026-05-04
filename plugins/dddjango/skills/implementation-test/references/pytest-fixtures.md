# pytest 기본 구조와 Fixture 레퍼런스

pytest 기본 사용법, 픽스처, 단언, 파라미터화에 대한 상세 규칙과 예시.

---

## 1. pytest 기본 구조

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

---

## 2. Fixture (setUp/tearDown)

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

**모듈 단위 픽스처** (비용이 큰 통합 테스트용):

```python
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

---

## 3. xUnit 패턴과 pytest 매핑

| xUnit 개념 | pytest 대응 |
|-----------|-----------|
| setUp() | `@pytest.fixture` 또는 `setup_method()` |
| tearDown() | fixture의 `yield` 이후 코드 |
| setUpModule() | `@pytest.fixture(scope="module")` |
| tearDownModule() | module 스코프 fixture의 teardown |
| TestSuite | `pytest.mark` 또는 디렉토리 구조 |

---

## 4. 단언(Assertion)

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

---

## 5. 예외 테스트

예외가 발생하는 것이 정상인 경우에는, 예상되는 예외를 잡아서 무시하고, 예외가 발생하지 않은 경우에 한해서 테스트가 실패하게 만든다.

```python
def test_invalid_input_raises():
    with pytest.raises(ValueError) as exc_info:
        process_input(-1)
    assert "음수" in str(exc_info.value)
```

---

## 6. 파라미터화 테스트

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

---

## 7. conftest.py를 활용한 공유 픽스처

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

---

## 8. monkeypatch를 활용한 환경 격리

```python
def test_api_url(monkeypatch):
    monkeypatch.setenv("API_URL", "http://test.example.com")
    config = load_config()
    assert config.api_url == "http://test.example.com"
```

> 시간 모킹의 경우 monkeypatch 직접 교체 대신 freezegun/time-machine 전용 라이브러리 사용을 권장한다.

---

## 9. tmp_path를 활용한 파일 테스트

```python
def test_file_processing(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world")

    output_file = tmp_path / "output.txt"
    process_file(input_file, output_file)

    assert output_file.read_text() == "HELLO WORLD"
```

---

## 10. 전체 테스트 실행

테스트 디렉토리는 1차 환경(`tests/isolated/`, `tests/real/`), 2차 범위(`unit/`, `integration/`, `e2e/`)로 분리되어 있다. 환경별로 실행 정책이 다르므로 명령도 환경 단위로 나눠 쓴다.

```bash
# CI 기본: 통제된/제공된 환경에서 결정적으로 실행되는 스위트
pytest tests/isolated/

# 마커 기반 동등 표현 (isolated/real 마커는 디렉토리에서 자동 부착됨)
pytest -m "not real"

# 사전 환경 셋업이 필요한 실 환경 스위트 (pre-deploy 잡에서)
pytest tests/real/

# 범위만 좁혀 실행
pytest tests/isolated/unit/         # 단위만
pytest tests/isolated/integration/  # in-memory/testcontainers 통합만
pytest tests/real/e2e/              # 실 E2E만

# 보조 옵션
pytest -m "not slow"   # 느린 테스트 제외
pytest -k "test_auth"  # 이름 패턴 매칭
pytest --lf            # 직전 실패한 테스트만 재실행
```

CI 파이프라인은 두 단계로 분리한다 -- (1) 모든 PR/푸시에서 `pytest tests/isolated/`를 실행해 결정적으로 빠른 피드백을 주고, (2) 배포 직전 게이트에서 자격 증명을 주입해 `pytest tests/real/`을 실행한다.
