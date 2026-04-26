# 은행 계좌 이체 기능 -- 애그리거트 설계

## 1. 전략 설계

### 1.1 하위 도메인 식별

| 하위 도메인 | 유형 | 설명 |
|------------|------|------|
| 계좌 관리 (Account) | 핵심(Core) | 계좌의 잔액 관리, 출금/입금, 잔액 불변식 보호 |
| 이체 (Transfer) | 핵심(Core) | 계좌 간 자금 이동, 이체 한도 관리, 수수료 정책 |
| 거래 내역 (Transaction History) | 지원(Supporting) | 양쪽 계좌의 이체 기록 저장 및 조회 |
| 수수료 (Fee) | 일반(Generic) | 타행 이체 수수료 계산 규칙 |

### 1.2 바운디드 컨텍스트

이체 기능의 핵심 도메인을 **Banking 컨텍스트** 하나로 설계한다.
"계좌"와 "이체"는 같은 유비쿼터스 언어를 공유하며, 동일한 비즈니스 프로세스 안에서 밀접하게 상호작용한다.
거래 내역은 Banking 컨텍스트 내부의 관심사로 포함한다.

외부 은행과의 연동(타행 이체 실행)은 **외부 은행 연동 컨텍스트**로 분리하고, ACL(충돌 방지 계층)을 두어 외부 모델의 오염을 차단한다.

```
[Banking 컨텍스트] --ACL--> [외부 은행 연동 컨텍스트]
```

### 1.3 유비쿼터스 언어

| 용어 | 정의 |
|------|------|
| 계좌 (Account) | 잔액을 보유하고 출금/입금이 가능한 금융 단위 |
| 이체 (Transfer) | 출금 계좌에서 입금 계좌로 자금을 이동하는 행위 |
| 출금 (Withdraw) | 계좌에서 금액을 차감하는 행위 |
| 입금 (Deposit) | 계좌에 금액을 추가하는 행위 |
| 일일 이체 한도 (Daily Transfer Limit) | 하루 동안 이체 가능한 최대 누적 금액 |
| 계좌 유형 (Account Type) | 개인/기업 구분. 이체 한도 정책을 결정한다 |
| 타행 이체 (Inter-bank Transfer) | 서로 다른 은행 간의 이체. 수수료가 발생한다 |
| 이체 수수료 (Transfer Fee) | 타행 이체 시 출금 계좌에 부과되는 비용 |
| 거래 내역 (Transaction Entry) | 계좌에 기록되는 개별 입출금 이력 |

---

## 2. 전술 설계 -- 애그리거트 경계 결정

### 2.1 핵심 질문: 두 계좌를 하나의 트랜잭션에서 수정할 것인가?

**결론: 결과적 일관성(Eventual Consistency)을 사용한다.**

근거는 다음과 같다.

**Vernon 규칙 1 -- "진짜 불변식을 일관성 경계 안에서 보호하라"**

출금 계좌의 불변식("잔액 >= 0", "일일 이체 한도 초과 불가")과 입금 계좌의 불변식은 서로 독립적이다.
출금 계좌가 잔액 부족인지 판단하는 데 입금 계좌의 상태는 필요 없다.
따라서 두 계좌는 서로 다른 일관성 경계에 속한다.

**Vernon 규칙 2 -- "작은 애그리거트를 설계하라"**

두 계좌를 하나의 애그리거트에 넣으면 애그리거트가 과도하게 커진다.
계좌 A에 대한 모든 이체가 계좌 B도 함께 잠가야 하므로 동시성 병목이 발생한다.

**Vernon 규칙 4 -- "일관성 경계 밖에서는 결과적 일관성을 사용하라"**

출금 계좌에서 출금이 성공하면 `MoneyWithdrawn` 도메인 이벤트를 발행하고, 이 이벤트를 구독하는 핸들러가 입금 계좌에 입금을 수행한다. 두 작업은 별도 트랜잭션으로 처리된다.

**실패 시나리오 처리:**

입금 측 실패 시 보상 트랜잭션(출금 취소)을 실행하는 Saga 패턴을 적용한다.
실무적으로 동일 데이터베이스 내 당행 이체의 경우, 같은 트랜잭션에서 두 계좌를 수정하는 것도 용인할 수 있다(reference: "동일 데이터베이스 내 단순 케이스에서는 같은 트랜잭션에서 복수 애그리거트를 수정하는 것도 용인할 수 있다"). 그러나 타행 이체는 물리적으로 분산 환경이므로 반드시 결과적 일관성이 필요하고, 당행 이체도 확장성을 위해 동일한 패턴으로 통일하는 것이 바람직하다.

