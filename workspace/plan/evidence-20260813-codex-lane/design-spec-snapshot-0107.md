# billing BC — 통합 설계 명세 (클린룸 리빌드 라운드 2)

작성 역할: `dddjango-design-architect` · 활성 lens: `ddd`, `api`, `db`

정본 입력:

- 승인 스코프: `.dddjango/20260812-2037-billing-checkout/scope.md`
- 제품 요구: `docs/rebuild/billing/spec.md`
- 성공 OpenAPI 정본: `docs/rebuild/billing/api_shape_pre_success.json`
- 전체 OpenAPI 참고: `docs/rebuild/billing/api_shape_pre.json`
- 승인 이관 빚: `docs/rebuild/billing/legacy_debt.txt`

클린룸 제약: 과거 billing 구현·테스트와 Git 이력은 열람하지 않았다. 아래 테스트 오라클은 현재 `spec.md`에서만 도출했고, 현존 accounts/products/entitlements/framework 코드와 테스트는 협력 계약·중복 coverage 조사에만 사용했다.

---

## 0. 컨텍스트 · 설계 기준

- **BC 배치(스코프 고정)**: `application/billing`은 신규 독립 바운디드 컨텍스트다. 결제 원장, 0원 checkout 정책, 결제별 멱등성·발급 임차는 accounts/products/entitlements 어느 한 곳의 언어가 아니며 billing이 소유한다. 배치를 재결정하지 않는다.
- **유비쿼터스 언어**: `Payment(결제)`, `Checkout(구매 완결)`, `PaymentStatus(pending/succeeded/failed)`, `PaymentSnapshot(구매 시점 상품 스냅샷)`, `IdempotencyKey(멱등성 키)`, `RequestFingerprint(요청 지문)`, `FamilyCheckoutAdmission(가족 checkout 입장 판정)`, `EntitlementGrantProgress(권한 발급 진행)`, `EntitlementGrantStatus(unrecorded/recorded/already_entitled)`, `GrantClaim(발급 임차)`, `PaymentFailureReason(family_already_entitled)`를 billing 언어로 쓴다. 타 BC의 `Family`, `Product`, `Entitlement` 객체는 가져오지 않고 scalar ID와 billing 포트 결과만 쓴다(architecture-ddd §2.3·§2.4·§3.3 규칙3).
- **API stack**: 프로젝트 단일 `broccoli_server.api.api`(`BroccoliNinjaAPI`/`NinjaExtraAPI`)에 billing controller만 명시 등록한다. `PaymentController`는 `@api_controller(..., auto_import=False)`, `api_router.py`는 side-effect-free `register_billing_api(api)` 하나를 제공하고 URLconf가 이를 호출한다. 중앙 API instance 설정과 기존 BC의 import-time 등록은 이 delivery에서 바꾸지 않는다. 별도 API instance와 billing import-time registration은 금지한다.
- **error profile**: 이 scope는 승인대로 `dddjango-code-json`이다. current common `FrameworkErrorSchema`의 exact shape를 그대로 재사용하고 변경하지 않는다. 필드가 RFC 9457형 의미를 갖더라도 이 scope의 BC-owned direct `Status` 응답 media type은 profile 규칙대로 `application/json`이며 중앙 `problem_response()`를 통과하지 않는다.
- **Risky Write**: 결제·ledger·멱등성·가족 단위 동시성이므로 Risky Write다. §7.5의 8행 consistency block이 필수다.
- **도메인 이벤트**: 발행 0, 구독 0. entitlement 발급은 사실 방송이 아니라 checkout이 성공하기 위해 응답을 기다려야 하는 동기 지시다. outbox/broker/saga를 도입하지 않는다(architecture-ddd §3.7·§6.8).
- **현재 프로젝트 DB 엔진**: local/test/prod 모두 PostgreSQL(`broccoli_server/settings/local.py`, `broccoli_server/settings/test.py`, `broccoli_server/settings/prod.py`). SQLite는 지원·검증 대상이 아니며, SQLite `select_for_update` no-op을 전제로 한 설계를 만들지 않는다.

왜: 전략 경계를 먼저 고정하고, 결제의 원자성·복구 압력에 필요한 repository/UoW/ACL/CAS만 선택한다. paid-provider abstraction, event sourcing, provider gateway, webhook, refund/saga는 현재 요구가 없어 제외한다(architecture-ddd §6.8).

---

## 1. 패키지 · 테스트 구조

### 1.1 표준 트리 불변식

`discipline-houserules/references/final.md` §0·§1을 그대로 적용한다.

