# TDD 개발 방법론 가이드

## P1 Source Sufficiency

| field | value |
|---|---|
| purpose | TDD methodology decisions: test list, Red-Green-Refactor, inside-out/outside-in choice, acceptance/unit loop, state vs behavior verification, refactoring checkpoints, and AI-assisted TDD guardrails. |
| use when | The work asks how to drive implementation through failing tests, choose TDD loop shape, or manage AI-assisted implementation with tests as executable specification. |
| exclude/handoff | Do not use for detailed pytest fixture/mock/factory mechanics, Django API TestClient mechanics, DB concurrency tests, or source governance; hand those to owning references. |
| core criteria | Write the smallest meaningful failing test first; make it pass with minimal code; refactor only on green; prefer tests resilient to refactoring; treat AI-generated code as untrusted until tests and human review validate it. |
| source priority | 2 primary TDD/testing books and Fowler/Meszaros material; 1 official tool docs only where tool behavior is discussed; 3 reputable engineering articles; 4 recent AI-assisted TDD articles are provisional and cannot prove eval completion. |
| P1 classification | provisional: AI-assisted TDD guidance is usable for cautious skill wording, but not as P5/P6/P8 completion evidence. |

---

## 1. TDD 핵심 철학

### 1.1 TDD의 목표 [테스트주도 개발]

TDD의 궁극적 목표는 **작동하는 깔끔한 코드(clean code that works)** 이다.

- 예측 가능한 개발 방법이다. 끊임없이 발생할 버그에 대해 걱정하지 않고, 일이 언제 마무리될지 알 수 있다
- 코드가 가르쳐주는 모든 교훈을 학습할 기회를 갖게 된다. 처음 생각나는 대로 후딱 완료해 버리면 더 나은 것에 대해 생각할 기회를 잃게 된다

### 1.2 TDD를 해야 하는 이유: 용기 [테스트주도 개발]

TDD는 프로그래밍하면서 나타나는 **두려움을 관리하는 방법**이다.

- 두려움이란 "정말 어려운 문제라서 시작 단계인 지금은 어떻게 마무리될지 알 수 없군"하고 생각하는 합리적인 두려움을 말한다
- TDD란 프로그래밍 도중 내린 결정과 그 결정에 대한 피드백 사이의 간격을 인지하고, 이 간격을 통제할 수 있게 해주는 기술이다
- 단, 보안과 동시성은 TDD만으로 목표 달성을 기계적으로 보여주기 부족한 주제이다

---

## 2. TDD 사이클 (Red-Green-Refactor)

### 2.1 기본 사이클 [테스트주도 개발]

```
Red   --> 작은 테스트를 하나 추가하고 실패하는 것을 확인한다
Green --> 테스트를 통과시키기 위해 최소한의 코드를 작성한다
Refactor --> 중복을 제거하고 코드를 정리한다
```

상세 단계:

1. **테스트를 작성한다** -- 마음속에 있는 오퍼레이션이 코드에 어떤 식으로 나타나길 원하는지 생각해보라. 이야기를 써내려가는 것이다
2. **실행 가능하게 만든다** -- 빨리 초록 막대를 보는 것이 가장 중요하다. 깔끔한 해법이 명백히 보인다면 그것을 입력하라. 몇 분 걸릴 것 같으면 일단 적어 놓은 뒤에 원래 문제(초록 막대를 보는 것)로 돌아오자
3. **올바르게 만든다** -- 시스템이 작동하므로 직전에 저질렀던 죄악을 수습하자. 중복을 제거하고 초록 막대로 되돌리자

핵심: '작동하는 깔끔한 코드'에서 **작동하는 것부터 먼저 해결**하는 나누어서 정복하는(divide and conquer) 방식이다.

### 2.2 pytest로 보는 TDD 사이클

```python
# --- Red: 실패하는 테스트 작성 ---
def test_add():
    assert add(3, 4) == 7  # NameError: add가 아직 없다


# --- Green: 최소한의 구현 ---
def add(a, b):
    return 7  # 가짜로 구현하기 (상수 반환)


# --- Refactor: 올바른 구현으로 리팩토링 ---
def add(a, b):
    return a + b
```

---

## 3. TDD 학파 비교: 고전 학파 vs 런던 학파

### 3.1 두 학파의 기원과 핵심 차이 [Fowler - Mocks Aren't Stubs]

Martin Fowler는 "Mocks Aren't Stubs" 아티클에서 TDD의 두 진영을 명확히 구분한다.

| 구분 | 고전 학파 (Detroit/Chicago) | 런던 학파 (London/Mockist) |
|------|---------------------------|--------------------------|
| 별칭 | Classicist, Inside-Out, Bottom-Up | Mockist, Outside-In, Top-Down |
| 단위(Unit) 정의 | 모듈 단위 (단일 클래스 ~ 밀접한 클래스 집합) | 단일 클래스 |
| 협력 객체 처리 | 실제 객체 사용 | Mock으로 대체 |
| 검증 방식 | **상태 검증** (State Verification) | **행위 검증** (Behavior Verification) |
| 테스트 관점 | 블랙박스 테스트 | 화이트박스 테스트 |
| 개발 방향 | 도메인 내부에서 외부로 | 외부 인터페이스에서 내부로 |
| 리팩토링 내성 | 높음 (구현 변경에 강함) | 낮음 (구현 변경 시 테스트도 변경) |
| 대표 인물 | Kent Beck | Steve Freeman, Nat Pryce |

### 3.2 상태 검증 vs 행위 검증 [Fowler - Mocks Aren't Stubs]

