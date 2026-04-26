# PaymentProcessor 테스트

## 의존성

```
pytest
pytest-asyncio
aioresponses
time-machine
```

`pyproject.toml` 설정:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## 테스트 코드

```python
from datetime import datetime
from unittest.mock import AsyncMock, create_autospec

import aiohttp
import pytest
import time_machine
from aioresponses import aioresponses

from payment import (
    PaymentProcessor,
    PaymentRepository,
    PaymentResult,
    PaymentStatus,
    SlackNotifier,
)

API_URL = "https://pay.example.com"
FROZEN_TIME = "2024-06-15 14:30:00"


@pytest.fixture
def repo():
    return create_autospec(PaymentRepository, instance=True)


@pytest.fixture
def notifier():
    return create_autospec(SlackNotifier, instance=True)


@pytest.fixture
def processor(repo, notifier):
    return PaymentProcessor(api_url=API_URL, repo=repo, notifier=notifier)


class TestPaymentSuccess:
    """결제 API가 200을 반환하는 정상 흐름"""

    @time_machine.travel(FROZEN_TIME)
    async def test_returns_success_result(self, processor):
        """API 성공 시 transaction_id, 금액, SUCCESS 상태를 포함한 결과를 반환한다."""
        with aioresponses() as mocked:
            mocked.post(
                f"{API_URL}/payments",
                payload={"transaction_id": "tx-abc-123"},
                status=200,
            )

            result = await processor.process_payment(order_id=1001, amount=50000.0)

        assert result.transaction_id == "tx-abc-123"
        assert result.amount == 50000.0
        assert result.status == PaymentStatus.SUCCESS
        assert result.processed_at == datetime(2024, 6, 15, 14, 30, 0)

    async def test_saves_result_to_repository(self, processor, repo):
        with aioresponses() as mocked:
            mocked.post(
                f"{API_URL}/payments",
                payload={"transaction_id": "tx-abc-123"},
                status=200,
            )

            result = await processor.process_payment(order_id=1001, amount=50000.0)

        repo.save.assert_awaited_once_with(result)

    async def test_does_not_send_slack_alert(self, processor, notifier):
        with aioresponses() as mocked:
            mocked.post(
                f"{API_URL}/payments",
                payload={"transaction_id": "tx-abc-123"},
                status=200,
            )

            await processor.process_payment(order_id=1001, amount=50000.0)

        notifier.send_alert.assert_not_awaited()

    async def test_sends_correct_request_payload(self, processor):
        """API에 order_id, amount, currency를 포함한 JSON을 전송한다."""
        with aioresponses() as mocked:
            mocked.post(
                f"{API_URL}/payments",
                payload={"transaction_id": "tx-1"},
                status=200,
            )

            await processor.process_payment(
                order_id=42, amount=9900.0, currency="USD"
            )

            request = mocked.requests[("POST", API_URL + "/payments")][0]
            import json

            body = json.loads(request.kwargs["json"])
            assert body == {"order_id": 42, "amount": 9900.0, "currency": "USD"}


class TestPaymentApiFailure:
    """결제 API가 비-200 상태를 반환하는 실패 흐름"""

    @time_machine.travel(FROZEN_TIME)
    async def test_returns_failed_result(self, processor):
        """API가 500을 반환하면 빈 transaction_id와 FAILED 상태를 반환한다."""
        with aioresponses() as mocked:
            mocked.post(f"{API_URL}/payments", status=500)

            result = await processor.process_payment(order_id=2001, amount=30000.0)

        assert result.transaction_id == ""
        assert result.amount == 30000.0
        assert result.status == PaymentStatus.FAILED
        assert result.processed_at == datetime(2024, 6, 15, 14, 30, 0)

    async def test_saves_failed_result_to_repository(self, processor, repo):
        with aioresponses() as mocked:
            mocked.post(f"{API_URL}/payments", status=500)

            result = await processor.process_payment(order_id=2001, amount=30000.0)

        repo.save.assert_awaited_once_with(result)

    async def test_sends_slack_alert_with_failure_details(self, processor, notifier):
        with aioresponses() as mocked:
            mocked.post(f"{API_URL}/payments", status=500)

            await processor.process_payment(order_id=2001, amount=30000.0)

        notifier.send_alert.assert_awaited_once_with(
            "#payment-alerts",
            "결제 실패: order=2001, status=failed",
        )

    @pytest.mark.parametrize("status_code", [400, 403, 404, 502, 503])
    async def test_non_200_status_codes_all_result_in_failure(
        self, processor, status_code
    ):
        with aioresponses() as mocked:
            mocked.post(f"{API_URL}/payments", status=status_code)

            result = await processor.process_payment(order_id=99, amount=1000.0)

        assert result.status == PaymentStatus.FAILED


class TestPaymentNetworkError:
    """네트워크 오류로 API 호출 자체가 실패하는 흐름"""

    @time_machine.travel(FROZEN_TIME)
    async def test_returns_timeout_result(self, processor):
        """ClientError 발생 시 빈 transaction_id와 TIMEOUT 상태를 반환한다."""
        with aioresponses() as mocked:
            mocked.post(
                f"{API_URL}/payments",
                exception=aiohttp.ClientError("connection refused"),
            )

            result = await processor.process_payment(order_id=3001, amount=15000.0)

        assert result.transaction_id == ""
        assert result.amount == 15000.0
        assert result.status == PaymentStatus.TIMEOUT
        assert result.processed_at == datetime(2024, 6, 15, 14, 30, 0)

    async def test_saves_timeout_result_to_repository(self, processor, repo):
        with aioresponses() as mocked:
            mocked.post(
                f"{API_URL}/payments",
                exception=aiohttp.ClientError("timeout"),
            )

            result = await processor.process_payment(order_id=3001, amount=15000.0)

        repo.save.assert_awaited_once_with(result)

    async def test_sends_slack_alert_with_timeout_details(self, processor, notifier):
        with aioresponses() as mocked:
            mocked.post(
                f"{API_URL}/payments",
                exception=aiohttp.ClientError("timeout"),
            )

            await processor.process_payment(order_id=3001, amount=15000.0)

        notifier.send_alert.assert_awaited_once_with(
            "#payment-alerts",
            "결제 실패: order=3001, status=timeout",
        )


class TestDefaultCurrency:
    """currency 파라미터 기본값 검증"""

    async def test_defaults_to_krw(self, processor):
        with aioresponses() as mocked:
            mocked.post(
                f"{API_URL}/payments",
                payload={"transaction_id": "tx-1"},
                status=200,
            )

            await processor.process_payment(order_id=1, amount=1000.0)

            request = mocked.requests[("POST", API_URL + "/payments")][0]
            import json

            body = json.loads(request.kwargs["json"])
            assert body["currency"] == "KRW"
```

