# 온라인 경매 시스템 — 빈혈 도메인 모델 DDD 리팩토링

## 1. 문제 진단

원본 코드의 핵심 문제점:

- **빈혈 도메인 모델(Anemic Domain Model)**: `Auction`과 `Bid`가 데이터 컨테이너에 불과하며, 모든 비즈니스 로직이 `AuctionService`에 집중되어 있다.
- **도메인 불변조건(invariant) 미보호**: `status`, `bids` 등 내부 상태를 외부에서 자유롭게 조작할 수 있어 불변조건이 깨질 수 있다.
- **Value Object 부재**: `amount`, `start_price` 같은 금액 개념이 원시 타입으로 표현되어 도메인 의미가 드러나지 않는다.
- **도메인 이벤트 부재**: 서비스가 인프라(notification, payment)를 직접 호출하여 도메인과 인프라가 강결합되어 있다.
- **문자열 기반 상태 관리**: `status = "active"` 같은 문자열 상태는 오타나 잘못된 상태 전이에 취약하다.

## 2. 리팩토링 결과

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


# ──────────────────────────────────────────────
# Value Objects
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class Money:
    """금액을 표현하는 Value Object. 음수를 허용하지 않는다."""

    amount: int  # 최소 화폐 단위(원) 기준 정수

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("금액은 0 이상이어야 합니다")

    def __gt__(self, other: Money) -> bool:
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        return self.amount >= other.amount

    def __le__(self, other: Money) -> bool:
        return self.amount <= other.amount


@dataclass(frozen=True)
class BidderId:
    value: UUID


@dataclass(frozen=True)
class SellerId:
    value: UUID


@dataclass(frozen=True)
class AuctionId:
    value: UUID


# ──────────────────────────────────────────────
# Domain Events
# ──────────────────────────────────────────────

class DomainEvent:
    """모든 도메인 이벤트의 기반 클래스."""

    occurred_on: datetime = field(default_factory=datetime.now, init=False)


@dataclass(frozen=True)
class BidPlaced(DomainEvent):
    auction_id: AuctionId
    bidder_id: BidderId
    bid_amount: Money
    previous_highest_bidder_id: Optional[BidderId]


@dataclass(frozen=True)
class AuctionClosed(DomainEvent):
    auction_id: AuctionId
    winning_bidder_id: Optional[BidderId]
    winning_amount: Optional[Money]
    seller_id: SellerId


# ──────────────────────────────────────────────
# Enum
# ──────────────────────────────────────────────

class AuctionStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"


# ──────────────────────────────────────────────
# Entity: Bid
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class Bid:
    """입찰 Entity. Auction Aggregate 내부에서만 생성된다."""

    bidder_id: BidderId
    amount: Money
    created_at: datetime


# ──────────────────────────────────────────────
# Aggregate Root: Auction
# ──────────────────────────────────────────────

