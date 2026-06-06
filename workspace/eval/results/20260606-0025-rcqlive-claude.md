# 채점 결과지 — rcqlive · Claude · 2026-06-05

> **방법** = `EVAL-METHOD.md` v3 · **채점일** 2026-06-06 00:25 (런: 2026-06-05)
> **픽스처** `~/Desktop/dddjango-rcqlive-claude` (기존규약: baseline = plain Django + 루트 `catalog` startapp 스텁; greenfield venv Django-only)
> **런타임** Claude Code (Opus) · **N=1** · plugin **1.4.0**(캐시=레포 HEAD IDENTICAL)
> **태스크** 주문 생성 API(상품·수량 → 주문, catalog 재고 차감, 부족 409) — Codex와 동일 입력
> **게이트(고정)** BC=미강제(설계자결정·order 분리)·렌즈 ddd+db+api·API/러너 "표준 기본대로"·G1·G2 무수정 승인·thinking OFF
> **검증 타깃** DR-37 BC FK 금지 · DR-43 R/C/Q 응용 명명 · DR-41 네이밍 · DR-40 산출폴더
> **범례** ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ⏸️ 보류 · ➖ N/A
> **⚠️ 단서**:
> - **N_grader=1** — 조정자 1차 채점(blind N≥3 프로토콜 아님).
> - **자기보고 불신 적용** — 코디 G2 요약 대신 fixture 직접 정독 + 백스톱 13종 직접 실행(모두 exit0) + pytest 34 passed 실행 검증 + Q-5 0001 baseline 대조 + FC-2 mutation 실측(차감부호 역전→8 red→복원).
> - **정적 트랙** — 정상 런 채점(위반주입 라이브 발화 트랙 아님).
> - **N=1 우열 결론 금지** — Codex 결과지(`20260605-1441-rcqlive-codex.md`)와 *대조*하되 동일태스크 A/B(N≥3) 아님. DR-36 런타임 반전 전례.

---

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | order=**신규 앱**(§0 강제) · catalog=**touched·삭제후재생성**(루트 `catalog/` 7파일 삭제 + application/catalog 재생성)·MQ0=Y·MQ1=Y(`deduct_stock` 판정)·MQ2=N → **§1.2**: application/catalog로 이주 |
| ② 치명 게이트 | SD-1~7 ✅ · FC-1~3 ✅ · SH-1·2·4·7 ✅ · NJ-1·2 ✅ · Q-4 ✅ → **치명 FAIL 0건 · 통과** |
| ②.5 실질성 관문 | 도메인 메서드 non-trivial(`Product.deduct_stock`) · 테스트 non-vacuous(mutation→8 red 실측) · 빈 골격 치명산출 0 → **PASS** |
| ③ 비치명 의미변종 | **0건** — SH-9 ✅(루트 삭제)·Q-6 ✅(pytest)·전 비치명 FAIL 0 → **"준수" 라벨 자격** |
| ④ TIER-Q 등급 | WEAK 0 · FAIL 0 → **품질 上**(WEAK≤2 ∧ FAIL 0) |

**한 줄 요지**: **치명 0 FAIL + 비치명 FAIL 0** — DR-37·43·41 실현 + **Q-5 마이그레이션 모범(0001 byte-불변·0002 state-only)** · **Q-6 pytest 부트스트랩** · **SH-9 루트 삭제 깨끗한 이주** · 협상 미발명(406 없음·415만 DR-35 처방 레시피). 유일 미세 흠 = StockConflictError(CAS 소진) HTTP 미매핑(→500, 비치명·드문 경로).

**2차원 라벨**: **(정적: 준수) × (라이브: 미검증)** — "완료" 아님(§4.4 N=1·단일태스크).

---

## A. TIER-S 척추 — DDD 도메인 충실도 (S-DDD)

