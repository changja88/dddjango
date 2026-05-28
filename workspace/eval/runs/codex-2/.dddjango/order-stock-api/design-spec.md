# 재고 기반 주문 생성 API 설계 명세

## 1. 컨텍스트와 기존 구조

- 이 기능은 사용자 G0 선택에 따라 기존 `catalog` 영역에 포함한다. `order`를 별도 바운디드 컨텍스트로 분리하지 않는다.
  - 왜: 현재 프로젝트에는 `catalog` 앱 하나와 `Product(name, price, stock)`만 있고, 이번 요구는 한 상품 재고 차감과 주문 생성이 같은 즉시 일관성 경계에서 끝난다(`architecture-ddd` 핵심 원칙: 전략 경계 우선, 애그리거트는 진짜 불변식만 보호).
- 여기서 `catalog`는 전략적으로 독립된 Catalog BC라기보다 현재 프로젝트의 단일 기능 영역이다. 결제, 배송, 주문 상태 전이, 취소/환불이 추가되면 Sales/Order 영역 분리를 다시 검토한다.
  - 왜: 유비쿼터스 언어는 바운디드 컨텍스트 안에서만 유효하며(`architecture-ddd` §2.3), 현재 요구만으로 미래 주문 생명주기까지 같은 경계로 고정하면 성급한 전략 경계가 된다.
- 현재 구조는 Django `startproject/startapp` 직후의 평면 구조(`catalog/models.py`, `catalog/tests.py`)이며, 확립된 소스/테스트 레이아웃 규약은 없다.
  - 왜: `discipline-houserules` §1은 확립된 규약이 없거나 미조직이면 dddjango 표준 파일트리를 적용하라고 정한다.
- 기존 `catalog` 앱 라벨과 DB 앱 라벨은 `catalog`로 유지한다.
  - 왜: 기존 마이그레이션 기록과 `catalog_product` 테이블을 보존해야 하며, `discipline-houserules`는 Django 앱을 새 위치로 옮기더라도 `AppConfig.label='<app>'`를 유지하는 표준을 둔다.

## 2. 유비쿼터스 언어

- `Product`: 판매 가능한 상품. `stock`은 주문 가능 재고 수량이다.
- `Order`: 한 상품에 대한 주문 생성 결과. 이번 범위에서는 결제·배송·상태 전이를 갖지 않는 생성 기록이다.
- `quantity`: 주문하려는 상품 수량. 1 이상이어야 한다.
- `reserve stock`: 주문 생성을 확정하기 위해 상품 재고를 최종 차감하는 도메인 행위다. 임시 hold, 만료, release 의미는 이번 범위에 없다.
- `insufficient stock`: 요청 수량이 현재 재고보다 커서 주문을 생성할 수 없는 상태다.

## 3. 도메인 설계

### 3.1 애그리거트와 불변식

- `Product` 애그리거트가 재고 불변식을 소유한다.
  - 불변식: `stock >= 0`.
  - 행위: `reserve(quantity)`는 `quantity >= 1`이고 재고가 충분할 때만 성공하며, 성공 시 재고를 최종 차감한다. 부족하면 `InsufficientStock` 도메인 예외를 낸다.
  - 왜: 재고가 음수가 되지 않는 규칙은 상품 재고의 핵심 도메인 규칙이며, `architecture-ddd` §3.3의 애그리거트 불변식 보호 기준에 맞는다.
- `Order` 애그리거트는 생성된 주문 기록을 소유한다.
  - 불변식: `quantity >= 1`, `unit_price >= 0`, `total_price = quantity * unit_price`.
  - 저장 정책: `total_price`는 저장하지 않고 `quantity * unit_price`로 계산한다.
  - 행위: `Order.create(product_id, quantity, unit_price)`는 유효한 주문 기록을 만든다.
  - 왜: 주문 생성 결과는 재고 차감과 다른 변경 이유를 갖는 기록이므로 `Product` 내부 엔티티로 넣지 않는다. 파생값을 저장하지 않으면 DB 제약으로 계산식을 중복 보장할 필요가 없다(`architecture-db` §3 정규화, §8 제약조건).
- 이번 유스케이스는 같은 `catalog` 기능 영역 안에서 `Product` 재고 차감과 `Order` 생성을 하나의 DB 트랜잭션으로 묶는다.
  - 왜: 오버셀 방지는 즉시 일관성이 필요하고, 단일 DB 안의 단순 케이스에서는 여러 애그리거트 변경을 한 트랜잭션에 묶을 수 있다(`architecture-ddd` §3.3 규칙4의 애그리거트 수준 예외).

