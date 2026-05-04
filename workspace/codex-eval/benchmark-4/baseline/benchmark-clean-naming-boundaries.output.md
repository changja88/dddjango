현재 `/private/tmp/dddjango-codex-eval`에는 `config.toml` 파일이 없어서 프로젝트별 규칙은 확인하지 못했습니다. Django DDD 기준으로는 아래처럼 정리하는 게 가장 덜 헷갈립니다.

**권장 네이밍**

`OrderUseCase`를 기준 이름으로 쓰는 것을 추천합니다.

```text
OrderUseCase
CreateOrderUseCase
CancelOrderUseCase
PayOrderUseCase
```

이유는 DDD에서 애플리케이션 계층의 핵심 책임이 “비즈니스 기능 하나를 수행하는 유스케이스 조율”이기 때문입니다. `Service`, `Manager`는 Django와 일반 레이어드 아키텍처에서 의미가 너무 넓어져서 금방 섞입니다.

**책임 기준**

`OrderUseCase`

- 애플리케이션 계층
- 트랜잭션 경계 담당
- DTO/input command를 받아 도메인 객체를 로드
- 도메인 메서드 호출
- repository 저장
- 외부 포트 호출 조율
- 복잡한 도메인 판단은 직접 하지 않음

예:

```python
class CancelOrderUseCase:
    def execute(self, command: CancelOrderCommand) -> None:
        order = self.order_repository.get(command.order_id)
        order.cancel(reason=command.reason)
        self.order_repository.save(order)
```

`OrderService`

- 가급적 “도메인 서비스”에만 사용
- 특정 Entity/Value Object 안에 넣기 어색한 순수 도메인 규칙을 담당
- DB, Django ORM, HTTP, Celery, settings에 의존하지 않음
- 상태 변경의 주체가 아니라 도메인 판단/계산을 담당

예:

```python
class OrderPricingService:
    def calculate_total(self, items: list[OrderItem]) -> Money:
        ...
```

`OrderManager`

- Django ORM의 `models.Manager`에만 사용
- `Order.objects` 커스텀 쿼리 API
- DDD 유스케이스나 도메인 조율 이름으로 쓰지 않음

예:

```python
class OrderManager(models.Manager):
    def paid(self):
        return self.filter(status=OrderStatus.PAID)
```

**실무 규칙**

이렇게 고정하면 됩니다.

```text
UseCase  = 애플리케이션 작업 단위
Service  = 순수 도메인 규칙 또는 외부 인프라 어댑터 명칭에만 제한적으로 사용
Manager  = Django ORM Manager 전용
```

추천 구조는 이런 식입니다.

```text
orders/
  application/
    use_cases/
      create_order.py
      cancel_order.py
  domain/
    entities.py
    services.py
    repositories.py
  infrastructure/
    django_models.py
    repositories.py
```

최종 기준:

```text
주문 생성/취소/결제 흐름 = CreateOrderUseCase, CancelOrderUseCase
주문 가격/정책/검증 규칙 = OrderPricingService, OrderPolicyService
Django QuerySet/objects 확장 = OrderManager
```

그래서 `OrderManager`, `OrderService`, `OrderUseCase`가 섞여 있다면, 우선 애플리케이션 흐름은 전부 `*UseCase`로 통일하고, `Manager`는 ORM 전용으로 격리하는 쪽이 가장 명확합니다.