### 2.2 애그리거트 식별

| 애그리거트 | 루트 엔티티 | 내부 구성요소 | 불변식 |
|-----------|-----------|-------------|--------|
| Account | Account | TransactionEntry (값 객체 컬렉션) | 잔액 >= 0, 일일 이체 누적 <= 한도 |
| Transfer | Transfer | -- | 이체 상태 전이 규칙 (요청됨 -> 완료/실패) |

Account와 Transfer는 별도 애그리거트다. Transfer는 출금 계좌와 입금 계좌를 ID로만 참조한다(Vernon 규칙 3).

---

## 3. 값 객체

```python
from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import date, datetime
from enum import Enum


@dataclass(frozen=True)
class Money:
    """금액 값 객체 -- 불변, 자기 검증"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def add(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return replace(self, amount=self.amount + other.amount)

    def subtract(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        if self.amount < other.amount:
            raise ValueError("잔액이 부족합니다")
        return replace(self, amount=self.amount - other.amount)

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")


class AccountType(Enum):
    """계좌 유형 -- 이체 한도 정책을 결정한다"""
    PERSONAL = "personal"
    CORPORATE = "corporate"

    @property
    def daily_transfer_limit(self) -> Money:
        limits = {
            AccountType.PERSONAL: Money(5_000_000),
            AccountType.CORPORATE: Money(50_000_000),
        }
        return limits[self]


class TransferStatus(Enum):
    """이체 상태"""
    REQUESTED = "requested"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class BankCode:
    """은행 코드 값 객체"""
    code: str

    def __post_init__(self) -> None:
        if not self.code or len(self.code) != 3:
            raise ValueError(f"은행 코드는 3자리여야 합니다: {self.code}")


@dataclass(frozen=True)
class TransactionEntry:
    """거래 내역 값 객체 -- 계좌에 기록되는 개별 입출금 이력"""
    transaction_type: str  # "WITHDRAWAL" | "DEPOSIT"
    amount: Money
    counterpart_account_id: str
    description: str
    occurred_at: datetime
    transfer_id: str
```

---

## 4. 애그리거트 설계

### 4.1 Account 애그리거트

```python
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List
from uuid import uuid4


@dataclass(frozen=True)
class MoneyWithdrawn:
    """출금 완료 도메인 이벤트"""
    account_id: str
    transfer_id: str
    amount: Money
    counterpart_account_id: str
    occurred_at: datetime


@dataclass(frozen=True)
class MoneyDeposited:
    """입금 완료 도메인 이벤트"""
    account_id: str
    transfer_id: str
    amount: Money
    counterpart_account_id: str
    occurred_at: datetime


@dataclass
class Account:
    """계좌 애그리거트 루트

    불변식:
    - 잔액은 0 이상이어야 한다
    - 일일 이체 누적 금액은 계좌 유형별 한도를 초과할 수 없다

    Vernon 규칙 적용:
    - 규칙 1: 잔액과 일일 이체 한도는 이 애그리거트 안에서 보호한다
    - 규칙 2: Account 루트 + 최소한의 값 객체로 구성한다
    - 규칙 3: 다른 Account는 ID로만 참조한다
    - 규칙 4: 입금 계좌 업데이트는 도메인 이벤트로 결과적 일관성 처리한다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    owner_name: str = ""
    account_type: AccountType = AccountType.PERSONAL
    bank_code: BankCode = None
    _balance: Money = field(default_factory=lambda: Money(0))
    _daily_transferred: Money = field(default_factory=lambda: Money(0))
    _daily_transferred_date: date = field(default_factory=date.today)
    _transaction_entries: List[TransactionEntry] = field(default_factory=list)
    _events: List = field(default_factory=list)

    @property
    def balance(self) -> Money:
        return self._balance

    def withdraw(
        self,
        amount: Money,
        transfer_id: str,
        counterpart_account_id: str,
    ) -> None:
        """출금 -- 잔액과 일일 이체 한도를 검증한 후 차감한다"""
        self._reset_daily_limit_if_new_day()
        self._verify_sufficient_balance(amount)
        self._verify_daily_transfer_limit(amount)

        self._balance = self._balance.subtract(amount)
        self._daily_transferred = self._daily_transferred.add(amount)

        self._transaction_entries.append(
            TransactionEntry(
                transaction_type="WITHDRAWAL",
                amount=amount,
                counterpart_account_id=counterpart_account_id,
                description=f"이체 출금 (이체번호: {transfer_id})",
                occurred_at=datetime.now(),
                transfer_id=transfer_id,
            )
        )

        self._events.append(
            MoneyWithdrawn(
                account_id=self.id,
                transfer_id=transfer_id,
                amount=amount,
                counterpart_account_id=counterpart_account_id,
                occurred_at=datetime.now(),
            )
        )

    def deposit(
        self,
        amount: Money,
        transfer_id: str,
        counterpart_account_id: str,
    ) -> None:
        """입금 -- 잔액에 금액을 추가한다"""
        self._balance = self._balance.add(amount)

        self._transaction_entries.append(
            TransactionEntry(
                transaction_type="DEPOSIT",
                amount=amount,
                counterpart_account_id=counterpart_account_id,
                description=f"이체 입금 (이체번호: {transfer_id})",
                occurred_at=datetime.now(),
                transfer_id=transfer_id,
            )
        )

        self._events.append(
            MoneyDeposited(
                account_id=self.id,
                transfer_id=transfer_id,
                amount=amount,
                counterpart_account_id=counterpart_account_id,
                occurred_at=datetime.now(),
            )
        )

    def _verify_sufficient_balance(self, amount: Money) -> None:
        if self._balance.amount < amount.amount:
            raise ValueError(
                f"잔액이 부족합니다. 현재 잔액: {self._balance.amount}, "
                f"출금 요청: {amount.amount}"
            )

    def _verify_daily_transfer_limit(self, amount: Money) -> None:
        limit = self.account_type.daily_transfer_limit
        projected = self._daily_transferred.add(amount)
        if projected.amount > limit.amount:
            raise ValueError(
                f"일일 이체 한도를 초과합니다. "
                f"한도: {limit.amount}, "
                f"금일 이체 누적: {self._daily_transferred.amount}, "
                f"요청 금액: {amount.amount}"
            )

    def _reset_daily_limit_if_new_day(self) -> None:
        today = date.today()
        if self._daily_transferred_date != today:
            self._daily_transferred = Money(0)
            self._daily_transferred_date = today

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events
```