### 3.2 도메인 이벤트

- 도메인 이벤트는 도입하지 않는다.
  - 왜: 이번 범위는 외부 통지, 포인트, 배송, 결제 등 결과적 일관성 후속 처리가 없고, `architecture-ddd` §6.8은 명확한 필요가 확인된 시점에 패턴을 선택하라고 한다.

### 3.3 응용 흐름

- `CreateOrderApp`는 `CreateOrderCommand(product_id, quantity)`를 입력으로 받는다.
- 흐름:
  1. 요청 수량을 1 이상으로 검증한다.
  2. `ProductRepository.reserve(product_id, quantity)`를 호출해 `Product.reserve(quantity)` 의미를 원자적으로 영속화하고 상품 가격과 차감 후 재고를 얻는다.
  3. `Order.create(...)`로 주문 도메인 객체를 만든다.
  4. `OrderRepository.save(order)`로 주문을 저장한다.
  5. 주문 식별자와 차감 후 재고를 응답 DTO로 반환한다.
- 응용 서비스는 트랜잭션 경계를 소유하지만 비즈니스 판단은 도메인 객체와 리포지토리 포트의 의미 있는 행위에 위임한다.
  - 왜: `architecture-ddd` §3.6은 응용 서비스가 흐름 제어와 트랜잭션 관리만 담당하라고 정한다.
- 조건부 `UPDATE`는 `DjangoProductRepository`의 영속성 구현 세부사항이며, 도메인 계약은 `Product.reserve()`가 재고 규칙의 단일 행위라는 점이다.
  - 왜: 도메인은 인프라를 직접 알지 않고 안정적인 역할에 의존해야 하며(`architecture-ddd` §5.1, §5.2), 동시성 방어는 DB lens의 Risky Write 구현 전략이다.

## 4. API 계약

### 4.1 엔드포인트

- `POST /api/orders/`
  - 의미: 한 상품에 대한 주문을 생성한다.
  - 멱등성: 멱등하지 않다. `Idempotency-Key`는 이번 범위에서 제외한다.
  - 인증: 없음. 이번 범위에서 제외한다.
  - 왜: `architecture-api` §2는 생성 요청을 non-idempotent `POST`로 구분하고, §3은 URL을 명사·복수형 리소스로 설계하라고 정한다.
- 이 엔드포인트는 무버전 `/api/` 경로에 추가한다. 기존 엔드포인트가 없으므로 하위 호환성 영향은 신규 추가에 한정한다.
  - 왜: 버전 전략과 하위 호환성은 API 변경 전에 명시해야 한다(`architecture-api` §10, §11).
- OpenAPI 산출물은 현재 프로젝트에 없으므로 이번 G0 범위에서 새로 만들지 않는다. 이후 OpenAPI를 도입하면 이 명세의 path, method, schema, response, error, header 계약을 그대로 반영한다.
  - 왜: `architecture-api` §14는 계약을 OpenAPI에 반영하라고 정하지만, 새 문서 생성은 현재 기능 구현 범위를 넘는다.
- `Idempotency-Key`를 지원하지 않으므로 클라이언트는 timeout, 네트워크 오류, 5xx 뒤에 같은 요청을 자동 재시도하지 않는다. 재시도하면 중복 주문과 중복 재고 차감이 발생할 수 있으며, 서버는 이를 중복 제거하지 않는다.
  - 왜: 중복 민감 생성 요청의 멱등성 정책은 계약으로 고정해야 한다(`architecture-api` §13). 이번 범위에서는 저장소 기반 멱등성 키를 도입하지 않는다.

### 4.2 요청

```json
{
  "product_id": 1,
  "quantity": 2
}
```

- `Content-Type`: `application/json`만 지원한다. 다른 Content-Type은 `415 Unsupported Media Type` Problem Details를 반환한다.
- `Accept`: 협상을 강제하지 않고 JSON 기본 정책을 쓴다. `Accept`가 없거나 `*/*`, `application/json`, `application/problem+json`이 아니어도 406을 반환하지 않고 성공은 `application/json`, 에러는 `application/problem+json`으로 응답한다.
- 본문 필드:
  - `product_id`: 정수, 필수, nullable 아님.
  - `quantity`: 정수, 필수, nullable 아님, `>= 1`.
