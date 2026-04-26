# DiscountCalculator 테스트 리팩토링

## 진단 요약

이 테스트 코드의 핵심 문제는 **Mockery (과도한 모킹)** 안티패턴이다. `DiscountCalculator`는 순수한 할인 계산 비즈니스 로직인데, 세 개의 의존성을 모두 `Mock()`으로 대체하고, 반환값 검증(출력 기반)과 함께 `assert_called_once_with` (통신 기반) 검증을 혼용하고 있다. 그 결과 "실제로 뭘 테스트하는 건지" 불명확해졌다.

---

## 개별 변경 사항

### 변경 1: Mock을 Fake로 교체

[Before]
```python
def test_gold_user_discount():
    user_repo = Mock()
    product_repo = Mock()
    promo_service = Mock()

    user_repo.get.return_value = {'id': 1, 'name': 'Alice', 'tier': 'gold'}
    product_repo.get.return_value = {'id': 100, 'name': '노트북', 'price': 1000000}
    promo_service.get_active_promotion.return_value = None

    calc = DiscountCalculator(user_repo, product_repo, promo_service)
    result = calc.calculate(1, 100)

    assert result == 900000
    user_repo.get.assert_called_once_with(1)
    product_repo.get.assert_called_once_with(100)
    promo_service.get_active_promotion.assert_called_once_with(100)
```

[After]
```python
class FakeUserRepo:
    def __init__(self, users: dict | None = None):
        self._users = users or {}

    def add(self, user: dict) -> None:
        self._users[user['id']] = user

    def get(self, user_id: int) -> dict | None:
        return self._users.get(user_id)


class FakeProductRepo:
    def __init__(self, products: dict | None = None):
        self._products = products or {}

    def add(self, product: dict) -> None:
        self._products[product['id']] = product

    def get(self, product_id: int) -> dict | None:
        return self._products.get(product_id)


class FakePromotionService:
    def __init__(self, promotions: dict | None = None):
        self._promotions = promotions or {}

    def set_promotion(self, product_id: int, promo: dict) -> None:
        self._promotions[product_id] = promo

    def get_active_promotion(self, product_id: int) -> dict | None:
        return self._promotions.get(product_id)


def test_gold_user_gets_10_percent_discount():
    user_repo = FakeUserRepo()
    product_repo = FakeProductRepo()
    promo_service = FakePromotionService()

    user_repo.add({'id': 1, 'name': 'Alice', 'tier': 'gold'})
    product_repo.add({'id': 100, 'name': '노트북', 'price': 1000000})

    calc = DiscountCalculator(user_repo, product_repo, promo_service)
    result = calc.calculate(1, 100)

    assert result == 900000
```

[Reason] Verification Priority (출력 기반 > 통신 기반) -- `user_repo`, `product_repo`, `promo_service`는 외부 시스템이 아니라 데이터 저장소 인터페이스다. Mock 대신 간소화된 실제 구현(Fake)을 사용하면 내부 호출 순서에 결합되지 않으면서 비즈니스 로직을 실제로 검증할 수 있다. `assert_called_once_with` 같은 통신 기반 검증은 리팩토링에 취약한 The Inspector 안티패턴이므로 제거하고, 반환값(출력 기반)만 검증한다.

---

### 변경 2: 통신 기반 검증(assert_called) 제거

[Before]
```python
    assert result == 900000
    user_repo.get.assert_called_once_with(1)
    product_repo.get.assert_called_once_with(100)
    promo_service.get_active_promotion.assert_called_once_with(100)
```

[After]
```python
    assert result == 900000
```

[Reason] The Inspector 안티패턴 -- `assert_called_once_with`는 "어떤 메서드가 어떤 인자로 호출되었는지"라는 구현 세부사항을 검증한다. 내부 구현이 캐싱을 도입하거나 호출 순서를 바꾸면 로직이 정확한데도 테스트가 깨진다. 반환값이 올바르면 내부 동작은 정확한 것이므로, 출력 기반 검증만으로 충분하다.

---

### 변경 3: 반복적인 Mock 설정을 Fixture로 추출

[Before]
```python
def test_gold_user_discount():
    user_repo = Mock()
    product_repo = Mock()
    promo_service = Mock()
    # ... setup ...
    calc = DiscountCalculator(user_repo, product_repo, promo_service)

def test_platinum_with_promo():
    user_repo = Mock()
    product_repo = Mock()
    promo_service = Mock()
    # ... setup ...
    calc = DiscountCalculator(user_repo, product_repo, promo_service)

# 4개 테스트 모두 동일한 3줄 Mock 생성 + DiscountCalculator 생성 반복
```

