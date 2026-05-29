# 통합 설계 명세 — 주문 생성 API (재고 검증·차감)

> 단일 근거(source of truth). 이후 인수 테스트·구현·감수는 스코프 메모가 아니라 **이 명세**를 읽는다.
> 활성 lens: ddd · api · db (셋 다 활성). 인증은 범위 밖(익명).

---

## 0. 컨텍스트와 배치 (BC 배치를 명세에 박음)

- **BC 배치(G0 사용자 확정, 존중)**: 주문은 **새 독립 바운디드 컨텍스트 `ordering` 앱**으로 분리한다. `catalog`(상품·재고 소유)와 별개 컨텍스트다. *왜* — 사용자가 G0에서 명시 선택. design은 이 배치를 재결정하지 않고, 이 안에서 애그리거트·통합 패턴만 설계한다.
- **두 컨텍스트의 소유 경계**: `catalog`가 **상품·재고(`Product.stock`)를 소유**한다. `ordering`은 **주문(Order)을 소유**한다. 재고 차감 판정·불변식은 재고를 소유한 `catalog`에 있고, `ordering`은 그 차감을 *요청*한다(아래 §1.4 협력).
  - **가드**: 이 분리에 `architecture-ddd` §3.3 규칙4(동일 DB 단순 케이스에서 한 트랜잭션에 복수 애그리거트 수정 용인)를 "두 개념을 한 BC로 합쳐 ACL 생략" 근거로 끌어쓰지 않는다. 규칙4는 *애그리거트(일관성) 경계* 완화 규칙이지 *컨텍스트 경계* 통합 허가가 아니다. BC 분리는 유비쿼터스 언어·소유 경계(재고=catalog, 주문=ordering)로 판단했다.
- **기존 프로젝트 레이아웃 조사 결과**: 루트에 `catalog/`·`config/`가 평면으로 존재(`startapp`/`startproject` 직후 미조직 평면 — `catalog/models.py`·`tests.py`·`views.py`). 확립된 4계층 규약 **없음**. API 프레임워크 미설치(settings `INSTALLED_APPS`에 DRF/Ninja 없음), SQLite 단일 DB.
- **레이아웃 결정**: `discipline-houserules` §1.1 "미조직 평면 답습 금지" → §1.2 **dddjango 표준 파일트리 적용**(`references/final.md` 단일 출처). 기존 `catalog/`는 이번 범위에서 도메인 계층화/구조 이주는 하지 않는다(스코프 고수). 단 **OD-1 G1 확정(옵션 A)** 에 따라 catalog `Product`에 **재고 차감 도메인 동작 + `version` 컬럼** 추가는 확정 작업이다(§1.4·§3.3·§6 OD-1) — catalog 스코프의 소폭 확장으로 G1에서 사용자 승인됨. 신규 `ordering` 앱만 표준 트리로 만든다. 한 프로젝트에 레이아웃 혼용이 되지만, 이는 *신규 앱에 표준을 적용*하는 것이며 기존 앱을 강제 이주하지 않는다(스코프 밖). *왜* — §1.4 한 기능 안 일관성은 신규 `ordering` 내부에서 지킨다.

---

## 1. 도메인 (ddd lens)

### 1.1 유비쿼터스 언어 (ordering 컨텍스트 내)

| 용어 | 의미 |
|---|---|
| Order(주문) | 한 상품을 특정 수량 주문한 기록. ordering의 애그리거트 루트. |
| Quantity(수량) | 주문 수량. 1 이상의 정수(값 객체). **수량 불변식의 정본(canonical)은 `Quantity` VO**다 — 요청 스키마 검증·DB CHECK는 같은 불변식의 *방어선*일 뿐 판정 정본이 아니다(ddd minor m3). |
| PricedSnapshot(가격 스냅샷) | 주문 시점 상품 단가·총액을 박제한 값. 이후 상품 가격 변동과 무관. |
| OrderStatus(상태) | 주문 생명주기 상태. 이번 범위에선 생성 직후 `PLACED` 단일 상태(전이 없음 — 확인됨, 누락 아님). |
| 재고 차감(stock deduction) | catalog가 소유하는 행위. ordering은 협력 포트로 *요청*만 한다. catalog 측 명명된 도메인 동작이 `stock >= qty` 판정을 내린다(§1.4). |

### 1.2 애그리거트 — Order (루트, 단일 상품 + 수량)

Vernon 4규칙 적용(`architecture-ddd` §3.3):
- **규칙1(진짜 불변식만 경계 내 보호)**: Order가 보호하는 불변식은 "수량 ≥ 1", "가격 스냅샷·총액은 생성 후 불변". **재고(stock) 불변식은 Order의 경계가 아니다** — 재고는 catalog `Product`가 소유하므로 Order 경계에 넣지 않는다(규칙3 ID 참조).
- **규칙2(작게)**: 루트 + 값 객체만. 단일 상품 + 수량이므로 종속 엔티티(line item 컬렉션) 없음.
- **규칙3(타 애그리거트는 ID로만 참조)**: Order는 `Product`를 **객체로 참조하지 않고 `product_id`(int)로만 참조**한다. catalog의 `Product` ORM/도메인 객체를 ordering 도메인이 import하지 않는다.

**Order 필드/구성**(도메인 표현, bare 이름 `Order`):

