**[주요 내용]**

Fixture 확인: `/Users/hyun/Desktop/dddjango/none` 경로가 존재하지 않아 읽을 fixture 파일이 없었습니다. 그래서 코드 diff 대신 Django DDD 팀 컨벤션으로 쓸 책임/네이밍 기준을 정리합니다.

핵심 결론: `OrderManager`, `OrderService`, `OrderUseCase`를 같은 의미로 섞지 말고, 프로젝트 기본 용어는 **Application Service**로 통일하는 편이 가장 덜 헷갈립니다.

| 이름 | 책임 | 써도 되는 위치 | 피해야 할 것 |
|---|---|---|---|
| `OrderManager` | Django ORM 진입점, QuerySet 생성, 저장소 접근 편의 | `Order.objects`, custom `Manager`, `QuerySet` | 주문 확정, 결제, 취소 같은 유스케이스 처리 |
| `OrderService` | 너무 넓은 이름. 가능하면 단독 사용 금지 | 작은 프로젝트에서 `services.py` 함수 묶음 정도 | 모든 주문 로직을 담는 God Service |
| `OrderUseCase` | 특정 입력으로 하나의 사용자 목적을 수행 | 팀이 Clean Architecture 용어를 명시적으로 채택한 경우 | Django 서비스와 같은 뜻으로 혼용 |
| `OrderApplicationService` | 트랜잭션, 권한/입력 조율, Repository/ORM 호출, 도메인 메서드 호출 | 중형 이상 DDD 구조 | 도메인 규칙 자체를 여기에 몰아넣기 |
| `Order` / `OrderLine` | 불변식, 상태 전이, 도메인 규칙 | domain model / Django model method | 외부 API, request, response, email 직접 호출 |

**책임 기준**

1. `Manager`는 저장소/조회 책임이다.  
   `Order.objects.pending().for_customer(user)`는 가능하지만 `Order.objects.place_order(...)`처럼 비즈니스 유스케이스를 실행하면 안 된다.

2. 도메인 규칙은 `Order` 안에 둔다.  
   예: “취소된 주문은 결제 확정 불가”, “배송 시작 후 취소 불가”, “총액 계산”은 `Order.confirm_payment()`, `Order.cancel()` 같은 행위 이름으로 둔다.

3. Application Service는 흐름 조율만 한다.  
   트랜잭션 시작, 주문 로드, 권한 확인, 도메인 메서드 호출, 저장, `transaction.on_commit()` 부수효과 예약까지 담당한다. 상태 전이 조건문을 길게 품기 시작하면 도메인 모델로 내려야 한다.

4. Domain Service는 드물게 쓴다.  
   특정 엔티티/값 객체에 자연스럽게 속하지 않는 순수 도메인 규칙에만 쓴다. 예: 여러 할인 정책을 조합해 최종 가격을 계산하는 `OrderPricingService`. DB, HTTP, Django request를 알면 Domain Service가 아니다.

**프로젝트 규모별 컨벤션**

작은 Django CRUD/운영툴:

```python
# apps/orders/services.py

@transaction.atomic
def order_cancel(*, order_id: int, actor: User) -> None:
    order = Order.objects.select_for_update().get(id=order_id)
    order.cancel(by=actor)
    order.save(update_fields=["status", "cancelled_at"])
```

규칙: `OrderService` 클래스 만들지 말고 `<entity>_<action>` 함수로 끝낸다.

중간 규모:

```python
# apps/orders/application/services.py

class CancelOrderService:
    @transaction.atomic
    def execute(self, *, order_id: OrderId, actor_id: UserId) -> None:
        order = self.orders.get(order_id)
        order.cancel(actor_id=actor_id)
        self.orders.save(order)
```

규칙: 클래스명은 `CancelOrderService`, 메서드는 `execute`. `CancelOrderUseCase`와 혼용하지 않는다.

큰 DDD/헥사고날 구조:

```python
# apps/orders/application/use_cases/cancel_order.py

class CancelOrder:
    def __call__(self, command: CancelOrderCommand) -> None:
        order = self.orders.get(command.order_id)
        order.cancel(actor_id=command.actor_id)
        self.orders.save(order)
```

규칙: 이 단계에서만 `use_cases/` 디렉터리와 `Command`를 도입한다. 단순 CRUD에 미리 만들지 않는다.

**팀 네이밍 룰**

- Django ORM 확장은 반드시 `OrderQuerySet`, `OrderManager`.
- 읽기 전용 조회는 `selectors.py`에 `order_get_detail`, `order_list_for_customer`.
- 쓰기 유스케이스는 작은 프로젝트에서 `services.py`의 `order_<verb>`.
- 중형 이상은 `<Verb>OrderService`: `PlaceOrderService`, `CancelOrderService`.
- Clean Architecture를 명시적으로 채택한 프로젝트만 `<Verb>OrderUseCase`.
- `OrderService`, `OrderManagerService`, `OrderUseCaseService` 같은 포괄/중복 suffix 금지.
- 도메인 메서드는 비즈니스 동사: `confirm_payment`, `cancel`, `mark_shipped`.
- CRUD 동사만 있는 이름은 피한다: `update_status`, `process`, `handle`.

**검증 기준**

- `rg "class Order(Service|UseCase|Manager)|OrderManager|OrderService|OrderUseCase"`로 혼용 지점을 찾는다.
- 각 이름이 위 표의 책임과 맞는지 확인한다.
- 도메인 규칙 조건문이 service/use case에 있으면 `Order` 메서드로 이동 후보로 표시한다.
- `Manager` 안에 `transaction.atomic`, 외부 API, 이메일, 상태 전이 로직이 있으면 책임 위반으로 본다.

---
> **관련 스킬 참조:**
> - Django 서비스 레이어와 selector 분리 → **implementation-django** 스킬
> - DDD Application Service / Domain Service 책임 분리 → **architecture-ddd** 스킬
> - 네이밍과 과한 추상화 방지 → **implementation-cleancode** 스킬