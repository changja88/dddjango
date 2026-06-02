# smoke6-claude 채점 결과지

> **방법**: `EVAL-METHOD.md` v3 — 결정 레인(백스톱 6종 직접 실행 + grep) ∥ 의미 레인(코드 직독·줄 인용) + 표준 직접 대조. 사전식 집계.
> **채점일**: 2026-06-02. **픽스처**: `~/Desktop/dddjango-smoke6-claude`. **태스크**: 주문 생성 API(별도 order, catalog 재고 차감, 재고부족 409).
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK · ⏸️ 보류 · ➖ 해당 레인 없음(N/A).

> 🟢 **버전 검증 — Claude 런은 1.0.2 최신(6종)을 실제로 썼다 (Codex와 정반대).**
> `changja88` 마켓플레이스 = `directory` 소스, **installLocation = 레포 자체**(`/Users/hyun/Desktop/dddjango`). → Claude Code가 레포의 `commands/`(6종)·`scripts/`(6개)를 **직접 로드**. 캐시(`~/.claude/.../1.0.0`, 3종)는 잔재이고 실행에 안 쓰임. G2 배너 "백스톱 6종 전부 exit0"이 이를 확증(6개 스크립트 실존 = 레포). → **이번 세션 NJ-4·SD-7 하드닝 + 생산자 예방이 Claude 런에서 실제 적용·라이브 검증됨**(6종 라이브 통과, content_negotiation 같은 이탈 0). 조정자도 레포 6종을 fixture에 직접 실행 → 전부 exit 0.
> ⚠️ 대조: **Codex 런은 캐시 복사본(1.0.1, 4종) stale** — 같은 directory 소스인데 Codex 런타임은 캐시로 복사해 갱신 실패. `EVAL-smoke6-codex.md` 참조.

## 종합 — 🔴 **FAIL (치명 SH-1·SH-4 = catalog 컨테이너 §0-1 위반 — Codex와 공유)**
catalog가 `application/` 밖 루트 평면(`catalog/`)에 방치 → 파일트리 §0-1("앱은 `application/<app>/` 아래") 위반. **이 위반은 두 런 공통**(Claude도 예외 아님 — 이전 'clean PASS'는 §632-(2)를 *위치 면제*로 오독한 채점 오류, 정정함). §632-(2)는 데이터소스의 **4계층 전개**만 면제하지 **위치**는 면제 안 함. **단 Codex의 추가 결함 3종(catalog에 판정 적재=§632-1 가중 · content_negotiation 미들웨어 · 비결정 동시성 테스트)은 Claude가 회피** — catalog-위치는 동률 FAIL, 나머지 결함은 Codex 가중(아래 대조표).

**Codex(smoke6) 대비 — 같은 태스크, 갈린 지점:**
| 축 | **Claude** | Codex |
|---|---|---|
| **SH-1/4 catalog 컨테이너(§0-1)** | ❌ **FAIL**(catalog 루트 방치=위치 위반. 단 판정-누출 없음=순수 데이터소스) | ❌ FAIL(catalog 루트 방치 **+ 판정까지 적재**=§632-1 가중) |
| **content_negotiation 미들웨어** | ✅ **없음**(415/406 ninja 위임) | ❌ 전역 Django 미들웨어 자작 |
| **Q-3 동시성 결정성** | ✅ **결정적 CAS-스파이** | ❌ ThreadPool 실스레드 레이스(CF-7) |
| **C1 약속 테스트** | ✅ **실재**(`test_create_order_concurrency.py`) | 🟡 부재(완화형) |
| **SD-6 중앙 변환** | ✅ `api.create_response`(ninja 경계) | 🟡 `JsonResponse`(경미 일탈) |
| 판정 소유(B1) | ordering 도메인 서비스 | catalog OHS |
| NJ-4·SD-7 | ✅ 청정 | ✅ 청정 |

> ⚠️ **N=1·태스크 단일·B1 설계 분기 — "Claude>Codex" 정량 결론 아님**(DR-14·DR-24 준수). 이번 런 한정 관측이다. 단 Codex의 결함 4종(미들웨어·미이주·비결정테스트·약속테스트부재)을 Claude가 모두 회피한 건 plan(`shiny-petting-lovelace.md`) 가설 — *말랑한 구조·메커니즘 빈칸에서 Codex 이탈*을 뒷받침하는 데이터.

