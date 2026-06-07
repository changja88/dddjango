# Codex aclex2live 채점 — B 트랙 ACL-EX2 예방 라이브 (EVAL-METHOD v3 §6 형식)

> **방법** v3 · **채점일** 2026-06-07 · **픽스처** `~/Desktop/dddjango-aclex2live-codex`(greenfield; baseline catalog 평면 `startapp` 시드를 런이 이주·판정 적재) · **런타임** Codex · **plugin** 1.7.0 · **산출** `.dddjango/20260607-1903-order-create-api/`
> **태스크** 주문 생성 API(별도 order BC·catalog 재고 차감·부족 시 409) · **게이트**(고정) BC배치=미강제 / 렌즈=ddd+db+api / 스택=표준기본(Ninja) / 테스트러너=표준기본 / G1 멱등성=미도입·transient=503 / G1·G2=명백결함만 반송 / thinking=OFF
> **범례** ✅PASS · ❌FAIL · 🟡WEAK/경미 · ⏸️보류 · ➖N/A
> ⚠️ **단서**: **N_grader=1**(조정자 단독·blind 미적용 — full 정본 아님) · **FC-1 골든표 사전등록 생략**(조정자 실측 probe로 갈음) · **자기보고 불신 적용**(조정자 직접 read+EP probe+mutation+백스톱 15종) · **⚠️ FC-2 측정 시 stale `.pyc` 오염 발견·교정**(macOS 1초 mtime 해상도로 mutation `.pyc` 잔존→매 사이클 `__pycache__` 박멸 후 재측정·DR-24/35 교훈) · **Codex는 pytest 미설치**(러너=`manage.py test`·Django TestCase — FC-2/baseline은 함수형 0개라 전수 수집·§1.4 거짓PASS 우려 무관) · **N=1·단일태스크**(P4③ 우열·완료 금지) · Codex=ACL-EX2 **대조군**(대안 B로 구조적 부재)

## 종합 판정 (사전식 집계 — EVAL-METHOD §2)
| 단계 | 결과 |
|---|---|
| ① 마스크 C | order=신규앱(§0 전부 강제) · catalog=기존앱·런 touched·판정 적재(MQ0=Y·MQ1=Y·MQ2=N)→§1.2·이주로 위치 PASS |
| ② 치명 게이트 | **FAIL 0건** (SD-1~7·FC-1~3·SH-1·2·4·7·NJ-1·2·Q-4 전부 ✅) |
| ②.5 실질성 관문 | 빈 골격 0 — 통과 |
| ③ 비치명·의미변종 | 의미적 변종 0건 · 비치명 **FAIL 2(Q-6 pytest·NJ-7 catch-all)**(품질 강등·"준수" 라벨엔 비영향) |
| ④ TIER-Q 등급 | WEAK 2(Q-1·Q-7)·**FAIL 2(Q-6·NJ-7)** → **품질 하**(§2.4: 중=FAIL≤1 위반) |

**한 줄 요지**: 치명 0 → **정적 준수** / 품질 **하**(Q-6 pytest 미채택 + NJ-7 catch-all 부재 FAIL 2). ACL-EX2 대조군대로 부재(대안 B).

**2차원 라벨**: **(정적: 준수·품질 하)** × **(라이브: 발화)** — N=1·단일태스크라 "완료" 금지.
- `폴더 동작`: **관측** (`.dddjango/20260607-1903-order-create-api/`)
- `에러경로 계약`(§4.3.1): **관측**(전부 충족) — EP-1/1b/2/4 problem+json·**EP-3=503**·정상 201. (Claude와 달리 **EP-1 깨진본문도 400 problem+json** — `HttpError` 핸들러 경유)

---

