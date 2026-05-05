지정 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 없고, 현재 작업 디렉터리도 비어 있었습니다. 접근 가능한 benchmark에는 `Fixture: none`으로 기록되어 있어 코드 diff는 만들 수 없고, 설계 기준으로 정리합니다.

**권장 기준**

| 이름 | 의미 | 허용 책임 | 금지 책임 |
|---|---|---|---|
| `OrderManager` / `OrderQuerySet` | Django ORM 확장 | 조회 scope, 필터, annotate, select/prefetch, 단순 생성 헬퍼 | 결제, 취소, 이메일, 외부 API, 트랜잭션 orchestration |
| `PlaceOrderUseCase` | 애플리케이션 유스케이스 | 트랜잭션, ORM/Repository 로딩, 도메인 메서드 호출, 저장, `on_commit()` 후속 작업 연결 | 가격/취소 가능 여부 같은 도메인 규칙 직접 계산 |
| `OrderPricingPolicy`, `OrderCancellationPolicy` | 도메인 정책/도메인 서비스 | Entity/VO 하나에 자연스럽게 들어가지 않는 순수 도메인 규칙 | ORM, Django settings, HTTP, email, transaction |
| `OrderService` | 모호한 이름 | 가급적 금지. 꼭 쓰면 `OrderApplicationService` 또는 `OrderPricingPolicy`처럼 구체화 | 모든 주문 로직을 모으는 God Service |
| `OrderUseCase` | 너무 넓은 이름 | 금지 | 엔티티 단위 유스케이스 묶음 |

핵심은 `Service`와 `UseCase`를 둘 다 일반명으로 열어두지 않는 것입니다. 팀 규칙은 하나로 고정하세요. 제 추천은 **복잡한 쓰기 흐름은 동사형 `*UseCase`**, 순수 도메인 규칙은 **역할형 `*Policy` / `*Calculator` / `*Specification`**, ORM 확장은 **`*Manager` / `*QuerySet`**입니다.

예시:

```python
class OrderQuerySet(models.QuerySet):
    def awaiting_payment(self):
        return self.filter(status=Order.Status.AWAITING_PAYMENT)


class OrderManager(models.Manager.from_queryset(OrderQuerySet)):
    pass
```

```python
class ConfirmPaymentUseCase:
    def __call__(self, command: ConfirmPaymentCommand) -> None:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=command.order_id)
            order.confirm_payment(command.payment_id)
            order.save(update_fields=["status", "payment_id", "updated_at"])

            transaction.on_commit(
                lambda: publish_events(order.collect_events())
            )
```

```python
class OrderCancellationPolicy:
    def can_cancel(self, order: Order, shipping_status: ShippingStatus) -> bool:
        return order.is_paid and not shipping_status.is_in_transit
```

**프로젝트 규칙으로 박을 문장**

1. `Manager`는 Django ORM 전용이다.
2. 읽기 조회는 `QuerySet/Manager` 또는 `selectors.py`에 둔다.
3. 단순 쓰기는 `services.py`의 동사형 함수로 충분하다.
4. 결제, 재고, 배송, 알림처럼 여러 경계를 조율하는 쓰기 흐름만 `*UseCase`로 승격한다.
5. `OrderService`, `OrderUseCase`처럼 엔티티명만 붙은 넓은 클래스명은 금지한다.
6. 도메인 규칙은 가능하면 `Order.confirm_payment()`, `Order.cancel()` 같은 도메인 객체 메서드에 둔다.
7. 도메인 객체 하나에 넣기 어색한 순수 규칙만 `*Policy`, `*Calculator`, `*Specification`으로 분리한다.

검토할 때는 이렇게 보면 됩니다:

```bash
rg "class .*Service|class .*UseCase|class .*Manager" apps/
rg "transaction.atomic|on_commit|send_mail|requests\\." apps/orders/
```

`Manager`에서 두 번째 명령 결과가 나오면 거의 경계 위반입니다. `Service`가 나오면 먼저 “이게 유스케이스 조율인가, 순수 도메인 규칙인가, 그냥 이름이 애매한가?”를 판별하고 이름을 좁히세요.

---
> **관련 스킬 참조:**
> - DDD 계층 책임과 Django 서비스 레이어 정리 → **architecture-ddd**, **implementation-django**, **implementation-cleancode** 스킬