## A. TIER-S 척추 — DDD 도메인 충실도 (S-DDD)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SD-1** 빈혈: 판정 소유 | 핵심 규칙·불변식이 도메인 메서드로 | §3.2·§3.1 | **재고 가용성 판정 = `StockAvailabilityChecker`(ordering `domain_layer/domain_service/`)** `stock_availability_checker.py:24` `if quantity > available_stock: raise`; 주문 불변식 = `Order`/`OrderLine` | ➖ | ✅ | ✅ (non-contested — Codex flat published_service와 달리 진짜 domain_layer) | 치명 |
| **SD-2** 빈혈: 프로덕션 호출 | 응용이 조회→도메인메서드→저장 실호출 | §3.2·§3.6 | `create_order_app.py:91-99` read→`check_availability` 실호출→차감→save(죽은코드 아님) | ➖ | ✅ | ✅ | 치명 |
| **SD-3** 빈혈: 무복제 | 판정이 인프라 SQL/ORM에 복제 안 됨 | §3.2 | ACL `decrease`는 `WHERE id=,stock=expected` CAS만 `product_stock_acl.py:45-47`; 판정 SQL 복제 0(`stock__gte` 없음). 명시 주석 `:6-8` | ✅ | ✅ | ✅ | 치명 |
| **SD-4** 애그리거트 경계 | 1트랜잭션 1애그리거트·ID 참조 | §3.3 | `Order`(루트)+`OrderLine`(VO), catalog를 `product_id` ID 참조·도메인 FK 0 | ➖ | ✅ | ✅ | 치명 |
| **SD-5** 모델 표현력 | frozen VO·무상태 서비스·유비쿼터스 명명 | §3.1·§3.5·§2.3 | `OrderLine` 값객체·`StockAvailabilityChecker` 무상태(`:13` 필드 없음)·도메인 네이밍 | ➖ | ✅ | ✅ | 치명 |
| **SD-6** 계층 순수성(P1a) | domain HTTP/ORM 0; status 변환 presentation 단일점 | §5.1·§6.1; ninja §2.2·§6.2 | operation `return 201, OrderOut(...)` schema만 `api_order.py:109`; 응용 예외 그대로 raise(`create_order_app.py:132` HTTP 무지); 중앙 `common/ninja/problem.py`가 `api.create_response`로 변환(`:45`) | ✅ | ✅ | ✅ | 치명 |
| **SD-7** 컨텍스트 통신 | 타 BC는 OHS/ACL로만; 결합 ACL 격리 | §3.2(3)·§2.5 | catalog 결합이 ACL `product_stock_acl.py` 한 곳; `Product.DoesNotExist`→`ProductNotFound` 번역 `:35-36`(ACL 격리); presentation·application catalog import 0 | ✅ | ✅ | ✅ | 치명 |