### 4.2 Transfer 애그리거트

```python
@dataclass(frozen=True)
class TransferRequested:
    """이체 요청됨 도메인 이벤트"""
    transfer_id: str
    source_account_id: str
    target_account_id: str
    amount: Money
    fee: Money
    occurred_at: datetime


@dataclass(frozen=True)
class TransferCompleted:
    """이체 완료됨 도메인 이벤트"""
    transfer_id: str
    occurred_at: datetime


@dataclass(frozen=True)
class TransferFailed:
    """이체 실패됨 도메인 이벤트"""
    transfer_id: str
    reason: str
    occurred_at: datetime


@dataclass
class Transfer:
    """이체 애그리거트 루트

    이체 프로세스의 상태를 추적하고, 상태 전이 규칙을 보호한다.
    출금 계좌와 입금 계좌는 ID로만 참조한다 (Vernon 규칙 3).
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    source_account_id: str = ""     # Account를 ID로 참조
    target_account_id: str = ""     # Account를 ID로 참조
    amount: Money = None
    fee: Money = field(default_factory=lambda: Money(0))
    _status: TransferStatus = TransferStatus.REQUESTED
    _failure_reason: str = ""
    requested_at: datetime = field(default_factory=datetime.now)
    _events: List = field(default_factory=list)

    def mark_withdrawn(self) -> None:
        """출금 완료를 기록한다"""
        if self._status != TransferStatus.REQUESTED:
            raise ValueError(
                f"출금 완료 처리는 REQUESTED 상태에서만 가능합니다. "
                f"현재 상태: {self._status.value}"
            )
        self._status = TransferStatus.WITHDRAWN

    def complete(self) -> None:
        """이체를 완료한다"""
        if self._status != TransferStatus.WITHDRAWN:
            raise ValueError(
                f"이체 완료는 WITHDRAWN 상태에서만 가능합니다. "
                f"현재 상태: {self._status.value}"
            )
        self._status = TransferStatus.COMPLETED
        self._events.append(
            TransferCompleted(
                transfer_id=self.id,
                occurred_at=datetime.now(),
            )
        )

    def fail(self, reason: str) -> None:
        """이체를 실패 처리한다"""
        if self._status == TransferStatus.COMPLETED:
            raise ValueError("이미 완료된 이체는 실패 처리할 수 없습니다")
        self._status = TransferStatus.FAILED
        self._failure_reason = reason
        self._events.append(
            TransferFailed(
                transfer_id=self.id,
                reason=reason,
                occurred_at=datetime.now(),
            )
        )

    @property
    def status(self) -> TransferStatus:
        return self._status

    @property
    def total_deduction(self) -> Money:
        """출금 계좌에서 차감할 총액 (이체 금액 + 수수료)"""
        return self.amount.add(self.fee)

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events
```

