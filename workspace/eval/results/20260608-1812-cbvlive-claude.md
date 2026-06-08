# CBV 라이브 채점 — Claude (DR-48 ninja 클래스 컨트롤러)

> **방법** EVAL-METHOD v3 · 정식 33차원 전수(결정 레인 grep/백스톱 ∥ 의미 레인 직접 read) · 사전식 집계
> **채점일** 2026-06-08 · **픽스처** `~/Desktop/dddjango-cbvlive-claude`(기존규약: baseline catalog.Product 평면 시드 — 마스크 C 적용) · 산출물 `.dddjango/20260608-1608-place-order-stock/`
> **런타임·N** Claude Code(Opus 4.8) · **N_grader=1**(조정자 단독·자기보고 불신=직접 read+백스톱 16종 실행+pytest 골든/mutation 실측) · **N=1·단일태스크**(P4③ 우열·완료 금지)
> **태스크** "재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API." · **게이트(사람 입력)** BC=① 새 독립 order / 렌즈 ddd+db+api / 스택 Ninja / 러너 표준 / 멱등성 미도입 / transient=503 / G1·G2 명백결함만 / thinking OFF
> **반칙 차단 ✅** fixture에 PROMPT.md/README.md/setup.sh 부재 · scope.md 컨닝흔적 0
> **범례** ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ➖ N/A
> **⚠️ 단서** N_grader<3(정본 full 아님) · FC-1 골든 조정자 사후작성(행위표 자명) · **Codex 런 별도 채점**(`20260608-1734-cbvlive-codex.md`) — N=1·단일태스크라 **우열 결론 금지**

---

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | catalog 완전이주(루트 `D` 전체·`R` rename 0001→infra_layer) · **MQ1=N**(판정은 order·catalog는 데이터소스) ∧ **MQ2=Y** → §1.2 미발동(4계층 면제)·**위치 `application/catalog` 이주로 충족** |
| ② 치명 게이트 | **FAIL 0건** — SD-1~7·FC-1~3·SH-1·2·4·7·NJ-1·2·Q-4 전부 통과(의미적 변종 0) |
| ②.5 실질성 | 프로덕션 import 그래프 충실 · 루트 catalog 완전 삭제(잔재 0) |
| ③ 비치명·의미변종 | 의미적 변종 0 → "준수" 유지. **Q-1 WEAK**(멀티라인 과설계·아래) |
| ④ TIER-Q 등급 | **상** (WEAK 1[Q-1]·FAIL 0·NJ 강 FAIL 0) |

**한 줄 요지**: 클래스 컨트롤러·완전이주·도메인서비스 판정·결정적 CAS-스파이·pytest·전수 예외번역까지 치명 0 FAIL의 정교한 산출물. 유일한 흠은 **태스크가 단일 상품인데 멀티라인 주문을 발명한 Q-1 과설계**.

**2차원 라벨**: **(정적: 준수 · 품질 상)** × **(라이브: 클래스 컨트롤러 생성 관측 · 에러경로 계약 관측)**
🔴 N=1·단일태스크 → "완료" 금지(§4.4).

---

## A. TIER-S 척추 — S-DDD

