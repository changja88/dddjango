# Django Ninja Code Review

## Review Checklist

- [x] DRF patterns used instead of Django Ninja -- 해당 없음
- [x] Missing type hints on endpoint parameters or return types -- **위반 발견**
- [x] Schema exposing all model fields without explicit selection -- **위반 발견 (Schema 미사용)**
- [x] Missing authentication on endpoints that require it -- **위반 발견**
- [x] No pagination on list endpoints -- **위반 발견**
- [x] No error handling or non-standard error format -- **위반 발견**
- [x] Sync view where async would improve performance -- 경미 (아래 참고)
- [x] FilterSchema not used for complex filtering logic -- 해당 없음 (필터링 로직 없음)
- [x] Missing input validation (no Schema for request body) -- **위반 발견**
- [x] Endpoint doing too much (should be split or use service layer) -- 해당 없음

---

## Findings

### 1. Missing Input Validation -- Schema 미사용으로 요청 본문 유효성 검증 없음

```
[Convention] Schema-Based Validation -- Django Ninja는 모든 요청/응답에 Pydantic Schema를
사용하여 자동 유효성 검증과 직렬화를 수행해야 한다. 현재 코드는 json.loads(request.body)로
요청 본문을 수동 파싱하고 있으며, 이는 Django Ninja의 핵심 기능을 완전히 무시하는 것이다.
타입 검증, 필수 필드 확인, OpenAPI 문서 자동 생성이 모두 누락된다.
```

`create_product`와 `update_product`에서 `import json; json.loads(request.body)` 패턴을 사용하고 있다. Django Ninja에서는 Schema 타입의 파라미터를 선언하면 프레임워크가 자동으로 JSON 파싱, 타입 변환, 유효성 검증을 수행한다. 수동 파싱은 불필요할 뿐 아니라, 잘못된 데이터가 검증 없이 모델에 직접 전달되어 보안 위험이 된다.

관련 대상: `create_product`, `update_product`

---

### 2. Missing Response Schema -- 응답에 response 스키마가 지정되지 않음

```
[Convention] Response Schema -- 모든 엔드포인트는 response= 파라미터로 응답 스키마를 명시해야
한다. 이를 통해 응답 데이터의 자동 직렬화, 불필요한 필드 제외, OpenAPI 문서 자동 생성이
이루어진다. 현재 모든 엔드포인트가 dict를 수동으로 구성하여 반환하고 있다.
```

`list_products`에서 수동 리스트 컴프리헨션으로 dict를 구성하고 있으며, `create_product`와 `update_product`도 dict를 수동 반환한다. `response=List[ProductOut]` 같은 형식으로 응답 스키마를 지정하면 QuerySet을 직접 반환할 수 있고, price 필드의 `str()` 변환 같은 수동 처리도 불필요해진다.

관련 대상: `list_products`, `create_product`, `update_product`, `delete_product`

---

### 3. Missing Type Hints -- 엔드포인트 파라미터와 반환 타입에 타입 힌트 누락

```
[Convention] Type Hints -- Django Ninja 컨벤션에서 타입 힌트는 필수다. 모든 엔드포인트
파라미터와 반환 타입에 타입 어노테이션이 있어야 한다. 타입 힌트는 자동 파싱, 유효성 검증,
OpenAPI 문서 생성의 기반이다.
```

- `product_id: int` 타입 힌트가 `update_product`와 `delete_product`의 path 파라미터에 누락되어 있다. 타입 힌트 없이는 Django Ninja가 경로 파라미터의 타입 변환과 검증을 수행할 수 없다.
- 반환 타입이 어떤 엔드포인트에도 선언되어 있지 않다.

관련 대상: 모든 엔드포인트

---

### 4. No Pagination on List Endpoint -- 리스트 엔드포인트에 페이지네이션 없음

