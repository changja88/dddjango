# 통합 설계 명세 — 재고 차감 주문 생성 (catalog)

> 단일 근거(source of truth). 이후 인수 테스트·coder·discipline-reviewer는 스코프 메모가 아니라 이 명세만 읽는다.
> 활성 lens: **ddd**(애그리거트·불변식·규칙 소유) · **db**(트랜잭션·동시성·제약 — 토이의 핵심) · **api**(최소: POST 생성, 부족 시 409).

---

## 0. 컨텍스트와 BC 배치 (고정 결정 — 명세에 박음)

- **무엇을**: 단일 품목 주문. 재고가 부족하면 `409`로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.
- **BC 배치 = 기존 `catalog` 영역 확장 (G0에서 고정)**. 신규 BC를 만들지 않는다. `Product`(재고 보유)와 `Order`(주문)는 **동일 `catalog` 바운디드 컨텍스트 안의 두 애그리거트**다. 이 배치는 스코프가 고정했으므로 존중하고 그 안에서 애그리거트·통합을 설계한다(암묵 재결정 금지). ddd 리뷰어가 배치 부적절을 지적하면 묵살하지 않고 G1 옵션으로 사용자 재고에 올린다.
  - *왜 단일 BC가 정합적인가*: `Product`와 `Order`가 같은 유비쿼터스 언어("재고/주문")·같은 소유 경계(catalog 팀) 안에 있고 같은 DB에 산다. **단, 이 단일-BC 판단의 근거는 유비쿼터스 언어·소유 경계이지 `architecture-ddd` §3.3 규칙4가 아니다** — 규칙4("동일 DB 단순 케이스에서 한 트랜잭션에 복수 애그리거트 수정 용인")는 *애그리거트(일관성) 경계* 완화 규칙이지 *두 개념을 같은 BC로 합쳐 ACL을 생략해도 된다는 컨텍스트 레벨 허가가 아니다*(애그리거트 레벨 규칙을 컨텍스트 레벨 결정에 오용 금지). 같은 BC이므로 BC 간 통신(OHS/ACL)은 **해당 없음** — `port/`·`acl/` 폴더를 두지 않는다(`references/final.md` §3 `[통합 시]`는 다른 컨텍스트 소비 시에만).
- **경계(스코프 고수)**: 단일 품목만(여러 라인 아이템·배송지·쿠폰·결제·취소·환불은 범위 밖). 명세에 없는 기능을 추가하지 않는다.
- **제약**: 개발 SQLite / 운영 Postgres. 동시 주문에서 oversell 금지(재고 차감 = Risky Write, `architecture-db` §9.6).

---

## 1. 도메인 설계 (ddd lens)

### 1.1 애그리거트 경계와 불변식

- **`Product` 애그리거트 (루트)** — 재고를 보유하고 **"재고 충분 판정 + 차감"의 불변식을 소유**한다.
  - 불변식: `stock >= 0`. 재고가 요청 수량 미만이면 차감을 거절한다(진짜 불변식이라 애그리거트 경계 안에서 보호 — `architecture-ddd` §3.3 규칙1).
  - 작은 애그리거트(규칙2): 루트 `Product` + `stock`(int) + 동시성용 `version`(int). 리뷰·이미지 등 부가 관심사는 포함하지 않는다.
- **`Order` 애그리거트 (루트)** — 주문 사실을 보유한다. `Product`를 **ID로만 참조**(`product_id`)한다(규칙3, 직접 객체 참조 금지).
  - 단일 품목: `Order`는 `product_id`·`quantity`를 갖는다. 최소 1개 수량 불변식(`quantity > 0`).
- **두 애그리거트, 한 트랜잭션 용인**: `Product` 차감과 `Order` 생성은 같은 DB·같은 응용 서비스 트랜잭션에서 함께 수정한다. 이는 `architecture-ddd` §3.3 규칙4의 "동일 DB 단순 케이스 용인"에 해당한다(분산되면 결과적 일관성으로 전환). 규칙4는 여기서 *애그리거트 일관성 경계 완화*로만 쓰며, BC 배치 근거로는 쓰지 않는다(§0 가드 참조).

