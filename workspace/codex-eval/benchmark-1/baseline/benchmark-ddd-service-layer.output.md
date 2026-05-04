Django 프로젝트에서 application service는 보통 **각 Django app 내부의 `services.py` 또는 `services/` 패키지**에 두는 게 가장 실용적입니다.

예를 들면:

```text
orders/
  api.py              # Ninja router
  models.py           # Django ORM model
  repositories.py     # DB 접근 추상화
  services.py         # application service
  schemas.py          # Ninja input/output schema
  domain/
    models.py         # domain model, value object, entity
```

규모가 커지면 이렇게 나누는 편이 좋습니다.

```text
orders/
  api/
    router.py
    schemas.py
  application/
    services.py
    commands.py
  domain/
    models.py
    policies.py
  infrastructure/
    repositories.py
  models.py           # Django ORM model
```

핵심 관계는 이렇게 잡으면 됩니다.

```text
Ninja Router
  -> Application Service
    -> Domain Model
    -> Repository
      -> Django ORM
```

`Ninja router`는 HTTP 입출력만 담당하는 얇은 계층이어야 합니다. 요청 schema 검증, 인증된 user 전달, service 호출, response 변환 정도만 하고 비즈니스 흐름을 직접 담지 않는 게 좋습니다.

```python
@router.post("/orders")
def create_order(request, payload: CreateOrderIn):
    order = order_service.create_order(
        user_id=request.user.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )
    return OrderOut.from_domain(order)
```

`application service`는 유스케이스를 조율합니다. 예를 들어 “주문 생성”, “결제 승인”, “회원 탈퇴” 같은 애플리케이션 동작이 여기에 들어갑니다. 트랜잭션 경계도 보통 여기서 잡습니다.

```python
class OrderService:
    def __init__(self, order_repo, product_repo):
        self.order_repo = order_repo
        self.product_repo = product_repo

    @transaction.atomic
    def create_order(self, user_id, product_id, quantity):
        product = self.product_repo.get(product_id)

        order = Order.create(
            user_id=user_id,
            product=product,
            quantity=quantity,
        )

        self.order_repo.save(order)
        return order
```

`domain model`은 비즈니스 규칙을 표현합니다. “주문 수량은 1개 이상이어야 한다”, “취소된 주문은 결제할 수 없다” 같은 규칙은 service보다 domain model 안에 있는 편이 좋습니다.

```python
class Order:
    @classmethod
    def create(cls, user_id, product, quantity):
        if quantity < 1:
            raise InvalidQuantity()
        if not product.is_available:
            raise ProductUnavailable()

        return cls(user_id=user_id, product_id=product.id, quantity=quantity)
```

`repository`는 저장소 접근을 감춥니다. application service가 Django ORM에 직접 강하게 묶이지 않게 해줍니다.

```python
class DjangoOrderRepository:
    def save(self, order: Order):
        return OrderModel.objects.create(
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
        )
```

실무적으로는 이렇게 판단하면 됩니다.

- 작은 Django app: `services.py`, `repositories.py`로 충분
- 도메인 규칙이 많음: `domain/`, `application/`, `infrastructure/` 분리
- Ninja router가 길어짐: service로 유스케이스 이동
- service에 validation이 너무 많아짐: domain model이나 policy로 이동
- repository가 단순 CRUD만 감싸고 있음: 꼭 만들 필요는 없음, ORM을 service에서 직접 써도 됨

가장 추천하는 기준은 이것입니다.

**router는 HTTP를 알고, application service는 유스케이스를 알고, domain model은 비즈니스 규칙을 알고, repository는 저장 방식을 안다.**

이 경계를 지키면 Django Ninja에서도 코드가 얇고 테스트하기 쉬운 구조가 됩니다.