| ID | 항목 | §근거 | Result(줄인용) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SD-1** 판정소유 | §3.2 | `stock_sufficiency_service.py:26-32` `resolve_new_value: if snapshot.value<quantity.value: raise InsufficientStock`(무상태 도메인 서비스) | ➖ | ✅ | ✅ | ✅ |
| **SD-2** 프로덕션 호출 | §3.2 | `place_order_command.py:89-108` atomic→`read_stock`→`sufficiency.resolve_new_value`(판정)→`apply_decrement`(CAS)→`repository.save` | ➖ | ✅ | ✅ | ✅ |
| **SD-3** 무복제 | §3.2 | `product_stock_adapter.py:33-35` CAS `filter(id,version).update(stock=new_value,version+1)` — `stock>=qty` 판정 복제 0(도메인이 new_value 산출) | ✅ | ✅ | ✅ | ✅ |
| **SD-4** 애그리거트 경계 | §3.3 | `order.py:6` catalog `product_id` **ID 참조**(FK 아님)·멀티라인은 `design-spec.md:197` Vernon 규칙1 **의식적 예외**(§3.3 규칙4 동일DB 용인·전체 롤백) | ✅ | ✅ | ✅ | ✅ |
| **SD-5** 표현력 | §3.1·§3.5 | `quantity/order_line/stock_snapshot.py` 전부 `@dataclass(frozen=True)`·`StockSufficiencyService` 무상태 | ✅ | ✅ | ✅ | ✅ |
| **SD-6** 계층순수(P1a) | §5.1·ninja §6.2 | domain `HTTP/ninja import 0`·`order_controller.py:57-66` 성공 schema만·예외→status는 `config/api.py:33-171` 중앙 단일점(`problem()` 헬퍼) | ✅ | ✅ | ✅ | ✅ |
| **SD-7** 컨텍스트 통신 | §3.2·§2.5 | catalog `Product` import가 `infra_layer/acl/product_stock_adapter.py:12`에 격리·`DoesNotExist→ProductNotFound` **전수 번역**·도메인은 `ProductStockPort(ABC)` 의존 | ✅ | ✅ | ✅ | ✅ |

---

## B. TIER-S 척추 — S-HR

| ID | 항목 | §근거 | Result(줄인용) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | §0-1 | `application/order/`·`application/catalog/`(완전이주) | ✅ | ✅ | ✅ | ✅ |
| **SH-2** 4계층 | §0-2 | `{domain,application,infra,presentation}_layer/` 물리분리 | ✅ | ➖ | ✅ | ✅ |
| **SH-3** 종류폴더+명명 | §0-3·§4 | `command/PlaceOrderCommand`·`dto/PlaceOrderRequest`·`OrderLineRequest`·`query/`(빈) | ✅ | ✅ | ✅ | — |
| **SH-4** Django앱 위치 | §0-5 | models·**migrations 모두** `infra_layer/django_<app>/`(`R` rename으로 0001까지 이주·MIGRATION_MODULES 불필요) | ✅ | ✅ | ✅ | ✅ |
| **SH-5** ORM 명명 | §0-6·§4 | `OrderModel`·`OrderLineModel`·`Product`(catalog)·도메인 `Order` bare | ✅ | ➖ | ✅ | — |
| **SH-6** 포트/구현 명명 | §4 | `ProductStockPort`→`DjangoProductStockAdapter`·`OrderRepository`→`DjangoOrderRepository` | ✅ | ➖ | ✅ | — |
| **SH-7** 협력포트 위치 | §2 | `domain_layer/order/port/product_stock_port.py` | ✅ | ➖ | ✅ | ✅ |
| **SH-8** ACL 분리 | §2·§3 | `infra_layer/acl/product_stock_adapter.py`(repository 분리) | ✅ | ✅ | ✅ | — |
| **SH-9** 단일 레이아웃 | §1.4 | `test/` 단일·루트 catalog **완전 삭제**(잔재 0) | ✅ | ✅ | ✅ | — |
| **SH-10** 테스트 의미군 | §1.3 | `test/{unit,integration}/`·HTTP=integration·`conftest.py` | ✅ | ✅ | ✅ | — |

---

## TIER-S(조건부) — S-NINJA (HTTP operation 존재 → 채점)

| ID | 항목 | §근거 | Result(줄인용) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **NJ-1** 스택 | §1.1 | `config/api.py:30 api=NinjaExtraAPI()`(단일)·`order_api_router.py:12 register_controllers`·`order_controller.py:39 @api_controller` | ✅ | ➖ | ✅ | ✅ |
| **NJ-2** operation 얇음 | §2.2 | `order_controller.py:57-66` command 위임+schema 매핑(raw 파싱/ORM/비즈 0). ⚠️ `_build_place_order_command`(컴포지션 루트)가 컨트롤러 내 — 배선만(노트) | ✅ | ✅ | ✅ | ✅ |
| **NJ-3** Schema 분리 | §2.2 | `schema_in.PlaceOrderIn(lines)`·`schema_out.OrderOut`·도메인 직렬화 0(Published Language 변환) | ✅ | ✅ | ✅ | —(강) |
| **NJ-4** status 선언 | §2.2 | `order_controller.py:43-49 response={201,404,409,422,503}` | ✅ | ➖ | ✅ | —(강) |
| **NJ-5** 문서화 | §2.2 | `:50-55 summary="주문 생성"+description`·반환 `Status[OrderOut]` | ✅ | ➖ | ✅ | —(경미) |
| **NJ-6** 버전 핀 | §2.1 | `requirements.txt django-ninja==1.6.2`·`-extra==0.31.4` | ✅ | ➖ | ✅ | —(경미) |
| **NJ-7** catch-all | §6.2 | `config/api.py:169-171 @api.exception_handler(Exception)→_server_error 500`·되던지기 0·`OperationalError`도 비-retryable→500 분기·스택 로그만(traceback 차단) | ✅ | ✅ | ✅ | —(강) |

