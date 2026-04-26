# 음식 배달 플랫폼 주문 처리 흐름 -- 도메인 이벤트 설계

## 1. 전략 설계: 하위 도메인과 바운디드 컨텍스트

### 1.1 하위 도메인 분류

| 하위 도메인 | 유형 | 근거 |
|------------|------|------|
| 주문(Ordering) | 핵심(Core) | 플랫폼의 핵심 비즈니스 흐름. 주문 생성, 상태 전이, 비즈니스 규칙이 집중됨 |
| 레스토랑(Restaurant) | 핵심(Core) | 주문 수락/거부 판단, 조리 관리 등 플랫폼 경쟁력의 핵심 |
| 배달(Delivery) | 핵심(Core) | 기사 배정 알고리즘, 실시간 위치 추적 등 차별화 요소 |
| 정산(Settlement) | 지원(Supporting) | 결제 완료 후 정산 처리. 비즈니스 규칙이 존재하나 상대적으로 안정적 |
| 알림(Notification) | 일반(Generic) | 푸시/SMS/이메일 발송. 외부 솔루션 활용 가능 |
| 결제(Payment) | 일반(Generic) | PG사 연동. 외부 솔루션 의존 |

### 1.2 바운디드 컨텍스트 정의

각 핵심/지원 하위 도메인을 독립된 바운디드 컨텍스트로 설계한다. 같은 "주문"이라는 용어가 각 컨텍스트에서 다른 의미를 갖는다.

| 바운디드 컨텍스트 | 유비쿼터스 언어에서의 "주문" |
|-----------------|------------------------|
| 주문(Ordering) | 고객이 요청한 음식 목록과 배달 주소를 포함하는 주문서 |
| 레스토랑(Restaurant) | 조리해야 할 접수 건 (메뉴 항목과 수량 중심) |
| 배달(Delivery) | 픽업지에서 배달지로 운송해야 할 배달 건 |
| 정산(Settlement) | 레스토랑/기사에게 지급해야 할 정산 대상 거래 |

### 1.3 컨텍스트 맵

```
[주문 컨텍스트] ---(이벤트 발행)---> [레스토랑 컨텍스트]
     |                                    |
     |                              (이벤트 발행)
     |                                    |
     |                                    v
     |                            [배달 컨텍스트]
     |                                    |
     |                              (이벤트 발행)
     |                                    |
     +------------------------------------+
     |                                    |
     v                                    v
[결제 컨텍스트]                    [정산 컨텍스트]
     |
     v
[알림 컨텍스트] <--- (모든 컨텍스트의 이벤트를 구독)
```

**컨텍스트 간 관계:**

| 업스트림 | 다운스트림 | 패턴 | 근거 |
|---------|----------|------|------|
| 주문 | 레스토랑 | OHS + Published Language | 주문 컨텍스트가 표준 이벤트를 발행하고, 레스토랑 컨텍스트가 ACL로 수신 |
| 레스토랑 | 배달 | OHS + Published Language | 조리 완료 이벤트를 배달 컨텍스트가 ACL로 수신 |
| 배달 | 정산 | OHS + Published Language | 배달 완료 이벤트를 정산 컨텍스트가 ACL로 수신 |
| 결제 | 정산 | 고객-공급자(Customer-Supplier) | 정산이 결제 정보를 필요로 함 |
| 모든 컨텍스트 | 알림 | 순응주의자(Conformist) | 알림은 각 이벤트의 페이로드를 그대로 사용하여 메시지를 구성 |

---

## 2. 전술 설계: 애그리거트와 도메인 이벤트

### 2.1 각 바운디드 컨텍스트의 애그리거트

Vernon의 4가지 규칙에 따라 애그리거트를 작게 유지하고, 다른 애그리거트는 ID로만 참조한다.

| 바운디드 컨텍스트 | 애그리거트 | 루트 엔티티 | 포함하는 값 객체 |
|-----------------|-----------|-----------|----------------|
| 주문 | Order | Order | OrderLineItem, DeliveryAddress, Money |
| 레스토랑 | Ticket | Ticket | TicketLineItem |
| 배달 | Delivery | Delivery | PickupAddress, DropoffAddress |
| 배달 | Courier | Courier | Location |
| 결제 | Payment | Payment | Money |
| 정산 | Settlement | Settlement | SettlementAmount, Commission |
| 알림 | Notification | Notification | Recipient, MessageContent |

