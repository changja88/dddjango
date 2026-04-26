# 초록 막대 패턴 레퍼런스

테스트를 통과시키는 세 가지 전략에 대한 패턴 모음.

---

## 가짜로 구현하기 (Fake It)

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

---

## 삼각측량 (Triangulation)

추상화 과정을 테스트로 주도할 때 최대한 보수적으로 하는 방법: **예가 두 개 이상일 때에만 추상화**한다.

```python
def test_plus():
    assert plus(3, 1) == 4
    assert plus(3, 4) == 7  # 두 번째 예에서 추상화


def plus(a, b):
    return a + b  # 두 예제가 있으므로 비로소 일반화
```

어떻게 올바르게 추상화할 것인지 감잡기 어려울 때 사용하면 좋다.

---

## 명백한 구현 (Obvious Implementation)

단순한 연산들은 그냥 구현해버린다. 어떻게 구현해야 할지 확신이 들면 그렇게 하는 것이 좋다.

---

## 변환 우선순위 전제 (Transformation Priority Premise) [Robert C. Martin]

Robert C. Martin(Uncle Bob)이 2013년에 제안한 개념. 리팩토링이 코드의 **구조**를 바꾸는 것이라면, 변환(transformation)은 코드의 **행위**를 바꾸는 것이다. Red에서 Green으로 갈 때 더 단순한 변환을 우선 적용하면 TDD 교착 상태를 줄일 수 있다.

### 변환 우선순위 목록

| 순위 | 변환 | 설명 | 예시 |
|:----:|------|------|------|
| 1 | `{} → nil` | 코드 없음에서 nil/None 반환 | `return None` |
| 2 | `nil → constant` | nil에서 상수로 | `return None` → `return ""` |
| 3 | `constant → constant+` | 단순 상수에서 ��잡한 상수로 | `return ""` → `return "1"` |
| 4 | `constant → scalar` | 상수에서 변수/인자로 | `return "1"` → `return str(n)` |
| 5 | `statement → statements` | 무조건 문장 추가 | 코드 한 줄 추가 |
| 6 | `unconditional → if` | 실행 경로 분기 | `if` 문 추가 |
| 7 | `scalar → array` | 스칼라를 배열/리스트로 | `value` → `values = [value]` |
| 8 | `array → container` | 배열을 더 복잡한 컨테이너로 | `list` → `dict` 또는 `set` |
| 9 | `statement → recursion` | 문장을 재귀로 | 재귀 호출 도입 |
| 10 | `if → while` | 조건문을 반복문으로 | `if` → `while` |
| 11 | `expression → function` | 표현식을 함수로 | 인라인 계산 → 함수 호출 |
| 12 | `variable → assignment` | 변수 값 변경 | 변수 재할당 |

### TPP 적용 예시: 단어 점수 계산

```python
# 테스트 1: 빈 문자열 → 0
def test_score_empty():
    assert score("") == 0

# 변환: {} → nil → constant
def score(word):
    return 0

# 테스트 2: 단일 문자 → 1
def test_score_single_letter():
    assert score("a") == 1

# 변환: constant → scalar (if를 추가하는 것보다 단순!)
def score(word):
    return len(word)

# 테스트 3: 여러 문자 → 이미 통과!
def test_score_hello():
    assert score("hello") == 5

# 테스트 4: 특수 문자 보너스 점수
def test_score_with_bonus():
    assert score("quiz") == 7  # q=3, u=1, i=1, z=3

# 변환: scalar → array/container + expression → function
BONUS = {"q": 3, "z": 3}
def score(word):
    return sum(BONUS.get(c, 1) for c in word)
```

**핵심 통찰**: 상수를 변수로 바꾸는 것(순위 4)이 if 문을 추가하는 것(순위 6)보다 **더 단순한 변환**이다. if를 쓰려고 할 때, 더 단순한 변환으로 테스트를 통과할 수 없는지 먼저 확인하라.

**우선순위를 위반하면?** Uncle Bob은 정렬 알고리즘 예시에서, 단순한 변환이 가능한데 복잡한 변환을 선택하면 이후 테스트를 통과시키기 점점 어려워지는 교착 상태에 빠진다는 것을 보여주었다.

**Fake It, Triangulation과의 관계**: TPP는 Beck이 직관적으로 설명한 초록 막대 패턴에 대해 **형식적 프레임워크**를 제공한다. Fake It은 `nil → constant` 변환이고, Triangulation은 `constant → scalar` 변환을 강제하는 기법이다.

> 출처: Robert C. Martin, [The Transformation Priority Premise](http://blog.cleancoder.com/uncle-bob/2013/05/27/TheTransformationPriorityPremise.html) (2013); Kent Beck, *테스트주도 개발*
