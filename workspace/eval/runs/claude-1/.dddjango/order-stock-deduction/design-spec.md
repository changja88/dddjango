# 통합 설계 명세 — 재고 차감 주문 생성 API

기능: 재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.
활성 lens: ddd · api · db. 이 명세는 이후 인수 테스트·구현 코드의 단일 근거다.

---

## 0. 컨텍스트와 배치 (고정 제약 — 하위 모두 이 절만 읽는다)

G0에서 사용자가 확정해 본 명세가 준수하는 제약(임의 변경 금지):

- **BC 배치**: 주문(Order)은 신규 개념이나 **기존 `catalog` 바운디드 컨텍스트(앱)에 포함**한다. 새 앱(`orders`) 분리 금지. *왜* — Product(상품·재고)와 Order(주문)는 같은 카탈로그/판매 유비쿼터스 언어를 공유하고 한 팀·한 DB가 소유하므로 단일 BC다. 별개 BC가 아니라서 **컨텍스트 간 ACL/OHS는 도입하지 않는다**(같은 BC 내 애그리거트 협력은 ACL 대상이 아님 — houserules §2 / final.md §2). 이 판단은 `architecture-ddd` §3.3 규칙4(애그리거트 일관성 경계 완화)가 아니라 **유비쿼터스 언어·소유 경계**로 내린다(규칙4를 BC 합치기 근거로 오용 금지).
- **API 어댑터**: 순수 Django `JsonResponse` 뷰. DRF·Django Ninja·기타 패키지 도입 금지.
- **테스트 러너**: Django 기본 `TestClient` + `manage.py test`. pytest 전제 금지.
- **의존성**: Django 4.2.30뿐. 추가 패키지 없이 설계·구현한다.
- **DB**: 개발·운영 모두 현재는 sqlite(db.sqlite3). 단 락 전략은 §4(db)에서 sqlite·Postgres 엔진차까지 확정해 환경 이주에도 안전하게 둔다.

스코프 경계(스코프 메모): 단일 상품·단일 수량 주문 생성 + 재고 검증·차감 + 부족 시 거절만 포함. 결제·장바구니·멀티라인·취소/환불·재고 복원·인증/인가는 **이번 범위 밖**(익명 허용).

---

## 1. 도메인 설계 (ddd lens)

### 1.1 애그리거트 경계

두 개의 별개 애그리거트가 한 BC(`catalog`) 안에 공존한다.

- **Product 애그리거트(루트)** — 기존. `stock`(재고)을 소유하며 **재고 차감의 불변식을 자기 경계 안에서 보호**한다(`architecture-ddd` §3.3 규칙1: 진짜 불변식은 애그리거트 경계 안에서). 차감 로직은 Product가 소유한다 — 다른 어떤 계층(응용·인프라)도 stock을 직접 빼지 않는다.
- **Order 애그리거트(루트)** — 신규. 어떤 상품을 얼마나 주문했는지(product_id, quantity)와 주문 시점 단가·합계를 보유한다. **Product를 ID로만 참조**한다(규칙3) — Order는 Product 객체를 품지 않는다.

단일 라인 전제이므로 Order는 OrderItem 자식 엔티티를 두지 않고 루트에 `product_id`·`quantity`·`unit_price`·`total_price`를 직접 둔다(규칙2: 일관성에 필요한 최소 크기). *왜* — 멀티라인은 스코프 밖이고, 자식 엔티티는 보호할 추가 불변식이 없어 YAGNI(`architecture-ddd` §3.3 규칙2).

### 1.2 불변식 (검증 가능)

- **I1 (Product)**: 차감 수량 `qty`에 대해 `stock >= qty`여야 차감 가능. 위반 시 도메인 예외(재고 부족) — 차감하지 않는다.
- **I2 (Product)**: 차감 후 `stock >= 0`. PositiveIntegerField + DB CHECK로 음수 영속화를 원천 차단(§4).
- **I3 (입력)**: `quantity >= 1`(정수). 0·음수·비정수는 도메인에 도달하기 전 입력 검증에서 거절.
- **I4 (Order)**: 생성된 Order의 `quantity`는 차감된 수량과 일치하고 `total_price = unit_price * quantity`. **Order 생성자(도메인)가 이 곱을 강제**한다(응용이 미리 계산해 넘기지 않는다).

### 1.3 상태 전이

- Product: `stock = s` → (차감 성공) → `stock = s - qty`. 실패 시 전이 없음(불변).
- Order: (없음) → `CREATED`. 이번 범위에서 Order는 생성 후 다른 상태로 가지 않는다(취소·결제 스코프 밖). **`status`는 도메인 불변식이 아니라 표현 계약상 고정 리터럴이다** — 도메인 `Order`는 status를 모르고(생성=성립의 단일 사실만 보유), 표현 계층 `schema_out`이 응답에 `"CREATED"` 상수를 채운다. DB `OrderModel.status`는 향후 상태 전이 도입 자리로 default `'CREATED'` 컬럼만 둔다(도메인 전이 없음 — 전이가 생기면 그때 도메인으로 끌어올린다). *왜* — 단일 상태를 도메인 불변식으로 모델링하면 보호할 전이가 없어 빈혈/장식이 되므로(§1.4 권위 원칙과 동일), 표현·영속 계약 레벨에만 둔다.

### 1.4 재고 차감 책임 배치 (소유권 — 자기모순 방지 기준)

재고 차감은 **이중 방어선 단일 모델**로 설계한다 — 도메인이 규칙의 **권위(authority)**, DB 조건부 UPDATE가 동시성 **안전망(safety net)**이다. 둘은 충돌이 아니라 같은 불변식(I1·I2)을 두 경계에서 집행하는 한 모델이다(`architecture-ddd` §3.3 규칙1: 진짜 불변식은 애그리거트 경계 안에서 보호).

