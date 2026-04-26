# Django Ninja API 코드 리뷰 및 리팩토링

## 코드 리뷰 -- 발견된 문제점

### 1. Schema 미사용 (심각도: 높음)
Django Ninja의 핵심 기능인 Schema(Pydantic 기반)를 전혀 사용하지 않고 있다. `json.loads(request.body)`로 직접 파싱하면 입력 검증이 없어 잘못된 데이터가 DB에 들어갈 수 있고, 자동 문서화(OpenAPI/Swagger)의 이점도 잃는다.

### 2. 잘못된 HTTP 메서드 (심각도: 높음)
`remove_item`이 `@api.get`으로 정의되어 있다. 삭제는 `@api.delete`를 사용해야 한다. GET 요청으로 리소스를 삭제하면 크롤러나 프리페치에 의해 의도치 않은 삭제가 발생할 수 있다.

### 3. 예외 처리 부재 (심각도: 높음)
`Item.objects.get(id=id)`는 해당 객체가 없을 때 `DoesNotExist` 예외를 발생시킨다. 이를 처리하지 않으면 500 에러가 클라이언트에 노출된다.

### 4. 함수 내부 import (심각도: 낮음)
`import json`이 함수 내부에 있다. 파일 상단에 두는 것이 PEP 8 관례이다. 다만 리팩토링 후에는 Schema를 사용하므로 `json` import 자체가 불필요해진다.

### 5. 응답 형식 비일관성 (심각도: 중간)
- `get_items`/`get_item`: 아이템 데이터 직접 반환
- `add_item`: `{'id': ...}` 반환
- `edit_item`/`remove_item`: `{'ok': True}` 반환

응답 형식이 엔드포인트마다 제각각이다.

### 6. 타입 힌트 부재 (심각도: 중간)
Django Ninja는 타입 힌트 기반으로 동작한다. 타입 힌트가 없으면 자동 문서화 품질이 떨어지고, 파라미터 변환도 제대로 되지 않는다.

### 7. 페이지네이션 미적용 (심각도: 중간)
`get_items`에서 `Item.objects.all()`을 그대로 반환한다. 데이터가 많아지면 성능 문제가 발생한다.

---

## 리팩토링 결과

```python
from ninja import NinjaAPI, Schema
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from decimal import Decimal
from typing import Optional

api = NinjaAPI()


# ──────────────────────────────────────
# Schemas
# ──────────────────────────────────────

class ItemIn(Schema):
    name: str
    price: Decimal


class ItemUpdate(Schema):
    name: Optional[str] = None
    price: Optional[Decimal] = None


class ItemOut(Schema):
    id: int
    name: str
    price: Decimal


# ──────────────────────────────────────
# Endpoints
# ──────────────────────────────────────

@api.get("/items", response=list[ItemOut])
@paginate(LimitOffsetPagination)
def list_items(request):
    return Item.objects.all()


@api.get("/items/{item_id}", response=ItemOut)
def get_item(request, item_id: int):
    return get_object_or_404(Item, id=item_id)


@api.post("/items", response={201: ItemOut})
def create_item(request, payload: ItemIn):
    item = Item.objects.create(**payload.dict())
    return 201, item


@api.patch("/items/{item_id}", response=ItemOut)
def update_item(request, item_id: int, payload: ItemUpdate):
    item = get_object_or_404(Item, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@api.delete("/items/{item_id}", response={204: None})
def delete_item(request, item_id: int):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return 204, None
```

---

## 변경 사항 요약

| 항목 | 원본 | 리팩토링 |
|---|---|---|
| 입력 검증 | `json.loads` 수동 파싱 | `Schema`로 자동 검증 |
| 응답 직렬화 | dict 수동 변환 | `response=ItemOut`으로 자동 직렬화 |
| 삭제 메서드 | `GET /items/{id}/remove` | `DELETE /items/{item_id}` |
| 수정 메서드 | `PUT` (전체 교체 의미) | `PATCH` (부분 수정 의미) |
| 예외 처리 | 없음 (`objects.get` 직접 호출) | `get_object_or_404`로 404 자동 반환 |
| 페이지네이션 | 없음 | `LimitOffsetPagination` 적용 |
| 파라미터 이름 | `id` (파이썬 내장 함수와 충돌) | `item_id` |
| 생성 응답 코드 | 200 | 201 (Created) |
| 삭제 응답 코드 | 200 + `{'ok': True}` | 204 (No Content) |
| 타입 힌트 | 없음 | 모든 파라미터에 적용 |