- 추가 필드는 무시한다.
  - 왜: G0 범위를 늘리지 않기 위해 strict unknown-field validation은 도입하지 않는다. 필수 필드와 타입은 명시적으로 검증한다(`architecture-api` §5, §7).

### 4.3 성공 응답

- 상태: `201 Created`
- `Content-Type`: `application/json`
- `Location` 헤더는 반환하지 않는다.
- 본문:

```json
{
  "order_id": 10,
  "product_id": 1,
  "quantity": 2,
  "unit_price": 5000,
  "total_price": 10000,
  "remaining_stock": 3
}
```

- 응답 필드:
  - `order_id`: 정수, 필수, nullable 아님.
  - `product_id`: 정수, 필수, nullable 아님.
  - `quantity`: 정수, 필수, nullable 아님.
  - `unit_price`: 정수, 필수, nullable 아님. 상품 가격 스냅샷이며 정수 원화(KRW) 단위로 소수점은 쓰지 않는다.
  - `total_price`: 정수, 필수, nullable 아님. `quantity * unit_price` 계산값이며 저장 컬럼이 아니다.
  - `remaining_stock`: 정수, 필수, nullable 아님.
- 주문 조회 API는 이번 범위에서 구현하지 않는다.
  - 왜: 생성 응답은 생성 결과와 식별자를 명시해야 하며(`architecture-api` §5), 조회 엔드포인트와 `Location` 대상 리소스 제공은 G0 범위 밖이다.

### 4.4 에러 응답

에러 본문은 RFC 9457 Problem Details 형식(`application/problem+json`)을 사용한다.

- 공통 필드:
  - `type`: 문자열, 필수, nullable 아님.
  - `title`: 문자열, 필수, nullable 아님.
  - `status`: 정수, 필수, nullable 아님.
  - `detail`: 문자열, 필수, nullable 아님.
- extension field는 문제 유형별로 명시한 필드만 사용한다.

- 재고 부족:
  - 상태: `409 Conflict`
  - `Content-Type`: `application/problem+json`
  - `type`: `/problems/insufficient-stock`
  - extension field: `product_id`(정수), `requested_quantity`(정수), `available_stock`(정수)
  - 본문:

```json
{
  "type": "/problems/insufficient-stock",
  "title": "Insufficient stock",
  "status": 409,
  "detail": "Requested quantity exceeds available stock.",
  "product_id": 1,
  "requested_quantity": 5,
  "available_stock": 3
}
```

- 상품 없음:
  - 상태: `404 Not Found`
  - `Content-Type`: `application/problem+json`
  - `type`: `/problems/product-not-found`
  - extension field: `product_id`(정수)
- 요청 JSON 파싱 실패 또는 필드 타입 오류:
  - 상태: `400 Bad Request`
  - `Content-Type`: `application/problem+json`
  - `type`: `/problems/invalid-request`
  - extension field: `invalid_fields`(문자열 배열, 필드 단위 식별이 가능할 때만)
- 필수 필드 누락:
  - 상태: `400 Bad Request`
  - `Content-Type`: `application/problem+json`
  - `type`: `/problems/invalid-request`
  - extension field: `invalid_fields`(누락된 필드명 배열)
- 수량이 1 미만:
  - 상태: `422 Unprocessable Content`
  - `Content-Type`: `application/problem+json`
  - `type`: `/problems/invalid-order-quantity`
- 지원하지 않는 Content-Type:
  - 상태: `415 Unsupported Media Type`
  - `Content-Type`: `application/problem+json`
  - `type`: `/problems/unsupported-media-type`
- SQLite write lock 등 일시적 DB busy:
  - 상태: `503 Service Unavailable`
  - `Content-Type`: `application/problem+json`
  - `type`: `/problems/database-busy`
  - `Retry-After`는 반환하지 않는다.

왜: `architecture-api` §4는 상태 코드를 의미에 맞게 구분하고, §6은 에러 응답에 Problem Details 형식을 쓰라고 정한다. 재고 부족은 현재 리소스 상태와 충돌하므로 `409`가 맞다.

### 4.5 API 구현 방식

- 새 외부 의존성을 추가하지 않고 Django 기본 JSON view로 구현 가능한 계약을 기준으로 한다.
  - 왜: 현재 설치 패키지는 Django뿐이며, 이번 기능의 본질은 계약과 트랜잭션이다. 프레임워크 추가는 G0 범위 밖이다.
