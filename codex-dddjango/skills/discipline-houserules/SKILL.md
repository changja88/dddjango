---
name: discipline-houserules
description: dddjango 플러그인 고유 하우스룰 — 생성 코드의 ①파일트리·디렉터리 구조·명명 규약(소스 레이아웃·테스트 의미군 분리·기존 규약 우선·평면 나열 방지·ORM/포트 클래스·파일 명명) ②타입 어노테이션 강제 수위(시그니처 필수·지역변수 권장) ③코드 주석·docstring 언어 규율. 코드를 어느 파일/디렉터리에 둘지·어떻게 타입을 달지·주석을 어느 언어로 쓸지 정하거나 검수할 때 로드한다. 새 모듈·테스트를 만들거나 프로젝트 레이아웃·코드 규약을 결정·점검하는 상황이면 반드시 사용. 보편 클린코드는 discipline-cleancode, Python 타입 지식은 implementation-python. 표준 파일트리는 references/final.md가 단일 출처이고, 그 배경 이론은 architecture-ddd(§6.1)·implementation-django(§3.1), 테스트 타입 조직은 implementation-test(§4.2)로 위임.
---

# 하우스룰 규율

## 무엇이고 왜

이 스킬은 **dddjango 플러그인이 만드는 코드에 한정된 집안 규칙(house rules)**이다. `discipline-cleancode`·`discipline-tdd`가 책에서 온 *보편* 규율인 것과 달리, 여기 담긴 것은 "우리는 이렇게 한다"는 **플러그인 고유의 권장·강제**다. 그래서 다른 스킬과 달리 책에서 온 외부 코퍼스가 없다 — 규칙은 이 SKILL.md 본문(§1~§6)이 곧이다. 그 토대인 **표준 파일트리는 배포 `references/final.md`가 단일 출처로 소유**하고, workspace/Codex reference는 corpus mirror tool이 동기화한다. (다른 스킬과 달리 이 SKILL.md는 `final.md`의 요약이 아니라, 규칙이 트리를 인용하는 형태다.)

첫 항목이자 토대는 **파일트리 구조**(§1~§3, 구체 트리는 `references/final.md`)다 — 프로젝트를 롱텀으로 유지하고 사람이 관리하기 쉽게 만드는 데 가장 중요하고, 규율로 강제하지 않으면 생성기가 "기존 평면 상태를 답습"하기 쉽다. 여기에 **타입 어노테이션**(§4)과 **주석·docstring 언어**(§5) 규율이 더해진다. 모두 결정(설계)·집행(구현)·점검(감수) 세 지점에서 공유된다.

경계:

- 코드 *내부* 구조(네이밍·함수 크기·SOLID) → `discipline-cleancode`
- DDD 계층·바운디드 컨텍스트 *이론* → `architecture-ddd` (§6.1 패키지 구조) — 표준 트리가 파생된 배경
- Django 프로젝트 *레이아웃 관용*·설정 분할 → `implementation-django` (§3.1)
- 테스트 *타입 조직*(unit/integration/e2e)·conftest 메커니즘 → `implementation-test` (§4.2)

이 스킬은 dddjango **표준 파일트리의 단일 출처**다(`references/final.md`). 그 트리는 위 코퍼스 레이아웃의 구체화·변종이고, 코퍼스는 *이론적 배경*으로만 인용한다(레이아웃 권위는 표준 문서). 프레임워크 구체(ORM·HTTP·conftest 등)는 위 구현 스킬로 위임한다.

## §1 파일트리 결정 순서

새 코드·테스트를 배치할 때 아래 순서를 따른다. 위에서 결론이 나면 멈춘다.

