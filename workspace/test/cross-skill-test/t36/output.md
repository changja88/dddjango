# T36 (Test 35): async 테스트에 TaskGroup과 except* 패턴 적용 컨벤션

**Skill:** implementation-test (Writing mode)
**Cross-skill references loaded:** implementation-python (TaskGroup, except*, async)

## [주요 내용]

### pytest-asyncio 설정 (auto 모드 권장)

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### TaskGroup 테스트 (Python 3.11+, implementation-python 위임)

```python
import asyncio
import pytest
from unittest.mock import AsyncMock

async def fetch_order_data(order_id: str) -> dict:
    """여러 소스에서 병렬 조회"""
    async with asyncio.TaskGroup() as tg:
        order_task = tg.create_task(fetch_order(order_id))
        payment_task = tg.create_task(fetch_payment(order_id))
        shipping_task = tg.create_task(fetch_shipping(order_id))

    return {
        "order": order_task.result(),
        "payment": payment_task.result(),
        "shipping": shipping_task.result(),
    }

# 테스트: 정상 경로
async def test_fetch_order_data_parallel(monkeypatch):
    """TaskGroup이 3개의 소스를 병렬로 조회해야 한다"""
    monkeypatch.setattr("module.fetch_order", AsyncMock(return_value={"id": "1"}))
    monkeypatch.setattr("module.fetch_payment", AsyncMock(return_value={"status": "paid"}))
    monkeypatch.setattr("module.fetch_shipping", AsyncMock(return_value={"carrier": "CJ"}))

    result = await fetch_order_data("1")

    assert result["order"]["id"] == "1"
    assert result["payment"]["status"] == "paid"
```

### except* 에러 테스트 (Python 3.11+, implementation-python 위임)

```python
async def test_taskgroup_partial_failure():
    """TaskGroup 내 하나의 태스크가 실패하면 ExceptionGroup이 발생해야 한다"""

    async def failing_task():
        raise ConnectionError("DB down")

    async def ok_task():
        return "ok"

    with pytest.raises(ExceptionGroup) as exc_info:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(ok_task())
            tg.create_task(failing_task())

    # except*로 ExceptionGroup 내 특정 예외 검증
    try:
        raise exc_info.value
    except* ConnectionError as eg:
        assert len(eg.exceptions) == 1
        assert "DB down" in str(eg.exceptions[0])
```

### AsyncMock 사용 시 주의

```python
# spec으로 API 드리프트 방지
mock_client = AsyncMock(spec=HttpClient)
```

---
> **관련 스킬 참조:**
> - [TaskGroup, except*, ExceptionGroup] → **implementation-python** 스킬
> - [AsyncMock, pytest-asyncio] → 이 스킬 `references/pytest-plugins.md`
> - [Django Ninja async 뷰 테스트] → **implementation-django-ninja** 스킬
