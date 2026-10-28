from __future__ import annotations

from .rate_seller_frame import RateSellerFrame


class SellerReview:
    def __init__(self, owner: "RateSellerUseCase", frame: RateSellerFrame) -> None:
        self._owner: "RateSellerUseCase" = owner
        self._frame: RateSellerFrame = frame

    def review(self, seller_id: int) -> None:
        self._frame.record_done(seller_id)
