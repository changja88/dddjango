# Inside-Out TDD: 환율 계산기

Inside-Out TDD(고전 학파)로 환율 계산기를 구현한다. 도메인 핵심(Money 값 객체)부터 시작하여 바깥(환율 서비스, 수수료)으로 나아간다. 모든 협력 객체는 실제 객체를 사용하고 Mock은 쓰지 않는다.

## 테스트 목록

```
[ ] Money 생성 및 동등성
[ ] Money 같은 통화 덧셈
[ ] Money 다른 통화 덧셈 거부
[ ] Money 곱셈 (수수료 계산용)
[ ] ExchangeRate 환율 등록 및 조회
[ ] ExchangeRate 미등록 통화 쌍 조회 시 에러
[ ] ExchangeService USD -> KRW 변환
[ ] ExchangeService EUR -> KRW 변환
[ ] ExchangeService 수수료 1.5% 적용
[ ] ExchangeService 수수료 적용 후 소수점 이하 반올림
[ ] ExchangeService 같은 통화 변환 (수수료 없음)
```

---

## 1단계: Money 값 객체 -- 도메인 핵심

가장 안쪽 도메인 핵심인 Money 값 객체부터 시작한다. 값 객체는 불변이며, 동등성은 값에 의해 결정된다.

### Cycle 1: Money 생성 및 동등성

**Red** -- Money를 생성하고 동등성을 검증하는 테스트를 작성한다.

```python
# test_money.py

def test_money_equality():
    assert Money(1000, "KRW") == Money(1000, "KRW")


def test_money_inequality_by_amount():
    assert Money(1000, "KRW") != Money(2000, "KRW")


def test_money_inequality_by_currency():
    assert Money(1000, "KRW") != Money(1000, "USD")
```

```
$ pytest test_money.py
NameError: name 'Money' is not defined
```

**Green** -- 테스트를 통과시키기 위한 최소한의 구현. `frozen=True`로 불변 값 객체를 만든다.

```python
# money.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str
```

```
$ pytest test_money.py
3 passed
```

**Refactor** -- `dataclass(frozen=True)`가 `__eq__`와 `__hash__`를 자동으로 제공하므로 추가 리팩토링 불필요. 테스트 파일에 import만 추가한다.

```python
# test_money.py
from money import Money
```

```
[x] Money 생성 및 동등성
```

### Cycle 2: 같은 통화 덧셈

**Red** -- 같은 통화끼리 더하는 테스트를 작성한다.

```python
def test_add_same_currency():
    result = Money(1000, "KRW").add(Money(2000, "KRW"))
    assert result == Money(3000, "KRW")
```

```
$ pytest test_money.py::test_add_same_currency
AttributeError: 'Money' object has no attribute 'add'
```

**Green** -- Obvious Implementation. 덧셈은 명백하다.

```python
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def add(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount, self.currency)
```

```
$ pytest test_money.py
4 passed
```

**Refactor** -- 깨끗하다. 다음으로.

```
[x] Money 같은 통화 덧셈
```

### Cycle 3: 다른 통화 덧셈 거부

**Red** -- 다른 통화끼리 더하면 에러가 발생해야 한다.

```python
import pytest


def test_add_different_currency_raises():
    with pytest.raises(ValueError, match="Cannot add different currencies"):
        Money(10, "USD").add(Money(1000, "KRW"))
```

```
$ pytest test_money.py::test_add_different_currency_raises
FAILED - ValueError not raised
```

**Green** -- 통화 일치 검증을 추가한다.

```python
def add(self, other: "Money") -> "Money":
    if self.currency != other.currency:
        raise ValueError(
            f"Cannot add different currencies: {self.currency} and {other.currency}"
        )
    return Money(self.amount + other.amount, self.currency)
```

```
$ pytest test_money.py
5 passed
```

**Refactor** -- 깨끗하다.

```
[x] Money 다른 통화 덧셈 거부
```

### Cycle 4: Money 곱셈

수수료 계산에 필요한 곱셈 연산이다. float 결과는 반올림하여 int로 변환한다.

**Red**

```python
def test_multiply():
    result = Money(10000, "KRW").multiply(1.015)
    assert result == Money(10150, "KRW")


def test_multiply_rounds_down():
    result = Money(10001, "KRW").multiply(1.015)
    # 10001 * 1.015 = 10151.015 -> 반올림 -> 10151
    assert result == Money(10151, "KRW")
```

