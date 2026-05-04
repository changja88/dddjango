# 빨간 막대 패턴 레퍼런스

테스트를 언제, 어디에 작성할 것인가에 대한 패턴 모음.

---

## 테스트 목록

시작하기 전에 작성해야 할 **테스트 목록을 모두 적어 둘 것**. 테스트 코드는 테스트 대상이 되는 코드를 작성하기 직전에 작성하는 것이 좋다.

---

## 한 단계 테스트

목록에서 다음 테스트를 고를 때 기준: **새로운 무언가를 가르쳐 줄 수 있으며, 구현할 수 있다는 확신이 드는 테스트**를 고른다. 아는 것에서 모르는 것으로 방향을 잡는다.

---

## 시작 테스트

오퍼레이션이 **아무 일도 하지 않는 경우를 먼저 테스트**한다. 뭔가를 가르쳐 줄 수 있으면서도 빠르게 구현할 수 있는 테스트를 선택하라.

```python
def test_empty_cart_total():
    cart = ShoppingCart()
    assert cart.total() == 0  # 가장 단순한 경우부터 시작
```

---

## 설명 테스트

자동화된 테스트가 널리 쓰이게 하려면 **테스트를 통해 설명을 요청하고, 테스트를 통해 설명**해야 한다.

---

## 학습 테스트 (Learning Test)

서드파티 API나 낯선 기술을 사용할 때, 그 API에 대한 테스트를 작성하여 **동작을 학습**한다. 자신의 코드가 아닌 외부 동작을 검증하면서 동시에 라이브러리 업그레이드 시 동작 변경을 감지하는 회귀 테스트 역할도 한다.

```python
import json
import pytest

def test_json_loads_basic():
    """JSON 라이브러리가 기본 파싱을 어떻게 하는지 학습"""
    result = json.loads('{"key": "value"}')
    assert result == {"key": "value"}

def test_json_loads_nested():
    """중첩 구조 파싱 동작 학습"""
    result = json.loads('{"a": {"b": [1, 2, 3]}}')
    assert result["a"]["b"] == [1, 2, 3]

def test_json_loads_invalid_raises():
    """잘못된 JSON에 대한 예외 동작 학습"""
    with pytest.raises(json.JSONDecodeError):
        json.loads("not valid json")
```

세 가지 상황에서 학습 테스트가 유용하다:
1. 삼각측량 후 일반화 리팩토링이 어려울 때
2. 테스트를 통과시키기 어려울 때 (문제 도메인에 대한 숨겨진 가정)
3. 새로운 라이브러리나 프레임워크를 도입할 때

---

## 회귀 테스트 (Regression Test)

버그가 보고되면 **가장 작은 실패 테스트를 먼저 작성**하고, 그 다음에 수정한다. 테스트 없이 수정하면 같은 버그가 재발할 보장이 없다.

```python
def test_discount_negative_quantity_bug_report_157():
    """Bug #157: 수량이 음수일 때 할인이 음수 금액을 반환함.
    재현: calculate_discount(-1, 0.1) -> -0.1 (잘못된 결과)
    기대: ValueError 발생"""
    with pytest.raises(ValueError, match="수량은 0 이상"):
        calculate_discount(quantity=-1, rate=0.1)
```

---

## 또 하나의 테스트 (Another Test)

구현 도중 새로운 아이디어가 떠오르면, **지금 하던 일을 중단하지 말고 테스트 목록에 추가**한다. 정확히 하나의 실패 테스트에만 집중하면서, 모든 산만함을 나중에 처리할 목록에 기록한다.

```
테스트 목록 (진행 중):
[x] 빈 장바구니는 0을 반환
[x] 단일 항목은 항목 가격을 반환
[ ] 같은 항목 여러 개는 수량 할인 적용   <-- 현재 작업 중
[ ] 음수 수량은 에러 발생               <-- 방금 떠오른 아이디어
[ ] 국제 항목의 환율 변환              <-- 방금 떠오른 아이디어
```

---

## 하나에서 여러 개로 (One to Many)

컬렉션에 대한 연산을 구현하려면, **먼저 단일 항목(scalar)에 대해 구현**하고 나서 컬렉션으로 확장한다.

```python
# 1단계: 단일 항목에 대해 먼저 구현
def test_sum_single():
    assert sum_items(5) == 5

def sum_items(value):
    return value

# 2단계: 컬렉션으로 확장
def test_sum_multiple():
    assert sum_items([5, 7, 3]) == 15

# 3단계: 리팩토링 -- 통합
def sum_items(values):
    if not isinstance(values, list):
        values = [values]
    return sum(values)
```

핵심 알고리즘을 컬렉션 처리 로직으로부터 격리하여 인지 부하를 줄인다.

---

> 출처: Kent Beck, *테스트주도 개발* Chapter 26; [Canon TDD](https://tidyfirst.substack.com/p/canon-tdd)