| 필드 | 타입 | 설명·불변식 |
|---|---|---|
| `id` | int (생성 후 부여) | 영속화 시 DB가 부여. 도메인 생성 시점엔 미부여 가능. |
| `product_id` | int | catalog `Product` ID 참조(객체 참조 금지, 규칙3). |
| `quantity` | Quantity(값 객체) | ≥ 1. 0·음수는 도메인 예외(`InvalidQuantity`). |
| `unit_price` | int (가격 스냅샷) | 주문 시점 `Product.price`. 생성 후 불변. |
| `total_price` | int (파생) | `unit_price * quantity`. Order가 계산·소유(빈혈 차단, §3.2). 외부에서 주입받지 않는다. |
| `status` | OrderStatus | 생성 시 `PLACED`. 이번 범위 전이 없음. |
| `created_at` | datetime | 생성 시각. |

**값 객체**:
- `Quantity` — `value: int`, 자기검증(`value >= 1` 아니면 `InvalidQuantity`). 불변(frozen).
- 가격 스냅샷은 `unit_price`/`total_price` 정수로 Order에 인라인(별도 Money VO는 현재 요구에 과함 — YAGNI, §05). *왜* — 단일 통화·정수 원화 가정, 다중 통화는 범위 밖.

**팩토리·판정 소유(빈혈 차단, `architecture-ddd` §3.2)**: Order 생성은 도메인 팩토리(`Order.place(product_id, quantity, unit_price, now)`)가 담당하고, 총액 계산·수량 검증을 **도메인이 프로덕션 경로에서 실행**한다. 응용 서비스·리포지토리·SQL이 이 판정을 복제하지 않는다.

### 1.3 도메인 예외

| 예외 | 발생 조건 | API 매핑(§2) |
|---|---|---|
| `InvalidQuantity` | 수량 < 1 | 422 (요청 검증 — 스키마에서 1차 차단, 도메인이 백스톱) |
| `ProductNotFound` | `product_id`에 해당 상품 없음 | 404 |
| `OutOfStock` | 재고 < 요청 수량(차감 판정 거부) | **409 Conflict** |
| `StockContentionExhausted` | 경합 재시도 상한 초과(실제 재고 부족 아님) | **503 Service Unavailable + Retry-After**(§2.3·§3.3) |

`exception.py`(커지면 패키지)에 정의. `StockContentionExhausted`는 `OutOfStock`과 **구분되는 별개 예외**다 — 재고 부족(영구적, 409)과 경합 소진(일시적, 503)은 의미가 다르다(api M4).

### 1.4 ordering ↔ catalog 협력 — 즉시 일관성, ACL 포트

**통합 스타일 선택(`references/final.md` §2 + `architecture-ddd` 규칙4·§6.8)**: 재고 차감은 **oversell을 동기적으로 차단**해야 하므로 **즉시 일관성**이 필요하다 → 비동기 도메인 이벤트(결과적 일관성)는 부적합. 따라서 동기 통합.

**OHS vs ACL**: catalog는 현재 OHS(`published_service/`)를 노출하지 않는다(미이주, 기존 평면 앱). 또한 oversell 차단을 위해 catalog 재고 행에 대한 원자적 차감·경합 가드가 같은 트랜잭션 안에서 필요하다 → 직접 통합이 불가피. 따라서 **ACL(부패 방지 계층)로 분리**한다:
- **도메인 협력 포트**: `ordering` 도메인에 `ProductStockPort`(ABC) — "지정 상품의 단가를 조회하고, 요청 수량만큼 재고 차감을 *요청*하라. 차감 판정 거부 시 도메인 예외(`OutOfStock`), 경합 소진 시 `StockContentionExhausted`" 역할을 정의. ordering 도메인은 이 포트에만 의존하고 catalog를 모른다.
- **ACL 어댑터**: `infra_layer/acl/`의 `DjangoProductStockPort` — catalog `Product` 도메인 동작을 호출·번역(업스트림 결과→ordering 예외). **catalog 모델 import는 이 어댑터에만 가둔다**(리포지토리에 섞지 않음 — houserules §3 레드플래그).

**재고 차감 판정의 소유권(자기점검 핵심 — 절 간 일관성, ddd M1·M2 / db BLOCKER-1 반영, 고정 결정)**:
재고(`stock`)를 소유한 것은 **catalog**다. **재고 충분성 판정(`stock >= qty`)은 catalog의 명명된 도메인 동작(`Product.deduct_stock(qty)` — OD-1 G1 확정으로 catalog에 추가)이 소유하고, 음수불가(`stock >= qty`) 판정을 그 동작 안에서 production 경로에 내린다.** ordering ACL 포트는 이 동작을 *호출(위임)*하고 결과(성공/`OutOfStock`)만 받는다.
- **판정 SQL 복제 금지(고정)**: `stock >= qty` 비즈니스 판정을 ordering 인프라의 SQL `WHERE`/`F()`나 ORM `update()`에 복제하지 않는다(`architecture-db` §9.5·§9.6 Rule ownership, `architecture-ddd` §3.2 빈혈 차단).
- **조건부 UPDATE 0행은 판정 대체물이 아니다**: 인프라의 `version` CAS 조건부 UPDATE에서 영향 0행은 **경합 재시도 트리거일 뿐**이며, 재고 충분성 판정을 대신하지 않는다. 0행이면 응용 서비스가 재조회 후 **catalog 도메인 동작부터 재실행**한다(§3.3). 판정은 항상 catalog 도메인 동작이 내린다.

**도메인 이벤트**: 채택하지 않는다. *왜* — 이번 범위에 결과적 일관성 후속(포인트·알림 등)이 없고(스코프 밖), 재고 차감은 즉시 일관성이라 이벤트가 아니라 동기 포트가 맞다(`references/final.md` §2 통합 스타일 선택). `domain_layer/order/event/` 폴더는 §0 불변식상 생성하되 비워 둔다.

