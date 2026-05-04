현재 작업공간은 비어 있고 읽기 전용이라 `config.toml` 확인, 파일 생성, 실행 검증은 하지 못했습니다. 아래 설계는 **DRF가 아니라 Django Ninja Router/Schema** 기준이며, PostgreSQL + Django ORM을 가정합니다.

**권장 접근**

재고 예약은 **DB 트랜잭션 + 재고 row lock + DB 기반 idempotency record**로 처리하는 구성이 가장 안전합니다.

대안은 세 가지입니다.

| 접근 | 장점 | 단점 | 판단 |
|---|---|---|---|
| DB idempotency + `select_for_update()` | 단순하고 강한 일관성, 장애 후 복구 쉬움 | 락 경합 가능 | 추천 |
| Redis idempotency + DB 락 | 빠름 | Redis/DB 불일치 복구 설계 필요 | 트래픽이 큰 경우 |
| 큐 기반 비동기 예약 | 피크 트래픽 흡수 | 즉시 예약 성공/실패 응답 어려움 | 대규모 이벤트성 판매 |

**API 리소스**

동사는 URL에 넣지 않고, 예약 자체를 리소스로 둡니다.

| Method | Path | 설명 |
|---|---|---|
| `POST` | `/v1/inventory-reservations` | 재고 예약 생성 |
| `GET` | `/v1/inventory-reservations/{reservation_id}` | 예약 조회 |
| `DELETE` | `/v1/inventory-reservations/{reservation_id}` | 예약 취소 및 재고 해제 |
| `PUT` | `/v1/inventory-reservations/{reservation_id}/confirmation` | 예약 확정 |

`POST /v1/inventory-reservations`는 반드시 헤더를 요구합니다.

```http
Idempotency-Key: 7f1d2fb0-7e1a-4c42-b0e4-8f65bda6e7d8
Content-Type: application/json
```

요청 예시:

```json
{
  "reference_id": "cart-20260504-001",
  "expires_in_seconds": 900,
  "items": [
    {"sku_id": "sku_iphone_15_black_128", "quantity": 2},
    {"sku_id": "sku_case_clear", "quantity": 1}
  ]
}
```

성공 응답은 `201 Created`와 `Location` 헤더를 반환합니다. 같은 idempotency key의 재시도는 저장된 동일 status/body를 반환하고 `X-Idempotent-Replay: true`를 붙입니다.

**Django Ninja Schema/Router 골격**

```python
from datetime import datetime
from uuid import UUID

from ninja import Header, Router, Schema

router = Router(tags=["inventory-reservations"])


class ReservationItemIn(Schema):
    sku_id: str
    quantity: int


class CreateInventoryReservationIn(Schema):
    reference_id: str
    expires_in_seconds: int = 900
    items: list[ReservationItemIn]


class ReservationItemOut(Schema):
    sku_id: str
    quantity: int


class InventoryReservationOut(Schema):
    id: UUID
    reference_id: str
    status: str
    expires_at: datetime
    items: list[ReservationItemOut]


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str


@router.post(
    "",
    response={
        201: InventoryReservationOut,
        400: ProblemDetail,
        409: ProblemDetail,
        422: ProblemDetail,
    },
)
def create_inventory_reservation(
    request,
    payload: CreateInventoryReservationIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> tuple[int, InventoryReservationOut]:
    result = reservation_service.reserve(
        user_id=request.auth.id,
        command=payload,
        idempotency_key=idempotency_key,
        method="POST",
        path="/v1/inventory-reservations",
    )
    return 201, result
```

라우터 합성은 문자열 경로가 아니라 router 객체를 넘기는 방식이 좋습니다.

```python
from ninja import NinjaAPI
from inventory.api import router as inventory_router

api = NinjaAPI(version="1.0.0")
api.add_router("/v1/inventory-reservations", inventory_router)
```

**Idempotency 설계**

`idempotency_records` 테이블을 둡니다.

| 컬럼 | 설명 |
|---|---|
| `id` | PK |
| `owner_id` | 사용자/클라이언트 ID |
| `method` | `POST` |
| `path` | `/v1/inventory-reservations` |
| `key` | `Idempotency-Key` |
| `request_hash` | 정규화한 body hash |
| `status` | `processing`, `succeeded`, `failed` |
| `response_status` | 최초 처리 결과 status |
| `response_body` | 최초 처리 결과 body |
| `expires_at` | 보통 24시간 후 |
| `created_at` | 생성 시각 |

제약 조건:

```text
UNIQUE(owner_id, method, path, key)
INDEX(expires_at)
```

처리 순서:

1. `Idempotency-Key` 없으면 `400`.
2. 같은 `owner_id + method + path + key`로 record 생성 시도.
3. 이미 있으면 `request_hash`를 비교한다.
4. hash가 다르면 `409 idempotency-key-reused`.
5. hash가 같고 완료된 record면 저장된 응답을 그대로 replay.
6. 첫 요청이면 같은 DB 트랜잭션 안에서 예약 생성, 응답 저장, commit.
7. commit 전 같은 key 요청은 unique constraint 때문에 대기하거나, 별도 `processing` 정책이면 `409` + `Retry-After` 반환.

검증 실패처럼 실행 전 단계의 오류는 idempotency record에 저장하지 않고, 재고 부족 같은 도메인 결과는 저장하는 편이 재시도 의미가 명확합니다.

**동시성 처리**

재고 불변식은 다음입니다.

