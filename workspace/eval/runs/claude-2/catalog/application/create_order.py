"""응용 서비스 create_order — 트랜잭션 owner·흐름 오케스트레이션(설계 명세 section 4).

흐름: 입력 DTO 수신 -> 리포지토리로 조건부 원자 UPDATE 차감(rowcount 분류는 리포지토리가 수행,
404/409 도메인 예외 발생) -> Order 생성·저장 -> 결과 DTO 반환. 전체를 한 트랜잭션으로 묶어
부족·없음 시 재고 변화·주문 생성이 모두 롤백되게 한다.
"""

from __future__ import annotations

from django.db import transaction

from catalog.application.dto import CreateOrderCommand, CreateOrderResult
from catalog.domain.order import Order
from catalog.domain.order_repository import OrderRepository
from catalog.domain.product_repository import ProductRepository


def create_order(
    command: CreateOrderCommand,
    product_repository: ProductRepository,
    order_repository: OrderRepository,
) -> CreateOrderResult:
    with transaction.atomic():
        product = product_repository.deduct_stock(
            command.product_id, command.quantity
        )
        order = order_repository.add(
            Order(product_id=command.product_id, quantity=command.quantity)
        )

    return CreateOrderResult(
        order_id=order.id,
        product_id=order.product_id,
        quantity=order.quantity,
        status=order.status,
        remaining_stock=product.stock,
    )
