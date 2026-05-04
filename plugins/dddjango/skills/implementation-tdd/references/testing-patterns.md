# 테스팅 패턴 레퍼런스

테스트 격리, 구조, 데이터, 명명, Mock 활용 등 테스트 작성 시 반복적으로 적용하는 패턴 모음.

---

## 테스트 격리

각각의 테스트는 서로 독립적이어야 하며, **실행 순서에서도 독립적**이어야 한다. 이를 달성하기 위한 구체적 전략은 **공유 상태 제거**이다.

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

> 출처: xUnit Test Patterns (Gerard Meszaros), 테스트주도 개발 (Kent Beck)

---

## AAA 패턴과 Assert First

테스트의 최종 코드 구조는 AAA 패턴을 따른다. 사고 과정에서는 Assert First(단언 우선)로 목적부터 정하되, 최종 코드는 위에서 아래로 자연스럽게 읽히도록 정리한다.

> Assert First 사고법: 완료 시 통과해야 할 단언부터 머릿속에 떠올리고, "이 값은 어디서 오는가?" 를 역추적하며 필요한 설정을 도출한다.

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

> 출처: Osherove, 테스트주도 개발 (Kent Beck)

---

## 테스트 데이터

- 테스트를 읽을 때 쉽고 따라가기 좋을 만한 데이터를 사용하라
- 데이터 간에 차이가 있다면 그 속에 **어떤 의미가 있어야** 한다
- 동일한 상수를 여러 의미로 쓰지 마라 (예: `plus(2, 2)` 대신 `plus(2, 3)`)

---

## 명백한 데이터

테스트 자체에 예상되는 값과 실제 값을 포함하고, 이 둘 사이의 **관계를 드러내기 위해 노력**하라.

```python
# 나쁨: 49.25가 왜 정답인지 알 수 없다
assert exchange(100, "USD", "GBP") == 49.25

# 좋음: 계산 과정이 드러난다
assert exchange(100, "USD", "GBP") == 100 / 2 * (1 - 0.015)
```

---

## 테스트 명명 규칙

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

> 출처: Osherove

---

## Mock 객체의 올바른 사용

통신 기반 테스트(Mock 중심)는 세 가지 테스트 스타일 중 **가장 낮은 우선순위**다. Mock은 외부 의존성 격리에 한정하고, 핵심 로직은 출력/상태 기반 테스트를 우선한다.

Mock이 유효한 경우:

- 외부 시스템(DB, API, 파일시스템)과의 통신 격리
- 비용이 많이 들거나 복잡한 리소스에 의존하는 경우
- 발생하기 힘든 에러 상황의 시뮬레이션 (크래시 테스트 더미)

```python
from unittest.mock import Mock, ANY

# Mock 생성 및 반환값 설정
mock_db = Mock(spec=DatabaseConnection)
mock_db.query.return_value = [
    {"name": "점박이", "species": "미어캣"},
]

# 테스트 실행
result = get_animals(mock_db, "미어캣")

# 호출 검증
mock_db.query.assert_called_once_with(ANY, "미어캣")
assert result[0]["name"] == "점박이"
```

> 출처: Khorikov, 테스트주도 개발 (Kent Beck)

---

## 크래시 테스트 더미

발생하기 힘든 에러 상황을 테스트할 때, 실제 작업을 수행하는 대신 **예외를 발생시키기만 하는 특수 객체**를 만들어서 호출한다.

```python
from unittest.mock import Mock

def test_file_system_error():
    mock_file = Mock()
    mock_file.write.side_effect = IOError("디스크 가득 참")

    with pytest.raises(IOError):
        save_data(mock_file, "some data")
```

> 출처: 테스트주도 개발 (Kent Beck)

---

## 셀프 션트 (Self Shunt)

한 객체가 다른 객체와 올바르게 대화하는지 테스트하려면, 테스트 대상이 되는 객체가 원래 대화 상대가 아니라 **테스트 케이스 자체와 대화하도록** 만든다.

```python
class TestNotification:
    def setup_method(self):
        self.count = 0

    def on_event(self):
        self.count += 1

    def test_listener_called(self):
        result = TestResult()
        result.add_listener(self)  # 테스트 자체가 리스너 역할
        run_test(result)
        assert self.count == 1
```

> 출처: 테스트주도 개발 (Kent Beck)

---

## 로그 문자열

메시지의 호출 순서가 올바른지 검사하기 위해 로그 문자열에 메시지가 호출될 때마다 추가한다.

```python
def test_lifecycle_order():
    test = WasRun("test_method")
    result = TestResult()
    test.run(result)
    assert test.log == "setUp test_method tearDown"
```

> 출처: 테스트주도 개발 (Kent Beck)

---

## 깨진 테스트 / 깨끗한 체크인

- **혼자 프로그래밍**: 테스트가 깨진 상태로 끝마치면 다음에 어디서부터 시작할지 좋은 단서가 된다
- **팀 프로그래밍**: 테스트가 성공한 상태로 끝마친다

> 출처: 테스트주도 개발 (Kent Beck)
