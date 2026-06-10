# 채점 결과지 — ptbootlive-codex (도구 미설치 깨끗 baseline · Tier-1 부트스트랩 관측 + carve-out/이주배타성 재검증)

> **방법** EVAL-METHOD v3(+§1.1.T) · **채점일** 2026-06-09 · **픽스처** `~/Desktop/dddjango-ptboot-codex`(기존규약: 평면 `catalog.Product` 선재·baseline `46d2acc`·**테스트도구 미설치·pytest 설정 없음**) · **런타임** Codex(plugin 캐시 `1.10.0`·소스 `015945c` = carve-out/이주배타성 커밋 반영·16백스톱·⑰부재) · **N** 1 · **태스크 요지** "재고 부족 409·충분 시 차감 주문 생성 API"(ptcat과 동일 — N=2 통제) · **게이트** 새 BC·내부전용·ninja-extra 클래스 컨트롤러·thinking OFF · **범례** ✅PASS ❌FAIL 🟡WEAK/경미 ⏸️보류 ➖N/A
> **⚠️ 단서**: `N_grader`=2(적대 2명)+조정자 결정레인 — full ≥3 미달 · **FC-2 조정자 직접 mutation 실측**(경계·부호·status 3종 주입→pytest) · 백스톱 16종·pytest·EP 전부 **조정자 직접 검증**(자기보고 불신) · N=1·단일태스크 → 우열결론 아님
> **fixture 도구 환경(§1.1.T — 필수 필드)**: **baseline venv = 테스트도구 0**(Django/ninja/ninja-extra/asgiref/sqlparse만·조정자 미개입 깨끗 baseline) → 이번 런의 venv 도구·핀은 **전부 Codex 산출(`produced`)**. 채점은 Codex 산출 venv 그대로 실행(조정자 추가 설치 0 — 오염 없음).

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | **catalog = 데이터소스 이주**(MQ0=Y·MQ1=N·MQ2=Y: 재고판정을 order BC가 소유·catalog domain 빈 골격 정당)·order=신규(판정 소유) → §0 전부 강제 |
| ② 치명 게이트 | **FAIL 0건 → 통과.** SD-1~7(7/7)·SH-1·2·3·4·7·NJ-1·2·Q-4·FC-1·**2**·3 전부 PASS (NJ-1은 비치명 🟡) |
| ②.5 실질성 관문 | PASS(빈 골격 아님·order 도메인 판정 실코드·테스트 17 실재·비-vacuous) |
| ③ 비치명·의미변종 | 의미적 변종 **0건** · WEAK 3(NJ-1 JsonResponse·NJ-5 `-> Status` bare·NJ-7 HttpError 누락) |
| ④ TIER-Q 등급 | 품질 **중**(WEAK 3·FAIL0: Q-1·2·3·5·6·7 PASS·NJ-3·4 PASS·NJ-1·5·7 WEAK) |

**한 줄 요지**: **§1.1.T 결정적 관측 — 깨끗 baseline에서 Codex가 Tier-1을 스스로 설치+핀 완전 이행**(ptcat의 "핀 0"이 fixture 오염 탓이었음 입증) · **FC-2 PASS**(경계 보유·ptcat 치명 FAIL 해소) · **Q-7 PASS**(테스트스택 핀·ptcat WEAK 개선) → **종합 PASS**. 흠 = NJ-1 plain leak·**HttpError 누락**(깨진본문 problem+json 미달·§6.2:516·architect 책임)·NJ-5·ACL-EX2 non-transient 누수·catalog 빈 dir husk(전부 비치명).

**2차원 라벨**: (정적: **준수** — 치명0·WEAK3) × (라이브: **관측** — §1.1.T Tier-1 설치+핀·FC-2 3종 red·EP 매트릭스 실측·백스톱16 exit0) · `폴더 동작`: 미검증(재빌드 아님) · `에러경로 계약`: **부분**(EP-2·3·4 problem+json ✅·**EP-1 깨진본문 application/json**·§6.2:516 HttpError 누락)

