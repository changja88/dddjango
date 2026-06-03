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

프로젝트에 Django Ninja가 아직 의존성으로 없는 신규 도입이면, 글로벌로 임의 설치하지 말고 의존성 매니페스트(`requirements/*.txt` 등, `implementation-django` §3.1)에 **버전을 핀해 추가**한다 — 핀 표기는 프로젝트의 기존 관례를 따른다(기존 항목이 `Django==4.2.30`처럼 정확 핀이면 `django-ninja==<버전>`으로 맞춘다). 버전 *값*(`<버전>`에 무엇을 핀할지)은 `discipline-houserules` §6.2를 따른다 — 기억 속 버전 금지, 설치 시점에 resolve한 실제 값을 핀하되 기존 프레임워크 핀과 호환되는 최신으로 한다. `INSTALLED_APPS`·`NinjaAPI` 인스턴스·URL 등록 같은 런타임 배선도 함께 둔다.

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
- 성공뿐 아니라 **가능한 모든 status를 `response={...}`에 선언한다** — 알려진 도메인/검증 오류(404·409·422 등)까지 포함한다. 선언하지 않은 status는 OpenAPI/Swagger에 드러나지 않아 client가 계약으로 알 수 없다.
- **`openapi_extra`·`get_openapi_schema`로 status를 수동 선언하는 것은 이 요구를 충족하지 않는다** — 그렇게 하면 Swagger 문서엔 드러나지만 ninja는 그 status를 응답 타입으로 인지하지 못해 검증·직렬화 계약 밖이다. 오류 status는 `response={...}`에 넣는다(문서 가시성과 타입 인지는 다른 것이다).
- **오류는 operation에서 `raise`하고 성공 schema만 `return`한다** — 도메인/애플리케이션 예외를 그대로 raise하면 중앙에서 problem+json으로 변환한다(§6.2). operation 본문에서 `(status, ErrorSchema)` 튜플이나 수제 `HttpResponse`/`JsonResponse`로 오류 응답을 직접 만들지 않는다 — 변환이 흩어지고 problem+json content-type을 일관되게 못 맞춘다.
- **operation을 문서화한다** — `summary`·`description`·`tags`를 decorator 인자로 주어 Swagger UI의 그룹과 설명을 채운다. 외부 client가 읽는 계약 문서다.
- **반환 타입을 명시한다** — `-> object`처럼 정보 없는 타입을 쓰지 않는다. 직렬화 자체는 `response=`가 결정하지만, 반환 타입 annotation은 사람·mypy를 위한 계약 표현이다. 오류를 raise로 처리하면 성공 타입만 남는다(단일 성공 schema면 그 타입, 다중 성공 status면 `Status[...]`).

