# smoke6-codex 채점 결과지

> **방법**: `EVAL-METHOD.md` v3 — 결정 레인(백스톱 6종 직접 실행 + grep) ∥ 의미 레인(코드 직독·줄 인용) + 표준 직접 대조. 사전식 집계.
> **채점일**: 2026-06-02 15:54. **픽스처**: `~/Desktop/dddjango-smoke6-codex`. **태스크**: 주문 생성 API(별도 order, catalog 재고 차감, 재고부족 409).
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK · ⏸️ 보류 · ➖ 해당 레인 없음(N/A) · ⚠️(contested) 인간 큐.

> 🔴🔴 **치명 메타-경고 — 이 런은 STALE 캐시(1.0.1, 백스톱 4종)에서 돌았다.**
> Codex 런타임 캐시(`~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0/`)는 plugin.json `1.0.1`·SKILL.md "4종"·스크립트 **4개**(`check-mechanism-ownership`·`error-centralization`·`response-schema-bypass`·`layer-skeleton`)였다. **이번 세션 하드닝(1.0.2: NJ-4 `check-openapi-error-declaration` + SD-7 `check-context-isolation` 백스톱 2종 + 생산자 예방 표준 편집)은 런타임에 없었다.** `/plugin marketplace update dddjango-local`가 1.0.2(eval 브랜치 로컬·unpushed)를 못 받음.
> → **이 결과지는 "1.0.1 베이스라인" 데이터이지, 이번 세션 NJ-4·SD-7 하드닝의 검증이 아니다.** 새 백스톱 2종의 라이브 발화는 미검증(캐시에 없었으니 발화할 기회 자체가 없었음).
> → 단 **조정자(나)가 레포 6종 백스톱을 픽스처에 직접 실행 → 전부 exit 0**. 코드는 6종 기준으로도 청정(생산자 예방 베이스가 이 태스크엔 충분했다 — N=1).

## 종합 — 🔴 **FAIL (치명 SH-1·SH-4 = catalog가 allocation 판정 소유(§632-1) → 이주 의무 발생 → 미이행 확정)** + content_negotiation 미들웨어 과설계(명백한 오류)
치명 게이트 중 **SH-1·SH-4 FAIL**(마스크 C: catalog가 allocation 판정 소유하나 평면 유지=이주 미시행). 결과지 초안은 contested(인간 큐)였으나 **사용자 판정(2026-06-02)으로 "이관 필요 = FAIL 확정"** — 표준 **architecture-ddd `final.md:632`-(1)** "판정·불변식을 소유하면 도메인 컨텍스트 → 표준 구조로 이주한다" 직격. **나머지 치명 전부 PASS.**
> ↔ **Claude 대조(채점 정정)**: catalog가 `application/` 밖 루트에 있는 건 파일트리 §0-1 위반이고 **두 런 공통**(Claude 결과지의 'clean PASS'는 §632-(2)를 위치 면제로 오독한 채점 오류 — 정정함). §632-(2)는 데이터소스의 **4계층 전개**만 면제하지 **위치**는 면제 안 함. **catalog-위치 = 양쪽 SH-1/4 FAIL.** Codex는 거기에 더해 판정을 catalog(`published_service`)에 적재 → §632-(1) "판정 소유=도메인 컨텍스트=이주" **가중 위반**. 즉 두 런 모두 catalog-컨테이너 FAIL이고, Codex가 판정-소유로 더 나쁨.

**🆕 content_negotiation 전역 미들웨어 = 명백한 오류(과설계·오메커니즘)**: `OrderApiContentNegotiationMiddleware`(`settings.py:46` 전역 `MIDDLEWARE` 등록)가 415/406 협상을 자작. **Context7 공식문서 확인 결과 ninja는 415/406을 `raise HttpError(415/406)`·튜플 `return 415,{...}`·`@api.exception_handler`·`Parser.parse_body`로 trivial하게 낸다 → 미들웨어 정당화 근거 0.** Claude는 같은 계약을 ninja 위임으로 0줄. → Q-1 과설계 + BC 격리 침범(조정자 노트).

**smoke4-codex 대비 실질 개선 (verdict는 FAIL이나 질적으로 나음):**
- **SD-3 교정**: smoke4 핵심 FAIL(`stock__gte=quantity` SQL 판정 복제) **사라짐** — Python 판정 + version-CAS 경합가드만.
- **테스트 수집 정상**: `catalog/tests.py` 크래시 없음 — `manage.py test` 17 green(3회).
- **NJ-4·SD-6(P1a)·SD-7 청정.**

