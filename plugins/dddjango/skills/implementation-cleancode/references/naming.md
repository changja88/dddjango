# 이름 짓기 레퍼런스

클린 코드 원칙의 이름 짓기에 대한 상세 규칙과 예시.
이름 결정이 필요한 코드를 작성, 리뷰, 리팩토링할 때 참조한다.

---

## 1.1 의도를 분명히 밝혀라 [CC]

변수, 함수, 클래스 이름은 존재 이유, 수행 기능, 사용 방법에 모두 답해야 한다.
따로 주석이 필요하다면 의도를 분명히 드러내지 못했다는 뜻이다.

```python
# bad
d = 7  # 경과 일수

# good
elapsed_days_since_creation = 7
```

## 1.2 그릇된 정보를 피하라 [CC]

실제와 다른 정보를 이름에 담지 마라.

```python
# bad — 실제로는 dict인데 list라고 명명
account_list = {}

# good
accounts = {}
account_map = {}
```

## 1.3 의미 있게 구분하라 [CC]

불용어(Info, Data, a, the)를 사용하면 개념을 구분하지 못한 채 이름만 달리한 것이다.

```python
# bad
class ProductInfo: ...
class ProductData: ...  # Info와 Data는 아무것도 구분하지 못한다

# good
class Product: ...
class ProductDetail: ...  # 구체적으로 무엇이 다른지 이름에 반영
```

## 1.4 이름 길이는 범위에 비례해야 한다 [CC] [CodeC]

넓은 범위에서 사용되는 변수일수록 긴 이름이 필요하고, 좁은 범위의 지역 변수는 짧아도 된다.
변수 이름의 최적 평균 길이는 10-16자, 루틴 이름은 15-20자를 참고한다.

```python
# bad — 매직 넘버, 불투명한 이름이 넓은 범위에서 사용
for i in range(34):
    s += t[i] * 4 / 5

# good
WORK_DAYS_PER_WEEK = 5
for task_index in range(number_of_tasks):
    real_days = task_estimate[task_index] * real_days_per_ideal_day
    weekly_sum += real_days / WORK_DAYS_PER_WEEK
```

## 1.5 한 개념에 한 단어를 사용하라 [CC]

추상적인 개념 하나에 단어 하나를 선택해 고수한다.

```python
# bad — 같은 개념에 fetch vs retrieve 혼용
class UserRepository:
    def fetch_user(self): ...
class OrderRepository:
    def retrieve_order(self): ...

# good
class UserRepository:
    def get_user(self): ...
class OrderRepository:
    def get_order(self): ...
```

## 1.6 클래스 이름은 명사, 메서드 이름은 동사 [CC] [IP]

```python
# 클래스: 명사 또는 명사구
class Customer: ...
class AddressParser: ...

# 메서드: 동사 또는 동사구
def post_payment(self): ...
def delete_page(self): ...
```

## 1.7 의도 제시형 이름 [IP]

메서드 이름에는 의도만 전달하고 구현 전략은 담지 마라.

```python
# bad — 구현 전략이 노출됨
def linear_search_customer(customer_id: str) -> Customer: ...

# good
def find_customer(customer_id: str) -> Customer: ...
```

## 1.8 역할 제시형 작명 [IP]

변수 이름은 연산에서의 역할을 반영하여 짓는다.

```python
# bad — 저장 방식의 세부사항이 노출됨
temp_str_list = get_items()

# good — 역할을 전달
results = get_items()
pending_count = len(queue)
```

## 1.9 컬렉션은 복수형으로 [IP]

```python
# bad
member = [user1, user2, user3]

# good
members = [user1, user2, user3]
```

## 1.10 한정자 배치: 핵심 개념을 앞에 [CodeC]

핵심 개념을 접두어로, 한정자를 뒤에 배치한다. 관련 변수들이 그룹으로 인식되고, IDE 자동완성에서도 이점이 있다.

```python
# bad — 한정자가 앞에 오면 관련 이름이 흩어진다
total_revenue = ...
avg_revenue = ...

# good — 핵심 개념이 앞에
revenue_total = ...
revenue_average = ...
revenue_max = ...
```

## 1.11 불리언 변수 명명 [CodeC]

술어 접두사나 긍정형 형용사를 사용한다. 부정형 이름은 피하라.

```python
# bad
status = True
not_found = True

# good
is_valid = True
has_permission = True
found = False
```

## 1.12 `num` 사용 회피 [CodeC]

`num`은 총 수인지 인덱스인지 모호하다.

```python
# bad
num_customers = 5
customer_num = 3

# good
customer_count = 5
customer_index = 3
```

## 1.13 루프 변수 명명 [CodeC]

짧은 루프에서는 `i`를 허용하지만, 긴 루프나 중첩 루프에서는 의미 있는 이름이 필요하다.

```python
for team_index, team in enumerate(teams):
    for player_index, player in enumerate(team.players):
        scores[team_index][player_index] = player.score
```