---

## 5. 도메인 서비스 -- 수수료 계산

수수료 계산은 출금 계좌의 은행 코드와 입금 계좌의 은행 코드를 비교해야 하므로, 한 애그리거트에 넣기 어려운 로직이다. 도메인 서비스로 분리한다. 애그리거트는 이 서비스를 모른다(응용 서비스가 호출하고 결과를 전달한다).

```python
class TransferFeeCalculationService:
    """이체 수수료 계산 도메인 서비스

    - 상태가 없다 (stateless)
    - 여러 애그리거트(출금 계좌, 입금 계좌)의 정보를 사용하여 계산
    - 애그리거트는 이 서비스를 모른다
    """

    INTER_BANK_FEE = Money(500)

    def calculate_fee(
        self,
        source_bank_code: BankCode,
        target_bank_code: BankCode,
    ) -> Money:
        """타행 이체 시 수수료를 계산한다"""
        if source_bank_code == target_bank_code:
            return Money(0)
        return self.INTER_BANK_FEE
```

---

## 6. 응용 서비스와 Saga -- 이체 프로세스

### 6.1 이체 요청 응용 서비스

```python
@dataclass
class TransferCommand:
    """이체 요청 커맨드"""
    source_account_id: str
    target_account_id: str
    amount: int


class TransferApplicationService:
    """이체 응용 서비스

    비즈니스 로직을 직접 구현하지 않는다.
    도메인 서비스와 애그리거트에 위임하고, 흐름을 조율한다.
    """

    def __init__(
        self,
        account_repo: AccountRepository,
        transfer_repo: TransferRepository,
        fee_service: TransferFeeCalculationService,
        event_bus: EventBus,
    ):
        self._account_repo = account_repo
        self._transfer_repo = transfer_repo
        self._fee_service = fee_service
        self._event_bus = event_bus

    def request_transfer(self, cmd: TransferCommand) -> str:
        """이체를 요청한다

        1. 수수료를 계산한다 (도메인 서비스)
        2. Transfer 애그리거트를 생성한다
        3. 출금 계좌에서 출금한다 (잔액, 한도 검증은 Account가 수행)
        4. Transfer 상태를 WITHDRAWN으로 변경한다
        5. 도메인 이벤트를 발행한다 (입금은 결과적 일관성으로 처리)
        """
        source_account = self._account_repo.find_by_id(cmd.source_account_id)
        if source_account is None:
            raise ValueError("출금 계좌를 찾을 수 없습니다")

        target_account = self._account_repo.find_by_id(cmd.target_account_id)
        if target_account is None:
            raise ValueError("입금 계좌를 찾을 수 없습니다")

        # 1. 수수료 계산 (도메인 서비스 -- 애그리거트는 서비스를 모른다)
        fee = self._fee_service.calculate_fee(
            source_bank_code=source_account.bank_code,
            target_bank_code=target_account.bank_code,
        )

        # 2. Transfer 애그리거트 생성
        transfer = Transfer(
            source_account_id=cmd.source_account_id,
            target_account_id=cmd.target_account_id,
            amount=Money(cmd.amount),
            fee=fee,
        )

        # 3. 출금 (잔액, 한도 검증은 Account 애그리거트가 수행)
        source_account.withdraw(
            amount=transfer.total_deduction,
            transfer_id=transfer.id,
            counterpart_account_id=cmd.target_account_id,
        )

        # 4. Transfer 상태 변경
        transfer.mark_withdrawn()

        # 5. 저장 및 이벤트 발행
        self._account_repo.save(source_account)
        self._transfer_repo.save(transfer)

        for event in source_account.collect_domain_events():
            self._event_bus.publish(event)

        return transfer.id
```

### 6.2 이벤트 핸들러 -- 결과적 일관성으로 입금 처리