---

## 2. 계약 (api lens)

### 2.1 API 어댑터 선택 — Django Ninja (신규 의존성 추가)

- **결정**: **Django Ninja**를 도입한다. settings `INSTALLED_APPS`에 추가하지 않아도 되지만(Ninja는 앱 등록 불필요) 패키지 의존성으로 `django-ninja`를 추가한다. *왜* — 프로젝트에 API 프레임워크가 없고(스코프 제약), Ninja는 Pydantic 기반 스키마·자동 OpenAPI·얇은 라우터로 표준 트리의 `presentation_layer/api`·`schema`와 정합한다. dddjango에 `implementation-django-ninja` 스킬이 존재해 구현 근거가 있다. DRF 대비 경량이고 타입 친화적(houserules §4 타입 어노테이션과 정합).
- **의존성 추가 명시**: `django-ninja`(Python 3.9 호환 버전). coder는 기존 패키지 매니저를 감지해 추가한다(houserules §6). Pydantic v1/v2는 설치된 Ninja 버전에 종속 — coder가 확정.

### 2.2 엔드포인트 계약

`architecture-api` §2(POST=non-idempotent 생성)·§3(명사 복수형 리소스).

| 항목 | 값 |
|---|---|
| Method · Path | `POST /api/orders` |
| 안전성·멱등성 | 안전하지 않음, 멱등 아님(POST 생성). |
| 인증 | 없음(익명, G0 확정). |
| 요청 Content-Type | `application/json` (미지원 타입은 **415**, §2.3). |
| 응답 표현 | **JSON 단일 표현, 콘텐츠 협상 안 함** — `Accept` 분기 없음. 따라서 **406 미사용**(정책상 단일 표현, §2.3). |

**요청 본문**(`schema_in`):
```
{ "product_id": <int, 필수, ≥1>, "quantity": <int, 필수, ≥1> }
```

**성공 응답 — 201 Created**(`schema_out`, 도메인 직접 직렬화 금지):
```
{ "order_id": <int>, "product_id": <int>, "quantity": <int>,
  "unit_price": <int>, "total_price": <int>,
  "status": "PLACED", "created_at": <ISO8601> }
```
- 헤더: `Location: /api/orders/{order_id}`(생성 리소스 위치. 조회 엔드포인트는 범위 밖이나 Location 관례는 둔다).

### 2.3 에러 계약 — RFC 9457 Problem Details

`architecture-api` §6. Content-Type `application/problem+json`. 모든 에러에 일관 적용.

**`type` URI 안정성(api M2)**: `type`은 RFC 9457상 "문서화 역할을 하는 안정적 URI"(`architecture-api` §6, line 253)다. 본 명세는 **상대 URI(`/problems/...`) + 베이스는 문서 루트(서비스 origin) 고정**으로 박는다 — 즉 `type`은 `{origin}/problems/<slug>`로 해석되는 안정 식별자이며, 경로 슬러그(`out-of-stock` 등)는 변경하지 않는다. coder는 베이스를 임의로 바꾸지 않는다.

| 상태 | 발생 | `type`(안정 URI, §6) | `title` | 비고 |
|---|---|---|---|---|
| **409 Conflict** | 재고 부족(`OutOfStock`) | `/problems/out-of-stock` | "Insufficient stock." | **재고·주문 상태 불변**(스코프). `detail`에 `requested`(요청 수량) 에코. `available`(가용 재고) 노출은 **익명 공개 카탈로그라 정보 민감도 없음** → 노출해도 무해(api minor m3). 단 차감 거부 시점 재고는 경합 중 변동 가능하므로 `available`은 *판정 시점 스냅샷*임을 detail 의미로 둔다. |
| 404 Not Found | 없는 상품(`ProductNotFound`) | `/problems/product-not-found` | "Product not found." | |
| **422 Unprocessable** | 필수 필드 누락·타입 오류·범위 위반(수량<1 등) 검증 실패 | `/problems/validation-error` | "Request validation failed." | **Ninja/Pydantic 검증 경로 1차**. 도메인 `InvalidQuantity`가 백스톱. 바디에 `errors: [{field, reason}]` 확장(api minor m2). **필수 필드 누락·타입·범위 위반은 모두 여기로 통합**(api minor m1) — 400과 구분. |
| **415 Unsupported Media Type** | 요청 `Content-Type`이 `application/json`이 아님 | `/problems/unsupported-media-type` | "Unsupported media type." | **요청 페이로드 형식 거절**(RFC 9110 §15.5.16). 400(malformed JSON)·422(검증)와 구분(api M1). |
| **400 Bad Request** | **malformed JSON(파싱 불가)으로 한정** | `/problems/bad-request` | "Malformed request." | 필수 필드 누락·타입·범위 위반은 400이 아니라 **422**로 보낸다(api minor m1, Ninja/Pydantic 검증 경로 정합). |