**결함 요약**: SH-1·SH-4(이관 미시행·확정) · **content_negotiation 미들웨어(과설계 확정)** · Q-3 비결정 동시성(CF-7) · C1 완화형(약속 테스트 3종 부재).

---

## A. TIER-S 척추 — DDD 도메인 충실도 (S-DDD)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SD-1** 빈혈: 판정 소유 | 핵심 규칙·불변식이 도메인 메서드로 | §3.2·§3.1 | 주문 불변식(product_id>0·qty>0) `order.py:22-25`; 재고충분성 판정 `stock_allocation.py:40-42`(catalog **평면** published_service — domain_layer 부재) | ➖ | ✅ | ✅⚠️(contested) | 치명 |
| **SD-2** 빈혈: 프로덕션 호출 | 응용이 조회→도메인메서드→저장 실호출 | §3.2·§3.6 | `create_order_app.py:37-42` atomic 내 `allocate`→`save` 실호출(죽은코드 아님) | ➖ | ✅ | ✅ | 치명 |
| **SD-3** 빈혈: 무복제 | 판정이 인프라 SQL/ORM에 복제 안 됨 | §3.2 | CAS `WHERE id=,version=`만 `stock_allocation.py:49-52`(경합가드); 판정은 Python `:40-42`. **`stock__gte` SQL 복제 0** | ✅ | ✅ | ✅ **(smoke4 ❌→교정)** | 치명 |
| **SD-4** 애그리거트 경계 | 1트랜잭션 1애그리거트·ID 참조 | §3.3 | `Order` frozen 단일·`catalog_product_id: int` ID 참조·도메인 FK 0 `order.py:7-11` | ➖ | ✅ | ✅ | 치명 |
| **SD-5** 모델 표현력 | frozen VO·무상태 서비스·유비쿼터스 명명 | §3.1·§3.5·§2.3 | `@dataclass(frozen=True) Order` `order.py:7`·`allocate_catalog_stock` 무상태 함수·도메인 네이밍 | ➖ | ✅ | ✅ | 치명 |
| **SD-6** 계층 순수성(P1a) | domain HTTP/ORM 0; status 변환 presentation 단일점 | §5.1·§6.1; ninja §2.2·§6.2 | operation은 `return 201, OrderOut(...)` schema만 `api_orders.py:48`; 변환은 중앙 `application_exception_handler` `problem_details.py:31` + 배선 `orders_api_router.py:17-19`; app/domain HTTP import 0 | ✅ | ✅ | ✅ | 치명 |
| **SD-7** 컨텍스트 통신 | 타 BC는 OHS/ACL로만; 결합 ACL 격리 | §3.2(3)·§2.5 | catalog 결합이 ACL `catalog_stock_acl.py` 한 곳; OHS `catalog.published_service.stock_allocation` 경유 `:5`; 예외 ACL 번역 `:17-23`(presentation·application 직접 import 0) | ✅ | ✅ | ✅ | 치명 |

## B. TIER-S 척추 — houserules 충실도 (S-HR)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | 신규/이주앱이 `application/<app>/` | §0-1 | 신규 `orders`는 `application/orders/` ✅. 단 **catalog가 allocation 판정 소유(MQ1=Y∧MQ2=N→§1.2 이주 대상)인데 평면 `catalog/` 유지** | ❌ | ➖ | ❌(FAIL 확정·사용자 판정) | 치명 |
| **SH-2** 4계층 | 4계층 물리 분리 | §0-2 | `orders` 4계층(`domain/application/infra/presentation_layer`) 존재 | ✅ | ➖ | ✅ | 치명 |
| **SH-3** 종류 폴더 | 종류 2차 폴더 | §0-3·§0-4 | `entity/value_object/repository/port/command/dto/...` 종류폴더 구조 | ✅ | ➖ | ✅ | — |
| **SH-4** Django앱 위치 | `models.py`가 `infra_layer/django_<app>/` | §0-5 | `orders` 모델은 `infra_layer/django_orders/models/order_model.py` ✅. 단 **`catalog/models.py` 루트**(판정소유→이주 대상) | ❌ | ➖ | ❌(FAIL 확정·사용자 판정) | 치명 |
| **SH-5** ORM 명명 | ORM `<Name>Model`, 도메인 bare | §0-6·§4 | ORM `OrderModel` `order_model.py:4`·도메인 `Order` bare | ✅ | ➖ | ✅ | — |
| **SH-6** 포트/구현 명명 | `Interface`/`Impl`·약어 0 | §4 | `ProductStockPort`/`DjangoProductStockPort`·`OrderRepository`/`DjangoOrderRepository`·`Interface`/`Impl`/`_repo.py` 0 | ✅ | ➖ | ✅ | — |
| **SH-7** 협력 포트 위치 | port가 `domain_layer/<agg>/port/` | §2 | `domain_layer/order/port/product_stock_port.py` | ✅ | ➖ | ✅ | 치명 |
| **SH-8** ACL 분리 | ACL이 `infra_layer/acl/` | §2·§3 | `infra_layer/acl/catalog_stock_acl.py` 분리·repository 미혼합 | ✅ | ✅ | ✅ | — |
| **SH-9** 단일 레이아웃 | 한 앱 두 레이아웃 금지 | §1.4 | `orders`는 `test/` 단일 ✅. **catalog는 `tests.py`(스텁 잔존)+`test/` 공존** | ❌ | ➖ | 🟡(비치명; smoke4와 달리 수집 크래시는 없음) | — |
| **SH-10** 테스트 의미군 | `test/{unit,integration,e2e}` 분리 | §1.3 | `orders/test/{unit/{domain,application},integration/{api,db}}` 의미군 분리·HTTP=integration ✅. 단 `integration/db/` 빈폴더(약속 테스트 부재) | ✅ | 🟡 | ✅(약속부재 노트) | — |