## B. TIER-S 척추 — houserules 충실도 (S-HR)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | 신규/이주앱이 `application/<app>/` | §0-1 | 신규 `ordering`은 `application/ordering/` ✅. **그러나 catalog가 루트 평면(`catalog/`) 방치 — §0-1 "앱은 `application/<app>/` 아래" 위반.** §632-(2)는 4계층 전개만 면제, 위치는 면제 안 함(데이터소스여도 `application/catalog/`이어야). 판정-누출은 없음(Codex와 차이) | ❌ | ➖ | ❌(catalog 위치 위반·Codex와 공유) | 치명 |
| **SH-2** 4계층 | 4계층 물리 분리 | §0-2 | `domain/application/infra/presentation_layer` 완비 | ✅ | ➖ | ✅ | 치명 |
| **SH-3** 종류 폴더 | 종류 2차 폴더 | §0-3·§0-4 | `entity/event/port/repository/specification/value_object/domain_service` + `published_service/` 빈 패키지까지 §0 불변식 충실 | ✅ | ➖ | ✅ | — |
| **SH-4** Django앱 위치 | `models.py`가 `infra_layer/django_<app>/` | §0-5 | `ordering`은 `infra_layer/django_ordering/models/order_model.py` ✅. **그러나 catalog `models.py`가 루트(`catalog/models.py`) — §0-1/§0-5 위반**(데이터소스여도 `application/catalog/infra_layer/django_catalog/`이어야; §632-(2)는 위치 면제 아님) | ❌ | ➖ | ❌(Codex와 공유) | 치명 |
| **SH-5** ORM 명명 | ORM `<Name>Model`, 도메인 bare | §0-6·§4 | ORM `OrderModel`/`OrderLineModel`·도메인 `Order`/`OrderLine` bare | ✅ | ➖ | ✅ | — |
| **SH-6** 포트/구현 명명 | `Interface`/`Impl`·약어 0 | §4 | `ProductStockPort`/`DjangoProductStockPort`·`OrderRepository`/`DjangoOrderRepository`·약어 0 | ✅ | ➖ | ✅ | — |
| **SH-7** 협력 포트 위치 | port가 `domain_layer/<agg>/port/` | §2 | `domain_layer/order/port/product_stock_port.py` | ✅ | ➖ | ✅ | 치명 |
| **SH-8** ACL 분리 | ACL이 `infra_layer/acl/` | §2·§3 | `infra_layer/acl/product_stock_acl.py` 분리·repository 미혼합 | ✅ | ✅ | ✅ | — |
| **SH-9** 단일 레이아웃 | 한 앱 두 레이아웃 금지 | §1.4 | `ordering`은 `test/` 단일. catalog는 `tests.py`만(test/ 미생성)→ catalog도 단일. 두 레이아웃 공존 없음 | ✅ | ➖ | ✅ | — |
| **SH-10** 테스트 의미군 | `test/{unit,integration,e2e}` 분리 | §1.3 | `test/{unit,integration,e2e}` 분리·HTTP=integration·동시성 별도 파일 | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — django-ninja 충실도 (S-NINJA)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명(조건부) |
|---|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | 신규 JSON API를 Ninja로 | §1.1·§10 | `NinjaAPI`+`Router`(`ordering_api_router.py`); plain view·DRF·**미들웨어 협상 0** | ✅ | ➖ | ✅ | 치명 |
| **NJ-2** operation 얇음 | 비즈로직·ORM·수동파싱 0 | §1.3·§2.2 | operation은 Schema→Command 변환+app 호출+201 매핑만 `api_order.py:97-115`; DI 조립은 `_build_create_order_app` helper | ➖ | ✅ | ✅ | 치명 |
| **NJ-3** Schema 입출력 분리 | 요청·응답 Schema 분리 | §2.2·§3.1 | `schema_in`/`schema_out`/`error_out`(status별 problem 스키마 분리 §3.4-1)·도메인 직접직렬화 0 | ✅ | ✅ | ✅ | —(강) |
| **NJ-4** status별 response 선언 | 모든 status `response={}` 선언(§2.2 line111) | §2.2·§8 | **`response={201, 422, 409}` 선언** `api_order.py:59-63`; `openapi_extra`는 **201 Location 헤더 문서화에만**(`:70-85`)·오류 선언 아님 → openapi_extra 우회 0 | ✅ | ➖ | ✅ | —(강) |
| **NJ-5** operation 문서화 | summary/tags·반환타입 | §2.2 | `summary`·`description`·`tags=["orders"]`·반환타입 `tuple[int, OrderOut]` `api_order.py:57-89` | ✅ | ➖ | ✅ | —(경미) |
| **NJ-6** ninja 버전 핀 | 매니페스트 버전 핀 | §2.1 | `django-ninja==1.6.2` `requirements.txt` | ✅ | ➖ | ✅ | —(경미) |

> **415/406 처리(미들웨어 없음)**: Claude는 설계 §3.4대로 415/406을 ninja 기본 동작에 위임 — 별도 미들웨어·오버라이드 0. **Context7 공식문서상 ninja가 `HttpError`/`exception_handler`/`Parser`로 415/406을 직접 제공**하므로 위임/직접처리 모두 ninja 경계 안. Codex의 전역 Django 미들웨어(`OrderApiContentNegotiationMiddleware`) 같은 이탈 없음.

## TIER-S(핵심) — 기능 정확성 (FC)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | 동시성: 재고10·주문4→CAS충돌주입→수렴·stock6·oversell0 `test_concurrency.py:81-94`; 원자성: 다중라인 한라인부족→409·전라인 불변·주문0 `:100-116`. 인수 계약(201/409/422)은 배너 40 green + design-spec §6 골든. | ➖ | ✅ | ✅(동시성·롤백 직독; 인수는 배너 기반) | 치명 |
| **FC-2** 테스트 비-vacuous | mutation 3종 미실행(프리즈 트랙) | ⏸️ | ➖ | ⏸️ 보류 | 치명 |
| **FC-3** 도메인 정합 | 차감 `F("stock") - qty` 정상 `product_stock_acl.py:47`·`stock>=0` CHECK(catalog 0002)·인과 정상 | ➖ | ✅ | ✅ | 치명 |

