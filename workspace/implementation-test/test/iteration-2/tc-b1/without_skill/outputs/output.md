# SubscriptionService 테스트

## 분석

이 서비스에는 테스트 시 주의해야 할 두 가지 핵심 요소가 있다.

1. **시간 의존성** -- `datetime.now()`를 직접 호출하므로 `freezegun` 또는 `unittest.mock.patch`로 시간을 고정해야 한다.
2. **외부 API 호출** -- `requests.post`로 결제 API를 호출하므로 mock 처리가 필요하다.
3. **Repository 의존성** -- `self.repo`는 인터페이스만 사용하므로 fake 또는 mock으로 대체한다.

## 테스트 전략

| 관심사 | 처리 방식 |
|--------|-----------|
| `datetime.now()` | `freezegun.freeze_time` 데코레이터로 시간 고정 |
| `requests.post` | `unittest.mock.patch`로 mock 처리 |
| `repo` | 인메모리 Fake Repository 구현 |

## 테스트 코드

```python
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from dataclasses import replace
from freezegun import freeze_time

from subscription import (
    Subscription,
    SubscriptionService,
    PlanType,
)


# ---------------------------------------------------------------------------
# Fake Repository -- 외부 DB 의존성 제거
# ---------------------------------------------------------------------------
class FakeSubscriptionRepo:
    def __init__(self):
        self._store: dict[int, Subscription] = {}
        self._next_id = 1

    def save(self, sub: Subscription) -> Subscription:
        if sub.id == 0:
            sub.id = self._next_id
            self._next_id += 1
        self._store[sub.id] = sub
        return sub

    def find_by_id(self, subscription_id: int) -> Subscription | None:
        return self._store.get(subscription_id)

    def find_all_active(self) -> list[Subscription]:
        return [s for s in self._store.values() if s.is_active]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def repo():
    return FakeSubscriptionRepo()


@pytest.fixture
def service(repo):
    return SubscriptionService(repo=repo, payment_api_url="https://pay.example.com")


# ---------------------------------------------------------------------------
# create_subscription
# ---------------------------------------------------------------------------
class TestCreateSubscription:

    @freeze_time("2025-01-15 10:00:00")
    def test_monthly_plan_sets_30_day_expiry(self, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        assert sub.id == 1
        assert sub.user_email == "user@test.com"
        assert sub.plan == PlanType.MONTHLY
        assert sub.started_at == datetime(2025, 1, 15, 10, 0, 0)
        assert sub.expires_at == datetime(2025, 2, 14, 10, 0, 0)
        assert sub.is_active is True

    @freeze_time("2025-01-15 10:00:00")
    def test_yearly_plan_sets_365_day_expiry(self, service):
        sub = service.create_subscription("user@test.com", PlanType.YEARLY)

        assert sub.expires_at == datetime(2026, 1, 15, 10, 0, 0)
        assert sub.plan == PlanType.YEARLY

    @freeze_time("2025-01-15 10:00:00")
    def test_created_subscription_is_persisted(self, service, repo):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        persisted = repo.find_by_id(sub.id)
        assert persisted is not None
        assert persisted.user_email == "user@test.com"

    @freeze_time("2025-03-01 00:00:00")
    def test_multiple_subscriptions_get_unique_ids(self, service):
        sub1 = service.create_subscription("a@test.com", PlanType.MONTHLY)
        sub2 = service.create_subscription("b@test.com", PlanType.YEARLY)

        assert sub1.id != sub2.id


# ---------------------------------------------------------------------------
# is_expired
# ---------------------------------------------------------------------------
class TestIsExpired:

    @freeze_time("2025-01-15 10:00:00")
    def test_not_expired_before_expiry_date(self, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        # 만료일 하루 전으로 이동
        with freeze_time("2025-02-13 10:00:00"):
            assert service.is_expired(sub.id) is False

    @freeze_time("2025-01-15 10:00:00")
    def test_expired_after_expiry_date(self, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        # 만료일 하루 후로 이동
        with freeze_time("2025-02-15 10:00:00"):
            assert service.is_expired(sub.id) is True

    @freeze_time("2025-01-15 10:00:00")
    def test_expired_exactly_at_expiry_boundary(self, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        # 만료 시각에서 1초 후 -- datetime.now() > expires_at 이므로 expired
        with freeze_time("2025-02-14 10:00:01"):
            assert service.is_expired(sub.id) is True

    @freeze_time("2025-01-15 10:00:00")
    def test_not_expired_exactly_at_expiry_time(self, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        # 정확히 만료 시각 -- now > expires_at 가 아니므로 (equal) not expired
        with freeze_time("2025-02-14 10:00:00"):
            assert service.is_expired(sub.id) is False

    def test_raises_for_nonexistent_subscription(self, service):
        with pytest.raises(ValueError, match="구독 999을 찾을 수 없습니다"):
            service.is_expired(999)


# ---------------------------------------------------------------------------
# renew
# ---------------------------------------------------------------------------
class TestRenew:

    @freeze_time("2025-01-15 10:00:00")
    @patch("subscription.requests.post")
    def test_monthly_renewal_extends_from_now(self, mock_post, service):
        mock_post.return_value = MagicMock(status_code=200)
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        # 20일 후 갱신
        with freeze_time("2025-02-04 10:00:00"):
            renewed = service.renew(sub.id)

        assert renewed.expires_at == datetime(2025, 2, 4, 10, 0, 0) + timedelta(days=30)

    @freeze_time("2025-01-15 10:00:00")
    @patch("subscription.requests.post")
    def test_yearly_renewal_extends_365_days(self, mock_post, service):
        mock_post.return_value = MagicMock(status_code=200)
        sub = service.create_subscription("user@test.com", PlanType.YEARLY)

        with freeze_time("2025-06-01 00:00:00"):
            renewed = service.renew(sub.id)

        assert renewed.expires_at == datetime(2025, 6, 1) + timedelta(days=365)

    @freeze_time("2025-01-15 10:00:00")
    @patch("subscription.requests.post")
    def test_renew_calls_payment_api_with_correct_payload(self, mock_post, service):
        mock_post.return_value = MagicMock(status_code=200)
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        service.renew(sub.id)

        mock_post.assert_called_once_with(
            "https://pay.example.com/charge",
            json={"email": "user@test.com", "plan": "monthly"},
        )

    @freeze_time("2025-01-15 10:00:00")
    @patch("subscription.requests.post")
    def test_renew_raises_on_payment_failure(self, mock_post, service):
        mock_post.return_value = MagicMock(status_code=402)
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        with pytest.raises(RuntimeError, match="결제 실패"):
            service.renew(sub.id)

    @freeze_time("2025-01-15 10:00:00")
    @patch("subscription.requests.post")
    def test_renew_does_not_update_expiry_on_payment_failure(self, mock_post, service):
        mock_post.return_value = MagicMock(status_code=500)
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)
        original_expiry = sub.expires_at

        with pytest.raises(RuntimeError):
            service.renew(sub.id)

        assert service.repo.find_by_id(sub.id).expires_at == original_expiry

    @freeze_time("2025-01-15 10:00:00")
    @patch("subscription.requests.post")
    def test_renew_inactive_subscription_raises(self, mock_post, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)
        service.cancel(sub.id)

        with pytest.raises(ValueError, match="비활성 구독은 갱신할 수 없습니다"):
            service.renew(sub.id)

        mock_post.assert_not_called()

    def test_renew_nonexistent_subscription_raises(self, service):
        with pytest.raises(ValueError, match="구독 999을 찾을 수 없습니다"):
            service.renew(999)


# ---------------------------------------------------------------------------
# cancel
# ---------------------------------------------------------------------------
class TestCancel:

    @freeze_time("2025-01-15 10:00:00")
    def test_cancel_deactivates_subscription(self, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        cancelled = service.cancel(sub.id)

        assert cancelled.is_active is False

    @freeze_time("2025-01-15 10:00:00")
    def test_cancel_preserves_expiry_date(self, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)
        original_expiry = sub.expires_at

        cancelled = service.cancel(sub.id)

        assert cancelled.expires_at == original_expiry

    @freeze_time("2025-01-15 10:00:00")
    def test_cancel_persists_state(self, service, repo):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)
        service.cancel(sub.id)

        persisted = repo.find_by_id(sub.id)
        assert persisted.is_active is False

    def test_cancel_nonexistent_subscription_raises(self, service):
        with pytest.raises(ValueError, match="구독 999을 찾을 수 없습니다"):
            service.cancel(999)


# ---------------------------------------------------------------------------
# get_expiring_soon
# ---------------------------------------------------------------------------
class TestGetExpiringSoon:

    @freeze_time("2025-01-15 10:00:00")
    def test_returns_subscriptions_expiring_within_default_7_days(self, service):
        # 만료까지 30일 남은 구독 생성 (2025-02-14)
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        # 만료 6일 전으로 이동 -- threshold = now + 7 = 2025-02-15, expires = 2025-02-14
        with freeze_time("2025-02-08 10:00:00"):
            expiring = service.get_expiring_soon()

        assert len(expiring) == 1
        assert expiring[0].id == sub.id

    @freeze_time("2025-01-15 10:00:00")
    def test_excludes_subscriptions_not_expiring_soon(self, service):
        service.create_subscription("user@test.com", PlanType.MONTHLY)

        # 만료까지 20일 남은 시점 -- threshold = now + 7, expires_at 는 그 이후
        with freeze_time("2025-01-25 10:00:00"):
            expiring = service.get_expiring_soon()

        assert len(expiring) == 0

    @freeze_time("2025-01-15 10:00:00")
    def test_custom_days_parameter(self, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        # 만료 15일 전 시점에서 days=14로 조회 -- 포함되지 않음
        with freeze_time("2025-01-30 10:00:00"):
            assert len(service.get_expiring_soon(days=14)) == 0

        # 만료 15일 전 시점에서 days=16으로 조회 -- 포함됨
        with freeze_time("2025-01-30 10:00:00"):
            assert len(service.get_expiring_soon(days=16)) == 1

    @freeze_time("2025-01-15 10:00:00")
    def test_excludes_cancelled_subscriptions(self, service):
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)
        service.cancel(sub.id)

        with freeze_time("2025-02-10 10:00:00"):
            expiring = service.get_expiring_soon()

        assert len(expiring) == 0

    @freeze_time("2025-01-15 10:00:00")
    def test_multiple_subscriptions_mixed(self, service):
        # monthly: 2025-02-14 만료
        sub_m = service.create_subscription("m@test.com", PlanType.MONTHLY)
        # yearly: 2026-01-15 만료
        sub_y = service.create_subscription("y@test.com", PlanType.YEARLY)

        # 2025-02-10 기준 -- monthly만 7일 이내 만료
        with freeze_time("2025-02-10 10:00:00"):
            expiring = service.get_expiring_soon()

        assert len(expiring) == 1
        assert expiring[0].user_email == "m@test.com"

    @freeze_time("2025-01-15 10:00:00")
    def test_already_expired_subscription_is_included(self, service):
        """이미 만료된 활성 구독도 expires_at <= threshold 이므로 포함된다."""
        sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

        with freeze_time("2025-03-01 10:00:00"):
            expiring = service.get_expiring_soon()

        assert len(expiring) == 1
```