- **도메인(Product 애그리거트) = 규칙의 권위**: `Product.deduct(qty)`는 순수 메서드로 I1(`stock >= qty`)·I2(`차감 후 stock >= 0`)의 **권위 있는 검사·결정**을 수행한다. 재고 부족이면 도메인 예외 `InsufficientStock`을 던지고 상태를 바꾸지 않는다(I1 위반=전이 없음). 성공이면 in-memory stock을 `stock - qty`로 줄여 차감 결정을 내린다. 차감 산술·판정의 권위는 오직 여기다 — 다른 어떤 계층도 stock을 직접 빼지 않는다. **이 메서드는 빈혈/장식이 아니다**: 차감 가능 여부의 비즈니스 판정이 여기서 일어나고, 단위 테스트(§5.6)가 이 메서드를 DB 없이 직접 검증한다.
- **인프라(리포지토리) = 동시성 안전망**: `DjangoProductRepository`의 조건부 원자 UPDATE(`WHERE stock >= qty`, §4.3)는 도메인이 내린 차감 결정을 **영속화**하면서, 읽기-검사-쓰기 사이의 race만 흡수한다. 이는 새 비즈니스 규칙이 아니라 도메인 I1·I2를 DB 경계에서 한 번 더 보장하는 *불변식의 영속 집행*이다(§4와 §1.4가 같은 규칙을 두 경계에서 — 모순 아님). **rowcount=0은 도메인 예외 `InsufficientStock`과 동일한 "재고 부족"을 의미한다** — 단일 프로세스에선 도메인 `deduct()`가 먼저 걸러내지만, 동시 차감으로 도메인 검사 통과 후 UPDATE 시점에 재고가 사라진 race에서는 rowcount=0이 그 부족을 잡는다.
- **응용 서비스(유스케이스) = 흐름·트랜잭션 + 번역**: 흐름·트랜잭션 경계만 소유하고 비즈니스 로직을 두지 않는다(`architecture-ddd` §3.6). 아래 순서를 한 `transaction.atomic()`으로 조율한다:
  1. **Product 존재 확인** — 리포지토리로 Product 조회. 없으면 `ProductNotFound` → 404(차감 시도 전에 먼저 분기).
  2. **unit_price 스냅샷 확보** — 조회한 Product의 현재 `price`를 읽어 Order 생성 입력으로 전달.
  3. **차감 위임** — `Product.deduct(qty)` 호출로 도메인 권위 검사. 부족이면 `InsufficientStock` → 409. 이어 리포지토리 조건부 UPDATE로 영속화하고, **rowcount=0이면 `InsufficientStock`과 동일하게 번역**해 409로 보낸다(race 흡수 → 도메인 의미로 환원). UPDATE 성공(rowcount=1)이면 차감 확정.
  4. **Order 생성** — `Order`를 `unit_price`로 생성하고 `total_price = unit_price * quantity`를 **Order 생성자(도메인)가 강제**한다(I4 — 응용이 곱셈을 미리 계산해 넘기지 않는다). 저장.
- **인프라(리포지토리) 추가 책임**: ORM↔도메인 변환과 영속화. 차감 산술을 인프라가 *발명*하지 않는다 — UPDATE의 `stock - qty`는 도메인이 내린 결정의 영속 표현일 뿐이다.

> 두 애그리거트(Product 차감 + Order 생성)를 **한 트랜잭션**에서 수정한다. over-sell 차단은 **즉시 일관성**이 필수라 결과적 일관성(이벤트)으로 미룰 수 없다(final.md §2 통합 스타일: 즉시 일관성=동기). 단일 DB·동기 흐름이므로 같은 트랜잭션에서 복수 애그리거트를 수정한다(`architecture-ddd` §3.3 규칙4의 동일-DB 단순 케이스 일관성 완화). 단 **이 규칙4는 애그리거트 *일관성 경계* 완화이지 BC 합치기 근거가 아니다** — Product·Order를 같은 catalog BC에 두는 판단은 규칙4가 아니라 유비쿼터스 언어·소유 경계로 내렸다(§0).

### 1.5 도메인 이벤트 — 채택 안 함

`OrderCreated`/`StockDeducted` 등 도메인 이벤트를 **이번 범위에서 도입하지 않는다**. *왜* — 외부 부수효과(알림·포인트·결제)가 모두 스코프 밖이고, 재고 차감은 같은 트랜잭션 내 즉시 일관성이라 결과적 일관성 전파가 불필요하다(`architecture-ddd` §3.7 / final.md §2: 결과적 일관성·외부 통지가 필요할 때만 이벤트). `event/` 폴더는 §0 불변식상 빈 패키지로 생성하되 비워 둔다.

### 1.6 유비쿼터스 언어

| 용어 | 의미 |
|---|---|
| Product | 상품. 재고(stock)를 보유하는 판매 단위 |
| stock | 가용 재고 수량(차감 대상) |
| Order | 단일 상품·수량의 주문(생성됨=CREATED) |
| quantity | 주문 수량(>=1) |
| unit_price | 주문 시점 Product.price 스냅샷(주문 생성 시 확정·이후 불변) |
| 재고 부족 (out of stock / insufficient stock) | `stock < quantity` 상태 — 409로 거절 |
| 차감 (deduct) | 주문 성립 시 `stock`을 `quantity`만큼 줄이는 것 |

---

## 2. API 계약 (api lens)

### 2.1 엔드포인트

| 항목 | 값 |
|---|---|
| Method | `POST` |
| Path | `/orders` |
| 의미 | 주문 리소스 생성(non-idempotent, RFC 9110 — `architecture-api` §2) |
| Auth | 없음(익명 허용 — 스코프 밖) |
| Content-Type(요청) | `application/json` |

URL은 명사·복수형(`orders`), 동사 미포함(`architecture-api` §3). Order는 catalog BC 소속이나 외부 리소스 명은 `/orders`로 노출한다(URL은 도메인 패키지 배치와 독립).

### 2.2 요청 본문

```json
{ "product_id": 1, "quantity": 2 }
```

| 필드 | 타입 | 필수 | 제약 |
|---|---|---|---|
| `product_id` | integer | 필수 | 양의 정수, 기존 Product PK |
| `quantity` | integer | 필수 | `>= 1` 정수 |

**Content-Type 정책 (요청)**: 본 API는 요청 `Content-Type` 헤더를 **엄격 검증하지 않는다** — 헤더가 `application/json`이 아니거나 누락돼도 415로 거절하지 않고, **본문을 JSON으로 파싱 시도해 성공 여부로만 판정**한다(파싱 실패 시 400, §2.5). *왜* — 순수 Django `JsonResponse` 환경에 콘텐츠 협상 미들웨어가 없고, 익명·단일 엔드포인트라 협상 복잡도를 들이는 이득이 없다(`architecture-api` §7 콘텐츠 협상은 필요할 때만). 415는 도입하지 않는다. **406(Not Acceptable)도 도입하지 않는다** — 응답 표현은 성공=`application/json`·에러=`application/problem+json`으로 고정이라 협상 여지가 없다.

### 2.3 응답 — 상태 코드별 계약 (외부 관찰 가능 행위)

