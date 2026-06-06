# 채점 결과지 — pytestlive · Codex (DR-42 라이브 검증)

> **런타임**: Codex (인터랙티브) · **fixture**: `~/Desktop/dddjango-pytestlive-codex` · **채점 일시**: 2026-06-04 23:11
> **목적(정직 경계)**: N=1 sanity — "DR-42(pytest 표준·§6.1 부트스트랩 해지·백스톱 ⑬)가 라이브 런에서 작동하나". **우열·결정성 결론 아님.**
> **채점자 경계**: 1차 단독 grader(N=1). 치명 의미 판정 2건(SH-1 §0-1·SD-6 timezone)은 EVAL-METHOD §1.0 N≥3 적대 확인 권장 — 아래 🔴⚠️ 표기. **(2026-06-04 사용자 피드백 반영 개정: catalog 2개=SH-1 격상·presentation 과다=Q-1 ninja 격상·published_service=모호점 신규)**
> **태스크**: 주문 생성 API(단일 상품+수량, 재고 부족 409). 게이트 답: G0 스코프 제안대로·lens ddd·api·db·배치 **설계자가 정함**(미강제) / G1 승인 / G2 승인 / coder thinking OFF.
> **architect 자율 결정**(배치 미강제 결과): order를 **별도 독립 BC**로 분리 + catalog 4계층 이주 — 올바른 BC 분리에 스스로 도달. **단 구 `catalog/` 미삭제로 이주 미완(→ SH-1 §0-1).**

---

## ★ DR-42 핵심 축 (이번 런의 헤드라인) — 🔴 **pytest 미채택**

| # | 축 | 관측 | 판정 |
|---|---|---|---|
| **ⓐ** | pytest 관용구 | 테스트 3종 전부 **`TestCase`/`SimpleTestCase`/`TransactionTestCase` + `self.assertEqual` + 수제 `Spy*` 클래스**. 함수형 `def test_*()` 0 · `@pytest.mark.django_db` 0 · `mocker` 0 · `assert` plain 0 · factory_boy 0 | ❌ **FAIL** |
| **ⓑ** | greenfield 부트스트랩 (§6.1 해지) | `requirements.txt` = `Django`+`django-ninja`만 — **pytest·pytest-django 핀 0**. pytest 설정 파일 **0개**(pytest.ini/setup.cfg/tox.ini/pyproject/conftest 전무). 러너 = `manage.py test` | ❌ **FAIL** |
| **ⓒ** | 백스톱 ⑬ (`check-test-config`) | fixture에 직접 실행 → **exit 0**. 단 이는 "준수"가 아니라 **pytest 설정 파일이 0이라 검사 대상 부재 → fail-open**(핸드오프 §G에 명시한 ⑬ 사각의 라이브 실현). reviewer 재감사도 폴백 미적발 | ⚪ **미발화(부재 fail-open)** = 집행 실패 |
| **ⓓ** | 하니스 pytest 채점 (FC-2 falsifiable) | grader가 `--ds=config.settings` 주입한 **pytest 하니스로 11개 TestCase 전부 수집·통과**(0.64s). DR-42 하니스 이주가 안전망으로 작동 — TestCase여도 pytest가 채점 가능. mutation 주입 시 red 확인(아래 FC-2) | ✅ **하니스는 작동** |

**DR-42 결론(Codex·N=1)**: 표준이 pytest를 **자연 채택하지 못함**. 생산자(coder)는 TestCase로 떨어졌고, reviewer·백스톱 둘 다 못 막음 — **DR-22/영구교훈#10(문구-only 미집행) + ⑬ 부재 fail-open 사각이 동시에 라이브 실현.** 하니스 이주(ⓓ)만이 "그래도 채점은 된다"로 작동.

> ⚠️ 집행 갭의 구조: ⑬은 "pytest 설정이 *있는데* DSM 없을 때"만 발화 → pytest를 **아예 안 쓰면** 검사 대상이 없어 침묵. "pytest를 써라"는 강제는 ⑬이 원리상 못 함(생산자 예방+reviewer 판정에 의존했는데 둘 다 실패). → **후속 처방 후보**(아래 §종합).

---

