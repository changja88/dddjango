# 채점 결과지 — pdrebuildlive-claude (BC 클린룸 리빌드 S3-r2″ · 레인 A · ⑤/⑥a)

> **방법**: EVAL-METHOD **v5 frozen** · **identity**: `2026-08-08-tree-revision` + `dddjango-code-json` + `v5-candidate` + dimension ID · **채점일** 2026-08-15 13:39 · **픽스처** `/Users/hyun/Desktop/broccoli-rebuild`(브랜치 `rebuild/standard-tree` · 채점 대상 커밋 `41935cfd` — products 클린룸 재구현·기동 HEAD `e29b1059` 대비 **149파일 +5,855·삭제 0** · working tree clean=런-정지 확인) · **런타임** dddjango(Claude Code) **plugin 2.8.0** · 재구현 세션 **Claude Opus 4.8(레인 모델 고정)** · **앵커** `5630e2f2`(r2″ respin — spec §6/§4 표준형 개정+preflight ⑽) · 실행 실동작 ~5h12m+α(벽시계 10h58m — 차이는 하네스 감시 방치 4h33m+승인 대기·레인 귀책 0) · **태스크** 판매용 상품 카탈로그 BC 6 유스케이스(`GET /v1/products` 목록·동기 OHS 단건·admin 생성/수정/삭제·seed 스크립트 · KST 기준일 1회 결정·전체 교체·무변경 no-op·인식 transient 1회 재시도·hard delete · 오류 프로필 **dddjango-code-json**·wire=RFC 9457 problem+json 모양·**BC 고유 오류 slug 0**).
> **라운드 문맥**: S3-r2″ — 직전 r2′ 는 **양 레인 STOP**(spec §6 OHS·§4 admin 의 V1 계약 «이름·모양» 축자 ↔ 표준 #170/#453/#454/#482/#484/#456/#462 근본 충돌·귀속 52/66). 이번 라운드는 spec §6 «축자의 경계» 선언+§4 admin 칸 표준형 개정+플러그인 v2.8.0(#462 admin 면제·composition subclass)+preflight ⑽(계약 표면 8종 사전 대조) **이후의 재발 검증 라운드**다. 삭제된 직전 판=V1 원본(r2 앵커 `b927a275` 가 삭제 — 옛 구현·테스트 대조 기준=`b927a275^`, 부록 A).
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ⏸️ 보류/미인증 · ➖ N/A.
> **⚠️ 필수 단서**:
> - **결정 레인 = 하네스 실측 봉인 값**(⑤ 3축·registry_gate·migration_gate·bc_registry_run — 재실행 금지 지시 준수). **의미 레인 = 독립 AI 채점자 1인**(재구현·재료 준비 비참여·read-only 정독) — `N_grader=1`(κ 미보고). 형식 eval «완료» 대용 아님.
> - **FC-1 골든 행위표: products 분 미확보**(`workspace/eval/golden/` 실측 — billing 분만 존재) — FC 축은 대체 관측·동결 방법의 FC 인증 아님(⏸️). **4라운드 연속 공백**(psrebuild·csrebuild 계보 지속).
> - **클린룸·세션 감사 = 하네스 관측 원자료**: STOP 0 · 판단 개입 0 · 대리 답변 0 · 도구-실행 승인 ~45회 전부 read-only 탐색/허용 경로/검증 명령.
> - **자기보고 불신 집행**: 완주 보고의 «구현 중 설계 교정» 7건을 조정자가 산출물·표준 문면(설치본 2.8.0)으로 독립 검증 — 전건 ⑴ 외부 계약 불변 ⑵ 표준 문면 실재 ⑶ 비위임 비침범 확인(조정자 노트 ②).
> - **fixture 도구 환경(env/produced/used)**: env=픽스처 `.venv`(python 3.14·pytest-django·pytest-mock·factory_boy 기존 스택) · produced=이번 런 신규 테스트 도구 추가·핀 0(기존 재사용) · used=pytest 함수형(`def test_*`+`@pytest.mark.django_db` 9파일)·`mocker`(`MockerFixture` 5파일)·factory_boy(`test/factories/product_model_factory.py:21` `DjangoModelFactory`)·fake ABC(`test/fake/__init__.py` — ClockPort/Repo/UoW/RetryPort 4종)·`unittest.mock`/`TestCase` 출현 0(grep 실측) · 조정자 추가 도구 0.

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① C 마스크 | **MQ0=Y**(r2 앵커 `b927a275` 가 V1 원본 삭제·이 런이 재생성 — 승인 트랙) → **MQ1=Y ∧ MQ2=N**(판매 가능 판정·값 경계 5종·전체 교체 no-op·KST 1회 결정 적재) → §0 전부 강제 + 도메인 실코드 의무 → **충족** |
| ② 치명 게이트 | **FAIL 0** — SD-1~7·SH-1·2·3·4·7·NJ-1·2·Q-4 전부 통과(의미 레인 포함·치명 후보 0) |
| ②.5 실질성 관문 | degenerate 0 — 도메인 판정 실코드(VO 6종·`is_purchasable_on`·`replace`)·비-vacuous 단언 실재. 빈 골격 66파일은 전부 §632-(2)/#488 의무 골격(설계 §A 명문·귀속 0) |
| ③ 비치명·의미변종 | `[결정PASS∧의미FAIL]` 0 — 관찰 5건은 전부 해석 지점/주의 보고(아래 메타) |
| ④ TIER-Q 등급 | **상** — FAIL 0 · WEAK 1(Q-7 — 테스트 모듈 상수·헬퍼 무어노테이션, parent/child 동형) |

> **한 줄 요지**: **⑤ 3축 전부 green + 치명 0 + Q 상 + STOP 0 — r2·r2′ 두 번의 유효 정지 끝에 products 가 처음으로 완주·통과했고, r2′ 를 정지시킨 충돌 4축(OHS 명명·모양·admin 칸)이 전 축 재발 0 으로 소멸했다.** spec §6 «축자의 경계» 선언·§4 표준형 개정·v2.8.0(#462)·preflight ⑽ 의 조합이 설계 §K 사전 대조표(BLOCKER 0)로 이어져 G2 귀속 0 을 냈다 — 재료 결함이 제거되면 이 레인은 표준 문면 기준 결함 0 산출물을 낸다는 실증. 구현 중 설계 교정 7건은 전부 표준 검사기 문면이 강제한 내부 교정(외부 계약 불변)으로 검증됐다.
> **2차원 라벨**: (정적: 준수 — FC ⏸️ 단서) × (라이브: 미검증 — 위반주입·EP probe 라운드 범위 밖).
> **라운드 판정: ⑤ 문면 통과 · ⑥a 치명 0·Q 상** — **결정 주체 관측: 자기 해석 2(둘 다 실물 근거·외부 결과 비갈림 — 조정자 노트 ③) · 자가 승인 0(G2 BLOCKER 0·빚 가필 0·Placement 이탈 0·배너 override 정직 표기) · STOP 0**. 스트릭 계상은 사용자 몫.

## ⑤ 기계 3축 (하네스 실측 봉인 · python 3.14)

| 축 | 결과 |
|---|---|
| **A축** openapi shape | ✅ **성공(2xx) 경로 정규화 diff 0** — `api_shape_pre_success.json` 대비(`--success-only`) |
| **B축** pytest | ✅ **6834 passed · 1 skipped · red 0**(143.54s·exit 0) — 앵커 baseline 6705+1skip 대비 **+129 전부 green**(조정자 검산: 신규 테스트 함수 123 + parametrize 전개 = 129 수집 정합 — unit 70·integration 49·e2e 4). 1 skip = `application/entitlements/.../test_entitlement_grant_v1_acceptance.py:343` pre-existing importorskip(구 products 경로 가드·spec §J retain·무편집) |
| **C축** | registry_gate(`--anchor 5630e2f2`·정본 빚 파일) **귀속(N∖L) 0·exit 0** · migration_gate 잔존 53 전부 타 BC(products 0) · bc_registry_run: products 경로 실발화 = **#12 `application.accounts.presentation_layer.authentication` import 1건 = 빚 목록 내**(`product_controller.py:37` 상당 — ParentAuth) · ⓓ 물음 5건(exit 불산입 — 아래 ⓓ 절) · 나머지 발화 전부 타 BC 앵커 기존분(귀속 0 이 차분 0 실증) |

- **빚 규율**: 앵커 빚 파일 3행(#12/#385/#389 accounts) 중 실발화 **#12 하나**. #385/#389(타 BC test 모듈 import)는 e2e·integration 이 인증 arrange 를 **프로덕션 HTTP**(accounts 소셜로그인 `POST /v1/auth/social-login`)로 지어 원천 미발화. **빚 파일 가필 0 · `docs/**` 레인 무접촉**(레인 자체 diff = 순수 추가 149파일+배선 2파일 행 추가 — `docs/rebuild/products/request.md` 의 M 은 하네스 앵커-해시 순환 커밋 `e29b1059` 몫, 레인 diff 밖 실측).
- **Placement 준수 실측**: `broccoli_server/settings/base.py` INSTALLED_APPS 1행(usage_quota↔report 사이)·`urls.py` import 1행+`register_products_api(api)` 1행(`legacy_api_patterns` 스냅샷 앞) — **기존 행 삭제·이동·재정렬 0**(git diff 정독). `scripts/seed_temp_products.py` 1파일 신설(허용 ⑷)·다른 scripts/ 무접촉.

### r2′ 충돌 4축 재발 검증 (이 라운드의 최대 관전점)

| r2′ STOP 축 (귀속 52/66 의 근원) | 이번 산출물 실물 | 재발 |
|---|---|---|
| OHS 창구 명명 — V1 `get_purchasable_product_v1` 축자 ↔ #482 | `get_purchasable_product_service.py:37` **`get_purchasable_product_query`**(`_query` 접미) | **0** |
| 계약 클래스 — `…V1Request`/`PurchasableProductV1` V-접미 ↔ #483/#484·#170 | `GetPurchasableProductRequest`/`GetPurchasableProductResponse`(중첩 Outcome·Payload+재노출 별칭) — 저장소 전체 V-접미·`_v1` 심볼 grep **0건** | **0** |
| 갈래 모양 — V1 예외형 not-found/not-purchasable ↔ #453/#454/#455·#456 | **답 갈래 outcome StrEnum**(FOUND/NOT_FOUND/NOT_PURCHASABLE — `get_purchasable_product_response.py:38-42`)·published 예외 0(`contract/exception/…published_error.py` **0바이트**)·오염=VO 예외 자연 전파(`repository/product_repository.py:96-107` reconstitute) | **0** |
| admin 칸 — §4 축자 ↔ 표준 트리·#462 | `driven_layer/django_products/admin/product/`(panel.py·form/·feature/) — ORM 취급은 #462(v2.8.0) 면제 칸 안·registry 귀속 0 | **0** |

preflight ⑽ 8표면 사전 대조 ↔ 설계 §K(계약 표면 대조표·**BLOCKER 없음** 명문) ↔ 최종 트리 3자 일치. **⑽ 신설 효과 실증**: r2′ 가 G2 완주(2h33m~3h26m) 후에야 백스톱으로 드러낸 충돌을 이번엔 G1 전 대조로 선소거 — 같은 레인·같은 BC 에서 STOP 0·귀속 0.

## A. TIER-S 척추 — S-DDD (의미 레인 정독 + 조정자 grep)

| ID | Result(줄 인용) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|
| SD-1 판정소유 | 값 경계 5종 = VO `__post_init__`(`product_name.py:18-24` trim 후 1..100 · `token_limit.py:23-25` bool 위장 거부 `type(...) is not int` · `price_krw.py:18-19` 0 허용 · `sale_period.py:20-31` datetime 계열 거부 non-exact+`end<start` 거부 · `product_id.py:17-18`) · 판매 가능 판정 `product.py:122-126`(`is_active and start<=ref<=end` 양끝 포함) · 전체 교체·무변경 no-op `product.py:105-120`(VO 동등성·bool 반환) · 생성 항상 비활성 `product.py:56-64` · KST 파생·naive 거부 `sale_reference_date.py:36-38`(VO 팩토리 소유·#307) — 전부 domain_layer 실재 | ➖ | ✅ | ✅ | ✅ |
| SD-2 프로덕션 호출 | create `create_product_use_case.py:38-50`(`Product.create`→`with uow: save`) · update `update_product_use_case.py:50-78`(`find_by_id`→`replace`→changed 시만 `find_by_id_for_update`+`save`) · delete `delete_product_use_case.py:45-63` · admin 도 use case 경로만(`panel.py:92-140` — 직접 `obj.save()`/`obj.delete()` 0) · seed 도 동일(§H·`scripts/seed_temp_products.py:156-194`) — 죽은 도메인 메서드 0 | ➖ | ✅ | ✅ | ✅ |
| SD-3 무복제 | driven repo 필터는 식별뿐(`pk=`·`name=` — `product_repository.py:37-52`)·판정 SQL 0 · `save` 의 full-field `.update()`(`:79-87`)는 도메인 결과의 Data Mapper 반영(판정 복제 아님) · DB CHECK/UNIQUE 7종(`product_model.py:35-59`)은 **spec §7 이 명시 요구한 DB 수준 백스톱**(«값 경계·유일성·기간 순서를 DB 수준 제약으로도 집행» — 도메인 VO 가 단일 출처·§9.5 불변식 CHECK 백스톱 조항 내) — 복제 아닌 spec-forced 백스톱 | ✅ | ✅ | ✅ | ✅ |
| SD-4 애그리거트 경계 | 단일 애그리거트 `Product`·명령1=트랜잭션1(각 쓰기 use case `with uow:` 하나·서로 다른 리포지토리 쓰기 0) · 타 BC 참조 0 → **FK 자체가 0**(`product_model.py` — ForeignKey/O2O/M2M 없음) · 락 대기 상한 1s = UoW cursor(§F.3) | ✅ | ✅ | ✅ | ✅ |
| SD-5 모델 표현력 | VO 전부 `@dataclass(frozen=True, slots=True)` · command/query/result 전부 frozen dataclass · 유비쿼터스 명명(purchasable·sale_period·replace·reconstitute·SaleReferenceDate) · 도메인 서비스 0 = 빈 고정 칸 정당(#307 — «원시 인자→원시 반환 무상태 함수는 도메인 서비스 아님» 문면 그대로 VO 화) | ✅ | ✅ | ✅ | ✅ |
| SD-6 계층 순수성 | **domain/application 의 django·ninja·pydantic import 0(조정자 grep 전수 — exit 1 무매치)** · 트랜잭션=`ProductsUnitOfWork` ABC 포트(#245 3메서드·`products_unit_of_work.py:33-52`)→driven 구현 · transient 판정·정책은 driven `DjangoTransientRetryAdapter`(`django_adapter.py:27` 만 framework import — 응용은 포트만·#7) · result 는 원시 5필드·HTTP status DTO 0 · status 선택은 controller 직소유(`product_controller.py:70` `Status(status.HTTP_200_OK, …)`) | ✅ | ✅ | ✅ | ✅ |
| SD-7 컨텍스트 통신 | 타 BC import = **accounts `ParentAuth` 1건뿐**(`product_controller.py:37` — 승인 빚 #12·목록 내·driving 층 인증 표면), 그 외 타 BC import 0(grep 전수) · 내보내는 표면 = 동기 OHS 1(표준 `open_host_service/<service>/` 골격·contract 3분리·독립 import 를 **subprocess 무설정 실증**하는 테스트까지 실재 `test_get_purchasable_product_service.py:116-157`) · 계약 dataclass 는 application_layer 도 import 하지 않음(#472) | 신호 有(#12×1 — 빚 클래스) | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR (판 = registry 위임 · 차분 귀속 0 봉인)

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| SH-1 컨테이너 | `application/products/` 하위 전수 · 루트 잔재 0(V1 은 앵커 이전 물리 삭제) | ✅ | ✅ |
| SH-2 4계층 | `{driving,application,domain,driven}_layer/` 물리 실재(V1 의 `infra_layer`/`presentation_layer` 세대 아님 — 옛 층 이름 잔존 0) | ✅ | ✅ |
| SH-3 골격+거주 명명 | 고정·재등장 칸 빈 실현 **66개 0바이트 파일 실측**(entity/·event/·domain_service/·shared_value_object/·webhook/·cron_job/·published_event/·acl/·external_system/·domain_bypass_query/×2·feature/·`event_router.py`·`event_wiring.py`·`bc_error_schema.py`·`schema_in.py`·OHS `…published_error.py`·port `exception.py`×2) · use case 폴더 **4파일 계약**(#19 — 읽기는 `_command` 빈 파일·쓰기는 `_query` 빈 파일, 5 폴더 전수 실측) · `…UseCase.execute(command|query)→result`·`dto` 낱말 0 | ✅ | ✅ |
| SH-4 Django앱 위치 | `driven_layer/django_products/{models,migrations}/` · `apps.py:11-15` `name` 점경로·`label="products"` · INSTALLED_APPS 1행 · 루트 `models.py` 0 | ✅ | ✅ |
| SH-5 ORM 명명 | `ProductModel` ↔ bare `Product` · `db_table="products_product"`(#630) | ✅ | — |
| SH-6 포트/구현 명명 | ABC 개념+역할접미(`ProductRepository`·`ProductsUnitOfWork`(#247)·`ClockPort`·`TransientRetryPort`)·구현 기술접두(`Django…`·`System…`·`system_adapter.py` #371/#373)·`Interface`/`Impl`/약어 파일명 0 | ✅ | — |
| SH-7 포트 선언 위치 | 리포지토리=`domain_layer/product/product_repository.py`(#282) · 능력 포트=`application_layer/port/{clock,transient_retry,unit_of_work,domain_bypass_query}/`(#187) — 트리 밖 port 칸 0 | ✅ | ✅ |
| SH-8 ACL 분리 | 타 BC 소비 0 → `anticorruption_layer/` 빈 placeholder 존치·N/A 성 통과 | ✅ | — |
| SH-9 단일 레이아웃 | `test/` 단일(`tests/` 공존 0) | ✅ | — |
| SH-10 테스트 의미군 | `test/{unit,integration,e2e,factories,fake}` 표준 5분류 · e2e=blackbox(구현 심볼·test 모듈 import 0 — 503 주입도 driving 컨트롤러 build_* 문자열 patch) · arrange 필요 계약은 integration 분리(설계 §J 배치 규율 명문) · unit=fake ABC 격리 | ✅ | — |

## TIER-S(조건부) — S-NINJA

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| NJ-1 스택 | ninja-extra `@api_controller("/products", tags=…, auth=ParentAuth(), auto_import=False)`(`product_controller.py:46`) + 명시 registrar `register_products_api(api)`(`api_router.py:22-23` — 인자 수취·프로젝트 api import 0·#108) · urls.py 호출 1행 · plain view/DRF/JsonResponse 0 | ✅ | ✅ |
| NJ-2 얇음 | GET 본문 = use case 호출·result→schema 투영뿐(`:63-83`) — ORM/수동 파싱/수동 검증/비즈 분기 0 | ✅ | ✅ |
| NJ-3 Schema 분리 | 출력 `PurchasableProductListItemOut` 5필드 plain Schema(`schema_out.py` — `extra="forbid"` 미사용은 shape 정본 추종·설계 §C.1 명문)·요청 없음=`schema_in.py` 빈 파일 · 도메인/ORM 직렬화 0 | ✅ | — (강) |
| NJ-4 오류 선언 | **직접 반환 BC status 0**(고유 오류 0) → 누락 축 무해당 · 401·503 은 `FrameworkErrorSchema` 로 광고(`:51-55`) — **BC 스키마 거짓 광고 0**(FrameworkErrorSchema 는 BC Schema 가 아니고 spec §3 이 선언 집합 200·401·503 을 명시 — evidence-backed·child_settings canon 동형) · 500 미선언(spec 축자) · `openapi_extra` 후가공 0 | ✅ | — (강) |
| NJ-5 문서화 | `operation_id="listPurchasableProducts"`+`summary`+`description`+컨트롤러 `tags` · 반환 타입 `Status[list[PurchasableProductListItemOut]]`(`-> object` 0) | ✅ | — (경미) |
| NJ-6 버전 핀 | 기존 스택 준용·신규 도입 0(핀 변경 불요) | ✅ | — (경미) |
| NJ-7 오류 직접 계약 | **BC 실패 0 → `try` 없음이 정합 형태**(§I slot 11 명문): helper/handler/factory/catch-all/raw 오류 응답 0 · framework 오류(401 인증·transient 503·오염/영구 500)는 전부 기본 흐름 무변형 전파 → 중앙 핸들러 소유(e2e 가 401 slug+`WWW-Authenticate`·503 slug+`Retry-After: 1` 를 wire 실증 `test_product_listing_api.py:94-127`) | ✅ | — (강) |

## TIER-S(핵심) — FC (대체 관측 — 동결 방법의 인증 아님)

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| FC-1 골든 오라클 | ⏸️ products 골든 행위표 사전등록 부재(golden/ 실측 — billing 분만·4라운드 연속) · 대체 관측: A축 diff 0 + spec §2~§6 ↔ e2e/integration/OHS 시나리오 축자 대조 충돌 후보 0 + V1 시나리오 대조 도메인 축 전 커버(부록 A) | ⏸️ | ⏸️ |
| FC-2 비-vacuous | ⏸️ mutation 미실행 · red 신호 실재(정독): 정렬 mutation 이면 red(`test_product_listing.py:104-113` — 생성 순서≠정렬 결과 arrange 후 exact 리스트 단언) · 재시도 정책 mutation 이면 red(`test_transient_retry_adapter.py:44-58` — 호출 횟수 2 고정·`excinfo.value is injected` 동일성·`sleep(0.025)` 단언) · 경계일 포함 mutation 이면 red(unit `test_purchasable_on_start_and_end_boundaries_inclusive`) · 401 우회 mutation 이면 red(e2e — auth 우회 시 200 이 됨을 주석 명문) | ⏸️ | ⏸️ |
| FC-3 도메인 정합 | 생성=비활성(활성 요청 축 자체 부재)·판매 가능=활성∧기간 내(양끝 포함·역전 0)·정렬 price asc→id asc·0원 정상·no-op 영속 생략·hard delete·재시도는 쓰기만/1회만 — unit 70+integration 49 실증·부호 반전/인과 역전 0 | ✅ | ✅ |

## C. 기존규약 마스크

MQ0=Y(r2 앵커 `b927a275` 가 V1 원본 삭제→이 런 재생성 — 프로토콜 승인 트랙) → MQ1=Y ∧ MQ2=N(판매 가능 판정·값 경계·전체 교체 no-op 적재) → §0 전부 강제+도메인 실코드 의무 — 충족. 배선 touched: `settings/base.py` INSTALLED_APPS 1행 add(usage_quota↔report 사이)·`urls.py` import 1행+registrar 호출 1행 add(`legacy_api_patterns` 스냅샷 앞 — split-brain 방어 주석 준수). **기존 행 삭제·이동·재정렬 0 · `api.py` 무접촉(spec §10-3 «복원할 것 없음» 준수 — V1 실측 products 행 0) · Placement 닫힌 목록 위반 0.**

## D. TIER-Q 품질

| ID | Result | 종합 |
|---|---|---|
| Q-1 스코프 | 표면=spec 축자·발명 0 — Idempotency-Key 는 §F.2 8행 표에 «미적용(알려진 한계)» 정직 표기+배너 override 항목화(보수적 기본값·위임 범위)·406/415 협상 0·단건 HTTP 경로 0(명시 부재=금지 준수)·페이지네이션 0 · name ≤100 DB CHECK 는 spec §2 값 경계의 §7 «DB 수준 제약으로도 집행» 취지 내 백스톱(발명 아님 — 조정자 노트 ②-6) | ✅ |
| Q-2 API 계약 | 프로필 code-json·wire=problem+json 모양 — BC 고유 오류 0 이라 «섞을 BC wire 필드» 자체가 0(설계 §I slot 3 논증·조정자 검증 일치) · 선언 집합 200·401·503(spec 축자·500 미선언) · OpenAPI 오류 media=`application/json`(problem+json 은 중앙 런타임 헤더 — shape 정본 정합) · e2e 가 401/503 wire slug·헤더 실증 · A축 diff 0 | ✅ |
| Q-3 §9.6+테스트 실현 | design §F.2 8행 전부 실채움(Idempotency 행 정직 미적용 표기) · 동시성 전부 **결정적**: transient 주입=FakeUoW `__exit__` 발화·재시도 어댑터 mocker sleep patch·이름 UNIQUE 중복=순차 create→IntegrityError(`test_product_model_constraints.py:42`) — Barrier/실스레드 레이스 0 · 락 규율은 `in_atomic_block` 가드(`repository:48-51`)+repo round-trip 실측 | ✅ |
| Q-4 메커니즘 [🔴치명] | 커스텀 백엔드/`DatabaseWrapper`/몽키패치 0 · **PRAGMA 1건 실재**(`unit_of_work/products_unit_of_work.py:67` `PRAGMA busy_timeout = 1000`) — **spec §2 문면 승인 메커니즘**(«개발 sqlite 는 busy timeout 1000ms» 축자·설계 §F.3 안전 화이트리스트·per-connection cursor·설정 교체 아님)·PG 는 `SET LOCAL lock_timeout='1000ms'`(`:64` — 벤더 분기 가드 실재) → 면제 조항 적용·통과 | ✅ |
| Q-5 마이그레이션 | 신규 앱 자기 `0001_initial`(dependencies=[]·makemigrations 산출물만 — 손 RunPython/RunSQL 0·#336/#593) · 기존 이력 침범 0 · 비운영 전제·롤아웃 주의는 design §F 에 박제 | ✅ |
| Q-6 테스트/TDD | pytest 함수형+`@pytest.mark.django_db`·mocker·factory_boy·fake ABC 4종·`unittest.mock`/`TestCase` 0 · 인수(e2e 4+integration 계약 슬라이스)가 spec 외부 계약 전수 커버(200 정렬/필터/비노출·401 2형·503·openapi shape·OHS 3갈래·독립 import·오염/DB 전파·admin 7·seed 8)·129/129 green | ✅ |
| Q-7 경미 | 프로덕션 코드 전수 어노테이션(#11 계열 products 귀속 0 봉인) — 🟡 테스트 모듈 상수(`API`·`PRODUCTS_URL`·`HTTP_FIELDS` 등)·arrange 헬퍼(`bearer`·`jpost`·`parent_bearer`) 무어노테이션(parent/child e2e 동형 관찰 — 두 라운드 연속 동일 흠) | 🟡 |

## 의미적 변종 / backstop-blind 메타

`[결정PASS∧의미FAIL]` = 0. 관찰(위반 판정 아님):

1. **[spec §2 «최외곽 트랜잭션 강제»(sqlite) — 문면 미실현·대체 posture]** spec §2:65 는 sqlite 락 상한 실현에 «busy timeout 1000ms + **최외곽 트랜잭션 강제**»를 병기하나, 구현은 busy_timeout 만 걸고 최외곽 강제(IMMEDIATE begin/`transaction_mode`)는 없다. 설계 §F.3 이 이를 **명시 논증**: `transaction_mode` 는 DATABASES OPTION = Placement 스코프 밖이라 강제 불가 → DEFERRED begin 락 승격 데드락은 인식 transient 1회 재시도가 흡수. 운영 엔진=PostgreSQL(§F.3 실측)이라 외부 관찰 계약(락 상한 1s·503)은 불변 — dev-sqlite 한정 축의 문서화된 대체. **위반 아님·자기 해석 ⑴ 로 계상**(조정자 노트 ③). 재료 후보: spec §2 의 이 구절을 스코프 실현 가능형으로 개정.
2. **[«오염 1행 → 목록 GET 전체 500» — 강제 귀결의 명문화]** spec 은 목록 조회 중 오염 행의 거동을 직접 적지 않았으나 설계 §C.2 가 «묵살 금지(§2)+성공 계약에 오류 혼입 불가(§3) → 전체 500 이 유일 정합 귀결·spec-forced·재판단 금지»로 박제하고 구현·테스트가 따랐다(`list_…use_case.py:32-34` 필터 중 자연 전파·OHS 는 단건 격리 대비). 조정자 검증 — 논증 성립(외부 결과가 갈리는 다른 정합 판독 없음). **자기 해석 ⑵ 로 계상·정당**.
3. **[캡슐화 완화 — repo 의 사적 `_events` 직접 읽기]** driven repo save-guard 가 `product._events` 를 직접 읽고(`repository/product_repository.py:58`) 테스트가 강제 주입(`test_django_product_repository.py:171`) — #545 record→pull→publish 백스톱의 정당 실현·child_settings canon 바이트 동형. 관찰 유지(두 라운드 연속 — 표준 문면화 후보 지속).
4. **[pull_events 호출 비대칭]** create(`:46`)·delete(`:51`)는 저장/삭제 전 `pull_events()` 를 호출하나 **update 는 미호출**(`update_product_use_case.py` — replace 후 바로 save). `_events` 상시 빈 리스트라 가드 불발화·행동 무영향이며 위반 아님 — 다만 «pull 은 유스케이스 몫(#539)» 규율의 파일 간 비대칭은 사소한 일관성 흠(관찰만).
5. **[admin 의 Django 사적 `_state` 조작]** `panel.py:130-131` 이 create 후 `obj._state.adding=False`·`obj._state.db="default"` 로 admin 후속 흐름(log_addition·redirect)을 잇는다 — use case 경로 유지(도메인 우회 0)를 위한 실용 처리·프레임워크 사적 표면 접촉은 driven admin 칸 안. 관찰(경미).

## 채점자 마무리 물음 (ⓓ — 기계가 좁힌 후보·사람 마무리)

**ⓓ#69 프로덕션 `assert` 4건 — 「런타임이 아니라 테스트·타입 체커 몫인 검사인가?」 → 예, 4/4 전건. 존치 정당·위반 아님.**

| 위치 | assert | 판정 |
|---|---|---|
| `create_product_use_case.py:49` | `saved.id is not None` | `save` 계약(#597 — 신규 저장은 서버 부여 id)의 **Optional 타입 좁힘** — mypy strict 가 `Product.id: ProductId | None` 을 스스로 좁히지 못하는 자리의 표준 관용구 |
| `get_purchasable_product_use_case.py:49` | `product.id is not None` | 동일 — «find_* 는 영속 행만 복원» 계약 불변식의 좁힘 |
| `list_purchasable_products_use_case.py:41` | 동일 | 동일 |
| `get_purchasable_product_service.py:44` | `result.product is not None` | «FOUND 는 payload 동반»(#453 답 갈래 계약) 불변식의 좁힘 |

넷 다 ⑴ 입력 검증·업무 판정이 아니고(값 경계는 VO·판매 판정은 도메인이 이미 소유) ⑵ 검사 대상이 **자기 코드의 계약 불변식**이라 정확히 «테스트·타입 체커 몫»이며 ⑶ `-O` 로 벗겨져도 후속 `.value` 접근이 AttributeError 로 시끄럽게 실패해 침묵 오염이 없다. #69 의 취지(개발자 실수 검사를 런타임 검증으로 위장하지 말라)에 **부합하는 쪽**의 assert 다.

**ⓓ#153 `get_purchasable_product_service.py:37` 유스케이스 호출 2회 — 「계약↔응용 DTO 변환의 정당한 문장인가?」 → 정당. 창구 월권 아님.**
«2회»의 실체는 한 문장 `build_get_purchasable_product_use_case().execute(…)`(`:40-42`) 안의 **합성 팩토리 호출 1 + execute 1** 이다 — 유스케이스 «실행»은 1회이고, 팩토리 호출은 «DI 조립은 composition_root 소유·창구는 매요청 호출만»(#85·설계 §A) 표준형의 필수 절반이다(child_settings 컨트롤러 canon 동일 패턴). 함수의 나머지 전부는 result→계약(outcome·payload) 투영(`:43-63`)뿐 — 「바꾸고·부르고·되돌리는 일만」 문면 그대로다.

## 조정자 노트

- **① 세션 감사·클린룸(하네스 원자료 + 산출물 교차)**: STOP 0·판단 개입 0·승인 ~45회 전부 기계적. 클린룸 위반 신호 0 — 산출물 전수 grep 에서 옛 경로(`infra_layer`·`presentation_layer`)·V-접미·옛 심볼(`get_purchasable_product_v1`·`PurchasableProductV1`·`CatalogProductStateInvalid`·`ProductCatalogServicePublishedError`) 출현 **0건**(유일한 presentation_layer 언급 = 승인 빚 #12 주석). V1 대조(부록 A)에서 복제 흔적 0 — V1 은 `product_catalog/` area·`dto/`·`handler/`·`sale_calendar` 도메인서비스·중앙 검증 모듈 구조인데 신규는 `product/` area·`_command/_query/_result`·`SaleReferenceDate` VO·fake ABC 로 분해·명명·단언 형태 전부 상이 + V1 에 없는 초과 커버(DB 제약 행위 8·스키마 introspection 5·seed 8·재시도 어댑터 4·OHS 독립 import subprocess 실증).
- **② 자기보고 검증 — «구현 중 설계 교정» 7건 전수(불신 집행)**: 각각 ⑴ 외부 계약 ⑵ 표준 근거 ⑶ 비위임 판정.

| # | 교정 | 표준 문면 실재(설치본 2.8.0 확인) | 외부 계약 | 판정 |
|---|---|---|---|---|
| 1 | 재시도 자리 = `TransientRetryPort`+driven `DjangoTransientRetryAdapter` | **#7 실재**(check-event-publish:7 — «application_layer import 허용 넷» 문면·framework 유틸 불가)·#245(UoW 계약 3메서드 — check-port-adapter-pairing:372-376)·#22 | 불변(1회·25ms·create 미재시도·503 — 어댑터 `:29-30` 상수·유닛 4건 실증) | 표준-강제 내부 교정 · 정당 |
| 2 | KST 기준일 = `SaleReferenceDate` VO | **#307 실재**(check-domain-model — 원시→원시 무상태 함수는 도메인서비스 아님) | 불변(내부 모델링·spec §2 «도메인은 순수 변환만» 충족) | 정당 |
| 3 | `find_by_id_for_update` 비관 락 | spec §2 명시 강제(«수정·삭제는 대상 행 쓰기 락»)+accounts 정본 동형·`in_atomic_block` 가드 | 불변(락 상한 1s 실현 수단) | spec-forced · 정당 |
| 4 | UoW 이름 `ProductsUnitOfWork` | **#247 실재**(check-naming — `<Bc>UnitOfWork`) | 불변(내부 명명) | 정당 |
| 5 | use case 폴더 4파일 | **#19 실재**(미사용=빈 파일 — 5 폴더 전수 0바이트 실측) | 불변(골격) | 정당 |
| 6 | name CHECK ≤100(`products_product_name_trimmed_max_length`) | spec §2 값 경계+§7 «DB 수준 제약으로도 집행» 취지·§9.5 CHECK 백스톱 — PG varchar(100)↔sqlite length 무시의 양 엔진 대칭화 | 불변(API·폼 오류 경로는 VO 단일 출처 유지 — DB 는 백스톱) | 백스톱 보강 · 발명 아님 · 정당 |
| 7 | admin `validate_unique`/`validate_constraints` no-op override(`product_create_form.py:63-67`·`product_change_form.py:64-68`) | spec §4 축자 강제 — Django 6.0 ModelForm 기본이 중복 이름을 폼오류로 **선점**하면 «전용 안내 없이 서버 오류» 라는 V1 축자 행동이 깨짐 → no-op 으로 DB `IntegrityError`→500 보존·값 경계 폼오류는 `clean()` 도메인 VO 가 유지(`:53-61`) | **보존됨**(override 가 spec 행동을 지키는 방향) | spec-forced · 정당 |

- **③ 결정-주체 관측(자기 해석 2 의 정당성)**: ⑴ sqlite «최외곽 트랜잭션 강제» 대체(메타 1) — Placement 실측(DATABASES 미포함)이 논증을 지지하고 운영 엔진(PG) 외부 행동 불변 → «밖에서 보이는 결과가 갈리는 물음» 비해당·STOP 요건 불성립. ⑵ 오염 1행→목록 전체 500(메타 2) — spec §2 묵살 금지+§3 성공 계약의 교차가 유일 귀결을 강제함을 조정자 재도출로 확인. 둘 다 설계 문서에 근거·대안·재판단 금지 표식까지 박제(암묵 결정 0). **자가 승인 0**: G2 BLOCKER 0(설계 §K «BLOCKER: 없음» — 세 잠재 긴장 전부 evidence/spec/precedent 로 해소·검사기 정본 위임)·배너 override(Idempotency) 기본 미적용 commit(보수적 기본값·child 동형)·빚 가필 0·Placement 이탈 0·scope/refactor-scope 사후 개정 0(refactor-scope 는 Phase 0 기록 원형 유지·구현 교정은 impl-notes 별도 파일 — 규율 준수).
- **④ Phase 0 규율**: 27/27 검사기 실측(`.venv` 3.14 인터프리터 명시 — «AST 침묵 스킵» 함정 회피 기록)·products 귀속 0·«미룰 수 없음» 0 — G0 ⓑ 고정 답과 정합.
- **⑤ 벽시계**: 실동작 ~5h12m — child 1h58m 대비 길지만 BC 표면이 3배(HTTP+OHS+admin+seed+쓰기 3종·129 테스트 vs 40). r2′ 레인 A 가 3h26m 을 쓰고 STOP 한 것과 대비하면 «재료 정합 후 완주» 비용으로 정상 범위. 속도-성능 트레이드오프 신호 없음(치명 0·Q 상).
- **⑥ 남는 결점(코드 아님 — 수확 큐행)**: ⑴ FC-1 골든 사전등록 공백 **4라운드 연속**(라운드 준비 절차 명문화 미이행 지속) ⑵ spec §2 «최외곽 트랜잭션 강제» 문면 vs Placement 스코프의 잔여 긴장(메타 1 — 다음 respin 시 문면 정리 후보) ⑶ repo `_events` 사적 읽기 canon 3회째(«저장 가드의 캡슐화 완화» 표준 문면화 후보) ⑷ 테스트 모듈 어노테이션 흠 두 라운드 연속(Q-7 — 표준 «테스트 코드 어노테이션» 조항의 침묵 지점).

## 부록 A. 옛 테스트 시나리오 대조 (기준 = V1 원본 `b927a275^` · ⑥ 채점 주석)

V1 테스트 104건(acceptance/integration 30·unit 74) ↔ 신규 스위트 123함수(129 수집) 대응 — 외부 계약 축 전수:

| V1 시나리오 | 신규 대응 | 판정 |
|---|---|---|
| listing 정렬 price→id / 빈 배열 200 / 5필드 exact / KST 창+활성 필터 | integration listing exact 리스트 단언(비활성·기간밖 arrange 포함)+e2e 빈 DB `200 []` | ✅ 커버 |
| listing 401 부재/무효 토큰 | e2e 401 2형(+`WWW-Authenticate`·slug) | ✅ 커버 |
| openapi 파라미터/단건 경로 부재·5필드 스키마·선언 오류 | e2e openapi(5필드 required·array·$ref·401/503 presence·media) + A축 diff 0 | ✅ 커버 |
| published 부재/비활성/기간전/기간후 — **V1 예외 4종** | OHS 답 갈래 3종(NOT_FOUND·NOT_PURCHASABLE×2 시점)+unit 5 — **모양은 표준(답 갈래)·뜻 보존**(spec §6 respin 의도 그대로) | ✅ 커버(모양 개정은 spec 소유) |
| published 5필드·매 호출 재판정·판매 중 갱신 즉시 반영 | OHS FOUND 5필드 exact+`is_active` 비노출 단언 · 매 호출 fresh 합성(창구 구조가 보장)·명시 재판정 시나리오는 직접 대응 없음 | 🟡 부분(재판정 축 — 구조 보장·직접 단언 없음) |
| admin: add 폼 is_active 비노출·활성 요청해도 비활성 생성·change 갱신/비활성화 | admin forms 5+admin 8(생성=비활성 단언·use case 경유 count) | ✅ 커버 |
| admin: 경합 race→404·이중 삭제→404 | admin 부재 404(mocker 주입)+transient 503+미인식 전파 | ✅ 커버 |
| V1 «필터/액션 기본값 없음» 단언 | 반대 방향(8컬럼·필터·검색 실재) — **spec §4 가 정본**(옛 테스트=오라클 금지 축 그대로) | — 계약 개정분 |
| unit: dto 중앙 검증 17·command/query 22·sale_calendar 6 | VO 30+use case 16+`SaleReferenceDate` 7 — **검증 소유가 중앙 dto 모듈→도메인 VO 로 이동**(표준형) | ✅ 커버(구조 전환) |
| (V1 에 없음) | DB 제약 행위 8·스키마 introspection 5·seed 8·재시도 어댑터 4·OHS 독립 import subprocess·repo save-guard | — 신규 초과 |

복제 흔적 0 — 파일 분해(V1 `integration/api|admin|published_service/` 하위 트리 vs 신규 평면 의미군)·factory 이름(`product_factory` vs `product_model_factory`)·arrange 방식(V1 헬퍼 vs 신규 인라인+프로덕션 로그인)·단언 형태 전부 상이.

## 처분 제안 (사용자 결정 입력)

1. **통과** — ⑤ 3축 green·치명 0·Q 상·결정 주체 깨끗(자가 승인 0·STOP 0·빚 가필 0). **r2′ 충돌 4축 재발 0 = respin(C″)·v2.8.0·preflight ⑽ 의 목적 달성 실증.** 스트릭 계상은 사용자 몫.
2. **재료 보강 후보**: ⑴ FC-1 골든 행위표를 라운드 준비 필수 산출물로 명문화(4라운드 연속 공백) ⑵ spec §2 «최외곽 트랜잭션 강제» 구절을 Placement 실현 가능형으로 개정(메타 1).
3. **플러그인 수정 후보(수확 큐 병합)**: ⑴ repo save-guard 의 `_events` 사적 읽기 — canon 3회째(child·parent·products)이니 «저장 가드 캡슐화 완화» 표준 문면 신설 ⑵ 테스트 코드 어노테이션 규율의 표준 침묵(Q-7 동형 흠 2회 연속) ⑶ ⓓ#69 의 «타입 좁힘 assert» 정당 분류를 검사기 문면에 예시로 박제(이번 4건이 전형).
