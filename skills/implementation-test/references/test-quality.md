# 테스트 코드 품질 원칙과 안티패턴 레퍼런스

FIRST 원칙, AAA 패턴, 테스트 안티패턴에 대한 상세 규칙과 예시.

---

## 1. FIRST 원칙 [Clean Code - Robert C. Martin]

**F - Fast (빠르게)**
테스트는 빨라야 한다. 느리면 자주 실행하지 않게 되고, 문제를 늦게 발견한다.

```python
# 나쁜 예: 실제 API 호출
def test_slow_api_call():
    response = requests.get("https://real-api.example.com/data")
    assert response.status_code == 200

# 좋은 예: mock으로 빠르게
@responses.activate
def test_fast_api_call():
    responses.add(responses.GET, "https://real-api.example.com/data", status=200)
    response = requests.get("https://real-api.example.com/data")
    assert response.status_code == 200
```

**I - Independent (독립적으로)**
테스트 간에 상태를 공유하지 않는다. 어떤 순서로 실행해도 결과가 같아야 한다.

```python
# 나쁜 예: 전역 상태 공유
_created_user_id = None

def test_create_user():
    global _created_user_id
    _created_user_id = create_user("Alice")

def test_get_user():
    user = get_user(_created_user_id)  # 위 테스트에 의존!
    assert user.name == "Alice"

# 좋은 예: 각 테스트가 독립적
def test_create_user(db_session):
    user_id = create_user("Alice")
    assert user_id is not None

def test_get_user(db_session):
    user_id = create_user("Bob")  # 자체적으로 데이터 생성
    user = get_user(user_id)
    assert user.name == "Bob"
```

**R - Repeatable (반복 가능하게)**
어떤 환경에서든 같은 결과를 내야 한다. 외부 서비스, 시간, 난수에 의존하지 않는다.

```python
# 나쁜 예: 현재 시간에 의존
def test_is_weekend():
    assert is_weekend() == (datetime.now().weekday() >= 5)

# 좋은 예: 시간을 고정
@time_machine.travel("2024-01-13")  # 토요일
def test_is_weekend_saturday():
    assert is_weekend() is True

@time_machine.travel("2024-01-15")  # 월요일
def test_is_weekend_monday():
    assert is_weekend() is False
```

**S - Self-Validating (자가 검증)**
테스트 결과를 사람이 수동으로 확인할 필요 없이, assert로 자동 판별되어야 한다.

```python
# 나쁜 예: print로 수동 확인
def test_calculation():
    result = complex_calculation(42)
    print(f"결과: {result}")  # 사람이 눈으로 확인??

# 좋은 예: 자동 검증
def test_calculation():
    result = complex_calculation(42)
    assert result == 1764
    assert isinstance(result, int)
```

**T - Timely (적시에)**
프로덕션 코드를 작성하기 직전 또는 직후에 테스트를 작성한다.

---

## 2. AAA 패턴 (Arrange-Act-Assert)

AAA 패턴을 기본으로 하되, **논리적으로 하나의 행위를 검증하는 관련 assert는 허용**한다.

```python
def test_user_discount_calculation():
    # ---- Arrange (준비) ----
    user = UserFactory(membership="gold", joined_years_ago=3)
    product = ProductFactory(price=100.00, category="electronics")
    discount_service = DiscountService()

    # ---- Act (실행) ----
    discount = discount_service.calculate(user, product)

    # ---- Assert (검증) ----
    assert discount.percentage == 15.0
    assert discount.final_price == 85.00
    assert discount.reason == "골드 회원 3년차 할인"
```

**AAA 핵심 규칙**:

1. **Act 섹션은 가능한 한 줄**: 테스트 대상 동작을 명확히 하기 위해 Act은 단일 함수 호출이어야 한다.
2. **여러 AAA 블록은 별도 테스트로 분리**: 하나의 테스트에 여러 Act-Assert 쌍이 있으면 분리해야 한다.
3. **동일한 Act에 대한 관련 assert는 허용**: 논리적으로 하나의 행위를 검증하는 여러 assert는 같은 테스트에 둘 수 있다.

```python
# 나쁜 예: 여러 AAA 블록
def test_user_lifecycle():
    user = create_user("Alice")
    assert user.is_active        # AAA 블록 1

    deactivate(user)
    assert not user.is_active    # AAA 블록 2

    reactivate(user)
    assert user.is_active        # AAA 블록 3

# 좋은 예: 분리된 테스트
def test_new_user_is_active():
    user = create_user("Alice")
    assert user.is_active

def test_deactivated_user_is_inactive():
    user = create_user("Alice")
    deactivate(user)
    assert not user.is_active

def test_reactivated_user_is_active():
    user = create_user("Alice")
    deactivate(user)
    reactivate(user)
    assert user.is_active
```

---

## 3. 화이트박스 테스트를 피하라

구현 세부사항에 결합하지 않는 테스트를 작성해야 한다.

**설계 관점** [Kent Beck]: 화이트박스 테스트를 바라는 것은 테스팅 문제가 아니라 설계 문제다. 내부 구현을 들여다봐야 한다면, 그것은 인터페이스 설계가 잘못된 것이다.

**테스트 기법 관점** [Codepipes Blog]: 내부 구현에 결합된 테스트("The Inspector" 안티패턴)는 리팩토링할 때마다 깨진다.

