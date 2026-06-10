# 채점 결과지 — finallive-codex (파이널 라이브 dual · 누적 처방 통합 검증 · Codex)

> **방법** EVAL-METHOD v3(+§1.1.T·§4.3.1) · **채점일** 2026-06-10 · **픽스처** `~/Desktop/dddjango-finallive-codex`(baseline `f68d092` = `catalog.Product` 평면앱 + ninja/ninja-extra·**테스트도구 0·pytest 설정 없음** Tier-1 부트스트랩 관측 baseline) · **런타임** Codex(plugin 캐시 동기 = 소스 최신 `824ccb0` 신선화·plugin.json **1.9.0**·**백스톱 16종**·FC-2 (b)+(d)·django-web §11·L1·2b정정 반영) · **N** 1 · **태스크** "재고 부족 409·충분 시 차감 주문 생성 API"(ptcat/ptboot/nj7live와 **verbatim 동일 프롬프트**) · **게이트** 배치③설계자결정·내부전용·ninja-extra 클래스 컨트롤러·G1 멱등성 미적용(선택1)·G2 승인(포트 위치 권고 잔여 수용)·thinking OFF · **범례** ✅PASS ❌FAIL 🟡WEAK/경미 ⏸️보류 ➖N/A
> **⚠️ 단서**: `N_grader`=조정자 결정레인 직접 실측(자기보고 불신) — 백스톱16·pytest·FC-2 mutation·FC-1 골든·EP probe 전부 조정자 직접 실행 · **N=1·단일태스크·런간 비결정 → 우열결론 아님**
> **🔬 바이트코드 위생**: 모든 동적 측정은 `__pycache__` 완전 purge 후 실측(루트 catalog stale `.pyc` 포함 — nj7live FC-1 마스킹 교훈). 클린 빌드 결과만 채점 반영.
> **fixture 도구 환경**(§1.1.T): **env**(채점 전)=테스트도구 0(baseline `f68d092`·venv=Django/ninja/ninja-extra) · **produced**=Codex가 `pyproject.toml`에 `pytest==8.3.5`·`pytest-django==4.9.0`·`pytest-mock==3.14.0` 추가+핀(+`[tool.pytest.ini_options] DJANGO_SETTINGS_MODULE`) · **조정자 추가 도구 0**(오염 없음 — Codex가 `.venv` 직접 부트스트랩)

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | **catalog = 판정 소유 분해**(MQ0=Y[baseline catalog `D`+application/catalog 재생성]·MQ1=Y[`product.py:17` `decrement_stock` 재고판정·차감 소유]·MQ2=N) + **order = 신규 BC** → 양 BC §0 전부 강제 |
| ② 치명 게이트 | **❌ FAIL 1건 → 종합 FAIL.** **SH-7**(협력 포트 위치) FAIL — `ProductStockPort`가 `application_layer/place_order/port/`(표준=`domain_layer/order/port/`). SD-1~7·FC-1~3·SH-1·2·3·4·NJ-1·2·Q-4는 **전부 PASS** |
| ②.5 실질성 관문 | (SH-7 치명 FAIL로 종료 전 참고) 빈 골격 아님·양 BC 도메인 실코드·테스트 25 실재·非-vacuous(FC-2 mutation red 입증) |
| ③ 비치명·의미변종 | 의미적 변종 0건 · NJ-3~7·config 배치 전부 *깔끔* · **NJ-7 catch-all PASS**(nj7live 대비 개선) |
| ④ TIER-Q 등급 | (종합 FAIL이라 비산입) 만약 SH-7 위치가 정상이었다면 품질 **상**(FC-2 (b)+(d) 처방효과·NJ-7·EP 전수 problem+json·ACL-EX2 누수0·멱등성 스코프준수·경계테스트 보유) — **그러나 협력 포트 오배치가 치명이라 무의미** |

**한 줄 요지**: **🎯 처방 효과 다수 라이브 입증**(FC-2 경계테스트 보유→mutation red·NJ-7 catch-all `@api.exception_handler(Exception)`·EP-1 깨진본문 400 problem+json·ACL-EX2 transient→503 누수0)이나, **종합 = FAIL** — 처방과 **무관한** SH-7: `ProductStockPort`를 `domain_layer/order/port/` 아닌 `application_layer/place_order/port/`에 배치(협력 포트 위치 치명 위반). **architect 설계가 박고(design-spec:85 "use-case dependency")·reviewer가 권고로 강등·백스톱 16종이 포트 위치 미검출·사용자 G2 수용 → 채점만 적출.**