## 설계 근거

**테스트 구조**: 테스트 클래스를 세 가지 핵심 시나리오(성공/API 실패/네트워크 오류)로 분리하고 각 테스트가 하나의 행위만 검증하도록 AAA 패턴을 적용했다.

**검증 우선순위**: 반환값 검증(출력 기반)을 우선하고, repository 저장과 슬랙 알림처럼 외부 부수효과만 communication 기반(assert_awaited)으로 검증했다.

**테스트 더블 선택**:
- `PaymentRepository`, `SlackNotifier` -- `create_autospec`으로 생성하여 실제 인터페이스와의 API 드리프트를 방지했다. 이들은 외부 의존성(DB, 슬랙)이므로 Mock이 적절하다.
- HTTP 외부 호출 -- `aioresponses`로 aiohttp 요청을 인터셉트하여 네트워크 격리를 달성했다.

**시간 모킹**: `datetime.now()` 호출의 결정성을 확보하기 위해 `time-machine`을 사용했다. freezegun 대비 100-200배 빠르며, C 레벨에서 시간 함수를 교체하므로 패치 대상 모듈 경로를 신경 쓸 필요가 없다.

**파라미터화**: 비-200 응답 코드에 대해 `@pytest.mark.parametrize`를 적용하여 반복적인 테스트 케이스를 제거했다.
