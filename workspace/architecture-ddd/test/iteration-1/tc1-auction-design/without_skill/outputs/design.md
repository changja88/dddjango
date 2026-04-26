# 온라인 경매 시스템 DDD 설계

## 1. 바운디드 컨텍스트 (Bounded Contexts)

### 1.1 상품 컨텍스트 (Catalog Context)
판매자가 경매에 출품할 상품을 등록하고 관리하는 영역.

### 1.2 경매 컨텍스트 (Auction Context)
경매의 생성, 입찰, 종료, 낙찰 등 경매의 핵심 생명주기를 담당하는 영역.

### 1.3 결제 컨텍스트 (Payment Context)
낙찰 후 결제 생성과 판매자 정산을 처리하는 영역.

### 1.4 배송 컨텍스트 (Shipping Context)
낙찰 후 상품 배송 과정을 관리하는 영역.

### 1.5 평가 컨텍스트 (Review Context)
거래 확정 후 구매자와 판매자 간 상호 평가를 관리하는 영역.

### 1.6 회원 컨텍스트 (Member Context)
구매자, 판매자의 계정과 프로필을 관리하는 영역.

---

## 2. 컨텍스트 맵 (Context Map)

```
[회원 컨텍스트] ──(U/D)──> [상품 컨텍스트]
                ──(U/D)──> [경매 컨텍스트]
                ──(U/D)──> [결제 컨텍스트]
                ──(U/D)──> [평가 컨텍스트]

[상품 컨텍스트] ──(U/D)──> [경매 컨텍스트]

[경매 컨텍스트] ──(Pub/Sub)──> [결제 컨텍스트]
               ──(Pub/Sub)──> [배송 컨텍스트]

[결제 컨텍스트] ──(Pub/Sub)──> [배송 컨텍스트]

[배송 컨텍스트] ──(Pub/Sub)──> [결제 컨텍스트]
               ──(Pub/Sub)──> [평가 컨텍스트]
```

- **U/D (Upstream/Downstream)**: 회원, 상품 컨텍스트는 다른 컨텍스트에 식별자를 제공하는 상류.
- **Pub/Sub**: 경매 종료 이후 흐름은 도메인 이벤트 기반의 비동기 통신.

---

## 3. 애그리거트 (Aggregates)

### 3.1 상품 컨텍스트

#### Product (애그리거트 루트)
| 속성 | 타입 | 설명 |
|------|------|------|
| productId | ProductId | 상품 식별자 |
| sellerId | SellerId | 판매자 식별자 |
| title | String | 상품명 |
| description | String | 상품 설명 |
| images | List\<Image\> | 상품 이미지 목록 |
| category | Category | 카테고리 |
| condition | ItemCondition | 상품 상태 (새상품/중고) |
| status | ProductStatus | DRAFT, REGISTERED, IN_AUCTION, SOLD |
| createdAt | DateTime | 등록일시 |

**행위**:
- `register()` -- 상품을 등록 상태로 변경
- `markInAuction()` -- 경매 시작 시 상태 변경
- `markSold()` -- 낙찰 시 상태 변경

---

### 3.2 경매 컨텍스트

#### Auction (애그리거트 루트)
| 속성 | 타입 | 설명 |
|------|------|------|
| auctionId | AuctionId | 경매 식별자 |
| productId | ProductId | 상품 식별자 (참조) |
| sellerId | SellerId | 판매자 식별자 |
| startingPrice | Money | 시작가 |
| currentHighestBid | Bid | 현재 최고 입찰 (VO) |
| bids | List\<Bid\> | 입찰 이력 |
| startTime | DateTime | 경매 시작 시간 |
| endTime | DateTime | 경매 종료 시간 |
| status | AuctionStatus | SCHEDULED, ACTIVE, ENDED, AWARDED, FAILED |
| winnerId | BidderId | 낙찰자 식별자 |

**행위**:
- `open()` -- 경매를 활성 상태로 전환. 시작 시간 검증.
- `placeBid(bidderId, amount)` -- 입찰. 현재 최고가보다 높아야 하며, 판매자 본인은 입찰 불가.
- `close()` -- 경매 종료. 최고 입찰자를 낙찰자로 결정. 입찰이 없으면 유찰.

#### Bid (값 객체)
| 속성 | 타입 | 설명 |
|------|------|------|
| bidId | BidId | 입찰 식별자 |
| bidderId | BidderId | 입찰자 식별자 |
| amount | Money | 입찰 금액 |
| bidTime | DateTime | 입찰 시간 |

**불변식 (Invariants)**:
- 입찰 금액은 반드시 현재 최고 입찰가보다 커야 한다.
- 입찰 금액은 반드시 시작가 이상이어야 한다.
- 경매가 ACTIVE 상태일 때만 입찰할 수 있다.
- 판매자 본인은 자신의 경매에 입찰할 수 없다.
- 경매 종료 시간이 지난 경매에는 입찰할 수 없다.