**2차원 라벨**: (정적: **FAIL** — SH-7 치명) × (라이브: **발화/관측** — 백스톱16 exit0·FC-2 mutation red·FC-1 골든 전케이스·EP probe 실측) · `폴더 동작`: 미검증(재빌드 아님) · `에러경로 계약`: **관측**(EP-1 400·EP-2 422·EP-3 503·EP-4 409 전부 problem+json·ACL-EX2 누수0) · `성공경로`: **정상**(클린빌드 201∧잔7)

---

## A. TIER-S 척추 — S-DDD

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SD-1 | 빈혈: 판정 소유 | ddd §3.2 | `product.py:17-22` `decrement_stock`(`quantity<1`·`stock<quantity` raise·`stock-=quantity` 차감)·`order.py:19-31` `Order.create`(불변식 quantity/unit_price·total 계산)·재고판정 도메인 소유 | ➖ | ✅ | ✅ | ✅ |
| SD-2 | 빈혈: 프로덕션 호출 | §3.2·3.6 | `decrement_product_stock_command.py:22-25` 조회→`product.decrement_stock`→`save_stock`(version CAS 재시도3)·`place_order_command.py:27·31` port→`Order.create`·죽은코드 아님 | ➖ | ✅ | ✅ | ✅ |
| SD-3 | 빈혈: 무복제 | §3.2 | `product_repository.py:28-34` `filter(id=,version=).update(stock=,version=F+1)` version CAS만·판정 SQL(`stock__gte`) 복제 0(check-anemic-sql-guard exit0) | ✅ | ✅ | ✅ | ✅ |
| SD-4 | 애그리거트 경계 | §3.3 | `place_order_command.py:26` 단일 `transaction.atomic`·`order.py:13` `product_id:int`(ID참조·cross-BC FK 0·DR-37 준수) | ✅ | ✅ | ✅ | ✅ |
| SD-5 | 모델 표현력 | §3.1·3.5 | `Product`/`Order` 엔티티·`decrement_stock`/`create` 도메인 메서드·`ProductStockSnapshot` 값객체(frozen) | ✅ | ✅ | ✅ | ✅ |
| SD-6 | 계층 순수성(P1a) | §5.1·6.1; ninja §6.2 | domain/application HTTP·status 변환 **0**·status 매핑은 presentation `config/api.py` 중앙핸들러만·command는 도메인예외만 raise(check-error-centralization exit0) | ✅ | ✅ | ✅ | ✅ |
| SD-7 | 컨텍스트 통신 | §3.2(3)·2.5 | **ACL `product_stock_adapter.py:26`가 catalog `published_service.write.decrement_product_stock`(OHS)만 호출**·catalog 예외 3종→order 포트예외 전수번역(`:30-35`)·catalog 구체 infra(ProductModel) 직접 import 0 — nj7live ProductModel 직접 import보다 깔끔 | ✅ | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SH-1 | 컨테이너 | §0-1 | 양 BC `application/catalog/`·`application/order/` 하위·INSTALLED_APPS `application.catalog...`/`application.order...`(settings:41-42)·루트 catalog는 빈 `migrations/` 디렉토리만(소스 .py 0·git `D`·check-app-container exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-2 | 4계층 | §0-2 | 양 BC `{domain,application,infra,presentation}_layer/` 물리 분리(check-layer-skeleton exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-3 | 종류폴더+거주명명 | §0-3·0-4·§4 | 종류 2차 폴더 전체·데이터소스 골격(`domain_layer/product/`·`domain_layer/order/` ORM명 도출)·`command/`=`PlaceOrderCommand`·`DecrementProductStockCommand`·`dto/`=`PlaceOrderRequest`·`DecrementProductStockRequest`(@dataclass) | ✅ | ✅ | ✅ | ✅ |
| SH-4 | Django앱 위치 | §0-5 | `models.py`·`migrations/`가 `infra_layer/django_catalog/`·`django_order/`·AppConfig `label`(settings 점경로 등록) | ✅ | ✅ | ✅ | ✅ |
| SH-5 | ORM 명명 | §0-6·§4 | `ProductModel`·`OrderModel`(infra)·도메인 `Product`·`Order` bare | ✅ | ✅ | ✅ | — |
| SH-6 | 포트/구현 명명 | §4 | `ProductStockPort`(추상)↔`DjangoProductStockAdapter`(구현·Port→Adapter·DR-41 헥사고날)·`ProductRepository`↔`DjangoProductRepository`·`Interface`/`Impl` 0 | ✅ | ✅ | ✅ | — |
| **SH-7** | **협력 포트 위치** | **§2** | **🔴 `ProductStockPort`가 `application/order/application_layer/place_order/port/product_stock_port.py`**(표준 houserules:144·178·190 = 협력 포트는 `domain_layer/<agg>/port/`)·`domain_layer/order/port/`는 빈 패키지·구현 ACL은 `infra_layer/acl/`에 올바로 위치(절반만 충족) | **❌** | **❌** | **❌** | **❌** |
| SH-8 | ACL 분리 | §2·§3 | ACL `infra_layer/acl/product_stock_adapter.py`·`repository/`(product_repository·order_repository)와 미혼합 | ✅ | ✅ | ✅ | — |
| SH-9 | 단일 레이아웃 | §1.4 | 한 앱 단일 레이아웃·`test`/`tests` 공존 0(check-structure exit0) | ✅ | ✅ | ✅ | — |
| SH-10 | 테스트 의미군 | §1.3 | `test/{unit,integration,e2e}/` 분리·HTTP=e2e(`test_place_order_api.py`)·평면나열 0 | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| NJ-1 | 스택 채택 | §1.1·§10 | `config/api.py:20` `NinjaExtraAPI`·`order_controller.py:25` `@api_controller("/orders")`+`@route.post`·`JsonResponse`/DRF 0(check-ninja-boundary-middleware exit0) | ✅ | ✅ | ✅ | ✅ |
| NJ-2 | operation 얇음 | §1.3·2.2 | `order_controller.py:71-79` command 호출 + `OrderOut.from_order` 매핑 + Location 헤더만·비즈로직·ORM·수동파싱 0 | ✅ | ✅ | ✅ | ✅ |
| NJ-3 | Schema 입출력 분리 | §2.2·3.1 | `OrderIn`(`schema_in.py`)·`OrderOut`(`schema_out.py`)·`ProblemDetailsOut`(`error_out.py`)·도메인 직접 직렬화 0 | ➖ | ✅ | ✅ | —(강) |
| NJ-4 | status별 response 선언 | §2.2·§8 | `order_controller.py:31-38` `response={201:OrderOut,400/404/409/422/503:ProblemDetailsOut}` 다중 status 선언(`openapi_extra`는 헤더·content 보강만) | ✅ | ✅ | ✅ | —(강) |
| NJ-5 | operation 문서화 | §2.2 | `:39` `summary="Create order"`·`:25` `tags=["orders"]`·반환타입 `Status`(무정보 `object` 아님) | ➖ | ✅ | ✅ | —(경미) |
| NJ-6 | ninja 버전 핀 | §2.1 | `requirements.txt`·`pyproject.toml` `django-ninja==1.6.2`·`django-ninja-extra==0.31.4` 핀(baseline 관례 유지) | ✅ | ✅ | ✅ | —(경미) |
| NJ-7 | 오류 변환 완전성(catch-all) | §6.2 | **`config/api.py:224` `@api.exception_handler(Exception)` catch-all 존재**·`:199` `DatabaseError` 핸들러(retryable 분기)·bare `raise exc` 0·미식별→500 problem+json 단일변환점 | ✅ | ✅ | ✅ | —(강) |

## TIER-S(핵심) — FC

| ID | 항목 | Result(조정자 직접 실측·클린빌드) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| FC-1 | 골든 오라클 | **독립 호출 probe**: 재고10주문3→**201∧잔7∧order1** / 재고2주문5→**409∧잔2∧order0** / 재고3주문3(경계)→**201∧잔0** 전부 일치(nj7live-claude `Status` 500 재현 안 됨 — `OrderOut`에 `status` 문자열 필드 없어 ProblemDetailsOut 검증 충돌 회피) | ✅ | ✅ | ✅ | ✅ |
| FC-2 | 테스트 비-vacuous | **mutation 주입**: ②경계(`stock<quantity`→`<=`)→`test_exact_stock`(stock==qty 경계) **red**(409≠201) / ①차감(`-=`→`+=`)→6 red / 복원후 25 passed — **경계테스트 보유=FC-2 (b)+(d) 처방효과**(nj7live-codex vacuous 개선) | ✅ | ✅ | ✅ | ✅ |
| FC-3 | 도메인 정합 | 음수재고 방지(CHECK `stock>=0`+도메인 `stock<quantity` 가드)·차감 방향 정상(`-=`)·주문↔재고 인과 정상(차감 성공 후 주문 생성) | ➖ | ✅ | ✅ | ✅ |

## C. 기존규약 마스크 (적용 메모 — §1.1.M)

- **MQ0**(기존앱 삭제·대체): **Y** — baseline `catalog/` 전체 git `D`(`__init__`·`models`·`apps`·`migrations/0001` 등) + `application/catalog/` 트리 재생성.
- **MQ1**(spec 핵심 판정 분기가 런 변경집합에): **Y** — `application/catalog/domain_layer/product/product.py:17-22`(신규·전체 추가) 재고판정·차감 메서드.
- **MQ2**(단순 상류 데이터소스): **N** — catalog가 재고 판정·차감을 *소유*(상류 데이터소스 아님).
- **판정**: catalog = **판정 소유 분해** → `application/catalog/` 위치 + 4계층 + 판정 실코드 채움 의무(전부 충족). order = 신규 BC → §0 전부 강제. 양 BC 위치·골격 의무 충족(SH-1·2·3·4 PASS), 단 SH-7 협력 포트 위치만 위반.

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| Q-1 | 스코프/과설계·G1 | ddd §6.8·hr §1.1 | 멱등성 미발명(`test_idempotency_key_does_not_suppress...:253` 중복 허용 명시·G1 선택1 준수)·멀티라인/합산 0·고-blast(동시성)는 §9.6 CAS로 G1 상정 | ➖ | ✅ | ✅ |
| Q-2 | API 계약 | api §4~14 | status/problem(RFC 9457) 일관(`_problem_body:46` type/title/status/detail/instance)·content-type `application/problem+json`·Location/Retry-After 헤더 | ➖ | ✅ | ✅ |
| Q-3 | §9.6 형식+테스트 | db §9.6·test §20.5 | version CAS+재시도3(`decrement_product_stock_command.py:21-33`)·소진→`StockContention`→503·`test_stock_contention...:224` mocker 스파이로 503 실현 | ➖ | ✅ | ✅ |
| Q-4 | 메커니즘 소유권 **[🔴치명]** | db §9.5·16.4 | 커스텀 DB백엔드/`DatabaseWrapper`/PRAGMA/몽키패치 0·표준 ORM `F()`/atomic만(check-mechanism-ownership exit0) | ✅ | ✅ | ✅ |
| Q-5 | 마이그레이션 안전 | db §11 | 새 catalog `0001`=baseline `0001` byte 동일(name='Product'·2026-05-28 보존)·`0002` version expand·`db_table="catalog_product"` 보존·`makemigrations --check` No changes | ➖ | ✅ | ✅ |
| Q-6 | 테스트/TDD | test·tdd | `check`+`pytest` 그린(25 passed)·인수=e2e 행위 덮음·의미군 분리·**pytest 함수형**(`@pytest.mark.django_db`)·`mocker`(`:228·232`)·factory non-blanket(create_product helper)·**설치+핀 §2.1 완전 준수**(§1.1.T) | ✅ | ✅ | ✅ |
| Q-7 | 경미 | hr §4·5·6.2 | 공개표면 어노테이션(`_RETRYABLE_*` 상수 타입선언·check-public-surface-annotation exit0)·의존성 핀(pyproject)·주석 언어 일관 | ➖ | ✅ | ✅ |

## 의미적 변종 / backstop-blind 메타

- **의미적 변종 0건** — `[결정PASS∧의미FAIL]` 칸 없음. SH-7은 결정·의미 *양 레인 모두 FAIL*(위장 변종 아닌 명시적 위치 위반).
- **backstop-blind (SH-7 사각)**: 백스톱 16종(check-app-container·check-layer-skeleton 등)이 **포트 위치를 결정 게이트로 검사하지 않음** → SH-7 위반에도 16종 전부 exit0. SH-7은 의미/grep 레인 전속(EVAL-METHOD §1.1 결정표 "find -type d -name port 부모가 domain_layer인가"). **이번 런이 그 사각을 실증** — architect 설계 결함이 백스톱·reviewer를 통과해 채점에서만 적출.
- **maj1 과잉매핑 사각 없음**: `database_exception_handler:204` retryable 분기 존재(if retryable→503 else→500)·check-transient-overmapping exit0과 정합.

## 에러 경로 라이브 관측 (§4.3.1)

| 키 | 관측 status | content-type | 화이트리스트 | 판정 |
|---|---|---|---|---|
| **EP-1 깨진 본문** | **400** | `application/problem+json` | {400} | ✅ (HttpError 핸들러 `config/api.py:134`·NJ-7 httperror 처방 효과) |
| **EP-2 무효 입력**(수량0) | **422** | `application/problem+json` | {422,400} | ✅ (ValidationError 핸들러 `:105`) |
| **EP-3 transient 소진** | **503** | `application/problem+json` | {503,409} | ✅ **ACL-EX2 누수0** — raw `OperationalError("database is locked")`→503(marker 매칭 `:96-102`)·비-retryable("no such table")→500·`IntegrityError`→500(영구장애 정당 분류) |
| **EP-4 재고 부족** | **409** | `application/problem+json` | {409} | ✅ (InsufficientStockForOrder 핸들러 `:170`·FC-1 골든 교차) |

> **ACL-EX2 평가**(메모리 #1 미해결 이슈): 이 산출물은 `config/api.py:199` `DatabaseError` 핸들러가 raw transient(`OperationalError` 락/deadlock marker)를 **503으로 정확 분류**하고 영구장애(no such table·IntegrityError)는 500으로 분리 → **transient→500 누수 없음**. ACL은 도메인 예외(StockContentionForOrder)로 번역(EP-3 어댑터 유형 ii)·raw 종단은 중앙 DatabaseError 핸들러가 포착. catch-all `Exception` 핸들러까지 형식 완전.

## 조정자 노트

1. **종합 FAIL의 단일 원인 = SH-7 협력 포트 위치.** 그 외 33항목 전 차원(SD 7·FC 3·NJ 7·SH 9·Q 7)이 PASS이고 처방 효과가 다수 입증됐으나, 사전식 집계상 치명 1건이 종합을 FAIL로 확정한다(가중평균 금지).
2. **SH-7 4중 미포착 체인**: ① architect가 `design-spec:85`에서 `ProductStockPort`를 "use-case dependency under `application_layer/place_order/port/`"로 설계(Order 애그리거트가 import 안 함을 근거) → ② discipline-reviewer가 G2에서 "설계 위반 아님·하우스룰 권고 잔여"로 강등 → ③ 백스톱 16종이 포트 위치 미검사 → ④ 사용자 G2 "1 승인"(자연 산출 보존 원칙). **채점만 적출.**
3. **표준 판정 근거**(architect 해석 B 기각): houserules `:144`("도메인은 협력 포트 `domain_layer/<aggregate>/port/`로 의존")·`:178`(폴더표 협력 포트=domain_layer)·`:190`("command는 domain repository/port 의존 DIP")가 협력 포트를 domain_layer에 명시(4중 근거). `PlaceOrderCommand`가 의존하는 port는 표준상 *domain port*여야 하므로(DIP) application_layer 배치는 위반. architect의 "도메인이 의존 안 하니 use-case 포트"라는 해석 여지(`:178` "도메인이 의존하는" 한정)는 정직히 기록하되, **결정 레인(위치 기반)·표준 다수근거상 FAIL**. ACL 구현은 `infra_layer/acl/`에 올바로 둬 ACL 패턴 절반만 충족한 점이 위치 위반을 더 분명히 한다.
4. **FC-2 (b)+(d) 처방 효과 라이브 입증**: Codex가 `test_exact_stock`(stock==quantity 경계)을 포함해 경계 mutation(`<`→`<=`)에 red. nj7live-codex(경계 미행사·vacuous green·FC-2 2/3 치명 FAIL)에서 개선 — 캐시 신선화로 반영된 처방이 작동.
5. **dual 반전(P4③ 재현)**: nj7live=Codex FC-2 FAIL·Claude FC-1 FAIL → finallive-codex=FC-2·FC-1·EP 전부 통과하나 **SH-7(구조) 치명 FAIL**. 치명 축이 기능(FC)에서 구조(SH)로 이동 — 런간 비결정의 또 다른 양상.
6. **N=1·단일태스크·런간 비결정 → 우열결론 아님.** Claude 런 채점과 대조는 양쪽 완료 후.

## 부록 — 동적 측정 로그 요약

- **클린 빌드 pytest**: 25 passed(0.22s·`__pycache__` purge·루트 catalog stale pyc 제거 후).
- **백스톱 16종**: 전부 exit 0(cwd=픽스처).
- **FC-2 mutation**: ②경계→1 failed(`test_exact_stock`)·①차감→6 failed·복원후 25 passed.
- **FC-1 골든+EP probe**: 독립 호출 스크립트(`setup_test_environment` 적용)로 .venv 실측 — 골든 3케이스·EP 4키 전부 화이트리스트 일치.
