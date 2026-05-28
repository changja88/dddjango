# codex-2 정적 분석 (Claude 대조 대기)

> 대상: `workspace/eval/runs/codex-2/`(=Codex CLI 0.134.0, API 프롬프트 클린 런).
> 프롬프트: "재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API". G0=옵션2(기존 catalog), 렌즈 ddd·api·db.
> baseline: Product(name,price,stock)만, Django 4.2.30. Claude 런(`dddjango-smoke-claude`) 완료 후 같은 차원으로 1:1 대조.

## 한 줄 결론

세 런(PoC 평면 / Claude smoke 컨테이너 주저 / 이번) 중 **구조·계약·테스트 품질이 가장 높음**. 단 **B1(도메인 죽은 코드)**과 **핵심 불변식 DB 제약 누락** 두 가지가 설계·감사를 통과해 남았다.

## Q1 차원별 (Claude 열은 런 후 채움)

| # | 차원 | codex-2 | 근거 |
|---|---|---|---|
| Q1-1 | 트리 형태 | **완전한 §0 4계층** `application/catalog/{domain,application,infra,presentation}_layer/`, Django 앱 `infra_layer/django_catalog/` | design-spec §6.2 |
| Q1-2 | 도메인 배치 | `Product.reserve()`(규칙), `Order.create()`+`total_price` 프로퍼티. 단 **Product 엔티티 프로덕션 미사용** | product.py / order.py / create_order_app.py |
| Q1-3 | 트랜잭션·동시성 | `transaction.atomic` 전체 래핑, **조건부 UPDATE**(`filter(stock__gte=q).update(F("stock")-q)`)로 오버셀 방지, `select_for_update` 불사용(SQLite no-op 인지) | design §5.3, infra product_repository.py |
| Q1-4 | 불변식 표현 | OrderModel CheckConstraint(quantity≥1, unit_price≥0). **ProductModel `stock≥0` 제약 누락**(설계 §5.1/§5.4가 요구한 "최후 방어선") | migration 0001 |
| Q1-5 | 예외 설계 | `ProductError`/`OrderError` 계층, 컨텍스트(product_id·requested·available) 보유. `DatabaseBusy`가 product 예외모듈에 위치(교차관심사 오배치) | product/order exception.py |
| Q1-6 | 네이밍 | `ProductModel`/`OrderModel`(§4), 포트=`ProductRepository`(Protocol)/구현=`DjangoProductRepository`. 규약 준수 | repository 포트/구현 |
| Q1-7 | 테스트 구조 | unit/integration/e2e 분리(e2e 빈 폴더=표준). 15개(product3·order2·app3·api7) | test/ |
| Q1-8 | 테스트 품질 | Fake 리포지토리·`ImmediateTransaction` 더블, 행위중심, 7개 상태코드 전부 커버. 503은 patch 주입(설계 허용) | test_create_order_app.py / test_api_orders.py |
| Q1-9 | 타입·주석 | 프로덕션·테스트 시그니처 타입 충실(`-> None`, `tuple[int,int,int]` 등). 주석 거의 없음(자명) | 전반 |
| Q1-10 | 빌드 | migrate OK / check OK / makemigrations --check 변경없음 / test 15 OK | G2 보고 |

## 핵심 발견 (심각도순)

**[Important] ① B1 — 도메인 죽은 코드 + 규칙 이중화**
- 프로덕션 경로(`create_order_app.py:36`)는 `product_repository.reserve()`(조건부 UPDATE)만 호출. **`Product` 엔티티는 프로덕션에서 한 번도 생성 안 됨**(non-test grep 0건). `Product.reserve()`는 단위 테스트에서만 실행.
- 재고 규칙 `stock>=quantity`가 두 곳: `Product.reserve()`(죽음) + `DjangoProductRepository._reserve()`의 `filter(stock__gte=quantity)`(실제 집행). §06 DRY 위반.
- **설계가 긴장을 그대로 통과시킴**: design-spec §3.3/§3.6/§8은 "규칙 소유자=Product.reserve(), 조건부 UPDATE는 영속성/동시성 방어"라 적었지만, SQLite에서 read-reserve-write가 안전 불가라 실제로는 SQL이 단독 집행 → Product.reserve()는 잔재. **이 긴장이 G1 ddd 리뷰 + G2 discipline 감사("이상 없음")를 모두 통과**.
- → **Claude smoke2가 Blocker B1으로 잡았던 그 축**(도메인 차감 소유 선언 vs 인프라 원자 집행의 미해소 긴장). dddjango 레벨 과제 + 이번 런 감사가 놓침.

**[Important] ② 핵심 불변식 DB 제약 누락**
- 설계 §5.1/§5.2/§5.4: `ProductModel.stock >= 0` CheckConstraint를 "음수 재고 막는 최후 방어선"으로 명시. **구현(`product_model.py`·migration 0001)에 없음**. OrderModel 제약 2개는 존재.
- 핵심 도메인 불변식(음수 재고 금지)의 DB 방어선 부재 + 이를 검증하는 테스트도 없음. 설계-코드 이탈을 감사·검증이 놓침.

