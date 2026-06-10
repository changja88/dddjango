# 채점 결과지 — finallive-claude (파이널 라이브 dual · 누적 처방 통합 검증 · Claude)

> **방법** EVAL-METHOD v3(+§1.1.T·§4.3.1) · **채점일** 2026-06-10 · **픽스처** `~/Desktop/dddjango-finallive-claude`(baseline `c0f62a2` = `catalog.Product` 평면앱 + ninja/ninja-extra·**테스트도구 0·pytest 설정 없음** Tier-1 부트스트랩 관측 baseline) · **런타임** Claude(plugin 캐시 동기 = 소스 최신 `824ccb0` 신선화·plugin.json **1.9.0**·**백스톱 16종**·FC-2 (b)+(d)·django-web §11·L1·2b정정 반영) · **N** 1 · **태스크** "재고 부족 409·충분 시 차감 주문 생성 API"(ptcat/ptboot/nj7live/Codex와 **verbatim 동일 프롬프트**) · **게이트** 배치③설계자결정·내부전용·ninja-extra 클래스 컨트롤러·G1 멱등성 미적용(선택1)·G2 승인·thinking OFF · **범례** ✅PASS ❌FAIL 🟡WEAK/경미 ⏸️보류 ➖N/A
> **⚠️ 단서**: `N_grader`=조정자 결정레인 직접 실측(자기보고 불신) — 백스톱16·pytest·FC-2 mutation·FC-1 골든·EP probe 전부 조정자 직접 실행 · **N=1·단일태스크·런간 비결정 → 우열결론 아님**
> **🔬 바이트코드 위생**: 모든 동적 측정은 `.pyc`·`__pycache__` 완전 purge 후 실측. (FC-2 복원 확인 시 `__pycache__` 디렉토리만 지우고 `.pyc` 잔존으로 거짓 9-failed 발생 → `.pyc`까지 명시 삭제 후 34 passed 확정. nj7live FC-1 stale pyc 교훈 연장.)
> **fixture 도구 환경**(§1.1.T): **env**(채점 전)=테스트도구 0(baseline `c0f62a2`) · **produced**=Claude가 `pyproject.toml`에 `pytest`·`pytest-django`·`pytest-mock`·`factory-boy` 추가+핀(+`DJANGO_SETTINGS_MODULE`) · **조정자 추가 도구 0**(오염 없음 — Claude가 `.venv` 직접 부트스트랩)

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | **catalog = 판정 소유 분해**(MQ0=Y[baseline catalog `R`/`D`+application/catalog 재생성]·MQ1=Y[`product.py:28` `deduct_stock` 재고판정 소유]·MQ2=N) + **order = 신규 BC** → 양 BC §0 전부 강제 |
| ② 치명 게이트 | **✅ FAIL 0건.** SD-1~7·FC-1~3·SH-1·2·3·4·**7**·NJ-1·2·Q-4 **전부 PASS** — **SH-7**(협력 포트)이 `domain_layer/order/port/`에 올바로 위치(Codex FAIL 지점 통과) |
| ②.5 실질성 관문 | 빈 골격 아님·양 BC 도메인 실코드·테스트 34 실재·非-vacuous(FC-2 mutation red 입증) |
| ③ 비치명·의미변종 | 의미적 변종 0건 · **EP-1 깨진본문 problem+json 미통일**(400 `application/json`·관측 트랙·비산입) → Q-2 🟡 |
| ④ TIER-Q 등급 | **품질 상**(WEAK 1: Q-2 깨진본문 problem+json 미통일·FAIL 0) — FC-2 (b)+(d) 처방효과·SH-7 정위치·SD-7 OHS carve-out 논증·NJ-7 catch-all·ACL-EX2 누수0·Q-5 정교 |

**한 줄 요지**: **✅ 종합 정적 준수(치명 0)** — SH-7 협력 포트를 `domain_layer/order/port/`에 정위치(Codex 치명 FAIL 지점 통과)·SD-7 ACL carve-out를 design-spec:24에서 표준 line 144(OHS 미노출+행잠금 불가피) 명시 논증·FC-2 경계테스트 보유·NJ-7 catch-all. **잔여 흠**: **EP-1 깨진본문이 400이나 `application/json`(problem+json 미통일)** — `config/api.py`에 HttpError/JSONDecodeError 핸들러 부재로 ninja 기본 400이 중앙 변환점 우회. **nj7-httperror 처방 중 A(architect)는 작동(design-spec:95·:319 형식 의무 명시) — 샌 곳은 coder 전사 누락+reviewer 미발화[사후정정 2026-06-10] — Codex(problem+json 완비)와 정확히 교차.**

