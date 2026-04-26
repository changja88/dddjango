# 전자상거래 주문 처리 아키텍처 설계

## 1. 아키텍처 개요

Django 모놀리스 내에서 **Layered Architecture + Domain Events** 패턴을 적용한다. 핵심 설계 원칙은 다음과 같다:

- **CQRS 라이트**: 주문 조회가 생성보다 10배 많으므로 Command(쓰기)와 Query(읽기) 경로를 분리
- **Anti-Corruption Layer**: 외부 시스템(토스페이먼츠, CJ대한통운)과의 결합을 방지하는 어댑터 계층
- **Domain Events**: 주문 상태 변경 시 이벤트를 발행하여 배송 시스템과 느슨하게 연결
- **Interface Segregation**: 배송 서비스를 인터페이스 뒤에 숨겨 향후 마이크로서비스 전환 대비

## 2. 디렉터리 구조

```
orders/
    __init__.py

    # --- Presentation Layer ---
    urls.py
    views/
        __init__.py
        command_views.py        # 주문 생성, 취소, 상태 변경 API
        query_views.py          # 주문 목록, 상세 조회 API
        serializers.py

    # --- Application Layer ---
    services/
        __init__.py
        order_command_service.py   # 주문 생성/변경 유스케이스
        order_query_service.py     # 주문 조회 유스케이스
    events/
        __init__.py
        handlers.py                # 도메인 이벤트 핸들러
        signals.py                 # Django signal 기반 이벤트 발행

    # --- Domain Layer ---
    domain/
        __init__.py
        models.py                  # Order, OrderItem, OrderStatus (엔티티/VO)
        enums.py                   # OrderStatus 열거형
        exceptions.py              # 도메인 예외
        rules.py                   # 주문 비즈니스 규칙

    # --- Infrastructure Layer ---
    infrastructure/
        __init__.py
        repositories/
            __init__.py
            order_repository.py        # 주문 저장소 (쓰기 최적화)
            order_read_repository.py   # 주문 조회 저장소 (읽기 최적화)
        adapters/
            __init__.py
            payment_adapter.py         # 토스페이먼츠 Anti-Corruption Layer
            shipping_adapter.py        # CJ대한통운 Anti-Corruption Layer
        interfaces/
            __init__.py
            payment_gateway.py         # 결제 게이트웨이 인터페이스
            shipping_gateway.py        # 배송 게이트웨이 인터페이스

    # --- Django Infra ---
    admin.py
    apps.py
    migrations/
```

## 3. 핵심 도메인 모델

### 3.1 Order 엔티티

```python
# orders/domain/enums.py
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"              # 주문 접수
    PAYMENT_REQUESTED = "payment_requested"  # 결제 요청됨
    PAID = "paid"                    # 결제 완료
    SHIPPING_REQUESTED = "shipping_requested"  # 배송 요청됨
    SHIPPED = "shipped"              # 배송 중
    DELIVERED = "delivered"          # 배송 완료
    CANCELLED = "cancelled"          # 취소


# orders/domain/models.py
import uuid
from django.db import models
from orders.domain.enums import OrderStatus

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, db_index=True)
    customer_id = models.IntegerField(db_index=True)
    status = models.CharField(
        max_length=30,
        choices=[(s.value, s.name) for s in OrderStatus],
        default=OrderStatus.PENDING.value,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_key = models.CharField(max_length=200, blank=True, null=True)
    shipping_tracking_number = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["customer_id", "-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["-created_at"]),
        ]

    # --- 도메인 로직 ---
    VALID_TRANSITIONS = {
        OrderStatus.PENDING: [OrderStatus.PAYMENT_REQUESTED, OrderStatus.CANCELLED],
        OrderStatus.PAYMENT_REQUESTED: [OrderStatus.PAID, OrderStatus.CANCELLED],
        OrderStatus.PAID: [OrderStatus.SHIPPING_REQUESTED, OrderStatus.CANCELLED],
        OrderStatus.SHIPPING_REQUESTED: [OrderStatus.SHIPPED],
        OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
    }

    def can_transition_to(self, new_status: OrderStatus) -> bool:
        current = OrderStatus(self.status)
        return new_status in self.VALID_TRANSITIONS.get(current, [])

    def transition_to(self, new_status: OrderStatus) -> None:
        if not self.can_transition_to(new_status):
            from orders.domain.exceptions import InvalidOrderTransitionError
            raise InvalidOrderTransitionError(
                f"Cannot transition from {self.status} to {new_status.value}"
            )
        self.status = new_status.value


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"
```

