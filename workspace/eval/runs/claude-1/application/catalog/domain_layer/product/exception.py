"""Product 애그리거트 도메인 예외."""


class InsufficientStock(Exception):
    """재고 부족 — 차감 수량이 가용 재고를 초과할 때 발생(I1 위반).

    available_stock(현재 재고)과 requested_quantity(요청 수량)를 담아
    응용/표현 계층이 409 Problem Details로 번역할 수 있게 한다.
    """

    def __init__(self, available_stock: int, requested_quantity: int) -> None:
        self.available_stock = available_stock
        self.requested_quantity = requested_quantity
        super().__init__(
            f"stock {available_stock} but {requested_quantity} was requested."
        )
