---
name: implementation-django-ninja
description: >
  Use when the user asks to build Django Ninja APIs, create endpoints,
  write Schema/ModelSchema, add API auth, paginate/filter data, handle
  API errors, write async API views, or test API endpoints. Covers Router,
  Schema/ModelSchema, auth, pagination, FilterSchema, errors, throttling,
  async views, TestClient, and django-ninja-extra. Also use for DRF,
  Django REST Framework, Serializer, ModelSerializer, ViewSet, APIView,
  rest_framework, DefaultRouter, or SimpleRouter requests in this repo;
  those must be converted to Django Ninja Schema/Router instead of DRF.
  Also use for common API response standards, error response standards,
  exception handlers, and validation errors; the standard is RFC 9457 Problem
  Details with application/problem+json plus success envelopes using items
  and meta, not custom {"error": {...}} as the standard. DRF is not used. For Django core models/ORM/migrations/settings use
  implementation-django; for REST design use architecture-api.
---

# Django Ninja 컨벤션과 패턴

이 스킬은 Django Ninja를 사용한 API 구현 패턴을 다룬다.
Django 코어(모델, QuerySet, 마이그레이션, 설정)는 implementation-django에
위임한다. API 설계 원칙(REST, URL 설계, 상태 코드, 버저닝, 페이지네이션
전략)은 architecture-api에 위임한다. Python 전용 컨벤션(타입 힌트,
dataclasses, async)은 implementation-python에 위임한다. Django 웹 페이지
(템플릿, 정적 파일, 디자인 시스템)는 implementation-django-web에 위임한다.

**DRF(Django REST Framework)는 사용하지 않는다.** 모든 API 코드는
Django Ninja로 구현한다. DRF 코드(Serializer, ViewSet, APIView,
permission_classes)를 발견하면 Django Ninja 패턴으로 전환을 권고한다.

**API 응답 표준 low-freedom rule.** 사용자가 공통 에러 응답, API 응답 표준,
error standard, validation error, exception handler를 요청하면 반드시
RFC 9457 Problem Details와 `application/problem+json`을 사용한다.
`{"error": {"code": ..., "message": ...}}`를 표준안으로 제안하지 않는다.
응답 표준 요청에는 성공 목록 응답 예시도 함께 포함하고, 그 예시는 반드시
`items`와 `meta` 키를 가진다.
또한 첫 코드 블록에는 반드시 `from ninja import NinjaAPI, Router, Schema`,
`class ProblemDetail(Schema):`, `class ErrorCode(str, Enum):` 또는 동등한
에러 코드 Enum, `@api.exception_handler(...)`, 그리고
`response={400: ProblemDetail, 404: ProblemDetail, 409: ProblemDetail, 422: ProblemDetail}`
형태의 상태 코드별 응답 스키마 매핑을 포함한다. 예시 엔드포인트는
`router = Router()`, `@router.get(...)`, `api.add_router(...)` 구조로 쓴다.
`ProblemDetail`을 dict나 dataclass만으로 제시하지 않는다.

응답의 첫 30줄 안에는 반드시 다음 네 단어/표현이 모두 보여야 한다:
`Problem Details`, `application/problem+json`, `items`, `meta`.

**모호한 API 요청 가드.** 사용자가 Django, Django Ninja, Python 프로젝트라는
맥락을 명시하지 않고 "API 구조", "엔드포인트", "서비스 레이어"처럼 일반적인
질문만 하면 첫 문장을 반드시 "맥락이 불명확하므로 Django/Django Ninja
프로젝트라는 가정하에 답합니다." 또는 "프로젝트가 Django라면..."처럼 쓴다.
FastAPI, Flask, Node, Rust, SQL-only처럼 명확히 다른 기술이면 Django Ninja,
DDD, dddjango 관련 스킬 참조를 붙이지 않는다.

**DRF 요청 override — 낮은 자유도 규칙:** 사용자가 DRF를 명시적으로
요청해도 DRF 코드를 생성하지 않는다. `rest_framework`, `Serializer`,
`ModelSerializer`, `ViewSet`, `APIView`, `DefaultRouter`, `SimpleRouter`를
사용하지 않는다. 같은 기능을 Django Ninja Schema/Router로 전환한다.
응답 시작부에서 "이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로
작성합니다."라고 짧게 밝힌 뒤, Django Ninja 대안을 코드로 제시한다.
정책 확인 문장: 사용자가 DRF를 명시적으로 요청해도 DRF 코드를 생성하지 않는다.