| 상황 | 상태 코드 | 본문 | 헤더 |
|---|---|---|---|
| 재고 충분 → 주문 생성 + 차감 | **201 Created** | 성공 본문(§2.4) | `Location: /orders/{id}`, `Content-Type: application/json` |
| **재고 부족** | **409 Conflict** | Problem Details(§2.5) | `Content-Type: application/problem+json` |
| 상품 없음 | **404 Not Found** | Problem Details | `Content-Type: application/problem+json` |
| 입력 검증 실패(필드 누락·비정수·`quantity<=0`·JSON 파싱 실패) | **400 Bad Request** | Problem Details | `Content-Type: application/problem+json` |
| 허용되지 않은 메서드(GET 등) | **405 Method Not Allowed** | Problem Details | `Content-Type: application/problem+json`, `Allow: POST` |

*왜 각 코드*:
- 201 — POST 자원 생성 성공 표준, `Location`으로 새 자원 URI 제공(`architecture-api` §4.2·§5.2).
- **409** — 자원 상태 충돌(재고와 요청 수량 충돌). 스코프가 확정한 코드. 입력은 문법·의미상 유효하나 현재 재고 상태와 충돌하므로 422가 아니라 409가 맞다(`architecture-api` §4.2: 409=자원 충돌).
- 404 — 참조 자원(Product) 없음(§4.2).
- 400 — 잘못된 요청 형식·유효성 실패(§4.2). 본 API는 422 대신 400으로 통일한다(검증 실패를 한 코드로 단순화; 의미상 충돌인 재고 부족만 409로 분리). *왜 422 미사용* — 입력 검증 실패와 재고 충돌을 400/409로 명확히 가르면 클라이언트가 재시도 가능성(입력 고치면 됨 vs 재고 회복 대기)을 코드만으로 판별 가능.
- **405** — POST 외 메서드. `Allow: POST` 헤더를 RFC 9110 §10.2.1에 따라 **계약으로 포함**한다(허용 메서드 광고 — `architecture-api` §5.2·§7 헤더). Django `require_http_methods`/뷰 메서드 분기가 405 시 `Allow`를 자동/명시 부여한다.

### 2.4 성공(201) 본문

```json
{
  "id": 10,
  "product_id": 1,
  "quantity": 2,
  "unit_price": 1000,
  "total_price": 2000,
  "status": "CREATED"
}
```

응답은 도메인 엔티티를 직접 직렬화하지 않고 표현 계층 스키마(DTO)로 구성한다(final.md §2 Published Language — 도메인 직접 노출 금지). 순수 Django 환경이므로 스키마는 dict 구성 함수로 구현한다(별도 직렬화 패키지 없음). `status`는 표현 계약상 고정 리터럴 `"CREATED"`로 `schema_out`이 채운다(§1.3 — 도메인 Order는 status를 모른다).

### 2.5 에러 본문 — RFC 9457 Problem Details (`architecture-api` §6)

Content-Type `application/problem+json`. 공통 필드 `type`·`title`·`status`·`detail`.

재고 부족(409) 예:
```json
{
  "type": "about:blank",
  "title": "Insufficient stock",
  "status": 409,
  "detail": "Product 1 has stock 1 but 2 was requested.",
  "product_id": 1,
  "available_stock": 1,
  "requested_quantity": 2
}
```

입력 검증 실패(400) 예 — 필드 검증 실패(`errors` 포함):
```json
{
  "type": "about:blank",
  "title": "Invalid request",
  "status": 400,
  "detail": "Request validation failed.",
  "errors": {
    "quantity": "must be an integer >= 1",
    "product_id": "this field is required"
  }
}
```

입력 검증 실패(400) — **JSON 파싱 실패** 분기(`errors` 생략, `detail`에만 사유):
```json
{
  "type": "about:blank",
  "title": "Invalid request",
  "status": 400,
  "detail": "Request body is not valid JSON."
}
```

| 상황 | status | title | 확장 필드 |
|---|---|---|---|
| 재고 부족 | 409 | `Insufficient stock` | `product_id`, `available_stock`, `requested_quantity` |
| 상품 없음 | 404 | `Product not found` | `product_id` |
| 입력 검증 실패(필드) | 400 | `Invalid request` | `errors`(필드→사유 맵) |
| 입력 검증 실패(JSON 파싱) | 400 | `Invalid request` | (`errors` 생략 — `detail`만) |
| 메서드 불가 | 405 | `Method not allowed` | — |

`errors`는 **필드명→사유 문자열 맵**으로 고정한다(필드 단위 검증 실패만). JSON 자체가 파싱 불가하면 필드를 특정할 수 없으므로 `errors`를 생략하고 `detail`에 파싱 실패 사유만 담는 **분기 규칙**을 둔다(`schema_in`/`error_out`이 두 분기를 구분 생성). `type`은 전용 URI 미운영이라 `about:blank`로 둔다(§6.1: 생략 시 about:blank). `status`는 실제 HTTP 코드와 일치. 인수 테스트는 상태 코드 + `title`/`status` + 핵심 확장 필드(특히 409의 `available_stock`, 400 필드 검증의 `errors`)를 검증한다.

### 2.6 멱등성 — 이번 범위 도입 안 함

`Idempotency-Key`를 **도입하지 않는다**. *왜* — 본 범위는 재시도 중복 방지가 요구사항에 없고, 인증·결제가 빠져 중복 주문 비용이 정의되지 않았다(`architecture-api` §13: duplicate-sensitive일 때 도입). over-sell(동시성) 방지는 멱등성이 아니라 §4 트랜잭션·조건부 UPDATE로 푼다 — 둘은 다른 문제다. 향후 결제 도입 시 §13 정책을 추가하는 것을 확장 자리로 남긴다.

---

## 3. 외부 관찰 가능 행위 목록 (인수 테스트의 근거)

1. 재고 충분(stock >= quantity): 201 + `Location` + 성공 본문, **Order 1건 생성**, **Product.stock이 정확히 quantity만큼 감소**.
2. 재고 부족(stock < quantity): 409 + Problem Details(`available_stock` 포함), **Order 미생성**, **Product.stock 불변**.
3. 존재하지 않는 product_id: 404, Order 미생성, 재고 불변.
4. quantity 누락/0/음수/비정수, product_id 누락: 400 + `errors`(필드→사유). JSON 파싱 실패: 400 + `errors` 생략·`detail`만. 모두 Order 미생성, 재고 불변.
5. 잘못된 메서드(GET /orders): 405 + **`Allow: POST` 헤더**.
6. **동시성**: 같은 Product에 동시 주문이 들어와도 차감 합계가 초기 재고를 초과하지 않는다(over-sell 없음). stock=1에 동시 quantity=1 주문 2건 → 정확히 1건 201·1건 409, 최종 stock=0(검증 기준·실행 모델은 §4.2 Test criteria·§4.6).