[After]
```python
@pytest.fixture
def user_repo():
    return FakeUserRepo()

@pytest.fixture
def product_repo():
    return FakeProductRepo()

@pytest.fixture
def promo_service():
    return FakePromotionService()

@pytest.fixture
def calculator(user_repo, product_repo, promo_service):
    return DiscountCalculator(user_repo, product_repo, promo_service)
```

[Reason] Excessive Setup 안티패턴 -- 4개 테스트 모두 동일한 객체 생성 보일러플레이트를 반복하고 있다. pytest fixture로 추출하면 각 테스트는 자신이 검증하는 시나리오의 데이터 설정에만 집중할 수 있다.

---

### 변경 4: 반복적인 등급별 할인 테스트를 parametrize로 통합

[Before]
```python
def test_gold_user_discount():
    # gold 등급 10% 할인 테스트
    ...

# platinum 등급 테스트는 프로모션과 결합되어 있어 등급별 할인만 따로 검증하지 않음
```

[After]
```python
@pytest.mark.parametrize(
    "tier, expected_price",
    [
        ("basic", 1000000),
        ("gold", 900000),
        ("platinum", 850000),
    ],
    ids=["basic-no-discount", "gold-10%-discount", "platinum-15%-discount"],
)
def test_tier_discount(calculator, user_repo, product_repo, tier, expected_price):
    user_repo.add({'id': 1, 'name': 'Alice', 'tier': tier})
    product_repo.add({'id': 100, 'name': '노트북', 'price': 1000000})

    result = calculator.calculate(1, 100)

    assert result == expected_price
```

[Reason] Repetitive test cases -> parametrize -- 등급별 할인율은 동일한 로직의 데이터만 다른 케이스다. parametrize로 통합하면 새로운 등급이 추가되어도 한 줄만 추가하면 되고, 누락된 등급(basic)도 자연스럽게 커버된다.

---

### 변경 5: 테스트 함수명을 행동 기반으로 개선

[Before]
```python
def test_gold_user_discount():
def test_platinum_with_promo():
def test_user_not_found():
def test_product_not_found():
```

[After]
```python
def test_tier_discount(...):            # 등급별 할인 적용
def test_promotion_discount(...):        # 프로모션 할인 적용
def test_combined_discount_capped(...):  # 복합 할인 최대 30% 제한
def test_user_not_found_raises(...):     # 미존재 사용자 에러
def test_product_not_found_raises(...):  # 미존재 상품 에러
```

[Reason] AAA -- 테스트 이름은 "어떤 행동을 검증하는지" 드러내야 한다. `test_platinum_with_promo`는 입력 조건만 나열하고 기대 행동이 불명확하다. `test_combined_discount_capped_at_30_percent`처럼 기대 결과를 이름에 포함하면 테스트가 실패했을 때 무엇이 깨졌는지 즉시 알 수 있다.

---

## 리팩토링 완성 코드

