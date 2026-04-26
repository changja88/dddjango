# 테스트 코드 리팩토링: Mock 과다 사용 개선

## 문제 분석

기존 테스트 코드의 핵심 문제:

1. **모든 테스트에서 Mock 3개를 반복 생성** -- 보일러플레이트가 과도하다.
2. **`assert_called_once_with` 남용** -- 구현 세부사항(어떤 메서드가 어떤 인자로 호출되었는가)을 검증하고 있다. 이것은 "무엇을 테스트하는가"가 아니라 "어떻게 구현되었는가"를 테스트하는 것이다. 내부 호출 순서가 바뀌거나 캐싱이 추가되면 로직은 정상인데 테스트가 깨진다.
3. **테스트 의도가 불명확** -- Mock 설정 코드가 길어서 실제로 검증하려는 비즈니스 규칙이 묻힌다.

## 리팩토링 전략

- **Fake(간단한 인메모리 구현)을 사용하여 Mock을 대체한다.** 의존성의 인터페이스를 만족하는 최소한의 구현체를 만들면, 테스트가 비즈니스 로직에만 집중할 수 있다.
- **구현 세부사항 검증(`assert_called_once_with`)을 전부 제거한다.** 테스트는 입력과 출력만 검증해야 한다.
- **`pytest.fixture`와 파라미터화를 활용하여 중복을 제거한다.**

## 리팩토링 결과

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

        total_discount = min(base_discount + promo_discount, 0.3)  # 최대 30%
        return product['price'] * (1 - total_discount)


# --- Fake 구현체 ---

class FakeUserRepo:
    def __init__(self, users: dict | None = None):
        self._users = users or {}

    def get(self, user_id: int):
        return self._users.get(user_id)


class FakeProductRepo:
    def __init__(self, products: dict | None = None):
        self._products = products or {}

    def get(self, product_id: int):
        return self._products.get(product_id)


class FakePromotionService:
    def __init__(self, promotions: dict | None = None):
        self._promotions = promotions or {}

    def get_active_promotion(self, product_id: int):
        return self._promotions.get(product_id)


# --- Fixture ---

def make_user(user_id=1, name='Alice', tier='gold'):
    return {user_id: {'id': user_id, 'name': name, 'tier': tier}}


def make_product(product_id=100, name='노트북', price=1_000_000):
    return {product_id: {'id': product_id, 'name': name, 'price': price}}


# --- 비즈니스 규칙별 테스트 ---

class TestTierDiscount:
    """등급별 할인율이 올바르게 적용되는지 검증한다."""

    @pytest.mark.parametrize('tier, expected_price', [
        ('basic', 1_000_000),    # 일반 등급: 할인 없음
        ('gold', 900_000),       # 골드: 10% 할인
        ('platinum', 850_000),   # 플래티넘: 15% 할인
    ])
    def test_tier_discount_without_promotion(self, tier, expected_price):
        calc = DiscountCalculator(
            user_repo=FakeUserRepo(make_user(tier=tier)),
            product_repo=FakeProductRepo(make_product(price=1_000_000)),
            promotion_service=FakePromotionService(),
        )

        assert calc.calculate(1, 100) == expected_price


class TestPromotionDiscount:
    """프로모션 할인이 등급 할인과 올바르게 합산되는지 검증한다."""

    def test_promotion_adds_to_tier_discount(self):
        calc = DiscountCalculator(
            user_repo=FakeUserRepo(make_user(tier='gold')),
            product_repo=FakeProductRepo(make_product(price=1_000_000)),
            promotion_service=FakePromotionService({100: {'discount_rate': 0.1}}),
        )

        # 골드 10% + 프로모션 10% = 20% 할인
        assert calc.calculate(1, 100) == 800_000

    def test_promotion_only_without_tier_discount(self):
        calc = DiscountCalculator(
            user_repo=FakeUserRepo(make_user(tier='basic')),
            product_repo=FakeProductRepo(make_product(price=200_000)),
            promotion_service=FakePromotionService({100: {'discount_rate': 0.2}}),
        )

        # 등급 할인 0% + 프로모션 20% = 20% 할인
        assert calc.calculate(1, 100) == 160_000


class TestMaxDiscountCap:
    """총 할인율이 30%를 초과하지 않는지 검증한다."""

    def test_discount_capped_at_30_percent(self):
        calc = DiscountCalculator(
            user_repo=FakeUserRepo(make_user(tier='platinum')),
            product_repo=FakeProductRepo(make_product(product_id=200, price=200_000)),
            promotion_service=FakePromotionService({200: {'discount_rate': 0.2}}),
        )

        # 플래티넘 15% + 프로모션 20% = 35% -> 30%로 캡
        assert calc.calculate(1, 200) == 140_000

    def test_discount_exactly_at_cap(self):
        calc = DiscountCalculator(
            user_repo=FakeUserRepo(make_user(tier='gold')),
            product_repo=FakeProductRepo(make_product(price=100_000)),
            promotion_service=FakePromotionService({100: {'discount_rate': 0.2}}),
        )

        # 골드 10% + 프로모션 20% = 정확히 30%
        assert calc.calculate(1, 100) == 70_000


class TestValidation:
    """존재하지 않는 사용자/상품에 대한 에러 처리를 검증한다."""

    def test_raises_error_for_unknown_user(self):
        calc = DiscountCalculator(
            user_repo=FakeUserRepo(),  # 빈 저장소
            product_repo=FakeProductRepo(make_product()),
            promotion_service=FakePromotionService(),
        )

        with pytest.raises(ValueError, match='사용자'):
            calc.calculate(999, 100)

    def test_raises_error_for_unknown_product(self):
        calc = DiscountCalculator(
            user_repo=FakeUserRepo(make_user()),
            product_repo=FakeProductRepo(),  # 빈 저장소
            promotion_service=FakePromotionService(),
        )

        with pytest.raises(ValueError, match='상품'):
            calc.calculate(1, 999)
```

## 변경 요약

| 항목 | Before | After |
|------|--------|-------|
| Mock 사용 | `unittest.mock.Mock` 3개를 매 테스트마다 생성 | Fake 클래스 3개를 한 번 정의하고 재사용 |
| 구현 세부사항 검증 | `assert_called_once_with`로 호출 여부 검증 | 제거 -- 입력/출력만 검증 |
| 테스트 구조 | 플랫한 함수 4개 | 비즈니스 규칙별 클래스 4개로 그룹화 |
| 테스트 케이스 수 | 4개 | 7개 (기존 시나리오 + 빠져있던 basic 등급, 캡 경계값 추가) |
| 파라미터화 | 없음 | 등급별 할인 테스트에 `@pytest.mark.parametrize` 적용 |

## 핵심 원칙

**Mock은 "제어할 수 없는 외부 의존성"을 격리할 때 사용하는 도구이지, 모든 의존성을 대체하는 도구가 아니다.** 이 경우 `user_repo`, `product_repo`, `promotion_service`는 단순한 데이터 조회 인터페이스이므로, 인메모리 Fake로 대체하면 다음 이점을 얻는다:

1. **테스트가 비즈니스 규칙을 직접 표현한다** -- "골드 등급은 10% 할인"이 코드에서 바로 읽힌다.
2. **리팩토링 내성이 높아진다** -- 내부 구현이 바뀌어도(예: 캐싱 추가, 호출 순서 변경) 결과만 같으면 테스트가 통과한다.
3. **실패 시 원인 파악이 쉽다** -- "이 입력에 대해 이 출력이 나와야 한다"가 명확하므로, 어떤 비즈니스 규칙이 깨졌는지 바로 알 수 있다.
