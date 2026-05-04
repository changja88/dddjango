# Mock 패턴 레퍼런스

unittest.mock 실전 사용법에 대한 상세 규칙과 예시.

---

## 1. Mock 기본 사용법

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

---

## 2. PropertyMock: 프로퍼티 모킹

```python
from unittest.mock import patch, PropertyMock

class DatabaseConnection:
    @property
    def is_connected(self):
        return self._check_connection()

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
        side_effect=[10, 50, 200]
    ):
        conn = DatabaseConnection()
        assert conn.latency_ms == 10
        assert conn.latency_ms == 50
        assert conn.latency_ms == 200
```

---

## 3. AsyncMock: 비동기 함수 모킹

Python 3.8+에서 제공되며, 비동기 함수를 모킹할 때 사용한다.

```python
from unittest.mock import AsyncMock, patch, MagicMock

class AsyncService:
    async def fetch_data(self, url: str) -> dict: ...
    async def process(self) -> str:
        data = await self.fetch_data("https://api.example.com/data")
        return data["result"]

@pytest.mark.asyncio
async def test_async_service():
    service = AsyncService()
    service.fetch_data = AsyncMock(return_value={"result": "success"})
    result = await service.process()
    assert result == "success"
    service.fetch_data.assert_awaited_once_with("https://api.example.com/data")

# async 컨텍스트 매니저 모킹
@pytest.mark.asyncio
async def test_async_context_manager():
    mock_session = MagicMock()
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

---

## 4. seal(): Mock 객체 봉인

`seal()`은 Mock 객체를 봉인하여, 미리 설정하지 않은 속성/메서드에 접근하면 에러를 발생시킨다.

```python
from unittest.mock import MagicMock, seal

def test_sealed_mock():
    user = MagicMock()
    user.name = "Alice"
    user.email = "alice@example.com"
    seal(user)

    assert user.name == "Alice"
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

    assert mock_service.get_user(1) == {"id": 1, "name": "Alice"}
    with pytest.raises(AttributeError):
        mock_service.update_user(1, name="Bob")
```

---

## 5. side_effect 고급 활용

```python
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
        {"status": "success"},
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
