# Django Ninja Code Review

## 1. Django Ninja의 핵심 기능 미사용: Schema 미적용

Django Ninja를 사용하는 가장 큰 이유는 Pydantic 기반의 `Schema`를 통해 요청/응답의 자동 검증과 직렬화를 얻는 것인데, 이 코드는 그 기능을 전혀 활용하지 않고 있다.

**현재 문제:**
- `json.loads(request.body)`로 직접 파싱하고 있다. 이는 Django Ninja가 아닌 순수 Django 방식이다.
- 입력 데이터에 대한 유효성 검증이 전혀 없다.
- 응답 형식이 딕셔너리 수동 조립이라 일관성이 보장되지 않는다.

**개선안:**
```python
from ninja import Schema
from decimal import Decimal
from typing import Optional

class ProductIn(Schema):
    name: str
    price: Decimal
    category_id: Optional[int] = None

class ProductOut(Schema):
    id: int
    name: str
    price: Decimal

class ProductUpdate(Schema):
    name: Optional[str] = None
    price: Optional[Decimal] = None

@router.post('/products', response=ProductOut)
def create_product(request, payload: ProductIn):
    product = Product.objects.create(**payload.dict())
    return product

@router.put('/products/{product_id}', response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdate):
    product = get_object_or_404(Product, id=product_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(product, attr, value)
    product.save()
    return product
```

## 2. 함수 내부 import

`create_product`와 `update_product` 내부에서 `import json`을 하고 있다. Schema를 도입하면 이 import 자체가 불필요해지지만, 일반적으로도 함수 내부 import는 가독성을 떨어뜨리므로 모듈 상단에 배치해야 한다.

## 3. 예외 처리 부재

**`Product.objects.get(id=product_id)` 호출 시 예외 처리가 없다.**

존재하지 않는 `product_id`로 요청하면 `Product.DoesNotExist` 예외가 발생하여 500 에러가 반환된다. 클라이언트에게는 404가 적절하다.

**개선안:**
```python
from django.shortcuts import get_object_or_404

@router.put('/products/{product_id}', response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdate):
    product = get_object_or_404(Product, id=product_id)
    ...

@router.delete('/products/{product_id}')
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {'success': True}
```

## 4. `list_products`의 N+1 및 직렬화 문제

- `Product.objects.all()`은 전체 레코드를 메모리에 로드한다. 페이지네이션이 없으면 데이터가 많을 때 심각한 성능 문제가 발생한다.
- `price`를 `str()`로 변환하고 있는데, 응답 Schema에서 `Decimal` 타입으로 선언하면 Django Ninja가 자동 처리한다.
- 다른 엔드포인트의 응답에는 `price`가 빠져 있어 일관성이 없다.

**개선안:**
```python
from ninja import Query
from typing import List

class ProductFilter(Schema):
    limit: int = 20
    offset: int = 0

@router.get('/products', response=List[ProductOut])
def list_products(request, filters: ProductFilter = Query(...)):
    qs = Product.objects.all()[filters.offset:filters.offset + filters.limit]
    return list(qs)
```

## 5. `product_id` 타입 힌트 누락

`update_product`와 `delete_product`의 `product_id` 파라미터에 타입 힌트가 없다. Django Ninja는 타입 힌트를 기반으로 경로 파라미터의 타입 변환과 검증을 수행하므로, `product_id: int`로 명시해야 한다.

## 6. `create_product`의 키 접근 방식

```python
data['name']       # KeyError 발생 가능
data['price']      # KeyError 발생 가능
data.get('category_id')  # None 반환
```

필수 필드와 선택 필드의 접근 방식이 혼재되어 있고, 필수 필드 누락 시 `KeyError`로 500 에러가 발생한다. Schema를 사용하면 이 문제가 자동으로 해결된다.

## 7. `delete_product` 응답

DELETE 요청의 경우 `204 No Content`를 반환하는 것이 REST 관례에 맞다.

```python
from ninja import Router

@router.delete('/products/{product_id}', response={204: None})
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

## 8. `Product` 모델 import 누락

코드에서 `Product`를 사용하고 있지만 import 구문이 없다. 실행 시 `NameError`가 발생한다.

## 요약

| 항목 | 심각도 | 설명 |
|------|--------|------|
| Schema 미사용 | 높음 | Django Ninja의 핵심 가치를 활용하지 않고 있음 |
| 예외 처리 부재 | 높음 | 존재하지 않는 리소스 접근 시 500 에러 발생 |
| 입력 검증 없음 | 높음 | 잘못된 데이터가 DB에 직접 들어갈 수 있음 |
| 페이지네이션 없음 | 중간 | 대량 데이터 시 성능 문제 |
| 타입 힌트 누락 | 중간 | 경로 파라미터 자동 검증 미작동 |
| 함수 내부 import | 낮음 | 코드 스타일 문제 |
| Product import 누락 | 높음 | 실행 불가 |
| 응답 일관성 | 중간 | 엔드포인트별 응답 필드가 다름 |