```python
import pytest
from unittest.mock import Mock, call


# === 상태 검증 (고전 학파) ===
class Order:
    def __init__(self):
        self.items: list[str] = []

    def add_item(self, item: str) -> None:
        self.items.append(item)

    def item_count(self) -> int:
        return len(self.items)


def test_order_state_verification():
    """상태 검증: 행위 실행 후 객체의 '상태'를 확인한다."""
    order = Order()
    order.add_item("사과")
    order.add_item("바나나")

    # 상태(state)를 검증
    assert order.item_count() == 2
    assert "사과" in order.items


# === 행위 검증 (런던 학파) ===
class OrderService:
    def __init__(self, repository, notifier):
        self.repository = repository
        self.notifier = notifier

    def place_order(self, user_id: str, items: list[str]) -> None:
        order = {"user_id": user_id, "items": items}
        self.repository.save(order)
        self.notifier.send(user_id, f"주문 {len(items)}건 접수")


def test_order_behavior_verification():
    """행위 검증: 협력 객체에 올바른 '메시지'를 보냈는지 확인한다."""
    mock_repo = Mock()
    mock_notifier = Mock()
    service = OrderService(mock_repo, mock_notifier)

    service.place_order("user-1", ["사과", "바나나"])

    # 행위(behavior)를 검증
    mock_repo.save.assert_called_once_with(
        {"user_id": "user-1", "items": ["사과", "바나나"]}
    )
    mock_notifier.send.assert_called_once_with("user-1", "주문 2건 접수")
```

### 3.3 Inside-Out vs Outside-In TDD

두 접근법은 배타적이지 않다. 실전에서는 상황에 따라 혼합하는 것이 효과적이다.

**Inside-Out TDD (고전 학파)**

도메인 모델의 핵심부터 시작하여 바깥으로 나아간다. Mock이 거의 필요 없다.

```python
# 1단계: 도메인 핵심 (Money) 먼저 구현
def test_money_addition():
    five = Money(5, "USD")
    ten = Money(10, "USD")
    assert five.plus(ten) == Money(15, "USD")


# 2단계: 도메인 서비스 구현 (실제 Money 사용)
def test_exchange_service():
    service = ExchangeService(rate=1100)
    result = service.convert(Money(10, "USD"), "KRW")
    assert result == Money(11000, "KRW")


# 3단계: API 계층 구현 (실제 서비스 사용)
def test_exchange_endpoint(client):
    response = client.post("/exchange", json={"amount": 10, "from": "USD", "to": "KRW"})
    assert response.json()["amount"] == 11000
```

**Outside-In TDD (런던 학파)**

사용자 인터페이스(외부)에서 시작하여 안쪽으로 파고든다. Mock으로 아직 구현되지 않은 계층을 대체한다.

```python
# 1단계: 외부 인터페이스(API)부터 시작, 내부는 Mock
def test_exchange_endpoint(client, mocker):
    mock_service = mocker.patch("app.exchange_service")
    mock_service.convert.return_value = Money(11000, "KRW")

    response = client.post("/exchange", json={"amount": 10, "from": "USD", "to": "KRW"})

    assert response.json()["amount"] == 11000
    mock_service.convert.assert_called_once()


# 2단계: 서비스 계층 구현, 하위는 Mock
def test_exchange_service(mocker):
    mock_rate_provider = mocker.patch("app.rate_provider")
    mock_rate_provider.get_rate.return_value = 1100

    service = ExchangeService(mock_rate_provider)
    result = service.convert(Money(10, "USD"), "KRW")

    assert result == Money(11000, "KRW")


# 3단계: 가장 안쪽 도메인 구현
def test_money_addition():
    five = Money(5, "USD")
    ten = Money(10, "USD")
    assert five.plus(ten) == Money(15, "USD")
```

### 3.4 실전 권고: 상황별 선택

| 상황 | 권장 접근법 |
|------|-----------|
| 순수 도메인 로직 | 고전 학파 (실제 객체, 상태 검증) |
| 외부 시스템 연동 (DB, API) | 런던 학파 (Mock, 행위 검증) |
| 새로운 기능의 전체 설계 탐색 | Outside-In (런던 학파) |
| 복잡한 알고리즘 구현 | Inside-Out (고전 학파) |

---

## 4. 좋은 단위 테스트의 4대 특성

### 4.1 네 가지 기둥 (Four Pillars) [Khorikov - Unit Testing Principles]

Vladimir Khorikov는 좋은 단위 테스트의 가치를 평가하는 4가지 기둥을 제시한다.

```
                    좋은 단위 테스트
                          |
        +--------+--------+--------+--------+
        |        |        |        |        |
    회귀 방지   리팩토링   빠른     유지
    (Protection  내성     피드백   보수성
     against   (Resistance (Fast   (Maintain-
     Regressions) to      Feedback) ability)
               Refactoring)
```

| 기둥 | 설명 | 측정 기준 |
|------|------|----------|
| **회귀 방지** | 테스트가 버그를 얼마나 잘 잡는가 | 코드 커버리지, 실행되는 코드량 |
| **리팩토링 내성** | 내부 구현을 바꿔도 테스트가 깨지지 않는가 | 거짓 양성(false positive) 빈도 |
| **빠른 피드백** | 테스트가 빠르게 실행되는가 | 실행 시간 |
| **유지보수성** | 테스트를 이해하고 실행하기 쉬운가 | 테스트 크기, 외부 의존성 수 |

### 4.2 회귀 방지의 위상 [Khorikov]