```python
from django.http import HttpRequest
from ninja import Router, Schema, Status

router = Router()


class OrderIn(Schema):        # request body
    product_id: int
    quantity: int


class OrderOut(Schema):       # response body -- public field만 노출
    id: int
    status: str


class ProblemOut(Schema):     # 오류 본문도 schema로 계약화 (형식은 §6.2 RFC 9457)
    type: str
    title: str
    status: int
    detail: str


# 성공·오류 status를 모두 response에 선언하고(OpenAPI 계약), summary/tags로 문서화한다.
# 오류는 raise만 하고, problem+json 변환은 중앙 한 곳이 한다(§6.2).
@router.post(
    "/orders",
    response={201: OrderOut, 404: ProblemOut, 409: ProblemOut},
    summary="주문 생성",
    description="재고가 충분하면 주문을 만들고 201, 부족하면 409로 거절한다.",
    tags=["orders"],
)
def create_order(request: HttpRequest, payload: OrderIn) -> Status[OrderOut]:
    order = place_order(product_id=payload.product_id, quantity=payload.quantity)  # service 호출
    # ProductNotFound(404)·InsufficientStock(409)은 raise되어 중앙 핸들러가 변환한다(§6.2)
    return Status(201, OrderOut(id=order.id, status=order.status))
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
- `406`: 응답 표현 협상 실패 — `Accept`를 만족하는 표현 없음 (`architecture-api` §7.2)
- `409`: conflict
- `415`: 요청 페이로드 형식 미지원 — `Content-Type`을 이 리소스가 처리 못 함 (`architecture-api` §7.2)
- `422`: semantically invalid input 또는 framework validation error 계약
- `429`: rate limit

> `406`/`415`의 *처리 메커니즘*은 §6.3(콘텐츠 협상 실패) 참조 — ninja 경계 안에서 내고 전역 미들웨어로 가로채지 않는다.

Django Ninja validation error의 default status·형식이 프로젝트 error contract와 다르면
`ValidationError` exception handler(또는 validation 전용 `NinjaAPI` subclass)로 맞춘다 —
problem+json 변환은 §6.2의 중앙 변환에서 422도 함께 처리한다.

### 6.2 RFC 9457 Problem Details

API error는 legacy compatibility contract가 명시적으로 다른 형식을 요구하지 않는
한 RFC 9457 Problem Details를 사용한다.

본문(body) 기준:

- `status` field는 HTTP status와 일치한다.
- `type`은 stable URI를 쓰고, 없으면 `about:blank`를 사용한다.
- `title`은 problem type 요약이며 같은 type이면 안정적으로 유지한다.
- `detail`은 특정 발생에 대한 설명이다.
- `instance`는 request/problem id 같은 식별자가 있을 때 포함한다.
- extension field는 문서화되어 있고 client가 무시해도 안전해야 한다. framework
  validation(422) 오류를 실을 때는 pydantic 내부 구조를 그대로 노출하지 말고
  `invalid-params` 같은 안정된 형태로 매핑한다.

런타임 응답의 media type은 `application/problem+json`이며, 아래 중앙 변환이 설정한다.

**오류는 operation에서 `raise`하고, problem+json 변환은 중앙 `@api.exception_handler`와
헬퍼 한 곳이 한다.** 이게 처방된 기본이다 — operation 본문은 성공 schema만 만들고(§2.2)
변환 형식·content-type을 한 출처로 모은다. 그래야 operation이 raw 응답을 만들 일이 없어
"본문 우회"가 구조적으로 불가능하고 형식이 흩어지지 않는다. 변환 대상:

- **도메인/애플리케이션 예외**: presentation이 예외→HTTP status를 매핑한다(도메인은 HTTP를
  모른다). 예외가 많으면 공통 도메인 베이스를 잡아 매핑 테이블로 status를 정하고, 예외
  *종류마다* 핸들러를 무한 증식시키지 않는다.
- **framework 기본 예외**: ninja는 `AuthenticationError`(401)·`AuthorizationError`(403)·
  `Http404`(404)·`ValidationError`(422)·`Throttled`(429)에 기본 핸들러를 자동 등록하는데
  기본 응답은 plain `application/json`이다. RFC 9457을 일관 적용하려면 이들도 같은 헬퍼로
  오버라이드한다(아래 대안 B는 이걸 한 번에 처리한다).
- `type` URI·`title` 문구·extension 설계는 프로젝트 problem 카탈로그 재량이다.

```python
from ninja import NinjaAPI
from ninja.errors import ValidationError       # ninja validation 오류(≠ pydantic.ValidationError)
from ninja.responses import Response           # JsonResponse 서브클래스 + ninja JSON 인코더

api = NinjaAPI()


def problem(status: int, *, title: str, detail: str,
            type: str = "about:blank", **ext) -> Response:
    # RFC 9457 본문을 한 곳에서 만든다 — 모든 오류 변환이 이 헬퍼만 거친다.
    body = {"type": type, "title": title, "status": status, "detail": detail, **ext}
    return Response(body, status=status, content_type="application/problem+json")


@api.exception_handler(ProductNotFound)        # 도메인 예외 → status 매핑은 presentation 소유
def on_product_not_found(request, exc):
    return problem(404, title="Product not found", detail=str(exc))


@api.exception_handler(InsufficientStock)
def on_insufficient_stock(request, exc):
    return problem(409, title="Insufficient stock", detail=str(exc))


@api.exception_handler(ValidationError)        # framework 기본 422를 problem+json으로 오버라이드
def on_validation_error(request, exc):
    return problem(422, title="Validation failed", detail="Request did not pass validation.",
                   **{"invalid-params": exc.errors})