---

### 3.3 결제 컨텍스트

#### Payment (애그리거트 루트)
| 속성 | 타입 | 설명 |
|------|------|------|
| paymentId | PaymentId | 결제 식별자 |
| auctionId | AuctionId | 경매 식별자 (참조) |
| buyerId | BuyerId | 구매자(낙찰자) 식별자 |
| sellerId | SellerId | 판매자 식별자 |
| amount | Money | 결제 금액 |
| status | PaymentStatus | PENDING, COMPLETED, FAILED, REFUNDED |
| createdAt | DateTime | 결제 생성일시 |
| completedAt | DateTime | 결제 완료일시 |

**행위**:
- `create()` -- 낙찰 이벤트 수신 시 결제 생성 (PENDING 상태)
- `complete()` -- 결제 완료 처리
- `fail()` -- 결제 실패 처리
- `refund()` -- 환불 처리

#### Settlement (애그리거트 루트)
| 속성 | 타입 | 설명 |
|------|------|------|
| settlementId | SettlementId | 정산 식별자 |
| paymentId | PaymentId | 결제 식별자 (참조) |
| sellerId | SellerId | 판매자 식별자 |
| amount | Money | 정산 금액 |
| fee | Money | 수수료 |
| netAmount | Money | 실 정산 금액 |
| status | SettlementStatus | PENDING, SETTLED |
| settledAt | DateTime | 정산 완료일시 |

**행위**:
- `create()` -- 거래 확정 시 정산 생성
- `settle()` -- 정산 실행 (판매자 계좌로 이체)

---

### 3.4 배송 컨텍스트

#### Shipment (애그리거트 루트)
| 속성 | 타입 | 설명 |
|------|------|------|
| shipmentId | ShipmentId | 배송 식별자 |
| auctionId | AuctionId | 경매 식별자 (참조) |
| sellerId | SellerId | 판매자 식별자 |
| buyerId | BuyerId | 구매자 식별자 |
| shippingAddress | Address | 배송지 주소 (VO) |
| trackingNumber | String | 운송장 번호 |
| carrier | String | 택배사 |
| status | ShipmentStatus | AWAITING_SHIPMENT, SHIPPED, IN_TRANSIT, DELIVERED, CONFIRMED |
| shippedAt | DateTime | 발송일시 |
| deliveredAt | DateTime | 배송 완료일시 |
| confirmedAt | DateTime | 수령 확정일시 |

**행위**:
- `create()` -- 결제 완료 시 배송 대기 상태로 생성
- `ship(trackingNumber, carrier)` -- 판매자가 발송 처리
- `markDelivered()` -- 배송 완료 표시
- `confirmReceipt()` -- 구매자가 수령 확정

---

### 3.5 평가 컨텍스트

#### Review (애그리거트 루트)
| 속성 | 타입 | 설명 |
|------|------|------|
| reviewId | ReviewId | 평가 식별자 |
| auctionId | AuctionId | 경매 식별자 (참조) |
| reviewerId | MemberId | 평가 작성자 식별자 |
| revieweeId | MemberId | 평가 대상자 식별자 |
| rating | Rating | 평점 (1~5) (VO) |
| comment | String | 평가 내용 |
| reviewType | ReviewType | BUYER_TO_SELLER, SELLER_TO_BUYER |
| createdAt | DateTime | 작성일시 |

**행위**:
- `write(rating, comment)` -- 평가 작성

**불변식**:
- 거래 확정(수령 확정) 이후에만 평가를 작성할 수 있다.
- 동일 경매에 대해 같은 방향의 평가는 한 번만 작성할 수 있다.
- 평점은 1~5 사이의 정수여야 한다.

---

### 3.6 회원 컨텍스트

#### Member (애그리거트 루트)
| 속성 | 타입 | 설명 |
|------|------|------|
| memberId | MemberId | 회원 식별자 |
| email | Email | 이메일 (VO) |
| nickname | String | 닉네임 |
| address | Address | 기본 주소 (VO) |
| rating | AverageRating | 평균 평점 (VO) |
| status | MemberStatus | ACTIVE, SUSPENDED, WITHDRAWN |

---

## 4. 도메인 이벤트 (Domain Events)

### 4.1 상품 컨텍스트
| 이벤트 | 발행 시점 | 주요 데이터 |
|--------|-----------|-------------|
| ProductRegistered | 상품 등록 완료 | productId, sellerId |

### 4.2 경매 컨텍스트
| 이벤트 | 발행 시점 | 주요 데이터 |
|--------|-----------|-------------|
| AuctionOpened | 경매 시작 | auctionId, productId, sellerId, startingPrice, endTime |
| BidPlaced | 입찰 성공 | auctionId, bidId, bidderId, amount, bidTime |
| AuctionEnded | 경매 종료 시간 도달 | auctionId |
| AuctionAwarded | 낙찰 결정 | auctionId, productId, winnerId, sellerId, finalPrice |
| AuctionFailed | 유찰 (입찰 없음) | auctionId, productId |