---

## 4. 데이터 설계 (db lens)

### 4.1 스키마 변경

기존 `catalog_product`(Product: name, price, stock=PositiveIntegerField default=0)는 **CHECK 추가 외 컬럼 변경 없음**(아래 CHECK 제약 참조). 신규 테이블 1개 추가.

**OrderModel** (ORM 클래스명 `OrderModel`; 도메인 `Order`와 구분 — §0 불변식6 / houserules §4):

| 컬럼 | 타입 | 제약 |
|---|---|---|
| `id` | BigAutoField | PK |
| `product_id` | FK → catalog_product(id), `on_delete=PROTECT` | not null, 인덱스(FK 자동) |
| `quantity` | PositiveIntegerField | not null, CHECK `quantity >= 1` |
| `unit_price` | PositiveIntegerField | not null(주문 시점 단가 스냅샷) |
| `total_price` | PositiveIntegerField | not null, CHECK `total_price = unit_price * quantity` |
| `status` | CharField(max_length=20) | not null, default `'CREATED'` |
| `created_at` | DateTimeField | `auto_now_add=True` |

- FK `on_delete=PROTECT` — 주문이 가리키는 상품의 임의 삭제로 주문 무결성이 깨지지 않게(주문은 catalog 역사 기록). *왜* — CASCADE면 상품 삭제가 주문을 지워 회계 불변식 위반.
- `unit_price`/`total_price`를 주문 시점에 **스냅샷**으로 저장 — 이후 Product.price가 바뀌어도 주문 금액은 불변(도메인 I4). 역정규화가 아니라 시점 사실 보존(`architecture-db` §4 — 정규화 우선이나 시점 스냅샷은 도메인 사실).
- 인덱스: `product_id`(FK 기본 인덱스)로 본 범위 충분. 추가 인덱스는 조회 요구가 없어 두지 않음(`architecture-db` §7 — 실제 액세스 패턴 기반).

**CHECK 제약**:
- `OrderModel`: `quantity >= 1`(I3 영속 보장).
- `OrderModel`: `total_price = unit_price * quantity`(**I4의 DB 경계 집행**). *왜* — I1·I2를 CHECK로 DB 경계에서 집행하기로 했으므로(아래 Product CHECK), 도메인 불변식의 DB 집행 일관성을 위해 I4도 동일 기준을 적용한다(`architecture-db` §8: 불변식이 DB 경계에서 지켜져야 하면 CHECK). 단일 라인이라 비용이 낮고, 응용이 곱을 잘못 계산해 영속화하는 경로를 원천 차단한다.
- `Product`: `stock >= 0` CHECK를 **추가**한다(I2의 DB 경계 집행). *왜* — PositiveIntegerField는 Django 폼/필드 검증일 뿐 sqlite에서 음수 차감을 항상 막지 못하므로, CHECK로 음수 영속화를 원천 차단(`architecture-db` §8). 이는 기존 Product 테이블에 제약을 더하는 마이그레이션이다(§4.5 안전성).

### 4.2 트랜잭션·동시성 — Risky Write Consistency Block (`architecture-db` §9.6)

재고 차감은 Risky Write(재고)다. §9.6 항목을 모두 확정한다.

| 항목 | 결정 |
|---|---|
| **Transaction owner** | 응용 서비스(주문 생성 유스케이스)가 `transaction.atomic()`으로 단일 트랜잭션 경계를 소유. Product 차감 + Order insert가 원자적. |
| **Locking strategy** | **CHECK 제약 + 조건부 원자 UPDATE**(아래 §4.3)를 환경 무관 1차 방어선(안전망)으로 한다. 도메인 `Product.deduct()`가 권위 검사(§1.4), DB 조건부 UPDATE가 race 안전망 — 이중 방어선. pessimistic row lock(`select_for_update`)은 운영(Postgres) 보조로만, sqlite에선 no-op이므로 정확성을 거기 의존하지 않는다. |
| **Idempotency storage** | 없음(§2.6 — 멱등성 미도입). |
| **API handoff** | `Idempotency-Key` 미사용(§2.6). |
| **Side-effect timing** | 외부 부수효과 없음(알림·결제 스코프 밖). on_commit 핸드오프 불필요. |
| **Isolation/retry** | 아래 §4.3 엔진별. sqlite는 직렬화 성격이 강함, Postgres는 Read Committed + 조건부 UPDATE의 원자성으로 충분(별도 retry 루프 불필요 — 조건부 UPDATE 단일 문이 race를 흡수). |
| **Test criteria** | over-sell 0을 **결정적으로** 증명한다(§4.6 실행 모델). 1차 증명: 리포지토리 조건부 UPDATE를 같은 stock=1 행에 두 번 호출 → 첫 호출 rowcount=1·두 번째 rowcount=0, 최종 stock=0(결정적·엔진 무관). 보강: 파일 기반 sqlite + `TransactionTestCase` + OS 스레드 2개 동시 POST → 1건 201·1건 409·최종 stock=0. 단위 테스트는 `Product.deduct()`의 부족 시 `InsufficientStock`과 응용의 rowcount=0→409 번역을 검증. |

### 4.3 over-sell 방지 메커니즘 — 환경 무관 조건부 원자 UPDATE

핵심은 "읽고-검사하고-쓰기"의 TOCTOU 경쟁을 **단일 원자 UPDATE**로 없애는 것이다. 이는 §1.4 이중 방어선의 *안전망*이며, 권위는 도메인 `Product.deduct()`에 있다.

```
UPDATE catalog_product
   SET stock = stock - :qty
 WHERE id = :product_id
   AND stock >= :qty
```

