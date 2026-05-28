# 통합 설계 명세 — 재고 검증 주문 생성 API

기능: 재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.
스코프 단일 근거: `.dddjango/order-create-with-stock/scope.md`
활성 lens: ddd · api · db
이 명세는 이후 인수 테스트·구현의 단일 근거(source of truth)다. 코드는 포함하지 않는다.

---

## 0. 컨텍스트·바운디드 컨텍스트 배치 (고정 결정)

- **BC 배치 = 기존 `catalog` 바운디드 컨텍스트에 포함**(별도 `orders` 앱 분리 금지). 사용자가 G0에서 고정한 결정이며, 이 명세는 그 제약 안에서 애그리거트·트랜잭션을 설계한다. 하위(acceptance-tester·coder·discipline-reviewer)는 스코프 메모가 아니라 이 명세만 읽으므로 배치를 여기 명시적으로 박는다.
- 결과적으로 `catalog`는 **상품 카탈로그(`Product`) + 단순 주문(`Order`) 두 애그리거트를 한 BC가 소유**한다. 두 개념이 같은 BC에 있으므로 **BC 간 통신(OHS)·ACL(`port/`·`acl/`)은 도입하지 않는다** — 다른 컨텍스트를 소비하지 않기 때문이다(`references/final.md` §2 컨텍스트 간 통신: ACL은 *다른* 컨텍스트 소비 시에만).
- *왜 ACL 없이 한 BC인가* — BC 합병의 근거는 **유비쿼터스 언어·소유 경계**(같은 catalog 팀이 상품과 단순 주문을 함께 소유)이지 DDD §3.3 규칙4가 아니다. **가드: §3.3 규칙4(동일 DB 단순 케이스에서 한 트랜잭션에 복수 애그리거트 수정 용인)는 *애그리거트(일관성) 경계* 완화 규칙이며, 두 개념을 한 BC로 합쳐 ACL을 생략해도 된다는 허가가 아니다.** 규칙4는 아래 §1·§3에서 *애그리거트 레벨* 트랜잭션 경계 판단에만 쓴다.
- **구조 배치 = 옵션 B(기존 `catalog` 최소 변경) — G1 사용자 결정.** 기존 평면 `catalog/` 앱과 그 `Product`·기존 마이그레이션·`catalog_product` 테이블은 **이동하지 않고 그대로 둔다**(이주 리스크 0). 이 기능의 신규 주문 코드와 `Product`에 필요한 변경만 기존 `catalog` 앱 안에 의미군 폴더로 추가한다(상세 §5). houserules 표준 트리(`infra_layer/django_catalog/`로의 전면 이주)는 채택하지 않는다 — 이는 §1.1 "기존 규약 존중" 경로에 해당한다(§5.1 근거).
- (ddd 리뷰어가 이 합병 배치를 부적절하다고 보면 묵살하지 않고 G1 배너 옵션으로 사용자 재고에 올린다 — 재결정 금지 ≠ 재고 불가.)

---

## 1. 도메인 모델 (ddd)

### 1.1 유비쿼터스 언어

| 용어 | 의미 |
|---|---|
| Product | 판매 상품. 이름·가격·재고(stock)를 가진 애그리거트 루트. |
| stock | 가용 재고 수량. **음수가 될 수 없다**(핵심 불변식). |
| Order | 단일 품목 주문(상품 1개 + 수량 1개). 애그리거트 루트. |
| quantity | 주문 수량(1 이상). |
| 재고 차감 (deduct) | 주문 생성 시 재고를 수량만큼 줄이는 행위. |
| 재고 부족 (insufficient stock) | 요청 수량 > 현재 재고. 주문을 거절(409)하고 재고 변화 없음. 도메인 예외 `InsufficientStockError` ↔ 409 `type=.../insufficient-stock`. |
| 상품 없음 (product not found) | `product_id`에 해당하는 Product가 없음(또는 트랜잭션 중 사라짐). 주문 거절(404). 도메인 예외 `ProductNotFoundError` ↔ 404 `type=.../product-not-found`로 단일 출처에 묶는다. |

### 1.2 애그리거트 경계

두 애그리거트, 같은 `catalog` BC:

- **Product 애그리거트** (기존). 루트 `Product`. 불변식: `stock >= 0`.
  - **불변식 판정 권위 — 의도적 트레이드오프(솔직한 명시)**: 동시성·정확성(오버셀 차단)을 위해 재고 부족의 **실질 판정 권위는 인프라의 조건부 원자 UPDATE(`WHERE stock >= qty`)+DB CHECK에 둔다**(§3.2). 이는 "도메인 인메모리 비교로 부족을 판정"하면 동시 요청 사이 TOCTOU로 오버셀이 나기 때문이다(§3.3 규칙1 불변식 보호를 *정확하게* 달성하려면 판정이 원자 쓰기와 한 단위여야 함).
  - 따라서 `Product.deduct_stock(quantity)`의 역할은 다음으로 **축소 재정의**한다: (a) **방어 가드** — `quantity >= 1` 검증(0 이하면 도메인 예외), (b) **차감 후 상태 동기화 지점** — 인프라가 원자 UPDATE로 차감을 성공시킨 뒤 도메인 객체의 `stock` 값을 차감 결과로 맞추고(인메모리 일관성), 차감 자체가 거절되면(rowcount==0) `InsufficientStockError`를 표현한다. 즉 도메인은 **불변식을 *이름 짓고 표현*하되, 동시성 정확성의 *판정*은 원자 UPDATE에 위임**한다. "Product 안에서만 부족을 판정한다"는 단언은 쓰지 않는다(명목-실제 괴리 방지) — acceptance-tester는 도메인 단위에서 *부족 판정의 동시성 정확성*을 기대하지 말고, 가드(quantity>=1)와 예외 표현만 도메인 단위로 검증한다(부족·오버셀 정확성은 §6 통합/동시성 테스트가 검증).
- **Order 애그리거트** (신규). 루트 `Order`. 다른 애그리거트(Product)는 **ID로만 참조**한다(§3.3 규칙3) — `Order`는 `product_id`와 `quantity`를 갖고 `Product` 객체를 직접 품지 않는다. Order는 자기 식별자·상태·수량의 일관성만 책임진다.

### 1.3 불변식

