# 유연한 설계 (Supple Design)

> 출처: Evans 파란책 Chapter 10

Evans가 제시하는 모델 코드의 품질 패턴 6가지다.

## 4.1 의도를 드러내는 인터페이스 (Intention-Revealing Interfaces)

클래스와 메서드의 이름이 **무엇을 하는지**(what)를 드러내야 하며, **어떻게 하는지**(how)는 숨겨야 한다.

```python
@dataclass(frozen=True)
class Paint:
    red: int
    yellow: int
    blue: int

    # 나쁜 예: 이름이 구현 방식을 드러냄
    # def add_rgb_values(self, other: "Paint") -> "Paint": ...

    # 좋은 예: 의도를 드러냄 -- "페인트를 혼합한다"
    def mix_with(self, other: "Paint") -> "Paint":
        """두 페인트를 혼합하여 새로운 색을 만든다"""
        return Paint(
            red=min(self.red + other.red, 255),
            yellow=min(self.yellow + other.yellow, 255),
            blue=min(self.blue + other.blue, 255),
        )
```

## 4.2 부작용 없는 함수 (Side-Effect-Free Functions)

가능한 한 많은 도메인 로직을 부작용 없는 함수로 배치하라. 값 객체의 메서드가 대표적이다.

```python
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

    def add(self, other: "Money") -> "Money":
        """부작용 없는 함수: 기존 객체를 변경하지 않고 새 객체를 반환"""
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)
```

## 4.3 단언 (Assertions)

연산의 사후 조건(post-condition)과 클래스의 불변식(invariant)을 명시적으로 선언한다.

```python
@dataclass
class BankAccount:
    account_id: str
    _balance: int = 0

    def deposit(self, amount: int) -> None:
        old_balance = self._balance
        self._balance += amount
        assert self._balance == old_balance + amount, "입금 후 잔액 불일치"
        assert self._balance >= 0, "잔액은 음수가 될 수 없다"
```

## 4.4 개념적 윤곽 (Conceptual Contours)

도메인의 자연스러운 경계선을 따라 설계를 분해한다. **"함께 변하는 것은 함께 두고, 따로 변하는 것은 분리하라."**

## 4.5 독립형 클래스 (Standalone Classes)

클래스 간 결합을 최소화하여 각 클래스를 독립적으로 이해할 수 있게 하라. 모든 불필요한 의존성을 제거하면 개별 개념의 복잡성이 크게 줄어든다.

## 4.6 연산의 닫힘 (Closure of Operations)

반환 타입이 인자의 타입과 동일한 연산을 정의하면, 해당 타입의 인스턴스 집합 안에서 연산이 "닫혀" 있게 된다.

```python
@dataclass(frozen=True)
class Color:
    """연산의 닫힘 예시: Color + Color -> Color"""
    r: int
    g: int
    b: int

    def blend(self, other: "Color") -> "Color":
        """Color 타입의 연산이 Color 타입으로 닫혀 있다"""
        return Color(
            r=(self.r + other.r) // 2,
            g=(self.g + other.g) // 2,
            b=(self.b + other.b) // 2,
        )

    def invert(self) -> "Color":
        """단항 연산도 닫힘: Color -> Color"""
        return Color(r=255 - self.r, g=255 - self.g, b=255 - self.b)
```
