현재 `/private/tmp/dddjango-codex-eval`에는 프로젝트 파일이 없어서 코드 구조 기준 판단은 못 했습니다. Django 기준으로는 보통 이렇게 두는 걸 권합니다.

**추천 위치**

```text
apps/
  orders/
    models.py
    views.py
    serializers.py
    services.py
```

또는 서비스가 커지면:

```text
apps/
  orders/
    services/
      __init__.py
      order_create.py
      payment_capture.py
```

앱 단위 유스케이스라면 각 Django app 내부에 두는 게 가장 낫습니다. 예를 들어 `orders.services.create_order()`처럼요. 이유는 서비스가 결국 해당 도메인의 모델, 정책, 트랜잭션 경계와 강하게 묶이기 때문입니다.

공통 `services/` 루트는 피하는 편이 좋습니다.

```text
services/
  order_service.py
  user_service.py
```

이 구조는 시간이 지나면 앱 경계가 흐려지고, “공용 잡동사니 계층”이 되기 쉽습니다.

내 기준은 이렇습니다.

- 한 앱의 유스케이스: `app/services.py` 또는 `app/services/*.py`
- 여러 앱을 조율하는 작업: `apps/<주도하는 앱>/services/`에 둠
- 외부 API 클라이언트: `app/clients.py`, `app/integrations/`, 또는 `infrastructure/`
- 순수 도메인 규칙: 가능하면 `models.py`, `domain.py`, `selectors.py` 쪽
- 읽기 전용 조회 로직: `selectors.py`로 분리하는 것도 좋음

예시:

```python
# orders/services.py

from django.db import transaction

@transaction.atomic
def create_order(*, user, items):
    order = Order.objects.create(user=user)

    for item in items:
        OrderLine.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
        )

    return order
```

짧게 말하면: **서비스 레이어는 프로젝트 루트가 아니라 해당 Django app 내부에 두는 게 기본값**입니다. 앱 하나 안에서 커지면 `services/` 패키지로 쪼개면 됩니다.