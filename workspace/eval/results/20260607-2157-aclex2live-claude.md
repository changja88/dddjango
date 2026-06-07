# Claude aclex2live 채점 — B 트랙 ACL-EX2 예방 라이브 (EVAL-METHOD v3 §6 형식)

> **방법** v3 · **채점일** 2026-06-07 · **픽스처** `~/Desktop/dddjango-aclex2live-claude`(greenfield; baseline catalog 평면 `startapp` 시드를 런이 이주·판정 적재) · **런타임** Claude · **plugin** 1.7.0 · **산출** `.dddjango/20260607-2013-order-creation/`
> **태스크** 주문 생성 API(별도 order BC·catalog 재고 차감·부족 시 409) · **게이트**(고정) BC배치=미강제 / 렌즈=ddd+db+api / 스택=표준기본(Ninja) / 테스트러너=표준기본 / G1 멱등성=미도입·transient=503 / G1·G2=명백결함만 반송 / thinking=OFF
> **범례** ✅PASS · ❌FAIL · 🟡WEAK/경미 · ⏸️보류 · ➖N/A
> ⚠️ **단서**: **N_grader=1**(조정자 단독·blind 역할분리 미적용 — full 정본 아님) · **FC-1 골든표 사전등록 생략**(코드 열람 후 조정자 실측 probe로 갈음) · **자기보고 불신 적용**(코디 보고 대신 조정자 직접 read+EP probe+mutation+백스톱 15종 실측) · **N=1·단일태스크 timeline**(P4③ 우열·완료 결론 금지) · B 트랙=Claude 단일 인스턴스(직전 maj1live ACL-EX2 보유자)

## 종합 판정 (사전식 집계 — EVAL-METHOD §2)
| 단계 | 결과 |
|---|---|
| ① 마스크 C | order=신규앱(§0 전부 강제) · catalog=기존앱·런 touched·판정 적재(MQ0=Y·MQ1=Y·MQ2=N)→§1.2 발동·이주로 위치 PASS |
| ② 치명 게이트 | **FAIL 0건** (SD-1~7·FC-1~3·SH-1·2·4·7·NJ-1·2·Q-4 전부 ✅) |
| ②.5 실질성 관문 | 빈 골격 0(전 종류폴더 import 그래프 참여·도메인 메서드 non-trivial) — 통과 |
| ③ 비치명·의미변종 | 의미적 변종 0건 → "준수" 상한 해제 |
| ④ TIER-Q 등급 | **NJ-7(강·catch-all) FAIL 1** → **품질 중**(§2.4: 강 FAIL 시 상한 중) |

**한 줄 요지**: 치명 0·의미변종 0·**NJ-7(강·catch-all) FAIL → 품질 중** → **정적 준수(품질 중)**. B 트랙 핵심(직전 ACL-EX2 보유자가 합성→도메인타입 전환) 라이브 입증.

**2차원 라벨**: **(정적: 준수·품질 중)** × **(라이브: 발화)** — 단 **N=1·단일태스크라 "완료" 선언 금지, "정적 준수"까지**(§4.4).
- `폴더 동작`: **관측** (`.dddjango/20260607-2013-order-creation/`)
- `에러경로 계약`(§4.3.1): **부분** (EP-3=503·EP-2/2b/4=problem+json 정상 / **EP-1 깨진본문만 ninja 기본 `{detail}` JSON 400 — problem+json 미적용**; status {400}는 화이트리스트 통과·치명 아님·freeze)

---