---

## TIER-S(핵심) — FC

| ID | 항목 | Result(.venv pytest 실측) | 레인 | 종합 | 치명 |
|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | 독립: 재고10·주문3→**201∧잔7** / 재고2·주문5→**409∧불변** = 2/2 | 의미 | ✅ | ✅ |
| **FC-2** mutation 비-vacuous | ②경계 `<→<=`=2 red(`test_exact_match_yields_zero` 커버) ①부호 `-→+`=10 red → **2/2 red** | 결정(주입) | ✅ | ✅ |
| **FC-3** 도메인 정합 | 차감 방향 정상·`stock>=0` CHECK·인과 정상·oversell 차단 검증 | 의미 | ✅ | ✅ |

---

## C. 기존규약 마스크 (§1.1.M)

- **런 변경집합** = `git diff HEAD`(D 루트 catalog 전체·R rename 0001·M settings/urls) ∪ untracked(`application/` 전체).
- **MQ0**: 기존 catalog 앱 삭제·대체 = Y(루트 완전 삭제→application/catalog 재생성).
- **MQ1**(핵심규칙 분기?): **N** — catalog는 `version` 필드+`CheckConstraint(stock≥0)`만. 판정은 order `StockSufficiencyService`.
- **MQ2**(데이터소스?): **Y**.
- **판정**: `MQ1=N` → §1.2 미발동(catalog 4계층 면제). touched라 위치 비면제 → `application/catalog/` 완전이주로 **SH-1·4 충족**(Codex 셰임 잔재와 달리 루트 완전 삭제).

---

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result(줄인용) | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| **Q-1** 스코프/과설계 | ddd §6.8 | **⚠️ 멀티라인 주문 발명** — 태스크는 단일 상품(`product_id`+`quantity`)인데 `lines=[OrderLineRequest...]`·`DuplicateProductLine`·`OrderLine`·`OrderLineModel`·다라인 트랜잭션. `scope.md:8`서 "단일/다품목 설계 위임"으로 열고 `design-spec.md:179,197`서 의식적 정당화(단일=1-라인 특수케이스)하나 **요청 외 발명**(RUBRIC Q-1 멀티라인 앵커). 멱등성·event는 절제 | ➖ | 🟡 | 🟡 |
| **Q-2** API 계약 | api §4~14 | problem+json(RFC9457)·status 일관·`409/503/422/404` 구분·`Retry-After`·`invalid-params` | ➖ | ✅ | ✅ |
| **Q-3** §9.6+동시성 실현 | db §9.6 | `design-spec.md:362-375 Risky Write Block 8행`+`test_oversell_contention.py:48-76` **결정적 CAS-스파이**(`mocker.patch` 경합 1회→수렴·전체 0행→503)·"스레드 race 아님" — RUBRIC Q-3 PASS 앵커 | grep+의미 | ✅ | ✅ |
| **Q-4** 메커니즘 **[🔴치명]** | db §9.5 | version CAS만·커스텀 백엔드/PRAGMA/몽키패치 0·`check-mechanism-ownership` exit0 | ✅ | ✅ | ✅ |
| **Q-5** 마이그레이션 | db §11 | `R` rename `catalog/0001→application/catalog/.../0001`(히스토리 보존)·`0002` expand(version/CHECK) | ✅ | ✅ | ✅ |
| **Q-6** 테스트/TDD | impl-test | **✅ pytest 도입** — `pyproject.toml [tool.pytest.ini_options]`+`DJANGO_SETTINGS_MODULE`·함수형 `def test_`·`mocker`·`@pytest.fixture`·`django_db`·**52 테스트 green** | 결정(실행)+의미 | ✅ |
| **Q-7** 경미 | houserules §4 | 공개표면 어노테이션·`check-public-surface-annotation` exit0·핀 일치 | ✅ | ✅ | ✅ |

