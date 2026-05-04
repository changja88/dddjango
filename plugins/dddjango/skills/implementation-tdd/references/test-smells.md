# 테스트 냄새 카탈로그 레퍼런스

테스트 실행 시 나타나는 행위 냄새와 테스트 코드 자체의 구조적 코드 냄새를 정리한다.

---

## 행위 냄새 (Behavior Smells)

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

---

## 코드 냄새 (Code Smells)

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

> 출처: Meszaros, xUnit Test Patterns §12