```text
0 <= reserved_quantity <= on_hand_quantity
available_quantity = on_hand_quantity - reserved_quantity
```

예약 생성은 하나의 `transaction.atomic()` 안에서 처리합니다.

1. 요청 item의 `sku_id`를 정렬합니다.
2. `InventoryStock.objects.select_for_update().filter(sku_id__in=sku_ids).order_by("sku_id")`로 row lock을 잡습니다.
3. 모든 SKU의 `available_quantity >= requested_quantity`를 확인합니다.
4. 하나라도 부족하면 전체 rollback 후 `409 insufficient-inventory`.
5. 모두 충분하면 각 row의 `reserved_quantity`를 증가시킵니다.
6. `inventory_reservations`, `inventory_reservation_lines`를 생성합니다.
7. idempotency response를 저장하고 commit합니다.

정렬 후 lock을 잡는 이유는 여러 SKU를 동시에 예약할 때 deadlock 가능성을 낮추기 위해서입니다. PostgreSQL 기본값인 Read Committed에서도 row lock이 재고 차감 경합을 직렬화하므로 보통 충분합니다. Serializable까지 올리면 재시도 로직이 필요하고 처리량이 떨어집니다.

**DB 모델**

| 테이블 | 핵심 컬럼 |
|---|---|
| `inventory_stocks` | `sku_id`, `on_hand_quantity`, `reserved_quantity`, `updated_at` |
| `inventory_reservations` | `id`, `owner_id`, `reference_id`, `status`, `expires_at`, `created_at` |
| `inventory_reservation_lines` | `reservation_id`, `sku_id`, `quantity` |
| `idempotency_records` | `owner_id`, `method`, `path`, `key`, `request_hash`, `response_status`, `response_body`, `expires_at` |

추천 제약:

```text
inventory_stocks.sku_id UNIQUE
CHECK(on_hand_quantity >= 0)
CHECK(reserved_quantity >= 0)
CHECK(reserved_quantity <= on_hand_quantity)

inventory_reservation_lines UNIQUE(reservation_id, sku_id)
idempotency_records UNIQUE(owner_id, method, path, key)
```

만료 처리는 배치 작업이 `expires_at < now()`이고 `status = "reserved"`인 예약을 `select_for_update(skip_locked=True)`로 가져와 `expired`로 바꾸고 `reserved_quantity`를 감소시킵니다.

**DDD 모델**

Bounded Context는 `Inventory`입니다. 주문, 결제, 상품 카탈로그와 분리하고 ID로만 연결합니다.

| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| `InventoryReservation` | 일정 시간 동안 재고를 선점한 예약 | hold, lock |
| `InventoryStock` | SKU별 물리/예약 수량의 일관성 경계 | stock row |
| `ReservedQuantity` | 아직 확정되지 않았지만 사용 불가한 수량 | blocked qty |
| `AvailableQuantity` | 예약 가능한 수량 | free stock |

Aggregate Root:

```python
@dataclass
class InventoryStock:
    """Aggregate Root.

    Invariants:
    - on_hand_quantity >= 0
    - reserved_quantity >= 0
    - reserved_quantity <= on_hand_quantity
    """
    sku_id: SkuId
    on_hand_quantity: Quantity
    reserved_quantity: Quantity

    def reserve(self, quantity: Quantity) -> None:
        if self.available_quantity < quantity:
            raise InsufficientInventoryError(self.sku_id)
        self.reserved_quantity = self.reserved_quantity.add(quantity)

    def release(self, quantity: Quantity) -> None:
        self.reserved_quantity = self.reserved_quantity.subtract(quantity)
```

Value Object는 `frozen=True` dataclass로 두고 `__post_init__`에서 검증합니다.

```python
@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise InvalidQuantityError(self.value)
```

Repository ABC는 도메인 계층에 둡니다.

```python
class InventoryStockRepository(ABC):
    @abstractmethod
    def find_by_sku_ids_for_update(self, sku_ids: list[str]) -> list[InventoryStock]:
        ...

    @abstractmethod
    def save_all(self, stocks: list[InventoryStock]) -> None:
        ...
```

응용 서비스는 트랜잭션, idempotency, repository 호출을 조율하고, 실제 재고 규칙은 aggregate에 위임합니다.

발행 이벤트는 과거형으로 명명합니다.

```python
InventoryReservedEvent
InventoryReservationCancelledEvent
InventoryReservationExpiredEvent
InventoryReservationConfirmedEvent
```

**오류 응답**

모든 오류는 RFC 9457 Problem Details 형식으로 통일합니다.

```json
{
  "type": "https://api.example.com/problems/insufficient-inventory",
  "title": "Insufficient Inventory",
  "status": 409,
  "detail": "sku_iphone_15_black_128 has only 1 available item.",
  "instance": "/v1/inventory-reservations"
}
```

권장 status:

| 상황 | Status |
|---|---|
| `Idempotency-Key` 누락 | `400` |
| 같은 key를 다른 body로 재사용 | `409` |
| 같은 key 요청이 아직 처리 중 | `409` + `Retry-After` |
| 재고 부족 | `409` |
| body 검증 실패 | `422` |
| 인증 없음 | `401` |
| 권한 없음 | `403` |
| rate limit 초과 | `429` + `Retry-After` |

---
> **관련 스킬 참조:**
> - API 엔드포인트/멱등성 → **architecture-api** 스킬
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬
> - 재고 트랜잭션/인덱스 → **architecture-db** 스킬
> - Inventory 도메인 모델링 → **architecture-ddd** 스킬