### 2.2 주문 처리 흐름 -- 도메인 이벤트 전체 설계

#### 단계 1: 고객이 음식을 주문 -- 주문 생성

```
[액터] 고객
[커맨드] 주문을 접수하라 (PlaceOrder)
[애그리거트] Order (주문 컨텍스트)
[도메인 이벤트] OrderPlaced (주문이 접수되었다)
```

**OrderPlaced 이벤트:**

```python
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: str
    customer_id: str
    restaurant_id: str
    order_line_items: tuple  # (product_id, product_name, quantity, price)
    delivery_address: str
    total_amount: int
```

**구독하는 컨텍스트와 후속 행동:**

| 구독 컨텍스트 | 핸들러 | 후속 행동 |
|-------------|--------|----------|
| 레스토랑 | OrderPlacedHandler | Ticket 애그리거트를 생성하여 레스토랑에 주문 접수 건을 전달 |
| 결제 | OrderPlacedHandler | Payment 애그리거트를 생성하여 결제를 요청(승인 대기) |
| 알림 | OrderPlacedHandler | 고객에게 "주문이 접수되었습니다" 알림 발송 |
| 알림 | OrderPlacedHandler | 레스토랑에게 "새로운 주문이 들어왔습니다" 알림 발송 |

---

#### 단계 2: 레스토랑이 주문을 수락 -- 조리 시작

```
[액터] 레스토랑
[커맨드] 주문을 수락하라 (AcceptTicket)
[애그리거트] Ticket (레스토랑 컨텍스트)
[도메인 이벤트] TicketAccepted (주문이 수락되었다)
```

**TicketAccepted 이벤트:**

```python
@dataclass(frozen=True)
class TicketAccepted(DomainEvent):
    ticket_id: str
    order_id: str
    restaurant_id: str
    estimated_preparation_minutes: int
```

**구독하는 컨텍스트와 후속 행동:**

| 구독 컨텍스트 | 핸들러 | 후속 행동 |
|-------------|--------|----------|
| 주문 | TicketAcceptedHandler | Order의 상태를 ACCEPTED로 전이 |
| 결제 | TicketAcceptedHandler | Payment의 결제를 확정(capture) |
| 알림 | TicketAcceptedHandler | 고객에게 "레스토랑이 주문을 수락했습니다. 예상 조리 시간: N분" 알림 발송 |

---

#### 단계 3: 조리 완료 -- 배달 기사 배정

```
[액터] 레스토랑
[커맨드] 조리 완료를 알려라 (MarkTicketReady)
[애그리거트] Ticket (레스토랑 컨텍스트)
[도메인 이벤트] TicketReadyForPickup (조리가 완료되었다)
```

**TicketReadyForPickup 이벤트:**

```python
@dataclass(frozen=True)
class TicketReadyForPickup(DomainEvent):
    ticket_id: str
    order_id: str
    restaurant_id: str
    pickup_address: str
```

**구독하는 컨텍스트와 후속 행동:**

| 구독 컨텍스트 | 핸들러 | 후속 행동 |
|-------------|--------|----------|
| 배달 | TicketReadyHandler | Delivery 애그리거트를 생성하고, 근처 가용 Courier를 탐색하여 배정 |
| 주문 | TicketReadyHandler | Order의 상태를 READY_FOR_PICKUP으로 전이 |
| 알림 | TicketReadyHandler | 고객에게 "음식 조리가 완료되었습니다. 배달 기사를 배정 중입니다" 알림 발송 |

**배달 기사 배정 시 발행되는 후속 이벤트:**

```
[정책] 조리 완료 시 배달 기사를 배정한다
[애그리거트] Delivery (배달 컨텍스트)
[도메인 이벤트] CourierAssigned (배달 기사가 배정되었다)
```

```python
@dataclass(frozen=True)
class CourierAssigned(DomainEvent):
    delivery_id: str
    order_id: str
    courier_id: str
    estimated_pickup_minutes: int
```

