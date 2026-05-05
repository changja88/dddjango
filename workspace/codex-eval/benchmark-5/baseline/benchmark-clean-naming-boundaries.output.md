Fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았습니다. 대신 benchmark case와 관련 문서(`architecture-ddd`, `implementation-django`, `service-layer`, `queryset-manager`)를 읽고 기준을 정리했습니다.

**권장 팀 컨벤션**

`OrderManager`는 Django ORM 전용으로 제한하세요. `models.Manager` 또는 `QuerySet` 서브클래스일 때만 쓰고, 주문 생성/확정/취소 같은 유스케이스 조율에는 쓰지 않습니다.

`OrderService`는 클래스명으로 쓰지 않는 쪽을 권합니다. 너무 넓어서 도메인 서비스인지, 애플리케이션 서비스인지, 외부 연동 서비스인지 흐려집니다. Django 관용을 따를 때는 `orders/services.py` 모듈 안에 `order_create`, `order_confirm`, `order_cancel` 같은 함수로 둡니다.

`OrderUseCase`도 피하세요. 유스케이스는 명사가 아니라 행위 단위여야 합니다. 클래스를 쓴다면 `CreateOrderUseCase`, `ConfirmOrderUseCase`, `CancelOrderUseCase`처럼 동사+대상으로 나눕니다.

DDD를 더 엄격히 적용하는 큰 도메인에서는 둘 중 하나만 선택하세요.

- Django 실용형: `orders/services.py` + `order_create()`, `order_confirm()`
- DDD 명시형: `application_layer/use_cases/confirm_order.py` + `ConfirmOrderUseCase`

섞지 않는 게 핵심입니다.

```diff
diff --git a/skills/implementation-django/references/service-layer.md b/skills/implementation-django/references/service-layer.md
--- a/skills/implementation-django/references/service-layer.md
+++ b/skills/implementation-django/references/service-layer.md
@@
 ## HackSoft 서비스/셀렉터 패턴 [HS]
+
+## 네이밍과 책임 경계
+
+주문처럼 유스케이스가 많은 도메인에서 `OrderManager`, `OrderService`,
+`OrderUseCase`를 섞어 쓰지 않는다. 이름은 레이어보다 책임을 먼저 드러내야 한다.
+
+| 이름 | 허용 위치 | 책임 | 금지 |
+|---|---|---|---|
+| `OrderManager` | Django model `objects` | QuerySet 생성, 기본 필터, 체이닝 가능한 조회 | 주문 생성/결제/취소 같은 유스케이스 조율 |
+| `orders/services.py` | Django app | 쓰기 유스케이스 함수. 트랜잭션, 모델 호출, 외부 부수효과 조율 | 모든 주문 규칙을 담는 `OrderService` 클래스 |
+| `CreateOrderUseCase` | DDD application layer | 하나의 명확한 유스케이스 실행 | `OrderUseCase`처럼 대상만 있고 행위가 없는 이름 |
+| `OrderPolicy`, `DiscountCalculator` | domain layer | 특정 엔티티/값 객체에 넣기 어려운 순수 도메인 규칙 | DB, HTTP, Django request 접근 |
+
+기본값은 Django 실용형이다. `orders/services.py`에 `<entity>_<action>` 함수
+(`order_create`, `order_confirm`, `order_cancel`)를 두고, 읽기는
+`orders/selectors.py`로 분리한다.
+
+도메인이 커져 유스케이스별 의존성, 트랜잭션, 이벤트 발행이 복잡해질 때만
+`CreateOrderUseCase`, `ConfirmOrderUseCase` 같은 class-per-use-case로 올린다.
+이 경우에도 `OrderUseCase`, `OrderService`처럼 넓은 이름은 사용하지 않는다.
 
 ```python
 # services.py -- 쓰기(Command) 로직
 def user_create(*, email: str, password: str) -> User:
diff --git a/skills/architecture-ddd/references/filetree-with-django.md b/skills/architecture-ddd/references/filetree-with-django.md
--- a/skills/architecture-ddd/references/filetree-with-django.md
+++ b/skills/architecture-ddd/references/filetree-with-django.md
@@
     ├── application_layer/          # 유스케이스 조율 (비즈니스 로직 금지, 조율만)
-    │   ├── *_service.py            # 응용 서비스 (네이밍: *_service.py)
+    │   ├── services.py             # Django 실용형: order_create/order_confirm 함수
+    │   ├── use_cases/              # 복잡한 DDD형: CreateOrderUseCase 등 행위 단위 클래스
     │   └── event_handlers.py       # 타 도메인 이벤트 구독 핸들러 (@receiver)
@@
 ### Django 앱 규칙
@@
 - 클래스명: `<모델명>Model` — 반드시 `Model` 접미사
 - `models/__init__.py`에서 모든 모델을 re-export
+
+### Manager / Service / UseCase 네이밍 규칙
+
+- `Manager`는 Django ORM `models.Manager` / `QuerySet`에만 사용한다.
+- `Service`는 모듈명(`services.py`) 또는 구체적 외부 어댑터명(`PaymentGateway`)에만
+  사용하고, `OrderService` 같은 넓은 클래스명은 피한다.
+- `UseCase`는 클래스 단위로 쓸 때 행위를 포함한다:
+  `CreateOrderUseCase`, `CancelOrderUseCase`.
+- 도메인 서비스는 `OrderService`가 아니라 도메인 개념으로 이름 붙인다:
+  `DiscountPolicy`, `ShippingFeeCalculator`, `InventoryReservationPolicy`.
```

검증은 하지 않았습니다. 현재 환경이 읽기 전용이고, 위 내용은 파일 수정 대신 적용 가능한 unified diff로 제시했습니다.