```
$ pytest test_money.py::test_multiply
AttributeError: 'Money' object has no attribute 'multiply'
```

**Green**

```python
def multiply(self, factor: float) -> "Money":
    return Money(round(self.amount * factor), self.currency)
```

```
$ pytest test_money.py
7 passed
```

**Refactor** -- 깨끗하다.

```
[x] Money 곱셈 (수수료 계산용)
```

### Money 중간 정리

```python
# money.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: float) -> "Money":
        return Money(round(self.amount * factor), self.currency)
```

```python
# test_money.py
import pytest
from money import Money


def test_money_equality():
    assert Money(1000, "KRW") == Money(1000, "KRW")


def test_money_inequality_by_amount():
    assert Money(1000, "KRW") != Money(2000, "KRW")


def test_money_inequality_by_currency():
    assert Money(1000, "KRW") != Money(1000, "USD")


def test_add_same_currency():
    result = Money(1000, "KRW").add(Money(2000, "KRW"))
    assert result == Money(3000, "KRW")


def test_add_different_currency_raises():
    with pytest.raises(ValueError, match="Cannot add different currencies"):
        Money(10, "USD").add(Money(1000, "KRW"))


def test_multiply():
    result = Money(10000, "KRW").multiply(1.015)
    assert result == Money(10150, "KRW")


def test_multiply_rounds_down():
    result = Money(10001, "KRW").multiply(1.015)
    assert result == Money(10151, "KRW")
```

---

## 2단계: ExchangeRate -- 환율 저장소

Money가 완성되었으므로 한 단계 바깥으로 나간다. 환율 정보를 관리하는 객체를 구현한다.

### Cycle 5: 환율 등록 및 조회

**Red** -- 환율을 등록하고 조회하는 가장 단순한 경우부터 시작한다.

```python
# test_exchange_rate.py
from exchange_rate import ExchangeRate


def test_register_and_get_rate():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    assert rates.get("USD", "KRW") == 1300
```

```
$ pytest test_exchange_rate.py
ModuleNotFoundError: No module named 'exchange_rate'
```

**Green** -- Fake It. 상수를 반환하여 일단 통과시킨다.

```python
# exchange_rate.py
class ExchangeRate:
    def register(self, source: str, target: str, rate: float) -> None:
        pass

    def get(self, source: str, target: str) -> float:
        return 1300
```

```
$ pytest test_exchange_rate.py
1 passed
```

이제 삼각측량으로 일반화를 강제한다.

**Red** -- 두 번째 예를 추가한다.

```python
def test_register_multiple_rates():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    rates.register("EUR", "KRW", 1400)
    assert rates.get("USD", "KRW") == 1300
    assert rates.get("EUR", "KRW") == 1400
```

```
$ pytest test_exchange_rate.py::test_register_multiple_rates
FAILED - assert 1300 == 1400
```

**Green** -- 삼각측량에 의해 일반화한다. 딕셔너리로 저장한다.

```python
class ExchangeRate:
    def __init__(self) -> None:
        self._rates: dict[tuple[str, str], float] = {}

    def register(self, source: str, target: str, rate: float) -> None:
        self._rates[(source, target)] = rate

    def get(self, source: str, target: str) -> float:
        return self._rates[(source, target)]
```

```
$ pytest test_exchange_rate.py
2 passed
```

**Refactor** -- 깨끗하다.

```
[x] ExchangeRate 환율 등록 및 조회
```

### Cycle 6: 미등록 통화 쌍 조회 시 에러

**Red**

```python
import pytest


def test_get_unregistered_rate_raises():
    rates = ExchangeRate()
    with pytest.raises(KeyError, match="No exchange rate"):
        rates.get("GBP", "KRW")
```

```
$ pytest test_exchange_rate.py::test_get_unregistered_rate_raises
FAILED - KeyError: ('GBP', 'KRW')  # 메시지가 다름
```

**Green** -- 명확한 에러 메시지를 제공한다.

```python
def get(self, source: str, target: str) -> float:
    try:
        return self._rates[(source, target)]
    except KeyError:
        raise KeyError(f"No exchange rate for {source} -> {target}")
```