## TIER-S(조건부) — django-ninja 충실도 (S-NINJA)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명(조건부) |
|---|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | 신규 JSON API를 Ninja로 | §1.1·§10 | `NinjaAPI`+`Router` `orders_api_router.py:15-16`; plain view·DRF 0 | ✅ | ➖ | ✅ | 치명 |
| **NJ-2** operation 얇음 | 비즈로직·ORM·수동파싱 0 | §1.3·§2.2 | operation은 app 생성+호출+schema 매핑만 `api_orders.py:37-53`; `json.loads`/ORM/분기 0 | ➖ | ✅ | ✅ | 치명 |
| **NJ-3** Schema 입출력 분리 | 요청·응답 Schema 분리 | §2.2·§3.1 | `schema_in.py`(In, `extra="forbid"`)·`schema_out.py`(Out)·`error_out.py` 분리·도메인 직접직렬화 0 | ✅ | ✅ | ✅ | —(강) |
| **NJ-4** status별 response 선언 | 모든 status `response={}` 선언(§2.2 line111) | §2.2·§8 | **201·404·406·409·415·422 전부 `response={...}` 선언** `api_orders.py:27-34`; `openapi_extra` 우회 0 | ✅ | ➖ | ✅ | —(강) |
| **NJ-5** operation 문서화 | summary/tags·반환타입 | §2.2 | `summary="Create order"` `:35`·`tags=["orders"]` `:22`·반환타입 `tuple[int, OrderOut]` `:37` | ✅ | ➖ | ✅ | —(경미) |
| **NJ-6** ninja 버전 핀 | 매니페스트 버전 핀 | §2.1 | `django-ninja==1.6.2` `requirements.txt` | ✅ | ➖ | ✅ | —(경미) |

> **NJ-4 정독(poc-codex miss 반영)**: 에러 경로 전체를 줄 인용으로 읽음 — `response={}`에 6 status 전부 선언(`:27-34`) + 중앙 핸들러 `problem_details.py`가 `JsonResponse`로 problem+json 반환(§6.2 처방 형태) + 협상 `content_negotiation.py`. **(a) `django.http.JsonResponse` 사용 = 경미 🟡 NJ-1**(§6.2는 `ninja.responses.Response` 처방이나 JsonResponse는 경미 일탈) · **(b) openapi_extra 우회 = 없음(NJ-4 청정)**. 이전 poc-codex의 NJ-4 위반이 이번엔 재현 안 됨.

## TIER-S(핵심) — 기능 정확성 (FC)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | 재고5·주문2→201∧남은3 `test:35-37` / 재고1·주문2→409∧재고1불변∧주문0 `:55-57` / 미존재→404∧주문0 `:75` / oversell 재고1·동시2→[201,409]∧재고0 `:199-203` — 골든 일치 | ➖ | ✅ | ✅(실측·소스) | 치명 |
| **FC-2** 테스트 비-vacuous | mutation 3종 미실행(프리즈 트랙) | ⏸️ | ➖ | ⏸️ 보류 | 치명 |
| **FC-3** 도메인 정합 | 차감방향 정상 `stock_allocation.py:46` `stock-quantity`·`stock>=0` CHECK `catalog/models.py:12-15`·인과 정상 | ➖ | ✅ | ✅ | 치명 |

