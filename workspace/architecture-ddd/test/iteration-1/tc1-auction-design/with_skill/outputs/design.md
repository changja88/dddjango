# 온라인 경매 시스템 DDD 설계

## 1. 전략 설계

### 1.1 하위 도메인 분류

| 하위 도메인 | 유형 | 설명 | 솔루션 전략 |
|------------|------|------|------------|
| 경매(Auction) | 핵심(Core) | 상품 등록, 입찰, 낙찰 판정 -- 시스템의 경쟁 우위 원천 | 사내 구현, 정교한 도메인 모델 |
| 결제(Payment) | 일반(Generic) | 낙찰 후 결제 생성 및 정산 처리 | 외부 PG 연동, ACL로 격리 |
| 배송(Delivery) | 지원(Supporting) | 낙찰 상품의 배송 추적 및 수령 확인 | 단순 상태 머신, CRUD 수준 |
| 평가(Review) | 지원(Supporting) | 거래 완료 후 구매자-판매자 간 상호 평가 | 단순 CRUD |
| 회원(Identity) | 일반(Generic) | 사용자 인증, 프로필 관리 | 외부 솔루션 또는 표준 구현 |

> 핵심 도메인은 **경매**다. 입찰 규칙, 경매 종료 판정, 낙찰 결정 로직이 이 시스템의 차별적 가치이므로, 최고 수준의 설계와 투자를 집중한다.

### 1.2 바운디드 컨텍스트 정의

같은 용어가 다른 의미로 쓰이는 지점을 기준으로 경계를 분리한다.

| 바운디드 컨텍스트 | 포함 하위 도메인 | 유비쿼터스 언어의 핵심 용어 |
|-----------------|----------------|------------------------|
| **경매 컨텍스트** (Auction Context) | 경매 | 경매(Auction), 입찰(Bid), 낙찰(Winning), 시작가(StartingPrice), 상품(Item) |
| **결제 컨텍스트** (Payment Context) | 결제 | 결제(Payment), 정산(Settlement), 결제금액(PaymentAmount) |
| **배송 컨텍스트** (Delivery Context) | 배송 | 배송(Shipment), 발송(Dispatch), 수령확인(ReceiptConfirmation) |
| **평가 컨텍스트** (Review Context) | 평가 | 평가(Review), 평점(Rating), 거래평가(TransactionReview) |
| **회원 컨텍스트** (Identity Context) | 회원 | 회원(Member), 판매자(Seller), 구매자(Buyer) |

**용어 분리 예시 -- "사용자"가 컨텍스트마다 다른 의미:**
- 경매 컨텍스트: **판매자**(Seller)는 상품을 등록하고 경매를 시작하는 주체, **입찰자**(Bidder)는 입찰하는 주체
- 결제 컨텍스트: **지불자**(Payer)는 결제하는 주체, **수취인**(Payee)는 정산받는 주체
- 배송 컨텍스트: **발송인**(Sender), **수령인**(Recipient)
- 평가 컨텍스트: **평가자**(Reviewer), **피평가자**(Reviewee)

### 1.3 컨텍스트 맵

```
[회원 컨텍스트]
    |
    | OHS/Published Language (회원 ID, 기본 프로필)
    |
    v
[경매 컨텍스트] -----> [결제 컨텍스트]
  (Core)          |      (Generic)
    |             |         |
    |             |    ACL (PG사 외부 시스템)
    |             |
    |             +---> [배송 컨텍스트]
    |                    (Supporting)
    |                        |
    +------------------------+-----> [평가 컨텍스트]
                                      (Supporting)
```

**컨텍스트 간 관계:**