### 4.3 결제 컨텍스트
| 이벤트 | 발행 시점 | 주요 데이터 |
|--------|-----------|-------------|
| PaymentCreated | 결제 생성 | paymentId, auctionId, buyerId, amount |
| PaymentCompleted | 결제 완료 | paymentId, auctionId, buyerId, sellerId, amount |
| PaymentFailed | 결제 실패 | paymentId, auctionId, reason |
| SettlementCompleted | 정산 완료 | settlementId, sellerId, netAmount |

### 4.4 배송 컨텍스트
| 이벤트 | 발행 시점 | 주요 데이터 |
|--------|-----------|-------------|
| ShipmentCreated | 배송 대기 생성 | shipmentId, auctionId, sellerId, buyerId |
| ItemShipped | 판매자 발송 처리 | shipmentId, trackingNumber, carrier |
| ItemDelivered | 배송 완료 | shipmentId |
| ReceiptConfirmed | 구매자 수령 확정 | shipmentId, auctionId, buyerId, sellerId |

### 4.5 평가 컨텍스트
| 이벤트 | 발행 시점 | 주요 데이터 |
|--------|-----------|-------------|
| ReviewWritten | 평가 작성 완료 | reviewId, auctionId, reviewerId, revieweeId, rating |

---

## 5. 이벤트 흐름 (Event Flow)

경매의 전체 생명주기를 이벤트 흐름으로 표현한다.

```
[판매자: 상품 등록]
    │
    ▼
ProductRegistered
    │
    ▼
[판매자: 경매 시작]
    │
    ▼
AuctionOpened
    │
    ▼
[구매자: 입찰] ──────► BidPlaced (반복)
    │
    ▼
[스케줄러: 경매 종료 시간 도달]
    │
    ▼
AuctionEnded
    │
    ├── 입찰 있음 ──► AuctionAwarded ──► [결제 컨텍스트] PaymentCreated
    │                                         │
    │                                         ▼
    │                                    PaymentCompleted
    │                                         │
    │                                         ▼
    │                                    [배송 컨텍스트] ShipmentCreated
    │                                         │
    │                                         ▼
    │                                    [판매자: 발송 처리] ItemShipped
    │                                         │
    │                                         ▼
    │                                    ItemDelivered
    │                                         │
    │                                         ▼
    │                                    [구매자: 수령 확정] ReceiptConfirmed
    │                                         │
    │                                    ┌────┴────┐
    │                                    ▼         ▼
    │                              [결제 컨텍스트]  [평가 컨텍스트]
    │                              Settlement      평가 가능 상태
    │                              Created         활성화
    │                                    │
    │                                    ▼
    │                              SettlementCompleted
    │
    └── 입찰 없음 ──► AuctionFailed (종료)
```

---

## 6. 컨텍스트 간 통합 패턴

| 발행 컨텍스트 | 이벤트 | 구독 컨텍스트 | 처리 |
|---------------|--------|---------------|------|
| 경매 | AuctionAwarded | 결제 | Payment 생성 (PENDING) |
| 경매 | AuctionAwarded | 상품 | Product 상태를 SOLD로 변경 |
| 결제 | PaymentCompleted | 배송 | Shipment 생성 (AWAITING_SHIPMENT) |
| 배송 | ReceiptConfirmed | 결제 | Settlement 생성 및 정산 실행 |
| 배송 | ReceiptConfirmed | 평가 | Review 작성 가능 상태 활성화 |
| 평가 | ReviewWritten | 회원 | Member의 평균 평점 갱신 |

---

## 7. 주요 설계 결정 사항

### Auction 애그리거트에 Bid를 포함시킨 이유
- 입찰 시 "현재 최고가보다 높아야 한다"는 불변식을 보호하려면 Auction이 Bid 목록을 직접 관리해야 한다.
- Bid를 별도 애그리거트로 분리하면 동시 입찰 시 불변식이 깨질 수 있다.
- 트랜잭션 경계 안에서 일관성을 보장한다.

### Payment와 Settlement를 분리한 이유
- 결제(구매자가 돈을 냄)와 정산(판매자에게 돈이 감)은 시점이 다르다.
- 결제는 낙찰 직후, 정산은 거래 확정(수령 확정) 후에 발생한다.
- 각각의 생명주기와 상태 전이가 독립적이다.

### 경매 종료 처리
- 스케줄러가 endTime에 도달한 Auction을 조회하여 `close()`를 호출한다.
- `close()` 내부에서 낙찰/유찰을 결정하고 해당 도메인 이벤트를 발행한다.

### 평가 시점 제한
- ReceiptConfirmed 이벤트 이후에만 평가가 가능하도록 하여, 실제 거래가 완료된 건에 대해서만 평가할 수 있도록 한다.
