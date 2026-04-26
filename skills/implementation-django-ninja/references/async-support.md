# 비동기 지원 레퍼런스

## 1. async def 뷰

Django 3.1부터 async 뷰를 지원하며, Django Ninja는 이를 완전히 활용한다. 네트워크 호출, 데이터베이스 쿼리, 디스크 I/O에서 특히 유리하다.

### 동기 버전

```python
import time

@api.get("/say-after")
def say_after(request, delay: int, word: str):
    time.sleep(delay)
    return {"saying": word}
```

### 비동기 버전

```python
import asyncio

@api.get("/say-after")
async def say_after(request, delay: int, word: str):
    await asyncio.sleep(delay)
    return {"saying": word}
```

변경 사항은 두 가지뿐이다: `async def`로 선언, `await` 사용.

## 2. ASGI 서버

비동기 뷰를 실행하려면 ASGI 서버가 필요하다.

### Uvicorn

```bash
pip install uvicorn
uvicorn your_project.asgi:application --reload
```

### Daphne

```bash
pip install daphne
daphne your_project.asgi:application
```

### 성능 비교

100개 동시 요청 기준:
- **ASGI (async)**: ~3초, 최소한의 오버헤드로 완료
- **WSGI (sync)**: 10개 이상의 워커 + 스레딩 필요

## 3. sync/async 혼합

Django Ninja는 동기와 비동기 엔드포인트를 동일한 API에서 자동으로 라우팅한다.

```python
import time
import asyncio

@api.get("/say-sync")
def say_after_sync(request, delay: int, word: str):
    time.sleep(delay)
    return {"saying": word}

@api.get("/say-async")
async def say_after_async(request, delay: int, word: str):
    await asyncio.sleep(delay)
    return {"saying": word}
```

동기 뷰와 비동기 뷰를 같은 NinjaAPI 인스턴스에 자유롭게 섞어 쓸 수 있다. Django가 내부적으로 적절한 실행 방식을 선택한다.

## 4. ORM 제약사항

Django ORM은 기본적으로 "async-unsafe"이다. 글로벌 상태 제한 때문에 async 뷰에서 직접 ORM을 호출하면 `SynchronousOnlyOperation` 예외가 발생한다.

### 4.1 sync_to_async 래퍼 (Django 4.0 이하)

```python
from asgiref.sync import sync_to_async

@api.get("/blog/{post_id}")
async def get_blog(request, post_id: int):
    blog = await sync_to_async(Blog.objects.get)(pk=post_id)
    return {"title": blog.title}
```

### 4.2 Django 4.1+ 네이티브 async ORM

Django 4.1부터 ORM 메서드의 async 버전이 제공된다.

```python
@api.get("/blog/{post_id}")
async def get_blog(request, post_id: int):
    blog = await Blog.objects.aget(pk=post_id)
    return {"title": blog.title}
```

주요 async ORM 메서드:
- `aget()`, `acreate()`, `aupdate()`, `adelete()`
- `afirst()`, `alast()`, `acount()`, `aexists()`
- `aget_or_create()`, `aupdate_or_create()`
- `abulk_create()`, `abulk_update()`

### 4.3 Lazy QuerySet 주의사항

Django QuerySet은 지연 평가(lazily evaluated)된다. async 뷰에서 직접 반복하면 안 된다.

```python
# 잘못된 방법 - SynchronousOnlyOperation 발생 가능
@api.get("/blogs")
async def list_blogs(request):
    blogs = Blog.objects.all()  # 이 시점에서는 쿼리 실행 안 됨
    return [{"title": b.title} for b in blogs]  # 여기서 동기 실행 시도

# 올바른 방법 1: sync_to_async로 리스트 강제 평가
@api.get("/blogs")
async def list_blogs(request):
    all_blogs = await sync_to_async(list)(Blog.objects.all())
    return [{"title": b.title} for b in all_blogs]

# 올바른 방법 2: async for 반복 (Django 4.1+)
@api.get("/blogs")
async def list_blogs(request):
    all_blogs = [blog async for blog in Blog.objects.all()]
    return [{"title": b.title} for b in all_blogs]
```

## 5. async 인증

내장 인증 클래스(`HttpBearer`, `APIKeyQuery` 등)는 기본적으로 async 호환이 아니다. 커스텀 async 인증 함수를 정의하여 사용한다.

```python
async def async_auth(request):
    key = request.headers.get("Authorization")
    if not key:
        return None
    # 비동기 토큰 검증 로직
    user = await sync_to_async(Token.objects.get)(key=key)
    return user

@api.get("/pets", auth=async_auth)
def pets(request):
    return {"pets": ["dog", "cat"]}
```

참고: 핸들러 자체는 async일 필요가 없다. `auth` 파라미터에 async callable을 전달하면 된다.

## 6. 실전 예제: Elasticsearch 비동기 검색

```python
from ninja import NinjaAPI
from elasticsearch import AsyncElasticsearch

api = NinjaAPI()
es = AsyncElasticsearch()

@api.get("/search")
async def search(request, q: str):
    resp = await es.search(
        index="documents",
        body={"query": {"query_string": {"query": q}}},
        size=20,
    )
    return resp["hits"]
```

## 7. TestAsyncClient

비동기 엔드포인트 테스트에는 `TestAsyncClient`를 사용한다.

```python
from ninja.testing import TestAsyncClient

client = TestAsyncClient(router)

# 테스트 함수도 async여야 한다
async def test_async_endpoint():
    response = await client.get("/say-async?delay=1&word=hello")
    assert response.status_code == 200
    assert response.json() == {"saying": "hello"}
```

## 8. async 뷰 선택 가이드

| 상황 | 권장 |
|---|---|
| 외부 API 호출이 많은 엔드포인트 | async |
| CPU 바운드 작업 (이미지 처리 등) | sync (또는 별도 워커) |
| 단순 ORM CRUD | sync (간단함) 또는 async (Django 4.1+) |
| WebSocket 처리 | async 필수 |
| 기존 sync 코드와 통합 | sync (호환성) |

## 9. ASGI 설정 파일

```python
# your_project/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

application = get_asgi_application()
```
