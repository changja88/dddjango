# 평가 기록 — Claude · p1a-v3 (주문생성 API)

> **대상**: `~/Desktop/dddjango-p1a-v3-claude` (런타임=Claude Code, 태스크B=주문생성, 가장 마지막 스모크)
> **기능**: "주문 생성 API. 별도 order 개념, 요청 상품·수량의 주문 생성, catalog가 재고 소유·주문 시 차감(부족 시 409)."
> **기준**: `eval/rubric/RUBRIC.md` + `EVAL-METHOD.md` (v2 초안, **미동결** — 동결 전 결정 미해소는 아래 명시)
> **채점일**: 2026-05-31. 증거 = 코드 정독 + 테스트 실행 + FC 골든 실측(서브에이전트 수집 → 호출자 집계·검증).
> **정직 경계**: N=1·단일 태스크. "규칙 준수 + 기능 정확성"까지. 우열 단정 아님.

---

## 종합 판정 (사전식 집계)

**🟠 규칙 준수 게이트 FAIL — 척추 치명 1건(논쟁적)** · **🟢 기능 정확성 FC 전부 PASS** · 의미적 변종 1건(동일 항목).

| 단계 | 결과 |
|---|---|
| ① 기존규약 마스크 C | catalog(기존앱)에 재고판정(`Product.deduct_stock`) 적재 + **DDD 이주** → §1.2·ddd §3.2:632(판정 소유→구조 이주)와 **정합**(표준이 지지하는 방향). 마스크 통과. |
| ② 치명 게이트 | **SD-7 ✗**(보수적 판정) → **픽스처 FAIL**. 그 외 SD·SH·NJ·FC 치명 **전부 PASS** |
| ②.5 실질성 관문 | PASS (리치 도메인·테스트 62개 비-vacuous·종류폴더 사용) |
| ③ 의미적 변종 | **1건(SD-7)** → "준수" 라벨 금지 |
| ④ TIER-Q | 게이트 FAIL이라 등급 산정 대상 아님(참고용; 사실상 Q-5 외 전부 PASS) |

**한 줄**: P1a·§9.6·메커니즘소유권·기능정확성·구조 **거의 전면 준수**. 유일 척추 치명 = **SD-7**(order의 ACL이 catalog 구체 infra `DjangoProductRepository` 직접 import + catalog OHS 부재) — *design-spec이 명시 수용한 underdetermined 흠*. 추가 품질 흠 = **Q-5 L1**(catalog 0001 재정의 — 신규DB 무해, §11 이력불변 관점 흠).

---

## 치명 게이트 표 (SD 전부·FC 전부·SH-1·2·4·7·NJ-1·2)

