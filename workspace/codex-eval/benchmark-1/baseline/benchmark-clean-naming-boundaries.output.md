`/private/tmp/dddjango-codex-eval` 안에는 현재 `config.toml`이나 소스 파일이 보이지 않아, 일반적인 Django DDD 기준으로 정리합니다.

핵심 기준은 이렇게 잡는 게 좋습니다.

| 이름 | 권장 여부 | 책임 |
|---|---:|---|
| `OrderManager` | 거의 비추천 | Django의 `models.Manager`와 헷갈림. ORM query helper일 때만 사용 |
| `OrderService` | 제한적으로 사용 | 도메인 규칙 중 특정 엔티티/값 객체에 넣기 애매한 순수 도메인 로직 |
| `OrderUseCase` | 비추천 | 너무 추상적. “무슨 행위인지” 드러나지 않음 |
| `PlaceOrderUseCase` | 추천 | 주문 생성이라는 애플리케이션 유스케이스 |
| `CancelOrderUseCase` | 추천 | 주문 취소 유스케이스 |
| `OrderRepository` | 추천 | 주문 aggregate 저장/조회 추상화 |
| `OrderQueryService` | 추천 가능 | 목록/상세 조회 전용 read model 조립 |

추천 네이밍 규칙은 이렇습니다.

**Application Layer**
유저/시스템이 수행하는 작업 단위입니다. 트랜잭션, 권한 확인, repository 호출, 외부 포트 호출을 조율합니다.

```python
PlaceOrderUseCase
CancelOrderUseCase
PayOrderUseCase
ShipOrderUseCase
```

또는 CQRS 스타일이면:

```python
PlaceOrderCommandHandler
CancelOrderCommandHandler
GetOrderDetailQueryHandler
```

여기에는 비즈니스 규칙 자체를 많이 넣지 말고, 도메인 객체에게 시키는 역할이 좋습니다.

```python
class CancelOrderUseCase:
    def execute(self, order_id: OrderId, actor: UserId) -> None:
        order = self.order_repository.get(order_id)
        order.cancel(by=actor)
        self.order_repository.save(order)
```

**Domain Layer**
주문 자체의 상태 전이와 불변식은 `Order` aggregate가 가집니다.

```python
class Order:
    def cancel(self, by: UserId) -> None:
        if self.status == OrderStatus.SHIPPED:
            raise CannotCancelShippedOrder()
        self.status = OrderStatus.CANCELED
```

`OrderService`는 정말로 `Order` 하나에 넣기 어려운 도메인 규칙일 때만 씁니다.

예:

```python
class OrderPricingService:
    def calculate_total(self, order_lines, coupon, membership) -> Money:
        ...
```

다만 이것도 가능하면 `PricingPolicy`, `DiscountPolicy`, `ShippingFeePolicy`처럼 더 구체적인 이름이 낫습니다.

**Infrastructure / Django Layer**
Django ORM 관련 이름에는 `Manager`를 써도 됩니다. 단, 이건 DDD의 서비스가 아니라 ORM query helper입니다.

```python
class OrderManager(models.Manager):
    def paid(self):
        return self.filter(status=OrderStatus.PAID)
```

DDD 쪽 repository와 Django manager를 섞지 않는 게 중요합니다.

```python
class DjangoOrderRepository(OrderRepository):
    def get(self, order_id: OrderId) -> Order:
        ...
```

제가 권장하는 최종 기준은 이겁니다.

1. `Manager`는 Django ORM 전용으로만 쓴다.
2. `UseCase`는 application layer의 행위 단위에만 쓴다.
3. `OrderUseCase`처럼 명사만 있는 이름은 금지하고 `PlaceOrderUseCase`처럼 동사+목적어로 쓴다.
4. `Service`는 남발하지 않는다.
5. 도메인 규칙은 먼저 `Order`, `OrderLine`, `Payment`, `PricingPolicy` 같은 도메인 객체에 둔다.
6. 여러 aggregate나 외부 포트를 조율하면 `UseCase`, 순수 도메인 계산이면 `DomainService` 또는 `Policy`로 둔다.

실무적으로는 다음처럼 정리하면 혼란이 줄어듭니다.

```text
orders/
  domain/
    entities.py        # Order, OrderLine
    policies.py        # PricingPolicy, CancellationPolicy
    repositories.py    # OrderRepository interface
  application/
    use_cases.py       # PlaceOrderUseCase, CancelOrderUseCase
    commands.py
  infrastructure/
    django_models.py
    repositories.py    # DjangoOrderRepository
  presentation/
    views.py
    serializers.py
```

한 줄 기준으로 말하면:

`UseCase`는 “무엇을 한다”, `Service/Policy`는 “도메인 판단이나 계산을 한다”, `Manager`는 “Django ORM query를 돕는다”로 고정하는 게 가장 깔끔합니다.