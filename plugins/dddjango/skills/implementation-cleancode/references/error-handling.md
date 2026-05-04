# 오류 처리 레퍼런스

예외 설계, 보호절, 계약에 의한 디자인, 방어적 프로그래밍에 관한 규칙과 예시를 다룬다.

---

### 2.1 1순위: 오류를 존재에서 제거하라 [APoSD]

예외 처리는 소프트웨어 시스템에서 가장 큰 복잡성 원천 중 하나다.
가능하다면 오류 조건 자체를 설계적으로 제거하라.

```python
# bad — 불필요한 오류 조건
class TextBuffer:
    def delete_selection(self):
        if not self.has_selection():
            raise NoSelectionError("Nothing is selected")
        # ... 삭제 로직

# good — 오류를 존재에서 제거
class TextBuffer:
    def delete_selection(self):
        """현재 선택 영역을 삭제한다. 선택이 없으면 아무것도 하지 않는다."""
        if not self.has_selection():
            return
        # ... 삭제 로직
```

### 2.2 2순위: 오류 코드보다 예외를 사용하라 [CC]

오류 코드를 반환하면 호출자는 오류 코드를 곧바로 처리해야 하고,
명령/조회 분리 규칙을 위반한다.

```python
# bad — 오류 코드 체인
result = delete_page(page)
if result == E_OK:
    result = registry.delete_reference(page.name)
    if result == E_OK:
        ...

# good — 예외 사용
try:
    delete_page(page)
    registry.delete_reference(page.name)
    config_keys.delete_key(page.name.make_key())
except Exception as e:
    logger.error(e)
```

### 2.3 Try/Catch 블록은 분리하라 [CC]

정상 동작과 오류 처리 동작을 분리하면 이해하고 수정하기 쉬워진다.

```python
def delete(page):
    try:
        delete_page_and_all_references(page)
    except Exception as e:
        log_error(e)

def delete_page_and_all_references(page):
    delete_page(page)
    registry.delete_reference(page.name)
    config_keys.delete_key(page.name.make_key())
```

### 2.4 올바른 추상화 수준에서 예외를 처리하라 [PC]

예외는 함수가 캡슐화하고 있는 로직의 도메인에 맞아야 한다.
하위 수준의 세부 사항이 상위 수준에 누출되지 않도록 한다.

### 2.5 보호절(Guard Clause)을 활용하라 [IP]

중첩된 조건문을 조기 반환으로 평탄화하여 주요 흐름과 예외 흐름의 차이를 부각시킨다.

```python
# bad — 깊은 중첩
def compute():
    server = get_server()
    if server is not None:
        client = server.get_client()
        if client is not None:
            request = client.get_request()
            if request is not None:
                process_request(request)

# good — 보호절
def compute():
    server = get_server()
    if server is None: return
    client = server.get_client()
    if client is None: return
    request = client.get_request()
    if request is None: return
    process_request(request)
```

### 2.6 계약에 의한 디자인 (DbC) [PC]

사전조건과 사후조건을 명시적으로 정의하여 책임 소재를 명확히 하라.

```python
def add_positive_numbers(a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        raise ValueError("입력 값은 양수여야 합니다")  # 사전 조건

    result = a + b

    assert result > 0, "결과 값은 양수여야 합니다"  # 사후 조건
    return result
```

### 2.7 방어적 프로그래밍 [CodeC]

잘못된 입력으로부터 프로그램을 보호하라. "외부"를 어디로 정할지 결정하고,
그 경계에서 데이터를 검증하라.

#### 단언(Assertion) vs 오류 처리

| 상황                              | 기법                  |
|-----------------------------------|-----------------------|
| 절대 발생해서는 안 되는 조건         | `assert` 사용         |
| 발생할 수 있는 예상된 외부 오류       | 오류 처리 코드 사용     |
| 고신뢰성이 필요한 코드              | 둘 다 사용             |

```python
# Assertion — 개발 중 논리 오류 탐지
def calculate_discount(price: float, rate: float) -> float:
    assert 0.0 <= rate <= 1.0, f"Rate must be 0-1, got {rate}"
    return price * (1 - rate)

# 오류 처리 — 외부 입력 검증
def parse_user_input(raw_rate: str) -> float:
    try:
        rate = float(raw_rate)
    except ValueError:
        raise InvalidInputError(f"'{raw_rate}' is not a valid number")
    if not 0.0 <= rate <= 1.0:
        raise InvalidInputError(f"Rate must be 0-1, got {rate}")
    return rate
```

#### 정확성(Correctness) vs 견고성(Robustness)

- **정확성** -- 부정확한 결과를 절대 반환하지 않는다 (안전 필수 시스템)
- **견고성** -- 소프트웨어가 계속 작동하도록 최선을 다한다 (소비자 앱)

```python
# 정확성 우선 (안전 필수 시스템)
def calculate_medication_dose(weight_kg, dosage_per_kg):
    if weight_kg <= 0 or dosage_per_kg <= 0:
        raise CriticalError("Invalid parameters")
    dose = weight_kg * dosage_per_kg
    if dose > MAX_SAFE_DOSE:
        raise CriticalError(f"Dose {dose}mg exceeds safety limit")
    return dose

# 견고성 우선 (소비자 앱)
def load_user_preferences(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_PREFERENCES
```