| 항목 | 판정 | 핵심 줄 인용 |
|---|---|---|
| SD-1 판정소유 | ✅ PASS | `catalog/.../product.py:35-46` `Product.deduct_stock`(`if self.stock<quantity: raise`→차감+version) |
| SD-2 프로덕션호출 | ✅ PASS | `product_stock_acl.py:42-44`→`create_order_app.py:76-80` repo.get→deduct→save |
| SD-3 무복제 | ✅ PASS | CAS WHERE = `id`+`version`만(`product_repository.py:38-44`), 비즈조건 복제 0; `stock__gte=0`은 CHECK뿐 |
| SD-4 경계 | ✅ PASS | `order_line.py:14-18` `product_id:int`만; ORM FK 미설정(`order_line_model.py:23`) |
| SD-5 표현력 | ✅ PASS | `order_line.py:13` `frozen=True`; 무상태 서비스 |
| SD-6 계층순수성/P1a | ✅ PASS | domain+app에 HTTP/ninja/status import **0**(grep); 중앙 `@api.exception_handler` 4개 단일(`order_api_router.py:68-145`); operation 성공만 return(`api_order.py:61-63`); **app은 status 변환 안 함**(`StaleProductVersion`만 재시도용 catch). **DR-24 C트랙 P1a 변종 미발견** |
| **SD-7 컨텍스트통신** | **🟠 FAIL(보수적·논쟁적)** | `product_stock_acl.py:17-18,34` catalog **구체 infra** `DjangoProductRepository` 직접 import; catalog `published_service/`(OHS) **부재**. §근거 FAIL="타 BC infra_layer(구체 포함) 직접 import" [DR-24 L2, §E 앵커 FAIL예시]. *단 design-spec §0가 "OHS 없으므로 ACL로 분리"를 명시 수용·소비 시그니처는 도메인 ABC* → underdetermined |
| SH-1 컨테이너 | ✅ PASS | `application/order/` |
| SH-2 4계층 | ✅ PASS | 4계층 분리 |
| SH-4 Django앱위치 | ✅ PASS | `infra_layer/django_order/` + `django_catalog/`; `apps.py:12-13` 점경로·label |
| SH-7 협력포트위치 | ✅ PASS | `order/domain_layer/order/port/product_stock_port.py` [§E 앵커 PASS예시] |
| NJ-1 스택채택 | ✅ PASS | `NinjaAPI`+`Router`(`order_api_router.py:45-46`) |
| NJ-2 operation얇음 | ✅ PASS | `api_order.py:61-63` 서비스호출+Location+Status(201)만 |
| FC-1 골든 | ✅ PASS(실측) | 재고10·주문3→201/잔7(`test_create_order_api.py:73-95`) · 재고2·주문5→409/불변2/주문0(`:101-116`) |
| FC-2 비-vacuous | ✅ PASS | 경계 `test_product.py:27-33`(stock5·qty5→0)·순차 oversell `test_create_order_api.py:204-225`·CAS 결정적 `test_create_order_service.py:115-152` |
| FC-3 도메인정합 | ✅ PASS | 음수재고 생성자 거부(`product.py:27-28`)·미충족 시 상태불변(`product.py:41-44`) |

→ **치명 게이트: SD-7 단일 FAIL(보수적) ⇒ 픽스처 FAIL.** 나머지 척추·NJ·FC 치명 **전부 PASS**.

---

## 비-치명 항목 (전부 PASS 또는 양성)

| 항목 | 판정 | 줄 인용 |
|---|---|---|
| SH-3 종류폴더 | ✅ | `value_object/`·`port/`·`repository/`·`models/`·`acl/` |
| SH-5 ORM명명 | ✅ | `OrderModel`/`OrderLineModel`/`ProductModel` vs bare |
| SH-6 포트명명 | ✅ | `Interface`/`Impl`/`*_repo.py` 0 |
| SH-8 ACL분리 | ✅ | `infra_layer/acl/product_stock_acl.py` |
| SH-9 단일레이아웃 | ✅ | `test/`만(tests/ 없음) |
| SH-10 테스트의미군 | ✅ | `test/{unit,integration,e2e}` |
| NJ-3 Schema분리 | ✅ | `CreateOrderIn`/`OrderOut`·`from_domain`(`schema_out.py:29-39`) |
| NJ-4 status선언 | ✅ | `order_api_router.py:51` `{201,404,409,422}` |
| NJ-5 문서화 | ✅ | summary/tags/description(`:52-54`) |
| NJ-6 버전핀 | ✅ | `django-ninja==1.6.2` |
| Q-1 스코프/과설계·G1 | ✅(주의) | catalog 이주(고-blast) §5.4 G1 옵션 A/B 상정·사용자 승인(`design-spec.md:298`). 합산정규화·UniqueConstraint는 task 미요구지만 §1.2 불변식으로 명세박힘(발명 아닌 설계결정·경계선) |
| Q-2 API계약 | ✅ | RFC9457(`error_out.py:18-45`), 409 type 2분리 |
| Q-3 §9.6+테스트 | ✅ | design-spec §3.3 8행 블록(`:159-168`)·CAS 스파이 `test_create_order_service.py:47-62`·소진→409 |
| Q-4 메커니즘소유권 | ✅ | 커스텀 백엔드/PRAGMA/`select_for_update`/몽키패치 **0**(grep); version CAS+CHECK만 |
| **Q-5 마이그레이션안전** | **🟠 WEAK(L1)** | catalog `0001_initial`을 **같은 label `catalog`에서 재정의**(baseline `catalog/migrations/0001`=Product 삭제 → 새 경로 `django_catalog/migrations/0001`=ProductModel). **신규DB 무해**(db_table `catalog_product` 보존·`makemigrations --check`=No changes·데이터유실 없음)이나 §11 "기존 0001 불변" 관점 흠 [DR-24 L1 — 유지] |
| Q-6 테스트/TDD | ✅ | `check` 0 issues · `test` **62/62 OK**(0.026s) |
| Q-7 경미 | ✅ | 빈 종류폴더 `__init__.py`(§0 준수)·타입힌트 완비·주석 한국어(§5.3) |