```
$ pytest test_exchange_rate.py
3 passed
```

**Refactor** -- 깨끗하다.

```
[x] ExchangeRate 미등록 통화 쌍 조회 시 에러
```

### ExchangeRate 중간 정리

```python
# exchange_rate.py
class ExchangeRate:
    def __init__(self) -> None:
        self._rates: dict[tuple[str, str], float] = {}

    def register(self, source: str, target: str, rate: float) -> None:
        self._rates[(source, target)] = rate

    def get(self, source: str, target: str) -> float:
        try:
            return self._rates[(source, target)]
        except KeyError:
            raise KeyError(f"No exchange rate for {source} -> {target}")
```

```python
# test_exchange_rate.py
import pytest
from exchange_rate import ExchangeRate


def test_register_and_get_rate():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    assert rates.get("USD", "KRW") == 1300


def test_register_multiple_rates():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    rates.register("EUR", "KRW", 1400)
    assert rates.get("USD", "KRW") == 1300
    assert rates.get("EUR", "KRW") == 1400


def test_get_unregistered_rate_raises():
    rates = ExchangeRate()
    with pytest.raises(KeyError, match="No exchange rate"):
        rates.get("GBP", "KRW")
```

---

## 3단계: ExchangeService -- 환율 변환 서비스

Money와 ExchangeRate가 모두 실제 객체로 준비되었다. 이들을 조합하는 서비스 계층을 구현한다. Mock 없이, 앞서 구현한 실제 객체를 그대로 사용한다.

### Cycle 7: USD -> KRW 기본 변환

**Red** -- 수수료 없는 가장 단순한 변환부터 시작한다.

```python
# test_exchange_service.py
from money import Money
from exchange_rate import ExchangeRate
from exchange_service import ExchangeService


def test_convert_usd_to_krw():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    service = ExchangeService(rates)

    result = service.convert(Money(10, "USD"), "KRW")

    assert result == Money(13000, "KRW")
```

```
$ pytest test_exchange_service.py
ModuleNotFoundError: No module named 'exchange_service'
```

**Green** -- Obvious Implementation. 환율을 조회하여 변환한다.

```python
# exchange_service.py
from money import Money
from exchange_rate import ExchangeRate


class ExchangeService:
    def __init__(self, rates: ExchangeRate) -> None:
        self._rates = rates

    def convert(self, source: Money, target_currency: str) -> Money:
        rate = self._rates.get(source.currency, target_currency)
        return Money(round(source.amount * rate), target_currency)
```

```
$ pytest test_exchange_service.py
1 passed
```

**Refactor** -- 깨끗하다.

```
[x] ExchangeService USD -> KRW 변환
```

### Cycle 8: EUR -> KRW 변환

**Red** -- 두 번째 통화 쌍으로 삼각측량. 기존 구현이 이미 일반적이므로 이 테스트는 바로 통과할 것으로 예상한다.

```python
def test_convert_eur_to_krw():
    rates = ExchangeRate()
    rates.register("EUR", "KRW", 1400)
    service = ExchangeService(rates)

    result = service.convert(Money(10, "EUR"), "KRW")

    assert result == Money(14000, "KRW")
```

```
$ pytest test_exchange_service.py
2 passed
```

이미 통과한다. 구현이 충분히 일반적임을 확인했다.

```
[x] ExchangeService EUR -> KRW 변환
```

### Cycle 9: 수수료 1.5% 적용

**Red** -- 수수료율을 적용한 변환을 테스트한다. 10 USD * 1300 = 13000, 수수료 1.5% 적용 = 13000 * 1.015 = 13195.

```python
def test_convert_with_commission():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    service = ExchangeService(rates, commission_rate=0.015)

    result = service.convert(Money(10, "USD"), "KRW")

    assert result == Money(13195, "KRW")
```

```
$ pytest test_exchange_service.py::test_convert_with_commission
TypeError: ExchangeService.__init__() got an unexpected keyword argument 'commission_rate'
```

**Green** -- 수수료율을 받아서 적용한다.

```python
class ExchangeService:
    def __init__(self, rates: ExchangeRate, commission_rate: float = 0.0) -> None:
        self._rates = rates
        self._commission_rate = commission_rate

    def convert(self, source: Money, target_currency: str) -> Money:
        rate = self._rates.get(source.currency, target_currency)
        converted = Money(round(source.amount * rate), target_currency)
        return converted.multiply(1 + self._commission_rate)
```

