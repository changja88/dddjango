# TDD 디자인 패턴 레퍼런스

TDD의 각 단계(테스트 작성, 리팩토링)에서 사용되는 디자인 패턴과 Python 구현 예제를 정리한다.

---

## 패턴-단계 매핑 테이블

| 패턴 | 테스트 작성 | 리팩토링 |
|------|:----:|:----:|
| 커맨드 | O | |
| 값 객체 | O | |
| 널 객체 | | O |
| 템플릿 메서드 | | O |
| 플러거블 객체 | | O |
| 플러거블 셀렉터 | | O |
| 팩토리 메서드 | O | O |
| 임포스터 | O | O |
| 컴포지트 | O | O |
| 수집 매개 변수 | O | O |

---

## 값 객체 (Value Object)

객체가 생성된 이후 그 값이 절대 변하지 않게 하여 별칭 문제가 발생하지 않게 한다.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def plus(self, other: "Money") -> "Money":
        assert self.currency == other.currency
        return Money(self.amount + other.amount, self.currency)


def test_money_immutable():
    five = Money(5, "USD")
    ten = five.plus(Money(5, "USD"))
    assert ten == Money(10, "USD")
    assert five == Money(5, "USD")  # 원본 불변
```

---

## 널 객체 (Null Object)

특별한 상황을 표현하는 새로운 객체를 만들어, 다른 정상적인 상황을 나타내는 객체와 동일한 프로토콜을 제공한다.

```python
class SecurityManager:
    def can_write(self, path: str) -> None:
        # 권한 검사 로직
        ...


class LaxSecurity:
    """널 객체: 보안 검사를 하지 않는 SecurityManager"""
    def can_write(self, path: str) -> None:
        pass  # 항상 허용


def get_security_manager() -> SecurityManager:
    if _security is None:
        return LaxSecurity()  # null 대신 널 객체 반환
    return _security
```

---

## 팩토리 메서드 (Factory Method)

생성자를 쓰는 대신 일반 메서드에서 객체를 생성하여 유연성을 확보한다.

```python
class Money:
    @staticmethod
    def dollar(amount: int) -> "Money":
        return Money(amount, "USD")

    @staticmethod
    def franc(amount: int) -> "Money":
        return Money(amount, "CHF")


def test_multiplication():
    five = Money.dollar(5)
    assert five.times(2) == Money.dollar(10)
```

---

> 출처: Kent Beck, 테스트주도 개발 §10