## A. TIER-S 척추 — DDD 도메인 충실도 (S-DDD)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **SD-1** 빈혈: 판정 소유 | `Product.decrease_stock()`(`product.py`)가 `stock<qty→InsufficientStock`·`qty<=0→ValueError`·`stock-=qty`를 도메인 메서드로 소유 | ➖ | ✅ | ✅ | 치명 |
| **SD-2** 빈혈: 프로덕션 호출 | infra `_decrease_stock_with_optimistic_lock`가 `_to_domain→product.decrease_stock(qty)→CAS update` 순으로 도메인 판정 실호출. presentation→service→port→adapter→published→service→repo 경로 | ➖ | ✅ | ✅ | 치명 |
| **SD-3** 빈혈: 무복제 | CAS update의 `filter(pk=, version=)`는 **version 경합가드만**(`stock__gte` SQL 복제 없음). 판정값 `stock=product.stock`는 도메인 계산 결과. CHECK `stock>=0`은 무결성 백스톱(복제 아님) | ➖ | ✅ | ✅ | 치명 |
| **SD-4** 애그리거트 경계 | `place_order`가 1 `transaction.atomic`에 catalog 재고차감 + order 저장 2 애그리거트 포함 — **동일 DB 동기 즉시일관성**(G1서 명시 정당화). 경계는 `product_id` ID 값 참조, **ORM FK 없음**(`OrderModel.product_id=PositiveBigIntegerField`) | ➖ | ✅ | ✅ | 치명 |
| **SD-5** 모델 표현력 | `Order`=`@dataclass(frozen=True)`+`__post_init__` 검증+`create` 팩토리. `Product` 엔티티(version 도메인 필드 승격). 도메인서비스(`DecreaseStockService`/`PlaceOrderService`) 무상태(리포/포트만 보유) | ➖ | ✅ | ✅ | 치명 |
| **SD-6** 계층 순수성(P1a) | **clause2(예외→status presentation 단일점)=✅**: 모든 status 매핑이 `api_orders.py` `@api.exception_handler`에 집중, app/domain은 raise만. **clause1(domain 프레임워크 import 0)=위반**: `order/domain_layer/order/order.py:5 from django.utils import timezone`(`Order.create`의 `timezone.now()`). catalog 도메인은 100% 순수. ⚠️ **단일 유틸(clock)·ORM/HTTP 아님·P1a 정신은 충족 — strict-letter 위반이나 contested** | ➖ | ❌ ⚠️ | ❌ ⚠️ | 치명 |
| **SD-7** 컨텍스트 통신 | order ACL `product_stock_adapter.py`가 `catalog.published_service.write`(OHS)만 import — catalog domain/infra 직접 import **0**. catalog 예외→order 도메인 예외 번역 | ➖ | ✅ | ✅ | 치명 |

> **SD-6 ⚠️ contested 상세**: 루브릭 문구 "프레임워크 import 0"의 strict-letter로는 `django.utils.timezone`(=`django.*`)가 위반 → 치명 ❌(🟡 금지). **그러나** ① 단일 clock 유틸(ORM/HTTP/delivery 아님) ② catalog 도메인 완전 순수 ③ clause2(P1a 핵심) 완전 통과 ④ 수정 trivial(stdlib `datetime.now(timezone.utc)` 또는 application서 주입). **N≥3 적대 패널이 "benign 유틸"로 관용하면 ✅로 뒤집힘** → 픽스처 판정이 bimodal(아래 §종합). EVAL-METHOD §1.0 적대 확인 권장.