- 이 UPDATE의 **affected rowcount로 성공/실패를 판정**한다: `1`이면 차감 성공, `0`이면 (상품 존재 & stock<qty) 재고 부족 → 트랜잭션 롤백 후 409. (상품 자체가 없으면 차감 전 조회에서 404로 먼저 분기 — §1.4 흐름 1단계.)
- **rowcount=0은 도메인 예외 `InsufficientStock`과 동일한 의미**로 응용 서비스가 번역한다(§1.4) — race로 도메인 검사 통과 후 재고가 사라진 경우를 잡는 안전망.
- `WHERE stock >= :qty` 가드가 불변식 I1을, CHECK `stock >= 0`이 I2를 DB 경계에서 보장한다.
- *왜 이 방식* (`architecture-db` §9.5 엔진 의존성): **sqlite는 `select_for_update`를 no-op으로 무시**(행 잠금 미지원)하고, Django 기본 **DEFERRED begin**은 atomic 내 SELECT→UPDATE 락 승격이 스레드 경합 시 `database is locked` 데드락을 낼 수 있다. 따라서 "select_for_update로 잠그고 파이썬에서 검사 후 빼기"는 sqlite에서 over-sell을 못 막는다. 조건부 원자 UPDATE는 **DB가 단일 문 안에서 검사+차감을 원자 수행**하므로 엔진 무관하게 race를 흡수한다(Django F-expression + filter로 표현).

### 4.4 엔진별 동작 차이 (개발 sqlite ↔ 운영 Postgres) — 명세 확정

| 측면 | sqlite (현재) | Postgres (이주 시) |
|---|---|---|
| 조건부 원자 UPDATE | 단일 문 원자 실행 — over-sell 방지 성립 | 동일하게 성립(행 단위 원자 UPDATE) |
| `select_for_update` | **no-op**(무시) — 정확성 의존 금지 | 실제 row lock — 보조 가능하나 본 설계는 불필요 |
| 동시 쓰기 | 파일 락 직렬화. 경합 시 `database is locked` 가능 → `atomic()` 짧게 유지, 필요 시 connection의 `busy_timeout`(예 5000ms)과 `isolation_level`/begin 모드(IMMEDIATE) 설정으로 완화 | MVCC 동시성. 조건부 UPDATE가 lost update 방지 |
| 격리 수준 | 사실상 직렬화에 가까움 | Read Committed로 충분(조건부 UPDATE가 가드) |

본 설계의 정확성은 **CHECK + 조건부 UPDATE**에만 의존하므로 두 엔진 모두에서 over-sell이 발생하지 않는다. 락은 운영 성능 최적화 여지로 남기되 본 범위에서 코드로 강제하지 않는다(YAGNI). sqlite `database is locked` 완화 설정(busy_timeout)은 안정성 보강이지 정확성 조건이 아니다 — coder는 정확성을 락이 아니라 조건부 UPDATE로 집행한다. 별도 retry 루프는 불필요하다 — **단, 이는 조건부 원자 단일 문 UPDATE 경로를 유지하는 한**의 결론이다(다중 문 read-then-write로 회귀하면 race·retry 재고가 필요해진다).

### 4.5 마이그레이션 안전성 (`architecture-db` §11 / §8)

- **신규 테이블 `catalog_order`**: 새 테이블 생성은 기존 트래픽 무영향. 단순 add — Expand 단계만으로 안전. `quantity >= 1`·`total_price = unit_price * quantity` CHECK는 신규 테이블에 같이 생성되므로 기존 행 검증 이슈가 없다.
- **기존 `catalog_product`에 CHECK `stock >= 0` 추가 — sqlite 테이블 재생성 주의**: sqlite는 `ALTER TABLE ... ADD CONSTRAINT`를 지원하지 않으므로, Django가 CHECK 추가 마이그레이션에서 **테이블을 재생성**한다(신규 테이블 생성 → 데이터 복사 → 기존 drop → rename). 재생성 중 **기존 행이 CHECK를 위반하면(stock<0) 복사 단계에서 마이그레이션이 실패**한다. 현재 stock은 PositiveIntegerField default 0이라 음수 행이 없을 것이므로 통과가 기대된다(`architecture-db` §8 — 기존 데이터가 제약을 이미 만족). **forward-fix 기준**: 만약 위반 행이 발견돼 마이그레이션이 실패하면 롤백하지 말고 **위반 행을 cleanup(음수 stock을 0 이상으로 교정)한 뒤 마이그레이션을 재실행**한다(제약을 약화하지 않는다 — 데이터를 제약에 맞춘다). 대용량·운영 Postgres라면 `NOT VALID` 후 `VALIDATE`로 락을 줄이는 단계적 적용을 권장하나, 현재 sqlite·소량 데이터에서는 단일 마이그레이션으로 충분(테이블 재생성 비용도 소량).
- 마이그레이션은 catalog 앱의 ORM 위치(§5)에서 생성하며 별도 데이터 backfill은 없다.

### 4.6 동시성 통합 테스트 실행 모델 (데이터 관점 — coder의 거짓 통과 방어)

§3 #6(over-sell 0)·§4.2 Test criteria를 sqlite + Django TestClient에서 어떻게 *실제로* 실행하는지를 확정한다. 두 경로를 **모두** 두되 1차를 권위 증명으로 한다.

- **1차(권위·결정적) — 리포지토리 레벨 결정적 테스트**: `integration/`에서 stock=1 Product 1건을 두고 `DjangoProductRepository`의 조건부 UPDATE를 **순차로 두 번 직접 호출**한다. 첫 호출 rowcount=1(차감 성공), 두 번째 rowcount=0(재고 부족). 최종 stock=0. 이것이 over-sell 불가의 **결정적 증명**이며 스레드 타이밍에 의존하지 않아 안정적이다. 응용 서비스 레벨에서는 mock/실 리포지토리로 rowcount=0 → 409 번역을 검증한다.
- **2차(보강) — 진짜 스레드 동시 POST**: 진짜 동시성을 끝까지 보고 싶으면 다음 전제를 **데이터 실행 모델로 확정**한다 — (a) `TestCase`가 아니라 **`TransactionTestCase`**를 쓴다(`TestCase`는 테스트를 트랜잭션으로 감싸 롤백하므로 다른 스레드가 미커밋 데이터를 못 보고 commit이 안 일어나 거짓 통과/실패가 난다). (b) **파일 기반 sqlite**를 쓴다(인메모리 `:memory:`는 connection별 별도 DB라 스레드 간 공유 불가 — `TEST['NAME']`을 파일로). (c) OS 스레드 2개로 동시 POST. (d) `database is locked` 흡수를 위해 connection `busy_timeout`(예 5000ms) 설정을 테스트 전제로 둔다. 기대: 1건 201·1건 409·최종 stock=0.
- **선택 지침(coder 집행)**: 진짜 스레드 테스트가 환경에서 불안정하면(타이밍·`database is locked`) **2차를 스킵해도 over-sell 불가 증명은 1차로 충족**된다 — 1차가 권위다. coder는 1차 결정적 테스트를 반드시 두고, 2차는 안정적으로 통과할 때만 유지한다(불안정한 2차를 거짓 통과로 남기지 않는다).

---