| 업스트림 | 다운스트림 | 관계 패턴 | 설명 |
|---------|----------|----------|------|
| 경매 | 결제 | 고객-공급자 + 도메인 이벤트 | 낙찰 이벤트가 결제 생성을 트리거 |
| 경매 | 배송 | 고객-공급자 + 도메인 이벤트 | 결제 완료 이벤트가 배송 준비를 트리거 |
| 배송 | 경매 | 도메인 이벤트 | 수령 확인 이벤트가 거래 확정을 트리거 |
| 경매 | 평가 | 고객-공급자 + 도메인 이벤트 | 거래 확정 이벤트가 평가 가능 상태를 트리거 |
| 결제 | 외부 PG | ACL(충돌 방지 계층) | PG사 모델 오염을 차단 |
| 회원 | 경매/결제/배송/평가 | OHS + Published Language | 회원 ID를 통한 느슨한 연결 |

---

## 2. 유비쿼터스 언어 사전

경매 컨텍스트(핵심 도메인)의 유비쿼터스 언어를 정의한다. 코드의 클래스명과 메서드명은 이 용어를 그대로 반영해야 한다.

| 용어 (한국어) | 용어 (영어) | 정의 |
|-------------|-----------|------|
| 경매 | Auction | 판매자가 등록한 상품에 대해 정해진 기간 동안 입찰을 받는 판매 방식 |
| 상품 | Item | 경매에 출품되는 물건. 이름, 설명, 시작가를 포함 |
| 시작가 | StartingPrice | 경매의 최소 입찰 가능 금액 |
| 입찰 | Bid | 구매자가 특정 경매에 제시하는 금액 |
| 입찰자 | Bidder | 입찰을 하는 구매자 |
| 최고입찰 | HighestBid | 현재 경매에서 가장 높은 입찰 |
| 낙찰 | Winning | 경매 종료 시 최고입찰자가 상품을 획득하는 것 |
| 낙찰자 | Winner | 경매에서 최고입찰을 한 구매자 |
| 경매 시작 | open | 판매자가 경매를 시작하는 행위 |
| 입찰하다 | placeBid | 입찰자가 금액을 제시하는 행위 |
| 경매 종료 | close | 종료 시간 도달로 경매가 마감되는 것 |
| 거래 확정 | confirmTransaction | 구매자가 상품 수령 후 거래를 최종 확정하는 행위 |

---

## 3. 전술 설계 -- 애그리거트, 엔티티, 값 객체, 도메인 이벤트

### 3.1 경매 컨텍스트 (핵심 도메인)

#### 애그리거트: Auction (경매)

Auction이 애그리거트 루트이며, Bid(입찰)는 Auction 내부의 값 객체 컬렉션이다. 입찰 금액이 현재 최고 입찰가보다 높아야 한다는 불변식은 반드시 Auction 애그리거트 내부에서 보호되어야 한다.

> **Vernon 규칙 1 적용:** "입찰 금액 > 현재 최고 입찰가"라는 불변식이 Auction 애그리거트의 일관성 경계를 결정한다.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4


# --- 값 객체 ---

