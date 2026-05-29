"""경합 소진 503 계약 통합 테스트 (안쪽 루프 — 결정론적).

근거: 설계 명세 §3.3 Test criteria (e)·§5 행위8.
행위8(경합 소진 503)은 "재고는 충분하나 경합만으로 retry 가 소진되는" 상태를
요구하는데, 블랙박스 HTTP 만으로는 내부 retry 타이밍·동시 version 충돌을 결정론적으로
강제하기 어렵다(인수 스켈레톤 StockContentionExhaustionTest 가 skip 인 이유).

여기서는 ACL 의 재고 차감을 *매 시도 경합(StockDeductionConflict)* 으로 강제하는
포트 더블을 엔드포인트 조립 지점에 주입해, 실제 HTTP 스택을 통과시켜 503+Retry-After
계약과 원자성(부분 변경 없음)을 결정론적으로 검증한다. 응용 서비스의 bounded retry
상한(3회)이 소진되면 StockContentionExhausted → 503 으로 매핑되는 경로다.
"""
import json
from typing import Optional

from django.test import TestCase

from application.ordering.domain_layer.order.exception import StockDeductionConflict
from application.ordering.domain_layer.order.port.product_stock_port import (
    ProductStockPort,
)
from application.ordering.infra_layer.django_ordering.models import OrderModel
from application.ordering.presentation_layer.api.place_order import api_order
from catalog.models import Product

ORDERS_URL = "/api/orders"


class AlwaysConflictStockPort(ProductStockPort):
    """단가는 정상 조회되지만 차감은 매번 경합(재시도 가능 신호)을 내는 포트 더블.

    재고 부족(OutOfStock)이 아니라 일시적 경합(StockDeductionConflict)이므로,
    응용 서비스가 bounded retry 를 소진하고 StockContentionExhausted 로 종단한다.
    """

    def __init__(self, *, unit_price: int) -> None:
        self._unit_price = unit_price

    def get_unit_price(self, product_id: int) -> int:
        return self._unit_price

    def deduct(self, product_id: int, quantity: int) -> None:
        raise StockDeductionConflict(f"강제 경합: product {product_id}")


class StockContentionExhaustion503Test(TestCase):
    """행위8: 경합 소진 → 503 + Retry-After, 부분 변경 없음 (명세 §5-8, §3.3 e).

    409(out-of-stock)와 의미를 분리한다 — 일시적 경합 소진은 503.
    """

    def setUp(self) -> None:
        # 재고는 충분(경합 소진은 재고 부족과 무관함을 명확히 — stock 변동 없음 확인용).
        self._product = Product.objects.create(name="Widget", price=1000, stock=100)
        self._original_builder = api_order._build_place_order_app

        def _build_with_conflict() -> object:
            app = self._original_builder()
            # ACL 포트만 경합 더블로 교체 — 리포지토리·트랜잭션 경계는 실제 경로 유지.
            app._stock_port = AlwaysConflictStockPort(unit_price=1000)
            return app

        api_order._build_place_order_app = _build_with_conflict

    def tearDown(self) -> None:
        api_order._build_place_order_app = self._original_builder

    def test_contention_exhaustion_returns_503_with_retry_after(self) -> None:
        response = self.client.post(
            ORDERS_URL,
            data=json.dumps({"product_id": self._product.id, "quantity": 1}),
            content_type="application/json",
        )

        # 503 Service Unavailable + Retry-After (일시적 경합 소진).
        self.assertEqual(response.status_code, 503)
        self.assertIn("Retry-After", response)
        self.assertEqual(response["Content-Type"], "application/problem+json")

        body = response.json()
        # 409(out-of-stock)와 type·의미 분리.
        self.assertEqual(body["type"], "/problems/stock-contention")
        self.assertEqual(body["status"], 503)

        # 원자성: 부분 변경 없음 — 재고 불변·주문 미생성(명세 §3.3 criteria e).
        self._product.refresh_from_db()
        self.assertEqual(self._product.stock, 100)
        self.assertEqual(OrderModel.objects.count(), 0)
