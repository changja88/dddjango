# 중복 제거와 DRY 레퍼런스

DRY 원칙의 올바른 적용, 코드 중복 제거, 지역적 변화의 원칙에 관한 규칙과 예시를 다룬다.

---

### 3.1 DRY는 지식의 중복을 금지하는 것이다 [PP]

> "모든 지식은 시스템 안에서 단일하고 모호하지 않은 권위 있는 표현을 가져야 한다."

DRY는 단순한 코드 중복 금지가 아니다. **지식의 중복**을 금지하는 것이다.
같은 코드라도 서로 다른 도메인 개념을 표현한다면 중복이 아닐 수 있고,
다른 코드라도 같은 비즈니스 규칙을 표현한다면 DRY 위반이다.

```python
# DRY 위반 — 같은 검증 규칙이 두 곳에
class UserValidator:
    def validate_age(self, age: int) -> bool:
        return 0 < age < 150

class UserForm:
    def is_valid_age(self, age: int) -> bool:
        return age > 0 and age < 150  # 같은 규칙의 다른 표현

# DRY 준수 — 검증 규칙의 단일 소스
class AgePolicy:
    MIN_AGE = 0
    MAX_AGE = 150

    @classmethod
    def is_valid(cls, age: int) -> bool:
        return cls.MIN_AGE < age < cls.MAX_AGE
```

```python
# DRY가 아닌 경우 — 우연히 같은 코드지만 다른 지식
def validate_user_age(age: int) -> bool:
    return 0 < age < 150  # 사용자 나이 정책

def validate_building_floors(floors: int) -> bool:
    return 0 < floors < 150  # 건물 층수 제한

# 이 두 함수를 합치면 안 된다. 서로 다른 도메인 규칙을 표현한다.
```

### 3.2 코드 중복 제거 [CC] [PC]

같은 계산이 여러 곳에 등장하면 추출하라.

```python
# bad — 점수 계산 공식이 중복
def process_students(students):
    ranking = sorted(students, key=lambda s: s.passed * 11 - s.failed * 5)
    for student in ranking:
        score = student.passed * 11 - student.failed * 5  # 중복!
        print(f"{student.name}: {score}")

# good — 추출
def calculate_score(student) -> int:
    return student.passed * 11 - student.failed * 5

def process_students(students):
    ranking = sorted(students, key=calculate_score)
    for student in ranking:
        print(f"{student.name}: {calculate_score(student)}")
```

### 3.3 지역적 변화의 원칙 [IP]

코드를 수정할 때 함께 바꿔야 하는 부분을 최소화하라.
중복을 없애는 방법은 프로그램을 여러 작은 부분으로 나누어,
각각이 하나의 지식을 소유하도록 하는 것이다.
