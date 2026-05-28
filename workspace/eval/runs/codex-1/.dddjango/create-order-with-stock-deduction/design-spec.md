# Design Spec: create order with stock deduction

## 1. Scope and Context

- 기능 스코프: 단일 상품과 수량을 입력받아 재고가 충분할 때만 주문을 생성하고, 같은 트랜잭션 안에서 상품 재고를 차감한다.
- 제외: HTTP API, 결제, 배송, 고객, 장바구니, 복수 상품 주문, 할인, 환불, 예약, 백오더.
- 기존 구조: Django 4.2 프로젝트이며 루트 `catalog` 앱에 `Product(name, price, stock)` 모델만 있다. 주문 모델, 서비스 계층, API 라우트, 의미 있는 테스트 구조는 없다.
- 바운디드 컨텍스트 배치: 승인된 G0 기본안에 따라 이 기능은 기존 `catalog` 영역 안에 둔다. 이유: 현재 프로젝트는 단일 앱이고 재고 소유 모델이 `catalog.Product`로 이미 존재하므로, 별도 주문 컨텍스트를 만들면 이번 스코프보다 큰 앱/마이그레이션 재배치가 된다.
- 경계 한정: 물리 배치는 `catalog` 앱 안에 두지만, 이번 스코프의 `Order`는 단일 상품 구매 기록만 뜻한다. 결제, 배송, 고객, 장바구니를 포함하는 독립 Ordering 컨텍스트 언어로 확장하지 않는다.
- HTTP API: 이번 명세에서 다루지 않는다. 외부 계약, status code, 요청/응답 schema, Idempotency-Key는 스코프 밖이다.

## 2. Ubiquitous Language

- Product: 판매 가능한 상품. 현재 재고(`stock`)를 가진다.
- Stock: 주문으로 즉시 차감되는 상품 재고 수량.
- Order: 이번 `catalog` 스코프에서 단일 상품과 수량에 대한 구매 기록.
- Ordered Quantity: 주문하려는 양의 정수 수량.
- Stock Deduction: 주문 생성과 원자적으로 실행되는 재고 차감.
- Insufficient Stock: 요청 수량이 현재 재고보다 커서 주문을 만들 수 없는 도메인 실패.

## 3. Domain Design

### 3.1 Aggregates

- `Product`는 재고 차감 불변식을 소유하는 애그리거트다.
  - 불변식: `stock >= 0`.
  - 행위: `deduct_stock(quantity)`는 주문 수량이 양수이고 `stock >= quantity`일 때만 재고를 차감한다.
  - 조건부 원자 UPDATE는 이 행위의 동시성 방어선이다. 충분 재고 판단과 차감 의도는 Product 애그리거트 언어로 표현하고, 응용 서비스는 같은 조건을 DB에 위임해 오버셀을 막는다.
  - 이유: `architecture-ddd` §3.3은 진짜 불변식을 애그리거트 경계 안에서 보호하라고 한다. 재고 음수 방지는 Product의 핵심 불변식이다.
- `Order`는 주문 생성 사실을 기록하는 애그리거트다.
  - 불변식: `quantity > 0`, `unit_price >= 0`, `total_price = unit_price * quantity`, 주문은 정확히 하나의 Product ID를 참조한다.
  - 생성 정책: Order는 Product 재고 차감이 성공한 뒤에만 생성할 수 있다.
  - Product 객체를 직접 들고 있지 않고 `product_id`만 가진다.
  - 이유: `architecture-ddd` §3.3 규칙 3은 다른 애그리거트를 ID로 참조하라고 한다.

### 3.2 Cross-Aggregate Consistency

- 주문 생성과 재고 차감은 같은 DB 트랜잭션에서 처리한다.
- 이유: 일반 원칙은 애그리거트 간 결과적 일관성이지만, `architecture-ddd` §3.3 규칙 4의 실무 참고는 동일 DB의 단순 케이스에서 복수 애그리거트 수정을 한 트랜잭션으로 처리하는 예외를 허용한다. 이 기능은 오버셀 차단이 핵심이므로 결과적 일관성보다 즉시 일관성이 필요하다.
- 응용 서비스가 트랜잭션 owner다.
  - 흐름: 입력 검증 -> Product의 `deduct_stock(quantity)` 정책과 같은 조건으로 조건부 재고 차감 -> 상품 존재/재고 실패 구분 -> 주문 생성 -> 커밋.
  - Order 생성은 조건부 재고 차감 affected rows가 1인 경우에만 진행한다.
  - 이유: `architecture-ddd` §3.6은 응용 서비스가 리포지토리 조회, 도메인 실행, 트랜잭션 관리, 결과 반환을 담당한다고 한다. 비즈니스 규칙은 Product와 Order의 행위 언어로 남기고, 응용 서비스는 흐름과 트랜잭션을 오케스트레이션한다.