### 1.2 "재고 충분 판정"의 소유 — 핵심 결정 (B1 방어)

- **판정과 차감은 도메인 `Product.deduct(quantity)`가 단독 소유한다.** 이 메서드가 유일한 권위(authority)다:
  - `quantity <= 0` → `ValueError`(또는 도메인 예외).
  - `stock < quantity` → 도메인 예외 `InsufficientStock`(재고 부족).
  - 그 외 → `self.stock -= quantity`.
- **리포지토리·SQL·응용 서비스에 "재고 충분" 판정을 복제하지 않는다.** 즉 `WHERE stock >= quantity` 같은 조건부 UPDATE로 판정을 인프라에 내려보내지 않는다 — 그렇게 하면 도메인 `deduct()`가 죽은 코드가 되는 B1(빈혈/죽은 도메인)이 발생한다. 이 결정은 B1-verify PoC(`workspace/design/b1-verify/FINDINGS.md`)에서 결정적으로 입증됐다: conditional UPDATE 변형은 `Product.deduct()`를 한 번도 호출하지 않았고(`calls == []`), repo 소스에 `stock__gte`가 박혀 "repository는 로직 없음" 원칙을 위반했다.
- *왜 도메인 소유인가*: `architecture-ddd` §3.6 — 응용 서비스는 흐름·트랜잭션만, 비즈니스 로직은 도메인에 위임. §7 — 불변식을 애그리거트로 감싸 자유도를 줄이는 게 DDD 전술 패턴의 본질. 판정이 SQL에 흩어지면 규칙의 단일 출처가 깨진다.

### 1.3 상태 전이

- `Product`: `stock = N` → (`deduct(q)`, `q <= N`) → `stock = N - q`. `q > N`이면 전이 거부(`InsufficientStock`).
- `Order`: (없음 → 생성) 단일 상태. 단일 품목 토이라 주문 라이프사이클(결제대기/준비/출고)은 범위 밖.

### 1.4 유비쿼터스 언어

| 용어 | 의미 |
|---|---|
| Product(상품) | 재고를 보유하는 애그리거트 |
| stock(재고) | 차감 가능한 수량. `stock >= 0` 불변식 |
| Order(주문) | 단일 품목 주문 사실. `product_id`로 Product 참조 |
| deduct(차감) | 재고 충분 판정 후 재고를 줄이는 도메인 연산(`Product` 소유) |
| InsufficientStock(재고 부족) | 차감 시 `stock < quantity`일 때의 도메인 규칙 위반 |

### 1.5 도메인 이벤트 — 채택하지 않음

- **이 기능에 도메인 이벤트를 도입하지 않는다.** `architecture-ddd` §6.8(가장 가벼운 패턴), 규칙4(즉시 일관성)에 근거.
  - 재고 차감은 **즉시 일관성**이 필요하다(oversell 차단). 결과적 일관성으로 미루면 oversell이 난다 → 동기 처리(같은 트랜잭션). 이벤트는 결과적 일관성용이라 부적합.
  - 외부 부수효과(결제·알림·포인트 적립)가 범위에 없다 → outbox/`on_commit` handoff 불필요(`architecture-db` §9.6: 외부 부수효과 없으면 outbox 피함).
  - `domain_layer/<aggregate>/event/` 폴더는 `references/final.md` §0 불변식대로 **빈 패키지로 생성**(`[선택]`=비어 있을 수 있음, 생략 아님). 트리거(외부 통지·결과적 일관성) 미충족이라 비어 있다.

---

## 2. 데이터·동시성 설계 (db lens) — 핵심

### 2.1 스키마 변화

