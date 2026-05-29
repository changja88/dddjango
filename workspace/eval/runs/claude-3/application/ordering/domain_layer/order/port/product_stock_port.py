"""ProductStockPort — catalog 재고 협력 포트 (명세 §1.4·§4.2).

ordering 도메인이 의존하는 ACL 협력 포트(ABC)다. "지정 상품의 단가를 조회하고,
요청 수량만큼 재고 차감을 요청"하는 역할을 정의한다. ordering 도메인은 이 포트에만
의존하고 catalog 를 모른다 — catalog 번역은 구현 어댑터(DjangoProductStockPort,
infra_layer/acl)가 담당한다.

판정(stock >= qty)은 catalog 의 도메인 동작이 소유한다(명세 §1.4·§3.3) — 포트는
결과만 ordering 도메인 언어(예외)로 전달한다.
"""
from abc import ABC, abstractmethod


class ProductStockPort(ABC):
    @abstractmethod
    def get_unit_price(self, product_id: int) -> int:
        """상품의 현재 단가를 조회한다. 상품이 없으면 ProductNotFound."""
        raise NotImplementedError

    @abstractmethod
    def deduct(self, product_id: int, quantity: int) -> None:
        """catalog 재고 차감을 요청한다(판정은 catalog 도메인 동작이 소유).

        - 재고 부족: OutOfStock (명세 §1.3 → 409).
        - 경합(version CAS 0행): StockDeductionConflict — 재시도 가능한 1회 실패
          신호. 재시도/소진(StockContentionExhausted→503) 판정은 응용 서비스가
          소유한다(명세 §3.3 Rule ownership).
        - 상품 없음: ProductNotFound (명세 §1.3 → 404).
        """
        raise NotImplementedError
