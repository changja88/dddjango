# 음식 배달 플랫폼 - 도메인 이벤트 설계

## Bounded Context 정의

| Bounded Context | 책임 |
|---|---|
| **Order** | 주문 생성, 주문 상태 관리 |
| **Restaurant** | 주문 수락/거절, 조리 상태 관리 |
| **Delivery** | 배달 기사 배정, 픽업, 배달 상태 관리 |
| **Payment** | 결제 처리, 정산 |
| **Notification** | 알림 발송 (SMS, 푸시, 이메일) |

## Aggregate 정의

| Aggregate | Bounded Context | Root Entity | 주요 속성 |
|---|---|---|---|
| **Order** | Order | Order | orderId, customerId, restaurantId, items, status, totalAmount |
| **Restaurant** | Restaurant | Restaurant | restaurantId, name, acceptedOrders |
| **Cooking** | Restaurant | CookingTicket | ticketId, orderId, status, estimatedTime |
| **Delivery** | Delivery | Delivery | deliveryId, orderId, riderId, status, pickupAddress, dropoffAddress |
| **Payment** | Payment | Payment | paymentId, orderId, amount, status |

## 전체 이벤트 흐름

```
[고객 주문]
    → OrderPlaced
        → Restaurant: 주문 수락 판단
        → Notification: 레스토랑에 신규 주문 알림
        → Payment: 결제 선점(pre-auth)

[레스토랑 수락]
    → OrderAccepted
        → Restaurant/Cooking: 조리 티켓 생성
        → Notification: 고객에게 주문 수락 알림

[조리 시작]
    → CookingStarted
        → Notification: 고객에게 조리 시작 알림

[조리 완료]
    → CookingCompleted
        → Delivery: 배달 기사 배정 시작
        → Notification: 고객에게 조리 완료 알림

[배달 기사 배정]
    → RiderAssigned
        → Notification: 고객/레스토랑에 기사 정보 알림
        → Notification: 기사에게 픽업 정보 알림

[배달 기사 픽업]
    → OrderPickedUp
        → Notification: 고객에게 배달 출발 알림

[배달 완료]
    → OrderDelivered
        → Notification: 고객에게 배달 완료 알림

[고객 수령 확인]
    → DeliveryConfirmed
        → Payment: 결제 정산 처리
        → Notification: 레스토랑에 정산 예정 알림
        → Notification: 기사에게 배달 완료 확정 알림

[결제 정산 완료]
    → PaymentSettled
        → Notification: 레스토랑에 정산 완료 알림
```

## 도메인 이벤트 상세

### 1단계: 주문 생성

**이벤트: `OrderPlaced`**

| 항목 | 내용 |
|---|---|
| 발행 주체 | Order (Order Context) |
| 트리거 | 고객이 주문 버튼 클릭 |
| 페이로드 | orderId, customerId, restaurantId, items[], totalAmount, deliveryAddress, placedAt |

| 구독자 | 처리 내용 |
|---|---|
| Restaurant Context | 해당 레스토랑에 주문 접수 요청 전달 |
| Payment Context | 결제 수단 유효성 확인 및 금액 선점(pre-authorization) |
| Notification Context | 레스토랑에 신규 주문 알림 발송 |

---

### 2단계: 레스토랑 주문 수락 및 조리 시작

**이벤트: `OrderAccepted`**

| 항목 | 내용 |
|---|---|
| 발행 주체 | Restaurant (Restaurant Context) |
| 트리거 | 레스토랑이 주문 수락 |
| 페이로드 | orderId, restaurantId, estimatedCookingTime, acceptedAt |

| 구독자 | 처리 내용 |
|---|---|
| Order Context | 주문 상태를 ACCEPTED로 변경 |
| Restaurant Context (Cooking) | CookingTicket 생성, 조리 시작 |
| Notification Context | 고객에게 주문 수락 알림 (예상 조리 시간 포함) |

**이벤트: `CookingStarted`**

| 항목 | 내용 |
|---|---|
| 발행 주체 | Cooking (Restaurant Context) |
| 트리거 | 조리 티켓 생성 후 조리 착수 |
| 페이로드 | orderId, ticketId, estimatedCompletionTime, startedAt |

| 구독자 | 처리 내용 |
|---|---|
| Order Context | 주문 상태를 COOKING으로 변경 |
| Notification Context | 고객에게 조리 시작 알림 |

---

### 3단계: 조리 완료 및 배달 기사 배정

**이벤트: `CookingCompleted`**

| 항목 | 내용 |
|---|---|
| 발행 주체 | Cooking (Restaurant Context) |
| 트리거 | 레스토랑이 조리 완료 처리 |
| 페이로드 | orderId, ticketId, restaurantId, pickupAddress, completedAt |

| 구독자 | 처리 내용 |
|---|---|
| Delivery Context | 배달 기사 매칭 알고리즘 실행, Delivery Aggregate 생성 |
| Order Context | 주문 상태를 COOKED로 변경 |
| Notification Context | 고객에게 조리 완료 알림 |