1. **기존 프로젝트 규약을 우선한다(일관성 최우선).** 대상 프로젝트에 이미 확립된 소스/테스트 배치가 있으면 그것을 따른다. 단, "존중"은 *확립된 규약을 따르는 것*이지 `startproject`/`startapp` 직후의 미조직 평면 상태를 답습하는 게 아니다. 기존이 `apps/<app>/` 규약이면 그 규약을, `src/<context>/` 계층이면 그 계층을 이어간다. **또한 *이번 작업이 touched(새 판정·불변식·쓰기 경로 적재)한* 데이터소스 앱의 루트 평면 배치는 — 이미 `Product` 모델·`0001` 마이그레이션이 있어도 — '확립된 규약'으로 보지 않는다(미조직 평면 답습과 동급).** **같은 원리로 *이번 작업이 touched한* published_service의 구 `read.py`/`write.py`·평면 구조·구 3파일형 contract(2026-07-07형 `request_contract.py` 등 계약 *모듈*)는 새 표면(서비스·공개 함수) 추가에 대한 '확립된 규약'으로 보지 않는다 — 새 표면은 신 구조(`references/final.md` §2 OHS 내부 구조 — 계약 3패키지·연산당 1파일)로 추가하고(3파일형 서비스에 새 연산 추가는 그 kind만 패키지로 부분 승격+⒝ 심 — §2 이주 조문), 기존 함수의 국소 수정은 미이주 허용이다(전면 이주는 §2 이주 조문·G1 트레이드오프).** 그 앱의 위치는 §0-1 `application/<app>/`다 — `architecture-ddd` §632-(2) 개정(2026-06-08)으로 데이터소스의 4계층/애그리거트 전개 면제는 폐지됐다: 면제는 *판정 실내용*(`.py` 코드)에만 남고 위치·4계층·개념 1차·종류 폴더 골격(빈 패키지)은 데이터소스도 무조건 실현한다(애그리거트명은 ORM 모델명 도출·유스케이스 없으면 `application_layer`만 빈 계층). 루트 평면 유지나 골격 생략이 필요하면 설계 명세에 박지 말고 G1 트레이드오프로 올린다. (§1.1 존중은 *프로젝트 전체 레이아웃 철학*과 *이번 작업이 안 건드린 무관 앱*에 적용된다.) **단 G1이 새/touched 범위에 code-profile을 선택하면 아래 오류 artifact와 HTTP 등록 owner/path는 주변 레이아웃과 무관하게 정확히 적용한다.** 프로젝트 `api.py`·`urls.py`, BC `presentation_layer/registrar.py`, use-case가 있는 BC의 BC-root `composition_root.py`, 공통/BC `error_out.py`를 rename·move·대체하지 않고, 기존 layout은 이 필수 경로 밖의 무관한 주변 디렉터리에만 유지한다. 옛 오류 계약·module-top-level 등록·오류 helper는 이미 승인된 legacy scope만 유지한다.
2. **확립된 규약이 없거나 미조직이면 dddjango 표준 파일트리를 적용한다(고정 기본값).** `references/final.md`가 단일 출처다 — `application/<app>/`의 4계층(`domain_layer`/`application_layer`/`infra_layer`/`presentation_layer`) 물리 분리, 개념(애그리거트/feature) 1차·종류 2차 조직, `infra_layer` 분할(`django_<app>`/`repository`/`acl`/`adapter` — 폴더는 항상 생성하고 `acl` 코드는 외부 컨텍스트 통합 시 채움), 컨텍스트 간 통신은 각 앱의 OHS(`published_service/`) 우선(내부는 서비스 1차 `<service>_service/`·contract 3패키지(request/response/exception_contract — request/response는 연산당 1파일 `<operation>_<kind>_contract.py`, exception은 base `<service>_published_error.py`+예외 클래스당 1모듈, folder-from-birth) — 공개 함수는 request contract 1개→response contract(또는 None) 반환·exception_contract 번역 예외만(3연조), 도메인 예외 재노출·published 계약 타입의 application_layer 관통 금지 — `references/final.md` §2 OHS 내부 구조)·직접 통합은 ACL(domain `port/`+infra `acl/`, 리포지토리와 분리)을 따른다. 이 표준은 `architecture-ddd` §6.1(4계층)과 `implementation-django` §3.1(설정 분할·앱 단위)을 구체화한 변종이며, 그 둘은 *이론적 배경*으로만 인용한다(레이아웃 권위는 표준 문서). 더 이상 lens로 §6.1 vs §3.1을 런타임에 택일하지 않는다. **표준을 적용할 때는 `references/final.md`를 반드시 읽고 그 §0 불변식을 따른다** — 아래는 YAGNI·단순성·"단일 앱이라 불필요"로 **생략·축소할 수 없는 골격**이다(트리를 읽지 않고 임의 축약 금지):
   - **`application/` 컨테이너** — 단일 앱이어도 `application/<app>/` 아래에 둔다.
   - **4계층 `_layer` 물리 분리** — `domain_layer`/`application_layer`/`infra_layer`/`presentation_layer`. 계층에 내용이 없어도(예: HTTP 표현 없는 내부 전용 BC의 `presentation_layer`) 폴더는 빈 패키지로라도 항상 생성하고 계층 자체를 생략하지 않는다(§0-2).
   - **개념 1차 폴더**(`<aggregate>/`·`<feature>/`) + **종류 2차 폴더 전체**(`entity`/`value_object`/`repository`/`command`/`dto`… — 비어도 폴더로 생성, 평면 파일 `repository.py`로 접지 않음).
   - **Django 앱은 `infra_layer/django_<app>/`에서 `startapp`** — `AppConfig.name`=점경로(`application.<app>.infra_layer.django_<app>`), `label='<app>'`; 앱 루트에 `models.py` 금지.
   - **ORM 모델 클래스명 `<Name>Model`**(도메인 엔티티/애그리거트는 bare `Order`).
   - **신규 ORM 모델 `db_table` 명시** — `<app_label>_<entity_snake>`(클래스 `<Name>Model`에서 `Model` 떼고 snake; `ProductModel`→`catalog_product`). app_label 접두 유지·신규만·`abstract`/`proxy`/`managed=False` 면제. 백스톱 `check-db-table.py`는 `db_table` *존재*만 강제(값 형태는 reviewer·`makemigrations --check`). 상세 `references/final.md` §4.
   - **리포지토리·포트 명명** — 추상화는 개념명+역할 접미사(`OrderRepository`·`ProductLockPort`·`PaymentGateway`; `Interface`/`Impl` 금지), 구현은 **확립 패턴명(`Repository`/`Gateway`)이면 패턴명 유지+기술 접두(`DjangoOrderRepository`·`StripePaymentGateway`), 일반 포트면 `…Port`→`…Adapter`로(`DjangoProductLockAdapter`)**. 파일명 약어 없이(`order_repository.py`). 상세 `references/final.md` §4. ⚠️ **`Django`+`ProductLockPort`(`Port`를 떼지 않고 붙여쓴 한 토큰)를 정답으로 쓰지 마라** — 개정 후 일반 포트 구현 정답은 `DjangoProductLockAdapter`다.
   - **응용 유스케이스 R/C/Q 명명** — `command/`=`…Command`(쓰기)·`query/`=`…Query`(읽기)·`dto/`=`@dataclass …Request`(입력)·`@dataclass …Result`(반환 — `<usecase>_result.py`, 소비처 불문), 모두 `execute(request)`·repository/port 의존. `…Command`=입력 DTO 아님(입력=`…Request`). 유스케이스 데이터 계약을 연산 모듈에 공개 dataclass로 인라인하지 않는다(§3 표 dto/ — `_` 사설 내부 스테이징(비반환·비수출)만 인라인 허용). 상세 `references/final.md` §4·어휘 노트.
   - **표현(presentation) 컨트롤러 명명** — ninja-extra 클래스 컨트롤러는 `<Aggregate>Controller`(예 `OrderController`)·파일 `<aggregate>_controller.py`(예 `order_controller.py`). 상세 `references/final.md` §4(함수형 Ninja `Router`는 레거시 병기).
   - **code-profile 오류 파일·명명** — `common/ninja/response/`는 빈 `__init__.py`+`error_out.py` 정확히 두 파일이다. plugin 기본 `ErrorOut` property는 없다. 기존 exact shape는 보존하고, 신규 exact shape 생성과 이후 shape 변경은 slot 6에 기록하되 일반 G1 승인과 분리된 사용자 명시 승인을 각각 받아야 한다. HTTP 오류를 직접 공개하는 각 BC는 `presentation_layer/schema/error_out.py` 정확히 하나에 snake_case BC명→PascalCase `<Bc>` 접두의 `<Bc>ErrorCode(StrEnum)` 하나, 승인된 식별자 field 하나만 좁히는 `<Bc>ErrorOut` 하나, concrete 전부를 둔다. BC base는 식별자의 annotation wrapper/nullability·required/default·Field metadata를 보존한다. concrete는 모든 기존 required field가 default라 no-arg로 만들고 새 필드·validator·child `model_config`·required 인자나 annotation/Field metadata drift를 추가하지 않는다. `Literal`/문자열로 Enum을 대신하거나 validation/retryable·사건별 파일을 만들지 않는다. 공개 오류가 없는 BC는 이 파일을 미리 만들지 않는다. 상세 `references/final.md` §1·§2·§4.
   - **HTTP 등록 네 소유자** — 프로젝트 `api.py`는 승인 contract scope당 API 인스턴스 하나만 소유하고 BC import·오류 매핑을 하지 않는다. 프로젝트 `urls.py`가 BC registrar를 명시 호출하고 API를 mount한다. BC `presentation_layer/registrar.py`는 project API를 import하지 않는 side-effect-free `register_<bc>_api(api)`로 자기 controller만 등록하며 함수 밖 등록을 하지 않는다(controller `auto_import=False`). BC 루트 `composition_root.py`는 use-case DI만 소유하고 API/controller 등록을 하지 않는다. 상세 `references/final.md` §2.
   - **오류 import·생성 경계** — domain/application/infra는 Django Ninja·HTTP response·공통/BC presentation `ErrorOut`에 의존하지 않고, 어떤 계층도 다른 BC `ErrorCode`/`ErrorOut`을 import하지 않는다. 협력 포트가 선언한 알려진 다른 BC domain/application 예외는 명시적 소비측 `infra_layer/acl/`만 import해 소비 BC 자신의 구체 exception으로 전수 번역하며 presentation/application direct catch는 금지다. 미승인 raw `OperationalError`·SDK/network 실패는 이 집합 밖이라 raw/framework 500이고, G1에서 안정된 공개 의미가 승인된 실패만 infra/ACL이 소비 BC 자신의 구체 exception으로 정규화한다. code-profile 오류 helper/factory/ErrorOut→HTTP response serializer/mapping/exception handler/handler 등록 decorator/global mapper는 **BC-local·공통 모두 만들거나 호출하지 않고**, 공유돼도 `common/` 승격 후보가 아니다. controller의 짧은 exception→concrete 매핑 반복을 허용한다. 인프라 예외 합성 금지. 승인된 common Schema의 Pydantic validator/serializer/decorator/hook은 보존 대상이며 HTTP 오류 변환·handler 금지 대상이 아니다. 상세 `references/final.md` §1·§2.
   - **오류 brownfield** — 관찰된 승인 status/body/header/media type과 기존 RFC 9457 compatibility를 보존하고 code-profile로 자동 이주·혼합하지 않는다. 새/touched 범위의 프로필·version·동시 rollout은 G1 결정이며, 기존 RFC 원인 사슬 보존은 그 compatibility 범위에서만 유지한다. 상세 `references/final.md` §1·§2.
   - **DI 컴포지션 루트(조건부)** — use-case·application 로직(command/query/service 등)을 가진 BC는 BC 루트 `composition_root.py`를 만들어 `build_<usecase>_command()`/`build_<usecase>_query()` 팩토리로 구체 infra를 매요청 주입하고 presentation은 호출만 한다(operation·application service 본문 직접 new-up 금지=Q-7 짝). 데이터소스 BC(빈 `application_layer`)는 생략. 상세 `references/final.md` §0 표·`implementation-django-ninja` 컴포지션 루트 절.
   - **상수·Enum 배치** — BC 내부 enum은 그 BC `domain_layer/` 소유(단일 출처; ORM `choices`·Schema는 파생·역참조 금지·`default=`는 `.value` 평탄화), 타 BC 직접 import 금지, `common/enum/` 승격은 공유 커널 결정(같은 지식 + 같은 변경 사유 근거)일 때만. 상세 `references/final.md` §1·`architecture-ddd` §2.5·§3.2·`implementation-django` §2.5.