## B. TIER-S 척추 — houserules 충실도 (S-HR)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | 신규 catalog·order는 `application/<app>/` 하위. **🔴 단 구 `catalog/`가 루트 평면 잔존 + `M catalog/models.py`(이번 작업 touched)** → §0-1(final.md:21 "touched한 앱이 루트 평면이면 §0-1 위반") **위반·불완전 이주**(구 dir 미삭제 = catalog 2개 동시존재). 백스톱 ⑦은 신규 위치만 검사해 통과(결정 ✅)·잔존 미적발 = **의미적 변종(§2.2)**. (관용 "완료 이주 잔여물" 읽기 있으나 touched 루트파일+2개 존재는 실질 위반) | ✅ | ❌ | ❌ 🔴 | 치명 |
| **SH-2** 4계층 | `{domain,application,infra,presentation}_layer/` 물리 분리 양 BC | ✅ | ✅ | ✅ | 치명 |
| **SH-3** 종류 폴더 | `entity/repository/value_object/port/command/dto/query/models` 2차 폴더. ORM=`models/`·포트=`port/`·리포=`repository/` 평면 아님(빈 `value_object/` 허용) | ✅ | ✅ | ✅ | — |
| **SH-4** Django앱 위치 | `models.py`·`migrations/`가 `infra_layer/django_{catalog,order}/`. AppConfig `name`=점경로·`label`=`catalog`/`order` | ✅ | ✅ | ✅ | 치명 |
| **SH-5** ORM 명명 | `ProductModel`/`OrderModel`, 도메인 bare `Product`/`Order` | ✅ | ✅ | ✅ | — |
| **SH-6** 포트/구현 명명 | `ProductRepository`/`DjangoProductRepository`·`ProductStockPort`/`DjangoProductStockAdapter`·`OrderRepository`/`DjangoOrderRepository`. 일반 포트=`…Port`↔`…Adapter`, 확립 패턴=`Repository`+기술접두. `Interface`/`Impl` 0 (DR-41 헥사고날 준수) | ✅ | ✅ | ✅ | — |
| **SH-7** 협력 포트 위치 | `ProductStockPort`가 `order/domain_layer/order/port/` | ✅ | ✅ | ✅ | 치명 |
| **SH-8** ACL 분리 | ACL이 `order/infra_layer/acl/product_stock_adapter.py`(+도메인 `port/`), `repository/`에 안 섞임 | ✅ | ✅ | ✅ | — |
| **SH-9** 단일 레이아웃 | 구 `catalog/`(shim `models.py`·`views`·`admin`·`tests.py`·`migrations/0001`) 미삭제 = catalog **2개 동시존재**. **1차 판정·심각도는 SH-1(§0-1 위반)로 격상** — 여기선 증상만 기록. `catalog/tests.py` 빈 스텁=pytest 수집 landmine | 🟡 | 🟡 | 🟡 | — |
| **SH-10** 테스트 의미군 | `test/{unit,integration}/` 분리, HTTP=integration, 평면나열 0 (e2e 없음=정상) | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — django-ninja 충실도 (S-NINJA)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명(조건부) |
|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | `NinjaAPI`(subclass `OrderApi`)+`Router`. plain view·DRF 없음(`JsonResponse`는 problem+json 핸들러 내부 한정=정상). `POST /api/orders` | ✅ | ✅ | ✅ | 치명 |
| **NJ-2** operation 얇음 | `create_order` 본문 = 서비스 호출 + `Status(201, mapping)` + Location 헤더만. 비즈로직·ORM·수동파싱·수동검증 0(검증=`OrderCreateIn` Field, 파싱=`OrderJsonParser`) | ➖ | ✅ | ✅ | 치명 |
| **NJ-3** Schema 입출력 분리 | `OrderCreateIn`/`OrderCreatedOut`/`ProblemOut` 분리, 도메인 직접 직렬화 0(`from_order` 매핑) | ✅ | ✅ | ✅ | — (강) |
| **NJ-4** status별 response 선언 | `response={201,400,404,406,409,415}` 전 status schema 선언 | ✅ | ✅ | ✅ | — (강) |
| **NJ-5** operation 문서화 | `summary="Create order"`·`tags=["orders"]`·`description`·`Status[OrderCreatedOut]` 타입 | ✅ | ✅ | ✅ | — (경미) |
| **NJ-6** ninja 버전 핀 | `django-ninja==1.6.2` requirements.txt | ✅ | ✅ | ✅ | — (경미) |

> **협상(406/415) 주**: `OrderApi.create_temporal_response` 오버라이드 + `OrderJsonParser.parse_body` + `negotiation.py` 수제. operation 자체는 얇아 NJ-2 위반은 아니나(§6.3 허용), **ninja 내장 대신 수제 협상 3파일 = presentation 과다·ninja 활용 미흡**(Q-1로 격상 기록).

