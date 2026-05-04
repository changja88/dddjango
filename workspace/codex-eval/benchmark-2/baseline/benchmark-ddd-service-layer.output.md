Django 프로젝트에서는 application service를 보통 **각 앱 내부의 `services.py` 또는 `application/` 패키지**에 두는 게 좋습니다.

예:

```text
orders/
  api.py              # Ninja router
  models.py           # Django ORM model
  repositories.py     # DB 접근 추상화
  services.py         # application service
  domain/
    models.py         # 순수 domain model, value object
```

규모가 커지면:

```text
orders/
  api/
    routers.py
    schemas.py
  application/
    services.py
    commands.py
  domain/
    models.py
    policies.py
  infrastructure/
    repositories.py
  models.py
```

핵심 관계는 이렇게 잡는 게 좋습니다.

```text
Ninja Router
  -> Application Service
    -> Domain Model
    -> Repository
      -> Django ORM
```

**Ninja router**는 HTTP 계층입니다. 요청/응답, 인증 정보 추출, schema 변환 정도만 담당하고 비즈니스 흐름은 직접 처리하지 않는 편이 좋습니다.

```python
@router.post("/orders")
def create_order(request, payload: CreateOrderIn):
    service = OrderService(order_repo=OrderRepository())
    order = service.create_order(
        user_id=request.user.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )
    return OrderOut.from_domain(order)
```

**Application service**는 유스케이스를 조율합니다. 예를 들어 “주문 생성”이라는 작업에서 repository로 데이터를 읽고, domain model에 규칙을 적용하고, 저장하고, 필요하면 이벤트나 외부 API 호출을 조율합니다.

```python
class OrderService:
    def __init__(self, order_repo):
        self.order_repo = order_repo

    def create_order(self, user_id, product_id, quantity):
        order = Order.create(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )

        self.order_repo.save(order)

        return order
```

**Domain model**은 핵심 비즈니스 규칙을 담습니다. 가능하면 Django request, Ninja schema, ORM query에 의존하지 않는 쪽이 좋습니다.

```python
@dataclass
class Order:
    user_id: int
    product_id: int
    quantity: int

    @classmethod
    def create(cls, user_id, product_id, quantity):
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        return cls(user_id=user_id, product_id=product_id, quantity=quantity)
```

**Repository**는 저장소 접근을 감쌉니다. application service가 Django ORM을 직접 만지지 않게 해주면 테스트가 쉬워지고, 비즈니스 흐름과 DB 쿼리가 섞이지 않습니다.

```python
class OrderRepository:
    def save(self, order: Order):
        return OrderORM.objects.create(
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
        )
```

실무적으로는 처음부터 너무 복잡하게 나누기보다, 다음 기준으로 시작하는 게 좋습니다.

- 단순 CRUD면 Ninja router + Django model만으로도 충분할 수 있음
- 여러 model을 조합하거나 트랜잭션이 필요하면 `services.py` 도입
- 비즈니스 규칙이 많아지면 domain model 분리
- 테스트에서 DB 의존을 줄이고 싶거나 쿼리 책임이 커지면 repository 분리

정리하면, **application service는 router와 domain/repository 사이의 유스케이스 계층**에 두는 게 가장 자연스럽습니다. Router는 얇게, domain model은 규칙 중심으로, repository는 persistence 중심으로 유지하면 Django에서도 구조가 꽤 오래 버팁니다.