| 구독 컨텍스트 | 핸들러 | 후속 행동 |
|-------------|--------|----------|
| 주문 | CourierAssignedHandler | Order에 배정된 기사 정보를 기록 |
| 알림 | CourierAssignedHandler | 고객에게 "배달 기사 OOO님이 배정되었습니다" 알림 발송 |
| 알림 | CourierAssignedHandler | 배달 기사에게 "새로운 배달 건이 배정되었습니다" 알림 발송 |
| 알림 | CourierAssignedHandler | 레스토랑에게 "기사가 N분 후 도착 예정입니다" 알림 발송 |

---

#### 단계 4: 배달 기사가 픽업 -- 배달 시작

```
[액터] 배달 기사
[커맨드] 픽업을 완료하라 (ConfirmPickup)
[애그리거트] Delivery (배달 컨텍스트)
[도메인 이벤트] DeliveryPickedUp (배달 기사가 음식을 픽업했다)
```

**DeliveryPickedUp 이벤트:**

```python
@dataclass(frozen=True)
class DeliveryPickedUp(DomainEvent):
    delivery_id: str
    order_id: str
    courier_id: str
    picked_up_at: datetime
```

**구독하는 컨텍스트와 후속 행동:**

| 구독 컨텍스트 | 핸들러 | 후속 행동 |
|-------------|--------|----------|
| 주문 | DeliveryPickedUpHandler | Order의 상태를 IN_DELIVERY로 전이 |
| 알림 | DeliveryPickedUpHandler | 고객에게 "배달 기사가 음식을 픽업했습니다. 배달이 시작됩니다" 알림 발송 |

---

#### 단계 5: 배달 완료 후 고객 확인 -- 결제 정산

```
[액터] 배달 기사
[커맨드] 배달 완료를 알려라 (CompleteDelivery)
[애그리거트] Delivery (배달 컨텍스트)
[도메인 이벤트] DeliveryCompleted (배달이 완료되었다)
```

**DeliveryCompleted 이벤트:**

```python
@dataclass(frozen=True)
class DeliveryCompleted(DomainEvent):
    delivery_id: str
    order_id: str
    courier_id: str
    delivered_at: datetime
```

**구독하는 컨텍스트와 후속 행동:**

| 구독 컨텍스트 | 핸들러 | 후속 행동 |
|-------------|--------|----------|
| 주문 | DeliveryCompletedHandler | Order의 상태를 DELIVERED로 전이 |
| 알림 | DeliveryCompletedHandler | 고객에게 "배달이 완료되었습니다. 수령을 확인해주세요" 알림 발송 |

**고객 수령 확인 시:**

```
[액터] 고객
[커맨드] 수령을 확인하라 (ConfirmReceipt)
[애그리거트] Order (주문 컨텍스트)
[도메인 이벤트] OrderConfirmed (고객이 수령을 확인했다)
```

```python
@dataclass(frozen=True)
class OrderConfirmed(DomainEvent):
    order_id: str
    customer_id: str
    confirmed_at: datetime
    total_amount: int
```

| 구독 컨텍스트 | 핸들러 | 후속 행동 |
|-------------|--------|----------|
| 정산 | OrderConfirmedHandler | Settlement 애그리거트를 생성하여 레스토랑/기사 정산을 개시 |
| 알림 | OrderConfirmedHandler | 레스토랑에게 "주문 정산이 시작됩니다" 알림 발송 |
| 알림 | OrderConfirmedHandler | 배달 기사에게 "배달 완료 정산이 시작됩니다" 알림 발송 |

**정산 완료 시:**

```
[정책] 고객 수령 확인 시 정산을 처리한다
[애그리거트] Settlement (정산 컨텍스트)
[도메인 이벤트] SettlementCompleted (정산이 완료되었다)
```

```python
@dataclass(frozen=True)
class SettlementCompleted(DomainEvent):
    settlement_id: str
    order_id: str
    restaurant_amount: int
    courier_amount: int
    platform_commission: int
    settled_at: datetime
```

| 구독 컨텍스트 | 핸들러 | 후속 행동 |
|-------------|--------|----------|
| 알림 | SettlementCompletedHandler | 레스토랑에게 "정산 금액 OOO원이 입금 예정입니다" 알림 발송 |
| 알림 | SettlementCompletedHandler | 배달 기사에게 "배달비 OOO원이 입금 예정입니다" 알림 발송 |