## C. 기존규약 마스크 (S-HR 판정 조건) — **정정됨**
- `catalog` = **기존 앱**. 런 diff: `catalog/models.py`에 `stock>=0` CHECK 1건(`0002_add_stock_check` AddConstraint) — **version 컬럼 0·판정 메서드 0·published_service 0**. 가용성 *판정*(stock<qty)은 **ordering 도메인 서비스**가 소유 → catalog는 **순수 데이터소스**(필드+음수금지 CHECK만).
- **MQ1**(catalog에 판정 적재?)=**N** ∧ **MQ2**(단순 데이터소스?)=**Y** → §632-(2) 발동 = **4계층 DDD 전개는 면제**(catalog를 애그리거트로 안 만들어도 됨). **그러나 §632-(2)는 *위치*를 면제하지 않는다** — 파일트리 §0-1 "앱은 `application/<app>/` 아래"는 데이터소스에도 적용. catalog는 `application/catalog/`(flat: `infra_layer/django_catalog/models.py`)에 있어야 하나 **루트에 방치 = §0-1 위반**.
- ↔ **Codex 대조(위치는 동률, 판정은 가중)**: catalog 루트 방치는 **두 런 공통 위반**. Codex는 거기에 더해 가용성 판정을 catalog `published_service`에 적재(MQ1=Y) → §632-(1) "판정 소유=도메인 컨텍스트=이주" 가중. **즉 catalog-위치는 둘 다 FAIL, Codex는 판정-소유로 가중.** (이전 초안의 "Claude clean PASS"는 §632-(2)를 위치 면제로 오독한 채점 오류 — 정정.)

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| **Q-1** 스코프/과설계·G1 | 발명 0·고-blast G1 상정 | ddd §6.8·houserules §6.1 | 멱등성·라인스냅샷을 **G1 옵션으로 표면화**(빌드 안 함)·이벤트 미도입·**미들웨어 0**·단일트랜잭션. 요청 외 발명 0, 과설계 0 | ➖ | ✅ | ✅ |
| **Q-2** API 계약 | RFC9457·버전 일관 | architecture-api §4~14 | RFC9457 problem+json·status별 스키마 분리·미존재상품 422(unknown-product, API B1)·버전 정책 명시 | ➖ | ✅ | ✅ |
| **Q-3** §9.6 동시성 | 결정적 CAS·소진→409 | architecture-db §9.6·impl-test §20.5 | 8행 블록 + **결정적 CAS-스파이**(`_ConflictOnceStockPort` expected_stock+1로 진짜 0행 유발 `test_concurrency.py:47-58`)→재조회·재판정·재차감 수렴. ThreadPool 0. **CF-7 회피** | ✅ | ✅ | ✅ |
| **Q-4** 메커니즘 소유권 **[🔴치명]** | 커스텀 백엔드/PRAGMA/몽키패치 0 | architecture-db §9.5·§16.4 | `F()`/`filter().update()` CAS·`transaction.atomic()`만; 커스텀 백엔드/PRAGMA/몽키패치 0 | ✅ | ➖ | ✅ |
| **Q-5** 마이그레이션 안전 | 0001 불변·expand | architecture-db §11 | catalog `0001` 불변 + `0002_add_stock_check`(AddConstraint stock>=0 expand)·신규앱 `ordering` 0001 | ✅ | ✅ | ✅ |
| **Q-6** 테스트/TDD | 그린·행위 덮음 | impl-test·discipline-tdd | **40 green**(단위25+통합15[인수8+화이트박스7])·의미군 분리·**약속 동시성 테스트 실재**(C1 없음)·`check` 0 issues | ✅ | ✅ | ✅ |
| **Q-7** 경미 | 경미 흠 | houserules §5·§6.2 | `catalog/tests.py` startapp 스텁 잔존(미삭제)·일부 빈 종류폴더(설계상 의도). nit 2건(경합신호 분리·테스트 `-> None`)은 reviewer 불요 판단 | ➖ | 🟡 | 🟡(경미) |

---

## 조정자 노트

- **🟢 1.0.2 라이브 검증(Claude 한정)**: 헤더 참조. Claude는 directory-소스 레포 직접 로드라 **이번 세션 하드닝(6종 백스톱+생산자 예방)이 실제 런타임에 적용**됐고 6종 라이브 통과. **새 백스톱 2종(NJ-4·SD-7)은 발화하지 않았다 — 위반이 없었으니(생산자 예방이 작동해 위반을 안 만듦)**. 즉 "라이브 작동(실행)"은 검증, "라이브 발화(blocker)"는 위반 부재로 미관측. catch 실효의 직접 증거는 아니나, 배선·실행은 확정.

