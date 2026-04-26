# Python 테스트 코드 작성 가이드

## 1. Python 테스트 실전 패턴

### 1.1 pytest 기본 구조 [파이썬코딩의기술]

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

### 1.2 Fixture (setUp/tearDown) [테스트주도 개발 + 파이썬코딩의기술]

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

### 1.3 Mock 활용법 [파이썬코딩의기술]

**목과 페이크의 차이**:

- **목(Mock)**: 흉내 내려는 대상에 의존하는 함수들이 어떤 요청을 보내면 어떤 응답을 보내야 할지 알고, 요청에 따라 적절한 응답을 돌려준다
- **페이크(Fake)**: 기능을 대부분 제공하지만 더 단순한 구현을 사용한다 (예: 메모리 내 데이터베이스)

**Mock 기본 사용법**:

```python
from unittest.mock import Mock, patch, ANY


# 1. Mock 객체 생성 (spec으로 인터페이스 강제)
mock_api = Mock(spec=WeatherAPI)
mock_api.get_temperature.return_value = 25.0

result = get_weather_report(mock_api, "서울")

mock_api.get_temperature.assert_called_once_with("서울")
assert "25.0" in result


# 2. 예외 발생 모킹 (side_effect)
mock_api.get_temperature.side_effect = ConnectionError("타임아웃")

with pytest.raises(ConnectionError):
    get_weather_report(mock_api, "서울")


# 3. patch 데코레이터로 모듈 레벨 모킹
@patch("myapp.weather.requests.get")
def test_fetch_weather(mock_get):
    mock_get.return_value.json.return_value = {"temp": 25.0}
    result = fetch_weather("서울")
    assert result["temp"] == 25.0


# 4. ANY를 사용한 유연한 검증
mock_api.get_temperature.assert_called_with(ANY, "서울")
```

**의존 관계 캡슐화로 모킹을 쉽게 만들기** [파이썬코딩의기술]:

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


def test_process_order():
    mock_db = Mock()
    mock_db.get_order.return_value = Order(email="test@test.com")
    mock_email = Mock()

    processor = OrderProcessor(mock_db, mock_email)
    processor.process(1)

    mock_email.send.assert_called_once_with("test@test.com", "주문 완료")
```

---

## 2. xUnit 패턴과 pytest 매핑 [테스트주도 개발 + 파이썬코딩의기술]

### 2.1 단언(Assertion)

프로그램이 자동으로 코드가 동작하는지에 대한 판단을 수행하도록 해야 한다. 판단 결과가 불리언 값이어야 하며 컴퓨터에 의해 검증되어야 한다.

**화이트박스 테스트를 바라는 것은 테스팅 문제가 아니라 설계 문제**다. public 프로토콜만을 이용해서 테스트를 작성해야 한다.

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

### 2.2 픽스처 (Fixture)

| xUnit 개념 | pytest 대응 |
|-----------|-----------|
| setUp() | `@pytest.fixture` 또는 `setup_method()` |
| tearDown() | fixture의 `yield` 이후 코드 |
| setUpModule() | `@pytest.fixture(scope="module")` |
| tearDownModule() | module 스코프 fixture의 teardown |
| TestSuite | `pytest.mark` 또는 디렉토리 구조 |

### 2.3 예외 테스트

예외가 발생하는 것이 정상인 경우에는, 예상되는 예외를 잡아서 무시하고, 예외가 발생하지 않은 경우에 한해서 테스트가 실패하게 만든다.

```python
def test_invalid_input_raises():
    with pytest.raises(ValueError) as exc_info:
        process_input(-1)
    assert "음수" in str(exc_info.value)
```

### 2.4 전체 테스트

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

## 3. 디버깅 기법 [파이썬코딩의기술]

### 3.1 repr 문자열 활용

디버깅을 할 때 `print`를 사용한다면 `repr`을 호출해서 타입이 다른 경우에도 명확히 차이를 볼 수 있게 만들어야 한다.

```python
print(repr(5))    # 5
print(repr('5'))  # '5'

# 커스텀 클래스에 __repr__ 정의
class Money:
    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"
```

### 3.2 pdb 대화형 디버거

```python
def compute(data):
    result = transform(data)
    breakpoint()  # 여기서 대화형 디버거 시작
    return finalize(result)
```

주요 명령어:

| 명령 | 설명 |
|-----|------|
| `where` | 현재 호출 스택 출력 |
| `up` / `down` | 호출 스택에서 이동 |
| `step` | 다음 줄 실행 (함수 내부 진입) |
| `next` | 다음 줄 실행 (함수 호출 건너뜀) |
| `return` | 현재 함수 반환까지 실행 |
| `continue` | 다음 중단점까지 계속 |
| `quit` | 디버거 종료 |

사후 디버깅: `python -m pdb -c continue program.py`

---

## 4. pytest 고급 패턴

### 4.1 파라미터화 테스트

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

### 4.2 conftest.py를 활용한 공유 픽스처

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

### 4.3 monkeypatch를 활용한 환경 격리

```python
def test_api_url(monkeypatch):
    monkeypatch.setenv("API_URL", "http://test.example.com")
    config = load_config()
    assert config.api_url == "http://test.example.com"


def test_with_fake_time(monkeypatch):
    import datetime
    fake_now = datetime.datetime(2025, 1, 1, 12, 0, 0)
    monkeypatch.setattr("myapp.utils.datetime", Mock(now=Mock(return_value=fake_now)))
```

### 4.4 tmp_path를 활용한 파일 테스트

```python
def test_file_processing(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world")

    output_file = tmp_path / "output.txt"
    process_file(input_file, output_file)

    assert output_file.read_text() == "HELLO WORLD"
```

---

## 참고 문헌

| 출처 | 다룬 내용 |
|------|---------|
| 테스트주도 개발 (Kent Beck) | xUnit 패턴, 픽스처, 단언, 예외 테스트 |
| 파이썬코딩의기술 (Brett Slatkin) | TestCase, setUp/tearDown, Mock, 의존 관계 캡슐화, repr, pdb |