**빈 workspace / read-only fallback.** 프로젝트 파일이 없거나 읽기 전용이라
파일 생성, 수정, 실행을 할 수 없어도 확인 질문으로 멈추지 않는다. 실행했다고
주장하지 않는다. 대신 합리적인 기본 가정(예: `products` 앱의 `Product`
모델)을 명시하고, 붙여 넣을 수 있는 Django Ninja 코드 예시를 제공한다:

1. `schemas.py` -- `Schema` 또는 `ModelSchema`.
2. `api.py` 또는 `router.py` -- `Router`와 HTTP 메서드 데코레이터.
3. `config/api.py` -- router 객체를 import해서 `NinjaAPI.add_router()`에
   넘기는 실제 합성 코드. 예:
   `from products.api import router as products_router`;
   `api.add_router("/products/", products_router)`. 문자열 경로를
   `api.add_router()`에 넘기지 않는다.
4. `config/urls.py` -- `path("api/", api.urls)`.
5. 실행하지 못했다는 검증 고지와 사용자가 실행할 명령. API 코드를
   제시했다면 최소한 `python manage.py check`와 `pytest` 또는
   `python manage.py test` 중 하나를 포함한다.

에러/응답 표준 fallback은 위 일반 파일 목록보다 우선한다. 이때 산출물에는
반드시 다음 두 조각이 모두 있어야 한다:
1. `ProblemDetail(Schema)` 코드, `problem_response()` 코드,
   `application/problem+json` content type, `@api.exception_handler(...)`.
2. 정상 목록 응답 envelope 예시:
   `{"items": [...], "meta": {"limit": 20, "offset": 0, "total": 100}}`.
3. `response={400: ProblemDetail, 404: ProblemDetail, 409: ProblemDetail, 422: ProblemDetail}`
   같은 상태 코드별 응답 스키마 매핑 예시.
4. `router = Router()`, `@router.get(...)`, `api.add_router(...)`를 포함한
   실제 Router 합성 예시.

**기준 요구사항 — 모든 모드에 적용:**
- 모든 요청/응답 검증에 Pydantic Schema를 사용한다. DRF Serializer를
  사용하지 않는다.
- 엔드포인트에 Router 데코레이터 패턴을 사용한다. ViewSet을 사용하지 않는다.
- 모든 엔드포인트 매개변수와 반환 타입에 타입 힌트가 필수다.
- sync 엔드포인트 첫 매개변수는 `request: HttpRequest`로 쓰고
  `from django.http import HttpRequest`를 import한다.
- Python 3.10+ 예시는 `list[Schema]`를 사용한다. `from typing import list`는
  존재하지 않는 import이므로 절대 작성하지 않는다. 레거시 Python만
  `from typing import List`와 `List[Schema]`를 사용한다.
- Django Ninja의 내장 인증 클래스를 사용한다. DRF의
  permission_classes나 authentication_classes를 사용하지 않는다.

아래 섹션에서 다루는 주제에 대해 작업할 때, 상세한 컨벤션과 코드 예제를
위해 연결된 참조 파일을 읽는다.

**참조 파일 로딩 규칙:**
- Writing 모드: 아래 주제와 관련된 코드를 생성하기 전에 해당 참조 파일을 먼저 읽는다.
- Review 모드: 리뷰 결과를 확정하기 전에 인용한 모든 컨벤션의 참조 파일을 읽는다.
- Refactoring 모드: 변경 사항을 제시하기 전에 적용한 각 패턴의 참조 파일을 읽는다.

## 응답 구조

모든 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.

ALWAYS use this exact template for the closing section:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **Writing**: 사용자가 API 코드 생성, 구현, 작성을 요청
- **Review**: 사용자가 기존 API 코드의 리뷰, 검토, 평가를 요청
- **Refactoring**: 사용자가 API 코드의 리팩토링, 개선, 현대화를 요청

의도가 모호한 경우 Writing 모드를 기본으로 한다.

요청이 여러 모드에 걸치는 경우(예: "리뷰하고 리팩토링해줘"),
Review를 먼저 적용한 후 같은 코드에 Refactoring을 적용한다.

### Writing 모드