@dataclass(frozen=True)
class Money:
    """금액 값 객체"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def is_greater_than(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount > other.amount

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")


@dataclass(frozen=True)
class Bid:
    """입찰 값 객체 -- 한번 생성되면 변경되지 않는다"""
    bidder_id: str
    amount: Money
    placed_at: datetime


@dataclass(frozen=True)
class AuctionItem:
    """경매 상품 값 객체"""
    name: str
    description: str
    starting_price: Money


class AuctionStatus(Enum):
    DRAFT = "draft"             # 상품 등록 완료, 경매 시작 전
    OPEN = "open"               # 경매 진행 중
    CLOSED = "closed"           # 경매 종료 (낙찰자 결정됨)
    CANCELLED = "cancelled"     # 경매 취소
    COMPLETED = "completed"     # 거래 확정 완료


# --- 도메인 이벤트 ---

@dataclass(frozen=True)
class AuctionOpened:
    auction_id: str
    seller_id: str
    starting_price: Money
    end_time: datetime
    occurred_at: datetime

@dataclass(frozen=True)
class BidPlaced:
    auction_id: str
    bidder_id: str
    bid_amount: Money
    occurred_at: datetime

@dataclass(frozen=True)
class AuctionClosed:
    """경매 종료 -- 낙찰자가 있는 경우와 없는 경우를 구분"""
    auction_id: str
    winner_id: Optional[str]
    winning_amount: Optional[Money]
    seller_id: str
    occurred_at: datetime

@dataclass(frozen=True)
class TransactionConfirmed:
    """거래 확정 -- 구매자가 수령 확인"""
    auction_id: str
    winner_id: str
    seller_id: str
    final_amount: Money
    occurred_at: datetime


# --- 애그리거트 루트 ---

@dataclass
class Auction:
    """경매 애그리거트 루트

    불변식:
    - 입찰 금액은 현재 최고 입찰가보다 높아야 한다
    - 경매가 OPEN 상태일 때만 입찰할 수 있다
    - 경매 종료 시간이 지나면 더 이상 입찰할 수 없다
    - 판매자는 자신의 경매에 입찰할 수 없다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    seller_id: str = ""                     # 회원 컨텍스트를 ID로 참조
    item: AuctionItem = None
    end_time: datetime = None
    _status: AuctionStatus = field(default=AuctionStatus.DRAFT)
    _bids: List[Bid] = field(default_factory=list)
    _winner_id: Optional[str] = None
    _events: List = field(default_factory=list)

    def open(self, end_time: datetime) -> None:
        """경매를 시작한다"""
        if self._status != AuctionStatus.DRAFT:
            raise ValueError("초안 상태에서만 경매를 시작할 수 있습니다")
        if self.item is None:
            raise ValueError("상품 정보가 등록되어야 합니다")
        if end_time <= datetime.now():
            raise ValueError("종료 시간은 현재 시간 이후여야 합니다")

        self.end_time = end_time
        self._status = AuctionStatus.OPEN
        self._events.append(AuctionOpened(
            auction_id=self.id,
            seller_id=self.seller_id,
            starting_price=self.item.starting_price,
            end_time=end_time,
            occurred_at=datetime.now(),
        ))

    def place_bid(self, bidder_id: str, amount: Money) -> None:
        """입찰한다

        불변식 보호:
        - OPEN 상태인지 확인
        - 종료 시간 이전인지 확인
        - 판매자 자신이 아닌지 확인
        - 최고 입찰가보다 높은지 확인
        """
        if self._status != AuctionStatus.OPEN:
            raise ValueError("경매가 진행 중일 때만 입찰할 수 있습니다")
        if datetime.now() >= self.end_time:
            raise ValueError("경매 종료 시간이 지났습니다")
        if bidder_id == self.seller_id:
            raise ValueError("판매자는 자신의 경매에 입찰할 수 없습니다")

        current_minimum = self._current_minimum_bid()
        if not amount.is_greater_than(current_minimum):
            raise ValueError(
                f"입찰 금액({amount.amount})은 현재 최소 입찰가"
                f"({current_minimum.amount})보다 높아야 합니다"
            )

        bid = Bid(bidder_id=bidder_id, amount=amount, placed_at=datetime.now())
        self._bids.append(bid)
        self._events.append(BidPlaced(
            auction_id=self.id,
            bidder_id=bidder_id,
            bid_amount=amount,
            occurred_at=datetime.now(),
        ))

    def close(self) -> None:
        """경매를 종료한다 -- 최고 입찰자가 낙찰자가 된다"""
        if self._status != AuctionStatus.OPEN:
            raise ValueError("진행 중인 경매만 종료할 수 있습니다")

        self._status = AuctionStatus.CLOSED
        highest = self.highest_bid

        if highest is not None:
            self._winner_id = highest.bidder_id

        self._events.append(AuctionClosed(
            auction_id=self.id,
            winner_id=self._winner_id,
            winning_amount=highest.amount if highest else None,
            seller_id=self.seller_id,
            occurred_at=datetime.now(),
        ))

    def confirm_transaction(self, confirmer_id: str) -> None:
        """거래를 확정한다 -- 구매자가 수령 확인"""
        if self._status != AuctionStatus.CLOSED:
            raise ValueError("종료된 경매에서만 거래를 확정할 수 있습니다")
        if self._winner_id is None:
            raise ValueError("낙찰자가 없는 경매는 거래를 확정할 수 없습니다")
        if confirmer_id != self._winner_id:
            raise ValueError("낙찰자만 거래를 확정할 수 있습니다")

        self._status = AuctionStatus.COMPLETED
        self._events.append(TransactionConfirmed(
            auction_id=self.id,
            winner_id=self._winner_id,
            seller_id=self.seller_id,
            final_amount=self.highest_bid.amount,
            occurred_at=datetime.now(),
        ))

    @property
    def highest_bid(self) -> Optional[Bid]:
        if not self._bids:
            return None
        return max(self._bids, key=lambda b: b.amount.amount)

    @property
    def status(self) -> AuctionStatus:
        return self._status

    @property
    def winner_id(self) -> Optional[str]:
        return self._winner_id

    def _current_minimum_bid(self) -> Money:
        """현재 최소 입찰 가능 금액을 반환한다"""
        highest = self.highest_bid
        if highest is None:
            return self.item.starting_price
        return highest.amount

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events
```

> **Vernon 규칙 2 적용:** Auction 애그리거트는 루트 엔티티(Auction)와 값 객체들(Bid, AuctionItem, Money)로 구성된다. Bid를 별도 애그리거트로 분리하지 않는 이유는 "입찰 금액 > 최고 입찰가"라는 불변식이 Auction과 Bid 사이에서 반드시 동시에 검증되어야 하기 때문이다.

> **Vernon 규칙 3 적용:** seller_id, bidder_id로 회원 컨텍스트의 Member를 ID 참조한다. 직접 객체 참조를 사용하지 않는다.

> **Vernon 규칙 4 적용:** 경매 종료 후 결제 생성, 배송 준비, 평가 활성화는 모두 도메인 이벤트를 통한 결과적 일관성으로 처리한다.


### 3.2 결제 컨텍스트 (일반 도메인)

#### 애그리거트: Payment (결제)

```python
class PaymentStatus(Enum):
    PENDING = "pending"         # 결제 대기
    COMPLETED = "completed"     # 결제 완료
    FAILED = "failed"           # 결제 실패