3. **테스트는 의미군으로 분리한다(평면 나열 금지).** `test_*.py`를 한 디렉터리에 의미 구분 없이 쏟지 않는다. 최소한 unit/integration(/e2e 또는 그에 준하는 분류)으로 나눈다 — 테스트 타입 조직은 `implementation-test` §4.2가 단독 소유한다(`implementation-django` §3.1도 이를 §4.2에 위임). 표준 트리에서는 앱별 `application/<app>/test/{unit,integration,e2e}/`에 둔다(`references/final.md` §2; HTTP 엔드포인트 테스트는 `integration/`). factory_boy 팩토리는 그 앱의 `test/factories/`에 둔다(§2 — 의미군과 같은 레벨의 적법한 테스트 하위폴더). 기존 규약이 앱별 `tests/`면 그 *안에서* 의미군 하위 분리를 둔다.
4. **한 프로젝트 안에서 레이아웃을 혼용하지 않는다.** 한 번 택한 소스/테스트 레이아웃을 기능 전체에 일관 적용한다.

## §2 충돌 중재 (코퍼스가 어긋날 때)

코퍼스의 구조 규칙(`architecture-ddd` §6.1의 `src/<context>/` 4계층 ↔ `implementation-django` §3.1의 `apps/<app>/`)은 서로 다른 트리를 제시하지만, dddjango는 이 둘을 **런타임에 택일하지 않는다** — `references/final.md`가 단일 출처이고 §6.1/§3.1은 그 표준이 파생된 배경이다. 남는 변수는 §1.1(기존 프로젝트에 이미 확립된 규약)뿐이고, 그 경우 일관성을 위해 기존 규약을 따른다(표준을 그 위에 강제하지 않음).