모든 Django Ninja 컨벤션을 묵시적으로 적용한다. 컨벤션을 설명하는
인라인 주석 없이 관용적인 코드를 작성한다. 코드가 스스로 말하게 한다.
모든 엔드포인트 매개변수와 반환 타입에 항상 타입 힌트를 작성한다.

코드를 생성하기 전에 관련 주제 영역의 참조 파일을 읽는다.

사용자가 DRF, Django REST Framework, Serializer, ModelSerializer,
ViewSet, APIView, rest_framework, DefaultRouter, SimpleRouter를 요청하면
다음 절차를 반드시 따른다:

1. DRF 미사용 정책을 한 문장으로 밝힌다.
2. Serializer/ModelSerializer는 Django Ninja `Schema` 또는 `ModelSchema`로
   변환한다.
3. ViewSet/APIView는 `Router`와 `@router.get`, `@router.post`,
   `@router.put`, `@router.patch`, `@router.delete` 엔드포인트로 변환한다.
4. DRF router(DefaultRouter/SimpleRouter)는 `NinjaAPI.add_router()`와 앱별
   `Router()` 구성으로 변환한다.
5. DRF permission_classes/authentication_classes는 Django Ninja 인증 클래스
   또는 라우터/엔드포인트 `auth=` 설정으로 변환한다.
6. DRF import 예시는 제공하지 않는다. 필요한 경우 금지 예시는 코드가 아닌
   설명 문장으로만 언급한다.
7. 마지막에 검증 블록을 둔다. 실제 실행을 못 했으면 그렇게 밝히고,
   사용자가 실행할 `python manage.py check`와 `pytest`/`python manage.py test`
   명령을 제시한다.

적용할 핵심 컨벤션:

**Schema 설계.** 요청/응답 검증에 `Schema`를 사용한다. 모델 기반
스키마에 `Meta.fields`와 함께 `ModelSchema`를 사용한다. 계산 필드에
resolver 메서드(`resolve_<field>`)를 사용한다. PATCH 작업에 `PatchDict`를
사용한다. 모든 모델 필드를 노출하지 않는다 — 명시적이 더 좋다.

**라우팅.** 앱별로 `Router()`를 사용하고, `api.add_router()`로 합성한다.
데코레이터 패턴(`@router.get`, `@router.post`)을 사용한다. 하위 리소스
URL을 최대 3단계로 유지한다. 검증이 있는 URL 매개변수에 `Path(...)`를
사용한다.

**인증.** Django Ninja의 내장 인증 클래스(HttpBearer, APIKeyHeader,
SessionAuth)를 사용한다. 글로벌, 라우터, 또는 작업 수준에서 인증을
적용한다. 특정 엔드포인트를 면제하려면 `auth=None`을 사용한다.

**페이지네이션.** 내장 페이지네이터(LimitOffsetPagination,
PageNumberPagination, CursorPagination)와 함께 `@paginate` 데코레이터를
사용한다. `PaginationBase`를 확장하여 커스텀 페이지네이터를 생성한다.

**필터링.** 타입 안전한 필터링에 `FilterSchema`와 `FilterLookup`을
사용한다. 복잡한 필터에 표현식 커넥터(OR, AND)를 사용한다.
null 필터 값을 건너뛰려면 `ignore_none=True`를 사용한다.

**검색/목록 API 표준.** 팀 컨벤션 형태의 검색 API를 만들 때는
`FilterSchema`와 `Query[...]`로 query parameter를 구조화한다. 정렬 필드는 allow-list
또는 Enum으로 제한하고, 사용자 입력을 `order_by()`에 직접 넣지
않는다. 페이지네이션 응답은 팀 표준이 필요하면 `items/meta envelope`를
명시하고 직접 슬라이싱하거나 `PaginationBase`로 구현한다. @paginate와 커스텀 envelope를 섞지 않는다;
내장 `@paginate`를 쓰면 해당 paginator의 응답 형식을 그대로 따른다.
특히 커스텀 envelope를 반환하면서 `response=list[...]`로 선언하지 않는다.
`response=list[...]`는 plain list 응답일 때만 사용한다. 에러 응답은 항상
`RFC 9457 Problem Details`로 정의하고 실제 응답 `Content-Type` 또는 테스트
assertion에 `application/problem+json`을 포함한다.