- **(Product) `stock >= 0`** — 어떤 경우에도 재고는 음수가 될 수 없다. **판정 권위는 조건부 원자 UPDATE+DB CHECK(인프라/DB)**, 도메인 `Product.deduct_stock`은 가드·예외 표현·상태 동기화를 담당(§1.2 트레이드오프). DB CHECK 제약이 최종 방어선(§3 데이터 설계).
- **(Order) `quantity >= 1`** — 0 이하 수량 주문은 검증 실패(422). 도메인 가드(`deduct_stock`·`Order` 생성)에서도 방어.
- **재고 변화 원자성** — "차감(조건부 UPDATE) → 주문 생성"은 한 트랜잭션. 부족 시 재고 변화 없음(rowcount==0 → 롤백·거절).

### 1.4 차감 정책·상태 전이

- 주문 생성 = 요청 시점 재고 차감(예약 없음, 즉시 차감). 결제·배송·취소는 스코프 밖이므로 Order는 **생성 시 단일 상태(`CREATED`)** 만 갖는다. 상태 머신·전이는 이번 범위에 없다(스코프 고수 — 결제/취소 제외).
- 차감은 **즉시 일관성**이 필수다(오버셀 차단). 따라서 재고 차감과 주문 생성은 **동기·한 트랜잭션**으로 묶는다. 결과적 일관성(도메인 이벤트)은 쓰지 않는다 — `references/final.md` §2 통합 스타일 선택(즉시 일관성=동기) 및 `architecture-ddd` §6.8.

### 1.5 두 애그리거트 한 트랜잭션 수정의 근거

- 본 기능은 한 트랜잭션에서 **Product(재고 차감) + Order(생성)** 두 애그리거트를 수정한다. 이는 `architecture-ddd` §3.3 규칙4 실무 예외("동일 DB 단순 케이스에서는 같은 트랜잭션에서 복수 애그리거트 수정 용인")에 정확히 해당한다 — 단일 SQLite/Postgres DB, 분산 없음, 오버셀 차단에 즉시 일관성 필수.
- 이 예외 채택은 **애그리거트 레벨 결정**일 뿐이며, §0의 BC 합병 결정과는 별개다(규칙4를 BC 근거로 오용하지 않는다).

### 1.6 도메인 이벤트 채택 여부

- **채택하지 않는다.** *도메인 근거*: 본 유스케이스는 한 트랜잭션 안에서 Product·Order 두 애그리거트를 **즉시 일관성**으로 동시에 확정하므로(오버셀 차단이 동기 필수), 경계 밖으로 전파해 결과적 일관성으로 처리할 부수효과·통합 트리거가 존재하지 않는다(`architecture-ddd` §3.3 규칙4: 경계 밖 일관성이 *필요할 때* 결과적 일관성/이벤트). 주문 후 외부 부수효과(알림·포인트 적립 등)는 스코프 밖이라 이벤트 발행 대상이 없다(§3.7). 결과적 일관성 트리거가 생기면(예: 알림) 그때 이벤트를 도입한다.
- 이벤트 정의 파일·전용 폴더는 두지 않는다(구조는 옵션 B 기준 — §5: 기존 평면 `catalog/` 최소 변경이라 표준 트리의 빈 종류 폴더를 새로 강제하지 않는다).

---

## 2. API 계약 (api)

### 2.1 API 프레임워크 도입

- **Django Ninja를 도입한다**(플러그인 기본; 미설치 상태에서 신규 도입). DRF 대비 Pydantic Schema·자동 OpenAPI·얇은 라우터가 본 기능의 얇은 표현 어댑터(§4·§5)와 정합한다. 의존성은 coder가 기존 패키지 매니저를 감지해 추가한다(houserules §6: init은 범위 밖, 기존 존중).
- 루트 `config/urls.py`는 현재 admin만 등록 — Ninja `NinjaAPI` 인스턴스를 마운트하고 `catalog`의 라우터를 등록한다(상세 §5).

### 2.2 엔드포인트

| 항목 | 값 |
|---|---|
| 경로 | `POST /api/v1/orders` |
| 메서드 | `POST` (생성, non-idempotent) |
| 리소스 | `orders` (명사·복수형 — `architecture-api` §3) |
| 인증 | 없음 (스코프: 인증·권한 미적용) |

- *왜 POST /api/v1/orders* — 주문 생성은 새 리소스 생성이며 안전하지도 멱등하지도 않다(`architecture-api` §2). URL에 동사("deduct")를 넣지 않고 리소스 컬렉션에 POST한다(§3).
- *왜 `/v1` 버전 prefix* — 첫 공개 API이므로 처음부터 URL 버전 전략을 박아 향후 하위호환 깨는 변경에 v2 경로를 열어둔다(`architecture-api` §10 URL 버전). 이는 스코프 확장이 아니라 *경로 결정*이다 — 기능 자체는 동일하고 경로 형태만 확정.

### 2.3 요청 계약

```
POST /api/v1/orders
Content-Type: application/json

{ "product_id": <int>, "quantity": <int> }
```

| 필드 | 타입 | 제약 |
|---|---|---|
| product_id | integer | 필수, 양의 정수 |
| quantity | integer | 필수, >= 1 |

- 요청 본문 미디어 타입은 `application/json`만 지원한다. 다른 Content-Type은 **415**로 거절(§2.5).

### 2.4 응답 계약

성공 — **201 Created**:

```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "order_id": <int>,
  "product_id": <int>,
  "quantity": <int>,
  "status": "CREATED",
  "remaining_stock": <int>
}
```

- **Location 헤더 — 두지 않는다.** 조회 엔드포인트(`GET /api/v1/orders/{id}`)가 이번 스코프에 없어 Location을 두면 죽은 링크(404 나는 경로)를 가리키는 셈이다(api 리뷰 반영). 생성 결과 식별·재고는 응답 body(`order_id`·`remaining_stock`)로 충분히 전달한다. 조회 엔드포인트가 추가되면 그때 Location을 도입한다. *응답 계약에 "주문 조회 미지원"을 명시*해 클라이언트가 조회 링크를 기대하지 않게 한다.
- `remaining_stock`은 차감 후 재고. 주문 식별자 + 상태 + 차감 후 재고를 노출한다. 도메인 엔티티를 직접 직렬화하지 않고 `schema_out`(Published Language)로 노출한다(`references/final.md` §2 표현 계층).

### 2.5 상태 코드

| 상태 | 조건 | 비고 |
|---|---|---|
| 201 Created | 재고 충분, 차감·주문 생성 성공 | 위 성공 body |
| 404 Not Found | `product_id`에 해당하는 상품이 없음(또는 트랜잭션 중 사라짐) | RFC 9457 problem+json. §2.6 우선순위 규칙 적용 |
| 409 Conflict | 상품은 존재하나 요청 시점 재고 < 수량(재고 부족) | 재고 변화 없음. RFC 9457 problem+json |
| 415 Unsupported Media Type | 요청 본문 Content-Type이 `application/json`이 아님 | RFC 9457 problem+json (`architecture-api` §7: 415=요청 페이로드 형식 거절) |
| 422 Unprocessable Content | 스키마/검증 실패(quantity < 1, 타입 불일치 등) | Ninja Schema 검증 → problem+json 변환(§2.6) |