---

## §1.1.T 테스트 도구 관측 매트릭스 (env ≠ produced ≠ used — 신설 후 첫 모범 기록)

| 축 | 관측 | 근거 |
|---|---|---|
| **env** (채점 전 venv) | 테스트도구 **0** | baseline `46d2acc`·`pip` = Django/ninja/ninja-extra/asgiref/sqlparse만(조정자 미개입) |
| **produced** (Codex 설치+핀) | **설치 Y · 핀 Y** | venv에 `pytest 8.4.2`·`pytest-django 4.11.1`·`pytest-mock 3.15.1`·`factory_boy 3.3.3`·`faker` 설치 + `requirements.txt:4-7` 4종 전부 핀 + `pyproject.toml` `[tool.pytest.ini_options]` `DJANGO_SETTINGS_MODULE` |
| **used** (실제 사용) | 수제 Fake + `objects.create` | `test_place_order_command.py:22·41·57·73` 수제 Fake/Recording 스파이·`test_place_order_api.py:36` `objects.create`(정확 필드) — `mocker`/`factory_boy`/`monkeypatch`/`TestCase` grep **0** |
| **판정** | **(설치 Y)×(핀 Y) = §2.1 완전 준수** | used에서 `mocker`/`factory_boy` *이름* 미사용은 §9.1 non-blanket·수제 Fake=§20.5 정당 → **흠 아님**. ptcat "핀 0(오염)"이 깨끗 baseline에선 **완전 핀**으로 드러남 |

> **핵심**: ptcat 채점지의 "설치/핀 미검증(오염)·Q-7 WEAK"는 *fixture 오염*(조정자 pytest 선설치)의 산물이었고, 도구 미설치 baseline에서 Codex는 **Tier-1 설치+핀을 완전 이행**한다. carve-out 처방의 미검증 부분이 입증됨.

---

