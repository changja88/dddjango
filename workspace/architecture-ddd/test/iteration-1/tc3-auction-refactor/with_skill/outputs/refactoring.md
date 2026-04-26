# 온라인 경매 시스템 DDD 리팩토링

## 리팩토링 체크리스트

- [x] 빈혈 도메인 모델 -> 풍부한 도메인 모델로 비즈니스 로직 이동
- [x] 원시 타입 -> 값 객체로 추출
- [x] 서비스의 비즈니스 로직 -> 엔티티/값 객체의 메서드로 이동
- [x] 동기 호출 -> 도메인 이벤트 + 결과적 일관성으로 변경
- [x] 직접 참조 -> ID 참조로 변경 (이미 ID 참조 사용 중, 유지)
- [x] 큰 애그리거트 -> 작은 애그리거트로 분리 (Bid를 Auction 내부 값 객체로 재정의)

---

## 1. 원시 타입을 값 객체로 추출

[Before]
```python
class Auction:
    def __init__(self, id, seller_id, item_name, start_price, end_time):
        self.id = id
        self.seller_id = seller_id
        self.item_name = item_name
        self.start_price = start_price
        self.end_time = end_time
        self.bids = []
        self.status = "active"

class Bid:
    def __init__(self, auction_id, bidder_id, amount, created_at):
        self.auction_id = auction_id
        self.bidder_id = bidder_id
        self.amount = amount
        self.created_at = created_at
```

[After]
```python
from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4


# --- 값 객체 ---

@dataclass(frozen=True)
class Money:
    """입찰 금액 값 객체 -- 불변, 자기 검증"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, int):
            object.__setattr__(self, "amount", int(self.amount))
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def is_higher_than(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount > other.amount

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")


class AuctionStatus(Enum):
    """경매 상태 값 객체 -- 문자열 대신 열거형으로 표현"""
    ACTIVE = "active"
    CLOSED = "closed"

    @property
    def is_active(self) -> bool:
        return self == AuctionStatus.ACTIVE


@dataclass(frozen=True)
class Bid:
    """입찰 값 객체 -- Auction 애그리거트 내부 구성요소

    Bid는 한번 생성되면 변경되지 않으며,
    속성의 조합(bidder_id + amount + bid_at)으로 동등성을 판단한다.
    별도의 생명주기가 없으므로 값 객체로 모델링한다.
    """
    bidder_id: str
    amount: Money
    bid_at: datetime
```

[Reason] 원시 타입 -> 값 객체 추출 -- `amount: int`를 `Money` 값 객체로, `status: str`을 `AuctionStatus` 열거형으로 추출했다. 값 객체는 자기 검증을 수행하여(Money의 `__post_init__`) 잘못된 값이 시스템에 진입하는 것을 원천 차단한다. `Bid`는 `auction_id`를 제거하고 Auction 애그리거트 내부의 불변 값 객체(`frozen=True`)로 재정의했다. Bid는 한번 생성되면 변경되지 않고, 별도 생명주기가 없으므로 엔티티가 아닌 값 객체가 적합하다.

---

## 2. 빈혈 도메인 모델을 풍부한 도메인 모델로 전환 + 도메인 이벤트 도입

[Before]
```python
class Auction:
    def __init__(self, id, seller_id, item_name, start_price, end_time):
        self.id = id
        self.seller_id = seller_id
        self.item_name = item_name
        self.start_price = start_price
        self.end_time = end_time
        self.bids = []
        self.status = "active"


class AuctionService:
    def __init__(self, auction_repo, payment_service, notification_service):
        self.auction_repo = auction_repo
        self.payment_service = payment_service
        self.notification_service = notification_service

    def place_bid(self, auction_id, bidder_id, amount):
        auction = self.auction_repo.find_by_id(auction_id)
        if auction.status != "active":
            raise ValueError("종료된 경매")
        if auction.end_time < datetime.now():
            raise ValueError("경매 시간 종료")
        current_max = max([b.amount for b in auction.bids], default=auction.start_price)
        if amount <= current_max:
            raise ValueError("현재가보다 높아야 합니다")
        bid = Bid(auction_id=auction_id, bidder_id=bidder_id, amount=amount, created_at=datetime.now())
        auction.bids.append(bid)
        self.auction_repo.save(auction)
        self.notification_service.notify_outbid(auction.bids[-2].bidder_id if len(auction.bids) > 1 else None)

    def close_auction(self, auction_id):
        auction = self.auction_repo.find_by_id(auction_id)
        auction.status = "closed"
        if auction.bids:
            winning_bid = max(auction.bids, key=lambda b: b.amount)
            self.payment_service.create_payment(winning_bid.bidder_id, auction.seller_id, winning_bid.amount)
        self.auction_repo.save(auction)
        self.notification_service.notify_auction_closed(auction_id)
```