**이벤트: `RiderAssigned`**

| 항목 | 내용 |
|---|---|
| 발행 주체 | Delivery (Delivery Context) |
| 트리거 | 배달 기사 매칭 완료 |
| 페이로드 | deliveryId, orderId, riderId, riderName, riderPhone, estimatedPickupTime, assignedAt |

| 구독자 | 처리 내용 |
|---|---|
| Order Context | 주문 상태를 RIDER_ASSIGNED로 변경, 기사 정보 연결 |
| Notification Context | 고객에게 배달 기사 배정 알림, 레스토랑에 기사 도착 예정 알림, 기사에게 픽업 주소 및 주문 정보 알림 |

---

### 4단계: 배달 기사 픽업 및 배달 시작

**이벤트: `OrderPickedUp`**

| 항목 | 내용 |
|---|---|
| 발행 주체 | Delivery (Delivery Context) |
| 트리거 | 배달 기사가 음식 픽업 확인 |
| 페이로드 | deliveryId, orderId, riderId, pickedUpAt, estimatedDeliveryTime |

| 구독자 | 처리 내용 |
|---|---|
| Order Context | 주문 상태를 IN_DELIVERY로 변경 |
| Notification Context | 고객에게 배달 출발 알림 (예상 도착 시간 포함) |

---

### 5단계: 배달 완료 및 결제 정산

**이벤트: `OrderDelivered`**

| 항목 | 내용 |
|---|---|
| 발행 주체 | Delivery (Delivery Context) |
| 트리거 | 배달 기사가 배달 완료 처리 |
| 페이로드 | deliveryId, orderId, riderId, deliveredAt |

| 구독자 | 처리 내용 |
|---|---|
| Order Context | 주문 상태를 DELIVERED로 변경 |
| Notification Context | 고객에게 배달 완료 및 수령 확인 요청 알림 |

**이벤트: `DeliveryConfirmed`**

| 항목 | 내용 |
|---|---|
| 발행 주체 | Order (Order Context) |
| 트리거 | 고객이 수령 확인 (또는 일정 시간 후 자동 확인) |
| 페이로드 | orderId, customerId, confirmedAt |

| 구독자 | 처리 내용 |
|---|---|
| Payment Context | 선점된 결제 금액 최종 캡처 및 정산 처리 시작 |
| Delivery Context | 배달 건 완료 확정, 기사 정산 대상 등록 |
| Notification Context | 레스토랑에 정산 예정 알림, 기사에게 배달 완료 확정 알림 |

**이벤트: `PaymentSettled`**

| 항목 | 내용 |
|---|---|
| 발행 주체 | Payment (Payment Context) |
| 트리거 | 정산 처리 완료 |
| 페이로드 | paymentId, orderId, restaurantAmount, riderAmount, platformFee, settledAt |

| 구독자 | 처리 내용 |
|---|---|
| Order Context | 주문 상태를 COMPLETED로 변경 |
| Notification Context | 레스토랑에 정산 완료 알림 |

## 이벤트-컨텍스트 매핑 요약

| 도메인 이벤트 | 발행 Context | 구독 Context |
|---|---|---|
| OrderPlaced | Order | Restaurant, Payment, Notification |
| OrderAccepted | Restaurant | Order, Restaurant(Cooking), Notification |
| CookingStarted | Restaurant | Order, Notification |
| CookingCompleted | Restaurant | Delivery, Order, Notification |
| RiderAssigned | Delivery | Order, Notification |
| OrderPickedUp | Delivery | Order, Notification |
| OrderDelivered | Delivery | Order, Notification |
| DeliveryConfirmed | Order | Payment, Delivery, Notification |
| PaymentSettled | Payment | Order, Notification |

## Order 상태 전이 다이어그램

```
PLACED → ACCEPTED → COOKING → COOKED → RIDER_ASSIGNED → IN_DELIVERY → DELIVERED → CONFIRMED → COMPLETED
                                                                                         ↓
                                                                                   (자동 확인: 30분 타임아웃)
```

## 설계 원칙

1. **이벤트 기반 느슨한 결합**: 각 Bounded Context는 직접 호출하지 않고 도메인 이벤트를 통해서만 통신한다.
2. **Notification Context는 순수 구독자**: 비즈니스 로직 없이 이벤트를 수신하여 알림만 발송하는 별도 컨텍스트로 분리한다.
3. **Order Aggregate가 상태 추적의 단일 진실 공급원(Single Source of Truth)**: 다른 컨텍스트의 이벤트를 구독하여 주문 상태를 일관되게 관리한다.
4. **Payment는 2단계 처리**: OrderPlaced 시 선점(pre-auth), DeliveryConfirmed 시 최종 캡처로 안전한 결제 흐름을 보장한다.
5. **최종 일관성(Eventual Consistency)**: 컨텍스트 간 통신은 비동기 이벤트로 처리하며, 즉각적 강한 일관성 대신 최종 일관성을 수용한다.