## A. TIER-S 척추 — S-DDD
| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SD-1** 판정 소유 | 핵심 규칙이 도메인 메서드로 | §3.2·§3.1 | `product_stock.py:21-31` `ProductStock.plan_deduction`(`available_quantity<quantity` 부족 판정→`ProductStockDeduction`) · `order.py:16-22` `Order.create`(product_id/quantity 검증) | ➖ | ✅ | ✅ | ✅ |
| **SD-2** 프로덕션 호출 | 조회→도메인→저장 실호출 | §3.2·§3.6 | `product_stock_operation.py:22-31` get→`plan_deduction`→try_deduct(재시도) · `place_order_command.py:33-44` atomic 내 `port.deduct`→`order_repository.save` | ➖ | ✅ | ✅ | ✅ |
| **SD-3** 무복제 | 판정 SQL 복제 0 | §3.2 | `product_stock_repository.py:39-45` CAS `filter(id,version=expected).update(stock=F("stock")-quantity, version=F+1)` — WHERE=version만·`stock__gte=` 판정 복제 0 (차감 산술 `F-quantity`=atomic 관용구·DR-32 (B) 허용) | ✅(anemic-sql exit0) | ✅ | ✅ | ✅ |
| **SD-4** 애그리거트 경계 | 1트랜잭션·ID참조 | §3.3 규칙1~4 | order/catalog 별도 애그리거트·단일 atomic(`place_order_command.py:39`)·cross-BC scalar `product_id`(도메인 FK 0·DR-37) | ✅(ID참조) | ✅ | ✅ | ✅ |
| **SD-5** 모델 표현력 | 값객체 불변·무상태서비스 | §3.1·§3.5·§2.3 | `product_stock.py:8·15` `@dataclass(frozen=True)` `ProductStockDeduction`/`ProductStock` · `order.py:9` `@dataclass(frozen=True) Order` 자기검증 · operation 무상태 (※ Quantity 별도 VO 없이 Order.create 인라인 검증 — 위반 아님) | ✅ | ✅ | ✅ | ✅ |
| **SD-6** 계층 순수성(P1a) | domain HTTP 0·중앙 변환 | §5.1·§6.1; ninja §2.2·§6.2 | domain HTTP import 0 · presentation 단일변환점 `order_api_router.py:44-118`(`@api.exception_handler` 7종) · operation 성공 매핑만 `api_orders.py:57-62` · 중앙핸들러 발화(EP probe 실측) | ✅(error-centralization exit0) | ✅ | ✅ | ✅ |
| **SD-7** 컨텍스트 통신 | OHS/ACL만·직접 import 0 | §3.2(3)·§2.5 | order ACL `infra_layer/acl/product_stock_adapter.py` catalog 예외→order 예외 `from` 번역 · catalog `published_service`(OHS) 경유 · domain은 포트 Protocol 의존 · ACL 밖 catalog import 0 | ✅(context-isolation exit0) | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR
| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | 신규 앱 `application/<app>/` | §0-1 | order=`application/order/` · catalog 이주=`application/catalog/`(루트 평면 아님) | ✅(app-container exit0) | ➖ | ✅ | ✅ |
| **SH-2** 4계층 | `*_layer/` 물리분리 | §0-2 | `application/order/{domain,application,infra,presentation}_layer/` 존재 | ✅(layer-skeleton exit0) | ➖ | ✅ | ✅ |
| **SH-3** 종류폴더+거주명명 | R/C/Q 거주명명 | §0-3·§0-4·§4 | `command/place_order_command.py PlaceOrderCommand`·`dto/place_order_request.py PlaceOrderRequest`·종류 2차 폴더 | ✅(폴더) | ✅(명명) | ✅ | — |
| **SH-4** Django앱 위치 | 모델/마이그 `infra_layer/django_<app>/` | §0-5 | `infra_layer/django_catalog/models/product.py`·`migrations/` · `db_table="catalog_product"`·AppConfig | ✅(app-container exit0) | ➖ | ✅ | ✅ |
| **SH-5** ORM 명명 | ORM `<Name>Model`·도메인 bare | §0-6·§4 | `ProductModel`(`product.py:4`)/`ProductStock`(도메인) · `OrderModel`/`Order` 분리 | ✅ | ➖ | ✅ | — |
| **SH-6** 포트/구현 명명 | 추상=개념+역할·구현=Adapter/패턴명 | §4 | `ProductStockPort`(Protocol)/`DjangoProductStockAdapter` · `DjangoProductStockRepository` · `Interface`/`Impl`·약어 0 | ✅ | ➖ | ✅ | — |
| **SH-7** 협력 포트 위치 | `domain_layer/<agg>/port/` | §2 | `domain_layer/order/port/product_stock_port.py` | ✅(SH-7 grep) | ➖ | ✅ | ✅ |
| **SH-8** ACL 분리 | `infra_layer/acl/`·repository 미혼합 | §2·§3 | `infra_layer/acl/product_stock_adapter.py` 단독·repository와 분리 | ✅ | ✅ | ✅ | — |
| **SH-9** 단일 레이아웃 | 두 레이아웃 미공존 | §1.4 | order=`test/`만·`src`+`apps` 혼용 0 | ✅ | ➖ | ✅ | — |
| **SH-10** 테스트 의미군 | `test/{unit,integration,e2e}`·HTTP=integration | §1.3 | `test/{unit,integration}/`·HTTP=`integration/test_api_orders.py`·평면나열 0 | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA (HTTP operation 有 → 채점)
| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | 신규 JSON API=Ninja | §1.1·§10 | `order_api_router.py:35` `NinjaAPI` + `api_orders.py:28·31` `Router`+`@router.post` · plain view/DRF 0 | ✅ | 🟡 | ✅ | ✅ |
| **NJ-2** operation 얇음 | 비즈/ORM/수동파싱 0 | §1.3·§2.2 | `api_orders.py:44-62` typed `payload: OrderIn`→`command.execute`→`return 201, OrderOut` 매핑만 · `json.loads`·ORM·비즈분기 0 (406 Accept 협상 분기 1줄 `:49-50`=§6.3 허용·NJ-2 비위반) | ➖ | ✅ | ✅ | ✅ |
| **NJ-3** Schema 입출력 분리 | 도메인 직접 직렬화 0 | §2.2·§3.1 | `OrderIn`/`OrderOut`/`*ProblemOut` 분리·`api_orders.py:57-62` 매핑 | ✅ | ✅ | ✅ | —(강) |
| **NJ-4** status별 response 선언 | `response={}`에 다중 status | §2.2·§8 | `api_orders.py:33-41` `response={201,404,406,409,415,422,503}` 전부 schema 선언·`openapi_extra` 0 | ✅ | ➖ | ✅ | —(강) |
| **NJ-5** operation 문서화 | summary/tags·유의미 반환 | §2.2 | `api_orders.py:42 summary`·`:28 tags`·`-> tuple[int, OrderOut]` | ✅ | ➖ | ✅ | —(경미) |
| **NJ-6** ninja 버전 핀 | 매니페스트 핀 | §2.1 | `requirements.txt` `django-ninja==1.6.2` | ✅ | ➖ | ✅ | —(경미) |
| **NJ-7** 오류 변환 완전성(catch-all) | 미식별·비-retryable 단일변환점 완전성 | §6.2(368·469·477) | **catch-all `@api.exception_handler(Exception)` 부재**(grep 0) + **`order_api_router.py:117 raise exc`**(permanent 되던지기) → 미식별·permanent가 problem+json 단일변환점 우회·Django 전파(DEBUG traceback) | ❌(catch-all 0·raise exc) | ❌ | ❌ | —(강) |