[After]
```python
# --- 도메인 이벤트 ---

@dataclass(frozen=True)
class DomainEvent:
    """도메인 이벤트 기본 클래스"""
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class BidPlacedEvent(DomainEvent):
    """입찰 발생 이벤트"""
    auction_id: str = ""
    bidder_id: str = ""
    amount: int = 0
    previous_bidder_id: Optional[str] = None


@dataclass(frozen=True)
class AuctionClosedEvent(DomainEvent):
    """경매 종료 이벤트"""
    auction_id: str = ""
    seller_id: str = ""
    winning_bidder_id: Optional[str] = None
    winning_amount: Optional[int] = None


# --- 애그리거트 ---

@dataclass
class Auction:
    """경매 애그리거트 루트

    - 모든 입찰 관련 비즈니스 규칙을 내부에 캡슐화한다
    - Bid는 애그리거트 내부 값 객체로, 외부에서 직접 생성하지 않는다
    - Seller, Bidder는 ID로만 참조한다 (Vernon 규칙 3)
    - 부수 효과(알림, 결제)는 도메인 이벤트로 분리한다 (Vernon 규칙 4)
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    seller_id: str = ""
    item_name: str = ""
    _start_price: Money = field(default_factory=lambda: Money(0))
    _end_time: datetime = field(default_factory=datetime.now)
    _bids: List[Bid] = field(default_factory=list)
    _status: AuctionStatus = field(default=AuctionStatus.ACTIVE)
    _events: List[DomainEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.item_name:
            raise ValueError("경매 물품명은 필수입니다")
        if self._start_price.amount <= 0:
            raise ValueError("시작가는 0보다 커야 합니다")

    # --- 비즈니스 행위 ---

    def place_bid(self, bidder_id: str, amount: Money) -> None:
        """입찰한다 -- 모든 비즈니스 규칙이 애그리거트 안에 있다"""
        self._ensure_active()
        self._ensure_not_expired()
        self._ensure_not_self_bid(bidder_id)
        self._ensure_higher_than_current_price(amount)

        previous_bidder_id = self._highest_bidder_id
        bid = Bid(bidder_id=bidder_id, amount=amount, bid_at=datetime.now())
        self._bids.append(bid)

        self._raise_event(
            BidPlacedEvent(
                auction_id=self.id,
                bidder_id=bidder_id,
                amount=amount.amount,
                previous_bidder_id=previous_bidder_id,
            )
        )

    def close(self) -> None:
        """경매를 종료한다"""
        self._ensure_active()
        self._status = AuctionStatus.CLOSED

        winning_bid = self._winning_bid
        self._raise_event(
            AuctionClosedEvent(
                auction_id=self.id,
                seller_id=self.seller_id,
                winning_bidder_id=winning_bid.bidder_id if winning_bid else None,
                winning_amount=winning_bid.amount.amount if winning_bid else None,
            )
        )

    # --- 도메인 규칙 (의도를 드러내는 인터페이스) ---

    def _ensure_active(self) -> None:
        if not self._status.is_active:
            raise ValueError("종료된 경매입니다")

    def _ensure_not_expired(self) -> None:
        if self._end_time < datetime.now():
            raise ValueError("경매 시간이 종료되었습니다")

    def _ensure_not_self_bid(self, bidder_id: str) -> None:
        if bidder_id == self.seller_id:
            raise ValueError("판매자는 자신의 경매에 입찰할 수 없습니다")

    def _ensure_higher_than_current_price(self, amount: Money) -> None:
        if not amount.is_higher_than(self.current_price):
            raise ValueError(
                f"현재가({self.current_price.amount})보다 높아야 합니다"
            )

    # --- 조회 (부작용 없는 함수) ---

    @property
    def current_price(self) -> Money:
        """현재 최고 입찰가를 반환한다"""
        if not self._bids:
            return self._start_price
        return max(self._bids, key=lambda b: b.amount.amount).amount

    @property
    def _winning_bid(self) -> Optional[Bid]:
        if not self._bids:
            return None
        return max(self._bids, key=lambda b: b.amount.amount)

    @property
    def _highest_bidder_id(self) -> Optional[str]:
        winning = self._winning_bid
        return winning.bidder_id if winning else None

    @property
    def bid_count(self) -> int:
        return len(self._bids)

    # --- 이벤트 수집 ---

    def _raise_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect_domain_events(self) -> List[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events
```

