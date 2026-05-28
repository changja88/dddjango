# codex-3 분석 (2차 결정성 런)

> 대상: `/Users/hyun/Desktop/dddjango-codex/` → 캡처 `runs/codex-3/`. Codex CLI(multi_agent), dddjango Codex 포트.
> 프롬프트·baseline·게이트(catalog·plain Django·Django test) 모두 codex-2/claude-1과 통제 일치.
> 목적: codex-2가 놓친 **B1(도메인 죽은 코드)·stock≥0 CHECK**가 2차에도 재현되는지(결정성) 확인.

## 구조 (Q1-1)

완전 §0 4계층 — `application/catalog/{domain_layer,application_layer,infra_layer,presentation_layer}` + 모든 종류폴더(entity/value_object/repository/command/dto/event/specification/domain_service). Django 앱은 `infra_layer/django_catalog/`(label=catalog 보존, `catalog_product` 테이블 보존). presentation에 `schema_in/schema_out/error_out` 분리(codex-2의 뷰 인라인보다 개선, claude-1 수준). 테스트 18개(codex-2는 15).

## 세 신호 판정

### 신호 1 — B1 (도메인 차감 규칙 소유) → ❌ **재현 (방향 동일, 형태는 더 강함)**

- **Product 도메인 엔티티가 아예 없음**(`domain_layer/product/entity/`에 `__init__.py`만). 도메인엔 `ProductRepository`(Protocol 포트)+`AcceptedStock`(VO)뿐.
- 차감 규칙(`stock >= quantity`)은 **infra `DjangoProductRepository.accept_stock`의 조건부 UPDATE에서만 집행**. 응용서비스(`create_order_app.py:14`)는 `unit_of_work.product_repository.accept_stock(...)`를 직접 호출 — 도메인 메서드 경유 없음.
- codex-2: `Product.reserve()` 도메인 메서드가 **있으나 죽은 코드**(호출처 0). codex-3: 도메인 메서드/엔티티 **자체가 없음**. → 같은 "도메인이 규칙을 소유하지 않고 infra로 샘" 방향, codex-3가 더 노골적.
- **단, 의식적 합리화**: design-spec §139가 "`accept_stock`은 raw 영속 명령이 아니라 **도메인 저장소 포트**이고 포트 의미론이 Product 애그리거트 행위를 보존한다"고 명시. → codex의 ddd 리뷰가 *port-as-domain* 논리를 수용. claude-1은 같은 패턴을 ddd 리뷰어가 **[blocker] 빈혈모델로 반려**하고 `Product.deduct()`를 흐름에 배선했음. **같은 표준 텍스트를 양쪽 ddd 리뷰가 정반대로 해석** — 이게 1차에서 본 감사 깊이/해석 격차의 재현.

### 신호 2 — stock≥0 CHECK → ✅ **재현 안 됨 (codex-3는 잡음, 오히려 더 철저)**

- `product_model.py` Meta + 마이그레이션 0002에 `catalog_product_stock_gte_0` **CHECK 추가**. 추가로 `price_gte_0`도.
- 마이그레이션 안전: `RunPython`으로 **음수 행 선검증 가드**(있으면 RuntimeError) + `SeparateDatabaseAndState`로 Product→ProductModel **state-only 리네임**(테이블 drop/recreate 회피). → DB 규율이 이번 런엔 날카로움(claude-1의 §4.5 안전성 의식과 동급).
- codex-2는 stock≥0를 **누락**했음 → **이 격차는 결정적이지 않고 런 분산**(codex가 이번엔 잡음).

### 신호 3 — race 시 available_stock → 해당 없음 (스펙 준수)

- `accept_stock` 실패 경로: 상품 존재하면 `InsufficientStock()`, 없으면 `ProductNotFound()`. **available_stock 미보고**(409 거절만). 프롬프트 요구(409 거절)는 충족 — 버그 아님. claude는 잔여재고 보고(설계 취향 차이). codex-3는 codex-2의 503/sqlite 문자열 결합도 없음.

## 기타

- Order 엔티티: frozen dataclass + `__post_init__` 불변식(product_id>0, quantity>0, unit_price≥0). order_model에 `quantity>0`·`unit_price≥0` CHECK. **total_price는 미저장**(unit_price+quantity만; claude-1은 total_price 저장+CHECK).
- `catalog.models.Product` → `ProductModel` 호환 shim 유지.
- cleancode 잔티: `type(x) is not int` 검사 반복(isinstance 관용 대비 비관용) — 경미.

## 결정성 시사 (claude-2 대기 중 잠정)

| 신호 | codex-2 | codex-3 | 재현? |
|---|---|---|---|
| B1 도메인 소유 | ❌ 죽은 reserve() | ❌ 엔티티 없음(port 합리화) | **재현(방향 동일)** — ddd 감사가 port-as-domain 수용 |
| stock≥0 CHECK | ❌ 누락 | ✅ 집행(+마이그 안전가드) | **재현 안 됨** — 런 분산 |
| race 보고 | ✅ 정확 | 해당없음(미보고, 스펙OK) | — |

→ **잠정 결론**: codex 감사 격차는 *일률적이지 않다*. **stock≥0 누락은 운(분산)**이었고, **도메인 소유(B1) 약함은 두 런 모두 재현** — 이쪽이 더 결정적인 축으로 보인다. 즉 개선 레버는 "DB 제약 감사"보다 **ddd 리뷰가 port/infra 집행을 도메인 소유로 합리화하지 못하게 막는 것**에 있다(이게 스캐폴딩 대상 후보). claude-2 캡처 후 claude 우위도 결정성인지 확정해 RESULTS에 종합.
