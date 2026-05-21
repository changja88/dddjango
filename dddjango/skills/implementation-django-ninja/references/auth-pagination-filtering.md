# Auth, Pagination, Filtering, Versioning

Django Ninja authentication/authorization wiring, list endpoint, filtering, sorting, pagination, 이미 정해진 rate limiting/versioning strategy의 adapter 연결을 구현할 때 이 reference를 읽는다.

## Authentication과 Authorization

- Authentication은 caller가 누구인지 답하고, authorization은 그 caller가 action을 수행할 수 있는지 답한다.
- Django Ninja auth는 API, Router, operation level에 연결할 수 있다. 프로젝트의 기존 scope와 override convention을 따른다.
- authentication이 필요하거나 실패하면 `401`, authenticated caller에게 permission이 없으면 `403`을 반환한다.
- API credential은 `Authorization` header를 우선한다. secret을 query parameter에 넣지 않는다.
- 명시적인 local development 환경이 아니면 API traffic은 HTTPS를 전제로 한다.
- adapter-level auth check는 API boundary에 둘 수 있지만, 여러 entry point에서 재사용되는 object/action authorization rule은 service나 domain policy로 옮긴다.
- object-level permission check는 endpoint가 필요한 것보다 많은 데이터를 로드하지 않게 selector/service의 query shape와 맞춘다.

Router-level auth 연결 예:

```python
orders_router = Router(auth=TokenAuth())
```

## Filtering, Sorting, Search

- filtering과 sorting parameter는 public API contract의 일부다.
- validation과 OpenAPI clarity를 높이면 Django Ninja `FilterSchema` 또는 프로젝트의 기존 filtering pattern을 사용한다.
- accepted filter를 명확히 드러낼 때는 typed `Query` binding을 사용한다.
- filter, sort key, sparse fieldset, search term은 query parameter를 우선한다.
- public parameter name에 내부 DB table name이나 우연한 ORM 구조를 반영하지 않는다.
- 허용 filter와 sort field를 검증한다. user-controlled ORM field name을 그대로 받지 않는다.
- reusable read logic과 N+1 optimization은 `implementation-django`의 selector나 QuerySet method로 위임한다.

`FilterSchema`와 `Query` binding 예:

```python
class OrderFilter(FilterSchema):
    status: str | None = None
    created_after: datetime | None = None


@orders_router.get("/", response=list[OrderListSchema])
def list_orders(request, filters: Query[OrderFilter]):
    return filters.filter(order_selector.visible_to(request.auth))
```

## Pagination

- pagination strategy는 API contract에서 고른다. 작은 admin-like collection은 offset, 큰 collection/실시간 목록/consistency-sensitive 목록은 cursor/keyset을 우선 검토한다.
- Django Ninja pagination decorator, custom pagination class, `RouterPaginated`는 request/response shape가 API contract와 맞을 때만 사용한다.
- page size 상한을 강제한다.
- client가 다음 page를 가져올 수 있도록 `has_more`, `next_cursor` 또는 프로젝트 contract의 metadata를 반환한다.
- cursor/keyset pagination은 보통 timestamp와 id를 함께 쓰는 stable indexed ordering을 사용한다.
- pagination behavior가 미정이면 구현 전에 `architecture-api`로 라우팅한다.

## Rate Limiting

- 프로젝트에 rate-limit mechanism이 있으면 비싼 authentication, database, external work 전에 rate limit을 적용한다.
- 프로젝트가 공개하는 경우 `429`와 `Retry-After`, limit/remaining/reset 같은 rate-limit header를 반환한다.
- public client가 의존하는 rate-limit policy는 API documentation/OpenAPI note에 드러나게 한다.
- rate-limit policy, quota unit, response header contract가 미정이면 `architecture-api`로 넘긴 뒤 Django Ninja wiring만 구현한다.

## Versioning과 Compatibility

- 프로젝트의 versioning strategy를 따른다. compatibility 이유 없이 URL, header, query strategy를 섞지 않는다.
- 기존 client에는 additive change를 우선한다.
- breaking change에는 deprecation과 migration window를 둔다.
- DRF에서 전환할 때는 version behavior를 비교하고 client에 영향을 줄 수 있는 변경을 문서화한다.
- URL/header/query versioning strategy나 deprecation policy가 미정이면 `architecture-api`로 넘긴다.
