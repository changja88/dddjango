# Django Ninja API 구현 종합 가이드

## P1 Source Sufficiency

| field | value |
|---|---|
| purpose | Django Ninja API adapter implementation: Router, Schema, auth, filtering/sorting, pagination, Problem Details mapping, OpenAPI generation impact, TestClient checks, and DRF-to-Ninja migration. |
| use when | Router/Schema/API adapter implementation is the main work and REST contract decisions are already stable or handed to `architecture-api`. |
| exclude/handoff | Do not use for domain rules, DB locking/idempotency storage, Django ORM/service internals, or pytest fixture mechanics beyond API adapter tests. |
| core criteria | Keep Router thin; use explicit request/response schemas; protect public fields; map errors to contract; check generated OpenAPI when contract changes; keep greenfield DRF requests on a Django Ninja target unless legacy/migration context is explicit. |
| source priority | 1 Django Ninja official docs and OpenAPI contract boundary inherited from `architecture-api`; 2 primary dddjango Django/API/test references; 3 reputable migration/comparison guidance only as secondary; 4 unsupported DRF habit is not source. |
| P1 classification | sufficient |

> 이 문서는 Django Ninja로 REST API adapter를 구현할 때의 기준을 정리한다.
> REST 계약 자체는 `workspace/reference/architecture-api/reference/final.md`,
> Django ORM, service, transaction, migration은
> `workspace/reference/implementation-django/reference/final.md`,
> pytest fixture와 test-double 세부 구현은
> `workspace/reference/implementation-test/reference/final.md`를 기준으로 한다.
>
> Django Ninja는 greenfield API 구현의 기본 목표다. DRF 자료는 legacy review,
> compatibility 비교, DRF-to-Ninja migration 때만 보조 근거로 사용한다.

---

## 목차

