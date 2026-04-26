# HTTP 모킹 레퍼런스

responses, aioresponses를 사용한 HTTP 모킹의 상세 규칙과 예시.

---

## 1. responses: requests 라이브러리 모킹

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

# 여러 응답 등록 (순차적)
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

---

## 2. aioresponses: aiohttp 모킹

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

---

## 3. HTTPretty: 소켓 레벨 인터셉트

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

---

## 4. 선택 가이드

| 라이브러리 | 대상 | 특징 |
|-----------|------|------|
| responses | requests | 가장 많이 사용, 간결한 API |
| aioresponses | aiohttp | async/await 전용 |
| HTTPretty | 모든 HTTP 라이브러리 | 소켓 레벨 인터셉트 |

> 출처: [responses - PyPI](https://pypi.org/project/responses/), [aioresponses - GitHub](https://github.com/pnuckowski/aioresponses), [HTTPretty Documentation](https://httpretty.readthedocs.io/)