class Auction:
    """
    경매 Aggregate Root.

    모든 입찰 관련 비즈니스 로직과 불변조건을 Aggregate 내부에서 보호한다.
    외부에서 내부 상태를 직접 변경할 수 없으며, 반드시 행위 메서드를 통해서만 상태가 전이된다.
    """

    def __init__(
        self,
        id: AuctionId,
        seller_id: SellerId,
        item_name: str,
        start_price: Money,
        end_time: datetime,
    ) -> None:
        if not item_name or not item_name.strip():
            raise ValueError("상품명은 비어 있을 수 없습니다")
        if end_time <= datetime.now():
            raise ValueError("종료 시간은 현재 시간 이후여야 합니다")

        self._id = id
        self._seller_id = seller_id
        self._item_name = item_name
        self._start_price = start_price
        self._end_time = end_time
        self._bids: list[Bid] = []
        self._status = AuctionStatus.ACTIVE
        self._domain_events: list[DomainEvent] = []

    # ── Properties (읽기 전용 접근) ──

    @property
    def id(self) -> AuctionId:
        return self._id

    @property
    def seller_id(self) -> SellerId:
        return self._seller_id

    @property
    def item_name(self) -> str:
        return self._item_name

    @property
    def start_price(self) -> Money:
        return self._start_price

    @property
    def end_time(self) -> datetime:
        return self._end_time

    @property
    def status(self) -> AuctionStatus:
        return self._status

    @property
    def bid_count(self) -> int:
        return len(self._bids)

    @property
    def current_price(self) -> Money:
        """현재 최고 입찰가. 입찰이 없으면 시작가를 반환한다."""
        if not self._bids:
            return self._start_price
        return max(self._bids, key=lambda b: b.amount.amount).amount

    @property
    def winning_bid(self) -> Optional[Bid]:
        """현재 최고 입찰. 입찰이 없으면 None."""
        if not self._bids:
            return None
        return max(self._bids, key=lambda b: b.amount.amount)

    # ── 도메인 이벤트 ──

    @property
    def domain_events(self) -> list[DomainEvent]:
        return list(self._domain_events)

    def clear_events(self) -> None:
        self._domain_events.clear()

    def _raise_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    # ── 핵심 비즈니스 행위 ──

    def place_bid(self, bidder_id: BidderId, amount: Money) -> Bid:
        """
        입찰을 수행한다.

        불변조건:
        - 경매가 활성 상태여야 한다.
        - 경매 종료 시간이 지나지 않아야 한다.
        - 판매자 본인은 입찰할 수 없다.
        - 입찰 금액은 현재 최고가보다 높아야 한다.
        """
        self._ensure_active()
        self._ensure_not_expired()

        if bidder_id.value == self._seller_id.value:
            raise SelfBidNotAllowedError(self._id)

        if amount <= self.current_price:
            raise BidTooLowError(
                auction_id=self._id,
                bid_amount=amount,
                current_price=self.current_price,
            )

        previous_highest_bidder = (
            self.winning_bid.bidder_id if self.winning_bid else None
        )

        bid = Bid(
            bidder_id=bidder_id,
            amount=amount,
            created_at=datetime.now(),
        )
        self._bids.append(bid)

        self._raise_event(
            BidPlaced(
                auction_id=self._id,
                bidder_id=bidder_id,
                bid_amount=amount,
                previous_highest_bidder_id=previous_highest_bidder,
            )
        )

        return bid

    def close(self) -> None:
        """
        경매를 종료한다.

        불변조건:
        - 이미 종료된 경매는 다시 종료할 수 없다.
        """
        if self._status == AuctionStatus.CLOSED:
            raise AuctionAlreadyClosedError(self._id)

        self._status = AuctionStatus.CLOSED

        winner = self.winning_bid
        self._raise_event(
            AuctionClosed(
                auction_id=self._id,
                winning_bidder_id=winner.bidder_id if winner else None,
                winning_amount=winner.amount if winner else None,
                seller_id=self._seller_id,
            )
        )

    # ── 내부 불변조건 검증 ──

    def _ensure_active(self) -> None:
        if self._status != AuctionStatus.ACTIVE:
            raise AuctionNotActiveError(self._id)

    def _ensure_not_expired(self) -> None:
        if self._end_time < datetime.now():
            raise AuctionExpiredError(self._id)


# ──────────────────────────────────────────────
# Domain Exceptions
# ──────────────────────────────────────────────

class AuctionDomainError(Exception):
    """경매 도메인 예외 기반 클래스."""


class AuctionNotActiveError(AuctionDomainError):
    def __init__(self, auction_id: AuctionId) -> None:
        super().__init__(f"경매({auction_id.value})는 활성 상태가 아닙니다")


class AuctionExpiredError(AuctionDomainError):
    def __init__(self, auction_id: AuctionId) -> None:
        super().__init__(f"경매({auction_id.value})의 입찰 시간이 종료되었습니다")


class AuctionAlreadyClosedError(AuctionDomainError):
    def __init__(self, auction_id: AuctionId) -> None:
        super().__init__(f"경매({auction_id.value})는 이미 종료되었습니다")


class BidTooLowError(AuctionDomainError):
    def __init__(
        self, auction_id: AuctionId, bid_amount: Money, current_price: Money
    ) -> None:
        super().__init__(
            f"입찰 금액({bid_amount.amount}원)이 현재가({current_price.amount}원)보다 높아야 합니다"
        )


class SelfBidNotAllowedError(AuctionDomainError):
    def __init__(self, auction_id: AuctionId) -> None:
        super().__init__(f"경매({auction_id.value})에 판매자 본인은 입찰할 수 없습니다")


# ──────────────────────────────────────────────
# Application Service (얇은 서비스 계층)
# ──────────────────────────────────────────────