### 3.3 Domain Events

- 도메인 이벤트와 outbox는 도입하지 않는다.
- 이유: 이번 스코프에는 외부 부수효과, 비동기 통합, 유실 방지 메시지 발행이 없다. `architecture-ddd` §6.8은 단순 직선 흐름에는 이벤트 소싱, saga, outbox, ACL을 기본 도입하지 말라고 한다.

### 3.4 Domain Errors

- `ProductNotFound`: 대상 상품이 없다.
- `InvalidOrderQuantity`: 주문 수량이 0 이하이다.
- `InsufficientStock`: 재고가 부족하다.
- DB lock timeout, deadlock, connection failure 같은 저장소 실패는 도메인 실패로 바꾸지 않는다. 재시도 정책이 없는 현재 스코프에서는 원래 DB 예외를 상위로 전파한다.
- 이 예외들은 HTTP status로 매핑하지 않는다. HTTP API가 스코프 밖이기 때문이다.

## 4. Application Behavior

### 4.1 Use Case

- 유스케이스 이름: create order with stock deduction.
- 입력 command: `product_id`, `quantity`.
- 출력 result: 생성된 `order_id`, `product_id`, `quantity`, `unit_price`, `total_price`, 남은 재고.
- 성공 조건:
  - 상품이 존재한다.
  - 수량이 양수이다.
  - Product가 `stock >= quantity` 조건으로 재고를 차감할 수 있다.
  - 주문 행이 생성된다.
  - 상품 재고가 주문 수량만큼 차감된다.
  - 주문 생성과 재고 차감은 같은 트랜잭션으로 커밋된다.
- 실패 조건:
  - 상품이 없으면 주문을 만들지 않고 재고를 변경하지 않는다.
  - 수량이 0 이하이면 주문을 만들지 않고 재고를 변경하지 않는다.
  - 재고가 부족하면 주문을 만들지 않고 재고를 변경하지 않는다.

### 4.2 Observable Behaviors for Acceptance Tests

- 재고가 충분한 상품에 대해 주문 생성 요청을 실행하면 주문이 생성되고 상품 재고가 요청 수량만큼 감소한다.
- 재고가 정확히 요청 수량과 같으면 주문이 생성되고 상품 재고는 0이 된다.
- 재고가 요청 수량보다 적으면 `InsufficientStock` 실패가 발생하고 주문 수와 상품 재고는 변경되지 않는다.
- 같은 상품에 대한 동시 주문이 재고 합계를 초과하면 성공한 주문들의 총 수량만큼만 재고가 차감되고, 초과 요청은 실패한다.
- 주문 생성 중 예외가 발생하면 주문과 재고 차감이 함께 롤백된다.

## 5. Data Design

### 5.1 Schema

- 기존 `catalog_product` 테이블을 유지한다.
- `Product.stock`에는 DB 수준 `stock >= 0` check constraint를 명시한다.
  - 이유: `architecture-db` §8.1은 단일 행 값 범위 규칙은 Check constraint로 보호하라고 한다.
- 새 주문 테이블을 추가한다.
  - 모델명: `Order`.
  - 테이블명: Django 기본값 `catalog_order`.
  - 필드:
    - `id`: `BigAutoField` primary key.
    - `product`: `ForeignKey` to `Product`, `on_delete=PROTECT`.
    - `quantity`: integer, `quantity > 0` check constraint.
    - `unit_price`: non-negative integer snapshot of product price at order time, `unit_price >= 0` check constraint.
    - `total_price`: non-negative integer snapshot, `total_price >= 0` and `total_price = unit_price * quantity` check constraints.
    - `created_at`: timestamp set on creation.
- `total_price`는 조회 시 계산하지 않고 주문 생성 시점의 금액 스냅샷으로 저장한다.
  - 이유: 주문 이력은 상품 가격 변경 이후에도 생성 시점 금액을 보존해야 한다. 저장된 중복 값의 불일치 위험은 DB check constraint(`total_price = unit_price * quantity`)로 막는다.