[Reason] 빈혈 모델 -> 풍부한 모델 + 도메인 이벤트 -- `AuctionService`에 흩어져 있던 모든 비즈니스 로직(`place_bid`의 상태 검증, 금액 비교, `close_auction`의 낙찰자 결정)을 `Auction` 애그리거트 내부로 이동했다. 이것이 DDD의 핵심이다. Millett가 "가장 흔한 DDD 실패 사례"로 지적한 빈혈 도메인 모델에서는 비즈니스 규칙이 서비스에 분산되어 있어 도메인 지식이 코드에 드러나지 않는다. 풍부한 도메인 모델에서는 `_ensure_active()`, `_ensure_not_expired()`, `_ensure_higher_than_current_price()` 같은 메서드명이 비즈니스 규칙을 직접 표현한다(의도를 드러내는 인터페이스). 또한 `notification_service.notify_outbid()`와 `payment_service.create_payment()` 같은 외부 부수 효과 호출을 `BidPlacedEvent`, `AuctionClosedEvent` 도메인 이벤트로 대체하여, 애그리거트가 외부 의존성을 갖지 않도록 했다(Vernon 규칙 4: 결과적 일관성).

---

## 3. 서비스를 응용 서비스(조율자)로 변환

[Before]
```python
class AuctionService:
    def __init__(self, auction_repo, payment_service, notification_service):
        self.auction_repo = auction_repo
        self.payment_service = payment_service
        self.notification_service = notification_service

    def place_bid(self, auction_id, bidder_id, amount):
        auction = self.auction_repo.find_by_id(auction_id)
        if auction.status != "active":
            raise ValueError("종료된 경매")
        if auction.end_time < datetime.now():
            raise ValueError("경매 시간 종료")
        current_max = max([b.amount for b in auction.bids], default=auction.start_price)
        if amount <= current_max:
            raise ValueError("현재가보다 높아야 합니다")
        bid = Bid(auction_id=auction_id, bidder_id=bidder_id, amount=amount, created_at=datetime.now())
        auction.bids.append(bid)
        self.auction_repo.save(auction)
        self.notification_service.notify_outbid(auction.bids[-2].bidder_id if len(auction.bids) > 1 else None)

    def close_auction(self, auction_id):
        auction = self.auction_repo.find_by_id(auction_id)
        auction.status = "closed"
        if auction.bids:
            winning_bid = max(auction.bids, key=lambda b: b.amount)
            self.payment_service.create_payment(winning_bid.bidder_id, auction.seller_id, winning_bid.amount)
        self.auction_repo.save(auction)
        self.notification_service.notify_auction_closed(auction_id)
```

