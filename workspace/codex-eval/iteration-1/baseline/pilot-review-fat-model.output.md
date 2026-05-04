`config.toml`은 현재 디렉터리에 없어 추가 지시는 확인하지 못했습니다. 제공된 모델 기준으로 리뷰합니다.

**주요 문제**

1. **Django 모델이 유스케이스를 직접 수행함**

`Order.checkout()`이 주문 상태 검증, 재고 차감, 결제 준비, DB 저장까지 모두 처리합니다. 클린 아키텍처 관점에서는 모델이 프레임워크 ORM에 묶인 상태에서 애플리케이션 유스케이스까지 담당하고 있어 책임이 과합니다.

권장 구조:

```python
class CheckoutOrderUseCase:
    def execute(self, order_id: int):
        order = order_repository.get(order_id)
        inventory_service.reserve(order.items)
        payment_service.prepare(order.total_amount)
        order.mark_ready_to_pay()
        order_repository.save(order)
```

`Order`는 상태 전이 같은 도메인 규칙만 갖고, 외부 작업은 유스케이스 계층이 조율하는 편이 좋습니다.

2. **도메인 모델이 ORM과 외부 시스템에 강하게 결합됨**

```python
for item in self.items.all():
```

`self.items.all()`은 Django ORM reverse relation입니다. 도메인 로직이 DB 접근 방식에 직접 의존합니다.

```python
payment_gateway.prepare(self.total_amount)
```

결제 게이트웨이도 모델 메서드 안으로 들어와 있습니다. 이는 엔티티가 외부 포트/어댑터를 직접 호출하는 형태라 의존성 방향이 안쪽에서 바깥쪽으로 새고 있습니다.

3. **트랜잭션 경계가 불명확함**

재고 차감 후 결제 준비 중 예외가 발생하면 일부 상품 재고만 차감된 상태로 남을 수 있습니다.

```python
item.product.stock -= item.quantity
item.product.save()
payment_gateway.prepare(...)
self.status = "ready_to_pay"
self.save()
```

이 흐름은 최소한 애플리케이션 서비스에서 `transaction.atomic()`으로 묶어야 합니다. 다만 외부 결제 호출을 DB 트랜잭션 안에 넣을지도 별도 설계가 필요합니다. 일반적으로는 재고 예약, 주문 상태 변경, 결제 준비 요청을 분리하거나 outbox/event 기반으로 처리하는 편이 더 안전합니다.

4. **동시성 문제가 있음**

```python
if item.product.stock < item.quantity:
    raise ValueError("out of stock")
item.product.stock -= item.quantity
item.product.save()
```

동시에 두 checkout이 들어오면 둘 다 재고 검사를 통과하고 초과 차감될 수 있습니다. `select_for_update()`, 조건부 update, 재고 예약 테이블 같은 방식이 필요합니다.

5. **예외 타입이 도메인 의미를 표현하지 못함**

```python
raise ValueError("invalid status")
raise ValueError("out of stock")
```

도메인 예외를 별도로 두는 것이 좋습니다.

```python
class InvalidOrderStatus(Exception): ...
class InsufficientStock(Exception): ...
```

이렇게 하면 유스케이스/API 계층에서 실패 원인을 명확히 매핑할 수 있습니다.

6. **상태 값이 문자열로 흩어질 가능성이 큼**

```python
status = models.CharField(max_length=20, default="draft")
```

Django라면 `TextChoices`를 쓰는 편이 낫습니다.

```python
class OrderStatus(models.TextChoices):
    DRAFT = "draft"
    READY_TO_PAY = "ready_to_pay"
```

**개선 방향**

모델에는 최소한의 도메인 상태 전이만 남기는 게 좋습니다.

```python
class Order(models.Model):
    ...

    def mark_ready_to_pay(self):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderStatus()
        self.status = OrderStatus.READY_TO_PAY
```

checkout 전체 흐름은 애플리케이션 서비스로 빼는 편이 클린 아키텍처에 더 맞습니다.

```python
class CheckoutOrderUseCase:
    def __init__(self, order_repo, inventory_service, payment_gateway):
        self.order_repo = order_repo
        self.inventory_service = inventory_service
        self.payment_gateway = payment_gateway

    def execute(self, order_id):
        order = self.order_repo.get_with_items(order_id)

        self.inventory_service.reserve(order.items)
        self.payment_gateway.prepare(order.total_amount)

        order.mark_ready_to_pay()
        self.order_repo.save(order)
```

요약하면, 현재 코드는 “Active Record 모델에 유스케이스를 넣은 Django식 구현”으로는 흔하지만, 클린 아키텍처 기준에서는 **도메인/애플리케이션/인프라 책임이 한 메서드에 섞여 있는 구조**입니다. 가장 먼저 `checkout`을 유스케이스 서비스로 분리하고, 모델에는 상태 전이 규칙만 남기는 것이 핵심 개선입니다.