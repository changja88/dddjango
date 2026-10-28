"""bad_composition_root_imports_part — 합성 루트가 ②′ 폴더의 틀 부품 모듈을 가져온다(#662 · 패키지 경로 import 는 통과)."""
from __future__ import annotations

from application.orders.application_layer.order.checkout_order.checkout_order_use_case import CheckoutOrderUseCase
from application.orders.application_layer.order.checkout_order.checkout_order_use_case.checkout_order_frame import (
    CheckoutOrderFrame,
)
