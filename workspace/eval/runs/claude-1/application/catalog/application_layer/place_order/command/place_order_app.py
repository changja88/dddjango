"""PlaceOrderApp — 주문 생성 유스케이스(응용 서비스).

흐름·트랜잭션 경계만 소유하고 비즈니스 로직은 도메인에 위임한다(§1.4·§3.6).
순서(한 transaction.atomic):
  1. Product 존재 확인 — 없으면 ProductNotFound(→404).
  2. unit_price 스냅샷 확보 — 조회한 Product.price.
  3. 차감 위임 — Product.deduct(qty)로 도메인 권위 검사(부족 시 InsufficientStock→409),
     이어 리포지토리 조건부 UPDATE로 영속화. rowcount=0이면 InsufficientStock으로 번역(409).
  4. Order 생성 — Order 생성자가 total_price=unit_price*quantity 강제(I4). 저장.
"""
from django.db import transaction

from application.catalog.application_layer.place_order.dto.place_order_command import (
    PlaceOrderCommand,
)
from application.catalog.application_layer.place_order.dto.place_order_result import (
    PlaceOrderResult,
)
from application.catalog.domain_layer.order.order import Order
from application.catalog.domain_layer.order.exception import ProductNotFound
from application.catalog.domain_layer.order.repository.order_repository import (
    OrderRepository,
)
from application.catalog.domain_layer.product.exception import InsufficientStock
from application.catalog.domain_layer.product.repository.product_repository import (
    ProductRepository,
)


class PlaceOrderApp:
    def __init__(
        self,
        product_repository: ProductRepository,
        order_repository: OrderRepository,
    ) -> None:
        self._product_repository = product_repository
        self._order_repository = order_repository

    def execute(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        with transaction.atomic():
            # 1. 존재 확인 — 없으면 차감 시도 전에 분기(404).
            product = self._product_repository.find_by_id(command.product_id)
            if product is None:
                raise ProductNotFound(command.product_id)

            # 2. unit_price 스냅샷 확보.
            unit_price = product.price

            # 3. 차감 위임 — 도메인 권위 검사(부족 시 InsufficientStock).
            product.deduct(command.quantity)
            # 조건부 원자 UPDATE로 영속화 — rowcount=0이면 race로 인한 부족(안전망).
            rowcount = self._product_repository.deduct_stock(
                command.product_id, command.quantity
            )
            if rowcount == 0:
                # race: 다른 트랜잭션이 재고를 가져가 UPDATE가 0행. product.stock은 이미
                # 메모리상 차감된 값이므로, DB의 실제 현재 잔여를 재조회해 보고한다(§2.5).
                current_product = self._product_repository.find_by_id(
                    command.product_id
                )
                raise InsufficientStock(
                    available_stock=current_product.stock,
                    requested_quantity=command.quantity,
                )

            # 4. Order 생성(생성자가 I4 강제) 후 저장.
            order = Order(
                product_id=command.product_id,
                quantity=command.quantity,
                unit_price=unit_price,
            )
            order_id = self._order_repository.save(order)

            return PlaceOrderResult(
                id=order_id,
                product_id=order.product_id,
                quantity=order.quantity,
                unit_price=order.unit_price,
                total_price=order.total_price,
            )
