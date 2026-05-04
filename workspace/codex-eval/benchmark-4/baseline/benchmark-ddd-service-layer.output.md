Django 프로젝트에서 application service는 보통 **각 app 내부의 `services.py` 또는 `services/` 패키지**에 두는 게 가장 실용적입니다.

예:

```text
orders/
  api.py              # Ninja router
  models.py           # Django ORM model
  domain.py           # domain model / value object / domain logic
  repositories.py     # DB 접근 추상화
  services.py         # application service
```

규모가 커지면:

```text
orders/
  services/
    create_order.py
    cancel_order.py
    fulfill_order.py
```

참고로 현재 `/private/tmp/dddjango-codex-eval` 안에는 `config.toml` 파일이 없어 별도 로컬 지침은 확인하지 못했습니다.

**역할 분리**

`Ninja router`는 HTTP 입출력만 담당하는 게 좋습니다.

```python
@router.post("/orders")
def create_order(request, payload: CreateOrderIn):
    result = create_order_service.execute(payload)
    return result
```

여기서 router는 다음 정도만 처리합니다.

- request body 검증
- 인증/인가 context 전달
- service 호출
- response schema 변환
- HTTP status 결정

비즈니스 흐름은 router에 두지 않는 편이 좋습니다.

Application service는 **유스케이스 조율자**입니다.

```python
class CreateOrderService:
    def __init__(self, order_repo, product_repo):
        self.order_repo = order_repo
        self.product_repo = product_repo

    def execute(self, command):
        product = self.product_repo.get(command.product_id)

        order = Order.create(
            product=product,
            quantity=command.quantity,
            user_id=command.user_id,
        )

        self.order_repo.save(order)

        return order
```

Application service가 담당하는 것:

- 하나의 유스케이스 흐름
- transaction 경계
- repository 호출
- domain model 생성/호출
- 외부 시스템 호출 조율
- permission이나 policy 적용 위치 조율

반대로 application service에 넣지 않는 게 좋은 것:

- HTTP request/response 객체 직접 의존
- Django Ninja schema에 강하게 묶인 로직
- SQL query 세부 구현
- domain model 내부 규칙

**Domain model과의 관계**

Domain model은 핵심 비즈니스 규칙을 담습니다.

```python
class Order:
    @classmethod
    def create(cls, product, quantity, user_id):
        if quantity <= 0:
            raise InvalidQuantity()

        if product.is_discontinued:
            raise ProductUnavailable()

        return cls(...)
```

즉, application service가 “주문을 만든다”는 흐름을 담당한다면, domain model은 “어떤 주문이 유효한가”를 담당합니다.

좋은 의존 방향은 보통 이렇습니다.

```text
Ninja router
  -> Application service
    -> Domain model
    -> Repository
      -> Django ORM
```

Domain model은 가능하면 Ninja, request, response, ORM query detail을 몰라야 합니다.

**Repository와의 관계**

Repository는 저장소 접근을 감춥니다.

```python
class OrderRepository:
    def get(self, order_id: int) -> Order:
        ...

    def save(self, order: Order) -> None:
        ...
```

Django에서는 repository가 반드시 필요한 건 아닙니다. 단순 CRUD 위주라면 service에서 ORM을 직접 써도 됩니다.

하지만 다음 경우에는 repository를 두는 게 좋습니다.

- domain model과 Django ORM model을 분리하고 싶다
- 복잡한 query가 많다
- 테스트에서 DB 접근을 대체하고 싶다
- 외부 저장소/API까지 섞인다
- application service가 ORM 세부사항으로 오염되고 있다

실용적인 기준은 이겁니다.

작은 Django app:

```text
api.py -> services.py -> models.py
```

복잡해진 app:

```text
api.py -> services/ -> domain.py -> repositories.py -> models.py
```

정리하면, **application service는 Ninja router 아래, domain/repository 위에 있는 유스케이스 계층**으로 두는 게 좋습니다. Django에서는 app 내부에 두는 방식이 가장 자연스럽고, 처음부터 과하게 전역 `application/` 패키지를 만들기보다는 app 단위 `services.py`로 시작해서 커질 때 `services/` 패키지로 나누는 편이 유지보수에 유리합니다.