---

## 3. 이벤트 흐름 종합 정리

```
[1] 고객 --- PlaceOrder ---> Order --- OrderPlaced --->  레스토랑(Ticket 생성)
                                                    |-> 결제(Payment 생성)
                                                    |-> 알림(고객, 레스토랑)

[2] 레스토랑 --- AcceptTicket ---> Ticket --- TicketAccepted --->  주문(상태 전이)
                                                              |-> 결제(결제 확정)
                                                              |-> 알림(고객)

[3] 레스토랑 --- MarkTicketReady ---> Ticket --- TicketReadyForPickup --->  배달(Delivery 생성, 기사 배정)
                                                                       |-> 주문(상태 전이)
                                                                       |-> 알림(고객)
    [3-1] 배달 --- (자동) ---> Delivery --- CourierAssigned --->  주문(기사 정보 기록)
                                                             |-> 알림(고객, 기사, 레스토랑)

[4] 기사 --- ConfirmPickup ---> Delivery --- DeliveryPickedUp --->  주문(상태 전이)
                                                               |-> 알림(고객)

[5] 기사 --- CompleteDelivery ---> Delivery --- DeliveryCompleted --->  주문(상태 전이)
                                                                   |-> 알림(고객)
    [5-1] 고객 --- ConfirmReceipt ---> Order --- OrderConfirmed --->  정산(Settlement 생성)
                                                                 |-> 알림(레스토랑, 기사)
    [5-2] 정산 --- (자동) ---> Settlement --- SettlementCompleted --->  알림(레스토랑, 기사)
```

## 4. 설계 결정 근거

### 4.1 애그리거트 간 결과적 일관성

모든 단계에서 애그리거트 간 상태 동기화는 도메인 이벤트를 통한 결과적 일관성(eventual consistency)으로 처리한다. 예를 들어 `TicketAccepted`가 발행되면, 주문 컨텍스트의 Order 상태 전이는 별도 트랜잭션에서 수행된다. 이는 Vernon의 애그리거트 설계 규칙 4를 따른 것이다.

### 4.2 ID 참조

각 컨텍스트의 애그리거트는 다른 컨텍스트의 애그리거트를 ID로만 참조한다. Ticket은 `order_id`를 문자열로 보유하며, Order 객체를 직접 참조하지 않는다. 이는 Vernon의 규칙 3에 해당한다.

### 4.3 알림 컨텍스트의 위치

알림은 일반(Generic) 하위 도메인이다. 모든 컨텍스트의 도메인 이벤트를 구독하는 순응주의자(Conformist) 관계로 설계했다. 알림 컨텍스트는 업스트림 이벤트의 페이로드를 그대로 사용하여 메시지를 구성하므로, 별도의 ACL이 필요하지 않다.

### 4.4 Saga 패턴 적용 지점

주문 생성 시 결제 승인이 필요한 구간(단계 1~2)은 Saga 패턴(Orchestration 방식)으로 구현한다. 결제 실패 시 Order를 취소하는 보상 트랜잭션이 필요하기 때문이다.

```
PlaceOrder Saga:
  1. Order 생성 (주문 컨텍스트)
  2. Payment 승인 요청 (결제 컨텍스트)
  3-성공. Ticket 생성 (레스토랑 컨텍스트)
  3-실패. Order 취소 (보상 트랜잭션)
```

### 4.5 이벤트 이름의 유비쿼터스 언어

모든 이벤트 이름은 과거형으로, 비즈니스 도메인의 언어를 반영한다. `StatusUpdated`가 아닌 `TicketAccepted`, `DeliveryPickedUp`처럼 비즈니스 의도가 드러나는 이름을 사용한다. 이는 유비쿼터스 언어 원칙을 따른 것이다.

### 4.6 Outbox 패턴

컨텍스트 간 이벤트 전달의 신뢰성을 보장하기 위해 Outbox 패턴을 적용한다. 각 애그리거트의 상태 변경과 이벤트 저장이 동일 트랜잭션 안에서 이루어지고, 별도 프로세서가 Outbox에서 이벤트를 읽어 메시지 브로커에 발행한다. 이벤트 유실을 방지하는 핵심 인프라 패턴이다.