## 5. 패키지·테스트 구조 결정 (lens 무관 — 필수)

### 5.1 레이아웃 판단 (houserules §1 결정 순서)

기존 프로젝트는 `catalog/`에 `models.py`·`views.py(빈)`·`tests.py`가 평면으로 놓인 **`startapp` 직후 미조직 상태**다(직접 확인). houserules §1.1의 "확립된 규약"은 *조직된* 규약을 뜻하며 미조직 평면 답습은 제외하므로, **§1.2 dddjango 표준 파일트리(`references/final.md`)를 적용**한다. *왜* — §1.1은 미조직 startapp 상태 답습을 명시적으로 배제하고, §3 평면 금지 레드플래그(앱 루트 평면·`models.py` 루트)에 현재 상태가 해당한다.

단, G0 제약(순수 Django·Ninja 미사용)을 표준 트리에 반영한다: 표준의 Ninja 전용 요소(`<app>_api_router.py`의 Ninja Router, `presentation_layer/schema/`의 Ninja Schema)는 **순수 Django 등가물**로 치환한다 — 라우터는 Django `urlpatterns`, 스키마는 dict 구성 함수. 이는 §0 불변식(컨테이너·4계층·개념1차·종류2차·django_<app>·명명)을 **축소하지 않으며**, 프레임워크 구체만 교체하는 것이다.

### 5.2 표준 트리 적용 — §0 불변식 그대로 박음

기존 평면 `catalog`를 표준 트리로 재배치한다. 앱 컨텍스트명 `<app>` = `catalog`.

```
application/                                  # ① 컨테이너 (불변식1 — 단일 앱이어도)
└── catalog/
    ├── catalog_urls.py                       # 외부 HTTP 진입점: urlpatterns (Ninja Router 대신 순수 Django)
    │                                         #   config/urls.py가 include
    ├── published_service/                    # OHS — 본 범위 다른 앱 소비 없어 빈 패키지로 생성
    │   └── __init__.py
    │
    ├── domain_layer/                         # ② 도메인 (불변식2 _layer)
    │   ├── order/                            #   애그리거트 1차 (불변식3)
    │   │   ├── order.py                      #     애그리거트 루트 — class Order (bare, 불변식6); 생성자가 total_price=unit_price*quantity 강제(I4)
    │   │   ├── entity/__init__.py            #     비어도 폴더 (불변식4)
    │   │   ├── value_object/__init__.py      #     비어도 폴더
    │   │   ├── repository/
    │   │   │   └── order_repository.py       #     ABC: class OrderRepository (개념+역할 접미사, §4)
    │   │   ├── domain_service/__init__.py    #     [선택] 비움
    │   │   ├── event/__init__.py             #     [선택] 비움 (이벤트 미채택 §1.5)
    │   │   ├── specification/__init__.py     #     [선택] 비움
    │   │   └── exception.py                  #     도메인 예외(ProductNotFound 등 Order 측)
    │   └── product/                          #   기존 Product 애그리거트(재고 차감 불변식 소유)
    │       ├── product.py                    #     class Product (도메인) — deduct(qty) 권위 메서드 보유(§1.4)
    │       ├── entity/__init__.py
    │       ├── value_object/__init__.py
    │       ├── repository/
    │       │   └── product_repository.py     #     ABC: class ProductRepository (조건부 차감 메서드 선언)
    │       ├── domain_service/__init__.py
    │       ├── event/__init__.py
    │       ├── specification/__init__.py
    │       └── exception.py                  #     도메인 예외(InsufficientStock 등)
    │
    ├── application_layer/                    # ③ 응용 — 흐름·트랜잭션만 (§1.4)
    │   ├── place_order/                      #   <feature>
    │   │   ├── command/
    │   │   │   └── place_order_app.py        #     유스케이스: transaction.atomic 소유, 도메인 위임, rowcount=0→InsufficientStock 번역
    │   │   ├── query/__init__.py             #     [선택] 비움(조회 없음)
    │   │   ├── dto/
    │   │   │   └── place_order_command.py    #     입력 DTO(product_id, quantity)
    │   │   ├── handler/__init__.py           #     [선택] 비움
    │   │   └── service/__init__.py           #     [선택] 비움
    │   └── unit_of_work.py                   #   [선택] — transaction.atomic으로 충분, 빈 파일 안 둠(생략 가능)
    │
    ├── infra_layer/                          # ④ 인프라
    │   ├── django_catalog/                   #   Django 앱(불변식5) — startapp을 여기서
    │   │   ├── __init__.py
    │   │   ├── apps.py                        #     AppConfig.name='application.catalog.infra_layer.django_catalog', label='catalog'
    │   │   ├── models/
    │   │   │   ├── __init__.py
    │   │   │   ├── product_model.py           #     class ProductModel (기존 Product 이전) + CHECK stock>=0
    │   │   │   └── order_model.py             #     class OrderModel (불변식6) + CHECK quantity>=1, total_price=unit_price*quantity
    │   │   ├── migrations/                    #     기존 0001 이전 + 신규(Order 테이블·Product CHECK)
    │   │   └── admin/__init__.py              #     [선택]
    │   ├── repository/                        #   ABC 구현 (자기 애그리거트 전용)
    │   │   ├── django_order_repository.py     #     class DjangoOrderRepository (§4 명명: 한정자 접두+base 일치)
    │   │   └── django_product_repository.py   #     class DjangoProductRepository — 조건부 원자 UPDATE 수행(§4.3), rowcount 반환
    │   └── service/__init__.py                #   외부 서비스 없음 — 빈 패키지
    │
    ├── presentation_layer/                   # ⑤ 표현 — 얇은 입력 어댑터
    │   ├── api/
    │   │   └── place_order/
    │   │       └── api_order.py               #     JsonResponse 뷰: 파싱→응용 호출→응답/예외 변환, 405 시 Allow: POST
    │   └── schema/
    │       ├── schema_in.py                   #     요청 파싱·검증(dict→DTO); JSON 파싱 실패/필드 검증 실패 분기
    │       ├── schema_out.py                  #     성공 응답 dict 구성(도메인 직접 노출 금지); status="CREATED" 리터럴 채움
    │       └── error_out.py                   #     Problem Details(application/problem+json) 구성; errors 맵/생략 분기
    │
    └── test/                                  # 의미군 분리 (houserules §1.3 / §4.2)
        ├── unit/                              #   도메인·응용 단위(deduct 권위·DTO 검증·rowcount=0→409 번역)
        ├── integration/                       #   HTTP 엔드포인트(TestClient) + 리포지토리(실제 DB) — 인수 테스트 여기; 동시성 §4.6
        └── e2e/                               #   [선택] 비움
```