## A. TIER-S 척추 — S-DDD
| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SD-1** 판정 소유 | 핵심 규칙이 도메인 메서드로 | §3.2·§3.1 | `product.py:29-41` `Product.decrease_stock`(`stock<qty` 판정·`stock-=qty` 차감·불변식) · `quantity.py:13-23` `Quantity` 자기검증 · `order.py:37-48` `Order.place` | ➖ | ✅ | ✅ | ✅ |
| **SD-2** 프로덕션 호출 | 조회→도메인→저장 실호출 | §3.2·§3.6 | `decrease_stock_command.py:42-67` find_by_id→`product.decrease_stock`→update_stock_with_version(재시도) · `place_order_command.py:41-53` atomic 내 차감→`Order.place`→save | ➖ | ✅ | ✅ | ✅ |
| **SD-3** 무복제 | 판정 SQL 복제 0 | §3.2 | `product_repository.py:45-51` CAS `filter(id,version=expected).update(stock=product.stock, version=F+1)` — WHERE=version만·`stock__gte=` 등 판정 복제 0 | ✅(anemic-sql exit0) | ✅ | ✅ | ✅ |
| **SD-4** 애그리거트 경계 | 1트랜잭션·ID참조 | §3.3 규칙1~4 | order/catalog 별도 애그리거트·단일 atomic(`place_order_command.py:41`)·catalog 진입점 새 트랜잭션 미개시(참여)·cross-BC scalar `product_id`(도메인 FK 0·DR-37) | ✅(ID참조) | ✅ | ✅ | ✅ |
| **SD-5** 모델 표현력 | 값객체 불변·무상태서비스 | §3.1·§3.5·§2.3 | `quantity.py:13` `@dataclass(frozen=True)` 자기검증 · `Order` bare 도메인 · 유비쿼터스 언어(`StockContentionError`·`InsufficientStockError`) | ✅ | ✅ | ✅ | ✅ |
| **SD-6** 계층 순수성(P1a) | domain HTTP 0·중앙 변환 | §5.1·§6.1; ninja §2.2·§6.2 | domain HTTP import 0 · presentation 단일변환점 `api.py:66-158`(`@api.exception_handler` 7종) · operation 성공 schema만 `api_order.py:56-64` `Status(201,OrderOut)` · 중앙핸들러 발화(EP probe 실측 422/409/503/500 전부 problem) | ✅(error-centralization exit0) | ✅ | ✅ | ✅ |
| **SD-7** 컨텍스트 통신 | OHS/ACL만·직접 import 0 | §3.2(3)·§2.5 | order ACL `infra_layer/acl/product_stock_adapter.py:55-64` catalog 예외 잡아 order 예외 `from` 번역 · `composition.py:13` catalog `published_service.factory`(OHS)만 import · domain은 포트 ABC 의존 · ACL 밖 catalog import 0 | ✅(context-isolation exit0) | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR
| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | 신규 앱 `application/<app>/` | §0-1 | order=`application/order/` · catalog 이주=`application/catalog/`(루트 평면 아님) | ✅(app-container exit0) | ➖ | ✅ | ✅ |
| **SH-2** 4계층 | `*_layer/` 물리분리 | §0-2 | `application/order/{domain,application,infra,presentation}_layer/` 존재 | ✅(layer-skeleton exit0) | ➖ | ✅ | ✅ |
| **SH-3** 종류폴더+거주명명 | R/C/Q 거주명명 | §0-3·§0-4·§4 | `command/PlaceOrderCommand`·`dto/PlaceOrderRequest`(`@dataclass(frozen=True)`)·`query/`(빈 패키지)·종류 2차 폴더 | ✅(폴더) | ✅(명명) | ✅ | — |
| **SH-4** Django앱 위치 | 모델/마이그 `infra_layer/django_<app>/` | §0-5 | `infra_layer/django_order/models/`·`migrations/` · catalog `infra_layer/django_catalog/` · AppConfig `label`(`0002_alter_ordermodel_table`) | ✅(app-container exit0) | ➖ | ✅ | ✅ |
| **SH-5** ORM 명명 | ORM `<Name>Model`·도메인 bare | §0-6·§4 | `OrderModel`/`Order` · `ProductModel`/`Product` 분리 | ✅ | ➖ | ✅ | — |
| **SH-6** 포트/구현 명명 | 추상=개념+역할·일반포트 구현=Adapter | §4 | `ProductStockPort`/`DjangoProductStockAdapter`(일반포트→Adapter) · `OrderRepository`/`DjangoOrderRepository` · `ProductRepository`/`DjangoProductRepository`(패턴명+기술접두) · `Interface`/`Impl`·약어 0 | ✅ | ➖ | ✅ | — |
| **SH-7** 협력 포트 위치 | `domain_layer/<agg>/port/` | §2 | `domain_layer/order/port/product_stock_port.py` | ✅(SH-7 grep) | ➖ | ✅ | ✅ |
| **SH-8** ACL 분리 | `infra_layer/acl/`·repository 미혼합 | §2·§3 | `infra_layer/acl/product_stock_adapter.py` 단독 · `infra_layer/repository/`와 분리 | ✅ | ✅ | ✅ | — |
| **SH-9** 단일 레이아웃 | 두 레이아웃 미공존 | §1.4 | order=`test/`만(`tests/` 부재) · `src`+`apps` 혼용 0 | ✅ | ➖ | ✅ | — |
| **SH-10** 테스트 의미군 | `test/{unit,integration,e2e}`·HTTP=integration | §1.3 | `test/{unit,integration,e2e,factories}/` · HTTP 엔드포인트=`integration/`(test_place_order_api·error_mapping) · 평면 나열 0 | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA (HTTP operation 有 → 채점)
| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | 신규 JSON API=Ninja | §1.1·§10 | `api.py:45` `NinjaAPI` + `api_order.py:30` `Router` + `:33` `@router.post` operation · plain view/DRF 0 | ✅ | ✅ | ✅ | ✅ |
| **NJ-2** operation 얇음 | 비즈/ORM/수동파싱 0 | §1.3·§2.2 | `api_order.py:47-64` `place_order(request, payload: OrderIn)` — schema 바인딩→command.execute→`Status(201,OrderOut)` 매핑만 · `json.loads`·수동검증·ORM·비즈분기 0 · 415=`decorate_view` 데코레이터 | ➖ | ✅ | ✅ | ✅ |
| **NJ-3** Schema 입출력 분리 | 도메인 직접 직렬화 0 | §2.2·§3.1 | `OrderIn`(입력)·`OrderOut`(출력)·`ErrorOut` 분리 · `api_order.py:58-63` `OrderOut(id=order.id,…)` 매핑 | ✅ | ✅ | ✅ | —(강) |
| **NJ-4** status별 response 선언 | `response={}`에 다중 status | §2.2·§8 | `api_order.py:34-42` `response={201,409,415,422,500,503}` 전부 schema 선언 · `openapi_extra` 0 | ✅ | ➖ | ✅ | —(강) |
| **NJ-5** operation 문서화 | summary/tags·유의미 반환 | §2.2 | `api_order.py:43` `summary="주문 생성"`·`:44 description`·`:30 tags=["orders"]`·`-> Status` | ✅ | ➖ | ✅ | —(경미) |
| **NJ-6** ninja 버전 핀 | 매니페스트 핀 | §2.1 | `requirements.txt` `django-ninja==1.6.2`(DR-16 핀) | ✅ | ➖ | ✅ | —(경미) |
| **NJ-7** 오류 변환 완전성(catch-all) | 미식별·비-retryable 단일변환점 완전성 | §6.2(368·469·477) | `api.py:66-158` 7 핸들러 등록·**`@api.exception_handler(Exception)` 최후방 부재**(grep 0) → 미식별 예외(`KeyError`·`ValueError` 등)가 problem+json 단일변환점 우회·Django 기본 500(DEBUG traceback 누출). 단 permanent OpErr는 500 problem 직접 반환(되던지기 0) | ❌(catch-all grep 0) | ❌ | ❌ | —(강) |