- **테스트 타입 조직**(unit/integration/e2e 의미군)은 `implementation-test` §4.2가 단독 소유한다(§3.1도 §4.2에 위임). 표준 트리는 이를 앱별 `application/<app>/test/`에 적용한다(§1.3). 기존 규약이 있으면 그 `tests/` 위치를 따르되 내부는 의미군 분리.

## §3 평면 금지 레드 플래그

다음이 보이면 구조 결정이 빠졌거나 평면을 답습한 신호다.

- 새 모듈이 전부 한 디렉터리(예: 앱 루트)에 모여 도메인·인프라·인터페이스 구분이 없다.
- 종류 폴더(`entity`/`value_object`/`command`/`query`…)에 여러 애그리거트·feature의 파일이 개념 구분 없이 평면 누적된다(개념 1차 조직 누락 — `references/final.md` §2 "개념 1차·종류 2차"의 2차 레벨 위반).
- **`application/` 컨테이너 없이** 앱이 루트에 평면으로 놓인다(§0 불변식 1 위반).
- **종류 2차 폴더가 평면 파일로 접힘**(예: `repository/` 폴더 대신 `repository.py`) 또는 4계층 중 일부가 누락된다(§0 불변식 2·4 위반).
- **Django 앱이 `infra_layer/django_<app>/` 밖**에 있다(앱 루트에 `models.py`가 있거나 `startapp`을 루트에서 함 — §0 불변식 5 위반).
- **ORM 모델 클래스명이 `<Name>Model`이 아니다**(도메인 엔티티와 이름이 충돌 — §0 불변식 6 위반).
- **신규 ORM 모델에 `db_table` 누락 또는 `<app_label>_<entity_snake>` 불일치** — Django 기본값 `<app>_<name>model`의 `model` 군더더기를 방치(§4·§0 불변식 6 위반). `abstract`/`proxy`/`managed=False`·기존 적용 모델은 제외.
- **리포지토리·포트 명명 규약 위반** — 일반 포트 구현이 `…Adapter`가 아니거나(개정 후엔 일반 포트 구현이 `Port`를 유지하면 위반: `ProductLockPort`의 구현은 `DjangoProductLockAdapter`이지 `Django`+`ProductLockPort`가 아니다 — 구현에서 `Port`를 떼고 `Adapter`로 바꾼다) 개념 base명이 불일치하거나(`ProductLockPort`→`DjangoProductLock`처럼 개념 base 어긋남), 확립 패턴명(`Repository`/`Gateway`) 구현이 패턴명을 잃거나 기술 한정자(`Django…`/`Stripe…`/`InMemory…`/`Fake…`)가 누락되거나, 추상화(ABC)에 `Interface`/`Impl` 타입표식 접미사가 붙거나, 파일명을 약어로 줄인다(`order_repo.py`)(추상=개념명+역할 접미사·일반 포트 구현=`Adapter`·확립 패턴명 구현=패턴명 유지+한정자 접두 — `references/final.md` §4 명명 규약).
- **ACL/외부 컨텍스트 어댑터를 `repository/`에 섞음** — 다른 바운디드 컨텍스트를 번역·소비하는 ACL은 리포지토리가 아니다. domain은 `<aggregate>/port/`(협력 포트), infra는 `acl/`(어댑터)로 분리한다(컨텍스트 간 통신은 OHS `published_service` 우선 — `references/final.md` §2).
- **published_service 평면 `.py`·도메인 예외 재노출·계약 관통** — OHS는 서비스 폴더(`<service>_service/`) 없이 평면 모듈을 두지 않고(`__init__.py`·이주 조문의 ⒜ 구 read/write 재노출 심 제외), `__init__` 재노출 큐레이션을 하지 않으며(이주 조문의 ⒝ `<kind>_contract/__init__.py` 한시 재노출 심 제외), 도메인 예외를 번역 없이 전파·재노출하지 않으며(exception_contract가 단일 출처), published 계약 타입을 application_layer로 관통시키지 않는다(`references/final.md` §2 OHS 내부 구조·3연조).
- **오류 파일 family·helper 확장** — `common/ninja/response/`에 빈 `__init__.py`·`error_out.py` 외 파일/하위 scope를 임의 추가하거나, BC 오류를 사건별·validation/retryable 파일로 나누거나, BC-local/공통 오류 helper/handler/global mapper를 만들거나 호출·승격한다.
- **HTTP 합성 책임 혼합** — BC가 project API를 import하거나 module top-level에서 controller를 등록하고, `urls.py` 밖에서 registrar를 숨겨 호출하거나, `composition_root.py`가 API/controller 등록을 맡는다.
- **오류 계층 누수·raw infra 분류** — inner layer가 Ninja/HTTP/ErrorOut에 의존하거나 다른 BC ErrorCode/ErrorOut을 import하고, presentation/application이 타 BC exception을 직접 catch하거나 raw `OperationalError`를 global recognizer로 503/409에 분류한다.
- **brownfield 자동 이주** — 관찰·승인된 기존 오류 계약을 G1 결정 없이 새 code-profile로 바꾸거나 두 프로필을 한 scope에 섞는다.
- **command/query 연산 모듈에 공개 dataclass 인라인** — 유스케이스 반환·공유 데이터 계약이 `dto/`(반환 `<usecase>_result.py`·입력 `<usecase>_request.py`)를 이탈해 연산 파일에 정의되거나, `_` 사설 dataclass를 `execute()`가 반환한다(사설 위장 반환). 연산 모듈의 공개 표면은 연산 클래스뿐이다(`references/final.md` §3 표 dto/·§2 — 결정적 백스톱 `check-usecase-dto-placement` 집행; `_` 사설 내부 스테이징(비반환·비수출) 인라인과 `@dataclass class …Command` DI 필드 스타일 연산 클래스는 정당).
- `test_*.py`가 의미군(unit/integration/…) 없이 한 디렉터리에 평면으로 나열돼 있다.
- 인수 테스트와 단위 테스트가 같은 평면에 섞여 있다.
- `startproject`/`startapp` 직후의 미조직 구조를 그대로 이어 쓴다.
- 한 기능 안에서 `src/` 레이아웃과 `apps/` 레이아웃이 섞인다.

