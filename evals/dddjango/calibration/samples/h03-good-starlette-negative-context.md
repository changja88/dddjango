# Starlette 주문 생성 엔드포인트

Django Ninja 없이 Starlette만 사용한다. Django 프로젝트 파일이나 데이터베이스
모델 계층은 만들지 않는다.

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def create_order(request):
    payload = await request.json()
    if not payload.get("items"):
        return JSONResponse({"detail": "items is required"}, status_code=422)
    return JSONResponse({"id": "ord_1", "items": payload["items"]}, status_code=201)


app = Starlette(routes=[Route("/orders", create_order, methods=["POST"])])
```

실행:

```sh
python -m pip install starlette uvicorn
uvicorn app:app --reload
curl -i -X POST http://127.0.0.1:8000/orders \
  -H 'content-type: application/json' \
  -d '{"items":[{"sku":"A-1","quantity":1}]}'
```

검증은 `pytest`와 Starlette `TestClient`로 `POST /orders`가 `201`을 반환하고,
items가 없으면 `422`를 반환하는지 확인한다.
