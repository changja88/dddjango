# 은행 계좌 이체 — 애그리거트 설계

## 1. 애그리거트 식별

### Account (계좌) 애그리거트

Account를 애그리거트 루트로 설계한다. 각 계좌는 독립적인 일관성 경계를 가진다.

```
Account (Aggregate Root)
├── accountId: AccountId
├── accountNumber: AccountNumber
├── holder: AccountHolder
├── balance: Money
├── accountType: AccountType (PERSONAL | CORPORATE)
├── bankCode: BankCode
├── dailyTransferredAmount: Money
├── lastTransferDate: LocalDate
└── transactionHistory: List<TransactionRecord>
```

### 주요 값 객체(Value Object)

```
Money
├── amount: Decimal
└── currency: Currency

AccountNumber
└── value: String

TransactionRecord
├── transactionId: TransactionId
├── type: TransactionType (WITHDRAWAL | DEPOSIT)
├── amount: Money
├── counterpartyAccount: AccountNumber
├── fee: Money
├── occurredAt: DateTime
└── memo: String
```

## 2. 트랜잭션 전략: 결과적 일관성 (Eventual Consistency)

### 판단 근거

두 계좌를 하나의 트랜잭션에서 수정하는 방식(강한 일관성)은 채택하지 않는다. 이유는 다음과 같다.

1. **애그리거트 간 트랜잭션 원칙 위반**: DDD의 핵심 원칙 중 하나는 "하나의 트랜잭션에서 하나의 애그리거트만 수정한다"이다. 출금 계좌와 입금 계좌는 서로 다른 애그리거트이므로 단일 트랜잭션으로 묶으면 애그리거트 경계가 무의미해진다.

2. **타행 이체 현실**: 타행 이체 시 상대 은행의 계좌를 동일 트랜잭션에서 수정하는 것은 물리적으로 불가능하다. 따라서 동일 은행 내 이체와 타행 이체를 동일한 아키텍처 패턴으로 처리하는 것이 일관된 설계다.

3. **성능과 확장성**: 두 계좌를 하나의 트랜잭션으로 묶으면 lock 경합이 발생하고, 계좌 수가 늘어날수록 병목이 심해진다.

### 채택 방식: Saga 패턴을 통한 결과적 일관성

이체 프로세스를 조율하는 별도의 도메인 서비스(TransferSaga)를 도입한다.

## 3. 이체 프로세스 흐름

```
[TransferService]
    │
    ├─ 1. 출금 계좌에서 출금 요청 (단일 트랜잭션)
    │      Account.withdraw(amount, fee)
    │      → 잔액 확인, 일일 한도 확인, 잔액 차감
    │      → TransactionRecord 기록
    │      → 도메인 이벤트 발행: MoneyWithdrawn
    │
    ├─ 2. 입금 계좌에 입금 처리 (별도 트랜잭션)
    │      Account.deposit(amount)
    │      → 잔액 추가
    │      → TransactionRecord 기록
    │      → 도메인 이벤트 발행: MoneyDeposited
    │
    └─ 3. 실패 시 보상 트랜잭션
           입금 실패 → 출금 계좌에 환불
           Account.compensateWithdrawal(amount, fee)
           → 도메인 이벤트 발행: WithdrawalCompensated
```

## 4. 애그리거트 행위 설계

### Account 애그리거트의 핵심 메서드

