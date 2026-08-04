---
name: implementation-django-ninja
description: Django Ninja JSON API 어댑터 구현 지식 — Router/Schema/Operation, controller-owned ErrorOut, registrar 합성, 인증·인가, 필터링·정렬·페이지네이션, Idempotency-Key, OpenAPI 계약 확인, TestClient HTTP 계약 검증, DRF-to-Ninja 마이그레이션. Router·Schema·API 어댑터 코드를 새로 작성하거나 리팩터링할 때 먼저 로드한다. REST 계약 설계는 architecture-api, 도메인 규칙·구조 패턴은 architecture-ddd, Django ORM·서비스·트랜잭션은 implementation-django, 테스트 픽스처·더블 구현은 implementation-test로 위임.
user-invocable: false
---

# Django Ninja JSON API 구현

## 언제 쓰나

Django Ninja Router/Schema/Operation·controller-owned ErrorOut·API registrar·인증·필터링·페이지네이션·OpenAPI·TestClient 코드를 설계·작성할 때 로드한다. 경계:

- REST 리소스·URL·HTTP 메서드·상태 코드·헤더·콘텐츠 협상·버전·레이트리밋·idempotency 계약(키 정책) → `architecture-api` (idempotency 저장소·retention은 `architecture-db`)
- 애그리거트·상태 전이·불변식·유스케이스 경계·구조 패턴(repository/UoW/핵사고날/CQRS/outbox/ACL) → `architecture-ddd`
- ORM 쿼리·셀렉터·서비스·트랜잭션·마이그레이션·캐시·보안 구현 → `implementation-django`
- pytest 픽스처·팩토리·mock·테스트더블·동시성 테스트 구현 → `implementation-test`

## 핵심 운영 원칙

- Router는 HTTP 어댑터로 얇게: 요청 바인딩·auth hook·서비스 호출·응답 매핑만 (§1.3)
- Request/Response schema는 명시적으로 분리, ModelSchema는 내부 구현 보호가 확실할 때만 (§3.1–§3.2)
- 발행 이벤트 봉투의 discriminator는 1종째부터 domain StrEnum + `Literal[EventType.X]` 파생(birth-enum), 버전 태그는 리터럴 동결, union-enum 동기 테스트 세트 (§3.1)
- dddjango는 공통 `ErrorOut` property를 정하지 않는다. `reuse`는 관찰된 exact shape를 보존한다. `create`와 `approved-change`는 신규 G1 slot 6에서 field/type/required/default/nullability/모든 `Field` metadata/model config·legacy `Config`/validator/serializer/computed field/Pydantic hook inventory와 effective semantics/wire 직렬화/field 의미 전체를 일반 G1과 분리해 명시 승인받는다. 공통 response 디렉터리는 빈 `__init__.py`와 `error_out.py`만 둔다. 승인된 common Schema의 Pydantic validator/serializer/decorator/hook은 보존 대상이며 아래 HTTP 오류 변환·handler 금지 대상이 아니다 (§6.2)
- 각 오류 BC는 `schema/error_out.py` 하나에 `<Bc>ErrorCode(StrEnum)`·`<Bc>ErrorOut`·no-arg concrete 오류를 둔다. BC/concrete는 공통 annotation/nullability·Field metadata를 보존하고, 추가 필드·validator·child model_config·URI/instance·다중 오류 schema 파일은 만들지 않는다 (§6.2)
- controller는 입력 준비 뒤 정확히 한 application call만 좁은 `try`에 두고 구체 known exception을 catch한다. concrete 오류를 준비해 `Status(<승인된 HTTP status 표현>, error)`로 직접 반환하고 성공 변환은 `try` 뒤에서 한다. `status` body property는 요구하지 않는다. 오류 tuple/raw Response·dict·helper/factory/ErrorOut→HTTP response serializer/mapper·exception handler/handler 등록 decorator·generic response builder는 금지한다 (§2.2·§6.2)
- 직접 반환하는 모든 BC 오류 status는 `response={...}`에 같은 BC base로 선언한다. framework-owned 401/403/route 404/422/429/일반 `HttpError`/미식별 500은 BC 오류로 변환·광고하지 않으며 body를 정확한 code-profile 계약이라 주장하지 않는다. 오류 선언의 `openapi_extra` 보충과 OpenAPI override·monkeypatch·postprocessor도 금지한다 (§6.2·§8)
- 프로젝트 `api.py`가 `NinjaExtraAPI` 하나를 소유하고, 명시 registrar가 소유하는 controller는 `@api_controller(..., auto_import=False)`로 auto-import/global registry side effect를 끈다. BC는 side-effect-free `register_<bc>_api(api)`를 노출하고 프로젝트 `urls.py`가 registrar를 명시 호출·mount하며, BC `composition_root.py`는 use-case DI만 소유한다 (§2.3)
- auth 실패는 `None` 또는 framework `AuthenticationError`이며 `request.auth`에 `ErrorOut`을 넣지 않는다. raw infra 실패는 기본 500이고, 승인된 안정 의미만 infra/ACL이 자기 BC exception으로 정규화한다 (§4·§6.2)
- 선언된 JSON 성공은 Schema/`Status`로 반환한다. `FileResponse`·`StreamingHttpResponse`·redirect·schema-less 204는 성공 native carveout이며 오류 응답 우회를 허용하지 않는다 (§2.2·§6.2)
- operation은 `summary`·`description`·`tags`로 문서화하고 반환 타입을 명시한다(`object` 금지) (§2.2)
- Idempotency-Key는 계약에 정의된 endpoint에만; 키 정책(scope·replay·conflict)은 `architecture-api`, 저장소·retention(테이블·unique constraint·fingerprint)은 `architecture-db`가 결정 (§7)
- 계약이 바뀌면 OpenAPI 생성 결과를 확인 (§8)
- 신규 API는 Django Ninja 목표, DRF는 legacy·migration 맥락에서만 보조 (§10)
- 신규 도입 시 Django Ninja를 의존성 매니페스트에 버전 핀으로 추가(글로벌 임의 설치 금지) — 핀 표기는 프로젝트 기존 관례 (§2.1)
- 라우팅 결정 전 계약·DB·도메인이 미결이면 각 소유 스킬 먼저 (§11)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| 책임 범위와 위임 경계·Router thinness 원칙 | §1 |
| Router 등록·Operation 선언 | §2 |
| Schema와 ModelSchema (request/response 분리·resolver) | §3 |
| 인증과 인가 | §4 |
| Filtering, sorting, pagination | §5 |
| 상태 코드와 controller-owned 오류 응답 | §6 |
| Idempotency-Key | §7 |
| OpenAPI | §8 |
| TestClient와 검증 | §9 |
| DRF-to-Ninja 마이그레이션 | §10 |
| 라우팅 기준(스킬 선택 결정 트리) | §11 |

각 절은 [`references/final.md`](references/final.md)에서 필요한 항목만 읽는다(전체 로드 불필요).