**Q 등급(카운트)**: Q-2·3·5·6·7 PASS · **Q-1 WEAK** · NJ-3·4·7 PASS → WEAK 1·FAIL 0·강 FAIL 0 → **품질 상**.

---

## 의미적 변종 / backstop-blind 메타

- `[결정 PASS ∧ 의미 FAIL]` 칸 = **0건**.
- 백스톱 16종 전부 exit0. blind-spot: `check-error-centralization`은 application_layer만 봄 → presentation 중앙 핸들러(`config/api.py`)는 의미 레인 직접 read로 SD-6 PASS 확인.
- 컴포지션 루트가 컨트롤러 내(`order_controller.py:31-36`) — presentation이 infra import(DIP 배선). DR-43서 컴포지션 루트 위치는 defer(표준 미확정) → 치명 아님·경미 노트.

---

## 에러 경로 라이브 관측 (§4.3.1 — 별도 트랙·완료 비산입·라벨 무영향)

| 키 | 계약 속성 | 관측 status·형식 | 화이트리스트 | 판정 |
|---|---|---|---|---|
| **EP-1** 깨진 본문 | 비-JSON POST→problem 클라오류 | `config/api.py:117 on_http_error→problem` 400 | {400} | ✅ 관측 |
| **EP-2** 무효 입력 | 수량 0/음수→problem 클라오류 | `422`(ValidationError→problem·invalid-params) | {422,400} | ✅ 관측 |
| **EP-3** transient 소진 | 락/CAS 소진→retryable·**500 아님** | `503 Retry-After`(StockContention·`OperationalError` retryable 분기)·비-retryable→500 | {503,409} | ✅ 관측 (ACL-EX2 회귀 없음·분기 명시) |
| **EP-4** 재고 부족 | 재고<주문→충돌 | `409 insufficient-stock`(FC-1 교차) | {409} | ✅ 관측 |

**에러경로 계약: 관측**(전 4종 화이트리스트 부합·probe FAIL 0). 치명 게이트 아님(라벨 무영향).

---

## 조정자 노트

1. **Codex와의 trade-off(우열 결론 아님·N=1)**: Claude는 **Q-3 결정적 CAS-스파이·Q-6 pytest·완전이주·전수 예외번역**에서 강하고, **Q-1 멀티라인 과설계**가 흠. Codex(`20260608-1734`)는 **Q-1 단일 절제**가 강하고 **Q-3 ThreadPool 비결정·Q-6 pytest 미도입·셰임 잔재**가 흠. 차원별 강·약이 **교차**한다 — 두 런 모두 치명 0 FAIL. **N=1·단일태스크라 종합 우열은 금지**(P4③).
2. **catalog 이주**: Claude는 루트 완전 삭제 + `R` git rename(0001 히스토리 보존) + application/catalog 재생성 = **깔끔한 완전이주**(SH-4·9 무흠). Codex는 셰임+MIGRATION_MODULES(잔재 🟡). 단 Claude는 이 이주에 라이브 1h+ 소요(catalog 반송 토끼굴) — 비용 차이는 별도(채점 무관·§3 bisect).
3. **Q-1 멀티라인 판정**: design-spec 의식적 정당화(Vernon 규칙1 예외·단일=1-라인)라 FAIL 아닌 WEAK. 단 태스크 프롬프트는 단일 상품이라 "요청 외 발명"이 성립 → 품질 상 유지하되 흠 명기.
4. **FC 복원**: 이번엔 측정 전 `git add -A`로 추적 상태를 만들어 `git checkout` 복원 성공(Codex 채점의 untracked 복원 실패 교훈 반영). pytest 21→52 green 무결.

🔴 **N=1·단일태스크·우열 금지**(P4③). reviewer ② "무조건 클래스" 발화는 자연 준수라 미측정(함수형 주입 프록시 별도).
