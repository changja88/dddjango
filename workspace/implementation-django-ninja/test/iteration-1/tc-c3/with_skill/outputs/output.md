# Django Ninja API Review & Refactoring

## Review

### Review Checklist

- [x] DRF patterns used instead of Django Ninja -- 해당 없음
- [x] Missing type hints on endpoint parameters or return types -- **위반 발견**
- [x] Schema exposing all model fields without explicit selection -- **위반 발견** (Schema 자체가 미사용)
- [x] Missing authentication on endpoints that require it -- **위반 발견**
- [x] No pagination on list endpoints -- **위반 발견**
- [x] No error handling or non-standard error format -- **위반 발견**
- [x] Sync view where async would improve performance -- 해당 코드 규모에서는 큰 차이 없으나 개선 가능
- [x] FilterSchema not used for complex filtering logic -- 해당 없음 (필터링 로직 미존재)
- [x] Missing input validation (no Schema for request body) -- **위반 발견**
- [x] Endpoint doing too much (should be split or use service layer) -- 현재 규모에서는 해당 없음

### Findings

```
[Schema/Validation] -- 모든 엔드포인트에서 request/response에 Pydantic Schema를 사용하지 않는다.
dict를 수동으로 생성하고, request.body를 json.loads로 직접 파싱하고 있다.
Django Ninja의 핵심인 Schema 기반 자동 검증과 직렬화를 전혀 활용하지 않는다.
```

```
[Type Hints] -- 모든 엔드포인트의 파라미터와 반환 타입에 type hint가 누락되어 있다.
id 파라미터의 타입, response 스키마가 모두 선언되지 않았다.
```

```
[Routing] -- 모든 엔드포인트가 NinjaAPI 인스턴스에 직접 등록되어 있다.
앱별 Router()를 사용하고 add_router()로 조합하는 패턴을 따라야 한다.
```

```
[Pagination] -- get_items (리스트 엔드포인트)에 페이지네이션이 없다.
데이터가 증가하면 전체 레코드를 한 번에 반환하게 되어 성능 문제가 발생한다.
```

```
[Error Handling] -- Item.objects.get()이 DoesNotExist 예외를 발생시킬 수 있으나
어떠한 에러 처리도 없다. 404를 적절히 반환하지 않는다.
```

```
[HTTP Method] -- remove_item이 GET 메서드를 사용한다.
삭제 작업은 DELETE 메서드를 사용해야 한다. GET은 안전한(safe) 메서드로,
부작용(side effect)이 있는 작업에 사용하면 안 된다.
```

```
[Input Validation] -- add_item과 edit_item에서 json.loads(request.body)로
수동 파싱하고 있다. Django Ninja Schema를 사용하면 자동으로 검증과 파싱이 수행된다.
```

```
[PATCH vs PUT] -- edit_item이 PUT 메서드를 사용하지만 부분 업데이트 로직(data.get으로
기존 값 유지)을 수행한다. 부분 업데이트는 PATCH 메서드와 PatchDict를 사용해야 한다.
```

---

## Refactoring

### 1. Schema 도입 -- dict 수동 생성 제거

```
[Before]
return [{'id': i.id, 'name': i.name, 'price': float(i.price)} for i in items]
return {'id': item.id, 'name': item.name, 'price': float(item.price)}
return {'id': item.id}

[After]
from ninja import ModelSchema, Schema
from decimal import Decimal

class ItemOut(ModelSchema):
    class Meta:
        model = Item
        fields = ['id', 'name', 'price']

class ItemIn(Schema):
    name: str
    price: Decimal

[Reason] Schema/Validation -- Django Ninja에서는 Pydantic Schema로 request/response를
정의한다. ModelSchema를 사용하면 모델 필드와 자동 동기화되며, 명시적 fields로 노출 필드를
제한한다. response 파라미터에 Schema를 지정하면 직렬화가 자동으로 수행되므로
dict 수동 생성이 불필요하다.
```

### 2. request.body 수동 파싱 제거 -- Schema 파라미터로 교체

```
[Before]
@api.post('/items')
def add_item(request):
    import json
    data = json.loads(request.body)
    item = Item.objects.create(name=data['name'], price=data['price'])
    return {'id': item.id}

@api.put('/items/{id}')
def edit_item(request, id):
    import json
    data = json.loads(request.body)
    item = Item.objects.get(id=id)
    item.name = data.get('name', item.name)
    item.price = data.get('price', item.price)
    item.save()
    return {'ok': True}

[After]
@router.post("/", response={201: ItemOut})
def create_item(request, payload: ItemIn) -> tuple[int, Item]:
    item = Item.objects.create(**payload.dict())
    return 201, item

@router.patch("/{item_id}", response=ItemOut)
def update_item(request, item_id: int, payload: PatchDict[ItemIn]) -> Item:
    item = get_object_or_404(Item, id=item_id)
    for attr, value in payload.items():
        setattr(item, attr, value)
    item.save()
    return item

[Reason] Schema/Validation + Input Parsing -- Schema 타입의 파라미터는 Django Ninja가
자동으로 JSON 파싱과 유효성 검증을 수행한다. json.loads 수동 파싱은 불필요하며,
검증 누락으로 인한 보안 위험이 있다. 부분 업데이트에는 PatchDict를 사용하여
제공된 필드만 업데이트한다. PUT을 PATCH로 변경하여 부분 업데이트 의도를 명확히 한다.
```

