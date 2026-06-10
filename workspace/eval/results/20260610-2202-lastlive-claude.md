# lastlive-claude 채점 결과 [사후정정 2026-06-10: 초판 "테스트 0·미완성"은 오채점 — 실측 = 테스트 33 그린·정적 준수·품질 상]

> **방법** EVAL-METHOD v3(+§1.1.T·§4.3.1) · **채점일** 2026-06-10 · **픽스처** `~/Desktop/dddjango-lastlive-claude`(baseline `832d3be` = `catalog.Product` 평면앱 + ninja/ninja-extra·**테스트도구 0·pytest 설정 없음** Tier-1 부트스트랩 관측 baseline) · **런타임** Claude(plugin 캐시 동기 = 소스 배포 마스터 byte-id·**plugin 1.11.0**·**백스톱 16종**·DR-55 ⑯ HttpError·DR-56 SH-7 4층 반영) · **N** 1 · **태스크** "재고 부족 409·충분 시 차감 주문 생성 API"(ptcat/ptboot/nj7live/finallive와 **verbatim 동일 프롬프트**) · **게이트** 배치③설계자결정 · **external API**(`scope §무엇`) · 클래스 컨트롤러(`@api_controller`) · G1 동시성 CAS 채택(Y-1)·멱등성 미적용 · **G2 통과 기록 미확인**[사후정정 — 초판 "G2 미도달(테스트 단계 중단)"은 오판의 파생이라 철회. 테스트는 33 그린·런 자신이 21:40 pytest 실행. 단 커밋 0·게이트 배너 기록이 픽스처에 안 남아 G2 도달 자체는 픽스처만으론 미확인] · **범례** ✅PASS ❌FAIL 🟡WEAK/경미 ⏸️보류/측정불가 ➖N/A
> **🔴 [사후정정 2026-06-10 22:37 — 초판 채점은 오채점이다. 아래 단서 블록의 "테스트 0·테스트도구 0·미완성·보류" 판정을 전부 철회한다.]**
> - **실측(정정 채점·런-정지 확인 후)**: 테스트 모듈 **7개**+factories 2(`*_test.py` 접미 관례)·`pytest --collect-only -q` = **33 tests collected**·전수 **33 passed**(0.34s)·**Tier-1 4종 설치됨**(pytest 8.4.2·pytest-django 4.11.1·pytest-mock 3.15.1·factory_boy 3.3.3 — `.venv/bin/pytest` mtime 20:56:25 = *런 중 부트스트랩*)·`requirements-dev.txt` 핀 4종·`pyproject.toml [tool.pytest.ini_options]`에 `DJANGO_SETTINGS_MODULE` 완비·**런 자신이 21:40에 pytest 실행**(`.pytest_cache/v/cache/nodeids` 21:40:10)·21:40 이후 픽스처 변경 0 → 초판(22:02)은 완결·정지 상태를 보고도 부재로 단정했다.
> - **FC-2 mutation(정정 실측)**: ②경계(`<`→`<=`) → **2 red**(단위 `test_stock_equals_quantity_deducts_to_zero` + 인수 `test_stock_equals_quantity_returns_201_and_deducts_to_zero`) / ①차감 방향(`-`→`+`) → **13 red** / 복원 후 **33 passed** → **FC-2 PASS**(경계 양 레벨 보유 = FC-2 (b)+(d) 처방 효과·finallive와 동형).
> - **오판 기전(박제)**: 초판의 부재 단정을 뒷받침하는 측정 명령(`pytest --collect-only`·find·pip list)이 transcript에서 발견되지 않음 — **측정 없이(또는 비기록 약식 확인으로) 부재를 단정**. 유력 혼동 요인 = 직전 채점한 Codex 픽스처는 `test_*.py` **접두** 관례·Claude는 `*_test.py` **접미** 관례(+ "도구 0"은 `requirements.txt`만 보고 `requirements-dev.txt`를 놓침). 이 사고로 EVAL-METHOD에 **채점 가드 3종**(수집 오라클 의무·부정 단정 출력 인용 의무·런-정지 확인) 신설.
> - **정정 종합 = ✅ 정적 준수(치명 0)·품질 상.** TDD 순서도 정상이었다(러너 준비 20:56 → 인수 테스트 21:01 → 단위·동시성·경계 ~21:30 — mtime 근거). 아래 본문 중 갱신된 칸은 `[사후정정]`으로 표기.
>
> **⚠️ 단서 (정직)**:
> - ~~**미완성 런 (Codex보다 덜 진행)**: 사용자 보고 = Claude "끝났어". 실측 = **코드 산출물은 완성**(EP probe 전수 problem+json·백스톱 16 exit0·Django 부팅), **그러나 테스트 파일 0개·테스트도구 0**(requirements baseline 그대로) → **TDD 코더 단계 전/중 중단**(acceptance test·unit test 미작성). `.dddjango/`에 감수 리포트도 부재. → **FC-2 mutation·Q-6은 테스트 부재로 측정 불가**, 종합 **정적 준수 자격 미달 = 보류(미완성)** — *코드 결함이 아니라 런 중단*.~~ **[철회 — 위 사후정정 참조. 원문은 오판 기록 보존용으로만 남긴다.]**
> - `N_grader`=**1(조정자 직접 검증)**, blind grader 미투입. 자기보고 불신 — 백스톱16·EP probe(DiscoverRunner standalone)·표준 텍스트 대조 전부 조정자 직접 실행.
> - **N=1·단일 런타임**(Codex 런은 별도 채점·`20260610-2130-lastlive-codex.md`). **게이트 조건·설계 분기 상이**(Codex=catalog 판정소유 분해·함수형 415 격리 / Claude=catalog 데이터소스·재고판정 order 소유·클래스 컨트롤러) → **우열 비교 금지**. 재고 판정 소유는 ddd §648 허용 분기라 **underdetermined**.
> **🔬 바이트코드 위생**: 모든 동적 측정(EP probe)은 `.pyc`·`__pycache__` 완전 purge 후 실측.
> **fixture 도구 환경**(§1.1.T) **[사후정정]**: **env**(런 전)=테스트도구 0(baseline `832d3be`) · **produced**=**Tier-1 4종**(pytest 8.4.2·pytest-django 4.11.1·pytest-mock 3.15.1·factory_boy 3.3.3 — `requirements-dev.txt` `==` 핀 + `pyproject.toml` DJANGO_SETTINGS_MODULE, *런이 직접 부트스트랩* 20:56) · **used**=**33 tests**·`mocker`(pytest-mock)·factory_boy 팩토리 2종(order/product) · 조정자 추가 도구 **0**(오염 없음). ~~env=도구0·produced=0·used=0~~ 철회.

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | **catalog = 데이터소스**(MQ0=Y[catalog `R` git rename 이주]·**MQ1=N**[재고 판정을 order `StockDeductionService`가 소유·catalog Product는 빈 골격]·MQ2=Y) + **order = 신규 BC**(재고 판정 소유) → 양 BC §0 강제·catalog 판정 실내용 면제(§648-(2)) |
| ② 치명 게이트 | **[사후정정] ✅ FAIL 0건** — SD-1~7·SH-1·2·3·4·**7**·NJ-1·2·Q-4·**FC-1·2·3 전부 PASS**(FC-2 mutation red 실측: 경계 2 red·방향 13 red·복원 33 passed) |
| ②.5 실질성 관문 | 도메인 판정 실코드 채움(`stock_deduction_service.py:13` non-trivial)·빈 골격 degenerate 없음·**[사후정정] 테스트 non-vacuous 입증**(33 그린·mutation red) |
| ③ 비치명·의미변종 | 의미적 변종 0건 · NJ-1 🟡 경미(에러 응답 `JsonResponse`·content-type은 problem+json 정확) · NJ-5 🟡 경미(/v1 부재) |
| ④ TIER-Q 등급 | **[사후정정] 품질 상**(FAIL 0·WEAK = NJ-1·NJ-5 경미 2건) — FC-2 (b)+(d) 처방효과·SH-7 정위치·EP-1 수복·동시성 5경계 결정적 주입 테스트·Tier-1 부트스트랩 §2.1 완전 |