- `config.urls`는 `application.catalog.catalog_api_router`를 `/api/` 하위에 include한다.
- HTTP 어댑터는 JSON 파싱, 응용 서비스 호출, 응답/Problem Details 변환만 담당한다.
  - 왜: 표현 계층은 얇은 입력 어댑터여야 한다(`discipline-houserules` 표준 트리 §2).

## 5. 데이터 설계

### 5.1 ORM 모델

- 기존 `Product` ORM 모델은 표준 명명으로 `ProductModel`이 된다.
  - 필드: `id`, `name`, `price`, `stock`.
  - `price`: 정수 원화(KRW) 단위이며 소수점은 쓰지 않는다.
  - `db_table='catalog_product'`를 지정해 기존 테이블명을 보존한다.
  - 제약: `stock >= 0`, `price >= 0`.
- 새 `OrderModel`을 추가한다.
  - 필드:
    - `id`: `BigAutoField`
    - `product`: `ForeignKey(ProductModel, on_delete=PROTECT)`
    - `quantity`: `PositiveIntegerField`
    - `unit_price`: `PositiveIntegerField`
    - `created_at`: `DateTimeField(auto_now_add=True)`
  - 제약:
    - `quantity >= 1`
    - `unit_price >= 0`
  - 인덱스:
    - 별도 복합 인덱스는 추가하지 않는다. Django `ForeignKey`가 만드는 기본 `product_id` 인덱스만 둔다.
  - 왜: 이번 범위에는 상품별 주문 목록 조회가 없으므로 `product_id, created_at` 복합 인덱스는 실제 액세스 패턴 없이 쓰기 비용만 늘린다(`architecture-db` §7). `total_price`는 파생값이므로 저장하지 않아 SQLite용 계산 CHECK 제약도 필요 없다.

### 5.2 마이그레이션

- 기존 앱 라벨 `catalog`의 마이그레이션 연속성을 유지한다.
- 구현 시 마이그레이션은 다음 의도를 반영한다.
  - `Product` 모델 상태를 `ProductModel`로 rename한다.
  - `ProductModel.Meta.db_table='catalog_product'`로 기존 DB 테이블명을 유지한다.
  - `OrderModel` 테이블을 추가한다.
  - `ProductModel.stock`, `OrderModel.quantity` 등에 check constraint를 추가한다.
- 대용량 backfill은 없다.
  - 왜: 새 주문 테이블은 빈 테이블로 추가되고, 기존 상품 테이블에는 이름/제약 보강만 필요하다. `architecture-db` §11의 Expand/Backfill/Contract 중 Backfill 단계가 필요하지 않다.
- 구현 게이트에서 `sqlmigrate` 또는 생성 migration 파일을 확인해 `Product` -> `ProductModel` 변경이 물리 `catalog_product` 테이블 rename, drop, recreate로 이어지지 않는지 검증한다.
  - 왜: 기존 데이터를 보존하는 rename/state 변경이어야 하며, 운영 rollout에서는 destructive migration을 명시적으로 차단해야 한다(`architecture-db` §11).

### 5.3 트랜잭션과 동시성

- `CreateOrderApp` 전체를 `transaction.atomic()`으로 감싼다.
- 재고 차감은 엔진 공통으로 조건부 `UPDATE`를 사용한다.
  - 의미: `UPDATE product SET stock = stock - quantity WHERE id = product_id AND stock >= quantity`.
  - Django ORM 구현 의도: `ProductModel.objects.filter(pk=product_id, stock__gte=quantity).update(stock=F("stock") - quantity)`.
  - 영향 행 수가 1이면 재고 차감 성공, 0이면 상품 존재 여부를 확인해 `ProductNotFound` 또는 `InsufficientStock`으로 변환한다.
- 조건부 `UPDATE` 뒤에는 같은 트랜잭션에서 갱신된 상품 row를 다시 읽어 `Product.reserve()` 결과와 동일한 `unit_price`, `remaining_stock` 응답 데이터를 구성한다. 조건부 `UPDATE` 자체를 도메인 규칙의 소유자로 보지 않는다.
- `select_for_update()`에 의존하지 않는다.
  - SQLite: `select_for_update()`가 실질적으로 no-op이므로 오버셀 방어가 되지 않는다. 조건부 `UPDATE`는 단일 쓰기 문장과 check constraint로 방어한다.
  - PostgreSQL: `READ COMMITTED`에서 조건부 `UPDATE`가 행 잠금을 잡고 predicate를 재평가하므로 오버셀을 방지한다.