### 5.3 수정·생성 파일 요약 (coder 집행 대상)

- **이전(이동)**: 기존 `catalog/models.py`의 Product → `application/catalog/infra_layer/django_catalog/models/product_model.py`(`ProductModel`로 명명). 기존 `catalog/migrations/0001_initial.py` → 새 django 앱의 `migrations/`로 귀속(앱 label은 `catalog` 유지 → 기존 테이블명 `catalog_product` 보존, DB 재생성 불필요).
- **신규**: 위 트리의 도메인(`order.py`·`product.py`·각 repository ABC·exception), 응용(`place_order_app.py`·`place_order_command.py`), 인프라 리포지토리 구현 2종, 표현(`api_order.py`·schema 3종), Order 테이블 + Product CHECK + Order CHECK 마이그레이션.
- **수정**: `config/urls.py`에 `path("orders", ...)` 또는 `include("application.catalog.catalog_urls")` 추가. `config/settings.py INSTALLED_APPS`에서 기존 `catalog` → `application.catalog.infra_layer.django_catalog`로 교체. 기존 루트 `catalog/`(평면 models/views/tests/apps/admin)는 표준 트리로 이전 후 제거.

> **앱 라벨 보존 주의(coder 집행)**: AppConfig `label='catalog'`를 유지하면 ORM 테이블명이 `catalog_product`로 보존돼 기존 0001 마이그레이션·기존 db.sqlite3 데이터와 정합. label이 바뀌면 테이블명이 달라져 마이그레이션이 깨진다. 이는 구조 결정의 일부라 명세에 박는다.

### 5.4 명명 규약 적용 (houserules §4 — 설계가 확정, 사후 교정 금지)

- 도메인: `Order`·`Product`(bare). ORM: `OrderModel`·`ProductModel`(`<Name>Model`).
- 리포지토리 추상화(ABC): `OrderRepository`·`ProductRepository`(개념+역할 접미사, `Interface`/`Impl` 금지).
- 구현: `DjangoOrderRepository`·`DjangoProductRepository`(기술 한정자 접두, base명 일치).
- 도메인 예외: `InsufficientStock`(재고 부족)·`ProductNotFound`(상품 없음) — 응용이 409/404로 번역.
- 파일명: 약어 없이 `order_repository.py`·`product_model.py` 등.
- ACL/포트 없음(§0 — 같은 BC라 컨텍스트 간 통합 부재). `port/`·`acl/` 폴더는 생성하지 않는다([통합 시]에만 생성 — final.md §3).

### 5.5 타입·주석 규율 (houserules §4·§5)

- 프로덕션 함수·메서드 시그니처는 타입 어노테이션 필수. 테스트 시그니처는 권장(nit).
- 기존 코드에 확립된 주석 언어 관례가 없으므로 주석·docstring은 **한국어**(전역 지침).

### 5.6 테스트 배치 (houserules §1.3 / implementation-test §4.2)

- **인수 테스트(HTTP 엔드포인트, `TestClient` + `manage.py test`)**: `application/catalog/test/integration/`. §3의 6개 외부 관찰 행위를 모두 검증 — 특히 #1(차감량 정확)·#2(409+불변)·#4(400 errors/파싱 분기)·#5(405 Allow)·#6(동시성 over-sell 0, 실행 모델 §4.6).
- **단위 테스트**: `application/catalog/test/unit/` — `Product.deduct()` 권위 검사(I1·I2: 성공 시 stock 감소, 부족 시 `InsufficientStock`), Order 생성자 I4 강제(`total_price=unit_price*quantity`), 입력 DTO 검증(I3), 응용 서비스 흐름(존재확인→차감→생성 순서, rowcount=0→409 번역; mock 리포지토리).
- **동시성 over-sell 증명**: `integration/`에 §4.6의 1차 결정적 테스트(조건부 UPDATE 2회 호출 → rowcount 1/0)를 권위로 둔다. 2차 스레드 테스트는 §4.6 전제 충족 시에만.
- 평면 나열 금지(레드플래그) — 의미군 unit/integration 분리. 인수와 단위를 같은 평면에 섞지 않는다.

---

## 6. 자기모순 스캔 (넘기기 전 1회)