## §4 타입 어노테이션

함수·메서드 **시그니처(인자·반환 타입)는 필수**다. `implementation-python` §1·§23.1의 타입 어노테이션 일관 적용 원칙을 이 플러그인의 강제 규율로 못박는다. 프로덕션 코드는 mypy strict의 `disallow_untyped_defs`로 자동 강제되며, 타입 검사가 구성돼 있으면 검증 단계에서 실행해 확인한다. 구성돼 있지 않아도 코드는 시그니처 타입을 갖춰 쓴다(감수자가 점검). 단 **테스트 코드는 mypy strict가 `tests.*` override로 자동강제에서 면제**(§23.1)하므로, 테스트 함수 시그니처 누락은 강제가 아니라 권장(nit)으로 본다.

**모듈 레벨 변수와 클래스 변수의 타입 어노테이션은 필수**다 — 새 변수를 단순 대입(`name = expr`)으로 *처음* 바인딩하는 모듈 상수·클래스 본문 변수에 `name: T = expr`를 단다. 이들은 다른 코드가 import하고 독자가 계약으로 읽는 **공개 표면**이라 명시 효용이 높다. **함수 지역 변수는 권장**(필수 아님)이다 — 추론 자명한 곳까지 강제하면 노이즈만 늘고 mypy strict로도 자동 강제되지 않는다; 추론이 모호하거나 가독성에 도움이 될 때만 명시한다(감수자 nit). 주류(PEP 8·mypy·Google)는 추론 가능 지역 변수 어노테이션을 비권장하나, 이 플러그인은 **공개 표면에 한해** 결정성·일관성을 위해 명시를 의무화한다(근거 §4.1). mypy strict는 시그니처만 강제하므로 이 규칙은 백스톱(공개 표면 한정)과 감수자가 집행한다.