```python
class Account:
    """계좌 애그리거트 루트"""

    DAILY_LIMIT_PERSONAL = Money(5_000_000, Currency.KRW)
    DAILY_LIMIT_CORPORATE = Money(50_000_000, Currency.KRW)

    def withdraw(self, amount: Money, fee: Money, counterparty: AccountNumber) -> None:
        """출금 처리 — 모든 비즈니스 규칙을 이 안에서 검증"""
        total = amount + fee

        # 규칙 1: 잔액 부족 검증
        if self.balance < total:
            raise InsufficientBalanceError(self.account_id, self.balance, total)

        # 규칙 2: 일일 이체 한도 검증
        daily_limit = self._get_daily_limit()
        today_transferred = self._get_today_transferred_amount()
        if today_transferred + amount > daily_limit:
            raise DailyTransferLimitExceededError(
                self.account_id, daily_limit, today_transferred, amount
            )

        # 상태 변경
        self.balance = self.balance - total
        self._update_daily_transferred(amount)

        # 거래 내역 기록
        record = TransactionRecord(
            transaction_id=TransactionId.generate(),
            type=TransactionType.WITHDRAWAL,
            amount=amount,
            fee=fee,
            counterparty_account=counterparty,
            occurred_at=DateTime.now(),
        )
        self.transaction_history.append(record)

        # 도메인 이벤트
        self.register_event(MoneyWithdrawn(
            account_id=self.account_id,
            amount=amount,
            fee=fee,
            counterparty=counterparty,
        ))

    def deposit(self, amount: Money, counterparty: AccountNumber) -> None:
        """입금 처리"""
        self.balance = self.balance + amount

        record = TransactionRecord(
            transaction_id=TransactionId.generate(),
            type=TransactionType.DEPOSIT,
            amount=amount,
            fee=Money.zero(),
            counterparty_account=counterparty,
            occurred_at=DateTime.now(),
        )
        self.transaction_history.append(record)

        self.register_event(MoneyDeposited(
            account_id=self.account_id,
            amount=amount,
            counterparty=counterparty,
        ))

    def compensate_withdrawal(self, amount: Money, fee: Money) -> None:
        """보상 트랜잭션 — 입금 실패 시 출금 취소"""
        self.balance = self.balance + amount + fee
        self._rollback_daily_transferred(amount)

        self.register_event(WithdrawalCompensated(
            account_id=self.account_id,
            amount=amount,
            fee=fee,
        ))

    def _get_daily_limit(self) -> Money:
        if self.account_type == AccountType.PERSONAL:
            return self.DAILY_LIMIT_PERSONAL
        return self.DAILY_LIMIT_CORPORATE

    def _get_today_transferred_amount(self) -> Money:
        if self.last_transfer_date != LocalDate.today():
            return Money.zero()
        return self.daily_transferred_amount

    def _update_daily_transferred(self, amount: Money) -> None:
        if self.last_transfer_date != LocalDate.today():
            self.daily_transferred_amount = Money.zero()
            self.last_transfer_date = LocalDate.today()
        self.daily_transferred_amount = self.daily_transferred_amount + amount
```

## 5. 도메인 서비스: 이체 조율

```python
class TransferService:
    """이체를 조율하는 도메인/애플리케이션 서비스"""

    def __init__(
        self,
        account_repository: AccountRepository,
        fee_policy: TransferFeePolicy,
    ):
        self.account_repository = account_repository
        self.fee_policy = fee_policy

    def transfer(self, command: TransferCommand) -> TransferResult:
        # 1. 수수료 계산
        source = self.account_repository.find_by_id(command.source_account_id)
        target = self.account_repository.find_by_id(command.target_account_id)
        fee = self.fee_policy.calculate(source.bank_code, target.bank_code, command.amount)

        # 2. 출금 (첫 번째 트랜잭션)
        source.withdraw(command.amount, fee, target.account_number)
        self.account_repository.save(source)

        # 3. 입금 (두 번째 트랜잭션)
        try:
            target.deposit(command.amount, source.account_number)
            self.account_repository.save(target)
        except Exception:
            # 4. 보상 트랜잭션
            source = self.account_repository.find_by_id(command.source_account_id)
            source.compensate_withdrawal(command.amount, fee)
            self.account_repository.save(source)
            raise TransferFailedError(command.source_account_id, command.target_account_id)

        return TransferResult.success(command.amount, fee)
```

## 6. 수수료 정책 (도메인 서비스)

```python
class TransferFeePolicy:
    """이체 수수료 정책 — 도메인 서비스로 분리"""

    INTER_BANK_FEE = Money(500, Currency.KRW)

    def calculate(self, source_bank: BankCode, target_bank: BankCode, amount: Money) -> Money:
        if source_bank == target_bank:
            return Money.zero()  # 동일 은행: 수수료 없음
        return self.INTER_BANK_FEE  # 타행: 수수료 발생
```

## 7. 도메인 이벤트

| 이벤트 | 발행 시점 | 소비자 |
|--------|----------|--------|
| MoneyWithdrawn | 출금 성공 후 | 입금 처리 트리거, 알림 서비스 |
| MoneyDeposited | 입금 성공 후 | 알림 서비스 |
| WithdrawalCompensated | 보상 트랜잭션 후 | 알림 서비스, 모니터링 |
| DailyLimitExceeded | 한도 초과 시도 시 | 모니터링, 알림 서비스 |

## 8. 설계 결정 요약

| 항목 | 결정 | 이유 |
|------|------|------|
| 애그리거트 루트 | Account | 계좌가 잔액, 한도, 거래내역의 일관성 경계 |
| Transfer를 별도 애그리거트로? | 아니오 | 이체는 두 계좌에 대한 조율이지 자체 생명주기가 없음 |
| 트랜잭션 전략 | 결과적 일관성 (Saga) | 애그리거트 간 단일 트랜잭션 원칙 준수, 타행 이체와 동일 패턴 |
| 수수료 정책 | 도메인 서비스로 분리 | 두 계좌의 은행 코드를 비교해야 하므로 단일 애그리거트에 넣을 수 없음 |
| 일일 한도 | Account 내부에서 관리 | 단일 애그리거트의 불변식으로 보호 가능 |
| 거래 내역 | Account 내 TransactionRecord | 양쪽 계좌 각각에 기록, 애그리거트 일관성 경계 내 |