@dataclass(frozen=True)
class PaymentCompleted:
    payment_id: str
    auction_id: str
    payer_id: str
    payee_id: str
    amount: Money
    occurred_at: datetime


@dataclass(frozen=True)
class SettlementProcessed:
    """정산 완료 이벤트"""
    payment_id: str
    payee_id: str
    amount: Money
    occurred_at: datetime


@dataclass
class Payment:
    """결제 애그리거트

    AuctionClosed 이벤트에 의해 생성된다.
    결제 완료 시 PaymentCompleted 이벤트를 발행한다.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    auction_id: str = ""        # 경매 컨텍스트를 ID로 참조
    payer_id: str = ""          # 낙찰자 (회원 ID 참조)
    payee_id: str = ""          # 판매자 (회원 ID 참조)
    amount: Money = None
    _status: PaymentStatus = field(default=PaymentStatus.PENDING)
    _events: List = field(default_factory=list)

    def complete(self) -> None:
        """결제를 완료한다"""
        if self._status != PaymentStatus.PENDING:
            raise ValueError("대기 상태의 결제만 완료할 수 있습니다")
        self._status = PaymentStatus.COMPLETED
        self._events.append(PaymentCompleted(
            payment_id=self.id,
            auction_id=self.auction_id,
            payer_id=self.payer_id,
            payee_id=self.payee_id,
            amount=self.amount,
            occurred_at=datetime.now(),
        ))

    def fail(self) -> None:
        if self._status != PaymentStatus.PENDING:
            raise ValueError("대기 상태의 결제만 실패 처리할 수 있습니다")
        self._status = PaymentStatus.FAILED

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events
```

#### 애그리거트: Settlement (정산)

정산은 결제와 별도의 애그리거트다. 거래 확정(TransactionConfirmed) 이벤트를 수신한 후 판매자에게 정산을 진행한다.

```python
class SettlementStatus(Enum):
    PENDING = "pending"
    PROCESSED = "processed"


@dataclass
class Settlement:
    """정산 애그리거트

    TransactionConfirmed 이벤트에 의해 생성된다.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    payment_id: str = ""        # Payment를 ID로 참조
    payee_id: str = ""          # 판매자 (회원 ID 참조)
    amount: Money = None
    _status: SettlementStatus = field(default=SettlementStatus.PENDING)
    _events: List = field(default_factory=list)

    def process(self) -> None:
        """정산을 처리한다"""
        if self._status != SettlementStatus.PENDING:
            raise ValueError("대기 상태의 정산만 처리할 수 있습니다")
        self._status = SettlementStatus.PROCESSED
        self._events.append(SettlementProcessed(
            payment_id=self.payment_id,
            payee_id=self.payee_id,
            amount=self.amount,
            occurred_at=datetime.now(),
        ))

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events
```


### 3.3 배송 컨텍스트 (지원 도메인)

#### 애그리거트: Shipment (배송)

```python
class ShipmentStatus(Enum):
    PENDING = "pending"           # 배송 준비 대기
    DISPATCHED = "dispatched"     # 발송 완료
    DELIVERED = "delivered"       # 배달 완료
    RECEIPT_CONFIRMED = "receipt_confirmed"  # 수령 확인