## 테스트 설계 근거

### 시간 제어 -- `freezegun`

`datetime.now()`를 직접 호출하는 코드에서는 테스트 실행 시점에 따라 결과가 달라진다. `freezegun`의 `freeze_time`을 사용하면:

- 데코레이터로 테스트 전체의 시간을 고정
- 컨텍스트 매니저로 테스트 중간에 시간을 이동
- `datetime.now()` 반환값이 고정되므로 결정론적 테스트 가능

예시: 구독 생성 시점과 만료 확인 시점을 각각 다른 시각으로 고정하여, 만료 경계값을 정확히 검증한다.

```python
@freeze_time("2025-01-15 10:00:00")
def test_expired_exactly_at_expiry_boundary(self, service):
    sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

    with freeze_time("2025-02-14 10:00:01"):  # 만료 시각 1초 후
        assert service.is_expired(sub.id) is True
```

### 외부 API Mock -- `unittest.mock.patch`

`renew` 메서드는 `requests.post`로 결제 API를 호출한다. 테스트에서는:

- `@patch("subscription.requests.post")`로 실제 HTTP 호출 차단
- `mock_post.return_value`의 `status_code`를 제어하여 성공/실패 시나리오 분리
- `mock_post.assert_called_once_with(...)`로 올바른 URL과 payload 전송 검증
- 결제 실패 시 만료일이 변경되지 않는 것까지 확인