> **NJ-1 🟡 노트**: `problem.py:29` `JsonResponse(body, content_type=PROBLEM_JSON)` 직접 생성 — RUBRIC NJ-1 주의 "(a) `ninja.responses.Response` 아닌 `JsonResponse` = 경미 🟡". 중앙핸들러 problem 반환 형태라 NJ-1 스택 채택 자체는 치명 통과 ✅·경미 노트만.

## TIER-S(핵심) — FC
| ID | 항목 | Result(조정자 실측) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | EP/정상 probe 실측(SQL 로깅 확정): 재고5·주문2→`UPDATE SET stock=stock-2`→**stock 3∧201** / 재고5·주문9→**409∧불변** / CAS소진→**503** — 골든 일치 | ➖ | ✅ | ✅ | ✅ |
| **FC-2** 비-vacuous | mutation 3종→`manage.py test` red(매 사이클 `__pycache__` 박멸·stale `.pyc` 교정 후): ①`F-quantity`→`F+` red · ②`available<qty`→`<=` red · ③`<`→`>` red · red율 **100%** · 복원 baseline OK | ✅(주입 실행) | ➖ | ✅ | ✅ |
| **FC-3** 도메인 정합 | 차감 방향 정상(SQL `stock-2` 확정)·`plan_deduction` 음수재고 차단·인과 정상 | ➖ | ✅ | ✅ | ✅ |

> **⚠️ FC-2 측정 함정 박제**: 1차 측정서 mutation `.pyc`(`F+quantity`)가 macOS 1초 mtime 해상도로 복원 후에도 잔존 → baseline이 거짓 FAIL(stock 5→7). `__pycache__` 박멸 + 소스 re-write로 교정 → 실제 SQL `stock=stock-2` 확인·baseline OK. **DR-24/35 ".pyc 철저정리" 교훈 재현** — mutation 채점 시 매 사이클 캐시 무효화 필수.