```python
# 나쁜 예: 내부 구현에 결합
def test_sort_uses_quicksort(mocker):
    spy = mocker.spy(sort_module, "_partition")
    sort_module.sort([3, 1, 2])
    spy.assert_called()  # 정렬 알고리즘 변경하면 깨짐

# 좋은 예: 동작만 검증
def test_sort_returns_sorted_list():
    assert sort_module.sort([3, 1, 2]) == [1, 2, 3]
```

---

## 4. 코드 수준 안티패턴

**The Liar (거짓말쟁이)**: 실행은 되지만 실제로 검증하는 것이 없는 테스트.

```python
# 나쁜 예
def test_user_creation():
    user = create_user("Alice")
    assert user is not None  # 이것만으로는 불충분

# 좋은 예
def test_user_creation():
    user = create_user("Alice")
    assert user.name == "Alice"
    assert user.is_active is True
    assert user.created_at is not None
```

**Excessive Setup (과도한 설정)**: 수백 줄의 설정 코드로 테스트 대상이 무엇인지 파악하기 어렵다.

```python
# 나쁜 예: 모든 것을 직접 설정
def test_order_total():
    db = create_database()
    db.connect()
    user = db.create_user(name="Alice", email="a@b.com", ...)
    # ... 50줄 더 ...
    assert order.total == 30

# 좋은 예: fixture와 팩토리로 단순화
def test_order_total(order_with_two_items):
    assert order_with_two_items.total == 30
```

**Mockery (과도한 모킹)**: 너무 많은 mock으로 실제 시스템을 전혀 테스트하지 않게 되는 패턴.

```python
# 나쁜 예: 6개의 mock
def test_process_order(mocker):
    mock_db = mocker.Mock()
    mock_cache = mocker.Mock()
    mock_email = mocker.Mock()
    mock_payment = mocker.Mock()
    mock_inventory = mocker.Mock()
    mock_logger = mocker.Mock()

# 좋은 예: 외부 의존성만 mock
def test_process_order(mocker):
    mock_payment = mocker.Mock(return_value=PaymentResult(success=True))
    service = OrderService(payment_gateway=mock_payment)
    result = service.process(order)
    assert result.is_completed
```

**The Giant (거인)**: 수천 줄에 수십 개의 assert를 포함하는 테스트. 시스템이 God Object일 가능성을 나타낸다.

**Slow Poke (느림보)**: 실행에 수 분이 걸리는 테스트. 개발자가 테스트를 피하게 만든다.

**The Inspector (검사관)**: 구현 세부사항을 너무 많이 알고 있어서, 리팩토링할 때마다 깨진다.

**Free Ride (무임승차)**: 기존 테스트에 관련 없는 assert를 추가하는 패턴.

```python
# 나쁜 예: 하나의 테스트에 관련 없는 검증 추가
def test_create_user():
    user = create_user("Alice")
    assert user.name == "Alice"
    assert user.email_is_valid()  # 별도 테스트여야 함
    assert user.default_settings_applied()  # 별도 테스트여야 함
```

**기타 안티패턴**:
- **Generous Leftovers (관대한 잔여물)**: 한 테스트가 남긴 데이터를 다른 테스트가 사용
- **Local Hero (로컬 영웅)**: 특정 개발 환경에서만 통과하는 테스트
- **Secret Catcher (비밀 포획자)**: assert 없이 예외가 발생하지 않는 것만으로 "통과"
- **Dodger (회피자)**: 쉬운 테스트만 작성하고 핵심 비즈니스 로직은 테스트하지 않음
- **Cuckoo (뻐꾸기)**: 관련 없는 테스트 클래스/파일에 들어있는 테스트
- **The Nitpicker (트집잡이)**: 의미 없는 세부사항까지 검증하는 테스트

```python
# 나쁜 예: 전체 HTML 비교
def test_render_page():
    html = render_page()
    assert html == "<html><head>...</head><body>...</body></html>"  # 깨지기 쉬움

# 좋은 예: 중요한 부분만 검증
def test_render_page():
    html = render_page()
    assert "<h1>Welcome</h1>" in html
    assert "user-dashboard" in html
```

---

## 5. 전략 수준 안티패턴

1. **단위 테스트만 있고 통합 테스트 없음** (또는 그 반대)
2. **잘못된 테스트 유형 선택**: 단위 테스트로 충분한데 E2E로 작성
3. **테스트를 개발 프로세스의 별도 단계로 취급**
4. **테스트 코드를 프로덕션 코드보다 낮은 품질로 작성**
5. **비결정적(flaky) 테스트를 방치**
6. **느린 테스트를 개선하지 않음**
7. **테스트를 수동으로 실행** (CI/CD 미연동)
8. **코드 커버리지에만 집착**: 커버리지 100%가 버그 0%를 의미하지 않음

> 출처: Robert C. Martin, "Clean Code" (2008), [FIRST Principles - DZone](https://dzone.com/articles/first-principles-solid-rules-for-tests)

> 출처: [AAA Pattern - Semaphore](https://semaphore.io/blog/aaa-pattern-test-automation), [Manning: Making Better Unit Tests](https://freecontent.manning.com/making-better-unit-tests-part-1-the-aaa-pattern/), Clean Code (Robert C. Martin)

> 출처: [Software Testing Anti-patterns - Codepipes Blog](https://blog.codepipes.com/testing/software-testing-antipatterns.html), [Unit Testing Anti-Patterns Full List - DZone](https://dzone.com/articles/unit-testing-anti-patterns-full-list)
