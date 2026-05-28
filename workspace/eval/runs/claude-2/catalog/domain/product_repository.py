"""Product 리포지토리 추상화(포트).

설계 명세 section 4: 응용 서비스는 이 ABC에 의존하고 구현을 주입받는다(DIP).
조건부 원자 차감과 rowcount 기반 404/409 분류는 인프라 구현이 소유한다.
"""

from abc import ABC, abstractmethod

from catalog.domain.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def deduct_stock(self, product_id: int, quantity: int) -> Product:
        """조건부 원자 UPDATE로 재고를 차감하고 차감 후 도메인 Product를 반환한다.

        rowcount==0이면 동일 트랜잭션 재SELECT로 분류:
        - 상품이 존재하면 ProductNotFoundError 대신 InsufficientStockError(재고 부족)
        - 상품이 없으면 ProductNotFoundError(상품 없음)
        """
        raise NotImplementedError