**API 표준화 응답은 envelope까지 함께 제시한다.** 공통 API 표준, 에러 표준,
응답 포맷 표준을 설계할 때는 에러만 보여주지 말고 정상 목록 응답의
`items/meta` envelope 예시도 함께 포함한다. 예:
`{"items": [...], "meta": {"limit": 20, "offset": 0, "total": 100}}`.
Problem Details는 에러 전용이고, 목록/검색 성공 응답은 `items/meta`로
일관성을 맞춘다.
이 규칙은 선택 사항이 아니다. 에러 표준 응답에서 `Problem Details`,
`application/problem+json`, `items`, `meta` 네 단어가 모두 보여야 한다.

**에러 처리.** 커스텀 에러 응답에 `@api.exception_handler()`를 사용한다.
단순 에러에 `HttpError(status, message)`를 사용한다. 모든 API 에러에
RFC 9457 Problem Details 형식을 반환한다. Problem Details 응답은
`application/problem+json`으로 내려가도록 `create_response()` 또는 response
객체의 content type을 명시하고, 테스트에서 이를 검증한다.
공통 에러 표준을 작성할 때는 `from ninja import Schema`를 import하고
`class ProblemDetail(Schema)`를 직접 정의한다. 에러 응답 스키마는
엔드포인트의 `response={...}` 매핑에도 연결한다. 예시 endpoint는
`Router`에 붙이고 마지막에 `api.add_router()`로 합성한다.

**Django Ninja 테스트 작성.** `ninja.testing.TestClient` 또는
`TestAsyncClient` 예시를 제시할 때는 정상, 인증/권한 실패, validation 실패,
경계/엣지 케이스를 모두 포함한다. 목록 API면 pagination shape와 query count,
생성 API면 빈 items, 수량 0, 중복/멱등성, 재고 부족 같은 경계 조건을 최소
하나 이상 테스트한다.

**트랜잭션과 멱등성 실패 응답.** `transaction.atomic()` 안에서 재고 부족,
결제 실패 같은 실패 응답을 저장한 직후 예외를 다시 raise하면 rollback으로
저장한 실패 상태가 사라질 수 있다. 실패 상태를 멱등성 키에 남겨야 한다면
예외를 밖으로 전파하지 말고 저장 후 명시적 error result를 반환하거나,
실패 응답 저장을 rollback 영향을 받지 않는 별도 durable 경계에서 처리한다.

### Review 모드

잘 구조화된 Django Ninja 코드를 리뷰할 때는 개선 사항을 나열하기 전에
코드의 잘된 점을 먼저 언급한다. 품질이 낮은 코드를 리뷰할 때는
가장 영향력 있는 문제부터 집중한다.

각 발견 사항을 다음 형식으로 작성한다:

```
[Convention] -- 이것이 관용적 Django Ninja가 아닌 이유 설명
```

리뷰를 확정하기 전에 아래의 모든 항목을 확인한다. 누락된 항목은 사용자가 나중에 직접 발견해야 하므로 모두 확인한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] Django Ninja 대신 DRF 패턴 사용 (Serializer, ViewSet, APIView)
- [ ] 엔드포인트 매개변수 또는 반환 타입에 타입 힌트 누락
- [ ] 명시적 선택 없이 모든 모델 필드를 노출하는 Schema
- [ ] 인증이 필요한 엔드포인트에 인증 누락
- [ ] 목록 엔드포인트에 페이지네이션 없음
- [ ] 에러 처리 없음 또는 비표준 에러 형식
- [ ] async가 성능을 개선할 수 있는 sync 뷰
- [ ] 복잡한 필터링 로직에 FilterSchema 미사용
- [ ] 입력 검증 누락 (요청 본문에 Schema 없음)
- [ ] 너무 많은 일을 하는 엔드포인트 (분할하거나 서비스 레이어 사용 필요)

리뷰 결과를 확정하기 전에 인용한 모든 컨벤션의 참조 파일을 읽어
정확성을 확인한다.

### Refactoring 모드

리팩토링 시 변경 전/후를 보여주고 각 변경의 이유를 명시한다.
각 변경을 특정 컨벤션에 연결하여 근거를 추적 가능하게 한다.
각 변경을 다음 형식으로 작성한다:

```
[Before]
<원본 코드>

[After]
<개선된 코드>

[Reason] Convention -- 이것이 Django Ninja 모범 사례를 따르는 이유 설명
```