**[Moderate] ③ 누수된 포트 계약**: `ProductRepository.reserve(product_id, quantity) -> tuple[int,int,int]` — 세 int의 의미 불투명, 인프라 편의로 빚어진 형태(§02/§07). 도메인 포트가 영속성에 끌려감.

**[Minor] ④** `_is_database_busy`가 product/order 리포지토리에 **복붙 중복**(DRY) + 에러 문자열 매칭("database is locked")이라 **SQLite 결합**(§03 취약).
**[Minor] ⑤** `DatabaseBusy`가 product 도메인 예외모듈에 있는데 order 인프라도 import → 교차관심사 오배치(§01).
**[Minor] ⑥** quantity<1 **삼중 검증**: api_orders(422) + CreateOrderApp.create + Product.reserve(죽음).

## 결함 아님 (정정 — 비교 시 오판 금지)

- **plain Django API(ninja 미사용)**: design-spec §4.5의 **의도된 결정**("Django만 설치됨, 의존성 추가는 G0 범위 밖"). YAGNI 근거 타당. 단 수동 JSON 파싱·검증·직렬화 보일러플레이트 존재 → Claude가 ninja를 썼는지가 주요 비교축.
- **빈 종류폴더**(query/handler/service/value_object/entity/e2e): §0 불변식 #4가 "비어도 폴더+`__init__.py` 유지"로 **명시 의무화** → 표준 준수, 과다설계 아님.

## 강점 (Claude 대비 우위 후보)

- **§4.4 Django 통합 집행 레시피 도출**: `AppConfig.label="catalog"` + `db_table="catalog_product"`로 중첩 패키지 앱의 짧은 라벨·기존 테이블명 보존 → 마이그레이션 rename/drop 없음. **smoke2가 "표준에 빠졌다"고 지적한 바로 그 레시피를 Codex가 채움**.
- design-spec이 지식 스킬(architecture-ddd/api/db, discipline-houserules) 절을 인용하며 자기일관성 점검(§8)까지 수행 — 설계 밀도 높음.
- 테스트 더블 설계 깔끔(과도 mock 없음), 외부 행위 7경로 커버.
- 정직한 보고(503 Red 없이 Green, 잔존 빈 `catalog/migrations` 자진 공개).

## G0 배치 추천 분기 (관찰)

같은 프롬프트인데 **G0 배치 추천이 런타임마다 갈림**: Codex 코디네이터는 옵션2(기존 catalog 포함)를 기본 제안 → 채택. **Claude 코디네이터는 "새 orders 앱 분리"를 추천**(catalog 포함은 2순위). 통제 비교를 위해 Claude도 옵션2로 강제 일치시켰으나, 이 추천 차이 자체가 코디네이터 G0 판단의 비결정/성향 차이를 보여주는 데이터.

## API 프레임워크 결정 방식 분기 (관찰)

**Codex**: 프레임워크 선택을 사용자에게 **묻지 않고** design-spec §4.5에서 "Django만 설치됨·의존성 추가는 G0 범위 밖"으로 **plain Django(JsonResponse)를 무언 결정**.
**Claude**: 프레임워크를 **G0 게이트로 노출**하고 **Django Ninja 도입을 추천**(plain은 2순위). → 통제 비교를 위해 사용자가 `2`(순수 Django)로 강제 일치. 두 런타임의 "의존성 도입 판단을 사용자에게 위임 vs 자체 결정" + "Ninja 선호 vs YAGNI plain" 성향 차이가 데이터.

## 의존성 결정 성향 — 반복 패턴 (핵심 관찰)

G0에서 의존성 결정이 **세 번 다 같은 방향으로 갈림**:

| 결정 | Claude 코디네이터 | Codex 코디네이터 |
|---|---|---|
| 기능 배치 | "새 orders 앱 분리" 추천 | 옵션2 "기존 catalog" 기본 |
| API 프레임워크 | 게이트 노출 + **Ninja 추천**("스택 기본") | 무언 **plain Django** 결정 |
| 테스트 러너 | 게이트 노출 + **pytest 추천**("dddjango 스킬 기본") | 무언 **Django test** 결정 |

→ **Claude = 의존성/구조 결정을 사용자 게이트로 노출하고 더 풍부한 표준 도구를 권장.
Codex = 묻지 않고 YAGNI·무의존 경로를 자체 결정.**
통제 비교를 위해 사용자가 매번 Codex 쪽(옵션2·plain·Django test)으로 강제 일치시킴 — 즉 **이번 1:1은 "plain Django + Django test"라는 Codex가 고른 최소 스택 위에서 코드 품질만 비교**한다. (Claude의 자연 추천 스택(Ninja+pytest) 품질은 별도 비통제 런이 필요.)

## Claude 대조 시 볼 것 (런 후)

1. 구조: Claude가 `application/` 컨테이너를 세웠나, 아니면 평면 `catalog/{_layer}`(smoke 재현)인가.
2. B1: Claude의 ddd 리뷰/discipline 감사가 도메인 죽은 코드를 잡나(smoke2처럼) 못 잡나.
3. 프레임워크: Claude가 django-ninja를 썼나 plain Django인가.
4. stock≥0 제약: Claude는 넣나.
5. 테스트 수·구성, 토큰·시간.
