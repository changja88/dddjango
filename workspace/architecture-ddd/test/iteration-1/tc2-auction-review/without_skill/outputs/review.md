# 온라인 경매 시스템 도메인 모델 DDD 리뷰

## 1. Aggregate 설계 문제

### 1.1 God Aggregate — Auction이 모든 것을 품고 있다

`Auction` 클래스가 경매 자체의 책임뿐 아니라 결제(`payment`), 배송(`shipping`), 리뷰(`reviews`)까지 직접 참조하고 있다. DDD에서 Aggregate는 트랜잭션 일관성 경계를 정의하는데, 하나의 Aggregate에 너무 많은 개념을 넣으면 다음 문제가 발생한다:

- **동시성 충돌 증가**: 입찰, 결제, 배송, 리뷰가 모두 같은 Aggregate를 수정하므로 락 경합이 심해진다.
- **변경 이유가 너무 많다**: 결제 로직 변경, 배송 정책 변경, 리뷰 정책 변경 모두가 Auction에 영향을 준다.

**개선 방향**: 최소 4개의 독립 Aggregate로 분리해야 한다.

| Aggregate | 포함 개념 |
|-----------|-----------|
| Auction | id, seller, item, start_price, end_time, bids, status, winning_bid |
| Payment | buyer, seller, amount, auction_id (참조만) |
| Shipping | sender, receiver, item, auction_id (참조만) |
| Review | reviewer, auction_id (참조만), rating, comment |

## 2. 도메인 로직의 위치 문제 — Anemic Domain Model

### 2.1 핵심 비즈니스 규칙이 Service에 있다

`place_bid`의 입찰 유효성 검증, `close_auction`의 낙찰자 결정 로직이 모두 `AuctionService`에 있다. Auction 엔티티 자체는 데이터만 들고 있는 빈혈 모델(Anemic Domain Model)이다.

DDD에서 도메인 규칙은 Aggregate Root에 있어야 한다:

```python
# 개선: 도메인 로직을 Aggregate Root 내부로 이동
class Auction:
    def place_bid(self, bidder, amount):
        self._ensure_active()
        self._validate_bid_amount(amount)
        bid = Bid(bidder=bidder, amount=amount)
        self.bids.append(bid)
        self._raise_event(BidPlaced(auction_id=self.id, bid=bid))

    def close(self):
        self._ensure_has_bids()
        self.status = AuctionStatus.CLOSED
        self.winning_bid = max(self.bids, key=lambda b: b.amount)
        self._raise_event(AuctionClosed(auction_id=self.id, winning_bid=self.winning_bid))
```

### 2.2 update_status는 캡슐화 파괴

`update_status` 메서드는 외부에서 아무 상태로나 변경할 수 있게 허용한다. 이는 도메인 불변식(invariant)을 무력화한다. 상태 전이는 의미 있는 도메인 행위(`open`, `close`, `cancel`)로 표현해야 한다.

```python
# 나쁜 예
service.update_status(auction, "closed")

# 좋은 예
auction.close()
auction.cancel(reason="seller_request")
```

## 3. Value Object 부재

### 3.1 Primitive Obsession

`start_price`가 단순 숫자, `status`가 문자열로 되어 있다. 이들은 Value Object로 모델링해야 한다:

- **Money**: 금액 + 통화를 함께 다루는 Value Object. `amount=10000`만으로는 원화인지 달러인지 알 수 없다.
- **AuctionStatus**: 문자열 대신 Enum 또는 상태 머신으로 유효한 전이만 허용해야 한다.
- **BidAmount**: 최소 입찰 단위, 최대 입찰 한도 등의 규칙을 캡슐화할 수 있다.

```python
class Money:
    def __init__(self, amount: Decimal, currency: str = "KRW"):
        if amount < 0:
            raise ValueError("금액은 음수일 수 없습니다")
        self.amount = amount
        self.currency = currency

class AuctionStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"
```

## 4. Bounded Context 미분리

현재 코드는 경매, 결제, 배송, 리뷰가 하나의 모듈에 섞여 있다. DDD 관점에서 이들은 서로 다른 Bounded Context에 속한다:

| Bounded Context | 핵심 개념 | 유비쿼터스 언어 |
|----------------|-----------|----------------|
| **Bidding** (경매/입찰) | Auction, Bid, Bidder | 입찰, 낙찰, 시작가, 현재가 |
| **Payment** (결제) | Payment, Invoice, Refund | 결제, 정산, 환불 |
| **Fulfillment** (배송) | Shipment, Tracking, Delivery | 발송, 배송추적, 수령확인 |
| **Feedback** (리뷰) | Review, Rating | 평점, 후기 |

컨텍스트 간 통신은 도메인 이벤트를 통해 느슨하게 결합해야 한다:

```
AuctionClosed 이벤트 발행
  -> Payment Context가 구독하여 결제 생성
  -> Fulfillment Context가 구독하여 배송 준비
```

## 5. 도메인 이벤트 부재

`close_auction`에서 결제 생성과 배송 생성을 직접 호출(동기적 절차적 코드)하고 있다. 이는 다음 문제를 일으킨다:

- **강결합**: Auction이 Payment, Shipping의 생성 방법을 알아야 한다.
- **트랜잭션 범위 과대**: 경매 종료, 결제 생성, 배송 생성이 하나의 트랜잭션에 묶인다. 결제 실패 시 경매 종료까지 롤백된다.
- **확장성 저하**: 낙찰 시 알림 발송, 수수료 정산 등 새로운 후속 처리를 추가하려면 `close_auction`을 계속 수정해야 한다.

**개선 방향**: `AuctionClosed` 도메인 이벤트를 발행하고, 각 Bounded Context가 이를 구독하여 독립적으로 처리한다.

## 6. 불변식(Invariant) 보호 미흡

### 6.1 누락된 검증

- 입찰자가 판매자 본인인 경우를 차단하지 않는다.
- `end_time` 이후 입찰이 가능한지 시간 검증이 없다.
- 입찰이 없는 경매의 `close_auction` 호출 시 `max()`가 빈 시퀀스에서 실패한다.
- `start_price` 음수 검증이 없다.

### 6.2 상태 전이 규칙 부재

"closed" 상태에서 다시 "active"로 되돌아갈 수 있는지, "cancelled" 상태에서 입찰이 가능한지 등의 규칙이 전혀 없다. `update_status`가 아무 문자열이나 받으므로 `auction.status = "asdf"`도 가능하다.

## 7. 종합 요약

| 항목 | 현재 상태 | 심각도 |
|------|----------|--------|
| Aggregate 경계 | 단일 God Aggregate | 높음 |
| 도메인 모델 | Anemic Domain Model | 높음 |
| Bounded Context | 미분리 (모노리스) | 높음 |
| Value Object | Primitive Obsession | 중간 |
| 도메인 이벤트 | 부재 (동기 절차적 코드) | 높음 |
| 불변식 보호 | 다수 누락 | 중간 |
| 상태 관리 | 문자열 기반, 전이 규칙 없음 | 중간 |

가장 시급한 개선 순서:
1. Aggregate 분리 (Auction에서 Payment, Shipping, Review 제거)
2. 도메인 로직을 Auction Aggregate Root 내부로 이동
3. 도메인 이벤트 도입으로 Bounded Context 간 결합도 제거
4. Value Object 도입 (Money, AuctionStatus 등)
5. 불변식 검증 강화