### 3.2 도메인 예외

```python
# orders/domain/exceptions.py

class OrderDomainError(Exception):
    """주문 도메인 기본 예외"""
    pass

class InvalidOrderTransitionError(OrderDomainError):
    """유효하지 않은 상태 전이"""
    pass

class PaymentFailedError(OrderDomainError):
    """결제 실패"""
    pass

class ShippingRequestFailedError(OrderDomainError):
    """배송 요청 실패"""
    pass
```

## 4. 외부 시스템 통합 (Anti-Corruption Layer)

### 4.1 인터페이스 정의

```python
# orders/infrastructure/interfaces/payment_gateway.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class PaymentRequest:
    order_id: str
    amount: Decimal
    order_name: str

@dataclass(frozen=True)
class PaymentResult:
    payment_key: str
    approved: bool
    message: str

class PaymentGateway(ABC):
    @abstractmethod
    def approve_payment(self, request: PaymentRequest) -> PaymentResult:
        pass

    @abstractmethod
    def cancel_payment(self, payment_key: str, reason: str) -> bool:
        pass


# orders/infrastructure/interfaces/shipping_gateway.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class ShippingRequest:
    order_id: str
    recipient_name: str
    recipient_address: str
    recipient_phone: str
    items_summary: str

@dataclass(frozen=True)
class ShippingResult:
    tracking_number: str
    success: bool
    message: str

class ShippingGateway(ABC):
    @abstractmethod
    def request_shipping(self, request: ShippingRequest) -> ShippingResult:
        pass

    @abstractmethod
    def get_shipping_status(self, tracking_number: str) -> str:
        pass
```

### 4.2 어댑터 구현

```python
# orders/infrastructure/adapters/payment_adapter.py
import requests
from django.conf import settings
from orders.infrastructure.interfaces.payment_gateway import (
    PaymentGateway, PaymentRequest, PaymentResult,
)

class TossPaymentsAdapter(PaymentGateway):
    """토스페이먼츠 API를 내부 인터페이스로 변환하는 어댑터"""

    BASE_URL = "https://api.tosspayments.com/v1"

    def __init__(self):
        self.secret_key = settings.TOSS_PAYMENTS_SECRET_KEY

    def approve_payment(self, request: PaymentRequest) -> PaymentResult:
        response = requests.post(
            f"{self.BASE_URL}/payments/confirm",
            json={
                "orderId": request.order_id,
                "amount": int(request.amount),
                "paymentKey": request.order_id,  # 실제로는 클라이언트에서 전달
            },
            headers=self._auth_headers(),
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            return PaymentResult(
                payment_key=data["paymentKey"],
                approved=True,
                message="결제 승인 완료",
            )
        return PaymentResult(payment_key="", approved=False, message=response.text)

    def cancel_payment(self, payment_key: str, reason: str) -> bool:
        response = requests.post(
            f"{self.BASE_URL}/payments/{payment_key}/cancel",
            json={"cancelReason": reason},
            headers=self._auth_headers(),
            timeout=30,
        )
        return response.status_code == 200

    def _auth_headers(self) -> dict:
        import base64
        encoded = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }


# orders/infrastructure/adapters/shipping_adapter.py
import requests
from django.conf import settings
from orders.infrastructure.interfaces.shipping_gateway import (
    ShippingGateway, ShippingRequest, ShippingResult,
)

class CJLogisticsAdapter(ShippingGateway):
    """CJ대한통운 API를 내부 인터페이스로 변환하는 어댑터"""

    def __init__(self):
        self.api_key = settings.CJ_LOGISTICS_API_KEY
        self.base_url = settings.CJ_LOGISTICS_BASE_URL

    def request_shipping(self, request: ShippingRequest) -> ShippingResult:
        response = requests.post(
            f"{self.base_url}/shipping/orders",
            json={
                "orderId": request.order_id,
                "receiverName": request.recipient_name,
                "receiverAddr": request.recipient_address,
                "receiverPhone": request.recipient_phone,
                "goodsName": request.items_summary,
            },
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            return ShippingResult(
                tracking_number=data.get("trackingNumber", ""),
                success=True,
                message="배송 접수 완료",
            )
        return ShippingResult(tracking_number="", success=False, message=response.text)

    def get_shipping_status(self, tracking_number: str) -> str:
        response = requests.get(
            f"{self.base_url}/shipping/tracking/{tracking_number}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("status", "UNKNOWN")
        return "UNKNOWN"
```