[After]
```python
from abc import ABC, abstractmethod


# --- 리포지토리 인터페이스 (도메인 영역) ---

class AuctionRepository(ABC):
    """경매 리포지토리 인터페이스 -- 애그리거트 단위로 제공"""

    @abstractmethod
    def find_by_id(self, auction_id: str) -> Optional[Auction]:
        ...

    @abstractmethod
    def save(self, auction: Auction) -> None:
        ...


# --- 응용 서비스 (유스케이스 조율) ---

class AuctionApplicationService:
    """경매 응용 서비스

    - 비즈니스 로직을 직접 구현하지 않는다
    - 애그리거트를 조회하고, 도메인 메서드를 호출하고, 저장한다
    - 트랜잭션을 관리한다
    """

    def __init__(self, auction_repo: AuctionRepository) -> None:
        self._auction_repo = auction_repo

    def place_bid(self, auction_id: str, bidder_id: str, amount: int) -> None:
        """입찰 유스케이스 -- 도메인 로직은 Auction에 위임"""
        auction = self._auction_repo.find_by_id(auction_id)
        if auction is None:
            raise ValueError("경매를 찾을 수 없습니다")

        auction.place_bid(bidder_id=bidder_id, amount=Money(amount))
        self._auction_repo.save(auction)
        # 도메인 이벤트는 UoW/인프라 계층에서 수집하여 디스패치

    def close_auction(self, auction_id: str) -> None:
        """경매 종료 유스케이스 -- 도메인 로직은 Auction에 위임"""
        auction = self._auction_repo.find_by_id(auction_id)
        if auction is None:
            raise ValueError("경매를 찾을 수 없습니다")

        auction.close()
        self._auction_repo.save(auction)
        # 도메인 이벤트는 UoW/인프라 계층에서 수집하여 디스패치


# --- 도메인 이벤트 핸들러 (결과적 일관성) ---

class BidPlacedEventHandler:
    """입찰 이벤트 핸들러 -- 별도 트랜잭션에서 알림 처리"""

    def __init__(self, notification_service) -> None:
        self._notification_service = notification_service

    def handle(self, event: BidPlacedEvent) -> None:
        if event.previous_bidder_id is not None:
            self._notification_service.notify_outbid(
                bidder_id=event.previous_bidder_id,
                auction_id=event.auction_id,
            )


class AuctionClosedEventHandler:
    """경매 종료 이벤트 핸들러 -- 별도 트랜잭션에서 결제/알림 처리"""

    def __init__(self, payment_service, notification_service) -> None:
        self._payment_service = payment_service
        self._notification_service = notification_service

    def handle(self, event: AuctionClosedEvent) -> None:
        if event.winning_bidder_id is not None:
            self._payment_service.create_payment(
                bidder_id=event.winning_bidder_id,
                seller_id=event.seller_id,
                amount=event.winning_amount,
            )
        self._notification_service.notify_auction_closed(
            auction_id=event.auction_id,
        )
```

[Reason] 응용 서비스 분리 + 결과적 일관성 -- 기존 `AuctionService`는 비즈니스 로직(검증, 상태 변경)과 인프라 호출(알림, 결제)을 모두 담당하는 Fat Service였다. 리팩토링 후 `AuctionApplicationService`는 순수한 조율자 역할만 수행한다: 리포지토리에서 애그리거트를 꺼내고, 도메인 메서드를 호출하고, 저장한다. `payment_service`와 `notification_service`에 대한 직접 호출은 도메인 이벤트 핸들러(`BidPlacedEventHandler`, `AuctionClosedEventHandler`)로 분리하여 결과적 일관성(Vernon 규칙 4)으로 처리한다. 이렇게 하면 Auction 애그리거트는 외부 서비스 의존성이 완전히 제거되어 순수한 도메인 로직만 남게 된다.

---

## 전체 구조 요약

```
Auction (애그리거트 루트)
  +-- Bid (값 객체, 내부 구성요소)
  +-- Money (값 객체)
  +-- AuctionStatus (값 객체, Enum)

도메인 이벤트
  +-- BidPlacedEvent
  +-- AuctionClosedEvent

응용 계층
  +-- AuctionApplicationService (조율자, 비즈니스 로직 없음)

이벤트 핸들러 (결과적 일관성)
  +-- BidPlacedEventHandler -> NotificationService
  +-- AuctionClosedEventHandler -> PaymentService, NotificationService
```

## 적용된 DDD 원칙 정리

| 원칙 | 적용 내용 |
|------|-----------|
| 풍부한 도메인 모델 | 모든 비즈니스 규칙이 Auction 애그리거트 내부에 캡슐화 |
| 값 객체 | Money, AuctionStatus, Bid를 불변 값 객체로 모델링 |
| Vernon 규칙 2 (작은 애그리거트) | Bid를 별도 애그리거트가 아닌 Auction 내부 값 객체로 유지 |
| Vernon 규칙 3 (ID 참조) | seller_id, bidder_id로 외부 애그리거트를 ID 참조 |
| Vernon 규칙 4 (결과적 일관성) | 알림/결제를 도메인 이벤트 핸들러로 분리 |
| 의도를 드러내는 인터페이스 | `_ensure_active()`, `_ensure_not_expired()`, `place_bid()`, `close()` |
| 자기 검증 | Money, Auction의 `__post_init__`에서 불변식 강제 |
| 응용 서비스 vs 도메인 로직 분리 | AuctionApplicationService는 조율만, 도메인 로직은 Auction에 위임 |