변경 사항을 제시하기 전에 아래의 모든 적용 가능한 개선을 적용한다. 적용 가능한 항목을 건너뛰면 사용자가 추가 리팩토링을 해야 하므로 모두 적용한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] DRF Serializer -> Django Ninja Schema로 변환
- [ ] DRF ViewSet -> Router + 데코레이터 엔드포인트로 변환
- [ ] DRF permission_classes -> Ninja 인증 클래스로 변환
- [ ] 타입 힌트 누락 -> 모든 매개변수와 반환에 추가
- [ ] 모든 필드를 가진 Schema -> 명시적 필드 목록으로 제한
- [ ] 페이지네이션 없음 -> @paginate 데코레이터 추가
- [ ] 커스텀 에러 형식 -> RFC 9457 Problem Details로 변환
- [ ] I/O가 있는 sync 엔드포인트 -> async로 변환
- [ ] 수동 필터링 -> FilterSchema로 변환
- [ ] Fat 엔드포인트 -> 서비스 레이어로 추출

변경 사항을 제시하기 전에 적용한 각 패턴의 참조 파일을 읽는다.

형식이 개선의 깊이를 제한하지 않도록 한다. 코드에 근본적인 재설계가
필요한 경우, 먼저 전체 재설계를 적용한 후 위의 형식으로 변경 사항을
제시한다.

---

## 1. Schema와 검증

요청/응답에 Schema. 모델 기반 자동 생성에 ModelSchema.
동적 스키마에 `create_schema()`. 계산 필드에 resolver 메서드.
PATCH 작업에 PatchDict. 데이터 변환에 필드 별칭.

> Reference: `references/schema-validation.md`

---

## 2. 인증과 보안

6개의 내장 인증 클래스: APIKeyQuery, APIKeyHeader, APIKeyCookie,
HttpBearer, HttpBasicAuth, SessionAuth. 글로벌/라우터/작업 수준 인증.
다중 인증기. CSRF 자동 관리. async 인증 지원.

> Reference: `references/authentication.md`

---

## 3. 라우팅과 구성

앱별 Router(), add_router() 합성. URL 매개변수 전파가 있는 중첩
라우터. 다중 NinjaAPI 인스턴스를 통한 API 버저닝.
권장 프로젝트 구조: 앱별 api.py.

> Reference: `references/routing.md`

---

## 4. 응답과 페이지네이션

상태 코드별 다중 응답 스키마. 빈 응답(204: None).
3개의 내장 페이지네이터. @paginate 데코레이터. PaginationBase를 통한
커스텀 페이지네이션. 대량 페이지네이션 적용을 위한 RouterPaginated.

> Reference: `references/response-pagination.md`

---

## 5. 입력 파싱과 필터링

Path/query/body 자동 감지. Form과 File 업로드 패턴.
FilterLookup 어노테이션을 가진 FilterSchema. 표현식 커넥터
(OR, AND, XOR). 커스텀 필터 메서드.

> Reference: `references/input-filtering.md`

---

## 6. 에러 처리와 쓰로틀링

내장 예외(HttpError, ValidationError). @exception_handler 데코레이터.
create_response()를 사용한 커스텀 에러 응답. 3개의 내장 쓰로틀러
(AnonRate, AuthRate, UserRate). 글로벌/라우터/작업 수준 쓰로틀링.

> Reference: `references/error-throttling.md`

---

## 7. Async 지원

네이티브 async def 뷰. ASGI 서버 요구사항. sync/async 혼합.
ORM async 패턴(sync_to_async, 네이티브 async ORM 4.1+).
지연 queryset 주의사항.

> Reference: `references/async-support.md`

---

## 8. 테스팅

TestClient(router)는 미들웨어를 우회한다. response.json() vs
response.data. 커스텀 요청 속성. 테스트에서의 사용자 인증.
async 뷰를 위한 TestAsyncClient.

> Reference: `references/testing.md`

---

## 9. 에코시스템

django-ninja-extra: 클래스 기반 뷰를 위한 @api_controller, 권한
시스템, 의존성 주입. JWT 인증을 위한 django-ninja-jwt.
자동 CRUD를 위한 모델 컨트롤러.

> Reference: `references/ecosystem.md`

---

## 응답 작성 직전 체크리스트 (필수)