- **`ProductModel`**(기존 `Product` ORM 확장): 기존 `name`·`price`·`stock`에 **`version`(PositiveIntegerField, default=0)** 컬럼 추가 — 낙관적 동시성 가드용.
  - `stock`: `PositiveIntegerField`. **추가로 CHECK 제약 `stock >= 0`**를 명시(엔진 무관 최종 방어선, §2.4).
- **`OrderModel`**(신규): `id`(BigAutoField PK), `product_id`(FK → `ProductModel`, `on_delete=PROTECT`), `quantity`(PositiveIntegerField, CHECK `quantity > 0`), `created_at`(auto_now_add).
  - FK 삭제 정책 `PROTECT`: 주문이 참조하는 상품은 삭제 금지(`architecture-db` §8.2 — 참조 무결성 보호).

### 2.2 동시성 수단 — 낙관적 동시성(version 가드) + CHECK 백스톱

**채택: Optimistic locking (version 컬럼 compare-and-swap) + 응용 서비스 재시도.** `architecture-db` §9.5 표의 "Optimistic locking(충돌이 드물고 retry 허용)" 전략. B1-verify PoC가 이 패턴이 (V1) 동시성 안전 + (V2) 도메인 규칙 소유 + repo 무로직을 **동시에** 만족하는 유일한 변형임을 입증했다.

메커니즘:
1. 응용 서비스가 리포지토리로 `Product`를 조회(현재 `stock`·`version`을 도메인 객체에 싣는다).
2. 도메인 `Product.deduct(quantity)` 호출 — **재고 충분 판정·차감이 여기서 일어난다**. 부족하면 `InsufficientStock` → 즉시 409 매핑(재시도 안 함).
3. 리포지토리 `save`가 `UPDATE ... SET stock=<new>, version=<v+1> WHERE id=<id> AND version=<읽은 v>` 단일 원자 UPDATE. 그새 다른 트랜잭션이 같은 행을 바꿨으면 **매칭 0건(rowcount=0)** → 경합 감지.
4. 경합(rowcount=0)이면 응용 서비스가 **fresh 재고로 1~3을 재시도**(상한 `max_retries=10`, 초과 시 `ConcurrencyConflict`). 재시도마다 도메인 규칙을 재실행하므로 stale 데이터로 oversell이 날 수 없다.

*왜 락이 아니라 낙관적인가*: §2.4 엔진차 참조. `select_for_update`(비관적 행 잠금)는 SQLite에서 no-op이라 환경 무관 정확성이 성립하지 않는다. version 가드 단일 UPDATE는 SQLite·Postgres 양쪽에서 원자적·portable하다(PoC 입증). 또한 version 가드는 `WHERE version=N`만 검사하므로 비즈니스 규칙(`stock>=qty`)을 **담을 수가 없다** → 규칙은 도메인 `deduct()` 말고 살 곳이 없어 B1을 구조적으로 불가능하게 만든다.

### 2.3 트랜잭션 경계·소유

- **Transaction owner**: 응용 서비스 `CreateOrderApp`(쓰기 유스케이스)이 트랜잭션 경계를 소유한다(`architecture-db` §9.6 Transaction owner; `architecture-ddd` §3.6 응용 서비스가 트랜잭션 관리). 한 유스케이스 호출 = `Product` 차감 + `Order` 생성을 한 트랜잭션(`transaction.atomic()`)으로 묶는다(같은 BC·같은 DB, §1.1 규칙4 용인).
- **재시도 루프와 트랜잭션의 관계**: 낙관적 경합 재시도는 **각 시도를 독립 `atomic()` 블록**으로 감싼다(읽기→deduct→save→commit). rowcount=0이면 그 시도를 롤백하고 fresh read로 다음 시도. 재시도 전체를 하나의 긴 트랜잭션으로 감싸지 않는다(락 hold time·스냅샷 고착 방지, §9.5 "락 범위 작게").

### 2.4 엔진별 동작 차이 확정 (개발 SQLite ↔ 운영 Postgres) — `architecture-db` §9.5