---

## 의미적 변종 (decision-lane PASS ∧ semantic FAIL)

**SD-7** (유일): 구조상 ACL은 `infra_layer/acl/`에 올바로 분리(SH-8 PASS) → decision-lane 통과. 그러나 semantic으로 ACL이 catalog **구체 infra `DjangoProductRepository`를 직접 import**(`product_stock_acl.py:17-18`) — OHS(published_service) 부재라 도메인 ABC만으로 소비할 표면이 없음. *단 design-spec §0 명시 수용 + 소비 시그니처가 도메인 ABC `ProductRepository`라 방어 여지*. **P1a 의미변종(멱등성 크립·app 비즈예외 catch·죽은 핸들러)은 미발견** — DR-24 C 트랙의 Codex 변종이 이 픽스처엔 **없음**.

---

## 마스크 C (기존규약) 적용 메모
catalog에 재고판정(`Product.deduct_stock`)을 적재하며 **DDD로 이주** → 마스크 C "기존앱+판정적재 → §1.2/ddd §3.2 이주" 분기와 **정합**(표준 지지 방향). 이주 *결정*은 깨끗. 다만 이주 *집행 디테일*에서 SD-7(L2)·Q-5(L1) 두 흠 발생 — "이주는 맞으나 실행이 거칠다".

---

## DR-24 L 트랙 대응 (정정 포함)
- **L1(0001 재작성) — 유지(서브에이전트 "반증" 정정)**: 호출자 직접 검증 — baseline `catalog/migrations/0001`(Product)이 삭제되고 같은 label에서 새 0001(ProductModel) 정의됨 = §11 이력불변 흠. 증거수집 서브에이전트가 *새 파일의 git 이력 0건*을 "불변"으로 오독했으나, 실제는 *baseline 0001 미보존*. 신규DB 무해는 맞음.
- **L2(ACL→catalog 구체infra import + OHS부재) — 해당(SD-7 FAIL)**: `product_stock_acl.py:17-18`.
- **L3·L4(P1a·§9.6·메커니즘·CAS = Clean) — 해당(전부 PASS)**: 정석 설계가 구현에서 실현.
- 과설계(합산정규화·UniqueConstraint): 명세 추적 가능·발명 아님(Q-1 주의 수준).

**견고한 면(공정)**: SD-1~6·SH 전부·NJ 전부·FC 전부 PASS — P1a clean·§9.6 8행 블록·메커니즘소유권 깨끗·CAS 3계층·62/62 그린. 결함은 cross-BC 경계 집행 2축(SD-7 OHS 부재·Q-5 이력)에 국한.

---

## 부록 — Codex와의 대칭 (cross-BC 경계의 반대 면)
같은 태스크에서 두 런타임은 **cross-context 경계(OHS/ACL)의 반대쪽에서 실패**:
- **Codex**: OHS 보유(SD-7 ✅)지만 catalog 평면 유지에서 **SQL 판정 복제(SD-3 ✗)** + **P1a 의미변종(SD-6 ✗)** + 포트위치(SH-7 ✗) + 멱등성 과설계.
- **Claude**: 리치 도메인(SD-3·SD-6 ✅)지만 ACL이 **구체 infra 직접 import(SD-7 ✗)** + 0001 재정의(Q-5).
- **공통**: FC 전부 PASS(기능 동등 정확)·테스트 그린·메커니즘소유권 깨끗. 둘 다 cross-BC 경계를 *완전히는* 못 맞췄으나, **Claude의 흠이 단일·논쟁적·양성인 반면 Codex는 다축·은닉(P1a)·과설계**. (상세 비교는 `EVAL-p1a-v3-codex.md`.)