> **NJ 노트(과교정 차단)**: `problem.py:43-47`은 `ninja.responses.Response` 아닌 `HttpResponse(content_type="application/problem+json")` 직접 생성 — §6.2가 `Response` 처방이나 problem+json content-type 강제를 위한 실용 선택이고 `django.http.JsonResponse`(RUBRIC 🟡 NJ-1 대상)는 **아니다**. 중앙핸들러 problem 반환 형태라 SD-6 'raw 응답'·NJ-1 'plain leak' over-call 금지(§1.2 양방향 보정). NJ-1 스택 채택 자체 PASS.

## TIER-S(핵심) — FC
| ID | 항목 | Result(조정자 실측) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | EP/정상 probe 실측: Widget(10)·주문1→**201∧차감(10→9)** / Gadget(3)·주문5→**409∧불변** / CAS소진→**503** — 차감 방향·status·부작용 골든 일치(*사전등록 골든표 생략·조정자 사후 실측*) | ➖ | ✅ | ✅ | ✅ |
| **FC-2** 비-vacuous | mutation 3종 주입→`pytest` red 실측: ①`stock-=qty`→`+=` rc=1 red · ②**`stock<qty`→`<=`(stock==qty 경계) rc=1 red** · ③`<`→`>` rc=1 red · red율 **100%** · 복원 68 passed | ✅(주입 실행) | ➖ | ✅ | ✅ |
| **FC-3** 도메인 정합 | 차감 방향 정상·`product.py:35` `stock<qty` 음수재고 차단·주문↔재고 인과 정상(차감 후 생성) | ➖ | ✅ | ✅ | ✅ |

> **FC-2 = DR-36 반전 차원**: ② `<`→`<=`(stock==quantity 경계)를 **Claude는 red 포착** — DR-36서 **Codex**가 바로 이 경계 회귀 테스트 부재로 FC-2 FAIL했던 것과 **반대**(런간 비결정·N=1·우열 아님).