회귀 방지(Protection against Regressions)는 단순히 버그 발견 시 사후에 작성하는 회귀 테스트를 넘어, **모든 테스트가 처음부터 갖춰야 할 설계 원칙**이다. 테스트 설계 시점부터 "이 테스트가 향후 회귀를 얼마나 잘 방지하는가"를 고려해야 한다.

실전 적용: 시스템 장애가 보고될 때에도 가장 먼저 할 일은 그 장애로 인하여 실패하는 테스트, 그리고 통과할 경우엔 장애가 수정되었다고 볼 수 있는 테스트를 작성하는 것이다. [테스트주도 개발]

```python
def test_division_by_zero_returns_error():
    """버그 리포트 #42: 0으로 나눌 때 ZeroDivisionError 대신 None 반환됨"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

### 4.3 리팩토링 내성 [Khorikov]

리팩토링 내성(Resistance to Refactoring)은 독립적 품질 기둥이다. 거짓 양성(false positive) 빈도로 측정하며, Mock 과용이 구현에 결합된 테스트를 만들어 "내부 구현을 바꿀 때마다 테스트가 깨지는" 문제를 야기한다.

### 4.4 CAP 정리와의 유사성 [Khorikov]

Khorikov의 핵심 통찰: 처음 세 기둥(회귀 방지, 리팩토링 내성, 빠른 피드백)은 **상호 배타적**이다. 세 가지를 동시에 최대화할 수 없다.

```python
# === 회귀 방지 높음 + 리팩토링 내성 높음 = 느린 피드백 (통합 테스트) ===
def test_end_to_end_order_flow(real_db, real_email_service):
    """실제 객체를 사용하여 버그를 잘 잡고 리팩토링에도 강하지만, 느리다."""
    service = OrderService(real_db, real_email_service)
    service.place_order("user-1", ["사과"])

    orders = real_db.query("SELECT * FROM orders WHERE user_id = 'user-1'")
    assert len(orders) == 1


# === 회귀 방지 높음 + 빠른 피드백 = 리팩토링 내성 낮음 (과도한 Mock) ===
def test_over_mocked_order(mocker):
    """Mock으로 빠르고 버그도 잡지만, 구현 변경 시 테스트도 깨진다."""
    mock_db = mocker.patch("app.db")
    mock_email = mocker.patch("app.email")
    service = OrderService(mock_db, mock_email)

    service.place_order("user-1", ["사과"])

    # 내부 구현에 결합된 검증 -> 리팩토링하면 깨진다
    mock_db.execute.assert_called_with(
        "INSERT INTO orders (user_id, items) VALUES (?, ?)",
        ("user-1", '["사과"]'),
    )


# === 리팩토링 내성 높음 + 빠른 피드백 = 회귀 방지 낮음 (너무 단순한 테스트) ===
def test_trivial():
    """빠르고 리팩토링에 강하지만, 의미 있는 버그를 잡지 못한다."""
    assert 1 + 1 == 2
```

### 4.5 세 가지 테스트 스타일 [Khorikov]

| 스타일 | 검증 대상 | 회귀 방지 | 리팩토링 내성 | 유지보수성 |
|--------|----------|:---------:|:-----------:|:---------:|
| **출력 기반** (Output-based) | 반환값 | 높음 | 높음 | 높음 |
| **상태 기반** (State-based) | 객체 상태 | 높음 | 높음 | 중간 |
| **통신 기반** (Communication-based) | 메서드 호출 | 중간 | 낮음 | 낮음 |

Khorikov의 권고: **출력 기반 > 상태 기반 > 통신 기반** 순으로 선호하라. 가능하면 비즈니스 로직을 순수 함수로 추출하여 출력 기반 테스트를 극대화하라.

```python
# === 출력 기반 테스트 (가장 권장) ===
def calculate_discount(price: float, is_vip: bool) -> float:
    """순수 함수: 부수효과 없이 입력만으로 출력 결정."""
    return price * 0.8 if is_vip else price


def test_output_based():
    """SUT의 반환값만 검증한다. 가장 리팩토링에 강하다."""
    assert calculate_discount(1000, is_vip=True) == 800.0
    assert calculate_discount(1000, is_vip=False) == 1000.0


# === 상태 기반 테스트 ===
class ShoppingCart:
    def __init__(self):
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)


def test_state_based():
    """행위 실행 후 SUT의 상태를 검증한다."""
    cart = ShoppingCart()
    cart.add("사과")

    assert cart.items == ["사과"]  # 상태 검증


# === 통신 기반 테스트 ===
def test_communication_based(mocker):
    """SUT가 협력 객체에 보내는 메시지를 검증한다."""
    mock_sender = mocker.Mock()
    service = NotificationService(mock_sender)

    service.notify("user@test.com", "안녕하세요")

    mock_sender.send.assert_called_once_with("user@test.com", "안녕하세요")
