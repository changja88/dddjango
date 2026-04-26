# 테스트 코드 리뷰

## 총평

커버리지 수치는 높을 수 있지만, **테스트의 깊이와 다양성이 부족**합니다. 현재 테스트는 "코드 라인을 실행하는가"에 집중되어 있고, "비즈니스 로직이 올바른가"를 검증하는 데는 미흡합니다. 아래에 함수별로 누락된 케이스와 구조적 개선점을 정리합니다.

---

## 1. `validate_email` -- 누락된 테스트 케이스

### 현재 커버하는 것
- 정상 이메일 1건
- `@` 없는 경우
- 도메인 없는 경우 (`user@`)
- 빈 문자열, None

### 누락된 케이스

| 카테고리 | 예시 입력 | 기대 결과 | 설명 |
|---------|----------|----------|------|
| `@` 2개 이상 | `user@@example.com`, `a@b@c.com` | `False` | `split('@')`이 3개 이상 반환 |
| local 부분 없음 | `@example.com` | `False` | local이 빈 문자열 |
| 도메인에 `.` 없음 | `user@localhost` | `False` | 분기 커버 누락 가능 |
| 도메인이 `.`으로 시작 | `user@.example.com` | `False` | `domain.startswith('.')` 분기 |
| 도메인이 `.`으로 끝남 | `user@example.` | `False` | `domain.endswith('.')` 분기 |
| 타입 오류 | `123`, `['a@b.com']` | `False` | `isinstance` 분기의 비문자열 케이스 |
| 공백 포함 | `user @example.com` | 현재 `True` 반환 (잠재적 버그) | 공백 검증 로직 없음 |
| 특수문자 | `user+tag@example.com` | `True` | 유효한 이메일이지만 테스트 없음 |
| 서브도메인 | `user@sub.example.com` | `True` | 다중 `.` 도메인 검증 |

특히 `domain.startswith('.')`, `domain.endswith('.')` 분기는 현재 테스트에서 한 번도 실행되지 않으므로, 라인 커버리지는 채워도 **브랜치 커버리지에 구멍**이 있습니다.

---

## 2. `calculate_shipping` -- 누락된 테스트 케이스

### 현재 커버하는 것
- 기본 계산 1건 (weight=2.0, distance=150)
- 익스프레스 1건
- weight=0 에러
- 음수 distance 에러

### 누락된 케이스

| 카테고리 | 예시 입력 | 기대 결과 | 설명 |
|---------|----------|----------|------|
| **상한 캡 (50,000원)** | `weight=100, distance=5000` | `50000` | `total > 50000` 분기 미검증 |
| 익스프레스 + 상한 캡 | `weight=100, distance=5000, is_express=True` | `50000` | 익스프레스 적용 후 캡이 걸리는 케이스 |
| 캡 경계값 | 합계가 정확히 50000이 되는 입력 | `50000` | 경계값 테스트 |
| 캡 직전 | 합계가 49999인 입력 | `49999` | 캡 미적용 확인 |
| 음수 weight | `weight=-1, distance=100` | `ValueError` | 음수 무게 검증 |
| distance=0 | `weight=1.0, distance=0` | `ValueError` | 0 거리 검증 |
| 소수점 weight | `weight=0.5, distance=100` | 정확한 계산값 | 소수점 연산 정확성 |
| distance 100 미만 | `weight=1.0, distance=50` | `3500` | `distance // 100 == 0`이므로 distance_fee=0 |
| 큰 거리 | `weight=1.0, distance=1000` | 정확한 계산값 | 거리 비례 증가 확인 |
| float 타입 distance | `weight=1.0, distance=150.5` | ? | 타입 힌트는 int인데 float 넘기면? |

**가장 큰 문제: `total > 50000` 캡 로직이 완전히 테스트되지 않았습니다.** 이 분기는 비즈니스적으로 중요한 상한선 규칙인데 단 한 번도 검증하지 않습니다.

---

## 3. 구조적 문제

### 3-1. 테스트 이름이 "무엇을 테스트하는가"를 제대로 설명하지 않음

현재 이름은 입력 조건만 기술합니다. **기대 동작**이 이름에 포함되면 실패 시 원인 파악이 훨씬 쉬워집니다.

```python
# 현재
def test_shipping_basic():

# 개선
def test_shipping_returns_base_plus_weight_and_distance_fees():
```

### 3-2. 매직 넘버 검증 부재

