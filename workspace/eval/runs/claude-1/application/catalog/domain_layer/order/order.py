"""Order 애그리거트 루트 (도메인).

단일 라인 주문 — Product를 ID로만 참조한다(규칙3). 생성자가 I4를 강제한다(§1.2·§1.4):
total_price = unit_price * quantity. 응용이 곱을 미리 계산해 넘기지 않는다.

status는 도메인 불변식이 아니라 표현 계약상 고정 리터럴이므로(§1.3) 도메인 Order는
status를 보유하지 않는다 — 생성=성립의 단일 사실만 보유한다.
"""


class Order:
    """단일 상품·수량 주문. 생성 시점 단가·합계 스냅샷을 보유한다."""

    def __init__(self, product_id: int, quantity: int, unit_price: int) -> None:
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        # I4: 합계는 생성자가 단가×수량으로 강제(도메인 권위).
        self.total_price = unit_price * quantity