락·동시성이 걸린 Risky Write라 엔진차를 명세에서 확정한다(coder는 한 환경만 보므로 구현에서 메우면 G1' 반송).

| 측면 | SQLite(개발) | Postgres(운영) | 본 설계의 환경 무관 방어 |
|---|---|---|---|
| `select_for_update` | **no-op**(행 잠금 미지원) | 행 잠금 동작 | **사용 안 함** — 낙관적 version 가드로 통일 |
| 동시성 정확성 | 쓰기 직렬화(BUSY) | MVCC | **version compare-and-swap 단일 UPDATE**(양쪽 원자적·portable) |
| 최종 방어선 | CHECK 제약 | CHECK 제약 | **CHECK `stock >= 0`**(version 가드가 새도 음수 재고 불가) |
| begin 모드 | 기본 DEFERRED → SELECT→UPDATE 락 승격이 스레드 경합 시 데드락(`database is locked`) | 해당 없음 | 본 설계는 **읽기 후 단일 UPDATE**(락 승격 패턴 아님)라 DEFERRED에서도 데드락 경로 없음. 필요 시 테스트는 파일 DB로 BUSY 직렬화(PoC 기판 주의 참조). |

- **CHECK `stock >= 0`는 version 가드의 백스톱**: §9.5 "격리/락만으로 불변식이 안 지켜지면 제약을 함께 설계". version 가드가 동시성을 막고, CHECK가 어떤 경로로도 음수 재고가 영속화되지 않도록 DB 경계에서 최종 보장한다(§8.1 비즈니스 불변식의 DB 경계 보호).
- **`OrderModel.quantity > 0` CHECK**도 동일 근거로 DB 경계에 둔다.

### 2.5 멱등성 — 이번 범위에서 도입하지 않음 (근거 명시)

- `Idempotency-Key` 저장소를 도입하지 않는다(`architecture-db` §9.6 Idempotency storage = 미적용). *왜* — 스코프가 멱등성을 요구하지 않고(단일 POST 생성), 외부 결제 같은 duplicate-sensitive 중복 비용이 없다. 도입 시 트레이드오프는 §5 옵션으로 남긴다(현재 결정: 미도입).
- **API handoff**(§9.6): 멱등성 미도입이므로 `architecture-api` §13 키 계약과 맞출 항목 없음.

### 2.6 Side-effect timing·마이그레이션 안전

- **Side-effect timing**(§9.6): 외부 결제·알림·message publish **없음**. 따라서 commit 전/후 handoff·outbox 불필요(§9.6 기본: 외부 부수효과 없으면 트랜잭션 내 외부 호출 자체가 없음).
- **마이그레이션 안전**(§11): 기존 `Product`에 `version` 추가 = nullable 없는 컬럼이라도 **default=0**으로 추가하면 backfill 불필요(기존 행 0으로 채워짐, Expand 단계만으로 안전). 신규 `OrderModel`·CHECK 제약은 신규 테이블이라 lock risk 낮음. 토이 규모라 단계적 rollout(Expand/Backfill/Contract) 분리 불요 — 단일 마이그레이션으로 충분하나 그 *근거*(default로 backfill 회피)를 남긴다.

### 2.7 인덱스

- `OrderModel.product_id` FK는 Django가 자동 인덱스. 추가 인덱스 불요(토이·조회 패턴 단순, `architecture-db` §7.4 실제 액세스 패턴 없으면 추가 인덱스 만들지 않음).

---

## 3. API 계약 (api lens — 최소)

### 3.1 엔드포인트

- **`POST /api/orders`** — 주문 생성. POST = non-idempotent 생성(`architecture-api` §2.1).
- 요청 본문(JSON): `{ "product_id": <int>, "quantity": <int> }`. `quantity >= 1`. (`architecture-api` §5.1: 필수 필드·타입·허용범위 명시.)

### 3.2 응답·상태 코드 (`architecture-api` §4.2)

| 상황 | status | 본문 |
|---|---|---|
| 생성 성공 | **201 Created** | `{ "order_id": <int>, "product_id": <int>, "quantity": <int> }` + `Location: /api/orders/<order_id>` |
| 재고 부족(`InsufficientStock`) | **409 Conflict** | Problem Details(아래) |
| 요청 형식·검증 오류(`quantity < 1`, 타입 오류) | **400 Bad Request** | Problem Details |
| 존재하지 않는 product_id | **404 Not Found** | Problem Details |

- *왜 재고 부족이 409인가*: §4.2 — 409 Conflict = 자원 충돌(재고라는 공유 자원의 상태와 요청이 충돌). 422(문법은 맞지만 의미 처리 불가)도 후보지만, 재고는 **시점 의존 상태 충돌**이라 동일 요청이 나중엔 성공할 수 있어 409가 더 정확하다. (검증 실패인 `quantity < 1`은 400으로 구분.)

### 3.3 에러 형식 (RFC 9457 Problem Details — `architecture-api` §6)

- Content-Type: `application/problem+json`. 모든 에러 응답에 일관 적용(§6.3).
- 재고 부족 예:
```json
HTTP/1.1 409 Conflict
Content-Type: application/problem+json
{
  "type": "https://example.com/probs/insufficient-stock",
  "title": "Insufficient stock.",
  "status": 409,
  "detail": "Requested quantity 3 exceeds available stock 2.",
  "product_id": 1,
  "available": 2,
  "requested": 3
}
```
- `title`은 유형(재사용), `detail`은 특정 발생(§6.3). `product_id`·`available`·`requested`는 확장 필드.

### 3.4 멱등성 정책

- `Idempotency-Key` 미사용(§2.5 db 결정과 정합). POST 재시도 시 중복 주문 가능성은 토이 범위에서 수용. (`architecture-api` §13 미적용.)

---

## 4. 외부 관찰 가능 행위 목록 (인수 테스트의 근거)

인수 테스트(acceptance-tester)가 검증할 슬라이스:

1. **재고 충분 시 201 + 재고 차감**: `stock=5`에 `quantity=3` 주문 → `201`, 응답에 `order_id`, 이후 `Product.stock == 2`, `Order` 1건 생성.
2. **재고 부족 시 409, 차감 없음**: `stock=2`에 `quantity=3` 주문 → `409` Problem Details, `Product.stock == 2`(불변), `Order` 미생성.
3. **동시 주문에서 oversell 없음**: `stock=N`에 동시 주문이 몰려도 성공한 차감 합 ≤ N, `stock` 음수 불가, oversell 0건(낙관적 version 가드 + 재시도 검증). PoC `test_concurrency_deterministic`·`test_concurrency_threaded` 패턴 준용.
4. **재고 충분 판정이 도메인 경로를 실제로 탄다(B1 방어)**: 생성 성공 경로가 `Product.deduct()`를 실제 호출한다(죽은 코드 아님). repo 구현에 `stock>=`/`stock__gte` 비즈니스 판정이 없다(version 가드만). PoC `test_b1_structure` 패턴 준용.
5. **`quantity < 1` → 400**, **없는 product_id → 404**.

---

## 5. 미해소 트레이드오프 (G1에서 사용자 제시)

- **낙관적 동시성의 코드 비용**: version 컬럼 + 재시도 루프 + 충돌 예외가 단일 필드 감소엔 조건부 UPDATE보다 코드가 늘어난다(B1-verify FINDINGS 트레이드오프 절). 본 설계는 "DDD 핵심=도메인이 규칙 소유 / repo는 로직 없음"을 우선해 낙관적을 택했다(정당한 대가). *대안*: conditional 원자 UPDATE는 코드가 짧지만 도메인을 죽인다(B1) — 채택하지 않음. 사용자가 "토이라 단순성 우선"을 원하면 이 트레이드오프를 G1에서 재고할 수 있다.
- **멱등성 미도입**: 네트워크 재시도로 중복 주문이 생길 수 있다(§2.5·§3.4). 토이 범위라 수용. 필요 시 `Idempotency-Key` 도입을 후속 옵션으로.

---

## 6. 패키지·테스트 구조 (lens 무관 — 항상 결정)

### 6.1 레이아웃 결정 근거

- **dddjango 표준 파일트리 적용**(`discipline-houserules` §1.2 + `references/final.md`). *왜* — 기존 `catalog`는 루트 평면 `catalog/`(startapp 직후 `models.py`·`views.py`·`tests.py` 미조직)이라 §1.1의 "확립된 규약"이 아니다(startapp 직후 미조직 평면 답습 금지). 따라서 고정 기본값인 표준 트리를 적용한다. 한 프로젝트 안에서 레이아웃 혼용 금지(§1.4).
- **§0 불변식 전부 적용**(YAGNI·"단일 기능"으로 생략·축소 불가):
  1. `application/` 컨테이너 — 단일 앱이어도.
  2. 4계층 `_layer` 물리 분리.
  3. 개념 1차 폴더(`domain_layer/product/`·`domain_layer/order/`·`application_layer/create_order/`).
  4. **종류 2차 폴더 전체** — 비어도 폴더로(`entity/`·`value_object/`·`repository/`·`event/`·`command/`·`query/`·`dto/` 등 `__init__.py`만 둔 빈 패키지 포함). 평면 파일로 접지 않음.
  5. Django 앱은 `infra_layer/django_catalog/`에서 `startapp`.
  6. ORM 모델 클래스명 `<Name>Model`.

### 6.2 디렉터리 골격 (`application/catalog/`)

```
application/catalog/
├── catalog_api_router.py                  # POST /api/orders 등록 (루트 urls.py가 포함)
├── domain_layer/
│   ├── product/
│   │   ├── product.py                     # Product 애그리거트 — deduct(qty) 규칙 소유 (§1.2)
│   │   ├── entity/                        # (빈 패키지)
│   │   ├── value_object/                  # (빈 패키지)
│   │   ├── repository/
│   │   │   └── product_repository.py      # class ProductRepository(ABC)
│   │   ├── event/                         # (빈 패키지 — 이벤트 미채택 §1.5)
│   │   └── exception.py                   # InsufficientStock, ConcurrencyConflict
│   └── order/
│       ├── order.py                       # Order 애그리거트 (product_id로 참조)
│       ├── entity/  value_object/         # (빈 패키지)
│       ├── repository/
│       │   └── order_repository.py        # class OrderRepository(ABC)
│       └── exception.py
├── application_layer/
│   └── create_order/
│       ├── command/
│       │   └── create_order_app.py        # class CreateOrderApp — 트랜잭션 owner·재시도 루프 (§2.3)
│       ├── dto/
│       │   └── create_order_command.py    # 입력 DTO (product_id, quantity)
│       ├── query/  handler/  service/     # (빈 패키지)
│       └── (unit_of_work.py 불요 — transaction.atomic()으로 충분, §2.3)
├── infra_layer/
│   ├── django_catalog/
│   │   ├── apps.py                        # AppConfig.name='application.catalog.infra_layer.django_catalog', label='catalog'
│   │   ├── models/
│   │   │   ├── product_model.py           # class ProductModel (stock, version, CHECK stock>=0)
│   │   │   └── order_model.py             # class OrderModel (product_id FK, quantity CHECK>0)
│   │   ├── migrations/
│   │   └── admin/
│   ├── repository/
│   │   ├── product_repository.py          # class DjangoProductRepository — version 가드 save (§2.2), 로직 없음
│   │   └── order_repository.py            # class DjangoOrderRepository
│   └── service/                           # (빈 패키지 — 외부 서비스 없음)
├── presentation_layer/
│   ├── api/
│   │   └── create_order/
│   │       └── api_orders.py              # 얇은 어댑터: 파싱→CreateOrderApp 호출→201/409/400/404 변환
│   └── schema/
│       ├── schema_in.py                   # CreateOrderIn (product_id, quantity)
│       ├── schema_out.py                  # OrderOut (order_id, product_id, quantity) — 도메인 직접 노출 금지
│       └── error_out.py                   # Problem Details (RFC 9457, §3.3)
└── test/
    ├── unit/                              # 도메인·응용 단위 (행위 1·2·4의 도메인 부분, mock repo)
    ├── integration/                       # DB·리포지토리·HTTP 엔드포인트 (행위 1~5, 실제 DB) — 동시성 테스트 포함
    └── e2e/                               # [선택] 비어 있을 수 있음
```

- **`port/`·`acl/` 폴더 없음**: 단일 BC라 BC 간 직접 통합이 없다(§0). `[통합 시]`만 생성하는 폴더이므로 두지 않는다(`references/final.md` §3).
- **테스트 의미군 분리**(`implementation-test` §4.2 / houserules §1.3·§3): 도메인·응용 단위 = `unit/`, DB·리포지토리·HTTP 엔드포인트·동시성 = `integration/`. 평면 나열 금지.

### 6.3 §4 명명 규약 (이 명세가 도입하는 추상화·구현·ORM)

추상화 = 도메인 개념 + 역할 접미사 / 구현 = 기술 한정자 접두로 base명 일치 / `Interface`·`Impl` 금지 / 파일명 약어 없이(`references/final.md` §4):

| 종류 | 추상화(ABC) | 구현 | 파일 |
|---|---|---|---|
| 상품 리포지토리 | `ProductRepository` | `DjangoProductRepository` | `product_repository.py` |
| 주문 리포지토리 | `OrderRepository` | `DjangoOrderRepository` | `order_repository.py` |
| 도메인 엔티티 ↔ ORM | `Product` / `Order`(bare) | `ProductModel` / `OrderModel`(`<Name>Model`) | `product.py` / `product_model.py` |
| 응용 서비스(쓰기) | — | `CreateOrderApp` | `create_order_app.py` |

- **리포지토리 책임 경계(명세가 못박음)**: 리포지토리는 ORM↔도메인 변환 + 영속화(version 가드 save)만 한다. **비즈니스 판정(`stock >= qty`)을 담지 않는다** — 판정은 도메인 `Product.deduct()` 소유(§1.2·자기점검 §7). `save`는 rowcount를 반환해 응용 서비스가 경합을 감지하게 한다(§2.2).
- 포트 ABC는 `domain_layer/<aggregate>/repository/`, 구현은 `infra_layer/repository/`(DIP).

---

## 7. 자기점검 — 절 간 일관성 (1회 스캔 결과)

- **재고 판정 소유 일치**: §1.2·§2.2·§4.4·§6.3이 모두 "`Product.deduct()`가 판정 소유, 리포지토리·SQL은 무로직(version 가드만)"으로 일치. 인프라에 차감 로직을 두는 절 없음.
- **동시성 수단 일치**: §2.2·§2.3·§2.4가 모두 낙관적 version 가드 + 응용 서비스 재시도 + CHECK 백스톱으로 일치. `select_for_update`는 명시적 배제(엔진차).
- **트랜잭션 owner 일치**: §1.1·§2.3·§6.3이 모두 `CreateOrderApp`(응용 서비스) 소유로 일치.
- **이벤트 미채택 일치**: §1.5·§2.6이 모두 미채택(즉시 일관성·외부 부수효과 없음), `event/` 빈 패키지로 §6.2와 정합.
- **BC 단일·ACL 없음 일치**: §0·§1.1·§6.2가 모두 단일 catalog BC, `port/`·`acl/` 미생성으로 일치. 규칙4를 BC 근거로 오용하지 않음(§0 가드).
- **status code 일치**: §3.2 표와 §4 행위 목록이 201/409/400/404로 일치.
- 모순 미발견 — 넘김.
```