`test_shipping_basic`에서 `assert result == 5000`이라고 했지만, 이 5000이 어떻게 나왔는지 테스트 코드만 보면 알 수 없습니다. 계산 과정을 주석이나 변수로 명시하는 것이 좋습니다.

```python
def test_shipping_basic():
    # base(3000) + weight_fee(2.0 * 500 = 1000) + distance_fee(150 // 100 * 1000 = 1000) = 5000
    result = calculate_shipping(2.0, 150)
    assert result == 5000
```

### 3-3. 에러 메시지 검증 없음

`pytest.raises(ValueError)`만 쓰고 메시지를 검증하지 않습니다. 다른 원인의 ValueError가 발생해도 테스트가 통과합니다.

```python
# 현재
with pytest.raises(ValueError):
    calculate_shipping(0, 100)

# 개선
with pytest.raises(ValueError, match="무게는 0보다 커야 합니다"):
    calculate_shipping(0, 100)
```

### 3-4. `parametrize` 미활용

유사한 패턴의 테스트가 반복됩니다. `@pytest.mark.parametrize`를 사용하면 케이스를 쉽게 추가하고 관리할 수 있습니다.

```python
@pytest.mark.parametrize("email, expected", [
    ("user@example.com", True),
    ("user+tag@example.com", True),
    ("user@sub.example.com", True),
    ("userexample.com", False),
    ("user@", False),
    ("@example.com", False),
    ("user@.example.com", False),
    ("user@example.", False),
    ("user@@example.com", False),
    ("", False),
    (None, False),
    (123, False),
])
def test_validate_email(email, expected):
    assert validate_email(email) is expected
```

### 3-5. 프로덕션 코드와 테스트 코드가 같은 파일

현재 함수 정의와 테스트가 한 파일에 있습니다. 실제 프로젝트에서는 분리해야 합니다. 리뷰 범위 밖이지만 참고사항으로 기록합니다.

---

## 4. 잠재적 프로덕션 코드 버그 (테스트가 잡지 못하는 것)

테스트 리뷰 과정에서 프로덕션 코드의 잠재적 문제도 발견됩니다.

1. **`validate_email`: 공백이 포함된 이메일을 허용함** -- `"user @example.com"`이 `True`를 반환합니다. 이를 검증하는 테스트가 없어서 이 동작이 의도된 것인지 버그인지 알 수 없습니다.

2. **`calculate_shipping`: `round(total, 2)` 호출이 무의미할 수 있음** -- 현재 계산식에서 소수점 이하가 발생하는 경우는 `is_express=True`일 때 `* 1.5`뿐이고, 정수 입력이면 항상 `.0` 또는 `.5`로 끝납니다. 하지만 weight가 소수점을 가질 경우 부동소수점 오차가 발생할 수 있으므로 `round`는 방어적으로 유효합니다. 이런 경우를 검증하는 테스트가 없습니다.

---

## 5. 우선순위별 추가 권장 테스트

### 반드시 추가 (비즈니스 로직 검증 누락)
1. 배송비 상한 50,000원 캡 테스트
2. 익스프레스 + 캡 조합 테스트
3. `validate_email`의 `startsWith('.')`/`endsWith('.')` 분기 테스트

### 강하게 권장 (경계값/엣지케이스)
4. distance가 100 미만인 경우 (distance_fee = 0)
5. `@`가 2개 이상인 이메일
6. local 파트가 없는 이메일 (`@domain.com`)
7. 에러 메시지 match 검증

### 권장 (견고성 향상)
8. 캡 경계값 (49,999 vs 50,000 vs 50,001)
9. 비문자열 타입 입력 (정수 등)
10. `parametrize` 리팩토링

---

## 요약

| 항목 | 현재 상태 | 평가 |
|------|----------|------|
| 라인 커버리지 | 높음 | 양호 |
| 브랜치 커버리지 | 미흡 (캡 로직, 도메인 시작/끝 `.` 미검증) | 부족 |
| 경계값 테스트 | 거의 없음 | 부족 |
| 조합 테스트 | 익스프레스 + 캡 등 미검증 | 부족 |
| 에러 메시지 검증 | 없음 | 개선 필요 |
| 테스트 가독성 | 매직 넘버, 이름 개선 여지 | 보통 |

"커버리지는 높은데 부족한 느낌"의 원인은 **라인 커버리지에만 의존하고, 브랜치 커버리지/경계값/조합 테스트가 빠져있기 때문**입니다. 특히 배송비 상한 캡(50,000원) 로직이 한 번도 테스트되지 않은 것이 가장 큰 결함입니다.