## C. 기존규약 마스크 (§1.1.M MQ 적용)
- **order**: baseline 부재 신규 앱 → **§0 전부 강제**(존중 면제 0). SH-1·2·4·7 강제 적용·전부 PASS.
- **catalog**: baseline 평면 `startapp` 시드 → **MQ0=Y**(baseline `catalog/` git `D` + `application/catalog/` 재생성) · **MQ1=Y**(런 diff에 version CAS·`Product.decrease_stock` 판정 분기 적재) · **MQ2=N**(단순 데이터소스 아님·판정 보유) → **§1.2 발동**(표준 트리 대상). catalog가 `application/catalog/infra_layer/django_catalog/`로 이주(루트 평면 아님) → **SH-1·4 PASS**(위치·깊이 모두 충족). `check-app-container.py` exit0 일치.

## D. TIER-Q 품질
| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| **Q-1** 스코프/G1 | 멱등성·협상·합산 미발명(게이트 미도입 선택)·요청 범위 내·고-blast(낙관 CAS) G1 상정·min1 상한(`schema_in.py:19-20` `le=2147483647`, §2.2) | ➖ | ✅ | ✅ |
| **Q-2** API 계약 | RFC 9457 problem+json 일관(`problem.py`)·status 의미 일관(409/422/503/500)·`Retry-After` 근거 | ➖ | ✅ | ✅ |
| **Q-3** §9.6+테스트 | Risky Write 동시성·소진→503 경로·결정적 CAS 스파이(`test_decrease_stock_command.py` `_FakeProductRepository` update_results=[0,0,0]) | ✅(grep) | ✅ | ✅ |
| **Q-4** 메커니즘 **[🔴치명]** | version CAS·표준 ORM(`F('version')+1`)·커스텀 DB백엔드/PRAGMA/몽키패치 0 | ✅(mechanism-ownership exit0) | ➖ | ✅(치명 통과) |
| **Q-5** 마이그레이션 안전 | catalog 기존 `0001_initial` 불변·`0002_rename`(state)·`0003`(version+check expand) 단계분리 · order `0001`+`0002_alter_table` | ✅ | ✅ | ✅ |
| **Q-6** 테스트/TDD | `pytest` 68 passed·함수형·`@pytest.mark.django_db`·`mocker`·`ProductFactory`(factory_boy)·의미군 분리·pyproject `[tool.pytest.ini_options]`+`DJANGO_SETTINGS_MODULE`(⑬ exit0) | ✅(실행) | ✅ | ✅ |
| **Q-7** 경미 | 공개표면 변수 어노테이션(`schema_in.py:13` `POSITIVE_INT_MAX: int`·⑫ exit0)·주석/docstring 한국어(production 영어 0건 전수)·`django-ninja==1.6.2` 핀 | ✅(public-surface exit0) | ✅ | ✅ |

**TIER-Q 카운트**(Q-1·2·3·5·6·7 + NJ-3·4·7): **NJ-7 FAIL 1(강·catch-all)** → **품질 중**(§2.4: 강 FAIL 시 상한 중).

---

## 의미적 변종 / backstop-blind 메타 (§1.3 — 측정의 주 산출물)
- **의미적 변종 0건**: `[결정 PASS ∧ 의미 FAIL]` 칸 없음. 치명 항목 전부 결정·의미 일치.
- **backstop-blind 카드**:
  - **⑮ check-synthetic-infra-exc**: from-less 인프라예외 *합성*만 본다 — 도메인 타입 raise(catalog `StockContentionError`)는 정상 통과(정확). 클린 exit0 + proxy 주입(`acl/`에 from-less `raise OperationalError`) → **exit2 차단** 실측(DR-30식 양방향 배선 확정).
  - **check-error-centralization**: `application_layer` HTTP 누수만 본다 — **presentation catch-all 완전성은 못 봄**. ⇒ EP-1(깨진 본문)이 ninja 기본 `{detail}` JSON 400으로 problem+json 단일변환점 우회 + catch-all `@api.exception_handler(Exception)` 부재는 **어느 백스톱도 미포착**, §4.3.1 관측 트랙서만 '부분'으로 포착. **Codex 후속 후보 #1(형식 완전성)과 같은 class — 양 런타임 공통 = 표준 빈틈**(치명 아님·후속).
  - 전 백스톱 15종 fixture 일괄 exit0(⑪⑫⑬⑭⑮ 포함).