@dataclass(frozen=True)
class ShipmentDispatched:
    shipment_id: str
    auction_id: str
    sender_id: str
    occurred_at: datetime

@dataclass(frozen=True)
class ReceiptConfirmed:
    shipment_id: str
    auction_id: str
    recipient_id: str
    occurred_at: datetime


@dataclass
class Shipment:
    """배송 애그리거트

    PaymentCompleted 이벤트에 의해 생성된다.
    판매자가 발송하고, 구매자가 수령을 확인한다.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    auction_id: str = ""         # 경매 컨텍스트를 ID로 참조
    sender_id: str = ""          # 판매자 (회원 ID 참조)
    recipient_id: str = ""       # 낙찰자 (회원 ID 참조)
    _status: ShipmentStatus = field(default=ShipmentStatus.PENDING)
    _events: List = field(default_factory=list)

    def dispatch(self) -> None:
        """판매자가 상품을 발송한다"""
        if self._status != ShipmentStatus.PENDING:
            raise ValueError("준비 대기 상태에서만 발송할 수 있습니다")
        self._status = ShipmentStatus.DISPATCHED
        self._events.append(ShipmentDispatched(
            shipment_id=self.id,
            auction_id=self.auction_id,
            sender_id=self.sender_id,
            occurred_at=datetime.now(),
        ))

    def mark_delivered(self) -> None:
        """배달 완료로 표시한다"""
        if self._status != ShipmentStatus.DISPATCHED:
            raise ValueError("발송 완료 상태에서만 배달 완료 처리할 수 있습니다")
        self._status = ShipmentStatus.DELIVERED

    def confirm_receipt(self, confirmer_id: str) -> None:
        """구매자가 수령을 확인한다"""
        if self._status != ShipmentStatus.DELIVERED:
            raise ValueError("배달 완료 상태에서만 수령 확인할 수 있습니다")
        if confirmer_id != self.recipient_id:
            raise ValueError("수령인만 수령을 확인할 수 있습니다")
        self._status = ShipmentStatus.RECEIPT_CONFIRMED
        self._events.append(ReceiptConfirmed(
            shipment_id=self.id,
            auction_id=self.auction_id,
            recipient_id=self.recipient_id,
            occurred_at=datetime.now(),
        ))

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events
```


### 3.4 평가 컨텍스트 (지원 도메인)

#### 애그리거트: TransactionReview (거래 평가)

구매자와 판매자가 각각 독립적으로 평가를 작성하므로, 각 평가는 별도의 애그리거트 인스턴스다.

```python
class ReviewRole(Enum):
    BUYER_TO_SELLER = "buyer_to_seller"     # 구매자가 판매자를 평가
    SELLER_TO_BUYER = "seller_to_buyer"     # 판매자가 구매자를 평가


@dataclass(frozen=True)
class Rating:
    """평점 값 객체"""
    score: int

    def __post_init__(self) -> None:
        if not (1 <= self.score <= 5):
            raise ValueError(f"평점은 1~5 사이여야 합니다: {self.score}")


@dataclass(frozen=True)
class ReviewSubmitted:
    review_id: str
    auction_id: str
    reviewer_id: str
    reviewee_id: str
    role: ReviewRole
    rating: Rating
    occurred_at: datetime


@dataclass
class TransactionReview:
    """거래 평가 애그리거트

    TransactionConfirmed 이벤트에 의해 평가 가능 상태가 된다.
    구매자와 판매자가 각각 하나씩 생성한다.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    auction_id: str = ""         # 경매 컨텍스트를 ID로 참조
    reviewer_id: str = ""        # 평가자 (회원 ID 참조)
    reviewee_id: str = ""        # 피평가자 (회원 ID 참조)
    role: ReviewRole = None
    _rating: Optional[Rating] = None
    _comment: str = ""
    _is_submitted: bool = False
    _events: List = field(default_factory=list)

    def submit(self, rating: Rating, comment: str) -> None:
        """평가를 제출한다"""
        if self._is_submitted:
            raise ValueError("이미 제출된 평가입니다")
        self._rating = rating
        self._comment = comment
        self._is_submitted = True
        self._events.append(ReviewSubmitted(
            review_id=self.id,
            auction_id=self.auction_id,
            reviewer_id=self.reviewer_id,
            reviewee_id=self.reviewee_id,
            role=self.role,
            rating=rating,
            occurred_at=datetime.now(),
        ))

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events
```

---

## 4. 도메인 이벤트 흐름

비즈니스 프로세스 전체를 관통하는 이벤트 흐름이다. 각 컨텍스트 간 결과적 일관성(Vernon 규칙 4)으로 연결된다.

```
[판매자] 상품 등록 + 경매 시작
    |
    v