class AuctionApplicationService:
    """
    Application Service는 유스케이스 오케스트레이션만 담당한다.

    비즈니스 로직은 Aggregate(Auction)에 위임하고,
    이 계층은 리포지토리 조회/저장과 도메인 이벤트 디스패치만 수행한다.
    """

    def __init__(
        self,
        auction_repo: AuctionRepository,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._auction_repo = auction_repo
        self._event_dispatcher = event_dispatcher

    def place_bid(
        self, auction_id: AuctionId, bidder_id: BidderId, amount: Money
    ) -> None:
        auction = self._auction_repo.find_by_id(auction_id)

        auction.place_bid(bidder_id=bidder_id, amount=amount)

        self._auction_repo.save(auction)
        self._event_dispatcher.dispatch_all(auction.domain_events)
        auction.clear_events()

    def close_auction(self, auction_id: AuctionId) -> None:
        auction = self._auction_repo.find_by_id(auction_id)

        auction.close()

        self._auction_repo.save(auction)
        self._event_dispatcher.dispatch_all(auction.domain_events)
        auction.clear_events()


# ──────────────────────────────────────────────
# Port Interfaces (추상 인터페이스)
# ──────────────────────────────────────────────

from abc import ABC, abstractmethod


class AuctionRepository(ABC):
    @abstractmethod
    def find_by_id(self, auction_id: AuctionId) -> Auction:
        ...

    @abstractmethod
    def save(self, auction: Auction) -> None:
        ...


class DomainEventDispatcher(ABC):
    @abstractmethod
    def dispatch_all(self, events: list[DomainEvent]) -> None:
        ...
```

## 3. 리팩토링 핵심 변경 사항

### 3.1 원시 타입을 Value Object로 교체

| Before | After | 이유 |
|--------|-------|------|
| `amount: float/int` | `Money` (frozen dataclass) | 금액의 도메인 의미 부여, 음수 방지 불변조건 내장 |
| `auction_id: str` | `AuctionId` (frozen dataclass) | 식별자 혼동 방지 (seller_id와 auction_id를 바꿔 넣는 실수 차단) |
| `bidder_id: str` | `BidderId` (frozen dataclass) | 동일 |
| `seller_id: str` | `SellerId` (frozen dataclass) | 동일 |
| `status: str = "active"` | `AuctionStatus` (Enum) | 잘못된 문자열 상태 진입 원천 차단 |

### 3.2 비즈니스 로직을 Aggregate Root로 이동

**Before**: `AuctionService.place_bid()`가 모든 검증과 상태 변경을 수행 (빈혈 모델)

**After**: `Auction.place_bid()`와 `Auction.close()`가 불변조건 검증과 상태 전이를 직접 수행

이동된 로직:
- 활성 상태 검증 (`_ensure_active`)
- 시간 만료 검증 (`_ensure_not_expired`)
- 최고가 비교 검증 (`current_price` property)
- 판매자 본인 입찰 금지 (원본에 없던 불변조건 추가)
- 상태 전이 (`close` 메서드)

### 3.3 내부 상태 캡슐화

- 모든 내부 필드를 `_` prefix로 보호하고, 읽기 전용 `@property`만 노출한다.
- `_bids` 리스트는 외부에서 직접 접근/조작 불가. 반드시 `place_bid()` 메서드를 통해서만 입찰이 추가된다.
- `_status`는 `close()` 메서드를 통해서만 전이된다.

### 3.4 도메인 이벤트로 인프라 의존성 제거

**Before**: Service가 `notification_service.notify_outbid()`와 `payment_service.create_payment()`를 직접 호출 (도메인과 인프라의 강결합)

**After**: Aggregate가 `BidPlaced`, `AuctionClosed` 도메인 이벤트를 발행하고, Application Service가 `DomainEventDispatcher`를 통해 이벤트를 전달한다. 결제 생성, 알림 발송 등은 이벤트 핸들러(인프라 계층)에서 처리한다.

이 구조의 이점:
- Aggregate는 인프라 서비스를 전혀 알지 못한다.
- 새로운 부수효과(이메일, 로그, 통계 등)를 이벤트 핸들러 추가만으로 확장할 수 있다.

### 3.5 Application Service를 얇은 오케스트레이터로 축소

**Before**: `AuctionService`가 검증, 상태 변경, 인프라 호출을 모두 담당 (fat service)

**After**: `AuctionApplicationService`의 각 메서드는 3단계만 수행:
1. 리포지토리에서 Aggregate 조회
2. Aggregate의 행위 메서드 호출 (비즈니스 로직 위임)
3. 저장 및 이벤트 디스패치

### 3.6 도메인 전용 예외 체계

`ValueError` 대신 도메인 의미가 담긴 전용 예외(`AuctionNotActiveError`, `BidTooLowError` 등)를 사용하여, 호출자가 예외 유형에 따라 적절한 대응을 할 수 있게 했다.

### 3.7 원본에 없던 불변조건 추가

- **판매자 본인 입찰 금지**: `SelfBidNotAllowedError` -- 경매 도메인에서 당연히 보호해야 할 규칙이 원본에 누락되어 있었다.
- **이중 종료 방지**: `AuctionAlreadyClosedError` -- 이미 종료된 경매를 다시 종료하는 것을 방지한다.
- **경매 생성 시 검증**: 빈 상품명, 과거 종료 시간 등 생성자에서 즉시 검증한다.