### 공통
- [ ] DRF 사용 금지 (Serializer/ViewSet/permission_classes 발견 시 Ninja Schema/Router/내장 인증으로 전환)
- [ ] Schema에 fields 명시 (fields='__all__' 금지)
- [ ] 모든 매개변수/반환에 타입 힌트
- [ ] sync endpoint는 `request: HttpRequest`, return type, `from django.http import HttpRequest`
- [ ] `from typing import list` 금지. Python 3.10+는 `list[Schema]`, 레거시는 `List[Schema]`
- [ ] 에러는 RFC 9457 Problem Details (`application/problem+json`, HttpError + exception_handler)
- [ ] 공통 에러 표준 요청이면 `ProblemDetail(Schema)`와 `response={...: ProblemDetail}` 예시 포함
- [ ] 공통 에러 표준 예시도 `Router`, `@router.get/post`, `api.add_router()` 포함
- [ ] 비멱등 POST에 Idempotency-Key 헤더 또는 DB UNIQUE 제약 + IntegrityError 캐치
- [ ] `transaction.atomic()` 안에서 저장한 실패 응답이 rollback으로 사라지지 않게 처리

### 작성 모드
- [ ] **FilterSchema에 다중 필드 lookup (예: `title__icontains`, `department`, `grade`) 사용**
- [ ] **`response={201: SuccessSchema, 409: ProblemDetail, 422: ProblemDetail}` 다중 상태코드 응답 스키마 매핑**
- [ ] **검색/목록 API 표준 작성 시 `Query[FilterSchema]`, 정렬 allow-list, 페이지네이션 `items/meta envelope`, RFC 9457 에러 표준을 함께 제시. 커스텀 envelope면 `response=list[...]`를 쓰지 않음**

### 리뷰 모드
- [ ] N+1 가능성 있는 직렬화에 select_related/prefetch_related 권고
- [ ] 외부 I/O 많은 엔드포인트는 sync vs async 검토 권고
- [ ] [Convention: 요약] -- 상세 형식

### 리팩토링 모드
- [ ] 외부 I/O 많은 핸들러는 async def + httpx로 전환 검토
- [ ] [Before] / [After] / [Reason] 형식
- [ ] **fat endpoint를 service layer로 추출하고 [Reason]에 "비즈니스 로직 분리, endpoint는 HTTP 변환만" 명시**
- [ ] **`response={201: ..., 409: ..., 422: ...}` 다중 응답 스키마로 변환**
- [ ] **외부 I/O 많은 핸들러는 `async def` + `httpx.AsyncClient`로 sync→async 전환을 실제 코드로 제시 (검토 권고만이 아닌 실제 변환)**

### 잔여 디테일 정밀도 (회귀 방지 — 절대 누락 금지)

다음 3개 항목은 단순 lookup, 일반적인 fields 지적, "Router로 분리하세요"라는 표면적 권고로 회귀하기 쉽다. 반드시 아래의 정확한 형태로 작성한다.

- [ ] **작성 모드에서 FilterSchema는 단일 필드 단일 lookup(`title: str | None = FilterLookup("title__icontains")`)이 아니라 다중 필드/다중 lookup 형태로 정의: 예 `q: str | None = FilterLookup(["title__icontains", "description__icontains"])` 또는 `class XxxFilter(FilterSchema): title: str | None = Field(None, q="title__icontains"); department: str | None = None; grade: int | None = None` 처럼 여러 필드와 여러 lookup을 함께 명시. 단일 필드 단일 lookup만 작성하면 회귀.**
- [ ] **리뷰 모드에서 Schema의 비밀번호/이메일/주민번호/전화번호 등 민감 필드 노출 위험을 **별도 항목**으로 명시: "fields = '__all__' 또는 명시적 필드 목록에 password/hash/personal_id 등이 포함되어 있는지 — 응답 Schema에 노출되면 보안 사고로 이어짐. UserOutSchema와 UserInSchema를 분리하고 응답에서는 민감 필드를 제외할 것" 형식. "fields 명시" 일반 지적과 합치면 회귀.**
- [ ] **리팩토링 모드에서 NinjaAPI 합성을 권고할 때는 `config/api.py`에 실제 합성 코드 블록을 직접 제시: `from ninja import NinjaAPI; from apps.users.api import router as users_router; from apps.orders.api import router as orders_router; api = NinjaAPI(); api.add_router("/users/", users_router); api.add_router("/orders/", orders_router)` 형태. "Router로 분리하세요"라는 말만으로 끝내면 회귀.**