```

### 4.6 테스트 품질 3대 속성 [Osherove - The Art of Unit Testing]

| 속성 | 의미 | 위반 징후 |
|------|------|----------|
| **신뢰성** (Trustworthiness) | 테스트 결과를 믿을 수 있다 | 테스트가 실패해도 무시하게 됨 |
| **유지보수성** (Maintainability) | 코드 변경 시 테스트 수정이 적다 | 사소한 변경에도 테스트가 대량으로 깨짐 |
| **가독성** (Readability) | 테스트 의도를 빠르게 파악할 수 있다 | 테스트 코드를 읽는 데 원본보다 오래 걸림 |

---

## 5. 빨간 막대 패턴 (테스트를 언제, 어디에 작성할 것인가) [테스트주도 개발]

### 5.1 테스트 목록

시작하기 전에 작성해야 할 **테스트 목록을 모두 적어 둘 것**. 테스트 코드는 테스트 대상이 되는 코드를 작성하기 직전에 작성하는 것이 좋다.

테스트 목록은 대표 예시만 나열하는 메모가 아니라, 행위와 정책의 경계를 드러내는 작업 목록이다. 사용자가 경계 예시를 하나만 말했더라도 그 예시가 전체 테스트 범위를 닫는 것은 아니다. 할인율, 최소 주문 금액, 수량 제한, 유효 기간처럼 결과가 바뀌는 경계가 있으면, 경계 자체와 결과가 달라지는 가장 가까운 바깥쪽 값 또는 보완 상태를 함께 적는다.

여러 독립 결정축이 결합된 정책에서는 각 축의 허용 사례와 거부 사례를 분리한다. 예를 들어 쿠폰 정책에서 만료일, 사용 여부, 활성 상태, 최소 주문 금액이 각각 결과를 바꾼다면 "이미 사용됨" 거부 사례가 "만료일 다음 날" 거부 사례를 대신하지 않는다. 유효 기간이 포함형이면 마지막 유효일은 허용 사례로, 그 다음 날은 거부 사례로 테스트 목록에 남긴다.

```python
def test_coupon_accepts_on_expiration_day():
    coupon = Coupon(expires_on=date(2026, 5, 21))
    assert coupon.can_apply(today=date(2026, 5, 21)) is True


def test_coupon_rejects_day_after_expiration():
    coupon = Coupon(expires_on=date(2026, 5, 21))
    assert coupon.can_apply(today=date(2026, 5, 22)) is False
```

### 5.2 한 단계 테스트

목록에서 다음 테스트를 고를 때 기준: **새로운 무언가를 가르쳐 줄 수 있으며, 구현할 수 있다는 확신이 드는 테스트**를 고른다. 아는 것에서 모르는 것으로 방향을 잡는다.

### 5.3 시작 테스트

오퍼레이션이 **아무 일도 하지 않는 경우를 먼저 테스트**한다. 뭔가를 가르쳐 줄 수 있으면서도 빠르게 구현할 수 있는 테스트를 선택하라.

```python
def test_empty_cart_total():
    cart = ShoppingCart()
    assert cart.total() == 0  # 가장 단순한 경우부터 시작
```

### 5.4 설명 테스트

자동화된 테스트가 널리 쓰이게 하려면 **테스트를 통해 설명을 요청하고, 테스트를 통해 설명**해야 한다.

---

## 6. 초록 막대 패턴 (테스트를 통과시키는 전략) [테스트주도 개발]

### 6.1 가짜로 구현하기 (Fake It)

실패하는 테스트를 만든 후 첫 번째 구현은 **상수를 반환**하게 하여 일단 통과시킨다. 그 후 상수를 변수를 사용하는 수식으로 변경한다.

```python
# 단계 1: 상수 반환
def summary(run_count, fail_count):
    return "1 run, 0 failed"

# 단계 2: 일부 변수화
def summary(run_count, fail_count):
    return f"{run_count} run, 0 failed"

# 단계 3: 완전한 구현
def summary(run_count, fail_count):
    return f"{run_count} run, {fail_count} failed"
```

두 가지 효과:

- **심리학적 효과**: 초록 막대 상태에서 확신을 갖고 리팩토링할 수 있다
- **범위 조절**: 하나의 구체적인 예에서 시작해서 일반화하면 쓸데없는 고민으로 혼동하는 일을 예방한다

### 6.2 삼각측량 (Triangulation)

추상화 과정을 테스트로 주도할 때 최대한 보수적으로 하는 방법: **예가 두 개 이상일 때에만 추상화**한다.

```python
def test_plus():
    assert plus(3, 1) == 4
    assert plus(3, 4) == 7  # 두 번째 예에서 추상화


def plus(a, b):
    return a + b  # 두 예제가 있으므로 비로소 일반화
```

어떻게 올바르게 추상화할 것인지 감잡기 어려울 때 사용하면 좋다.

### 6.3 명백한 구현 (Obvious Implementation)

단순한 연산들은 그냥 구현해버린다. 어떻게 구현해야 할지 확신이 들면 그렇게 하는 것이 좋다.

---

## 7. 테스팅 패턴 [테스트주도 개발]

### 7.1 테스트 격리

각각의 테스트는 서로 독립적이어야 하며, **실행 순서에서도 독립적**이어야 한다. 이를 달성하기 위한 구체적 전략은 **공유 상태 제거**이다. [xUnit Test Patterns]

전역 공유 상태는 Erratic Test(불안정 테스트)의 근본 원인이다. pytest fixture를 사용하여 테스트별 독립적인 상태를 생성한다.

```python
# === 나쁨: 공유 상태로 인한 불안정 ===
shared_list = []  # 전역 공유 상태 -> 테스트 순서에 따라 결과 달라짐

def test_add_item_erratic():
    shared_list.append("item")
    assert len(shared_list) == 1  # 다른 테스트가 먼저 실행되면 실패


# === 좋음: 각 테스트에서 독립적인 상태 사용 ===
@pytest.fixture
def fresh_list():
    return []

def test_add_item_stable(fresh_list):
    fresh_list.append("item")
    assert len(fresh_list) == 1  # 항상 성공