```python
import pytest


class DiscountCalculator:
    def __init__(self, user_repo, product_repo, promotion_service):
        self.user_repo = user_repo
        self.product_repo = product_repo
        self.promotion_service = promotion_service

    def calculate(self, user_id: int, product_id: int) -> float:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError(f'사용자 {user_id}을 찾을 수 없습니다')
        product = self.product_repo.get(product_id)
        if not product:
            raise ValueError(f'상품 {product_id}을 찾을 수 없습니다')

        base_discount = 0.0
        if user['tier'] == 'gold':
            base_discount = 0.1
        elif user['tier'] == 'platinum':
            base_discount = 0.15

        promo = self.promotion_service.get_active_promotion(product_id)
        promo_discount = promo['discount_rate'] if promo else 0.0

        total_discount = min(base_discount + promo_discount, 0.3)
        return product['price'] * (1 - total_discount)


# ---------------------------------------------------------------------------
# Fakes -- 간소화된 실제 구현으로 Mock을 대체한다
# ---------------------------------------------------------------------------

class FakeUserRepo:
    def __init__(self, users: dict | None = None):
        self._users = users or {}

    def add(self, user: dict) -> None:
        self._users[user['id']] = user

    def get(self, user_id: int) -> dict | None:
        return self._users.get(user_id)


class FakeProductRepo:
    def __init__(self, products: dict | None = None):
        self._products = products or {}

    def add(self, product: dict) -> None:
        self._products[product['id']] = product

    def get(self, product_id: int) -> dict | None:
        return self._products.get(product_id)


class FakePromotionService:
    def __init__(self, promotions: dict | None = None):
        self._promotions = promotions or {}

    def set_promotion(self, product_id: int, promo: dict) -> None:
        self._promotions[product_id] = promo

    def get_active_promotion(self, product_id: int) -> dict | None:
        return self._promotions.get(product_id)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user_repo():
    return FakeUserRepo()


@pytest.fixture
def product_repo():
    return FakeProductRepo()


@pytest.fixture
def promo_service():
    return FakePromotionService()


@pytest.fixture
def calculator(user_repo, product_repo, promo_service):
    return DiscountCalculator(user_repo, product_repo, promo_service)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "tier, expected_price",
    [
        ("basic", 1000000),
        ("gold", 900000),
        ("platinum", 850000),
    ],
    ids=["basic-no-discount", "gold-10%-discount", "platinum-15%-discount"],
)
def test_tier_discount(calculator, user_repo, product_repo, tier, expected_price):
    """등급별 기본 할인율이 올바르게 적용되는지 검증한다."""
    user_repo.add({'id': 1, 'name': 'Alice', 'tier': tier})
    product_repo.add({'id': 100, 'name': '노트북', 'price': 1000000})

    result = calculator.calculate(1, 100)

    assert result == expected_price


def test_promotion_discount(calculator, user_repo, product_repo, promo_service):
    """프로모션이 활성화된 상품에 프로모션 할인이 적용되는지 검증한다."""
    user_repo.add({'id': 1, 'name': 'Alice', 'tier': 'basic'})
    product_repo.add({'id': 100, 'name': '노트북', 'price': 1000000})
    promo_service.set_promotion(100, {'discount_rate': 0.2})

    result = calculator.calculate(1, 100)

    assert result == 800000


def test_combined_discount_capped_at_30_percent(
    calculator, user_repo, product_repo, promo_service,
):
    """등급 할인 + 프로모션 할인 합계가 최대 30%를 초과하지 않는지 검증한다."""
    user_repo.add({'id': 2, 'name': 'Bob', 'tier': 'platinum'})
    product_repo.add({'id': 200, 'name': '키보드', 'price': 200000})
    promo_service.set_promotion(200, {'discount_rate': 0.2})

    result = calculator.calculate(2, 200)

    assert result == 140000  # 15% + 20% = 35% -> 30%로 제한


def test_user_not_found_raises(calculator):
    """존재하지 않는 사용자 ID로 계산 시 ValueError가 발생하는지 검증한다."""
    with pytest.raises(ValueError, match='사용자'):
        calculator.calculate(999, 100)


def test_product_not_found_raises(calculator, user_repo):
    """사용자는 존재하지만 상품이 없을 때 ValueError가 발생하는지 검증한다."""
    user_repo.add({'id': 1, 'name': 'Alice', 'tier': 'gold'})

    with pytest.raises(ValueError, match='상품'):
        calculator.calculate(1, 999)
```

## 적용된 원칙 요약

| 체크리스트 항목 | 적용 여부 | 내용 |
|---|---|---|
| Multiple Act sections -> SPLIT | 해당 없음 | 모든 테스트가 단일 Act |
| Shared mutable state -> ISOLATE | 해당 없음 | 공유 상태 없음 |
| Over-mocked tests -> REPLACE with Fakes | **적용** | 3개 Mock을 Fake로 교체 |
| Mock without spec -> ADD spec | **해소** | Fake 전환으로 spec 불필요 |
| Time-dependent tests -> time-machine | 해당 없음 | 시간 의존성 없음 |
| Repetitive test cases -> parametrize | **적용** | 등급별 할인을 parametrize로 통합 |
| Complex setup -> EXTRACT to fixture | **적용** | 4개 fixture 추출 |
| Implementation-coupled assertions -> behavior | **적용** | assert_called 전부 제거 |
| Empty/weak assertions -> meaningful | 해당 없음 | 기존 assert 자체는 유의미 |
| Misplaced test level -> appropriate level | 해당 없음 | 단위 테스트 수준 적절 |

### 핵심 개선 효과

1. **Mock 3개 -> Fake 3개**: 실제 딕셔너리 기반 저장소를 사용하므로, `get()` 호출이 실제로 데이터를 조회한다. 테스트가 프로덕션 코드의 동작을 실제로 실행한다.
2. **통신 기반 검증 전량 제거**: `assert_called_once_with` 6건을 모두 제거했다. 내부 호출 순서나 횟수가 바뀌어도 테스트가 깨지지 않는다.
3. **누락 시나리오 추가**: 기존에 없던 "basic 등급 (할인 없음)"과 "프로모션만 적용" 케이스를 추가하여 테스트 커버리지를 확대했다.
4. **보일러플레이트 60% 감소**: fixture 추출로 각 테스트 함수가 자신의 시나리오에만 집중한다.