1. [범위와 책임 경계](#1-범위와-책임-경계)
2. [Router와 endpoint operation](#2-router와-endpoint-operation)
3. [Schema와 ModelSchema](#3-schema와-modelschema)
4. [인증과 인가](#4-인증과-인가)
5. [Filtering, sorting, pagination](#5-filtering-sorting-pagination)
6. [상태 코드와 Problem Details](#6-상태-코드와-problem-details)
7. [Idempotency-Key](#7-idempotency-key)
8. [OpenAPI](#8-openapi)
9. [TestClient와 검증](#9-testclient와-검증)
10. [DRF-to-Ninja migration](#10-drf-to-ninja-migration)
11. [라우팅 기준](#11-라우팅-기준)
12. [참고 문헌](#12-참고-문헌)

---

## 1. 범위와 책임 경계

### 1.1 Django Ninja skill의 역할

Django Ninja skill은 HTTP 요청과 응답을 Django application/service/usecase로
연결하는 adapter 구현을 다룬다. 핵심 책임은 다음이다.

- Router 등록과 operation 선언
- path/query/header/body 파라미터를 명시적 schema로 받기
- authentication/authorization 연결
- service/usecase 호출
- domain/application error를 API error contract로 변환
- response schema와 status code mapping
- OpenAPI에 드러나는 계약 변화 확인
- Django Ninja `TestClient` 기반 HTTP contract 검증 기준 제시

### 1.2 다른 source reference로 위임할 책임

- REST resource, URL, HTTP method, status code, header, content negotiation,
  pagination strategy, versioning, rate limit, idempotency contract는
  `architecture-api`가 결정한다.
- aggregate, state transition, invariant, policy, usecase boundary, 구조 패턴
  (repository/UoW/핵사고날/CQRS/outbox/ACL) 선택은 `architecture-ddd`가 결정한다.
- ORM query, selector, service, transaction, migration, cache, security
  implementation은 `implementation-django`가 담당한다.
- pytest fixture, factory, mock/test-double, concurrency test mechanics는
  `implementation-test`가 담당한다.

### 1.3 Router thinness 원칙

Router operation은 HTTP adapter다. 다음은 Router 안에 둘 수 있다.

- request schema validation과 parameter binding
- auth/permission hook 연결
- service/usecase 호출
- API-facing DTO 또는 schema로 response mapping
- known application/domain exception을 Problem Details로 변환

다음은 Router, Schema, FilterSchema에 두지 않는다.

- 핵심 business rule과 state transition
- transaction ownership
- 복잡한 ORM query construction과 N+1 최적화
- 외부 SDK 호출 orchestration
- 여러 entry point에서 재사용해야 하는 object/action authorization policy

---

## 2. Router와 endpoint operation

### 2.1 Router 등록

Django Ninja는 `NinjaAPI`와 `Router`를 통해 path operation을 등록한다.
프로젝트의 API namespace와 versioning 방식이 이미 있으면 그 방식을 따른다.
새로운 Router를 추가할 때는 다음을 확인한다.

- API root와 version prefix가 기존 convention과 일치하는가
- operation path가 REST resource 계약과 일치하는가
- operation method가 resource action의 safe/idempotent 의미와 맞는가
- router-level auth와 operation-level auth override가 의도대로 적용되는가
- tag, summary, response schema가 OpenAPI에 필요한 만큼 드러나는가

### 2.2 Operation 선언

Django Ninja operation은 decorator의 HTTP method, path, response 선언,
operation 함수의 typed parameters로 API contract를 만든다. 여러 status code가
가능한 경우 `response={status: Schema}` 형태로 성공/오류 schema를 분리한다.

Operation 구현 기준:

- path parameter, query parameter, request body를 명확히 구분한다.
- request body와 response body는 별도 schema를 사용한다.
- create operation은 성공 시 `201`과 필요하면 `Location` header 계약을 맞춘다.
- delete 또는 no-body update는 `204`를 사용하고 body를 반환하지 않는다.
- async operation에서 ORM을 직접 호출하지 않도록 Django async ORM 제약을 확인한다.

```python
from ninja import Router, Schema

router = Router()


class OrderIn(Schema):        # request body
    product_id: int
    quantity: int


class OrderOut(Schema):       # response body -- public field만 노출
    id: int
    status: str


class ErrorOut(Schema):
    detail: str


# 성공/오류 schema를 status code별로 분리한다
@router.post("/orders", response={201: OrderOut, 422: ErrorOut})
def create_order(request, payload: OrderIn):
    order = place_order(product_id=payload.product_id, quantity=payload.quantity)  # service 호출
    return 201, OrderOut(id=order.id, status=order.status)
```

---

## 3. Schema와 ModelSchema

### 3.1 Request/response schema 분리

Django Ninja `Schema`는 Pydantic 기반 request/response contract다. 하나의
model을 그대로 노출하는 방식보다, API contract에 맞는 create/update/list/detail
schema를 분리한다.

- request schema는 입력 형식과 transport-level validation에 집중한다.
- response schema는 public field, type, nullable 여부, enum 값을 명시한다.
- domain invariant는 service/model/DB boundary에서 보장한다.
- field 제거, rename, type change, 새 required field, status-code/error-shape
  change는 breaking change로 보고 version/deprecation을 검토한다.

### 3.2 ModelSchema 사용 기준

`ModelSchema`는 모델 필드를 API schema로 빠르게 매핑할 때 유용하지만, 다음을
확인한 뒤 사용한다.

- 내부 필드, 관리 필드, 보안 민감 필드가 노출되지 않는가
- public API 용어와 DB/model 용어가 다를 때 무리하게 모델명을 노출하지 않는가
- list/detail/create/update의 field set이 실제로 같은가
- permission에 따라 field visibility가 달라지는 경우 별도 response mapping이
  필요한가

```python
from ninja import ModelSchema
from myapp.models import Article


# 노출할 필드를 명시한다 -- 내부/관리/보안 민감 필드는 넣지 않는다
class ArticleOut(ModelSchema):
    class Meta:
        model = Article
        fields = ["id", "title", "published_at"]
```

### 3.3 Resolver와 computed field

Response schema의 computed field나 resolver는 표현 mapping에 한정한다. DB 조회,
권한 판단, domain decision이 필요한 계산은 selector/service에서 끝낸 값을 받아
mapping한다.

---

## 4. 인증과 인가

### 4.1 Authentication

Authentication은 caller identity를 판정한다. Django Ninja는 API, Router,
operation 수준에 auth를 연결할 수 있다. 프로젝트의 기존 auth mechanism이 있으면
그 adapter를 우선한다.

기준:

- API credential은 `Authorization` header 같은 header 기반 전달을 우선한다.
- secret을 query parameter에 넣지 않는다.
- 인증 실패 또는 인증 필요는 `401`로 응답한다.
- local development를 제외한 API traffic은 HTTPS를 전제로 한다.

### 4.2 Authorization

Authorization은 authenticated caller가 action/object에 접근할 수 있는지
판정한다.

- 단일 endpoint에만 해당하는 단순 gate는 adapter에서 연결할 수 있다.
- 여러 entry point에서 재사용되는 object/action rule은 service/domain policy로
  옮긴다.
- authenticated caller가 권한이 없으면 `403`으로 응답한다.
- 존재를 숨겨야 하는 resource는 API contract에 따라 `404`를 사용할 수 있다.
- object-level permission은 필요한 query shape, selector, prefetch/select_related
  기준과 함께 검토한다.

---

## 5. Filtering, sorting, pagination

### 5.1 Filtering과 sorting

Filtering, sorting, search parameter는 public API contract다. Django Ninja
`FilterSchema`와 `Query[...]` binding은 query parameter validation과 OpenAPI
가독성을 높일 수 있다.

기준:

- 허용 filter와 sort key를 명시한다.
- user-controlled ORM field name을 그대로 받지 않는다.
- DB table/model 내부 구조가 public parameter에 새지 않게 한다.
- reusable read logic, query optimization, N+1 방지는 `implementation-django`의
  selector/QuerySet method로 위임한다.
- 검색, sparse fieldset, 복합 filter는 `architecture-api`의 계약이 먼저 있어야 한다.

```python
from typing import Optional
from ninja import FilterSchema, Query


class OrderFilter(FilterSchema):
    status: Optional[str] = None       # 허용 filter key만 명시한다


@router.get("/orders", response=list[OrderOut])
def list_orders(request, filters: Query[OrderFilter]):
    return select_orders(filters=filters)   # 실제 query는 selector/QuerySet로 위임
```

### 5.2 Pagination

Pagination strategy는 API contract가 결정한다.

- 작은 admin-like collection은 offset pagination이 단순하다.
- 큰 collection, 실시간 목록, consistency-sensitive 목록은 cursor/keyset을
  우선 검토한다.
- page size 상한을 둔다.
- cursor/keyset은 stable indexed ordering을 사용한다. 일반적으로 timestamp와 id를
  함께 쓴다.
- response에는 다음 페이지를 요청할 수 있는 metadata를 포함한다.

Django Ninja의 pagination decorator나 `RouterPaginated` 같은 framework 기능을
사용할 수 있지만, strategy와 response shape는 프로젝트 계약과 맞아야 한다.

```python
from ninja.pagination import paginate, PageNumberPagination


@router.get("/orders", response=list[OrderOut])
@paginate(PageNumberPagination)        # page size 상한 등은 NINJA_PAGINATION_* 설정으로
def list_orders(request):
    return select_orders()             # paginate가 queryset을 잘라 페이지를 만든다
```

---

## 6. 상태 코드와 Problem Details

### 6.1 Status code mapping

상태 코드의 의미는 `architecture-api` 기준을 따른다.

- `200`: body를 반환하는 read/update 성공
- `201`: resource 생성
- `202`: 비동기 작업 접수
- `204`: body 없는 delete/update 성공
- `400`: malformed request
- `401`: authentication 실패 또는 필요
- `403`: authorization 부족
- `404`: resource 없음 또는 존재 숨김
- `409`: conflict
- `422`: semantically invalid input 또는 framework validation error 계약
- `429`: rate limit

Django Ninja validation error의 default status가 프로젝트 error contract와 다르면
exception handler 또는 API subclass로 contract를 맞춘다.

### 6.2 RFC 9457 Problem Details

API error는 legacy compatibility contract가 명시적으로 다른 형식을 요구하지 않는
한 RFC 9457 Problem Details를 사용한다.

필수 기준:

- response media type은 `application/problem+json`을 사용한다.
- `status` field는 HTTP status와 일치한다.
- `type`은 stable URI를 쓰고, 없으면 `about:blank`를 사용한다.
- `title`은 problem type 요약이며 같은 type이면 안정적으로 유지한다.
- `detail`은 특정 발생에 대한 설명이다.
- `instance`는 request/problem id 같은 식별자가 있을 때 포함한다.
- extension field는 문서화되어 있고 client가 무시해도 안전해야 한다.

Django Ninja에서는 `api.exception_handler(...)` 또는 `NinjaAPI` subclass로
application/domain exception과 validation error를 Problem Details로 변환한다.

```python
from ninja import NinjaAPI
from django.http import JsonResponse

api = NinjaAPI()


# application/domain 예외를 RFC 9457 형식으로 변환한다
@api.exception_handler(OrderConflict)
def on_order_conflict(request, exc):
    return JsonResponse(
        {
            "type": "about:blank",
            "title": "Order conflict",
            "status": 409,
            "detail": str(exc),
        },
        status=409,
        content_type="application/problem+json",
    )
```

---

## 7. Idempotency-Key

Duplicate-prone POST, 특히 order/payment 생성은 `Idempotency-Key` 정책을
API adapter만으로 처리하지 않는다. contract, durable storage, transaction,
concurrency behavior가 함께 결정되어야 한다.

기준:

- key 요구 여부, TTL, scope, payload mismatch behavior를 API contract에 둔다.
- 첫 요청 결과를 DB 또는 Redis 등 durable storage에 저장한다.
- 같은 key와 같은 payload의 재시도는 저장된 첫 응답을 반환한다.
- 생성된 resource가 나중에 변할 수 있으면 현재 resource를 재조회하지 말고 첫 응답
  snapshot 또는 immutable DTO를 저장한다.
- 같은 key와 다른 payload는 conflict로 처리한다.
- DB unique constraint, lock, transaction boundary는 `architecture-db`와
  `implementation-django`가 소유한다.

---

## 8. OpenAPI

Django Ninja는 typed operation과 schema에서 OpenAPI 문서를 생성한다. 구현 변경은
runtime behavior뿐 아니라 generated schema의 client-visible contract를 바꿀 수 있다.

확인 항목:

- path, method, tag, operation id, summary
- request body, query/path/header parameter
- required/optional/nullable field
- enum, format, default
- status별 response schema
- Problem Details error schema
- auth/security requirement
- pagination/filtering parameter와 response metadata
- deprecation/versioning note

OpenAPI generation 또는 schema diff를 실행하지 않았다면 실행했다고 말하지 않는다.
DRF-to-Ninja migration에서는 가능한 경우 기존 DRF schema와 Django Ninja schema를
비교하고 차이를 기록한다.

---

## 9. TestClient와 검증

### 9.1 TestClient 사용 범위

Django Ninja `TestClient`는 Router/API operation을 HTTP adapter 수준에서 검증하는
도구다. Business rule은 domain/service test로 더 직접 검증하고, API test는 다음을
중점으로 둔다.

- request schema validation
- status code와 header
- response schema field/type
- auth/permission wiring
- Problem Details error shape
- pagination/filtering/sorting parameter
- idempotency replay와 conflict
- DRF-to-Ninja compatibility

```python
from ninja.testing import TestClient


def test_create_order_returns_201():
    client = TestClient(router)
    res = client.post("/orders", json={"product_id": 7, "quantity": 2})
    assert res.status_code == 201
    assert res.json()["status"] == "created"


def test_invalid_quantity_returns_422():
    client = TestClient(router)
    res = client.post("/orders", json={"product_id": 7, "quantity": 0})
    assert res.status_code == 422
```

### 9.2 검증 보고 기준

검증 보고에는 실제 실행한 명령이나 검토한 artifact만 쓴다.

- focused pytest path
- Django Ninja `TestClient` test run
- OpenAPI generation command
- schema comparison artifact
- compatibility checklist

실행하지 않은 TestClient, pytest, OpenAPI, compatibility check는 `Not run`으로
분명히 표시한다. Skill/reference loading command는 사용자 작업 검증으로 보고하지
않는다.

---

## 10. DRF-to-Ninja migration

DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`, `rest_framework` 요청이
greenfield work라면 Django Ninja 구현으로 전환한다. Legacy code review 또는 migration
작업이라면 DRF behavior를 source behavior로 읽고 Django Ninja target contract와 비교한다.

Migration checklist:

- URL, path parameter, method
- status code와 response body 존재 여부
- request/response field 이름, type, nullable, required
- validation error shape
- auth/permission behavior
- pagination, filtering, sorting
- throttling/rate limiting
- exception mapping과 Problem Details compatibility
- OpenAPI schema
- client deprecation/migration note

DRF-specific abstraction을 새 greenfield 표준으로 유지하지 않는다. 필요한 behavior는
Django Ninja Router/Schema, service validation, exception handler, TestClient 검증으로
옮긴다.

---

## 11. 라우팅 기준

- REST contract가 undecided이면 `architecture-api`를 먼저 사용한다.
- DB consistency, idempotency storage, lock, transaction이 undecided이면
  `architecture-db`와 `implementation-django`를 먼저 사용한다.
- domain invariant/state transition이 undecided이면 `architecture-ddd`를 먼저 사용한다.
- Router/Schema 구현이 주 작업이고 계약이 충분히 정해졌으면
  `implementation-django-ninja`를 사용한다.
- pytest fixture, factory, mock/test-double 세부 구현이 주 작업이면
  `implementation-test`를 사용한다.
- risky domain work가 DDD, DB, API, Django, tests를 함께 건드리면 각 영역의
  owning reference(`architecture-ddd`, `architecture-db`, `architecture-api`,
  `implementation-django`)를 함께 확인한다.

---

## 12. 참고 문헌

- dddjango `architecture-api` final reference: REST resource, method, status,
  Problem Details, header/content negotiation, pagination, versioning,
  rate limiting, idempotency, OpenAPI.
- dddjango `implementation-django` final reference: Django service, selector,
  ORM, transaction, migration, security, performance.
- dddjango `implementation-test` final reference: pytest, fixture, test-double,
  factory, concurrency and contract test mechanics.
- Django Ninja official documentation:
  - Routers: `https://django-ninja.dev/guides/routers/`
  - Request body and schemas: `https://django-ninja.dev/guides/input/body/`
  - Filtering: `https://django-ninja.dev/guides/input/filtering/`
  - Response schemas and status-specific responses:
    `https://django-ninja.dev/guides/response/`
  - Pagination: `https://django-ninja.dev/guides/response/pagination/`
  - Authentication: `https://django-ninja.dev/guides/authentication/`
  - Errors and exception handlers: `https://django-ninja.dev/guides/errors/`
  - Testing: `https://django-ninja.dev/guides/testing/`
