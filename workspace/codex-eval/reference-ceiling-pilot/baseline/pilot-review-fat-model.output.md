클린 아키텍처 관점에서 보면 이 `Order` 모델은 Django ORM 모델 안에 도메인 규칙, 저장소 접근, 외부 결제 연동, 상태 변경 영속화가 모두 섞여 있습니다.

가장 큰 문제는 `checkout()`이 “주문이 결제 준비 상태로 갈 수 있는가”라는 도메인 판단뿐 아니라 DB 조회/저장과 외부 결제 게이트웨이 호출까지 직접 수행한다는 점입니다.

```python
def checkout(self, payment_gateway):
```

이 메서드는 현재 다음 책임을 동시에 가집니다.

- 주문 상태 검증
- 주문 상품 재고 검증
- 상품 재고 차감
- 상품 저장
- 결제 게이트웨이 호출
- 주문 상태 변경
- 주문 저장

클린 아키텍처 기준으로는 핵심 도메인 규칙과 프레임워크/DB/외부 SDK 세부사항이 강하게 결합된 구조입니다.

## 주요 문제

`self.items.all()`은 Django ORM 관계를 직접 순회합니다.

```python
for item in self.items.all():
```

이 때문에 `Order`의 핵심 로직이 Django의 lazy queryset, relation manager, DB 접근 방식에 묶입니다. 도메인 규칙을 순수하게 테스트하기 어렵고, checkout 로직을 실행하면 DB 접근이 암묵적으로 발생합니다.

재고 차감도 모델 내부에서 바로 저장합니다.

```python
item.product.stock -= item.quantity
item.product.save()
```

`Order`가 `Product`의 내부 상태를 직접 변경하고 저장까지 책임집니다. 주문 도메인이 상품 저장 방식까지 알고 있는 셈입니다. 또한 여러 상품 중 일부는 저장되고 이후 결제 준비에서 실패하면 데이터가 중간 상태로 남을 수 있습니다. 트랜잭션 경계도 보이지 않습니다.

외부 결제 게이트웨이 호출도 도메인 모델 안에 들어와 있습니다.

```python
payment_gateway.prepare(self.total_amount)
```

결제 준비는 애플리케이션 유스케이스에서 조율하는 편이 낫습니다. 도메인 모델이 외부 SDK나 포트 역할을 직접 호출하면 테스트와 교체가 어려워지고, 결제 호출 실패 시 재고 차감과 주문 상태 변경의 일관성도 애매해집니다.

마지막으로 상태 변경과 저장이 한 메서드에 결합되어 있습니다.

```python
self.status = "ready_to_pay"
self.save()
```

도메인 객체가 “상태를 바꾼다”와 “DB에 저장한다”를 동시에 수행합니다. 클린 아키텍처에서는 보통 상태 전이는 도메인/유스케이스가 결정하고, 저장은 repository 또는 application service가 담당합니다.

## 개선 방향

Django 모델을 완전히 빈 데이터 객체로 만들 필요는 없습니다. 다만 이 정도의 checkout 흐름은 모델 메서드 하나에 넣기보다 application service/use case로 빼는 편이 자연스럽습니다.

예를 들면 다음처럼 역할을 나눌 수 있습니다.

```python
class CheckoutOrderService:
    def __init__(self, payment_gateway):
        self.payment_gateway = payment_gateway

    @transaction.atomic
    def checkout(self, order):
        if order.status != "draft":
            raise ValueError("invalid status")

        for item in order.items.select_related("product").all():
            product = item.product

            if product.stock < item.quantity:
                raise ValueError("out of stock")

            product.stock -= item.quantity
            product.save(update_fields=["stock"])

        self.payment_gateway.prepare(order.total_amount)

        order.status = "ready_to_pay"
        order.save(update_fields=["status"])
```

이 정도만 해도 최소한 checkout이라는 애플리케이션 흐름이 모델 밖으로 나가고, 트랜잭션 경계가 명확해집니다. 다만 여전히 Django ORM에 의존하는 application service이므로, 엄격한 클린 아키텍처라면 repository와 domain entity를 더 분리할 수 있습니다.

도메인 모델 쪽에는 저장을 하지 않는 순수 규칙만 남기는 방향이 좋습니다.

```python
class Order(models.Model):
    # fields ...

    def can_checkout(self):
        return self.status == "draft"

    def mark_ready_to_pay(self):
        if self.status != "draft":
            raise ValueError("invalid status")
        self.status = "ready_to_pay"
```

또는 Django 모델을 persistence model로 보고, 별도의 도메인 객체를 둘 수도 있습니다. 다만 현재 코드 규모에서는 과한 분리일 수 있습니다.

## 특히 확인할 점

재고 차감과 결제 준비 호출의 순서가 중요합니다. 현재 코드는 재고를 DB에 저장한 뒤 결제 게이트웨이를 호출합니다. 게이트웨이 호출이 실패하면 재고만 줄어든 상태가 될 수 있습니다. `transaction.atomic()`을 써도 외부 결제 호출은 DB 트랜잭션과 함께 롤백되지 않기 때문에, 실제 시스템에서는 결제 준비와 재고 예약을 별도 상태로 관리하거나 outbox/saga 같은 패턴을 고려해야 합니다.

또한 동시 checkout 요청이 들어오면 재고 검증 후 차감 사이에 race condition이 생길 수 있습니다. `select_for_update()`, 조건부 update, 재고 예약 테이블 같은 방식이 필요할 수 있습니다.

요약하면, 이 코드는 작은 프로젝트에서는 읽기 쉽지만 클린 아키텍처 관점에서는 `Order` 모델이 너무 많은 이유로 변경됩니다. 우선 checkout 유스케이스를 application service로 분리하고, 트랜잭션과 동시성, 외부 결제 실패 시나리오를 명시적으로 다루는 방향이 좋습니다.