- `on_delete=PROTECT`를 사용한다.
  - 이유: `architecture-db` §8.2는 참조 중인 데이터 삭제를 금지해야 하는 경우 Restrict/Protect를 사용하라고 한다. 주문 이력은 상품 삭제로 함께 지워지면 안 된다.

### 5.2 Indexes

- `Order.product_id`는 FK 인덱스를 사용한다.
- `Order.created_at` 단독 인덱스는 지금 추가하지 않는다.
  - 이유: 현재 스코프는 조회/API가 없고, `architecture-db` §7은 실제 액세스 패턴 기반으로 인덱스를 결정하라고 한다.

### 5.3 Transaction and Locking

이 기능은 주문과 재고를 다루는 Risky Write다. `architecture-db` §9.6에 따라 다음을 확정한다.

| 항목 | 결정 |
|---|---|
| Transaction owner | create order 응용 서비스 |
| Locking strategy | 조건부 원자 UPDATE를 1차 방어선으로 사용한다: `WHERE id = product_id AND stock >= quantity` 조건으로 재고를 차감하고, affected rows가 1일 때만 주문을 생성한다. |
| Idempotency storage | 도입하지 않는다. HTTP API와 retry replay 계약이 스코프 밖이고, caller-level idempotency key가 없다. |
| API handoff | 없음. API lens 비활성. |
| Side-effect timing | 외부 부수효과 없음. |
| Isolation/retry | 기본 DB 격리 수준을 사용한다. 조건부 UPDATE의 affected rows가 0이면 실패 후 존재 여부를 재조회해 `ProductNotFound`와 `InsufficientStock`을 구분한다. DB lock timeout/deadlock은 재고 부족 도메인 실패가 아니므로 재시도하지 않고 상위로 전파한다. |
| Test criteria | 충분한 재고, 정확히 0이 되는 재고, 부족 재고, 상품 없음과 재고 부족의 구분, 동시 요청 초과, 롤백을 검증한다. |

- SQLite 개발 환경: `select_for_update`에 의존하지 않는다. SQLite는 `select_for_update`를 no-op으로 무시할 수 있으므로, 환경 무관 정확성은 조건부 UPDATE와 check constraint로 확보한다.
- SQLite 동시성 테스트: PostgreSQL row-level locking과 동일한 락 동작을 기대하지 않는다. 통합 테스트는 `TransactionTestCase` 또는 트랜잭션 DB 사용 조건에서 affected rows 판단, check constraint, 롤백을 중심으로 검증하고, SQLite에서 재현되지 않는 lock wait/deadlock 세부 동작은 acceptance 기준으로 삼지 않는다.
- PostgreSQL 운영 가정: 조건부 UPDATE만으로도 오버셀 방지가 가능하다. 필요 시 같은 조건부 UPDATE 앞뒤에 짧은 트랜잭션을 유지하되 외부 I/O를 넣지 않는다.
- 이유: `architecture-db` §9.5는 SQLite의 `select_for_update` no-op과 DEFERRED begin 락 승격 문제를 명세에서 분기하고, 환경 무관 방어선으로 CHECK와 조건부 원자 UPDATE를 사용하라고 한다.

### 5.4 Rollout

- 기존 데이터 점검: 현재 `Product.stock` 값이 모두 0 이상인지 확인한다.
- 새 constraint 추가 전에 위 조건을 만족하지 않는 데이터가 있으면 cleanup 후 migration을 적용한다.
- 새 `Order` 테이블은 신규 테이블이므로 backfill은 없다.
- 이 smoke 프로젝트는 소규모 개발 DB(`db.sqlite3`)를 전제로 하므로 단순 Django migration을 허용한다.
- 운영 PostgreSQL 대용량 테이블에 같은 변경을 적용한다면 check constraint는 `NOT VALID` 추가 후 `VALIDATE CONSTRAINT` 같은 단계적 검증으로 lock risk를 줄인다.
- 이유: `architecture-db` §8.4와 §11은 기존 데이터가 있는 테이블의 새 제약조건은 데이터 점검과 rollout 순서를 먼저 설계하라고 한다.

## 6. Package and Test Structure

### 6.1 Source Placement

