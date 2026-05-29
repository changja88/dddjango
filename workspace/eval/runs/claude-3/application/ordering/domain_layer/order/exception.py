"""ordering 도메인 예외 (명세 §1.3).

각 예외는 표현 계층에서 RFC 9457 Problem Details 상태로 매핑된다(명세 §2.3).
이번 슬라이스(해피패스)에서는 InvalidQuantity 만 사용되지만, 다음 슬라이스의
에러 계약(404/409/503)이 확장만 하면 되도록 도메인 예외를 함께 정의해 둔다.
"""


class OrderingError(Exception):
    """ordering 도메인 최상위 예외."""


class InvalidQuantity(OrderingError):
    """수량이 1 미만일 때 발생 (명세 §1.3 → 422)."""


class ProductNotFound(OrderingError):
    """참조한 product_id 에 해당 상품이 없을 때 발생 (명세 §1.3 → 404)."""


class OutOfStock(OrderingError):
    """재고가 요청 수량보다 적어 차감이 거부될 때 발생 (명세 §1.3 → 409).

    재고 부족은 영구적 거절이다(경합 소진과 의미 구분 — 명세 §2.3 api M4).
    requested(요청 수량)를 담아 표현 계층이 409 에 에코한다(명세 §2.3 409 확장).
    """

    def __init__(self, *, requested: int, detail: str) -> None:
        self.requested = requested
        super().__init__(detail)


class StockDeductionConflict(OrderingError):
    """재고 차감 1회 시도가 version CAS 경합(0행)으로 실패할 때 발생 (재시도 트리거).

    재고 부족(영구, OutOfStock)도 경합 소진(종단, StockContentionExhausted)도 아닌
    *재시도 가능한 1회 시도 실패 신호*다(명세 §1.4·§3.3 — CAS 0행은 재시도 트리거).
    ACL 어댑터가 catalog 의 경합 신호를 이 예외로 번역하고, 응용 서비스가 이를
    잡아 재조회→도메인 동작 재실행으로 bounded retry 한다. API 로 새지 않는다
    (재시도 정책은 응용 서비스가 소유 — 명세 §3.3).
    """


class StockContentionExhausted(OrderingError):
    """version CAS 경합 재시도 상한 초과 시 발생 (명세 §1.3 → 503).

    실제 재고 부족이 아니라 일시적 경합 소진이다(OutOfStock 과 구분).
    응용 서비스가 bounded retry(최대 3회)를 소진했을 때만 던진다(명세 §3.3).
    """
