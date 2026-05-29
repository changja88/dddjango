"""DjangoProductStockPort — catalog 재고 ACL 어댑터 (명세 §1.4·§4.2).

ProductStockPort 의 구현. catalog Product 도메인 동작(deduct_stock)을 호출하고,
catalog 측 결과·예외를 ordering 도메인 언어로 번역한다(부패 방지 계층).
catalog 모델 import 는 이 어댑터에만 가둔다(명세 §1.4 — 리포지토리에 섞지 않음).

판정(stock >= qty)은 catalog 의 deduct_stock 이 소유한다 — 이 어댑터는 결과만
번역하고 stock >= qty 판정을 복제하지 않는다(명세 §1.4·§3.3 Rule ownership).
"""
from application.ordering.domain_layer.order.exception import (
    OutOfStock,
    ProductNotFound,
    StockDeductionConflict,
)
from application.ordering.domain_layer.order.port.product_stock_port import (
    ProductStockPort,
)
from catalog.exceptions import InsufficientStock, StockUpdateConflict
from catalog.models import Product


class DjangoProductStockPort(ProductStockPort):
    def get_unit_price(self, product_id: int) -> int:
        product = self._get_product(product_id)
        return product.price

    def deduct(self, product_id: int, quantity: int) -> None:
        product = self._get_product(product_id)
        try:
            product.deduct_stock(quantity)
        except InsufficientStock as exc:
            # catalog 의 재고 부족 판정을 ordering 도메인 언어로 번역(영구 거절 → 409).
            # 요청 수량을 담아 표현 계층이 409 requested 에 에코한다(명세 §2.3).
            raise OutOfStock(requested=quantity, detail=str(exc)) from exc
        except StockUpdateConflict as exc:
            # version CAS 0행 경합 신호를 ordering 언어로 번역(재시도 가능한 1회 실패).
            # 종단 예외(StockContentionExhausted)가 아니라 retryable 신호로 올린다 —
            # 재시도/소진 판정은 응용 서비스가 소유한다(명세 §3.3 Rule ownership).
            raise StockDeductionConflict(str(exc)) from exc

    @staticmethod
    def _get_product(product_id: int) -> Product:
        try:
            return Product.objects.get(pk=product_id)
        except Product.DoesNotExist as exc:
            raise ProductNotFound(f"상품 없음: {product_id}") from exc