- **409 매핑의 핵심**: 동시성 하에서 재고 차감 판정 거부(catalog 도메인 동작의 `OutOfStock`)는 ordering 응용 서비스로 올라오고, 표현 계층이 이를 409 Problem Details로 변환한다. 트랜잭션은 롤백되어 주문 레코드도 남지 않는다(원자성, §3.2).
- **503 매핑(api M4 확정)**: 경합 재시도 상한 초과(`StockContentionExhausted`)는 **실제 재고 부족이 아닌 일시적 경합 소진**이므로 **503 Service Unavailable + `Retry-After` 헤더**로 계약한다(`/problems/stock-contention`, "Temporary contention, please retry."). 409(out-of-stock, 영구적)와 **의미를 분리**한다 — coder에게 위임하지 않고 design이 확정. *왜* — 클라이언트는 503+Retry-After를 재시도 신호로, 409를 비재시도(재고 없음)로 다르게 처리한다.
- 에러 본문 필드: `type`·`title`·`status`·`detail`(+409는 `requested`/`available`, 422는 `errors[]` 확장). `instance`는 선택.
- **버전 전략(api minor m5)**: 신규 API라 v1 단일. **URL prefix 미부여(무버전 `/api/orders`)로 시작**하고, 향후 호환 깨지는 변경이 필요할 때 URL 버전(`/api/v1/...`)을 도입한다(`architecture-api` §10). *왜* — 단일 신규 엔드포인트에 선제 버전 경로는 YAGNI, 도입 지점만 기록.

### 2.4 멱등성 키 — 미채택 확정 (중복 주문 갭 정직 기재)

`architecture-api` §13. POST 생성이라 중복 생성 위험이 이론상 있으나, `Idempotency-Key` 정책은 **미채택**(OD-2 G1 확정). *왜* — G0 스코프가 단일 생성 엔드포인트·동시성(oversell) 차단만 요구.

**중복 주문 갭(api M3, 정직 기재)**: §3.3의 oversell 동시성 가드는 **재고 초과 차감만 막을 뿐, 같은 의도의 2회 요청(네트워크 재시도 등)을 둘 다 정상 주문으로 받아 중복 주문 2건을 만든다.** 이는 oversell과 **다른 실패 모드**다 — 재고가 충분하면 둘 다 201이 된다. 멱등 키 미도입으로 이 **중복 주문 계약 노출은 후속까지 잔존한다(OD-2 확정, 수용됨)**. 후속에서 도입할 수 있으나, 그때까지 갭이 존재함을 계약 수준에서 명시한다.

---

## 3. 데이터 (db lens) — 신규 테이블·Risky Write

### 3.1 스키마 — OrderModel (신규)

Django ORM 모델 `OrderModel`(클래스명 `<Name>Model`, §0 불변식6·houserules §4). 위치 `infra_layer/django_ordering/models/order_model.py`.

| 컬럼 | 타입 | 제약·인덱스 |
|---|---|---|
| `id` | BigAutoField | PK |
| `product_id` | PositiveIntegerField | catalog `Product` ID 참조. **DB FK·인덱스 없는 정수 컬럼(OD-3 G1 확정)** — FK 미설정(BC 독립). |
| `quantity` | PositiveIntegerField | CHECK `quantity >= 1`(불변식 백스톱, 정본은 `Quantity` VO §1.1). |
| `unit_price` | PositiveIntegerField | 가격 스냅샷. |
| `total_price` | PositiveIntegerField | 파생값 저장(도메인 계산 결과). **불변 스냅샷이라 역정규화 anomaly 없음**(생성 후 `unit_price`·`quantity` 모두 불변이므로 갱신 이상 불가, db minor m1). |
| `status` | CharField(choices) | 기본 `PLACED`. |
| `created_at` | DateTimeField(auto) | 생성 시각. |

- **`product_id` 인덱스 — 두지 않는다(OD-3 G1 확정, YAGNI)**: 이번 범위에 `product_id` 기준 조회 엔드포인트가 없다(주문 조회/목록은 스코프 밖). 추측성 인덱스는 쓰기 비용만 늘린다(`architecture-db` §7). 필요해지는 후속에서 추가한다(OD-3 "추측성 보류").
- **orphan 우려 불요(db MAJOR-4)**: FK 미설정 시 상품 삭제로 주문이 orphan이 될 수 있으나, **주문은 `product_id` + 가격 스냅샷(`unit_price`·`total_price`)으로 자기완결적**이라 사후 조인이 불필요하다 → 정합성상 문제 없음. 무결성은 생성 시점 ACL 조회로 보장(존재하지 않으면 404).

마이그레이션: ordering 신규 테이블 생성 1건(Expand만, 기존 데이터 backfill 없음 — `architecture-db` §11).

**catalog `Product.version` 추가 마이그레이션 Rollout(db MAJOR-2, OD-1 G1 확정)**:
- **Expand 단계**: `version = IntegerField(default=0)` 추가. nullable 불필요(default 충족).
- **구코드 호환**: 기존 catalog 코드는 `version`을 읽거나 쓰지 않으므로(차감을 안 함) **무해**. 신규 ordering ACL 경로만 `version`을 CAS에 사용.
- **Backfill 불필요**: `default=0`이 기존 행을 즉시 충족(`architecture-db` §11.1 — default가 채우므로 별도 batch backfill 없음).
- **운영 Postgres lock 영향 확인 항목**: 상수 default 컬럼 추가는 PostgreSQL 11+ 에서 메타데이터만 변경(테이블 rewrite 없음)이라 짧은 lock이나, coder는 대상 Postgres 버전에서 **상수 default add가 full table rewrite를 유발하지 않는지** 확인한다(개발 SQLite는 무관).

### 3.2 트랜잭션 경계·원자성