## A. TIER-S 척추 — S-DDD

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SD-1 | 빈혈: 판정 소유 | ddd §3.2 | `order/domain_layer/order/value_object/product_stock.py:28-33` `if self.available_quantity < quantity: raise InsufficientStock` + `reserve` 차감계산 — order BC가 재고판정 소유(catalog는 데이터소스) | ➖ | ✅ | ✅ | ✅ |
| SD-2 | 빈혈: 프로덕션 호출 | §3.2·3.6 | `place_order_command.py:54-60` load→`OrderPlacementService.place()`→persist→save(죽은코드 아님·도메인서비스 경유) | ➖ | ✅ | ✅ | ✅ |
| SD-3 | 빈혈: 무복제 | §3.2 | `published_service.py:54-60` `filter(id=,version=expected_version).update(stock=remaining,version=F+1)` — version CAS만·`stock__gte=` 복제 0(check-anemic-sql-guard exit0) | ✅ | ✅ | ✅ | ✅ |
| SD-4 | 애그리거트 경계 | §3.3 | `place_order_command.py:53` 1 `atomic`·`order_model.py:7` `product_id=PositiveBigIntegerField`(ID참조·FK 없음·DR-37 준수)·풍부한 CHECK 6종 | ✅ | ✅ | ✅ | ✅ |
| SD-5 | 모델 표현력 | §3.1·3.5 | `product_stock.py`·`reserved_stock.py`·`order.py` `@dataclass(frozen=True)` VO+`__post_init__` 불변식·유비쿼터스 | ✅ | ✅ | ✅ | ✅ |
| SD-6 | 계층 순수성(P1a) | §5.1·6.1; ninja §6.2 | domain/application HTTP·status 변환 0(grep)·status 매핑은 presentation `config/api.py:49-119` 중앙핸들러만·command는 도메인예외(`StockContention`)만 흐름 | ✅ | ✅ | ✅ | ✅ |
| SD-7 | 컨텍스트 통신 | §3.2(3)·2.5 | order의 catalog import는 ACL `product_stock_adapter.py:1` 단일점·OHS `published_service` 경유·`ProductModel`/catalog infra 직접 import 0 | ✅ | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SH-1 | 컨테이너 | §0-1 | 신규앱 `application/<app>/`·**루트 `catalog/`는 빈 dir husk만**(`.py` 8개 전부 git `D`·`apps.py`/`models.py` 부재·INSTALLED_APPS 탈등록 settings.py:41) → SH-1 입력 PASS(check-app-container exit0) | ✅ | ➖ | ✅ | ✅ |
| SH-2 | 4계층 | §0-2 | 양 BC `{domain,application,infra,presentation}_layer/` 완비(catalog application_layer는 데이터소스라 빈 계층 정당) | ✅ | ➖ | ✅ | ✅ |
| SH-3 | 종류폴더+거주명명 | §0-3·4 | catalog domain `entity/`·`repository/`·`value_object/` 빈 패키지·order `command/`·`dto/`·`query/`·`presentation/api`·`schema` 실재(check-layer-skeleton exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-4 | Django앱 위치 | §0-5 | `django_catalog/{models,migrations}/`·`django_order/{models,migrations}/`·`db_table='catalog_product'`·`label` 보존 | ✅ | ➖ | ✅ | ✅ |
| SH-5 | ORM 명명 | §0-6 | `ProductModel`·`OrderModel`·도메인 `Order`/`ProductStock` bare | ✅ | ➖ | ✅ | — |
| SH-6 | 포트/구현 명명 | §4 | `Interface`/`Impl`/`_repo.py` 0·`ProductStockPort`↔`CatalogProductStockAdapter` | ✅ | ➖ | ✅ | — |
| SH-7 | 협력 포트 위치 | §2 | `order/domain_layer/order/port/product_stock_port.py` | ✅ | ➖ | ✅ | ✅ |
| SH-8 | ACL 분리 | §2·3 | `infra_layer/acl/product_stock_adapter.py`·repository 미혼합 | ✅ | ✅ | ✅ | — |
| SH-9 | 단일 레이아웃 | §1.4 | 단일 `test/` | ✅ | ➖ | ✅ | — |
| SH-10 | 테스트 의미군 | §1.3 | `test/{unit,integration,e2e,factories}/`·HTTP=integration | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA (HTTP operation 존재 → 채점)

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| NJ-1 | 스택 채택 | §1.1·10 | `config/api.py:17` `NinjaExtraAPI`·`order_controller.py:20` `@api_controller`·`order_api_router.py:27` `register_controllers`·DRF 0 — **단 중앙핸들러 `config/api.py:38` `django.http.JsonResponse`**(§6.2:487 `ninja.responses.Response` 처방 이탈·plain leak) | ✅ | 🟡 | 🟡 | ✅ |
| NJ-2 | operation 얇음 | §1.3·2.2 | `order_controller.py:47-65` schema→Request 매핑+`execute`+`Status(201,…)`만·json.loads/수동검증/ORM/비즈분기 0 | ➖ | ✅ | ✅ | ✅ |
| NJ-3 | Schema 입출력 분리 | §2.2·3.1 | `schema_in.py PlaceOrderIn`/`schema_out.py PlaceOrderOut`/`error_out.py ProblemDetailsOut+4` 분리·도메인 직접 직렬화 0 | ✅ | ✅ | ✅ | —(강) |
| NJ-4 | status별 response 선언 | §2.2 | `order_controller.py:24-30` `response={201,400,404,409,503}`·openapi.json 검증(`test:264`) | ✅ | ✅ | ✅ | —(강) |
| NJ-5 | operation 문서화 | §2.2 | `summary`/`description` 有 BUT 반환 annotation `-> Status`(타입파라미터 없음·`Status[PlaceOrderOut]` 미사용·ptcat 동일) | 🟡 | ➖ | 🟡 | —(경미) |
| NJ-6 | ninja 버전 핀 | §2.1 | `requirements.txt:2-3` `django-ninja==1.6.2`·`django-ninja-extra==0.31.4` + **테스트스택 4종 핀**(ptcat 무핀 대비 개선) | ✅ | ➖ | ✅ | —(경미) |
| NJ-7 | 오류 변환 완전성(catch-all) | §6.2 | `config/api.py:109` `@api.exception_handler(Exception)`→500 problem+`logger.exception`(✅ catch-all 충족·ptcat의 logger 누락 개선) BUT **`@api.exception_handler(HttpError)` 부재** → 깨진본문 problem+json 미변환(§6.2:516 처방 누락·실측 EP-1=`application/json`) | 🟡 | 🟡 | 🟡 | —(강) |

## TIER-S(핵심) — FC

| ID | 항목 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| FC-1 | 골든 오라클 | 재고5·주문2→201∧stock3∧order1 / 재고1·주문2→409∧불변∧0 / 미존재→404 / 무효q=0→400 / 동시→oversell0 / 락→503 — 전부 일치(17 passed) | ➖ | ✅ | ✅ | ✅ |
| **FC-2** | 테스트 비-vacuous | **경계 `<`→`<=` = 1 failed(test_concurrent stock=1·q=1 경계) · 차감 `-`→`+` = 4 failed · status `created`→`cancelled` = 3 failed** → **3종 다 red·복원 후 17 passed**. ptcat의 경계 green(FC-2 FAIL) **해소**(단위는 경계 미커버이나 통합이 잡음) | ✅(주입실측) | ✅ | ✅ | ✅ |
| FC-3 | 도메인 정합 | 음수재고 불가(`product_stock.py:18` `__post_init__`+migration 0002 CHECK stock>=0)·차감 정방향·인과 정상 | ➖ | ✅ | ✅ | ✅ |

## C. 기존규약 마스크 (적용 메모)

- **MQ0**=Y(옛 `catalog/*.py` 8개 git `D` + `application/catalog/` 재생성). **MQ1**=N(catalog domain에 판정 분기 **없음** — `ProductModel`은 필드+CHECK만·재고판정은 order `ProductStock.reserve`). **MQ2**=Y(catalog=순수 데이터소스).
- → catalog는 **데이터소스 이주**: domain 빈 골격 정당(§632-(2) 판정 실내용 면제)·위치·4계층·골격은 무조건 실현(충족). order = 신규 판정소유 앱. **ptcat(catalog 판정소유)과 다른 분해** — 재고판정 소유 BC가 런마다 다름(underdetermined·둘 다 방어가능).

## §1.1.T·D. TIER-Q 품질

| ID | 항목 | §근거 | Result(조정자 검증) | 종합 |
|---|---|---|---|---|
| Q-1 | 스코프/과설계 | ddd §6.8 | 415/406 발명 0(내부전용·design-spec:98 framework-default)·멱등성 범위외(spec §3.4)·503 transient 정당 | ✅ |
| Q-2 | API 계약 | api §4~14 | RFC 9457 problem+json(`config/api.py:30-46` 단일 헬퍼·`type/title/status/detail/instance`)·503 `Retry-After`+`retryable` — *단 깨진본문은 problem+json 미달(NJ-7 참조)* | ✅ |
| Q-3 | §9.6 형식+테스트 | db §9.6 | 8행 다룸·**결정적 CAS 스파이**(`FakeProductStockPort.contention_count` 재시도·fresh snapshot version 1→2)·실 `ThreadPoolExecutor` 동시성·**실 SQLite `BEGIN EXCLUSIVE` 주입→503**·소진→503·롤백 | ✅ |
| Q-4 | 메커니즘 소유권 **[🔴치명]** | db §9.5 | 커스텀 백엔드/PRAGMA/몽키패치 0(check-mechanism-ownership exit0) | ✅ |
| Q-5 | 마이그레이션 안전 | db §11 | `0001` 불변·`0002` `SeparateDatabaseAndState`(state-only `RenameModel`+`AlterModelTable`·`database_operations=[]`)·`db_table='catalog_product'` 보존·`makemigrations --check` 드리프트 0 | ✅ |
| Q-6 | 테스트/TDD | impl-test | **§1.1.T (설치 Y)×(핀 Y) 완전 준수**·pytest 17 passed·함수형·`@pytest.mark.django_db(transaction=True)`·수제 Fake(§20.5)·`objects.create`(§9.1) | ✅ |
| Q-7 | 경미 | §4·4.1·5·6.2 | 공개표면 어노테이션(check-public-surface-annotation exit0·`STATUS_CREATED: str`)·**의존성 핀 — 테스트스택 4종 핀**(ptcat WEAK 대비 PASS) | ✅ |

## 의미적 변종 / backstop-blind 메타

**의미적 변종 0건** — 백스톱 16종 exit0 = 의미 PASS와 일치(적대 grader 2명 독립 줄인용 검증). 단 **백스톱이 원리상 못 보는 2건**(라벨 무영향):
1. **NJ-7 HttpError 누락**: check-catch-all-handler는 `@api.exception_handler(Exception)` 존재만 봄(Codex 충족·exit0) → HttpError 별도 핸들러 부재로 인한 깨진본문 problem+json 미달은 **결정 레인 사각**(의미/EP 관측이 잡음).
2. **ACL-EX2 non-transient 누수**: `published_service.py:37·64`가 non-transient `DatabaseError`를 raw re-raise → ACL(`product_stock_adapter.py:8-34`)이 미번역 → catch-all 500. check-synthetic-infra-exc는 `from` 동반 합성만 봄(exit0). **표준-수준 #1 미해결 갭**(DR-44/45)·EP-3는 transient 503 정상이라 PASS·non-transient 500은 status 정당·형식 problem+json 안전 → 비치명 잔여흠.

## 에러 경로 라이브 관측 (§4.3.1)

> 통합 테스트(testserver·17 passed) + 조정자 직접 probe 실측.

| 키 | 관측 status | content-type | 화이트리스트 | 판정 |
|---|---|---|---|---|
| EP-1 깨진 본문 | **400**(probe: malformed/garbage JSON) | **application/json** ⚠️ | {400} | 🟡 **부분** — status ✅·**problem+json 미달**(§6.2:516 `HttpError` 핸들러 누락·ninja 기본 `{"detail"}`) |
| EP-2 무효 입력 | **400**(`test:151` q=0) | application/problem+json | {422,400} | ✅ 관측(ValidationError→400 핸들러) |
| EP-3 transient 소진 | **503**(`test:191` 실 SQLite EXCLUSIVE lock·`:299` 재시도소진) | application/problem+json | {503,409} | ✅ 관측 — **500 아님**(ACL-EX2/maj1 회귀 없음·transient 경로 정상) |
| EP-4 재고 부족 | **409**(`test:110`) | application/problem+json | {409} | ✅ 관측(FC-1 교차) |
| (비-EP) non-transient DB error | **500** | application/problem+json | — | ACL-EX2 누수(probe: disk I/O·IntegrityError→500·status 정당·형식 안전·잔여흠) |

## 조정자 노트

- **이번 라이브 목적 = §1.1.T 깨끗 baseline에서 Codex Tier-1 설치+핀 관측(ptcat 오염 해소) + carve-out/이주배타성/FC-2 재검증. 핵심 결과 전부 입증**:
  1. **Tier-1 설치+핀 완전 이행**(§1.1.T 매트릭스 (설치 Y)×(핀 Y)) — **ptcat의 "핀 0·Q-7 WEAK"는 *fixture 오염*(조정자 pytest 선설치) 탓이었고, 깨끗 baseline에선 Codex가 pytest·pytest-django·pytest-mock·factory_boy를 설치+`requirements.txt` 핀+`pyproject.toml` 설정 완비.** Q-6·Q-7 PASS.
  2. **FC-2 PASS**(경계·부호·status 3종 mutation 다 red) — **ptcat 치명 FAIL(경계 green) 해소**. `test_concurrent`(stock=1·q=1=경계)가 잡음. 단 단위(`test_product_stock`)는 `available==quantity` 직접 케이스 미보유(통합이 커버) → 단위 보강 권고.
  3. **catalog 완전이주**(SH-1/4 PASS·INSTALLED_APPS 탈등록·db_table 보존) — 옛 루트 `.py` 8개 삭제. 단 **빈 `catalog/`·`catalog/migrations/` dir husk 잔존**(§10.4 `git rm -r` 미사용·git 미추적·SH-1/4 무영향·경미).
- **종합 PASS**(치명 게이트 FAIL 0) — ptcat 종합 FAIL(FC-2)에서 **개선**. 품질 **중**(WEAK 3: NJ-1 JsonResponse·NJ-5 bare·NJ-7 HttpError).
- **가장 날카로운 실질 흠 = HttpError 누락**(EP-1 깨진본문 problem+json 미달). **책임 = architect**: `design-spec:98`이 "Non-JSON content-type·parse 실패는 framework-default·outside contract"로 선제 배제 → coder는 명세 충실 구현. 단 표준 §6.2:516은 깨진본문 problem+json 변환을 *명시 처방*이라 명세의 배제가 표준과 충돌. **§6.3 C정책(내부 415 비적용)과 무관한 별개 처방**(415=content-type 협상·HttpError=parse 실패 형식). → 후속 후보(architect 단계 집행 갭).
- 부수(채점 무관): NJ-1 `JsonResponse`는 §6.2:487 처방 이탈이나 RUBRIC:67/EVAL-METHOD:100이 **🟡 경미**로 못박음(중앙화·content-type 충족·기능결함 아님·grader 갈림 underdetermined). DR-48 클래스 컨트롤러 준수(`@api_controller`·`ControllerBase` 미상속). 컴포지션 루트 = `order_api_router.register_order_api`(global factory 주입).
- `N_grader`=2(적대)+조정자 결정레인(full ≥3 미달). 백스톱·pytest·FC-2 mutation·EP·§1.1.T 전부 조정자 직접 실측(자기보고 불신). **N=1·단일태스크 → 우열결론 아님**(ptcat과 N=2 통제이나 catalog 판정소유 분해가 런마다 다름).

## 부록 — 후속 후보 (채점 골격 밖)

- **🔴 HttpError 깨진본문 problem+json 미달 (architect 집행 갭)**: 표준 §6.2:516이 `@api.exception_handler(HttpError)`를 명시 처방하나 design-spec이 "outside contract"로 배제 → EP-1 plain. **런간 비결정**(ptcat은 problem+json·ptboot는 plain). architect가 §6.2 catch-all 완전성(HttpError 포함)을 명세에 박는 처방 후보 — 단 N=1·design-architect 단계라 백스톱 부적합 가능성. NJ-7 의미 레인 강화 후보.
- **ACL-EX2 non-transient 누수**(표준-수준 #1 미해결·DR-44/45): `published_service` non-transient DatabaseError raw 재-raise → ACL 미번역 → 500. transient는 503 정상. 백스톱(check-synthetic-infra-exc) 원리상 사각(from 동반 합성만). 기존 미해결 갭 재확인.
- **FC-2 단위 경계 보강**: `test_product_stock`에 `available==quantity` 직접 케이스 추가 권고(현재 통합 `test_concurrent`만 커버).
- **catalog 빈 dir husk**: §10.4 `git rm -r` 미사용으로 빈 `catalog/migrations/` 잔존(SH-1/4 무영향·경미). ptcat 동일 재발.
- 품질 nit: NJ-1 `JsonResponse`·NJ-5 `-> Status` bare.
