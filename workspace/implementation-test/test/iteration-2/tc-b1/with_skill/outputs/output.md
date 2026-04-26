# SubscriptionService 테스트

## 설계 판단

- **Repository**: Fake 객체를 사용한다. repo는 내부 협력 객체이므로 Mock이 아닌 실제 동작하는 간소화된 구현(Fake)으로 대체한다. 이렇게 하면 핵심 비즈니스 로직을 실제 객체로 테스트할 수 있다.
- **시간**: `time-machine`을 사용한다. CPython 프로젝트에서 freezegun보다 100~200배 빠르며, `datetime.now()` 호출을 C 레벨에서 일괄 패치한다.
- **HTTP**: `responses` 라이브러리를 사용한다. 대상 코드가 `requests` 라이브러리를 사용하므로 가장 적합하다.
- **검증 우선순위**: 출력 기반 검증(반환값 assert)을 우선하고, 외부 API 호출 여부만 통신 기반 검증을 적용한다.

## 테스트 코드

```python
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import Enum

import pytest
import responses
import time_machine

# ── Production code (테스트 대상) ──────────────────────────────


class PlanType(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class Subscription:
    id: int
    user_email: str
    plan: PlanType
    started_at: datetime
    expires_at: datetime
    is_active: bool = True


# ── Fake Repository ────────────────────────────────────────────


class FakeSubscriptionRepo:
    """메모리 기반 Fake Repository. 실제 DB 동작을 간소화하여 재현한다."""

    def __init__(self) -> None:
        self._store: dict[int, Subscription] = {}
        self._next_id = 1

    def save(self, sub: Subscription) -> Subscription:
        if sub.id == 0:
            sub = replace(sub, id=self._next_id)
            self._next_id += 1
        self._store[sub.id] = sub
        return sub

    def find_by_id(self, subscription_id: int) -> Subscription | None:
        return self._store.get(subscription_id)

    def find_all_active(self) -> list[Subscription]:
        return [s for s in self._store.values() if s.is_active]


# ── Fixtures ───────────────────────────────────────────────────

PAYMENT_API_URL = "https://payments.example.com"


@pytest.fixture
def repo():
    return FakeSubscriptionRepo()


@pytest.fixture
def service(repo):
    from subscription_service import SubscriptionService

    return SubscriptionService(repo, PAYMENT_API_URL)


# ── create_subscription ───────────────────────────────────────


class TestCreateSubscription:

    @time_machine.travel("2024-06-01 12:00:00", tick=False)
    def test_monthly_plan_expires_in_30_days(self, service, repo):
        sub = service.create_subscription("alice@example.com", PlanType.MONTHLY)

        assert sub.id == 1
        assert sub.user_email == "alice@example.com"
        assert sub.plan == PlanType.MONTHLY
        assert sub.started_at == datetime(2024, 6, 1, 12, 0, 0)
        assert sub.expires_at == datetime(2024, 7, 1, 12, 0, 0)
        assert sub.is_active is True

    @time_machine.travel("2024-06-01 12:00:00", tick=False)
    def test_yearly_plan_expires_in_365_days(self, service, repo):
        sub = service.create_subscription("bob@example.com", PlanType.YEARLY)

        assert sub.plan == PlanType.YEARLY
        assert sub.expires_at == datetime(2025, 6, 1, 12, 0, 0)

    @time_machine.travel("2024-06-01 12:00:00", tick=False)
    def test_subscription_is_persisted_in_repo(self, service, repo):
        sub = service.create_subscription("carol@example.com", PlanType.MONTHLY)

        persisted = repo.find_by_id(sub.id)
        assert persisted is not None
        assert persisted.user_email == "carol@example.com"


# ── is_expired ─────────────────────────────────────────────────


class TestIsExpired:

    @time_machine.travel("2024-06-01 12:00:00", tick=False)
    def test_not_expired_before_expiry_date(self, service, repo):
        sub = Subscription(
            id=0,
            user_email="alice@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 7, 1),
        )
        saved = repo.save(sub)

        assert service.is_expired(saved.id) is False

    @time_machine.travel("2024-08-01 12:00:00", tick=False)
    def test_expired_after_expiry_date(self, service, repo):
        sub = Subscription(
            id=0,
            user_email="alice@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 7, 1),
        )
        saved = repo.save(sub)

        assert service.is_expired(saved.id) is True

    def test_raises_when_subscription_not_found(self, service):
        with pytest.raises(ValueError, match="구독 999을 찾을 수 없습니다"):
            service.is_expired(999)


# ── renew ──────────────────────────────────────────────────────


class TestRenew:

    @responses.activate
    @time_machine.travel("2024-06-15 10:00:00", tick=False)
    def test_monthly_renewal_extends_expiry_by_30_days(self, service, repo):
        """결제 성공 시 만료일이 현재 시점 기준 +30일로 갱신된다."""
        sub = Subscription(
            id=0,
            user_email="alice@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 15),
            expires_at=datetime(2024, 6, 14),
        )
        saved = repo.save(sub)
        responses.add(
            responses.POST,
            f"{PAYMENT_API_URL}/charge",
            json={"status": "ok"},
            status=200,
        )

        renewed = service.renew(saved.id)

        assert renewed.expires_at == datetime(2024, 7, 15, 10, 0, 0)

    @responses.activate
    @time_machine.travel("2024-06-15 10:00:00", tick=False)
    def test_yearly_renewal_extends_expiry_by_365_days(self, service, repo):
        sub = Subscription(
            id=0,
            user_email="bob@example.com",
            plan=PlanType.YEARLY,
            started_at=datetime(2023, 6, 15),
            expires_at=datetime(2024, 6, 15),
        )
        saved = repo.save(sub)
        responses.add(
            responses.POST,
            f"{PAYMENT_API_URL}/charge",
            json={"status": "ok"},
            status=200,
        )

        renewed = service.renew(saved.id)

        assert renewed.expires_at == datetime(2025, 6, 15, 10, 0, 0)

    @responses.activate
    def test_sends_correct_payment_request(self, service, repo):
        """결제 API에 올바른 이메일과 플랜 정보가 전달되는지 검증한다."""
        sub = Subscription(
            id=0,
            user_email="alice@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 6, 1),
        )
        saved = repo.save(sub)
        responses.add(
            responses.POST,
            f"{PAYMENT_API_URL}/charge",
            json={"status": "ok"},
            status=200,
        )

        service.renew(saved.id)

        assert len(responses.calls) == 1
        request_body = responses.calls[0].request.body
        import json

        payload = json.loads(request_body)
        assert payload == {"email": "alice@example.com", "plan": "monthly"}

    @responses.activate
    def test_raises_on_payment_failure(self, service, repo):
        sub = Subscription(
            id=0,
            user_email="alice@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 6, 1),
        )
        saved = repo.save(sub)
        responses.add(
            responses.POST,
            f"{PAYMENT_API_URL}/charge",
            json={"error": "insufficient funds"},
            status=402,
        )

        with pytest.raises(RuntimeError, match="결제 실패"):
            service.renew(saved.id)

    def test_raises_when_subscription_not_found(self, service):
        with pytest.raises(ValueError, match="구독 999을 찾을 수 없습니다"):
            service.renew(999)

    def test_raises_when_subscription_inactive(self, service, repo):
        sub = Subscription(
            id=0,
            user_email="alice@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 6, 1),
            is_active=False,
        )
        saved = repo.save(sub)

        with pytest.raises(ValueError, match="비활성 구독은 갱신할 수 없습니다"):
            service.renew(saved.id)


# ── cancel ─────────────────────────────────────────────────────


class TestCancel:

    def test_sets_subscription_inactive(self, service, repo):
        sub = Subscription(
            id=0,
            user_email="alice@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 6, 1),
        )
        saved = repo.save(sub)

        cancelled = service.cancel(saved.id)

        assert cancelled.is_active is False

    def test_persists_cancellation(self, service, repo):
        sub = Subscription(
            id=0,
            user_email="alice@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 6, 1),
        )
        saved = repo.save(sub)

        service.cancel(saved.id)

        persisted = repo.find_by_id(saved.id)
        assert persisted.is_active is False

    def test_raises_when_subscription_not_found(self, service):
        with pytest.raises(ValueError, match="구독 999을 찾을 수 없습니다"):
            service.cancel(999)


# ── get_expiring_soon ──────────────────────────────────────────


class TestGetExpiringSoon:

    @time_machine.travel("2024-06-01 00:00:00", tick=False)
    def test_returns_subscriptions_expiring_within_threshold(self, service, repo):
        """기본 7일 이내 만료 구독만 반환한다."""
        expiring = Subscription(
            id=0,
            user_email="expiring@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 6, 5),
        )
        not_expiring = Subscription(
            id=0,
            user_email="safe@example.com",
            plan=PlanType.YEARLY,
            started_at=datetime(2024, 1, 1),
            expires_at=datetime(2024, 12, 31),
        )
        repo.save(expiring)
        repo.save(not_expiring)

        result = service.get_expiring_soon()

        assert len(result) == 1
        assert result[0].user_email == "expiring@example.com"

    @time_machine.travel("2024-06-01 00:00:00", tick=False)
    def test_custom_threshold_days(self, service, repo):
        sub = Subscription(
            id=0,
            user_email="alice@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 6, 20),
        )
        repo.save(sub)

        within_30 = service.get_expiring_soon(days=30)
        within_7 = service.get_expiring_soon(days=7)

        assert len(within_30) == 1
        assert len(within_7) == 0

    @time_machine.travel("2024-06-01 00:00:00", tick=False)
    def test_excludes_inactive_subscriptions(self, service, repo):
        inactive = Subscription(
            id=0,
            user_email="inactive@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 6, 3),
            is_active=False,
        )
        repo.save(inactive)

        result = service.get_expiring_soon()

        assert len(result) == 0

    @time_machine.travel("2024-06-01 00:00:00", tick=False)
    def test_includes_subscription_expiring_exactly_on_threshold(self, service, repo):
        """만료일이 threshold와 정확히 같은 경우도 포함된다 (경계값)."""
        boundary = Subscription(
            id=0,
            user_email="boundary@example.com",
            plan=PlanType.MONTHLY,
            started_at=datetime(2024, 5, 1),
            expires_at=datetime(2024, 6, 8, 0, 0, 0),
        )
        repo.save(boundary)

        result = service.get_expiring_soon(days=7)

        assert len(result) == 1

    @time_machine.travel("2024-06-01 00:00:00", tick=False)
    def test_returns_empty_when_no_active_subscriptions(self, service, repo):
        result = service.get_expiring_soon()

        assert result == []


# ── Parametrized: plan duration mapping ────────────────────────


class TestPlanDuration:

    @pytest.mark.parametrize(
        "plan, expected_days",
        [
            (PlanType.MONTHLY, 30),
            (PlanType.YEARLY, 365),
        ],
    )
    @time_machine.travel("2024-01-01 00:00:00", tick=False)
    def test_plan_determines_subscription_duration(self, service, plan, expected_days):
        sub = service.create_subscription("test@example.com", plan)

        expected_expiry = datetime(2024, 1, 1) + timedelta(days=expected_days)
        assert sub.expires_at == expected_expiry
```

## 적용한 원칙 요약

| 원칙 | 적용 |
|------|------|
| AAA 구조 | 모든 테스트가 Arrange-Act-Assert 단일 흐름. Act은 한 줄 |
| Fake Repository | repo는 내부 협력 객체이므로 Mock 대신 메모리 기반 Fake 사용 |
| 외부 의존성만 Mock | 결제 API(`requests.post`)만 `responses`로 모킹 |
| time-machine | `datetime.now()` 의존 로직을 결정적으로 테스트 (freezegun 대비 100~200x 빠름) |
| responses | `requests` 라이브러리의 HTTP 호출을 인터셉트 |
| 출력 기반 검증 우선 | 반환값 assert를 우선하고, API 호출 검증은 `test_sends_correct_payment_request`에서만 수행 |
| parametrize | 월간/연간 플랜의 기간 매핑을 데이터 주도 테스트로 검증 |
| 경계값 테스트 | threshold 정확히 일치하는 경우의 포함 여부 검증 |
| 독립성(FIRST-I) | 각 테스트가 자체 데이터를 생성. fixture는 function 스코프로 격리 |
| 반복 가능(FIRST-R) | 시간을 고정하여 어떤 환경/시점에서도 동일 결과 |