- **Transaction owner**: ordering **응용 서비스**(`place_order` use case)가 트랜잭션 경계를 소유한다(`transaction.atomic()`). *왜* — 응용 서비스는 흐름·트랜잭션만 담당(§3.6), 비즈니스 로직은 도메인 위임.
- **원자 단위**: (재고 차감) + (Order 영속화)를 **하나의 트랜잭션**으로 묶는다. 재고 차감 거부(`OutOfStock`)면 트랜잭션 전체 롤백 → 주문 레코드 미생성·재고 불변(409 계약 §2.3 보장).
- **흐름**(빈혈 차단 순서 `architecture-ddd` §3.2): 조회(단가·상품 존재) → 도메인 `Order.place(...)` 생성(수량 검증·총액 계산) → ACL 포트로 재고 차감 위임(catalog 도메인 동작이 판정) → Order 영속화. 모두 한 `atomic()` 안.

### 3.3 동시성 / oversell 방지 — Risky Write Consistency Block (§9.6)

핵심 제약(스코프). 개발(SQLite)·운영(Postgres) 엔진차까지 확정(`architecture-db` §9.5 엔진 의존성).

> **전제(OD-1 G1 확정)**: 본 §3.3의 정합성은 **catalog `Product`에 `version` 컬럼 + `deduct_stock` 차감 도메인 동작 추가**(OD-1 옵션 A, G1 승인)를 토대로 **무조건 성립**한다. version CAS 경합 가드와 catalog 도메인 판정이 함께 정합성을 보장한다(폐기된 옵션 C는 version 부재로 이 정합성을 만족하지 못해 채택 불가였다 — §6 OD-1).

| 항목 | 결정 |
|---|---|
| **Transaction owner** | ordering 응용 서비스 `place_order`(§3.2). |
| **Locking strategy** | **낙관적 동시성 + version CAS 조건부 원자 UPDATE(경합 가드만) + CHECK 백스톱**을 환경 무관 방어선으로 채택. `select_for_update`(비관적 행 락)는 **운영 Postgres 전용 보강**으로만 둔다(SQLite no-op). *왜* — 개발 SQLite는 `select_for_update`를 무시하고 DEFERRED begin이 SELECT→UPDATE 락 승격 시 `database is locked` 데드락을 내므로, 락만으로는 환경 무관 정확성이 성립 안 함(§9.5). |
| **경합 가드 메커니즘(단일 방어선, OD-1 확정)** | catalog 재고 차감을 **version CAS 조건부 원자 UPDATE**로 수행: `WHERE id=? AND version=<read_version>`(**경합 가드만**), `SET stock = stock - qty, version = version + 1`. **비즈니스 판정(`stock >= qty`)은 `WHERE`/`F()`에 복제하지 않는다** — 판정은 catalog 도메인 동작(`Product.deduct_stock`)이 내린다(§1.4·§9.5·§9.6 Rule ownership). UPDATE 영향 0행이면 **경합**(다른 트랜잭션이 version을 올림) → 응용 서비스가 재조회 후 **catalog 도메인 동작부터 재실행**(bounded retry). **CAS 0행은 판정 대체물이 아니라 재시도 트리거**다. |
| **불변식 백스톱(CHECK)** | catalog `Product.stock`은 `PositiveIntegerField`(이미 음수 불가) + ordering `OrderModel.quantity >= 1` CHECK. 재고가 음수로 떨어지는 최후 경로를 DB가 차단. 이는 *불변식*이지 트랜잭션 *판정*이 아니다(§9.5). **정상 경로에선 version CAS·도메인 판정이 먼저 막으므로 CHECK 위반(IntegerError)은 도달 불가에 가깝다**(아래 CHECK 번역 경로). |
| **CHECK 위반 번역 경로(db MAJOR-1, 경합 재시도와 구분)** | DB `IntegrityError`(stock CHECK 위반)는 **"version CAS 누락 신호"**다 — 정상 경로면 도메인 판정·version CAS가 먼저 차단하므로 여기 도달하면 안 된다. 따라서 IntegrityError 경로는 (1) `OutOfStock`이 아니라 **경합 가드 누락/버그 신호로 로깅**하고, (2) "UPDATE 0행 → 경합 재시도" 경로와 **명시적으로 분리**한다(0행=정상 경합 재시도, IntegrityError=비정상 백스톱 발동). Test criteria (e)에 반영. |
| **SQLite 직렬화 설정(db minor m2 — db가 결정)** | 개발/테스트 SQLite connection에 **`busy_timeout` 하한 5000ms(5초)** 설정, **begin 모드 IMMEDIATE**로 직렬화(쓰기 트랜잭션 시작 시 즉시 RESERVED lock 획득 → DEFERRED의 SELECT→UPDATE 승격 데드락 회피). 이 값·모드는 **명세가 결정**(§9.5 "연결 설정을 명세가 명시")하고, 구체 connection init 코드만 coder가 작성. *왜* — DEFERRED 기본은 경합 시 `database is locked` 데드락. |
| **Rule ownership** | 재고 충분성 판정·재고 불변식은 재고 소유자 **catalog의 도메인 동작**(`Product.deduct_stock`, OD-1 확정)이 소유. ordering 인프라·SQL은 version 경합 가드와 결과 저장만. 주문 불변식(수량·총액)은 Order 애그리거트 소유. |
| **Idempotency storage** | 없음(§2.4 멱등 키 미채택 OD-2 확정, 중복 주문 갭 잔존). |
| **Side-effect timing** | 외부 부수효과 없음(결제·알림 범위 밖). 트랜잭션 내 외부 I/O 없음(§9.6). |
| **Isolation/retry(db MAJOR-3 — 트랜잭션 경계 확정)** | OLTP 기본 Read Committed(운영 Postgres). **retry 트랜잭션 경계: 각 시도 = 독립 `atomic()` 블록, retry 루프는 트랜잭션 밖**(한 시도 실패 시 롤백 후 새 트랜잭션으로 재시도 — 실패한 시도의 부분 변경이 다음 시도에 새지 않음). version CAS 0행(경합) 시 **bounded retry 최대 3회** — 응용 서비스가 재조회→catalog 도메인 동작 재실행. **상한 초과 시 `StockContentionExhausted` → 503 + Retry-After**(§2.3, 409 out-of-stock과 의미 분리, api M4). |
| **Test criteria** | (a) 단일 요청 성공 시 재고 차감·주문 생성·201, (b) 재고 부족 시 409·재고 불변·주문 미생성, (c) **동시 N요청(재고 M<N)에 정확히 M건만 성공·oversell 0**, (d) 차감 실패 시 트랜잭션 롤백(주문·재고 부분 변경 없음), (e) **retry 최종 실패(경합 소진) 시 부분 변경 없음(원자성) + 503**, (f) **CHECK 위반(IntegrityError)은 정상 경로에서 도달 불가 — 발생 시 경합 가드 누락 신호로 로깅됨**을 검증. |