**합법 경로(누락이 위반이 아니다 — 강제하지 말 것):**

- 함수 지역 변수 (위 권장 — 의무 아님)
- 어노테이션 문법이 없는 곳: `for x in xs:`·`with f() as x:`·`except E as e:`·언패킹(`a, b = pair`)·다중 대입(`a = b = 0`)·증강 대입(`x += 1`)
- 재대입 (첫 바인딩에서 1회만 단다)
- 인스턴스 속성 `self.x = ...` (타입은 클래스 본문에 `x: T`로 선언)
- 프레임워크 선언: Django 모델 필드(`name = models.CharField(...)`)·`class Meta`/`Config` 옵션·enum 멤버(`RED = 1`) — 어노테이트하지 않는다(달면 ORM/enum 의미 오작동)
- RHS가 리터럴·컬렉션 상수가 *아닌* 경우: 호출식(`router = Router()`·`api = NinjaAPI()`·`api = NinjaExtraAPI()`)·타입 별칭(`= Union[...]`)·이름 참조(`router = make_router`) — 타입이 RHS·원본에서 자명하거나 관용 무어노테이션이다

**주의(면제 아님 — 어노테이션 필수)**: pydantic·django-ninja `Schema`·`dataclass` 필드는 `x: T`가 *반드시* 있어야 동작한다 — bare 대입이면 오히려 버그다.