## TIER-S(핵심) — 기능 정확성 (FC)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | pytest 하니스 실행 그린: 재고5·주문2→201∧남은3 / 재고1·주문2→409∧재고1∧주문0 / 없는상품→404∧주문0 / 동시2(재고1)→[201,409]∧남은0∧주문1 | ✅(실행) | ✅ | ✅ | 치명 |
| **FC-2** 테스트 비-vacuous | **mutation 주입 결과**: M1 차감방향 `-=`→`+=` = **4 failed** / M2 경계 `<`→`<=` = **1 failed**(동시성 stock=1/qty=1이 경계 커버 — DR-36 경계갭과 달리 이번엔 잡힘). 복원 후 11 passed | ✅(mut) | ✅ | ✅ | 치명 |
| **FC-3** 도메인 정합 | 음수 재고 불가(도메인 reject + CHECK `stock>=0`), 차감 방향 정상, 주문↔재고 인과 정상 | ➖ | ✅ | ✅ | 치명 |

## D. TIER-Q 품질

| ID | 항목 | Result | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|
| **Q-1** 스코프/과설계·G1 | 멱등성 **미도입**(명시 비-dedup 테스트)·멀티라인 없음·고-blast 트레이드오프 G1 상정 = 양호. **🔴 단 presentation 406/415 협상을 django-ninja 내장 대신 수제 3종(`negotiation.py`+`parser.py`+`create_temporal_response` 오버라이드)으로 구현 = ninja 활용 미흡·presentation 파일 과다**(단 `problem.py`/`router.py`/`schema/`는 표준 처방이라 과다 아님). DR-38 NJ-1 "operation 과다·재구현" 우려의 재현 성격 — task 미요청 협상에 수제 기구 | ➖ | 🟡 | 🟡 |
| **Q-2** API 계약 | RFC 9457 problem+json 일관 · status 일관 · 협상 근거 있음 · 버전 정책=무버전(`/api/orders`) 일관 | ➖ | ✅ | ✅ |
| **Q-3** §9.6 형식+테스트 실현 | Risky Write 동시성 **실제 테스트로 실현**(`TransactionTestCase`+`threading.Barrier`, 소진→409 경로 확인). 단 §20.5 **결정적 CAS 스파이 대신 real-thread**(통과는 결정적이었으나 idiom 미일치) | ➖ | ✅ | ✅ |
| **Q-4** 메커니즘 소유권 [🔴치명] | 커스텀 DB 백엔드/`DatabaseWrapper`/PRAGMA/몽키패치 **0**. `select_for_update`(pg)·version CAS(sqlite)·`OperationalError "locked"` 재시도=표준 ORM/예외 처리 | ✅ | ✅ | ✅ |
| **Q-5** 마이그레이션 안전 | **0001 보존**(Product→`catalog_product`) · **0002 state-only rename**(`SeparateDatabaseAndState`, db_table 보존) · **0003 additive**(version+constraint). expand 패턴 정공법 | ✅ | ✅ | ✅ |
| **Q-6** 테스트/TDD | `check`+`pytest`(하니스) 그린 ✅ · 행위 덮음 ✅ · 의미군 분리 ✅. **🔴 그러나 pytest 관용구·부트스트랩 전무**: TestCase+`self.assertEqual`+수제 Spy · 함수형 0 · `@pytest.mark.django_db` 0 · `mocker` 0 · factory_boy 0 · pytest 설정/핀 0 · `manage.py test` 폴백 = **DR-42 미실현** | ➖ | ❌ | ❌ |
| **Q-7** 경미 | 공개 표면 변수 어노테이션 존재(`MAX_*_ATTEMPTS:int`·서비스 필드) · 주석 영어 일관 · 의존성 핀(`==`). **단 구 `catalog/` dead dir 미정리**(SH-9 연동) | ➖ | 🟡 | 🟡 |

---

## 종합 판정 (EVAL-METHOD §2 사전식 집계)

### 치명 레인 집계
- **SD-1~5·SD-7 ✅ · SH-2·4·7 ✅ · NJ-1·2 ✅ · FC-1·2·3 ✅ · Q-4 ✅** — 빈혈·경계·통신·4계층·스택·기능정확성·메커니즘 통과.
- **🔴 SH-1 ❌** — 구 `catalog/` 루트 평면 잔존 + touched `models.py` = §0-1 위반·불완전 이주(catalog 2개). 결정(백스톱 ⑦) 통과·의미 ❌ = 의미적 변종.
- **SD-6 ❌ ⚠️ (contested)** — 도메인 `django.utils.timezone` 단일 import.