```

### 7.2 AAA 패턴: Arrange-Act-Assert [Osherove]

테스트의 최종 코드 구조는 AAA 패턴을 따른다. 사고 과정에서는 Assert First(단언 우선)로 목적부터 정하되, 최종 코드는 위에서 아래로 자연스럽게 읽히도록 정리한다.

> Assert First 사고법 [테스트주도 개발]: 완료 시 통과해야 할 단언부터 머릿속에 떠올리고, "이 값은 어디서 오는가?" 를 역추적하며 필요한 설정을 도출한다.

```python
def test_transfer_funds():
    # --- Arrange: 테스트에 필요한 객체와 상태를 준비한다 ---
    source = Account(balance=5000)
    target = Account(balance=1000)
    service = TransferService()

    # --- Act: 테스트 대상 행위를 실행한다 (단 하나만) ---
    result = service.transfer(source, target, amount=2000)

    # --- Assert: 기대 결과를 검증한다 ---
    assert result.success is True
    assert source.balance == 3000
    assert target.balance == 3000
```

### 7.3 테스트 데이터

- 테스트를 읽을 때 쉽고 따라가기 좋을 만한 데이터를 사용하라
- 데이터 간에 차이가 있다면 그 속에 **어떤 의미가 있어야** 한다
- 동일한 상수를 여러 의미로 쓰지 마라 (예: `plus(2, 2)` 대신 `plus(2, 3)`)

### 7.4 명백한 데이터

테스트 자체에 예상되는 값과 실제 값을 포함하고, 이 둘 사이의 **관계를 드러내기 위해 노력**하라.

```python
# 나쁨: 49.25가 왜 정답인지 알 수 없다
assert exchange(100, "USD", "GBP") == 49.25

# 좋음: 계산 과정이 드러난다
assert exchange(100, "USD", "GBP") == 100 / 2 * (1 - 0.015)
```

### 7.5 테스트 명명 규칙 [Osherove]

```
[테스트 대상 단위]_[상태/조건]_[기대 행위]
```

```python
def test_divide__divisor_is_zero__raises_value_error():
    """divide 함수가 0으로 나눌 때 ValueError를 발생시킨다."""
    with pytest.raises(ValueError, match="0으로 나눌 수 없습니다"):
        divide(10, 0)


def test_withdraw__amount_exceeds_balance__returns_insufficient_funds():
    """출금액이 잔액을 초과하면 잔액 부족 오류를 반환한다."""
    account = Account(balance=1000)
    result = account.withdraw(1500)
    assert result.error == "잔액 부족"
```

### 7.6 Mock보다 출력·상태 검증을 우선한다 [Khorikov]

TDD로 구현을 몰아갈 때 검증 방식은 **출력 기반 > 상태 기반 > 통신 기반(Mock)** 순으로 선호한다. Mock은 외부 의존성(DB, API, 파일시스템, 결제, 알림 등) 격리에만 쓰고, 핵심 로직은 실제 객체의 출력/상태로 검증한다. 이는 무엇을 어떻게 검증할지에 대한 실천 원칙이며, Mock 우선순위표와 구체적 사용법(`Mock(spec=)`, `side_effect`, 호출/순서 검증)은 작성법이므로 `workspace/reference/implementation-test/reference/final.md` §7을 따른다. Mock이 필요한 경계에서의 *도구*는 pytest-mock `mocker` 픽스처다(자동 teardown) — 고전 학파 기본(§3 실제 협력 객체)은 불변이고 *도구만* 격상한다(무엇을·얼마나 mock할지는 위 우선순위가 소유).

### 7.7 깨진 테스트 / 깨끗한 체크인 [테스트주도 개발]

- **혼자 프로그래밍**: 테스트가 깨진 상태로 끝마치면 다음에 어디서부터 시작할지 좋은 단서가 된다
- **팀 프로그래밍**: 테스트가 성공한 상태로 끝마친다

---

## 8. 테스트 더블 분류 체계

테스트 더블의 상세 분류와 Python 구현은 `workspace/reference/implementation-test/reference/final.md`를 참조한다.

---

## 9. Outside-In TDD와 이중 루프 [Freeman & Pryce - GOOS]

### 9.1 이중 루프 TDD (Double Loop TDD)

"Growing Object-Oriented Software, Guided by Tests"의 핵심 개념. 바깥 루프(인수 테스트)와 안쪽 루프(단위 테스트)를 동시에 운용한다.

```
+---------------------------------------------------+
|  바깥 루프: 인수 테스트 (Acceptance Test)            |
|  RED -> (아직 기능이 없으므로 실패)                   |
|                                                     |
|   +-------------------------------------------+    |
|   |  안쪽 루프: 단위 테스트 (Unit Test)          |    |
|   |  RED -> GREEN -> REFACTOR (반복)            |    |
|   +-------------------------------------------+    |
|                                                     |
|  GREEN -> (단위 테스트를 충분히 통과시키면            |
|            인수 테스트도 통과한다)                    |
+---------------------------------------------------+
```

```python
# === 바깥 루프: 인수 테스트 (End-to-End) ===
def test_acceptance_user_registration(client):
    """전체 시스템을 블랙박스로 취급한다."""
    response = client.post("/register", json={
        "email": "new@example.com",
        "password": "secure123",
    })
    assert response.status_code == 201

    # 실제로 로그인이 되는지 확인
    login_response = client.post("/login", json={
        "email": "new@example.com",
        "password": "secure123",
    })
    assert login_response.status_code == 200


