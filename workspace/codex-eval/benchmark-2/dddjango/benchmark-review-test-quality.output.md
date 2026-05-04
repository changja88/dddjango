**리뷰 결과**

workspace가 비어 있고 읽기 전용이라 실제 pytest 실행이나 파일별 라인 리뷰는 불가능했습니다. 따라서 아래는 “DB fixture 과의존, 약한 assert, 느린 Django 테스트”를 기준으로 한 품질 리뷰와 개선 기준입니다.

좋은 방향은 pytest를 쓰고 있다는 점입니다. 다만 현재 설명된 냄새가 맞다면, 테스트가 “도메인 동작 검증”보다 “DB에 데이터를 깔고 화면상 통과 여부 확인”에 가까워졌을 가능성이 큽니다.

- [Test Strategy] -- 대부분의 테스트가 `db`, `django_db`, 대형 fixture로 시작하면 단위 테스트가 통합 테스트로 밀려납니다. 도메인 규칙은 DB 없이 `tests/isolated/unit/`에서 밀리초 단위로 끝나야 하고, ORM/제약조건/쿼리/API는 `tests/isolated/integration/`으로 제한합니다.

- [Fixture] -- `user`, `order`, `paid_order`, `admin_client` 같은 fixture가 숨은 객체 그래프를 만들면 테스트 의도가 사라집니다. setup이 5줄 이상이거나 여러 모델을 한 번에 만들면 Excessive Setup입니다. 공통 fixture는 최소화하고, 상태 변형은 Factory Boy `Trait` 또는 테스트 안의 명시적 Arrange로 드러내세요.

- [Assertion] -- `assert response.status_code == 200`, `assert obj is not None`, `assert count > 0`, `mock.send.assert_called()`만 있으면 회귀를 거의 못 잡습니다. 반환값, 상태 전이, 저장된 필드, 도메인 예외, 외부 호출 인자를 정확히 검증해야 합니다. 외부 호출은 `mock.send.assert_called_once_with(expected_args)`처럼 인자까지 검증합니다.

- [Speed] -- DB fixture 남용은 테스트를 초/분 단위로 밀어냅니다. 시간 의존 테스트는 `freezegun`보다 `time-machine`을 기본값으로 두세요. freezegun은 순수 Python 구현인 반면 time-machine은 C 확장이라 동일 작업에서 100~200배 빠르고, 시간 모킹이 많은 스위트에서 차이가 납니다.

**경계 기준**

권장 구조:

```text
tests/
  isolated/
    unit/          # 도메인 객체, 값 객체, 정책, 순수 서비스. DB 금지.
    integration/   # Django ORM, repository adapter, view/API, transaction, query count.
  real/
    integration/   # stage/real DB, 외부 sandbox. pre-deploy 전용.
```

도메인 unit test는 Django 모델 생성 없이 `Coupon`, `Money`, `OrderPolicy`, `InMemoryCouponRepository` 같은 실제 도메인 객체와 Fake repository를 씁니다. integration test는 `pytest.mark.django_db`를 허용하되, `assertNumQueries`, DB 제약조건, manager/queryset, `transaction.on_commit`, API 응답 계약처럼 DB가 있어야만 검증 가능한 것만 둡니다.

**RED 테스트 예시**

실행은 못 했지만, `tests/isolated/unit/test_coupon_redeem.py`에 둘 수 있는 실패 테스트입니다.

```python
import pytest
import time_machine
from datetime import date

def test_redeem_expired_coupon_raises_domain_error():
    coupon = Coupon(code="WELCOME", expires_on=date(2026, 5, 1))

    with time_machine.travel("2026-05-04", tick=False):
        with pytest.raises(CouponExpiredError, match="WELCOME"):
            coupon.redeem(user_id="user-1")

def test_redeem_available_coupon_marks_redeemed_once():
    coupon = Coupon(code="WELCOME", expires_on=date(2026, 5, 10))

    result = coupon.redeem(user_id="user-1")

    assert result.code == "WELCOME"
    assert coupon.is_redeemed is True
    assert coupon.redeemed_by == "user-1"
```

예상 실패: `Coupon`, `CouponExpiredError`, `redeem()` 또는 명시적 결과 타입이 없으면 실패해야 합니다. 단순히 DB row를 만들고 `status_code == 200`만 보는 기존 테스트라면 이 도메인 규칙 결함을 놓칩니다.

**GREEN 최소 구현**

```python
from dataclasses import dataclass
from datetime import date

class CouponExpiredError(Exception):
    pass

@dataclass(frozen=True)
class RedeemResult:
    code: str

@dataclass
class Coupon:
    code: str
    expires_on: date
    is_redeemed: bool = False
    redeemed_by: str | None = None

    def redeem(self, user_id: str) -> RedeemResult:
        if date.today() > self.expires_on:
            raise CouponExpiredError(f"{self.code} expired")
        self.is_redeemed = True
        self.redeemed_by = user_id
        return RedeemResult(code=self.code)
```

**REFACTOR 기준**

DB fixture는 “도메인 규칙을 만들기 위한 준비물”이 아니라 “Django adapter 검증용”으로 격하하세요. Repository/Gateway는 `MagicMock` 남발보다 `InMemoryCouponRepository` Fake를 우선하고, 외부 HTTP는 `@responses.activate` + `responses.add(...)`로 차단합니다. 반복 케이스는 `pytest.mark.parametrize`, 경계값은 만료일 전날/당일/다음날로 추가합니다. 순서 의존성은 `pytest-randomly`로 드러내세요.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration -q
pytest --randomly-seed=last tests/isolated -q
```

---
> **관련 스킬 참조:**
> - 테스트 리팩터링과 fixture 정리 → **implementation-test** 스킬
> - 도메인 규칙을 DB 없이 분리 → **architecture-ddd** 스킬
> - Django ORM/API 통합 테스트 경계 → **implementation-django** 스킬