---

## 4. 패키지·테스트 구조 결정 (lens 무관, 항상 결정)

`discipline-houserules` §1.2 표준 파일트리(`references/final.md`) 적용. §0 불변식 전부 생성(YAGNI로 생략 금지). 신규 `ordering` 앱만 생성, 기존 `catalog/`·`config/`는 settings·urls 최소 등록(§4.3)과 OD-1 G1 확정에 따른 `Product` 차감 동작·`version` 추가(§3.1)를 제외하고 미변경.

### 4.1 ordering 앱 트리 (생성)

```
application/                                   # 컨테이너(불변식1) — 신규
└── ordering/
    ├── ordering_api_router.py                 # 라우터 진입점(루트 urls가 포함)
    ├── published_service/                     # OHS(불변식: 비어도 폴더). 이번 범위 노출 없음 → 빈 패키지
    │
    ├── domain_layer/
    │   └── order/                             # 애그리거트(개념) 1차
    │       ├── order.py                       # 애그리거트 루트 Order(bare 이름) + Order.place() 팩토리
    │       ├── entity/                        # 종속 엔티티 없음 → 빈 패키지(불변식4)
    │       ├── value_object/
    │       │   └── quantity.py                # Quantity VO
    │       ├── repository/
    │       │   └── order_repository.py        # class OrderRepository(ABC) — DIP 포트(§4 명명)
    │       ├── port/                          # ACL 협력 포트
    │       │   └── product_stock_port.py      # class ProductStockPort(ABC)
    │       ├── domain_service/                # 빈 패키지(불변식4)
    │       ├── event/                         # 빈 패키지(이벤트 미채택 §1.4)
    │       ├── specification/                 # 빈 패키지
    │       └── exception.py                   # InvalidQuantity·ProductNotFound·OutOfStock·StockContentionExhausted
    │
    ├── application_layer/
    │   ├── place_order/                       # feature 1차
    │   │   ├── command/
    │   │   │   └── place_order_app.py         # 응용 서비스(트랜잭션 경계·흐름·bounded retry, 도메인 위임)
    │   │   ├── query/                         # 빈 패키지(조회 범위 밖)
    │   │   ├── dto/
    │   │   │   └── place_order_command.py     # 입력 DTO(command 객체)
    │   │   ├── handler/                       # 빈 패키지(이벤트 미채택)
    │   │   └── service/                       # 빈 패키지
    │   └── unit_of_work.py                    # [선택] — transaction.atomic()로 충분, 둘지는 §4.4
    │
    ├── infra_layer/
    │   ├── django_ordering/                   # Django 앱(불변식5) — startapp 여기서
    │   │   ├── apps.py                        # name='application.ordering.infra_layer.django_ordering', label='ordering'
    │   │   ├── models/
    │   │   │   └── order_model.py             # class OrderModel(불변식6)
    │   │   ├── migrations/
    │   │   └── admin/                         # [선택] 비어도 폴더
    │   ├── repository/
    │   │   └── order_repository.py            # class DjangoOrderRepository(OrderRepository 구현, §4 명명)
    │   ├── acl/                               # 외부 컨텍스트 ACL
    │   │   └── catalog_acl.py                 # class DjangoProductStockPort(ProductStockPort 구현) — catalog Product 도메인 동작 소비·번역
    │   └── service/                           # 빈 패키지(외부 I/O 없음)
    │
    ├── presentation_layer/
    │   ├── api/
    │   │   └── place_order/
    │   │       └── api_order.py               # 얇은 어댑터(파싱→응용 호출→응답·예외 변환: 409/503/404/422/415/400)
    │   └── schema/
    │       ├── schema_in.py                   # 요청 계약(product_id, quantity)
    │       ├── schema_out.py                  # 201 응답 DTO(도메인 직접 직렬화 금지)
    │       └── error_out.py                   # RFC 9457 Problem Details 스키마(errors[]·requested/available 확장 포함)
    │
    └── test/                                  # 의미군 분리(implementation-test §4.2)
        ├── unit/
        │   ├── test_order.py                  # Order·Quantity 불변식·총액 계산(순수 단위)
        │   └── test_place_order_app.py        # 응용 서비스 흐름·retry 경계(포트·리포지토리 stub/mock)
        ├── integration/
        │   ├── test_order_repository.py       # DjangoOrderRepository ↔ 실제 DB
        │   ├── test_catalog_acl.py            # 재고 차감 ACL ↔ catalog Product 도메인 동작·version CAS(실제 DB)
        │   ├── test_place_order_api.py        # POST /api/orders 엔드포인트(201/409/503/404/422/415/400)
        │   └── test_concurrency.py            # 동시 N요청 oversell 0·경합 소진 503 검증(§3.3 Test criteria c·e)
        └── e2e/                               # [선택] 비워 둠
```

