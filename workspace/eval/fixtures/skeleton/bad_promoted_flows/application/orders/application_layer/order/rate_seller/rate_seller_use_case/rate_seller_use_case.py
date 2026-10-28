from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.rate_seller.rate_seller_command import RateSellerCommand
from application.orders.application_layer.order.rate_seller.rate_seller_result import RateSellerResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .rate_seller_frame import RateSellerFrame
from .seller_review import SellerReview


class RateSellerUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: RateSellerFrame = RateSellerFrame(new_unit_of_work)
        owner: RateSellerUseCase = self
        self._seller_review: SellerReview = SellerReview(owner, frame=self._frame)

    def execute(self, command: RateSellerCommand) -> RateSellerResult:
        self._seller_review.review(command.target_id)
        return RateSellerResult(target_id=command.target_id, done=True)
