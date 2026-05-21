# Router와 Schema

Django Ninja Router, Schema/ModelSchema, endpoint adapter 경계, request/response mapping, DRF-to-Ninja conversion을 구현할 때 이 reference를 읽는다.

## Router 경계

- Router operation은 business-rule owner가 아니라 HTTP adapter로 다룬다.
- Router code는 request parsing, auth/permission wiring, schema validation, service/usecase invocation, response mapping, error translation으로 제한한다.
- URL registration은 프로젝트의 기존 Ninja API layout과 일관되게 명시한다.
- REST contract와 맞는 method, path, response schema, status code를 operation decorator에 드러낸다.
- 여러 status response가 가능하면 문서화되지 않은 shape를 반환하지 말고 status-specific response schema를 선언한다.
- state transition, invariant, transactional write, 복잡한 ORM query construction, 외부 SDK 호출은 `implementation-django`가 소유하는 model/service/usecase code로 옮긴다.
- route에 아직 결정되지 않은 domain decision이 필요하면 멈추고 `architecture-ddd` 또는 `architecture-api`로 라우팅한다.

간단한 operation 선언 예:

```python
router = Router(tags=["orders"])


@router.post("/", response={201: OrderDetailSchema, 409: ProblemDetailSchema})
def create_order(request, payload: OrderCreateSchema):
    result = create_order_usecase(payload.to_command(), actor=request.auth)
    return 201, OrderDetailSchema.from_domain(result)
```

## Schema와 ModelSchema

- input shape에는 request schema, output shape에는 response schema를 사용한다. 모든 model field를 기본 노출하지 않는다.
- field, permission, performance 요구가 다르면 create/update/list/detail schema를 분리한다.
- schema validation은 transport/input shape에 집중한다. 재사용 domain invariant는 model/service/DB boundary에 둔다.
- API contract가 다른 public language를 쓰면 내부 model name이나 DB 구조가 새지 않게 한다.
- `ModelSchema`는 내부 필드, 관리 필드, 보안 민감 필드가 노출되지 않는지 확인한 뒤 사용한다.
- computed field와 schema resolver는 response mapping으로 제한한다. DB access, permission check, domain decision은 selector/service에 둔다.
- field 추가는 대체로 compatible로 볼 수 있지만 field 제거, rename, type change, 새 required field, status-code change, error-shape change는 versioning 없이는 breaking change로 본다.

`ModelSchema` 사용 예는 반드시 `fields`를 명시해 검토 가능한 API surface를 만든다.

```python
class OrderListSchema(ModelSchema):
    class Meta:
        model = Order
        fields = ["id", "status", "total_amount", "created_at"]
```

## DRF-to-Ninja conversion

- DRF `ViewSet`/`APIView` routing은 명시적인 Django Ninja Router operation으로 바꾼다.
- DRF `Serializer`/`ModelSerializer` 책임은 Django Ninja request/response schema와 필요한 service-layer validation으로 나눈다.
- public API contract를 보존하면서 DRF-specific pagination, permission, exception behavior를 프로젝트의 Django Ninja equivalent로 교체한다.
- 기존/신규 endpoint URL, method, status code, response field, error shape, auth behavior, pagination, OpenAPI schema를 비교한다.
- DRF reference는 legacy source 이해에만 사용한다. DRF를 greenfield 표준으로 유지하지 않는다.

## Endpoint review 질문

- HTTP contract가 `architecture-api`에서 이미 결정되었는가?
- Router가 기대한 API namespace/version에 등록되었는가?
- HTTP 없이 business behavior를 테스트할 수 있을 만큼 Router가 얇은가?
- request/response schema가 public API field로 의도적으로 제한되었는가?
- domain/application error가 Problem Details로 일관되게 mapping되는가?
- OpenAPI와 compatibility 영향이 구현 메모나 검증에 드러나는가?