- SQLite `database is locked` 같은 lock 오류는 자동 재시도하지 않는다. 저장소/응용 경계에서 일시적 DB busy 오류로 변환하고 API는 `503 Service Unavailable` Problem Details를 반환한다.
  - 테스트 보장 수준: 실제 동시성 스트레스 테스트는 G0 범위에서 제외하고, repository 또는 transaction 경계가 DB busy 예외를 변환하는 단위/통합 테스트로 보장한다.
- 주문 저장은 재고 차감 성공 이후 같은 트랜잭션에서 실행한다.
- 트랜잭션 안에서 외부 I/O는 실행하지 않는다.
  - 왜: 이 작업은 `architecture-db` §9.6의 Risky Write(주문·재고)에 해당하므로 transaction owner, locking strategy, isolation/retry, test criteria가 명시되어야 한다. 외부 부수효과 금지는 §9.7 원칙이다.

### 5.4 실패 시 데이터 상태

- 재고 부족이면 `OrderModel` row는 생성되지 않고 `ProductModel.stock`도 변경되지 않는다.
- 요청 검증 실패나 상품 없음도 DB 변경 없이 끝난다.
- DB check constraint는 애플리케이션 버그가 있더라도 음수 재고와 0 이하 수량 저장을 막는 최후 방어선이다.
  - 왜: `architecture-db` §8은 DB 경계에서 지켜야 하는 비즈니스 불변식에 constraint를 사용하라고 정한다.

## 6. 패키지·테스트 구조 결정

### 6.1 레이아웃 결정

- 확립된 기존 규약이 없으므로 dddjango 표준 파일트리를 적용한다.
- 기존 `catalog` 기능은 `application/catalog/` 아래로 옮긴다. 단, Django 앱 라벨은 `catalog`를 유지한다.
- 표준 파일트리 §0 불변식:
  1. 단일 앱이어도 `application/` 컨테이너 아래에 둔다.
  2. `domain_layer/`, `application_layer/`, `infra_layer/`, `presentation_layer/` 4계층을 모두 물리 분리한다.
  3. `domain_layer/<aggregate>/`, `application_layer/<feature>/`처럼 개념 1차 폴더를 둔다.
  4. `entity/`, `value_object/`, `repository/`, `command/`, `query/`, `dto/` 등 종류 2차 폴더는 비어도 폴더로 유지하고 `__init__.py`를 둔다.
  5. Django 앱은 `application/catalog/infra_layer/django_catalog/`에 둔다. `AppConfig.name='application.catalog.infra_layer.django_catalog'`, `label='catalog'`로 둔다. 앱 루트 `models.py`는 금지한다.
  6. 도메인 엔티티/애그리거트는 bare 이름(`Product`, `Order`), Django ORM 모델은 `<Name>Model`(`ProductModel`, `OrderModel`)로 구분한다.

왜: `discipline-houserules` §1과 `references/final.md` §0은 미조직 프로젝트에서 이 불변식을 생략·축소하지 말라고 정한다.

### 6.2 소스 배치

```text
application/
  catalog/
    catalog_api_router.py
    domain_layer/
      product/
        product.py
        entity/
        value_object/
        repository/
          product_repository.py        # ProductRepository
        exception.py
      order/
        order.py
        entity/
        value_object/
        repository/
          order_repository.py          # OrderRepository
        exception.py
    application_layer/
      create_order/
        command/
          create_order_app.py          # CreateOrderApp
        dto/
          create_order_command.py      # CreateOrderCommand
        query/
        handler/
        service/
    infra_layer/
      django_catalog/
        apps.py                        # CatalogConfig, label='catalog'
        models/
          product_model.py             # ProductModel
          order_model.py               # OrderModel
        migrations/
        admin/
      repository/
        product_repository.py          # DjangoProductRepository
        order_repository.py            # DjangoOrderRepository
      service/
    presentation_layer/
      api/
        create_order/
          api_orders.py
      schema/
        schema_in.py
        schema_out.py
        error_out.py
    test/
      unit/
      integration/
      e2e/
```

- ACL/port 폴더는 만들지 않는다.
  - 왜: 같은 `catalog` 기능 영역 내부에서 `Product`와 `Order`를 다루므로 외부 컨텍스트 소비가 없다. `discipline-houserules` 표준 트리 §2는 외부 컨텍스트 직접 통합 때만 ACL을 둔다.