```python
class MoneyWithdrawnHandler:
    """출금 완료 이벤트 핸들러 -- 별도 트랜잭션에서 입금을 수행한다

    결과적 일관성: 출금과 입금은 별도 트랜잭션으로 처리된다.
    입금 실패 시 보상 트랜잭션(출금 취소)을 실행한다.
    """

    def __init__(
        self,
        account_repo: AccountRepository,
        transfer_repo: TransferRepository,
    ):
        self._account_repo = account_repo
        self._transfer_repo = transfer_repo

    def handle(self, event: MoneyWithdrawn) -> None:
        transfer = self._transfer_repo.find_by_id(event.transfer_id)
        target_account = self._account_repo.find_by_id(
            event.counterpart_account_id
        )

        try:
            target_account.deposit(
                amount=event.amount,
                transfer_id=event.transfer_id,
                counterpart_account_id=event.account_id,
            )
            transfer.complete()

            self._account_repo.save(target_account)
            self._transfer_repo.save(transfer)

        except Exception as e:
            # 보상 트랜잭션: 출금을 취소한다
            transfer.fail(reason=str(e))
            self._transfer_repo.save(transfer)
            self._compensate_withdrawal(event)

    def _compensate_withdrawal(self, event: MoneyWithdrawn) -> None:
        """보상 트랜잭션 -- 출금 계좌에 금액을 되돌린다"""
        source_account = self._account_repo.find_by_id(event.account_id)
        source_account.deposit(
            amount=event.amount,
            transfer_id=event.transfer_id,
            counterpart_account_id=event.counterpart_account_id,
        )
        self._account_repo.save(source_account)
```

---

## 7. 리포지토리 인터페이스

```python
from abc import ABC, abstractmethod
from typing import Optional


class AccountRepository(ABC):
    """계좌 리포지토리 -- 애그리거트 단위로 영속성 처리"""

    @abstractmethod
    def find_by_id(self, account_id: str) -> Optional[Account]:
        ...

    @abstractmethod
    def save(self, account: Account) -> None:
        ...


class TransferRepository(ABC):
    """이체 리포지토리 -- 애그리거트 단위로 영속성 처리"""

    @abstractmethod
    def find_by_id(self, transfer_id: str) -> Optional[Transfer]:
        ...

    @abstractmethod
    def save(self, transfer: Transfer) -> None:
        ...
```

---

## 8. 설계 결정 요약

| # | 결정 사항 | 결론 | 근거 |
|---|----------|------|------|
| 1 | 두 계좌를 하나의 트랜잭션에서 수정? | **아니오 -- 결과적 일관성 사용** | Vernon 규칙 4. 두 계좌의 불변식은 독립적이다. 타행 이체는 물리적으로 분산 환경이므로 반드시 결과적 일관성이 필요하고, 당행 이체도 동일 패턴으로 통일한다. |
| 2 | Account와 Transfer를 분리? | **별도 애그리거트** | Vernon 규칙 2. Transfer는 프로세스 상태를 추적하는 독립적 관심사다. Account에 넣으면 애그리거트가 과도하게 커진다. |
| 3 | 수수료 계산을 어디에 위치시키나? | **도메인 서비스** | 두 계좌의 은행 코드를 비교해야 하므로 한 애그리거트에 넣기 어렵다. 무상태 도메인 서비스로 분리하고, 응용 서비스가 호출한 결과를 Transfer에 전달한다. |
| 4 | 일일 이체 한도 검증 위치? | **Account 애그리거트 내부** | 한도는 계좌의 불변식이다. 빈혈 모델을 피하고, 비즈니스 규칙을 엔티티 안에 캡슐화한다. |
| 5 | 거래 내역 기록 방식? | **TransactionEntry 값 객체를 Account 내부에 보유** | 거래 내역은 계좌의 상태 변경과 함께 동일 트랜잭션에서 기록되어야 하는 불변식이다. |
| 6 | 입금 실패 시 처리? | **Saga 보상 트랜잭션** | 출금 계좌에 금액을 되돌리는 보상 행동을 실행한다. |

## 9. 이체 흐름 시퀀스

```
사용자 -> TransferApplicationService.request_transfer()
  |
  |--> TransferFeeCalculationService.calculate_fee()     -- 수수료 계산
  |--> Transfer 생성 (REQUESTED)
  |--> Account(출금).withdraw()                          -- 잔액/한도 검증 + 출금
  |      불변식 검증: 잔액 >= 출금액+수수료
  |      불변식 검증: 일일 이체 누적 + 출금액 <= 한도
  |      TransactionEntry 기록
  |      MoneyWithdrawn 이벤트 수집
  |--> Transfer.mark_withdrawn() (WITHDRAWN)
  |--> 저장 + 이벤트 발행
  |
  |--- [비동기 / 결과적 일관성] --->
  |
MoneyWithdrawnHandler.handle()
  |--> Account(입금).deposit()                           -- 입금
  |      TransactionEntry 기록
  |--> Transfer.complete() (COMPLETED)
  |--> 저장
  |
  |--- [실패 시] --->
  |
  |--> Transfer.fail() (FAILED)
  |--> 보상: Account(출금).deposit()                      -- 출금 취소
```