AuctionOpened -----> (경매 컨텍스트 내부)
    |
[입찰자] 입찰
    |
    v
BidPlaced ---------> (경매 컨텍스트 내부)
    |
[스케줄러] 경매 종료 시간 도달
    |
    v
AuctionClosed -----> [결제 컨텍스트] Payment 자동 생성
                          |
                     [낙찰자] 결제 완료
                          |
                          v
                     PaymentCompleted --> [배송 컨텍스트] Shipment 생성
                                              |
                                         [판매자] 발송
                                              |
                                              v
                                         ShipmentDispatched
                                              |
                                         [배달 완료]
                                              |
                                         [낙찰자] 수령 확인
                                              |
                                              v
                                         ReceiptConfirmed --> [경매 컨텍스트] 거래 확정
                                                                   |
                                                                   v
                                                              TransactionConfirmed
                                                                   |
                                                        +----------+----------+
                                                        |                     |
                                                        v                     v
                                                   [결제 컨텍스트]       [평가 컨텍스트]
                                                   Settlement 생성    TransactionReview
                                                   정산 처리           평가 가능 활성화
```

### 이벤트 요약표

| 도메인 이벤트 | 발행 컨텍스트 | 구독 컨텍스트 | 트리거하는 행동 |
|-------------|-------------|-------------|--------------|
| AuctionOpened | 경매 | -- | 경매 목록에 노출 |
| BidPlaced | 경매 | -- | 입찰 알림 발송 (알림은 별도 일반 도메인) |
| AuctionClosed | 경매 | 결제 | 낙찰자가 있으면 Payment 자동 생성 |
| PaymentCompleted | 결제 | 배송 | Shipment 생성 (배송 준비 대기) |
| ShipmentDispatched | 배송 | -- | 구매자에게 발송 알림 |
| ReceiptConfirmed | 배송 | 경매 | Auction.confirmTransaction() 호출 |
| TransactionConfirmed | 경매 | 결제, 평가 | Settlement 생성 + 정산 처리, TransactionReview 생성 |
| SettlementProcessed | 결제 | -- | 판매자에게 정산 완료 알림 |
| ReviewSubmitted | 평가 | -- | 피평가자 평점 갱신 |

---

## 5. 애그리거트 설계 요약

| 바운디드 컨텍스트 | 애그리거트 | 루트 엔티티 | 내부 값 객체 | 참조하는 외부 애그리거트 (ID 참조) |
|-----------------|----------|-----------|------------|-------------------------------|
| 경매 | Auction | Auction | Bid, AuctionItem, Money, AuctionStatus | seller_id, bidder_id (회원) |
| 결제 | Payment | Payment | Money, PaymentStatus | auction_id (경매), payer_id, payee_id (회원) |
| 결제 | Settlement | Settlement | Money, SettlementStatus | payment_id (결제), payee_id (회원) |
| 배송 | Shipment | Shipment | ShipmentStatus | auction_id (경매), sender_id, recipient_id (회원) |
| 평가 | TransactionReview | TransactionReview | Rating, ReviewRole | auction_id (경매), reviewer_id, reviewee_id (회원) |

---

## 6. 리포지토리 인터페이스

리포지토리는 애그리거트 단위로 제공한다. Bid, AuctionItem 등 내부 값 객체를 위한 별도 리포지토리는 만들지 않는다.

```python
from abc import ABC, abstractmethod
from typing import Optional, List