```python
@patch("subscription.requests.post")
def test_renew_raises_on_payment_failure(self, mock_post, service):
    mock_post.return_value = MagicMock(status_code=402)
    sub = service.create_subscription("user@test.com", PlanType.MONTHLY)

    with pytest.raises(RuntimeError, match="결제 실패"):
        service.renew(sub.id)
```

### Fake Repository

Mock 대신 Fake 패턴을 선택한 이유:

- Repository는 상태를 가지므로 `save` 후 `find_by_id`로 조회하는 흐름이 자연스러워야 한다
- Mock으로는 `save`의 반환값과 `find_by_id`의 반환값을 일일이 설정해야 하고, 상태 변경 추적이 번거롭다
- Fake는 실제 동작과 동일한 인메모리 구현이므로 테스트가 더 견고하다

### 테스트 커버리지 요약

| 메서드 | 테스트 수 | 주요 시나리오 |
|--------|-----------|---------------|
| `create_subscription` | 4 | monthly/yearly 기간, 영속화, ID 유일성 |
| `is_expired` | 5 | 만료 전/후, 경계값(equal, +1초), 미존재 |
| `renew` | 7 | 기간 연장, API payload 검증, 결제 실패, 비활성 구독, 미존재 |
| `cancel` | 4 | 비활성화, 만료일 보존, 영속화, 미존재 |
| `get_expiring_soon` | 6 | 기본 7일, 커스텀 days, 취소 제외, 혼합, 이미 만료 포함 |
| **합계** | **26** | |