### 4.2 명명 규약 적용(`references/final.md` §4 — 설계 단계에서 확정, 사후 교정 금지)

| 대상 | 추상화(포트/인터페이스) | 구현(어댑터) | 파일명(약어 금지) |
|---|---|---|---|
| 주문 리포지토리 | `OrderRepository`(ABC, domain) | `DjangoOrderRepository`(infra) | `order_repository.py` |
| 재고 협력 포트(ACL) | `ProductStockPort`(ABC, domain `port/`) | `DjangoProductStockPort`(infra `acl/`) | `product_stock_port.py` / `catalog_acl.py` |
| 도메인 애그리거트 | `Order`(bare) | — | `order.py` |
| ORM 모델 | — | `OrderModel`(`<Name>Model`) | `order_model.py` |
| **catalog 측 재고 차감 동작(OD-1 G1 확정)** | — | **`Product.deduct_stock(qty)`**(catalog `Product`의 명명된 도메인 동작) | catalog 측 |

- **포트↔catalog 동작 매핑(ddd minor m1)**: ordering `ProductStockPort.deduct(product_id, qty)` (도메인 포트 메서드) ↔ ACL `DjangoProductStockPort`가 catalog `Product.deduct_stock(qty)`(판정 소유 동작)를 호출·번역. 판정은 catalog 동작이 내리고, 포트는 결과(성공/`OutOfStock`/`StockContentionExhausted`)만 ordering 도메인 언어로 전달.
- `Interface`/`Impl` 타입 표식 금지. 구현은 `Django` 한정자 접두 + base명 일치(역할 접미사 `Port`/`Repository` 유지).
- ACL은 `acl/`에 두고 `repository/`에 섞지 않는다(houserules §3 레드플래그). catalog 모델 import는 `catalog_acl.py`에만.

### 4.3 settings·urls 최소 변경(기존 config)

- `INSTALLED_APPS`에 `'application.ordering.infra_layer.django_ordering'` 등록(불변식5 점경로).
- `config/urls.py`에 `ordering_api_router`를 포함(Ninja `NinjaAPI` 인스턴스 마운트, `/api/` 프리픽스). Ninja 인스턴스 1개 생성 위치는 coder가 표준에 맞춰 결정(루트 또는 앱 라우터). catalog는 (OD-1 G1 확정 `Product` 변경을 제외하고) urls/settings 변경 없음.
- **SQLite connection 설정(§3.3)**: test/dev settings의 DB connection에 `busy_timeout=5000`·begin 모드 IMMEDIATE를 명시(값은 §3.3에서 결정, 구체 코드만 coder).

### 4.4 타입·주석·언어(houserules §4·§5)

- 함수·메서드 시그니처 타입 어노테이션 **필수**(프로덕션). 테스트 시그니처 타입은 권장(nit).
- 주석·docstring: 기존 코드베이스에 확립된 주석 언어 관례 없음 → **한국어**(전역 지침·houserules §5). 한 코드베이스 안에서 섞지 않는다.

### 4.5 OpenAPI 반영 표면(api minor m4)

`architecture-api` §14 — 모든 계약을 OpenAPI에 반영한다. Ninja 자동 생성에 다음이 빠짐없이 나타나야 한다:
- 에러 응답 미디어 타입 `application/problem+json`(201만 `application/json`).
- 201 `Location` 헤더.
- 415·422·409·503·404·400 다중 에러 응답 스키마(각 상태별 `error_out` 표현, 422의 `errors[]`·409의 `requested`/`available`·503의 `Retry-After`).

---

## 5. 외부 관찰 가능 행위 목록 (인수 테스트 근거 — 슬라이스)

acceptance-tester는 이 목록을 검증한다:

1. 재고 충분 시 `POST /api/orders` → **201**, 응답에 `order_id`·가격 스냅샷(`unit_price`·`total_price`)·`status=PLACED`, `Location` 헤더. 재고는 요청 수량만큼 차감된다.
2. 재고 부족 시 → **409** `application/problem+json`(`type=/problems/out-of-stock`, `requested` 에코). **재고·주문 상태 불변**(주문 미생성).
3. 없는 `product_id` → **404**(`/problems/product-not-found`).
4. `quantity < 1`·타입 오류·필수 필드 누락 → **422**(`/problems/validation-error`, `errors[]`). 주문 미생성.
5. 잘못된 JSON(malformed, 파싱 불가) → **400**(`/problems/bad-request`).
6. 요청 `Content-Type`이 `application/json` 아님 → **415**(`/problems/unsupported-media-type`).
7. **동시성**: 재고 M인 상품에 동시 N(>M) 주문 → 정확히 **M건만 201, 나머지 409**(또는 경합 소진 시 503), **oversell 0**. 차감 실패 건은 트랜잭션 롤백(주문 미생성).
8. **경합 소진**: retry 상한 초과 시 → **503 + `Retry-After`**(`/problems/stock-contention`). 부분 변경 없음(원자성). 409(out-of-stock)와 의미 구분.