class AuctionRepository(ABC):
    """경매 애그리거트 리포지토리 인터페이스"""

    @abstractmethod
    def find_by_id(self, auction_id: str) -> Optional[Auction]:
        ...

    @abstractmethod
    def save(self, auction: Auction) -> None:
        ...

    @abstractmethod
    def find_open_auctions_past_end_time(self, now: datetime) -> List[Auction]:
        """종료 시간이 지난 진행 중 경매를 조회한다 (스케줄러용)"""
        ...


class PaymentRepository(ABC):
    @abstractmethod
    def find_by_id(self, payment_id: str) -> Optional[Payment]:
        ...

    @abstractmethod
    def save(self, payment: Payment) -> None:
        ...


class SettlementRepository(ABC):
    @abstractmethod
    def find_by_id(self, settlement_id: str) -> Optional[Settlement]:
        ...

    @abstractmethod
    def save(self, settlement: Settlement) -> None:
        ...


class ShipmentRepository(ABC):
    @abstractmethod
    def find_by_id(self, shipment_id: str) -> Optional[Shipment]:
        ...

    @abstractmethod
    def find_by_auction_id(self, auction_id: str) -> Optional[Shipment]:
        ...

    @abstractmethod
    def save(self, shipment: Shipment) -> None:
        ...


class TransactionReviewRepository(ABC):
    @abstractmethod
    def find_by_id(self, review_id: str) -> Optional[TransactionReview]:
        ...

    @abstractmethod
    def save(self, review: TransactionReview) -> None:
        ...
```

---

## 7. 이벤트 핸들러 -- 결과적 일관성 구현

각 이벤트 핸들러는 별도 트랜잭션에서 실행되며, 컨텍스트 간 결과적 일관성을 구현한다.

```python
class AuctionClosedHandler:
    """AuctionClosed -> Payment 생성"""

    def __init__(self, payment_repo: PaymentRepository):
        self._payment_repo = payment_repo

    def handle(self, event: AuctionClosed) -> None:
        if event.winner_id is None:
            return  # 낙찰자가 없으면 결제를 생성하지 않는다

        payment = Payment(
            auction_id=event.auction_id,
            payer_id=event.winner_id,
            payee_id=event.seller_id,
            amount=event.winning_amount,
        )
        self._payment_repo.save(payment)


