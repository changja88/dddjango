# 평가 기록 — Codex · p1a-v3 (주문생성 API)

> **대상**: `~/Desktop/dddjango-p1a-v3-codex` (런타임=Codex CLI, 태스크B=주문생성, 가장 마지막 스모크)
> **기능**: "주문 생성 API. 별도 order 개념, 요청 상품·수량의 주문 생성, catalog가 재고 소유·주문 시 차감(부족 시 409)."
> **기준**: `eval/rubric/RUBRIC.md` + `EVAL-METHOD.md` (v2 초안, **미동결** — 일부 동결 전 결정 미해소는 아래 명시)
> **채점일**: 2026-05-31. 증거 = 코드 정독 + 테스트 실행 + FC 골든 실측(서브에이전트 수집 → 호출자 집계).
> **정직 경계**: N=1·단일 태스크. "규칙 준수 + 기능 정확성"까지 — baseline 차별가치·라이브 게이트 발화는 안 잼(EVAL-METHOD §4). 우열 단정 아님.

---

## 종합 판정 (사전식 집계)

**🔴 규칙 준수 게이트 FAIL — 척추 치명 3건** · **🟢 기능 정확성 FC 전부 PASS** · 의미적 변종 1건.

| 단계 | 결과 |
|---|---|
| ① 기존규약 마스크 C | catalog(기존앱)에 재고판정(`can_decrement_stock`) 적재 + **평면 유지** → 마스크 C 엄격 적용 시 §1.2 발동(이주 대상). **단 DO-NOT-RETRY #7·DR-24 "underdetermined"로 평면 유지 자체는 방어가능** → 하드 FAIL 안 함, *논쟁적 항목으로 플래그*. (실제 해악은 SD-3로 발현.) |
| ② 치명 게이트 | **SD-3 ✗ · SD-6 ✗ · SH-7 ✗** → **픽스처 FAIL** |
| ②.5 실질성 관문 | PASS (도메인 메서드 실분기·테스트 27개 비-vacuous·종류폴더 사용) |
| ③ 의미적 변종 | **1건(SD-6 P1a)** → "준수" 라벨 금지 |
| ④ TIER-Q | 게이트 FAIL이라 등급 산정 대상 아님(참고용 기록) |

**한 줄**: 구조·테스트·기능·마이그레이션·메커니즘소유권은 견고하나, **(1) P1a 의미적 변종**(application이 HTTP status 소유·중앙핸들러 죽은코드), **(2) SQL 판정 복제**, **(3) 협력 포트 위치 위반**, **(4) task 미요구 멱등성 과설계** — 규칙 준수 4대 결함.

---

## 치명 게이트 표 (SD 전부·FC 전부·SH-1·2·4·7·NJ-1·2)

| 항목 | 판정 | 핵심 줄 인용 |
|---|---|---|
| SD-1 판정소유 | ✅ PASS | `quantity.py:10-12`(양수 불변식); 재고판정은 catalog `stock_policy.py:8`(명세상 catalog 소유) |
| SD-2 프로덕션호출 | ✅ PASS | `create_order_app.py:89-106` 조회→도메인→port→save |
| **SD-3 무복제** | **🔴 FAIL** | `stock.py:42` `stock__gte=quantity` — `stock_policy.py:8` 충분성 규칙을 CAS WHERE에 **복제**(version CAS는 정당, gte는 위반). [DR-24 C4] |
| SD-4 경계 | ✅ PASS | `order.py:10` `product_id: ProductId`(ID 참조), catalog 객체 미참조 |
| SD-5 표현력 | ✅ PASS | `quantity.py:6`·`product_id.py:6` `frozen=True,slots=True` |
| **SD-6 계층순수성/P1a** | **🔴 FAIL(의미변종)** | `idempotency_store.py:17-21` `IdempotencySnapshot(status:int)` = app 반환타입(`create_order_app.py:51`); app이 비즈예외 직접 catch(`create_order_app.py:72`)→status snapshot; `orders_api_router.py:87-108` 중앙핸들러 3개 **죽은코드**; operation `-> JsonResponse`(`api_orders.py:55`) [DR-24 C2·C3] |
| SD-7 컨텍스트통신 | ✅ PASS | `catalog_acl.py:4` `catalog.published_service.stock`(OHS) 단일 소비, 직접 import 0 |
| SH-1 컨테이너 | ✅ PASS | 신규 `application/orders/` |
| SH-2 4계층 | ✅ PASS | `{domain,application,infra,presentation}_layer/` 분리 |
| SH-4 Django앱위치 | ✅ PASS(신규앱) | orders `infra_layer/django_orders/` + `apps.py:6-7` 점경로·label. (catalog 평면=마스크 C 논쟁적, 별도) |
| **SH-7 협력포트위치** | **🔴 FAIL** | `ProductStockPort`가 `application_layer/create_order/port/`(표준=`domain_layer/<agg>/port/`) [DR-24 C6, §E 앵커 FAIL예시] |
| NJ-1 스택채택 | ✅ PASS | `NinjaAPI`+`Router`(`api_orders.py:28`) |
| NJ-2 operation얇음 | ✅ PASS | `api_orders.py:51-69` 헤더검증+app호출+매핑만(SD-6과 직교; 파싱·ORM 0) |
| FC-1 골든 | ✅ PASS(실측) | 재고10·주문3→201/잔7/주문1 · 재고2·주문5→409/불변2/주문0 (독립 호출 실측) |
| FC-2 비-vacuous | ✅ PASS | 소진→409 어서션 `test_create_order_api.py:80-99`; CAS 결정적 `test_stock_published_service.py:34-64` |
| FC-3 도메인정합 | ✅ PASS | `stock>=0` CHECK·`F("stock")-quantity` 정상 방향 |