# === 안쪽 루프: 단위 테스트 (Mock 사용) ===
def test_registration_service_saves_user(mocker):
    """서비스 계층이 repository에 올바르게 저장하는지 확인."""
    mock_repo = mocker.Mock()
    mock_hasher = mocker.Mock()
    mock_hasher.hash.return_value = "hashed_pw"

    service = RegistrationService(mock_repo, mock_hasher)
    service.register("new@example.com", "secure123")

    mock_repo.save.assert_called_once()
    saved_user = mock_repo.save.call_args[0][0]
    assert saved_user["email"] == "new@example.com"
    assert saved_user["password"] == "hashed_pw"
```

### 9.2 Walking Skeleton [Freeman & Pryce - GOOS]

GOOS의 첫 번째 단계: **가장 얇은 슬라이스의 실제 기능**을 구현하여 빌드, 배포, 테스트가 끝까지(end-to-end) 동작하는 것을 확인한다.

```python
# Walking Skeleton: 최소한의 end-to-end 경로

# 1. 가장 단순한 인수 테스트 작성
def test_walking_skeleton_health_check(client):
    """시스템이 기동되어 응답할 수 있는지 확인하는 가장 얇은 슬라이스."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# 이 테스트가 통과하려면:
# - 웹 서버 기동
# - 라우팅 설정
# - 응답 직렬화
# - 테스트 인프라 (클라이언트 fixture)
# 위의 모든 것이 동작해야 한다 -> 아키텍처 결정을 강제한다
```

### 9.3 Mock Roles, Not Objects [Freeman, Pryce, Mackinnon, Walnes -- OOPSLA 2004]

Mock의 대상은 구체적인 객체가 아니라 **역할(Role)** 이다. 프로덕션 코드는 구체 구현 클래스(예: `StripeGateway`, `SmtpSender`)가 아니라 역할(인터페이스)에 의존하고, 테스트는 그 역할을 Mock한다. 역할을 `Protocol`로 정의하고 `mocker.Mock(spec=...)`로 대체하는 구체 구현은 작성법이므로 `workspace/reference/implementation-test/reference/final.md` §7을 따른다.

### 9.4 Tell, Don't Ask 원칙 [Freeman & Pryce - GOOS]

> "객체에게 정보를 요청해서 우리가 답을 계산하지 말고, 우리가 진짜 원하는 것을 객체에게 말하라(Tell)."

```python
# --- 나쁨: Ask (정보를 가져와서 외부에서 판단) ---
class BadOrderProcessor:
    def process(self, order):
        if order.get_status() == "pending":
            if order.get_total() > 0:
                order.set_status("confirmed")
                self.notifier.send(order.get_email(), "확인됨")


# --- 좋음: Tell (객체에게 행위를 위임) ---
class GoodOrderProcessor:
    def process(self, order):
        order.confirm(self.notifier)  # 객체에게 "확인하라"고 말한다


class Order:
    def confirm(self, notifier):
        """주문 스스로가 확인 로직을 수행한다."""
        if self.status == "pending" and self.total > 0:
            self.status = "confirmed"
            notifier.send(self.email, "확인됨")
```

---

## 10. 디자인 패턴과 TDD [테스트주도 개발]

TDD의 각 단계에서 사용되는 디자인 패턴:

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

### 10.1 값 객체 (Value Object)

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

### 10.2 널 객체 (Null Object)

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

### 10.3 팩토리 메서드 (Factory Method)

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

## 11. 리팩토링 패턴 [테스트주도 개발]

### 11.1 차이점 일치시키기

비슷해 보이는 두 코드 조각을 합치려면, 두 코드가 **단계적으로 닮아가게끔 수정**한다. 완전히 동일해지면 둘을 합친다.

### 11.2 변화 격리하기

객체나 메서드의 일부만 바꾸려면, 일단 바꿔야 할 부분을 격리한다. 격리 방법에는 **메서드 추출하기**, 객체 추출하기, 메서드 객체 등이 있다.

### 11.3 데이터 이주시키기

표현 양식을 변경하려면 **일시적으로 데이터를 중복**시킨다.

내부에서 외부로의 변화 단계:

1. 새로운 포맷의 인스턴스 변수를 추가한다
2. 기존 포맷의 인스턴스 변수를 세팅하는 모든 부분에서 새로운 인스턴스 변수도 세팅하게 만든다
3. 기존 변수를 사용하는 모든 곳에서 새 변수를 사용하게 만든다
4. 기존 포맷을 제거한다
5. 새 포맷에 맞게 외부 인터페이스를 변경한다

```python
# 단계 1-2: 데이터 중복
class TestSuite:
    def __init__(self):
        self.tests = []

    def add(self, test):
        self.test = test        # 기존 (곧 제거)
        self.tests.append(test)  # 신규

    # 단계 3: 새 변수 사용
    def run(self, result):
        for test in self.tests:
            test.run(result)

    # 단계 4: self.test 제거 완료
```

### 11.4 메서드 추출하기

길고 복잡한 메서드의 일부분을 **별도의 메서드로 분리**해내고 이를 호출하게 한다.

```python
# Before
def generate_report(data):
    # 데이터 검증 (20줄)
    ...
    # 포맷팅 (30줄)
    ...
    # 출력 (10줄)
    ...

# After
def generate_report(data):
    validated = validate_data(data)
    formatted = format_report(validated)
    output_report(formatted)
```

### 11.5 메서드 인라인

너무 꼬여있거나 산재한 제어 흐름을 단순화하려면, 메서드를 호출하는 부분을 **호출될 메서드의 본문으로 교체**한다.

### 11.6 인터페이스 추출하기

오퍼레이션에 대한 두 번째 구현을 추가하려면, 공통되는 오퍼레이션을 담고 있는 **인터페이스(Protocol)**를 만든다.

```python
from typing import Protocol


class Repository(Protocol):
    def get(self, id: int) -> dict: ...
    def save(self, data: dict) -> None: ...


class PostgresRepository:
    def get(self, id: int) -> dict: ...
    def save(self, data: dict) -> None: ...


class InMemoryRepository:
    """테스트용 구현"""
    def __init__(self):
        self._store = {}

    def get(self, id: int) -> dict:
        return self._store[id]

    def save(self, data: dict) -> None:
        self._store[data["id"]] = data
```

### 11.7 메서드 옮기기

메서드를 원래 있어야 할 장소로 옮기려면, 어울리는 클래스에 메서드를 추가해주고 그것을 호출하게 하라.

### 11.8 메서드 객체

여러 개의 매개 변수와 지역 변수를 갖는 복잡한 메서드를 표현하려면, 메서드를 꺼내서 객체로 만든다.

---

## 12. 테스트 냄새 카탈로그 [Meszaros - xUnit Test Patterns]

### 12.1 행위 냄새 (Behavior Smells)

테스트를 실행할 때 발생하는 문제들.

| 냄새 | 설명 | 해결책 |
|------|------|--------|
| **Assertion Roulette** | 여러 단언 중 어느 것이 실패했는지 알기 어려움 | 각 단언에 메시지 추가, 테스트 분리 |
| **Erratic Test** | 같은 코드인데 때로 성공, 때로 실패 | 공유 상태 제거, 테스트 격리 |
| **Fragile Test** | 관련 없는 코드 변경에도 깨짐 | 구현이 아닌 행위에 대해 테스트 |
| **Frequent Debugging** | 테스트 실패 시 원인을 디버깅해야만 알 수 있음 | 테스트를 작게, 단언을 명확하게 |
| **Slow Test** | 전체 테스트 실행이 수 분~수 시간 소요 | 외부 의존성 제거, 병렬 실행 |
| **Manual Intervention** | 테스트 실행에 사람의 수동 개입 필요 | 완전 자동화 |

```python
# === Assertion Roulette (나쁨) ===
def test_user_creation_roulette():
    user = create_user("홍길동", "hong@test.com", 30)
    assert user.name == "홍길동"       # 이 줄이 실패? 아래 줄이 실패?
    assert user.email == "hong@test.com"
    assert user.age == 30
    assert user.is_active is True


# === Assertion Roulette 해결: 테스트 분리 ===
def test_user_has_correct_name():
    user = create_user("홍길동", "hong@test.com", 30)
    assert user.name == "홍길동"


def test_user_is_active_by_default():
    user = create_user("홍길동", "hong@test.com", 30)
    assert user.is_active is True
```

### 12.2 코드 냄새 (Code Smells)

테스트 코드 자체의 구조적 문제.

| 냄새 | 설명 |
|------|------|
| **Obscure Test** | 테스트를 읽어도 무엇을 테스트하는지 이해하기 어려움 |
| **Conditional Test Logic** | 테스트 안에 if/else, try/catch 등 분기 로직이 있음 |
| **Hard-Coded Test Data** | 테스트 데이터가 매직 넘버로 하드코딩되어 의미 불명 |
| **Test Code Duplication** | 여러 테스트에서 동일한 설정/검증 코드가 반복됨 |
| **Eager Test** | 하나의 테스트에서 너무 많은 조건을 검증하려 함 |

```python
# === Obscure Test (나쁨) ===
def test_x():
    r = f(42, True, None, "abc")
    assert r == 17  # 무엇을 테스트하는가?


# === Obscure Test 해결: 의도를 드러내는 이름과 변수 ===
def test_calculate_shipping_fee_for_domestic_order():
    weight_kg = 42
    is_fragile = True
    coupon = None
    destination = "서울"

    fee = calculate_shipping(weight_kg, is_fragile, coupon, destination)

    expected_fee = 17000  # 42kg * 400원 + 취급비 200원
    assert fee == expected_fee
```

---

## 13. 레거시 코드 다루기

레거시 코드 다루기는 `workspace/reference/discipline-cleancode/reference/final.md`를 참조한다.

---

## 14. Property-Based Testing

Property-Based Testing은 `workspace/reference/implementation-test/reference/final.md`를 참조한다.

---

## 15. Mutation Testing

Mutation Testing은 `workspace/reference/implementation-test/reference/final.md`를 참조한다.

---

## 16. BDD (Behavior-Driven Development) [Cucumber, pytest-bdd]

### 16.1 TDD와 BDD의 관계

BDD는 TDD의 **진화형**이다. TDD가 개발자 중심의 코드 정확성에 집중한다면, BDD는 비즈니스 요구사항을 자연어로 표현하여 이해관계자와의 소통을 중시한다.

```
TDD 진화 경로:
TDD (코드 정확성) -> ATDD (인수 테스트) -> BDD (행위 명세 + 소통)
```

| 구분 | TDD | BDD |
|------|-----|-----|
| 관점 | 개발자 중심 | 사용자/비즈니스 중심 |
| 명세 언어 | 프로그래밍 언어 | 자연어 (Gherkin) |
| 테스트 단위 | 함수/클래스 | 시나리오/행위 |
| 산출물 | 단위 테스트 | 살아있는 문서(living documentation) |
| 참여자 | 개발자 | 개발자 + 기획자 + QA |

pytest-bdd 구현 상세는 `workspace/reference/implementation-test/reference/final.md`를 참조한다.

---

## 17. TDD와 AI 코딩의 관계

### 17.1 TDD as Prompt Engineering

> "TDD는 프롬프트 엔지니어링이다. 테스트가 AI에게 '무엇을' 만들고 '언제 완료인지'를 알려준다."

TDD의 Red-Green-Refactor 사이클은 AI 코딩 도구와 자연스럽게 결합된다.

```
전통 TDD:     개발자가 테스트 작성 -> 개발자가 구현
AI 보조 TDD:  개발자가 테스트 작성 -> AI가 구현 제안 -> 개발자가 검증
TDAID:        Plan -> Red -> Green(AI) -> Refactor(AI+개발자) -> Validate
```

### 17.2 AI 보조 TDD 워크플로우

```python
# 1단계: 개발자가 명세로서의 테스트를 작성한다 (Red)
def test_parse_korean_date():
    """한국어 날짜 문자열을 파싱한다."""
    assert parse_date("2026년 4월 4일") == date(2026, 4, 4)
    assert parse_date("2026년 12월 25일") == date(2026, 12, 25)


def test_parse_korean_date_edge_cases():
    """엣지케이스를 포함한다."""
    with pytest.raises(ValueError):
        parse_date("잘못된 날짜")
    with pytest.raises(ValueError):
        parse_date("2026년 13월 1일")  # 13월은 없다

# 2단계: AI에게 구현을 요청한다 (Green)
# "위 테스트를 통과하는 parse_date 함수를 구현해줘"
# -> AI가 구현 제안

# 3단계: 개발자가 AI 구현을 검증하고 리팩토링한다 (Refactor)
# - 테스트가 통과하는가?
# - 코드가 의도대로인가?
# - 보안 문제나 환각(hallucination)이 없는가?
```

### 17.3 TDD가 AI 코딩에서 더 중요한 이유

| 위험 | TDD의 방어 효과 |
|------|---------------|
| AI 환각 (hallucinated code) | 실패하는 테스트가 잘못된 구현을 즉시 감지 |
| 의도와 다른 구현 | 테스트가 명세 역할을 하여 의도를 명시 |
| 보안 취약점 | 보안 테스트가 AI 생성 코드의 취약점 포착 |
| 과도한 신뢰 | Red-Green 사이클이 점진적 검증을 강제 |

### 17.4 Test-Driven AI Development (TDAID) 5단계

```
1. Plan     : 기능 요구사항을 테스트 목록으로 변환
2. Red      : 실패하는 테스트 작성 (개발자)
3. Green    : 테스트를 통과하는 구현 (AI 보조)
4. Refactor : 코드 품질 개선 (AI + 개발자 협업)
5. Validate : AI 생성 코드의 정확성, 보안, 성능 최종 검증
```

---

## 18. Python 테스트 생태계 심화

Python 테스트 도구 생태계는 `workspace/reference/implementation-test/reference/final.md`를 참조한다.

---

## 참고 문헌

| 출처 | 다룬 내용 |
|------|---------|
| 테스트주도 개발 (Kent Beck) | TDD 사이클, 빨간/초록 막대 패턴, 테스팅 패턴, 디자인 패턴, 리팩토링 |
| 파이썬코딩의기술 (Brett Slatkin) | TestCase, setUp/tearDown, Mock, 의존 관계 캡슐화 |
| Martin Fowler, "Mocks Aren't Stubs" (2007) | 상태 검증 vs 행위 검증, 고전 학파 vs 런던 학파, 테스트 더블 분류 |
| Steve Freeman & Nat Pryce, "Growing Object-Oriented Software, Guided by Tests" (2009) | 이중 루프 TDD, Walking Skeleton, Outside-In TDD, Mock Roles Not Objects, Tell Don't Ask |
| Gerard Meszaros, "xUnit Test Patterns" (2007) | 테스트 더블 5가지 분류, 테스트 냄새 카탈로그, 테스트 리팩토링 패턴 |
| Vladimir Khorikov, "Unit Testing Principles, Practices, and Patterns" (2020) | 좋은 테스트의 4대 기둥, 세 가지 테스트 스타일, 고전 학파 vs 런던 학파 비교 |
| Michael Feathers, "Working Effectively with Legacy Code" (2004) | 레거시 코드 정의, Seam 모델, 특성화 테스트, 의존성 깨뜨리기 기법 |
| Roy Osherove, "The Art of Unit Testing" 3rd ed. (2024) | 신뢰성/유지보수성/가독성 3대 속성, 테스트 명명 규칙, AAA 패턴 |
| Hypothesis 공식 문서 (hypothesis.readthedocs.io) | Property-Based Testing, 전략(Strategy), 축소(Shrinking) |
| mutmut 공식 문서 (mutmut.readthedocs.io) | Mutation Testing 개념, 뮤테이션 종류, 점수 해석 |
| pytest-bdd 공식 문서 (pytest-bdd.readthedocs.io) | BDD와 TDD의 관계, Given-When-Then, Gherkin 시나리오 |
| pytest-mock 공식 문서 (pytest-mock.readthedocs.io) | mocker fixture, patch, spy, side_effect |
| Thoughtworks, "TDD and Pair Programming: Perfect Companions for Copilot" (2024) | AI 보조 TDD, 페어 프로그래밍과 AI |
| Simon Willison, "Red/Green TDD - Agentic Engineering Patterns" (2025) | AI 시대의 Red-Green-Refactor, 테스트를 명세로 활용 |
| Awesome Testing, "Test-Driven AI Development (TDAID)" (2025) | TDAID 5단계 워크플로우 |