## C. 기존규약 마스크 (S-HR 판정 조건)
- `catalog` = **기존 앱**. 런 diff가 **재고 충분성 판정 + 차감(allocation)을 catalog에 적재**(`published_service/stock_allocation.py` 신규 — baseline엔 데이터-only `Product`만).
- **MQ1**(핵심규칙 분기 추가?)=**Y** ∧ **MQ2**(단순 상류 데이터소스?)=**N**(판정 소유) → **§632-(1) 발동 = 이주 대상**. 평면 유지 → SH-1·SH-4 입력.
- **위치 위반은 Claude와 공유, 판정-소유는 Codex 가중**: catalog가 `application/` 밖 루트에 있는 것 자체가 파일트리 §0-1 위반(Claude도 동일 — 그쪽 결과지 정정함). Codex는 거기에 더해 판정까지 catalog에 적재 → §632-(1) "판정 소유=도메인 컨텍스트" 가중. 즉 **catalog-위치=양쪽 FAIL, Codex=판정-소유 가중**.
- **사용자 판정(2026-06-02): 이관 필요 = FAIL 확정.** 표준 텍스트(houserules §1.2·ddd §3.2)가 "판정 소유→구조 이주" 쪽이고, narrow OHS를 평면 `published_service/`로 노출하는 데 만족하고 전체 catalog 이주를 안 한 것은 smoke4와 동일한 반복 패턴. (설계 §5 `design-spec.md:432`가 "Do not migrate the whole catalog"를 명시 결정했고 DR-24는 "방어가능/underdetermined"라 했으나, 사용자가 이관쪽으로 확정.)

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| **Q-1** 스코프/과설계·G1 | 발명 0·고-blast G1 상정 | ddd §6.8·houserules §6.1 | 스코프 절제 양호(멱등성 명시제외+테스트 `test:159-181`·단일상품·이벤트 미도입). **그러나 ❌ `OrderApiContentNegotiationMiddleware`(`settings.py:46` 전역) = 명백한 과설계** — ninja `HttpError(415/406)`로 trivial한 걸 51줄 전역 Django 미들웨어+`request.path` 하드코딩으로 자작(Context7 공식문서 확인). + catalog `version` 컬럼 고-blast G1 미상정(C5 약화형) | 🟡(미들웨어 전역등록) | ❌(과설계) | ❌ |
| **Q-2** API 계약 | RFC9457·버전 일관 | architecture-api §4~14 | RFC9457 problem+json·404/409/422/415/406 일관·버전정책 명시 `design-spec §3.versioning` | ➖ | ✅ | ✅ |
| **Q-3** §9.6 동시성 | 결정적 CAS·소진→409 | architecture-db §9.6·impl-test §20.5 | 8행 블록 ✅·소진→409 결정적 `test:39-57`. **그러나 oversell 테스트가 `ThreadPoolExecutor` 실스레드 레이스 `test:183-203`=스케줄러 의존 비결정(CF-7 FAIL 앵커)** + 설계 약속 `test_stock_allocation_concurrency.py` 부재 | 🟡 | ❌ | ❌ |
| **Q-4** 메커니즘 소유권 **[🔴치명]** | 커스텀 백엔드/PRAGMA/몽키패치 0 | architecture-db §9.5·§16.4 | version-CAS + `select_for_update`만; 커스텀 DB백엔드/PRAGMA/몽키패치 0 | ✅ | ➖ | ✅ |
| **Q-5** 마이그레이션 안전 | 0001 불변·expand | architecture-db §11 | 기존 `catalog/0001` 불변 + 신규 `0002_product_version_stock_check`(version+CHECK expand)·신규앱 `orders/0001` | ✅ | ✅ | ✅ |
| **Q-6** 테스트/TDD | 그린·행위 덮음 | impl-test·discipline-tdd | 기본 `manage.py test` **17 green(3회)**·수집 정상(smoke4 크래시 교정)·계약/원자성/협상 행위 덮음. 단 **설계 §5 약속 테스트파일 3종 부재**(`test_order_persistence.py`·`test_stock_allocation_concurrency.py`·`test_stock_allocation_persistence.py` — 동시성은 api test에 통합) | ✅(실행) | 🟡 | 🟡 |
| **Q-7** 경미 | 경미 흠 | houserules §5·§6.2 | `catalog/tests.py` 스텁 잔존·`integration/db/` 빈폴더·`application_layer/.../{query,handler,service}` 빈폴더·`infra_layer/service` 빈폴더 | ➖ | 🟡 | 🟡 |

---

## 조정자 노트