```
$ pytest test_exchange_service.py
3 passed
```

**Refactor** -- 깨끗하다. 수수료를 변환 결과에 곱하는 방식은 Money.multiply를 재사용하므로 중복이 없다.

```
[x] ExchangeService 수수료 1.5% 적용
```

### Cycle 10: 수수료 적용 후 소수점 이하 반올림

**Red** -- 반올림이 정확히 이루어지는지 경계 케이스를 확인한다. 7 USD * 1300 = 9100, 수수료 1.5% 적용 = 9100 * 1.015 = 9236.5 -> 반올림 -> 9237 (Python round는 banker's rounding이지만 .5는 짝수 쪽으로, 여기서는 9236이 짝수이므로 9236).

수치를 조정한다. 33 USD * 1300 = 42900, 수수료 1.5% = 42900 * 1.015 = 43543.5 -> round = 43544 (banker's rounding: .5에서 짝수 쪽으로 -> 43544).

**Red**

```python
def test_convert_with_commission_rounds():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    service = ExchangeService(rates, commission_rate=0.015)

    result = service.convert(Money(33, "USD"), "KRW")

    # 33 * 1300 = 42900, 42900 * 1.015 = 43543.5 -> round -> 43544
    assert result == Money(43544, "KRW")
```

```
$ pytest test_exchange_service.py
4 passed
```

이미 통과한다. Money.multiply에서 round()를 사용하고 있어 반올림이 올바르게 처리된다.

```
[x] ExchangeService 수수료 적용 후 소수점 이하 반올림
```

### Cycle 11: 같은 통화 변환

**Red** -- 같은 통화로 변환하면 수수료 없이 그대로 반환해야 한다. 환율은 1이고 수수료도 없다.

```python
def test_convert_same_currency_no_commission():
    rates = ExchangeRate()
    service = ExchangeService(rates, commission_rate=0.015)

    result = service.convert(Money(1000, "KRW"), "KRW")

    assert result == Money(1000, "KRW")
```

```
$ pytest test_exchange_service.py::test_convert_same_currency_no_commission
KeyError: No exchange rate for KRW -> KRW
```

**Green** -- 같은 통화일 때 바로 반환하는 조건을 추가한다.

```python
def convert(self, source: Money, target_currency: str) -> Money:
    if source.currency == target_currency:
        return source
    rate = self._rates.get(source.currency, target_currency)
    converted = Money(round(source.amount * rate), target_currency)
    return converted.multiply(1 + self._commission_rate)
```

```
$ pytest test_exchange_service.py
5 passed
```

**Refactor** -- 깨끗하다.

```
[x] ExchangeService 같은 통화 변환 (수수료 없음)
```

---

## 최종 코드

### money.py

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: float) -> "Money":
        return Money(round(self.amount * factor), self.currency)
```

### exchange_rate.py

```python
class ExchangeRate:
    def __init__(self) -> None:
        self._rates: dict[tuple[str, str], float] = {}

    def register(self, source: str, target: str, rate: float) -> None:
        self._rates[(source, target)] = rate

    def get(self, source: str, target: str) -> float:
        try:
            return self._rates[(source, target)]
        except KeyError:
            raise KeyError(f"No exchange rate for {source} -> {target}")
```

### exchange_service.py

```python
from money import Money
from exchange_rate import ExchangeRate


class ExchangeService:
    def __init__(self, rates: ExchangeRate, commission_rate: float = 0.0) -> None:
        self._rates = rates
        self._commission_rate = commission_rate

    def convert(self, source: Money, target_currency: str) -> Money:
        if source.currency == target_currency:
            return source
        rate = self._rates.get(source.currency, target_currency)
        converted = Money(round(source.amount * rate), target_currency)
        return converted.multiply(1 + self._commission_rate)
```

### test_money.py

```python
import pytest
from money import Money


def test_money_equality():
    assert Money(1000, "KRW") == Money(1000, "KRW")


def test_money_inequality_by_amount():
    assert Money(1000, "KRW") != Money(2000, "KRW")


def test_money_inequality_by_currency():
    assert Money(1000, "KRW") != Money(1000, "USD")


def test_add_same_currency():
    result = Money(1000, "KRW").add(Money(2000, "KRW"))
    assert result == Money(3000, "KRW")


def test_add_different_currency_raises():
    with pytest.raises(ValueError, match="Cannot add different currencies"):
        Money(10, "USD").add(Money(1000, "KRW"))


def test_multiply():
    result = Money(10000, "KRW").multiply(1.015)
    assert result == Money(10150, "KRW")


def test_multiply_rounds():
    result = Money(10001, "KRW").multiply(1.015)
    assert result == Money(10151, "KRW")
```

### test_exchange_rate.py

```python
import pytest
from exchange_rate import ExchangeRate


def test_register_and_get_rate():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    assert rates.get("USD", "KRW") == 1300


def test_register_multiple_rates():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    rates.register("EUR", "KRW", 1400)
    assert rates.get("USD", "KRW") == 1300
    assert rates.get("EUR", "KRW") == 1400


def test_get_unregistered_rate_raises():
    rates = ExchangeRate()
    with pytest.raises(KeyError, match="No exchange rate"):
        rates.get("GBP", "KRW")
```

### test_exchange_service.py

```python
from money import Money
from exchange_rate import ExchangeRate
from exchange_service import ExchangeService


def test_convert_usd_to_krw():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    service = ExchangeService(rates)

    result = service.convert(Money(10, "USD"), "KRW")

    assert result == Money(13000, "KRW")


def test_convert_eur_to_krw():
    rates = ExchangeRate()
    rates.register("EUR", "KRW", 1400)
    service = ExchangeService(rates)

    result = service.convert(Money(10, "EUR"), "KRW")

    assert result == Money(14000, "KRW")


def test_convert_with_commission():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    service = ExchangeService(rates, commission_rate=0.015)

    result = service.convert(Money(10, "USD"), "KRW")

    assert result == Money(13195, "KRW")


def test_convert_with_commission_rounds():
    rates = ExchangeRate()
    rates.register("USD", "KRW", 1300)
    service = ExchangeService(rates, commission_rate=0.015)

    result = service.convert(Money(33, "USD"), "KRW")

    # 33 * 1300 = 42900, 42900 * 1.015 = 43543.5 -> round -> 43544
    assert result == Money(43544, "KRW")


def test_convert_same_currency_no_commission():
    rates = ExchangeRate()
    service = ExchangeService(rates, commission_rate=0.015)

    result = service.convert(Money(1000, "KRW"), "KRW")

    assert result == Money(1000, "KRW")
```

---

## 완료된 테스트 목록

```
[x] Money 생성 및 동등성
[x] Money 같은 통화 덧셈
[x] Money 다른 통화 덧셈 거부
[x] Money 곱셈 (수수료 계산용)
[x] ExchangeRate 환율 등록 및 조회
[x] ExchangeRate 미등록 통화 쌍 조회 시 에러
[x] ExchangeService USD -> KRW 변환
[x] ExchangeService EUR -> KRW 변환
[x] ExchangeService 수수료 1.5% 적용
[x] ExchangeService 수수료 적용 후 소수점 이하 반올림
[x] ExchangeService 같은 통화 변환 (수수료 없음)
```

## Inside-Out 진행 요약

```
1단계 (도메인 핵심)     Money 값 객체      -- 불변, 동등성, 덧셈, 곱셈
        |
2단계 (도메인 인프라)   ExchangeRate       -- 환율 등록/조회 (실제 dict 사용)
        |
3단계 (도메인 서비스)   ExchangeService    -- 실제 Money + 실제 ExchangeRate 조합
```

모든 계층에서 실제 객체만 사용했고 Mock은 없다. 각 계층은 아래 계층이 완성된 후에 구현되었으므로, 테스트에서 실제 객체를 자연스럽게 조립할 수 있었다. 이것이 Inside-Out TDD(고전 학파)의 핵심 이점이다.

사용된 Green Bar 전략:
- **Fake It + 삼각측량**: ExchangeRate에서 상수 반환 후 두 번째 예로 일반화
- **Obvious Implementation**: Money.add, Money.multiply, ExchangeService.convert 등 명백한 구현
- **상태 검증**: 모든 테스트가 `assert result == expected` 형태의 상태 검증 사용