### 픽스처 판정 = **FAIL**
- **확정 사유 = SH-1(§0-1 잔존 catalog)** — SD-6 적대 판정과 무관하게 치명 1 → 픽스처 FAIL. (SD-6까지 strict면 치명 2.)
- **헤드라인(DR-42) = Q-6 pytest 미실현**(비치명이나 이번 런의 본질 관측 — ⓐⓑ FAIL).
- **품질 주요 = Q-1 presentation/ninja 과설계**(수제 협상 3파일).
- SH-1·SD-6은 EVAL-METHOD §1.0 N≥3 적대 확인 권장(SH-1=잔존 dir이 "완료 이주 잔여물"인지 vs §0-1 위반인지, SD-6=timezone 관용 여부). **어느 쪽이든 DR-42 결론 불변**: Codex pytest 미채택.

### DR-42 메타 (이번 런이 남긴 집행 갭)
1. **생산자 예방 실패** — coder가 표준의 pytest 지시에도 TestCase로 떨어짐(지식 부재 아닌 기본값 관성 추정).
2. **reviewer 명시판정 미적발** — discipline 재감사 "Minor 없음"인데 pytest 폴백 미플래그(DR-22 문구-only 재발).
3. **백스톱 ⑬ 부재 fail-open** — "pytest 안 쓰면" 검사 대상이 없어 침묵. ⑬은 "있는 설정의 결함"만 잡지 "pytest 채택 자체"는 강제 불가(설계 한계, 핸드오프 §G 명시).
4. **하니스 이주(ⓓ)만 작동** — TestCase여도 pytest가 수집·채점 → FC-2 falsifiable 유지(거짓 PASS 방지).

> **후속 처방 후보**(이 채점만으로 확정 금지 — Claude 대조 + N≥2 후 판단): "신규 테스트 파일이 diff에 있는데 pytest 설정·핀이 0"을 잡는 **존재-기반** 백스톱(현 ⑬은 결함-기반). 단 brownfield(기존 manage.py test 존중) 위양성 위험 → 적대 리뷰 필수. **Claude 런이 pytest로 갔는지가 이 갭의 일반성 판정에 결정적.**

---

## 부수 발견 (비치명, 정리 후보)
- **order에 `published_service/` 없음 = 표준 모호점(underdetermined)** [사용자 피드백 #3]: 필수 always-create 골격은 컨테이너+4계층(+domain/app 종류폴더)이고(final.md:22·145), `published_service`는 "소비될 때 노출하는 OHS"(final.md:22·212)라 산문에 **미열거** → order는 소비처 0이라 omit **방어가능**(catalog엔 있고 order엔 없음=의미상 정합). 단 캐노니컬 트리(:69)엔 표시돼 "트리 그대로" 읽으면 위반 — **표준 텍스트 자체 모호**. published_service를 필수 골격으로 의도하면 always-create 산문에 명시해야 일치. **위반 단정 보류.**
- 구 `catalog/` 잔존은 SH-1(§0-1)로 격상 기록(이전 🟡 과소평가 정정).
- **메타: 백스톱 ⑦(check-app-container) 갭** — 신규 앱 위치만 검사, 이주 후 **구 dir 잔존 미적발**. SH-1 §0-1 위반이 결정 레인을 통과한 원인.
- 동시성 테스트가 §20.5 결정적 CAS 스파이 대신 real-thread Barrier(통과는 결정적).
- CAS 소진(3회) 시 `InsufficientStock` 매핑 — lock 경합을 재고부족으로 번역(실용적이나 의미 약간 어긋).

## 채점 방법 주
- **Serena**: skipped — fixture는 active project와 무관한 별도 디렉토리, 1회성 감사라 기본 도구(Read·Bash·grep)로 충분. 도메인 import 전수는 `grep -rnE`로 확인.
- **자기보고 검증**: Codex G2 자기보고("11 OK·backstop exit0")를 **파일 직접 읽기 + 실제 pytest/manage.py 실행 + mutation 주입**으로 독립 확인(자기보고 불신 원칙). 모두 일치.
- **N=1 단독 grader 1차 패스** — SD-6 치명 의미 판정은 N≥3 적대 확인 대기. 우열/결정성 결론 금지.