## 5. CQRS 분리 (Application Layer)

### 5.1 Command Service (쓰기)

```python
# orders/services/order_command_service.py
import logging
from django.db import transaction
from orders.domain.models import Order, OrderItem
from orders.domain.enums import OrderStatus
from orders.domain.exceptions import PaymentFailedError, ShippingRequestFailedError
from orders.infrastructure.interfaces.payment_gateway import PaymentGateway, PaymentRequest
from orders.infrastructure.interfaces.shipping_gateway import ShippingGateway, ShippingRequest
from orders.events.signals import order_paid, order_shipping_requested

logger = logging.getLogger(__name__)


class OrderCommandService:
    def __init__(
        self,
        payment_gateway: PaymentGateway,
        shipping_gateway: ShippingGateway,
    ):
        self._payment = payment_gateway
        self._shipping = shipping_gateway

    @transaction.atomic
    def create_order(self, customer_id: int, items: list[dict]) -> Order:
        """주문 생성 (PENDING 상태)"""
        order = Order.objects.create(
            customer_id=customer_id,
            order_number=self._generate_order_number(),
            total_amount=sum(
                item["unit_price"] * item["quantity"] for item in items
            ),
        )
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )
            for item in items
        ])
        return order

    @transaction.atomic
    def confirm_payment(self, order_id: str, payment_key: str) -> Order:
        """결제 승인 처리"""
        order = Order.objects.select_for_update().get(id=order_id)
        order.transition_to(OrderStatus.PAYMENT_REQUESTED)
        order.save()

        result = self._payment.approve_payment(
            PaymentRequest(
                order_id=str(order.id),
                amount=order.total_amount,
                order_name=f"주문 {order.order_number}",
            )
        )

        if not result.approved:
            order.transition_to(OrderStatus.CANCELLED)
            order.save()
            raise PaymentFailedError(result.message)

        order.payment_key = result.payment_key
        order.transition_to(OrderStatus.PAID)
        order.save()

        # 도메인 이벤트 발행 -> 배송 요청 트리거
        order_paid.send(sender=self.__class__, order=order)
        return order

    def request_shipping(self, order_id: str, shipping_info: dict) -> Order:
        """배송 요청 (이벤트 핸들러 또는 직접 호출)"""
        order = Order.objects.select_for_update().get(id=order_id)
        order.transition_to(OrderStatus.SHIPPING_REQUESTED)
        order.save()

        result = self._shipping.request_shipping(
            ShippingRequest(
                order_id=str(order.id),
                recipient_name=shipping_info["name"],
                recipient_address=shipping_info["address"],
                recipient_phone=shipping_info["phone"],
                items_summary=self._build_items_summary(order),
            )
        )

        if not result.success:
            raise ShippingRequestFailedError(result.message)

        order.shipping_tracking_number = result.tracking_number
        order.save()

        order_shipping_requested.send(sender=self.__class__, order=order)
        return order

    @transaction.atomic
    def cancel_order(self, order_id: str, reason: str) -> Order:
        """주문 취소"""
        order = Order.objects.select_for_update().get(id=order_id)
        order.transition_to(OrderStatus.CANCELLED)

        if order.payment_key:
            self._payment.cancel_payment(order.payment_key, reason)

        order.save()
        return order

    def _generate_order_number(self) -> str:
        import time
        import random
        return f"ORD-{int(time.time())}-{random.randint(1000, 9999)}"

    def _build_items_summary(self, order: Order) -> str:
        items = order.items.all()
        first = items.first()
        if items.count() > 1:
            return f"{first.product_name} 외 {items.count() - 1}건"
        return first.product_name
```