---

## 6. 확정 결정 (G1 게이트에서 사용자 확정, 2026-05-29)

> G1에서 사용자가 미해결 결정을 모두 닫았다. 아래는 확정된 결정이며, 이후 인수 테스트·구현·감수의 단일 근거다. **§1.4 "판정을 ordering 인프라 SQL에 복제 금지" 원칙·§3.3 version CAS 단일 방어선은 고정**이다.

### OD-1 — 재고 차감 판정 소유 + catalog 변경 (**G1 확정: 옵션 A 승인**)

catalog `Product`는 재고를 소유한다. ddd·db 두 lens가 옵션 A로 수렴했고, **사용자가 G1에서 옵션 A를 승인**해 catalog 변경(스코프 소폭 확장)을 허가했다.

- **G1 확정: 옵션 A 채택** — catalog `Product`에 **`version` 컬럼**(마이그레이션 1건, §3.1 Rollout) + **`Product.deduct_stock(qty)` 명명 도메인 동작**(`stock >= qty` 판정 소유)을 추가한다. ordering ACL(`DjangoProductStockPort`)이 이를 호출하고, version CAS 0행이면 재조회·재시도(§3.3). 재고 판정이 catalog(소유자)에 머물러 빈혈/판정 복제를 회피하고, 환경 무관(SQLite/Postgres)하게 §3.3 정합성을 만족한다. 동시성 방어선은 **version CAS 조건부 UPDATE 단일 경로**(CHECK은 백스톱).
- **옵션 B — 폐기**: 옵션 A + 운영 Postgres `select_for_update` 보강. SQLite no-op이라 개발/테스트는 여전히 낙관적 경로 의존(이중 경로 복잡도). 단 §3.3 Locking strategy에 기재한 대로 `select_for_update`는 *운영 Postgres 전용 보강*으로만 남길 수 있다(필수 경로 아님).
- **옵션 C — 폐기**: ordering ACL이 catalog Product를 직접 조건부 UPDATE(catalog 무변경). `version` 부재로 §3.3 version CAS 경합 가드 미성립(데이터 정합성 blocker), 재고 판정 소유가 catalog→ordering으로 이전되어 BC 경계·빈혈 원칙 위반(도메인 blocker). blocker 2건으로 채택 불가.

### OD-2 — 멱등성 키(`Idempotency-Key`) (**G1 확정: 미도입**)

POST 생성의 네트워크 재시도 중복 방지. **G1 확정: 미도입**(스코프 고수). §3.3 oversell 가드는 중복 주문(같은 의도 2회 → 주문 2건)을 막지 못하며, 미도입에 따라 이 **중복 주문 계약 노출이 후속까지 잔존함을 사용자가 수용**했다(§2.4·api M3). 도입은 후속 기능으로 미룬다(도입 시 키 저장소·replay/conflict 계약 추가, `architecture-api` §13).

### OD-3 — `OrderModel.product_id`의 DB FK 여부 + 인덱스 (**G1 확정: FK 미설정·인덱스 없음**)

별개 BC(ordering/catalog) 간 참조. **G1 확정: `OrderModel.product_id`는 DB FK·인덱스 없는 정수 컬럼**(`PositiveIntegerField`)으로 둔다. 규칙3(ID 참조)·BC 독립·orphan 자기완결성(§3.1)과 정합하며, 무결성은 생성 시점 ACL 조회(없으면 404)로 보장한다. `product_id` 인덱스는 이번 범위에 조회 엔드포인트가 없어 두지 않는다(YAGNI, db MAJOR-4) — 조회 엔드포인트 후속에서 추가(추측성 보류).

---

## 7. 자기모순 스캔 결과(넘기기 전 1회)

- **재고 판정 소유권**: §0(catalog 소유)·§1.4(catalog 도메인 동작이 판정, ordering은 위임)·§3.3(Rule ownership: catalog `deduct_stock`이 판정, CAS 0행은 재시도 트리거)·§4.2(포트↔동작 매핑)·§6 OD-1(옵션 A 확정) 일관. 판정을 ordering 인프라가 갖는 옵션 C는 정합성·도메인 blocker 2건으로 폐기.
- **명명**: `OrderRepository`/`DjangoOrderRepository`, `ProductStockPort`/`DjangoProductStockPort`, `Order`/`OrderModel`, `Product.deduct_stock` — §1·§4.1·§4.2 전반 일치.
- **409 vs 503 분리**: §1.3(`OutOfStock`→409, `StockContentionExhausted`→503)·§2.3(상태표·매핑)·§3.3(Isolation/retry: 소진→503)·§5(행위2·7·8) 일치. 재고 부족(영구)·경합 소진(일시) 의미 분리 일관.
- **에러 상태 구분**: 400(malformed JSON)·415(미지원 Content-Type)·422(검증·필드 누락·범위) — §2.3·§5·§4.5 일치, 서로 겹치지 않음.
- **version CAS 단일화**: §3.3 version CAS 단일 방어선, CHECK은 백스톱(판정 아님). §1.4·§3.3·§6 OD-1 일관(OD-1 옵션 A 확정으로 무조건 성립).
- **이벤트 미채택**: §1.4·§4.1(event/handler 빈 패키지) 일치.
- **인덱스·FK YAGNI**: §3.1(product_id 인덱스·FK 없음)·§6 OD-3(FK 미설정·인덱스 없음 확정) 일치.
- 모순 미발견(OD-1/2/3 모두 G1 확정으로 닫힘).