| ID | 항목 | §근거 | Result (조정자 검증·줄인용) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SD-1** 판정 소유 | §3.2·3.1 | `product.py:22-29` `Product.deduct_stock`(stock<qty→`InsufficientStockError`·else 차감); 수량 불변식은 `Order.create` 소유 | ➖ | ✅ | ✅ | ✅ |
| **SD-2** 프로덕션 호출 | §3.2·3.6 | `deduct_stock_command.py:35-43` get→`product.deduct_stock`→`save_with_version_guard`(CAS 3회 재시도). 경로 order PlaceOrder→port→ACL→DeductStock→domain | ➖ | ✅ | ✅ | ✅ |
| **SD-3** 무복제 | §3.2 | `product_repository.py:24-30` `.filter(pk,version=expected).update(stock,version=+1)` = **version CAS만**, `stock__gte` 없음. ⑪ exit0 | ✅ | ✅ | ✅ | ✅ |
| **SD-4** 애그리거트 경계 | §3.3 | `order_model.py:12` scalar `product_id`; `place_order_command.py:40` 단일 atomic owner, `deduct_stock_command.py:33` 자체 atomic 미개시(owner 합류) | ✅ | ✅ | ✅ | ✅ |
| **SD-5** 모델 표현력 | §3.1·3.5 | `Product` 엔티티(가변 stock 정당); `version`=인프라 토큰 명시(`product.py:14`); `Order.create` 팩토리+불변식; 도메인 용어 | ➖ | ✅ | ✅ | ✅ |
| **SD-6** 계층 순수성(P1a) | §5.1·6.1 | domain import=dataclass/exception만; operation 성공 schema만(`api_order.py:72`); 오류→status 중앙 `@api.exception_handler`(`:78-121`); 컴포지션루트 module-level(operation 본문 직접생성 0). ⑤ exit0 | ✅ | ✅ | ✅ | ✅ |
| **SD-7** 컨텍스트 통신 | §3.2(3)·2.5 | order→catalog는 **ACL**(`product_stock_adapter.py`)이 catalog command/예외/repo 통합·번역을 격리; order app/presentation은 **order 포트 예외만** import(`api_order.py:23-26`). catalog OHS 미노출이나 단일트랜잭션 ACL-직접 = §2 허용. ⑥ exit0(1회 발화→수정) | ✅ | ✅ | ✅ | ✅ |

**S-DDD = 7/7 치명 통과.**

## B. TIER-S 척추 — houserules 충실도 (S-HR)

| ID | 항목 | §근거 | Result (줄인용) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | §0-1 | 등록 앱 `application.catalog…django_catalog`·`application.order…django_order` application/ 하위. ⑦ exit0 | ✅ | ➖ | ✅ | ✅ |
| **SH-2** 4계층 | §0-2 | order·catalog 모두 4 `_layer/` | ✅ | ➖ | ✅ | ✅ |
| **SH-3** 종류폴더+거주명명 | §0-3·4 | **DR-43 일치**: `PlaceOrderCommand.execute(request)`(`place_order_command.py:35`)·`@dataclass PlaceOrderRequest`·catalog `DeductStockCommand`/`DeductStockRequest`. query/ 빈(읽기 없음). **빈 service/handler 없음**(Codex보다 정갈)·`adapter/`(DR-41 service→adapter) | ✅ | ✅ | ✅ | — |
| **SH-4** Django앱 위치 | §0-5 | `…/django_catalog/models/`·`…/django_order/models/`; label "catalog"/"order" 보존(마이그 dep·get_model 작동) | ✅ | ➖ | ✅ | ✅ |
| **SH-5** ORM 명명 | §0-6·4 | `ProductModel`·`OrderModel` ↔ bare `Product`·`Order` | ✅ | ➖ | ✅ | — |
| **SH-6** 포트/구현 명명 | §4 | **DR-41 일치**: `ProductStockPort`↔`DjangoProductStockAdapter`·`ProductRepository`↔`DjangoProductRepository`·`OrderRepository`↔`DjangoOrderRepository`. Interface/Impl/_repo 0 | ✅ | ➖ | ✅ | — |
| **SH-7** 협력포트 위치 | §2 | `order/domain_layer/order/port/product_stock_port.py` | ✅ | ➖ | ✅ | ✅ |
| **SH-8** ACL 분리 | §2·3 | `order/infra_layer/acl/product_stock_adapter.py`·repository 분리 | ✅ | ✅ | ✅ | — |
| **SH-9** 단일 레이아웃 | §1.4 | ✅ **PASS** — 루트 `catalog/` **완전 삭제**(git diff: `__init__`·`admin`·`apps`·`models`·`tests`·`views`·`migrations/0001` 전부 deletion). 이중 레이아웃 0(Codex와 반대) | ✅ | ➖ | ✅ | — |
| **SH-10** 테스트 의미군 | §1.3 | `test/{unit,integration,e2e}` + `factories/` 분리; HTTP=integration; 평면나열 0 | ✅ | ✅ | ✅ | — |

**S-HR = 전 항목 PASS** (SH-9 깨끗).

## TIER-S(조건부) — django-ninja 충실도 (S-NINJA)