### 5.2 Query Service (읽기)

```python
# orders/services/order_query_service.py
from django.core.cache import cache
from orders.domain.models import Order

CACHE_TTL = 60 * 5  # 5분


class OrderQueryService:
    """
    읽기 전용 서비스.
    - select_related/prefetch_related로 N+1 방지
    - 캐시 레이어를 통한 조회 성능 최적화
    - 쓰기 모델과 분리하여 독립적으로 최적화 가능
    """

    def get_order_detail(self, order_id: str) -> Order:
        cache_key = f"order:detail:{order_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        order = (
            Order.objects
            .select_related()
            .prefetch_related("items")
            .get(id=order_id)
        )
        cache.set(cache_key, order, CACHE_TTL)
        return order

    def list_customer_orders(
        self, customer_id: int, page: int = 1, page_size: int = 20
    ):
        cache_key = f"order:list:{customer_id}:{page}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        offset = (page - 1) * page_size
        orders = (
            Order.objects
            .filter(customer_id=customer_id)
            .prefetch_related("items")
            .order_by("-created_at")[offset:offset + page_size]
        )
        result = list(orders)
        cache.set(cache_key, result, CACHE_TTL)
        return result

    def list_orders_by_status(self, status: str, page: int = 1, page_size: int = 50):
        offset = (page - 1) * page_size
        return list(
            Order.objects
            .filter(status=status)
            .order_by("-created_at")[offset:offset + page_size]
        )
```

## 6. 도메인 이벤트 (배송 시스템 연동)

```python
# orders/events/signals.py
import django.dispatch

order_paid = django.dispatch.Signal()              # sender, order
order_shipping_requested = django.dispatch.Signal() # sender, order
order_cancelled = django.dispatch.Signal()          # sender, order


# orders/events/handlers.py
import logging
from django.dispatch import receiver
from django.core.cache import cache
from orders.events.signals import order_paid, order_shipping_requested

logger = logging.getLogger(__name__)


@receiver(order_paid)
def handle_order_paid(sender, order, **kwargs):
    """결제 완료 시 캐시 무효화 및 후속 처리"""
    cache.delete(f"order:detail:{order.id}")
    cache.delete_pattern(f"order:list:{order.customer_id}:*")
    logger.info(f"Order {order.order_number} paid, cache invalidated")


@receiver(order_shipping_requested)
def handle_shipping_requested(sender, order, **kwargs):
    """배송 요청 완료 후처리"""
    cache.delete(f"order:detail:{order.id}")
    logger.info(
        f"Order {order.order_number} shipping requested, "
        f"tracking: {order.shipping_tracking_number}"
    )
```

## 7. Presentation Layer (API)

