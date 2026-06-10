# lastlive-codex 채점 결과 (진행분·감수 미완 기준)

> **방법** EVAL-METHOD v3(+§1.1.T·§4.3.1) · **채점일** 2026-06-10 · **픽스처** `~/Desktop/dddjango-lastlive-codex`(baseline `c8f5be3` = `catalog.Product` 평면앱 + ninja/ninja-extra·**테스트도구 0·pytest 설정 없음** Tier-1 부트스트랩 관측 baseline) · **런타임** Codex(plugin 캐시 동기 = 소스 최신·캐시 skills byte-id·**plugin 1.11.0**·**백스톱 16종**·DR-55 ⑯ HttpError·DR-56 ④ 외래port·SH-7 4층 반영) · **N** 1 · **태스크** "재고 부족 409·충분 시 차감 주문 생성 API"(ptcat/ptboot/nj7live/finallive와 **verbatim 동일 프롬프트**) · **게이트** 배치③설계자결정 · **external API**(scope `:9`) · 415 함수형 Router 격리(DR-48 외부공개 C정책) · G1 멱등성 미적용(scope 제외) · 동시성 CAS 채택 · **G2 감수 미완**(토큰 소진) · **범례** ✅PASS ❌FAIL 🟡WEAK/경미 ⏸️보류 ➖N/A
> **⚠️ 단서 (정직)**:
> - **미완성 런**: 사용자 보고 = Codex 토큰 부족으로 완성 못 함. 실측 = **코드+테스트 산출물은 완성**(pytest 25 passed·EP 계약 전수·백스톱 16 exit0), 다만 `.dddjango/`에 **discipline-reviewer 감수 리포트 부재**(scope.md·design-spec.md만) → G2 감수 단계서 중단. 채점은 *저장 fixture 정적 측정*(§4.2)으로 가능하나, **G2 게이트 자연 발화(§4.3)는 미검증** — 백스톱은 조정자가 *사후 직접 실행*(정적 대리).
> - `N_grader`=**1(조정자 직접 검증)**, 의미 레인 blind grader 미투입(라이브 단일 채점). 자기보고(코디네이터) 불신 — 백스톱16·pytest·FC-2 mutation·EP probe 전부 조정자 직접 실행.
> - **N=1·단일 런타임**(claude 런은 사용자 별도 드라이브). **게이트 조건 finallive와 상이**(finallive=내부전용·클래스 컨트롤러 / 이번=external·415 함수형 Router 격리) → finallive와 **직접 우열 비교 금지**.
> - **SH-7 정위치는 이번 1회 관측** — DR-56 처방 자연 발화에 우호적이나 N=1·런간 비결정 배제 못 함("처방이 야기" 단정 금지).
> **🔬 바이트코드 위생**: 모든 동적 측정(pytest·FC-2 mutation·EP probe)은 `.pyc`·`__pycache__` 완전 purge 후 실측.
> **fixture 도구 환경**(§1.1.T): **env**(채점 전)=테스트도구 0(baseline `c8f5be3`)·조정자 추가 도구 **0**(Codex가 `.venv` 직접 부트스트랩) · **produced**=Codex가 `requirements.txt`에 `pytest`·`pytest-django`·`pytest-mock`·`factory_boy` 추가+핀 + `pyproject.toml` `DJANGO_SETTINGS_MODULE` · **used**=`mocker`(e2e)·`objects.create`(factory_boy 핀했으나 미사용=§9.1 정당)

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | **catalog = 판정 소유 분해**(MQ0=Y[baseline catalog `D`+application/catalog 재생성]·MQ1=Y[`product.py:20` `deduct_stock` 재고판정 소유]·MQ2=N) + **order = 신규 BC** → 양 BC §0 전부 강제 |
| ② 치명 게이트 | **FAIL 0건** — SD-1~7·FC-1~3·SH-1·2·3·4·7·NJ-1·2·Q-4 전부 PASS(의미적 변종 포함) |
| ②.5 실질성 관문 | 통과 — 도메인 판정 실코드 채움(`product.py:20`·`order.py:19`)·테스트 non-vacuous(mutation red 3종)·빈 골격 degenerate 없음 |
| ③ 비치명·의미변종 | **의미적 변종 0건**(`[결정PASS∧의미FAIL]` 빔) — WEAK 0 |
| ④ TIER-Q 등급 | **품질 상**(WEAK 0·FAIL 0·강 NJ-3/4/7 전부 PASS) |