## 에러 경로 라이브 관측 (§4.3.1 — 별도 트랙·완료 비산입·치명 아님)
> 조정자 직접 probe(자기보고 불신)·어댑터 ⓑ = `POST /api/orders` + 본문. EP-3 = CAS 소진 유도(type ii: catalog 도메인 `StockContentionError` 번역 경로·raw 종단 없음). 계약 속성표(ⓐ)·status 화이트리스트 정본 = `EVAL-METHOD.md §4.3.1`.

| 키 | 관측 status | content-type | 화이트리스트 | 판정 |
|---|---|---|---|---|
| EP-1 깨진 본문 | **400** | ninja 기본 `{detail}` JSON | {400} | 🟡 부분(problem+json 미적용·status는 통과) |
| EP-2 무효 입력(qty=0·2b 변종) | **422** | application/problem+json | {422,400} | ✅ 관측 |
| EP-4 재고 부족 | **409** | application/problem+json | {409} | ✅ 관측 |
| EP-3 transient 소진(type ii) | **503** | application/problem+json | {503,409} | ✅ 관측(직전 ACL-EX2 보유자 전환 입증) |
| 정적 대응물(거대 식별자 상한) | `le=2147483647` 선언(`schema_in.py:19-20`) | — | (정적 관측) | ✅ |

- **EP-3=503 = ACL-EX2 수복 라이브 입증**: 직전 maj1live서 합성 `OperationalError`→500이던 흠을, catalog가 소진→도메인 타입 `StockContentionError` raise·ACL `from` 번역·presentation 503 매핑으로 전환(합성 0). 계약("소진→retryable, 절대 500 아님") 충족.
- **EP-1 '부분'**: 깨진 본문이 ninja 기본 `{detail}` JSON 400으로 problem+json 단일변환점 우회(status {400}는 화이트리스트 통과·**치명 아님**·형식 완전성은 RUBRIC 차원 밖 후속 후보). EP-2·4·content-type 충족.

## 조정자 노트 (결론만)
- **B 트랙 핵심 검증 = 성공**: 직전 maj1live ACL-EX2 보유자(Claude:82 — CAS 소진을 합성 `OperationalError` `from` 없이 신호→500)가 **전 계층 도메인 타입으로 전환**. catalog `DecreaseStockCommand`(소진→`raise StockContentionError` 도메인타입·합성 0)·catalog 예외 docstring에 B 트랙 근본축("드라이버가 던진 인프라 예외의 합성이 아니다") 안착·ACL `from` 번역·presentation 타입매핑·**EP-3=503 실측**·⑮ proxy 발화. **흠을 가졌던 인스턴스가 안 가짐 = 가장 강한 예방 증거**.
- **EP-1 problem+json 미적용**(에러경로 '부분')은 §4.3.1상 **치명 아님**(status {400} 화이트리스트 통과·관측 트랙·freeze). 내 1차 서술형 채점에서 이를 "흠/major"로 과대평가했던 것을 정식 형식서 정정 — 정식 차원(SD-6/NJ)으론 PASS이고, 형식 완전성은 RUBRIC 차원 밖 후속 후보다.
- **FC-2는 실측 필수였다**(치명·DR-34/36 런간 반전 차원): 1차 채점이 mutation 미주입 PASS였던 것을 정식서 mutation 3종 실측으로 교체 → red율 100% 확정.
- **N=1·P4③**: Codex(대조군·원래 대안 B)와의 차이(pytest 채택·docstring 한국어·FC-2 경계 포착)는 런타임 경향이 아니라 인스턴스 선택일 수 있음. 우열·완료 결론 금지.

## 부록 — vs Codex aclex2live 대조 (N=1·우열 아님)
| 차원 | Claude | Codex |
|---|---|---|
| 종합 | 정적 준수·품질 상 | 정적 PASS·품질 상 |
| ACL-EX2 | 부재(**직전 보유자 전환 입증**) | 부재(대조군·대안 B) |
| EP-3 | 503 실측 | 503 실측 |
| FC-2 경계 | stock==qty red 포착 ✅ | (maj1live FC-2 경계 갭) |
| Q-6 pytest | 채택 ✅ | 미채택(manage.py test) |
| Q-7 docstring | 한국어 0 영어 ✅ | 영어 1건(nit) |
| 형식 완전성 | 갭(EP-1·catch-all) | 갭(permanent re-raise·catch-all) |

**후속 후보**: ① catch-all/형식 완전성(양 런타임 공통·표준 빈틈) · ② DR-42 집행(Codex만 pytest 미채택·N=1). → 사용자와 처방 여부 결정 대기.