class PaymentCompletedHandler:
    """PaymentCompleted -> Shipment 생성"""

    def __init__(self, shipment_repo: ShipmentRepository):
        self._shipment_repo = shipment_repo

    def handle(self, event: PaymentCompleted) -> None:
        shipment = Shipment(
            auction_id=event.auction_id,
            sender_id=event.payee_id,       # 판매자 = 발송인
            recipient_id=event.payer_id,     # 낙찰자 = 수령인
        )
        self._shipment_repo.save(shipment)


class ReceiptConfirmedHandler:
    """ReceiptConfirmed -> Auction 거래 확정"""

    def __init__(self, auction_repo: AuctionRepository):
        self._auction_repo = auction_repo

    def handle(self, event: ReceiptConfirmed) -> None:
        auction = self._auction_repo.find_by_id(event.auction_id)
        auction.confirm_transaction(event.recipient_id)
        self._auction_repo.save(auction)


class TransactionConfirmedHandler:
    """TransactionConfirmed -> Settlement 생성 + TransactionReview 생성"""

    def __init__(
        self,
        settlement_repo: SettlementRepository,
        review_repo: TransactionReviewRepository,
        payment_repo: PaymentRepository,
    ):
        self._settlement_repo = settlement_repo
        self._review_repo = review_repo
        self._payment_repo = payment_repo

    def handle(self, event: TransactionConfirmed) -> None:
        # 정산 생성
        payment = self._payment_repo.find_by_auction_id(event.auction_id)
        settlement = Settlement(
            payment_id=payment.id,
            payee_id=event.seller_id,
            amount=event.final_amount,
        )
        self._settlement_repo.save(settlement)
        settlement.process()
        self._settlement_repo.save(settlement)

        # 양방향 평가 생성 (구매자->판매자, 판매자->구매자)
        buyer_review = TransactionReview(
            auction_id=event.auction_id,
            reviewer_id=event.winner_id,
            reviewee_id=event.seller_id,
            role=ReviewRole.BUYER_TO_SELLER,
        )
        seller_review = TransactionReview(
            auction_id=event.auction_id,
            reviewer_id=event.seller_id,
            reviewee_id=event.winner_id,
            role=ReviewRole.SELLER_TO_BUYER,
        )
        self._review_repo.save(buyer_review)
        self._review_repo.save(seller_review)
```

---

## 8. 설계 결정 근거 요약

| 설계 결정 | 적용 원칙 | 근거 |
|----------|----------|------|
| 전략 설계(바운디드 컨텍스트)를 먼저 정의 | 전략 설계 우선 원칙 (Vernon) | 잘못된 경계에서 좋은 전술 패턴을 적용해도 복잡성이 해결되지 않는다 |
| Bid를 Auction 내부 값 객체로 배치 | Vernon 규칙 1 (불변식 = 일관성 경계) | "입찰 금액 > 최고 입찰가" 불변식을 단일 트랜잭션에서 보호 |
| Auction에 최소한의 구성요소만 포함 | Vernon 규칙 2 (작은 애그리거트) | Bid, AuctionItem, Money만 포함. 결제/배송/평가는 별도 애그리거트 |
| seller_id, bidder_id로 회원 참조 | Vernon 규칙 3 (ID 참조) | 컨텍스트 간 결합도를 낮추고 독립 배포 가능 |
| AuctionClosed -> Payment 생성을 이벤트로 처리 | Vernon 규칙 4 (결과적 일관성) | 경매 종료와 결제 생성은 다른 애그리거트이므로 별도 트랜잭션 |
| Settlement를 Payment와 별도 애그리거트로 분리 | Vernon 규칙 2 | 결제와 정산은 서로 다른 생명주기를 가진다 |
| `open()`, `place_bid()`, `close()` 등 비즈니스 의도를 드러내는 메서드명 | 유비쿼터스 언어 반영 | `updateStatus()`가 아닌 도메인 전문가의 용어를 사용 |
| 비즈니스 규칙을 Auction 엔티티 내부에 배치 | 풍부한 도메인 모델 | 빈혈 도메인 모델 안티패턴을 피하고, 불변식 보호 로직을 엔티티가 소유 |