**2차원 라벨**: (정적: **준수** — 치명 0·품질 상) × (라이브: **발화/관측** — 백스톱16 exit0·FC-2 mutation red·FC-1 골든 전케이스·EP probe 실측) · `폴더 동작`: 미검증(재빌드 아님) · `에러경로 계약`: **부분**(EP-2 422·EP-3 503·EP-4 409 problem+json ✅·**EP-1 깨진본문 400 application/json — problem+json 미달**) · `성공경로`: **정상**(클린빌드 201∧잔7)

---

## A. TIER-S 척추 — S-DDD

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SD-1 | 빈혈: 판정 소유 | ddd §3.2 | `product.py:28-32` `deduct_stock`(`stock<quantity` raise·`stock-=quantity`·경계 `==` 성공 docstring 명시)·`order.py:35-47` `Order.place`(불변식·total 계산) | ➖ | ✅ | ✅ | ✅ |
| SD-2 | 빈혈: 프로덕션 호출 | §3.2·3.6 | `place_order_command.py:47-55` port→`Order.place`→repo.add·catalog `deduct_stock_command`→`product.deduct_stock`·죽은코드 아님 | ➖ | ✅ | ✅ | ✅ |
| SD-3 | 빈혈: 무복제 | §3.2 | `product_repository.py:33-41` `filter(id=,version=).update(stock=,version=+1)` version CAS만·"WHERE stock>=qty 금지" docstring·판정 SQL 복제 0(check-anemic-sql-guard exit0) | ✅ | ✅ | ✅ | ✅ |
| SD-4 | 애그리거트 경계 | §3.3 | `place_order_command.py:46` 단일 `transaction.atomic`·`order.py:22` `product_id:int`(ID참조·cross-BC FK 0·DR-37 준수) | ✅ | ✅ | ✅ | ✅ |
| SD-5 | 모델 표현력 | §3.1·3.5 | `Product`/`Order` 엔티티·`StockDeductionResult`(frozen 값객체)·도메인 메서드·유비쿼터스 | ✅ | ✅ | ✅ | ✅ |
| SD-6 | 계층 순수성(P1a) | §5.1·6.1; ninja §6.2 | domain/application HTTP·status 변환 **0**(order.py:7 "HTTP·status 모름")·status 매핑은 presentation `config/api.py`+`problem.py` 중앙만·command 도메인예외만 raise(check-error-centralization exit0) | ✅ | ✅ | ✅ | ✅ |
| SD-7 | 컨텍스트 통신 | §3.2(3)·2.5 | order 코어(`place_order_command`)는 협력 포트 `ProductStockPort`(domain_layer/order/port/)로만 의존·ACL `product_stock_adapter`가 catalog 소비+예외 전수번역(`from` 보존)·**catalog OHS 미노출(published_service 빈)+단일트랜잭션 행잠금 불가피 → ACL 직접(design-spec:24 표준 line144 carve-out 명시 논증)** | ✅ | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SH-1 | 컨테이너 | §0-1 | 양 BC `application/catalog/`·`application/order/`·INSTALLED_APPS `application.*`(settings:41-42)·루트 catalog 비어있음(git `R` rename 이주·잔존 0·check-app-container exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-2 | 4계층 | §0-2 | 양 BC `{domain,application,infra,presentation}_layer/` 물리 분리(check-layer-skeleton exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-3 | 종류폴더+거주명명 | §0-3·0-4·§4 | 종류 2차 폴더 전체·데이터소스 골격·`command/`=`PlaceOrderCommand`·`DeductStockCommand`·`dto/`=`PlaceOrderRequest`·`DeductStockRequest` | ✅ | ✅ | ✅ | ✅ |
| SH-4 | Django앱 위치 | §0-5 | `models.py`·`migrations/`가 `infra_layer/django_catalog/`·`django_order/`·AppConfig label | ✅ | ✅ | ✅ | ✅ |
| SH-5 | ORM 명명 | §0-6·§4 | `ProductModel`·`OrderModel`(infra)·도메인 `Product`·`Order` bare | ✅ | ✅ | ✅ | — |
| SH-6 | 포트/구현 명명 | §4 | `ProductStockPort`↔`DjangoProductStockAdapter`(Port→Adapter·DR-41)·`ProductRepository`↔`DjangoProductRepository`·`Interface`/`Impl` 0 | ✅ | ✅ | ✅ | — |
| **SH-7** | **협력 포트 위치** | **§2** | **✅ `ProductStockPort`가 `application/order/domain_layer/order/port/product_stock_port.py`**(표준 정위치)·docstring "order 도메인이 의존하는 역할 포트"·command가 domain port 의존(DIP)·**Codex(application_layer 오배치) 대비 정확** | ✅ | ✅ | ✅ | ✅ |
| SH-8 | ACL 분리 | §2·§3 | ACL `infra_layer/acl/product_stock_adapter.py`·`repository/`와 미혼합 | ✅ | ✅ | ✅ | — |
| SH-9 | 단일 레이아웃 | §1.4 | 단일 레이아웃·`test`/`tests` 공존 0 | ✅ | ✅ | ✅ | — |
| SH-10 | 테스트 의미군 | §1.3 | `test/{unit,integration}/`+factories 분리·HTTP=integration·평면나열 0 | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| NJ-1 | 스택 채택 | §1.1·§10 | `config/api.py:36` `NinjaExtraAPI`·`order_controller.py:33` `@api_controller("/orders")`+`@route.post`·JsonResponse/DRF 0 | ✅ | ✅ | ✅ | ✅ |
| NJ-2 | operation 얇음 | §1.3·2.2 | `order_controller.py:63-69` command 호출+Location 헤더+`return 201, order`만·비즈로직·ORM·수동파싱 0 | ✅ | ✅ | ✅ | ✅ |
| NJ-3 | Schema 입출력 분리 | §2.2·3.1 | `OrderIn`/`OrderOut`/`ProblemOut` 분리·도메인 직접 직렬화 0 | ➖ | ✅ | ✅ | —(강) |
| NJ-4 | status별 response 선언 | §2.2·§8 | `order_controller.py:43-49` `response={201:OrderOut,404/409/422/503:ProblemOut}` 다중 선언 | ✅ | ✅ | ✅ | —(강) |
| NJ-5 | operation 문서화 | §2.2 | `:50` `summary="주문 생성"`·`:51` description·`:33` tags·반환타입 `tuple[int,OrderOut]`(무정보 object 아님) | ➖ | ✅ | ✅ | —(경미) |
| NJ-6 | ninja 버전 핀 | §2.1 | requirements/pyproject `django-ninja`·`django-ninja-extra` 핀 | ✅ | ✅ | ✅ | —(경미) |
| NJ-7 | 오류 변환 완전성(catch-all) | §6.2 | `config/api.py:173` `@api.exception_handler(Exception)` catch-all·`:151` OperationalError transient 분기·bare raise 0·**미식별→500 problem+json** ✅. (단 깨진본문 HttpError는 핸들러 부재로 problem+json 우회 — EP-1·Q-2에 기록·NJ-7 catch-all 자체는 충족) | ✅ | ✅ | ✅ | —(강) |

## TIER-S(핵심) — FC

| ID | 항목 | Result(조정자 직접 실측·클린빌드) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| FC-1 | 골든 오라클 | **독립 호출 probe**: 재고10주문3→**201∧잔7∧order1** / 재고2주문5→**409∧잔2∧order0** / 재고3주문3(경계)→**201∧잔0** 전부 일치(nj7live-claude `Status` 500을 `return 201,order` tuple로 우회·DeprecationWarning만·기능 정상) | ✅ | ✅ | ✅ | ✅ |
| FC-2 | 테스트 비-vacuous | **mutation 주입**: ②경계(`stock<quantity`→`<=`)→3 red(`test_stock_equals_quantity`·`test_deduct_stock_at_exact_boundary`·`test_deduct_stock_equal_quantity`) / ①차감→9 red / 복원후 34 passed — **경계테스트 보유=FC-2 (b)+(d) 처방효과**(design-spec §6.6 "재고==수량" 별도 관찰 행위) | ✅ | ✅ | ✅ | ✅ |
| FC-3 | 도메인 정합 | 음수재고 방지(CHECK+도메인 가드)·차감 방향 정상·주문↔재고 인과 정상(차감 후 주문) | ➖ | ✅ | ✅ | ✅ |

## C. 기존규약 마스크 (적용 메모 — §1.1.M)

- **MQ0**: **Y** — baseline `catalog/` git `R`(rename → `application/catalog/infra_layer/django_catalog/`)+`D`(admin/models/tests/views).
- **MQ1**: **Y** — `application/catalog/domain_layer/product/product.py:28` 재고판정·차감(신규·전체 추가).
- **MQ2**: **N** — catalog가 재고 판정 소유.
- **판정**: catalog = 판정 소유 분해 → `application/catalog/` 위치+4계층+판정 실코드(충족). order = 신규 BC → §0 전부 강제. **양 BC SH-1·2·3·4·7 전부 PASS**(Codex와 달리 SH-7도 정위치).

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| Q-1 | 스코프/과설계·G1 | ddd §6.8·hr §1.1 | 멱등성 미발명(G1 선택1 준수)·멀티라인/합산 0·고-blast(동시성) §9.6 CAS로 상정 | ➖ | ✅ | ✅ |
| Q-2 | API 계약 | api §4~14 | status/problem(RFC 9457) 대체로 일관(`problem.py` type/title/status/detail/instance)·**단 깨진본문(EP-1)이 problem+json 아닌 `application/json` 400 — HttpError 핸들러 부재로 일관성 흠** | ➖ | 🟡 | 🟡 |
| Q-3 | §9.6 형식+테스트 | db §9.6·test §20.5 | version CAS+재시도(catalog `deduct_stock_command`)·소진→`StockContentionError`→409·`test_transient_and_catchall` 503/catch-all 실현 | ➖ | ✅ | ✅ |
| Q-4 | 메커니즘 소유권 **[🔴치명]** | db §9.5·16.4 | 커스텀 DB백엔드/PRAGMA/몽키패치 0·표준 ORM CAS만(check-mechanism-ownership exit0) | ✅ | ✅ | ✅ |
| Q-5 | 마이그레이션 안전 | db §11 | 0001 **byte 동일**(baseline 보존)·0002 state rename `Product→ProductModel`+`db_table='catalog_product'` 못박음·0003/0004 expand·`makemigrations --check` 정합 | ➖ | ✅ | ✅ |
| Q-6 | 테스트/TDD | test·tdd | `check`+pytest 그린(34)·인수=design-spec §6.6 행위목록 덮음·의미군 분리·pytest 함수형·`mocker`·factory_boy(`product_factory`)·**설치+핀 §2.1 완전 준수**(§1.1.T) | ✅ | ✅ | ✅ |
| Q-7 | 경미 | hr §4·5·6.2 | 공개표면 어노테이션(`_TRANSIENT_LOCK_SIGNATURES` 등 타입선언·check-public-surface-annotation exit0)·의존성 핀·주석 언어 일관 | ➖ | ✅ | ✅ |

## 의미적 변종 / backstop-blind 메타

- **의미적 변종 0건** — `[결정PASS∧의미FAIL]` 칸 없음.
- **EP-1 깨진본문 problem+json 미달은 backstop·NJ-7 결정레인 사각**: 백스톱 16종·NJ-7 catch-all grep(`@api.exception_handler(Exception)`)으로는 *미식별 예외*만 보장 → ninja 기본 HttpError(깨진본문 400 application/json)는 catch-all을 거치지 않아 problem+json 미통일을 미검출. **테스트도 깨진본문 케이스 부재**(`test_transient_and_catchall`=transient·catch-all만) → 코더가 못 봄. nj7-httperror 처방 **C(백스톱 ⑯ HttpError 확장)** 집행 근거.
- **maj1 과잉매핑 사각 없음**: `handle_operational_error:160` `if not _is_transient_lock` 분기(transient만 503·아니면 catch-all 500)·check-transient-overmapping exit0.

## 에러 경로 라이브 관측 (§4.3.1)

| 키 | 관측 status | content-type | 화이트리스트 | 판정 |
|---|---|---|---|---|
| **EP-1 깨진 본문** | **400** | **`application/json`** | {400}+`application/problem+json` | **🟡 부분** — status 400 ✓·**content-type problem+json 미달**(HttpError/JSONDecodeError 핸들러 부재·ninja 기본 400 우회) |
| **EP-2 무효 입력**(수량0) | **422** | `application/problem+json` | {422,400} | ✅ (ValidationError·InvalidOrderError 핸들러) |
| **EP-3 transient 소진** | **503** | `application/problem+json` | {503,409} | ✅ **ACL-EX2 누수0** — raw `OperationalError("database is locked")`→503(`_is_transient_lock` marker)·비-retryable("no such table")→500·`IntegrityError`→500(영구장애 정당)·CAS 소진(StockContentionError)→409 |
| **EP-4 재고 부족** | **409** | `application/problem+json` | {409} | ✅ (StockUnavailableError 핸들러·FC-1 골든 교차) |

> **EP-1 평가**: Claude `config/api.py`는 도메인 예외·ValidationError·OperationalError·catch-all Exception 핸들러만 두고 **HttpError/JSONDecodeError 핸들러가 없다**. 깨진본문은 ninja 1.6.x `parse_body`가 `HttpError(400)`을 raise하는데, 이를 잡는 중앙 핸들러가 없어 ninja 기본 응답(400 `application/json`)이 problem+json 변환점을 우회한다. **status는 화이트리스트 {400} 충족이나 content-type 미통일** = EP-1 부분. (Codex는 `@api.exception_handler(HttpError)`+`JSONDecodeError`로 400 problem+json 완비 — 정확히 교차.) **EP는 관측 트랙(치명 아님·freeze 밖)이라 종합 라벨 자동 FAIL 아님** — 잔여흠 원장 + Q-2 WEAK에만 입력.

## 조정자 노트

1. **종합 = 정적 준수(치명 FAIL 0)·품질 상.** 33항목 중 Q-2만 WEAK(깨진본문 problem+json 미통일)·나머지 전부 PASS. Codex의 종합 FAIL 원인이던 SH-7을 Claude는 `domain_layer/order/port/`에 정위치해 통과.
2. **dual 정확한 교차**(P4③ 재현): **Codex=SH-7(구조) 치명 FAIL·EP-1 problem+json 완비** / **Claude=SH-7 PASS·EP-1 problem+json 미달**. 흠이 구조 ↔ 에러경로 형식으로 서로 반대편에 위치. Codex 흠은 *치명*(종합 FAIL)·Claude 흠은 *비치명 관측*(종합 PASS) — 라벨은 갈리나 **N=1·단일태스크·우열결론 아님**.
3. **SD-7 ACL carve-out 정당화**: Claude는 catalog OHS(published_service)를 빈 패키지로 두고 ACL이 catalog `application_layer.DeductStockCommand`+`infra_layer.DjangoProductRepository`를 직접 소비. design-spec:24가 표준 houserules §2 line144("OHS 미노출 또는 단일 트랜잭션·행 잠금 불가피 시 ACL 직접")를 명시 인용·논증 → **carve-out 충족 PASS**. order 코어(PlaceOrderCommand)는 협력 포트로만 의존(직접 import 0). 의미 관찰: Codex는 OHS(published_service.write) 경유로 더 느슨한 결합이나, 둘 다 표준 ACL 범위 내.
4. **FC-2 (b)+(d) 처방 효과 라이브 입증**: design-spec §6.6 "외부 관찰 가능 행위 목록"이 "재고==수량(경계값)→201,재고=0"을 *별도 관찰 행위*로 박았고(처방 b), 인수테스트가 그 경계를 행사 → 경계 mutation(`<`→`<=`)에 red. (Codex도 동일 효과 — 양 런타임 FC-2 처방 작동.)
5. **nj7-httperror 처방 C 집행 근거**: Claude가 또 깨진본문 problem+json 미달(`@api.exception_handler(HttpError)` 부재). **[사후정정 2026-06-10]** 처방 A(architect)는 *작동* — design-spec:95·:319에 "깨진 본문·parse 실패도 중앙 problem+json 변환점이 덮는다" 형식 의무가 실제로 박혔다(초판의 "A·B 미반영" 표현은 A에 대해 부정확). 샌 곳은 ① coder 전사 누락(§6.2:527 레시피 블록에서 핸들러 7종 중 HttpError만 빠뜨림 — P1a·C4 동형 묻힌-가드 전사 누락) ② design-spec §6.6 행위 목록에 깨진 본문 부재(§6.6의 결["외부 결과를 가르는 행위"]대로면 일관된 제외)→acceptance-tester 미행사→coder가 Red를 본 적 없음 ③ reviewer 불릿(B) 캐시 실재·신선에도 라이브 미발화(B 라이브 0/1·3분 홀리스틱 감사 가시성 천장) ④ 백스톱 ⑯ 원리상 사각(Exception catch-all만 검사). 사전 합의의 결과-기준 조건("또 plain이면 C 집행") 충족 → **백스톱 ⑯ HttpError 확장(C) 같은 날 집행**(적대 2렌즈 리뷰 후 구현·발화 매트릭스 10/10 검증 — claude exit2·codex exit0·합성 8종 FP 0). Codex는 같은 처방에서 HttpError 핸들러 구현 — 런간 비결정.
6. **N=1·단일태스크·런간 비결정 → 우열결론 아님.**

## 부록 — 동적 측정 로그 요약

- **클린빌드 pytest**: 34 passed(0.27s·`.pyc`+`__pycache__` 완전 purge 후). tuple 반환 2건 DeprecationWarning(기능 정상).
- **백스톱 16종**: 전부 exit 0.
- **FC-2 mutation**: ②경계→3 red·①차감→9 red·복원후 34 passed(`.pyc` 완전 purge 후 — 부분 purge 시 stale pyc로 거짓 9-failed 관측 → 정정).
- **FC-1 골든+EP probe**: 독립 호출 스크립트(`setup_test_environment`)로 .venv 실측 — 골든 3케이스 일치·EP 4키 중 EP-1만 content-type 부분 미달.