### 3. GET 삭제 -> DELETE 메서드로 변경

```
[Before]
@api.get('/items/{id}/remove')
def remove_item(request, id):
    Item.objects.get(id=id).delete()
    return {'ok': True}

[After]
@router.delete("/{item_id}", response={204: None})
def delete_item(request, item_id: int) -> tuple[int, None]:
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return 204, None

[Reason] Routing + Response -- 삭제는 DELETE 메서드를 사용해야 한다.
GET은 안전한 메서드로 부작용이 없어야 한다. URL도 /items/{id}/remove가 아닌
/items/{id}에 DELETE 메서드를 사용하는 것이 RESTful 설계다.
204 No Content를 반환하여 삭제 성공을 나타낸다.
```

### 4. 리스트 엔드포인트에 페이지네이션 추가

```
[Before]
@api.get('/items')
def get_items(request):
    items = Item.objects.all()
    return [{'id': i.id, 'name': i.name, 'price': float(i.price)} for i in items]

[After]
@router.get("/", response=list[ItemOut])
@paginate(PageNumberPagination)
def list_items(request) -> QuerySet[Item]:
    return Item.objects.all()

[Reason] Response/Pagination -- 리스트 엔드포인트에는 반드시 페이지네이션이 필요하다.
@paginate 데코레이터와 내장 페이지네이터를 사용하면 QuerySet 슬라이싱이 자동으로
처리된다. response에 Schema를 지정하면 QuerySet을 직접 반환할 수 있다.
```

### 5. 에러 처리 추가 -- get_object_or_404 사용

```
[Before]
item = Item.objects.get(id=id)
# DoesNotExist 예외 시 500 에러 발생

[After]
from django.shortcuts import get_object_or_404

item = get_object_or_404(Item, id=item_id)
# DoesNotExist 예외 시 404 에러 자동 반환

[Reason] Error Handling -- Item.objects.get()은 객체가 없을 때
DoesNotExist 예외를 발생시켜 500 에러가 된다. get_object_or_404를 사용하면
Django의 Http404 예외가 발생하고, Django Ninja가 이를 404 응답으로 변환한다.
```

### 6. NinjaAPI 직접 등록 -> Router 패턴으로 전환

```
[Before]
from ninja import NinjaAPI

api = NinjaAPI()

@api.get('/items')
def get_items(request):
    ...

[After]
# items/api.py
from ninja import Router

router = Router(tags=["items"])

@router.get("/", ...)
def list_items(request):
    ...

# project/api.py
from ninja import NinjaAPI
from items.api import router as items_router

api = NinjaAPI()
api.add_router("/items", items_router)

[Reason] Routing -- 앱별 Router()를 사용하고 NinjaAPI에 add_router()로 조합하는 것이
Django Ninja의 권장 프로젝트 구조다. 이를 통해 앱 간 분리가 명확해지고,
인증과 태그를 라우터 단위로 관리할 수 있다.
```

### 7. Type Hints 추가

```
[Before]
def get_item(request, id):
def add_item(request):
def edit_item(request, id):
def remove_item(request, id):

[After]
def list_items(request) -> QuerySet[Item]:
def get_item(request, item_id: int) -> Item:
def create_item(request, payload: ItemIn) -> tuple[int, Item]:
def update_item(request, item_id: int, payload: PatchDict[ItemIn]) -> Item:
def delete_item(request, item_id: int) -> tuple[int, None]:

[Reason] Type Hints -- Django Ninja에서 type hint는 필수다. 파라미터 타입은
자동 파싱과 검증에 사용되고, 반환 타입은 코드의 의도를 명확히 한다.
id -> item_id로 변경하여 Python 내장 함수 id()와의 이름 충돌을 방지한다.
```

---

## Refactored Code (전체)

```python
# items/schemas.py
from decimal import Decimal

from ninja import ModelSchema, Schema

from .models import Item


class ItemIn(Schema):
    name: str
    price: Decimal


class ItemOut(ModelSchema):
    class Meta:
        model = Item
        fields = ['id', 'name', 'price']
```

```python
# items/api.py
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from ninja import PatchDict, Router
from ninja.pagination import PageNumberPagination, paginate

from .models import Item
from .schemas import ItemIn, ItemOut

router = Router(tags=["items"])


@router.get("/", response=list[ItemOut])
@paginate(PageNumberPagination)
def list_items(request) -> QuerySet[Item]:
    return Item.objects.all()


@router.get("/{item_id}", response=ItemOut)
def get_item(request, item_id: int) -> Item:
    return get_object_or_404(Item, id=item_id)


@router.post("/", response={201: ItemOut})
def create_item(request, payload: ItemIn) -> tuple[int, Item]:
    item = Item.objects.create(**payload.dict())
    return 201, item


@router.patch("/{item_id}", response=ItemOut)
def update_item(request, item_id: int, payload: PatchDict[ItemIn]) -> Item:
    item = get_object_or_404(Item, id=item_id)
    for attr, value in payload.items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete("/{item_id}", response={204: None})
def delete_item(request, item_id: int) -> tuple[int, None]:
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return 204, None
```

```python
# project/api.py
from ninja import NinjaAPI

from items.api import router as items_router

api = NinjaAPI()
api.add_router("/items", items_router)
```