```python
# orders/views/command_views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from orders.services.order_command_service import OrderCommandService
from orders.infrastructure.adapters.payment_adapter import TossPaymentsAdapter
from orders.infrastructure.adapters.shipping_adapter import CJLogisticsAdapter
from orders.domain.exceptions import OrderDomainError


def _get_command_service() -> OrderCommandService:
    """서비스 인스턴스 생성 (간이 DI)"""
    return OrderCommandService(
        payment_gateway=TossPaymentsAdapter(),
        shipping_gateway=CJLogisticsAdapter(),
    )


class OrderCreateView(APIView):
    def post(self, request):
        service = _get_command_service()
        try:
            order = service.create_order(
                customer_id=request.user.id,
                items=request.data["items"],
            )
            return Response(
                {"order_id": str(order.id), "order_number": order.order_number},
                status=status.HTTP_201_CREATED,
            )
        except OrderDomainError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderPaymentConfirmView(APIView):
    def post(self, request, order_id):
        service = _get_command_service()
        try:
            order = service.confirm_payment(
                order_id=order_id,
                payment_key=request.data["payment_key"],
            )
            return Response({"status": order.status})
        except OrderDomainError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderCancelView(APIView):
    def post(self, request, order_id):
        service = _get_command_service()
        try:
            order = service.cancel_order(order_id, request.data.get("reason", ""))
            return Response({"status": order.status})
        except OrderDomainError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# orders/views/query_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from orders.services.order_query_service import OrderQueryService
from orders.views.serializers import OrderDetailSerializer, OrderListSerializer


class OrderDetailView(APIView):
    def get(self, request, order_id):
        service = OrderQueryService()
        order = service.get_order_detail(order_id)
        return Response(OrderDetailSerializer(order).data)


class OrderListView(APIView):
    def get(self, request):
        service = OrderQueryService()
        page = int(request.query_params.get("page", 1))
        orders = service.list_customer_orders(request.user.id, page=page)
        return Response(OrderListSerializer(orders, many=True).data)
```

## 8. 마이크로서비스 전환 전략

현재 구조가 향후 배송 서비스 분리를 자연스럽게 지원하는 방법:

### 8.1 현재 (모놀리스)

```
OrderCommandService --> ShippingGateway (interface)
                              |
                    CJLogisticsAdapter (같은 프로세스)
```

### 8.2 전환 후 (마이크로서비스)

```
OrderCommandService --> ShippingGateway (interface)
                              |
                    ShippingServiceAdapter (HTTP/gRPC 호출)
                              |
                    [Shipping Microservice]
                              |
                    CJLogisticsAdapter (배송 서비스 내부)
```

전환 시 변경 사항:

| 계층 | 변경 여부 | 설명 |
|------|-----------|------|
| Domain (models, rules) | 변경 없음 | 주문 도메인은 배송과 무관 |
| Interface (ShippingGateway) | 변경 없음 | 인터페이스 계약 유지 |
| Adapter | **교체** | `CJLogisticsAdapter` -> `ShippingServiceAdapter` |
| Event Handler | **교체** | Django Signal -> 메시지 큐 (Kafka/RabbitMQ) |
| Service | 변경 없음 | 인터페이스에만 의존 |

```python
# 전환 후 새 어댑터 예시
class ShippingMicroserviceAdapter(ShippingGateway):
    """배송 마이크로서비스를 호출하는 어댑터"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def request_shipping(self, request: ShippingRequest) -> ShippingResult:
        response = requests.post(
            f"{self.base_url}/api/v1/shipments",
            json=dataclasses.asdict(request),
            timeout=10,
        )
        data = response.json()
        return ShippingResult(
            tracking_number=data["tracking_number"],
            success=data["success"],
            message=data["message"],
        )
```

## 9. 주요 설계 결정 요약

| 결정 | 근거 |
|------|------|
| CQRS 라이트 (서비스 레벨 분리) | 조회:생성 = 10:1 비율. 별도 DB까지는 불필요하나 서비스 분리로 독립 최적화 가능 |
| Django Signal 기반 이벤트 | 모놀리스 내에서 가장 낮은 도입 비용. 전환 시 메시지 큐로 교체 |
| Anti-Corruption Layer (어댑터 패턴) | 외부 PG/배송 API의 변경이 도메인에 전파되지 않도록 차단 |
| 상태 전이 규칙을 엔티티에 배치 | 주문 상태 머신은 핵심 불변식. 서비스가 아닌 엔티티가 보호 |
| 읽기 경로에 캐시 적용 | 10배 많은 조회에 대한 DB 부하 감소 |
| 인터페이스 기반 외부 의존성 | 배송 서비스 분리 시 어댑터만 교체. 도메인/서비스 코드 무변경 |
