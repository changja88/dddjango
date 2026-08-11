from __future__ import annotations


class PlaceOrderUseCase:
    def execute(self) -> str:
        return render_to_string("orders/mail/notice.html", {})
