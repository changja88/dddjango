"""catalog 도메인 예외.

catalog 는 ordering 컨텍스트의 예외를 알지 않는다(BC 독립 — 명세 §1.4).
ordering 으로의 번역은 ordering 의 ACL 어댑터가 담당한다.
"""


class InsufficientStock(Exception):
    """재고가 요청 수량보다 적어 차감 판정이 거부될 때 발생.

    deduct_stock 의 재고 충분성 판정(stock >= qty)이 거부될 때 던진다
    (명세 §1.4·§3.3 Rule ownership — 판정은 재고 소유자 catalog 가 가진다).
    """


class StockUpdateConflict(Exception):
    """version CAS 조건부 UPDATE 가 0행에 영향(경합)일 때 발생.

    재고 부족이 아니라 다른 트랜잭션이 version 을 올린 경합 신호다 — 재고
    충분성 판정과 의미가 다르다(명세 §3.3: CAS 0행은 재시도 트리거).
    재조회 후 재시도는 호출자(ordering 응용 서비스)가 소유한다.
    """