- 이번 슬라이스는 기존 `catalog` Django 앱 안에 둔다.
- 이유: G0에서 기존 `catalog` 영역 확장이 승인되었고, `Product` 모델과 마이그레이션이 이미 `catalog` 앱 라벨에 귀속되어 있다. dddjango 표준 파일트리의 `application/<app>/.../infra_layer/django_<app>/` 재배치는 별도 구조 마이그레이션 작업으로 분리한다.
- 새 코드의 물리 배치 결정:
  - `catalog/models.py`: `Order` ORM 모델과 `Product.stock >= 0`, `Order.quantity > 0`, `Order.unit_price >= 0`, `Order.total_price >= 0`, `Order.total_price = unit_price * quantity` 제약조건을 둔다. 기존 프로젝트가 이미 root `models.py`를 쓰므로 이 슬라이스에서는 앱 라벨/마이그레이션 안정성을 우선한다.
  - `catalog/services.py`: create order 응용 서비스를 둔다. 함수 또는 얇은 service class는 구현 단계에서 기존 코드 규모에 맞춰 선택하되, 트랜잭션 경계와 조건부 UPDATE는 이 모듈이 소유한다.
  - `catalog/exceptions.py`: `ProductNotFound`, `InvalidOrderQuantity`, `InsufficientStock`를 둔다.
- 명명:
  - 기존 ORM 클래스는 `Product` 그대로 유지한다. 새 ORM 클래스도 기존 Django 앱 관례에 맞춰 `Order`로 둔다.
  - 별도 repository/port/ACL은 만들지 않는다.
  - 이유: `architecture-ddd` §6.8은 현재 압력을 해결하는 가장 가벼운 패턴을 선택하고, 단순 직선 흐름에는 리포지토리, 커스텀 UoW, ACL을 기본 도입하지 말라고 한다.

### 6.2 dddjango Standard Tree Tradeoff

- 이 프로젝트는 `startproject`/`startapp` 직후에 가까운 평면 구조라 `discipline-houserules` §1 기준으로는 dddjango 표준 파일트리 적용 후보이다.
- 표준 파일트리의 생략 불가 불변식은 다음이다: `application/` 컨테이너, 4계층 `_layer` 물리 분리, 개념 1차 폴더, 종류 2차 폴더 전체, Django 앱은 `infra_layer/django_<app>/`, ORM 모델 클래스명은 `<Name>Model` 패턴.
- 이번 명세는 표준 파일트리를 새로 깔지 않는다.
- 이유: 승인된 기능 범위는 기존 `catalog.Product` 재고와 주문 생성이고, 표준 트리 도입은 기존 앱 라벨, migration path, `INSTALLED_APPS`, ORM 모델명을 바꾸는 구조 작업이다. 이는 재고 차감 기능보다 큰 변경 이유를 가진다.

### 6.3 Test Placement

- 기존 `catalog/tests.py` 평면 파일은 새 테스트에 사용하지 않는다.
- 새 테스트는 의미군으로 분리한다.
  - `catalog/tests/unit/test_create_order_domain.py`: 수량 검증, 가격 계산, 부족 재고 판단처럼 DB 없이 검증 가능한 단위 규칙.
  - `catalog/tests/integration/test_create_order_with_stock_deduction.py`: 실제 DB transaction, 조건부 UPDATE, 주문 생성/롤백, 동시성 방어.
- 이유: `discipline-houserules` §1.3은 테스트를 최소 unit/integration 의미군으로 나누고 평면 나열을 금지한다.

## 7. Self-Consistency Check

- 재고 차감 규칙은 Product의 `deduct_stock(quantity)` 행위와 불변식으로 정의하고, 실제 동시성 방어는 DB 조건부 UPDATE로 수행한다. 도메인 규칙과 DB 방어선은 같은 `stock >= quantity` 조건을 공유한다.
- Order 생성은 Product 재고 차감 성공 이후에만 가능하다.
- Order는 Product를 객체 참조하지 않고 `product_id`/FK로만 참조한다.
- 저장된 `total_price`는 `unit_price * quantity` DB check constraint로 보존한다.
- 응용 서비스가 트랜잭션 owner이고, 모델이나 view가 트랜잭션 오케스트레이션을 소유하지 않는다.
- HTTP API 관련 status, schema, router는 명세에 포함하지 않았다.
- 외부 부수효과가 없으므로 도메인 이벤트와 outbox를 도입하지 않는다.
