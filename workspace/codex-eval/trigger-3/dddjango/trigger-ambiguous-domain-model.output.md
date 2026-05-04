**[주요 내용]**

정확히 나누려면 “어떤 비즈니스인지”가 필요합니다. 우선은 **Django 기반 업무 서비스이고, 주문/결제/배송/정산처럼 상태 전이와 외부 연동이 있는 도메인**이라는 가정으로 답하겠습니다.

도메인 모델은 Django 앱이나 DB 테이블 기준이 아니라, 먼저 **바운디드 컨텍스트**로 나누는 게 좋습니다.

| 후보 Context | 책임 | Aggregate Root | 주요 불변식 |
|---|---|---|---|
| 주문 | 고객의 구매 의사, 주문 확정/취소 | `Order` | 확정된 주문은 임의 수정 불가, 취소 가능 상태 제한 |
| 결제 | 승인/캡처/환불 | `Payment` | 승인 금액과 캡처 금액의 통화/한도 일치 |
| 재고 | 예약/차감/해제 | `StockReservation` | 예약 수량은 가용 수량을 초과할 수 없음 |
| 배송 | 출고/배송 상태 | `Shipment` | 출고 후 주소 변경 제한 |
| 정산 | 판매자 지급/수수료 | `Settlement` | 정산 완료 후 금액 변경 불가 |

나누는 기준은 이 순서로 보면 됩니다.

1. **같은 단어가 다른 의미로 쓰이면 Context를 분리**
   예: 주문의 `confirmed`는 고객 주문 확정, 결제의 `confirmed`는 PG 승인 완료일 수 있습니다.

2. **한 트랜잭션에서 반드시 지켜야 하는 규칙만 같은 Aggregate에 둠**
   `Order`가 `Payment`, `Shipment`, `Stock` 객체를 직접 들고 있으면 대개 너무 큽니다. `payment_id`, `shipment_id`처럼 ID로 연결하고, 변경은 도메인 이벤트로 이어갑니다.

3. **Django ORM 모델을 곧바로 도메인 모델로 보지 않음**
   복잡한 핵심 도메인은 대략 이렇게 둡니다.

```text
orders/
  domain/
    model/order/
      order.py
      value_objects.py
      events.py
      repository.py
    service.py
  application/
    confirm_order.py
  infrastructure/
    django_models.py
    django_order_repository.py
```

도메인 계층의 Repository 인터페이스는 사용하는 쪽이 소유합니다.

```python
class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Order: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...
```

Application Service는 유스케이스 조율만 합니다. 비즈니스 판단은 Aggregate 메서드에 둡니다.

```python
class ConfirmOrderService:
    def confirm(self, order_id: OrderId) -> None:
        order = self.orders.find_by_id(order_id)
        order.confirm()
        self.orders.save(order)
```

유비쿼터스 언어도 먼저 고정하세요.

| 권장 용어 | 의미 | 금지 동의어 |
|---|---|---|
| `confirm` | 주문 확정 | `update_status`, `set_done` |
| `authorize` | 결제 승인 | `pay`, `success` |
| `reserve` | 재고 예약 | `hold`, `minus` |
| `dispatch` | 출고 처리 | `send`, `ship_start` |

핵심 원칙은 간단합니다: **Context는 언어와 책임 기준으로 나누고, Aggregate는 불변식 기준으로 작게 유지하고, Django/DB 구조는 그다음에 맞춥니다.**

---
> **관련 스킬 참조:**
> - Django 구현 구조와 Repository/Service 배치 → **architecture-implementation-patterns** 스킬