- 리포지토리/포트 명명:
  - 추상화: `ProductRepository`, `OrderRepository`.
  - 구현: `DjangoProductRepository`, `DjangoOrderRepository`.
  - 파일명: `product_repository.py`, `order_repository.py`.
  - 금지: `Interface`, `Impl`, `repo` 약어.
  - 왜: `discipline-houserules` §4는 추상화는 개념명+역할 접미사, 구현은 기술 한정자 접두로 base명을 일치시키라고 정한다.

### 6.3 테스트 구조

- 단위 테스트: `application/catalog/test/unit/`
  - `Product.reserve` 수량 검증과 재고 부족 예외.
  - `Order.create` 총액 계산과 수량 검증.
  - `CreateOrderApp` 흐름은 fake repository로 성공/부족/상품없음 경로 검증.
- 통합 테스트: `application/catalog/test/integration/`
  - `POST /api/orders/` 성공 시 `201`, 주문 생성, 재고 차감.
  - 재고 부족 시 `409`, 주문 미생성, 재고 불변.
  - 상품 없음 `404`, invalid request `400`(JSON 파싱 실패, 필드 타입 오류, 필수 필드 누락), invalid quantity `422`, unsupported media type `415`.
  - DB busy 예외가 `503` Problem Details로 변환되는지 검증한다. 실제 동시성 스트레스 검증은 제외한다.
  - DB repository의 조건부 update가 재고를 음수로 만들지 않는지 검증.
- E2E 테스트: 이번 범위에서는 필수 아님. 폴더는 표준 구조로 두되 테스트는 비워둘 수 있다.
  - 왜: `discipline-houserules` §1.3은 테스트를 의미군으로 분리하라고 정하고, HTTP 엔드포인트 테스트는 integration에 둔다.

## 7. 외부 관찰 가능 행위

인수 테스트는 아래 행위를 검증한다.

1. 재고가 충분한 상품에 `POST /api/orders/`를 호출하면 `201 Created`를 반환한다.
2. 성공 응답은 `order_id`, `product_id`, `quantity`, `unit_price`, `total_price`, `remaining_stock`를 포함한다.
3. 성공 시 주문 row가 생성되고 상품 재고가 요청 수량만큼 차감된다.
4. 재고가 부족하면 `409 Conflict`와 `/problems/insufficient-stock` Problem Details를 반환한다.
5. 재고 부족 실패 시 주문 row가 생성되지 않고 상품 재고가 변경되지 않는다.
6. 존재하지 않는 상품이면 `404 Not Found` Problem Details를 반환한다.
7. 요청 JSON이 잘못됐거나 필드 타입이 맞지 않으면 `400 Bad Request` Problem Details를 반환한다.
8. 필수 필드가 누락되면 `400 Bad Request` Problem Details를 반환한다.
9. 수량이 1 미만이면 `422 Unprocessable Content` Problem Details를 반환한다.
10. `Content-Type`이 `application/json`이 아니면 `415 Unsupported Media Type` Problem Details를 반환한다.
11. SQLite write lock 등 DB busy 오류는 자동 재시도하지 않고 `503 Service Unavailable` Problem Details로 변환된다.
12. `total_price`는 저장 컬럼이 아니라 응답에서 `quantity * unit_price`로 계산된다.

## 8. 자기 일관성 점검

- `catalog`는 기존 영역 선택을 유지하지만 물리 구조는 미조직 상태라 표준 트리로 재배치한다. 새 BC를 만들지 않는다.
- `catalog`는 현재 단일 기능 영역이며, 결제/배송/상태 전이가 생기기 전까지 전략적 Sales/Order 분리를 고정하지 않는다.
- 재고 규칙 소유자는 `Product.reserve()`이며, DB 조건부 update와 check constraint는 같은 불변식의 동시성/저장소 방어다.
- API의 `409`는 도메인 `InsufficientStock` 예외에서만 변환한다.
- ORM 이름은 `ProductModel`/`OrderModel`, 도메인 이름은 `Product`/`Order`로 일관한다.
- `total_price`는 도메인/응답 계산값이고 DB 저장 컬럼이 아니다.
- 조회 엔드포인트가 없으므로 `201 Created` 응답에 `Location`을 보내지 않는다.
- `Idempotency-Key`와 자동 중복 제거는 지원하지 않으며, 클라이언트 자동 재시도도 계약상 금지한다.
- ACL과 도메인 이벤트는 이번 범위에 도입하지 않는다.
