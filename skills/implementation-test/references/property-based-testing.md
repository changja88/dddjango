# Property-Based Testing (Hypothesis) 레퍼런스

Hypothesis를 사용한 속성 기반 테스트의 상세 규칙과 예시.

```bash
pip install hypothesis
```

---

## 1. 기본 사용법

전통적 테스트는 특정 입력값을 직접 선택하지만, Property-Based Testing은 **코드가 만족해야 할 속성(property)**을 정의하고, 프레임워크가 자동으로 수백 가지 입력을 생성하여 검증한다.

```python
from hypothesis import given, example, settings
from hypothesis import strategies as st

# 기본: 정수에 대한 속성 테스트
@given(st.integers())
def test_integer_negation_is_involutory(n):
    """이중 부정은 원래 값과 같다"""
    assert -(-n) == n

# 문자열 인코딩 라운드트립
@given(st.text())
def test_encode_decode_roundtrip(s):
    """UTF-8 인코딩 후 디코딩하면 원본과 같다"""
    assert s.encode("utf-8").decode("utf-8") == s

# 리스트 정렬 속성
@given(st.lists(st.integers()))
def test_sorted_list_properties(lst):
    sorted_lst = sorted(lst)
    assert len(sorted_lst) == len(lst)
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]
    assert sorted(sorted_lst) == sorted_lst
```

---

## 2. 전략(Strategies) 조합

```python
from hypothesis import strategies as st

# 기본 전략
integers = st.integers(min_value=0, max_value=100)
texts = st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L",)))
floats = st.floats(allow_nan=False, allow_infinity=False)

# 복합 전략: 사전 생성
user_strategy = st.fixed_dictionaries({
    "name": st.text(min_size=1, max_size=30),
    "age": st.integers(min_value=0, max_value=150),
    "email": st.emails(),
})

@given(user=user_strategy)
def test_user_validation(user):
    assert validate_user(user) or not is_valid_age(user["age"])

# 재귀적 전략: 트리 구조 생성
json_strategy = st.recursive(
    st.none() | st.booleans() | st.integers() | st.text(max_size=10),
    lambda children: st.lists(children, max_size=3)
                   | st.dictionaries(st.text(max_size=5), children, max_size=3),
    max_leaves=20,
)

@given(data=json_strategy)
def test_json_roundtrip(data):
    import json
    assert json.loads(json.dumps(data)) == data
```

---

## 3. @example: 경계값 명시

```python
@given(st.integers())
@example(0)
@example(-1)
@example(2**31)
def test_absolute_value(n):
    result = abs(n)
    assert result >= 0
    assert result == n or result == -n
```

---

## 4. settings로 실행 제어

```python
from hypothesis import given, settings, HealthCheck

@settings(
    max_examples=500,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(st.lists(st.integers(), min_size=100))
def test_large_list_sorting(lst):
    assert sorted(lst) == list(sorted(lst))

# CI에서는 더 많은 예제
@settings(max_examples=int(os.environ.get("HYPOTHESIS_MAX_EXAMPLES", "100")))
@given(st.text())
def test_string_processing(s):
    process(s)
```

---

## 5. Stateful Testing: 시퀀스 기반 테스트

상태를 가진 시스템(예: 데이터베이스, 캐시)을 테스트할 때, Hypothesis가 작업 시퀀스를 자동 생성한다.

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize
from hypothesis import strategies as st

class SetMachine(RuleBasedStateMachine):
    """파이썬 set과 동일하게 동작하는지 검증하는 상태 머신"""

    def __init__(self):
        super().__init__()
        self.model = set()
        self.impl = MyCustomSet()

    @rule(value=st.integers())
    def add_value(self, value):
        self.model.add(value)
        self.impl.add(value)
        assert self.impl.contains(value)

    @rule(value=st.integers())
    def remove_value(self, value):
        self.model.discard(value)
        self.impl.discard(value)
        assert not self.impl.contains(value) or value in self.model

    @rule()
    def check_size(self):
        assert len(self.impl) == len(self.model)

    @rule()
    def check_contents(self):
        for item in self.model:
            assert self.impl.contains(item)

TestSetMachine = SetMachine.TestCase
```

> 출처: [Hypothesis 공식 문서](https://hypothesis.readthedocs.io/), [Hypothesis Quickstart](https://hypothesis.readthedocs.io/en/latest/quickstart.html), [Stateful Testing](https://hypothesis.readthedocs.io/en/latest/stateful.html)