- **재고 차감 소유권(권위 vs 안전망)**: §1.4(도메인 `Product.deduct()`=권위, 인프라 조건부 UPDATE=안전망)·§4.2~§4.3(rowcount=0을 `InsufficientStock`으로 번역) 일관 — 산술·판정 권위는 도메인, DB 가드는 같은 규칙의 race 흡수 집행. §5.2 트리(`product.py`가 deduct 보유, `django_product_repository.py`가 UPDATE 수행)도 일치. 인프라에 비즈니스 규칙을 두지 않는다는 §1.4 ↔ "UPDATE의 stock-qty는 도메인 결정의 영속 표현일 뿐" 일관. 모순 없음.
- **unit_price 출처**: §1.4 흐름2(응용이 Product.price 조회→Order 입력)·§1.6 용어·§4.1 스냅샷 컬럼·§2.4 응답 일치. I4 곱 강제 위치는 §1.2·§1.4(Order 생성자)·§4.1(CHECK)이 모두 도메인 생성자+DB로 일치(응용은 곱을 미리 계산 안 함).
- **트랜잭션 경계**: §1.4·§4.2 모두 응용 서비스 `transaction.atomic()` 소유로 일치.
- **status 소유**: §1.3(도메인 모름·표현 리터럴)·§2.4(`schema_out`이 "CREATED" 채움)·§4.1(DB default 컬럼만, 도메인 전이 없음) 일치 — 도메인 불변식 아님으로 통일.
- **명명**: §1(도메인 bare)·§4(`OrderModel`)·§5.4(추상/구현·예외명) 일치.
- **이벤트**: §1.5 미채택과 §5.2 `event/` 빈 폴더 일치(불변식상 폴더는 두되 비움).
- **에러 계약 일관**: §2.3(상태 코드·Allow·Content-Type)·§2.5(errors 맵/파싱 분기)·§3(행위 목록 #4·#5)이 일치. 415/406 미도입(§2.2)과 §2.3 표(415/406 행 없음) 일치.
- **409 vs 422**: §2.3에서 재고 충돌=409, 입력 실패=400으로 분리 확정 — §3 행위 목록과 일치.
- **동시성 증명 경로**: §3 #6 → §4.2 Test criteria → §4.6 실행 모델(1차 결정적·2차 스레드) → §5.6 테스트 배치가 끊김 없이 연결(이전 §4.4→§4.5 참조 끊김 해소). `TransactionTestCase`+파일 sqlite 전제가 §4.6에 명시.
- **엔진차**: §4.3·§4.4가 select_for_update 비의존·조건부 UPDATE 의존으로 일관 — coder가 한 엔진만 보고 락으로 메우면 안 됨을 명시(G1' 반송 방지). §4.4 retry 불필요는 "단일 문 UPDATE 경로 유지" 전제로 한정.
- **CHECK 집행 일관**: §4.1이 I2(`stock>=0`)·I3(`quantity>=1`)·I4(`total_price=unit_price*quantity`)를 모두 CHECK로 집행 — DB 경계 집행 기준을 세 불변식에 동일 적용(I1은 조건부 UPDATE의 WHERE 가드가 담당, CHECK 대상 아님). 모순 없음.

---

## 7. 트레이드오프 — G1 사용자 결정 (2026-05-28 승인, 확정)

- **구조 이전 범위**: **표준 4계층 트리로 이전** 채택(하우스룰 기본). §5.2 트리 그대로 집행.
- **동시성 테스트 범위**: **옵션 A** 채택 — §4.6 1차 결정적 테스트(조건부 UPDATE 2회→rowcount 1/0)를 over-sell 불가 증명 권위로. 2차 스레드 테스트는 안정 시에만 보강(인수 필수 아님).

(아래는 결정 배경 원문 — 참고용)

## 7-bis. 미해소 트레이드오프 (G1에서 사용자 제시 후보)

- **기존 `catalog/`(평면)를 표준 트리로 이전하는 비용**: G0 제약(catalog 포함·표준 적용)의 논리적 귀결이나, "기존 평면을 최소 수정으로 둘지 vs 표준 트리로 이전할지"는 사용자가 비용을 재고하고 싶을 수 있는 지점이다(houserules §1.2는 미조직 평면에 표준 적용을 지시하므로 기본은 이전). 이전 비용을 받아들이지 않으려면 G1에서 결정 필요.
- **동시성 2차(스레드) 테스트 채택 범위**: §4.6은 over-sell 불가 증명의 권위를 1차 결정적 테스트(조건부 UPDATE 2회)로 두고, 진짜 스레드 동시 POST는 보강으로 둔다. 2차는 `TransactionTestCase`+파일 sqlite+busy_timeout 전제와 OS 스레드 타이밍 의존이라 CI 환경에 따라 불안정할 수 있다. **옵션 A(기본)**: 1차 권위 + 2차 안정 시에만 유지. **옵션 B**: 진짜 동시성 신뢰가 인수 기준에 필수면 2차를 필수화하고 CI에 파일 sqlite·busy_timeout을 고정 전제로 명문화(불안정 비용 수용). 어느 쪽을 인수 기준으로 둘지 사용자가 G1에서 정할 수 있다(기본은 A).

---

## 8. 리뷰 반영 요약 (lens별 독립 리뷰 → 반영 위치)

각 지적을 명세 본문 어디에서 제자리 반영했는지 정리한다(이력 아닌 추적용 인덱스).

**DDD lens**
- [blocker] 빈혈 모델 위험(도메인 권위 vs DB 안전망) → §1.4를 "이중 방어선 단일 모델"로 재서술: `Product.deduct()`가 I1·I2 권위 검사·`InsufficientStock` 던짐(권위), 조건부 UPDATE는 영속·race 흡수(안전망), rowcount=0=재고 부족을 응용이 번역. §4.2·§4.3·§6에 일관 반영.
- [권고] unit_price 스냅샷 출처 → §1.4 흐름2(응용이 Product.price 조회→Order 입력), §1.6 용어, total_price=unit_price*quantity는 Order 생성자(도메인)가 강제(I4) 명시.
- [권고] Product 존재확인 순서 → §1.4 흐름 "존재 확인(404)→차감 위임(409)→Order 생성" 번호 순서로 명시.
- [권고] status 필드 위치 재규정 → §1.3을 "도메인 불변식 아님·표현 계약상 고정 리터럴(schema_out이 채움)·DB는 default 컬럼만" 으로 재규정, §2.4·§4.1·§6에 일관.

**API lens**
- [important] 415/Content-Type 정책 → §2.2에 "엄격 검증 안 함·본문 파싱 성공 여부로 판정·415 미도입·406 미도입" 계약 확정.
- [important] 405 Allow 헤더 → §2.3 405 행에 `Allow: POST` 추가, §3 #5에 검증 항목 명시.
- [important] 400 errors 스키마 → §2.5에 400 본문 예시 2종(필드 검증 errors 맵 / JSON 파싱 실패 errors 생략·detail만) 추가, 분기 규칙·표 갱신.
- [nit] §2.3 헤더 칸 `Content-Type:` 표기 통일 → 모든 행에 `Content-Type: ...` 접두 통일.

**DB lens**
- [blocker] sqlite 동시성 테스트 실현 모델 미정(참조 끊김) → §4.6 신설: 1차 결정적 테스트(조건부 UPDATE 2회→rowcount 1/0, 권위)·2차 스레드 테스트(`TransactionTestCase`+파일 sqlite+OS 스레드 2개+busy_timeout 전제). §4.2 Test criteria·§3 #6·§5.6이 §4.6을 가리키도록 참조 연결(끊김 해소).
- [important] CHECK 마이그레이션=sqlite 테이블 재생성 → §4.5에 sqlite ALTER 미지원·테이블 재생성(생성→복사→drop→rename)·위반 행 발견 시 "cleanup 후 재실행" forward-fix 기준 명시.
- [important] total_price 파생 CHECK → §4.1 OrderModel에 CHECK `total_price = unit_price * quantity` 추가(I4 DB 경계 집행 일관), §6 CHECK 집행 일관 스캔 갱신.
- [nit] §4.4 retry 불필요 전제 → "단, 조건부 원자 UPDATE 단일 문 경로를 유지하는 한" 전제 추가.

**중재(리뷰어 간)**
- DDD 도메인 권위 ↔ DB 조건부 UPDATE는 충돌이 아니라 **이중 방어선**으로 통합 — §1.4·§4.2·§4.3·§6에 권위/안전망 단일 모델로 일관 확정.
- 새 트레이드오프(동시성 2차 스레드 테스트 채택 범위)는 §7 옵션 A/B로 남겨 G1 제시(기존 "평면→표준 트리 이전 비용" 옵션은 유지).