- **B1 설계 분기 = 판정-누출 여부의 분수령(핵심·정정)**: Claude는 재고 가용성 판정을 **ordering 도메인 서비스**(길 A)에 뒀다 → catalog는 순수 데이터소스(판정-누출 없음). Codex는 판정을 **catalog published_service**에 적재 → catalog가 판정 소유(§632-1 가중 위반). **그러나 catalog가 루트 평면에 있는 것(§0-1 위치 위반)은 두 B1 선택과 무관하게 양쪽 공통 FAIL** — B1 분기는 *판정-누출*(Codex 가중)을 가르지, *catalog 위치*(둘 다 위반)를 면제하지 않는다. Claude가 더 안전한 건 판정-누출을 피했기 때문이지 catalog 위치를 맞춰서가 아니다(둘 다 틀림).

- **사용자 "catalog 미이관" 피드백 = 옳았음(채점 정정)**: 사용자가 Codex catalog를 FAIL로 판정했고, 같은 잣대로 **Claude catalog도 루트 방치 = §0-1 위반 = FAIL**이 맞다(이전 초안이 §632-(2)를 위치 면제로 오독 → clean PASS로 잘못 줌, 정정). §632-(2)는 데이터소스의 **4계층 전개**만 면제하고 **위치**(`application/<app>/` 아래)는 면제하지 않는다 — 파일트리 §0-1이 1순위. catalog는 데이터소스여도 `application/catalog/`(flat)에 있어야 한다. → **두 런 모두 catalog-컨테이너 FAIL**, Codex는 판정-소유로 가중. **잔존 표준 모호성**: §632-(2)가 "평면 유지"의 *위치*를 명시하지 않아 이 오독이 발생 → §632-(2)에 "위치는 `application/<app>/` 유지, 면제는 4계층 전개에 한정" 명문화 필요(처방 후보).

- **content_negotiation 미들웨어 부재(Codex 대조)**: Claude는 415/406을 ninja에 위임, 전역 미들웨어 0. Context7 공식문서로 ninja의 415/406 직접 처리(HttpError/exception_handler/Parser)가 확인됐으므로 위임·직접처리 모두 정당. Codex의 전역 Django 미들웨어 자작이 *유일한* 이탈이었고 Claude엔 없음.

- **`problem()` 헬퍼 정당성(사용자 큐 검증 — 표준 직접 대조)**: `common/ninja/problem.py`의 `problem()`은 Claude 발명/과설계가 아니라 **ninja 스킬 §6.2가 정규 예시로 처방한 중앙 변환 헬퍼**(`implementation-django-ninja/references/final.md:353-357`이 동일한 `problem()` 함수를 그대로 제시). **역할**: 모든 오류를 RFC 9457 problem+json 본문 + `application/problem+json` content-type으로 **단일 지점**에서 변환 → SD-6(변환 중앙화)을 실재하게 만드는 load-bearing 메커니즘. 제거하면 5개 핸들러가 본문·content-type을 반복 → 스킬 §1.3(`:113`)이 경고한 "변환 흩어지고 problem+json content-type 불일치" 회귀. 선언된 `*ProblemOut` 스키마(계약·OpenAPI)와 런타임 dict의 2중 표현은 **스킬 §6.2가 명시 수용한 한계**(`:388-396` "OpenAPI error media-type가 application/json으로 표기되는 것은 수용된 한계 — 사후 변형하지 않는다"). 유일한 구현 뉘앙스: content-type을 `api.create_response` 후 사후 설정(스킬의 두 정규형 중 "대안 B" 경계 안). → **불필요/이상 아님 = 표준 처방. 별도 ding 없음.** 단 사용자가 *2중 표현 자체*를 싫어하면 §6.2를 "스키마 단일소스(핸들러가 선언 스키마 인스턴스 return)"로 바꾸는 **표준 변경 사안**(현 §6.2는 의도적으로 dict 헬퍼 + 수용 한계를 채택).

- **Q-3 결정성(Codex 대조)**: Claude `_ConflictOnceStockPort`는 expected_stock을 일부러 어긋내 **진짜 stock-CAS 0행을 결정적으로 유발**(몽키패치 아님, 낡은 값 흘리기) → 스케줄러 무관 수렴 검증. Codex `ThreadPoolExecutor` 실스레드 레이스(비결정·flaky, CF-7)와 정반대. 표준 impl-test §20.5 "결정적 CAS 스파이" 처방의 모범.

- **미세 미관측(정직)**: 인수 `test_create_order_api.py`·`order.py`/`order_line.py`/`error_out.py` 본문은 직독 안 함(design-spec §·배너 40green·구조·동시성/롤백 직독으로 채점). FC-1 인수 계약은 배너·design-spec 골든 기반(동시성·롤백은 직독). 필요 시 추가 정독 가능.

- **N=1·태스크 단일·B1 분기**: 우열·결정성 결론 아님(DR-14·DR-24). 이번 런 한정으로 Claude가 더 깨끗하나, 일반화 금지.