### 2.6 에러 형식 (RFC 9457 Problem Details)

- **Content-Type: `application/problem+json`** 으로 통일한다(`architecture-api` §6). 모든 에러 응답(404·409·415·422)에 일관 적용. **Ninja 기본 검증 에러(422)는 problem+json 형식이 아니므로 problem+json으로 변환하는 것이 계약**이다 — 변환 핸들러를 표현 계층에 둔다(§4).

- **404 vs 409 우선순위 규칙 (api#1·db#1 통합 중재 결정)**: TOCTOU 경계에서 두 코드가 비결정적이지 않도록 다음으로 **결정적 계약**을 박는다.
  - **존재하지 않거나(사전 SELECT 미발견) 트랜잭션 중 사라지면 → 404.**
  - **존재하나 재고가 부족하면 → 409.**
  - 구현상 부족·없음 모두 조건부 UPDATE의 `rowcount==0`로 귀결되므로(§3.2), **rowcount==0일 때 동일 트랜잭션 내에서 상품 존재를 재SELECT로 재확인**한다: 행이 있으면 재고 부족 → 409, 없으면 상품 없음 → 404. 사전 SELECT는 404 분류 편의·빠른 경로일 뿐이고 **정확성(오버셀 차단)은 오직 조건부 UPDATE의 rowcount에 의존**한다. 404/409 경계 race에서 어느 쪽으로 분류되든 **둘 다 안전 거절**(재고 변화·주문 생성 없음)이므로 정확성에는 영향이 없고, 분류만 위 순서로 결정한다.

- **에러별 problem+json 계약** (모든 type URI는 안정적 문서 링크 역할 placeholder, 실제 호스트는 운영 확정 — §6.3):

  재고 부족 — **409**:
  ```
  HTTP/1.1 409 Conflict
  Content-Type: application/problem+json

  {
    "type": "https://errors.example.com/catalog/insufficient-stock",
    "title": "Insufficient stock",
    "status": 409,
    "detail": "Requested quantity 5 exceeds available stock 2.",
    "instance": "/api/v1/orders/req-<request_id>",
    "product_id": <int>,
    "requested": <int>,
    "available": <int>
  }
  ```

  상품 없음 — **404**:
  ```
  HTTP/1.1 404 Not Found
  Content-Type: application/problem+json

  {
    "type": "https://errors.example.com/catalog/product-not-found",
    "title": "Product not found",
    "status": 404,
    "detail": "Product <product_id> does not exist.",
    "instance": "/api/v1/orders/req-<request_id>",
    "product_id": <int>
  }
  ```

  검증 실패 — **422** (Ninja 검증 에러를 problem+json으로 변환):
  ```
  HTTP/1.1 422 Unprocessable Content
  Content-Type: application/problem+json

  {
    "type": "https://errors.example.com/catalog/validation-error",
    "title": "Request validation failed",
    "status": 422,
    "detail": "quantity must be >= 1.",
    "instance": "/api/v1/orders/req-<request_id>",
    "errors": [ { "field": "quantity", "message": "..." } ]
  }
  ```

  지원하지 않는 미디어 타입 — **415**:
  ```
  HTTP/1.1 415 Unsupported Media Type
  Content-Type: application/problem+json

  {
    "type": "https://errors.example.com/catalog/unsupported-media-type",
    "title": "Unsupported media type",
    "status": 415,
    "detail": "Request body must be application/json.",
    "instance": "/api/v1/orders/req-<request_id>"
  }
  ```

- 확장 필드: 409는 `product_id`·`requested`·`available`(§6.2), 404는 `product_id`, 422는 `errors`(필드별 검증 메시지 배열).
- **`instance` 정책**: 컬렉션 경로 고정값(`/api/v1/orders`)은 발생 식별 기능을 잃으므로(api 리뷰), **요청별 식별자를 붙인다**(`/api/v1/orders/req-<request_id>`, request_id는 요청마다 발급). 식별자 발급 메커니즘은 구현 세부(coder)이나 *요청별 식별 가능해야 함*이 계약이다.

- *왜 409인가* — 재고 부족은 "요청은 적법하나 현재 자원 상태와 충돌"이다(`architecture-api` §4: 409 = 자원 충돌·동시 수정). 스코프 명시 요구사항.

### 2.7 멱등성 키 — 도입하지 않음 (G1 옵션 A 확정)

- **이번 스코프에서 `Idempotency-Key`를 도입하지 않는다 — G1에서 사용자가 옵션 A(미도입)로 결정.** 단 *근거*와 *향후 자리*를 남긴다(`architecture-api` §13.3 계약 결정). 이번 구현 범위 밖이다.
- 근거: 멱등성 키는 중복이 치명적인 POST(결제·주문)에서 권장(§13.4)이나, 이번 스코프 G0의 핵심 안전 요구는 "**오버셀(재고 음수) 차단**"이며 이는 §3의 조건부 원자 UPDATE+CHECK로 보장된다 — 네트워크 재시도로 인한 **중복 주문 레코드** 방지는 별개 관심사이고 사용자가 G1에서 단순성을 택했다. 중복 주문 방지는 동시성 안전(오버셀)과 구분되는 *추가* 보장이라 이번 범위에서 제외한다(`전역 §05` 현재 요구 우선).
- 향후 도입 시 계약(미리 고정된 향후 메모, 이번 구현 대상 아님): scope=caller+operation, replay=최초 결과 재현(201 snapshot 보관), conflict=동일 key+다른 fingerprint는 422 problem+json, storage=DB 테이블+unique 제약, concurrency=key unique 제약으로 직렬화(`architecture-api` §13.3·`architecture-db` §9.6 API handoff). 이는 *결정 상태*가 아니라 미도입 전제의 향후 계약 메모다.
- **알려진 공백(수용된 트레이드오프)**: 멱등성 키 부재 시, 클라이언트 재시도가 중복 주문 레코드를 만들 수 있다(재고는 정확히 그만큼 차감됨). 사용자가 G1에서 이 공백을 수용했다(§8.2).

### 2.8 OpenAPI 반영 (계약 결정)

- 모든 계약 결정은 OpenAPI 스펙에 드러나야 한다(`architecture-api` §14): path(`/api/v1/orders`)·method(POST)·요청 schema(`schema_in`)·201 응답 schema(`schema_out`)·**에러 응답(404·409·415·422) 각각의 problem+json schema(`error_out`)와 상태 코드**·security(none, 인증 미적용)를 모두 기술한다. Ninja 자동 OpenAPI에 에러 응답·problem+json 미디어 타입이 누락되지 않도록, 라우터에서 응답 스키마를 상태 코드별로 선언한다.

---

## 3. 데이터 설계 (db)

### 3.1 Order 스키마 (신규 ORM 모델 `OrderModel`)

`catalog/models.py`에 `class OrderModel`을 기존 `Product`와 같은 파일에 추가한다(옵션 B — 기존 평면 앱 유지, 모델은 의미군 모듈로 분리하지 않고 기존 `models.py`에 둔다; §5.3). 테이블명은 Django 기본(`catalog_ordermodel`).

| 필드 | 타입 | 제약·근거 |
|---|---|---|
| id | BigAutoField (PK) | Django 기본 |
| product | ForeignKey(Product, on_delete=PROTECT) | 주문이 가리킨 상품 삭제 방지(주문 무결성). 애그리거트는 ID 참조(§3.3 규칙3)지만 ORM은 FK로 참조 무결성 확보 — DB 레벨 FK 제약(`architecture-db` §8). 컬럼 `product_id`. |
| quantity | PositiveIntegerField | CHECK `quantity >= 1`(불변식 §1.3). |
| status | CharField(max_length=16, default="CREATED") | 단일 상태. **CHECK `status = 'CREATED'`** 또는 `choices`로 단일 허용값을 DB 경계에 못박는다(아래 제약). |
| created_at | DateTimeField(auto_now_add=True) | 생성 시각. |

인덱스:
- `product_id`에 인덱스 — **Django ORM이 `ForeignKey`에 기본으로 인덱스를 생성**한다(DB 엔진 기본이 아니라 Django ORM 동작). 향후 상품별 주문 조회 액세스 패턴에 부합하며 별도 선언 불필요. 이번 스코프엔 조회 엔드포인트가 없으므로 추가 복합 인덱스는 두지 않는다(`architecture-db` §7: 실제 액세스 패턴 기반, YAGNI).

제약:
- Order: `CHECK (quantity >= 1)`.
- Order: `CHECK (status = 'CREATED')` — 상태가 단일값뿐이라 추가 비용 없이 불변식을 DB에 못박는다(`architecture-db` §8: 비즈니스 불변식이 DB 경계에서 지켜져야 하면 check constraint). 상태 전이가 생기면 그때 CHECK를 확장한다(YAGNI가 아니라 *현재 단일 상태를 정확히 표현*).
- **Product: `CHECK (stock >= 0)`** 를 추가한다(신규 제약) — 재고 음수 금지 불변식의 **DB 최종 방어선**(`architecture-db` §8). 기존 `PositiveIntegerField`는 0 이상을 모델 검증 수준에서만 보장하므로 DB CHECK로 못박는다. 이 CHECK는 §1.2 트레이드오프상 **불변식 판정 권위의 일부**다(조건부 UPDATE와 함께 환경 무관 정확성 보장). 기존 `catalog/models.py`의 `Product`에 `Meta.constraints`로 추가한다(모델 이동 없음 — §3.4).

### 3.2 재고 차감 트랜잭션 경계·동시성 전략

이 쓰기는 **Risky Write**(재고·주문)다. `architecture-db` §9.6 Risky Write Consistency Block:

| 항목 | 결정 |
|---|---|
| Transaction owner | 응용 서비스 `create_order_app`(§4)이 트랜잭션 경계를 소유(`transaction.atomic()`). |
| Locking strategy | **조건부 원자 UPDATE(`WHERE stock >= quantity`) + CHECK 제약**을 환경 무관 1차 방어선(=불변식 판정 권위)으로. 운영(Postgres)에선 보강으로 pessimistic row lock(`select_for_update`) 사용 가능하나 정확성은 조건부 UPDATE만으로 성립. (§3.3 엔진 분기) |
| Idempotency storage | 없음(§2.7 멱등성 키 미도입 — G1 옵션 A). |
| API handoff | 해당 없음(멱등성 키 없음). |
| Side-effect timing | 외부 부수효과 없음(알림·결제 스코프 밖). 트랜잭션 내부엔 DB 쓰기만. |
| Isolation/retry | **정확성에는 retry 불필요** — 조건부 UPDATE의 원자성이 오버셀 race를 차단하므로 격리 상향·재시도 없이도 정확(§9.4). 단 SQLite 테스트 환경의 writer 락 경합 처리는 별개 사안(§3.3). |
| Test criteria | 동시 요청 N개에서 오버셀 없음(차감 합 <= 초기 재고), 부족 시 409·재고 불변, 롤백 시 주문 미생성, 상품 없음 404. (인수/통합 테스트가 검증) |

**동시성 핵심 — 조건부 원자 UPDATE**: 재고 차감은 "읽고-검사하고-쓰기"(read-check-write)를 애플리케이션에서 분리하지 않고, **단일 원자 UPDATE의 `WHERE` 가드로 검사와 쓰기를 DB에서 원자화**한다:

```
UPDATE catalog_product SET stock = stock - :qty
WHERE id = :product_id AND stock >= :qty
```

- 영향 행 수(`rowcount`)가 1이면 차감 성공 → 주문 생성. 0이면 **상품 없음 또는 재고 부족** → 동일 트랜잭션 내 재SELECT로 분류(§2.6: 행 존재하면 409, 없으면 404) 후 트랜잭션 롤백. 이 UPDATE는 그 자체로 원자적이라 두 동시 요청이 같은 행을 차감해도 DB가 직렬화하며, 한쪽만 성공한다 → 오버셀 불가.
- **분류 정확성 주의(db#1)**: 사전 SELECT는 조건부 UPDATE와 원자 단위가 아니다(TOCTOU). 따라서 **사전 SELECT는 빠른 404 분류 편의용일 뿐, 정확성(오버셀 차단)은 오직 rowcount에만 의존**한다. rowcount==0의 404/409 분류는 §2.6대로 **동일 트랜잭션 내 재SELECT**로 확정하고, 경계 race에서 어느 쪽이든 둘 다 안전 거절이다.
- 도메인 `Product.deduct_stock(quantity)`는 가드(quantity>=1)·차감 후 상태 동기화·부족 예외 표현을 담당(§1.2), 리포지토리가 조건부 UPDATE로 원자 영속화·rowcount 검사를 담당한다(§4 소유권). 즉 *불변식의 이름·표현은 도메인*, *동시성 정확성의 판정·원자 영속화는 인프라 리포지토리*가 소유한다 — 두 절이 모순되지 않게 일치시킨다.
- 대상 테이블명은 기존 `catalog_product`다(Product 이동 없음 — §3.4). 조건부 UPDATE는 ORM `QuerySet.filter(...).update(...)`로 표현하며, `update()`가 영향 행 수를 반환한다.

### 3.3 SQLite(개발) vs Postgres(운영) 엔진 차이 — 명세에서 확정

`architecture-db` §9.5 엔진 의존성. coder는 개발(SQLite) 한 환경만 보므로 엔진차 락 공백을 명세에서 메운다:

- **SQLite는 `select_for_update`를 no-op으로 무시**(행 잠금 미지원)하고, Django 기본 **DEFERRED begin**은 `atomic()` 안 SELECT→UPDATE 락 승격이 스레드 경합 시 데드락(`database is locked`)을 낼 수 있다. → 따라서 **행 잠금에 의존하지 않는다.**
- **환경 무관 정확성 방어선 = CHECK(`stock >= 0`) + 조건부 원자 UPDATE(`WHERE stock >= qty`)** (§3.2). 이 둘은 SQLite·Postgres 모두에서 동일하게 오버셀을 차단한다(단일 UPDATE 원자성은 엔진 무관). **이 정확성에 retry는 불필요**하다.
- **SQLite 테스트 환경의 writer 락 경합 처리(db#2) — 정확성과 분리된 별개 사안**: SQLite는 단일 조건부 UPDATE라도 동시 writer 경합 시 `database is locked` 예외를 던질 수 있다. 이는 *오버셀*이 아니라 *락 예외*이므로, **동시성 통합 테스트가 오버셀 검증 전에 락 예외로 실패하지 않도록** 다음을 명세에 자리잡는다.
  - **SQLite 연결에 `busy_timeout`(PRAGMA)을 설정**해 writer가 락 해제를 일정 시간 대기하게 한다(테스트 환경 적용). 필요 시 락 예외에 대한 짧은 재시도(`database is locked`에 한해 bounded retry)를 통합 테스트 경로에 둔다.
  - 이 처리는 **테스트 환경 락 경합 완화용**이지 *정확성 보강이 아니다* — 정확성은 위 조건부 UPDATE로 이미 성립한다(두 사안을 분리 기술). Postgres(운영)는 행 단위 락으로 writer 경합을 큐잉하므로 이 문제가 없다.
- **Postgres(운영)**: 조건부 UPDATE가 동일하게 성립하며, 추가로 `select_for_update`(pessimistic row lock)를 보강으로 쓸 수 있으나 정확성에 필수는 아니다.

- *왜 락이 아니라 조건부 UPDATE인가* — 개발/운영 엔진별 락 동작 차이(SQLite no-op·데드락)로 락만으로는 환경 무관 정확성이 성립하지 않기 때문(`architecture-db` §9.5). 환경 무관 방어는 제약+조건부 UPDATE다.

### 3.3' 차감 0 보호

- 검증 실패(`quantity < 1`)는 API 스키마(422)에서 1차 차단하므로 `WHERE stock >= qty`에 음수/0 수량이 도달하지 않는다. 도메인 `Product.deduct_stock`도 `quantity >= 1`을 방어적으로 검증한다(이중 방어, §1.2 가드).

### 3.4 마이그레이션 안전 (rollout)

옵션 B에서는 **기존 `Product`·테이블·마이그레이션을 이동하지 않으므로 물리 이주가 없다.** 마이그레이션 변경은 (1) `OrderModel` 신설, (2) `Product`에 `CHECK (stock >= 0)` 추가 두 가지뿐이고, 둘 다 기존 `catalog` 앱의 `migrations/`에 새 마이그레이션으로 추가된다. `architecture-db` §11 Expand/Backfill/Contract 관점:

- **`OrderModel` 테이블 신설(`CREATE TABLE catalog_ordermodel`)** — 기존 데이터 무영향, backfill 불필요.
- **`Product`에 `CHECK (stock >= 0)` 추가** — 기존 `Product` 데이터가 이미 `PositiveIntegerField`(>=0)이므로 제약 위반 행이 없어 검증 통과가 보장된다(안전). 운영 Postgres에서 대용량 테이블이면 CHECK 추가가 잠깐 락을 잡을 수 있으나(NOT VALID→VALIDATE 분리 고려), 본 프로젝트 규모·개발 SQLite에선 단일 마이그레이션으로 충분. 대용량 운영 적용 시 단계 분리를 후속 자리로 남긴다.
- **기존 Product 물리 이주 안전성 — 해당 없음**: 옵션 B는 `Product`를 이동하지 않으므로 `db_table` 보존·state-only 이전·테이블 재생성 회피 같은 이주 안전 절차가 **이번 범위에 존재하지 않는다**. coder는 `Product` 모델 파일·`db_table`·기존 `0001_initial`을 건드리지 않고, `makemigrations` 결과가 `Product`에 대해 `CHECK` 제약 추가(`AddConstraint`) 외의 변경(`DROP`/`RENAME`/`RECREATE`)을 내지 않는지만 확인한다.
- **rollout 산출물 — 기존 데이터 보존 검증**: CHECK 추가 마이그레이션이 기존 `catalog_product` 행을 보존하는지(데이터 유실·테이블 재생성 없음) 확인하는 통합 테스트를 rollout 산출물로 둔다(§5.3 `test_product_stock_constraint.py`).
- 마이그레이션 파일은 기존 `catalog/migrations/`에 생성된다(§5).

---

## 4. 서비스/셀렉터 레이어 구조 (책임·소유권)

트랜잭션을 열고 차감·검증·생성을 오케스트레이션하는 위치를 못박는다(절 간 소유권 일치 — 자기점검 통과 기준). 물리 파일 경로는 §5.3을 따른다(옵션 B — 기존 `catalog` 앱 내 의미군 모듈):

- **응용 서비스 `create_order`** (`catalog/application/create_order.py`):
  - 트랜잭션 경계(`transaction.atomic()`)를 **소유**한다(§9.6 Transaction owner).
  - 흐름: 입력 DTO 수신 → 리포지토리로 조건부 원자 UPDATE 차감 영속화(rowcount 검사) → rowcount==0이면 동일 트랜잭션 재SELECT로 404(상품없음)/409(부족) 분류해 도메인 예외 발생 → 차감 성공 시 `Product.deduct_stock`로 도메인 상태 동기화 → `Order` 생성·저장 → 결과 DTO 반환. **불변식의 표현(예외·가드)은 도메인에 위임**하고 응용은 흐름·트랜잭션만 담당(`architecture-ddd` §3.6).
  - domain 리포지토리 인터페이스(ABC)에 의존하고 구현을 주입받는다(DIP).
- **도메인**: `Product.deduct_stock(quantity)`가 가드(quantity>=1)·차감 후 상태 동기화·부족 예외 표현(`InsufficientStockError`)을 소유(§1.2). `Order`는 자기 생성·수량 검증을 소유. **인프라/응용에 가드·예외 표현을 중복 정의하지 않는다**(소유권 단일). 단 *동시성 정확성의 판정 권위*는 §1.2 트레이드오프대로 인프라 조건부 UPDATE에 있다.
- **리포지토리(인프라)**: `DjangoProductRepository`가 조건부 원자 UPDATE(`WHERE stock >= qty`)로 차감을 영속화하고 rowcount==0이면 재SELECT로 존재 확인해 `ProductNotFoundError`(없음)/`InsufficientStockError`(부족)로 변환. `DjangoOrderRepository`가 Order 저장(ORM↔도메인 Data Mapper). *동시성 정확성·원자적 영속화*는 인프라가 소유(§3.2와 일치).
- **표현(api 어댑터)**: 요청 파싱 → `create_order` 호출 → 도메인 예외(`InsufficientStockError`→409, `ProductNotFoundError`→404)를 problem+json으로 변환, Ninja 검증 에러(422)·미디어 타입 불일치(415)도 problem+json으로 변환 → `schema_out` 응답. 얇은 어댑터, 로직 없음(`references/final.md` §2 표현 계층 원칙).
- **셀렉터/쿼리(CQRS)**: 이번 스코프는 쓰기 단일 유스케이스라 query/selector를 만들지 않는다(조회 엔드포인트 없음).

---

## 5. 패키지·테스트 구조 결정 (acceptance-tester·coder의 단일 근거) — 옵션 B

### 5.1 레이아웃 결정 근거 (G1 = 옵션 B)

- 조사 결과 `catalog/`는 `startapp` 직후 **평면 앱**(`models.py`·`views.py`·`admin.py`·`tests.py`·`migrations/0001_initial.py`)이고, `Product`(테이블 `catalog_product`)는 이미 마이그레이션이 적용된 상태다. `config/`가 설정 패키지다.
- **G1에서 사용자가 옵션 B(기존 catalog 최소 변경)를 선택**했다. 따라서 houserules §1.2 표준 파일트리(`application/catalog/`로의 4계층 전면 이주, `infra_layer/django_catalog/`로의 `Product` 물리 이주)는 **적용하지 않는다.** 기존 평면 `catalog/` 앱과 그 `Product`·마이그레이션·테이블은 **그대로 유지**한다(이주 리스크 0).
- *왜 표준 트리를 강제하지 않는가* — houserules `references/final.md` §0 불변식은 명문상 "**확립된 규약이 없어 이 표준을 *새로 까는* 경우**"의 규칙이고, "이미 다른 레이아웃 규약이 확립된 기존 프로젝트는 §1.1대로 그 규약을 존중한다"고 단서를 단다. 본 프로젝트는 이미 적용·운영 중인 `catalog` Django 앱(데이터 보유)이 있으므로, 사용자 결정에 따라 **기존 앱 구조를 존중하고 그 안에서 의미군으로 조직**하는 것이 §1.1 일관성·이주 리스크 0과 정합한다. 표준 4계층·컨테이너·`<app>` 분리·`infra_layer/django_<app>/`·`db_table` 보존 이주 등 §0 불변식 골격은 **이 옵션 B에서는 적용 대상이 아니다**(전면 이주를 하지 않으므로).
- **부분 적용의 경계(명시)**: 표준 트리를 *전면* 적용하지 않되, "단일 거대 파일에 몰아넣지 않는다"는 **의미군 분리 원칙은 유지**한다(§5.3) — 모델/응용 서비스/도메인/리포지토리/api/스키마를 기존 `catalog` 앱 안의 별도 모듈·하위 패키지로 나눈다. 즉 *표준 4계층 디렉터리 골격은 차용하지 않되, 관심사 분리·테스트 의미군 분리는 유지*한다.
- **수용된 트레이드오프(한 줄)**: 옵션 B는 표준 트리 전면 적용 대비 프로젝트 내 레이아웃 일관성이 떨어질 수 있으나(향후 다른 앱이 표준 트리를 쓰면 혼용), 사용자가 G1에서 "기능 범위에 비례하는 최소 변경·이주 리스크 0"을 우선해 이 트레이드오프를 수용했다(§8.1).

### 5.2 §0 불변식 적용 여부 (옵션 B 기준 — 명시)

- houserules `references/final.md` §0 불변식 골격(`application/` 컨테이너·4계층 `_layer`·종류 2차 폴더·`infra_layer/django_<app>/` `startapp`·ORM `<Name>Model`·`db_table` 보존 이주)은 **"표준을 새로 까는 경우"에만 적용**되는 규칙이며, 옵션 B(기존 확립된 `catalog` 앱 존중)에서는 적용 대상이 아니다(§5.1 근거). 이 명세는 옵션 B에서 그 골격을 박지 않는다 — 이는 §0 불변식의 *축소·생략*이 아니라, 불변식이 명문으로 제외한 "기존 규약 존중" 경로의 선택이다.
- 다만 §0의 정신 중 **"평면 답습 금지·의미군 분리"** 는 옵션 B에서도 §5.3·§5.5로 유지한다(기존 `tests.py` 평면을 테스트 패키지로 분리, 한 거대 모듈 금지).
- **ORM 모델 명명**: 신규 주문 ORM 모델은 `OrderModel`로 짓는다(도메인 `Order`와 구분). 단 기존 `Product`는 이미 bare `Product`로 운영 중이므로 **`ProductModel`로 개명하지 않는다**(개명은 테이블·코드 변경을 부르는 이주이며 옵션 B의 "최소 변경"에 반함). 즉 이 명세에서 도메인 `Product`와 ORM `Product`는 같은 클래스를 공유한다(기존 상태 존중) — 신규 `Order`만 도메인/ORM(`OrderModel`)을 분리한다. 이 비대칭은 옵션 B의 의도적 결과다.

### 5.3 파일 배치 (옵션 B — 기존 `catalog` 앱 내 의미군 모듈)

기존 평면 `catalog/` 앱을 유지하되, 신규 코드를 의미군 하위 패키지로 추가한다. **기존 파일은 최소만 수정**한다.

```
catalog/                                  # 기존 Django 앱 (유지 — 이동 없음)
├── __init__.py                           # (기존)
├── apps.py                               # (기존 CatalogConfig — 변경 없음)
├── admin.py                              # (기존) Order admin 등록을 여기 추가(선택)
├── models.py                             # [수정] 기존 Product에 CHECK(stock>=0) 추가 + class OrderModel 신규 추가
├── migrations/
│   ├── 0001_initial.py                   # (기존 — 변경 없음)
│   └── 0002_*.py                         # [신규] OrderModel 생성 + Product CHECK(stock>=0) 추가 (makemigrations 산출)
│
├── domain/                               # [신규] 순수 도메인 (Django 비의존)
│   ├── __init__.py
│   ├── product.py                        # 애그리거트 루트 Product — deduct_stock(qty): 가드+상태동기화+부족예외표현
│   ├── order.py                          # 애그리거트 루트 Order — product_id ID참조, quantity>=1
│   ├── product_repository.py             # class ProductRepository (ABC) — 조건부 차감 포함 포트
│   ├── order_repository.py               # class OrderRepository (ABC)
│   └── exceptions.py                     # InsufficientStockError, ProductNotFoundError
│
├── application/                          # [신규] 응용 서비스 (트랜잭션·흐름)
│   ├── __init__.py
│   ├── create_order.py                   # create_order: 트랜잭션 owner, 흐름 오케스트레이션·404/409 분류
│   └── dto.py                            # CreateOrderCommand 입력 DTO(product_id, quantity)
│
├── repositories/                         # [신규] 도메인 리포지토리 ABC의 Django 구현 (ORM↔도메인 Data Mapper)
│   ├── __init__.py
│   ├── product_repository.py             # class DjangoProductRepository — 조건부 원자 UPDATE+rowcount 분류
│   └── order_repository.py               # class DjangoOrderRepository — Order 저장
│
├── api/                                  # [신규] 표현 어댑터 (Ninja)
│   ├── __init__.py
│   ├── router.py                         # Ninja Router — POST /orders; config/urls.py가 /api/v1 로 마운트
│   ├── schemas.py                        # CreateOrderIn / CreateOrderOut / ProblemDetail(error_out)
│   └── errors.py                         # 도메인 예외→problem+json, Ninja 검증(422)·미디어타입(415) 변환 핸들러
│
└── tests/                                # [신규] tests.py 평면을 테스트 패키지로 교체 (§5.5)
    ├── __init__.py
    ├── unit/
    │   ├── __init__.py
    │   ├── test_product_deduct_stock.py  # 도메인: 가드(quantity>=1)·부족 예외 표현·상태 동기화 (동시성 정확성은 여기서 X)
    │   └── test_order_creation.py        # 도메인: quantity 검증
    └── integration/
        ├── __init__.py
        ├── test_product_repository.py        # 조건부 UPDATE·rowcount 분류(404/409)·CHECK (실제 DB)
        ├── test_create_order_api.py          # HTTP 엔드포인트: 201/404/409/415/422 계약·problem+json
        ├── test_create_order_concurrency.py  # 동시 요청 오버셀 차단 (실제 DB, SQLite busy_timeout/retry 적용)
        └── test_product_stock_constraint.py  # Product CHECK(stock>=0) 적용·기존 데이터 보존 검증 (rollout 산출물 §3.4)
```

기존 평면 파일 처리:
- `catalog/models.py` — **수정**(이동·재생성 없음): 기존 `Product`에 `Meta.constraints`로 `CHECK(stock>=0)` 추가, `class OrderModel` 신규 추가. `Product` 클래스명·`db_table`(기본 `catalog_product`)은 그대로.
- `catalog/migrations/0001_initial.py` — **변경 없음**. 신규 마이그레이션 `0002_*`만 추가.
- `catalog/tests.py` — **제거하고 `catalog/tests/` 패키지로 교체**(평면 단일 파일 금지, 의미군 분리 — §5.5). `tests.py`와 `tests/` 패키지는 공존 불가하므로 파일을 패키지로 전환한다.
- `catalog/views.py` — 미사용이면 그대로 둔다(옵션 B는 기존 파일을 굳이 건드리지 않음; 정리 여부는 coder 재량의 사소 정돈).
- 루트 `config/urls.py` — **수정**: `NinjaAPI` 인스턴스를 만들고 `catalog.api.router`의 Router를 `/api/v1`로 등록(admin는 유지).

### 5.4 명명 규약 (이 명세가 결정 — coder 집행; houserules §4 차용)

- **도메인 ↔ ORM**: 신규 주문은 도메인 bare `Order`(`catalog/domain/order.py`), ORM `OrderModel`(`catalog/models.py`). 기존 `Product`는 도메인·ORM 동일 클래스(`Product`)를 공유한다(옵션 B 최소 변경 — §5.2). 도메인 표현이 필요한 곳에서는 `catalog/domain/product.py`의 `Product`(순수 도메인) 객체를 쓰고, 영속화는 리포지토리가 ORM `Product`와 매핑한다.
- **리포지토리 추상화 ↔ 구현**: 추상=개념+역할 접미사 `ProductRepository`·`OrderRepository`(ABC, `catalog/domain/*_repository.py`), 구현=기술 한정자 접두로 base명 일치 `DjangoProductRepository`·`DjangoOrderRepository`(`catalog/repositories/*_repository.py`). `Interface`/`Impl` 금지.
- **파일명**: 약어 없이 `product_repository.py`·`order_repository.py`·`create_order.py`.
- **ACL/포트 없음**: BC 합병으로 다른 컨텍스트를 소비하지 않으므로 `port/`·`acl/`는 만들지 않는다(houserules §3: ACL은 다른 컨텍스트 소비 시에만).

### 5.5 테스트 배치·명명

- 의미군 분리(houserules §1.3, implementation-test §4.2): 도메인·응용 순수 단위 = `catalog/tests/unit/`, DB·리포지토리·**HTTP 엔드포인트**·동시성·CHECK/데이터 보존 = `catalog/tests/integration/`. 평면 나열·인수↔단위 혼재 금지.
- 기존 `catalog/tests.py`(단일 평면 파일)는 **`catalog/tests/` 패키지로 교체**한다 — 옵션 B에서도 "평면 답습 금지"는 유지(§5.2).
- 인수 테스트(외부 관찰 가능 행위, §6)는 `tests/integration/test_create_order_api.py`(계약별 케이스)와 `test_create_order_concurrency.py`(오버셀)에서 검증한다.

---

## 6. 외부 관찰 가능 행위 목록 (인수 테스트 근거)

acceptance-tester가 이 목록을 검증한다(슬라이스 근거):

1. 재고가 충분하면 **201**과 함께 주문이 생성되고 `remaining_stock`이 `초기재고 - quantity`다.
2. 재고가 부족하면(`quantity > stock`, **상품은 존재**) **409 Conflict**(`application/problem+json`, `type=.../insufficient-stock`)로 거절되고 **재고가 변하지 않으며 주문이 생성되지 않는다**.
3. `quantity < 1`·타입 불일치 등 검증 실패 시 **422**(problem+json, `type=.../validation-error`).
4. 존재하지 않는 `product_id`면 **404**(problem+json, `type=.../product-not-found`).
5. 요청 본문 Content-Type이 `application/json`이 아니면 **415**(problem+json).
6. **동시 요청에서도 초과 판매가 없다** — 동시 N 요청 시 차감 합이 초기 재고를 넘지 않고, 재고는 음수가 되지 않으며, 성공한 주문 수 = 차감된 재고량/수량. (SQLite 테스트는 락 예외가 아니라 오버셀 여부를 검증해야 하므로 busy_timeout/retry로 락 경합을 흡수한다 — §3.3.)
7. 성공 응답은 도메인 엔티티가 아니라 `schema_out` 형태로만 노출된다(필드: order_id·product_id·quantity·status·remaining_stock). Location 헤더는 없다(조회 미지원 — §2.4).
8. Product `CHECK(stock>=0)` 추가 마이그레이션 후에도 기존 `catalog_product` 데이터가 보존된다(테이블 재생성·데이터 유실 없음 — §3.4 rollout 산출물).

---

## 7. 자기모순 스캔 (넘기기 전 1회)

- **구조(옵션 B) 정합**: §0·§1.6·§3.1·§3.4·§4·§5 전체가 "기존 `catalog` 앱 유지·`Product` 미이동·신규 코드는 `catalog/{domain,application,repositories,api,tests}` 의미군 모듈"로 일치. 표준 트리 전면 이주·`infra_layer/django_catalog/`·`db_table` 보존 이주 서술은 모두 제거됨. 모순 없음.
- **재고 차감 규칙 소유권**: §1.2·§3.2·§4 모두 "불변식의 *이름·가드·예외 표현·상태 동기화*는 도메인 `Product.deduct_stock`, *동시성 정확성의 판정 권위·원자 영속화*는 인프라 조건부 UPDATE+CHECK"로 일치. 모순 없음.
- **404 vs 409 분류**: §1.1(UL)·§2.5·§2.6·§3.2·§4 모두 "rowcount==0 시 동일 트랜잭션 재SELECT로 존재 확인→있으면 409·없으면 404, 정확성은 rowcount에만 의존"으로 일치(api#1·db#1 단일 중재). 모순 없음.
- **동시성 전략·retry**: §3.2(정확성 retry 불필요)·§3.3(SQLite 테스트 락 경합은 busy_timeout/retry로 별개 처리) 분리 일치. §6.6 테스트 기준도 일치.
- **상태 코드 집합**: §2.5(201/404/409/415/422)·§2.6(각 problem+json)·§2.8(OpenAPI)·§4(어댑터 변환)·§6(관찰 행위) 일치.
- **ORM 명명(옵션 B 비대칭)**: §3.1(`OrderModel` 신규·`Product` 기존 유지)·§5.2(`Product` 미개명, `Order`만 도메인/ORM 분리)·§5.3 트리·§5.4 명명 일치. 의도적 비대칭을 세 절 모두 동일하게 명시. 모순 없음.
- **멱등성 미도입(G1 옵션 A)**: §2.7·§3.2(Idempotency storage 없음)·§8.2 일치.
- **마이그레이션 안전**: §3.4(이주 없음·CHECK 추가만)·§5.3 트리(`0002_*`만 신규, `0001` 무변경)·§6.8 보존 검증 일치.
- 발견된 모순 없음.

---

## 8. G1 트레이드오프 결정 결과 (사용자 확정)

### 8.1 [구조] 전면 표준 트리 이주 vs 기존 catalog 최소 변경 — **G1에서 옵션 B로 결정**

- **배경**: 본 기능은 "재고 검증 주문 생성" 단일 엔드포인트다. 현재 `catalog/`는 평면 앱이며 `Product` 1개 모델·데이터가 있다.
- **옵션 A — 전면 표준 트리 이주**: houserules §1.2 표준 트리를 전면 적용(`application/catalog/` 4계층, `Product`를 `infra_layer/django_catalog/`로 state-only 이주). 장점: 일관된 골격, 향후 확장 정합. 단점: 단일 엔드포인트 대비 구조 변경 폭이 크고, 기존 데이터 테이블 이주의 마이그레이션 안전을 반드시 검증해야 한다(테이블 재생성·유실 리스크 관리 필요).
- **옵션 B — 기존 catalog 최소 변경 (✅ 채택)**: 기존 평면 `catalog/`·`Product`·migration·테이블을 그대로 두고, 신규 주문 코드만 기존 앱 안 의미군 모듈로 추가(§5.3). 장점: 기능 범위에 비례, 기존 `Product`/migration 무이동(이주 리스크 0). 단점: houserules 표준 트리 골격을 이 기능에 온전히 적용하지 않아, 향후 다른 앱이 표준 트리를 쓰면 프로젝트 내 레이아웃 혼용 가능.
- **결정**: 사용자가 G1에서 **옵션 B**를 선택했다. 이주 리스크 0·기능 범위 비례를 우선했고, 레이아웃 혼용 가능성을 수용된 트레이드오프로 받아들였다. 본 명세 §5는 옵션 B 기준으로 작성되었다.

### 8.2 [기능] 멱등성 키 부재 → 중복 주문 가능 — **G1에서 옵션 A(미도입)로 결정**

- **배경**: 오버셀(재고 음수)은 §3 조건부 UPDATE+CHECK로 차단되나, 멱등성 키가 없어 클라이언트 네트워크 재시도가 **중복 주문 레코드**를 만들 수 있다(재고는 그만큼 정확히 차감됨).
- **옵션 A — 현행 유지(미도입) (✅ 채택)**: 단순성 우선, 스코프 G0 명시 요구(오버셀 차단)만 충족. 중복 주문은 허용 공백.
- **옵션 B — `Idempotency-Key` 도입**: §2.7의 향후 계약을 이번에 구현. 중복 주문 방지. 단점: 스코프 확장·저장소·계약 추가 비용.
- **결정**: 사용자가 G1에서 **옵션 A(미도입)**를 선택했다. 중복 주문 공백을 수용했고, 멱등성 키는 이번 구현 범위 밖이다(§2.7 향후 계약 메모만 보존).