## C. 기존규약 마스크 (§1.1.M MQ 적용)
- **order**: baseline 부재 신규 앱 → §0 전부 강제·SH-1·2·4·7 전부 PASS.
- **catalog**: MQ0=Y(baseline `catalog/` `D`+`application/catalog/` 재생성)·MQ1=Y(version CAS·`plan_deduction` 판정 적재)·MQ2=N → **§1.2 발동**. `application/catalog/infra_layer/django_catalog/`로 이주(루트 평면 아님)→**SH-1·4 PASS**. `check-app-container.py` exit0 일치.

## D. TIER-Q 품질
| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| **Q-1** 스코프/G1 | 멱등성·합산 미발명 · **406 Accept 협상 발명**(`api_orders.py:49-50`·`problem.py:45-73` `is_json_compatible_accept_header`) — DR-38: §6.3 허용영역이나 task 미요구 협상 레이어 = 경미 underdetermined | ➖ | 🟡 | 🟡 |
| **Q-2** API 계약 | RFC 9457 problem+json 일관(`problem.py`)·status 의미 일관·`Retry-After` | ➖ | ✅ | ✅ |
| **Q-3** §9.6+테스트 | Risky Write·소진→503·결정적 CAS 스파이(`test_product_stock_operation.py` Fake·`forced_conflicts`) | ✅(grep) | ✅ | ✅ |
| **Q-4** 메커니즘 **[🔴치명]** | version CAS·표준 ORM(`F`)·커스텀 백엔드/PRAGMA/몽키패치 0 | ✅(mechanism-ownership exit0) | ➖ | ✅(치명 통과) |
| **Q-5** 마이그레이션 안전 | 기존 `0001_initial`(CreateModel Product) 불변 · `0002` `SeparateDatabaseAndState` state-only rename(Product→ProductModel)+`db_table="catalog_product"` 보존+version backfill+constraint expand | ✅ | ✅ | ✅ |
| **Q-6** 테스트/TDD | **pytest 미채택**: `manage.py test`·`TestCase`(`test_api_orders.py:20`)·`SimpleTestCase`(×3)·`from unittest.mock import patch` — greenfield인데 Django TestCase 폴백(RUBRIC Q-6 FAIL 조건). 단 17 green·mutation red·행위 커버 | ❌(러너) | ❌ | ❌ |
| **Q-7** 경미 | 공개표면 어노테이션(⑫ exit0) · **영어 docstring**(`product_stock_port.py:7` Protocol `"""Deducts catalog-owned stock…"""`·§5 한국어 기본 deviation) · `django-ninja==1.6.2` 핀 | ✅(public-surface exit0) | 🟡 | 🟡 |

**TIER-Q 카운트**(Q-1·2·3·5·6·7 + NJ-3·4·7): WEAK 2(Q-1·Q-7)·**FAIL 2(Q-6·NJ-7)** → **품질 하**(§2.4: 중=FAIL≤1 위반).

---

## 의미적 변종 / backstop-blind 메타 (§1.3)
- **의미적 변종 0건**: `[결정 PASS ∧ 의미 FAIL]` 칸 없음. (Q-6은 결정·의미 둘 다 FAIL=정직 비치명 FAIL이지 의미적 변종 아님.)
- **backstop-blind 카드**:
  - **⑮ check-synthetic-infra-exc**: 클린 exit0(catalog repository가 raw `OperationalError`를 받아 `raise CatalogRetryableStockContention from error`로 *번역*·합성 0). proxy 주입 시 차단(이전 DR-30식 확인). ACL-EX2 대조군대로 부재.
  - **check-error-centralization**: app층만 — **presentation catch-all 완전성 못 봄**. ⇒ `order_api_router.py:115-118` `handle_operational_error`가 permanent 시 `raise exc`(되던지기) + catch-all `@api.exception_handler(Exception)` 부재 → permanent/미식별 예외가 problem+json 우회(§6.2:467 위반·prod 500 non-problem·DEBUG traceback). **어느 백스톱도 미포착**·§4.3.1 관측 트랙 밖(EP-1~4는 problem+json). **Claude와 공통 catch-all 갭=표준 빈틈**(후속 후보). 단 status(500)는 정당·KNOWN 계약 정확이라 치명 아닌 품질 흠.
  - 전 백스톱 15종 fixture 일괄 exit0(⑪⑫⑬⑭⑮ 포함).