공개 표면에서 검출 대상은 리터럴·컬렉션 상수(`= 3`·`= "..."`·`= [...]`·`= {...}`)의 첫 단순대입이며, 누락은 감수자가 important로 올린다(시그니처와 동급). 단 이 표준 문서군의 코드 예시는 개념 전달용 발췌라 이 규칙의 적용·감수 대상이 아니다(교육적 간결성 우선) — 규칙은 생성기가 산출하는 프로덕션 코드에만 건다.

### §4.1 왜 공개 표면을 의무화하나

이 의무의 실익은 버그-예방이 아니다 — mypy strict가 시그니처를 강제하면 호출 결과 변수의 타입은 대부분 추론되므로, 추론 자명한 변수에 어노테이션을 더해도 타입 안전은 거의 안 오른다. 실익은 **생성 결정성과 계약 가독성**이다. 모듈 상수·클래스 변수는 다른 모듈이 import하고 독자가 계약으로 읽는 공개 표면이라 타입 명시 효용이 높고, AST로 100% 판정돼 런마다 흔들리지 않는다(결정성). 함수 지역 변수는 함수에 갇혀 효용이 낮고 노이즈가 커 권장에 둔다. 이는 `implementation-python` §1의 "타입 어노테이션 일관 적용"을 공개 표면까지 결정적으로 명문화한 것이며(§1 산문과 충돌하지 않는다), 주류(PEP 8·mypy·Google)의 "추론 가능 지역 변수엔 비권장"과는 공개 표면 한정으로 갈린다 — 주류와 다른 선택임을 숨기지 않는다(출처 정직성).

