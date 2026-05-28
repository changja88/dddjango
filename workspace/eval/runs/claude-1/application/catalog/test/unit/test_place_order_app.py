"""PlaceOrderApp 응용 서비스 흐름 단위 테스트 (§1.4 / §5.6).

흐름: 존재확인(없으면 ProductNotFound) → 차감 위임 → 조건부 UPDATE,
rowcount=0이면 InsufficientStock 번역 → Order 생성. mock 리포지토리로 협력·순서를 검증한다.
트랜잭션 경계(transaction.atomic)는 인수/통합 테스트가 덮으므로 여기서는 흐름·번역만 본다.
"""
from typing import Optional
from unittest import mock

from django.test import TestCase

from application.catalog.application_layer.place_order.command.place_order_app import (
    PlaceOrderApp,
)
from application.catalog.application_layer.place_order.dto.place_order_command import (
    PlaceOrderCommand,
)
from application.catalog.domain_layer.order.exception import ProductNotFound
from application.catalog.domain_layer.product.exception import InsufficientStock
from application.catalog.domain_layer.product.product import Product


def _build_app(
    product: Optional[Product], deduct_rowcount: int
) -> "tuple[PlaceOrderApp, mock.Mock, mock.Mock]":
    product_repository = mock.Mock()
    product_repository.find_by_id.return_value = product
    product_repository.deduct_stock.return_value = deduct_rowcount
    order_repository = mock.Mock()
    order_repository.save.return_value = 10
    app = PlaceOrderApp(
        product_repository=product_repository,
        order_repository=order_repository,
    )
    return app, product_repository, order_repository


class PlaceOrderAppTest(TestCase):
    def test_상품이_없으면_ProductNotFound를_던지고_차감하지_않는다(self) -> None:
        app, product_repository, order_repository = _build_app(
            product=None, deduct_rowcount=0
        )

        with self.assertRaises(ProductNotFound):
            app.execute(PlaceOrderCommand(product_id=999, quantity=1))

        product_repository.deduct_stock.assert_not_called()
        order_repository.save.assert_not_called()

    def test_재고가_충분하면_차감하고_주문을_생성한다(self) -> None:
        product = Product(id=1, name="위젯", price=1000, stock=10)
        app, product_repository, order_repository = _build_app(
            product=product, deduct_rowcount=1
        )

        result = app.execute(PlaceOrderCommand(product_id=1, quantity=2))

        # 존재확인 → 차감 위임(조건부 UPDATE) → 생성 순서.
        product_repository.find_by_id.assert_called_once_with(1)
        product_repository.deduct_stock.assert_called_once_with(1, 2)
        order_repository.save.assert_called_once()
        # 생성된 Order는 단가 스냅샷·곱 강제(I4).
        saved_order = order_repository.save.call_args.args[0]
        self.assertEqual(saved_order.unit_price, 1000)
        self.assertEqual(saved_order.total_price, 2000)
        self.assertEqual(result.id, 10)

    def test_도메인_차감에서_재고_부족이면_InsufficientStock을_던진다(self) -> None:
        # stock=1 인데 2 요청 → 도메인 deduct가 먼저 거른다(권위).
        product = Product(id=1, name="위젯", price=1000, stock=1)
        app, product_repository, order_repository = _build_app(
            product=product, deduct_rowcount=1
        )

        with self.assertRaises(InsufficientStock):
            app.execute(PlaceOrderCommand(product_id=1, quantity=2))

        order_repository.save.assert_not_called()

    def test_조건부_UPDATE_rowcount가_0이면_InsufficientStock으로_번역한다(self) -> None:
        # 도메인 검사는 통과(stock 충분)했으나 race로 UPDATE 시점에 재고가 사라진 경우(안전망).
        # 409의 available_stock은 차감된 메모리 값(8)이 아니라 DB 재조회 잔여(0)여야 한다(§2.5).
        product = Product(id=1, name="위젯", price=1000, stock=10)
        reread_product = Product(id=1, name="위젯", price=1000, stock=0)
        app, product_repository, order_repository = _build_app(
            product=product, deduct_rowcount=0
        )
        # 첫 조회는 원래 재고, race 분기 재조회는 충돌 시점의 실제 잔여를 돌려준다.
        product_repository.find_by_id.side_effect = [product, reread_product]

        with self.assertRaises(InsufficientStock) as ctx:
            app.execute(PlaceOrderCommand(product_id=1, quantity=2))

        self.assertEqual(ctx.exception.available_stock, 0)
        order_repository.save.assert_not_called()