## 에러 경로 라이브 관측 (§4.3.1 — 별도 트랙·완료 비산입·치명 아님)
> 조정자 직접 probe(자기보고 불신)·어댑터 ⓑ = `POST /api/orders` + 본문. EP-3 = CAS 소진 유도(type ii: catalog 도메인 `CatalogRetryableStockContention` 번역 경로·대안 B). 계약 속성표(ⓐ)·status 화이트리스트 정본 = `EVAL-METHOD.md §4.3.1`.

| 키 | 관측 status | content-type | 화이트리스트 | 판정 |
|---|---|---|---|---|
| EP-1 깨진 본문(1b 변종) | **400** | application/problem+json (`HttpError` 핸들러) | {400} | ✅ 관측 |
| EP-2 무효 입력(qty=0) | **422** | application/problem+json | {422,400} | ✅ 관측 |
| EP-4 재고 부족 | **409** | application/problem+json | {409} | ✅ 관측 |
| EP-3 transient 소진(type ii) | **503** | application/problem+json | {503,409} | ✅ 관측(대조군·대안 B 도메인 타입 번역) |

- **EP-3=503 = 대조군 대안 B**: catalog `try_deduct`가 raw `OperationalError`를 받아 `raise CatalogRetryableStockContention from error`(도메인 타입·`from` 보존)·ACL→order 번역·presentation 503. 합성 인프라 예외 0(ACL-EX2 구조적 부재).
- **EP-1~4·content-type 전부 충족** — Claude와 달리 EP-1 깨진본문도 400 problem+json(`HttpError` 핸들러 경유). 단 catch-all 완전성(미식별·permanent `raise exc` 되던지기)은 **EP-1~4 밖** 후속 후보(NJ-7 라벨이 전담·§ backstop-blind 카드).

## 조정자 노트 (결론만)
- **ACL-EX2 = 대조군대로 부재**(대안 B): catalog `try_deduct`가 raw `OperationalError`를 *받아* `_is_retryable`→`raise CatalogRetryableStockContention from error`(도메인 타입·`from` 보존)·operation 소진→`raise CatalogRetryableStockContention`·ACL→order `RetryableStockContention`·presentation 타입매핑 503. **합성 인프라 예외 0**. EP-3=503 실측. (렌즈 A "Codex recognizer 상류" 실증 — message-match는 repository에 있으나 도메인 타입 raise.)
- **Q-6 = 정식 FAIL**(품질 중 강등): greenfield인데 pytest 미설치·`manage.py test`·Django TestCase. DR-42 위반. **사용자 피드백("여전히 pytest 미사용")이 정확히 이것** — Claude(pytest 채택·품질 상)와 갈리는 핵심 차원. ⑬ 백스톱은 *pytest 부재*를 면제(집행 갭·후속 후보 ②).
- **N=1·P4③**: ACL-EX2는 Codex 구조적 부재(원래 대안 B)라 Codex 런은 *대조군*·진짜 검증은 Claude(직전 보유자 전환). 우열·완료 결론 금지.

## 부록 — vs Claude aclex2live 대조 (N=1·우열 아님)
| 차원 | Codex | Claude |
|---|---|---|
| 종합 | 정적 준수·**품질 중** | 정적 준수·**품질 상** |
| ACL-EX2 | 부재(대조군·대안 B) | 부재(**직전 보유자 전환 입증**) |
| EP-3 | 503 실측 | 503 실측 |
| EP-1 형식 | **400 problem+json** ✅ | 400 ninja 기본 JSON(problem+json 아님) |
| FC-2 경계 | stock==qty red 포착 ✅ | stock==qty red 포착 ✅ |
| **Q-6 pytest** | **미채택 ❌**(TestCase) | 채택 ✅ |
| Q-7 docstring | 영어 1건 🟡 | 한국어 0 영어 ✅ |
| Q-1 협상 | 406 발명 🟡 | 미발명 ✅ |
| 형식 완전성 | 갭(permanent re-raise·catch-all) | 갭(EP-1·catch-all) |

**후속 후보**: ① catch-all/형식 완전성(양 런타임 공통·표준 빈틈) · ② DR-42 집행 강화(Codex pytest 미채택·⑬ 면제·N=1). → 사용자와 처방 여부 결정 대기.
