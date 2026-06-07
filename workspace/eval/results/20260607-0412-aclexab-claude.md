> **방법**: EVAL-METHOD.md v3 · **채점일**: 2026-06-07
> **픽스처**: `~/Desktop/dddjango-aclexab-claude` (baseline `6e48b68` rcqlive-claude 계보) · 산출 `.dddjango/20260607-0244-order-creation-api/`
> **런타임·N**: Claude · **N=1** (단일 태스크 timeline — 우열·결정성 결론 아님)
> **태스크**: 주문 생성 API + catalog ACL + CAS (aclex 테마 A+B 처방 `062a64f` 재라이브) — **라이브 목표=Claude 완벽화**라 표준 채점 + DR-24식 심층 감사 병행
> **게이트**: BC=미강제(설계자→4계층 이주 선택) · 렌즈 ddd+db+api · 스택 "표준 기본대로" · G1·G2 명백한 결함만 반송 · thinking OFF
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ➖ N/A
> **⚠️ 단서**: ① **N_grader=1**(조정자 단독·blind 미적용) ② 라이브 게이트 발화 미검증(정적+probe) ③ FC-1·min1·maj2는 조정자 `override_settings(ALLOWED_HOSTS)`+migrate 후 직접 probe로 실측 ④ **자기보고 불신 적용**(코디 "44 passed·blocker 0" 너머 심층 적대 감사 수행).

# 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | **발동** — catalog 판정 적재(MQ1=Y∧MQ2=N) → **catalog 4계층 이주**(`application/catalog/`·`infra_layer/django_catalog/`)로 **충족** |
| ② 치명 게이트 | **FAIL 0** — SD 1~7·FC 1~3·SH-1·2·4·7·NJ-1·2·Q-4 전부 통과 |
| ②.5 실질성 관문 | 통과 (도메인 메서드·4계층 실사용·빈 골격 아님) |
| ③ 비치명·의미변종 | min1❌·maj1 transient 부정밀·graphify 오염 → WEAK 상한 |
| ④ TIER-Q 등급 | WEAK 3·FAIL 0 → **품질 '중'** |

**한 줄 요지**: 치명 0 = **정적 준수**. catalog 4계층 이주(SH-1·4 ✅)·pytest 44 passed(Q-6 ✅)·version CAS만(SD-3 ✅)·결정적 CAS 스파이(maj3 ✅)로 **Codex보다 깨끗**. 단 **2개 처방 흠**(maj1 transient 판정 부재·min1 product_id 상한 누락) + graphify 오염.

**2차원 라벨**: **(정적: 준수[WEAK]) × (라이브: 미검증)** — Codex(정적 FAIL)와 대조.

---

## A. TIER-S 척추 — S-DDD