- 모든 BC는 내용 유무와 무관하게 표준 골격을 갖는다(#486).
- fixed/reappearing 폴더는 빈 경우에도 `__init__.py`, fixed 파일은 빈 파일로 실현한다(#488).
- `<...>` placeholder만 개념이 실제 생길 때 연다(#489).
- `application/billing/**`에 표준 밖 `utils/`, `common/`, `helpers/`, legacy `presentation_layer/`, `infra_layer/`, `published_service/`, `acl/`을 만들지 않는다(#490).
- BC 직계는 `composition_root`, `published_event`, `driving_layer`, `application_layer`, `domain_layer`, `driven_layer`, `test` 일곱 폴더뿐이다(#81).
- 테스트는 아래 입장 표에서 `add`된 artifact만 실현한다. 구조만을 이유로 case/assertion/helper를 만들지 않는다.

### 1.2 billing 구체 파일트리

아래는 표준 140행의 billing 인스턴스다. `∅`는 fixed/reappearing 골격만 존재하고 실내용이 없다는 뜻이다.

```text
application/billing/
  __init__.py
  composition_root/
    __init__.py
    dependency_wiring.py
      build_checkout_payment_use_case()
      build_process_operator_checkout_use_case()
    event_wiring.py                         ∅ (event 없음)
  published_event/
    __init__.py                             ∅
  driving_layer/
    __init__.py
    api/
      __init__.py
      api_router.py                         register_billing_api(api), side-effect-free
      bc_error_schema.py                    BillingErrorCode/BillingErrorSchema/concrete 11종
      webhook/
        __init__.py                         ∅
      payment/
        __init__.py
        payment_controller.py               PaymentController
        schema/
          __init__.py
          schema_in.py                      CheckoutPaymentIn
          schema_out.py                     PaymentOut/CheckoutPaymentOut
    open_host_service/
      __init__.py                           ∅ (다른 BC가 billing을 호출하는 공개 함수 없음)
    cron_job/
      __init__.py                           ∅ (worker/retry job 없음)
    event_subscription/
      __init__.py                           ∅
      event_router.py                       ∅
  application_layer/
    __init__.py
    payment/
      __init__.py
      checkout_payment/
        __init__.py
        checkout_payment_use_case.py        CheckoutPaymentUseCase
        checkout_payment_command.py         CheckoutPaymentCommand
        checkout_payment_query.py           ∅
        checkout_payment_result.py          CheckoutPaymentResult/PaymentResult
      process_operator_checkout/
        __init__.py
        process_operator_checkout_use_case.py
        process_operator_checkout_command.py
        process_operator_checkout_query.py  ∅
        process_operator_checkout_result.py
    port/
      __init__.py
      family_purchase_context/
        __init__.py
        family_purchase_context_port.py
        exception.py
        family_purchase_context_out.py
      purchasable_product_catalog/
        __init__.py
        purchasable_product_catalog_port.py
        exception.py
        purchasable_product_out.py
      entitlement_grant/
        __init__.py
        entitlement_grant_port.py
        exception.py
        entitlement_grant_in.py
        entitlement_grant_out.py
      checkout_clock/
        __init__.py
        checkout_clock_port.py
        exception.py                       ∅
      checkout_token/
        __init__.py
        checkout_token_port.py
        exception.py                       ∅
      domain_bypass_query/
        __init__.py                         ∅ (원장 읽기 API 없음)
      unit_of_work/
        __init__.py
        payment_checkout_unit_of_work.py    PaymentCheckoutUnitOfWork/BillingPersistenceFailure
  domain_layer/
    __init__.py
    payment/
      __init__.py
      payment.py                            Payment aggregate root
      payment_repository.py                 PaymentRepository
      entity/
        __init__.py
        entitlement_grant_progress.py       EntitlementGrantProgress
      value_object/
        __init__.py
        payment_status.py
        payment_failure_reason.py
        entitlement_grant_status.py
        payment_snapshot.py
        idempotency_key.py
        request_fingerprint.py
        grant_claim.py
      event/
        __init__.py                         ∅
      exception/
        __init__.py
        invalid_payment.py
        invalid_payment_transition.py
        family_owner_required.py
        family_required.py
        product_not_found.py
        product_not_purchasable.py
        paid_checkout_not_supported.py
        idempotency_key_required.py
        idempotency_key_conflict.py
        idempotency_key_in_progress.py
        family_checkout_in_progress.py
        family_already_entitled.py
        entitlement_unavailable.py
        payment_state_corrupted.py
        grant_claim_conflict.py
    shared_value_object/
      __init__.py                           ∅
    domain_service/
      __init__.py
      family_checkout_admission_policy.py   FamilyCheckoutAdmissionPolicy
  driven_layer/
    __init__.py
    django_billing/
      __init__.py
      apps.py                               DjangoBillingConfig
      models/
        __init__.py
        payment_model.py                    PaymentModel
        entitlement_grant_progress_model.py EntitlementGrantProgressModel
      migrations/
        __init__.py
        0001_initial.py                     makemigrations 생성물
      admin/
        __init__.py
        payment/
          __init__.py
          panel.py                          PaymentAdmin
          form/
            __init__.py
            checkout_form.py                OperatorCheckoutForm
          feature/
            __init__.py
            checkout.py                     operator checkout admin view
      templates/
        admin/billing/checkout.html
    adapter/
      __init__.py
      persistence/
        __init__.py
        repository/
          __init__.py
          payment_repository.py             DjangoPaymentRepository
        domain_bypass_query/
          __init__.py                       ∅
        unit_of_work/
          __init__.py
          payment_checkout_unit_of_work.py  DjangoPaymentCheckoutUnitOfWork
      anticorruption_layer/
        __init__.py
        accounts/
          __init__.py
          family_purchase_context_adapter.py AccountsFamilyPurchaseContextAdapter
        products/
          __init__.py
          purchasable_product_catalog_adapter.py ProductsPurchasableProductCatalogAdapter
        entitlements/
          __init__.py
          entitlement_grant_adapter.py       EntitlementsGrantAdapter
      external_system/
        __init__.py                         ∅ (PG/provider 없음)
      checkout_clock/
        __init__.py
        postgresql_adapter.py               PostgresCheckoutClockAdapter
      checkout_token/
        __init__.py
        secrets_adapter.py                  SecretsCheckoutTokenAdapter
  test/
    __init__.py
    unit/
      __init__.py
      domain/
        __init__.py
        test_payment.py
        test_payment_corruption.py
        test_idempotency_key.py
        test_family_checkout_admission_policy.py
        test_entitlement_grant_progress.py
      application/
        __init__.py
        test_checkout_payment_use_case.py
        test_process_operator_checkout_use_case.py
      adapter/
        __init__.py
        test_accounts_family_purchase_context_adapter.py
        test_products_purchasable_product_catalog_adapter.py
        test_entitlements_grant_adapter.py
    integration/
      __init__.py
      repository/
        __init__.py
        test_django_payment_repository.py
        test_payment_constraints.py
        test_payment_checkout_unit_of_work.py
      concurrency/
        __init__.py
        test_billing_checkout_concurrency.py
      api/
        __init__.py
        test_payment_controller.py
        test_payment_checkout_openapi.py
      admin/
        __init__.py
        test_payment_admin.py
    e2e/
      __init__.py
      conftest.py                           self-contained public HTTP/admin fixtures
      test_payment_checkout_acceptance.py   billing implementation import/patch 0
    factories/
      __init__.py
      payment_factory.py                    billing ORM integration 전용
      entitlement_grant_progress_factory.py billing ORM integration 전용
    fake/
      __init__.py
      checkout_ports.py                     승인 use-case port fake

framework/                                  현존 전역 컨테이너; billing 전용 복제 없음
broccoli_server/
  api.py                                    READ ONLY; diff 0
  urls.py                                   billing import/call 2곳만
  settings/base.py                          DjangoBillingConfig 등록
```

표현은 `POST /v1/payments`와 admin surface가 실제 존재하므로 `driving_layer`/admin을 빈 골격으로 둘 수 없다. OHS·webhook·cron·event subscription·published event는 scope에 없어서 빈 골격이다. `domain_bypass_query`는 payment list/detail API가 없어 채택하지 않는다. `<...>` placeholder가 열리지 않은 자리에 임의 in/out 파일을 만들지 않는다(#489). 반대로 열린 use-case의 command/query/result, API schema, event router 같은 fixed/reappearing 파일은 쓰지 않아도 모두 존재한다(#488).

`checkout_payment_exception.py`와 `application_layer/port/unit_of_work/exception.py`는 표준 트리에 없는 칸이므로 만들지 않는다(#490). Controller-facing checkout 업무 거절은 `domain_layer/payment/exception/<exception>.py`, UoW/DB mechanism failure인 `BillingPersistenceFailure`는 표준 UoW 계약 파일 `payment_checkout_unit_of_work.py`가 소유한다. `templates/admin/billing/checkout.html`도 트리 87행의 exact owner다. 이 세 결정은 현재 provisional acceptance artifact의 잘못된 private import를 정당화하지 않으며 §10에서 테스트 소유를 바로잡는다.

위 closed inventory는 `application/billing` 아래 **158 files**다: production 123(그중 package marker 51, HTML template 1), test 35(그중 package marker 13). 따라서 `__init__.py` 64 + 그 밖 Python module 93 + template 1이다. Project edit는 §8의 settings/URLconf 2 files뿐이며 `broccoli_server/api.py` edit count는 0이다.

### 1.3 명명 · import 방향 · Django app

- Django app: `DjangoBillingConfig`, `name="application.billing.driven_layer.django_billing"`, `label="billing"`, `default_auto_field="django.db.models.BigAutoField"`, `verbose_name="Billing"`. `ready()`는 없다.
- ORM은 `<Entity>Model`: `PaymentModel`, `EntitlementGrantProgressModel`; `db_table`은 `billing_payment`, `billing_entitlement_grant_progress`.
- aggregate repository 계약은 `domain_layer/payment/payment_repository.py`의 `PaymentRepository`; 구현은 `DjangoPaymentRepository`. `Interface`/`Impl` 접미사와 파일명 약어를 쓰지 않는다.
- 비애그리거트 협력 포트는 `application_layer/port/<capability>/<capability>_port.py`; ACL 구현은 `driven_layer/adapter/anticorruption_layer/<upstream>/..._adapter.py`다.
- use case는 공개 class 하나와 `execute(command) -> result`; 경계 자료에 `dto`라는 이름을 쓰지 않는다. controller/admin은 result의 원시 자료만 본다.
- controller가 매핑하는 구체 checkout 업무 예외는 billing `domain_layer/payment/exception/**`만 import한다. 타 BC 예외는 ACL에서 billing 예외로 번역하고 driving layer로 누수하지 않는다.
- 모든 타 BC 참조는 positive int64 scalar ID다. billing ORM에서 accounts/products/entitlements 모델로 `ForeignKey`/`OneToOneField`/`ManyToManyField`를 만들지 않는다.
- 기존 주석 관례가 한국어 중심이므로 생성 코드의 주석/docstring도 한국어로 맞춘다.


## 2. Error response contract

### 2.1 계약 범위 · 소유

- API instance는 현존 `broccoli_server.api.api` 하나다. Billing이 추가하는 공개 JSON surface는 legacy `path("v1/", legacy_api_urls)` 아래 `POST /v1/payments` 하나뿐이고 별도 `/api/v1` mount나 API instance는 없다.
- billing registrar/controller/error artifact는 각각 `application/billing/driving_layer/api/api_router.py`, `payment/payment_controller.py`, `bc_error_schema.py`다.
- 공통 framework 오류 shape와 handler의 canonical owner는 현행 `framework/ninja/framework_error_schema.py`, `framework/ninja/framework_validation_error_schema.py`, `broccoli_server/api.py`다. 모두 read-only이며 `broccoli_server/api.py` diff는 0이다.
- current project-wide registrar/controller/error inventory는 기존 legacy composition을 이해하기 위한 read-only evidence다. 이 delivery의 change target이나 정리할 debt가 아니다. 다른 BC의 파일·테스트·등록 순서·오류 mapping은 변경하지 않는다.
- 부모 인증은 승인된 current surface `application/accounts/presentation_layer/authentication.py::ParentAuth/authed_parent_id`를 사용한다. 이 billing outbound import만 `docs/rebuild/billing/legacy_debt.txt`가 이미 승인한다. Accounts 파일 자체는 수정하지 않는다.

### 2.2 Error profile · common shape

Billing BC-owned 오류는 승인된 `dddjango-code-json` profile이다. `FrameworkErrorSchema`의 공통 필드 의미는 재사용하지만 controller가 concrete schema를 direct `Status`로 반환하므로 media type은 `application/json`이다. Framework-owned 400/401/validation 422/500/503은 current central handler가 계속 `application/problem+json`으로 소유한다.

`FrameworkErrorSchema`는 변경 없이 아래 exact shape를 재사용한다.

- `type: str = "about:blank"`, `title: str`, `status: int`, `detail: str`
- `instance: str | None = None`, `retryable: bool | None = None`
- billing wire serialization은 `by_alias=True`, `exclude_none=True`; 선언 밖 property는 없다.
- `FrameworkValidationErrorSchema`의 `invalid-params` alias도 현행 그대로다.

### 2.3 Billing error module

`application/billing/driving_layer/api/bc_error_schema.py`는 import side effect가 없고 common schema와 `StrEnum`/`Literal`만 사용한다.

`BillingErrorCode(StrEnum)` 값은 다음 11개 full URI다.

```text
FAMILY_OWNER_REQUIRED          = https://broccoli.app/problems/family-owner-required
FAMILY_REQUIRED                = https://broccoli.app/problems/family-required
PRODUCT_NOT_FOUND              = https://broccoli.app/problems/product-not-found
PRODUCT_NOT_PURCHASABLE        = https://broccoli.app/problems/product-not-purchasable
PAID_CHECKOUT_NOT_SUPPORTED    = https://broccoli.app/problems/paid-checkout-not-supported
IDEMPOTENCY_KEY_REQUIRED       = https://broccoli.app/problems/idempotency-key-required
IDEMPOTENCY_KEY_CONFLICT       = https://broccoli.app/problems/idempotency-key-conflict
IDEMPOTENCY_KEY_IN_PROGRESS    = https://broccoli.app/problems/idempotency-key-in-progress
FAMILY_CHECKOUT_IN_PROGRESS    = https://broccoli.app/problems/family-checkout-in-progress
FAMILY_ALREADY_ENTITLED        = https://broccoli.app/problems/family-already-entitled
ENTITLEMENT_UNAVAILABLE        = https://broccoli.app/problems/entitlement-unavailable
```

- `BillingErrorSchema(FrameworkErrorSchema)`는 `type: BillingErrorCode`만 좁힌다.
- concrete no-arg schema 11개는 `type/title/status/detail`을 literal default로 고정하고 계약이 지정한 경우에만 `retryable` literal을 둔다.
- class names는 `FamilyOwnerRequiredErrorSchema`, `FamilyRequiredErrorSchema`, `ProductNotFoundErrorSchema`, `ProductNotPurchasableErrorSchema`, `PaidCheckoutNotSupportedErrorSchema`, `IdempotencyKeyRequiredErrorSchema`, `IdempotencyKeyConflictErrorSchema`, `IdempotencyKeyInProgressErrorSchema`, `FamilyCheckoutInProgressErrorSchema`, `FamilyAlreadyEntitledErrorSchema`, `EntitlementUnavailableErrorSchema`다.
- `Billing409ErrorSchema`는 409 concrete 5종 union, `Billing422ErrorSchema`는 422 concrete 3종 union이다. Base 하나로 literal을 소실하지 않는다.

### 2.4 준비된 오류 mapping

| billing domain failure | output schema | HTTP | exact title / detail / retryable | conditional headers |
|---|---|---:|---|---|
| `CheckoutFamilyOwnerRequired` | `FamilyOwnerRequiredErrorSchema()` | 403 | `가족 소유자 전용` / `가족 소유자만 상품을 구매할 수 있습니다.` / omitted | none |
| `CheckoutFamilyRequired` | `FamilyRequiredErrorSchema()` | 409 | `가족 필요` / `결제하려면 먼저 가족이 필요합니다.` / omitted | none |
| `CheckoutProductNotFound` | `ProductNotFoundErrorSchema()` | 404 | `상품 없음` / `상품을 찾을 수 없습니다.` / omitted | none |
| `CheckoutProductNotPurchasable` | `ProductNotPurchasableErrorSchema()` | 409 | `판매 중인 상품 아님` / `현재 판매 중인 상품이 아닙니다.` / omitted | none |
| `PaidCheckoutNotSupported` | `PaidCheckoutNotSupportedErrorSchema()` | 422 | `유료 결제 미지원` / `무료 상품만 결제할 수 있습니다.` / `false` | none |
| `CheckoutIdempotencyKeyRequired` | `IdempotencyKeyRequiredErrorSchema()` | 422 | `멱등성 키 필요` / `Idempotency-Key 헤더가 필요합니다.` / omitted | none |
| `CheckoutIdempotencyKeyConflict` | `IdempotencyKeyConflictErrorSchema()` | 422 | `멱등성 키 충돌` / `Idempotency-Key 지문이 일치하지 않습니다.` / omitted | none |
| `CheckoutIdempotencyKeyInProgress` | `IdempotencyKeyInProgressErrorSchema()` | 409 | `멱등성 요청 처리 중` / `원래 요청을 아직 처리하고 있습니다.` / `true` | `Retry-After: 1` |
| `CheckoutFamilyInProgress` | `FamilyCheckoutInProgressErrorSchema()` | 409 | `가족 결제 처리 중` / `이 가족의 다른 결제가 처리 중입니다.` / `true` | none |
| `CheckoutFamilyAlreadyEntitled(replayed=False)` | `FamilyAlreadyEntitledErrorSchema()` | 409 | `이미 사용 권한 보유` / `이미 사용 권한을 보유한 가족입니다.` / `false` | none |
| `CheckoutFamilyAlreadyEntitled(replayed=True)` | same | 409 | same | `Idempotency-Replayed: true` |
| `CheckoutEntitlementUnavailable` | `EntitlementUnavailableErrorSchema()` | 503 | `권한 발급 일시 실패` / `권한 발급을 일시적으로 사용할 수 없습니다. 같은 Idempotency-Key로 다시 시도해 주세요.` / `true` | `Retry-After: 1` |

위 failure는 `domain_layer/payment/exception/<exception>.py`가 한 종류씩 소유한다. Accounts/products/entitlements contract exception은 각 ACL adapter가 이 billing 업무 실패로 번역한다. 알 수 없는 DB/contract/corruption/permanent grant failure는 준비된 BC schema가 없고 framework 500으로 흐른다. UoW adapter의 raw `OperationalError`는 cause를 보존한 `BillingPersistenceFailure`로 감싸므로 중앙 DB-message 503 recognizer에 잘못 분류되지 않는다.

### 2.5 Controller mapping

- `PaymentController`는 `@api_controller(..., auto_import=False)`다. 부모 ID, raw `Idempotency-Key`, payload→command 준비, use-case factory 호출은 narrow try 밖이다.
- try 안은 정확히 `use_case.execute(command)` 한 문장이다. §2.4 concrete billing domain failure만 catch하고 catch-all은 없다.
- 각 catch는 concrete no-arg schema를 만들고 필요한 header를 temporal `HttpResponse`에 설정한 뒤 `Status(<literal>, error)`를 직접 반환한다.
- success는 `CheckoutPaymentOut.from_result`와 `Idempotency-Replayed: "true"|"false"`를 설정한 뒤 `Status(201, out)`을 반환한다.
- application/domain은 HTTP status, media type, response header를 모른다. 저장하는 것은 immutable payment snapshot과 billing outcome뿐이다.

### 2.6 Runtime/OpenAPI 계약

| HTTP | owner/schema candidate | media type | response headers |
|---:|---|---|---|
| 201 | `CheckoutPaymentOut` | `application/json` | `Idempotency-Replayed` required, enum `false|true` |
| 400 | framework `FrameworkErrorSchema` | `application/problem+json` | none |
| 401 | framework `FrameworkErrorSchema` | `application/problem+json` | `WWW-Authenticate` required, runtime `Bearer` |
| 403 | `FamilyOwnerRequiredErrorSchema` | `application/json` | none |
| 404 | `ProductNotFoundErrorSchema` | `application/json` | none |
| 409 | `Billing409ErrorSchema` | `application/json` | `Idempotency-Replayed`/`Retry-After` optional by branch |
| 422 | `Billing422ErrorSchema` / framework validation schema | `application/json` / `application/problem+json` | none |
| 500 | framework `FrameworkErrorSchema` | `application/problem+json` | none |
| 503 | `EntitlementUnavailableErrorSchema` / framework schema | `application/json` / `application/problem+json` | response-level `Retry-After` optional; billing branch runtime `1` |

- operation은 `POST /v1/payments`, auth `ParentAuth()`, `by_alias=True`, `exclude_none=True`다.
- `Idempotency-Key`는 raw header로 읽고 operation metadata에 required/min 1/max 128/pattern `^[\x21-\x7E]{1,128}$`를 문서화한다.
- 201 body/header/security는 `docs/rebuild/billing/api_shape_pre_success.json`과 normalized diff 0이다. 공개 ID는 integer/int64, minimum 1, maximum `9223372036854775807`다.
- Error OpenAPI는 11 literal을 concrete ref/union으로 보존하고 같은 status의 billing/framework media를 분리한다.

### 2.7 Compatibility · rollout

신규 endpoint/admin/table이므로 기존 billing consumer/data migration은 없다. Accounts/products/entitlements/framework public contract와 current legacy URL set은 변하지 않는다. Billing registrar를 first `api.urls` access 전에 한 번 호출하는 §8의 두-line URLconf wiring만 추가하고 중앙 API·공통 error handler·기존 registrar에는 손대지 않는다. 테스트 소유와 public/private seam은 §10이 고정한다.


## 3. 도메인 설계 (ddd lens)

### 3.1 Payment aggregate 경계

`Payment` 한 애그리거트가 immutable ledger root와 그 결제의 `EntitlementGrantProgress` entity를 소유한다.

- `Payment` root: ID, purchaser parent ID, family ID, `PaymentSnapshot`, idempotency digest, request fingerprint, status, failure reason, created/succeeded/failed timestamps.
- `PaymentSnapshot`: product ID, trimmed product name, amount KRW, daily/weekly token limit, payment method(None). 구매 뒤 upstream Product가 변경/삭제돼도 바뀌지 않는다.
- `EntitlementGrantProgress`: succeeded payment에만 존재. insert-only family ID, `EntitlementGrantStatus`, entitlement ID(optional), current `GrantClaim`(optional), optimistic version을 소유한다. application/repository가 이 entity를 독립 변경·저장하지 않는다.
- ledger root row와 snapshot/terminal fields는 insert 뒤 갱신하지 않는다. 임차·entitlement 기록만 progress entity/table에서 CAS 갱신한다. 왜: 회복을 위해 mutable coordination은 필요하지만 결제 원장 자체의 시간적 불변성과 섞지 않는다.
- 같은 aggregate 내부 `PaymentModel`↔`EntitlementGrantProgressModel` OneToOne FK는 허용한다. 타 BC FK는 금지한다.

### 3.2 가족 checkout 입장 판정

- `FamilyCheckoutAdmissionPolicy`는 여러 `Payment`에 걸친 **가족당 진행 checkout 최대 1** 규칙을 소유하는 무상태 domain service다. 입력은 candidate의 payment/key 식별과 repository가 조회한 `ActiveFamilyCheckout(payment_id,key_digest,claim_expires_at)` 사실뿐이며 ORM/constraint exception을 알지 않는다.
- `decide(candidate, active, now)` 결과는 `ADMIT_NEW`, `RESUME_SAME_PAYMENT`, `REJECT_OTHER_PAYMENT`의 닫힌 domain result다. active 없음은 admit, 같은 persisted payment/key는 root replay/resume로 위임, 다른 payment/key는 claim 만료 여부와 무관하게 `REJECT_OTHER_PAYMENT`다. 만료는 소유 key가 resume할 수 있다는 뜻이지 새 key가 ledger를 탈취한다는 뜻이 아니다.
- 정상 생성 경로는 UoW A에서 active 사실을 조회해 이 policy를 **partial unique insert 전에 호출**한다. `uniq_bill_active_family` 경합 뒤에도 loser가 winner를 재조회해 같은 policy를 다시 호출한 뒤 `CheckoutFamilyInProgress`로 번역한다. SQL/constraint 예외 자체가 가족 규칙을 판정하지 않는다.
- 왜: 이 규칙은 여러 Payment root를 가로질러 단일 root에 넣을 수 없지만 billing의 업무 판정이다. domain service가 정상/경합 경로의 의미를 한 곳에서 소유하고 partial unique는 최종 race guard만 담당한다(architecture-ddd §3.2·§3.5, architecture-db §9.5).

### 3.3 값 · 상태 · 전이

- `PaymentStatus(StrEnum)`: `PENDING="pending"`, `SUCCEEDED="succeeded"`, `FAILED="failed"`. `PENDING`은 생성 중 domain state이고 ORM choices는 Enum에서 파생하되 committed DB CHECK는 terminal `succeeded|failed`만 허용한다.
- `PaymentFailureReason(StrEnum)`: 현재 `FAMILY_ALREADY_ENTITLED="family_already_entitled"` 한 값. DB 저장 failure code는 underscore regex이고 HTTP slug와 별도 언어다.
- `EntitlementGrantStatus(StrEnum)`: `UNRECORDED="unrecorded"`, `RECORDED="recorded"`, `ALREADY_ENTITLED="already_entitled"`. `RECORDED`와 `ALREADY_ENTITLED`는 grant progress terminal이며 둘 다 가족 partial unique 점유를 해제한다.
- `Payment.start(...)`: 모든 positive int64, snapshot, aware time, digests를 검증하고 pending을 만든다.
- `succeed(at)`: pending→succeeded only, `succeeded_at` 설정, `EntitlementGrantProgress` 생성 준비.
- `fail(FAMILY_ALREADY_ENTITLED, at)`: pending→failed only. 다른 terminal transition, cancel/refund/delete는 없다.
- 정상 production flow는 한 짧은 UoW 안에서 `start` 후 `succeed+claim` 또는 `fail`까지 실행해 committed pending을 만들지 않는다.
- terminal root에 대한 `succeed/fail` 재호출, unknown failure reason, impossible state/field combination은 `PaymentStateCorrupted`/`InvalidPaymentTransition`으로 표면화되어 500으로 흐른다.
- progress의 모든 변경은 root 의도 메서드 `Payment.acquire_grant_claim(now, token_digest)`, `Payment.release_grant_claim(token_digest)`, `Payment.record_entitlement(token_digest, entitlement_id)`, `Payment.record_entitlement_already_held(token_digest)`를 거친다. root는 succeeded/progress 존재, family equality, current grant status, token ownership, terminal 전이를 확인하고 version을 증가시킨다. entity setter와 독립 repository는 없다.

### 3.4 0원 정책 · 멱등성 값

- `Payment.start`/snapshot factory가 `amount_krw == 0`만 허용한다. `>0`은 `PaidCheckoutNotSupported`; `<0`은 upstream/corruption defect다. 이 정책은 billing이 소유하고 product ACL은 가격을 전달만 한다.
- `IdempotencyKey`: raw `str|None`을 받아 1~128 visible ASCII 0x21~0x7E를 검증한다. missing/invalid를 use case가 하나의 `CheckoutIdempotencyKeyRequired`로 수렴시킨다. persistence에는 raw를 저장하지 않고 SHA-256 hex digest만 저장한다.
- `RequestFingerprint`: canonical `billing:v1:product_id=<decimal positive-int64>`의 SHA-256 hex. 같은 parent+key digest에서 fingerprint가 다르면 conflict다.
- domain의 멱등성 소유는 key validation, canonical fingerprint 생성, fingerprint equality까지다. 기존 payment의 다른 product를 `CheckoutIdempotencyKeyConflict`로 내고 collaborators를 0회로 만드는 분류는 application §5.3 한 곳이 소유한다.
- key retention은 payment ledger lifetime과 같아 영구적이다. failed key도 unique 점유를 유지하며 cleanup job이 없다.

### 3.5 GrantClaim 불변식

- TTL은 정확히 30초. 주입 clock의 aware `now`와 token issuer 결과를 쓴다.
- active 조건은 `expires_at > now`; `expires_at == now`는 만료라 새 claim 가능하다.
- claim token raw는 호출자의 일시 메모리에만 두고 DB에는 SHA-256 digest를 저장한다.
- acquire: root `Payment.acquire_grant_claim`이 succeeded + grant status `UNRECORDED`에서만 수행한다. active claim이면 `CheckoutIdempotencyKeyInProgress`; absent/expired면 새 digest/expiry와 version 증가.
- release: root `Payment.release_grant_claim`이 token digest가 current와 같을 때만 claim을 지우고 version 증가한다. transient grant failure에 사용한다.
- record success: root `Payment.record_entitlement`가 token digest 일치와 positive entitlement ID를 확인하고 status를 `RECORDED`로 바꾸며 claim을 지우고 version 증가한다. 이후 replay는 grant/OHS 호출 0이다.
- record already-held: root `Payment.record_entitlement_already_held`가 token digest 일치를 확인하고 status를 `ALREADY_ENTITLED`로 바꾸며 entitlement/claim을 null로, version을 증가시킨다. 이후 같은 key는 저장 terminal 409를 replay하고 OHS 호출 0이며 partial unique 점유도 해제된다.
- stale token/CAS loser는 상태를 덮어쓰지 않고 reload 후 이미 같은 entitlement가 기록됐으면 성공 수렴, active other claim이면 in-progress, 그 외 bounded one-retry 후 internal concurrency fault다.

### 3.6 외부 상태 소유

- family 존재/owner, product 존재/purchasability, entitlement eligibility/grant는 각 upstream OHS가 소유한다. billing aggregate/controller/repository가 재판정하지 않는다.
- billing은 OHS 결과를 billing `...Out` data로 번역하고 snapshot/ID만 도메인에 준다.
- domain event 없음: 외부 grant는 transaction 밖의 동기 command이고 성공 응답을 기다려야 한다.

---

## 4. ACL · 포트 · BC 간 채널

### 4.1 Accounts ACL

- port: `FamilyPurchaseContextPort.resolve(parent_id: int) -> FamilyPurchaseContextOut(family_id:int)`.
- adapter가 `GetFamilyPurchaseContextV1RequestContract`와 `get_family_purchase_context_v1`을 사용한다.
- `FamilyRequiredV1`→`FamilyContextMissing`; `FamilyOwnerRequiredV1`→`FamilyContextOwnerRequired`; raw transient/unknown은 감싸지 않는다. use case가 이를 controller-facing checkout outcome으로 정규화한다.

### 4.2 Products ACL

- port: `PurchasableProductCatalogPort.get(product_id:int) -> PurchasableProductOut(product_id,name,price_krw,daily_token_limit,weekly_token_limit)`.
- adapter가 `GetPurchasableProductV1Request`/`get_purchasable_product_v1`을 사용한다.
- `PurchasableProductNotFoundV1`→`PurchasableProductMissing`; `ProductNotPurchasableV1`→`PurchasableProductUnavailable`.
- `CatalogProductStateInvalidV2`, contract value error, unknown/raw infra는 public product error로 축소하지 않고 500/central transient path로 둔다.

### 4.3 Entitlements ACL

- port:
  - `ensure_eligible(family_id:int) -> None`
  - `grant(data: EntitlementGrantIn) -> EntitlementGrantOut(entitlement_id:int)`; upstream `granted_at`은 검증 후 버리고 저장/노출하지 않는다.
- input은 family/payment/product IDs, product name, daily/weekly limits. 가격은 entitlements contract에 없다.
- `FamilyAlreadyEntitledV1`→`EntitlementAlreadyHeld`.
- `OperationalError` 중 `framework.django.retryable_database_error.is_retryable_database_error`가 true인 sqlstate `40001/40P01/55P03`만 `EntitlementGrantTemporarilyUnavailable`; 나머지 DB failure는 raw/internal.
- `EntitlementIdempotencyConflictV1`, `EntitlementGrantInvalidRequestV1`, response contract corruption은 `EntitlementGrantPermanentFailure`로 번역한다. use case가 payment/family/product/reason을 식별 가능하게 exception log 후 다시 raise하여 framework 500으로 보낸다.

### 4.4 BC 횡단 채널 물음 넷

| 물음 | 답 |
|---|---|
| #563 실패하면 내가 할 일이 있는가 / 응답을 기다려도 되는가 | accounts/products 조회와 entitlements eligibility/grant는 모두 **예/예**. checkout의 다음 상태와 public response가 결과에 의존하는 동기 request/command다. 사실 broadcast가 아니다. |
| #526 internal broker에 반드시 도달을 기대는가 | 아니오. internal broker를 사용하지 않는다. rollback되면 발행 안 됨만 보장하는 at-most-once 통로로 checkout 완결을 설계하지 않는다. |
| #626 받는 쪽이 유실을 못 견디는가 | 해당 없음. subscriber가 없고 entitlement OHS에 직접 묻고 지시한다. receiver cron reconciliation 경로도 이번 scope에 없다. |
| #530 내구성/백프레셔/재시도로 external broker를 여는가 | 아니오. 발급 회복은 payment별 persisted lease + client same-key retry가 담당한다. external broker/outbox/cron을 열지 않는다. |

---

## 5. 응용 유스케이스

### 5.1 자료 계약

- `CheckoutPaymentCommand(parent_id:int, product_id:int, idempotency_key:str|None)`.
- `CheckoutPaymentUseCase.execute(command) -> CheckoutPaymentResult`.
- `PaymentResult`: public success에 필요한 `id,status,product_id,product_name,amount_krw,daily_token_limit,weekly_token_limit,payment_method,succeeded_at`만 담는다.
- `CheckoutPaymentResult(payment:PaymentResult, entitlement_id:int, idempotency_replayed:bool)`.
- `ProcessOperatorCheckoutCommand(parent_id:int, product_id:int, idempotency_key:str)`.
- `ProcessOperatorCheckoutUseCase.execute(command) -> ProcessOperatorCheckoutResult`; admin session이 logical attempt 시작 전에 보존한 valid key를 그대로 동일 `CheckoutPaymentUseCase`에 전달하고 같은 결과를 투영한다. 전송 재시도/프로세스 crash는 같은 attempt/key이고, terminal 결과 뒤 새 form attempt만 새 key다.
- result에 aggregate/ORM/OHS contract/HTTP status/header를 넣지 않는다.

### 5.2 CheckoutPaymentUseCase 정확한 흐름

1. parent/product scalar 범위, `IdempotencyKey`, `RequestFingerprint`를 만든다. 실패는 협력 호출 전 `CheckoutIdempotencyKeyRequired`.
2. repository에서 `(parent_id,key_digest)`를 조회한다. 발견 시 §5.3 replay/resume만 수행하고 accounts/products/eligibility OHS 호출은 0.
3. accounts ACL로 family/owner 확인.
4. products ACL로 purchasable snapshot 확인.
5. Payment domain에 snapshot을 넣어 amount `==0`을 판정한다.
6. entitlements ACL `ensure_eligible` 선행 확인. 실패 시 ledger/key 소비 없음.
7. **짧은 UoW A**:
   - idempotency row를 다시 조회해 same-key race를 닫는다.
   - repository가 제공한 active-family 사실을 `FamilyCheckoutAdmissionPolicy`에 넣어 정상 입장을 판정한다. 다른 payment이면 constraint insert를 시도하지 않고 `CheckoutFamilyInProgress`다.
   - entitlement eligibility를 transaction 안에서 한 번 더 확인한다.
   - final recheck가 already-entitled이면 `Payment.start→fail` terminal ledger만 insert/commit하고 `CheckoutFamilyAlreadyEntitled(replayed=False)`를 raise한다. 이 경우 key는 소비되고 family progress row는 없다.
   - 가능하면 `Payment.start→succeed`, 30초 claim 획득, immutable `PaymentModel` + `EntitlementGrantProgressModel`을 함께 insert한다.
   - `(parent,key_digest)` unique 충돌은 rollback 후 기존 row 재조회/replay로 수렴한다. active-family partial unique 충돌은 rollback 후 winner를 재조회하고 `FamilyCheckoutAdmissionPolicy`를 다시 실행해 `REJECT_OTHER_PAYMENT`일 때만 `CheckoutFamilyInProgress`; 새 ledger 0.
8. UoW 밖에서 entitlements `grant`를 호출한다. DB transaction을 열린 채 OHS를 부르지 않는다.
9. grant success면 **짧은 UoW B**에서 claim-token/version CAS로 entitlement ID를 progress에 기록한다. 확인된 뒤에만 201 result를 반환한다.
10. transient면 **짧은 UoW C**에서 matching claim을 즉시 release하고 `CheckoutEntitlementUnavailable`.
11. grant-time `EntitlementAlreadyHeld`면 **짧은 UoW B**에서 `Payment.record_entitlement_already_held(token)`을 aggregate CAS로 저장한 뒤 live `CheckoutFamilyAlreadyEntitled(replayed=False)`를 반환한다. Payment root는 succeeded 그대로이며 progress는 terminal `ALREADY_ENTITLED`; claim과 family partial unique가 해제된다. 저장 뒤 같은 key는 OHS 0으로 replay한다.
12. permanent failure면 payment/family/product/reason을 exception log하고 claim은 TTL까지 유지한 채 exception을 재전파하여 framework 500. unknown/corruption도 같은 500 경로다.

왜: 선행 실패 key 미소비, terminal replay snapshot, short transaction, external grant outside transaction, crash recovery를 동시에 만족한다. application은 흐름/transaction만 소유하고 값·전이는 aggregate에 위임한다(architecture-ddd §3.6).

### 5.3 Existing payment 분류

| stored aggregate | result |
|---|---|
| fingerprint mismatch | 422 idempotency-key-conflict; stored row unchanged |
| failed + known `family_already_entitled` | 409 same body + `Idempotency-Replayed:true`; OHS 0 |
| succeeded + entitlement recorded | stored snapshot 그대로 201 + `Idempotency-Replayed:true`; OHS 0 |
| succeeded + progress `already_entitled` | stored 409 + `Idempotency-Replayed:true`; OHS 0; family partial unique 미점유 |
| succeeded + entitlement unrecorded + claim expiry `>now` | 409 idempotency-key-in-progress + `Retry-After:1`; OHS 0 |
| succeeded + entitlement unrecorded + claim absent/expiry `<=now` | 새 claim CAS 후 **상품/가족/eligibility 재조회 없이** stored snapshot만으로 grant resume |
| committed pending, impossible combinations, unknown failure reason | `PaymentStateCorrupted`→framework 500 |

---

## 6. API · admin 계약

### 6.1 POST `/v1/payments`

- controller: `@api_controller("/payments", tags=["billing"], auth=ParentAuth())`, `@route.post("")`.
- request body `CheckoutPaymentIn`: `product_id: int = Field(..., gt=0, le=9223372036854775807)`, additional public fields 없음. OpenAPI는 integer/int64 minimum 1/maximum `9223372036854775807`; `2^63-1`은 schema 통과, `2^63`은 framework validation 422다.
- `Idempotency-Key`는 `request.headers.get("Idempotency-Key")` raw로 읽어 command에 전달한다. Ninja `Header` parameter/validator로 받지 않는다.
- schema validation `product_id` missing/0/non-int는 framework 422 `validation-error` + `invalid-params`; key missing/invalid는 application call에서 billing 422 단일 code다.
- 201 schema:
  - `CheckoutPaymentOut(payment: PaymentOut, entitlement_id:int)`.
  - `PaymentOut` exact 9 keys: `id`, `status: Literal["succeeded"]`, `product_id`, `product_name`, `amount_krw`, `daily_token_limit`, `weekly_token_limit`, `payment_method: str|None`(current always None), `succeeded_at` aware datetime.
  - family/parent/idempotency/claim/failure/created_at/version은 어떤 깊이에도 노출하지 않는다.
- 201은 persisted entitlement ID가 progress에 기록된 뒤에만 반환한다.
- 201 header `Idempotency-Replayed`는 항상 lowercase string `false|true`.
- auth failure는 `ParentAuth.authenticate`의 None→central 401; `WWW-Authenticate: Bearer`. child credential 경로 없음.
- 캐시/목록/detail/poll/webhook는 없다. POST semantics는 mandatory idempotency key로 retry-safe outcome replay를 제공한다(architecture-api §2·§13).

### 6.2 OpenAPI

- exact success operation은 `docs/rebuild/billing/api_shape_pre_success.json`의 `/v1/payments`와 같아야 한다: header parameter, request body, 201 nested schema/header, bearer security.
- `openapi_extra`는 parameter/header response documentation만 추가하고 runtime body parsing을 하지 않는다.
- summary/description/tags 및 optional `x-problem-slugs`는 normalized comparison 밖이다. 오류 public literals는 slot 10이 정본이다.
- 다른 billing path/method를 만들지 않는다. success-only normalized global snapshot이 extra billing success path 부재도 보호한다.

### 6.3 Django admin

- `PaymentAdmin` list/detail: ID, family, purchaser, product/snapshot amount, status, entitlement ID, created/succeeded/failed time를 읽는다. 모든 model fields readonly; `has_add_permission=False`, `has_change_permission=False`, `has_delete_permission=False`; bulk delete action 없음.
- custom operator URL/form은 admin session/staff permission을 사용한다. `OperatorCheckoutForm(parent_id,product_id)`는 positive int64를 검증하되 domain/application 검증을 대체하지 않는다.
- admin view는 새 logical form attempt를 열 때 1~128 visible ASCII idempotency key를 만들고 **checkout 호출 전에 DB-backed Django session에 저장·save**한다. POST/네트워크 재전송/worker process crash 뒤 같은 session은 그 key를 재사용한다. success 또는 알려진 terminal/precheck 결과를 관찰한 뒤에만 session key를 지우며, transient 503·unknown 500·응답 전 crash에는 보존한다. 따라서 reload/retry가 만료 claim을 같은 key로 resume하며 새 key 때문에 partial unique에 영구 차단되지 않는다. 새 form attempt는 terminal 정리 뒤 새 key를 발급한다. 이 구분에서 명세의 “재제출은 새 checkout”은 **새 logical form attempt**이고 동일 POST의 전송 재시도는 같은 attempt다.
- submit은 session key를 담은 `ProcessOperatorCheckoutCommand`로 `build_process_operator_checkout_use_case().execute(...)` 한 application call을 사용하고 동일 checkout flow에 위임한다. raw operator key는 payment table에는 저장하지 않고 session/POST attempt에만 존재한다.
- 성공 message에 payment ID, entitlement ID, product name. slot 10의 알려진 11 갈래는 friendly Korean form/message로 변환하며 problem JSON을 만들지 않는다. unknown/permanent/infra는 숨기지 않고 admin 500/logging 경로.
- admin view에 `transaction.atomic`/`ATOMIC_REQUESTS`를 두지 않는다. external entitlement grant가 changeform transaction 밖이라는 API와 같은 경계를 유지한다.

---

## 7. 영속화 · 트랜잭션 (db lens)

### 7.1 `PaymentModel` — immutable terminal ledger

| field | DB form / invariant |
|---|---|
| `id` | BigAutoField, positive |
| `purchaser_parent_id` | BigInteger, positive, scalar only |
| `family_id` | BigInteger, positive, scalar only |
| `product_id` | BigInteger, positive, scalar only |
| `product_name` | varchar(100), trim-equivalent, length 1..100 |
| `amount_krw` | bigint, DB CHECK `=0`; 도메인도 current checkout에서 정확히 0만 허용 |
| `daily_token_limit`, `weekly_token_limit` | bigint, positive |
| `payment_method` | nullable varchar(32), current CHECK `IS NULL` |
| `idempotency_key_hash` | char(64) lowercase hex; raw key 미저장 |
| `request_fingerprint` | char(64) lowercase hex |
| `status` | varchar choices from PaymentStatus; DB CHECK는 terminal `succeeded|failed`만 허용, `pending`은 commit 전 domain memory state뿐 |
| `failure_reason` | nullable varchar(100), `[a-z0-9_]{1,100}` when non-null |
| `created_at` | aware timestamp, explicit clock |
| `succeeded_at`, `failed_at` | nullable aware timestamps, state shape CHECK |

constraints/indexes:

- `UniqueConstraint(purchaser_parent_id,idempotency_key_hash, name="uniq_bill_payment_parent_idem")` — status와 무관, failed도 영구 점유.
- named CHECK 닫힌 집합:
  - `chk_bill_payment_parent_id`, `chk_bill_payment_family_id`, `chk_bill_payment_product_id`: 각각 `BETWEEN 1 AND 9223372036854775807`.
  - `chk_bill_payment_name`: `product_name = btrim(product_name)` and char length 1..100.
  - `chk_bill_payment_amount_zero`: `amount_krw = 0`.
  - `chk_bill_payment_daily_limit`, `chk_bill_payment_weekly_limit`: 각각 positive signed-int64.
  - `chk_bill_payment_method_null`: `payment_method IS NULL`.
  - `chk_bill_payment_idem_hash`, `chk_bill_payment_fingerprint`: 각각 lowercase hex 64자.
  - `chk_bill_payment_terminal_shape`: status는 `succeeded|failed`만이며 아래 timestamp/failure shape를 한 식으로 묶는다.
- terminal state shape:
  - succeeded: succeeded_at non-null; failed_at/failure null.
  - failed: failed_at/failure non-null; succeeded_at null; failure currently `family_already_entitled`.
- `Index(fields=["-created_at"], name="idx_bill_payment_created_desc")` 하나가 admin default global ledger ordering을 직접 지원한다. `(family_id,-created_at)`는 global ordering을 커버하지 않고 현재 승인된 family-filtered ledger query도 없으므로 만들지 않는다. 향후 그런 access pattern이 생기면 실제 query/EXPLAIN 근거로 별도 심사한다(architecture-db §7).
- repository는 root insert와 read만 제공하고 update/delete method가 없다. admin도 mutation을 차단한다.

### 7.2 `EntitlementGrantProgressModel` — mutable aggregate entity

| field | DB form / invariant |
|---|---|
| `payment` | OneToOne FK/primary key to same-BC PaymentModel, `PROTECT` |
| `family_id` | positive bigint, root snapshot과 repository mapping에서 동일 |
| `grant_status` | `unrecorded|recorded|already_entitled`; domain `EntitlementGrantStatus`에서 파생 |
| `entitlement_id` | nullable positive bigint, entitlements scalar only |
| `claim_token_hash` | nullable char(64) lowercase hex |
| `claim_expires_at` | nullable aware timestamp |
| `version` | nonnegative bigint, CAS guard |

constraints:

- partial unique `UniqueConstraint(fields=["family_id"], condition=Q(grant_status="unrecorded"), name="uniq_bill_active_family")`. 이는 domain admission policy 뒤의 race guard다. `recorded`와 `already_entitled` terminal progress는 가족을 해방한다.
- `chk_bill_progress_family_id`: family ID positive signed-int64.
- `chk_bill_progress_resolution`: exact status shape — `unrecorded`면 entitlement null이고 claim pair는 both-null/both-non-null; `recorded`면 entitlement positive signed-int64이고 claim 둘 다 null; `already_entitled`면 entitlement/claim 셋 다 null.
- `chk_bill_progress_claim`: non-null claim hash는 lowercase hex 64자이고 expiry는 non-null이다(역방향도 동일).
- `chk_bill_progress_version`: `version >= 0` and signed bigint range.
- succeeded Payment와 progress의 동시 생성, failed Payment와 progress 부재, `progress.family_id == root.family_id`는 UoW/repository aggregate contract가 보장한다. `family_id`는 insert-only coordination key로, CAS `SET` 목록에 절대 포함하지 않는다. rehydration 불일치는 `PaymentStateCorrupted`; DB-backed round-trip/rollback/immutability test가 보호한다. cross-table business 판정을 trigger/SQL에 복제하지 않는다.

### 7.3 Repository · CAS

- `PaymentRepository.find_by_idempotency(parent_id,key_hash) -> Payment|None`.
- `find_active_family_checkout(family_id) -> ActiveFamilyCheckout|None`은 domain policy에 줄 사실만 읽고 판정하지 않는다.
- `add_terminal(payment) -> Payment`: root와 optional progress를 같은 UoW에 insert하고 assigned ID를 aggregate에 반영한다.
- `get(payment_id) -> Payment|None`은 `select_related` progress로 aggregate를 재구성하며 unknown enum/impossible DB shape를 `PaymentStateCorrupted`로 만든다.
- `save(payment: Payment, expected_progress_version:int)`: root를 통해 변경된 aggregate progress만 저장한다. `WHERE payment_id=? AND version=?`만 CAS predicate로 쓰고 `SET`은 `grant_status,entitlement_id,claim_token_hash,claim_expires_at,version` 닫힌 집합이다. `family_id`/root ledger fields는 갱신하지 않는다. update count 0은 `PaymentGrantVersionConflict`; entitlement/business 판정을 SQL WHERE에 넣지 않는다.
- named unique violation만 `PaymentIdempotencyOccupied`/`FamilyCheckoutOccupied`로 정규화한다. unknown `IntegrityError`는 500. raw nonretryable DB failure도 안정 public meaning으로 바꾸지 않는다.
- billing repository/UoW/PostgreSQL clock adapter가 낸 모든 `OperationalError`는 각 adapter boundary에서 cause를 보존한 internal mechanism exception `BillingPersistenceFailure`로 감싸고 다시 raise한다. 이 exception은 controller가 catch하지 않아 shared catch-all 500으로 간다. 따라서 shared `broccoli_server/api.py::on_db_operational_error`의 message/sqlstate 503 recognizer가 billing raw infra를 우회 분류하지 않는다. 오직 entitlements ACL이 OHS 호출에서 승인한 `40001/40P01/55P03`만 `EntitlementGrantTemporarilyUnavailable`로 바꿔 billing-owned 503이 된다.

### 7.4 Transaction/isolation/locking

- transaction owner는 `CheckoutPaymentUseCase`가 주입받은 `PaymentCheckoutUnitOfWork`; implementation은 Django `transaction.atomic`과 repository를 묶는다. application은 Django를 import하지 않는다.
- PostgreSQL READ COMMITTED 유지. predicate safety는 two named unique constraints, progress CAS, entitlements provider의 own unique invariant로 달성한다. Serializable 전역 상향과 broad row lock은 불필요하다.
- UoW A/B/C는 짧고 외부 grant를 포함하지 않는다. accounts/products precheck도 transaction 밖; spec이 요구한 entitlement final recheck만 UoW A 안에서 동기 호출한다.
- same-key insert race는 unique가 한 승자만 허용하고 loser가 commit 뒤 row를 reread한다. different-key same-family race는 active-family partial unique가 loser ledger insert를 rollback시킨다.
- claim expiry/lease의 production `now`는 `PostgresCheckoutClockAdapter`가 `SELECT clock_timestamp()`로 읽은 PostgreSQL authoritative aware time이다. 각 acquire/replay/CAS convergence UoW가 한 번 읽어 domain policy/root에 전달하고 expiry는 그 값 + 정확히 30초다. multi-process host clock/skew를 사용하지 않는다. 테스트는 fake port로 exact `<,==,>` 경계를 주입하고 실제 sleep은 없다.
- retry: application의 CAS finalize/release만 bounded 1회 reload/survival classification. DB deadlock/serialization/lock timeout을 무한 retry하지 않는다; recognized framework/ACL transient는 승인된 503으로 반환해 caller same-key retry를 유도한다.

### 7.5 Risky Write Consistency Block (8행)

| 항목 | 결정 내용 |
|---|---|
| Transaction owner | `CheckoutPaymentUseCase` + `PaymentCheckoutUnitOfWork`. A=create terminal ledger+progress/final eligibility, B=record entitlement, C=release transient claim. Operator use case도 같은 core를 사용한다. |
| Locking strategy | PostgreSQL named unique `(parent,key_hash)` + partial unique `family_id WHERE grant_status='unrecorded'`; progress `version` optimistic CAS; production time은 PostgreSQL `clock_timestamp()`. broad `select_for_update`, advisory lock, Serializable은 쓰지 않는다. |
| Rule ownership | Payment/VO/root methods가 zero-cost, state/progress transition, value shape, claim expiry/token, replay/corruption을 소유하고 `FamilyCheckoutAdmissionPolicy`가 교차-Payment 가족 입장을 소유한다. repository SQL은 unique/CHECK/CAS 경합 가드와 결과 저장만 담당한다. |
| Idempotency storage | `billing_payment`: per-parent raw-key SHA-256 digest, canonical product request fingerprint, immutable terminal snapshot/outcome; permanent retention; unique constraint. HTTP status/body는 저장하지 않는다. |
| API handoff | same request replay=stored result; different fingerprint=422 conflict; active claim=409+Retry-After; failed replay=409+replayed header; success replay=201+replayed header. §2/§6과 일치. |
| Side-effect timing | entitlements grant는 UoW A commit 후 transaction 밖. UoW B가 success 또는 already-entitled terminal progress를 root 경유 기록하고, transient release는 별도 C다. no event/outbox. 201은 recorded B commit 뒤. |
| Isolation/retry | all supported env PostgreSQL READ COMMITTED + authoritative DB clock. unique/CAS conflict를 closed outcome으로 재조회; CAS 1회 bounded convergence. OHS에서 승인된 `40001/40P01/55P03`만 billing 503; billing persistence OperationalError는 internal wrapper→500. |
| Test criteria (candidate) | same-key same/different payload race, different-key same-family policy+partial unique race, final eligibility failed ledger, exact CHECK/unique rejection, rollback, success-crash same-key/API와 DB-session operator resume, grant-time already-entitled terminal replay/unique 해제, active/expired/premature-takeover boundary, insert-only family key, CAS stale owner, grant outside transaction, 201-after-record. 각각 §10에서 독자 failure/coverage를 심사한다. |

### 7.6 Migration/rollout

- 신규 `billing` app/table이라 `0001_initial.py` 하나를 `makemigrations`로 생성한다. dependencies는 같은 migration 안 두 model 순서 외 타 BC migration 없음; cross-BC FK 없음.
- existing row/backfill/cleanup 없음. Expand 단계는 app + two tables + constraints/indexes를 한 배포 전에 적용한다. Backfill/Contract 단계는 미적용.
- unique/check/index build 대상 table이 비어 있어 legacy lock/data validation 위험 없음. 그래도 production migration은 normal deployment window에 먼저 적용하고 앱 코드를 올린다.
- migration file/operation/history 자체를 영구 pytest oracle로 만들지 않는다. current model constraints와 runtime DB behavior를 integration tests로 검증한다.
- data가 생긴 뒤 rollback은 table drop이 아니라 application forward-fix/route disable이다. ledger 보존 때문에 destructive rollback 금지.

---

## 8. Composition · 프로젝트 wiring

Change inventory는 아래 셋으로 닫힌다. `application/billing/**` 밖 production edit는 두 project wiring file뿐이다.

| target | exact change | non-change guarantee |
|---|---|---|
| `broccoli_server/settings/base.py` | `INSTALLED_APPS`의 application app block에서 entitlements 항목 곁에 `"application.billing.driven_layer.django_billing.apps.DjangoBillingConfig"` 한 줄 추가 | 다른 app path/order/setting/UNFOLD 값은 그대로 |
| `broccoli_server/urls.py` import block | `from application.billing.driving_layer.api.api_router import register_billing_api` 한 줄 추가 | 기존 BC router imports, `usage_quota_urlpatterns`, `ai_chat_root_urlpatterns`, comments를 그대로 둠 |
| `broccoli_server/urls.py` first materialization 전 | `from broccoli_server.api import api` 이후, `legacy_api_patterns = [...]`보다 앞에 `register_billing_api(api)` 한 번 호출 | existing selector comprehension, `legacy_api_urls`, `urlpatterns`, mount/order/path를 byte-for-byte 유지 |

`application/billing/driving_layer/api/api_router.py`의 production contract는 다음과 같다.

```python
def register_billing_api(api: Any) -> None:
    api.register_controllers(PaymentController)
```

- Router module은 `broccoli_server.api.api`를 import하지 않고 import-time registration을 하지 않는다.
- Controller set/order는 `PaymentController` 하나다. Controller decorator의 `auto_import=False`가 framework auto-discovery 중복을 막는다.
- URLconf call은 첫 `api.urls` 접근 전에 있으므로 기존 legacy mount의 frozen route set에 `/v1/payments`가 포함된다.
- Existing BC는 현재 import side effect 방식과 selector/mount를 그대로 유지한다. 이 delivery는 이를 표준화하거나 별도 debt로 기록하지 않는다.
- `broccoli_server/api.py`는 제품 명세 §6에 따라 restore point가 아니며 read-only/diff 0이다. `BroccoliNinjaAPI` 생성 인자, central error mapping/handler, OpenAPI augmenter도 바꾸지 않는다.
- `application/billing/driven_layer/django_billing/admin/payment/panel.py` import가 Django admin autodiscovery에 의존하지 않도록 `django_billing/admin/__init__.py`가 `PaymentAdmin` 등록 module을 import한다. `apps.py.ready()` registration은 두지 않는다.

Phase 2 순서는 `(B0) §1.2 전체 skeleton과 package marker → (B1) domain/value/exception → (B2) application ports/use cases → (B3) driven ORM/repository/UoW/ACL → (B4) controller/error/admin → (B5) settings/URLconf wiring → (B6) test table owner별 Green 및 full gates`다. 각 단계는 다른 BC 파일을 수정하지 않는다.


## 9. 외부 관찰 가능 행위 목록

입장 심사 후보의 제품 행위는 다음과 같다.

1. valid zero-cost checkout은 entitlement 기록 후 201, exact snapshot, replayed=false.
2. success replay는 upstream collaboration 0, stored snapshot, replayed=true.
3. failed terminal replay는 현재 family 상태와 무관하게 same 409/replayed=true.
4. missing/invalid key가 한 422 code로 수렴하고 key를 소비하지 않음.
5. same key/different product는 422 conflict, 기존 ledger 불변.
6. family missing/owner mismatch, product missing/unpurchasable, paid product, initial entitlement held는 exact status/body이고 ledger 0.
7. final eligibility race는 failed ledger를 보존하고 live 409; replay는 stored 409.
8. same family active different key는 domain admission policy와 partial unique 경합 가드가 같은 결과(한 승자/한 `family-checkout-in-progress`, loser ledger 0)를 낸다.
9. active lease same key는 in-progress; `expires_at==now`부터 resume 가능.
10. transient grant는 succeeded ledger/미기록 progress를 보존하고 claim release, 503/Retry-After.
11. grant-time already-entitled는 progress terminal 저장/partial unique 해제 뒤 live 409, same-key replay는 OHS 0/409/replayed=true.
12. permanent/corruption/billing persistence OperationalError는 500과 식별 가능한 log, shared retry recognizer에 의한 false 503 없음.
13. grant record CAS 뒤만 201; crash gap은 same-key retry가 stored snapshot으로 resume.
14. auth 401 challenge, schema validation 422와 billing 422 분리; product_id max int64 통과/max+1 framework 422.
15. admin ledger immutable/read-only; operator logical attempt key는 checkout 전 DB session에 보존되어 process crash 후 같은 flow를 resume하고, known messages는 friendly Korean이다.
16. 다른 billing route/method/event/subscriber/API 없음.

---

## 10. 영구 테스트 입장 표

현재 working tree의 두 provisional test artifact는 제품 계약 초안을 고정했지만 `test/e2e` black-box 경계를 어겼다. 따라서 행위 오라클은 보존하되 owner를 아래처럼 바로잡는다. `pending`은 0개다.

아래 owner의 `test/...` shorthand는 모두 `application/billing/test/...` 기준 상대 경로다.

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| T-DOMAIN-STATE Payment transition/snapshot/terminal immutability | `spec.md` §2 | terminal 역전, snapshot drift | 없음 | add | coder `application/billing/test/unit/domain/test_payment.py` |
| T-DOMAIN-VALUES positive int64/name/amount/time/failure corruption | `spec.md` §2 value boundaries | invalid provider/storage value가 정상 ledger/응답으로 침투 | upstream tests는 billing rehydration을 보호하지 않음 | add | coder `test/unit/domain/test_payment.py`, `test_payment_corruption.py` |
| T-DOMAIN-IDEM key boundary/canonical fingerprint/equality | `spec.md` §2 | invalid key/fingerprint가 협력·DB까지 도달 | 없음 | add | coder `test/unit/domain/test_idempotency_key.py` |
| T-DOMAIN-FAMILY-ADMISSION active none/same/other + constraint-race 재판정 | `spec.md` §2 | DB exception이 business verdict가 됨 | 없음 | add | coder `test/unit/domain/test_family_checkout_admission_policy.py` |
| T-DOMAIN-CLAIM active `>`/boundary `==`/expired `<`, token/root-only terminal | `spec.md` §2 | premature takeover, child 독립 mutation | 없음 | add | coder `test/unit/domain/test_entitlement_grant_progress.py` via `Payment` methods |
| T-APP-PRECHECK exact call order, key first, precheck rejection ledger 0 | `spec.md` §3.4 | invalid key 전에 collaborator 호출, rejected key 소비 | provider tests only | add | coder `test/unit/application/test_checkout_payment_use_case.py` |
| T-APP-REPLAY success/failed/grant-time-already-entitled/fingerprint/active claim, collaborators 0 | `spec.md` §2 | upstream state로 replay 재조합 | 없음 | add | coder `test/unit/application/test_checkout_payment_use_case.py` |
| T-APP-FINAL-RECHECK second eligibility failure commits failed ledger | `spec.md` §2 | double grant 또는 failed outcome/key 유실 | provider eligibility test는 billing ledger 미보호 | add | coder `test/unit/application/test_checkout_payment_use_case.py` |
| T-APP-SIDE-EFFECT grant outside UoW, record before result | `spec.md` §3.4/201 guarantee | lock-held OHS 또는 미기록 201 | 없음 | add | coder `test/unit/application/test_checkout_payment_use_case.py` |
| T-APP-GRANT transient release/permanent log/live already-entitled terminal | `spec.md` §2 | retry 차단, terminal 저장 누락 | framework classifier는 billing resolution 미보호 | add | coder `test/unit/application/test_checkout_payment_use_case.py` |
| T-APP-OPERATOR logical-attempt key unchanged/delegates same core | `spec.md` §3.5 | 매 호출 key 교체, 별도 정책 drift | 없음 | add | coder `test/unit/application/test_process_operator_checkout_use_case.py` |
| T-ACL-ACCOUNTS request/response/exception translation | `spec.md` §5 | upstream exception/model 누수 | provider own current tests | add | coder `test/unit/adapter/test_accounts_family_purchase_context_adapter.py` |
| T-ACL-PRODUCTS snapshot/two public exceptions/invalid fallback | `spec.md` §5 | missing vs unpurchasable 오역 | provider own current tests | add | coder `test/unit/adapter/test_products_purchasable_product_catalog_adapter.py` |
| T-ACL-ENTITLEMENTS eligibility/grant translation and `granted_at` discard | `spec.md` §5 | transient/permanent 오분류, field leak | provider own current tests | add | coder `test/unit/adapter/test_entitlements_grant_adapter.py` |
| T-ACL-TRANSIENT exact SQLSTATE set | current framework contract | shared classifier drift | `framework/test/unit/test_retryable_database_error.py` | reuse | no billing test write |
| T-REPO-ROUNDTRIP root+progress/snapshot/corruption/insert-only family | `spec.md` §2 | ORM mapping drift, impossible row 수용 | 없음 | add | coder `test/integration/repository/test_django_payment_repository.py` |
| T-DB-CHECKS terminal zero/state/progress/hash/scalar shapes | `spec.md` §2 | corrupt row commit | 없음 | add | coder `test/integration/repository/test_payment_constraints.py` |
| T-DB-IDEMPOTENCY parent/key unique, different parent allowed, failed retains | `spec.md` §2 | duplicate ledger/key reuse | 없음 | add | coder `test/integration/repository/test_payment_constraints.py` |
| T-DB-FAMILY policy parity + PostgreSQL partial unique + terminal release | `spec.md` §2/§7 | both active rows 또는 permanent family lock | upstream concurrency is another invariant | add | coder `test/integration/concurrency/test_billing_checkout_concurrency.py`, serial/no sleep |
| T-DB-SAME-KEY-RACE same/different fingerprint collision reread | `spec.md` §2 | `IntegrityError` leak, duplicate payment | constraint-only test insufficient | add | coder `test/integration/concurrency/test_billing_checkout_concurrency.py` |
| T-DB-LEASE-CAS stale version/token, DB time, expired recovery | `spec.md` §2 | host skew/old worker overwrite | 없음 | add | coder `test/integration/concurrency/test_billing_checkout_concurrency.py`, injected barrier/clock |
| T-DB-ROLLBACK final check/unique/unknown leaves no partial root/progress | `spec.md` §3.4 | orphan/consumed key | 없음 | add | coder `test/integration/repository/test_payment_checkout_unit_of_work.py` |
| T-E2E-SUCCESS first 201 exact body/header and entitlement public observability | `spec.md` §3.2 | premature 201/wire leak | 없음 | add | acceptance-tester `test/e2e/test_payment_checkout_acceptance.py`, e2e conftest의 public HTTP/admin arrange only |
| T-E2E-REPLAY stored snapshot/header true after public product deletion | `spec.md` §2 replay | current Product state breaks replay | application unit 미보호 mounted wire | add | acceptance-tester `test/e2e/test_payment_checkout_acceptance.py`; mounted admin delete, ORM import 0 |
| T-CONTROLLER-ERROR exact 11 body/status/conditional headers | `spec.md` §3.3 | wrong mapping/literal/header | common shape test는 billing literals 미보호 | add | coder `test/integration/api/test_payment_controller.py`; mounted client + billing composition seam injection |
| T-E2E-AUTH mounted 401 and bearer challenge | `spec.md` §3.1 | wrong status/challenge | common body test만 존재 | add | acceptance-tester `test/e2e/test_payment_checkout_acceptance.py`; billing patch/call-count 0 |
| T-CONTROLLER-AUTH-GUARD unauthenticated request invokes application 0 | `spec.md` §3.1 | auth failure가 use case 실행 | pure e2e는 internal call count를 관찰할 수 없음 | add | coder `test/integration/api/test_payment_controller.py`; mounted client + billing builder spy |
| T-E2E-VALIDATION-ROUTING product missing/0/non-int/max/max+1 and raw key branch | `spec.md` §2·§3 | owner/media/int64 drift | common validation exact shape는 reuse 행 소유 | add | acceptance-tester `test/e2e/test_payment_checkout_acceptance.py`; public request/response only |
| T-CONTROLLER-INFRA billing persistence failure→framework 500, entitlement transient→billing 503 | `spec.md` §3.3/§5 | raw billing DB가 false 503 | shared classifier 미보호 physical boundary | add | coder `test/integration/api/test_payment_controller.py`; mounted client + billing seam injection |
| T-OPENAPI-SUCCESS normalized success exact + one billing success path | `spec.md` §7 + success snapshot | header/security/schema/path drift | 없음 | add | acceptance-tester `test/integration/api/test_payment_checkout_openapi.py` |
| T-OPENAPI-ERROR 11 literal refs/media/status/header declarations | `spec.md` §3.3 | docs가 base schema로 소실 | 없음 | add | acceptance-tester `test/integration/api/test_payment_checkout_openapi.py` |
| T-ADMIN-LEDGER readonly/no add/change/delete/display | `spec.md` §3.5 | operator ledger mutation | 다른 model admin test는 미보호 | add | coder `test/integration/admin/test_payment_admin.py` |
| T-ADMIN-CHECKOUT success/Korean failures/session crash resume/core reuse/outside tx | `spec.md` §3.4~3.5 | session key late save, admin policy fork | application unit은 admin wrapper 미보호 | add | coder `test/integration/admin/test_payment_admin.py` |
| T-COMMON-SHAPE exact FrameworkErrorSchema fields/default/omit None | fixed common reuse | common shape drift | `framework/test/unit/test_framework_error_schema.py` | reuse | no billing test write |
| T-VALIDATION-SHAPE invalid-params alias | framework-owned 422 | alias drift | `framework/test/unit/test_framework_validation_error_schema.py` | reuse | no billing test write |
| T-UPSTREAM-ACCOUNTS OHS provider behavior | `spec.md` §5 observed contract | owner/member semantics drift | current accounts unit/integration OHS contract tests | reuse | no billing/other-BC test write |
| T-UPSTREAM-PRODUCTS OHS provider behavior | `spec.md` §5 | sale/purchasability drift | current products unit/integration OHS contract tests | reuse | no billing/other-BC test write |
| T-UPSTREAM-ENTITLEMENTS OHS grant/concurrency | `spec.md` §5 | duplicate grant/provider drift | current entitlements acceptance/concurrency tests | reuse | no billing/other-BC test write |
| T-ROUTER registrar/import/order source introspection | private composition mechanics | mounted route/OpenAPI + registry backstop이 잡음 | T-OPENAPI-SUCCESS + root registry | reject | source-shape pytest 0 |
| T-SCHEMA-INTERNAL Pydantic metadata/validator location | private library mechanism | public wire/OpenAPI가 failure를 잡음 | HTTP/OpenAPI rows | reject | private introspection 0 |
| T-MIGRATION-FILE exact operation/history snapshot | generated implementation detail | runtime DB constraints/roundtrip이 failure를 잡음 | DB rows | reject | migration pytest 0 |
| T-DEFAULT-ROUTES explicit 404/405 framework snapshot | framework default, custom contract 아님 | extra billing success path는 OpenAPI가 잡음 | T-OPENAPI-SUCCESS | reject | no duplicate test |
| T-NO-EVENT-ARTIFACT empty event/webhook/cron source assertion | absence/source shape | full skeleton + registry and surface list가 잡음 | root registry/OpenAPI | reject | behavior 없는 placeholder test 0 |

### 10.1 Corrected acceptance ownership

`application/billing/test/e2e/conftest.py`가 true e2e의 self-contained arrange 계약을 소유한다.

- `bearer`, `post_json`, `login_parent`, `bootstrap_family`는 `django.test.Client`로 current public `/v1/auth/social-login`, `/v1/families/me/children`, `/v1/families/me`만 호출한다. Accounts test helper를 import하거나 복사본과 runtime linkage를 만들지 않는다.
- `create_and_activate_free_product_via_admin`은 `django.contrib.auth.get_user_model`, `django.urls.reverse`, mounted `admin:products_productmodel_add/change`만 쓴다. Add를 `_continue`로 제출해 redirect의 public admin URL에서 product ID를 얻고 change form으로 활성화한다. `delete_product_via_admin`도 mounted delete form을 사용한다. Products ORM/factory/OHS implementation import는 0이다.
- 같은 file이 위 helper를 fixture로 노출한다. e2e test module은 stdlib와 pytest/Django public test types만 import하고, fixtures는 pytest discovery로 받는다. `application.*` import는 0이다.
- Billing-owned `payment_factory.py`와 `entitlement_grant_progress_factory.py`는 billing repository/DB integration tests에서만 쓴다. 다른 BC model을 import하거나 생성하지 않는다.
- Controller integration은 필요한 authenticated parent를 자기 test module의 작은 public HTTP arrange로 만들며 e2e conftest를 import하지 않는다. Test-specific builder/use-case injection은 그 integration module 안에만 있다.

Current provisional `application/billing/test/e2e/test_payment_checkout_acceptance.py`의 case 이동은 exact하게 다음과 같다.

| current case | final owner/action |
|---|---|
| `test_first_checkout_returns_exact_201_after_entitlement_is_observable` | e2e 유지; parent/family/product arrange를 public-entry fixture로 교체 |
| `test_success_replay_returns_the_stored_snapshot_without_upstream_state` | e2e 유지; `ParentModel` mutation 제거, mounted product admin delete 뒤 replay로 같은 snapshot을 검증 |
| `test_billing_errors_keep_the_exact_public_wire_contract` | `test/integration/api/test_payment_controller.py`로 이동; billing builder/use-case seam에 concrete domain exception을 주입하고 mounted response를 검증 |
| `test_unauthenticated_checkout_returns_bearer_challenge_without_application_call` | e2e에는 status/challenge만 유지; call-count는 controller integration의 `T-CONTROLLER-AUTH-GUARD`로 분리 |
| `test_invalid_product_id_stays_on_the_framework_validation_branch` | e2e 유지, public login helper만 사용 |
| `test_signed_int64_max_reaches_the_billing_application_branch` | e2e 유지, family 없는 public parent로 real billing branch 관찰 |
| `test_missing_or_invalid_raw_key_stays_on_the_billing_error_branch` | e2e 유지, public request/response only |
| `test_billing_persistence_failure_remains_framework_500` | controller integration으로 이동; UoW contract module의 `BillingPersistenceFailure` 주입 허용 |
| `test_approved_entitlement_transient_uses_the_billing_503_branch` | controller integration의 11종 table/infra branch가 소유 |

E2E에서 `_patch_checkout_execute`, `_checkout_error`, `mocker.patch`, `application.billing.application_layer/**` import는 전부 제거한다. Controller integration은 white-box seam을 쓸 수 있지만 다른 BC test/model/factory는 여전히 import하지 않는다. OpenAPI test는 현재처럼 mounted `/v1/openapi.json`만 읽고 billing implementation을 import하지 않는다.

### 10.2 Billing-attributable registry closure

Current registry report는 provisional billing artifact의 신규 귀속 **20**만 근거로 사용한다.

| rule | current count | exact closure | target |
|---|---:|---|---:|
| #51 | 2 | accounts test helper/products factory imports 제거, billing e2e conftest의 public fixtures로 교체 | 0 |
| #488 | 12 | §1.2의 complete billing fixed/reappearing skeleton/package marker를 production 시작 전에 한 번에 materialize | 0 |
| #385 | 3 | accounts private ORM + accounts test helper + products factory imports 제거; public HTTP/admin conftest만 사용 | 0 |
| #390 | 3 | billing use-case/package/UoW exception imports와 patches를 e2e에서 제거; injection cases를 controller integration으로 이동 | 0 |
| **합계** | **20** |  | **0** |

이 closure는 test case의 제품 오라클을 삭제하지 않고 black-box/public seam 또는 integration/controller owner로 옮긴다. 다른 BC test artifact는 read-only `reuse` evidence일 뿐 수정 대상이 아니다.

### 10.3 결정 집계

- `add 32 / reuse 6 / reject 5 / pending 0` — 총 43행.
- 다른 BC test의 import/patch/module string을 기계 갱신하는 행은 없다.
- Acceptance-tester는 true e2e 4행과 OpenAPI 2행만 소유한다. Coder는 domain/application/adapter/DB/admin 및 white-box controller integration을 소유한다.

---

## 11. 확정 delivery scope · gate

- Production allowlist: `application/billing/**`, `broccoli_server/settings/base.py`, `broccoli_server/urls.py`.
- `broccoli_server/api.py` diff 0. 다른 BC의 registrar/controller/presentation/application/test 및 framework handler는 read-only evidence다.
- Registry command는 anchor `68ce0e51`과 `docs/rebuild/billing/legacy_debt.txt`를 사용한다. Current baseline의 legacy **5680**은 report-only이며 이 delivery의 fix 목록이나 새 debt가 아니다.
- 새 billing 귀속은 §10.2의 20→0, 이후 구현으로 생기는 신규 귀속도 0이어야 한다. 승인 debt 파일 밖 새 debt/shim은 없다.
- Product contract, status/body/header/OpenAPI/transaction/admin semantics는 §2~§9 그대로다.
- `pending 0`, `STOP_FOR_USER_APPROVAL 0`. `request.md`의 unattended gate 위임과 `scope.md`/`refactor-scope.md`의 2026-08-13 correction이 승인 근거다.

---

## 12. 자기모순 스캔

- **범위**: 모든 planned production path가 §11 allowlist 안이다. Other-BC 현행 구조는 관찰만 하고 수정·표준화·debt화하지 않는다.
- **골격**: billing은 첫 production write 전에 §1.2 fixed/reappearing package/file을 전부 만들고, placeholder는 실제 개념만 연다. 표준 밖 application exception/UoW exception/template path가 없다.
- **composition**: 기존 URL imports/selectors/mount/order는 그대로이고 billing registrar import/call만 첫 `api.urls` 접근 전에 추가한다. 중앙 API diff는 0이며 billing controller 중복 auto-registration은 없다.
- **오류**: 11 BC-owned code-json 오류와 framework-owned problem media가 status별로 분리된다. Controller의 narrow catch와 unknown 500 경로가 함께 유지된다.
- **DDD/DB**: cross-BC 참조는 scalar/OHS+ACL이고 FK는 없다. External grant는 short transaction 밖, root/progress CAS 뒤만 201이다.
- **테스트**: true e2e는 다른 BC test/private ORM 및 billing implementation import/patch가 0이다. Outcome injection은 controller integration owner로 분리했고 public wire 오라클은 보존한다.
- **gate**: billing-attributable 20과 이후 신규 findings는 0, legacy report-only, pending/STOP 0이 양립한다.
