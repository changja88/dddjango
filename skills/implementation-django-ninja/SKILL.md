---
name: implementation-django-ninja
description: >
  This skill should be used when the user asks to "build an API with
  Django Ninja", "create API endpoints", "write a Schema", "add API
  authentication", "paginate API results", "filter API data", "handle
  API errors", "write async views", "test API endpoints", or when any
  Django Ninja API code generation, review, or refactoring task occurs.
  Covers Django Ninja Schema/ModelSchema, Router, authentication
  (APIKey, Bearer, Session), pagination, FilterSchema, error handling,
  throttling, async views, testing with TestClient, and the
  django-ninja-extra ecosystem. Use this skill whenever Django Ninja
  API code is being written, reviewed, or refactored — even for
  seemingly simple tasks like adding an endpoint or defining a Schema.
  DRF(Django REST Framework) is NOT used — all API code uses Django
  Ninja. For Django core (models, ORM, migrations, settings), see
  implementation-django. For API design principles (REST, status
  codes, versioning), see architecture-api.
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

**기준 요구사항 — 모든 모드에 적용:**
- 모든 요청/응답 검증에 Pydantic Schema를 사용한다. DRF Serializer를
  사용하지 않는다.
- 엔드포인트에 Router 데코레이터 패턴을 사용한다. ViewSet을 사용하지 않는다.
- 모든 엔드포인트 매개변수와 반환 타입에 타입 힌트가 필수다.
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

**에러 처리.** 커스텀 에러 응답에 `@api.exception_handler()`를 사용한다.
단순 에러에 `HttpError(status, message)`를 사용한다. 모든 API 에러에
RFC 9457 Problem Details 형식을 반환한다.

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
