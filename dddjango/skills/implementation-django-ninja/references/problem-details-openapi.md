# Problem Details, Idempotency, OpenAPI

API error response, status code, idempotency behavior, compatibility, OpenAPI 영향을 구현할 때 이 reference를 읽는다.

## Status Code

- body를 반환하는 read/update 성공에는 `200`을 사용한다.
- resource 생성에는 `201`을 사용하고 contract가 요구하면 새 resource location을 포함한다.
- asynchronous work 접수에는 `202`를 사용한다.
- body 없는 delete/update 성공에는 `204`를 사용한다.
- malformed request는 `400`, authentication failure는 `401`, authorization failure는 `403`, missing 또는 intentionally hidden resource는 `404`, conflict는 `409`, contract가 쓰는 semantically invalid input은 `422`, rate limit은 `429`를 사용한다.
- status-code change는 기존 client와 compatible하게 유지하거나 versioning한다.

## Problem Details

- Problem Details error의 response media type은 `application/problem+json`을 사용한다.
- legacy compatibility contract가 명시적으로 다르게 요구하지 않는 한 API error에는 RFC 9457 Problem Details를 사용한다.
- `status`는 HTTP response status와 맞춘다.
- `title`은 reusable problem type summary, `detail`은 specific occurrence 설명으로 쓴다.
- stable `type` URI를 사용하고 안정된 type이 없으면 `about:blank`를 사용한다.
- specific occurrence에 유용한 request/problem identifier URI가 있으면 `instance`를 포함한다.
- extension field는 문서화되어 있고 client가 무시해도 안전할 때만 추가한다.
- Django Ninja exception handler 또는 `NinjaAPI` subclass를 사용해 validation, application, domain error를 프로젝트의 Problem Details contract로 mapping한다.
- Django Ninja default validation error status나 body shape가 API contract와 다르면 framework-default error를 public client에 노출하지 말고 customize한다.

Exception handler 예:

```python
@api.exception_handler(OrderConflict)
def order_conflict(request, exc):
    return api.create_response(
        request,
        {
            "type": "https://api.example.test/problems/order-conflict",
            "title": "Order conflict",
            "status": 409,
            "detail": str(exc),
        },
        status=409,
        content_type="application/problem+json",
    )
```

## Idempotency-Key

- 주문 또는 결제 생성처럼 duplicate-prone POST operation에는 `Idempotency-Key`를 요구하거나 지원한다.
- service transaction design에 따라 첫 request result를 DB 또는 Redis 같은 durable storage에 저장한다.
- 같은 key와 equivalent request가 반복되면 저장된 response를 반환한다.
- 생성된 resource가 나중에 상태 변경될 수 있으면 현재 resource id만 저장해 재조회하지 말고 immutable first-result DTO/response snapshot을 저장한다.
- 같은 key와 다른 payload의 conflict behavior를 정의한다.
- key TTL, storage owner, transaction boundary, concurrency behavior는 `implementation-django`, `architecture-db`와 맞춘다.
- mutable current state 때문에 retry response가 original response와 달라질 수 있으면 later state change 이후 replay를 테스트한다.

## OpenAPI

- Router와 Schema 변경이 의도한 OpenAPI request/response shape를 만드는지 확인한다.
- name, required field, nullable field, enum value, status response, error schema, auth requirement, pagination shape, tag를 확인한다.
- 프로젝트가 공개하는 경우 documented error response에 Problem Details schema와 security requirement를 포함한다.
- DRF migration에서는 가능하면 old/new generated schema를 비교하고 client-visible difference를 문서화한다.
- OpenAPI generation 또는 schema diff를 실제 실행하지 않았으면 실행했다고 주장하지 않는다.