**한 줄 요지**: **종합 = 정적 준수·품질 상**. finallive-codex(SH-7 치명 FAIL)와 **정반대로 SH-7 협력 포트가 `domain_layer/order/port/` 정위치** — DR-56 처방 자연 발화에 우호적(N=1). EP-1 깨진본문 400 problem+json(HttpError 핸들러)·FC-2 경계(stock==quantity) 보유·동시성 oversell 방지·백스톱 16 exit0. **단 G2 감수 미완**(자연 게이트 발화 미검증·조정자 사후 백스톱으로 정적 대리).

**2차원 라벨**: (정적: **준수** — 치명 0·품질 상) × (라이브: **부분** — 백스톱16 조정자 사후 exit0·FC-2 mutation red·EP probe 전수·**단 G2 감수 자연 발화 미관측**[토큰 중단]) · `폴더 동작`: 미검증(재빌드 아님·신규만) · `에러경로 계약`: **관측**(EP-1~4 전수 problem+json) · `성공경로`: **정상**(클린빌드 201∧pytest 25 green)

---

## A. TIER-S 척추 — S-DDD

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SD-1 | 빈혈: 판정 소유 | ddd §3.2 | `product.py:20-26` `deduct_stock`(`quantity<=0` raise·`stock<quantity`→`InsufficientStock`·`stock-=quantity` 차감)·`order.py:19-26` `Order.create`(`product_id>0`·`quantity>0` 불변식)·재고판정 도메인 소유 | ➖ | ✅ | ✅ | ✅ |
| SD-2 | 빈혈: 프로덕션 호출 | §3.2·3.6 | `create_order_command.py:61-76` `_try_create_order`(port.deduct→`Order.create`→repository.save·atomic)·`write.py:16-21` `deduct_product_stock`(get→`deduct_stock`→save)·죽은코드 아님 | ➖ | ✅ | ✅ | ✅ |
| SD-3 | 빈혈: 무복제 | §3.2 | `product_repository.py:30-39`(catalog infra) `filter(id=,version=).update(stock=,version=F+1)` version CAS만·판정 SQL(`stock__gte=`) 복제 0(check-anemic-sql-guard exit0) | ✅ | ✅ | ✅ | ✅ |
| SD-4 | 도메인 이벤트 | ddd §3.5 | 이벤트 미발명(슬라이스 범위·`event/` 빈 폴더 정당)·과설계 없음 | ➖ | ✅ | ✅ | ✅ |
| SD-5 | 값객체/식별자 | ddd §3.4 | `Order.product_id:int` 스칼라 식별자(FK 아님)·`value_object/` 빈 폴더(범위) | ➖ | ✅ | ✅ | ✅ |
| SD-6 | 계층 순수성 | ninja §2.2 | domain/application HTTP 변환 0(check-error-centralization application_layer exit0)·`create_order_command`은 도메인 예외(`StockConflict`→`StockContention`) raise만·status:int 객체 흐름 없음·HTTP는 `config/api.py`·presentation 중앙화 | ✅ | ✅ | ✅ | ✅ |
| SD-7 | 컨텍스트 통신 | ddd §2 | order가 catalog를 `published_service.write.deduct_product_stock`로만 소비(OHS)·ACL `catalog_product_stock_adapter.py:15-26`(`ProductStockPort` 구현·catalog published 예외→order 도메인 예외 번역)·catalog `domain_layer`/`infra_layer` 직접 import 0(check-context-isolation exit0) | ✅ | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SH-1 | application 컨테이너 | hr §0-1 | `application/order/`·`application/catalog/`(루트 평면앱 catalog `D` 삭제·잔재 0·check-app-container exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-2 | 4계층 물리분리 | ddd §632 | 양 BC `{domain,application,infra,presentation}_layer/` 존재(check-layer-skeleton exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-3 | 종류 2차 폴더 | ddd §632-(2) | order domain=`entity·value_object·repository·port·domain_service·event·specification`·application=`command·dto·handler·query·service`·presentation=`api·schema` 전부 디렉토리 유지 | ✅ | ✅ | ✅ | ✅ |
| SH-4 | Django앱 위치 | hr §0 | `infra_layer/django_order/models/order_model.py`·`django_catalog/models/product_model.py`·app 루트에 `models.py` 0·label 보존(catalog/order)(check-structure 골격 충족) | ✅ | ✅ | ✅ | ✅ |
| SH-5 | ORM/도메인 명명 | hr §6.3 | ORM=`ProductModel`·`OrderModel`(`<Name>Model`)·도메인=`Product`·`Order`(bare) | ➖ | ✅ | ✅ | ✅ |
| SH-6 | 포트/어댑터 명명 | DR-41 §4 | `ProductStockPort`(`…Port`)·`CatalogProductStockAdapter`(`…Adapter`)·`DjangoProductRepository`(Repository) | ➖ | ✅ | ✅ | — |
| SH-7 | **협력 포트 위치** | hr §2·§3 | **`application/order/domain_layer/order/port/product_stock_port.py`(ABC)** ← **domain_layer 정위치**(`find -type d -name port` 부모=domain_layer·check-layer-skeleton 외래port exit0)·ACL 구현은 `infra_layer/acl/` | ✅ | ✅ | ✅ | ✅ |
| SH-8 | published 표면 | ddd §2 | `application/catalog/published_service/write.py`·`exception.py` 비어있지 않음(OHS 실체)·order는 이것만 import | ➖ | ✅ | ✅ | — |
| SH-9 | 단일 레이아웃 | hr §0 | 양 BC `test/`만(`tests/` 공존 0)·`src`+`apps` 공존 0 | ✅ | ✅ | ✅ | — |
| SH-10 | 공개표면 어노테이션 | DR-39 §4.1 | 모듈 상수 어노테이션(`CREATED_STATUS:str`·`MAX_PRODUCT_ID:int` 등)(check-public-surface-annotation exit0) | ➖ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA  *(HTTP operation 존재 → NJ-1·2 치명 적용)*

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| NJ-1 | API 스택 | ninja §2.1 | 단일 `NinjaExtraAPI`(`config/api.py:24`)·`/api/` 마운트·**함수형 `Router`+`@router.post`(`api_orders.py:24,58`)는 415 외부 계약 격리 예외**(design-spec `:77·:309·:328` 명시·DR-48 외부공개 C정책·EVAL §1.1 "415 격리=PASS")·`JsonResponse`/DRF 0 | ✅ | ✅ | ✅ | ✅ |
| NJ-2 | 415·raw 파싱 금지 | §6.3 | `add_decorator(enforce_json_content_type, mode="view")`(`api_orders.py:55`·DR-35 데코레이터 레시피)·payload=`CreateOrderIn` ninja 스키마·`json.loads`/`request.body` 수제 파싱 0(`:72`) | ✅ | ✅ | ✅ | ✅ |
| NJ-3 | 단일 변환점(강) | §6.2 | 전 오류 `config/problem.py:problem_response` 단일 헬퍼·`application/problem+json`·핸들러 외 raw 응답 0 | ➖ | ✅ | ✅ | —(강) |
| NJ-4 | status별 response 선언(강) | §2.2·§8 | `api_orders.py:60-68` `response={201:CreateOrderOut,400/404/409/415/422/503:ProblemOut}` 다중 status 선언(`openapi_extra` 아님) | ✅ | ✅ | ✅ | —(강) |
| NJ-5 | 버전/하위호환 | api §7 | URL 버저닝 `/api/v1/orders`(design-spec §4)·이전 버전 없음 | ➖ | ✅ | ✅ | — |
| NJ-6 | 멱등성 표기 | api §13 | `Idempotency-Key` 미수용 명시(scope 제외·G1 선택1)·죽은 멱등 코드 0 | ➖ | ✅ | ✅ | — |
| NJ-7 | 오류 변환 완전성(catch-all, 강) | §6.2 | **`config/api.py:137` `@api.exception_handler(Exception)` catch-all**(미식별→500 problem+json)·`:59` `@api.exception_handler(HttpError)`(깨진본문 400)·bare `raise exc` 0·단일변환점 우회 0 | ✅ | ✅ | ✅ | —(강) |

## TIER-S(핵심) — FC

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| FC-1 | 골든 오라클 | §1.4 | 조정자 직접 probe(EP probe 스크립트·`.venv` 실측): 재고부족(stock=1,qty=5)→**409**·충분(stock=10,qty=3)→**201**·**경계(stock=2,qty=2)→201·stock=0**(`test_..exact_stock:97`)·초과→201 decrement — 골든 행위 전 케이스 일치 | ✅ | ✅ | ✅ | ✅ |
| FC-2 | mutation | §1.4 | 주입 사이트=`product.py:23` `deduct_stock` 판정. **3종 전부 red**: ①판정경계(`<`→`<=`)=2 failed ②차감부호(`-=`→`+=`)=4 failed ③status매핑(409→200)=2 failed → red율 100%·테스트 non-vacuous | ✅ | ✅ | ✅ | ✅ |
| FC-3 | 도메인 정합 | §1.4 | `deduct_stock` 음수재고 방지(`stock<quantity` 차단·`stock>=0` DB constraint backstop)·차감 정방향·인과 정상·oversell 방지(`test_concurrent..:335` [201,409]·stock=0) | ➖ | ✅ | ✅ | ✅ |

## C. 기존규약 마스크 (적용 메모)

- **런 변경 집합**: baseline `c8f5be3` 대비 `git diff HEAD` ∪ untracked. catalog 루트 평면앱 `D`(삭제)·`application/` 전체 untracked 신규.
- **MQ0**: **Y** — baseline `catalog/`(루트) git `D` 삭제 + `application/catalog/` 재생성(삭제-후-재생성 = 판정 적재 후보).
- **MQ1**: **Y** — `application/catalog/domain_layer/product/product.py:20-26` `deduct_stock`에 재고 판정 분기(`stock<quantity` raise)·불변식 메서드 존재.
- **MQ2**: **N** — catalog가 재고 판정 소유(단순 데이터소스 아님).
- **판정**: catalog = **판정 소유 분해** → `application/catalog/` 위치 + 4계층 + 판정 실코드(`product.py:20`)·published_service OHS(전부 충족). order = 신규 BC → §0 전부 강제. **양 BC SH-1·2·3·4·7 전부 PASS**(finallive-codex와 달리 SH-7도 정위치).

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| Q-1 | 스코프/과설계·G1 | ddd §6.8·hr §1.1 | 멱등성 미발명(scope 제외·G1 선택1 준수·`design-spec §5` "Not applied")·멀티라인/합산 0·고-blast(동시성)는 Risky Write §9.6 CAS로 G1 상정 | ➖ | ✅ | ✅ |
| Q-2 | API 계약 | api §4~14 | RFC 9457 problem(`problem.py:20` type/title/status/detail/instance)·`application/problem+json`·`Retry-After`/`retryable` 확장(`api.py:124`)·URL 버저닝 | ➖ | ✅ | ✅ |
| Q-3 | §9.6 형식+테스트 | db §9.6·test §20.5 | Risky Write 6요소(트랜잭션 owner·CAS locking·rule ownership·멱등성 N/A·side-effect·isolation/retry)(`design-spec:197-208`)·version CAS+재시도10(`create_order_command.py:46-59`)·소진→`StockContention`→503·oversell 동시성 테스트(`:335` transaction=True) | ➖ | ✅ | ✅ |
| Q-4 | 메커니즘 소유권 **[🔴치명]** | db §9.5·16.4 | 커스텀 DB백엔드/PRAGMA/몽키패치 0·표준 ORM `version`/CAS만(`product_repository.py:30`)(check-mechanism-ownership exit0)·`select_for_update` 의존 금지 명시(`design-spec:202`) | ✅ | ✅ | ✅ |
| Q-5 | 마이그레이션 안전 | db §11 | catalog `0001`(name="Product")+`0002` version expand+stock constraint·**`db_table="catalog_product"` 보존·`label="catalog"` 보존·state-only rename(`design-spec:172,194`)·`makemigrations --check` No changes**·order `0001` 신규앱 정당(`order_order`)·backfill/constraint rollout 명시(`:188-195`). 0001 byte 비동일은 포매팅(따옴표)·이력 정합 무해 | ➖ | ✅ | ✅ |
| Q-6 | 테스트 도구 | test §20 | (설치∧핀) `requirements.txt` pytest·pytest-django·pytest-mock·factory_boy 핀(produced)·러너=**pytest**(manage.py test 아님·`DJANGO_SETTINGS_MODULE` pyproject)·used=`mocker`(e2e 500/503 스파이)·`objects.create`(factory_boy 핀했으나 미사용=§9.1 비-blanket 정당) | ✅ | ✅ | ✅ |
| Q-7 | 의존성 핀 | hr §1.1 | requirements 전 항목 `==` 핀(Django·ninja·ninja-extra·테스트 4종) | ➖ | ✅ | ✅ |

## 의미적 변종 / backstop-blind 메타

- **의미적 변종 0건**: `[결정 PASS ∧ 의미 FAIL]` 칸 없음 — 백스톱 16종 exit0과 의미 레인 코드 정독 PASS가 전 차원 일치.
- **백스톱 blind-spot 점검**: ④ check-layer-skeleton은 폴더명 `port` 직격만 봄(개명 변종 못 봄) → 의미 정독으로 `product_stock_port.py`가 진짜 협력 포트 ABC임 확인(SH-7 의미 PASS). ⑯ check-catch-all-handler는 텍스트 계약(HttpError 핸들러 존재)만 → EP probe로 깨진본문 400 problem+json 실측 교차확인.
- **자기보고 불신 집행**: Codex e2e(`test_create_order_api.py` 19테스트)가 EP 전수 주장하나, 조정자가 **독립 probe**(별도 스크립트)로 EP-1~4 직접 두드려 status·content-type 실측 + FC-2 mutation으로 vacuous 아님 검증.

## 9.5 에러 경로 라이브 관측 (§4.3.1)

| 키 | 관측 status | content-type | 화이트리스트 | 판정 |
|---|---|---|---|---|
| **EP-1 깨진 본문** | **400** | `application/problem+json` | {400} | ✅ — 절단 JSON `{"product_id":1,"quantity":` → ninja 1.6.2 `HttpError(400)` → `@api.exception_handler(HttpError)`(`api.py:59` status==400 분기) → problem+json. (DR-55가 막으려던 EP-1 흠 부재 — HttpError 핸들러 작동) |
| **EP-2 무효 입력** | **422** | `application/problem+json` | {422,400} | ✅ — `quantity:0` → `InvalidOrderQuantity` → 422 problem+json(`api.py:91`) |
| **EP-3 transient 소진** | **503** | `application/problem+json` | {503,409} | ✅ — CAS 소진 `StockContention`→503+`retryable:true`+`Retry-After`(`api.py:124`)·도메인경로 검증(§4.3.1 EP-3 (ii) ACL 도메인번역 어댑터)·비-retryable OperationalError는 re-raise→500(`create_order_command.py:53`)·과잉매핑 0(check-transient-overmapping exit0) |
| **EP-4 재고 부족** | **409** | `application/problem+json` | {409} | ✅ — stock<qty → `InsufficientStock`→409(`api.py:113`)·FC-1 골든과 교차 일치 |

> **EP probe 환경**: Django test `Client`(testserver 자동 허용)·`.pyc` purge 후 실측·status 추론 금지(전부 실제 응답 코드).

## 조정자 노트

1. **종합 = 정적 준수·품질 상**. 치명 게이트 전부 통과·의미변종 0·품질 WEAK 0. 산출물(코드 26파일·테스트 5종·pytest 25 green) 완성도 높음.
2. **SH-7 정위치 = 이번 채점의 핵심 발견**. finallive-codex(`application_layer/place_order/port/` 오배치·치명 FAIL·DR-56 처방 동기)와 **정반대로** `domain_layer/order/port/product_stock_port.py` 정위치. design-spec이 명시적으로 협력 포트를 도메인에 두고(§3·§6 트리) ACL 어댑터를 `infra_layer/acl/`에 분리 → **DR-56 처방(architect 재분류 금지·reviewer §2 앵커·④ 외래port 백스톱·표준 §3:178) 자연 발화에 우호적**. 단 **N=1·런간 비결정 배제 못 함** — finallive 시점에도 architect 분류가 비결정(P4③)이었으므로 "처방이 야기" 단정 금지. 백스톱 ④는 정위치라 발화 불필요(exit0 = 위반 없음 정상).
3. **EP-1(DR-55) 흠 부재**. Codex는 finallive에서도 EP-1 양호(HttpError 핸들러)였고 이번도 `@api.exception_handler(HttpError)` + `JSONDecodeError` 이중 안전망 + catch-all로 완비. DR-55가 *Claude* 흠을 겨눈 처방이라 Codex엔 원래 비해당이나, 깨진본문 400 problem+json 라이브 실측으로 계약 확인.
4. **DR-48(415 클래스 컨트롤러) 정확 적용**. external API + 415 계약 → 함수형 Router를 *이 엔드포인트만* 격리(단일 NinjaExtraAPI 유지). architect가 design-spec에 격리 근거를 명문(`:77·:309·:328`) → NJ-1 PASS(415 격리 예외). finallive(내부전용)와 게이트 조건이 달라 클래스/함수형이 갈린 것이지 회귀 아님.
5. **미완성(감수 미완)의 채점 영향**: discipline-reviewer 리포트 부재라 **G2 게이트 자연 발화(§4.3 라이브 완료)는 미검증**. 조정자가 백스톱 16종을 사후 직접 실행(전부 exit0)했으나 이는 *정적 대리*다. 단 SH-7은 G1(architect) 산출이라 정위치가 자연 관측됨. 코드/테스트는 완성이라 정적 준수(§4.2)·품질 채점은 유효.
6. **N=1·우열 금지**: lastlive-claude 런은 사용자가 별도 드라이브(미채점). finallive와 게이트 조건 상이(internal 클래스 ↔ external 415 함수형)라 런타임/처방 효과 직접 비교 불가.

## 부록 — 비처방 관찰

- `api_orders.py:72` `-> Status` 반환(ninja `Status(201, ...)`): DR-52/53 동시성 사냥서 비결함 확정된 패턴·기능 정상(pytest 201 green).
- factory_boy 핀했으나 미사용(헬퍼 `create_product`=`objects.create`): §9.1 non-blanket·이름 부재 흠 아님·과-핀은 Q-7 영향 없음.
- 1h 미만 추정 런타임(감수 전 중단)·telemetry 미수집(미완성).