- **🔴 STALE 캐시(메타-치명)**: 위 헤더 경고 참조. 이 런은 **1.0.1(백스톱 4종)** — 이번 세션 하드닝 미적용. 결과지는 1.0.1 베이스라인 데이터이며 NJ-4·SD-7 신규 백스톱의 *라이브 발화*는 **미검증**. 조정자가 레포 6종을 픽스처에 직접 실행해 **전부 exit 0** 확인(코드는 6종 기준으로도 청정) — 생산자 예방 베이스가 이 태스크엔 충분(N=1, 우열 결론 아님).

- **SD-3 교정 확인(핵심)**: smoke4-codex의 치명 FAIL `stock__gte=quantity`(판정 SQL 복제)가 이번엔 **부재**. `_persist_allocation_with_cas`는 `filter(id=, version=).update(...)`로 경합가드만(`stock_allocation.py:49-52`), 충분성 판정은 `_ensure_sufficient_stock`의 Python `stock < quantity`(`:40-42`). 빈혈 회귀 없음.

- **SH-1·SH-4 FAIL 확정(사용자 판정 2026-06-02)**: catalog가 allocation 판정을 소유(published_service)하나 평면 유지 → 마스크 C §1.2상 이주 대상인데 미이주. 결과지 초안은 contested(인간 큐)였으나 **사용자가 "이관 필요 = FAIL"로 확정**. 표준 텍스트(houserules §1.2·ddd §3.2)도 "판정 소유→구조 이주" 쪽. smoke4와 **반복 패턴**(narrow OHS를 평면 published_service로 노출하고 전체 이주는 안 함). 단 SD-3 동반 FAIL이 없어 smoke4보다 질적으로 나음.

- **🆕 content_negotiation 전역 미들웨어 = 명백한 오류(과설계·오메커니즘)**: `OrderApiContentNegotiationMiddleware`가 `settings.py:46` 전역 `MIDDLEWARE`에 등록돼 415/406 협상을 자작(`__call__`+`request.path == "/api/orders"` 하드코딩 `content_negotiation.py:13`). **Context7 공식문서 확인**: ninja는 415/406을 `raise HttpError(415/406)`·튜플 `return 415,{...}`·`@api.exception_handler`·`Parser.parse_body` 오버라이드로 trivial하게 낸다(미들웨어 정당화 근거 0). problem+json media type 맞춤도 `create_response` 오버라이드(ninja 경계, 표준 `implementation-django-ninja/final.md:379-398`)로 해결. **결함 4종**: ①메커니즘 오선택(전역 미들웨어 vs ninja 경계) ②BC 격리 침범(orders presentation이 전역 `settings.MIDDLEWARE` 점유) ③라우팅 중복·취약(path 하드코딩→경로 변경 시 silent 깨짐) ④YAGNI(Claude는 ninja 위임 0줄). **근본원인**: 표준이 406/415 *계약*(architecture-api §7)은 요구하나 *협상 처리 위치*를 안 박은 빈칸 → Codex가 미들웨어로 이탈. → ninja 스킬 보강 대상(Claude 런 후).

- **Q-3 비결정 동시성(CF-7)**: 설계 §4는 **결정적 재시도**(CAS 실패→재조회→재판정→2차 CAS→409)를 처방했으나, coder가 oversell 검증을 `ThreadPoolExecutor(max_workers=2)` **실스레드 레이스**로 구현(`test:183-203`). 3회 green이나 스케줄러 의존이라 flaky 위험 — 루브릭 CF-7 FAIL 앵커. 결정적 CAS-스파이(stale version 1회 주입→수렴)가 PASS 형태.

- **C1 완화형(약속 테스트 부재)**: 설계 §5(`design-spec.md:449-452`)가 `test_order_persistence.py`·`test_stock_allocation_concurrency.py`·`test_stock_allocation_persistence.py`를 명시했으나 **셋 다 부재**(동시성은 api test로 통합, 영속화는 api test로 간접 덮음). DR-24 C1(약속 테스트 부재 Critical)의 완화형 — 행위는 덮이나 명세=단일근거 규율엔 흠.

- **C5 약화형(고-blast 미상정)**: catalog에 `version` 컬럼 추가(기존 소유 컨텍스트 스키마 수정)는 고-blast인데 G1 트레이드오프 옵션으로 미상정(G1 배너 "트레이드오프 없음"). 설계 요약에 *공개*는 됐으나 *선택지*로 올리진 않음. Claude(같은 태스크)는 멱등성·라인스냅샷을 G1 옵션으로 표면화 — 대조.

- **as-delivered 위생**: smoke4의 stale `.pyc` 차감역전 결함은 이번 미관측(소스 `stock - quantity` 정상, 실측 17 green). 

- **N=1·태스크 단일**: 우열·결정성 결론 아님(DR-14·DR-24 준수).