## §5 코드 주석·docstring 언어

**기존 코드베이스의 주석 언어 관례를 우선한다.** 영어 주석이 지배적이면 영어로 맞춘다(일관성 최우선). 확립된 관례가 없으면 **한국어**로 쓴다(전역 지침: 주석·docstring은 한국어). 언어는 코드 동작이 아니라 사람의 유지보수를 위한 것이므로, 한 코드베이스 안에서 섞지 않는다.

## §6 패키지·의존성

### §6.1 부트스트랩·표준 도구셋

표준 도구셋(패키지 매니저 uv·ruff·mypy strict·django-stubs·pydantic·pytest)은 기능 추가 흐름이 **직접 다룬다** — 기존 프로젝트의 도구·패키지 매니저를 감지해 존중하고(§1.1 기존 존중), 기능에 필요한 표준 도구가 없으면 `implementation-django-ninja` §2.1 버전-핀 규율로 셋업한다(임의 글로벌 설치 금지). 현재 구체 셋업 레시피가 정의된 것은 **테스트 스택**이다(파이프라인이 acceptance 테스트 실행 전 러너를 준비한다 — `commands/dddjango.md` Phase 2·`implementation-test` §4); 나머지 도구도 같은 원칙(감지·존중·없으면 `implementation-django-ninja` §2.1 셋업)을 따르며 레시피는 필요 시 추가한다.

### §6.2 새 런타임 의존성의 버전 선택

기능에 새 런타임 의존성이 필요한데 그 패키지에 기존 제약이 없으면 (버전 *값* 규칙 — 핀 *표기*·매니페스트 위치는 `implementation-django-ninja` §2.1·`implementation-django` §3.1이 소유):

- **훈련 기억의 버전 번호를 적지 않는다.** 무핀 설치(`uv add <pkg>`/`pip install <pkg>`)로 받은 *실제 설치 버전*을 매니페스트에 핀한다. 무핀 설치는 *resolve 수단*일 뿐 **최종 상태는 핀**이다(핀을 안 박고 무핀으로 남기면 비결정이 영구화된다).
- **왜**: 기억 기반 버전은 모델 컷오프에 묶여 낡고, 런타임마다 달라 비결정적이다. resolve 후 핀은 실제 최신을 반영하고, 핀이 박힌 뒤 모든 설치는 결정적이다(비결정성을 최초 도입 1회로 격리 — 락파일 철학).
- **'최신'은 *기존 핀과 호환되는* 최신이다**(기존 존중 §1.1을 의존성 그래프로 확장). 무핀 resolve가 기존 프레임워크·핵심 의존성 핀(예: `Django==4.2`)을 올리려 들면 호환 한계 신호다 — 올리지 말고 기존 핀 안에서 가능한 최신을 핀하거나, 불가하면 보고한다(설계 반송).
- **안정 릴리스만 택한다.** resolve 결과가 pre/rc/dev면 핀하지 말고 보고한다. 직접 의존성만 매니페스트에 핀하고, 전이 의존성은 락파일에 맡긴다(이미 전이로 깔려 있으면 그 버전이 의도한 최신인지 확인).
- **막힌 환경**: 인덱스가 사설/제한적이면 그 인덱스의 최신을 핀하고, resolve 자체가 불가(오프라인·샌드박스)하면 기억값으로 채우지 말고 보고한다.
