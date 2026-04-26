# Mutation Testing (mutmut) 레퍼런스

뮤테이션 테스트의 개념과 mutmut 사용법에 대한 상세 규칙과 예시.

---

## 1. 개념: 테스트의 테스트

뮤테이션 테스트는 소스 코드에 의도적으로 **작은 변형(mutant)**을 가하고, 테스트 스위트가 이를 **감지(kill)**하는지 확인한다. 감지하지 못한 변형은 테스트에 구멍이 있음을 의미한다.

```
원본 코드:  if x > 0:
변형 1:     if x >= 0:    # 비교 연산자 변경
변형 2:     if x < 0:     # 비교 연산자 반전
변형 3:     if True:       # 조건 상수화
```

---

## 2. 뮤테이션 종류

| 뮤테이션 유형 | 원본 | 변형 |
|-------------|------|------|
| 산술 연산자 | `a + b` | `a - b` |
| 비교 연산자 | `x > 0` | `x >= 0` |
| 논리 연산자 | `a and b` | `a or b` |
| 상수 변형 | `return 0` | `return 1` |
| 부정 제거 | `not x` | `x` |
| 문장 삭제 | `x += 1` | `(삭제)` |

---

## 3. mutmut 사용법

```bash
# 설치
pip install mutmut

# 실행
mutmut run --paths-to-mutate "src/" --tests-dir "tests/"

# 결과 확인
mutmut results

# 개별 뮤턴트 상세 확인
mutmut show 42
```

---

## 4. 결과 해석

```
뮤테이션 점수(Mutation Score) = 죽인 뮤턴트 / 전체 뮤턴트 x 100

- Killed (죽음): 테스트가 변형을 감지함 -> 좋음
- Survived (생존): 테스트가 변형을 감지 못함 -> 테스트 보강 필요
- Timeout: 뮤턴트가 무한루프 유발 -> 보통 죽인 것으로 간주
- Suspicious: 비정상 종료 -> 수동 확인 필요
```

---

## 5. 경계값 테스트로 뮤턴트 죽이기

```python
# 뮤테이션 테스트에 취약한 코드
def calculate_discount(price: float, quantity: int) -> float:
    if quantity > 10:
        return price * 0.9
    return price


def test_discount_weak():
    """이 테스트는 mutmut에서 생존하는 뮤턴트를 남긴다."""
    assert calculate_discount(1000, 15) == 900
    # mutmut이 > 를 >= 로 바꾸면? quantity=10 케이스가 없어서 감지 못함!


# 뮤테이션 테스트에 강한 코드
def test_discount_strong():
    """경계값을 포함하여 뮤턴트를 죽인다."""
    assert calculate_discount(1000, 15) == 900   # > 10: 할인 적용
    assert calculate_discount(1000, 10) == 1000  # == 10: 할인 미적용 (경계)
    assert calculate_discount(1000, 11) == 900   # == 11: 할인 적용 (경계+1)
    assert calculate_discount(1000, 5) == 1000   # < 10: 할인 미적용
```

---

## 6. 뮤테이션 점수 목표

80% 이상의 뮤테이션 점수가 테스트 스위트의 강력한 결함 감지 능력을 나타낸다. 100%를 목표로 하기보다는 **생존한 뮤턴트를 분석**하여 의미 있는 테스트를 추가하는 것이 중요하다.