**한 줄 요지 [사후정정]**: **✅ 종합 = 정적 준수(치명 0)·품질 상** — SH-7 포트 정위치·SD-7 ACL 패턴 표준 정확·**🎯 EP-1 깨진본문 400 problem+json = DR-55 처방 작동**(finallive 흠 수복)·테스트 33 그린·FC-2 mutation red(경계 양 레벨)·동시성·transient 5경계를 결정적 주입으로 행사(503+Retry-After·영구장애 500 과잉매핑 0)·Tier-1 러너 부트스트랩 완전(§2.1 핀). ~~보류(미완성)~~ 철회 — 초판 "테스트 0"은 오채점이었다.

**2차원 라벨 [사후정정]**: (정적: **준수** — 치명 0·품질 상) × (라이브: **발화/관측** — 33 passed·FC-2 mutation red·FC-1 골든·EP probe 전수 problem+json·백스톱16 조정자 사후 exit0·단 G2 게이트 통과 기록은 픽스처에 안 남아 미확인[커밋 0]) · `에러경로 계약`: **관측**(EP-1~4 전수 problem+json·**DR-55 EP-1 수복**·EP-3 테스트 주입 행사) · `성공경로`: **정상**(EP probe 201·차감 10→7)

---

## A. TIER-S 척추 — S-DDD

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SD-1 | 빈혈: 판정 소유 | ddd §3.2·§3.5 | 재고 판정(`stock>=quantity`)·차감 계산을 **order 도메인 서비스** `stock_deduction_service.py:13-23` `deduct`(new_stock<0→`InsufficientStock`)가 소유·SQL/ORM에 판정 0(빈혈 아님). catalog Product 빈 골격은 §648-(2) 데이터소스 정당(판정 실내용 면제). **재고판정 order 소유는 §648-(2) 허용 분기**(catalog 소유와 둘 다 방어 가능·underdetermined) | ➖ | ✅ | ✅ | ✅ |
| SD-2 | 빈혈: 프로덕션 호출 | §3.2·3.6 | `place_order_command.py:58` `_stock_deduction.deduct(...)` 프로덕션 경로 실호출·ACL `get_stock`→도메인 판정→`set_stock` CAS·죽은코드 아님 | ➖ | ✅ | ✅ | ✅ |
| SD-3 | 빈혈: 무복제 | §3.2 | `product_stock_adapter.py:37-39` `filter(id=,version=).update(stock=,version=F+1)` version CAS만·판정 SQL(`stock__gte=`) 복제 0(check-anemic-sql-guard exit0)·판정은 도메인이 계산한 결과값만 저장 | ✅ | ✅ | ✅ | ✅ |
| SD-4 | 도메인 이벤트 | ddd §3.5 | 이벤트 미발명(동기 ACL·즉시 일관성·`event/` 빈 폴더 정당·design-spec §1.5 근거) | ➖ | ✅ | ✅ | ✅ |
| SD-5 | 값객체/식별자 | ddd §3.4 | `ProductStockSnapshot` 값객체(`value_object/`)·`Order.product_id:int` 스칼라(FK 아님) | ➖ | ✅ | ✅ | ✅ |
| SD-6 | 계층 순수성 | ninja §2.2 | domain/application HTTP 변환 0(check-error-centralization exit0)·`place_order_command`은 도메인 예외(`StockContentionExhausted`) raise만·HTTP는 `config/api.py` 중앙 | ✅ | ✅ | ✅ | ✅ |
| SD-7 | 컨텍스트 통신 | hr §2·ddd §648 | **ACL 패턴 표준 정확**(hr §2:144): catalog OHS 미노출(데이터소스)+단일 트랜잭션·CAS 행잠금 → ACL 명시·`product_stock_adapter.py`(infra_layer/acl)가 catalog `ProductModel` 직접·**업스트림 모델을 ACL에 격리**·order 도메인은 `ProductStockPort`(domain_layer/port)로만 의존·**ACL 밖(presentation·application·domain) catalog import 0**(grep)·`ProductNotFound` 번역(전수). published_service 빈 골격은 OHS 미경유(ACL 경로)라 정당 | ✅ | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SH-1 | application 컨테이너 | hr §0-1 | `application/order/`·`application/catalog/`(루트 평면앱 catalog `R` rename 이주·잔재 0·check-app-container exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-2 | 4계층 물리분리 | ddd §632 | 양 BC `{domain,application,infra,presentation}_layer/`(check-layer-skeleton exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-3 | 종류 2차 폴더 | ddd §632-(2) | order domain=`entity·value_object·repository·port·domain_service·event·specification`·application=`command·dto·handler·query·service`·catalog 데이터소스도 빈 골격 실현 | ✅ | ✅ | ✅ | ✅ |
| SH-4 | Django앱 위치 | hr §0 | `infra_layer/django_order/models/order_model.py`·`django_catalog/models/product_model.py`·app 루트 `models.py` 0·label 보존 | ✅ | ✅ | ✅ | ✅ |
| SH-5 | ORM/도메인 명명 | hr §6.3 | ORM=`ProductModel`·`OrderModel`·도메인=`Product`·`Order`(bare) | ➖ | ✅ | ✅ | ✅ |
| SH-6 | 포트/어댑터 명명 | DR-41 §4 | `ProductStockPort`(`…Port`)·`DjangoProductStockAdapter`(`…Adapter`) 헥사고날 쌍 | ➖ | ✅ | ✅ | — |
| SH-7 | **협력 포트 위치** | hr §2·§3 | **`application/order/domain_layer/order/port/product_stock_port.py`(ABC)** ← **domain_layer 정위치**(부모=domain_layer·check-layer-skeleton 외래port exit0)·ACL 구현은 `infra_layer/acl/`·Claude는 finallive에서도 정위치(일관) | ✅ | ✅ | ✅ | ✅ |
| SH-8 | published 표면 | ddd §2 | catalog published_service 빈 골격(데이터소스·ACL 경로라 OHS 미경유 정당·hr §2:152 [통합 시] 폴더 항상) | ➖ | ✅ | ✅ | — |
| SH-9 | 단일 레이아웃 | hr §0 | 양 BC `test/`만·공존 0 | ✅ | ✅ | ✅ | — |
| SH-10 | 공개표면 어노테이션 | DR-39 §4.1 | 모듈 상수 어노테이션(`PROBLEM_JSON:str`·`INT32_MAX:int`·`MAX_CAS_ATTEMPTS:int`)(check-public-surface-annotation exit0) | ➖ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA  *(HTTP operation 존재 → NJ-1·2 치명 적용)*

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| NJ-1 | API 스택 | ninja §2.1 | 단일 `NinjaExtraAPI`(`config/api.py:58`)·**클래스 컨트롤러** `@api_controller("/orders")` `OrderController(ControllerBase)`·`register_controllers`·`/api/` 마운트·DRF 0. **🟡 경미**: 에러 응답이 `ninja.responses.Response` 아닌 `django.http.JsonResponse`(`api.py:80`)·단 content-type `application/problem+json` 정확·기능 정상(§6.2 'plain leak' over-call 아님이나 Response 권장형 미준수) | ✅ | 🟡 | 🟡 | ✅(스택) |
| NJ-2 | 415·raw 파싱 금지 | §6.3 | payload=`OrderIn` ninja 스키마(`Field(ge=1,le=INT32_MAX)`)·`json.loads`/`request.body` 수제 파싱 0·**클래스 컨트롤러라 415 함수형 격리 불요**(내부 415 미요구·깨진본문은 HttpError 중앙변환) | ✅ | ✅ | ✅ | ✅ |
| NJ-3 | 단일 변환점(강) | §6.2 | 전 오류 `_problem` 단일 헬퍼(`api.py:61`)·중앙 `@api.exception_handler`·핸들러 외 raw 응답 0 | ➖ | ✅ | ✅ | —(강) |
| NJ-4 | status별 response 선언(강) | §2.2·§8 | `order_controller.py:23-29` `response={201:OrderOut,404/409/422/503:ErrorOut}` 다중 선언 | ✅ | ✅ | ✅ | —(강) |
| NJ-5 | 버전/하위호환 | api §7 | (경미) URL 버저닝 명시 약함(`/api/orders`·v 프리픽스 없음)·단일 슬라이스라 영향 경미 | ➖ | 🟡 | 🟡 | — |
| NJ-6 | 멱등성 표기 | api §13 | 멱등성 미적용 명시(scope·G1)·죽은 멱등 코드 0 | ➖ | ✅ | ✅ | — |
| NJ-7 | 오류 변환 완전성(catch-all, 강) | §6.2 | **`config/api.py:209` `@api.exception_handler(Exception)` catch-all**·`:197` `@api.exception_handler(HttpError)`(깨진본문 400)·`:167` OperationalError 분기(transient만 503·영구→500)·bare `raise exc` 0 | ✅ | ✅ | ✅ | —(강) |

## TIER-S(핵심) — FC

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| FC-1 | 골든 오라클 | §1.4 | 조정자 직접 probe(DiscoverRunner standalone·`.venv`): 재고부족(stock=1,qty=5)→**409**·충분(stock=10,qty=3)→**201·stock 10→7**·미존재→404 — 골든 행위 일치 | ✅ | ✅ | ✅ | ✅ |
| FC-2 | mutation | §1.4 | **[사후정정] ✅ 실측** — ②경계(`stock_deduction_service.py:19` `<`→`<=`)→**2 red**(단위 `test_stock_equals_quantity_deducts_to_zero`+인수 `test_stock_equals_quantity_returns_201_and_deducts_to_zero` — **경계 양 레벨 보유**=FC-2 (b)+(d) 처방효과) / ①방향(`-`→`+`)→**13 red** / 복원 **33 passed**(`.pyc` purge 위생). ~~측정 불가(테스트 0)~~ 철회 | ✅ | ✅ | ✅ | ✅ |
| FC-3 | 도메인 정합 | §1.4 | `stock_deduction_service.deduct` 음수재고 방지(new_stock<0 차단·`stock>=0` CHECK 백스톱)·차감 정방향·EP probe 차감 정상(10→7)·인과 정상 | ➖ | ✅ | ✅ | ✅ |

## C. 기존규약 마스크 (적용 메모)

- **런 변경 집합**: baseline `832d3be` 대비. catalog 루트 평면앱 `R`(git rename 이주)·`application/` 신규.
- **MQ0**: **Y** — catalog `R` rename으로 `application/catalog/` 이주(touched 데이터소스).
- **MQ1**: **N** — catalog Product에 판정 분기 **없음**(빈 골격). 재고 판정은 order `StockDeductionService`가 소유(design-spec §1.2 명시).
- **MQ2**: **Y** — catalog는 필드·DB 제약(stock≥0 CHECK)·version만, 판정 없는 상류 데이터 소스.
- **판정**: catalog = **데이터소스**(§648-(2)) → `application/catalog/` 위치+4계층+빈 도메인 골격(판정 실내용 면제·빈혈 회귀 방지). order = 신규 BC(재고 판정 소유). **양 BC SH-1·2·3·4·7 PASS**. ⚠️ **Codex(catalog=판정소유 분해)와 마스크 C 분기가 다름** — 재고 판정 소유처가 런타임마다 갈림(§648 허용 분기·underdetermined, 우열 아님).

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| Q-1 | 스코프/과설계·G1 | ddd §6.8·hr §1.1 | 멱등성 미발명(scope·G1)·고-blast 동시성 CAS(Y-1 채택)·design-spec §6 트레이드오프 기록 | ➖ | ✅ | ✅ |
| Q-2 | API 계약 | api §4~14 | RFC 9457 problem(`_problem:74` type/title/status/detail)·`application/problem+json`·`Retry-After`(503)·EP probe 전수 확인 | ➖ | ✅ | ✅ |
| Q-3 | §9.6 형식+테스트 | db §9.6·test §20.5 | **[사후정정] ✅ 설계+테스트 완비** — Risky Write Block 6요소(design-spec §3.4)·CAS 유한재시도(`place_order_command.py:53`)·**동시성·transient 5경계를 결정적 주입으로 행사**(`place_order_concurrency_test.py`: CAS 충돌 1회→수렴 201·소진→503+Retry-After·IntegrityError CHECK→409·락 시그니처→503·**영구장애→500 과잉매핑 0**)+단위 CAS 소진·판정 재실행(`test_retry_re_runs_domain_judgment_each_attempt`). ~~테스트 미작성~~ 철회 | ➖ | ✅ | ✅ |
| Q-4 | 메커니즘 소유권 **[🔴치명]** | db §9.5·16.4 | 커스텀 DB백엔드/PRAGMA/몽키패치 0·표준 ORM `version`/CAS만(`product_stock_adapter.py:37`)(check-mechanism-ownership exit0) | ✅ | ✅ | ✅ |
| Q-5 | 마이그레이션 안전 | db §11 | **catalog `0001` git rename(`R`)으로 byte 보존**(이력 완전 보존)·`0002` state-only rename(Product→ProductModel)+stock CHECK·`0003` version expand(default=0 backfill 불요)·`db_table="catalog_product"` 보존·**`makemigrations --check` No changes**·order `0001` 신규앱 정당 | ➖ | ✅ | ✅ |
| Q-6 | 테스트 도구 | test §20 | **[사후정정] ✅** — Tier-1 4종 부트스트랩(pytest·pytest-django·pytest-mock·factory_boy, `requirements-dev.txt` `==` 핀)+`pyproject.toml [tool.pytest.ini_options]` `DJANGO_SETTINGS_MODULE` — **§2.1 설치+핀 완전 준수**(pip list 실측 4종). 실제 사용: pytest 함수형 33·`mocker`(concurrency/command 테스트)·factory_boy 팩토리 2종. ~~FAIL 러너 부재~~ 철회(채점 가드 3종 신설 계기) | ✅ | ✅ | ✅ |
| Q-7 | 의존성 핀 | hr §1.1 | requirements 런타임 3종 `==` 핀(테스트도구는 미추가·미완성) | ➖ | ✅ | ✅ |

## 의미적 변종 / backstop-blind 메타

- **의미적 변종 0건**: `[결정 PASS ∧ 의미 FAIL]` 없음 — 백스톱 16 exit0과 의미 정독 일치(NJ-1 🟡는 결정·의미 모두 경미 표기·변종 아님).
- **백스톱 blind-spot**: ④ check-layer-skeleton 외래port exit0(SH-7 정위치)·⑯ check-catch-all-handler exit0(HttpError 핸들러 존재)·⑬ check-test-config exit0(pyproject DSM 완비라 정상 통과).
- **[사후정정] 채점자 blind-spot 박제(이번 결과지의 진짜 교훈)**: 초판은 "자기보고 불신" 원칙을 내걸고도 **부재 단정 자체를 측정 없이 했다** — "테스트 0·도구 0·pytest 미설치"를 뒷받침하는 명령 기록이 없고, 실제로는 33 테스트·Tier-1 4종이 채점 1시간 전부터 존재했다(`.venv/bin/pytest` 20:56·마지막 테스트 21:30·런 pytest 실행 21:40·이후 변경 0). 유력 혼동 = 직전 Codex 픽스처의 `test_*.py` 접두 관례 vs Claude의 `*_test.py` 접미 관례 + `requirements.txt`(불변)만 보고 `requirements-dev.txt` 누락. **불신은 긍정 주장("끝났어")만이 아니라 채점자 자신의 부정 단정에도 적용해야 한다** → EVAL-METHOD 채점 가드 3종(수집 오라클 `pytest --collect-only -q` 인용 의무·부정 단정 출력 인용 의무·런-정지 mtime 확인) 신설.

## 9.5 에러 경로 라이브 관측 (§4.3.1)

| 키 | 관측 status | content-type | 화이트리스트 | 판정 |
|---|---|---|---|---|
| **EP-1 깨진 본문** | **400** | `application/problem+json` | {400} | ✅ **DR-55 처방 작동** — 절단 JSON → ninja `HttpError(400)` → `@api.exception_handler(HttpError)`(`api.py:197`) → problem+json. **finallive-claude(HttpError 핸들러 부재·EP-1 흠) → lastlive 수복**(핵심 검증 성공) |
| **EP-2 무효 입력** | **422** | `application/problem+json` | {422,400} | ✅ — `quantity:0` → `OrderIn` Field(ge=1) 검증 실패 → ninja `ValidationError` → 422(`api.py:184`) |
| **EP-3 transient 소진** | **503** | `application/problem+json` | {503,409} | ✅ **[사후정정] 테스트 주입으로 라이브 행사** — `test_cas_exhaustion_returns_503_with_retry_after`(CAS 소진→503+Retry-After)·락 시그니처→503·**영구장애→500**(과잉매핑 0)·IntegrityError CHECK→409, 전부 마운트된 HTTP 표면 통과(`place_order_concurrency_test.py`)·33 그린에 포함. 정적 근거(`api.py:136`·`:167`·check-transient-overmapping exit0) 동일 |
| **EP-4 재고 부족** | **409** | `application/problem+json` | {409} | ✅ — stock<qty → `InsufficientStock`→409(`api.py:123`)·FC-1 골든 교차 일치 |

> **EP probe 환경**: Django `DiscoverRunner` standalone(pytest 미설치·조정자 도구 추가 0)·`.pyc` purge 후 실측·status 추론 금지(실제 응답 코드).

## 조정자 노트

1. **[사후정정] 종합 = ✅ 정적 준수(치명 0)·품질 상.** 치명 전부 PASS(FC-2 mutation red 실측 포함)·WEAK는 NJ-1·NJ-5 경미 2건뿐. ~~보류(미완성)~~ 철회 — "테스트 0·도구 0"은 채점 오판이었고(메타 절 박제), 런은 러너 부트스트랩→인수→단위·동시성·경계까지 정상 TDD 순서로 완주했다(commit 단계만 부재 — 양 lastlive 공통·별도 조사). Codex와의 "완성도 차이" 서술도 철회: **양 런타임 모두 코드+테스트 완성**(Codex 25·Claude 33 tests)·Codex는 감수 리포트만 미완(토큰 소진).
2. **🎯 EP-1/DR-55 처방 작동 = 이번 검증의 본 무대 성공**. finallive-claude는 `@api.exception_handler(HttpError)` 부재로 깨진본문 problem+json 미달(EP-1 흠)이었다. lastlive-claude는 **HttpError 핸들러를 구현**(`api.py:197` docstring "깨진 본문·parse 실패 프레임워크 HttpError도 problem 형식으로 통일") → EP probe로 **깨진본문 400 problem+json 실측 확정**. DR-55 처방(⑯ 백스톱·reviewer 분업)의 **라이브 자연 발화 성공 가능성**(N=1·런간 비결정 배제 못 함).
3. **SH-7 정위치**(Claude는 finallive에서도 정위치라 일관)·**SD-7 ACL 패턴 표준 정확**(hr §2:144 "OHS 미노출+행잠금 시 ACL이 업스트림 모델 직접·infra_layer/acl 격리" — 조정자 초기 "OHS 부재 위반" 우려를 표준 정독으로 자기 정정).
4. **재고 판정 소유 = underdetermined**. Claude(order `StockDeductionService` 소유·catalog 데이터소스) vs Codex(catalog `Product.deduct_stock` 소유). ddd §648-(2)가 "판정을 다른 컨텍스트가 소유"를 명시 허용 → **둘 다 방어 가능·우열 아님**. 마스크 C 분기(catalog 데이터소스 ↔ 판정소유 분해)가 런타임마다 갈리는 것은 P4③(설계 비결정)의 새 인스턴스이나 표준이 허용하는 범위.
5. **[사후정정] 게이트 발화 관측 한계**: 자연 G2 게이트 발화는 픽스처에 기록이 안 남아 미확인(커밋 0·배너는 대화 산출물). 백스톱 16은 조정자 사후 실행 exit0. ~~"재테스트하면 정적 준수 가능성"~~ → 재측정 완료·**정적 준수 확정**.
6. **N=1·우열 금지**. Codex와 게이트 조건(함수형 415 격리 ↔ 클래스 컨트롤러)·설계 분기(catalog 판정소유 ↔ 데이터소스)가 달라 직접 비교 불가. [사후정정] 완성도 축도 "양쪽 코드+테스트 완성"으로 정정 — 차이는 감수 리포트 유무 정도.
7. **[사후정정 추가] "최근 수정이 플러그인을 악화시켰다" 가설 반증**: 이 결과지의 초판 오판("테스트 0")이 그 가설의 핵심 근거였다. 정정 실측으로 근거 소멸 — lastlive-claude는 finallive-claude 대비 EP-1 **수복**(DR-55 작동)·SH-7 정위치 유지·치명 0이며, NJ-1/NJ-5 🟡는 기존 비결정 축 수준. L1(G1 하이브리드) 유발 가설도 mtime으로 반증(Y-채택 20:48 후 러너 준비 20:56→인수 21:01 정상 진입).

## 부록 — 비처방 관찰

- NJ-1 🟡(JsonResponse): `_problem`이 `JsonResponse`+content-type 수동 설정. §6.2 권장형(`ninja.responses.Response`)은 아니나 problem+json 정확·기능 정상. EVAL NJ-1 Q-a "JsonResponse=🟡 경미" 적용.
- catalog 0001 **git rename(`R`)** 보존은 Codex(D+재생성·byte 비동일)보다 이력 보존이 깔끔(Q-5 우위)·단 N=1.
- ~~미완성이라 telemetry·런타임 비교 무의미(테스트 단계 중단).~~ [사후정정] 테스트 파일명이 `*_test.py` 접미 관례(Codex는 `test_*.py` 접두) — `pyproject.toml python_files`에 양 관례를 명시해 수집은 결정적. 표준 위반 아님(비처방 관찰)·채점 오판의 혼동 요인이었음.
- [사후정정] 동적 측정 로그: `pytest --collect-only -q` 33 collected · 전수 33 passed(0.34s) · mutation ②경계 2 red / ①방향 13 red / 복원 33 passed(매 회 `.pyc`+`__pycache__` purge) · 채점 시작 22:37:07 > 픽스처 최신 mtime 21:32:46(런-정지 확인).
