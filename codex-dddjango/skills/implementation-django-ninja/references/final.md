# Django Ninja API 구현 종합 가이드


> 이 문서는 Django Ninja로 REST API adapter를 구현할 때의 기준을 정리한다.
> REST 계약 자체는 `architecture-api` 스킬,
> Django ORM, service, transaction, migration은
> `implementation-django` 스킬,
> pytest fixture와 test-double 세부 구현은
> `implementation-test` 스킬을 기준으로 한다.
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
6. [상태 코드와 오류 응답](#6-상태-코드와-오류-응답)
7. [Idempotency-Key](#7-idempotency-key)
8. [OpenAPI](#8-openapi)
9. [Mounted Django client와 검증](#9-mounted-django-client와-검증)
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
- OpenAPI에 드러나는 계약 변화의 candidate·승인 뒤 검증 기준 제시
- 실제 mount를 통과하는 Django client 기반 HTTP contract 검증 기준 제시

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
- known application/domain exception을 BC `ErrorSchema`로 변환

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

프로젝트에 Django Ninja가 아직 의존성으로 없는 신규 도입이면, 글로벌로 임의 설치하지 말고 의존성 매니페스트(`requirements/*.txt` 등, `implementation-django` §3.1)에 **버전을 핀해 추가**한다 — 핀 표기는 프로젝트의 기존 관례를 따른다(기존 항목이 `Django==4.2.30`처럼 정확 핀이면 `django-ninja==<버전>`으로 맞춘다). 버전 *값*(`<버전>`에 무엇을 핀할지)은 다음 버전-핀 규율을 따른다 — 기억 속/추정 버전을 쓰지 않는다. 설치 시점에 resolve한 실제 버전을 매니페스트(`requirements`/`pyproject`)에 핀으로 기록하되 기존 프레임워크 핀과 호환되는 최신으로 한다. `django-ninja`·`django-ninja-extra` 모두 동일하다. `INSTALLED_APPS`·`NinjaAPI` 인스턴스·URL 등록 같은 런타임 배선도 함께 둔다.

신규 표준 presentation 표면은 클래스 컨트롤러(§2.3)이므로 **`django-ninja-extra`를 설치하고 `INSTALLED_APPS`에 `'ninja_extra'`를 등록한다**(`NinjaExtraAPI`·`register_controllers` 동작에 필요). 핀 표기·버전 값 규율은 위 `django-ninja`와 동일하다.

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

> **형태 선택.** 신규 표준 presentation 표면은 §2.3의 ninja-extra 클래스 컨트롤러다.
> 기존 함수형 Router는 확립된 표면을 유지할 때 보존한다. 오류 응답 때문에 클래스
> 컨트롤러를 함수형 Router로 바꾸지 않는다.

Operation 구현 기준:

- path parameter, query parameter, request body를 명확히 구분한다.
- request body와 response body는 별도 schema를 사용한다.
- create operation은 성공 시 `201`과 필요하면 `Location` header 계약을 맞춘다.
- delete 또는 no-body update는 `204`를 사용하고 body를 반환하지 않는다.
- async operation에서 ORM을 직접 호출하지 않도록 Django async ORM 제약을 확인한다.
- 직접 반환하는 BC 오류 status는 모두 `response={...}`에 그 BC의 base `ErrorSchema`로
  선언한다. framework가 소유하는 401/403/route 404/422/429/일반 `HttpError`/미식별
  500은 BC 오류로 직접 반환하지도, BC `ErrorSchema`로 광고하지도 않는다.
- `openapi_extra`나 `get_openapi_schema` override·monkeypatch·postprocessor로 오류
  응답을 수동 선언하거나 사후 변형하지 않는다. operation의 `response=`가 runtime과
  OpenAPI가 함께 아는 계약이다.
- known domain/application exception은 컨트롤러가 구체적으로 catch하고, 준비된
  no-arg concrete `ErrorSchema`를 `Status(<승인된 HTTP status 표현>, error)`로 직접 반환한다. 오류
  `(status, schema)` tuple, raw `Response`/dict, 오류 helper/factory/serializer/mapper,
  등록 handler/decorator로 우회하지 않는다(§6.2).
- **operation을 문서화한다** — `summary`·`description`·`tags`를 decorator 인자로 주어 Swagger UI의 그룹과 설명을 채운다. 외부 client가 읽는 계약 문서다.
- **반환 타입을 명시한다** — `-> object`처럼 정보 없는 타입을 쓰지 않는다. 직렬화 자체는 `response=`가 결정하지만, 반환 타입 annotation은 사람·mypy를 위한 계약 표현이다. 직접 반환하는 성공 Schema와 BC `ErrorSchema`/`Status`를 실제 흐름에 맞게 표현한다.
- 선언된 JSON 성공은 Schema 또는 `Status`로 반환한다. `FileResponse`,
  `StreamingHttpResponse`, redirect, schema-less 204는 framework-native 성공
  carveout이며 오류 응답 우회를 허용하지 않는다.

Operation은 10번 slot이 승인한 **한 경로**를 선택한다.

- **exception path:** request를 준비한 뒤 `try`에는 최외곽 application call 한 문장만 둔다.
  구체 exception 또는 구체 exception tuple만 catch하고, catch 안에서 no-arg concrete 또는
  populated BC-base `ErrorSchema`, 필요하면 주입된 응답용 header를 만든 뒤 두 인자
  `Status(<승인된 HTTP status 표현>, error)`로 직접 반환한다. 성공 변환은 `try` 뒤에 둔다.
- **failed Result/`None`/outcome path:** application call을 정확히 한 번 한 뒤, `try` 없이
  slot이 승인한 failed branch를 call 바로 다음에 둔다. 같은 ErrorSchema/header/두 인자 `Status`
  구성을 직접 수행하며, 예외·catch·helper·mapping table을 꾸며내지 않는다.

```python
from ninja import Status
from ninja_extra import api_controller, route, status

from application.order.application_layer.order.place_order.place_order_command import PlaceOrderCommand
from application.order.composition_root.dependency_wiring import build_place_order
from application.order.domain_layer.order.exception.insufficient_stock import InsufficientStock
from application.order.domain_layer.order.exception.product_not_found import ProductNotFound
from application.order.driving_layer.api.bc_error_schema import (
    OrderErrorSchema,
    OrderInsufficientStockError,
    OrderProductNotFoundError,
)
from application.order.driving_layer.api.order.schema.schema_in import OrderIn
from application.order.driving_layer.api.order.schema.schema_out import OrderOut


@api_controller("/orders", tags=["orders"], auto_import=False)
class OrderController:
    @route.post(
        "",
        response={201: OrderOut, 404: OrderErrorSchema, 409: OrderErrorSchema},
        summary="주문 생성",
        description="재고가 충분하면 주문을 만들고 201, 부족하면 409로 거절한다.",
    )
    def create_order(
        self,
        request,
        payload: OrderIn,
    ) -> Status[OrderOut | OrderErrorSchema]:
        command = PlaceOrderCommand(
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        use_case = build_place_order()

        try:
            order = use_case.execute(command)
        except ProductNotFound:
            error = OrderProductNotFoundError()
            return Status(status.HTTP_404_NOT_FOUND, error)
        except InsufficientStock:
            error = OrderInsufficientStockError()
            return Status(status.HTTP_409_CONFLICT, error)

        response = OrderOut(id=order.id, status=order.status)
        return Status(status.HTTP_201_CREATED, response)
```

### 2.3 클래스 컨트롤러 (ninja-extra) — 신규 표준

신규 표준 presentation 표면은 함수형 `@router.post` operation이 아니라 **ninja-extra
`@api_controller` 클래스 컨트롤러**로 만든다. 함수형 Router operation(§2.2)은 레거시
경로로 읽고 기존 형태를 보존한다. **touched(신규·수정) presentation 표면은 클래스
컨트롤러로 만든다.** 406/415나 오류 응답을 이유로 클래스 컨트롤러를 함수형 Router로
강등하지 않는다.

클래스 컨트롤러는 함수형 operation의 계약을 그대로 보존한다 — `response={status: Schema}`
선언과 Schema/`Status` 반환을 유지하며, known exception의 직접 `ErrorSchema` 변환 순서도
§2.2와 같다. 바뀌는 것은 *형태*뿐이다: Router prefix가 클래스 데코레이터로,
operation 함수가 `self` 첫 인자를 받는 메서드로 올라간다.

요점:

- 클래스 데코레이터 `@api_controller("/orders", tags=[...], auto_import=False)`가 resource
  prefix·tag를 소유하고,
  메서드 데코레이터 `@route.post("")`가 그 prefix 기준 *상대* 경로를 잡는다(함수형의
  `@router.post("/orders")` 한 줄이 둘로 나뉜 것).
- operation 함수가 `self`를 첫 인자로 받는 메서드가 된다. 메서드명은 함수형과 같이 동사구를
  유지한다(`create_order`).
- `response=`/`Status` 반환, controller-owned 오류 처리, 반환 타입 명시는 §2.2와
  **동일하게 보존**한다.
- **`ControllerBase`를 직접 상속하지 않는다** — `@api_controller` 데코레이터가 컨트롤러 기반을
  자동 주입한다(명시 상속은 중복이다).

**등록 — 프로젝트 소유 API, BC 소유 registrar, URLconf 소유 합성.** contract scope 안에서
프로젝트 `api.py`가 `NinjaExtraAPI` 인스턴스 하나를 소유한다. 각 BC는 project API를 import하지
않는 side-effect-free `register_<bc>_api(api)`만 노출한다. 프로젝트 `urls.py`가 API와 registrar를
import하고, 각 registrar를 명시적으로 한 번 호출한 뒤 API를 mount한다. BC 모듈 import만으로
registration이 일어나면 안 된다.

명시 registrar 합성을 선택한 controller는 `@api_controller(..., auto_import=False)`로
Ninja Extra auto-import를 끈다. 그래야 controller import가 global registry를 채우는
side effect를 만들지 않고, 등록 집합과 시점은 `register_<bc>_api(api)`와 프로젝트
`urls.py` 호출만으로 결정된다.

```python
# config/api.py — 프로젝트가 contract scope의 API 인스턴스 하나를 소유한다.
from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
```

```python
# application/order/driving_layer/api/api_router.py
from ninja_extra import NinjaExtraAPI

from .order.order_controller import OrderController


def register_order_api(api: NinjaExtraAPI) -> None:
    api.register_controllers(OrderController)
```

```python
# config/urls.py — explicit composition과 mount를 함께 소유한다.
from django.urls import path

from application.order.driving_layer.api.api_router import register_order_api
from config.api import api

register_order_api(api)

urlpatterns = [
    path("api/", api.urls),
]
```

요점:

- registrar는 자기 BC controller만 import하며, 전달받은 `api`에 등록하는 함수 밖에서는
  아무 등록도 하지 않는다.
- registrar가 `config.api`를 import하거나 모듈 top-level에서 `register_controllers`를
  호출하지 않는다.
- 프로젝트 `urls.py` 밖에서 registrar를 몰래 호출하거나 직접 controller를 등록하지 않는다.
- public/internal 또는 version별 API 인스턴스가 이미 독립 계약 surface로 확립돼 **소비자가
  의존하는** 경우는 승인된 별도 scope로 보존할 수 있다 — 보존의 근거는 «소비자 의존»이지
  «먼저 작성돼 있음»이 아니다. 신규 BC마다 API 인스턴스를 만드는 것은 scope 분리가 아니다.

**컴포지션 루트(배선) — `composition_root/`.** operation/메서드 본문에서 `Django…Repository()`·`…Adapter()`를 직접 생성하면 presentation→infra 직접 결합(Q-7)이다. DI 조립은 BC 루트 `application/<bounded_context>/composition_root/`에 모은다 — 결선은 `dependency_wiring.py`가 소유하고 use-case마다 `build_<use_case>()` 팩토리를 두며, presentation은 컨트롤러 메서드에서 그 팩토리를 **호출만** 한다(매요청 조립). 이벤트 구독 결선은 `event_wiring.py`가 따로 진다. use-case 없는 순수 데이터소스 BC는 둘 게 없으니 생략한다.

```python
# application/order/composition_root/dependency_wiring.py — BC 루트의 DI 결선. 구체 infra를 use-case에 주입.
from application.order.application_layer.order.place_order.place_order_use_case import PlaceOrderUseCase
from application.order.driven_layer.adapter.anticorruption_layer.catalog.product_stock_adapter import DjangoProductStockAdapter
from application.order.driven_layer.adapter.persistence.repository.order_repository import DjangoOrderRepository


def build_place_order() -> PlaceOrderUseCase:
    # 구체 infra를 고르는 유일한 곳 — 안쪽 계층은 domain repository/port 추상에만 의존(DIP).
    return PlaceOrderUseCase(
        order_repository=DjangoOrderRepository(),
        product_stock_port=DjangoProductStockAdapter(),
    )
```

- **단일 파일·BC당 1개**: 컴포지션 루트는 "구체를 아는 유일한 곳"이라 한 파일에 모은다 — feature별 `composition/` 폴더로 쪼개면 루트가 분열돼 패턴 위반이다. `config/api.py`나 `api_router.py`(HTTP 등록)에 섞지도 않는다.
- **매요청 호출**: 컨트롤러 메서드에서 `use_case = build_place_order()` 후 `use_case.execute(command)`. 모듈 레벨 전역 인스턴스로 import 시점에 만들지 않는다(import 부작용·테스트 오버라이드 회피).
- **BC 격리**: order의 루트는 *자기 BC*의 infra/ACL만 import한다(`DjangoProductStockAdapter`는 order `driven_layer/adapter/anticorruption_layer/`; catalog는 직접 import 안 하고 OHS/ACL 경유). `composition_root/`(`dependency_wiring.py`)는 use-case DI만 소유하며 API instance·controller registration을 소유하지 않는다.

**설치.** ninja-extra는 별도 앱이다 — `INSTALLED_APPS += ['ninja_extra']`가 필요하다(의존성
매니페스트 핀은 §2.1과 동일하다).

**탐색 → 포함/생성 규칙 (새 operation 추가 시).** 새 operation을 둘 곳은 다음 순서로 정한다.

1. 해당 앱 `driving_layer/api/`에서 `@api_controller` 데코 클래스를 grep한다.
2. 단일 컨트롤러가 있으면 → 그 컨트롤러의 메서드로 포함한다.
3. 분할되어 여럿이면 → 리소스(URL prefix)가 일치하는 컨트롤러에 포함하고, 없으면 새 리소스
   컨트롤러를 만든다.
4. 컨트롤러가 없으면 → 새 `<Aggregate>Controller`를 생성한다.

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
- enum성 필드(상태·종류)는 `Literal[...]` 또는 `StrEnum`으로 선언해 OpenAPI 계약에
  enum으로 노출한다. 도메인 enum에서 파생하되, 계약 안정성을 도메인 리팩터링과 분리해야
  하면 경계-로컬 `Literal`로 고정한다(published language — `architecture-ddd` §2.5).
  응답 조립·비교에 원시 리터럴을 흩지 않는다(`discipline-cleancode` §2.14 소비 규율).
- **발행 이벤트 봉투(태그드 유니온)의 discriminator는 1종째부터 domain `StrEnum` 파생으로
  선언한다**(birth-enum — `architecture-ddd` §3.7). 각 이벤트 Schema의 태그는
  `event_type: Literal[EventType.PARENT_SAFE_ALERT] = EventType.PARENT_SAFE_ALERT`,
  봉투는 `Event = Annotated[Union[...], Field(discriminator="event_type")]` — 평
  (non-Literal) Enum 필드는 discriminator로 쓸 수 없으므로(Pydantic) Literal 파생이
  유일 경로다. enum 파생과 문자열 Literal은 JSON schema가 동일하게 `const`로 렌더되므로
  OpenAPI 계약은 불변 — "계약 안정성 때문에 맨 Literal"은 이 위치에서 성립하지 않는다.
  `payload_schema_version` 등 버전 태그는 형태가 같아도 리터럴 동결 유지(발행 순간
  동결되는 계약 표식 — §3.7 짝 조항). union-enum 동기는 중앙 영구 테스트 입장 심사의
  candidate다. 승인된 공개 event wire literal과 독자 failure를 보호해 `add/update`인 경우에만
  직렬화 경계에서 검증한다(`discipline-tdd`; mechanics는 `implementation-test` §15.5).
  봉투 union을 페이지네이션 응답에 직접 조합하지 않는다
  (ninja discriminated union+pagination의 OpenAPI 렌더 미해결 버그 — vitalik/django-ninja#1308).

Schema의 validator 위치, `ValidationError.loc`, Pydantic/Ninja 기본 validation·직렬화는 그 자체로
영구 테스트 자격이 아니다. 별도 사용자 승인 또는 실제 deployed consumer evidence가 있는 공개
Python 계약이면 중앙 입장 심사로 판정할 수 있고, 공개 HTTP·wire 계약이면 isolated Schema 직접 호출이
아니라 실제 mount 경계에서 검증한다.

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
- auth adapter는 성공 시 identity/principal을 반환한다. 실패는 `None`을 반환하거나
  framework `AuthenticationError`를 raise한다.
- `ErrorSchema`를 auth 결과로 반환하거나 `request.auth`에 저장하지 않는다. framework 401을
  BC 식별자 body로 바꾸는 전역 변환도 추가하지 않는다(§6.2).
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

(아래는 Ninja 원생 함수형 예시다 — 이 플러그인의 신규 표면은 §2.3 의 클래스 컨트롤러 형태를 쓴다)

```python
from typing import Optional
from ninja import FilterSchema, Query


class OrderFilter(FilterSchema):
    status: Optional[str] = None       # 허용 filter key만 명시한다


@router.get("/orders", response=list[OrderOut])
def list_orders(request, filters: Query[OrderFilter]):
    use_case = build_list_orders()   # dependency_wiring.py 팩토리 — 매요청 조립(아래 "컴포지션 루트")
    return use_case.execute(ListOrdersQuery(filters=filters))
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
    use_case = build_list_orders()   # dependency_wiring.py 팩토리 — 매요청 조립
    return use_case.execute(ListOrdersQuery())   # use case가 QuerySet 반환 → paginate가 페이지로 자른다
```

---

## 6. 상태 코드와 오류 응답

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
- `503`: 일시적 서비스 불가(과부하·정비·승인된 일시 경합). 직접 공개하는 retryable BC
  오류라면 controller가 주입받은 응답용(temporal) Django `HttpResponse`에 승인된 `Retry-After`를
  설정한 뒤 두 인자 `Status`를 반환한다. 503/409 선택은 명세 §5/G1이 정하고 raw 인프라
  예외를 controller가 임의 분류하지 않는다(§6.2,
  `architecture-api` §13.4).

> `406`/`415`의 *처리 메커니즘*은 §6.3(콘텐츠 협상 실패) 참조 — ninja 경계 안에서 내고 전역 미들웨어로 가로채지 않는다.

Django Ninja validation error의 default status·body는 framework-owned 응답이다. 새
code-profile에서는 이를 BC 식별자 body로 맞추기 위한 전역 변환을 추가하지 않으며, 그 body를
정확하고 안정적인 공개 식별자 계약이라고 주장하지 않는다. 별도 공개 계약이 필요하면 G1로
돌아가 profile과 호환성 범위를 먼저 승인한다.

### 6.2 `dddjango-code-json` 오류 프로필

오류 프로필 선택은 `architecture-api` §5.4를 따른다. 이미 배포된 범위는 관찰한 계약을
보존하고, 새 dddjango Django Ninja 범위의 기본은 `dddjango-code-json`이다. 이 절은 그
기본 프로필의 copy-safe 구현 기준이다.

**공통 core와 변경 gate.** dddjango는 공통 body property를 정하지 않는다. 기존 프로젝트는
관찰된 기존 오류 schema exact shape를 기준선으로 보존한다. 신규 scope는 exact field set·각 type·
required/default·nullable·Field metadata·model config/legacy Config·validator/serializer/computed field/Pydantic hook inventory와 effective semantics·wire 직렬화를 G1 slot 6에서 먼저 제안하고 별도로
명시 승인받는다. 기준선의 property 추가·삭제·이름·타입·존재성·변환 규칙·의미 변경도 일반
기능 승인에 묻히지 않는 별도 contract 변경이다. 호환성 영향과 server/client/test 전환 범위를
보여 준 뒤 사용자가 명시 승인하기 전에는 코드부터 바꾸지 않는다. `code/title/status/detail`과
`error_type/msg/is_show`는 모두 가능한 프로젝트 계약 예일 뿐 plugin 기본값이 아니다.

기존 승인 shape의 canonical common/BC schema 정의에 있는 dynamic field default·validator/serializer/
Pydantic hook·custom config/decorator 또는 project·relative import/dynamic binding은 코드를 단순화하거나
explicit alias를 새로 넣어 우회하지 않는다. class-header `**`·legacy `Config` 상속·non-alias config callable·config mutation을 포함한
임의 Python의 import-time·호출-time 의미 때문에 schema checker가 항상
`DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`를 낸다. canonical module의 직접 import-time mutation/side effect는
proof 대상이 아니라 구조 위반으로 차단한다. controller/OpenAPI checker가 단순 형태를 정적으로
계산해 추가 진단을 내더라도 이 marker를 없애지 않는다. target의 실제 dependency pin에서 model
field/validation path/serialization alias와 실제 BC-base 생성 key·ErrorCode 멤버·exact dump를
검토하는 것은 별도 shape 승인 근거를 위한 일회성 분석이며 영구 테스트를 자동 생성하지 않는다.
mounted status/body와 generated OpenAPI는 각각 중앙 입장 심사의 공개 wire 후보이고,
`add/update`일 때만 §8–§9의 mount 경계 recipe로 검증한다. API와
discipline reviewer가 기존 shape 무변경을 확인한 경우에만 Coordinator가
`RESOLVED_DYNAMIC_ERROR_SHAPE_ANALYSIS`로 해소한다. 이는 새 shape나 shape 변경의 별도 사용자 명시
승인을 대신하지 않고, 다른 analysis/blocker를 면제하지도 않는다. controller 등 schema 소유 경계
밖의 model config mutation은 기존 shape 보존 경로가 아니다. 선택 module의 직접 mutation과 직접
import한 module-level callable 경로는 owning controller checker가 차단한다. imported class method·
2-hop·dynamic dispatch는 결정적 AST 증명 범위 밖이므로 checker 통과로 면제하지 않고 API/discipline
reviewer가 직접 읽는다.

새 단일-scope code-profile의 공통 오류 모듈은 `framework/ninja/framework_error_schema.py`
하나다(validation 응답 schema가 필요하면 `framework_validation_error_schema.py`).
`framework/ninja/`는 공유 `<technology>` 폴더라 이 계약 밖의 다른 `<module>.py`와 공존한다.

```text
framework/ninja/
├── __init__.py
└── framework_error_schema.py
```

```python
# framework/ninja/framework_error_schema.py
from ninja import Schema


class FrameworkErrorSchema(Schema):
    # slot 6에서 승인된 프로젝트 고유 필드만 그대로 선언한다.
    ...
```

공통 `FrameworkErrorSchema`는 slot 6에서 승인된 transport core shape만 소유한다. concrete 오류와 BC
ErrorCode catalog를 이 파일에 추가하지 않으며, 승인 shape 밖의 validator·field metadata·임의
extension bag도 발명하지 않는다. 독립된 public/internal,
version, namespace가 실제로 다른 계약 scope라면 G1에서 scope와 공통 경로를 각각 승인한다.
기존 공용 경로가 있으면 승인된 동등 계약을 우선 재사용한다.

**BC 오류 언어.** 오류를 직접 공개하는 각 BC는
`application/<bc>/driving_layer/api/bc_error_schema.py` 파일 하나에 다음을 함께 둔다.

- `<Bc>ErrorCode(StrEnum)` 하나
- 공통 `FrameworkErrorSchema`를 상속하고 slot 6의 식별자 필드 하나만 `<Bc>ErrorCode`로 좁히는 `<Bc>ErrorSchema` 하나
- 반복해서 반환할 사건별 concrete `ErrorSchema` subclass
- BC가 공개하는 모든 식별자 문자열 값은 프로젝트 전체 code-profile inventory에서 중복되지 않는 값

```python
# application/order/driving_layer/api/bc_error_schema.py
from enum import StrEnum

from framework.ninja.framework_error_schema import FrameworkErrorSchema


class OrderErrorCode(StrEnum):
    PRODUCT_NOT_FOUND = "order_product_not_found"
    INSUFFICIENT_STOCK = "order_insufficient_stock"
    TEMPORARILY_UNAVAILABLE = "order_temporarily_unavailable"
    VERSION_MISMATCH = "order_version_mismatch"


class OrderErrorSchema(FrameworkErrorSchema):
    # slot 6에서 지정한 공통 식별자 필드를 OrderErrorCode로 좁힌다.
    ...


class OrderProductNotFoundError(OrderErrorSchema):
    # slot 6의 모든 required field에 승인된 default를 제공한다.
    # 식별자 default는 OrderErrorCode.PRODUCT_NOT_FOUND다.
    ...
```

BC base의 식별자 field는 공통 annotation의 wrapper/nullability·required/default와 default를
제외한 `Field(...)` metadata를 보존하고 `str` 자리만 자기 Enum으로 좁힌다. 공통 default가
문자열이면 같은 wire value의 Enum member로 표현한다. concrete 오류는 slot 6에서 해당
concrete의 고정값으로 승인된 모든 required field에 default가 있어 인자 없이 생성한다.
새 필드·validator·child `model_config`나 annotation/Field metadata drift를 concrete subclass에
추가하지 않고, 승인 alias 등이 있는 field를 재선언하면 같은 metadata를 반복한다. URI·instance
같은 다른 profile 필드도 섞지 않는다. 오류마다 파일을 나누거나 validation 전용 두 번째 오류
schema 파일을 만들지 않는다.

한 operation에서만 의미가 생기는 사건이고 별도 concrete type이 필요하지 않다고 승인된
경우에는 BC base를 직접 채울 수 있다. 이것은 concrete를 인자와 함께 생성하는 우회가 아니다.
실제 controller의 `OrderErrorSchema(...)` 호출에 slot 6의 모든 field keyword와 승인된 값을 그
자리에서 전부 명시하는 것이 아니라, 모든 required field와 그 사건에서 기본값을 덮어써야 하는
승인 optional field만 keyword로 명시한다. 다음 문장에서
`Status(status.HTTP_409_CONFLICT, error)`를 반환한다.
dictionary unpacking, builder, factory, mapping table로 field 작성을 우회하지 않는다.

**컨트롤러가 변환을 소유한다.** known domain/application failure의 공개 식별자·status 선택은
해당 BC controller가 한다. 짧은 반복 mapping은 의도적인 지역 중복이며, 다음 순서를
10번 slot이 승인한 한 path로 보인다.

1. **exception path:** 입력 Schema를 준비하고 `try`에는 최외곽 application call 한 문장만
   둔다. 구체 known exception 또는 구체 exception tuple만 catch해 no-arg concrete 또는
   populated BC-base `ErrorSchema`, 필요하면 주입된 응답용 header를 만든 뒤 두 인자
   `Status(<승인된 HTTP status 표현>, error)`를 직접 반환한다. status 표현은 literal/Ninja
   status 상수 또는 slot 6이 실제로 승인한 body field 접근일 수 있다. 성공 변환은 `try` 뒤에 둔다.
2. **failed Result/`None`/outcome path:** 입력 Schema를 준비한 뒤 application call을 정확히
   한 번 하고, `try` 없이 승인된 failure branch를 call 바로 다음에 둔다. 같은 ErrorSchema/header/
   두 인자 Status 구성을 직접 수행하며, 성공 변환은 그 branch 뒤에 둔다. 예외·catch·helper·
   mapping table을 꾸며내지 않는다.

§2.2가 sync concrete-catch 예시다. async와 동일한 contract는 다음과 같다.

```python
@route.get(
    "/{order_id}",
    response={200: OrderOut, 404: OrderErrorSchema},
    summary="주문 조회",
    description="주문을 조회한다.",
)
async def get_order(
    self,
    request,
    order_id: int,
) -> OrderOut | Status[OrderErrorSchema]:
    query_value = GetOrderQuery(order_id=order_id)
    use_case = build_get_order()

    try:
        order = await use_case.execute(query_value)
    except (OrderNotFound, ArchivedOrderNotFound):
        error = OrderProductNotFoundError()
        return Status(status.HTTP_404_NOT_FOUND, error)

    return OrderOut.from_result(order)
```

`try` 안에 준비·분기·로그·성공 변환을 넣지 않는다. `Exception`, framework exception,
raw DB/SDK exception을 catch하지 않고, 컨트롤러가 방금 raise한 예외를 즉시 catch하지
않는다. 서로 다른 공개 의미가 필요한 known exception은 별도 catch와 concrete로 나누고,
같은 공개 의미로 수렴할 때만 tuple catch를 쓴다.

다음은 10번 slot이 `ReserveOrderInsufficientStockResult`를 승인된 failed Result로 정한
경우의 controller-owned 직접 변환이다. application command/Result variant는 application
layer DTO에서 import하고 use case는 BC `composition_root`에서 조립한다. call 뒤 branch가 BC
`ErrorSchema`를 만들며 예외 path나 presentation helper를 흉내 내지 않는다.

```python
from typing import assert_never

from ninja import Status
from ninja_extra import api_controller, route, status

from application.order.application_layer.order.reserve_order.reserve_order_command import (
    ReserveOrderCommand,
)
from application.order.application_layer.order.reserve_order.reserve_order_result import (
    ReserveOrderInsufficientStockResult,
    ReserveOrderResult,
    ReserveOrderSucceededResult,
)
from application.order.composition_root.dependency_wiring import build_reserve_order
from application.order.driving_layer.api.bc_error_schema import (
    OrderErrorSchema,
    OrderInsufficientStockError,
)
from application.order.driving_layer.api.order.schema.schema_in import OrderIn
from application.order.driving_layer.api.order.schema.schema_out import OrderOut


@api_controller("/orders", tags=["orders"], auto_import=False)
class OrderController:
    @route.post(
        "/reserve",
        response={201: OrderOut, 409: OrderErrorSchema},
        summary="주문 예약",
        description="재고가 부족하면 409, 가능하면 예약 주문을 만든다.",
    )
    def reserve_order(
        self,
        request,
        payload: OrderIn,
    ) -> Status[OrderOut | OrderErrorSchema]:
        command = ReserveOrderCommand(
            order_id=payload.order_id,
            quantity=payload.quantity,
        )
        use_case = build_reserve_order()
        result: ReserveOrderResult = use_case.execute(command)

        if isinstance(result, ReserveOrderInsufficientStockResult):
            error = OrderInsufficientStockError()
            return Status(status.HTTP_409_CONFLICT, error)

        if isinstance(result, ReserveOrderSucceededResult):
            response = OrderOut.from_result(result.order)
            return Status(status.HTTP_201_CREATED, response)

        assert_never(result)
```

application-owned closed `ReserveOrderResult`와 `assert_never`가 mapping을 exhaustive하게 만든다.
새 variant나 untyped 값은 `None`으로 조용히 반환되거나 BC 오류로 꾸며지지 않고 framework-owned
500 계약 위반으로 드러난다.

반대로 use case가 계약상 Result/`None`을 native 성공으로 반환하면 controller가 그 값을 helper
없이 직접 성공 계약으로 반환할 수 있다. `None`/Result 자체가 언제나 실패라는 뜻은 아니다.
12-slot이 그 operation의 의미를 결정하며, 실패를 Result의 익명 dict나 `None`으로 숨기는 규칙은
아니다.

```python
result = query.execute(query_value)

if result is None:
    return None
return result
```

승인된 BC 오류 헤더도 같은 controller가 소유하되 `Status` 생성자에 header를 넘기지 않는다.
명세가 retryable BC 503과 `Retry-After`를 승인했다면 controller method가 주입된 응답용(temporal)
Django `HttpResponse`를 받아 선택된 mapping branch에서 header를 설정한 뒤 두 인자 `Status`를
반환한다. exception path의 구체 catch는 그 branch의 한 형태다.

```python
from django.http import HttpResponse


@route.post(
    "/retry",
    response={200: OrderOut, 503: OrderErrorSchema},
    summary="주문 재시도",
    description="일시 경합이면 재시도 시점을 안내한다.",
)
def retry_order(
    self,
    request,
    response: HttpResponse,
    payload: RetryOrderIn,
) -> OrderOut | Status[OrderErrorSchema]:
    command = RetryOrderCommand(order_id=payload.order_id)
    use_case = build_retry_order()

    try:
        order = use_case.execute(command)
    except OrderContention:
        response["Retry-After"] = "1"
        error = OrderTemporarilyUnavailableError()
        return Status(status.HTTP_503_SERVICE_UNAVAILABLE, error)

    return OrderOut.from_result(order)
```

**추출 금지.** 오류 응답 helper/factory/serializer/mapping, exception handler,
handler 등록 decorator, generic response builder를 만들거나 호출하지 않는다.
여기서 serializer와 decorator는 `ErrorSchema`를 HTTP 응답으로 바꾸는 변환기와 예외 handler 등록을 뜻한다.
승인된 common Schema 자체의 Pydantic validator/serializer/decorator/hook은 exact shape의 일부로 보존한다.
오류를 raw `Response`/`JsonResponse`/`HttpResponse`, dict, tuple로 만들지 않고
`model_dump`를 직접 호출하지 않는다. controller가 짧은 exception→concrete mapping과
`Status` 반환을 직접 소유해야 runtime 직렬화와 `response=` 선언이 한눈에 대응한다.
여러 controller의 짧은 반복은 이 명시성을 위해 허용한다.

**framework 오류 경계.** 인증 401, 인가 403, route 404, request validation 422,
throttling 429, 일반 `HttpError`, 미식별 500은 framework가 소유한다. 새 code-profile은
이를 BC `ErrorSchema`/`<Bc>ErrorCode`로 바꾸지 않으며, 전역 handler나 catch-all mapper로
가로채지 않는다. 깨진 JSON과 framework validation body도 정확하고 안정적인
`dddjango-code-json` wire contract라고 주장하지 않는다. framework status를 특정 BC의
`response={...}`에 광고하지 않는다.

authentication adapter의 성공 반환값은 identity/principal이다. 실패는 `None`을 반환하거나
framework `AuthenticationError`를 raise한다. `request.auth`에 `ErrorSchema`를 저장하거나
`ErrorSchema`를 인증 결과로 반환하지 않는다.

```python
from ninja.errors import AuthenticationError
from ninja.security import HttpBearer


class BearerAuth(HttpBearer):
    def authenticate(self, request, token):
        principal = authenticate_token(token)
        if principal is None:
            return None
        if principal.is_disabled:
            raise AuthenticationError
        return principal
```

**인프라 오류 경계.** raw `OperationalError`, `IntegrityError`, SDK/network 오류를
controller나 전역 recognizer가 문자열·SQLSTATE로 분류하지 않는다. 기본은 framework의
미식별 500 경로다. 특정 실패가 안정된 공개 의미를 가진다고 G1에서 승인된 경우에만 infra/ACL이
그 실패를 자기 BC의 구체 domain/application exception으로 정규화하고, controller가 그
구체 exception을 위의 직접 흐름으로 처리한다. 인프라 예외를 합성하거나 다른 BC exception을
그대로 통과시키지 않는다.

**응답 선언과 OpenAPI.** controller가 직접 반환할 수 있는 각 BC 오류 status는 operation의
`response={...}`에서 같은 BC base `<Bc>ErrorSchema`에 매핑한다. concrete class는 runtime
instance를 고정하지만 OpenAPI status mapping에는 BC base를 쓴다. 직접 반환하지 않는
framework status는 BC base로 선언하지 않는다. 오류 응답 선언을 `openapi_extra`로 보충하거나
`get_openapi_schema` override, monkeypatch, postprocessor로 사후 변형하지 않는다. 공개 OpenAPI
후보가 중앙 입장 심사에서 `add/update`이면 mounted API의 생성 문서에서 status별 BC base schema를 확인한다.

선언된 JSON 성공은 Schema 또는 `Status`를 통해 Ninja의 validation/serialization을 탄다.
`FileResponse`, `StreamingHttpResponse`, redirect, schema-less 204는 성공 응답의
framework-native carveout이다. 어느 carveout도 오류 helper나 raw 오류 응답을 허용하지 않는다.

**승인된 wire 보존 — 근거는 소비자 의존.** 기존 범위가 RFC 9457 Problem Details를 이미 공개하고
소비자·테스트가 승인된 wire contract에 의존한다면 관찰한 status, body, header, media type을
그대로 보존한다. 보존이 정당한 근거는 둘뿐이다 — ⑴ 밖이 의존한다(wire shape) ⑵ 되돌릴 수 없다.
«먼저 작성돼 있음»(brownfield)은 근거가 아니며 코드의 «자리»는 둘 어디에도 안 걸린다(자리는
백스톱 위반 = 리팩터링 대상). 이 짧은 carveout은 wire 계약을 지키기 위한 것이며, 새
helper·handler 레시피나 code-profile과의 혼합을 제시하지 않는다.

### 6.3 콘텐츠 협상 실패 (406/415)

`406`/`415` 계약은 `architecture-api` §7.2에서 별도 승인한 경우에만 구현한다.
새 code-profile의 모든 endpoint에 자동으로 강제하지 않는다.

- **406**: 실제로 여러 응답 표현을 제공하고 `Accept` 협상이 승인된 operation만 Ninja
  경계에서 header를 검사한다. 만족하는 표현이 없으면 framework
  `HttpError(406, "Not acceptable")`를 raise한다.
- **415**: 지원 media type을 제한하는 계약이 별도 승인된 endpoint만 처리한다.
  사용 중인 Django Ninja 버전에서 parser 예외가 다른 status로 정규화될 수 있으므로,
  현재 presentation 스타일과 호환되는 Ninja-owned pre-body 경계를 선택하고
  공개 415 wire를 중앙 입장 심사의 candidate로 제출한다. `add/update`이면 실제 URLconf에
  mount된 Django client로 `HttpError(415, "Unsupported media type")`가 415로 나가는지 검증한다.
- 406/415는 framework `HttpError` body를 그대로 사용한다. BC `ErrorSchema`, code,
  오류 helper, custom handler, raw response를 만들지 않고 BC `response={...}`에도
  광고하지 않는다.
- 클래스 컨트롤러를 415 때문에 함수형 Router로 바꾸지 않는다. 기존 함수형 Router도
  오류 때문에 클래스 컨트롤러로 자동 변환하지 않는다.
- 어느 경로에서도 `request.body`/`json.loads`로 본문을 수동 파싱하지 않는다.
  request body는 선언적 `payload: Schema`가 받는다.
- Django 전역 middleware, root URL wrapper, 별도 dispatcher처럼 Ninja 라우팅 밖에서
  status를 합성하지 않는다.

별도 승인이 없으면 framework의 현재 content negotiation/parsing 동작을 보존하고,
그 body를 정확한 code-profile 공개 계약이라고 주장하지 않는다.


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

아래 항목은 자동 테스트 목록이 아니라 중앙 영구 테스트 입장 심사의 candidate다. 공개 OpenAPI
계약과 독자 failure를 보호해 `add/update`인 항목만 프로젝트 URLconf에 mount된 API가 생성하는
문서에서 검증한다. isolated Schema나 미등록 Router/controller가 만든 문서는 공개 OpenAPI 증거가 아니다.

입장 심사 후보:

- path, method, tag, operation id, summary
- request body, query/path/header parameter
- required/optional/nullable field
- enum, format, default
- status별 response schema
- 직접 반환하는 BC status별 `<Bc>ErrorSchema` schema와 승인 식별자 field의 Enum 값
- framework-owned status가 BC `ErrorSchema`로 잘못 광고되지 않는지
- auth/security requirement
- pagination/filtering parameter와 response metadata
- deprecation/versioning note

OpenAPI generation 또는 schema diff를 실행하지 않았다면 실행했다고 말하지 않는다.
DRF-to-Ninja migration에서는 가능한 경우 기존 DRF schema와 Django Ninja schema를
비교하고 차이를 기록한다.

---

## 9. Mounted Django client와 검증

### 9.1 공개 HTTP 검증 범위

Django Ninja HTTP 항목도 먼저 `discipline-tdd`의 중앙 입장 심사를 거친다. 아래는 자동 테스트
목록이 아니라 candidate이며, 승인된 공개 HTTP 계약과 독자 production failure가 `add/update`인
경우에만 테스트를 작성한다. Business rule은 승인된 domain/service boundary에서 검증한다.

- request schema validation
- status code와 header
- response schema field/type
- auth/permission wiring
- 직접 반환한 BC 오류의 slot-6 exact body shape와 mapping별 HTTP status
- pagination/filtering/sorting parameter
- idempotency replay와 conflict
- DRF-to-Ninja compatibility

공개 HTTP 계약은 `django.test.Client` 또는 프로젝트가 이미 쓰는 동등한 Django client로 실제
URLconf에 mount된 endpoint를 호출한다. `ninja.testing.TestClient(router)`나
`ninja_extra.testing.TestClient(Controller)`로 미등록 Router/controller를 직접 감싼 결과는 공개
mount·registrar·middleware·URL prefix를 통과하지 않으므로 공개 HTTP 계약의 영구 증거가 아니다.

```python
from django.test import Client


def test_create_order_returns_201():
    client = Client()
    res = client.post(
        "/api/orders",  # 프로젝트 URLconf에 실제 mount된 경로
        {"product_id": 7, "quantity": 2},
        content_type="application/json",
    )
    assert res.status_code == 201
    assert res.json()["status"] == "created"
```

Framework 기본 401/403/404/422/429 body, Pydantic/Ninja 기본 직렬화, validator 배치,
`ValidationError.loc`, private/helper/handler 직접 호출은 그 자체로 test 자격이 아니다. 별도 승인된
공개 Python consumer 계약은 중앙 입장 심사를 통과하면 그 공개 boundary에서 테스트할 수 있지만,
그 근거가 없으면 오류 helper/handler 내부 unit test를 만들지 않는다. 승인된 공개 status/body/header,
wire Enum·security 계약을 실제 mount에서 검증하는 테스트까지 금지하는 규칙은 아니다.

### 9.2 검증 보고 기준

검증 보고에는 실제 실행한 명령이나 검토한 artifact만 쓴다.

- focused pytest path
- mounted Django client test run
- mounted API의 OpenAPI generation command 또는 generated document
- schema comparison artifact
- compatibility checklist

실행하지 않은 mounted client, pytest, OpenAPI, compatibility check는 `Not run`으로
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
- exception mapping과 선택한 오류 프로필 compatibility
- OpenAPI schema
- client deprecation/migration note

DRF-specific abstraction을 새 greenfield 표준으로 유지하지 않는다. 필요한 behavior는
Django Ninja Router/Schema, service validation, controller-owned 오류 변환, mounted Django client 검증으로
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
  error profile, header/content negotiation, pagination, versioning,
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