```
[Convention] @paginate Decorator -- 컬렉션을 반환하는 리스트 엔드포인트에는 반드시
@paginate 데코레이터를 적용해야 한다. Product.objects.all()은 테이블의 모든 레코드를
한 번에 반환하므로, 데이터가 증가하면 응답 시간과 메모리 사용량이 비례하여 증가한다.
LimitOffsetPagination, PageNumberPagination, CursorPagination 중 적절한 것을 사용한다.
```

`list_products`가 `Product.objects.all()`의 전체 결과를 반환하고 있다.

---

### 5. No Authentication -- 인증이 어떤 엔드포인트에도 설정되지 않음

```
[Convention] Authentication -- 데이터를 변경하는 엔드포인트(POST, PUT, DELETE)에는
반드시 인증이 필요하다. Django Ninja의 내장 인증 클래스(HttpBearer, APIKeyHeader,
SessionAuth 등)를 글로벌, 라우터, 또는 개별 엔드포인트 수준에서 적용해야 한다.
현재 NinjaAPI와 Router 모두 auth 설정이 없으며, 모든 엔드포인트가 인증 없이 접근 가능하다.
```

최소한 쓰기 작업(create, update, delete)에는 인증이 필요하다. 읽기 전용 엔드포인트가 공개인 경우에도, Router 수준에서 인증을 설정하고 리스트 엔드포인트만 `auth=None`으로 면제하는 것이 더 안전한 패턴이다.

---

### 6. No Error Handling -- 에러 처리 없이 예외가 그대로 전파됨

```
[Convention] Error Handling -- Product.objects.get()은 객체가 없으면 DoesNotExist 예외를
발생시킨다. Django Ninja에서는 HttpError를 사용하거나 @api.exception_handler()를 등록하여
RFC 9457 Problem Details 형식의 에러 응답을 반환해야 한다. 현재 코드는 예외 처리가 전혀
없어서 존재하지 않는 product_id 요청 시 500 에러가 반환된다.
```

`update_product`와 `delete_product`에서 `Product.objects.get(id=product_id)`가 실패할 경우에 대한 처리가 없다. `get_object_or_404(Product, id=product_id)` 또는 try/except와 `HttpError(404, ...)` 조합을 사용해야 한다.

---

### 7. PUT Used Where PATCH Is More Appropriate -- 부분 업데이트에 PUT 사용

```
[Convention] PatchDict -- 부분 업데이트(일부 필드만 변경)에는 PUT이 아닌 PATCH 메서드를
사용하고, PatchDict[Schema]를 파라미터로 받아야 한다. 현재 update_product는 PUT으로
선언되었으나 data.get()으로 부분 업데이트를 수행하고 있어 HTTP 의미론과 일치하지 않는다.
PUT은 리소스의 전체 교체를 의미한다.
```

`update_product`의 `data.get('name', product.name)` 패턴은 부분 업데이트 의미이므로 PATCH + PatchDict가 적합하다. 전체 교체(PUT)를 의도한다면 모든 필드가 필수인 Schema를 사용해야 한다.

---

### 8. delete_product Returns Non-Standard Response -- 삭제 응답이 비표준

```
[Convention] Empty Response (204 None) -- 삭제 작업은 response={204: None}을 사용하여
빈 응답을 반환하는 것이 REST 표준이다. {'success': True}는 비표준 응답 형식이다.
```

---

## Summary

이 코드는 Django Ninja의 핵심 기능을 거의 활용하지 않고 있다. 가장 심각한 문제는 **Schema를 사용하지 않고 `json.loads(request.body)`로 수동 파싱**하는 것이며, 이는 Django Ninja를 사용하는 이유 자체를 부정한다. Schema 도입을 통해 유효성 검증, 응답 직렬화, OpenAPI 문서 생성이 자동으로 이루어지므로, 이 부분을 최우선으로 개선해야 한다. 그 다음으로 인증, 페이지네이션, 에러 처리를 순서대로 적용해야 한다.
