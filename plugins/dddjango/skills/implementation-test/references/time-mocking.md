# 시간 모킹 레퍼런스

freezegun과 time-machine을 사용한 시간 모킹의 상세 규칙과 예시.

시간 모킹에는 전용 라이브러리를 사용한다. monkeypatch로 datetime을 직접 교체하는 방식은 패치 대상 모듈 경로를 정확히 지정해야 하고, 여러 모듈에서 datetime을 import하면 누락이 발생하므로 비권장한다.

---

## 1. freezegun

순수 Python 구현으로 `datetime.now()`, `date.today()`, `time.time()` 등을 모킹한다.

```python
from freezegun import freeze_time
from datetime import datetime, date, timedelta

# 데코레이터로 사용
@freeze_time("2024-01-15 10:30:00")
def test_current_time():
    assert datetime.now() == datetime(2024, 1, 15, 10, 30, 0)
    assert date.today() == date(2024, 1, 15)

# 컨텍스트 매니저로 사용
def test_time_travel():
    with freeze_time("2024-06-01"):
        assert date.today() == date(2024, 6, 1)
    assert date.today() != date(2024, 6, 1)

# 시간 흐름 시뮬레이션
@freeze_time("2024-01-01", tick=True)
def test_time_passes():
    """tick=True면 시간이 실제로 흐른다 (시작점만 고정)"""
    start = datetime.now()
    import time
    time.sleep(0.1)
    assert datetime.now() > start

# 시간 이동
def test_time_move():
    with freeze_time("2024-01-01") as frozen:
        assert date.today() == date(2024, 1, 1)
        frozen.move_to("2024-07-01")
        assert date.today() == date(2024, 7, 1)
        frozen.tick(timedelta(days=30))
        assert date.today() == date(2024, 7, 31)
```

---

## 2. time-machine

C 확장 기반으로 freezegun보다 100~200배 빠르다. C 레벨에서 시간 함수 포인터를 교체하므로, 프로젝트 크기와 무관하게 일정한 성능을 유지한다.

```python
import time_machine
from datetime import datetime, timezone

# 데코레이터로 사용
@time_machine.travel("2024-01-15 10:30:00")
def test_fixed_time():
    assert datetime.now().year == 2024

# 컨텍스트 매니저로 사용
def test_context_manager():
    with time_machine.travel("2024-06-01 12:00:00"):
        assert datetime.now().hour == 12

# 시간 이동
def test_time_shift():
    with time_machine.travel("2024-01-01", tick=False) as traveller:
        assert datetime.now() == datetime(2024, 1, 1)
        traveller.shift(timedelta(days=30))
        assert datetime.now() == datetime(2024, 1, 31)

# UTC 시간 고정
@time_machine.travel(datetime(2024, 1, 1, tzinfo=timezone.utc))
def test_utc_time():
    assert datetime.now(timezone.utc).year == 2024

# pytest fixture로 사용
@pytest.fixture
def frozen_time():
    with time_machine.travel("2024-03-15 09:00:00") as traveller:
        yield traveller

def test_with_fixture(frozen_time):
    assert datetime.now().month == 3
    frozen_time.shift(timedelta(hours=5))
    assert datetime.now().hour == 14
```

---

## 3. 비교 및 선택 기준

| 항목 | freezegun | time-machine |
|------|-----------|--------------|
| 성능 | 느림 (순수 Python) | 100~200배 빠름 (C 확장) |
| CPython 외 지원 | 모든 Python 구현체 | CPython만 |
| 선택적 패치 | 가능 | 불가 (전체 패치) |
| 추천 환경 | PyPy 사용, 선택적 패치 필요 | 일반 CPython 프로젝트 |
| 성숙도 | 오래된 커뮤니티, 안정적 | 비교적 최신, Adam Johnson 개발 |

> 출처: [freezegun PyPI](https://pypi.org/project/freezegun/), [time-machine PyPI](https://pypi.org/project/time-machine/), [Time-machine vs Freezegun - Better Stack](https://betterstack.com/community/guides/testing/time-machine-vs-freezegun/)
