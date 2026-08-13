ELIGIBILITY_LIMIT: int = 3


def decide_eligibility(count: int) -> bool:
    """세탁 사례 — 예외 칸에 숨긴 판정 함수(#210 은 이것을 물어야 한다)."""
    return count < ELIGIBILITY_LIMIT


class OrderNotPayable(Exception):
    """결제 불가 주문."""
