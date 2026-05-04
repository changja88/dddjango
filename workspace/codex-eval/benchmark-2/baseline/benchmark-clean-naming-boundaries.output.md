`config.toml`은 현재 디렉터리에 없어서 프로젝트별 규칙은 확인하지 못했습니다. 일반적인 Django DDD 기준으로는 아래처럼 정리하는 게 가장 덜 헷갈립니다.

**권장 기준**

`OrderUseCase`
- 애플리케이션 계층.
- 사용자/시스템이 수행하는 “업무 시나리오”를 표현.
- 트랜잭션 경계, 권한/입력 검증 조율, 도메인 객체 호출, 저장소 호출, 이벤트 발행 조율을 담당.
- 예: `CreateOrderUseCase`, `CancelOrderUseCase`, `PayOrderUseCase`
- 보통 가장 명확한 이름입니다.

`OrderService`
- 이름만으로는 모호해서 남용하기 쉽습니다.
- 쓴다면 두 종류 중 하나로 제한하는 게 좋습니다.

1. `Application Service`
   - 사실상 UseCase와 같은 역할.
   - 이 경우 `OrderService`보다 `OrderApplicationService` 또는 구체적인 `CreateOrderUseCase`가 낫습니다.

2. `Domain Service`
   - 특정 엔티티 하나에 넣기 애매한 순수 도메인 규칙.
   - DB, Django ORM, 외부 API를 몰라야 합니다.
   - 예: `OrderPricingService`, `OrderEligibilityService`
   - “주문 생성 흐름 전체”를 담당하면 안 됩니다.

`OrderManager`
- Django에서는 이미 `models.Manager` 의미가 강합니다.
- ORM QuerySet/Manager 커스터마이징에만 쓰는 것을 권장합니다.
- 예: `Order.objects.active()`, `OrderManager.get_queryset()`
- 유스케이스나 비즈니스 흐름 이름으로 쓰면 혼란이 커집니다.

**추천 네이밍 규칙**

```text
orders/
  domain/
    models.py              # Order, OrderItem
    services.py            # OrderPricingService 같은 순수 도메인 서비스
    repositories.py        # OrderRepository interface
  application/
    use_cases.py           # CreateOrderUseCase, CancelOrderUseCase
    dtos.py
  infrastructure/
    repositories.py        # DjangoOrderRepository
  models.py                # Django ORM 모델
  views.py                 # DRF/View
```

**책임 기준**

```text
View / API
- HTTP 요청/응답
- serializer 검증
- UseCase 호출

UseCase
- 하나의 업무 흐름
- 트랜잭션 시작
- repository 조회/저장
- domain model/domain service 호출
- 결과 DTO 반환

Domain Model
- 핵심 상태와 불변식
- 예: order.cancel(), order.add_item()

Domain Service
- 엔티티에 넣기 애매한 순수 도메인 계산/판단
- DB 접근 없음

Repository
- 저장/조회 추상화
- Django ORM 세부사항 숨김

Manager
- Django ORM QuerySet 편의 기능만
```

**실무 결론**

`OrderManager`, `OrderService`, `OrderUseCase`가 섞여 있다면 이렇게 정리하세요.

- 업무 흐름이면 `CreateOrderUseCase`, `CancelOrderUseCase`
- 순수 도메인 판단/계산이면 `OrderPricingService`, `OrderPolicyService`
- ORM 쿼리 편의 기능이면 `OrderManager`
- 애매한 `OrderService`는 새로 만들지 말고, 기존 것도 가능하면 `UseCase` 또는 구체적인 `DomainService`로 분해

즉, Django DDD에서는 `OrderUseCase`를 애플리케이션 흐름의 기본 이름으로 잡고, `OrderService`는 도메인 서비스일 때만 제한적으로 쓰는 게 가장 명확합니다.