→ **치명 게이트: SD-3·SD-6·SH-7 FAIL ⇒ 픽스처 전체 FAIL.** FC 3항목은 전부 PASS(기능은 올바름).

---

## 비-치명 항목

| 항목 | 판정 | 줄 인용 |
|---|---|---|
| SD-3 외 SH-3 종류폴더 | ✅ | `models/`·`port/`·`repository/`·`acl/` |
| SH-5 ORM명명 | ✅ | `OrderModel`/`OrderIdempotencyRecordModel` vs bare `Order` |
| SH-6 포트명명 | ✅ | `Interface`/`Impl`/`*_repo.py` 0 |
| SH-8 ACL분리 | ✅ | `infra_layer/acl/catalog_acl.py` |
| **SH-9 단일레이아웃** | **🟠 FAIL** | catalog `test/`(실)+`tests/`(빈)+`tests.py`(스텁) 3중 공존 |
| SH-10 테스트의미군 | ✅ | orders `test/{unit,integration}` |
| NJ-3 Schema분리 | ✅ | `CreateOrderIn`/`CreateOrderOut`/`ProblemDetailsOut` |
| NJ-4 status선언 | ✅ | `api_orders.py:41-49` `{201,400,404,406,409,415,422}` |
| **NJ-5 문서화** | **🟠 WEAK** | summary/tags 있으나 operation `-> JsonResponse`(`api_orders.py:55`) 반환타입 누수 |
| NJ-6 버전핀 | ✅ | `requirements.txt:2` `django-ninja==1.6.2` |
| **Q-1 스코프/과설계·G1** | **🔴 FAIL** | task 미요구 멱등성 대규모 발명(Idempotency-Key **필수**·`OrderIdempotencyRecordModel`·fingerprint·replay·24h). design-spec §9 Open Questions 사후기록만, G1 고-blast 미상정 [DR-24 C3·C5] |
| Q-2 API계약 | ✅ | RFC9457(`problem_details.py:239-255`)·`/api/v1/`·`problem+json` |
| Q-3 §9.6+테스트 | ✅(부분) | design-spec §6 8행 블록 실재(line 265-274)·CAS 실현. 단 §7(line 369) 약속 `test_stock_concurrency.py` **부재**(커버리지는 catalog로 이동 존재) [DR-24 C1] |
| Q-4 메커니즘소유권 | ✅ | 커스텀 백엔드/PRAGMA/몽키패치 0; 표준 sqlite3(`settings.py:80`) |
| Q-5 마이그레이션안전 | ✅ | catalog `0001_initial` **불변**(원본 Product); version+`stock>=0`는 신규 `0002`; db_table 보존; `makemigrations --check`=No changes |
| Q-6 테스트/TDD | ✅ | `check` 0 issues · `test` **27/27 OK**(0.169s) |
| Q-7 경미 | 🟠 WEAK | 빈 종류폴더 8개(일부 의도)·`catalog/tests/` 빈 디렉터리 |

---

## 의미적 변종 (decision-lane PASS ∧ semantic FAIL) — 주 산출물

**SD-6 / P1a 변종** (DR-24가 정확히 여기서 나옴):
- **decision-lane 통과**: domain HTTP import 0 + `@api.exception_handler` 12개 등록 → 결정적 백스톱 `check-error-centralization.py`도 **exit0**(application_layer가 직접 `JsonResponse`/`status=` 안 만듦 — status는 `IdempotencySnapshot` *객체*로 표현, raw 응답화는 presentation에서).
- **semantic FAIL**: 그러나 application이 **HTTP status를 소유·결정**한다 — 비즈예외를 app이 직접 catch(`create_order_app.py:72`)해 status를 든 snapshot 반환(`idempotency_store.py:17-21`, app 반환타입), 그 결과 중앙 비즈예외 핸들러 3개가 **도달 불가 죽은코드**(`orders_api_router.py:87-108`).
- **뿌리** = Q-1 멱등성 스코프크립(status-bearing 객체를 application 흐름에 태움).
- **교훈 박제(DO-NOT-RETRY #11)**: 백스톱 exit0 = "좁은 텍스트 계약 통과"일 뿐 의미적 준수 아님.

---

## 마스크 C (기존규약) 적용 메모
catalog는 baseline 시드(평면 startapp). Codex가 catalog에 재고판정(`can_decrement_stock`)을 **적재**하면서 **평면 유지** → 마스크 C 엄격 해석은 §1.2(판정→구조 이주) 발동(평면 유지 시 SH FAIL). **그러나** DO-NOT-RETRY #7("기존 startapp 강제 이주 = 스코프 초과, 조치 없음[A]")·DR-24 catalog 직답("미이관 결정 자체는 underdetermined")로 평면 유지 *그 자체*는 하드 FAIL 처리 안 함 — **동결 전 결정(마스크 C "판정 적재" 판정 강도) 미해소**로 플래그. 단 평면+판정적재의 *구체 해악*인 **SD-3 SQL 복제는 별도로 FAIL**.

---

## DR-24 C 트랙 대응
C1(약속 테스트 부재)·C2(P1a 변종)·C3(멱등성 크립)·C4(SQL 복제)·C5 부분(G1 미상정)·C7(죽은 핸들러) **전부 재현·확인**. C6=ProductStockPort `application_layer` 배치(SH-7 FAIL로 반영). 본 채점이 추가 식별: SH-9 3중 레이아웃·NJ-5 반환타입 누수.

**견고한 면(공정)**: FC 전부 PASS(기능 정확), 27/27 그린, 마이그레이션 0001 불변, 메커니즘소유권 깨끗, OHS 단일소비(SD-7 PASS), §9.6 8행 블록 실재. 결함은 *규칙 준수*의 4축에 집중.
