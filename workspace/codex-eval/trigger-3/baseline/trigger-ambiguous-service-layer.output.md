현재 `/private/tmp/dddjango-codex-eval`에는 파일이 없어서 저장소 기준으로는 확인할 수 없었습니다. Django 기준으로는 보통 **앱 내부에 서비스 레이어를 두는 것**을 추천합니다.

예시:

```text
users/
  models.py
  views.py
  serializers.py
  services.py
  selectors.py
```

또는 서비스가 커지면:

```text
orders/
  services/
    __init__.py
    checkout.py
    refund.py
    fulfillment.py
```

권장 기준은 이렇습니다.

- 특정 앱의 유스케이스라면 `app/services.py` 또는 `app/services/`
- 여러 앱을 조합하는 비즈니스 흐름이라면 중심이 되는 도메인 앱의 `services/`
- 단순 조회 로직은 `selectors.py`로 분리
- DB 변경, 트랜잭션, 외부 API 호출, 도메인 규칙 조합은 `services/`
- `views.py`, `serializers.py`, `forms.py`에는 입출력 변환과 호출만 남기기

예를 들어 주문 생성이면:

```python
# orders/services/checkout.py

from django.db import transaction

@transaction.atomic
def create_order(*, user, items, address):
    # validate domain rules
    # create order
    # create order items
    # reserve stock
    # return order
    ...
```

그리고 뷰에서는:

```python
order = create_order(
    user=request.user,
    items=serializer.validated_data["items"],
    address=serializer.validated_data["address"],
)
```

피해야 할 위치는 프로젝트 루트의 거대한 `services/`입니다. 초반에는 편해 보여도 도메인 경계가 흐려지고, 앱 간 의존성이 금방 꼬입니다. 공유 인프라성 코드만 `common/`, `core/`, `integrations/` 같은 곳에 두고, 비즈니스 서비스는 앱 안에 두는 쪽이 유지보수하기 좋습니다.