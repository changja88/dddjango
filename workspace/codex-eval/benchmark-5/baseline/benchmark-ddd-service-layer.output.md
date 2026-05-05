지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 현재 환경에 존재하지 않아 읽을 파일이 없었습니다. 따라서 특정 코드 변경안이 아니라, Django + Ninja + DDD-ish 구조에서의 일반적인 배치 기준으로 설명합니다.

Application service는 보통 **Django app 내부의 `services.py` 또는 `application/` 패키지**에 둡니다.

예:

```text
orders/
  api.py                 # Ninja router
  models.py              # Django ORM model
  domain/
    order.py             # domain model, value object, domain rule
  repositories.py        # repository
  application/
    services.py          # application service
    commands.py          # request/use-case input DTO, 선택
```

작은 앱이면:

```text
orders/
  api.py
  models.py
  repositories.py
  services.py
```

앱이 커지면:

```text
orders/
  application/
    services.py
    commands.py
  domain/
    models.py
    policies.py
  infrastructure/
    repositories.py
```

핵심 관계는 이렇게 잡는 게 좋습니다.

```text
Ninja router
  -> application service
    -> domain model
    -> repository
```

Ninja router는 HTTP 계층입니다. 요청 파싱, 인증된 사용자 확인, schema 변환, HTTP status 결정 정도만 맡기고, 비즈니스 흐름은 application service에 넘깁니다.

```python
@router.post("/orders")
def create_order(request, payload: CreateOrderIn):
    service = CreateOrderService(order_repository=OrderRepository())
    order = service.create(
        user_id=request.user.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )
    return OrderOut.from_domain(order)
```

Application service는 **use case의 조율자**입니다. 트랜잭션 경계, repository 호출, domain model 생성/변경, 외부 시스템 호출 순서를 담당합니다. 하지만 할인 계산, 주문 가능 여부, 상태 전이 같은 핵심 규칙은 가능하면 domain model 안에 둡니다.

```python
class CreateOrderService:
    def __init__(self, order_repository):
        self.order_repository = order_repository

    @transaction.atomic
    def create(self, user_id, product_id, quantity):
        order = Order.create(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        self.order_repository.save(order)
        return order
```

Domain model은 비즈니스 규칙과 불변식을 가집니다. application service가 `order.status = "paid"`처럼 내부 상태를 직접 만지는 대신, `order.pay()` 같은 의도 있는 메서드를 호출하게 하는 편이 좋습니다.

```python
class Order:
    def pay(self):
        if not self.can_pay():
            raise OrderCannotBePaid()
        self.status = OrderStatus.PAID
```

Repository는 저장소 접근을 감춥니다. Django ORM을 직접 쓰는 구현은 repository 안에 두고, application service는 “주문을 저장한다”, “주문을 가져온다”는 역할에만 의존하게 합니다.

```python
class OrderRepository:
    def get(self, order_id):
        orm_order = OrderModel.objects.get(id=order_id)
        return to_domain(orm_order)

    def save(self, order):
        OrderModel.objects.update_or_create(
            id=order.id,
            defaults=to_model_fields(order),
        )
```

정리하면:

- `router`: HTTP/Ninja 관심사
- `application service`: 하나의 유스케이스 흐름 조율
- `domain model`: 비즈니스 규칙과 상태 불변식
- `repository`: ORM/DB 접근 세부사항

Django에서는 너무 이른 추상화를 피하는 게 중요합니다. 단순 CRUD라면 router에서 ORM을 바로 써도 됩니다. 하지만 여러 모델을 함께 변경하거나, 트랜잭션이 필요하거나, 같은 유스케이스가 API/관리 명령/Celery task에서 재사용된다면 application service를 두는 편이 좋습니다.