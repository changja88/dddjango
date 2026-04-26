# Architecture Review: OrderService.confirm_order

## Overview

`order/domain/order_service.py`의 `OrderService.confirm_order` 메서드를 아키텍처 패턴 관점에서 리뷰한다. 이 코드는 주문 확인 처리를 단일 메서드에서 수행하며, DB 조회, 결제, 상태 변경, 이메일 발송, 외부 시스템 호출을 모두 포함한다.

---

## Review Checklist

| # | 점검 항목 | 결과 |
|---|---|---|
| 1 | Dependencies point inward (domain does not import infrastructure) | FAIL |
| 2 | Interfaces are owned by the consuming layer, not the implementing layer | FAIL |
| 3 | External systems are isolated behind ports/adapters or ACL | FAIL |
| 4 | CQRS is applied selectively, not system-wide | N/A |
| 5 | Domain events are not directly exposed as integration events | N/A |
| 6 | Repository abstractions are per aggregate, not per table | FAIL |
| 7 | Unit of Work manages transaction boundaries explicitly | FAIL |

---

## Findings

### 1. Domain Layer가 Infrastructure에 직접 의존

```
[Hexagonal / DIP] -- 도메인 서비스가 인프라 구현체를 직접 import하여
Dependency Rule을 위반한다.
```

파일 경로가 `order/domain/order_service.py`인데, 이 모듈이 다음 인프라 요소를 직접 import한다:

- `from order.infrastructure.email_client import send_confirmation_email`
- `from order.infrastructure.models import OrderModel`
- `import requests`
- `from stripe import Stripe`

DIP(Dependency Inversion Principle)에 따르면 고수준 모듈(도메인)이 저수준 모듈(인프라)에 의존해서는 안 된다. 현재 코드에서는 도메인이 4개의 인프라 구현체에 직접 결합되어 있다. 도메인 계층은 추상화(Port)를 정의하고, 인프라가 이를 구현해야 한다.

### 2. Port/Interface 부재 -- Ownership Inversion 미적용

```
[Hexagonal / Ownership Inversion] -- 도메인이 사용할 인터페이스(Port)가
전혀 정의되어 있지 않아, 인프라 교체 및 테스트 격리가 불가능하다.
```

Hexagonal Architecture에서 도메인은 Driven Port(인터페이스)를 정의하고 소유한다. 현재 코드에는 다음 Port가 모두 누락되어 있다:

- **PaymentGateway** -- 결제 처리 추상화
- **OrderRepository** -- 주문 영속성 추상화
- **NotificationService** -- 이메일 발송 추상화
- **ShippingService** -- 배송 시스템 통신 추상화

이 인터페이스들이 없으므로 구현체를 Mock으로 교체할 수 없고, 단위 테스트가 불가능하다.

### 3. 외부 시스템 직접 호출 -- ACL/Adapter 부재

```
[Integration / ACL] -- 외부 시스템(Stripe, shipping-service)을 ACL이나
Adapter 없이 도메인에서 직접 호출하여, 외부 변경이 도메인을 오염시킨다.
```

**Stripe 결제**: API 키가 하드코딩(`"sk_live_xxx"`)되어 있고, Stripe SDK를 도메인 서비스에서 직접 인스턴스화한다. Stripe API 변경 시 도메인 코드가 직접 영향을 받는다.

**배송 시스템**: `requests.post()`로 HTTP URL을 하드코딩하여 직접 호출한다. 배송 시스템의 API 스키마, URL, 프로토콜이 변경되면 도메인 코드를 수정해야 한다.

ACL은 외부 시스템의 모델과 인터페이스를 내부 도메인 개념으로 번역하는 격리 계층이다. 현재 두 외부 시스템 모두 이 격리 없이 도메인에 노출되어 있다.

### 4. Repository 추상화 부재 -- ORM 직접 사용

```
[Persistence / Repository] -- Django ORM의 Manager API(objects.select_related,
items.values)를 도메인 서비스에서 직접 사용하여 영속성 기술에 강결합된다.
```

`OrderModel.objects.select_related('user').get(id=order_id)`는 Django ORM의 Active Record 패턴을 도메인 서비스에서 직접 호출하는 것이다. Repository 패턴을 적용하면 도메인은 `order_repository.get(order_id)`만 알면 되고, ORM 구현 세부사항(select_related, values 등)은 Repository 내부에 캡슐화된다.

반환부의 `list(order.items.values("name", "quantity", "price"))` 역시 Django QuerySet API가 도메인 로직에 노출된 사례이다.

### 5. 트랜잭션 경계 미관리

```
[Persistence / Unit of Work] -- 결제, DB 저장, 이메일, 외부 호출이 하나의
메서드에서 암묵적으로 실행되어, 부분 실패 시 일관성이 보장되지 않는다.
```

현재 실행 순서에서 다음 시나리오가 문제가 된다:

1. Stripe 결제 성공 후 `order.save()` 실패 -- 결제는 됐으나 DB에 반영 안 됨
2. `order.save()` 성공 후 이메일 발송 실패 -- 주문은 확인됐으나 사용자 미통보
3. 이메일 성공 후 배송 시스템 호출 실패 -- 주문 확인/통보됐으나 배송 미등록

Unit of Work 패턴으로 트랜잭션 경계를 명시적으로 관리하고, 외부 시스템 호출(이메일, 배송)은 트랜잭션 커밋 후 별도 처리해야 한다.

### 6. Command와 Query의 혼합

```
[CQRS / CQS] -- confirm_order 메서드가 상태를 변경(Command)하면서
동시에 조회용 dict를 반환(Query)하여 CQS 원칙을 위반한다.
```

Meyer의 CQS 원칙에 따르면 상태를 변경하는 메서드는 값을 반환하지 않아야 한다. `confirm_order`는 결제 처리, 상태 변경, 이메일 발송, 외부 호출(Command)을 수행하면서 동시에 조회용 dict(Query)를 반환한다. 주문 확인 처리와 주문 정보 조회는 분리되어야 한다.

CQRS를 시스템 전체에 적용할 필요는 없으나, 최소한 CQS 수준에서 Command 메서드와 Query 메서드를 분리하는 것이 바람직하다.

---

## Summary

이 코드의 근본적인 문제는 **도메인 서비스가 모든 인프라 구현체에 직접 의존**한다는 점이다. Hexagonal Architecture의 핵심 목표인 "UI나 DB 없이 비즈니스 규칙을 테스트할 수 있어야 한다"(Cockburn)가 달성되지 않는다.

개선 방향을 우선순위로 정리하면:

1. **Port 정의**: 도메인 계층에 PaymentGateway, OrderRepository, NotificationService, ShippingGateway 인터페이스를 정의한다.
2. **Adapter 구현**: 각 Port에 대한 인프라 Adapter(StripePaymentGateway, DjangoOrderRepository 등)를 인프라 계층에 구현한다.
3. **DI 적용**: OrderService 생성자에서 Port를 주입받도록 변경한다.
4. **트랜잭션 경계 분리**: 핵심 트랜잭션(결제+DB 저장)과 부가 작업(이메일, 배송 알림)을 분리한다. 부가 작업은 트랜잭션 커밋 후 비동기 또는 이벤트 기반으로 처리한다.
5. **CQS 분리**: 상태 변경(confirm)과 조회(get order detail)를 별도 메서드로 분리한다.
