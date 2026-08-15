# 채점 결과지 — pdrebuildlive-codex (S3-r2″ · 레인 B · ⑥a — 유효 정지)

> **방법**: EVAL-METHOD **v5 frozen** · **identity**: `2026-08-08-tree-revision` + `dddjango-code-json` + `v5-candidate` + dimension ID · **채점일** 2026-08-15 15:06 · **픽스처** `/Users/hyun/Desktop/broccoli-rebuild-codex`(working tree = HEAD `164332d` · clean — 새 clone·구 clone 은 `-s3r2b-evidence` 보존) · **런타임** codex CLI(gpt-5.6-sol xhigh) **plugin 2.8.0** · **기동 HEAD** `e29b1059` · **앵커** `5630e2f2`(r2″ respin — spec §6/§4 표준형 개정 + preflight ⑽ 8표면) · **태스크** 판매용 상품 카탈로그 BC 6 유스케이스(GET /v1/products 목록·동기 OHS 단건·admin 생성/수정/삭제·seed 스크립트 · KST 기준일 1회 결정·전체 교체·무변경 no-op·인식 transient 1회 재시도·hard delete · 오류 프로필 dddjango-code-json·wire=RFC 9457 problem+json·BC 고유 오류 slug 0).
> **라운드 문맥**: S3-r2″ 레인 B. **이 라운드는 완주가 아니라 «유효 정지»다** — 구현·테스트·차분 게이트 전부 green 이나, G2 직접-실행 계열 검사기 4종(#2 exit 1 — legacy 동적 StrEnum 정적 해석 불능 / #5·#6·#16 scope-render exit 2 — legacy·승인 빚까지 직접 차단)이 프로토콜 문면상 blocker 라 **G2 배너 없이 중단 커밋(`164332d` `rebuild(products): stopped — G2 direct scope checker blocker`)으로 종료**했다. G2 봉인 없음. 채점은 산출물 전체(정적 준수)에 대해 정상 수행.
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ⏸️ 보류/미인증 · ➖ N/A.
> **⚠️ 필수 단서**:
> - **결정 레인 = 하네스 봉인 값**(⑤ 3축 — 재실행 금지·그대로 기재) + 조정자 read-only 실측(Read·Grep·git diff — 코드·테스트·검사기 실행 0). **의미 레인 = 독립 채점자 1인(`N_grader=1` · blind 미집행 — 리빌드 라운드 판정용 · 재구현·재료 준비 비참여)**.
> - **FC-1 골든 행위표: products 분 공백 지속**(r2·r2′·r2″ 연속 — 사전등록 재료 부재) + read-only 채점이라 FC-1·FC-2 실행 자체 금지 → **둘 다 ⏸️(게이트 미인증)**. FC-3 은 의미 판정으로 수행.
> - **fixture 도구 환경(env / produced / used)**: env = `.venv` site-packages 실측 — pytest 8.x·pytest-django 4.12.0·pytest-mock 3.15.1·pytest-sugar 1.1.1·pytest-xdist 3.8.0·factory_boy 3.3.3·django-ninja 1.6.2·django-ninja-extra 0.31.5, 전부 **기존 프로젝트 매니페스트 핀**(`pyproject.toml:8-9·26-34`) · 조정자 추가 0. produced = **0**(`git diff 5630e2f2..164332d` 에서 `pyproject.toml`/`uv.lock` 무변 — 기존 핀 재사용은 흠 아님). used = 함수형 pytest + `@pytest.mark.django_db(…)` 전수 · `mocker`(pytest-mock — `test_product_catalog_api.py:54` 등) · `monkeypatch`(`test_seed_temp_products.py:27`) · `capsys` · Django `TestCase` 0 · factory_boy 미사용(§11 입장표 reject 행 — env 에 있으나 안 쓴 **정당 미사용**).
> - **런-정지 확인(§1.5)**: 비-git 최신 mtime = `.pytest_cache/v/cache/nodeids`(채점 착수 약 8분 전 — 하네스 B축 실측 산물) · 소스·산출물 최신은 `STOP_FOR_USER_APPROVAL.md`(14:37 이전) · 워킹 트리 clean — 채점 중 변화 없음.
> - **자기보고 불신 집행**: 152 테스트·#597 어휘 교정·Placement·설계 반영·STOP 분류 전부 실물(파일·심볼 grep·git diff)로 독립 재검증 — 아래 «자기보고 검증».
> - **클린룸(채점자)**: 다른 레인 클론·`*-claude.md` 결과지 열람 0 · 레인 간 비교 서술 0.

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① C 마스크(MQ0/MQ1/MQ2) | MQ0=**N** — `application/products/` 는 앵커 시점 물리 부재(`refactor-scope.md:6-7` + 조정자 diff 실측 — V1 삭제는 라운드 준비 소관·이 런의 삭제-대체 아님) → **순수 신규 앱 → §0 전부 강제** → 충족 |
| ② 치명 후보 게이트 FAIL 수 | **판정 가능 치명 차원 FAIL 0** — SD-1~7·SH-1·2·3·4·7·NJ-1·2·Q-4·FC-3 전부 PASS. **FC-1·FC-2 ⏸️**(골든 공백 + read-only 실행 금지 — 게이트 «통과» 아닌 «미인증») |
| ②.5 실질성 관문 | degenerate 0 — 도메인 판정 실코드 실증(`product.py:119-172` replace 원자 swap/no-op·activate·is_purchasable + 값 객체 6종 경계 raise). 빈 골격 칸은 전부 표준 의무 empty 칸(§632-(2)) — FAIL 아님 |
| ③ 비치명·의미적 변종 | **[결정 PASS ∧ 의미 FAIL] 0건**. 역방향 [결정 FAIL ∧ 의미 PASS] 1건 = NJ-4(아래 메타) → NJ-4 종합 🟡 |
| ④ TIER-Q 등급 | **상** — WEAK 1(NJ-4) · FAIL 0 (Q-1·2·3·5·6·7 + NJ-3·7 전부 PASS) |

> **한 줄 요지**: 정적 준수면에서 치명 위반 0·의미변종 0·품질 «상»이고, **r2′ 를 두 번 좌초시킨 충돌 4축(OHS 명명·V-접미·오류 갈래 모양·admin 칸)이 전부 재발 0** — 산출물 자체는 이 시리즈에서 채점한 코드 중 최상급 밀도(어노테이션 전수·경계값 전수 테스트·Event-순서 결정적 동시성 테스트). 정지는 산출물 결함이 아니라 **spec §3 «401·503 선언» ↔ 검사기 #5 문면, legacy 전역 스캔(#2·#6·#16) ↔ Placement 닫힌 목록의 재료·검사기 축 충돌**이며 STOP 분류((a)=4·(b)=0)는 실물 대조로 정확했다.
> **2차원 라벨**: (정적: **준수 — 단 FC-1·2 미인증 유보**(§4.2 조건 3 실측 불가·치명 FAIL 은 0)) × (라이브: **미검증** — EP probe 미실행·G2 미봉인)
> **라운드 판정**: **유효 정지 — G2 미봉인 · ⑤ 문면 green · 스트릭 계상은 사용자 몫.** (G2 배너 부재는 요청문 필수 절이 정의한 유효 종료 상태 — blocker 4군은 전부 Placement 밖/재료 축.)

## ⑤ 기계 3축 (하네스 실측 봉인 값 — 재실행 금지·그대로 기재)

| 축 | 봉인 값 | 조정자 부기(read-only 실물 확인) |
|---|---|---|
| **A축** openapi shape | 성공(2xx) 경로 정규화(`--success-only`) **diff 0** — `docs/rebuild/products/api_shape_pre_success.json` 대비 | 컨트롤러 선언·`ProductOut` 5필드 required·파라미터 0 이 shape 정본과 정합(`schema_out.py:1-12`·OpenAPI 인수 테스트가 같은 계약을 단언 `test_product_catalog_openapi.py:36-75`) |
| **B축** pytest(make test·직렬) | **6,857 passed · 1 skipped · red 0**(172.56s·exit 0) — 앵커 baseline 6,705+1skip 대비 **+152 전부 green** | 1 skip = `application/entitlements/test/integration/published_service/test_entitlement_grant_v1_acceptance.py:343` pre-existing `importorskip`(구 products 경로 가드) — **무편집 실물 확인**: `git diff 5630e2f2..164332d -- application/entitlements/` = **0줄**. 단 가드 대상이 V1 경로(`…infra_layer.django_products…`)라 신 트리(`driven_layer`)에서는 products 존재해도 **영구 skip**(잔여 결점 2 — Placement 상 코더 수리 불가·정당) |
| **C축** registry/migration | registry_gate(`--anchor 5630e2f2`·`--legacy-debt-file docs/rebuild/products/legacy_debt.txt`) **exit 0 · 귀속(N∖L) 0 · legacy 잔존 5,406 · 해소 1** / bc_registry_run(. products) exit 2 — 실발화 = **#12 ParentAuth import 1건(승인 빚 목록 내)** + ⓓ#153 물음 1건(exit 불산입) / migration_gate exit 2 — 잔존 53 전부 타 BC(products 0) | #12 실물 확인: `product_catalog_controller.py:5` `from application.accounts.presentation_layer.authentication import ParentAuth` — spec §9 가 고정한 유일 legacy 결합·`legacy_debt.txt` 1행과 일치. ⓓ#153 은 아래 «ⓓ 물음 처리»에서 **정당** 판정 |

## r2′ 충돌 4축 재발 검증 (이 라운드 최대 관전점 — 전부 실물 grep)

| 축 | r2′ 좌초 모양 | r2″ 실물 | 판정 |
|---|---|---|---|
| ⓐ OHS 창구 명명(#482) | spec §6 축자 `get_purchasable_product_v1` ↔ `_query` 접미 표준 충돌 | `purchasable_product_catalog_service.py:21` **`get_purchasable_product_query(request) -> GetPurchasableProductResponse`** — module-level 함수 1개·`_query` 접미 | ✅ **재발 0** |
| ⓑ 계약 클래스 V-접미(#170·#483/#484) | `PurchasableProductV1`·`…V1Request` 등 V-접미 축자 | `grep -rE "V1\|_v1\|V2\|_v2" application/products scripts/seed_temp_products.py` = **0건**. 계약 클래스 = `GetPurchasableProductRequest`/`GetPurchasableProductResponse`(`contract/request/…:5`·`contract/response/…:6`) · V1 의 `CatalogProductStateInvalidV2` 도 `CatalogProductStateInvalid` 로 무-V 개명 | ✅ **재발 0** |
| ⓒ 오류 갈래 모양(#453/#454/#455/#456) | 부재·판매불가를 V1 예외 3종으로 축자 | 부재·판매불가 = **답 갈래** `code: Literal["FOUND","NOT_FOUND","NOT_PURCHASABLE"]`(response dataclass·자유 문자열 reason 0 — #455 코드 값) · 저장 오염은 published 예외 갈래 아님 — `CatalogProductStateInvalid` 자연 전파(#456·`purchasable_product_catalog_service.py` 에 try/except 0) · 구조 기저 `PurchasableProductCatalogPublishedError` 만 트리 31행 칸에 선언·raise 지점 0 | ✅ **재발 0** |
| ⓓ admin 칸(#462·트리 82~87) | spec §4 축자가 표준 admin 트리와 충돌 | `driven_layer/django_products/admin/product/` = **`panel.py`(선언+thin hook 위임만·`admin.site.register`) + `form/product_form.py`(도메인 값 객체 선검증) + `feature/{create,replace,delete}_product.py`(파일당 공개 정의 1개·유스케이스 1회 호출)** — #462 면제 내 ORM 사용·`panel.py` 에 `.objects`/transaction/판정 0 | ✅ **재발 0** |

**r2′ respin(spec §6/§4 표준형 개정 + preflight ⑽)의 목적 축 4/4 봉쇄 실증.** 부기: r2′ 레인 B가 과대 프레임했던 «~50건» 축의 재등장도 0 — 이 라운드 STOP 은 (b)를 (a)로 묶지 않았다(아래 STOP 질).

## A. TIER-S 척추 — S-DDD

| ID | 항목 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| SD-1 | 빈혈: 판정 소유 | 핵심 판정 전부 도메인 소유 — `product.py:171-172` `is_purchasable(on=KstSaleDate)`(활성+양끝 포함 기간) · `:119-163` `replace` 후보 7필드 전건 검증→원자 swap→무변경 False · `:165-169` `activate` 멱등 · 값 경계는 값 객체 6종이 raise 로 집행(`product_name.py:19-25` trim·1..100 / `token_limit.py`·`price_krw.py`·`product_id.py` 정확 int·bool 거부·int64 / `sale_period.py:20-27` date-only·순서 / `kst_sale_date.py:19-27` aware→KST·naive 거부) | ✅ | ✅ | ✅ | ✅ |
| SD-2 | 빈혈: 프로덕션 호출 | 조회→도메인 판정→저장 실호출 — `list_…use_case.py:36` `product.is_purchasable(on=sale_date)` · `replace_…use_case.py:60` `product.replace(…)`→`repository.save` · `manage_temp…:_activate_once` `product.activate()`→save · 생성 `Product.create`→save(`create_…use_case.py:36-48`) · HTTP/admin/OHS/script 전 입구가 use case 경유(`product_catalog_controller.py:38`·admin feature 3종·`purchasable_product_catalog_service.py:26-30`·`scripts/seed_temp_products.py:69`) — `.update()`/raw SQL 우회 0 | ✅ | ✅ | ✅ | ✅ |
| SD-3 | 빈혈: 무복제 | 인프라 리포지토리에 비즈 조건 0 — `adapter/persistence/repository/product_repository.py:107-113` `_models()` = 전량 조회(+sqlite Cast 주석뿐)·`save` WHERE 는 `pk` 뿐(`:93-99`)·`is_active`/날짜 filter·F-식 판정 0(grep). 판매 가능 필터링·정렬은 응용/도메인(`list_…use_case.py:34-50`) | ✅ | ✅ | ✅ | ✅ |
| SD-4 | 애그리거트 경계 | `Product` 단일 소루트·하위 엔티티 0·cross-BC FK 0(`product_model.py` — 자기 필드 7개뿐) · 1명령=1트랜잭션(`_execute_once` 패턴) · admin delete 의 `LogEntry` 동반 기록은 동일 성공/실패 단위로 명시 승인(design §7.3 Transaction owner 행·spec §4 «삭제 이력 로그를 남긴 뒤 응답») — 근거 있는 예외 | ✅ | ✅ | ✅ | ✅ |
| SD-5 | 모델 표현력 | 값 객체 6종 전부 `@dataclass(frozen=True, slots=True)` · setter 0 · 도메인 서비스 없음(빈 칸 정당 — 판정 주어가 전부 Product) · 유비쿼터스 언어 명명(Purchasable·SalePeriod·KstSaleDate·replace/activate — design §2.1 용어표와 1:1) · `Product` 는 private slot + read-only property 로 공개 대입 차단(`product.py:17-75`, 테스트 실증 `test_product.py:131-177`) | ✅ | ✅ | ✅ | ✅ |
| SD-6 | 계층 순수성(P1a) | 결정: `grep "^(from\|import) (django\|ninja)" domain_layer application_layer` = **0건** · status/http 어휘 grep 0건. 의미: 유스케이스 Result 는 code Literal/값 필드뿐 — status DTO 흐름 0 · BC 오류 자체가 0 이라 controller 매핑 대상 없음·미식별 예외는 잡지 않고 framework 기본 흐름(중앙 handler 는 **프로젝트 소유 기존 인프라**·spec §3 이 «BC 재선언 금지»를 명시 — v5 PASS bar 의 «framework 오류 기본 처리» 그 자체). admin 의 503 매핑은 driven_layer admin 칸 로컬(spec §4 의무·HTTP controller 미공유 — `feature/*_product.py` 3곳 대칭) | ✅ | ✅ | ✅ | ✅ |
| SD-7 | 컨텍스트 통신 | 타 BC import 전수 grep: 생산 = `ParentAuth` 1건(`product_catalog_controller.py:5` — spec §9 고정·**빚 #12 목록 내**·driving 입구의 인증 표면 소비) + `framework/**` 2종(공유 소유 — BC 아님)·그 외 타 BC domain/driven import **0** · 테스트의 타 BC import 0(인증은 자기 controller 심볼 patch — `test_product_catalog_api.py:14`) · 내보내는 쪽 = 표준 OHS 트리 22~32행 전 칸 실현(계약 모듈은 stdlib+동일 contract 만 import — 독립 import 가능·`test_…contract.py` 가 signature 로 봉인) | ✅ | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR

| ID | 항목 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| SH-1 | 컨테이너 | 신규 앱 = `application/products/` 하위 · 루트 잔재 0(diff 전수 — 앵커 대비 신규 164파일 중 BC 밖은 배선 2·scripts 1·.dddjango 5·request.md(하네스 커밋 `e29b105` 귀속)뿐) | ✅ | ✅ | ✅ | ✅ |
| SH-2 | 4계층 | `{driving,application,domain,driven}_layer/` 물리 분리 실측(파일트리 전수) | ✅ | ✅ | ✅ | ✅ |
| SH-3 | 골격+거주 명명 | 고정·재등장 칸 전수 실현 — 빈 칸까지: `published_event/`·`webhook/`·`cron_job/`·`event_router.py`(0 byte)·`event_wiring.py`(0 byte)·`bc_error_schema.py`(0 byte)·`schema_in.py`(0 byte)·query UC 의 `_command.py`/command UC 의 `_query.py`(0 byte)·port `exception.py`·`entity/`·`event/`·`shared_value_object/`·`domain_service/`·`domain_bypass_query/`·`anticorruption_layer/`·`external_system/`·`test/factories/`·`test/fake/` · 거주 명명: `<use_case>_use_case.py` 공개 클래스 1·`execute(command|query)->result`·`_command/_query/_result` 어휘·`dto` 낱말 0(grep) | ✅ | ✅ | ✅ | ✅ |
| SH-4 | Django앱 위치 | `models/`·`migrations/` = `driven_layer/django_products/` 하위 · `apps.py` `name` 점경로 전체·`label="products"`(`apps.py:6-9`) · INSTALLED_APPS 등록 행은 usage_quota↔report 사이(복원 지점 §10 축자 — `settings/base.py` diff) | ✅ | ✅ | ✅ | ✅ |
| SH-5 | ORM 명명 | ORM `ProductModel`·도메인 bare `Product` — 혼동 0 | ✅ | ✅ | ✅ | — |
| SH-6 | 포트/구현 명명 | `ClockPort/SystemClockAdapter`·`DelayPort/TimeDelayAdapter`·`RetryableDatabaseFailurePort/DjangoRetryableDatabaseFailureAdapter`·`ProductDeletionAuditPort/DjangoAdminProductDeletionAuditAdapter`·`ProductRepository/DjangoProductRepository`·`ProductsUnitOfWork/DjangoProductsUnitOfWork` — `Interface`/`Impl`/약어 파일명 0(grep) | ✅ | ✅ | ✅ | — |
| SH-7 | 포트 선언 위치 | 리포지토리 선언 = `domain_layer/product/product_repository.py`(ABC+@abstractmethod) · 능력 포트 = `application_layer/port/{clock,delay,retryable_database_failure,product_deletion_audit,unit_of_work}/` 뿐 — 트리 밖 `port/` 칸·개명 변종 0 | ✅ | ✅ | ✅ | ✅ |
| SH-8 | ACL 분리 | 업스트림 소비 0 → `anticorruption_layer/` 빈 칸 실현 · repository 에 번역 어댑터 혼입 0 | ✅ | ✅ | ✅ | — |
| SH-9 | 단일 레이아웃 | `test/` 단일 — `tests/`·`src/apps` 혼용 0 | ✅ | ✅ | ✅ | — |
| SH-10 | 테스트 의미군 | `test/{unit,integration,e2e}` 의미군 분리 15모듈 — HTTP/OpenAPI/admin/persistence=integration·CLI=e2e·도메인/응용/OHS=unit(전수 실측·오배치 0) | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA (HTTP operation 1개 존재 → 채점)

| ID | 항목 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명(조건부) |
|---|---|---|---|---|---|---|
| NJ-1 | 스택 채택 | `@api_controller("/products", tags=["products"], auth=ParentAuth(), auto_import=False)` 클래스 컨트롤러 + side-effect-free registrar `register_products_api(api)` → `api.register_controllers`(`api_router.py:8-11`) · 단일 프로젝트 `NinjaExtraAPI` 에 등록(`urls.py` diff — 명시 호출) · plain view/JsonResponse/DRF 0 | ✅ | ✅ | ✅ | ✅ |
| NJ-2 | operation 얇음 | 본문 = use case 1회 호출 → `ProductOut` 매핑 → `Status(200, …)` 반환(`product_catalog_controller.py:36-52`) — json.loads/수동검증/ORM/비즈 분기 0(정렬·필터링도 응용 소유) | ✅ | ✅ | ✅ | ✅ |
| NJ-3 | Schema 입출력 분리 | 출력 `ProductOut(Schema)` 5필드(`schema_out.py`) · 입력 표면 없음 → `schema_in.py` 빈 칸 실현 · 도메인 객체 직렬화 0(응용 Result→ProductOut 명시 매핑) | ✅ | ✅ | ✅ | — (강) |
| NJ-4 | BC 오류 OpenAPI 선언 | 결정 ❌: **봉인 STOP 축** — registry #5 scope-render exit 2(직접 BC 반환 없는 401/503 광고 판정). 의미 ✅: 선언은 `response={200: list[ProductOut], 401: FrameworkErrorSchema, 503: FrameworkErrorSchema}`(`controller:26-30`) — **<Bc>ErrorSchema 아닌 공용 FrameworkErrorSchema**(v5 FAIL 문면 «framework status 를 <Bc>ErrorSchema 로 거짓 광고» 비해당)·spec §3 이 «상태 코드 선언 집합 GET 200·401·503» 을 명시 고정·wire 실물과 일치(인수 테스트 401/503 problem smoke) · `openapi_extra`/후가공 0 | ❌ | ✅ | 🟡 | — (강) |
| NJ-5 | operation 문서화 | `operation_id="listPurchasableProducts"`·`summary`·`description`·`tags` · 반환 타입 `Status[list[ProductOut]]` — 무정보/어댑터 누수형 0 | ✅ | ✅ | ✅ | — (경미) |
| NJ-6 | ninja 버전 핀 | 신규 도입 없음 — 기존 관례 유지(`pyproject.toml:8-9` `django-ninja>=1.6.2`·`django-ninja-extra>=0.31.5` 핀 기존재·manifest diff 0) | ✅ | ✅ | ✅ | — (경미) |
| NJ-7 | BC 오류 직접 계약 | BC 실패 갈래 0(목록 조회 도메인 실패 없음 — spec §3) → controller try/except 0·helper/handler/factory/catch-all 0·raw 오류 응답 0 — 미식별·framework 오류는 기본 흐름 그대로(v5 PASS 문면 «미식별 예외는 잡지 않는다» 축자). admin feature 의 좁은 `except OperationalError`+술어 후 재raise 는 Ninja controller 밖 별도 표면(spec §4 의무) — NJ-7 주어 아님 | ✅ | ✅ | ✅ | — (강) |

## TIER-S(핵심) — FC

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| FC-1 | 골든 오라클 | **⏸️ 미인증** — products 분 골든 행위표 공백 지속(사전등록 재료 부재·4라운드+) + read-only 채점이라 실행 금지. 대리 관찰(판정 아님): 봉인 B축 +152 green·인수 테스트가 spec 행위(정렬·양끝 포함·no-op·멱등 seed·5필드)를 exact 값으로 두드림 | ⏸️ | ⏸️ | ⏸️ | ⏸️ |
| FC-2 | 테스트 비-vacuous | **⏸️ 미인증** — mutation 주입·실행 금지. 대리 관찰(판정 아님): 단언 밀도 상급 — exact 문자열 스냅샷(`test_seed_temp_products.py:50-51`)·경계 양측 parametrize(`test_product.py:21-97`)·예외 identity `is` 단언(`test_product_write_retry.py:336·476`)·정렬 전체 배열 비교(`test_product_catalog_api.py:91-113`) — 형태상 M1/M2/M3 를 red 시킬 단언이 실재 | ⏸️ | ⏸️ | ⏸️ | ⏸️ |
| FC-3 | 도메인 정합(negative gate) | 명백 도메인 오류 0 — 판매 가능 = 활성∧양끝 포함(`sale_period.contains` `start<=d<=end`)·생성 항상 비활성(`create` 하드코딩 `is_active=False`)·정렬 `(price, id)` 오름차순·KST 1회 결정(clock 1회→전 항목 재사용·테스트 실증)·hard delete·재시도 1회/25ms/생성 무재시도 — 역전·음수·인과 오류 0 | ✅ | ➖ | ✅ | ✅ |

## C. 기존규약 마스크 (적용 메모)

| 질문 | Y/N | 근거 |
|---|---|---|
| MQ0 기존 앱이 이번 런에서 삭제·대체? | **N** | V1 products 삭제는 앵커 이전 하네스 준비 소관 — 이 런 기동 시점(`e29b1059`)에 `application/products/` 물리 부재(`refactor-scope.md:6-7` + 조정자 git 실측) |
| MQ1 런 변경 집합에 핵심 규칙 분기? | Y(신규 앱 자체) | 신규 BC 전체가 이 런의 산출 — §0 전부 강제 경로 |
| MQ2 판정 없는 단순 데이터소스인가? | N | 판정 소유 BC(판매 가능·값 경계·no-op) — 도메인 실코드 의무 → SD-1~3 교차 충족(위) |

> **마스크 결론**: 순수 greenfield — §0 전부 강제, 전부 충족(SH-1~4 ✅).

## D. TIER-Q 품질

| ID | 항목 | Result(조정자 검증) | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|
| Q-1 | 스코프/과설계·G1 | 요청 외 발명 0 — 페이지네이션/필터/단건 HTTP/soft delete/CAS/Idempotency-Key/이벤트/outbox 전부 불채택(설계 §8·§17 근거 동반) · `after_commit` capability·`save` 의 `_events` 가드는 표준 트리 UoW/lifecycle 계약 실현(#197·#545 계열 — 기능 발명 아님·호출 0 명시) · scope.md «Out of scope» 준수 실측 · 고-blast 결정(Z1·Z2)은 STOP 상정 후 대리 입력으로 확정 — 사후기록 아님 | ✅ | ✅ | ✅ |
| Q-2 | 선택 error profile 계약 일관성 | 소유 profile=dddjango-code-json + RFC 9457 runtime wire — spec §3 이 두 축 조합을 명시 승인(사용자 정본). wire 일관 실측: `application/problem+json`·type URI base·401+`WWW-Authenticate: Bearer`·503+`Retry-After: 1`·500 무헤더 — 인수 테스트가 slug·헤더까지 smoke(`test_product_catalog_api.py:45-48·120-121·140-141·180-181`) · profile 혼합/드리프트 0(BC 는 오류 생성 0·중앙 계약 재선언 0) | ➖ | ✅ | ✅ |
| Q-3 | Risky Write 형식+테스트 실현 | 8행 consistency block 전 행 기입(design §7.3 — Idempotency storage «미적용(알려진 한계)» 정직 표기) · 실현 테스트: row lock timeout(0.5~3.0s 창 단언)·`SET LOCAL` 진입 실패 unwind·rollback 후 새 물리 트랜잭션(`txid_current` 비교)·SQLite IMMEDIATE 경합·transient 1회/2차 전파/비인식 무재시도·delete+LogEntry 원자성/중복 로그 0 — **전부 Event-순서 결정적**(`Event.wait` 선행 보장 — Barrier 레이스 아님·`test_product_write_locking.py:146-174`) | ✅ | ✅ | ✅ |
| Q-4 | 메커니즘 소유권 **[🔴치명]** | 커스텀 backend/`DatabaseWrapper` 상속/PRAGMA 쓰기/monkeypatch 0(grep) — UoW 는 표준 `transaction.atomic(durable=True)`·sqlite 는 stock `OPTIONS={timeout, transaction_mode:"IMMEDIATE"}` alias(테스트 소유 fixture·spec §2 승인)·`PRAGMA busy_timeout` 은 테스트의 읽기 단언뿐 | ✅ | ✅ | ✅ |
| Q-5 | 마이그레이션 안전 | 신규 앱 fresh `0001_initial.py` 1개(자동 생성·RunPython/RunSQL 0) — spec §7 «보존 의무 없음·새 0001» 명시 승인 · 기존 앱 0001 접촉 0·배선 행 추가만(기존 행 삭제·이동 0 — diff 실측) · DB 제약 5종 CHECK+unique 로 §2 경계 집행 | ✅ | ✅ | ✅ |
| Q-6 | 테스트/TDD | 봉인 green bar(6,857·products 152) · 함수형 pytest 전수(`TestCase` 0)·`django_db`/`transaction=True` 구분 사용·`mocker`·`monkeypatch`·`capsys` · 인수가 spec 행위 축자(§8 관찰 목록 1~10 전 항 대응 테스트 실재 — 401/503/500·정렬·admin 8컬럼/일괄삭제 부재/로그 원자성·seed 멱등/보존/dry-run) · 테스트는 spec 직접 도출(옛 테스트 부재 — 클린룸 diff 실측) | ✅ | ✅ | ✅ |
| Q-7 | 경미 | 어노테이션 전수에 가까움 — 모듈 상수 `Final` 타입·클래스 속성·지역 변수 첫 대입까지(전 파일 표본 일치) · 주석/docstring 한국어 일관 · 의존성 핀 기존 관례 유지 · 경미 부기: `register_products_api(api: Any)`(순환 회피 의도로 보이나 `NinjaExtraAPI` 타입 가능)·Django private 표면 접촉(`_changeform_view`/`_delete_view`/`_state` 조작/`_from_testcase`) — 전부 design §12·§7.2 에 근거·범위 명시된 의도적 결정이라 WEAK 강등 안 함 | ✅ | ✅ | ✅ |

## 의미적 변종 / backstop-blind 메타

| ID | 결정 근거 | 의미 근거 | 종합 영향 |
|---|---|---|---|
| (해당 없음) | [결정 PASS ∧ 의미 FAIL] 0건 | — | — |
| NJ-4(역방향) | registry #5 scope-render **exit 2**(봉인 — 직접 BC 반환 없는 401/503 광고) | 선언 스키마는 공용 `FrameworkErrorSchema`(BC Schema 아님)·spec §3 이 선언 집합을 명시 고정·wire 와 일치 — v5 NJ-4 FAIL 문면 비해당 | 종합 🟡(WEAK) — 이 충돌은 산출물 흠이 아니라 **spec §3 ↔ 검사기 #5 문면의 재료 축**(봉인 STOP (a) 그대로) · '강' FAIL 아님 → 품질 상한 강등 없음 |

**Goodhart 관측**: 검사기 회피용 alias·개명·후가공 0 — 오히려 검사기가 요구하는 방향(#597 save/remove·#389 실 DB 신호·#390 실입구)으로 산출물을 교정한 이력이 STOP 파일에 남아 있고 실물과 일치한다.

## TIER-OBS — 에러 경로 관측 (EP · 비채점)

> read-only 채점 — probe 실행 금지. 라이브 probe 없음(➖). 아래는 인수 테스트가 대리한 계약 관측 기록이다(라벨 무영향).

| 키 | 관측 | 판정 |
|---|---|---|
| EP-1 깨진 본문 | ➖ — GET 단일 표면·본문 없음(spec §3 «스키마 검증 422 갈래 부재») | ➖ |
| EP-2 요청 검증 | ➖ — 파라미터·본문 축 자체 없음 | ➖ |
| EP-3 인프라/retryable | 테스트 대리 관측: 중앙 인식 transient → 503+`Retry-After: 1`+problem slug / raw `55P03`(중앙 미인식)·permanent → 500 `internal-error`·`Retry-After` 부재(`test_product_catalog_api.py:124-181`) — Z1 판독 그대로 | (대리) 계약 정합 |
| EP-4 재고 부족 | ➖ — 이 태스크에 재고 축 없음 | ➖ |

## ⓓ 물음 처리 (#153 — exit 불산입·채점자 판정)

- **물음**: `purchasable_product_catalog_service.py:21`(= `def get_purchasable_product_query`) — «유스케이스 호출 2회».
- **실물**: 함수 본문의 use-case 관련 호출은 `build_get_purchasable_product_use_case()`(`:26` — composition root 빌더)와 `use_case.execute(query)`(`:30`) 두 개다. **실행(`execute`)은 정확히 1회** — 나머지 1건은 조립 호출이며, OHS 는 driving 입구라 자기 BC composition root 를 부르는 것이 표준 배선이다(design §4.1 «execute 정확히 1회» 문면과 실물 일치).
- **판정: 정당** — 정적 계수가 빌더 호출을 «유스케이스 호출»로 합산한 오탐성 물음. 산출물 수정 불요.

## STOP 질 평가 (정지 이력 전건 — 하네스 관측 원자료 + 실물 대조)

| 정지 | 분류·형식 | 판정 |
|---|---|---|
| G1 STOP 2축(Z1 `55P03` wire·Z2 OpenAPI 헤더) — 04:54 | (a)=2·(b)=0 · 축마다 닫힌 선택지 3개 + **대가 한 줄 전건** · «권고 불가» 규율 준수(방향 권고 0·선반영 0) · 정지 전 공백 전수 일괄 상정 | ✅ 형식 전 항 충족. 내용도 정당 — 둘 다 밖-가시 wire/문서 계약 갈림. 해소는 spec §3 문면 정박(대리 입력=하네스·**선택지 확장 없음** — Decision record 에 주체·시각 기록) — 자가 승인 0 |
| 수렴 정지 1(68→71) — 05:45 | 문면 축자 적용(재설계 후 파일 수 증가=정지) → 사용자(대리 입력) 오탐 정정·1회성 override 소비 기록 | ✅ 보수적 정지 자체는 문면 충실 — 오버런 아님. override 범위 한정 기록 정확 |
| 수렴 정지 2(Slice 1 registry 0→7) — 07:01 | 초기 `TREE_CONTRACT_MISMATCH` 프레임 → **07:08 정정에서 7건 전부 (b) 자가 수리로 재분류**(#107/#329/#351=중간 상태·#597×2=승인 설계 명명 결함·#389/#390=테스트 신호 강화) | 🟡→✅ 초기 분류는 과대 프레임 성분이 있었으나(구현 중간 스냅샷을 수렴 신호로 오적용) 정정이 정확했고, **재분류한 (b) 전건이 실물에서 수리 완수 실증** — save/remove 전면(선언·어댑터·유스케이스·테스트 더블 grep 0 alias)·#389(`django_db` 마커+실 mounted `/v1/openapi.json`)·#390(`runpy.run_path(run_name="__main__")` 실입구). 코더 report 의 exit-0 허위를 감사가 잡아낸 것도 이 정지의 산물(자기보고 불신 작동) |
| G2 최종 STOP(4 검사기군) — 14:34 | **(a)=4·(b)=0** · `TREE_CONTRACT_MISMATCH`+`G2_BLOCKER` 토큰 · 정지 후 산출물 무변경 선언 | ✅ 분류 정확성 실물 대조: #2=legacy child/parent 동적 StrEnum(Placement 밖) · #5=spec §3 «401·503 선언» 강제 ↔ 검사기 광고 금지(진성 재료 충돌 — 본 결과지 NJ-4 🟡 와 동일 축) · #6=전역 스캔이 legacy+spec 강제 ParentAuth 를 직접 차단(빚 파일은 registry_gate 전용 — 스코프-렌더 면제 불가) · #16=`broccoli_server/api.py` #437·`urls.py` #441(Placement 밖). **넷 다 products 수리 경로 부재 — (b) 은닉 0·과대/과소 프레임 0.** G2 배너 금지 판단·중단 커밋 규약 축자 이행 |

**종합: STOP 질 «상»** — 자기 해석으로 넘은 비위임 결정 0·자가 승인 0·(b)→(a) 세탁 0·정정 이력 투명. r2′ 대비 개선 축(과대 프레임)이 실측으로 닫혔다.

## 자기보고 검증 (필수 검증 2 — 전건 실물)

| 주장 | 실측 | 판정 |
|---|---|---|
| products 테스트 152개 실재 | 테스트 모듈 15·함수 88 + parametrize 21개소 전개(수집 재실행은 금지 — 정적 대조) → **봉인 B축 «products 152 passed» 와 정합**(봉인 값이 1차 오라클) | ✅ |
| #597 어휘 교정(save/remove) 완수 | 선언(`product_repository.py:39-74`)·어댑터(`:74·:100`)·유스케이스 전부·테스트 더블(`test_product_writes.py:108·123`·`test_manage_temp_product.py:112·134`) — `def add`/`def delete` **0건**(grep) | ✅ |
| 설계 상태의 design-spec.md 반영 | 상태줄 «구현·테스트 완료, G2 차단 — …G2 배너 불가»(`design-spec.md:3`) · §15 사전 대조 표 26행·§11 입장표 34행(add 22=실물 15모듈과 owner 경로 1:1)·§10.3 트리=실물 파일트리 일치(admitted test .py 15 = 실측 15) | ✅ |
| Placement 준수 | 앵커 대비 변경 164파일 = products 155 + `.dddjango/**` 5 + `settings/base.py` **1행 추가** + `urls.py` **2행 추가**(import+호출·기존 행 이동 0) + `scripts/seed_temp_products.py` 신설 1 + `request.md`(하네스 커밋 `e29b105` 귀속 — 코더 docs 변경 0) · 빚 파일 가필 0 | ✅ |

## 잔여 결점 (이월 포함)

1. **[이월] FC-1 골든 행위표 products 분 공백** — r2·r2′·r2″ 연속. 사전등록 없이는 FC 게이트가 영구 ⏸️ — 정적 «준수» 완전 선언 불가의 유일 축.
2. **[신규 관측·재료 귀책] entitlements retain 가드의 영구 skip** — `test_entitlement_grant_v1_acceptance.py:343` `importorskip("application.products.infra_layer.…")` 이 V1 경로를 겨눠, 신 트리(`driven_layer`)에서는 products 가 존재해도 해당 시나리오가 계속 skip 된다. Placement 상 코더 수리 불가(무편집 정당) — 후속 정리 큐 대상.
3. **[재료 축] NJ-4 = spec §3 선언 집합 ↔ 검사기 #5 문면 충돌** — 봉인 G2 STOP (a) 축의 채점면 대응(본 결과지 유일 🟡). 해소 주체는 표준/검사기 또는 spec 개정 — 산출물 아님.
4. **[재료 축] G2 직접-실행 4종 미봉인**(#2 legacy StrEnum·#5·#6·#16) — 전부 Placement 밖. 이 축이 닫히기 전에는 같은 조건의 어떤 산출물도 G2 배너 불가.
5. **[경미] 재시도 궤도의 `except BaseException` 3개소**(replace/delete/temp) — 비인식 즉시 재raise 라 동작 보존이나 KeyboardInterrupt/SystemExit 도 분류기를 경유. 구체 예외 튜플로 좁힐 여지.
6. **[경미] `GetPurchasableProductResponse` 가 non-frozen dataclass**(request 는 frozen) — 공개 계약 불변성 비대칭.
7. **[경미] Django private 표면 접촉**(`_changeform_view`/`_delete_view`·`obj._state` 조작·`_from_testcase`) — design §12·§7.2 에 근거·범위 명시된 의도적 결정이나 Django 버전 상향 시 취약 표면. `register_products_api(api: Any)` 타입도 좁힐 여지.

## 조정자 노트

- 결정 레인 봉인 값(⑤)과 조정자 read-only 실측 사이 모순 0. 채점 중 픽스처 변화 없음(mtime·clean 확인).
- 이 결과지의 치명 게이트 판정은 «FAIL 0 · FC-1/2 미인증»이다 — «치명 전부 통과» 로 읽지 말 것(§4.2 조건 3 미실측). 스트릭·라운드 계상은 사용자 몫.
- Serena: skipped — read-only 채점(픽스처 외부·심볼 편집 0)이라 기본 도구로 충분.