| ID | 항목 | §근거 | Result (줄인용) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | §1.1·10 | ✅ 모듈레벨 `NinjaAPI`+`@api.post`(`api_order.py:41,56`); 오류 헬퍼 `problem()`가 **`ninja.responses.Response` 반환**(`problem.py:30`) = §6.2 처방 정합(JsonResponse 경미 없음 — Codex와 대비) | ✅ | ✅ | ✅ | ✅ |
| **NJ-2** operation 얇음 | §1.3·2.2 | operation `create_order`(`api_order.py:63-75`) = OrderIn→PlaceOrderRequest→`execute`→`Status(201)` 매핑만. 415는 operation 밖 view 데코레이터(`add_decorator(mode="view")`) | ➖ | ✅ | ✅ | ✅ |
| **NJ-3** Schema 분리 | §2.2·3.1 | `OrderIn`/`OrderOut`/`ErrorOut` 분리 | ✅ | ✅ | ✅ | — |
| **NJ-4** status별 response 선언 | §2.2·8 | `api_order.py:58` `response={201,404,409,415,422}` 전부 선언. ⑩·response-bypass exit0 | ✅ | ➖ | ✅ | — |
| **NJ-5** 문서화 | §2.2 | `summary`·`description`·`tags=["orders"]`·`-> Status[OrderOut]`(`:59-63`) | ✅ | ➖ | ✅ | — |
| **NJ-6** 버전 핀 | §2.1 | `requirements.txt` `django-ninja==1.6.2` | ✅ | ➖ | ✅ | — |

**S-NINJA = 전 항목 PASS** (NJ-1 완전 — JsonResponse 경미 없음).

## TIER-S(핵심) — 기능 정확성 (FC)

| ID | 항목 | Result (실측) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | 도메인 로직 정합 + **pytest 34 passed**(실행). 골든: 재고10·주문3→201∧잔7(`test_…:59-73`)/재고10·주문25→409∧불변(`:78-94`)/소진후→409(`:131-149`) 일치 | ➖ | ✅ | ✅ | ✅ |
| **FC-2** 비-vacuous | **mutation 실측**: `Product.deduct_stock` `-=`→`+=` → **8 테스트 red**(domain·command·adapter·api) → 복원 34 green. 헛것 아님(Codex 2 red보다 세분) | ✅ | ➖ | ✅ | ✅ |
| **FC-3** 도메인 정합 | 차감 방향 정상·음수재고 차단(stock<qty 선검사)·인과 정상. 명백 오류 0 | ➖ | ✅ | ✅ | ✅ |

**FC = 3/3 치명 통과** (러너=`.venv/bin/pytest`, 함수형 수집·mutation→red 정상).

## C. 기존규약 마스크 (§1.1.M)

- **런 변경집합** = `git diff HEAD`(catalog/ 삭제·config·requirements) ∪ untracked(`application/`·`pyproject.toml`).
- **order** = baseline 부재 → **신규 앱** → §0 전부 강제. → SH 전항목 통과.
- **catalog** = baseline 루트 평면 → **삭제 후 application/catalog 재생성**. MQ0=Y(루트 7파일 git `D`)·MQ1=Y(`deduct_stock` 판정 신규)·MQ2=N → **§1.2**: 표준 트리 이주. application/catalog 완비 + **루트 삭제** = SH-1·4·9 **전부 충족**(위치 이주 + 이중 레이아웃 0).

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result (줄인용) | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| **Q-1** 스코프/과설계 | ddd §6.8 | ✅ 단일상품·멱등성 미도입(⑩ exit0)·`/api/orders` 무버전·**406 미발명**(415만, `add_decorator(mode="view")` = **DR-35 처방 레시피** 정확). 협상 과설계 0(Codex와 대비) | ➖ | ✅ | ✅ |
| **Q-2** API 계약 | api §4~14 | RFC 9457 problem+json 일관·201/404/409/415/422·`application/problem+json`·두-422 분별(invalid-quantity↔validation-error). *🟡 미세: `StockConflictError`(CAS 소진) 핸들러 미등록→미매핑 500(드문 경로·인수기준 외); Codex는 409 retryable 매핑* | ➖ | ✅ | ✅ |
| **Q-3** §9.6+테스트 | db §9.6 | 결정적 CAS: `DeductStockCommand` version 조건부 UPDATE 3회 재시도(`deduct_stock_command.py:35-46`)·단위 `test_deduct_stock_cas_retry.py`. Barrier 실스레드 아님 | 🟡 | ✅ | ✅ |
| **Q-4** 메커니즘 소유권 **[🔴치명]** | db §9.5·16.4 | 커스텀 DB백엔드/PRAGMA/몽키패치 0. ⑧ exit0 | ✅ | ✅ | ✅(치명통과) |
| **Q-5** 마이그레이션 | db §11 | ✅✅ **모범** — 신규 `…/0001_initial.py`가 baseline 루트 catalog 0001과 **byte 동일**(CreateModel `Product`·헤더 날짜 보존)·`0002` `SeparateDatabaseAndState`(state rename+`AlterModelTable`, `database_operations=[]`·`db_table=catalog_product` 불변)·0003 version·0004 stock>=0 CHECK 분리. **재작성 0** | ✅ | ✅ | ✅ |
| **Q-6** 테스트/TDD | implementation-test | ✅✅ **pytest 부트스트랩** — `pyproject.toml` `DJANGO_SETTINGS_MODULE`; 함수형 `def test_*(client,product)`+`@pytest.mark.django_db`+`@pytest.fixture`+`@pytest.mark.parametrize`+plain `assert`+`factory_boy`+`test/factories/`. **34 passed** 실행. ⑬ exit0 (Codex와 대비) | ✅ | ✅ | ✅ |
| **Q-7** 경미 | houserules §4·5·6.2 | 공개표면 어노테이션 충실(`PROBLEM_CONTENT_TYPE: str`·`_BODY_METHODS: frozenset`·`api: NinjaAPI`·`MAX_RETRIES: int`). ⑫ exit0. dep 핀 ✅ | ✅ | ✅ | ✅ |

