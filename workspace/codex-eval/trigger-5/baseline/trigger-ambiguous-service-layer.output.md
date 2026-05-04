현재 `/private/tmp/dddjango-codex-eval`에는 코드나 `config.toml`이 없어서, 일반적인 Django 구조 기준으로 답하면: **서비스 레이어는 각 도메인 앱 안에 두는 게 가장 무난합니다.**

예를 들어:

```text
orders/
  models.py
  views.py
  selectors.py
  services.py
  tests/
```

권장 기준은 이렇습니다.

- `views.py`: HTTP 요청/응답, serializer/form 처리
- `services.py`: 상태 변경이 있는 유스케이스, 트랜잭션, 여러 모델을 조합하는 비즈니스 로직
- `selectors.py`: 조회 전용 쿼리, 화면/API에 필요한 read 모델 구성
- `models.py`: 도메인 불변식, 단일 모델에 자연스럽게 속하는 메서드

예:

```python
# orders/services.py
from django.db import transaction

@transaction.atomic
def place_order(*, user, items):
    order = Order.objects.create(user=user)

    for item in items:
        OrderLine.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
        )

    return order
```

```python
# orders/views.py
def create_order(request):
    order = place_order(user=request.user, items=...)
    ...
```

피하는 게 좋은 구조는 프로젝트 최상위에 거대한 `services/` 패키지를 두는 방식입니다. 처음엔 깔끔해 보여도 시간이 지나면 도메인 경계가 흐려지고, `services/order.py`, `services/payment.py`, `services/user.py`처럼 사실상 앱 구조를 한 번 더 복제하게 됩니다.

다만 여러 앱을 가로지르는 유스케이스가 명확히 많다면 별도 앱을 둘 수 있습니다.

```text
checkout/
  services.py
```

즉 기본값은 **“도메인 앱 내부의 `services.py`”**, 조회 로직이 커지면 **`selectors.py` 분리**, 앱 경계를 넘는 큰 유스케이스는 **별도 orchestration 앱**이 좋습니다.