| ID | 항목 | Result (조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| SD-1 | 판정 소유 | `product.py:22 Product.deduct_stock`(`stock<quantity` raise)·`order.py Order.place` | ✅ | ✅ | ✅ | ✅ |
| SD-2 | 프로덕션 호출 | `command.py:54→adapter:51 product.deduct_stock→:57 save_stock_deduction` 호출 추적 | ➖ | ✅ | ✅ | ✅ |
| SD-3 | 무복제 | `product_repository.py:32-37` **version CAS만**(`filter(pk,version).update`)·**`stock__gte` 복제 0** — Codex B형보다 깨끗 | ✅ | ✅ | ✅ | ✅ |
| SD-4 | 애그리거트 경계 | `Order`(scalar `product_id` no-FK)·1트랜잭션(`command:53 atomic`) | ✅ | ✅ | ✅ | ✅ |
| SD-5 | 모델 표현력 | `Product`/`Order` 도메인·무상태·유비쿼터스 | ✅ | ✅ | ✅ | ✅ |
| SD-6 | 계층 순수성 | operation `api_order.py:67-88` service+`Status(201)`만·**presentation 단일 변환점**(`problem_response.py`)·domain HTTP 0·**Exception catch-all 있음**(Codex 누락분) | ✅ | ✅ | ✅ | ✅ |
| SD-7 | 컨텍스트 통신 | `product_stock_adapter.py` ACL이 catalog `ProductRepository`(포트) 경유·catalog 예외 번역·**catalog infra import ACL 안에 캡슐화**(:38-41) | ✅ | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **SH-1** | 컨테이너 | **catalog·order 둘 다 `application/<app>/`**(catalog 이주 — Codex와 정반대). 백스톱 exit0 | ✅ | ✅ | ✅ | ✅ |
| **SH-4** | Django앱 위치 | `infra_layer/django_catalog/models`·`django_order/models`·migrations 전부 `infra_layer/django_<app>/` | ✅ | ➖ | ✅ | ✅ |
| SH-2 | 4계층 | catalog·order 각 `{domain,application,infra,presentation}_layer/` | ✅ | ➖ | ✅ | ✅ |
| SH-3 | 종류폴더+명명 | `command/place_order_command.py PlaceOrderCommand`·`dto/place_order_request @dataclass PlaceOrderRequest`·R/C/Q 일치 | ✅ | ✅ | ✅ | — |
| SH-5 | ORM 명명 | `ProductModel`·`OrderModel`(ORM)·`Product`·`Order`(도메인 bare) | ✅ | ➖ | ✅ | — |
| SH-6 | 포트/구현 명명 | `ProductStockPort`·`DjangoProductStockAdapter`·`ProductRepository`·`DjangoProductRepository` | ✅ | ➖ | ✅ | — |
| SH-7 | 협력 포트 위치 | `order/domain_layer/order/port/product_stock_port.py` | ✅ | ➖ | ✅ | ✅ |
| SH-8 | ACL 분리 | `order/infra_layer/acl/product_stock_adapter.py` | ✅ | ✅ | ✅ | — |
| SH-9 | 단일 레이아웃 | 단일 `test/` (catalog `tests.py` 삭제됨 — `D catalog/tests.py`) | ✅ | ➖ | ✅ | — |
| SH-10 | 테스트 의미군 | `test/{unit,integration,e2e}`·HTTP=integration | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| NJ-1 | 스택 채택 | `api_order.py:31 Router`·`order_api_router.py:19 NinjaAPI` | ✅ | ➖ | ✅ | ✅ |
| **NJ-2** | operation 얇음 | `api_order.py:67-88` 선언적 `payload: OrderIn`·command 호출·`Status(201)` 매핑만 — 수동 파싱·ORM·분기 0 | ✅ | ✅ | ✅ | ✅ |
| NJ-3 | Schema 분리 | `OrderIn`·`OrderOut`·`ProblemOut` 분리 | ✅ | ✅ | ✅ | —(강) |
| NJ-4 | status별 response 선언 | `api_order.py:51-60 response={201,400,404,409,415,422,503,500}` 전부 `response={}` | ✅ | ➖ | ✅ | —(강) |
| NJ-5 | 문서화 | `summary`·`description`·`tags`·`-> Status[OrderOut]` | ✅ | ➖ | ✅ | —(경미) |
| NJ-6 | ninja 버전 핀 | `requirements.txt django-ninja==1.6.2` | ✅ | ➖ | ✅ | —(경미) |

## TIER-S(핵심) — FC

| ID | 항목 | Result (조정자 실측) | 종합 | 치명 |
|---|---|---|---|---|
| FC-1 | 골든 오라클 | probe: 재고5주문2→**201·잔3** / 인수 `test_repeated_orders_exhaust...→409` | ✅ | ✅ |
| FC-2 | 비-vacuous | pytest 44 passed·`test_deduct_more_than_stock_raises`·CAS 스파이 red 가능·mutation 적합 | ✅ | ✅ |
| FC-3 | 도메인 정합 | 차감 방향 정상·`CHECK(stock>=0)` 최후그물·인과 정상 | ✅ | ✅ |

## C. 기존규약 마스크 (§1.1.M)

- **MQ0**(catalog 삭제·대체?): Y — baseline `catalog/` `D`(삭제) + `application/catalog/` 재생성(이주).
- **MQ1**(핵심 규칙 분기?): **Y** — `Product.deduct_stock` 판정.
- **MQ2**(단순 데이터소스?): **N** — 재고 차감 판정 소유.
- **판정**: MQ1=Y∧MQ2=N → §1.2 발동 → catalog 표준 트리 대상. **`application/catalog/` 이주로 충족** → **SH-1·4 PASS**(Codex는 동일 입력에 평면 유지 = FAIL). Q-5: catalog `0001` 불변 + `0002` state-only rename + `0003` version/CHECK expand = 이력 보존 ✅.

## D. TIER-Q 품질 (WEAK 3·FAIL 0 → '중')

| ID | 항목 | Result | 종합 |
|---|---|---|---|
| Q-1 | 스코프/과설계 | 멱등성 미구현(스코프 준수)·협상 415만(406 Accept 미발명 — Codex와 대조 ✅) / **🟡 스코프 외 오염**: `graphify-out/`·`CLAUDE.md`·`.claude/settings.json` = Claude가 태스크 무관 **graphify 스킬 산출**(dddjango 외) | 🟡 |
| Q-2 | API 계약 | problem+json·status 일관·503 근거 / **🟡 maj1 transient 판정 부재**: `handle_operational_error`가 `OperationalError` **전부 503**(design-spec:136 "transient 변종만"과 불일치 — 영구 장애도 retryable 오분류) | 🟡 |
| Q-3 | §9.6+동시성 | 8행 design-spec:211-222 ✅·**결정적 CAS 스파이**(stale-version `test_django_product_repository:50`·재시도 수렴 `test_place_order_command:55`)·rollback 원자성 `test_..._rollback` | ✅ |
| Q-4 | 메커니즘 [🔴치명] | 표준 ORM·version CAS·`CHECK`·커스텀 백엔드/PRAGMA/몽키패치 0 | ✅ |
| Q-5 | 마이그레이션 | `0001` 불변·`0002` state-only rename·`0003` expand·`db_table='catalog_product'` 보존 | ✅ |
| Q-6 | 테스트/TDD | **✅ pytest 44 passed**·`@pytest.mark.django_db`·`mocker`·함수형 — **pytest 관용구 준수**(Codex와 정반대) | ✅ |
| Q-7 | 경미 | **🟡 min1**: `schema_in.py:11 product_id: int = Field(gt=0)` **상한 없음**(quantity는 `le=MAX_QUANTITY` 有) → 거대 id 500 / 공개표면 어노테이션 부분 | 🟡 |

---

## 의미적 변종 / backstop-blind 메타

- 치명 항목 [결정 PASS ∧ 의미 FAIL] **없음** — SH-1·4가 결정·의미 모두 PASS(catalog 이주). Codex와 정반대.
- 백스톱 13종 전부 통과는 **진짜 준수**(catalog 이주·version CAS·중앙 핸들러)로 뒷받침됨 — backstop-blind 의미변종 없음.

## 조정자 노트 (결론) — Claude 완벽화 관점

1. **테마 A+B 처방 대부분 실현 + Codex 대비 우수**: catalog 4계층 이주(SH-1·4)·pytest(Q-6)·version CAS만(SD-3)·결정적 CAS 스파이(maj3)·Exception catch-all(maj1 형식)·named constraint(maj4)·마이그레이션 이력(Q-5). **치명 FAIL 0 = 정적 준수**.
2. **🔴 처방 흠 2개 (표준 처방 후보 — '별도 채점할 것')** — 아래 §심층 감사.
3. **P4③ 재현**: 같은 입력에 Claude=이주·pytest / Codex=평면·Django TestCase. 런타임 갈림이 **이번엔 Claude 우위**(DR-24·c4live·nj2live에선 반대로도 갈렸음 — N=1·우열 단정 금지).

## 부록 A — 테마 A+B 7결함 처방 실현 매트릭스

| # | 처방 | Claude 실현 | 근거 |
|---|---|---|---|
| maj1 | DB예외 transient→503/영구→500 | **🟡 부분** | `handle_operational_error`·catch-all·**단 OperationalError 전부 503**(transient 판정 부재) |
| maj2 | HttpError→problem+json | **✅** | probe 깨진본문→400 problem+json |
| maj3 | 동시성 위장 방지 | **✅ (우수)** | 결정적 CAS 스파이·stale-version 주입·재시도 수렴 (모킹 아님) |
| maj4 | constraint 귀속 | **🟡** | named `CheckConstraint(stock>=0)` 검증(sqlite선 PositiveIntegerField 미작동이라 구별)·**Postgres면 동치 오귀속 잠재** |
| min1 | 외부 식별자·수치 상한 | **❌ (비대칭)** | quantity `le=MAX_QUANTITY` ✅ / **product_id 상한 없음**→거대 id 500 |
| min2 | latent 도메인 핸들러 | **✅** | `InvalidQuantity` 핸들러(`problem_response:125` 422) 있음 |
| min3 | write-conflict e2e | ➖ | (해당 없음) |

## 부록 B — 🔬 DR-24식 심층 감사: Claude 완벽화 처방 후보

> 자기보고 "44 passed·백스톱 PASS·blocker 0" *너머*. 표면 통과지만 표준을 고칠 실질 흠.

### 🔴 H1 — maj1 transient 판정 부재 (design-spec↔구현 갭)
- **현상**: `problem_response.py:156-164 handle_operational_error`가 **`OperationalError`를 무조건 503+Retry-After**로 매핑. sqlstate/메시지 판정 없음.
- **갭**: design-spec:136은 **"transient `OperationalError`(락·deadlock·serialization failure 변종)만 503"**으로 정밀 명시했으나 **구현이 전부 503**으로 뭉갬 → 영구 장애(disk I/O·no-such-table·schema 손상)도 retryable 503 → 클라이언트 무한 재시도 유발.
- **대조**: **Codex는 `is_retryable_database_error`**(sqlstate 40001/40P01/55P03 + "locked"/"deadlock" 메시지)로 정밀 판정 — 영구는 500. **이 항목은 Codex가 우수**.
- **표준 처방 후보**: `implementation-django-ninja` final.md의 maj1 레시피에 `_is_retryable_db_error` 판정 함수가 *있는데도*(062a64f) Claude coder가 미준수·단순화. → **레시피 salience 강화** 또는 discipline-reviewer "Operationalost 전수 503 = transient 판정 누락" 렌즈, 혹은 결정적 백스톱(handler가 OperationalError를 무판정 503 매핑 시 경고).

### 🔴 H2 — min1 입력 상한 비대칭 (product_id 누락)
- **현상**: `schema_in.py` `quantity: Field(ge=1, le=MAX_QUANTITY)` 상한 有 / **`product_id: Field(gt=0)` 상한 無** → 거대 product_id(10³⁰) → `OverflowError`(`product_repository.py:21 get(pk=...)`) → catch-all 500. (problem+json이나 **입력 오류가 422 아닌 5xx 오분류** — min1 처방 목적 미달.)
- **표준 처방 후보**: `architecture-api` §5.1 "외부 식별자·수치 입력 상한"이 *수량*엔 적용됐으나 *외부 식별자(product_id)*엔 누락. §5.1 salience("식별자도 포함") 또는 reviewer.

### 🟡 H3 — graphify 스코프 외 오염
- `CLAUDE.md`("graphify knowledge graph at graphify-out/")·`graphify-out/`(graph.json·GRAPH_REPORT.md)·`.claude/settings.json` = Claude가 주문 API 태스크 중 **graphify 스킬 실행**. dddjango 산출물(application/)은 깨끗하나 **fixture 환경 오염** — dddjango 표준 밖 사안(graphify 별도 스킬)이나 라이브 위생 차원 기록.

### 🟡 H4 — maj4 환경 의존 구별 (잠재)
- `test_check_constraint_rejects_negative_stock`가 named constraint 검증이나, **sqlite라서** PositiveIntegerField CHECK 미생성으로 *우연히* 구별됨. **Postgres면 둘 다 CHECK 생성→동치→오귀속**(The Liar 변종 재발 가능). design-spec:236이 인지했으나 테스트는 환경 의존.