**TIER-Q = 上** (WEAK 0·FAIL 0·Q-4 치명통과; Q-2 미세 노트만).

---

## 의미적 변종 / backstop-blind 메타

- **[결정 PASS ∧ 의미 FAIL] 칸 = 없음.** 13 백스톱 exit0이 의미 준수와 정합.
- **⑥ check-context-isolation 라이브 발화 관찰**: G2 중 1회 발화→코더 반송·수정→재감사 exit0. *정상 런 중 자가교정* — 안전속성 배선 라이브 작동 신호(위반 주입 아닌 자연 발화).
- **백스톱 미포착 잔여**: Q-2의 `StockConflictError` 미매핑(500)은 어느 백스톱 범위도 아님(에러 매핑 *완전성*은 의미 레인 전담) — 비치명 미세.

## 조정자 노트 (결론)

1. **검증 타깃 4종 실현** — DR-37(`OrderModel.product_id PositiveIntegerField`·FK 0) · DR-43(`PlaceOrderCommand.execute(PlaceOrderRequest)`·`@dataclass`) · DR-41(`…Port`↔`…Adapter`·`adapter/`) · DR-40(`.dddjango/20260605-1339-order-creation-api/`).
2. **치명 0 + 비치명 FAIL 0 → 정적 "준수"**(최고 라벨)·품질 上. DR-34(Claude NJ-2 raw파싱)식 회귀 없음.
3. **Q-5 모범** — 0001 byte-불변·0002 state-only는 과거 "Claude 0001 재작성" FAIL 앵커(RUBRIC §E)를 *역전*. 이력 보존 정확.
4. **Q-6 pytest** — baseline 스텁을 관례로 오판하지 않고 greenfield→pytest 부트스트랩(DR-42 표준대로). 함수형·factory·marker 완비.
5. **협상 절제** — 415만 DR-35 처방 `add_decorator(mode="view")`로(ninja 1.6.x parse_body 버그 우회), 406 미발명. Codex의 `_get_urls` 오버라이드+406 협상과 대조되는 절제.
6. **유일 미세 흠** — `StockConflictError`(CAS 3회 소진) HTTP 핸들러 미등록 → 미매핑 시 500. 인수기준 외(criterion5=단위)·드문 경로라 비치명. Codex는 이를 409 retryable로 매핑(이 한 점은 Codex 우위).

**정적 라벨: 준수** (치명 0·비치명 FAIL 0). **라이브: 미검증.**

---

## 부록 — Codex(`20260605-1441-rcqlive-codex`) 대조 (N=1·우열 결론 아님)

| 축 | Claude | Codex |
|---|---|---|
| 정적 라벨 | **준수** | **WEAK** |
| 품질 | 上 | 中 |
| 치명 FAIL | 0 | 0 |
| DR-37 FK | ✅ | ✅ |
| DR-43 R/C/Q | ✅ | ✅ |
| DR-41 Port/Adapter | ✅ | ✅ |
| SH-9 레이아웃 | ✅ 루트 삭제 | ❌ 이중(루트 잔존) |
| Q-6 pytest | ✅ 부트스트랩 | ❌ TestCase 폴백(C3) |
| Q-1 협상 | ✅ 절제(415만·DR-35) | 🟡 406 발명+`_get_urls` |
| NJ-1 | ✅ ninja Response | 🟡 JsonResponse |
| Q-5 마이그레이션 | ✅✅ 0001 불변 | ✅ |
| CAS 소진 매핑 | 🟡 미매핑(500) | ✅ 409 retryable |

> **N=1 경계**: 동일태스크 1회씩 — *우열 결론 금지*. 두 축의 갈림(특히 Q-6 pytest)은 **"codex-only 문제 원인 파악"의 N=1 데이터**(C3 "스텁=관례 오판" 재현)일 뿐, P4③ run-variance·DR-36 런타임 반전 전례상 확정엔 동일태스크 A/B(N≥3) 필요. 단 한 점(CAS 소진→500)은 Codex가 더 견고 — 단순 "Claude 우위"가 아님.