```

핸들러·헬퍼는 `NinjaAPI` 인스턴스 단위다 — API가 여럿이면 공통 베이스로 일관 적용한다.
async operation도 같은 핸들러 경로를 타므로 별도 처방이 없다.

**헬퍼·중앙 핸들러의 *위치*** — 단일 BC면 그 BC `application/<app>/presentation_layer/`에 둔다.
2개 이상 BC가 *실제로* 공유할 때만 루트 `common/ninja/`(전체경로 `<project_root>/common/ninja/`
— `application/` *아래*가 아니다)로 *승격*한다. 횡단이 생기기 전 조기 승격(`application/common/`
생성)은 YAGNI 위반이다 — 단일 BC에서는 problem 헬퍼도 그 BC의 presentation에 머문다. 위치 규약은
`discipline-houserules` §1.

**대안 B(더 DRY) — `create_response` 오버라이드.** 핸들러마다 content-type을 반복하기 번거롭거나
framework 기본 예외까지 한 번에 통일하고 싶으면, `NinjaAPI`를 상속해 런타임 메서드
`create_response`만 오버라이드해 `status >= 400`이면 media type을 `application/problem+json`으로
바꾼다(2xx 성공은 건드리지 않는다). 그러면 도메인 예외·`Http404`·422·401/403/429가 한 곳에서
일괄 변환되고 핸들러는 problem *본문*만 만들면 된다. 이는 ninja가 공개한 정식 런타임 확장점이며
**생성된 OpenAPI를 건드리지 않는다**(아래 금지 대상과 혼동하지 말 것).

**OpenAPI는 error 응답을 `application/json`으로 표기한다 — 수용된 한계다.** ninja는 선언한
`response={...}` schema를 전역 `renderer.media_type`(기본 `application/json`)으로 문서화하므로,
런타임이 `application/problem+json`을 보내도 생성 OpenAPI의 error 응답 media-type은
`application/json`으로 찍힌다. ninja 1.6.x에 per-status media type이 없어 생기는 것이고
**계약 위반이 아니다** — 런타임 응답도, error 응답 *schema 형태*도 정확하다(§8은 schema
형태를 확인하지 media-type 라벨을 강제하지 않는다). 따라서:

- **생성된 OpenAPI를 사후 변형하지 않는다.** `get_openapi_schema`를 오버라이드해 만들어진
  schema의 media-type을 바꿔치기하는 것은 ninja 내부 dict 구조·경로에 의존해 조용히 깨지고,
  문서를 런타임과 다르게 위조한다(런타임을 바꾸는 위 대안 B와 다르다 — B는 정당, 이건 금지).
- OpenAPI 문서 자체에 `application/problem+json` 표기가 계약상 꼭 필요하면, 개별 응답을
  후가공하지 말고 **설계 단계에서 API 전역 렌더러(`NinjaAPI(renderer=...)`)로 결정**한다
  (전역 렌더러는 성공 응답 media type까지 바꾸므로 trade-off를 따진다).

> 위 사실은 django-ninja 1.6.x 기준이다. operation 본문은 `Status`/도메인 예외 `raise`만
> 쓴다 — `(status, schema)` 튜플 반환은 1.6.x에서 deprecated다. 성공 응답도 같은
> 원칙이다 — 선언한 2xx `response` schema를 수제 `HttpResponse`/`JsonResponse`로
> 우회하지 말고 `Status`/schema 객체로 return한다(직접 조립하면 ninja 직렬화·검증·필드
> 제한이 건너뛰어져 OpenAPI 광고 schema와 실본문이 어긋난다). download·stream·redirect
> 등 선언 schema 없는 성공 경로는 예외다.

### 6.3 콘텐츠 협상 실패 (406/415)

`406`(응답 표현 협상 실패)·`415`(요청 페이로드 형식 미지원)의 **계약은 `architecture-api` §7.2**가
정의한다. *처리 메커니즘은 ninja 경계 안*에서 낸다 — 별도 메커니즘을 발명하지 않는다:

- **415(요청 미디어 미지원)**: ninja 1.6.x는 `BodyModel`이 `Parser.parse_body`의 예외를 일괄 `HttpError(400)`으로 재포장하므로(`ninja/params/models.py`), `parse_body` 안에서 `raise HttpError(415)`해도 400으로 먹혀 작동하지 않는다. 415는 `parse_body` *전*에 내야 하는데 operation 본문은 이미 ninja가 body resolution을 시작한 뒤라 늦다 — **`operation.run` 이전에 도는 view 데코레이터**(`router.add_decorator(fn, mode="view")`)에서 `request.content_type`을 검사한다. 본문 있는 메서드만 대상이다(데코레이터는 GET에도 불리므로, 바디 없는 메서드를 검사에서 빼는 가드를 코드에 둔다 — Parser 경로의 자동 면제가 없다). problem 본문은 데코레이터에서 직접 조립하지 말고 §6.2의 중앙 problem 헬퍼를 호출한다(헬퍼가 아직 없으면 먼저 세운다 — 데코레이터에 수제 `JsonResponse` 인라인 금지). §6.2 대안 B(`create_response` 일괄 problem화)를 쓰면 415만 그 일괄 변환 밖이라 problem 헬퍼를 직접 거치지만 본문 형식은 중앙과 일관한다.

  ```python
  # presentation_layer/api/<feature>/content_negotiation.py — operation은 선언적 payload만 유지
  from functools import wraps

  def enforce_json_content_type(run_op):
      @wraps(run_op)  # 누락 시 ninja가 functools.wraps 미사용 TypeError 경고
      def wrapper(request, *args, **kwargs):
          if request.method in ("POST", "PUT", "PATCH"):
              media = (request.content_type or "").split(";", 1)[0].strip()
              if media != "application/json":
                  return problem_response(415, ...)  # §6.2 중앙 헬퍼 재사용(수제 JsonResponse 금지)
          return run_op(request, *args, **kwargs)     # 통과 → ninja가 payload: Schema 파싱
      return wrapper

  router.add_decorator(enforce_json_content_type, mode="view")
  # operation: def create_order(request, payload: CreateOrderIn) -> Status[CreateOrderOut]  ← 얇음 유지
  ```
- **406(응답 협상 실패)**: ninja `Renderer`는 응답 *형식을 고정*할 뿐 `Accept`를 읽어 표현을 고르는
  협상 훅이 없다. 협상이 필요하면 **operation/경계 코드에서 `request`의 `Accept`를 직접 검사**해
  만족하는 표현이 없으면 `raise HttpError(406, ...)`. (대안 표현을 *실제로* 제공할 때만 협상이 의미
  있고, 단일 표현이면 보통 406이 불필요하다.) 이 검사는 `Accept`·`Content-Type` 같은 **헤더만** 읽으며,
  어느 status에서도 operation·helper가 `request.body`/`json.loads`로 본문을 수동 파싱하지 않는다 — 본문은
  선언적 `payload: Schema`가 받는다(operation을 얇게 유지하는 핵심 신호).
- **임의 status**: `raise HttpError(status, detail)`(`ninja.errors.HttpError`) — operation·Parser
  어디서든 ninja가 응답으로 변환한다. problem+json 본문이 필요하면 위 §6.2의 중앙 변환을 탄다 —
  §6.2 대안 B(`create_response` 오버라이드)를 쓰면 `status >= 400`이 일괄 problem+json화되어 별도
  `HttpError` 핸들러가 불요하고, 안 쓰면 `@api.exception_handler(HttpError)`로 본문을 통일한다(둘 중 하나).

**귀결 — ninja 라우팅 *밖*에 협상을 두지 않는다.** ninja가 협상·임의 status를 경계 안에서 직접
주므로, 협상을 Django 전역 `MIDDLEWARE`·루트 `urls.py` 래퍼·별도 디스패처 등 ninja 라우팅 *밖*
어디에도 두지 않는다(라우팅 중복·BC 격리 침범·`request.path` 하드코딩 시 경로 변경에 silent 깨짐).
협상은 `application/<app>/presentation_layer/`의 ninja 경계(operation·Parser·view 데코레이터 `add_decorator(mode="view")`)가 소유한다.

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
- Problem Details error schema 형태 (생성 OpenAPI상 error 응답 media-type이 `application/json`으로 표기되는 것은 §6.2의 수용된 한계 — 사후 변형하지 않는다)
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
